#!/usr/bin/env python3
"""Find UFO vertices that are identically zero, Dirac structures included.

    validate/zero_vertex.py <UFO dir> [--structures] [--wcs]   (needs numpy: python3.13 here)

validate/zero_lorentz.py tests each Lorentz structure on its own and skips anything carrying a
Gamma, on the assumption, written into its docstring, that no zero structure has one.  That
assumption is false: Q_{q^4B}^{(4)} reaches the shipped model with FFFFV200, a four-fermion
structure that ALOHA reduces to zero and then writes as a Fortran routine whose arguments it
never declares, so `u u~ > d d~ a` dies with "A compilation Error occurs" and the real message,
"Symbol 'f1' has no IMPLICIT type", appears only if you run make in Source/DHELAS by hand.

Two things are tested here that zero_lorentz.py cannot reach.

  --structures   every Lorentz structure, Dirac ones included, evaluated at random momenta
                 obeying momentum conservation, random polarisations for the vector legs and
                 random four-component wavefunctions for the fermion legs.  Generic rather than
                 on-shell wavefunctions on purpose: that is what ALOHA reduces, so a structure
                 that vanishes only on shell is correctly kept.

  --wcs          the whole vertex, sum over (colour, Lorentz) of coupling times structure, per
                 Wilson coefficient.  This is the test that catches a coefficient whose every
                 vertex cancels between two live structures, which is how six of the psi^4 B
                 operators come to be presented as live and give exactly zero: their two
                 surviving structures differ by a swap of two dummy indices inside one Epsilon
                 and carry the same coupling, so they sum to nothing.

Default runs both.  A structure or coefficient is reported when it vanishes at every random
point to 1e-9 of the size of its own terms, which for a multilinear form is proof.
"""
import itertools, os, re, sys
import numpy as np

G = np.diag([1.0, -1.0, -1.0, -1.0])
EPS = np.zeros((4, 4, 4, 4))
for _p in itertools.permutations(range(4)):
    _s, _q = 1, list(_p)
    for _i in range(4):
        for _j in range(_i + 1, 4):
            if _q[_i] > _q[_j]: _s = -_s
    EPS[_p] = _s

# Dirac matrices, Dirac basis; only the algebra matters for a zero test.
_I2, _s1 = np.eye(2), np.array([[0, 1], [1, 0]], dtype=complex)
_s2, _s3 = np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]], dtype=complex)
GAMMA = np.zeros((4, 4, 4), dtype=complex)
GAMMA[0] = np.block([[_I2, np.zeros((2, 2))], [np.zeros((2, 2)), -_I2]])
for _k, _s in enumerate((_s1, _s2, _s3), start=1):
    GAMMA[_k] = np.block([[np.zeros((2, 2)), _s], [-_s, np.zeros((2, 2))]])
GAMMA5 = 1j * GAMMA[0] @ GAMMA[1] @ GAMMA[2] @ GAMMA[3]
ID4 = np.eye(4, dtype=complex)
PROJP, PROJM = (ID4 + GAMMA5) / 2, (ID4 - GAMMA5) / 2
SIGMA = np.zeros((4, 4, 4, 4), dtype=complex)
for _m in range(4):
    for _n in range(4):
        SIGMA[_m, _n] = 0.5j * (GAMMA[_m] @ GAMMA[_n] - GAMMA[_n] @ GAMMA[_m])

# name -> (number of Lorentz indices, number of spinor indices)
SHAPE = {"Epsilon": (4, 0), "Metric": (2, 0), "P": (2, 0), "Gamma": (1, 2), "Gamma5": (0, 2),
         "Identity": (0, 2), "ProjP": (0, 2), "ProjM": (0, 2), "Sigma": (2, 2)}


def strip_outer(t):
    while t.startswith("(") and t.endswith(")"):
        d = 0
        for k, ch in enumerate(t):
            d += (ch == "(") - (ch == ")")
            if d == 0 and k < len(t) - 1: return t
        t = t[1:-1]
    return t


def split_top(s, seps):
    out, d, cur = [], 0, ""
    for ch in s:
        d += (ch == "(") - (ch == ")")
        if ch in seps and d == 0:
            out.append(cur); cur = ""
            if ch == "-": cur = "-"
        else:
            cur += ch
    out.append(cur)
    return [t for t in out if t.strip()]


def parse(struct):
    """[(coefficient, [(name, lorentz indices, spinor indices)])] or None if unsupported."""
    s = struct.replace(" ", "")
    terms, d, cur, sign = [], 0, "", 1
    for ch in s:
        d += (ch == "(") - (ch == ")")
        if ch in "+-" and d == 0:
            if cur: terms.append((sign, cur))
            cur, sign = "", (1 if ch == "+" else -1)
        else:
            cur += ch
    if cur: terms.append((sign, cur))
    parsed = []
    for sign, term in terms:
        coef, tens = complex(sign), []
        for f in split_top(strip_outer(term), "*"):
            f = strip_outer(f)
            m = re.match(r"(\w+)\(([^()]*)\)$", f)
            if m and m.group(1) in SHAPE:
                name = m.group(1)
                args = [int(a) for a in m.group(2).split(",")]
                nl, ns = SHAPE[name]
                if len(args) != nl + ns: return None
                tens.append((name, args[:nl], args[nl:]))
            else:
                try:
                    coef *= complex(eval(f, {"__builtins__": {}}, {"complex": complex}))
                except Exception:
                    return None
        parsed.append((coef, tens))
    return parsed


def chain_arrays(tens, spin):
    """Contract the Dirac factors into one array per fermion chain.

    Returns a list of (array, lorentz index labels) plus None if the spinor structure is not a
    set of open chains between external legs."""
    dirac = [(n, li, si) for n, li, si in tens if SHAPE[n][1] == 2]
    if not dirac: return []
    # row index si[0], column index si[1]; negative indices are internal to a chain
    by_row = {}
    for k, (n, li, si) in enumerate(dirac):
        by_row.setdefault(si[0], []).append(k)
    used, out = set(), []
    starts = [si[0] for n, li, si in dirac if si[0] > 0]
    for start in starts:
        ks, cur, labels, mats = [], start, [], []
        while True:
            cand = [k for k in by_row.get(cur, []) if k not in used]
            if not cand: return None
            k = cand[0]; used.add(k); ks.append(k)
            n, li, si = dirac[k]
            labels.extend(li)
            mats.append((n, li))
            cur = si[1]
            if cur > 0: break
        # build the array over this chain's Lorentz indices
        shape = tuple(4 for _ in labels)
        arr = np.zeros(shape, dtype=complex)
        for combo in itertools.product(range(4), repeat=len(labels)):
            M, pos = ID4, 0
            for n, li in mats:
                if n == "Gamma":    F = GAMMA[combo[pos]]; pos += 1
                elif n == "Sigma":  F = SIGMA[combo[pos], combo[pos + 1]]; pos += 2
                elif n == "Gamma5": F = GAMMA5
                elif n == "ProjP":  F = PROJP
                elif n == "ProjM":  F = PROJM
                else:               F = ID4
                M = M @ F
            arr[combo] = spin[start] @ M @ spin[cur]
        out.append((arr, labels))
    if len(used) != len(dirac): return None
    return out


def evaluate(parsed, rng, nlegs=None):
    """Value at one random point, or None if the term uses something unsupported."""
    if parsed is None: return None
    legs, plegs = set(), set()
    for _, tens in parsed:
        for n, li, si in tens:
            legs |= {i for i in li if i > 0} | {i for i in si if i > 0}
            if n == "P": plegs.add(li[1] if len(li) > 1 else li[0])
    # The leg count must come from the vertex's own spins list, not from the indices that happen
    # to appear.  Inferring it made a three-point V V S look like a two-point one and imposed
    # p1 = -p2, which turns the CP-odd Epsilon(1,2,a,b) p1^a p2^b of VVS2 into a false zero.
    nmax = max(nlegs or 0, max(legs | plegs | {2}))
    mom = {i: rng.normal(size=4) for i in range(1, nmax + 1)}
    mom[nmax] = -sum(mom[i] for i in range(1, nmax))   # ALOHA imposes momentum conservation
    pol = {i: rng.normal(size=4) + 1j * rng.normal(size=4) for i in range(1, nmax + 1)}
    spin = {i: rng.normal(size=4) + 1j * rng.normal(size=4) for i in range(1, nmax + 1)}
    total, scale = 0j, 0.0
    for coef, tens in parsed:
        chains = chain_arrays(tens, spin)
        if chains is None: return None
        labels, specs, arrays = {}, [], []
        letters = iter("abcdefghijklmnopqrstuvwxyz")
        def lab(i):
            if i not in labels: labels[i] = next(letters)
            return labels[i]
        for n, li, si in tens:
            if SHAPE[n][1] == 2: continue
            if n == "P":
                arrays.append(G @ mom[li[1]] if len(li) > 1 else G @ mom[li[0]])
                specs.append(lab(li[0]))
            else:
                arrays.append(EPS if n == "Epsilon" else G)
                specs.append("".join(lab(i) for i in li))
        for arr, ls in chains:
            arrays.append(arr); specs.append("".join(lab(i) for i in ls))
        for i in [i for i in labels if i > 0]:          # free Lorentz index: a vector leg
            arrays.append(pol[i]); specs.append(labels[i])
        for i in [i for i in labels if i < 0]:          # dummy: one metric per pair
            l = labels[i]; l2 = next(letters)
            seen, new = False, []
            for sp in specs:
                if l in sp and not seen: seen = True; new.append(sp); continue
                if l in sp and seen: sp = sp.replace(l, l2, 1)
                new.append(sp)
            specs = new; specs.append(l + l2); arrays.append(G)
        try:
            v = np.einsum(",".join(specs) + "->", *arrays, optimize=True)
        except Exception:
            return None
        total += coef * v; scale += abs(coef) * abs(v)
        # The natural size of the term, the product of the norms of what it contracts.  The zero
        # test compares the total with the scale, and a scale built only from the terms' own
        # values is rounding noise when every term vanishes by itself: VSS1 of Q_{BH^4D^2}^{(2)},
        # Epsilon p1 p2 p3 at three legs, is zero term by term under momentum conservation and
        # read as 1e-16 against 3e-16, so it was kept and ALOHA wrote an empty routine
        # (2026-10-04).  The scale is therefore the larger of the two.
        nat = abs(coef)
        for arr in arrays:
            nat *= float(np.linalg.norm(np.asarray(arr).ravel()))
        scale = max(scale, nat)
    return total, scale


def zero_structures(ufo, verbose=True):
    txt = open(os.path.join(ufo, "lorentz.py")).read()
    hits, tested, skipped = [], 0, 0
    rng = np.random.default_rng(20260907)
    for name, spins, struct in re.findall(r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[([^\]]*)\],\s*"
                                          r"structure = '([^']*)'\)", txt):
        if struct.strip() in ("0", ""):
            hits.append(name); continue
        nlegs = len([x for x in spins.split(",") if x.strip()])
        p = parse(struct)
        vals = [evaluate(p, rng, nlegs) for _ in range(4)]
        if any(v is None for v in vals):
            skipped += 1; continue
        tested += 1
        if all(abs(t) <= 1e-9 * max(s, 1e-300) for t, s in vals):
            hits.append(name)
    if verbose:
        print(f"structures tested {tested}, unsupported {skipped}, identically zero {len(hits)}")
        if hits: print("   " + " ".join(sorted(hits)))
    return set(hits)


def dead_coefficients(ufo, zeros, verbose=True):
    """Wilson coefficients whose every vertex sums to zero over its Lorentz structures.

    A coefficient can have hundreds of live couplings and still contribute nothing, if the
    structures they multiply cancel among themselves.  For each coefficient, every vertex it
    touches is evaluated as sum over (colour, Lorentz) of coupling times structure, at random
    points, with the coefficient at one and all others at zero."""
    sys.path.insert(0, ufo)
    import parameters as P, couplings as C, vertices as V
    import cmath, math

    wcs = [p.name for p in P.all_parameters
           if p.nature == "external" and p.name.startswith("c8") and p.name != "Lam"]
    base = {p.name: float(p.value) for p in P.all_parameters if p.nature == "external"}
    ns = {"cmath": cmath, "math": math, "complex": complex,
          "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z}

    def params(on):
        v = dict(base)
        for k in wcs: v[k] = 0.0
        v[on] = 1.0
        for p in P.all_parameters:
            if p.nature == "internal":
                try: v[p.name] = eval(p.value, ns, v)
                except Exception: v[p.name] = float("nan")
        return v

    struct = {}
    txt = open(os.path.join(ufo, "lorentz.py")).read()
    for name, st in re.findall(r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[[^\]]*\],\s*"
                               r"structure = '([^']*)'\)", txt):
        struct[name] = st

    touched = {}
    for vx in V.all_vertices:
        names = set()
        for c in vx.couplings.values():
            names |= {w for w in wcs if re.search(r"\b" + w + r"\b", c.value)}
            names |= {w for w in wcs if re.search(r"\b" + w + r"(Re|Im)\b", c.value)}
        for w in names: touched.setdefault(w, []).append(vx)

    dead = []
    for w in sorted(touched):
        vals = params(w)
        alive = False
        for vx in touched[w]:
            for ci in range(len(vx.color)):
                tot, scale = 0j, 0.0
                for rep in range(3):
                    rng = np.random.default_rng(1000 + rep)
                    tot, scale = 0j, 0.0
                    for (cc, li), cp in vx.couplings.items():
                        if cc != ci: continue
                        try: g = complex(eval(cp.value, ns, dict(vals)))
                        except Exception: g = float("nan")
                        if g != g: continue
                        st = struct.get(vx.lorentz[li].name)
                        if st is None: continue
                        if st.strip() in ("0", ""): continue
                        # Same trap evaluate() warns about: the leg count is the vertex's,
                        # not whatever indices the structure happens to mention.  Inferring
                        # it imposed three-leg momentum conservation on the four-leg g g g H
                        # of VVVS4 and reported c8G2H4x2 dead when it is not.
                        e = evaluate(parse(st), rng, len(vx.particles))
                        if e is None: alive = True; break
                        tot += g * e[0]; scale += abs(g) * e[1]
                    if alive or abs(tot) > 1e-9 * max(scale, 1e-300): break
                if alive or abs(tot) > 1e-9 * max(scale, 1e-300): alive = True; break
            if alive: break
        if not alive: dead.append((w, len(touched[w])))
    if verbose:
        print(f"coefficients with couplings but no surviving vertex: {len(dead)}")
        for w, n in dead: print(f"   {w:16s} touches {n} vertices, every one of them sums to zero")
    return dead


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    ufo = os.path.abspath(argv[1])
    want = set(a for a in argv[2:] if a.startswith("--")) or {"--structures", "--wcs"}
    zeros = zero_structures(ufo) if "--structures" in want else set()
    if "--wcs" in want: dead_coefficients(ufo, zeros)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
