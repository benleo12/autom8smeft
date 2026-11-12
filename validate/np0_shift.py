#!/usr/bin/env python3
"""The part of the 1/Lambda^4 interference that carries no coupling order.

    validate/np0_shift.py <study dir> [--nev 5000] [--seed 21] [--classes] [--report] [--lam 3000]

MadGraph counts interaction orders on couplings, and a mass is not a coupling.  In the
{alpha, M_Z, G_F} scheme a dimension-eight coefficient shifts the W mass, which sits in a
propagator and therefore enters EVERY order including NP=0, while every coupling shift (gauge
couplings, vev, Yukawas, Higgs quartic, all written as tagged series) appears in
NP^2==2 as a new vertex would.  The complete order 1/Lambda^4 cross section is

    sigma_{1/Lambda^4} = sigma(NP^2==2, c) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]

and this script measures the bracket, which the class tables of the studies do not contain.  The
coefficients enter NP=0 only through M_W, so a pair of runs whose W masses differ by a resolvable
amount gives d sigma/d M_W^2, and the report multiplies it by the M_W^2 shift at the setting of each
tagged row, so that bracket and tagged interference stand at one scale.  It is cheap: the NP=0
amplitude is the Standard-Model diagram set, so one process directory serves every coefficient
setting and only the param card changes between runs.  The runs of a process share one random seed
(--seed), so that their difference is far more precise than either run: in p p > z z, where no W
enters, the two runs of examples/studies/diboson/np0_shift.tsv agree to every digit.  The report
adds the errors of the two runs in quadrature, as if they were independent, which is therefore an
upper bound.

Without --classes only the all-coefficients-on bracket is measured, one number per process.
With --classes the 21 class cards are measured too, which is only worth doing for a process whose
Standard-Model diagram count is small.  --report prints the table of a study from its
np0_shift.tsv without running anything, and --tex FILE also writes it as a LaTeX table.  Given
--all in place of a study directory, the script merges the np0_shift.tsv of every study into
validate/np0_all.tsv and reports on the merged table, again with an optional --tex FILE.  --lam sets
the scale of the tagged rows the bracket is quoted against (default 3000, the studies' Lam=).  The
tagged rows are those of the same model in the study's results.tsv.  Where it has none, the bracket
is quoted at --lam with every coefficient of the set at one, so that --report --lam 1000 gives the
difference of the pair itself.

The combined models.  With DIM8_MODEL naming a model with a dimension-six sector (dim68_is), the
script runs a mode of its own:

    DIM8_MODEL=models/dim68_is validate/np0_shift.py <study dir> [--lams 2000,3000,4000] [--lam 3000]
                                                     [--nev 20000] [--seed 21] [--point FILE] [--report | --settle]

There the W mass moves already at 1/Lambda^2.  With t = 1/Lambda^2 it is
M_W^2 = M_W0^2 (1 + a t + b t^2), a from dimension six and b from dimension eight and the squares and
products of the dimension-six coefficients.  Write sigma_k(t) for the run at NP^2==k and scale t,
with the shifted mass inside, and S_k = sigma_k / t^k, a function of t through M_W^2 alone.  The
full cross section is the sum of the sigma_k, and expanding each S_k about M_W0^2 gives

    t^1:  S_1 + a M_W0^2 S_0'
    t^2:  S_2 + a M_W0^2 S_1' + b M_W0^2 S_0' + (a M_W0^2)^2 S_0''/2

with the derivatives taken with respect to M_W^2 at M_W0^2.  The square of the dimension-six
amplitude is part of S_2, which is NP^2==2 at the unshifted mass.  NP^2==2 run at the shifted mass
differs from that by a term of order t^3, so it needs no correction at this order.  What the tags
miss is collected by one combination of runs,

    X(t) = sigma(NP=0, c; t) - sigma(NP=0, 0) + sigma(NP^2==1, c; t) = x1 t + x2 t^2 + x3 t^3 + ...

    sigma_{1/Lambda^2} = x1 t,        sigma_{1/Lambda^4} = sigma(NP^2==2, c; t) + x2 t^2

x1 is the dimension-six interference together with the first-order shift of the SM rate.  x2 holds
the second-order shift of the SM rate (its b and a^2 terms) and the shift of the dimension-six
interference by the dimension-six mass shift.  The script runs NP=0 and NP^2==1 at each scale of
--lams with every coefficient of both sectors at one and one random seed (--seed), NP=0 with the
coefficients off, and NP^2==2 at --lam, and solves X(t)/t = x1 + x2 t (+ x3 t^2 with three scales)
through the scales.  The neglected terms move x2 by about x3 (t_1 + t_2) with two scales and by
less with three, and x3/x2 is roughly the relative shift of M_W^2 per unit t times the logarithmic
sensitivity of the rate to M_W^2.  So the scales have to keep the shift of M_W^2 small against the
scale on which the rate varies with it: M_W^2 for produced W bosons, M_W Gamma_W where a W line
shape is resolved.  With every coefficient at one in dim68_is, M_W moves by -1.82 GeV at 2 TeV and
-0.77 GeV at 3 TeV, so |delta M_W^2| reaches M_W Gamma_W near Lambda = 2.6 TeV.  The default scales
suit produced W bosons and off-shell tails.  In p p > w+ w- x3 t^3 is +0.003 +- 0.009 pb at 3 TeV
against x2 t^2 = +0.07 +- 0.03 pb (14 seeds), and in u d~ > e+ ve with m(e+ ve) > 100 GeV the three
scales miss the t^2 term at 3 TeV by 0.6 per cent.  Where the W line shape is resolved, take --lams
4000,6000,8000.  At a fixed u d~ > e+ ve phase-space point on the W pole the defaults miss x2 by up
to twice the whole t^2 term, these scales by under a fifth of it, and by under three per cent once
sqrt(s) is a width from the pole.  Larger scales cost statistical precision, since X shrinks with t.  The report prints x2 from the two
smallest t as well, so that the user sees how far the third scale moved it.  Errors are propagated
as if the runs were independent, which overstates them, because a common seed correlates the runs
positively.  So run two or three values of --seed (their rows add up in one file) and quote the
error of the mean from their spread, which the report prints.  For p p > w+ w- at 13.6 TeV with
20000 events a run, x2 t^2 at 3 TeV spreads by 0.10 pb from seed to seed (14 seeds), so that three
seeds give it to 0.06 pb, against 0.9 pb propagated for one seed.  The correlation needs every run
to depend on its cards and its seed alone.  A MadEvent run also reads the random-number offsets
that the run before left in its channel directories, so the script removes those directories
before every run.

A seed counts only when it is complete: NP=0 with the coefficients off, NP=0 and NP^2==1 at every
scale of --lams, and NP^2==2 at --lam.  The fit is through exactly the scales of --lams, so --report
and --all take the --lams of the runs, and a scale in the file but not in --lams is not used.  For a
process and seed that lacks any of these runs the report prints one line INCOMPLETE naming them,
leaves the seed out of the fit and of the mean over seeds, and returns nonzero.

By default every coefficient of both sectors is at one.  --point FILE sets them instead, a line
NAME=VALUE for each coefficient with its param-card name (cW, cHW, c8H8x1, ...) and # for a
comment, and every coefficient the file does not name is zero.  Lam is not part of a point and
comes from --lams and --lam.  A name that is not in the card of every process directory, misspelt or
removed there by a restriction card, stops the script before anything runs.  A point has an
identifier, the stem of the file and the first 8 hex digits of the sha256 of its sorted nonzero
assignments, so that it does not change when the lines are reordered or a value is written another
way, and changes with any value.  The default is all_one.  The runs of the default go to
np0_shift_<model>.tsv in the study and those of a point to np0_shift_<model>_<identifier>.tsv.  The
report refuses a file with the rows of another point or of several, and --all merges only the files
of the one point, into validate/np0_all_<model>.tsv or validate/np0_all_<model>_<identifier>.tsv.
The W masses the report prints are those of the point.

Each row holds the order, the scale, the number of events, the seed, the extra run settings of the
line of processes.txt (the part after "|", sorted, or "none") and the identifier of the point, and a
run is reused only when all of them and the process agree.  A changed --nev or a changed cut
therefore makes the runs again, and the report fits the runs of one line and one number of events
together.  A file written before the settings were recorded is rewritten with them "unknown" (and
with all_one where it has no point column).  Such rows are never reused, and the report counts them
and leaves them out.  --settle writes the extras of the present processes.txt into them and runs
nothing, and is for a file whose job is known to have run with that line, since nothing in the
rows says so.

validate/np0_fixed_order.py tests this mode with the real generator.  It finds the same terms a
second way, as the t and t^2 coefficients of the full cross section at fixed order over many
scales, and it runs the mode on two controls, with three seeds at 3 TeV in p p > w+ w- and in
u d~ > e+ ve with m(e+ ve) > 100 GeV.  In dim68_mw, where M_W is an input and the coefficients reach
NP=0 nowhere, the mode has to find NP=0 with the coefficients on equal to NP=0 with them off,
x2 t^2 zero and x1 t equal to NP^2==1.  It finds NP=0 the same to every digit with the coefficients
on and off, x2 t^2 = +0.000005 +- 0.0001 pb in u d~ > e+ ve, where NP^2==2 is 0.075 pb, and
+0.001 +- 0.001 pb in p p > w+ w-, where NP^2==2 is 1.15 pb, and x1 t - NP^2==1 =
-0.0000007 +- 0.00007 pb and -0.0008 +- 0.0007 pb.  In a copy of dim68_is whose M_W is frozen at
M_W0 the mode can only return the tagged terms at the unshifted mass, and it has to reproduce them
and miss the full result by more than five errors.  It returns x1 t = +0.117 pb in u d~ > e+ ve,
where the full t term is -0.736 +- 0.004 pb, and -1.337 pb in p p > w+ w-, where it is
+0.60 +- 0.08 pb.
"""
from __future__ import annotations

import collections
import hashlib
import json
import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
PY = "python3.11"
MODEL = os.environ.get("DIM8_MODEL", os.path.join(ROOT, "models", "dim8_is"))   # any copy of the released model
# The bracket exists in a model whose W mass moves, dim8_is, which is why that is the default.  In
# dim8_mw M_W is an input and the bracket vanishes, which DIM8_MODEL=models/dim8_mw measures.  Each
# model has its own files: np0_shift.tsv and validate/np0_all.tsv for dim8_is, the names they had
# when it was the default, and np0_shift_<model>.tsv and validate/np0_all_<model>.tsv for any other.
MNAME = os.path.basename(MODEL.rstrip("/"))
MTAG = "" if MNAME == "dim8_is" else "_" + MNAME
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "np0")
NICE = ["nice", "-n", "19"]
# The coefficients enter NP=0 only through M_W, so the bracket is d sigma_SM/d M_W^2 times delta M_W^2
# to first order.  Lam=1000 with every coefficient at one lowers the M_W of dim8_is by 0.47 GeV, a
# shift the Monte Carlo resolves, and the derivative it gives times the delta M_W^2 of any other
# setting is the bracket there (the paper's 3 TeV number, where M_W moves by -6 MeV).
LAM_BRACKET = 1000


def _has_dim6(model):
    """A combined model has a DIM6 block in its card, and the mode at the end of the docstring
    replaces the bracket pair.  dim68_mw has the block too, and there the mode measures zero, since
    its M_W does not move."""
    p = os.path.join(model, "param_card_template.dat")
    if os.path.exists(p):
        return re.search(r"^\s*block\s+dim6\b", open(p).read(), re.I | re.M) is not None
    return MNAME.startswith("dim68")


COMBINED = _has_dim6(MODEL)
# The scales, in GeV, at which that mode runs NP=0 and NP^2==1.
LAMS = [2000.0, 3000.0, 4000.0]
# A row of the results file: the run, the cross section, the events and seed of the run, the extra
# run settings of its line in processes.txt (the part after "|", sorted, "none" when there are none)
# and the identifier of the coefficient point.
HEAD_C = "process\torder\tlam\tsigma_pb\terror_pb\tnevents\tseed\tsettings\tpoint"
# the headers of the files written before the points (HEAD_C7) and before the settings (HEAD_C8)
HEAD_C7 = "process\torder\tlam\tsigma_pb\terror_pb\tnevents\tseed"
HEAD_C8 = HEAD_C7 + "\tpoint"
# the identifier of the default point, every coefficient of both sectors at one
ALL_ONE = "all_one"
# the settings of a line without extras, and of a row written before the settings were recorded
NONE, UNKNOWN = "none", "unknown"
Point = collections.namedtuple("Point", "id asg written path")


def class_wcs(n):
    """The param-card entries of a class: a complex coefficient is a Re and an Im entry, not the
    base name the catalogue carries."""
    sys.path.insert(0, os.path.join(ROOT, "validate"))
    import cardnames
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    return cardnames.expand(MODEL, [w for e in idx if e["cls"] == n for w in e["wcs"]])


_mw_cache = {}


def mw_of(settings, cls=None):
    """M_W of the model at these settings, from validate/eval_ufo_params.py as table_study.py reads
    it.  For a class only that class's coefficients take the dim8_all= value, as in its card."""
    if cls is not None and "dim8_all=" in settings:
        v = re.search(r"dim8_all=(\S+)", settings).group(1)
        settings = " ".join(f"{w}={v}" for w in class_wcs(cls)) + " " + re.sub(r"dim8_all=\S+", "", settings)
    if settings not in _mw_cache:
        py = shutil.which("python3.11") or "python3"
        res = subprocess.run([py, os.path.join(ROOT, "validate", "eval_ufo_params.py"), MODEL]
                             + settings.split() + ["--show=MW"], capture_output=True, text=True)
        m = re.search(r"^MW\s*=\s*([-\d.eE+]+)", res.stdout, re.M)
        # no number in place of a mass that could not be evaluated: every shift printed from it
        # would be a nan, and the reader would not see why
        if not m:
            sys.exit(f"validate/eval_ufo_params.py gave no M_W for {MODEL} at \"{settings}\" (it returned "
                     f"{res.returncode}):\n" + ((res.stderr or res.stdout).strip()[-2000:] or "no output"))
        _mw_cache[settings] = float(m.group(1))
    return _mw_cache[settings]


def run(cmd, log, cwd=None):
    with open(log, "a") as fh:
        fh.write("\n$ " + " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else "") + "\n")
        return subprocess.run(NICE + cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, cwd=cwd, check=False).returncode


def main(argv) -> int:
    global LAM
    # the usage, when the study directory is missing
    if len(argv) < 2 or argv[1] in ("-h", "--help") or (argv[1].startswith("-") and argv[1] != "--all"):
        print(__doc__)
        return 0 if argv[1:2] in (["-h"], ["--help"]) else 2
    LAM = float(argv[argv.index("--lam") + 1]) if "--lam" in argv else 3000.0
    if COMBINED:
        return main_combined(argv)
    if "--point" in argv:
        print("--point is an option of the mode for combined models")
        return 2
    if argv[1] == "--all":
        # one table over every study that has been measured, which is what the paper carries
        import glob
        studies = sorted(glob.glob(os.path.join(ROOT, "examples", "studies", "*", f"np0_shift{MTAG}.tsv")))
        merged = os.path.join(ROOT, "validate", f"np0_all{MTAG}.tsv")
        seen, out = set(), ["process\tset\tsigma_pb\terror_pb\tnevents"]
        for f in studies:
            for l in open(f).read().split("\n")[1:]:
                if l and tuple(l.split("\t")[:2]) not in seen:
                    seen.add(tuple(l.split("\t")[:2]))
                    out.append(l)
        open(merged, "w").write("\n".join(out) + "\n")
        tex = argv[argv.index("--tex") + 1] if "--tex" in argv else None
        # the tagged interference comes from whichever study holds the process
        return report(merged, tex, os.path.join(ROOT, "examples", "studies"), multi=True, lam=LAM)
    st = os.path.abspath(argv[1])
    out = os.path.join(st, f"np0_shift{MTAG}.tsv")
    if "--report" in argv:
        return report(out, argv[argv.index("--tex") + 1] if "--tex" in argv else None, st, lam=LAM)
    nev = int(argv[argv.index("--nev") + 1]) if "--nev" in argv else 5000
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 21
    with_classes = "--classes" in argv
    procs = []
    for l in open(os.path.join(st, "processes.txt")):
        l = l.split("#")[0].strip()
        if l:
            procs.append(l)
    # the process directories of a model sit in a directory of their own, so that one made with
    # another model is never taken for it
    work = os.path.join(WORK, MNAME)
    os.makedirs(work, exist_ok=True)
    if not os.path.exists(out):
        open(out, "w").write("process\tset\tsigma_pb\terror_pb\tnevents\n")
    done = {tuple(l.split("\t")[:2]) for l in open(out).read().split("\n")[1:] if l}
    failed = 0
    for line in procs:
        proc = line.split("|")[0].strip()
        extra = line.split("|")[1].split() if "|" in line else []
        tag = re.sub(r"[^A-Za-z0-9]+", "_", proc.replace("+", "p").replace("-", "m")).strip("_")
        d = os.path.join(work, tag)
        log = os.path.join(work, tag + ".log")
        if not os.path.exists(os.path.join(d, "bin", "generate_events")):
            sc = os.path.join(work, tag + ".mg5")
            open(sc, "w").write(f"import model {MODEL}\ngenerate {proc} NP=0\noutput {d} -f\n")
            run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc], log)
            if not os.path.exists(os.path.join(d, "bin", "generate_events")):
                print(f"[{tag}] no output, see {log}", flush=True)
                failed += 1
                continue
            open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
                "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
        bad = _unknown_extras(d, extra)
        if bad:
            print(f"[{tag}] the cards have no entry {', '.join(bad)} of its line in processes.txt, misspelt "
                  "or not a setting of this process, so nothing is run for it", flush=True)
            failed += 1
            continue
        jobs = [("off", ["dim8_all=0"]), ("on", ["dim8_all=1"])]
        if with_classes:
            jobs += [(f"cls{c}", ["dim8_all=0"] + [f"{w}=1" for w in class_wcs(c)]) for c in range(1, 22)]
        for name, sets in jobs:
            if (proc, name) in done:
                continue
            # H_T/2, the scale MadGraph sets for the tagged interference, so that the bracket and the
            # interference it is added to share one scale
            # one seed for every run of the process: without it MadEvent takes the next seed of the
            # directory for each run, and the difference of two runs carries both their errors
            common = [f"nevents={nev}", "ebeam1=6800", "ebeam2=6800", f"iseed={seed}",
                      "hel_recycling=False", "use_syst=False", "dynamical_scale_choice=3"]
            have = set(re.findall(r"=\s*(\w+)", open(os.path.join(d, "Cards", "run_card.dat")).read()))
            # only the script's own settings may be left out when a run card lacks them.  The cuts
            # of the line were checked above, and a run is made with every one of them
            common = [a for a in common if a.split("=")[0] in have or a.startswith("hel_recycling")] + extra
            if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d]
                   + common + sets + [f"Lam={LAM_BRACKET}"], log):
                print(f"[{tag}] {name}: card error, see {log}", flush=True)
                failed += 1
                continue
            _clear_channels(d)
            before = os.path.getsize(log)
            run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
            txt = open(log, errors="replace").read()[before:]
            m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
            # a run that stopped has no cross section, and no row: it is run again next time, and the
            # report leaves the process out rather than taking a zero for its rate
            if not m or "interrupted with error" in txt:
                print(f"[{tag}] {name}: MadGraph gave no cross section, see {log}", flush=True)
                failed += 1
                continue
            x, e = float(m[-1][0]), float(m[-1][1])
            with open(out, "a") as fh:
                fh.write(f"{proc}\t{name}\t{x:.6g}\t{e:.6g}\t{nev}\n")
            print(f"[{tag}] NP=0 {name:7s} {x:12.5g} +- {e:.3g} pb", flush=True)
    if failed:
        print(f"{failed} runs gave no cross section")
    return report(out, None, st, lam=LAM) or (1 if failed else 0)


def report(out, tex=None, study=None, multi=False, lam=3000.0) -> int:
    if not os.path.exists(out):
        print("no results yet")
        return 1
    rows = [l.split("\t") for l in open(out).read().split("\n")[1:] if l]
    by = {(p, s): (float(x), float(e)) for p, s, x, e, _ in rows}
    # The tagged interference of the same process and the SAME model, for context, from the study's
    # results.tsv, the file that run_study.sh writes and that ships.  A bracket set against the
    # tagged term of the other scheme would be meaningless, so a row of another model is not used.
    # The tagged rows give the setting the bracket is wanted at (the study's Lam=, with the full model
    # or one class on), and their interference is quoted at that same setting, never moved to another
    # scale.  Without a tagged row of this model the bracket is quoted at --lam with every
    # coefficient of the set at one.
    tagged = {}
    import glob as _g
    dirs = (sorted(_g.glob(os.path.join(study, "*", ""))) if multi and study else ([study] if study else []))
    for sd in dirs:
        for rp in (os.path.join(sd, "results.tsv"),):
            if not os.path.exists(rp):
                continue
            R = [l.rstrip("\n").split("\t") for l in open(rp)]
            h, R = R[0], R[1:]
            ci = {k: i for i, k in enumerate(h)}
            for r in R:
                mod = r[ci["model"]]
                if mod.split("-")[0] != MNAME or r[ci["order"]] != "NP^2==2" or "-op_" in mod \
                   or not re.match(r"^-?[\d.]", r[ci["sigma_pb"]]):
                    continue
                lm = re.search(r"Lam=([\d.]+)", r[ci["settings"]])
                if not lm or float(lm.group(1)) != lam:   # one scale: rows at another Lam are not used
                    continue
                cm = re.search(r"-cls(\d+)$", mod)
                s = f"cls{cm.group(1)}" if cm else ("on" if mod == MNAME else None)
                if s:
                    tagged[(r[ci["process"]].strip(), s)] = (float(r[ci["sigma_pb"]]), float(r[ci["error_pb"]]),
                                                             r[ci["settings"]])
    # The coefficients enter NP=0 only through M_W, so the pair measures d sigma/d M_W^2, and the
    # bracket at the tagged setting is that derivative times the M_W^2 shift there.  The pair is run
    # at LAM_BRACKET, where M_W moves enough for the Monte Carlo to resolve the difference.
    def mw(s, settings):
        cls = int(s[3:]) if s.startswith("cls") else None
        return mw_of(settings if s != "off" else "dim8_all=0", cls)
    print(f"\nthe pair at Lambda = {LAM_BRACKET / 1000:g} TeV gives d sigma/d M_W^2, and the bracket is "
          "quoted at the setting of the tagged interference beside it (its Lam=, every coefficient of "
          f"the set at one), or without one at Lambda = {lam / 1000:g} TeV with every coefficient of the set "
          "at one; of SM is the bracket over NP=0 with the coefficients off")
    print(f"{'process':<22s} {'set':<6s} {'dM_W pair':>10s} {'dsig/dM_W^2':>12s} {'Lam':>5s} {'dM_W':>8s} "
          f"{'bracket':>11s} {'error':>9s} {'of SM [%]':>15s} {'tagged':>11s} {'total':>11s}  [pb, GeV]; "
          "error: those of the two runs in quadrature, an upper bound for runs that share a seed")
    lines = []
    for p in sorted({k[0] for k in by}):
        off = by.get((p, "off"))
        if not off:
            continue
        m0 = mw("off", "")
        for s in ["on"] + [f"cls{c}" for c in range(1, 22)]:
            v = by.get((p, s))
            if not v:
                continue
            m1 = mw(s, f"dim8_all=1 Lam={LAM_BRACKET}")
            if not m1 - m0:
                print(f"{p:<22s} {s:<6s} M_W does not move with this set, so the bracket is zero")
                continue
            der = (v[0] - off[0]) / (m1 ** 2 - m0 ** 2)
            dere = (v[1] ** 2 + off[1] ** 2) ** 0.5 / abs(m1 ** 2 - m0 ** 2)
            t = tagged.get((p, s))
            if t and "Lam=" not in t[2]:
                t = None
            sett = t[2] if t else f"dim8_all=1 Lam={lam:g}"
            lamv = float(re.search(r"Lam=([\d.]+)", sett).group(1))
            mt = mw(s, sett)
            d, de = der * (mt ** 2 - m0 ** 2), dere * abs(mt ** 2 - m0 ** 2)
            print(f"{p:<22s} {s:<6s} {m1 - m0:>+10.4f} {der:>+12.4g} {lamv / 1000:>4g}T "
                  f"{mt - m0:>+8.2e} {d:>+11.4g} {de:>9.2g} {100 * d / off[0]:>+8.2f} +- {100 * de / abs(off[0]):<4.2f}"
                  + (f" {t[0]:>11.4g} {t[0] + d:>11.4g}" if t else f" {'no row':>11s} {'':>11s}")
                  + ("" if abs(d) > 2 * de else "   (consistent with zero)"))
            if s == "on" and t:
                lines.append((p, off, v, d, de, t, lamv))
    if tex and lines:
        def _g(x, sig=4):
            """A LaTeX number: a power of ten below 1e-3, where %g would print 4.5e-05 and
            math mode would typeset it as 4.5e - 05."""
            if x == 0:
                return "0"
            if abs(x) >= 1e-3:
                return f"{x:.{sig}g}"
            m, ex = f"{x:.{sig - 1}e}".split("e")
            return f"{m}\\times 10^{{{int(ex)}}}"

        def num(x, e=None):
            return f"${_g(x)}$" if e is None else f"${_g(x)} \\pm {_g(e, 2)}$"
        body = [f"{_texproc(p)} & {num(d, de)} & {num(t[0], t[1])} & "
                f"{num(t[0] + d)} & ${100*d/t[0]:+.0f}\\%$" + r" \\"
                for p, off, v, d, de, t, lam in lines]
        lams = {lam for *_, lam in lines}
        lamtex = f"$\\Lambda = {lams.pop() / 1000:g}$~TeV" if len(lams) == 1 else "the $\\Lambda$ of each row"
        open(tex, "w").write(r"""\begin{table}[t]\centering\footnotesize
\begin{tabular}{@{}l r r r r@{}}
\toprule
process & bracket [pb] & $\sigma(\texttt{NP\^{}2==2})$ [pb] & total [pb] & ratio \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\caption{The part of order $1/\Lambda^4$ that carries no coupling order, \cref{eq:np0}, with all 674
coefficients at one and """ + lamtex + r""". ``bracket'' is $\sigma(\mathrm{NP}=0; C) - \sigma(\mathrm{NP}=0; 0)$,
the shift of the Standard-Model rate caused by the $W$ mass moving with the coefficients, given by
the derivative of that rate with respect to $M_W^2$ at fixed couplings times the shift of $M_W^2$. It
is not in the $\texttt{NP\^{}2==2}$ column and has to be added to it. Generated by
\code{validate/np0\_shift.py --report --tex}.}
\label{tab:np0}
\end{table}
""")
        print(f"wrote {tex}")
    return 0


def _texproc(p):
    m = {"p": "p", "w+": "W^+", "w-": "W^-", "z": "Z", "h": "H", "a": r"\gamma", "j": "j",
         "e+": "e^+", "e-": "e^-"}
    i, f = p.split(">", 1)
    f = re.sub(r"\b(QCD|QED|NP)\S*", "", f)
    return ("$" + " ".join(m.get(x, x) for x in i.split()) + r" \to "
            + " ".join(m.get(x, x) for x in f.split()) + "$")


def _names_of(card):
    """The names of the entries of a param card, block by block."""
    blk, out = None, {}
    for l in open(card):
        mb = re.match(r"^\s*block\s+(\S+)", l, re.I)
        if mb:
            blk = mb.group(1).upper()
            continue
        m = re.match(r"^\s*\d+\s+\S+\s*#\s*(\w+)", l)
        if m and blk:
            out.setdefault(blk, []).append(m.group(1))
    return out


def _card_names(d):
    """The names of the entries of a process directory's param card, block by block."""
    return _names_of(os.path.join(d, "Cards", "param_card.dat"))


def _unknown_extras(d, extra):
    """The settings of a line of processes.txt that neither card of the process directory d has, as
    written.  examples/studies/set_cards.py would refuse them, and hel_recycling is the one entry it
    adds to a run card by itself."""
    lines = open(os.path.join(d, "Cards", "run_card.dat")).read().split("\n")
    have = {_norm(m.group(1)) for l in lines for m in [re.match(r"^\s*[^=!]+?\s*=\s*(\w+)", l)] if m}
    have |= {_norm(n) for names in _card_names(d).values() for n in names} | {"hel_recycling"}
    return [a.split("=")[0] for a in extra if _norm(a.split("=")[0]) not in have]


def _norm(n):
    """A card name as examples/studies/set_cards.py matches it: without case and without the __2 that
    MadGraph appends on a name collision, so that the dimension-six cW, which a process card writes
    as cw, is one name."""
    return re.sub(r"__\d+$", "", n).lower()


def _scale(x):
    """A scale in GeV to the six digits that the rows and the cards carry, so that a scale of --lams
    always matches the rows written at it."""
    return float(f"{float(x):g}")


def read_point(path):
    """A coefficient point from a file of lines NAME=VALUE, with the names of the param card and #
    starting a comment.  The assignments are keyed on the name as set_cards.py matches it.  The
    identifier is the file's stem and the first 8 hex digits of the sha256 of the sorted assignments,
    each value written as the float it is and a zero left out, since a coefficient set to zero is set
    as if it were not named.  So reordering the file or writing 1 as 1.0 keeps the identifier, and
    changing a value changes it.  A line that is not an assignment, a name given twice, a value that
    is not a finite number, and Lam (which the scales set) or dim8_all (which would switch on what the
    file does not name) raise ValueError."""
    asg, written = {}, {}
    for i, l in enumerate(open(path), 1):
        l = l.split("#")[0].strip()
        if not l:
            continue
        m = re.match(r"^([A-Za-z]\w*)\s*=\s*(\S+)$", l)
        if not m:
            raise ValueError(f"{path}, line {i}: not NAME=VALUE: {l}")
        k = _norm(m.group(1))
        if k in ("lam", "dim8_all"):
            raise ValueError(f"{path}, line {i}: {m.group(1)} is not a coefficient, and the scale comes "
                             "from --lams and --lam")
        if k in asg:
            raise ValueError(f"{path}, line {i}: {m.group(1)} is set twice")
        try:
            v = float(m.group(2))
        except ValueError:
            v = float("nan")
        if not math.isfinite(v):
            raise ValueError(f"{path}, line {i}: {m.group(2)} is not a finite number")
        asg[k], written[k] = v, m.group(1)
    key = "\n".join(f"{k}={v!r}" for k, v in sorted(asg.items()) if v != 0)
    stem = re.sub(r"[^A-Za-z0-9_-]+", "_", os.path.splitext(os.path.basename(path))[0])
    return Point(f"{stem}_{hashlib.sha256(key.encode()).hexdigest()[:8]}", asg, written, path)


def _point_missing(names, point):
    """The names of a point that are not exactly one coefficient entry of a card (blocks DIM6, DIM8
    and DIM8F, Lam aside): one that a restriction card removed, or a misspelt one."""
    have = {}
    for b in ("DIM6", "DIM8", "DIM8F"):
        for n in names.get(b, []):
            have.setdefault(_norm(n), []).append(n)
    have.pop("lam", None)
    return [point.written[k] for k in point.asg if len(have.get(k, [])) != 1]


def _settings(d, on, lam, point=None):
    """Every coefficient of both sectors at one (on) or at zero, and the scale lam in GeV.  dim8_all
    sets the dimension-eight entries.  The dimension-six ones are named one by one from the card of
    the process, a complex one as its modulus with the phase at zero, so that a restriction card that
    removed some of them is respected.  With a point (read_point) and on, every coefficient is at zero
    except those the point names, which take its values: dim8_all=0 and the named dimension-eight
    entries, and every dimension-six entry with its value or zero."""
    names = _card_names(d)
    v = 1 if on else 0
    has8 = any(n.lower().startswith("c8") for b in ("DIM8", "DIM8F") for n in names.get(b, []))
    if point is None or not on:
        out = [f"dim8_all={v}"] if has8 else []
        out += [f"{n}={0 if n.endswith('Ph') else v}" for n in names.get("DIM6", [])]
    else:
        out = ["dim8_all=0"] if has8 else []
        out += [f"{n}={point.asg[_norm(n)]!r}" for b in ("DIM8", "DIM8F") for n in names.get(b, [])
                if _norm(n) in point.asg]
        out += [f"{n}={point.asg.get(_norm(n), 0.0)!r}" for n in names.get("DIM6", [])]
    out.append(f"Lam={lam:g}")
    return out


def _mw_on(lam, point=None):
    """M_W with every coefficient of both sectors at one and the scale lam (0: all off), from the
    model's own expressions, under the names of the UFO.  With a point, the coefficients it names
    take its values and every other one is at zero, as in the runs."""
    if not lam:
        return mw_of("dim8_all=0")
    names = _names_of(os.path.join(MODEL, "param_card_template.dat"))
    six = names.get("DIM6", [])
    if point is None:
        return mw_of("dim8_all=1 " + " ".join(f"{n}=1" for n in six if not n.endswith("Ph")) + f" Lam={lam:g}")
    eight = [n for b in ("DIM8", "DIM8F") for n in names.get(b, []) if _norm(n) in point.asg]
    return mw_of(" ".join(["dim8_all=0"] + [f"{n}={point.asg[_norm(n)]!r}" for n in eight]
                          + [f"{n}={point.asg.get(_norm(n), 0.0)!r}" for n in six] + [f"Lam={lam:g}"]))


def _out_c(st, point=None):
    """The results file of a study: np0_shift_<model>.tsv for every coefficient at one, and
    np0_shift_<model>_<identifier>.tsv for a point."""
    return os.path.join(st, f"np0_shift{MTAG}" + (f"_{point.id}" if point else "") + ".tsv")


def _extras(line):
    """The extra run settings of a line of processes.txt, the part after "|", as a row records them:
    sorted and joined by spaces, "none" when there are none."""
    extra = line.split("|")[1].split() if "|" in line else []
    return " ".join(sorted(extra)) or NONE


def _rows_c(out):
    """The rows of a results file of the combined mode, each of the nine columns of HEAD_C.  A row of
    seven columns was written before points existed and is read as all_one, and a row of seven or
    eight columns was written before the settings were recorded and has settings "unknown".  A row
    of any other length raises ValueError, since a cut row cannot be told from a complete one."""
    rows = []
    for i, l in enumerate(open(out).read().split("\n")[1:], 2):
        if not l:
            continue
        r = l.split("\t")
        if len(r) in (7, 8):
            r = r[:7] + [UNKNOWN, r[7] if len(r) == 8 else ALL_ONE]
        if len(r) != 9:
            raise ValueError(f"{out}, line {i}: {len(r)} columns, not 9")
        rows.append(r)
    return rows


def _key_c(r):
    """What a run is: process, order, scale, seed, events, extra settings and point.  A row is reused
    only for a run that agrees in all seven, so a changed --nev or cut makes the runs again."""
    return (r[0], r[1], r[2], r[6], r[5], r[7], r[8])


def _done_c(out, pid):
    """The runs a results file holds, keyed as _key_c, leaving out the rows whose settings are unknown,
    which are never reused.  A file with rows of another point raises ValueError, since a run of one
    point is no run of another and appending to that file would mix the two."""
    rows = _rows_c(out)
    other = sorted({r[8] for r in rows} - {pid})
    if other:
        raise ValueError(f"{out} holds rows of point {', '.join(other)}, and this is point {pid}")
    return {_key_c(r) for r in rows if r[7] != UNKNOWN}


def _write_c(out, rows):
    """The rows written as the whole file, under the present header, by a rename so that a file that is
    read at that moment is either the old or the new one."""
    open(out + ".tmp", "w").write("\n".join([HEAD_C] + ["\t".join(r) for r in rows]) + "\n")
    os.replace(out + ".tmp", out)


def _upgrade_c(out):
    """A results file with a header from before the points or before the settings is rewritten with the
    present header, its rows given all_one where they have no point and "unknown" settings, before
    anything is appended to it.  Returns the number of rows whose settings are unknown."""
    if open(out).readline().rstrip("\n") in (HEAD_C7, HEAD_C8):
        _write_c(out, _rows_c(out))
    return sum(1 for r in _rows_c(out) if r[7] == UNKNOWN)


def _settle_c(out, settings):
    """--settle: the rows whose settings are unknown and whose process is a key of settings are given
    its value, the extras of the line of processes.txt that made them.  Only for rows whose job is
    known to have run with that line, since nothing in the row says so.  Returns the number given."""
    _upgrade_c(out)
    rows, n = _rows_c(out), 0
    for r in rows:
        if r[7] == UNKNOWN and r[0] in settings:
            r[7], n = settings[r[0]], n + 1
    if n:
        _write_c(out, rows)
    return n


def _merge_c(files, pid, merged):
    """One table from the results files of the studies, all of the point pid, a run that two studies
    hold kept once.  A file with rows of another point raises ValueError."""
    seen, out = set(), [HEAD_C]
    for f in files:
        rows = _rows_c(f)
        other = sorted({r[8] for r in rows} - {pid})
        if other:
            raise ValueError(f"{f} holds rows of point {', '.join(other)}, and the merge is of point {pid}")
        for r in rows:
            if r[7] == UNKNOWN or _key_c(r) not in seen:
                seen.add(_key_c(r))
                out.append("\t".join(r))
    open(merged, "w").write("\n".join(out) + "\n")


def _required(lams, lam):
    """The runs that the fit of one process and one seed needs, with the words that name them: NP=0
    with the coefficients off, NP=0 and NP^2==1 at every scale of lams, and NP^2==2 at lam."""
    return ([(("np0", 0.0), "NP=0 with the coefficients off")]
            + [(("np0", l), f"NP=0 at {l / 1000:g} TeV") for l in lams]
            + [(("np1", l), f"NP^2==1 at {l / 1000:g} TeV") for l in lams]
            + [(("np2", lam), f"NP^2==2 at {lam / 1000:g} TeV")])


# A MadEvent run is not a function of its cards and seed alone.  The refinement of a channel that
# is not split leaves the file moffset.dat in the channel's directory SubProcesses/P*/G*, and the
# survey of the next run reads it as an offset of its random numbers.  So the first run in a
# directory differs from the same card and seed run after another run: by 0.014 pb of 68.05 pb in
# NP=0 of p p > w+ w- with the coefficients off and by 0.04 pb of 73.1 pb at 2 TeV, where one
# channel of six keeps the file, and not at all in u d~ > e+ ve, where none does.  Which channels
# keep it depends on the run before, so a difference of two runs that one seed is to correlate would
# carry it.  The channel directories are therefore removed before each run.  MadEvent makes them
# again, and every run starts as the first run of its directory does.


def _clear_channels(d):
    """Removes the channel directories that the run before left in the process directory d, so that
    the next run depends on its cards and seed alone."""
    import glob
    for g in glob.glob(os.path.join(d, "SubProcesses", "P*", "G*")):
        if os.path.isdir(g) and re.match(r"G\d", os.path.basename(g)):
            shutil.rmtree(g)


def _xsec(d, txt, rn="run_01"):
    """The cross section of the run just made.  The printed line rounds it to four digits, and the
    extraction lives on differences of runs that a common seed keeps close, so the value is taken
    from the run's banner, which keeps six, with the error from the printed line.  A run that reuses
    the name of an earlier one appends its block to the same banner, so the last block is this run."""
    m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
    if not m or "interrupted with error" in txt:
        return None
    x, e = float(m[-1][0]), float(m[-1][1])
    try:
        b = re.findall(r"Integrated weight \(pb\)\s*:\s*([-\d.eE+]+)",
                       open(os.path.join(d, "Events", rn, f"{rn}_tag_1_banner.txt"), errors="replace").read())
        if b and abs(float(b[-1]) - x) <= 1e-3 * abs(x) + 1e-12:
            x = float(b[-1])
    except (OSError, ValueError):
        pass
    return x, e


def _poly_weights(ts, deg):
    """W with c = W y for the least-squares polynomial c_0 + c_1 t + ... of degree deg through the
    points (ts, y), which is the interpolating polynomial when there are deg + 1 points."""
    n = deg + 1
    A = [[t ** k for k in range(n)] for t in ts]
    ata = [[sum(A[i][r] * A[i][c] for i in range(len(ts))) for c in range(n)] for r in range(n)]
    aug = [row[:] + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(ata)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(aug[r][col]))
        aug[col], aug[piv] = aug[piv], aug[col]
        dv = aug[col][col]
        aug[col] = [v / dv for v in aug[col]]
        for r in range(n):
            if r != col:
                f = aug[r][col]
                aug[r] = [v - f * w for v, w in zip(aug[r], aug[col])]
    inv = [row[n:] for row in aug]
    return [[sum(inv[k][j] * A[i][j] for j in range(n)) for i in range(len(ts))] for k in range(n)]


def _solve(ts, s0, s1, sm, deg):
    """x_k of X(t)/t = x_1 + x_2 t + ..., X = sigma0(t) - sigma0(0) + sigma1(t), and the NP=0 and
    NP^2==1 parts of each, with errors propagated as if the runs were independent.  The SM run
    enters every point, so its error is propagated through the sum of its weights."""
    Wt = _poly_weights(ts, deg)
    res = []
    for w in Wt:
        p0 = sum(wi * (a[0] - sm[0]) / t for wi, a, t in zip(w, s0, ts))
        p1 = sum(wi * a[0] / t for wi, a, t in zip(w, s1, ts))
        e0 = (sum((wi * a[1] / t) ** 2 for wi, a, t in zip(w, s0, ts))
              + (sm[1] * sum(wi / t for wi, t in zip(w, ts))) ** 2) ** 0.5
        e1 = sum((wi * a[1] / t) ** 2 for wi, a, t in zip(w, s1, ts)) ** 0.5
        res.append((p0 + p1, (e0 ** 2 + e1 ** 2) ** 0.5, p0, e0, p1, e1))
    return res


def main_combined(argv) -> int:
    """NP=0 and NP^2==1 at the scales of --lams, NP=0 with the coefficients off and NP^2==2 at
    --lam, one row each in the results file of the point, and then the report."""
    global LAM
    LAM = _scale(LAM)
    lams = (sorted({_scale(x) for x in argv[argv.index("--lams") + 1].split(",")}) if "--lams" in argv
            else LAMS)
    if len(lams) < 2:
        print("--lams needs two scales at least")
        return 2
    point = None
    if "--point" in argv:
        try:
            point = read_point(argv[argv.index("--point") + 1])
        except (OSError, ValueError) as e:
            print(f"--point: {e}")
            return 2
        # a misspelt name is caught here, before MadGraph has made anything, and a name that a
        # restriction card removed is caught on the card of each process below
        tpl = os.path.join(MODEL, "param_card_template.dat")
        bad = _point_missing(_names_of(tpl), point) if os.path.exists(tpl) else []
        if bad:
            print(f"--point {point.path}: {MNAME} has no coefficient {', '.join(bad)}")
            return 2
    pid = point.id if point else ALL_ONE
    if argv[1] == "--all":
        # only the files of this point, so that the merged table holds one point
        import glob
        files = sorted(glob.glob(os.path.join(ROOT, "examples", "studies", "*", os.path.basename(_out_c("", point)))))
        merged = os.path.join(ROOT, "validate", f"np0_all{MTAG}" + (f"_{pid}" if point else "") + ".tsv")
        try:
            _merge_c(files, pid, merged)
        except ValueError as e:
            print(f"REFUSED: {e}")
            return 2
        return report_combined(merged, LAM, lams, point)
    st = os.path.abspath(argv[1])
    out = _out_c(st, point)
    if "--report" in argv:
        return report_combined(out, LAM, lams, point)
    if "--classes" in argv or "--tex" in argv:
        print("for a combined model the script measures the set with every coefficient on, and writes "
              "no LaTeX table")
        return 2
    nev = int(argv[argv.index("--nev") + 1]) if "--nev" in argv else 20000
    seed = int(argv[argv.index("--seed") + 1]) if "--seed" in argv else 21
    cores = int(os.environ.get("NP0_CORES", "1"))
    procs = []
    for l in open(os.path.join(st, "processes.txt")):
        l = l.split("#")[0].strip()
        if l:
            procs.append(l)
    if "--settle" in argv:
        if not os.path.exists(out):
            print("no results yet")
            return 1
        try:
            n = _settle_c(out, {l.split("|")[0].strip(): _extras(l) for l in procs})
        except ValueError as e:
            print(f"REFUSED: {e}")
            return 2
        print(f"{out}: the settings of processes.txt written into {n} rows whose settings were unknown")
        return report_combined(out, LAM, lams, point)
    # the process directories of a model other than dim8_is sit in a directory of their own, so that
    # one made with another model is never taken for it
    work = os.path.join(WORK, MNAME)
    os.makedirs(work, exist_ok=True)
    try:
        done = _done_c(out, pid) if os.path.exists(out) else set()
    except ValueError as e:
        print(f"REFUSED: {e}")
        return 2
    failed, ready = 0, []
    for line in procs:
        proc = line.split("|")[0].strip()
        extra = line.split("|")[1].split() if "|" in line else []
        tag = re.sub(r"[^A-Za-z0-9]+", "_", proc.replace("+", "p").replace("-", "m")).strip("_")
        # one MadGraph session writes the three directories, since an import of these models keeps no
        # cached copy and costs as much as the rest of the session
        gens = (("np0", "NP=0"), ("np1", "NP^2==1"), ("np2", "NP^2==2"))
        dirs, log = {}, os.path.join(work, tag + ".log")
        new = [(o, g) for o, g in gens
               if not os.path.exists(os.path.join(work, f"{tag}_{o}", "bin", "generate_events"))]
        if new:
            sc = os.path.join(work, tag + ".mg5")
            open(sc, "w").write(f"import model {MODEL}\n" + "".join(
                f"generate {proc} {g}\noutput {os.path.join(work, f'{tag}_{o}')} -f\n" for o, g in new))
            run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc], log)
        for o, gen in gens:
            d = os.path.join(work, f"{tag}_{o}")
            if not os.path.exists(os.path.join(d, "bin", "generate_events")):
                print(f"[{tag}] {gen}: no output, see {log}", flush=True)
                failed += 1
                continue
            if (o, gen) in new:
                open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
                    (f"run_mode = 2\nnb_core = {cores}\n" if cores > 1 else "run_mode = 0\nnb_core = 1\n")
                    + "automatic_html_opening = False\n")
            dirs[o] = (d, log)
        ready.append((proc, extra, tag, dirs))
    # every name of the point has to be an entry of every card, before any run is made
    if point:
        bad = [(tag, o, _point_missing(_card_names(d), point))
               for proc, extra, tag, dirs in ready for o, (d, _) in sorted(dirs.items())]
        bad = [b for b in bad if b[2]]
        for tag, o, names in bad:
            print(f"[{tag}] {o}: the card has no coefficient {', '.join(names)} of point {pid}, removed by "
                  "a restriction card or misspelt")
        if bad:
            print("nothing was run")
            return 2
    # and every setting of a line of processes.txt has to be an entry of the cards of its process: a
    # cut that the run card does not have would be left out of the run and still be written in the
    # settings column of its rows
    bad = [(tag, o, _unknown_extras(d, extra))
           for proc, extra, tag, dirs in ready for o, (d, _) in sorted(dirs.items())]
    bad = [b for b in bad if b[2]]
    for tag, o, names in bad:
        print(f"[{tag}] {o}: the cards have no entry {', '.join(names)} of its line in processes.txt, "
              "misspelt or not a setting of this process")
    if bad:
        print("nothing was run")
        return 2
    if not os.path.exists(out):
        open(out, "w").write(HEAD_C + "\n")
    elif n_unknown := _upgrade_c(out):
        print(f"{out}: {n_unknown} rows were written before the run settings were recorded, and are "
              "not reused (--settle gives them the settings of processes.txt, when the job that made them "
              "is known to have run with it)")
    for proc, extra, tag, dirs in ready:
        jobs = ([("np0", 0.0)] + [("np0", l) for l in lams] + [("np1", l) for l in lams]
                + [("np2", l) for l in sorted(set(lams + [LAM]))])
        ex = " ".join(sorted(extra)) or NONE          # as _extras records the line
        for o, lam in jobs:
            if (proc, o, f"{lam:g}", str(seed), str(nev), ex, pid) in done or o not in dirs:
                continue
            d, log = dirs[o]
            # every run of a process with one seed, so that the differences the extraction rests on
            # are not swamped by independent fluctuations
            common = [f"nevents={nev}", "ebeam1=6800", "ebeam2=6800", f"iseed={seed}",
                      "hel_recycling=False", "use_syst=False", "dynamical_scale_choice=3"]
            have = set(re.findall(r"=\s*(\w+)", open(os.path.join(d, "Cards", "run_card.dat")).read()))
            # only the script's own settings may be left out when a run card lacks them: the cuts of
            # the line were checked above, and the settings column records every one of them
            common = [a for a in common if a.split("=")[0] in have or a.startswith("hel_recycling")] + extra
            if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d]
                   + common + _settings(d, lam > 0, lam or LAM, point), log):
                print(f"[{tag}] {o} Lam={lam:g}: card error, see {log}", flush=True)
                failed += 1
                continue
            _clear_channels(d)
            before = os.path.getsize(log)
            run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
            r = _xsec(d, open(log, errors="replace").read()[before:])
            if r is None:
                print(f"[{tag}] {o} Lam={lam:g}: MadGraph gave no cross section, see {log}", flush=True)
                failed += 1
                continue
            with open(out, "a") as fh:
                fh.write(f"{proc}\t{o}\t{lam:g}\t{r[0]:.10g}\t{r[1]:.6g}\t{nev}\t{seed}\t{ex}\t{pid}\n")
            print(f"[{tag}] {o} Lam={lam:g} {r[0]:14.8g} +- {r[1]:.3g} pb", flush=True)
    if failed:
        print(f"{failed} runs gave no cross section")
    return report_combined(out, LAM, lams, point) or (1 if failed else 0)


def report_combined(out, lam, lams=None, point=None) -> int:
    """The order 1/Lambda^2 and 1/Lambda^4 terms at the scale lam, from the rows of one process and
    one seed: the shift x1 t and x2 t^2 that the tags miss, beside the tagged runs.  With several
    seeds of a process it also prints their mean and the error of the mean from their spread, which
    is the error to quote, since the propagated one ignores the correlation the seed brings.  The fit
    is through exactly the scales of lams (LAMS by default), and a seed that lacks one of the runs
    _required names is printed as INCOMPLETE, left out, and makes the return nonzero.  The runs of a
    seed are those of one line of processes.txt and one number of events, and rows whose settings are
    unknown are counted and left out.  The rows have to be of one point, the point given (None for
    every coefficient at one), whose settings the M_W lines use."""
    if not os.path.exists(out):
        print("no results yet")
        return 1
    try:
        rows = _rows_c(out)
    except ValueError as e:
        print(f"REFUSED: {e}")
        return 2
    if not rows:
        print("no results yet")
        return 1
    pid, pids = (point.id if point else ALL_ONE), sorted({r[8] for r in rows})
    if len(pids) > 1:
        print(f"REFUSED: {out} mixes the rows of {len(pids)} points ({', '.join(pids)}), and a fit takes "
              "the runs of one point")
        return 2
    if pids != [pid]:
        print(f"REFUSED: {out} holds the rows of point {pids[0]}, and the report is for point {pid}")
        return 2
    sc = sorted(lams or LAMS, reverse=True)            # increasing t
    # the runs of one seed are those of one process line and one number of events, so that runs made
    # with other cuts or other statistics are fitted apart, and rows of unknown settings not at all
    by, unknown = {}, collections.Counter(r[0] for r in rows if r[7] == UNKNOWN)
    for r in rows:
        if r[7] != UNKNOWN:
            lab = r[0] + (f" | {r[7]}" if r[7] != NONE else "") + f", {r[5]} events"
            by.setdefault((lab, r[6]), {})[(r[1], float(r[2]))] = (float(r[3]), float(r[4]))
    tr = (1000.0 / lam) ** 2
    what = ("every coefficient of both sectors at one" if point is None else
            f"point {pid} ({len(point.asg)} coefficients named, every other at zero)")
    print(f"\nt = 1/Lambda^2 in TeV^-2, {what}; X(t) = sigma(NP=0; t) - sigma_SM + sigma(NP^2==1; t), "
          f"solved for x1 and x2 through Lambda = {', '.join(f'{l / 1000:g}' for l in sc[::-1])} TeV; quoted "
          f"at Lambda = {lam / 1000:g} TeV [pb]")
    for p, n in sorted(unknown.items()):
        print(f"UNKNOWN SETTINGS {p}: {n} runs written before the run settings were recorded are left out "
              "(--settle gives them the settings of processes.txt, when the job that made them is known to "
              "have run with it)")
    if not by:
        print("no results with known run settings")
        return 1
    m0 = _mw_on(0)
    seeds, incomplete = {}, 0
    for (p, seed), R in sorted(by.items()):
        miss = [w for k, w in _required(sc, lam) if k not in R]
        if miss:
            print(f"INCOMPLETE {p} (seed {seed}): no {', '.join(miss)}.  This seed is left out of the fit "
                  "and of the mean over seeds")
            incomplete += 1
            continue
        sm = R[("np0", 0.0)]
        ts = [(1000.0 / l) ** 2 for l in sc]
        s0, s1 = [R[("np0", l)] for l in sc], [R[("np1", l)] for l in sc]
        deg = min(len(ts) - 1, 2)
        x = _solve(ts, s0, s1, sm, deg)
        x1, x2 = x[0], x[1]
        one = seeds.setdefault(p, {})
        one.setdefault("x1 t", []).append(x1[0] * tr)
        one.setdefault("x2 t^2", []).append(x2[0] * tr ** 2)
        print(f"\n{p}   seed {seed}   sigma_SM = {sm[0]:.6g} +- {sm[1]:.2g}")
        for l, t in zip(sc, ts):
            mw = _mw_on(l, point)
            print(f"   Lambda = {l / 1000:g} TeV: M_W - M_W0 = {mw - m0:+.4f} GeV, sigma(NP=0) - sigma_SM = "
                  f"{R[('np0', l)][0] - sm[0]:+.5g}, sigma(NP^2==1) = {R[('np1', l)][0]:+.5g}")
        n1 = R.get(("np1", lam))
        print(f"   1/Lambda^2:  x1 t = {x1[0] * tr:+.5g} +- {x1[1] * tr:.2g}"
              f"   (NP=0 part {x1[2] * tr:+.4g}, NP^2==1 part {x1[4] * tr:+.4g})"
              + (f", against NP^2==1 = {n1[0]:+.5g} alone" if n1 else ""))
        print(f"   1/Lambda^4:  x2 t^2 = {x2[0] * tr ** 2:+.5g} +- {x2[1] * tr ** 2:.2g}"
              f"   (NP=0 part {x2[2] * tr ** 2:+.4g} +- {x2[3] * tr ** 2:.2g}, NP^2==1 part {x2[4] * tr ** 2:+.4g}"
              f" +- {x2[5] * tr ** 2:.2g})")
        if deg == 2:
            two = _solve(ts[:2], s0[:2], s1[:2], sm, 1)[1]
            print(f"   the third scale: x3 t^3 = {x[2][0] * tr ** 3:+.3g} +- {x[2][1] * tr ** 3:.2g}, and x2 t^2 from the"
                  f" two smallest t alone = {two[0] * tr ** 2:+.5g} +- {two[1] * tr ** 2:.2g}")
        # NP^2==2 at the target is the tagged term at the shifted mass, which differs from its value
        # at M_W0 by a term of order t^3.  Its runs at the scales give that value too, as the
        # intercept of sigma2/t^2, and with it the t^2 coefficient of the full cross section exactly.
        n2 = R.get(("np2", lam))
        if n2:
            one.setdefault("NP^2==2 + x2 t^2", []).append(n2[0] + x2[0] * tr ** 2)
            print(f"   NP^2==2 = {n2[0]:+.5g} +- {n2[1]:.2g}, and sigma_1/Lambda^4 = NP^2==2 + x2 t^2 = "
                  f"{n2[0] + x2[0] * tr ** 2:+.5g} +- {(n2[1] ** 2 + (x2[1] * tr ** 2) ** 2) ** 0.5:.2g}")
        s2 = [R.get(("np2", l)) for l in sc]
        if all(s2):
            w = _poly_weights(ts, deg)[0]
            v = sum(wi * a[0] / t ** 2 for wi, a, t in zip(w, s2, ts))
            e = sum((wi * a[1] / t ** 2) ** 2 for wi, a, t in zip(w, s2, ts)) ** 0.5
            one.setdefault("NP^2==2 at M_W0 + x2 t^2", []).append((v + x2[0]) * tr ** 2)
            print(f"   NP^2==2 at M_W0 (sigma2/t^2 at t = 0, times t^2) = {v * tr ** 2:+.5g} +- {e * tr ** 2:.2g}, and the "
                  f"t^2 term of the full cross section = {(v + x2[0]) * tr ** 2:+.5g} +- "
                  f"{(e ** 2 + x2[1] ** 2) ** 0.5 * tr ** 2:.2g}")
    for p, one in sorted(seeds.items()):
        if len(one["x1 t"]) < 2:
            continue
        print(f"\n{p}: mean over {len(one['x1 t'])} seeds, error of the mean from their spread")
        for k, v in one.items():
            if len(v) > 1:
                mean = sum(v) / len(v)
                err = (sum((u - mean) ** 2 for u in v) / (len(v) - 1) / len(v)) ** 0.5
                print(f"   {k:<26s} {mean:+.5g} +- {err:.2g}   ({len(v)} seeds)")
    if incomplete:
        print(f"\n{incomplete} seeds INCOMPLETE, which count once their missing runs are made")
    return 1 if incomplete else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
