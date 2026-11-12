# Drell-Yan study

High-mass neutral-current Drell-Yan at 13.6 TeV, `p p > e+ e-` and `p p > e+ e- a`, both with the
lepton pair above 200 GeV. This is the process that reaches the four-fermion classes with a vertex.
311 of the 674 operators sit in classes 18 to 21. Class 18 enters every study, in diboson and
triboson production through the G_F relation alone, and the others appear in no other study, so
without this one classes 19 and 21 would appear in no cross section. Class 19, psi^4 X, needs the
extra photon and gives no diagram in `p p > e+ e-` alone, which is why the second process is there.
Class 20 has no diagram here either: it flips chirality, and the cards of the studies keep only the
Yukawa couplings of the b and the t.

Run

    examples/studies/run_study.sh examples/studies/drellyan models/dim8_mw 5000

Conventions and columns are those of the other studies, and so are the records of each cross
section in `records.tsv` that the table scripts check: see `../diboson/README.md`.
