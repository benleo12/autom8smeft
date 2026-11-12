#!/usr/bin/env python3
"""
gen/derive_geo.py  --  the input relations, the canonical field rotation, the Higgs quartic, the Yukawas and
the gluon rescaling to O(t^N), with the geoSMEFT towers above dimension eight.

    python3 gen/derive_geo.py N [mw|alpha]      writes gen/input_scheme_formulae_geo{N}_{scheme}.json

It is gen/derive_input_scheme.py, gen/derive_rotation.py and gen/derive_higgs_yukawa.py carried to any order:
the same exact relations, the same conventions and the same names, with the operators of the field-space
connections (arXiv:2001.01453) added at every dimension that reaches O(t^N).  Through O(t^2) its results are
those three scripts' (validation (1) below), and the default N of a released model is 2.

BOOKKEEPING.  A dimension-six coefficient carries t (with L6 = 1/Lam^2), a dimension-eight one t^2 (L8 =
1/Lam^4), and one of dimension d = 8 + 2k carries t^{2+k} with L{d} = 1/Lam^{d-4} (L10, L12, ...).  The
solution is the polynomial in t through t^N, and t -> 1 in the formulae written.

TOWERS.  The member of dimension 8 + 2k of a dimension-eight connection operator Q is (H^dag H)^k Q, with the
coefficient c{d} + the label of Q, e.g. c10H6x1 for (H^dag H) Q_{H^6}^{(1)}.  At the vacuum H^dag H = v^2/2,
so every vacuum quantity of (H^dag H)^k Q (a kinetic or mass term, a W-lepton coupling, a four-lepton
contact) is (v^2/2)^k times that of Q, with the extra 1/Lam^{2k}.  The one exception is the Higgs mass,
which takes the second derivative of the potential: (H^dag H)^n contributes n(n-1) C_n (v^2/2)^{n-2} to 2 lam.
The dimension-eight form factors are those of gen/derive_input_scheme.py:

    L_kin = -(1/4)[(1-fW)(W1^2+W2^2) + (1-fW3) W3^2 + (1-fB) B^2 + 2 m W3.B]
      fW  = 2 cHW v^2 L6 + T[W2H4x1] v^4         fW3 = fW + T[W2H4x3] v^4
      fB  = 2 cHB v^2 L6 + T[B2H4x1] v^4         m   = cHWB v^2 L6 + T[WBH4x1] v^4/2
    M_W^2 = g^2 v^2/4 (1 + dmW)/(1 - fW),          dmW = (T[H6x1] - T[H6x2]) v^4/4
    M_neutral^2 = (v^2/4)(1 + dmZ) n n^T,          dmZ = cHDD v^2 L6/2 + (T[H6x1] + T[H6x2]) v^4/4
    Zh^2 = 1 + zh,   zh = (cHDD/2 - 2 cHbox) v^2 L6 + (T[H6x1] + T[H6x2]) v^4/4
    gluon: -(1/4)(1 - x) G G,   x = 2 cHG v^2 L6 + T[G2H4x1] v^4

where T[X] = sum over d = 8, 10, ... of c{d}X L{d} (v^2/2)^{(d-8)/2}, cut at order t^N.

MUON DECAY.  G_F is read off the rate as the experiment reads it, G_F^2 = 192 pi^3 Gamma/(m_mu^5 f(x)), the
Standard Model's tree rate with the same x = m_e^2/m_mu^2.  With the W exchanged at zero momentum the operators
of the models give the decay two couplings, A of O = (nubar_mu g P_L mu)(ebar g P_L nu_e) and S of
O_S = (ebar P_L nu_e)(nubar_mu P_R mu), each relative to the Standard Model's -2/v^2 (g^V_LL and g^S_RR of the
Michel analysis), and with the rate given below

    sqrt2 GF v^2 = [ |A|^2 + 2 Re(A) s yleta + s^2 ylprod/4 ]^(1/2),    A = f_mu conj(f_e)/(1 + dmW) + dc + i dci,

where S = y_e y_mu s.  Without S it is |A|, 2007.00565's eqs. gfermi2 and allordersGF.

f_p = 1 + dl_p + i a_p is the factor of the nubar_p e_p W vertex.  The CP-even operators give dl_p,

    dl_p = cHl3 v^2 L6 + (T[l2H4Dx2] + T[l2H4Dx4] + y_p^2 (T[l2H4Dx2FE] + T[l2H4Dx4FE])) v^4/2,

as gen/derive_input_scheme.py has them, and the CP-odd Q_{l^2H^4D}^{(3)} = i eps^{IJK} (lbar tau^I l)
(H^dag tau^J D H - h.c.)(H^dag tau^K H) gives an imaginary part,

    a_p = -(T[l2H4Dx3] + y_p^2 T[l2H4Dx3FE]) v^4/2

(at the vacuum it is -(g v^4/4) eps^{IJ3}(lbar tau^I l) W^J, whose nubar e entry is -i v^4/2 times the
Standard Model's (g/2)(W^1 - i W^2); the same computation gives the v^4/2 of Q^{(2)} and Q^{(4)}).  It enters
only through f_mu conj(f_e), at O(t^4): a_mu a_e in the real part (2007.00565's <L_{1,2}>^2) and
a_mu(1 + dl_e) - a_e(1 + dl_mu) in the imaginary part.  y_p^2 = 2 m_p^2/vevSM^2 is the weight of the
structure (Y_e Y_e^dag)_pp, the parameter yl of the base, which is not shifted.

The contact terms, real and imaginary, are

    dc  = -cll1 v^2 L6 - (T[l4H2x1Fx00] + T[l4H2x1Fx0E] ylsq/2) v^4/2
          + (T3[l4H2x3Fx00] + T3[l4H2x3Fx0E] ylsq/2) v^2 (v^2/2)^2,
    dci = -T[l4H2x2Fx0EIm] (y_e^2 - y_mu^2) v^4/4,

with T3[X] = sum over d = 10, 12, ... of c{d}X L{d} (v^2/2)^{(d-10)/2}.  The first two lines are
2007.00565's LLLL tower, with Q_{l^4H^2}^{(1)} = (H^dag H)(lbar g l)(lbar g l) its "llH" and
c{d}l4H2x3 the coefficient of the new operator at d = 10 + 2m,

    (H^dag H)^m (H^dag tau^I H)(H^dag tau^J H)(lbar_p g tau^I l_r)(lbar_s g tau^J l_t),

its "l.l.H.H", with the structures Fx00 = delta_pt delta_sr and Fx0E = delta_pt (Y_e Y_e^dag)_sr of
Q_{l^4H^2}^{(1)}.  Its weight: at the vacuum H^dag tau^I H = -(v^2/2) delta^{I3}, so the operator is
(v^2/2)^{m+2} (lbar tau^3 l)(lbar tau^3 l), and in the crossed structure (lbar_mu tau^3 l_e)(lbar_e tau^3 l_mu)
the piece (nubar_mu nu_e)(ebar mu), which the Fierz identity of two left-handed currents turns into O with a
plus sign, comes with (+1)(-1).  The singlet crossed structure gives it with (+1)(+1).  So at equal
dimension l.l.H.H has the weight of llH with the opposite sign.  In 2007.00565's G^{4pt}_{ll}, whose n-th
l.l.H.H term has two more mass dimensions than its n-th llH term, this reads +C_ll, +llH/2^{1+n},
-l.l.H.H/2^{2+n}.  The imaginary contact is the crossed structure delta_pt
(Y_e Y_e^dag)_sr of Q_{l^4H^2}^{(2)} = (H^dag tau^I H)(lbar g l)(lbar g tau^I l), whose coefficient is
i c8l4H2x2Fx0EIm: at the vacuum it gives i c (v^2/2)(y_e^2 - y_mu^2)(O - O^dag), the antisymmetric
combination of 2007.00565's l.Hl H.

The scalar coupling.  With the flavour structures of the models every four-lepton contact either has the
Standard Model's neutrinos and chirality, and is in dc or dci above, or does not reach muon decay at zero
momentum, except the crossed structures (Y_e)_pt (Y_e^dag)_sr of Q_{l^2e^2H^2}^{(1)} = (H^dag H)(lbar g l)(ebar g e)
and Q_{l^2e^2H^2}^{(2)} = (H^dag tau^I H)(lbar g tau^I l)(ebar g e), the coefficients c8l2e2H2x1Fx00 and
c8l2e2H2x2Fx00, and their towers.  Of the sum over flavours only (p r s t) = (mu e e mu) holds
(nubar_mu nu_e)(ebar mu), with the weight (Y_e)_mumu (Y_e^dag)_ee = y_e y_mu.  At the vacuum Q^{(1)} gives it with
v^2/2 and Q^{(2)} with -v^2/2, since H^dag tau^I H = -(v^2/2) delta^{I3} and tau^3 is +1 on the neutrinos, and
the Fierz identity of a left- and a right-handed current turns (nubar_mu g P_L nu_e)(ebar g P_R mu) into
-2 (nubar_mu P_R mu)(ebar P_L nu_e).  So S = y_e y_mu s, with

    s = (T[l2e2H2x1Fx00] - T[l2e2H2x2Fx00]) v^4/2.

Nothing else reaches S or a coupling of another kind.  The scalar Q_{l^2e^2H^2}^{(3)} = (lbar e H)(lbar e H) holds no
neutrino at the vacuum, the other structures of Q_{l^2e^2H^2}^{(1),(2)} give the two neutrinos one flavour, Q_le
has delta_pr delta_st alone in U(3)^5, a tensor coupling needs a right-handed neutrino, and the dipoles of
dimension six and eight carry the momentum of the W.  With Y_e diagonal every structure keeps the lepton number
of each flavour, so the neutrinos are the Standard Model's.  Summed over spins, the rate of S is that of O with
the two neutrino momenta exchanged, so |S|^2/4 has the Standard Model's phase space, and S interferes with A only
through the electron mass (the Michel eta, Re(A conj S)/2):

    192 pi^3 Gamma/(m_mu^5 G0^2) = (|A|^2 + |S|^2/4) f(x) + 2 sqrt(x) Re(A conj S) g(x),    G0 = 1/(sqrt2 v^2),
    f = 1 - 8x + 8x^3 - x^4 - 12 x^2 ln x,    g = 1 + 9x - 9x^2 - x^3 + 6x(1 + x) ln x.

S is real, its structure being real and Hermitian, and sqrt(x) = y_e/y_mu, so the interference is
2 Re(A) s yleta with yleta = y_e^2 g(x)/f(x), and the square is s^2 ylprod/4.  The interference enters at O(t^2)
and the square at O(t^4).  Both vanish for massless e and mu, the models' default (yme = ymm = 0), as do the
terms of dl, a and dci that are weighted by lepton Yukawas.  All of them are kept, exactly.

Apart from yleta, in which the electron is the lighter lepton of the decay, the relations are symmetric in e
and mu.  They are written through ylsq = y_e^2 + y_mu^2 (the base's 2 (yme^2 + ymm^2)/vevSM^2),
ylprod = y_e^2 y_mu^2 (= 4 yme^2 ymm^2/vevSM^4) and yleta, the last two new helpers of the base, which computes
yleta from yme and ymm (gen/input_scheme.py).  ylprod first appears at O(t^4).

SOLUTION.  The three inputs ({MW, MZ, GF} or {alpha, MZ, GF}) are imposed on g = gwSM (1 + sum gw_k t^k),
g' = g1SM (1 + sum g1_k t^k), v = vevSM (1 + sum vev_k t^k) order by order: at order k the equations are
linear in gw_k, g1_k, vev_k with the Standard-Model Jacobian.  The arithmetic is that of power series in t
truncated at t^N, with inverses, square roots and the matrix K^{-1/2} as series, so nothing is
differentiated and N = 4 takes minutes.  The rotation is gen/derive_rotation.py's construction
S = K^{-1/2} [z a], T = R0^T S, rW = (1 - fW)^{-1/2}, rh = (1 + zh)^{-1/2}, with every square root a
series.  They, and the derived alpha (or M_W^2), are written in the symbols gw_k, g1_k and vev_k, which the
base declares before them, so that each is a short polynomial in those and the coefficients.  Written out in
the coefficients alone, aEW4 alone would run to millions of characters, which FeynRules, the UFO and the
Fortran MadGraph writes from it would carry for nothing.

The quartic and the Yukawas are series in the vev shifts, as gen/derive_higgs_yukawa.py writes them:

    lam (1 + lamr1 + ... + lamrN),   2 lam = Zh^2 MH^2/vT^2 + 3 cH vT^2 L6 + sum_n n(n-1) c{2n}H8 L{2n} (vT^2/2)^{n-2}
    y_f (1 + yr1 + ... + yrN) + sum_d yc{d} (c{d}fH5 structures),   y_f = Sqrt[2] m_f/vevSM

with vT = vevSM (1 + vev1 + ... + vevN), each vev_k of order t^k, Zh^2 at vT, and the class-12 operators'
mass terms compensated so that the fermion masses stay at their inputs: (H^dag H)^{2+k}(fbar f H) adds
-(vT/Sqrt2) c (vT^2/2)^{2+k} L{d} to the mass, so the compensation is c vT^{4+2k} L{d}/2^{2+k}, written as
yc{d} = vevSM^{4+2k} L{d}/2^{2+k} [(1 + vev1 + ...)^{4+2k}]_{order <= N - 2 - k}; yc8 = vevSM^4 L8/4 at N = 2.

The gluon: G' = Sqrt[1 - x] G and g_s' = g_s/Sqrt[1 - x] keep g_s G, so G -> (1 + rG) G' with
1 + rG = (1 - x)^{-1/2} and g_s -> g_s (1 + sG) with 1 + sG = (1 - x)^{1/2} = 1/(1 + rG) exactly
(gen/make_dim6.py writes g_s (1 - rG1), its first order).  rG1 = cHG vevSM^2 L6 as there.  These too are
written in the symbols vev_k.

KEYS of the JSON (Mathematica strings, k = 1..N; "keys" holds these descriptions and N, scheme):
    gw{k}, g1{k}, vev{k}     the O(t^k) relative shifts of gw, g1 and the vev
    aEW{k} (mw) / MW2{k} (alpha)   the derived alpha, or M_W^2, as aEWSM (1 + sum aEW_k), MW2SM (1 + sum MW2_k),
                             in the symbols gw1..gwN, g11..g1N, vev1..vevN
    TZZ{k}, TZA{k}, TAZ{k}, TAA{k}   Z -> (1 + TZZ) Z + TZA A, A -> TAZ Z + (1 + TAA) A, order k, in the same symbols
    rW{k}, rh{k}             W -> (1 + rW) W, h -> (1 + rh) h, in the symbols vev1..vevN
    lamr{k}, yr{k}           the quartic and Yukawa series, in the symbols vev1..vevN
    yc{d}                    the class-12 compensation multiplier of dimension d (8, 10, ..., up to order N)
    xG{k}, rG{k}, sG{k}      the gluon's vacuum form factor x, its field rescaling and the g_s factor, in vev1..vevN
New symbols the base must declare: L10, L12, ... = 1/Lam^6, 1/Lam^8, ...; ylprod and yleta; the tower coefficients.

VALIDATION, printed with PASS or FAIL:
    (1) through O(t^2) every key of gen/input_scheme_formulae_mw.json (or gen/input_scheme_formulae.json
        for alpha) equals this script's, symbolically;
    (2) the residuals of the exact relations (the three inputs, the derived alpha or M_W^2, S^T K S = 1, the
        diagonal neutral mass, rW, rh, the gluon, the quartic and the Yukawa) at the truncated solution fall
        as t^{N+1}, at a random point with every coefficient on, towers and lepton Yukawas included (yleta at
        its value for those Yukawas), the symbols gw_k, g1_k and vev_k at their solved values;
    (3) T(0) = 1, and S^T K S = 1, a diagonal neutral mass matrix and a massless photon through t^N,
        exactly, at three rational points, which hold whatever the values of gw_k, g1_k and vev_k;
    (4) MH and the fermion masses equal their inputs through t^N, exactly, at three rational points.
"""
import json
import math
import os
import random
import sys
import time

import mpmath as mp
import sympy as sp
from sympy.printing.mathematica import mathematica_code as mc

HERE = os.path.dirname(os.path.abspath(__file__))
if len(sys.argv) < 2 or not sys.argv[1].isdigit():
    print(__doc__, file=sys.stderr)
    sys.exit(2)   # the usage, with the exit status of argparse
N = int(sys.argv[1])
SCHEME = (sys.argv[2] if len(sys.argv) > 2 else "mw").lower()
assert N >= 1 and SCHEME in ("mw", "alpha"), (N, SCHEME)
CLOCK = time.time()


def stamp(msg):
    print(f"[{time.time() - CLOCK:7.1f} s] {msg}", flush=True)


# ---- symbols ----------------------------------------------------------------------------------------
t = sp.Symbol('t')
g0, gp0, v0 = sp.symbols('gwSM g1SM vevSM', positive=True)
MH, yf = sp.symbols('MH yf', positive=True)
ylsq, ylprod = sp.Symbol('ylsq', nonnegative=True), sp.Symbol('ylprod', nonnegative=True)
yleta = sp.Symbol('yleta', real=True)         # y_e^2 g(x)/f(x), the weight of the Michel eta term
yD = sp.Symbol('ylD', real=True)              # y_e^2 - y_mu^2, eliminated before anything is written
ye2, ym2 = (ylsq + yD)/2, (ylsq - yD)/2
DIMS = list(range(8, 2*N + 5, 2))             # dimensions >= 8 that reach O(t^N): order (d - 4)/2 <= N
ORDER = {d: (d - 4)//2 for d in [6] + DIMS}
L = {d: sp.Symbol(f'L{d}', positive=True) for d in [6] + DIMS}
cHW, cHB, cHWB, cHDD, cHl3, cll1, cHbox, cH, cHG = sp.symbols('cHW cHB cHWB cHDD cHl3 cll1 cHbox cH cHG', real=True)
DIM6 = [cHW, cHB, cHWB, cHDD, cHl3, cll1, cHbox, cH, cHG]
VEVS = [sp.Symbol(f'vev{j}') for j in range(1, N + 1)]   # as gen/derive_higgs_yukawa.py: no assumptions
GWS = [sp.Symbol(f'gw{j}') for j in range(1, N + 1)]     # the shifts of the couplings, as symbols of the base
G1S = [sp.Symbol(f'g1{j}') for j in range(1, N + 1)]
LABELS = ['W2H4x1', 'W2H4x3', 'B2H4x1', 'WBH4x1', 'H6x1', 'H6x2', 'H8', 'G2H4x1',
          'l2H4Dx2', 'l2H4Dx4', 'l2H4Dx2FE', 'l2H4Dx4FE', 'l2H4Dx3', 'l2H4Dx3FE',
          'l4H2x1Fx00', 'l4H2x1Fx0E', 'l4H2x2Fx0EIm']
LABELS10 = ['l4H2x3Fx00', 'l4H2x3Fx0E']      # the new four-lepton operator, from dimension ten
LABELS_S = ['l2e2H2x1Fx00', 'l2e2H2x2Fx00']  # the scalar coupling of muon decay, from dimension eight
COEF = {}


def c(label, d):
    name = f"c{d}{label}"
    if name not in COEF:
        COEF[name] = sp.Symbol(name, real=True)
    return COEF[name]


for d in DIMS:
    for lab in LABELS + (LABELS10 if d >= 10 else []) + LABELS_S:
        c(lab, d)

# ---- power series in t, truncated at t^ORD -------------------------------------------------------------
ORD = N


def binom(p, n):
    out = sp.Integer(1)
    for i in range(n):
        out *= (p - i)
    return out/math.factorial(n)


class Ser:
    """c[0] + c[1] t + ... + c[ORD] t^ORD with sympy coefficients."""
    __slots__ = ("c",)

    def __init__(self, cs=()):
        cs = [sp.sympify(x) for x in list(cs)[:ORD + 1]]
        self.c = cs + [sp.Integer(0)]*(ORD + 1 - len(cs))

    @staticmethod
    def lift(x):
        return x if isinstance(x, Ser) else Ser([x])

    def __add__(self, o):
        o = Ser.lift(o)
        return Ser([a + b for a, b in zip(self.c, o.c)])
    __radd__ = __add__

    def __neg__(self):
        return Ser([-a for a in self.c])

    def __sub__(self, o):
        return self + (-Ser.lift(o))

    def __rsub__(self, o):
        return Ser.lift(o) - self

    def __mul__(self, o):
        if not isinstance(o, Ser):
            o = sp.sympify(o)
            return Ser([sp.expand(a*o) for a in self.c])
        out = [sp.Integer(0)]*(ORD + 1)
        for i, a in enumerate(self.c):
            if a == 0:
                continue
            for j in range(ORD + 1 - i):
                if o.c[j] != 0:
                    out[i + j] += a*o.c[j]
        return Ser([sp.expand(x) for x in out])
    __rmul__ = __mul__

    def shift(self, m):
        """times t^m"""
        return Ser([0]*m + self.c)

    def inv(self):
        a0 = self.c[0]
        assert a0 != 0, "series without a constant term has no inverse"
        b = [1/a0]
        for n in range(1, ORD + 1):
            b.append(sp.expand(-sum(self.c[j]*b[n - j] for j in range(1, n + 1))/a0))
        return Ser(b)

    def __truediv__(self, o):
        if not isinstance(o, Ser):
            return self*(1/sp.sympify(o))
        return self*o.inv()

    def __rtruediv__(self, o):
        return Ser.lift(o)*self.inv()

    def __pow__(self, p):
        p = sp.Rational(p)
        if p.is_Integer and p >= 0:
            out = Ser([1])
            for _ in range(int(p)):
                out = out*self
            return out
        a0 = self.c[0]
        u = self/a0 - 1
        out, term = Ser([1]), Ser([1])
        for n in range(1, ORD + 1):
            term = term*u
            out = out + term*binom(p, n)
        return out*(a0**p)

    def total(self, upto=None):
        """the polynomial with t -> 1, through t^upto"""
        return sum(self.c[:(ORD if upto is None else upto) + 1], sp.Integer(0))


def mmul(A, B):
    return [[A[i][0]*B[0][j] + A[i][1]*B[1][j] for j in range(2)] for i in range(2)]


def mvec(A, x):
    return [A[0][0]*x[0] + A[0][1]*x[1], A[1][0]*x[0] + A[1][1]*x[1]]


def mT(A):
    return [[A[0][0], A[1][0]], [A[0][1], A[1][1]]]


# ---- the vacuum form factors ----------------------------------------------------------------------------
# Each is a sum of monomials (order in t, coefficient, power of v^2, rational prefactor), so that the same
# table gives the series and, for the residual test, the exact numbers.
def tower(label, pre, p8, dims=None, first=8):
    """sum over d of c{d}label L{d} (v^2/2)^{(d-first)/2} times pre v^{2 p8}"""
    return [(ORDER[d], c(label, d)*L[d], p8 + (d - first)//2, sp.Rational(pre)/2**((d - first)//2))
            for d in (dims if dims is not None else DIMS) if d >= first]


def table():
    T = {}
    T['fW'] = [(1, cHW*L[6], 1, 2)] + tower('W2H4x1', 1, 2)
    T['fW3'] = T['fW'] + tower('W2H4x3', 1, 2)
    T['fB'] = [(1, cHB*L[6], 1, 2)] + tower('B2H4x1', 1, 2)
    T['m'] = [(1, cHWB*L[6], 1, 1)] + tower('WBH4x1', sp.Rational(1, 2), 2)
    T['dmW'] = tower('H6x1', sp.Rational(1, 4), 2) + tower('H6x2', -sp.Rational(1, 4), 2)
    T['dmZ'] = [(1, cHDD*L[6], 1, sp.Rational(1, 2))] + tower('H6x1', sp.Rational(1, 4), 2) + tower('H6x2', sp.Rational(1, 4), 2)
    T['zh'] = [(1, (cHDD/2 - 2*cHbox)*L[6], 1, 1)] + tower('H6x1', sp.Rational(1, 4), 2) + tower('H6x2', sp.Rational(1, 4), 2)
    for p, y2 in (('m', ym2), ('e', ye2)):
        T['dl' + p] = ([(1, cHl3*L[6], 1, 1)] + tower('l2H4Dx2', sp.Rational(1, 2), 2) + tower('l2H4Dx4', sp.Rational(1, 2), 2)
                       + [(o, y2*x, q, f) for o, x, q, f in tower('l2H4Dx2FE', sp.Rational(1, 2), 2) + tower('l2H4Dx4FE', sp.Rational(1, 2), 2)])
        T['a' + p] = (tower('l2H4Dx3', -sp.Rational(1, 2), 2)
                      + [(o, y2*x, q, f) for o, x, q, f in tower('l2H4Dx3FE', -sp.Rational(1, 2), 2)])
    T['dc'] = ([(1, cll1*L[6], 1, -1)] + tower('l4H2x1Fx00', -sp.Rational(1, 2), 2)
               + [(o, ylsq/2*x, q, f) for o, x, q, f in tower('l4H2x1Fx0E', -sp.Rational(1, 2), 2)]
               + tower('l4H2x3Fx00', sp.Rational(1, 4), 3, first=10)
               + [(o, ylsq/2*x, q, f) for o, x, q, f in tower('l4H2x3Fx0E', sp.Rational(1, 4), 3, first=10)])
    T['dci'] = [(o, yD*x, q, f) for o, x, q, f in tower('l4H2x2Fx0EIm', -sp.Rational(1, 4), 2)]
    # s of the scalar coupling S = y_e y_mu s
    T['ds'] = tower('l2e2H2x1Fx00', sp.Rational(1, 2), 2) + tower('l2e2H2x2Fx00', -sp.Rational(1, 2), 2)
    T['xG'] = [(1, cHG*L[6], 1, 2)] + tower('G2H4x1', 1, 2)
    # the curvature of the potential at the minimum: sum_n n(n-1) C_n (v^2/2)^{n-2}, C_3 = cH L6, C_{d/2} = c{d}H8 L{d}
    T['curv'] = [(1, cH*L[6], 1, 3)] + [(ORDER[d], c('H8', d)*L[d], d//2 - 2, sp.Rational((d//2)*(d//2 - 1), 2**(d//2 - 2)))
                                        for d in DIMS]
    return {k: [m for m in v if m[0] <= N] for k, v in T.items()}


TABLE = table()


def ser_of(name, vv):
    """the form factor as a series, v^2 = vv a series"""
    pw = {0: Ser([1])}
    out = Ser()
    for o, x, q, f in TABLE[name]:
        if o > ORD:
            continue
        for j in range(max(pw) + 1, q + 1):
            pw[j] = pw[j - 1]*vv
        out = out + (pw[q]*(f*x)).shift(o)
    return out


XN = {}


def num_of(name, v2, tt):
    """the form factor as a number at the point of the residual test, every coefficient of order o scaled by
    tt^o.  A coefficient of the table can be a product or a sum (cHW L6, (cHDD/2 - 2 cHbox) L6), so it is
    evaluated by substitution."""
    tot = mp.mpf(0)
    for o, x, q, f in TABLE[name]:
        if x not in XN:
            XN[x] = numc(x)
        f = sp.Rational(f)
        tot += XN[x]*mp.mpf(f.p)/f.q*v2**q*tt**o
    return tot


# ---- the input relations ----------------------------------------------------------------------------------
N02 = g0**2 + gp0**2
aEW_of = g0**2*gp0**2/N02                    # e0^2
MZ2_of = N02*v0**2/4
MW2_of = g0**2*v0**2/4


def physics(A, B, C):
    """g = g0(1+A), g' = gp0(1+B), v = v0(1+C), A, B, C series without constant term"""
    g, gp = (1 + A)*g0, (1 + B)*gp0
    vv = (1 + C)*(1 + C)*v0**2
    F = {k: ser_of(k, vv) for k in ('fW', 'fW3', 'fB', 'm', 'dmW', 'dmZ', 'dlm', 'dle', 'am', 'ae', 'dc', 'dci', 'ds')}
    K11, K12, K22 = 1 - F['fW3'], F['m'], 1 - F['fB']
    detK = K11*K22 - K12*K12
    e2 = g*g*gp*gp/(gp*gp*K11 + 2*g*gp*K12 + g*g*K22)
    MZ2 = vv*(1 + F['dmZ'])*(g*g*K22 + 2*g*gp*K12 + gp*gp*K11)/(4*detK)
    MW2 = g*g*vv*(1 + F['dmW'])/(4*(1 - F['fW']))
    W = 1/(1 + F['dmW'])
    Re = ((1 + F['dlm'])*(1 + F['dle']) + F['am']*F['ae'])*W + F['dc']
    Im = (F['am']*(1 + F['dle']) - F['ae']*(1 + F['dlm']))*W + F['dci']
    R = (Re*Re + Im*Im + 2*Re*F['ds']*yleta + F['ds']*F['ds']*(ylprod/4))**sp.Rational(1, 2)
    return dict(g=g, gp=gp, vv=vv, F=F, e2=e2, MZ2=MZ2, MW2=MW2, R=R)


def equations(A, B, C):
    P = physics(A, B, C)
    first = P['e2']/aEW_of - 1 if SCHEME == "alpha" else P['MW2']/MW2_of - 1
    return [first, P['MZ2']/MZ2_of - 1, P['vv']/v0**2 - P['R']]


stamp(f"N = {N}, scheme {SCHEME}, dimensions {[6] + DIMS}, {len(COEF)} coefficients above dimension six")
a_, b_, c_ = sp.symbols('a_ b_ c_')
As, Bs, Cs = [sp.Integer(0)], [sp.Integer(0)], [sp.Integer(0)]
J1 = None
for k in range(1, N + 1):
    ORD = k
    E = equations(Ser(As + [a_]), Ser(Bs + [b_]), Ser(Cs + [c_]))
    Ek = [sp.expand(e.c[k]) for e in E]
    for e in E:
        assert all(sp.simplify(e.c[j]) == 0 for j in range(1 if k > 1 else 0, 1)), "zeroth order"
    J = sp.Matrix([[sp.diff(e, x) for x in (a_, b_, c_)] for e in Ek])
    assert not (J.free_symbols & {a_, b_, c_}), f"order {k}: not linear in the order-{k} shifts"
    J = J.applyfunc(sp.cancel)
    if J1 is None:
        J1 = J
    assert (J - J1).applyfunc(sp.cancel) == sp.zeros(3, 3), f"order {k}: Jacobian differs from the first order's"
    r = sp.Matrix([e.subs({a_: 0, b_: 0, c_: 0}) for e in Ek])
    x = J.LUsolve(-r).applyfunc(lambda z: sp.expand(sp.cancel(z)))
    As.append(x[0]); Bs.append(x[1]); Cs.append(x[2])
    stamp(f"order {k} solved")
ORD = N
A, B, C = Ser(As), Ser(Bs), Ser(Cs)
E = equations(A, B, C)
out = {}
for k in range(1, N + 1):
    out[f"gw{k}"], out[f"g1{k}"], out[f"vev{k}"] = A.c[k], B.c[k], C.c[k]
# Everything derived from here on is written in the symbols gw_k, g1_k and vev_k, each of order t^k
PH = physics(Ser([0] + GWS), Ser([0] + G1S), Ser([0] + VEVS))
if SCHEME == "alpha":
    MW2s = PH['MW2']/MW2_of
    for k in range(1, N + 1):
        out[f"MW2{k}"] = MW2s.c[k]
else:
    aEWs = PH['e2']/aEW_of
    for k in range(1, N + 1):
        out[f"aEW{k}"] = aEWs.c[k]
stamp("input relations done")

# ---- the canonical rotation, rW, rh, the gluon (gen/derive_rotation.py's construction, to t^N) ----------
F = PH['F']
vv = PH['vv']
fW, fW3, fB, mm = F['fW'], F['fW3'], F['fB'], F['m']
zh = ser_of('zh', vv)
xG = ser_of('xG', vv)
dK = [[fW3, -mm], [-mm, fB]]
Kinvhalf = [[Ser([1]), Ser()], [Ser(), Ser([1])]]
P_ = [[Ser([1]), Ser()], [Ser(), Ser([1])]]
for n in range(1, N + 1):                      # (1 - dK)^{-1/2} = sum binom(2n, n)/4^n dK^n
    P_ = mmul(P_, dK)
    cn = sp.Rational(math.comb(2*n, n), 4**n)
    Kinvhalf = [[Kinvhalf[i][j] + P_[i][j]*cn for j in range(2)] for i in range(2)]
nvec = [PH['g'], -PH['gp']]
xv = mvec(Kinvhalf, nvec)
eta = (xv[0]*xv[0] + xv[1]*xv[1])/N02 - 1
inv_norm = (1 + eta)**sp.Rational(-1, 2)/sp.sqrt(N02)
z = [xv[0]*inv_norm, xv[1]*inv_norm]
av = [-z[1], z[0]]
S = mmul(Kinvhalf, [[z[0], av[0]], [z[1], av[1]]])
sw0, cw0 = gp0/sp.sqrt(N02), g0/sp.sqrt(N02)
R0 = [[Ser([cw0]), Ser([sw0])], [Ser([-sw0]), Ser([cw0])]]
T = mmul(mT(R0), S)
rW = (1 - fW)**sp.Rational(-1, 2)
rh = (1 + zh)**sp.Rational(-1, 2)
rG = (1 - xG)**sp.Rational(-1, 2)
sG = (1 - xG)**sp.Rational(1, 2)
for k in range(1, N + 1):
    out[f"TZZ{k}"], out[f"TZA{k}"], out[f"TAZ{k}"], out[f"TAA{k}"] = T[0][0].c[k], T[0][1].c[k], T[1][0].c[k], T[1][1].c[k]
    out[f"rW{k}"], out[f"rh{k}"] = rW.c[k], rh.c[k]
    out[f"xG{k}"], out[f"rG{k}"], out[f"sG{k}"] = xG.c[k], rG.c[k], sG.c[k]
stamp("rotation and gluon done")

# ---- the quartic and the Yukawas as series in the vev shifts -----------------------------------------------
vT = Ser([v0] + [v0*x for x in VEVS])
vT2 = vT*vT
Zh2 = 1 + ser_of('zh', vT2)
lamr = Zh2*v0**2/vT2 + ser_of('curv', vT2)*(v0**2/MH**2)
yrat = v0/vT
for k in range(1, N + 1):
    out[f"lamr{k}"], out[f"yr{k}"] = lamr.c[k], yrat.c[k]
YC = {}
for d in DIMS:
    kk = (d - 8)//2
    p = 2 + kk
    YC[d] = v0**(4 + 2*kk)*L[d]/2**(2 + kk)*((vT/v0)**(4 + 2*kk)).total(N - p)
    out[f"yc{d}"] = sp.expand(YC[d])
assert sp.simplify(lamr.c[0] - 1) == 0 and sp.simplify(yrat.c[0] - 1) == 0
stamp("quartic and Yukawas done")


# ---- y_e^2 - y_mu^2 out, through ylsq and ylprod ---------------------------------------------------------
def elim(e):
    e = sp.expand(e)
    if not e.has(yD):
        return e, True
    deg = sp.Poly(e, yD).degree() if e.is_polynomial(yD) else None
    assert deg is not None, "not polynomial in y_e^2 - y_mu^2"
    odd = all(sp.cancel(e.coeff(yD, n)) == 0 for n in range(1, deg + 1, 2))
    res = sum(e.coeff(yD, n)*(ylsq**2 - 4*ylprod)**(n//2) for n in range(0, deg + 1, 2))
    return sp.expand(res), odd


odd_ok = True
for k_ in list(out):
    out[k_], ok = elim(out[k_])
    odd_ok &= ok
print("=== the relations are even in y_e^2 - y_mu^2 (symmetric in e and mu):", "PASS" if odd_ok else "FAIL")

# ---- (1) through O(t^2), the three older scripts' formulae ----------------------------------------------
NAMES = {s.name: s for s in [t, g0, gp0, v0, MH, yf, ylsq, ylprod, yleta] + DIM6 + list(L.values()) + list(COEF.values()) + VEVS}
old_path = os.path.join(HERE, "input_scheme_formulae_mw.json" if SCHEME == "mw" else "input_scheme_formulae.json")
ok1, n1 = True, 0
if os.path.exists(old_path):
    old = json.load(open(old_path))
    print(f"=== (1) O(t) and O(t^2) against {os.path.basename(old_path)} ===")
    # the old file writes the quartic and the Yukawas in the vev shifts, as here, and the rest in the coefficients
    solved = {s: out[f"{k}{j}"] for k, S_ in (("gw", GWS), ("g1", G1S), ("vev", VEVS)) for j, s in enumerate(S_, 1)}
    for key, s_ in sorted(old.items()):
        if key not in out or not key[-1] in "12" or (key[-2:-1].isdigit() and key not in out):
            continue
        o = sp.sympify(s_.replace("^", "**"), locals=NAMES)
        new = out[key] if key.startswith(("lamr", "yr", "yc")) else sp.sympify(out[key]).xreplace(solved)
        dif = sp.cancel(sp.expand(new - o))
        n1 += 1
        if dif != 0:
            ok1 = False
            print(f"  {key}: DIFFERS by {str(dif)[:200]}")
    missing = [k_ for k_ in old if k_ not in out]
    if missing:
        ok1 = False
        print("  keys of the old file this script does not write:", missing)
    print(f"  (1) {n1} keys compared:", "PASS" if ok1 else "FAIL")
else:
    print(f"=== (1) skipped: no {old_path} ===")
    ok1 = False
stamp("(1) done")

# ---- (2) residuals of the exact relations at the truncated solution ---------------------------------------
mp.mp.dps = 50
rng = random.Random(20261108 + N)
Gfn, MZn, MWn = mp.mpf('1.16637e-5'), mp.mpf('91.1876'), mp.mpf('79.82435975')
v0n = 1/mp.sqrt(mp.sqrt(2)*Gfn)
g0n = 2*MWn/v0n
gp0n = g0n*mp.sqrt((1 - MWn**2/MZn**2)/(MWn**2/MZn**2))
L6n = mp.mpf('0.05')/v0n**2                   # every shift a few per cent at t = 1
Pn = {g0: g0n, gp0: gp0n, v0: v0n, MH: mp.mpf(125), yf: mp.mpf(1), L[6]: L6n}
for d in DIMS:
    Pn[L[d]] = L6n**ORDER[d]
for s in DIM6 + list(COEF.values()):
    Pn[s] = mp.mpf(rng.uniform(-1, 1))
# lepton Yukawas on, so that every weighted term is tested, the electron the lighter, so that x < 1 is a decay
ye2n, ym2n = mp.mpf('0.1'), mp.mpf('0.2')
Pn[ylsq], Pn[ylprod], Pn[yD] = ye2n + ym2n, ye2n*ym2n, ye2n - ym2n
xn = ye2n/ym2n
Pn[yleta] = ye2n*(1 + 9*xn - 9*xn**2 - xn**3 + 6*xn*(1 + xn)*mp.log(xn))/(1 - 8*xn + 8*xn**3 - xn**4 - 12*xn**2*mp.log(xn))
for j, s in enumerate(VEVS, start=1):
    Pn[s] = mp.mpf(rng.uniform(-1, 1))*mp.mpf('0.03')**j
SUB = {s: sp.Float(mp.nstr(val, 45), 45) for s, val in Pn.items()}


def numc(e):
    return mp.mpf(str(sp.N(sp.sympify(e).xreplace(SUB), 45)))


def numser(name_or_list):
    return [numc(x) for x in name_or_list]


An, Bn, Cn = numser(A.c), numser(B.c), numser(C.c)
# what is written in the symbols gw_k, g1_k and vev_k, at their solved values
SOLVEDN = {s: sp.Float(mp.nstr(x, 45), 45) for s, x in zip(GWS + G1S + VEVS, An[1:] + Bn[1:] + Cn[1:])}


def numsol(cs):
    return [numc(sp.sympify(x).xreplace(SOLVEDN)) for x in cs]


Tn = [[numsol(T[i][j].c) for j in range(2)] for i in range(2)]
rWn, rhn, rGn, sGn = numsol(rW.c), numsol(rh.c), numsol(rG.c), numsol(sG.c)
dern = numsol(aEWs.c if SCHEME == "mw" else MW2s.c)
lamn = [numc(out.get(f"lamr{k}", 1)) if k else mp.mpf(1) for k in range(N + 1)]
yrn = [numc(out[f"yr{k}"]) if k else mp.mpf(1) for k in range(N + 1)]
P1 = lambda cs, tt: sum(x*tt**i for i, x in enumerate(cs))


def residuals(tt):
    g, gp, v = g0n*(1 + P1(An[1:], tt)*0 + P1([0] + An[1:], tt)), gp0n*(1 + P1([0] + Bn[1:], tt)), v0n*(1 + P1([0] + Cn[1:], tt))
    v2 = v*v
    f = {k: num_of(k, v2, tt) for k in TABLE}
    K11, K12, K22 = 1 - f['fW3'], f['m'], 1 - f['fB']
    detK = K11*K22 - K12**2
    e2 = g**2*gp**2/(gp**2*K11 + 2*g*gp*K12 + g**2*K22)
    MZ2 = v2/4*(1 + f['dmZ'])*(g**2*K22 + 2*g*gp*K12 + gp**2*K11)/detK
    MW2 = g**2*v2/4*(1 + f['dmW'])/(1 - f['fW'])
    fmu = 1 + f['dlm'] + 1j*f['am']
    fe = 1 + f['dle'] + 1j*f['ae']
    amp = fmu*mp.conj(fe)/(1 + f['dmW']) + f['dc'] + 1j*f['dci']
    rate = mp.sqrt(abs(amp)**2 + 2*amp.real*f['ds']*Pn[yleta] + f['ds']**2*Pn[ylprod]/4)
    first = e2/(g0n**2*gp0n**2/(g0n**2 + gp0n**2)) - 1 if SCHEME == "alpha" else MW2/(g0n**2*v0n**2/4) - 1
    r_in = max(abs(first), abs(MZ2/((g0n**2 + gp0n**2)*v0n**2/4) - 1), abs(v2/v0n**2 - rate))
    # the derived alpha, or M_W^2, against the series written for it
    der = e2/(g0n**2*gp0n**2/(g0n**2 + gp0n**2)) if SCHEME == "mw" else MW2/(g0n**2*v0n**2/4)
    r_der = abs(der - P1(dern, tt))
    # rotation: S = R0 T must bring K to 1 and the neutral mass to diagonal form
    Tm = mp.matrix([[P1(Tn[i][j], tt) for j in range(2)] for i in range(2)])
    N0 = mp.sqrt(g0n**2 + gp0n**2)
    R0m = mp.matrix([[g0n/N0, gp0n/N0], [-gp0n/N0, g0n/N0]])
    Sm = R0m*Tm
    Km = mp.matrix([[K11, K12], [K12, K22]])
    can = Sm.T*Km*Sm - mp.eye(2)
    nv = mp.matrix([[g], [-gp]])
    sn = Sm.T*nv
    r_rot = max(max(abs(can[i, j]) for i in range(2) for j in range(2)), abs(sn[0]*sn[1]), abs(sn[1]))
    r_rw = abs(P1(rWn, tt)**2*(1 - f['fW']) - 1)
    r_rh = abs(P1(rhn, tt)**2*(1 + f['zh']) - 1)
    r_g = max(abs(P1(rGn, tt)**2*(1 - f['xG']) - 1), abs(P1(sGn, tt)**2 - (1 - f['xG'])))
    # the quartic and the Yukawa, with the vev shifts as free numbers of order t^j
    vT_ = v0n*(1 + sum(Pn[s]*tt**j for j, s in enumerate(VEVS, start=1)))
    lam_ex = (1 + num_of('zh', vT_**2, tt))*v0n**2/vT_**2 + num_of('curv', vT_**2, tt)*v0n**2/Pn[MH]**2
    sv = {s: sp.Float(mp.nstr(Pn[s]*tt**j, 45), 45) for j, s in enumerate(VEVS, start=1)}
    # lamr_k is of order t^k counting vev_j as t^j and a coefficient by its dimension, so its value at the
    # point scaled by t is tt^k times its value at the point
    r_lam = abs(lam_ex - P1(lamn, tt))
    y_ex = v0n/vT_
    y_se = 1 + sum(mp.mpf(str(sp.N(sp.sympify(out[f"yr{k}"]).xreplace({**SUB, **sv}), 45))) for k in range(1, N + 1))
    for d in DIMS:
        kk = (d - 8)//2
        cd = Pn[COEF[f"c{d}H8"]]                  # any coefficient stands for the class-12 one here
        y_ex += cd*tt**(2 + kk)*vT_**(4 + 2*kk)*Pn[L[d]]/2**(2 + kk)
        y_se += cd*tt**(2 + kk)*mp.mpf(str(sp.N(YC[d].xreplace({**SUB, **sv}), 45)))
    r_y = abs(y_ex - y_se)
    return dict(inputs=r_in, derived=r_der, rotation=r_rot, rW=r_rw, rh=r_rh, gluon=r_g, quartic=r_lam, yukawa=r_y)


print(f"=== (2) residuals of the exact relations at the O(t^{N}) solution, each should fall by 2^{N + 1} = {2**(N + 1)} per halving ===")
tts = [mp.mpf(1)/2**i for i in range(0, 6)]
rows = [residuals(tt) for tt in tts]
ok2 = True
for key in rows[0]:
    rs = [r[key] for r in rows]
    ratios = [rs[i]/rs[i + 1] if rs[i + 1] != 0 else mp.inf for i in range(len(rs) - 1)]
    good = ratios[-1] > 0.7*2**(N + 1) or rs[-1] < mp.mpf(10)**-40
    ok2 &= bool(good)
    print(f"  {key:9s} " + " ".join(mp.nstr(x, 3) for x in rs) + "   ratios " + " ".join(mp.nstr(x, 4) for x in ratios)
          + ("" if good else "   <- FAIL"))
print("  (2)", "PASS" if ok2 else "FAIL")
stamp("(2) done")

# ---- (3), (4) exact identities at rational points ---------------------------------------------------------
POINTS = [(sp.Rational(3, 5), sp.Rational(4, 5)), (sp.Rational(12, 13), sp.Rational(5, 13)), (sp.Rational(30, 17), sp.Rational(16, 17))]


def rpoint(i):
    r = random.Random(1000 + i)
    P = {g0: POINTS[i][0], gp0: POINTS[i][1], v0: sp.Rational(r.randint(2, 9), r.randint(2, 9)),
         MH: sp.Rational(r.randint(1, 9), 7), yf: sp.Rational(r.randint(1, 9), 5)}
    for s in DIM6 + list(COEF.values()) + VEVS + list(L.values()) + GWS + G1S:
        P[s] = sp.Rational(r.randint(-40, 40), r.randint(1, 13)) or sp.Rational(1, 3)
    ye, ym = sp.Rational(r.randint(1, 9), 11), sp.Rational(r.randint(1, 9), 13)
    P[ylsq], P[ylprod], P[yD] = ye + ym, ye*ym, ye - ym
    P[yleta] = sp.Rational(r.randint(1, 9), 17)
    return P


def zero_at_points(exprs):
    for i in range(len(POINTS)):
        P = rpoint(i)
        for e in exprs:
            val = sp.nsimplify(sp.sympify(e).xreplace(P)) if not isinstance(e, int) else e
            if val != 0:
                return False, val
    return True, 0


print("=== (3) T(0) = 1; S^T K S = 1, diagonal neutral mass and massless photon through t^N (exact, 3 rational points) ===")
T0 = [[sp.simplify(T[i][j].c[0]) for j in range(2)] for i in range(2)]
ok3a = T0 == [[1, 0], [0, 1]]
K = [[1 - fW3, mm], [mm, 1 - fB]]
can = mmul(mmul(mT(S), K), S)
sn = mvec(mT(S), nvec)
checks = [can[0][0] - 1, can[1][1] - 1, can[0][1], can[1][0], sn[0]*sn[1], sn[1]]
ok3b, bad = zero_at_points([x.c[k] for x in checks for k in range(N + 1)])
okE, badE = zero_at_points([e.c[k] for e in E for k in range(N + 1)])
print(f"  T(0) = 1: {ok3a};  canonical through t^{N}: {ok3b}{'' if ok3b else ' (' + str(bad) + ')'};"
      f"  the input equations vanish through t^{N}: {okE}")
ok3 = ok3a and ok3b and okE
print("  (3)", "PASS" if ok3 else "FAIL")

print("=== (4) MH and the fermion masses at their inputs through t^N (exact, 3 rational points) ===")
lam_ser = Ser([1] + [out[f"lamr{k}"] for k in range(1, N + 1)])*(MH**2/(2*v0**2))
mh2 = (2*lam_ser - ser_of('curv', vT2))*vT2/Zh2
ok4a, bad4a = zero_at_points([mh2.c[0] - MH**2] + mh2.c[1:])
yser = Ser([1] + [out[f"yr{k}"] for k in range(1, N + 1)])
for d in DIMS:
    kk = (d - 8)//2
    p = 2 + kk
    cyc = c('H8', d)/yf                        # a stand-in coefficient for the class-12 one, over y_f
    trunc = Ser(((vT/v0)**(4 + 2*kk)).c[:N - p + 1])
    yser = yser + (trunc*(v0**(4 + 2*kk)*L[d]/2**(2 + kk)) - vT**(4 + 2*kk)*(L[d]/2**(2 + kk))).shift(p)*cyc
mf = vT*yser/v0                                # m_f Sqrt2/(y_f vevSM)
ok4b, bad4b = zero_at_points([mf.c[0] - 1] + mf.c[1:])
print(f"  MH: {ok4a};  fermion masses: {ok4b}")
ok4 = ok4a and ok4b
print("  (4)", "PASS" if ok4 else "FAIL")
stamp("(3), (4) done")

# ---- write --------------------------------------------------------------------------------------------------
desc = {
    "N": N, "scheme": SCHEME,
    "gw{k}, g1{k}, vev{k}": "O(t^k) relative shifts: gw = gwSM (1 + gw1 + ... + gwN), likewise g1 and the vev; "
                            "every other key is written in these symbols and the coefficients",
    ("aEW{k}" if SCHEME == "mw" else "MW2{k}"): ("alpha = aEWSM (1 + aEW1 + ...), derived" if SCHEME == "mw"
                                                 else "MW^2 = MW2SM (1 + MW21 + ...), derived"),
    "TZZ{k}, TZA{k}, TAZ{k}, TAA{k}": "Z -> (1 + sum TZZ) Z + (sum TZA) A, A -> (sum TAZ) Z + (1 + sum TAA) A",
    "rW{k}, rh{k}": "W -> (1 + sum rW) W, h -> (1 + sum rh) h",
    "lamr{k}, yr{k}": "quartic lam (1 + sum lamr), Yukawa y_f (1 + sum yr), in the symbols vev1..vevN",
    "yc{d}": "class-12 compensation of dimension d: Y_f += yc{d} (structures of c{d}fH5), already in vev1..vevN",
    "xG{k}, rG{k}, sG{k}": "gluon: -(1/4)(1 - x) G G, G -> (1 + sum rG) G, g_s -> g_s (1 + sum sG), sG = 1/(1+rG) - 1",
    "symbols": "L{d} = 1/Lam^(d-4) for d >= 10; ylsq = y_e^2 + y_mu^2; ylprod = y_e^2 y_mu^2; yleta = y_e^2 g(x)/f(x), "
               "x = m_e^2/m_mu^2, the weight of the Michel eta term; c{d}<label> the tower "
               "coefficient of (H^dag H)^((d-8)/2) Q_<label>; c{d}l4H2x3Fx00/Fx0E the new four-lepton operator; "
               "c{d}l2e2H2x1Fx00/x2Fx00 the scalar coupling of muon decay",
}
dest = os.path.join(HERE, f"input_scheme_formulae_geo{N}_{SCHEME}.json")
written = {}
for k_, e in out.items():
    written[k_] = mc(sp.factor(e)) if k_[-1] == "1" and not k_.startswith("yc") else mc(e)
written["keys"] = desc
ok_all = odd_ok and ok1 and ok2 and ok3 and ok4
if ok_all:
    json.dump(written, open(dest, "w"), indent=1)
    print(f"wrote {os.path.relpath(dest, os.path.dirname(HERE))}: {len(out)} formulae")
else:
    print("a validation failed: nothing written")
stamp("done")
print("GEODONE" if ok_all else "GEOFAILED")
