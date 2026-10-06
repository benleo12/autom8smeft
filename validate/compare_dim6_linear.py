#!/usr/bin/env python3
"""Are the linear dimension-six couplings of two UFOs the same, coefficient by coefficient?

    python3.11 validate/compare_dim6_linear.py <UFO A> <UFO B> [--tol 1e-9]

Each model is read in its own interpreter (two UFOs cannot be imported side by side, their module
names collide).  With ONE real coefficient of block DIM6 at one and the rest at zero, every
coupling of order NP=1 that carries the dimension-six scale is evaluated, and for each vertex,
keyed by its PDG codes, the magnitudes over its colour and Lorentz structures are compared as a
sorted list.  One coefficient at a time is the point: with several on, a model that kept the
input shifts inside untagged parameters (ours before 2026-10-03) differs from one that tags them
at the per-cent level, which is a second-order effect and not a difference in the linear vertex.

Used on 2026-10-05 to show that rebuilding the dimension-six sector changed nothing at linear
order except the pure-gluon vertices of cHG, and, in passing, that the build of 2026-10-04 had
three Yukawa operators in it twice.  Sorted magnitudes are blind to a relabelling of dummy
indices and to the order of identical legs, which differ freely between two writes of one model,
and to an overall sign, which they do not.  Needs a Python that can import a UFO (3.11).
"""
import collections
import json
import os
import subprocess
import sys

DUMP = r'''
import sys, os, cmath, math, json, collections
ufo = os.path.abspath(sys.argv[1]); sys.path.insert(0, ufo)
mg = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3")); sys.path.insert(0, mg)
import parameters as P, vertices as V
ext0 = {p.name: float(p.value) for p in P.all_parameters if p.nature == "external"}
six = [p.name for p in P.all_parameters if p.nature == "external" and p.lhablock == "DIM6"
       and p.name != "Lam6" and not p.name.endswith("Ph")]
for n in six: ext0[n] = 0.0
ns = {"cmath": cmath, "math": math, "complex": complex,
      "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z}
internal = [(p.name, compile(p.value, p.name, "eval")) for p in P.all_parameters if p.nature == "internal"]
entries = []
for v in V.all_vertices:
    key = ",".join(str(x) for x in sorted(p.pdg_code for p in v.particles))
    for (ic, il), cs in v.couplings.items():
        for c in (cs if isinstance(cs, (list, tuple)) else [cs]):
            if c.order.get("NP", 0) == 1 and "Lam6" in c.value:
                entries.append((key, v.color[ic] + "|" + v.lorentz[il].structure, compile(c.value, c.name, "eval")))
out = {}
for name in six:
    vals = dict(ext0); vals[name] = 1.0
    for n, code in internal: vals[n] = eval(code, ns, vals)
    acc = collections.defaultdict(complex)
    for key, st, code in entries: acc[(key, st)] += complex(eval(code, ns, vals))
    per = collections.defaultdict(list)
    top = max([abs(z) for z in acc.values()] or [0.0])
    for (key, st), z in acc.items():
        # a coupling that is zero by a relation between parameters comes out at rounding level
        if abs(z) > 1e-12 * top: per[key].append(abs(z))
    out[name] = {k: sorted(m) for k, m in per.items()}
print(json.dumps(out))
'''


def dump(ufo):
    r = subprocess.run([sys.executable, "-c", DUMP, ufo], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"could not read {ufo}:\n{r.stderr[-800:]}")
    return json.loads(r.stdout)


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    tol = float(argv[argv.index("--tol") + 1]) if "--tol" in argv else 1e-9
    a, b = dump(argv[1]), dump(argv[2])
    only = sorted(set(a) ^ set(b))
    if only:
        print("coefficients in one model only:", " ".join(only))
    pairs, bad = 0, collections.defaultdict(list)
    for c in sorted(set(a) & set(b)):
        for k in set(a[c]) | set(b[c]):
            pairs += 1
            x, y = a[c].get(k, []), b[c].get(k, [])
            if len(x) != len(y) or any(abs(p - q) > tol * max(p, q) for p, q in zip(x, y)):
                bad[c].append(k)
    print(f"{len(set(a) & set(b))} coefficients, {pairs} (coefficient, vertex) pairs compared at {tol:g}; "
          f"{sum(len(v) for v in bad.values())} differ")
    for c, ks in bad.items():
        for k in sorted(ks):
            print(f"  {c:10s} vertex {k:22s} A {[float('%.4g' % m) for m in a[c].get(k, [])]}  "
                  f"B {[float('%.4g' % m) for m in b[c].get(k, [])]}")
    return 1 if bad or only else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
