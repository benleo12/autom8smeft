#!/usr/bin/env python3
"""The complete class-by-process grid, as one table.

    examples/studies/table_appendix.py > paper/tables/grid.tex

This replaces the twelve per-process tables an earlier version of the paper carried.  Those
repeated the class column twelve times and the derived W mass in every row of every one of them,
which is 252 cells holding at most 21 distinct numbers, since the W mass a class derives depends
on which coefficients are on and not at all on the process.  One grid says the same thing once:
rows are the 21 classes, columns the twelve processes, each cell the dimension-eight interference
as a percentage of that process's Standard-Model rate.  A dash is no diagram, which is the
reachability statement of the counting made visible as the shape of the table.

The absolute cross sections, the Monte Carlo errors and the squared terms are in each study's
results.tsv in the repository, which is the machine-readable form and the one worth reading.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

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
                v = (float(f[3]), float(f[4]))
            except ValueError:
                # keep the WORD, not just the absence of a number: "NO_DIAGRAMS" and
                # "NOT_INTEGRATED" mean opposite things and a table that renders both as a dash
                # tells the reader a class is absent when it was merely never run
                v = (f[3], None)
            # A process run twice (the Drell-Yan photon channel was) keeps the entry that has a
            # number, so a later NO_DIAGRAMS pass cannot overwrite a measured row.
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
    interference is below a hundredth of a per cent of the Standard Model, and otherwise the
    number.  Parentheses mark a Monte Carlo error above a tenth of the entry.  Writing the
    negligible entries out as numbers instead buries the pattern of dashes, which is the result."""
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
    pct = 100 * sig / sm
    if abs(pct) < 0.005:
        return r"$\circ$"
    t = f"{pct:+.0f}" if abs(pct) >= 100 else f"{pct:+.1f}" if abs(pct) >= 10 else f"{pct:+.2f}"
    return f"$({t})$" if (err and abs(err / sig) > 0.1) else f"${t}$"


# The rows the text of the paper discusses, shaded and with the class in bold so a reader can
# find them: psi^2X^2D, X^2H^2D^2 and psi^4D^2 set Lambda_min in diboson, VBF and Drell-Yan
# (the energy-growth subsection), and X^4 carries the asterisk discussion and the +13.3% in
# W+W-W+ (the reachability subsection).  Keep this set in step with paper/sections/pheno.tex.
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
            r"\cref{sec:pheno}, as a percentage of that process's Standard-Model rate, at "
            r"$13.6$~TeV with $\Lambda=1$~TeV and every coefficient of the class at one. A dash "
            r"is no diagram rather than a small number, and the pattern of dashes is the "
            r"reachability prediction of \cref{eq:reach} together with the field-content "
            r"obstruction of \cref{fig:reach}(c). An asterisk is a class that reaches the process only through a channel with no tree-level Standard-Model amplitude, so it has a square and no interference. An open circle is a class that does produce a "
            r"diagram but interferes below a hundredth of a per cent, a dagger one that produces "
            r"diagrams whose cross section was not run because the process was too expensive, and "
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
