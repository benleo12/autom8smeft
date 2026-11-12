#!/usr/bin/env python3
"""The export checks of a model of order N (gen/towers.py), which it must pass before it is released.

    python3 validate/geo_export_check.py UFO N [--ref REF] [--ref-legs K] [--prov DIR_OR_FILE ...] [--blocks FILE]
                                                [--low UFO [--only6]] [--raw] [--seed S]

examples/release_model.sh runs them on a model whose name ends in _geo<N> before it replaces the release, and
hpc/build_geo.sh check runs that.  Each check prints PASS or FAIL, and the script exits 1 when one fails.

How the vertices of the model enter (hpc/build_geo.sh).  The vertices with at most three legs come from the base
of order N (base_geo<N>_mw.fr, every series of its Standard-Model Lagrangian cut at t^N, t = 1/Lambda^2) and from
the blocks of the geo tree, G6cl* (the dimension-six classes with the corrections to order N - 1), G8op* (the
dimension-eight connection operators, to order N - 2) and T<d>op* (the members of dimension d, to order
N - (d - 4)/2), all but two of them computed with at most three legs (DIM8_MAXLEGS=3).  The vertices with four
or more legs come from the caches of the release (L6cl*, L8op*), whose vertices with at most three legs the
writer leaves out where a geo block gives them (DIM8_DROPBELOW), from the base, and from the two geo blocks
computed with every leg, G6cl4 and the G8op of Q_{G^2H^4}^{(1)}, whose gluon operators are vev-subtracted and so
replace their release blocks whole.  The writer then keeps the pieces of each vertex through NP = N when it has
at most three legs and through NP = 2 when it has more (validate/np_truncate.m with DIM8_GEO_N), NP counting
powers of 1/Lambda^2.  The checks:

1. Orders.  The NP order of every coupling is its power of 1/Lambda^2.  Every coupling is evaluated with every
   coefficient at a random value, at Lam = 500 GeV and at 1000 GeV, and a coupling of order NP = n must fall by
   4^n, to the rounding of its terms, which the evaluation follows operation by operation (Evaluator), so that
   the test is exact up to that rounding and needs no tolerance chosen by hand.  A term of another order in the
   coupling moves the ratio: a series piece of another order, a coefficient with the scale of another
   dimension, a parameter that hides an order (vevT), a second scale.  Every name in a coupling or a parameter
   must be defined, every vertex with at most three legs is of order NP <= N, no coupling of order NP = n
   holds a coefficient of an order above n, and the NP expansion order of coupling_orders.py is at least N,
   which MadGraph needs for NP<=N (not with --raw, a model as the writer leaves it, at 2 until
   examples/release_model.sh raises it).
2. Four or more legs.  Every coupling of a vertex with four or more legs is of order NP <= 2 and depends,
   through any chain of internal parameters, on no coefficient above dimension eight (blocks DIM10, DIM10F, ...,
   GEOGF) and no internal parameter of order three or more (L10, gw3, vev3, ...).  That is the content of the
   release through 1/Lambda^4, the Standard-Model quartic couplings included: the operators of dimension six and
   eight, the products of the dimension-six ones with the first-order shifts of the inputs and fields, and the
   shifts of the Standard-Model couplings through second order.
3. Coefficient blocks.  DIM<d> for d = 10, ..., 2N + 4 holds the members of gen/towers.py of dimension d and
   nothing else, DIM<d>F and GEOGF hold coefficients of dimension d in that range, there is no block above
   dimension 2N + 4, every (block, code) of the card is unique, and Lam is the one scale: no other external
   parameter has a name starting with Lam.
4. Included once, by block (--prov, the files the writer records with DIM8_PROVENANCE, one per shard, which
   hpc/write_shards.sh keeps in build/shards/<name>/).  A coefficient may reach a vertex of at most three legs
   (by its fields) from one block only, and every block of --blocks was written in exactly one shard.  A release
   block whose vertices of at most three legs were not left out gives the coefficients of its operator to the
   vertices its geo block gives them to, and fails this, as does a block written in two shards.  The base is
   not a block: the operators of the Yukawa compensation reach the Yukawa vertices from it and from their own
   blocks, which is the compensation.
5. Included once, against a reference (--ref, the release dim68_mw or the model of order 2).  At NP <= 2 the
   model is the dimension-six/eight model: every vertex with at most --ref-legs legs (default every vertex),
   evaluated as validate/compare_ufo.py evaluates one, with random wavefunctions and momenta and every
   coefficient that both models have at a random value, has the same value in both models for each set of
   coupling orders, and neither has one the other lacks.  A vertex counted twice at NP = 1 or 2 is off by its
   own size.  At N = 2 this is the whole model, and at N > 2 the orders NP = 3, ..., N of the vertices of at most
   three legs come from the base and the geo blocks alone, which check 4 sees and check 6 compares.
6. At most three legs, order by order, against the blocks written without the truncation (--low, the UFO of the
   step low of hpc/build_geo.sh).  The writer takes the cached blocks to the model through the flavour rules,
   DIM8_DROPBELOW, the merging of the vertices of one particle content, validate/np_truncate.m with its cap N
   and the join of the shards, and above NP = 2 no other check compares what comes out with what went in:
   check 5 stops at NP = 2, validate/geo_tower_check.py reads the leading order of one coefficient at a time,
   and check 4 counts inclusions.  --low is the same blocks of the geo tree and the base written in one piece,
   with at most three legs and the plain cut of validate/fr_writeufo.wls (DIM8_ORDERCUT: the terms of NP order
   at most N by the orders of their parameters, nothing else removed), so without np_truncate.m, the release
   blocks, DIM8_DROPBELOW or the join.  Every vertex of at most three legs, evaluated as in check 5 with every
   coefficient at a random value, must have the same value in both for each NP order through N, the couplings
   of one NP order summed whatever their other orders, since a piece that vanishes through the parameter
   relations is removed from the model and left in --low as couplings that cancel.  A piece of order three or
   more that the truncation removed, a block written from another cache than --low, a vertex of at most three
   legs that a release block still gives, all move a value.  The check fails too when it compares nothing at
   one of the orders 3, ..., N, which a --low without them would let pass.  What the two have in common it
   does not see: the flavour rules, FeynRules' merging and WriteUFO act on both, as they do at NP <= 2, where
   check 5 compares their result with the release.

couplings.py and vertices.py are read as text (read_ufo), since importing those of a whole model takes gigabytes,
and parameters.py, particles.py and lorentz.py are imported.  Needs numpy, which validate/compare_ufo.py imports.
"""
import argparse
import ast
import cmath
import collections
import glob
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from compare_ufo import coefficient, leave_ufo, use_ufo  # noqa: E402
from generic_inputs import generic_value  # noqa: E402

EPS = sys.float_info.epsilon
# the rounding a coupling may show, in units of its error scale (Evaluator): the scale follows each operation to
# first order, so a homogeneous coupling stays within a few units of it and 64 leaves room for the second order
LIMIT = 64 * EPS
LAM = 500.0
COEF_BLOCK = re.compile(r"DIM\d+F?|GEOGF")
TOWER_BLOCK = re.compile(r"DIM(1[0-9]|[2-9][0-9])F?|GEOGF")
NAME = re.compile(r"(?<![\w.])[A-Za-z_]\w*")   # a name, not an attribute (cmath.sqrt) or a digit


# ---- the model as text ---------------------------------------------------------------------------------------

COUPLING = re.compile(r"^(\w+) = Coupling\(name = '\w+',\s*value = ('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\"),"
                      r"\s*order = \{([^}]*)\}\)", re.M)
VERTEX = re.compile(r"^(\w+) = Vertex\(name = '\w+',\s*particles = \[([^\]]*)\],\s*color = \[([^\]]*)\],"
                    r"\s*lorentz = \[([^\]]*)\],\s*couplings = \{([^}]*)\}\)", re.M)
ENTRY = re.compile(r"\((\d+),\s*(\d+)\)\s*:\s*(\[[^\]]*\]|C\.\w+)")


class Model:
    """A UFO read as plain data.  couplings: {name: (value, {order: n})}.  vertices: [(name, [particle],
    [colour], [Lorentz object], {(ci, li): [coupling name]})], the particles and Lorentz structures the
    objects of particles.py and lorentz.py.  P: the module parameters.py.  F: the callables of
    function_library.py, with cmath and math.  expansion: the NP expansion order of coupling_orders.py."""

    def __init__(self, ufo, keep=None):
        self.ufo = os.path.abspath(ufo)
        use_ufo(self.ufo)
        try:
            import function_library as Fl
            import lorentz as Lm
            import parameters as Pm
            import particles as Pa
            self.P = Pm
            self.F = {k: v for k, v in vars(Fl).items() if callable(v)}
            self.F.update(cmath=cmath, math=math, complex=complex, abs=abs)
            part = {k: v for k, v in vars(Pa).items() if hasattr(v, "pdg_code")}
            lor = {k: v for k, v in vars(Lm).items() if hasattr(v, "structure")}
        finally:
            leave_ufo(self.ufo)
        txt = open(os.path.join(self.ufo, "coupling_orders.py")).read()
        m = re.search(r"NP = CouplingOrder\(name = 'NP',\s*expansion_order = (\d+)", txt)
        self.expansion = int(m.group(1)) if m else None
        self.vertices = []
        txt = open(os.path.join(self.ufo, "vertices.py")).read()
        # a vertex this pattern does not read would go unchecked, so the two counts must agree
        self.unread = len(re.findall(r"^\w+ = Vertex\(", txt, re.M))
        for m in VERTEX.finditer(txt):
            self.unread -= 1
            ps = [part[x.strip()[2:]] for x in m.group(2).split(",") if x.strip()]
            if keep is not None and not keep(ps):
                continue
            cols = ast.literal_eval("[" + m.group(3) + "]")
            ls = [lor[x.strip()[2:]] for x in m.group(4).split(",") if x.strip()]
            cps = {}
            for e in ENTRY.finditer(m.group(5)):
                names = [x.strip()[2:] for x in e.group(3).strip("[]").split(",") if x.strip()]
                cps[(int(e.group(1)), int(e.group(2)))] = names
            self.vertices.append((m.group(1), ps, cols, ls, cps))
        del txt
        want = None if keep is None else {c for v in self.vertices for cs in v[4].values() for c in cs}
        self.couplings = {}
        txt = open(os.path.join(self.ufo, "couplings.py")).read()
        for m in COUPLING.finditer(txt):
            if want is None or m.group(1) in want:
                order = ast.literal_eval("{" + m.group(3) + "}")
                self.couplings[m.group(1)] = (ast.literal_eval(m.group(2)), order)
        del txt

    def externals(self):
        return [p for p in self.P.all_parameters if p.nature == "external"]

    def internals(self):
        return [p for p in self.P.all_parameters if p.nature == "internal"]


def coefficient_order(p):
    """The order in 1/Lambda^2 of the coefficient p, or None for an external parameter that is not one (the scale
    Lam sits in block DIM8)."""
    if p.name == "Lam":
        return None
    if p.lhablock == "DIM6":
        return 1
    if p.lhablock in ("DIM8", "DIM8F"):
        return 2
    m = re.fullmatch(r"DIM(\d+)F?", p.lhablock)
    if m:
        return (int(m.group(1)) - 4) // 2
    if p.lhablock == "GEOGF":
        return (int(re.match(r"c(\d+)", p.name).group(1)) - 4) // 2
    return None


# ---- values with their rounding -------------------------------------------------------------------------------

class Evaluator:
    """The value of an expression of a UFO and the scale of its rounding error: a value v with error scale e has
    a rounding error of about EPS * e.  The inputs are exact (scale 0), and each operation adds the modulus of its
    result to the scale of the errors it carries forward, to first order.  Two evaluations of a coupling that is
    homogeneous in 1/Lambda^2, at Lam and 2 Lam, then agree with the factor 4^-n to within a few EPS times their
    scales, whatever the cancellations inside it, while a piece of another order of the size of the rounding
    scale would show.  Sums and products are walked as chains, since a long sum is a left spine of thousands of
    nodes."""

    def __init__(self, functions):
        self.F = functions

    def __call__(self, node, V, E):
        t = type(node)
        if t is ast.Constant:
            return node.value, 0.0
        if t is ast.Name:
            return V[node.id], E.get(node.id, 0.0)
        if t is ast.BinOp:
            op = type(node.op)
            if op in (ast.Add, ast.Sub):
                chain, n = [], node
                while type(n) is ast.BinOp and type(n.op) in (ast.Add, ast.Sub):
                    chain.append((type(n.op) is ast.Sub, n.right))
                    n = n.left
                v, e = self(n, V, E)
                for neg, r in reversed(chain):
                    a, ea = self(r, V, E)
                    v = v - a if neg else v + a
                    e = e + ea + abs(v)
                return v, e
            if op in (ast.Mult, ast.Div):
                chain, n = [], node
                while type(n) is ast.BinOp and type(n.op) in (ast.Mult, ast.Div):
                    chain.append((type(n.op) is ast.Div, n.right))
                    n = n.left
                v, e = self(n, V, E)
                for div, r in reversed(chain):
                    a, ea = self(r, V, E)
                    if div:
                        w = v / a
                        e = e / abs(a) + abs(w) * ea / abs(a) + abs(w)
                    else:
                        w = v * a
                        e = e * abs(a) + abs(v) * ea + abs(w)
                    v = w
                return v, e
            if op is ast.Pow:
                a, ea = self(node.left, V, E)
                k, ek = self(node.right, V, E)
                v = a ** k
                if a == 0:
                    return v, ea ** abs(k) if ea else 0.0
                return v, abs(k) * abs(v) * ea / abs(a) + abs(v) * abs(cmath.log(a)) * ek + abs(v)
            raise ValueError(f"operator {op.__name__} not handled")
        if t is ast.UnaryOp:
            a, ea = self(node.operand, V, E)
            if type(node.op) is ast.USub:
                return -a, ea
            if type(node.op) is ast.UAdd:
                return a, ea
            raise ValueError(f"unary operator {type(node.op).__name__} not handled")
        if t is ast.Call:
            f = self.function(node.func)
            args = [self(x, V, E) for x in node.args]
            if f is complex:
                return complex(*(a for a, _ in args)), sum(e for _, e in args)
            if len(args) != 1:
                v = f(*(a for a, _ in args))
                return v, sum(e for _, e in args) + abs(v)
            (a, ea), = args
            v = f(a)
            name = getattr(f, "__name__", None) or getattr(f, "name", "")
            if name in ("complexconjugate", "re", "im", "abs", "conjugate"):
                return v, ea
            if name == "sqrt":
                return v, (ea / (2 * abs(v)) if v != 0 else math.sqrt(ea)) + abs(v)
            # any other function: its derivative, numerically, times the error carried in
            h = 1e-6 * max(abs(a), 1.0)
            d = (f(a + h) - f(a - h)) / (2 * h)
            return v, abs(d) * ea + abs(v)
        if t is ast.Attribute:
            return self.function(node), 0.0
        raise ValueError(f"{t.__name__} not handled")

    def function(self, node):
        if type(node) is ast.Name:
            return self.F[node.id]
        if type(node) is ast.Attribute and type(node.value) is ast.Name:
            return getattr(self.F[node.value.id], node.attr)
        raise ValueError(f"call of {ast.dump(node)} not handled")


def parse(text):
    return ast.parse(text, mode="eval").body


def point(model, lam, seed):
    """{name: value} and {name: error scale} of every parameter, with every coefficient at a random value fixed
    by its name and the seed, the inputs that are zero on the card at values of their own
    (validate/generic_inputs.py) and Lam at lam.  Raises on an undefined name."""
    ev = Evaluator(model.F)
    V, E = {}, {}
    for p in model.externals():
        if p.name == "Lam":
            V[p.name] = lam
        elif coefficient_order(p) is not None:
            V[p.name] = coefficient(p.name, seed)
        else:
            V[p.name] = generic_value(p.name, float(p.value), p.lhablock)
    for p in model.internals():
        try:
            V[p.name], E[p.name] = ev(parse(p.value), V, E)
        except KeyError as k:
            raise SystemExit(f"FAIL: the parameter {p.name} uses {k}, which parameters.py does not define before it")
    return V, E


def homogeneous(v1, e1, v2, e2, n):
    """Whether v2 = 4^-n v1 within the rounding, the second value at twice the scale of the first."""
    s = 4.0 ** -n
    return abs(v2 - s * v1) <= LIMIT * (e2 + s * e1) + 1e-300


def apparent_order(v1, v2):
    """log_4 of v1/v2, the order a single power of 1/Lambda^2 would have, for a report."""
    if v1 == 0 or v2 == 0:
        return float("nan")
    return math.log(abs(v1 / v2)) / math.log(4)


# ---- 1, 2: the orders ---------------------------------------------------------------------------------------

def check_orders(model, N, raw=False, seed=1, out=print):
    """Checks 1 and 2.  Returns the list of problems (empty when both pass), and prints a line for each."""
    problems = []
    V1, E1 = point(model, LAM, seed)
    V2, E2 = point(model, 2 * LAM, seed)
    ev = Evaluator(model.F)
    # the internal parameters: of which order each is, where it is of one
    order_of = {}
    for p in model.internals():
        v1, v2 = V1[p.name], V2[p.name]
        if not (cmath.isfinite(complex(v1)) and cmath.isfinite(complex(v2))):
            problems.append(f"parameter {p.name} is not finite at the probe: {v1}")
            continue
        for n in range(0, 2 * N + 3):
            if homogeneous(v1, E1[p.name], v2, E2[p.name], n):
                order_of[p.name] = n
                break
    ext = {p.name: p for p in model.externals()}
    coef = {k: coefficient_order(p) for k, p in ext.items() if coefficient_order(p) is not None}
    # an internal parameter written with coefficients alone (a complex coefficient from its Re and Im parts) has
    # the order of the highest of them
    for p in model.internals():
        uses = set(NAME.findall(p.value)) - set(model.F)
        if p.name.startswith("c") and uses and uses <= set(coef):
            coef[p.name] = max(coef[w] for w in uses)
    # what each parameter depends on, through any chain: a coefficient of an order above 2 or an internal
    # parameter of order 3 or more makes it "high"
    high = {k for k, o in coef.items() if o > 2}
    for p in model.internals():
        uses = set(NAME.findall(p.value))
        if order_of.get(p.name, 0) > 2 or uses & high:
            high.add(p.name)
    known = set(V1) | set(model.F)
    nbad, worst, count, n3, n4 = collections.Counter(), {}, 0, collections.Counter(), collections.Counter()
    seen = {}
    for vname, ps, cols, ls, cps in model.vertices:
        legs = len(ps)
        names = [p.name for p in ps]
        for key, cs in cps.items():
            for c in cs:
                if c not in model.couplings:
                    problems.append(f"{vname} {names}: coupling {c} is not defined in couplings.py")
                    continue
                value, order = model.couplings[c]
                n = order.get("NP", 0)
                (n3 if legs <= 3 else n4)[n] += 1
                if c in seen and seen[c] == legs:
                    continue
                seen[c] = legs
                count += 1
                if legs <= 3 and n > N:
                    nbad["above N"] += 1
                    problems.append(f"{vname} {names}: {c} of order NP {n} > N = {N} on a vertex of {legs} legs")
                if legs >= 4 and n > 2:
                    nbad["four legs above 2"] += 1
                    problems.append(f"{vname} {names}: {c} of order NP {n} on a vertex of {legs} legs, above the "
                                    f"1/Lambda^4 its content is complete to")
                uses = set(NAME.findall(value))
                undefined = sorted(uses - known)
                if undefined:
                    problems.append(f"{vname} {names}: {c} uses names that are not defined: {undefined}")
                    continue
                over = sorted(w for w in uses if coef.get(w, 0) > n)
                if over:
                    problems.append(f"{vname} {names}: {c} of order NP {n} holds coefficients of a higher order: {over}")
                if legs >= 4 and uses & high:
                    nbad["four legs high"] += 1
                    problems.append(f"{vname} {names}: {c} depends on parameters of order three or more: "
                                    f"{sorted(uses & high)[:6]}")
                tree = parse(value)
                v1, e1 = ev(tree, V1, E1)
                v2, e2 = ev(tree, V2, E2)
                if not (cmath.isfinite(complex(v1)) and cmath.isfinite(complex(v2))):
                    problems.append(f"{vname} {names}: {c} is not finite at the probe")
                    continue
                if not homogeneous(v1, e1, v2, e2, n):
                    nbad["order"] += 1
                    r = abs(v2 - 4.0 ** -n * v1) / (e2 + 4.0 ** -n * e1 + 1e-300) / EPS
                    if len(problems) < 10000:
                        problems.append(f"{vname} {names}: {c} declared NP {n} but does not fall as 4^-{n} "
                                        f"(apparent order {apparent_order(v1, v2):.3f}, off by {r:.3g} rounding units)")
                    worst[c] = r
    if not raw and (model.expansion is None or model.expansion < N):
        problems.append(f"coupling_orders.py: the NP expansion order is {model.expansion}, below N = {N}")
    out(f"orders: {count} couplings on {len(model.vertices)} vertices, at most three legs by NP order "
        f"{dict(sorted(n3.items()))}, four or more legs {dict(sorted(n4.items()))}; {len(order_of)} of "
        f"{len(model.internals())} internal parameters of a single order (the others: "
        f"{sorted(p.name for p in model.internals() if p.name not in order_of)[:8]}), {len(high - set(coef))} of "
        f"order three or more; NP expansion order {model.expansion}{' (raw model, not required)' if raw else ''}")
    if model.unread:
        problems.append(f"vertices.py: {model.unread} vertices opened that this script cannot read")
    return problems


# ---- 3: the blocks of the coefficients ------------------------------------------------------------------------

def tower_names(N):
    """{d: the coefficients of the members of dimension d}, d = 10, ..., 2N + 4, from gen/towers.py."""
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    import towers
    return {d: {o.wc for o in towers.tower(d)} for d in range(10, 2 * N + 5, 2)}


def check_blocks(model, N, expected=None, out=print):
    """Check 3.  expected: {d: coefficient names} of the members (gen/towers.py when None)."""
    problems = []
    ext = model.externals()
    codes = collections.Counter((p.lhablock, tuple(p.lhacode)) for p in ext)
    problems += [f"the card entry {b} {list(c)} is used {k} times" for (b, c), k in codes.items() if k > 1]
    scales = sorted(p.name for p in ext if p.name.startswith("Lam"))
    if scales != ["Lam"]:
        problems.append(f"the scales of the card are {scales}: the model has the one scale Lam")
    expected = tower_names(N) if expected is None else expected
    got = collections.defaultdict(set)
    for p in ext:
        m = re.fullmatch(r"DIM(\d+)(F?)", p.lhablock)
        if p.lhablock == "GEOGF" or (m and int(m.group(1)) >= 10):
            d = int(re.match(r"c(\d+)", p.name).group(1)) if re.match(r"c\d+", p.name) else None
            blockd = int(m.group(1)) if m else d
            if d is None or d != blockd:
                problems.append(f"{p.name} in block {p.lhablock}: a coefficient of block {p.lhablock} is c<{blockd}>...")
                continue
            if d > 2 * N + 4:
                problems.append(f"{p.name} in block {p.lhablock}: dimension {d} is above 2N + 4 = {2 * N + 4}")
            if m and not m.group(2):
                got[d].add(re.sub(r"(Re|Im)$", "", p.name))
    for d, names in expected.items():
        if got.get(d, set()) != names:
            miss, extra = sorted(names - got.get(d, set())), sorted(got.get(d, set()) - names)
            problems.append(f"block DIM{d}: members missing {miss[:8]}{' ...' if len(miss) > 8 else ''}, "
                            f"coefficients that are no member {extra[:8]}{' ...' if len(extra) > 8 else ''}")
    for d in sorted(set(got) - set(expected)):
        problems.append(f"block DIM{d} is not a dimension of the model of order {N}")
    towers = ', '.join(f'DIM{d} {len(got.get(d, ()))}' for d in sorted(expected)) or f'none at N = {N}'
    out(f"blocks: {len(ext)} external parameters, tower coefficients by block {towers}, "
        f"GEOGF {sum(1 for p in ext if p.lhablock == 'GEOGF')}, scales {scales}")
    return problems


# ---- 4: included once, by block -----------------------------------------------------------------------------

def read_provenance(paths):
    """{shard file: {"loaded": {block: (n3, n4)}, "rows": [(block, fields, coefficient)], "end": blocks or None}}
    of the files the writer records with DIM8_PROVENANCE (a directory stands for its *.prov).  "end" is the count
    of its last line, "#end TAB <blocks>", and None for a record without it, which was cut off."""
    files = []
    for p in paths:
        files += sorted(glob.glob(os.path.join(p, "*.prov"))) if os.path.isdir(p) else [p]
    out = {}
    for f in files:
        d = {"loaded": {}, "rows": [], "end": None}
        for line in open(f):
            x = line.rstrip("\n").split("\t")
            if d["end"] is not None and line.strip():
                raise SystemExit(f"{f}: a line after the end line: {line.strip()[:120]}")
            if len(x) == 2 and x[0] == "#end" and x[1].isdigit():
                d["end"] = int(x[1])
            elif len(x) == 4 and x[1] == "loaded":
                d["loaded"][x[0]] = (int(x[2]), int(x[3]))
            elif len(x) == 4 and x[1] == "vertex":
                d["rows"].append((x[0], x[2], x[3]))
            elif line.strip():
                raise SystemExit(f"{f}: not a line of a provenance file: {line.strip()[:120]}")
        out[f] = d
    return out


def geo_block(b):
    return re.fullmatch(r"G6cl\w+|G8op\d+|T\d+op\d+", b) is not None


def check_provenance(prov, blocks=None, out=print):
    """Check 4, on read_provenance(...), with blocks the block list of the model or None."""
    problems = []
    where = collections.defaultdict(list)
    for f, d in prov.items():
        for b in d["loaded"]:
            where[b].append(os.path.basename(f))
    problems += [f"block {b} is written in {len(fs)} shards: {fs}" for b, fs in sorted(where.items()) if len(fs) > 1]
    # a record ends with the count of its blocks, so that one cut off while it was written is not read as whole
    for f, d in sorted(prov.items()):
        if d.get("end") is None:
            problems.append(f"{os.path.basename(f)} has no end line: the record was cut off")
        elif d["end"] != len(d["loaded"]):
            problems.append(f"{os.path.basename(f)} ends with {d['end']} blocks and records {len(d['loaded'])}")
    if blocks is not None:
        missing = sorted(set(blocks) - set(where))
        extra = sorted(set(where) - set(blocks))
        if missing:
            problems.append(f"{len(missing)} blocks of the model are in no provenance file: {missing[:10]}"
                            + (" ..." if len(missing) > 10 else ""))
        if extra:
            problems.append(f"{len(extra)} blocks written that the model does not list: {extra[:10]}")
    src = collections.defaultdict(set)
    release_low = collections.Counter()
    for f, d in prov.items():
        for b, fields, c in d["rows"]:
            src[(fields, c)].add(b)
            if not geo_block(b):
                release_low[b] += 1
    twice = {k: bs for k, bs in src.items() if len(bs) > 1}
    for (fields, c), bs in sorted(twice.items())[:30]:
        problems.append(f"{c} reaches the vertex {{{fields}}} from {len(bs)} blocks: {sorted(bs)}")
    if len(twice) > 30:
        problems.append(f"... {len(twice) - 30} more (coefficient, vertex) pairs from more than one block")
    n3 = sum(v[0] for d in prov.values() for v in d["loaded"].values())
    out(f"provenance: {len(where)} blocks in {len(prov)} shards, {n3} vertices of at most three legs, "
        f"{len(src)} (coefficient, vertex) pairs; release blocks with vertices of at most three legs: "
        f"{len(release_low)}{' ' + str(sorted(release_low)[:8]) if release_low else ''}")
    return problems


# ---- 5: included once, against a reference --------------------------------------------------------------------

def vertex_values(model, switched, seed, maxlegs=None, maxnp=2, points=2, by_np=False):
    """{(sorted particles, orders): [value at each point]} of the vertices of at most maxlegs legs, from the
    couplings of order NP <= maxnp, as validate/compare_ufo.py evaluates them, with the coefficients in
    switched at random values and the others at their card values, and Lam at 1 TeV.  With by_np the couplings
    of one NP order are summed whatever their other orders."""
    import random
    import numpy as np  # noqa: F401  (compare_ufo's structures)
    import zero_vertex as Z
    from compare_ufo import Point, scalar
    ns = {"cmath": cmath, "math": math, "complex": complex}
    ns.update(model.F)
    vals = {}
    for p in model.externals():
        v = float(p.value)
        if p.name == "Lam":
            v = 1000.0
        elif coefficient_order(p) is not None:
            v = coefficient(p.name, seed) if p.name in switched else v
        else:
            v = generic_value(p.name, v, p.lhablock)
        vals[p.name] = v
    for p in model.internals():
        vals[p.name] = eval(p.value, ns, vals)
    code = {}
    comp = lambda s: code.setdefault(s, compile(s, "<structure>", "eval"))
    out = collections.defaultdict(lambda: [0j] * points)
    for vname, ps, cols, ls, cps in model.vertices:
        names = [p.name for p in ps]
        if maxlegs is not None and len(names) > maxlegs:
            continue
        terms = []
        for (ci, li), cs in cps.items():
            for c in cs:
                value, order = model.couplings[c]
                if order.get("NP", 0) <= maxnp:
                    key = (("NP", order.get("NP", 0)),) if by_np else tuple(sorted(order.items()))
                    terms.append((ci, li, (tuple(sorted(names)), key), complex(eval(comp(value), ns, vals))))
        if not terms:
            continue
        order = sorted(range(len(names)), key=lambda k: (names[k], k))
        pos = {order[j] + 1: j for j in range(len(order))}
        ferm = [k for k in order if ps[k].spin % 2 == 0]
        sgn = [1] * len(ls)
        if len(ferm) >= 4:
            eps = Z.order_sign(ferm)
            for li, lo in enumerate(ls):
                s = Z.structure_sign(lo.structure)
                if s is None:
                    raise SystemExit(f"{model.ufo}: no fermion flow for {lo.name} = {lo.structure}")
                sgn[li] = eps * s
        for pt in range(points):
            rng = random.Random(f"{seed}:{pt}:{'/'.join(sorted(names))}")
            P = Point([ps[k].color for k in order], pos, rng)
            lns, cns = P.lorentz_ns(), P.colour_ns()
            lor = [sgn[li] * scalar(eval(comp(lo.structure), lns)) for li, lo in enumerate(ls)]
            col = [scalar(eval(comp(c), cns)) for c in cols]
            for ci, li, key, g in terms:
                out[key][pt] += g * col[ci] * lor[li]
    return out


def check_reference(model, ref, maxlegs=None, seed=1, tol=1e-9, out=print):
    """Check 5: the vertices of model and ref at NP <= 2, with every coefficient both have switched on."""
    problems = []
    wa = {p.name for p in model.externals() if coefficient_order(p) is not None}
    wb = {p.name for p in ref.externals() if coefficient_order(p) is not None}
    switched = wa & wb
    A = vertex_values(model, switched, seed, maxlegs)
    B = vertex_values(ref, switched, seed, maxlegs)
    size = lambda x: max(abs(z) for z in x)
    scale = max([size(x) for x in A.values()] + [size(x) for x in B.values()] + [1e-300])
    bad, only = [], [[], []]
    for k in set(A) | set(B):
        x, y = A.get(k), B.get(k)
        if x is None or y is None:
            z = x if y is None else y
            if size(z) > 1e-14 * scale:
                only[0 if y is None else 1].append((size(z), k))
            continue
        d = max(abs(p - q) for p, q in zip(x, y))
        if d > tol * max(size(x), size(y)) and d > 1e-14 * scale:
            bad.append((d / max(size(x), size(y)), k, x[0], y[0]))
    bad.sort(reverse=True)
    for r, k, x, y in bad[:20]:
        problems.append(f"{k[0]} {dict(k[1])}: {x:.8g} here, {y:.8g} in the reference (relative difference {r:.2e})")
    if len(bad) > 20:
        problems.append(f"... {len(bad) - 20} more vertices that differ")
    for side, rows in zip(("here", "in the reference"), only):
        for z, k in sorted(rows, reverse=True)[:10]:
            problems.append(f"{k[0]} {dict(k[1])} only {side}, at {z:.3g}")
        if len(rows) > 10:
            problems.append(f"... {len(rows) - 10} more vertices only {side}")
    out(f"reference {ref.ufo}: {len(switched)} coefficients in both switched on ({len(wa - wb)} only here, "
        f"{len(wb - wa)} only there, at 0), vertices of {'every number of' if maxlegs is None else f'at most {maxlegs}'} "
        f"legs at NP <= 2: {len(A)} here and {len(B)} there by coupling orders, {len(bad)} differ, "
        f"{len(only[0])} only here, {len(only[1])} only there")
    return problems


# ---- 6: at most three legs, order by order, against the blocks written without the truncation -----------------

def check_low(model, low, N, seed=1, tol=1e-9, out=print):
    """Check 6: the vertices of model with at most three legs, NP order by NP order through N, against those of
    low, the blocks of the geo tree and the base written in one piece with the plain cut of
    validate/fr_writeufo.wls (DIM8_ORDERCUT) in place of validate/np_truncate.m, with every coefficient on."""
    problems = []
    wa = {p.name for p in model.externals() if coefficient_order(p) is not None}
    wb = {p.name for p in low.externals() if coefficient_order(p) is not None}
    if wa != wb:
        problems.append(f"the two do not have the same coefficients: {len(wa - wb)} only here {sorted(wa - wb)[:5]}, "
                        f"{len(wb - wa)} only there {sorted(wb - wa)[:5]}")
    switched = wa & wb
    A = vertex_values(model, switched, seed, 3, N, by_np=True)
    B = vertex_values(low, switched, seed, 3, N, by_np=True)
    size = lambda x: max(abs(z) for z in x)
    np_of = lambda k: dict(k[1])["NP"]
    scale = max([size(x) for x in A.values()] + [size(x) for x in B.values()] + [1e-300])
    bad, only, seen = [], [[], []], collections.Counter()
    for k in set(A) | set(B):
        x, y = A.get(k), B.get(k)
        if x is None or y is None:
            # a piece that cancels to rounding, which the truncation removes and the plain cut keeps, is no difference
            z = x if y is None else y
            if size(z) > 1e-14 * scale:
                only[0 if y is None else 1].append((size(z), k))
            continue
        seen[np_of(k)] += 1
        d = max(abs(p - q) for p, q in zip(x, y))
        if d > tol * max(size(x), size(y)) and d > 1e-14 * scale:
            bad.append((d / max(size(x), size(y)), k, x[0], y[0]))
    bad.sort(reverse=True)
    for r, k, x, y in bad[:20]:
        problems.append(f"{k[0]} at NP {np_of(k)}: {x:.8g} here, {y:.8g} from the blocks (relative difference {r:.2e})")
    if len(bad) > 20:
        problems.append(f"... {len(bad) - 20} more vertices that differ")
    for side, rows in zip(("here", "from the blocks"), only):
        for z, k in sorted(rows, reverse=True)[:10]:
            problems.append(f"{k[0]} at NP {np_of(k)} only {side}, at {z:.3g}")
        if len(rows) > 10:
            problems.append(f"... {len(rows) - 10} more vertices only {side}")
    # the comparison must have reached every order: a reference without the orders above 2 would pass an empty test
    high = [n for n in range(3, N + 1) if not seen[n]]
    if high:
        problems.append(f"no vertex compared at NP {high}: the blocks written without the truncation hold none there")
    out(f"blocks without the truncation {low.ufo}: {len(switched)} coefficients switched on, vertices of at most three "
        f"legs compared by NP order: " + ", ".join(f"NP {n}: {seen[n]}" for n in range(N + 1)) +
        f"; {len(bad)} differ, {len(only[0])} only here, {len(only[1])} only there")
    return problems


# ---- the command ----------------------------------------------------------------------------------------------

def report(name, problems, out=print):
    for p in problems[:40]:
        out(f"  {p}")
    if len(problems) > 40:
        out(f"  ... {len(problems) - 40} more")
    out(f"{name}: {'PASS' if not problems else 'FAIL'}")
    return not problems


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("ufo")
    a.add_argument("N", type=int)
    a.add_argument("--ref", help="the model at NP <= 2 to compare with (the release dim68_mw or the model of order 2)")
    a.add_argument("--ref-legs", type=int, default=None, help="compare only the vertices with at most this many legs")
    a.add_argument("--prov", nargs="*", default=None, help="the provenance files of the shards, or their directory")
    a.add_argument("--blocks", help="the block list of the model, for the provenance check")
    a.add_argument("--low", help="the blocks of the geo tree and the base written in one piece without the truncation "
                                 "(validate/fr_writeufo.wls with DIM8_ORDERCUT=1), for check 6")
    a.add_argument("--only6", action="store_true", help="run check 6 alone")
    a.add_argument("--raw", action="store_true", help="a model as the writer leaves it: NP expansion order not required")
    a.add_argument("--seed", type=int, default=1)
    args = a.parse_args(argv)
    if args.N < 2:
        sys.exit("the order N of a model of order N is 2 or more")
    sys.setrecursionlimit(100000)
    print(f"model {args.ufo}, order N = {args.N}")
    ok = True
    model = Model(args.ufo)
    if args.only6:
        if not args.low:
            sys.exit("--only6 needs --low")
        ok = report("6. at most three legs through NP <= N, against the blocks without the truncation",
                    check_low(model, Model(args.low), args.N, args.seed))
        print("EXPORT CHECK 6 " + ("PASS" if ok else "FAIL"))
        return 0 if ok else 1
    ok &= report("1, 2. orders, and four or more legs at NP <= 2", check_orders(model, args.N, args.raw, args.seed))
    ok &= report("3. coefficient blocks", check_blocks(model, args.N))
    if args.prov is not None:
        blocks = [b.strip() for b in open(args.blocks) if b.strip()] if args.blocks else None
        ok &= report("4. included once, by block", check_provenance(read_provenance(args.prov), blocks))
    else:
        print("4. included once, by block: not run (no --prov)")
    if args.ref:
        ref = Model(args.ref)
        ok &= report("5. included once, against the reference at NP <= 2",
                     check_reference(model, ref, args.ref_legs, args.seed))
    else:
        print("5. included once, against a reference: not run (no --ref)")
    if args.low:
        ok &= report("6. at most three legs through NP <= N, against the blocks without the truncation",
                     check_low(model, Model(args.low), args.N, args.seed))
    else:
        print("6. at most three legs through NP <= N, against the blocks without the truncation: not run (no --low)")
    print("EXPORT CHECKS " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
