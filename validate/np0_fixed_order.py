#!/usr/bin/env python3
"""The check of validate/np0_shift.py's mode for combined models against the fixed-order expansion
of the full result, and the controls of that mode with the real generator.

    NP0REF_DIR=<work dir> MG5_DIR=<MadGraph> DIM8_MODEL=<model whose W mass moves, dim68_is> \
        validate/np0_fixed_order.py points | udx | ww | controls --mw <dim68_mw> | report  [options]

np0_shift.py finds the order 1/Lambda^2 and 1/Lambda^4 terms of a cross section in a model whose W
mass moves from runs at three scales, through X(t)/t = x1 + x2 t + x3 t^2 (its docstring).  This
script finds the same terms a second way, as the coefficients of t and t^2 of the full result at
fixed order, every NP order up to the truncation and no NP^2 selection, computed at many scales,
and compares the two.  Run it after a change to that mode or to the input scheme of the models, and
to reproduce the numbers the paper quotes.  Every part works under NP0REF_DIR, makes what it needs
there when it is missing (MadGraph outputs, an event sample, the runs) and reuses what it finds,
prints its table, writes its numbers into NP0REF_DIR/reference.tsv (process, quantity, value,
error, in pb, at --lam with every coefficient of both sectors at one) and returns nonzero when one
of its checks fails.

  points    u d~ > e+ ve at fixed phase-space points (sqrt(s) from 40 GeV to 1 TeV, two angles),
            with the squared matrix elements of standalone outputs of the process at NP=0,
            NP^2==1, NP^2==2 and with no NP^2 selection, at forty scales from 2 to 50 TeV, so that
            nothing is a Monte Carlo estimate.  The t^2 coefficient c2 of the full |M|^2 is fitted
            in t, and compared with (A) the pieces fitted in t and (B) the expansion term by term,
            S2 + a m0 S1' + b m0 S0' + (a m0)^2 S0''/2, the derivatives in M_W^2 taken by moving M_W
            with one dimension-eight coefficient alone (--knob).  Then the recipe of np0_shift.py
            with the scales of --recipe (sets split by /), and the share of c2 it gets wrong.
            Must pass: (A) and (B) equal c2 to 1e-6 of it at every point, NP=0 and NP^2==1/t agree
            with the scans of M_W at the same M_W to 1e-4, and the t coefficient of the full |M|^2
            is NP^2==1 plus the linear part of NP=0 to 1e-9.
  udx       u d~ > e+ ve at 13.6 TeV with m(e+ ve) > --mmin GeV (100), on Standard-Model samples
            of MadEvent, one in each slice of m(e+ ve) (upper edges --slices
            300,600,1000,1500,2000,2500,3000,4000,5500, the last slice open, --nev 40000 events
            each, --seed 21), since the terms that grow with the energy live where one sample of
            the SM has no events: at 3 TeV NP^2==2 is 26.8 fb, with -28 fb from below 300 GeV and
            +30 fb from above 1 TeV, and one sample of 200000 events, 32 of them above 1 TeV, gave
            15.8 +- 5.9 fb.  Each event is reweighted by the exact squared matrix elements of the
            four outputs at the forty scales, so that every cross section is made of the same
            events and their differences are exactly correlated.  Prints NP^2==2 in each slice,
            the t and t^2 terms of the full cross section at --lam (3000 GeV), the pieces of the
            t^2 term, the tags alone, and the recipe at each set of --recipe.  The errors come from
            twenty batches, each a twentieth of every slice.  Must pass: the pieces add up to the
            full t^2 term to 1e-6 of it, the recipe's x1 t is the full t term to 1e-3 of it at
            every set of scales, and with the first set the recipe's t^2 term at M_W0 is the full
            one to two per cent.
  ww        p p > w+ w- at 13.6 TeV: np0_shift.py itself on a study of that process with --seeds
            (21,22,23) and --nev (20000) events a run (--part recipe), and the full cross section
            with the same seeds at Lambda = 3, 3.5, 4, 5, 6, 8 and 12 TeV and with the coefficients
            off (--part full), with NP^2==3 and NP^2==4 at 3 TeV and the first seed (--part pieces),
            which are taken out as t^3 and t^4 before c1 t + c2 t^2 is fitted to each seed (--part
            fit).  --recipe-seeds names the seeds whose recipe enters its means (those of --seeds,
            or more of them, since a seed of the recipe needs no full run).  Each seed of full has
            a copy of the process directory of its own, so that seeds can run side by side as
            separate calls.  Must pass: the recipe's x1 t and the fit's c1 t, and the recipe's t^2
            term at M_W0 and the fit's c2 t^2, agree within three errors of the difference of their
            means over the seeds.
  controls  np0_shift.py with --seeds in the processes of udx and ww (--procs udx,ww), in three
            models (--arms a,b,c).  --part prepare makes the frozen copy and the studies, run makes
            the runs, check only judges them, and all does the three.
            (a) --mw, dim68_mw, in which M_W is an input and the coefficients reach NP=0 nowhere:
            NP=0 with the coefficients on must equal NP=0 with them off at every scale, x2 t^2
            must vanish within its error and x1 t must equal NP^2==1.  Before it runs, the model is
            checked to be the release of DIM8_MODEL: the same files, the same coefficients and one
            scale Lam, without a Lam6.  (b) A copy of DIM8_MODEL whose W mass is frozen at its value
            with every coefficient at zero, which the script makes under NP0REF_DIR/models.  The
            mode then returns the tagged terms alone: it must reproduce them, x1 t the NP^2==1 term
            and the t^2 term NP^2==2, both at the unshifted mass, within three errors, and it must
            miss the full result of udx and ww, in x1 t or in the shift of the t^2 term, by more
            than five errors.  (c) DIM8_MODEL itself in u d~ > e+ ve, whose x1 t must agree with
            the full t term of udx within three errors, which shows that the runs and the
            reweighted sample compute the same thing.  Returns zero only when (a) and (c) pass and
            (b) fails as it must.  Needs the reference rows of udx and ww.
  report    prints NP0REF_DIR/reference.tsv.

Errors on a mean over seeds come from the spread of the seeds, as np0_shift.py quotes them.  The
checks of (a) allow in addition for the digits to which the runs record a cross section.  Of the
rows of np0_shift.py only those of --nev events and of the settings of the study's line are used,
and rows from before the settings were recorded are counted and left out, as np0_shift.py does.
Environment: NP0REF_DIR, MG5_DIR and DIM8_MODEL are required.  NCORES (8) sets the cores of a
MadEvent run and the threads of the reweighting, PYTHON (python3.11) the Python of MadGraph and
of the UFO.  Everything runs from the repository copy of np0_shift.py, set_cards.py and
eval_ufo_params.py, so a change to them is what this script tests.
"""
from __future__ import annotations

import gzip
import hashlib
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
import np0_shift as N  # noqa: E402  (reads DIM8_MODEL)

R = os.environ.get("NP0REF_DIR", "")
MG = os.environ.get("MG5_DIR", "")
MODEL = os.path.abspath(os.environ["DIM8_MODEL"].rstrip("/")) if os.environ.get("DIM8_MODEL") else ""
NCORES = int(os.environ.get("NCORES", "8"))
PY = os.environ.get("PYTHON", "python3.11")
SET_CARDS = os.path.join(ROOT, "examples", "studies", "set_cards.py")
# 13.6 TeV and the run settings of np0_shift.py, so that the two sides differ only in the orders
COMMON = ["ebeam1=6800", "ebeam2=6800", "hel_recycling=False", "use_syst=False", "dynamical_scale_choice=3"]
UDX = "u d~ > e+ ve QCD<=99 QED<=99"
WW = "p p > w+ w- QCD<=99 QED<=99"
PIECES = ("np0", "np1", "np2", "full")
ORDERS = {"np0": "NP=0", "np1": "NP<=4 NP^2==1", "np2": "NP<=4 NP^2==2", "full": "NP<=4"}
# forty scales from 2 to 50 TeV, rounded to ten digits so that the card (which MadGraph reads into
# twenty characters, so thirteen digits) carries the scale the fits use exactly
LAMS40 = [float(f"{2000 * 25.0 ** (i / 39.0):.10g}") for i in range(40)]
# the scales of the full p p > w+ w- runs (0: every coefficient off)
LAMS_WW = [0.0, 3000.0, 3500.0, 4000.0, 5000.0, 6000.0, 8000.0, 12000.0]
REF_HEAD = "process\tquantity\tvalue\terror\tsource"
FAILED = []

# Evaluates SMATRIX at the phase-space points of a file, for the parameter card named on the command
# line, and prints each value with 17 significant digits, and M_W as the Fortran computes it from the
# card, since that is the mass the matrix element sees.
MEDRV = """\
      PROGRAM MEDRV
      IMPLICIT NONE
      INCLUDE 'nexternal.inc'
      INCLUDE 'coupl.inc'
      REAL*8 P(0:3,NEXTERNAL), ANS
      CHARACTER*512 CARD, PSF
      INTEGER I, J, NPT
      CALL GETARG(1, CARD)
      CALL GETARG(2, PSF)
      CALL SETPARA(CARD)
      WRITE(*,'(A,ES26.17)') 'MW ', MDL_MW
      OPEN(UNIT=21, FILE=PSF, STATUS='OLD')
      READ(21,*) NPT
      DO I=1,NPT
        DO J=1,NEXTERNAL
          READ(21,*) P(0,J),P(1,J),P(2,J),P(3,J)
        ENDDO
        CALL SMATRIX(P,ANS)
        WRITE(*,'(A,I6,1X,ES26.17)') 'ME ', I, ANS
      ENDDO
      END
"""


def opt(argv, name, default):
    return argv[argv.index(name) + 1] if name in argv else default


def check(name, ok, what=""):
    print(("PASS " if ok else "FAIL ") + name + (f"   [{what}]" if what else ""), flush=True)
    if not ok:
        FAILED.append(name)
    return ok


def need():
    """Stop unless the environment names a work directory, MadGraph and a UFO."""
    miss = [k for k, v in (("NP0REF_DIR", R), ("MG5_DIR", MG), ("DIM8_MODEL", MODEL)) if not v]
    if miss:
        sys.exit("set " + ", ".join(miss) + " (see the docstring)")
    if not os.path.exists(os.path.join(MODEL, "parameters.py")):
        sys.exit(f"DIM8_MODEL={MODEL} is not a UFO")
    os.makedirs(R, exist_ok=True)


def mg5(script, log):
    """One MadGraph session running the commands of script, logged to log."""
    sc = re.sub(r"\.log$", "", log) + ".mg5"
    open(sc, "w").write("set automatic_html_opening False\n" + script)
    return N.run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc], log)


def cores(d):
    """MadEvent in the process directory d runs on NCORES cores."""
    open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
        f"run_mode = 2\nnb_core = {NCORES}\nautomatic_html_opening = False\n")


def mean_err(v):
    """The mean of the values and the error of the mean from their spread."""
    n = len(v)
    m = sum(v) / n
    return m, ((sum((u - m) ** 2 for u in v) / (n - 1) / n) ** 0.5 if n > 1 else float("nan"))


def ref_put(proc, rows, source):
    """Rows (quantity, value, error) of a process into NP0REF_DIR/reference.tsv, in place of the rows
    of that process and quantity already there."""
    p = os.path.join(R, "reference.tsv")
    old = [l.split("\t") for l in open(p).read().split("\n")[1:] if l] if os.path.exists(p) else []
    keys = {(proc, q) for q, _, _ in rows}
    new = [r for r in old if (r[0], r[1]) not in keys] + [[proc, q, f"{v:.10g}", f"{e:.4g}", source] for q, v, e in rows]
    open(p, "w").write("\n".join([REF_HEAD] + ["\t".join(r) for r in new]) + "\n")


def ref_get():
    p = os.path.join(R, "reference.tsv")
    if not os.path.exists(p):
        return {}
    return {(r[0], r[1]): (float(r[2]), float(r[3]))
            for r in (l.split("\t") for l in open(p).read().split("\n")[1:] if l)}


def study_dir(name, line):
    """A study directory under NP0REF_DIR with one process, the line of its processes.txt."""
    st = os.path.join(R, f"study_{name}")
    os.makedirs(st, exist_ok=True)
    p = os.path.join(st, "processes.txt")
    want = f"# made by validate/np0_fixed_order.py\n{line}\n"
    if not os.path.exists(p):
        open(p, "w").write(want)
    elif open(p).read() != want:
        sys.exit(f"{p} holds another process than {line}")
    return st


def np0(model, study, seed, nev, lams, lam):
    """np0_shift.py on the study with the model, one seed, its process directories under
    NP0REF_DIR/build.  Runs already in the study's results file are not made again."""
    env = dict(os.environ, DIM8_MODEL=model, DIM8_BUILD=os.path.join(R, "build"), NP0_CORES=str(NCORES), MG5_DIR=MG)
    print(f"\n== np0_shift.py {study} --seed {seed}, model {os.path.basename(model)}", flush=True)
    return subprocess.run([PY, os.path.join(ROOT, "validate", "np0_shift.py"), study, "--nev", str(nev),
                           "--seed", str(seed), "--lams", lams, "--lam", f"{lam:g}"], env=env).returncode


# ---------------------------------------------------------------- standalone matrix elements

def _pdir(d):
    """The one subprocess directory of a standalone output, or None."""
    sp = os.path.join(d, "SubProcesses")
    p = sorted(x for x in os.listdir(sp) if x.startswith("P")) if os.path.isdir(sp) else []
    return os.path.join(sp, p[0]) if len(p) == 1 and os.path.exists(os.path.join(sp, p[0], "matrix.f")) else None


def standalone():
    """The standalone outputs of u d~ > e+ ve at NP=0, NP^2==1, NP^2==2 and with no NP^2 selection,
    under NP0REF_DIR/me, each with medrv built beside its matrix element.  Returns their prefix."""
    pre = os.path.join(R, "me", "udx")
    os.makedirs(os.path.dirname(pre), exist_ok=True)
    new = [k for k in PIECES if not _pdir(f"{pre}_{k}")]
    if new:
        mg5(f"import model {MODEL}\n" + "".join(f"generate {UDX} {ORDERS[k]}\noutput standalone {pre}_{k} -f\n"
                                                 for k in new), pre + "_gen.log")
    src = os.path.join(R, "me", "medrv.f")
    if not os.path.exists(src) or open(src).read() != MEDRV:
        open(src, "w").write(MEDRV)
    for k in PIECES:
        p = _pdir(f"{pre}_{k}")
        if not p:
            sys.exit(f"no standalone output {pre}_{k}, see {pre}_gen.log")
        if os.path.exists(os.path.join(p, "medrv")):
            continue
        log = os.path.join(p, "build.log")
        N.run(["make", f"-j{NCORES}", "check"], log, cwd=p)
        N.run(["gfortran", "-O", "-w", "-ffixed-line-length-132", "-I.", "-I../../Source/MODEL", "-I../../Source",
               "-o", "medrv", src, "matrix.o", "-L../../lib", "-ldhelas", "-lmodel"], log, cwd=p)
        if not os.path.exists(os.path.join(p, "medrv")):
            sys.exit(f"medrv did not build in {p}, see {log}")
    return pre


def card(src, dst, lam, c6=1.0, c8=1.0, extra=None):
    """A copy of the card src with every dimension-six coefficient at c6 (a complex one as modulus c6
    and phase zero), every entry of DIM8 and DIM8F at c8, Lam at lam GeV, then the named overrides."""
    extra = dict(extra or {})
    out, blk = [], None
    for l in open(src).read().split("\n"):
        mb = re.match(r"^\s*block\s+(\S+)", l, re.I)
        if mb:
            blk = mb.group(1).upper()
        m = re.match(r"^(\s*\d+\s+)([-+\d.eE]+)(\s*#\s*(\w+).*)$", l)
        if m and blk in ("DIM6", "DIM8", "DIM8F"):
            name = m.group(4)
            if name in extra:
                v = extra.pop(name)
            elif name == "Lam":
                v = lam
            elif blk == "DIM6":
                v = 0.0 if name.endswith("Ph") else c6
            else:
                v = c8
            l = f"{m.group(1)}{v:.12e}{m.group(3)}"
        elif m and m.group(4) in extra:
            l = f"{m.group(1)}{extra.pop(m.group(4)):.12e}{m.group(3)}"
        out.append(l)
    if extra:
        sys.exit(f"not in the card {src}: {extra}")
    open(dst, "w").write("\n".join(out))


_runs = {}


def medrv(d, crd, ps):
    """M_W and the squared matrix elements at the points of ps, of the output d with the card crd."""
    key = (d, crd, ps)
    if key not in _runs:
        exe = os.path.join(_pdir(d), "medrv")
        o = subprocess.run([exe, crd, ps], capture_output=True, text=True, cwd=os.path.dirname(exe)).stdout
        mw = float(re.search(r"^MW\s+(\S+)", o, re.M).group(1).replace("D", "E"))
        me = [float(x.replace("D", "E")) for x in re.findall(r"^ME\s+\d+\s+(\S+)", o, re.M)]
        _runs[key] = (mw, me)
    return _runs[key]


def prefetch(jobs):
    """medrv for (dir, card, points) triples, NCORES at a time, into the cache of medrv(): each call
    spends about fifteen seconds reading the full model's card."""
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(NCORES) as ex:
        list(ex.map(lambda j: medrv(*j), jobs))


def lsq(xs, ys, deg):
    """Least-squares polynomial of degree deg in 50-digit arithmetic, so that the solver adds nothing
    to the rounding of the double-precision data."""
    import mpmath as mp
    mp.mp.dps = 50
    xs = [mp.mpf(x) for x in xs]
    ys = [mp.mpf(y) for y in ys]
    s = max(abs(x) for x in xs)
    A = mp.matrix([[(x / s) ** k for k in range(deg + 1)] for x in xs])
    Q, Rm = mp.qr(A)
    c = mp.lu_solve(Rm[:deg + 1, :deg + 1], (Q.T * mp.matrix(ys))[:deg + 1])
    return [c[k] / s ** k for k in range(deg + 1)]


def coeff(xs, ys, k, xmaxes, minpts=10):
    """The x^k coefficient of a function sampled at xs, from polynomial fits over the ranges
    |x| <= xmax and degrees from k + 2 up.  For each range the error is the spread of the last three
    degrees, and the range with the smallest error wins.  Returns (value, error, xmax)."""
    import mpmath as mp
    best = None
    for xm in xmaxes:
        sel = [(x, y) for x, y in zip(xs, ys) if abs(x) <= xm * (1 + 1e-12)]
        if len(sel) < minpts:
            continue
        X, Y = [x for x, _ in sel], [y for _, y in sel]
        vals = [lsq(X, Y, d)[k] for d in range(k + 2, min(11, len(sel) - 3) + 1)]
        if len(vals) < 3:
            continue
        v = vals[-1]
        e = max(abs(u - v) for u in vals[-3:]) + mp.mpf(10) ** -40
        if best is None or e / max(abs(v), mp.mpf(10) ** -300) < best[1] / max(abs(best[0]), mp.mpf(10) ** -300):
            best = (v, e, xm)
    return best


def T(lam):
    """t = 1/Lambda^2 in TeV^-2."""
    return (1000.0 / lam) ** 2


# ---------------------------------------------------------------- points

def cmd_points(argv):
    import mpmath as mp
    knob = opt(argv, "--knob", "c8l2H4Dx2")
    recipes = [[float(x) for x in r.split(",")] for r in opt(argv, "--recipe", "2000,3000,4000/4000,6000,8000").split("/")]
    rs = [float(x) for x in opt(argv, "--sqrts", "40,60,70,75,78,79.5,80.3,81,83,86,90,100,130,200,350,600,1000").split(",")]
    cs = [float(x) for x in opt(argv, "--costh", "-0.5,0.3").split(",")]
    pre = standalone()
    # the two incoming partons along +-z and the outgoing pair at polar angle theta and azimuth 0.7;
    # no W is external, so the points do not depend on M_W and serve every card
    ps = os.path.join(R, "me", "ps_points.txt")
    labels = [(r, c) for r in rs for c in cs]
    with open(ps, "w") as f:
        f.write(f"{len(labels)}\n")
        for r, c in labels:
            e, s, ph = r / 2, math.sqrt(1 - c * c), 0.7
            for v in ((e, 0, 0, e), (e, 0, 0, -e), (e, e * s * math.cos(ph), e * s * math.sin(ph), e * c),
                      (e, -e * s * math.cos(ph), -e * s * math.sin(ph), -e * c)):
                f.write(" ".join(f"{x:.17e}" for x in v) + "\n")
    wd = os.path.join(R, "me", "cards_points")
    os.makedirs(wd, exist_ok=True)
    src = os.path.join(pre + "_full", "Cards", "param_card.dat")
    gw = float(re.search(r"^\s*DECAY\s+24\s+(\S+)", open(src).read(), re.M | re.I).group(1))
    npt = len(labels)
    D = {k: {} for k in PIECES}
    MW = {}
    sm = os.path.join(wd, "sm.dat")
    card(src, sm, 3000.0, 0.0, 0.0)
    cards = {}
    for lam in sorted(set(LAMS40 + [l for r in recipes for l in r])):
        c = os.path.join(wd, f"L{lam:.6f}.dat")
        card(src, c, lam)
        cards[lam] = c
    prefetch([(f"{pre}_{k}", c, ps) for c in [sm] + list(cards.values()) for k in PIECES])
    for k in PIECES:
        MW[0.0], D[k][0.0] = medrv(f"{pre}_{k}", sm, ps)
    for lam, c in cards.items():
        for k in PIECES:
            MW[T(lam)], D[k][T(lam)] = medrv(f"{pre}_{k}", c, ps)
    ts = sorted(T(l) for l in LAMS40)
    m0 = mp.mpf(MW[0.0]) ** 2
    cm = lsq(ts, [(mp.mpf(MW[t]) ** 2 / m0 - 1) / t for t in ts], 2)
    a, b = cm[0], cm[1]
    print(f"u d~ > e+ ve at fixed points, every coefficient at one; W width {gw} GeV fixed")
    print(f"M_W0 = {mp.nstr(mp.sqrt(m0), 12)} GeV, M_W^2 = M_W0^2 (1 + a t + b t^2): a = {mp.nstr(a, 12)} TeV^2,"
          f" b = {mp.nstr(b, 12)} TeV^4 (a fitted cubic term {mp.nstr(cm[2], 2)})")
    for lam in (2000.0, 3000.0, 50000.0):
        if T(lam) in MW:
            print(f"   Lambda = {lam / 1000:g} TeV: M_W - M_W0 = {mp.nstr(MW[T(lam)] - mp.sqrt(m0), 6)} GeV")
    # M_W moved by the knob alone: NP=0 with every other coefficient off, and NP^2==1 with dimension
    # six on at a fixed scale, the knob chosen so that m runs through m0 on both sides
    lamk = 10000.0
    tk = T(lamk)
    c = os.path.join(wd, "kprobe.dat")
    card(src, c, lamk, 0.0, 0.0, {knob: 1e4})
    per = (mp.mpf(medrv(pre + "_np0", c, ps)[0]) ** 2 - m0) / 1e4
    c = os.path.join(wd, "k6.dat")
    card(src, c, lamk, 1.0, 0.0)
    dm6 = mp.mpf(medrv(pre + "_np1", c, ps)[0]) ** 2 - m0
    dms = [0.0] + [s * 2.0 ** j for j in range(-1, 8) for s in (1, -1)]
    jobs = []
    for dm in dms:
        c = os.path.join(wd, f"k0_{dm:g}.dat")
        card(src, c, lamk, 0.0, 0.0, {knob: float(dm / per)})
        jobs.append((pre + "_np0", c, ps))
        c = os.path.join(wd, f"k1_{dm:g}.dat")
        card(src, c, lamk, 1.0, 0.0, {knob: float((dm - dm6) / per)})
        jobs.append((pre + "_np1", c, ps))
    prefetch(jobs)
    K0, K1 = [], []
    for dm in dms:
        mw, me = medrv(pre + "_np0", os.path.join(wd, f"k0_{dm:g}.dat"), ps)
        K0.append((mp.mpf(mw) ** 2 - m0, me))
        mw, me = medrv(pre + "_np1", os.path.join(wd, f"k1_{dm:g}.dat"), ps)
        K1.append((mp.mpf(mw) ** 2 - m0, [x / tk for x in me]))
    print(f"knob {knob}: {mp.nstr(per, 4)} GeV^2 per unit at Lambda = 10 TeV; dimension six moves m by "
          f"{mp.nstr(dm6, 5)} GeV^2 there; scans |dm| <= 128 GeV^2")
    tms = [0.25, 0.1, 0.04, 0.016]
    rows = []
    for i in range(npt):
        s = labels[i][0] ** 2
        Rp = abs(mp.mpc(s - m0, mp.sqrt(m0) * gw))       # distance to the W pole in m
        dmax = [x for x in (128.0, 64.0, 32.0, 16.0, 8.0) if x <= 0.3 * Rp] or [4.0]
        full = [(D["full"][t][i] - D["full"][0.0][i]) / t for t in ts]
        c2f, c1f = coeff(ts, full, 1, tms), coeff(ts, full, 0, tms)
        y0 = [(D["np0"][t][i] - D["np0"][0.0][i]) / t for t in ts]
        A1, A2 = coeff(ts, y0, 0, tms), coeff(ts, y0, 1, tms)
        y1 = [D["np1"][t][i] / t for t in ts]
        S1, B1 = coeff(ts, y1, 0, tms), coeff(ts, y1, 1, tms)
        S2 = coeff(ts, [D["np2"][t][i] / t ** 2 for t in ts], 0, tms)
        x0, x1 = [x[0] for x in K0], [x[0] for x in K1]
        S0p, S0pp = coeff(x0, [x[1][i] for x in K0], 1, dmax, 7), coeff(x0, [x[1][i] for x in K0], 2, dmax, 7)
        S1p = coeff(x1, [x[1][i] for x in K1], 1, dmax, 7)
        # NP=0 and NP^2==1/t depend on the coefficients and on t only through m: the knob scans,
        # evaluated at the m of each scale, must give the Lambda scans
        sel0 = [(x, y[i]) for x, y in K0 if abs(x) <= S0p[2]]
        p0 = lsq([x for x, _ in sel0], [y for _, y in sel0], 6)
        sel1 = [(x, y[i]) for x, y in K1 if abs(x) <= S1p[2]]
        p1 = lsq([x for x, _ in sel1], [y for _, y in sel1], 6)
        dev0 = dev1 = mp.mpf(0)
        for t in ts:
            dm = mp.mpf(MW[t]) ** 2 - m0
            if abs(dm) <= S0p[2]:
                dev0 = max(dev0, abs(sum(p0[k] * dm ** k for k in range(7)) / D["np0"][t][i] - 1))
            if abs(dm) <= S1p[2]:
                dev1 = max(dev1, abs(sum(p1[k] * dm ** k for k in range(7)) / (D["np1"][t][i] / t) - 1))
        tB1, tb, taa = a * m0 * S1p[0], b * m0 * S0p[0], (a * m0) ** 2 * S0pp[0]   # S0pp is S0''/2
        predA, predB = S2[0] + A2[0] + B1[0], S2[0] + tB1 + tb + taa
        eA = S2[1] + A2[1] + B1[1]
        eB = abs(S2[1]) + abs(a * m0 * S1p[1]) + abs(b * m0 * S0p[1]) + abs((a * m0) ** 2 * S0pp[1])
        rec = []
        for recipe in recipes:
            tr = [T(l) for l in recipe]
            X = [(D["np0"][t][i] - D["np0"][0.0][i] + D["np1"][t][i]) / t for t in tr]
            rec.append((lsq(tr, X, len(tr) - 1)[1], lsq(tr[-2:], X[-2:], 1)[1]))
        rows.append(dict(lab=labels[i], c2=c2f, A=predA, eA=eA, B=predB, eB=eB, S2=S2[0], tB1=tB1, tb=tb, taa=taa,
                         c1=c1f, c1p=S1[0] + A1[0], x2=A2[0] + B1[0], rec=rec, dev0=dev0, dev1=dev1))
    rel = lambda x, y: mp.nstr((x - y) / y, 2)
    lab = lambda r: f"{r['lab'][0]:g} {r['lab'][1]:g}"
    print("\nc2 is the t^2 coefficient of |M|^2 (t in TeV^-2), at each phase-space point (sqrt s [GeV], cos theta)")
    print(f"{'point':>12s} {'c2 full fit':>19s} {'err':>7s} | {'(A) pieces':>19s} {'A-full':>8s} {'err':>7s} |"
          f" {'(B) terms':>19s} {'B-full':>8s} {'err':>7s}")
    for r in rows:
        c2, e2 = r["c2"][0], r["c2"][1]
        print(f"{lab(r):>12s} {mp.nstr(c2, 13):>19s} {mp.nstr(e2 / abs(c2), 1):>7s} | {mp.nstr(r['A'], 13):>19s}"
              f" {rel(r['A'], c2):>8s} {mp.nstr(r['eA'] / abs(c2), 1):>7s} | {mp.nstr(r['B'], 13):>19s}"
              f" {rel(r['B'], c2):>8s} {mp.nstr(r['eB'] / abs(c2), 1):>7s}")
    print("\nthe terms of (B), each over c2, and what (B) misses without the NP^2==1 term or the a^2 term")
    print(f"{'point':>12s} {'S2':>10s} {'a m0 S1p':>10s} {'b m0 S0p':>10s} {'a2m0^2S0pp/2':>12s} | {'miss no S1p':>11s} {'miss no a2':>11s}")
    for r in rows:
        c2 = r["c2"][0]
        print(f"{lab(r):>12s} {mp.nstr(r['S2'] / c2, 4):>10s} {mp.nstr(r['tB1'] / c2, 4):>10s} "
              f"{mp.nstr(r['tb'] / c2, 4):>10s} {mp.nstr(r['taa'] / c2, 4):>12s} | "
              f"{mp.nstr(-r['tB1'] / c2, 3):>11s} {mp.nstr(-r['taa'] / c2, 3):>11s}")
    print("\nNP=0 and NP^2==1/t at every scale against the knob scans at the same M_W (largest relative deviation)")
    for r in rows:
        print(f"{lab(r):>12s} NP=0 {mp.nstr(r['dev0'], 2):>9s}   NP^2==1 {mp.nstr(r['dev1'], 2):>9s}")
    print("\nt^1 coefficient: full fit against NP^2==1 plus the linear part of NP=0")
    for r in rows:
        print(f"{lab(r):>12s} {mp.nstr(r['c1'][0], 13):>19s} {mp.nstr(r['c1p'], 13):>19s} {rel(r['c1p'], r['c1'][0]):>8s}")
    for j, recipe in enumerate(recipes):
        print(f"\nthe recipe with the scales {[l / 1000 for l in recipe]} TeV: x2 against the exact one, and the share"
              f" of the t^2 term it gets wrong (x2 error over c2)")
        for r in rows:
            x3, x2s = r["rec"][j]
            print(f"{lab(r):>12s} x2 exact {mp.nstr(r['x2'], 8):>15s}  {len(recipe)} scales {rel(x3, r['x2']):>8s}"
                  f" ({mp.nstr((x3 - r['x2']) / r['c2'][0], 2)} of c2)   2 scales {rel(x2s, r['x2']):>8s}"
                  f" ({mp.nstr((x2s - r['x2']) / r['c2'][0], 2)} of c2)")
        share = lambda r: abs((r["rec"][j][0] - r["x2"]) / r["c2"][0])
        far = [r for r in rows if abs(r["lab"][0] - mp.sqrt(m0)) > gw]
        print(f"   largest share of c2: {mp.nstr(max(share(r) for r in rows), 2)} at any point, "
              f"{mp.nstr(max(share(r) for r in far), 2)} more than a width from the pole")
    print()
    worst = lambda f: max(f(r) for r in rows)
    check("points: (A) the pieces fitted in t give c2", worst(lambda r: abs((r["A"] - r["c2"][0]) / r["c2"][0])) < 1e-6,
          f"largest |A - c2| / |c2| = {mp.nstr(worst(lambda r: abs((r['A'] - r['c2'][0]) / r['c2'][0])), 2)}")
    check("points: (B) the expansion term by term gives c2", worst(lambda r: abs((r["B"] - r["c2"][0]) / r["c2"][0])) < 1e-6,
          f"largest |B - c2| / |c2| = {mp.nstr(worst(lambda r: abs((r['B'] - r['c2'][0]) / r['c2'][0])), 2)}")
    check("points: NP=0 and NP^2==1 depend on the coefficients through M_W alone", worst(lambda r: max(r["dev0"], r["dev1"])) < 1e-4,
          f"largest deviation from the scans of M_W {mp.nstr(worst(lambda r: max(r['dev0'], r['dev1'])), 2)}")
    check("points: the t coefficient is NP^2==1 plus the linear part of NP=0",
          worst(lambda r: abs((r["c1p"] - r["c1"][0]) / r["c1"][0])) < 1e-9,
          f"largest relative difference {mp.nstr(worst(lambda r: abs((r['c1p'] - r['c1'][0]) / r['c1'][0])), 2)}")


# ---------------------------------------------------------------- udx

def sm_sample(lo, hi, nev, seed):
    """A Standard-Model sample of u d~ > e+ ve at 13.6 TeV with lo < m(e+ ve) < hi (hi None: no upper
    cut), every coefficient off, from the MadEvent directory NP0REF_DIR/xs/udx_ev (no NP^2
    selection).  Returns its LHE file."""
    d = os.path.join(R, "xs", "udx_ev")
    os.makedirs(os.path.dirname(d), exist_ok=True)
    if not os.path.exists(os.path.join(d, "bin", "generate_events")):
        mg5(f"import model {MODEL}\ngenerate {UDX} NP<=4\noutput {d} -f\n", d + "_gen.log")
        if not os.path.exists(os.path.join(d, "bin", "generate_events")):
            sys.exit(f"no output {d}, see {d}_gen.log")
        cores(d)
    rn = f"sm_m{lo:g}_{'inf' if hi is None else f'{hi:g}'}_s{seed}_n{nev}"
    lhe = os.path.join(d, "Events", rn, "unweighted_events.lhe.gz")
    if not os.path.exists(lhe):
        log = d + ".log"
        if N.run([PY, SET_CARDS, d, f"nevents={nev}", f"iseed={seed}", f"mmnl={lo:g}",
                  f"mmnlmax={-1 if hi is None else f'{hi:g}'}"] + COMMON + N._settings(d, False, 3000.0), log):
            sys.exit(f"card error, see {log}")
        N._clear_channels(d)                 # so that the sample depends on its cards and seed alone
        N.run([os.path.join(d, "bin", "generate_events"), "-f", rn], log)
        if not os.path.exists(lhe):
            sys.exit(f"no events in {lhe}, see {log}")
    return lhe


def read_lhe(path):
    """The cross section of an LHE file and the momenta (E, px, py, pz) of u, d~, e+, ve of each event."""
    txt = gzip.open(path, "rt").read()
    init = re.search(r"<init>\n(.*?)</init>", txt, re.S).group(1).strip().split("\n")
    nproc = int(init[0].split()[-1])
    sig = sum(float(l.split()[0]) for l in init[1:1 + nproc])
    ev = []
    for blk in re.findall(r"<event>\n(.*?)</event>", txt, re.S):
        lines = [l for l in blk.strip().split("\n") if l.strip() and not l.lstrip().startswith("<")]
        n = int(lines[0].split()[0])
        parts = [l.split() for l in lines[1:1 + n]]
        inc = [p for p in parts if p[1] == "-1"]
        out = {p[0]: p for p in parts if p[1] == "1"}
        mom = lambda p: (float(p[9]), float(p[6]), float(p[7]), float(p[8]))
        a, b = inc
        if a[0] == "-1":                      # the mirror configuration: d~ from the first beam
            a, b = b, a
        assert a[0] == "2" and b[0] == "-1", (a[0], b[0])
        ev.append([mom(a), mom(b), mom(out["-11"]), mom(out["12"])])
    return sig, ev


def cmd_udx(argv):
    import numpy as np
    import mpmath as mp
    mmin = float(opt(argv, "--mmin", "100"))
    nev, seed = int(opt(argv, "--nev", "40000")), int(opt(argv, "--seed", "21"))
    edges = [mmin] + [float(x) for x in opt(argv, "--slices", "300,600,1000,1500,2000,2500,3000,4000,5500").split(",") if x] + [None]
    recipes = [[float(x) for x in r.split(",")] for r in
               opt(argv, "--recipe", "2000,3000,4000/3000,4000,6000/4000,6000,8000").split("/")]
    lref = float(opt(argv, "--lam", "3000"))
    nb = 20
    pre = standalone()
    # A sample of the SM in each slice of m(e+ ve), with as many events in the last as in the first.
    # The terms that grow with the energy live in the tail, where one sample of the SM has almost
    # no event: of 200000 events with m > 100 GeV, 32 lie above 1 TeV and none above 2.4 TeV.
    sig, ev, slices = 0.0, [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        s, e = read_lhe(sm_sample(lo, hi, nev, seed))
        slices.append((s, np.array_split(np.arange(len(ev), len(ev) + len(e)), nb)))
        sig += s
        ev += e
    n = len(ev)
    wd = os.path.join(R, "xs", f"rw_udx_m{mmin:g}")
    os.makedirs(wd, exist_ok=True)
    ps = os.path.join(wd, "events.txt")
    with open(ps, "w") as f:
        f.write(f"{n}\n")
        for p in ev:
            for v in p:
                f.write(" ".join(f"{x:.15e}" for x in v) + "\n")
    src = os.path.join(pre + "_full", "Cards", "param_card.dat")
    lams = sorted(set(LAMS40 + [l for r in recipes for l in r] + [lref]))
    sm = os.path.join(wd, "sm.dat")
    card(src, sm, 3000.0, 0.0, 0.0)
    cards = {0.0: sm}
    for lam in lams:
        c = os.path.join(wd, f"L{lam:.6f}.dat")
        card(src, c, lam)
        cards[T(lam)] = c
    prefetch([(f"{pre}_{k}", c, ps) for c in cards.values() for k in PIECES])
    ME, MW = {}, {}
    for t, c in cards.items():
        for k in PIECES:
            MW[t], ME[(k, t)] = medrv(f"{pre}_{k}", c, ps)
    ref = np.array(ME[("full", 0.0)])
    ok_sm = np.allclose(np.array(ME[("np0", 0.0)]), ref, rtol=1e-12, atol=0)
    # sigma for each card on all events and per batch of events: the batches give the errors of
    # anything computed from the cross sections, since each estimator below is applied to each batch.
    # A batch holds a twentieth of every slice, and a cross section is the sum over the slices of the
    # slice's SM cross section times the mean ratio of the matrix elements on its events.
    ratio = {key: np.array(v) / ref for key, v in ME.items()}
    S = {key: np.array([sum(s * np.mean(r[bs[j]]) for s, bs in slices) for j in range(nb)]) for key, r in ratio.items()}
    tot = {key: sum(s * np.mean(r[np.concatenate(bs)]) for s, bs in slices) for key, r in ratio.items()}
    ts = sorted(T(l) for l in LAMS40)
    m0 = mp.mpf(MW[0.0]) ** 2
    cm = lsq(ts, [(mp.mpf(MW[t]) ** 2 / m0 - 1) / t for t in ts], 2)
    tr = T(lref)
    print(f"u d~ > e+ ve, pp at 13.6 TeV, m(e+ ve) > {mmin:g} GeV, {n} events of the SM in {len(slices)} slices of m "
          f"(edges {', '.join(f'{x:g}' for x in edges[:-1])} GeV), sigma_SM = {sig:.6g} pb "
          f"(MadEvent), every coefficient at one; M_W0 = {mp.nstr(mp.sqrt(m0), 8)} GeV, a = {mp.nstr(cm[0], 8)} TeV^2, "
          f"b = {mp.nstr(cm[1], 8)} TeV^4")
    print(f"at Lambda = {lref / 1000:g} TeV: M_W - M_W0 = {mp.nstr(MW[tr] - mp.sqrt(m0), 6)} GeV")
    # where NP^2==2 lives: a last slice that carries much of it, or with a large error, asks for more slices
    print("NP^2==2 at Lambda in each slice of m [pb]: " + ", ".join(
        f"{lo:g}-{'' if hi is None else f'{hi:g}'} {x * np.mean(ratio[('np2', tr)][np.concatenate(bs)]):.4g} +- "
        f"{x * np.std([np.mean(ratio[('np2', tr)][c]) for c in bs], ddof=1) / np.sqrt(nb):.2g}"
        for (lo, hi), (x, bs) in zip(zip(edges[:-1], edges[1:]), slices)))
    batches = [{key: S[key][j] for key in S} for j in range(nb)]

    def estimate(get):
        """the estimator on all events, and its error from the batches"""
        vb = [get(Db) for Db in batches]
        return get(tot), float(np.std(np.array(vb, dtype=float), ddof=1) / np.sqrt(nb))
    memo = {}

    def cached(f):
        def g(Dd, *a):
            k = (f.__name__, id(Dd), a)
            if k not in memo:
                memo[k] = f(Dd, *a)
            return memo[k]
        return g
    tms = [0.25, 0.1, 0.04, 0.016]

    @cached
    def c2_full(Dd):
        return float(coeff(ts, [(Dd[("full", t)] - Dd[("full", 0.0)]) / t for t in ts], 1, tms)[0])

    @cached
    def c1_full(Dd):
        return float(coeff(ts, [(Dd[("full", t)] - Dd[("full", 0.0)]) / t for t in ts], 0, tms)[0])

    @cached
    def piece(Dd, k, j, off):
        y = [(Dd[(k, t)] - (Dd[(k, 0.0)] if off else 0.0)) / t ** (2 if k == "np2" else 1) for t in ts]
        return float(coeff(ts, y, j, tms)[0])

    def recipe_x(Dd, scales, j):
        trs = [T(l) for l in scales]
        X = [(Dd[("np0", t)] - Dd[("np0", 0.0)] + Dd[("np1", t)]) / t for t in trs]
        return float(lsq(trs, X, len(trs) - 1)[j])

    def s2_ext(Dd, scales):
        trs = [T(l) for l in scales]
        return float(lsq(trs, [Dd[("np2", t)] / t ** 2 for t in trs], len(trs) - 1)[0])
    quant = {
        "t^2 term": lambda Dd: c2_full(Dd) * tr ** 2,
        "NP^2==2": lambda Dd: Dd[("np2", tr)],
        "NP^2==2 at M_W0": lambda Dd: piece(Dd, "np2", 0, False) * tr ** 2,
        "shift t^2": lambda Dd: (c2_full(Dd) - piece(Dd, "np2", 0, False)) * tr ** 2,
        "x1 t": lambda Dd: c1_full(Dd) * tr,
        "NP^2==1": lambda Dd: Dd[("np1", tr)],
        "NP^2==1 at M_W0": lambda Dd: piece(Dd, "np1", 0, False) * tr,
    }
    rows = [
        ("t^2 term of the full cross section (fit over 2-50 TeV)", quant["t^2 term"]),
        ("NP^2==2 at Lambda, shifted mass", quant["NP^2==2"]),
        ("NP^2==2 at M_W0 (S2 t^2, fit)", quant["NP^2==2 at M_W0"]),
        ("x2 t^2 exact: NP=0 part (fit)", lambda Dd: piece(Dd, "np0", 1, True) * tr ** 2),
        ("x2 t^2 exact: NP^2==1 part (fit)", lambda Dd: piece(Dd, "np1", 1, False) * tr ** 2),
        ("the shift: full t^2 term minus NP^2==2 at M_W0", quant["shift t^2"]),
        ("tags alone (NP^2==2 at Lambda) minus the full t^2 term", lambda Dd: Dd[("np2", tr)] - c2_full(Dd) * tr ** 2),
        ("the pieces (NP^2==2 at M_W0 + both x2 parts) minus the full t^2 term",
         lambda Dd: (piece(Dd, "np2", 0, False) + piece(Dd, "np0", 1, True) + piece(Dd, "np1", 1, False) - c2_full(Dd)) * tr ** 2),
        ("t^1 term of the full cross section (fit)", quant["x1 t"]),
        ("NP^2==1 at Lambda", quant["NP^2==1"]),
        ("NP^2==1 at M_W0 (S1 t, fit)", quant["NP^2==1 at M_W0"]),
        ("tags alone at 1/Lambda^2 (NP^2==1 at Lambda) minus the full t^1 term", lambda Dd: Dd[("np1", tr)] - c1_full(Dd) * tr),
    ]
    for recipe in recipes:
        nm = "/".join(f"{l / 1000:g}" for l in recipe)
        rows += [
            (f"[{nm} TeV] recipe x2 t^2", lambda Dd, r=recipe: recipe_x(Dd, r, 1) * tr ** 2),
            (f"[{nm} TeV] recipe total: NP^2==2 at Lambda + x2 t^2", lambda Dd, r=recipe: Dd[("np2", tr)] + recipe_x(Dd, r, 1) * tr ** 2),
            (f"[{nm} TeV] recipe total at M_W0: S2 t^2 (scales) + x2 t^2", lambda Dd, r=recipe: (s2_ext(Dd, r) + recipe_x(Dd, r, 1)) * tr ** 2),
            (f"[{nm} TeV] recipe total at M_W0 minus the full t^2 term", lambda Dd, r=recipe: (s2_ext(Dd, r) + recipe_x(Dd, r, 1) - c2_full(Dd)) * tr ** 2),
            (f"[{nm} TeV] recipe x1 t", lambda Dd, r=recipe: recipe_x(Dd, r, 0) * tr),
            (f"[{nm} TeV] recipe x1 t minus the full t^1 term", lambda Dd, r=recipe: (recipe_x(Dd, r, 0) - c1_full(Dd)) * tr),
        ]
    print(f"\n[pb] at Lambda = {lref / 1000:g} TeV, errors from {nb} batches of the events")
    val = {}
    for name, f in rows:
        val[name] = estimate(f)
        print(f"  {name:<70s} {val[name][0]:+.6g} +- {val[name][1]:.2g}")
    print()
    c1v, c2v = val["t^1 term of the full cross section (fit)"][0], val["t^2 term of the full cross section (fit over 2-50 TeV)"][0]
    check("udx: NP=0 and the full matrix element agree with the coefficients off", ok_sm)
    pm = val["the pieces (NP^2==2 at M_W0 + both x2 parts) minus the full t^2 term"][0]
    check("udx: the pieces add up to the full t^2 term", abs(pm) < 1e-6 * abs(c2v), f"{pm:+.2g} pb against {c2v:+.4g} pb")
    for recipe in recipes:
        nm = "/".join(f"{l / 1000:g}" for l in recipe)
        d1 = val[f"[{nm} TeV] recipe x1 t minus the full t^1 term"][0]
        check(f"udx: the recipe's x1 t at {nm} TeV is the full t term", abs(d1) < 1e-3 * abs(c1v),
              f"{d1:+.2g} pb against {c1v:+.4g} pb")
    nm = "/".join(f"{l / 1000:g}" for l in recipes[0])
    d2 = val[f"[{nm} TeV] recipe total at M_W0 minus the full t^2 term"][0]
    check(f"udx: the recipe's t^2 term at {nm} TeV is the full one to two per cent", abs(d2) < 0.02 * abs(c2v),
          f"{d2:+.2g} pb, {100 * d2 / c2v:+.2g} per cent of {c2v:+.4g} pb")
    ref_put(f"udx_m{mmin:g}", [(q, *estimate(f)) for q, f in quant.items()],
            f"np0_fixed_order.py udx, {n} events in {len(slices)} slices of m, seed {seed}")


# ---------------------------------------------------------------- ww

def xsrun(d, out, seed, nev, lams):
    """The cross section of the process directory d with every coefficient of both sectors at one at
    each scale of lams (0: every coefficient off), one row each in out.  A run already in out is not
    made again, and every run starts without the channel directories of the run before, as the runs
    of np0_shift.py do."""
    log = d.rstrip("/") + ".log"
    if not os.path.exists(out):
        open(out, "w").write("dir\tlam\tsigma_pb\terror_pb\tnevents\tseed\n")
    done = {(r[0], r[1], r[4], r[5]) for r in (l.split("\t") for l in open(out).read().split("\n")[1:] if l)}
    for lam in lams:
        key = (os.path.basename(d), f"{lam:g}", str(nev), str(seed))
        if key in done:
            continue
        if N.run([PY, SET_CARDS, d, f"nevents={nev}", f"iseed={seed}"] + COMMON + N._settings(d, lam > 0, lam or 3000.0), log):
            check(f"ww: cards of {key[0]} at {lam:g}", False, f"see {log}")
            continue
        N._clear_channels(d)                 # so that the scales of a seed differ by the card alone
        before = os.path.getsize(log)
        N.run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
        r = N._xsec(d, open(log, errors="replace").read()[before:])
        if r is None:
            check(f"ww: a cross section of {key[0]} at {lam:g}", False, f"see {log}")
            continue
        with open(out, "a") as fh:
            fh.write(f"{key[0]}\t{lam:g}\t{r[0]:.10g}\t{r[1]:.6g}\t{nev}\t{seed}\n")
        print(f"  {key[0]} Lambda = {lam:g}: {r[0]:.8g} +- {r[1]:.3g} pb", flush=True)


def full_ww(seeds, nev, pieces):
    """The full p p > w+ w- (no NP^2 selection) at the scales LAMS_WW, one copy of the process
    directory per seed, or (pieces) NP^2==3 and NP^2==4 at 3 TeV with the first seed."""
    xs = os.path.join(R, "xs")
    os.makedirs(xs, exist_ok=True)
    outs = {"ww_full": "NP<=4", "ww_np3": "NP<=4 NP^2==3", "ww_np4": "NP<=4 NP^2==4"}
    new = [k for k in outs if not os.path.exists(os.path.join(xs, k, "bin", "generate_events"))]
    if new:
        mg5(f"import model {MODEL}\n" + "".join(f"generate {WW} {outs[k]}\noutput {os.path.join(xs, k)} -f\n" for k in new),
            os.path.join(xs, "ww_gen.log"))
        for k in new:
            if not os.path.exists(os.path.join(xs, k, "bin", "generate_events")):
                sys.exit(f"no output {os.path.join(xs, k)}, see {os.path.join(xs, 'ww_gen.log')}")
            cores(os.path.join(xs, k))
    if pieces:
        for k in ("ww_np3", "ww_np4"):
            xsrun(os.path.join(xs, k), os.path.join(xs, "ww_pieces.tsv"), seeds[0], nev, [3000.0])
        return
    for s in seeds:
        d = os.path.join(xs, f"ww_full_s{s}")
        if not os.path.exists(d):
            subprocess.run(["cp", "-a", os.path.join(xs, "ww_full"), d], check=True)
        xsrun(d, os.path.join(xs, f"ww_full_s{s}.tsv"), s, nev, LAMS_WW)


def recipe_rows(tsv, lams, lam, nev, line):
    """For each complete seed of a results file of np0_shift.py, with every coefficient at one: x1 t
    and x2 t^2 and their NP^2==1 parts, NP^2==1 and NP^2==2 at lam, NP^2==2 at M_W0 from its runs at
    the scales, the NP=0 shifts at the scales, and the rounding of x1 t and x2 t^2 (see half_ulp).
    Only the runs of nev events with the extra settings of the processes.txt line are used, and rows
    whose settings are unknown are counted and left out, as np0_shift.py itself does."""
    rows = N._rows_c(tsv)
    pids = {r[8] for r in rows}
    if pids != {N.ALL_ONE}:
        sys.exit(f"{tsv}: rows of {sorted(pids)}, and the reference is every coefficient at one")
    unknown = sum(1 for r in rows if r[7] == N.UNKNOWN)
    if unknown:
        print(f"UNKNOWN SETTINGS {os.path.basename(tsv)}: {unknown} rows written before the run settings were "
              "recorded are left out")
    by = {}
    for r in rows:
        if r[5] == str(nev) and r[7] == N._extras(line):
            by.setdefault(r[6], {})[(r[1], float(r[2]))] = (float(r[3]), float(r[4]), half_ulp(r[3]))
    sc = sorted(lams, reverse=True)
    ts = [T(l) for l in sc]
    tr, deg = T(lam), min(len(ts) - 1, 2)
    W = N._poly_weights(ts, deg)
    out = {}
    for seed, Rr in sorted(by.items()):
        miss = [w for k, w in N._required(sc, lam) if k not in Rr]
        if miss:
            print(f"INCOMPLETE {os.path.basename(tsv)} seed {seed}: no {', '.join(miss)}")
            continue
        sm = Rr[("np0", 0.0)]
        s0, s1 = [Rr[("np0", l)] for l in sc], [Rr[("np1", l)] for l in sc]
        x = N._solve(ts, [v[:2] for v in s0], [v[:2] for v in s1], sm[:2], deg)

        def floor(k):
            """how far x_k t^(k+1) can move when every cross section moves within its last digit"""
            return (sum(abs(W[k][i]) / ts[i] * (s0[i][2] + s1[i][2]) for i in range(len(ts)))
                    + sm[2] * abs(sum(W[k][i] / ts[i] for i in range(len(ts))))) * tr ** (k + 1)
        s2 = [Rr.get(("np2", l)) for l in sc]
        n1 = Rr.get(("np1", lam), (float("nan"), 0.0, 0.0))
        out[seed] = dict(
            x1=x[0][0] * tr, x1e=x[0][1] * tr, x1_np1=x[0][4] * tr, x2=x[1][0] * tr ** 2, x2e=x[1][1] * tr ** 2,
            f1=floor(0) + n1[2], f2=floor(1), np1=n1[0], np2=Rr[("np2", lam)][0],
            s2=(sum(W[0][i] * s2[i][0] / ts[i] ** 2 for i in range(len(ts))) * tr ** 2 if all(s2) else float("nan")),
            d0=[(l, Rr[("np0", l)][0] - sm[0], (Rr[("np0", l)][1] ** 2 + sm[1] ** 2) ** 0.5) for l in sc])
    return out


def half_ulp(s):
    """Half a unit in the last digit of a number as written, the precision of a recorded cross section."""
    m = re.match(r"^[-+]?\d*(?:\.(\d*))?(?:[eE]([-+]?\d+))?$", s.strip())
    return 0.5 * 10.0 ** (int(m.group(2) or 0) - len(m.group(1) or ""))


def cmd_ww(argv):
    import numpy as np
    seeds = [int(x) for x in opt(argv, "--seeds", "21,22,23").split(",")]
    nev = int(opt(argv, "--nev", "20000"))
    lams_s, lam = opt(argv, "--lams", "2000,3000,4000"), float(opt(argv, "--lam", "3000"))
    lams = [float(x) for x in lams_s.split(",")]
    part = opt(argv, "--part", "all")
    # the seeds of the recipe that enter its means: those of the full runs, or more of them
    rseeds = [int(x) for x in opt(argv, "--recipe-seeds", ",".join(map(str, seeds))).split(",")]
    st = study_dir("ww", WW)
    if part in ("recipe", "all"):
        for s in sorted(set(seeds + rseeds), key=(seeds + rseeds).index):
            rc = np0(MODEL, st, s, nev, lams_s, lam)
            if rc:                               # a run that failed, or a seed left incomplete
                check(f"ww: np0_shift.py on seed {s}", False, f"returned {rc}")
    if part in ("full", "all"):
        full_ww(seeds, nev, False)
    if part in ("pieces", "all"):
        full_ww(seeds, nev, True)
    if part not in ("fit", "all"):
        return
    tr = T(lam)
    if not os.path.exists(N._out_c(st)):
        check("ww: the recipe's runs", False, f"no {N._out_c(st)}, run --part recipe")
        return
    rec = recipe_rows(N._out_c(st), lams, lam, nev, WW)
    xs = os.path.join(R, "xs")
    hi = {}
    pf = os.path.join(xs, "ww_pieces.tsv")
    for r in (l.split("\t") for l in (open(pf).read().split("\n")[1:] if os.path.exists(pf) else []) if l):
        if int(r[4]) == nev and int(r[5]) == seeds[0]:
            hi[int(r[0][-1])] = (float(r[2]), T(float(r[1])))       # ww_np3, ww_np4
    res = {}
    for s in seeds:
        F = {}
        f = os.path.join(xs, f"ww_full_s{s}.tsv")
        for r in (l.split("\t") for l in (open(f).read().split("\n")[1:] if os.path.exists(f) else []) if l):
            if int(r[4]) == nev and int(r[5]) == s:
                F[float(r[1])] = (float(r[2]), float(r[3]))
        if str(s) not in rec or sorted(F) != sorted(LAMS_WW) or sorted(hi) != [3, 4]:
            check(f"ww: seed {s} has its recipe, its full runs and the NP^2==3 and NP^2==4 pieces", False)
            continue
        ls = [l for l in LAMS_WW if l > 0]
        ts = [T(l) for l in ls]
        # NP^2==3 and NP^2==4 taken out as t^3 and t^4, then c1 t + c2 t^2 by weighted least squares
        ys = [F[l][0] - F[0.0][0] - sum(v * (t / t0) ** k for k, (v, t0) in hi.items()) for l, t in zip(ls, ts)]
        es = [(F[l][1] ** 2 + F[0.0][1] ** 2) ** 0.5 for l in ls]
        fit = {}
        for deg in (2, 3):
            A = np.array([[t ** k for k in range(1, deg + 1)] for t in ts])
            Wm = np.diag(1 / np.array(es) ** 2)
            cov = np.linalg.inv(A.T @ Wm @ A)
            c = cov @ A.T @ Wm @ np.array(ys)
            chi2 = float(sum(((y - sum(c[k - 1] * t ** k for k in range(1, deg + 1))) / e) ** 2 for t, y, e in zip(ts, ys, es)))
            fit[deg] = (c[0] * tr, c[1] * tr ** 2, cov[1, 1] ** 0.5 * tr ** 2, chi2, len(ts) - deg)
        v = rec[str(s)]
        res[s] = dict(c1=fit[2][0], c2=fit[2][1], shift=fit[2][1] - v["s2"], x1=v["x1"], x1_np1=v["x1_np1"], x2=v["x2"],
                      np1=v["np1"], np2=v["np2"], s2=v["s2"], rec=v["np2"] + v["x2"], rec0=v["s2"] + v["x2"])
        print(f"seed {s}: recipe x1 t = {v['x1']:+.4f} (NP^2==1 part {v['x1_np1']:+.4f}), NP^2==1 = {v['np1']:+.4f}, "
              f"x2 t^2 = {v['x2']:+.4f}, NP^2==2 = {v['np2']:+.4f}, NP^2==2 at M_W0 = {v['s2']:+.4f}")
        for deg, (c1, c2, e2, chi2, ndf) in fit.items():
            print(f"    full fit, NP^2==3 and NP^2==4 taken out, degree {deg}: c1 t = {c1:+.4f}, c2 t^2 = {c2:+.4f} "
                  f"+- {e2:.3f}, chi2 {chi2:.1f}/{ndf}")
    if len(res) < 2:
        check("ww: two complete seeds at least", False)
        return
    names = {"x1": "recipe x1 t", "np1": "NP^2==1 alone", "x1_np1": "NP^2==1 part of x1 t", "c1": "full fit c1 t",
             "x2": "recipe x2 t^2", "np2": "NP^2==2 alone", "s2": "NP^2==2 at M_W0", "rec": "recipe NP^2==2 + x2 t^2",
             "rec0": "recipe at M_W0", "c2": "full fit c2 t^2", "shift": "full fit c2 t^2 - NP^2==2 at M_W0"}
    # the rows of the recipe alone, over the seeds of --recipe-seeds, which need no full run
    rall = {}
    for s in rseeds:
        if str(s) not in rec:
            check(f"ww: seed {s} of the recipe is complete", False)
            continue
        v = rec[str(s)]
        rall[s] = dict(x1=v["x1"], x1_np1=v["x1_np1"], x2=v["x2"], np1=v["np1"], np2=v["np2"], s2=v["s2"],
                       rec=v["np2"] + v["x2"], rec0=v["s2"] + v["x2"])
    if len(rall) < 2:
        check("ww: two complete seeds of the recipe at least", False)
        return
    src = lambda k: res if k in ("c1", "c2", "shift") else rall
    M = {k: mean_err([r[k] for r in src(k).values()]) for k in names}
    print(f"\nthe mean and its error from the spread of the seeds [pb, Lambda = {lam / 1000:g} TeV]: the full fit over "
          f"{len(res)} seeds, the recipe over {len(rall)}")
    for k, nm in names.items():
        print(f"  {nm:<36s} {M[k][0]:+.4f} +- {M[k][1]:.4f}   ({' '.join(f'{r[k]:+.4f}' for r in src(k).values())})")
    dx1 = mean_err([r["x1"] - r["c1"] for r in res.values()])
    dx2 = mean_err([r["rec0"] - r["c2"] for r in res.values()])
    print()
    check("ww: the recipe's x1 t is the full fit's c1 t", abs(dx1[0]) <= 3 * dx1[1], f"difference {dx1[0]:+.3f} +- {dx1[1]:.3f} pb")
    check("ww: the recipe's t^2 term at M_W0 is the full fit's c2 t^2", abs(dx2[0]) <= 3 * dx2[1],
          f"difference {dx2[0]:+.3f} +- {dx2[1]:.3f} pb")
    ref_put("ww", [("x1 t", *M["c1"]), ("t^2 term", *M["c2"]), ("shift t^2", *M["shift"]), ("NP^2==1", *M["np1"]),
                   ("NP^2==2", *M["np2"]), ("NP^2==1 at M_W0", *M["x1_np1"]), ("NP^2==2 at M_W0", *M["s2"]),
                   ("x1 t recipe", *M["x1"]), ("x2 t^2 recipe", *M["x2"]), ("t^2 term recipe", *M["rec"])],
            f"np0_fixed_order.py ww, seeds {','.join(map(str, res))}"
            + ("" if list(rall) == list(res) else f" (recipe rows: seeds {','.join(map(str, rall))})") + f", {nev} events a run")


# ---------------------------------------------------------------- controls

def mw_value(model, settings):
    """M_W of a UFO at the settings, from validate/eval_ufo_params.py."""
    o = subprocess.run([PY, os.path.join(ROOT, "validate", "eval_ufo_params.py"), model] + settings.split() + ["--show=MW"],
                       capture_output=True, text=True)
    m = re.search(r"^MW\s*=\s*([-\d.eE+]+)", o.stdout, re.M)
    if not m:                                    # as np0_shift.mw_of: no number for a mass that failed
        sys.exit(f"validate/eval_ufo_params.py gave no M_W for {model} at \"{settings}\" (it returned "
                 f"{o.returncode}):\n" + ((o.stderr or o.stdout).strip()[-2000:] or "no output"))
    return float(m.group(1))


def all_on(model, lam):
    """Every coefficient of both sectors of the UFO at one and Lambda at lam, as eval_ufo_params.py takes it."""
    six = N._names_of(os.path.join(model, "param_card_template.dat")).get("DIM6", [])
    return "dim8_all=1 " + " ".join(f"{n}=1" for n in six if not n.endswith("Ph")) + f" Lam={lam:g}"


def freeze(model):
    """A copy of the model under NP0REF_DIR/models whose W mass is frozen at its value with every
    coefficient at zero: in parameters.py MW = sqrt((1 + MW21 + MW22) MW2SM) becomes sqrt(MW2SM), and
    every parameter that derives from MW follows.  The copy is checked: with every coefficient at one
    at 2 TeV its M_W is that of the model with every coefficient at zero, which the model's own is not."""
    dst = os.path.join(R, "models", os.path.basename(model) + "_mwfrozen")
    if not os.path.exists(os.path.join(dst, "parameters.py")):
        tmp = dst + ".tmp"
        shutil.rmtree(tmp, ignore_errors=True)
        shutil.copytree(model, tmp, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pkl"))
        p = os.path.join(tmp, "parameters.py")
        new, n = re.subn(r"(MW = Parameter\(name = 'MW',\s+nature = 'internal',\s+type = 'real',\s+value = ')"
                         r"cmath\.sqrt\(\(1 \+ MW21 \+ MW22\)\*MW2SM\)(')", r"\1cmath.sqrt(MW2SM)\2", open(p).read())
        if n != 1:
            sys.exit(f"{model}/parameters.py does not define MW as cmath.sqrt((1 + MW21 + MW22)*MW2SM)")
        open(p, "w").write(new)
        os.rename(tmp, dst)
    m0, m_on, f_on = mw_value(model, "dim8_all=0"), mw_value(model, all_on(model, 2000.0)), mw_value(dst, all_on(dst, 2000.0))
    check(f"controls: {os.path.basename(dst)} keeps M_W at its value with the coefficients off",
          abs(f_on - m0) < 1e-6 and abs(m_on - m0) > 1e-3,
          f"M_W0 = {m0:.6f} GeV; every coefficient at one at 2 TeV: {f_on:.6f} GeV frozen, {m_on:.6f} GeV in {os.path.basename(model)}")
    return dst


def same_release(a, b):
    """The second model is the release of the first in the other input scheme: the same files, the
    same coefficients in DIM6, DIM8 and DIM8F, and one scale Lam, without Lam6, with L6 = Lam**(-2)
    and L8 = Lam**(-4) in both."""
    files = lambda m: sorted(x for x in os.listdir(m) if x != "__pycache__" and not x.endswith((".pyc", ".pkl")))
    na, nb = (N._names_of(os.path.join(m, "param_card_template.dat")) for m in (a, b))
    blocks = all(na.get(k) == nb.get(k) for k in ("DIM6", "DIM8", "DIM8F"))
    scale = all("Lam" in n.get("DIM8", []) and not any(x.lower() == "lam6" for v in n.values() for x in v) for n in (na, nb))
    pars = [open(os.path.join(m, "parameters.py")).read() for m in (a, b)]
    lam = all(re.search(r"L6 = Parameter\(name = 'L6',[^)]*value = 'Lam\*\*\(-2\)'", p, re.S)
              and re.search(r"L8 = Parameter\(name = 'L8',[^)]*value = 'Lam\*\*\(-4\)'", p, re.S)
              and "name = 'Lam6'" not in p for p in pars)
    md5 = lambda f: hashlib.md5(open(f, "rb").read()).hexdigest()
    differ = [f for f in files(a) if f in files(b) and md5(os.path.join(a, f)) != md5(os.path.join(b, f))]
    return check(f"controls: {os.path.basename(b)} is the release of {os.path.basename(a)}",
                 files(a) == files(b) and blocks and scale and lam,
                 f"{len(files(a))} files alike, {sum(len(na.get(k, [])) for k in ('DIM6', 'DIM8', 'DIM8F'))} entries in DIM6, "
                 f"DIM8 and DIM8F alike, one scale Lam; the files that differ: {', '.join(differ) or 'none'}")


def cmd_controls(argv):
    mw = os.path.abspath(opt(argv, "--mw", "").rstrip("/")) if "--mw" in argv else ""
    seeds = [int(x) for x in opt(argv, "--seeds", "21,22,23").split(",")]
    nev = int(opt(argv, "--nev", "20000"))
    lams_s, lam = opt(argv, "--lams", "2000,3000,4000"), float(opt(argv, "--lam", "3000"))
    lams = [float(x) for x in lams_s.split(",")]
    mmin = float(opt(argv, "--mmin", "100"))
    part = opt(argv, "--part", "all")
    arms = opt(argv, "--arms", "a,b,c").split(",")
    procs = opt(argv, "--procs", "udx,ww").split(",")
    if "a" in arms and not mw:
        sys.exit("control (a) needs --mw, the model in which M_W is an input")
    lines = {"ww": WW, "udx": f"{UDX} | mmnl={mmin:g}"}
    studies = {"ww": study_dir("ww", lines["ww"]), "udx": study_dir(f"udx_m{mmin:g}", lines["udx"])}
    refkey = {"ww": "ww", "udx": f"udx_m{mmin:g}"}
    label = {"ww": "p p > w+ w-", "udx": f"u d~ > e+ ve, m > {mmin:g} GeV"}
    models = {}
    if "a" in arms:
        if not same_release(MODEL, mw):
            return 1
        models["a"] = mw
    if "b" in arms:
        models["b"] = freeze(MODEL)
    if "c" in arms:
        models["c"] = MODEL
    plan = [(arm, p) for arm in arms for p in procs if not (arm == "c" and p == "ww")]
    if part == "prepare":                 # the copy and the studies, before runs go side by side
        return 1 if FAILED else 0
    if part in ("run", "all"):
        for arm, p in plan:
            for s in seeds:
                rc = np0(models[arm], studies[p], s, nev, lams_s, lam)
                if rc:                           # a run that failed, or a seed left incomplete
                    check(f"({arm}) {label[p]}: np0_shift.py on seed {s}", False, f"returned {rc}")
    if part == "run":
        return 1 if FAILED else 0
    tsv = lambda m, p: os.path.join(studies[p], f"np0_shift_{os.path.basename(m)}.tsv")
    ref = ref_get()
    verdict = {}
    print(f"\nthe controls at Lambda = {lam / 1000:g} TeV, every coefficient at one, seeds {','.join(map(str, seeds))}; "
          "means over the seeds with the error from their spread [pb]")
    for arm, p in plan:
        E = recipe_rows(tsv(models[arm], p), lams, lam, nev, lines[p]) if os.path.exists(tsv(models[arm], p)) else {}
        E = {s: v for s, v in E.items() if int(s) in seeds}
        tag = f"({arm}) {os.path.basename(models[arm])}, {label[p]}"
        print(f"\n{tag}")
        if len(E) < len(seeds):
            check(f"{tag}: every seed complete", False, f"{len(E)} of {len(seeds)}")
            verdict.setdefault(arm, []).append(None)
            continue
        vals = list(E.values())
        k = len(vals)
        M = {q: mean_err([v[q] for v in vals]) for q in ("x1", "x2", "np1", "np2", "s2")}
        dd = mean_err([v["x1"] - v["np1"] for v in vals])
        fl1, fl2 = sum(v["f1"] for v in vals) / k, sum(v["f2"] for v in vals) / k
        worst = max(abs(d) / e for v in vals for _, d, e in v["d0"])
        zero = all(d == 0 for v in vals for _, d, _ in v["d0"])
        print(f"   NP=0 on minus off: largest |difference| / error {worst:.2g}" + (", every difference exactly zero" if zero else "")
              + "; " + ", ".join(f"{l / 1000:g} TeV {mean_err([dict((x[0], x[1]) for x in v['d0'])[l] for v in vals])[0]:+.4g}"
                                 for l in sorted(lams, reverse=True)))
        print(f"   x1 t = {M['x1'][0]:+.5g} +- {M['x1'][1]:.2g}, NP^2==1 = {M['np1'][0]:+.5g} +- {M['np1'][1]:.2g}, "
              f"x1 t - NP^2==1 = {dd[0]:+.3g} +- {dd[1]:.2g}")
        print(f"   x2 t^2 = {M['x2'][0]:+.4g} +- {M['x2'][1]:.2g} (rounding of the runs {fl2:.2g}), NP^2==2 = {M['np2'][0]:+.5g} "
              f"+- {M['np2'][1]:.2g}, NP^2==2 at M_W0 from its scales = {M['s2'][0]:+.5g} +- {M['s2'][1]:.2g}")
        rk = refkey[p]
        if arm == "a":
            ok = [check(f"{tag}: NP=0 with the coefficients on equals NP=0 with them off at every scale", worst <= 3,
                        f"largest |difference| / error = {worst:.2g}"),
                  check(f"{tag}: x2 t^2 vanishes", abs(M["x2"][0]) <= 3 * M["x2"][1] + fl2,
                        f"{M['x2'][0]:+.3g} +- {M['x2'][1]:.2g}, rounding {fl2:.2g}"),
                  check(f"{tag}: x1 t equals NP^2==1", abs(dd[0]) <= 3 * dd[1] + fl1,
                        f"difference {dd[0]:+.3g} +- {dd[1]:.2g}, rounding {fl1:.2g}")]
            verdict.setdefault(arm, []).append(all(ok))
            continue
        need_ref = [q for q in ("x1 t", "shift t^2", "NP^2==1 at M_W0", "NP^2==2 at M_W0") if (rk, q) not in ref]
        if need_ref:
            check(f"{tag}: the reference of {rk} in {os.path.join(R, 'reference.tsv')}", False, "missing " + ", ".join(need_ref))
            verdict.setdefault(arm, []).append(None)
            continue
        z = lambda v, e, q: abs(v - ref[(rk, q)][0]) / (e ** 2 + ref[(rk, q)][1] ** 2) ** 0.5
        r1, rs = ref[(rk, "x1 t")], ref[(rk, "shift t^2")]
        if arm == "c":
            zc = z(M["x1"][0], M["x1"][1], "x1 t")
            verdict.setdefault(arm, []).append(check(
                f"{tag}: x1 t is the full t term of {rk}", zc <= 3,
                f"{M['x1'][0]:+.5g} +- {M['x1'][1]:.2g} against {r1[0]:+.5g} +- {r1[1]:.2g}, {zc:.1f} errors"))
            continue
        # (b): the tagged terms alone, which miss the full result
        z1, z2 = z(M["x1"][0], M["x1"][1], "x1 t"), z(M["x2"][0], M["x2"][1], "shift t^2")
        t1, t2 = z(M["x1"][0], M["x1"][1], "NP^2==1 at M_W0"), z(M["np2"][0], M["np2"][1], "NP^2==2 at M_W0")
        print(f"   against the full result of {rk}: x1 t {r1[0]:+.5g} +- {r1[1]:.2g}, missed by {z1:.0f} errors; the shift of the "
              f"t^2 term {rs[0]:+.4g} +- {rs[1]:.2g}, against x2 t^2 here, missed by {z2:.0f} errors")
        tags = [check(f"{tag}: x1 t is NP^2==1 at the unshifted mass", t1 <= 3,
                      f"against {ref[(rk, 'NP^2==1 at M_W0')][0]:+.5g} +- {ref[(rk, 'NP^2==1 at M_W0')][1]:.2g}, {t1:.1f} errors"),
                check(f"{tag}: NP^2==2 is NP^2==2 at the unshifted mass", t2 <= 3,
                      f"{M['np2'][0]:+.5g} +- {M['np2'][1]:.2g} against {ref[(rk, 'NP^2==2 at M_W0')][0]:+.5g} +- "
                      f"{ref[(rk, 'NP^2==2 at M_W0')][1]:.2g}, {t2:.1f} errors")]
        miss = max(z1, z2) > 5
        print(f"{'FAILS' if miss else 'DOES NOT FAIL'} {tag}: it misses the full result by {max(z1, z2):.0f} errors"
              + (", and this control must fail" if miss else ", where it must miss it by more than five"))
        verdict.setdefault(arm, []).append(all(tags) and miss)
    print()
    ok = True
    for arm, want in (("a", "passes"), ("b", "fails against the full result, reproducing the tagged terms"), ("c", "passes")):
        if arm not in verdict:
            continue
        good = all(v is True for v in verdict[arm])
        ok &= good
        print(f"control ({arm}) {os.path.basename(models[arm])}: {'as required' if good else 'NOT as required'}: it must be that it {want}")
    ok = ok and bool(verdict) and not FAILED
    print("controls: " + ("as required" if ok else "NOT as required"))
    return 0 if ok else 1


def cmd_report(argv):
    p = os.path.join(R, "reference.tsv")
    if not os.path.exists(p):
        print("no reference yet")
        return 1
    rows = [l.split("\t") for l in open(p).read().split("\n")[1:] if l]
    for r in rows:
        print(f"{r[0]:<10s} {r[1]:<20s} {float(r[2]):+.5g} +- {float(r[3]):.2g} pb   ({r[4]})")
    return 0


def main(argv):
    cmds = {"points": cmd_points, "udx": cmd_udx, "ww": cmd_ww, "controls": cmd_controls, "report": cmd_report}
    if len(argv) < 2 or argv[1] not in cmds:
        print(__doc__)
        return 2
    need()
    rc = cmds[argv[1]](argv[1:])
    if argv[1] == "controls":
        return rc
    if FAILED:
        print(f"\n{len(FAILED)} checks failed: {'; '.join(FAILED)}")
    return 1 if FAILED or rc else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
