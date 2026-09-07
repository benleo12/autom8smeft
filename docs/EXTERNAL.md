# External dependencies

Nothing in this list is redistributed here. You need none of it to **use** the model, which is
the point of shipping a UFO. You need it only to rebuild the model from the operator tables.

## To use models/dim8_is

MadGraph5_aMC@NLO 3.5.3 or later, and Python 3.11. That is all.

Python 3.12 generates events but disables reweighting, and 3.13 breaks `model_reader`.

## To rebuild the model

**FeynRules 2.3.49** and **Mathematica 13**. Get FeynRules from
<https://feynrules.irmp.ucl.ac.be/>. The generator expects it wherever `$FeynRulesPath` points.

**The base Standard Model FeynRules file.** `gen/` writes the dimension-eight Lagrangian on top
of a Standard Model `.fr` file which is not included, because it is a modified copy of the
FeynRules SM as distributed with the dimension-eight model of Hays, Martin, Setford and Sanz
(arXiv:1808.00442). Take theirs, or the stock FeynRules `SM.fr`, and place it at
`models/base/sm.fr`. `gen/input_scheme.py` reads it, applies the {alpha, MZ, GF} corrections and
writes `tests/gen_smoke/base_inputscheme.fr`, which is the file the UFO writer loads. The
substitutions it makes are listed in that script and are the whole interface, so any SM `.fr`
with the usual FeynRules names will do.

**Murphy's operator tables.** The basis is arXiv:2005.00059. `gen/parse_murphy.py` reads the
paper's LaTeX source, which you can download from arXiv, and expects it at
`murphy_src/dim8_v6.tex`. `docs/murphy_parsed.json` and `docs/block_index.json` are the parsed
output and are included, so you do not need the source unless you want to re-derive them.

## For the cross-checks only

**SmeftFR 3.03**, <https://www.fuw.edu.pl/smeftfr/>, used to compare 44 operator pairs.
**SMEFTsim 3**, <https://smeftsim.github.io/>, whose input-scheme conventions the dimension-six
half of `gen/input_scheme.py` reproduces to 1e-11, and which is where you take dimension six from
for a consistent 1/Lambda^4 result.
**The Eboli and Gonzalez-Garcia quartic-gauge operators**, for an independent check of the
bosonic classes against a different basis. This comparison has not been done and is the most
valuable one still open.

## Compute

The 674-operator vertex cache is the expensive part, days of Mathematica, and it is a one-off:
it uses the plain Standard Model and does not depend on the input scheme. Writing the UFO from
that cache is a single job, about sixteen hours for the full basis. Neither is needed to use the
shipped model.
