#!/usr/bin/env python3
"""The energy growth of the dimension-eight interference, fitted against the counting.

    validate/energy_growth.py [--proc TAG] [--energies 500,1000,2000,4000] [--nev 2000]
    validate/energy_growth.py --report

The counting of Ref. [Assi:2025zmp] assigns to an operator of class (N_D, N_H, N_f, N_X) and a
vertex of multiplicity n the leading behaviour E^{q} v^{p}/Lambda^4 with

    p_min = max(N_f + N_X + N_H - n, 0),      q_max = 4 + 4 - n - p_min

at dimension eight.  For a 2 -> 2 process the whole amplitude is dimensionless, the Standard
Model one is O(g^2) and energy independent, so the interference cross section behaves as

    sigma_int(E) ~ E^{q - 2} v^{p} / Lambda^4,          d log sigma_int / d log E = q - 2,

and the contact term with n = 4 external legs is the leading route: a three-point insertion has
q_max larger by nothing (p_min grows by one as n falls by one) and pays a propagator, E^{-2}.
So the prediction for a 2 -> 2 process is  slope = q_max(n=4) - 2 = 2 - p_min(n=4).

Measuring it needs a fixed angular acceptance, or the forward Standard-Model peak drags a
logarithm into the fit: the run card's eta_max_pdg does that for the final-state particles
whatever their spin.  A lepton collider at fixed sqrt(s) is used rather than a hadron collider
so that no parton luminosity enters the energy dependence at all.

The model is imported and the process generated ONCE per process; each class is then selected by
zeroing every other coefficient in the param card, which commit 8253062 measured to be exactly
equivalent to a restriction card.  Results append to validate/v12_results.tsv.
"""
from __future__ import annotations

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
MODEL = os.path.join(ROOT, "models", "dim8_is")
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "v12")
OUT = os.path.join(ROOT, "validate", "v12_results.tsv")
NICE = ["nice", "-n", "19"]

# Murphy's classes as (N_D, N_H, N_f, N_X), the order gen/epower.py uses
CLASSES = {
    1: (0, 0, 0, 4), 2: (0, 8, 0, 0), 3: (2, 6, 0, 0), 4: (4, 4, 0, 0), 5: (0, 2, 0, 3),
    6: (0, 4, 0, 2), 7: (2, 2, 0, 2), 8: (2, 4, 0, 1), 9: (0, 1, 2, 2), 10: (0, 3, 2, 1),
    11: (3, 2, 2, 0), 12: (0, 5, 2, 0), 13: (1, 4, 2, 0), 14: (1, 0, 2, 2), 15: (1, 2, 2, 1),
    16: (2, 1, 2, 1), 17: (2, 3, 2, 0), 18: (0, 2, 4, 0), 19: (0, 0, 4, 1), 20: (1, 1, 4, 0),
    21: (2, 0, 4, 0),
}
NAMES = {1: "X^4", 2: "H^8", 3: "H^6D^2", 4: "H^4D^4", 5: "X^3H^2", 6: "X^2H^4",
         7: "X^2H^2D^2", 8: "XH^4D^2", 9: "psi^2X^2H", 10: "psi^2XH^3", 11: "psi^2H^2D^3",
         12: "psi^2H^5", 13: "psi^2H^4D", 14: "psi^2X^2D", 15: "psi^2XH^2D", 16: "psi^2XHD^2",
         17: "psi^2H^3D^2", 18: "psi^4H^2", 19: "psi^4X", 20: "psi^4HD", 21: "psi^4D^2"}

# Final states whose angular acceptance the run card can cut on by PDG code.  Each process is
# chosen so that at least one class reaches it with a four-point contact vertex.
PROCS = {
    "ww": ("e+ e- > w+ w-", "{24:1.1}"),
    "zh": ("e+ e- > z h", "{23:1.1,25:1.1}"),
    "mm": ("e+ e- > mu+ mu-", "{13:1.1}"),
    "uu": ("e+ e- > u u~", "{2:1.1}"),
}


def qmax(cls: int, n: int = 4):
    """(q_max, p_min) at vertex multiplicity n, from the validated port of the counting
    notebook rather than a second hand-written copy of the same formula.  Returns None when the
    class cannot reach n external legs at all: psi^4X needs five, so it has no 2 -> 2 contact
    term and appears in a 2 -> 2 process only through an internal gauge propagator."""
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    import epower
    ND, NH, Nf, NX = CLASSES[cls]
    L = epower.leading(ND, NH, Nf, NX, n)
    if L is epower.NO_LEGS:
        return None
    return L.q, L.p


def class_wcs(n: int):
    """The param-card entries of a class.  A complex coefficient reaches the card as a Re and an
    Im part, so the catalogue's base name is not a card entry and set_cards.py rejects it."""
    sys.path.insert(0, os.path.join(ROOT, "validate"))
    import cardnames
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    return cardnames.expand(MODEL, [w for e in idx if e["cls"] == n for w in e["wcs"]])


def run(cmd, log, cwd=None):
    with open(log, "a") as fh:
        fh.write("\n$ " + " ".join(cmd) + "\n")
        return subprocess.run(NICE + cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, cwd=cwd, check=False).returncode


def generate(tag: str, order: str = "NP^2==2", suffix: str = ""):
    """Import the model and output the process once.  Returns the process directory."""
    proc, _ = PROCS[tag]
    d = os.path.join(WORK, tag + suffix)
    if os.path.exists(os.path.join(d, "bin", "generate_events")):
        return d
    os.makedirs(WORK, exist_ok=True)
    sc = os.path.join(WORK, f"{tag}{suffix}.mg5")
    open(sc, "w").write(f"import model {MODEL}\ngenerate {proc} {order}\noutput {d} -f\n")
    rc = run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc],
             os.path.join(WORK, f"{tag}{suffix}_gen.log"))
    if rc or not os.path.exists(os.path.join(d, "bin", "generate_events")):
        print(f"[{tag}] generation FAILED, see {WORK}/{tag}{suffix}_gen.log")
        return None
    open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
        "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
    return d


def one(d, tag, label, sets, energy, nev, log):
    """One cross section: edit the cards, integrate, parse.  Returns (sigma, error) in pb."""
    _, eta = PROCS[tag]
    common = [f"nevents={nev}", "lpp1=0", "lpp2=0", f"ebeam1={energy/2:g}", f"ebeam2={energy/2:g}",
              "hel_recycling=False", "use_syst=False", f"eta_max_pdg={eta}",
              # neutralise the default acceptance so eta_max_pdg is the ONLY cut, but only for the
              # entries this process's card actually has: MadGraph writes a minimal run card and
              # omits the lepton and jet blocks for a final state with neither, and set_cards.py
              # treats an unknown name as an error on purpose.
              "ptl=0", "etal=-1", "drll=0", "mmll=0", "ptj=0", "etaj=-1", "drjj=0", "ptgmin=0"]
    have = set(re.findall(r"=\s*(\w+)", open(os.path.join(d, "Cards", "run_card.dat")).read()))
    common = [a for a in common if a.split("=")[0] in have or a.startswith("hel_recycling")]
    if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d] + common + sets, log):
        return None, None
    before = os.path.getsize(log) if os.path.exists(log) else 0
    run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
    txt = open(log, errors="replace").read()[before:]
    m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
    if not m:
        return 0.0, 0.0     # a vanishing amplitude prints no cross section line
    return float(m[-1][0]), float(m[-1][1])


def main(argv) -> int:
    if "--report" in argv:
        return report(argv[argv.index("--tex") + 1] if "--tex" in argv else None)
    tags = [argv[argv.index("--proc") + 1]] if "--proc" in argv else list(PROCS)
    energies = [float(x) for x in (argv[argv.index("--energies") + 1] if "--energies" in argv
                                  else "500,1000,2000,4000").split(",")]
    nev = int(argv[argv.index("--nev") + 1]) if "--nev" in argv else 2000
    if not os.path.exists(OUT):
        open(OUT, "w").write("process\tlabel\tenergy_GeV\tsigma_pb\terror_pb\tnevents\n")
    done = {tuple(l.split("\t")[:3]) for l in open(OUT).read().split("\n")[1:] if l}
    for tag in tags:
        # The Standard-Model rate at the same energies and the same acceptance.  Without it the
        # only reference is the contact-term prediction, and a class that reaches the process
        # through a three-point insertion on an internal line or through the input relations
        # inherits the Standard Model's own energy dependence instead, which has to be measured
        # rather than assumed: sigma_SM of a 2 -> 2 at fixed angle falls like 1/s only if nothing
        # in the amplitude grows, and for e+e- -> W+W- the t-channel neutrino makes that worth
        # checking.  NP^2==2 with the coefficients off is exactly zero, that bin being the
        # interference itself, so this needs its own NP=0 process directory.
        dsm = generate(tag, "NP=0", "_sm")
        if dsm:
            logsm = os.path.join(WORK, f"{tag}_sm_runs.log")
            for E in energies:
                if (PROCS[tag][0], "SMrate", f"{E:g}") in done:
                    continue
                x, e = one(dsm, tag, "SMrate", ["dim8_all=0", "Lam=1000"], E, nev, logsm)
                if x is None:
                    continue
                with open(OUT, "a") as fh:
                    fh.write(f"{PROCS[tag][0]}\tSMrate\t{E:g}\t{x:.6g}\t{e:.6g}\t{nev}\n")
                print(f"[{tag}] SMrate {E:6g} GeV  {x:12.5g} +- {e:.3g} pb", flush=True)
        d = generate(tag)
        if not d:
            continue
        log = os.path.join(WORK, f"{tag}_runs.log")
        skip = set()
        for E in energies:
            for label in ["SM", "all"] + [f"cls{c}" for c in sorted(CLASSES)]:
                if (PROCS[tag][0], label, f"{E:g}") in done or label in skip:
                    continue
                if label == "SM":
                    sets = ["dim8_all=0", "Lam=1000"]
                elif label == "all":
                    sets = ["dim8_all=1", "Lam=1000"]
                else:
                    c = int(label[3:])
                    sets = ["dim8_all=0", "Lam=1000"] + [f"{w}=1" for w in class_wcs(c)]
                x, e = one(d, tag, label, sets, E, nev, log)
                if x is None:
                    print(f"[{tag}] {label} at {E:g} GeV: card error, see {log}", flush=True)
                    continue
                with open(OUT, "a") as fh:
                    fh.write(f"{PROCS[tag][0]}\t{label}\t{E:g}\t{x:.6g}\t{e:.6g}\t{nev}\n")
                print(f"[{tag}] {label:6s} {E:6g} GeV  {x:12.5g} +- {e:.3g} pb", flush=True)
                if label.startswith("cls") and E == energies[0] and x == 0.0:
                    skip.add(label)          # no amplitude at all: the other energies are the same
    return report()


def _fit(pts):
    """Weighted least squares of log|sigma| on log E.  Returns (slope, error) or None."""
    good = {E: (x, e) for E, (x, e) in pts.items() if abs(x) > 3 * e > 0}
    if len(good) < 3:
        return None
    xs = [math.log(E) for E in sorted(good)]
    ys = [math.log(abs(good[E][0])) for E in sorted(good)]
    ws = [(abs(good[E][0]) / good[E][1]) ** 2 for E in sorted(good)]
    S = sum(ws); Sx = sum(w * x for w, x in zip(ws, xs)); Sy = sum(w * y for w, y in zip(ws, ys))
    Sxx = sum(w * x * x for w, x in zip(ws, xs)); Sxy = sum(w * x * y for w, x, y in zip(ws, xs, ys))
    den = S * Sxx - Sx * Sx
    if den == 0:
        return None
    # the statistical error of the fit understates the spread when the points are this precise,
    # so the quoted error is the larger of it and the scatter about the line
    slope = (S * Sxy - Sx * Sy) / den
    inter = (Sy - slope * Sx) / S
    chi = sum(w * (y - slope * x - inter) ** 2 for w, x, y in zip(ws, xs, ys))
    err = math.sqrt(max(S / den, chi / max(len(good) - 2, 1) * S / den))
    return slope, err, len(good)


def report(tex=None) -> int:
    """Print the fitted exponents against both references, and with ``tex`` write the table.

    Two references, because a class can reach a 2 -> 2 process by two routes with different
    energy behaviour.  A four-point contact term gives the counting's own prediction,
    q_max(n=4) - 2, the two coming from the phase space.  A class that gets there only through a
    three-point insertion on an internal line, or through the input relations, multiplies the
    Standard-Model amplitude instead and inherits its energy dependence, which is measured here
    rather than assumed.  The verdict column says which reference the fit matches."""
    if not os.path.exists(OUT):
        print("no results yet")
        return 1
    texrows = []
    rows = [l.split("\t") for l in open(OUT).read().split("\n")[1:] if l]
    by = {}
    for p, lab, E, x, e, _ in rows:
        by.setdefault((p, lab), {})[float(E)] = (float(x), float(e))
    print(f"{'process':<16s} {'class':<13s} {'contact':>8s} {'SM':>13s} {'fitted':>14s}  verdict")
    for p in sorted({k[0] for k in by}):
        sm = _fit(by.get((p, "SMrate"), {}))
        smtxt = f"{sm[0]:.2f} +- {sm[1]:.2f}" if sm else "not measured"
        for lab in sorted((k[1] for k in by if k[0] == p),
                          key=lambda l: int(l[3:]) if l.startswith("cls") else 99):
            if not lab.startswith("cls"):
                continue
            c = int(lab[3:])
            f = _fit(by[(p, lab)])
            if not f:
                continue
            qp = qmax(c)
            contact = None if qp is None else qp[0] - 2
            # The counting gives the exponent of the class's MAXIMAL four-point vertex.  Which
            # vertex a given process actually uses, and with how many vacuum insertions, is a
            # property of the process, so the counting is a BOUND and only a class that reaches
            # the process through that maximal contact term saturates it.  Three verdicts:
            # saturated, below the bound (a slower route), or the Standard-Model exponent, which
            # is what a pure coupling rescaling gives.  Anything above the bound is a failure.
            tol = max(3 * f[1], 0.25)
            verdict = []
            if contact is not None and f[0] > contact + tol:
                verdict.append("ABOVE THE BOUND")
            elif contact is not None and abs(f[0] - contact) <= tol:
                verdict.append("saturates the bound")
            elif contact is not None:
                verdict.append("below the bound")
            if sm and abs(f[0] - sm[0]) < max(3 * f[1], 3 * sm[1], 0.25):
                verdict.append("the SM exponent")
            texrows.append((p, c, f, contact, sm, verdict))
            print(f"{p:<16s} {NAMES[c]:<13s} "
                  f"{('--' if contact is None else str(contact)):>8s} {smtxt:>13s} "
                  f"{f[0]:>8.2f} +- {f[1]:.2f}  {', '.join(verdict) or '-'}")
    if tex:
        procs = sorted({r[0] for r in texrows})

        def block(pr):
            """One process as a list of rows, each already joined with & and carrying no \\\\."""
            out = [r"\multicolumn{5}{l}{$" + tex_proc(pr) + r"$}"]
            for r in [x for x in texrows if x[0] == pr]:
                _, c, f, contact, sm, verdict = r
                nm = NAMES[c].replace("psi", r"\psi")
                v = {"saturates the bound": "saturated", "below the bound": "below",
                     "below the bound, the SM exponent": "SM exponent",
                     "saturates the bound, the SM exponent": "saturated = SM",
                     "ABOVE THE BOUND": r"ABOVE$^{\ddagger}$"}.get(", ".join(verdict),
                                                               ", ".join(verdict) or "--")
                out.append(f"{c} & ${nm}$ & " + ("--" if contact is None else f"${contact}$")
                           + f" & ${f[0]:.2f} \\pm {f[1]:.2f}$ & {v}")
            return out

        # Two process blocks side by side.  Stacked, 41 fits make a table taller than a text page,
        # and LaTeX then pushes it and every float after it to float pages at the end of the
        # document, twenty pages from the text that discusses them.
        half = (len(procs) + 1) // 2
        left, right = [], []
        for pr in procs[:half]:
            left += block(pr) + [""]
        for pr in procs[half:]:
            right += block(pr) + [""]
        blank = "& & & &"
        body = []
        for i in range(max(len(left), len(right))):
            a = left[i] if i < len(left) else ""
            b = right[i] if i < len(right) else ""
            if a == "" and b == "":
                body.append(r"\addlinespace[4pt]")
                continue
            body.append((a or blank) + " & " + (b or blank) + r" \\")
        smline = ""
        for pr in procs:
            s0 = _fit(by.get((pr, "SMrate"), {}))
            if s0:
                smline = (f" The Standard-Model rate itself falls with an exponent "
                          f"${s0[0]:.2f} \\pm {s0[1]:.2f}$ over the same range.")
        open(tex, "w").write(r"""\begin{table}[!htbp]\centering\footnotesize
\setlength{\tabcolsep}{4pt}
\begin{tabular}{@{}r l c c l @{\qquad} r l c c l@{}}
\toprule
 & class & bound & fitted & route & & class & bound & fitted & route \\
\midrule
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\caption{The exponent of the energy growth of the dimension-eight interference,
$\sigma_{1/\Lambda^4} \propto E^{\,s}$, at a lepton collider at fixed $\sqrt{s}$ with
$|\eta| < 1.1$ on the final state, fitted over $\sqrt{s} = 0.5$ to $4$~TeV with unit
coefficients and $\Lambda = 1$~TeV. The ``bound'' column is what the class's four-leg $\lambda$ power implies, $2-k$ for
$\lambda^{4+k}$, and it is a bound and not a prediction: it is the exponent of the class's fastest four-point vertex, and a process that
can only use a slower one, with more vacuum insertions, or whose amplitude does not interfere with the Standard-Model one for reasons of helicity, grows more slowly. ``saturated'' means
the fit reaches the bound, ``below'' that it does not, and ``SM exponent'' that the class
reproduces the Standard-Model rate's own exponent, which is consistent with a pure rescaling of a
Standard-Model coupling.""" + smline + r"""
A double dagger would mark a fit above its bound, which the first build of the model produced for $\psi^2H^5$ because its entry was quadratic in the coefficient and not an interference, as \cref{sec:np0} records. Classes absent from a block give no amplitude in that process. Generated by
\code{validate/energy\_growth.py --report --tex}.}
\label{tab:v12}
\end{table}
""")
        print(f"wrote {tex}")
    return 0


def tex_proc(p):
    m = {"e+": "e^+", "e-": "e^-", "mu+": r"\mu^+", "mu-": r"\mu^-", "w+": "W^+", "w-": "W^-",
         "z": "Z", "h": "H", "u": "u", "u~": r"\bar u", "a": r"\gamma"}
    i, f = p.split(">", 1)
    return " ".join(m.get(x, x) for x in i.split()) + r" \to " + " ".join(m.get(x, x) for x in f.split())


if __name__ == "__main__":
    sys.exit(main(sys.argv))
