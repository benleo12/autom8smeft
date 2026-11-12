#!/bin/bash
# Driver for the paper's studies: cross sections at 13.6 TeV for a list of processes, at each
# order of the Lambda expansion, for the full model and for one operator class at a time.
#   usage: examples/studies/run_study.sh <study dir> [model dir] [nevents]
# The model is models/dim8_mw, the {MW, MZ, GF} scheme, unless [model dir] names another.
# <study dir> holds processes.txt (one MadGraph process per line, run-card settings after a '|'
# as "ptj=20 mmjj=500", and after a second '|' optionally the restriction card to use for the
# "full model" rows of that process: p p > h h j j QCD=0 NP^2==2 on the unrestricted dim8_mw has 525156
# diagrams, 3539 core-minutes of generation, so the VBF study runs
# its full rows on the bosonic card) and classes.txt (one restriction-card name per line,
# for cards that ship with the model or that validate/make_restriction.py writes into the model
# directory).  Optionally coefficients.txt gives "NAME=VALUE" assignments applied at every launch.
# The default is every dimension-eight coefficient at 1 with Lam at 3000 GeV, the scale at which the
# paper quotes every entry, which is what the study means by "the full model switched on".  The
# tables read each row's own Lam from its settings column.
#
# The flow is generate, `output`, edit the cards with set_cards.py, then bin/generate_events,
# rather than MadGraph's interactive `launch` prompt.  Two reasons.  A `set` typed at that prompt
# for a name the model does not have is accepted silently and the run then uses the default, so
# a restricted model would give Standard-Model numbers.  set_cards.py makes that an error.  And
# the LHE files are needed for the distributions, so they are copied to <study dir>/lhe/ before
# the process directory is deleted.  Process directories live in $DIM8_RUNS (default
# ~/dim8auto_build/mg5runs).  $DIM8_CORES (default 2) caps the number of cores.  Results append
# to <study dir>/results.tsv, and the record of each row to <study dir>/records.tsv beside it: the
# model as MadGraph read it (a hash of the UFO's files, the release archive's sha256 when it is a
# released model, the restriction card's hash), the MadGraph version, the param and run cards as the
# run used them (a hash of each, the copy in <study dir>/cards/), the cross section and the event
# file with its sha256.  The table and figure scripts check every row against its record before
# they write anything (examples/studies/provenance.py).
set -u
ST=$(cd "${1:?study dir}" && pwd); MODEL=$(cd "${2:-models/dim8_mw}" && pwd); NEV=${3:-5000}
MG=${MG5_DIR:-${MG5_DIR:-/path/to/MG5_aMC}}; PY=$(command -v python3.11 || command -v python3)
RUNS=${DIM8_RUNS:-$HOME/dim8auto_build/mg5runs}; CORES=${DIM8_CORES:-2}
HERE=$(cd "$(dirname "$0")" && pwd)
mkdir -p $RUNS $ST/lhe
# $DIM8_RESULTS names the results file, results.tsv by default.  results_<x> writes results_<x>.tsv with
# its records in records_<x>.tsv, and adds _<x> to the name of every run and event file, so that one
# study can hold rows that share a process, model and order (examples/studies/zwidth, a file a Lambda).
RES=${DIM8_RESULTS:-results}
case "$RES" in results|results_*) ;; *) echo "run_study.sh: \$DIM8_RESULTS is results or results_<name>, not $RES"; exit 2;; esac
OUT=$ST/$RES.tsv
# "NP=0 on" is the Standard-Model bin run with the coefficients switched ON.  Every shift of a
# Lagrangian parameter by the input scheme enters the Lagrangian as a tagged series, so this row
# differs from "NP=0" through ONE thing only: the W mass.  The {alpha, MZ, GF} scheme derives it,
# it moves with the coefficients, and it sits in a propagator and not in a coupling, so MadGraph
# cannot tag it.  The complete 1/Lambda^4 prediction is
#     sigma_int = sigma(NP^2==2) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]
# and the bracket is what this row measures.  It is zero in a process in which no W is produced
# or exchanged (VBF di-Higgs exchanges two, and its NP=0 bin moves by 6.7 +- 0.9 per cent with every
# entry of DIM8 and DIM8F at 1 and Lam at 1 TeV, ptj = 25 GeV, etaj = 5, mmjj = 400 GeV).  See docs/HOW_TO_BREAK_IT.md.
ORDERS=("NP=0" "NP=0 on" "NP^2==2" "NP<=2 NP^2==4")
# The bracket exists only where M_W is derived.  In a model that takes M_W as an input (dim8_mw)
# no mass depends on a coefficient, so the "NP=0 on" row would repeat the NP=0 row to every digit
# (it did, in all twelve processes of the 2026-10-29 studies), and it is not run.
if grep -A1 "^MW = Parameter(name = 'MW'," "$MODEL/parameters.py" | grep -q "nature = 'external'"; then
  ORDERS=("NP=0" "NP^2==2" "NP<=2 NP^2==4")
fi
# $DIM8_ORDERS, a ';'-separated subset such as "NP=0;NP=0 on", reruns only those orders of the
# full-model rows (the class rows are interference and square and are not affected by it)
if [ -n "${DIM8_ORDERS:-}" ]; then IFS=';' read -r -a ORDERS <<< "$DIM8_ORDERS"; fi
# $DIM8_CLASS_ORDERS does the same for the class rows ("NP<=2 NP^2==4" reruns only their squares)
CLASS_ORDERS=("NP^2==2" "NP<=2 NP^2==4")
if [ -n "${DIM8_CLASS_ORDERS:-}" ]; then IFS=';' read -r -a CLASS_ORDERS <<< "$DIM8_CLASS_ORDERS"; fi
SETS="dim8_all=1"; [ -f $ST/coefficients.txt ] && SETS=$(grep -v "^#" $ST/coefficients.txt | tr '\n' ' ')
# The scale is the Lam= of coefficients.txt, else $DIM8_LAM, else 3 TeV, and it is always written into the
# settings of the row, where the tables read it.  $DIM8_LAM with $DIM8_RESULTS scans the scale of one study.
if [[ " $SETS " == *" Lam="* ]]; then
  [ -n "${DIM8_LAM:-}" ] && { echo "run_study.sh: \$DIM8_LAM is set and $ST/coefficients.txt names its own Lam="; exit 2; }
else
  SETS="${SETS% } Lam=${DIM8_LAM:-3000}"
fi
# the scale of this study's rows, for the W-mass evaluation of a restricted model below
LAMSET=$(echo " $SETS " | grep -o ' Lam=[^ ]*' | tail -1); LAMSET=${LAMSET:- Lam=3000}
[ -f $OUT ] || printf "process\tmodel\torder\tsigma_pb\terror_pb\tnevents\tMW_GeV\tsettings\tlhe\n" > $OUT

# A row goes to results.tsv and its record to records.tsv beside it.  The record is written while
# the process directory still exists, since the cards are read from it, and with the model hash
# taken before MadGraph read the model, so that a model replaced during the run cannot pass for the
# one the run used.  Uses run_one's $d, $tag, $card and $mid.
# provenance.py appends the row and the record under the lock that merge_rows.py and provenance.py
# attest hold while they rewrite the two files; a row it could not append is appended here.
put_row () { # $1 the row, $2 the run name ("-" for a run that never reached generate_events)
  $PY $HERE/provenance.py record --row "$OUT" "$1" "$MODEL" "$card" "$d" "$2" "$MG" $mid >> $RUNS/$tag.log 2>&1 \
    || { grep -qxF -- "$1" $OUT || printf "%s\n" "$1" >> $OUT; echo "   no record written for this row, see $RUNS/$tag.log"; }
}

# The W mass is derived in the {alpha, MZ, GF} scheme, so switching coefficients on moves it and
# MadGraph says so.  Record it: with every entry of DIM8 and DIM8F at 1 and Lam at 1 TeV it
# comes out at 79.36 instead of the scheme's tree-level 79.82, and a row with a visibly shifted MW is not being compared
# with the Standard Model at the same vacuum.  A class at a time keeps the shift small.
# bin/generate_events does not print the derived W mass the way the launch prompt does, so it is
# evaluated from the model's own parameter definitions at this row's settings (the plain model
# has no MW shift and reports the input value).
# For a restricted model only the card's coefficients exist, whatever dim8_all= says, so the
# W mass is evaluated with just those switched on (the names come from the card's nonzero
# DIM8 and DIM8F entries, since the further flavour structures of c8l4H2x1 enter muon decay);
# the unrestricted model takes the settings as they are.  Uses run_one's $sets and $extra.
w_mass () { # $1 model spec
  local mwsets="$sets"
  if [[ "$1" == *-* ]] && [ -f "$MODEL/restrict_${1##*-}.dat" ]; then
    mwsets=$(awk 'toupper($1)=="BLOCK"{b=toupper($2)} (b=="DIM8" || b=="DIM8F") && $1 ~ /^[0-9]+$/ && $2+0 != 0 && $4 != "Lam" {printf "%s=1 ", $4}' "$MODEL/restrict_${1##*-}.dat")"$LAMSET"
    [[ "$sets" == *dim8_all=0* ]] && mwsets="dim8_all=0$LAMSET"
  fi
  # only NAME=number settings can be model parameters.  A run-card cut such as pt_min_pdg={25:100}
  # is not one, and passing it would make the evaluation fail and the column read "-".
  local mwextra=""; for tok in $extra; do [[ "$tok" =~ ^[A-Za-z_0-9]+=[-+0-9.eE]+$ ]] && mwextra="$mwextra $tok"; done
  $PY $HERE/../../validate/eval_ufo_params.py $MODEL $mwsets $mwextra --show=MW 2>/dev/null | awk '$1=="MW" && $2=="="{printf "%.3f", $3; exit}'
}

# A decay (one particle in, such as z > e+ e-) is not integrated.  MadGraph writes its standalone matrix
# element, decay_width.f takes the place of check_sa.f and evaluates it along three directions, and the
# partial width is |M|^2 |p| / (8 pi M^2), exact at tree level (decay_width.f says why bin/generate_events
# is not used).  The row's sigma_pb and error_pb columns hold the width in GeV and 0, its nevents is "-", and
# its lhe column names the printout of decay_width.f, lhe/<tag>.width.txt, from which provenance.py computes
# the width again.  A decay to a multiparticle label has a matrix element for each channel and is refused:
# give the channels one at a time.  Uses run_one's $d, $tag, $sets and $extra.
width_row () { # $1 process, $2 model spec, $3 order
  local P=($d/SubProcesses/P*/)
  if [ ${#P[@]} != 1 ] || [ ! -f ${P[0]}check_sa.f ]; then
    put_row "$(printf "%s\t%s\t%s\tFAILED\t-\t-\t-\t%s\t-" "$1" "${2##*/}" "$3" "$sets")" -
    echo "$(date +%H:%M) $1 | ${2##*/} | $3 -> FAILED, ${#P[@]} matrix elements in $d/SubProcesses, give one decay channel at a time"
    rm -rf $d.failed; mv $d $d.failed; return
  fi
  if ! $PY $HERE/set_cards.py $d $sets $extra >> $RUNS/$tag.log 2>&1; then
    put_row "$(printf "%s\t%s\t%s\tBAD_SETTING\t-\t-\t-\t%s\t-" "$1" "${2##*/}" "$3" "$sets")" -
    echo "$(date +%H:%M) $1 | ${2##*/} | $3 -> $(grep "^set_cards:" $RUNS/$tag.log | tail -1)"; rm -rf $d; return
  fi
  # check_sa.f of a standalone output is a link to the file the subprocesses share, so the link goes first
  rm -f ${P[0]}check_sa.f; cp $HERE/decay_width.f ${P[0]}check_sa.f
  local out=$ST/lhe/$tag.width.txt xs="" lhe="-"
  rm -f $out
  if (cd ${P[0]} && make check >> $RUNS/$tag.log 2>&1 && ./check > $out 2>> $RUNS/$tag.log); then
    xs=$(awk '$1=="width" && $2=="(GeV)" && $3=="=" && $4 ~ /^-?[0-9]\.[0-9]+E[-+][0-9]+$/ {printf "%.10g\t0", $4}' $out)
  fi
  [ -n "$xs" ] && lhe=lhe/$tag.width.txt || { xs=$'FAILED\t-'; [ -f $out ] && cat $out >> $RUNS/$tag.log; rm -f $out; }
  local mw=$(w_mass "$2")
  put_row "$(printf "%s\t%s\t%s\t%s\t-\t%s\t%s\t%s" "$1" "${2##*/}" "$3" "$xs" "${mw:--}" "$sets" "$lhe")" -
  echo "$(date +%H:%M) $1 | ${2##*/} | $3 -> $xs   MW ${mw:--}"
  if [[ "$xs" == FAILED* ]]; then rm -rf $d.failed; mv $d $d.failed; echo "   kept $d.failed"; else rm -rf $d; fi
}

run_one () { # $1 process line, $2 model spec (dir or dir-card), $3 order
  local proc=${1%%|*}; local rest=""; [[ "$1" == *"|"* ]] && rest=${1#*|}
  local extra=${rest%%|*}
  # '+' and '-' are spelled out before the sanitising, since otherwise "w+ z" and "w- z" (and
  # w+ w- w+ and w+ w- w-) share one tag and the second process's event files overwrite the first's.
  local tag=$(echo "${proc}_${2##*/}_$3${RES#results}" | sed 's/+/p/g; s/-/m/g' | tr -c 'A-Za-z0-9_\n' '_'); local d=$RUNS/$tag
  # "NP=0 on" generates the same NP=0 amplitude and runs it with the coefficients on.
  local gen="$3"; local sets="$SETS"
  [ "$3" = "NP=0" ]    && sets="dim8_all=0$LAMSET"
  [ "$3" = "NP=0 on" ] && gen="NP=0"
  # The squared rows are there for the cross section, not for distributions (only the leading
  # classes' squares are ever plotted), and a tiny, peaked squared term can spend an hour
  # unweighting 5000 events out of tens of thousands of trials; $DIM8_NEV_SQ (default 1000)
  # caps the event count for that order.
  local nev=$NEV; [[ "$3" == *"NP^2==4"* ]] && nev=${DIM8_NEV_SQ:-1000}
  local card=""; [ "$2" != "$MODEL" ] && card=${2#$MODEL-}
  local mid; mid=$($PY $HERE/provenance.py model "$MODEL" "$card")
  rm -rf $d
  local decay=0 fmt=""; [ $(echo ${proc%%>*} | wc -w) = 1 ] && decay=1 && fmt="standalone "
  printf 'import model %s\ngenerate %s %s\noutput %s%s\n' "$2" "$proc" "$gen" "$fmt" "$d" > $RUNS/$tag.mg5
  $PY $MG/bin/mg5_aMC -f $RUNS/$tag.mg5 > $RUNS/$tag.log 2>&1 < /dev/null
  if [ $decay = 1 ] && [ -d $d/SubProcesses ]; then width_row "$proc" "$2" "$3"; return; fi
  if [ ! -x $d/bin/generate_events ]; then
    # no diagrams is a result (a class with no vertex for the process, e.g. X^4 in q q~ > W W),
    # anything else is a failure worth reading about
    local why=NO_OUTPUT; grep -q "NoDiagramException" $RUNS/$tag.log && why=NO_DIAGRAMS
    local n=$NEV; [ $decay = 1 ] && n=-
    put_row "$(printf "%s\t%s\t%s\t%s\t-\t%s\t-\t%s\t-" "$proc" "${2##*/}" "$3" "$why" "$n" "$sets")" -
    echo "$(date +%H:%M) $proc | ${2##*/} | $3 -> $why, see $RUNS/$tag.log"; return
  fi
  printf 'run_mode = 2\nnb_core = %s\nautomatic_html_opening = False\n' "$CORES" >> $d/Cards/me5_configuration.txt
  # MadGraph sets the scale to H_T/2 (dynamical_scale_choice=3) by itself for any process with the
  # ^2 order syntax and leaves its default for NP=0, so every order is run at H_T/2 here and the
  # interference and the Standard-Model rate it is divided by share one scale.
  # A refused request is a row of its own, with the event count asked for at its order ($nev, which the
  # squared rows cap), and set_cards.py leaves both cards as they were, so its record holds the cards
  # MadGraph wrote.
  if ! $PY $HERE/set_cards.py $d nevents=$nev ebeam1=6800 ebeam2=6800 hel_recycling=False dynamical_scale_choice=3 $sets $extra >> $RUNS/$tag.log 2>&1; then
    put_row "$(printf "%s\t%s\t%s\tBAD_SETTING\t-\t%s\t-\t%s\t-" "$proc" "${2##*/}" "$3" "$nev" "$sets")" -
    echo "$(date +%H:%M) $proc | ${2##*/} | $3 -> $(grep "^set_cards:" $RUNS/$tag.log | tail -1)"; rm -rf $d; return
  fi
  $d/bin/generate_events -f run_01 >> $RUNS/$tag.log 2>&1 < /dev/null
  # MadGraph's integration channels are the diagrams with three-point vertices, weighted by default by
  # their squared amplitudes.  With the light fermions massless they can all vanish while a contact
  # diagram does not (in g g > e+ e- at NP^2==4 the only such channel is a Higgs that couples to the
  # electron), and the run stops with "All amp2 are zero but not the total matrix-element".  Such a
  # run is done again with each channel weighted by its propagators alone (sde_strategy=2, as in
  # validate/cp_rates.py), which changes how the phase space is sampled and not the cross section.
  local rn=run_01
  if ! grep -q "Cross-section :" $RUNS/$tag.log && grep -qs "All amp2 are zero" $RUNS/$tag.log $d/run_01_tag_1_debug.log; then
    rn=run_02; echo "   all amp2 zero in run_01, run again with sde_strategy=2" >> $RUNS/$tag.log
    $PY $HERE/set_cards.py $d sde_strategy=2 >> $RUNS/$tag.log 2>&1 && $d/bin/generate_events -f $rn >> $RUNS/$tag.log 2>&1 < /dev/null
  fi
  local xs=$(grep -h "Cross-section :" $RUNS/$tag.log | tail -1 | sed 's/.*Cross-section : *//' | awk '{print $1"\t"$3}')
  local mw=$(w_mass "$2")
  local lhe="-"
  if [ -f $d/Events/$rn/unweighted_events.lhe.gz ]; then
    cp $d/Events/$rn/unweighted_events.lhe.gz $ST/lhe/$tag.lhe.gz; lhe=lhe/$tag.lhe.gz
  fi
  # An amplitude that integrates to exactly zero is a physics answer, not a failure: class 11
  # (psi^2H^2D^3) does that in p p > e+ e-, where MadGraph generates the diagrams and the survey
  # returns nothing.  It is recorded as ZERO, since FAILED would make a real result look like
  # breakage and hide it among rows that really did break.
  if [ -z "$xs" ] && grep -q "Survey return zero cross section" $RUNS/$tag.log 2>/dev/null; then
    xs=$'ZERO\t-'
  fi
  [ -z "$xs" ] && xs=$'FAILED\t-'
  put_row "$(printf "%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s" "$proc" "${2##*/}" "$3" "$xs" "$nev" "${mw:--}" "$sets" "$lhe")" $rn
  echo "$(date +%H:%M) $proc | ${2##*/} | $3 -> $xs   MW ${mw:--}"
  # a failed run keeps its process directory (renamed) so that the compiler's message can be read
  if [[ "$xs" == FAILED* ]]; then rm -rf $d.failed; mv $d $d.failed; echo "   kept $d.failed"; else rm -rf $d; fi
}

# Both lists are read into arrays first.  MadGraph reads standard input after its script file and
# would otherwise swallow the rest of processes.txt, so that only the first line would run.
PROCS=(); while IFS= read -r line; do line=${line%%$'\r'}; case ${line// /} in ""|\#*) continue;; esac; PROCS+=("$line"); done < $ST/processes.txt
CLASSES=(); [ -f $ST/classes.txt ] && while IFS= read -r c; do c=${c%%#*}; c=$(echo $c); [ -z "$c" ] && continue; CLASSES+=("$c"); done < $ST/classes.txt
for line in "${PROCS[@]}"; do
  full=$MODEL; card=""; [[ "$line" == *"|"*"|"* ]] && card=${line##*|} && card=${card// /}; [ -n "$card" ] && full=$MODEL-$card
  # DIM8_SKIP_FULL=1 skips the three full-model rows everywhere (rerunning class rows that
  # failed); a card field of "-" skips them for that process alone (its full rows are already in
  # results.tsv, or the unrestricted process is too heavy to be worth it)
  if [ "${DIM8_SKIP_FULL:-0}" != 1 ] && [ "$card" != "-" ]; then for o in "${ORDERS[@]}"; do run_one "$line" "$full" "$o"; done; fi
  # the +"${CLASSES[@]}" form is for bash 3.2, where an empty array is "unbound" under set -u
  # and a study with no class rows would stop after its full rows
  for c in ${CLASSES[@]+"${CLASSES[@]}"}; do
    for o in "${CLASS_ORDERS[@]}"; do run_one "$line" "$MODEL-$c" "$o"; done
  done
done
echo "results in $OUT, their records in $ST/records${RES#results}.tsv, event files in $ST/lhe/, cards in $ST/cards/"
