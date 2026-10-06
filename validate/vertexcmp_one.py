#!/usr/bin/env python3
"""Evaluate one UFO's vertices numerically, twice: with a coefficient off and on.

A UFO is plain Python, so this reads it directly rather than driving MadGraph's internals.
External parameters are set from the caller's dict, internal ones are evaluated to a fixpoint
(FeynRules usually writes them in dependency order, but the fixpoint makes that irrelevant), and
every coupling expression is then evaluated in that namespace.

Vertices are keyed by SORTED PDG CODES, so the two models line up even though they name their
particles and their Lorentz structures differently.  For each vertex the value reported is the
sum over its (colour, lorentz) coupling entries of |coupling|, which is basis-independent enough
to compare across two models that may order their colour/Lorentz lists differently, and is all
that is needed to answer "does this coefficient change this vertex by the same amount".

    python3.11 vertexcmp_one.py <ufo path> '<json {param: value}>' '<json [coeff names]>'

Prints JSON: {"<pdg key>": [off, on]}.  MUST be python3.11 (PEP 667 breaks MadGraph from 3.13).
"""
import cmath
import json
import re
import os
import sys

if len(sys.argv) < 4:
    print(__doc__)
    sys.exit(2)
ufo_path = os.path.abspath(sys.argv[1])
inputs = json.loads(sys.argv[2])
coeffs = json.loads(sys.argv[3])
# optional 4th argument: the value to switch the coefficient ON at, default 1.  Comparing at a
# SMALL value separates a genuine difference in the linear term from a difference in how far the
# two models truncate: ours corrects the input scheme to 1/Lam^4, SMEFTsim stops at 1/Lam^2, so
# any mismatch that is higher order in c must vanish as c -> 0.
CVAL = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0

# a UFO's __init__ does "import object_library", a Python-2 implicit relative import, so the
# model directory itself has to be on the path as well as its parent
# a UFO's write_param_card imports models.*, so MG5's root goes on the path when we know it
_mg = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
if os.path.isdir(_mg):
    sys.path.append(_mg)
sys.path.insert(0, ufo_path)
sys.path.insert(0, os.path.dirname(ufo_path))
pkg = __import__(os.path.basename(ufo_path))
params = pkg.all_parameters
couplings = pkg.all_couplings
vertices = pkg.all_vertices


def evaluate(on):
    ns = {"cmath": cmath, "complex": complex, "complexconjugate": lambda z: complex(z).conjugate(),
          "re": lambda z: complex(z).real, "im": lambda z: complex(z).imag,
          "sqrt": cmath.sqrt, "pi": cmath.pi, "abs": abs}
    for f in getattr(pkg, "all_functions", []):
        try:
            ns[f.name] = eval("lambda %s: %s" % (",".join(f.arguments), f.expr), dict(ns))
        except Exception:
            pass
    ext = {}
    for p in params:
        if p.nature == "external":
            v = inputs.get(p.name, p.value)
            if p.name in coeffs:
                v = CVAL if on else 0.0
            ext[p.name] = v
    ns.update(ext)
    # internal parameters, to a fixpoint so declaration order does not matter
    todo = [p for p in params if p.nature != "external"]
    for _ in range(len(todo) + 2):
        left = []
        for p in todo:
            try:
                ns[p.name] = eval(p.value, ns)
            except Exception:
                left.append(p)
        if not left or len(left) == len(todo):
            todo = left
            break
        todo = left
    if todo:
        print("unresolved internal parameters: %s" % [p.name for p in todo][:5], file=sys.stderr)
    cv = {}
    for c in couplings:
        try:
            cv[c.name] = complex(eval(c.value, ns))
        except Exception:
            cv[c.name] = 0j
    # Key by PDG content AND the colour/Lorentz structure the coupling sits on, then sum the
    # couplings SIGNED.  Summing |coupling| over a vertex's entries is wrong: where a model keeps
    # the operator's contribution and the input-scheme compensation as two entries on one vertex,
    # |a| + |b| turns their cancellation into an addition.  On the Higgs self-coupling that reads
    # as 15 + 9 = 24 against the true |-15 + 9| = 6, a spurious factor of 4.
    # Two invariants per vertex, keyed by PDG content alone.
    #   sum   the SIGNED sum of every coupling entry.  Summing |coupling| instead would turn a
    #         cancellation into an addition: where a model keeps the operator's contribution and
    #         the input-scheme compensation as two entries on one vertex, |a| + |b| reads as
    #         15 + 9 = 24 on the Higgs self-coupling against the true |-15 + 9| = 6.
    #   mags  the sorted magnitudes of the entries.  Keying on the colour/Lorentz structure
    #         instead is too strict: the two models order their Dirac structures differently, so
    #         identical physics shows up as every four-fermion entry "differing".
    # Both must match.  The sum alone would miss two structures' couplings being swapped, and the
    # magnitudes alone would miss a sign.
    # Sum the IDENTITY component, not the raw entries, because the two models do not use the
    # same Dirac decomposition for a scalar-fermion vertex.  SMEFTsim writes e+ e- h on
    # Identity(2,1) and Gamma5(2,1); this model writes it on ProjP and ProjM.  Since
    #     a ProjM + b ProjP = (a+b)/2 Identity + (b-a)/2 Gamma5,
    # a pair of pure projectors each carrying g is exactly one Identity carrying g, and adding
    # the raw entries reports 2g against their g.  Weight a bare projector by one half.
    # Structures that pair a projector with Gamma(...) are the four-fermion ones, where both
    # models already use the same decomposition, so they keep weight one.
    # ONE projector means one fermion bilinear, and SMEFTsim decomposes those onto
    # Identity/Gamma5 while this model uses ProjP/ProjM: two projector entries at g ARE one
    # Identity at g, so halve them.  This covers the scalar vertex (e+ e- h) and the DIPOLES,
    # whose SMEFTsim structures are Gamma- and Gamma5-based (FFV9, FFV2) with no projector.
    # TWO projectors means a four-fermion vertex, where SMEFTsim also uses ProjM/ProjM
    # (FFFF3, FFFF4), so the decompositions already agree and the weight stays one.
    # LIMIT OF THIS TOOL.  It halves a BARE projector only.  A dipole's structure carries the
    # projector inside the two terms of the sigma^{mu nu} antisymmetrisation, and SMEFTsim writes
    # the same dipole on Gamma/Gamma5 structures (FFV9, FFV2) with no projector at all, so cdB
    # and its relatives read as a clean factor 2 here that is decomposition, not physics.
    # Settling a dipole needs the projectors expanded symbolically into Identity and Gamma5;
    # until then compare dipoles by cross section, where they agree.
    bare = re.compile(r"^Proj[PM]\(\d+,\d+\)$")
    out = {}
    for v in vertices:
        pdg = ",".join(str(x) for x in sorted(p.pdg_code for p in v.particles))
        tot, mags = out.setdefault(pdg, [0j, []])[0], out[pdg][1]
        for (ci, li), c in v.couplings.items():
            w = 0.5 if bare.match(v.lorentz[li].structure.replace(" ", "")) else 1.0
            z = cv.get(c.name, 0j) * w
            tot += z
            mags.append(abs(z))
        out[pdg][0] = tot
    return {k: [[z.real, z.imag], sorted(m)] for k, (z, m) in out.items()}


off, on = evaluate(False), evaluate(True)
print(json.dumps({k: [off.get(k, [0.0, 0.0]), on.get(k, [0.0, 0.0])]
                  for k in set(off) | set(on)}))
