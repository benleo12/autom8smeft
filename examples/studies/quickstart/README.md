# quickstart

    export MG5_DIR=/path/to/MG5_aMC
    examples/studies/run_study.sh examples/studies/quickstart models/dim8_is 2000

About half an hour on two cores. Writes `results.tsv` here. Expected, all 1030 coefficients at 1
and Lambda at 1 TeV, 13.6 TeV:

    dim8_is        NP=0             68.2  pb     Standard Model
    dim8_is        NP=0 on          69.5  pb     the same, operators on
    dim8_is        NP^2==2          -4.0  pb     dimension-eight interference
    dim8_is        NP<=2 NP^2==4  4000    pb     dimension-eight squared
    dim8_is-cls14  NP^2==2          -2.38 pb     class 14 alone
    dim8_is-cls14  NP<=2 NP^2==4   142   pb
    dim8_is-cls15  NP^2==2           0.061 pb    class 15 alone
    dim8_is-cls15  NP<=2 NP^2==4     2.1  pb

Statistics at 2000 events is a few percent, so agreement to two digits is fine.

The square is 59 times the Standard Model. That is the expansion failing at c = 1 and
Lambda = 1 TeV, not the model misbehaving. Raise Lambda or cut the tail.

`NP=0 on` minus `NP=0` is +1.4 pb. That is a 1/Lambda^4 contribution the interference row does
not contain, because MadGraph tags couplings and the W mass is not a coupling. Add it.

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
    Lam=3000
