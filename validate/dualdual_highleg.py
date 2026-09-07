#!/usr/bin/env python3
"""Exact decision of the 7- and 8-gluon vertices of the dual-dual G^4 operators
Q_{G^4}^{(2)} (L8op426), Q_{G^4}^{(4)} (L8op428), Q_{G^4}^{(8)} (L8op432).

Two independent routes, both exact over Q(sqrt 3):

(A) 8-gluon piece by structure.  With X^{ab} = eps^{mu nu ka la} G^a_{mu nu} G^b_{ka la} and
    G = G1 + G2 (G2^a_{mu nu} = f^{abc} A^b_mu A^c_nu), the eight-field piece of X^{ab} is
    f^{acd} f^{bef} P^{cdef} with P^{cdef} = eps^{mu nu ka la} A^c_mu A^d_nu A^e_ka A^f_la, which is
    totally antisymmetric in cdef, so only the 4-form W^{ab} = f^a ^ f^b enters.  P^{cdef} are the
    maximal minors of the 4x8 matrix A, which are linearly independent polynomials.  Each operator's
    eight-field piece is a sum of squares of real linear forms in P:
        426: (sum_a W^{aa} . P)^2          428: sum_{ab} (W^{ab} . P)^2
        432: sum_e (V^e . P)^2  with  V^e = sum_{ab} d^{abe} W^{ab}
    so it vanishes identically iff the corresponding 4-forms vanish.  Route A computes them.

(B) Plane waves.  A^a_mu = sum_i t_i c_i^a eps_{i mu} exp(-i p_i x), sum p_i = 0.  The coefficient of
    t_1...t_n in the n-field piece of the operator is the n-gluon vertex contracted with the c_i,
    eps_i at momenta p_i (up to the overall i and the (-i) per derivative, which are dropped).  It
    is extracted exactly by inclusion-exclusion over the 2^n subsets of waves.  A non-zero value at
    one rational point proves the vertex non-zero; zero at several random points makes it zero
    with overwhelming probability (Schwartz-Zippel), and for the cases that are zero route A or
    the Jacobi identity gives the proof.

Validation before use: the f and d tables are built from the Gell-Mann matrices and asserted
against their defining identities and the standard values; the plane-wave extraction is checked
on the Yang-Mills three- and four-gluon vertices against the multilinear coefficients derived by
hand from -1/4 G G (exact equality, two random points), and the Pontryagin four-field piece
sum_a X4^{aa} is asserted to vanish at every evaluation while X4^{11} does not.
Numbers are pairs (a, b) of Python integers or Fractions meaning a + b sqrt 3.
"""
import itertools, random, sys, time
from fractions import Fraction as Fr

# ---------- Q(sqrt 3) pair arithmetic -------------------------------------------------------
def qadd(x, y): return (x[0] + y[0], x[1] + y[1])
def qsub(x, y): return (x[0] - y[0], x[1] - y[1])
def qmul(x, y): return (x[0] * y[0] + 3 * x[1] * y[1], x[0] * y[1] + x[1] * y[0])
def qscale(x, s): return (x[0] * s, x[1] * s)
def qzero(x): return x[0] == 0 and x[1] == 0
Q0 = (0, 0)

# ---------- SU(3): exact f and d from the Gell-Mann matrices --------------------------------
# Complex numbers with entries in Q(sqrt3): represent as ((re_a, re_b), (im_a, im_b)).
def cadd(x, y): return (qadd(x[0], y[0]), qadd(x[1], y[1]))
def csub(x, y): return (qsub(x[0], y[0]), qsub(x[1], y[1]))
def cmul(x, y):
    re = qsub(qmul(x[0], y[0]), qmul(x[1], y[1]))
    im = qadd(qmul(x[0], y[1]), qmul(x[1], y[0]))
    return (re, im)
C0 = (Q0, Q0)
def cnum(re=Fr(0), im=Fr(0), re3=Fr(0), im3=Fr(0)): return ((Fr(re), Fr(re3)), (Fr(im), Fr(im3)))

def mat(rows): return [[cnum(*e) if isinstance(e, tuple) else cnum(e) for e in r] for r in rows]
def mmul(X, Y):
    return [[_sum(cmul(X[i][k], Y[k][j]) for k in range(3)) for j in range(3)] for i in range(3)]
def madd(X, Y): return [[cadd(X[i][j], Y[i][j]) for j in range(3)] for i in range(3)]
def msub(X, Y): return [[csub(X[i][j], Y[i][j]) for j in range(3)] for i in range(3)]
def mscale(X, c): return [[cmul(X[i][j], c) for j in range(3)] for i in range(3)]
def _sum(it):
    acc = C0
    for v in it: acc = cadd(acc, v)
    return acc
def tr(X): return _sum(X[i][i] for i in range(3))

s3inv = Fr(1, 3)  # 1/sqrt3 = sqrt3/3
lam = [
    mat([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
    mat([[0, (0, -1), 0], [(0, 1), 0, 0], [0, 0, 0]]),
    mat([[1, 0, 0], [0, -1, 0], [0, 0, 0]]),
    mat([[0, 0, 1], [0, 0, 0], [1, 0, 0]]),
    mat([[0, 0, (0, -1)], [0, 0, 0], [(0, 1), 0, 0]]),
    mat([[0, 0, 0], [0, 0, 1], [0, 1, 0]]),
    mat([[0, 0, 0], [0, 0, (0, -1)], [0, (0, 1), 0]]),
    [[cnum(0, 0, s3inv), C0, C0], [C0, cnum(0, 0, s3inv), C0], [C0, C0, cnum(0, 0, -2 * s3inv)]],
]
T = [mscale(l, cnum(Fr(1, 2))) for l in lam]
# f^{abc} = -2 i Tr([T^a,T^b] T^c),  d^{abc} = 2 Tr({T^a,T^b} T^c)
f = [[[Q0] * 8 for _ in range(8)] for _ in range(8)]
d = [[[Q0] * 8 for _ in range(8)] for _ in range(8)]
for a in range(8):
    for b in range(8):
        com = msub(mmul(T[a], T[b]), mmul(T[b], T[a]))
        acom = madd(mmul(T[a], T[b]), mmul(T[b], T[a]))
        for c in range(8):
            fc = cmul(cnum(0, -2), tr(mmul(com, T[c])))
            dc = cmul(cnum(2), tr(mmul(acom, T[c])))
            assert qzero(fc[1]) and qzero(dc[1]), "f or d not real"
            f[a][b][c] = fc[0]; d[a][b][c] = dc[0]
# identities (lesson: assert every hand-built tensor against its definitions)
half = (Fr(1, 2), Fr(0))
assert f[0][1][2] == (Fr(1), Fr(0)) and f[3][4][7] == (Fr(0), Fr(1, 2)) and f[0][3][6] == half and f[0][4][5] == (Fr(-1, 2), Fr(0))
assert d[0][0][7] == (Fr(0), Fr(1, 3)) and d[7][7][7] == (Fr(0), Fr(-1, 3)) and d[0][3][5] == half and d[3][3][7] == (Fr(0), Fr(-1, 6))
for a in range(8):
    for b in range(8):
        # [T^a, T^b] = i f^{abc} T^c ;  {T^a, T^b} = delta/3 + d^{abc} T^c
        com = msub(mmul(T[a], T[b]), mmul(T[b], T[a]))
        acom = madd(mmul(T[a], T[b]), mmul(T[b], T[a]))
        rhs1 = [[C0] * 3 for _ in range(3)]; rhs2 = [[C0] * 3 for _ in range(3)]
        for c in range(8):
            rhs1 = madd(rhs1, mscale(T[c], (Q0, f[a][b][c])))
            rhs2 = madd(rhs2, mscale(T[c], (d[a][b][c], Q0)))
        if a == b:
            for i in range(3): rhs2[i][i] = cadd(rhs2[i][i], cnum(Fr(1, 3)))
        assert all(com[i][j] == rhs1[i][j] for i in range(3) for j in range(3))
        assert all(acom[i][j] == rhs2[i][j] for i in range(3) for j in range(3))
        for c in range(8):
            assert f[a][b][c] == qscale(f[b][a][c], -1) == f[b][c][a] and d[a][b][c] == d[b][a][c] == d[b][c][a]
print("[su3] exact f and d tables pass [T,T]=ifT, {T,T}=delta/3+dT, f123=1, f458=sqrt3/2, d118=1/sqrt3")

# ---------- Route A: the colour 4-forms -----------------------------------------------------
quads = list(itertools.combinations(range(8), 4))
perms4 = [(p, _sign(p)) if False else p for p in itertools.permutations(range(4))]
def sign(p):
    s = 1
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            if p[i] > p[j]: s = -s
    return s
perm4 = [(p, sign(p)) for p in itertools.permutations(range(4))]

def wedge(a, b):
    """W^{ab}_I = sum_pi sgn(pi) f^{a I_pi1 I_pi2} f^{b I_pi3 I_pi4}  (f^a ^ f^b, unnormalised)."""
    W = {}
    for I in quads:
        acc = Q0
        for p, s in perm4:
            v = qmul(f[a][I[p[0]]][I[p[1]]], f[b][I[p[2]]][I[p[3]]])
            acc = qadd(acc, qscale(v, s))
        if not qzero(acc): W[I] = acc
    return W
W = [[wedge(a, b) for b in range(8)] for a in range(8)]
def formadd(F, G, s=(1, 0)):
    H = dict(F)
    for I, v in G.items():
        H[I] = qadd(H.get(I, Q0), qmul(v, s))
    return {I: v for I, v in H.items() if not qzero(v)}
J = {}
for a in range(8): J = formadd(J, W[a][a])
n428 = sum(1 for a in range(8) for b in range(8) if W[a][b])
V = []
for e in range(8):
    Ve = {}
    for a in range(8):
        for b in range(8):
            if W[a][b] and not qzero(d[a][b][e]): Ve = formadd(Ve, W[a][b], d[a][b][e])
    V.append(Ve)
print(f"[routeA] sum_a f^a^f^a (Pontryagin quartic, must vanish by Jacobi): {len(J)} non-zero components")
print(f"[routeA] f^a^f^b: {n428} of 64 pairs non-zero; f^1^f^1 has {len(W[0][0])} non-zero components -> 428 eight-gluon piece {'NON-ZERO' if n428 else 'zero'}")
print(f"[routeA] V^e = d^{{abe}} f^a^f^b: non-zero components per e = {[len(v) for v in V]} -> 432 eight-gluon piece {'NON-ZERO' if any(V) else 'zero'}")
assert len(J) == 0

# ---------- Route B: plane waves ---------------------------------------------------------------
eps4 = {p: sign(p) for p in itertools.permutations(range(4))}
eta = [1, -1, -1, -1]
fnz = [(a, b, c, f[a][b][c]) for a in range(8) for b in range(8) for c in range(8) if not qzero(f[a][b][c])]

def fields(waves, S):
    """A^a_mu and d_nu A^a_mu (derivative -> p_nu, the -i dropped) for the waves in S."""
    A = [[Q0] * 4 for _ in range(8)]
    dA = [[[Q0] * 4 for _ in range(8)] for _ in range(4)]   # dA[nu][a][mu]
    for i in S:
        c, e, p = waves[i]
        for a in range(8):
            if c[a] == 0: continue
            for mu in range(4):
                v = (c[a] * e[mu], 0)
                A[a][mu] = qadd(A[a][mu], v)
                for nu in range(4):
                    dA[nu][a][mu] = qadd(dA[nu][a][mu], qscale(v, p[nu]))
    G1 = [[[qsub(dA[mu][a][nu], dA[nu][a][mu]) for nu in range(4)] for mu in range(4)] for a in range(8)]
    G2 = [[[Q0] * 4 for _ in range(4)] for _ in range(8)]
    for a, b, c, fv in fnz:
        for mu in range(4):
            if qzero(A[b][mu]): continue
            for nu in range(4):
                if qzero(A[c][nu]): continue
                G2[a][mu][nu] = qadd(G2[a][mu][nu], qmul(fv, qmul(A[b][mu], A[c][nu])))
    return A, G1, G2

def XYpieces(G1, G2):
    """X_k^{ab} = eps^{mu nu ka la} (G^a_{mu nu} G^b_{ka la})_k and Y_k^{ab} = (G^a_{mu nu} G^{b mu nu})_k
    (metric contraction), k = 2 (G1 G1), 3 (G1 G2 + G2 G1), 4 (G2 G2) fields."""
    X = {k: [[Q0] * 8 for _ in range(8)] for k in (2, 3, 4)}
    Y = {k: [[Q0] * 8 for _ in range(8)] for k in (2, 3, 4)}
    for a in range(8):
        for b in range(8):
            x2 = x3 = x4 = Q0
            for (m, n, k, l), s in eps4.items():
                g1a, g2a, g1b, g2b = G1[a][m][n], G2[a][m][n], G1[b][k][l], G2[b][k][l]
                x2 = qadd(x2, qscale(qmul(g1a, g1b), s))
                x3 = qadd(x3, qscale(qadd(qmul(g1a, g2b), qmul(g2a, g1b)), s))
                x4 = qadd(x4, qscale(qmul(g2a, g2b), s))
            X[2][a][b], X[3][a][b], X[4][a][b] = x2, x3, x4
            y2 = y3 = y4 = Q0
            for m in range(4):
                for n in range(4):
                    s = eta[m] * eta[n]
                    g1a, g2a, g1b, g2b = G1[a][m][n], G2[a][m][n], G1[b][m][n], G2[b][m][n]
                    y2 = qadd(y2, qscale(qmul(g1a, g1b), s))
                    y3 = qadd(y3, qscale(qadd(qmul(g1a, g2b), qmul(g2a, g1b)), s))
                    y4 = qadd(y4, qscale(qmul(g2a, g2b), s))
            Y[2][a][b], Y[3][a][b], Y[4][a][b] = y2, y3, y4
    return X, Y

# The nine Q_{G^4} operators as bilinear forms A^{ab} B^{cd} with a colour structure, read off
# models/dev/dim8_generated.fr (block = 424 + k for Q_{G^4}^{(k)}):
#   (1) Y^{aa} Y^{bb}   (2) X^{aa} X^{bb}   (3) Y^{ab} Y^{ab}   (4) X^{ab} X^{ab}   (5) Y^{aa} X^{bb}
#   (6) Y^{ab} X^{ab}   (7) d d Y Y         (8) d d X X         (9) d d Y X
OPS = {425: ("Y", "Y", "tr"), 426: ("X", "X", "tr"), 427: ("Y", "Y", "pair"), 428: ("X", "X", "pair"),
       429: ("Y", "X", "tr"), 430: ("Y", "X", "pair"), 431: ("Y", "Y", "dd"), 432: ("X", "X", "dd"),
       433: ("Y", "X", "dd")}
CAPPED = {426, 428, 429, 430, 432, 433}

def colour_form(kind, A, B):
    acc = Q0
    if kind == "tr":
        ta = Q0; tb = Q0
        for a in range(8): ta = qadd(ta, A[a][a]); tb = qadd(tb, B[a][a])
        return qmul(ta, tb)
    if kind == "pair":
        for a in range(8):
            for b in range(8): acc = qadd(acc, qmul(A[a][b], B[a][b]))
        return acc
    for e in range(8):
        ya = Q0; yb = Q0
        for a in range(8):
            for b in range(8):
                dv = d[a][b][e]
                if qzero(dv): continue
                ya = qadd(ya, qmul(dv, A[a][b])); yb = qadd(yb, qmul(dv, B[a][b]))
        acc = qadd(acc, qmul(ya, yb))
    return acc

def op_piece(op, X, Y, n):
    """n-field piece of the operator (overall constants dropped)."""
    ta, tb, kind = OPS[op]
    TA = X if ta == "X" else Y; TB = X if tb == "X" else Y
    acc = Q0
    for k in (2, 3, 4):
        l = n - k
        if l not in (2, 3, 4): continue
        acc = qadd(acc, colour_form(kind, TA[k], TB[l]))
    return acc

def ym_piece(G1, G2, n):
    """n-field piece of -1/4 G^a_{mu nu} G^{a mu nu} (n = 3, 4), metric explicit."""
    acc = Q0
    for a in range(8):
        for mu in range(4):
            for nu in range(4):
                s = eta[mu] * eta[nu]
                if n == 3: v = qscale(qmul(G1[a][mu][nu], G2[a][mu][nu]), 2 * s)
                else: v = qscale(qmul(G2[a][mu][nu], G2[a][mu][nu]), s)
                acc = qadd(acc, v)
    return qscale(acc, Fr(-1, 4))

def multilinear(waves, n, evaluate):
    """coefficient of t_1...t_n of a homogeneous degree-n polynomial, by inclusion-exclusion."""
    acc = Q0
    for r in range(n + 1):
        for S in itertools.combinations(range(n), r):
            v = evaluate(S)
            acc = qadd(acc, qscale(v, (-1) ** (n - r)))
    return acc

def random_waves(n, rng, lo=-3, hi=3):
    waves = []
    for i in range(n):
        c = [rng.randint(lo, hi) for _ in range(8)]
        e = [rng.randint(lo, hi) for _ in range(4)]
        p = [rng.randint(lo, hi) for _ in range(4)]
        waves.append((c, e, p))
    # momentum conservation: last momentum balances the others
    last = [-sum(w[2][mu] for w in waves[:-1]) for mu in range(4)]
    waves[-1] = (waves[-1][0], waves[-1][1], last)
    return waves

def dot(x, y): return sum(eta[m] * x[m] * y[m] for m in range(4))

def ym3_byhand(waves):
    """multilinear coefficient of -f^{abc} (d_mu A^a_nu) A^{b mu} A^{c nu} on the three waves."""
    acc = Q0
    for i, j, k in itertools.permutations(range(3)):
        ci, ei, pi = waves[i]; cj, ej, _ = waves[j]; ck, ek, _ = waves[k]
        lor = dot(pi, ej) * dot(ei, ek)
        col = Q0
        for a, b, c, fv in fnz: col = qadd(col, qscale(fv, ci[a] * cj[b] * ck[c]))
        acc = qadd(acc, qscale(col, -lor))
    return acc

def ym3_textbook(waves):
    """f^{abc}[g_{mu nu}(p1-p2)_rho + g_{nu rho}(p2-p3)_mu + g_{rho mu}(p3-p1)_nu] c1 c2 c3 e1 e2 e3."""
    (c1, e1, p1), (c2, e2, p2), (c3, e3, p3) = waves
    lor = (dot(e1, e2) * dot([p1[m] - p2[m] for m in range(4)], e3)
           + dot(e2, e3) * dot([p2[m] - p3[m] for m in range(4)], e1)
           + dot(e3, e1) * dot([p3[m] - p1[m] for m in range(4)], e2))
    col = Q0
    for a, b, c, fv in fnz: col = qadd(col, qscale(fv, c1[a] * c2[b] * c3[c]))
    return qscale(col, lor)

def ym4_byhand(waves):
    """multilinear coefficient of -1/4 f^{abc} f^{ade} A^b_mu A^c_nu A^{d mu} A^{e nu}."""
    acc = Q0
    ff = [[[[Q0] * 8 for _ in range(8)] for _ in range(8)] for _ in range(8)]
    for a in range(8):
        for b in range(8):
            for c in range(8):
                if qzero(f[a][b][c]): continue
                for dd in range(8):
                    for e in range(8):
                        if qzero(f[a][dd][e]): continue
                        ff[b][c][dd][e] = qadd(ff[b][c][dd][e], qmul(f[a][b][c], f[a][dd][e]))
    for i, j, k, l in itertools.permutations(range(4)):
        ci, ei, _ = waves[i]; cj, ej, _ = waves[j]; ck, ek, _ = waves[k]; cl, el, _ = waves[l]
        lor = dot(ei, ek) * dot(ej, el)
        if lor == 0: continue
        col = Q0
        for b in range(8):
            if ci[b] == 0: continue
            for c in range(8):
                if cj[c] == 0: continue
                for dd in range(8):
                    if ck[dd] == 0: continue
                    for e in range(8):
                        if cl[e] == 0 or qzero(ff[b][c][dd][e]): continue
                        col = qadd(col, qscale(ff[b][c][dd][e], ci[b] * cj[c] * ck[dd] * cl[e]))
        acc = qadd(acc, qscale(col, lor))
    return qscale(acc, Fr(-1, 4))

def fmt(x):
    a, b = x
    return f"{a}" if b == 0 else (f"{b}*sqrt3" if a == 0 else f"{a} + {b}*sqrt3")

# ---- validation of route B on Yang-Mills -----------------------------------------------------
rng = random.Random(20260905)
for trial in range(2):
    w3 = random_waves(3, rng)
    cache = {}
    def ev3(S):
        A, G1, G2 = fields(w3, S); return ym_piece(G1, G2, 3)
    m3 = multilinear(w3, 3, ev3)
    h3 = ym3_byhand(w3); t3 = ym3_textbook(w3)
    print(f"[ym3] trial {trial}: plane-wave {fmt(m3)} | by hand {fmt(h3)} | textbook form {fmt(t3)}")
    assert m3 == h3 and not qzero(m3), "plane-wave extraction disagrees with the hand-derived 3-gluon coefficient"
    assert m3 == t3 or m3 == qscale(t3, -1), "3-gluon coefficient is not +-(textbook form)"
    w4 = random_waves(4, rng)
    def ev4(S):
        A, G1, G2 = fields(w4, S); return ym_piece(G1, G2, 4)
    m4 = multilinear(w4, 4, ev4)
    h4 = ym4_byhand(w4)
    print(f"[ym4] trial {trial}: plane-wave {fmt(m4)} | by hand {fmt(h4)}")
    assert m4 == h4 and not qzero(m4), "plane-wave extraction disagrees with the hand-derived 4-gluon coefficient"
print("[routeB] validated: 3- and 4-gluon Yang-Mills coefficients match the hand derivation exactly, non-zero, and the 3-gluon one is +-(textbook form)")

# ---- the nine G^4 operators --------------------------------------------------------------------
NPTS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
OPLIST = sorted(OPS)
results = {}
for n in range(4, 9):
    for trial in range(NPTS):
        waves = random_waves(n, rng)
        t0 = time.time()
        cache = {}
        def XYof(S):
            if S not in cache:
                A, G1, G2 = fields(waves, S)
                X, Y = XYpieces(G1, G2)
                tr4 = Q0
                for a in range(8): tr4 = qadd(tr4, X[4][a][a])
                assert qzero(tr4), "sum_a X4^{aa} is not zero: evaluator or f table wrong"
                cache[S] = (X, Y)
            return cache[S]
        line = []
        for op in OPLIST:
            m = multilinear(waves, n, lambda S, op=op: op_piece(op, *XYof(S), n))
            results.setdefault((op, n), []).append(m)
            line.append(f"{op}:{'0' if qzero(m) else 'NZ'}")
        print(f"[n={n}] point {trial} ({time.time()-t0:.1f}s) | " + " ".join(line))

print()
print("SUMMARY (n-gluon vertex of each Q_{G^4} block over the random points; NONZERO = proven, zero = at every point):")
for op in OPLIST:
    row = []
    for n in range(4, 9):
        vals = results[(op, n)]
        nz = sum(1 for v in vals if not qzero(v))
        row.append(f"{n}g:{'zero' if nz == 0 else 'NONZERO'}")
    print(f"  L8op{op} Q_G4^({op-424}) {'capped ' if op in CAPPED else 'full   '}: " + "  ".join(row))
print("Route A (exact structure of the 8-gluon piece): 426 zero (Jacobi), 428 %s, 432 %s; 429 zero (its X factor is the Pontryagin quartic)" % (
    "NON-ZERO" if n428 else "zero", "NON-ZERO" if any(V) else "zero"))
print("Consistency: the uncapped blocks 425, 427, 431 have 7- and 8-gluon vertices in the cache, so they must read NONZERO above.")
