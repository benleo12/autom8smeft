#!/usr/bin/env python3
"""Every linear dimension-six vertex of models/dim68_is against SMEFTsim's {alpha, MZ, GF} model.

    python3 validate/dim6_vs_smeftsim.py <SMEFTsim U35 alphaScheme UFO> [--ours models/dim68_is]
                                         [--coeffs cHWB,cll1,...] [--tol 1e-6] [--show 5]

The reference is SMEFTsim_U35_alphaScheme_UFO, version 3.0.2 (github.com/SMEFTsim/SMEFTsim, commit
e4cf6f9).  It is not shipped here; download it and give its path.

Both models are read as text with read_model of validate/index_vs_ufo.py, at the same Standard
Model inputs: SMEFTsim's defaults, with alpha entering ours as aEWM1 = 1/aEW, the CKM matrix the
unit matrix in both (our model carries only the Cabibbo angle, SMEFTsim the Wolfenstein form), and
Lambda = 1 TeV.  For each dimension-six coefficient the derivative of every coupling at zero is
taken, from symmetric differences combined so that the quadratic and cubic terms cancel: our model
carries the dimension-six squares of the input relations, SMEFTsim stops at 1/Lambda^2, and the two
must agree on the linear term only.  A real coefficient is probed by name.  A complex one is probed
along its real and its imaginary direction, through the complex combination both models build (ours
C = Abs exp(i Ph), SMEFTsim C = Re + i Im), set to eps and to i eps.

Each vertex is then contracted completely: colour indices with random colour vectors, Lorentz
indices with random polarisation vectors, spinor indices with random spinors, and the momenta
random and conserved, the same for a given particle in both models, summed over the orderings of
identical particles with the sign of the permutation for fermions.  The number obtained does not
depend on how a model splits its vertex into Lorentz structures, colour bases or Dirac projectors,
so two models agree on a vertex exactly when these numbers agree.  Two random draws are taken.

Outcomes per coefficient, direction and vertex (keyed by sorted PDG codes):
  agree          the two derivatives agree to --tol (relative) at both draws
  differ         they do not.  Error
  only ours      SMEFTsim's derivative vanishes.  Error
  only SMEFTsim  ours vanishes.  Error
A derivative counts as vanishing below 1e-9 of the largest one of that coefficient.  SMEFTsim's
coefficients that our model lacks are listed and not compared.  The exit status is 1 when anything
differs.

Believe it when: a model compared with itself agrees on every vertex, and a coefficient planted with
the wrong sign in one model (--plant cHWB) is reported as differing on every vertex it moves.
"""
from __future__ import annotations

import collections
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
import index_vs_ufo as IV  # noqa: E402

from vertex_contract import compare, response, vertex_numbers  # noqa: E402


# ------------------------------------------------------------------ the comparison
def matched_inputs(ours, smeftsim):
    """Our inputs and SMEFTsim's, at SMEFTsim's defaults: alpha as aEWM1 = 1/aEW, the unit CKM
    matrix, Lambda = 1 TeV."""
    def defaults(path):
        txt = open(os.path.join(path, "parameters.py")).read()
        return {n: v for n, nat, v in re.findall(
            r"(\w+) = Parameter\(name = '\w+',\s*nature = '(external)',\s*type = '\w+',\s*value = ([^,]+),", txt)}
    a, b = defaults(ours), defaults(smeftsim)
    common = {n: float(b[n]) for n in a if n in b and not n.startswith("c")}
    mine = dict(common, aEWM1=1 / float(b["aEW"]) if "aEW" in b else float(b["aEWM1"]), cabi=0.0, Lam6=1000.0)
    theirs = dict(common, CKMlambda=0.0, CKMA=0.0, CKMrho=0.0, CKMeta=0.0, LambdaSMEFT=1000.0,
                  linearPropCorrections=0.0, cabi=0.0, Lam6=1000.0)
    return mine, theirs


def probes(ours, smeftsim):
    """[(label, [(our coefficient, direction)], [(SMEFTsim coefficient, direction)])] and the
    SMEFTsim coefficients our model lacks."""
    def coeffs(path, blocks):
        txt = open(os.path.join(path, "parameters.py")).read()
        return [n for n, blk in re.findall(r"(\w+) = Parameter\(name = '\w+',\s*nature = 'external',.*?lhablock = '(\w+)'",
                                           txt, re.S) if blk in blocks]
    a = set(coeffs(ours, {"DIM6"})) - {"Lam6"}
    # a reference with our own conventions (a model compared with itself) has a DIM6 block
    b = set(coeffs(smeftsim, {"SMEFT", "SMEFTcpv"})) or set(coeffs(smeftsim, {"DIM6"})) - {"Lam6"}
    def internal(path):
        txt = open(os.path.join(path, "parameters.py")).read()
        return set(re.findall(r"(\w+) = Parameter\(name = '\w+',\s*nature = 'internal'", txt))
    ia, ib = internal(ours), internal(smeftsim)
    out, used = [], set()
    for n in sorted(a):
        if n.endswith("Ph"):
            continue
        if n.endswith("Abs"):
            # A complex coefficient moves along its real and its imaginary direction.  A model's
            # couplings may carry the complex combination (ours: C = Abs exp(i Ph)) or the parts
            # (SMEFTsim: Re and Im), each a separate leaf of read_model, so the derivative along a
            # direction is the sum of the partial ones over every spelling, the chain rule:
            # along Re, dC = eps, dRe = eps, dAbs = eps; along Im, dC = i eps, dIm = eps.
            base = n[:-3]
            if (base in ia or base + "Re" in b) and (base in ib or base + "Re" in b or base + "Abs" in b):
                re_dir = [(base, 1.0), (base + "Re", 1.0), (base + "Abs", 1.0)]
                im_dir = [(base, 1j), (base + "Im", 1.0)]
                out += [(base + " Re", re_dir, re_dir), (base + " Im", im_dir, im_dir)]
                used |= {base + "Re", base + "Im", base + "Abs", base + "Ph"}
            continue
        if n in b:
            out.append((n, [(n, 1.0)], [(n, 1.0)]))
            used.add(n)
    return out, sorted(b - used)


def main(argv) -> int:
    if len(argv) < 2 or argv[1].startswith("-"):
        print(__doc__)
        return 2
    smeftsim = os.path.abspath(argv[1])
    ours = os.path.abspath(argv[argv.index("--ours") + 1]) if "--ours" in argv else os.path.join(ROOT, "models", "dim68_is")
    tol = float(argv[argv.index("--tol") + 1]) if "--tol" in argv else 1e-6
    show = int(argv[argv.index("--show") + 1]) if "--show" in argv else 5
    plant = argv[argv.index("--plant") + 1] if "--plant" in argv else None
    P, missing = probes(ours, smeftsim)
    if "--coeffs" in argv:
        keep = set(argv[argv.index("--coeffs") + 1].split(","))
        P = [p for p in P if p[0].split()[0] in keep]
    mine, theirs = matched_inputs(ours, smeftsim)
    print(f"ours     {ours}\nSMEFTsim {smeftsim}\n{len(P)} coefficient directions compared; "
          f"SMEFTsim coefficients our model lacks: {', '.join(missing) or 'none'}")
    ra = IV.read_model(ours, inputs=mine, only={c for p in P for c, _ in p[1]})
    rb = IV.read_model(smeftsim, inputs=theirs, only={c for p in P for c, _ in p[2]})
    for lab, r in (("ours", ra), ("SMEFTsim", rb)):
        if r["failed"]:
            print(f"{lab}: {len(r['failed'])} couplings could not be evaluated, e.g. {r['failed'][:3]}")
    need = lambda r: {g for (g, n, v), d in r["resp"].items() if d}  # noqa: E731
    na, nb = vertex_numbers(ra["entries"], need(ra)), vertex_numbers(rb["entries"], need(rb))

    bad = 0
    summary = []
    for lab, sa_, sb_ in P:
        A = response(ra, na, sa_, -1.0 if plant and lab.split()[0] == plant else 1.0)
        B = response(rb, nb, sb_)
        c, rows = compare(A, B, tol)
        cnt = collections.Counter({"agree": c["agree"], "differ": c["differ"],
                                   "only ours": c["only first"], "only SMEFTsim": c["only second"]})
        bad += cnt["differ"] + cnt["only ours"] + cnt["only SMEFTsim"]
        summary.append((lab, cnt))
        print(f"{lab:14s} agree {cnt['agree']:4d}   differ {cnt['differ']:3d}   only ours {cnt['only ours']:3d}"
              f"   only SMEFTsim {cnt['only SMEFTsim']:3d}")
        for key, what, sa, sb, q in rows[:show]:
            what = {"only first": "only ours", "only second": "only SMEFTsim"}.get(what, what)
            what += f", ratio {1 / q:.6g}" if q else ""
            print(f"    {','.join(map(str, key)):28s} {what}   |ours| {sa:.3e}  |SMEFTsim| {sb:.3e}")
    tot = collections.Counter()
    for _, c in summary:
        tot.update(c)
    print(f"\n{len(P)} directions, {sum(tot.values())} vertex comparisons: agree {tot['agree']}, differ "
          f"{tot['differ']}, only ours {tot['only ours']}, only SMEFTsim {tot['only SMEFTsim']}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
