#!/usr/bin/env python3
"""Whether two UFO models give the same amplitudes at the cards of the study runs.

    python3.11 validate/same_couplings.py UFO_A UFO_B RECORDS [RECORDS ...] [--all] [--card CARD ...] [--out VERDICTS] [--tol 1e-9]

The records of a study (examples/studies/provenance.py) name, for every row, the restriction card of its
run and its param card, copies of which are kept in the study's cards/ directory.  At each distinct set of
the two among the rows run with model A (among all rows with --all), the restriction card by its sha256,
both models are evaluated the way MadGraph evaluates them for that run.  MadGraph restricts a model at the
values of its restriction card restrict_<card>.dat: a parameter, external or internal, that is 0 or 1 there
keeps that value, a coupling that vanishes there is removed with its vertex entries, couplings equal there up
to a sign (and of the same orders) are merged into the first of them, and external parameters of one block
equal there up to a sign are merged into the first of them.  The param card of the run then sets the
parameters left.  Model A is restricted by the copy of the card the run was imported with, and the comparison
stops if there is none.  Model B is restricted by its own restrict_<card>.dat, which is what a run with it
would use, and by the run's card, read by name, when it has no card of that name.  A model imported without a
card is restricted by its restrict_default.dat when it has one, and is not restricted otherwise (a row of
model A without a card whose record names no restrict_default.dat stops the comparison when A has one).

Each vertex is evaluated as a number, as validate/compare_ufo.py does: the sum over its colour and Lorentz
structures of coupling times colour structure times Lorentz structure, at random wavefunctions and momenta
fixed by its particles, at two points.  The values are summed, with their signs, over the vertices of one set
of particles (by PDG code) and one set of coupling orders, because two builds of a model split a vertex into
different structures, and the difference of the two models is measured against the largest single term of
that sum, so that a sum whose terms cancel does not count as a difference.  When the two models have the same
couplings.py, vertices.py and lorentz.py the couplings themselves are compared by name as well, which says
exactly which couplings differ.  A coupling that the restriction card merges into another, and that differs
from it at the run's param card by more than 1e-9 of its size at either card, is listed for each model, since
MadGraph then computes the run with the other coupling's value.

Two kinds of difference do not count against the rows.  A vertex sum that differs between the models by less
than 1e-12 of the size of its terms differs only in the rounding of a sum that vanishes (the size of a
coupling's terms is its expression with every sum replaced by the sum of the sizes of its terms).  And a vertex
that no tree diagram of the rows' processes can contain does not change their amplitudes.  Removing a vertex
from a tree leaves one piece per leg, each with external particles of its own, so a vertex has at most as many
legs as the process has external particles.  A fermion line of a tree runs from one external fermion to
another and passes a vertex once, so a vertex with 2n quark legs needs 2n external quarks (p and j supply one each), and a vertex with 2n leptons of one generation needs 2n external
leptons of that generation, as long as every vertex of the model conserves baryon number and each lepton
number.  Both kinds are listed in the details file, and the verdict counts only the others.

couplings.py is read as text and each value compiled alone, since the file of a dimension-eight model is
half a gigabyte and importing it as a module would build its whole syntax tree at once.

Writes VERDICTS (default same_couplings.tsv) with one line per set of cards: model_a and model_b (the model
hashes of provenance.py), card, card_sha256 (the run's restriction card), card_b (the sha256 of the card model
B was restricted by), param_card, keys, differing, max_rel, couplings_differing, rows and processes (the
processes whose tree diagrams decided which vertices count, separated by ';'), which `provenance.py attest`
reads, then notes, keys_only_a and keys_only_b (the vertices by orders that only one of the models has and that a
tree diagram of those processes can contain: where their sum vanishes the amplitudes agree, and the number of
diagrams MadGraph draws does not), and VERDICTS with .details.tsv for .tsv, every vertex and coupling that differs.  A copy of model B's
card goes into the cards/ directory of each study whose rows it was compared for, since a row found equal
counts from then on as a row run with that card.
"""
import argparse
import ast
import cmath
import collections
import gzip
import hashlib
import math
import os
import random
import re
import sys
import time
import types

import numpy as np

# the two models are read and never written: importing their python files must not leave a
# __pycache__ in a model directory that may belong to a released or running study
sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "examples", "studies"))
import provenance as PV  # noqa: E402
import zero_vertex as Z  # noqa: E402
from compare_ufo import Point, leave_ufo, scalar, use_ufo  # noqa: E402
from generic_inputs import COEFFICIENT_BLOCKS  # noqa: E402

# the values MadGraph leaves free although a card writes 0 or 1 with them
NOT_SPECIAL = (0.000001e-99, 9.999999e-1)


class Ref:
    """C.GC_1 in vertices.py, read as the name of the coupling only."""
    __slots__ = ("name",)

    def __init__(self, name):
        self.name = name


def read_couplings(path):
    """{name: (value, orders)} of a couplings.py, read as text."""
    out = {}
    with open(path) as f:
        text = f.read()
    for m in re.finditer(r"^\w+ = Coupling\(name = '(\w+)',\s*value = '([^']*)',\s*order = \{([^}]*)\}\)", text, re.M):
        out[m.group(1)] = (m.group(2), tuple(sorted((k, int(v)) for k, v in re.findall(r"'(\w+)'\s*:\s*(-?\d+)", m.group(3)))))
    return out


def limit_to_6_digit(a):
    """MadGraph's rounding before it looks for equal couplings (models/import_ufo.py)."""
    x = a.real
    if x != 0:
        x = round(x, int(abs(round(math.log(abs(x), 10), 0)) + 10))
    y = a.imag
    if y != 0:
        y = round(y, int(abs(round(math.log(abs(y), 10), 0)) + 10))
    return complex(x, y)


def _value(node, ns):
    if type(node) is ast.Name:
        return ns[node.id]
    return eval(compile(ast.Expression(node), "<term>", "eval"), ns)


def magnitude(node, ns):
    """The size of the terms of a coupling's expression: the expression with every sum replaced by the sum
    of the sizes of its terms, so that a value far below it is a sum of terms that cancel."""
    t = type(node)
    if t is ast.Expression:
        return magnitude(node.body, ns)
    if t is ast.Constant:
        return abs(node.value)
    if t is ast.UnaryOp:
        return magnitude(node.operand, ns)
    if t is ast.BinOp:
        op = type(node.op)
        if op in (ast.Add, ast.Sub):
            return magnitude(node.left, ns) + magnitude(node.right, ns)
        if op is ast.Mult:
            return magnitude(node.left, ns) * magnitude(node.right, ns)
        if op is ast.Div:
            return magnitude(node.left, ns) / abs(_value(node.right, ns))
        if op is ast.Pow:
            e = _value(node.right, ns)
            if complex(e).imag == 0 and complex(e).real > 0:
                return magnitude(node.left, ns) ** complex(e).real
    return abs(_value(node, ns))   # a parameter, a function of one, or complex(0,1)


# what the external particles of a process can supply: quark legs (p and j one each), lepton legs by generation
QUARKS = {"u", "d", "s", "c", "b", "t"}
LEPTON_GEN = {"e": 1, "ve": 1, "mu": 2, "vm": 2, "ta": 3, "vt": 3}
BOSONS = {"g", "a", "z", "w", "h"}


def external_legs(process):
    """(quark legs, {generation: lepton legs}, legs) of the external particles of a MadGraph process, None for
    a process with a name or a syntax this reading does not know, for which no vertex is ruled out."""
    sides = process.split(">")
    if len(sides) != 2:
        return None
    nq, nl, n = 0, collections.Counter(), 0
    for w in " ".join(sides).split():
        if "=" in w:
            continue   # a coupling order
        n += 1
        name = w.rstrip("+-~")
        if w in ("p", "j") or name in QUARKS:
            nq += 1
        elif name in LEPTON_GEN:
            nl[LEPTON_GEN[name]] += 1
        elif name in ("l", "vl"):
            nl[1] += 1
            nl[2] += 1
        elif name not in BOSONS:
            return None
    return nq, nl, n


class Restriction:
    """What MadGraph fixes when it restricts a model at a card."""

    def __init__(self, card, sha, placeholder, fixed, pmerge, zero, cmerge, scale):
        self.card, self.sha, self.placeholder = card, sha, placeholder
        self.fixed, self.pmerge, self.zero, self.cmerge = fixed, pmerge, zero, cmerge
        self.scale = scale   # |value| at the restriction card of each coupling merged into another


class Model:
    def __init__(self, ufo, seed=1, points=2):
        self.ufo, self.seed, self.points = os.path.abspath(ufo), seed, points
        self.version = PV.model_id(self.ufo)[0]
        self.files = {f: PV.sha256_file(os.path.join(self.ufo, f)) for f in ("couplings.py", "vertices.py", "lorentz.py")}
        t0 = time.time()
        use_ufo(self.ufo)
        stub = types.ModuleType("couplings")
        stub.__getattr__ = Ref
        sys.modules["couplings"] = stub
        try:
            import function_library as F
            import parameters as P
            import vertices as V
            self.ns = {"cmath": cmath, "math": math, "complex": complex, "abs": abs}
            for f in F.all_functions:
                self.ns[f.name] = eval(f"lambda {','.join(f.arguments)}: {f.expr}", self.ns)
            self.ext = []
            for p in P.all_parameters:
                if p.nature == "external":
                    code = tuple(str(c) for c in p.lhacode)
                    self.ext.append((p.name, p.lhablock, ("decay", code) if p.lhablock.lower() == "decay" else (p.lhablock.lower(), code), p.value))
            self.internal = [(p.name, compile(p.value, p.name, "eval")) for p in P.all_parameters if p.nature == "internal"]
            vs = V.all_vertices
            self.masses = {x.name for v in vs for q in v.particles for x in (q.mass, q.width)}
        finally:
            leave_ufo(self.ufo)
        cs = read_couplings(os.path.join(self.ufo, "couplings.py"))
        self.vertices, index, self.names, self.orders = [], {}, [], []
        for v in vs:
            terms = []
            for (ci, li), c in v.couplings.items():
                for r in (c if isinstance(c, list) else [c]):
                    if r.name not in index:
                        index[r.name] = len(self.names)
                        self.names.append(r.name)
                        self.orders.append(cs[r.name][1])
                    terms.append((ci, li, index[r.name]))
            self.vertices.append((v, tuple(sorted(q.pdg_code for q in v.particles)), terms))
        self.code = [compile(cs[n][0], n, "eval") for n in self.names]
        self.source, self.trees = [cs[n][0] for n in self.names], {}   # for the size of a coupling's terms
        self.by_string = sorted(range(len(self.names)), key=lambda i: self.names[i])
        self.users = collections.defaultdict(list)
        self.by_pdgs = collections.defaultdict(list)
        for k, (v, key, terms) in enumerate(self.vertices):
            self.by_pdgs[key].append(k)
            for _, _, i in terms:
                self.users[i].append(k)
        # whether every vertex conserves baryon number, each lepton number, and lepton number
        kept = lambda sel: all(sum(1 if p > 0 else -1 for p in key if sel(abs(p))) == 0 for _, key, _ in self.vertices)
        self.baryon = kept(lambda a: 1 <= a <= 6)
        self.lepton_gen = all(kept(lambda a, g=g: a in (9 + 2 * g, 10 + 2 * g)) for g in (1, 2, 3))
        self.lepton = kept(lambda a: 11 <= a <= 16)
        self.params = [n for n, *_ in self.ext] + [n for n, _ in self.internal]
        self.by_key = {k: n for n, block, k, default in self.ext}
        self.by_name = {n.lower(): n for n in self.params}
        # the Wilson coefficients, and the couplings that read each parameter.  The scales are not
        # coefficients: Lam, in block DIM8, and in a model with a dimension-six scale of its own Lam6, in DIM6.
        self.wc = {n for n, block, k, default in self.ext if block.upper() in COEFFICIENT_BLOCKS and not re.fullmatch(r"Lam\d*", n)}
        known = set(self.params)
        self.readers = collections.defaultdict(list)
        for i, c in enumerate(self.code):
            for p in set(c.co_names) & known:
                self.readers[p].append(i)
        self.cache, self.structures, self.restrictions, self.bases = {}, {}, {}, {}
        print(f"{self.ufo}: model {self.version[:12]}, {len(self.vertices)} vertices, {len(self.names)} couplings, "
              f"read in {time.time() - t0:.0f} s", flush=True)

    # ---- the parameters ---------------------------------------------------------------------------

    def card_values(self, text):
        """{parameter: value} of a card's entries, and how many entries name no parameter of this model.
        An entry is this model's parameter at its block and indices when the name agrees, and the
        parameter of its name otherwise, so that a card written for another build of the model, whose
        parameters may be numbered differently, sets the parameters it names."""
        out, foreign = {}, 0
        for k, (v, n) in PV.param_entries(text).items():
            if " : " in n:
                continue   # a value MadGraph fixes itself ("d : 0.0" for a massless quark)
            p = self.by_key.get(k)
            if p is None or (n and p.lower() != n.lower()):
                p = self.by_name.get(n.lower())
            if p is None:
                foreign += 1
                continue
            try:
                out[p] = float(v)
            except ValueError:
                pass
        return out, foreign

    def externals(self, text):
        """{name: value} of every external parameter: the card's, and the model's default where the
        card has none."""
        vals = self.card_values(text)[0]
        return {name: vals.get(name, default) for name, block, k, default in self.ext}

    def base(self, ext):
        """The parameters and couplings with every Wilson coefficient at zero and the other inputs at
        those of ext, computed once for each set of those inputs."""
        key = tuple(v for (name, *_), v in zip(self.ext, ext.values()) if name not in self.wc)
        if key not in self.bases:
            t0 = time.time()
            b = {n: (0.0 if n in self.wc else v) for n, v in ext.items()}
            ns = dict(self.ns)
            ns.update(b)
            for name, code in self.internal:
                ns[name] = eval(code, ns)
            g = np.array([eval(c, ns) for c in self.code], dtype=complex)
            self.bases[key] = (ns, g)
            print(f"   {os.path.basename(self.ufo)}: every coupling with the coefficients at zero, in {time.time() - t0:.0f} s", flush=True)
        return self.bases[key]

    def evaluate(self, ext, fixed=None):
        """The namespace of every parameter at these external values (a parameter in fixed keeps the
        value given there), and every coupling.  A coupling is evaluated only when a parameter it reads
        differs from its value with the coefficients at zero, and is that value otherwise."""
        ns = dict(self.ns)
        ns.update(ext)
        if fixed:
            ns.update({n: v for n, v in fixed.items() if n in ext})
        for name, code in self.internal:
            ns[name] = fixed[name] if fixed and name in fixed else eval(code, ns)
        nb, gb = self.base(ext)
        changed = [p for p in self.params if ns[p] != nb[p]]
        todo = sorted({i for p in changed for i in self.readers.get(p, ())})
        g = gb.copy()
        for i in todo:
            g[i] = eval(self.code[i], ns)
        return ns, g

    def own_card(self, card):
        """(text, sha256) of this model's restrict_<card>.dat (restrict_default.dat for card ''), None if absent."""
        path = os.path.join(self.ufo, f"restrict_{card or 'default'}.dat")
        if not os.path.isfile(path):
            return None
        with open(path, "rb") as f:
            b = f.read()
        return b.decode(), hashlib.sha256(b).hexdigest()

    def restriction(self, card, text, sha):
        """The restriction MadGraph applies for `import model <name>-<card>` (card '' for the plain name) when
        the restriction card has the text given (None: no restriction card, nothing restricted)."""
        if text is None:
            return None
        if (card, sha) in self.restrictions:
            return self.restrictions[(card, sha)]
        ph = self.externals(text)
        ns, g = self.evaluate(ph)
        fixed = {}
        for n in self.params:
            v = ns[n]
            if n != "ZERO" and (v == 0 or (v == 1 and n not in self.masses)):
                fixed[n] = 0.0 if v == 0 else 1.0
        # couplings: vanishing ones are removed, equal ones merged (detect_identical_couplings)
        strict = False
        while True:
            zero, groups, again = set(), {}, False
            for i in self.by_string:
                v = g[i]
                if v == 0 or (not strict and abs(v) < 1e-13):
                    zero.add(i)
                    continue
                if not strict and abs(v) < 1e-10:
                    strict, again = True, True
                    break
                r = limit_to_6_digit(v)
                if r in groups:
                    groups[r].append((i, 1))
                elif -r in groups:
                    groups[-r].append((i, -1))
                else:
                    groups[r] = [(i, 1)]
            if not again:
                break
        cmerge = {}
        for grp in groups.values():
            if len(grp) < 2:
                continue
            by_order = collections.defaultdict(list)
            for i, s in grp:
                by_order[self.orders[i]].append((i, s))
            for sub in by_order.values():
                if len(sub) > 1:
                    if sub[0][1] == -1:
                        sub = [(i, -s) for i, s in sub]
                    for i, s in sub[1:]:
                        cmerge[i] = (sub[0][0], s)
        # external parameters of one block with one value up to a sign (detect_identical_parameters)
        pmerge, first = {}, {}
        for name, block, k, default in self.ext:
            v = ph[name]
            if name in fixed or v in (0, 1) or v in NOT_SPECIAL or block.lower() == "decay":
                continue
            if (block, v) in first:
                pmerge[name] = (first[(block, v)], 1)
            elif (block, -v) in first:
                pmerge[name] = (first[(block, -v)], -1)
            else:
                first[(block, v)] = name
        r = Restriction(card, sha, ph, fixed, pmerge, zero, cmerge, {i: abs(g[i]) for i in cmerge})
        self.restrictions[(card, sha)] = r
        return r

    def run(self, r, text, borrowed=False):
        """The couplings MadGraph computes for a run with the restriction r (None for none) and this param card
        (with text None, at the values of the restriction card), and notes on what of the card this model
        does not take."""
        notes, self.fused = collections.Counter(), []
        if borrowed:
            notes[f"no restrict_{r.card}.dat of its own, restricted by the run's, read by name"] += 1
        if r is None:
            vals, foreign = self.card_values(text or "")
            if foreign:
                notes["card entries naming no parameter of this model"] = foreign
            ns, g = self.evaluate({name: vals.get(name, default) for name, block, k, default in self.ext})
            self.last_ns = ns
            return g, notes
        if text is None:
            vals, foreign = {n: v for n, v in r.placeholder.items() if n not in r.fixed and n not in r.pmerge}, 0
        else:
            vals, foreign = self.card_values(text)
        if foreign:
            notes["card entries naming no parameter of this model"] = foreign
        ext = {}
        for name, block, k, default in self.ext:
            if name in r.fixed:
                ext[name] = r.fixed[name]
                if name in vals and vals[name] != r.fixed[name]:
                    notes["card entries this model fixes at the restriction card"] += 1
            elif name in r.pmerge:
                ext[name] = None
                if name in vals:
                    notes["card entries this model merges into another parameter"] += 1
            elif name in vals:
                ext[name] = vals[name]
            else:
                ext[name] = r.placeholder[name]
                if block.lower() != "decay":
                    notes["parameters this model keeps that the card does not set"] += 1
        for name, (f, s) in r.pmerge.items():
            ext[name] = s * ext[f]
        ns, g = self.evaluate(ext, r.fixed)
        self.last_ns = ns
        g[list(r.zero)] = 0
        # a coupling merged into another takes that one's value, which is what MadGraph computes.  Where
        # the two differ at the run the restriction card has fused couplings it should not have.  The
        # difference is measured against the size of the coupling at the restriction card, and against
        # the size of the terms of the two couplings at the run (magnitude), since a coupling that
        # vanishes at the run is a sum of terms that cancel there only to rounding.
        self.fused = []
        for i, (m, s) in sorted(r.cmerge.items()):
            d = abs(g[i] - s * g[m])
            if d > 1e-9 * max(abs(g[i]), abs(g[m]), r.scale[i]) and d > 1e-9 * max(self.size(i, ns), self.size(m, ns)):
                self.fused.append((self.names[i], self.names[m], s, g[i], s * g[m]))
            g[i] = s * g[m]
        if self.fused:
            notes["couplings merged at the restriction card that differ at the run"] = len(self.fused)
        return g, notes

    # ---- the vertices ----------------------------------------------------------------------------

    def factors(self, k):
        """(colour times Lorentz structure) of each term of vertex k at each point."""
        if k in self.cache:
            return self.cache[k]
        v, _, terms = self.vertices[k]
        names = [p.name for p in v.particles]
        order = sorted(range(len(names)), key=lambda j: (names[j], j))
        pos = {order[j] + 1: j for j in range(len(order))}
        ferm = [j for j in order if v.particles[j].spin % 2 == 0]
        sgn = [1] * len(v.lorentz)
        if len(ferm) >= 4:
            eps = Z.order_sign(ferm)
            for li, l in enumerate(v.lorentz):
                s = Z.structure_sign(l.structure)
                if s is None:
                    raise SystemExit(f"{self.ufo}: no fermion flow for {l.name} = {l.structure}")
                sgn[li] = eps * s
        comp = lambda s: self.structures.setdefault(s, compile(s, "<structure>", "eval"))
        out = np.zeros((len(terms), self.points), dtype=complex)
        for pt in range(self.points):
            rng = random.Random(f"{self.seed}:{pt}:{'/'.join(sorted(names))}")
            point = Point([v.particles[j].color for j in order], pos, rng)
            lns, cns = point.lorentz_ns(), point.colour_ns()
            lor = [sgn[li] * scalar(eval(comp(l.structure), lns)) for li, l in enumerate(v.lorentz)]
            col = [scalar(eval(comp(c), cns)) for c in v.color]
            for t, (ci, li, _) in enumerate(terms):
                out[t, pt] = col[ci] * lor[li]
        self.cache[k] = out
        return out

    def vertex_sums(self, g):
        """{(PDG codes, orders): (signed sum at each point, largest single term)} at these couplings."""
        live = set(np.flatnonzero(g).tolist())
        ks = sorted({k for i in live for k in self.users[i]})
        sums, top = collections.defaultdict(lambda: np.zeros(self.points, dtype=complex)), collections.defaultdict(float)
        for k in ks:
            f = self.factors(k)
            _, key, terms = self.vertices[k]
            for t, (_, _, i) in enumerate(terms):
                if i in live:
                    x = g[i] * f[t]
                    sums[(key, self.orders[i])] += x
                    top[(key, self.orders[i])] = max(top[(key, self.orders[i])], float(np.max(np.abs(x))))
        return {k: (sums[k], top[k]) for k in sums}

    def size(self, i, ns):
        """The size of the terms of coupling i at the parameters ns (magnitude)."""
        if i not in self.trees:
            self.trees[i] = ast.parse(self.source[i], mode="eval")
        return magnitude(self.trees[i], ns)

    def noise(self, key, g, ns, restriction):
        """The size of the terms of the vertex sum of key (particles, orders) at the couplings g and the
        parameters ns: over its terms, the size of the terms of the coupling MadGraph computes (the
        coupling it is merged into, if any) times the size of the colour and Lorentz factor."""
        pdgs, orders = key
        merged = restriction.cmerge if restriction is not None else {}
        out = 0.0
        for k in self.by_pdgs.get(pdgs, ()):
            terms, f = self.vertices[k][2], None
            for t, (_, _, i) in enumerate(terms):
                if self.orders[i] != orders or g[i] == 0:
                    continue
                j = merged[i][0] if i in merged else i
                if j not in self.trees:
                    self.trees[j] = ast.parse(self.source[j], mode="eval")
                f = self.factors(k) if f is None else f
                out += magnitude(self.trees[j], ns) * float(np.max(np.abs(f[t])))
        return out

    def can_enter(self, pdgs, ext):
        """Whether a vertex of these particles can be part of a tree diagram of a process whose external
        particles supply ext (external_legs)."""
        if ext is None:
            return True
        nq, nl, n = ext
        if len(pdgs) > n:
            return False   # each leg of a vertex of a tree leads to external particles of its own
        q = sum(1 for p in pdgs if 1 <= abs(p) <= 6)
        l = collections.Counter((abs(p) - 11) // 2 + 1 for p in pdgs if 11 <= abs(p) <= 16)
        if self.baryon and q > nq:
            return False
        if self.lepton_gen:
            return all(n <= nl.get(gen, 0) for gen, n in l.items())
        return not (self.lepton and sum(l.values()) > sum(nl.values()))


def study_points(records, version, every, model_dir):
    """{(card, restriction-card sha256, param card hash): [study directories, param card text, rows, processes,
    restriction card text]} of the rows of these records run with the model of this hash (every row with
    every).  The restriction card is the copy the record names (in the study's cards/, or the card of
    model_dir when it is that file), and the comparison stops when a row has none.  A row with no diagrams has
    no param card, and is compared at the values of its restriction card, which decide what vertices the run
    had (param card '-', text None)."""
    out, missing = {}, collections.Counter()
    for rp in records:
        study = os.path.dirname(os.path.abspath(rp))
        hr, recs = PV.read_tsv(rp)
        for r in recs:
            d = PV.as_dict(hr, r)
            if not (every or d["model_sha256"] == version):
                continue
            base, _, card = d["model"].partition("-")
            sha = d["card_sha256"] or "-"
            rtext = None
            if card:
                rtext = PV.load_restriction(study, sha, base, card, model_dir)
                if rtext is None:
                    missing[(rp, card, sha)] += 1
                    continue
            if d["param_card"] in ("", "-"):
                if d["sigma_pb"] != "NO_DIAGRAMS":
                    continue
                k, text = (card, sha, "-"), None
            else:
                k = (card, sha, d["param_card"])
                text = PV.load_card(study, d["param_card"], "param") if k not in out else out[k][1]
                if text is None:
                    print(f"{rp}: no copy of the param card {d['param_card'][:12]} in cards/", file=sys.stderr)
                    continue
            p = out.setdefault(k, [[], text, 0, set(), rtext])
            if study not in p[0]:
                p[0].append(study)
            p[2] += 1
            p[3].add(" ".join(d["process"].split()))
    if missing:
        raise SystemExit("no copy of the restriction card the run was imported with, so model A cannot be restricted the way "
                         "MadGraph restricted it:\n" + "\n".join(f"   {rp}: {n} rows of restrict_{c}.dat {s[:12]}" for (rp, c, s), n in sorted(missing.items())))
    return out


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("a")
    a.add_argument("b")
    a.add_argument("records", nargs="+")
    a.add_argument("--all", action="store_true", help="every row of the records, not only those run with model A")
    a.add_argument("--card", action="append", help="only the rows of this restriction card ('' for none); may be repeated")
    a.add_argument("--out", default="same_couplings.tsv")
    a.add_argument("--tol", type=float, default=1e-9)
    args = a.parse_args(argv[1:])
    A = Model(args.a)
    pts = study_points(args.records, A.version, args.all, A.ufo)
    if args.card is not None:
        pts = {k: v for k, v in pts.items() if k[0] in args.card}
    if not pts:
        print(f"no row of {', '.join(args.records)} was run with {args.a} (model {A.version[:12]})")
        return 1
    if any(not k[0] for k in pts) and A.own_card("") is not None:
        raise SystemExit(f"{A.ufo} has a restrict_default.dat, which MadGraph applies to a model imported without a card, "
                         "and the records of its rows without a card name none")
    print(f"{len(pts)} cards: " + ", ".join(f"{c or '(none)'} {s[:8]} {h[:8]} ({p[2]} rows)" for (c, s, h), p in sorted(pts.items())), flush=True)
    res = {}
    for k, (studies, text, n, procs, rtext) in sorted(pts.items()):
        ra = A.restriction(k[0], rtext, k[1])
        g, notes = A.run(ra, text)
        res[k] = [g, A.vertex_sums(g), notes, ra, getattr(A, "fused", []), A.last_ns]
        print(f"   {os.path.basename(A.ufo)} at {k[0] or '(none)'} {k[1][:8]} {k[2][:8]}", flush=True)
    # model A stays in memory: a difference is weighed against the size of the terms of both sums
    B = Model(args.b)
    same_files = A.files == B.files
    if same_files:
        B.cache = A.cache   # the same vertices, so the same structures at the same points
    lines, details = [], []
    for k, (studies, text, n, procs, rtext) in sorted(pts.items()):
        card, sha, h = k
        ga, va, na, ra, fused_a, ns_a = res[k]
        # model B as a run with it would be restricted: by its own card of that name, else by the run's
        own = B.own_card(card)
        borrowed = own is None and bool(card)
        rtext_b, sha_b = own if own is not None else (rtext, sha if card else "-")
        rb = B.restriction(card, rtext_b, sha_b)
        gb, nb = B.run(rb, text, borrowed)
        fused_b, ns_b = getattr(B, "fused", []), B.last_ns
        vb = B.vertex_sums(gb)
        exts = [external_legs(p) for p in sorted(procs)]
        counted, rounding, outside = [], [], []
        for key in set(va) | set(vb):
            (sa, ta), (sb, tb) = va.get(key, (np.zeros(B.points), 0.0)), vb.get(key, (np.zeros(B.points), 0.0))
            d = float(np.max(np.abs(sa - sb)))
            scale = max(ta, tb)
            if d <= args.tol * scale:
                continue
            item = (d / scale, key, sa[0], sb[0], "only in A" if key not in vb else "only in B" if key not in va else "")
            if d <= 1e-12 * max(A.noise(key, ga, ns_a, ra), B.noise(key, gb, ns_b, rb)):
                rounding.append(item)
            elif not any(A.can_enter(key[0], e) or B.can_enter(key[0], e) for e in exts):
                outside.append(item)
            else:
                counted.append(item)
        for x in (counted, rounding, outside):
            x.sort(key=lambda x: -x[0])
        cdiff = []
        if same_files:
            keys = {key for _, key, *_ in counted}
            for i in np.flatnonzero((ga != 0) | (gb != 0)).tolist():
                d, s = abs(ga[i] - gb[i]), max(abs(ga[i]), abs(gb[i]))
                if d > args.tol * s and any((B.vertices[v][1], B.orders[i]) in keys for v in B.users[i]):
                    cdiff.append((d / s, B.names[i], ga[i], gb[i]))
            cdiff.sort(key=lambda x: -x[0])
        # a row found equal counts as a row run with B's card, so the study keeps a copy of it
        if own is not None:
            for st in studies:
                PV.store_restriction(st, B.ufo, card or "default", sha_b)
        rel = max([x[0] for x in counted] + [0.0])
        note = "; ".join(f"A: {m} {c}" for m, c in na.items()) + ("; " if na and nb else "") + "; ".join(f"B: {m} {c}" for m, c in nb.items())
        if rounding:
            note += ("; " if note else "") + f"{len(rounding)} vertex sums differ only in the rounding of terms that cancel"
        if outside:
            note += ("; " if note else "") + f"{len(outside)} differing vertices no tree diagram of the rows' processes contains"
        nkeys = len(set(va) | set(vb))
        # The vertices by orders that one model has and the other lacks.  Where the sum of such a vertex vanishes
        # the amplitudes are the same, and it is no difference above, but MadGraph draws the diagrams that contain
        # it in one model and not in the other, so the number of diagrams of a process, and whether a row whose
        # cross section vanishes has diagrams at all, can differ.  Those a tree diagram of the rows' processes can
        # contain are counted in the verdict (keys_only_a, keys_only_b) and all are listed in the details file.
        lone = {"A": sorted(set(va) - set(vb)), "B": sorted(set(vb) - set(va))}
        enters = {s: [key for key in ks if any(A.can_enter(key[0], e) or B.can_enter(key[0], e) for e in exts)] for s, ks in lone.items()}
        lines.append([card or "-", sha, sha_b, h, str(nkeys), str(len(counted)), f"{rel:.3g}",
                      str(len(cdiff)) if same_files else "-", str(n), ";".join(sorted(procs)), note or "-",
                      str(len(enters["A"])), str(len(enters["B"]))])
        print(f"card {card or '(none)'} {sha[:12]} (B {sha_b[:12]}), param card {h[:12]} ({n} rows of {', '.join(sorted(procs))}): "
              f"{nkeys} vertices by orders, {len(counted)} differ" + (f" (largest {rel:.3g})" if counted else "")
              + (f", {len(cdiff)} couplings differ" if same_files else "")
              + "".join(f", {len(enters[s])} only in {s} that the rows' processes can contain (of {len(lone[s])})" for s in "AB" if lone[s])
              + (f"   [{note}]" if note else ""), flush=True)
        for s, ks in lone.items():
            inside = set(enters[s])
            for key in ks:
                x, y = va.get(key, (np.zeros(B.points), 0.0))[0][0], vb.get(key, (np.zeros(B.points), 0.0))[0][0]
                details.append([card or "-", sha, h, f"vertex in {s} only" + ("" if key in inside else ", in no tree diagram of the rows' processes"),
                                " ".join(map(str, key[0])) + " " + ",".join(f"{o}={p}" for o, p in key[1]), f"{x:.10g}", f"{y:.10g}", "-", "-"])
        for what, items in (("", counted), ("rounding", rounding), ("no tree", outside)):
            for r, key, x, y, only in items[:12]:
                print(f"   {what + ' ' if what else ''}{r:.3g}  {key[0]} {dict(key[1])}: {x:.6g} vs {y:.6g} {only}")
        for r, name, x, y in cdiff[:12]:
            print(f"   {r:.3g}  {name}: {x:.6g} vs {y:.6g}")
        for what, items in (("vertex", counted), ("vertex, differs only in rounding", rounding),
                            ("vertex, in no tree diagram of the rows' processes", outside)):
            for r, key, x, y, only in items:
                details.append([card or "-", sha, h, what, " ".join(map(str, key[0])) + " " + ",".join(f"{o}={p}" for o, p in key[1]),
                                f"{x:.10g}", f"{y:.10g}", f"{r:.6g}", only or "-"])
        for r, name, x, y in cdiff:
            details.append([card or "-", sha, h, "coupling", name, f"{x:.10g}", f"{y:.10g}", f"{r:.6g}", "-"])
        for side, fused in (("A", fused_a), ("B", fused_b)):
            for name, main, s, true, used in fused:
                print(f"   {side} fuses {name} into {'-' if s < 0 else ''}{main}: {true:.6g} at the run, MadGraph uses {used:.6g}")
                details.append([card or "-", sha, h, f"fused in {side}", f"{name} into {'-' if s < 0 else ''}{main}", f"{true:.10g}", f"{used:.10g}", "-", "-"])
    with open(args.out, "w") as f:
        f.write("model_a\tmodel_b\tcard\tcard_sha256\tcard_b\tparam_card\tkeys\tdiffering\tmax_rel\tcouplings_differing\trows\tprocesses\tnotes"
                "\tkeys_only_a\tkeys_only_b\n")
        for l in lines:
            f.write("\t".join([A.version, B.version] + l) + "\n")
    dp = re.sub(r"\.tsv$", "", args.out) + ".details.tsv"
    with open(dp, "w") as f:
        f.write("card\tcard_sha256\tparam_card\twhat\tname\ta\tb\trel\tnote\n")
        for l in details:
            f.write("\t".join(l) + "\n")
    print(f"wrote {args.out} and {dp}")
    return 0 if all(l[5] == "0" for l in lines) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
