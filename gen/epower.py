"""
gen/epower.py  --  the energy-enhanced (lambda) power counting, as a user-facing tool.

A faithful port of ``Epower_count.nb`` (B. Assi, geosmeft VBF folder), the notebook used
for the Assi-Martin counting paper, so that the same numbers are available from
``./dim8 count`` and from Python without Mathematica.  The two notebook functions are

    CalculatePowersRegime1[D, H, psi, F, n]                 -> leading (p, q, lambdaExp)
    CalculateSubleadingPowersRegime1[D, H, psi, F, n]       -> the whole tower in k
    CalculateSubleadingPowersRegime1[D, H, psi, F, n, exp]  -> filtered on one exponent

and the argument order is kept: (N_D, N_H, N_psi, N_X, n).  Regime 1 is
Lambda >> E >> v with (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1).

    Dop     = 3/2 psi + H + 2 F + D - 4           operator dimension minus four
    p_min   = max(H + psi + F - n, 0)             fields that must be vev'd for n legs
    q_max   = Dop + 4 - n - p_min                 powers of E at p = p_min
    k_max   = H - max(n - psi - 2F - D, 0)        (0 if H = 0)
    tower   = (p_min + k, q_max - k),  k = 0 .. min(k_max, q_max)
    lambda  = 3 Dop - 2 q - p

Two rules from the notebook are reproduced exactly and are worth knowing about.

* Reachability is  psi + F <= n <= psi + H + 2F + D.  The leading function only checks
  the lower bound, the subleading one checks both; this port does the same.
* ``If[pMin == kMax, kMax = 0]``: when every Higgs that could be traded for a vev is
  already vev'd at leading order, the subleading tower is empty.  This is the correct
  rule (confirmed BA 2026-08-28); gen/lambda_counting.py now applies it too.  It changes
  the subleading towers of 16 (class, n) combinations at dimension eight and no
  leading-order result.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from fractions import Fraction
from typing import Dict, List, Optional, Tuple

# (N_D, N_H, N_psi, N_X) for every dimension-eight class, notebook order and spelling
DIM8_CLASSES: Dict[str, Tuple[int, int, int, int]] = {
    "X^4": (0, 0, 0, 4), "H^8": (0, 8, 0, 0), "H^6D^2": (2, 6, 0, 0), "H^4D^4": (4, 4, 0, 0),
    "X^3H^2": (0, 2, 0, 3), "X^2H^4": (0, 4, 0, 2), "X^2H^2D^2": (2, 2, 0, 2), "XH^4D^2": (2, 4, 0, 1),
    "psi^2X^2H": (0, 1, 2, 2), "psi^2XH^3": (0, 3, 2, 1), "psi^2H^2D^3": (3, 2, 2, 0),
    "psi^2H^5": (0, 5, 2, 0), "psi^2H^4D": (1, 4, 2, 0),
    # Murphy's class 14.  It was missing from the port until 2026-09-26, so `./dim8 count`
    # printed 20 classes and `resolve("psi^2X^2D")` failed; the per-term evaluation, which
    # reads the field content out of the catalogue rather than this table, was unaffected.
    "psi^2X^2D": (1, 0, 2, 2), "psi^2XH^2D": (1, 2, 2, 1),
    "psi^2XHD^2": (2, 1, 2, 1), "psi^2H^3D^2": (2, 3, 2, 0), "psi^4H^2": (0, 2, 4, 0),
    "psi^4X": (0, 0, 4, 1), "psi^4HD": (1, 1, 4, 0), "psi^4D^2": (2, 0, 4, 0),
}
# The notebook listed psi^4H^2 with the field content of psi^2H^4, (0,4,2,0); corrected
# here to (0,2,4,0) (confirmed typo, BA 2026-08-28).  tests/test_epower.py still
# re-evaluates the notebook's own call with its original arguments.

DIM6_CLASSES: Dict[str, Tuple[int, int, int, int]] = {
    "H^6": (0, 6, 0, 0), "H^4D^2": (2, 4, 0, 0), "X^2H^2": (0, 2, 0, 2), "psi^2H^3": (0, 3, 2, 0),
    "X^3": (0, 0, 0, 3), "psi^2XH": (0, 1, 2, 1), "psi^2H^2D": (1, 2, 2, 0), "psi^4": (0, 0, 4, 0),
}

NO_LEGS = "Operator can't generate this number of legs"


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


def leading(D: int, H: int, psi: int, F: int, n: int):
    """CalculatePowersRegime1.  Returns Leading, or the notebook's message string."""
    Dop = op_dimension(D, H, psi, F)
    p = max(H + psi + F - n, 0)
    q = Dop + (4 - n) - p
    lam = 3 * Dop - 2 * q - p
    if psi + F <= n:
        return Leading(p, q, lam)
    return NO_LEGS


def tower(D: int, H: int, psi: int, F: int, n: int, target: Optional[int] = None):
    """CalculateSubleadingPowersRegime1, both arities.

    With ``target`` given, behaves like the six-argument notebook function: returns the
    full tower if any entry has that exponent, else a "No match" string.  (The notebook
    filters and then returns the unfiltered list; that quirk is reproduced.)
    """
    Dop = op_dimension(D, H, psi, F)
    pMin = max(H + psi + F - n, 0)
    qMax = Dop + (4 - n) - pMin
    lam = 3 * Dop - 2 * qMax - pMin
    kMax = (H - max(n - psi - 2 * F - D, 0)) if H > 0 else 0
    if pMin == kMax:
        kMax = 0
    if not (psi + F <= n <= psi + H + 2 * F + D):
        return NO_LEGS
    results = []
    for k in range(0, min(kMax, qMax) + 1):
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
    lines = [f"{'class':14s} {'(D,H,psi,F)':13s} {'p':>2s} {'q':>2s} {'lam':>4s}   tower (p,q) with lambda exponent"]
    for name, args in classes.items():
        t = tower(*args, n)
        if isinstance(t, str):
            lines.append(f"{name:14s} {str(args):13s}   cannot make {n} legs")
            continue
        tw = "  ".join(f"({r['p']},{r['q']})λ^{3 * t.OperatorDimension - 2 * r['q'] - r['p']}" for r in t.Results)
        lines.append(f"{name:14s} {str(args):13s} {t.pMin:2d} {t.qMax:2d} {t.lambdaExp:4d}   {tw}")
    return "\n".join(lines)
