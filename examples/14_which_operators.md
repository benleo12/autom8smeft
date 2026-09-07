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

## What the selector cannot see

`./dim8 select` follows the model's vertices: it starts from the external legs and asks which
operators have a vertex that can be reached with Standard-Model internal lines. An operator that
affects the process only through the electroweak input relations has no such vertex and is not
listed, even though it changes the answer. The clearest case is `p p > w+ w-`: the two operators
`Q_{l^2H^4D}^{(2)}` and `Q_{l^2H^4D}^{(4)}` contain no quarks, enter through muon decay and so
through G_F, shift the weak coupling by `gw2` and the W mass with it, and carry about a third of
the process's dimension-eight interference. The same holds for `Q_{H^6}`, the X^2 H^4 operators
and the other G_F operators wherever their vertices do not reach.

So the operators that can affect a process are the selector's list plus the input-relation
operators, which are the same short list for every process: classes 3 (H^6 D^2) and 6 (X^2 H^4),
and the l^2 H^4 D operators of class 13. `validate/eval_ufo_params.py <model> <coefficient>=1
Lam=1000` prints the shifts any coefficient induces, and a coefficient with a nonzero `gw2`,
`vev2` or `MW22` is one to include whatever the selector says.
