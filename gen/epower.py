"""
gen/epower.py  --  the energy-enhanced (lambda) power counting, as a user-facing tool.

A port of ``Epower_count.nb``, the Mathematica notebook of the Assi-Martin counting paper,
so that the same numbers are available from ``./dim8 count`` and from Python without
Mathematica.  It reproduces every evaluated call of the notebook.  The two notebook
functions are

    CalculatePowersRegime1[D, H, psi, F, n]                 -> leading (p, q, lambdaExp)
    CalculateSubleadingPowersRegime1[D, H, psi, F, n]       -> the leading and subleading vertices, in k
    CalculateSubleadingPowersRegime1[D, H, psi, F, n, exp]  -> filtered on one exponent

and the argument order is kept: (N_D, N_H, N_psi, N_X, n).  Regime 1 is
Lambda >> E >> v with (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1).

    Dop     = 3/2 psi + H + 2 F + D - 4           operator dimension minus four
    p_min   = max(H + psi + F - n, 0)             fields that must be vev'd for n legs
    q_max   = Dop + 4 - n - p_min                 powers of E at p = p_min
    k_max   = H - max(n - psi - 2F - D, 0)        (0 if H = 0)
    vertices (p_min + k, q_max - k),  k = 0 .. min(k_max - p_min, q_max)
    lambda  = 3 Dop - 2 q - p

The notebook is reproduced, with the number of legs and the range of k fixed as follows.

* A vertex has  max(psi + F + HD, 3) <= n <= psi + H + 2F + D  legs, where HD is the number of
  Higgs fields that carry a derivative (a covariant derivative of the vacuum is a gauge boson,
  so such a field leaves a leg either way), smallest over the terms of the class.  The terms
  with fewer than three legs are the vacuum energy, the tadpole and the two-point terms, which
  shift masses and normalisations, so none of them is a vertex (eq:legs of the paper).  The
  notebook has HD = 0 and no floor, which changes five of its eight calls at n = 2 (the other three
  already have no vertex).  The leading function only checks the lower bound, the subleading one
  checks both, as in the notebook.
* k_max is the largest number of Higgs fields that can sit at the vacuum when the vertex has n
  legs: of the n legs, at least n - psi - 2F - D must be Higgs fields, since the fermions give one
  leg each, a field strength at most two and a covariant derivative one more gauge boson.  So
  p = p_min + k cannot exceed k_max, and k runs to min(k_max - p_min, q_max).  A vertex with
  p > k_max would have fewer than n legs, for example psi^2H^4D at n = 4 with p = 4: two fermions
  and the gauge boson of its derivative are three legs.

Leg counting allows the (p, q) of this range and no others, but some of them have no vertex in any
operator of a class, by C, by the antisymmetry of a field strength or, in a unitary-gauge model,
because the Goldstone component carries them (validate/check_legs.py, which checks the range
against the vertices of the released model).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

import basis as _basis

# (N_D, N_H, N_psi, N_X) for every dimension-eight class, notebook order and spelling
DIM8_CLASSES: Dict[str, Tuple[int, int, int, int]] = {
    "X^4": (0, 0, 0, 4), "H^8": (0, 8, 0, 0), "H^6D^2": (2, 6, 0, 0), "H^4D^4": (4, 4, 0, 0),
    "X^3H^2": (0, 2, 0, 3), "X^2H^4": (0, 4, 0, 2), "X^2H^2D^2": (2, 2, 0, 2), "XH^4D^2": (2, 4, 0, 1),
    "psi^2X^2H": (0, 1, 2, 2), "psi^2XH^3": (0, 3, 2, 1), "psi^2H^2D^3": (3, 2, 2, 0),
    "psi^2H^5": (0, 5, 2, 0), "psi^2H^4D": (1, 4, 2, 0),
    "psi^2X^2D": (1, 0, 2, 2), "psi^2XH^2D": (1, 2, 2, 1),
    "psi^2XHD^2": (2, 1, 2, 1), "psi^2H^3D^2": (2, 3, 2, 0), "psi^4H^2": (0, 2, 4, 0),
    "psi^4X": (0, 0, 4, 1), "psi^4HD": (1, 1, 4, 0), "psi^4D^2": (2, 0, 4, 0),
}
# psi^4H^2 has the field content (0,2,4,0).  The notebook's call for this class passes
# (0,4,2,0), the field content of psi^2H^4, so a comparison with the notebook's output uses
# the notebook's own arguments.

DIM6_CLASSES: Dict[str, Tuple[int, int, int, int]] = {
    "H^6": (0, 6, 0, 0), "H^4D^2": (2, 4, 0, 0), "X^2H^2": (0, 2, 0, 2), "psi^2H^3": (0, 3, 2, 0),
    "X^3": (0, 0, 0, 3), "psi^2XH": (0, 1, 2, 1), "psi^2H^2D": (1, 2, 2, 0), "psi^4": (0, 0, 4, 0),
}

# Higgs fields that carry a derivative, smallest over the terms of the class, from
# gen/operators.py; validate/check_legs.py recomputes them and checks the window against the vertices
# of the released model.  Class 11 depends on the basis (gen/basis.py): every Higgs field of its
# operators carries a derivative in the default basis, and one of the two in the Murphy basis.
DIM8_HD: Dict[str, int] = {
    "X^4": 0, "H^8": 0, "H^6D^2": 2, "H^4D^4": 4, "X^3H^2": 0, "X^2H^4": 0, "X^2H^2D^2": 2,
    "XH^4D^2": 2, "psi^2X^2H": 0, "psi^2XH^3": 0, "psi^2H^2D^3": 1 if _basis.basis() == "murphy" else 2, "psi^2H^5": 0,
    "psi^2H^4D": 1, "psi^2X^2D": 0, "psi^2XH^2D": 1, "psi^2XHD^2": 1, "psi^2H^3D^2": 2,
    "psi^4H^2": 0, "psi^4X": 0, "psi^4HD": 0, "psi^4D^2": 0,
}
# Q_{H box} = (H^dag H) box (H^dag H) puts both derivatives on one Higgs field in one of its terms
DIM6_HD: Dict[str, int] = {"H^4D^2": 1, "psi^2H^2D": 1}

NO_LEGS = "Operator can't generate this number of legs"


def higgs_with_derivative(name: str) -> int:
    """HD of a named class, and 0 for an explicit field content, which gives the weaker bound."""
    return DIM8_HD.get(name, DIM6_HD.get(name, 0))


def op_dimension(D: int, H: int, psi: int, F: int) -> int:
    d = Fraction(3, 2) * psi + H + 2 * F + D - 4
    if d.denominator != 1:
        raise ValueError("odd number of fermion fields")
    return int(d)


@dataclass
class Leading:
    p: int
    q: int
    lambdaExp: int

    def as_dict(self):
        return {"p": self.p, "q": self.q, "lambdaExp": self.lambdaExp}


@dataclass
class Tower:
    OperatorDimension: int
    pMin: int
    qMax: int
    lambdaExp: int
    Results: List[Dict[str, int]] = field(default_factory=list)

    def as_dict(self):
        return {"OperatorDimension": self.OperatorDimension, "pMin": self.pMin, "qMax": self.qMax,
                "lambdaExp": self.lambdaExp, "Results": self.Results}


def leading(D: int, H: int, psi: int, F: int, n: int, HD: int = 0):
    """CalculatePowersRegime1.  Returns Leading, or the notebook's message string."""
    Dop = op_dimension(D, H, psi, F)
    p = max(H + psi + F - n, 0)
    q = Dop + (4 - n) - p
    lam = 3 * Dop - 2 * q - p
    if max(psi + F + HD, 3) <= n:
        return Leading(p, q, lam)
    return NO_LEGS


def tower(D: int, H: int, psi: int, F: int, n: int, target: Optional[int] = None, HD: int = 0):
    """CalculateSubleadingPowersRegime1, both arities, with the range of k corrected (see the
    module docstring): the (p, q) that leg counting allows at n legs, the leading entry at k = 0 and
    the k-th subleading entry with k more Higgs fields at the vacuum, k powers of lambda higher.
    Some entries vanish by C or by gauge structure.

    With ``target`` given, behaves like the six-argument notebook function: returns the
    full list if any entry has that exponent, else a "No match" string.  (The notebook
    filters and then returns the unfiltered list; that quirk is reproduced.)
    """
    Dop = op_dimension(D, H, psi, F)
    pMin = max(H + psi + F - n, 0)
    qMax = Dop + (4 - n) - pMin
    lam = 3 * Dop - 2 * qMax - pMin
    kMax = (H - max(n - psi - 2 * F - D, 0)) if H > 0 else 0   # the largest p, not the largest k
    if not (max(psi + F + HD, 3) <= n <= psi + H + 2 * F + D):
        return NO_LEGS
    results = []
    for k in range(0, min(kMax - pMin, qMax) + 1):
        p, q = pMin + k, qMax - k
        row = {"k": k, "p": p, "q": q}
        if target is not None:
            row["lambdaExp"] = 3 * Dop - 2 * q - p
        results.append(row)
    if target is not None:
        if not any(r["lambdaExp"] == target for r in results):
            return f"No match found for requested exponent {target}"
        return results
    return Tower(Dop, pMin, qMax, lam, results)


def resolve(spec: str) -> Tuple[str, Tuple[int, int, int, int]]:
    """A class name ("psi^2H^2D^3") or an explicit "D,H,psi,F" tuple."""
    s = spec.strip()
    if s in DIM8_CLASSES:
        return s, DIM8_CLASSES[s]
    if s in DIM6_CLASSES:
        return s, DIM6_CLASSES[s]
    parts = [int(x) for x in s.replace(" ", "").split(",")]
    if len(parts) != 4:
        raise ValueError(f"{spec!r}: give a class name or four integers D,H,psi,F")
    return s, tuple(parts)  # type: ignore[return-value]


def table(classes: Dict[str, Tuple[int, int, int, int]], n: int) -> str:
    lines = [f"{'class':14s} {'(D,H,psi,F)':13s} {'p':>2s} {'q':>2s} {'lam':>4s}   leading and subleading vertices (p,q) with lambda exponent"]
    for name, args in classes.items():
        t = tower(*args, n, HD=higgs_with_derivative(name))
        if isinstance(t, str):
            lines.append(f"{name:14s} {str(args):13s}   cannot make {n} legs")
            continue
        tw = "  ".join(f"({r['p']},{r['q']})λ^{3 * t.OperatorDimension - 2 * r['q'] - r['p']}" for r in t.Results)
        lines.append(f"{name:14s} {str(args):13s} {t.pMin:2d} {t.qMax:2d} {t.lambdaExp:4d}   {tw}")
    return "\n".join(lines)
