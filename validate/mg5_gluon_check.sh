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
# the five-point vertices.  The vertices of six and more gluons are also tested as vertices, by
# validate/g4_highleg.py check and ufo.  MadGraph 3.5.6 names some combined ALOHA routines inconsistently,
# and without the fix that every model carries in its __init__.py (examples/mg5_fixes.py) check stops
# on g g > g g g g, and on u u~ > t t~ g and u u~ > t t~ a of validate/procs_dim6.txt at NP<=2, with
# "NameError: name 'ALOHA_<hash>P0_1' is not defined".  With the fix all three pass (2026-11-05).  Should the
# error appear again, the script reports the process as not evaluated and runs the processes after it in
# a new session.
# A third argument replaces the gluonic process list with one read from a file, one process per
# line, which is how the electroweak sector is checked: an external photon has the same Ward
# identity as an external gluon, so `check lorentz` on processes with photons tests the B and W
# kinetic form factors d8fB and d8fW and the photon-Z rotation the way the gluon processes test
# d8fG.  validate/procs_ew.txt is that list.  validate/procs_mfv.txt adds the processes in which the
# flavour structures of block DIM8F act: external t and b, light quarks and leptons of every generation,
# charged currents across generations, and four external fermions with a photon or a gluon.  On the default
# card those structures vanish wherever they need a light Yukawa coupling or the Cabibbo angle, so that list
# is meant for WARD_INPUTS=generic below.
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
  NONE=()    # a line starting with ! is a process that must have no matrix element at this order
  while IFS= read -r pr; do
    case ${pr// /} in ""|\#*) continue;; \!*) pr=${pr#!}; pr=${pr# }; NONE+=("$pr");; esac
    PLIST+=("$pr")
  done < "$PROCS"
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
#   WARD_ON=dim6   every dimension-six coefficient of block DIM6, at a spread of values, and the
#                  phase of each complex one (the parameters ending in Ph) at a spread of angles
#   WARD_ON=both   both sets
#   WARD_ORDER     the amplitude order, default NP<=2; NP<=1 is the linear dimension-six test
# With only c8* switched on, the dimension-six sector of a combined model is not tested at all.
# The dimension-six option tests it: QCD gauge invariance of its gluon operators at 1/Lambda^2,
# and the photon's Ward identity for the products of an operator with the input-scheme shifts
# at 1/Lambda^4.  validate/procs_dim6.txt is the list for it.
#   WARD_INPUTS    card (default): the inputs of the model's card.  generic: every input that is zero on
#                  the card, the light Yukawa masses and cabi, at a value of its own (validate/generic_inputs.py),
#                  in the ON copy and in a copy <name>_off for the control, which then runs there with the
#                  coefficients off and the same inputs.  On the default card a coupling proportional to a light
#                  Yukawa coupling or to the Cabibbo angle vanishes, and with it most of block DIM8F.
WARD_ON=${WARD_ON:-dim8}; WARD_ORDER=${WARD_ORDER:-NP<=2}; WARD_INPUTS=${WARD_INPUTS:-card}
HERE=$(cd "$(dirname "$0")" && pwd)
switch () { # $1 = parameters.py, $2 = the coefficients to switch on (dim8, dim6, both, or none for the control)
$PY - "$1" "$2" "$WARD_INPUTS" "$HERE" <<'EOF'
import re, sys
p, which, inputs = sys.argv[1], sys.argv[2], sys.argv[3]
sys.path.insert(0, sys.argv[4])
from generic_inputs import COEFFICIENT_BLOCKS, generic_value
blocks = open(p).read().split("\n\n")
spread = [0.3, -0.2, 0.25, 0.15, 0.1, -0.1, 0.2, -0.3, 0.35]
angles = [0.7, -1.2, 2.1, 0.4, -2.6, 1.5]
n8 = n6 = nph = 0
moved = []
for i, b in enumerate(blocks):
    m = re.match(r"\s*(\w+) = Parameter\(name = '(\w+)',\s*nature = 'external'", b)
    if not m: continue
    name = m.group(2)
    block = re.search(r"lhablock = '(\w+)'", b).group(1)
    # a zero default is "0" from FeynRules under Mathematica 14 and "0." under Mathematica 15
    if which in ("dim8", "both") and name.startswith("c8") and re.search(r"value = 0\.?0*,?\s*$", b, re.M):
        blocks[i] = re.sub(r"value = 0\.?0*(,?\s*)$", r"value = 0.7\1", b, count=1, flags=re.M); n8 += 1
    elif which in ("dim6", "both") and "lhablock = 'DIM6'" in b and name.endswith("Ph"):
        blocks[i] = re.sub(r"value = [^,]*,", "value = %s," % angles[nph % len(angles)], b, count=1); nph += 1
    elif which in ("dim6", "both") and "lhablock = 'DIM6'" in b:
        blocks[i] = re.sub(r"value = [^,]*,", "value = %s," % spread[n6 % len(spread)], b, count=1); n6 += 1
    elif inputs == "generic" and block not in COEFFICIENT_BLOCKS + ("DECAY",) and re.search(r"value = 0\.?0*,?\s*$", b, re.M):
        v = generic_value(name, 0.0, block)
        blocks[i] = re.sub(r"value = 0\.?0*(,?\s*)$", r"value = %r\1" % v, b, count=1, flags=re.M); moved.append(f"{name}={v:.4f}")
open(p, "w").write("\n\n".join(blocks))
print(f"[on] {n8} dimension-eight coefficients set to 0.7 and {n6} dimension-six coefficients switched on, "
      f"{nph} of them complex with their phases set, in {p}")
if inputs == "generic":
    print(f"[inputs] {len(moved)} inputs that are zero on the card at generic values: {' '.join(moved)}")
    if not moved: sys.exit("[inputs] no input of the card is zero, so WARD_INPUTS=generic would change nothing")
if which != "none" and n8 + n6 == 0: sys.exit("[on] nothing was switched on: the check would only repeat the control")
EOF
}
switch "$ON/parameters.py" "$WARD_ON"
OFF="$UFO"
if [ "$WARD_INPUTS" = generic ]; then
  OFF="${ON%_on}_off"
  rm -rf "$OFF"; cp -r "$UFO" "$OFF"; rm -rf "$OFF/__pycache__"
  switch "$OFF/parameters.py" none
fi

session () { # $1 = UFO dir, $2 = check (gauge or lorentz), $3 = log.  MadGraph stops a command file at
  # the first command that raises and lists the rest as "command not executed", so the rest run again
  # in a new session and one process cannot hide the others.  The process that stopped it fails,
  # except for the hashed-name NameError of the header, a MadGraph naming bug that says nothing about the model.
  local cmd=$1/mg5_$2.cmd part=$3.part stop err
  { echo "import model $1 --modelname"; for pr in "${PLIST[@]}"; do echo "check $2 $pr $WARD_ORDER"; done; } > $cmd
  while :; do
    $PY $MG/bin/mg5_aMC -f $cmd > $part 2>&1 || true
    cat $part >> $3
    grep -aq "interrupted in sub-command" $part || break
    stop=$(sed -n 's/^"check [a-z]* \(.*\)" with error:.*/\1/p' $part | head -1)
    err=$(grep -a -A1 '^"check .*" with error:' $part | sed -n 2p | cut -c1-100)
    case $err in
      "NameError : name 'ALOHA_"*"' is not defined") echo "Not evaluated: $stop, the hashed ALOHA routine that check cannot find ($err)" >> $3;;
      *) echo "Summary: 0/1 passed, 1/1 failed: $stop stopped MadGraph ($err)" >> $3;;
    esac
    { echo "import model $1 --modelname"; sed -n 's/.*command not executed: \(.*\)/\1/p' $part | sed 's/\x1b\[[0-9;]*m//g'; } > $cmd
    [ "$(wc -l < $cmd)" -gt 1 ] || break
  done
  rm -f $part
}

run () { # $1 = UFO dir, $2 = tag.  Gauge and Lorentz checks in SEPARATE MadGraph sessions: within
  # one session `check lorentz` skips a process whose matrix element the gauge check already
  # evaluated ("identical matrix element already tested") and reports 0/0.
  local log=$1/mg5_gluon_check.log
  : > $log
  [ $TWOGAUGE = 1 ] && session $1 gauge $log
  session $1 lorentz $log
  echo "== $2: $1"
  grep -E "^check |Process  |Passed|Failed|Summary|Not checked|Not evaluated|InvalidCmd|Error" $log | grep -vE "Interpreting|Samurai|JAMP|^\s*$" | cut -c1-160
  # A process marked ! in the list must give no matrix element: MadGraph finds no diagram for it, or
  # diagrams that vanish, which it lists as not checked.  A row of results for it is a failure, whatever
  # the row says, since a spurious coupling with a sound Lorentz structure would pass `check lorentz`.
  for pr in "${NONE[@]}"; do
    if [ -n "$(awk -v p="$pr" 'index($0, p) == 1 && /Passed|Failed/' "$log")" ]; then
      echo "Summary: 0/1 passed, 1/1 failed: $pr has a matrix element where none should exist"
    else
      echo "no matrix element, as there should be none: $pr"
    fi
  done
  echo "log: $log"
}
run "$ON" "coefficients ON ($WARD_ON, $WARD_ORDER, Lambda 1 TeV, $WARD_INPUTS inputs)"
run "$OFF" "coefficients OFF (control$([ "$WARD_INPUTS" = generic ] && echo ", generic inputs"))"
