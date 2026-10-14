#!/usr/bin/env python3
"""The number of legs a vertex of each class can have, against the vertices of the released model.

    python3 validate/check_legs.py [models/dim8_is]

A vertex of a class with field content (N_D, N_H, N_psi, N_X) has

    max(N_psi + N_X + N_HD, 2) <= n <= N_psi + N_H + 2 N_X + N_D

legs, N_HD being the number of Higgs fields that carry a derivative, smallest over the terms of
the class.  The two-point terms shift masses and field normalisations, which the input relations
absorb, so the vertices of the released model start at three legs.  The test recomputes N_HD from
gen/operators.py, checks it against epower.DIM8_HD, and checks that the smallest and largest
vertex of every class in the model sit exactly on the two bounds.
"""
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import epower  # noqa: E402
from operators import OPS  # noqa: E402


def higgs_with_derivative():
    """{class number: N_HD}, smallest over the terms of the class."""
    hd = collections.defaultdict(lambda: 99)
    for op in OPS:
        for t in op.terms:
            k = sum(1 for f in t.factors if type(f).__name__ == "H" and f.derivs)
            hd[op.cls] = min(hd[op.cls], k)
    return hd


def vertex_legs(model):
    """{class number: Counter of leg counts} over the vertices whose couplings carry a coefficient
    of the class directly, which leaves out the input relations."""
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
        for g in set(re.findall(r"C\.(GC_\w+)", m.group(2))):
            for c in classes.get(g, ()):
                legs[c][n] += 1
    return legs


def main(argv):
    model = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(ROOT, "models", "dim8_is")
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
    print(f"\n{len(names) - bad}/{len(names)} classes sit exactly on the bounds")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
