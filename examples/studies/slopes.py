#!/usr/bin/env python3
"""The energy-growth slope of every class in the hadron-collider distributions.

    examples/studies/slopes.py [--tex out.tex]

The lepton-collider fits measure the exponent under conditions the counting assumes: fixed
angle, fixed partonic energy, no parton luminosity.  The distributions of the phenomenology
section are the same quantity under realistic conditions, and the ratio panel of each figure is
already the right object to read it off.

In a bin of the pair mass the parton luminosity cancels between a class and the Standard Model,
because both are the same initial states integrated over the same range of x, so

    sigma_int / sigma_SM  =  2 Re(M_8 / M_SM)   ~   E^q      d log / d log m  =  q
    sigma_sq  / sigma_SM  =  |M_8 / M_SM|^2     ~   E^{2q}   d log / d log m  = 2q

with M_8 ~ E^q v^p / Lambda^4 and a Standard-Model amplitude that is energy independent at fixed
angle.  Three things break that at a hadron collider and the measured slopes show all three: the
Standard-Model amplitude is not energy independent once the forward t-channel is included, the
bin integrates over angle, and the interference picks only the part of M_8 that overlaps the
Standard-Model helicity structure while the square picks all of it.  The slopes are therefore
read as an ordering and a route classification rather than as a measurement of q, which is what
the fixed-angle lepton-collider test is for.

The fit window matches what the figures plot, so the number describes the curve on the page.
"""
from __future__ import annotations

import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import epower  # noqa: E402

# (tsv, label, low cut, high cut) with the cuts of paper/refresh.sh so the fit is over the
# plotted range and not over the empty tail
STUDIES = [
    ("paper/figs/ww_classes_mVV.tsv",    r"$pp \to W^+W^-$",    300.0, 2400.0),
    ("paper/figs/zz_classes_mVV.tsv",    r"$pp \to ZZ$",        300.0, 2400.0),
    ("paper/figs/www_classes_mVV.tsv",   r"$pp \to W^+W^-W^+$", 400.0, 3000.0),
    ("paper/figs/vbfhh_classes_mVV.tsv", r"$pp \to HHjj$",      300.0, 2100.0),
]


def counting_of(tex):
    """(lambda power, energy power) at four legs, for a class as the tsv header writes it.

    The lambda power is the label: with (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1) it is
    one number per class instead of a pair, and a smaller one is a larger contribution.  The
    energy power is what a slope can be compared against, and at four legs the two are tied,
    lambda^(4+p) meaning p powers of E traded for p powers of v.
    """
    name = tex.replace("$", "").replace("\\psi", "psi").replace(" squared", "").strip()
    if name not in epower.DIM8_CLASSES:
        return None, None
    r = epower.leading(*epower.DIM8_CLASSES[name], 4)
    return (None, None) if isinstance(r, str) else (r.lambdaExp, r.q)


def slope(xs, ys):
    n = len(xs)
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    b = sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    resid = [y - (my + b * (x - mx)) for x, y in zip(xs, ys)]
    s2 = sum(r * r for r in resid) / max(n - 2, 1)
    return b, math.sqrt(s2 / sxx)


def run(path, lo_cut, hi_cut):
    rows = [l.rstrip("\n").split("\t") for l in open(path) if l.strip()]
    head, rows = rows[0], rows[1:]
    si = head.index("SM")
    out = []
    for ci, col in enumerate(head[2:], start=2):
        if col == "SM":
            continue
        xs, ys = [], []
        for r in rows:
            lo, hi = float(r[0]), float(r[1])
            sm, v = float(r[si]), abs(float(r[ci]))
            m = 0.5 * (lo + hi)
            if sm <= 0 or v <= 0 or m < lo_cut or m > hi_cut:
                continue
            xs.append(math.log(m))
            ys.append(math.log(v / sm))
        if len(xs) < 4:
            continue
        s = slope(xs, ys)
        if s:
            lam, q = counting_of(col)
            out.append((col, lam, q, s[0], s[1], len(xs), "squared" in col))
    return out


def main(argv):
    res = [(lab, run(os.path.join(ROOT, f), lo, hi)) for f, lab, lo, hi in STUDIES
           if os.path.exists(os.path.join(ROOT, f))]
    for lab, rows in res:
        print(f"\n{lab}")
        for col, lam, q, b, e, n, sq in rows:
            exp = "--" if q is None else f"{2*q if sq else q:+d}"
            lm = "--" if lam is None else f"lam^{lam}"
            print(f"   {col.replace('$',''):<24s} {lm:>6s}  expect {exp:>3s}   "
                  f"measured {b:+6.2f} +- {e:4.2f}   ({n} bins){'  [square]' if sq else ''}")

    if "--tex" in argv:
        path = argv[argv.index("--tex") + 1]
        body = []
        for lab, rows in res:
            body.append(r"\midrule \multicolumn{5}{l}{" + lab + r"} \\")
            for col, lam, q, b, e, n, sq in rows:
                nm = col.replace("$", "")
                exp = "--" if q is None else f"${2*q if sq else q:+d}$"
                lm = "--" if lam is None else (r"$\lambda^{%d}$" % lam)
                body.append(f"${nm}$".replace("squared", r"\text{ sq}")
                            + f" & {lm} & {exp} & ${b:+.2f} \\pm {e:.2f}$ & {n}" + r" \\")
        open(path, "w").write(
            r"""\begin{table}[!htbp]\centering\footnotesize
\setlength{\tabcolsep}{6pt}
\begin{tabular}{@{}l c c c r@{}}
\toprule
class & $\lambda$ & implied & fitted slope & bins \\
""" + "\n".join(body) + r"""
\bottomrule
\end{tabular}
\caption{The energy-growth slope $d\log|\sigma/\sigma_{\rm SM}|/d\log m$ of every class in the
distributions of \cref{fig:ww,fig:triboson,fig:vbfhh}, fitted over the range each figure plots.
The $\lambda$ column is the counting's label for the class at four legs, and a smaller power is
a larger contribution. The ``implied'' column is the slope that label predicts: the parton
luminosity cancels in the ratio, so $\lambda^{4+p}$ means an interference growing as $E^{4-p}$
and a square as $E^{2(4-p)}$ against a Standard-Model amplitude that is energy independent at
fixed angle. It is not energy independent once the forward $t$-channel is included and the bin is
integrated over angle, so the measured slopes sit below the implied one, by a roughly common
amount within each process wherever a power law fits at all. Three rows have a fit error of three
to five and are not measurements of anything. What survives is the ordering and the route: the
classes the counting puts at $\lambda^4$ are the steep ones, and those acting through the input
relations are flat, with an error small enough to exclude their label. The fixed-angle measurement
is \cref{tab:v12}.}
\label{tab:slopes}
\end{table}
""")
        print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
