#!/usr/bin/env python3
"""The power of lambda of every dimension-eight class in a process, by its cheapest tree.

    gen/lambda_routes.py "p p > w+ w-" [--n 4]

A tree is the product of its vertices and propagators.  In the energy-enhanced counting of the
paper (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1): a Standard Model three-point vertex
carries a momentum and counts lambda^-2 or a vev and counts lambda^-1, a four-point vertex
counts lambda^0, a propagator lambda^4, and a dimension-eight vertex with m legs and p vacuum
insertions lambda^(2m-4+p).  The Standard Model amplitude of an n-point process is lambda^(2n-8),
so a class entering at lambda^(2n-8+Delta) has M8/MSM ~ E^(8-Delta) v^(Delta-4) / Lambda^4.

For every operator of a class, every vertex in the selector's list (build/vertex_index.json)
and every way of hanging the external particles on it through Standard Model vertices (the
same recursion as gen/process.py, with the light-quark and lepton Yukawa couplings removed,
since those routes are suppressed by the quark masses), the cheapest tree is kept.  The number
of vacuum insertions of a vertex is the operator's number of Higgs fields minus the Higgs legs
of the vertex.  Classes that enter only through the input relations have no tree here and are
lambda^(2n-8+8).  Whether a class interferes with the Standard Model is a separate question
(chirality, or a gluon-initiated channel with no tree-level SM amplitude); the tables of the
paper answer it, this script does not.  The number of external legs n is read from the process
unless --n is given.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import process as P  # noqa: E402

INF = 10 ** 6
BOSONS = {"A", "Z", "W", "Wbar", "G", "H"}
CLASSES = {1: "X^4", 2: "H^8", 3: "H^6D^2", 4: "H^4D^4", 5: "X^3H^2", 6: "X^2H^4", 7: "X^2H^2D^2",
           8: "XH^4D^2", 9: "psi^2X^2H", 10: "psi^2XH^3", 11: "psi^2H^2D^3", 12: "psi^2H^5",
           13: "psi^2H^4D", 14: "psi^2X^2D", 15: "psi^2XH^2D", 16: "psi^2XHD^2", 17: "psi^2H^3D^2",
           18: "psi^4H^2", 19: "psi^4X", 20: "psi^4HD", 21: "psi^4D^2"}


class Cheapest:
    """Minimal lambda cost for a leg to reach a group of externals through SM vertices."""

    def __init__(self, sm):
        self.sm = [tuple(sorted(v)) for v in sm]
        self.by = {}
        for v in self.sm:
            for f in set(v):
                for m in set(P._members(f)) | {f}:
                    self.by.setdefault(m, []).append(v)
        self.cache = {}

    def _cands(self, f):
        seen, out = set(), []
        for key in set(P._members(f)) | {f}:
            for v in self.by.get(key, ()):
                if v not in seen:
                    seen.add(v)
                    out.append(v)
        return out

    @staticmethod
    def weight(v):
        n_h = v.count("H")
        if n_h and any(x not in BOSONS for x in v):
            return None                     # a Yukawa vertex: not a route for light fermions
        if len(v) == 3:
            return -1 if n_h else -2        # hVV and hhh carry a vev, the others a momentum
        return 0

    def reach(self, f, group):
        if len(group) == 1 and P._same_field(f, group[0]):
            return 0
        key = (f, group)
        if key in self.cache:
            return self.cache[key]
        self.cache[key] = INF
        best, af = INF, P.anti(f)
        for v in self._cands(af):
            w = self.weight(v)
            if w is None:
                continue
            rest = list(v)
            for i, x in enumerate(rest):
                if P._same_field(x, af):
                    rest.pop(i)
                    break
            else:
                continue
            if len(rest) < 2 or len(rest) > len(group):
                continue
            for parts in P._partitions(group, len(rest)):
                c = w + 4
                for i in range(len(rest)):
                    c += self.reach(rest[i], parts[i])
                    if c >= INF:
                        break
                best = min(best, c)
        self.cache[key] = best
        return best

    def vertex(self, legs, externals):
        best = INF
        for parts in P._partitions(externals, len(legs)):
            c = 0
            for i in range(len(legs)):
                c += self.reach(legs[i], parts[i])
                if c >= INF:
                    break
            best = min(best, c)
        return best


def routes(proc, vertex_index, base_vertices, catalogue):
    """class -> (lambda power, p, operator label, vertex legs) of the cheapest tree."""
    slots = P.parse_process(proc, collapse=True)
    assignments = {tuple(sorted(a)) for a in P._product(slots)}
    cheap = Cheapest(P.standard_model_vertices(base_vertices))
    best = {}
    for block, verts in vertex_index.items():
        e = catalogue.get(block)
        if not e or int(block[4:]) >= 675:
            continue
        n_higgs = e["fields"]["N_H"]
        for legs in verts:
            p = n_higgs - legs.count("H")
            w8 = 2 * len(legs) - 4 + p
            for ext in assignments:
                c = cheap.vertex(list(legs), ext)
                if c >= INF:
                    continue
                k = e["cls"]
                if k not in best or w8 + c < best[k][0]:
                    best[k] = (w8 + c, p, e["label"], list(legs))
    return best, len(slots)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    proc = argv[1]
    vi, base = P.load_data(ROOT)
    cat = {e["block"]: e for e in json.load(open(os.path.join(ROOT, "docs", "catalogue.json")))}
    best, n = routes(proc, vi, base, cat)
    if "--n" in argv:
        n = int(argv[argv.index("--n") + 1])
    print(f"{proc}: {n} external legs, Standard Model amplitude ~ lambda^{2 * n - 8}")
    for k in sorted(best, key=lambda k: (best[k][0], k)):
        tot, p, lab, legs = best[k]
        d = tot - (2 * n - 8)
        print(f"  lambda^{tot:<2d}  M8/MSM ~ E^{8 - d} v^{d - 4}/Lambda^4   class {k:2d} {CLASSES[k]:12s}"
              f" via {lab:26s} [{' '.join(legs)}]  p={p}")
    rest = [CLASSES[k] for k in CLASSES if k not in best]
    print("  no tree with Standard Model internal lines (input relations only, or not reached):", ", ".join(rest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
