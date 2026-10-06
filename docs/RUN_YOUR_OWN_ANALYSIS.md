# Running an analysis

From a process to cross sections. Needs MadGraph5_aMC@NLO 3.5 and Python 3.11.

## 1. Install

    ln -s /path/to/autom8smeft/models/dim68_is  /path/to/MG5_aMC/models/dim68_is
    ln -s /path/to/autom8smeft/models/dim8_is   /path/to/MG5_aMC/models/dim8_is

`dim68_is` carries both sectors, `dim8_is` the dimension-eight one alone and so generates far
fewer diagrams. Everything below works with either; the examples name `dim8_is` because its
numbers are the checked ones.
    export MG5_DIR=/path/to/MG5_aMC

## 2. Which operators enter

    ./dim8 select "u c > u c h"

prints the classes and operators with a tree-level vertex in that process, and the diagram
counts. It is a LOWER BOUND. Eight dimension-eight coefficients enter the {alpha, MZ, GF}
relations (c8B2H4x1, c8H6x1, c8H6x2, c8W2H4x1, c8W2H4x3, c8WBH4x1, c8l2H4Dx2, c8l2H4Dx4) and
so move every amplitude whether or not they have a vertex in the process you asked about. On
p p > w+ w- the last two have no vertex in any diagram and carry a third of the effect.

## 3. Set up a study

A directory with two or three text files.

`processes.txt`, one MadGraph process per line. Run-card settings after a `|`, and after a second
`|` an optional restriction card for that process's full-model rows:

    p p > w+ w-
    p p > e+ e- | mmll=200
    p p > h h j j QCD=0 | ptj=20 mmjj=500 | bosonic

Restrict heavy processes. `p p > h h j j QCD=0 NP<=2` unrestricted is 166 subprocesses and 298888
diagrams, hours of code generation.

`classes.txt`, one restriction card per line:

    cls14
    cls15
    cls18

29 cards ship, one per class plus `bosonic`, `cpeven`, `cpodd`, `all`, `ten`, `only_q2H4D`,
`only_W2H2D2`, `l2H4D24`. `cpeven` and `cpodd` use the derived C x P parity of `gen/cp_parity.py`, which is
not the same as counting dual field strengths: see the README. Any other selection, by operator name, coefficient, block number or class:

    validate/make_restriction.py models/dim8_is mine Q_{q^2W^2D}^{(1)} c8q2WH2Dx1 cls:18

`coefficients.txt`, optional, `NAME=VALUE` per line. Default is every dimension-eight coefficient
at 1 with `Lam` at 1000 GeV.

## 4. Run

    MG5_DIR=/path/to/MG5_aMC DIM8_CORES=2 \
        examples/studies/run_study.sh mystudy models/dim8_is 5000

Cross sections append to `mystudy/results.tsv`, event files to `mystudy/lhe/`. `DIM8_RUNS` sets
where process directories go, `DIM8_CORES` caps cores, `DIM8_NEV_SQ` caps events for the squared
rows.

Rows per process:

| row | order |
|---|---|
| `NP=0` | Standard Model, coefficients off |
| `NP=0 on` | same amplitude, coefficients on |
| `NP^2==2` | interference, 1/Lambda^4 |
| `NP<=2 NP^2==4` | square, 1/Lambda^8 |

`NP=0 on` is not a duplicate. MadGraph tags couplings, not masses, and the W mass shifts with the
coefficients, so part of the 1/Lambda^4 term sits in the `NP=0` bin:

    sigma(1/Lambda^4) = sigma(NP^2==2) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]

On `p p > w+ w-` with all coefficients at 1 and Lambda at 1 TeV that bracket is +1.40 pb against
an interference of -3.998. It vanishes for every process in which no W is produced or exchanged.
It does not vanish in vector-boson fusion, where the W sits in the t-channel propagators: 6.8 per
cent of the cross section in `p p > h h j j QCD=0`.

## 5. Output

`mystudy/results.tsv`, one row per process, model and order: cross section, error, event count,
the W mass at that row's coefficients, the settings used, and the path to the event file. Event
files land in `mystudy/lhe/` as gzipped LHE.

An interference sample has negative weights and reproduces its cross section only statistically,
so its effective statistics is the excess of positive over negative events.

## 6. One operator at a time

    for c in $(grep -o 'c8[A-Za-z0-9]*' models/dim8_is/param_card_template.dat | sort -u); do
        validate/make_restriction.py models/dim8_is op_$c $c
    done

then put those card names in `classes.txt`.

## 7. MadGraph practicalities

`set Lam 1000` at the launch prompt is accepted and does nothing. The card calls the scale
`lam__2`, because MadGraph lowercases names and `lam` is already the Higgs quartic.

`hel_recycling` defaults to on in 3.5 and fails on these Lorentz structures. Set it False. The
default run card lacks the key, so it has to be appended.

Set the beam energies. MadGraph defaults to 6500 GeV per beam.

`import model` takes an installed name or an absolute path. A relative path fails.

A restriction keeping only operators with no vertex removes the `NP` coupling order, and MadGraph
then rejects `NP^2==2` without explaining why.

Class 7 has no three-point vertex, so "No amplitudes generated" in a two-to-two diboson process is
physics, not an error.

`event_norm` defaults to `average`: every event of an unweighted sample carries the full cross
section as its weight and the cross section is the mean, not the sum. Normalise to the banner's
integrated weight.

Python 3.12 disables reweighting, 3.13 breaks `model_reader`. Use 3.11.
