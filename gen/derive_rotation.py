"""
gen/derive_rotation.py  --  canonical field rotation for the input-scheme model (step 3).

After the input relations shift g, g' and v, the neutral gauge kinetic matrix
K = [[1-fW3, m],[m, 1-fB]] and the mass matrix (v^2/4)(1+dmZ) n n^T, n = (g,-g'), are no
longer diagonalised by the Standard Model rotation with the SM mixing angle that base.fr
keeps.  Without the compensating field rotation the Lagrangian carries spurious vertices
whose couplings vanish at the SM point and not otherwise (the FeynRules check found 36 LSM
vertices against base.fr's 31).  This is exactly what SMEFTsim's rotateGaugeB does at
O(1/Lambda^2); here it is derived to O(1/Lambda^4) with the same exact-then-expand method.

Construction.  V = (W3, B) = S (Z', A') with S^T K S = 1 and S^T M^2 S = diag(MZ^2, 0):
S = K^{-1/2} [z a], z = K^{-1/2} n / |K^{-1/2} n|, a = z rotated by 90 degrees.  base.fr
writes W3 = cw Z + sw A, B = -sw Z + cw A with the SM angle, i.e. V = R0 (Z, A), so
(Z, A) = T (Z', A') with T = R0^T S, T -> 1 at t = 0.  The charged W and the Higgs rescale
by 1/sqrt(1-fW) and 1/Zh.  Every square root is expanded as a series in the small matrix
delta K = 1 - K, so the algebra stays rational.  Validation: at O(t) the entries must
reproduce SMEFTsim's rotateGaugeB verbatim, including the dsth2/(2 sth cth) mixing terms,
which arise only because the SHIFTED g, g' from the input-scheme solution feed n.
"""
import math, json, os, sys
import sympy as sp
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import importlib.util
spec = importlib.util.spec_from_file_location("dis", os.path.join(os.path.dirname(os.path.abspath(__file__)), "derive_input_scheme.py"))
# reuse the input-scheme derivation (it prints its own validations first)
dis = importlib.util.module_from_spec(spec); spec.loader.exec_module(dis)
t, L6, L8 = dis.t, dis.L6, dis.L8
g0, gp0, v0 = dis.g0, dis.gp0, dis.v0
sol, sub = dis.sol, dis.sub
cHW, cHB, cHWB, cHDD, cHl3, cll1 = dis.cHW, dis.cHB, dis.cHWB, dis.cHDD, dis.cHl3, dis.cll1
cHbox = sp.symbols('cHbox', real=True)
c8W2H4x1, c8W2H4x3, c8B2H4x1, c8WBH4x1, c8H6x1, c8H6x2 = dis.c8W2H4x1, dis.c8W2H4x3, dis.c8B2H4x1, dis.c8WBH4x1, dis.c8H6x1, dis.c8H6x2

# shifted Lagrangian couplings and vev from the input-scheme solution
g  = dis.g.subs(sub).subs(sol); gp = dis.gp.subs(sub).subs(sol); v = dis.v.subs(sub).subs(sol)
e6, e8 = t*L6, t**2*L8
fW  = 2*cHW*v**2*e6 + c8W2H4x1*v**4*e8
fW3 = fW + c8W2H4x3*v**4*e8
fB  = 2*cHB*v**2*e6 + c8B2H4x1*v**4*e8
m   = cHWB*v**2*e6 + sp.Rational(1, 2)*c8WBH4x1*v**4*e8
zh  = cHDD*v**2*e6/2 - 2*cHbox*v**2*e6 + (c8H6x1 + c8H6x2)/4*v**4*e8     # Zh^2 = 1 + zh

def trunc(E, order=2):
    """Taylor polynomial in t through t^order, by differentiation at t = 0."""
    out = 0
    d = E
    for k in range(order + 1):
        out += sp.cancel(sp.together(d.subs(t, 0)))/math.factorial(k)*t**k
        d = sp.diff(d, t)
    return sp.expand(out)

def mtrunc(M): return M.applyfunc(trunc)
I2 = sp.eye(2)
dK = sp.Matrix([[fW3, -m], [-m, fB]])                 # K = 1 - dK
Kinvhalf = mtrunc(I2 + dK/2 + sp.Rational(3, 8)*dK*dK)  # (1 - dK)^(-1/2) to O(dK^2)
n = sp.Matrix([g, -gp])
x = mtrunc(Kinvhalf*n)
# |x| = sqrt(x.x): write x.x = N0^2 (1 + eta) with N0^2 the SM value g0^2 + gp0^2
N02 = g0**2 + gp0**2
eta = trunc(sp.expand((x.T*x)[0, 0]/N02 - 1))
inv_norm = trunc((1 - eta/2 + sp.Rational(3, 8)*eta**2))/sp.sqrt(N02)
z = mtrunc(x*inv_norm)
a = sp.Matrix([-z[1], z[0]])                          # photon direction: z = (g,-g')/N -> a = (g', g)/N, matching base.fr's A = (sw, cw) column
S = mtrunc(Kinvhalf*sp.Matrix.hstack(z, a))
# base.fr: W3 = cw Z + sw A, B = -sw Z + cw A  (SM angle), so V = R0 (Z, A)
sw0, cw0 = gp0/sp.sqrt(N02), g0/sp.sqrt(N02)
R0 = sp.Matrix([[cw0, sw0], [-sw0, cw0]])
T = mtrunc(R0.T*S)
# check T -> identity at t = 0
T0 = T.subs(t, 0).applyfunc(sp.simplify)
assert T0 == I2, f"T(0) is not the identity: {T0}"
rW = trunc((1 + fW/2 + sp.Rational(3, 8)*fW**2))            # W -> rW W
rh = trunc((1 - zh/2 + sp.Rational(3, 8)*zh**2))            # h -> rh h

# ---- validation against SMEFTsim rotateGaugeB at O(t) --------------------------------------
# The rotation depends on the input scheme, because the shifted g and g' that feed n do.  This
# file was written for {alpha, M_Z, G_F} and until 2026-10-05 computed its numerical point and
# SMEFTsim's dg1, dgw from that scheme's formulae whatever scheme the imported derivation had
# solved, and wrote the result into the alpha file whatever the scheme.  The {M_W, M_Z, G_F}
# formulae file therefore carried a copy of the alpha rotation, and the one model built from it
# had a photon coupled to neutrinos at 1/Lambda^4.  Everything scheme-dependent is now taken
# from the derivation that was actually run: the point, the first-order shifts, the file.
SCHEME = dis.SCHEME
num = dis.num
s, c = dis.sth, dis.cth
v0n = float(num[v0])
wc6 = {**dis.wc6, cHbox: 0.0}
vh2 = v0n**2
dg1, dgw = dis.dg1, dis.dgw            # SMEFTsim's first-order shifts IN THIS SCHEME
# SMEFTsim defines the shift of the mixing angle once, for both of its schemes
dsth2 = 2*c**2*s**2*(dg1 - dgw) + c*s*(1-2*s**2)*wc6[cHWB]*vh2
mix = vh2*(-wc6[cHB]*c*s + wc6[cHW]*c*s - 0.5*wc6[cHWB]*(1-2*s**2))
target = {  # SMEFTsim: OLD field in terms of NEW fields, first-order pieces
    'T_ZZ': vh2*(wc6[cHB]*s**2 + wc6[cHW]*c**2 + wc6[cHWB]*s*c),      # Z -> Z(1+...)
    'T_ZA': mix + dsth2/(2*s*c),                                      # Z -> ... + A(...)
    'T_AZ': mix - dsth2/(2*s*c),                                      # A -> ... + Z(...)
    'T_AA': vh2*(wc6[cHB]*c**2 + wc6[cHW]*s**2 - wc6[cHWB]*s*c),      # A -> A(1+...)
    'rW':   wc6[cHW]*vh2,
}
first = lambda E: float(sp.diff(E, t).subs(t, 0).subs({L6: 1, L8: 0}).subs(wc6).subs(num))
ours = {'T_ZZ': first(T[0, 0]), 'T_ZA': first(T[0, 1]), 'T_AZ': first(T[1, 0]), 'T_AA': first(T[1, 1]), 'rW': first(rW)}
print(f"=== rotation, O(t) vs SMEFTsim rotateGaugeB (L6 = 1), scheme {SCHEME} ===")
ok = True
for k in target:
    d = ours[k] - target[k]; ok &= abs(d) < 1e-9
    print(f"  {k:5s} ours {ours[k]:+.12f}  SMEFTsim {target[k]:+.12f}  diff {d:+.1e}")
print("  rotation O(t):", "PASS" if ok else "FAIL")
# canonical check at O(t^2): S^T K S must be the identity and S^T (n n^T) S must be diagonal, both through t^2
K = I2 - dK
canon = mtrunc(S.T*K*S) - I2
massoff = trunc((S.T*n*n.T*S)[0, 1])
print("=== O(t^2) self-test: max |S^T K S - 1| and |off-diagonal mass| coefficients (numeric, L6=1e-6, L8=1e-12) ===")
allwc = {**wc6, L6: 1e-6, L8: 1e-12, **num}
for tt in (1.0, 0.5):
    cn = max(abs(float(canon[i, j].subs(allwc).subs(t, tt))) for i in range(2) for j in range(2))
    mo = abs(float(massoff.subs(allwc).subs(t, tt)))
    print(f"  t={tt}: canonical residual {cn:.2e}   mass off-diagonal {mo:.2e}   (both should scale as t^3)")
from sympy.printing.mathematica import mathematica_code as mc
DEST = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "input_scheme_formulae.json" if SCHEME == "alpha" else "input_scheme_formulae_mw.json")
F = json.load(open(DEST))
for name, E in [('TZZ', T[0, 0] - 1), ('TZA', T[0, 1]), ('TAZ', T[1, 0]), ('TAA', T[1, 1] - 1), ('rW', rW - 1), ('rh', rh - 1)]:
    E = sp.expand(E)
    F[f"{name}1"] = mc(sp.factor(E.coeff(t, 1)))
    F[f"{name}2"] = mc(E.coeff(t, 2))
if not ok:
    sys.exit("rotation O(t) does not reproduce SMEFTsim: nothing written")
json.dump(F, open(DEST, "w"), indent=1)
print("wrote rotation entries {TZZ,TZA,TAZ,TAA,rW,rh}{1,2} to gen/" + os.path.basename(DEST), "for the", SCHEME, "scheme")
print("ROTATIONDONE")
