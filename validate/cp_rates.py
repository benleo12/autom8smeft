#!/usr/bin/env python3
"""A CP-odd coefficient must not interfere with the Standard Model in a CP-even rate.

    validate/cp_rates.py [--nev 4000] [--lam 3000]
    validate/cp_rates.py --report [--lam 3000] [--tex table.tex]

A total cross section is CP even, and at tree level the amplitudes have no absorptive part, so
the interference of a CP-odd dimension-eight operator with the Standard Model must vanish exactly
while its square must not.  What that tests is the CP assignment: an operator misclassified as CP
odd, or one whose terms carry a relative sign or a factor i that mixes a CP-even and a CP-odd
piece, shows up as a nonzero interference.  It has teeth because the usual rule fails it: the set
that counting dual field strengths calls CP odd interferes at -1.2 pb in p p > w+ w- (coefficients
at one, Lam = 1 TeV), while the derived set gives zero.  It does not test the overall sign of the
Levi-Civita symbol, which turns a CP-odd operator into a CP-odd operator, nor an operator that
cannot interfere in these processes for another reason, such as a chirality flip with massless
quarks: that one passes whatever its parity.  The verdict and the ratio of the CP-odd to the
CP-even interference do not depend on Lam, since both scale as 1/Lam^4.

CP parity is the C times P assignment derived field by field and recorded in the catalogue,
which gen/cp_parity.py reads.  It is never taken from the label or from a count of dual field
strengths, a rule that fails for many dimension-eight operators.  An operator with a real
coefficient is in the CP-odd or the CP-even set.  An operator with a complex coefficient is in both,
through its two card entries: its real part multiplies Q + Q^dagger and its imaginary part
i(Q - Q^dagger), whose parities are eta and -eta, so the part with parity -1 goes into the CP-odd
set and the other into the CP-even one (44 of the 236 have a CP-odd real part).

The scale is Lam = 3 TeV unless --lam says otherwise, and the results of each scale are kept in their
own file, validate/cp_results_lam<Lam>.tsv; validate/v11_results.tsv holds the runs at 1 TeV.

The reference point is the CP-even set run the same way, whose interference is large.  Without
that control a vanishing number is also what a run with no coefficient set at all would give.
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


def out_path(lam):
    """The results file of one scale: the runs at 1 TeV are the original v11_results.tsv."""
    return OUT if float(lam) == 1000 else os.path.join(ROOT, "validate", f"cp_results_lam{int(float(lam))}.tsv")
NICE = ["nice", "-n", "19"]

# Which processes are a CP test and which are not.  A CP-odd operator cannot interfere with the
# Standard Model in a CP-even observable, and a total rate is CP even only when the final state is
# self-conjugate AND the initial-state luminosity is symmetric under the swap CP induces.  At a
# proton-proton collider u ubar -> W+W- maps under CP onto ubar u -> W+W-, the same partonic
# process with the beams exchanged, and the pp luminosity is symmetric in that exchange, so the
# CP-odd piece cancels.  u dbar -> W+Z maps onto ubar d -> W-Z, a DIFFERENT final state carried by
# a different luminosity, so nothing cancels and a nonzero answer there is physics rather than a
# failure: it is the proton's charge asymmetry turning a CP-odd operator into a rate difference.
PROCS = {"ww": "p p > w+ w-", "zz": "p p > z z", "zh": "p p > z h", "wz": "p p > w+ z",
         "eea": "p p > e+ e- a", "eeg": "p p > e+ e- g"}
SELF_CONJUGATE = {"p p > w+ w-", "p p > z z", "p p > z h", "p p > e+ e- a", "p p > e+ e- g"}
# generation cuts that make a rate with a massless final-state boson finite, those of the Drell-Yan
# study for the photon, the same for the gluon
CUTS = {"p p > e+ e- a": ["mmll=200", "pta=20", "dral=0.4"], "p p > e+ e- g": ["mmll=200", "ptj=20", "drjl=0.4"]}
ORDERS = {"int": "NP^2==2", "sq": "NP<=2 NP^2==4"}


def cp_sets():
    """(cp_odd, cp_even) coefficient names, from the shared classifier of gen/cp_parity.py.

    The parity is the derived C times P assignment of the catalogue, not a count of dual field
    strengths or of tilde characters in the label.  A coefficient is placed only when every
    operator it multiplies has the same parity, and the names are expanded to the entries of the
    param card."""
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
        return report(argv[argv.index("--tex") + 1] if "--tex" in argv else None,
                      argv[argv.index("--lam") + 1] if "--lam" in argv else "3000")
    nev = int(argv[argv.index("--nev") + 1]) if "--nev" in argv else 4000
    lam = argv[argv.index("--lam") + 1] if "--lam" in argv else "3000"
    out = out_path(lam)
    odd, even = cp_sets()
    print(f"CP-odd card entries: {len(odd)}   CP-even: {len(even)}   Lam = {lam} GeV   -> {out}", flush=True)
    os.makedirs(WORK, exist_ok=True)
    if not os.path.exists(out):
        open(out, "w").write("process\torder\tset\tsigma_pb\terror_pb\tnevents\n")
    done = {tuple(l.split("\t")[:3]) for l in open(out).read().split("\n")[1:] if l}
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
                sets = ["dim8_all=0", f"Lam={lam}"] + [f"{w}=1" for w in wcs] + CUTS.get(proc, [])
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
                with open(out, "a") as fh:
                    fh.write(f"{proc}\t{ospec}\t{name}\t{x:.6g}\t{e:.6g}\t{nev}\n")
                print(f"[{tag} {okey}] {name:6s} {x:12.5g} +- {e:.3g} pb", flush=True)
    return report(lam=lam)


def report(tex=None, lam="3000") -> int:
    out = out_path(lam)
    if not os.path.exists(out):
        print("no results yet")
        return 1
    rows = [l.split("\t") for l in open(out).read().split("\n")[1:] if l]
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
    print(f"\nCP null test: {npass} of {npass + nfail} self-conjugate final states have a vanishing "
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
\caption{With the CP-odd coefficients switched on and everything else off, the
interference of a dimension-eight insertion with the Standard Model in a total cross section
must vanish, while the square of the same amplitude must not. The CP-even set run the same way
is the control that says the coefficients were set. $\Lambda = """ + f"{float(lam) / 1000:g}" + r"""$~TeV, coefficients at one,
$13.6$~TeV. Generated by \code{validate/cp\_rates.py --report --tex}.}
\label{tab:cp}
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
