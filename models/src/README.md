# Model source

The FeynRules source the UFOs in `models/` are built from. Everything here is generated or
maintained by the code in `gen/` and `validate/`, and nothing here is edited by hand.

| file | what it is |
|---|---|
| `dim8_generated.fr` | the master dimension-eight Lagrangian: one `Block` per operator (`L8opNNN`), one named coefficient per operator (`c8...`), emitted by `gen/emit_fr.py` from the operator encoding `gen/operators.py`. A fermionic operator is written with a general flavour coefficient, a placeholder (`z8F2`, `z8F4`) that the rules of `gen_flavour_rules.m` replace when the UFO is written. `docs/block_index.json` maps every block to its operator label, its coefficient and the coefficients of its flavour structures. `./dim8 build` writes it again, with `tests/gen_smoke/gen.fr`, the same text, which is what the programs read. |
| `gen_flavour.fr`, `gen_flavour_rules.m` | the placeholders, and the rules that put the flavour structures of each fermionic operator in their place (`gen/emit_flavour.py`, from the list `build/mfv_structures.json`). The structures are those of minimal flavour violation. A four-fermion operator has both pairings of its fields into flavour invariants. Each bilinear carries a delta, or the Yukawa matrix where it joins two species, with at most one insertion of Y Y^dag, and with the up and down Yukawas, whose top and bottom entries are of order one, both bilinears may carry one at once. Each structure has a coefficient of its own in block `DIM8F`, real and imaginary parts apart. `./dim8 model` writes a model for a process with the structures in its Lagrangian, so that FeynRules reads it without the rules. |
| `base.fr` | the Standard Model base (FeynRules SM template, unitary gauge, Goldstones removed). A model on it alone has no input relations and does not ship. `./dim8 rebuild` writes one as `models/dim8_plain` where that directory exists, for `validate/index_vs_ufo.py`. |
| `base_inputscheme.fr` | the base with the {alpha, M_Z, G_F} input scheme and canonical normalisation through 1/Lambda^4, emitted by `gen/input_scheme.py` from `gen/input_scheme_formulae.json`. `models/dim8_is` is `base_inputscheme.fr + dim8_generated.fr` with the Lambda^-8 truncation (`DIM8_TRUNCATE=1`). |
| `base_inputscheme_mw.fr` | the same in the {M_W, M_Z, G_F} scheme (`gen/input_scheme_formulae_mw.json`). |
| `base_fg.fr` | the base in Feynman gauge, for MadGraph's `check gauge` and the Feynman-gauge vertex lists. |

## Conventions

The covariant derivative is `D_mu = d_mu + i g A_mu`, Murphy's convention, set by
`FR$DSign = -1` in the base files. This is the opposite of the FeynRules default. When comparing
with a model built on the default convention the two are related by `A -> -A`, under which the
Standard Model is invariant and every field strength changes sign, so a coefficient here equals
`(-1)^{n_F}` times the coefficient of the same operator there, with `n_F` the number of field
strengths in the operator. Covariant-derivative operators carry no sign.

## From source to UFO

One command goes from `gen/operators.py` to the released models:

    ./dim8 rebuild                     # every model this tree can write
    ./dim8 rebuild --models dim8_mw    # one of them
    ./dim8 rebuild --dry-run           # the checks, and what would be computed and written

It needs Mathematica 14 or 15 and FeynRules 2.3.49 unpacked at `external/feynrules/feynrules-current`,
a Python with `numpy` for the zero tests of the release (`DIM8_NUMPY_PY` names it, and otherwise
`python3.13` or `python3`), and MadGraph for its import test (`MG5_DIR`, and `DIM8_SKIP_MG5_IMPORT=1`
releases without that test and says so). It checks for all of them before it starts, since the release
comes after the hours of writing a UFO. `WS` names `wolframscript` when it is not on the `PATH`. On a
cluster, set `WS=hpc/ws_retry.sh` and `WS_REAL` to the `wolframscript`. Now and then one of the hundreds
of kernels a rebuild starts never connects, and its `wolframscript` then waits for ever. The wrapper sees
that and starts it again.

A clone has no vertex cache, so its first run computes every block, about eight days of one worker,
which the `-j` workers share, with the heaviest operators under 60 GB of memory. After that a correction
recomputes that operator alone, but writing a UFO merges every operator again. The command writes it in 120 small UFOs side by
side and joins them (`hpc/write_shards.sh`, `--shards`), three to four hours on a node of 64 cores, set by the
slowest shard, out of 60 to 100 hours of one kernel for the whole model. The command stops at the first step that
fails, and the model it would have replaced stays in place. It takes no cached block without a stamp,
since nothing then shows that a correction has reached the block. `python3 validate/cache_source.py
backstamp <cache> --write` checks such a block against the history of `gen.fr`, and it stamps the block
or marks it for a rebuild.

To correct an operator, edit its entry in `gen/operators.py`, in its terms and, if the correction
changes it, in its `cp` and `hc_mode`, and run the command. A new operator goes after the last
entry, with a name and a coefficient of its own. The block number, the label and the coefficient name
of an existing operator must stay, since the vertex cache, the released models and the restriction
cards are keyed on them, and the build stops if they change. An operator that changes between a real
and a complex coefficient moves the numbers of the later coefficients in block `DIM8`, and the release
gives every card in the model directory the new numbers (`validate/rekey_cards.py`). A card kept
anywhere else holds the old ones.

The exception is one of the fourteen operators that enter the input relations (`INPUT_SCHEME_WCS` in
`./dim8`). The base files hold those relations, which are derived from the operators by hand and are not
written from the encoding, so the build stops when one of these operators changes. Correct the relation
in `gen/derive_input_scheme.py`, `gen/derive_rotation.py` or `gen/derive_higgs_yukawa.py`, and then:

    python3 gen/derive_input_scheme.py alpha
    python3 gen/derive_rotation.py alpha
    python3 gen/derive_input_scheme.py mw
    python3 gen/derive_rotation.py mw
    python3 gen/derive_higgs_yukawa.py
    python3 gen/input_scheme.py tests/gen_smoke/base.fr tests/gen_smoke/base_inputscheme.fr alpha
    python3 gen/input_scheme.py tests/gen_smoke/base.fr tests/gen_smoke/base_inputscheme_mw.fr mw
    ./dim8 rebuild --relations-updated

The steps of the command follow, each of which can be run alone from this tree, with `DIM8_ROOT=$PWD`
in the environment of a Wolfram program:

1. `./dim8 build --source-only` checks the encoding before it writes anything, and stops on a failure:
   `validate/structural.py` (mass dimension, contracted indices, hypercharge, invariant tensors) and
   the CP parity recorded on each operator against the parity of its encoded terms (`gen/cp_parity.py
   --check`). A disagreement is a finding, and nothing overwrites either side. It then writes
   `tests/gen_smoke/gen.fr`, `docs/block_index.json`, `docs/catalogue.json`,
   `examples/cards/coefficients.md` and the copies in this directory from `gen/operators.py`, which
   needs no Mathematica.
2. `./dim8 build` does that and computes the vertices. `validate/fr_worker.wls` evaluates one block at a
   time (`ExpandIndices`, `FeynmanRules`, `CheckHermiticity`) and caches the vertex list with a stamp of
   the code it came from (`validate/cache_source.py`). A cached block is skipped unless its stamp differs
   from its code, and then it is rebuilt. The six operators `Q_{G^4}^{(2),(4),(5),(6),(8),(9)}` are
   built up to six legs in a worker of their own (`DIM8_MAXLEGS=6`, `DIM8_EPSEPS=0`, `DIM8_CHUNK=25`),
   since their seven- and eight-gluon vertices exceed the memory of a node, and every other operator is
   built whole. A worker that is run alone rebuilds a stale block with the leg range of its status line.
3. For a combined model, the worker computes the eleven dimension-six blocks on the base of its scheme,
   in `DIM8_VDIR6` or `DIM8_VDIR6_MW`, by default beside the dimension-eight cache with the suffixes `6`
   and `6_mw`. `docs/DIM6.md` gives the command.
4. `./dim8 index` writes the vertex lists the selector reads, from the caches, on `base.fr`.
5. `DIM8_BASE=base_inputscheme_mw.fr DIM8_TRUNCATE=1 DIM8_VDIR=<cache> wolframscript -file
   validate/fr_writeufo.wls dim8_mw_raw build/dim8_mw.blocks` merges the caches for the block list of
   the model and writes the UFO into `tests/gen_smoke`, here for `dim8_mw`, with `DIM8_BASE` the base of
   its scheme. `hpc/write_shards.sh` (`plan`, `run`, `merge`) writes the same UFO in shards, the base
   together with the operators of its relations in one of them, with `validate/merge_ufo.py` joining them, and `validate/compare_ufo.py` compares the result with a model
   written in one piece, vertex by vertex at random momenta, wavefunctions and coefficients.
6. `bash examples/release_model.sh tests/gen_smoke/dim8_mw_raw dim8_mw` turns the UFO into
   `models/dim8_mw`. It reads the model back before the model replaces the old one: the files must be
   well formed, pass `validate/audit_ufo.py` and `validate/check_dimensions_ufo.py`, and import in
   MadGraph.
7. `python3 gen/catalogue_json.py` writes the catalogue again, since a corrected operator can gain or
   lose its vertices, `python3 validate/dim6_index.py --models models/dim68_is models/dim68_mw` reads the
   dimension-six vertices off the combined models, and `python3 validate/index_vs_ufo.py --write`
   compares the vertex lists with the released models. It stops on a vertex that one model has and
   another lacks, which is what it finds while only some of the models have been rewritten after a
   correction. In the chain the lists of step 4 are written as `build/vertex_index_new.json` and its
   two neighbours, and they replace the lists that `./dim8 select` reads only when this step passes, so
   a chain that fails on the way, or a run for some of the models, leaves those lists as they were.

Two inputs of `./dim8 series` and of the `{0}` marks are not part of this chain. The Feynman-gauge lists
(`build/*_fg.json`) hold the old vertices of a corrected operator with a Higgs doublet until that block is
built again on `base_fg.fr`, in a cache of its own, and merged into them:

    DIM8_ROOT=$PWD DIM8_BASE=base_fg.fr DIM8_VDIR=<its cache> DIM8_MAXLEGS=6 DIM8_HERM=0 \
        wolframscript -file validate/fr_worker.wls L8op469 0 734 0 20000
    DIM8_ROOT=$PWD DIM8_BASE=base_fg.fr DIM8_VDIR=<its cache> DIM8_INDEX_TAG=_fg DIM8_INDEX_MERGE=1 \
        wolframscript -file validate/dump_vertex_index.wls

Without `DIM8_INDEX_MERGE=1` the dump holds only the blocks of the caches it is given, and the lists
would lose every other block. `build/onshell_zero.json` holds the old outcome of a corrected three-point
vertex of two fermions until `python3 validate/onshell_zero.py` reads the released models again. That
command writes the whole file, so it keeps the outcomes of the Goldstone vertices only with `--fg`, which
names a Feynman-gauge UFO of the blocks that `--list-fg-blocks` lists.

`./dim8 rebuild --blocks FILE` tries the chain on the blocks of a file, as `models/<name>_trial`. It
computes only those blocks, so it takes minutes when they are cached or small, and it leaves the released
models and the vertex lists alone.

The Wolfram programs are headless `wolframscript` programs that load
`tests/fr_env/fr_headless_init.m` (the runtime fixes FeynRules 2.3 needs on Mathematica 14 and 15) and
read the base file and `gen.fr` from `tests/gen_smoke` under `DIM8_ROOT`. The base files are
there too, so this directory is the readable copy and `tests/gen_smoke` the working one. Run alone, the
base is chosen with `DIM8_BASE` (default `base.fr`) and the cache directory with `DIM8_VDIR`. The
usage lines at the top of each script give the arguments.

## Not shipped

The dimension-six sector of `models/dim68_mw` and `models/dim68_is` uses SMEFTsim's operator
definitions on this base, so `./dim8 rebuild` leaves the combined models out until
`tests/gen_smoke/dim6_smeftsim.fr` exists: obtain SMEFTsim from its authors and run `gen/make_dim6.py`
(see `docs/DIM6.md`). The vertex caches are build artifacts and are regenerated by `./dim8 build`.
