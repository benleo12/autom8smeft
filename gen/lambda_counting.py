"""
gen/lambda_counting.py  --  the Assi-Martin energy-enhanced (lambda) counting, applied
automatically to every term of the catalogue.

Algorithm (Assi, Martin, "Energy-Enhanced Expansion of the SMEFT", Sec. II), for an
operator with field content (N_f, N_H, N_X, N_D) and a tree-level n-point vertex:

    D      = 3/2 N_f + N_H + 2 N_X + N_D - 4           (= 4 at dimension 8)
    d      = 4 - n
    p_min  = max(N_f + N_X + N_H - n, 0)
    q_max  = D + d - p_min
    k_max  = N_H - max(n - N_f - 2 N_X - N_D, 0)       (0 if N_H = 0)
    p_k    = p_min + k,  q_k = q_max - k,  k = 0 .. min(k_max, q_max)
    lambda exponent  = 3 D - 2 q_max - p_min           (regime Lambda >> E >> v)

Reachability.  The paper writes N_f + N_X <= n <= 2 N_f + N_X + N_D + N_H, which with
N_f = number of fermion fields cannot be right (a bilinear has N_f = 2 and gives two legs)
and excludes X^4 at n = 5, 6 although those rows appear in its Tables V and VI.  We use
the bound that the k_max formula itself implies,

    N_f + N_X <= n <= N_f + 2 N_X + N_D + N_H    (non-abelian X gives V^2),

and record this choice (docs/lambda_counting_extract.md, Q4) for the erratum list.

Usage:  python3 gen/lambda_counting.py docs/murphy_catalogue.json [--n 4 5 6] [--latex out.tex]
"""

from __future__ import annotations

import argparse
import csv
import json
from fractions import Fraction
from pathlib import Path


def count(Nf: int, NH: int, NX: int, ND: int, n: int) -> dict | None:
    D = Fraction(3, 2) * Nf + NH + 2 * NX + ND - 4
    assert D.denominator == 1, "half-integer operator dimension"
    D = int(D)
    if not (Nf + NX <= n <= Nf + 2 * NX + ND + NH):
        return None
    d = 4 - n
    pmin = max(Nf + NX + NH - n, 0)
    qmax = D + d - pmin
    if qmax < 0:
        return None
    kmax = (NH - max(n - Nf - 2 * NX - ND, 0)) if NH > 0 else 0
    kmax = max(kmax, 0)
    if pmin == kmax:
        # every Higgs that could be traded for a vev is already vev'd at leading order,
        # so there is no subleading tower (Epower_count.nb rule, confirmed BA 2026-08-28)
        kmax = 0
    ks = list(range(0, min(kmax, qmax) + 1))
    return dict(
        n=n, D=D, p_min=pmin, q_max=qmax, k_max=kmax,
        lam=3 * D - 2 * qmax - pmin,
        sub=[(qmax - k, pmin + k) for k in ks],
    )


def classify(cat: list, ns=(4, 5, 6)) -> list:
    rows = []
    for op in cat:
        f = op["fields"]
        r = dict(name=op["name"], cls=op["class_number"], class_name=op["class_name"], **f)
        for n in ns:
            c = count(f["N_f"], f["N_H"], f["N_X"], f["N_D"], n)
            if c is None:
                r[f"lam{n}"] = None
                r[f"qp{n}"] = None
            else:
                r[f"lam{n}"] = c["lam"]
                r[f"qp{n}"] = c["sub"][0]
                r[f"sub{n}"] = c["sub"]
        rows.append(r)
    return rows


def per_class_table(rows: list, ns=(4, 5, 6)) -> list:
    """One line per Murphy class: count of terms and the lambda exponent at each n (all
    terms of a class share (N_f, N_H, N_X, N_D), so the exponent is a class property)."""
    out = {}
    for r in rows:
        key = (r["cls"], r["class_name"])
        if key not in out:
            out[key] = dict(cls=r["cls"], class_name=r["class_name"], n_terms=0,
                            **{f"lam{n}": r[f"lam{n}"] for n in ns},
                            **{f"qp{n}": r[f"qp{n}"] for n in ns})
        out[key]["n_terms"] += 1
    return [out[k] for k in sorted(out)]


def latex_table(tab: list, ns=(4, 5, 6)) -> str:
    head = "class & $N_{\\rm term}$ & " + " & ".join(f"$n={n}$: $(q,p)$, $\\lambda^{{(n)}}$" for n in ns) + " \\\\"
    lines = ["\\begin{tabular}{l r " + " ".join("c" for _ in ns) + "}", "\\toprule", head, "\\midrule"]
    for r in tab:
        cells = []
        for n in ns:
            if r[f"lam{n}"] is None:
                cells.append("--")
            else:
                q, p = r[f"qp{n}"]
                cells.append(f"$({q},{p})$, $\\lambda^{{{r[f'lam{n}']}}}$")
        lines.append(f"{r['cls']}: ${r['class_name']}$ & {r['n_terms']} & " + " & ".join(cells) + " \\\\")
    lines += ["\\bottomrule", "\\end{tabular}"]
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("catalogue")
    ap.add_argument("--n", nargs="+", type=int, default=[4, 5, 6])
    ap.add_argument("--latex")
    ap.add_argument("--csv")
    a = ap.parse_args()
    cat = json.load(open(a.catalogue))
    rows = classify(cat, tuple(a.n))
    tab = per_class_table(rows, tuple(a.n))
    for r in tab:
        print(f"{r['cls']:2d} {r['class_name']:16s} terms={r['n_terms']:4d} " + "  ".join(
            f"n={n}: {('-' if r[f'lam{n}'] is None else f'(q,p)={r[f'qp{n}']} lam^{r[f'lam{n}']}')}" for n in a.n))
    if a.latex:
        Path(a.latex).write_text(latex_table(tab, tuple(a.n)))
    if a.csv:
        with open(a.csv, "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                w.writerow({k: (json.dumps(v) if isinstance(v, (list, tuple)) else v) for k, v in r.items()})
