#!/usr/bin/env python3
"""The members of the towers against their operators of dimension eight, on every vertex without a Higgs boson.

    validate/geo_tower_check.py <UFO dir> [--tol 1e-8]

At the vacuum a member (H^dag H)^k Q of a tower (gen/towers.py) is (v^2/2)^k times Q.  On a vertex with at
most three legs and no Higgs boson, the term linear in the member's coefficient c_d at its own NP order
(d - 4)/2 is therefore (v^2/2)^k L_d/L_8 times the term linear in the coefficient c_8 of Q at NP order 2,
with v = vevSM.  This holds for the vertex of the operator itself and for the shifts its connection makes
in the vertices of the Standard Model, through the inputs, the rotation of the neutral fields, the
rescalings of W and of the gluon and the coupling g_s (gen/derive_geo.py), since at leading order each of
them is linear in the values of the connections at the vacuum.  (A vertex with a Higgs boson sees their
derivatives as well, which scale otherwise.)

Each pair is evaluated as validate/compare_ufo.py evaluates a vertex, with random wavefunctions and
momenta, once with c_d alone at 1 and once with c_8 alone at 1, every other coefficient at 0.  The test
fails if a vertex differs from the scaled one by more than tol of the largest of the pair's vertices, or if
a member has a vertex its operator lacks.  The operators of the towers that have no operator of dimension
eight (Q_{WH^6D^2}^{(5),(6)} of the connection k, coefficients c<d>WH4D2x5, x6) are listed apart.
"""
import argparse
import cmath
import collections
import math
import os
import random
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_ufo import Point, leave_ufo, scalar, use_ufo  # noqa: E402
from generic_inputs import generic_value  # noqa: E402


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("ufo")
    a.add_argument("--tol", type=float, default=1e-8)
    args = a.parse_args(argv)
    ufo = os.path.abspath(args.ufo)
    use_ufo(ufo)
    try:
        import function_library as F
        import parameters as P
        import vertices as V
        ns = {"cmath": cmath, "math": math, "complex": complex}
        ns.update({k: v for k, v in vars(F).items() if callable(v)})
        ext = {}
        for p in P.all_parameters:
            if p.nature == "external":
                c = p.name.startswith("c") and p.name != "cabi"
                ext[p.name] = 0.0 if c else generic_value(p.name, float(p.value))
        internal = [(p.name, compile(p.value, p.name, "eval")) for p in P.all_parameters if p.nature == "internal"]
        wcs = {k for k in ext if k.startswith("c") and k != "cabi"}
        members = sorted(k for k in wcs if re.match(r"c(1[0-9]|[2-9][0-9])[A-Za-z]", k))
        parent = {k: "c8" + re.match(r"c\d+(.*)", k).group(1) for k in members}
        orphans = [k for k in members if parent[k] not in wcs]
        pairs = [k for k in members if parent[k] in wcs]

        # the vertices with at most three legs and no Higgs boson, each with its structures evaluated once
        code = {}
        comp = lambda s: code.setdefault(s, compile(s, "<structure>", "eval"))
        rows = []
        for v in V.all_vertices:
            names = [p.name for p in v.particles]
            if len(names) > 3 or "H" in names:
                continue
            order = sorted(range(len(names)), key=lambda k: (names[k], k))
            pos = {order[j] + 1: j for j in range(len(order))}
            vals = []
            for pt in range(2):
                rng = random.Random(f"1:{pt}:{'/'.join(sorted(names))}")
                point = Point([v.particles[k].color for k in order], pos, rng)
                lns, cns = point.lorentz_ns(), point.colour_ns()
                vals.append(([scalar(eval(comp(l.structure), lns)) for l in v.lorentz],
                             [scalar(eval(comp(c), cns)) for c in v.color]))
            terms = [(ci, li, c.order.get("NP", 0), compile(c.value, c.name, "eval"))
                     for (ci, li), cs in v.couplings.items() for c in (cs if isinstance(cs, list) else [cs])]
            rows.append((tuple(sorted(names)), vals, terms))
        print(f"{len(rows)} vertices with at most three legs and no Higgs boson; {len(pairs)} members with an "
              f"operator of dimension eight, {len(orphans)} without: {orphans}")

        def at(wc, np_order):
            vals = dict(ext, **{wc: 1.0})
            for name, c in internal:
                vals[name] = eval(c, ns, vals)
            out = collections.defaultdict(lambda: [0j, 0j])
            for key, pts, terms in rows:
                for ci, li, npo, c in terms:
                    if npo != np_order:
                        continue
                    g = complex(eval(c, ns, vals))
                    if g == 0:
                        continue
                    for pt, (lor, col) in enumerate(pts):
                        out[key][pt] += g*col[ci]*lor[li]
            return out, vals

        bad, live, dead = [], 0, []
        cache8 = {}
        for k in pairs:
            d = int(re.match(r"c(\d+)", k).group(1))
            if parent[k] not in cache8:
                cache8[parent[k]] = at(parent[k], 2)
            (A8, vals8), (Ad, valsd) = cache8[parent[k]], at(k, (d - 4)//2)
            s = (valsd["vevSM"]**2/2)**((d - 8)//2)*valsd[f"L{d}"]/valsd["L8"]
            size = max([abs(z) for x in list(A8.values()) + list(Ad.values()) for z in x] + [0.0])
            if size == 0:
                dead.append(k)
                continue
            live += 1
            worst = 0.0
            for key in set(A8) | set(Ad):
                x, y = A8.get(key, [0j, 0j]), Ad.get(key, [0j, 0j])
                worst = max(worst, max(abs(q - s*p) for p, q in zip(x, y))/(abs(s)*size))
            if worst > args.tol:
                bad.append((worst, k))
        print(f"{live} members with vertices of this kind, {len(dead)} with none (as their operators): {dead}")
        for w, k in sorted(bad, reverse=True)[:20]:
            print(f"  {k} against {parent[k]}: largest difference {w:.2e} of the largest vertex")
        ok = not bad and live > 0
        print("PASS" if ok else f"FAIL: {len(bad)} members differ from their operators")
        return 0 if ok else 1
    finally:
        leave_ufo(ufo)


if __name__ == "__main__":
    sys.exit(main())
