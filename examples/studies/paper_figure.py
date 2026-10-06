#!/usr/bin/env python3
"""Publication figures from the .tsv files plot_study.py writes.

    examples/studies/paper_figure.py <in.tsv> <out.pdf> [--xmax GeV] [--xlabel TEXT]
                                     [--title TEXT] [--ratio-max R] [--ratio-min R]
                                     [--edges a,b,c,...]

plot_study.py produces a diagnostic: every 100 GeV bin it filled, a 6 TeV axis and a ratio panel
that carries the statistical noise of the empty tail.  This produces the figure that goes in the
paper.  It is drawn at the size it is printed, in the fonts of the paper, so nothing is scaled.

The bins widen with the mass, 100 GeV to 800, then 200 to 1600, then 400, because the samples
are five thousand events and a Standard-Model bin at two TeV holds a handful of them.  What is
plotted is the cross section per 100 GeV, so a change of bin width leaves a smooth curve smooth.
The first column of the file is the reference and the ratio panel is taken against it.

Both panels are absolute values on plain log axes.  The interference of a dimension-eight class
changes sign from class to class and the curves span five decades, which a symmetric log axis
cannot show.  The sign belongs in the table.  What a distribution is for here is the SHAPE,
whether a class grows with energy or tracks the Standard Model, and the lower panel reads that
off directly: a flat line is a class acting through the input relations, a rising one is a class
with its own contact term, and unity is where the class is as large as the process it corrects.

Every curve is named at its right-hand end instead of in a legend, so the ordering of the
classes at high mass, which is the point of the figure, is read without a lookup.  The colour of
a class is fixed by its label, so the same class is the same colour in every figure of the
paper.

The squared term of the leading class is drawn as a VALIDITY MARKER and nothing else
(2026-10-04): grey, dashed, in the ratio panel only.  Where it crosses the interference the
1/Lambda^4 truncation has failed at this Lambda, which is the clipping energy an analysis would
use, and nothing above that crossing is a prediction.  That is the dimension-eight form of the
linear-against-quadratic comparison dimension-six fits make, and of the clipping that VBS
analyses apply to the dimension-eight square they fit.  It is kept out of the upper panel, where
a 1/Lambda^8 curve above the Standard Model reads as a prediction of a large effect, which it is
not.  A dotted line marks m = Lambda (--lambda GeV), the a priori expectation the crossing
confirms.
"""
from __future__ import annotations

import math
import os
import sys

import matplotlib
matplotlib.use("pdf")
import matplotlib.pyplot as plt          # noqa: E402
from matplotlib.ticker import LogLocator, NullFormatter  # noqa: E402

# Okabe-Ito, which stays distinguishable in greyscale and to a colour-blind reader, fixed per
# class so that a class is the same colour in every figure of the paper; a squared term takes the
# colour of its class and a dashed line
COLOUR = {
    "SM": "#000000",
    r"\psi^2X^2D": "#E69F00",
    r"X^2H^4": "#009E73",
    r"\psi^2H^4D": "#56B4E9",
    r"\psi^2XH^2D": "#CC79A7",
    r"X^4": "#D55E00",
    r"X^2H^2D^2": "#0072B2",
    r"H^4D^4": "#7F3C8D",
}
FALLBACK = ["#999999", "#F0E442", "#1B9E77", "#E7298A"]


def colour_of(name, i):
    core = name.replace("squared", "").strip().strip("$")
    return COLOUR.get(core, FALLBACK[i % len(FALLBACK)])

# the width of the printed figure: 0.95 of the JHEP text width, which is 0.72 of a letter page
WIDTH_IN = 5.85


def read(path):
    rows = [l.rstrip("\n").split("\t") for l in open(path) if l.strip()]
    head, rows = rows[0], rows[1:]
    lo = [float(r[0]) for r in rows]
    hi = [float(r[1]) for r in rows]
    cols = {head[i]: [float(r[i]) for r in rows] for i in range(2, len(head))}
    return lo, hi, cols


def default_edges(start, xmax):
    """100 GeV bins to 800, 200 to 1600, 400 beyond, from the first filled bin to xmax."""
    e, x = [start], start
    while x < xmax - 1e-9:
        step = 100 if x < 800 else 200 if x < 1600 else 400
        # the last bin absorbs a remainder shorter than a bin instead of becoming a sliver
        x = xmax if xmax - x < 2 * step else x + step
        e.append(x)
    return e


def rebin_to(lo, hi, cols, edges):
    """Sum the 100 GeV bins into the given edges, which must sit on the original boundaries."""
    out = {k: [0.0] * (len(edges) - 1) for k in cols}
    for i, (a, b) in enumerate(zip(lo, hi)):
        for j in range(len(edges) - 1):
            if a >= edges[j] - 1e-9 and b <= edges[j + 1] + 1e-9:
                for k in cols:
                    out[k][j] += cols[k][i]
                break
    return out


def pretty(name):
    """The label of a column as it should read on the page."""
    name = name.strip()
    if name == "SM":
        return "SM"
    if name.endswith("squared"):
        core = name[:-len("squared")].strip().strip("$")
        return r"$(" + core + r")^2$"
    return name


def spread(fracs, gap, lo=0.02, hi=0.98):
    """Move label positions (axes fractions) apart until none are closer than gap."""
    order = sorted(range(len(fracs)), key=lambda i: fracs[i])
    pos = [fracs[i] for i in order]
    for k in range(1, len(pos)):
        pos[k] = max(pos[k], pos[k - 1] + gap)
    over = pos[-1] - hi
    if over > 0:
        pos = [p - over for p in pos]
    for k in range(len(pos) - 2, -1, -1):
        pos[k] = min(pos[k], pos[k + 1] - gap)
    under = lo - pos[0]
    if under > 0:
        pos = [p + under for p in pos]
    res = [0.0] * len(fracs)
    for k, i in enumerate(order):
        res[i] = pos[k]
    return res


def label_right(ax, curves, fontsize, gap=0.085):
    """Name every curve just outside the right edge, at the height of its last two bins, with a
    thin leader from where the curve ends to where its name had to move."""
    y0, y1 = ax.get_ylim()
    ends, items = [], []
    for name, color, ys in curves:
        vals = [v for v in ys[-2:] if v == v and v > 0] or [v for v in ys if v == v and v > 0]
        if not vals:
            continue
        v = math.exp(sum(math.log(x) for x in vals) / len(vals))
        f = (math.log10(v) - math.log10(y0)) / (math.log10(y1) - math.log10(y0))
        ends.append(min(max(f, 0.0), 1.0))
        items.append((name, color))
    for (name, color), f0, f in zip(items, ends, spread(ends, gap)):
        ax.plot([1.0, 1.03, 1.045], [f0, f, f], color=color, lw=0.6, alpha=0.8,
                transform=ax.transAxes, clip_on=False, solid_capstyle="round")
        ax.text(1.055, f, name, color=color, fontsize=fontsize, ha="left", va="center",
                transform=ax.transAxes)


def main(argv) -> int:
    if len(argv) < 3:
        print(__doc__)
        return 2
    src, out = argv[1], argv[2]

    def opt(flag, default, cast=float):
        return cast(argv[argv.index(flag) + 1]) if flag in argv else default

    xmax = opt("--xmax", None)
    xlabel = opt("--xlabel", r"$m$ [GeV]", str)
    title = opt("--title", "", str)
    rmax = opt("--ratio-max", None)
    rmin = opt("--ratio-min", 1e-3)
    edges_opt = opt("--edges", None, str)
    lam = opt("--lambda", None)

    lo, hi, cols = read(src)
    squares = {k: v for k, v in cols.items() if k.strip().endswith("squared")}
    cols = {k: v for k, v in cols.items() if k not in squares}
    names = list(cols)
    ref = names[0]
    first = min((i for i, v in enumerate(cols[ref]) if v != 0), default=0)
    start = lo[first]
    if xmax is None:
        xmax = hi[max(i for i, v in enumerate(cols[ref]) if v != 0)]
    edges = [float(x) for x in edges_opt.split(",")] if edges_opt else default_edges(start, xmax)
    binned = rebin_to(lo, hi, cols, edges)
    widths = [(b - a) / 100.0 for a, b in zip(edges[:-1], edges[1:])]

    plt.rcParams.update({
        "text.usetex": True,
        "text.latex.preamble": r"\usepackage{amsmath,amssymb}",
        "font.family": "serif", "font.size": 10,
        "axes.labelsize": 11, "xtick.labelsize": 9.5, "ytick.labelsize": 9.5,
        "axes.linewidth": 0.8, "xtick.direction": "in", "ytick.direction": "in",
        "xtick.top": True, "ytick.right": True,
        "xtick.major.size": 4, "ytick.major.size": 4, "xtick.minor.size": 2, "ytick.minor.size": 2,
        "lines.linewidth": 1.5, "pdf.fonttype": 42,
    })
    fig, (ax, rx) = plt.subplots(2, 1, figsize=(WIDTH_IN, 0.86 * WIDTH_IN), sharex=True,
                                 gridspec_kw={"height_ratios": [1.0, 1.0], "hspace": 0.05,
                                              "left": 0.12, "right": 0.79, "top": 0.945,
                                              "bottom": 0.10})

    # the cross section per 100 GeV, absolute, on a log axis
    top = []
    for i, nm in enumerate(names):
        y = [abs(v) / w for v, w in zip(binned[nm], widths)]
        y = [v if v > 0 else float("nan") for v in y]
        sq = nm.endswith("squared")
        ax.stairs(y, edges, color=colour_of(nm, i), ls="--" if sq else "-",
                  lw=2.0 if i == 0 else 1.5, baseline=None)
        top.append((pretty(nm), colour_of(nm, i), y))
    ax.set_yscale("log")
    ax.set_ylabel(r"$|\sigma|$ per 100 GeV [pb]")
    pos = [v for _, _, ys in top for v in ys if v == v]
    ax.set_ylim(max(min(pos) * 0.4, max(pos) * 1e-6), max(pos) * 4)
    ax.yaxis.set_major_locator(LogLocator(base=10, numticks=8))
    ax.yaxis.set_minor_locator(LogLocator(base=10, subs=range(2, 10), numticks=12))
    ax.yaxis.set_minor_formatter(NullFormatter())
    if title:
        ax.text(0.0, 1.03, title, transform=ax.transAxes, ha="left", va="bottom", fontsize=10.5)
    label_right(ax, top, fontsize=9.5)

    # the ratio to the reference, which is the panel the energy counting is about
    r0 = binned[ref]
    bot = []
    for i, nm in enumerate(names[1:], start=1):
        rr = [(abs(a / b) if b else float("nan")) for a, b in zip(binned[nm], r0)]
        rr = [v if v == v and v > 0 else float("nan") for v in rr]
        rx.stairs(rr, edges, color=colour_of(nm, i),
                  ls="--" if nm.endswith("squared") else "-", baseline=None)
        bot.append((pretty(nm), colour_of(nm, i), rr))
    # the validity marker: the square of the leading class against the Standard Model, grey
    for nm, ys in squares.items():
        rr = [(abs(a / b) if b else float("nan")) for a, b in zip(rebin_to(lo, hi, {nm: ys}, edges)[nm], r0)]
        rr = [v if v == v and v > 0 else float("nan") for v in rr]
        rx.stairs(rr, edges, color="0.45", ls="--", lw=1.1, baseline=None)
        bot.append((pretty(nm), "0.45", rr))
    rx.set_yscale("log")
    if rmax is None:
        top_r = max(v for _, _, rr in bot for v in rr if v == v)
        rmax = 10 ** math.ceil(math.log10(top_r * 1.5))
    rx.set_ylim(rmin, rmax)
    rx.axhline(1.0, color="0.45", lw=0.8, ls=":")
    bot.append(("SM", "0.35", [1.0, 1.0]))
    rx.set_ylabel(r"$|\sigma| / \sigma_{\mathrm{SM}}$")
    rx.set_xlabel(xlabel)
    rx.set_xlim(edges[0], edges[-1])
    rx.yaxis.set_major_locator(LogLocator(base=10, numticks=8))
    rx.yaxis.set_minor_locator(LogLocator(base=10, subs=range(2, 10), numticks=12))
    rx.yaxis.set_minor_formatter(NullFormatter())
    if lam is not None and edges[0] < lam < edges[-1]:
        for a in (ax, rx):
            a.axvline(lam, color="0.45", lw=0.8, ls=":")
        rx.text(lam * 0.985, rx.get_ylim()[1] * 0.55, r"$m = \Lambda$", color="0.35", fontsize=8.5,
                ha="right", va="top")
    label_right(rx, bot, fontsize=9.5)

    fig.savefig(out)
    print(f"wrote {out}  ({len(edges)-1} bins, {edges[0]:.0f} to {edges[-1]:.0f} GeV)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
