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
a member has a vertex its operator lacks.

Every coupling is evaluated with the scale of its rounding error, operation by operation, by the Evaluator of
validate/geo_export_check.py, and so is each vertex, the sum of its couplings.  A vertex is there when its
value exceeds the rounding of its terms (LIMIT of that file), and two vertices that differ by no more than
their rounding do not differ.  This matters where the terms of a vertex cancel exactly.  At the vacuum
Q_{W^2H^4}^{(1)} and Q_{B^2H^4}^{(1)}, and their towers, only rescale the kinetic term of W or B, which the
inputs M_W, M_Z and G_F absorb into the gauge couplings, so every vertex without a Higgs boson is that of the
Standard Model: the vertex of the operator cancels against its shift of the Standard-Model vertex, to the
rounding of the two (about 1e-17 of each).  Measured against the largest of the pair's own vertices, two such
residues differ by their own size, so without the rounding these members fail with nothing to compare.

The two towers that have no operator of dimension eight, those of Q_{WH^6D^2}^{(5),(6)} of the connection k
(coefficients c<d>WH4D2x5, x6), are tested in two other ways.  A member of dimension 12 or more is compared, as
above, with the member of dimension ten, at (v^2/2)^k L_d/L_10.  The member of dimension ten is compared with
the operator of dimension eight with the same field strength: at the vacuum (H^dag tau^I H) is -(v^2/2) delta^I3,
so Q^{(5)} is (v^2/2)^2 i (D H^dag tau^3 D H) W^3 and Q_{WH^4D^2}^{(1)} = i (H^dag H)(D H^dag tau^I D H) W^I is
(v^2/2) times the same plus the terms with I = 1, 2.  Those mix the upper and the lower component of the doublet
(in the unitary gauge of the models), so their three-point vertices hold a W boson in D H^dag tau^I D H and
another in the abelian part of W^I: they are W+ W- Z and W+ W- H alone.  On the vertices W+ W- a, H Z a and
H Z Z the term linear in c10WH4D2x5 is therefore (v^2/2) L10/L8 times that linear in c8WH4D2x1, and the same
holds for x6 against x2 with the dual field strength.  The Higgs boson of H Z a and H Z Z comes from the
derivative in D H, never from the factors (v + h)^2/2, since the antisymmetric part of (D H^dag tau^3 D H)
without it would need two Z bosons.  Neither operator enters the two-point functions, so the inputs and the
rotation of the fields do not see them.  Their vertices W+ W- Z and W+ W- H have no such partner, and this
test leaves them to validate/geo_export_check.py.

The four-lepton operator that is new at dimension ten, (H^dag tau^I H)(H^dag tau^J H)(lbar g tau^I l)(lbar g tau^J l)
(coefficients c<d>l4H2x3Fx00 and Fx0E, block GEOGF), has no operator of dimension eight either.  It has no
vertex of at most three legs: it enters these vertices through the relation of G_F alone, as Q_{l^4H^2}^{(1)}
does, and at equal dimension with the opposite sign (gen/derive_geo.py: the contact term of muon decay is
-c8 L8 v^4/2 for the one and +c10 L10 v^2 (v^2/2)^2 for the other).  So on every vertex the term linear in
c10l4H2x3Fx00 is -(v^2/2) L10/L8 times the term linear in c8l4H2x1Fx00, and the same holds for Fx0E.  Its
members of dimension 12 and more are compared with the member of dimension ten, as above.  In a UFO written
without the vertices of the base (a shard) neither of the two has a vertex, and there is nothing to compare.

A model with no member of a tower has nothing to compare, and the command says so and exits 2.
"""
import argparse
import ast
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
from geo_export_check import LIMIT, Evaluator, parse  # noqa: E402

# the towers without an operator of dimension eight, by the label of their coefficient: the operator of dimension
# eight their member of dimension ten is compared with, the factor beside (v^2/2) L10/L8, and the vertices it is
# compared on, None for every vertex without a Higgs boson (docstring)
SIBLING_VERTICES = {("W+", "W-", "a"), ("H", "Z", "a"), ("H", "Z", "Z")}
SIBLINGS = {"WH4D2x5": ("WH4D2x1", 1, SIBLING_VERTICES), "WH4D2x6": ("WH4D2x2", 1, SIBLING_VERTICES),
            "l4H2x3Fx00": ("l4H2x1Fx00", -1, None), "l4H2x3Fx0E": ("l4H2x1Fx0E", -1, None)}


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
        ev = Evaluator(ns)
        ext = {}
        for p in P.all_parameters:
            if p.nature == "external":
                c = p.name.startswith("c") and p.name != "cabi"
                ext[p.name] = 0.0 if c else generic_value(p.name, float(p.value))
        internal = [(p.name, parse(p.value)) for p in P.all_parameters if p.nature == "internal"]
        wcs = {k for k in ext if k.startswith("c") and k != "cabi"}
        members = sorted(k for k in wcs if re.match(r"c(1[0-9]|[2-9][0-9])[A-Za-z]", k))
        dim = lambda k: int(re.match(r"c(\d+)", k).group(1))
        label = lambda k: re.match(r"c\d+(.*)", k).group(1)
        # each member against its operator of dimension eight, or, without one, the member of dimension ten
        parent = {}
        for k in members:
            for d0 in range(8, dim(k), 2):
                if f"c{d0}{label(k)}" in wcs:
                    parent[k] = f"c{d0}{label(k)}"
                    break
        orphans = [k for k in members if k not in parent]
        pairs = [k for k in members if k in parent]
        if not members:
            print("no member of a tower in this model (a model of order 2 has none): nothing to compare")
            return 2

        # the vertices with at most three legs and no Higgs boson, each with its structures evaluated once
        code = {}
        comp = lambda s: code.setdefault(s, compile(s, "<structure>", "eval"))
        rows = []
        for v in V.all_vertices:
            names = [p.name for p in v.particles]
            if len(names) > 3 or ("H" in names and tuple(sorted(names)) not in SIBLING_VERTICES):
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
            terms = [(ci, li, c.order.get("NP", 0), parse(c.value))
                     for (ci, li), cs in v.couplings.items() for c in (cs if isinstance(cs, list) else [cs])]
            rows.append((tuple(sorted(names)), vals, terms))
        print(f"{sum(1 for r in rows if 'H' not in r[0])} vertices with at most three legs and no Higgs boson; "
              f"{sum(1 for k in pairs if dim(parent[k]) == 8)} members with an operator of dimension eight, "
              f"{sum(1 for k in pairs if dim(parent[k]) > 8)} compared with the member of dimension ten, "
              f"{len(orphans)} with neither: {orphans}")

        # the coefficients each internal parameter and each coupling reads, directly or through the internal
        # parameters, and the value of each with every coefficient at zero.  What does not read wc has that value
        # and that rounding scale when wc is at 1 (the Evaluator is a function of what it reads), so at() evaluates
        # again only what reads wc and gives what evaluating everything gives
        uses, sets = {}, {}

        def coefficients(node):
            r = {n.id for n in ast.walk(node) if type(n) is ast.Name}
            s = frozenset((r & wcs).union(*(uses[x] for x in r if x in uses)))
            return sets.setdefault(s, s)   # one copy of each set, which many couplings share

        zero, zerr = dict(ext), {}
        for name, node in internal:
            uses[name] = coefficients(node)
            zero[name], zerr[name] = ev(node, zero, zerr)
        for i, (key, pts, terms) in enumerate(rows):
            rows[i] = (key, pts, [(ci, li, npo, node, coefficients(node), ev(node, zero, zerr))
                                  for ci, li, npo, node in terms])

        def at(wc, np_order, with_h=False):
            """{vertex: [value at each point]} from the couplings of NP order np_order with wc alone at 1, the scale
            of the rounding of each value (Evaluator), and the parameters."""
            vals, errs = dict(zero, **{wc: 1.0}), dict(zerr)
            for name, node in internal:
                if wc in uses[name]:
                    vals[name], errs[name] = ev(node, vals, errs)
            out = collections.defaultdict(lambda: [0j, 0j])
            err = collections.defaultdict(lambda: [0.0, 0.0])
            for key, pts, terms in rows:
                if "H" in key and not with_h:
                    continue
                for ci, li, npo, node, used, at_zero in terms:
                    if npo != np_order:
                        continue
                    g, eg = ev(node, vals, errs) if wc in used else at_zero
                    g = complex(g)
                    if g == 0 and eg == 0:
                        continue
                    for pt, (lor, col) in enumerate(pts):
                        cl = col[ci]*lor[li]
                        out[key][pt] += g*cl
                        # the product with the structures and the sum, each rounded, as the Evaluator counts them
                        err[key][pt] += eg*abs(cl) + 2*abs(g*cl) + abs(out[key][pt])
            return out, err, vals

        def compare(k, p, keys=None, factor=1):
            """The largest difference of the vertices of k from factor (v^2/2)^j L_d/L_d0 times those of p, as a
            fraction of the largest vertex of the pair, and the vertices either has, or None when neither has a
            vertex above the rounding of its terms.  A difference within the rounding of the two is none."""
            d, d0 = dim(k), dim(p)
            if (p, keys is not None) not in cache:
                cache[(p, keys is not None)] = at(p, (d0 - 4)//2, keys is not None)
            (A0, E0, _), (Ad, Ed, valsd) = cache[(p, keys is not None)], at(k, (d - 4)//2, keys is not None)
            if keys is not None:
                A0, E0 = {q: A0[q] for q in A0 if q in keys}, {q: E0[q] for q in E0 if q in keys}
                Ad, Ed = {q: Ad[q] for q in Ad if q in keys}, {q: Ed[q] for q in Ed if q in keys}
            s = factor*(valsd["vevSM"]**2/2)**((d - d0)//2)*valsd[f"L{d}"]/valsd[f"L{d0}"]
            there = lambda A, E, q: any(abs(z) > LIMIT*e for z, e in zip(A[q], E[q]))
            seen = {q for q in A0 if there(A0, E0, q)} | {q for q in Ad if there(Ad, Ed, q)}
            if not seen:
                return None, set()
            # the size of the pair in the units of the member: its own vertices and the scaled ones of its operator
            size = max(max(abs(z) for z in Ad.get(q, [0j])) for q in seen)
            size = max(size, max(abs(s)*max(abs(z) for z in A0.get(q, [0j])) for q in seen))
            worst = 0.0
            for key in set(A0) | set(Ad):
                x, ex = A0.get(key, [0j, 0j]), E0.get(key, [0.0, 0.0])
                y, ey = Ad.get(key, [0j, 0j]), Ed.get(key, [0.0, 0.0])
                for p_, ep, q, eq in zip(x, ex, y, ey):
                    if abs(q - s*p_) > LIMIT*(eq + abs(s)*ep):
                        worst = max(worst, abs(q - s*p_)/size)
            return worst, seen

        bad, live, dead = [], 0, []
        cache = {}
        for k in pairs:
            worst, _ = compare(k, parent[k])
            if worst is None:
                dead.append(k)
                continue
            live += 1
            if worst > args.tol:
                bad.append((worst, k, parent[k], "every vertex without a Higgs boson"))
        print(f"{live} members with vertices of this kind, {len(dead)} with none (as their operators): {dead}")
        # the members of dimension ten without an operator of dimension eight, against their siblings
        sib = 0
        for k in orphans:
            other, factor, keys = SIBLINGS.get(label(k), (None, 1, None))
            p = f"c8{other}" if other else None
            if dim(k) != 10 or p not in wcs:
                bad.append((math.inf, k, p, "no operator to compare it with"))
                continue
            worst, seen = compare(k, p, keys, factor)
            where = "every vertex without a Higgs boson" if keys is None else "W+ W- a, H Z a and H Z Z"
            if keys is not None and (worst is None or not seen >= keys):
                # an operator with vertices of its own: each of those it shares with its partner must be there
                bad.append((math.inf, k, p, f"vertices {sorted(seen)} of {sorted(keys)} present"))
                continue
            sib += 1
            if worst is None:
                # one that enters through the input relations alone, in a model without the vertices of the base
                print(f"  {k} against {p}: neither has a vertex with at most three legs and no Higgs boson")
                continue
            print(f"  {k} against {p} on {where if keys is None else sorted(keys)} at {'-' if factor < 0 else ''}(v^2/2) L10/L8: "
                  f"largest difference {worst:.2e}")
            if worst > args.tol:
                bad.append((worst, k, p, where))
        for w, k, p, where in sorted(bad, key=lambda b: -b[0])[:20]:
            print(f"  {k} against {p}: {where}" if w == math.inf else
                  f"  {k} against {p} ({where}): largest difference {w:.2e} of the largest vertex")
        ok = not bad and live > 0 and sib == len(orphans)
        print("tower check: PASS" if ok else
              f"tower check: FAIL: {len(bad)} members differ from their operators or have none to compare with")
        return 0 if ok else 1
    finally:
        leave_ufo(ufo)


if __name__ == "__main__":
    sys.exit(main())
