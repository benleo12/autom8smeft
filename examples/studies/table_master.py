#!/usr/bin/env python3
"""One table for the whole phenomenology section, organised by the energy counting.

    examples/studies/table_master.py > paper/tables/master.tex

The per-process tables say what each class does in one process.  This one says what the 21
classes do across four processes at once, next to the exponent the counting assigns them, which
is the only arrangement in which the counting's three predictions are visible as predictions:

  * a class with no four-point vertex reachable in the process has no diagram at all, and the
    table shows that as a dash rather than as a small number,
  * the classes with the largest q are the ones whose square overruns their interference first,
  * and the ordering of the four processes by how badly the expansion fails is the ordering of
    their leading class's q.

Columns per process are the interference as a percentage of the Standard Model and Lambda_min,
the scale above which the class's square is smaller than its interference at unit coefficient in
the inclusive sample.  The ratio R = sigma_{1/Lambda^8}/|sigma_{1/Lambda^4}| scales as 1/Lambda^4
at fixed kinematics, so Lambda_min = R^{1/4} TeV from the runs at 1 TeV, and it is the scale below
which the 1/Lambda^4 truncation is not self-consistent for that class in that sample.  A raw R of
61 at Lambda = 1 TeV is not a prediction of a large effect; it says the expansion has failed there,
and 2.8 TeV is the number a reader can use (2026-10-04, after a reader asked what the point of a
square larger than its interference was).  For a class with no interference the bracketed entry
is the scale above which the square is smaller than the Standard-Model rate, (sq/SM)^{1/8} TeV.
Pure Python, reads each study's results.tsv.
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import epower  # noqa: E402

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
                out[(proc, model, order)] = (float(sig), float(err))
            except ValueError:
                # keep the word: NO_DIAGRAMS and NOT_INTEGRATED mean opposite things, and a table
                # that renders both as a dash claims a class is absent when it was never run
                out[(proc, model, order)] = (sig, None)
    return out


def tev(x):
    """A scale in TeV with the precision its size deserves."""
    return f"{x:.2f}" if x < 1 else f"{x:.1f}" if x < 10 else f"{x:.0f}"


def tex_ratio(r):
    """Lambda_min in TeV from R at 1 TeV: R^(1/4)."""
    return "$" + tev(r ** 0.25) + "$"


def sq_over_sm(x):
    """For a class with no interference: the scale in TeV above which its square is below the
    Standard-Model rate, (sq/SM)^(1/8) from the run at 1 TeV."""
    return tev(x ** 0.125)


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


def tex_q(cls):
    """The counting's leading lambda power for this class at four legs, or a dash when four legs
    cannot be made at all.  One number rather than a (q, p) pair, and it is the column the
    reachability prediction lives in: a dash is a class that cannot reach a four-point vertex."""
    r = epower.leading(*epower.DIM8_CLASSES[CLASSES[cls]], 4)
    return "--" if isinstance(r, str) else "$\\lambda^{%d}$" % r.lambdaExp


def main():
    data = {s: read(s) for s, _, _ in COLS}
    # The Standard-Model row of a process is the same whichever restriction card carries it,
    # since every coefficient is off, and the studies put it under whichever card was cheapest
    # to run: "dim8_is" for diboson and Drell-Yan, "dim8_is-bosonic" for triboson and VBF.
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
            i = d.get((proc, f"dim8_is-cls{c}", INT), (None, None))
            q = d.get((proc, f"dim8_is-cls{c}", SQ), (None, None))
            # No interference is not the same statement as no diagram.  A class reached only
            # through a channel with no tree-level Standard-Model amplitude, gg > W+ W- through
            # G^2W^2 being the plainest case, has diagrams, a square, and nothing to interfere
            # with.  Rendering that as a dash told the reader the class was absent from a process
            # where its square is 53 times the Standard Model.  It gets an asterisk, and in the
            # Lambda_min column, since there is no interference to divide by, the scale at which
            # the square falls below the Standard Model, in brackets.
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
                x = 100 * i[0] / s0
                pct = (r"$\circ$" if abs(x) < 0.005 else f"${x:+.0f}$" if abs(x) >= 100
                       else f"${x:+.1f}$" if abs(x) >= 10 else f"${x:+.2f}$")
            else:
                pct = "--"
            if not isinstance(q[0], float) or not isinstance(i[0], float) or i[0] == 0:
                # an interference with no square beside it is a square that was never run,
                # which is a dagger; a dash is reserved for no diagram
                rat = (r"$\dagger$" if (isinstance(q[0], str) and q[0] == "NOT_INTEGRATED")
                       or (q[0] is None and isinstance(i[0], float)) else "--")
            else:
                rat = tex_ratio(q[0] / abs(i[0]))
            cells += [pct, rat]
        rows.append((c, cells))

    head = (r"\begin{table}[!htbp]" "\n" r"\centering" "\n" r"\footnotesize" "\n"
            r"\setlength{\tabcolsep}{3.2pt}" "\n"
            r"\begin{tabular}{@{}r l c " + " ".join(["r r"] * 4) + r"@{}}" "\n" r"\toprule" "\n"
            + r" & & & " + " & ".join(r"\multicolumn{2}{c}{" + h + "}" for _, _, h in COLS) + r" \\" + "\n"
            + "".join(f"\\cmidrule(lr){{{4+2*i}-{5+2*i}}}" for i in range(4)) + "\n"
            + r" & class & $\lambda$ & " + " & ".join([r"$\delta\%$ & $\Lambda_{\min}$"] * 4) + r" \\" + "\n"
            r"\midrule")
    body = []
    for c, cells in rows:
        body.append(label(c) + f" & {tex_q(c)} & " + " & ".join(cells) + r" \\")
    tail = (r"\bottomrule" "\n" r"\end{tabular}" "\n"
            r"\caption{Every dimension-eight class in four processes, as the term \MG\ returns at \code{NP\^{}2==2}, which excludes the $W$-mass bracket of \cref{eq:np0}, against the power of $\lambda$ the "
            r"counting assigns it. The $\lambda$ column is the leading power the class's fastest "
            r"four-point vertex can reach, with $(\Lambda, E, v) \sim (\lambda^{-3}, \lambda^{-2}, \lambda^{-1})$, so $\lambda^4$ is the steepest and a larger power more suppressed. A dash there means four legs cannot be made from the "
            r"class's fields at all. $\delta\%$ is the interference with the Standard Model as a "
            r"percentage of it, an open circle where the interference is below $0.01$, and a dagger where "
            r"the process was too expensive to run that entry. $\Lambda_{\min}$, in TeV, is the scale above which the square of the class is smaller than its interference at unit coefficient in this inclusive sample: the ratio $\sigma_{1/\Lambda^8}/|\sigma_{1/\Lambda^4}|$ scales as $\Lambda^{-4}$ at fixed kinematics, so $\Lambda_{\min}$ is its fourth root at the $1$~TeV runs, and below it the $1/\Lambda^4$ truncation is not self-consistent for that class. An asterisk marks a class that reaches the process only through a channel with no tree-level Standard-Model amplitude, so that it has a square and no interference. The bracketed number beside it is then the scale above which that square is smaller than the Standard-Model rate. A dash in either column means the class "
            r"produces no diagram in that process. All at $13.6$~TeV with every "
            r"coefficient of the class at one, the interference quoted at $\Lambda=1$~TeV. \cref{tab:grid} extends the interference column "
            r"to all twelve processes of the four studies. The shaded rows are the classes the text discusses: the three that set $\Lambda_{\min}$ in "
            r"diboson, vector boson fusion and Drell-Yan production, and $X^4$.}" "\n"
            r"\label{tab:master}" "\n" r"\end{table}")
    print(head)
    print("\n".join(body))
    print(tail)


if __name__ == "__main__":
    main()
