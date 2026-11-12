"""
tests/test_towers.py  --  the operators above dimension eight of the models of order N (gen/towers.py).

Run:  python3.11 tests/test_towers.py

Six checks, on the towers of the model of order 4 (dimensions ten and twelve) and its base.

1. The count: at each dimension, one member (H^dag H)^k Q for each of the 51 dimension-eight operators of the
   connection classes of the default basis (H^8, H^6D^2, X^3H^2, X^2H^4, XH^4D^2, psi^2XH^3, psi^2H^5,
   psi^2H^4D), and the two operators of the connection k^A_IJ that are new at dimension ten, 53 in all.
2. The names: the coefficient of the member of dimension d is c<d> followed by the label of its operator, the
   names are unique, and each member has the class, hc_mode, CP parity, generations and flavour structures of
   its dimension-eight operator.
3. The structure of every term (validate/structural.py), with the mass dimension of the member.
4. The CP parity recorded for each member is the one its encoded terms give (gen/cp_parity.py), and each is
   Hermitian or complex as its hc_mode says (validate/hermiticity.py), the checks the dimension-eight
   operators pass.  Q_{WH^6D^2}^{(5)} is CP even and Q^{(6)} CP odd.
5. The FeynRules file: one block per operator, each with its Lagrangian passed through the truncation of the
   model's base at its own order, the gluon member vev-subtracted, and the coefficients of dimension d in the
   blocks DIM<d> and DIM<d>F.
6. The base (gen/input_scheme.py on gen/input_scheme_formulae_geo4_mw.json): a value with more than PART_TERMS
   terms goes in as parts, each compiles with Python, which MadGraph evaluates every parameter with and whose
   compiler stops near 3000 terms, and the parts written one after the other are the value.
"""
from __future__ import annotations

import collections
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "gen"))
sys.path.insert(0, os.path.join(ROOT, "validate"))

import cp_parity  # noqa: E402
import emit_fr  # noqa: E402
import hermiticity  # noqa: E402
import input_scheme  # noqa: E402
import structural  # noqa: E402
import towers  # noqa: E402

cases = []


def check(name, got, want):
    cases.append((name, got, want))


def main(argv) -> int:
    conn = towers.connection_operators()
    ops = towers.towers(4)
    dim = towers.dimension
    check("dimension-eight connection operators by class", dict(sorted(collections.Counter(o.cls for o in conn).items())),
          {2: 1, 3: 2, 5: 6, 6: 10, 8: 6, 10: 11, 12: 3, 13: 12})
    check("members by dimension", dict(sorted(collections.Counter(dim(o) for o in ops).items())), {10: 53, 12: 53})
    check("coefficients carry the dimension", [o.wc for o in ops if not o.wc.startswith(f"c{dim(o)}")], [])
    check("unique names", (len({o.name for o in ops}), len({o.wc for o in ops})), (len(ops), len(ops)))
    by = {o.wc[2:]: o for o in conn}
    st = towers.structures(ops, emit_fr.MFV_STRUCTURES)
    own, differ = [], []
    for o in ops:
        b = by.get(o.wc[len(str(dim(o))) + 1:])
        if b is None:
            own.append(o.wc)
            continue
        if (b.cls, b.hc_mode, b.cp, b.gens) != (o.cls, o.hc_mode, o.cp, o.gens) or \
                (b.name in emit_fr.MFV_STRUCTURES and st.get(o.name) != emit_fr.MFV_STRUCTURES[b.name]):
            differ.append(o.wc)
    check("members without a dimension-eight operator", sorted(own),
          ["c10WH4D2x5", "c10WH4D2x6", "c12WH4D2x5", "c12WH4D2x6"])
    check("members that differ from their operator", differ, [])
    check("fermionic members without flavour structures", [o.wc for o in ops if o.gens and o.name not in st], [])
    bad = []
    for o in ops:
        probs = [p for p in structural.check_operator(o)["problems"] if not p.startswith("mass dimension")]
        if probs:
            bad.append((o.wc, probs[:2]))
    check("structure of every term", bad, [])
    check("CP parity from the encoded terms", cp_parity.report_disagreements(ops), 0)
    want = {"real": "hermitian", "complex": "complex"}
    check("Hermiticity as hc_mode says", [o.wc for o in ops if hermiticity.classify(o).kind != want.get(o.hc_mode)], [])
    check("CP of the new operators", {o.wc: o.cp for o in ops if "WH4D2x5" in o.wc or "WH4D2x6" in o.wc},
          {"c10WH4D2x5": "even", "c10WH4D2x6": "odd", "c12WH4D2x5": "even", "c12WH4D2x6": "odd"})
    txt, index = towers.emit(4)
    check("blocks: 51 of dimension eight again, 53 of ten, 53 of twelve",
          dict(sorted(collections.Counter(re.match(r"[A-Z]\d+op", e["block"]).group(0) for e in index).items())),
          {"G8op": 51, "T10op": 53, "T12op": 53})
    # Return[z8geoTrunc[z8lagH + z8lagN + ..., p]]; over several lines, the order p closing it
    trunc = [re.search(r", (\d+)\]\];", part).group(1) for part in txt.split("Return[z8geoTrunc[z8lagH")[1:]]
    check("every block truncated at its own order", collections.Counter(trunc), collections.Counter({"2": 51, "3": 53, "4": 53}))
    check("the gluon members are vev-subtracted", len(re.findall(r"-\(z8vT\^2/2\)\^\d+ FS\[G,", txt)), 3)
    blocks = set(re.findall(r"BlockName\s*->\s*(\w+)", txt))
    check("coefficient blocks", sorted(blocks), ["DIM10", "DIM10F", "DIM12", "DIM12F"])
    F = input_scheme.formulae("mw", 4)
    over, wrong, fails, longest = [], [], [], 0
    for k, v in F.items():
        parts = input_scheme.split_sum(v)
        again = parts[0] + "".join(" " + (x if x.startswith("- ") else "+ " + x) for x in parts[1:])
        if again != v:
            wrong.append(k)
        for x in parts:
            n = len(input_scheme.split_sum(x, 1))          # one part per term of the top-level sum
            longest = max(longest, n)
            if n > input_scheme.PART_TERMS:
                over.append(k)
            try:
                compile(x.replace("^", "**"), k, "eval")
            except (RecursionError, SyntaxError) as e:
                fails.append((k, type(e).__name__))
    check("the parts of every value of the base are the value", wrong, [])
    check(f"no part longer than {input_scheme.PART_TERMS} terms (longest {longest})", sorted(set(over)), [])
    check("every part compiles with Python", fails, [])
    check("the long values of order 4 are cut", sorted(k for k, v in F.items() if len(input_scheme.split_sum(v)) > 1),
          ["TAA3", "TAA4", "TAZ4", "TZA4", "TZZ3", "TZZ4", "aEW4", "g14"])
    nbad = [(n, g, w) for n, g, w in cases if g != w]
    for n, g, w in cases:
        print(("ok   " if g == w else "FAIL ") + n + ("" if g == w else f"\n       got {g!r}\n       want {w!r}"))
    print(f"\n{len(cases) - len(nbad)}/{len(cases)} passed")
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
