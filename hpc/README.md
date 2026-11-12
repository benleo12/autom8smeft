# The long steps of the build, side by side

The scripts of this directory run the long steps of the build on many cores at once: on one machine, or as
steps of Slurm jobs. `./dim8 rebuild` calls the first of them itself, and `hpc/build_geo.sh` builds the models
of order N with the others. None of them names a machine. Each takes the checkout from `DIM8_ROOT`, its caches
from the variables its header lists, and the `wolframscript` to call from `WS`.

| script | what it does | who calls it |
|---|---|---|
| `write_shards.sh` | writes one UFO as many small UFOs side by side and joins them | `./dim8 rebuild`, `build_geo.sh` |
| `ws_retry.sh` | `wolframscript`, started again when its kernel never starts | whatever has it as `WS` |
| `run_parts.sh` | computes one heavy block in many processes at once | `build_geo.sh`, or by hand |
| `build_geo.sh` | builds a model of order N, `dim68_mw_geo<N>`, from its sources to the released model | by hand |
| `geo_sched.py` | spreads the blocks of `build_geo.sh blocks` over Slurm jobs | `build_geo.sh` with `GEO_SCHED` |
| `twopoint_geo.sh` | runs the two-point checks of the models of order N in K kernels | by hand |

## What a machine needs

* What `./dim8 rebuild` needs (`models/src/README.md`): Mathematica with FeynRules, a `python3` with `numpy`,
  and for the models of order N `sympy` as well. On a cluster, load its modules for them first.
* A checkout and caches on a file system that keeps its files: not a synchronised folder, which may evict
  them. `DIM8_ROOT` names the checkout, and the header of each script the variables of its caches and logs.
* One Mathematica licence seat for every kernel that runs at once. Each script takes the number of kernels as
  an argument or a variable (`--par`, `GEO_PAR`, the K of `twopoint_geo.sh`).
* `WS=hpc/ws_retry.sh` with `WS_REAL` set to the `wolframscript`, where hundreds of kernels start side by side.
  Now and then one of them never connects to its `wolframscript`, which then waits without end. The wrapper
  sees that and starts it again, three times at most.
* On Slurm, a job to run in. A login node should only start the steps. `GEO_RUN=slurm` makes `build_geo.sh`
  run each kernel as a step through `$GEO_SRUN` (`srun -N1 -n1`, or `srun --jobid=<job> --overlap -N1 -n1`
  inside an allocation that is already held), and every other script can be started the same way.

## One UFO in shards: `write_shards.sh`

FeynRules' WriteUFO on a whole model runs for a day or more, and its time grows faster than the number of
blocks. So the cached blocks are written as many small UFOs at once, and `validate/merge_ufo.py` joins them.
`validate/compare_ufo.py` checks the result against a model written in one piece.

    hpc/write_shards.sh plan  NAME BLOCKS NSHARDS [WITHBASE]   # the block list of each shard, by cache size
    hpc/write_shards.sh run   NAME FIRST LAST PAR              # writes shards FIRST..LAST, PAR at a time
    hpc/write_shards.sh merge NAME                             # joins them into tests/gen_smoke/NAME_raw

`./dim8 rebuild` runs the three for each model (`--shards`, `--par`). Shard 0 holds the vertices of the base
model and the blocks of the file WITHBASE, the operators that enter the relations of the base, whose vacuum
pieces cancel against the shifts the base carries only when the two are written together. A plan never has
more shards than blocks, so a large NSHARDS gives one block a shard. What follows is in the header of the
script in full.

* A shard is complete when its UFO is whole and its key is the one it would have now. The key
  (`build/shards/NAME/<k>.key`) records what the shard was written from: for each block the stamp of its source
  (`validate/cache_source.py`) and the content of its vertex file, then every model file the writer loads and
  the settings that change what it writes. `run` skips a complete shard and writes any other again, so a run
  cut short is taken up by running it again, and a shard written from another version of a block is not kept.
* A UFO is whole (`hpc/write_shards.sh sound NAME K`) when every file of a UFO is there and none is empty,
  each data file is Python, the couplings and Lorentz structures defined are exactly those its vertices use,
  and every name in a value is a parameter. A full disk or quota can leave a UFO with files missing or cut
  short under a log that says it is written, and such a shard gets no key.
* `merge` joins the shards only when each is complete, and records which it joined
  (`build/shards/NAME/merged`). `hpc/write_shards.sh merged NAME` exits 0 when the joined model is still the
  merge of the shards as they are.
* Shard 0 runs on one kernel like the others (`DIM8_NKERNELS_BASE`, 0 by default), which is faster than
  with subkernels: see "The writer" below.

## One heavy block in parts: `run_parts.sh`

`hpc/run_parts.sh BLOCK N [M]` computes a block that takes hours on one kernel as N parts at once, after an
expansion in M processes, and joins the parts into the block a single run gives. A run cut short is taken up
from the parts it has, as long as the source of the block is the one they were made from. `build_geo.sh`
uses it for the heaviest blocks when it spreads them over Slurm jobs.

## The models of order N: `build_geo.sh`

`hpc/build_geo.sh` builds `dim68_mw_geo<N>`, the model `dim68_mw` with its two- and three-point vertices
complete through `1/Lambda^(2N)`: the dimension-six and dimension-eight operators with their input relations,
field normalisations, quartic and Yukawas to that order, and the members of dimension 10 to `2N + 4` of the
geoSMEFT towers of `gen/towers.py`. Its vertices with four or more fields are those of `dim68_mw`, through
`1/Lambda^4`, the quartics of the Standard Model among them. N = 2 gives the two- and three-point vertices
of `dim68_mw` itself, N = 4 those through dimension twelve. The header of the script says how each vertex
enters and lists its settings.

    hpc/build_geo.sh all 4            # or the steps one by one:
    hpc/build_geo.sh sources 4        # base_geo4_mw.fr, dim6_geo.fr, gen_geo4.fr and the block lists
    hpc/build_geo.sh blocks 4         # the 164 blocks of the geo tree into $GEO_VDIR
    hpc/build_geo.sh cachecheck 4     # the 157 cached tower blocks against their operators
    hpc/build_geo.sh write 4          # the UFO in shards, with the release caches
    hpc/build_geo.sh low 4            # the vertices of at most three legs once more, without the truncation
    hpc/build_geo.sh merge 4          # tests/gen_smoke/dim68_mw_geo4_raw
    hpc/build_geo.sh check 4          # the export checks, then models/dim68_mw_geo4
    hpc/build_geo.sh adopt 4          # once, for the shards of a write made before shards had keys

* When. After the release caches exist (`DIM8_VDIR` and `DIM8_VDIR6_MW`, as `./dim8 rebuild` leaves them,
  with `tests/gen_smoke/dim6_smeftsim.fr`, which `gen/make_dim6.py` writes from SMEFTsim's sources)
  and with the release `models/dim68_mw` unpacked, which the check compares with (`GEO_REF`). Run `sources`
  again after a change to `gen/operators.py`, `gen/towers.py`, `gen/input_scheme.py` or `gen/make_dim6.py`.
  `blocks` then rebuilds exactly the blocks whose source changed, by their stamps (`validate/cache_source.py`).
  At order 3 and 4 `sources` first runs `gen/derive_geo.py N mw` if its relations are missing (sympy, hours
  at N = 4).
* Where. `GEO_RUN=local` (the default) runs every kernel on this machine, `GEO_RUN=slurm` runs each through
  `$GEO_SRUN` (`srun -N1 -n1`, or `srun --jobid=<job> --overlap -N1 -n1` inside a held allocation). With
  `GEO_SCHED=<file of "<job> <cores>" lines>`, `blocks` spreads the geo blocks over those jobs, the heavy ones
  split into parts (`hpc/geo_sched.py`, `hpc/run_parts.sh`), with the times of an earlier build of the same
  order from `GEO_TIMES`. A block starts on a running holder with its cores free, preferably one that runs for
  twice its estimate more, else on one that may end first, and never on a holder that is not running or has
  less than ten minutes left. A holder that is starting, ending, requeued, suspended or preempted, or that
  `squeue` cannot report, counts as coming back for `GEO_SCHED_GRACE` seconds (900) after it was last running or
  waiting, and a block whose holder stopped under it goes back to the list without using up its one retry. Each
  block runs under a lock that names its slurm step and its host and process (`<job>.<step> <host>:<pid>`), and
  a lock whose step has left the queue, or whose process on this host has gone, is taken over. The scheduler
  gives up with exit 1, and the blocks left in `sched.log`, when no holder is running, waiting in the queue or
  coming back, or when nothing has run or could start for `GEO_SCHED_IDLE` seconds (3600). It then names the
  blocks under a lock it cannot tell, an older one that names only its job (a step killed before its exit trap
  ran leaves it, and the job may stay in the queue for hours): remove `$GEO_VDIR/<block>.lock` once no step of
  that job runs the block. The blocks are the short part: the 58 geo blocks of N = 2 took 1.6 core hours and
  the 164 of N = 4 took 7.6. The write is the step that wants a cluster. At N = 4, with one block a shard
  (`GEO_SHARDS` at the number of blocks or more), the 661 shards took 120 core hours: five and a half minutes
  for the median shard, 54 minutes for shard 0, which holds the base and the blocks written with it, and 2.7
  hours for the heaviest, which sets the time of the write when a hundred kernels run at once.
* The worker and the tower blocks. The Module of a block `G8op<i>` or `T<d>op<i>` ends in
  `Return[z8geoTrunc[., p]]`, which puts the corrections of the base on its fields and couplings to the order the
  block owes. `validate/fr_worker.wls` caches a block term by term and never evaluates that Return, so it applies
  the truncation itself, to every expanded monomial, at the order p it reads from the Return, and writes
  `geotrunc <p>` in the status line of the block. A block cached without that truncation is right at its own
  order and wrong above it, and the step `cachecheck` below does not let such a block through to the write.
* The cached blocks against their operators. `cachecheck` runs `validate/geo_cache_check.wls` on every block of
  `gen_geo<N>.json` (`G8op<i>`, `T<d>op<i>`), in `GEO_PAR` kernels at once, each with a list of blocks. The check
  evaluates the Module of a block whole and compares the coupling of every structure of its vertices of at most
  three legs with the cached block, NP order by NP order through N, with every coefficient at an irrational
  value. The worker caches these blocks term by term and puts the corrections of the base on them itself, so a
  block cached without them is right at its own order and wrong above it. Nothing else sees that: the two-point
  checks evaluate the Modules and not the cache, and the export checks compare the model with `dim68_mw` at
  `NP <= 2` only. A block of order 4 cached without the corrections fails it, with
  `[cachecheck] G8op44 order 4: FAIL`, at 0.81 of its largest coefficient at NP 3 and 0.87 at NP 4. A block that
  passes is recorded in `$DIM8_BUILD/dim68_mw_geo<N>/cachecheck` with the content of its vertex file, the stamp
  of its source and the check it passed, and is not checked again while those stay. `write` stops unless every
  tower block has a pass of the cache and the source it has now. The dimension-six blocks `G6cl*` are not in this
  check: the worker evaluates them whole, with their corrections. The model load takes about 80 s a kernel at
  N = 4, and a block seconds to several minutes.
* The writer. `validate/np_truncate.m` moves the parameters to its two probe points with
  `validate/update_parameters.m` (`z8UpdateParameters`), which leaves what FeynRules' `UpdateParameters` leaves:
  that takes 150 s a call on the model of order 2 and does not end on the model of order 4, where this takes
  seconds. `validate/update_parameters_check.wls` compares the two (`DIM8_UPDATE_CAP=<s>` for a model on which
  FeynRules' call does not end). Shard 0, with the base, is written on one kernel (`DIM8_NKERNELS_BASE`, 0 by
  default): at N = 2 it took 798 s against 3017 s with four subkernels, 13 s against 622 s of it in
  LoadModel, and `validate/compare_ufo.py` finds the same 2357 vertices by coupling order in both.
* A write cut short. `GEO_FRESH=0 hpc/build_geo.sh write N` resumes it with the plan it has, which a new plan
  could deal differently. A shard is complete when its UFO is written, with every file of a UFO, and its key
  (`<k>.key`) is the one it would have now: for each of its blocks the stamp of its source, the content of its
  vertex file and whether its vertices of at most three legs are left out, then every model file the writer
  loads and the settings of the writer. A shard gets its key only when the UFO written is whole
  (`hpc/write_shards.sh sound`): every file there and none empty, each data file Python, the couplings and
  Lorentz structures defined exactly those its vertices use, and every name in a value a parameter. A full disk
  or quota can leave a UFO with files missing or cut short under a log that says it is written, and such a shard
  is written again. A complete shard is skipped, and a shard written from another version of a block, of the
  base or of the lists is written again.
  A complete shard whose record of its blocks (`<k>.prov`) is missing, cut off (it ends with the line
  `#end <blocks>`) or short of a block has it recorded alone (`DIM8_PROVENANCE_ONLY=1`, a minute or two) and is
  not written again. A shard written before shards had keys has none and is written
  again, unless `hpc/build_geo.sh adopt N` finds its UFO whole and younger than its plan and every file it is
  written from older, by its date and by its change time, which shows that the shard was written from them: run
  it once, with the settings of that write, which no file records (`hpc/write_shards.sh adoptable` says what it
  would do and writes nothing). A
  resume stops if the plan is not that of the current `model.blocks` and `withbase`. The writer itself
  (`validate/fr_writeufo.wls`, `validate/np_truncate.m`) is not in the key, so a change to it needs
  `GEO_FRESH=1`, the default, which plans afresh and removes the shards and the merged model of the earlier
  write. `merge` joins the shards only when each is complete and records which it joined
  (`build/shards/dim68_mw_geo<N>/merged`).
* What it writes. `tests/gen_smoke/` gets the generated sources, each replaced only where it changed.
  `$DIM8_BUILD/dim68_mw_geo<N>/` gets the lists: `model.blocks` (every block of the model), `withbase` (the
  blocks written beside the base in shard 0), `dropbelow` (the release blocks whose vertices of at most three
  legs the geo blocks give), `blocks3` and `blocksall` (the geo blocks with the leg cap and with every leg),
  `towers.txt` and `key`. The geo cache is `$GEO_VDIR` (`$DIM8_BUILD/vertices_geo<N>_mw`). The shards are
  `tests/gen_smoke/dim68_mw_geo<N>_s<k>_raw`, with `build/shards/dim68_mw_geo<N>/<k>.blocks` and `<k>.prov`,
  the record of which block gave which coefficient to which vertex of at most three legs. The logs go to
  `$DIM8_BUILD/logs/dim68_mw_geo<N>/` and `logs/shards/`. Each step ends with `SOURCESDONE`, `BLOCKSDONE`,
  `CACHEDONE`, `WRITEDONE`, `MERGEDONE` or `MODELDONE models/dim68_mw_geo<N>`, and otherwise exits 1 with the
  reason.
* What it refuses. N below 2, a basis other than the default (`DIM8_BASIS`), a checkout or cache in a
  synchronised folder such as Dropbox, which evicts files, a geo cache or list directory of another order,
  scheme or basis (their `cache.key` and `key`),
  and, before `write`, any block of the model that is stale or has no stamp
  (`validate/cache_source.py check --strict`).
* The scheme. The models of order N are built in the `{MW, MZ, GF}` scheme only, and `GEO_SCHEME=alpha` is
  refused. Supporting `{alpha, MZ, GF}` takes five things: its relations of order N
  (`gen/derive_geo.py N alpha`, which at N = 4 has not been run to its end), the base `base_geo<N>_alpha.fr`
  written from them, the derived `M_W` carried as a series (in this scheme a mass moves with the
  coefficients, see "Getting the orders right" in the README), the release caches of that scheme
  (`vertices6`, with `DIM8_L6BASES=base_inputscheme.fr`) and the two-point checks and export checks run
  on the result.

What must pass. `check` runs `examples/release_model.sh`, which for a model of order N adds these to the audits
of every release and leaves `models/` as it was when one fails. `check` needs the reference (`GEO_REF`), the
`.prov` files of the write, the UFO of the step `low` and MadGraph (`MG5_DIR`), and stops without them, and it
stops unless the merged model is the merge of the shards as they are now, each complete. It runs the release
with `DIM8_GEO_STRICT=1`, under which the release stops before it copies anything unless every check below
will run, and it prints `MODELDONE` exactly when the release exits 0, so that none can drop out unnoticed:

1. `validate/geo_export_check.py`, six checks on the files of the model, in Python, no MadGraph:
   * orders: every coupling is evaluated exactly at two values of `Lam` with the coefficients at random
     values, and must fall as the power of `1/Lambda^2` its `NP` order states, within the rounding of its own
     evaluation. A vertex of at most three legs may not exceed `NP = N`, a coupling may not use an undefined
     name or a coefficient of higher order than its own, and the released model must allow `NP <= N`.
     It fails with `GC_3 declared NP 1 but does not fall as 4^-1 (apparent order 2.000, ...)`.
   * four or more legs: no coupling of such a vertex above `NP = 2`, and none that depends, even through an
     internal parameter, on a parameter of order three or more (a tower coefficient, or `gw3`). It fails with
     `V_7 ['e+', 'e-', 'Z', 'Z']: GC_7 of order NP 3 on a vertex of 4 legs, above the 1/Lambda^4 its content
     is complete to`.
   * blocks: the card has the one scale `Lam`, each card entry once, and the blocks `DIM10`, ..., `DIM<2N+4>`
     hold exactly the coefficients of `gen/towers.py` (`the scales of the card are ['Lam', 'Lam6']: the model
     has the one scale Lam`, `block DIM10: members missing [...]`).
   * included once, by block: from the `.prov` files of the shards, each coefficient reaches each vertex of at
     most three legs from one block only, and each block is written in one shard. Written without
     `DIM8_DROPBELOW`, the model of order 2 fails it with 337 pairs such as `c8WH4D2x1 reaches the vertex
     {A H Z} from 2 blocks: ['G8op46', 'L8op621']`.
   * included once, against the reference: at `NP <= 2` every vertex equals that of `dim68_mw`, with every
     coefficient at a random value. One coupling of `Z e+ e-` doubled gives `relative difference 4.18e-01`.
   * at most three legs, order by order: every vertex of at most three legs has, at each NP order through N and
     with every coefficient at a random value, the value it has in the UFO of the step `low`. That is the blocks
     of the geo tree and the base written once more in one piece, with at most three legs and the plain cut of
     the writer (`DIM8_ORDERCUT`: the terms of NP order at most N, nothing else removed) in place of
     `validate/np_truncate.m`, and without the release blocks, `DIM8_DROPBELOW` or the join of the shards. Above
     `NP = 2` nothing else compares the written model with the cache it is written from. A UFO of thirteen tower
     blocks of order 4 passes it, with eight vertices compared at each of NP 2, 3 and 4. Written from those
     blocks cached without the corrections that the worker puts on them it fails with twelve values off,
     such as `('W+', 'W-', 'a') at NP 4: ... (relative difference 8.62e-01)`, with one such block among them it
     fails with six, and with the couplings of NP 3 taken off `H a a` by hand it fails on that vertex. What the
     two UFOs share, the flavour rules, FeynRules' merging and WriteUFO, this check does not see.

   `tests/test_geo_export.py` (`-v` prints the first problem of each case) runs the checks on a small model
   of order 3, in 22 cases on a copy broken so that the check it targets must fail (a record of the shards cut
   off before its end line among them), and in 8 on one that must pass.
2. From N = 3, `validate/geo_tower_check.py`: each member of a tower against its operator of dimension eight
   on every vertex of at most three legs without a Higgs boson, at `(v^2/2)^k L_d/L_8`. The two towers with no
   operator of dimension eight, those of `Q_{WH^6D^2}^{(5),(6)}` (`c<d>WH4D2x5`, `x6`), are compared at
   dimension 12 and above with their member of dimension ten, and at dimension ten with `Q_{WH^4D^2}^{(1),(2)}`
   on `W+ W- a`, `H Z a` and `H Z Z`, where the two have the same vertex at `(v^2/2) L10/L8` (the docstring
   derives it).
   No other check sees these two operators: they have no two-point term and no W-lepton vertex, so neither
   `validate/check_bilinears_geo.wls` nor `validate/geo_vertex_check.py` covers them, and their vertices
   `W+ W- Z` and `W+ W- H` have only the export checks above. The four-lepton operator that is new at
   dimension ten (`c<d>l4H2x3Fx00`, `Fx0E`, block `GEOGF`) has no operator of dimension eight either. It reaches
   these vertices through the relation of `G_F` alone, as `Q_{l^4H^2}^{(1)}` does and with the opposite sign, so
   its member of dimension ten is compared with `c8l4H2x1Fx00` (`Fx0E`) at `-(v^2/2) L10/L8` on every vertex
   without a Higgs boson. Each vertex is evaluated with the scale of its rounding (the Evaluator of
   `validate/geo_export_check.py`), and one within the rounding of its terms counts as none. This matters for
   `Q_{W^2H^4}^{(1)}`, `Q_{B^2H^4}^{(1)}` and their members, whose vertices without a Higgs boson cancel exactly,
   since at the vacuum they only rescale the kinetic term of the W or the B, which the inputs absorb. In the
   released model of order 4, 48 members have no such vertex, as their operators have none, and 230 are compared.
   `tests/test_geo_tower.py` breaks a stand-in eleven ways that the check must catch.
3. MadGraph imports the model and generates `e+ e- > z h NP<=2` and `z > e+ e- NP<=N`. Without MadGraph the
   release of a model of order N stops.

`tests/test_build_geo.sh` runs the steps `cachecheck`, `write`, `adopt`, `low`, `merge`, `check` and `all` on a
sandbox with `validate/cache_source.py` itself and stubs for wolframscript, the join, the release and MadGraph.
`write` stops until every tower block has passed `cachecheck`, which stops on a block that fails, that could not be
checked or that the check says nothing of, and a block computed again or whose source changed has no pass any more.
A resume that finds every shard complete writes nothing and keeps the plan. One that finds a shard without its UFO
or its key writes that shard alone, and one that finds a record missing or cut off records that shard alone. A shard
whose UFO lacks a file is written again, and a write that leaves its UFO spoiled (a file not copied, cut inside an
object or between two, a parameter missing) gets no key. A block whose source or vertex file changed has the shard
that holds it written again and no other, and a model file that every shard loads has them all written again.
`adopt` records the key of a shard whose files are older than its plan and refuses one whose block changed since, or
was put in place since with an older date, or whose UFO lacks a file. A resume after the block list or the blocks
written with the base changed stops. `merge` stops while a shard is not complete, and `check` releases only the
merge of the shards as they are. `low` writes the reference of check 6 as one shard of the geo blocks and writes
nothing when it is there, and `check` stops without it. `check` stops without MadGraph, follows the exit status of
the release even when its log cannot be written, and asks the release for every check, and the release stops before
it copies anything when one could not run. `all` started by a relative path from another directory runs its first
step. And `hpc/run_parts.sh` starts a split block afresh when the files of a run cut short are of another source
than the block has now, and keeps the parts when its merge leaves no block of the current source.
`tests/test_geo_sched.py` runs `hpc/geo_sched.py` on a sandbox with a fake `srun` and queue: a stale block is
built again, a block starts on a holder that ends early when no other has room, a block goes to no holder
that is not running or has less than ten minutes left, a holder still starting is waited for, and one that
stays between running and gone for `GEO_SCHED_GRACE` seconds and no longer, two preemptions under a block cost
it no retry, a `squeue` that fails is not a holder that has gone, a lock whose step or process has gone is
taken over and one whose step is in the queue is waited for, an older lock that names only its job is named
when the scheduler gives up, as is a block whose step keeps finding its lock held, `geo_sched.py alive` tells
each form of lock, the scheduler gives up when no holder is left and when nothing could start, and a log it
cannot write does not stop it.

The two-point checks test the sources rather than the exported files, and are run separately, after
`sources`: `hpc/twopoint_geo.sh bil|ferm N K [PREFIX]` runs `validate/check_bilinears_geo.wls` (the gauge and
Higgs two-point terms canonical through `t^N`) or `validate/check_fermion_masses_geo.wls` (the fermion masses
at their inputs through `t^N`) with the quadratic terms computed in K kernels at once. They share them through
`validate/twopoint_units.m`, which computes each block and each summand of the Standard-Model Lagrangian once
and keeps the result in `$DIM8_TWOPOINT_DIR` (default `build/twopoint`), keyed on its expression, the field
definitions and the code. A second run, or the run with PREFIX, reads them again. The report is
`logs/twopoint/<kind>_<N>.progress`, and the check passes when each residue falls by `2^(N+1)` per halving
of t (the last ratio above `10^-13` of the scale reaching 0.85 of it). PREFIX leaves out the blocks whose
names start with it (`T12` for the members of dimension twelve), and the check must then fail. At N = 4 the
Standard-Model part alone took 16618 s on one kernel, which is why the units are shared.
`validate/check_bilinears_geo.wls` caps the expansion of the unit of a block at two doublet fields, which keeps
every two-point term: the unit of `T12op28` takes 13.6 s where it took 15805 s, and is the same unit. The
bilinear check passes at N = 3 (every two-point residue falls as `t^4`) and at N = 4 (as `t^5`).
