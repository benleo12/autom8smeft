"""
tests/test_gluon_normalisation.py: alpha_s is the coupling of the canonical gluon.

Run:  python3 tests/test_gluon_normalisation.py [UFO dir ...]      (default: the input-scheme models in models/)

The vacuum piece of Q_{G^2H^4}^{(1)} (and of C_HG in dim68_is) is a gluon kinetic term.  The
input-scheme models cancel it with d8fG (rG1), so G = sqrt(4 pi aS) is the coupling of the
canonically normalised gluon, the one e+e- -> 3 jets measures, and the coefficient survives only
on vertices with a Higgs leg.  A pair of entries that carries the vacuum piece and its
cancellation in two vertices, with the colour spelled two ways, sums to zero but puts c8G2H4x1
and d8fG on g g g g, where a reader of vertices.py takes it for a shift of alpha_s.
validate/drop_zero_structures.py removes such pairs across vertices.  This
test fails on any vertex without a Higgs leg whose coupling names one of these parameters, and
checks the colour canonicalisation that the removal relies on.
"""

import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "validate"))

from drop_zero_structures import colour_key  # noqa: E402

IS_MODELS = ("dim8_is", "dim8_mw", "dim68_is", "dim68_mw")
# the parameters through which a gluon-normalisation operator can reach a vertex
NAMES = {"c8G2H4x1", "c8G2H4x2", "d8fG", "cHG", "cHGtil"}


def higgs_free_offenders(ufo: str) -> list:
    """(vertex, legs, coupling, value) for every vertex without a Higgs leg whose coupling names
    one of NAMES."""
    cp = dict(re.findall(r"^(GC_\d+) = Coupling\(name = 'GC_\d+',\s*value = '([^']*)'",
                         open(os.path.join(ufo, "couplings.py")).read(), re.M))
    out = []
    for block in open(os.path.join(ufo, "vertices.py")).read().split("\n\n"):
        m = re.match(r"\s*(V_\d+) = Vertex\(", block)
        if not m:
            continue
        legs = re.findall(r"P\.(\w+)", re.search(r"particles = \[(.*?)\]", block, re.S).group(1))
        if "H" in legs:
            continue
        for g in set(re.findall(r"C\.(GC_\d+)", block)):
            hit = NAMES & set(re.findall(r"[A-Za-z_]\w*", cp.get(g, "")))
            if hit:
                out.append((m.group(1), " ".join(legs), g, cp[g]))
    return out


def main(argv) -> int:
    ok = bad = 0

    def check(cond, what):
        nonlocal ok, bad
        if cond:
            ok += 1
        else:
            bad += 1
            print("FAIL", what)

    # colour: one structure in two spellings, and an odd permutation that costs a sign
    check(colour_key("f(-1,1,3)*f(-1,2,4)") == colour_key("f(-1,1,3)*f(2,4,-1)"), "f cyclic")
    check(colour_key("f(2,1,3)") == ("f(1,2,3)", -1), "f odd permutation")
    check(colour_key("d(3,1,2)") == ("d(1,2,3)", 1), "d symmetric")
    check(colour_key("Identity(2,1)*T(3,4,5)") == ("Identity(1,2)*T(3,4,5)", 1), "factor order")
    check(colour_key("f(-1,1,2)*f(-1,3,4)") != colour_key("f(-2,1,2)*f(-2,3,4)"),
          "dummies are not renamed, so a match is never invented")

    ufos = argv[1:] or [os.path.join(ROOT, "models", m) for m in IS_MODELS
                        if os.path.exists(os.path.join(ROOT, "models", m, "vertices.py"))]
    for ufo in ufos:
        off = higgs_free_offenders(ufo)
        for v, legs, g, val in off[:6]:
            print(f"  {os.path.basename(ufo)} {v} [{legs}] {g} = {val}")
        check(not off, f"{os.path.basename(ufo)}: {len(off)} Higgs-free vertex couplings name a "
                       f"gluon-normalisation parameter")
    print(f"{ok}/{ok + bad} checks pass on {len(ufos)} models")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
