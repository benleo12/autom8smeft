# autom8smeft

A validated dimension-eight SMEFT model for MadGraph5_aMC@NLO: all 674 baryon-number-conserving
operators of the Murphy basis (arXiv:2005.00059), generated from the paper's tables by an
automated FeynRules pipeline, together with the tooling to turn "what does dimension eight do to
process X" into cross sections, tables and distributions for any process MadGraph can generate.

You do not need Mathematica, FeynRules or anything in this repository except the model directory.

**Start with [docs/RUN_YOUR_OWN_ANALYSIS.md](docs/RUN_YOUR_OWN_ANALYSIS.md)** if you have a
process in mind. It goes from installing the model to the LaTeX tables and the figures, and it
tells you the two things about MadGraph's coupling orders that will otherwise give you a wrong
number without an error message.

**Read [docs/HOW_TO_BREAK_IT.md](docs/HOW_TO_BREAK_IT.md)** before you trust a number. It is the
adversarial companion: what has been validated and at what level, where the model is most likely
still wrong, and the traps that look like physics failures and are not. It is deliberately
unflattering.

## Install

Copy or symlink `models/dim8_is` into MadGraph's `models/` directory under the same name:

    ln -s /path/to/dim8auto/models/dim8_is  /path/to/MG5_aMC/models/dim8_is

## Use

    import model dim8_is
    generate p p > w+ w- NP^2==2
    output ww_int
    launch ww_int
    set nevents 5000
    set ebeam1 6800
    set ebeam2 6800
    set hel_recycling False
    set lam__2 1000
    set c8q2W2Dx1 1.0
    done

That gives -1.189 +- 0.003 pb, the dimension-eight interference of `Q_{q^2W^2D}^{(1)}` with the
Standard Model at 13.6 TeV with Lambda = 1 TeV. Four notes on the lines that are not obvious.

`NP` counts powers of 1/Lambda^2, so a dimension-eight insertion is two units and `NP^2==2` is
the interference, `NP<=2 NP^2==4` the dimension-eight square and `NP<=2` both plus the Standard
Model. Read the note on `NP^2==2` under Known limits before treating the interference as the
whole 1/Lambda^4 prediction.

In the model's own card the scale is `Lam`, block `DIM8` entry 0, default 1000 GeV, but MadGraph
renames it `lam__2` on import, because it lowercases names and `lam` is already the Higgs
quartic, so both the `set` command and the card in the process directory want `lam__2`. A
`set Lam 1000` is accepted and silently does nothing.

`hel_recycling False` is needed because MadGraph 3.5's helicity recycler fails on these Lorentz
structures with "split amp are not supported for spin2 and 3/2". The default run card does not
carry the key, so it has to be appended, which `set` does.

Set the beam energies. MadGraph defaults to 6500 GeV a beam and every number quoted in this
repository is at 6800.

Every dimension-eight Wilson coefficient is an external parameter in block `DIM8`, zero by
default, named after its operator: `c8q2W2Dx1` is `Q_{q^2W^2D}^{(1)}`. The full list is
`examples/cards/coefficients.md`, and `models/dim8_is/param_card_template.dat` is a parameter
card with every coefficient annotated by operator and class.

To work with a subset of operators, use a restriction card. The shipped model has 27: one per
Murphy class, plus `bosonic`, `cpeven`, `all`, `ten`, `only_q2H4D` and `only_W2H2D2`:

    import model dim8_is-cls14

and `validate/make_restriction.py` writes any other selection from operator names, coefficient
names, block numbers or classes.

## Testing it

`validate/quicktest.sh /path/to/MG5_aMC` is a fifteen-minute acceptance test on one core: the
truncation of the input scheme, the derived Standard Model parameters, the Standard Model limit
against MadGraph's own `sm` model, the interference, its 1/Lambda^4 scaling and the square. Every
test prints the number it expects before it runs. `docs/HOW_TO_BREAK_IT.md` is the adversarial
companion: what is already checked and at what level, where the model is most likely to be wrong,
and the MadGraph traps that look like physics failures and are not.

## Worked examples

`examples/README.md` is the guide: thirteen scripts on two tracks (run a process "up to dimension
eight", or choose the operators), the Lambda power counting in MadGraph syntax, and what the
order counting can and cannot see. `examples/studies/` holds the studies of the paper (diboson, triboson,
Higgs-pair production in vector boson fusion, and a Drell-Yan one written to reach the
four-fermion classes and not yet run) with the driver, the table generator and the plotting
script that produce every number and figure in it.

## Two models

`dim8_is` is the model to use: the operators sit on the Standard Model in the {alpha, MZ, GF}
input scheme, corrected to 1/Lambda^4, with canonically normalised fields. `dim8_plain` puts the
same operators on the plain FeynRules Standard Model and is for cross-checks only: operators that
shift a gauge kinetic term break gauge invariance there once the UFO format drops the two-point
vertex, which `check lorentz` shows at the 1e-4 level. See `examples/16_plain_vs_input_scheme.md`.

## What is validated

Hermiticity of all 674 operators of the model, and of the nine baryon-number-violating blocks
that were built, by an exact three-stage test. The mass dimension of every vertex-coupling pair
carrying a single dimension-eight coefficient, 152956 of them across 48201 distinct couplings.
The gluon and photon Ward identities on 21 processes, better than 5e-14, with all 1030
coefficients switched on at 0.7, of which 893 are live. The Standard Model limit, which
reproduces MadGraph's own `sm` model on `p p > w+ w-` at 0.07 sigma. The truncation of the input
relations, every one of their 330 coefficient-dependent parameters exactly linear in the
coefficient. And at the level of cross sections, the class interferences of `p p > w+ w-` summing
to the all-on result at 0.7 sigma, on the 13 of 21 classes that have a diagram there, and its 86
single-operator interferences at 0.5 sigma.

`docs/HOW_TO_BREAK_IT.md` is the companion and should be read with this list, because it records
three defects that all of the above missed.

## Known limits

Flavour-universal coefficients, one per operator.

`NP^2==2` is not quite the 1/Lambda^4 interference. Fourteen couplings carry a coefficient with
no `NP` tag, and the shift of the W mass carries none and cannot, so part of the 1/Lambda^4
prediction sits in the `NP=0` bin. On `p p > w+ w-` it is +1.35 pb against an `NP^2==2` value of
-3.998. Read `docs/HOW_TO_BREAK_IT.md` before quoting an interference.

The 60 baryon-number-violating operators are in the catalogue but not in the model. Nine were
built as a sample and MadGraph's ALOHA refuses their fermion-flow-violating four-point vertices,
and the other 51 were not built.

Fifteen operators vanish identically for a universal coefficient, so 893 of the 1030 card entries
are live. The card marks nine of them and not yet the six `Q_{psi^4B}` duals.

Six operators of class 1 are exported with at most six gluons. `Q_{G^4}^{(2)}` has no seven- or
eight-gluon vertex at all, by the Jacobi identity, and `Q_{G^4}^{(5)}` has no eight-gluon one.
The seven- and eight-gluon vertices of `Q_{G^4}^{(4)}`, `^{(6)}`, `^{(8)}`, `^{(9)}` and the
seven-gluon vertex of `^{(5)}` are non-zero and are not in the model. No process below seven
external gluons can see any of them.

Nine Lorentz structures in the model are identically zero and fifty vertices carry them. Most are
harmless, one breaks the build. `validate/zero_vertex.py` lists them.

The dimension-six operator basis is not included, so take it from SMEFTsim and use the two models
together. Eight Warsaw coefficients and their own scale `Lam6` do appear in block `DIM6`, zero by
default, because the input scheme is built with them in SMEFTsim's conventions. They enter only as
shifts of Standard-Model couplings and masses, with no compensating vertices, so a non-zero one
gives a silently wrong and not gauge-invariant answer. Leave that block alone.
