# Running an analysis

From a process to cross sections. Needs MadGraph5_aMC@NLO 3.5 and Python 3.11.

## 1. Install

    ln -s /path/to/autom8smeft/models/dim8_mw   /path/to/MG5_aMC/models/dim8_mw
    ln -s /path/to/autom8smeft/models/dim8_is   /path/to/MG5_aMC/models/dim8_is
    ln -s /path/to/autom8smeft/models/dim68_mw  /path/to/MG5_aMC/models/dim68_mw
    ln -s /path/to/autom8smeft/models/dim68_is  /path/to/MG5_aMC/models/dim68_is

`dim8_mw` and `dim8_is` carry the dimension-eight sector alone, in the {MW, MZ, GF} and the
{alpha, MZ, GF} scheme, and so generate far fewer diagrams. `dim68_mw` and `dim68_is` carry both
sectors, in the same two schemes. Everything below works with any of them. The selector and the study
driver default to `dim8_mw`, and an example that names `dim8_is` quotes that model's numbers. The
study driver of section 4 finds MadGraph through `MG5_DIR`:

    export MG5_DIR=/path/to/MG5_aMC

## 2. Which operators enter

    ./dim8 select "u c > u c h" --model models/dim8_is
    ./dim8 select "u c > u c h" --model models/dim8_is --card vbfh

prints the operators with a tree-level vertex in that process, by class and with the vertex of
each one's leading tree, and then a second group: the operators with no vertex in the process that
still move its prediction because they enter the {alpha, MZ, GF} relations (c8B2H4x1, c8H6x1,
c8H6x2, c8W2H4x1, c8W2H4x3, c8WBH4x1, c8l2H4Dx2, c8l2H4Dx4, c8l4H2x1, c8l2e2H2x1 and c8l2e2H2x2
are the eleven that can, the last two only with the electron and muon Yukawas on). On
p p > w+ w- six of them have no vertex in any diagram, in either scheme, and with the lepton
Yukawas off three of those six move it, all through muon decay: c8l2H4Dx2, c8l2H4Dx4 and, with
the opposite sign, c8l4H2x1. With every coefficient at 1, c8l2H4Dx2 and c8l2H4Dx4 carry 46 per
cent of the 1/Lambda^4 cross section of section 4 in `dim8_is`, where the shift of the W mass is
part of it (40 per cent of the `NP^2==2` row alone), and 48 per cent in `dim8_mw`. The two groups
together are complete at tree level with one insertion.

`--card NAME` writes `restrict_NAME.dat` into the model that `--model` names (`models/dim8_mw`, the
{MW, MZ, GF} scheme, without the option), keeping both groups, and `import model dim8_is-NAME`
applies it. Nothing is rebuilt at this step: FeynRules has already been run, the shipped model
carries all its operators, and MadGraph drops the zeroed coefficients and the vertices
whose couplings vanish at import. With `--model models/dim68_is` the selector lists the
dimension-six coefficients as well, one by one under their Warsaw classes, from the vertices of each
coefficient in `build/dim6_index.json`, which `python3 validate/dim6_index.py` writes from the
released models. The vertices of a coefficient include the Standard Model vertices it rescales, as
C_HBox rescales h W W, h Z Z and the Yukawa couplings through the normalisation of the Higgs field,
and such a vertex counts at the power of the Standard Model vertex and four more, v^2/Lambda^2. A
coefficient with no vertex in a tree of the process can still enter at 1/Lambda^4 where the Standard
Model has a tree, through a tree with a second dimension-six vertex or through a vertex at `NP=2`
that multiplies it by a second coefficient or by itself, and is flagged "only with a second
dimension-six insertion, of this coefficient or another". In g g > t t~, whose Standard Model trees
the input relations do not shift, C_Hl^(3) and C_ll' still enter that way, since their shift of the
vev multiplies the chromomagnetic vertex of C_uG. The dimension-six coefficients are zeroed in the
card unless you add `--with-dim6`, as in the class cards. With it the card keeps exactly the
dimension-six coefficients listed, those of the input relations included. A model without a
dimension-six sector of its own, `dim8_mw` or `dim8_is`, refuses the option, since it fixes the
dimension-six coefficients of its input relations at zero: set alone they would be half a calculation.
The kept coefficients carry placeholder values until the param card sets them (section 4).
`validate/select_complement.py "p p > w+ w-"` checks the dimension-eight selection with MadGraph as
the judge: a card keeping the complement of the selection generates no diagram. It does not check
the dimension-six selection, since a coefficient whose couplings cancel between vertex objects, as
the gauge vertices of C_HW cancel against the rescaling of the W field, keeps those couplings in a
restricted model, where MadGraph would draw diagrams that vanish.
`validate/select_complement6.py "p p > w+ w-" --model models/dim68_mw` checks that one by matrix
elements: at random coefficient values and phase-space points, in every subprocess, at `NP^2==1` and at
`NP^2==2`, |M|^2 with every dimension-six coefficient on must equal |M|^2 with only the kept ones on. Do not compare
diagram COUNTS between the full and a restricted model instead: MadGraph drops from a restricted model
every vertex whose couplings evaluate to zero with the card (the u-b-W vertex with the
Cabibbo-only CKM, for one), and keeps such vertices, and their vanishing diagrams, in the full model.

The power of lambda beside each operator of the first group is that of its leading tree, in the
energy counting of arXiv:2504.10617, (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1). A Standard
Model three-point vertex counts lambda^-2 with a momentum or a fermion pair and lambda^-1 with a vev,
a four-point vertex lambda^0, a propagator lambda^4, and a vertex of an operator of mass dimension d
with m legs and p Higgs fields set to the vev lambda^(d-12+2m+p). The header gives the power of the
Standard Model amplitude in the channel the powers are counted in, an unmarked W or Z being
transverse: lambda^0 in p p > w+ w-, and lambda^1 in u u~ > z h, whose unpolarised amplitude is
lambda^0 through the longitudinal Z. No Standard Model tree of n external particles lies below
lambda^(2n-8), and a smaller power is a larger contribution in the tails. The second group multiplies the
Standard Model amplitude by v^4/Lambda^4 and sits eight powers above it (four for the dimension-six
coefficients of `dim68_is`, by v^2/Lambda^2). The power predicts which operators grow fastest in
the tails, E >> v. It says nothing about the inclusive rate, nor about whether the operator
interferes with the Standard Model, which `./dim8 series` answers below.

Chirality decides which trees count. A massless quark or lepton keeps its chirality along a fermion
line, since only its mass or its Yukawa coupling flips it, and the counting keeps those of the top
quark alone, a top mass insertion costing one power of lambda (m_t ~ v stands where pslash ~ E
would). A tree that needs a light fermion, the b quark included, to flip is therefore not counted,
and an operator that reaches the process only that way is printed with the remark "only through the
Yukawa coupling or the mass of a light quark or a lepton". A right-handed quark or lepton couples to
the photon and the Z through the hypercharge boson alone, which has no vertex with a W pair, so a
photon or Z line between a right-handed current and the W-pair vertices of the Standard Model costs
two more powers of lambda: there the photon and Z trees cancel up to M_Z^2/E^2. The dimension-six
sector of `dim68_is` follows SMEFTsim's U(3)^5 framework, in which an operator whose fermion
bilinear joins two different fields carries a Yukawa matrix, so its dipoles and Yukawa-like
operators count for the top quark alone and its scalar four-fermion operators not at all.
`examples/14_which_operators.md` gives the selector's other remarks.

MadGraph's polarisation marks on a W or a Z name a channel, as in
`./dim8 select "u u~ > w+{0} w-{T}"`. `{T}`, like no mark, is transverse. `{0}` is longitudinal and
is counted by the equivalence theorem: its Goldstone boson takes its place at no cost, or it keeps
its gauge leg, whose polarisation vector is of order M_W/E and costs one power of lambda. The header
then gives the Standard Model amplitude of the channel, found the same way, which can lie above
lambda^(2n-8), as W_L W_T does at lambda^1. The selection, and with it the card, is that of the
unpolarised process. A `{0}` mark needs the Feynman-gauge vertex lists, `build/vertex_index_fg.json`
and `build/sm_vertices_fg.json`, which are made in Feynman gauge with Mathematica and FeynRules and
ship in `build/` with the release. Without them the selector prints the operators and writes the
card with no powers, and says why. The dimension-six coefficients of `dim68_is` are printed with no
powers in every `{0}` channel, with those lists or without them, and a note says why: their vertices
come from `build/dim6_index.json`, which is read from the unitary-gauge model and holds no Goldstone
vertex. MadGraph's helicity marks `{L}` and `{R}` are refused, since the counting does not tell them
apart from `{T}`.

    ./dim8 series "u u~ > w+ w-"

writes the same counting out topology by topology. For the s channel, the t channel (with the u
channel merged into it, as for any quark-antiquark initial state) and the contact terms it gives
the smallest power of every class, with the products of Standard Model couplings that reach it,
beside the Standard Model's own terms. A term is kept only where it can interfere with the Standard
Model, that is, where its tree gives the massless external quarks and leptons the chiralities of a
Standard Model tree, since amplitudes of different helicities do not interfere. Where the Standard
Model trees with those chiralities lie k powers of lambda above the leading ones, the term
interferes k powers down and is marked so: right-handed quarks in u u~ > w+ w- are two powers down,
since their photon and Z trees cancel up to M_Z^2/E^2. An external top quark of the other chirality
costs m_t/E, and the term is marked so too. The classes left out are listed at the end. A star marks
a dimension-eight term at most four powers of lambda above the Standard Model, which grows at least
as E^4/Lambda^4 relative to it. The command takes the same marks, `--latex` writes the series as an
align block and `--vbf` gives vector-boson fusion in the effective-W approximation. Without the
Feynman-gauge lists it counts with the unitary-gauge ones,
and without `build/onshell_zero.json`, which `python3 validate/onshell_zero.py` writes, it counts a
three-point vertex of two light fermions even where that vertex vanishes on shell. The output says
so in both cases.

The series is that of one model, `--model` as for the selector, `dim68_mw` unless another is given,
and it uses the operators of that model's basis and the vertices of its input scheme. Its last lines
name the operators of the input relations of the scheme, which shift every Standard Model term by
v^4/Lambda^4 at dimension eight and v^2/Lambda^2 at dimension six, and so have no topology of their
own. The two bases differ in class 11, psi^2H^2D^3. In the default basis every Higgs field of these
operators carries a derivative and none of their vertices has fewer than four fields, while in the
Murphy basis (`dim68_mw_murphy`) they have three-point vertices with a q qbar Z vertex proportional to
k^2, which give terms in the s channel as well. The command checks the vertex lists against the
couplings of the model before it counts, and stops when the model was written from another version
of `gen/operators.py`, carries an operator the lists do not hold, or carries the class-11 operators
of one basis while its name says the other.

To test what the series leaves out, import the model with the card of a class it leaves out (a
chirality-flipping class such as psi^2XH^3, `dim8_is-cls10`, in `u u~ > w+ w-`) and generate
`NP^2==2` with the masses and Yukawa couplings of the light quarks and leptons set to zero in the
param card. The interference must vanish. [HOW_TO_BREAK_IT.md](HOW_TO_BREAK_IT.md) has the other
ways to attack the counting.

## 3. Set up a study

A directory with two or three text files.

`processes.txt`, one MadGraph process per line. Run-card settings after a `|`, and after a second
`|` an optional restriction card for that process's full-model rows:

    p p > w+ w-
    p p > e+ e- | mmll=200
    p p > h h j j QCD=0 | ptj=20 mmjj=500 | bosonic

Restrict heavy processes. `p p > h h j j QCD=0 NP^2==2` on the unrestricted `dim8_mw` is 525156
diagrams, 3539 core-minutes of generation, and 9540 diagrams in a 31-minute session
with the card `./dim8 select` writes for it. A card costs time at import (44 minutes for
`dim8_mw-all`), so a light process such as `p p > w+ w-` is faster unrestricted.

`classes.txt`, one restriction card per line:

    cls14
    cls15
    cls18

29 cards ship with `dim8_is`, one per class plus `bosonic`, `cpeven`, `cpodd`, `all`, `ten`,
`only_q2H4D`, `only_W2H2D2`, `l2H4D24`. `cpeven` and `cpodd` use the derived C x P parity of
`gen/cp_parity.py`, which is not the same as counting dual field strengths: see the README. Any
other selection, by operator name, coefficient, block number or class:

    validate/make_restriction.py models/dim8_is mine Q_{q^2W^2D}^{(1)} c8q2WH2Dx1 cls:18

`coefficients.txt`, optional, `NAME=VALUE` per line. Default is every dimension-eight coefficient
at 1 with `Lam` at 1000 GeV.

## 4. Run

    MG5_DIR=/path/to/MG5_aMC DIM8_CORES=2 \
        examples/studies/run_study.sh mystudy models/dim8_is 5000

Cross sections append to `mystudy/results.tsv`, event files to `mystudy/lhe/`, and the record of
each cross section to `mystudy/records.tsv` (section 5). `DIM8_RUNS` sets
where process directories go, `DIM8_CORES` caps cores, `DIM8_NEV_SQ` caps events for the squared
rows.

Rows per process:

| row | order |
|---|---|
| `NP=0` | Standard Model, coefficients off |
| `NP=0 on` | same amplitude, coefficients on |
| `NP^2==2` | interference, 1/Lambda^4 |
| `NP<=2 NP^2==4` | square, 1/Lambda^8 |

`NP=0 on` is not a duplicate. MadGraph tags couplings, not masses, and the W mass shifts with the
coefficients, so part of the 1/Lambda^4 term sits in the `NP=0` bin:

    sigma(1/Lambda^4) = sigma(NP^2==2) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]

On `p p > w+ w-` in `dim8_is` at 13.6 TeV, with every entry of DIM8 and DIM8F at 1 and Lambda at
1 TeV, that bracket is +1.11 +- 0.19 pb (`examples/studies/diboson/np0_shift.tsv`). At Lambda =
3 TeV it is +0.014 +- 0.002 pb (`validate/np0_shift.py examples/studies/diboson --report`),
against a tagged interference of -0.044 pb (`examples/studies/quickstart/results.tsv`). It vanishes
for every process in which no W is produced or exchanged. It does not vanish in vector-boson
fusion, where the W sits in the t-channel propagators: 6.7 +- 0.9 per cent of the cross
section in `p p > h h j j QCD=0` at Lambda = 1 TeV (`examples/studies/vbf_dihiggs/np0_shift.tsv`),
with `ptj` = 25 GeV, `etaj` = 5 and `mmjj` = 400 GeV.

## 5. Output

`mystudy/results.tsv`, one row per process, model and order: cross section, error, event count,
the W mass at that row's coefficients, the settings used, and the path to the event file. Event
files land in `mystudy/lhe/` as gzipped LHE.

`mystudy/records.tsv` says where each cross section comes from: the model MadGraph read (a hash of
its Python files, the sha256 of the release archive when the directory is a release, the hash of the
restriction card), the MadGraph version, the `import model` and `generate` commands, the param and run
cards as the run used them (a hash of each, with a copy in `mystudy/cards/`), and the event file with
its sha256 and the cross section MadGraph wrote into its header.

    examples/studies/provenance.py check mystudy/results.tsv

compares each line of `results.tsv` with its record, its event file and its cards: the cross section
and its error, `Lam` and the coefficients the settings switch on, the coefficients the restriction card
keeps, the process and order generated, the event count, beam energies and cuts of the run card (a
cut that `processes.txt` does not set must have the value MadGraph writes), whether every line comes
from one version of the model and, for each restriction card, from one version of that card, and
whether that version of the model is the released one, whose hash follows from the list
`models/<name>.sha256` (for a model with no list, the directory `models/<name>/` as it is). A line
whose cards have no copy in `mystudy/cards/` does not pass. The table and
figure scripts of `examples/studies/` make this check first and write nothing when it fails.
`plot_study.py` also writes `<prefix>.sources.tsv`, the event files behind its histograms and the
tables it wrote, each with its sha256, which `paper_figure.py` checks before it draws: the table must be
unchanged since, with an event file for every column. For cross sections computed before the records
were kept, `provenance.py recover` writes the records from the headers of their event files, and lists
those it cannot trace. Such a record is marked as recovered, since the model and restriction card in it
are those that `--model` names for the import path of the run, and nothing in the event file confirms
them. The check passes a recovered line only once `attest` has tied it to the table's model, as below,
and never one with no event file, which has to be run again. A cross section computed with another
version of the model or of its restriction card counts as the table's only after `validate/same_couplings.py` has found its couplings equal to those
of the table's model, restricted by its own card of that name, at the cross section's cards and in every
vertex that a tree diagram of its process can contain, and `provenance.py attest` has written that into
its record.

An interference sample has negative weights and reproduces its cross section only statistically,
so its effective statistics is the excess of positive over negative events.

`examples/studies/observable.py` makes the distribution of any observable of these event files, or of
any other MadGraph run, with the normalisation and the errors of `plot_study.py`:

    examples/studies/observable.py pt:w+,w- 0,100,200,400,800 SM=<SM events> int=<interference events>

The README shows it on a process of your own, and the header of the script lists the observables it
knows and how to histogram any other.

## 6. One operator at a time

    for c in $(grep -o 'c8[A-Za-z0-9]*' models/dim8_is/param_card_template.dat | sort -u); do
        validate/make_restriction.py models/dim8_is op_$c $c
    done

then put those card names in `classes.txt`.

## 7. MadGraph practicalities

Write restriction cards with `validate/make_restriction.py` or `--card`, not by hand. MadGraph fuses
couplings that agree at the values of the card, and removes those that vanish there, whatever values
the run then sets, so round numbers can give the wrong amplitude with no message. The values these
two write satisfy no such relation.

`hel_recycling` defaults to on in 3.5 and fails on these Lorentz structures. Set it False. The
default run card lacks the key, so it has to be appended.

Set the beam energies. MadGraph defaults to 6500 GeV per beam.

`import model` takes an installed name or an absolute path. A relative path fails.

A restriction keeping only operators with no vertex removes the `NP` coupling order, and MadGraph
then rejects `NP^2==2` without explaining why.

Class 7 has no three-point vertex, so "No amplitudes generated" in a two-to-two diboson process is
physics, not an error.

`event_norm` defaults to `average`: every event of an unweighted sample carries the full cross
section as its weight and the cross section is the mean, not the sum. Normalise to the banner's
integrated weight.

Python 3.12 disables reweighting, 3.13 breaks `model_reader`. Use 3.11.
