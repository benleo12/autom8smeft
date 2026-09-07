#!/bin/bash
# Gauge-invariance check of the GLUON sector of a dim8auto UFO: the earlier V10 checks used
# u u~ / u d~ initial states and never touched a gluon vertex, which is how an unsound colour
# zero test in the worker went unnoticed for five days (the development log, not shipped, 2026-09-03).
#
# Two things the first version got wrong (2026-09-06):
#  * MadGraph's `check gauge` needs a UFO that allows BOTH gauges, i.e. one written from the
#    Feynman-gauge base model (base_fg.fr, Goldstones kept) and a Feynman-gauge cache; on a
#    unitary-gauge UFO it stops with "does not allow for both Feynman and unitary gauge".
#    hpc/run_fg.sh builds that cache and writes <name>_fg.
#  * Every Wilson coefficient defaults to 0 in the UFO, so a check on the UFO as written tests
#    only the Standard Model part and a process without an SM tree amplitude (g g > h g) has a
#    zero matrix element and no result at all.  This script therefore copies the UFO to <UFO>_on
#    with every c8 coefficient at 0.7 (Lambda stays at 1 TeV), edited value line by value line
#    (a blanket sed once turned "c8l2WH2Dx1 ... 1" into "c8l2WH2Dx10.7"), runs the checks
#    there, and runs the same gauge checks on the untouched UFO as the coefficient-off control.
#
# What the two checks probe.  For external GLUONS the unitary/Feynman comparison changes nothing
# (the gluon propagator is the same in both), so `check gauge` only tests the massive-boson sector;
# the Ward identity of external gluons is probed by `check lorentz`, because a boost shifts a
# massless polarisation vector by a term proportional to its momentum.  Finding (2026-09-06): on
# the plain (unitary-gauge base) model the Lorentz check FAILS at the 1e-4 level for g g > g g,
# u u~ > g g, g g > g g g when Q_{G^2H^4}^{(1)} is switched on, and passes at 1e-15 with the nine
# X^4 operators alone or with G^3H^2: the vev of (H^dag H)^2 G G shifts the gluon kinetic term,
# FeynRules writes no two-point vertex into the UFO, and the three- and four-gluon vertices it
# does write are then inconsistent with the unshifted propagator at O(v^4/Lambda^4).  Such
# operators need the input-scheme (canonically normalised) model: use a *_is UFO for them.
#
# Runs `check gauge` (unitary vs Feynman gauge at one phase-space point) on u u~ > g g,
# g g > h g, g g > g g and g g > g g g at one dim-8 insertion (NP<=2), and `check lorentz`
# on g g > g g, g g > h g and g g > g g g.  The five-gluon process exercises the five-point
# vertices; six-point vertices would need g g > g g g g.
# A third argument replaces the gluonic process list with one read from a file, one process per
# line, which is how the electroweak sector is checked: an external photon has the same Ward
# identity as an external gluon, so `check lorentz` on processes with photons tests the B and W
# kinetic form factors d8fB and d8fW and the photon-Z rotation the way the gluon processes test
# d8fG.  validate/procs_ew.txt is that list.
# usage: validate/mg5_gluon_check.sh <UFO dir> [MG5 dir] [process list]      needs python 3.11
set -e
UFO=$(cd "${1:?UFO directory}" && pwd)
MG=${2:-${MG5_DIR:-${MG5_DIR:-/path/to/MG5_aMC}}}
[ -x "$MG/bin/mg5_aMC" ] || { echo "MG5 not found (pass the directory as the second argument or set MG5_DIR)"; exit 2; }
PY=$(command -v python3.11 || command -v python3)
PROCS=${3:-}
if [ -n "$PROCS" ]; then
  [ -f "$PROCS" ] || { echo "no such process list: $PROCS"; exit 2; }
  PLIST=()   # a read loop, not mapfile: this machine's bash is 3.2, and word splitting would
  while IFS= read -r pr; do case ${pr// /} in ""|\#*) continue;; esac; PLIST+=("$pr"); done < "$PROCS"
else
  PLIST=("u u~ > g g" "g g > h g" "g g > g g" "g g > g g g")
fi
echo "processes: ${#PLIST[@]}"
# A unitary-gauge UFO cannot run `check gauge` ("does not allow for both Feynman and unitary
# gauge"), but `check lorentz` -- the gluon Ward-identity test, and the one that catches a
# mis-normalised gluon kinetic term -- works on it.  Run what the UFO allows and say which.
TWOGAUGE=0
grep -q "gauge = \[0, 1\]" "$UFO/__init__.py" && TWOGAUGE=1
[ $TWOGAUGE = 1 ] || echo "note: $UFO allows only the unitary gauge, so this runs the Lorentz (Ward) checks alone. A gauge check needs a model written from base_fg.fr with hpc/run_fg.sh."

ON="${UFO}_on"
rm -rf "$ON"; cp -r "$UFO" "$ON"; rm -rf "$ON/__pycache__"
$PY - "$ON/parameters.py" <<'EOF'
import re, sys
p = sys.argv[1]
lines = open(p).read().split("\n")
out, pending, n = [], False, 0
for l in lines:
    if re.match(r"\w+ = Parameter\(name = 'c8\w+'", l): pending = True
    if pending and re.match(r"\s*value = 0,?\s*$", l):
        l = l.replace("value = 0", "value = 0.7"); n += 1; pending = False
    elif pending and "value =" in l:
        pending = False
    out.append(l)
open(p, "w").write("\n".join(out))
print(f"[on] {n} Wilson coefficients set to 0.7 in {p}")
EOF

run () { # $1 = UFO dir, $2 = tag.  Gauge and Lorentz checks in SEPARATE MadGraph sessions: within
  # one session `check lorentz` skips a process whose matrix element the gauge check already
  # evaluated ("identical matrix element already tested") and reports 0/0.
  local log=$1/mg5_gluon_check.log
  : > $log
  if [ $TWOGAUGE = 1 ]; then
    { echo "import model $1 --modelname"; for pr in "${PLIST[@]}"; do echo "check gauge $pr NP<=2"; done; } > $1/mg5_gauge.cmd
    $PY $MG/bin/mg5_aMC -f $1/mg5_gauge.cmd > $log 2>&1 || true
  fi
  { echo "import model $1 --modelname"; for pr in "${PLIST[@]}"; do echo "check lorentz $pr NP<=2"; done; } > $1/mg5_lorentz.cmd
  $PY $MG/bin/mg5_aMC -f $1/mg5_lorentz.cmd >> $log 2>&1 || true
  echo "== $2: $1"
  grep -E "^check |Process  |Passed|Failed|Summary|Not checked|InvalidCmd|Error" $log | grep -vE "Interpreting|Samurai|JAMP|^\s*$" | cut -c1-120
  echo "log: $log"
}
run "$ON" "coefficients ON (0.7, Lambda 1 TeV)"
run "$UFO" "coefficients OFF (control)"
