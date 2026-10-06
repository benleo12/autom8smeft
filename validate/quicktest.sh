#!/bin/bash
# A fifteen-minute acceptance test of models/dim8_is, for someone who has not built it and does
# not intend to read the pipeline.  Every test states the number it expects BEFORE it runs, so a
# disagreement is a result and not a judgement call.
#
#     validate/quicktest.sh [/path/to/MG5_aMC] [/path/to/scratch]
#
# Tests 1 and 2 need no MadGraph and take five seconds.  Tests 3 to 6 each generate 5000 events
# on one core.  Run it from the top of the repository.

set -u
MG=${1:-${MG5_DIR:-/path/to/MG5_aMC}}
S=${2:-$PWD/.quicktest}
PY=${DIM8_PY:-python3.11}
REPO=$(cd "$(dirname "$0")/.." && pwd)
MODEL=$REPO/models/dim8_is
mkdir -p "$S"
pass=0; fail=0

# Diagnose the two things that are wrong on somebody else's machine, rather than letting tests 3
# to 6 fall through an empty cross section into float("") and print a traceback each.
command -v "$PY" > /dev/null || PY=python3
command -v "$PY" > /dev/null || { echo "no python3 on PATH"; exit 2; }
[ -x "$MG/bin/mg5_aMC" ] || {
    echo "no mg5_aMC under $MG"
    echo "pass the MadGraph directory as the first argument: validate/quicktest.sh /path/to/MG5_aMC"
    echo "tests 1 and 2 need no MadGraph and are worth running on their own:"
    echo "    $PY validate/truncation_check.py $MODEL"
    echo "    $PY validate/eval_ufo_params.py  $MODEL"
    exit 2
}
"$PY" -c "import sys; sys.exit(0 if sys.version_info[:2] == (3, 11) else 1)" || \
    echo "warning: MadGraph 3.5 wants python 3.11 here (3.12 disables reweighting, 3.13 breaks model_reader)" 

say()  { printf '\n=== %s\n' "$*"; }
check() {   # check <name> <value> <expected> <tolerance>
    "$PY" - "$@" <<'PY'
import sys
name, v, e, tol = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
ok = abs(v - e) <= tol
print(f"    {'PASS' if ok else 'FAIL'}  {name}: got {v:.6g}, expected {e:.6g} +- {tol:.3g}")
sys.exit(0 if ok else 1)
PY
    if [ $? -eq 0 ]; then pass=$((pass+1)); else fail=$((fail+1)); fi
}

xsec() {    # xsec <run label> <settings...>  -> prints the cross section in pb
    local d=$S/ww_$1; shift
    "$PY" "$REPO/examples/studies/set_cards.py" "$d" nevents=5000 ebeam1=6800 ebeam2=6800 \
        hel_recycling=False "$@" > "$d/../cards.log" 2>&1
    "$d/bin/generate_events" -f run_01 > "$d/../gen_events.log" 2>&1 < /dev/null
    grep -h 'Cross-section' "$d/../gen_events.log" | tail -1 | sed 's/.*: *//; s/ .*//'
}

build() {   # build <label> <order>
    local d=$S/ww_$1
    [ -d "$d" ] && return 0
    printf 'import model %s\ngenerate p p > w+ w- %s\noutput %s\n' "$MODEL" "$2" "$d" > "$S/$1.mg5"
    "$PY" "$MG/bin/mg5_aMC" -f "$S/$1.mg5" > "$S/$1.gen.log" 2>&1 < /dev/null
    printf 'run_mode = 2\nnb_core = 1\n' >> "$d/Cards/me5_configuration.txt"
}

# ---------------------------------------------------------------- 1. truncation, no MadGraph
say "1. the input scheme is truncated at 1/Lambda^4 and nothing beyond survives (5 s)"
"$PY" "$REPO/validate/truncation_check.py" "$MODEL" > "$S/trunc.txt" 2>&1
r1=$(grep -m1 'largest quadratic/linear' "$S/trunc.txt" | sed 's/.*: //')
r2=$(grep    'largest quadratic/linear' "$S/trunc.txt" | tail -1 | sed 's/.*: //')
echo "    quadratic remainder at c=1e-3: $r1, at c=5e-4: $r2 (must halve)"
check "quadratic remainder halves when c halves" \
      "$("$PY" -c "print($r1/$r2)")" 2 0.1

# ---------------------------------------------------------------- 2. SM parameters, no MadGraph
say "2. at zero coefficients the derived parameters are the Standard Model's (1 s)"
"$PY" "$REPO/validate/eval_ufo_params.py" "$MODEL" > "$S/params.txt" 2>&1
check "M_W from {alpha, MZ, GF}" "$(awk '/^MW  /{print $3}' "$S/params.txt")" 79.82435975 1e-6
check "v"                        "$(awk '/^vevT/{print $3}' "$S/params.txt")" 246.2205691 1e-6

# ---------------------------------------------------------------- 3. the Standard Model limit
say "3. the SM limit reproduces MadGraph's own sm model (2 min)"
build sm0 "NP=0"
check "p p > w+ w- at c = 0" "$(xsec sm0 dim8_all=0)" 68.05 0.6
echo "    reference: the stock sm model with the same inputs (aEWM1 127.9, MZ 91.1876, MT 172)"
echo "    gives 68.05 +- 0.24 pb"

# ---------------------------------------------------------------- 4. the interference
say "4. the 1/Lambda^4 interference, all 1030 coefficients at 1, Lambda = 1 TeV (3 min)"
build int "NP^2==2"
i1000=$(xsec int dim8_all=1 lam__2=1000)
check "interference at Lambda = 1 TeV" "$i1000" -3.998 0.06

# ---------------------------------------------------------------- 5. the Lambda scaling
say "5. that interference falls as 1/Lambda^4 (3 min)"
i2000=$(xsec int dim8_all=1 lam__2=2000)
check "interference at Lambda = 2 TeV" "$i2000" "$("$PY" -c "print($i1000/16)")" 0.01
echo "    the expected answer is NOT exactly i(1 TeV)/16.  A 0.8 per cent deficit is physical and"
echo "    measured: the W mass shifts by 0.625 per cent at c = 1 and Lambda = 1 TeV, it carries no"
echo "    order tag, and the Standard-Model half of the interference is evaluated at that shifted"
echo "    mass.  A fit to A/Lambda^4 + B/Lambda^8 gives B/A = 0.85 per cent and predicts the 3 TeV"
echo "    point at 0.27 sigma, where pure 1/Lambda^4 misses it by 3.2.  A deviation much larger"
echo "    than one per cent, or one that does not fall as 1/Lambda^8, would be the real failure."

# ---------------------------------------------------------------- 6. the square
say "6. the dimension-eight square (5 min)"
build sq "NP<=2 NP^2==4"
check "square at Lambda = 1 TeV" "$(xsec sq dim8_all=1 lam__2=1000)" 3989 100
echo "    this is 59 times the Standard Model, which is the truncation failing at c = 1 and"
echo "    Lambda = 1 TeV in an inclusive sample, not the model being wrong"

printf '\n%s passed, %s failed\n' "$pass" "$fail"
[ "$fail" -eq 0 ]
