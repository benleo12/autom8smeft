# Worked examples

Everything here runs with MadGraph5_aMC@NLO alone. No Mathematica, no FeynRules.

## The two models

| model directory | what it is | use it for |
|---|---|---|
| `dim8_is` | all 674 baryon-number-conserving dimension-eight operators of the Murphy basis on top of the Standard Model, in the {alpha, MZ, GF} input scheme with canonically normalised fields, truncated at 1/Lambda^4 in the input relations | **everything**: this is the model to download |
| `dim8_plain` | the same operators on the plain FeynRules Standard Model, no input-scheme corrections | cross-checks only. Operators that shift a kinetic term (for instance `Q_{G^2H^4}^{(1)}`) are not gauge-consistent here once the two-point vertex is dropped by the UFO format |

Install: copy or symlink the model directory into MadGraph's `models/` folder under the same
name, which is what the example scripts assume, or give `import model` an absolute path. The
import takes about 30 seconds and 1.1 GB of memory (MG5_aMC 3.5.3, Apple silicon), once per
session. Diagram generation is what the full basis costs: `p p > w+ w- NP<=2` is 9 subprocesses
and 458 diagrams in 25 seconds, `p p > w+ w- z NP<=2` is fine too, but `p p > h h j j QCD=0
NP<=2` on the unrestricted model is 166 subprocesses and 298888 diagrams in four and a half
minutes, followed by hours of code generation, because every four-fermion and psi^2 X H operator
adds contact terms. For 2 to 4 processes restrict first (`import model dim8_is-bosonic` for the
bosonic classes, or a class card), which is what the VBF di-Higgs study does. A
relative path is not one of the two: MadGraph resolves it against its own directory and stops
with "is not a valid pathname".

Every Wilson coefficient is an external parameter in block `DIM8` of the parameter card,
named after the operator (`c8G2H4x1` is `Q_{G^2H^4}^{(1)}`, complex ones come as `...Re` and
`...Im`), and every one of them is **zero by default**. The scale is `Lam` in GeV (default
1000). The full list with operator names is `cards/coefficients.md`: 734 operator blocks, which
come to 1030 card entries once the 296 complex ones are split into real and imaginary parts.

Of those 734 blocks, 674 conserve baryon number and 60 do not, and the shipped model contains the
674. The 120 card entries of the baryon-number-violating operators are still there, because the
parameter list is written from the whole basis, and setting one of them does nothing at all. The
parameter-card template marks every such line, and `make_restriction.py` says so if you select
them.

Nine more operators of the 674 have no vertices either, so 899 of the 1030 entries are live.
Seven vanish identically once the coefficient is flavour universal: `Q_{e^4B}`, `Q_{l^4B}^{(1)}`,
`Q_{u^4B}`, `Q_{d^4B}`, `Q_{q^4B}^{(1)}` and `Q_{q^4B}^{(3)}` contract two identical currents,
symmetric in their Lorentz indices, with the antisymmetric B field strength, and `Q_{q^4H^2}^{(5)}`
contracts two identical isotriplet currents with epsilon^{IJK}. With generation indices these
operators are not zero, which is why Murphy's basis lists them, but with one coefficient per
operator they are. The remaining two, `Q_{udWH^2}^{(1)}` and `Q_{udWH^2}^{(2)}`, vanish by their
SU(2) structure. Their card entries are marked like the baryon-number-violating ones.

## Lambda power counting in MadGraph

Every dimension-eight coupling carries the coupling order `NP = 2` (one power of `1/Lambda^2`
per unit of NP, so that a dimension-six model would sit at `NP = 1`). MadGraph's order syntax
then selects the terms of the expansion:

| what you want | order of |M|^2 | syntax |
|---|---|---|
| Standard Model only | Lambda^0 | `NP=0` |
| interference of one dimension-eight insertion with the SM | 1/Lambda^4 | `NP^2==2` |
| dimension-eight squared (one insertion in each amplitude) | 1/Lambda^8 | `NP<=2 NP^2==4` |
| SM + interference + squared, one insertion per amplitude | mixed | `NP<=2` (this is what "up to dimension eight" usually means in practice) |
| everything at 1/Lambda^8 from dimension eight alone, including two insertions in one amplitude interfering with the SM | up to 1/Lambda^8 | `NP<=4 NP^2<=4` (needs `expansion_order = 4` in `coupling_orders.py`, which the shipped `dim8_is` has) |

The consistent 1/Lambda^4 prediction is the interference term. The squared term and the double
insertions are formally of the same order as dimension-six-squared and dimension-eight
interference from a dimension-six model, which this model does not contain; quote them as an
estimate of the truncation uncertainty, not as the 1/Lambda^8 prediction. Because everything is
linear in the coefficients at 1/Lambda^4, the interference cross section for any coefficient
value follows from one run per operator by scaling; reweighting (example 08) does this for you.

### What the order counting cannot see

MadGraph counts orders on couplings. Operators that enter the input relations (the X^2 H^4
kinetic terms, H^6, the l^2 H^4 D operators behind G_F, ...) act partly through *parameters*, and
the two kinds of parameter behave differently. A shifted **coupling** is order-tagged and does
enter the interference: `gw2`, the O(1/Lambda^4) shift of the weak coupling, appears in 201
couplings of the shipped model, 29 of them at `NP:2`, so an operator that shifts it contributes
at `NP^2==2` even in a process where it has no vertex of its own. A shifted **mass** is not:
`MW22` and `vev2` reach the amplitude through the mass spectrum, so they are present in every
run, `NP=0` included, and invisible to the order counting.

Two consequences. The pure Standard Model is the model with every coefficient at zero (example
02), not `NP=0` with coefficients on. And the operators that can affect a process are not only
those with a vertex in it: in `p p > w+ w-` the two operators `Q_{l^2H^4D}^{(2)}` and
`Q_{l^2H^4D}^{(4)}`, which contain no quarks at all and enter only through muon decay and hence
G_F, carry about a third of the whole dimension-eight interference. `./dim8 select` is a
tree-reachability test over the model's vertices and will not list them; add the input-relation
operators to whatever it returns. This treatment of an input scheme is inherited from SMEFTsim. For
operators with genuine new vertices (X^2 H^2 D^2, X^3 H^2, psi^2 X^2 D, the four-fermion and
X^4 classes) the counting is exact. Which classes can enter a given process at all is a
separate question, answered by `./dim8 select` (example 14) or by trying: the bosonic
X^2 H^2 D^2 operators have no three-point vertex (their lowest are W W W W, W W H H, a W W Z), so
they give no diagram in 2 to 2 diboson or `z h` production and first appear in triboson
production and vector-boson scattering, while 2 to 2 diboson gets its dimension-eight
interference from the two-fermion classes psi^2 H^2 D^3, psi^2 H^4 D, psi^2 X^2 D and
psi^2 X H^2 D. A check worth knowing: in the {alpha, MZ, GF} scheme
`Q_{W^2H^4}^{(1)}` and `Q_{H^6}^{(1)}` have no O(1/Lambda^4) effect on p p > w+ w- at all,
because the W field rescaling is absorbed by the inputs (the coupling shifts gw2 and rW2 cancel
exactly and MW is unshifted); `validate/eval_ufo_params.py` prints these shifts for any
coefficient values.

## Index

Experimentalist track (run a process "up to dimension eight"):

| # | script | shows |
|---|---|---|
| 01 | `mg5/01_import_and_inspect.mg5` | importing the model, what it contains, the NP order |
| 02 | `mg5/02_sm_reference.mg5` | `p p > w+ w-` with `NP=0`, the Standard Model baseline |
| 03 | `mg5/03_interference.mg5` | the same process at `NP^2==2` with `Q_{q^2W^2D}^{(1)}` and `Q_{q^2WH^2D}^{(1)}` switched on: the 1/Lambda^4 term, which can be negative |
| 04 | `mg5/04_dim8_squared.mg5` | `NP<=2 NP^2==4`: the 1/Lambda^8 squared term |
| 05 | `mg5/05_up_to_dim8.mg5` | `NP<=2`: SM plus interference plus squared in one run |
| 06 | `mg5/06_two_insertions.mg5` | `NP<=4 NP^2<=4`: double insertions |
| 07 | `mg5/07_coefficient_scan.mg5` | MadGraph's `scan:` syntax over a coefficient |
| 08 | `mg5/08_reweighting.mg5` + `cards/reweight_card.dat` | one sample, many coefficient points |
| 09 | `mg5/09_lambda_dependence.mg5` | scanning `Lam` to see the 1/Lambda^4 and 1/Lambda^8 scaling directly |
| 10 | `cards/param_card_template.dat` | the parameter card with every coefficient grouped and labelled, a copy of the one in `models/dim8_is/` refreshed at release. The restriction cards live in the model directory and nowhere else, so that they cannot drift from it |

Theorist track (choose operators):

| # | script | shows |
|---|---|---|
| 11 | `mg5/11_single_operator.mg5` | a restriction card keeping one operator (`Q_{q^2H^4D}^{(1)}`), its interference in `p p > z h` |
| 12 | `mg5/12_operator_class.mg5` | one whole class (`cls:14`, the psi^2 X^2 D contact terms) in `p p > w+ w-` |
| 13 | `mg5/13_my_ten_operators.mg5` | a hand-picked list of ten operators |
| 14 | `14_which_operators.md` | how to find which operators can enter a process at all (`./dim8 select`, Python only) |
| 15 | `mg5/15_validation_checks.mg5` | the gauge and Lorentz checks MadGraph can run on the model |
| 16 | `16_plain_vs_input_scheme.md` | when the two models differ and why the input-scheme one is the default |

Studies for the paper (full runs, cross-section tables and distributions, see each folder's README):

| folder | process |
|---|---|
| `studies/diboson/` | `p p > w+ w-`, `p p > w z`, `p p > z z` |
| `studies/triboson/` | `p p > w+ w- z`, `p p > w+ w- w-`, `p p > z z z` |
| `studies/vbf_dihiggs/` | `p p > h h j j` with VBF cuts |

Restriction cards are written with

    python3 validate/make_restriction.py <model dir> <card name> <operator | coefficient | block | cls:N> ...

and used with `import model <model dir>-<card name>`. Kept coefficients get distinct placeholder
values in the card, since MadGraph removes zeros, freezes ones and merges equal values, and the
physical values are set in the run's parameter card as usual. The shipped model carries all 674
operators, so any selection has vertices behind it; on a partial UFO built for one sector the
writer warns when the operators you kept have none, because the restricted model then has no NP
coupling order at all and MadGraph answers a request for `NP^2==2` with "model order NP^2 not
valid for this model".

Running a script: `./bin/mg5_aMC path/to/script.mg5`. Each script writes its process directory
next to itself under `runs/`; delete those freely.

Three things you will see in the logs. A `NameError: name 'MW21' is not defined` from
`write_param_card.py` comes from MadGraph writing the optional dependent-parameter block of
the card in the process directory in its own file order, after it has already evaluated the
model correctly; the run is unaffected (the model's own `write_param_card.py` runs clean). The
scripts set `hel_recycling False` because MadGraph 3.5's helicity recycler fails on the
dimension-eight Lorentz structures at event generation ("split amp are not supported for spin2
and 3/2"). And "For consistency, the mass of particle 24 (w+) is changed to ..." is the input
scheme at work: M_W is derived from alpha, M_Z and G_F, 79.82 GeV at tree level, and moves when
coefficients that enter the input relations are switched on.

What the examples gave on this machine (13.6 TeV, Lam 1 TeV, coefficients at 1): `p p > w+ w-`
68.07 pb in the SM (02), -1.163 pb of interference from `Q_{q^2W^2D}^{(1)}` and
`Q_{q^2WH^2D}^{(1)}` (03), -2.358 pb from the whole psi^2 X^2 D class (12), -1.31 pb from the ten
operators of example 13; `p p > z h` -0.0051 pb from `Q_{q^2H^4D}^{(1)}` alone (11); and the five
Ward checks of example 15 pass at 1e-14 with every coefficient at 0.7.
