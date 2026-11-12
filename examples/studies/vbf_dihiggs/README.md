# VBF di-Higgs study

Cross sections at 13.6 TeV for the processes in `processes.txt`, in the Standard Model
(`NP=0`, every Wilson coefficient at zero), at 1/Lambda^4 (`NP^2==2`) and at the
dimension-eight-squared order (`NP<=2 NP^2==4`), first with the full model and every
coefficient at 1 with Lam at 3 TeV, then one operator class at a time through the restriction
cards listed in `classes.txt`. Running one class at a time is what isolates the classes that
dominate and shows where the squared term overtakes the interference, as in the study of
dimension eight in vector-boson-fusion Higgs production, arXiv:2410.21563.

`QCD=0` removes the QCD topologies at tree level so that what is left is genuine vector-boson fusion. The cuts in `processes.txt` (jet p_T above 25 GeV, |eta| below 5, dijet mass above 400 GeV) are the usual VBF selection and are applied through the run card, not at the launch prompt. This is the process where the energy-enhanced classes of arXiv:2410.21563 show up most clearly, and where the squared term overtakes the interference first.

Run

    examples/studies/run_study.sh examples/studies/vbf_dihiggs models/dim8_mw 5000

The class cards ship in the model directory, written by `examples/release_model.sh` when it
builds `models/dim8_mw`, and `validate/make_restriction.py <model> cls7 cls:7` writes one at a
time. Cross sections append to `results.tsv` and the event files are kept in `lhe/`,
one per row, from which

    examples/studies/plot_study.py vbf_dihiggs SM=lhe/<...>_NP_0.lhe.gz int=lhe/<...>_NP_2_2.lhe.gz

makes the invariant-mass and leading-p_T tables and plots for the paper.

Every cross section also gets a record in `records.tsv`, and the table scripts and `plot_study.py`
check each line of `results.tsv` against it before they write anything, as in `../diboson/README.md`.

The interference samples need more events than the Standard-Model ones. Their integral is a
difference of positive and negative weights, so the effective statistics is the excess of one
over the other rather than the event count, and at a few thousand events the unweighted sample
can sit tens of per cent away from the integration's own cross section. `plot_study.py`
normalises each histogram to the integrated weight from the banner and prints the factor it
used, which is the signal to raise the event count if the factor is far from one.

One caution about the row with every coefficient at one, which runs on the `bosonic` card in
this study. With every coefficient of that card at 1 and Lam at 3 TeV, the squared term of that
row comes out four times the interference, so the truncation is not self-consistent for it. That
row is a linearity check, since the class interferences must add up to it, rather than a
prediction. The physics is in the per-class rows, where only a handful of operators are on. In
`dim8_mw` the W mass is an input, so no coefficient moves it, and `results.tsv` carries the W mass
and the coefficient settings of every row.
