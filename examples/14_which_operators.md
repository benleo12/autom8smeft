# 14: which operators can enter my process at all?

MadGraph answers this implicitly by drawing the diagrams, but the operator list is useful before
writing a restriction card. The selector reads the vertex index shipped with the code (Python
only) and lists every operator with a vertex that can appear in a tree diagram of the process,
at one or two insertions:

    ./dim8 select "p p > z h"                  # one insertion
    ./dim8 select --two-insertions "p p > z h" # two insertions in one amplitude

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
a first guess; an operator listed here contributes at least one diagram, which may still vanish
after interference or cuts.

Beside each operator the selector prints the vertex of its leading tree and that tree's power of
lambda, with (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1) as in `gen/lambda_routes.py`: when
an operator reaches the process through vertices with different numbers of legs, the one printed
is the one through which it grows fastest with energy, which holds in the tails, E >> v, and says
nothing about the inclusive rate. A tree through a Yukawa coupling of a quark or lepton is not
counted, since the fermion mass suppresses it, so an operator that reaches the process only that
way is printed with the vertex that fits and the remark "only through a quark or lepton Yukawa
coupling". In `p p > w+ w-` that is the case for `Q_{H^6}^{(1,2)}` and `Q_{W^2H^4}^{(1,2)}`,
through an s-channel Higgs boson attached to the light quarks. `--card NAME` writes the selection, together with the second group
below, as a restriction card in the model, for `import model dim8_is-NAME`.
`validate/make_restriction.py` writes a card for any other subset.

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
relations)", and writes them into the restriction card with `--card` and into the list of blocks
with `-o`. The two groups together are the complete list at tree level with one insertion.

The second group follows the model named by `--model` (default `models/dim8_is`). With
`models/dim8_mw` the same eight shift the electromagnetic coupling instead of the W mass and the
heading names the {MW, MZ, GF} scheme. `models/dim8_plain` has no input relations, so there is no
second group, and it carries vertices that the input schemes absorb, such as the three-gluon
vertex of `Q_{G^2H^4}^{(1)}`, which the selector then uses (`build/vertex_index_absorbed.json`,
written by `validate/index_vs_ufo.py --write`). With `models/dim68_is` the selector also lists the
dimension-six classes under their Warsaw names and the four dimension-six coefficients of the input
relations, `C_HD`, `C_HWB`, `C_Hl^(3)` and `C_ll'`.
`validate/eval_ufo_params.py <model> <coefficient>=1 Lam=1000` prints the shifts any coefficient
induces, which is how to see what each of the eight does.
