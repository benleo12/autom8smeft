#!/usr/bin/env python3
"""The sign of the Levi-Civita tensor, end to end on the exported model.

    python3.11 validate/check_eps_sign.py [models/dim8_is]        ($MG5_DIR points to MadGraph)

The model follows the Murphy basis, X~_{mu nu} = (1/2) eps_{mu nu rho sigma} X^{rho sigma} with
eps_{0123} = +1.  The sign reaches an amplitude through three steps: the FeynRules Lagrangian,
the Lorentz structure FeynRules writes into the UFO, and the value ALOHA gives the UFO's Epsilon
when it builds the helicity routine.  This test takes the h gamma gamma vertex of
Q_{B^2H^4}^{(2)} = (H^dag H)^2 B~_{mu nu} B^{mu nu}, the simplest single-dual operator, and
compares the routine ALOHA builds from the released UFO with the vertex derived by hand from the
Lagrangian with eps_{0123} = +1:

    L  >  C v^3 c_W^2 h F~_{mu nu} F^{mu nu} / Lambda^4
    V  =  -4 i C v^3 c_W^2 / Lambda^4  eps_{mu nu rho sigma} p2^mu e2^nu p1^rho e1^sigma

with p_i the incoming momenta and e_i the polarisation vectors.  ALOHA multiplies every routine by
its own phase and by the scalar wavefunction, so both sides are divided by the same vertex of
Q_{B^2H^4}^{(1)} = (H^dag H)^2 B_{mu nu} B^{mu nu}, which carries no epsilon,

    V  =  -4 i C v^3 c_W^2 / Lambda^4  [(p1.p2)(e1.e2) - (p1.e2)(p2.e1)],

and the ratio is compared at random momenta and polarisations.  A flipped sign anywhere in the
chain flips the ratio.
"""
import cmath
import os
import random
import re
import sys
from itertools import permutations

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
G = (1.0, -1.0, -1.0, -1.0)   # the diagonal of the metric


def eps_lower():
    """{(mu, nu, rho, sigma): eps_{mu nu rho sigma}} on its nonzero entries, eps_{0123} = +1."""
    e = {}
    for p in permutations(range(4)):
        inv = sum(1 for i in range(4) for j in range(i + 1, 4) if p[i] > p[j])
        e[p] = (-1) ** inv
    return e


def dot(a, b):
    return sum(G[m] * a[m] * b[m] for m in range(4))


def coupling_of(model, vertex_particles, wc, lorentz_name):
    """The coefficient of one Wilson coefficient in the coupling that multiplies a Lorentz structure
    of the vertex with the given particles, all other coefficients set to zero."""
    vt = open(os.path.join(model, "vertices.py")).read()
    cp = open(os.path.join(model, "couplings.py")).read()
    gcs = {m.group(1): m.group(2) for m in re.finditer(r"(GC_\w+) = Coupling\(name = '\w+',\s*value = '([^']*)'", cp)}
    for m in re.finditer(r"Vertex\(name = '\w+',\s*particles = \[([^\]]*)\],\s*color = \[[^\]]*\],\s*"
                         r"lorentz = \[([^\]]*)\],\s*couplings = \{([^}]*)\}", vt):
        if sorted(p.strip() for p in m.group(1).split(",")) != sorted(vertex_particles):
            continue
        lors = [x.strip() for x in m.group(2).split(",")]
        for i, j, g in re.findall(r"\((\d+),(\d+)\):C\.(GC_\w+)", m.group(3)):
            if lors[int(j)] == "L." + lorentz_name and re.search(r"\b" + wc + r"\b", gcs[g]):
                names = set(re.findall(r"\b[A-Za-z_]\w*\b", gcs[g])) - {"complex", "cmath", "sqrt"}
                env = {n: 0.0 for n in names}
                env.update(cw=0.88, sw=0.47, vev=246.0, vevSM=246.0, Lam=1000.0, complex=complex, cmath=cmath)
                env[wc] = 1.0
                return complex(eval(gcs[g], {"__builtins__": {}}, env))
    raise SystemExit(f"no {lorentz_name} coupling of {wc} in the vertex {vertex_particles}")


def main(argv):
    model = os.path.abspath(argv[1]) if len(argv) > 1 else os.path.join(ROOT, "models", "dim8_is")
    sys.path.insert(0, MG)
    sys.path.insert(0, model)
    import lorentz                                     # the UFO's Lorentz structures
    import aloha.create_aloha as create_aloha
    from aloha.aloha_object import L_Epsilon

    print("ALOHA eps^{0123} =", L_Epsilon("e", 1, 2, 3, 4).give_parity((0, 1, 2, 3)),
          "(contravariant components), so eps_{0123} = +1 when all four indices are lowered")

    def routine(name):
        ns = {"cmath": cmath, "wavefunctions": None}
        txt = create_aloha.AbstractRoutineBuilder(getattr(lorentz, name)).compute_routine(0).write(
            output_dir=None, language="Python")
        exec(txt.replace("import wavefunctions\n", ""), ns)
        return ns[name + "_0"]

    # the h gamma gamma vertex: Q^(2) on the dual structure, Q^(1) on the plain one
    parts = ["P.a", "P.a", "P.H"]
    L2, L1 = "VVS2", "VVS7"
    g2 = coupling_of(model, parts, "c8B2H4x2", L2)
    g1 = coupling_of(model, parts, "c8B2H4x1", L1)
    f2, f1 = routine(L2), routine(L1)
    eps = eps_lower()
    rng = random.Random(20261016)
    vec = lambda: [rng.gauss(0, 100) for _ in range(4)]
    cvec = lambda: [complex(rng.gauss(0, 1), rng.gauss(0, 1)) for _ in range(4)]
    worst = 0.0
    for _ in range(20):
        p1, p2, e1, e2 = vec(), vec(), cvec(), cvec()
        wf = lambda p, e: [complex(p[0], p[3]), complex(p[1], p[2])] + list(e)
        s3 = [0, 0, 1.0]
        model_ratio = (g2 * f2(wf(p1, e1), wf(p2, e2), s3, 1.0)) / (g1 * f1(wf(p1, e1), wf(p2, e2), s3, 1.0))
        dual = sum(s * p2[a] * e2[b] * p1[c] * e1[d] for (a, b, c, d), s in eps.items())
        plain = dot(p1, p2) * dot(e1, e2) - dot(p1, e2) * dot(p2, e1)
        hand_ratio = dual / plain
        worst = max(worst, abs(model_ratio - hand_ratio) / abs(hand_ratio))
        flipped = abs(model_ratio + hand_ratio) / abs(hand_ratio)
    ok = worst < 1e-9
    print(f"largest relative difference over 20 random points: {worst:.1e}"
          f"  ({'PASS: the model carries eps_{0123} = +1' if ok else 'FAIL'})")
    if not ok and flipped < 1e-9:
        print("the ratio has the opposite sign: the model carries eps_{0123} = -1")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
