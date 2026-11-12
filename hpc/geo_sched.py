#!/usr/bin/env python3
"""The geo blocks of a model of order N spread over slurm jobs, each block once: hpc/build_geo.sh blocks with GEO_SCHED.

    python3 hpc/geo_sched.py plan N     the table of the blocks still to build, nothing started
    python3 hpc/geo_sched.py run N      starts them, log in $GEO_LOG/sched.log
    python3 hpc/geo_sched.py alive LOCK whether the holder a block's lock names still runs it: exit 0 when it
                                        does, 1 when it does not, 2 when that cannot be told (hpc/build_geo.sh)

hpc/build_geo.sh sets the environment: GEO_LISTS (the lists of its sources step, blocks3 and blocksall), GEO_VDIR (the
cache of the geo blocks) and GEO_LOG, with DIM8_ROOT and the worker's DIM8_BASE.  GEO_SCHED names a file of
"<job> <cores>" lines, the slurm jobs (holders) whose cores the blocks run on, read again every cycle, so that a
holder that starts later joins.  Each block runs as a slurm step on a holder (srun --jobid=<job> --overlap) through
hpc/build_geo.sh block, which takes the block's lock first, so that two schedulers never run one block: the blocks
with every leg on one kernel each, the light ones on one kernel with the leg cap, and the heavy ones split over
kernels by hpc/run_parts.sh (fr_worker.wls DIM8_PART), M expansions and P parts chosen so that each part takes about
an hour.  The time of a block is the one its status line records in GEO_TIMES, the cache of an earlier build of
the same order: its FeynmanRules time as it was, its expansion capped at 900 s, since the leg cut of
validate/truncexp.m brought those expansions from hours to minutes.  Without GEO_TIMES every block counts an hour.

A block is done when the cache holds it with the stamp of its current source (validate/cache_source.py, as the
worker reads it), so a block whose source has changed since it was built is built again.  A block starts on a
running holder with the cores it needs free, heaviest first, preferably one that runs for twice its estimate more.
When no such holder has room it starts on one that may end first (run_parts.sh takes a split block up from its
files), and never on a holder with less than ten minutes left or one that is not running.  A block wider than every
running holder is cut to the widest.  A block that fails is started once more, and a block whose holder stopped
running under it (preempted, requeued, at its time limit) is started again without that counting as its retry.

A holder is running (RUNNING), waiting in the queue (PENDING, for as long as it waits), or in between: starting,
ending, requeued, suspended or preempted (CONFIGURING, COMPLETING, REQUEUED, SUSPENDED, PREEMPTED, ...), out of the
queue, or not to be read because squeue failed.  A holder in between counts as coming back for GEO_SCHED_GRACE
seconds (900) after it was last running or waiting.  The scheduler waits while a block runs here or under the lock
of a step that is still in the queue, and while a holder waits or may come back.  It gives up, with exit 1 and the
blocks left in the log, when no holder is running, waiting or coming back, or when nothing has run or could start
for GEO_SCHED_IDLE seconds (3600).  A lock names the slurm step and the host:pid that hold it (hpc/build_geo.sh
block): a block whose step has left the queue, or whose process on this host has gone, is started again, and one
whose lock cannot be told (an older lock that names only its job) is left and named when the scheduler gives up, as
is one whose step finds its lock held three times though it reads as free here (the process of another host).
A line of the log that cannot be written (a full disk or quota) is kept and written with the next one, so the
scheduler and its blocks go on.
"""
import math
import os
import re
import shutil
import socket
import subprocess
import sys
import time

TARGET, MCAP, ECAP, MARGIN = 3600.0, 48, 900.0, 600.0
ROOT = os.environ.get("DIM8_ROOT") or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else 0
L, VD = os.environ.get("GEO_LISTS", ""), os.environ.get("GEO_VDIR", "")
LOG = os.path.join(os.environ.get("GEO_LOG", "."), "sched.log")
HOLDERS, TIMES = os.environ.get("GEO_SCHED", ""), os.environ.get("GEO_TIMES", "")
IDLE = float(os.environ.get("GEO_SCHED_IDLE", "3600"))
GRACE = float(os.environ.get("GEO_SCHED_GRACE", "900"))
# the states of a holder between running and gone, from which it may come back
BETWEEN = {"CONFIGURING", "COMPLETING", "REQUEUED", "REQUEUE_HOLD", "REQUEUE_FED", "RESIZING", "SIGNALING",
           "STAGE_OUT", "SUSPENDED", "PREEMPTED", "STOPPED", "UNKNOWN", ""}
SRUN, SQUEUE = shutil.which("srun") or "srun", shutil.which("squeue") or "squeue"
sys.path.insert(0, os.path.join(ROOT, "validate"))
import cache_source as C  # noqa: E402

_pending = []      # log lines not yet written
_current = {}      # block -> the stamp of its current source, computed once
_holders = {}      # the last holders file that could be read


def log(msg):
    """Append a line to the log.  A line that cannot be written is kept and written with the next that can."""
    _pending.append(time.strftime("%H:%M:%S ") + msg + "\n")
    del _pending[:-10000]
    try:
        with open(LOG, "a") as f:
            f.write("".join(_pending))
        del _pending[:]
    except OSError as e:
        print(f"geo_sched: cannot write {LOG} ({e}), {len(_pending)} lines kept: {msg}", file=sys.stderr, flush=True)


def listed(name):
    return [b.strip() for b in open(os.path.join(L, name)) if b.strip()]


def times(path):
    m = re.search(r"tEval ([0-9.]+) \| tVert ([0-9.]+)", open(path, errors="replace").read())
    return (float(m.group(1)), float(m.group(2))) if m else (3600.0, 3600.0)


def done(b):
    """Does the cache hold block b, built from its current source?"""
    st = os.path.join(VD, b + ".status")
    if not os.path.exists(st) or not any(os.path.exists(os.path.join(VD, b + e)) for e in (".mx", ".wxf")):
        return False
    if b not in _current:
        try:
            _current[b] = C.source_hash(b)
        except (KeyError, OSError) as e:
            log(f"{b}: no stamp of its source ({e}), so it counts as not built")
            _current[b] = None
    return _current[b] is not None and C._stamp_in(st) == _current[b]


def holders():
    global _holders
    try:
        out = {}
        for line in open(HOLDERS):
            f = line.split()
            if len(f) == 2 and not line.startswith("#"):
                out[f[0]] = int(f[1])
        _holders = out
    except (OSError, ValueError) as e:
        log(f"the holders file {HOLDERS} cannot be read ({e}), the last one read is used")
    return dict(_holders)


def squeue(*args):
    """The lines squeue prints, [] for a job slurm no longer knows, None when squeue cannot be run or fails."""
    try:
        r = subprocess.run([SQUEUE, "-h", *args], capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        return [] if "Invalid job id" in r.stderr else None
    return [x.strip() for x in r.stdout.splitlines() if x.strip()]


def lock_state(line):
    """"held", "free" or "unknown": whether the holder a lock names still runs the block.  A lock of hpc/build_geo.sh
    block is "<job>.<step> <host>:<pid>" ("<job> <host>:<pid>" from a job's own script, "- <host>:<pid>" outside
    slurm), an older one "<job>" or "<host>:<pid>".  A process of this host that has gone frees the lock, and so does a
    step or a job that has left the queue.  A step in the queue holds it, and so does a live process of this host.  A
    job still in the queue, with no step or no process of this host to tell, cannot be told: its step may have been
    killed without removing the lock, and the job stay in the queue for hours."""
    f = line.split()
    slurm = next((x for x in f if ":" not in x and x != "-"), "")
    hp = next((x for x in f if ":" in x), "")
    host, _, pid = hp.rpartition(":")
    here = bool(hp) and host == socket.gethostname() and pid.isdigit()
    if here:
        try:
            os.kill(int(pid), 0)
        except ProcessLookupError:
            return "free"
        except PermissionError:
            pass
    if "." in slurm:
        steps = squeue("-s", "-j", slurm.split(".")[0], "-o", "%i")
        return "unknown" if steps is None else ("held" if slurm in steps else "free")
    if slurm:
        jobs = squeue("-j", slurm, "-o", "%i")
        return "free" if jobs == [] else ("held" if here else "unknown")
    if hp:
        return "held" if here else "unknown"
    return "free"


def locked(b):
    """The state of the lock of block b (lock_state), "free" without one."""
    try:
        line = open(os.path.join(VD, b + ".lock", "job")).read().strip()
    except OSError:
        return "free"
    return lock_state(line)


def shape(j, m, n):
    """Block job j with m expansions and n parts: its cores and its estimated wall time."""
    j.update(m=m, n=n, cores=max(m, n), wall=j["e"] / m + j["v"] / n + (0 if m == n == 1 else 900))
    return j


def plan():
    jobs = []
    for b in listed("blocks3"):
        if done(b):
            continue
        old = os.path.join(TIMES, b + ".status") if TIMES else ""
        e0, v = times(old) if old and os.path.exists(old) else (3600.0, 3600.0)
        e = min(e0, ECAP)
        # the blocks of the operator 5 spend their time in FeynmanRules on few terms: smaller chunks, more parts
        chunk = "10" if b.split("op")[-1] == "5" and not b.startswith("G6cl") else ""
        j = dict(b=b, e=e, v=v, chunk=chunk, cpu=e + v)
        jobs.append(shape(j, max(1, min(MCAP, math.ceil(e / TARGET))), max(1, min(MCAP, math.ceil(v / TARGET)))))
    jobs.sort(key=lambda j: -j["wall"])
    return jobs


def queue_state(j):
    """(state, end time) of slurm job j: ("RUNNING", its end), (its other state, 0), ("", 0) once it has left the
    queue, ("UNKNOWN", 0) when squeue fails."""
    out = squeue("-j", j, "-o", "%T %e")
    if out is None:
        return "UNKNOWN", 0
    t = " ".join(out).split()
    if len(t) >= 2 and t[0] == "RUNNING":
        try:
            return "RUNNING", time.mktime(time.strptime(t[1], "%Y-%m-%dT%H:%M:%S"))
        except ValueError:
            return "RUNNING", time.time() + 3.15e8      # no end time (UNLIMITED): it runs on
    return (t[0] if t else ""), 0


def srun(h, cores, args, out):
    cmd = [SRUN, f"--jobid={h}", "--overlap", "-N1", "-n1", "-c", str(cores),
           "bash", os.path.join(ROOT, "hpc", "build_geo.sh"), "block", str(N)] + args
    try:
        sink = open(out, "a")
    except OSError as e:
        log(f"the log {out} cannot be opened ({e}), the step runs without it")
        sink = subprocess.DEVNULL
    return subprocess.Popen(cmd, stdout=sink, stderr=subprocess.STDOUT)


def run():
    jobs, live, tries, free, end, cap = plan(), {}, {}, {}, {}, {}
    full = [b for b in listed("blocksall") if not done(b)]
    log(f"start: {len(jobs)} blocks with the leg cap, {sum(j['cpu'] for j in jobs) / 3600:.0f} estimated core hours, "
        f"{len(full)} with every leg")
    out = lambda b: os.path.join(os.environ.get("GEO_LOG", "."), f"sched_{b}.log")
    t_start = quiet_since = time.time()
    seen, down, refused = {}, {}, {}   # last running or waiting, last not running; lock refusals by block
    while jobs or live or full:
        now = time.time()
        states = {}
        for h, c in holders().items():
            if h not in cap:
                cap[h], free[h] = c, c
                log(f"holder {h} with {c} cores")
            states[h], end[h] = queue_state(h)
            if states[h] in ("RUNNING", "PENDING"):
                seen[h] = now
            if states[h] != "RUNNING":
                down[h] = now
        # the running holders with ten minutes or more left: a holder that has ended or not started takes nothing
        alive = [h for h in cap if states.get(h) == "RUNNING" and end[h] - now > MARGIN]
        # a holder between running and gone may come back, for GRACE seconds after it was last running or waiting
        between = [h for h in cap if states.get(h) in BETWEEN and now - seen.get(h, t_start) <= GRACE]
        widest = max([cap[h] for h in alive], default=0)
        started = elsewhere = False
        unclear, balked = [], []

        def lock_of(b):
            """True when the block is not to be started now: run under a lock that still holds, or one that cannot be
            told (unclear), or one its block step found held three times though it reads as free here (balked)"""
            nonlocal elsewhere
            st = locked(b)
            if st == "held":
                elsewhere = True
            elif st == "unknown":
                unclear.append(b)
            elif refused.get(b, 0) >= 3:
                balked.append(b)
            else:
                return False
            return True

        for b in list(full):
            if done(b):
                full.remove(b)
                log(f"{b} done elsewhere")
                continue
            if lock_of(b):
                continue
            ok = [h for h in alive if free[h] >= 2]
            if not ok:
                continue
            h = max(ok, key=lambda h: (end[h], free[h]))
            live[srun(h, 2, [b, "full"], out(b))] = (dict(b=b, cores=2), h, now)
            free[h] -= 2
            full.remove(b)
            started = True
            log(f"started {b} on {h} with every leg on one kernel")
        for j in list(jobs):
            if done(j["b"]):
                jobs.remove(j)
                log(f"{j['b']} done elsewhere")
                continue
            if lock_of(j["b"]):
                continue
            if 0 < widest < j["cores"]:
                shape(j, min(j["m"], widest), min(j["n"], widest))
                log(f"{j['b']} cut to {j['cores']} cores, the widest running holder")
            roomy = [h for h in alive if free[h] >= j["cores"]]
            if not roomy:
                continue
            # a holder that runs for twice the estimate more if one has room, else one that may end first
            ok = [h for h in roomy if end[h] - now > 2 * j["wall"] + MARGIN] or roomy
            h = max(ok, key=lambda h: (end[h], free[h]))
            args = [j["b"]] + ([] if j["m"] == j["n"] == 1 else [str(j["n"]), str(j["m"])] + ([j["chunk"]] if j["chunk"] else []))
            live[srun(h, j["cores"], args, out(j["b"]))] = (j, h, now)
            free[h] -= j["cores"]
            jobs.remove(j)
            started = True
            log(f"started {j['b']} on {h} with {j['m']} expansions, {j['n']} parts, chunk {j['chunk'] or 'default'}, "
                f"estimate {j['wall'] / 3600:.1f} h, holder ends in {(end[h] - now) / 3600:.1f} h, free {free}")
        for p in list(live):
            if p.poll() is None:
                continue
            j, h, t0 = live.pop(p)
            free[h] += j["cores"]
            ok = done(j["b"])
            back = lambda: (jobs.insert(0, j) if "wall" in j else full.append(j["b"]))
            if p.returncode == 3 and not ok:
                refused[j["b"]] = refused.get(j["b"], 0) + 1
                log(f"{j['b']} on {h}: the block step finds its lock held, back in the list")
                back()
                continue
            if not ok and (states.get(h) != "RUNNING" or down.get(h, 0) >= t0):
                # the holder stopped running under the block (preempted, requeued, at its end): not the block's
                # failure, so it does not count as its retry
                log(f"{j['b']} on {h} ended with its holder {states.get(h) or 'gone'} (exit {p.returncode}), back in the list")
                back()
                continue
            tries[j["b"]] = tries.get(j["b"], 0) + 1
            log(f"{'done' if ok else 'FAILED'} {j['b']} on {h} exit {p.returncode} in {(time.time() - t0) / 3600:.2f} h")
            if not ok and tries[j["b"]] < 2:
                back()
        # something runs, here or under the lock of a step in the queue, or a holder waits in the queue to start or
        # may come back
        if live or started or elsewhere or any(states.get(h) == "PENDING" for h in cap) or between:
            quiet_since = now
        elif jobs or full:
            why = (f"{len(jobs) + len(full)} blocks left ({', '.join([j['b'] for j in jobs] + full)[:300]}); holders "
                   + ", ".join(f"{h} {states.get(h) or 'gone'} {cap[h]} cores"
                               + (f" {(end[h] - now) / 60:.0f} min left" if states.get(h) == "RUNNING" else "")
                               for h in cap)
                   + (f"; locks that cannot be told, which a step still in the queue may hold (remove {VD}/<block>.lock "
                      f"if none does): {sorted(set(unclear))[:20]}" if unclear else "")
                   + (f"; blocks whose step found their lock held three times, though it reads as free here (their "
                      f"sched_<block>.log says by whom): {sorted(set(balked))[:20]}" if balked else ""))
            if not any(states.get(h) == "RUNNING" for h in cap):
                log(f"GIVING UP: no holder is running, waiting in the queue or coming back. {why}")
                break
            if now - quiet_since > IDLE:
                log(f"GIVING UP: nothing could start for {IDLE:.0f} s (blocks under locks that cannot be told or that "
                    f"their step finds held, or holders with too little time or too few cores). {why}")
                break
        time.sleep(30)
    left = [b for b in listed("blocks3") + listed("blocksall") if not done(b)]
    log(f"SCHEDDONE, blocks not built from their current source: {left}")
    return 1 if left else 0


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "alive":
        sys.exit({"held": 0, "free": 1}.get(lock_state(sys.argv[2]), 2))
    if len(sys.argv) != 3 or sys.argv[1] not in ("plan", "run") or not (L and VD) or (sys.argv[1] == "run" and not HOLDERS):
        sys.exit(__doc__ + "\nrun it through hpc/build_geo.sh blocks N with GEO_SCHED set")
    if sys.argv[1] == "plan":
        for j in plan():
            print(f"{j['b']:9s} M {j['m']:2d} N {j['n']:2d} chunk {j['chunk'] or '-':3s} wall {j['wall'] / 3600:5.2f} h  "
                  f"cpu {j['cpu'] / 3600:6.1f} h")
    else:
        sys.exit(run())
