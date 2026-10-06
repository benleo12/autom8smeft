"""
validate/check_counts.py  --  the number of Lagrangian terms per class read from the
tables must equal Murphy's Table 1 (results_v5.tex), with a "+h.c." row counted as two
terms (Q and Q^dagger), which is the convention that reproduces his N_term column.

Usage: python3 validate/check_counts.py   (reads docs/catalogue.json)
"""

import json
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "validate"))
import catalogue   # noqa: E402

# Murphy 2005.00059 v6, Table 1 (N_term column).  "a+b": b terms vanish for n_g = 1.
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


def main():
    es = catalogue.derived()
    got = {}
    for e in es:
        key = (e["cls"], e["b_violating"]) if e["cls"] >= 18 else e["cls"]
        got[key] = got.get(key, 0) + (2 if e["plus_hc"] else 1)
    ok = True
    print(f"{'class':>12s} {'Murphy':>8s} {'tables':>8s}")
    for k in EXPECTED:
        g = got.get(k, 0)
        flag = "" if g == EXPECTED[k] else "   <-- MISMATCH"
        ok &= g == EXPECTED[k]
        print(f"{str(k):>12s} {EXPECTED[k]:8d} {g:8d}{flag}")
    tb = sum(v for k, v in got.items() if not (isinstance(k, tuple) and k[1]))
    tbv = sum(v for k, v in got.items() if isinstance(k, tuple) and k[1])
    print(f"\nB-conserving terms: {tb} (Murphy {TOTAL_B})\nB-violating terms:  {tbv} (Murphy {TOTAL_BV})\ntotal: {tb + tbv} (Murphy {TOTAL})")
    ok &= tb == TOTAL_B and tbv == TOTAL_BV
    parsed = sum(e["status"] == "ok" for e in es)
    print(f"\nrows parsed into the DSL: {parsed} / {len(es)}")
    print("term counts", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
