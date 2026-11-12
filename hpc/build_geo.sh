#!/bin/bash
# The model of order N, dim68_mw_geo<N> (gen/towers.py): dimension six and eight in the {MW, MZ, GF} scheme, with
# the vertices of at most three legs complete to 1/Lambda^(2N) and the vertices of four or more legs those of the
# release, through 1/Lambda^4.  N = 2 gives the two- and three-point vertices of the release dim68_mw, N = 4 those
# through dimension twelve.
#
#   hpc/build_geo.sh sources N   the base of order N, the dimension-six and tower files and the block lists
#   hpc/build_geo.sh blocks N    the blocks of the geo tree into their cache
#   hpc/build_geo.sh cachecheck N  the cached tower blocks against their operators (validate/geo_cache_check.wls)
#   hpc/build_geo.sh write N     the UFO in shards (hpc/write_shards.sh), with the release caches
#   hpc/build_geo.sh low N       the vertices of at most three legs once more, in one piece, without the truncation
#   hpc/build_geo.sh merge N     the shards joined into tests/gen_smoke/dim68_mw_geo<N>_raw
#   hpc/build_geo.sh check N     the export checks and the release into models/dim68_mw_geo<N>, then MODELDONE
#   hpc/build_geo.sh all N       the seven in turn
#   hpc/build_geo.sh adopt N     the keys of the shards of a write made before shards had keys, where their files
#                                show what they were written from (hpc/write_shards.sh adopt), before a resume
#
# How each vertex enters.  The base of order N, base_geo<N>_mw.fr (gen/input_scheme.py --geo N, from the relations
# of gen/derive_geo.py), carries every series of the inputs, the field rotation, the Higgs quartic, the Yukawas and
# the gluon rescaling to t^N, t = 1/Lambda^2, and its Standard-Model vertices go into shard 0 with every leg.  The
# blocks of the geo tree are computed on that base: G6cl1..7, the dimension-six classes of dim6_geo.fr (gen/make_dim6.py
# --geo) with the corrections to order N - 1, G8op<i>, the 51 dimension-eight connection operators of gen_geo<N>.fr
# (gen/towers.py) to order N - 2, and T<d>op<i>, the members of dimension d = 10, ..., 2N + 4, to order N - (d - 4)/2,
# all with at most three legs (DIM8_MAXLEGS=3) except G6cl4 and the G8op of Q_{G^2H^4}^{(1)}: their gluon operators
# are vev-subtracted, so their vertices of four or more legs differ in form from the release's and these two are
# computed with every leg and replace L6cl4 and the L8op of Q_{G^2H^4}^{(1)} whole.  Every other block of the release
# dim68_mw is taken from the release caches ($DIM8_VDIR, $DIM8_VDIR6_MW, read only): the L8op of the connection
# operators and L6cl1,2,3,5,6,7 without their vertices of at most three legs, which their geo blocks give
# (DIM8_DROPBELOW), and the others whole, which have no vertex of at most three legs in the default basis
# (tests/test_geo_basis.py).  The writer keeps the pieces of each vertex through NP = N when it has at most three
# legs and through NP = 2 when it has four or more (validate/np_truncate.m, DIM8_GEO_N), so the Standard-Model
# quartics too are those of the release, through 1/Lambda^4.
#
# What the steps write.  sources: tests/gen_smoke/base_geo<N>_mw.fr, dim6_geo.fr, gen_geo<N>.fr with its index
# gen_geo<N>.json and flavour rules gen_geo<N>_flavour_rules.m, each moved in by rename only where it changed, so that
# a worker reading one keeps its copy, and the lists of $DIM8_BUILD/dim68_mw_geo<N>/: model.blocks (the blocks of the
# model), withbase (those written with the base in shard 0: the geo blocks, the dimension-six classes and the
# operators of the input relations), dropbelow, blocks3 and blocksall (the geo blocks computed with at most three legs
# and with every leg).  gen/derive_geo.py writes gen/input_scheme_formulae_geo<N>_mw.json first if it is missing
# (sympy, minutes at N = 3 and hours at N = 4).  blocks: the cache $GEO_VDIR (default $DIM8_BUILD/vertices_geo<N>_mw),
# keyed on the order, scheme and basis by its file cache.key, which the later steps compare.  A block whose stamp
# (validate/cache_source.py) is that of its current source is not computed again, and a stale one is.  cachecheck:
# validate/geo_cache_check.wls on every block of gen_geo<N>.json (G8op<i>, T<d>op<i>), in GEO_PAR kernels at once.  It
# evaluates the Module of each block whole and compares the coupling of every structure of its vertices of at most
# three legs with the cached block, NP order by NP order through N.  The worker caches these blocks term by term and
# puts the corrections of the base on them itself, and a block cached without them is right at its own order and wrong
# above it, where no other check looks: the two-point checks evaluate the Modules and not the cache, and the export
# check compares the model with the release at NP <= 2 only.  A block that passes is recorded in
# $DIM8_BUILD/dim68_mw_geo<N>/cachecheck with the content of its vertex file, the stamp of its source and the check it
# passed, and a block whose record is of the cache and source it has now is not checked again.  write stops unless
# every tower block has such a record.  write: the shards in tests/gen_smoke/dim68_mw_geo<N>_s<k>_raw, with their
# block lists, their keys (what each was written from) and the provenance of their vertices of at most three legs in
# build/shards/dim68_mw_geo<N>/ (<k>.blocks, <k>.key, <k>.prov), after validate/cache_source.py has found every block
# of the model stamped with its current source: a stale block or one without a stamp stops it.  merge: the join, with
# the record of the shards it joined (build/shards/dim68_mw_geo<N>/merged).  low: the blocks of the geo tree and the
# base written as one shard of their own, tests/gen_smoke/dim68_mw_geo<N>_low_s0_raw, with at most three legs and the
# plain cut of the writer at NP <= N (DIM8_ORDERCUT) in place of validate/np_truncate.m, without the release blocks,
# DIM8_DROPBELOW or the join.  It is the reference of export check 6, which compares the vertices of at most three
# legs of the model with it NP order by NP order through N: the stage from the cache to the written model, which no
# other check sees above NP 2.  It has its key as a shard has, and is written again when a block changes.  check:
# examples/release_model.sh, which for a model of order N runs validate/geo_export_check.py on the model it is about
# to release, with the provenance of the shards and the reference $GEO_REF, and has MadGraph import it and generate z
# > e+ e- at NP<=N. check stops without the reference, the provenance, the reference of check 6 or MadGraph, and when
# the merged model is not the merge of the shards as they are now, each complete, and any failure leaves the release
# as it was.  It runs the release with DIM8_GEO_STRICT=1, under which the release refuses to start unless every check
# will run, so that MODELDONE, which check prints when the release exits 0, means that each check ran and passed and
# models/dim68_mw_geo<N> is the new model.
#
# Settings, from the environment, with their defaults:
#   DIM8_ROOT      the checkout written into (the directory above this script), not in Dropbox, which evicts files
#   DIM8_BUILD     caches, lists and logs (~/dim8auto_build), the logs in $DIM8_BUILD/logs/dim68_mw_geo<N>/
#   GEO_VDIR       the cache of the geo blocks ($DIM8_BUILD/vertices_geo<N>_mw)
#   DIM8_VDIR      the release cache of dimension eight ($DIM8_ROOT/build/vertices), as for ./dim8
#   DIM8_VDIR6_MW  the release cache of dimension six in the {MW, MZ, GF} scheme (${DIM8_VDIR}6_mw), as for ./dim8
#   GEO_SCHEME     mw, the only scheme the models of order N are built in: alpha is refused (hpc/README.md says why)
#   WS             wolframscript (the one on the PATH), hpc/ws_retry.sh on a cluster
#   GEO_RUN        local (each kernel here) or slurm (each step through $GEO_SRUN, with -c cores appended)
#   GEO_SRUN       the step command of GEO_RUN=slurm ("srun -N1 -n1"); "srun --jobid=<job> --overlap -N1 -n1" runs
#                  inside a held allocation
#   GEO_PAR        the kernels of the blocks with the leg cap, those of cachecheck, and the shards written at once
#                  (2), each a Mathematica licence seat, and the two blocks with every leg run beside them, two
#                  seats each
#   GEO_SCHED      a file of "<job> <cores>" lines: blocks spreads the geo blocks over those slurm jobs, heaviest
#                  first, the heavy ones split over kernels (hpc/geo_sched.py), in place of GEO_PAR workers
#   GEO_TIMES      the cache of an earlier build of the same order, whose status lines give hpc/geo_sched.py the
#                  times of the blocks (without it every block counts an hour on one kernel)
#   GEO_SCHED_IDLE seconds hpc/geo_sched.py waits with nothing running and nothing it can start before it gives up
#                  with exit 1 (3600), and at once when no holder is running, waiting in the queue or coming back
#   GEO_SCHED_GRACE seconds a holder between running and gone (starting, ending, requeued, suspended, preempted, or
#                  not to be read from squeue) counts as coming back, after it was last running or waiting (900)
#   GEO_SHARDS     the shards of write besides shard 0 (40)
#   GEO_FRESH      1 (default): write plans the shards afresh and removes those of an earlier write and its merged
#                  model.  0 resumes a write cut short with its plan: it skips the shards that are complete, those
#                  whose key is the one they would have now, writes the others again, and records the provenance of a
#                  complete shard whose record is missing or cut off (hpc/write_shards.sh)
#   GEO_TIMEOUT    seconds a kernel of blocks may run (72000), where timeout(1) exists
#   GEO_REF        the reference of the export check at NP <= 2 ($DIM8_ROOT/models/dim68_mw, the release unpacked)
#   GEO_CHECK_MEM  the memory of the merge and check steps under GEO_RUN=slurm (32G): MadGraph's first import of a
#                  whole model takes about 8 GB and the reference comparison holds both models' couplings
#   DIM8_HERM      0 (default here): the Hermiticity check of the worker is deferred, and tests/test_towers.py checks the
#                  members' Hermiticity on their terms
#   MG5_DIR        MadGraph, which check needs: a model of order N is not released without its import test
#   DIM8_NUMPY_PY  as for examples/release_model.sh
#
# On a cluster, load its modules (Mathematica, a python3 with numpy and sympy) before running this, and run the
# step itself where a long job may run (a login node only starts the steps).  The blocks are the short part: the 58
# geo blocks of N = 2 took 1.6 core hours and the 164 of N = 4 took 7.6.  The write is the long step at every order,
# since each shard writes every parameter of the model.  At N = 4, with one block a shard (GEO_SHARDS at the number
# of blocks or more), the 661 shards took 120 core hours: five and a half minutes for the median shard, 54 minutes
# for shard 0, which holds the base and the blocks written with it, and 2.7 hours for the heaviest.  With a hundred
# kernels at once the write then takes about three hours, set by that shard, and on two kernels two and a half days.
set -u
step=${1:?usage: hpc/build_geo.sh sources|blocks|cachecheck|write|low|merge|check|all|adopt N}
# this script by its absolute path, which `all` and hpc/geo_sched.py call again after the cd below
self=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
N=${2:?the order N}
root=$(cd "${DIM8_ROOT:-$(dirname "$self")/..}" && pwd) || exit 1
build=${DIM8_BUILD:-$HOME/dim8auto_build}
scheme=${GEO_SCHEME:-mw}
case $N in [2-9]|[1-9][0-9]) ;; *) echo "N is the order of the model, 2 or more: $N"; exit 2 ;; esac
# The {alpha, MZ, GF} scheme is refused until it is supported end to end: its relations of order 4 are not derived
# (gen/derive_geo.py 4 alpha did not finish), and its base, its release caches (dim68_is) and the two-point checks
# have not been run with the geo blocks.  hpc/README.md lists what it takes.
[ "$scheme" = mw ] || { echo "the models of order N are built in the {MW, MZ, GF} scheme only (GEO_SCHEME=mw), not $scheme"; exit 2; }
# the towers are those of the default basis, whose two- and three-point functions are those of the geoSMEFT
[ "${DIM8_BASIS:-geo}" = geo ] || { echo "the models of order N are built in the default basis only, not DIM8_BASIS=$DIM8_BASIS"; exit 2; }
case "$root$build" in *Dropbox*|*CloudStorage*) echo "the checkout and the caches may not live in Dropbox: $root, $build"; exit 2 ;; esac
NAME=dim68_${scheme}_geo$N
L=$build/$NAME
LOG=$build/logs/$NAME
GV=${GEO_VDIR:-$build/vertices_geo${N}_${scheme}}
REL8=${DIM8_VDIR:-$root/build/vertices}
REL6=${DIM8_VDIR6_MW:-${REL8%/}6_mw}
GEO_RUN=${GEO_RUN:-local}; GEO_SRUN=${GEO_SRUN:-srun -N1 -n1}; GEO_PAR=${GEO_PAR:-2}; GEO_SHARDS=${GEO_SHARDS:-40}
GEO_TIMEOUT=${GEO_TIMEOUT:-72000}; GEO_CHECK_MEM=${GEO_CHECK_MEM:-32G}
KEY="order $N, scheme $scheme, basis geo"
export DIM8_ROOT=$root WS=${WS:-wolframscript} PYTHONDONTWRITEBYTECODE=1 DIM8_NUMPY_PY=${DIM8_NUMPY_PY:-python3} \
       DIM8_BASE="base_geo${N}_${scheme}.fr;dim6_geo.fr;gen_geo${N}.fr" DIM8_HERM=${DIM8_HERM:-0}
mkdir -p "$L" "$LOG"
cd "$root" || exit 1

on() {   # on CORES COMMAND...: the command here, or as a slurm step on CORES cores
  local c=$1; shift
  if [ "$GEO_RUN" = slurm ]; then $GEO_SRUN -c "$c" "$@"; else "$@"; fi
}
onm() {   # the same with the memory of GEO_CHECK_MEM
  local c=$1; shift
  if [ "$GEO_RUN" = slurm ]; then $GEO_SRUN -c "$c" --mem="$GEO_CHECK_MEM" "$@"; else "$@"; fi
}
shard_env() {   # the environment of the writer of the shards, which write, merge and check share, since the key of
  # each shard (hpc/write_shards.sh) is taken in it
  export DIM8_VDIR="$GV;$REL8;$REL6" DIM8_L6BASES=base_inputscheme_${scheme}.fr DIM8_EXTRA_RULES=gen_geo${N}_flavour_rules.m \
         DIM8_DROPBELOW=$L/dropbelow DIM8_TRUNCATE=1 DIM8_GEO_N=$N
}
low_env() {   # the environment the reference of export check 6 is written in (the step low), and its key taken in:
  # the geo cache alone, at most three legs, the plain order cut in place of the truncation
  export DIM8_VDIR="$GV" DIM8_EXTRA_RULES=gen_geo${N}_flavour_rules.m DIM8_ORDERCUT=$N DIM8_MAXLEGS=3
  unset DIM8_TRUNCATE DIM8_DROPBELOW DIM8_L6BASES DIM8_GEO_N
}
lim() {   # a kernel with the time limit, where timeout(1) exists (macOS has none)
  if command -v timeout > /dev/null; then timeout "$GEO_TIMEOUT" "$@"; else "$@"; fi
}
state() {   # the state of block $1 in the geo cache, as the worker reads it (validate/cache_source.py)
  python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import cache_source as C; print(C.state(sys.argv[2], sys.argv[3]))' \
    "$root/validate" "$GV" "$1" 2>/dev/null
}
keyed() {   # the geo cache is that of this order, scheme and basis, and a new one is keyed
  mkdir -p "$GV"
  if [ -f "$GV/cache.key" ]; then
    [ "$(cat "$GV/cache.key")" = "$KEY" ] || { echo "$GV holds the blocks of $(cat "$GV/cache.key"), not $KEY: set GEO_VDIR"; exit 2; }
  else
    echo "$KEY" > "$GV/cache.key"
  fi
}
lists() {   # the lists of the sources step, of this order
  for f in model.blocks withbase dropbelow blocks3 blocksall key; do
    [ -f "$L/$f" ] || { echo "no $L/$f: run hpc/build_geo.sh sources $N first"; exit 1; }
  done
  [ "$(cat "$L/key")" = "$KEY" ] || { echo "$L holds the lists of $(cat "$L/key"), not $KEY"; exit 2; }
}
alive() {   # whether the holder a lock names still runs the block, as hpc/geo_sched.py alive tells it: its slurm step
  # still in the queue and its process, where this host can see it, still there.  One that cannot be told counts as there
  [ -n "$1" ] || return 1
  python3 "$root/hpc/geo_sched.py" alive "$1"
  [ $? != 1 ]
}
lock() {   # one runner per block, whichever scheduler starts it.  The lock names the slurm step and the host:pid that
  # run the block, "<job>.<step> <host>:<pid>" ("- <host>:<pid>" outside slurm), and is taken over once they have
  # gone: a step killed without its EXIT trap leaves its lock, and the job it ran in may stay in the queue for hours.
  # It is renamed into place with the holder already in it, so that no reader sees it empty (mv -T: GNU, as on a
  # cluster)
  local l=$GV/$1.lock t=$GV/$1.lock.$$ s=${SLURM_STEP_ID:-${SLURM_STEPID:-}} me held
  # a step of srun has a small number, and a job's own script none or one of slurm's reserved ones, which squeue -s
  # does not list under it: the lock then names the job alone, with the process
  case $s in ''|*[!0-9]*|??????????*) s= ;; esac
  me=${SLURM_JOB_ID:+$SLURM_JOB_ID${s:+.$s}}; me="${me:--} $(hostname):$$"
  rm -rf "$t"; mkdir "$t" && echo "$me" > "$t/job" || return 1
  if ! mv -T "$t" "$l" 2> /dev/null; then
    held=$(cat "$l/job" 2> /dev/null)
    if alive "$held"; then rm -rf "$t"; echo "$1 is run by $held"; return 1; fi
    rm -rf "$l"
    mv -T "$t" "$l" 2> /dev/null || { rm -rf "$t"; echo "$1: the lock was taken"; return 1; }
  fi
  trap "rm -rf '$l'" EXIT
}

cache_gate() {   # the passes of validate/geo_cache_check.wls, in $L/cachecheck: one line a tower block (the blocks of
  # gen_geo<N>.json) with the content of its vertex file, the stamp of its source and the check, as they were when
  # the check that passed it started.  cache_gate todo K deals the blocks without a pass of what they have now to
  # $L/c<k>.list, k < K, the largest first into the lightest; cache_gate record reads the logs of the K kernels and
  # records the blocks that passed; cache_gate checked exits 0 when every block has a pass of what it has now
  python3 - "$1" "$root" "$N" "$GV" "$L" "$LOG" "${2:-0}" <<'EOF'
import glob, hashlib, json, os, re, sys
mode, root, N, gv, L, log, K = sys.argv[1:7] + [int(sys.argv[7])]
sys.path.insert(0, os.path.join(root, "validate"))
import cache_source as C


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def now():
    """block -> (its line of the record as it would be now, the size of its vertex file)"""
    check = sha(os.path.join(root, "validate", "geo_cache_check.wls"))
    out = {}
    for e in json.load(open(os.path.join(root, "tests", "gen_smoke", f"gen_geo{N}.json"))):
        b = e["block"]
        files = [os.path.join(gv, b + x) for x in (".mx", ".wxf") if os.path.exists(os.path.join(gv, b + x))]
        try:
            src = C.source_hash(b)
        except (KeyError, OSError):
            src = "no-source"
        out[b] = ("\t".join([b, sha(files[0]) if len(files) == 1 else "no-file", src, check]),
                  os.path.getsize(files[0]) if len(files) == 1 else 0)
    return out


record = os.path.join(L, "cachecheck")
passed = {x.split("\t")[0]: x for x in open(record).read().splitlines() if x.strip()} if os.path.exists(record) else {}
if mode == "checked":
    cur = now()
    left = [b for b in cur if passed.get(b) != cur[b][0]]
    if left:
        print(f"{len(left)} of {len(cur)} tower blocks have no pass of validate/geo_cache_check.wls for the cache and the "
              f"source they have now: {' '.join(left[:20])}{' ...' if len(left) > 20 else ''}")
    sys.exit(1 if left else 0)
if mode == "todo":
    cur = now()
    lost = [b for b in cur if "\tno-file\t" in cur[b][0]]
    if lost:
        sys.exit(f"tower blocks that are not in {gv}, or twice: {' '.join(lost[:20])}")
    todo = sorted((b for b in cur if passed.get(b) != cur[b][0]), key=lambda b: -cur[b][1])
    for f in glob.glob(os.path.join(L, "c[0-9]*.list")) + glob.glob(os.path.join(L, "c[0-9]*.rc")):
        os.remove(f)
    load, lists = [0]*K, [[] for _ in range(K)]
    for b in todo:
        k = min(range(K), key=lambda i: (load[i], len(lists[i])))
        load[k] += cur[b][1]
        lists[k].append(b)
    for k in range(K):
        if lists[k]:
            open(os.path.join(L, f"c{k}.list"), "w").write(",".join(lists[k]))
    # what each block is now, for the passes of the kernels that start now
    open(os.path.join(L, "cachecheck.ids"), "w").write("".join(cur[b][0] + "\n" for b in cur))
    print(f"{len(cur)} tower blocks, {len(cur) - len(todo)} with a pass of the cache and the source they have now, "
          f"{len(todo)} to check in {sum(1 for x in lists if x)} kernels")
    sys.exit(0)
# record: a pass counts for the block as it was when its check started, and only a PASS line of this order
ids = {x.split("\t")[0]: x for x in open(os.path.join(L, "cachecheck.ids")).read().splitlines()}
bad = 0
for f in sorted(glob.glob(os.path.join(L, "c[0-9]*.list"))):
    k = re.search(r"c(\d+)\.list$", f).group(1)
    out = os.path.join(log, f"cachecheck_w{k}.log")
    text = open(out, errors="replace").read() if os.path.exists(out) else ""
    said = dict(re.findall(rf"^\[cachecheck\] (\S+) order {N}: (PASS|FAIL|NOT CHECKED)", text, re.M))
    for b in open(f).read().split(","):
        if said.get(b) == "PASS":
            passed[b] = ids[b]
        else:
            bad += 1
            line = re.search(rf"^\[cachecheck\] {re.escape(b)} order {N}: .*$", text, re.M)
            print(line.group(0)[:300] if line else f"[cachecheck] {b} order {N}: no line in {out}")
open(record + ".new", "w").write("".join(passed[b] + "\n" for b in sorted(passed)))
os.replace(record + ".new", record)
sys.exit(1 if bad else 0)
EOF
}

case $step in
sources)
  F=gen/input_scheme_formulae_geo${N}_${scheme}.json
  if [ ! -f "$F" ]; then
    echo "$F is missing: gen/derive_geo.py $N $scheme writes it, log in $LOG/derive.log"
    on 1 python3 gen/derive_geo.py "$N" "$scheme" > "$LOG/derive.log" 2>&1 || { echo "gen/derive_geo.py failed, see $LOG/derive.log"; exit 1; }
  fi
  T=$L/sources.tmp; rm -rf "$T"; mkdir -p "$T"
  python3 gen/input_scheme.py tests/gen_smoke/base.fr "$T/base_geo${N}_${scheme}.fr" "$scheme" --geo "$N" || exit 1
  python3 gen/make_dim6.py --geo "$T/dim6_geo.fr" || exit 1
  python3 gen/towers.py "$N" -o "$T/gen_geo${N}.fr" > "$L/towers.txt" || exit 1
  for f in base_geo${N}_${scheme}.fr dim6_geo.fr gen_geo${N}.fr gen_geo${N}.json gen_geo${N}_flavour_rules.m; do
    if cmp -s "$T/$f" "tests/gen_smoke/$f"; then echo "$f unchanged"; else mv "$T/$f" "tests/gen_smoke/$f"; echo "$f written"; fi
  done
  rm -rf "$T"
  python3 - "$N" "$L" "$root" <<'EOF' || exit 1
import json, os, re, sys
N, L, root = int(sys.argv[1]), sys.argv[2], sys.argv[3]
# the blocks of the release dim68_mw and those written with its base, as ./dim8 rebuild lists them
sys.argv = ["dim8"]
g = {"__name__": "dim8lib", "__file__": os.path.join(root, "dim8")}
exec(open(os.path.join(root, "dim8")).read().split("def main():")[0], g)
idx = json.load(open(os.path.join(root, "docs", "block_index.json")))
release = g["_release_blocks"](idx, True)
withbase_rel = set(g["_input_scheme_blocks"]()) | set(g["_dim6_blocks"]())
import towers
geo = json.load(open(os.path.join(root, "tests", "gen_smoke", f"gen_geo{N}.json")))
d6 = open(os.path.join(root, "tests", "gen_smoke", "dim6_geo.fr")).read()
G6 = re.findall(r'"(\w+)"', re.search(r"DIM6\$Classes = \{([^}]*)\}", d6).group(1))
by_wc = {w: e["block"] for e in idx for w in e["wcs"]}
# each geo block of dimension six or eight, and the release block whose vertices of at most three legs it gives
twin = {b: "L6" + b[2:] for b in G6}
twin.update({e["block"]: by_wc[e["wcs"][0]] for e in geo if e["block"].startswith("G8op")})
lost = sorted(t for t in twin.values() if t not in release)
if lost:
    sys.exit(f"the release blocks {lost} are not blocks of dim68_mw")
# the blocks of the vev-subtracted gluon operators are computed with every leg and replace their release blocks whole
full = {b for b in G6 if re.search(rf"^{b}\s*:=[^;]*\bcHG\b", d6, re.M)}
full |= {e["block"] for e in geo if e["wcs"][0] == "c8" + towers.GLUON_KINETIC}
if len(full) != 2:
    sys.exit(f"expected the two blocks of the gluon operators cHG and c8{towers.GLUON_KINETIC}, found {sorted(full)}")
GT = G6 + [e["block"] for e in geo]
whole = {twin[b] for b in full}
out = [b for b in release if b not in whole] + GT
withbase = [b for b in sorted(withbase_rel, key=g["_bkey"]) if b not in whole] + GT
drop = [twin[b] for b in twin if b not in full]
# each list written only where it changed, as the sources above, so that its date says when it last did
# (hpc/write_shards.sh adopt reads the date of dropbelow)
for name, rows in (("model.blocks", out), ("withbase", withbase), ("dropbelow", drop),
                   ("blocks3", [b for b in GT if b not in full]), ("blocksall", sorted(full))):
    p, text = os.path.join(L, name), "\n".join(rows) + "\n"
    if not os.path.exists(p) or open(p).read() != text:
        open(p, "w").write(text)
print(f"{len(out)} blocks ({len(GT)} of the geo tree), {len(withbase)} with the base, {len(drop)} release blocks "
      f"without their vertices of at most three legs, {sorted(whole)} left out for {sorted(full)}, which have every leg")
EOF
  echo "$KEY" > "$L/key"
  echo "SOURCESDONE"
  ;;
blocks)
  lists; keyed
  export DIM8_VDIR=$GV
  if [ -n "${GEO_SCHED:-}" ]; then
    GEO_N=$N GEO_LISTS=$L GEO_VDIR=$GV GEO_LOG=$LOG python3 hpc/geo_sched.py run "$N" || exit 1
  else
    # the blocks with every leg each on a kernel of its own, the others dealt round robin to GEO_PAR kernels
    python3 - "$L" "$GEO_PAR" <<'EOF'
import sys
L, p = sys.argv[1], int(sys.argv[2])
capped = [b.strip() for b in open(f"{L}/blocks3") if b.strip()]
for k in range(p):
    open(f"{L}/w{k}.list", "w").write(",".join(capped[k::p]))
EOF
    for b in $(cat "$L/blocksall"); do
      on 2 $(command -v timeout > /dev/null && echo timeout "$GEO_TIMEOUT") \
        "$WS" -file validate/fr_worker.wls "$b," 0 0 1 10000 > "$LOG/blocks_$b.log" 2>&1 &
    done
    for k in $(seq 0 $((GEO_PAR - 1))); do
      [ -s "$L/w$k.list" ] || continue
      on 1 env DIM8_MAXLEGS=3 $(command -v timeout > /dev/null && echo timeout "$GEO_TIMEOUT") \
        "$WS" -file validate/fr_worker.wls "$(cat "$L/w$k.list")," 0 0 0 10000 > "$LOG/blocks_w$k.log" 2>&1 &
    done
    wait
  fi
  left=$(for b in $(cat "$L/blocks3" "$L/blocksall"); do [ "$(state "$b")" = current ] || echo "$b"; done)
  [ -z "$left" ] || { echo "blocks not built from their current source:" $left "(logs in $LOG)"; exit 1; }
  echo "BLOCKSDONE"
  ;;
cachecheck)
  lists; keyed
  [ -f validate/geo_cache_check.wls ] || { echo "no validate/geo_cache_check.wls in $root"; exit 1; }
  export DIM8_VDIR=$GV
  cache_gate todo "$GEO_PAR" || { echo "stopped: run hpc/build_geo.sh blocks $N first"; exit 1; }
  for k in $(seq 0 $((GEO_PAR - 1))); do
    [ -s "$L/c$k.list" ] || continue
    ( on 1 env DIM8_PROGRESS="$LOG/cachecheck_w$k.progress" $(command -v timeout > /dev/null && echo timeout "$GEO_TIMEOUT") \
        "$WS" -file validate/geo_cache_check.wls "$N" "$(cat "$L/c$k.list")" "$GV" > "$LOG/cachecheck_w$k.log" 2>&1
      echo $? > "$L/c$k.rc" ) &
  done
  wait
  # every kernel must end with exit 0 (1: a block fails, 2: one could not be checked) and every block with its PASS
  # line.  A block that passed is recorded whatever the others did, so that the next run checks the others alone
  bad=0
  cache_gate record || bad=1
  for k in $(seq 0 $((GEO_PAR - 1))); do
    [ -s "$L/c$k.list" ] || continue
    rc=$(cat "$L/c$k.rc" 2> /dev/null)
    [ "$rc" = 0 ] || { echo "the kernel of $L/c$k.list ended with exit ${rc:-unknown}, see $LOG/cachecheck_w$k.log"; bad=1; }
  done
  [ $bad = 0 ] || { echo "stopped: the cached blocks above are not those of their operators (FAIL: rebuild them, hpc/build_geo.sh blocks $N after removing their files from $GV) or could not be checked (logs in $LOG/cachecheck_w<k>.log)"; exit 1; }
  cache_gate checked || { echo "stopped: blocks changed while they were checked: run hpc/build_geo.sh cachecheck $N again"; exit 1; }
  echo "CACHEDONE"
  ;;
block)
  # one block for hpc/geo_sched.py: hpc/build_geo.sh block N BLOCK full | PARTS EXPANSIONS [CHUNK]
  lists; keyed
  b=${3:?block}; shift 3
  export DIM8_VDIR=$GV
  [ "$(state "$b")" = current ] && { echo "$b is built from its current source already"; exit 0; }
  lock "$b" || exit 3
  if [ "${1:-}" = full ]; then
    lim "$WS" -file validate/fr_worker.wls "$b," 0 0 1 10000
  elif [ "${1:-1}${2:-1}" != 11 ]; then
    env DIM8_MAXLEGS=3 DIM8_PARTS_LOG="$LOG/parts" DIM8_RECURSION=10000 ${3:+DIM8_CHUNK=$3} bash hpc/run_parts.sh "$b" "$1" "$2"
  else
    lim env DIM8_MAXLEGS=3 "$WS" -file validate/fr_worker.wls "$b," 0 0 0 10000
  fi
  [ "$(state "$b")" = current ]
  ;;
write)
  lists; keyed
  shard_env
  # every block from the source it has now, and none without a stamp, which would say nothing of its source
  python3 validate/cache_source.py check "$DIM8_VDIR" "$L/model.blocks" --strict \
    || { echo "stopped: rebuild the blocks above (hpc/build_geo.sh blocks $N for the geo tree, ./dim8 rebuild for the release)"; exit 1; }
  # and every tower block the one its operator gives, to every order: no check of the written model sees that above NP 2
  cache_gate checked || { echo "stopped: run hpc/build_geo.sh cachecheck $N"; exit 1; }
  S=build/shards/$NAME
  if [ "${GEO_FRESH:-1}" = 1 ] || ! ls "$S"/*.blocks > /dev/null 2>&1; then
    # the shards, the logs and the merged model of an earlier write go, so that no later step takes them for this one
    rm -rf tests/gen_smoke/${NAME}_s[0-9]*_raw tests/gen_smoke/${NAME}_raw logs/shards/${NAME}_[0-9]*.log logs/shards/${NAME}.done
    bash hpc/write_shards.sh plan "$NAME" "$L/model.blocks" $((GEO_SHARDS + 1)) "$L/withbase" || exit 1
  else
    # a resume keeps the plan, which a new one could deal differently, and the shards that are complete, those
    # written from the blocks and the base there are now (hpc/write_shards.sh complete).  The plan must still be
    # of this block list, each block in one shard and those written with the base in shard 0
    python3 - "$S" "$L/model.blocks" "$L/withbase" <<'EOF' || { echo "stopped: $S is the plan of another block list: GEO_FRESH=1 writes afresh"; exit 1; }
import collections, glob, sys
S, blocks, withbase = sys.argv[1:4]
want = [b.strip() for b in open(blocks) if b.strip()]
have = collections.Counter(b.strip() for f in glob.glob(f"{S}/*.blocks") for b in open(f) if b.strip())
twice, lost, extra = [b for b, c in have.items() if c > 1], set(want) - set(have), set(have) - set(want)
base = {b.strip() for b in open(withbase) if b.strip()} & set(want)
zero = {b.strip() for b in open(f"{S}/0.blocks") if b.strip()}
print(f"resuming the plan of {len(glob.glob(f'{S}/*.blocks'))} shards in {S}")
for what, bs in (("in two shards", twice), ("in no shard", lost), ("not in the model", extra),
                 ("to be written with the base and not in shard 0", base - zero), ("in shard 0 and not to be", zero - base)):
    if bs:
        print(f"  blocks {what}: {sorted(bs)[:10]}")
sys.exit(1 if twice or lost or extra or base != zero else 0)
EOF
  fi
  n=$(ls "$S"/*.blocks | wc -l)
  on $((GEO_PAR + 3)) bash hpc/write_shards.sh run "$NAME" 0 $((n - 1)) "$GEO_PAR"
  bad=$(for k in $(seq 0 $((n - 1))); do bash hpc/write_shards.sh complete "$NAME" "$k" || echo "$k"; done)
  [ -z "$bad" ] || { echo "shards not complete (not written, not recorded, or from other blocks or another base than now):" $bad "(logs in logs/shards/${NAME}_<k>.log)"; exit 1; }
  echo "WRITEDONE"
  ;;
low)
  lists; keyed
  cache_gate checked || { echo "stopped: run hpc/build_geo.sh cachecheck $N"; exit 1; }
  low_env
  cat "$L/blocks3" "$L/blocksall" > "$L/low.blocks"
  S=build/shards/${NAME}_low
  # one shard, of the base and every block of the geo tree.  Its plan is made again only when the list changed, and
  # the shard is written when it is not complete: when a block, a model file or a setting is not what its key says
  cmp -s "$L/low.blocks" "$S/0.blocks" 2> /dev/null \
    || bash hpc/write_shards.sh plan "${NAME}_low" "$L/low.blocks" 1 "$L/low.blocks" || exit 1
  on 2 bash hpc/write_shards.sh run "${NAME}_low" 0 0 1
  bash hpc/write_shards.sh complete "${NAME}_low" 0 \
    || { echo "stopped: the reference of check 6 is not written, see logs/shards/${NAME}_low_0.log"; exit 1; }
  echo "LOWDONE"
  ;;
merge)
  lists
  # the environment of the write, from which hpc/write_shards.sh tells that each shard is complete before it joins them
  shard_env
  onm 2 bash hpc/write_shards.sh merge "$NAME" || exit 1
  echo "MERGEDONE"
  ;;
check)
  lists
  raw=tests/gen_smoke/${NAME}_raw
  [ -f "$raw/vertices.py" ] || { echo "no $raw: run hpc/build_geo.sh merge $N first"; exit 1; }
  # every check runs here: the reference of check 5, the provenance of check 4 and MadGraph are all required
  ref=${GEO_REF:-$root/models/dim68_$scheme}
  [ -f "$ref/vertices.py" ] || { echo "no reference model $ref: unpack the release, or set GEO_REF"; exit 1; }
  ls "$root/build/shards/$NAME"/*.prov > /dev/null 2>&1 || { echo "no provenance in build/shards/$NAME: run hpc/build_geo.sh write $N"; exit 1; }
  [ "${DIM8_SKIP_MG5_IMPORT:-0}" != 1 ] && [ -x "${MG5_DIR:-}/bin/mg5_aMC" ] \
    || { echo "set MG5_DIR to a MadGraph (with python3.11 on the PATH): the check imports the model (now '${MG5_DIR:-}')"; exit 1; }
  # the model checked is the merge of the shards as they are, each written from the blocks and base there are now
  shard_env
  bash hpc/write_shards.sh merged "$NAME" || { echo "stopped: $raw is not the merge of the shards as they are: run hpc/build_geo.sh write $N and merge $N"; exit 1; }
  # the reference of check 6, written from the blocks and the base there are now
  ( low_env; bash hpc/write_shards.sh complete "${NAME}_low" 0 ) \
    || { echo "stopped: no reference of check 6 written from the blocks there are now: run hpc/build_geo.sh low $N"; exit 1; }
  export DIM8_GEO_LOW=$root/tests/gen_smoke/${NAME}_low_s0_raw
  # DIM8_GEO_STRICT: the release refuses to start unless every check will run, and moves the model into models/
  # only once all have passed, so that its exit status is the verdict and no check can drop out unnoticed
  export DIM8_GEO_REF=$ref DIM8_GEO_PROV=$root/build/shards/$NAME DIM8_GEO_BLOCKS=$L/model.blocks DIM8_GEO_STRICT=1
  onm 2 bash examples/release_model.sh "$raw" "$NAME" 2>&1 | tee "$LOG/check.log"
  [ "${PIPESTATUS[0]}" = 0 ] || { echo "stopped: the export checks or the release failed, see $LOG/check.log"; exit 1; }
  echo "MODELDONE models/$NAME"
  ;;
all)
  for s in sources blocks cachecheck write low merge check; do bash "$self" "$s" "$N" || exit 1; done
  ;;
adopt)
  # a shard written before shards had keys has none, and a resume writes it again unless its files show that it was
  # written from what there is now: each of them older than its plan.  Run it with the settings of that write
  # (DIM8_TRUNCATE and the rest of shard_env are this script's own), which nothing else records
  lists
  shard_env
  S=build/shards/$NAME
  ls "$S"/*.blocks > /dev/null 2>&1 || { echo "no plan in $S: nothing to adopt"; exit 1; }
  n=$(ls "$S"/*.blocks | wc -l)
  bash hpc/write_shards.sh adopt "$NAME" 0 $((n - 1)) \
    || { echo "the shards above keep no key: GEO_FRESH=0 hpc/build_geo.sh write $N writes them again"; exit 1; }
  echo "ADOPTDONE"
  ;;
*)
  echo "usage: hpc/build_geo.sh sources|blocks|cachecheck|write|low|merge|check|all|adopt N"; exit 2 ;;
esac
