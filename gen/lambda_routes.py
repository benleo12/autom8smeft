#!/usr/bin/env python3
"""The power of lambda of every dimension-six and dimension-eight class in a process, by its cheapest tree.

    gen/lambda_routes.py "p p > w+ w-" [--n 4]

A tree is the product of its vertices and propagators.  In the energy-enhanced counting of the
paper (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1): a Standard Model three-point vertex
carries a momentum and counts lambda^-2 or a vev and counts lambda^-1, a four-point vertex
counts lambda^0, a propagator lambda^4, and a vertex of an operator of mass dimension d with
m legs and p vacuum insertions lambda^(d-12+2m+p), that is lambda^(2m-4+p) at dimension eight
and lambda^(2m-6+p) at dimension six.  The Standard Model amplitude of an n-point process is
lambda^(2n-8), so a dimension-eight class entering at lambda^(2n-8+Delta) has
M8/MSM ~ E^(8-Delta) v^(Delta-4) / Lambda^4 and a dimension-six class M6/MSM ~ E^(4-Delta) v^(Delta-2) / Lambda^2.
The route printed beside each class is its cheapest tree: the operator vertex, its vacuum
insertions, and the Standard Model vertices the tree uses, which are the coupling factors that
multiply the term.

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
DIM6 = {"L6cl1": ("X^3", 0), "L6cl2": ("H^6", 6), "L6cl3": ("H^4D^2", 4), "L6cl4": ("X^2H^2", 2),
        "L6cl5": ("psi^2H^3", 3), "L6cl6": ("psi^2XH", 1), "L6cl7": ("psi^2H^2D", 2),
        "L6cl8a": ("psi^4", 0), "L6cl8b": ("psi^4", 0), "L6cl8c": ("psi^4", 0), "L6cl8d": ("psi^4", 0)}
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
        """(cost, SM vertices used) for leg f to reach exactly the externals in group."""
        if len(group) == 1 and P._same_field(f, group[0]):
            return (0, ())
        key = (f, group)
        if key in self.cache:
            return self.cache[key]
        self.cache[key] = (INF, ())
        best, af = (INF, ()), P.anti(f)
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
                c, used = w + 4, (v,)
                for i in range(len(rest)):
                    ci, ui = self.reach(rest[i], parts[i])
                    c += ci
                    used += ui
                    if c >= INF:
                        break
                if c < best[0]:
                    best = (c, used)
        self.cache[key] = best
        return best

    def vertex(self, legs, externals):
        best = (INF, ())
        for parts in P._partitions(externals, len(legs)):
            c, used = 0, ()
            for i in range(len(legs)):
                ci, ui = self.reach(legs[i], parts[i])
                c += ci
                used += ui
                if c >= INF:
                    break
            if c < best[0]:
                best = (c, used)
        return best


def routes(proc, vertex_index, base_vertices, catalogue):
    """(dim, class name) -> (lambda power, p, operator label, vertex legs, SM vertices) of the cheapest tree."""
    slots = P.parse_process(proc, collapse=True)
    assignments = {tuple(sorted(a)) for a in P._product(slots)}
    cheap = Cheapest(P.standard_model_vertices(base_vertices))
    best = {}
    for block, verts in vertex_index.items():
        if block.startswith("L8op"):
            e = catalogue.get(block)
            if not e or int(block[4:]) >= 675:
                continue
            dim, key, n_higgs, label = 8, (8, e["cls"]), e["fields"]["N_H"], e["label"]
        elif block in DIM6:
            dim, (name, n_higgs), label = 6, DIM6[block], block
            key = (6, name)
        else:
            continue
        for legs in verts:
            p = n_higgs - legs.count("H")
            w = dim - 12 + 2 * len(legs) + p      # lambda^(2m-4+p) at dimension eight, lambda^(2m-6+p) at six
            for ext in assignments:
                c, used = cheap.vertex(list(legs), ext)
                if c >= INF:
                    continue
                if key not in best or w + c < best[key][0]:
                    best[key] = (w + c, p, label, list(legs), used)
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
    sm = 2 * n - 8
    print(f"{proc}: {n} external legs, Standard Model amplitude ~ lambda^{sm}")
    for dim in (6, 8):
        print(f" dimension {dim}:")
        for key in sorted((k for k in best if k[0] == dim), key=lambda k: (best[k][0], str(k[1]))):
            tot, p, lab, legs, used = best[key]
            d = tot - sm
            name = key[1] if dim == 6 else CLASSES[key[1]]
            ratio = (f"E^{4 - d} v^{d - 2}/Lambda^2" if dim == 6 else f"E^{8 - d} v^{d - 4}/Lambda^4")
            smv = " + ".join("[" + " ".join(v) + "]" for v in used) or "contact"
            print(f"  lambda^{tot:<2d}  M/MSM ~ {ratio:18s} {name:12s} via {lab:24s} [{' '.join(legs)}] p={p}   SM vertices: {smv}")
    rest = [CLASSES[k] for k in CLASSES if (8, k) not in best]
    print("  dimension-eight classes with no tree (input relations only, or not reached):", ", ".join(rest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
