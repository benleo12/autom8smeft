#!/usr/bin/env python3
"""The part of the 1/Lambda^4 interference that carries no coupling order.

    validate/np0_shift.py <study dir> [--nev 5000] [--classes] [--report] [--lam 3000]

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
setting and only the param card changes between runs.

Without --classes only the all-coefficients-on bracket is measured, one number per process.
With --classes the 21 class cards are measured too, which is only worth doing for a process whose
Standard-Model diagram count is small.  --report prints the table of a study from its
np0_shift.tsv without running anything, and --tex FILE also writes it as a LaTeX table.  Given
--all in place of a study directory, the script merges the np0_shift.tsv of every study into
validate/np0_all.tsv and reports on the merged table, again with an optional --tex FILE.  --lam sets
the scale of the tagged rows the bracket is quoted against (default 3000, the studies' Lam=).
"""
from __future__ import annotations

import json
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
# to first order.  Lam=1000 with every coefficient at one lowers the M_W of dim8_is by 0.50 GeV, a
# shift the Monte Carlo resolves, and the derivative it gives times the delta M_W^2 of any other
# setting is the bracket there (the paper's 3 TeV number, where M_W moves by -6 MeV).
LAM_BRACKET = 1000


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
        out = subprocess.run([py, os.path.join(ROOT, "validate", "eval_ufo_params.py"), MODEL]
                             + settings.split() + ["--show=MW"], capture_output=True, text=True).stdout
        m = re.search(r"^MW\s*=\s*([-\d.eE+]+)", out, re.M)
        _mw_cache[settings] = float(m.group(1)) if m else float("nan")
    return _mw_cache[settings]


def run(cmd, log, cwd=None):
    with open(log, "a") as fh:
        fh.write("\n$ " + " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else "") + "\n")
        return subprocess.run(NICE + cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, cwd=cwd, check=False).returncode


def main(argv) -> int:
    global LAM
    LAM = float(argv[argv.index("--lam") + 1]) if "--lam" in argv else 3000.0
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
    with_classes = "--classes" in argv
    procs = []
    for l in open(os.path.join(st, "processes.txt")):
        l = l.split("#")[0].strip()
        if l:
            procs.append(l)
    os.makedirs(WORK, exist_ok=True)
    if not os.path.exists(out):
        open(out, "w").write("process\tset\tsigma_pb\terror_pb\tnevents\n")
    done = {tuple(l.split("\t")[:2]) for l in open(out).read().split("\n")[1:] if l}
    failed = 0
    for line in procs:
        proc = line.split("|")[0].strip()
        extra = line.split("|")[1].split() if "|" in line else []
        tag = re.sub(r"[^A-Za-z0-9]+", "_", proc.replace("+", "p").replace("-", "m")).strip("_")
        d = os.path.join(WORK, tag)
        log = os.path.join(WORK, tag + ".log")
        if not os.path.exists(os.path.join(d, "bin", "generate_events")):
            sc = os.path.join(WORK, tag + ".mg5")
            open(sc, "w").write(f"import model {MODEL}\ngenerate {proc} NP=0\noutput {d} -f\n")
            run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc], log)
            if not os.path.exists(os.path.join(d, "bin", "generate_events")):
                print(f"[{tag}] no output, see {log}", flush=True)
                failed += 1
                continue
            open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
                "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
        jobs = [("off", ["dim8_all=0"]), ("on", ["dim8_all=1"])]
        if with_classes:
            jobs += [(f"cls{c}", ["dim8_all=0"] + [f"{w}=1" for w in class_wcs(c)]) for c in range(1, 22)]
        for name, sets in jobs:
            if (proc, name) in done:
                continue
            # H_T/2, the scale MadGraph sets for the tagged interference, so that the bracket and the
            # interference it is added to share one scale
            common = [f"nevents={nev}", "ebeam1=6800", "ebeam2=6800",
                      "hel_recycling=False", "use_syst=False", "dynamical_scale_choice=3"] + extra
            have = set(re.findall(r"=\s*(\w+)", open(os.path.join(d, "Cards", "run_card.dat")).read()))
            common = [a for a in common if a.split("=")[0] in have or a.startswith("hel_recycling")]
            if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d]
                   + common + sets + [f"Lam={LAM_BRACKET}"], log):
                print(f"[{tag}] {name}: card error, see {log}", flush=True)
                failed += 1
                continue
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
    # The tagged interference of the same process and the SAME model, for context.  A study's
    # results.tsv holds the rows of the model it was run with, and the rows of another model, when
    # kept, are in results_<model>.tsv beside it (the dim8_is rows since the studies moved to
    # dim8_mw).  A bracket set against the tagged term of the other scheme would be meaningless.
    # The tagged rows give the setting the bracket is wanted at (the study's Lam=, with the full model
    # or one class on), and their interference is quoted at that same setting, never moved to another
    # scale.
    tagged = {}
    import glob as _g
    dirs = (sorted(_g.glob(os.path.join(study, "*", ""))) if multi and study else ([study] if study else []))
    for sd in dirs:
        for rp in (os.path.join(sd, "results.tsv"), os.path.join(sd, f"results_{MNAME}.tsv")):
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
          "the set at one)")
    print(f"{'process':<22s} {'set':<6s} {'dM_W pair':>10s} {'dsig/dM_W^2':>12s} {'Lam':>5s} {'dM_W':>8s} "
          f"{'bracket':>11s} {'error':>9s} {'tagged':>11s} {'total':>11s}  [pb, GeV]")
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
            lamv = re.search(r"Lam=([\d.]+)", t[2]).group(1) if t and "Lam=" in t[2] else None
            if not lamv:
                print(f"{p:<22s} {s:<6s} {m1 - m0:>+10.4f} {der:>+12.4g}   no tagged row at Lam={lam:g} to quote it at")
                continue
            mt = mw(s, t[2])
            d, de = der * (mt ** 2 - m0 ** 2), dere * abs(mt ** 2 - m0 ** 2)
            print(f"{p:<22s} {s:<6s} {m1 - m0:>+10.4f} {der:>+12.4g} {float(lamv) / 1000:>4g}T "
                  f"{mt - m0:>+8.2e} {d:>+11.4g} {de:>9.2g} {t[0]:>11.4g} {t[0] + d:>11.4g}"
                  + ("" if abs(d) > 2 * de else "   (consistent with zero)"))
            if s == "on":
                lines.append((p, off, v, d, de, t, float(lamv)))
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


if __name__ == "__main__":
    sys.exit(main(sys.argv))
