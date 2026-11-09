#!/usr/bin/env python3
"""The vertices each class can have, against the vertices of the released model.

    python3 validate/check_legs.py [models/dim8_mw]

A vertex of a class with field content (N_D, N_H, N_psi, N_X) has

    max(N_psi + N_X + N_HD, 3) <= n <= N_psi + N_H + 2 N_X + N_D

legs (eq:legs of the paper), N_HD being the number of Higgs fields that carry a derivative,
smallest over the terms of the class, since a covariant derivative of the vacuum is a gauge boson.
The terms with fewer than three legs are not vertices: the two-point terms shift masses and field
normalisations, which the input relations absorb.  The test recomputes N_HD from gen/operators.py,
checks it against epower.DIM8_HD, and checks that the smallest and the largest vertex of every class
sit on the two bounds.

It then checks the subleading vertices.  At n legs a vertex has p Higgs fields at the vacuum,
p = N_H minus its Higgs legs, and gen/epower.py allows p = p_min + k with
k = 0 .. min(k_max - p_min, q_max), k_max being the largest p that leaves n legs.  Leg counting
allows these p and no others, but it does not promise each of them a vertex: some vanish for every
operator of a class, by C (no vertex of Higgs bosons and a single Z from a C-even bosonic operator,
the hhZ of H^6D^2), by the antisymmetry of a field strength (X_{mu nu} d^mu h d^nu h = 0, at p_min in
XH^4D^2), or because a Higgs current H^dag D_mu H has no term with the neutral h alone, so that in
this unitary-gauge model the vertex at p_min of psi^2H^4D is carried by a longitudinal W or Z.  So
for every class and every n the test requires the p of the model to lie in the allowed set and the
largest allowed p, k_max, to be present.  A wider range, k <= min(k_max, q_max), puts its largest p
above k_max where it differs, so it fails this test in every cell where the two ranges differ, and
the test prints how many entries of that range the model lacks.  In a model with the dimension-six sector (dim68_is, dim68_mw) the
eight dimension-six classes are checked the same way.
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import basis  # noqa: E402
import epower  # noqa: E402
from operators import OPS  # noqa: E402


def higgs_with_derivative():
    """{class number: N_HD}, smallest over the terms of the class, in the basis of DIM8_BASIS (gen/basis.py)."""
    hd = collections.defaultdict(lambda: 99)
    for op in basis.ops(OPS):
        for t in op.terms:
            k = sum(1 for f in t.factors if type(f).__name__ == "H" and f.derivs)
            hd[op.cls] = min(hd[op.cls], k)
    return hd


def _higgs_legs(particles):
    return sum(1 for x in particles.split(",") if x.strip() == "P.H")


def vertex_legs(model, with_higgs=False):
    """{class number: Counter of leg counts} over the vertices whose couplings carry a coefficient
    of the class directly, which leaves out the input relations.  With with_higgs, the Counter is
    over (legs, Higgs legs)."""
    cls_of = {w: e["cls"] for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
              for w in e["wcs"]}
    couplings = open(os.path.join(model, "couplings.py")).read()
    classes = {}
    for m in re.finditer(r"(GC_\w+) = Coupling\(name = '\w+',\s*value = '([^']*)'", couplings):
        names = set(re.findall(r"\b(c8\w+?)(?:Re|Im)?\b", m.group(2)))
        classes[m.group(1)] = {cls_of[n] for n in names if n in cls_of}
    legs = collections.defaultdict(collections.Counter)
    vertices = open(os.path.join(model, "vertices.py")).read()
    for m in re.finditer(r"Vertex\(name = '\w+',\s*particles = \[([^\]]*)\].*?couplings = \{([^}]*)\}",
                         vertices, re.S):
        n = m.group(1).count("P.")
        key = (n, _higgs_legs(m.group(1))) if with_higgs else n
        for g in set(re.findall(r"C\.(GC_\w+)", m.group(2))):
            for c in classes.get(g, ()):
                legs[c][key] += 1
    return legs


# the dimension-six coefficients of the combined model, by class; Ph and Abs are the phase and
# modulus of a complex coefficient
DIM6 = {"H^6": "cH", "H^4D^2": "cHbox cHDD", "X^2H^2": "cHW cHB cHWB cHG cHGtil cHWtil cHBtil cHWBtil",
        "X^3": "cG cGtil cW cWtil", "psi^2H^3": "ceH cuH cdH",
        "psi^2XH": "ceW ceB cuG cuW cuB cdG cdW cdB",
        "psi^2H^2D": "cHl1 cHl3 cHe cHq1 cHq3 cHu cHd cHud",
        "psi^4": "cll cll1 cqq1 cqq11 cqq3 cqq31 clq1 clq3 cee cuu cuu1 cdd cdd1 ceu ced cud1 cud8 "
                 "cle clu cld cqe cqu1 cqu8 cqd1 cqd8 cledq cquqd1 cquqd8 cquqd11 cquqd81 clequ1 clequ3"}


def dim6_legs(model, with_higgs=False):
    """{class name: Counter of leg counts} for the dimension-six vertices, or {} without them.
    With with_higgs, the Counter is over (legs, Higgs legs)."""
    if "lhablock = 'DIM6'" not in open(os.path.join(model, "parameters.py")).read() \
            or "cHbox" not in open(os.path.join(model, "couplings.py")).read():
        return {}
    cls_of = {w: c for c, ws in DIM6.items() for w in ws.split()}
    classes = {}
    for m in re.finditer(r"(GC_\w+) = Coupling\(name = '\w+',\s*value = '([^']*)'",
                         open(os.path.join(model, "couplings.py")).read()):
        ids = set(re.findall(r"\b(c[A-Za-z0-9]+?)(?:Ph|Abs)?\b", m.group(2)))
        classes[m.group(1)] = {cls_of[i] for i in ids if i in cls_of}
    legs = collections.defaultdict(collections.Counter)
    for m in re.finditer(r"Vertex\(name = '\w+',\s*particles = \[([^\]]*)\].*?couplings = \{([^}]*)\}",
                         open(os.path.join(model, "vertices.py")).read(), re.S):
        n = m.group(1).count("P.")
        key = (n, _higgs_legs(m.group(1))) if with_higgs else n
        for g in set(re.findall(r"C\.(GC_\w+)", m.group(2))):
            for c in classes.get(g, ()):
                legs[c][key] += 1
    return legs


def predicted_p(args, n, HD, old=False):
    """The p of the vertices with n legs, from gen/epower.py, or with the wider range k <= min(k_max, q_max)."""
    D, H, psi, F = args
    t = epower.tower(D, H, psi, F, n, HD=HD)
    if isinstance(t, str):
        return set()
    if not old:
        return {r["p"] for r in t.Results}
    k_max = (H - max(n - psi - 2 * F - D, 0)) if H > 0 else 0
    if t.pMin == k_max:
        k_max = 0
    return {t.pMin + k for k in range(min(k_max, t.qMax) + 1)}


def check_subleading(label, args, HD, seen):
    """One line per class: the realised p at each n against the allowed set.  Returns (ok, the
    number of entries that only the previous range allows and that the model lacks)."""
    H = args[1]
    got = {}
    for (n, nh) in seen:
        got.setdefault(n, set()).add(H - nh)
    lo, hi = max(args[2] + args[3] + HD, 3), args[2] + H + 2 * args[3] + args[0]
    ok, extra, cells = True, 0, []
    for n in range(lo, hi + 1):
        want, have = predicted_p(args, n, HD), got.get(n, set())
        good = have <= want and (not want or max(want) in have)
        ok &= good
        extra += len((predicted_p(args, n, HD, old=True) - want) - have)
        cells.append(f"n={n}:{''.join(map(str, sorted(have)))}" + ("" if have == want else f"(of {''.join(map(str, sorted(want)))})")
                     + ("" if good else "!"))
    ok &= set(got) <= set(range(lo, hi + 1))
    print(f"{'ok  ' if ok else 'FAIL'} {label}  p by legs  " + "  ".join(cells))
    return ok, extra


def main(argv):
    model = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(ROOT, "models", basis.model_name("dim8_mw"))
    names = list(epower.DIM8_CLASSES)
    hd = higgs_with_derivative()
    legs = vertex_legs(model)
    bad = 0
    for c, name in enumerate(names, start=1):
        D, H, psi, F = epower.DIM8_CLASSES[name]
        lo, hi = max(psi + F + hd[c], 3), psi + H + 2 * F + D
        seen = legs.get(c)
        ok = (hd[c] == epower.DIM8_HD[name] and seen is not None
              and min(seen) == lo and max(seen) == hi)
        bad += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {c:2d} {name:12s} N_HD={hd[c]} (table {epower.DIM8_HD[name]})"
              f"  bounds {lo}..{hi}  vertices {min(seen) if seen else '-'}..{max(seen) if seen else '-'}")
    total = len(names)
    for name, seen in sorted(dim6_legs(model).items()):
        D, H, psi, F = epower.DIM6_CLASSES[name]
        lo = max(psi + F + epower.higgs_with_derivative(name), 3)
        hi = psi + H + 2 * F + D
        ok = min(seen) == lo and max(seen) == hi
        bad += not ok
        total += 1
        print(f"{'ok  ' if ok else 'FAIL'}  6 {name:12s}  bounds {lo}..{hi}  vertices {min(seen)}..{max(seen)}")
    print(f"\n{total - bad}/{total} classes sit exactly on the bounds")

    # the subleading vertices
    print()
    hl = vertex_legs(model, with_higgs=True)
    bad2 = extra = 0
    for c, name in enumerate(names, start=1):
        ok, x = check_subleading(f"{c:2d} {name:12s}", epower.DIM8_CLASSES[name], epower.DIM8_HD[name], hl.get(c, {}))
        bad2 += not ok
        extra += x
    total2 = len(names)
    for name, seen in sorted(dim6_legs(model, with_higgs=True).items()):
        ok, x = check_subleading(f" 6 {name:12s}", epower.DIM6_CLASSES[name], epower.higgs_with_derivative(name), seen)
        bad2 += not ok
        extra += x
        total2 += 1
    print(f"\n{total2 - bad2}/{total2} classes have their vertices inside the allowed p and one at k_max for every "
          f"number of legs; the wider range k <= min(k_max, q_max) allows {extra} more entries, none of which "
          f"the model has")
    return 1 if bad or bad2 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
