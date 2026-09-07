# triboson study

Cross sections at 13.6 TeV for the processes in `processes.txt`, in the Standard Model
(`NP=0`, every Wilson coefficient at zero), at 1/Lambda^4 (`NP^2==2`) and at the
dimension-eight-squared order (`NP<=2 NP^2==4`), first with the full model and every
coefficient at 1 with Lam at 1 TeV, then one operator class at a time through the restriction
cards listed in `classes.txt`. Running one class at a time is what isolates the classes that
dominate and shows where the squared term overtakes the interference, as in the VBF paper.

Triboson production reaches the quartic gauge vertices directly, so class 1 (X^4) and class 7 (X^2 H^2 D^2) contribute at tree level here and not in diboson production. The cross sections are small, so these runs want more events than the diboson ones.

Run

    examples/studies/run_study.sh examples/studies/triboson models/dim8_is 5000

The class cards have to exist in the model directory first, which `examples/release_model.sh`
does when it builds `models/dim8_is`, or `validate/make_restriction.py <model> cls7 cls:7`
one at a time. Cross sections append to `results.tsv` and the event files are kept in `lhe/`,
one per row, from which

    examples/studies/plot_study.py triboson SM=lhe/<...>_NP_0.lhe.gz int=lhe/<...>_NP_2_2.lhe.gz

makes the invariant-mass and leading-p_T tables and plots for the paper.

The interference samples need more events than the Standard-Model ones. Their integral is a
difference of positive and negative weights, so the effective statistics is the excess of one
over the other rather than the event count, and at a few thousand events the unweighted sample
can sit tens of per cent away from the integration's own cross section. `plot_study.py`
normalises each histogram to the integrated weight from the banner and prints the factor it
used, which is the signal to raise the event count if the factor is far from one.

One caution about the all-coefficients-at-one row. The W mass is derived in the {alpha, MZ, GF}
scheme, so switching coefficients on moves it: with all 1030 at 1 and Lam at 1 TeV the model
derives 79.33 GeV instead of the tree-level 79.82 of the {alpha, MZ, GF} scheme, and the squared term for `p p > w+ w-` comes out three times
the Standard Model, which is not a regime where the expansion means anything. That row is a
linearity check, since the class interferences must add up to it, rather than a prediction. The
physics is in the per-class rows, where only a handful of operators are on and the shift is
small. `results.tsv` carries the derived W mass and the coefficient settings for every row so
that a distorted one is visible rather than buried.
