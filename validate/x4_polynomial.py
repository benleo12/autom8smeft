#!/usr/bin/env python3
"""Are two forms of each operator of X^4 the same polynomial in the field strengths?

    python3 validate/x4_polynomial.py <out.json>      needs numpy

What it does.  It reads what validate/x4_polynomial.wls wrote and evaluates both forms of each pair at
random antisymmetric tensors F^a_{mu nu}, W^I_{mu nu} and B_{mu nu}, one set of independent numbers for each
component, contracting Lorentz indices with the metric and colour and SU(2) indices with a delta.

When to reach for it.  For X^4, in place of validate/fr_compare.wls, which cannot reach its seven- and
eight-gluon vertices.

What the output means.  One line per pair with the size of the difference relative to the size of the terms,
and PASS when it is below 1e-10 at three random points.  Then the control: each form is compared with the other
form of every other pair, and such a comparison must differ, since the operators are independent.  The last line
reads OVERALL: PASS only if every pair agrees and every control differs.  Otherwise the status is 1.  This test
takes the two sides to be polynomials in one FS.  It does not test the expansion of FS in gauge fields, which is
common to both and is tested with the other classes by validate/fr_compare.wls.

Believe it when the control differs throughout, as it must, and when the pairs of X^4 that FeynRules can reach
agree with validate/fr_compare.wls as well.
"""
import json
import string
import sys

import numpy as np

ETA = np.diag([1.0, -1.0, -1.0, -1.0])


def levi(n):
    e = np.zeros((n,) * n)
    import itertools
    for p in itertools.permutations(range(n)):
        sign = 1
        for i in range(n):
            for j in range(i + 1, n):
                if p[i] > p[j]:
                    sign = -sign
        e[p] = sign
    return e


EPS4, EPS3 = levi(4), levi(3)
GELL = np.zeros((8, 3, 3), complex)
for k, (i, j, v) in enumerate([(0, 1, 1), (0, 1, -1j), (0, 0, 1), (0, 2, 1), (0, 2, -1j), (1, 2, 1), (1, 2, -1j)]):
    GELL[k, i, j] = v
    GELL[k, j, i] = np.conj(v)
GELL[2] = np.diag([1, -1, 0])
GELL[7] = np.diag([1, 1, -2]) / np.sqrt(3)
T = GELL / 2
F3 = np.real(-2j * (np.einsum("aij,bjk,cki->abc", T, T, T) - np.einsum("bij,ajk,cki->abc", T, T, T)))
D3 = np.real(2 * (np.einsum("aij,bjk,cki->abc", T, T, T) + np.einsum("bij,ajk,cki->abc", T, T, T)))
assert abs(F3[0, 1, 2] - 1) < 1e-12 and abs(D3[0, 0, 7] - 1 / np.sqrt(3)) < 1e-12


def tensors(rng):
    def anti(*shape):
        x = rng.normal(size=shape + (4, 4))
        return x - np.swapaxes(x, -1, -2)
    return {"G": anti(8), "Wi": anti(3), "B": anti()}


def term_value(term, fields):
    letters = iter(string.ascii_letters)
    names, seen_lor, arrays, subs = {}, {}, [], []

    def letter(idx):
        if idx not in names:
            names[idx] = next(letters)
        return names[idx]

    def lorentz(idx):
        """A Lorentz index occurs twice in a term: the second occurrence gets a letter of its own and a metric."""
        if idx in seen_lor:
            other = next(letters)
            arrays.append(ETA)
            subs.append(seen_lor.pop(idx) + other)
            return other
        seen_lor[idx] = next(letters)
        return seen_lor[idx]

    for fac in term["f"]:
        head, args = fac[0], fac[1:]
        if head == "FS":
            name, rest = args[0], args[1:]
            arr = fields[name]
            mu, nu = lorentz(rest[0]), lorentz(rest[1])
            if name == "B":
                arrays.append(arr)
                subs.append(mu + nu)
            elif rest[2].isdigit():
                arrays.append(arr[int(rest[2]) - 1])
                subs.append(mu + nu)
            else:
                arrays.append(arr)
                subs.append(letter(rest[2]) + mu + nu)
        elif head == "Eps" and len(args) == 4:
            arrays.append(EPS4)
            subs.append("".join(lorentz(a) for a in args))
        elif head in ("Eps", "f", "d"):
            arr = {"Eps": EPS3, "f": F3, "d": D3}[head]
            sub = ""
            for k, a in enumerate(args):
                if a.isdigit():
                    arr = np.take(arr, int(a) - 1, axis=len(sub))
                else:
                    sub += letter(a)
            arrays.append(arr)
            subs.append(sub)
        elif head == "delta":
            if all(a.isdigit() for a in args):
                if args[0] != args[1]:
                    return 0.0
            else:
                raise SystemExit(f"a delta of two dummies should have been summed: {fac}")
        else:
            raise SystemExit(f"unknown factor {fac}")
    if seen_lor:
        raise SystemExit(f"a Lorentz index occurs once: {sorted(seen_lor)}")
    value = np.einsum(",".join(subs) + "->", *arrays, optimize="greedy")
    return complex(term["re"], term["im"]) * complex(value)


def value(terms, fields):
    vals = [term_value(t, fields) for t in terms]
    return sum(vals), sum(abs(v) for v in vals)


def main():
    if len(sys.argv) < 2:
        print("usage: validate/x4_polynomial.py <out.json>, the file validate/x4_polynomial.wls writes", file=sys.stderr)
        sys.exit(2)
    pairs = json.load(open(sys.argv[1]))
    rngs = [np.random.default_rng(s) for s in (11, 22, 33)]
    points = [tensors(r) for r in rngs]
    refs, gens, ok = [], [], True
    for p in pairs:
        r = [value(p["ref_terms"], F) for F in points]
        g = [value(p["gen_terms"], F) for F in points]
        rel = max(abs(a[0] - p["norm"] * b[0]) / max(a[1], abs(p["norm"]) * b[1], 1e-300) for a, b in zip(r, g))
        size = max(a[1] for a in r)
        good = rel < 1e-10 and size > 0
        ok = ok and good
        print(f"{'PASS' if good else 'FAIL'}  {p['ref']:12s} {p['gen']:9s} terms {len(p['ref_terms']):4d} {len(p['gen_terms']):4d}  relative difference {rel:.1e}")
        refs.append([a[0] for a in r])
        gens.append([p["norm"] * b[0] for b in g])
    same = []
    for i, a in enumerate(refs):
        for j, b in enumerate(gens):
            if i != j and max(abs(x - y) for x, y in zip(a, b)) < 1e-8 * max(abs(a[0]), abs(b[0])):
                same.append((pairs[i]["ref"], pairs[j]["gen"]))
    print(f"control: {len(pairs) * (len(pairs) - 1)} comparisons of different operators, {len(same)} agree {same[:6]}")
    print("OVERALL:", "PASS" if ok and not same else "FAIL")
    return 0 if ok and not same else 1


if __name__ == "__main__":
    sys.exit(main())
