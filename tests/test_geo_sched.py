"""
tests/test_geo_sched.py  --  hpc/geo_sched.py builds what it should, where it may, and stops when nothing can run.

Run:  python3 tests/test_geo_sched.py [-v]      (python3 and bash; -v prints the scheduler's log of each case)

The scheduler runs here on a sandbox: tests/gen_smoke holds a base, a dimension-six file and a gen_geo2.fr with two
blocks, so that validate/cache_source.py gives each block the stamp of its source, srun is a script that "builds"
the block it is given (its .mx and its status line with the stamp of its current source) and records the holder,
squeue is replaced by a table of holder states that may change from one cycle to the next, or, where the locks and
the reading of squeue are under test, by a script that prints what files of jobs and steps say, which may change
from one cycle to the next too, and the clock moves 30 s a cycle.  A scheduler that waits on after 500 cycles counts
as hanging.  The cases:

  a block whose stamp is not that of its current source is not done, and a block stamped with it is,
  the plan lists the stale block and not the current one,
  run builds the stale block,
  a block starts on a holder that ends before twice its estimate when no other has room,
  a block with every leg goes to no holder that waits in the queue or has left it, nor to one with less than ten
  minutes left,
  run gives up with exit 1 when no holder is running or waiting,
  run gives up with exit 1 when nothing could start for GEO_SCHED_IDLE seconds,
  a holder still starting (CONFIGURING) is waited for, and one that stays between running and gone (COMPLETING) for
  GEO_SCHED_GRACE seconds and no longer,
  a holder stopped under its block twice (preempted, then requeued) costs the block no retry: it is built the third time,
  squeue that fails is not a holder that has gone,
  a lock whose step has left the queue, its job still running, and a lock of a process of this host that has gone,
  are taken over, and a lock whose step is in the queue is waited for until the step leaves,
  an older lock that names only its job, still in the queue, is left and named when run gives up, and so is a block
  whose step finds its lock held three times,
  geo_sched.py alive tells held (0), free (1) and cannot be told (2) for each form of lock,
  a line of the log that cannot be written is kept and written with the next, and run goes on without its log.
"""
import contextlib
import importlib.util
import io
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time as _time

REPO = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
VERBOSE = "-v" in sys.argv
HANG = 500

GEN = """(* two blocks of a model of order 2 *)
G8op1 := cX1 Phi^2 ;
G8op2 := cX2 Phi^4 ;
"""
SRUN = r"""#!/bin/bash
# srun --jobid=H --overlap -N1 -n1 -c C bash <root>/hpc/build_geo.sh block N B [ARGS]: builds B, as the block step would
h=${1#--jobid=}; c=$6; b=${11}
echo "$h $c $b" >> "$FAKE_CALLS"
python3 - "$b" <<'EOF'
import os, sys
sys.path.insert(0, os.path.join(os.environ["DIM8_ROOT"], "validate"))
import cache_source as C
b, vd = sys.argv[1], os.environ["GEO_VDIR"]
open(os.path.join(vd, b + ".mx"), "w").write("x")
open(os.path.join(vd, b + ".status"), "w").write(f"{b} | tEval 1 | tVert 1 | src {C.source_hash(b)}\n")
EOF
"""
SRUN_KILLED = r"""#!/bin/bash
# the fake srun whose first two steps end without the block, as the steps of a holder that is preempted do
n=$(grep -c . "$FAKE_CALLS" 2> /dev/null); n=${n:-0}
if [ "$n" -lt 2 ]; then echo "${1#--jobid=} $6 ${11} killed" >> "$FAKE_CALLS"; sleep 0.05; exit 143; fi
exec "$(dirname "$0")/srun" "$@"
"""
SRUN_REFUSED = r"""#!/bin/bash
# the fake srun of a block step that finds the lock of its block held (exit 3 of hpc/build_geo.sh block)
echo "${1#--jobid=} $6 ${11}" >> "$FAKE_CALLS"; exit 3
"""
SQUEUE = r"""#!/bin/bash
# squeue -h [-s] -j J [-o FMT] from the files of $FAKE_Q: fail (slurm cannot be reached), jobs ("<job> <state> <end>")
# and steps ("<job>.<step>")
[ -e "$FAKE_Q/fail" ] && { echo "squeue: error: slurm_load_jobs error: Socket timed out on send/recv operation" >&2; exit 1; }
s=0; j=; o=
while [ $# -gt 0 ]; do case $1 in -s) s=1 ;; -j) j=$2; shift ;; -o) o=$2; shift ;; esac; shift; done
if [ $s = 1 ]; then grep "^$j\." "$FAKE_Q/steps" 2> /dev/null; exit 0; fi
line=$(grep "^$j " "$FAKE_Q/jobs" 2> /dev/null) || { echo "slurm_load_jobs error: Invalid job id specified" >&2; exit 1; }
if [ "$o" = %i ]; then echo "$j"; else echo "${line#* }"; fi
"""


class Hang(Exception):
    pass


class Clock:
    """The time module of the scheduler: 30 s a cycle, and a hang after HANG cycles."""
    def __init__(self):
        self.now, self.cycles = 1.0e9, 0
        self.strftime, self.mktime, self.strptime = _time.strftime, _time.mktime, _time.strptime
        self.on_cycle = None        # called with the cycle at the start of each, to change what squeue says

    def time(self):
        return self.now

    def sleep(self, s):
        self.cycles += 1
        self.now += s
        _time.sleep(0.01)
        if self.cycles > HANG:
            raise Hang(f"still waiting after {HANG} cycles")
        if self.on_cycle:
            self.on_cycle(self.cycles)


def sandbox(base):
    """the root: validate/cache_source.py of the tree under test, the sources, the fake srun"""
    root = os.path.join(base, "root")
    os.makedirs(os.path.join(root, "validate"))
    os.makedirs(os.path.join(root, "tests", "gen_smoke"))
    shutil.copy(os.path.join(REPO, "validate", "cache_source.py"), os.path.join(root, "validate"))
    smoke = os.path.join(root, "tests", "gen_smoke")
    open(os.path.join(smoke, "gen_geo2.fr"), "w").write(GEN)
    open(os.path.join(smoke, "base_geo2_mw.fr"), "w").write("(* base *) MW := 80.4 ;\n")
    open(os.path.join(smoke, "dim6_geo.fr"), "w").write("G6cl4 := cHG Phi^2 G^2 ;\n")
    os.makedirs(os.path.join(base, "bin"))
    for name, text in (("srun", SRUN), ("srun_killed", SRUN_KILLED), ("srun_refused", SRUN_REFUSED),
                       (os.path.join("bin", "squeue"), SQUEUE)):
        open(os.path.join(base, name), "w").write(text)
        os.chmod(os.path.join(base, name), 0o755)
    return root, os.path.join(base, "srun")


def case_dirs(base, name, blocks3, blocksall, holders):
    d = os.path.join(base, name)
    for s in ("lists", "vdir", "log"):
        os.makedirs(os.path.join(d, s))
    open(os.path.join(d, "lists", "blocks3"), "w").write("".join(b + "\n" for b in blocks3))
    open(os.path.join(d, "lists", "blocksall"), "w").write("".join(b + "\n" for b in blocksall))
    open(os.path.join(d, "holders"), "w").write("".join(f"{h} {c}\n" for h, c in holders))
    return d


def load(root, d, idle=3600):
    """hpc/geo_sched.py of the tree under test, fresh, for case directory d"""
    os.environ.update(DIM8_ROOT=root, GEO_LISTS=os.path.join(d, "lists"), GEO_VDIR=os.path.join(d, "vdir"),
                      GEO_LOG=os.path.join(d, "log"), GEO_SCHED=os.path.join(d, "holders"),
                      GEO_SCHED_IDLE=str(idle), GEO_SCHED_GRACE="900", DIM8_BASE="base_geo2_mw.fr;dim6_geo.fr;gen_geo2.fr",
                      FAKE_CALLS=os.path.join(d, "calls"), PYTHONDONTWRITEBYTECODE="1")
    sys.modules.pop("cache_source", None)
    argv, sys.argv = sys.argv, ["geo_sched.py", "run", "2"]
    try:
        spec = importlib.util.spec_from_file_location("geo_sched_" + os.path.basename(d),
                                                      os.path.join(REPO, "hpc", "geo_sched.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
    finally:
        sys.argv = argv
    return m


def stamp(root, b):
    sys.path.insert(0, os.path.join(root, "validate"))
    sys.modules.pop("cache_source", None)
    import cache_source as C
    sys.path.pop(0)
    return C.source_hash(b)


def put(d, b, src):
    open(os.path.join(d, "vdir", b + ".mx"), "w").write("x")
    open(os.path.join(d, "vdir", b + ".status"), "w").write(f"{b} | tEval 1 | tVert 1 | src {src}\n")


def wire(m, srun, table):
    """the clock, the fake srun and the queue: table(holder, cycle, now) -> (state, end)"""
    clock = Clock()
    m.time, m.SRUN = clock, srun
    seen = []

    def queue_state(h):
        s, e = table(h, clock.cycles, clock.now)
        return s, (e if s == "RUNNING" else 0)
    m.queue_state = queue_state
    m.end_of = lambda h: queue_state(h)[1]          # the scheduler before queue_state
    real = m.srun

    def srun_(h, cores, args, out):
        seen.append((h, clock.cycles) + queue_state(h) + (clock.now,))
        return real(h, cores, args, out)
    m.srun = srun_
    return clock, seen


def wire_q(m, srun, squeue, d, script):
    """the clock and a fake srun, with the scheduler's own reading of squeue and of the locks, on the fake squeue,
    whose files in d/q script(q, cycle) writes at the start of each cycle"""
    clock = Clock()
    q = os.path.join(d, "q")
    os.makedirs(q, exist_ok=True)
    os.environ["FAKE_Q"] = q
    m.time, m.SRUN, m.SQUEUE = clock, srun, squeue
    clock.on_cycle = lambda c: script(q, c)
    script(q, 0)
    seen = []
    real = m.srun

    def srun_(h, cores, args, out):
        seen.append((h, clock.cycles))
        return real(h, cores, args, out)
    m.srun = srun_
    return clock, seen


def qfiles(q, jobs=(), steps=(), fail=False):
    """what the fake squeue prints: jobs as (job, "<state> <end>"), steps as "<job>.<step>", fail for a squeue that
    cannot reach slurm"""
    open(os.path.join(q, "jobs"), "w").write("".join(f"{j} {s}\n" for j, s in jobs))
    open(os.path.join(q, "steps"), "w").write("".join(f"{x}\n" for x in steps))
    f = os.path.join(q, "fail")
    if fail:
        open(f, "w").close()
    elif os.path.exists(f):
        os.remove(f)


def lock(d, b, line):
    os.makedirs(os.path.join(d, "vdir", b + ".lock"))
    open(os.path.join(d, "vdir", b + ".lock", "job"), "w").write(line + "\n")


def calls(d):
    p = os.path.join(d, "calls")
    return [line.split() for line in open(p)] if os.path.exists(p) else []


def logged(d):
    p = os.path.join(d, "log", "sched.log")
    return open(p).read() if os.path.isfile(p) else ""


def run(m):
    try:
        return m.run(), ""
    except Hang as e:
        return None, str(e)


def main() -> int:
    base = tempfile.mkdtemp()
    root, srun = sandbox(base)
    os.environ["DIM8_BASE"] = "base_geo2_mw.fr;dim6_geo.fr;gen_geo2.fr"
    cur1, cur2 = stamp(root, "G8op1"), stamp(root, "G8op2")
    stale = "0123456789abcdef"
    results = []

    def check(name, ok, detail="", d=None):
        results.append(bool(ok))
        print(f"{'ok  ' if ok else 'FAIL'} {name}" + ("" if ok else f": {detail}"))
        if VERBOSE and d:
            print("".join("     " + line + "\n" for line in logged(d).splitlines()))

    try:
        # done(): the stamp against the current source
        d = case_dirs(base, "done", ["G8op1"], [], [("h1", 4)])
        put(d, "G8op1", stale)
        m = load(root, d)
        a = m.done("G8op1")
        put(d, "G8op1", cur1)
        b = load(root, d).done("G8op1")
        check("a stale block is not done, a current one is", a is False and b is True, f"stale {a}, current {b}")

        d = case_dirs(base, "plan", ["G8op1", "G8op2"], [], [("h1", 4)])
        put(d, "G8op1", stale)
        put(d, "G8op2", cur2)
        listed = [j["b"] for j in load(root, d).plan()]
        check("the plan lists the stale block and not the current one", listed == ["G8op1"], f"plan {listed}")

        # run builds the stale block, on a holder with time to spare
        d = case_dirs(base, "rebuild", ["G8op1"], [], [("h1", 4)])
        put(d, "G8op1", stale)
        m = load(root, d)
        wire(m, srun, lambda h, c, now: ("RUNNING", 1.0e9 + 36000))
        rc, hang = run(m)
        st = m.C.state(os.path.join(d, "vdir"), "G8op1") if hasattr(m, "C") else "?"
        check("run builds the stale block", rc == 0 and [c[2] for c in calls(d)] == ["G8op1"] and st == "current",
              f"exit {rc} {hang}, srun calls {calls(d)}", d)

        # no holder runs for twice the estimate (4500 s): the block starts on the one there is
        d = case_dirs(base, "fallback", ["G8op1"], [], [("h1", 4)])
        m = load(root, d)
        wire(m, srun, lambda h, c, now: ("RUNNING", 1.0e9 + 9000))
        rc, hang = run(m)
        check("a block starts on a holder that ends before twice its estimate when no other has room",
              rc == 0 and [c[:3] for c in calls(d)] == [["h1", "1", "G8op1"]], f"exit {rc} {hang}, srun calls {calls(d)}", d)

        # a block with every leg: h1 waits in the queue for five cycles and h2 has gone, and then with h3 beside them,
        # which has five minutes left
        def table(h, c, now):
            if h == "h1":
                return ("PENDING", 0) if c < 5 else ("RUNNING", now + 36000)
            if h == "h2":
                return "", 0
            return "RUNNING", 1.0e9 + 300
        for name, hs, what in (("full", [("h1", 4), ("h2", 4)], "waits in the queue or has gone"),
                               ("full3", [("h1", 4), ("h2", 4), ("h3", 4)], "has under ten minutes")):
            d = case_dirs(base, name, [], ["G8op2"], hs)
            m = load(root, d)
            _, seen = wire(m, srun, table)
            rc, hang = run(m)
            bad = [s for s in seen if s[2] != "RUNNING" or s[3] - s[4] <= 600]
            check(f"a block with every leg goes to no holder that {what}",
                  rc == 0 and seen and not bad and seen[0][0] == "h1", f"exit {rc} {hang}, started on {seen}", d)

        # every holder has left the queue
        d = case_dirs(base, "gone", ["G8op1"], [], [("h1", 4)])
        m = load(root, d)
        wire(m, srun, lambda h, c, now: ("", 0))
        rc, hang = run(m)
        check("run gives up with exit 1 when no holder is running or waiting",
              rc == 1 and "GIVING UP: no holder is running" in logged(d) and not calls(d), f"exit {rc} {hang}", d)

        # a holder of one core and a block with every leg, which takes two: nothing can start
        d = case_dirs(base, "idle", [], ["G8op2"], [("h1", 1)])
        m = load(root, d, idle=600)
        clock, _ = wire(m, srun, lambda h, c, now: ("RUNNING", 1.0e9 + 360000))
        rc, hang = run(m)
        check("run gives up with exit 1 when nothing could start for GEO_SCHED_IDLE seconds",
              rc == 1 and "GIVING UP: nothing could start" in logged(d) and clock.cycles <= 30,
              f"exit {rc} {hang} after {clock.cycles} cycles", d)

        # a holder still starting for three cycles
        d = case_dirs(base, "configuring", ["G8op1"], [], [("h1", 4)])
        m = load(root, d)
        _, seen = wire(m, srun, lambda h, c, now: ("CONFIGURING", 0) if c < 3 else ("RUNNING", now + 36000))
        rc, hang = run(m)
        check("a holder still starting (CONFIGURING) is waited for", rc == 0 and seen and seen[0][1] >= 3 and calls(d),
              f"exit {rc} {hang}, started {seen}", d)

        # a holder between running and gone from the start, for good
        d = case_dirs(base, "completing", ["G8op1"], [], [("h1", 4)])
        m = load(root, d)
        clock, _ = wire(m, srun, lambda h, c, now: ("COMPLETING", 0))
        rc, hang = run(m)
        check("a holder that stays between running and gone is waited for GEO_SCHED_GRACE seconds and no longer",
              rc == 1 and "GIVING UP: no holder is running" in logged(d) and 29 <= clock.cycles <= 32 and not calls(d),
              f"exit {rc} {hang} after {clock.cycles} cycles", d)

        # the holder preempted under the block's first step and requeued under its second: each step ends without the
        # block while the holder is COMPLETING, then PENDING, then RUNNING again
        d = case_dirs(base, "preempted", ["G8op1"], [], [("h1", 4)])
        m = load(root, d)
        box = {"seen": []}

        def table(h, c, now):
            for s in box["seen"][:2]:
                if s[1] < c <= s[1] + 3:
                    return "COMPLETING", 0
                if s[1] + 3 < c <= s[1] + 6:
                    return "PENDING", 0
            return "RUNNING", now + 36000
        _, box["seen"] = wire(m, os.path.join(base, "srun_killed"), table)
        rc, hang = run(m)
        log_ = logged(d)
        check("a holder stopped under its block twice costs the block no retry: it is built the third time",
              rc == 0 and len(calls(d)) == 3 and log_.count("ended with its holder") == 2 and "FAILED" not in log_,
              f"exit {rc} {hang}, srun calls {calls(d)}", d)

        # squeue cannot reach slurm for three cycles, then says the holder runs
        end = _time.strftime("%Y-%m-%dT%H:%M:%S", _time.localtime(1.0e9 + 36000))
        squeue = os.path.join(base, "bin", "squeue")
        d = case_dirs(base, "squeue_fails", ["G8op1"], [], [("h1", 4)])
        m = load(root, d)
        _, seen = wire_q(m, srun, squeue, d, lambda q, c: qfiles(q, [("h1", f"RUNNING {end}")], fail=c < 3))
        rc, hang = run(m)
        qfiles(os.path.join(d, "q"), [("h1", f"RUNNING {end}")], fail=True)
        st = m.queue_state("h1")
        check("squeue that fails is not a holder that has gone",
              rc == 0 and seen and seen[0][1] >= 3 and st == ("UNKNOWN", 0), f"exit {rc} {hang}, started {seen}, "
              f"a failing squeue reads {st}", d)

        # the locks, which the fake srun does not take: it builds the block once it is started
        host = socket.gethostname()
        p = subprocess.Popen(["true"])
        p.wait()
        dead = p.pid
        running = [("h1", f"RUNNING {end}")]
        for name, line, steps, what in (
                ("lock_step_gone", "h1.7 node9:1", ["h1.3"], "a lock whose step has left the queue, its job still running,"),
                ("lock_pid_gone", f"- {host}:{dead}", [], "a lock of a process of this host that has gone")):
            d = case_dirs(base, name, ["G8op1"], [], [("h1", 4)])
            lock(d, "G8op1", line)
            m = load(root, d)
            wire_q(m, srun, squeue, d, lambda q, c, steps=steps: qfiles(q, running, steps))
            rc, hang = run(m)
            check(f"{what} is taken over", rc == 0 and calls(d), f"exit {rc} {hang}, srun calls {calls(d)}", d)

        d = case_dirs(base, "lock_step_held", ["G8op1"], [], [("h1", 4)])
        lock(d, "G8op1", "h1.7 node9:1")
        m = load(root, d)
        _, seen = wire_q(m, srun, squeue, d, lambda q, c: qfiles(q, running, ["h1.7"] if c < 5 else []))
        rc, hang = run(m)
        check("a lock whose step is in the queue is waited for until the step leaves",
              rc == 0 and seen and seen[0][1] >= 5, f"exit {rc} {hang}, started {seen}", d)

        d = case_dirs(base, "lock_job_only", ["G8op1"], [], [("h1", 4)])
        lock(d, "G8op1", "h1")
        m = load(root, d, idle=600)
        clock, _ = wire_q(m, srun, squeue, d, lambda q, c: qfiles(q, running))
        rc, hang = run(m)
        log_ = logged(d)
        check("an older lock that names only its job, still in the queue, is left and named when run gives up",
              rc == 1 and "locks that cannot be told" in log_ and "['G8op1']" in log_ and not calls(d)
              and clock.cycles <= 25, f"exit {rc} {hang} after {clock.cycles} cycles, srun calls {calls(d)}", d)

        d = case_dirs(base, "refused", ["G8op1"], [], [("h1", 4)])
        m = load(root, d, idle=600)
        wire(m, os.path.join(base, "srun_refused"), lambda h, c, now: ("RUNNING", now + 36000))
        rc, hang = run(m)
        check("a block whose step finds its lock held three times is left and named when run gives up",
              rc == 1 and len(calls(d)) == 3 and "found their lock held three times" in logged(d),
              f"exit {rc} {hang}, srun calls {calls(d)}", d)

        # geo_sched.py alive, as hpc/build_geo.sh asks it, on the fake squeue
        q = os.path.join(base, "alive_q")
        os.makedirs(q)
        env = dict(os.environ, PATH=os.path.dirname(squeue) + os.pathsep + os.environ.get("PATH", ""), FAKE_Q=q,
                   DIM8_ROOT=root)
        got, want = [], []
        for line, steps, fail, code in (
                (f"- {host}:{os.getpid()}", [], False, 0), (f"- {host}:{dead}", [], False, 1),
                ("h1.7 node9:1", ["h1.7"], False, 0), ("h1.7 node9:1", ["h1.3"], False, 1),
                ("h1.7 node9:1", [], True, 2), ("h1", [], False, 2), ("h2", [], False, 1), ("node9:5", [], False, 2),
                (f"h1 {host}:{os.getpid()}", [], False, 0), (f"h1 {host}:{dead}", [], False, 1)):
            qfiles(q, running, steps, fail)
            r = subprocess.run([sys.executable, os.path.join(REPO, "hpc", "geo_sched.py"), "alive", line], env=env,
                               capture_output=True, text=True)
            got.append((line, r.returncode))
            want.append((line, code))
        check("geo_sched.py alive tells held (0), free (1) and cannot be told (2)", got == want,
              f"{[g for g, w in zip(got, want) if g != w]}, wanted {[w for g, w in zip(got, want) if g != w]}")

        # the log cannot be written: a directory stands where it would be
        d = case_dirs(base, "log", ["G8op1"], [], [("h1", 4)])
        os.makedirs(os.path.join(d, "log", "sched.log"))
        m = load(root, d)
        err = ""
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                m.log("one")
            os.rmdir(os.path.join(d, "log", "sched.log"))
            m.log("two")
        except OSError as e:
            err = repr(e)
        lines = [line.split(" ", 1)[1] for line in logged(d).splitlines()]
        check("a line of the log that cannot be written is written with the next", not err and lines == ["one", "two"],
              err or f"log {lines}")
        # nor the log of the block's step
        d = case_dirs(base, "nolog", ["G8op1"], [], [("h1", 4)])
        os.makedirs(os.path.join(d, "log", "sched.log"))
        os.makedirs(os.path.join(d, "log", "sched_G8op1.log"))
        m = load(root, d)
        wire(m, srun, lambda h, c, now: ("RUNNING", 1.0e9 + 36000))
        try:
            with contextlib.redirect_stderr(io.StringIO()):
                rc, hang = run(m)
            err = ""
        except OSError as e:
            rc, hang, err = None, "", repr(e)
        check("run goes on without its log or the log of the step", rc == 0 and calls(d),
              err or f"exit {rc} {hang}, srun calls {calls(d)}")
    finally:
        shutil.rmtree(base, ignore_errors=True)
    print(f"\n{sum(results)}/{len(results)} passed")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
