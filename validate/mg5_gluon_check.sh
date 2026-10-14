#!/bin/bash
# Gauge-invariance check of the GLUON sector of a dim8auto UFO.  A check on u u~ or u d~ initial
# states with electroweak final states touches no gluon vertex, so the gluonic vertices are tested here.
#
# Two requirements:
#  * MadGraph's `check gauge` needs a UFO that allows BOTH gauges, i.e. one written from the
#    Feynman-gauge base model (base_fg.fr, Goldstones kept) and a Feynman-gauge cache; on a
#    unitary-gauge UFO it stops with "does not allow for both Feynman and unitary gauge".
#    Such a cache is built by validate/fr_worker.wls with DIM8_BASE=base_fg.fr and a cache
#    directory of its own (DIM8_VDIR); a block without the Higgs doublet has the same vertices in
#    both gauges.  validate/fr_writeufo.wls with the same base then writes the UFO.
#  * Every Wilson coefficient defaults to 0 in the UFO, so a check on the UFO as written tests
#    only the Standard Model part and a process without an SM tree amplitude (g g > h g) has a
#    zero matrix element and no result at all.  This script therefore copies the UFO to
#    ${DIM8_BUILD:-~/dim8auto_build}/ufo/<name>_on with the coefficients switched on (by default
#    every c8 coefficient at 0.7, Lambda stays at 1 TeV; WARD_ON below), runs the checks there,
#    and runs the same checks on the untouched UFO as the coefficient-off control.  The values
#    are edited one parameter at a time, since a blanket substitution of the value can also
#    change a parameter name (c8l2WH2Dx1 into c8l2WH2Dx10.7).
#
# What the two checks probe.  For external GLUONS the unitary/Feynman comparison changes nothing
# (the gluon propagator is the same in both), so `check gauge` only tests the massive-boson sector;
# the Ward identity of external gluons is probed by `check lorentz`, because a boost shifts a
# massless polarisation vector by a term proportional to its momentum.  On the plain
# (unitary-gauge base) model the Lorentz check FAILS at the 1e-4 level for g g > g g,
# u u~ > g g, g g > g g g when Q_{G^2H^4}^{(1)} is switched on, and passes at 1e-15 with the nine
# X^4 operators alone or with G^3H^2: the vev of (H^dag H)^2 G G shifts the gluon kinetic term,
# FeynRules writes no two-point vertex into the UFO, and the three- and four-gluon vertices it
# does write are then inconsistent with the unshifted propagator at O(v^4/Lambda^4).  Such
# operators need the input-scheme (canonically normalised) model: use a *_is UFO for them.
#
# Runs `check gauge` (unitary vs Feynman gauge at one phase-space point, on a UFO that allows
# both gauges) and `check lorentz` on u u~ > g g, g g > h g, g g > g g and g g > g g g at one
# dim-8 insertion (NP<=2 unless WARD_ORDER says otherwise).  The five-gluon process exercises
# the five-point vertices; six-point vertices would need g g > g g g g.
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
  PLIST=()   # a read loop, not mapfile, which the bash 3.2 of macOS lacks; one process per line
  while IFS= read -r pr; do case ${pr// /} in ""|\#*) continue;; esac; PLIST+=("$pr"); done < "$PROCS"
else
  PLIST=("u u~ > g g" "g g > h g" "g g > g g" "g g > g g g")
fi
echo "processes: ${#PLIST[@]}"
# A unitary-gauge UFO cannot run `check gauge` ("does not allow for both Feynman and unitary
# gauge"), but `check lorentz`, the gluon Ward-identity test that catches a mis-normalised gluon
# kinetic term, works on it.  Run what the UFO allows and say which.
TWOGAUGE=0
grep -q "gauge = \[0, 1\]" "$UFO/__init__.py" && TWOGAUGE=1
[ $TWOGAUGE = 1 ] || echo "note: $UFO allows only the unitary gauge, so this runs the Lorentz (Ward) checks alone. A gauge check needs a model written from base_fg.fr, by validate/fr_worker.wls with DIM8_BASE=base_fg.fr and its own DIM8_VDIR, then validate/fr_writeufo.wls."

# The coefficients-on copy lives OUTSIDE any synced folder: removing and recreating a model
# directory under Dropbox mid-sync can restore the old files beside the new ones as "conflicted
# copies", and a check would then run an earlier command list.
ON="${DIM8_BUILD:-$HOME/dim8auto_build}/ufo/$(basename "$UFO")_on"
mkdir -p "$(dirname "$ON")"
rm -rf "$ON"; cp -r "$UFO" "$ON"; rm -rf "$ON/__pycache__"
# Which coefficients the ON copy switches on, and to what order the amplitudes are taken:
#   WARD_ON=dim8   (default) every dimension-eight coefficient at 0.7
#   WARD_ON=dim6   every real dimension-six coefficient of block DIM6, at a spread of values
#   WARD_ON=both   both sets
#   WARD_ORDER     the amplitude order, default NP<=2; NP<=1 is the linear dimension-six test
# With only c8* switched on, the dimension-six sector of a combined model is not tested at all.
# The dimension-six option tests it: QCD gauge invariance of its gluon operators at 1/Lambda^2,
# and the photon's Ward identity for the products of an operator with the input-scheme shifts
# at 1/Lambda^4.  validate/procs_dim6.txt is the list for it.
WARD_ON=${WARD_ON:-dim8}; WARD_ORDER=${WARD_ORDER:-NP<=2}
$PY - "$ON/parameters.py" "$WARD_ON" <<'EOF'
import re, sys
p, which = sys.argv[1], sys.argv[2]
blocks = open(p).read().split("\n\n")
spread = [0.3, -0.2, 0.25, 0.15, 0.1, -0.1, 0.2, -0.3, 0.35]
n8 = n6 = 0
for i, b in enumerate(blocks):
    m = re.match(r"\s*(\w+) = Parameter\(name = '(\w+)',\s*nature = 'external'", b)
    if not m: continue
    name = m.group(2)
    if which in ("dim8", "both") and name.startswith("c8") and re.search(r"value = 0,?\s*$", b, re.M):
        blocks[i] = re.sub(r"value = 0(,?\s*)$", r"value = 0.7\1", b, count=1, flags=re.M); n8 += 1
    elif which in ("dim6", "both") and "lhablock = 'DIM6'" in b and name != "Lam6" and not name.endswith("Ph"):
        blocks[i] = re.sub(r"value = [^,]*,", "value = %s," % spread[n6 % len(spread)], b, count=1); n6 += 1
open(p, "w").write("\n\n".join(blocks))
print(f"[on] {n8} dimension-eight coefficients set to 0.7 and {n6} dimension-six coefficients switched on in {p}")
if n8 + n6 == 0: sys.exit("[on] nothing was switched on: the check would only repeat the control")
EOF

run () { # $1 = UFO dir, $2 = tag.  Gauge and Lorentz checks in SEPARATE MadGraph sessions: within
  # one session `check lorentz` skips a process whose matrix element the gauge check already
  # evaluated ("identical matrix element already tested") and reports 0/0.
  local log=$1/mg5_gluon_check.log
  : > $log
  if [ $TWOGAUGE = 1 ]; then
    { echo "import model $1 --modelname"; for pr in "${PLIST[@]}"; do echo "check gauge $pr $WARD_ORDER"; done; } > $1/mg5_gauge.cmd
    $PY $MG/bin/mg5_aMC -f $1/mg5_gauge.cmd > $log 2>&1 || true
  fi
  { echo "import model $1 --modelname"; for pr in "${PLIST[@]}"; do echo "check lorentz $pr $WARD_ORDER"; done; } > $1/mg5_lorentz.cmd
  $PY $MG/bin/mg5_aMC -f $1/mg5_lorentz.cmd >> $log 2>&1 || true
  echo "== $2: $1"
  grep -E "^check |Process  |Passed|Failed|Summary|Not checked|InvalidCmd|Error" $log | grep -vE "Interpreting|Samurai|JAMP|^\s*$" | cut -c1-120
  echo "log: $log"
}
run "$ON" "coefficients ON ($WARD_ON, $WARD_ORDER, Lambda 1 TeV)"
run "$UFO" "coefficients OFF (control)"
