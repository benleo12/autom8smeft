#!/bin/bash
# Driver for the paper's studies: cross sections at 13.6 TeV for a list of processes, at each
# order of the Lambda expansion, for the full model and for one operator class at a time.
#   usage: examples/studies/run_study.sh <study dir> [model dir] [nevents]
# <study dir> holds processes.txt (one MadGraph process per line, run-card settings after a '|'
# as "ptj=20 mmjj=500", and after a second '|' optionally the restriction card to use for the
# "full model" rows of that process: p p > h h j j QCD=0 NP<=2 on the unrestricted model is
# 298888 diagrams in 166 subprocesses, hours of code generation per order, so the VBF study
# runs its full rows on the bosonic card) and classes.txt (one restriction-card name per line, cards written
# beforehand with validate/make_restriction.py into the model directory).  Optionally
# coefficients.txt gives "NAME=VALUE" assignments applied at every launch; the default is every
# dimension-eight coefficient at 1 with Lam at 1000 GeV, which is what the study means by "the
# full model switched on".
#
# The flow is generate, `output`, edit the cards with set_cards.py, then bin/generate_events,
# rather than MadGraph's interactive `launch` prompt.  Two reasons.  A `set` typed at that prompt
# for a name the model does not have is accepted silently and the run then uses the default, so
# a restricted model quietly produced Standard-Model numbers; set_cards.py makes that an error.
# And the LHE files are needed for the distributions, so they are copied to <study dir>/lhe/
# before the process directory is deleted.  Process directories live in $DIM8_RUNS (default
# ~/dim8auto_build/mg5runs, outside Dropbox).  $DIM8_CORES (default 2) caps the cores, since this
# machine is shared.  Results append to <study dir>/results.tsv.
set -u
ST=$(cd "${1:?study dir}" && pwd); MODEL=$(cd "${2:-models/dim8_is}" && pwd); NEV=${3:-5000}
MG=${MG5_DIR:-${MG5_DIR:-/path/to/MG5_aMC}}; PY=$(command -v python3.11 || command -v python3)
RUNS=${DIM8_RUNS:-$HOME/dim8auto_build/mg5runs}; CORES=${DIM8_CORES:-2}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p $RUNS $ST/lhe
OUT=$ST/results.tsv; [ -f $OUT ] || printf "process\tmodel\torder\tsigma_pb\terror_pb\tnevents\tMW_GeV\tsettings\tlhe\n" > $OUT
# "NP=0 on" is the Standard-Model bin run with the coefficients switched ON.  It is not a
# duplicate: fourteen couplings of the model carry a Wilson coefficient with no NP tag (the Higgs
# self-couplings, hVV and the nine h f fbar, through vevT, lam and the Yukawas) and the W mass
# shift carries none either and cannot, since MadGraph counts orders on couplings and a mass is
# not one.  So NP=0 moves when the coefficients move, by +1.35 +- 0.115 pb on p p > w+ w- with all
# 1030 at 1 and Lambda at 1 TeV, and that shift is a genuine O(1/Lambda^4) term that NP^2==2 does
# not contain.  The complete 1/Lambda^4 prediction is
#     sigma_int = sigma(NP^2==2) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]
# and the bracket is what this row measures.  See docs/HOW_TO_BREAK_IT.md.
ORDERS=("NP=0" "NP=0 on" "NP^2==2" "NP<=2 NP^2==4")
SETS="dim8_all=1 Lam=1000"; [ -f $ST/coefficients.txt ] && SETS=$(grep -v "^#" $ST/coefficients.txt | tr '\n' ' ')

run_one () { # $1 process line, $2 model spec (dir or dir-card), $3 order
  local proc=${1%%|*}; local rest=""; [[ "$1" == *"|"* ]] && rest=${1#*|}
  local extra=${rest%%|*}
  # '+' and '-' are spelled out before the sanitising, or "w+ z" and "w- z" (and w+ w- w+ against
  # w+ w- w-) share one tag: the runs were sequential so the cross sections were right, but the
  # second process's event files overwrote the first's.
  local tag=$(echo "${proc}_${2##*/}_$3" | sed 's/+/p/g; s/-/m/g' | tr -c 'A-Za-z0-9_\n' '_'); local d=$RUNS/$tag
  # "NP=0 on" generates the same NP=0 amplitude and runs it with the coefficients on.
  local gen="$3"; local sets="$SETS"
  [ "$3" = "NP=0" ]    && sets="dim8_all=0 Lam=1000"
  [ "$3" = "NP=0 on" ] && gen="NP=0"
  # The squared rows are there for the cross section, not for distributions (only the leading
  # classes' squares are ever plotted), and a tiny, peaked squared term can spend an hour
  # unweighting 5000 events out of tens of thousands of trials; $DIM8_NEV_SQ (default 1000)
  # caps the event count for that order.
  local nev=$NEV; [[ "$3" == *"NP^2==4"* ]] && nev=${DIM8_NEV_SQ:-1000}
  rm -rf $d
  printf 'import model %s\ngenerate %s %s\noutput %s\n' "$2" "$proc" "$gen" "$d" > $RUNS/$tag.mg5
  $PY $MG/bin/mg5_aMC -f $RUNS/$tag.mg5 > $RUNS/$tag.log 2>&1 < /dev/null
  if [ ! -x $d/bin/generate_events ]; then
    # no diagrams is a result (a class with no vertex for the process, e.g. X^4 in q q~ > W W),
    # anything else is a failure worth reading about
    local why=NO_OUTPUT; grep -q "NoDiagramException" $RUNS/$tag.log && why=NO_DIAGRAMS
    printf "%s\t%s\t%s\t%s\t-\t%s\t-\t%s\t-\n" "$proc" "${2##*/}" "$3" "$why" "$NEV" "$sets" >> $OUT
    echo "$(date +%H:%M) $proc | ${2##*/} | $3 -> $why, see $RUNS/$tag.log"; return
  fi
  printf 'run_mode = 2\nnb_core = %s\nautomatic_html_opening = False\n' "$CORES" >> $d/Cards/me5_configuration.txt
  if ! $PY $HERE/set_cards.py $d nevents=$nev ebeam1=6800 ebeam2=6800 hel_recycling=False $sets $extra >> $RUNS/$tag.log 2>&1; then
    printf "%s\t%s\t%s\tBAD_SETTING\t-\t%s\t-\t%s\t-\n" "$proc" "${2##*/}" "$3" "$NEV" "$sets" >> $OUT
    echo "$(date +%H:%M) $proc | ${2##*/} | $3 -> $(tail -1 $RUNS/$tag.log)"; rm -rf $d; return
  fi
  $d/bin/generate_events -f run_01 >> $RUNS/$tag.log 2>&1 < /dev/null
  local xs=$(grep -h "Cross-section :" $RUNS/$tag.log | tail -1 | sed 's/.*Cross-section : *//' | awk '{print $1"\t"$3}')
  # The W mass is derived in the {alpha, MZ, GF} scheme, so switching coefficients on moves it and
  # MadGraph says so.  Record it: with every one of the 1030 coefficients at 1 and Lam at 1 TeV it
  # comes out at 79.33 instead of the scheme's tree-level 79.82, and a row with a visibly shifted MW is not being compared
  # with the Standard Model at the same vacuum.  A class at a time keeps the shift small.
  # bin/generate_events does not print the derived W mass the way the launch prompt does, so it is
  # evaluated from the model's own parameter definitions at this row's settings (the plain model
  # has no MW shift and reports the input value).
  # For a restricted model only the card's coefficients exist, whatever dim8_all= says, so the
  # W mass is evaluated with just those switched on (the names come from the card's nonzero
  # DIM8 entries); the unrestricted model takes the settings as they are.
  local mwsets="$sets"
  if [[ "$2" == *-* ]] && [ -f "$MODEL/restrict_${2##*-}.dat" ]; then
    mwsets=$(awk 'toupper($1)=="BLOCK"{b=toupper($2)} b=="DIM8" && $1 ~ /^[0-9]+$/ && $2+0 != 0 && $4 != "Lam" {printf "%s=1 ", $4}' "$MODEL/restrict_${2##*-}.dat")" Lam=1000"
    [[ "$sets" == *dim8_all=0* ]] && mwsets="dim8_all=0 Lam=1000"
  fi
  local mw=$($PY $HERE/../../validate/eval_ufo_params.py $MODEL $mwsets $extra --show=MW 2>/dev/null | awk '$1=="MW" && $2=="="{printf "%.3f", $3; exit}')
  local lhe="-"
  if [ -f $d/Events/run_01/unweighted_events.lhe.gz ]; then
    cp $d/Events/run_01/unweighted_events.lhe.gz $ST/lhe/$tag.lhe.gz; lhe=lhe/$tag.lhe.gz
  fi
  [ -z "$xs" ] && xs=$'FAILED\t-'
  printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\n" "$proc" "${2##*/}" "$3" "$xs" "$nev" "${mw:--}" "$sets" "$lhe" >> $OUT
  echo "$(date +%H:%M) $proc | ${2##*/} | $3 -> $xs   MW ${mw:--}"
  # a failed run keeps its process directory (renamed) so that the compiler's message can be read
  if [[ "$xs" == FAILED* ]]; then rm -rf $d.failed; mv $d $d.failed; echo "   kept $d.failed"; else rm -rf $d; fi
}

# Both lists are read into arrays first: MadGraph reads standard input after its script file and
# would otherwise swallow the rest of processes.txt, so only the first line ever ran.
PROCS=(); while IFS= read -r line; do line=${line%%$'\r'}; case ${line// /} in ""|\#*) continue;; esac; PROCS+=("$line"); done < $ST/processes.txt
CLASSES=(); [ -f $ST/classes.txt ] && while IFS= read -r c; do c=${c%%#*}; c=$(echo $c); [ -z "$c" ] && continue; CLASSES+=("$c"); done < $ST/classes.txt
for line in "${PROCS[@]}"; do
  full=$MODEL; card=""; [[ "$line" == *"|"*"|"* ]] && card=${line##*|} && card=${card// /}; [ -n "$card" ] && full=$MODEL-$card
  # DIM8_SKIP_FULL=1 skips the three full-model rows everywhere (rerunning class rows that
  # failed); a card field of "-" skips them for that process alone (its full rows already exist
  # from an earlier pass, or the unrestricted process is too heavy to be worth it)
  if [ "${DIM8_SKIP_FULL:-0}" != 1 ] && [ "$card" != "-" ]; then for o in "${ORDERS[@]}"; do run_one "$line" "$full" "$o"; done; fi
  for c in "${CLASSES[@]}"; do
    for o in "NP^2==2" "NP<=2 NP^2==4"; do run_one "$line" "$MODEL-$c" "$o"; done
  done
done
echo "results in $OUT, event files in $ST/lhe/"
