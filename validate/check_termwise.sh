#!/bin/bash
# Two-path equivalence check of the worker: the term-wise (chunked) evaluation must give the
# same vertices, coupling by coupling, as the whole-block FeynmanRules call, for a Hermitian
# row (real WC), a "+ h.c." row (complex WC) and a symmetrised row (sym).  The first term-wise
# validation used three Hermitian rows only and missed that the h.c. branch expanded
# generations differently (the development log, not shipped, 2026-09-03).  Blocks: 286 (real, class 18),
# 402 (complex, class 19), 12 (sym, class 2), all seconds to a minute each.
# usage: validate/check_termwise.sh [wolframscript]      writes to a scratch directory only
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); export DIM8_ROOT=$ROOT
WS=${1:-${WOLFRAMSCRIPT:-/Applications/Wolfram.app/Contents/MacOS/wolframscript}}
T=${TMPDIR:-/tmp}/dim8_termwise_$$; mkdir -p $T/tw $T/wb
BLOCKS="286 402 12"
for b in $BLOCKS; do
  DIM8_VDIR=$T/tw DIM8_HERM=0 $WS -file $ROOT/validate/fr_worker.wls $b 0 674 0 20000 > $T/tw_$b.log 2>&1
  DIM8_VDIR=$T/wb DIM8_TERMWISE=0 DIM8_HERM=0 $WS -file $ROOT/validate/fr_worker.wls $b 0 674 0 20000 > $T/wb_$b.log 2>&1
  printf "%-4s term-wise %-4s whole-block %s\n" $b "$(sed -E 's/.*\| vertices ([0-9]+) \|.*/\1/' $T/tw/L8op$b.status)" "$(sed -E 's/.*\| vertices ([0-9]+) \|.*/\1/' $T/wb/L8op$b.status)"
done
L=$(for b in $BLOCKS; do echo -n "L8op$b "; done)
$WS -file $ROOT/validate/compare_vertex_mx.wls $T/wb $T/tw $L 2>&1 | grep -a "^\[compare\]\|^\[alldone\]" | tee $T/ab.txt
$WS -file $ROOT/validate/compare_vertex_mx.wls $T/tw $T/wb $L 2>&1 | grep -a "^\[compare\]\|^\[alldone\]" | tee $T/ba.txt
if grep -q "mismatched 0" $T/ab.txt && grep -q "mismatched 0" $T/ba.txt; then echo "TERMWISE CHECK PASS"; rm -rf $T; else echo "TERMWISE CHECK FAIL (kept $T)"; exit 1; fi
