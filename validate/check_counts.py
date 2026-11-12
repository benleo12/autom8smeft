"""
validate/check_counts.py  --  the number of Lagrangian terms per class in the catalogue
must equal the N_term column of Table 1 of the Murphy basis paper (arXiv:2005.00059).  An
operator written with "+h.c." counts as two terms (Q and Q^dagger), which is the convention
of that column.

Usage: python3 validate/check_counts.py   (reads docs/catalogue.json)
"""

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "validate"))
import catalogue   # noqa: E402

# arXiv:2005.00059 v6, Table 1 (N_term column).  In "a+b" the b terms vanish for n_g = 1.
EXPECTED = {
    1: 43, 2: 1, 3: 2, 4: 3, 5: 6, 6: 10, 7: 18, 8: 6,
    9: 96, 10: 22, 11: 16, 12: 6, 13: 13, 14: 57, 15: 92, 16: 48, 17: 36,
    (18, False): 75 + 1, (18, True): 12 + 8,
    (19, False): 156 + 12, (19, True): 44 + 12,
    (20, False): 134 + 2, (20, True): 32,
    (21, False): 55, (21, True): 10 + 2,
}
TOTAL_B = 895 + 15
TOTAL_BV = 98 + 22
TOTAL = 993 + 37


def vanishing_wcs():
    """Coefficients whose operator, as encoded, emits an identically vanishing Lagrangian."""
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    import emit_fr                    # noqa: E402
    from operators import OPS         # noqa: E402
    return {o.wc for o in OPS if emit_fr.emit_operator_expr(o).endswith("(0)")}


def main():
    es = catalogue.derived()
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    import basis                      # noqa: E402
    # A label whose operator vanishes identically is not a term of the basis.  As printed,
    # Q_{udWH^2}^{(1,2)} vanished, and counting their labels made class 15 agree with Table 1
    # while the encoded basis was two operators short.  Classes 18 to 21 are exempt: their "+b"
    # terms vanish for one generation by construction and Table 1 counts them.
    dead = vanishing_wcs()
    # Class 11 is held in two forms, the fifteen operators of the Murphy basis and the fifteen of the
    # default basis that take their place (gen/basis.py).  A model has one form or the other, so the
    # terms are counted once for each, the operators common to both with those of that form, and
    # each count must be that of Table 1.
    forms = [b for b in ("murphy",) + tuple(x for x in basis.BASES if x != "murphy")
             if any(e.get("basis") == b for e in es)] or [None]
    got, skipped = {b: {} for b in forms}, []
    for e in es:
        key = (e["cls"], e["b_violating"]) if e["cls"] >= 18 else e["cls"]
        if e["cls"] < 18 and e["wc"] in dead:
            skipped.append(e["label"])
            continue
        for b in forms:
            if e.get("basis") in (None, b):
                got[b][key] = got[b].get(key, 0) + (2 if e["plus_hc"] else 1)
    if skipped:
        print(f"not counted, the operator vanishes identically: {', '.join(skipped)}\n")
    ok = True
    name = lambda b: "encoded" if b is None else basis.NAME[b]
    print(f"{'class':>12s} {'Table 1':>8s} " + " ".join(f"{name(b):>8s}" for b in forms))
    for k in EXPECTED:
        g = [got[b].get(k, 0) for b in forms]
        flag = "" if all(x == EXPECTED[k] for x in g) else "   <-- MISMATCH"
        ok &= not flag
        print(f"{str(k):>12s} {EXPECTED[k]:8d} " + " ".join(f"{x:8d}" for x in g) + flag)
    for b in forms:
        tb = sum(v for k, v in got[b].items() if not (isinstance(k, tuple) and k[1]))
        tbv = sum(v for k, v in got[b].items() if isinstance(k, tuple) and k[1])
        print(f"\n{name(b)}: B-conserving terms {tb} (Table 1 {TOTAL_B}), B-violating terms {tbv} (Table 1 {TOTAL_BV}), "
              f"total {tb + tbv} (Table 1 {TOTAL})")
        ok &= tb == TOTAL_B and tbv == TOTAL_BV
    parsed = sum(e["status"] == "ok" for e in es)
    print(f"\noperators encoded: {parsed} / {len(es)}")
    print("term counts", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
