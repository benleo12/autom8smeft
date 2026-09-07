"""
dim8auto.gen.emit_fr
====================

Emit FeynRules model code from DSL operators, in the dialect used by the collaborators'
hand-typed files (dim8_geosmeftVBF.fr): every operator is one ``ExpandIndices[...]`` block
with ``FlavorExpand->{SU2W,SU2D}``, Goldstones zeroed in unitary gauge, Levi-Civita
canonicalised, and the block cached.

Public entry points
-------------------
emit_term(term)                  -> FeynRules string for one DSL term (no WC)
emit_operator_expr(op, wc=None)  -> "wc (term1 + term2 + ...)" with h.c. if needed
emit_block(ops, name)            -> a complete  Lname := Block[...]  definition
emit_parameters(ops, ...)        -> M$Parameters entries for the Wilson coefficients
emit_model_fragment(ops, ...)    -> parameters + blocks + an Ltotal for a list of ops
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Dict, Iterable, List, Optional, Sequence

from dsl import ALL_INDEX_NAMES, FRContext, Gamma, H, Operator, Psi, Term, FS, Tensor, EPS_LOR_SIGN


# --------------------------------------------------------------------------------------
# single term
# --------------------------------------------------------------------------------------


def emit_term(term: Term, flavor: str = "universal", flavor_pairs=()) -> str:
    """flavor = "universal": generation indices are identified pairwise (delta_{pr});
    flavor = "general": every generation index is kept free (WC carries them)."""
    ctx = FRContext(term)
    # 1. Kronecker identifications first (so that both sides of a delta get one name)
    for f in term.factors:
        for a, b in f.identities():
            ctx.identify(a, b)
    if flavor == "universal":
        for a, b in flavor_pairs:
            if a in ctx.types and b in ctx.types:
                ctx.identify(a, b)

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



_FERM_FIELD = re.compile(r"\b(QLbar|QL|LLbar|LL)\[([^\]]*)\]")


def sub_su2_index(t: str, n: str, v: int) -> str:
    """Substitute SU(2) index ``n`` by the literal ``v`` everywhere EXCEPT inside fermion
    doublet fields, where the component is selected with IndexDelta instead.

    The model defines QL[sp,1,ff,cc] :> Module[{sp2}, ProjM[sp,sp2] uq[sp2,ff,cc]]; with a
    literal index that definition fires before ExpandIndices and plants an explicit-index
    ProjM inside the Dot chain, corrupting the spin indices (Part::pkspec1 and a
    charge-violating vertex on Q_{quWHD^2}^{(1)}).  IndexDelta is resolved by
    FlavorExpand -> {SU2D} inside ExpandIndices, where Dot chains are handled correctly.
    Higgs components are safe as literals (control Q_{leWH^3}^{(1)}: 36 vertices)."""
    # NOTE (2026-08-28): the IndexDelta variant was tried and is WORSE: the control
    # Q_{leWH^3}^{(1)} went from 36 clean vertices to 32 with 9 gauge-free ones and its own
    # spin-index warnings.  Literal indices on fermions are fine for that control
    # (36 vertices, no warnings), so literals are used everywhere.
    return re.sub(rf"\b{n}\b", str(v), t)

_SU2A_EPS = re.compile(r"Eps\[(z8[A-F]),(z8[A-F]),(z8[A-F])\] ")
_PERMS = (((1, 2, 3), 1), ((2, 3, 1), 1), ((3, 1, 2), 1), ((1, 3, 2), -1), ((3, 2, 1), -1), ((2, 1, 3), -1))


def expand_eps_su2a(term_str: str) -> str:
    """Write epsilon^{IJK} on SU(2)_w adjoint indices as its six explicit permutations.

    FeynRules' ``Eps[A,B,C]`` with three adjoint indices contracted into ``Ta``'s is
    mis-expanded under ``FlavorExpand -> {SU2W}``: on Q_{l^2H^4D}^{(3)} it yields 272
    terms, 60 vertices, 180 non-Hermitian ones and vertices with no W at all, which the
    epsilon forbids.  The identical operator with the epsilon written out gives 40 terms,
    10 vertices and CheckHermiticity = 0 (tests/gen_smoke/bisect13b.log, 2026-08-28).
    Numeric adjoint indices are legal in Ta[1,i,j] and FS[Wi,mu,nu,1], so the expansion
    is a textual substitution on the emitted term."""
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
    eps_{12} = +1.  Same FeynRules failure family as the adjoint case: Q_{udWH^2}^{(1,2)},
    which vanish identically, were producing 108 and 60 charge-violating vertices, and the
    three Q_{quWHD^2} blocks (Ta . Eps[j,k] . DC[Phibar[k]]) never finished expanding."""
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

    Motivation: FeynRules' own SU(2) expansion is the source of every failure found so far
    (Eps[A,B,C] with Ta's, Eps[j,k] with Ta and DC, Ta with a numeric fundamental and a
    symbolic adjoint index).  Doing the expansion here, exactly and visibly, removes that
    machinery from the trust chain.  Terms that vanish by antisymmetry (Eps with a repeated
    numeric index) are dropped before emission."""
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
# Ta[3,2,2] stays symbolic, tests/gen_smoke/look133.log), so the emitter must supply the
# numbers itself.  tau^a = 2 Ta = sigma^a.
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
    it on inner spaces and re-sorting scrambled every sigma^{mu nu} operator (control
    Q_{leWH^3}^{(1)}: 36 clean vertices became 32 with 9 gauge-free ones)."""
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
    emitted Q_{udWH^2}^{(1)} is a polynomial that cancels to zero exactly, and FeynRules
    still produced 38 terms and 18 vertices from it (tests/gen_smoke/mono133.log).  So the
    cancellation is done here, where it is exact, and FeynRules only ever sees a
    polynomial with nothing left to cancel."""
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
    """``wc/Lam^4 * (Q)``.  The Hermitian conjugate for +h.c. operators is NOT emitted here:
    FeynRules' HC[] must be applied to the *expanded* Lagrangian (emit_block does that), since
    HC inside ExpandIndices on the explicit-spinor-index dialect loses vertices."""
    wc = wc or op.wc
    terms = [expand_eps_su2f(expand_eps_su2a(emit_term(t, flavor=flavor, flavor_pairs=op.flavor_pairs or ()))) for t in op.terms]
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
    pref = f"{wc}/{lam}^4"
    return f"{pref} ({expr})"


# --------------------------------------------------------------------------------------
# Lagrangian block (hand-typed dialect)
# --------------------------------------------------------------------------------------

BLOCK_LOCALS = ",".join(["z8lagH", "z8lagN", "z8lagS", "z8fmgr"] + ALL_INDEX_NAMES)


def emit_block(ops: Iterable[Operator], name: str, comment: str = "", flavor: str = "universal") -> str:
    """One FeynRules Lagrangian block.  Operators are bucketed by ``hc_mode``:

      "real"    Hermitian as emitted, real WC          -> z8lagH, no HC
      "complex" Murphy's "+ h.c." rows, complex WC     -> z8lagN, plus HC[z8lagN]
      "sym"     Hermitian only up to IBP, real WC      -> z8lagS with a 1/2, plus HC[z8lagS]

    HC is applied AFTER index expansion and canonicalisation, the only reliable order
    (inside ExpandIndices it silently drops vertices, see tests/gen_smoke/hcdiag4.log).
    """
    ops = list(ops)
    herm = [o for o in ops if o.hc_mode == "real"]
    nonh = [o for o in ops if o.hc_mode == "complex"]
    symm = [o for o in ops if o.hc_mode == "sym"]

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
    return f"""{head}{name} := Module[{{{BLOCK_LOCALS}}},
  z8fmgr = If[Not[FeynmanGauge], {{G0|GP|GPbar -> 0}}, {{}}];
{body}
  Return[z8lagH
    + z8lagN + If[z8lagN === 0, 0, HC[z8lagN]]
    + z8lagS + If[z8lagS === 0, 0, HC[z8lagS]]];
];
"""


def emit_parameters(ops: Iterable[Operator], block_name: str = "DIM8", start: int = 1, order: str = "NP", order_power: int = 2) -> str:
    """External real (or complex) Wilson coefficients.  Complex ones are emitted as two real
    externals (Re, Im) plus an internal complex parameter, the usual FeynRules pattern."""
    out = []
    n = start
    for o in ops:
        cplx = o.hc_mode == "complex"
        if not cplx:
            out.append(
                f"""  {o.wc} == {{ ParameterType -> External, BlockName -> {block_name}, OrderBlock -> {n},
    Value -> 0, InteractionOrder -> {{{order},{order_power}}}, TeX -> Subscript[c, {o.wc[1:]}],
    Description -> "{o.name}" }}"""
            )
            n += 1
        else:
            out.append(
                f"""  {o.wc}Re == {{ ParameterType -> External, BlockName -> {block_name}, OrderBlock -> {n},
    Value -> 0, InteractionOrder -> {{{order},{order_power}}}, Description -> "Re {o.name}" }}"""
            )
            out.append(
                f"""  {o.wc}Im == {{ ParameterType -> External, BlockName -> {block_name}, OrderBlock -> {n + 1},
    Value -> 0, InteractionOrder -> {{{order},{order_power}}}, Description -> "Im {o.name}" }}"""
            )
            out.append(
                f"""  {o.wc} == {{ ParameterType -> Internal, ComplexParameter -> True,
    Value -> {o.wc}Re + I {o.wc}Im, InteractionOrder -> {{{order},{order_power}}}, Description -> "{o.name}" }}"""
            )
            n += 2
    return ",\n".join(out)


def emit_model_fragment(ops: List[Operator], block_prefix: str = "L8", per_block: int = 1, lam_value: float = 1000.0):
    """Parameters plus one Lagrangian block per chunk of ``per_block`` operators.

    The default is one operator per block.  That is what makes the build parallel and
    resumable: each block is an independent unit of work whose expanded Lagrangian and
    vertex list can be computed in a separate process, cached to disk, and merged into a
    single ``WriteUFO[..., Input -> vertices]`` call at the end.  It also means a
    Hermiticity failure names one operator rather than a group of six.

    Returns (text, index) where index is a list of {block, ops, wcs} for the drivers.
    """
    blocks = []
    names = []
    index = []
    for i in range(0, len(ops), per_block):
        chunk = ops[i : i + per_block]
        nm = f"{block_prefix}op{i // per_block + 1}" if per_block == 1 else f"{block_prefix}blk{i // per_block + 1}"
        names.append(nm)
        index.append(dict(block=nm, ops=[o.name for o in chunk], wcs=[o.wc for o in chunk],
                          cls=chunk[0].cls, hc_mode=chunk[0].hc_mode, n_terms=sum(len(o.terms) for o in chunk)))
        blocks.append(emit_block(chunk, nm, comment=", ".join(o.name for o in chunk)))
    params = emit_parameters(ops)
    lam = f"""  Lam == {{ ParameterType -> External, BlockName -> DIM8, OrderBlock -> 0, Value -> {lam_value},
    TeX -> \\[CapitalLambda], Description -> "EFT cutoff scale [GeV]" }}"""
    eps = f"""  {EPS_LOR_SIGN} == {{ ParameterType -> Internal, Value -> 1, Description -> "sign relating eps_(0123)=+1 to FeynRules Eps; fixed by validate/levi_civita" }}"""
    txt = (
        "(* ===== generated by dim8auto: Wilson coefficients (FeynRules merges M$Parameters across model files) ===== *)\nM$Parameters = {\n"
        + lam + ",\n" + eps + ",\n" + params + "\n};\n\n"
        + "(* ===== generated by dim8auto: Lagrangian blocks, one per operator ===== *)\n"
        + "\n".join(blocks)
        + f"\n(* {len(names)} blocks; the drivers never sum them, they are computed and cached one at a time *)\n"
    )
    return txt, index
