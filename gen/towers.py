"""The operators above dimension eight that reach the vertices with at most three legs: the geoSMEFT towers.

In the default basis the dimension-eight operators with a vertex of at most three legs are those of the classes
H^8, H^6D^2, X^3H^2, X^2H^4, XH^4D^2, psi^2XH^3, psi^2H^5 and psi^2H^4D (tests/test_geo_basis.py), and they make up
the field-space connections of the geometric SMEFT at this order (arXiv:2001.01453, arXiv:2306.00053).  The number
of operators in each connection stops growing at dimension eight, with one exception: the connection k^A_IJ of
(D phi)^I (D phi)^J W^A gains one operator at dimension ten, and with it its dual (Table 1 of arXiv:2001.01453).
The operators of dimension d = 8 + 2k that reach the two- and three-point vertices are therefore

    (H^dag H)^k Q                     for every dimension-eight operator Q of those classes,
    (H^dag H)^(k-1) Q_{WH^6D^2}^{(5)}  and the same with Q^{(6)}, for k >= 1,

    Q_{WH^6D^2}^{(5)} = i (H^dag tau^I H)(H^dag tau^J H)(D_mu H^dag tau^I D_nu H) W^{J mu nu}   (Q_{HDHW,3} of 2001.01453)
    Q_{WH^6D^2}^{(6)} = the same with the dual field strength.

Multiplying an operator by (H^dag H)^k multiplies its connection by (phi^2/2)^k, which keeps the operators
independent and of connection form, so at every order these span the connections that the operators of that
dimension can give.  Q^{(5)} and Q^{(6)} continue the numbering of Q_{WH^4D^2}^{(1)-(4)}, which pair the same
SU(2) contractions with W and with its dual: Q^{(5)} is CP even and Q^{(6)} CP odd.

Names.  The member of dimension d of the tower of Q carries the coefficient c<d><label>, with <label> the
coefficient of Q without its "c8": c10H6x1 multiplies (H^dag H) Q_{H^6}^{(1)} and c12leH5 multiplies
(H^dag H)^2 Q_{leH^5}.  The two new towers are c<d>WH4D2x5 and c<d>WH4D2x6.  A fermionic member keeps the flavour
structures of its dimension-eight operator, with coefficients named after its own (gen/emit_flavour.py).

The four-lepton operators that reach muon decay at these orders have four legs, so they enter only the input
relations (gen/derive_geo.py) and are not listed here.
"""

from __future__ import annotations

import os
import sys
from dataclasses import replace
from fractions import Fraction
from typing import Dict, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import basis  # noqa: E402
from dsl import C, FS, H, Operator, Tensor, Term  # noqa: E402
from operators import OPS  # noqa: E402

# the classes whose operators are connections, in the numbering of the Murphy basis (tests/test_geo_basis.py)
CONNECTIONS = (2, 3, 5, 6, 8, 10, 12, 13)


def connection_operators() -> List[Operator]:
    """The dimension-eight operators of the default basis whose vertices with at most three legs are those of
    their connections, in the order of the encoding."""
    return [o for o in basis.ops(OPS, "geo") if o.cls in CONNECTIONS]


def _hdagh(k: int, tag: str) -> tuple:
    """(H^dag H)^k as factors, with SU(2) indices of their own."""
    out = ()
    for i in range(k):
        j = f"zt{tag}{i}"
        out += (H(j=j, dag=True), H(j=j, dag=False))
    return out


def _power(k: int) -> str:
    return "(H^\\dagger H)" + (f"^{k}" if k > 1 else "")


def times_hdagh(op: Operator, k: int) -> Operator:
    """(H^dag H)^k op, the member of dimension d + 2k of the tower of op, an operator of dimension d."""
    d = dimension(op)
    assert k >= 1 and op.wc.startswith(f"c{d}"), (op.name, k)
    terms = [Term(t.coeff, _hdagh(k, f"{n}x") + t.factors) for n, t in enumerate(op.terms)]
    return replace(op, name=f"{_power(k)} {op.name}", wc=f"c{d + 2 * k}{op.wc[len(str(d)) + 1:]}", terms=terms,
                   notes=f"{_power(k)} times {op.name}")


def _kij(dual: bool) -> Operator:
    """Q_{WH^6D^2}^{(5)} (dual=False) or Q^{(6)}: i (H^dag tau^I H)(H^dag tau^J H)(D_mu H^dag tau^I D_nu H) W^{J mu nu}."""
    f = (H(j="a1", dag=True), Tensor(kind="tau", idx=("I", "a1", "a2")), H(j="a2"),
         H(j="a3", dag=True), Tensor(kind="tau", idx=("J", "a3", "a4")), H(j="a4"),
         H(j="a5", dag=True, derivs=("\\mu",)), Tensor(kind="tau", idx=("I", "a5", "a6")), H(j="a6", derivs=("\\nu",)),
         FS(group="W", mu="\\mu", nu="\\nu", adj="J", dual=dual))
    n = 6 if dual else 5
    return Operator(name=f"Q_{{WH^6D^2}}^{{({n})}}", wc=f"c10WH4D2x{n}", terms=[Term(C(Fraction(0), Fraction(1)), f)],
                    cls=8, hermitian=True, hc_mode="real", cp="odd" if dual else "even",
                    notes="Q_{HDHW,3} of arXiv:2001.01453" + (", dual field strength" if dual else ""))


NEW_AT_TEN = (_kij(False), _kij(True))


def tower(d: int) -> List[Operator]:
    """The operators of dimension d (10, 12, ...) that reach the vertices with at most three legs."""
    assert d >= 10 and d % 2 == 0, d
    k = (d - 8) // 2
    out = [times_hdagh(o, k) for o in connection_operators()]
    out += [o if d == 10 else times_hdagh(o, k - 1) for o in NEW_AT_TEN]
    return out


def towers(n: int) -> List[Operator]:
    """Every tower operator through order 1/Lambda^(2n), that is through dimension 2n + 4, by dimension."""
    return [o for d in range(10, 2 * n + 5, 2) for o in tower(d)]


def structures(ops: List[Operator], dim8: Dict[str, list]) -> Dict[str, list]:
    """The flavour structures of the tower operators, keyed by name as build/mfv_structures.json keys those of
    dimension eight: each member has those of its dimension-eight operator."""
    by_wc = {o.wc[2:]: o.name for o in connection_operators()}
    out = {}
    for o in ops:
        base = by_wc.get(o.wc[len(str(dimension(o))) + 1:])
        if base in dim8:
            out[o.name] = dim8[base]
    return out


def dimension(op: Operator) -> int:
    d = op.mass_dimension()
    assert d.denominator == 1, (op.name, d)
    return int(d)


# The blocks of the connection operators in the model of order n.  Each is truncated, once its indices are
# expanded, by z8geoTrunc[L, p] with p its order in 1/Lambda^2, which the base of that model defines
# (gen/input_scheme.py): it keeps the corrections of the couplings, the vev and the fields to order n - p, so
# that every vertex the block gives is complete to 1/Lambda^(2n).  The base also defines z8vT, the corrected
# vev as the doublet carries it.  The file is of no use without that base, so it stops the load.
GUARD = ('If[DownValues[z8geoTrunc] === {} || OwnValues[z8vT] === {},\n'
         '  Print["[geo] FATAL: this file needs the base of the model of its order, which defines z8geoTrunc and z8vT"]; '
         'Abort[]];\n')

# The operators whose vacuum piece is a correction to the gluon kinetic term: (H^dag H)^m G G.  As O_HG in the
# dimension-six sector (gen/make_dim6.py), each is written with that piece subtracted, (H^dag H)^m - (z8vT^2/2)^m,
# so that the gluon of the model is canonical and alpha_s is the coupling of the canonical field.  What the
# subtraction removes returns as the rescaling of the gluon inside the blocks (rG of the base).
GLUON_KINETIC = "G2H4x1"


def _subtracted(block: str, op: Operator) -> str:
    """The block of (H^dag H)^m G G with its vacuum piece subtracted."""
    d = dimension(op)
    m = (d - 4) // 2
    head = f"{op.wc}/Lam^{d - 4} (("
    gg = "FS[G,z8mu,z8nu,z8g1] FS[G,z8mu,z8nu,z8g1]"
    assert block.count(head) == 1 and gg in block, (op.name, block[:600])
    return block.replace(head, f"{head}-(z8vT^2/2)^{m} {gg}) + (", 1)


def _truncated(block: str, p: int) -> str:
    """A block of gen/emit_fr.py with its Lagrangian passed through z8geoTrunc at order p."""
    head, tail = block.split("  Return[z8lagH", 1)
    end = "];\n];\n"                       # the bracket of Return, and that of the Module
    assert tail.endswith(end) and tail.count("Return[") == 0, block[-200:]
    return head + "  Return[z8geoTrunc[z8lagH" + tail[:-len(end)] + ", " + str(p) + "]" + end


def emit(n: int):
    """The FeynRules file of the connection operators of the model of order n: the dimension-eight ones again,
    as blocks G8op<i> (their coefficients are declared in gen.fr), and the towers of dimension 10 to 2n + 4 as
    blocks T<d>op<i> with their coefficients in the blocks DIM<d> and DIM<d>F.  Returns (text, index)."""
    import emit_fr
    import emit_flavour as EF
    tw = towers(n)
    emit_fr.MFV_STRUCTURES.update(structures(tw, emit_fr.MFV_STRUCTURES))
    groups = [(8, "G8op", connection_operators())] + [(d, f"T{d}op", [o for o in tw if dimension(o) == d])
                                                       for d in range(10, 2 * n + 5, 2)]
    params, blocks, index = [], [], []
    for d, prefix, ops in groups:
        p = (d - 4) // 2
        if d > 8:
            params.append(emit_fr.emit_parameters(ops, block_name=f"DIM{d}", order_power=p))
            flav = EF.emit_parameters(ops, emit_fr.MFV_STRUCTURES, block=f"DIM{d}F", np=p, chains=False)[0]
            if flav:
                params.append(flav)
        for i, o in enumerate(ops, start=1):
            nm = f"{prefix}{i}"
            entry = dict(block=nm, ops=[o.name], wcs=[o.wc], cls=o.cls, dim=d, hc_mode=o.hc_mode, cp=o.cp)
            if o.name in emit_fr.MFV_STRUCTURES:
                entry["flavour"] = [x for q in EF.structure_parameters(o, emit_fr.MFV_STRUCTURES[o.name])
                                    for x, _, _ in q["externals"]]
            index.append(entry)
            b = emit_fr.emit_block([o], nm, comment=o.name, flavor=emit_fr.FLAVOR)
            if o.wc[len(str(d)) + 1:] == GLUON_KINETIC:
                b = _subtracted(b, o)
            blocks.append(_truncated(b, p))
    txt = ("(* ===== generated by dim8auto (gen/towers.py): the connection operators of the model of order "
           f"{n}, through dimension {2 * n + 4} ===== *)\n"
           + GUARD + "M$Parameters = {\n" + ",\n".join(params) + "\n};\n\n" + "\n".join(blocks)
           + f"\n(* {len(blocks)} blocks *)\n")
    return txt, index


def emit_rules(n: int) -> str:
    """The flavour rules of the blocks of emit(n), for validate/fr_writeufo.wls (DIM8_EXTRA_RULES): the
    rules of gen/emit_flavour.py, joined to those of gen_flavour_rules.m."""
    import emit_fr
    import emit_flavour as EF
    tw = towers(n)
    emit_fr.MFV_STRUCTURES.update(structures(tw, emit_fr.MFV_STRUCTURES))
    ops, blocks = [], {}
    for prefix, group in [("G8op", connection_operators())] + [(f"T{d}op", [o for o in tw if dimension(o) == d])
                                                               for d in range(10, 2 * n + 5, 2)]:
        for i, o in enumerate(group, start=1):
            ops.append(o)
            blocks[o.name] = f"{prefix}{i}"
    txt = EF.emit_rules(ops, emit_fr.MFV_STRUCTURES, blocks)
    a, b = "z8FlavourRules = <|\n", "\n|>;\nz8FlavourPlaceholders = {"
    assert txt.count(a) == 1 and txt.count(b) == 1, txt[-300:]
    txt = txt.replace(a, "z8FlavourRules = Join[z8FlavourRules, <|\n").replace(
        b, "\n|>];\nz8FlavourPlaceholders = Union[z8FlavourPlaceholders, {")
    assert txt.rstrip().endswith("};"), txt[-200:]
    return txt.rstrip()[:-2] + "}];\n"


if __name__ == "__main__":
    import argparse
    import json
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("n", type=int, help="the order: operators through dimension 2n + 4")
    p.add_argument("-o", help="write the FeynRules file here, and its block index beside it (.json)")
    a = p.parse_args()
    ops = towers(a.n)
    for o in ops:
        print(dimension(o), o.cls, o.wc, o.hc_mode, o.cp, o.name)
    print(f"{len(ops)} operators of dimension 10 to {2 * a.n + 4}")
    if a.o:
        txt, index = emit(a.n)
        open(a.o, "w").write(txt)
        stem = a.o.rsplit(".", 1)[0]
        json.dump(index, open(stem + ".json", "w"), indent=1)
        open(stem + "_flavour_rules.m", "w").write(emit_rules(a.n))
        print(f"wrote {a.o}: {len(index)} blocks, with {stem}.json and {stem}_flavour_rules.m")
