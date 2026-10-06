#!/usr/bin/env python3
"""Distributions from MadGraph LHE files for the paper's studies, pure Python.

    examples/studies/plot_study.py <out prefix> <label>=<unweighted_events.lhe.gz> [<label>=<file> ...]

For each file: the invariant mass of all final-state bosons (W, Z, h; PDG 23, 24, 25) and the
leading final-state transverse momentum, histogrammed so that each histogram integrates to the
sample's cross section in pb, with the negative weights of an interference sample kept.  The
normalisation is read from the banner rather than assumed: MadGraph's run card carries
event_norm, which is "average" by default in recent versions, meaning every event of an
unweighted sample carries the full cross section as its weight and the cross section is the mean
of the weights, not the sum.  With event_norm = sum the weights are already sigma/N.  Getting
this wrong scales every distribution by the number of events.  Each histogram is then rescaled
so that it integrates to the banner's "Integrated weight (pb)", the phase-space integration's own
answer: the shape comes from the events and the normalisation from the integration, which is the
usual convention and matters for interference samples, where unweighting reproduces the cross
section only statistically.  With a signed sample the integral is a difference of two large
numbers, the effective statistics is the excess of positive over negative events, and at 1000
events the raw event sum can sit tens of per cent from the integrated weight; the rescaling
factor is printed whenever it exceeds a per mille so that a sample with too few events is
visible rather than silently misnormalised.  Needs python3.13 on this machine for the plots
(the other interpreters have no matplotlib); the tables are written either way.
Writes <out prefix>_mVV.tsv and <out prefix>_pT.tsv (bin edges in GeV, one column per label) and,
if matplotlib is importable, <out prefix>_mVV.png and <out prefix>_pT.png with the same content.
Bins: 100 GeV in mass up to 6 TeV, 50 GeV in p_T up to 3 TeV; the overflow goes in the last bin,
which the plots label as such (the squared samples of the gluon-initiated contact terms put much
of their cross section there).  The plots have two panels: the cross section per bin on a
symmetric log scale, and the ratio of each sample to the first one given, which is the panel
the paper uses.
"""
import gzip, math, re, sys

BOSONS = {23, 24, 25}
MBINS = [100 * i for i in range(0, 61)]
PBINS = [50 * i for i in range(0, 61)]


def banner(path):
    """event_norm and the banner cross section, read from the header before the first event."""
    op = gzip.open if path.endswith(".gz") else open
    norm, xsec = "average", None
    with op(path, "rt") as f:
        for line in f:
            if line.startswith("<event"):
                break
            m = re.search(r"^\s*(\w+)\s*=\s*event_norm", line)
            if m:
                norm = m.group(1)
            m = re.search(r"Integrated weight \(pb\)\s*:\s*([-\d.eE+]+)", line)
            if m:
                xsec = float(m.group(1))
    return norm, xsec


def events(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        inside, lines = False, []
        for line in f:
            if line.startswith("<event"):
                inside, lines = True, []
            elif line.startswith("</event"):
                inside = False
                yield lines
            elif inside and not line.startswith("<") and not line.startswith("#"):
                lines.append(line)


def analyse(path):
    norm, xsec = banner(path)
    mv, pt, wsum, n = [], [], 0.0, 0
    for lines in events(path):
        head = lines[0].split()
        nup, weight = int(head[0]), float(head[2])
        E = px = py = pz = 0.0; lead = 0.0
        for l in lines[1:1 + nup]:
            p = l.split()
            pid, status = abs(int(p[0])), int(p[1])
            if status != 1: continue
            ppx, ppy, ppz, pe = float(p[6]), float(p[7]), float(p[8]), float(p[9])
            lead = max(lead, math.hypot(ppx, ppy))
            if pid in BOSONS:
                E += pe; px += ppx; py += ppy; pz += ppz
        m2 = E * E - px * px - py * py - pz * pz
        mv.append((math.sqrt(max(m2, 0.0)), weight)); pt.append((lead, weight))
        wsum += weight; n += 1
    if norm == "average" and n:
        mv = [(x, w / n) for x, w in mv]; pt = [(x, w / n) for x, w in pt]; wsum /= n
    return mv, pt, wsum, n, xsec


def hist(pairs, edges):
    h = [0.0] * (len(edges) - 1)
    for x, w in pairs:
        i = min(max(int(x // (edges[1] - edges[0])), 0), len(h) - 1)
        h[i] += w
    return h


def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    prefix, samples = argv[1], [a.split("=", 1) for a in argv[2:]]
    results = {}
    for label, path in samples:
        mv, pt, wsum, n, xsec = analyse(path)
        results[label] = (hist(mv, MBINS), hist(pt, PBINS))
        note = ""
        if xsec is not None and wsum and abs(wsum - xsec) > 1e-3 * max(abs(xsec), 1e-30):
            f = xsec / wsum
            results[label] = tuple([x * f for x in h] for h in results[label])
            note = f", rescaled by {f:.4g} to the integrated weight {xsec:.6g} pb"
        print(f"{label}: {n} events, event sum {wsum:.6g} pb{note}")
    for name, edges, k in (("mVV", MBINS, 0), ("pT", PBINS, 1)):
        with open(f"{prefix}_{name}.tsv", "w") as f:
            f.write("low_GeV\thigh_GeV\t" + "\t".join(l for l, _ in samples) + "\n")
            for i in range(len(edges) - 1):
                f.write(f"{edges[i]}\t{edges[i+1]}\t" + "\t".join(f"{results[l][k][i]:.6g}" for l, _ in samples) + "\n")
        print("wrote", f"{prefix}_{name}.tsv")
    try:
        import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
        ref = samples[0][0]
        for name, edges, k, xl in (("mVV", MBINS, 0, "invariant mass of the boson system [GeV]"), ("pT", PBINS, 1, "leading p_T [GeV]")):
            plt.rcParams.update({"font.size": 12, "axes.labelsize": 12, "legend.fontsize": 10})   # paper-sized labels
            fig, (ax, ar) = plt.subplots(2, 1, figsize=(7.2, 6.0), sharex=True, gridspec_kw={"height_ratios": [2, 1], "hspace": 0.05})
            colours = {l: f"C{i}" for i, (l, _) in enumerate(samples)}   # one colour per sample in both panels
            for l, _ in samples:
                ax.stairs(results[l][k], edges, label=l, color=colours[l])
                if l != ref:
                    ar.stairs([r / d if d else float("nan") for r, d in zip(results[l][k], results[ref][k])], edges, label=f"{l} / {ref}", color=colours[l])
            ax.set_ylabel("sigma per bin [pb]"); ax.set_yscale("symlog", linthresh=1e-6); ax.legend(fontsize=10, ncol=2)
            ax.axvspan(edges[-2], edges[-1], color="0.9", zorder=0); ax.text(edges[-2], ax.get_ylim()[1], "overflow", fontsize=7, va="top", ha="right", rotation=90)
            ar.set_yscale("symlog", linthresh=1e-3); ar.axhline(0, color="0.6", lw=0.8); ar.set_ylabel(f"ratio to {ref}"); ar.set_xlabel(xl); ar.legend(fontsize=9, ncol=2)
            fig.savefig(f"{prefix}_{name}.png", dpi=130, bbox_inches="tight"); plt.close(fig)
            print("wrote", f"{prefix}_{name}.png")
    except ImportError:
        print("matplotlib not available: tables only")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
