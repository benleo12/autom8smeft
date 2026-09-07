#!/bin/bash
# Switch the build to the numeric-SU(2) dialect and rebuild the vertex cache.
# The old cache (FeynRules' own SU(2) expansion) is kept aside: blocks that carry no SU(2)
# tensor at all must give identical vertex counts under both dialects, which is a free
# consistency test of the new emission (validate/compare_caches.py).
set -e
cd "$(dirname "$0")/.."
pkill -9 -f fr_worker.wls || true; sleep 2
python3 gen/build_catalogue.py --emit models/dev/dim8_generated.fr | tail -1
python3 validate/check_counts.py | tail -1
python3 validate/check_symbol_clash.py | tail -1
cp tests/gen_smoke/gen.fr tests/gen_smoke/gen_flavexp.fr   # kept for validate/compare_caches.py
cp models/dev/dim8_generated.fr tests/gen_smoke/gen.fr
if [ -d build/vertices ]; then rm -rf build/vertices_flavexp; mv build/vertices build/vertices_flavexp; fi
mkdir -p build/vertices build/logs
N=${1:-10}
for s in $(seq 1 $N); do
  nohup /Applications/Wolfram.app/Contents/MacOS/wolframscript -file "$PWD/validate/fr_worker.wls" $s $N 674 1 20000 > build/logs/worker_${s}_num.log 2>&1 &
done
sleep 3; echo "workers: $(pgrep -f fr_worker | wc -l | tr -d ' ')  old cache -> build/vertices_flavexp"
