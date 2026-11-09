#!/usr/bin/env python3
"""One table for the whole phenomenology section: the 21 classes in four processes.

    examples/studies/table_master.py > paper/tables/master.tex

The per-process tables say what each class does in one process.  This one says what the 21
classes do across four processes at once.  A class with no vertex that fits a diagram of the process
has no diagram at all, and the table shows that as a dash rather than as a small number.  The energy
counting of each class is tabulated separately, in the catalogue summary of the paper.

Columns per process are the interference in units of 1e-4 of the Standard Model and R, the square of
the class over its interference in the sample of that process, both at the paper's scale, Lambda = 3
TeV, and unit coefficients.  The interference carries 1/Lambda^4 and the square 1/Lambda^8, so read()
brings every entry from the Lambda recorded in its settings column to LAM_PAPER (the W-mass bracket is
not a tagged order and is not in these tables).  For a class with no interference the bracketed entry
is the square in units of 1e-4 of the Standard Model.
Pure Python, reads each study's results.tsv.
"""
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))

CLASSES = {1: "X^4", 2: "H^8", 3: "H^6D^2", 4: "H^4D^4", 5: "X^3H^2", 6: "X^2H^4",
           7: "X^2H^2D^2", 8: "XH^4D^2", 9: "psi^2X^2H", 10: "psi^2XH^3", 11: "psi^2H^2D^3",
           12: "psi^2H^5", 13: "psi^2H^4D", 14: "psi^2X^2D", 15: "psi^2XH^2D",
           16: "psi^2XHD^2", 17: "psi^2H^3D^2", 18: "psi^4H^2", 19: "psi^4X",
           20: "psi^4HD", 21: "psi^4D^2"}

# (study, process, short column head).  One representative per study, the one whose class rows
# are complete.
COLS = [("diboson",    "p p > w+ w-",         r"$pp\to W^+W^-$"),
        ("triboson",   "p p > w+ w- w+",      r"$pp\to W^+W^-W^+$"),
        ("vbf_dihiggs","p p > h h j j QCD=0", r"$pp\to HHjj$"),
        ("drellyan",   "p p > e+ e-",         r"$pp\to e^+e^-$")]

INT, SQ = "NP^2==2", "NP<=2 NP^2==4"
POWER = {INT: 4, SQ: 8}   # the power of 1/Lambda that each tagged order carries
LAM_PAPER = 3000.0    # the scale every table and figure of the paper is printed at, in GeV
UNIT = 1e-4           # the interference is printed in units of 1e-4 of the Standard Model


def study_model(d, where):
    """The model a study was run with, read from the model column of its rows ("dim8_mw" for
    "dim8_mw-cls7"), so that the class rows are looked up under the name they were written with.
    A study whose rows come from two models is refused: a merge that mixed schemes would
    otherwise fill a table with whichever rows the lookup happened to name."""
    base = {m.split("-")[0] for (_, m, _) in d}
    if len(base) != 1:
        sys.exit(f"{where}: rows from {len(base)} models ({', '.join(sorted(base))}), expected one")
    return base.pop()


def at_paper_scale(order, sig, err, settings, where):
    """A tagged cross section and its error at LAM_PAPER, from the Lam= of the row's settings."""
    k = POWER.get(order)
    if k is None:
        return sig, err
    m = re.search(r"\bLam=([0-9.eE+-]+)", settings)
    if not m:
        sys.exit(f"{where}: a {order} row with no Lam= in its settings")
    f = (float(m.group(1)) / LAM_PAPER) ** k
    return sig * f, err * f


def read(study):
    """{(process, model, order): (sigma, error)}, sigma None where there was no diagram."""
    out = {}
    with open(os.path.join(HERE, study, "results.tsv")) as fh:
        head = fh.readline()
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) < 6:
                continue
            proc, model, order, sig, err = f[0].strip(), f[1], f[2], f[3], f[4]
            try:
                out[(proc, model, order)] = at_paper_scale(
                    order, float(sig), float(err), f[7] if len(f) > 7 else "", f"{study}: {proc} {model}")
            except ValueError:
                # keep the word: NO_DIAGRAMS and NOT_INTEGRATED mean opposite things, and a table
                # that renders both as a dash claims a class is absent when it was never run
                out[(proc, model, order)] = (sig, None)
    return out


def tex_ratio(r, err=False):
    """R as printed: two significant figures, in parentheses when the interference has a Monte Carlo error above a tenth."""
    if r < 0.01:
        t = "<0.01"
    else:
        e = math.floor(math.log10(r))
        x = round(r, 1 - e)
        t = (f"{x / 10**e:.1f}\\times10^{{{e}}}" if e >= 3 else f"{x:.0f}" if e >= 1 else f"{x:.{1 - e}f}")
    return f"$({t})$" if err else f"${t}$"


def sq_over_sm(x):
    """For a class with no interference: its square in units of UNIT of the Standard-Model rate, printed as R is."""
    return tex_ratio(x / UNIT).strip("$")


# The rows the text of the paper discusses, shaded and with the class in bold so a reader can
# find them: psi^2X^2D, X^2H^2D^2 and psi^4D^2 are discussed in the truncation subsection, and X^4
# carries the asterisk discussion (the subsection on which classes contribute).  Keep this set in step with the phenomenology section of the paper.
HIGHLIGHT = {1, 7, 14, 21}


def label(c):
    """Row number and class, bold and on a shaded row when the text discusses the class."""
    name = CLASSES[c].replace("psi", "\\psi")
    if c in HIGHLIGHT:
        return "\\rowcolor{black!8}\\textbf{" + str(c) + "} & $\\boldsymbol{" + name + "}$"
    return str(c) + " & $" + name + "$"


def main():
    data = {s: read(s) for s, _, _ in COLS}
    M = {s: study_model(d, s) for s, d in data.items()}
    # The Standard-Model row of a process is the same whichever restriction card carries it,
    # since every coefficient is off, and the studies put it under whichever card was cheapest
    # to run: the unrestricted model for diboson and Drell-Yan, its bosonic card for triboson and VBF.
    sm = {}
    for study, proc, _ in COLS:
        v = [x for (p_, m_, o_), x in data[study].items()
             if p_ == proc and o_ == "NP=0" and isinstance(x[0], float)]
        sm[(study, proc)] = v[0][0] if v else None

    rows = []
    for c in sorted(CLASSES):
        cells = []
        for study, proc, _ in COLS:
            d, s0 = data[study], sm[(study, proc)]
            i = d.get((proc, f"{M[study]}-cls{c}", INT), (None, None))
            q = d.get((proc, f"{M[study]}-cls{c}", SQ), (None, None))
            # No interference is not the same statement as no diagram.  A class reached only
            # through a channel with no tree-level Standard-Model amplitude, gg > W+ W- through
            # G^2W^2 being the plainest case, has diagrams, a square, and nothing to interfere
            # with.  A dash would tell the reader the class is absent from the process.  It gets an
            # asterisk, and in the R column, since there is no interference to divide by, the
            # square in units of UNIT of the Standard-Model rate, in brackets.
            if i[0] == "ZERO":
                # diagrams exist and integrate to exactly zero: an open circle in both columns,
                # since the ratio of two vanishing terms is not "no diagram"
                cells += [r"$\circ$", r"$\circ$"]
                continue
            if i[0] == "NO_DIAGRAMS" and isinstance(q[0], float) and s0:
                cells += [r"$\ast$", "$[" + sq_over_sm(q[0] / s0) + "]$"]
                continue
            if isinstance(i[0], str) or isinstance(q[0], str) or i[0] is None or q[0] is None:
                mark = ("--" if "NO_DIAGRAMS" in (i[0], q[0]) or (i[0] is None and q[0] is None)
                        else r"$\dagger$")
                if not isinstance(i[0], float):
                    cells += [mark, mark]
                    continue
            if not isinstance(i[0], float):
                pct = "--"
            elif s0:
                # the same three-way encoding as the appendix grid: an open circle is a class that
                # produces a diagram but interferes negligibly, which is not the same statement as
                # a dash, and the two must not look alike
                x = i[0] / s0 / UNIT
                pct = (r"$\circ$" if abs(x) < 0.005 else f"${x:+.0f}$" if abs(x) >= 100
                       else f"${x:+.1f}$" if abs(x) >= 10 else f"${x:+.2f}$")
                # parentheses mark a Monte Carlo error above a tenth of the entry, as in the grid
                if pct != r"$\circ$" and i[1] and abs(i[1] / i[0]) > 0.1:
                    pct = "$(" + pct.strip("$") + ")$"
            else:
                pct = "--"
            if not isinstance(q[0], float) or not isinstance(i[0], float) or i[0] == 0:
                # an interference with no square beside it is a square that was never run,
                # which is a dagger; a dash is reserved for no diagram
                rat = (r"$\dagger$" if (isinstance(q[0], str) and q[0] == "NOT_INTEGRATED")
                       or (q[0] is None and isinstance(i[0], float)) else "--")
            else:
                rat = tex_ratio(q[0] / abs(i[0]), abs(i[1] / i[0]) > 0.1)
            cells += [pct, rat]
        rows.append((c, cells))

    head = (r"\begin{table}[!htbp]" "\n" r"\centering" "\n" r"\footnotesize" "\n"
            r"\setlength{\tabcolsep}{3.2pt}" "\n"
            r"\begin{tabular}{@{}r l " + " ".join(["r r"] * 4) + r"@{}}" "\n" r"\toprule" "\n"
            + r" & & " + " & ".join(r"\multicolumn{2}{c}{" + h + "}" for _, _, h in COLS) + r" \\" + "\n"
            + "".join(f"\\cmidrule(lr){{{3+2*i}-{4+2*i}}}" for i in range(4)) + "\n"
            + r" & class & " + " & ".join([r"$\delta\,[10^{-4}]$ & $R$"] * 4) + r" \\" + "\n"
            r"\midrule")
    body = []
    for c, cells in rows:
        body.append(label(c) + " & " + " & ".join(cells) + r" \\")
    # Adam's \AM review comments stay in the caption, verbatim, until their item is resolved: the table
    # is regenerated, so a comment written only into master.tex would be lost on the next refresh.
    tail = (r"\bottomrule" "\n" r"\end{tabular}" "\n"
            r"\caption{How much each dimension-eight class changes four LHC processes at order $1/\Lambda^4$, and how large its square is compared with that change. "
            r"All entries are for proton-proton collisions at the LHC with a centre-of-mass energy of $13.6$~TeV, with every coefficient of the class at one and $\Lambda = 3$~TeV, and the $HHjj$ and $e^+e^-$ samples carry the cuts given in \cref{tab:grid}. "
            r"$\delta$ is the interference with the Standard Model that \MG\ returns at \code{NP\^{}2==2}, in units of $10^{-4}$ of the Standard-Model rate, with an open circle where it is below $0.005$ in these units" + (" and a dagger where the class produces diagrams but was not run in these studies" if any(r"\dagger" in x for _, cells in rows for x in cells) else "") + r". "
            r"$R = \sigma_{1/\Lambda^8}/|\sigma_{1/\Lambda^4}|$ is the square of the class over its interference in the same sample, which we use to judge the validity of the $1/\Lambda^4$ truncation (\cref{sec:truncation}). "
            r"Parentheses, in either column, mean that the Monte Carlo error on the interference exceeds a tenth of it, and an open circle in an $R$ column means that the interference and the square both vanish. "
            r"An asterisk marks a class that reaches the process only through a channel with no tree-level Standard-Model amplitude, so that it has a square and no interference, and the number in square brackets beside it is that square in units of $10^{-4}$ of the Standard-Model rate. "
            r"A dash means the class produces no diagram in that process. "
            r"The power of each class at four, five and six legs is in \cref{tab:class-powers}, and \cref{sec:routes} explains which of its vertices a process uses. "
            r"\Cref{tab:grid} extends the interference column to all twelve processes. The shaded classes are those the text discusses, $X^4$ in \cref{sec:classes} and $X^2H^2D^2$, $\psi^2X^2D$ and $\psi^4D^2$ in \cref{sec:truncation}.}" "\n"
            r"\label{tab:master}" "\n" r"\end{table}")
    print(head)
    print("\n".join(body))
    print(tail)


if __name__ == "__main__":
    main()
