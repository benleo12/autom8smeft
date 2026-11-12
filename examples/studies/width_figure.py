#!/usr/bin/env python3
"""The figure of a partial width order by order in the EFT expansion, against the precision of measurements.

    examples/studies/width_figure.py <out.pdf> <results.tsv> [<results.tsv> ...] [--lines FILE] [--ymin Y]
                                     [--title TEXT]

Each results file is the rows of a decay at one Lambda (examples/studies/zwidth/results_L<Lambda>.tsv), one
row at each order: NP=0, NP^2==1, NP^2==2, NP<=3 NP^2==3 and NP<=4 NP^2==4.  The row of order k is the
term Gamma^(k) of the width at 1/Lambda^(2k), with every product of amplitudes at that order, so the
width truncated at order N is Gamma_N = Gamma^(0) + ... + Gamma^(N).  Against Lambda the figure draws the
contribution at each order, |Gamma_N - Gamma_(N-1)|/Gamma_SM = |Gamma^(N)|/Gamma_SM for N = 1 to 4, with
Gamma_SM = Gamma^(0), each named by its order 1/Lambda^(2N).
The lines join the runs.  A curve is named at the right edge, or where it leaves the axis if it passes
below --ymin (default: the decade below the smallest value drawn).

--lines names a file of horizontal lines, a relative precision on the width each (zwidth/precision.txt):
a label, the value and its source on a line, separated by tabs, with # for a comment.  A contribution is
relevant at a precision where its curve lies above that precision's line.

At fixed coefficients every coupling of NP order n carries 1/Lambda^(2n), so Gamma^(k) times
Lambda^(2k) is the same number at every Lambda and Gamma^(0) does not depend on Lambda at all.  The
script stops unless every row agrees with that within half a unit in its last printed digit and three
times its error.  run_study.sh writes the width of a decay to ten digits with error 0, since it is the
exact tree-level width of the matrix element (examples/studies/decay_width.f).  A row from a model with a
coupling of the wrong order, or one run at a Lambda other than the one its settings name, fails this.
It also stops if a term changes sign between two values of Lambda, which a log axis would hide.

The table of what is drawn is written beside the figure (<out>.tsv), with the values at each Lambda:
shift_N = (Gamma_N - Gamma_SM)/Gamma_SM and term_N = |Gamma^(N)|/Gamma_SM.
Nothing is drawn unless every row checks out against its record, with the released model for the
whole figure (provenance.py).
"""
from __future__ import annotations

import argparse
import math
import os
import re
import sys

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.ticker import FixedLocator, LogLocator, NullFormatter  # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import provenance  # noqa: E402
from paper_figure import WIDTH_IN, label_right, paper_style  # noqa: E402

# the order N of a row, from the squared NP order it was generated at
ORDER = {"NP=0": 0, "NP^2==1": 1, "NP^2==2": 2, "NP<=3 NP^2==3": 3, "NP<=4 NP^2==4": 4}
TOP = max(ORDER.values())
# Okabe-Ito, one colour per order, and the precisions in dark grey
COLOUR = {1: "#0072B2", 2: "#E69F00", 3: "#009E73", 4: "#D55E00"}
PRECISION = "0.3"


def half_digit(x, digits):
    """Half a unit in the last of the significant digits of x that its row prints."""
    return 0.5 * 10 ** (math.floor(math.log10(abs(x))) - digits + 1) if x else 0.0


def terms(path):
    """(Lambda in GeV, {order: (Gamma^(k), error, printed digits)}, process) of one study."""
    head, rows = provenance.read_tsv(path)
    lam, out, procs = set(), {}, set()
    for r in rows:
        d = provenance.as_dict(head, r)
        where = f"{path}: {d['process'].strip()} | {d['model']} | {d['order']}"
        if d["order"] not in ORDER:
            sys.exit(f"{where}: an order this figure does not draw")
        m = re.search(r"\bLam=(" + provenance.NUM + r")(?:\s|$)", d["settings"])
        if not m:
            sys.exit(f"{where}: no Lam= in its settings")
        try:
            out[ORDER[d["order"]]] = (float(d["sigma_pb"]), float(d["error_pb"]), provenance.sig_digits(d["sigma_pb"]))
        except ValueError:
            sys.exit(f"{where}: {d['sigma_pb']} is not a width")
        lam.add(float(m.group(1)))
        procs.add(d["process"].strip())
    if len(lam) != 1 or len(procs) != 1 or sorted(out) != sorted(ORDER.values()):
        sys.exit(f"{path}: needs one process at one Lam, with a row at each of {', '.join(ORDER)}")
    return lam.pop(), out, procs.pop()


def check_scaling(studies):
    """Stop unless Gamma^(k) Lambda^(2k) is the same at every Lambda, within the digits and errors."""
    ref_lam, ref = studies[0][0], studies[0][1]
    for lam, t in studies[1:]:
        for k in sorted(t):
            f = (lam / ref_lam) ** (2 * k)
            a, ea = t[k][0] * f, t[k][1] * f
            b, eb, nb = ref[k]
            tol = half_digit(t[k][0], t[k][2]) * f + half_digit(b, nb) + 3 * math.hypot(ea, eb)
            if abs(a - b) > tol:
                sys.exit(f"Gamma^({k}) does not scale as Lambda^-{2 * k}: {t[k][0]:.10g} GeV at Lam = {lam:g} "
                         f"is {a:.10g} at Lam = {ref_lam:g}, and the row there gives {b:.10g} (tolerance {tol:.2g})")


def read_lines(path):
    """[(label, relative precision)] of a --lines file."""
    out = []
    for i, line in enumerate(open(path), 1):
        line = line.split("#", 1)[0].rstrip("\n")
        if not line.strip():
            continue
        f = [x.strip() for x in line.split("\t")]
        try:
            if len(f) != 3 or not f[0] or not f[2]:
                raise ValueError
            v = float(f[1])
        except ValueError:
            sys.exit(f"{path}:{i}: a line needs a label, a value and its source, separated by tabs")
        if not 0 < v < 1:
            sys.exit(f"{path}:{i}: {f[1]} is not a relative precision")
        out.append((f[0], v))
    return out


def main(argv) -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("out")
    ap.add_argument("files", nargs="+")
    ap.add_argument("--lines")
    ap.add_argument("--ymin", type=float)
    ap.add_argument("--title", default="")
    if len(argv) < 3:
        print(__doc__)
        return 2
    a = ap.parse_args(argv[1:])
    provenance.require(a.files, "width_figure.py")
    lines = read_lines(a.lines) if a.lines else []

    got = sorted(terms(f) for f in a.files)
    if len({p for _, _, p in got}) != 1 or len({lam for lam, _, _ in got}) != len(got):
        sys.exit("width_figure.py: the studies must be of one decay, each at its own Lam")
    studies = [(lam, t) for lam, t, _ in got]
    check_scaling(studies)

    lams = [lam / 1000 for lam, _ in studies]
    shift = {n: [sum(t[k][0] for k in range(1, n + 1)) / t[0][0] for _, t in studies] for n in range(1, TOP + 1)}
    term = {k: [t[k][0] / t[0][0] for _, t in studies] for k in range(1, TOP + 1)}
    for k, ys in term.items():
        if len({math.copysign(1, v) for v in ys}) != 1:
            sys.exit(f"width_figure.py: Gamma^({k}) changes sign, and the axis is a log axis")

    with open(os.path.splitext(a.out)[0] + ".tsv", "w") as f:
        f.write("Lam_GeV\tGamma_SM_GeV\t" + "\t".join(f"shift_N{n}" for n in shift)
                + "\t" + "\t".join(f"term_N{k}" for k in term) + "\n")
        for i, (lam, t) in enumerate(studies):
            f.write(f"{lam:g}\t{t[0][0]:.6g}\t" + "\t".join(f"{shift[n][i]:.6g}" for n in shift)
                    + "\t" + "\t".join(f"{abs(term[k][i]):.6g}" for k in term) + "\n")

    paper_style()
    fig, ax = plt.subplots(figsize=(WIDTH_IN, 0.62 * WIDTH_IN),
                           gridspec_kw={"left": 0.12, "right": 0.79, "top": 0.92, "bottom": 0.14})
    named = [(rf"$1/\Lambda^{{{2 * k}}}$", COLOUR[k], k, [abs(v) for v in ys]) for k, ys in term.items()]
    for _, colour, _, ys in named:
        ax.plot(lams, ys, color=colour, lw=1.8, solid_capstyle="butt")
    for _, v in lines:
        ax.axhline(v, color=PRECISION, lw=0.8, ls=(0, (5, 3)), zorder=1)
    ax.set_xscale("log")
    ax.set_yscale("log")
    pos = [v for *_, ys in named for v in ys] + [v for _, v in lines]
    y0 = a.ymin if a.ymin else 10 ** math.floor(math.log10(min(pos)))
    ax.set_ylim(y0, 10 ** math.ceil(math.log10(max(pos))))
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=12))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=range(2, 10), numticks=12))
    ax.yaxis.set_minor_formatter(NullFormatter())
    ax.set_xlim(lams[0], lams[-1])
    ax.xaxis.set_major_locator(FixedLocator([x for x in (1, 2, 3, 5, 10, 20, 30, 50) if lams[0] <= x <= lams[-1]]))
    ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda x, _: f"{x:g}"))
    ax.xaxis.set_minor_formatter(NullFormatter())
    ax.set_ylabel(r"$|\Gamma_N-\Gamma_{N-1}|/\Gamma_{\mathrm{SM}}$")
    ax.set_xlabel(r"$\Lambda$ [TeV]")
    if a.title:
        ax.text(0.0, 1.03, a.title, transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5)
    # a curve that leaves through the bottom is named where it leaves, at the Lambda where
    # |Gamma^(k)| Lambda^(2k) reaches y0 Lambda^(2k), and the others and the lines at the right edge
    right = [(label, PRECISION, [v]) for label, v in lines]
    for name, colour, k, ys in named:
        if ys[-1] >= y0:
            right.append((name, colour, ys[-1:]))
        else:
            exit_lam = lams[0] * (ys[0] / y0) ** (1 / (2 * k))
            ax.text(exit_lam * 1.04, y0 * 1.5, name, color=colour, fontsize=9.5, ha="left", va="bottom")
    label_right(ax, right, fontsize=9.5)
    fig.savefig(a.out)
    print(f"wrote {a.out} and its table, {len(studies)} values of Lambda, {lams[0]:g} to {lams[-1]:g} TeV")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
