# 14: which operators can enter my process at all?

MadGraph answers this implicitly by drawing the diagrams, but the operator list is useful before
writing a restriction card. The selector reads the vertex index shipped with the code (Python
only) and lists every operator with a vertex that can appear in a tree diagram of the process,
at one or two insertions. This page uses `models/dim8_is`, the {alpha, MZ, GF} scheme:

    ./dim8 select "p p > z h" --model models/dim8_is                   # one insertion
    ./dim8 select --two-insertions "p p > z h" --model models/dim8_is  # two insertions in one amplitude

For the LHC processes of the paper the counts of operators with a vertex are

| process | one insertion | two insertions |
|---|---|---|
| p p > h j j | 210 | 219 |
| p p > z h | 68 | 68 |
| p p > w+ w- | 96 | 96 |
| u u~ > w+ w- | 63 | 63 |
| u u~ > z h | 48 | 48 |
| u u~ > a h | 40 | 43 |

The selector follows internal fermion lines and multi-boson vertices, so it can be larger than
a first guess. An operator listed here contributes at least one diagram, which may still vanish
after interference or cuts.

Beside each operator the selector prints the vertex of its leading tree and that tree's power of
lambda, with (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1) as in `gen/lambda_routes.py`: when
an operator reaches the process through vertices with different numbers of legs, the one printed
is the one through which it grows fastest with energy, which holds in the tails, E >> v, and says
nothing about the inclusive rate. A tree through the Yukawa coupling of a light quark or a lepton
is not counted, since the fermion mass suppresses it, and neither is a tree whose light fermion line
joins a left-handed and a right-handed field, which needs the mass itself. An operator that reaches
the process only that way is printed with the vertex that fits and the remark "only through the
Yukawa coupling or the mass of a light quark or a lepton". In `p p > w+ w-` that is the case for
`Q_{H^6}^{(1,2)}` and `Q_{W^2H^4}^{(1,2)}`, through an s-channel Higgs boson attached to the light
quarks. In `u u~ > w+ w-` it is the case for `Q_{qdWH^3}^{(1)}`, whose vertex joins a left-handed u
to a right-handed d, and for the right-handed charged currents `Q_{udH^2D^3}` and `Q_{udH^4D}`,
whose vertex joins a right-handed u to a right-handed d. Their right-handed quark meets the
left-handed W current of the Standard Model only through its mass. In `p p > w+ w-` they are
flagged as well: their tree through the b b~ initial state runs on a top line, but the current
carries Y_u^dag Y_d, so that tree carries y_t y_b. The top Yukawa coupling and the top mass are counted like any other
vertex, the mass at one power of lambda. The selection itself is flavour and chirality blind, so
it can list an operator that has no tree once the flavours of the external particles are kept,
for example in `u b~ > e+ ve`, since a b quark joins only a top quark at a W vertex. Such an
operator is printed with the remark "has no tree once the flavours of the external particles are
kept". With `QCD=0` in the process, as in electroweak `p p > h h j j QCD=0`, the powers leave out
every tree with a power of g_s, as MadGraph does, while the selection keeps them, so that an
operator which reaches the process only through gluon couplings, `Q_{G^3H^2}^{(1)}` among them, is
printed with the remark "only through a power of g_s, which QCD=0 removes", and one that needs a
light Yukawa coupling or mass as well with "only through a power of g_s, which QCD=0 removes,
together with the Yukawa coupling or the mass of a light quark or a lepton". An operator that only
the second insertion brings in, as three do in `u u~ > a h`, has no tree with one insertion and is
printed with the remark "only with a second operator insertion". A longitudinal mark, `w+{0}`,
needs the Feynman-gauge vertex lists that ship in `build/`, and without them the operators are
printed with no powers and a note saying why.

    ./dim8 select "p p > z h" --model models/dim8_is --card NAME

writes the selection, together with the second group below, as a restriction card in the model,
for `import model dim8_is-NAME`. `validate/make_restriction.py` writes a card for any other subset.

## The second group: operators with no vertex that still contribute

The vertex test is one half of the answer. An operator that enters the electroweak input
relations shifts the weak coupling, the hypercharge coupling, the vev and the W mass of every
amplitude, whether or not it has a vertex among the external legs. The clearest case is
`p p > w+ w-`: the two operators `Q_{l^2H^4D}^{(2)}` and `Q_{l^2H^4D}^{(4)}` contain no quarks,
enter through muon decay and so through G_F, and carry about a third of the process's
dimension-eight interference through their shift of `gw`, the vev and `MW`, with no vertex in
any diagram.

Eight operators act this way: the two of class 3 (H^6 D^2), four of class 6 (X^2 H^4) and the
two l^2 H^4 D operators of class 13. `./dim8 select` lists whichever of them have no vertex in the
process under its own heading, "through the {alpha, MZ, GF} input relations, with no vertex in this
process", counts them in its summary line, marks those of the first group with "(and the input
relations)", and writes them into the restriction card with `--card` and into the list that `-o`
writes for `./dim8 ufo`. The two groups together are the complete list at tree level with one insertion.

The second group follows the model named by `--model`. Without the option it is `models/dim8_mw`,
the {MW, MZ, GF} scheme, where the same eight shift the electromagnetic coupling instead of the W
mass and the heading names that scheme, and the card goes into that model, for
`import model dim8_mw-NAME`. This page uses `models/dim8_is`, the {alpha, MZ, GF} scheme. With
`models/dim68_is` the selector also lists the dimension-six coefficients, one by one under the
headings of their Warsaw classes, each with the vertex of its leading tree and that tree's power of
lambda, and the four dimension-six coefficients of the input relations, `C_HD`, `C_HWB`, `C_Hl^(3)`
and `C_ll'`, under a heading of their own. It reads the vertices of each coefficient from
`build/dim6_index.json`, which `python3 validate/dim6_index.py` writes from the released models, and
without that file it lists the classes instead and says so. The vertices of a coefficient include
the Standard Model vertices it rescales: `C_HBox` names no vertex but the Higgs self-couplings, and
it rescales h W W, h Z Z and the Yukawa couplings through the normalisation of the Higgs field, each
counted at the power of the Standard Model vertex and four more, so that it enters `u u~ > z h` at
lambda^5, four above the Standard Model amplitude. A coefficient with no tree of one insertion can
still enter at 1/Lambda^4 where the Standard Model has a tree: through a tree with a second
dimension-six vertex, of the same coefficient or another, or through a vertex at order NP=2 that
multiplies it by a second coefficient or by itself, both of which interfere with the Standard Model
at that order. Such a coefficient is listed with the remark "only with a second dimension-six
insertion, of this coefficient or another". So is one whose trees with one insertion all need a
light Yukawa coupling, when it has a vertex at NP=2 with no fermion or gluon leg through which the
counting finds a tree: `C_HW` in `p p > w+ w-`, whose gauge vertices cancel at 1/Lambda^2 against
the rescaling of the W field and come back at 1/Lambda^4 on the triple-gauge vertex of `C_W`. Where
the Standard Model has no tree only the coefficients with a tree of their own enter at 1/Lambda^4,
through the square of the dimension-six amplitude. The coefficients of the input relations enter
even where the input relations shift no Standard Model tree, as in `g g > t t~`, since their shift of
the vev multiplies dimension-six vertices, the chromomagnetic vertex of `C_uG` among them. In
`p p > w+ w-` the listing holds the coefficients with a tree of one insertion, `C_HWB` among them,
and those that enter only with a second insertion, among them the other three of the input
relations, whose shift of g_2 and the vev multiplies the W vertex of `C_Hq^(3)`, and
`--card NAME --with-dim6` keeps exactly the listed coefficients and those of the input relations not
among them, which `validate/select_complement6.py` checks by matrix elements. `models/dim8_is` and
`models/dim8_mw` have no dimension-six sector and refuse the option. With a longitudinal mark, `w+{0}`, the dimension-six coefficients are listed with no
powers, with the Feynman-gauge lists or without them, since `build/dim6_index.json` is read from the
unitary-gauge model and holds no Goldstone vertex. The dimension-six sector follows SMEFTsim's
U(3)^5 flavour symmetry, in which the coefficient of an operator whose fermion bilinear joins two
different fields carries a Yukawa matrix, as in `C_dH = cdH Y_d`. Only the top-quark entry y_t is
of order one, so the Yukawa-like operators and the dipoles count for the top quark alone, and the
scalar four-fermion operators, each of which carries a light Yukawa coupling as well, not at all. A
coefficient that reaches the process only through such a light entry is flagged like a light Yukawa
coupling.
`validate/eval_ufo_params.py <model> <coefficient>=1 Lam=1000` prints the shifts any coefficient
induces, which is how to see what each of the eight does.
