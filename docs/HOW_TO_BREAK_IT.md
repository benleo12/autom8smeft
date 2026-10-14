# How to break it

For a reader who did not build this model, has an afternoon at most, and wants to know where the
physics is wrong rather than where the documentation is thin. It is written to be adversarial on
purpose. The first section is the ten minutes that get you a number. The next three say what has
already been checked and to what level, so that you do not spend the afternoon there. Then comes
the ranked list of places where I think a determined person actually finds an error, and then the
traps that look like a physics failure and are not. Read the traps first if you are short of
time.

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

The same Ward identities with the dimension-six sector on instead: the 64 real coefficients of
block `DIM6`, thirty processes, at `NP<=1` and at `NP<=2`, sixty checks passing at the 1e-13
level on the released `dim68_is`. And the two-point terms, which no
Ward identity on a `Z` or a Higgs can see: `validate/check_bilinears.wls` shows the twelve kinetic
and mass terms of the gauge bosons and the Higgs canonical through `1/Lambda^4` with nine
dimension-six coefficients on, in both input schemes. "The dimension-six sector" below says what
each of them tests.

Restriction cards are exactly equivalent to the full model, which matters because every class row of
every study is a restricted model compared against a full one. `p p > w+ w- NP^2==2` with
`c8q2W2Dx1` at 1 gives -1.182, -1.186, -1.188, -1.185 pb on four seeds through the full model at 456
diagrams, and the same four numbers to every printed digit, error bars included, through the
one-operator card at 24 diagrams. Not consistent within errors, identical.

Two more. The Standard Model limit of `dim8_is` with every coefficient at zero gives
68.07 +- 0.15 pb for `p p > w+ w-` against 68.05 +- 0.24 pb from MadGraph's own `sm` model with
the same inputs, agreeing at 0.07 sigma, which is the cheapest sharp test of the whole
input-scheme construction. And
`validate/truncation_check.py` shows that all 330 coefficient-dependent internal parameters have a
quadratic remainder that halves exactly when the coefficient halves, so no 1/Lambda^8 term
survives in the input relations, which are the part that is supposed to stop at 1/Lambda^4. That
is a statement about the parameters and not about the cross section, and the difference between
the two is the subject of "Operators that act only through the input relations" below.

## Four things that are easy to get wrong, and how the model handles them

**Every coupling that depends on a coefficient carries an `NP` order.** The input scheme shifts the
gauge couplings, the vev, the Yukawas and the Higgs quartic. If any of these shifts sat inside a
parameter that FeynRules does not expand, the couplings built from it would carry coefficient
dependence with no order tag: the Higgs trilinear and quartic, `hWW`, `hZZ`, `h a a` and all nine `h
f fbar`. The `NP=0` bin would then carry `1/Lambda^4` physics. The product of an untagged shift with
a tagged vertex, quadratic in the coefficient, would also be counted at `NP^2==2`. The shifts are
therefore written as FeynRules *Definitions*, which FeynRules expands and tags piece by piece. The
weak coupling is `gw -> gwSM (1 + gw1 + gw2)`, and `g1` is written the same way. The doublet carries
`vevSM (1 + vev1 + vev2)`, LHiggs carries `lam (1 + lamr1 + lamr2)` and LYukawa carries `y_f (1 +
yr1 + yr2) + c8fH5 vevSM^4 L8/4`, with the four series derived by `gen/derive_higgs_yukawa.py` from
the exact relations. `validate/audit_ufo.py` checks that no coupling without an `NP` order touches a
coefficient.

`validate/lambda_scaling.py` is the test that sees a failure here. A class whose linear term is
chirality-suppressed, psi^2 H^5 in `e+ e- > w+ w-`, returns a ratio of 15.9 between 1 and 2 TeV at
an interference of -1.9e-9 pb. An untagged shifted Yukawa would make the interference fall as
1/Lambda^8, a ratio of 256. And in `e+ e- > z h`, a process with no W anywhere, the `NP=0` bin is
0.01196 pb at 1 TeV on one seed with the coefficients on and with them off.

What remains is a property of the {alpha, M_Z, G_F} scheme rather than of this model. The W mass
is derived, it shifts with the eight input-scheme coefficients, and it sits in a propagator and in
the phase space, where no coupling order reaches it. It is kept exact, which is what SMEFTsim 3
does by default (its linearised option uses dummy fields and a custom propagators.py, and its guide
warns that expanding a mass shift inside a propagator distorts the W line shape). So the complete
1/Lambda^4 prediction is the `NP^2==2` cross section plus the difference of the `NP=0` cross
section with the coefficients on and off. That bracket is zero in any process in which no W is
produced or exchanged. VBF di-Higgs has no W in its final state and the bracket is 6.8 per cent of
its cross section, through the W mass in its two t-channel propagators. Since the `NP=0` row is
the cheapest one in any study, run it both ways rather than guess. In the {M_W, M_Z, G_F} scheme
the bracket is absent by construction.

**Three four-fermion operators have vertices that sum to zero in the released models.** They are
`Q_{ledqB}^(2)`, `Q_{lequB}^(2)` and `Q_{q^2udB}^(2)`, independent members of the Murphy basis that
are not zero as operators, on 90, 126 and 114 vertices, none of which survives the sum.
Two structures of the same vertex differ by a swap of two dummy indices inside one `Epsilon`, so
one is minus the other, and they carry the same coupling: evaluated numerically each is 29.50 and
the sum is 5e-15. With the nine operators that have no vertex at all ("The nine operators that
vanish", below), twelve of the 674 coefficients have no effect in the released models. Each of the three
carries a complex coefficient and so occupies two card entries, Re and Im, so 893 of the 899
entries with vertices do something. Every other `psi^4 B` dual is alive, and so is `c8G2H4x2`.

`validate/zero_vertex.py --wcs` finds the three. It takes each vertex's leg count from the vertex
rather than from the indices its structure happens to mention. A count inferred from the indices
imposes the wrong momentum conservation and turns live structures into false zeros, which
`evaluate()` warns about in its own docstring and `zero_structures()` honours.

**No identically-zero Lorentz structure ships.** ALOHA reduces such a structure to zero and then
writes a Fortran routine whose arguments it never declares. A process that reaches one dies at
compilation. With such a structure in place, `Q_{q^4B}^{(4)}` generates 24 diagrams for
`u u~ > d d~ a`, and the run then stops with "A compilation Error occurs when trying to compile ...
P1_uux_ddxa". The real message appears only if you run `make` in `Source/DHELAS` by hand, and it
is "Symbol 'f1' at (1) has no IMPLICIT type".

`validate/zero_vertex.py` handles Dirac structures and conserves momentum. Besides the structures
that vanish by the antisymmetry of `Epsilon` alone, it finds nine that need the Dirac algebra or
momentum conservation to vanish, on fifty vertices of `models/dim8_is` and fifty-seven of
`models/dim68_is`:

| structure | coefficients | example vertex |
|---|---|---|
| `VVV5` | `c8G2H4x2`, `c8W2H4x2`, `c8WH4D2x2` | `W- W+ Z` |
| `VVS4`, `VVSS7`, `VVSSS6`, `VVSSSS6` | `c8WH4D2x4` | `W- W+ H` and its Higgs tower |
| `FFVV56` | `c8l2WBDx3`, `c8q2WBDx3` | `b~ b Z Z`, 24 vertices |
| `FFVVV187`, `FFVVV188` | `c8q2W2Dx3`, `c8q2W2Dx4` | `b~ c a g W+`, 15 vertices |
| `FFVVV344` | `c8l2WBDx3` | `e+ e- a Z Z` |

`validate/zero_lorentz.py` cannot replace it. It skips anything containing a Gamma matrix, on an
assumption its own docstring states, and it never imposes momentum conservation on the momenta it
randomises, so it can only catch a structure that vanishes by the antisymmetry of `Epsilon` alone.

`VVV5` is a physical zero worth understanding rather than a defect of the operator: the vev piece
of `(H^dag H)^2 X Xtilde` is a theta term, a total derivative, so its three-boson vertex with no
Higgs leg has to vanish. Whether a zero structure breaks a build depends on which way ALOHA
simplifies it. `VVV5` does not, and the triboson study's class-6 row of `p p > w+ w- z` runs to
-0.001324 pb, while the four-fermion one does. The failure has an error message that points at the
wrong thing, so every zero structure is removed rather than left to the processes that happen to
survive it.

`validate/drop_zero_structures.py` does the removal, and `examples/release_model.sh` calls it.
The part that needs care is not the deletion. Only fifteen of the fifty vertices have nothing in
them but dead structures. The other thirty-five carry live ones alongside, and a UFO vertex keys
its couplings by position in its own `lorentz` list, so dropping an entry renumbers every index
above it. Delete the list entry without remapping `couplings = {(colour, lorentz): coupling}` and
the model still imports and gives wrong numbers, which is worse than a model that fails. The
script remaps, and writes all three files or none. `validate/zero_vertex.py <model> --structures`
reports zero on the released models.

**The CP cards use the derived parity, not a count of duals.** `restrict_cpeven.dat` and
`restrict_cpodd.dat` keep the operators with a real coefficient whose CP parity is even or odd.
Counting dual field strengths is not the CP parity at dimension eight. The derivation, C times P
field by field, sits in `gen/cp_parity.py` and disagrees with dual counting on 170 of the 438
operators with a real coefficient, most sharply in `Q_{q^2W^2D}^{(1..4)}` where the member carrying
NO dual is the CP-odd one. `validate/cp_rates.py` is the test: switch on what a card calls the
CP-odd set and the interference with the Standard Model in a total rate must vanish. A set chosen
by counting duals gives -1.2 pb on `p p > w+ w-`. If you want to break something here, check the
derivation itself against your own C and P assignments for a class we have not quoted.

## The dimension-six sector

The Ward checks above switch on the dimension-eight coefficients only, and a check with only those
on does not look at the dimension-six sector of `dim68_is` at all. That sector has checks of its
own, which switch its coefficients on, and the details are in [DIM6.md](DIM6.md). They test three
constructions.

**`O_HG` is written with its vacuum piece subtracted.** On a base that does not rescale the gluon,
the vacuum piece of `O_HG` moves the three- and four-gluon vertices and not the quark-gluon vertex.
Five of six gluonic processes then fail `check lorentz` at `NP<=1`, `u u~ > g g` at 1e-2. A
cross-section comparison of `cHG` against SMEFTsim on `g g > h` agrees to four digits all the same,
because the vacuum piece does not touch the Higgs vertices.

**The operators are evaluated on the shifted couplings and on the rotated fields.** Shifted `g`
and `g'` on unrotated fields give a photon coupled to neutrinos, a bare `g^{mu nu}`
photon-Z-Higgs vertex and a W-W-photon coupling that is not `e`, all at `1/Lambda^4`, and seven
of fourteen processes then fail at `NP<=2`.

**The Higgs quartic and the Higgs rescaling use the same truncation.** Both second-order relations
take the dimension-six operators at the corrected vev. No Ward identity sees the Higgs two-point
function. `validate/check_bilinears.wls` does, and a mismatch shows there as a Higgs mass off its
input, by 2.3e-3.

Two guards on the build stop a wrong model being written from right inputs. FeynRules sums the
terms of a coupling one at a time through a rule that Mathematica stops applying after 4096
iterations, and writes the unevaluated remainder into the UFO, so a coupling with more terms
makes the model unimportable. Couplings of 5810 terms occur. `validate/fr_writeufo.wls` lifts the
limit and reads the written file back. A file left in a cache directory, such as the dump of a
Hermiticity check, would be read as a block, and the next block would then enter the model twice.
The writer aborts on any file that does not hold a vertex list. Before a rebuilt model is
released, its linear couplings are compared with the last validated one, vertex by vertex.

**In the `{MW, MZ, GF}` model, `ee` stays at its Standard Model value.** There alpha is derived,
and `ee` is an untagged parameter that 33334 dimension-eight couplings carry. `ee` and `aEW` are
held at the SM value derived from the inputs, and the derived alpha is kept as `aEWM1` for reading
only. If `ee` followed the shifted alpha, every such coupling would carry a factor
`(1 + aEW2/2)`, a second coefficient inside a coupling tagged `NP=2`. With one coefficient on, the
factor is the identity and every check passes. With `c8W2H4x1` and `c8W2H4x3` on together,
`u d~ > w+ a` fails at 1e-5. A Ward check run one coefficient at a time cannot see a product of
two, so the standard run switches all of them on.

To repeat these checks:

    WARD_ON=dim6 WARD_ORDER="NP<=1" validate/mg5_gluon_check.sh models/dim68_is "" validate/procs_dim6.txt
    WARD_ON=dim6 WARD_ORDER="NP<=2" validate/mg5_gluon_check.sh models/dim68_is "" validate/procs_dim6.txt
    wolframscript -file validate/check_bilinears.wls
    python3.11 validate/gf_closure.py models/dim68_is

The last is the one with a physical observable in it: muon decay, which must not move when a
coefficient is switched on because `G_F` is an input. Without the products of `O_Hl3` with the
first-order shifts it moves at second order.

## Where else I think it breaks

**The four-fermion sector, classes 18 to 21.** Those 311 operators are built, Hermiticity-checked,
dimension-audited and present in the model. Of the studies, only Drell-Yan reaches them in a cross
section, so most of what is validated here tests the bosonic and two-fermion half of the basis.
`p p > e+ e- | mmll=200` with all coefficients at 1 and Lambda at 1 TeV gives, at `NP^2==2`,
class 18 at +0.03765 +- 0.00048 pb, class 20 at -9.965e-06 +- 2.7e-08 and class 21 at
+0.1877 +- 0.0070, against a full-model +0.2114 +- 0.0062. That is 202 of the 311 exercised
inside a class card. Class 19 has no diagram there, and `p p > e+ e- a | mmll=200 pta=20 dral=0.4`
reaches it, at -3.35e-4 pb of interference. None of them has been run one at a time. If something
is wrong in the encoding, the contact terms are where I would look first. They are the operators
whose Fierz and colour structures have the least independent cross-checking, and ALOHA already
refuses to write the baryon-number-violating members of the same classes.

**Operators that act only through the input relations.** This is the subtlety I would attack if I
wanted to find a conceptual error rather than a coding one. The muon-decay operators
`Q_{l^2H^4D}^{(2)}` and `^{(4)}` have no vertex in any `p p > w+ w-` diagram, yet each contributes
-0.7164 pb, together a third of the whole dimension-eight interference, by shifting gw2, the vev and
M_W. The mechanism matters: a shifted coupling carries the `NP=2` order tag and MadGraph counts it,
while a shifted mass carries no tag at all. So the order counting is not a complete description of
where the dimension-eight dependence lives, and a process-specific model built by selecting
operators that have a vertex is incomplete in this scheme. `./dim8 select` lists such operators in a
group of their own, but the general question of what the untagged mass shift does is the sharpest
thing I know to ask, and it is measurable rather than rhetorical. With all 1030 coefficients at 1
and Lambda at 1 TeV the W mass comes out at 79.325 GeV against 79.824 in the Standard Model, a shift
of 0.625 per cent that falls exactly as 1/Lambda^4. The interference therefore does not scale
exactly as 1/Lambda^4 either, because the Standard Model half of it is evaluated at that shifted
mass. Measured, it does not: -3.998 +- 0.012 pb at 1 TeV against -0.2479 +- 0.0010 pb at 2 TeV,
where exact scaling would give -0.2499, a deviation of 0.79 per cent. Fitting sigma = A/Lambda^4 +
B/Lambda^8 to those two points gives B/A = 0.85 per cent at 1 TeV, the same size as the mass shift,
which is what the mechanism predicts with a sensitivity of order one. That fit then predicts 3 TeV
blind, and the measurement is -0.04891 +- 0.00014 pb against a prediction of -0.048947, agreeing at
0.27 sigma, while pure 1/Lambda^4 scaling from the 1 TeV point predicts -0.049358 and misses by 3.2
sigma. So the effect is real, it is the size the W mass shift says it should be, and a third point
confirms a fit made without it. I believe this is correct rather than a defect, because the input
scheme is defined at fixed G_F and a 1/Lambda^8 remainder is beyond the truncation, but it does mean
the coupling-order label is not a complete bookkeeping of the Lambda expansion in this model.
Disagreeing with that reading would be a real finding.

**The nine operators that vanish.** Seven of them contract two identical currents, symmetric in
their Lorentz indices, with an antisymmetric field strength, and two vanish by their SU(2)
structure. I claim this is a consequence of taking one flavour-universal coefficient per operator
and not a defect, and the argument is short enough to check independently in ten minutes. If any of
them should be nonzero the whole flavour-universal simplification is in question.

**Class 1 at high multiplicity.** `Q_{G^4}^{(4)}` and `Q_{G^4}^{(8)}` carry no seven- or
eight-gluon vertex in the shipped model. Nothing below seven external gluons can see it, so it
does not affect any realistic process, but it is a genuine hole rather than a physical zero.

**Conventions against an external implementation.** The bosonic classes 1 to 8 are compared with
SmeftFR's dimension-eight files vertex by vertex (`validate/smeftfr_by_class/`). That comparison
runs in unitary gauge with our covariant derivative on both sides, so it tests the operators as
written and not the derivative sign or the Goldstone sector. No cross section has been compared
against an independent dimension-eight implementation. The overlap with the Eboli and
Gonzalez-Garcia quartic-gauge operators is the obvious target, and a single matched cross section
would either close a convention question or open a real one.

## Traps that look like physics failures

`set Lam 1000` at the launch prompt does nothing at all and prints no error. MadGraph lowercases
parameter names, `lam` is already the Higgs quartic, and the card therefore calls the scale
`lam__2`. Use `set lam__2 1000` or `set dim8 0 1000`.

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

Flavour is universal, one coefficient per operator, so anything that needs a flavour structure is
outside the shipped model. The 60 baryon-number-violating operators are in the catalogue and not in
the model, because ALOHA cannot write their fermion-flow-violating four-point vertices. Dimension
six is in `models/dim68_is`, SMEFTsim's U(3)^5 sector on the same base (see [DIM6.md](DIM6.md)).
