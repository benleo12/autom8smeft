# quickstart

    export MG5_DIR=/path/to/MG5_aMC
    examples/studies/run_study.sh examples/studies/quickstart models/dim8_is 2000

About three hours on two cores of a cluster node. Writes `results.tsv` here, with the record of
each cross section in `records.tsv` and a copy of its cards in `cards/`, which
`examples/studies/provenance.py check examples/studies/quickstart/results.tsv` checks. Expected, every
entry of DIM8 and DIM8F at 1 and Lambda at 3 TeV, 13.6 TeV:

    dim8_is        NP=0             68.2     pb     Standard Model
    dim8_is        NP=0 on          68.2     pb     the same, operators on
    dim8_is        NP^2==2          -0.044   pb     dimension-eight interference
    dim8_is        NP<=2 NP^2==4     0.59    pb     dimension-eight squared
    dim8_is-cls14  NP^2==2          -0.029   pb     class 14 alone
    dim8_is-cls14  NP<=2 NP^2==4     0.021   pb
    dim8_is-cls15  NP^2==2           0.00077 pb     class 15 alone
    dim8_is-cls15  NP<=2 NP^2==4     0.00032 pb

Statistics at 2000 events is a few percent, so agreement to two digits is fine.

The square is thirteen times the size of the interference. In this total rate, with every
coefficient at 1, the 1/Lambda^8 term is the larger one even at Lambda = 3 TeV. That is the
expansion, not the model misbehaving. Raise Lambda or cut the tail.

`NP=0 on` and `NP=0` agree here. The W mass moves from 79.824 to 79.819 GeV, and the shift of the
Standard-Model bin is below the Monte Carlo error. It is a 1/Lambda^4 contribution the interference
row does not contain, because MadGraph tags couplings and the W mass is not a coupling. At
this setting it is +0.014 +- 0.002 pb against the interference of -0.044 pb
(`validate/np0_shift.py examples/studies/diboson --report`, from the pair of runs at Lambda = 1 TeV
in `../diboson/np0_shift.tsv`, where it is +1.11 +- 0.19 pb). Add it.

## Things to try next

Which operators can reach a process, before spending any CPU:

    ./dim8 select "p p > z h"
    ./dim8 select "u u~ > h d d~"

A different process, with cuts. Edit `processes.txt`:

    p p > z h
    p p > e+ e- | mmll=200
    p p > w+ w- | ptl=30 mmll=200

Every class instead of two. Edit `classes.txt` to `cls1` through `cls21`, or drop the file to run
the full model only.

One operator at a time:

    validate/make_restriction.py models/dim8_is myop c8q2W2Dx1
    echo myop > examples/studies/quickstart/classes.txt

A different scale or coefficient. Make `coefficients.txt`:

    dim8_all=1
    Lam=2000
