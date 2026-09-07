"""
dim8auto.gen.dsl
=================

A small term algebra for SMEFT operators built from covariant building blocks.

An ``Operator`` is a sum of ``Term``s.  A ``Term`` is a numerical coefficient times
an ordered list of ``Factor``s.  Every factor carries *abstract* indices (strings such
as "mu", "I", "j", "A", "alpha", "p").  Index *types* are inferred from the slot they
occupy in a factor, so the author never has to declare them.  Contractions are
implicit: an index name that appears twice in a term is summed over.

The design goals are

* the encoding should read like the published operator (Murphy, arXiv:2005.00059),
* every factor knows how to render itself to FeynRules and to LaTeX, so that the same
  object can be (i) emitted as a model file and (ii) diffed against the source table,
* composite objects that the paper writes compactly (Hermitian derivatives, dual field
  strengths, derivatives of products, H-tilde) are expanded here, *once*, under test.

Index types
-----------
lor   Lorentz vector index
su2a  SU(2)_w adjoint (I, J, K)
su2f  SU(2)_w fundamental (j, k, m, n)
su3a  SU(3)_c adjoint (A, B, C)
su3f  SU(3)_c fundamental (alpha, beta, gamma)
sp    Dirac spinor index (internal, never written by the author)
gen   generation / flavour index (p, r, s, t)

Conventions (Murphy 2005.00059, Sec. 2)
---------------------------------------
tau^I = Pauli matrices, t^I = tau^I/2 ; FeynRules' ``Ta[a,i,j]`` is sigma/2, so
tau^I -> 2 Ta.  Dual: Xtilde_{mu nu} = 1/2 eps_{mu nu rho sigma} X^{rho sigma} with
eps_{0123} = +1.  Htilde_j = eps_{jk} H^{dagger k}, eps_{12} = +1.
i H^dag Dlr_mu H = i H^dag (D_mu H) - i (D_mu H^dag) H.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from fractions import Fraction
from itertools import count
from typing import Iterable, List, Optional, Sequence, Tuple, Union

# --------------------------------------------------------------------------------------
# numbers: we keep exact rationals with an optional factor of i, so coefficients are
# (re, im) pairs of Fractions.  Enough for everything in the basis.
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class C:
    """Exact complex rational  re + i*im."""

    re: Fraction = Fraction(1)
    im: Fraction = Fraction(0)

    @staticmethod
    def of(x) -> "C":
        if isinstance(x, C):
            return x
        return C(Fraction(x), Fraction(0))

    def __mul__(self, o) -> "C":
        o = C.of(o)
        return C(self.re * o.re - self.im * o.im, self.re * o.im + self.im * o.re)

    __rmul__ = __mul__

    def __neg__(self) -> "C":
        return C(-self.re, -self.im)

    def __add__(self, o) -> "C":
        o = C.of(o)
        return C(self.re + o.re, self.im + o.im)

    def conj(self) -> "C":
        return C(self.re, -self.im)

    def is_zero(self) -> bool:
        return self.re == 0 and self.im == 0

    def fr(self) -> str:
        """FeynRules/Mathematica rendering."""

        def frac(f: Fraction) -> str:
            return str(f.numerator) if f.denominator == 1 else f"({f.numerator}/{f.denominator})"

        if self.im == 0:
            return frac(self.re)
        if self.re == 0:
            if self.im == 1:
                return "I"
            if self.im == -1:
                return "(-I)"
            return f"({frac(self.im)} I)"
        return f"({frac(self.re)} + {frac(self.im)} I)"

    def latex(self) -> str:
        def frac(f: Fraction, with_sign=True) -> str:
            s = "-" if f < 0 else ""
            f = abs(f)
            body = str(f.numerator) if f.denominator == 1 else rf"\tfrac{{{f.numerator}}}{{{f.denominator}}}"
            return s + body

        if self.im == 0:
            return frac(self.re)
        if self.re == 0:
            if self.im == 1:
                return "i"
            if self.im == -1:
                return "-i"
            return frac(self.im) + " i"
        return f"({frac(self.re)} + {frac(self.im)} i)"


I = C(Fraction(0), Fraction(1))
ONE = C()
HALF = C(Fraction(1, 2))


# --------------------------------------------------------------------------------------
# Factors
# --------------------------------------------------------------------------------------

IndexSlots = Tuple[Tuple[str, str], ...]  # ((index_name, index_type), ...)


class Factor:
    """Base class.  Subclasses implement ``slots()`` (index names with their types),
    ``conj()`` (Hermitian conjugate), ``fr(ctx)`` and ``latex()``."""

    def slots(self) -> IndexSlots:
        raise NotImplementedError

    def conj(self) -> "Factor":
        raise NotImplementedError

    def fr(self, ctx: "FRContext") -> str:
        raise NotImplementedError

    def latex(self) -> str:
        raise NotImplementedError

    # Grassmann parity, used to order fermion fields when conjugating
    grassmann: bool = False

    def identities(self) -> List[Tuple[str, str]]:
        """Pairs of indices this factor identifies (Kronecker deltas).  Processed by the
        emitter before any index is named."""
        return []


# ---- gauge field strengths -------------------------------------------------------------

GROUPS = {
    "B": dict(fr="B", adj=None, latex="B"),
    "W": dict(fr="Wi", adj="su2a", latex="W"),
    "G": dict(fr="G", adj="su3a", latex="G"),
}


@dataclass(frozen=True)
class FS(Factor):
    """Field strength X_{mu nu}^{A} possibly with covariant derivatives acting on it
    (``derivs`` is an ordered list of Lorentz indices, outermost last) and possibly dual."""

    group: str
    mu: str
    nu: str
    adj: Optional[str] = None
    dual: bool = False
    derivs: Tuple[str, ...] = ()

    def __post_init__(self):
        assert self.group in GROUPS, self.group
        if GROUPS[self.group]["adj"] is None:
            assert self.adj is None, "B has no adjoint index"
        else:
            assert self.adj is not None, f"{self.group} needs an adjoint index"

    def slots(self) -> IndexSlots:
        s = [(self.mu, "lor"), (self.nu, "lor")]
        if self.adj is not None:
            s.append((self.adj, GROUPS[self.group]["adj"]))
        s += [(d, "lor") for d in self.derivs]
        return tuple(s)

    def conj(self) -> "FS":
        return self  # real fields

    def latex(self) -> str:
        g = GROUPS[self.group]["latex"]
        name = rf"\widetilde{{{g}}}" if self.dual else g
        sup = f"^{{{self.adj}}}" if self.adj else ""
        core = rf"{name}_{{{self.mu}{self.nu}}}{sup}"
        for d in self.derivs:
            core = rf"(D_{{{d}}} {core})"
        return core

    def fr(self, ctx: "FRContext") -> str:
        g = GROUPS[self.group]["fr"]
        mu, nu = ctx.name(self.mu), ctx.name(self.nu)
        adj = f",{ctx.name(self.adj)}" if self.adj else ""
        if self.dual:
            r, s = ctx.fresh("lor"), ctx.fresh("lor")
            core = f"(1/2) Eps[{mu},{nu},{r},{s}] FS[{g},{r},{s}{adj}]"
            # derivatives act on the undualised object; eps is constant so we can wrap
            inner = f"FS[{g},{r},{s}{adj}]"
            for d in self.derivs:
                inner = f"DC[{inner},{ctx.name(d)}]"
            return f"(1/2) Eps[{mu},{nu},{r},{s}] {inner}"
        core = f"FS[{g},{mu},{nu}{adj}]"
        for d in self.derivs:
            core = f"DC[{core},{ctx.name(d)}]"
        return core


# ---- Higgs doublet ----------------------------------------------------------------------


@dataclass(frozen=True)
class H(Factor):
    """Higgs doublet H^{j} (conj=False) or H^{dagger}_{j} (conj=True), with covariant
    derivatives ``derivs`` (outermost last)."""

    j: str
    dag: bool = False
    derivs: Tuple[str, ...] = ()

    def slots(self) -> IndexSlots:
        return ((self.j, "su2f"),) + tuple((d, "lor") for d in self.derivs)

    def conj(self) -> "H":
        return replace(self, dag=not self.dag)

    def latex(self) -> str:
        core = rf"H^{{\dagger}}_{{{self.j}}}" if self.dag else rf"H^{{{self.j}}}"
        for d in self.derivs:
            core = rf"(D_{{{d}}} {core})"
        return core

    def fr(self, ctx: "FRContext") -> str:
        core = f"{'Phibar' if self.dag else 'Phi'}[{ctx.name(self.j)}]"
        for d in self.derivs:
            core = f"DC[{core},{ctx.name(d)}]"
        return core


# ---- fermions ---------------------------------------------------------------------------

FERMIONS = {
    # murphy name: (FR class, chirality, su2 doublet?, colour?)
    "l": dict(fr="LL", chir="L", su2=True, col=False, latex="l"),
    "e": dict(fr="lR", chir="R", su2=False, col=False, latex="e"),
    "q": dict(fr="QL", chir="L", su2=True, col=True, latex="q"),
    "u": dict(fr="uR", chir="R", su2=False, col=True, latex="u"),
    "d": dict(fr="dR", chir="R", su2=False, col=True, latex="d"),
}


@dataclass(frozen=True)
class Psi(Factor):
    """A chiral fermion field with an (internal) spinor index ``sp``.  ``bar=True`` is the
    Dirac-conjugate field.  ``su2``/``col`` are the gauge indices when applicable, ``gen``
    the flavour index, ``derivs`` covariant derivatives (outermost last)."""

    name: str
    sp: str
    bar: bool = False
    su2: Optional[str] = None
    col: Optional[str] = None
    gen: str = "p"
    derivs: Tuple[str, ...] = ()
    # charge-conjugated member of a (psi C Gamma chi) bilinear (Murphy's B-violating
    # classes 18-21).  cc=True, bar=False is the transposed left field psi^T C, which is
    # \overline{psi^c} and is written CC[psibar] in FeynRules; cc=True, bar=True is the
    # conjugate psi^c = C psibar^T on the right of a bilinear, FeynRules' CC[psi].
    # tests/gen_smoke/cctest.wls: FeynRules' TreatMajoranasAndCC accepts CC[psibar].G.chi
    # chains with explicit spinor indices and its HC[] of them is consistent.
    cc: bool = False
    grassmann = True

    def __post_init__(self):
        info = FERMIONS[self.name]
        assert (self.su2 is not None) == info["su2"], f"{self.name}: su2 index mismatch"
        assert (self.col is not None) == info["col"], f"{self.name}: colour index mismatch"

    def slots(self) -> IndexSlots:
        s: List[Tuple[str, str]] = [(self.sp, "sp")]
        if self.su2 is not None:
            s.append((self.su2, "su2f"))
        if self.col is not None:
            s.append((self.col, "su3f"))
        s.append((self.gen, "gen"))
        s += [(d, "lor") for d in self.derivs]
        return tuple(s)

    def conj(self) -> "Psi":
        return replace(self, bar=not self.bar)

    def latex(self) -> str:
        nm = FERMIONS[self.name]["latex"]
        core = rf"\bar {nm}_{{{self.gen}}}" if self.bar else rf"{nm}_{{{self.gen}}}"
        sup = "".join(x for x in (self.su2, self.col) if x)
        if sup:
            core += f"^{{{sup}}}"
        if self.cc:
            core = (core + " C") if not self.bar else ("C " + core + "^{T}")
        for d in self.derivs:
            core = rf"(D_{{{d}}} {core})"
        return core

    @property
    def opens_chain(self) -> bool:
        """True for the field that starts a Dirac chain in FeynRules' Dot notation:
        a barred field, or the transposed (CC[psibar]) member of a C-bilinear."""
        return self.bar != self.cc

    def fr(self, ctx: "FRContext") -> str:
        info = FERMIONS[self.name]
        cls = info["fr"] + ("bar" if self.opens_chain else "")
        if self.cc:
            cls = f"CC[{cls}]"
        idx = [ctx.name(self.sp)]
        if self.su2 is not None:
            idx.append(ctx.name(self.su2))
        idx.append(ctx.name(self.gen))
        if self.col is not None:
            idx.append(ctx.name(self.col))
        core = f"{cls}[{','.join(idx)}]"
        for d in self.derivs:
            core = f"DC[{core},{ctx.name(d)}]"
        return core


@dataclass(frozen=True)
class Gamma(Factor):
    """Dirac structure between spinor indices sp1, sp2.
    kind: "1" (identity), "ga" (gamma^mu), "sig" (sigma^{mu nu} = i/2 [gamma^mu, gamma^nu]),
    "gaga" (gamma^mu gamma^nu)."""

    kind: str
    lor: Tuple[str, ...]
    sp1: str
    sp2: str

    def slots(self) -> IndexSlots:
        return tuple((l, "lor") for l in self.lor) + ((self.sp1, "sp"), (self.sp2, "sp"))

    def identities(self) -> List[Tuple[str, str]]:
        return [(self.sp1, self.sp2)] if self.kind == "1" else []

    def conj(self) -> "Gamma":
        """gamma^0 Gamma^dag gamma^0 : 1 -> 1, ga -> ga, sig -> sig, gaga -> reversed order.
        The two spinor slots swap as well: (psibar_a Gamma_ab chi_b)^dag = chibar_b Gammabar_ba psi_a,
        so the barred field of the conjugate sits on what was the *second* slot."""
        if self.kind == "gaga":
            return Gamma("gaga", tuple(reversed(self.lor)), self.sp2, self.sp1)
        return Gamma(self.kind, self.lor, self.sp2, self.sp1)

    def latex(self) -> str:
        if self.kind == "1":
            return ""
        if self.kind == "ga":
            return rf"\gamma^{{{self.lor[0]}}}"
        if self.kind == "sig":
            return rf"\sigma^{{{self.lor[0]}{self.lor[1]}}}"
        if self.kind == "gaga":
            return rf"\gamma^{{{self.lor[0]}}} \gamma^{{{self.lor[1]}}}"
        raise ValueError(self.kind)

    def fr(self, ctx: "FRContext") -> str:
        if self.kind == "1":
            return ""  # identity in spinor space: handled by identities()
        a, b = ctx.name(self.sp1), ctx.name(self.sp2)
        if self.kind == "ga":
            return f"Ga[{ctx.name(self.lor[0])},{a},{b}]"
        if self.kind == "sig":
            # FeynRules' Sig with explicit spinor indices silently yields ZERO vertices for
            # same-chirality projector sandwiches (TensDot[ProjP, Sig, ProjP]); verified on
            # FR 2.3.34 and 2.3.49 (tests/gen_smoke/hcdiag*.log).  Emit the definition
            # sigma^{mu nu} = I/2 (Ga^mu Ga^nu - Ga^nu Ga^mu) instead, which works.
            x = ctx.fresh("sp")
            mu_, nu_ = ctx.name(self.lor[0]), ctx.name(self.lor[1])
            return f"(I/2) (Ga[{mu_},{a},{x}] Ga[{nu_},{x},{b}] - Ga[{nu_},{a},{x}] Ga[{mu_},{x},{b}])"
        if self.kind == "gaga":
            c = ctx.fresh("sp")
            return f"Ga[{ctx.name(self.lor[0])},{a},{c}] Ga[{ctx.name(self.lor[1])},{c},{b}]"
        raise ValueError(self.kind)


# ---- invariant tensors ------------------------------------------------------------------


@dataclass(frozen=True)
class Tensor(Factor):
    """Numerical invariant tensors.

    kind and index types:
      tau     (I, j, k)      Pauli matrix  (tau^I)_j^k         -> 2 Ta[I,j,k]
      epsSU2  (j, k)         epsilon_{jk}, eps_{12}=+1         -> Eps[j,k]
      epsIJK  (I, J, K)      epsilon^{IJK}                      -> Eps[I,J,K]
      delSU2  (j, k)         delta_j^k
      T       (A, alpha, beta) Gell-Mann/2                      -> T[A,alpha,beta]
      f       (A, B, C)      f^{ABC}                            -> f[A,B,C]
      d       (A, B, C)      d^{ABC}                            -> dSUN[A,B,C]
      epsSU3  (alpha,beta,gamma) epsilon_{alpha beta gamma}    -> Eps[alpha,beta,gamma]
      delSU3  (alpha, beta)
      delA    (A, B)         delta^{AB}
      epsLor  (mu,nu,rho,sigma) Levi-Civita, eps_{0123}=+1     -> (sign) Eps[mu,nu,rho,sigma]
      g       (mu, nu)       metric
    """

    kind: str
    idx: Tuple[str, ...]

    _types = {
        "tau": ("su2a", "su2f", "su2f"),
        "epsSU2": ("su2f", "su2f"),
        "epsIJK": ("su2a", "su2a", "su2a"),
        "delSU2": ("su2f", "su2f"),
        "T": ("su3a", "su3f", "su3f"),
        "f": ("su3a", "su3a", "su3a"),
        "d": ("su3a", "su3a", "su3a"),
        "epsSU3": ("su3f", "su3f", "su3f"),
        "delSU3": ("su3f", "su3f"),
        "delA": ("su3a", "su3a"),
        "epsLor": ("lor", "lor", "lor", "lor"),
        "g": ("lor", "lor"),
    }

    def __post_init__(self):
        assert self.kind in self._types, self.kind
        assert len(self.idx) == len(self._types[self.kind]), (self.kind, self.idx)

    def slots(self) -> IndexSlots:
        return tuple(zip(self.idx, self._types[self.kind]))

    def identities(self) -> List[Tuple[str, str]]:
        if self.kind in ("delSU2", "delSU3", "delA", "g"):
            return [(self.idx[0], self.idx[1])]
        return []

    def conj(self) -> "Tensor":
        if self.kind == "tau":  # (tau^I)_j^k is Hermitian: conj swaps the two fundamental slots
            I_, j, k = self.idx
            return Tensor("tau", (I_, k, j))
        if self.kind == "T":
            A, a, b = self.idx
            return Tensor("T", (A, b, a))
        return self

    def latex(self) -> str:
        i = self.idx
        k = self.kind
        if k == "tau": return rf"(\tau^{{{i[0]}}})_{{{i[1]}}}^{{{i[2]}}}"
        if k == "epsSU2": return rf"\epsilon_{{{i[0]}{i[1]}}}"
        if k == "epsIJK": return rf"\epsilon^{{{i[0]}{i[1]}{i[2]}}}"
        if k == "delSU2": return rf"\delta_{{{i[0]}}}^{{{i[1]}}}"
        if k == "T": return rf"(T^{{{i[0]}}})_{{{i[1]}}}^{{{i[2]}}}"
        if k == "f": return rf"f^{{{i[0]}{i[1]}{i[2]}}}"
        if k == "d": return rf"d^{{{i[0]}{i[1]}{i[2]}}}"
        if k == "epsSU3": return rf"\epsilon_{{{i[0]}{i[1]}{i[2]}}}"
        if k == "delSU3": return rf"\delta_{{{i[0]}}}^{{{i[1]}}}"
        if k == "delA": return rf"\delta^{{{i[0]}{i[1]}}}"
        if k == "epsLor": return rf"\epsilon_{{{i[0]}{i[1]}{i[2]}{i[3]}}}"
        if k == "g": return rf"g_{{{i[0]}{i[1]}}}"
        raise ValueError(k)

    def fr(self, ctx: "FRContext") -> str:
        n = [ctx.name(x) for x in self.idx]
        if self.kind == "tau":
            return f"2 Ta[{n[0]},{n[1]},{n[2]}]"
        if self.kind in ("epsSU2", "epsIJK", "epsSU3"):
            return f"Eps[{','.join(n)}]"
        if self.kind == "epsLor":
            # FeynRules' Eps[mu,nu,rho,sig] for Lorentz indices: the sign relative to
            # eps_{0123}=+1 is fixed by EPS_LOR_SIGN below (see validate/levi_civita.md).
            return f"({EPS_LOR_SIGN}) Eps[{','.join(n)}]"
        if self.kind in ("delSU2", "delSU3", "delA", "g"):
            return ""  # handled by identities()
        if self.kind == "T":
            return f"T[{n[0]},{n[1]},{n[2]}]"
        if self.kind == "f":
            return f"f[{n[0]},{n[1]},{n[2]}]"
        if self.kind == "d":
            return f"dSUN[{n[0]},{n[1]},{n[2]}]"
        raise ValueError(self.kind)


# Sign relating Murphy's eps_{0123}=+1 (so eps^{0123} = -1) to FeynRules' Eps.
# FeynRules defines Eps[0,1,2,3] with lower-index convention eps_{0123} = +1 ... this is
# verified numerically by validate/levi_civita.wls; until then we keep it symbolic so the
# generated file is self-documenting.
EPS_LOR_SIGN = "epsLorSign"


# --------------------------------------------------------------------------------------
# Terms and operators
# --------------------------------------------------------------------------------------


@dataclass(frozen=True)
class Term:
    coeff: C
    factors: Tuple[Factor, ...]

    def __mul__(self, o: Union[C, int, Fraction, "Term"]) -> "Term":
        if isinstance(o, Term):
            return Term(self.coeff * o.coeff, self.factors + o.factors)
        return Term(self.coeff * C.of(o), self.factors)

    __rmul__ = __mul__

    def __neg__(self) -> "Term":
        return Term(-self.coeff, self.factors)

    def indices(self) -> dict:
        """name -> (type, multiplicity)"""
        out: dict = {}
        for f in self.factors:
            for name, typ in f.slots():
                if name in out:
                    t0, m = out[name]
                    assert t0 == typ, f"index {name} used as {t0} and {typ}"
                    out[name] = (typ, m + 1)
                else:
                    out[name] = (typ, 1)
        return out

    def free_indices(self) -> List[Tuple[str, str]]:
        return [(n, t) for n, (t, m) in self.indices().items() if m == 1 and t != "gen"]

    def check_contracted(self):
        bad = [(n, t, m) for n, (t, m) in self.indices().items() if m != 2 and t != "gen"]
        if bad:
            raise ValueError(f"indices not pairwise contracted: {bad}")

    def hermitian_conjugate(self) -> "Term":
        """(c * f1 f2 ... fn)^dagger = c^* fn^dag ... f1^dag.  Bosonic factors commute, so we
        keep their order and reverse only the relative order of Grassmann fields (which for
        a product of bilinears psi-bar Gamma psi just swaps bar <-> psi inside each bilinear).
        Sign from reordering two fermion fields inside a bilinear: (psibar_a G_ab psi_b)^dag
        = psibar_b (gamma0 G^dag gamma0)_ba psi_a  with no extra sign (standard)."""
        new = [f.conj() for f in self.factors]
        return Term(self.coeff.conj(), tuple(new))

    def latex(self) -> str:
        body = " ".join(f.latex() for f in self.factors if f.latex())
        c = self.coeff.latex()
        if c == "1":
            return body
        if c == "-1":
            return "-" + body
        return f"{c}\\, {body}"


@dataclass
class Operator:
    """A named Lagrangian term Q (a sum of DSL terms), plus bookkeeping."""

    name: str  # Murphy label, e.g. "Q_{q^2H^4D}^{(1)}"
    wc: str  # FeynRules parameter name, e.g. "c8q2H4D1"
    terms: List[Term]
    cls: int  # Murphy class number
    gens: Tuple[str, ...] = ()  # flavour indices in order, e.g. ("p","r")
    hermitian: Optional[bool] = None  # None = decide automatically
    plus_hc: bool = False  # Murphy marks + h.c.
    # how the operator enters the Lagrangian, set by validate/hermiticity.apply_convention:
    #   "real"    L = C Q          C real, Q Hermitian (the factor i is already in Q if the
    #                              published row was anti-Hermitian as typeset)
    #   "complex" L = C Q + h.c.   C complex, Murphy marks + h.c.
    #   "sym"     L = (C/2)(Q + Q^dag)  C real, Q Hermitian only up to integration by parts
    #                              (the 14 class-11 psi^2H^2D^3 rows)
    hc_mode: str = "real"
    cp: str = "even"
    notes: str = ""
    # pairs of flavour indices that are identified under the flavour-universal assumption
    # (one pair per fermion bilinear, in order); derived from ``gens`` if not given
    flavor_pairs: Optional[Tuple[Tuple[str, str], ...]] = None

    def __post_init__(self):
        for t in self.terms:
            t.check_contracted()
        if self.flavor_pairs is None and self.gens:
            assert len(self.gens) % 2 == 0, "odd number of flavour indices"
            self.flavor_pairs = tuple((self.gens[i], self.gens[i + 1]) for i in range(0, len(self.gens), 2))

    def latex(self) -> str:
        parts = [t.latex() for t in self.terms]
        s = parts[0]
        for p in parts[1:]:
            s += (" " + p) if p.startswith("-") else (" + " + p)
        return s

    def field_content(self) -> dict:
        """(N_f, N_H, N_X, N_D) of the first term (all terms share it)."""
        t = self.terms[0]
        Nf = sum(isinstance(f, Psi) for f in t.factors)
        NH = sum(isinstance(f, H) for f in t.factors)
        NX = sum(isinstance(f, FS) for f in t.factors)
        ND = sum(len(f.derivs) for f in t.factors if hasattr(f, "derivs"))
        return dict(N_f=Nf, N_H=NH, N_X=NX, N_D=ND)

    def mass_dimension(self) -> Fraction:
        fc = self.field_content()
        return Fraction(3, 2) * fc["N_f"] + fc["N_H"] + 2 * fc["N_X"] + fc["N_D"]


# --------------------------------------------------------------------------------------
# Composite builders (the paper's shorthand, expanded once here)
# --------------------------------------------------------------------------------------

_fresh = count(1)


def fresh(prefix: str = "x") -> str:
    return f"{prefix}{next(_fresh)}"


def T(coeff, *factors: Factor) -> Term:
    return Term(C.of(coeff), tuple(factors))


def HdH(j: str = None) -> Term:
    """(H^dag H)"""
    j = j or fresh("j")
    return T(1, H(j, dag=True), H(j))


def HtauH(I_: str, j: str = None, k: str = None) -> Term:
    """(H^dag tau^I H)"""
    j = j or fresh("j")
    k = k or fresh("k")
    return T(1, H(j, dag=True), Tensor("tau", (I_, j, k)), H(k))


def iHDlrH(mu: str, j: str = None) -> List[Term]:
    """i H^dag Dlr_mu H = i H^dag (D_mu H) - i (D_mu H^dag) H   (two terms)."""
    j = j or fresh("j")
    return [
        T(I, H(j, dag=True), H(j, derivs=(mu,))),
        T(-I, H(j, dag=True, derivs=(mu,)), H(j)),
    ]


def iHDlrIH(mu: str, I_: str, j: str = None, k: str = None) -> List[Term]:
    """i H^dag Dlr^I_mu H = i H^dag tau^I (D_mu H) - i (D_mu H^dag) tau^I H."""
    j = j or fresh("j")
    k = k or fresh("k")
    return [
        T(I, H(j, dag=True), Tensor("tau", (I_, j, k)), H(k, derivs=(mu,))),
        T(-I, H(j, dag=True, derivs=(mu,)), Tensor("tau", (I_, j, k)), H(k)),
    ]


def D_HdH(mu: str, j: str = None) -> List[Term]:
    """D_mu (H^dag H) = (D_mu H^dag) H + H^dag (D_mu H)."""
    j = j or fresh("j")
    return [
        T(1, H(j, dag=True, derivs=(mu,)), H(j)),
        T(1, H(j, dag=True), H(j, derivs=(mu,))),
    ]


def D_HtauH(mu: str, I_: str, j: str = None, k: str = None) -> List[Term]:
    """D_mu (H^dag tau^I H)."""
    j = j or fresh("j")
    k = k or fresh("k")
    return [
        T(1, H(j, dag=True, derivs=(mu,)), Tensor("tau", (I_, j, k)), H(k)),
        T(1, H(j, dag=True), Tensor("tau", (I_, j, k)), H(k, derivs=(mu,))),
    ]


def bilinear(
    psibar: str,
    psi: str,
    gamma: str,
    lor: Sequence[str] = (),
    p: str = "p",
    r: str = "r",
    su2: Tuple[Optional[str], Optional[str]] = (None, None),
    col: Tuple[Optional[str], Optional[str]] = (None, None),
    dbar: Sequence[str] = (),
    dpsi: Sequence[str] = (),
) -> Term:
    """(psibar_p Gamma psi_r) with optional gauge indices and derivatives on either field.
    If a doublet/colour index is needed and not supplied, a fresh contracted one is used
    (i.e. the bilinear is a gauge singlet)."""
    a, b = fresh("s"), fresh("s")
    infoA, infoB = FERMIONS[psibar], FERMIONS[psi]
    s1, s2 = su2
    if infoA["su2"] and infoB["su2"] and s1 is None and s2 is None:
        s1 = s2 = fresh("j")
    c1, c2 = col
    if infoA["col"] and infoB["col"] and c1 is None and c2 is None:
        c1 = c2 = fresh("a")
    fa = Psi(psibar, a, bar=True, su2=s1 if infoA["su2"] else None, col=c1 if infoA["col"] else None, gen=p, derivs=tuple(dbar))
    fb = Psi(psi, b, bar=False, su2=s2 if infoB["su2"] else None, col=c2 if infoB["col"] else None, gen=r, derivs=tuple(dpsi))
    return T(1, fa, Gamma(gamma, tuple(lor), a, b), fb)


def prod(*pieces: Union[Term, List[Term]]) -> List[Term]:
    """Distribute products of (sums of) terms."""
    out: List[Term] = [T(1)]
    for p in pieces:
        ps = p if isinstance(p, list) else [p]
        out = [a * b for a in out for b in ps]
    return out


def scale(c, terms: Union[Term, List[Term]]) -> List[Term]:
    ts = terms if isinstance(terms, list) else [terms]
    return [t * C.of(c) for t in ts]


def FSdual(group: str, mu: str, nu: str, adj: Optional[str] = None, derivs=()) -> FS:
    return FS(group, mu, nu, adj=adj, dual=True, derivs=tuple(derivs))


# --------------------------------------------------------------------------------------
# FeynRules naming context
# --------------------------------------------------------------------------------------

# Index-name pools.  Every name is prefixed so that it CANNOT collide with a symbol the
# model defines.  This is not cosmetic: the emitted blocks scope these names, and a
# collision silently corrupts the model.  Two real cases found this way, on top of the
# single-letter "b" that clobbered the b quark in session 1:
#   "ee" is the electromagnetic coupling, and "mu" is the muon (ClassMembers -> {e,mu,ta}).
# validate/check_symbol_clash.py re-derives the model's symbol list and asserts the pools
# are disjoint from it, so this can never silently regress.
FR_POOLS = {
    "lor": ["z8mu", "z8nu", "z8rho", "z8sig", "z8ka", "z8la", "z8om", "z8th", "z8mu2", "z8nu2", "z8rho2", "z8sig2"],
    "su2f": ["z8i", "z8j", "z8k", "z8l", "z8m", "z8n", "z8o", "z8p", "z8q", "z8r"],
    "su2a": ["z8A", "z8B", "z8C", "z8D", "z8E", "z8F"],
    "su3f": ["z8c1", "z8c2", "z8c3", "z8c4", "z8c5", "z8c6"],
    "su3a": ["z8g1", "z8g2", "z8g3", "z8g4", "z8g5", "z8g6"],
    "sp": ["z8s1", "z8s2", "z8s3", "z8s4", "z8s5", "z8s6", "z8s7", "z8s8"],
    "gen": ["z8f1", "z8f2", "z8f3", "z8f4"],
}

ALL_INDEX_NAMES = [n for pool in FR_POOLS.values() for n in pool]


class FRContext:
    """Maps abstract index names to FeynRules index names, per term."""

    def __init__(self, term: Term):
        self.types = {n: t for n, (t, m) in term.indices().items()}
        self.map: dict = {}
        self.used = {k: 0 for k in FR_POOLS}
        self.alias: dict = {}  # for identified indices (delta tensors)

    def fresh(self, typ: str) -> str:
        pool = FR_POOLS[typ]
        i = self.used[typ]
        self.used[typ] += 1
        return pool[i] if i < len(pool) else f"{pool[0]}{i}"

    def identify(self, a: str, b: str):
        ra, rb = self._root(a), self._root(b)
        if ra != rb:
            self.alias[rb] = ra
            if rb in self.map and ra not in self.map:
                self.map[ra] = self.map[rb]

    def _root(self, a: str) -> str:
        while a in self.alias:
            a = self.alias[a]
        return a

    def name(self, idx: str) -> str:
        r = self._root(idx)
        if r not in self.map:
            self.map[r] = self.fresh(self.types[idx])
        return self.map[r]

    def all_names(self) -> List[str]:
        return sorted(set(self.map.values()))
