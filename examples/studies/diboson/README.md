# diboson study

Cross sections at 13.6 TeV for the processes in `processes.txt`, in the Standard Model
(`NP=0`, every Wilson coefficient at zero), at 1/Lambda^4 (`NP^2==2`) and at the
dimension-eight-squared order (`NP<=2 NP^2==4`), first with the full model and every
coefficient at 1 with Lam at 3 TeV, then one operator class at a time through the restriction
cards listed in `classes.txt`. Running one class at a time is what isolates the classes that
dominate and shows where the squared term overtakes the interference, as in the study of
dimension eight in vector-boson-fusion Higgs production, arXiv:2410.21563.

The four processes are the on-shell diboson final states. `p p > w+ w-` is the one where the
input scheme matters most. In the {alpha, MZ, GF} scheme the coefficient shifts of
`Q_{W^2H^4}^{(1)}` and `Q_{H^6}^{(1)}` cancel exactly, and neither operator has any O(1/Lambda^4)
effect there. The largest class interferences in `p p > w+ w-` are those of class 14
(psi^2 X^2 D), class 18 (psi^4 H^2), class 13 (psi^2 H^4 D) and class 11 (psi^2 H^2 D^3), as
`table.md` shows. The bosonic X^2 H^2 D^2 class has no three-point vertex, so its interference rows say no
diagram here, and its interference first appears in the triboson study. Its squared row in
`p p > w+ w-` is `g g > w+ w-` through a G G W W contact vertex, which has no Standard-Model
amplitude to interfere with.

Run

    examples/studies/run_study.sh examples/studies/diboson models/dim8_mw 5000

The class cards ship in the model directory, written by `examples/release_model.sh` when it
builds `models/dim8_mw`, and `validate/make_restriction.py <model> cls7 cls:7` writes one at a
time. Cross sections append to `results.tsv` and the event files are kept in `lhe/`,
one per row, from which

    examples/studies/plot_study.py diboson SM=lhe/<...>_NP_0.lhe.gz int=lhe/<...>_NP_2_2.lhe.gz

makes the invariant-mass and leading-p_T tables and plots for the paper.

Every cross section also gets a record in `records.tsv`: the version of the model MadGraph read,
the MadGraph version, the param and run cards, with a copy of each in `cards/`, and the event file
with its sha256. `examples/studies/provenance.py check results.tsv` checks each line of
`results.tsv` against its record, its event file and its cards. The table scripts and
`plot_study.py` make the same check first and write nothing if it fails, and `plot_study.py` names
the event files it read in `diboson.sources.tsv`, which `paper_figure.py` checks before it draws.
`docs/RUN_YOUR_OWN_ANALYSIS.md` (section 5) says what is compared.

The interference samples need more events than the Standard-Model ones. Their integral is a
difference of positive and negative weights, so the effective statistics is the excess of one
over the other rather than the event count, and at a few thousand events the unweighted sample
can sit tens of per cent away from the integration's own cross section. `plot_study.py`
normalises each histogram to the integrated weight from the banner and prints the factor it
used, which is the signal to raise the event count if the factor is far from one.

One caution about the all-coefficients-at-one row. With every coefficient at 1 (those of `DIM8F`
included) and Lam at 3 TeV, the squared term for `p p > w+ w-` comes out 23 times the
interference, so the truncation is not self-consistent for that row. That row is a linearity
check, since the class interferences must add up to it, rather than a prediction. The physics is
in the per-class rows, where only a handful of operators are on. In `dim8_mw` the W mass is an
input, so no coefficient moves it, and `results.tsv` carries the W mass and the coefficient
settings of every row.

How to read the class-1 rows. At `NP^2==2` the X^4 class gives no diagram at all in
`p p > w+ w-`, because a four-field-strength operator has no three-point vertex and its
four-point ones cannot attach to a quark line, so the row says NO_DIAGRAMS. At `NP<=2 NP^2==4`
the same class gives 0.55 pb at Lam = 3 TeV, 21 times the interference of the whole model:
that is `g g > w+ w-` through the G^2 W^2 contact vertex squared, one diagram, with no
Standard-Model amplitude to interfere with, growing like s^2/Lambda^4 in the amplitude and fed by
the gluon luminosity. Since it falls as 1/Lambda^8 it is thousands of picobarns at Lam = 1 TeV,
the clearest illustration in the study of why the squared column cannot be read as a prediction
at low Lambda with coefficients of order one, and why the paper quotes it with the scale caveat.
The full-model squared row is dominated by the same terms.
