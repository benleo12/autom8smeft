"""
validate/check_dimensions_ufo.py  --  V16: mass-dimension consistency of every UFO vertex.

A dimension-eight operator enters the Lagrangian as (C / Lambda^4) O, and the Lagrangian
density has mass dimension four.  A vertex obtained from it by putting p of its Higgses on
their vacuum expectation value, keeping n legs of mass dimensions d_i (1 for a scalar or a
vector, 3/2 for a fermion) and q derivatives, therefore satisfies

    -4 (from Lambda^-4)  +  p (from vev^p)  +  sum_i d_i  +  q  =  4,

that is  p + q = 8 - sum_i d_i.  The relation is exact and involves nothing but the emitted
vertex itself, so it is a direct test of the emitter and of FeynRules' index expansion: a
dropped derivative, a spurious vev, a Higgs leg that was silently vev'd or a field strength
that lost its momentum all break it.  It is deliberately NOT the lambda counting of
gen/epower.py, whose q counts powers of E in the amplitude (external spinors contribute
sqrt(E) for each fermion) rather than derivatives in the Lagrangian.

p is read off the coupling value, q off the Lorentz structure, and both are required to be
the same for every monomial of a structure (FeynRules groups vertices by Lorentz structure,
so an inhomogeneous structure would itself be a finding and is reported).

Usage:  python3 validate/check_dimensions_ufo.py <ufo_dir>
Exit code 0 if every dimension-eight vertex is consistent, 1 otherwise.
"""

from __future__ import annotations

import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "validate"))

from audit_ufo import load_ufo, operators_by_wc, wc_in  # noqa: E402

# UFO spin codes: 1 = scalar, 2 = Dirac fermion, 3 = vector (2S+1)
DIM_BY_SPIN = {1: 2, 2: 3, 3: 2}  # twice the mass dimension, to stay in integers


def split_monomials(struct: str) -> list:
    """Split a UFO Lorentz structure into its top-level monomials (depth-zero + and -)."""
    out, depth, cur = [], 0, ""
    for i, ch in enumerate(struct):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        # not a term separator inside a float exponent such as 1e-6
        expo = i > 0 and struct[i - 1] in "eE" and i > 1 and (struct[i - 2].isdigit() or struct[i - 2] == ".")
        if depth == 0 and ch in "+-" and cur.strip() and not expo:
            out.append(cur)
            cur = ""
            continue
        cur += ch
    if cur.strip():
        out.append(cur)
    return [m for m in out if m.strip()]


def momenta(struct: str):
    """Set of momentum counts over the monomials of a Lorentz structure."""
    return {len(re.findall(r"\bP\(", m)) for m in split_monomials(struct)}


def _vev_power_term(term: str) -> int:
    p = 0
    for m in re.finditer(r"(/?)\s*\bvev\b(\s*\*\*\s*(\d+))?", term):
        k = int(m.group(3)) if m.group(3) else 1
        p += -k if m.group(1) == "/" else k
    return p


def vev_power(value: str):
    """Set of vev powers over the terms of a coupling.  A coupling is a SUM of terms (the
    UFO writes e.g. cw-part + sw-part for one Z vertex) and each term carries the same
    power, so the power must be read per term: summing over the whole string counts
    vev**4 + vev**4 as eight."""
    return {_vev_power_term(t) for t in split_monomials(value)}


def main(ufo: str) -> int:
    ol = load_ufo(ufo)
    ops = operators_by_wc()
    wcs = list(ops)
    bad, checked, skipped, inhomog = [], 0, 0, []

    for v in ol.all_vertices:
        twice_legs = sum(DIM_BY_SPIN.get(p.spin, 2) for p in v.particles)
        for (ic, il), c in sorted(v.couplings.items()):
            if c.order.get("NP", 0) != 2:      # only dimension-eight couplings
                continue
            found = wc_in(c.value, wcs)
            if not found:                      # no dimension-eight WC at all
                skipped += 1
                continue
            # a merged coupling (MergeVertices puts several operators on one Lorentz
            # structure) is still checkable: every term shares that structure, so every
            # term must satisfy the identity with the same q, i.e. the vev power must be
            # homogeneous across terms whichever operator produced them
            qs = momenta(v.lorentz[il].structure)
            if len(qs) != 1:
                inhomog.append((v.name, v.lorentz[il].name, sorted(qs)))
                continue
            q = qs.pop()
            ps = vev_power(c.value)
            if len(ps) != 1:
                inhomog.append((v.name, c.name, "vev powers " + str(sorted(ps))))
                continue
            p = ps.pop()
            checked += 1
            # 2*(p + q) + twice_legs must equal 16, i.e. p + q = 8 - sum(d_i)
            if 2 * (p + q) + twice_legs != 16:
                bad.append(dict(vertex=v.name, coupling=c.name, wc="/".join(found),
                                legs=[x.name for x in v.particles], p=p, q=q,
                                sum2d=twice_legs,
                                want=(16 - twice_legs) / 2.0, got=p + q))

    print(f"{len(ol.all_vertices)} vertices, {checked} dimension-eight couplings checked, "
          f"{skipped} skipped (merged or no single WC)")
    for s in inhomog[:10]:
        print(f"  inhomogeneous: {s[0]} {s[1]} {s[2]}")
    if inhomog:
        print(f"  ... {len(inhomog)} inhomogeneous Lorentz structures in total")
    for b in bad[:20]:
        print(f"  DIMENSION MISMATCH {b['vertex']} {b['coupling']} ({b['wc']}): "
              f"legs {'+'.join(b['legs'])} need p+q={b['want']}, got p={b['p']} q={b['q']}")
    if bad:
        print(f"  ... {len(bad)} mismatching couplings in total")
    ok = not bad and not inhomog
    print("dimension audit: " + ("PASS" if ok else "FAIL"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "tests/gen_smoke/uuww")))
