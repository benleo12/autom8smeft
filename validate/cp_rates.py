#!/usr/bin/env python3
"""A CP-odd coefficient must not interfere with the Standard Model in a CP-even rate.

    validate/cp_rates.py [--nev 4000] [--lam 3000] [--procs ww,zz,...]
    validate/cp_rates.py --report [--lam 3000] [--tex table.tex]

A total cross section summed over a final state and its CP conjugate is CP even, so the
interference of a CP-odd dimension-eight operator with the Standard Model must vanish there while
its square must not (which final states qualify at a proton-proton collider is set out at PROCS
below).  What that tests is the CP assignment: an operator misclassified as CP
odd, or one whose terms carry a relative sign or a factor i that mixes a CP-even and a CP-odd
piece, shows up as a nonzero interference.  It has teeth because the usual rule fails it: the set
that counting dual field strengths calls CP odd interferes at -15.1 fb in p p > w+ w- (models/dim8_mw,
coefficients at one, Lam = 3 TeV, validate/cp_probe.py), while the derived set gives zero.  It does not test the overall sign of the
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

The model is models/dim8_mw, the {MW, MZ, GF} scheme, unless DIM8_MODEL names another.  The scale
is Lam = 3 TeV unless --lam says otherwise.  The results of each model and scale have their own file,
validate/cp_results_<model>_lam<Lam>.tsv, except those of models/dim8_is, which keep the names they
had when it was the default: validate/cp_results_lam<Lam>.tsv, and validate/v11_results.tsv at 1 TeV.

The reference point is the CP-even set run the same way, whose interference is large.  Without
that control a vanishing number is also what a run with no coefficient set at all would give.

--procs runs only the processes of those tags in PROCS, so that several runs side by side share the
work: each process has its own directories, and each run skips the rows that the results file holds
when it starts and appends its own.
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
MODEL = os.environ.get("DIM8_MODEL", os.path.join(ROOT, "models", "dim8_mw"))
# another model (DIM8_MODEL=models/dim8_mw) keeps its own process directories and results files
MTAG = "" if os.path.basename(MODEL.rstrip("/")) == "dim8_is" else "_" + os.path.basename(MODEL.rstrip("/"))
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "v11" + MTAG)
OUT = os.path.join(ROOT, "validate", "v11_results.tsv")


def out_path(lam):
    """The results file of one scale: the runs at 1 TeV are the original v11_results.tsv."""
    if float(lam) == 1000 and not MTAG:
        return OUT
    return os.path.join(ROOT, "validate", f"cp_results{MTAG}_lam{int(float(lam))}.tsv")
NICE = ["nice", "-n", "19"]

# Which processes are a CP test and which are not.  In one partonic channel the CP-odd interference
# is half the rate difference between the channel and its CP conjugate, sigma(i -> f) minus
# sigma(ibar -> fbar).  MadGraph's propagators carry the widths, so the amplitudes have an absorptive
# part and that difference need not vanish channel by channel.  It cancels in the total rate when
# the conjugate channel is the same process: u ubar -> W+W- maps under CP onto ubar u -> W+W-, the
# same partonic process with the beams exchanged, and the pp luminosity is symmetric in that
# exchange.  u dbar -> W+Z maps onto ubar d -> W-Z, a different final state, so nothing cancels and
# W+Z is not a test.  Its CP-odd interference is the absorptive part of the s-channel W propagator,
# linear in the W width: with the derived CP-odd set on models/dim8_mw at Lam = 3 TeV it is
# 1.480e-5 +- 0.009e-5 pb at Gamma_W = 2.085 GeV, 2.961e-5 +- 0.019e-5 pb at twice that, and
# -1.9e-19 +- 2.5e-19 pb at Gamma_W = 0 (2026-10-29).  Without the width each channel gives zero
# on its own, so the different u dbar and ubar d luminosities do not produce it.
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
    import basis, cp_parity, cardnames
    odd, even = cp_parity.coefficient_sets(basis.of_model(MODEL))
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
    tags = argv[argv.index("--procs") + 1].split(",") if "--procs" in argv else list(PROCS)
    if set(tags) - set(PROCS):
        print(f"unknown process tags {sorted(set(tags) - set(PROCS))}, the tags are {' '.join(PROCS)}")
        return 2
    odd, even = cp_sets()
    print(f"CP-odd card entries: {len(odd)}   CP-even: {len(even)}   Lam = {lam} GeV   -> {out}", flush=True)
    os.makedirs(WORK, exist_ok=True)
    if not os.path.exists(out):
        open(out, "w").write("process\torder\tset\tsigma_pb\terror_pb\tnevents\n")
    done = {tuple(l.split("\t")[:3]) for l in open(out).read().split("\n")[1:] if l}
    failed = 0
    for tag, proc in PROCS.items():
        if tag not in tags:
            continue
        for okey, ospec in ORDERS.items():
            d = os.path.join(WORK, f"{tag}_{okey}")
            log = os.path.join(WORK, f"{tag}_{okey}.log")
            if not os.path.exists(os.path.join(d, "bin", "generate_events")):
                sc = os.path.join(WORK, f"{tag}_{okey}.mg5")
                open(sc, "w").write(f"import model {MODEL}\ngenerate {proc} {ospec}\noutput {d} -f\n")
                run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc], log)
                if not os.path.exists(os.path.join(d, "bin", "generate_events")):
                    print(f"[{tag} {okey}] no output, see {log}", flush=True)
                    failed += 2
                    continue
                open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
                    "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
            for name, wcs in (("cpodd", odd), ("cpeven", even)):
                if (proc, ospec, name) in done:
                    continue
                sets = ["dim8_all=0", f"Lam={lam}"] + [f"{w}=1" for w in wcs] + CUTS.get(proc, [])
                # The channels of MadGraph's phase-space integration are diagrams with three-point
                # vertices, weighted by default by their squared amplitudes.  With the light fermions
                # massless the only such diagrams of a square of CP-odd operators can all vanish (a
                # Higgs that couples to nothing in the beams) while the contact diagrams do not, and
                # the run stops ("All amp2 are zero but not the total matrix-element").  Strategy 2
                # weights a channel by its propagators alone, whatever the couplings.
                common = [f"nevents={nev}", "ebeam1=6800", "ebeam2=6800",
                          "hel_recycling=False", "use_syst=False", "sde_strategy=2"]
                if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d]
                       + common + sets, log):
                    print(f"[{tag} {okey}] {name}: card error, see {log}", flush=True)
                    failed += 1
                    continue
                before = os.path.getsize(log)
                run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
                txt = open(log, errors="replace").read()[before:]
                m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
                # a run that stopped has no cross section, and no row: it is run again next time,
                # and the report counts the process as incomplete rather than as a zero
                if not m or "interrupted with error" in txt:
                    print(f"[{tag} {okey}] {name}: MadGraph gave no cross section, see {log}", flush=True)
                    failed += 1
                    continue
                x, e = float(m[-1][0]), float(m[-1][1])
                with open(out, "a") as fh:
                    fh.write(f"{proc}\t{ospec}\t{name}\t{x:.6g}\t{e:.6g}\t{nev}\n")
                print(f"[{tag} {okey}] {name:6s} {x:12.5g} +- {e:.3g} pb", flush=True)
    if failed:
        print(f"{failed} runs gave no cross section")
    return report(lam=lam) or (1 if failed else 0)


def report(tex=None, lam="3000") -> int:
    out = out_path(lam)
    if not os.path.exists(out):
        print("no results yet")
        return 1
    rows = [l.split("\t") for l in open(out).read().split("\n")[1:] if l]
    by = {(p, o, s): (float(x), float(e)) for p, o, s, x, e, _ in rows}
    procs = [p for p in PROCS.values() if any(k[0] == p for k in by)]
    npass = nfail = nopen = 0
    lines = []
    print(f"\n{'process':<14s} {'CP-odd interference':>24s} {'CP-odd square':>15s} "
          f"{'CP-even interference':>24s}  verdict")
    for p in procs:
        oi = by.get((p, "NP^2==2", "cpodd"))
        osq = by.get((p, "NP<=2 NP^2==4", "cpodd"))
        ei = by.get((p, "NP^2==2", "cpeven"))
        if not (oi and ei and osq):
            print(f"{p:<14s} incomplete")
            nopen += 1
            continue
        frac = abs(oi[0]) / abs(ei[0]) if ei[0] else float("inf")
        if p not in SELF_CONJUGATE:
            print(f"{p:<14s} {oi[0]:>15.4g} +- {oi[1]:<6.2g} "
                  f"{(osq[0] if osq else float('nan')):>15.4g} {ei[0]:>15.4g} +- {ei[1]:<6.2g}  "
                  f"not a CP test: the final state is not self-conjugate "
                  f"({frac:.1e} of CP-even)")
            lines.append((p, oi, osq, ei, frac))
            continue
        # a vanishing interference means something only where the CP-odd set acts (its square is
        # there) and where the CP-even set run the same way interferes
        zero = abs(oi[0]) < 3 * oi[1] or frac < 1e-5
        acts = osq[0] > 3 * osq[1] and abs(ei[0]) > 3 * ei[1]
        ok = zero and acts
        npass += ok
        nfail += not ok
        verdict = ("zero" if zero else "NONZERO") + ("" if acts else ", NO SQUARE OR NO CONTROL")
        print(f"{p:<14s} {oi[0]:>15.4g} +- {oi[1]:<6.2g} "
              f"{osq[0]:>15.4g} {ei[0]:>15.4g} +- {ei[1]:<6.2g}  "
              f"{verdict} ({frac:.1e} of CP-even)")
        lines.append((p, oi, osq, ei, frac))
    print(f"\nCP null test: {npass} of {npass + nfail} self-conjugate final states have a vanishing "
          f"CP-odd interference beside a nonzero square and a nonzero CP-even interference"
          + (f", {nopen} incomplete" if nopen else ""))
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
    return 0 if nfail == 0 and nopen == 0 else 1


def tex_proc(p):
    m = {"p": "p", "w+": "W^+", "w-": "W^-", "z": "Z", "h": "H", "a": r"\gamma"}
    i, f = p.split(">", 1)
    return ("$" + " ".join(m.get(x, x) for x in i.split()) + r" \to "
            + " ".join(m.get(x, x) for x in f.split()) + "$")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
