"""
dim8auto.gen.emit_flavour
=========================

The flavour structures of the fermionic operators in the FeynRules model.

A fermionic operator Q is built once with a general coefficient: a complex tensor in its flavour
indices, in the order of ``op.gens``, the placeholder z8F2 or z8F4 by their number.  The placeholders
are shared, since a block holds one operator.  Its block is

    complex coefficient (Murphy's "+ h.c."):   z8F Q + h.c.
    real coefficient (Q Hermitian):            (z8F Q + h.c.)/2

so that it is Hermitian for any value of the tensor, and its vertices are cached in that form.  They
hold the operator with any flavour structure.  When the UFO is written (validate/fr_writeufo.wls),
the placeholder is replaced by the sum of the operator's flavour structures under U(3)^5 with the
Yukawa matrices as spurions, build/mfv_structures.json from validate/flavour_rank.py:

    z8F[p,r,...] -> sum over structures S of  coef_S T^S[p,r,...]

T^S is a product of one factor per fermion bilinear, a Kronecker delta or a chain of Yukawa matrices.
The chains are the internal matrix parameters mfv<barred species><species><insertion> below.  A
structure keeps the parts that are independent, the part "re" with a real coefficient and the part
"im" with i times one, so coef_S is c, i c_Im or c_Re + i c_Im.  A real coefficient then multiplies
(T Q + (T Q)^dag)/2, which is T Q when T Q is Hermitian.

The structure each operator has had so far (gen/emit_fr.py, mfv_structure) keeps the operator's own
coefficient, so that every card written for the models before stays valid.  The others take new
coefficients, in the block DIM8F, named after the operator's coefficient:

    <wc>F<insertions>      two fermions: U, D or E, one Y Y^dag insertion of that kind
    <wc>F[x]<a><b>         four fermions: the insertion on each bilinear (0 for none), the bilinears in
                           the order of their barred fields, x when they pair the fields across the
                           bilinears as written

with Re and Im appended for the parts of a complex coefficient, and Im alone for the part "im" of a
real one.
"""

from __future__ import annotations

import itertools
import json
import os
from typing import Dict, List, Tuple

from dsl import Operator, Psi

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STRUCTURES = os.path.join(ROOT, "build", "mfv_structures.json")
BLOCK = "DIM8F"

# The Yukawa matrices of the base model, in the basis of its doublets: Y_u = yu and Y_e = yl, diagonal,
# and Y_d = CKM yd, since the down component of the quark doublet is CKM d.  Each is a product of
# elementary matrices, with ("name", True) for the conjugate transpose.
YUKAWA = {"Yu": [("yu", False)], "Yd": [("CKM", False), ("yd", False)], "Ye": [("yl", False)]}
# The base model sets the entries of yu, yd and yl off the diagonal to zero in Definitions, which FeynRules
# applies to the Lagrangian but not to the value of a parameter: an entry such as yd[1,2] in the value of a
# chain would stay in the UFO as yd(1,2), which neither MadGraph nor Python can evaluate.  So the terms
# that hold one are left out of the chains, and an element left with none is 0.
DIAGONAL = {"yu", "yd", "yl"}

# The chain that joins a barred field of the first species to a field of the second, for each insertion,
# as a product of Yukawa matrices ("Yu+" the conjugate transpose), in the convention of
# validate/flavour_rank.py (CHAINS): the bilinear is psibar_a M[a,b] chi_b.  A chain between two fields
# of one species without an insertion is the Kronecker delta.  The reversed pairs (u q, d q, e l, d u) are
# the conjugate transposes of these.
CHAINS = {
    ("q", "q", "U"): ["Yu", "Yu+"],
    ("q", "q", "D"): ["Yd", "Yd+"],
    ("u", "u", "U"): ["Yu+", "Yu"],
    ("d", "d", "D"): ["Yd+", "Yd"],
    ("l", "l", "E"): ["Ye", "Ye+"],
    ("e", "e", "E"): ["Ye+", "Ye"],
    ("q", "u", ""): ["Yu"],
    ("q", "u", "U"): ["Yu", "Yu+", "Yu"],
    ("q", "u", "D"): ["Yd", "Yd+", "Yu"],
    ("q", "d", ""): ["Yd"],
    ("q", "d", "U"): ["Yu", "Yu+", "Yd"],
    ("q", "d", "D"): ["Yd", "Yd+", "Yd"],
    ("l", "e", ""): ["Ye"],
    ("l", "e", "E"): ["Ye", "Ye+", "Ye"],
    ("u", "d", ""): ["Yu+", "Yd"],
    ("u", "d", "U"): ["Yu+", "Yu", "Yu+", "Yd"],
    ("u", "d", "D"): ["Yu+", "Yd", "Yd+", "Yd"],
}


def matrix_name(key: Tuple[str, str, str]) -> str:
    return "mfv" + "".join(key)


def _elementary(chain: List[str]) -> List[Tuple[str, bool]]:
    """The chain as a product of the base model's matrices."""
    out = []
    for y in chain:
        if y.endswith("+"):
            out.extend((n, not c) for n, c in reversed(YUKAWA[y[:-1]]))
        else:
            out.extend(YUKAWA[y])
    return out


def _entry(chain: List[str], i: int, j: int) -> str:
    """Element i, j of the chain, written out as a sum over the summed generations."""
    el = _elementary(chain)
    terms = []
    for ks in itertools.product((1, 2, 3), repeat=len(el) - 1):
        idx = (i,) + ks + (j,)
        if any(n in DIAGONAL and idx[m] != idx[m + 1] for m, (n, _) in enumerate(el)):
            continue
        terms.append(" ".join(f"Conjugate[{n}[{idx[m + 1]},{idx[m]}]]" if c else f"{n}[{idx[m]},{idx[m + 1]}]"
                              for m, (n, c) in enumerate(el)))
    return " + ".join(terms) or "0"


def emit_matrices() -> str:
    """The chains as internal parameters.  Each carries QED order one per Yukawa matrix, as yu, yd and yl
    do, so that a coupling counts its Yukawa matrices as the structures with the lowest number of them
    always have."""
    out = []
    for key, chain in CHAINS.items():
        n = matrix_name(key)
        vals = ",\n      ".join(f"{n}[{i},{j}] -> {_entry(chain, i, j)}" for i in (1, 2, 3) for j in (1, 2, 3))
        desc = " ".join(y.replace("+", "^dag") for y in chain)
        out.append(f"""  {n} == {{ ParameterType -> Internal, ComplexParameter -> True,
    Indices -> {{Index[Generation], Index[Generation]}}, InteractionOrder -> {{QED, {len(chain)}}},
    Value -> {{{vals}}},
    Description -> "MFV chain {desc} ({key[0]}bar to {key[1]})" }}""")
    return ",\n".join(out)


def chain(barred: str, other: str, label: str, a: str, b: str, conj: bool = False) -> str:
    """Element a, b of the chain from a barred field of one species to a field of another, or of its
    complex conjugate."""
    if barred == other and label == "":
        return f"IndexDelta[{a},{b}]"
    if (barred, other, label) in CHAINS:
        m = f"{matrix_name((barred, other, label))}[{a},{b}]"
        return f"Conjugate[{m}]" if conj else m
    m = f"{matrix_name((other, barred, label))}[{b},{a}]"
    return m if conj else f"Conjugate[{m}]"


def load_structures(path: str = STRUCTURES) -> Dict[str, list]:
    return json.load(open(path)) if os.path.exists(path) else {}


def placeholder(op: Operator) -> str:
    """The general coefficient of an operator's block.  One per number of flavour indices, declared once
    (FeynRules processes every component of a declared tensor as it loads a model, which for one tensor
    per operator took minutes), and replaced block by block."""
    return f"z8F{len(op.gens)}"


def _bars(op: Operator) -> Dict[str, bool]:
    return {f.gen: f.bar for f in op.terms[0].factors if isinstance(f, Psi)}


def tag(op: Operator, s: dict) -> str:
    """The suffix that names a structure after the operator's coefficient ('' for the structure the
    models have carried so far)."""
    if s["now"]:
        return ""
    labels = s["insertions"]
    if len(labels) == 1:
        assert labels[0], (op.name, s)
        return "F" + labels[0]
    bar = _bars(op)
    written = {(a, b) if bar[a] else (b, a) for a, b in op.flavor_pairs}
    crossed = {tuple(p) for p in s["pairing"]} != written
    return "F" + ("x" if crossed else "") + "".join(l or "0" for l in labels)


def eta(op: Operator) -> str:
    """The CP parity of the part "re" of a structure: that of the operator, or of the real part of its
    coefficient.  With real Yukawa and CKM matrices, CP takes T Q to its conjugate, so the part "re" has
    the parity of the operator and the part "im" the opposite one."""
    return op.cp.split(",")[0].replace("Re ", "").strip()


def structure_parameters(op: Operator, structures: list) -> List[dict]:
    """The coefficients of an operator's structures: for each structure its name, coefficient expression,
    the external parameters it introduces (name, part, CP parity) and a description."""
    flip = {"even": "odd", "odd": "even"}
    out = []
    complex_parent = op.hc_mode == "complex"
    for s in structures:
        t = tag(op, s)
        base = op.wc + t
        if s["now"]:
            assert s["parts"] == (["re", "im"] if complex_parent else ["re"]), (op.name, s)
            coef, ext = op.wc, []          # the operator's own coefficient, declared by emit_parameters
        else:
            ext = []
            for part in s["parts"]:
                name = base + ("Re" if part == "re" else "Im") if (complex_parent or len(s["parts"]) == 2) else \
                    (base if part == "re" else base + "Im")
                ext.append((name, part, eta(op) if part == "re" else flip[eta(op)]))
            coef = " + ".join(n if p == "re" else f"I {n}" for n, p, _ in ext)
        conj = op.wc if s["now"] and not complex_parent else (
            f"Conjugate[{op.wc}]" if s["now"] else " + ".join(n if p == "re" else f"(-I) {n}" for n, p, _ in ext))
        out.append(dict(structure=s, tag=t, coef=coef, conj=conj, externals=ext, description=describe(op, s)))
    return out


def describe(op: Operator, s: dict) -> str:
    """The flavour tensor in words, for the parameter card: delta or the chain on each bilinear."""
    parts = []
    for (a, b), lab, (x, y) in zip(s["pairing"], s["insertions"], s["species"]):
        if x == y and lab == "":
            parts.append(f"delta_{a}{b}")
        elif (x, y, lab) in CHAINS:
            parts.append("(" + " ".join(c.replace("+", "^dag") for c in CHAINS[(x, y, lab)]) + f")_{a}{b}")
        else:
            parts.append("(" + " ".join(c.replace("+", "^dag") for c in CHAINS[(y, x, lab)]) + f")^dag_{a}{b}")
    return " ".join(parts)


def tensor(op: Operator, s: dict, conj: bool = False) -> str:
    """T^S in the pattern names z8w1, z8w2, ... of the placeholder's indices (the order of op.gens)."""
    pos = {g: f"z8w{k + 1}" for k, g in enumerate(op.gens)}
    return " ".join(chain(x, y, lab, pos[a], pos[b], conj)
                    for (a, b), lab, (x, y) in zip(s["pairing"], s["insertions"], s["species"]))


def yukawa_term(op: Operator, structures: list, a: str, b: str) -> str:
    """The flavour matrix of a two-fermion operator, element a, b: the sum over its structures of coef_S
    T^S[a, b].  The base model adds it, times v^4/(4 Lambda^4), to the Yukawa matrix of the same fields,
    which keeps every fermion mass at its input (gen/input_scheme.py)."""
    terms = []
    for p in structure_parameters(op, structures):
        (x, y), lab = p["structure"]["species"][0], p["structure"]["insertions"][0]
        terms.append(f"({p['coef']}) {chain(x, y, lab, a, b)}")
    return " + ".join(terms)


def emit_rules(ops: List[Operator], structures: Dict[str, list], blocks: Dict[str, str]) -> str:
    """The replacement of the placeholder of each block by its operator's structures, for
    validate/fr_writeufo.wls, keyed by block.  The rule for the conjugate comes first, so that
    Conjugate[z8F4[...]] is replaced as a whole."""
    lines = []
    for op in ops:
        if op.name not in structures:
            continue
        pars = structure_parameters(op, structures[op.name])
        pat = ", ".join(f"z8w{k + 1}_" for k in range(len(op.gens)))
        ph = placeholder(op)
        direct = " +\n    ".join(f"({p['coef']}) {tensor(op, p['structure'])}" for p in pars)
        conj = " +\n    ".join(f"({p['conj']}) {tensor(op, p['structure'], conj=True)}" for p in pars)
        lines.append(f"(* {op.name} *)\n\"{blocks[op.name]}\" -> Dispatch[{{\nConjugate[{ph}[{pat}]] :> (\n    {conj}),\n"
                     f"{ph}[{pat}] :> (\n    {direct})}}]")
    phs = sorted({placeholder(o) for o in ops if o.name in structures})
    return ("(* generated by dim8auto (gen/emit_flavour.py): the flavour structures of every fermionic operator,\n"
            "   replacing the general coefficient of its block in the cached vertices when the UFO is written *)\n"
            "z8FlavourRules = <|\n" + ",\n".join(lines) + "\n|>;\n"
            f"z8FlavourPlaceholders = {{{', '.join(phs)}}};\n")


def emit_placeholders(ops: List[Operator], structures: Dict[str, list]) -> str:
    """The placeholders as complex tensor parameters, for the workers only: they never reach a UFO."""
    ns = sorted({len(o.gens) for o in ops if o.name in structures})
    decl = [f"""  z8F{n} == {{ ParameterType -> Internal, ComplexParameter -> True,
    Indices -> {{{', '.join(['Index[Generation]'] * n)}}}, Description -> "general flavour coefficient of an operator with {n} fermions" }}"""
            for n in ns]
    return ("(* generated by dim8auto (gen/emit_flavour.py): the general flavour coefficients of the fermionic\n"
            "   operators.  Loaded by validate/fr_worker.wls beside gen.fr, never by the UFO writer. *)\n"
            "M$Parameters = {\n" + ",\n".join(decl) + "\n};\n")


def emit_parameters(ops: List[Operator], structures: Dict[str, list], block: str = BLOCK, np: int = 2,
                    chains: bool = True) -> Tuple[str, List[dict]]:
    """The coefficients of the structures each operator has besides its own, in the block DIM8F, and the
    chains.  Returns the M$Parameters entries and a table of the coefficients.  The towers of gen/towers.py
    take a block and an order of their own, and leave the chains to the dimension-eight file."""
    out, table, n = [], [], 1
    for op in ops:
        if op.name not in structures:
            continue
        for p in structure_parameters(op, structures[op.name]):
            for name, part, cp in p["externals"]:
                out.append(f"""  {name} == {{ ParameterType -> External, BlockName -> {block}, OrderBlock -> {n},
    Value -> 0, InteractionOrder -> {{NP,{np}}}, Description -> "{'Re' if part == 're' else 'Im'} {op.name.replace(chr(92) + 'dagger', 'dag').replace(chr(92), '')} {p['description']}" }}""")
                table.append(dict(name=name, block=block, order=n, op=op.name, wc=op.wc, part=part, cp=cp,
                                  order_in_yukawa=p["structure"]["order"], structure=p["description"]))
                n += 1
    return ",\n".join(out + ([emit_matrices()] if chains else [])), table
