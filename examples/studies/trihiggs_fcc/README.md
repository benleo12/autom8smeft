# Tri-Higgs production at FCC-hh, up to dimension eight

A complete study in three text files and one command: `p p > h h h` at 100 TeV with two cuts,
cross sections at each order in `1/Lambda`, and two distributions. On two cores it takes about two
hours, most of it MadGraph reading the model once for each of the eight cross sections. Copy the
directory and change the process, the cuts or the operator classes to make your own.

## 0. Once

    ln -s /path/to/autom8smeft/models/dim8_is /path/to/MG5_aMC/models/dim8_is
    export MG5_DIR=/path/to/MG5_aMC

## 1. Which operators can contribute, and how fast do they grow?

No event generator is needed for this step.

    $ ./dim8 select "p p > h h h" --model models/dim8_is
    selected: 23 of the 674 dimension-eight operators through a vertex of the process, plus 9 that enter through the {alpha, MZ, GF} input relations
    class 2: ...  class 3: ...  class 4: ...  class 6: ...  class 7: ...  class 11: ...
    class 12: ...  class 17: ...

    $ ./dim8 count "X^2H^2D^2"
    X^2H^2D^2    leading power of the class's vertex, by its number of legs: lambda^4 at four legs, lambda^6 at five legs, lambda^8 at six legs
    ...
    $ ./dim8 count "X^2H^4"
    X^2H^4       leading power of the class's vertex, by its number of legs: lambda^6 at four legs, lambda^7 at five legs, lambda^8 at six legs
    ...

The summary line of `select` also counts the nine operators that enter through the input
relations with no vertex in this process, two of them only with the electron and muon Yukawas on.
The full output of `select`, shortened above, lists them under their own heading, and prints
beside every operator of the first group the vertex of its leading tree. It gives that tree's
power of lambda for the operators of classes 6, 7 and 11, and says of the others that they enter
only through the Yukawa coupling or the mass of a light quark or a lepton.

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

`results.tsv`, one line per cross section, in pb. The run that made this directory is at 100 TeV
with the cuts of `processes.txt`, at `Lam` = 10 TeV and with every dimension-eight coefficient at
one, or at zero in the `NP=0` row:

| model | order | what it is | cross section |
|---|---|---|---|
| all operators | `NP=0` | SM at tree level | zero |
| all operators | `NP=0 on` | the same with the coefficients on | zero |
| all operators | `NP^2==2` | interference, 1/Lambda^4 | zero |
| all operators | `NP<=2 NP^2==4` | squared term, 1/Lambda^8 | 8.23e-05 |
| class 6 | `NP^2==2` | interference | no diagram |
| class 6 | `NP<=2 NP^2==4` | squared term | 1.15e-06 |
| class 12 | `NP^2==2` | interference | no diagram |
| class 12 | `NP<=2 NP^2==4` | squared term | no diagram |

A run keeps the event file of every nonzero cross section in `lhe/`, and the record of each cross
section in `records.tsv` with a copy of its cards in `cards/`, which
`examples/studies/provenance.py check` compares with `results.tsv` (see `../diboson/README.md`).

## 5. Two observables

    examples/studies/plot_study.py hhh \
        "all operators squared=examples/studies/trihiggs_fcc/lhe/p_p___h_h_h__dim8_is_NP__2_NP_2__4.lhe.gz" \
        "class 6 squared=examples/studies/trihiggs_fcc/lhe/p_p___h_h_h__dim8_ismcls6_NP__2_NP_2__4.lhe.gz"

writes `hhh_mVV.tsv` and `hhh_pT.tsv`, the invariant mass of the three Higgs bosons and the
leading transverse momentum, normalised to the cross sections above, and the two plots as PNG.
For any other observable, read the LHE files with your own analysis code.

## What to know before using these numbers

**The model is a tree-level model.** In the SM, `p p > h h h` proceeds through gluon fusion and a
top loop, which is not in it. With the Yukawa couplings of the light quarks at zero, as on the
release cards, the process has no SM amplitude at tree level, so the `NP=0` and `NP^2==2` rows are
zero and the dimension-eight contribution enters only through its square. Class 6 couples the two
gluons to the Higgs bosons directly. Class 12 acts on the quarks of the proton only through their
Yukawa couplings, so it has no diagram here.

**For an interference with a tree-level SM amplitude, use vector-boson fusion,**
`p p > h h h j j QCD=0`. On `dim8_is` its SM amplitude alone has 85,416 diagrams in 120 subprocesses,
which take 68 core-minutes to generate. Give the full-model rows a card (`| bosonic` after the cuts
in `processes.txt`). The di-Higgs process
`p p > h h j j QCD=0 NP^2==2` already has 525,156 diagrams on the unrestricted `dim8_mw`, which take
3539 core-minutes to generate, and 9,540 with the card `./dim8 select` writes for it.

**The scale.** With nothing to interfere with, the nonzero cross sections above are of order
`1/Lambda^8` and scale as `(10 TeV/Lambda)^8` with `Lam`. Before using them, compare the tri-Higgs
masses the events reach (`hhh_mVV.tsv`) with Lambda.
