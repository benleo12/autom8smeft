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
    set Lam 1000
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

The same Ward identities with the dimension-six sector on instead: the 66 coefficients of
block `DIM6` and the phases of the complex ones, thirty processes, at `NP<=1` and at `NP<=2`. In
both combined models the twenty-nine with an amplitude pass at `NP<=1` (`ve ve~ > a z` has none),
and at `NP<=2` all of them but `u u~ > t t~ g` and `u u~ > t t~ a`, which MadGraph 3.5.6 cannot
evaluate in this check (the header of `validate/mg5_gluon_check.sh` says why), the worst at 3e-12. And the two-point terms, which no
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

## Five things that are easy to get wrong, and how the model handles them

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
produced or exchanged. VBF di-Higgs has no W in its final state and the bracket is 5.9 per cent of
its cross section (every coefficient at 1, Lambda at 1 TeV, `ptj` = 25 GeV, `etaj` = 5, `mmjj` = 400 GeV), through the W mass in its two t-channel propagators. Since the `NP=0` row is
the cheapest one in any study, run it both ways rather than guess. In the {M_W, M_Z, G_F} scheme
the bracket is absent by construction.

**No coefficient whose vertices cancel ships.** Two structures of one vertex can each be nonzero
and cancel, when they carry couplings equal up to sign, and MadGraph then merges them into one
routine that ALOHA reduces to zero. A coefficient can also vanish as a whole. The twelve
four-fermion field-strength operators with two identical currents, those of `l^4B`, `q^4B`, `e^4B`,
`u^4B` and `d^4B`, are symmetric in the Lorentz indices of an antisymmetric field strength and
vanish once the currents are flavour diagonal, yet FeynRules writes some of them as pairs of structures
that differ by a swap of two dummy indices inside one `Epsilon` and carry the same coupling.
`validate/drop_zero_structures.py` groups the structures of every vertex by coupling, removes a group
whose sum vanishes, and sets to zero every coefficient whose whole contribution vanishes. A group can
span two vertices. FeynRules writes the vacuum piece of `Q_{G^2H^4}^{(1)}` on the four-gluon vertex
and the `d8fG` term that cancels it into two vertices with the same legs, with the colour spelled
`f(-1,1,3)*f(-1,2,4)` in one and `f(-1,1,3)*f(2,4,-1)` in the other, so the groups are formed over
every vertex with the same legs and the colours are compared in a canonical spelling. Left in, that
pair changes no amplitude, but it puts `c8G2H4x1` on `g g g g`, where it reads as a shift of
alpha_s. `tests/test_gluon_normalisation.py` fails on it. Every
vertex of the released models equals the vertex FeynRules wrote at a common random point with all
coefficients on, so nothing live is removed. With `Q_{q^4H^2}^{(5)}`, which vanishes with
flavour-diagonal currents as well, thirteen of the 674 have no vertex ("The thirteen operators
that vanish", below). `validate/zero_vertex.py --wcs` evaluates every
coefficient's vertices at one common point and finds no cancelling coefficient in a released model.

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
by counting duals gives -1.2 pb on `p p > w+ w-`, with its coefficients at one and `Lam` = 1 TeV. If you want to break something here, check the
derivation itself against your own C and P assignments for a class we have not quoted.

**No coupling reaches MadGraph's Fortran as a seven-digit decimal.** FeynRules writes a coupling
whose leading coefficient is a negative fraction as a decimal,
`-0.16666666666666666*(cw*complex(0,1)*g1SM)`, and every other coefficient as a fraction,
`(...)/6.`. Python reads the decimal as the nearest double, so every check that evaluates the UFO in
Python, the comparisons in `validate/` included, sees the right number. MadGraph's Fortran writer
prints the same literal as `-1.666667D-01`, and in the compiled matrix element the photon's
hypercharge coupling to the quark doublet is off by 2e-7. A cancellation that coupling takes part in
then fails by 2e-7 times the factor the cancellation suppresses the result by. In `u u~ > w+ w-` the
right-handed amplitude is the difference of the photon and Z exchanges, smaller than either by
M_Z^2/s, and the interference of `Q_{u^2W^2D}` with it came out high by 2.4e-5 at 1 TeV, 9.6e-5 at 2
TeV and 2.2e-4 at 3 TeV, growing like s. `Q_{u^2H^2D^3}^{(1)}` on the same amplitude moved the same
way, while `Q_{q^2W^2D}^{(1)}` on the left-handed one stayed at 1e-8. A comparison of compiled
matrix elements with the Matchete UFO found it, since that model writes its literals as integers.
`validate/exact_literals.py` writes each decimal as the fraction it is, `(1./6.)`, which Python
evaluates to the same double and MadGraph writes as an exact quotient. After it every ratio in that
check is a clean number to 4e-13. `examples/release_model.sh` calls it, and
`tests/test_exact_literals.py` fails if a shipped model holds a literal MadGraph would truncate. The
models released before 23 October 2026 held 2,306 to 2,313 such literals, all 1/3, 1/6, 1/12 or
1/24, and the rates in `examples/studies` were computed with them. Their smallest Monte Carlo error
is 1.1e-3, five times the largest shift above, so they stand. An amplitude that cancels more
strongly than this one, at a higher energy, would show more.

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
    DIM8_ROOT=$PWD wolframscript -file validate/check_bilinears.wls
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

**The thirteen operators that vanish.** Twelve of them contract two identical currents, symmetric
in their Lorentz indices, with an antisymmetric field strength, and `Q_{q^4H^2}^{(5)}` vanishes with
flavour-diagonal currents as well. Two more, `Q_{udWH^2}^{(1,2)}`, vanish as printed in the
Murphy basis whatever the flavour, since `\widetilde H^\dag \overleftrightarrow D^I H` sandwiches the
symmetric matrix epsilon tau^I between identical doublets. The Hilbert series counts two operators of
that field content, so the model encodes D^mu of the triplet bilinear, `D^\mu(\widetilde H^\dag \tau^I H)
W^I_{\mu\nu}` and its dual, which have vertices. I claim the thirteen are a consequence of taking one coefficient per operator with flavour-diagonal
currents, as both flavour modes of `gen/emit_fr.py` do, and not a defect, and the argument is short enough to check independently in ten minutes. If any of
them should be nonzero the whole one-coefficient simplification is in question.

**Class 1 at high multiplicity.** FeynRules exceeds 122 GB on the seven- and eight-gluon vertices of
the six `Q_{G^4}` operators with a dual field strength, so `validate/g4_highleg.py` writes them from
the operators as a sum over the assignments of the legs to the fields. `Q_{G^4}^{(2)}` has neither and
`Q_{G^4}^{(5)}` has no eight-gluon vertex, by the Jacobi identity. Break it by changing a sign or a factor
of the sum: `check` compares the sum with FeynRules at every number of gluons FeynRules reaches, on all
nine operators, and with the exact plane-wave coefficient of `validate/dualdual_highleg.py` at all of
them, and `ufo` repeats the second comparison on a written model.

**Conventions against an external implementation.** The bosonic classes 2 and 4 to 8 are compared
with SmeftFR's dimension-eight files vertex by vertex (`validate/smeftfr_by_class/`), 44 pairs and 851
vertices of the difference, none surviving. Each vertex of the difference is contracted at random
points, every free index with a dense random vector of its own and the arithmetic exact, three times
(`validate/fr_compare.wls`). An earlier version drew single values of the indices, which can miss a
sparse tensor, so a report older than 2026-11-01 means less than this one. The test stops if it fails any of
ten cases at load, among them a wrong relative sign, a colour tensor on six gluons and the Jacobi identity.
Break it by planting a wrong norm or a mismatched pair in a pair list. The X^4 operators of class 1 are
compared as polynomials in the field strengths (`validate/x4_polynomial.wls` and `.py`), which holds at
every number of legs, since FeynRules cannot reach the difference there. All 43 agree, and each differs
from the other 42, which must fail. Nine of them without a dual go through FeynRules as well
(`class1_nodual.m`). Class 3 is left out, as `validate/smeftfr_pairs.m` explains, since the two bases differ
there. All of this runs in unitary gauge with our covariant derivative on both sides, so it tests the
operators as written and not the derivative sign or the Goldstone sector. No cross section has been compared
against an independent dimension-eight implementation. The overlap with the Eboli and
Gonzalez-Garcia quartic-gauge operators is the obvious target, and a single matched cross section
would either close a convention question or open a real one.

**The powers of lambda.** `./dim8 select` prints beside each operator the power of lambda of its
leading tree, and `./dim8 series` writes the amplitude out topology by topology, in the energy
counting of arXiv:2504.10617, (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1). A power predicts
which operators grow fastest with energy. It is not a bound, and fitting an energy exponent to a
cross section does not test it. Chirality decides which trees count. A massless quark or lepton
keeps its chirality along a fermion line, since only its mass or its Yukawa coupling flips it, and
the counting keeps those of the top quark alone, a top mass insertion costing one power of lambda.
A photon or Z line between a right-handed current and a W-pair vertex of the Standard Model costs
two more powers, since a right-handed fermion couples to them through the hypercharge boson alone,
which has no W-pair vertex, so the two trees cancel up to M_Z^2/E^2. MadGraph's polarisation marks
name a channel: a W or Z marked `{0}` is counted by the equivalence theorem, as its Goldstone boson
at no cost or as the gauge boson at one power of lambda, and `{T}`, like no mark, is transverse.

The claim I would attack is the interference test of `./dim8 series`, because it is sharp. A term is
kept only where its tree gives the massless external quarks and leptons the chiralities of some
Standard Model tree, and is marked as interfering k powers down where the Standard Model trees with
those chiralities lie k powers above the leading ones (right-handed quarks in `u u~ > w+ w-` are two
powers down). So a class the series leaves out must give no interference once the light fermions
are massless. The model carries their masses (`MU` is 2.55 MeV in the card), so import it with the
card of the left-out class (`dim8_is-cls10` for
psi^2XH^3 in `u u~ > w+ w-`, say), generate `NP^2==2`, and set the masses and Yukawa couplings of the
light quarks, the b included, and of the leptons to zero in the param card (blocks `MASS` and
`YUKAWA`) before the run. MadGraph takes the same polarisation marks, so the test also runs channel
by channel. A nonzero rate is a term the series left out that interferes after all. The same holds
for an operator that
`./dim8 select` flags "only through the Yukawa coupling or the mass of a light quark or a lepton",
unless it also enters the input relations: with those couplings at zero it has no amplitude in the
process at all. The other place to look is the on-shell rule. A three-point vertex of two light
fermions that vanishes between massless spinors, or that is proportional to the square k^2 of its
boson's momentum, cancels a propagator and leaves a local term of the same power, so a wrong verdict
puts a term in the wrong topology or drops it. `validate/onshell_zero.py` decides each vertex
numerically and writes the verdicts to `build/onshell_zero.json`. The class to check by hand is
psi^2H^2D^3: its q qbar h vertex should vanish between massless spinors, and its q qbar Z vertex
should be k^2 times a remainder, since Q + Q^dag couples the Z to the total derivative of the quark
current.

**The dimension-six selection.** `./dim8 select --with-dim6` says which dimension-six coefficients can
change a process at 1/Lambda^4, and a complement of the selection cannot test that: couplings that
cancel between vertex objects leave diagrams that vanish, and a coefficient that enters only together
with a selected one does nothing while that one is zeroed. So
`validate/select_complement6.py "your process" --model models/dim68_mw` compares matrix elements. At
random coefficient values and phase-space points, in every subprocess, at `NP^2==1` and at `NP^2==2`,
|M|^2 with every dimension-six coefficient on must equal |M|^2 with only the kept ones on, to 1e-10. A
process where it does not is a coefficient the selector misses. `--drop cHW` on `p p > w+ w-` takes a kept
coefficient out and shows that the check can fail.

## Traps that look like physics failures

A restriction card is more than a list of what to keep. MadGraph evaluates the couplings at the
values of the card and fuses any two of one order that agree there up to sign, to about ten digits,
into one, which keeps the formula of the first at any values of the run, and it removes a coupling
that vanishes there with its vertices. A card written by hand with round numbers can do this and say
nothing: `cHbox` at 0.106 and `cee` at 0.159 fuse `-3 cHbox` on `H H H H` with `2 cee` on `e e mu mu`.
`validate/make_restriction.py` and `./dim8 select --card` write values with no such relation, so use
them, and `validate/make_restriction.py --renew <model>` gives those values to the cards of a model.

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

Diagram generation is what the full basis costs. Measured on `dim8_mw` with `NP^2==2` on a Mac mini:
`p p > w+ w-` is 452 diagrams and a 32-second session on the unrestricted model, but
`p p > h h j j QCD=0` is 268104 diagrams and a 2.2-hour session, of which 1.7 hours are the generate
step. Any restriction card cuts this, because MadGraph drops the couplings that vanish with it (for
example those proportional to the zero light-quark Yukawa couplings): with `dim8_mw-all`, which keeps
every operator, HHjj is 173928 diagrams in 47 minutes, and with the selector's card the same 173928
diagrams in 39 minutes. Restrict first.

Use Python 3.11. Python 3.12 generates events but disables reweighting and 3.13 breaks
`model_reader`.

## What is not here

Flavour is universal, one coefficient per operator, so anything that needs a flavour structure is
outside the shipped model. The 60 baryon-number-violating operators are in the catalogue and not in
the model, because ALOHA cannot write their fermion-flow-violating four-point vertices. Dimension
six is in `models/dim68_is`, SMEFTsim's U(3)^5 sector on the same base (see [DIM6.md](DIM6.md)).
