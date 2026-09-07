# diboson study

Cross sections at 13.6 TeV for the processes in `processes.txt`, in the Standard Model
(`NP=0`, every Wilson coefficient at zero), at 1/Lambda^4 (`NP^2==2`) and at the
dimension-eight-squared order (`NP<=2 NP^2==4`), first with the full model and every
coefficient at 1 with Lam at 1 TeV, then one operator class at a time through the restriction
cards listed in `classes.txt`. Running one class at a time is what isolates the classes that
dominate and shows where the squared term overtakes the interference, as in the VBF paper.

The four processes are the on-shell diboson final states. `p p > w+ w-` is the one where the input scheme matters most: in the {alpha, MZ, GF} scheme the coefficient shifts of `Q_{W^2H^4}^{(1)}` and `Q_{H^6}^{(1)}` cancel exactly and neither operator has any O(1/Lambda^4) effect there, so the interference comes from the two-fermion classes 11, 13, 14 and 15 (psi^2 H^2 D^3, psi^2 H^4 D, psi^2 X^2 D and psi^2 X H^2 D). The bosonic X^2 H^2 D^2 class has no three-point vertex and gives no diagram in 2 to 2 diboson production, its per-class rows come out empty here and it first appears in the triboson study.

Run

    examples/studies/run_study.sh examples/studies/diboson models/dim8_is 5000

The class cards have to exist in the model directory first, which `examples/release_model.sh`
does when it builds `models/dim8_is`, or `validate/make_restriction.py <model> cls7 cls:7`
one at a time. Cross sections append to `results.tsv` and the event files are kept in `lhe/`,
one per row, from which

    examples/studies/plot_study.py diboson SM=lhe/<...>_NP_0.lhe.gz int=lhe/<...>_NP_2_2.lhe.gz

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

How to read the class-1 rows. At `NP^2==2` the X^4 class gives no diagram at all in
`p p > w+ w-`, because a four-field-strength operator has no three-point vertex and its
four-point ones cannot attach to a quark line, so the row says NO_DIAGRAMS. At `NP<=2 NP^2==4`
the same class gives thousands of picobarns: that is `g g > w+ w-` through the G^2 W^2 contact
vertex squared, one diagram, with no Standard-Model amplitude to interfere with, growing like
s^2/Lambda^4 in the amplitude and fed by the gluon luminosity. It is the clearest illustration
in the study of why the squared column cannot be read as a prediction at Lam = 1 TeV with
coefficients of order one, and why the paper quotes it with the scale caveat. The full-model
squared row is dominated by the same terms.
