#!/usr/bin/env python3
"""Find Lorentz structures of a UFO that vanish identically, and the vertices that carry them.

SUPERSEDED by validate/zero_vertex.py (2026-09-07).  Two holes, both found by auditing the
release gate rather than the model.  This test randomises the momenta INDEPENDENTLY, so it can
only catch a structure that vanishes by the antisymmetry of Epsilon alone, never one that
vanishes through momentum conservation, which ALOHA does impose; and it skips every structure
carrying a Gamma matrix.  Run on the released dim8_is it reports zero, while zero_vertex.py finds
nine, used by fifty vertices, one of which (the psi^4 B one) breaks the build.  Kept because its
Epsilon-only pass is fast and its findings were real.

    validate/zero_lorentz.py <UFO dir> [--all]    (needs numpy: python3.13 on this machine)

By default only structures containing Epsilon are tested, since the missing antisymmetrisation
is the Epsilon one and Metric/P-only structures come out of FeynRules canonicalised; --all
tests every Dirac-free structure (an hour on the full model, seconds for the Epsilon ones).

Why: FeynRules does not antisymmetrise Epsilon over its dummy indices, so a structure such as
  -(Epsilon(1,-1,-2,-3)*P(-3,1)*P(-2,3)*P(-1,2)) - Epsilon(1,-1,-2,-3)*P(-3,1)*P(-2,2)*P(-1,3)
(the two terms cancel under -1 <-> -2) reaches the UFO as a live vertex.  ALOHA simplifies it to
zero and then writes a Fortran routine whose arguments it never declares ("Symbol 's2' has no
IMPLICIT type"), and every process that touches the vertex fails to compile.  Seen on dim8_is:
the a H H and Z H H vertices of Q_{BH^4D^2}^{(2)}, killing p p > w+ w- z.

Method: each structure built from Epsilon, P, Metric and Identity (no Dirac matrices) is
evaluated numerically at random momenta and random polarisation vectors for its external legs,
the free Lorentz indices contracted with the vectors' polarisations, six random points; a
structure that vanishes at all of them to 1e-9 relative to the size of its individual terms is
reported.  Structures with Gamma matrices are left alone (none of the zero ones found had any).
"""
import os, re, sys
import numpy as np

G = np.diag([1.0, -1.0, -1.0, -1.0])
EPS = np.zeros((4, 4, 4, 4))
for p in __import__("itertools").permutations(range(4)):
    sgn = 1
    q = list(p)
    for i in range(4):
        for j in range(i + 1, 4):
            if q[i] > q[j]: sgn = -sgn
    EPS[p] = sgn


def parse(struct):
    """The structure as a list of (sign, coefficient, [(tensor name, index list)]) terms, or None
    when a factor is not one of Epsilon, P, Metric (Identity structures are skipped)."""
    s = struct.replace(" ", "")
    # split on top-level + and -
    out, depth, cur, sign, terms = [], 0, "", 1, []
    for ch in s:
        if ch == "(": depth += 1
        if ch == ")": depth -= 1
        if ch in "+-" and depth == 0 and cur:
            terms.append((sign, cur)); cur, sign = "", (1 if ch == "+" else -1)
        elif ch in "+-" and depth == 0 and not cur:
            sign = sign * (1 if ch == "+" else -1)
        else:
            cur += ch
    if cur: terms.append((sign, cur))
    parsed = []
    def strip_outer(t):   # "-(A*B*C)" arrives as the term "(A*B*C)": peel one enclosing pair
        while t.startswith("(") and t.endswith(")"):
            depth = 0
            for k, ch in enumerate(t):
                depth += (ch == "(") - (ch == ")")
                if depth == 0 and k < len(t) - 1: return t
            t = t[1:-1]
        return t
    for sign, term in terms:
        term = strip_outer(term)
        val, coef = np.array(1.0 + 0j), 1.0
        # factors are separated by '*' at top level
        facs, depth, cur = [], 0, ""
        for ch in term:
            if ch == "(": depth += 1
            if ch == ")": depth -= 1
            if ch == "*" and depth == 0: facs.append(cur); cur = ""
            else: cur += ch
        facs.append(cur)
        tensors = []
        for f in facs:
            f = strip_outer(f)   # never str.strip("()"): that turns P(-3,1) into P(-3,1
            m = re.match(r"(Epsilon|P|Metric|Identity)\(([^)]*)\)$", f)
            if not m:
                try: coef *= complex(eval(f, {"__builtins__": {}}, {"complex": complex})); continue
                except Exception: return None
            name, args = m.group(1), [int(a) for a in m.group(2).split(",")]
            if name == "Identity": return None
            tensors.append((name, args))
        parsed.append((sign, coef, tensors))
    return parsed


def evaluate(parsed, nlegs, rng):
    """Value at one random point, all free indices contracted with polarisations.  Positive
    indices are external legs, negative ones dummies; vectors carry upper indices and every
    contraction goes through the metric."""
    if parsed is None: return None
    mom = {i: rng.normal(size=4) for i in range(1, nlegs + 1)}
    pol = {i: rng.normal(size=4) + 1j * rng.normal(size=4) for i in range(1, nlegs + 1)}
    total, scale = 0.0, 0.0
    for sign, coef, named in parsed:
        tensors = [(EPS if n == "Epsilon" else G if n == "Metric" else G @ mom[a[1]], a if n != "P" else [a[0]]) for n, a in named]
        labels = {}
        letters = iter("abcdefghijklmnopqrstuvwxyz")
        specs, arrays = [], []
        for arr, idx in tensors:
            spec = ""
            for i in idx:
                if i not in labels: labels[i] = next(letters)
                spec += labels[i]
            specs.append(spec); arrays.append(arr)
        # free indices contracted with the polarisation of that leg (upper index, so use metric-lowered eps... we use plain product with pol since P and Metric carry the lowering)
        for i, l in labels.items():
            if i > 0:
                specs.append(l); arrays.append(pol[i])
        # dummies must be contracted with one metric each pair: our tensors carry all-lower-index
        # conventions except EPS; treat every dummy pair with a metric insertion
        dummies = [i for i in labels if i < 0]
        for i in dummies:
            l = labels[i]; l2 = next(letters)
            # replace second occurrence with l2 and insert metric(l, l2)
            seen = False; new = []
            for sp in specs:
                if l in sp and not seen and sp.count(l) == 1: seen = True; new.append(sp); continue
                if l in sp and seen: sp = sp.replace(l, l2, 1)
                new.append(sp)
            specs = new; specs.append(l + l2); arrays.append(G)
        try:
            v = np.einsum(",".join(specs) + "->", *arrays, optimize=True)
        except Exception:
            return None
        total += sign * coef * v; scale += abs(coef * v)
    return total, scale


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    ufo = os.path.abspath(argv[1]); L = open(os.path.join(ufo, "lorentz.py")).read(); V = open(os.path.join(ufo, "vertices.py")).read()
    rng = np.random.default_rng(1)
    zero = []
    everything = "--all" in argv
    for name, spins, struct in re.findall(r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[([^\]]*)\],\s*structure = '([^']*)'", L):
        if re.search(r"Gamma|Proj|Sigma|Gamma5|C\(", struct) or struct.strip() == "0": continue
        if not everything and "Epsilon" not in struct: continue
        nlegs = len(spins.split(","))
        parsed = parse(struct)
        vals = [evaluate(parsed, nlegs, rng) for _ in range(4)]
        if any(v is None for v in vals): continue
        if all(abs(t) <= 1e-9 * max(sc, 1e-300) for t, sc in vals) and all(sc > 0 for _, sc in vals):
            zero.append(name)
    print(f"identically zero Lorentz structures: {len(zero)} {zero}" + ("" if everything else " (Epsilon structures only; --all for every Dirac-free one)"))
    for z in zero:
        vs = [(n, re.sub(r"\s+", "", re.search(r"particles = \[(.*?)\]", b, re.S).group(1)).replace("P.", ""), re.findall(r"L\.(\w+)", b))
              for n, b in re.findall(r"(V_\d+) = Vertex\((.*?)\)\n\n", V + "\n\n", re.S) if re.search(rf"\bL\.{z}\b", b)]
        st = re.search(rf"{z} = Lorentz\(.*?structure = '([^']*)'", L, re.S).group(1)
        print(f"  {z}: {st[:150]}"); [print("     ", v) for v in vs]
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
