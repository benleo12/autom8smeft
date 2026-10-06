#!/usr/bin/env python3
"""
gen/make_dim6.py  --  emit tests/gen_smoke/dim6_smeftsim.fr

The dimension-six sector is not ours.  It is SMEFTsim's, in the U(3)^5 flavour-symmetric
framework, and the point of this file is to put SMEFTsim's operator definitions on OUR
Standard Model base so that one model carries both sectors and MadGraph counts powers of
1/Lambda^2 across them with a single coupling order.

Two things make that possible without rewriting any physics.  The field names agree:
SMEFTsim and our base both descend from the FeynRules Standard Model, so Phi, QL, uR, dR,
LL, lR, Wi, B, G and the SU2W/SU2D/Colour/Gluon/Generation index types are the same
symbols on both sides, and SMEFTsim's operator expressions evaluate against our fields
unchanged.  And the input relations already expect it: our base declares eight dimension-six
coefficients in block DIM6 under SMEFTsim's own names, with the dimension-six-squared terms
that the {alpha, MZ, GF} relations need at 1/Lambda^4, so those eight feed the operators and
the input scheme from the same external parameter.

What this script does NOT do is reinterpret the operators.  SMEFTsim's own truncation rule
redefCtoZero is applied exactly as SMEFTsim applies it, which keeps the dimension-six
vertices identical to SMEFTsim's and therefore checkable against SMEFTsim's shipped UFO.
The consequence is that the dimension-six sector is linear: the product of a dimension-six
vertex with the dimension-six shift of the vev, a 1/Lambda^4 term, is not in the vertices.
It is in the input relations, which do carry the squares.  See docs/DIM6.md.

    python3 gen/make_dim6.py [--smeftsim DIR] [-o tests/gen_smoke/dim6_smeftsim.fr]
"""

from __future__ import annotations

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# SMEFTsim's FeynRules sources, which are not redistributed here: set $SMEFTSIM_FR or pass
# --smeftsim.  Obtain them from the SMEFTsim authors (arXiv:1709.06492, arXiv:2012.11343).
DEFAULT_SMEFTSIM = os.environ.get(
    "SMEFTSIM_FR", os.path.expanduser("~/Downloads/SMEFT_HandsOn_pt1/SMEFTsim_FR"))

# Declared already by tests/gen_smoke/base_inputscheme.fr, in block DIM6, because the
# {alpha, MZ, GF} relations need them.  Re-declaring a parameter makes FeynRules keep the
# first and warn, so they are dropped here and the base's declaration is the one that counts.
IN_BASE = {"cH", "cHW", "cHB", "cHWB", "cHDD", "cHl3", "cll1", "cHbox"}
# The scale: ours is Lam6, declared in the base beside them.
SCALE = "LambdaSMEFT"


# What an operator is evaluated on.  The base brings the Lagrangian to canonical form, to second
# order, by shifting g, g' and the vev and by rotating and rescaling the fields.  A dimension-six
# operator multiplied by a first-order shift is a 1/Lambda^4 term like any other, and the second-
# order relations of the base were derived assuming it is there: the W kinetic term, for one, is
# canonical only if the vacuum piece of O_HW is evaluated on the rescaled W.  Until 2026-10-05
# the operators were given the shifted couplings (FeynRules applies a parameter Definition to
# every term) and the unrotated fields, which is neither SMEFTsim's truncation nor the complete
# one.  It left a photon coupled to neutrinos at cHl3 x (g11 - gw1), a g^{mu nu} photon-Z-Higgs
# vertex from cHDD, and a W-W-photon coupling that was not e, all at 1/Lambda^4, and `check
# lorentz ... NP<=2` with the coefficients on failed on seven of fourteen processes.
#
# TRUNC_SECOND is the complete version and the default.  Each field and coupling carries its
# first-order correction, tagged with a bookkeeping symbol so that products of two corrections,
# which are 1/Lambda^6 beside a dimension-six coefficient, are dropped: here where the power is
# explicit, and again on the finished vertices by validate/fr_worker.wls, which reads
# DIM6$FirstOrder and is the authority.  The corrections are separate couplings of order NP=2,
# so the NP=1 vertices stay SMEFTsim's and stay comparable with SMEFTsim's model.
#
# TRUNC_LINEAR is SMEFTsim's rule, which our earlier port only believed it was applying: no
# shift and no rotation inside an operator.  It is gauge invariant at 1/Lambda^2 and its vertices
# are SMEFTsim's and nothing else.  A model built from it must not be run at NP=2 with the
# coefficients of the input relations on, because the base's second-order terms then have
# nothing to cancel against.
#
# Both write the coupling rules twice, as the symbol and as its pieces, because a parameter
# Definition may or may not have been applied by the time the rule sees the expression.
TRUNC_SECOND = [
    "z6vev := vevSM (1 + vev1);",
    "redefCtoZero = {Alternatives @@ WC6 -> 0,",
    "  vevT -> vevSM (1 + z9eps vev1), vev1 -> z9eps vev1, vev2 -> 0,",
    "  gw -> gwSM (1 + z9eps gw1), gw1 -> z9eps gw1, gw2 -> 0,",
    "  g1 -> g1SM (1 + z9eps g11), g11 -> z9eps g11, g12 -> 0,",
    "  Z[z9mu_] :> (1 + z9eps TZZ1) Z[z9mu] + z9eps TZA1 A[z9mu],",
    "  A[z9mu_] :> z9eps TAZ1 Z[z9mu] + (1 + z9eps TAA1) A[z9mu],",
    "  W[z9mu_] :> (1 + z9eps rW1) W[z9mu], Wbar[z9mu_] :> (1 + z9eps rW1) Wbar[z9mu],",
    "  H :> (1 + z9eps rh1) H,",
    "  (* the gluon: g_s G is unchanged, so a field strength scales as one power of the field *)",
    "  FS[G, z9m_, z9n_, z9a_] :> (1 + z9eps rG1) FS[G, z9m, z9n, z9a],",
    "  G[z9mu_, z9a_] :> (1 + z9eps rG1) G[z9mu, z9a], gs -> gs (1 - z9eps rG1)};",
    "z6trunc[z9e_] := (Expand[z9e] /. z9eps^z9n_ /; z9n >= 2 :> 0) /. z9eps -> 1;",
    "DIM6$FirstOrder = {TZZ1, TZA1, TAZ1, TAA1, rW1, rh1, vev1, gw1, g11, rG1};",
    'If[FeynmanGauge, Print["[dim6] WARNING: the first-order rotation is written for the unitary gauge; '
    'the Goldstone and ghost terms are not rotated"]];',
]
TRUNC_LINEAR = [
    "z6vev := vevSM;",
    "redefCtoZero = {Alternatives @@ WC6 -> 0, vevT -> vevhat, vev1 -> 0, vev2 -> 0,",
    "  gw -> gwSM, g1 -> g1SM, gw1 -> 0, gw2 -> 0, g11 -> 0, g12 -> 0};",
    "z6trunc[z9e_] := z9e;",
    "DIM6$FirstOrder = {};",
]
# The one parameter the second-order truncation adds: the first-order rescaling of the gluon,
# the analogue of the base's rW1 = cHW v^2/Lambda^2.
RG1 = ('  rG1 == { ParameterType -> Internal, Value -> cHG vevSM^2/Lam6^2, InteractionOrder -> {NP,1}, '
       'Description -> "O(1/Lambda^2) piece: G -> (1 + rG) G with g_s G fixed" }')


def split_entries(text: str, listname: str) -> list[tuple[str, str]]:
    """Return [(name, body), ...] for  listname = { name == { body }, ... }."""
    m = re.search(re.escape(listname) + r"\s*=\s*\{", text)
    if not m:
        sys.exit(f"{listname} not found")
    i = m.end()
    depth = 1
    while depth:                                      # find the closing brace of the list
        if text[i] == "{":
            depth += 1
        elif text[i] == "}":
            depth -= 1
        i += 1
    body = text[m.end():i - 1]
    out, j = [], 0
    while True:
        e = re.compile(r"([A-Za-z][A-Za-z0-9]*)\s*==\s*\{").search(body, j)
        if not e:
            return out
        k, d = e.end(), 1
        while d:
            if body[k] == "{":
                d += 1
            elif body[k] == "}":
                d -= 1
            k += 1
        out.append((e.group(1), body[e.end():k - 1]))
        j = k


def _find(text: str, pat: str):
    m = re.search(pat, text)
    if not m:
        sys.exit(f"could not find {pat!r} in SMEFTsim's source")
    return m


def extract_class_block(text: str, pat: str) -> str:
    """A field declaration 'F[n] == { ... }', brace-matched from the opening brace the
    pattern ends on.  Class blocks are list entries and end in a comma, not a semicolon."""
    m = _find(text, pat)
    j, depth = m.end(), 1                            # the pattern consumed the opening brace
    while j < len(text):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return text[m.start():j + 1]
        j += 1
    sys.exit(f"unbalanced braces after {pat!r}")


def extract_statement(text: str, pat: str) -> str:
    """A whole top-level statement, from the pattern to the first ';' outside any bracket."""
    m = _find(text, pat)
    j, depth = m.end(), 0
    while j < len(text):
        c = text[j]
        if c in "[{(":
            depth += 1
        elif c in "]})":
            depth -= 1
        elif c == ";" and depth == 0:
            return text[m.start():j + 1]
        j += 1
    sys.exit(f"no terminating semicolon after {pat!r}")


def rewrite(name: str, body: str, order: int) -> str:
    """Zero the value, put it in block DIM6, keep everything else SMEFTsim wrote."""
    fields = {}
    for key in ("ParameterType", "Value", "InteractionOrder", "TeX", "ComplexParameter",
                "ParameterName", "Description"):
        m = re.search(key + r"\s*->\s*", body)
        if not m:
            continue
        k, d = m.end(), 0
        while k < len(body):                          # to the comma at depth zero
            c = body[k]
            if c in "{[":
                d += 1
            elif c in "}]":
                d -= 1
            elif c == "," and d == 0:
                break
            k += 1
        fields[key] = body[m.end():k].strip()
    kind = fields.get("ParameterType", "External")
    out = [f"ParameterType -> {kind}"]
    if kind == "External":
        # SMEFTsim ships every coefficient at Value -> 1.  A user who imports this model and
        # forgets the param card would then get every dimension-six operator switched on at
        # full strength, which is the trap recorded in reference_smeftsim_traps.  Zero here.
        out.append("Value -> 0")
        out.append("BlockName -> DIM6")
        out.append(f"OrderBlock -> {order}")
    else:
        out.append("Value -> " + fields["Value"])
    if "InteractionOrder" in fields:
        out.append("InteractionOrder -> " + fields["InteractionOrder"])
    if "ComplexParameter" in fields:
        out.append("ComplexParameter -> " + fields["ComplexParameter"])
    if "TeX" in fields:
        out.append("TeX -> " + fields["TeX"])
    out.append(f'Description -> "dimension-six, SMEFTsim U(3)^5 name {name}"')
    return "  " + name + " == { " + ", ".join(out) + " }"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smeftsim", default=DEFAULT_SMEFTSIM)
    ap.add_argument("-o", default="")
    ap.add_argument("--linear", action="store_true",
                    help="SMEFTsim's own truncation: every operator strictly linear, with no product "
                         "of an operator and an input-scheme shift.  Gauge invariant at 1/Lambda^2 "
                         "only; the default keeps those products to first order and is gauge "
                         "invariant at 1/Lambda^4")
    a = ap.parse_args()
    if not a.o:
        a.o = os.path.join(ROOT, "tests/gen_smoke/dim6_smeftsim"
                           + ("_linear" if a.linear else "") + ".fr")

    os.makedirs(os.path.dirname(os.path.abspath(a.o)), exist_ok=True)
    if not os.path.isdir(a.smeftsim):
        sys.exit(f"no SMEFTsim sources at {a.smeftsim}.\n"
                 "They are not redistributed with this repository.  Obtain SMEFTsim from its\n"
                 "authors (arXiv:1709.06492 with the flavour framework of arXiv:2012.11343) and\n"
                 "point this at its FeynRules directory:\n"
                 "    SMEFTSIM_FR=/path/to/SMEFTsim_FR python3 gen/make_dim6.py\n"
                 "or pass --smeftsim /path/to/SMEFTsim_FR.  docs/DIM6.md says what it is used for.")
    ptxt = open(os.path.join(a.smeftsim, "d6_parameters_U35.fr")).read()
    otxt = open(os.path.join(a.smeftsim, "SMEFTsim_A_operators_U35.fr")).read()
    ftxt = open(os.path.join(a.smeftsim, "SMEFTsim_A_fields.fr")).read()
    mtxt = open(os.path.join(a.smeftsim, "SMEFTsim_A_main.fr")).read()

    # Three things the operator file uses that live in SMEFTsim's other files.  They are taken
    # verbatim rather than retyped, because without them the operators evaluate to something
    # that is neither an error nor right, which is the worst of the three outcomes.
    #   QLm     the quark doublet WITHOUT the CKM rotation.  Our base has only QL, which carries
    #           CKM on its down component, so the operators that must not see CKM need this
    #           field declared.  SMEFTsim's class index F[131] does not collide with our F[1..15].
    #   sigmaT  sigma^{mu nu} = i/2 [gamma^mu, gamma^nu].  The same convention our own generator
    #           emits for the dimension-eight operators, so the two sectors agree on the sign.
    #   HDH     the Hermitian Higgs current i H^dag D_mu H - i (D_mu H^dag) H.
    # The SU(2) conventions already agree without any translation: both models declare
    # Ta[a,b,c] -> PauliSigma[a,b,c]/2 and FSU2L[i,j,k] :> I Eps[i,j,k].
    qlm = extract_class_block(ftxt, r"F\[131\]\s*==\s*\{")
    sigmat = extract_statement(mtxt, r"sigmaT\[mu_,\s*nu_,\s*sp1_,\s*sp2_\]\s*:=")
    hdh = extract_statement(mtxt, r"HDH\[mu_\]\s*:=")

    phases = split_entries(ptxt, "SMEFTParametersPhases0")
    params = split_entries(ptxt, "SMEFTParameters0")
    wc6 = [n for n, _ in params if n != SCALE]        # exactly SMEFTsim's own WC6

    keep, order, skipped = [], 10, []
    for n, b in phases + params:
        if n == SCALE or n in IN_BASE:
            skipped.append(n)
            continue
        keep.append(rewrite(n, b, order))
        order += 1

    # The operator definitions, verbatim.  Everything above the first operator in SMEFTsim's
    # file is its own header plus the redefCtoZero line, which is reproduced explicitly below
    # so that the file reads as what it is rather than depending on load order.
    cut = re.search(r"^\(\*+ class 1", otxt, re.M)
    if not cut:
        sys.exit("could not find the start of the operators in SMEFTsim's file")
    ops = otxt[cut.start():]

    # SMEFTsim calls the sum of its dimension-six terms L6.  Our base declares an INTERNAL
    # PARAMETER of the same name, L6 = 1/Lam6^2, which the input relations are written in terms
    # of.  Letting SMEFTsim's definition land on that symbol replaces the parameter with a whole
    # Lagrangian: FeynRules then asks for MR$ParameterRules[L6], gets the Lagrangian as the
    # parameter it is supposed to describe, and the load wedges (25 hours at 1% CPU, 2026-09-16).
    # The aggregates are not used by the build, which drives the classes one at a time, so they
    # are renamed rather than dropped.
    ops = re.sub(r"^L6no4f\s*:=", "LD6no4f :=", ops, flags=re.M)
    ops = re.sub(r"^L6\s*:=", "LD6 :=", ops, flags=re.M)

    # The class-5 Yukawa operators, vev-subtracted.  SMEFTsim's shipped UFO uses
    #     (H^dag H - vhat^2/2)(qbar_L d_R H)
    # and ours used the operator as the Warsaw basis writes it, which is the same physics in a
    # different basis but means the fermion mass moves with C_fH while every other observable in
    # this model is held at its input.  That also made our dimension-six sector Yukawa-basis while
    # our dimension-eight class-12 operators are compensated in the Yukawas and so mass-basis.
    #
    # Subtracting the vev fixes both at once.  In unitary gauge the factor becomes
    # ((v+h)^2 - vhat^2)/2 = v h + h^2/2 after redefCtoZero sends vevT -> vevhat, and the operator
    # expands to (2 v^2 h + 3 v h^2 + h^3) * (fbar f)/(2 sqrt2), that is h : hh : hhh = 2 : 3 : 1
    # against the unsubtracted 3 : 3 : 1.  Only the single-Higgs vertex moves, which is exactly
    # the 3/2 measured against SMEFTsim on b b~ > h, and the fermion mass loses its C_fH
    # dependence entirely.
    #
    # SMEFTsim itself gets to the same basis the other way, by compensating in the Yukawa:
    # SMEFTsim_A_parameters.fr defines the Yukawa entering its Standard Model term as
    #     yd0[i,j] -> yd[i,j] (1 - dGf/Sqrt[2]) + vevhat^2/2/LambdaSMEFT^2 Conjugate[cdH] yd[j,i]
    # which gives the same 2 : 3 : 1 and the same mass.  That route needs TWO Yukawa symbols, one
    # for the Standard Model term and one inside the operator, and these operators carry
    # Conjugate[yd[ff2,ff1]] explicitly, so shifting the single symbol we have would scale the
    # operator term and the Standard Model term together and leave their ratio alone, which is
    # what two earlier attempts measured.  Subtracting the vev needs no second symbol, stays
    # exactly linear in C, and conjugates correctly on its own because HC[L6cl50] generates the
    # Hermitian conjugate from the subtracted operator.
    for _o, _hh in (("OeH", "Phibar[jj] Phi[jj]"), ("OuH", "Phibar[kk] Phi[kk]"),
                    ("OdH", "Phibar[jj] Phi[jj]")):
        _i = ops.index(_o + ":=")
        _j = ops.index("ExpandIndices[", _i) + len("ExpandIndices[")
        assert ops[_j:_j + len(_hh) + 1].strip().startswith(_hh), \
            f"{_o}: expected the H^dag H factor first, found {ops[_j:_j+40]!r}"
        ops = ops[:_j] + ops[_j:].replace(_hh, f"({_hh} - z6vev^2/2)", 1)
    print("  class-5 operators vev-subtracted (mass basis)")

    # O_HG, vev-subtracted for the same reason and found the same way, by a test rather than by
    # reading.  (H^dag H) G G has a vacuum piece, v^2/2 G G, which is a correction to the gluon
    # kinetic term.  SMEFTsim removes it by rescaling the gluon field and the strong coupling in
    # opposite directions, which leaves g_s G, and so every interaction, where it was.  The
    # operator as the Warsaw basis writes it, on a base that does no such rescaling, keeps the
    # vacuum piece in the three- and four-gluon vertices and nowhere else: the gluon then couples
    # to itself with a strength different from the one it couples to quarks with.  With cHG on,
    # `check lorentz` failed on five of six gluonic processes at 1/Lambda^2 (u u~ > g g at 1e-2,
    # 2026-10-05), in a model whose g g > h cross section agreed with SMEFTsim's to four digits,
    # because that vertex is the part of the operator that was right.  Subtracting the vacuum
    # piece is the rescaling carried out: -1/4 (1 - x) G G with x = 2 cHG v^2/Lambda^2 becomes
    # canonical in G' = Sqrt[1 - x] G with g' = g/Sqrt[1 - x], and what is left of the operator is
    # cHG (H^dag H - v^2/2) G' G'/(1 - x).  The 1/(1 - x) is a product of two coefficients and is
    # supplied below, to first order, as the rescaling of G inside the operators.
    _i = ops.index("OHG:=")
    _hh = "Phibar[ii] Phi[ii]"
    _j = ops.index("ExpandIndices[", _i) + len("ExpandIndices[")
    assert ops[_j:_j + len(_hh) + 1].strip().startswith(_hh), \
        f"OHG: expected the H^dag H factor first, found {ops[_j:_j+40]!r}"
    ops = ops[:_j] + ops[_j:].replace(_hh, f"({_hh} - z6vev^2/2)", 1)
    print("  O_HG vev-subtracted (canonical gluon)")
    # every operator ends in SMEFTsim's truncation rule; ours has a second step after it
    _n = ops.count("/.redefCtoZero")
    ops = ops.replace("/.redefCtoZero", "/.redefCtoZero//z6trunc")
    print(f"  truncation applied in {_n} operator definitions")

    classes = re.findall(r"^(L6cl[0-9a-d]+)\s*:?=", ops, re.M)
    classes = [c for c in classes if not c.endswith("0")]     # L6cl50 etc. are intermediates
    classes = [c for c in classes if c != "L6cl8"]            # the sum of 8a..8d

    # Every symbol this file defines, checked against every name the base already declares.
    # One such collision (L6) cost a day, so it is a hard error rather than a warning.
    # the base lives in tests/gen_smoke in the development tree and in models/src in the
    # released one, which ships the FeynRules source but not the build directory
    base = next((q for q in (os.path.join(ROOT, "tests/gen_smoke/base_inputscheme.fr"),
                             os.path.join(ROOT, "models/src/base_inputscheme.fr"))
                 if os.path.exists(q)), None)
    if base is None:
        sys.exit("no base_inputscheme.fr under tests/gen_smoke or models/src")
    btxt = open(base).read()
    base_names = {n for n, _ in split_entries(btxt, "M$Parameters")}
    base_names |= set(re.findall(r"ClassName\s*->\s*([A-Za-z][A-Za-z0-9]*)", btxt))
    mine = {n for n, _ in phases + params if n not in IN_BASE and n != SCALE}
    mine |= set(re.findall(r"^([A-Za-z][A-Za-z0-9$]*)\s*:?=", ops, re.M))
    mine |= {"QLm", "sigmaT", "HDH", "WC6", "redefCtoZero", "LambdaSMEFT", "vevhat",
             "z6vev", "z6trunc", "rG1"}
    clash = sorted(mine & base_names)
    if clash:
        sys.exit("name collision with tests/gen_smoke/base_inputscheme.fr: " + " ".join(clash)
                 + "\n  the base's declaration would be replaced by SMEFTsim's definition, "
                   "silently for a parameter and fatally for L6.  Rename in the generator.")

    hdr = f'''(* GENERATED by gen/make_dim6.py.  Do not edit; edit the generator.

   SMEFTsim's dimension-six sector, U(3)^5 flavour symmetric, on the dim8auto Standard
   Model base.  Operator definitions are SMEFTsim's, verbatim and unreinterpreted, so the
   vertices this produces are checkable against SMEFTsim's own UFO.

   Source: SMEFTsim_A_operators_U35.fr and d6_parameters_U35.fr.
   Cite arXiv:1709.06492 for the model and arXiv:2012.11343 for the flavour framework.

   Three couplings to our side of the model:

     LambdaSMEFT is our Lam6, the external dimension-six scale the base declares in block
       DIM6 beside the eight coefficients the {{alpha, MZ, GF}} relations need.

     vevhat is our vevSM, 1/Sqrt[Sqrt[2] Gf], which is what SMEFTsim's vevhat is too.

     redefCtoZero is SMEFTsim's own truncation, applied unchanged.  It sets the dimension-six
       coefficients to zero inside an operator's own expansion and replaces the corrected vev
       by the uncorrected one, which is what makes the dimension-six sector linear and what
       makes it agree with SMEFTsim vertex by vertex.

   {len(keep)} coefficients are declared here.  {len(skipped)} more are dimension-six and live:
   {" ".join(sorted(skipped))}, declared by the base because the input relations use them.
   Every coefficient is ZERO by default.  SMEFTsim ships them at one.
*)

'''
    body = ["(* ---- SMEFTsim's CKM-free quark doublet, which our base does not declare ---- *)",
            "M$ClassesDescription = {", "  " + qlm.rstrip().rstrip(";").rstrip(), "};", "",
            "M$Parameters = {", ",\n".join(keep + ([] if a.linear else [RG1])), "};", "",
            "(* ---- helpers the operator file uses, from SMEFTsim_A_main.fr, verbatim ---- *)",
            sigmat, "", hdh, "",
            "(* ---- the couplings to our side, before the operators are read ---- *)",
            "LambdaSMEFT := Lam6;",
            "vevhat := vevSM;",
            "WC6 = {" + ", ".join(wc6) + "};",
            *(TRUNC_LINEAR if a.linear else TRUNC_SECOND),
            "",
            "(* ---- SMEFTsim's operator definitions, verbatim ---- *)",
            ops.rstrip(),
            "",
            "(* the classes this file defines, for DIM8_LSM *)",
            "DIM6$Classes = {" + ", ".join('"%s"' % c for c in classes) + "};",
            ""]
    open(a.o, "w").write(hdr + "\n".join(body))
    print(f"wrote {os.path.relpath(a.o, ROOT)}")
    print(f"  {len(keep)} coefficients declared, {len(skipped)} left to the base")
    print(f"  {len(wc6)} names in WC6")
    print(f"  classes: {' '.join(classes)}")


if __name__ == "__main__":
    main()
