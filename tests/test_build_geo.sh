#!/bin/bash
# tests/test_build_geo.sh  --  the steps of hpc/build_geo.sh that need no Mathematica, on a sandbox with stubs.
#
#   bash tests/test_build_geo.sh [-v]      (bash and python3; -v prints the output of each case)
#
# The sandbox is a checkout of hpc/build_geo.sh, hpc/write_shards.sh, hpc/geo_sched.py, hpc/run_parts.sh and
# validate/cache_source.py, with the sources of a model of order 2 (gen.fr, gen_geo2.fr, dim6_geo.fr,
# base_geo2_mw.fr, and dim6_smeftsim.fr and base_inputscheme_mw.fr for its block of the dimension-six release) and
# caches of its seven blocks stamped with them, and stubs for what the steps call: a wolframscript that writes a
# shard (a UFO of its own with every file of one, the [ufo] line, and with DIM8_PROVENANCE the record of its blocks
# with its end line), stands in for validate/geo_cache_check.wls, and logs each call, a join of the shards, a release that prints the lines a release prints,
# and a MadGraph that is only a file.  The cases:
#
#   write before the tower blocks are checked against their operators (cachecheck): it stops, cachecheck with a
#   block that fails, that could not be checked, that the check says nothing of, or with a kernel that fails: it
#   stops and records the blocks that passed, which it does not check again, and a block computed again, or whose
#   definition or base changed, has no pass any more,
#   write, then adopt (hpc/build_geo.sh adopt), which records the key of a shard written without one from files
#   older than its plan, and refuses one whose block changed after it, or was put in place after it with an
#   older date, which the resume then writes alone, and adoptable, which says the same and writes nothing,
#   blocks computed again from the same source, so that a new plan would deal them differently: the shards that
#   hold them written again, in the plan there is, and then a resume that finishes at once and writes nothing,
#   a complete shard without its record, or with a record cut off before its end line: recorded alone,
#   a shard without its UFO, or without its key: that shard written alone,
#   a shard whose UFO lacks a file: not complete, not adopted, written again, and a write that leaves its UFO
#   spoiled under a log that says it is written (a file not copied, cut in an object, cut between two, a
#   parameter missing): no key, so not complete,
#   a block whose source changed and was rebuilt: the shard that holds it written again, and no other,
#   a model file every shard loads that changed (a block definition in gen_geo2.fr, the base): every shard again,
#   a resume after the block list or the blocks written with the base changed: it stops,
#   merge after a shard went: it stops, and check does not release the model of the earlier merge,
#   check after a shard was written again since the merge: it stops,
#   check before the reference of export check 6 is written (low), or with one that lost a file: it stops, low
#   writes it as one shard of the geo blocks with the plain cut, and again writes nothing,
#   a fresh write removes the merged model of an earlier one,
#   check without MG5_DIR: it stops before the release, check whose release fails: no MODELDONE,
#   check follows the exit status of the release, even when its log cannot be written, and requires every
#   check of it (DIM8_GEO_STRICT=1),
#   examples/release_model.sh with DIM8_GEO_STRICT=1 and no provenance: it stops before it copies anything,
#   all, started by a relative path from another directory: its first step runs,
#   hpc/run_parts.sh on a block cut short before its source changed, or by a run that kept no record of its source:
#   it starts afresh, and with the source unchanged it takes the block up from its files,
#   hpc/run_parts.sh whose merge fails beside the status line of an older build: it fails and keeps the parts.
set -u
here=$(cd "$(dirname "$0")/.." && pwd)
verbose=0; [ "${1:-}" = -v ] && verbose=1
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
R=$T/root; B=$T/build; N=2; NAME=dim68_mw_geo2
S=$R/build/shards/$NAME; GS=$R/tests/gen_smoke; GV=$B/vertices_geo2_mw; L=$B/$NAME
mkdir -p $R/hpc $R/validate $R/examples $GS $L $GV $T/rel8 $T/rel6 $T/mg/bin $T/x/elsewhere $T/ref
cp $here/hpc/build_geo.sh $here/hpc/write_shards.sh $here/hpc/geo_sched.py $R/hpc/
cp $here/validate/cache_source.py $R/validate/
touch $R/validate/fr_writeufo.wls $T/mg/bin/mg5_aMC $T/ref/vertices.py; chmod +x $T/mg/bin/mg5_aMC
echo "(* the stand-in of the check of the cached tower blocks *)" > $R/validate/geo_cache_check.wls
BASES="base_geo2_mw.fr;dim6_geo.fr;gen_geo2.fr"
# the sources and the caches of the seven blocks, stamped with them
printf 'Lam == {Value -> 1000};\nL8op1 := c8a Phi^4 ;\nL8op2 := c8b Phi^6 ;\n' > $GS/gen.fr
printf 'G8op1 := c8c Phi^2 ;\nG8op2 := c8d Phi^4 ;\nT10op1 := c10c Phi^2 ;\n' > $GS/gen_geo2.fr
printf 'G6cl1 := cH Phi^6 ;\n' > $GS/dim6_geo.fr
printf 'MW := 80.4 ;\n' > $GS/base_geo2_mw.fr
printf 'MW := 80.4 ;\n' > $GS/base_inputscheme_mw.fr
printf 'L6cl2 := cHD Phi^4 ;\n' > $GS/dim6_smeftsim.fr
printf 'z8FlavourRules = <||>;\n' > $GS/gen_geo2_flavour_rules.m
printf '[{"block": "G8op1", "dim": 8}, {"block": "G8op2", "dim": 8}, {"block": "T10op1", "dim": 10}]\n' > $GS/gen_geo2.json
size() { head -c $2 /dev/zero > $1.mx; }
# the plan deals G8op2 | L8op1, T10op1 | L8op2, L6cl2 into shards 1 to 3
size $GV/G6cl1 300; size $GV/G8op1 300; size $GV/G8op2 900; size $T/rel8/L8op1 500; size $T/rel8/L8op2 400
size $T/rel6/L6cl2 200; size $GV/T10op1 100
stamp() {   # stamp DIR BLOCK...: status lines with the stamps of their current sources
  for b in "${@:2}"; do echo "$b | tEval 1 | tVert 1" > $1/$b.status; done
  env DIM8_BASE="$BASES" DIM8_L6BASES=base_inputscheme_mw.fr python3 $R/validate/cache_source.py stamp "$1" "${@:2}" > /dev/null
}
stamp $GV G6cl1 G8op1 G8op2 T10op1; stamp $T/rel8 L8op1 L8op2; stamp $T/rel6 L6cl2
# the lists of the sources step
printf '%s\n' L8op1 L8op2 L6cl2 G6cl1 G8op1 G8op2 T10op1 > $L/model.blocks
printf '%s\n' G6cl1 G8op1 > $L/withbase
printf '%s\n' L8op1 > $L/dropbelow
printf '%s\n' G6cl1 G8op1 G8op2 T10op1 > $L/blocks3
: > $L/blocksall
echo "order 2, scheme mw, basis geo" > $L/key
echo "order 2, scheme mw, basis geo" > $GV/cache.key
# every file a shard is written from older than its plan, as after the sources and blocks steps, by its date and
# by its change time, on a file system that keeps them to the second too
touch -t 202601010000 $GS/* $GV/* $T/rel8/* $T/rel6/* $L/*
sleep 2
cat > $T/ws <<'EOF'
#!/bin/bash
# the stub of wolframscript: -file validate/geo_cache_check.wls <N> <block,block,...> <cache>, which says PASS for
# each block but those STUB_CACHE_FAIL, STUB_CACHE_NOT and STUB_CACHE_SILENT name, with the exit status of the check
if [ "$(basename "$2")" = geo_cache_check.wls ]; then
  echo "cachecheck $4" >> "$STUB_CALLS"
  rc=0
  for b in $(echo "$4" | tr , " "); do
    case $b in
      "${STUB_CACHE_FAIL:-}") echo "[cachecheck] $b order $3: FAIL: NP 3: 0.81 of the largest coupling"; [ $rc = 2 ] || rc=1 ;;
      "${STUB_CACHE_NOT:-}") echo "[cachecheck] $b order $3: NOT CHECKED: no cached block"; rc=2 ;;
      "${STUB_CACHE_SILENT:-}") ;;
      *) echo "[cachecheck] $b order $3: PASS 3 vertices" ;;
    esac
  done
  exit ${STUB_CACHE_RC:-$rc}
fi
# and -file validate/fr_writeufo.wls <name> <selection>
name=$3; sel=$4
echo "$name prov_only=${DIM8_PROVENANCE_ONLY:-0}" >> "$STUB_CALLS"
if [ -n "${DIM8_PROVENANCE:-}" ]; then
  n=0; while read -r b; do [ -n "$b" ] && { printf '%s\tloaded\t1\t0\n%s\tvertex\tZ e ebar\tc8x\n' "$b" "$b"; n=$((n + 1)); }; done < "$sel" > "$DIM8_PROVENANCE"
  printf '#end\t%s\n' $n >> "$DIM8_PROVENANCE"
fi
[ "${DIM8_PROVENANCE_ONLY:-0}" = 1 ] && exit 0
o=$DIM8_ROOT/tests/gen_smoke/$name; mkdir -p "$o"
# a UFO of one vertex, with every file FeynRules writes
tag="# $name $(date +%s) $RANDOM $$"
for f in __init__ object_library function_library write_param_card propagators coupling_orders; do echo "$tag" > "$o/$f.py"; done
echo "complexconjugate = Function(name = 'complexconjugate', arguments = ('z',), expression = 'z.conjugate()')" >> "$o/function_library.py"
printf '%s\n' "$tag" "a = Particle(pdg_code = 22, name = 'a')" "e__minus__ = Particle(pdg_code = 11, name = 'e-')" \
  "e__plus__ = e__minus__.anti()" > "$o/particles.py"
printf '%s\n' "$tag" "cX = Parameter(name = 'cX', nature = 'external', value = 0.1)" \
  "ee = Parameter(name = 'ee', nature = 'internal', value = 'cX*cmath.sqrt(2)*complexconjugate(1.5e-3)')" > "$o/parameters.py"
printf '%s\n' "$tag" "GC_1 = Coupling(name = 'GC_1', value = 'ee*complex(0,1)', order = {'NP':1})" > "$o/couplings.py"
printf '%s\n' "$tag" "FFV1 = Lorentz(name = 'FFV1', spins = [ 2, 2, 3 ], structure = 'Gamma(3,2,1)')" > "$o/lorentz.py"
printf '%s\n' "$tag" "V_1 = Vertex(name = 'V_1', particles = [ P.e__plus__, P.e__minus__, P.a ], color = [ '1' ]," \
  "  lorentz = [ L.FFV1 ], couplings = {(0,0):C.GC_1})" > "$o/vertices.py"
# what a full disk or quota leaves under a log that says the UFO is written: a helper file not copied, a file cut
# in the middle of an object, a file cut between two
case ${STUB_BROKEN:-} in
  nofile) rm -f "$o/object_library.py" ;;
  cut) printf '%s\n' "$tag" "V_1 = Vertex(name = 'V_1', particles = [ P.e__plus__, P.e__minus__," > "$o/vertices.py" ;;
  between) printf '%s\n' "GC_2 = Coupling(name = 'GC_2', value = 'ee', order = {'NP':2})" >> "$o/couplings.py" ;;
  noname) printf '%s\n' "$tag" "cX = Parameter(name = 'cX', nature = 'external', value = 0.1)" > "$o/parameters.py" ;;
esac
echo "[ufo] $name written"
EOF
chmod +x $T/ws
# the join of the shards: the model holds what each shard holds
cat > $R/validate/merge_ufo.py <<'EOF'
import os, sys
out, shards = sys.argv[1], sys.argv[2:]
os.makedirs(out)
for f in ("vertices.py", "couplings.py", "parameters.py", "lorentz.py", "coupling_orders.py"):
    open(os.path.join(out, f), "w").write("".join(open(os.path.join(s, f)).read() if os.path.exists(os.path.join(s, f)) else ""
                                                   for s in shards))
EOF
# the release, which build_geo.sh must run with every check required
cat > $R/examples/release_model.sh <<'EOF'
#!/bin/bash
# with STUB_STRICT=1 it stops unless every check is required (DIM8_GEO_STRICT=1) and the reference of check 6 is given
[ "${STUB_STRICT:-0}" = 1 ] && [ "${DIM8_GEO_STRICT:-}" != 1 ] && { echo "release stopped (stub): DIM8_GEO_STRICT is not 1"; exit 1; }
[ "${STUB_STRICT:-0}" = 1 ] && [ ! -f "${DIM8_GEO_LOW:-}/vertices.py" ] && { echo "release stopped (stub): no DIM8_GEO_LOW"; exit 1; }
cat "$STUB_RELEASE"; exit "${STUB_RELEASE_RC:-0}"
EOF
printf '%s\n' "1, 2. orders, and four or more legs at NP <= 2: PASS" "3. coefficient blocks: PASS" \
  "4. included once, by block: PASS" "5. included once, against the reference at NP <= 2: PASS" \
  "MadGraph imports the model and generates through it" "EXPORT CHECKS PASS" > $T/release.txt
export DIM8_ROOT=$R DIM8_BUILD=$B DIM8_VDIR=$T/rel8 DIM8_VDIR6_MW=$T/rel6 WS=$T/ws GEO_SHARDS=3 GEO_PAR=2 \
       STUB_CALLS=$T/calls STUB_RELEASE=$T/release.txt DIM8_NUMPY_PY=python3
wenv() {   # the environment build_geo.sh writes the shards in
  env DIM8_BASE="$BASES" DIM8_VDIR="$GV;$T/rel8;$T/rel6" DIM8_L6BASES=base_inputscheme_mw.fr \
      DIM8_EXTRA_RULES=gen_geo2_flavour_rules.m DIM8_DROPBELOW=$L/dropbelow DIM8_TRUNCATE=1 DIM8_GEO_N=2 "$@"
}
fails=0
fail() { echo "FAIL $*"; fails=$((fails + 1)); }
case_() {   # case_ NAME WANT-EXIT GREP-PATTERN-OR-EMPTY COMMAND...: the exit code and a line of the output
  local name=$1 want=$2 pat=$3; shift 3
  : > $T/calls
  "$@" > $T/out 2>&1; local rc=$?
  local ok=1
  [ "$rc" = "$want" ] || ok=0
  [ -z "$pat" ] || grep -qE "$pat" $T/out || ok=0
  if [ $ok = 1 ]; then echo "ok   $name"; [ $verbose = 1 ] && sed 's/^/     /' $T/out; return 0; fi
  fail "$name (exit $rc, wanted $want${pat:+, and a line matching '$pat'})"; sed 's/^/     /' $T/out | tail -8
}
calls() { grep -c . $T/calls; }
written() { tr '\n' ' ' < $T/calls; }
plan_sum() { cat $S/*.blocks | cksum; }
shard_of() { basename "$(grep -lx "$1" $S/*.blocks)" .blocks; }
geo() { bash $R/hpc/build_geo.sh "$@"; }

# the gate between the blocks and the write: every tower block checked against its operator
checked() { cut -f1 $L/cachecheck 2> /dev/null | tr '\n' ' '; }
case_ "write before the tower blocks are checked stops" 1 "run hpc/build_geo.sh cachecheck" env GEO_FRESH=1 bash $R/hpc/build_geo.sh write $N
[ "$(calls)" = 0 ] || fail "... after it wrote $(written)"
case_ "cachecheck with a block that fails stops, with its FAIL line" 1 "G8op2 order 2: FAIL: NP 3: 0.81" env STUB_CACHE_FAIL=G8op2 bash $R/hpc/build_geo.sh cachecheck $N
grep -q CACHEDONE $T/out && fail "... and printed CACHEDONE"
[ "$(checked)" = "G8op1 T10op1 " ] && echo "ok   ... and records the two that passed" || fail "... recorded: $(checked)"
case_ "... and write still stops" 1 "1 of 3 tower blocks have no pass.*G8op2" env GEO_FRESH=1 bash $R/hpc/build_geo.sh write $N
case_ "cachecheck with a block that could not be checked stops" 1 "G8op2 order 2: NOT CHECKED" env STUB_CACHE_NOT=G8op2 bash $R/hpc/build_geo.sh cachecheck $N
[ "$(written)" = "cachecheck G8op2 " ] && echo "ok   ... having asked for that block alone" || fail "... calls: $(written)"
case_ "cachecheck with a block the check says nothing of stops" 1 "G8op2 order 2: no line" env STUB_CACHE_SILENT=G8op2 bash $R/hpc/build_geo.sh cachecheck $N
case_ "cachecheck whose kernel fails after it said PASS stops" 1 "ended with exit 2" env STUB_CACHE_RC=2 bash $R/hpc/build_geo.sh cachecheck $N
case_ "cachecheck with every block passed" 0 "^CACHEDONE" geo cachecheck $N
[ "$(checked)" = "G8op1 G8op2 T10op1 " ] || fail "... recorded: $(checked)"
[ "$(calls)" = 0 ] && echo "ok   ... without checking again the blocks that passed" || fail "... calls: $(written)"
case_ "write: every shard written" 0 "WRITEDONE" env GEO_FRESH=1 bash $R/hpc/build_geo.sh write $N
[ "$(calls)" = 4 ] && echo "ok   ... with 4 shard writes" || fail "... with $(calls) shard writes"
p0=$(plan_sum)

# a shard written without a key, by a write_shards.sh before the keys: adopted when nothing changed since its plan
rm -f $S/1.key
case_ "adoptable says that adopt would record the key of a shard written from files older than its plan" 0 \
  "shard 1: adopt would record its key" wenv bash $R/hpc/write_shards.sh adoptable $NAME 0 3
[ -e $S/1.key ] || [ -e $S/1.key.new ] && fail "... and wrote a key"
case_ "adopt records the key of a shard written from files older than its plan" 0 "shard 1: key recorded" geo adopt $N
grep -q "^ADOPTDONE" $T/out || fail "... without ADOPTDONE"
case_ "... and the resume then writes nothing" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(calls)" = 0 ] || fail "... wrote $(written)"
k=$(shard_of T10op1); rm -f $S/$k.key; touch $GV/T10op1.mx
case_ "adopt refuses a shard one of whose blocks changed after its plan" 1 "shard $k: .*changed after its plan" \
  wenv bash $R/hpc/write_shards.sh adopt $NAME $k $k
[ -f $S/$k.key ] && fail "... and recorded a key"
# the same block put in place after the plan with an older date, as a copy that keeps the date leaves it
touch -t 202601010000 $GV/T10op1.mx
case_ "... and one whose block was put in place after its plan with an older date" 1 "shard $k: .*changed after its plan" \
  wenv bash $R/hpc/write_shards.sh adopt $NAME $k $k
[ -f $S/$k.key ] && fail "... and recorded a key"
case_ "... as adoptable says, with nothing written" 1 "shard $k: .*changed after its plan" \
  wenv bash $R/hpc/write_shards.sh adoptable $NAME $k $k
case_ "... which the resume writes afresh" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s${k}_raw prov_only=0 " ] && echo "ok   ... alone" || fail "... calls: $(written)"

# T10op1 and G8op2 computed again from the sources they have (by a worker that changed, say), so that a plan made
# now would deal T10op1 | L8op1, G8op2 | L8op2, L6cl2: the shards that hold them are written again, in the plan there is
size $GV/T10op1 5000; size $GV/G8op2 50
case_ "write after tower blocks were computed again stops until they are checked" 1 "2 of 3 tower blocks have no pass" \
  env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(calls)" = 0 ] || fail "... after it wrote $(written)"
case_ "cachecheck then checks those two" 0 "^CACHEDONE" geo cachecheck $N
[ "$(sed 's/cachecheck //' $T/calls | tr ',\n' '  ' | xargs -n 1 | sort | tr '\n' ' ')" = "G8op2 T10op1 " ] && echo "ok   ... and no other" \
  || fail "... calls: $(written)"
want=$(printf '%s prov_only=0\n' "${NAME}_s$(shard_of G8op2)_raw" "${NAME}_s$(shard_of T10op1)_raw" | sort | tr '\n' ' ')
case_ "blocks computed again from the same source: their shards written again" 0 "WRITEDONE" \
  env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(sort $T/calls | tr '\n' ' ')" = "$want" ] && echo "ok   ... those two and no other" || fail "... calls: $(written)"
[ "$(plan_sum)" = "$p0" ] && echo "ok   ... with the plan kept" || fail "... the plan changed"
case_ "write again with GEO_FRESH=0: done at once" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(calls)" = 0 ] && echo "ok   ... writing nothing" || fail "... wrote $(written)"

rm -f $S/1.prov
case_ "a complete shard without its record: recorded alone" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s1_prov prov_only=1 " ] && echo "ok   ... by one provenance run and no write" || fail "... calls: $(written)"

# a record cut off at a line boundary, before its end line
grep -v '^#end' $S/2.prov > $S/2.prov.cut; mv $S/2.prov.cut $S/2.prov
case_ "complete says that a shard whose record has no end line is not recorded" 2 "" wenv bash $R/hpc/write_shards.sh complete $NAME 2
case_ "... and the resume records it alone" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s2_prov prov_only=1 " ] && echo "ok   ... by one provenance run and no write" || fail "... calls: $(written)"

rm -rf $GS/${NAME}_s2_raw
case_ "a shard without its UFO: that shard written" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s2_raw prov_only=0 " ] && echo "ok   ... alone" || fail "... calls: $(written)"

rm -f $S/3.key
case_ "a shard without its key: written afresh" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s3_raw prov_only=0 " ] && echo "ok   ... alone" || fail "... calls: $(written)"

# a UFO that lost a file after it was written
mv $GS/${NAME}_s1_raw/object_library.py $T/object_library.kept
case_ "a shard whose UFO lacks a file is not complete" 1 "" wenv bash $R/hpc/write_shards.sh complete $NAME 1
mv $S/1.key $T/1.key.kept
case_ "... and adopt does not take it" 1 "shard 1: its UFO has no object_library.py" wenv bash $R/hpc/write_shards.sh adopt $NAME 1 1
[ -e $S/1.key ] && fail "... it recorded a key"
case_ "... and the resume writes it afresh" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s1_raw prov_only=0 " ] && echo "ok   ... alone" || fail "... calls: $(written)"
# a write that a full disk or quota spoils under a log that says the UFO is written: no key, so not complete
for how in nofile cut between noname; do
  mv $GS/${NAME}_s2_raw $T/s2.$how
  case_ "a write that leaves its UFO spoiled ($how) is not complete" 1 "shards not complete.* 2 " \
    env GEO_FRESH=0 STUB_BROKEN=$how bash $R/hpc/build_geo.sh write $N
  [ -e $S/2.key ] && fail "... it got a key"
  grep -q "shard 2: its UFO" $R/logs/shards/${NAME}_2.log && echo "ok   ... and its log says what its UFO lacks" \
    || fail "... its log does not say why: $(tail -1 $R/logs/shards/${NAME}_2.log)"
done
case_ "... and the next resume writes it whole" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s2_raw prov_only=0 " ] && echo "ok   ... alone" || fail "... calls: $(written)"

# the base of the dimension-six release block L6cl2 changed, a file the writer of this model does not load, and
# the block rebuilt on it: its stamp alone tells
echo 'MZ := 91.19 ;' >> $GS/base_inputscheme_mw.fr; stamp $T/rel6 L6cl2
k=$(shard_of L6cl2)
case_ "a block whose source changed and was rebuilt: its shard written again" 0 "WRITEDONE" \
  env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(written)" = "${NAME}_s${k}_raw prov_only=0 " ] && echo "ok   ... and no other" || fail "... calls: $(written)"
# the definition of G8op2 corrected in gen_geo2.fr, which every shard loads, and the block rebuilt from it
sed -i.bak 's/^G8op2 := c8d Phi^4 ;$/G8op2 := 2 c8d Phi^4 ;/' $GS/gen_geo2.fr; stamp $GV G8op2
case_ "a tower block whose definition changed has no pass any more" 1 "1 of 3 tower blocks have no pass.*G8op2" \
  env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
geo cachecheck $N > /dev/null
case_ "a model file every shard loads changed: every shard written again" 0 "WRITEDONE" \
  env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(calls)" = 4 ] && echo "ok   ... all four" || fail "... calls: $(written)"

# a change to the base, on which every geo block is rebuilt, and which every shard writes
echo 'MZ := 91.19 ;' >> $GS/base_geo2_mw.fr; stamp $GV G6cl1 G8op1 G8op2 T10op1
case_ "after a change of the base no tower block has a pass" 1 "3 of 3 tower blocks have no pass" \
  env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
geo cachecheck $N > /dev/null
case_ "a base that changed: every shard written again" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
[ "$(calls)" = 4 ] && echo "ok   ... all four" || fail "... calls: $(written)"

echo 'L8op3 := c8e Phi^8 ;' >> $GS/gen.fr; echo L8op3 >> $L/model.blocks; size $T/rel8/L8op3 300; stamp $T/rel8 L8op3
case_ "a resume after the block list changed stops" 1 "plan of another block list" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
sed -i.bak '/^L8op3$/d' $L/model.blocks; sed -i.bak '/^L8op3 /d' $GS/gen.fr; rm -f $T/rel8/L8op3.*
echo G8op2 >> $L/withbase
case_ "a resume after the blocks written with the base changed stops" 1 "with the base and not in shard 0" \
  env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N
sed -i.bak '/^G8op2$/d' $L/withbase
case_ "... and is done at once once they are back" 0 "WRITEDONE" env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N

# merge and check
case_ "merge joins the shards" 0 "MERGEDONE" geo merge $N
# the reference of export check 6: the geo blocks and the base once more, as one shard of its own
case_ "check before the reference of check 6 is written stops" 1 "run hpc/build_geo.sh low" \
  env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
case_ "low writes the reference" 0 "^LOWDONE" geo low $N
[ "$(written)" = "${NAME}_low_s0_raw prov_only=0 " ] && echo "ok   ... one shard" || fail "... calls: $(written)"
[ "$(tr '\n' ' ' < $R/build/shards/${NAME}_low/0.blocks)" = "G6cl1 G8op1 G8op2 T10op1 " ] \
  && echo "ok   ... of the blocks of the geo tree and no other" || fail "... of $(tr '\n' ' ' < $R/build/shards/${NAME}_low/0.blocks)"
grep -q "DIM8_ORDERCUT.$N$" $R/build/shards/${NAME}_low/0.key && grep -q "DIM8_MAXLEGS.3$" $R/build/shards/${NAME}_low/0.key \
  && grep -q "DIM8_TRUNCATE.$" $R/build/shards/${NAME}_low/0.key && echo "ok   ... with the plain cut at N, three legs and no truncation" \
  || fail "... its key: $(grep setting $R/build/shards/${NAME}_low/0.key | tr '\n\t' '; ')"
case_ "low again writes nothing" 0 "^LOWDONE" geo low $N
[ "$(calls)" = 0 ] || fail "... wrote $(written)"
case_ "check releases the merge of the shards as they are" 0 "^MODELDONE" env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
mv $GS/${NAME}_low_s0_raw/object_library.py $T/low_object_library.kept
case_ "check with a reference of check 6 that lost a file stops" 1 "run hpc/build_geo.sh low" \
  env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
case_ "... and low writes it again" 0 "^LOWDONE" geo low $N
[ "$(written)" = "${NAME}_low_s0_raw prov_only=0 " ] || fail "... calls: $(written)"
rm -rf $GS/${NAME}_s1_raw
case_ "merge stops when a shard is not written" 1 "not complete" geo merge $N
case_ "... and check does not release the model of the earlier merge" 1 "not the merge of the shards|is not written|no $GS" \
  env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
grep -q MODELDONE $T/out && fail "... it printed MODELDONE"
case_ "... nor does it after the shard is written again" 1 "not the merge of the shards|no $GS" \
  bash -c "env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N > /dev/null && env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N"
case_ "... until it is merged again" 0 "^MODELDONE" \
  bash -c "bash $R/hpc/build_geo.sh merge $N > /dev/null && env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N"
rm -rf $GS/${NAME}_s2_raw; env GEO_FRESH=0 bash $R/hpc/build_geo.sh write $N > /dev/null
case_ "check after a shard was written again since the merge stops" 1 "not the merge of the shards" \
  env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
geo merge $N > /dev/null

case_ "check without MG5_DIR stops before the release" 1 "set MG5_DIR" env -u MG5_DIR GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
grep -q MODELDONE $T/out && fail "... and printed MODELDONE"
case_ "check whose release fails: no MODELDONE" 1 "stopped" \
  env STUB_RELEASE_RC=1 MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
grep -q MODELDONE $T/out && fail "... and printed MODELDONE"
rm -f $B/logs/$NAME/check.log; mkdir -p $B/logs/$NAME/check.log
case_ "check follows the release when its log cannot be written" 0 "^MODELDONE" \
  env MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N
rmdir $B/logs/$NAME/check.log
case_ "check requires every check of the release (DIM8_GEO_STRICT=1)" 0 "^MODELDONE" \
  env STUB_STRICT=1 MG5_DIR=$T/mg GEO_REF=$T/ref bash $R/hpc/build_geo.sh check $N

case_ "a fresh write removes the merged model of an earlier one" 0 "WRITEDONE" env GEO_FRESH=1 bash $R/hpc/build_geo.sh write $N
[ -e $GS/${NAME}_raw ] && fail "... $GS/${NAME}_raw is still there"

# examples/release_model.sh itself, strict, without the provenance of check 4
Q=$T/rel; mkdir -p $Q/examples $Q/models $T/ufo; cp $here/examples/release_model.sh $Q/examples/
case_ "release_model.sh with DIM8_GEO_STRICT=1 and no provenance stops at once" 1 "release stopped: .*check 4" \
  env -u DIM8_GEO_PROV DIM8_GEO_STRICT=1 MG5_DIR=$T/mg DIM8_GEO_REF=$T/ref bash $Q/examples/release_model.sh $T/ufo dim68_mw_geo2
[ -e $Q/models/dim68_mw_geo2_new ] && fail "... after it copied the model into models/"

# all from another directory by a relative path, the checkout found from it: the sources step runs (and stops at
# gen/derive_geo.py, which the sandbox does not have)
rel=$(python3 -c "import os, sys; print(os.path.relpath(sys.argv[1], sys.argv[2]))" $R/hpc/build_geo.sh $T/x/elsewhere)
case_ "all by a relative path from another directory runs its first step" 1 "is missing: gen/derive_geo.py" \
  env -u DIM8_ROOT bash -c "cd $T/x/elsewhere && bash $rel all $N"
grep -q "No such file" $T/out && fail "... could not find itself"

# hpc/run_parts.sh, with validate/cache_source.py itself on a block G8op1 of a model of order 2, and a worker that
# writes the file of each step (the chunks, the parts, and at the merge the block with the stamp of its source)
P=$T/parts; mkdir -p $P/hpc $P/validate $P/tests/gen_smoke $P/v
cp $here/hpc/run_parts.sh $P/hpc/; cp $here/validate/cache_source.py $P/validate/
printf 'G8op1 := cX1 Phi^2 ;\n' > $P/tests/gen_smoke/gen_geo2.fr
printf 'MW := 80.4 ;\n' > $P/tests/gen_smoke/base_geo2_mw.fr; printf 'G6cl4 := cHG ;\n' > $P/tests/gen_smoke/dim6_geo.fr
cat > $T/wsp <<'EOF'
#!/bin/bash
# the stub of the worker: -file fr_worker.wls "<block>," 0 0 0 <recursion>, the step in DIM8_PART
b=${3%,}; p=$DIM8_PART; v=$DIM8_VDIR
echo "$p" >> "$STUB_CALLS"
case $p in
  prep|prep/*) echo chunks > "$v/$b.chunks.mx" ;;
  merge/*) [ -n "${STUB_MERGE_FAILS:-}" ] && exit 1
           echo block > "$v/$b.mx"
           echo "$b | tEval 1 | tVert 1 | src $(python3 "$DIM8_ROOT/validate/cache_source.py" hash "$b")" > "$v/$b.status" ;;
  */*) echo part > "$v/$b.part${p%/*}of${p#*/}.mx" ;;
esac
EOF
chmod +x $T/wsp
parts() { env DIM8_ROOT=$P DIM8_VDIR=$P/v DIM8_BASE="$BASES" DIM8_PARTS_LOG=$T/plog WS=$T/wsp \
            bash $P/hpc/run_parts.sh G8op1 2; }
cut_short() {   # a run of two parts cut short after part 1, from the source whose stamp is $1 (none: an older script)
  rm -f $P/v/G8op1.*; echo old > $P/v/G8op1.chunks.mx; echo old > $P/v/G8op1.part1of2.mx
  [ "$1" = none ] || echo "$1" > $P/v/G8op1.parts.src
}
cur=$(env DIM8_BASE="$BASES" python3 $P/validate/cache_source.py hash G8op1)
cut_short 0123456789abcdef
case_ "run_parts on a block cut short before its source changed starts afresh" 0 "starting afresh" parts
[ "$(sort $T/calls | tr '\n' ' ')" = "1/2 2/2 merge/2 prep " ] && echo "ok   ... with the expansion and both parts computed again" \
  || fail "... steps run: $(written)"
cut_short none
case_ "run_parts on the files of a run without a record of its source starts afresh" 0 "starting afresh" parts
cut_short "$cur"
case_ "run_parts on a block cut short with its source unchanged takes it up" 0 "" parts
[ "$(written)" = "2/2 merge/2 " ] && echo "ok   ... computing part 2 and the merge alone" || fail "... steps run: $(written)"
# a block built from an older source, its parts all computed, and a merge that fails before it gets to the block
cut_short "$cur"; echo old > $P/v/G8op1.part2of2.mx; echo old > $P/v/G8op1.mx
echo "G8op1 | tEval 1 | tVert 1 | src 0123456789abcdef" > $P/v/G8op1.status
export STUB_MERGE_FAILS=1
case_ "run_parts whose merge fails beside an older block's status line fails" 1 "no block built from the current source" parts
unset STUB_MERGE_FAILS
[ -f $P/v/G8op1.part1of2.mx ] && [ -f $P/v/G8op1.part2of2.mx ] && echo "ok   ... and keeps the parts" || fail "... and deleted the parts"

echo
[ $fails = 0 ] && echo "all passed" || echo "$fails failed"
exit $((fails > 0))
