#!/usr/bin/env python3
"""CP parity of every operator of the catalogue, in one place.

    gen/cp_parity.py [--json out.json] [--compare]
    gen/cp_parity.py --check

The Murphy basis does not label CP, and the rule everyone reaches for, "CP odd when the number
of dual tensors is odd", is not safe at dimension eight.  The parity used here is C times P, derived
field by field, with

    B_mu -> -B_mu,   W^I -> -s_I W^I,   G^A -> -s_A G^A,   H -> H^*,

where s = +1 for a generator whose matrix is symmetric (tau^1, tau^3 and the symmetric Gell-Mann
matrices) and s = -1 for an antisymmetric one (tau^2 and lambda^{2,5,7}), and P contributing
(-1)^{number of dual field strengths}.  The consequences that matter are that
(H^dag tau^I H) carries +s_I, that the mu-nu symmetric part of (D_mu H^dag tau^I D_nu H) carries
+s_I while its antisymmetric part carries -s_I, and that epsilon^{IJK} and f^{ABC} contribute
s_I s_J s_K = -1 while d^{ABC} contributes +1.  It reproduces the textbook assignment for every
operator built only from singlet contractions, and for Q_W, Q_G, Q_{HWB} and the HISZ structure
and their duals.  The parity of every operator is recorded in gen/operators.py (Operator.cp), which
table() reads and docs/catalogue.json copies.

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

The record is checked against the encoded terms, which --check and ./dim8 build do for every operator.
The eta of a term is the product of the signs of its building blocks, the rule of the appendix on
conventions of the paper: -1 for a vector or tensor bilinear and +1 for a scalar one, with or without
derivatives or a charge-conjugation matrix, -1 for a field strength and +1 for a dual one, -1 for each
epsilon^{IJK} or f^{ABC} and for a Lorentz epsilon that writes out a dual, +1 for d^{ABC} and for the
Higgs fields, and -1 for a term with an imaginary coefficient, which is how the i of a Hermitian derivative,
and the i restored in an operator that is anti-Hermitian as printed, appear in the encoding.  Every term
of an operator must give the same eta.
With hc_mode "real" or "sym" the parity is then "even" or "odd" for eta = +1 or -1, and with
"complex" it is the label above.  A disagreement with the record is a finding about the operator or
about the rule, so it is reported and nothing overwrites either of them: whoever corrects an operator
looks at the report and sets its cp by hand.

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
_CACHE = None
_BVIOL = None


RE_EVEN, RE_ODD = "Re even, Im odd", "Re odd, Im even"
HC_MODES = ("real", "complex", "sym")


def _operators():
    """The encoding, gen/operators.py."""
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    from operators import OPS
    return OPS


def table():
    """{label: 'even' | 'odd' | RE_EVEN | RE_ODD} for the whole catalogue, computed once and read from
    the encoding, so that it follows a correction to an operator and needs no other file."""
    global _CACHE
    if _CACHE is None:
        _CACHE = {op.name: op.cp for op in _operators()}
    return _CACHE


def carries_baryon_number(op) -> bool:
    """Whether the fields of an operator carry a net number of quarks, which makes it baryon-number
    violating whatever its place in the encoding.  A charge-conjugated field counts as the field it
    is: psi^T C is a quark and psi^c an antiquark, as the flag bar says."""
    import dsl
    return sum(-1 if f.bar else 1 for f in op.terms[0].factors
               if isinstance(f, dsl.Psi) and f.name in ("q", "u", "d")) != 0


def baryon_violating():
    """The labels of the baryon-number-violating operators, computed once."""
    global _BVIOL
    if _BVIOL is None:
        _BVIOL = {op.name for op in _operators() if carries_baryon_number(op)}
    return _BVIOL


def term_eta(term):
    """eta of one encoded term, CP(term) = eta term^dagger, or None for a coefficient that is neither
    real nor imaginary, which has no definite parity.  The rule is in the module docstring.  A product
    gamma^mu gamma^nu = g^{mu nu} - i sigma^{mu nu} counts +1, since the scalar part has +1 and the
    tensor part has -1 from the tensor and -1 from its i."""
    import dsl
    if term.coeff.re != 0 and term.coeff.im != 0:
        return None
    eta = -1 if term.coeff.re == 0 else 1
    for f in term.factors:
        if isinstance(f, dsl.Gamma) and f.kind in ("ga", "sig"):
            eta = -eta
        elif isinstance(f, dsl.FS) and not f.dual:
            eta = -eta
        elif isinstance(f, dsl.Tensor) and f.kind in ("epsIJK", "f", "epsLor"):
            eta = -eta
    return eta


def derived(op):
    """(the parity label the encoded terms of an operator give, None), or (None, why they give none)."""
    if op.hc_mode not in HC_MODES:
        return None, f"hc_mode {op.hc_mode!r} is none of {', '.join(HC_MODES)}, and the emitter would drop the operator"
    etas = {term_eta(t) for t in op.terms if not t.coeff.is_zero()}
    if None in etas:
        return None, "a term has a coefficient that is neither real nor imaginary"
    if len(etas) != 1:
        return None, "the terms do not share one parity" if etas else "the operator has no term"
    eta = etas.pop()
    if op.hc_mode == "complex":
        return (RE_EVEN if eta > 0 else RE_ODD), None
    return ("even" if eta > 0 else "odd"), None


def disagreements(ops=None):
    """(label, recorded parity, derived parity or why there is none) of the operators whose record is
    not what their terms give."""
    out = []
    for op in _operators() if ops is None else ops:
        got, why = derived(op)
        if got != op.cp:
            out.append((op.name, op.cp, got or why))
    return out


def report_disagreements(ops=None) -> int:
    """Print the check of the record against the encoded terms and return the number of disagreements."""
    ops = _operators() if ops is None else ops
    bad = disagreements(ops)
    for name, recorded, got in bad:
        print(f"[CP] {name}: gen/operators.py records {recorded!r}, the encoded terms give {got!r}")
    print(f"CP parity from the encoded terms: {len(ops) - len(bad)} of {len(ops)} operators agree with the record")
    return len(bad)


def dual_count(op) -> str:
    """The rule this does NOT use, kept so that --compare can show where the two differ: the
    parity of the number of dual field strengths per term of the encoded operator."""
    import dsl
    if op.hc_mode == "complex":
        return "complex"
    par = {sum(1 for f in t.factors if isinstance(f, dsl.FS) and f.dual) % 2 for t in op.terms}
    return "odd" if par.pop() else "even"


def coefficient_sets(b=None, ufo=None):
    """(cp_odd, cp_even) Wilson coefficient names, one per operator and one per flavour structure, baryon
    conserving, of the operators of basis b (gen/basis.py: DIM8_BASIS, or the default), since a card
    that names an operator of the other basis cannot be written for the model.  With ufo, a model of
    order N (gen/towers.py), the coefficients of the members of its towers as well (tower_sets).

    A coefficient is placed only when every operator sharing its block has the same parity, which
    is how a restriction card has to be built: a card switches a block on or off as a whole.  No
    block is mixed under the derived assignment, which is itself a check on it.  A complex
    coefficient enters as its two card entries, <name>Re with the parity of eta and <name>Im with
    the other one."""
    cp = table()
    bviol = baryon_violating()
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    import basis
    odd, even = [], []
    for e in idx:
        if bviol & set(e["ops"]) or not basis.in_basis(e["wcs"], b):
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
    # The coefficients of the flavour structures (gen/emit_flavour.py), each a card entry of its own, with
    # the parity of its part: that of the operator for the part "re" and the other one for "im".
    import emit_flavour as EF
    structures = EF.load_structures()
    for op in _operators():
        if op.name in bviol or op.name not in structures or not basis.in_basis([op.wc], b):
            continue
        for s in EF.structure_parameters(op, structures[op.name]):
            for name, _, parity in s["externals"]:
                (odd if parity == "odd" else even).append(name)
    if ufo:
        o, e = tower_sets(ufo, odd, even)
        odd, even = odd + o, even + e
    return odd, even


def tower_sets(ufo, odd, even):
    """(cp_odd, cp_even) coefficients of the members of the towers of a model of order N: the external
    parameters c<d><label> of the blocks DIM10, DIM10F, ... and GEOGF.  (H^dag H)^k is CP even, so a
    member c<d><label> has the parity of c8<label>, its part and flavour structure included.  The members
    without an operator of dimension eight have the parity gen/towers.py derives for them (Q_{WH^6D^2}^{(5)}
    even, Q^{(6)} odd), and the four-lepton members of the G_F relation c<d>l4H2x3F.. of
    (H^dag H)^m (H^dag tau^I H)(H^dag tau^J H)(lbar g tau^I l)(lbar g tau^J l) (gen/derive_geo.py) are even:
    under CP each H^dag tau^I H takes s_I and each current lbar g^mu tau^I l takes -s_I with its index
    lowered, so the product is even, and the structures delta_pt delta_sr and delta_pt (Y_e Y_e^dag)_sr are
    real and make the operator Hermitian with a real coefficient."""
    import re
    txt = open(os.path.join(ufo, "parameters.py")).read()
    ext = re.findall(r"name = '(c(\d+)[A-Za-z]\w*)',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,"
                     r"\s*texname = '[^']*',\s*lhablock = '(\w+)'", txt)
    members = [(n, int(d)) for n, d, blk in ext if re.fullmatch(r"DIM(1[0-9]|[2-9][0-9])F?|GEOGF", blk)]
    if not members:
        return [], []
    import towers
    own = {o.wc: o.cp for d in sorted({d for _, d in members}) for o in towers.tower(d)}
    so, se = set(odd), set(even)
    o, e, unknown = [], [], []
    for n, d in members:
        parent = "c8" + n[len(f"c{d}"):]
        if parent in so:
            o.append(n)
        elif parent in se:
            e.append(n)
        elif own.get(n) in ("even", "odd"):
            (o if own[n] == "odd" else e).append(n)
        elif re.fullmatch(r"c\d+l4H2x3Fx0[0E]", n):
            e.append(n)
        else:
            unknown.append(n)
    if unknown:
        raise SystemExit(f"members of the towers of {ufo} with no CP parity: {unknown}")
    return o, e


def main(argv) -> int:
    if "--check" in argv:
        return 1 if report_disagreements() else 0
    cp = table()
    print(f"CP parity of the {len(cp)} operators:", dict(collections.Counter(cp.values())))
    odd, even = coefficient_sets()
    print(f"coefficients in blocks that are uniformly CP odd: {len(odd)}, "
          f"uniformly CP even: {len(even)}")
    if "--compare" in argv:
        d = collections.Counter()
        ops = _operators()
        for op in ops:
            if op.hc_mode == "complex":
                continue
            if dual_count(op) != cp[op.name]:
                d[op.cls] += 1
        print(f"operators where dual counting disagrees with the derivation: {sum(d.values())} "
              f"of {sum(1 for op in ops if op.hc_mode != 'complex')}")
        print("  by class:", dict(sorted(d.items())))
    if "--json" in argv:
        json.dump(cp, open(argv[argv.index("--json") + 1], "w"), indent=1)
    return 1 if report_disagreements() else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
