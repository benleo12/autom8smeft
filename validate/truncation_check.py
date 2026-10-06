#!/usr/bin/env python3
"""Check that the input-scheme corrections are truncated consistently at 1/Lambda^4.

    validate/truncation_check.py <UFO dir> [--tol 1e-9]

Every dimension-eight coefficient enters at order 1/Lambda^4, so every internal parameter of the
model must be exactly LINEAR in a common coefficient c, up to the places where a nonlinearity is
physical rather than a truncation error (MW = sqrt(MW2) is the standard example: MW2 is linear,
its square root is not).  This evaluates the whole internal parameter list at several values of c
and fits each parameter to a + b c, then reports the size of the quadratic remainder relative to
the linear term.

A parameter with a quadratic remainder that does not shrink like c^2 when c shrinks is a genuine
inconsistency: a 1/Lambda^8 term has been kept in a 1/Lambda^4 construction.  A parameter whose
remainder scales exactly like c^2 with a coefficient of order one is a nonlinearity introduced by
a square root or a division downstream of a linear shift, which is harmless as long as the
amplitude is expanded by MadGraph's coupling orders.

Needs a Python that can import the UFO (3.11 works).
"""
import sys, os, cmath, math


def evaluate(ufo, c):
    """Internal parameter values with every c8 coefficient set to c."""
    sys.path.insert(0, ufo)
    import parameters as P
    vals = {}
    for p in P.all_parameters:
        if p.nature == "external":
            vals[p.name] = c if p.name.startswith("c8") else float(p.value)
    ns = {"cmath": cmath, "math": math, "complex": complex,
          "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z}
    order = []
    for p in P.all_parameters:
        if p.nature == "internal":
            try:
                vals[p.name] = eval(p.value, ns, vals)
            except Exception:
                vals[p.name] = float("nan")
            order.append(p.name)
    return vals, order


def real(z):
    return z.real if isinstance(z, complex) else z


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ufo = os.path.abspath(argv[1])
    tol = 1e-9
    if "--tol" in argv:
        tol = float(argv[argv.index("--tol") + 1])

    # Two scales an octave apart.  A true 1/Lambda^8 contamination keeps the same relative size at
    # both, a square-root nonlinearity falls by four.
    for scale in (1e-3, 5e-4):
        cs = [-2 * scale, -scale, 0.0, scale, 2 * scale]
        rows = [evaluate(ufo, c) for c in cs]
        vals = [r[0] for r in rows]
        names = rows[0][1]
        worst = []
        for n in names:
            y = [real(v.get(n, float("nan"))) for v in vals]
            if any(math.isnan(t) or math.isinf(t) for t in y):
                continue
            # central second difference at c = 0, in units of the linear slope times the step
            lin = (y[3] - y[1]) / 2.0
            quad = (y[3] + y[1] - 2 * y[2]) / 2.0
            if abs(lin) < 1e-300 and abs(quad) < 1e-300:
                continue
            ref = max(abs(lin), abs(y[2]) * 1e-16)
            if ref == 0:
                continue
            worst.append((abs(quad) / ref, n, y[2], lin, quad))
        worst.sort(reverse=True)
        print(f"c = +-{scale:g}: {len(worst)} c-dependent internal parameters")
        for r, n, y0, lin, quad in worst[:12]:
            print(f"    {n:24s} value {y0: .8g}  linear {lin: .4g}  quadratic/linear {r:.3e}")
        print(f"    largest quadratic/linear ratio: {worst[0][0]:.3e}"
              if worst else "    no c dependence found")
    print()
    print("Read the two blocks together.  A ratio that HALVES when the step halves is a harmless")
    print("downstream nonlinearity, since the quadratic remainder scales like c^2 while the linear")
    print("term scales like c.  A ratio that stays PUT is a 1/Lambda^8 term surviving in a")
    print("1/Lambda^4 construction, which is a real defect.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
