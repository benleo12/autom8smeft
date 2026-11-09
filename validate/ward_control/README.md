# The control of the Ward test

`dim8_plain` here is not a model to run. It holds the same operators as the released models on the FeynRules
Standard Model, with no input relations. Its fields are not canonical once an operator shifts a two-point term,
and FeynRules writes no two-point vertex into a UFO, so it is not gauge invariant with such an operator on:
with `Q_{G^2H^4}^{(1)}` at one and Lambda = 3 TeV, `g g > g g` moves by -2464 pb.

It is here because it shows that the Ward test can fail. `validate/mg5_gluon_check.sh` runs MadGraph's `check
lorentz` on processes with an external massless vector. With the dimension-eight coefficients on, the released
models pass on all of them, and this one fails on the processes that a shifted gluon or W kinetic term reaches.
`examples/16_plain_vs_input_scheme.md` gives the details. It ships packed: unpack it here with
`tar -xJf dim8_plain.tar.xz`, then link it into the `models` directory of MadGraph to run it.
