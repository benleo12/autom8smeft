#!/usr/bin/env python3
"""Operator counts of our catalogue against Matchete's dimension-eight model file.

    validate/matchete_rows.py /path/to/Matchete/Models/SMEFT_D8.m

Matchete [arXiv:2212.04510] ships ``SMEFT_D8.m``, its own implementation of the Murphy basis,
written in a different language, for a different purpose (functional matching rather than event
generation) and by different people.  That makes its coupling list an independent encoding of
the same operators, and comparing the two is a check no amount of internal consistency can give:
an operator we dropped, duplicated or attributed to the wrong class shows up as a count that
differs, and an operator missing from their file shows up the same way.

The comparison is at the level of operators per (class, baryon number), which is what the two
files can be compared on without translating conventions: their couplings carry flavour indices
and ours are flavour universal, their labels are Mathematica ``NiceForm`` strings and ours are
the labels of the Murphy basis, but both have exactly one coupling per operator.

The file is not redistributed here.  Obtain Matchete from its authors.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def theirs(path):
    """Couplings per (class, baryon-violating), read from the section comments of the file.

    Their headers are not bare class numbers: class 15 is split into ``(* 15 RR *)`` and
    ``(* 15 LL *)``, class 18 into six chirality sections and class 19 into five, so a regular
    expression anchored on ``(* N *)`` alone would fold the whole of class 15 into class 14,
    with no error.  This takes the leading integer of the header and looks for the word
    ``B-violating`` in the rest."""
    lines = open(path).read().split("\n")
    start = next(i for i, l in enumerate(lines) if l.strip() == "(* Dimension 8 *)")
    end = next(i for i, l in enumerate(lines) if i > start and "Subsubsection" in l)
    cls, bv, per = None, False, collections.Counter()
    for l in lines[start:end]:
        m = re.match(r"\s*\(\*\s*(\d+)\b(.*?)\*\)\s*$", l)
        if m:
            cls, bv = int(m.group(1)), "B-violating" in m.group(2)
            continue
        for _ in re.findall(r"DefineCoupling\[\s*([A-Za-z0-9$]+)", l):
            per[(cls, bv)] += 1
    return per


def ours():
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    mur = {e["label"]: e for e in json.load(open(os.path.join(ROOT, "docs", "catalogue.json")))}
    out = collections.Counter()
    for e in idx:
        for o in e["ops"]:
            out[(e["cls"], mur[o]["b_violating"])] += 1
    return out


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    a, b = ours(), theirs(argv[1])
    print(f"{'class':>6s} {'B-viol':>7s} {'ours':>6s} {'Matchete':>9s}")
    bad = 0
    for k in sorted(set(a) | set(b)):
        x, y = a.get(k, 0), b.get(k, 0)
        bad += x != y
        print(f"{k[0]:>6d} {'yes' if k[1] else 'no':>7s} {x:>6d} {y:>9d}"
              + ("   <-- differs" if x != y else ""))
    print(f"\ntotals: ours {sum(a.values())} operators, Matchete {sum(b.values())} couplings, "
          f"{len(set(a) | set(b))} buckets, {bad} differing")
    print("Matchete counts", "PASS" if bad == 0 else "FAIL")
    return 0 if bad == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
