# Running your own dimension-eight analysis

This walks from "I want to know what dimension eight does to process X" to the tables and figures
you would put in a paper, for any process MadGraph can generate. It is the same path the studies
in `examples/studies/` take, and those are worked examples you can copy rather than read.

Nothing here needs Mathematica or FeynRules. You need MadGraph5_aMC@NLO 3.5 and Python 3.11.

## 1. Install

    ln -s /path/to/autom8smeft/models/dim8_is  /path/to/MG5_aMC/models/dim8_is
    export MG5_DIR=/path/to/MG5_aMC

Then confirm the model is sound on your machine before you trust a number out of it:

    validate/quicktest.sh $MG5_DIR

Six checks, about fifteen minutes on one core, each printing the number it expects before it
runs. The first two need no MadGraph and take five seconds.

## 2. Find out which operators can enter

    ./dim8 select "u c > u c h"

prints the Murphy classes and operators with a tree-level vertex in that process, and the
diagram counts. Use it to decide what is worth running, because the full basis is 674 operators
and almost none of them touch any given process.

Two warnings about that output, both of which matter for a paper.

It is a **lower bound**. Operators that act only through the {alpha, MZ, GF} input relations have
no vertex anywhere and still contribute. In `p p > w+ w-` the two muon-decay operators
`Q_{l^2H^4D}^{(2)}` and `^{(4)}` carry a third of the whole dimension-eight interference with no
vertex in any diagram, by shifting the W mass and the weak coupling. Thirteen coefficients act
this way. `docs/HOW_TO_BREAK_IT.md` lists them.

It says nothing about **size**. A class with a hundred diagrams can give less than one with two.
The energy-enhancement argument is what tells you which operators grow with the hard scale, and
that is a property of the operator's derivative and field content, not of its diagram count. The
selector tells you what is possible, the run tells you what is large.

## 3. Set up a study

A study is a directory with two or three text files.

`processes.txt`, one MadGraph process per line. Run-card settings go after a `|`, and after a
second `|` an optional restriction card for that process's full-model rows:

    p p > w+ w-
    p p > e+ e- | mmll=200
    p p > h h j j QCD=0 | ptj=20 mmjj=500 | bosonic

The third line says something worth knowing. `p p > h h j j QCD=0 NP<=2` on the unrestricted
model is 166 subprocesses and 298888 diagrams, four and a half minutes to generate and hours to
compile, because every four-fermion and psi^2XH operator adds a contact term. Restrict first.

`classes.txt`, one restriction card per line. The 27 shipped cards are one per Murphy class plus
`bosonic`, `cpeven`, `all`, `ten`, `only_q2H4D` and `only_W2H2D2`:

    cls14
    cls15
    cls18

Any other selection is one command, by operator name, coefficient name, block number or class:

    validate/make_restriction.py models/dim8_is mine Q_{q^2W^2D}^{(1)} c8q2WH2Dx1 cls:18

`coefficients.txt`, optional, `NAME=VALUE` per line. The default is every dimension-eight
coefficient at 1 with `Lam` at 1000 GeV, which is what the studies mean by "switched on".

## 4. Run it

    MG5_DIR=/path/to/MG5_aMC DIM8_CORES=2 \
        examples/studies/run_study.sh mystudy models/dim8_is 5000

Each process is run at every order of the expansion, for the full model and then one class at a
time, and the cross sections append to `mystudy/results.tsv`. Event files land in `mystudy/lhe/`.
`DIM8_RUNS` chooses where the MadGraph process directories go, `DIM8_CORES` caps the cores, and
`DIM8_NEV_SQ` caps the event count for the squared rows, which are there for the cross section
and not for distributions.

The orders it runs, and what they mean:

| row | what it is | order |
|---|---|---|
| `NP=0` | the Standard Model, coefficients off | Lambda^0 |
| `NP=0 on` | the same amplitude with the coefficients on | see below |
| `NP^2==2` | one dimension-eight insertion interfering with the SM | 1/Lambda^4 |
| `NP<=2 NP^2==4` | the dimension-eight square | 1/Lambda^8 |

**The `NP=0 on` row is not a duplicate and you cannot drop it.** MadGraph counts coupling orders
on couplings, and a mass is not a coupling, so the shift of the W mass carries no order tag at
all. Fourteen couplings of the model are untagged for a related reason. The consequence is
measurable: on `p p > w+ w-` with every coefficient at 1 and Lambda at 1 TeV the `NP=0` cross
section moves from 68.03 +- 0.077 pb to 69.38 +- 0.085, and that +1.35 pb is a genuine
1/Lambda^4 term that `NP^2==2` does not contain. The complete prediction is

    sigma(1/Lambda^4)  =  sigma(NP^2==2)  +  [ sigma(NP=0, c) - sigma(NP=0, 0) ]

If you quote `NP^2==2` alone as "the interference", you are wrong by 34 percent on that process.
This is a property of doing an input scheme inside MadGraph and not a defect you can configure
away. `docs/HOW_TO_BREAK_IT.md` has the measurement and the mechanism.

## 5. Tables

    examples/studies/table_study.py mystudy models/dim8_is

writes `mystudy/table.md` and `mystudy/table.tex`: per process, the Standard Model row, the
full-model interference and square, then one line per operator class with its interference and
squared cross sections and the ratio to the SM, with classes that give no diagram marked as such.
It also writes a ranked one-operator-at-a-time table when the study has single-operator rows, and
a line checking that the class interferences sum to the all-on one, which is the sharpest cheap
test that nothing is being double counted or dropped.

The W mass of every row is recomputed from the model at that row's coefficients, so a row whose
vacuum differs from the Standard Model's is visible rather than hidden.

## 6. Distributions

    examples/studies/plot_study.py mystudy/fig \
        SM=mystudy/lhe/<sm>.lhe.gz  int=mystudy/lhe/<interference>.lhe.gz

gives the invariant mass of the final-state bosons and the leading transverse momentum, each
histogram normalised to its sample's cross section, negative weights kept, with a ratio panel.

Read the normalisation from the banner and do not assume it. MadGraph's `event_norm` defaults to
`average`, which means every event of an unweighted sample carries the **full** cross section as
its weight and the cross section is the mean rather than the sum. Assuming sigma/N scales every
distribution by the number of events. `plot_study.py` reads the banner.

An interference sample has negative weights, so it reproduces its cross section only
statistically and its effective statistics is the excess of positive over negative events. Do not
read a two-sigma wiggle in the tail as a shape.

## 7. Single operators

For a ranked table, one operator at a time, write one card per coefficient and put them in
`classes.txt`:

    for c in $(grep -o 'c8[A-Za-z0-9]*' models/dim8_is/param_card_template.dat | sort -u); do
        validate/make_restriction.py models/dim8_is op_$c $c
    done

That is how the diboson study got its 86 single-operator interferences, whose sum agrees with the
all-on number at 0.5 sigma. It is also the honest way to present a dimension-eight result, since
a single all-on number hides cancellations between operators of opposite sign.

## 8. Things that will cost you a day if nobody says them

`set Lam 1000` at MadGraph's launch prompt is accepted and does nothing. The card calls the scale
`lam__2`, because MadGraph lowercases names and `lam` is already the Higgs quartic.

`hel_recycling` is on by default in MadGraph 3.5 and dies on these Lorentz structures with "split
amp are not supported for spin2 and 3/2". Set it False.

Set the beam energies. MadGraph defaults to 6500 GeV a beam.

Every coefficient is zero by default, so `check lorentz` on the model as shipped tests only the
Standard Model part, and MadGraph ignores a param card passed to `check`. Use
`validate/ufo_on.py models/dim8_is 0.7` to get a copy whose defaults are on.

`import model` takes an installed name or an absolute path. A relative path fails.

A restriction keeping only operators with no vertex removes the `NP` coupling order, and MadGraph
then answers `NP^2==2` with "model order NP^2 not valid for this model" without saying why.

"No amplitudes generated" for the `X^2H^2D^2` operators of class 7 in a two-to-two diboson process
is physics. Their lowest vertex is four-point, so one insertion cannot enter.

Use Python 3.11. Python 3.12 generates events but disables reweighting, and 3.13 breaks
`model_reader`.

The full list, with the failures behind each, is in `docs/HOW_TO_BREAK_IT.md`, which also records
what has been validated and to what level, and where the model is most likely still wrong.

## 9. What a paper needs that this does not give you

The energy-scaling argument, which operator structures grow with the hard scale and why, is
physics you do for your process. The tools give you the cross sections and the shapes.

Dimension six. This model has none. A consistent 1/Lambda^4 result is dimension-six squared plus
dimension-eight interference, and the dimension-six half has to come from SMEFTsim, run
separately and added. Leave the `DIM6` block of this model at zero: those parameters shift
couplings and masses with no compensating vertices.

Flavour. One coefficient per operator, flavour universal.
