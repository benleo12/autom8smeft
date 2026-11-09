"""The independent flavour structures of the dimension-eight operators, from their contact amplitudes.

    python3.11 validate/flavour_rank.py herm [--classes ...]
    python3.11 validate/flavour_rank.py check [--ng 1,2,3] [--classes 18,19] [--seed N]
    python3.11 validate/flavour_rank.py mfv [--classes ...] [--out build/mfv_structures.json] [--seed N]

check and mfv take the operators of the basis DIM8_BASIS (gen/basis.py), herm every operator of the
encoding.

Two flavour structures of a class are the same operator exactly when their contact amplitudes agree,
the amplitude with every field of the operator an external, massless, on-shell particle and momentum
conserved.  On shell, integration by parts and the equations of motion relate no two amplitudes that
differ, and explicit spinors carry every Fierz identity, so the number of independent operators is the
rank of the amplitudes over random kinematics, gauge and flavour wave functions.  The gauge fields enter
through the linear part of their field strengths, which is all a contact amplitude with the fewest
fields sees.

`check` tests the method against the counting of the Murphy basis: with n_g generations and general
flavour, the rank of each class must be the number of operators that the Hilbert series gives
(Murphy's Table 2, the column N_op), Q and Q^dag counted separately.

`mfv` finds the flavour structures of each operator under U(3)^5 with the Yukawa matrices as spurions:
every structure at the lowest order in them, every structure with two more Yukawa matrices, and those
with four more, all of them quark Yukawa matrices, that add something at the default card, where y_t and
y_b are the only nonzero Yukawa couplings.  A model coefficient is a number at the physical Yukawa matrices, so the
selection holds them fixed: one generic draw, and for the four-Yukawa structures values of y_t and y_b with
every other Yukawa coupling zero.  Each structure T Q enters through its Hermitian parts T Q + (T Q)^dag and
i (T Q - (T Q)^dag), one real parameter each, and a part is kept when it raises the rank, so the kept set
is independent.  The order of the candidates decides which of two equivalent structures is kept: the
structure the models carry now first, then the other structures of the lowest order, then two more
Yukawa matrices, then four, and within each the operators in the order of the catalogue.
"""
from __future__ import annotations

import argparse
import collections
import itertools
import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import basis  # noqa: E402
from operators import OPS  # noqa: E402
from dsl import FS, H, Gamma, Psi, Tensor  # noqa: E402
from emit_fr import mfv_structure  # noqa: E402

# ---------------------------------------------------------------------------------------------------
# numerical tensors.  Every Lorentz index is carried upper, and a contraction inserts the metric.
# ---------------------------------------------------------------------------------------------------

ETA = np.diag([1.0, -1.0, -1.0, -1.0]).astype(complex)
_PAULI = [np.array(m, complex) for m in ([[1, 0], [0, 1]], [[0, 1], [1, 0]], [[0, -1j], [1j, 0]], [[1, 0], [0, -1]])]
SIG = _PAULI                                     # sigma^mu = (1, sigma^i)
SIGB = [_PAULI[0]] + [-m for m in _PAULI[1:]]    # sigmabar^mu = (1, -sigma^i)
GAM = np.zeros((4, 4, 4), complex)               # gamma^mu, Weyl representation
for _mu in range(4):
    GAM[_mu][:2, 2:] = SIG[_mu]
    GAM[_mu][2:, :2] = SIGB[_mu]
G5 = 1j * GAM[0] @ GAM[1] @ GAM[2] @ GAM[3]
PROJ = {"L": (np.eye(4) - G5) / 2, "R": (np.eye(4) + G5) / 2}
GAGA = np.einsum("mab,nbc->mnac", GAM, GAM)
SIGMA = 0.5j * (GAGA - GAGA.transpose(1, 0, 2, 3))


def _levi(n):
    e = np.zeros((n,) * n)
    for perm in itertools.permutations(range(n)):
        inv = sum(1 for i in range(n) for j in range(i + 1, n) if perm[i] > perm[j])
        e[perm] = -1.0 if inv % 2 else 1.0
    return e


# eps_{0123} = +1, so with every index upper eps^{0123} = -1
EPS_UP = -_levi(4).astype(complex)
TAU = np.array(_PAULI[1:])                       # (tau^I)_j^k
EPS2 = np.array([[0, 1], [-1, 0]], complex)      # eps_{12} = +1
EPS3 = _levi(3).astype(complex)
_GM = np.zeros((8, 3, 3), complex)
for (_a, _i, _j), _v in {(0, 0, 1): 1, (0, 1, 0): 1, (1, 0, 1): -1j, (1, 1, 0): 1j, (2, 0, 0): 1, (2, 1, 1): -1,
                         (3, 0, 2): 1, (3, 2, 0): 1, (4, 0, 2): -1j, (4, 2, 0): 1j, (5, 1, 2): 1, (5, 2, 1): 1,
                         (6, 1, 2): -1j, (6, 2, 1): 1j}.items():
    _GM[_a, _i, _j] = _v
_GM[7] = np.diag([1, 1, -2]) / np.sqrt(3)
TSU3 = _GM / 2
FSU3 = np.real(-2j * np.einsum("aij,bjk,cki->abc", TSU3, TSU3, TSU3)
               + 2j * np.einsum("bij,ajk,cki->abc", TSU3, TSU3, TSU3)).astype(complex)
DSU3 = np.real(2 * np.einsum("aij,bjk,cki->abc", TSU3, TSU3, TSU3)
               + 2 * np.einsum("bij,ajk,cki->abc", TSU3, TSU3, TSU3)).astype(complex)

TENSORS = {"tau": TAU, "epsSU2": EPS2, "epsIJK": EPS3, "delSU2": np.eye(2, dtype=complex),
           "T": TSU3, "f": FSU3, "d": DSU3, "epsSU3": EPS3, "delSU3": np.eye(3, dtype=complex),
           "delA": np.eye(8, dtype=complex), "epsLor": EPS_UP, "g": ETA}
GAMMAS = {"ga": GAM, "sig": SIGMA, "gaga": GAGA}
ADJ = {"B": 0, "W": 3, "G": 8}
CHIR = {"l": "L", "q": "L", "e": "R", "u": "R", "d": "R"}
SU2 = {"l": True, "q": True, "e": False, "u": False, "d": False}
COL = {"l": False, "q": True, "e": False, "u": True, "d": True}


# ---------------------------------------------------------------------------------------------------
# external states
# ---------------------------------------------------------------------------------------------------

def _crandn(rng, *shape):
    return rng.normal(size=shape) + 1j * rng.normal(size=shape)


def momenta(n, rng):
    """n complex null momenta that sum to zero, p_i = lambda_i lambdatilde_i."""
    lam, lamt = _crandn(rng, n, 2), _crandn(rng, n, 2)
    K = sum(np.outer(lam[i], lamt[i]) for i in range(n - 2))
    X = -np.linalg.solve(np.stack([lam[n - 2], lam[n - 1]], axis=1), K)
    lamt[n - 2], lamt[n - 1] = X[0], X[1]
    out = []
    for i in range(n):
        P = np.outer(lam[i], lamt[i])
        out.append(np.array([0.5 * np.trace(SIGB[mu] @ P) for mu in range(4)]))
    return out


def _null(M):
    """The null vector of a matrix whose null space is one-dimensional."""
    _, s, vh = np.linalg.svd(M)
    assert s[-1] < 1e-8 * s[0] and (len(s) < 2 or s[-2] > 1e-6 * s[0]), s
    return vh[-1].conj()


def spinor(p, chir, bar):
    """u with pslash u = 0 and P_chir u = u, or for the barred field the row ubar with ubar pslash = 0
    and ubar P = ubar for the projector of the opposite chirality (psibar_L = psibar P_R)."""
    pslash = np.einsum("mab,m->ab", GAM, ETA @ p)
    if not bar:
        B = np.linalg.svd(PROJ[chir])[0][:, :2]
        return B @ _null(pslash @ B)
    B = np.linalg.svd(PROJ["R" if chir == "L" else "L"])[0][:, :2]
    return _null((B.T @ pslash).T) @ B.T


def leg_key(f):
    if isinstance(f, Psi):
        assert not f.cc, "baryon-number violating"
        return ("f", f.name, bool(f.bar))
    if isinstance(f, H):
        return ("H", bool(f.dag))
    if isinstance(f, FS):
        return ("X", f.group)
    return None


def wavefunctions(keys, ng, rng):
    """One random external state for each leg: momentum, spinor or polarisation, gauge and flavour vectors."""
    ps = momenta(len(keys), rng)
    wf = []
    for k, p in zip(keys, ps):
        w = {"p": p, "d": -1j * p}
        if k[0] == "f":
            w["sp"] = spinor(p, CHIR[k[1]], k[2])
            w["su2"] = _crandn(rng, 2) if SU2[k[1]] else None
            w["col"] = _crandn(rng, 3) if COL[k[1]] else None
            w["gen"] = _crandn(rng, ng)
        elif k[0] == "H":
            w["su2"] = _crandn(rng, 2)
        else:
            r, e0 = _crandn(rng, 4), _crandn(rng, 4)
            eps = e0 - (e0 @ ETA @ p) / (r @ ETA @ p) * r
            F = -1j * (np.outer(p, eps) - np.outer(eps, p))
            w["F"] = F
            w["Fdual"] = 0.5 * np.einsum("mnrs,rs->mn", EPS_UP, ETA @ F @ ETA)
            w["adj"] = _crandn(rng, ADJ[k[1]]) if ADJ[k[1]] else None
        wf.append(w)
    return wf


# ---------------------------------------------------------------------------------------------------
# one term, one assignment of its fields to the legs
# ---------------------------------------------------------------------------------------------------

class TermPlan:
    """The index bookkeeping of a term, fixed once: which factors are fields and of what kind, the
    einsum subscripts with the metric on every Lorentz contraction, and the open flavour indices."""

    def __init__(self, term, gens):
        self.coeff = complex(float(term.coeff.re), float(term.coeff.im))
        self.fields = []        # (factor position, leg key)
        self.parts = []         # (kind, factor, extra) in einsum order; names filled below
        names = []
        types = {n: t for n, (t, _) in term.indices().items()}
        for i, f in enumerate(term.factors):
            k = leg_key(f)
            if k is not None:
                self.fields.append((i, k))
            if isinstance(f, Psi):
                self.parts.append(("sp", i, [f.sp]))
                if f.su2 is not None:
                    self.parts.append(("su2", i, [f.su2]))
                if f.col is not None:
                    self.parts.append(("col", i, [f.col]))
                self.parts.append(("gen", i, [f.gen]))
                self.parts += [("d", i, [d]) for d in f.derivs]
            elif isinstance(f, H):
                self.parts.append(("su2", i, [f.j]))
                self.parts += [("d", i, [d]) for d in f.derivs]
            elif isinstance(f, FS):
                self.parts.append(("Fdual" if f.dual else "F", i, [f.mu, f.nu]))
                if f.adj is not None:
                    self.parts.append(("adj", i, [f.adj]))
                self.parts += [("d", i, [d]) for d in f.derivs]
            elif isinstance(f, Gamma):
                if f.kind == "1":
                    self.parts.append(("const", np.eye(4, dtype=complex), [f.sp1, f.sp2]))
                else:
                    self.parts.append(("const", GAMMAS[f.kind], list(f.lor) + [f.sp1, f.sp2]))
            elif isinstance(f, Tensor):
                self.parts.append(("const", TENSORS[f.kind], list(f.idx)))
            else:
                raise TypeError(type(f))
        # a Lorentz index used twice gets the metric between its two occurrences
        seen = collections.Counter()
        for part in self.parts:
            new = []
            for n in part[2]:
                if types.get(n) == "lor":
                    seen[n] += 1
                    new.append(n if seen[n] == 1 else n + "'")
                else:
                    new.append(n)
            part[2][:] = new
        for n, c in seen.items():
            assert c == 2, (n, c)
            self.parts.append(("const", ETA, [n, n + "'"]))
        letters = {}
        for part in self.parts:
            for n in part[2]:
                letters.setdefault(n, "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"[len(letters)])
        self.gens = list(gens)
        missing = [g for g in self.gens if g not in letters]
        assert not missing, missing
        self.subs = ",".join("".join(letters[n] for n in part[2]) for part in self.parts) \
            + "->" + "".join(letters[g] for g in self.gens)
        self.path = None

    def assignments(self, keys):
        """Every way to put the fields of the term on the legs, with the sign of the fermion permutation."""
        bytype = collections.defaultdict(list)
        for pos, k in self.fields:
            bytype[k].append(pos)
        legs = collections.defaultdict(list)
        for j, k in enumerate(keys):
            legs[k].append(j)
        assert {k: len(v) for k, v in bytype.items()} == {k: len(v) for k, v in legs.items()}, (bytype, legs)
        types = list(bytype)
        for choice in itertools.product(*(itertools.permutations(legs[k]) for k in types)):
            amap = {}
            for k, perm in zip(types, choice):
                amap.update(zip(bytype[k], perm))
            seq = [amap[pos] for pos, k in self.fields if k[0] == "f"]
            inv = sum(1 for i in range(len(seq)) for j in range(i + 1, len(seq)) if seq[i] > seq[j])
            yield amap, (-1.0 if inv % 2 else 1.0)

    def value(self, wf, amap):
        ops = []
        for kind, x, _ in self.parts:
            if kind == "const":
                ops.append(x)
            else:
                ops.append(wf[amap[x]][kind] if kind != "d" else wf[amap[x]]["d"])
        if self.path is None:
            self.path = np.einsum_path(self.subs, *ops, optimize="greedy")[0]
        return np.einsum(self.subs, *ops, optimize=self.path)


class OpPlan:
    """An operator, or its Hermitian conjugate, ready to evaluate: the amplitude as a tensor in its
    flavour indices, for one set of external states."""

    def __init__(self, op, conj=False):
        self.op, self.conj = op, conj
        terms = [t.hermitian_conjugate() for t in op.terms] if conj else list(op.terms)
        fermions = [f for f in terms[0].factors if isinstance(f, Psi)]
        self.gens = [f.gen for f in fermions]
        assert len(set(self.gens)) == len(self.gens), (op.name, self.gens)
        self.terms = [TermPlan(t, self.gens) for t in terms]
        # Term.hermitian_conjugate keeps the factor order, so read literally each bilinear has its two
        # fermion fields swapped: one sign per bilinear restores Q^dag
        self.sign = (-1.0) ** (len(fermions) // 2) if conj else 1.0
        self.keys = tuple(sorted(k for _, k in self.terms[0].fields))
        for t in self.terms[1:]:
            assert tuple(sorted(k for _, k in t.fields)) == self.keys, op.name
        self._assign = [list(t.assignments(self.keys)) for t in self.terms]

    def amplitude(self, wf, ng):
        """The amplitude, and the sum of the moduli of its contributions: an amplitude that cancels
        between the terms of the Wick sum is zero to rounding on the scale of the second."""
        out = np.zeros((ng,) * len(self.gens), complex)
        size = np.zeros((ng,) * len(self.gens))
        for t, assigns in zip(self.terms, self._assign):
            for amap, sign in assigns:
                v = t.coeff * t.value(wf, amap)
                out += sign * v
                size += np.abs(v)
        return self.sign * out, size


def exported(op):
    return not any(isinstance(f, Psi) and f.cc for f in op.terms[0].factors)


def plans(classes):
    """OpPlans grouped by external field content: every exported operator, and the conjugate of each
    operator with a complex coefficient (Q and Q^dag are counted separately)."""
    groups = collections.defaultdict(list)
    for op in basis.ops(OPS):
        if op.cls not in classes or not exported(op):
            continue
        for conj in ((False, True) if op.hc_mode == "complex" else (False,)):
            p = OpPlan(op, conj)
            groups[(op.cls, p.keys)].append(p)
    return groups


def rank(M, S, label=""):
    """Rank from the singular values, with the gap between the last kept and the first dropped.  The
    rows and the columns are scaled by the sizes S of the contributions to each entry, so that an entry
    that cancels to rounding stays small."""
    if M.shape[0] == 0:
        return 0, float("inf")
    M = M / np.maximum(np.linalg.norm(S, axis=1, keepdims=True), 1e-300)
    S = S / np.maximum(np.linalg.norm(S, axis=1, keepdims=True), 1e-300)
    M = M / np.maximum(np.linalg.norm(S, axis=0, keepdims=True), 1e-300)
    s = np.linalg.svd(M, compute_uv=False)
    if s[0] < 1e-10:
        return 0, float("inf")
    s = s / s[0]
    r = int(np.sum(s > 1e-8))
    gap = (s[r - 1] / s[r]) if 0 < r < len(s) else float("inf")
    if gap < 1e4:
        print(f"  WARNING {label}: no clean gap in the singular values, {s[max(r - 3, 0):r + 3]}", flush=True)
    return r, gap


# ---------------------------------------------------------------------------------------------------
# check: general flavour against the Hilbert series
# ---------------------------------------------------------------------------------------------------

def murphy_nop(cls, ng):
    """N_op of the baryon-number-conserving classes, Murphy's Table 2."""
    fixed = {1: 43, 2: 1, 3: 2, 4: 3, 5: 6, 6: 10, 7: 18, 8: 6}
    if cls in fixed:
        return fixed[cls]
    two = {9: 96, 10: 22, 11: 16, 12: 6, 13: 13, 14: 57, 15: 92, 16: 48, 17: 36}
    if cls in two:
        return two[cls] * ng ** 2
    return {18: ng ** 2 * (67 * ng ** 2 + ng + 7), 19: 4 * ng ** 2 * (40 * ng ** 2 - 1),
            20: ng ** 3 * (135 * ng - 1), 21: (11 * ng ** 2 * (9 * ng ** 2 + 1)) // 2}[cls]


def check(classes, ngs, seed):
    ok = True
    for ng in ngs:
        rng = np.random.default_rng(seed + ng)
        tot = collections.Counter()
        for (cls, keys), ps in sorted(plans(classes).items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
            nrow = sum(ng ** len(p.gens) for p in ps)
            ncfg = nrow + 40
            M = np.zeros((nrow, ncfg), complex)
            S = np.zeros((nrow, ncfg))
            for c in range(ncfg):
                wf = wavefunctions(keys, ng, rng)
                amps = [p.amplitude(wf, ng) for p in ps]
                M[:, c] = np.concatenate([a.ravel() for a, _ in amps])
                S[:, c] = np.concatenate([z.ravel() for _, z in amps])
            r, gap = rank(M, S, f"class {cls} {keys}")
            tot[cls] += r
        for cls in sorted(tot):
            want = murphy_nop(cls, ng)
            flag = "ok" if tot[cls] == want else "MISMATCH"
            ok &= tot[cls] == want
            print(f"n_g = {ng}  class {cls:>2}: rank {tot[cls]:>6}   Hilbert series {want:>6}   {flag}", flush=True)
    return ok


# ---------------------------------------------------------------------------------------------------
# mfv: the flavour structures under U(3)^5 with Yukawa spurions
# ---------------------------------------------------------------------------------------------------

def _chains():
    """For a bilinear from a barred field of one species to a field of another: the Yukawa matrices that
    join them at the lowest order, and with one insertion of Y Y^dag of each kind.  Each entry is
    (label, number of Yukawa matrices, function of (Yu, Yd, Ye))."""
    d = lambda m: m.conj().T  # noqa: E731
    I3 = np.eye(3, dtype=complex)
    return {
        ("q", "q"): [("", 0, lambda u, dd, e: I3), ("U", 2, lambda u, dd, e: u @ d(u)), ("D", 2, lambda u, dd, e: dd @ d(dd))],
        ("u", "u"): [("", 0, lambda u, dd, e: I3), ("U", 2, lambda u, dd, e: d(u) @ u)],
        ("d", "d"): [("", 0, lambda u, dd, e: I3), ("D", 2, lambda u, dd, e: d(dd) @ dd)],
        ("l", "l"): [("", 0, lambda u, dd, e: I3), ("E", 2, lambda u, dd, e: e @ d(e))],
        ("e", "e"): [("", 0, lambda u, dd, e: I3), ("E", 2, lambda u, dd, e: d(e) @ e)],
        ("q", "u"): [("", 1, lambda u, dd, e: u), ("U", 3, lambda u, dd, e: u @ d(u) @ u), ("D", 3, lambda u, dd, e: dd @ d(dd) @ u)],
        ("u", "q"): [("", 1, lambda u, dd, e: d(u)), ("U", 3, lambda u, dd, e: d(u) @ u @ d(u)), ("D", 3, lambda u, dd, e: d(u) @ dd @ d(dd))],
        ("q", "d"): [("", 1, lambda u, dd, e: dd), ("U", 3, lambda u, dd, e: u @ d(u) @ dd), ("D", 3, lambda u, dd, e: dd @ d(dd) @ dd)],
        ("d", "q"): [("", 1, lambda u, dd, e: d(dd)), ("U", 3, lambda u, dd, e: d(dd) @ u @ d(u)), ("D", 3, lambda u, dd, e: d(dd) @ dd @ d(dd))],
        ("l", "e"): [("", 1, lambda u, dd, e: e), ("E", 3, lambda u, dd, e: e @ d(e) @ e)],
        ("e", "l"): [("", 1, lambda u, dd, e: d(e)), ("E", 3, lambda u, dd, e: d(e) @ e @ d(e))],
        ("u", "d"): [("", 2, lambda u, dd, e: d(u) @ dd), ("U", 4, lambda u, dd, e: d(u) @ u @ d(u) @ dd), ("D", 4, lambda u, dd, e: d(u) @ dd @ d(dd) @ dd)],
        ("d", "u"): [("", 2, lambda u, dd, e: d(dd) @ u), ("U", 4, lambda u, dd, e: d(dd) @ u @ d(u) @ u), ("D", 4, lambda u, dd, e: d(dd) @ dd @ d(dd) @ u)],
    }


CHAINS = _chains()


def current(op):
    """The pairing of the structure the models carry now (gen/emit_fr.py), as a set of (barred flavour
    index, flavour index)."""
    bar = {f.gen: f.bar for f in op.terms[0].factors if isinstance(f, Psi)}
    deltas, spurions = mfv_structure(op)
    return frozenset([(a, b) if bar[a] else (b, a) for a, b in deltas] + [(a, b) for _, _, a, b in spurions])


def candidates(op):
    """The flavour structures of an operator: (tier, order, pairing, labels, species), where the pairing
    lists (barred flavour index, flavour index) for each bilinear, the labels the insertion on each and
    species the two fields of each.  order 0 is the lowest order, 2 two more Yukawa matrices, 4 four more,
    all of them quark Yukawa matrices.  The tier orders them for the selection: the structure the models carry now
    first, then the other structures of the lowest order, then order 2, then order 4."""
    fs = [f for f in op.terms[0].factors if isinstance(f, Psi)]
    bar = [(f.gen, f.name) for f in fs if f.bar]
    unb = [(f.gen, f.name) for f in fs if not f.bar]
    out = []
    for perm in itertools.permutations(range(len(unb))):
        pairs = [(bar[i], unb[j]) for i, j in enumerate(perm)]
        opts = [CHAINS.get((a[1], b[1])) for a, b in pairs]
        if any(o is None for o in opts):
            continue
        for combo in itertools.product(*opts):
            out.append((sum(c[1] for c in combo), tuple((a[0], b[0]) for a, b in pairs),
                        tuple(c[0] for c in combo), tuple((a[1], b[1]) for a, b in pairs)))
    if not out:
        return []
    m = min(c[0] for c in out)
    now = current(op)
    keep = []
    for cost, pairing, labels, species in out:
        order = cost - m
        if order in (0, 2) or (order == 4 and all(l in ("", "U", "D") for l in labels)):
            tier = {0: 1, 2: 2, 4: 3}[order]
            if order == 0 and frozenset(pairing) == now:
                tier = 0
            keep.append((tier, order, pairing, labels, species))
    assert sum(c[0] == 0 for c in keep) == 1, (op.name, now)
    keep.sort(key=lambda c: c[0])      # stable: within a tier the pairing as written first
    return keep


def structure_tensor(gens, pairing, labels, species, Y):
    """The flavour tensor of a structure in the flavour indices of the operator, in their order."""
    subs, ops = [], []
    letters = {g: "abcdefgh"[i] for i, g in enumerate(gens)}
    for (gb, gu), lab, sp in zip(pairing, labels, species):
        f = dict((l, fn) for l, _, fn in CHAINS[sp])[lab]
        ops.append(f(*Y))
        subs.append(letters[gb] + letters[gu])
    return np.einsum(",".join(subs) + "->" + "".join(letters[g] for g in gens), *ops)


def yukawas(rng, mode):
    """generic: random complex matrices.  top: only y_t.  default: y_t and y_b, the default card (every
    other fermion massless); with mixing among the first two generations only, the CKM matrix drops out.
    The values are generic, not physical, so that no rank depends on how small y_b is."""
    if mode == "generic":
        return tuple(_crandn(rng, 3, 3) / 2 for _ in range(3))
    P3 = np.diag([0, 0, 1]).astype(complex)
    yb = 0.37 if mode == "default" else 0
    return (0.94 * P3, yb * P3, np.zeros((3, 3), complex))


def mfv(classes, out, seed):
    rng = np.random.default_rng(seed)
    result = {}
    summary = collections.Counter()
    byop = collections.OrderedDict()
    for op in basis.ops(OPS):
        if op.cls in classes and exported(op) and any(isinstance(f, Psi) for f in op.terms[0].factors):
            byop[op.name] = op
    # the classes of field content that Q and Q^dag of each operator fall in, joined so that every
    # structure that can be related to another sits in one group
    content = {}
    for name, op in byop.items():
        content[name] = (OpPlan(op).keys, OpPlan(op, conj=True).keys)
    parent = {}

    def root(x):
        while parent.get(x, x) != x:
            x = parent[x]
        return x
    for a, b in content.values():
        ra, rb = root(a), root(b)
        if ra != rb:
            parent[rb] = ra
    groups = collections.defaultdict(list)
    for name, (a, b) in content.items():
        groups[(byop[name].cls, root(a))].append(name)
    for (cls, _), names in sorted(groups.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
        cands = []    # (tier, op name, structure)
        for name in names:
            for c in candidates(byop[name]):
                cands.append((c[0], name, c[1:]))
        cands.sort(key=lambda x: (x[0], names.index(x[1])))
        oplan = {n: (OpPlan(byop[n]), OpPlan(byop[n], conj=True)) for n in names}
        legsets = sorted({p.keys for pr in oplan.values() for p in pr}, key=str)

        def rows(Y, ncfg):
            """The amplitudes of each candidate (rows R) and of its conjugate (rows Rc) over ncfg random
            states, at the Yukawa matrices Y, with the sizes of their contributions (SR, SRc)."""
            shape = (len(cands), len(legsets), ncfg)
            R, Rc, SR, SRc = (np.zeros(shape, complex), np.zeros(shape, complex), np.zeros(shape), np.zeros(shape))
            tens = []
            for _, n, (order, pairing, labels, species) in cands:
                pq, pc = oplan[n]
                T = structure_tensor(pq.gens, pairing, labels, species, Y)
                Tc = structure_tensor(pc.gens, pairing, labels, species, Y).conj()
                tens.append((T, Tc))
            for c in range(ncfg):
                wfs = {ls: wavefunctions(ls, 3, rng) for ls in legsets}
                amp = {n: (pq.amplitude(wfs[pq.keys], 3), pc.amplitude(wfs[pc.keys], 3)) for n, (pq, pc) in oplan.items()}
                for i, (_, n, _) in enumerate(cands):
                    pq, pc = oplan[n]
                    (aq, zq), (ac, zc) = amp[n]
                    T, Tc = tens[i]
                    jq, jc = legsets.index(pq.keys), legsets.index(pc.keys)
                    R[i, jq, c], SR[i, jq, c] = np.sum(T * aq), np.sum(np.abs(T) * zq)
                    Rc[i, jc, c], SRc[i, jc, c] = np.sum(Tc * ac), np.sum(np.abs(Tc) * zc)
            return tuple(x.reshape(len(cands), -1) for x in (R, Rc, SR, SRc))

        def stack(rowsets, parts):
            """The Hermitian combinations T Q + (T Q)^dag (part "re") and i (T Q - (T Q)^dag) (part "im") of
            the listed candidates, as rows, with their sizes.  For Hermitian operators complex and real
            linear dependence coincide, so each part raises the rank by at most one real parameter."""
            R, Rc, SR, SRc = rowsets
            if not parts:
                return np.zeros((0, R.shape[1]), complex), np.zeros((0, R.shape[1]))
            M = np.vstack([R[i] + Rc[i] if part == "re" else 1j * (R[i] - Rc[i]) for i, part in parts])
            S = np.vstack([SR[i] + SRc[i] for i, part in parts])
            return M, S

        # The coefficients of a model are numbers at the physical Yukawa matrices, so two structures are
        # the same parameter when they are proportional at those matrices.  The selection therefore holds
        # the Yukawa matrices fixed: one generic draw, and for the structures with four more Yukawa
        # matrices values of y_t and y_b with every other Yukawa coupling zero.
        ncfg = 2 * len(cands) + 40
        gen_rows = rows(yukawas(rng, "generic"), ncfg)
        top_rows = rows(yukawas(rng, "top"), ncfg)
        def_rows = rows(yukawas(rng, "default"), ncfg)
        kept = []      # (candidate, part)
        for i, cand in enumerate(cands):
            if cand[0] == 3:
                continue
            for part in ("re", "im"):
                r, _ = rank(*stack(gen_rows, kept + [(i, part)]), f"class {cls} {cand[1]}")
                if r > len(kept):
                    kept.append((i, part))
            if cand[0] == 0 and not any(k == i for k, _ in kept):
                print(f"  NOTE class {cls} {cand[1]}: the structure the models carry now adds nothing", flush=True)
        now_top, _ = rank(*stack(top_rows, [(k, part) for k, part in kept if cands[k][0] == 0]), f"class {cls} now top")
        now_def, _ = rank(*stack(def_rows, [(k, part) for k, part in kept if cands[k][0] == 0]), f"class {cls} now default")
        # the structures with four more quark Yukawa matrices: kept where they add to the rank at the
        # default card, y_t and y_b nonzero, over the structures already kept
        rt0, _ = rank(*stack(def_rows, kept), f"class {cls} default")
        for i, cand in enumerate(cands):
            if cand[0] != 3:
                continue
            for part in ("re", "im"):
                r, _ = rank(*stack(def_rows, kept + [(i, part)]), f"class {cls} {cand[1]} default")
                if r > rt0:
                    # it must be independent at the generic Yukawa matrices too
                    rg, _ = rank(*stack(gen_rows, kept + [(i, part)]), f"class {cls} {cand[1]} generic")
                    assert rg > len(kept), cand
                    kept.append((i, part))
                    rt0 = r
        rdef = rt0
        rt0, _ = rank(*stack(top_rows, kept), f"class {cls} top")
        R, Rc = gen_rows[0], gen_rows[1]
        parts_of = collections.defaultdict(list)
        for i, part in kept:
            parts_of[i].append(part)
        for i in sorted(parts_of):
            tier, name, (order, pairing, labels, species) = cands[i]
            parts = parts_of[i]
            nreal = len(parts)
            # whether the structure is Hermitian by itself, (T Q)^dag = phase * T Q, and the phase
            own, _ = rank(*stack(gen_rows, [(i, "re"), (i, "im")]), f"class {cls} {name} pair")
            phase = None
            if own == 1:
                phase = complex(np.vdot(R[i], Rc[i]) / np.vdot(R[i], R[i]))
                assert abs(abs(phase) - 1) < 1e-6, phase
                phase = [round(phase.real, 9), round(phase.imag, 9)]
            if own != nreal:
                print(f"  NOTE class {cls} {name} {labels} {pairing}: keeps the part {parts} only, "
                      f"of a structure that is not Hermitian by itself", flush=True)
            result.setdefault(name, []).append(dict(order=order, now=tier == 0, pairing=[list(x) for x in pairing],
                                                   insertions=list(labels), species=[list(x) for x in species],
                                                   parts=parts, real_parameters=nreal, hermitian_phase=phase))
            key = "now" if tier == 0 else order
            summary[(cls, key, "structures")] += 1
            summary[(cls, key, "real")] += nreal
        summary[(cls, "top", "real")] += rt0
        summary[(cls, "nowtop", "real")] += now_top
        summary[(cls, "def", "real")] += rdef
        summary[(cls, "nowdef", "real")] += now_def
        print(f"class {cls:>2} group of {len(names):>3} operators: {len(cands):>4} candidates, kept "
              f"{len(parts_of):>4} structures, {len(kept):>4} real parameters, {rt0:>4} with only y_t nonzero "
              f"({now_top} from the structures the models carry now)", flush=True)
    print()
    for cls in sorted({k[0] for k in summary}):
        s = {o: (summary[(cls, o, 'structures')], summary[(cls, o, 'real')]) for o in ("now", 0, 2, 4)}
        print(f"class {cls:>2}: now {s['now'][0]:>3} ({s['now'][1]} real), other lowest order {s[0][0]:>3} ({s[0][1]}), "
              f"y^2 {s[2][0]:>4} ({s[2][1]}), y_t^4 {s[4][0]:>3} ({s[4][1]}); real parameters with only y_t nonzero "
              f"{summary[(cls, 'top', 'real')]} ({summary[(cls, 'nowtop', 'real')]} now); with y_t and y_b "
              f"{summary[(cls, 'def', 'real')]} ({summary[(cls, 'nowdef', 'real')]} now)")
    if out:
        # an existing file keeps the entries of the operators not computed here: those of other classes, and
        # those of the other basis (gen/basis.py), which both sit in build/mfv_structures.json
        old = json.load(open(out)) if os.path.exists(out) else {}
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        json.dump({**old, **result}, open(out + ".tmp", "w"), indent=1)
        os.replace(out + ".tmp", out)
        print(f"wrote {out}: {len(result)} operators computed, {len(set(old) - set(result))} kept from the file")


def herm(classes, seed):
    """One generation: the amplitude of every operator with a real coefficient must equal that of its
    conjugate, and of every operator with a complex one must not.  This tests the spinors, the Dirac
    matrices, the conjugation and the signs of the evaluator against the Hermiticity in the catalogue."""
    rng = np.random.default_rng(seed)
    bad = 0
    for op in OPS:
        if op.cls not in classes or not exported(op):
            continue
        pq, pc = OpPlan(op), OpPlan(op, conj=True)
        if pq.keys != pc.keys:
            assert op.hc_mode == "complex", op.name
            continue
        a, z = [], 0.0
        for _ in range(6):
            wf = wavefunctions(pq.keys, 1, rng)
            (aq, zq), (ac, zc) = pq.amplitude(wf, 1), pc.amplitude(wf, 1)
            a.append([aq.item(), ac.item()])
            z = max(z, zq.item(), zc.item())
        a = np.array(a)
        scale = np.abs(a).max()
        if scale < 1e-10 * z:
            print(f"  {op.name}: zero amplitude", flush=True)
            continue
        same = np.abs(a[:, 0] - a[:, 1]).max() / scale < 1e-9
        if same != (op.hc_mode != "complex"):
            bad += 1
            print(f"  MISMATCH {op.name} ({op.hc_mode}): Q^dag {'equals' if same else 'differs from'} Q, "
                  f"ratio {a[:, 1] / a[:, 0]}", flush=True)
    print(f"{bad} operators whose Hermiticity disagrees with the catalogue", flush=True)
    return bad == 0


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("mode", choices=["herm", "check", "mfv"])
    a.add_argument("--ng", default="1,2")
    a.add_argument("--classes", default=",".join(str(c) for c in range(1, 22)))
    a.add_argument("--out", default="")
    a.add_argument("--seed", type=int, default=20261105)
    args = a.parse_args(argv)
    classes = {int(c) for c in args.classes.split(",")}
    if args.mode == "herm":
        return 0 if herm(classes, args.seed) else 1
    if args.mode == "check":
        return 0 if check(classes, [int(n) for n in args.ng.split(",")], args.seed) else 1
    mfv(classes, args.out, args.seed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
