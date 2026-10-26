#!/usr/bin/env python3
"""The dimension-eight vertices of models/dim8_mw against the Murphy-basis UFO of Matchete.

    python3 validate/vs_matchete_ufo.py <ufo_murphy_nf5_mW> [--ours models/dim8_mw] [--classes 1,2,...]
                                        [--coeffs c8H8,...] [--tol 1e-6] [--show 4]

The reference is the dimension-eight UFO of Hourtz et al. in the Matchete model database
(gitlab.com/matchete/model-database, UFO-models/SMEFT_Murphy/ufo_murphy_nf5_mW, commit 738e511),
written in "a modified version of Murphy's basis", five flavours and the {M_W, M_Z, G_F} scheme,
the scheme of dim8_mw.  It is not shipped here; download it and give its path.

Pairing.  Our coefficient c8<stem>x<k> (c8<stem> for a class with one operator) is theirs
c<stem><k> (c<stem>).  Their fermionic coefficients carry flavour indices: c<stem><k>_pp for a
bilinear, and for four fermions c<stem><k>_ppss and the crossed c<stem><k>_pssp.  Our
flavour-universal coefficient identifies p with r and s with t, so it is all of their entries with
p = r (and s = t) at once, and the derivative along it is the sum of the derivatives along those
entries; the crossed entries are another flavour structure and are left at zero.  Their coefficients carry the scale, ours c/Lam^4, so
theirs are divided by Lam^4 with Lam = 1 TeV.  Their model has no operator of the classes that flip
chirality (psi^2X^2H, psi^2XH^3, psi^2H^5, psi^2XHD^2, psi^2H^3D^2 and parts of psi^4H^2,
psi^4HD and psi^4D^2), so those coefficients are listed and not compared.

The inputs are theirs: M_W, M_Z, G_F, alpha_s, m_h, m_t, the top and bottom Yukawas and the widths,
the other fermions massless, no CKM mixing.  The vertices are compared as in
validate/dim6_vs_smeftsim.py (validate/vertex_contract.py): the derivative of every coupling at
zero, every vertex contracted completely with the same external state in both models.  Since
their basis is "modified", an operator may differ from ours by a normalisation; a ratio that is
the same on every vertex of the operator is reported as one, apart from a disagreement.

Outcomes per coefficient: agree, agree up to a factor (the factor printed), differ, only ours,
only theirs.  The exit status is 1 when anything differs or is found in one model only.

Believe it when: the Standard Model vertices of the two models agree once each boson field of
theirs is given its sign (printed first; their covariant derivative has the opposite sign of the
gauge coupling), and a sign planted on one coefficient of ours (--plant c8H8) is reported as a
factor -1 on every vertex that coefficient moves.

The vertices are evaluated in Python, so what happens to a coupling on its way into MadGraph's
Fortran is out of reach here, and so is the question whether a difference off shell is physics:
for both, compare squared matrix elements compiled by MadGraph.
"""
from __future__ import annotations

import collections
import json
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
import index_vs_ufo as IV  # noqa: E402
from vertex_contract import compare, moved_beyond, response, vertex_numbers  # noqa: E402

LAM = 1000.0
MAXLEGS = 4       # their UFO holds three- and four-point vertices only
BOSONS = (21, 22, 23, 24, 25)
# Standard Model vertices that fix the relative sign of each boson field between the two models
SM_REFERENCE = [(-11, 11, 22), (-11, 11, 23), (-12, 12, 23), (-2, 2, 21), (-2, 2, 22), (-2, 2, 23),
                (-1, 1, 23), (-24, 24, 22), (-24, 24, 23), (21, 21, 21), (-24, 24, 25), (23, 23, 25),
                (25, 25, 25), (-6, 6, 25), (-24, 24, 25, 25), (23, 23, 25, 25), (-24, -24, 24, 24),
                (21, 21, 21, 21), (-24, 22, 23, 24), (-24, 22, 22, 24), (-24, 23, 23, 24), (-12, 11, 24),
                (-11, 12, -24), (-2, 1, 24), (-1, 2, -24)]


def their_coefficients(theirs):
    txt = open(os.path.join(theirs, "parameters.py")).read()
    return set(re.findall(r"(\w+) = Parameter\(\s*name = '\w+',\s*nature = 'external',.*?lhablock = 'COUPLINGS'",
                          txt, re.S))


def pairs(theirs):
    """[(label, class, [(our coefficient, direction)], [(their coefficient, direction)])] and our
    coefficients with no counterpart."""
    have = their_coefficients(theirs)
    # Their entries are C_pr for a bilinear and C_prst for four fermions, the latter both p=r, s=t
    # (1122) and the crossed p=t, r=s (1221).  Our flavour-universal coefficient identifies p with r
    # and s with t (gen/operators.py, flavor_pairs), so it is their entries with p = r and s = t;
    # the crossed ones are another flavour structure and stay at zero.
    flav = collections.defaultdict(list)
    for n in have:
        m = re.match(r"(c\w+?)_(\d+)$", n)
        if m and m.group(2)[0] == m.group(2)[1] and (len(m.group(2)) == 2 or m.group(2)[2] == m.group(2)[3]):
            flav[m.group(1)].append(n)
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    out, unpaired = [], []
    for e in idx:
        if int(e["block"][4:]) > 674:
            continue
        for w in e["wcs"]:
            m = re.match(r"c8(\w+?)(?:x(\d+))?$", w)
            stem, k = m.group(1), m.group(2)
            cands = [f"c{stem}{k}"] if k else [f"c{stem}", f"c{stem}1"]
            theirs_list = next(([(c, 1.0)] for c in cands if c in have), None) or \
                next(([(n, 1.0) for n in sorted(flav[c])] for c in cands if c in flav), None)
            if theirs_list is None:
                unpaired.append(w)
                continue
            # a complex coefficient of ours is compared along its real part, the only one theirs has
            ours_list = [(w, 1.0)] if e["hc_mode"] != "complex" else [(w, 1.0), (w + "Re", 1.0)]
            out.append((w, e["cls"], ours_list, theirs_list))
    return out, unpaired


def matched_inputs():
    """(ours, theirs): their inputs, set in our model; the fermions other than t and b massless."""
    theirs = {"aS": 0.118, "Gf": 0.0000116638, "mh": 125.08, "mt": 172.56, "mW": 80.369, "mZ": 91.188,
              "yMb": 4.183, "yMt": 172.56, "Wh": 0.0037, "Wt": 1.42, "WW": 2.14, "WZ": 2.4955}
    ours = {"aS": 0.118, "Gf": 0.0000116638, "MH": 125.08, "MT": 172.56, "MW": 80.369, "MZ": 91.188,
            "ymb": 4.183, "ymt": 172.56, "WH": 0.0037, "WT": 1.42, "WW": 2.14, "WZ": 2.4955,
            "cabi": 0.0, "Lam": LAM, "MB": 0.0}
    for n in ("MU", "MD", "MS", "MC", "Me", "MMU", "MTA", "ymup", "ymdo", "yms", "ymc", "yme", "ymm", "ymtau"):
        ours[n] = 0.0
    return ours, theirs


def sm_values(r, keys):
    """{key: [contracted Standard Model vertex per draw]} for the vertices with these PDG keys"""
    want = {tuple(sorted(k)) for k in keys}
    need = {g for names, pdgs, ents in r["entries"] if tuple(sorted(pdgs)) in want for _, _, g in ents}
    nums = vertex_numbers(r["entries"], need)
    out = collections.defaultdict(lambda: np.zeros(2, complex))
    for vi, (names, pdgs, ents) in enumerate(r["entries"]):
        key = tuple(sorted(pdgs))
        if key in want:
            for ei, (_, _, g) in enumerate(ents):
                out[key] += r["value"].get(g, 0j) * np.array(nums[(vi, ei)])
    return out


def boson_signs(ra, rb):
    """The sign of each boson field of their model relative to ours, from the Standard Model
    vertices: a model that writes D = d + i g W instead of d - i g W has every vertex with an odd
    number of gauge fields of the opposite sign, which is a convention and not a difference.  The
    magnitudes must agree, which tests the matching of the inputs."""
    A, B = sm_values(ra, SM_REFERENCE), sm_values(rb, SM_REFERENCE)
    ratio = {k: np.mean(B[k] / A[k]) for k in A if k in B and np.all(np.abs(A[k]) > 0)}
    best = None
    import itertools
    for signs in itertools.product((1, -1), repeat=len(BOSONS)):
        eta = dict(zip(BOSONS, signs))
        dev = max(abs(q * np.prod([eta.get(abs(p), 1) for p in k]) - 1) for k, q in ratio.items())
        if best is None or dev < best[0]:
            best = (dev, eta)
    return best[1], best[0], ratio


def main(argv) -> int:
    if len(argv) < 2 or argv[1].startswith("-"):
        print(__doc__)
        return 2
    theirs = os.path.abspath(argv[1])
    ours = os.path.abspath(argv[argv.index("--ours") + 1]) if "--ours" in argv else os.path.join(ROOT, "models", "dim8_mw")
    tol = float(argv[argv.index("--tol") + 1]) if "--tol" in argv else 1e-6
    show = int(argv[argv.index("--show") + 1]) if "--show" in argv else 4
    plant = argv[argv.index("--plant") + 1] if "--plant" in argv else None
    P, unpaired = pairs(theirs)
    if "--classes" in argv:
        keep = {int(c) for c in argv[argv.index("--classes") + 1].split(",")}
        P = [p for p in P if p[1] in keep]
    if "--coeffs" in argv:
        keep = set(argv[argv.index("--coeffs") + 1].split(","))
        P = [p for p in P if p[0] in keep]
    mine, theirs_in = matched_inputs()
    print(f"ours   {ours}\ntheirs {theirs}\n{len(P)} coefficients compared; {len(unpaired)} of ours have no "
          f"counterpart in their model")
    ra = IV.read_model(ours, inputs=mine, only={c for p in P for c, _ in p[2]})
    rb = IV.read_model(theirs, inputs=theirs_in, only={c for p in P for c, _ in p[3]},
                       coeffs=their_coefficients(theirs))
    for lab, r in (("ours", ra), ("theirs", rb)):
        if r["failed"]:
            print(f"{lab}: {len(r['failed'])} couplings could not be evaluated, e.g. {r['failed'][:3]}")
    eta, dev, ratio = boson_signs(ra, rb)
    print(f"Standard Model vertices compared: {len(ratio)}; boson signs theirs/ours {eta}; largest deviation "
          f"of a vertex from ours after them {dev:.2e}")
    if dev > tol * 100:
        for k, q in sorted(ratio.items()):
            print(f"    {','.join(map(str, k)):20s} theirs/ours {q:.6g}")
        print("the Standard Model vertices do not agree: the inputs are not matched")
        return 1
    need = lambda r: {g for (g, n, v), d in r["resp"].items() if d}  # noqa: E731
    # vertices with more legs than theirs are not contracted at all: an eight-Higgs vertex is 8!
    # orderings of identical particles, and it could not be compared anyway
    na = vertex_numbers(ra["entries"], need(ra), maxlegs=MAXLEGS)
    nb = vertex_numbers(rb["entries"], need(rb), maxlegs=MAXLEGS)
    bad, by_class, factors, beyond = 0, collections.defaultdict(collections.Counter), [], collections.Counter()

    def within(R, sign=False):
        out = {}
        for k, x in R.items():
            if len(k) <= MAXLEGS:
                out[k] = x * (np.prod([eta.get(abs(p), 1) for p in k]) if sign else 1)
        return out

    for w, cls, sa_, sb_ in P:
        beyond[w] = len(moved_beyond(ra, sa_, MAXLEGS))
        A = within(response(ra, na, sa_, -1.0 if w == plant else 1.0, maxlegs=MAXLEGS))
        B = within(response(rb, nb, sb_, 1.0 / LAM ** 4, maxlegs=MAXLEGS), sign=True)
        cnt, rows = compare(A, B, tol, ratio=True)
        outcome = ("agree" if cnt["agree"] and len(cnt) == 1 else
                   "factor" if "agree up to a factor" in cnt else
                   "none" if not cnt else "error")
        by_class[cls][outcome] += 1
        if outcome == "factor":
            factors.append((w, rows[0][4]))
        if outcome == "error":
            bad += 1
            print(f"class {cls:2d} {w:14s} agree {cnt['agree']:3d}  differ {cnt['differ']:3d}  "
                  f"only ours {cnt['only first']:3d}  only theirs {cnt['only second']:3d}")
            for key, what, sa, sb, q in rows[:show]:
                what = {"only first": "only ours", "only second": "only theirs"}.get(what, what)
                what += f", theirs/ours {q:.6g}" if q is not None else ""
                print(f"      {','.join(map(str, key)):26s} {what}   |ours| {sa:.3e}  |theirs| {sb:.3e}")
    print("\nby class (coefficients): agree / agree up to a factor / no vertex in either / error")
    for cls in sorted(by_class):
        c = by_class[cls]
        print(f"  class {cls:2d}: {c['agree']:3d} / {c['factor']:3d} / {c['none']:3d} / {c['error']:3d}")
    if factors:
        fc = collections.Counter(f"{complex(q).real:+.6g}{complex(q).imag:+.6g}i" for _, q in factors)
        print("factors theirs/ours:", dict(fc))
        for w, q in factors[:show * 3]:
            print(f"    {w:16s} {complex(q):.6g}")
    print(f"\nnot compared (no operator in their model): {len(unpaired)}; vertices of ours with more than "
          f"{MAXLEGS} legs, beyond their model: {sum(beyond.values())}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
