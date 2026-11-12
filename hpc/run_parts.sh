#!/bin/bash
# One block by many processes at once.  Feynman rules are linear in the Lagrangian, and validate/fr_worker.wls
# computes a block chunk by chunk, so the chunks can be computed side by side (DIM8_PART in the worker):
# the block is expanded, monomial by monomial in M processes, its chunks are computed in N parts, and the
# parts are joined in the order of the chunks into the block a single run gives.  That brings the heaviest
# blocks, ten hours and more on one kernel, under an hour.
#
#   hpc/run_parts.sh BLOCK N [M]
#
# with M = 1, the default, for an expansion in one process.  The environment is that of the worker
# (DIM8_ROOT, DIM8_BASE, DIM8_VDIR, DIM8_HERM, DIM8_CHUNK, ...), the same for every step, since the
# expansion and chunk files record the options they were made with and the later steps stop on any other.
# A run cut short (a preempted job) is taken up again: a block whose stamp is current is left alone, and an
# expansion or a part whose file is there is not computed again, as long as the source of the block is the one
# they were made from (<block>.parts.src, its stamp by validate/cache_source.py).  Otherwise they go and the
# block starts afresh, since the worker checks its chunk file against the definition of the block alone and not
# against the base it is evaluated on.  The intermediate files go once the block is written.  A block of the release, L8op<n>, goes to the worker by its number, any other (the blocks of the
# models of order N, G6cl*, G8op*, T<d>op*, hpc/build_geo.sh) by its name.  DIM8_PARTS_LOG sets the directory of
# the logs (default logs/parts) and DIM8_RECURSION the recursion limit of the kernels (default 2500, FeynRules'
# own, which the dimension-six class blocks of the models of order N go past, so hpc/build_geo.sh sets 10000).
set -u
root=${DIM8_ROOT:?set DIM8_ROOT}
b=$1; n=$2; m=${3:-1}
vdir=${DIM8_VDIR:-$root/build/vertices}
log=${DIM8_PARTS_LOG:-$root/logs/parts}
mkdir -p "$log"
case $b in L8op[0-9]*) which="${b#L8op} 0 674" ;; *) which="$b, 0 0" ;; esac
export root b log which
step() {   # step DIM8_PART log-tag
  DIM8_PART=$1 "${WS:-wolframscript}" -file "$root/validate/fr_worker.wls" $which 0 "${DIM8_RECURSION:-2500}" > "$log/${b}_$2.log" 2>&1
}
export -f step
# "current" printed, and not an exit status, which a Python that fails to run would give as well
state() {
  python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import cache_source as C; print(C.state(sys.argv[2], sys.argv[3]))' \
    "$root/validate" "$vdir" "$b" 2>/dev/null
}
state=$(state)
if [ "$state" = current ]; then
  echo "$b: built from the current source already, $(cut -d'|' -f2-7 "$vdir/$b.status")"
  exit 0
fi
t0=$(date +%s)
src=$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import cache_source as C; print(C.source_hash(sys.argv[2]))' \
      "$root/validate" "$b" 2>/dev/null)
[ -n "$src" ] || { echo "$b: no stamp of its source (python3 validate/cache_source.py hash $b)"; exit 1; }
if [ "$(cat "$vdir/$b.parts.src" 2> /dev/null)" != "$src" ]; then
  for f in "$vdir/$b".chunks.mx "$vdir/$b".part*of*.mx "$vdir/$b".exp*of*.mx; do
    [ -e "$f" ] && { echo "$b: the files of a run cut short are not of the current source, starting afresh"; break; }
  done
  rm -f "$vdir/$b".chunks.mx "$vdir/$b".part*of*.mx "$vdir/$b".exp*of*.mx
  echo "$src" > "$vdir/$b.parts.src"
fi
if [ ! -f "$vdir/$b.chunks.mx" ]; then
  if [ "$m" -gt 1 ]; then
    seq 1 "$m" | while read -r i; do [ -f "$vdir/$b.exp${i}of$m.mx" ] || echo "$i"; done \
      | xargs -r -P "$m" -I{} bash -c "step expand/{}/$m exp{}"
    for i in $(seq 1 "$m"); do
      [ -f "$vdir/$b.exp${i}of$m.mx" ] || { echo "$b: expansion $i of $m failed, see $log/${b}_exp$i.log"; exit 1; }
    done
    step "prep/$m" prep
  else
    step prep prep
  fi
fi
[ -f "$vdir/$b.chunks.mx" ] || { echo "$b: the expansion left no chunk file, see $log/${b}_prep.log"; exit 1; }
seq 1 "$n" | while read -r i; do [ -f "$vdir/$b.part${i}of$n.mx" ] || echo "$i"; done \
  | xargs -r -P "$n" -I{} bash -c "step {}/$n {}"
for i in $(seq 1 "$n"); do
  [ -f "$vdir/$b.part${i}of$n.mx" ] || { echo "$b: part $i of $n failed, see $log/${b}_$i.log"; exit 1; }
done
step "merge/$n" merge
# the block built from its current source, and not the status line of an older build that a merge which failed
# before it got to the block left in place: until then the parts are kept, and a run again merges them
state=$(state)
[ "$state" = current ] || { echo "$b: the merge left no block built from the current source ($state), see $log/${b}_merge.log; the parts are kept"; exit 1; }
rm -f "$vdir/$b.chunks.mx" "$vdir/$b.part"*"of$n.mx" "$vdir/$b.exp"*"of$m.mx" "$vdir/$b.parts.src"
echo "$b: $(cut -d'|' -f2-7 "$vdir/$b.status") in $(( $(date +%s) - t0 )) s with $m expansions and $n parts"
