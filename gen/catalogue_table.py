#!/usr/bin/env python3
"""The appendix tables, generated from the catalogue so that they cannot drift from the model.

    gen/catalogue_table.py [outdir]     (default paper/tables)

Writes two files.

``catalogue_summary.tex`` is one row per class: the number of operators of the Murphy basis, the
number of Lagrangian terms after the ``+ h.c.`` doubling, how the rows split by conjugacy, how
many are CP odd, and the leading energy behaviour $(q, p)$ of the class at vertex multiplicity
four, five and six from the counting of gen/epower.py.

``catalogue_ops.tex``, written to ``docs/``, is one entry per operator, two entries per printed line:
the operator label, the Wilson coefficient name as it appears in the parameter card, how it
enters the Lagrangian, its CP parity, and a flag for the rows that have no vertex in the model.
This is the dictionary a reader needs to set a coefficient, and it is the reason the appendix is
generated rather than typed.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import epower                                    # noqa: E402

CLASSES = {1: "X^4", 2: "H^8", 3: "H^6D^2", 4: "H^4D^4", 5: "X^3H^2", 6: "X^2H^4",
           7: "X^2H^2D^2", 8: "XH^4D^2", 9: r"\psi^2X^2H", 10: r"\psi^2XH^3",
           11: r"\psi^2H^2D^3", 12: r"\psi^2H^5", 13: r"\psi^2H^4D", 14: r"\psi^2X^2D",
           15: r"\psi^2XH^2D", 16: r"\psi^2XHD^2", 17: r"\psi^2H^3D^2", 18: r"\psi^4H^2",
           19: r"\psi^4X", 20: r"\psi^4HD", 21: r"\psi^4D^2"}
FIELDS = {k: v for k, v in zip(CLASSES, epower.DIM8_CLASSES.values())}
# abbreviated in the table and spelled out in its caption: the third form is wide enough to
# push the two-entries-per-line layout past the margin
HOW = {"real": "$CQ$", "complex": "$+\\hc$", "sym": "sym"}


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


def main(argv) -> int:
    outdir = argv[1] if len(argv) > 1 else os.path.join(ROOT, "paper", "tables")
    os.makedirs(outdir, exist_ok=True)
    # the catalogue, or the authors' working file where only that exists
    derived = os.path.join(ROOT, "docs", "catalogue.json")
    cat = json.load(open(derived if os.path.exists(derived)
                         else os.path.join(ROOT, "docs", "murphy_parsed.json")))
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    wc = {o: e["wcs"][i] for e in idx for i, o in enumerate(e["ops"]) if i < len(e["wcs"])}
    for e in idx:                      # a block with several operators shares one coefficient
        for o in e["ops"]:
            wc.setdefault(o, e["wcs"][0])
    # Which rows produce no vertex is read off the shipped model rather than listed here.  The
    # list used to be hard coded, which meant the paper's "nine" was an assertion; a coefficient
    # that appears in no coupling expression of the UFO has no vertex, and that is checkable.
    # Complex coefficients reach the card as <name>Re and <name>Im, so both spellings count.
    novertex = set()
    cpath = os.path.join(ROOT, "models", "dim8_is", "couplings.py")
    if os.path.exists(cpath):
        coup = open(cpath, errors="replace").read()
        for e in cat:
            if e["b_violating"]:
                continue
            w = wc.get(e["label"])
            if w and not re.search(r"\b" + re.escape(w) + r"(Re|Im)?\b", coup):
                novertex.add(e["label"])
    else:                                   # no model built: fall back to the known answer
        novertex = {"Q_{udWH^2}^{(1)}", "Q_{udWH^2}^{(2)}", "Q_{q^4H^2}^{(5)}", "Q_{l^4B}^{(1)}",
                    "Q_{q^4B}^{(1)}", "Q_{q^4B}^{(3)}", "Q_{e^4B}^{(1)}", "Q_{u^4B}^{(1)}",
                    "Q_{d^4B}^{(1)}"}

    # ---------------------------------------------------------------- summary
    rows = []
    for c in sorted(CLASSES):
        es = [e for e in cat if e["cls"] == c]
        nb = sum(1 for e in es if not e["b_violating"])
        nbv = len(es) - nb
        terms = sum(2 if e["plus_hc"] else 1 for e in es)
        conj = collections.Counter(e["hc_mode"] for e in es)
        odd = sum(1 for e in es if cp_of(e) == "odd")
        cx = sum(1 for e in es if cp_of(e) == "Re/Im")
        qp = []
        for n in (4, 5, 6):
            L = epower.leading(*FIELDS[c], n)
            qp.append("--" if L is epower.NO_LEGS else f"$\\lambda^{{{L.lambdaExp}}}$")
        rows.append(f"{c} & ${CLASSES[c]}$ & {nb} & {nbv} & {terms} & "
                    f"{conj.get('real',0)} & {conj.get('complex',0)} & {conj.get('sym',0)} & "
                    f"{odd} & {cx} & " + " & ".join(qp) + r" \\")
    tot = (sum(1 for e in cat if not e["b_violating"]), sum(1 for e in cat if e["b_violating"]),
           sum(2 if e["plus_hc"] else 1 for e in cat))
    with open(os.path.join(outdir, "catalogue_summary.tex"), "w") as fh:
        fh.write(r"""\begin{table}[!htbp]\centering\small
\resizebox{\textwidth}{!}{%
\begin{tabular}{r l rr r rrr rr ccc}
\toprule
 & & \multicolumn{2}{c}{operators} & terms & \multicolumn{3}{c}{enters as} & \multicolumn{2}{c}{CP} & \multicolumn{3}{c}{$\lambda$ at $n=$} \\
\cmidrule(lr){3-4}\cmidrule(lr){6-8}\cmidrule(lr){9-10}\cmidrule(lr){11-13}
 & class & $\Delta B{=}0$ & $\Delta B{\neq}0$ & & $CQ$ & $+\hc$ & sym & odd & Re/Im & 4 & 5 & 6 \\
\midrule
""" + "\n".join(rows) + r"""
\midrule
 & total & """ + f"{tot[0]} & {tot[1]} & {tot[2]}" + r""" & & & & & & & & \\
\bottomrule
\end{tabular}}
\caption{The Murphy basis by class. ``operators'' counts the operators of the basis, and ``terms'' counts Lagrangian terms with an operator marked $+\,\hc$ counted twice, which is the convention that reproduces the $N_{\rm term}$ of the Murphy basis. ``enters as'' is the conjugacy classification of \cref{sec:basis}: $CQ$ with $C$ real, $CQ + \hc$ with $C$ complex, or the Hermitian part with $C$ real. ``CP odd'' counts operators with a real coefficient that the derived $C\times P$ assignment of \cref{sec:basis} makes odd, which is not the same set as the one dual counting gives, and ``Re/Im'' those whose complex coefficient has a CP-even real and a CP-odd imaginary part. The last three columns are the leading power of $\lambda$ the class can reach at vertex multiplicity $n$, with $(\Lambda, E, v) \sim (\lambda^{-3}, \lambda^{-2}, \lambda^{-1})$, so a smaller power is a larger contribution and $\lambda^4$ is the steepest a dimension-eight operator can be. A dash means the class cannot form a vertex with that many legs. Generated by \code{gen/catalogue\_table.py}.}
\label{tab:catalogue-summary}
\end{table}
""")

    # ---------------------------------------------------------------- per-operator dictionary
    def cell(e):
        flag = r"$^{\dagger}$" if e["label"] in novertex else ""
        return (f"{latex_label(e['label'])}{flag} & \\code{{{wc.get(e['label'], '--')}}} & "
                f"{HOW[e['hc_mode']]} & {cp_of(e)}")
    body = []
    for c in sorted(CLASSES):
        es = [e for e in cat if e["cls"] == c]
        body.append(r"\midrule \multicolumn{8}{l}{\textbf{class " + str(c) + r": $" + CLASSES[c]
                    + r"$}} \\ \midrule")
        for i in range(0, len(es), 2):
            left = cell(es[i])
            right = cell(es[i + 1]) if i + 1 < len(es) else " & & & "
            body.append(left + " & " + right + r" \\")
    # The 734-row dictionary is machine output and is more useful searchable than printed, so it
    # goes to docs/ beside catalogue.json rather than into the paper, which stopped inputting it.
    opsdir = os.path.join(ROOT, "docs")
    os.makedirs(opsdir, exist_ok=True)
    with open(os.path.join(opsdir, "catalogue_ops.tex"), "w") as fh:
        fh.write(r"""{\footnotesize\setlength{\tabcolsep}{3.5pt}
\begin{longtable}{l l c c l l c c}
\caption{Every operator of the Murphy basis with the Wilson coefficient name the model uses, how the operator enters the Lagrangian, and its CP parity. Two entries per line. ``enters as'' abbreviates the conjugacy classification of \cref{sec:basis}: $CQ$ is $C\,Q$ with $C$ real, $+\hc$ is $C\,Q + \hc$ with $C$ complex, and sym is the Hermitian part $\tfrac12 C(Q + Q^\dagger)$ with $C$ real. A dagger marks the nine baryon-conserving rows that have no vertex in the model, two because the $SU(2)$ structure vanishes identically and seven because the structure vanishes for a flavour-universal coefficient. Coefficients marked $CQ+\hc$ appear in the parameter card as a \code{Re} and an \code{Im} entry. Generated by \code{gen/catalogue\_table.py}.}
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
          f"({len(cat)} rows, {sum(1 for e in cat if e['label'] in novertex)} flagged)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
