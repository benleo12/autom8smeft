#!/bin/bash
# Write one UFO in shards, all at once, then join them.  FeynRules' WriteUFO on a whole model runs for a day
# or more, and its time grows faster than the number of blocks, so the cached blocks are written in many
# small UFOs side by side and validate/merge_ufo.py joins them; validate/compare_ufo.py checks the result
# against a model written in one piece.
#
#   hpc/write_shards.sh plan  NAME BLOCKS NSHARDS [WITHBASE]
#                                                     the block list of each shard, balanced by cache size
#   hpc/write_shards.sh run   NAME FIRST LAST PAR     write shards FIRST..LAST, PAR at a time
#   hpc/write_shards.sh merge NAME                    join the shards into tests/gen_smoke/NAME_raw
#
# The environment is that of validate/fr_writeufo.wls (DIM8_ROOT, DIM8_BASE, DIM8_VDIR, DIM8_TRUNCATE, ...),
# the same for every step.  Shard 0 holds the base model's vertices and the blocks the file WITHBASE lists;
# the others leave the base out (DIM8_NOBASE=1), and every shard runs on one kernel (DIM8_NKERNELS=0, and for
# shard 0 DIM8_NKERNELS_BASE, by default 0 too: with four subkernels the shard of the model of order 2 took 3017 s
# where it takes 798 s on one kernel, 622 s against 13 s of them in LoadModel, for the same vertices).  WITHBASE
# names the operators that enter the relations of the base (INPUT_SCHEME_WCS of ./dim8, and the
# dimension-six sector of a combined model).  The base carries the shifts of those relations, which cancel
# against the operators' own vacuum pieces when the writer merges and truncates a vertex
# (validate/np_truncate.m), so the two must be written together: written apart, the vacuum piece of
# Q_{G^2H^4}^{(1)} stays as a three-gluon coupling of orders NP 2, QED -4 beside the gluon normalisation
# of orders NP 2, numerically opposite but separable by an order constraint in MadGraph, where the model
# written in one piece has no such vertex.  WS names wolframscript, and DIM8_NUMPY_PY the Python with numpy that
# joins the shards, as for ./dim8.
#
# What a shard was written from.  Each shard written records its key, build/shards/NAME/<k>.key: for each of its
# blocks the stamp of its source (validate/cache_source.py), the content of the vertex file the writer loads, and
# whether its vertices of at most three legs are left out (DIM8_DROPBELOW), then the content of every model file
# the writer loads (the files of DIM8_BASE, gen.fr and the flavour rules), and the settings of the writer that
# change what it writes.  A shard gets its key only when the UFO written is whole (`sound`): every file of a UFO
# there and none empty, each data file Python, the couplings and Lorentz structures defined those the vertices
# use, and every name in a value a parameter.  A full disk or quota can leave a UFO with files missing or cut short
# under a log that says it is written.  A shard is complete when its UFO is written, with every file, and its key
# is the key it would have now, so that a run cut short is resumable: it skips the
# complete shards and writes afresh a shard written from another version of a block or of the base.  A shard
# without a key (written before shards had one) is written afresh too, since nothing says what it was written
# from, unless `adopt` shows that nothing it is written from has changed since its plan.  The writer itself is
# not in the key: a change to fr_writeufo.wls or np_truncate.m that changes what they write needs a fresh plan.
# Each key reads the vertex files of its blocks whole, which on a cluster file system takes a minute or so for
# all the shards of a model.
#
# For a model of order N (DIM8_GEO_N set, hpc/build_geo.sh) each shard also records which block gives which
# coefficient to a vertex of at most three legs, in build/shards/NAME/<k>.prov (DIM8_PROVENANCE of
# validate/fr_writeufo.wls), which validate/geo_export_check.py --prov reads, and which ends with a line
# "#end <blocks>" once every block is recorded.  A shard whose UFO and key are complete but whose record is
# missing, cut off, or lacks one of its blocks, has it recorded alone (DIM8_PROVENANCE_ONLY=1, a minute or two),
# which reads the blocks its key names, and is not written again.
#
#   hpc/write_shards.sh complete NAME K   exit 0 when shard K is complete, 2 when only its record is not, else 1
#   hpc/write_shards.sh sound NAME K      exit 0 when the UFO of shard K is whole, else 1 with what it lacks
#   hpc/write_shards.sh key NAME K        the key shard K would have now
#   hpc/write_shards.sh adopt NAME FIRST LAST
#                       record the key of each shard written without one when its UFO is whole, younger than
#                       its plan, and every file it is written from (its blocks' vertex files and status lines, the model
#                       files, DIM8_DROPBELOW) is older, by its date and by its change time, which a copy that
#                       keeps the date still sets: the shard was then written from these files as they are.  The
#                       settings must be those of its write, which only the one who ran it can say
#   hpc/write_shards.sh adoptable NAME FIRST LAST
#                       what adopt would do, shard by shard, with nothing written
#   hpc/write_shards.sh merged NAME       exit 0 when tests/gen_smoke/NAME_raw is the merge of the shards as
#                                         they are, each complete (build/shards/NAME/merged)
#
# `plan` removes the block lists, keys, records and the merge record of an earlier plan, since they belong to it:
# a run that resumes keeps the plan.
set -u
root=${DIM8_ROOT:?set DIM8_ROOT}
self=$(cd "$(dirname "$0")" && pwd)/$(basename "$0")
export WS=${WS:-wolframscript}
step=$1; name=$2
dir=$root/build/shards/$name
out() { echo "$root/tests/gen_smoke/${name}_s$1_raw"; }

key() {   # key MODE K: the key of shard K now (MODE key), or with the proof that its write read these (MODE adopt)
  python3 - "$1" "$name" "$2" <<'EOF'
import hashlib, os, sys
mode, name, k = sys.argv[1:4]
root = os.environ["DIM8_ROOT"]
sys.path.insert(0, os.path.join(root, "validate"))
import cache_source as C
d, smoke = os.path.join(root, "build", "shards", name), os.path.join(root, "tests", "gen_smoke")
env = lambda v: os.environ.get(v, "")
split = lambda v: [f.strip() for f in env(v).split(";") if f.strip()]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


sel = os.path.join(d, f"{k}.blocks")
blocks = sorted({b.strip() for b in open(sel) if b.strip()})
drop = {b.strip() for b in open(env("DIM8_DROPBELOW")) if b.strip()} if env("DIM8_DROPBELOW") else set()
files = (split("DIM8_BASE") or ["base.fr"]) + ["gen.fr", "gen_flavour_rules.m"] + split("DIM8_EXTRA_RULES")
vdirs = split("DIM8_VDIR") or [os.path.join(root, "build", "vertices")]
# the vertex files of a block, of which the writer loads the one there is (two stop it)
held = lambda b: [os.path.join(v, b + e) for v in vdirs for e in (".mx", ".wxf") if os.path.exists(os.path.join(v, b + e))]
lines = [f"setting\t{v}\t{env(v)}" for v in ("DIM8_BASE", "DIM8_L6BASES", "DIM8_LSM", "DIM8_EXTRA_RULES",
                                             "DIM8_TRUNCATE", "DIM8_GEO_N", "DIM8_NPORDER", "DIM8_MAXLEGS")]
# the plain cut of the reference of export check 6, recorded where it is set, so that the keys of the shards
# of a model, which never have it, stay what they were
if env("DIM8_ORDERCUT"):
    lines.append(f"setting\tDIM8_ORDERCUT\t{env('DIM8_ORDERCUT')}")
lines.append(f"shard\t{k}\t{'with the base' if k == '0' else 'without the base'}")
for f in files:
    p = os.path.join(smoke, f)
    lines.append(f"file\t{f}\t{sha(p) if os.path.exists(p) else 'absent'}")
for b in blocks:
    try:
        s = C.source_hash(b)
    except (KeyError, OSError):
        s = "no-source"
    # the content of its vertex file too: a block computed again from the same source, by a worker that has changed,
    # keeps its stamp
    h = held(b)
    v = f"{os.path.basename(h[0])} {sha(h[0])}" if len(h) == 1 else f"{len(h)} vertex files"
    lines.append(f"block\t{b}\t{s}\t{'dropbelow' if b in drop else 'whole'}\t{v}")
if mode == "adopt":
    # the plan comes before every write of it: a shard written after its plan from files none of which changed
    # since then was written from these files
    plan = os.path.getmtime(sel)
    ufo = os.path.join(smoke, f"{name}_s{k}_raw", "vertices.py")
    if not os.path.exists(ufo) or os.path.getmtime(ufo) <= plan:
        sys.exit(f"shard {k}: no UFO written after its plan")
    inputs = [os.path.join(smoke, f) for f in files + split("DIM8_L6BASES") + ["dim6_smeftsim.fr"]]
    inputs += [env("DIM8_DROPBELOW")] if env("DIM8_DROPBELOW") else []
    for b in blocks:
        if len(held(b)) != 1:
            sys.exit(f"shard {k}: block {b} has {len(held(b))} vertex files in DIM8_VDIR, not one")
        inputs += held(b) + [os.path.join(v, b + ".status") for v in vdirs]
    # the later of the date of a file and of its change time, which a copy or a move that keeps the date still sets
    changed = lambda p: max(os.stat(p).st_mtime, os.stat(p).st_ctime)
    newer = sorted(p for p in inputs if os.path.exists(p) and changed(p) >= plan)
    if newer:
        sys.exit(f"shard {k}: {len(newer)} files it is written from changed after its plan (by their date, or by "
                 f"their change time for a file put in place with an older date), so it may not have been written "
                 f"from them: {[os.path.basename(p) for p in newer[:5]]}")
print("\n".join(lines))
EOF
}

record_ok() {   # the record of shard K names every block of its list and ends with its end line, the last (the
  # list of shard 0 may be empty, so the files are told apart by name)
  awk -F'\t' 'FILENAME == ARGV[1] { if ($0 != "" && !($0 in w)) { w[$0]; n++ }; next }
               e != "" { after = 1 }
               $1 == "#end" { e = $2; next }
               $2 == "loaded" { m++; if ($1 in w) { delete w[$1]; n-- } }
               END { exit (n > 0 || e == "" || after || e + 0 != m + 0) }' "$dir/$1.blocks" "$dir/$1.prov" 2> /dev/null
}

manifest() {   # the shards the merge joined, by their UFO and key, and the model it wrote
  python3 - "$root/tests/gen_smoke" "$name" "$dir" <<'EOF'
import glob, hashlib, os, sys
smoke, name, d = sys.argv[1:4]


def sha(p):
    if not os.path.exists(p):
        return "missing"
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


for k in range(len(glob.glob(os.path.join(d, "*.blocks")))):
    s = os.path.join(smoke, f"{name}_s{k}_raw")
    print("\t".join(["shard", str(k)] + [sha(os.path.join(s, f)) for f in ("vertices.py", "couplings.py", "parameters.py")]
                    + [sha(os.path.join(d, f"{k}.key")), sha(os.path.join(d, f"{k}.prov"))]))
r = os.path.join(smoke, f"{name}_raw")
for f in ("vertices.py", "couplings.py", "parameters.py", "lorentz.py", "coupling_orders.py"):
    print(f"model\t{f}\t{sha(os.path.join(r, f))}")
EOF
}

UFOFILES="__init__.py object_library.py function_library.py write_param_card.py propagators.py particles.py parameters.py vertices.py couplings.py lorentz.py coupling_orders.py"
whole() {   # the UFO of shard K has every file FeynRules writes a UFO in, none of them empty
  local f o
  o=$(out "$1")
  for f in $UFOFILES; do [ -s "$o/$f" ] || { echo "shard $1: its UFO has no $f, or an empty one"; return 1; }; done
}

sound() {   # and the files are whole: each is Python, and they name nothing the others lack and define nothing unused
  whole "$1" || return 1
  python3 - "$(out "$1")" "$1" <<'EOF'
import builtins, os, re, sys
d, k = sys.argv[1:3]
text = {}
for f in ("particles.py", "parameters.py", "vertices.py", "couplings.py", "lorentz.py", "coupling_orders.py"):
    text[f] = open(os.path.join(d, f), errors="replace").read()
    try:
        compile(text[f], f, "exec")
    except (SyntaxError, ValueError) as e:
        sys.exit(f"shard {k}: its UFO is not whole: {f} is cut short or not Python ({e})")
V, C, L, P = (text[f] for f in ("vertices.py", "couplings.py", "lorentz.py", "parameters.py"))
bad = []
# FeynRules writes the couplings and Lorentz structures of the vertices it writes and no other, so a file that ends
# early, even between two of its objects, leaves one side with more than the other
for what, used, made in (("couplings", set(re.findall(r"\bC\.(\w+)", V)), set(re.findall(r"^(\w+) = Coupling\(", C, re.M))),
                         ("Lorentz structures", set(re.findall(r"\bL\.(\w+)", V)), set(re.findall(r"^(\w+) = Lorentz\(", L, re.M)))):
    if used - made:
        bad.append(f"{len(used - made)} {what} of vertices.py are not defined, {sorted(used - made)[:3]}")
    if made - used:
        bad.append(f"{len(made - used)} {what} are in no vertex, {sorted(made - used)[:3]}")
lost = set(re.findall(r"\bP\.(\w+)", V)) - set(re.findall(r"^(\w+) = ", text["particles.py"], re.M))
if lost:
    bad.append(f"{len(lost)} particles of vertices.py are not defined, {sorted(lost)[:3]}")
# and every name in the value of a coupling or of a parameter is a parameter or a function of the model
names = set(re.findall(r"^(\w+) = Parameter\(", P, re.M)) | set(re.findall(r"name = '(\w+)'", P))
known = names | set(re.findall(r"name = '(\w+)'", open(os.path.join(d, "function_library.py"), errors="replace").read())) \
    | set(dir(builtins)) | {"cmath", "math"}
for f, t in (("couplings.py", C), ("parameters.py", P)):
    und = set()
    for v in re.findall(r"value = '([^']*)'", t):
        und |= set(re.findall(r"(?<![\w.])[A-Za-z_]\w*", re.sub(r"\bcmath\.\w+", "", v))) - known
    if und:
        bad.append(f"{len(und)} names in the values of {f} are not parameters, {sorted(und)[:3]}")
if bad:
    sys.exit(f"shard {k}: its UFO is not whole: " + "; ".join(bad))
EOF
}

complete() {   # 0: shard K is written from what it has now and recorded; 2: all but its record; 1: neither
  local k=$1
  whole "$k" > /dev/null && grep -q "\[ufo\]" "$root/logs/shards/${name}_$k.log" 2> /dev/null || return 1
  [ -s "$dir/$k.key" ] && cmp -s "$dir/$k.key" <(key key "$k" 2> /dev/null) || return 1
  [ -n "${DIM8_GEO_N:-}" ] || return 0
  record_ok "$k" || return 2
}

case $step in
plan)
  blocks=$3; n=$4; withbase=${5:-}
  mkdir -p "$dir" && rm -f "$dir"/*.blocks "$dir"/*.prov "$dir"/*.key "$dir"/*.key.new "$dir"/*.key.log "$dir/merged"
  python3 - "$blocks" "$n" "$dir" "${DIM8_VDIR:?}" "$withbase" <<'EOF'
import os, sys
blocks, n, d, vdirs, wb = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4].split(";"), sys.argv[5]
names = [b.strip() for b in open(blocks) if b.strip()]
base = [b.strip() for b in open(wb) if b.strip() in names] if wb else []
# no shard without a block: FeynRules writes an empty one with a vertex of no particles, whose Lorentz
# structure is named "1" and stops the join
n = min(n, len(set(names) - set(base)) + 1)
def size(b):
    for v in vdirs:
        for ext in (".mx", ".wxf"):
            p = os.path.join(v, b + ext)
            if os.path.exists(p):
                return os.path.getsize(p)
    sys.exit(f"block {b} is not in {vdirs}")
# the largest block first into the lightest shard; shard 0 is the base model's
load = [0] * n
lists = [[] for _ in range(n)]
for b in sorted(set(names) - set(base), key=size, reverse=True):
    k = min(range(1, n), key=lambda i: load[i])
    load[k] += size(b)
    lists[k].append(b)
open(os.path.join(d, "0.blocks"), "w").write("".join(b + "\n" for b in base))
for k in range(1, n):
    open(os.path.join(d, f"{k}.blocks"), "w").write("\n".join(lists[k]) + "\n")
print(f"{len(names)} blocks, {len(base)} of them with the base in shard 0 and the others in {n - 1} shards, largest shard {max(load) / 1e6:.1f} MB of cache, "
      f"smallest {min(load[1:], default=0) / 1e6:.1f} MB")
EOF
  ;;
run)
  first=$3; last=$4; par=$5
  mkdir -p "$root/logs/shards"
  export root name dir self
  # each shard number as the argument of its own bash, not substituted into the script: BSD xargs (macOS) allows
  # -I no replacement longer than 255 bytes
  seq "$first" "$last" | xargs -P "$par" -n 1 bash -c '
    k=$1; o=$root/tests/gen_smoke/${name}_s${k}_raw; log=$root/logs/shards/${name}_$k.log
    sel=$dir/$k.blocks
    prov=; [ -n "${DIM8_GEO_N:-}" ] && prov=$dir/$k.prov
    # an empty selection file selects no block (no file at all would select every cached block), and a
    # shard the plan did not make, for a list with fewer blocks than shards, is not written
    [ "$k" = 0 ] || [ -f "$sel" ] || exit 0
    bash "$self" complete "$name" "$k"; c=$?
    [ "$c" = 0 ] && exit 0
    if [ "$c" = 2 ]; then
      # written from the blocks and the base it has now, but without the whole record of its blocks: recorded
      # alone, from the blocks its key names, and not written again
      rm -f "$prov"
      env DIM8_NOBASE=1 DIM8_NKERNELS=0 DIM8_PROVENANCE=$prov DIM8_PROVENANCE_ONLY=1 \
        "$WS" -file "$root/validate/fr_writeufo.wls" "${name}_s${k}_prov" $sel > "$dir/$k.prov.log" 2>&1
      rc=$?
      echo "$(date +%H:%M:%S) shard $k provenance exit $rc" >> "$root/logs/shards/${name}.done"
      exit $rc
    fi
    # not written, or written from another version of a block or of the base than there is now, or without a
    # key: written afresh, its key taken before the writer reads its blocks
    if [ "$k" = 0 ]; then nb=0; nk=${DIM8_NKERNELS_BASE:-0}; else nb=1; nk=0; fi
    rm -rf "$o"; rm -f "$dir/$k.key" "$dir/$k.key.new"
    [ -z "$prov" ] || rm -f "$prov"
    bash "$self" key "$name" "$k" > "$dir/$k.key.new" 2> "$dir/$k.key.log" && [ -s "$dir/$k.key.new" ] \
      || { rm -f "$dir/$k.key.new"; echo "shard $k: no key, see $dir/$k.key.log, so it will not count as complete"; }
    t0=$(date +%s)
    env DIM8_NOBASE=$nb DIM8_NKERNELS=$nk ${prov:+DIM8_PROVENANCE=$prov} \
      "$WS" -file "$root/validate/fr_writeufo.wls" "${name}_s${k}_raw" $sel > "$log" 2>&1
    rc=$?
    # the key only for a UFO that is whole: a full disk or quota can leave one with files missing or cut short
    # under a log that says it is written
    if [ "$rc" = 0 ] && grep -q "\[ufo\]" "$log" && [ -f "$dir/$k.key.new" ]; then
      if bash "$self" sound "$name" "$k" >> "$log" 2>&1; then mv "$dir/$k.key.new" "$dir/$k.key"; else rc=1; fi
    fi
    rm -f "$dir/$k.key.new"
    echo "$(date +%H:%M:%S) shard $k exit $rc after $(( $(date +%s) - t0 )) s" >> "$root/logs/shards/${name}.done"
    exit $rc' shard
  ;;
complete)
  complete "$3"
  ;;
sound)
  sound "$3"
  ;;
key)
  key key "$3"
  ;;
adopt|adoptable)
  first=$3; last=$4; rc=0
  for k in $(seq "$first" "$last"); do
    [ -f "$dir/$k.blocks" ] || continue
    if [ -s "$dir/$k.key" ]; then echo "shard $k has a key"; continue; fi
    grep -q "\[ufo\]" "$root/logs/shards/${name}_$k.log" 2> /dev/null || { echo "shard $k is not written"; rc=1; continue; }
    sound "$k" || { rc=1; continue; }
    if [ "$step" = adoptable ]; then
      # the same test, and nothing written
      if key adopt "$k" > /dev/null; then echo "shard $k: adopt would record its key"; else rc=1; fi
    elif key adopt "$k" > "$dir/$k.key.new" && [ -s "$dir/$k.key.new" ]; then
      mv "$dir/$k.key.new" "$dir/$k.key"; echo "shard $k: key recorded"
    else
      rm -f "$dir/$k.key.new"; echo "shard $k: not adopted, a run writes it afresh"; rc=1
    fi
  done
  exit $rc
  ;;
merge)
  n=$(ls "$dir"/*.blocks | wc -l)
  bad=$(for k in $(seq 0 $((n - 1))); do complete "$k" || echo "$k"; done)
  [ -z "$bad" ] || { echo "shards not complete, so not joined (written from other blocks or another base than they have now, not written, or not recorded):" $bad; exit 1; }
  # the join replaces the model of an earlier one, which is gone before it starts, so that a join that fails
  # leaves no model that `merged` could take for it
  rm -rf "$root/tests/gen_smoke/${name}_raw" "$dir/merged"
  shards=$(for k in $(seq 0 $((n - 1))); do out "$k"; done)
  "${DIM8_NUMPY_PY:-python3}" "$root/validate/merge_ufo.py" "$root/tests/gen_smoke/${name}_raw" $shards || exit 1
  manifest > "$dir/merged.new" && mv "$dir/merged.new" "$dir/merged"
  ;;
merged)
  [ -s "$dir/merged" ] || { echo "no record of a merge in $dir"; exit 1; }
  n=$(ls "$dir"/*.blocks | wc -l)
  bad=$(for k in $(seq 0 $((n - 1))); do complete "$k" || echo "$k"; done)
  [ -z "$bad" ] || { echo "shards not complete now:" $bad; exit 1; }
  cmp -s "$dir/merged" <(manifest) || { echo "tests/gen_smoke/${name}_raw is not the merge of the shards as they are now"; exit 1; }
  ;;
*)
  echo "usage: $0 plan|run|complete|sound|key|adopt|adoptable|merge|merged NAME ..."; exit 2;;
esac
