"""
validate/structural.py  --  V1, V2: structural checks on DSL operators, no Mathematica.

V1  mass dimension 8, every non-flavour index appears exactly twice (done in Operator.__post_init__,
    re-run here so the report is explicit)
V2  gauge invariance by construction:
      * hypercharge of every term sums to zero,
      * SU(2) doublet balance: (#upper - #lower) fundamental indices carried by fields is
        compensated only by invariant tensors (eps_{jk} absorbs two uppers, eps^{jk} two lowers,
        tau and delta are balanced),
      * SU(3) triplet balance likewise (eps_{abc} absorbs three uppers),
      * every Lorentz index pair is contracted (already in V1).
    Together with "all tensors are invariant tensors" this is equivalent to gauge invariance.

Usage:   python3 validate/structural.py gen/ops/<module>.py   (module must define OPS: list[Operator])
"""

from __future__ import annotations

import importlib.util
import json
import sys
from fractions import Fraction
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "gen"))
from dsl import FS, Gamma, H, Operator, Psi, Tensor, Term  # noqa: E402

HYPERCHARGE = {"l": Fraction(-1, 2), "e": Fraction(-1), "q": Fraction(1, 6), "u": Fraction(2, 3), "d": Fraction(-1, 3)}


def hypercharge(term: Term) -> Fraction:
    y = Fraction(0)
    for f in term.factors:
        if isinstance(f, H):
            y += Fraction(-1, 2) if f.dag else Fraction(1, 2)
        elif isinstance(f, Psi):
            y += -HYPERCHARGE[f.name] if f.bar else HYPERCHARGE[f.name]
    return y


def gauge_variance_check(term: Term, kind: str) -> list:
    """Gauge invariance of fundamental-index contractions.

    Every fundamental index carried by a field has a variance: upper for H, psi (doublet or
    triplet), lower for H^dag, psibar.  Generators tau^I_j^k / T^A_a^b have one upper (first)
    and one lower (second) slot.  A contraction is invariant when it pairs an upper with a
    lower index, or when an epsilon tensor contracts indices of equal variance (two for
    eps_{jk}, three for eps_{abc}).  Returns a list of problems."""
    up, down, eps_slots = {}, {}, {}
    for f in term.factors:
        if kind == "su2":
            if isinstance(f, H):
                (down if f.dag else up).setdefault(f.j, []).append("H")
            elif isinstance(f, Psi) and f.su2 is not None:
                (down if f.bar else up).setdefault(f.su2, []).append(f.name)
            elif isinstance(f, Tensor) and f.kind == "tau":
                up.setdefault(f.idx[1], []).append("tau")
                down.setdefault(f.idx[2], []).append("tau")
            elif isinstance(f, Tensor) and f.kind == "epsSU2":
                eps_slots.setdefault(id(f), []).extend(f.idx)
        else:
            if isinstance(f, Psi) and f.col is not None:
                (down if f.bar else up).setdefault(f.col, []).append(f.name)
            elif isinstance(f, Tensor) and f.kind == "T":
                up.setdefault(f.idx[1], []).append("T")
                down.setdefault(f.idx[2], []).append("T")
            elif isinstance(f, Tensor) and f.kind == "epsSU3":
                eps_slots.setdefault(id(f), []).extend(f.idx)
    problems = []
    eps_indices = {i for v in eps_slots.values() for i in v}
    names = set(up) | set(down) | eps_indices
    for n in names:
        nu, nd = len(up.get(n, [])), len(down.get(n, []))
        ne = sum(v.count(n) for v in eps_slots.values())
        if ne == 0 and not (nu == 1 and nd == 1):
            problems.append(f"{kind} index {n}: up={nu} down={nd} (need one of each)")
        if ne == 1 and not (nu + nd == 1):
            problems.append(f"{kind} index {n}: epsilon slot needs exactly one field partner, got up={nu} down={nd}")
        if ne >= 2:
            problems.append(f"{kind} index {n}: contracted between two epsilons")
    for _, idx in eps_slots.items():
        var = []
        for n in idx:
            if n in up:
                var.append("up")
            elif n in down:
                var.append("down")
        if len(set(var)) > 1:
            problems.append(f"{kind} epsilon {idx} contracts mixed variances {var}")
    return problems


def check_operator(op: Operator) -> dict:
    res = {"name": op.name, "wc": op.wc, "ok": True, "problems": []}
    d = op.mass_dimension()
    if d != 8:
        res["ok"] = False
        res["problems"].append(f"mass dimension {d} != 8")
    for i, t in enumerate(op.terms):
        try:
            t.check_contracted()
        except ValueError as e:
            res["ok"] = False
            res["problems"].append(f"term {i}: {e}")
        y = hypercharge(t)
        if y != 0:
            res["ok"] = False
            res["problems"].append(f"term {i}: hypercharge sum {y} != 0")
        for kind in ("su2", "su3"):
            for p in gauge_variance_check(t, kind):
                res["ok"] = False
                res["problems"].append(f"term {i}: {p}")
        # every term of one operator must have the same field content
        if i > 0:
            fc0 = _fc(op.terms[0])
            fci = _fc(t)
            if fc0 != fci:
                res["ok"] = False
                res["problems"].append(f"term {i}: field content {fci} differs from term 0 {fc0}")
    res["field_content"] = op.field_content()
    return res


def _fc(t: Term):
    return dict(
        N_f=sum(isinstance(f, Psi) for f in t.factors),
        N_H=sum(isinstance(f, H) for f in t.factors),
        N_X=sum(isinstance(f, FS) for f in t.factors),
        N_D=sum(len(f.derivs) for f in t.factors if hasattr(f, "derivs")),
    )


def load_ops(path: str):
    spec = importlib.util.spec_from_file_location("opsmod", path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(Path(path).resolve().parent))
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.OPS


if __name__ == "__main__":
    ops = load_ops(sys.argv[1])
    results = [check_operator(o) for o in ops]
    nbad = sum(not r["ok"] for r in results)
    for r in results:
        flag = "ok " if r["ok"] else "BAD"
        print(f"[{flag}] {r['name']:32s} {r['wc']:16s} {r['field_content']}  {'; '.join(r['problems'])}")
    print(f"\n{len(results)} operators, {nbad} with problems")
    out = Path(sys.argv[1]).with_suffix(".structural.json")
    out.write_text(json.dumps(results, indent=1))
    sys.exit(1 if nbad else 0)
