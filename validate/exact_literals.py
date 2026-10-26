#!/usr/bin/env python3
"""Write the decimal literals of a UFO's expressions as exact fractions, in place.

    validate/exact_literals.py <UFO dir>            rewrite, and print what was rewritten
    validate/exact_literals.py <UFO dir> --check    rewrite nothing; exit 1 if MadGraph would
                                                    truncate a literal of a coupling or parameter

FeynRules writes a leading negative rational coefficient as a decimal,
-0.16666666666666666*(cw*complex(0,1)*g1SM), and the others as fractions, (...)/6.  Python
reads the decimal as the nearest double, so every Python reader of the UFO, the comparisons in
validate/ included, sees the right number.  MadGraph does not.  Its Fortran writer prints a
literal with seven significant digits, 1.666667D-01, so in the compiled matrix element that
coupling is 1/6 (1 + 2e-7).  Couplings that should cancel then do not quite: in
u_R u_R~ > W+ W- the photon and Z exchanges cancel down to M_Z^2/s, and with the photon's
hypercharge coupling to the quark doublet off by 2e-7 the amplitude is off by about
2e-7 s/M_Z^2, 2e-5 at 1 TeV and 2e-4 at 3 TeV.  Seen first as a ratio of 1.0000239 against the
Matchete UFO for the u^2W^2D and d^2W^2D interference, growing like s, and the same for
Q_{u^2H^2D^3}^{(1)}, while left-handed quarks stayed at 1e-8
(a comparison of compiled matrix elements, 2026-10-23).

A literal is rewritten when seven significant digits do not give back the same double and a
fraction p/q with q <= 10^6 does; it is written (p./q.), which Python evaluates to the same
double and MadGraph writes as an exact quotient.  So nothing changes for a Python reader.  A
literal with no such fraction is left and reported.  ALOHA turns the decimals of lorentz.py into
fractions itself; they are rewritten all the same, so that the model reads one way throughout.
Only quoted expressions are touched (coupling values, internal parameter values, Lorentz
structures), never the default value of an external parameter."""
import os
import re
import sys
from fractions import Fraction

FILES = ("couplings.py", "parameters.py", "lorentz.py")
EXPR = re.compile(r"((?:value|structure) = ')([^']*)(')")
# a decimal or exponent literal that is not part of a name or of a longer number
LIT = re.compile(r"(?<![\w.])(\d+\.\d+(?:[eE][-+]?\d+)?|\d+[eE][-+]?\d+)(?![\w.])")
MAXDEN = 10 ** 6


def truncated(lit):
    """True when MadGraph's seven significant digits do not give back the literal's double."""
    x = float(lit)
    return float("%e" % x) != x


def fraction(lit):
    """The fraction p/q, q <= MAXDEN, that rounds to exactly the literal's double, or None."""
    f = Fraction(float(lit)).limit_denominator(MAXDEN)
    return f if float(f) == float(lit) else None


def rewrite_text(txt):
    """(new text, {(literal, fraction): count}, [literals left]) for one file's text."""
    done, left = {}, []

    def one(m):
        lit = m.group(1)
        if not truncated(lit):
            return lit
        f = fraction(lit)
        if f is None:
            left.append(lit)
            return lit
        key = (lit, f"{f.numerator}/{f.denominator}")
        done[key] = done.get(key, 0) + 1
        return f"({f.numerator}./{f.denominator}.)"

    new = EXPR.sub(lambda m: m.group(1) + LIT.sub(one, m.group(2)) + m.group(3), txt)
    return new, done, left


def main(argv):
    if not argv or argv[0].startswith("-"):
        print(__doc__)
        return 2
    d, check = argv[0], "--check" in argv[1:]
    bad = 0
    for name in FILES:
        p = os.path.join(d, name)
        if not os.path.exists(p):
            continue
        txt = open(p).read()
        new, done, left = rewrite_text(txt)
        n = sum(done.values())
        if check:
            # lorentz.py is read by ALOHA, which makes the fractions exact itself
            if name != "lorentz.py":
                bad += n + len(left)
            print(f"{name}: {n + len(left)} literal(s) MadGraph would truncate"
                  + (" (ALOHA writes them exactly)" if name == "lorentz.py" and n + len(left) else ""))
            continue
        if new != txt:
            tmp = p + ".tmp"
            open(tmp, "w").write(new)
            os.replace(tmp, p)
        kinds = ", ".join(f"{fr} x{c}" for (lit, fr), c in sorted(done.items(), key=lambda kv: -kv[1]))
        print(f"{name}: {n} literal(s) written as fractions" + (f" ({kinds})" if kinds else ""))
        if left:
            bad += len(left)
            print(f"{name}: left as written, no fraction q <= {MAXDEN}: {sorted(set(left))}")
    if check and bad:
        print(f"exact_literals: {bad} literal(s) in couplings or parameters that MadGraph prints to "
              "seven digits; run validate/exact_literals.py on the model")
        return 1
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
