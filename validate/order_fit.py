#!/usr/bin/env python3
"""
validate/order_fit.py  --  get the EFT orders out of MadGraph without trusting coupling tags.

Why this exists.  MadGraph decides which order bin a term belongs to by the coupling orders it
was given, and it tags couplings, not masses.  In the {alpha, M_Z, G_F} scheme M_W is derived, so
it moves when a Wilson coefficient moves, and so do the vev, the Yukawas and the Higgs
normalisation.  None of that can carry an NP tag, so a tagged bin such as NP^2==1 is not the
complete interference: on p p > w+ w- the missing piece measured +1.35 +- 0.115 pb, which is 11.7
sigma.  Adding the dimension-six sector makes it worse, not better, because more internal
parameters become coefficient-dependent.

What is exact is the TOTAL.  Ask MadGraph for every diagram up to the truncation you want, with
no NP^2 constraint, and it computes the honest cross section of the Lagrangian it was given,
masses and all.  Scan one coefficient, fit a polynomial in it, and the fit coefficients are the
orders:

    sigma(c) = sigma_0 + sigma_1 c + sigma_2 c^2 + ...

sigma_0 is the Standard Model, sigma_1 the interference (1/Lambda^4 for a dimension-eight
coefficient, 1/Lambda^2 for a dimension-six one) and sigma_2 the square.  No tag is involved.

sigma(c) is not exactly polynomial, since M_W(c) is a square root of a linear expression, but the
departure is beyond the truncation: every coefficient-dependent internal parameter was measured
linear in c to 1.8e-5 relative (validate/truncation_check.py).  The tool fits one degree above
what you ask for and reports the extra coefficient, so you can see the contamination rather than
assume it away.

    validate/order_fit.py <UFO dir or model name> "p p > w+ w-" --coeff c8q2W2Dx1
    validate/order_fit.py dim68_is "p p > e+ e-" --coeff cHq1 --scale6 1000 --degree 2
    validate/order_fit.py dim8_is "p p > w+ w-" --coeff c8q2W2Dx1 --compare-tagged "NP^2==2"

With --compare-tagged it also runs the tagged bin and prints both, which is how the size of the
tagging defect gets measured instead of argued about.
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.environ.get("MG5_DIR", "${MG5_DIR:-/path/to/MG5_aMC}")


def mg5_python() -> str:
    for c in ("python3.11", "python3"):
        p = shutil.which(c)
        if p:
            return p
    sys.exit("no python3 found")


def write_script(a, values, path, outdir) -> None:
    """One MadGraph script: generate and output once, then launch once per coefficient value."""
    lines = [f"import model {a.model}", f"generate {a.process} {a.order}",
             f"output {outdir} -f"]
    for i, v in enumerate(values):
        lines += [f"launch {outdir}",
                  "  0",
                  f"  set nevents {a.events}",
                  f"  set ebeam1 {a.ebeam}",
                  f"  set ebeam2 {a.ebeam}",
                  "  set hel_recycling False",
                  f"  set iseed {a.seed + i}"]
        if a.scale8:
            # the dimension-eight scale is lam__2 in the param card, not lam: the external Lam
            # lowercases onto the Standard Model's quartic coupling lam, and MadGraph resolves
            # the clash by appending __2
            lines.append(f"  set lam__2 {a.scale8}")
        if a.scale6:
            lines.append(f"  set lam6 {a.scale6}")
        lines.append(f"  set {a.coeff} {v!r}")
        lines.append("  0")
    open(path, "w").write("\n".join(lines) + "\n")


def cross_sections(log: str) -> list[tuple[float, float]]:
    out = []
    for m in re.finditer(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", log):
        out.append((float(m.group(1)), float(m.group(2))))
    return out


def _inverse(m):
    """Inverse of a small square matrix by Gauss-Jordan with partial pivoting."""
    n = len(m)
    a = [list(row) + [1.0 if i == j else 0.0 for j in range(n)] for i, row in enumerate(m)]
    for col in range(n):
        piv = max(range(col, n), key=lambda r: abs(a[r][col]))
        if abs(a[piv][col]) < 1e-300:
            raise ZeroDivisionError("singular design matrix: are two scan points equal?")
        a[col], a[piv] = a[piv], a[col]
        d = a[col][col]
        a[col] = [v / d for v in a[col]]
        for r in range(n):
            if r != col and a[r][col]:
                f = a[r][col]
                a[r] = [v - f * w for v, w in zip(a[r], a[col])]
    return [row[n:] for row in a]


def fit(values, xs, errs, degree):
    """Weighted least squares on a polynomial of the given degree, in plain Python so that the
    tool has no dependency to install: solve (A^T W A) beta = A^T W y and take the covariance
    from the same inverse.  Returns (coeffs, errors, chi2, dof), coeffs[k] multiplying c^k."""
    e = [max(v, 1e-12) for v in errs]
    w = [1.0 / v ** 2 for v in e]
    A = [[x ** k for k in range(degree + 1)] for x in values]
    n = degree + 1
    ata = [[sum(w[i] * A[i][r] * A[i][c] for i in range(len(values))) for c in range(n)]
           for r in range(n)]
    aty = [sum(w[i] * A[i][r] * xs[i] for i in range(len(values))) for r in range(n)]
    cov = _inverse(ata)
    beta = [sum(cov[r][c] * aty[c] for c in range(n)) for r in range(n)]
    chi2 = sum(w[i] * (xs[i] - sum(beta[k] * A[i][k] for k in range(n))) ** 2
               for i in range(len(values)))
    return beta, [cov[k][k] ** 0.5 for k in range(n)], chi2, max(len(values) - n, 0)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("process")
    ap.add_argument("--coeff", required=True)
    ap.add_argument("--values", default="", help="comma separated; default is 0 and +-delta, +-2delta")
    ap.add_argument("--delta", type=float, default=1.0)
    ap.add_argument("--order", default="NP<=2",
                    help="the truncation, with NO NP^2 constraint (default NP<=2: up to one dim-8 "
                         "or two dim-6 insertions)")
    ap.add_argument("--degree", type=int, default=2)
    ap.add_argument("--events", type=int, default=5000)
    ap.add_argument("--ebeam", type=float, default=6800)
    ap.add_argument("--seed", type=int, default=21)
    ap.add_argument("--scale8", default="", help="Lam in GeV, if the model has dimension eight")
    ap.add_argument("--scale6", default="", help="Lam6 in GeV, if the model has dimension six")
    ap.add_argument("--compare-tagged", default="",
                    help="also run this tagged order and print it beside the fitted coefficient")
    ap.add_argument("--rundir", default=os.path.expanduser("~/dim8auto_build/mg5runs/order_fit"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--reuse", action="store_true",
                    help="re-fit from the log of a previous run instead of calling MadGraph again")
    a = ap.parse_args()

    values = ([float(v) for v in a.values.split(",")] if a.values
              else [-2 * a.delta, -a.delta, 0.0, a.delta, 2 * a.delta])
    if len(values) < a.degree + 2:
        sys.exit(f"need at least {a.degree + 2} values to fit degree {a.degree} and see the next one")

    tag = re.sub(r"\W+", "_", f"{a.process}_{a.coeff}").strip("_")
    outdir = os.path.join(a.rundir, tag)
    os.makedirs(a.rundir, exist_ok=True)
    script = os.path.join(a.rundir, tag + ".mg5")
    write_script(a, values, script, outdir)
    print(f"[cfg] model {a.model}  process {a.process}  order {a.order}")
    print(f"[cfg] {a.coeff} at {values}, {a.events} events each, degree {a.degree} + 1")
    print(f"[cfg] script {script}")
    if a.dry_run:
        print(open(script).read())
        return

    log = os.path.join(a.rundir, tag + ".log")
    if a.reuse and os.path.exists(log) and len(cross_sections(open(log, errors="replace").read())) >= len(values):
        print(f"[reuse] {len(values)} cross sections already in {log}")
    else:
        with open(log, "w") as fh:
            subprocess.run([mg5_python(), os.path.join(MG, "bin", "mg5_aMC"), "-f", script],
                           stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, check=False)
    text = open(log, errors="replace").read()
    got = cross_sections(text)
    if len(got) < len(values):
        print(f"[abort] {len(got)} cross sections for {len(values)} points; see {log}")
        for i, (x, e) in enumerate(got):
            print(f"    {values[i] if i < len(values) else '?'}: {x} +- {e}")
        sys.exit(1)
    got = got[:len(values)]

    # A 'set' naming something MadGraph does not know is ignored SILENTLY, so the whole scan
    # would come back flat and be fitted as a Standard Model with no operator in it.  Read the
    # coefficient back out of the param card of the last run before believing any of it.
    pc = os.path.join(outdir, "Cards", "param_card.dat")
    if os.path.exists(pc):
        want = re.compile(r"^\s*\d+\s+([-\d.eE+]+)\s*#\s*" + re.escape(a.coeff) + r"\s*$",
                          re.I | re.M)
        m = want.search(open(pc, errors="replace").read())
        if not m:
            print(f"[abort] {a.coeff} is not in {pc}: the set command was ignored")
            sys.exit(1)
        if abs(float(m.group(1)) - values[-1]) > 1e-9 * max(1.0, abs(values[-1])):
            print(f"[abort] the param card has {a.coeff} = {m.group(1)} after the last point, "
                  f"which asked for {values[-1]}: the set command did not take")
            sys.exit(1)
        print(f"[ok] the param card confirms {a.coeff} = {m.group(1)} on the last point")

    print(f"\n{'coefficient':>14s} {'sigma [pb]':>16s} {'MC error':>12s}")
    for v, (x, e) in zip(values, got):
        print(f"{v:>14.6g} {x:>16.6g} {e:>12.4g}")

    beta, err, chi2, dof = fit(values, [g[0] for g in got], [g[1] for g in got], a.degree + 1)
    names = {0: "sigma_0  (Standard Model)", 1: "sigma_1  (interference)",
             2: "sigma_2  (square)", 3: "sigma_3  (beyond the truncation)",
             4: "sigma_4  (beyond the truncation)"}
    print(f"\nfit of degree {a.degree + 1}, chi2/dof = {chi2:.2f}/{dof}")
    for k in range(a.degree + 2):
        flag = ""
        if k > a.degree:
            ref = max(abs(beta[j]) for j in range(a.degree + 1)) or 1.0
            flag = ("   <- should be small against the others: "
                    f"{abs(beta[k]) / ref:.2e} of the largest")
        print(f"  {names.get(k, 'sigma_' + str(k)):<30s} {beta[k]:>14.6g} +- {err[k]:.4g}{flag}")

    # The fit is exact but it is statistics-hungry in a way a tagged bin is not: MadGraph
    # integrates a tagged interference on its own, so its error is a fraction of that
    # interference, while the fit has to resolve the same term against the full cross section.
    # The cure is a larger coefficient, which costs nothing as long as sigma_3 stays small.
    for k in (1, 2):
        if k <= a.degree and beta[k] and err[k] > 0.2 * abs(beta[k]):
            want = a.delta * (err[k] / (0.1 * abs(beta[k]))) ** 0.5
            print(f"\n[advice] sigma_{k} is only {abs(beta[k]) / err[k]:.1f} sigma from zero. The fit has to"
                  f" resolve it\n          against the whole cross section, so scan wider rather than"
                  f" longer: --delta {want:.0f}\n          would get it to about ten percent, and sigma_"
                  f"{a.degree + 1} is {abs(beta[a.degree + 1]) / max(abs(b) for b in beta[:a.degree + 1]):.1e}"
                  f" of the largest term, so there is room.")
            break

    if a.compare_tagged:
        t2 = tag + "_tagged"
        d2 = os.path.join(a.rundir, t2)
        s2 = os.path.join(a.rundir, t2 + ".mg5")
        b = argparse.Namespace(**vars(a))
        b.order = a.compare_tagged
        write_script(b, [a.delta], s2, d2)
        l2 = os.path.join(a.rundir, t2 + ".log")
        with open(l2, "w") as fh:
            subprocess.run([mg5_python(), os.path.join(MG, "bin", "mg5_aMC"), "-f", s2],
                           stdout=fh, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, check=False)
        tg = cross_sections(open(l2, errors="replace").read())
        if tg:
            x, e = tg[0]
            # the tagged bin at c = delta against what the fit says that order contributes there
            k = 1 if "==1" in a.compare_tagged else 2
            pred = beta[k] * a.delta ** k
            dd = x - pred
            sig = (e ** 2 + (err[k] * a.delta ** k) ** 2) ** 0.5
            print(f"\ntagged {a.compare_tagged} at {a.coeff} = {a.delta}: {x:.6g} +- {e:.4g} pb")
            print(f"  the fit says that order contributes {pred:.6g} +- {err[k] * a.delta ** k:.4g} pb")
            print(f"  difference {dd:+.6g} pb"
                  + (f" = {abs(dd) / sig:.1f} sigma" if sig else "")
                  + "   (the part of the order that no coupling tag can see)")
        else:
            print(f"\n[warn] the tagged run gave no cross section; see {l2}")


if __name__ == "__main__":
    main()
