# How to break it

For a reader who did not build this model, has an afternoon at most, and wants to know where the
physics is wrong rather than where the documentation is thin. It is written to be adversarial on
purpose. The first section is the ten minutes that get you a number, the second says what has
already been checked and to what level so that you do not spend the afternoon there, the third is
the ranked list of places where I think a determined person actually finds an error, and the last
is the list of traps that will look like a physics failure and are not. Read the last section
first if you are short of time, because every one of them has already cost me a day.

## Ten minutes to a number

Symlink `models/dim8_is` into MadGraph's `models/` directory, then run

    validate/quicktest.sh /path/to/MG5_aMC

which is six tests taking about fifteen minutes on one core, each printing the number it expects
before it runs. Two of them need no MadGraph and finish in five seconds. If you would rather
drive it yourself, the whole model in one process is

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

and that should give -1.189 +- 0.003 pb, the interference of `Q_{q^2W^2D}^{(1)}` alone at
13.6 TeV with Lambda at 1 TeV. Set `ebeam` explicitly, because MadGraph defaults to 6500 GeV a
beam and every number quoted here is at 6800. There is no prompt command that switches on all
1030 coefficients at once, which is what `examples/studies/set_cards.py` exists for and what the
quicktest uses. With all of them at 1 the same process gives -3.998 +- 0.012 pb against a
Standard Model 68.07 +- 0.15 pb and a dimension-eight square of 3989 +- 20 pb.

That last number is the first thing worth arguing about. The square is fifty-nine times the
Standard Model, so at c = 1 and Lambda = 1 TeV the expansion has no meaning in an inclusive
sample. That is the truncation failing, not the model, and it is the honest reason the paper
quotes interference and not squares.

## What is already checked, and how hard

Hermiticity of all 683 cached operator blocks, by an exact three-stage test rather than a
numerical one. Dimensional analysis and the NP order tag on all 152956 dimension-eight couplings
of the released model. The gluon and photon Ward identities on 21 processes with all 1030
coefficients switched on at 0.7 and Lambda at 1 TeV, passing at the 1e-14 level, which is the
test that catches a mis-normalised kinetic term and is the reason the form factors sit on vev^4.
At the level of cross sections, the 21 class interferences of `p p > w+ w-` sum to the all-on
result at 0.7 sigma and its 86 single-operator interferences at 0.5 sigma, which is a real
additivity test over 86 independent MadGraph runs.

Two more closed while this document was being written. The Standard Model limit of `dim8_is` with
every coefficient at zero gives 68.07 +- 0.15 pb for `p p > w+ w-` against 68.05 +- 0.24 pb from
MadGraph's own `sm` model with the same inputs, agreeing at 0.07 sigma, which is the cheapest
sharp test of the whole input-scheme construction and had never been run. And
`validate/truncation_check.py` shows that all 330 coefficient-dependent internal parameters have a
quadratic remainder that halves exactly when the coefficient halves, so no 1/Lambda^8 term
survives in the input relations, which are the part that is supposed to stop at 1/Lambda^4. That
is a statement about the parameters and not about the cross section, and the difference between
the two is the subject of the second entry in the next section.

## Three defects found while writing this, all confirmed by measurement

**`NP=0` carries O(1/Lambda^4) physics, so `NP^2==2` is not the whole interference.** Fourteen
couplings of the shipped model carry Wilson-coefficient dependence with no `NP` order tag: the
Higgs trilinear and quartic, `hWW`, `hZZ`, `h a a` and all nine `h f fbar`, reached through
`vevT`, `lam` and the Yukawas. The W mass shift sits in no coupling at all and cannot be tagged,
because MadGraph counts orders on couplings and a mass is not one. Measured on `p p > w+ w-` at
`NP=0`, the cross section is 68.03 +- 0.077 pb with every coefficient at zero and 69.38 +- 0.085
with every coefficient at one, a shift of +1.35 +- 0.115 pb, 11.7 sigma. It is linear in the
coefficient (0.72 +- 0.10 at c = 0.5) and falls as 1/Lambda^4 (consistent with the predicted
+0.084 at 2 TeV), so it is a genuine 1/Lambda^4 term, and it is not in the -3.998 pb that the
tables call the interference. The complete 1/Lambda^4 number for that process is about -2.65 pb.
`NP<=2` is unaffected, since it contains all three bins. It is the separation into a Standard
Model and an interference that does not hold. Reproduce it with
`validate/quicktest.sh` extended, or directly: generate `p p > w+ w- NP=0` and run it twice, once
with the coefficients off and once on.

It is process-dependent, which tells you when to worry. The same test on `p p > e+ e- a` gives
0.02097 +- 0.00009 pb with the coefficients off and 0.02097 +- 0.00009 with all of them at one,
identical to four digits on the same 5000 events, because that process has no W and no Higgs
coupling at tree level, so neither the mass shift nor the untagged Higgs couplings reach it. The
contamination is there whenever the process is sensitive to M_W or to a Higgs coupling, and
absent otherwise. Since the `NP=0` row is also the cheapest one in any study, run it both ways
and do not try to guess.

The remedy has two halves. The fourteen couplings are an emitter bug whose cure already sits
three lines above it in `gen/input_scheme.py`: `gw` and `g1` are emitted as FeynRules
*Definitions*, `gw -> gwSM (1 + gw1 + gw2)`, so FeynRules expands them, `gw2` appears
symbolically and the coupling is correctly tagged `NP=2`, which is why 37 couplings are right.
`vevT` is emitted as a *Parameter* with `InteractionOrder -> {QED,-1}`, is never expanded, and
everything built from it comes out untagged. The mass shift needs a procedural fix instead: the
1/Lambda^4 prediction has to be assembled as the `NP^2==2` cross section plus the difference of
the `NP=0` cross section with the coefficients on and off, which picks up whatever remains
untagged whether or not the emitter is fixed.

**Six four-fermion operators are presented as live and give exactly zero.** Every
`Q_{psi^4B}^{(1)}` and `^{(3)}` has no coupling in the model, and every dual partner `^{(2)}`,
`^{(4)}` has some, although the same symmetry argument kills both: the dual field strength is
antisymmetric in its two indices exactly as the field strength is. The survivors are dead. In the
`mu+ mu- e+ e- a` vertex the structures `FFFFV143` and `FFFFV156` differ by a swap of two dummy
indices inside one `Epsilon`, so one is minus the other, and they carry the same coupling.
Evaluated numerically each is 29.50 and the sum is 5e-15. So the count of
operators that vanish for a flavour-universal coefficient is fifteen and not nine, and the number
of live card entries is 893 and not 899.

**The release gate for identically-zero Lorentz structures is incomplete, and nine of them are
still in the shipped model.** `Q_{q^4B}^{(4)}` keeps 170 couplings and does generate diagrams, 24
of them for `u u~ > d d~ a`, and then the run dies with "A compilation Error occurs when trying to
compile ... P1_uux_ddxa". The real message appears only if you run `make` in `Source/DHELAS` by
hand, and it is "Symbol 'f1' at (1) has no IMPLICIT type", the signature of ALOHA reducing a
structure to zero and then writing a Fortran routine whose arguments it never declares.

Ten such structures were dropped at release by `validate/zero_lorentz.py`. That test has two
holes. It skips anything containing a Gamma matrix, on an assumption its own docstring states,
and it never imposes momentum conservation on the momenta it randomises, so it can only ever
catch a structure that vanishes by the antisymmetry of `Epsilon` alone. Run today it reports
zero. `validate/zero_vertex.py` handles Dirac structures and conserves momentum, and finds nine,
used by fifty vertices of `models/dim8_is`:

| structure | coefficients | example vertex |
|---|---|---|
| `VVV5` | `c8G2H4x2`, `c8W2H4x2`, `c8WH4D2x2` | `W- W+ Z` |
| `VVS4`, `VVSS7`, `VVSSS6`, `VVSSSS6` | `c8WH4D2x4` | `W- W+ H` and its Higgs tower |
| `FFVV56` | `c8l2WBDx3`, `c8q2WBDx3` | `b~ b Z Z`, 24 vertices |
| `FFVVV187`, `FFVVV188` | `c8q2W2Dx3`, `c8q2W2Dx4` | `b~ c a g W+`, 15 vertices |
| `FFVVV344` | `c8l2WBDx3` | `e+ e- a Z Z` |

`VVV5` is a physical zero worth understanding rather than a bug in the operator: the vev piece of
`(H^dag H)^2 G Gtilde` is a theta term, a total derivative, so its three-boson vertex with no
Higgs leg has to vanish. The defect is that the model ships it as a live vertex with a zero
structure. Whether that breaks a build depends on which way ALOHA simplifies: `VVV5` does not,
and the triboson study's class-6 row of `p p > w+ w- z` ran to -0.001324 pb, while the
four-fermion one does. Every one of the fifty is a latent instance of a failure whose error
message points at the wrong thing.

**A fourth, found in the shipped cards rather than the model.** `restrict_cpeven.dat` kept 128
CP-odd operators, among them `Q_{B^4}^{(3)}` and every `Q_{X^2H^2D}^{(2),(4)}` dipole partner, so
`import model dim8_is-cpeven` gave a CP-violating model. The rule in `examples/release_model.sh`
asked for `'tilde' not in e['ops'][0]`, and no operator label in the basis contains the string
`tilde`, because the dual lives in the LaTeX. The clause matched nothing and the card was really
"operators with a real Wilson coefficient". It now counts duals in the LaTeX, requires an even
count for every operator in the block rather than only the first, and keeps 289 with none CP-odd.
The `bosonic` card next to it uses the same label-substring trick and does happen to be right,
which is luck rather than design.

## Where else I think it breaks

**The four-fermion sector, classes 18 to 21.** This was the weak point and it is now half closed.
Those 311 operators are built, Hermiticity-checked, dimension-audited and present in the model,
and until today not one had appeared in a MadGraph cross section, so everything else validated
here tests the bosonic and two-fermion half of the basis. `p p > e+ e- | mmll=200` with all
coefficients at 1 and Lambda at 1 TeV now gives, at `NP^2==2`, class 18 at +0.03765 +- 0.00048 pb,
class 20 at -9.965e-06 +- 2.7e-08 and class 21 at +0.1877 +- 0.0070, against a full-model
+0.2114 +- 0.0062. That is 202 of the 311 exercised inside a class card. Class 19 has no diagram
there, and `p p > e+ e- a | mmll=200 pta=20 dral=0.4` reaches it and is running. None of them has
been run one at a time. If something is wrong in the basis translation, the contact terms are where I would look
first, because they are the operators whose Fierz and colour structures had the least independent
cross-checking and because ALOHA already refuses to write the baryon-number-violating members of
the same classes.

**Operators that act only through the input relations.** This is the subtlety I would attack if I
wanted to find a conceptual error rather than a coding one. The muon-decay operators
`Q_{l^2H^4D}^{(2)}` and `^{(4)}` have no vertex in any `p p > w+ w-` diagram, yet each contributes
-0.7164 pb, together a third of the whole dimension-eight interference, by shifting gw2, the vev
and M_W. The mechanism matters: a shifted coupling carries the `NP=2` order tag and MadGraph
counts it, while a shifted mass carries no tag at all. So the order counting is not a complete
description of where the dimension-eight dependence lives, and a process-specific model built by
selecting operators that have a vertex is incomplete in this scheme. `./dim8 select` says so now,
but the general question of what the untagged mass shift does is the sharpest thing I know to ask,
and it is measurable rather than rhetorical. With all 1030 coefficients at 1 and Lambda at 1 TeV
the W mass comes out at 79.325 GeV against 79.824 in the Standard Model, a shift of 0.625 per cent
that falls exactly as 1/Lambda^4. The interference therefore does not scale exactly as 1/Lambda^4
either, because the Standard Model half of it is evaluated at that shifted mass. Measured, it does
not: -3.998 +- 0.012 pb at 1 TeV against -0.2479 +- 0.0010 pb at 2 TeV, where exact scaling would
give -0.2499, a deviation of 0.79 per cent. Fitting sigma = A/Lambda^4 + B/Lambda^8 to those two
points gives B/A = 0.85 per cent at 1 TeV, the same size as the mass shift, which is what the
mechanism predicts with a sensitivity of order one. That fit then predicts 3 TeV blind, and the
measurement is -0.04891 +- 0.00014 pb against a prediction of -0.048947, agreeing at 0.27 sigma,
while pure 1/Lambda^4 scaling from the 1 TeV point predicts -0.049358 and misses by 3.2 sigma.
So the effect is real, it is the size the W mass shift says it should be, and a third point
confirms a fit made without it. I believe this is correct rather than a bug,
because the input scheme is defined at fixed G_F and a 1/Lambda^8 remainder is beyond the
truncation, but it does mean the coupling-order label is not a complete bookkeeping of the
Lambda expansion in this model. Disagreeing with that reading would be a real finding.

**The nine operators that vanish.** Seven of them contract two identical currents, symmetric in
their Lorentz indices, with an antisymmetric field strength, and two vanish by their SU(2)
structure. I claim this is a consequence of taking one flavour-universal coefficient per operator
and not a bug, and the argument is short enough to check independently in ten minutes. If any of
them should be nonzero the whole flavour-universal simplification is in question.

**Class 1 at high multiplicity.** `Q_{G^4}^{(4)}` and `Q_{G^4}^{(8)}` carry no seven- or
eight-gluon vertex in the shipped model. Nothing below seven external gluons can see it, so it
does not affect any realistic process, but it is a genuine hole rather than a physical zero.

**Conventions against an external implementation.** Nothing here has been compared against an
independent public dimension-eight implementation. The overlap with the Eboli and Gonzalez-Garcia
quartic-gauge operators is the obvious target, and a single matched cross section would either
close a convention question or open a real one.

## Traps that look like physics failures

`set Lam 1000` at the launch prompt does nothing at all and prints no error. MadGraph lowercases
parameter names, `lam` is already the Higgs quartic, and the card therefore calls the scale
`lam__2`. Ten of the example scripts were setting the scale and silently not setting it, and
example 09 was scanning Lambda while holding it fixed. Use `set lam__2 1000` or `set dim8 0 1000`.

`hel_recycling` defaults to on in MadGraph 3.5 and fails at event generation on these Lorentz
structures with "split amp are not supported for spin2 and 3/2". Set it to `False`. The default
run card does not contain the key, so it has to be appended.

Every Wilson coefficient is zero by default, which means `check lorentz` and `check gauge` on the
model as shipped test the Standard Model part and nothing else, and a process with no Standard
Model tree amplitude such as `g g > h g` reports "not checked" rather than a result. MadGraph's
`check` also accepts a param card argument and then ignores it. The only way to check with
coefficients on is a model copy whose defaults are on, which `validate/ufo_on.py models/dim8_is
0.7` writes.

`import model` takes an installed name or an absolute path. A relative path fails with "is not a
valid pathname" because MadGraph resolves it against its own directory.

A restriction card that keeps only operators with no vertex removes the `NP` coupling order
itself, and MadGraph then answers `NP^2==2` with "model order NP^2 not valid for this model"
without saying why.

"No amplitudes generated" for the `X^2H^2D^2` operators of class 7 in a two-to-two diboson process
is physics. Their lowest vertex is four-point, so one insertion cannot enter. Diboson at two-to-two
gets classes 11, 13, 14 and 15.

`event_norm` in the run card defaults to `average`, so every event of an unweighted sample carries
the full cross section as its weight and sigma is the mean of the weights rather than the sum.
Normalise histograms to the banner's integrated weight.

Diagram generation is what the full basis costs. `p p > w+ w- NP<=2` is 458 diagrams in 25
seconds, but `p p > h h j j QCD=0 NP<=2` on the unrestricted model is 166 subprocesses and 298888
diagrams in four and a half minutes followed by hours of code generation, because every
four-fermion and psi^2XH operator adds a contact term. Restrict first.

Use Python 3.11. Python 3.12 generates events but disables reweighting and 3.13 breaks
`model_reader`.

## What is not here

Flavour is universal, one coefficient per operator, so anything that needs a flavour structure
needs the pipeline rather than the shipped model. The 60 baryon-number-violating operators are in
the catalogue and not in the model, because ALOHA cannot write their fermion-flow-violating
four-point vertices. Dimension six is absent and has to come from SMEFTsim alongside.
