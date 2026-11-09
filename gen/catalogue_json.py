#!/usr/bin/env python3
"""The derived catalogue, written from the operator encoding.

    gen/catalogue_json.py [out]     (default docs/catalogue.json)

Everything the shipped code needs to know about an operator without its terms: the label, the Wilson
coefficient name, the block, the class, the basis it belongs to (gen/basis.py: "murphy" or "geo" for the two
forms of class 11, null for the operators common to both), whether it violates baryon number, how it enters
the Lagrangian, its CP parity, its field content, whether the released model has a vertex for it, and
whether its leading flavour structure vanishes.  An operator whose own coefficient (block DIM8) has no
coupling can still have vertices through the coefficients of its further flavour structures (block DIM8F,
listed in docs/block_index.json): of the thirteen whose leading structure vanishes with flavour-diagonal
currents, all but Q_{e^4B}^{(2)} do.
All of it comes from gen/operators.py, apart from the last two items, which are read off the couplings of
models/dim8_mw, or of models/dim8_mw_murphy for an operator of the Murphy basis alone, so that the file
follows a correction to an operator.  ./dim8 build rewrites it, and
./dim8 rebuild once more after the models are released, since a corrected operator can gain or lose
its vertices.  It lets ./dim8 select, ./dim8 series and the appendix generator read the classification
from one small file, without loading the encoding.  The default run also writes the table of
examples/cards/coefficients.md from the same entries.
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import dsl  # noqa: E402

# Operators that the Murphy basis lists as redundant when there is only one generation of fermions
# (the class-20 caption: "The operator below the dashed line is redundant when there is only one
# generation of fermions").  The model gives them vertices like any other operator, so a
# one-generation fit that floats them together with the rest of the basis has a flat direction, and
# the flag says so wherever the operator is listed.
REDUNDANT_ONE_GENERATION = {"Q_{le^3HD}^{(2)}"}


def conjugacy(op) -> str:
    """How the operator conjugates as the Murphy basis prints it.  An operator that is anti-Hermitian
    as printed enters with hc_mode "real" and the factor i in its terms, which its note records, and a
    complex one and one that is Hermitian only up to integration by parts are neither."""
    if op.hc_mode != "real":
        return "complex"
    return "antihermitian" if "factor i inserted" in op.notes else "hermitian"


def rows(ops, couplings=None, previous=None):
    """The entries of the catalogue, one per operator in block order.  couplings is the text of
    models/dim8_mw/couplings.py, or a dict of such texts by basis (gen/basis.py), and previous the entries
    of the file being replaced, whose vertex flags stay when there is no model to read them off."""
    import basis
    import cp_parity
    prev = {e["label"]: e for e in previous or []}
    by_basis = couplings if isinstance(couplings, dict) else {basis.DEFAULT: couplings}
    # the coefficient names in each text (c8..., all of them start with c and a digit), read in one pass: the
    # couplings of a flavour model are 460 MB, and a search of them per operator takes ten minutes
    by_basis = {b: None if t is None else {m.group() for m in re.finditer(r"\bc\d\w*", t)} for b, t in by_basis.items()}
    ipath = os.path.join(ROOT, "docs", "block_index.json")
    flav = {o: e.get("flavour", []) for e in (json.load(open(ipath)) if os.path.exists(ipath) else [])
            for o in e["ops"]}

    def has(w, names):
        # a complex coefficient reaches the couplings as <name>Re and <name>Im, so both spellings count
        w = re.sub(r"(Re|Im)$", "", w)
        return bool({w, w + "Re", w + "Im"} & names)

    def vertex(op, bviol):
        # an operator of one basis alone is looked up in the model of that basis, the others in the default one
        names = by_basis.get(basis.of_wcs([op.wc]) or basis.DEFAULT)
        # Whether the released model has a vertex for the operator: a coefficient that appears in no
        # coupling of models/dim8_mw has none (the same set in dim8_is), which happens only for
        # operators that vanish once their currents are flavour diagonal.  The baryon-number-violating
        # operators are not exported and carry null.
        if bviol:
            return None, None, None
        if names is None:
            old = prev.get(op.name, {})
            return old.get("vertex"), old.get("no_vertex_reason"), old.get("leading_vanishes")
        if {op.wc, op.wc + "Re", op.wc + "Im"} & names:
            return True, None, None
        # an operator appended to the encoding is not in the released model until the next rebuild
        lead = "vanishes with flavour-diagonal currents" if op.name in dsl.NO_VERTEX else "not in the released model"
        # its own coefficient has no coupling, and its further flavour structures may still have vertices
        if any(has(w, names) for w in flav.get(op.name, [])):
            return True, None, lead
        return False, lead, lead

    out = []
    for i, op in enumerate(ops):
        bviol = cp_parity.carries_baryon_number(op)
        vtx, why, lead = vertex(op, bviol)
        # plus_hc counts an operator that the Murphy basis marks + h.c., which an operator with hc_mode
        # "sym" is not: it enters through its Hermitian part because it is Hermitian only up to
        # integration by parts
        out.append(dict(label=op.name, wc=op.wc, block=f"L8op{i + 1}", status="ok",
                        cls=op.cls, basis=basis.of_wcs([op.wc]), b_violating=bviol, plus_hc=op.hc_mode == "complex",
                        hc_mode=op.hc_mode, conjugacy=conjugacy(op), cp=op.cp,
                        n_terms=len(op.terms), fields=op.field_content(), gens=list(op.gens),
                        vertex=vtx, no_vertex_reason=why, leading_vanishes=lead,
                        redundant_one_generation=op.name in REDUNDANT_ONE_GENERATION))
    return out


def coefficients_table(entries) -> str:
    """The text of examples/cards/coefficients.md, the list of the Wilson coefficients for a reader who
    fills a parameter card, one row per operator."""
    head = ["# Wilson coefficients of the dimension-eight model", "",
            "One row per operator block (Q_{...} names as in the Murphy basis, arXiv:2005.00059). Complex",
            "coefficients appear in the parameter card as `<name>Re` and `<name>Im`. Class numbers are Murphy's.",
            "The models hold class 11 in one of two forms (gen/basis.py): the default models the operators marked",
            "`default`, in which every Higgs field carries a derivative, and the models with the suffix `_murphy`",
            "those marked `Murphy`.", "",
            "| block | class | operator | coefficient | type | basis |", "|---|---|---|---|---|---|"]
    names = {"geo": "default", "murphy": "Murphy", None: ""}
    rows = [f"| {e['block']} | {e['cls']} | `{e['label']}` | `{e['wc']}` | {e['hc_mode']} | {names[e.get('basis')]} |"
            for e in entries]
    return "\n".join(head + rows) + "\n"


def main(argv) -> int:
    out = argv[1] if len(argv) > 1 else os.path.join(ROOT, "docs", "catalogue.json")
    import basis
    from operators import OPS
    couplings = {}
    for b in basis.BASES:
        cpath = os.path.join(ROOT, "models", basis.model_name("dim8_mw", b), "couplings.py")
        couplings[b] = open(cpath, errors="replace").read() if os.path.exists(cpath) else None
    previous = json.load(open(out)) if None in couplings.values() and os.path.exists(out) else None
    entries = rows(OPS, couplings, previous)
    # through a temporary file, so that a failed write never leaves a truncated catalogue behind
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out + ".tmp", "w") as fh:
        json.dump(entries, fh, indent=1)
    os.replace(out + ".tmp", out)
    print(f"wrote {out}: {len(entries)} rows")
    if len(argv) <= 1:
        table = os.path.join(ROOT, "examples", "cards", "coefficients.md")
        os.makedirs(os.path.dirname(table), exist_ok=True)
        with open(table + ".tmp", "w") as fh:
            fh.write(coefficients_table(entries))
        os.replace(table + ".tmp", table)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
