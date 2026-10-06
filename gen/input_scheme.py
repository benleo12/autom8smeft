"""
gen/input_scheme.py  --  electroweak input-scheme corrections for the {alpha, MZ, GF} scheme.

``base.fr`` derives gw, g1, vev and MW from {alpha, MZ, GF} by the ordinary Standard Model
relations with no SMEFT corrections, as do the hand-typed reference files.  That is wrong as
soon as an operator that shifts one of the three input observables is switched on.

WHICH OPERATORS.  The input-scheme section of the paper works through all 21 dimension-eight classes:
only eight operators enter.  Four class-6 operators correct the gauge kinetic terms
(alpha, MZ), Q_{H^6}^{(1),(2)} correct the gauge mass matrix (MZ, MW and hence GF), and
Q_{l^2H^4D}^{(2),(4)} correct the W-lepton vertex (GF).  Q_{G^2H^4}^{(1)} touches alpha_s
alone.  The bosonic half is confirmed against SmeftFR v3.03's code/smeft_input_scheme.m.

HOW THE FORMULAE ARE OBTAINED.  gen/derive_input_scheme.py writes the EXACT kinetic and mass
matrices and the EXACT muon-decay relation, with the dimension-six (Warsaw, SMEFTsim
conventions) and dimension-eight corrections in, imposes the three inputs, and expands the
solution for the Lagrangian couplings to O(1/Lambda^4).  Every (dim-6)^2 cross term is
therefore derived, not guessed.  It is validated three ways: the dim-6 linear limit
reproduces SMEFTsim's alphaShifts for gw, g1, vev and MW to 1e-11; the dim-8 limit
reproduces the documented delta_G = 2 delta_gWl - delta_mW; and the residuals of the exact
relations at the truncated solution scale as (1/Lambda^2)^3.  The result is stored in
gen/input_scheme_formulae.json and read here, so nothing is transcribed by hand.

WHAT IS EMITTED.  The Standard Model values gwSM, g1SM, vevSM, MW2SM from the inputs, the
dimension-six coefficients as External parameters in SMEFTsim's names (so a SMEFTsim fit can
be used unchanged), and gw = gwSM (1 + gw1 + gw2) etc.  Every shift enters the Lagrangian as
such a sum, the gauge couplings through their Definitions, the vev in the doublet, the Higgs
quartic and the Yukawas through the series of gen/derive_higgs_yukawa.py, so FeynRules splits
every coupling into pieces of definite NP order and the NP=0 amplitude is the Standard Model.
The one exception is the W mass, which in the {alpha, MZ, GF} scheme is derived and is kept
exact in the propagator, as SMEFTsim 3 does by default.

FLAVOUR CAVEAT.  Our flavour-universal contraction is C delta_pr delta_st.  With it the
dimension-eight four-lepton operators contain no mu -> e nu nu structure and do not shift
GF; SMEFTsim's crossed delta_pt delta_sr would.  A convention choice, not physics.

NOT DONE HERE.  These are the parameter relations only.  The canonical normalisation of the
gauge and Higgs fields (SMEFTsim's rotateGaugeB), the tadpole for muH and the Yukawa
re-derivation multiply every vertex and are steps 3 to 5 of the plan in the doc.
"""

from __future__ import annotations

import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# The dimension-six coefficients below make the shift formulae complete, but the SHIFTS ALONE
# are not a consistent model: the rotation and the coupling shifts cancel against the kinetic
# and mass terms that the OPERATORS themselves induce, and this project ships no
# dimension-six Lagrangian.  With only our dimension-eight blocks loaded, leave every dim-6
# coefficient at zero; to use them, load a dimension-six Lagrangian in SMEFTsim conventions
# (which is what the names follow) alongside.
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


def formulae(scheme: str = None) -> dict:
    scheme = scheme or SCHEME
    return json.load(open(os.path.join(
        HERE, "input_scheme_formulae.json" if scheme == "alpha" else "input_scheme_formulae_mw.json")))


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
    # order {'1': 1} and MadGraph refuses the model ("Some couplings have '1' order",
    # 2026-09-06; the SM couplings of both input-scheme UFOs were affected).
    rows = ["(* " + "=" * 84,
            "   Electroweak input scheme " + ("{alpha, MZ, GF}" if scheme == "alpha" else "{MW, MZ, GF}")
            + " to O(1/Lambda^4): dim-6 (SMEFTsim conventions),",
            "   dim-6 squared and dim-8.  Generated by gen/input_scheme.py from",
            "   gen/input_scheme_formulae" + ("" if scheme == "alpha" else "_mw")
            + ".json, itself written by gen/derive_input_scheme.py.",
            "   " + "=" * 84 + " *)"]
    # dimension-six coefficients and scale, SMEFTsim names, default zero
    rows.append('  Lam6 == { ParameterType -> External, BlockName -> DIM6, OrderBlock -> 1, Value -> 1000,'
                ' Description -> "dimension-six scale in GeV (SMEFTsim LambdaSMEFT)" }')
    for i, (c, op) in enumerate(DIM6, start=2):
        rows.append(f'  {c} == {{ ParameterType -> External, BlockName -> DIM6, OrderBlock -> {i}, Value -> 0,'
                    f' InteractionOrder -> {{NP,1}}, Description -> "{op}, SMEFTsim convention" }}')
    rows.append('  L6 == { ParameterType -> Internal, Value -> 1/Lam6^2, Description -> "1/Lambda_6^2" }')
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
                row = ("  (* canonical field rotation (step 3), applied to the expanded SM Lagrangian; first- and\n"
                       "     second-order pieces are separate parameters so MadGraph can count NP orders *)\n" + row)
                first = False
            rows.append(row)
            rows.append(P(f"{k}2", F[f"{k}2"], f"O(1/Lambda^4) piece: {desc}", 2))
    # Step 4, the Higgs potential.  base.fr has V = -muH^2 |H|^2 + lam |H|^4; with Q_H, Q_H8 in
    # the Lagrangian as + cH |H|^6/Lam6^2 + c8H8 |H|^8/Lam^4 and a canonically normalised h,
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
    # Steps 4 and 5 as SERIES.  The quartic and the Yukawas used to be exact functions of vevT,
    # which hid their coefficient dependence from the order tags (the NP=0 amplitude moved with
    # the coefficients, and NP^2==2 held terms quadratic in them).  They now enter the Lagrangian
    # as lam (1 + lamr1 + lamr2) and y_f (1 + yr1 + yr2) + c8fH5 vevSM^4 L8/4, the form gw already
    # had, so FeynRules splits every coupling by order.  gen/derive_higgs_yukawa.py derives the
    # four series from the exact relations and writes them into the formulae file.
    for k, desc in (("lamr", "relative shift of the Higgs quartic"), ("yr", "relative shift of every Yukawa")):
        rows.append(P(f"{k}1", F[f"{k}1"], f"O(1/Lambda^2) {desc}", 1))
        rows.append(P(f"{k}2", F[f"{k}2"], f"O(1/Lambda^4) {desc}, dim-6 squared plus dim-8", 2))
    # The gluon kinetic form factor.  Q_{G^2H^4}^{(1)} = c (H^dag H)^2 G G contributes
    # + c vev^4/(4 Lam^4) G^A_{mn} G^{A mn} from the doublet's vev, the FULL non-abelian field
    # strength squared, so its two-, three- and four-gluon pieces all appear; the UFO writer
    # drops the two-point one, and the surviving three- and four-gluon pieces then break the
    # gluon Ward identity at O(v^4/Lambda^4) (MadGraph check lorentz, 2026-09-06).  The gluon
    # does not mix, so no field rotation is needed: LGauge carries -1/4 (1 + d8fG) FS[G]^2 and
    # the merged Lagrangian is exactly -1/4 FS[G]^2 with gs = Sqrt[4 Pi aS] in every vertex,
    # i.e. alpha_s is the coupling of the canonical field; the operator survives only through
    # its Higgs-dependent pieces.  It MUST be written with vev (= vevSM), the symbol the cached
    # operator vertices carry (the cache is built from base.fr), so that the cancellation is
    # symbol for symbol; vevT^4 = vev^4 (1 + vev2)^4 left an untruncated O((v^4/Lambda^4)^2)
    # mismatch whenever the H^6 partners shift the vev (Lorentz check residual 1e-6 to 1e-5
    # with every coefficient on, zero family by family, 2026-09-06).
    rows.append(P("d8fG", "c8G2H4x1 vev^4/Lam^4", "dim-8 form factor: gluon kinetic term, cancelled in LGauge", 2))
    if not helpers_only:
        rows.append(P("gw",  "gwSM (1 + gw1 + gw2)",  "SU(2) coupling, corrected"))
        rows.append(P("g1",  "g1SM (1 + g11 + g12)",  "U(1) coupling, corrected"))
        rows.append(P("vev", "vevSM (1 + vev1 + vev2)", "vev, corrected"))
        if scheme == "alpha":
            rows.append(P("MW",  "Sqrt[MW2SM (1 + MW21 + MW22)]", "W mass, corrected"))
        # in the mw scheme M_W is the input and does not move: that is the point of the scheme
    return "\n".join(rows[:5]) + "\n" + ",\n".join(rows[5:]) + ("\n" if not helpers_only else ",\n")


def write_variant(base: str, out: str, scheme: str = None) -> None:
    """Write an opt-in copy of base.fr that uses the corrected input relations.

    The structure follows SMEFTsim exactly.  gw and g1 are shifted through their
    Definitions, so the Lagrangian sees gwSM (1 + gw1 + gw2) and the NP content is tracked
    through gw1 (NP 1) and gw2 (NP 2).  The shifted vev enters where SMEFTsim's redefVev
    puts it, in the Higgs doublet, while the parameter vev keeps the SM value that lam, muH
    and the Yukawas are built from until the tadpole and Yukawas are redone (steps 4, 5).
    MW is shifted as the pole mass.  sw2 stays the SM mixing angle from the inputs, as
    SMEFTsim keeps sth: the field rotation to canonical kinetic terms is step 3.  With every
    coefficient zero every substitution is the identity and the model is base.fr."""
    scheme = scheme or SCHEME
    s = open(base).read()
    if scheme == "alpha":
        swap = [("Value         -> Sqrt[MZ^2/2+Sqrt[MZ^4/4-Pi/Sqrt[2]*aEW/Gf*MZ^2]], ",
                 "Value         -> Sqrt[MW2SM (1 + MW21 + MW22)], ")]
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
    Value            -> 1/(aEWSM (1 + aEW1 + aEW2)),
    InteractionOrder -> {QED,-2},"""),
            # alpha itself, and with it ee = Sqrt[4 Pi aEW], must stay at the SM value derived from
            # the inputs.  The shift of alpha enters the Lagrangian through the tagged series of gw
            # and g1 and nowhere else, whereas ee is an untagged parameter that 33334 couplings of
            # the dimension-eight sector carry (the vertex cache was computed against the alpha
            # base, where ee is an input and FeynRules writes gwSM sw as ee).  With ee following
            # the shifted alpha, every one of those couplings picked up a factor (1 + aEW2/2), a
            # product of two coefficients tagged as one, and `check lorentz u d~ > w+ a` failed at
            # 1e-5 with c8W2H4x1 and c8W2H4x3 on together while passing with each alone
            # (2026-10-05).  aEWM1 above keeps the shifted value, as the number a user reads off
            # the parameter block; nothing in the Lagrangian uses it.
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
        ("Definitions      -> {gw->ee/sw}, ", "Definitions      -> {gw -> gwSM (1 + gw1 + gw2)}, "),
        ("Definitions      -> {g1->ee/cw}, ", "Definitions      -> {g1 -> g1SM (1 + g11 + g12)}, "),
        ("Value            -> 2*MW*sw/ee, ", "Value            -> vevSM, "),
        ("- 1/4 FS[G,mu,nu,aa] FS[G,mu,nu,aa]", "- 1/4 (1 + d8fG) FS[G,mu,nu,aa] FS[G,mu,nu,aa]"),
        # the vev in the doublet as a tagged sum, not as the one untagged parameter vevT
        ("(vev + H)/Sqrt[2]", "(vevSM (1 + vev1 + vev2) + H)/Sqrt[2]"),
        # lam and muH keep base.fr's Standard-Model values (vev is vevSM here); the quartic's
        # shift is written into LHiggs below.  muH multiplies only the tadpole and the h mass
        # term, neither of which is a vertex, so it needs no series.
        ("- lam Phibar[ii] Phi[ii] Phibar[jj] Phi[jj]",
         "- lam (1 + lamr1 + lamr2) Phibar[ii] Phi[ii] Phibar[jj] Phi[jj]"),
        # the Yukawas: the Standard-Model y_f = Sqrt[2] m_f/vevSM stays in the parameter, the
        # vev shift multiplies it as a tagged series, and the class-12 compensation that keeps
        # the input mass fixed is its own tagged term (c8 vevSM^4 rather than vevT^4, the
        # difference being O(1/Lambda^8)).  The IndexDelta keeps it diagonal, which is what the
        # old yl[i,i] substitution did.
        ("-yd[ff2, ff3] CKM[ff1, ff2] QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] Phi[ii] -",
         "-(yd[ff2, ff3] (1 + yr1 + yr2) + c8qdH5 vevSM^4 L8/4 IndexDelta[ff2, ff3]) CKM[ff1, ff2] QLbar[sp, ii, ff1, cc].dR [sp, ff3, cc] Phi[ii] -"),
        ("    yl[ff1, ff3] LLbar[sp, ii, ff1].lR [sp, ff3] Phi[ii] -",
         "    (yl[ff1, ff3] (1 + yr1 + yr2) + c8leH5 vevSM^4 L8/4 IndexDelta[ff1, ff3]) LLbar[sp, ii, ff1].lR [sp, ff3] Phi[ii] -"),
        ("    yu[ff1, ff2] QLbar[sp, ii, ff1, cc].uR [sp, ff2, cc] Phibar[jj] Eps[ii, jj]",
         "    (yu[ff1, ff2] (1 + yr1 + yr2) + c8quH5 vevSM^4 L8/4 IndexDelta[ff1, ff2]) QLbar[sp, ii, ff1, cc].uR [sp, ff2, cc] Phibar[jj] Eps[ii, jj]"),
    ]
    # Step 5, the Yukawas.  base.fr has -y fbar f Phi (mass m = y v/sqrt2) and the class-12
    # operators enter as + c8fH5 (H^dag H)^2 (fbar f H) / Lam^4, whose mass-giving term is
    # + c8 v^5/(4 sqrt2) fbar f.  Keeping the input masses fixed therefore needs
    #     y_f = sqrt2 m_f/vevT + c8fH5 vevT^4/(4 Lam^4)
    # with c8quH5 for up-type, c8qdH5 for down-type and c8leH5 for the charged leptons.  Since
    # 2026-10-03 that relation is written into LYukawa as the series y_f (1 + yr1 + yr2) +
    # c8fH5 vevSM^4 L8/4 (edits list above), so that the shift is tagged; the parameter y_f
    # itself keeps its Standard-Model value.
    #
    # The dimension-six class-5 operators are NOT compensated here, and that is deliberate after
    # 2026-09-22.  They are SMEFTsim's operators verbatim, which is what makes them checkable
    # against SMEFTsim's own UFO, and they carry the Yukawa as an explicit factor
    # (Conjugate[yd[ff2,ff1]] in OdH).  A compensating shift of y_f therefore scales the operator
    # term and the Standard Model term together and cannot convert one basis into the other; two
    # attempts, additive and multiplicative, made the disagreement worse and then left it
    # unchanged.  Converting to the mass basis means using the vev-subtracted operator
    # (H^dag H - v^2/2)(qbar d H), which is a change to the operators themselves.
    #
    # So this model is the MASS basis at dimension eight and the YUKAWA basis at dimension six,
    # and that is a real inconsistency, recorded in docs/DIM6.md, not a bug to paper over.  The
    # three-number test that tells the bases apart is there too.
    for old, new in edits:
        assert s.count(old) == 1, f"expected exactly one occurrence of {old!r}, found {s.count(old)}"
        s = s.replace(old, new)
    # the canonical rotation acts on the EXPANDED SM Lagrangian: LSM is written with the
    # unphysical Wi, B and the doublet Phi, and Z, A, h only appear after ExpandIndices applies
    # their Definitions, so a rule on the raw LSM would miss all of them.  SMEFTsim applies
    # rotateGaugeB at the level of mass eigenstates for the same reason.  All rules go in one
    # ReplaceAll so Z -> ... A ... and A -> ... Z ... do not chain.
    F = formulae(scheme)
    if "TZZ1" in F:
        lsm_old = "LSM:= LGauge + LFermions + LHiggs + LYukawa + LGhost;"
        assert s.count(lsm_old) == 1
        s = s.replace(lsm_old,
            "LSMbare := LGauge + LFermions + LHiggs + LYukawa + LGhost;\n"
            "(* canonical field rotation, step 3 of the input scheme; see gen/input_scheme.py *)\n"
            "LSM := ExpandIndices[LSMbare, FlavorExpand -> {SU2D, SU2W}] /. {\n"
            "  Z[z9mu_] :> (1 + TZZ1 + TZZ2) Z[z9mu] + (TZA1 + TZA2) A[z9mu],\n"
            "  A[z9mu_] :> (TAZ1 + TAZ2) Z[z9mu] + (1 + TAA1 + TAA2) A[z9mu],\n"
            "  W[z9mu_] :> (1 + rW1 + rW2) W[z9mu],  Wbar[z9mu_] :> (1 + rW1 + rW2) Wbar[z9mu],\n"
            "  H :> (1 + rh1 + rh2) H};")
    # helper parameters go in just before MW, the first parameter that uses them
    anchor = "  MW == { "
    assert s.count(anchor) == 1
    s = s.replace(anchor, emit(helpers_only=True, scheme=scheme) + anchor, 1)
    header = "\n".join([
        "(* GENERATED by gen/input_scheme.py write_variant() from base.fr.  Do not edit; edit",
        "   base.fr or gen/input_scheme.py and regenerate.  Corrected {alpha, MZ, GF} input",
        "   relations to O(1/Lambda^4); identical to base.fr when every coefficient is zero. *)", ""])
    open(out, "w").write(header + s)


if __name__ == "__main__":
    import sys
    if len(sys.argv) in (3, 4):
        write_variant(sys.argv[1], sys.argv[2],
                      sys.argv[3] if len(sys.argv) > 3 else None)
        print("wrote", sys.argv[2], "in the", (sys.argv[3] if len(sys.argv) > 3 else SCHEME), "scheme")
    else:
        print(emit())
