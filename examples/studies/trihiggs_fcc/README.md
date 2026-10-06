# Tri-Higgs production at FCC-hh, up to dimension eight

A complete study in three text files and one command: `p p > h h h` at 100 TeV with two cuts,
cross sections at each order in `1/Lambda`, and two distributions. It takes about a quarter of an
hour on two cores. Copy the directory and change the process, the cuts or the operator classes to
make your own.

## 0. Once

    ln -s /path/to/autom8smeft/models/dim8_is /path/to/MG5_aMC/models/dim8_is
    export MG5_DIR=/path/to/MG5_aMC

## 1. Which operators can contribute, and how fast do they grow?

No event generator is needed for this step.

    $ ./dim8 select "p p > h h h"
    selected: 28 of the 674 dimension-eight operators, and 4 of the dimension-six classes
    class 2: ...  class 3: ...  class 4: ...  class 6: ...  class 7: ...  class 8: ...
    class 11: ...  class 12: ...  class 17: ...

    $ ./dim8 count "X^2H^2D^2"
    X^2H^2D^2    lambda^4 at four legs, lambda^6 at five legs, lambda^8 at six legs
    $ ./dim8 count "X^2H^4"
    X^2H^4       lambda^6 at four legs, lambda^7 at five legs, lambda^8 at six legs

A smaller power of lambda is a larger contribution, so the classes with derivatives are the ones
that grow fastest with energy.

## 2. The three text files

`processes.txt`, the process and the cuts, in MadGraph's own run-card names:

    p p > h h h | ebeam1=50000 ebeam2=50000 pt_min_pdg={25:100} eta_max_pdg={25:4}

`classes.txt`, the operator classes to run one at a time, one restriction card per line:

    cls6
    cls12

`coefficients.txt`, the coefficient values and the scale:

    dim8_all=1
    Lam=10000

Any coefficient can be set by name instead (`c8G2H4x1=0.5`), and any subset of operators gets its
own card with `validate/make_restriction.py models/dim8_is NAME c8G2H4x1 cls:12`.

## 3. Run

    examples/studies/run_study.sh examples/studies/trihiggs_fcc models/dim8_is 5000

## 4. What comes back

`results.tsv`, one line per cross section, in pb. From the run that made this directory:

| model | order | what it is | cross section |
|---|---|---|---|
| all operators | `NP=0` | SM at tree level | 2.82e-08 |
| all operators | `NP=0 on` | the same with the coefficients on | 2.82e-08 |
| all operators | `NP^2==2` | interference, 1/Lambda^4 | 9.9e-10 |
| all operators | `NP<=2 NP^2==4` | squared term, 1/Lambda^8 | 1.11e-04 |
| class 6 | `NP^2==2` | interference | no diagram |
| class 6 | `NP<=2 NP^2==4` | squared term | 1.15e-06 |
| class 12 | `NP^2==2` | interference | -7.5e-10 |
| class 12 | `NP<=2 NP^2==4` | squared term | 9.7e-10 |

The event file of every row is in `lhe/`.

## 5. Two observables

    examples/studies/plot_study.py hhh \
        "SM=examples/studies/trihiggs_fcc/lhe/p_p___h_h_h__dim8_is_NP_0.lhe.gz" \
        "all operators squared=examples/studies/trihiggs_fcc/lhe/p_p___h_h_h__dim8_is_NP__2_NP_2__4.lhe.gz"

writes `hhh_mVV.tsv` and `hhh_pT.tsv`, the invariant mass of the three Higgs bosons and the
leading transverse momentum, normalised to the cross sections above, and the two plots as PNG.
For any other observable, read the LHE files with your own analysis code.

## What to know before using these numbers

**The model is a tree-level model.** In the SM, `p p > h h h` proceeds through gluon fusion and a
top loop, which is not in it. The `NP=0` row is therefore only the quark-initiated tree-level
rate, which is tiny, and it is not the SM tri-Higgs cross section. What the model does give
correctly is the dimension-eight contact contribution, and for the gluon-initiated classes that
contribution has no tree-level SM amplitude to interfere with, which is why class 6 has a squared
term and no interference.

**For an interference with a tree-level SM amplitude, use vector-boson fusion,**
`p p > h h h j j QCD=0`. It is 96,636 SM diagrams in 120 subprocesses, so expect hours rather than
minutes, and give the full-model rows a card (`| bosonic` after the cuts in `processes.txt`).

**Check the scale.** The squared term above is five orders of magnitude larger than the
interference, so at these coefficients and this Lambda the expansion in `E/Lambda` is not under
control over the whole sample at 100 TeV. Raise `Lam`, lower the coefficients, or cut on the
tri-Higgs mass (`mxx_min_pdg`, or a cut in your analysis) below Lambda.
