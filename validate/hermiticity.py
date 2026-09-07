"""
validate/hermiticity.py  --  V5, DSL half.

Decide, from the symbolic term algebra alone and before any Mathematica is involved,
whether each parsed operator is Hermitian, anti-Hermitian, or neither.  The published
tables do not say: Murphy marks "+ h.c." on the rows whose Wilson coefficient is complex,
but a row can still be anti-Hermitian *as typeset* because his Hermitian derivative

    i H^dag Dlr_mu H = i H^dag (D_mu H) - i (D_mu H^dag) H          (conventions_v2.tex:87)

carries the factor i outside the Dlr symbol, and many table rows write the bare
Dlr without a leading i.  Those rows need the i restored before they are Hermitian.
This module finds them automatically instead of trusting the typesetting.

Method
------
Two terms are "the same structure" when there is a bijection of their index names,
type-preserving and factor-preserving, that maps one onto the other.  The bijection is
built by backtracking over the factors; index-symmetric factors (epsilon tensors,
f^{ABC}, d^{ABC}, X_{mu nu}, sigma^{mu nu}, metric, deltas) may be matched under any
permutation of their slots, and the signature of that permutation is accumulated into a
relative sign.  So each match returns a sign sigma with

    structure(A)  ==  sigma * structure(B).

Then Q^dagger is compared term by term with Q under a bipartite matching:

    Q^dagger == +Q   ->  "hermitian"      real Wilson coefficient
    Q^dagger == -Q   ->  "antihermitian"  multiply Q by i, then real coefficient
    neither          ->  "complex"        complex coefficient, Lagrangian needs + h.c.

For flavour-general operators the bijection also maps the generation labels; the
permutation it needs is reported, since Q_{pr}^dagger = Q_{rp} is exactly the statement
that the Wilson coefficient matrix is Hermitian.

Public entry points
-------------------
match_terms(a, b)      -> sign (+1/-1) or None
classify(op)           -> Verdict(kind, gen_perm, detail)
apply_i_convention(op) -> the same operator, made Hermitian (mutates coefficients)
"""

from __future__ import annotations

import itertools
import os
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gen"))

from dsl import C, FS, Gamma, H, I, Operator, Psi, Tensor, Term  # noqa: E402


# --------------------------------------------------------------------------------------
# factor shapes: a tag that must match exactly, an index list, and the allowed
# slot permutations of that list with their signs
# --------------------------------------------------------------------------------------

Perm = Tuple[Tuple[int, ...], int]  # (permutation of slot positions, sign)


def _signed_perms(n: int, sign: int) -> List[Perm]:
    """All n! permutations; sign=-1 means totally antisymmetric (carry the signature),
    sign=+1 means totally symmetric (signature ignored)."""
    out = []
    for p in itertools.permutations(range(n)):
        s = _signature(p) if sign == -1 else 1
        out.append((p, s))
    return out


def _signature(p: Tuple[int, ...]) -> int:
    s = 1
    p = list(p)
    for i in range(len(p)):
        while p[i] != i:
            j = p[i]
            p[i], p[j] = p[j], p[i]
            s = -s
    return s


_IDENT: List[Perm] = [((0,), 1)]


def factor_shape(f) -> Tuple[tuple, List[str], List[Perm]]:
    """(tag, index names in slot order, allowed slot permutations with signs)."""
    if isinstance(f, FS):
        idx = [f.mu, f.nu] + ([f.adj] if f.adj is not None else []) + list(f.derivs)
        tag = ("FS", f.group, f.dual, len(f.derivs))
        # X_{mu nu} = -X_{nu mu}; the adjoint slot and the derivatives stay put
        n = len(idx)
        ident = tuple(range(n))
        swap = (1, 0) + ident[2:]
        return tag, idx, [(ident, 1), (swap, -1)]
    if isinstance(f, H):
        return ("H", f.dag, len(f.derivs)), [f.j] + list(f.derivs), [(tuple(range(1 + len(f.derivs))), 1)]
    if isinstance(f, Psi):
        idx = [f.sp]
        if f.su2 is not None:
            idx.append(f.su2)
        if f.col is not None:
            idx.append(f.col)
        idx.append(f.gen)
        idx += list(f.derivs)
        tag = ("Psi", f.name, f.bar, f.su2 is not None, f.col is not None, len(f.derivs))
        return tag, idx, [(tuple(range(len(idx))), 1)]
    if isinstance(f, Gamma):
        idx = list(f.lor) + [f.sp1, f.sp2]
        n = len(idx)
        ident = tuple(range(n))
        if f.kind == "sig":  # sigma^{mu nu} = -sigma^{nu mu}
            return ("Ga", "sig"), idx, [(ident, 1), ((1, 0, 2, 3), -1)]
        return ("Ga", f.kind), idx, [(ident, 1)]
    if isinstance(f, Tensor):
        k, idx = f.kind, list(f.idx)
        n = len(idx)
        if k in ("epsSU2",):
            return ("Tn", k), idx, [((0, 1), 1), ((1, 0), -1)]
        if k in ("epsIJK", "epsSU3", "f"):
            return ("Tn", k), idx, _signed_perms(3, -1)
        if k == "epsLor":
            return ("Tn", k), idx, _signed_perms(4, -1)
        if k == "d":
            return ("Tn", k), idx, _signed_perms(3, +1)
        if k in ("delSU2", "delSU3", "delA", "g"):
            return ("Tn", k), idx, [((0, 1), 1), ((1, 0), 1)]
        # tau^I_j{}^k and (T^A)_alpha{}^beta are Hermitian, not symmetric: no slot swap
        return ("Tn", k), idx, [(tuple(range(n)), 1)]
    raise TypeError(f"no shape for {type(f).__name__}")


# --------------------------------------------------------------------------------------
# structural matching
# --------------------------------------------------------------------------------------


def match_terms(a: Term, b: Term) -> Optional[int]:
    """Relative sign sigma with structure(a) == sigma * structure(b), or None if the two
    terms are not the same structure.  Coefficients are ignored."""
    for sigma, _ in _matches(a, b, first_only=True):
        return sigma
    return None


def match_terms_with_map(a: Term, b: Term) -> Optional[Tuple[int, Dict[str, str]]]:
    for sigma, mp in _matches(a, b, first_only=True):
        return sigma, mp
    return None


def _matches(a: Term, b: Term, first_only: bool = True):
    sa = [factor_shape(f) for f in a.factors]
    sb = [factor_shape(f) for f in b.factors]
    if len(sa) != len(sb):
        return
    if sorted(t for t, _, _ in sa) != sorted(t for t, _, _ in sb):
        return
    # order A's factors so that the most constrained (rarest tag) come first: prunes hard
    tag_count: Dict[tuple, int] = {}
    for t, _, _ in sb:
        tag_count[t] = tag_count.get(t, 0) + 1
    order = sorted(range(len(sa)), key=lambda i: (tag_count.get(sa[i][0], 0), -len(sa[i][1])))

    used = [False] * len(sb)
    fwd: Dict[str, str] = {}
    rev: Dict[str, str] = {}
    results = []

    def rec(k: int, sign: int):
        if k == len(order):
            results.append((sign, dict(fwd)))
            return True
        ia = order[k]
        tag_a, idx_a, _ = sa[ia]
        for ib in range(len(sb)):
            if used[ib]:
                continue
            tag_b, idx_b, perms_b = sb[ib]
            if tag_b != tag_a:
                continue
            for perm, psign in perms_b:
                added: List[str] = []
                ok = True
                for slot, ja in enumerate(idx_a):
                    jb = idx_b[perm[slot]]
                    if ja in fwd:
                        if fwd[ja] != jb:
                            ok = False
                            break
                    elif jb in rev:
                        ok = False
                        break
                    else:
                        fwd[ja] = jb
                        rev[jb] = ja
                        added.append(ja)
                if ok:
                    used[ib] = True
                    if rec(k + 1, sign * psign) and first_only:
                        for ja in added:
                            del rev[fwd[ja]]
                            del fwd[ja]
                        used[ib] = False
                        return True
                    used[ib] = False
                for ja in added:
                    del rev[fwd[ja]]
                    del fwd[ja]
        return False

    rec(0, 1)
    for r in results:
        yield r


# --------------------------------------------------------------------------------------
# operator classification
# --------------------------------------------------------------------------------------


@dataclass
class Verdict:
    kind: str  # "hermitian" | "antihermitian" | "complex"
    gen_perm: Optional[Dict[str, str]]  # how the flavour labels map, e.g. {"p": "r", "r": "p"}
    detail: str = ""


def classify(op: Operator) -> Verdict:
    """Compare Q^dagger with Q term by term."""
    if any(isinstance(f, Psi) and f.cc for t in op.terms for f in t.factors):
        # a (psi C chi) bilinear changes baryon number: Q^dagger is a different operator
        return Verdict("complex", None, "charge-conjugated bilinear (B-violating), never Hermitian")
    conj = [t.hermitian_conjugate() for t in op.terms]
    orig = list(op.terms)
    n = len(orig)
    gen_names = set(op.gens)

    # bipartite matching conj[i] <-> orig[j]; n is 1..4 in practice, brute force is fine
    for perm in itertools.permutations(range(n)):
        signs: List[int] = []
        ratios: List[C] = []
        gmap: Dict[str, str] = {}
        good = True
        for i, j in enumerate(perm):
            m = match_terms_with_map(conj[i], orig[j])
            if m is None:
                good = False
                break
            sigma, mp = m
            g = {k: v for k, v in mp.items() if k in gen_names}
            if any(gmap.get(k, v) != v for k, v in g.items()):
                good = False
                break
            gmap.update(g)
            signs.append(sigma)
            # conj[i] == coeff(conj[i]) * structure(conj[i]) == coeff * sigma * structure(orig[j])
            ratios.append(C(conj[i].coeff.re, conj[i].coeff.im) * C(sigma) )
        if not good:
            continue
        # Q^dagger = lambda * Q requires coeff_conj_i * sigma_i == lambda * coeff_orig_perm(i)
        lams = []
        for i, j in enumerate(perm):
            co, cj = orig[j].coeff, ratios[i]
            if co.is_zero():
                continue
            lam = _div(cj, co)
            if lam is None:
                lams = None
                break
            lams.append(lam)
        if lams is None or not lams:
            continue
        if any(l != lams[0] for l in lams[1:]):
            continue
        lam = lams[0]
        if lam == C(1):
            return Verdict("hermitian", gmap or None)
        if lam == C(-1):
            return Verdict("antihermitian", gmap or None)
        return Verdict("complex", gmap or None, f"Q^dagger = ({lam.fr()}) Q")
    return Verdict("complex", None, "no term-by-term match between Q^dagger and Q")


def _div(a: C, b: C) -> Optional[C]:
    d = b.re * b.re + b.im * b.im
    if d == 0:
        return None
    return C((a.re * b.re + a.im * b.im) / d, (a.im * b.re - a.re * b.im) / d)


def apply_convention(op: Operator, verdict: Optional[Verdict] = None) -> Verdict:
    """Fix how ``op`` enters the Lagrangian, from its derived conjugacy.  Mutates ``op``.

    hermitian      -> L = C Q, C real.
    antihermitian  -> restore the factor i that Murphy's typesetting drops on the bare
                      Dlr rows (his definition puts the i outside the symbol), so that
                      L = C (i Q) with C real.  68 rows, classes 8, 14 and 15.
    complex        -> if Murphy marks + h.c., L = C Q + h.c. with C complex.  If he does
                      not (the 14 class-11 psi^2H^2D^3 rows, Hermitian only after
                      integration by parts), L = (C/2)(Q + Q^dag) with C real: the
                      Hermitian part, which coincides with C Q whenever Q is Hermitian.
    """
    v = verdict or classify(op)
    if v.kind == "hermitian":
        op.hermitian, op.plus_hc, op.hc_mode = True, False, "real"
    elif v.kind == "antihermitian":
        op.terms = [Term(I * t.coeff, t.factors) for t in op.terms]
        op.hermitian, op.plus_hc, op.hc_mode = True, False, "real"
        op.notes = (op.notes + "; " if op.notes else "") + "factor i inserted (row anti-Hermitian as typeset)"
    elif op.plus_hc:
        op.hermitian, op.hc_mode = False, "complex"
    else:
        op.hermitian, op.plus_hc, op.hc_mode = False, True, "sym"
        op.notes = (op.notes + "; " if op.notes else "") + "Hermitian only up to IBP: emitted as (C/2)(Q + h.c.), C real"
    return v


# backwards-compatible alias
apply_i_convention = apply_convention
