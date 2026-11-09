#!/usr/bin/env python3
"""The catalogue tables, generated from the catalogue so that they cannot drift from the model.

    gen/catalogue_table.py [outdir]     (default paper/tables)

Writes three files.

``catalogue_summary.tex`` is one row per class: the number of operators of the Murphy basis, the
number of Lagrangian terms after the ``+ h.c.`` doubling, how the operators split by conjugacy and
how many are CP odd.

``class_powers.tex`` is one row per class: its leading power of lambda at vertex multiplicity four,
five and six from the counting of gen/epower.py.

``catalogue_ops.tex``, written to ``docs/``, is one entry per operator, two entries per printed line:
the operator label, the Wilson coefficient name as it appears in the parameter card, how it
enters the Lagrangian, its CP parity, and a flag for the operators whose leading flavour structure
vanishes (the caption names those of them that have no vertex in the model).  This is the dictionary
a reader needs to set a coefficient, and it is generated from the catalogue so that it always matches
the model.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import dsl  # noqa: E402
import epower                                    # noqa: E402

CLASSES = {1: "X^4", 2: "H^8", 3: "H^6D^2", 4: "H^4D^4", 5: "X^3H^2", 6: "X^2H^4",
           7: "X^2H^2D^2", 8: "XH^4D^2", 9: r"\psi^2X^2H", 10: r"\psi^2XH^3",
           11: r"\psi^2H^2D^3", 12: r"\psi^2H^5", 13: r"\psi^2H^4D", 14: r"\psi^2X^2D",
           15: r"\psi^2XH^2D", 16: r"\psi^2XHD^2", 17: r"\psi^2H^3D^2", 18: r"\psi^4H^2",
           19: r"\psi^4X", 20: r"\psi^4HD", 21: r"\psi^4D^2"}
FIELDS = {k: v for k, v in zip(CLASSES, epower.DIM8_CLASSES.values())}
# named in words in the table and written out in its caption: the third form is wide enough to
# push the two-entries-per-line layout past the margin
WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
         "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen",
         "nineteen", "twenty"]
HOW = {"real": "real", "complex": "complex", "sym": "Herm.\\ part"}


def word(n: int) -> str:
    """A count in words, and in digits past the words, where operators appended to the basis can take it."""
    return WORDS[n] if n < len(WORDS) else str(n)


def latex_label(lbl: str) -> str:
    """'Q_{q^2W^2D}^{(1)}' -> '$Q^{(1)}_{q^2W^2D}$', with psi-type letters left as they are."""
    m = re.match(r"Q_\{(.*?)\}(?:\^\{\((\d+(?:,\d+)*)\)\})?$", lbl)
    if not m:
        return "$" + lbl + "$"
    sub, sup = m.group(1), m.group(2)
    return f"$Q^{{({sup})}}_{{{sub}}}$" if sup else f"$Q_{{{sub}}}$"


def cp_of(entry) -> str:
    """CP parity, from the shared classifier.  See gen/cp_parity.py for why the count is taken
    per term of the encoded operator rather than over the characters of the printed label."""
    import cp_parity
    return cp_parity.table()[entry["label"]]


def cp_cell(entry) -> str:
    """The CP column of the dictionary: the parity for a real coefficient, and for a complex one the
    parity of its real part, written "Re even" or "Re odd"; the imaginary part has the other one."""
    p = cp_of(entry)
    return p.split(",")[0] if p.startswith("Re ") else p


def main(argv) -> int:
    outdir = argv[1] if len(argv) > 1 else os.path.join(ROOT, "paper", "tables")
    os.makedirs(outdir, exist_ok=True)
    # docs/catalogue.json; the second path is read only in a tree that lacks it
    derived = os.path.join(ROOT, "docs", "catalogue.json")
    cat = json.load(open(derived if os.path.exists(derived)
                         else os.path.join(ROOT, "docs", "murphy_parsed.json")))
    # the operators of the basis the models are written in (gen/basis.py): class 11 in one form or the other
    import basis
    cat = [e for e in cat if e.get("basis") in (None, basis.basis())]
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    wc = {o: e["wcs"][i] for e in idx for i, o in enumerate(e["ops"]) if i < len(e["wcs"])}
    for e in idx:                      # a block with several operators shares one coefficient
        for o in e["ops"]:
            wc.setdefault(o, e["wcs"][0])
    # Which operators lose their leading flavour structure, and which of those have no vertex at all, is
    # read off the shipped model rather than listed here: a coefficient that appears in no coupling
    # expression of the UFO has no vertex, and that is checkable.  The dagger marks the operators whose own
    # coefficient (block DIM8) has no coupling, and the caption names those of them whose further flavour
    # structures (block DIM8F, docs/block_index.json) have none either.
    # Complex coefficients reach the card as <name>Re and <name>Im, so both spellings count.
    flav = {o: e.get("flavour", []) for e in idx for o in e["ops"]}
    leadzero, novertex = set(), set()
    cpath = os.path.join(ROOT, "models", basis.model_name("dim8_mw"), "couplings.py")
    if os.path.exists(cpath):
        # the coefficient names in the couplings (c8..., all of them start with c and a digit), read in one
        # pass: the file of a flavour model is 460 MB, and a search of it per operator takes 20 minutes
        names = {m.group() for m in re.finditer(r"\bc\d\w*", open(cpath, errors="replace").read())}

        def used(w):
            w = re.sub(r"(Re|Im)$", "", w)
            return bool({w, w + "Re", w + "Im"} & names)
        for e in cat:
            if e["b_violating"]:
                continue
            w = wc.get(e["label"])
            if w and not ({w, w + "Re", w + "Im"} & names):
                leadzero.add(e["label"])
                if not any(used(f) for f in flav.get(e["label"], [])):
                    novertex.add(e["label"])
    else:                                   # no model built: fall back to the known answer
        leadzero = set(dsl.NO_VERTEX)
        novertex = {o for o in leadzero if not flav.get(o)}

    # ---------------------------------------------------------------- summary
    rows, powers = [], []
    for c in sorted(CLASSES):
        es = [e for e in cat if e["cls"] == c]
        nb = sum(1 for e in es if not e["b_violating"])
        nbv = len(es) - nb
        terms = sum(2 if e["plus_hc"] else 1 for e in es)
        conj = collections.Counter(e["hc_mode"] for e in es)
        odd = sum(1 for e in es if cp_of(e) == "odd")
        cx = sum(1 for e in es if cp_of(e).startswith("Re odd"))
        qp = []
        for n in (4, 5, 6):
            L = epower.leading(*FIELDS[c], n, HD=epower.DIM8_HD[list(epower.DIM8_CLASSES)[c - 1]])
            qp.append("--" if L is epower.NO_LEGS else f"$\\lambda^{{{L.lambdaExp}}}$")
        rows.append(f"{c} & ${CLASSES[c]}$ & {nb} & {nbv} & {terms} & "
                    f"{conj.get('real',0)} & {conj.get('complex',0)} & {conj.get('sym',0)} & "
                    f"{odd} & {cx}" + r" \\")
        powers.append(f"{c} & ${CLASSES[c]}$ & " + " & ".join(qp) + r" \\")
    tot = (sum(1 for e in cat if not e["b_violating"]), sum(1 for e in cat if e["b_violating"]),
           sum(2 if e["plus_hc"] else 1 for e in cat))
    # the caption names the basis that the table counts (gen/basis.py)
    if basis.basis() == "murphy":
        head = (r"The Murphy basis class by class: how many operators and Lagrangian terms each class has, how its "
                r"operators enter the Lagrangian, and how many are CP odd. A term is counted twice when its operator "
                r"enters with its Hermitian conjugate, as in the term count of the Murphy basis. Under ``enters as'', "
                r"the coefficient $C$ is real in $C\,Q$ and in $\tfrac12 C(Q+Q^\dagger)$, the Hermitian part of an "
                r"operator that is Hermitian only up to integration by parts, and complex in $C\,Q+\hc$ (\cref{sec:basis}).")
    else:
        head = (r"Our default basis class by class: how many operators and Lagrangian terms each class has, how its "
                r"operators enter the Lagrangian, and how many are CP odd. The default basis is the Murphy basis with "
                r"the operators of $\psi^2H^2D^3$ replaced (\cref{sec:geo}), and every count other than the way these "
                r"operators enter is the same in both. A term is counted twice when its operator enters with its "
                r"Hermitian conjugate, as in the term count of the Murphy basis. Under ``enters as'', the coefficient "
                r"$C$ is real in $C\,Q$ and in $\tfrac12 C(Q+Q^\dagger)$, and complex in $C\,Q+\hc$ (\cref{sec:basis}). "
                r"The form $\tfrac12 C(Q+Q^\dagger)$ is the Hermitian part of an operator that is Hermitian only up to "
                r"integration by parts. It is the form of fourteen operators of $\psi^2H^2D^3$ in the models in the "
                r"Murphy basis, and no operator of the default basis needs it.")
    with open(os.path.join(outdir, "catalogue_summary.tex"), "w") as fh:
        fh.write(r"""\begin{table}[!htbp]\centering\small
\resizebox{\textwidth}{!}{%
\begin{tabular}{r l rr r rrr rr}
\toprule
 & & \multicolumn{2}{c}{operators} & terms & \multicolumn{3}{c}{enters as} & \multicolumn{2}{c}{CP} \\
\cmidrule(lr){3-4}\cmidrule(lr){6-8}\cmidrule(lr){9-10}
 & class & $\Delta B{=}0$ & $\Delta B{\neq}0$ & & $C\,Q$ & $C\,Q{+}\hc$ & $\tfrac12 C(Q{+}Q^\dagger)$ & odd & Re odd \\
\midrule
""" + "\n".join(rows) + r"""
\midrule
 & total & """ + f"{tot[0]} & {tot[1]} & {tot[2]}" + r""" & & & & & \\
\bottomrule
\end{tabular}}
\caption{""" + head + r""" Under ``CP'', with the parity derived in \cref{sec:basis}, ``odd'' counts the CP-odd operators with a real coefficient and ``Re odd'' the complex coefficients whose real part is CP odd. In every other complex coefficient the imaginary part is CP odd.}
\label{tab:catalogue-summary}
\end{table}
""")
    with open(os.path.join(outdir, "class_powers.tex"), "w") as fh:
        fh.write(r"""\begin{table}[!htbp]\centering\small
\begin{tabular}{r l ccc}
\toprule
 & & \multicolumn{3}{c}{$\lambda$ at $n=$} \\
\cmidrule(lr){3-5}
 & class & 4 & 5 & 6 \\
\midrule
""" + "\n".join(powers) + r"""
\bottomrule
\end{tabular}
\caption{How fast each class grows with energy at four, five and six legs, before any process is chosen. An entry is the power of the class at that number of legs (\cref{eq:counting}), with $(\Lambda, E, v) \sim (\lambda^{-3}, \lambda^{-2}, \lambda^{-1})$, and within a column a smaller power is a larger contribution. The powers follow from the field content of the class and refer to no process. Every dimension-eight contribution to an $n$-point amplitude carries $\lambda^{2n-4+p}$, so only the vacuum insertions $p$ of \cref{eq:counting} distinguish the classes. The entries $\lambda^4$ at four legs, $\lambda^6$ at five and $\lambda^8$ at six all have $p = 0$ and all grow as $E^4/\Lambda^4$ relative to the SM. An added leg raises the power by two when $p = 0$ and by one while $p > 0$, since it then replaces a vacuum insertion. A dash means the class cannot form a vertex with that many legs. In a given process the power of a class can be larger, since the external particles decide which of its vertices can appear (\cref{sec:routes}).}
\label{tab:class-powers}
\end{table}
""")

    # ---------------------------------------------------------------- per-operator dictionary
    def cell(e):
        flag = r"$^{\dagger}$" if e["label"] in leadzero else ""
        flag += r"$^{\ddagger}$" if e.get("redundant_one_generation") else ""
        return (f"{latex_label(e['label'])}{flag} & \\code{{{wc.get(e['label'], '--')}}} & "
                f"{HOW[e['hc_mode']]} & {cp_cell(e)}")
    body = []
    for c in sorted(CLASSES):
        es = [e for e in cat if e["cls"] == c]
        body.append(r"\midrule \multicolumn{8}{l}{\textbf{class " + str(c) + r": $" + CLASSES[c]
                    + r"$}} \\ \midrule")
        for i in range(0, len(es), 2):
            left = cell(es[i])
            right = cell(es[i + 1]) if i + 1 < len(es) else " & & & "
            body.append(left + " & " + right + r" \\")
    # The 734-entry dictionary is machine output and is more useful searchable than printed, so it
    # goes to docs/ beside catalogue.json rather than into the paper.
    opsdir = os.path.join(ROOT, "docs")
    os.makedirs(opsdir, exist_ok=True)
    # the caption counts the daggers it explains: Q_{udWH^2}^{(1,2)} vanish identically, every other
    # flagged operator's leading structure vanishes because its two currents are flavour diagonal and
    # identical, and it names the flagged operators that have no vertex through a further structure either
    n_su2 = sum(1 for o in leadzero if o.startswith("Q_{udWH^2}"))
    n_flav = len(leadzero) - n_su2
    dead = [latex_label(o) for o in sorted(novertex)]
    if not leadzero:
        rest = ""
    elif not dead:
        rest = r"Each of them has vertices through its further flavour structures. "
    elif len(dead) == 1:
        rest = (r"All of them but " + dead[0] + r" have vertices through their further flavour structures, and "
                + dead[0] + r" has no vertex in the model. ")
    else:
        rest = (r"Of them, " + ", ".join(dead[:-1]) + " and " + dead[-1] + r" have no vertex in the model, and "
                r"the others have vertices through their further flavour structures. ")
    # the operators listed are those of the basis of the models (gen/basis.py), as in the summary table
    which = (r"the Murphy basis" if basis.basis() == "murphy" else
             r"our default basis (the Murphy basis with the operators of $\psi^2H^2D^3$ replaced, \cref{sec:geo})")
    with open(os.path.join(opsdir, "catalogue_ops.tex"), "w") as fh:
        fh.write(r"""{\footnotesize\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{l l c c l l c c}
\caption{Every operator of """ + which + r""" with the Wilson coefficient name the model uses, how the operator enters the Lagrangian, and its CP parity. Two entries per line. ``enters as'' says how the operator enters the Lagrangian, as derived in \cref{sec:basis}: real is $C\,Q$ with $C$ real, complex is $C\,Q + \hc$ with $C$ complex, and Herm.\ part is $\tfrac12 C(Q + Q^\dagger)$ with $C$ real, the Hermitian part of an operator that is Hermitian only up to integration by parts. For a complex coefficient the CP column gives the parity of its real part, and the imaginary part has the opposite one. A dagger marks the """ + word(n_su2 + n_flav) + r""" baryon-conserving operators whose leading flavour structure vanishes, """ + ((word(n_su2) + r""" because the $SU(2)$ structure vanishes identically and """ + word(n_flav) + r""" because""") if n_su2 else "because") + r""" each of its currents is flavour diagonal. """ + rest + r"""A double dagger marks the operator that the Murphy basis lists as redundant when there is only one generation of fermions, which has vertices in the model and should be left out of a one-generation fit. A complex coefficient appears in the parameter card as a \code{Re} and an \code{Im} entry. Generated by \code{gen/catalogue\_table.py}.}
\label{tab:catalogue-ops}\\
\toprule
operator & coefficient & enters as & CP & operator & coefficient & enters as & CP \\
\midrule
\endfirsthead
\toprule
operator & coefficient & enters as & CP & operator & coefficient & enters as & CP \\
\midrule
\endhead
\bottomrule
\endfoot
""" + "\n".join(body) + "\n" + r"""\end{longtable}}
""")
    print(f"wrote {outdir}/catalogue_summary.tex and {opsdir}/catalogue_ops.tex "
          f"({len(cat)} operators, {sum(1 for e in cat if e['label'] in leadzero)} flagged, "
          f"{len(novertex)} of them with no vertex)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
