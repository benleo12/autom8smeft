# The dimension-six sector

The dimension-six operators in this model are SMEFTsim's, in the U(3)^5 flavour-symmetric
framework, put on our Standard Model base so that one model carries both sectors and MadGraph
counts powers of `1/Lambda^2` across them with a single coupling order. Cite arXiv:1709.06492 for
SMEFTsim and arXiv:2012.11343 for its flavour framework.

`gen/make_dim6.py` writes `tests/gen_smoke/dim6_smeftsim.fr` from SMEFTsim's own sources. It does
not retype any operator. What it does is declare the 90 coefficients our base does not already
have, at zero rather than SMEFTsim's default of one, connect three symbols to our side of the
model, and say what each operator is evaluated on: the corrected couplings and the canonical
fields of our input scheme, to first order, which is what makes the combined model complete and
gauge invariant at `1/Lambda^4` (see "What an operator is evaluated on" below). With the eight
coefficients the base already declares that is 81 in block `DIM6`, plus `Lam6` at index 1.

## Why this works at all

The field names agree. SMEFTsim and our base both descend from the FeynRules Standard Model, so
`Phi`, `QL`, `uR`, `dR`, `LL`, `lR`, `Wi`, `B`, `G` and the `SU2W`, `SU2D`, `Colour`, `Gluon`,
`Generation` index types are the same symbols on both sides, and SMEFTsim's operator expressions
evaluate against our fields unchanged. The SU(2) conventions need no translation either: both
declare `Ta[a,b,c] -> PauliSigma[a,b,c]/2` and `FSU2L[i,j,k] :> I Eps[i,j,k]`.

The input relations were already built for it. `tests/gen_smoke/base_inputscheme.fr` declares
eight dimension-six coefficients in block `DIM6` under SMEFTsim's own names, `cHW cHB cHWB cHDD
cHl3 cll1 cHbox cH`, because the `{alpha, M_Z, G_F}` relations need them, and it carries the
dimension-six **squared** terms as well, `cHl3^2`, `cHl3 cll1`, `cll1^2` and the rest, so the
scheme is complete to `1/Lambda^4` across both sectors. Those eight feed the operators and the
input relations from the same external parameter.

## The three connections

- `LambdaSMEFT` is our `Lam6`, the dimension-six scale, declared in block `DIM6` index 1 and
  separate from the dimension-eight `Lam`. Two scales, because nothing forces them equal.
- `vevhat` is our `vevSM`, which is `1/Sqrt[Sqrt[2] Gf]`. That is what SMEFTsim's `vevhat` is too.
- `redefCtoZero` is the name of SMEFTsim's truncation rule, which every operator definition ends
  in. Its content here is ours and is the subject of the next section but one.

## What is taken verbatim, and why that matters

Three things the operator file uses live in SMEFTsim's other files and are extracted from them
rather than retyped:

- `QLm`, the quark doublet **without** the CKM rotation. Our base has only `QL`, which carries CKM
  on its down component, so every operator SMEFTsim deliberately writes with `QLm` would otherwise
  pick up a CKM factor it should not have. Nothing errors out when this field is missing; the
  vertices are simply wrong, which is the worst of the three outcomes.
- `sigmaT`, which is `sigma^{mu nu} = i/2 [gamma^mu, gamma^nu]`. The same convention our own
  generator emits for the dimension-eight operators, so the two sectors agree on the sign.
- `HDH`, the Hermitian Higgs current `i H^dag D_mu H - i (D_mu H^dag) H`.

The generator also checks every symbol it defines against every name the base declares, and
aborts rather than warns. That check exists because one collision cost a day: SMEFTsim calls the
sum of its dimension-six terms `L6`, our base declares an internal **parameter** `L6 = 1/Lam6^2`
that the input relations are written in terms of, and SMEFTsim's definition landing on that symbol
made FeynRules ask for the options of a parameter that was actually a whole Lagrangian. The load
wedged for 25 hours at one percent CPU. The aggregates are now `LD6` and `LD6no4f`.

## What an operator is evaluated on

Our base brings the Lagrangian to canonical form through second order. It shifts `g`, `g'` and
the vev so that `alpha`, `M_Z` and `G_F` stay at their inputs, rotates the neutral gauge fields,
and rescales `W` and `h`. A dimension-six operator multiplied by one of those first-order
corrections is a `1/Lambda^4` term like any other, and the base's second-order relations were
derived assuming it is there: the `W` kinetic term, for one, is canonical at second order only if
the vacuum piece of `O_HW` is evaluated on the rescaled `W`.

So every operator is evaluated on

    gw -> gwSM (1 + gw1)        Z -> (1 + TZZ1) Z + TZA1 A        W -> (1 + rW1) W
    g1 -> g1SM (1 + g11)        A -> TAZ1 Z + (1 + TAA1) A        h -> (1 + rh1) h
    v  -> vevSM (1 + vev1)      G -> (1 + rG1) G,  gs -> gs (1 - rG1)

and products of two corrections, which are `1/Lambda^6` beside a dimension-six coefficient, are
dropped. `gen/make_dim6.py` writes the rule into the operator file and names the corrections in
`DIM6$FirstOrder`; `validate/fr_worker.wls` cuts every finished vertex at first order in that
list, where a coupling is an honest polynomial. The products come out as separate couplings of
order `NP=2`. **The `NP=1` vertices are SMEFTsim's and nothing else**, so they stay checkable
against SMEFTsim's own UFO, which was the reason for keeping its truncation in the first place.

`gen/make_dim6.py --linear` writes SMEFTsim's strict rule instead, no correction of any kind
inside an operator. A model built from it is gauge invariant at `1/Lambda^2` and must not be run
at `NP=2` with the coefficients of the input relations switched on, because the base's
second-order terms then have nothing to cancel against. `validate/check_bilinears.wls` measures
that directly: on the linear file seven of the twelve kinetic and mass terms it tests, among them
the kinetic terms of the `W`, the `Z`, the photon and the Higgs, are off their canonical values at
second order, and on the default file all twelve are canonical.

### What this replaced, and how it was found

Until 2026-10-05 the port was neither of the two. FeynRules applies a parameter `Definition` to
every term of a Lagrangian, so the operators received the shifted `gw` and `g1`, while the field
rotation is applied by the base to its own terms only. The combination `g W3 - g' B` inside an
operator then pointed slightly away from the `Z`, and the model had a photon coupled to
neutrinos at `cHl3 (g11 - gw1)`, a bare `g^{mu nu}` photon-Z-Higgs vertex from `cHDD`, and a
W-W-photon coupling that was not `e`, all at `1/Lambda^4`. The earlier text of this section
described the model as "linear in the vertices"; it was not, and nothing had tested the
difference, because the Ward checks switched on the dimension-eight coefficients only.
With the dimension-six ones on, `check lorentz` at `NP<=2` failed on seven of fourteen processes
(`u u~ > h a` at 1e-2, `e+ ve > w+ a` at 8e-3).

### The vev in the Yukawa spurion

One convention has to be stated because it only exists at second order. A U(3)^5 coefficient
multiplies a Yukawa matrix, `C_dH = cdH Y_d`. The matrix in the operators is `yd`, defined from
the mass and the uncorrected vev, `sqrt2 m_d/vevSM`, which is SMEFTsim's convention and an input
quantity. It is not the Lagrangian Yukawa `yd (1 + yr1)`. The two definitions of `cdH` differ by
a factor `1 + yr1`, a relabelling at `1/Lambda^4`.

## Building it

The dimension-six classes are cached as blocks, exactly like the 674 dimension-eight ones, so
nothing in the merge logic is special-cased:

    python3 gen/make_dim6.py                     # writes tests/gen_smoke/dim6_smeftsim.fr
    env DIM8_BASE="base_inputscheme.fr;dim6_smeftsim.fr" \
        DIM8_VDIR=~/dim8auto_build/vertices6 DIM8_HERM=0 \
        wolframscript -file validate/fr_worker.wls \
        L6cl1,L6cl2,L6cl3,L6cl4,L6cl5,L6cl6,L6cl7,L6cl8a,L6cl8b,L6cl8c,L6cl8d 0 674 2

About twenty minutes for 198 vertices, class 1 taking fifteen of them. The cache is keyed on the
block name alone, so **an operator file that has changed needs an empty cache directory**. Then
the combined UFO, with both caches and a list of the blocks that go in, the 674
baryon-number-conserving dimension-eight ones and the eleven above:

    env DIM8_BASE="base_inputscheme.fr;dim6_smeftsim.fr" \
        DIM8_VDIR="~/dim8auto_build/vertices;~/dim8auto_build/vertices6" \
        wolframscript -file validate/fr_writeufo.wls dim68_is blocks.txt

The dimension-six blocks live in their own cache directory on purpose, so that a plain
dimension-eight build cannot pick them up by accident. A block name found in two directories is a
hard abort, not a silent choice, and so is a file in either directory that does not hold a vertex
list. That second abort is new. A leftover `L6cl5.herm.mx`, the dump of a Hermiticity check, was
loaded as if it were a block on 2026-10-04, and the way the loop was written the next block,
`L6cl5`, then entered the model twice: three Yukawa operators at double strength, in a release
whose earlier builds had them right.

For a quick look at the dimension-six sector alone, give the writer the eleven names only. That
model takes twenty minutes rather than nine hours and is what the Ward checks below were first
run on.

## Orders

`NP` counts powers of `1/Lambda^2`, so a dimension-six insertion is one unit and a dimension-eight
insertion is two. MadGraph's `NP^2==n` constrains the sum over the two amplitudes:

| selection | what it is |
| --- | --- |
| `NP=0` | Standard Model |
| `NP^2==1` | dimension-six interference, `1/Lambda^2` |
| `NP^2==2` | dimension-six squared **and** dimension-eight interference, both `1/Lambda^4` |
| `NP^2==3` | dimension-six cubed and dim-6 x dim-8, `1/Lambda^6` |
| `NP^2==4` | dimension-eight squared and the rest of `1/Lambda^8` |
| `NP<=2` | everything up to one dimension-eight or two dimension-six insertions |

That `NP^2==2` mixes the dimension-six square with the dimension-eight interference is not a bug,
it is the power counting: both are `1/Lambda^4` and a consistent calculation at that order needs
both. To separate them, switch one sector off in the param card.

**But do not read the separate orders off the tagged bins without one correction.** MadGraph
tags couplings and not masses, and in this scheme `M_W` moves when a coefficient moves, which no
tag can express. (Until 2026-10-03 the vev, the Yukawas and the Higgs quartic were in the same
position. They are written as tagged sums now, and the `W` mass is the one quantity left.) On
`p p > w+ w-` the piece missing from the tagged dimension-eight interference measures
+1.40 +- 0.25 pb. Use `validate/order_fit.py`, which scans one coefficient with no `NP^2`
constraint and fits the polynomial:

    validate/order_fit.py dim68_is "p p > e+ e-" --coeff cHq1 --scale6 1000

The fit coefficients are the orders, no tag involved, and it fits one degree higher than asked so
the contamination beyond the truncation is reported rather than assumed away. With
`--compare-tagged` it runs the tagged bin as well and prints the difference, which is how the size
of the tagging defect gets measured instead of argued about. On `cHq1` in Drell-Yan, scanning to
`--delta 8`:

    sigma_0  (Standard Model)         862.366   +- 1.671
    sigma_1  (interference)             8.22263 +- 0.3084
    sigma_2  (square)                   3.5492  +- 0.01261
    sigma_3  (beyond the truncation)   -0.000728 +- 0.001438     8.4e-07 of the largest

    tagged NP^2==1 at cHq1 = 8:  59.25 +- 1.29 pb
    the fit says that order is:  65.78 +- 2.47 pb
    difference -6.53 pb, ten percent of the interference

The fit is exact but statistics-hungry, since it has to resolve the interference against the
whole cross section rather than integrating it alone, so scan wide rather than long: the tool
says so when the fitted term is under five sigma from zero.

These numbers were measured on the September build and have not been repeated on the rebuilt
model. An earlier version of this paragraph also read the tagged bin as "not even proportional to
the coefficient", from 6.544 pb at `cHq1 = 1` against 59.25 pb at eight, and blamed the mass
shifts. That reading does not survive: `cHq1` enters no input relation and shifts no mass, so the
tagged interference is exactly linear in it, and a 4 sigma departure from linearity between two
runs is MadGraph's error on an interference, which is underestimated when the integrand changes
sign. The comparison between the fit and the tagged bin stands as a measurement of that, not of
the model.

## What has been checked

Five things, in the order of what they can see.

**Gauge invariance, with the dimension-six coefficients on.** `validate/mg5_gluon_check.sh` with
`WARD_ON=dim6` switches on all 64 real coefficients of block `DIM6` and runs MadGraph's
`check lorentz` on the thirty processes of `validate/procs_dim6.txt`, eight gluonic, fifteen with
a photon and seven without a massless vector, at `WARD_ORDER="NP<=1"` and at `"NP<=2"`. The
released `dim68_is` passes sixty of sixty, the worst at 6e-14, and the seven electroweak
processes of `validate/procs_ew.txt` pass with `WARD_ON=both` as well. (The control run with the
coefficients off prints `Failed` for `ve ve~ > h a`. That process has no Standard Model
amplitude, and the verdict is the ratio of two numbers of order 1e-36.) The model it replaced
failed five of six gluonic processes at `NP<=1` and seven of fourteen electroweak processes at
`NP<=2`. This check did not exist before 2026-10-05: the Ward
checks switched on the dimension-eight coefficients alone, and both failures had been in the
released model since September.

**The two-point terms.** FeynRules computes no two-point vertex and MadGraph reads none, so a
kinetic or mass term that is off its canonical value at second order is invisible to everything
above unless a Ward identity happens to see it, which it does for the `W` and the gluon and not
for the `Z`, the photon-`Z` mixing or the Higgs. `validate/check_bilinears.wls` multiplies the
quadratic part of the Lagrangian, minus the canonical quadratic terms, by a spectator field at
rest, which turns every two-point term into a three-point vertex FeynRules will compute. With
nine coefficients on at `t`, `t/2` and `t/4`, all twelve kinetic and mass residues fall by eight
per halving, in both input schemes, so the quadratic Lagrangian is canonical through
`1/Lambda^4`. It found one thing: the base's second-order relation for the Higgs quartic had been
derived with the Higgs kinetic factor at the uncorrected vev while the rescaling of `h` used the
corrected one, which left the Higgs mass off its input by 2.3e-3 at the test point. One line of
the base changed (`gen/derive_higgs_yukawa.py`).

**The linear vertices against the validated build.** `validate/compare_dim6_linear.py` switches
on one dimension-six coefficient at a time and compares every `NP=1` coupling of two models,
vertex by vertex. Between the released model and the September release, the one the cross
sections below were measured on, 1143 of 1146 coefficient-vertex pairs agree to nine digits. The three
that do not are the three- and four-gluon vertices of `cHG`, which is the correction, and a
four-gluon term of `cHGtil` that vanishes by the Jacobi identity and that the new build no longer
writes. The same comparison against the build of 2026-10-04 found the three Yukawa operators at
twice their strength there (see "Building it"). One coefficient at a time matters: with several
on, the September model differs from the new one at the per-cent level, because it kept the
input shifts inside untagged parameters, and that is a second-order difference, not a linear one.

**The Fermi constant.** `G_F` is an input, so muon decay must not move when a coefficient is
switched on: the W-lepton vertices, the W mass and the four-lepton contact term change together
and cancel. At `1/Lambda^4` the cancellation needs the products of `O_Hl3` with the first-order
shifts, and it is a physical observable, which a Ward identity and a two-point term are not.
`validate/gf_closure.py` evaluates the matrix element of `mu- > e- ve~ vm` at a fixed
phase-space point with nine coefficients on at strength `t`, the W width set to zero:

    |M|^2/SM - 1          t = 1       1/2        1/4        1/8      per halving
    rebuilt sector      -2.4e-3    -2.7e-4    -3.3e-5    -4.0e-6     8.7  8.3  8.2
    the model replaced  -4.1e-2    -9.3e-3    -2.2e-3    -5.4e-4     4.4  4.2  4.1

Third order now, second order before, where the Fermi constant was off its input by 1.5% in the
amplitude at `cHl3 = 1`, `Lam6 = 1 TeV`, which is the product `2 vev1 x cHl3 v^2/Lam6^2` missing
from each W-lepton vertex. The width has to be off because a width that stays fixed while `M_W`
moves leaves a first-order term of relative size `Gamma_W^2/M_W^2 = 7e-4` times the shift of
`M_W^2`. That term is real, and worth knowing about in a scheme where `M_W` is derived.

**Cross sections against SMEFTsim's own UFO**, coefficient by coefficient, with every shared
Standard Model input matched. `scratchpad/dim6check/matrix2.sh` does that and
`scratchpad/dim6check/summarise.py` reads the verdicts back out of the param cards the runs
actually used. These are September's numbers; the vertices they test are the ones the previous
paragraph shows unchanged.

| coefficient | process | ours [pb] | SMEFTsim [pb] | agreement |
| --- | --- | --- | --- | --- |
| `cHG` | `g g > h` | 5870 +- 7.6 | 5870 +- 7.5 | exact |
| `cG` | `p p > t t~` | -38.75 +- 0.084 | -38.76 +- 0.077 | 0.09 sigma, 0.03% |
| `cW` | `p p > w+ w-` | -0.2369 +- 0.0022 | -0.2375 +- 0.0021 | 0.20 sigma, 0.25% |
| `cHq1` | `p p > e+ e-` | 6.544 +- 0.114 | 6.639 +- 0.124 | 0.57 sigma, 1.43% |
| `clq1` | `p p > e+ e-` | -1.264 +- 0.017 | -1.259 +- 0.019 | 0.19 sigma, 0.40% |
| `cqe` | `p p > e+ e-` | -1.148 +- 0.012 | -1.174 +- 0.014 | 1.42 sigma, 2.21% |
| `cHu` | `p p > e+ e-` | 15.15 +- 0.027 | 15.13 +- 0.027 | 0.52 sigma, 0.13% |
| `cuGAbs` | `p p > t t~` | -151.4 +- 0.170 | -151.5 +- 0.164 | 0.42 sigma, 0.07% |

Seven independent comparisons, worst 1.42 sigma, which is what seven draws look like.

`g g > h` is the one comparison that needs no matching at all: the tree-level Standard Model has
no `Hgg` vertex, so the whole cross section is the `cHG` operator and it depends on `alpha_s`,
`m_h` and `cHG/Lambda^2` and on nothing electroweak.

For the rest the schemes differ, ours being `{alpha, M_Z, G_F}` with `M_W` derived and the shipped
SMEFTsim U(3)^5 UFO being the `m_W` scheme with `alpha` derived. They are the same LO relation
solved in opposite directions, so SMEFTsim is given the `M_W` our model derives, 79.82435975 GeV,
and its derived `alpha` then equals our input `alpha`. CKM is set to the identity in both, the two
parametrising it differently with no single value making both matrices equal.

Everything else shared is matched from a list computed off the two UFOs rather than written by
hand, because hand lists kept missing things. **Of the 26 external parameters the two models
share, fourteen differ by default**: `G_F`, `M_B`, `M_D`, `M_H`, `M_S`, `M_T`, `M_U`, the top
width, `alpha_s`, and the `ymb`, `ymdo`, `yms`, `ymt`, `ymup` Yukawas. Matching only `M_W`, `M_Z`,
`G_F` and `alpha_s` put `cG` 1.7 sigma out and `cW` 2.5 sigma out, which is what a 0.44 percent
top mass does to `t t~`. Adding the masses and widths but not the Yukawas left `cuG` at 2.97 sigma
and 0.46 percent low, since the chromomagnetic interference is proportional to the top Yukawa and
`ymt` was 172.00 here against 172.76 there; with `ymt` matched it is 0.42 sigma and 0.07 percent.
`alpha_s` is the one exception, excluded rather than matched: MadGraph annotates that card entry
"not used if you use a pdf set" and both runs take it from the same nn23lo1 set.

The eight coefficients that enter our input relations, `cHW cHB cHWB cHDD cHl3 cll1 cHbox cH`,
are not compared this way. They shift `M_W` in our scheme and `alpha` in theirs, so it is not
like for like.

Two more checks on the sector as a whole. All eleven classes pass `CheckHermiticity` with a zero
residual. And the Standard Model limit of the combined model, every coefficient at zero, is
bit-identical to the dimension-eight-only model on `p p > e+ e-` (863.1 pb) and `p p > t t~`
(575.0 pb), and agrees with MadGraph's own `sm` to 0.13 sigma.

## One thing to know before running anything

Invoke MadGraph through **python3.11**. From Python 3.13 the `locals()` snapshot of PEP 667 breaks
`model_reader`, and every restricted model then fails to import with `Unable to evaluate mdl_L6 =
mdl_Lam6**(-2): name 'mdl_Lam6' is not defined`. That looks exactly like a broken restriction card
and is not one.

## The class-5 Yukawa operators: the mass basis, and how it is reached

The class-5 operators are `C_fH (H^dag H)(fbar_L f_R H)/Lam^2`, and they are the one place where
a dimension-six coefficient can move a fermion mass off its input value. This model subtracts the
vev so that it does not, which puts it in the same basis as SMEFTsim. The section records the
check, because the question comes up whenever someone compares coefficient values across models.

**The test.** Read the operator's one-, two- and three-Higgs vertices out of a UFO. In units of
`C y_f/(2 sqrt2 Lam6^2)`, with MadGraph's `n!` for identical legs, they are

    operator as written (Yukawa basis):   h 3,  hh 6,  hhh 6
    vev-subtracted     (mass basis):      h 2,  hh 6,  hhh 6

Only the single-Higgs entry moves, which is what makes the other two the control. The operator
now built here gives 2, 6, 6, and so does SMEFTsim. On `b b~ > h`, which is that vertex and
nothing else, the two cross sections agree; before the subtraction ours was larger by exactly 3/2.

**What the subtraction does.** Writing the operator as `(H^dag H - vhat^2/2)(fbar_L f_R H)` removes
`v^2 (v+h)` from `(v+h)^3` and leaves `2 v^2 h + 3 v h^2 + h^3`. The constant term is gone
entirely, so the fermion mass is `y_f v/sqrt2` with no `C_fH` in it, and the whole effect of the
operator sits in the vertices where it can be measured.

**SMEFTsim reaches the same place by the other route.** It keeps the operator unsubtracted and
compensates in the Yukawa instead. `SMEFTsim_A_parameters.fr` defines the Yukawa that enters its
Standard Model Lagrangian as

    yd0[i,j] -> yd[i,j] (1 - dGf/Sqrt[2]) + vevhat^2/2/LambdaSMEFT^2 Conjugate[cdH] yd[j,i]

The single-Higgs coefficient is then `-y/sqrt2 - C y v^2/(2 sqrt2 Lam^2) + 3 C y v^2/(2 sqrt2 Lam^2)`,
whose Wilson-coefficient part is `2 v^2` in the units above, and the mass comes back to its input
by construction. The two routes are algebraically identical in all three vertices and in the mass,
so a coefficient means the same thing in the two models and the values can be compared directly.

**Why the Yukawa route was the wrong one to take here, and why an earlier attempt at it failed.**
It matters *which* Yukawa symbol is shifted. SMEFTsim has two, `yd0` in the Standard Model term
and `yd` inside the operator, and shifts only the first. This model has one symbol serving both,
because its class-5 operators carry `Conjugate[yd[ff2,ff1]]` as an explicit factor, so a shift
there scales the operator term and the Standard Model term together and leaves their ratio alone.
That is exactly what two earlier attempts measured, an additive shift sending `cdH` from a factor
100 too small to a factor 13 too large and the multiplicative one moving it by 3% with the 3/2
untouched. Subtracting the vev needs no second symbol, stays exactly linear in `C`, and gets the
conjugation right for a complex coefficient on its own, since the operator and its Hermitian
conjugate are generated together by `HC[L6cl50]`.

**Consistency with dimension eight.** The dimension-eight class-12 operators are compensated in
the Yukawa term of the base, which is written `y_f (1 + yr1 + yr2) + c8fH5 vevSM^4/(4 Lam^4)`
with `y_f = sqrt2 m_f/vevSM`, and are therefore mass-basis. With the subtraction the
dimension-six sector is mass-basis too, so one convention holds across the whole model and a
fermion mass is an input everywhere. At second order the subtraction is of the corrected vev,
`vevSM (1 + vev1)`, the one the doublet carries, so the mass stays at its input at `1/Lambda^4`
as well.

**Why the spot check missed this.** The eight-coefficient comparison contained no class-5 operator
at all. The sweep over all sixty-four is what surfaced it, and `b b~ > h` rather than
`p p > b b~` is what made it legible: on the latter the effect is 5 pb on a 58000 pb cross
section and everything else in the model is in the way.

## O_HG: the same subtraction, for the gluon

`O_HG = (H^dag H) G G` has a vacuum piece too, `v^2/2 G G`, and it is a correction to the gluon
kinetic term. SMEFTsim removes it by rescaling the gluon field and the strong coupling in opposite
directions, which leaves `g_s G`, and with it every interaction, where it was. Our base does no
such rescaling, and until 2026-10-05 the operator was taken as the Warsaw basis writes it. The
vacuum piece then stayed in the three- and four-gluon vertices and nowhere else, so with `cHG`
switched on the gluon coupled to itself with a strength 1.8% away from the one it couples to
quarks with (at `cHG = 0.15`, `Lam6 = 1 TeV`), and `check lorentz` failed at `1/Lambda^2`:

    u u~ > g g      1.0e-2        g g > t t~       5.2e-3
    g g > g g       3.8e-4        u u~ > t t~ g    2.1e-3
    g g > g g g     8.8e-4        g g > h g        passes

`g g > h g` passes because the Higgs vertices are the part of the operator that was right, and
that is also why the comparison with SMEFTsim on `g g > h`, exact to four digits, said nothing.

The operator is now `(H^dag H - v^2/2) G G`, which is the rescaling carried out: `-1/4 (1 - x) G G`
with `x = 2 cHG v^2/Lam6^2` is canonical in `G' = Sqrt[1 - x] G` with `g' = g_s/Sqrt[1 - x]`, and
what is left of the operator is `cHG (H^dag H - v^2/2) G' G'/(1 - x)`. The factor `1/(1 - x)` is a
product of two coefficients and enters at second order through `rG1 = cHG vevSM^2/Lam6^2`, the
gluon's entry in the table of "What an operator is evaluated on". After the change all six
processes pass at 1e-14, and SMEFTsim's own model has no `cHG` in the pure-gluon vertices either.

The factor `1/(1 - x)` is gauge invariant on its own and leaves the two-point terms alone, so
neither the Ward checks nor `check_bilinears.wls` can tell whether it is there. A cross section
can. With `cHG` alone switched on, the amplitude of `g g > h` is its linear value times
`1/(1 - x)`, so the cross section at order `cHG^3` must be `2x = 4 cHG v^2/Lam6^2` times the one
at order `cHG^2`, which is 0.24250 at `cHG = 1`, `Lam6 = 1 TeV`:

    g g > h  NP<=1 NP^2==2     5883 +- 6.4 pb
    g g > h  NP<=2 NP^2==3     1427 +- 1.6 pb        ratio 0.2426

on one seed, so the errors are correlated and the ratio is good to better than they suggest.

## The coefficients no cross section can test, and how they were tested anyway

Five dimension-six coefficients have no tree-level probe in proton collisions. `cH` modifies the
Higgs potential only, `ceH` needs a Higgs radiated off an electron line, and `cll`, `cee`, `cle`
are four-lepton contact terms. The sweep reports them as untested rather than pretending, which
is right, but they are not beyond reach: switch the coefficient on, evaluate the UFO's parameters
and couplings numerically, and read what it did to the vertices. No phase space, no Monte Carlo,
no statistical error. `cH`, `cll`, `cee` and `cle` agree with SMEFTsim to one part in 10^15, which
is machine precision, and `ceH` is the lepton half of the class-5 fix above.

Two traps in doing this, both of which produced a convincing false alarm before being caught.

The first is summing `|coupling|` over a vertex's entries. Where a model keeps the operator's
contribution and the input-scheme compensation as two separate entries on one vertex, `|a| + |b|`
turns their cancellation into an addition. On the Higgs self-coupling that reads as `15 + 9 = 24`
against the true `|-15 + 9| = 6`, so `cH` appears to be out by a factor of four and `hhhh` by
exactly 3/2, with `h^5` and `h^6` agreeing because nothing cancels there. Sum the couplings
SIGNED. The second is then keying on the colour and Lorentz structure, which is too strict: the
two models order their Dirac structures differently, so identical physics shows up as every
four-fermion entry differing. Key on the particle content and sum.

There is a third, and it is the subtlest. The two models do not use the same Dirac decomposition
for a scalar-fermion vertex. SMEFTsim writes `e+ e- h` on `Identity(2,1)` and `Gamma5(2,1)`,
this model writes it on `ProjP` and `ProjM`. Since

    a ProjM + b ProjP = (a+b)/2 Identity + (b-a)/2 Gamma5

a pair of bare projectors each carrying `g` IS one `Identity` carrying `g`, so adding the raw
entries reports `2g` against their `g` and `ceH` looks like it is out by exactly a factor of two
on all nine of its vertices at once. A uniform factor across every vertex of one coefficient,
with the ratios between `h`, `hh` and `hhh` all correct, is the signature: it is a normalisation
or a decomposition, not a basis. Weight a bare projector by one half. Structures that pair a
projector with `Gamma(...)` are the four-fermion ones, where the two models already agree on the
decomposition, and they keep weight one.

## Why this model does not agree with SMEFTsim to all orders, and should not

Six coefficients move `M_W` in our `{alpha, M_Z, G_F}` scheme and `alpha` in SMEFTsim's
`{M_W, M_Z, G_F}` one, so the shipped sweep marks them not comparable. SMEFTsim also ships an
alpha-scheme UFO, which is our scheme exactly, and against that they can be compared. At
`c = 1` and `Lam = 1 TeV` they differ by 0.65 to 6 percent on `p p > h z`. That is not a defect,
and the way to see it is to lower `c`:

    cHbox, relative deviation      c = 1      0.127
                                   c = 0.1    0.0122
                                   c = 0.01   0.00121

which is exactly linear in `c`, so the disagreement is O(c) RELATIVE and the linear term itself
agrees. It is this model's `1/Lam^4` input-scheme correction, which SMEFTsim does not have
because it truncates at `1/Lam^2`. Keeping it is the point of a dimension-eight model.

Do not reach for the odd part in `c` to settle this. `(sigma(+c) - sigma(-c))/2` removes the even
orders and so removes MadGraph's mass-tagging artefact, which is real and is described below, but
it does NOT remove this, and the disagreement survives it almost unchanged.

For scale, SMEFTsim's own two UFOs differ from each other by a median of 21 percent on `cHWB`'s
vertices, while this model sits within 0.1 percent of its alpha-scheme one. We agree with
SMEFTsim better than SMEFTsim agrees with itself across its own two schemes.

## Traps

**MadGraph constrains only what you write, and this one invalidated three rows.** `NP^2==1` pins
the dimension-six order and leaves the QCD and QED hierarchy to MadGraph's automatic resolution,
which lands differently in two models with different vertex content. Unpinned, the SM limits of
three processes disagreed between this model and SMEFTsim by 0.73% (`p p > w+ w-`), 1.29%
(`p p > h z`) and 4.78% (`p p > t t~ h`), before any Wilson coefficient was switched on. The
symptom was `cuH` reporting 8.87 sigma at 60000 events while its vertices were bit-identical to
SMEFTsim's, a contradiction that had to be one or the other. Pinning the orders brought that row
to 0.61%.

Diagram COUNT is not the diagnostic, and it is worth saying so because it is the first thing you
reach for. All twelve processes in the sweep have different counts in the two models, SMEFTsim
having roughly two to three times more, because it has more vertices and the surplus diagrams
carry zero couplings. Yet `b b~ > h` at 4 diagrams against 7 agrees to 0.00 sigma, and
`g g > h` at 1 against 2 agrees to 0.00%. The diagnostic that means something is the SM limit
of the process, `NP=0`, under the exact specification being used.

Choosing the pinning needs both of two conditions and they pull in opposite directions:

    (1) the SM limit must agree between the two models UNDER THE EXACT SPEC USED
    (2) the interference must come out nonzero in BOTH models

Too loose and extra SM orders creep in that the two models resolve differently, breaking (1).
Too tight and an operator vertex is excluded wherever that model counts its QED order higher,
breaking (2): with `QED=2` pinned, SMEFTsim's `cW` cross section came back as a flat zero,
"Survey return zero cross section", while ours was fine. So there is no single rule. The
specifications this sweep settled on, each measured rather than reasoned:

    p p > w+ w-    QED<=4 QCD=0    a BOUND, because QED=2 zeroes SMEFTsim's cW
    p p > h z      QED=2  QCD=0    an EQUALITY, because QED<=4 breaks the SM limit to 1.29%
    p p > t t~ h   QCD=2  QED=1    an EQUALITY, because QED<=3 breaks the SM limit to 0.73%

The other four processes carrying a tree-level SM amplitude need no pinning: their SM limits
already agree at 0.05% (`p p > e+ e-`), 0.21% (`p p > t t~`), 0.02% (`p p > e+ ve`) and 0.00%
(`b b~ > h`). Check, do not assume, and check under the spec you are actually going to run.


A complex coefficient is an internal parameter built from `<name>Abs` and `<name>Ph`, so
`set cuG 1.0` is not a thing: set `cuGAbs`. MadGraph only WARNS on a `set` it does not understand,
so read the value back out of the param card rather than trusting the command.

The shipped SMEFTsim UFO parametrises its complex coefficients differently, as `<name>Re` and
`<name>Im`, because it was generated from a later SMEFTsim than the 2018 U(3)^5 FeynRules files
this port is built on. The operators are the same; only the two real numbers standing for one
complex coefficient are chosen differently. With the phase at zero `cuGAbs` here is `cuGRe`
there, which is how the two are compared.
