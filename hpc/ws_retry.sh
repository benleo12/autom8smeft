#!/bin/bash
# wolframscript, started again when its kernel never starts.  Of the thousands of kernels a build starts side
# by side on a node, now and then one fails to link to its wolframscript (LinkConnect::linkc in the output):
# the wolframscript is then left with no kernel under it and waits for one without end, and so does the step
# that waits on it, until its job runs out of time.  Set as WS (./dim8, hpc/write_shards.sh, hpc/run_parts.sh,
# hpc/build_geo.sh, hpc/twopoint_geo.sh), this script runs the wolframscript WS_REAL (by default the one on
# the PATH) with the same arguments, input and output, and when no kernel has appeared under it after
# WS_START seconds (default 300), kills it and starts it again, three times at most.  A wolframscript whose
# kernel has gone (a kernel that died) and that stays on for as long is killed too, and the run reported as
# failed, since starting it again would most likely end the same way.
set -u
real=${WS_REAL:-$(command -v wolframscript)}
limit=${WS_START:-300}
exec 3<&0
kernel() {   # a child of process $1 that is not a zombie
  local c
  for c in $(pgrep -P "$1"); do
    case $(ps -o stat= -p "$c" 2>/dev/null) in Z*|"") ;; *) return 0;; esac
  done
  return 1
}
for try in 1 2 3; do
  "$real" "$@" <&3 &
  pid=$!
  seen=0; idle=0
  while kill -0 "$pid" 2>/dev/null; do
    if kernel "$pid"; then seen=1; idle=0; else idle=$((idle + 5)); fi
    [ "$idle" -ge "$limit" ] && { kill -9 "$pid" 2>/dev/null; break; }
    sleep 5
  done
  wait "$pid" 2>/dev/null; rc=$?
  [ "$idle" -ge "$limit" ] || exit $rc
  if [ "$seen" = 1 ]; then
    echo "$(date +%H:%M:%S) ws_retry: the kernel under wolframscript went and it stayed on for $limit s, killed" >&2
    exit 1
  fi
  echo "$(date +%H:%M:%S) ws_retry: no kernel under wolframscript after $limit s, killed (try $try of 3)" >&2
  sleep $((RANDOM % 20))
done
exit 1
