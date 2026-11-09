#!/usr/bin/env python3
"""Compare two UFO models vertex by vertex, with every Wilson coefficient switched on.

    python3.11 validate/compare_ufo.py UFO_A UFO_B [--seed N] [--tol 1e-9] [--common] [--off REGEX] [--maxlegs N] [--maxnp N]

Both models are evaluated at the same values of their external parameters: the defaults of the card,
with an input the card sets to zero, a light mass or cabi, at a value of its own fixed by its name
(validate/generic_inputs.py), so that the couplings of the light flavours are compared too, and every
Wilson coefficient (an external parameter whose name starts with c and is not cabi) set to a random
value fixed by its name and the seed.  Each vertex is then evaluated as a number: the sum over
its colour and Lorentz structures of coupling times colour structure times Lorentz structure, with
every leg given a random wavefunction (a spinor, a polarisation vector, a colour vector) and a random
momentum, the momenta adding up to zero, fixed by the particle and the seed, at two such points.  The
sum is taken for each set of coupling orders apart, since MadGraph files couplings by their orders.

The two models agree when every vertex has the same values in both.  With --maxlegs only the vertices with
at most that many legs are compared, which is how a model of order N (gen/towers.py) built at N = 2 is
compared with the dimension-eight model whose vertices with at most three legs it must reproduce.  With
--maxnp only the couplings of NP order at most that are compared: the model of order 2 holds every vertex of
at most three legs through NP = 2 alone, while the dimension-eight model also carries some products of
coefficients at NP = 3 and 4, which MadGraph's order cuts leave out.  The structures themselves are not
compared: FeynRules splits a vertex into colour and Lorentz structures in a basis it chooses for the
whole vertex, so a model written in shards (validate/merge_ufo.py) and one written in one piece hold
the same vertex in different structures.  A number per vertex at random wavefunctions is what MadGraph
computes amplitudes from, and two different vertices give different numbers at a random point.

With --off the Wilson coefficients whose names match the regular expression keep the values of the card (0) in
both models.  The models in the Murphy basis are compared with the default ones with --common --off H2D3, which leaves
class 11, psi^2H^2D^3, the one class in which the two bases differ (gen/basis.py), at 0 in both.
"""
import argparse
import cmath
import collections
import hashlib
import itertools
import math
import os
import random
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import zero_vertex as Z  # noqa: E402
from generic_inputs import generic_value  # noqa: E402

MODULES = ("object_library", "function_library", "particles", "parameters", "couplings", "lorentz",
           "vertices", "coupling_orders", "propagators", "write_param_card", "CT_couplings", "decays",
           "form_factors")


def use_ufo(ufo):
    """Put a UFO first on the path with no module of another UFO loaded, and its object_library.py loaded
    with the Python 2 raise statements FeynRules writes in Python 3 form (examples/release_model.sh does
    the same to the files of a release), so that a model as the writer leaves it imports."""
    import re
    import types
    for m in MODULES:
        sys.modules.pop(m, None)
    sys.path.insert(0, ufo)
    f = os.path.join(ufo, "object_library.py")
    src = re.sub(r'raise (\w+),\s*("[^"\n]*")', r'raise \1(\2)', open(f).read())
    lib = types.ModuleType("object_library")
    lib.__file__ = f
    exec(compile(src, f, "exec"), lib.__dict__)
    sys.modules["object_library"] = lib


def leave_ufo(ufo):
    sys.path.remove(ufo)
    for m in MODULES:
        sys.modules.pop(m, None)


def coefficient(name, seed):
    h = hashlib.sha256(f"{seed}:{name}".encode()).digest()
    return int.from_bytes(h[:8], "big") / 2 ** 64 * 2 - 1


def wilson(ufo):
    """The Wilson coefficients of a UFO: its external parameters whose names start with c, but cabi."""
    use_ufo(ufo)
    try:
        import parameters as P
        return {p.name for p in P.all_parameters if p.nature == "external" and p.name.startswith("c") and p.name != "cabi"}
    finally:
        leave_ufo(ufo)


# ---- the algebra of the structures ------------------------------------------------------------------
# Every object carries upper Lorentz indices, and two equal negative (summed) Lorentz indices are
# contracted with the metric; spinor and colour indices are summed plainly.  A positive index is that of
# a leg and is contracted at once with the leg's wavefunction, so a finished product is a number.

G = np.diag([1.0, -1.0, -1.0, -1.0])
_s = [np.array([[0, 1], [1, 0]]), np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]])]
_z, _1 = np.zeros((2, 2)), np.eye(2)
GAMMA = np.array([np.block([[_1, _z], [_z, -_1]])] + [np.block([[_z, s], [-s, _z]]) for s in _s], dtype=complex)
GAMMA5 = 1j * GAMMA[0] @ GAMMA[1] @ GAMMA[2] @ GAMMA[3]
SIGMA = np.array([[0.5j * (GAMMA[m] @ GAMMA[n] - GAMMA[n] @ GAMMA[m]) for n in range(4)] for m in range(4)])
CMAT = 1j * GAMMA[2] @ GAMMA[0]
EPS4 = np.zeros((4,) * 4)
for _p in itertools.permutations(range(4)):
    EPS4[_p] = np.linalg.det(np.eye(4)[list(_p)])
# SU(3): T^a = lambda^a/2, f and d from them
_l = np.zeros((8, 3, 3), dtype=complex)
_l[0][0, 1] = _l[0][1, 0] = 1
_l[1][0, 1], _l[1][1, 0] = -1j, 1j
_l[2][0, 0], _l[2][1, 1] = 1, -1
_l[3][0, 2] = _l[3][2, 0] = 1
_l[4][0, 2], _l[4][2, 0] = -1j, 1j
_l[5][1, 2] = _l[5][2, 1] = 1
_l[6][1, 2], _l[6][2, 1] = -1j, 1j
_l[7] = np.diag([1, 1, -2]) / math.sqrt(3)
TCOL = _l / 2
FCOL = np.real(-2j * (np.einsum("aij,bjk,cki->abc", TCOL, TCOL, TCOL) - np.einsum("bij,ajk,cki->abc", TCOL, TCOL, TCOL)))
DCOL = np.real(2 * (np.einsum("aij,bjk,cki->abc", TCOL, TCOL, TCOL) + np.einsum("bij,ajk,cki->abc", TCOL, TCOL, TCOL)))
EPS3 = np.zeros((3, 3, 3))
for _p in itertools.permutations(range(3)):
    EPS3[_p] = np.linalg.det(np.eye(3)[list(_p)])
DIM = {"L": 4, "S": 4, "A": 8, "F": 3}


class Ten:
    """A tensor whose open indices are summed indices (negative integers) of a structure, with their kinds."""
    __slots__ = ("a", "lab", "kind")

    def __init__(self, a, lab=(), kind=None):
        self.a, self.lab, self.kind = np.asarray(a, dtype=complex), tuple(lab), dict(kind or {})

    def __mul__(self, y):
        if not isinstance(y, Ten):
            return Ten(self.a * y, self.lab, self.kind)
        x, a = self, self.a
        shared = [l for l in x.lab if l in y.lab]
        for l in shared:
            if x.kind[l] == "L":
                shape = [1] * a.ndim
                shape[x.lab.index(l)] = 4
                a = a * np.diag(G).reshape(shape)
        letters = {l: chr(97 + k) for k, l in enumerate(dict.fromkeys(x.lab + y.lab))}
        out = [l for l in x.lab if l not in shared] + [l for l in y.lab if l not in shared]
        spec = "".join(letters[l] for l in x.lab) + "," + "".join(letters[l] for l in y.lab) + "->" + "".join(letters[l] for l in out)
        return Ten(np.einsum(spec, a, y.a), out, {**x.kind, **y.kind})

    __rmul__ = __mul__

    def __add__(self, y):
        if not isinstance(y, Ten):
            y = Ten(y)
        if set(self.lab) != set(y.lab):
            raise ValueError(f"sum of terms with different open indices {self.lab} and {y.lab}")
        b = np.transpose(y.a, [y.lab.index(l) for l in self.lab]) if self.lab else y.a
        return Ten(self.a + b, self.lab, self.kind)

    __radd__ = __add__

    def __sub__(self, y):
        return self + (-1) * y

    def __rsub__(self, y):
        return (-1) * self + y

    def __neg__(self):
        return (-1) * self

    def __truediv__(self, y):
        return self * (1 / y)

    def __pow__(self, n):
        out = self
        for _ in range(n - 1):
            out = out * self
        return out


def scalar(x):
    if isinstance(x, Ten):
        if x.lab:
            raise ValueError(f"a structure left the indices {x.lab} open")
        return complex(x.a)
    return complex(x)


def factory(base, kinds, wf):
    """A structure function: each positive argument is contracted with the wavefunction wf(kind, leg)."""
    def make(*idx):
        a, lab, kind = np.asarray(base, dtype=complex), [], {}
        axis = 0
        for i, k in zip(idx, kinds):
            if i > 0:
                a = np.tensordot(a, wf(k, i), axes=([axis], [0]))
            else:
                lab.append(i)
                kind[i] = k
                axis += 1
        return Ten(a, lab, kind)
    return make


class Point:
    """The wavefunctions and momenta of the legs of one vertex at one random point.  The draws are made
    for the legs in the canonical order (sorted by particle), and leg k of the vertex takes those of
    canonical leg pos[k], so that two models that list a vertex in different orders give each particle
    the same wavefunction."""

    def __init__(self, colours, pos, rng):
        n = len(colours)
        c = lambda d: np.array([complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(d)])
        mom = [np.array([rng.gauss(0, 1) for _ in range(4)]) for _ in range(n - 1)]
        mom.append(-sum(mom))
        lor = [c(4) for _ in range(n)]
        spi = [c(4) for _ in range(n)]
        col = [c({3: 3, -3: 3, 8: 8}.get(colours[k], 1)) for k in range(n)]
        self.mom = {k: mom[j] for k, j in pos.items()}
        self.lor = {k: lor[j] for k, j in pos.items()}
        self.spi = {k: spi[j] for k, j in pos.items()}
        self.col = {k: col[j] for k, j in pos.items()}

    def wf(self, kind, leg):
        return {"L": self.lor, "S": self.spi, "A": self.col, "F": self.col}[kind][leg]

    def lorentz_ns(self):
        ns = {"complex": complex, "cmath": cmath, "math": math}
        for name, base, kinds in (("Gamma", GAMMA, "LSS"), ("Gamma5", GAMMA5, "SS"), ("ProjM", (np.eye(4) - GAMMA5) / 2, "SS"),
                                  ("ProjP", (np.eye(4) + GAMMA5) / 2, "SS"), ("Identity", np.eye(4), "SS"), ("C", CMAT, "SS"),
                                  ("Metric", np.linalg.inv(G), "LL"), ("Epsilon", EPS4, "LLLL"), ("Sigma", SIGMA, "LLSS")):
            ns[name] = factory(base, kinds, self.wf)
        ns["P"] = lambda mu, leg: factory(self.mom[leg], "L", self.wf)(mu)
        return ns

    def colour_ns(self):
        ns = {"complex": complex, "cmath": cmath, "math": math}
        for name, base, kinds in (("T", TCOL, "AFF"), ("f", FCOL, "AAA"), ("d", DCOL, "AAA"),
                                  ("Epsilon", EPS3, "FFF"), ("EpsilonBar", EPS3, "FFF")):
            ns[name] = factory(base, kinds, self.wf)

        def identity(i, j):
            if i > 0 and j > 0:
                return Ten(np.dot(self.col[i], self.col[j]))
            raise ValueError("colour Identity with a summed index")
        ns["Identity"] = identity
        return ns


def evaluate(ufo, seed, switched=None, points=2, maxlegs=None):
    """{(particles, orders): [vertex value at each point]} and {sorted particles: the orders in which the
    model lists them}.  With switched, only the Wilson coefficients it names take random values, and the
    others keep those of the card."""
    use_ufo(ufo)
    try:
        import function_library as F
        import parameters as P
        import vertices as V
        ns = {"cmath": cmath, "math": math, "complex": complex}
        ns.update({k: v for k, v in vars(F).items() if callable(v)})
        vals = {}
        for p in P.all_parameters:
            if p.nature == "external":
                v = float(p.value)
                if p.name.startswith("c") and p.name != "cabi":
                    if switched is None or p.name in switched:
                        v = coefficient(p.name, seed)
                else:
                    v = generic_value(p.name, v)
                vals[p.name] = v
        for p in P.all_parameters:
            if p.nature == "internal":
                vals[p.name] = eval(p.value, ns, vals)
        code = {}
        comp = lambda s: code.setdefault(s, compile(s, "<structure>", "eval"))
        out = collections.defaultdict(lambda: [0j] * points)
        listed = collections.defaultdict(set)
        for v in V.all_vertices:
            names = [p.name for p in v.particles]
            if maxlegs is not None and len(names) > maxlegs:
                continue
            listed[tuple(sorted(names))].add(tuple(names))
            order = sorted(range(len(names)), key=lambda k: (names[k], k))
            pos = {order[j] + 1: j for j in range(len(order))}
            # With four fermions or more, each structure takes the sign MadGraph puts on its coupling when its
            # fermion flow is crossed, and the vertex the sign of the order of its fermion legs
            # (validate/zero_vertex.py).  FeynRules writes a vertex of identical fermions as both pairings with
            # one coupling, which without the signs sums to its Fierz zero in any model, held or dropped.
            ferm = [k for k in order if v.particles[k].spin % 2 == 0]
            sgn = [1] * len(v.lorentz)
            if len(ferm) >= 4:
                eps = Z.order_sign(ferm)
                for li, l in enumerate(v.lorentz):
                    s = Z.structure_sign(l.structure)
                    if s is None:
                        raise SystemExit(f"{ufo}: no fermion flow for {l.name} = {l.structure}")
                    sgn[li] = eps * s
            terms = [(ci, li, (tuple(sorted(names)), tuple(sorted(c.order.items()))), complex(eval(comp(c.value), ns, vals)))
                     for (ci, li), cs in v.couplings.items() for c in (cs if isinstance(cs, list) else [cs])]
            for pt in range(points):
                rng = random.Random(f"{seed}:{pt}:{'/'.join(sorted(names))}")
                point = Point([v.particles[k].color for k in order], pos, rng)
                lns, cns = point.lorentz_ns(), point.colour_ns()
                lor = [sgn[li] * scalar(eval(comp(l.structure), lns)) for li, l in enumerate(v.lorentz)]
                col = [scalar(eval(comp(c), cns)) for c in v.color]
                for ci, li, key, g in terms:
                    out[key][pt] += g * col[ci] * lor[li]
        return out, listed
    finally:
        leave_ufo(ufo)


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("a")
    a.add_argument("b")
    a.add_argument("--seed", type=int, default=1)
    a.add_argument("--tol", type=float, default=1e-9)
    a.add_argument("--common", action="store_true",
                   help="switch on only the Wilson coefficients both models have; the others keep the values of "
                        "the card (0), so that a model with more coefficients is compared on those of the other")
    a.add_argument("--off", default=None,
                   help="the Wilson coefficients whose names match this regular expression keep the values of the card (0)")
    a.add_argument("--maxlegs", type=int, default=None, help="compare only the vertices with at most this many legs")
    a.add_argument("--maxnp", type=int, default=None, help="compare only the couplings of NP order at most this")
    args = a.parse_args(argv)
    switched = wilson(args.a) & wilson(args.b) if args.common else None
    if args.common:
        print(f"{len(switched)} Wilson coefficients in both models switched on; "
              f"{len(wilson(args.a) - switched)} only in the first and {len(wilson(args.b) - switched)} only in the second at 0")
    if args.off:
        on = switched if switched is not None else wilson(args.a) | wilson(args.b)
        switched = {w for w in on if not re.search(args.off, w)}
        print(f"{len(on) - len(switched)} Wilson coefficients matching {args.off!r} left at 0")
    (A, LA), (B, LB) = (evaluate(args.a, args.seed, switched, maxlegs=args.maxlegs),
                        evaluate(args.b, args.seed, switched, maxlegs=args.maxlegs))
    if args.maxnp is not None:
        A, B = ({k: v for k, v in M.items() if dict(k[1]).get("NP", 0) <= args.maxnp} for M in (A, B))
    # a vertex listed in another order of its particles is the same vertex only up to the sign of the
    # exchange of its fermions, so those are counted apart
    reordered = {k for k in set(LA) & set(LB) if LA[k] != LB[k]}
    size = lambda x: max(abs(z) for z in x)
    scale = max([size(x) for x in A.values()] + [size(x) for x in B.values()] + [1e-300])
    bad, only = [], [[], []]
    for k in set(A) | set(B):
        x, y = A.get(k), B.get(k)
        if x is None or y is None:
            # a vertex one model lacks counts only if the other has it at a value that is not zero
            z = x if y is None else y
            if size(z) > 1e-14 * scale:
                only[0 if y is None else 1].append((size(z), k))
            continue
        d = max(abs(p - q) for p, q in zip(x, y))
        if d > args.tol * max(size(x), size(y)) and d > 1e-14 * scale:
            bad.append((d / max(size(x), size(y)), k, x[0], y[0]))
    bad.sort(reverse=True)
    print(f"{args.a}: {len(A)} vertices by coupling order   {args.b}: {len(B)}   nonzero only in the first "
          f"{len(only[0])}, only in the second {len(only[1])}, disagreeing {len(bad)}")
    print(f"{len(reordered)} vertices listed with their particles in another order, "
          f"{sum(1 for b in bad if b[1][0] in reordered)} of them among those disagreeing")
    for r, k, x, y in bad[:20]:
        print(f"  {r:.2e}  {k[0]} {dict(k[1])}: {x:.6g} vs {y:.6g}" + ("  (reordered)" if k[0] in reordered else ""))
    for side, rows in zip(("first", "second"), only):
        if rows:
            print(f"  only in the {side}, by NP order: "
                  f"{dict(sorted(collections.Counter(dict(k[1]).get('NP', 0) for _, k in rows).items()))}")
        for z, k in sorted(rows, reverse=True)[:10]:
            print(f"  only in the {side}: {k[0]} {dict(k[1])} at {z:.3g}")
    return 1 if bad or only[0] or only[1] else 0


if __name__ == "__main__":
    sys.exit(main())
