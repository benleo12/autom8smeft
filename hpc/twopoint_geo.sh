#!/bin/bash
# The two-point checks of the models of order N with their quadratic terms computed in K kernels at once:
#
#   hpc/twopoint_geo.sh bil|ferm N K [PREFIX]
#
# K runs of validate/check_bilinears_geo.wls (bil) or validate/check_fermion_masses_geo.wls (ferm) with
# DIM8_TWOPOINT_PREP=1 share the units of the quadratic terms (validate/twopoint_units.m: the blocks one by
# one and LSM summand by summand) and quit, then one run reads them all and does the check.  PREFIX is the
# negative control of the check, and it reuses the units the run without it has left.  The environment is the
# check's (DIM8_ROOT, and WS for the wolframscript to call).  The units go to DIM8_TWOPOINT_DIR (default
# $DIM8_ROOT/build/twopoint), the logs to $DIM8_ROOT/logs/twopoint, and the report, line by line as it is
# written, to logs/twopoint/<kind>_<N>[_PREFIX].progress.  The locks left by killed runs of the same order are
# cleared first, so two of these on one order at once only compute some units twice.
set -u
root=${DIM8_ROOT:?set DIM8_ROOT}; kind=$1; n=$2; k=$3; drop=${4:-}
case $kind in
  bil) f=check_bilinears_geo.wls ;;
  ferm) f=check_fermion_masses_geo.wls ;;
  *) echo "usage: hpc/twopoint_geo.sh bil|ferm N K [PREFIX]"; exit 2 ;;
esac
dir=${DIM8_TWOPOINT_DIR:-$root/build/twopoint}; log=$root/logs/twopoint
mkdir -p "$dir" "$log"
name=${kind}_${n}${drop:+_$drop}
rm -rf "$dir/${kind}${n}_"*.lock
export DIM8_TWOPOINT_DIR=$dir root f n drop log name
t0=$(date +%s)
seq 1 "$k" | xargs -P "$k" -I{} bash -c 'DIM8_TWOPOINT_PREP=1 DIM8_PROGRESS=$log/${name}_prep{}.progress \
  "${WS:-wolframscript}" -file "$root/validate/$f" "$n" $drop > "$log/${name}_prep{}.log" 2>&1'
p=$?
echo "$name: units in $(( $(date +%s) - t0 )) s with $k kernels"
[ $p = 0 ] || { echo "$name: a run of the units stopped (xargs exit $p), see $log/${name}_prep*.log"; exit 1; }
rm -f "$log/$name.progress"
DIM8_PROGRESS=$log/$name.progress "${WS:-wolframscript}" -file "$root/validate/$f" "$n" $drop > "$log/$name.log" 2>&1
r=$?
v=$(grep -h "PASS\|fall slower\|ABORT" "$log/$name.progress" 2>/dev/null | tail -1)
# exit 0 with no PASS line is a run that did not reach the check, not a pass
if [ $r = 0 ] && ! printf '%s\n' "$v" | grep -q "PASS"; then r=1; v="no verdict in $log/$name.progress"; fi
echo "$name: exit $r in $(( $(date +%s) - t0 )) s: $v"
exit $r
