#!/usr/bin/env python3
"""The normalisation of the symmetric SU(3) symbol d^{ABC} as MadGraph reads it from the UFO.

    python3.11 validate/check_d_symbol.py        ($MG5_DIR points to MadGraph)

The UFO writes d^{ABC} and f^{ABC} as the symbols d(a,b,c) and f(a,b,c) in its colour structures,
and MadGraph's colour algebra gives them their values.  The model assumes the standard
normalisation, {T^A, T^B} = delta^{AB}/N + d^{ABC} T^C with Tr(T^A T^B) = delta^{AB}/2, which
validate/check_colour_norm.wls checks on the colour tensors of the vertex computation.  For that
normalisation d^{ABC} d^{ABC} = (N^2 - 1)(N^2 - 4)/N = 40/3 and f^{ABC} f^{ABC} = N (N^2 - 1) = 24,
and this script evaluates both contractions with MadGraph's own colour algebra.
"""
import os
import sys
from fractions import Fraction

MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))


def main():
    sys.path.insert(0, MG)
    import madgraph.core.color_algebra as ca

    def full(*objs):
        cf = ca.ColorFactor([ca.ColorString(list(objs))]).full_simplify()
        return sum(Fraction(cs.coeff) * Fraction(3) ** cs.Nc_power for cs in cf)

    dd, ff = full(ca.d(1, 2, 3), ca.d(1, 2, 3)), full(ca.f(1, 2, 3), ca.f(1, 2, 3))
    ok = dd == Fraction(40, 3) and ff == 24
    print(f"d^ABC d^ABC = {dd} (standard 40/3), f^ABC f^ABC = {ff} (standard 24): {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
