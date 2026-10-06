"""
gen/derive_input_scheme.py  --  derive the {alpha, MZ, GF} input relations to O(1/Lambda^4).

Method, the one SmeftFR uses in code/smeft_input_scheme.m applied to OUR scheme: write the
EXACT kinetic and mass matrices and the EXACT muon-decay relation with the dimension-six and
dimension-eight corrections in, impose the three inputs, and expand the solution for the
Lagrangian parameters (g, g', v) once at the end.  Every (dim-6)^2 cross term then comes out
of the algebra instead of being guessed.

Bookkeeping: L6 = 1/Lambda_6^2 carries one power of t, L8 = 1/Lambda^4 carries t^2; the
solution is taken to O(t^2).  The base symbols are the Standard Model Lagrangian couplings
g0, gp0, v0 (base.fr's gw, g1, vev with every coefficient zero), so all three input
relations are RATIONAL and the t-coefficients are extracted by differentiation at t = 0.
A first version used sp.series on nested square roots and reached 7 GB without finishing.

Conventions, checked against SMEFTsim's rotateGaugeB and SmeftFR's Z-factors:
  L_kin = -(1/4)[(1-fW)(W1^2+W2^2) + (1-fW3) W3^2 + (1-fB) B^2 + 2 m W3.B]
     fW  = 2 cHW v^2 L6 + c8W2H4x1 v^4 L8         fW3 = fW + c8W2H4x3 v^4 L8
     fB  = 2 cHB v^2 L6 + c8B2H4x1 v^4 L8
     m   = cHWB v^2 L6 + (1/2) c8WBH4x1 v^4 L8   (Q_HWB -> -(v^2/2) W3B, Q_{WBH^4}^(1) -> -(v^4/4) W3B)
  M_W^2 = g^2 v^2/4 (1 + dmW),                    dmW = (c8H6x1 - c8H6x2)/4 v^4 L8
  M_neutral^2 = (v^2/4)(1 + dmZ) n n^T, n = (g,-g'), dmZ = cHDD v^2 L6/2 + (c8H6x1 + c8H6x2)/4 v^4 L8
  sqrt2 GF v^2 = R = (1 + dl)^2/(1 + dmW) + dc,   dl = cHl3 v^2 L6 + d8gWl,  dc = -cll1 v^2 L6,
     d8gWl = (c8l2H4Dx2 + c8l2H4Dx4)/2 v^4 L8.
  (The muon-decay R reproduces SmeftFR's universal-flavour c6 and c8 exactly, including the
   2 cHl3^2 that a naive square misses; under our delta_pr delta_st contraction the dim-8
   four-lepton operators and the non-interfering cle^2 give nothing.)
"""
import math
import os
import sys

import sympy as sp

# Which three measurements are imposed.  "alpha" is {alpha, M_Z, G_F}, the scheme this file was
# written for and the one models/dim68_is uses.  "mw" is {M_W, M_Z, G_F}, where BOTH masses are
# inputs and therefore carry no Wilson-coefficient dependence at all.  That is the whole point of
# having it: MadGraph tags couplings and not masses, so in the alpha scheme the shift of M_W is
# invisible to every order constraint and NP^2==1 is not the complete interference.  With M_W an
# input there is no mass shift to lose, and the orders can be made exact.
SCHEME = (sys.argv[1] if len(sys.argv) > 1 else os.environ.get("DIM8_SCHEME", "alpha")).lower()
assert SCHEME in ("alpha", "mw"), f"scheme must be alpha or mw, not {SCHEME}"

t = sp.symbols('t')
L6, L8 = sp.symbols('L6 L8', positive=True)
cHW, cHB, cHWB, cHDD, cHl3, cll1 = sp.symbols('cHW cHB cHWB cHDD cHl3 cll1', real=True)
c8W2H4x1, c8W2H4x3, c8B2H4x1, c8WBH4x1, c8H6x1, c8H6x2, c8l2H4Dx2, c8l2H4Dx4 = sp.symbols(
    'c8W2H4x1 c8W2H4x3 c8B2H4x1 c8WBH4x1 c8H6x1 c8H6x2 c8l2H4Dx2 c8l2H4Dx4', real=True)
g, gp, v = sp.symbols('g gp v', positive=True)
g0, gp0, v0 = sp.symbols('gwSM g1SM vevSM', positive=True)

e6, e8 = t*L6, t**2*L8
fW  = 2*cHW*v**2*e6 + c8W2H4x1*v**4*e8
fW3 = fW + c8W2H4x3*v**4*e8
fB  = 2*cHB*v**2*e6 + c8B2H4x1*v**4*e8
m   = cHWB*v**2*e6 + sp.Rational(1, 2)*c8WBH4x1*v**4*e8
dmW = (c8H6x1 - c8H6x2)/4*v**4*e8
dmZ = cHDD*v**2*e6/2 + (c8H6x1 + c8H6x2)/4*v**4*e8
dl  = cHl3*v**2*e6 + (c8l2H4Dx2 + c8l2H4Dx4)/2*v**4*e8
dc  = -cll1*v**2*e6

K11, K12, K22 = 1 - fW3, m, 1 - fB
detK = K11*K22 - K12**2
# photon coupling (unit null vector of the canonically normalised neutral mass matrix)
e2  = g**2*gp**2/(gp**2*K11 + 2*g*gp*K12 + g**2*K22)
# Z mass: nonzero eigenvalue, n^T K^-1 n with K^-1 = [[K22,-K12],[-K12,K11]]/detK
MZ2 = (v**2/4)*(1 + dmZ)*(g**2*K22 + 2*g*gp*K12 + gp**2*K11)/detK
MW2 = g**2*v**2/4*(1 + dmW)/(1 - fW)
R   = (1 + dl)**2/(1 + dmW) + dc

# inputs written through the SM couplings, so the zeroth order cancels identically
aEW_of = g0**2*gp0**2/(g0**2 + gp0**2)          # = e0^2
MZ2_of = (g0**2 + gp0**2)*v0**2/4
GFv2   = 1                                      # sqrt2 GF v0^2 = 1  ->  sqrt2 GF = 1/v0^2

a1, a2, b1, b2, c1, c2 = sp.symbols('a1 a2 b1 b2 c1 c2')
sub = {g: g0*(1 + a1*t + a2*t**2), gp: gp0*(1 + b1*t + b2*t**2), v: v0*(1 + c1*t + c2*t**2)}
MW2_of = g0**2*v0**2/4                          # the reference M_W, in the mw scheme an INPUT
first = (e2 - aEW_of) if SCHEME == "alpha" else (MW2 - MW2_of)
eqs = [first.subs(sub), (MZ2 - MZ2_of).subs(sub), (v**2/v0**2 - R).subs(sub)]

def coeff(E, k):
    """k-th Taylor coefficient in t at t = 0, by differentiation (no generic series)."""
    d = E
    for _ in range(k):
        d = sp.diff(d, t)
    return sp.cancel(sp.together(d.subs(t, 0)))/math.factorial(k)

E0 = [sp.simplify(coeff(E, 0)) for E in eqs]
assert all(x == 0 for x in E0), f"zeroth order not zero: {E0}"
E1 = [sp.expand(coeff(E, 1)) for E in eqs]
sol1 = sp.solve(E1, [a1, b1, c1], dict=True)[0]
sol1 = {k: sp.cancel(x) for k, x in sol1.items()}
E2 = [sp.expand(coeff(E, 2).subs(sol1)) for E in eqs]
sol2 = sp.solve(E2, [a2, b2, c2], dict=True)[0]
sol2 = {k: sp.cancel(sp.expand(x)) for k, x in sol2.items()}
sol = {**sol1, **sol2}

rel = {'gw': (a1, a2), 'g1': (b1, b2), 'vev': (c1, c2)}
out = {k: (sol[p[0]], sol[p[1]]) for k, p in rel.items()}
# whichever of the two the scheme does NOT take as an input comes out derived
if SCHEME == "alpha":
    MW2s = MW2.subs(sub).subs(sol)                          # MW^2 = MW0^2 (1 + w1 t + w2 t^2)
    out['MW2'] = (sp.cancel(coeff(MW2s/MW2_of, 1)), sp.cancel(coeff(MW2s/MW2_of, 2)))
else:
    aEWs = e2.subs(sub).subs(sol)                           # aEW = aEW0 (1 + a1 t + a2 t^2)
    out['aEW'] = (sp.cancel(coeff(aEWs/aEW_of, 1)), sp.cancel(coeff(aEWs/aEW_of, 2)))

# ---- numerics for the checks: base.fr inputs -> SM values ---------------------------------
aEWn, MZn, Gfn, MWn = 1/127.9, 91.1876, 1.16637e-5, 79.82435975
v0n = 1/math.sqrt(math.sqrt(2)*Gfn)
if SCHEME == "alpha":
    sw2n = (1 - math.sqrt(1 - 4*math.pi*aEWn/(math.sqrt(2)*Gfn*MZn**2)))/2
    e0n = math.sqrt(4*math.pi*aEWn); MW0n = math.sqrt(1 - sw2n)*MZn
    g0n, gp0n = e0n/math.sqrt(sw2n), e0n/math.sqrt(1 - sw2n)
else:
    # M_W and M_Z are the inputs, so sin^2 theta is exact and alpha is derived.  MWn above is the
    # value the alpha scheme predicts from the same G_F and M_Z, which keeps the two schemes on
    # the same numerical point and makes every comparison between them like for like.
    sw2n = 1 - MWn**2/MZn**2; MW0n = MWn
    g0n = 2*MWn/v0n; gp0n = g0n*math.sqrt(sw2n/(1 - sw2n))
    e0n = g0n*math.sqrt(sw2n); aEWn = e0n**2/(4*math.pi)
cw2n = 1 - sw2n
num = {g0: g0n, gp0: gp0n, v0: v0n}
sth, cth = math.sqrt(sw2n), math.sqrt(cw2n)

print("=== (a) SM limit: the zeroth-order relations vanish identically (asserted) ===")
print("=== (b) dim-6 LINEAR vs SMEFTsim alphaShifts, Lagrangian couplings (L6 = 1) ===")
wc6 = {cHW: 0.7, cHB: -0.4, cHWB: 0.3, cHDD: 0.5, cHl3: 0.2, cll1: -0.6}
vh2 = v0n**2
dMZ2 = vh2*(wc6[cHDD]/2 + 2*cth*sth*wc6[cHWB])
if SCHEME == "alpha":
    dGf  = vh2*(wc6[cHl3]*math.sqrt(2) - wc6[cll1]/math.sqrt(2))
    dg1  = sth**2/2/(1-2*sth**2)*(math.sqrt(2)*dGf + dMZ2 + 2*cth**2*cth/sth*wc6[cHWB]*vh2)
    dgw  = -cth**2/2/(1-2*sth**2)*(math.sqrt(2)*dGf + dMZ2 + 2*sth**2*sth/cth*wc6[cHWB]*vh2)
    dMW  = dGf/math.sqrt(2) + dgw
    # SMEFTsim's Lagrangian couplings: gwsh = ee(1+dgw - cHW v^2)/sth, g1sh = ee(1+dg1 - cHB v^2)/cth
    targets = {'gw': dgw - wc6[cHW]*vh2, 'g1': dg1 - wc6[cHB]*vh2,
               'vev': dGf/math.sqrt(2), 'MW2': 2*dMW}
else:
    # read straight off SMEFTsim_U35_MwScheme_UFO/parameters.py:
    #   dGf  = (2 cHl3 - cll1) vhat^2        dMZ2 = (cHDD/2 + 2 cHWB cth sth) vhat^2
    #   dgw  = -dGf/2                        dg1  = (-dGf - dMZ2/sth^2)/2
    #   vevT = (1 + dGf/2) vhat              gwsh = ee(1+dgw-cHW vhat^2)/sth
    #   aEW  = sqrt2 GF MW^2 (1 - MW^2/MZ^2)/pi, which is an INPUT combination and so unshifted
    #          except through the Lagrangian couplings; the derived shift is what we report
    dGf  = vh2*(2*wc6[cHl3] - wc6[cll1])
    dgw  = -dGf/2
    dg1  = (-dGf - dMZ2/sth**2)/2
    targets = {'gw': dgw - wc6[cHW]*vh2, 'g1': dg1 - wc6[cHB]*vh2, 'vev': dGf/2}
ok_b = True
for k, (x1, _) in out.items():
    if k not in targets:
        print(f"  {k:4s} ours {float(x1.subs({L6: 1, L8: 0}).subs(wc6).subs(num)):+.12f}  (derived, no SMEFTsim target)")
        continue
    ours = float(x1.subs({L6: 1, L8: 0}).subs(wc6).subs(num))
    diff = ours - targets[k]; ok_b &= abs(diff) < 1e-9
    print(f"  {k:4s} ours {ours:+.12f}  SMEFTsim {targets[k]:+.12f}  diff {diff:+.1e}")
print("  (b)", "PASS" if ok_b else "FAIL")

print("=== (c) dim-8 only vs the by-hand derivation, step 2 (L8 = 1) ===")
wc8 = {c8W2H4x1: 0.5, c8W2H4x3: -0.3, c8B2H4x1: 0.4, c8WBH4x1: 0.6, c8H6x1: 0.8, c8H6x2: -0.2,
       c8l2H4Dx2: 0.35, c8l2H4Dx4: 0.15}
v4 = v0n**4
d8gWl = (wc8[c8l2H4Dx2] + wc8[c8l2H4Dx4])/2*v4; d8mW = (wc8[c8H6x1] - wc8[c8H6x2])/4*v4
vev2_ours = 2*float(out['vev'][1].subs({L6: 0, L8: 1}).subs(wc8).subs(num))
print(f"  vev^2: ours {vev2_ours:+.12f}   doc 2 d8gWl - d8mW = {2*d8gWl - d8mW:+.12f}   diff {vev2_ours-(2*d8gWl-d8mW):+.1e}")

print("=== (e) truncation self-test: residuals of the EXACT relations at the O(t^2) solution ===")
allwc = {**wc6, **wc8, L6: 1e-6, L8: 1e-12}
for tt in [1.0, 0.5, 0.25]:
    s_t = {**allwc, **num, t: tt}
    gs  = float((g0*(1 + out['gw'][0]*t + out['gw'][1]*t**2)).subs(s_t))
    gps = float((gp0*(1 + out['g1'][0]*t + out['g1'][1]*t**2)).subs(s_t))
    vs  = float((v0*(1 + out['vev'][0]*t + out['vev'][1]*t**2)).subs(s_t))
    res = [float(E.subs({g: gs, gp: gps, v: vs}).subs(s_t)) for E in (first, MZ2 - MZ2_of, v**2/v0**2 - R)]
    print(f"  t={tt:<4}: {'alpha' if SCHEME == 'alpha' else 'MW2  '} {res[0]:+.2e}   MZ2 {res[1]:+.2e}   GF {res[2]:+.2e}")
print("  (residuals should fall by ~8x per halving of t, i.e. O(t^3))")

print("=== Mathematica forms: X = XSM (1 + X1 + X2), t -> 1 ===")
from sympy.printing.mathematica import mathematica_code as mc
for k, (x1, x2) in out.items():
    print(f"{k}1 = {mc(sp.factor(x1.subs(t, 1)))}")
    print(f"{k}2 = {mc(x2.subs(t, 1))}")
import json, os
# GUARD.  This script derives gw, g1, vev and MW2 (or aEW).  The formulae file it writes ALSO
# holds the canonical field-rotation entries TZZ, TZA, TAZ, TAA, rW and rh, which come from a
# separate step and are NOT regenerated here.  Rerunning this as a regression test on 2026-09-21
# therefore silently deleted twelve of the twenty keys, the base lost its whole rotation block,
# and MadGraph died at output with "Unable to evaluate mdl_rh1__exp__2 = rh1**2".  Merge into
# whatever is already there instead of replacing it.
_dest = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                     "input_scheme_formulae.json" if SCHEME == "alpha" else "input_scheme_formulae_mw.json")
_old = json.load(open(_dest)) if os.path.exists(_dest) else {}
json.dump(_old | {f"{k}1": mc(sp.factor(x1.subs(t, 1))) for k, (x1, _) in out.items()} |
          {f"{k}2": mc(x2.subs(t, 1)) for k, (_, x2) in out.items()},
          open(_dest, "w"), indent=1)
print("wrote gen/input_scheme_formulae" + ("" if SCHEME == "alpha" else "_mw") + ".json")
print("DERIVEDONE")
