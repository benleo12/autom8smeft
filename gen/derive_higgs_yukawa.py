"""
gen/derive_higgs_yukawa.py  --  the Higgs quartic and the Yukawas as series in the input shifts.

WHY.  MadGraph counts interaction orders on couplings, and FeynRules assigns an order to a
coupling by the tagged parameters that appear in it explicitly.  If the corrected vev entered the
doublet as one internal parameter vevT = vevSM (1 + vev1 + vev2), and the quartic and the Yukawas
were exact functions of vevT, every coupling built from them would be a function of the Wilson
coefficients that carries no NP tag.  The NP=0 amplitude would then move with the coefficients,
and NP^2==2 would hold products of a tagged and an untagged shift, i.e. terms quadratic in the
coefficients.  The gauge couplings have the form that avoids this: gw and g1 enter the
Lagrangian as gwSM (1 + gw1 + gw2), a sum FeynRules splits by order.

WHAT.  The same form for the vev, the quartic and the Yukawas, with the series truncated at
O(1/Lambda^4):

    Phi      = (vevSM (1 + vev1 + vev2) + H)/Sqrt[2]
    quartic  = lam (1 + lamr1 + lamr2),       lam = MH^2/(2 vevSM^2)
    Yukawa   = y_f (1 + yr1 + yr2) + c8fH5 vevSM^4 L8/4,   y_f = Sqrt[2] m_f/vevSM

where lamr1, yr1 are O(1/Lambda^2) and lamr2, yr2 are O(1/Lambda^4), dimension-six squared
included.  They follow from the exact relations

    lam  = (Zh2 MH^2/vevT^2 + 3 cH vevT^2 L6 + 3 c8H8 vevT^4 L8)/2
    y_f  = Sqrt[2] m_f/vevT + c8fH5 vevT^4 L8/4
    Zh2  = 1 + (cHDD/2 - 2 cHbox) vevT^2 L6 + (c8H6x1 + c8H6x2)/4 vevT^4 L8

by expanding in a bookkeeping parameter t with vev1, cH, cHDD, cHbox at O(t) and vev2, c8H8,
c8H6x1, c8H6x2 at O(t^2).  muH is left alone: it multiplies only the tadpole and the h mass term,
neither of which is a vertex.  The W mass is left exact, as SMEFTsim 3 does by default.

Zh2 is the coefficient of the Higgs kinetic term and it is evaluated at the CORRECTED vev, like
everything else here.  The dimension-six operators are evaluated at the corrected vev
(gen/make_dim6.py), and gen/derive_rotation.py derives the rescaling of h from the same quantity
at the corrected vev.  Zh2 at vevSM would differ by (cHDD - 4 cHbox) vev1 vevSM^2 L6, a product
of two dimension-six coefficients, and the quartic and the rescaling of h would then agree only
when the dimension-six sector is off.  validate/check_bilinears.wls tests this through the Higgs
mass, which must equal its input at second order.

The results are merged into gen/input_scheme_formulae.json and gen/input_scheme_formulae_mw.json
under lamr1, lamr2, yr1, yr2, and gen/input_scheme.py reads them from there.
"""
import json
import os
import random

import sympy as sp
from sympy.printing.mathematica import mathematica_code as mc

HERE = os.path.dirname(os.path.abspath(__file__))

t = sp.symbols('t')
vev1, vev2 = sp.symbols('vev1 vev2')
cH, cHDD, cHbox, c8H8, c8H6x1, c8H6x2 = sp.symbols('cH cHDD cHbox c8H8 c8H6x1 c8H6x2')
L6, L8, vevSM, MH, yf, c8f = sp.symbols('L6 L8 vevSM MH yf c8f', positive=True)

# every tagged quantity carries its power of t
o1 = {vev1: t*vev1, cH: t*cH, cHDD: t*cHDD, cHbox: t*cHbox}
o2 = {vev2: t**2*vev2, c8H8: t**2*c8H8, c8H6x1: t**2*c8H6x1, c8H6x2: t**2*c8H6x2}
tag = lambda e: e.subs({**o1, **o2}, simultaneous=True)

vevT = vevSM*(1 + vev1 + vev2)
Zh2 = 1 + (cHDD/2 - 2*cHbox)*vevT**2*L6 + (c8H6x1 + c8H6x2)/4*vevT**4*L8
lam_exact = (Zh2*MH**2/vevT**2 + 3*cH*vevT**2*L6 + 3*c8H8*vevT**4*L8)/2
lam0 = MH**2/(2*vevSM**2)
# the Yukawa, with the class-12 term written separately: it is O(t^2) on its own, so to this
# order it multiplies vevSM^4 and not vevT^4, and the relative series is the same for every fermion
y_exact = sp.sqrt(2)*(yf*vevSM/sp.sqrt(2))/vevT      # = y_f vevSM/vevT with y_f = sqrt2 m_f/vevSM


def coeff(E, k):
    d = E
    for _ in range(k):
        d = sp.diff(d, t)
    return sp.expand(sp.cancel(d.subs(t, 0)))/sp.factorial(k)


lamr = [sp.expand(coeff(tag(lam_exact)/lam0, k)) for k in (0, 1, 2)]
yr = [sp.expand(coeff(tag(y_exact)/yf, k)) for k in (0, 1, 2)]
assert lamr[0] == 1 and yr[0] == 1, (lamr[0], yr[0])

print("lamr1 =", lamr[1])
print("lamr2 =", lamr[2])
print("yr1   =", yr[1])
print("yr2   =", yr[2])

# truncation self-test: the residual of the exact quantity against its series must be O(t^3)
rng = random.Random(8)
num = {vev1: 0.013, vev2: -0.004, cH: 0.7, cHDD: -0.5, cHbox: 0.3, c8H8: 0.6, c8H6x1: 0.8,
       c8H6x2: -0.2, L6: 0.03, L8: 0.002, vevSM: 1.0, MH: 0.508, yf: 1.0}
# in units of the vev, with L6 and L8 chosen so that every shift is a few per cent at t = 1
print("=== truncation residuals, should fall by about 8x per halving of t ===")
for tt in (1.0, 0.5, 0.25):
    s = {**num, t: tt}
    ex_l = float(tag(lam_exact).subs(s)/lam0.subs(s))
    se_l = float(sum(c*tt**k for k, c in enumerate(lamr)).subs(num))
    ex_y = float(tag(y_exact).subs(s)/yf.subs(s))
    se_y = float(sum(c*tt**k for k, c in enumerate(yr)).subs(num))
    print(f"  t={tt:<4}  lam {ex_l - se_l:+.3e}   yukawa {ex_y - se_y:+.3e}")

out = {"lamr1": mc(lamr[1]), "lamr2": mc(lamr[2]), "yr1": mc(yr[1]), "yr2": mc(yr[2])}
for name in ("input_scheme_formulae.json", "input_scheme_formulae_mw.json"):
    p = os.path.join(HERE, name)
    old = json.load(open(p)) if os.path.exists(p) else {}
    json.dump(old | out, open(p, "w"), indent=1)
    print("merged lamr1, lamr2, yr1, yr2 into", name)
