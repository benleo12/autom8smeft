#!/usr/bin/env python3
"""The complete class-by-process grid, as one table.

    examples/studies/table_appendix.py > paper/tables/grid.tex

One grid takes the place of twelve per-process tables, which would repeat the class column and
the derived W mass in every row, although the W mass a class derives depends on which
coefficients are on and not at all on the process.  Rows are the 21 classes, columns the twelve
processes, and each cell is the dimension-eight interference in units of 1e-4 of that process's
Standard-Model rate at Lambda = 3 TeV, brought there from the Lambda recorded in each row by the
reader of table_master.py.  A dash is no diagram, so the pattern of dashes shows which classes
reach which process.

The absolute cross sections, the Monte Carlo errors and the squared terms are in each study's
results.tsv in the repository.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from table_master import at_paper_scale  # noqa: E402

# (study, process, column head).  Order: the four body processes first, then the rest.
PROCS = [
    ("diboson",     "p p > w+ w-",         r"$W^+W^-$"),
    ("diboson",     "p p > w+ z",          r"$W^+Z$"),
    ("diboson",     "p p > w- z",          r"$W^-Z$"),
    ("diboson",     "p p > z z",           r"$ZZ$"),
    ("triboson",    "p p > w+ w- w+",      r"$W^+W^-W^+$"),
    ("triboson",    "p p > w+ w- w-",      r"$W^+W^-W^-$"),
    ("triboson",    "p p > w+ w- z",       r"$W^+W^-Z$"),
    ("triboson",    "p p > w+ z z",        r"$W^+ZZ$"),
    ("triboson",    "p p > z z z",         r"$ZZZ$"),
    ("vbf_dihiggs", "p p > h h j j QCD=0", r"$HHjj$"),
    ("drellyan",    "p p > e+ e-",         r"$e^+e^-$"),
    ("drellyan",    "p p > e+ e- a",       r"$e^+e^-\gamma$"),
]

CLASSES = {1: "X^4", 2: "H^8", 3: "H^6D^2", 4: "H^4D^4", 5: "X^3H^2", 6: "X^2H^4",
           7: "X^2H^2D^2", 8: "XH^4D^2", 9: "psi^2X^2H", 10: "psi^2XH^3", 11: "psi^2H^2D^3",
           12: "psi^2H^5", 13: "psi^2H^4D", 14: "psi^2X^2D", 15: "psi^2XH^2D",
           16: "psi^2XHD^2", 17: "psi^2H^3D^2", 18: "psi^4H^2", 19: "psi^4X",
           20: "psi^4HD", 21: "psi^4D^2"}

INT = "NP^2==2"
UNIT = 1e-4           # the interference is printed in units of 1e-4 of the Standard Model


def read(study):
    out = {}
    with open(os.path.join(HERE, study, "results.tsv")) as fh:
        fh.readline()
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 6:
                continue
            key = (f[0].strip(), f[1], f[2])
            try:
                v = at_paper_scale(f[2], float(f[3]), float(f[4]), f[7] if len(f) > 7 else "",
                                   f"{study}: {f[0].strip()} {f[1]}")
            except ValueError:
                # keep the WORD, not just the absence of a number: "NO_DIAGRAMS" and
                # "NOT_INTEGRATED" mean opposite things and a table that renders both as a dash
                # tells the reader a class is absent when it was never run
                v = (f[3], None)
            # A process run twice keeps its first entry, so a later pass, such as one that
            # reports NO_DIAGRAMS, cannot overwrite a measured row.
            if key not in out or out[key][0] is None:
                out[key] = v
    return out


def sm_of(data, study, proc):
    v = [x for (p, m, o), x in data[study].items()
         if p == proc and o == "NP=0" and isinstance(x[0], float)]
    return v[0][0] if v else None


def cell(sig, err, sm, square=None):
    """One entry, on a three-way encoding that makes the shape of the table readable at a glance:
    a dash where the class produces no diagram, an open circle where it produces one whose
    interference is below 1e-6 of the Standard Model at Lambda = 3 TeV, and otherwise the
    number, in units of 1e-4 of the Standard Model at 3 TeV.  Parentheses mark a Monte Carlo error above a tenth of the entry.  Writing
    the negligible entries out as numbers instead buries the pattern of dashes, which is the result."""
    if sig is None or not sm:
        return "--"
    if isinstance(sig, str):
        if sig == "ZERO":
            return r"$\circ$"            # diagrams exist and the interference integrates to zero
        if sig == "NOT_INTEGRATED":
            return r"$\dagger$"
        # no interference but a square: the class reaches the process through a channel with
        # no tree-level Standard-Model amplitude, which is not the same as not reaching it
        return r"$\ast$" if isinstance(square, float) else "--"
    pct = sig / sm / UNIT
    if abs(pct) < 0.005:
        return r"$\circ$"
    t = f"{pct:+.0f}" if abs(pct) >= 100 else f"{pct:+.1f}" if abs(pct) >= 10 else f"{pct:+.2f}"
    return f"$({t})$" if (err and abs(err / sig) > 0.1) else f"${t}$"


# The rows the text of the paper discusses, shaded and with the class in bold so a reader can
# find them: psi^2X^2D, X^2H^2D^2 and psi^4D^2 set Lambda_min in diboson, VBF and Drell-Yan
# (the energy-growth subsection), and X^4 carries the asterisk discussion and the +13.3% in
# W+W-W+ (the subsection on which classes contribute).  Keep this set in step with the phenomenology section of the paper.
HIGHLIGHT = {1, 7, 14, 21}


def label(c):
    """Row number and class, bold and on a shaded row when the text discusses the class."""
    name = CLASSES[c].replace("psi", "\\psi")
    if c in HIGHLIGHT:
        return "\\rowcolor{black!8}\\textbf{" + str(c) + "} & $\\boldsymbol{" + name + "}$"
    return str(c) + " & $" + name + "$"


def main():
    data = {s: read(s) for s in {p[0] for p in PROCS}}
    sm = [sm_of(data, s, p) for s, p, _ in PROCS]

    n = len(PROCS)
    out = [r"\begin{table}[!htbp]", r"\centering", r"\scriptsize",
           r"\setlength{\tabcolsep}{2.6pt}",
           # fourteen columns do not fit at any readable tabcolsep, and shrinking the type until
           # they do makes the numbers unreadable; scale the whole box instead
           r"\resizebox{\textwidth}{!}{%",
           r"\begin{tabular}{@{}r l " + "r" * n + r"@{}}", r"\toprule",
           r" & class & " + " & ".join(h for _, _, h in PROCS) + r" \\",
           r"\cmidrule(lr){3-" + str(2 + n) + r"}",
           r" & $\sigma_{\rm SM}$ [pb] & "
           + " & ".join(("--" if x is None else
                         (f"${x:.3g}$" if x >= 1e-3 else
                          "$" + f"{x:.1e}".split("e")[0] + r"\!\times\!10^{"
                          + str(int(f"{x:.1e}".split("e")[1])) + "}$"))
                        for x in sm) + r" \\",
           r"\midrule"]
    for c in sorted(CLASSES):
        cells = []
        for (study, proc, _), s0 in zip(PROCS, sm):
            sig, err = data[study].get((proc, f"dim8_is-cls{c}", INT), (None, None))
            sq = data[study].get((proc, f"dim8_is-cls{c}", "NP<=2 NP^2==4"), (None, None))[0]
            cells.append(cell(sig, err, s0, sq))
        out.append(label(c) + " & " + " & ".join(cells) + r" \\")
    out += [r"\bottomrule", r"\end{tabular}}",
            r"\caption{The term \MG\ returns at \code{NP\^{}2==2}, which excludes the $W$-mass bracket of \cref{eq:np0}, for every class in every process of "
            r"\cref{sec:pheno}, in units of $10^{-4}$ of that process's Standard-Model rate, at "
            r"$13.6$~TeV, $\Lambda = 3$~TeV and every coefficient of the class at one. A dash "
            r"is no diagram rather than a small number, and the pattern of dashes follows from the "
            r"number of legs of \cref{eq:legs} and the field content of the vertices, "
            r"as \cref{sec:routes} explains. An asterisk is a class that reaches the process only through a channel with no tree-level Standard-Model amplitude, so it has a square and no interference. An open circle is a class that does produce a "
            r"diagram but interferes below $10^{-6}$ of the Standard-Model rate, a dagger one that produces "
            r"diagrams but was not run in these studies, and "
            r"parentheses mark a Monte Carlo error above a tenth of the entry. "
            r"The Drell-Yan processes carry $m_{ee}>200$~GeV, the photon channel additionally "
            r"$p_T^\gamma>20$~GeV and $\Delta R(\gamma,\ell)>0.4$, and $HHjj$ is generated with "
            r"$\mathrm{QCD}=0$ and $p_T^j>25$~GeV, $|\eta_j|<5$, $m_{jj}>400$~GeV. Absolute cross "
            r"sections, Monte Carlo errors and the squared terms are in each study's "
            r"\code{results.tsv}.}",
            r"\label{tab:grid}", r"\end{table}"]
    print("\n".join(out))


if __name__ == "__main__":
    main()
