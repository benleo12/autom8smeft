#!/bin/bash
# Regression test of the Levi-Civita-pair rewrite (default in fr_worker.wls, DIM8_EPSEPS=0 disables it): build the
# dual-dual Q_{G^2B^2}^{(2)} (L8op455) with and without it into scratch caches and require numeric
# equality vertex by vertex.  usage: validate/check_epseps.sh [wolframscript]
set -e
ROOT=$(cd "$(dirname "$0")/.." && pwd); export DIM8_ROOT=$ROOT
WS=${1:-${WOLFRAMSCRIPT:-/Applications/Wolfram.app/Contents/MacOS/wolframscript}}
T=${TMPDIR:-/tmp}/dim8_epseps_$$; mkdir -p $T/eps $T/det
DIM8_VDIR=$T/eps DIM8_HERM=0 DIM8_EPSEPS=0 $WS -file $ROOT/validate/fr_worker.wls 455 0 674 0 20000 > $T/eps.log 2>&1
DIM8_VDIR=$T/det DIM8_HERM=0 DIM8_EPSEPS=1 $WS -file $ROOT/validate/fr_worker.wls 455 0 674 0 20000 > $T/det.log 2>&1
grep -a "^\[epseps\]" $T/det.log
if $WS -file $ROOT/validate/compare_vertex_numeric.wls $T/eps/L8op455.mx $T/det/L8op455.mx 2>&1 | grep -a "^\[numeric\]\|DIFFERENT\|missing\|order" | tee $T/res.txt | grep -q "EQUAL$"; then echo "EPSEPS CHECK PASS"; rm -rf $T; else echo "EPSEPS CHECK FAIL (kept $T)"; exit 1; fi
