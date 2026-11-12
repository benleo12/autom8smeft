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
visible rather than silently misnormalised.  The plots need matplotlib, and the tables are
written either way.
Writes <out prefix>_mVV.tsv and <out prefix>_pT.tsv (bin edges in GeV, one column per label) and,
if matplotlib is importable, <out prefix>_mVV.png and <out prefix>_pT.png with the same content.
Bins: 100 GeV in mass up to 6 TeV, 50 GeV in p_T up to 3 TeV; the overflow goes in the last bin,
which the plots label as such (the squared samples of the gluon-initiated contact terms put much
of their cross section there).  The plots have two panels: the cross section per bin on a
symmetric log scale, and the ratio of each sample to the first one given.  They are diagnostics,
and paper_figure.py draws the figures of the paper from the .tsv files.

The statistical errors are written beside the histograms.  A bin is h = sigma f, with sigma the
integrated cross section and f = S_b / S the bin's share of the sum of the event weights.  The
share has the variance sum_i w_i^2 (1_b(i) - f)^2 / S^2, from the squared weights with their
signs and with the correlation between a bin and the total it is a share of, and sigma has the
integration's own error, the XERRUP of the <init> block.  The two are independent, so

    err^2 = sum_b w^2 (1 - 2 f) + f^2 sum w^2 + f^2 err_sigma^2      (weights rescaled to sigma)

A bin that holds a small part of the sample has the familiar sqrt(sum_b w^2), and the whole
sample has the integration's error.  The same holds for any range of mass, in particular for
everything below an upper cut.  A file with no banner cross section is its own event sum, with
the error sqrt(sum_b w^2).  Beside the histograms it writes
  <out prefix>_mVV_err.tsv, <out prefix>_pT_err.tsv  the error of every bin, laid out as the histograms
  <out prefix>_mVV_R.tsv  the truncation table.  For every sample after the first, one row per bin
      (the widening bins of paper_figure.py, over the whole range) and one per upper cut on the
      mass (at every 100 GeV, the last one being the whole sample): the reference (the first
      sample, the Standard Model in the studies), the interference, its square where a sample
      labelled "<label> squared" is given, R = square / |interference|, the interference and the
      square over the reference, and the share of each sample's total in the bin or below the cut,
      each with its error.  The interference, the square and the reference are separate runs and
      are taken as independent.
  <out prefix>_stat.json  the sums of the weights and of their squares per bin and the error of
      each normalisation, from which read_stat() gives the error in any binning (paper_figure.py
      --errors uses it)
  <out prefix>.sources.tsv  the event files behind the histograms, with their sha256 and the
      model version of their runs, and the files above with their sha256, which paper_figure.py
      checks before it draws: the table it draws and the _stat.json it reads must be unchanged
      since plot_study.py wrote them, with an event file for every column

Before it reads the events, every event file kept in a study's lhe/ directory is checked against
the record of its row (provenance.py): it must be the recorded file, the results file holding the
row must check out, and the files must come from one model version, the released one.  Otherwise
nothing is written.
"""
import gzip, json, math, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import provenance  # noqa: E402

BOSONS = {23, 24, 25}
MBINS = [100 * i for i in range(0, 61)]
PBINS = [50 * i for i in range(0, 61)]


def banner(path):
    """event_norm, the banner cross section and the error of the integration, read from the header
    before the first event.  The error is the XERRUP of the <init> block, in quadrature over its
    process lines, and None without an <init> block."""
    op = gzip.open if path.endswith(".gz") else open
    norm, xsec, errs, init = "average", None, [], None
    with op(path, "rt") as f:
        for line in f:
            if line.startswith("<event"):
                break
            if line.startswith("<init>"):
                init = 0; continue
            if line.startswith("</init"):
                init = None; continue
            if init is not None:
                # the first line is the beams, each further one XSECUP XERRUP XMAXUP LPRUP
                if line.strip() and not line.lstrip().startswith(("<", "#")):
                    if init:
                        errs.append(float(line.split()[1]))
                    init += 1
                continue
            m = re.search(r"^\s*(\w+)\s*=\s*event_norm", line)
            if m:
                norm = m.group(1)
            m = re.search(r"Integrated weight \(pb\)\s*:\s*([-\d.eE+]+)", line)
            if m:
                xsec = float(m.group(1))
    return norm, xsec, (math.sqrt(sum(e * e for e in errs)) if errs else None)


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
    norm, xsec, xerr = banner(path)
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
    return mv, pt, wsum, n, xsec, xerr


def hist(pairs, edges, power=1):
    """The sum of the weights in each bin, or with power=2 the sum of their squares."""
    h = [0.0] * (len(edges) - 1)
    for x, w in pairs:
        i = min(max(int(x // (edges[1] - edges[0])), 0), len(h) - 1)
        h[i] += w ** power
    return h


def default_edges(start, xmax):
    """100 GeV bins to 800, 200 to 1600, 400 beyond, from the first filled bin to xmax (the bins of
    the paper's figures, which paper_figure.py takes from here)."""
    e, x = [start], start
    while x < xmax - 1e-9:
        step = 100 if x < 800 else 200 if x < 1600 else 400
        # the last bin absorbs a remainder shorter than a bin instead of becoming a sliver
        x = xmax if xmax - x < 2 * step else x + step
        e.append(x)
    return e


class Sample:
    """One histogram with what its errors need: per bin the sum of the weights (the histogram
    itself) and of their squares, and the error of the cross section it integrates to, None for a
    sample that is its own event sum."""

    def __init__(self, edges, sumw, sumw2, norm_err):
        self.edges, self.sumw, self.sumw2, self.norm_err = list(edges), list(sumw), list(sumw2), norm_err
        self.norm, self.w2 = sum(self.sumw), sum(self.sumw2)

    def part(self, lo, hi):
        """(sigma, error, share of the sample, error of the share) in [lo, hi), which must sit on
        bin edges.  The last bin holds the overflow, so a range that ends at the last edge does."""
        idx = [i for i in range(len(self.sumw)) if self.edges[i] >= lo - 1e-9 and self.edges[i + 1] <= hi + 1e-9]
        if not idx or abs(self.edges[idx[0]] - lo) > 1e-9 or abs(self.edges[idx[-1] + 1] - hi) > 1e-9:
            raise ValueError(f"[{lo}, {hi}) does not sit on the bin edges")
        s, w2 = sum(self.sumw[i] for i in idx), sum(self.sumw2[i] for i in idx)
        if not self.norm:
            return s, math.sqrt(w2), float("nan"), float("nan")
        f = s / self.norm
        # sum_i w_i^2 (1_range(i) - f)^2, which is norm^2 times the variance of the share
        var = max(w2 * (1 - 2 * f) + f * f * self.w2, 0.0)
        df = math.sqrt(var) / abs(self.norm)
        if self.norm_err is None:
            return s, math.sqrt(w2), f, df
        return s, math.sqrt(var + (f * self.norm_err) ** 2), f, df


def ratio(a, da, b, db):
    """a / |b| and its error, for a and b from independent samples."""
    if not b:
        return float("nan"), float("nan")
    r = a / abs(b)
    return r, math.sqrt(da * da + r * r * db * db) / abs(b)


TRUNC_HEAD = ["sample", "kind", "low_GeV", "high_GeV", "ref_pb", "ref_err_pb", "int_pb", "int_err_pb",
              "sq_pb", "sq_err_pb", "R", "R_err", "int_ref", "int_ref_err", "sq_ref", "sq_ref_err",
              "int_frac", "int_frac_err", "sq_frac", "sq_frac_err"]


def truncation_rows(ref, pairs):
    """The rows of the truncation table (TRUNC_HEAD), for the reference Sample and a list of
    (label, interference Sample or None, square Sample or None).  The bins start at the first bin
    the reference fills, and the upper cuts run over every bin edge above it."""
    edges = ref.edges
    first = min((i for i, v in enumerate(ref.sumw) if v != 0), default=0)
    be = default_edges(edges[first], edges[-1])
    ranges = [("bin", a, b) for a, b in zip(be[:-1], be[1:])] + [("cut", edges[0], c) for c in edges[first + 1:]]
    rows = []
    for label, si, sq in pairs:
        for kind, lo, hi in ranges:
            r0, dr0 = ref.part(lo, hi)[:2]
            I = si.part(lo, hi) if si else None
            Q = sq.part(lo, hi) if sq else None
            rows.append([label, kind, lo, hi, r0, dr0]
                        + (list(I[:2]) if I else [None] * 2) + (list(Q[:2]) if Q else [None] * 2)
                        + (list(ratio(Q[0], Q[1], I[0], I[1])) if I and Q else [None] * 2)
                        + (list(ratio(I[0], I[1], r0, dr0)) if I else [None] * 2)
                        + (list(ratio(Q[0], Q[1], r0, dr0)) if Q else [None] * 2)
                        + (list(I[2:]) if I else [None] * 2) + (list(Q[2:]) if Q else [None] * 2))
    return rows


def pairs_of(labels, stats):
    """(label, interference, square) for every label after the first, a label "<x> squared" being
    the square of <x>; a square given without its interference gets a row of its own."""
    sq = {l.strip()[:-len("squared")].strip(): l for l in labels[1:] if l.strip().endswith("squared")}
    out = [(l, stats[l], stats[sq[l.strip()]] if l.strip() in sq else None)
           for l in labels[1:] if not l.strip().endswith("squared")]
    named = {l.strip() for l in labels[1:]}
    return out + [(l, None, stats[l]) for b, l in sq.items() if b not in named]


def write_errors(prefix, labels, stats, name, edges):
    """<prefix>_<name>_err.tsv: the error of every bin of <prefix>_<name>.tsv."""
    with open(f"{prefix}_{name}_err.tsv", "w") as f:
        f.write("low_GeV\thigh_GeV\t" + "\t".join(labels) + "\n")
        for i in range(len(edges) - 1):
            f.write(f"{edges[i]}\t{edges[i+1]}\t" + "\t".join(f"{stats[l].part(edges[i], edges[i+1])[1]:.6g}" for l in labels) + "\n")
    print("wrote", f"{prefix}_{name}_err.tsv")


def write_truncation(prefix, labels, stats):
    """<prefix>_mVV_R.tsv, the truncation table of truncation_rows."""
    cell = lambda x: "-" if x is None else x if isinstance(x, str) else f"{x:.6g}"
    with open(f"{prefix}_mVV_R.tsv", "w") as f:
        f.write("\t".join(TRUNC_HEAD) + "\n")
        for row in truncation_rows(stats[labels[0]], pairs_of(labels, stats)):
            f.write("\t".join(cell(x) for x in row) + "\n")
    print("wrote", f"{prefix}_mVV_R.tsv")


def write_stat(prefix, labels, stats):
    """<prefix>_stat.json: {observable: {label: {edges, sumw, sumw2, norm_err}}}, for read_stat."""
    out = {name: {l: {"edges": s[l].edges, "sumw": s[l].sumw, "sumw2": s[l].sumw2, "norm_err": s[l].norm_err}
                  for l in labels} for name, s in stats.items()}
    with open(f"{prefix}_stat.json", "w") as f:
        json.dump(out, f)
    print("wrote", f"{prefix}_stat.json")


def read_stat(path, name="mVV"):
    """{label: Sample} for one observable of a <prefix>_stat.json."""
    return {l: Sample(d["edges"], d["sumw"], d["sumw2"], d["norm_err"]) for l, d in json.load(open(path))[name].items()}


def tables(prefix, samples):
    """The histograms of the event files of samples, [(label, path)], and their errors: writes <prefix>_mVV.tsv,
    _pT.tsv, their _err.tsv, _mVV_R.tsv and _stat.json, and returns the histograms by label.  main() calls it once
    the event files have checked out against their records."""
    results, stats = {}, {"mVV": {}, "pT": {}}
    for label, path in samples:
        mv, pt, wsum, n, xsec, xerr = analyse(path)
        h = ((hist(mv, MBINS), hist(mv, MBINS, 2)), (hist(pt, PBINS), hist(pt, PBINS, 2)))
        note, f = "", 1.0
        if xsec is not None and wsum and abs(wsum - xsec) > 1e-3 * max(abs(xsec), 1e-30):
            f = xsec / wsum
            note = f", rescaled by {f:.4g} to the integrated weight {xsec:.6g} pb"
        results[label] = tuple([x * f for x in h1] for h1, _ in h)
        # the squared weights scale with f^2, and the normalisation carries the integration's error
        # unless the banner gives no cross section, when the histogram is its own event sum
        if xsec is not None and xerr is None:
            xerr = 0.0; note += ", no integration error in the file, so the normalisation counts as exact"
        for (name, edges), (h1, h2) in zip((("mVV", MBINS), ("pT", PBINS)), h):
            stats[name][label] = Sample(edges, [x * f for x in h1], [x * f * f for x in h2], xerr if xsec is not None else None)
        print(f"{label}: {n} events, event sum {wsum:.6g} pb{note}")
    for name, edges, k in (("mVV", MBINS, 0), ("pT", PBINS, 1)):
        with open(f"{prefix}_{name}.tsv", "w") as f:
            f.write("low_GeV\thigh_GeV\t" + "\t".join(l for l, _ in samples) + "\n")
            for i in range(len(edges) - 1):
                f.write(f"{edges[i]}\t{edges[i+1]}\t" + "\t".join(f"{results[l][k][i]:.6g}" for l, _ in samples) + "\n")
        print("wrote", f"{prefix}_{name}.tsv")
    labels = [l for l, _ in samples]
    for name, edges in (("mVV", MBINS), ("pT", PBINS)):
        write_errors(prefix, labels, stats[name], name, edges)
    write_truncation(prefix, labels, stats["mVV"])
    write_stat(prefix, labels, stats)
    return results


def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    prefix, samples = argv[1], [a.split("=", 1) for a in argv[2:]]
    checked = provenance.require_events([p for _, p in samples], "plot_study.py")
    results = tables(prefix, samples)
    provenance.write_sources(prefix, [l for l, _ in samples], checked)
    print("wrote", f"{prefix}.sources.tsv")
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
