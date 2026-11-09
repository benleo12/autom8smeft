#!/usr/bin/env python3
"""Is what MadGraph returns at NP^2==2 really linear in the coefficient?  Class by class.

    validate/lambda_scaling.py [--proc ww|zh|mm|uu] [--energy 1000] [--nev 2000]
                               [--model dim8_is] [--classes 3,6,13] [--out file.tsv] [--set MW=79.82]

A term linear in a dimension-eight coefficient falls as 1/Lambda^4, so the cross section at
Lambda = 1 TeV is sixteen times the one at 2 TeV.  A term quadratic in it falls as 1/Lambda^8 and
the ratio is 256.  The order tag NP^2==2 is meant to select the first and nothing else.

That holds only if every coefficient-dependent coupling carries its NP tag.  The derived
parameters of the input scheme, the vacuum expectation value, the Yukawas and the Higgs quartic,
enter the Lagrangian as tagged series (gen/input_scheme.py).  Were one of them an exact, untagged
function of the coefficients, the amplitude MadGraph labels NP=0 would depend on the
coefficients, and its product with a tagged NP=2 amplitude would be quadratic while counted at
NP^2==2.  A class whose interference vanishes by chirality, such as psi^2H^5 in e+ e- > w+ w-,
is the sharpest case: there the quadratic piece would be everything the tag returns, and the
ratio would be 256.  The W mass is exact and untagged, so for the classes that shift it (3, 6 and
the leptonic part of 13) the Standard-Model half of the interference is evaluated at the shifted
mass and the ratio sits a few per mille from 16 at unit coefficients.  That residue is the mass
and not a tagging defect, and it is absent in the {M_W, M_Z, G_F} scheme.

This runs the restriction card of every class (restrict_clsN.dat) at both scales and prints the
ratio with a verdict: linear, QUADRATIC, mixed or zero.  Results append to
validate/lambda_scaling.tsv, or to validate/lambda_scaling_<model>.tsv for another model.
"""
from __future__ import annotations

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "gen"))
import energy_growth as E   # noqa: E402
import epower               # noqa: E402

OUT = os.path.join(HERE, "lambda_scaling.tsv")
NAMES = {i + 1: n for i, n in enumerate(epower.DIM8_CLASSES)} if isinstance(epower.DIM8_CLASSES, dict) else {}


def main(argv) -> int:
    global OUT
    tags = [argv[argv.index("--proc") + 1]] if "--proc" in argv else ["ww", "zh"]
    energy = float(argv[argv.index("--energy") + 1]) if "--energy" in argv else 1000.0
    nev = int(argv[argv.index("--nev") + 1]) if "--nev" in argv else 2000
    # another model, e.g. dim8_mw, whose results go to their own file and process directories
    model = argv[argv.index("--model") + 1] if "--model" in argv else "dim8_is"
    classes = ([int(c) for c in argv[argv.index("--classes") + 1].split(",")] if "--classes" in argv
               else list(range(1, 22)))
    # extra card settings for every run, comma separated: MW=79.82435975 puts the {MW, MZ, GF}
    # model on the numerical point the alpha scheme derives
    extra = argv[argv.index("--set") + 1].split(",") if "--set" in argv else []
    if "--out" in argv:
        OUT = argv[argv.index("--out") + 1]
    elif model != "dim8_is":
        OUT = os.path.join(HERE, f"lambda_scaling_{model}.tsv")
    if not os.path.exists(OUT):
        open(OUT, "w").write("process\tclass\tsigma_1TeV_pb\terr\tsigma_2TeV_pb\terr\tratio\tverdict\n")
    done = {tuple(l.split("\t")[:2]) for l in open(OUT).read().split("\n")[1:] if l}
    for tag in tags:
        proc = E.PROCS[tag][0]
        for cls in classes:
            if (proc, str(cls)) in done:
                continue
            E.MODEL = os.path.join(ROOT, "models", f"{model}-cls{cls}")
            d = E.generate(tag, "NP^2==2", suffix=f"_lam{cls}" + ("" if model == "dim8_is" else f"_{model}"))
            if d is None:
                continue                      # no diagram for this class in this process
            r = []
            for lam in (1000, 2000):
                s, e = E.one(d, tag, f"cls{cls}", ["dim8_all=1", f"Lam={lam}"] + extra, energy, nev,
                             os.path.join(E.WORK, f"lam_{tag}_{cls}_{lam}.log"))
                r.append((s, e))
            (a, ea), (b, eb) = r
            if not a or not b:
                verdict, ratio = "zero", float("nan")
            else:
                ratio = a / b
                verdict = ("linear" if abs(ratio - 16) < 1.5 else
                           "QUADRATIC" if abs(ratio - 256) < 30 else "mixed")
            open(OUT, "a").write(f"{proc}\t{cls}\t{a}\t{ea}\t{b}\t{eb}\t{ratio:.2f}\t{verdict}\n")
            print(f"{proc:<16s} cls{cls:<3d} {a!s:>12} {b!s:>12}  ratio {ratio:7.1f}  {verdict}", flush=True)
    print("LAMBDA SCALING DONE")
    return 0


if __name__ == "__main__":
    if "-h" in sys.argv or "--help" in sys.argv:
        print(__doc__); sys.exit(0)
    sys.exit(main(sys.argv))
