#!/usr/bin/env python3
"""Vertices of a UFO contracted completely, so that two models can be compared vertex by vertex.

    from vertex_contract import vertex_numbers, response, compare

A vertex is a sum over (colour, Lorentz) entries of coupling x colour structure x Lorentz
structure.  Here every index is contracted with an external state: colour indices with random
colour vectors, Lorentz indices with random polarisation vectors, spinor indices with random
spinors, momenta random and conserved.  The state is fixed by the particle (its PDG code and its
occurrence in the vertex) and the draw, so two models see the same state for the same particle,
and the vertex is summed over the orderings of identical particles, fermions with the sign of the
permutation.  The number obtained does not depend on how a model splits its vertex into Lorentz
structures, colour bases or Dirac projectors, which is where a comparison of coupling values goes
wrong.  validate/dim6_vs_smeftsim.py and validate/vs_matchete_ufo.py use it, on the derivatives of
the couplings that validate/index_vs_ufo.py read_model takes.
"""
import collections
import itertools
import math
import zlib

import numpy as np

# ------------------------------------------------------------------ numeric Lorentz and colour
G = np.diag([1.0, -1.0, -1.0, -1.0])
_I2, _Z2 = np.eye(2), np.zeros((2, 2))
_s = [np.array([[0, 1], [1, 0]], complex), np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]], complex)]
GAM = np.zeros((4, 4, 4), complex)
GAM[0] = np.block([[_I2, _Z2], [_Z2, -_I2]])
for _i, _m in enumerate(_s):
    GAM[_i + 1] = np.block([[_Z2, _m], [-_m, _Z2]])
G5 = 1j * GAM[0] @ GAM[1] @ GAM[2] @ GAM[3]
PM, PP = (np.eye(4) - G5) / 2, (np.eye(4) + G5) / 2
SIG = np.zeros((4, 4, 4, 4), complex)
for _a in range(4):
    for _b in range(4):
        SIG[_a, _b] = 0.5j * (GAM[_a] @ GAM[_b] - GAM[_b] @ GAM[_a])
EPS4 = np.zeros((4, 4, 4, 4))
for _p in itertools.permutations(range(4)):
    EPS4[_p] = np.linalg.det(np.eye(4)[list(_p)])
CCONJ = 1j * GAM[2] @ GAM[0]          # charge conjugation, in case a structure carries C
# SU(3): T^a = lambda^a / 2, f^{abc} = -2i tr([T^a, T^b] T^c), d^{abc} = 2 tr({T^a, T^b} T^c)
_lam = np.zeros((8, 3, 3), complex)
for _k, (_i, _j, _v) in enumerate([(0, 1, 1), (0, 1, -1j), (0, 0, 1), (0, 2, 1), (0, 2, -1j), (1, 2, 1), (1, 2, -1j)]):
    _lam[_k, _i, _j] = _v
    _lam[_k, _j, _i] = np.conj(_v)
_lam[2] = np.diag([1, -1, 0])
_lam[7] = np.diag([1, 1, -2]) / math.sqrt(3)
TGEN = _lam / 2
FABC = np.real(-2j * np.einsum("aij,bjk,cki->abc", TGEN, TGEN, TGEN)
               + 2j * np.einsum("bij,ajk,cki->abc", TGEN, TGEN, TGEN))
DABC = np.real(2 * np.einsum("aij,bjk,cki->abc", TGEN, TGEN, TGEN)
               + 2 * np.einsum("bij,ajk,cki->abc", TGEN, TGEN, TGEN))
EPS3 = np.zeros((3, 3, 3))
for _p in itertools.permutations(range(3)):
    EPS3[_p] = np.linalg.det(np.eye(3)[list(_p)])


class Ten:
    """A tensor over the summed (negative) indices of a structure, the leg indices already
    contracted with the external wavefunctions.  kinds: 'L' Lorentz (contracted with the metric),
    's' spinor, 'a' adjoint, 'f' fundamental."""

    def __init__(self, arr, labels=(), kinds=()):
        self.arr, self.labels, self.kinds = np.asarray(arr, complex), tuple(labels), tuple(kinds)

    def _lift(o):
        return o if isinstance(o, Ten) else Ten(complex(o))

    def __mul__(self, o):
        o = Ten._lift(o)
        return Ten(np.multiply.outer(self.arr, o.arr), self.labels + o.labels,
                   self.kinds + o.kinds)._self_contract()

    def _self_contract(self):
        """Contract repeated labels within one tensor (left after a product)."""
        la, ka, a = list(self.labels), list(self.kinds), self.arr
        while True:
            rep = [x for x in la if la.count(x) > 1]
            if not rep:
                return Ten(a, la, ka)
            lab = rep[0]
            i = la.index(lab)
            j = la.index(lab, i + 1)
            if ka[i] == "L":
                a = np.moveaxis(np.tensordot(G, a, axes=([1], [j])), 0, j)
            a = np.trace(a, axis1=i, axis2=j)
            for k in sorted((i, j), reverse=True):
                la.pop(k); ka.pop(k)

    __rmul__ = __mul__

    def _align(self, o):
        o = Ten._lift(o)
        if set(o.labels) != set(self.labels):
            if not o.labels:
                return o.arr
            raise ValueError(f"cannot add tensors over {self.labels} and {o.labels}")
        perm = [o.labels.index(x) for x in self.labels]
        return np.transpose(o.arr, perm)

    def __add__(self, o):
        return Ten(self.arr + self._align(o), self.labels, self.kinds)

    __radd__ = __add__

    def __sub__(self, o):
        return Ten(self.arr - self._align(o), self.labels, self.kinds)

    def __rsub__(self, o):
        return Ten(self._align(o) - self.arr, self.labels, self.kinds)

    def __neg__(self):
        return Ten(-self.arr, self.labels, self.kinds)

    def __truediv__(self, o):
        return Ten(self.arr / complex(o), self.labels, self.kinds)

    def __pow__(self, n):
        out = Ten(1.0)
        for _ in range(int(n)):
            out = out * self
        return out

    def value(self):
        if self.labels:
            raise ValueError(f"open indices {self.labels} left")
        return complex(self.arr)


class Ext:
    """The external state of one vertex: per leg (1-based) a polarisation vector, a spinor, a
    colour vector and a momentum."""

    def __init__(self, pol, spin, col, mom):
        self.pol, self.spin, self.col, self.mom = pol, spin, col, mom

    def _build(self, arr, args, kinds, leg_kind):
        """arr has one axis per argument; positive arguments are legs, contracted here."""
        labels, ks = [], []
        axis = 0
        for x, k in zip(args, kinds):
            if x > 0:
                w = {"L": lambda n: G @ self.pol[n], "s": lambda n: self.spin[n],
                     "a": lambda n: self.col[n], "f": lambda n: self.col[n]}[k](x)
                arr = np.tensordot(arr, w, axes=([axis], [0]))
            else:
                labels.append(x)
                ks.append(k)
                axis += 1
        return Ten(arr, labels, ks)

    def lorentz_ns(self):
        b = self._build
        return {
            "Metric": lambda i, j: b(G.astype(complex), (i, j), "LL", None),
            "P": lambda m, n: b(self.mom[n].astype(complex), (m,), "L", None),
            "Gamma": lambda m, i, j: b(GAM, (m, i, j), "Lss", None),
            "Gamma5": lambda i, j: b(G5, (i, j), "ss", None),
            "ProjM": lambda i, j: b(PM, (i, j), "ss", None),
            "ProjP": lambda i, j: b(PP, (i, j), "ss", None),
            "Identity": lambda i, j: b(np.eye(4, dtype=complex), (i, j), "ss", None),
            "Sigma": lambda m, n, i, j: b(SIG, (m, n, i, j), "LLss", None),
            "Epsilon": lambda a, c, d, e: b(EPS4.astype(complex), (a, c, d, e), "LLLL", None),
            "C": lambda i, j: b(CCONJ, (i, j), "ss", None),
            "complex": complex, "cmath": __import__("cmath"), "math": math,
        }

    def colour_ns(self, reps):
        b = self._build

        def ident(i, j):
            n = 8 if reps.get(i if i > 0 else j) == 8 else 3
            return b(np.eye(n, dtype=complex), (i, j), "aa" if n == 8 else "ff", None)
        return {
            "Identity": ident,
            "T": lambda a, i, j: b(TGEN, (a, i, j), "aff", None),
            "f": lambda a, c, d: b(FABC.astype(complex), (a, c, d), "aaa", None),
            "d": lambda a, c, d: b(DABC.astype(complex), (a, c, d), "aaa", None),
            "Epsilon": lambda i, j, k: b(EPS3.astype(complex), (i, j, k), "fff", None),
            "EpsilonBar": lambda i, j, k: b(EPS3.astype(complex), (i, j, k), "fff", None),
            "complex": complex,
        }


def evaluate(expr, namespace):
    if not expr.strip() or expr.strip() == "1":
        return 1.0 + 0j
    out = eval(expr, {"__builtins__": {}}, namespace)
    return out.value() if isinstance(out, Ten) else complex(out)


# ------------------------------------------------------------------ external states
SPIN = {}   # pdg -> spin (1 scalar, 2 fermion, 3 vector), from the PDG code
COLOUR = {}  # pdg -> colour representation (1, 3, -3, 8)


def spin_of(pdg):
    a = abs(pdg)
    return 2 if a <= 18 else (3 if a in (21, 22, 23, 24) else 1)


def colour_of(pdg):
    a = abs(pdg)
    return 8 if a == 21 else (3 if a <= 6 else 1)


def rng_for(*key):
    return np.random.default_rng(zlib.crc32(repr(key).encode()))


def wavefunctions(pdgs_sorted, draw):
    """Per sorted position: polarisation, spinor and colour vector, fixed by the particle and its
    occurrence; momenta fixed by the whole vertex and conserved."""
    pol, spin, col = [], [], []
    seen = collections.Counter()
    for p in pdgs_sorted:
        occ = seen[p]
        seen[p] += 1
        r = rng_for("wf", p, occ, draw)
        pol.append(r.normal(size=4) + 1j * r.normal(size=4))
        spin.append(r.normal(size=4) + 1j * r.normal(size=4))
        col.append(r.normal(size=8 if colour_of(p) == 8 else 3) + 1j * r.normal(size=8 if colour_of(p) == 8 else 3))
    r = rng_for("mom", tuple(pdgs_sorted), draw)
    mom = [r.normal(size=4) for _ in pdgs_sorted[:-1]]
    mom.append(-sum(mom))
    return pol, spin, col, mom


def vertex_numbers(entries, need, draws=2, maxlegs=None):
    """{entry id: [number per draw]}: the colour x Lorentz contraction of every (vertex, entry)
    whose coupling is in `need`, with the external state assigned by sorted PDG position and summed
    over the orderings of identical particles (fermions with the sign of the permutation)."""
    out = {}
    for vi, (names, pdgs, ents) in enumerate(entries):
        if not any(g in need for _, _, g in ents):
            continue
        if maxlegs is not None and len(pdgs) > maxlegs:
            continue                 # beyond the other model's vertices: not contracted, not compared
        order = sorted(range(len(pdgs)), key=lambda i: pdgs[i])           # sorted position -> UFO leg
        srt = [pdgs[i] for i in order]
        groups = [[k for k, p in enumerate(srt) if p == q] for q in dict.fromkeys(srt)]
        perms = []
        for combo in itertools.product(*[itertools.permutations(g) for g in groups]):
            perm, sign = list(range(len(srt))), 1
            for g, pg in zip(groups, combo):
                for a, b in zip(g, pg):
                    perm[a] = b
                if spin_of(srt[g[0]]) == 2:
                    inv = sum(1 for i in range(len(pg)) for j in range(i + 1, len(pg)) if pg[i] > pg[j])
                    sign *= -1 if inv % 2 else 1
            perms.append((perm, sign))
        reps = {}
        for d in range(draws):
            pol, spn, col, mom = wavefunctions(srt, d)
            for ei, (colour, struct, g) in enumerate(ents):
                if g not in need:
                    continue
                tot = 0j
                for perm, sign in perms:
                    # UFO leg order[k] (0-based) carries the state of sorted position perm[k]
                    leg = {order[k] + 1: perm[k] for k in range(len(srt))}
                    ext = Ext({n: pol[s] for n, s in leg.items()}, {n: spn[s] for n, s in leg.items()},
                              {n: col[s] for n, s in leg.items()}, {n: mom[s] for n, s in leg.items()})
                    reps = {n: colour_of(pdgs[n - 1]) for n in leg}
                    c = evaluate(colour, ext.colour_ns(reps))
                    if c == 0:
                        continue
                    tot += sign * c * evaluate(struct, ext.lorentz_ns())
                out.setdefault((vi, ei), []).append(tot)
    return out


def response(r, nums, spellings, sign=1.0, maxlegs=None):
    """{sorted PDG key: [derivative of the contracted vertex per draw]}, summed over the
    (coefficient, direction) spellings of one direction (several when a model writes a complex
    coefficient both as the combination and as its parts: the chain rule)"""
    out = collections.defaultdict(lambda: np.zeros(2, complex))
    for vi, (names, pdgs, ents) in enumerate(r["entries"]):
        if maxlegs is not None and len(pdgs) > maxlegs:
            continue
        key = tuple(sorted(pdgs))
        for ei, (colour, struct, g) in enumerate(ents):
            d = sum(r["resp"].get((g, c, v), 0j) for c, v in spellings)
            if d:
                out[key] += sign * d * np.array(nums[(vi, ei)])
    return out


def moved_beyond(r, spellings, maxlegs):
    """The vertex keys with more than maxlegs legs that a direction moves, without contracting them"""
    keys = set()
    for names, pdgs, ents in r["entries"]:
        if len(pdgs) > maxlegs and any(r["resp"].get((g, c, v), 0j) for _, _, g in ents for c, v in spellings):
            keys.add(tuple(sorted(pdgs)))
    return keys


def compare(A, B, tol, ratio=False):
    """Counter of outcomes and the rows that are not agreements, for two responses.  A derivative
    counts as vanishing below 1e-9 of the largest of the direction.  With ratio=True a constant
    ratio B/A over every vertex is reported instead of a disagreement, for two models whose
    operators may differ by a normalisation."""
    big = max([np.max(np.abs(x)) for x in list(A.values()) + list(B.values())] + [0.0])
    floor = 1e-9 * big
    cnt, rows, ratios = collections.Counter(), [], []
    for key in sorted(set(A) | set(B)):
        a, b = A.get(key, np.zeros(2)), B.get(key, np.zeros(2))
        sa, sb = np.max(np.abs(a)), np.max(np.abs(b))
        if sa <= floor and sb <= floor:
            continue
        if sb <= floor:
            cnt["only first"] += 1
            rows.append((key, "only first", sa, sb, None))
        elif sa <= floor:
            cnt["only second"] += 1
            rows.append((key, "only second", sa, sb, None))
        elif np.max(np.abs(a - b)) <= tol * max(sa, sb):
            cnt["agree"] += 1
        else:
            q = b / a
            ratios.append(np.mean(q))
            cnt["differ"] += 1
            rows.append((key, "differ", sa, sb, np.mean(q)))
    if ratio and ratios and cnt["only first"] + cnt["only second"] == 0:
        r0 = ratios[0]
        if all(abs(q - r0) <= tol * max(abs(r0), 1e-300) for q in ratios) and cnt["agree"] == 0:
            cnt = collections.Counter({"agree up to a factor": cnt["differ"]})
            rows = [(None, f"factor {r0:.6g}", 0.0, 0.0, r0)]
    return cnt, rows
