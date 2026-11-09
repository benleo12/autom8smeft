# autom8smeft

SMEFT models for MadGraph5_aMC@NLO with all 674 baryon-number-conserving dimension-eight operators,
with minimal flavour violation for the fermionic ones, alone or beside the dimension-six operators in
the U(3)^5 flavour-symmetric framework, each in two input schemes:

| model | operators | input scheme |
| --- | --- | --- |
| `dim8_mw` | dimension eight | `{MW, MZ, GF}` |
| `dim8_is` | dimension eight | `{alpha, MZ, GF}` |
| `dim68_mw` | dimension six and eight | `{MW, MZ, GF}` |
| `dim68_is` | dimension six and eight | `{alpha, MZ, GF}` |

Each also comes in the Murphy basis, under the same name with the suffix `_murphy` (`dim8_mw_murphy`
and so on).

The input relations are corrected to `1/Lambda^4`, with the dimension-six squares in the models
that carry both sectors, so cross sections can be computed to that order for any process MadGraph
can generate. A model with one sector generates far fewer diagrams.

The dimension-eight operators are those of the Murphy basis, arXiv:2005.00059, whose naming and
class numbering the models follow, with one change. The default models replace the fifteen operators
of class 11, `psi^2H^2D^3`, by fifteen operators of the same class in which every Higgs field carries
a derivative, those of arXiv:2306.00053 extended to every fermion current, so that the two- and
three-point functions of the models are those of the geometric SMEFT. The models with the suffix
`_murphy` keep the Murphy basis. `gen/basis.py` defines the two sets and relates their coefficients.
Dimension six is SMEFTsim's, arXiv:1709.06492 with the flavour
framework of arXiv:2012.11343, put on the same base, with the same vertices at `1/Lambda^2`: see
[docs/DIM6.md](docs/DIM6.md).

## Install

The models ship packed, since each is about a gigabyte unpacked. Unpack them in `models/`:

    cd models && for f in *.tar.xz; do tar -xJf $f; done

`shasum -a 256 -c dim68_is.sha256`, run in `models/`, checks a model against the list of its files.
Then link a model into MadGraph:

    ln -s /path/to/autom8smeft/models/dim68_is  /path/to/MG5_aMC/models/dim68_is

and the same for each of the other models you want. The scripts of this repository read the
unpacked directories.

## Use

    import model dim68_is
    generate p p > w+ w- NP^2==2
    output ww
    launch ww
    set nevents 5000
    set ebeam1 6800
    set ebeam2 6800
    set hel_recycling False
    set Lam 1000
    set c8q2W2Dx1 1.0
    done

-1.180 +- 0.006 pb, the dimension-eight interference of `Q_{q^2W^2D}^{(1)}` at 13.6 TeV with
Lambda = 1 TeV. `hel_recycling False` is required. Set the beam energies, MadGraph defaults to
6500.

Two scales, because nothing forces them equal: `Lam` is the dimension-eight scale in the param
card, block `DIM8` index 0, and `Lam6` the dimension-six one, block `DIM6` index 1.

## Orders

`NP` counts powers of `1/Lambda^2`, so a dimension-six insertion is one unit and a dimension-eight
insertion is two. `NP^2==n` constrains the sum over the two amplitudes.

| selection | what it is |
| --- | --- |
| `NP=0` | Standard Model |
| `NP^2==1` | dimension-six interference, `1/Lambda^2` |
| `NP^2==2` | dimension-six squared **and** dimension-eight interference, both `1/Lambda^4` |
| `NP^2==4` | dimension-eight squared, `1/Lambda^8` |
| `NP<=2` | everything up to one dimension-eight or two dimension-six insertions |

`NP^2==2` mixes the two because of the power counting: both are `1/Lambda^4` and a consistent
calculation at that order needs both. To separate them, switch one sector off in the
param card.

## Getting the orders right

Every coupling of the model carries a definite `NP` order: the shifts of the gauge couplings, the
vev, the Yukawas and the Higgs quartic by the input scheme are written into the Lagrangian as
tagged series, so the `NP=0` amplitude is the Standard Model. One derived quantity cannot be
tagged, because it is a mass and not a coupling: in the `{alpha, MZ, GF}` scheme `M_W` shifts with
nine dimension-eight entries of the card, those of six operators (`c8H6x2`, `c8W2H4x3`, `c8WBH4x1`,
`c8l2H4Dx2` and `c8l2H4Dx4` with their structures `c8l2H4Dx2FE` and `c8l2H4Dx4FE`, and the structures
`c8l4H2x1Fx00` and `c8l4H2x1Fx0E` of `Q_{l^4H^2}^{(1)}`), and in `dim68_is` with `cHDD`, `cHl3`,
`cHWB` and `cll1` as well. Its effect is therefore not in `NP^2==2`, and the complete
`1/Lambda^4` prediction is

    sigma(1/Lambda^4) = sigma(NP^2==2, c) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]

The bracket is zero in any process in which no W is produced or exchanged. With every coefficient
at 1 and Lambda at 1 TeV it is +1.19 +- 0.13 pb in `p p > w+ w-` against an interference of
-3.6 pb, and 5.9 +- 0.4 per cent of the cross section in `p p > h h j j QCD=0` (with `ptj` = 25 GeV,
`etaj` = 5 and `mmjj` = 400 GeV), where the W sits in the two t-channel propagators. `examples/studies/run_study.sh` runs the `NP=0` row both ways for you
(rows `NP=0` and `NP=0 on`). In the `{MW, MZ, GF}` models `M_W` is an input and no mass moves with a
coefficient, so there is no bracket and `NP^2==2` is the whole term.

A model-independent cross-check is to scan one coefficient with no `NP^2` constraint and fit the
polynomial:

    validate/order_fit.py dim68_is "p p > e+ e-" --coeff cHq1 --scale6 1000

`sigma_0` is the Standard Model, `sigma_1` the interference, `sigma_2` the square, no tag
involved, and `--compare-tagged NP^2==1` runs the tagged bin beside it.

And test any class you rely on for linearity: a term linear in a coefficient falls as
`1/Lambda^4`, so its value at 1 TeV is 16 times its value at 2 TeV.

    validate/lambda_scaling.py --proc ww

## Coefficients

Every Wilson coefficient is an external parameter, zero by default, named after its operator:
`c8q2W2Dx1` is `Q_{q^2W^2D}^{(1)}` in block `DIM8`, and the 85 dimension-six coefficients keep
SMEFTsim's names in block `DIM6`, alongside `Lam6` at index 1. `models/dim68_is/param_card_template.dat` lists them with
operator and class.

The flavour structures beyond the leading one of each fermionic operator have coefficients of their
own in block `DIM8F`, named after the operator's coefficient. `c8l2H4Dx2FE` is `Q_{l^2H^4D}^{(2)}`
with one insertion of `Y_e Y_e^dag` on the lepton current, and `c8l4H2x1Fx00` is `Q_{l^4H^2}^{(1)}`
with its fields paired across the two currents and no insertion. `gen/emit_flavour.py` gives the rule
for every name.

A complex dimension-eight coefficient appears as `<name>Re` and `<name>Im`, as `c8leWH3x1Re` and
`c8leWH3x1Im`. A complex dimension-six coefficient is not itself external: it is built from
`<name>Abs` and `<name>Ph`, so set `cuGAbs`, not `cuG`. MadGraph only **warns** on a `set` it does not recognise and carries on, so
read the value back out of the run's param card rather than trusting the command.

## What you need

Nothing but python3 for the model itself: the restriction cards, the operator selector,
`./dim8 series`, the catalogue and the parameter evaluation are pure standard library. MadGraph
needs its own python3.11 (see below). Fifteen of the validation scripts want `numpy`
(`validate/zero_lorentz.py`, `zero_vertex.py`, `zero_vertex_dirac.py`, `b4_normalisation.py`,
`onshell_zero.py`, `drop_zero_structures.py`, `audit_ufo.py`, `compare_ufo.py`, `flavour_rank.py`,
`mfv_generic.py`, `vertex_contract.py`, `g4_highleg.py`, `x4_polynomial.py`, `dim6_vs_smeftsim.py`,
`vs_matchete_ufo.py`) and four want `sympy` (`gen/derive_input_scheme.py`, `gen/derive_rotation.py`,
`gen/derive_higgs_yukawa.py`, `gen/derive_geo.py`).
Rebuilding the FeynRules models needs Mathematica 14 or 15 with FeynRules 2.3.49, a Python with `numpy`
(`DIM8_NUMPY_PY` names it) and MadGraph (`MG5_DIR`), and nothing in the shipped model does. The
operators themselves are encoded in `gen/operators.py`,
one typed object per operator, from which `./dim8 build` writes the FeynRules Lagrangian before it
computes the vertices. To correct an operator, edit its entry and run `./dim8 rebuild`, which goes from
that file to the released models. `models/src/README.md` describes the steps, the source files and what
more an operator of the input relations needs.

Four things are deliberately not redistributed and every script that wants one says which and
where to get it: SMEFTsim's FeynRules sources (for `gen/make_dim6.py`, set `$SMEFTSIM_FR`),
SmeftFR's model files (for the class-by-class comparison in `validate/smeftfr_by_class/`),
SMEFTsim's U(3)^5 UFOs of the two schemes (for the vertex-by-vertex comparison of the dimension-six sector,
`validate/dim6_vs_smeftsim.py`) and the Murphy-basis UFO of the Matchete model database (for the
comparison of the dimension-eight sector, `validate/vs_matchete_ufo.py`). The two vertex
comparisons want `numpy`.

Run MadGraph through **python3.11**. From Python 3.13 the `locals()` change of PEP 667 breaks
MadGraph's `model_reader` and every restricted model fails to import with `Unable to evaluate
mdl_L6 = mdl_Lam6**(-2)`, which looks like a broken restriction card and is not one.

Each model's `__init__.py` ends with two fixes to MadGraph, which `examples/mg5_fixes.py` explains.
The first is for a naming bug of MadGraph's ALOHA, which without it stops `p p > e+ e- g` and a few
other processes at the link step with an undefined `ALOHA_...P0` routine. It leaves every routine
name that MadGraph already gets right. The second makes MadGraph's renaming of the parameters to
`mdl_<name>` one pass over the expressions, which otherwise takes more than an hour of every import
of these models (about two minutes with the fix, for `dim8_is` on a Mac mini), with the same result. Nothing
needs to be done with MadGraph itself. The first import also compiles the model's Python files and needs
7.7 GB of memory, and later ones need 2.4 GB.

Restriction cards ship with every model: one per dimension-eight class, plus `bosonic`, `cpeven`,
`cpodd` and `all`, which keeps every dimension-eight coefficient. `dim68_is` and `dim68_mw` have
`dim6`, `dim8` and `both` in place of `all`, for the two sectors apart and together. Separating the sectors is how you read
`NP^2==2`, which holds the dimension-six square and the dimension-eight interference together.
A card that keeps an operator keeps its structures in `DIM8F` as well.

The cards hold the inputs of the default card: `cabi` = 0, and the Yukawa couplings of the leptons
and of every quark but the bottom and the top zero. MadGraph removes every coupling that vanishes on the card, so a
restricted model has no vertex that only these Yukawa couplings or the Cabibbo angle make. To keep
those vertices, write a card with the inputs you want:

    python3 validate/make_restriction.py models/dim8_mw cls12c cls:12 ymc=1.27 cabi=0.227

`cpeven` and `cpodd` keep the coefficients of each CP parity, each part of a complex coefficient and
each flavour structure in the card of its own parity. Of the operators with a real coefficient, 285
are CP even and 153 CP odd. The parity is DERIVED, field by field: `CP(Q) = eta Q^dag`, with `eta` the
product of `+1` for a scalar bilinear and `-1` for a vector or tensor bilinear, `-1` for a field
strength and `+1` for a dual one, `-1` for each `eps^{IJK}` or `f^{ABC}`, `+1` for `d^{ABC}` and
for every Higgs factor, and `-1` for each explicit `i`. An operator that is Hermitian as written
has parity `eta` and an anti-Hermitian one `-eta`. For a complex coefficient the real part has
`eta` and the imaginary part `-eta`, which `docs/catalogue.json` records as "Re even, Im odd" or
"Re odd, Im even". Of the 236 complex operators, 44 have a CP-odd real part.

That is not the same as counting dual field strengths, and the difference is 170 of the 438
operators with a real coefficient. The clearest case is `Q_{q^2W^2D}^{(1..4)}`, where the
derivation gives even, ODD, even, even: the member with no dual is the CP-odd one. The CP test
`validate/cp_rates.py` checks the card. A CP-odd set must give zero interference in a total rate,
and a set chosen by counting duals gives -0.0152 pb on `p p > w+ w-` in `dim8_mw`, with its
coefficients at one and `Lam` = 3 TeV, where the derived set gives zero. The parity of each operator is recorded as `cp` in `gen/operators.py`, and
`gen/cp_parity.py` checks the record against the encoded terms at every build.

    import model dim68_is-cls14
    import model dim68_is-dim6

`validate/make_restriction.py` writes any other selection. `./dim8 select "p p > w+ w-"` lists
which dimension-eight operators can enter a process, in two groups: those with a vertex in some
tree diagram, each with the vertex of its leading tree and that tree's power of lambda, and those
with none that enter through the input relations of the model's scheme. With `--card ww` it
writes `restrict_ww.dat` into the model (`models/dim8_mw`, the `{MW, MZ, GF}` scheme, unless
`--model` names another), keeping both groups, for `import model dim8_mw-ww`.
With `--model dim68_is` it lists the dimension-six coefficients as well, one by one under their
Warsaw classes, from `build/dim6_index.json`, the vertices of each coefficient, which
`python3 validate/dim6_index.py` writes from the released models. The vertices of a coefficient
include the Standard Model vertices it rescales, as `C_HBox` rescales h W W, h Z Z and the Yukawa
couplings through the normalisation of the Higgs field, counted at their own power of lambda and
four more. A coefficient with no vertex in a tree of the process can still enter at `1/Lambda^4`
where the Standard Model has a tree, through a tree with a second dimension-six vertex or through a
vertex at `NP=2` that multiplies it by a second coefficient or by itself, as the vev shift of
`C_Hl^(3)` multiplies the chromomagnetic vertex of `C_uG`, and is listed with the remark "only with
a second dimension-six insertion, of this coefficient or another". `--with-dim6` keeps exactly the
listed coefficients in the card, those of the input relations included, and without it the card
zeroes the dimension-six sector. `dim8_mw` and `dim8_is` have no dimension-six sector and refuse
the option.
`--max-power N` cuts the card to the operators and coefficients listed at most N powers of lambda
above the Standard Model amplitude, which the header of the listing gives, those that grow fastest
with energy relative to it. In `p p > w+ w-` the Standard Model is at lambda^0, and
`./dim8 select "p p > w+ w-" --max-power 4 --card ww4` keeps the 13 of the 99 that reach lambda^4
(E^4/Lambda^4). In `u u~ > z h` it is at lambda^1, and `--max-power 4` keeps those at lambda^5 or
below. An operator of the input relations, eight powers above the Standard Model at dimension eight
and four at dimension six, is kept at that power, and one listed without a power is left out, except
a dimension-six coefficient that enters only with a second insertion, whose power the counting does
not give. Where the powers are left out (a longitudinal mark without the Feynman-gauge lists), or the
Standard Model has no tree to count from, the cut stops and writes nothing.
FeynRules has already been run and the shipped model carries all its operators,
so a selection is a restriction card that MadGraph applies at import, never a rebuild.
`validate/select_complement.py` checks the dimension-eight selection by keeping its complement
instead, which must generate no diagram. It does not check the dimension-six one, since a
coefficient whose couplings cancel between vertex objects, as the gauge vertices of `C_HW` cancel
against the rescaling of the W field, keeps those couplings in a restricted model, and MadGraph
would draw diagrams that vanish, and since a coefficient that enters only together with a selected
one, as `C_HW` does with `C_W` in `p p > w+ w-`, does nothing while that one is zeroed.
`validate/select_complement6.py "p p > w+ w-" --model models/dim68_mw` checks the dimension-six one
by matrix elements: at random coefficient values and phase-space points, in every subprocess, at
`NP^2==1` and at `NP^2==2`, `|M|^2` with every dimension-six coefficient on must equal `|M|^2` with
only the kept ones on.

## Commands

The selector and the energy counting run on python3 alone, from the vertex lists that ship in
`build/`. `./dim8 -h` lists every command.

| command | what it gives |
| --- | --- |
| `./dim8 select "p p > w+ w-"` | the operators that can enter the process, each with the vertex of its leading tree and that tree's power of lambda, then those that enter through the input relations, and with `--model dim68_is` the dimension-six coefficients one by one. `--card NAME` writes both groups into a restriction card |
| `./dim8 series "u u~ > w+ w-"` | the amplitude topology by topology as a series in lambda, the Standard Model couplings and the dimension-six and dimension-eight classes side by side, without the terms that cannot interfere with the Standard Model |
| `./dim8 count psi^2X^2D` | the leading power of lambda of the vertices of a class, by their number of legs (`all` gives every class) |
| `./dim8 model "p p > h j j" -o vbf` | a FeynRules model file holding only the operators of the process |
| `./dim8 ufo "p p > h j j" -o vbf` | the UFO of those operators, which needs Mathematica, FeynRules and the vertices of `./dim8 build` |
| `./dim8 rebuild` | every step from `gen/operators.py` to the released models, with Mathematica, FeynRules, `numpy` and MadGraph (`models/src/README.md`). `--dry-run` shows the steps, which needs none of them |
| `./dim8 build`, `./dim8 index` | the checks of the encoding and the vertices of every operator, and the vertex lists the selector reads, with Mathematica and FeynRules. `./dim8 build --source-only` needs neither |

The powers are those of the energy counting of arXiv:2504.10617, (Lambda, E, v) ~ (lambda^-3,
lambda^-2, lambda^-1). No Standard Model tree of n external particles lies below lambda^(2n-8), and
the header of each command gives the power of the process's own leading trees, lambda^0 in
`p p > w+ w-` and lambda^3 in `p p > h j j`, whose Higgs boson couples through a vev. A smaller
power is a larger contribution in the tails. A dimension-eight term Delta powers above the Standard
Model grows as E^(8-Delta) v^(Delta-4)/Lambda^4 relative to it, and a dimension-six term as
E^(4-Delta) v^(Delta-2)/Lambda^2. A power predicts which operators grow
fastest in the tails, E >> v, and says nothing about the inclusive rate.
[docs/RUN_YOUR_OWN_ANALYSIS.md](docs/RUN_YOUR_OWN_ANALYSIS.md) gives the weights of the counting
and says which trees count.

`./dim8 select` and `./dim8 series` take MadGraph's polarisation marks on a W or a Z. `w+{T}`, like
an unmarked `w+`, is the transverse W, and `w+{0}` the longitudinal one, counted by the equivalence
theorem as its Goldstone boson or as the gauge boson at one more power of lambda. The Goldstone
vertices come from the Feynman-gauge vertex lists, `build/vertex_index_fg.json` and
`build/sm_vertices_fg.json`, which are made in Feynman gauge with Mathematica and FeynRules and
ship in `build/` with the release. Without them `./dim8 select` prints the operators of a `{0}`
channel, and writes its card, with no powers and a note saying why, while `./dim8 series` refuses a
`{0}` mark and counts the other channels with the unitary-gauge lists, which is exact wherever every
internal W or Z ends on a light quark or lepton. The dimension-six coefficients of `dim68_is` are
printed with no powers in every `{0}` channel, with the Feynman-gauge lists or without them, and a
note says why: `build/dim6_index.json` is read from the unitary-gauge model and holds no Goldstone
vertex.

For example,

    ./dim8 series "u u~ > w+ w-"

starts with the process, its four external legs and the gauge of the vertex lists it used, then the
power of the Standard Model amplitude, lambda^0 here, and the remark that an unmarked W is counted
as transverse. The terms follow in three groups, `A_s`, `A_t` and `A_c`: the s channel, the t
channel with the u channel merged into it, as for any quark-antiquark initial state, and the
contact terms. A line of the Standard Model gives a power of lambda, `SM` and every product of
Standard Model couplings that reaches that power. A line of a class gives the power, the dimension
(`dim 6`, `dim 8`), the class (of the Warsaw basis at dimension six, as `psi^2H^2D`, and of the
Murphy basis at dimension eight, as `psi^2X^2D`), the products of couplings, the growth relative to
the Standard Model, and up to three of its operators (for a dimension-six class, its Lagrangian in
the model, `L6cl1` to `L6cl8d`). In the products `g_qqV` couples a quark pair to a photon, Z or W,
`g_VVV` is the triple-gauge coupling and `m_t` a top mass insertion, and a term with no coupling at
all reads `(contact)`. A star after the class marks a dimension-eight term at most four powers of
lambda above the Standard Model, which grows at least as E^4/Lambda^4 relative to it. A remark in
its place says that the term interferes some powers down, by the powers of lambda by which the
Standard Model trees with the same chiralities of the external quarks and leptons lie above the
leading ones (two for the right-handed quarks of q q~ > W+W-, whose photon and Z trees cancel up to
M_Z^2/E^2), or by m_t/E for each external top quark of the other chirality.

Below the terms come the classes left out because none of their operators interferes with the
Standard Model at leading order in the light fermion masses, the number of operators of the printed
classes left out for the same reason, and the dimension-eight classes with no tree, which enter
through the input relations or not at all. Until they are built, a note says that the Feynman-gauge
lists or `build/onshell_zero.json` are missing. The second is written by
`python3 validate/onshell_zero.py` from the released models, and without it a three-point vertex of
two light fermions is counted even where it vanishes on shell. The same command with
`u u~ > w+{0} w-{0}` gives the longitudinal channel, `--latex` writes the series as a LaTeX align
block, `--json` gives every term with its couplings, operators and external legs, and `--vbf` gives
vector-boson fusion in the effective-W approximation, as in
`./dim8 series "p p > h h j j QCD=0" --vbf`. `./dim8 series -h` prints every rule.

## Try it

    export MG5_DIR=/path/to/MG5_aMC
    examples/studies/run_study.sh examples/studies/quickstart models/dim8_is 2000

`p p > w+ w-` with two operator classes, about two hours with `DIM8_CORES=4` and longer on the
default two cores.
`examples/studies/quickstart/README.md` lists the numbers to expect and what to change next.
It runs on the dimension-eight model because those numbers are the ones that have been checked.
The same driver takes `models/dim68_is`, which gives the same answers with the dimension-six
coefficients at zero and generates a great many more diagrams to do it, since `NP^2==2` then
admits dimension-six pairs as well.

[docs/RUN_YOUR_OWN_ANALYSIS.md](docs/RUN_YOUR_OWN_ANALYSIS.md) goes from a process to cross
sections.

## Limits

Minimal flavour violation at dimension eight, with the Yukawa matrices as the only spurions that
break U(3)^5. For each fermionic operator the models carry every invariant flavour structure with at
most one `Y Y^dag` insertion per fermion bilinear, the second contraction of a four-fermion operator
whose fields can be paired into currents in two ways, and the structures of a four-fermion operator
with an insertion on each bilinear. The leading structure takes a Kronecker delta for a bilinear of
one species and the Yukawa matrix between two species, `Y_u` for `qbar u`, `Y_d` (with the CKM
matrix) for `qbar d`, `Y_e` for `lbar e` and `Y_u^dag Y_d` for `ubar d`. It keeps the operator's
coefficient in block `DIM8`, and every other structure has its own coefficient in block `DIM8F`. In
all the 585 fermionic operators carry 2247 structures with 3315 real parameters: 572 leading
structures, 147 second contractions without an insertion, 1485 structures with one insertion and 43
with an insertion on each bilinear. So an operator that flips chirality, or carries the right-handed
charged current `ubar gamma^mu d`, acts on light quarks only through their Yukawa couplings, in the
square as well as in the interference, and on the top quark at full strength.
`DIM8_FLAVOUR=universal ./dim8 rebuild` writes the models with a delta on every bilinear instead.

The leading structures of thirteen operators vanish because their currents are flavour diagonal:
`Q_{q^4H^2}^{(5)}` and the twelve four-fermion field-strength operators with two identical currents
(`l^4B`, `q^4B`, `e^4B`, `u^4B`, `d^4B`), which are then symmetric in the Lorentz indices of an
antisymmetric field strength. Their coefficients in `DIM8` have no vertex, so 897 of the 1030 `DIM8`
coefficients of the basis have one, the others being these thirteen and the 120 entries of the
baryon-number-violating operators. All of the thirteen but `Q_{e^4B}^{(2)}` have vertices through
their structures in `DIM8F`, which tell the two currents apart, and `Q_{e^4B}^{(2)}` has none.
(`Q_{udWH^2}^{(1,2)}` as printed in the Murphy basis vanish identically, whatever the flavour
structure, and are encoded in the form that does not.)

The dimension-six sector is complete at `1/Lambda^4`. Its `NP=1` vertices are SMEFTsim's, and
checkable against its shipped UFO. The products of a dimension-six operator with the first-order
shifts of the input scheme, which are `1/Lambda^4` terms, are separate couplings of order `NP=2`,
so that the dimension-six squared contribution is gauge invariant and the two-point terms are
canonical at that order. See [docs/DIM6.md](docs/DIM6.md).

The 60 baryon-number-violating operators are not included.

`models/dim8_is` is the dimension-eight sector alone, `models/dim8_mw` is the same sector in the
`{MW, MZ, GF}` input scheme, in which both masses are inputs, alpha is derived and no mass moves
with a coefficient (so the `NP=0` bracket above is absent, and its `NP=0` matrix element is
identical to every digit with the coefficients on and off). Set `MW` to 79.82435975 in
`dim8_mw` to put it on the same numerical point as `dim8_is`, whose derived W mass that is. The input
relations of both are also written in eight dimension-six coefficients, which these two models fix at
zero, so that their param cards have no block `DIM6`: set alone, one of them would have its effect on
the inputs and not the operator itself, which is half a calculation. Dimension six is what `dim68_is`
and `dim68_mw` are for.
