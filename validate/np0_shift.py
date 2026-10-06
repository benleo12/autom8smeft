#!/usr/bin/env python3
"""The part of the 1/Lambda^4 interference that carries no coupling order.

    validate/np0_shift.py <study dir> [--nev 5000] [--classes] [--report]

MadGraph counts interaction orders on couplings, and a mass is not a coupling.  In the
{alpha, M_Z, G_F} scheme a dimension-eight coefficient shifts the W mass, which sits in a
propagator and therefore enters EVERY order including NP=0, while every coupling shift (gauge
couplings, vev, Yukawas, Higgs quartic, all written as tagged series since 2026-10-03) appears in
NP^2==2 as a new vertex would.  The complete order 1/Lambda^4 cross section is

    sigma_{1/Lambda^4} = sigma(NP^2==2, c) + [ sigma(NP=0, c) - sigma(NP=0, 0) ]

and this script measures the bracket, which the class tables of the studies do not contain.  It
is cheap: the NP=0 amplitude is the Standard-Model diagram set, so one process directory serves
every coefficient setting and only the param card changes between runs.

Without --classes only the all-coefficients-on bracket is measured, one number per process.
With --classes the 21 class cards are measured too, which is only worth doing for a process whose
Standard-Model diagram count is small.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
PY = "python3.11"
MODEL = os.path.join(ROOT, "models", "dim8_is")
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "np0")
NICE = ["nice", "-n", "19"]


def class_wcs(n):
    """The param-card entries of a class: a complex coefficient is a Re and an Im entry, not the
    base name the catalogue carries."""
    sys.path.insert(0, os.path.join(ROOT, "validate"))
    import cardnames
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    return cardnames.expand(MODEL, [w for e in idx if e["cls"] == n for w in e["wcs"]])


def run(cmd, log, cwd=None):
    with open(log, "a") as fh:
        fh.write("\n$ " + " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else "") + "\n")
        return subprocess.run(NICE + cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, cwd=cwd, check=False).returncode


def main(argv) -> int:
    if argv[1] == "--all":
        # one table over every study that has been measured, which is what the paper carries
        import glob
        studies = sorted(glob.glob(os.path.join(ROOT, "examples", "studies", "*", "np0_shift.tsv")))
        merged = os.path.join(ROOT, "validate", "np0_all.tsv")
        seen, out = set(), ["process\tset\tsigma_pb\terror_pb\tnevents"]
        for f in studies:
            for l in open(f).read().split("\n")[1:]:
                if l and tuple(l.split("\t")[:2]) not in seen:
                    seen.add(tuple(l.split("\t")[:2]))
                    out.append(l)
        open(merged, "w").write("\n".join(out) + "\n")
        tex = argv[argv.index("--tex") + 1] if "--tex" in argv else None
        # the tagged interference comes from whichever study holds the process
        return report(merged, tex, os.path.join(ROOT, "examples", "studies"), multi=True)
    st = os.path.abspath(argv[1])
    out = os.path.join(st, "np0_shift.tsv")
    if "--report" in argv:
        return report(out, argv[argv.index("--tex") + 1] if "--tex" in argv else None, st)
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
                continue
            open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
                "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
        jobs = [("off", ["dim8_all=0"]), ("on", ["dim8_all=1"])]
        if with_classes:
            jobs += [(f"cls{c}", ["dim8_all=0"] + [f"{w}=1" for w in class_wcs(c)]) for c in range(1, 22)]
        for name, sets in jobs:
            if (proc, name) in done:
                continue
            common = [f"nevents={nev}", "ebeam1=6800", "ebeam2=6800",
                      "hel_recycling=False", "use_syst=False"] + extra
            have = set(re.findall(r"=\s*(\w+)", open(os.path.join(d, "Cards", "run_card.dat")).read()))
            common = [a for a in common if a.split("=")[0] in have or a.startswith("hel_recycling")]
            if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d]
                   + common + sets + ["Lam=1000"], log):
                print(f"[{tag}] {name}: card error, see {log}", flush=True)
                continue
            before = os.path.getsize(log)
            run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
            txt = open(log, errors="replace").read()[before:]
            m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
            x, e = (float(m[-1][0]), float(m[-1][1])) if m else (0.0, 0.0)
            with open(out, "a") as fh:
                fh.write(f"{proc}\t{name}\t{x:.6g}\t{e:.6g}\t{nev}\n")
            print(f"[{tag}] NP=0 {name:7s} {x:12.5g} +- {e:.3g} pb", flush=True)
    return report(out, None, st)


def report(out, tex=None, study=None, multi=False) -> int:
    if not os.path.exists(out):
        print("no results yet")
        return 1
    rows = [l.split("\t") for l in open(out).read().split("\n")[1:] if l]
    by = {(p, s): (float(x), float(e)) for p, s, x, e, _ in rows}
    # the tagged interference of the same process, for context
    tagged = {}
    import glob as _g
    for rp in (_g.glob(os.path.join(study, "*", "results.tsv")) if multi and study
               else ([os.path.join(study, "results.tsv")] if study else [])):
        if os.path.exists(rp):
            R = [l.rstrip("\n").split("\t") for l in open(rp)]
            h, R = R[0], R[1:]
            ci = {k: i for i, k in enumerate(h)}
            for r in R:
                if r[ci["order"]] == "NP^2==2" and "-cls" not in r[ci["model"]] \
                   and "-op_" not in r[ci["model"]] and re.match(r"^-?[\d.]", r[ci["sigma_pb"]]):
                    tagged[r[ci["process"]].strip()] = (float(r[ci["sigma_pb"]]),
                                                        float(r[ci["error_pb"]]))
    print(f"\n{'process':<22s} {'set':<8s} {'NP=0':>12s} {'bracket':>12s} {'error':>9s} "
          f"{'tagged':>12s} {'total':>12s}")
    lines = []
    for p in sorted({k[0] for k in by}):
        off = by.get((p, "off"))
        if not off:
            continue
        for s in ["on"] + [f"cls{c}" for c in range(1, 22)]:
            v = by.get((p, s))
            if not v:
                continue
            d = v[0] - off[0]
            de = (v[1] ** 2 + off[1] ** 2) ** 0.5
            t = tagged.get(p) if s == "on" else None
            print(f"{p:<22s} {s:<8s} {v[0]:>12.5g} {d:>+12.4g} {de:>9.3g} "
                  + (f"{t[0]:>12.4g} {t[0]+d:>12.4g}" if t else " " * 25)
                  + ("" if abs(d) > 2 * de else "   (consistent with zero)"))
            if s == "on" and t:
                lines.append((p, off, v, d, de, t))
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
                for p, off, v, d, de, t in lines]
        open(tex, "w").write(r"""\begin{table}[t]\centering\footnotesize
\begin{tabular}{@{}l r r r r@{}}
\toprule
process & bracket [pb] & $\sigma(\texttt{NP\^{}2==2})$ [pb] & total [pb] & ratio \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\caption{The part of order $1/\Lambda^4$ that carries no coupling order, \cref{eq:np0}. ``bracket''
is $\sigma(\mathrm{NP}=0; C) - \sigma(\mathrm{NP}=0; 0)$ with all 674 coefficients at one and
$\Lambda = 1$~TeV, the shift of the Standard-Model bin caused by the $W$ mass, the vacuum
expectation value and the Yukawa couplings moving with the coefficients. It is not in the
$\texttt{NP\^{}2==2}$ column and has to be added to it. Generated by
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
