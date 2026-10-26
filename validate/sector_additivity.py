#!/usr/bin/env python3
"""Do the dim6 and dim8 cards of models/dim68_is split NP^2==2 into its two sectors?

    python3 validate/sector_additivity.py run [--model models/dim68_is] [--proc "p p > w+ w-"]
                                              [--nevents 10000] [--lam 3000] [--seed 37] [--cores 2]

(Three MadGraph runs, about half an hour on four cores; without "run" it prints this.)

What it does.  NP^2==2 holds the whole 1/Lambda^4 term of the combined model: the dimension-six
coefficients squared (with the dimension-six squares of the input relations) and the
dimension-eight interference with the Standard Model.  The model ships restrict_dim6,
restrict_dim8 and restrict_both to take them apart.  This runs one process at NP^2==2 with each
of the three cards, every coefficient the card keeps at 1 and both scales (Lam6, Lam) at --lam,
the same seed and run card in all three, and tests sigma(both) = sigma(dim6) + sigma(dim8).

When to reach for it.  After a release of dim68_is, or a change to examples/release_model.sh or
validate/make_restriction.py, which write the cards.  A card that dropped coefficients, kept one
of the other sector, or left a vertex the other card's coefficients reach shows here as a sum
that misses.  The W mass is derived in this scheme and no coupling order tags it, so it is not
the same in the three runs; that breaks the sum only at second order, 1/Lambda^6, far below the
errors at Lambda = 3 TeV.  It does not test the vertices themselves (validate/dim6_vs_smeftsim.py,
validate/index_vs_ufo.py --linear).

What the output means.  The three cross sections with their Monte Carlo errors, the difference
sigma(both) - sigma(dim6) - sigma(dim8) and its error (the three errors in quadrature: the runs
are separate integrations), and the pull.  **A pull above 3 is a FAILURE and the exit status is
1.**  A card that does not import, or a run without a cross section, is a failure too.

Believe it when the pull is of order one at two seeds, and when a run with a coefficient of one
sector left out of the sum (--drop dim8, which compares sigma(both) with sigma(dim6) alone) fails.
Process directories go to $DIM8_RUNS (default ~/dim8auto_build/mg5runs)/additivity_<card>.
"""
from __future__ import annotations

import math
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
PY = shutil.which("python3.11") or "python3"
RUNS = os.environ.get("DIM8_RUNS", os.path.expanduser("~/dim8auto_build/mg5runs"))
SET_CARDS = os.path.join(ROOT, "examples", "studies", "set_cards.py")


def kept(model, card):
    """The coefficients a restriction card keeps: nonzero entries named c..., the Cabibbo angle aside."""
    out = []
    for line in open(os.path.join(model, f"restrict_{card}.dat")):
        m = re.match(r"^\s*(?:\d+\s+)+([-\deE.+]+)\s*#\s*(\w+)", line)
        if m and float(m.group(1)) != 0.0 and m.group(2).startswith("c") and m.group(2) != "cabi":
            out.append(m.group(2))
    return out


def run(model, card, proc, nev, lam, seed, cores):
    d = os.path.join(RUNS, f"additivity_{card}")
    if os.path.isdir(d):
        shutil.rmtree(d)
    os.makedirs(RUNS, exist_ok=True)
    script = os.path.join(RUNS, f"additivity_{card}.mg5")
    open(script, "w").write(f"import model {model}-{card}\ngenerate {proc} NP^2==2\noutput {d} -f\n")
    log = open(os.path.join(RUNS, f"additivity_{card}.log"), "w")
    subprocess.run(["nice", "-n", "10", PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", script],
                   stdout=log, stderr=subprocess.STDOUT)
    if not os.path.isdir(d):
        return None, f"{card}: no process directory (see {log.name})"
    names = kept(model, card)
    sets = [f"{n}=1" for n in names] + [f"nevents={nev}", f"iseed={seed}", "ebeam1=6800", "ebeam2=6800",
                                        "hel_recycling=False", "dynamical_scale_choice=3"]
    # each scale is set only where the card keeps a coefficient that carries it
    if any(n.startswith("c8") for n in names):
        sets.append(f"Lam={lam}")
    if any(not n.startswith("c8") for n in names):
        sets.append(f"Lam6={lam}")
    r = subprocess.run([sys.executable, SET_CARDS, d] + sets, stdout=log, stderr=subprocess.STDOUT)
    if r.returncode:
        return None, f"{card}: set_cards.py refused an assignment (see {log.name})"
    with open(os.path.join(d, "Cards", "me5_configuration.txt"), "a") as f:
        f.write(f"\nrun_mode = 2\nnb_core = {cores}\nautomatic_html_opening = False\n")
    subprocess.run(["nice", "-n", "10", os.path.join(d, "bin", "generate_events"), "-f", "run_01"],
                   cwd=d, stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL)
    txt = open(log.name).read()
    m = re.findall(r"Cross-section :\s*([-\deE.+]+)\s*\+-\s*([-\deE.+]+)\s*pb", txt)
    if not m:
        return None, f"{card}: no cross section (see {log.name})"
    return (float(m[-1][0]), float(m[-1][1]), len(names)), None


def main(argv) -> int:
    if not argv or argv[0] != "run":
        print(__doc__)
        return 2
    opt = lambda k, dflt: argv[argv.index(k) + 1] if k in argv else dflt  # noqa: E731
    model = os.path.abspath(opt("--model", os.path.join(ROOT, "models", "dim68_is")))
    proc, nev = opt("--proc", "p p > w+ w-"), int(opt("--nevents", "10000"))
    lam, seed, cores = float(opt("--lam", "3000")), int(opt("--seed", "37")), int(opt("--cores", "2"))
    drop = opt("--drop", None)
    res, fails = {}, []
    for card in ("dim6", "dim8", "both"):
        r, err = run(model, card, proc, nev, lam, seed, cores)
        if err:
            fails.append(err); print(err, flush=True)
            continue
        res[card] = r
        print(f"{card:5s} {r[2]:4d} coefficients at 1   sigma(NP^2==2) = {r[0]:+.5e} +- {r[1]:.2e} pb", flush=True)
    if fails:
        return 1
    parts = [c for c in ("dim6", "dim8") if c != drop]
    diff = res["both"][0] - sum(res[c][0] for c in parts)
    err = math.sqrt(res["both"][1] ** 2 + sum(res[c][1] ** 2 for c in parts))
    pull = diff / err if err else float("inf")
    print(f"\n{proc} at NP^2==2, Lam6 = Lam = {lam:g} GeV, seed {seed}:")
    print(f"sigma(both) - " + " - ".join(f"sigma({c})" for c in parts) + f" = {diff:+.3e} +- {err:.2e} pb, pull {pull:+.2f}")
    print("FAILURE" if abs(pull) > 3 else "additive within the Monte Carlo errors")
    return 1 if abs(pull) > 3 else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
