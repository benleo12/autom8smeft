#!/usr/bin/env python3
"""The W coupling of the electron in a model of order N against its closed form.

    validate/geo_vertex_check.py <UFO dir> N

In a model of order N (gen/towers.py) the coefficient of nubar_e gamma^mu P_L e W_mu in the Lagrangian is
complete to O(t^N), t = 1/Lambda^2.  At the vacuum it is the Standard Model's g/Sqrt2 times
    (1 + gw1 + ... + gwN) (1 + rW1 + ... + rWN) (1 + dl + i a),
    dl = cHl3 vT^2 L6 + (T[l2H4Dx2] + T[l2H4Dx4]) vT^4/2,   a = -T[l2H4Dx3] vT^4/2,
    T[X] = sum over d = 8, 10, ... of c{d}X L{d} (vT^2/2)^((d-8)/2),   vT = vevSM (1 + vev1 + ... + vevN),
the shifted coupling, the rescaled W, and the W-lepton connection L_{I,A} of class 13 with its towers, as
gen/derive_geo.py writes them for G_F (the electron Yukawa at zero, the default).  The sign of a follows from
Q_{l^2H^4D}^{(3)} = eps^{IJK} (lbar gamma^mu tau^I l)(H^dag tau^K H)(H^dag i D<->^J_mu H) at H = (0, vT/Sqrt2).
The UFO vertex of an outgoing W+, nubar_e and e- comes from the conjugate term ebar gamma^mu P_L nu W_mu^dag,
so it carries the complex conjugate, 1 + dl - i a: the check sees the sign of the CP-odd part, which G_F,
depending on the modulus alone, does not.  The model's coupling is the
sum over the NP orders through N of the couplings of the left-handed structure of the vertex, which FeynRules
computed from the operators and the base.  Every coefficient of NP order p is set to c t^p, and the difference
from the closed form must fall as t^(N+1).  It tests the expansion and the truncation of the vertex, the
normalisation of the tower members and the normalisation and sign of the CP-odd Q_{l^2H^4D}^{(3)}.
"""
import cmath
import math
import os
import random
import re
import sys


def main(argv):
    if len(argv) != 3:
        print(__doc__)
        return 2
    ufo, N = os.path.abspath(argv[1]), int(argv[2])
    # the model as the writer leaves it imports too, as in validate/compare_ufo.py
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from compare_ufo import use_ufo
    use_ufo(ufo)
    import parameters as P
    import vertices as V
    ext = {p.name: float(p.value) for p in P.all_parameters if p.nature == "external"}
    ns = {"cmath": cmath, "math": math, "complex": complex,
          "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z}
    order = lambda name: (lambda m: (int(m.group(1)) - 4)//2 if m else 1)(re.match(r"c(\d+)", name))
    rng = random.Random(20261108)
    # every Wilson coefficient: the dimension-six ones (SMEFTsim names, NP order 1) and c<d>... of order (d-4)/2
    coefs = {k: rng.uniform(-1, 1)*3**order(k) for k in ext
             if re.match(r"c\d+", k) or k in ("cHW", "cHB", "cHWB", "cHDD", "cHl3", "cll1", "cHbox", "cH", "cHG")}

    def point(t):
        vals = dict(ext, Lam=1000.0, Lam6=1000.0, **{k: v*t**order(k) for k, v in coefs.items()})
        for p in P.all_parameters:
            if p.nature == "internal":
                vals[p.name] = eval(p.value, ns, vals)
        return vals

    # a merged model has a vertex of these particles for each set of coupling orders (validate/merge_ufo.py)
    vtx = [v for v in V.all_vertices if sorted(p.name for p in v.particles) == sorted(["ve~", "e-", "W+"])]
    assert vtx, "no W+ nubar_e e- vertex"
    left = lambda l: "ProjM" in l.structure and "ProjP" not in l.structure
    assert any(left(l) for v in vtx for l in v.lorentz), [l.structure for v in vtx for l in v.lorentz]

    def model(vals, upto):
        tot = 0
        for v in vtx:
            for (i, j), c in v.couplings.items():
                if not left(v.lorentz[j]):
                    continue
                for cc in (c if isinstance(c, list) else [c]):
                    if cc.order.get("NP", 0) <= upto:
                        tot += eval(cc.value, ns, vals)
        return tot

    def closed(vals):
        S = lambda k: sum(vals[f"{k}{j}"] for j in range(1, N + 1))
        vT = vals["vevSM"]*(1 + S("vev"))
        T = lambda X: sum(vals.get(f"c{d}{X}", 0)*vals[f"L{d}"]*(vT**2/2)**((d - 8)//2) for d in range(8, 2*N + 5, 2))
        dl = vals["cHl3"]*vT**2*vals["L6"] + (T("l2H4Dx2") + T("l2H4Dx4"))*vT**4/2
        a = -T("l2H4Dx3")*vT**4/2
        # the conjugate of the coefficient of nubar_e gamma^mu P_L e W_mu, for the vertex of W+, nubar_e and e-
        return (1 + S("gw"))*(1 + S("rW"))*(1 + dl - 1j*a)

    ts = [0.5, 0.25, 0.125, 0.0625]
    res = []
    for t in ts:
        vals = point(t)
        sm = model(vals, 0)
        res.append(abs(model(vals, N)/sm - closed(vals)))
        print(f"t = {t:<7} model/SM = {model(vals, N)/sm:.12g}   closed form = {closed(vals):.12g}   difference {res[-1]:.3e}")
    ratios = [res[i]/res[i + 1] for i in range(len(res) - 1)]
    print("ratios", " ".join(f"{r:.3g}" for r in ratios), f" (t^{N + 1} gives {2**(N + 1)})")
    ok = ratios[-1] > 0.75*2**(N + 1) or res[-1] < 1e-13
    print("PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
