"""
gen/parse_murphy.py  --  parse the LaTeX of Murphy's operator tables into DSL Operators.

Pipeline:  LaTeX string  -> tokens -> atoms (a flat list of typed objects with their explicit
indices) -> semantic resolution (implicit SU(2)/SU(3)/Lorentz contractions, Hermitian
derivatives, derivatives of brackets, duals) -> dsl.Operator (sum of Terms).

Design rule: anything not understood raises ParseError.  Never guess.

Grammar (informal)
------------------
expr     := ['i'] prefactor* product
prefactor:= '\\epsilon^{IJK}' | '\\epsilon_{jk}' | 'f^{ABC}' | 'd^{ABC}' | '\\epsilon_{\\alpha\\beta\\gamma}'
product  := item+
item     := '(' sum ')' | '[' sum ']' | deriv item | atom
sum      := product (('+'|'-') product)*
deriv    := 'D' idx                   (D_\\mu, D^\\mu, D_{(\\mu}D_{\\nu)} ...)
atom     := fieldstrength | higgs | fermion | gamma | tensor
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from typing import List, Optional, Tuple, Union

from dsl import (
    C, FS, Gamma, H, I, Operator, Psi, Tensor, Term, T, fresh, prod, scale, FSdual,
)


class ParseError(Exception):
    pass


# --------------------------------------------------------------------------------------
# tokenizer
# --------------------------------------------------------------------------------------

TOKEN_RE = re.compile(
    r"""
    (?P<ws>\s+|\\,|\\;|\\!|\\quad|\\qquad|\\\\|\\nonumber|\\nn|&)      # whitespace-ish
  | (?P<lbr>\{)|(?P<rbr>\})|(?P<lp>\()|(?P<rp>\))|(?P<lsq>\[)|(?P<rsq>\])
  | (?P<sup>\^)|(?P<sub>_)
  | (?P<plus>\+)|(?P<minus>-)
  | (?P<cmd>\\[A-Za-z]+)
  | (?P<name>[A-Za-z])
  | (?P<num>\d+)
  | (?P<other>.)
    """,
    re.VERBOSE,
)


def tokenize(s: str) -> List[Tuple[str, str]]:
    s = s.strip().strip("$").strip()
    out = []
    for m in TOKEN_RE.finditer(s):
        kind = m.lastgroup
        if kind == "ws":
            continue
        out.append((kind, m.group()))
    return out


# --------------------------------------------------------------------------------------
# atoms
# --------------------------------------------------------------------------------------

GREEK_LOR = {"\\mu", "\\nu", "\\rho", "\\sigma", "\\lambda", "\\alpha", "\\beta", "\\gamma", "\\tau"}  # Lorentz when on X/D/gamma
SU2A = {"I", "J", "K"}
SU2F = {"j", "k", "m", "n"}
SU3A = {"A", "B", "C", "D", "E"}
SU3F = {"\\alpha", "\\beta", "\\gamma", "\\delta"}
GEN = {"p", "r", "s", "t"}
FERMION_NAMES = {"l", "e", "q", "u", "d"}


@dataclass
class Atom:
    kind: str  # 'FS','H','Psi','Gamma','Tensor','D','Dlr','open','close','plus','minus','i','C'
    name: str = ""
    sup: List[str] = field(default_factory=list)  # raw index tokens (strings)
    sub: List[str] = field(default_factory=list)
    bar: bool = False
    tilde: bool = False
    dag: bool = False
    bracket: str = ""  # '(' or '[' for open/close
    sym: Optional[Tuple[str, str]] = None  # symmetrised derivative pair D_{(mu}D_{nu)}
    extra: dict = field(default_factory=dict)


class Cursor:
    def __init__(self, toks):
        self.t = toks
        self.i = 0

    def peek(self, k=0):
        return self.t[self.i + k] if self.i + k < len(self.t) else (None, None)

    def next(self):
        tok = self.peek()
        self.i += 1
        return tok

    def done(self):
        return self.i >= len(self.t)


def read_group(cur: Cursor) -> List[str]:
    """Read either a single token or a {...} group; return list of index-ish strings."""
    kind, val = cur.peek()
    if kind == "lbr":
        cur.next()
        items = []
        depth = 1
        buf = ""
        while True:
            kind, val = cur.next()
            if kind is None:
                raise ParseError("unbalanced {")
            if kind == "lbr":
                depth += 1
            elif kind == "rbr":
                depth -= 1
                if depth == 0:
                    break
            if kind in ("cmd", "name", "num", "lp", "rp", "other", "plus", "minus"):
                items.append(val)
        return items
    cur.next()
    return [val]


def split_indices(items: List[str]) -> List[str]:
    """'A\\mu\\nu' style groups come as separate tokens already; handle (..) symmetrisation
    markers and spacing commands."""
    out = []
    for x in items:
        if x in ("\\,", "\\;", "\\!"):
            continue
        out.append(x)
    return out


def parse_atoms(s: str) -> List[Atom]:
    cur = Cursor(tokenize(s))
    atoms: List[Atom] = []
    while not cur.done():
        kind, val = cur.next()
        if kind == "lp" and _is_eps_tau(cur):
            atoms.append(_parse_eps_tau(cur))
        elif kind == "lp" and _is_paren_T(cur):
            atoms.append(_parse_paren_T(cur))
        elif kind == "lp":
            atoms.append(Atom("open", bracket="("))
        elif kind == "rp":
            atoms.append(Atom("close", bracket="("))
            if cur.peek()[0] == "sup":
                cur.next()
                grp = read_group(cur)
                if len(grp) != 1 or not grp[0].isdigit():
                    raise ParseError(f"bracket power {grp}")
                atoms.append(Atom("power", name=grp[0]))
        elif kind == "lsq":
            atoms.append(Atom("open", bracket="["))
        elif kind == "rsq":
            atoms.append(Atom("close", bracket="["))
        elif kind == "plus":
            atoms.append(Atom("plus"))
        elif kind == "minus":
            atoms.append(Atom("minus"))
        elif kind == "num":
            atoms.append(Atom("num", name=val))
        elif kind == "name" and val == "i" and not atoms or (kind == "name" and val == "i" and atoms[-1].kind in ("open", "plus", "minus")):
            atoms.append(Atom("i"))
        elif kind == "name" and val == "C":
            atoms.append(Atom("C"))
        elif kind == "cmd" and val in ("\\bar", "\\widetilde", "\\tilde"):
            # modifier applies to the next atom
            nxt = parse_one(cur, bar=(val == "\\bar"), tilde=(val != "\\bar"))
            atoms.append(nxt)
        elif kind == "name" and val == "D":
            atoms.append(parse_deriv(cur))
        elif kind == "cmd" and val == "\\overleftrightarrow":
            # \overleftrightarrow{D}^\nu  or  \overleftrightarrow{D}^{I\nu}
            grp = read_group(cur)
            if grp != ["D"]:
                raise ParseError(f"overleftrightarrow of {grp}")
            a = parse_deriv(cur)
            a.kind = "Dlr"
            atoms.append(a)
        else:
            cur.i -= 1
            atoms.append(parse_one(cur))
    return _merge_symmetrised_colour(atoms)


def _merge_symmetrised_colour(atoms: List[Atom]) -> List[Atom]:
    """(T^A)_{(alpha}^delta eps_{beta)gamma delta}  ->  one TepsSym atom."""
    out = []
    i = 0
    while i < len(atoms):
        a = atoms[i]
        if a.kind == "Tensor" and a.name == "T" and a.extra.get("sym_open"):
            if i + 1 >= len(atoms):
                raise ParseError("symmetrised (T^A)_{(alpha} with no epsilon following")
            e = atoms[i + 1]
            if not (e.kind == "Tensor" and e.name == "eps" and ")" in e.sub):
                raise ParseError(f"symmetrised (T^A)_{{(alpha}} must be followed by eps_{{beta)..}}: {e}")
            esub = [x for x in e.sub if x != ")"]
            if len(esub) != 3 or e.sub.index(")") != 1:
                raise ParseError(f"malformed symmetrised colour epsilon {e.sub}")
            m = Atom("TepsSym", name="T", sup=[a.sup[0]])
            m.extra = dict(A=a.sup[0], row=a.extra["row"], col=a.extra["col"], eps=esub)
            out.append(m)
            i += 2
            continue
        out.append(a)
        i += 1
    return out


def _is_paren_T(cur: Cursor) -> bool:
    r"""lookahead for  ( T ^ A )  followed by explicit fundamental indices, the colour
    structure of the B-violating psi^4 X rows:  (T^A)_\gamma^\delta \epsilon_{\delta\alpha\beta}"""
    return (cur.peek(0) == ("name", "T") and cur.peek(1)[0] == "sup"
            and cur.peek(2)[0] in ("name", "lbr") and (cur.peek(3)[0] == "rp" or cur.peek(4)[0] == "rp"))


def _parse_paren_T(cur: Cursor) -> Atom:
    """(T^A)_{lower}^{upper}.  Murphy writes the generator with its column index (the one
    contracted with the fundamental quark) as the LOWER index and the row index (contracted
    with the antitriplet epsilon d u) as the UPPER one.  A lower index written as "(alpha"
    opens a symmetrisation with the following epsilon, closed by ")" there:
        (T^A)_{(alpha}^delta eps_{beta)gamma delta} = 1/2 [T_alpha^delta eps_{beta gamma delta}
                                                          + T_beta^delta eps_{alpha gamma delta}]"""
    cur.next()  # T
    cur.next()  # ^
    adj = read_group(cur)
    kind, val = cur.next()
    if kind != "rp" or len(adj) != 1:
        raise ParseError(f"malformed (T^A): {adj}")
    a = Atom("Tensor", name="T", sup=[adj[0]])
    parse_indices(cur, a)   # a.sub = lower (column), a.sup = [A] + upper (row)
    lower = [x for x in a.sub if x != "("]
    upper = [x for x in a.sup[1:]]
    if len(lower) != 1 or len(upper) != 1:
        raise ParseError(f"(T^A) needs one lower and one upper fundamental index: {a.sub} {a.sup}")
    a.extra = dict(col=lower[0], row=upper[0], sym_open=("(" in a.sub))
    a.sub, a.sup = [], [adj[0]]
    return a


def _is_eps_tau(cur: Cursor) -> bool:
    r"""lookahead for  ( \epsilon \tau ^ I )  or  ( \tau ^ I \epsilon )  followed by _{jk}"""
    k1, v1 = cur.peek(0)
    k2, v2 = cur.peek(1)
    return (k1 == "cmd" and k2 == "cmd" and {v1, v2} == {"\\epsilon", "\\tau"}) or \
           (k1 == "cmd" and v1 == "\\epsilon" and k2 == "cmd" and v2 == "\\tau") or \
           (k1 == "cmd" and v1 == "\\tau" and k2 == "sup")


def _parse_eps_tau(cur: Cursor) -> Atom:
    order = []
    adj = None
    while True:
        kind, val = cur.next()
        if kind == "rp":
            break
        if kind == "cmd" and val == "\\epsilon":
            order.append("eps")
        elif kind == "cmd" and val == "\\tau":
            order.append("tau")
            k, v = cur.peek()
            if k == "sup":
                cur.next()
                adj = read_group(cur)[0]
        elif kind is None:
            raise ParseError("unterminated (eps tau)")
        else:
            raise ParseError(f"unexpected {val} in (eps tau)")
    a = Atom("EpsTau", name="".join(order))
    a.sup = [adj] if adj else []
    parse_indices(cur, a)
    if order not in (["eps", "tau"], ["tau", "eps"]) or adj is None or len(a.sub) != 2:
        raise ParseError(f"malformed (eps tau): {order} {adj} {a.sub}")
    return a


def parse_indices(cur: Cursor, a: Atom):
    """Consume any number of ^{...} / _{...} after an atom."""
    while True:
        kind, val = cur.peek()
        if kind == "sup":
            cur.next()
            a.sup += split_indices(read_group(cur))
        elif kind == "sub":
            cur.next()
            a.sub += split_indices(read_group(cur))
        else:
            break


def parse_deriv(cur: Cursor) -> Atom:
    a = Atom("D")
    parse_indices(cur, a)
    # symmetrised pair  D_{(\mu} D_{\nu)}
    if a.sub and a.sub[0] == "(":
        # expect  D _{(mu}  then  D _{nu)}
        mu = a.sub[1]
        kind, val = cur.next()
        if not (kind == "name" and val == "D"):
            raise ParseError("expected second D in symmetrised pair")
        b = Atom("D")
        parse_indices(cur, b)
        if not (b.sub and b.sub[-1] == ")"):
            raise ParseError("expected closing ) in symmetrised derivative")
        nu = b.sub[0]
        a.sub = []
        a.sym = (mu, nu)
    return a


def parse_one(cur: Cursor, bar=False, tilde=False) -> Atom:
    kind, val = cur.next()
    if kind == "lbr":  # \bar{l} style
        inner = read_group_from_open(cur)
        kind, val = "name", inner
    if kind == "name" and val in ("G", "W", "B"):
        a = Atom("FS", name=val, tilde=tilde)
    elif kind == "name" and val == "H":
        a = Atom("H", name="H", tilde=tilde)
    elif kind == "name" and val == "d" and not bar and cur.peek()[0] == "sup":
        # d^{ABC}: distinguished from the down quark d_p (which carries a subscript) by the
        # superscript of adjoint indices
        a = Atom("Tensor", name="d")
    elif kind == "name" and val in FERMION_NAMES:
        a = Atom("Psi", name=val, bar=bar)
    elif kind == "cmd" and val == "\\gamma":
        a = Atom("Gamma", name="ga")
    elif kind == "cmd" and val == "\\sigma":
        a = Atom("Gamma", name="sig")
    elif kind == "cmd" and val == "\\tau":
        a = Atom("Tensor", name="tau")
    elif kind == "name" and val == "T":
        a = Atom("Tensor", name="T")
    elif kind == "name" and val == "f":
        a = Atom("Tensor", name="f")
    elif kind == "cmd" and val == "\\epsilon":
        a = Atom("Tensor", name="eps")
    elif kind == "cmd" and val == "\\dag":
        raise ParseError("dangling \\dag")
    else:
        raise ParseError(f"unknown atom {kind} {val!r}")
    parse_indices(cur, a)
    # H^\dag / \widetilde H^\dag : the dagger appears as a sup token
    if "\\dag" in a.sup or "\\dagger" in a.sup:
        a.dag = True
        a.sup = [x for x in a.sup if x not in ("\\dag", "\\dagger")]
    # the case "d" quark vs d-symbol: d_p is a quark
    if a.kind == "Tensor" and a.name == "d" and not a.sup:
        a = Atom("Psi", name="d", bar=bar, sub=a.sub)
    return a


def read_group_from_open(cur: Cursor) -> str:
    depth = 1
    buf = ""
    while True:
        kind, val = cur.next()
        if kind is None:
            raise ParseError("unbalanced {")
        if kind == "lbr":
            depth += 1
        elif kind == "rbr":
            depth -= 1
            if depth == 0:
                return buf
        buf += val
    return buf


# --------------------------------------------------------------------------------------
# semantic resolution  (atoms -> DSL terms)
# --------------------------------------------------------------------------------------
# This is the part with physics content: it decides which implicit indices contract with
# what.  Implemented for the bracket conventions seen in the tables; every unhandled
# situation raises ParseError so that coverage is measured honestly.


def classify_index(tok: str, where: str) -> str:
    if tok in SU2A:
        return "su2a"
    if tok in SU3A:
        return "su3a"
    if tok in SU2F:
        return "su2f"
    if tok in GEN:
        return "gen"
    if tok in SU3F and where in ("Psi", "eps3"):
        return "su3f"
    if tok in GREEK_LOR or tok in SU3F:
        return "lor"
    raise ParseError(f"cannot classify index {tok!r} on {where}")


def resolve(atoms: List[Atom]) -> List[Term]:
    """Top-level: a product of items, where an item may be a bracketed sum.  Returns the
    expanded list of DSL terms."""
    items, pos = parse_sum(atoms, 0, top=True)
    if pos != len(atoms):
        raise ParseError(f"trailing atoms at {pos}: {atoms[pos:]}")
    return items


# The intermediate representation for an item is a list of "pieces" (sums of products of
# Factor lists), kept as lists of Terms with *unresolved* gauge slots stored in the
# Factor objects using placeholder index names '?su2', '?su3' that the contraction pass
# then ties together.

Piece = List[Term]


def parse_sum(atoms, pos, top=False, bracket=None) -> Tuple[Piece, int]:
    terms: Piece = []
    sign = 1
    cur_prod, pos = parse_product(atoms, pos, bracket)
    terms += cur_prod
    while pos < len(atoms) and atoms[pos].kind in ("plus", "minus"):
        sign = 1 if atoms[pos].kind == "plus" else -1
        nxt, pos = parse_product(atoms, pos + 1, bracket)
        terms += scale(sign, nxt)
    return terms, pos


def parse_product(atoms, pos, bracket=None) -> Tuple[Piece, int]:
    factors_pieces: List[Piece] = []
    coeff = C.of(1)
    pending_deriv: List[Atom] = []
    while pos < len(atoms):
        a = atoms[pos]
        if a.kind == "close":
            break
        if a.kind in ("plus", "minus"):
            break
        if a.kind == "i":
            coeff = coeff * I
            pos += 1
            continue
        if a.kind == "num":
            coeff = coeff * int(a.name)
            pos += 1
            continue
        if a.kind == "open":
            inner, pos2 = parse_sum(atoms, pos + 1, bracket=a.bracket)
            if not (pos2 < len(atoms) and atoms[pos2].kind == "close"):
                raise ParseError("unbalanced bracket")
            pos = pos2 + 1
            power = 1
            if pos < len(atoms) and atoms[pos].kind == "power":
                power = int(atoms[pos].name)
                pos += 1
            inner = mark_bracket(inner, a.bracket)
            if pending_deriv:
                if power != 1:
                    raise ParseError("derivative of a bracket power")
                inner = apply_derivs(inner, pending_deriv)
                pending_deriv = []
            factors_pieces.append(inner)
            for _ in range(power - 1):  # a bracket raised to a power is a scalar: copies get fresh dummies
                factors_pieces.append(relabel(inner))
            continue
        if a.kind == "D":
            pending_deriv.append(a)
            pos += 1
            continue
        if a.kind == "Dlr":
            # Hermitian derivative acting on the *next* field: (psibar Gamma Dlr psi) handled
            # inside bilinear resolution; here we store it as a marker piece
            factors_pieces.append([T(1, DlrMarker(a))])
            pos += 1
            continue
        # plain atom
        piece = atom_to_piece(a)
        if pending_deriv:
            piece = apply_derivs(piece, pending_deriv)
            pending_deriv = []
        factors_pieces.append(piece)
        pos += 1
    if pending_deriv:
        raise ParseError("derivative with nothing to act on")
    out = prod(*factors_pieces) if factors_pieces else [T(1)]
    return scale(coeff, out), pos


# ---- marker factors used during resolution -------------------------------------------


@dataclass(frozen=True)
class DlrMarker:
    atom: Atom

    def slots(self):
        return ()

    def identities(self):
        return []

    def conj(self):
        return self

    def latex(self):
        return r"\overleftrightarrow{D}"

    def fr(self, ctx):
        raise ParseError("unresolved Dlr marker")

    grassmann = False


@dataclass(frozen=True)
class Bracket:
    """Bracket boundary marker so that the contraction pass knows bilinear extents."""

    kind: str  # '(' or '[' ; 'open'/'close'
    which: str

    def slots(self):
        return ()

    def identities(self):
        return []

    def conj(self):
        return self

    def latex(self):
        return ""

    def fr(self, ctx):
        return ""

    grassmann = False


def relabel(piece: Piece) -> Piece:
    """Return a copy of the piece with every index renamed to a fresh name (placeholders
    keep their '?' prefix).  Used for powers of brackets."""
    out = []
    for t in piece:
        names = {}
        for f in t.factors:
            for n, _ in f.slots():
                if n not in names:
                    names[n] = fresh("?r") if n.startswith("?") else fresh("r")
        out.append(Term(t.coeff, tuple(rename_factor(f, names) for f in t.factors)))
    return out


def rename_factor(f, names):
    if isinstance(f, Bracket):
        return f
    if isinstance(f, FS):
        return FS(f.group, names[f.mu], names[f.nu], names[f.adj] if f.adj else None, f.dual, tuple(names[d] for d in f.derivs))
    if isinstance(f, H):
        return H(names[f.j], f.dag, tuple(names[d] for d in f.derivs))
    if isinstance(f, Psi):
        return Psi(f.name, names[f.sp], f.bar, names[f.su2] if f.su2 else None, names[f.col] if f.col else None, names[f.gen], tuple(names[d] for d in f.derivs), f.cc)
    if isinstance(f, Gamma):
        return Gamma(f.kind, tuple(names[l] for l in f.lor), names[f.sp1], names[f.sp2])
    if isinstance(f, Tensor):
        return Tensor(f.kind, tuple(names[i] for i in f.idx))
    return f


def mark_bracket(piece: Piece, br: str) -> Piece:
    return [Term(t.coeff, (Bracket(br, "open"),) + t.factors + (Bracket(br, "close"),)) for t in piece]


def atom_to_piece(a: Atom) -> Piece:
    """Convert a single atom into a one-term piece with explicit indices where given and
    placeholder indices ('?') where the table leaves them implicit."""
    if a.kind == "FS":
        lor = [x for x in a.sub + a.sup if x in GREEK_LOR or x in SU3F]
        adj = [x for x in a.sub + a.sup if x in SU2A or x in SU3A]
        if len(lor) != 2:
            raise ParseError(f"field strength {a} needs two Lorentz indices, got {lor}")
        if a.name == "B":
            f = FS("B", lor[0], lor[1], dual=a.tilde)
        else:
            if len(adj) != 1:
                raise ParseError(f"field strength {a.name} needs an adjoint index")
            f = FS(a.name, lor[0], lor[1], adj=adj[0], dual=a.tilde)
        return [T(1, f)]
    if a.kind == "H":
        su2 = [x for x in a.sub + a.sup if x in SU2F]
        j = su2[0] if su2 else fresh("?h")
        if a.tilde:
            # Htilde_j = eps_{jk} H^{dag k};  Htilde^dag^j = eps^{jk} H_k  (numerically the same eps)
            k = fresh("k")
            if a.dag:
                return [T(1, Tensor("epsSU2", (j, k)), H(k, dag=False))]
            return [T(1, Tensor("epsSU2", (j, k)), H(k, dag=True))]
        return [T(1, H(j, dag=a.dag))]
    if a.kind == "Psi":
        gen = [x for x in a.sub if x in GEN]
        if len(gen) != 1:
            raise ParseError(f"fermion {a.name} needs one flavour index, got {a.sub}")
        su2 = [x for x in a.sub + a.sup if x in SU2F]
        col = [x for x in a.sub + a.sup if x in SU3F]
        from dsl import FERMIONS

        info = FERMIONS[a.name]
        s2 = (su2[0] if su2 else fresh("?j")) if info["su2"] else None
        c3 = (col[0] if col else fresh("?a")) if info["col"] else None
        return [T(1, Psi(a.name, fresh("s"), bar=a.bar, su2=s2, col=c3, gen=gen[0]))]
    if a.kind == "Gamma":
        lor = [x for x in a.sub + a.sup if x in GREEK_LOR]
        if a.name == "ga" and len(lor) == 1:
            return [T(1, Gamma("ga", (lor[0],), "?s1", "?s2"))]
        if a.name == "sig" and len(lor) == 2:
            return [T(1, Gamma("sig", (lor[0], lor[1]), "?s1", "?s2"))]
        raise ParseError(f"gamma structure {a}")
    if a.kind == "Tensor":
        idx = a.sub + a.sup
        if a.name == "tau":
            if len(idx) != 1 or idx[0] not in SU2A:
                raise ParseError(f"tau needs one adjoint index: {a}")
            return [T(1, Tensor("tau", (idx[0], fresh("?j"), fresh("?j"))))]
        if a.name == "T":
            if len(idx) != 1 or idx[0] not in SU3A:
                raise ParseError(f"T needs one adjoint index: {a}")
            if a.extra.get("row"):
                # explicit (T^A)_col^row: slot 1 is the row (contracted with the antitriplet),
                # slot 2 the column (contracted with the fundamental quark), as in FeynRules'
                # T[A, i, j] for  ubar[i] T[A,i,j] u[j]
                return [T(1, Tensor("T", (idx[0], a.extra["row"], a.extra["col"])))]
            return [T(1, Tensor("T", (idx[0], fresh("?a"), fresh("?a"))))]
        if a.name in ("f", "d"):
            if len(idx) != 3:
                raise ParseError(f"{a.name} needs three indices: {a}")
            return [T(1, Tensor(a.name, tuple(idx)))]
        if a.name == "eps":
            if len(idx) == 3 and all(x in SU2A for x in idx):
                return [T(1, Tensor("epsIJK", tuple(idx)))]
            if len(idx) == 2 and all(x in SU2F for x in idx):
                return [T(1, Tensor("epsSU2", tuple(idx)))]
            if len(idx) == 3 and all(x in SU3F for x in idx):
                return [T(1, Tensor("epsSU3", tuple(idx)))]
            raise ParseError(f"epsilon with indices {idx}")
    if a.kind == "EpsTau":
        j, k = a.sub
        m = fresh("m")
        I_ = a.sup[0]
        if a.name == "epstau":   # (eps tau^I)_{jk} = eps_{jm} (tau^I)_m^k
            return [T(1, Tensor("epsSU2", (j, m)), Tensor("tau", (I_, m, k)))]
        else:                    # (tau^I eps)_{jk} = (tau^I)_j^m eps_{mk}
            return [T(1, Tensor("tau", (I_, j, m)), Tensor("epsSU2", (m, k)))]
    if a.kind == "C":
        return [T(1, ChargeConj())]
    if a.kind == "TepsSym":
        A, row, col = a.extra["A"], a.extra["row"], a.extra["col"]
        b, g, d = a.extra["eps"]
        if d != row:
            raise ParseError(f"symmetrised colour structure: T's upper index {row} must be summed with the epsilon {a.extra['eps']}")
        from fractions import Fraction
        half = C(Fraction(1, 2))
        return [T(half, Tensor("T", (A, row, col)), Tensor("epsSU3", (b, g, d))),
                T(half, Tensor("T", (A, row, b)), Tensor("epsSU3", (col, g, d)))]
    raise ParseError(f"cannot convert atom {a}")


@dataclass(frozen=True)
class ChargeConj:
    def slots(self):
        return ()

    def identities(self):
        return []

    def conj(self):
        return self

    def latex(self):
        return "C"

    def fr(self, ctx):
        raise ParseError("charge conjugation not yet supported in emission")

    grassmann = False


def apply_derivs(piece: Piece, derivs: List[Atom]) -> Piece:
    """D_mu (X) : Leibniz over every field in X (fields inside brackets are all hit).  For a
    single-field piece this just adds the derivative to that field."""
    out = piece
    for d in reversed(derivs):  # innermost derivative first
        if d.sym is not None:
            # D_{(mu} D_{nu)} = 1/2 (D_mu D_nu + D_nu D_mu)
            mu, nu = d.sym
            a = leibniz(leibniz(out, nu), mu)
            b = leibniz(leibniz(out, mu), nu)
            out = scale(C.of(1) * C(__import__("fractions").Fraction(1, 2)), a + b)
        else:
            idx = [x for x in d.sub + d.sup if x in GREEK_LOR or x in SU3F]
            adj = [x for x in d.sub + d.sup if x in SU2A]
            if len(idx) != 1:
                raise ParseError(f"derivative needs one Lorentz index: {d}")
            if adj:
                raise ParseError("D^I (adjoint Hermitian derivative) must be Dlr")
            out = leibniz(out, idx[0])
    return out


def leibniz(piece: Piece, mu: str) -> Piece:
    out: Piece = []
    for t in piece:
        fields = [i for i, f in enumerate(t.factors) if isinstance(f, (FS, H, Psi))]
        if not fields:
            raise ParseError("derivative acting on no field")
        for i in fields:
            f = t.factors[i]
            nf = type(f)(**{**f.__dict__, "derivs": f.derivs + (mu,)}) if not isinstance(f, FS) else FS(f.group, f.mu, f.nu, f.adj, f.dual, f.derivs + (mu,))
            out.append(Term(t.coeff, t.factors[:i] + (nf,) + t.factors[i + 1 :]))
    return out


# --------------------------------------------------------------------------------------
# contraction pass: resolve '?'-placeholders and Dlr markers inside each term
# --------------------------------------------------------------------------------------


def contract(terms: List[Term]) -> List[Term]:
    out: List[Term] = []
    for t in terms:
        for tt in expand_dlr(t):
            out.append(tie_indices(tt))
    return out


def expand_dlr(t: Term) -> List[Term]:
    """(psibar Gamma Dlr^{(I)}_mu psi) -> psibar Gamma (tau^I) (D psi) - (D psibar) Gamma (tau^I) psi.
    The marker sits between Gamma (or psibar) and psi."""
    idxs = [i for i, f in enumerate(t.factors) if isinstance(f, DlrMarker)]
    if not idxs:
        return [t]
    i = idxs[0]
    m: DlrMarker = t.factors[i]  # type: ignore[assignment]
    a = m.atom
    lor = [x for x in a.sub + a.sup if x in GREEK_LOR]
    adj = [x for x in a.sub + a.sup if x in SU2A]
    if len(lor) != 1:
        raise ParseError(f"Dlr needs one Lorentz index: {a}")
    mu = lor[0]
    # Higgs case:  X Dlr Y with X, Y Higgs covariants (H^dag, or eps H for Htilde^dag) :
    #   X Dlr_mu Y = X (D_mu Y) - (D_mu X) Y ; the derivative acts on the Higgs field inside X
    left_h = next((j for j in range(i - 1, -1, -1) if isinstance(t.factors[j], H)), None)
    right_h = i + 1 if i + 1 < len(t.factors) and isinstance(t.factors[i + 1], H) else None
    between_ok = left_h is not None and all(isinstance(t.factors[j], Tensor) and t.factors[j].kind == "epsSU2" for j in range(left_h + 1, i))
    if right_h is not None and between_ok:
        hb, h = t.factors[left_h], t.factors[right_h]
        fac = list(t.factors)
        tau_factors = (Tensor("tau", (adj[0], fresh("?j"), fresh("?j"))),) if adj else ()
        f1 = fac[:i] + list(tau_factors) + [H(h.j, h.dag, h.derivs + (mu,))] + fac[i + 2 :]
        f2 = fac[:left_h] + [H(hb.j, hb.dag, hb.derivs + (mu,))] + fac[left_h + 1 : i] + list(tau_factors) + [h] + fac[i + 2 :]
        return expand_dlr(Term(t.coeff, tuple(f1))) + expand_dlr(Term(-t.coeff, tuple(f2)))
    # find the psi after and the psibar before (same bilinear, i.e. within the innermost bracket)
    after = next((j for j in range(i + 1, len(t.factors)) if isinstance(t.factors[j], Psi)), None)
    before = next((j for j in range(i - 1, -1, -1) if isinstance(t.factors[j], Psi)), None)
    if after is None or before is None:
        raise ParseError("Dlr not inside a bilinear")
    fac = list(t.factors)
    del fac[i]
    after -= 1
    tau_factors: Tuple = ()
    if adj:
        tau_factors = (Tensor("tau", (adj[0], fresh("?j"), fresh("?j"))),)
    psi: Psi = fac[after]  # type: ignore[assignment]
    psib: Psi = fac[before]  # type: ignore[assignment]
    f1 = fac[:after] + list(tau_factors) + [Psi(**{**psi.__dict__, "derivs": psi.derivs + (mu,)})] + fac[after + 1 :]
    f2 = fac[:before] + [Psi(**{**psib.__dict__, "derivs": psib.derivs + (mu,)})] + fac[before + 1 : after] + list(tau_factors) + [psi] + fac[after + 1 :]
    t1 = Term(t.coeff, tuple(f1))
    t2 = Term(-t.coeff, tuple(f2))
    return expand_dlr(t1) + expand_dlr(t2)


def tie_indices(t: Term) -> Term:
    """Resolve placeholder indices:
    * spinor '?s1','?s2' on a Gamma: tie to the psibar before and psi after it; a bilinear
      with no Gamma gets an identity Gamma.
    * SU(2) '?h' / '?j' on H, fermion doublets and tau: inside a bracket, psibar-tau-psi
      contract in order; a doublet fermion bilinear without tau contracts psibar with psi;
      an uncontracted doublet fermion contracts with the nearest Higgs-type object to the
      right (H, Htilde, tau H ...), matching Murphy's convention.
    * SU(3) '?a' on T and quarks likewise.
    The procedure is deliberately explicit; if a placeholder remains it is an error."""
    fac = list(t.factors)
    # --- spinors and bilinear extents --------------------------------------------------
    # bilinears are (psibar ... psi) pairs in order
    psis = [i for i, f in enumerate(fac) if isinstance(f, Psi)]
    if len(psis) % 2:
        raise ParseError("odd number of fermion fields")
    pairs = [(psis[k], psis[k + 1]) for k in range(0, len(psis), 2)]
    for (ib, ia) in pairs:
        pb, pa = fac[ib], fac[ia]
        if not pb.bar and not pa.bar and not pb.cc:
            # (psi C Gamma chi) = psi^T C Gamma chi: the left field becomes the transposed
            # member (FeynRules CC[psibar]); the explicit C symbol must be present.
            ccs = [j for j in range(ib + 1, ia) if isinstance(fac[j], ChargeConj)]
            if len(ccs) != 1:
                raise ParseError("two unbarred fermions without a single C between them")
            fac[ib] = replace(pb, cc=True)
            del fac[ccs[0]]
            return tie_indices(Term(t.coeff, tuple(fac)))
        if not ((pb.bar or pb.cc) and not pa.bar):
            raise ParseError("bilinear is not psibar ... psi")
        gam = [j for j in range(ib + 1, ia) if isinstance(fac[j], Gamma)]
        if len(gam) > 1:
            raise ParseError("more than one Dirac structure in a bilinear")
        if gam:
            g: Gamma = fac[gam[0]]  # type: ignore[assignment]
            fac[gam[0]] = Gamma(g.kind, g.lor, pb.sp, pa.sp)
        else:
            fac.insert(ia, Gamma("1", (), pb.sp, pa.sp))
            # re-index
            return tie_indices(Term(t.coeff, tuple(fac)))
    # --- SU(2) fundamental ---------------------------------------------------------------
    fac = tie_gauge(fac, "su2", pairs_of(fac))
    fac = tie_gauge(fac, "su3", pairs_of(fac))
    # --- leftover placeholders -> error ----------------------------------------------------
    for f in fac:
        for n, _ in f.slots():
            if n.startswith("?"):
                raise ParseError(f"unresolved index {n} on {f}")
        if isinstance(f, ChargeConj):
            raise ParseError("C outside a (psi C chi) bilinear")
    fac = [f for f in fac if not isinstance(f, Bracket)]
    return Term(t.coeff, tuple(fac))


def pairs_of(fac):
    psis = [i for i, f in enumerate(fac) if isinstance(f, Psi)]
    return [(psis[k], psis[k + 1]) for k in range(0, len(psis), 2)]


def _slot(f, kind):
    """Return the list of (attr-or-position) placeholders of a given gauge kind on a factor."""
    if kind == "su2":
        if isinstance(f, H):
            return [("j",)] if f.j.startswith("?") else []
        if isinstance(f, Psi):
            return [("su2",)] if (f.su2 and f.su2.startswith("?")) else []
        if isinstance(f, Tensor) and f.kind == "tau":
            return [("idx", 1), ("idx", 2)] if f.idx[1].startswith("?") else []
        if isinstance(f, Tensor) and f.kind == "epsSU2":
            return [("idx", k) for k in (0, 1) if f.idx[k].startswith("?")]
    if kind == "su3":
        if isinstance(f, Psi):
            return [("col",)] if (f.col and f.col.startswith("?")) else []
        if isinstance(f, Tensor) and f.kind == "T":
            return [("idx", 1), ("idx", 2)] if f.idx[1].startswith("?") else []
    return []


def _set(f, slot, name):
    if slot[0] == "idx":
        idx = list(f.idx)
        idx[slot[1]] = name
        return Tensor(f.kind, tuple(idx))
    return type(f)(**{**f.__dict__, slot[0]: name})


def tie_gauge(fac, kind, pairs):
    """Contract placeholders of one gauge kind.  Strategy, per bilinear (ib, ia):
      chain = [psibar] + generators between them + [psi]; contract sequentially.
    Then, left-over single placeholders on fermions contract with the nearest Higgs/tau-H
    object to the right within the same bracket (or anywhere to the right if none)."""
    fac = list(fac)
    # 1. inside bilinears
    for (ib, ia) in pairs:
        chain = [ib] + [j for j in range(ib + 1, ia) if isinstance(fac[j], Tensor) and _slot(fac[j], kind)] + [ia]
        # psibar slot, tensor slots (in, out), psi slot
        if len(chain) == 2:
            sb, sa = _slot(fac[ib], kind), _slot(fac[ia], kind)
            if sb and sa:
                nm = fresh("c")
                fac[ib] = _set(fac[ib], sb[0], nm)
                fac[ia] = _set(fac[ia], sa[0], nm)
        else:
            prev = ib
            prev_slot = _slot(fac[ib], kind)
            if not prev_slot:
                raise ParseError(f"{kind} generator inside bilinear but psibar has no {kind} index")
            prev_slot = prev_slot[0]
            for j in chain[1:-1]:
                nm = fresh("c")
                fac[prev] = _set(fac[prev], prev_slot, nm)
                fac[j] = _set(fac[j], ("idx", 1), nm)
                prev, prev_slot = j, ("idx", 2)
            sa = _slot(fac[ia], kind)
            if not sa:
                raise ParseError(f"{kind} generator inside bilinear but psi has no {kind} index")
            nm = fresh("c")
            fac[prev] = _set(fac[prev], prev_slot, nm)
            fac[ia] = _set(fac[ia], sa[0], nm)
    # 2. remaining placeholders: contract left-to-right with tau/H objects outside bilinears
    if kind == "su2":
        fac = tie_su2_external(fac)
    else:
        fac = tie_su3_external(fac)
    return fac


def tie_su2_external(fac):
    """Handles: (psibar_j ... psi) H^j ;  (psibar ... psi) tau^I H ;  (H^dag tau^I H) ;
    (H^dag H) ; (D H^dag tau^I D H) ; eps_{jk} (...) ; H ... bilinear ... Htilde etc."""
    # collect open slots in order
    def open_slots():
        return [(i, s) for i, f in enumerate(fac) for s in _slot(f, "su2")]

    guard = 0
    while open_slots():
        guard += 1
        if guard > 50:
            raise ParseError("SU(2) contraction did not converge")
        slots = open_slots()
        i, s = slots[0]
        f = fac[i]
        # a tau^I with both slots open: (X tau Y) -> X_j tau_j^k Y_k with X the nearest open
        # slot to the left and Y the nearest open slot to the right
        if isinstance(f, Tensor) and f.kind == "tau":
            left = [(k, ss) for (k, ss) in slots if k < i]
            right = [(k, ss) for (k, ss) in slots if k > i and not (isinstance(fac[k], Tensor) and fac[k].kind == "tau")]
            if not left or not right:
                raise ParseError("tau with no neighbours to contract")
            kl, sl = left[-1]
            kr, sr = right[0]
            n1, n2 = fresh("c"), fresh("c")
            fac[kl] = _set(fac[kl], sl, n1)
            fac[i] = Tensor("tau", (f.idx[0], n1, n2))
            fac[kr] = _set(fac[kr], sr, n2)
            continue
        # a field with an open slot: partner = next open non-tau slot to the right,
        # unless a tau sits between (then the tau rule above fires first when we reach it)
        right = [(k, ss) for (k, ss) in slots if k > i]
        if not right:
            raise ParseError(f"unpaired SU(2) index on {f}")
        kr, sr = right[0]
        if isinstance(fac[kr], Tensor) and fac[kr].kind == "tau":
            # let the tau rule handle it: process the tau now
            fr = fac[kr]
            right2 = [(k, ss) for (k, ss) in slots if k > kr and not (isinstance(fac[k], Tensor) and fac[k].kind == "tau")]
            if not right2:
                raise ParseError("tau with no right neighbour")
            k2, s2 = right2[0]
            n1, n2 = fresh("c"), fresh("c")
            fac[i] = _set(fac[i], s, n1)
            fac[kr] = Tensor("tau", (fr.idx[0], n1, n2))
            fac[k2] = _set(fac[k2], s2, n2)
            continue
        nm = fresh("c")
        fac[i] = _set(fac[i], s, nm)
        fac[kr] = _set(fac[kr], sr, nm)
    return fac


def tie_su3_external(fac):
    def open_slots():
        return [(i, s) for i, f in enumerate(fac) for s in _slot(f, "su3")]

    guard = 0
    while open_slots():
        guard += 1
        if guard > 50:
            raise ParseError("SU(3) contraction did not converge")
        slots = open_slots()
        i, s = slots[0]
        right = [(k, ss) for (k, ss) in slots if k > i]
        if not right:
            raise ParseError(f"unpaired SU(3) index on {fac[i]}")
        kr, sr = right[0]
        nm = fresh("c")
        fac[i] = _set(fac[i], s, nm)
        fac[kr] = _set(fac[kr], sr, nm)
    return fac


# --------------------------------------------------------------------------------------
# public API
# --------------------------------------------------------------------------------------


def parse_operator(latex: str, name: str, wc: str, cls: int, **kw) -> Operator:
    atoms = parse_atoms(latex)
    terms = resolve(atoms)
    terms = contract(terms)
    # flavour indices present, in order
    gens = []
    for t in terms[:1]:
        for f in t.factors:
            if isinstance(f, Psi):
                gens.append(f.gen)
    return Operator(name=name, wc=wc, terms=terms, cls=cls, gens=tuple(gens), **kw)


def wc_name(label: str) -> str:
    """Q_{q^2 B H^2 D}^{(3)}  ->  c8q2BH2Dx3"""
    m = re.match(r"Q_\{(.+?)\}(?:\^\{\((\w+)\)\})?", label)
    if not m:
        raise ParseError(f"bad label {label}")
    body = re.sub(r"[\\^{} ]", "", m.group(1)).replace("tilde", "t")
    n = m.group(2)
    return "c8" + body + (f"x{n}" if n else "")
