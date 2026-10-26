#!/usr/bin/env python3
"""CP parity of every operator of the catalogue, in one place.

    gen/cp_parity.py [--json out.json] [--compare]

The Murphy basis does not label CP, and the rule everyone reaches for, "CP odd when the number
of dual tensors is odd", is not safe at dimension eight.  The parity used here is derived field
by field and recorded in the catalogue, C times P with

    B_mu -> -B_mu,   W^I -> -s_I W^I,   G^A -> -s_A G^A,   H -> H^*,

where s = +1 for a generator whose matrix is symmetric (tau^1, tau^3 and the symmetric Gell-Mann
matrices) and s = -1 for an antisymmetric one (tau^2 and lambda^{2,5,7}), and P contributing
(-1)^{number of dual field strengths}.  The consequences that matter are that
(H^dag tau^I H) carries +s_I, that the mu-nu symmetric part of (D_mu H^dag tau^I D_nu H) carries
+s_I while its antisymmetric part carries -s_I, and that epsilon^{IJK} and f^{ABC} contribute
s_I s_J s_K = -1 while d^{ABC} contributes +1.  It reproduces the textbook assignment for every
operator built only from singlet contractions, and for Q_W, Q_G, Q_{HWB} and the HISZ structure
and their duals.  The parity of every operator is recorded in docs/catalogue.json.

Where it differs from dual counting, and it does on 170 of the 438 operators with a real coefficient,
the difference is real and the counting rule is what is wrong.  The sharpest case is the
psi^2 X^2 D family with identical field strengths: for Q_{q^2W^2D} the derivation gives
(1) even, (2) ODD, (3) even, (4) even, so the member that carries no dual is the CP-odd one and
the two that do carry one are not.  Counting duals gets that family exactly backwards, and the
CP test of validate/cp_rates.py fails on the set that dual counting calls odd.

An operator with a complex coefficient C enters as C Q + C* Q^dagger = Re C (Q + Q^dagger) +
Im C i(Q - Q^dagger).  With CP(Q) = eta Q^dagger the real part has parity eta and the imaginary part
-eta, so both parities are present, the parameter card carries them as separate entries, and the
catalogue records which is which: "Re even, Im odd" for eta = +1 and "Re odd, Im even" for
eta = -1.  The second case is not rare: Q_{leB^2H}^{(2)} = (lbar e) H Btilde B has eta = -1, and so
do 44 of the 236 baryon-conserving complex operators (classes 9, 15, 17 and 19).

The derivation is an assignment, not a theorem, and it is verified numerically rather than
trusted: the CP test switches the CP-odd set on alone and requires its interference with the Standard
Model in a CP-even rate to vanish while its square does not.
"""
from __future__ import annotations

import collections
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CATS = ("catalogue_bosonic", "catalogue_twofermion", "catalogue_fourfermion")
_CACHE = None


RE_EVEN, RE_ODD = "Re even, Im odd", "Re odd, Im even"


def table():
    """{label: 'even' | 'odd' | RE_EVEN | RE_ODD} for the whole catalogue, computed once.

    Assembled from the per-class catalogue files that carry the C x P derivation, whose "cp" is
    eta, the parity of the real part for a complex coefficient.  The public tree ships only the
    derived catalogue docs/catalogue.json, and there the table is read from it.  The derived
    catalogue is written from this table, so it is never read where the per-class files exist: it
    once was, and every complex operator then kept the label "Re/Im" it had been written with."""
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    if not all(os.path.exists(os.path.join(ROOT, "docs", f + ".json")) for f in CATS):
        derived = os.path.join(ROOT, "docs", "catalogue.json")
        _CACHE = {e["label"]: e["cp"] for e in json.load(open(derived))}
        return _CACHE
    cp = {}
    for f in CATS:
        for e in json.load(open(os.path.join(ROOT, "docs", f + ".json"))):
            cp[e["name"]] = e["cp"]
    rows = json.load(open(os.path.join(ROOT, "docs", "murphy_parsed.json")))
    out = {}
    for e in rows:
        # the per-class catalogue files spell Q_{q^2H^2D^3}^{(4)} as Q_{q^2H^2D^2}^{(4)}, as the
        # Murphy paper prints it; the operator belongs to the class psi^2H^2D^3
        eta = cp.get(e["label"], cp.get(e["label"].replace("D^3", "D^2")))
        if eta not in ("even", "odd"):
            raise KeyError(f"no derived CP parity for {e['label']}")
        out[e["label"]] = ({"even": RE_EVEN, "odd": RE_ODD}[eta] if e["hc_mode"] == "complex" else eta)
    _CACHE = out
    return out


def dual_count(op) -> str:
    """The rule this does NOT use, kept so that --compare can show where the two differ: the
    parity of the number of dual field strengths per term of the encoded operator."""
    import dsl
    if op.hc_mode == "complex":
        return "complex"
    par = {sum(1 for f in t.factors if isinstance(f, dsl.FS) and f.dual) % 2 for t in op.terms}
    return "odd" if par.pop() else "even"


def coefficient_sets():
    """(cp_odd, cp_even) Wilson coefficient names, flavour universal, baryon conserving.

    A coefficient is placed only when every operator sharing its block has the same parity, which
    is how a restriction card has to be built: a card switches a block on or off as a whole.  No
    block is mixed under the derived assignment, which is itself a check on it.  A complex
    coefficient enters as its two card entries, <name>Re with the parity of eta and <name>Im with
    the other one."""
    cp = table()
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    odd, even = [], []
    for e in idx:
        if int(e["block"][4:]) > 674:
            continue
        p = {cp[o] for o in e["ops"]}
        if p == {RE_EVEN}:
            even += [w + "Re" for w in e["wcs"]]
            odd += [w + "Im" for w in e["wcs"]]
            continue
        if p == {RE_ODD}:
            odd += [w + "Re" for w in e["wcs"]]
            even += [w + "Im" for w in e["wcs"]]
            continue
        if p == {"odd"}:
            odd += e["wcs"]
        elif p == {"even"}:
            even += e["wcs"]
    return odd, even


def main(argv) -> int:
    cp = table()
    print("CP parity of the 734 operators:", dict(collections.Counter(cp.values())))
    odd, even = coefficient_sets()
    print(f"coefficients in blocks that are uniformly CP odd: {len(odd)}, "
          f"uniformly CP even: {len(even)}")
    if "--compare" in argv:
        sys.path.insert(0, os.path.join(ROOT, "gen"))
        from operators import OPS
        d = collections.Counter()
        for op in OPS:
            if op.hc_mode == "complex":
                continue
            if dual_count(op) != cp[op.name]:
                d[op.cls] += 1
        print(f"operators where dual counting disagrees with the derivation: {sum(d.values())} "
              f"of {sum(1 for op in OPS if op.hc_mode != 'complex')}")
        print("  by class:", dict(sorted(d.items())))
    if "--json" in argv:
        json.dump(cp, open(argv[argv.index("--json") + 1], "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
