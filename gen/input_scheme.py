"""
gen/input_scheme.py  --  electroweak input-scheme corrections, {alpha, MZ, GF} and {MW, MZ, GF}.

``base.fr`` derives gw, g1, vev and MW from {alpha, MZ, GF} by the ordinary Standard Model
relations with no SMEFT corrections.  Those relations fail as soon as an operator that shifts
one of the three input observables is switched on.

WHICH OPERATORS.  The input-scheme section of the paper works through all 21 dimension-eight classes:
nine operators enter with massless leptons.  Four class-6 operators correct the gauge kinetic terms
(alpha, MZ), Q_{H^6}^{(1),(2)} correct the gauge mass matrix (MZ, MW and hence GF), Q_{l^2H^4D}^{(2),(4)}
correct the W-lepton vertex (GF), and the crossed flavour structures of Q_{l^4H^2}^{(1)} add a
four-lepton contact term to muon decay (GF).  With the lepton Yukawas on, the crossed structure of
Q_{l^2e^2H^2}^{(1),(2)} adds a scalar coupling to muon decay, which shifts G_F through its interference
with the Standard Model, weighted by the electron's mass, and through its square.  Q_{G^2H^4}^{(1)}
touches alpha_s alone.  The bosonic half is confirmed against SmeftFR v3.03's code/smeft_input_scheme.m.

HOW THE FORMULAE ARE OBTAINED.  gen/derive_input_scheme.py writes the EXACT kinetic and mass
matrices and the EXACT muon-decay relation, with the dimension-six (Warsaw, SMEFTsim
conventions) and dimension-eight corrections in, imposes the three inputs, and expands the
solution for the Lagrangian couplings to O(1/Lambda^4).  Every (dim-6)^2 cross term is
therefore derived, not guessed.  It is validated three ways: the dim-6 linear limit
reproduces SMEFTsim's alphaShifts for gw, g1, vev and MW to 1e-11; the dim-8 limit
reproduces the documented delta_G = 2 delta_gWl - delta_mW; and the residuals of the exact
relations at the truncated solution scale as (1/Lambda^2)^3.  The result is stored in
gen/input_scheme_formulae.json and read here, so the model carries the derived formulae.

WHAT IS WRITTEN.  The Standard Model values gwSM, g1SM, vevSM, MW2SM from the inputs, the
dimension-six coefficients as External parameters in SMEFTsim's names (so a SMEFTsim fit can
be used unchanged), and gw = gwSM (1 + gw1 + gw2) etc.  Every shift enters the Lagrangian as
such a sum, the gauge couplings through their Definitions, the vev in the doublet, the Higgs
quartic and the Yukawas through the series of gen/derive_higgs_yukawa.py, so FeynRules splits
every coupling into pieces of definite NP order and the NP=0 amplitude is the Standard Model.
The one exception is the W mass, which in the {alpha, MZ, GF} scheme is derived and is kept
exact in the propagator, as SMEFTsim 3 does by default.

FLAVOUR.  In the flavour mode of the released models, mfv (gen/emit_fr.py), every fermionic operator
carries each of its flavour structures with a coefficient of its own.  Six of them reach muon decay
and so G_F: the crossed structures delta_pt delta_sr and delta_pt (Y_e Y_e^dag)_sr of
Q_{l^4H^2}^{(1)} (c8l4H2x1Fx00, c8l4H2x1Fx0E), the structure (Y_e Y_e^dag)_pr of
Q_{l^2H^4D}^{(2),(4)} (c8l2H4Dx2FE, c8l2H4Dx4FE), the last two weighted by y_e^2 + y_mu^2 (ylsq),
and the crossed structure (Y_e)_pt (Y_e^dag)_sr of Q_{l^2e^2H^2}^{(1),(2)} (c8l2e2H2x1Fx00,
c8l2e2H2x2Fx00), weighted by yleta = y_e^2 g(x)/f(x) and, from O(t^4), by ylprod = y_e^2 y_mu^2.
gen/derive_input_scheme.py and gen/derive_geo.py have them.  In the universal mode the operators have one
structure each, these coefficients do not exist, and emit() sets them to zero in the formulae.

THE OTHER INGREDIENTS.  The canonical normalisation of the gauge and Higgs fields (SMEFTsim's
rotateGaugeB) comes from gen/derive_rotation.py, and the Higgs quartic and the Yukawas as series
from gen/derive_higgs_yukawa.py.  Both write into the same formulae file, and write_variant()
applies them to base.fr.  muH keeps its Standard Model value: it multiplies only the tadpole
and the h mass term, neither of which is a vertex.
"""

from __future__ import annotations

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# The dimension-six coefficients below make the shift formulae complete, but the SHIFTS ALONE
# are not a consistent model: the rotation and the coupling shifts cancel against the kinetic
# and mass terms that the OPERATORS themselves induce.  In a model with only the
# dimension-eight blocks (dim8_is, dim8_mw) every dim-6 coefficient stays at zero.
# models/dim68_is carries the dimension-six Lagrangian in SMEFTsim conventions, which the names
# follow, and is the model in which they may be set.
DIM6 = [("cHW", "Q_HW"), ("cHB", "Q_HB"), ("cHWB", "Q_HWB"), ("cHDD", "Q_HD"),
        ("cHl3", "Q_Hl^(3)"), ("cll1", "Q_ll (universal)"), ("cHbox", "Q_Hbox"), ("cH", "Q_H")]

DIM8_FORM_FACTORS = [   # informational, and needed by the field-normalisation step
    ("d8fW",  "c8W2H4x1 vev^4/Lam^4",                  "W^{1,2} kinetic term"),
    ("d8fW3", "(c8W2H4x1 + c8W2H4x3) vev^4/Lam^4",     "W^3 kinetic term"),
    ("d8fB",  "c8B2H4x1 vev^4/Lam^4",                  "B kinetic term"),
    ("d8fWB", "(1/2) c8WBH4x1 vev^4/Lam^4",            "W^3-B kinetic mixing (SmeftFR sign)"),
    ("d8mW",  "(c8H6x1 - c8H6x2)/4 vev^4/Lam^4",       "W mass"),
    ("d8mZ",  "(c8H6x1 + c8H6x2)/4 vev^4/Lam^4",       "Z mass"),
    ("d8gWl", "(c8l2H4Dx2 + c8l2H4Dx4)/2 vev^4/Lam^4", "W-lepton vertex"),
    ("d8Zh",  "(c8H6x1 + c8H6x2)/4 vev^4/Lam^4",       "Higgs kinetic term"),
]


# Which three measurements the variant imposes.  "alpha" is {alpha, M_Z, G_F}; "mw" is
# {M_W, M_Z, G_F}, where both masses are inputs and so carry no Wilson-coefficient dependence.
# That difference is not cosmetic: MadGraph tags couplings and not masses, so in the alpha scheme
# the shift of M_W is invisible to every order constraint and NP^2==1 is not the complete
# interference.  With M_W an input there is no mass shift to lose.
SCHEME = os.environ.get("DIM8_SCHEME", "alpha").lower()


# The coefficients of flavour structures in the formulae, which only the mfv mode has.
FLAVOUR_WCS = ("c8l2H4Dx2FE", "c8l2H4Dx4FE", "c8l4H2x1Fx00", "c8l4H2x1Fx0E", "c8l2e2H2x1Fx00", "c8l2e2H2x2Fx00")


def _eta_rows(P) -> list:
    """The weight yleta = y_e^2 g(x)/f(x), x = m_e^2/m_mu^2, of the interference of the scalar coupling of muon
    decay with the Standard Model (gen/derive_geo.py), and the helpers it is computed from.  MadGraph evaluates
    every argument of cond, in Python and in Fortran, so no branch may divide by zero or take the logarithm of
    zero: x is guarded at ymm = 0 and its logarithm at x = 0, where it enters only as x ln x.  f and g both
    vanish as (1 - x)^5 at x = 1, where g/f is 1/4, and the cond on fmuon gives that value.  Since
    f(1/x) = -f(x)/x^4 and g(1/x) = -g(x)/x^3, for yme > ymm the same expression is y_mu^2 g(1/x)/f(1/x),
    the decay of the heavier of the two into the lighter, which at ymm = 0 is zero."""
    return [
        P("xemu", "yme^2/(ymm^2 + FR$Cond[ymm, 1, 0])", "m_e^2/m_mu^2 in muon decay"),
        P("lxemu", "Log[xemu + FR$Cond[xemu, 1, 0]]", "Log[xemu], zero at xemu = 0, where xemu multiplies it"),
        P("fmuon", "1 - 8 xemu + 8 xemu^3 - xemu^4 - 12 xemu^2 lxemu", "phase-space function f of muon decay"),
        P("gmuon", "1 + 9 xemu - 9 xemu^2 - xemu^3 + 6 xemu (1 + xemu) lxemu",
          "phase-space function g of the Michel eta term"),
        P("yleta", "FR$Cond[ymm, 0, 2 yme^2/vevSM^2 FR$Cond[fmuon, 1/4, gmuon/(fmuon + FR$Cond[fmuon, 1, 0])]]",
          "y_e^2 g/f, the weight of the Michel eta term in the muon-decay relation"),
    ]


def formulae(scheme: str = None, n: int = None) -> dict:
    """The formulae of the scheme, to O(1/Lambda^4), or with n to O(t^n) from gen/derive_geo.py."""
    scheme = scheme or SCHEME
    if n is not None:
        F = json.load(open(os.path.join(HERE, f"input_scheme_formulae_geo{n}_{scheme}.json")))
        F.pop("keys")
        assert os.environ.get("DIM8_FLAVOUR", "mfv") in ("mfv", "mfvexplicit"), \
            "the models of order n are built in the flavour mode mfv"
        return F
    F = json.load(open(os.path.join(
        HERE, "input_scheme_formulae.json" if scheme == "alpha" else "input_scheme_formulae_mw.json")))
    if os.environ.get("DIM8_FLAVOUR", "mfv") not in ("mfv", "mfvexplicit"):
        drop = re.compile(r"\b(" + "|".join(FLAVOUR_WCS) + r")\b")
        F = {k: drop.sub("0", v) for k, v in F.items()}
    return F


def emit(helpers_only: bool = False, scheme: str = None) -> str:
    scheme = scheme or SCHEME
    F = formulae(scheme)
    P = lambda name, value, desc, order=None, io=None: (
        f"  {name} == {{ ParameterType -> Internal, Value -> {value},"
        + (f" InteractionOrder -> {{NP,{order}}}," if order is not None else "")
        + (f" InteractionOrder -> {io}," if io is not None else "")
        + f' Description -> "{desc}" }}')
    # Every parameter that carries a power of a gauge coupling or of the vev needs its
    # InteractionOrder, otherwise FeynRules gives the couplings built from it the placeholder
    # order {'1': 1} and MadGraph refuses the model ("Some couplings have '1' order").
    rows = ["(* " + "=" * 84,
            "   Electroweak input scheme " + ("{alpha, MZ, GF}" if scheme == "alpha" else "{MW, MZ, GF}")
            + " to O(1/Lambda^4): dim-6 (SMEFTsim conventions),",
            "   dim-6 squared and dim-8.  Generated by gen/input_scheme.py from",
            "   gen/input_scheme_formulae" + ("" if scheme == "alpha" else "_mw")
            + ".json, itself written by gen/derive_input_scheme.py.",
            "   " + "=" * 84 + " *)"]
    # dimension-six coefficients, SMEFTsim names, default zero.  Their scale is Lam (block DIM8, entry 0), the one
    # scale of dimension six and eight.  Entry 1 of DIM6 held a second scale until 2026-11-10 and stays empty, so
    # that the coefficients keep their entries.
    for i, (c, op) in enumerate(DIM6, start=2):
        rows.append(f'  {c} == {{ ParameterType -> External, BlockName -> DIM6, OrderBlock -> {i}, Value -> 0,'
                    f' InteractionOrder -> {{NP,1}}, Description -> "{op}, SMEFTsim convention" }}')
    rows.append('  L6 == { ParameterType -> Internal, Value -> 1/Lam^2, Description -> "1/Lambda^2" }')
    rows.append('  L8 == { ParameterType -> Internal, Value -> 1/Lam^4, Description -> "1/Lambda^4" }')
    # Standard Model values from the inputs (base.fr relations, unchanged)
    rows.append(P("vevSM", "1/Sqrt[Sqrt[2] Gf]", "SM vev from GF", io="{QED,-1}"))
    if scheme == "alpha":
        rows.append(P("sw2SM", "(1 - Sqrt[1 - 4 Pi aEW/(Sqrt[2] Gf MZ^2)])/2", "SM sin^2 theta_W from the inputs"))
        rows.append(P("gwSM",  "Sqrt[4 Pi aEW]/Sqrt[sw2SM]", "SM SU(2) coupling", io="{QED,1}"))
        rows.append(P("g1SM",  "Sqrt[4 Pi aEW]/Sqrt[1 - sw2SM]", "SM U(1) coupling", io="{QED,1}"))
        rows.append(P("MW2SM", "gwSM^2 vevSM^2/4", "SM MW^2"))
    else:
        # M_W and M_Z are both inputs, so the mixing angle is exact and alpha is derived
        rows.append(P("sw2SM", "1 - MW^2/MZ^2", "sin^2 theta_W, exact from the two input masses"))
        rows.append(P("gwSM",  "2 MW/vevSM", "SM SU(2) coupling from M_W and G_F", io="{QED,1}"))
        rows.append(P("g1SM",  "gwSM Sqrt[sw2SM/(1 - sw2SM)]", "SM U(1) coupling", io="{QED,1}"))
        rows.append(P("MW2SM", "MW^2", "M_W^2, an input"))
        rows.append(P("aEWSM", "gwSM^2 g1SM^2/(4 Pi (gwSM^2 + g1SM^2))",
                      "alpha, derived from the inputs", io="{QED,2}"))
    for name, expr, desc in DIM8_FORM_FACTORS:
        rows.append(P(name, expr, f"dim-8 form factor: {desc}", 2))
    rows.append(P("ylsq", "2 (yme^2 + ymm^2)/vevSM^2", "y_e^2 + y_mu^2, in the muon-decay relation"))
    rows += _eta_rows(P)
    # the derived shifts
    for k in (("gw", "g1", "vev", "MW2") if scheme == "alpha" else ("gw", "g1", "vev", "aEW")):
        rows.append(P(f"{k}1", F[f"{k}1"], f"O(1/Lambda^2) relative shift of {k}", 1))
        rows.append(P(f"{k}2", F[f"{k}2"], f"O(1/Lambda^4) relative shift of {k}, dim-6 squared plus dim-8", 2))
    ROT = [("TZZ", "Z -> (1 + TZZ) Z + TZA A"), ("TZA", "Z -> ... + TZA A"),
           ("TAZ", "A -> ... + TAZ Z"), ("TAA", "A -> (1 + TAA) A + TAZ Z"),
           ("rW", "W -> (1 + rW) W"), ("rh", "h -> (1 + rh) h")]
    if all(f"{k}1" in F for k, _ in ROT):
        first = True
        for k, desc in ROT:
            row = P(f"{k}1", F[f"{k}1"], f"O(1/Lambda^2) piece: {desc}", 1)
            if first:   # comment rides on the first row; a bare comment row would sit between two commas
                row = ("  (* canonical field rotation, applied to the expanded SM Lagrangian; first- and\n"
                       "     second-order pieces are separate parameters so MadGraph can count NP orders *)\n" + row)
                first = False
            rows.append(row)
            rows.append(P(f"{k}2", F[f"{k}2"], f"O(1/Lambda^4) piece: {desc}", 2))
    # The Higgs potential.  base.fr has V = -muH^2 |H|^2 + lam |H|^4; with Q_H, Q_H8 in
    # the Lagrangian as + cH |H|^6/Lam^2 + c8H8 |H|^8/Lam^4 and a canonically normalised h,
    # the minimum and the curvature at the actual vev vevT give
    #     2 lam = Zh^2 MH^2/vevT^2 + 3 cH vevT^2 L6 + 3 c8H8 vevT^4 L8
    #     muH^2 = lam vevT^2 - (3/4) cH vevT^4 L6 - (1/2) c8H8 vevT^6 L8
    # which is SmeftFR's hlambda (= 2 lam) verbatim and, at fixed lam, reproduces SMEFTsim's
    # dMH2 = MH^2 v^2 (2 cHbox - cHDD/2 - 3 cH/(2 lam)).  Like SMEFTsim's lam these carry no
    # InteractionOrder of their own.
    rows.append(P("Zh2", "1 + cHDD vevSM^2 L6/2 - 2 cHbox vevSM^2 L6 + (c8H6x1 + c8H6x2)/4 vevSM^4 L8",
                  "Higgs kinetic normalisation Zh^2 (dim-6 and dim-8), for reference"))
    rows.append(P("vevT", "vevSM (1 + vev1 + vev2)",
                  "the corrected vev, exact, for reference: the Lagrangian carries vevSM (1 + vev1 + vev2)", io="{QED,-1}"))
    # The quartic and the Yukawas as SERIES.  As exact functions of vevT they would hide their
    # coefficient dependence from the order tags (the NP=0 amplitude would move with the
    # coefficients, and NP^2==2 would hold terms quadratic in them).  They enter the Lagrangian
    # as lam (1 + lamr1 + lamr2) and y_f (1 + yr1 + yr2) + c8fH5 vevSM^4 L8/4, the form gw has,
    # so FeynRules splits every coupling by order.  gen/derive_higgs_yukawa.py derives the
    # four series from the exact relations and writes them into the formulae file.
    for k, desc in (("lamr", "relative shift of the Higgs quartic"), ("yr", "relative shift of every Yukawa")):
        rows.append(P(f"{k}1", F[f"{k}1"], f"O(1/Lambda^2) {desc}", 1))
        rows.append(P(f"{k}2", F[f"{k}2"], f"O(1/Lambda^4) {desc}, dim-6 squared plus dim-8", 2))
    # The gluon kinetic form factor.  Q_{G^2H^4}^{(1)} = c (H^dag H)^2 G G contributes
    # + c vev^4/(4 Lam^4) G^A_{mn} G^{A mn} from the doublet's vev, the FULL non-abelian field
    # strength squared, so its two-, three- and four-gluon pieces all appear; the UFO writer
    # drops the two-point one, and the surviving three- and four-gluon pieces then break the
    # gluon Ward identity at O(v^4/Lambda^4) (MadGraph check lorentz).  The gluon
    # does not mix, so no field rotation is needed: LGauge carries -1/4 (1 + d8fG) FS[G]^2 and
    # the merged Lagrangian is exactly -1/4 FS[G]^2 with gs = Sqrt[4 Pi aS] in every vertex,
    # i.e. alpha_s is the coupling of the canonical field; the operator survives only through
    # its Higgs-dependent pieces.  It MUST be written with vev (= vevSM), the symbol the cached
    # operator vertices carry (the cache is built from base.fr), so that the cancellation is
    # symbol for symbol; vevT^4 = vev^4 (1 + vev2)^4 would leave an untruncated
    # O((v^4/Lambda^4)^2) mismatch whenever the H^6 partners shift the vev.
    rows.append(P("d8fG", "c8G2H4x1 vev^4/Lam^4", "dim-8 form factor: gluon kinetic term, cancelled in LGauge", 2))
    if not helpers_only:
        rows.append(P("gw",  "gwSM (1 + gw1 + gw2)",  "SU(2) coupling, corrected"))
        rows.append(P("g1",  "g1SM (1 + g11 + g12)",  "U(1) coupling, corrected"))
        rows.append(P("vev", "vevSM (1 + vev1 + vev2)", "vev, corrected"))
        if scheme == "alpha":
            rows.append(P("MW",  "Sqrt[MW2SM (1 + MW21 + MW22)]", "W mass, corrected"))
        # in the mw scheme M_W is the input and does not move: that is the point of the scheme
    return "\n".join(rows[:5]) + "\n" + ",\n".join(rows[5:]) + ("\n" if not helpers_only else ",\n")


# The most terms in the value of one parameter of the base of a model of order n.  MadGraph compiles every
# parameter with Python, whose compiler recurses once per term of a sum and stops near 3000 terms (CPython 3.9
# to 3.11), and the neutral rotation reaches 2700 at n = 4, so a longer sum goes in as parts of at most this
# many terms, each a parameter of its own, about the size of the largest coupling of the released models.
PART_TERMS = 400


def split_sum(expr: str, size: int = PART_TERMS) -> list:
    """The value of a parameter as parts of at most size terms each, cut where a term of the top-level sum
    begins (the " + " and " - " of sympy's mathematica_code, outside any bracket), so that the parts written
    one after the other are the value itself."""
    cuts, depth = [0], 0
    for i, ch in enumerate(expr):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif depth == 0 and ch in "+-" and expr[i - 1:i] == " " and expr[i + 1:i + 2] == " ":
            cuts.append(i)
    terms = [expr[a:b] for a, b in zip(cuts, cuts[1:] + [len(expr)])]
    assert "".join(terms) == expr and depth == 0
    parts = ["".join(terms[j:j + size]).strip() for j in range(0, len(terms), size)]
    return [x[2:] if x.startswith("+ ") else x for x in parts]


def emit_geo(n: int, scheme: str = None) -> str:
    """The parameters of the base of the model of order n (gen/towers.py): those of emit() with every series
    carried to O(t^n), the rescaling of the gluon, and the four-lepton coefficients above dimension eight,
    which enter only G_F (their operators have four legs, so the model has no vertex of them).  The
    dimension-eight form factors and Zh2 of emit() are left out: they hold to O(1/Lambda^4) only, and nothing
    in the Lagrangian uses them.  d8fG is left out because the gluon operators are vev-subtracted instead
    (gen/towers.py, gen/make_dim6.py --geo)."""
    scheme = scheme or SCHEME
    F = formulae(scheme, n)
    P = lambda name, value, desc, order=None, io=None: (
        f"  {name} == {{ ParameterType -> Internal, Value -> {value},"
        + (f" InteractionOrder -> {{NP,{order}}}," if order is not None else "")
        + (f" InteractionOrder -> {io}," if io is not None else "")
        + f' Description -> "{desc}" }}')
    dims = range(10, 2*n + 5, 2)
    rows = ["(* " + "=" * 84,
            "   Electroweak input scheme " + ("{alpha, MZ, GF}" if scheme == "alpha" else "{MW, MZ, GF}")
            + f" to O(t^{n}), t = 1/Lambda^2, with the towers of the field-space",
            f"   connections.  Generated by gen/input_scheme.py from gen/input_scheme_formulae_geo{n}_{scheme}.json,",
            "   itself written by gen/derive_geo.py.",
            "   " + "=" * 84 + " *)"]
    for i, (c, op) in enumerate(DIM6, start=2):
        rows.append(f'  {c} == {{ ParameterType -> External, BlockName -> DIM6, OrderBlock -> {i}, Value -> 0,'
                    f' InteractionOrder -> {{NP,1}}, Description -> "{op}, SMEFTsim convention" }}')
    rows.append('  L6 == { ParameterType -> Internal, Value -> 1/Lam^2, Description -> "1/Lambda^2" }')
    rows.append('  L8 == { ParameterType -> Internal, Value -> 1/Lam^4, Description -> "1/Lambda^4" }')
    for d in dims:
        rows.append(f'  L{d} == {{ ParameterType -> Internal, Value -> 1/Lam^{d - 4}, Description -> "1/Lambda^{d - 4}" }}')
    # the four-lepton coefficients above dimension eight in the relations (2007.00565's LLLL tower), then the
    # towers of the scalar coupling, numbered after them
    gf = sorted({w for v in F.values()
                 for w in re.findall(r"\bc(?:1[0-9]|[2-9][0-9])(?:l4H2x|l2e2H2x)[0-9A-Za-z]+\b", v)},
                key=lambda w: ("l2e2H2x" in w, int(re.match(r"c(\d+)", w).group(1)), w))
    for i, w in enumerate(gf, start=1):
        d = int(re.match(r"c(\d+)", w).group(1))
        rows.append(f'  {w} == {{ ParameterType -> External, BlockName -> GEOGF, OrderBlock -> {i}, Value -> 0,'
                    f' InteractionOrder -> {{NP,{(d - 4)//2}}},'
                    f' Description -> "dimension-{d} four-lepton coefficient in G_F, no vertex in the model" }}')
    rows.append(P("vevSM", "1/Sqrt[Sqrt[2] Gf]", "SM vev from GF", io="{QED,-1}"))
    if scheme == "alpha":
        rows.append(P("sw2SM", "(1 - Sqrt[1 - 4 Pi aEW/(Sqrt[2] Gf MZ^2)])/2", "SM sin^2 theta_W from the inputs"))
        rows.append(P("gwSM",  "Sqrt[4 Pi aEW]/Sqrt[sw2SM]", "SM SU(2) coupling", io="{QED,1}"))
        rows.append(P("g1SM",  "Sqrt[4 Pi aEW]/Sqrt[1 - sw2SM]", "SM U(1) coupling", io="{QED,1}"))
        rows.append(P("MW2SM", "gwSM^2 vevSM^2/4", "SM MW^2"))
    else:
        rows.append(P("sw2SM", "1 - MW^2/MZ^2", "sin^2 theta_W, exact from the two input masses"))
        rows.append(P("gwSM",  "2 MW/vevSM", "SM SU(2) coupling from M_W and G_F", io="{QED,1}"))
        rows.append(P("g1SM",  "gwSM Sqrt[sw2SM/(1 - sw2SM)]", "SM U(1) coupling", io="{QED,1}"))
        rows.append(P("MW2SM", "MW^2", "M_W^2, an input"))
        rows.append(P("aEWSM", "gwSM^2 g1SM^2/(4 Pi (gwSM^2 + g1SM^2))",
                      "alpha, derived from the inputs", io="{QED,2}"))
    rows.append(P("ylsq", "2 (yme^2 + ymm^2)/vevSM^2", "y_e^2 + y_mu^2, in the muon-decay relation"))
    rows.append(P("ylprod", "4 yme^2 ymm^2/vevSM^4", "y_e^2 y_mu^2, in the muon-decay relation"))
    rows += _eta_rows(P)
    series = [(k, f"relative shift of {k}") for k in
              (("gw", "g1", "vev", "MW2") if scheme == "alpha" else ("gw", "g1", "vev", "aEW"))]
    series += [("TZZ", "Z -> (1 + TZZ) Z + TZA A"), ("TZA", "Z -> ... + TZA A"),
               ("TAZ", "A -> ... + TAZ Z"), ("TAA", "A -> (1 + TAA) A + TAZ Z"),
               ("rW", "W -> (1 + rW) W"), ("rh", "h -> (1 + rh) h"),
               ("lamr", "relative shift of the Higgs quartic"), ("yr", "relative shift of every Yukawa"),
               ("rG", "G -> (1 + rG) G inside the operators, g_s G fixed"), ("sG", "g_s -> g_s (1 + sG) inside the operators")]
    for k, desc in series:
        for j in range(1, n + 1):
            parts = split_sum(F[f"{k}{j}"])
            if len(parts) > 1:
                for i, x in enumerate(parts, start=1):
                    rows.append(P(f"{k}{j}p{i}", x, f"part {i} of {len(parts)} of {k}{j}", j))
                parts = [" + ".join(f"{k}{j}p{i}" for i in range(1, len(parts) + 1))]
            rows.append(P(f"{k}{j}", parts[0], f"O(t^{j}) piece: {desc}", j))
    vev = " + ".join(f"vev{j}" for j in range(1, n + 1))
    rows.append(P("vevT", f"vevSM (1 + {vev})",
                  f"the corrected vev, for reference: the Lagrangian carries vevSM (1 + {vev})", io="{QED,-1}"))
    return "\n".join(rows[:5]) + "\n" + ",\n".join(rows[5:]) + ",\n"


def geo_definitions(n: int) -> str:
    """The truncation of the model of order n.  Each correction of order j is tagged z9eps^j, and an operator
    of NP order p keeps the products of its corrections through order n - p (z8geoTrunc, which the blocks of
    gen/towers.py and gen/make_dim6.py --geo call).  The Standard-Model Lagrangian (p = 0) is cut at n with the
    electroweak rules only: the gluon is canonical as it stands, since the gluon operators are vev-subtracted,
    and the rescaling rG, sG that this leaves acts inside the operators (gen/derive_geo.py)."""
    tag = lambda j: "z9eps" if j == 1 else f"z9eps^{j}"
    ser = lambda k: " + ".join(f"{tag(j)} {k}{j}" for j in range(1, n + 1))
    tags = lambda k: ", ".join(f"{k}{j} -> {tag(j)} {k}{j}" for j in range(1, n + 1))
    vev = " + ".join(f"vev{j}" for j in range(1, n + 1))
    return "\n".join([
        f"(* the truncation of the model of order {n}; see gen/input_scheme.py geo_definitions *)",
        f"z8geoN = {n};",
        f"z8vT := vevSM (1 + {vev});",
        "z8geoRulesEW = {",
        f"  vevT -> vevSM (1 + {ser('vev')}), {tags('vev')},",
        f"  gw -> gwSM (1 + {ser('gw')}), {tags('gw')},",
        f"  g1 -> g1SM (1 + {ser('g1')}), {tags('g1')},",
        f"  Z[z9mu_] :> (1 + {ser('TZZ')}) Z[z9mu] + ({ser('TZA')}) A[z9mu],",
        f"  A[z9mu_] :> ({ser('TAZ')}) Z[z9mu] + (1 + {ser('TAA')}) A[z9mu],",
        f"  W[z9mu_] :> (1 + {ser('rW')}) W[z9mu], Wbar[z9mu_] :> (1 + {ser('rW')}) Wbar[z9mu],",
        f"  H :> (1 + {ser('rh')}) H,",
        f"  {tags('lamr')}, {tags('yr')}}};",
        "z8geoRules = Join[z8geoRulesEW, {",
        "  (* the gluon: g_s G is unchanged, so a field strength scales as one power of the field *)",
        f"  FS[G, z9m_, z9n_, z9a_] :> (1 + {ser('rG')}) FS[G, z9m, z9n, z9a],",
        f"  G[z9mu_, z9a_] :> (1 + {ser('rG')}) G[z9mu, z9a], gs -> gs (1 + {ser('sG')})}}];",
        "(* the cut at order M: the expansion of z9e with the powers of z9eps above M dropped.  Expand[z9e] would first",
        "   make every order of the products of the corrections, z8geoExp drops them product by product, with the",
        "   same result: like Expand it acts on sums, products and positive powers and leaves other heads as they are *)",
        "z8geoMul[z9a_, z9b_, z9M_] := Expand[z9a z9b] /. z9eps^z9n_ /; z9n > z9M :> 0;",
        "z8geoExp[z9e_Plus, z9M_] := z8geoExp[#, z9M] & /@ z9e;",
        "z8geoExp[z9e_Times, z9M_] := Fold[z8geoMul[#1, z8geoExp[#2, z9M], z9M] &, 1, List @@ z9e];",
        "z8geoExp[Power[z9b_, z9n_Integer?Positive], z9M_] /; ! FreeQ[z9b, z9eps] := Nest[z8geoMul[#, z8geoExp[z9b, z9M], z9M] &, 1, z9n];",
        "z8geoExp[z9e_, _] := z9e;",
        "z8geoCut[z9e_, z9M_] := If[z9M <= 0, Expand[z9e /. z9eps -> 0],",
        "  (z8geoExp[z9e, z9M] /. z9eps^z9n_ /; z9n > z9M :> 0) /. z9eps -> 1];",
        "z8geoTrunc[z9L_, z9p_] := z8geoCut[z9L /. z8geoRules, z8geoN - z9p];",
        'If[FeynmanGauge, Print["[geo] WARNING: the rotation is written for the unitary gauge; '
        'the Goldstone and ghost terms are not rotated"]];', ""])


def tower_yukawa_terms(d: int) -> dict:
    """yukawa_terms() for the class-12 members of dimension d, (H^dag H)^((d-8)/2) Q_{fH^5} (gen/towers.py):
    the same flavour structures, with the coefficients of the member."""
    if d == 8:
        return yukawa_terms()
    import sys
    sys.path.insert(0, HERE)
    import emit_flavour as EF
    import towers
    from operators import OPS
    structures = EF.load_structures()
    ops = {o.wc: o for o in OPS}
    idx = {"c8quH5": ("ff1", "ff2"), "c8qdH5": ("ff1", "ff3"), "c8leH5": ("ff1", "ff3")}
    out = {}
    for wc, (a, b) in idx.items():
        member = towers.times_hdagh(ops[wc], (d - 8)//2)
        assert member.wc == f"c{d}" + wc[2:], member.wc
        out[wc] = EF.yukawa_term(member, structures[ops[wc].name], a, b)
    return out


def yukawa_terms() -> dict:
    """The flavour matrix of each class-12 operator, by its coefficient, in the indices of the Yukawa term
    of base.fr it compensates.  In the flavour mode of the released models, mfv (gen/emit_fr.py), it is
    the sum of the operator's structures, the Yukawa matrix and the chains with one Y Y^dag insertion,
    each with its own coefficient.  DIM8_FLAVOUR=universal has the delta."""
    idx = {"c8quH5": ("ff1", "ff2"), "c8qdH5": ("ff1", "ff3"), "c8leH5": ("ff1", "ff3")}
    if os.environ.get("DIM8_FLAVOUR", "mfv") not in ("mfv", "mfvexplicit"):
        return {wc: f"{wc} IndexDelta[{a}, {b}]" for wc, (a, b) in idx.items()}
    import sys
    sys.path.insert(0, HERE)
    import emit_flavour as EF
    from operators import OPS
    structures = EF.load_structures()
    ops = {o.wc: o for o in OPS}
    out = {}
    for wc, (a, b) in idx.items():
        assert ops[wc].name in structures, f"{EF.STRUCTURES} has no structures of {ops[wc].name}"
        out[wc] = EF.yukawa_term(ops[wc], structures[ops[wc].name], a, b)
    return out


def write_variant(base: str, out: str, scheme: str = None, n: int = None) -> None:
    """Write an opt-in copy of base.fr that uses the corrected input relations.

    The structure follows SMEFTsim exactly.  gw and g1 are shifted through their
    Definitions, so the Lagrangian sees gwSM (1 + gw1 + gw2) and the NP content is tracked
    through gw1 (NP 1) and gw2 (NP 2).  The shifted vev enters where SMEFTsim's redefVev
    puts it, in the Higgs doublet, while the parameter vev keeps the SM value that lam, muH
    and the Yukawas are built from; the quartic and the Yukawas carry their shifts as the
    tagged series lamr and yr.  In the alpha scheme MW is shifted as the pole mass, and in
    the mw scheme it is an input.  sw2 stays the SM mixing angle from the inputs, as SMEFTsim
    keeps sth, and the canonical field rotation is applied to the expanded SM Lagrangian.
    With every coefficient zero every substitution is the identity and the model is base.fr.

    With n, the base of the model of order n (gen/towers.py): every series to O(t^n) (gen/derive_geo.py), the
    class-12 compensation of every dimension through 2n + 4, no d8fG, and the truncation of geo_definitions."""
    scheme = scheme or SCHEME
    s = open(base).read()
    # FeynRules declares FR$Cond, the cond of the UFO, but gives it no value, and yleta uses it
    old = "FR$DSign = -1;"
    assert s.count(old) == 1, f"expected exactly one occurrence of {old!r}, found {s.count(old)}"
    s = s.replace(old, old + "\n\n(* the value of FR$Cond[a, b, c], the UFO's cond, that FeynRules has no definition for *)\n"
                  "FR$Cond[z9a_?NumericQ, z9b_, z9c_] := If[z9a == 0, z9b, z9c];")
    m = n or 2
    S = lambda k: " + ".join(f"{k}{j}" for j in range(1, m + 1))
    if n is None:
        T = {wc: f"vevSM^4 L8/4 ({t})" for wc, t in yukawa_terms().items()}
    else:
        F = formulae(scheme, n)
        terms = {d: tower_yukawa_terms(d) for d in range(8, 2*n + 5, 2)}
        T = {wc: "(" + " + ".join(f"({F[f'yc{d}']}) ({terms[d][wc]})" for d in terms) + ")" for wc in terms[8]}
    if scheme == "alpha":
        swap = [("Value         -> Sqrt[MZ^2/2+Sqrt[MZ^4/4-Pi/Sqrt[2]*aEW/Gf*MZ^2]], ",
                 f"Value         -> Sqrt[MW2SM (1 + {S('MW2')})], ")]
    else:
        # The two inputs trade places.  M_W becomes the external at SMINPUTS 1 and alpha is
        # derived from it, which is what removes every Wilson-coefficient dependence from the
        # masses.  The default is SMEFTsim's 80.387 so that moving between the two models is one
        # fewer surprise; set it to 79.82435975, which is what the alpha scheme derives from
        # aEWM1 = 127.9, to put the two models on the same numerical point.
        swap = [
            ("""  aEWM1 == { 
    ParameterType    -> External, 
    BlockName        -> SMINPUTS, 
    OrderBlock       -> 1, 
    Value            -> 127.9,
    InteractionOrder -> {QED,-2},""",
             """  aEWM1 == { 
    ParameterType    -> Internal, 
    Value            -> 1/(aEWSM (1 + """ + S('aEW') + """)),
    InteractionOrder -> {QED,-2},"""),
            # alpha itself, and with it ee = Sqrt[4 Pi aEW], must stay at the SM value derived from
            # the inputs.  The shift of alpha enters the Lagrangian through the tagged series of gw
            # and g1 and nowhere else, whereas ee is an untagged parameter that 33334 couplings of
            # the dimension-eight sector carry (the vertex cache is computed against the alpha
            # base, where ee is an input and FeynRules writes gwSM sw as ee).  If ee followed the
            # shifted alpha, every one of those couplings would pick up a factor (1 + aEW2/2), a
            # product of two coefficients tagged as one, and `check lorentz u d~ > w+ a` would
            # fail with c8W2H4x1 and c8W2H4x3 on together while passing with each alone.  aEWM1
            # above keeps the shifted value, as the number a user reads off the parameter block;
            # nothing in the Lagrangian uses it.
            ("""  aEW == {
    ParameterType    -> Internal,
    Value            -> 1/aEWM1,""",
             """  aEW == {
    ParameterType    -> Internal,
    Value            -> aEWSM,"""),
            ("""   MW == { 
    ParameterType -> Internal, 
    Value         -> Sqrt[MZ^2/2+Sqrt[MZ^4/4-Pi/Sqrt[2]*aEW/Gf*MZ^2]], ""","""   MW == { 
    ParameterType -> External, 
    BlockName     -> SMINPUTS, 
    OrderBlock    -> 1, 
    Value         -> 80.387, """),
        ]
    edits = swap + [
        ("Value         -> 1-(MW/MZ)^2, ", "Value         -> sw2SM, "),
        ("Definitions      -> {gw->ee/sw}, ", f"Definitions      -> {{gw -> gwSM (1 + {S('gw')})}}, "),
        ("Definitions      -> {g1->ee/cw}, ", f"Definitions      -> {{g1 -> g1SM (1 + {S('g1')})}}, "),
        ("Value            -> 2*MW*sw/ee, ", "Value            -> vevSM, "),
    ] + ([("- 1/4 FS[G,mu,nu,aa] FS[G,mu,nu,aa]", "- 1/4 (1 + d8fG) FS[G,mu,nu,aa] FS[G,mu,nu,aa]")]
         if n is None else []) + [
        # the vev in the doublet as a tagged sum, not as the one untagged parameter vevT
        ("(vev + H)/Sqrt[2]", f"(vevSM (1 + {S('vev')}) + H)/Sqrt[2]"),
        # lam and muH keep base.fr's Standard-Model values (vev is vevSM here); the quartic's
        # shift is written into LHiggs below.  muH multiplies only the tadpole and the h mass
        # term, neither of which is a vertex, so it needs no series.
        ("- lam Phibar[ii] Phi[ii] Phibar[jj] Phi[jj]",
         f"- lam (1 + {S('lamr')}) Phibar[ii] Phi[ii] Phibar[jj] Phi[jj]"),
        # the Yukawas: the Standard-Model y_f = Sqrt[2] m_f/vevSM stays in the parameter, the
        # vev shift multiplies it as a tagged series, and the class-12 compensation that keeps
        # the input mass fixed is its own tagged term (c8 vevSM^4 rather than vevT^4, the
        # difference being O(1/Lambda^8)).  The compensation is the operator's flavour matrix in the
        # basis of the doublet, so the down-type one stands outside the product with CKM.
        ("-yd[ff2, ff3] CKM[ff1, ff2] QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] Phi[ii] -",
         f"-yd[ff2, ff3] (1 + {S('yr')}) CKM[ff1, ff2] QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] Phi[ii] -\n"
         f"    {T['c8qdH5']} QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] Phi[ii] -"),
        ("    yl[ff1, ff3] LLbar[sp, ii, ff1].lR [sp, ff3] Phi[ii] -",
         f"    (yl[ff1, ff3] (1 + {S('yr')}) + {T['c8leH5']}) LLbar[sp, ii, ff1].lR [sp, ff3] Phi[ii] -"),
        ("    yu[ff1, ff2] QLbar[sp, ii, ff1, cc].uR [sp, ff2, cc] Phibar[jj] Eps[ii, jj]",
         f"    (yu[ff1, ff2] (1 + {S('yr')}) + {T['c8quH5']}) QLbar[sp, ii, ff1, cc].uR [sp, ff2, cc] Phibar[jj] Eps[ii, jj]"),
    ]
    # The Yukawas.  base.fr has -y fbar f Phi (mass m = y v/sqrt2) and the class-12
    # operators enter as + c8fH5 (H^dag H)^2 (fbar f H) / Lam^4, whose mass-giving term is
    # + c8 v^5/(4 sqrt2) fbar T f, with T the operator's flavour matrix.  Keeping the input masses
    # fixed therefore needs
    #     Y_f = sqrt2 M_f/vevT + vevT^4/(4 Lam^4) sum_S c_S T^S
    # with the structures of c8quH5 for up-type, c8qdH5 for down-type and c8leH5 for the charged
    # leptons (yukawa_terms).  That relation is written into LYukawa as the series
    # y_f (1 + yr1 + yr2) + vevSM^4 L8/4 sum_S c_S T^S (edits list above), so that the shift is
    # tagged; the parameter y_f itself keeps its Standard-Model value.  The mass matrix is then
    # sqrt2 M_f/vevT whatever the structures, diagonal and real, and no field is rotated.
    #
    # The dimension-six class-5 operators are NOT compensated here.  They carry the Yukawa as an
    # explicit factor (Conjugate[yd[ff2,ff1]] in OdH), so a compensating shift of y_f would
    # scale the operator term and the Standard Model term together and could not change the
    # basis.  gen/make_dim6.py writes them vev-subtracted instead, (H^dag H - v^2/2)(qbar d H),
    # which keeps every fermion mass at its input.  The model is therefore in the MASS basis at
    # dimension six as at dimension eight; docs/DIM6.md records the three-number test that
    # tells the two bases apart.
    for old, new in edits:
        assert s.count(old) == 1, f"expected exactly one occurrence of {old!r}, found {s.count(old)}"
        s = s.replace(old, new)
    # the canonical rotation acts on the EXPANDED SM Lagrangian: LSM is written with the
    # unphysical Wi, B and the doublet Phi, and Z, A, h only appear after ExpandIndices applies
    # their Definitions, so a rule on the raw LSM would miss all of them.  SMEFTsim applies
    # rotateGaugeB at the level of mass eigenstates for the same reason.  All rules go in one
    # ReplaceAll so Z -> ... A ... and A -> ... Z ... do not chain.
    F = formulae(scheme, n)
    if n is not None:
        lsm_old = "LSM:= LGauge + LFermions + LHiggs + LYukawa + LGhost;"
        assert s.count(lsm_old) == 1
        s = s.replace(lsm_old,
            "LSMbare := LGauge + LFermions + LHiggs + LYukawa + LGhost;\n" + geo_definitions(n) +
            "(* canonical field rotation of the input scheme, cut at O(t^z8geoN); see gen/input_scheme.py *)\n"
            "LSM := z8geoCut[ExpandIndices[LSMbare, FlavorExpand -> {SU2D, SU2W}] /. z8geoRulesEW, z8geoN];")
    elif "TZZ1" in F:
        lsm_old = "LSM:= LGauge + LFermions + LHiggs + LYukawa + LGhost;"
        assert s.count(lsm_old) == 1
        s = s.replace(lsm_old,
            "LSMbare := LGauge + LFermions + LHiggs + LYukawa + LGhost;\n"
            "(* canonical field rotation of the input scheme; see gen/input_scheme.py *)\n"
            "LSM := ExpandIndices[LSMbare, FlavorExpand -> {SU2D, SU2W}] /. {\n"
            "  Z[z9mu_] :> (1 + TZZ1 + TZZ2) Z[z9mu] + (TZA1 + TZA2) A[z9mu],\n"
            "  A[z9mu_] :> (TAZ1 + TAZ2) Z[z9mu] + (1 + TAA1 + TAA2) A[z9mu],\n"
            "  W[z9mu_] :> (1 + rW1 + rW2) W[z9mu],  Wbar[z9mu_] :> (1 + rW1 + rW2) Wbar[z9mu],\n"
            "  H :> (1 + rh1 + rh2) H};")
    # helper parameters go in just before MW, the first parameter that uses them
    anchor = "  MW == { "
    assert s.count(anchor) == 1
    s = s.replace(anchor, (emit(helpers_only=True, scheme=scheme) if n is None else emit_geo(n, scheme)) + anchor, 1)
    header = "\n".join([
        "(* GENERATED by gen/input_scheme.py write_variant() from base.fr.  Do not edit; edit",
        "   base.fr or gen/input_scheme.py and regenerate.  Input relations of this scheme",
        "   corrected to O(1/Lambda^4); identical to base.fr when every coefficient is zero. *)", ""]) if n is None else \
        "\n".join([
        f"(* GENERATED by gen/input_scheme.py write_variant(n = {n}) from base.fr.  Do not edit; edit",
        "   base.fr or gen/input_scheme.py and regenerate.  Input relations of this scheme and the",
        f"   canonical normalisation corrected to O(t^{n}), t = 1/Lambda^2, with the towers of the field-space",
        "   connections; identical to base.fr when every coefficient is zero. *)", ""])
    open(out, "w").write(header + s)


if __name__ == "__main__":
    import sys
    args, n = sys.argv[1:], None
    if "--geo" in args:      # python3 gen/input_scheme.py base.fr base_geo4_mw.fr mw --geo 4
        i = args.index("--geo")
        n = int(args[i + 1])
        del args[i:i + 2]
    if len(args) in (2, 3):
        write_variant(args[0], args[1], args[2] if len(args) > 2 else None, n)
        print("wrote", args[1], "in the", (args[2] if len(args) > 2 else SCHEME), "scheme"
              + (f", every series to O(t^{n})" if n else ""))
    else:
        print(emit())
