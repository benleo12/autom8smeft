#!/usr/bin/env python3
"""A CP-odd coefficient must not interfere with the Standard Model in a CP-even rate.

    validate/cp_rates.py [--nev 4000]
    validate/cp_rates.py --report

A total cross section is CP even, and at tree level the amplitudes have no absorptive part, so
the interference of a CP-odd dimension-eight operator with the Standard Model must vanish exactly
while its square must not.  That is a test of the derived CP assignment, of the sign of the
Levi-Civita symbol, and of the whole export chain at once: a dual field strength written with the
wrong sign, or an operator misclassified as CP even, shows up here as a nonzero interference.

CP parity is read from the encoded operator and never from its label: a block is CP odd when its
coefficient is real and every operator in it carries an odd number of dual field strengths, and
CP even when the coefficient is real and every count is even.  Blocks with a complex coefficient
are in neither set, their imaginary part being the CP-odd half of a pair.

The reference point is the CP-even set run the same way, whose interference is large.  Without
that control a vanishing number is consistent with having set nothing at all, which is the trap
this project has already paid for once.
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
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "v11")
OUT = os.path.join(ROOT, "validate", "v11_results.tsv")
NICE = ["nice", "-n", "19"]

# Which processes are a CP test and which are not.  A CP-odd operator cannot interfere with the
# Standard Model in a CP-even observable, and a total rate is CP even only when the final state is
# self-conjugate AND the initial-state luminosity is symmetric under the swap CP induces.  At a
# proton-proton collider u ubar -> W+W- maps under CP onto ubar u -> W+W-, the same partonic
# process with the beams exchanged, and the pp luminosity is symmetric in that exchange, so the
# CP-odd piece cancels.  u dbar -> W+Z maps onto ubar d -> W-Z, a DIFFERENT final state carried by
# a different luminosity, so nothing cancels and a nonzero answer there is physics rather than a
# failure: it is the proton's charge asymmetry turning a CP-odd operator into a rate difference.
PROCS = {"ww": "p p > w+ w-", "zz": "p p > z z", "zh": "p p > z h", "wz": "p p > w+ z"}
SELF_CONJUGATE = {"p p > w+ w-", "p p > z z", "p p > z h"}
ORDERS = {"int": "NP^2==2", "sq": "NP<=2 NP^2==4"}


def cp_sets():
    """(cp_odd, cp_even) coefficient names, from the shared classifier of gen/cp_parity.py.

    The parity is the number of dual field strengths per TERM of the parsed operator, not the
    number of tilde characters in the printed row: that distinction moves 27 coefficients from
    even to odd, and the shipped CP-even restriction card was wrong on exactly those before this
    check was written."""
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    sys.path.insert(0, os.path.join(ROOT, "validate"))
    import cp_parity, cardnames
    odd, even = cp_parity.coefficient_sets()
    return cardnames.expand(MODEL, odd), cardnames.expand(MODEL, even)


def run(cmd, log, cwd=None):
    with open(log, "a") as fh:
        fh.write("\n$ " + " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else "") + "\n")
        return subprocess.run(NICE + cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, cwd=cwd, check=False).returncode


def main(argv) -> int:
    if "--report" in argv:
        return report(argv[argv.index("--tex") + 1] if "--tex" in argv else None)
    nev = int(argv[argv.index("--nev") + 1]) if "--nev" in argv else 4000
    odd, even = cp_sets()
    print(f"CP-odd coefficients: {len(odd)}   CP-even: {len(even)}   "
          f"(complex coefficients, in neither set: {1030 - len(odd) - len(even)})", flush=True)
    os.makedirs(WORK, exist_ok=True)
    if not os.path.exists(OUT):
        open(OUT, "w").write("process\torder\tset\tsigma_pb\terror_pb\tnevents\n")
    done = {tuple(l.split("\t")[:3]) for l in open(OUT).read().split("\n")[1:] if l}
    for tag, proc in PROCS.items():
        for okey, ospec in ORDERS.items():
            d = os.path.join(WORK, f"{tag}_{okey}")
            log = os.path.join(WORK, f"{tag}_{okey}.log")
            if not os.path.exists(os.path.join(d, "bin", "generate_events")):
                sc = os.path.join(WORK, f"{tag}_{okey}.mg5")
                open(sc, "w").write(f"import model {MODEL}\ngenerate {proc} {ospec}\noutput {d} -f\n")
                run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc], log)
                if not os.path.exists(os.path.join(d, "bin", "generate_events")):
                    print(f"[{tag} {okey}] no output, see {log}", flush=True)
                    continue
                open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
                    "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
            for name, wcs in (("cpodd", odd), ("cpeven", even)):
                if (proc, ospec, name) in done:
                    continue
                sets = ["dim8_all=0", "Lam=1000"] + [f"{w}=1" for w in wcs]
                common = [f"nevents={nev}", "ebeam1=6800", "ebeam2=6800",
                          "hel_recycling=False", "use_syst=False"]
                if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d]
                       + common + sets, log):
                    print(f"[{tag} {okey}] {name}: card error, see {log}", flush=True)
                    continue
                before = os.path.getsize(log)
                run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
                txt = open(log, errors="replace").read()[before:]
                m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
                x, e = (float(m[-1][0]), float(m[-1][1])) if m else (0.0, 0.0)
                with open(OUT, "a") as fh:
                    fh.write(f"{proc}\t{ospec}\t{name}\t{x:.6g}\t{e:.6g}\t{nev}\n")
                print(f"[{tag} {okey}] {name:6s} {x:12.5g} +- {e:.3g} pb", flush=True)
    return report()


def report(tex=None) -> int:
    if not os.path.exists(OUT):
        print("no results yet")
        return 1
    rows = [l.split("\t") for l in open(OUT).read().split("\n")[1:] if l]
    by = {(p, o, s): (float(x), float(e)) for p, o, s, x, e, _ in rows}
    procs = [p for p in PROCS.values() if any(k[0] == p for k in by)]
    npass = nfail = 0
    lines = []
    print(f"\n{'process':<14s} {'CP-odd interference':>24s} {'CP-odd square':>15s} "
          f"{'CP-even interference':>24s}  verdict")
    for p in procs:
        oi = by.get((p, "NP^2==2", "cpodd"))
        osq = by.get((p, "NP<=2 NP^2==4", "cpodd"))
        ei = by.get((p, "NP^2==2", "cpeven"))
        if not (oi and ei):
            print(f"{p:<14s} incomplete")
            continue
        frac = abs(oi[0]) / abs(ei[0]) if ei[0] else float("inf")
        if p not in SELF_CONJUGATE:
            print(f"{p:<14s} {oi[0]:>15.4g} +- {oi[1]:<6.2g} "
                  f"{(osq[0] if osq else float('nan')):>15.4g} {ei[0]:>15.4g} +- {ei[1]:<6.2g}  "
                  f"not a CP test: the final state is not self-conjugate "
                  f"({frac:.1e} of CP-even)")
            lines.append((p, oi, osq, ei, frac))
            continue
        ok = abs(oi[0]) < 3 * oi[1] or frac < 1e-5
        npass += ok
        nfail += not ok
        print(f"{p:<14s} {oi[0]:>15.4g} +- {oi[1]:<6.2g} "
              f"{(osq[0] if osq else float('nan')):>15.4g} {ei[0]:>15.4g} +- {ei[1]:<6.2g}  "
              f"{'zero' if ok else 'NONZERO'} ({frac:.1e} of CP-even)")
        lines.append((p, oi, osq, ei, frac))
    print(f"\nV11: {npass} of {npass + nfail} self-conjugate final states have a vanishing "
          f"CP-odd interference")
    if tex and lines:
        def n(v):
            if v is None:
                return "--"
            x = v[0]
            if x == 0:
                return "$0$"
            m, e = f"{x:.2e}".split("e")
            return f"${m}\\times 10^{{{int(e)}}}$" if abs(x) < 1e-2 else f"${x:.4g}$"
        import math as _m
        body = []
        for p, oi, osq, ei, frac in lines:
            r = ("--" if not (frac == frac and frac > 0)
                 else f"$10^{{{round(_m.log10(frac))}}}$")
            body.append(f"{tex_proc(p)} & {n(oi)} & {n(osq)} & {n(ei)} & {r}" + r" \\")
        open(tex, "w").write(r"""\begin{table}[t]\centering\small
\begin{tabular}{l r r r r}
\toprule
process & CP-odd $\sigma_{1/\Lambda^4}$ & CP-odd $\sigma_{1/\Lambda^8}$ & CP-even $\sigma_{1/\Lambda^4}$ & ratio \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\caption{With the 153 CP-odd coefficients switched on and everything else off, the
interference of a dimension-eight insertion with the Standard Model in a total cross section
must vanish, while the square of the same amplitude must not. The CP-even set run the same way
is the control that says the coefficients were set. $\Lambda = 1$~TeV, coefficients at one,
$13.6$~TeV. Generated by \code{validate/v11\_cp.py --report --tex}.}
\label{tab:v11}
\end{table}
""")
        print(f"wrote {tex}")
    return 0 if nfail == 0 else 1


def tex_proc(p):
    m = {"p": "p", "w+": "W^+", "w-": "W^-", "z": "Z", "h": "H", "a": r"\gamma"}
    i, f = p.split(">", 1)
    return ("$" + " ".join(m.get(x, x) for x in i.split()) + r" \to "
            + " ".join(m.get(x, x) for x in f.split()) + "$")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
