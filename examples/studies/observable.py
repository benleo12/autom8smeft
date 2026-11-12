#!/usr/bin/env python3
"""The distribution of any observable in the MadGraph event files of your own runs, with the signed weights kept.

    examples/studies/observable.py <observable> <edges> <label>=<unweighted_events.lhe.gz> [<label>=<file> ...] [--tsv <file>]

<observable> is a kind and the final-state particles it is computed from, as kind:particles:
    m       the invariant mass of their sum                          m:z,a        GeV
    pt      the transverse momentum of their sum                     pt:w+,w-     GeV
    y       the rapidity of their sum                                y:z,a
    ptmax   the largest transverse momentum of any one of them       ptmax:j      GeV
The particles are PDG ids or MadGraph names, separated by commas, with the sign ignored: a z w h g t b e mu ta,
ve vm vt, j for the gluon and the quarks d u s c b, l for e and mu, and all for every final-state particle.
<edges> are the bin edges, increasing and separated by commas, for example 200,300,400,600,1000,2000.

Each file is a sample, the first one usually the Standard Model, then the interference (NP^2==2) and the square
(NP<=2 NP^2==4).  The histogram of each sample integrates to its cross section in pb: the weights are averaged when
the run card has MadGraph's default event_norm = average, and the histogram is rescaled to the banner's integrated
weight, so the shape comes from the events and the normalisation from the phase-space integration.  The error of a
bin is that of its share of the event weights, with their signs, and the error of the integration, as
examples/studies/plot_study.py computes it for the paper's figures.  It prints one table per sample: every bin, the
events below the first edge and above the last, those in which none of the particles is present, and the total,
each with its error, and for every sample after the first the ratio to the first in each bin.  --tsv writes the
same numbers as one table, one row per bin and two columns per sample.

The generation cuts of the run card (mmll, ptj, ...) bound what the events can show.  A distribution below a cut is
empty, not small.

For an observable that is not one of these, import the reader and write the function, which gets the final-state
particles of an event as (PDG id, px, py, pz, E) in GeV and returns a number, or None when it is not defined:

    import sys; sys.path.insert(0, "examples/studies")
    from observable import histogram, mass, pick
    h = histogram("int.lhe.gz", lambda ps: mass(pick(ps, [11, 13])), [100, 200, 400, 800])
    for lo, hi, s, e in h.bins():
        print(lo, hi, s, e)

tests/test_observable.py checks the numbers against their definitions, event by event.
"""
import bisect, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from plot_study import Sample, banner, events, normalisation, ratio  # noqa: E402

NAMES = {"a": [22], "z": [23], "w": [24], "w+": [24], "w-": [24], "h": [25], "g": [21], "t": [6], "b": [5],
         "e": [11], "mu": [13], "ta": [15], "ve": [12], "vm": [14], "vt": [16],
         "j": [1, 2, 3, 4, 5, 21], "l": [11, 13]}


def final_states(path):
    """(weight, particles) for every event of an event file, the weight as the file gives it and the particles those
    of the final state (status 1) as (PDG id, px, py, pz, E) in GeV."""
    for lines in events(path):
        head = lines[0].split()
        nup, w = int(head[0]), float(head[2])
        ps = []
        for l in lines[1:1 + nup]:
            p = l.split()
            if int(p[1]) == 1:
                ps.append((int(p[0]), float(p[6]), float(p[7]), float(p[8]), float(p[9])))
        yield w, ps


def pick(ps, ids):
    """The particles of ps whose PDG id is in ids, up to its sign, and all of them for ids None."""
    return list(ps) if ids is None else [p for p in ps if abs(p[0]) in ids]


def total(ps):
    return tuple(sum(p[i] for p in ps) for i in (1, 2, 3, 4))


def mass(ps):
    """The invariant mass of the sum of ps, None when ps is empty."""
    if not ps:
        return None
    px, py, pz, E = total(ps)
    return math.sqrt(max(E * E - px * px - py * py - pz * pz, 0.0))


def pt(ps):
    """The transverse momentum of the sum of ps, None when ps is empty."""
    if not ps:
        return None
    px, py, _, _ = total(ps)
    return math.hypot(px, py)


def rapidity(ps):
    """The rapidity of the sum of ps, None when ps is empty or the sum moves along the beam at the speed of light."""
    if not ps:
        return None
    _, _, pz, E = total(ps)
    return 0.5 * math.log((E + pz) / (E - pz)) if E > abs(pz) else None


def ptmax(ps):
    """The largest transverse momentum of any one particle of ps, None when ps is empty."""
    return max((math.hypot(p[1], p[2]) for p in ps), default=None)


KINDS = {"m": mass, "pt": pt, "y": rapidity, "ptmax": ptmax}


def parse(spec):
    """The function of the particles that the observable kind:particles names, or a ValueError that says why not."""
    kind, _, parts = spec.partition(":")
    if kind not in KINDS or not parts:
        raise ValueError(f"observable '{spec}': the form is kind:particles with the kind one of {', '.join(KINDS)}, "
                         "as in m:z,a")
    ids = set()
    for x in parts.lower().split(","):
        if x == "all":
            ids = None
            break
        if x.lstrip("-").isdigit():
            ids.add(abs(int(x)))
        elif x in NAMES:
            ids.update(NAMES[x])
        else:
            raise ValueError(f"observable '{spec}': no particle '{x}', give a PDG id or one of {' '.join(NAMES)} all")
    f = KINDS[kind]
    return lambda ps: f(pick(ps, ids))


class Histogram:
    """The histogram of one observable over one event file.  The bins are those of the edges given, between them
    the range below the first edge, the range above the last and the events with no value, so that the parts
    together hold the whole sample and integrate to its cross section."""

    def __init__(self, path, func, edges):
        edges = [float(x) for x in edges]
        if len(edges) < 2 or any(b <= a for a, b in zip(edges, edges[1:])):
            raise ValueError(f"bin edges {edges}: give at least two, increasing")
        norm, xsec, xerr = banner(path)
        # parts: 0 no value, 1 below the first edge, 2 ... the bins, last above the last edge
        n_parts = len(edges) + 2
        sumw, sumw2, count, wsum = [0.0] * n_parts, [0.0] * n_parts, [0] * n_parts, 0.0
        for w, ps in final_states(path):
            x = func(ps)
            k = 0 if x is None else 1 + bisect.bisect_right(edges, x)
            sumw[k] += w; sumw2[k] += w * w; count[k] += 1; wsum += w
        n = sum(count)
        if n == 0:
            raise ValueError(f"{path}: no events")
        if norm == "average":
            # MadGraph's default: every event carries the whole cross section, which is the mean of the weights
            sumw, sumw2, wsum = [x / n for x in sumw], [x / (n * n) for x in sumw2], wsum / n
        f, nerr, self.note = normalisation(wsum, xsec, xerr)
        self.edges, self.n, self.wsum, self.n_undefined = edges, n, wsum, count[0]
        # the parts on edges 0, 1, 2, ..., which Sample needs only to tell them apart
        self.sample = Sample(range(n_parts + 1), [x * f for x in sumw], [x * f * f for x in sumw2], nerr)

    def part(self, k):
        """(sigma, error) of part k: 0 the events with no value, 1 below the first edge, 2 ... the bins, and
        len(edges) + 1 above the last edge."""
        return self.sample.part(k, k + 1)[:2]

    def bins(self):
        """(low, high, sigma, error) for every bin, in pb."""
        return [(self.edges[i], self.edges[i + 1]) + self.part(2 + i) for i in range(len(self.edges) - 1)]

    def below(self):
        return self.part(1)

    def above(self):
        return self.part(len(self.edges) + 1)

    def undefined(self):
        return self.part(0)

    def total(self):
        return self.sample.part(0, len(self.edges) + 2)[:2]


def histogram(path, func, edges):
    """The Histogram of func, a function of the final-state particles of an event, over the event file path."""
    return Histogram(path, func, edges)


def main(argv):
    args, tsv = list(argv[1:]), None
    if "--tsv" in args:
        i = args.index("--tsv")
        if i + 1 >= len(args):
            print("observable.py: --tsv needs a file name"); return 2
        tsv = args[i + 1]; del args[i:i + 2]
    if len(args) < 3:
        print(__doc__); return 2
    spec, edges_text, samples = args[0], args[1], [a.split("=", 1) for a in args[2:]]
    try:
        func = parse(spec)
        edges = [float(x) for x in edges_text.split(",")]
        bad = [a[0] for a in samples if len(a) != 2 or not a[1]]
        if bad:
            raise ValueError(f"give each sample as label=file, not {bad[0]}")
        missing = [p for _, p in samples if not os.path.isfile(p)]
        if missing:
            raise ValueError(f"no file {missing[0]}")
        hs = [(label, histogram(path, func, edges)) for label, path in samples]
    except ValueError as e:
        print(f"observable.py: {e}"); return 2
    ref_label, ref = hs[0]
    for label, h in hs:
        print(f"{label}: {h.n} events, event sum {h.wsum:.6g} pb{h.note}")
        print(f"  {spec:>18s}   {'sigma [pb]':>12s} {'error [pb]':>10s}" + (f"   {'ratio to ' + ref_label:>24s}" if h is not ref else ""))
        rows = [(f"{lo:g} - {hi:g}", s, e, (ref.bins()[i][2], ref.bins()[i][3])) for i, (lo, hi, s, e) in enumerate(h.bins())]
        rows += [(f"below {edges[0]:g}", *h.below(), ref.below()), (f"above {edges[-1]:g}", *h.above(), ref.above())]
        if h.n_undefined or ref.n_undefined:
            rows.append(("not defined", *h.undefined(), ref.undefined()))
        rows.append(("total", *h.total(), ref.total()))
        for name, s, e, (rs, re_) in rows:
            line = f"  {name:>18s}   {s:+12.4e} {e:10.2e}"
            if h is not ref:
                r, dr = ratio(s, e, rs, re_)
                line += "   " + (f"{r:+12.4e} +- {dr:8.2e}" if r == r else f"{'-':>24s}")
            print(line)
    if tsv:
        with open(tsv, "w") as f:
            f.write("low\thigh\t" + "\t".join(f"{l}\t{l}_err" for l, _ in hs) + "\n")
            for i in range(len(edges) - 1):
                f.write(f"{edges[i]:g}\t{edges[i + 1]:g}\t"
                        + "\t".join(f"{h.bins()[i][2]:.6g}\t{h.bins()[i][3]:.6g}" for _, h in hs) + "\n")
        print("wrote", tsv)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
