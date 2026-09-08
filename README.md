# autom8smeft

A SMEFT model for MadGraph5_aMC@NLO implementing the dimension-eight operator basis, with the
dimension-six coefficients entering the {alpha, MZ, GF} input relations, so cross sections can be
computed to order 1/Lambda^4 for any process MadGraph can generate. All 674
baryon-number-conserving dimension-eight operators are included.

Operator tabulation: arXiv:2005.00059, whose naming and class numbering this model follows.

## Install

    ln -s /path/to/autom8smeft/models/dim8_is  /path/to/MG5_aMC/models/dim8_is

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

-1.189 +- 0.003 pb, the dimension-eight interference of `Q_{q^2W^2D}^{(1)}` at 13.6 TeV with
Lambda = 1 TeV.

`NP` counts powers of 1/Lambda^2: `NP^2==2` is the interference, `NP<=2 NP^2==4` the square,
`NP<=2` both plus the Standard Model. The scale is `lam__2` in the param card, not `Lam`.
`hel_recycling False` is required. Set the beam energies, MadGraph defaults to 6500.

Every Wilson coefficient is an external parameter in block `DIM8`, zero by default, named after
its operator: `c8q2W2Dx1` is `Q_{q^2W^2D}^{(1)}`. `models/dim8_is/param_card_template.dat` lists
them all with operator and class. 27 restriction cards ship, one per class plus `bosonic`,
`cpeven`, `all`:

    import model dim8_is-cls14

`validate/make_restriction.py` writes any other selection. `./dim8 select "p p > w+ w-"` lists
which operators can enter a process.

## Analysis

[docs/RUN_YOUR_OWN_ANALYSIS.md](docs/RUN_YOUR_OWN_ANALYSIS.md): from a process to cross sections,
using `examples/studies/run_study.sh`.

## Limits

`NP^2==2` is not the complete 1/Lambda^4 interference. MadGraph tags couplings, not masses, and
the W mass shifts with the coefficients. Add the shift of the `NP=0` bin:

    sigma(1/Lambda^4) = sigma(NP^2==2) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]

`NP<=2` is unaffected. The study driver runs the extra row automatically.

Flavour universal, one coefficient per operator. 15 operators vanish identically under that
assumption, so 893 of the 1030 card entries are live.

Dimension-six operators are not implemented. Block `DIM6` carries the coefficients the input
relations need and nothing else, so leave it at zero and take dimension six from SMEFTsim.

The 60 baryon-number-violating operators are not included.

`models/dim8_plain` puts the same operators on the plain FeynRules Standard Model and is for
cross-checks only.
