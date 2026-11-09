#!/usr/bin/env python3
"""The flavour structures of the fermionic operators, checked at generic Yukawa and CKM matrices.

    python3 validate/mfv_generic.py MODEL [--json OUT] [--only NAME,...] [--detail] [--plant ckm|insertion|transpose]

Every fermionic operator carries each of its flavour structures (gen/emit_flavour.py) with a coefficient of its
own: the operator's coefficient for the structure it has always had, and one in the block DIM8F for each further
one (a Y Y^dag insertion, a second contraction of a four-fermion operator).  The default card has every fermion
but the top and bottom quarks massless and no Cabibbo angle, where most of these structures vanish or are
diagonal, so a structure built from the wrong chain, with the CKM matrix on the wrong side, or transposed would go
unseen there.  This evaluates the model at generic inputs instead (validate/generic_inputs.py: every light mass
and the Cabibbo angle at a value of its own between 0.1 and 0.3) and switches on each real parameter of each
structure alone.  Two tests.

  live     it moves a vertex of the model, as validate/index_vs_ufo.py decides that an operator has a vertex:
           the parameter appears by name in a coupling of the vertex, and the linear response, with every
           internal parameter it enters recomputed and summed over the vertex objects of that field content
           per colour structure, exceeds 1e-8 of its triangle-inequality bound.  The Lorentz structures are
           summed as numbers, as MadGraph computes the vertex (validate/zero_vertex.py: each structure at two
           common random kinematic points, a crossed four-fermion structure with the sign MadGraph gives its
           coupling), so that the Fierz-equivalent forms FeynRules writes for identical fermions, and the pairs
           of them that cancel, count as the vertex they make.  A structure that cannot be evaluated is
           compared in its canonical form.

  pattern  wherever it appears, its couplings depend on the generations of the fermions as its flavour tensor
           does.  The tensor is built here from the masses and the Cabibbo angle alone, not from the chain
           parameters of the model: Y_u = diag(y_u), Y_d = V diag(y_d) and Y_e = diag(y_e) in the basis of the
           doublets, with q_i = (u_i, V_ij d_j), the chain of each bilinear from its insertion (CHAIN below, the
           products that minimal flavour violation allows), their product over the bilinears of the structure,
           and V on every slot of a doublet q that a down-type quark fills.  The couplings are taken with every
           internal parameter fixed but the operator's own complex coefficient, so that the shifts of the input
           relations, which multiply Standard Model couplings, do not enter.  For each vertex type (the fields
           without their generations and a colour structure, the Lorentz structures summed as numbers at each
           kinematic point as in the live test) the responses over the
           generations, the vertices the model lacks counted as zero, must be a combination of the tensor
           over the ways the fermions fill the slots of the operator (the term and its conjugate), with one
           constant per way.  The fit is weighted point by point, since the entries span the Yukawa hierarchy,
           and at every point the residual must be below 1e-7 of the size a term of the fit has there.  A
           vertex type with no more generation assignments than independent ways cannot fail and is counted
           apart.

--plant builds an error into the expected tensors, as a model written with it would carry it, and counts the
parameters that then fail: a negative control of the pattern test.  The model is read as text and evaluated with
cmath and numpy.  Every parameter of block DIM8F must be tested, except those of the operators of the other basis
(class 11, gen/basis.py), which parameters.py declares and which must then appear in no coupling.  The exit
status is 1 when a parameter is not live, a pattern fails or block DIM8F is not covered so (with --plant, 0).
"""
import argparse
import cmath
import collections
import itertools
import json
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import basis  # noqa: E402
import cp_parity  # noqa: E402
import emit_flavour as EF  # noqa: E402
import index_vs_ufo as IU  # noqa: E402
import zero_vertex as Z  # noqa: E402
from generic_inputs import generic_value  # noqa: E402
from operators import OPS  # noqa: E402

FIT_TOL = 1e-7
NREP = 2    # the common kinematic points at which the Lorentz structures are evaluated
# the errors --plant builds into the expected tensors, as a model written with them would have them
PLANTS = {"ckm": "V^T in place of V, in Y_d and on the doublet slots",
          "insertion": "the insertions Y_u Y_u^dag and Y_d Y_d^dag swapped wherever the bilinear has both",
          "transpose": "every chain transposed"}
PLANT = None
# the chain of a bilinear psibar_x M chi_y, by its species and insertion, as products of the Yukawa matrices in
# the basis of the doublets ("Yu+" the conjugate transpose): Y_u of q to u, Y_d of q to d, Y_e of l to e, and
# Y Y^dag inserted on the doublet side.  The reversed pairs are the conjugate transposes.
CHAIN = {
    ("q", "q", "U"): ["Yu", "Yu+"], ("q", "q", "D"): ["Yd", "Yd+"],
    ("u", "u", "U"): ["Yu+", "Yu"], ("d", "d", "D"): ["Yd+", "Yd"],
    ("l", "l", "E"): ["Ye", "Ye+"], ("e", "e", "E"): ["Ye+", "Ye"],
    ("q", "u", ""): ["Yu"], ("q", "u", "U"): ["Yu", "Yu+", "Yu"], ("q", "u", "D"): ["Yd", "Yd+", "Yu"],
    ("q", "d", ""): ["Yd"], ("q", "d", "U"): ["Yu", "Yu+", "Yd"], ("q", "d", "D"): ["Yd", "Yd+", "Yd"],
    ("l", "e", ""): ["Ye"], ("l", "e", "E"): ["Ye", "Ye+", "Ye"],
    ("u", "d", ""): ["Yu+", "Yd"], ("u", "d", "U"): ["Yu+", "Yu", "Yu+", "Yd"], ("u", "d", "D"): ["Yu+", "Yd", "Yd+", "Yd"],
}
# the fermions of the UFO by PDG code: family and generation
FERMION = {1: ("d", 0), 3: ("d", 1), 5: ("d", 2), 2: ("u", 0), 4: ("u", 1), 6: ("u", 2),
           11: ("e", 0), 13: ("e", 1), 15: ("e", 2), 12: ("v", 0), 14: ("v", 1), 16: ("v", 2)}
# the families each species of the operators holds
HOLDS = {"q": ("u", "d"), "u": ("u",), "d": ("d",), "l": ("e", "v"), "e": ("e",)}
WORD = re.compile(r"\b[A-Za-z_]\w*\b")


def read(model):
    """The model at generic inputs: the namespace with every parameter evaluated (every coefficient zero), the
    internal parameters in evaluation order, the external parameters by block, the couplings and the vertices."""
    rd = lambda f: open(os.path.join(model, f + ".py")).read()  # noqa: E731
    ns = {"cmath": cmath, "complex": complex, "pi": cmath.pi}
    for m in re.finditer(r"(\w+) = Function\(\s*name = '\w+',\s*arguments = \(([^)]*)\),\s*expression = '([^']*)'",
                         rd("function_library")):
        a = ",".join(x.strip().strip("'\"") for x in m.group(2).split(",") if x.strip())
        ns[m.group(1)] = eval(f"lambda {a}: {m.group(3)}", dict(ns))
    params = re.findall(r"(\w+) = Parameter\(\s*name = '\w+',\s*nature = '(\w+)',\s*type = '\w+',\s*"
                        r"value = ('[^']*'|[^,]+),(.*?)\)\n", rd("parameters"), re.S)
    block, todo = {}, []
    for name, nature, value, rest in params:
        if nature == "external":
            b = re.search(r"lhablock = '(\w+)'", rest).group(1)
            block[name] = b
            # a coefficient as validate/index_vs_ufo.py names one: the scale Lam shares the block DIM8
            coefficient = name.startswith("c8") or re.sub(r"(Abs|Ph|Re|Im)$", "", name) in IU.DIM6_NAMES
            ns[name] = complex(0.0 if coefficient else generic_value(name, eval(value), b))
        else:
            todo.append((name, value.strip("'")))
    order = []
    for _ in range(len(todo) + 1):
        left = []
        for name, value in todo:
            try:
                ns[name] = eval(value, ns)
                order.append((name, value))
            except (NameError, ZeroDivisionError, ValueError, TypeError):
                left.append((name, value))
        if not left or len(left) == len(todo):
            break
        todo = left
    if left:
        sys.exit(f"internal parameters that do not evaluate: {[n for n, _ in left][:10]}")
    # the triangle-inequality bound on every parameter, through the internal ones: FeynRules writes the couplings
    # of a flavour-changing vertex through internal parameters such as I8a21, a sum over the CKM matrix that
    # cancels to round-off where the structure is diagonal, and a bound taken with their values would be
    # round-off too
    nsb = dict(ns)
    for name in block:
        nsb[name] = abs(ns[name])
    for name, value in order:
        nsb[name] = eval(IU._compile(value, bound=True), nsb)
    couplings = dict(re.findall(r"(GC_\w+) = Coupling\(\s*name = '\w+',\s*value = '([^']*)'", rd("couplings")))
    pdg = {}
    ptxt = rd("particles")
    for var, code, name, anti in re.findall(r"(\w+) = Particle\(\s*pdg_code = (-?\d+),\s*name = '([^']*)',\s*antiname = '([^']*)'", ptxt):
        pdg[var] = (name, int(code))
        pdg[var + "__anti"] = (anti, int(code) if anti == name else -int(code))
    for var, base in re.findall(r"(\w+) = (\w+)\.anti\(\)", ptxt):
        pdg[var] = pdg[base + "__anti"]
    lstruct = dict(re.findall(r"(\w+) = Lorentz\(\s*name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '([^']*)'", rd("lorentz")))
    vertices = []
    for parts, col, lor, cpl in re.findall(
            r"Vertex\(\s*name = '\w+',\s*particles = \[([^\]]*)\],\s*color = \[([^\]]*)\],\s*"
            r"lorentz = \[([^\]]*)\],\s*couplings = \{([^}]*)\}", rd("vertices"), re.S):
        plist = [pdg[p] for p in re.findall(r"P\.(\w+)", parts)]
        lors = re.findall(r"L\.(\w+)", lor)
        cols = re.findall(r"'([^']*)'", col)
        vertices.append((plist, [(cols[int(c)], lstruct.get(lors[int(l)], ""), g)
                                 for c, l, g in re.findall(r"\((\d+),(\d+)\):C\.(GC_\w+)", cpl)]))
    return ns, nsb, order, block, couplings, vertices


def matrices(ns):
    """Y_u, Y_d, Y_e in the basis of the doublets and V, from the masses and the Cabibbo angle of the model."""
    val = lambda n: complex(ns[n])  # noqa: E731
    V = np.array([[val(f"CKM{i}x{j}") for j in (1, 2, 3)] for i in (1, 2, 3)])
    if PLANT == "ckm":
        V = V.T
    yu = np.diag([val(n) for n in ("yup", "yc", "yt")])
    yd = np.diag([val(n) for n in ("ydo", "ys", "yb")])
    ye = np.diag([val(n) for n in ("ye", "ym", "ytau")])
    Y = {"Yu": yu, "Yd": V @ yd, "Ye": ye}
    return Y, V


def chain(Y, x, y, lab, bound=False):
    """The matrix of the bilinear xbar M y, or with bound its entry-wise triangle-inequality bound."""
    if x == y and lab == "":
        return np.eye(3, dtype=complex)
    if PLANT == "insertion":
        swap = {"U": "D", "D": "U"}.get(lab, lab)
        if (x, y, swap) in CHAIN or (y, x, swap) in CHAIN:
            lab = swap
    key, dag = ((x, y, lab), False) if (x, y, lab) in CHAIN else ((y, x, lab), True)
    m = np.eye(3, dtype=complex)
    for f in CHAIN[key]:
        y_ = Y[f[:-1]].conj().T if f.endswith("+") else Y[f]
        m = np.abs(m) @ np.abs(y_) if bound else m @ y_
    m = m.conj().T if dag else m
    return m.T if PLANT == "transpose" else m


def tensor(op, s, Y):
    """T^S over the flavour slots of the operator (the order of op.gens), its entry-wise triangle-inequality
    bound, the species of each slot and whether it is barred."""
    k = {g: i for i, g in enumerate(op.gens)}
    T = np.ones((3,) * len(op.gens), dtype=complex)
    Tb = np.ones((3,) * len(op.gens))
    species = [None] * len(op.gens)
    for (a, b), lab, (x, y) in zip(s["pairing"], s["insertions"], s["species"]):
        shape = [1] * len(op.gens)
        shape[k[a]], shape[k[b]] = 3, 3
        for bound in (False, True):
            m = chain(Y, x, y, lab, bound)
            m = (m if k[a] < k[b] else m.T).reshape(shape)
            if bound:
                Tb = Tb * np.abs(m)
            else:
                T = T * m
        species[k[a]], species[k[b]] = x, y
    bars = EF._bars(op)
    return T, Tb, species, [bars[g] for g in op.gens]


def structures(mb):
    """{real parameter: (operator, structure)} for every structure of every fermionic operator of the basis mb
    that conserves baryon number, and the parameters each structure has."""
    data = EF.load_structures()
    bviol = cp_parity.baryon_violating()
    out = {}
    for op in OPS:
        if op.name not in data or op.name in bviol or not basis.in_basis([op.wc], mb):
            continue
        for p in EF.structure_parameters(op, data[op.name]):
            names = [n for n, _, _ in p["externals"]] or None
            out[(op.wc, p["tag"])] = (op, p["structure"], names)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("model")
    ap.add_argument("--json", help="write the result per parameter to this file")
    ap.add_argument("--only", help="comma-separated real parameters to check, for a quick look")
    ap.add_argument("--detail", action="store_true", help="print the responses and the tensors of every vertex type that fails")
    ap.add_argument("--plant", choices=sorted(PLANTS), help="a negative control: build the expected tensors with this error, "
                    "and report how many parameters then fail, which must be every one the error changes")
    a = ap.parse_args(argv)
    global PLANT
    PLANT = a.plant
    assert {k: v for k, v in CHAIN.items()} == EF.CHAINS, "CHAIN differs from the chains of gen/emit_flavour.py"
    ns, nsb, order, block, couplings, vertices = read(a.model)
    Y, V = matrices(ns)
    print(f"{a.model}: cabi {ns['cabi'].real:.4f}, light masses " +
          " ".join(f"{n} {ns[n].real:.3f}" for n in ("ymup", "ymdo", "yms", "ymc", "yme", "ymm", "ymtau")), flush=True)
    mb = basis.of_model(a.model)
    st = structures(mb)
    # the real parameters of each structure: those of block DIM8F, or for the structure an operator has always
    # had, its own coefficient's (Re and Im parts when it is complex)
    params = {}
    for (wc, t), (op, s, names) in st.items():
        if names is None:
            names = [n for n in (wc, wc + "Re", wc + "Im") if n in block]
        for n in names:
            params[n] = (op, s, t)
    # the parameters of block DIM8F that no structure of the basis has: those of the other basis's operators
    # (class 11, which parameters.py declares for both bases) must be in no coupling, through an internal
    # parameter or directly, and any other is a structure this check would miss
    untested = sorted(n for n, b in block.items() if b == "DIM8F" and n not in params)
    other = [n for n in untested if re.sub(r"F\w*$", "", re.sub(r"(Re|Im)$", "", n)) in basis.left_out(mb)]
    missed = [n for n in untested if n not in other]
    carriers = set(other)
    for name, value in order:
        if carriers & set(WORD.findall(value)):
            carriers.add(name)
    pattern = re.compile(r"\b(?:" + "|".join(map(re.escape, sorted(carriers))) + r")\b") if carriers else None
    in_coupling = sorted({g for g, expr in couplings.items() if pattern.search(expr)}) if pattern else []
    if a.only:
        params = {n: params[n] for n in a.only.split(",")}
    # the internal parameters each real parameter enters, through others, in evaluation order (a complex
    # coefficient's own combination first among them)
    deps, chains = {}, collections.defaultdict(list)
    for name, value in order:
        d = set()
        for x in set(WORD.findall(value)):
            d |= {x} if x in params else deps.get(x, set())
        deps[name] = d
        for n in d:
            chains[n].append((name, compile(value, name, "eval"), IU._compile(value, bound=True)))
    value = dict(order)
    own = {n: [c[0] for c in chains[n] if c[0].startswith("c8") and n in WORD.findall(value[c[0]])] for n in params}
    reach = collections.defaultdict(set)      # parameter -> couplings that name it or its own combination
    moved = collections.defaultdict(set)      # parameter -> couplings that move with it through any internal
    names_of = collections.defaultdict(set)
    for n in params:
        for w in [n] + own[n]:
            names_of[w].add(n)
    via = collections.defaultdict(set)
    for n in params:
        for c in chains[n]:
            via[c[0]].add(n)
    for g, expr in couplings.items():
        ws = set(WORD.findall(expr))
        for w in ws:
            for n in names_of.get(w, ()):
                reach[n].add(g)
            for n in via.get(w, ()):
                moved[n].add(g)
    code = {}

    def compiled(g):
        if g not in code:
            code[g] = (IU._compile(couplings[g]), IU._compile(couplings[g], bound=True))
        return code[g]

    # the vertices by coupling, each with the PDG codes and names of its particles
    at = collections.defaultdict(list)
    for vi, (plist, ents) in enumerate(vertices):
        for col, struct, g in ents:
            at[g].append((vi, col, struct))

    results = {}
    for i, (n, (op, s, t)) in enumerate(sorted(params.items())):
        results[n] = check(n, op, s, block, ns, nsb, chains, own, reach, moved, compiled, at, vertices, Y, V, a.detail)
        if (i + 1) % 200 == 0:
            done = list(results.values())
            print(f"  {i + 1} of {len(params)} parameters, {sum(r['live'] for r in done)} live, "
                  f"{sum(not r['live'] or not r['pattern_ok'] for r in done)} failing", flush=True)
    bad = {n: r for n, r in results.items() if not r["live"] or not r["pattern_ok"]}
    con = sum(r["live"] and r["pattern_ok"] and r["constrained"] > 0 for r in results.values())
    free = sum(r["live"] and r["pattern_ok"] and r["constrained"] == 0 for r in results.values())
    print(f"\n{len(params)} real parameters of {len(st)} structures of {len({v[0].name for v in params.values()})} operators "
          f"of the {mb} basis")
    print(f"  block DIM8F, other basis: {len(other)} parameters, of operators the model does not have, in "
          f"{len(in_coupling)} couplings {other[:4]}{' ...' if len(other) > 4 else ''}")
    print(f"  block DIM8F, untested: {len(missed)} {missed[:6]}")
    print(f"  Lorentz structures compared in canonical form, unread: {sum(isinstance(v[0][0], tuple) for v in _LV.values())}")
    print(f"  live: {sum(r['live'] for r in results.values())} of {len(params)}")
    print(f"  pattern: {con} agree on every vertex type, with at least one type that could fail; {free} with no such type")
    print(f"  vertex types: {sum(r['types'] for r in results.values())}, of them {sum(r['constrained'] for r in results.values())} "
          f"that could fail")
    for n, r in sorted(bad.items()):
        print(f"  FAIL {n} ({r['op']}): live {r['live']}, pattern {r['pattern_ok']} {r.get('note', '')}")
        for f in r.get("failures", []):
            print(f"      {f}")
    # the coverage of block DIM8F: a parameter no structure has, or one of the other basis in a coupling
    if missed:
        print(f"  FAIL untested: {len(missed)} parameters of block DIM8F have no structure of the {mb} basis: {missed[:10]}")
    if in_coupling:
        print(f"  FAIL other basis: {len(in_coupling)} couplings carry parameters of the other basis, e.g. {in_coupling[:5]}")
    nfail = len(bad) + bool(missed) + bool(in_coupling)
    if a.json:
        json.dump(dict(model=a.model, basis=mb, untested=missed, other_basis=other, other_basis_couplings=in_coupling,
                       results=results), open(a.json, "w"), indent=1)
    if PLANT:
        print(f"PLANTED {PLANT} ({PLANTS[PLANT]}): {len(bad)} of {len(params)} parameters fail", flush=True)
        return 0
    print("MFVGENERIC " + ("OK" if not nfail else f"FAILED ({nfail})"), flush=True)
    return 1 if nfail else 0


_LV = {}


def _split(s, seps):
    """The pieces of s between the separators seps at bracket depth zero, each with the separator before it."""
    out, d, cur, op = [], 0, "", None
    for ch in s:
        d += (ch == "(") - (ch == ")")
        if ch in seps and d == 0:
            out.append((op, cur))
            cur, op = "", ch
        else:
            cur += ch
    out.append((op, cur))
    return out


def parse_lorentz(struct):
    """A Lorentz structure in the form zero_vertex.parse gives, [(coefficient, [(name, Lorentz indices, spinor
    indices)])], or None.  A bracketed factor is expanded where zero_vertex.parse gives up on it: FeynRules writes
    terms such as (6*Epsilon(3,4,5,-1)*Gamma(-1,2,-2)*Metric(6,7)*ProjM(-2,1))/5. and -0.5*(A*B - C*D), 937 of the
    8598 structures of dim8_mw.  Read in part, a vertex was compared partly as numbers and partly in canonical
    form, and where FeynRules wrote one structure in two normalisations, one of them readable, the split moved
    from one generation to the next: Q_{q^2W^2D}^{(3)} with Y_u Y_u^dag failed on s~ d a W- W+ Z Z, whose
    FFVVVVV153 = -5 FFVVVVV151 carries the term that FFVVVVV151 carries in d~ d, though the vertex follows the
    flavour tensor exactly.  Where zero_vertex.parse reads a structure, the two agree."""
    out = []
    for op, term in _split(struct.replace(" ", ""), "+-"):
        if not term:
            continue                                    # the sign that opens the structure
        prods = [(complex(-1 if op == "-" else 1), [])]
        for fop, f in _split(term, "*/"):
            if not f:
                return None
            m = re.match(r"(\w+)\(([^()]*)\)$", f)
            if m and m.group(1) in Z.SHAPE:
                nl, ns = Z.SHAPE[m.group(1)]
                args = [int(x) for x in m.group(2).split(",")]
                if fop == "/" or len(args) != nl + ns:
                    return None
                prods = [(c, t + [(m.group(1), args[:nl], args[nl:])]) for c, t in prods]
                continue
            try:
                v = complex(eval(f, {"__builtins__": {}}, {"complex": complex}))
            except Exception:
                v = None
            if v is not None:
                prods = [(c / v if fop == "/" else c * v, t) for c, t in prods]
            elif f.startswith("(") and f.endswith(")") and fop != "/":
                sub = parse_lorentz(f[1:-1])
                if sub is None:
                    return None
                prods = [(c1 * c2, t1 + t2) for (c1, t1), (c2, t2) in itertools.product(prods, sub)]
            else:
                return None
        out += prods
    return out


def at_points(struct, nlegs):
    """The Lorentz structure of a vertex entry at the NREP common kinematic points, as MadGraph's amplitude
    carries it (validate/zero_vertex.py: the contraction times the sign MadGraph gives a crossed four-fermion
    flow), [(point, value, size)]; for a structure that cannot be read or evaluated, its canonical form and
    coefficient instead.  Summing the values over the entries of a vertex gives the vertex itself, whichever
    of the Fierz-equivalent forms FeynRules wrote: for identical fermions it writes both pairings, in a form
    that differs from one generation to the next, and validate/drop_zero_structures.py removes pairs that
    cancel, so a comparison form by form would see changes the vertex does not have."""
    k = (struct, nlegs)
    if k not in _LV:
        p = parse_lorentz(struct)
        pts = [Z.evaluate(p, np.random.default_rng(4100 + rep), nlegs) for rep in range(NREP)]
        if any(x is None for x in pts):
            form, c0 = IU._canon(struct)
            _LV[k] = [(("form", form), c0, abs(c0))]
        else:
            _LV[k] = [(rep, x[0], x[1]) for rep, x in enumerate(pts)]
    return _LV[k]


def code_of(t, gen):
    """The PDG code of the vertex-type entry t: a fermion in generation gen, or a boson."""
    if t[0] == "b":
        return t[2]
    c = {"d": (1, 3, 5), "u": (2, 4, 6), "e": (11, 13, 15), "v": (12, 14, 16)}[t[1]][gen]
    return -c if t[2] else c


def evaluate(ns, nsb, code, n, x, which):
    """A compiled coupling and its triangle-inequality bound with parameter n at x, the internal parameters in
    `which` recomputed, the bound through the bounds of the internal parameters."""
    out = []
    for space, k, val in ((ns, 0, x), (nsb, 1, abs(x))):
        keep = {c[0]: space[c[0]] for c in which}
        k0 = space[n]
        space[n] = val
        for c in which:
            space[c[0]] = eval(c[1 + k], space)
        out.append(eval(code[k], space))
        space.update(keep)
        space[n] = k0
    return out


def check(n, op, s, block, ns, nsb, chains, own, reach, moved, compiled, at, vertices, Y, V, detail=False):
    """Both tests for one real parameter."""
    out = dict(op=op.name, structure=EF.describe(op, s), live=False, pattern_ok=False, types=0, constrained=0)
    if n not in block:
        return dict(out, note="not a parameter of the model")
    mine = [c for c in chains[n] if c[0] in own[n]]
    # live: the response with every internal parameter recomputed, per vertex content, colour structure and
    # kinematic point
    tot = collections.defaultdict(lambda: collections.defaultdict(complex))
    bnd = collections.defaultdict(lambda: collections.defaultdict(float))
    named = set()
    for g in reach[n] | moved[n]:
        try:
            code = compiled(g)
            b0 = eval(code[1], nsb)
            vals = {e: evaluate(ns, nsb, code, n, e, chains[n]) for e in (IU.EPS, -IU.EPS, IU.EPS / 2, -IU.EPS / 2)}
        except Exception as e:  # an error, never skipped
            return dict(out, note=f"{g} does not evaluate: {e}")
        d1 = (vals[IU.EPS][0] - vals[-IU.EPS][0]) / (2 * IU.EPS)
        d2 = (vals[IU.EPS / 2][0] - vals[-IU.EPS / 2][0]) / IU.EPS
        r = (4 * d2 - d1) / 3
        sc = max(vals[IU.EPS][1] - b0, 0.0) / IU.EPS
        for vi, col, struct in at[g]:
            key = tuple(sorted(p[0] for p in vertices[vi][0]))
            if g in reach[n]:
                named.add(key)
            ccol, csign = IU._canon_colour(col)
            for pt, val, size in at_points(struct, len(vertices[vi][0])):
                tot[key][(ccol, pt)] += r * val * csign
                bnd[key][(ccol, pt)] += sc * size
    live = sorted(k for k in named if any(b > 0 and abs(tot[k][c]) > IU.TOL * b for c, b in bnd[k].items()))
    out.update(live=bool(live), live_vertices=[" ".join(k) for k in live][:8])
    # pattern: the response with only the parameter's own complex combination recomputed, per vertex type
    T, Tb, species, bars = tensor(op, s, Y)
    resp = collections.defaultdict(complex)     # (type, colour, kinematic point, generations) -> response
    rbnd = collections.defaultdict(float)       # and the triangle-inequality bound on it
    seen = set()                                # the vertices (sorted PDG codes) in which the parameter appears
    for g in reach[n]:
        code = compiled(g)
        plus, minus = evaluate(ns, nsb, code, n, 1.0, mine), evaluate(ns, nsb, code, n, -1.0, mine)
        r = (plus[0] - minus[0]) / 2
        rb = max(plus[1] - eval(code[1], nsb), 0.0)
        for vi, col, struct in at[g]:
            plist = vertices[vi][0]
            typ = tuple(("f", FERMION[abs(c)][0], c < 0) if abs(c) in FERMION else ("b", nm, c) for nm, c in plist)
            gens = tuple(FERMION[abs(c)][1] for _, c in plist if abs(c) in FERMION)
            ccol, csign = IU._canon_colour(col)
            for pt, val, size in at_points(struct, len(plist)):
                resp[(typ, ccol, pt, gens)] += r * val * csign
                rbnd[(typ, ccol, pt, gens)] += rb * size
            seen.add(tuple(sorted(c for _, c in plist)))
    # a response below 1e-10 of its bound is the round-off of terms that cancel, through a parameter relation
    # or a unitary CKM matrix
    classes = collections.defaultdict(dict)
    for key, r in resp.items():
        classes[key[:3]][key[3]] = r if abs(r) > 1e-10 * rbnd[key] else 0j
    report = []
    for (typ, ccol, pt), pts in classes.items():
        fpos = [k for k, x in enumerate(typ) if x[0] == "f"]
        fam = [typ[k][1] for k in fpos]
        anti = [typ[k][2] for k in fpos]
        name = " ".join(x[1] + ("~" if x[2] else "") if x[0] == "f" else x[1] for x in typ)
        kind = "vertex" if isinstance(pt, int) else "form " + str(pt[1])[:60]
        if len(fpos) != len(species):
            report.append(dict(type=name, colour=ccol, kind=kind, ok=False, constrained=True,
                               why="the number of fermions is not the operator's"))
            continue
        # the ways the fermions fill the slots: each family held by the slot's species, and the antiparticles
        # in the barred slots (the term) or in the unbarred ones (its conjugate); V on every doublet slot that a
        # down-type quark fills
        ways = []
        for perm in itertools.permutations(range(len(species))):
            if not all(f in HOLDS[species[perm[j]]] for j, f in enumerate(fam)):
                continue
            if not (all(anti[j] == bars[perm[j]] for j in range(len(fam))) or
                    all(anti[j] != bars[perm[j]] for j in range(len(fam)))):
                continue
            Tm, Tmb = T, Tb
            for j, f in enumerate(fam):
                if species[perm[j]] == "q" and f == "d":
                    Tm = np.moveaxis(np.tensordot(V, Tm, axes=([0], [perm[j]])), 0, perm[j])
                    Tmb = np.moveaxis(np.tensordot(np.abs(V), Tmb, axes=([0], [perm[j]])), 0, perm[j])
            # an entry below 1e-10 of its bound is the round-off of a sum that vanishes, as V^T V does
            ways.append((perm, np.where(np.abs(Tm) > 1e-10 * Tmb, Tm, 0)))
        # every generation assignment: the response, or zero where the parameter has no coupling in that vertex
        # at all; skipped where it has couplings there in other structures or another order of the fields only
        G, R = [], []
        for gens in itertools.product(range(3), repeat=len(fpos)):
            if gens in pts:
                G.append(gens)
                R.append(pts[gens])
                continue
            it = iter(gens)
            codes = tuple(sorted(code_of(x, next(it) if x[0] == "f" else None) for x in typ))
            if codes not in seen:
                G.append(gens)
                R.append(0j)
        A = np.array([[Tm[tuple(gens[perm.index(sl)] for sl in range(len(species)))] for perm, Tm in ways] for gens in G],
                     dtype=complex).reshape(len(G), len(ways))
        R = np.array(R, dtype=complex)
        big = np.maximum(np.abs(R), np.abs(A).max(axis=1) if ways else 0.0)
        use = big > 0
        if not use.any():
            continue
        A, R, G = A[use], R[use], [g for g, u in zip(G, use) if u]
        W = 1 / big[use]
        k = np.linalg.lstsq(A * W[:, None], R * W, rcond=None)[0] if ways else np.zeros(0, dtype=complex)
        fit = A @ k
        # the residual of each point in the weighted system, against the size a term of the fit has there: its
        # response, or a tensor that is not zero times the largest constant (the constants of the ways that do
        # not contribute come out of the fit at round-off, 1e-15 of the others)
        res = np.abs(R - fit) * W
        scale = np.maximum(np.abs(R) * W, (np.abs(A) * W[:, None]).max(axis=1) * (np.abs(k).max() if ways else 0.0))
        bad = res > FIT_TOL * scale
        rank = int(np.linalg.matrix_rank(A * W[:, None], tol=1e-10)) if ways else 0
        if detail and bad.any():
            np.set_printoptions(linewidth=200, precision=6)
            print(f"--- {n} {name} {ccol} {'point ' + str(pt) if isinstance(pt, int) else pt[1][:1]}\n"
                  f"  slots: species {species}, barred {bars}")
            if T.ndim == 2:
                print(T.real)
            print(f"  ways {[w[0] for w in ways]}, k {k}")
            for j, gg in enumerate(G):
                print(f"  {gg}: response {R[j]:.6e}  fit {fit[j]:.6e}  tensors {A[j]}")
        report.append(dict(type=name, colour=ccol, kind=kind, points=len(G), ways=len(ways), rank=rank,
                           constrained=rank < len(G), ok=not bad.any(),
                           worst=float(np.max(np.where(scale > 0, res / np.where(scale > 0, scale, 1), 0.0))),
                           bad=[list(G[j]) for j in np.where(bad)[0][:5]]))
    # a vertex type is its fields and colour structure, tested at each kinematic point (or in one canonical
    # form, where the structure is not evaluated): it passes when every point does
    merged = {}
    for r in report:
        k = (r["type"], r["colour"], r["kind"])
        if k not in merged:
            merged[k] = dict(r)
        else:
            m = merged[k]
            m.update(ok=m["ok"] and r["ok"], constrained=m["constrained"] or r["constrained"],
                     worst=max(m.get("worst", 0.0), r.get("worst", 0.0)), bad=m.get("bad", []) or r.get("bad", []))
    report = list(merged.values())
    out.update(types=len(report), constrained=sum(r["constrained"] for r in report),
               pattern_ok=all(r["ok"] for r in report), failures=[r for r in report if not r["ok"]][:5])
    return out


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
