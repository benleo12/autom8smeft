# 14: which operators can enter my process at all?

MadGraph answers this implicitly by drawing the diagrams, but the operator list is useful before
writing a restriction card. The selector reads the vertex index shipped with the code (Python
only) and lists every operator with a vertex that can appear in a tree diagram of the process,
at one or two insertions:

    ./dim8 select "p p > z h"                  # one insertion
    ./dim8 select --two-insertions "p p > z h" # two insertions in one amplitude

For the LHC processes of the paper the counts are

| process | one insertion | two insertions |
|---|---|---|
| p p > h j j | 209 | 218 |
| p p > z h | 68 | 70 |
| p p > w+ w- | 96 | 96 |
| u u~ > w+ w- | 63 | 63 |
| u u~ > z h | 48 | 48 |
| u u~ > a h | 40 | 43 |

The selector follows internal fermion lines and multi-boson vertices, so it can be larger than
a first guess; an operator listed here contributes at least one diagram, which may still vanish
after interference or cuts. Feed the output straight into `validate/make_restriction.py` to get a
model containing only those operators.

## The second group: operators with no vertex that still contribute

The vertex test is one half of the answer. An operator that enters the electroweak input
relations shifts the weak coupling, the hypercharge coupling, the vev and the W mass of every
amplitude, whether or not it has a vertex among the external legs. The clearest case is
`p p > w+ w-`: the two operators `Q_{l^2H^4D}^{(2)}` and `Q_{l^2H^4D}^{(4)}` contain no quarks,
enter through muon decay and so through G_F, and carry about a third of the process's
dimension-eight interference through their shift of `gw`, the vev and `MW`, with no vertex in
any diagram.

Eight operators act this way, classes 3 (H^6 D^2) and 6 (X^2 H^4) and the two l^2 H^4 D
operators of class 13, and `./dim8 select` lists whichever of them have no vertex in the process
under its own heading, "through the input relations, with no vertex in this process", counts them
in its summary line and writes them into the block list with `-o`. The two groups together are
the complete list at tree level with one insertion; there is nothing further to add by hand.
`validate/eval_ufo_params.py <model> <coefficient>=1 Lam=1000` prints the shifts any coefficient
induces, which is how to see what each of the eight does.
