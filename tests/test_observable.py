"""
tests/test_observable.py  --  the distributions that examples/studies/observable.py makes from the event files of a run.

Run:  python3 tests/test_observable.py

  1. The observables of a Z and a photon built with a known mass, transverse momentum and rapidity of their sum, and
     of each one alone, in all four kinds, with the initial state and a particle of status 2 in the event as well.
  2. Every bin, the ranges below and above the edges, the events without the particle and the total, each with its
     error, against the definition event by event: the weights averaged under event_norm = average and taken as they
     are under sum, rescaled to the banner, error^2 = sum_i u_i^2 (1_part(i) - share)^2 + share^2 xerr^2.  Signed
     weights, events on the bin edges (in the bin above the edge, the last edge in the range above), a file whose
     event sum sits off its banner, and one with no photon in some events.  The parts add up to the banner's cross
     section and the total has the integration's error.
  3. The mass of the W pair is the invariant mass that plot_study.py histograms for the paper's figures, bin by bin.
  4. The command: what it refuses (exit 2, with the reason), its printed table and ratio column, and --tsv.
"""
import gzip
import math
import os
import subprocess
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "examples", "studies"))
import observable as O  # noqa: E402
import plot_study as P  # noqa: E402

SCRIPT = os.path.join(ROOT, "examples", "studies", "observable.py")
MZ = 91.1876


def close(a, b, rel=1e-9, tiny=1e-15):
    return abs(a - b) <= rel * max(abs(a), abs(b)) + tiny


def write_lhe(path, xsec, xerr, evs, norm="average"):
    """A MadGraph event file: evs is [(weight, [(pdg id, status, px, py, pz, E, m), ...])], two incoming gluons
    added to each event."""
    with gzip.open(path, "wt") as f:
        f.write(f'<LesHouchesEvents version="3.0">\n<header>\n  {norm} =  event_norm       ! average/sum\n')
        f.write(f"#  Integrated weight (pb)  :       {xsec!r}\n</header>\n<init>\n")
        f.write("2212 2212 6.800000e+03 6.800000e+03 0 0 247000 247000 -4 1\n")
        f.write(f"{xsec:e} {xerr:e} {max(abs(w) for w, _ in evs):e} 1\n</init>\n")
        for w, ps in evs:
            E = sum(p[5] for p in ps)
            pz = sum(p[4] for p in ps)
            f.write(f"<event>\n {len(ps) + 2:2d}      1 {w:+.12e} 1.0e+02 7.5e-03 1.2e-01\n")
            f.write(f"       21 -1 0 0 501 502 +0.0 +0.0 {(E + pz) / 2:+.12e} {(E + pz) / 2:.12e} 0.0 0.0 1.0\n")
            f.write(f"       21 -1 0 0 502 501 -0.0 -0.0 {-(E - pz) / 2:+.12e} {(E - pz) / 2:.12e} 0.0 0.0 -1.0\n")
            for pid, st, px, py, pz_, e, m in ps:
                f.write(f"  {pid:7d} {st:2d} 1 2 0 0 {px:+.12e} {py:+.12e} {pz_:+.12e} {e:.12e} {m:.6e} 0.0 1.0\n")
            f.write("</event>\n")
        f.write("</LesHouchesEvents>\n")


def pair(M, a, Y, m1, m2, theta=0.7):
    """Two particles of masses m1 and m2 whose sum has the mass M, the transverse momentum M sinh(a) along x and the
    rapidity Y: back to back at theta to the beam in their rest frame, then boosted along x by a and along z by Y."""
    E1, E2 = (M * M + m1 * m1 - m2 * m2) / (2 * M), (M * M + m2 * m2 - m1 * m1) / (2 * M)
    q = math.sqrt(E1 * E1 - m1 * m1)
    out = []
    for E, s, m in ((E1, 1, m1), (E2, -1, m2)):
        px, py, pz = s * q * math.sin(theta), 0.0, s * q * math.cos(theta)
        E, px = E * math.cosh(a) + px * math.sinh(a), px * math.cosh(a) + E * math.sinh(a)
        E, pz = E * math.cosh(Y) + pz * math.sinh(Y), pz * math.cosh(Y) + E * math.sinh(Y)
        out.append((px, py, pz, E, m))
    return out


def za(M, a=0.0, Y=0.0):
    (z, g) = pair(M, a, Y, MZ, 0.0)
    return [(23, 1) + z, (22, 1) + g]


def check_kinematics():
    M, a, Y = 750.0, 0.4, -0.9
    ps = [(p[0],) + p[2:6] for p in za(M, a, Y)]
    # a photon of status 2 and the initial state must not enter
    ev = za(M, a, Y) + [(22, 2, 30.0, 5.0, 1.0, math.sqrt(926.0), 0.0)]
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "k.lhe.gz")
        write_lhe(f, 1.0, 0.0, [(1.0, ev)])
        (w, got), = list(O.final_states(f))
        assert w == 1.0 and len(got) == 2 and all(close(x, y, 1e-11) for p, q in zip(got, ps) for x, y in zip(p, q)), got
    z_pt = math.hypot(ps[0][1], ps[0][2])
    want = {"m:z,a": M, "m:23,-22": M, "pt:z,a": M * math.sinh(a), "y:z,a": Y, "y:all": Y,
            "ptmax:z,a": max(z_pt, math.hypot(ps[1][1], ps[1][2])), "pt:z": z_pt, "m:z": MZ}
    for spec, v in want.items():
        assert close(O.parse(spec)(ps), v, 1e-9, 1e-7), (spec, O.parse(spec)(ps), v)
    # a kind or a particle that does not exist is refused, and an event without the particle has no value
    for bad in ("mass:z", "m:", "m:zz", "pt"):
        try:
            O.parse(bad)
            raise AssertionError(f"{bad} was accepted")
        except ValueError:
            pass
    assert O.parse("pt:w")(ps) is None and O.parse("y:a")([(22, 0.0, 0.0, 5.0, 5.0)]) is None
    return 1


def by_definition(evs, xsec, xerr, norm, inside):
    """(sigma, error) of the events for which inside(event) holds, from the definition."""
    n = len(evs)
    u = [w / n if norm == "average" else w for w, _ in evs]
    if abs(sum(u) - xsec) > 1e-3 * abs(xsec):
        u = [x * xsec / sum(u) for x in u]
    tot = sum(u)
    ins = [inside(ps) for _, ps in evs]
    h = sum(x for x, i in zip(u, ins) if i)
    f = h / tot
    var = sum(x * x * ((1.0 if i else 0.0) - f) ** 2 for x, i in zip(u, ins))
    return h, math.sqrt(var + (f * xerr) ** 2)


def photon(ptv, extra=()):
    """A Z and a photon of transverse momentum ptv, the photon along x, so that pt:a is exactly ptv."""
    return [(23, 1, -ptv, 0.0, 40.0, math.sqrt(ptv * ptv + 1600.0 + MZ * MZ), MZ), (22, 1, ptv, 0.0, 60.0, math.hypot(ptv, 60.0), 0.0)] + list(extra)


def check_parts():
    edges = [100.0, 200.0, 400.0, 800.0]
    # on the edges 100, 200 and 800, below, above, and four events with no photon, with signed weights
    pts = [50, 100, 100, 150, 199.5, 200, 260, 390, 400, 640, 800, 1200]
    ws = [0.9, -0.9, 0.9, 0.9, -0.9, 0.9, 0.9, -0.9, 0.9, -0.9, 0.9, 0.9]
    evs = [(w, photon(p)) for p, w in zip(pts, ws)]
    evs += [(0.9, [(23, 1, 0.0, 0.0, 10.0, math.hypot(MZ, 10.0), MZ)]), (-0.9, [(23, 1, 0.0, 0.0, -5.0, math.hypot(MZ, 5.0), MZ)]),
            (0.9, [(22, 2, 300.0, 0.0, 0.0, 300.0, 0.0), (11, 1, 1.0, 0.0, 0.0, 1.0, 0.0)]), (0.9, [(21, 1, 300.0, 0.0, 0.0, 300.0, 0.0)])]
    ptof = lambda ps: next((math.hypot(p[2], p[3]) for p in ps if p[0] == 22 and p[1] == 1), None)
    ok = 0
    # the weights sum to 5.4: the average file's event sum 5.4/16 sits off its banner, 0.21, and is rescaled, and
    # the sum file's is its banner
    for norm, xsec, xerr in (("average", 0.21, 0.004), ("sum", 5.4, 0.05)):
        with tempfile.TemporaryDirectory() as tmp:
            f = os.path.join(tmp, "p.lhe.gz")
            write_lhe(f, xsec, xerr, evs, norm)
            h = O.histogram(f, O.parse("pt:a"), edges)
        assert h.n == len(evs) and h.n_undefined == 4, (h.n, h.n_undefined)
        for (lo, hi, s, e), i in zip(h.bins(), range(3)):
            want = by_definition(evs, xsec, xerr, norm, lambda ps: ptof(ps) is not None and edges[i] <= ptof(ps) < edges[i + 1])
            assert close(s, want[0]) and close(e, want[1]) and (lo, hi) == (edges[i], edges[i + 1]), (norm, i, s, e, want)
        for got, inside in ((h.below(), lambda ps: ptof(ps) is not None and ptof(ps) < 100),
                            (h.above(), lambda ps: ptof(ps) is not None and ptof(ps) >= 800),
                            (h.undefined(), lambda ps: ptof(ps) is None)):
            want = by_definition(evs, xsec, xerr, norm, inside)
            assert close(got[0], want[0]) and close(got[1], want[1]), (norm, got, want)
        parts = [s for *_, s, _ in h.bins()] + [h.below()[0], h.above()[0], h.undefined()[0]]
        assert close(sum(parts), xsec, 1e-12) and close(h.total()[0], xsec, 1e-12) and close(h.total()[1], xerr), (norm, sum(parts), h.total())
        ok += 1
    return ok


def check_plot_study():
    """The pair mass of W+ W- events, binned as plot_study.py bins it for the figures (100 GeV to 6 TeV, the overflow
    in the last bin), is that of observable.py with m:w+,w- on the same edges."""
    masses = [170.5, 199.9, 200.0, 333.0, 812.0, 1999.0, 2475.0, 5950.0, 6400.0]
    ws = [1.2, 1.2, -1.2, 1.2, -1.2, 1.2, 1.2, -1.2, -1.2]
    evs = []
    for k, (m, w) in enumerate(zip(masses, ws)):
        (p, q) = pair(m, 0.3 * k / len(masses), 0.2 * k - 0.5, 80.4, 80.4)
        evs.append((w, [(24, 1) + p, (-24, 1) + q, (21, 1, 20.0, 0.0, 3.0, math.hypot(20.0, 3.0), 0.0)]))
    with tempfile.TemporaryDirectory() as tmp:
        f = os.path.join(tmp, "ww.lhe.gz")
        write_lhe(f, 0.41, 0.01, evs)
        mv, _, wsum, n, xsec, xerr = P.analyse(f)
        fac = P.normalisation(wsum, xsec, xerr)[0]
        want = [x * fac for x in P.hist(mv, P.MBINS)]
        h = O.histogram(f, O.parse("m:w+,w-"), P.MBINS)
    got = [s for *_, s, _ in h.bins()]
    # plot_study's last bin holds the overflow, which observable.py keeps apart
    got[-1] += h.above()[0]
    assert sum(1 for x in want if x) >= 7 and all(close(a, b, 1e-12) for a, b in zip(got, want)), (got, want)
    return 1


def cli(*args):
    return subprocess.run([sys.executable, SCRIPT, *args], capture_output=True, text=True, timeout=120)


def check_command():
    with tempfile.TemporaryDirectory() as tmp:
        sm, it = os.path.join(tmp, "sm.lhe.gz"), os.path.join(tmp, "int.lhe.gz")
        write_lhe(sm, 2.0, 0.02, [(2.0, za(m)) for m in (250, 320, 520, 900)])
        write_lhe(it, -0.1, 0.01, [(w, za(m)) for m, w in ((260, -0.1), (330, 0.1), (510, -0.1), (2500, -0.1))])
        for args, why in ((["m:z,a", "300,200", f"SM={sm}"], "increasing"), (["mass:z,a", "200,300", f"SM={sm}"], "the form is"),
                          (["m:z,q", "200,300", f"SM={sm}"], "no particle 'q'"), (["m:z,a", "200,300", "SM=" + sm + "x"], "no file"),
                          (["m:z,a", "200,300", sm], "label=file")):
            r = cli(*args)
            assert r.returncode == 2 and why in r.stdout, (args, r.returncode, r.stdout)
        r = cli()
        assert r.returncode == 2 and "kind:particles" in r.stdout
        tsv = os.path.join(tmp, "za.tsv")
        r = cli("m:z,a", "200,300,600,1000", f"SM={sm}", f"int={it}", "--tsv", tsv)
        assert r.returncode == 0, r.stdout + r.stderr
        hs = {l: O.histogram(p, O.parse("m:z,a"), [200, 300, 600, 1000]) for l, p in (("SM", sm), ("int", it))}
        rows = [l.split("\t") for l in open(tsv).read().split("\n") if l]
        assert rows[0] == ["low", "high", "SM", "SM_err", "int", "int_err"] and len(rows) == 4, rows
        for row, b6, bi in zip(rows[1:], hs["SM"].bins(), hs["int"].bins()):
            assert [float(x) for x in row] == [float(f"{x:.6g}") for x in (b6[0], b6[1], b6[2], b6[3], bi[2], bi[3])], (row, b6, bi)
        # the interference's bin from 300 to 600 GeV is +0.1/4 - 0.1/4 = 0 and the SM's 1.0, so its ratio is 0
        line = next(l for l in r.stdout.split("\n") if l.strip().startswith("300 - 600") and "+-" in l)
        r_, d = P.ratio(hs["int"].bins()[1][2], hs["int"].bins()[1][3], hs["SM"].bins()[1][2], hs["SM"].bins()[1][3])
        assert f"{r_:+12.4e}" in line and f"{d:8.2e}" in line and abs(r_) < 1e-15, (line, r_, d)
        assert "above 1000" in r.stdout and "not defined" not in r.stdout and "wrote" in r.stdout
    return 1


def main() -> int:
    ok = check_kinematics()
    ok += check_parts()
    ok += check_plot_study()
    ok += check_command()
    print(f"tests/test_observable.py: {ok}/5 checks pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
