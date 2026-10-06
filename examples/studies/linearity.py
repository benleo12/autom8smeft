#!/usr/bin/env python3
"""The linearity check the paper quotes, recomputed from the study data.

    examples/studies/linearity.py

The dimension-eight interference is linear in the coefficients, so the sum of the per-class rows
must reproduce the run with every coefficient of that card switched on at once.  It is the
cross-section level statement that the restriction cards keep exactly what they should and that
the all-on run has nothing the class rows miss.

The card has to match: the triboson and vector-boson-fusion all-on rows were run on the bosonic
card, so they are compared against classes 1 to 8 and not against all 21.  Comparing all 21
against a bosonic all-on row gives a 200 sigma "failure" that is entirely the mismatch.  A class
row that was never integrated makes the check incomplete rather than failed, and is reported so.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import table_appendix as T  # noqa: E402

BOSONIC = set(range(1, 9))


def main():
    data = {s: T.read(s) for s in {p[0] for p in T.PROCS}}
    rows, skipped = [], []
    for st, pr, h in T.PROCS:
        d = data[st]
        allon = [(m, x) for (p_, m, o), x in d.items()
                 if p_ == pr and o == T.INT and "-cls" not in m and isinstance(x[0], float)]
        for m, (a, ea) in allon:
            which = BOSONIC if m.endswith("-bosonic") else set(T.CLASSES)
            tot = var = 0.0
            miss = []
            for c in which:
                v = d.get((pr, f"dim8_is-cls{c}", T.INT), (None, None))
                if isinstance(v[0], float):
                    tot += v[0]
                    var += v[1] ** 2
                elif v[0] == "NOT_INTEGRATED":
                    miss.append(c)
            if miss:
                skipped.append((h, m, sorted(miss)))
                continue
            s = (var + ea ** 2) ** 0.5
            rows.append((abs(tot - a) / s if s else 0.0, h, m, tot, a))

    w = max(len(r[1]) for r in rows) if rows else 10
    for dev, h, m, tot, a in rows:
        print(f"{h:<{w}s}  {m:<18s} classes {tot:+.5g}  all-on {a:+.5g}   {dev:.2f} sigma")
    for h, m, miss in skipped:
        print(f"{h:<{w}s}  {m:<18s} INCOMPLETE, classes never integrated: {miss}")
    if rows:
        d = sorted(r[0] for r in rows)
        print(f"\n{len(rows)} complete checks, {d[0]:.1f} to {d[-1]:.1f} sigma")
        bad = [r for r in rows if r[0] > 3]
        print("all pass at 3 sigma" if not bad else f"FAILURES: {[r[1] for r in bad]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
