"""
tests/test_geo_basis.py  --  the class-11 operators of the default basis (gen/basis.py).

Run:  python3.11 tests/test_geo_basis.py [model ...]

Four checks.

1. They are a basis of class 11: the contact amplitudes of two fermions and two Higgs bosons of the fifteen
   operators of the default basis and of the fifteen of the Murphy basis have the same span, for each field
   content, with one, two and three generations of general flavour, and its dimension is the number of
   operators the Hilbert series gives (Murphy's Table 2).  The amplitudes are those of
   validate/flavour_rank.py: random massless kinematics and gauge and flavour wave functions, on shell, where
   integration by parts and the equations of motion relate no two amplitudes that differ.  Each Murphy
   operator is then fitted by those of the default basis with one generation, and the fit must be exact with
   the coefficients gen/basis.py states.
2. Every Higgs field of every term of the fifteen carries a derivative, as gen/operators.py writes them, so
   that the vacuum value of a Higgs field leaves no vertex with fewer than four fields.
3. In each model named on the command line, by default models/dim8_mw and models/dim8_mw_murphy where they
   are present: no vertex with fewer than four legs carries a class-11 coefficient of the default basis, and in
   a Murphy-basis model a three-point vertex does carry one of its class-11 coefficients, which is the
   difference between the bases that the test must see.
4. In the same models, over every dimension-eight coefficient, its flavour structures included: the classes
   with a vertex of at most three legs are exactly those whose operators make up the field-space connections
   of the geometric SMEFT at dimension eight (arXiv:2001.01453), H^8, H^6D^2, X^3H^2, X^2H^4, XH^4D^2,
   psi^2XH^3, psi^2H^5 and psi^2H^4D, in a model of the default basis, and these and psi^2H^2D^3 in a model of
   the Murphy basis, where the operators outside them with such a vertex are its fifteen of class 11.  A class
   of the connections with no such vertex fails it too, so that a reader that finds nothing cannot pass.
"""
from __future__ import annotations

import collections
import os
import re
import sys

import numpy as np

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "gen"))
sys.path.insert(0, os.path.join(ROOT, "validate"))

import basis  # noqa: E402
import flavour_rank as FR  # noqa: E402
from dsl import H  # noqa: E402
from operators import OPS  # noqa: E402

cases = []


def check(name, got, want):
    cases.append((name, got, want))


def plans(ops):
    g = collections.defaultdict(list)
    for o in ops:
        for conj in ((False, True) if o.hc_mode == "complex" else (False,)):
            p = FR.OpPlan(o, conj)
            g[p.keys].append(p)
    return g


def span():
    by_wc = {o.wc: o for o in OPS}
    murphy = [by_wc[w] for w in basis.MURPHY]
    geo = [by_wc[w] for w in basis.GEO]
    gm, gg = plans(murphy), plans(geo)
    check("the two forms of class 11 have the same field contents", sorted(map(str, gm)), sorted(map(str, gg)))
    # the fit of each Murphy operator by those of the default basis, as gen/basis.py states it
    pair = {"x1": {"g1": 0.25, "g2": -0.25}, "x2": {"g1": -0.25, "g2": -0.25},
            "x3": {"g3": 0.25, "g4": -0.25}, "x4": {"g3": -0.25, "g4": -0.25}}
    for ng in (1, 2, 3):
        rng = np.random.default_rng(20261107 + ng)
        tot = collections.Counter()
        for keys in sorted(gm, key=str):
            both = gm[keys] + gg[keys]
            nrow = sum(ng ** len(p.gens) for p in both)
            ncfg = nrow + 40
            M = np.zeros((nrow, ncfg), complex)
            S = np.zeros((nrow, ncfg))
            for c in range(ncfg):
                wf = FR.wavefunctions(keys, ng, rng)
                amps = [p.amplitude(wf, ng) for p in both]
                M[:, c] = np.concatenate([a.ravel() for a, _ in amps])
                S[:, c] = np.concatenate([z.ravel() for _, z in amps])
            nm = sum(ng ** len(p.gens) for p in gm[keys])
            rm, _ = FR.rank(M[:nm], S[:nm], "murphy")
            rg, _ = FR.rank(M[nm:], S[nm:], "geo")
            rb, _ = FR.rank(M, S, "both")
            tot["murphy"] += rm
            tot["geo"] += rg
            tot["both"] += rb
            check(f"n_g = {ng}, {keys}: the rank of each form and of the two together", (rm, rg, rb), (rm, rm, rm))
            if ng == 1:
                A = M[nm:].T
                for i, p in enumerate(gm[keys]):
                    x, *_ = np.linalg.lstsq(A, M[i], rcond=None)
                    got = {q.op.wc[-2:] if q.op.wc[-2] == "g" else "g": complex(v) for v, q in zip(x, gg[keys])}
                    want = pair.get(p.op.wc[-2:], {"g": -0.5})
                    ok = all(abs(got.get(k, 0) - want.get(k, 0)) < 1e-9 for k in set(got) | set(want))
                    res = np.linalg.norm(A @ x - M[i]) / np.linalg.norm(M[i])
                    check(f"{p.op.wc}{'^dag' if p.conj else ''} is the combination of gen/basis.py, exactly",
                          (ok, res < 1e-10), (True, True))
        want = FR.murphy_nop(11, ng)
        check(f"n_g = {ng}: the rank of class 11 in either form is the Hilbert series count",
              (tot["murphy"], tot["geo"], tot["both"]), (want, want, want))


def derivatives():
    by_wc = {o.wc: o for o in OPS}
    bare = [(w, i) for w in basis.GEO for i, t in enumerate(by_wc[w].terms)
            for f in t.factors if isinstance(f, H) and not f.derivs]
    check("every Higgs field of the default class 11 carries a derivative", bare, [])
    some = [w for w in basis.MURPHY if any(isinstance(f, H) and not f.derivs for f in by_wc[w].terms[0].factors)]
    check("and every Murphy operator of class 11 has a Higgs field without one", sorted(some), sorted(basis.MURPHY))


def legs(model):
    """{coefficient: smallest number of legs of a vertex whose couplings carry it}, for class 11."""
    couplings = open(os.path.join(model, "couplings.py"), errors="replace").read()
    names = set(basis.MURPHY) | set(basis.GEO)
    of = {}
    for m in re.finditer(r"(GC_\w+) = Coupling\(name = '\w+',\s*value = '([^']*)'", couplings):
        found = {re.sub(r"(Re|Im)$", "", n) for n in re.findall(r"\b(c8\w+?)\b", m.group(2))} & names
        if found:
            of[m.group(1)] = found
    out = {}
    vertices = open(os.path.join(model, "vertices.py"), errors="replace").read()
    for m in re.finditer(r"Vertex\(name = '\w+',\s*particles = \[([^\]]*)\].*?couplings = \{([^}]*)\}", vertices, re.S):
        n = m.group(1).count("P.")
        for g in set(re.findall(r"C\.(GC_\w+)", m.group(2))):
            for w in of.get(g, ()):
                out[w] = min(out.get(w, 99), n)
    return out


# the classes whose operators make up the connections at dimension eight: H^8, H^6D^2, X^3H^2, X^2H^4, XH^4D^2,
# psi^2XH^3, psi^2H^5 and psi^2H^4D, in the numbering of the Murphy basis
CONNECTIONS = {2, 3, 5, 6, 8, 10, 12, 13}


def small(model):
    """{block: smallest number of legs of a vertex whose couplings carry a coefficient of the block}, over every
    block of docs/block_index.json, a coefficient of a flavour structure counting for its block."""
    import json
    blk = {}
    for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json"))):
        for n in list(e["wcs"]) + [re.sub(r"(Re|Im)$", "", f) for f in e.get("flavour", [])]:
            blk[n] = e["block"]
    couplings = open(os.path.join(model, "couplings.py"), errors="replace").read()
    of = {}
    for m in re.finditer(r"(GC_\w+) = Coupling\(name = '\w+',\s*value = '([^']*)'", couplings):
        found = {blk[n] for n in (re.sub(r"(Re|Im)$", "", x) for x in re.findall(r"\b(c8\w+?)\b", m.group(2))) if n in blk}
        if found:
            of[m.group(1)] = found
    out = {}
    vertices = open(os.path.join(model, "vertices.py"), errors="replace").read()
    for m in re.finditer(r"Vertex\(name = '\w+',\s*particles = \[([^\]]*)\].*?couplings = \{([^}]*)\}", vertices, re.S):
        n = m.group(1).count("P.")
        for g in set(re.findall(r"C\.(GC_\w+)", m.group(2))):
            for b in of.get(g, ()):
                out[b] = min(out.get(b, 99), n)
    return out


def models(argv):
    import json
    idx = {e["block"]: e for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json")))}
    paths = argv or [os.path.join(ROOT, "models", n) for n in ("dim8_mw", "dim8_mw_murphy")]
    for model in paths:
        if not os.path.isfile(os.path.join(model, "vertices.py")):
            print(f"no model at {model}, check 3 left out there")
            continue
        b = basis.of_model(model)
        smallest = legs(model)
        mine = basis.GEO if b == "geo" else basis.MURPHY
        check(f"{os.path.basename(model)}: every class-11 coefficient of its basis has a vertex",
              sorted(w for w in mine if w not in smallest), [])
        check(f"{os.path.basename(model)}: no class-11 coefficient of the other basis",
              sorted(w for w in smallest if w not in mine), [])
        if b == "geo":
            check(f"{os.path.basename(model)}: no class-11 vertex with fewer than four legs",
                  sorted(w for w in mine if smallest.get(w, 99) < 4), [])
        else:
            check(f"{os.path.basename(model)}: the Murphy basis has class-11 vertices with three legs",
                  any(smallest.get(w, 99) == 3 for w in mine), True)
        few = {x for x, n in small(model).items() if n <= 3}
        want = CONNECTIONS | ({11} if b == "murphy" else set())
        check(f"{os.path.basename(model)}: the classes with a vertex of at most three legs",
              sorted({idx[x]["cls"] for x in few}), sorted(want))
        check(f"{os.path.basename(model)}: the operators outside the connections with such a vertex",
              sorted(idx[x]["wcs"][0] for x in few if idx[x]["cls"] not in CONNECTIONS),
              sorted(basis.MURPHY) if b == "murphy" else [])


def main(argv) -> int:
    span()
    derivatives()
    models(argv[1:])
    bad = [(n, g, w) for n, g, w in cases if g != w]
    for n, g, w in cases:
        print(("ok   " if g == w else "FAIL ") + n + ("" if g == w else f"\n       got {g!r}\n       want {w!r}"))
    print(f"\n{len(cases) - len(bad)}/{len(cases)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
