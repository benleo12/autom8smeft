# autom8smeft

A SMEFT model for MadGraph5_aMC@NLO carrying both sectors: all 674 baryon-number-conserving
dimension-eight operators, and the dimension-six operators in the U(3)^5 flavour-symmetric
framework. The `{alpha, MZ, GF}` input relations are corrected to `1/Lambda^4` and include the
dimension-six squares, so cross sections can be computed to that order for any process MadGraph
can generate.

Dimension-eight tabulation: arXiv:2005.00059, whose naming and class numbering this model follows.
Dimension six is SMEFTsim's, arXiv:1709.06492 with the flavour framework of arXiv:2012.11343, put
on the same base, with the same vertices at `1/Lambda^2`: see [docs/DIM6.md](docs/DIM6.md).

## Install

    ln -s /path/to/autom8smeft/models/dim68_is  /path/to/MG5_aMC/models/dim68_is

## Use

    import model dim68_is
    generate p p > w+ w- NP^2==2
    output ww
    launch ww
    set nevents 5000
    set ebeam1 6800
    set ebeam2 6800
    set hel_recycling False
    set lam__2 1000
    set c8q2W2Dx1 1.0
    done

-1.189 +- 0.003 pb, the dimension-eight interference of `Q_{q^2W^2D}^{(1)}` at 13.6 TeV with
Lambda = 1 TeV. `hel_recycling False` is required. Set the beam energies, MadGraph defaults to
6500.

Two scales, because nothing forces them equal: `lam__2` is the dimension-eight scale in the param
card, block `DIM8` index 0, and `lam6` the dimension-six one, block `DIM6` index 1. `Lam`
lowercases onto the Standard Model quartic `lam`, which is why MadGraph renames it `lam__2`.

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

That `NP^2==2` mixes the two is the power counting, not a bug: both are `1/Lambda^4` and a
consistent calculation at that order needs both. To separate them, switch one sector off in the
param card.

## Getting the orders right

Every coupling of the model carries a definite `NP` order: the shifts of the gauge couplings, the
vev, the Yukawas and the Higgs quartic by the input scheme are written into the Lagrangian as
tagged series, so the `NP=0` amplitude is the Standard Model. One derived quantity cannot be
tagged, because it is a mass and not a coupling: in the `{alpha, MZ, GF}` scheme `M_W` shifts with
eight of the coefficients. Its effect is therefore not in `NP^2==2`, and the complete
`1/Lambda^4` prediction is

    sigma(1/Lambda^4) = sigma(NP^2==2, c) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]

The bracket is zero in any process in which no W is produced or exchanged. With every coefficient
at 1 and Lambda at 1 TeV it is +1.40 +- 0.25 pb in `p p > w+ w-` against an interference of
-4.0 pb, and 6.8 per cent of the cross section in `p p > h h j j QCD=0`, where the W sits in the
two t-channel propagators. `examples/studies/run_study.sh` runs the `NP=0` row both ways for you
(rows `NP=0` and `NP=0 on`).

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
`c8q2W2Dx1` is `Q_{q^2W^2D}^{(1)}` in block `DIM8`, and the 81 dimension-six coefficients keep
SMEFTsim's names in block `DIM6`, alongside `Lam6` at index 1. `models/dim68_is/param_card_template.dat` lists them with
operator and class.

A complex coefficient is not itself external: it is built from `<name>Abs` and `<name>Ph`, so set
`cuGAbs`, not `cuG`. MadGraph only **warns** on a `set` it does not recognise and carries on, so
read the value back out of the run's param card rather than trusting the command.

## What you need

Nothing but python3 for the model itself: the restriction cards, the operator selector, the
catalogue and the parameter evaluation are pure standard library. MadGraph needs its own
python3.11 (see below). Four of the validation scripts want `numpy` (`validate/zero_lorentz.py`,
`zero_vertex.py`, `zero_vertex_dirac.py`, `b4_normalisation.py`) and two want `sympy`
(`gen/derive_input_scheme.py`, `gen/derive_rotation.py`); each says so if the module is missing.
Rebuilding the FeynRules models needs Mathematica 14.2 or earlier with FeynRules 2.3.49, and
nothing in the shipped model does. The operators themselves are `gen/operators.py`, one object
per operator in block order, from which `./dim8 build` emits the FeynRules Lagrangian before it
computes the vertices; `models/src/README.md` describes the source files.

Two things are deliberately not redistributed and every script that wants one says which and
where to get it: SMEFTsim's FeynRules sources (for `gen/make_dim6.py`, set `$SMEFTSIM_FR`), and
SmeftFR's model files (for the class-by-class comparison in `validate/smeftfr_by_class/`).

Run MadGraph through **python3.11**. From Python 3.13 the `locals()` change of PEP 667 breaks
MadGraph's `model_reader` and every restricted model fails to import with `Unable to evaluate
mdl_L6 = mdl_Lam6**(-2)`, which looks like a broken restriction card and is not one.

27 restriction cards ship: one per dimension-eight class, plus `bosonic`, `cpeven`, `cpodd` and
`all`, plus `dim6` and `both` for the two sectors. Separating the sectors is how you read
`NP^2==2`, which holds the dimension-six square and the dimension-eight interference together.

`cpeven` and `cpodd` keep the 285 and 153 operators whose coefficient is real and whose CP parity
is even or odd. The parity is DERIVED, field by field, as C times P: P gives one minus sign per
dual field strength, C sends `B -> -B`, `W^I -> -s_I W^I`, `G^A -> -s_A G^A` and `H -> H^*` with
`s = +1` for a symmetric generator and `-1` for an antisymmetric one, so `eps^{IJK}` and `f^{ABC}`
each contribute `-1` and the symmetric and antisymmetric parts of a fermion bilinear carry
opposite signs.

That is not the same as counting dual field strengths, and the difference is 170 of the 438
operators with a real coefficient. The clearest case is `Q_{q^2W^2D}^{(1..4)}`, where the
derivation gives even, ODD, even, even: the member with no dual is the CP-odd one. Two earlier
versions of this card counted instead, and the CP test `validate/cp_rates.py` measures the
difference as a 1.2 pb interference on `p p > w+ w-` where a CP-odd set must give zero.
`gen/cp_parity.py` is the single place the parity is decided.

    import model dim68_is-cls14
    import model dim68_is-dim6

`validate/make_restriction.py` writes any other selection. `./dim8 select "p p > w+ w-"` lists
which dimension-eight operators can enter a process.

## Try it

    export MG5_DIR=/path/to/MG5_aMC
    examples/studies/run_study.sh examples/studies/quickstart models/dim8_is 2000

`p p > w+ w-` with two operator classes, about half an hour on two cores.
`examples/studies/quickstart/README.md` lists the numbers to expect and what to change next.
It runs on the dimension-eight model because those numbers are the ones that have been checked.
The same driver takes `models/dim68_is`, which gives the same answers with the dimension-six
coefficients at zero and generates a great many more diagrams to do it, since `NP^2==2` then
admits dimension-six pairs as well.

[docs/RUN_YOUR_OWN_ANALYSIS.md](docs/RUN_YOUR_OWN_ANALYSIS.md) goes from a process to cross
sections.

## Limits

Flavour universal, one coefficient per operator, so the basis's `p, r, s, t` collapse to `p = r`
and `s = t`. `Q_{udWH^2}^{(1)}` and `Q_{udWH^2}^{(2)}` vanish identically as written, whatever the
flavour structure, because `epsilon tau^I` is symmetric for all three `I` while `epsilon` is
antisymmetric; their coefficients are in the card and do nothing. A further set vanishes because
of flavour universality alone, leaving 915 of the 1030 `DIM8` coefficients with a vertex in the
model.

The dimension-six sector is complete at `1/Lambda^4`. Its `NP=1` vertices are SMEFTsim's, and
checkable against its shipped UFO. The products of a dimension-six operator with the first-order
shifts of the input scheme, which are `1/Lambda^4` terms, are separate couplings of order `NP=2`,
so that the dimension-six squared contribution is gauge invariant and the two-point terms are
canonical at that order. See [docs/DIM6.md](docs/DIM6.md).

The 60 baryon-number-violating operators are not included.

`models/dim8_is` is the dimension-eight sector alone, `models/dim8_mw` is the same sector in the
`{MW, MZ, GF}` input scheme, in which both masses are inputs, alpha is derived and no mass moves
with a coefficient (so the `NP=0` bracket above is absent, and its `NP=0` matrix element is
identical to every digit with the coefficients on and off), and `models/dim8_plain` puts the same
operators on the plain FeynRules Standard Model, for cross-checks. Set `MW` to 79.82435975 in
`dim8_mw` to put it on the same numerical point as `dim8_is`, whose derived W mass that is. The param card of `dim8_is`
still has a block `DIM6`, with the eight dimension-six coefficients its input relations are
written in. Leave them at zero there: that model has their effect on the inputs and not the
operators themselves, which is half a calculation. Dimension six is what `dim68_is` is for.
