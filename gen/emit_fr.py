"""
dim8auto.gen.emit_fr
====================

Write FeynRules model code from DSL operators.  Every operator is one ``ExpandIndices[...]``
block with ``FlavorExpand->{SU2W,SU2D}``, Goldstones zeroed in unitary gauge, Levi-Civita
canonicalised, and the block cached.

Public entry points
-------------------
emit_term(term)                  -> FeynRules string for one DSL term (no WC)
emit_operator_expr(op, wc=None)  -> "wc (term1 + term2 + ...)" with h.c. if needed
emit_block(ops, name)            -> a complete  Lname := Block[...]  definition
emit_parameters(ops, ...)        -> M$Parameters entries for the Wilson coefficients
emit_model_fragment(ops, ...)    -> parameters + blocks + an Ltotal for a list of ops
index_mismatch(new, old)         -> what a new block index changes that must stay fixed (./dim8 build)
"""

from __future__ import annotations

import os
import re
from fractions import Fraction
from typing import Dict, Iterable, List, Optional, Sequence

from dsl import ALL_INDEX_NAMES, FRContext, Gamma, H, Operator, Psi, Term, FS, Tensor, EPS_LOR_SIGN
import emit_flavour as EF


# --------------------------------------------------------------------------------------
# flavour
# --------------------------------------------------------------------------------------

# The flavour mode of a build: "mfv" (the default, and that of the released models), a delta on the
# bilinears of one species and Yukawa matrices on the others, or with DIM8_FLAVOUR=universal a delta on
# each bilinear.  A bilinear that joins two species is not invariant under U(3)^5 with a delta.  It is
# invariant with the Yukawa matrices as spurions, in the form the dimension-six sector has them
# (gen/make_dim6.py), with Y_u and Y_e diagonal and Y_d = CKM diag(y_d) in the basis of the doublet of the
# base model.  The other operators come out exactly as in the universal mode, so that only the blocks of
# the first kind differ between the two.
FLAVOR = os.environ.get("DIM8_FLAVOUR", "mfv")
# The flavour structures of the fermionic operators (gen/emit_flavour.py).  An operator that has them is
# written with a general flavour coefficient in the mfv mode; one that has none (Q_{e^4B}^{(2)}, whose
# structures all vanish to the order kept) keeps the structure of mfv_structure below.
MFV_STRUCTURES = EF.load_structures() if FLAVOR in ("mfv", "mfvexplicit") else {}
# Without the list a build in the mfv mode would write every operator with one structure, a model that
# the vertices of the general form cannot be compared with, so it stops instead.
if FLAVOR in ("mfv", "mfvexplicit") and not MFV_STRUCTURES:
    raise SystemExit(f"{EF.STRUCTURES} is missing: write it with python3 validate/flavour_rank.py mfv, "
                     "or build in the universal mode (DIM8_FLAVOUR=universal)")

# the number of Yukawa matrices that join a barred field of the first species to a field of the second
MFV_YUKAWAS = {("q", "q"): 0, ("u", "u"): 0, ("d", "d"): 0, ("l", "l"): 0, ("e", "e"): 0,
               ("q", "u"): 1, ("u", "q"): 1, ("q", "d"): 1, ("d", "q"): 1, ("l", "e"): 1, ("e", "l"): 1,
               ("u", "d"): 2, ("d", "u"): 2}
MFV_DUMMIES = ("z8y1", "z8y2", "z8y3", "z8y4")


def mfv_structure(op: Operator):
    """(pairs, spurions) of an operator at leading order in the Yukawa matrices: the pairs of generation
    indices a delta identifies, and (species of the barred field, of the other, its index, the other's
    index) for each pair that a Yukawa matrix joins.  Of the two ways to pair the barred fields of a
    four-fermion operator with the others, this takes the one with fewer Yukawa matrices and, when they
    tie, the bilinears as written, which is how the dimension-six operators have them.  So
    (qbar u)(qbar d) has Y_u Y_d, (lbar q)(qbar e) has Y_e on l and e and a delta on the quarks, and
    (ubar d)(qbar u) has Y_d on q and d and a delta on the up quarks.  An operator that violates
    baryon number has no such pairing and stays as it is: it is not exported."""
    pairs = tuple(op.flavor_pairs or ())
    seen = None
    for t in op.terms:
        here = {f.gen: (f.name, bool(f.bar)) for f in t.factors if isinstance(f, Psi)}
        if seen is None:
            seen = here
        if here != seen:
            raise ValueError(f"{op.name}: the terms give the generation indices different fields")
    if not pairs or not seen or sum(bar for _, bar in seen.values()) * 2 != len(seen) or any(a not in seen or b not in seen for a, b in pairs):
        return pairs, ()
    ordered = [(a, b) if seen[a][1] else (b, a) for a, b in pairs]
    if any(not seen[a][1] or seen[b][1] for a, b in ordered):
        return pairs, ()
    ways = [ordered]
    if len(ordered) == 2:
        ways.append([(ordered[0][0], ordered[1][1]), (ordered[1][0], ordered[0][1])])
    def cost(way):
        return sum(MFV_YUKAWAS.get((seen[a][0], seen[b][0]), 99) for a, b in way)
    best = min(ways, key=cost)      # min keeps the first of a tie, the bilinears as written
    if cost(best) >= 99:
        raise ValueError(f"{op.name}: no pairing of its fields has Yukawa matrices that join them")
    return (tuple((a, b) for a, b in best if seen[a][0] == seen[b][0]),
            tuple((seen[a][0], seen[b][0], a, b) for a, b in best if seen[a][0] != seen[b][0]))


def mfv_factor(barred: str, other: str, a: str, b: str, y1: str, y2: str) -> str:
    """The element a, b of the Yukawa matrices that join a barred field of one species to a field of another."""
    return {("q", "u"): f"yu[{a},{b}]",
            ("u", "q"): f"yu[{b},{a}]",
            ("l", "e"): f"yl[{a},{b}]",
            ("e", "l"): f"yl[{b},{a}]",
            ("q", "d"): f"CKM[{a},{y1}] yd[{y1},{b}]",
            ("d", "q"): f"Conjugate[CKM[{b},{y1}]] yd[{y1},{a}]",
            ("u", "d"): f"yu[{a},{y1}] CKM[{y1},{y2}] yd[{y2},{b}]",
            ("d", "u"): f"yd[{y2},{a}] Conjugate[CKM[{y1},{y2}]] yu[{y1},{b}]"}[(barred, other)]


# --------------------------------------------------------------------------------------
# single term
# --------------------------------------------------------------------------------------


def emit_term(term: Term, flavor: str = "universal", flavor_pairs=(), spurions=(), gens=()) -> str:
    """flavor = "universal": generation indices are identified pairwise (delta_{pr});
    flavor = "general": every generation index is kept free (WC carries them, named in the order of gens,
    so that every term of an operator gives them the names the coefficient has);
    flavor = "mfv": as universal on flavor_pairs, with the Yukawa matrices of spurions on the others."""
    ctx = FRContext(term)
    # 1. Kronecker identifications first (so that both sides of a delta get one name)
    for f in term.factors:
        for a, b in f.identities():
            ctx.identify(a, b)
    if flavor in ("universal", "mfv"):
        for a, b in flavor_pairs:
            if a in ctx.types and b in ctx.types:
                ctx.identify(a, b)
    if flavor == "general":
        for g in gens:
            ctx.name(g)

    # 2. name every index in order of appearance (deterministic output)
    for f in term.factors:
        for n, _ in f.slots():
            if ctx.types.get(n) != "sp":  # spinor indices are named when the bilinear is built
                ctx.name(n)

    # 3. walk factors: commuting pieces are multiplied, fermion fields are grouped into
    #    Dot-chains psibar . psi (Grassmann ordering matters for FeynRules)
    pieces: List[str] = []
    chain: List[str] = []  # open fermion chain

    def flush():
        nonlocal chain
        if chain:
            pieces.append("(" + ".".join(chain) + ")")
            chain = []

    for f in term.factors:
        if isinstance(f, Psi):
            chain.append(f.fr(ctx))
            if not f.opens_chain:  # a bilinear ends with the un-barred (or CC[psi]) field
                flush()
        else:
            s = f.fr(ctx)
            if s:
                pieces.append(s)
    flush()
    for k, (barred, other, a, b) in enumerate(spurions):
        pieces.append(mfv_factor(barred, other, ctx.name(a), ctx.name(b), MFV_DUMMIES[2 * k], MFV_DUMMIES[2 * k + 1]))
    c = term.coeff.fr()
    body = " ".join(pieces)
    return body if c == "1" else f"{c} {body}"


# --------------------------------------------------------------------------------------
# operator -> expression
# --------------------------------------------------------------------------------------


def _split_top(s: str) -> List[str]:
    """Split "(a) + (b) + (c)" at top-level plus signs, stripping one layer of parens."""
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "+" and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    res = []
    for x in out:
        x = x.strip()
        if x.startswith("(") and x.endswith(")"):
            x = x[1:-1]
        if x:
            res.append(x)
    return res


def _monomials(s: str) -> List[str]:
    """Fully flatten a nested sum of parenthesised products into its monomials.  Repeats
    _split_top until no piece is itself a sum, so a zero factor can only ever kill the one
    monomial it multiplies."""
    todo, out = [s], []
    while todo:
        x = todo.pop()
        parts = _split_top(x)
        if len(parts) == 1:
            y = parts[0].strip()
            # strip redundant outer parentheses around a single product
            while y.startswith("(") and y.endswith(")") and len(_split_top(y[1:-1])) == 1 and _balanced(y[1:-1]):
                y = y[1:-1].strip()
            if len(_split_top(y)) == 1:
                # a coefficient times a parenthesised SUM, e.g. "-1 ((a) + (b))" (two
                # epsilon expansions nest this way): distribute it, otherwise the sum
                # would be carried as one opaque factor and never combined exactly.
                # Differences ("(Ga Ga - Ga Ga)", the sigma block) are not sums here and
                # stay intact.
                toks = _factor_tokens(y)
                k = next((i for i, tk in enumerate(toks)
                          if tk.startswith("(") and tk.endswith(")") and _balanced(tk[1:-1]) and len(_split_top(tk[1:-1])) > 1), None)
                if k is None:
                    # a parenthesised PRODUCT used as a factor, e.g. "-1 (a b c)": unwrap it
                    # so that the combiner sees the individual factors.  Numeric tokens
                    # ("(-1)", "(I/2)") and differences (the sigma block) are left alone.
                    k = next((i for i, tk in enumerate(toks)
                              if tk.startswith("(") and tk.endswith(")") and tk not in _NUM_TOK
                              and _balanced(tk[1:-1]) and not _has_top_sign(tk[1:-1])
                              and len(_factor_tokens(tk[1:-1])) > 1), None)
                    if k is None:
                        out.append(y)
                    else:
                        todo.append(" ".join(toks[:k] + _factor_tokens(toks[k][1:-1]) + toks[k + 1:]))
                else:
                    for part in _split_top(toks[k][1:-1]):
                        todo.append(" ".join(toks[:k] + [f"({part})"] + toks[k + 1:]))
            else:
                todo.append(y)
        else:
            todo.extend(parts)
    return out


def _has_top_sign(s: str) -> bool:
    """True if a '+' or a binary '-' occurs outside every bracket (a sum or difference)."""
    d = 0
    prev = " "
    for i, ch in enumerate(s):
        if ch in "([":
            d += 1
        elif ch in ")]":
            d -= 1
        elif d == 0 and i > 0 and (ch == "+" or (ch == "-" and prev == " ")):
            return True
        prev = ch
    return False


def _balanced(s: str) -> bool:
    d = 0
    for ch in s:
        if ch == "(":
            d += 1
        elif ch == ")":
            d -= 1
        if d < 0:
            return False
    return d == 0


def _sum(terms: Sequence[str]) -> str:
    return " + ".join(f"({t})" for t in terms) if len(terms) > 1 else terms[0]



def sub_su2_index(t: str, n: str, v: int) -> str:
    """Substitute SU(2) index ``n`` by the literal ``v`` everywhere, fermion doublet fields
    included.

    The model defines QL[sp,1,ff,cc] :> Module[{sp2}, ProjM[sp,sp2] uq[sp2,ff,cc]], so a
    literal index on a doublet selects its component directly.  With literal indices on the
    Higgs and on the fermion doublets the control Q_{leWH^3}^{(1)} gives its 36 vertices and
    no spin-index warnings."""
    return re.sub(rf"\b{n}\b", str(v), t)

_SU2A_EPS = re.compile(r"Eps\[(z8[A-F]),(z8[A-F]),(z8[A-F])\] ")
_PERMS = (((1, 2, 3), 1), ((2, 3, 1), 1), ((3, 1, 2), 1), ((1, 3, 2), -1), ((3, 2, 1), -1), ((2, 1, 3), -1))


def expand_eps_su2a(term_str: str) -> str:
    """Write epsilon^{IJK} on SU(2)_w adjoint indices as its six explicit permutations.

    FeynRules' ``Eps[A,B,C]`` with three adjoint indices contracted into ``Ta``'s is
    mis-expanded under ``FlavorExpand -> {SU2W}``: on Q_{l^2H^4D}^{(3)} it yields 272
    terms, 60 vertices, 180 non-Hermitian ones and vertices with no W at all, which the
    epsilon forbids.  The identical operator with the epsilon written out gives 40 terms,
    10 vertices and CheckHermiticity = 0.  Numeric adjoint indices are legal in Ta[1,i,j]
    and FS[Wi,mu,nu,1], so the expansion is a textual substitution on the generated term."""
    m = _SU2A_EPS.search(term_str)
    if not m:
        return term_str
    a, b, c = m.groups()
    base = term_str[: m.start()] + term_str[m.end():]
    out = []
    for (x, y, z), sg in _PERMS:
        t = re.sub(rf"\b{a}\b", str(x), base)
        t = re.sub(rf"\b{b}\b", str(y), t)
        t = re.sub(rf"\b{c}\b", str(z), t)
        out.append(("" if sg > 0 else "-1 ") + t)
    return " + ".join(f"({t})" for t in out)


_SU2F_EPS = re.compile(r"Eps\[(z8[i-r]),(z8[i-r])\] ")


def expand_eps_su2f(term_str: str) -> str:
    """epsilon_{jk} on SU(2)_w fundamental indices as its two explicit terms,
    eps_{12} = +1.  FeynRules fails here as in the adjoint case: under its own expansion
    Q_{udWH^2}^{(1,2)}, which vanish identically, produce 108 and 60 charge-violating
    vertices, and the three Q_{quWHD^2} blocks (Ta . Eps[j,k] . DC[Phibar[k]]) do not
    finish expanding."""
    out = term_str
    while True:
        m = _SU2F_EPS.search(out)
        if not m:
            return out
        a, b = m.groups()
        base = out[: m.start()] + out[m.end():]
        t1 = sub_su2_index(sub_su2_index(base, a, 1), b, 2)
        t2 = sub_su2_index(sub_su2_index(base, a, 2), b, 1)
        out = f"(({t1}) + (-1 {t2}))"


_SU2F_IDX = re.compile(r"\bz8[i-r]\b")
_SU2A_IDX = re.compile(r"\bz8[A-F]\b")
EXPAND_SU2_EXPLICITLY = True
COMBINE_MONOMIALS = True
SORT_FACTORS = True


def expand_su2_all(term_str: str) -> str:
    """Substitute every SU(2)_w index, fundamental (1,2) and adjoint (1,2,3), so that
    FeynRules never sees a symbolic SU(2) index.  Ta[a,i,j], Eps[i,j], Eps[a,b,c],
    Phi[i], QL[s,i,f,c] and FS[Wi,mu,nu,a] all accept numeric indices and evaluate to
    numbers or components, and FlavorExpand has nothing left to do.

    FeynRules' own SU(2) expansion fails on several structures (Eps[A,B,C] with Ta's,
    Eps[j,k] with Ta and DC, Ta with a numeric fundamental and a symbolic adjoint index).
    Doing the expansion here, exactly and visibly, removes that machinery from the trust
    chain.  Terms that vanish by antisymmetry (Eps with a repeated numeric index) are
    dropped before the term is written."""
    fund = sorted(set(_SU2F_IDX.findall(term_str)))
    adj = sorted(set(_SU2A_IDX.findall(term_str)))
    if not fund and not adj:
        return term_str
    import itertools

    out = []
    for fv in itertools.product((1, 2), repeat=len(fund)):
        for av in itertools.product((1, 2, 3), repeat=len(adj)):
            t = term_str
            for n, v in zip(fund, fv):
                t = sub_su2_index(t, n, v)
            for n, v in zip(adj, av):
                t = re.sub(rf"\b{n}\b", str(v), t)
            # antisymmetric tensors with a repeated index vanish: drop the term
            dead = False
            for m in re.finditer(r"Eps\[([0-9,]+)\]", t):
                idx = m.group(1).split(",")
                if len(set(idx)) != len(idx):
                    dead = True
                    break
            if not dead:
                out.append(t)
    if not out:
        return "0"
    return " + ".join(f"({t})" for t in out)


# (sigma^a)_{ij}: FeynRules leaves Ta[a,i,j] with numeric indices UNEVALUATED (Ta[3,1,1] +
# Ta[3,2,2] stays symbolic), so the numbers are supplied here.  tau^a = 2 Ta = sigma^a.
_SIGMA = {
    (1, 1, 1): "0", (1, 1, 2): "1", (1, 2, 1): "1", (1, 2, 2): "0",
    (2, 1, 1): "0", (2, 1, 2): "(-I)", (2, 2, 1): "I", (2, 2, 2): "0",
    (3, 1, 1): "1", (3, 1, 2): "0", (3, 2, 1): "0", (3, 2, 2): "(-1)",
}
_TA_NUM = re.compile(r"2 Ta\[([123]),([12]),([12])\]")
_EPS_NUM = re.compile(r"Eps\[([0-9]),([0-9])\] |Eps\[([0-9]),([0-9]),([0-9])\] ")


def _signature(seq):
    seq = list(seq)
    sgn = 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                sgn = -sgn
    return sgn


def numeric_su2_values(term_str: str) -> str:
    """Replace numeric-index SU(2) tensors by their values: 2 Ta[a,i,j] -> (sigma^a)_ij,
    Eps[i,j] and Eps[a,b,c] -> their signature.  A vanishing entry kills the term."""
    def ta(m):
        return _SIGMA[(int(m.group(1)), int(m.group(2)), int(m.group(3)))]
    t = _TA_NUM.sub(ta, term_str)
    if re.search(r"(?<![0-9A-Za-z_])0 ", t):        # a zero Pauli entry appeared
        return "0"
    def eps(m):
        idx = [int(x) for x in m.groups() if x is not None]
        if len(set(idx)) != len(idx):
            return "0 "
        return ("" if _signature(idx) > 0 else "(-1) ")
    t = _EPS_NUM.sub(eps, t)
    if re.search(r"(?<![0-9A-Za-z_])0 ", t):
        return "0"
    return t


_NUM_TOK = {"-1": (-1, 0), "1": (1, 0), "I": (0, 1), "(I)": (0, 1), "(-I)": (0, -1), "(-1)": (-1, 0), "(1)": (1, 0),
            "(I/2)": (0, Fraction(1, 2)), "(-I/2)": (0, Fraction(-1, 2)), "(1/2)": (Fraction(1, 2), 0),
            "(-1/2)": (Fraction(-1, 2), 0), "2": (2, 0), "(2)": (2, 0)}


def _cmul(a, b):
    return (a[0] * b[0] - a[1] * b[1], a[0] * b[1] + a[1] * b[0])


def _cstr(c) -> str:
    re_, im = Fraction(c[0]), Fraction(c[1])
    def f(x):
        return str(x.numerator) if x.denominator == 1 else f"({x.numerator}/{x.denominator})"
    if im == 0:
        return f(re_)
    if re_ == 0:
        return "I" if im == 1 else "(-I)" if im == -1 else f"({f(im)} I)"
    return f"({f(re_)} + {f(im)} I)"


def _factor_tokens(m: str) -> List[str]:
    """Split a monomial into factors at spaces that are outside every ( ) and [ ].
    A factor such as "(I/2) (Ga[..] Ga[..] - Ga[..] Ga[..])" must stay one token: splitting
    it on inner spaces and re-sorting would scramble every sigma^{mu nu} operator (on the
    control Q_{leWH^3}^{(1)} it turns 36 clean vertices into 32, 9 of them without a gauge
    field)."""
    out, cur, depth = [], "", 0
    for ch in m:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == " " and depth == 0:
            if cur:
                out.append(cur)
            cur = ""
        else:
            cur += ch
    if cur:
        out.append(cur)
    return out


def combine_monomials(monos: List[str]) -> List[str]:
    """Sum coefficients of identical products and drop the zeros.

    FeynRules' ExpandIndices is not linear on sums of numeric-component monomials: the
    generated Q_{udWH^2}^{(1)} is a polynomial that cancels to zero exactly, and FeynRules
    still produces 38 terms and 18 vertices from it.  So the cancellation is done here,
    where it is exact, and FeynRules only ever sees a polynomial with nothing left to
    cancel."""
    acc: Dict[tuple, tuple] = {}
    order: List[List[str]] = []
    for m in monos:
        coef = (Fraction(1), Fraction(0))
        keep = []
        for t in _factor_tokens(m.strip()):
            if t in _NUM_TOK:
                coef = _cmul(coef, _NUM_TOK[t])
            elif t:
                keep.append(t)
        key = tuple(sorted(keep))
        if key not in acc:
            order.append(keep)
        c0 = acc.get(key, (Fraction(0), Fraction(0)))
        acc[key] = (c0[0] + coef[0], c0[1] + coef[1])
    out = []
    for key, c in acc.items():
        if c[0] == 0 and c[1] == 0:
            continue
        # keep the original factor order for readability where possible: sorted is fine
        # for Mathematica (Times is orderless; Dot chains are single tokens)
        factors = key if SORT_FACTORS else next(o for o in order if tuple(sorted(o)) == key)
        out.append((_cstr(c) + " " if c != (1, 0) else "") + " ".join(factors))
    return out


def emit_operator_expr(op: Operator, wc: Optional[str] = None, lam: str = "Lam", flavor: str = "universal") -> str:
    """``wc/Lam^(d-4) * (Q)`` for an operator of dimension d.  The Hermitian conjugate for +h.c. operators is NOT added here:
    FeynRules' HC[] must be applied to the *expanded* Lagrangian (emit_block does that), since
    HC inside ExpandIndices on the explicit-spinor-index dialect loses vertices.

    In the mfv mode an operator with flavour structures (gen/emit_flavour.py) is written in the general
    mode, with the placeholder z8F<wc> as its coefficient; "mfvexplicit" writes the sum of its structures
    there instead, the same Lagrangian with the replacement made before FeynRules rather than after."""
    if flavor in ("mfv", "mfvexplicit") and op.name in MFV_STRUCTURES:
        if flavor == "mfv":
            return emit_operator_expr(op, wc=wc or EF.placeholder(op), lam=lam, flavor="general")
        ctx = FRContext(op.terms[0])
        names = {f"z8w{k + 1}": ctx.name(g) for k, g in enumerate(op.gens)}
        pars = EF.structure_parameters(op, MFV_STRUCTURES[op.name])
        coef = " + ".join(f"({p['coef']}) {EF.tensor(op, p['structure'])}" for p in pars)
        coef = re.sub(r"z8w\d+", lambda m: names[m.group(0)], coef)
        body = emit_operator_expr(op, wc="z8EXPLICIT", lam=lam, flavor="general")
        return body.replace("z8EXPLICIT[" + ",".join(names.values()) + "]", f"({coef})", 1)
    wc = wc or op.wc
    pairs, spurions = mfv_structure(op) if flavor == "mfv" else (op.flavor_pairs or (), ())
    terms = [expand_eps_su2f(expand_eps_su2a(emit_term(t, flavor=flavor, flavor_pairs=pairs, spurions=spurions, gens=op.gens)))
             for t in op.terms]
    if EXPAND_SU2_EXPLICITLY:
        expanded = []
        for t in terms:
            # work on MONOMIALS: the epsilon expansion already produced a sum, and a zero
            # Pauli entry may kill only one monomial of it
            pieces = []
            for mono in _monomials(t):
                for x in _monomials(expand_su2_all(mono)):
                    v = numeric_su2_values(x)
                    if v.strip() != "0":
                        pieces.append(v)
            expanded.extend(pieces)
        if COMBINE_MONOMIALS:
            expanded = combine_monomials(expanded)
        terms = [" + ".join(f"({x})" for x in expanded)] if expanded else ["0"]
    expr = _sum(terms)
    if flavor == "general" and op.gens:
        # WC carries the generation indices, in the FR names the context assigned
        ctx = FRContext(op.terms[0])
        gnames = [ctx.name(g) for g in op.gens]  # deterministic: ff1, ff2, ...
        wc = f"{wc}[{','.join(gnames)}]"
    # the power of the scale follows the mass dimension: 4 for every operator of gen/operators.py, more for
    # the towers of gen/towers.py
    pref = f"{wc}/{lam}^{int(op.mass_dimension()) - 4}"
    return f"{pref} ({expr})"


# --------------------------------------------------------------------------------------
# Lagrangian block (one ExpandIndices block per operator)
# --------------------------------------------------------------------------------------

BLOCK_LOCALS = ",".join(["z8lagH", "z8lagN", "z8lagS", "z8fmgr"] + ALL_INDEX_NAMES)


def emit_block(ops: Iterable[Operator], name: str, comment: str = "", flavor: str = "universal") -> str:
    """One FeynRules Lagrangian block.  Operators are bucketed by ``hc_mode``:

      "real"    Hermitian as written, real WC          -> z8lagH, no HC
      "complex" Murphy's "+ h.c." operators, complex WC -> z8lagN, plus HC[z8lagN]
      "sym"     Hermitian only up to IBP, real WC      -> z8lagS with a 1/2, plus HC[z8lagS]

    HC is applied AFTER index expansion and canonicalisation, the only reliable order
    (inside ExpandIndices it drops vertices without an error).
    """
    ops = list(ops)
    # An operator with a general flavour coefficient is Hermitian only with its conjugate added, so a
    # real coefficient goes with the 1/2 and the h.c. of the "sym" bucket (gen/emit_flavour.py).
    general = {o.name for o in ops if flavor in ("mfv", "mfvexplicit") and o.name in MFV_STRUCTURES}
    if general and flavor == "mfv" and len(ops) > 1:
        raise ValueError(f"{name}: the general flavour coefficient is shared between blocks, so a block holds one operator")
    herm = [o for o in ops if o.hc_mode == "real" and o.name not in general]
    nonh = [o for o in ops if o.hc_mode == "complex"]
    symm = [o for o in ops if o.hc_mode == "sym" or (o.hc_mode == "real" and o.name in general)]

    def sum_of(sub, half=False):
        pre = "(1/2) " if half else ""
        return " +\n".join(f"    (* {o.name} *)\n    {pre}{emit_operator_expr(o, flavor=flavor)}" for o in sub)

    def stanza(var, sub, half=False):
        if not sub:
            return f"  {var} = 0;"
        return f"""  {var} = ExpandIndices[
{sum_of(sub, half)},
    FlavorExpand -> {{SU2W, SU2D}}] /. z8fmgr;
  {var} = OptimizeIndex[{var}] /. Eps[args__] :> Signature[{{args}}] Eps[Sequence @@ Sort[{{args}}]];
  {var} = {var} /. del[a_, m1_] del[a_, m2_] Eps[n1__, m1_, n2__, m2_, n3__] :> 0;"""

    head = f"(* ---- {comment} ---- *)\n" if comment else ""
    body = "\n".join([stanza("z8lagH", herm), stanza("z8lagN", nonh), stanza("z8lagS", symm, half=True)])
    spur = flavor == "mfv" and any(mfv_structure(o)[1] for o in ops if o.name not in general)
    return f"""{head}{name} := Module[{{{BLOCK_LOCALS + ("," + ",".join(MFV_DUMMIES) if spur else "")}}},
  z8fmgr = If[Not[FeynmanGauge], {{G0|GP|GPbar -> 0}}, {{}}];
{body}
  Return[z8lagH
    + z8lagN + If[z8lagN === 0, 0, HC[z8lagN]]
    + z8lagS + If[z8lagS === 0, 0, HC[z8lagS]]];
];
"""


def emit_parameters(ops: Iterable[Operator], block_name: str = "DIM8", start: int = 1, order: str = "NP", order_power: int = 2) -> str:
    """External real (or complex) Wilson coefficients.  Complex ones are written as two real
    externals (Re, Im) plus an internal complex parameter, the usual FeynRules pattern."""
    out = []
    n = start
    for o in ops:
        cplx = o.hc_mode == "complex"
        # the name in a Wolfram string, without a backslash: FeynRules parses the Descriptions again when it merges the
        # model files, where an escaped backslash is read as an escape, so the (H^\dagger H)^k of gen/towers.py is (H^dag H)^k
        name = o.name.replace("\\dagger", "dag").replace("\\", "")
        if not cplx:
            out.append(
                f"""  {o.wc} == {{ ParameterType -> External, BlockName -> {block_name}, OrderBlock -> {n},
    Value -> 0, InteractionOrder -> {{{order},{order_power}}}, TeX -> Subscript[c, {o.wc[1:]}],
    Description -> "{name}" }}"""
            )
            n += 1
        else:
            out.append(
                f"""  {o.wc}Re == {{ ParameterType -> External, BlockName -> {block_name}, OrderBlock -> {n},
    Value -> 0, InteractionOrder -> {{{order},{order_power}}}, Description -> "Re {name}" }}"""
            )
            out.append(
                f"""  {o.wc}Im == {{ ParameterType -> External, BlockName -> {block_name}, OrderBlock -> {n + 1},
    Value -> 0, InteractionOrder -> {{{order},{order_power}}}, Description -> "Im {name}" }}"""
            )
            out.append(
                f"""  {o.wc} == {{ ParameterType -> Internal, ComplexParameter -> True,
    Value -> {o.wc}Re + I {o.wc}Im, InteractionOrder -> {{{order},{order_power}}}, Description -> "{name}" }}"""
            )
            n += 2
    return ",\n".join(out)


def emit_model_fragment(ops: List[Operator], block_prefix: str = "L8", per_block: int = 1, lam_value: float = 1000.0,
                        flavor: str = FLAVOR):
    """Parameters plus one Lagrangian block per chunk of ``per_block`` operators.

    The default is one operator per block.  That is what makes the build parallel and
    resumable: each block is an independent unit of work whose expanded Lagrangian and
    vertex list can be computed in a separate process, cached to disk, and merged into a
    single ``WriteUFO[..., Input -> vertices]`` call at the end.  It also means a
    Hermiticity failure names one operator.

    Returns (text, index) where index is a list of {block, ops, wcs} for the drivers, with the
    coefficients of the flavour structures of an operator under "flavour".  flavor is the mode of the
    blocks; a model to be read without the rules of emit_flavour_files takes "mfvexplicit".
    """
    blocks = []
    names = []
    index = []
    for i in range(0, len(ops), per_block):
        chunk = ops[i : i + per_block]
        nm = f"{block_prefix}op{i // per_block + 1}" if per_block == 1 else f"{block_prefix}blk{i // per_block + 1}"
        names.append(nm)
        entry = dict(block=nm, ops=[o.name for o in chunk], wcs=[o.wc for o in chunk],
                     cls=chunk[0].cls, hc_mode=chunk[0].hc_mode, n_terms=sum(len(o.terms) for o in chunk))
        # the coefficients of the flavour structures each operator has besides its own, in block DIM8F
        flav = [n for o in chunk if o.name in MFV_STRUCTURES
                for p in EF.structure_parameters(o, MFV_STRUCTURES[o.name]) for n, _, _ in p["externals"]]
        if flav:
            entry["flavour"] = flav
        index.append(entry)
        blocks.append(emit_block(chunk, nm, comment=", ".join(o.name for o in chunk), flavor=flavor))
    params = emit_parameters(ops)
    if MFV_STRUCTURES:
        params += ",\n" + EF.emit_parameters(ops, MFV_STRUCTURES)[0]
    lam = f"""  Lam == {{ ParameterType -> External, BlockName -> DIM8, OrderBlock -> 0, Value -> {lam_value},
    TeX -> \\[CapitalLambda], Description -> "EFT cutoff scale [GeV]" }}"""
    eps = f"""  {EPS_LOR_SIGN} == {{ ParameterType -> Internal, Value -> 1, Description -> "sign relating eps_(0123)=+1 to FeynRules Eps, see validate/conventions.md" }}"""
    txt = (
        "(* ===== generated by dim8auto: Wilson coefficients (FeynRules merges M$Parameters across model files) ===== *)\nM$Parameters = {\n"
        + lam + ",\n" + eps + ",\n" + params + "\n};\n\n"
        + "(* ===== generated by dim8auto: Lagrangian blocks, one per operator ===== *)\n"
        + "\n".join(blocks)
        + f"\n(* {len(names)} blocks; the drivers never sum them, they are computed and cached one at a time *)\n"
    )
    return txt, index


def emit_flavour_files(ops: List[Operator]) -> Dict[str, str]:
    """The files beside gen.fr that the mfv mode needs, by name in tests/gen_smoke: the placeholders the
    workers declare, and the rules that replace them when the UFO is written (gen/emit_flavour.py)."""
    if FLAVOR != "mfv" or not MFV_STRUCTURES:
        return {}
    # the block names of emit_model_fragment with one operator per block, which a shared placeholder needs
    blocks = {o.name: f"L8op{i + 1}" for i, o in enumerate(ops)}
    return {"gen_flavour.fr": EF.emit_placeholders(ops, MFV_STRUCTURES),
            "gen_flavour_rules.m": EF.emit_rules(ops, MFV_STRUCTURES, blocks)}


def index_mismatch(new_index: List[dict], old_index: List[dict]) -> List[str]:
    """What a block index written from the encoding changes in the existing one, as lines to print.

    What stays fixed is what the rest of the chain is keyed on: the block of an operator, which names
    its cached vertices, and the operator and coefficient names, which the released models, the
    restriction cards and the selector use.  So every existing entry must keep its block, ops and wcs.
    Everything else follows the encoding, so that a correction that changes the number of terms of an
    operator or how it enters the Lagrangian (cls, hc_mode, n_terms) is not refused, and operators
    appended after the existing ones take the next block numbers.  No two entries may share an operator
    or a coefficient, as an entry copied from a neighbour would: they would share one parameter, and
    every table keyed on a name would keep only one of them."""
    out = []
    for key in ("ops", "wcs"):
        seen = {}
        for e in new_index:
            for name in e[key]:
                if name in seen:
                    out.append(f"{e['block']}: {key} has {name}, which {seen[name]} has too")
                seen.setdefault(name, e["block"])
    for i, old in enumerate(old_index):
        if i >= len(new_index):
            out.append(f"{old['block']}: {', '.join(old['ops'])} is no longer in the encoding")
            continue
        for key in ("block", "ops", "wcs"):
            if new_index[i][key] != old[key]:
                out.append(f"{old['block']}: {key} was {old[key]}, the encoding has {new_index[i][key]}")
    return out
