#!/usr/bin/env python3
"""Is G_F still G_F?  Muon decay with the dimension-six coefficients of the input relations on.

    python3.11 validate/gf_closure.py <UFO dir with a DIM6 block> [--keep DIR]

G_F is an input of the scheme, so the muon decay amplitude must not move when a coefficient is
switched on: the W-lepton vertices, the W mass and the four-lepton contact term change together
and the changes cancel.  At 1/Lambda^2 that is SMEFTsim's statement.  At 1/Lambda^4 it involves
the products of an operator with the first-order shifts, O_Hl3 at the corrected vev and on the
rescaled W, which is the part of the model that was missing until 2026-10-05.  No Ward identity
and no two-point term sees it, and it is a physical observable, which the others are not.

The test writes a standalone matrix element for mu- > e- ve~ vm with the amplitude at NP<=2,
evaluates it at MadGraph's fixed phase-space point with nine coefficients on at strength t, and
prints |M|^2/|M|^2_SM - 1 for t = 1, 1/2, 1/4, 1/8.  That must fall by eight per halving.

The W width is set to zero first.  A width that stays fixed while the W mass moves leaves a
first-order term of relative size Gamma_W^2/M_W^2 = 7e-4 times the shift of M_W^2 in
|1/(q^2 - M_W^2 + i M_W Gamma_W)|^2, which is real, is not what is being tested, and hides a
third-order residue completely.  What remains at first order with the width off is of relative
size m_mu^2/M_W^2, the momentum dependence of the propagator, at the 1e-8 level.

Results on 2026-10-05, nine coefficients on:   t = 1        1/2       1/4       1/8
    dimension-six sector rebuilt             -2.4e-3    -2.7e-4   -3.3e-5   -4.0e-6    ratios 8.7 8.3 8.2
    the model it replaced                    -4.1e-2    -9.3e-3   -2.2e-3   -5.4e-4    ratios 4.4 4.2 4.1
"""
import os
import re
import subprocess
import sys
import tempfile

COEFF = {"cHl3": 0.8, "cll1": -0.6, "cHW": 0.7, "cHB": -0.4, "cHWB": 0.3, "cHDD": 0.5,
         "cHbox": 0.45, "cHl1": 0.5, "cH": 0.35}


def set_card(card, values):
    lines = open(card).read().split("\n")
    seen = set()
    for i, l in enumerate(lines):
        if re.match(r"^DECAY\s+24\s", l):
            lines[i] = re.sub(r"^(DECAY\s+24\s+)\S+", r"\g<1>0.000000e+00", l); seen.add("WW")
            continue
        m = re.match(r"^(\s*(?:\d+\s+)+)([-\deE.+]+)(\s*#\s*(\w+))", l)
        if m and m.group(4) in values:
            lines[i] = f"{m.group(1)}{values[m.group(4)]:.6e}{m.group(3)}"; seen.add(m.group(4))
    missing = set(values) - seen
    if missing:
        sys.exit(f"not in the parameter card: {' '.join(sorted(missing))}")
    if "WW" not in seen:
        sys.exit("no DECAY 24 line in the parameter card: the W width could not be set to zero")
    open(card, "w").write("\n".join(lines))


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ufo = os.path.abspath(argv[1])
    mg = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
    work = argv[argv.index("--keep") + 1] if "--keep" in argv else tempfile.mkdtemp(prefix="gf_closure_")
    os.makedirs(work, exist_ok=True)
    # the writer's NP limit is 2 on a model that has not been through the release step; raise it
    # in a copy so the amplitude at NP=2 is allowed whatever state the model directory is in
    model = os.path.join(work, "model")
    subprocess.run(["rm", "-rf", model]); subprocess.run(["cp", "-r", ufo, model], check=True)
    co = os.path.join(model, "coupling_orders.py")
    orders = open(co).read()           # read BEFORE opening for writing: open(co, "w") truncates
    open(co, "w").write(re.sub(r"(NP = CouplingOrder\(name = 'NP',\s*expansion_order = )\d+", r"\g<1>4", orders))
    for junk in ("__pycache__",):      # bytecode of another Python version stops MadGraph's import
        subprocess.run(["rm", "-rf", os.path.join(model, junk)])
    proc = os.path.join(work, "mu")
    open(os.path.join(work, "mu.mg5"), "w").write(
        f"import model {model}\ngenerate mu- > e- ve~ vm NP<=2\noutput standalone {proc} -f\n")
    r = subprocess.run([sys.executable, os.path.join(mg, "bin", "mg5_aMC"), "-f", os.path.join(work, "mu.mg5")],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL,
                       cwd=work)        # MadGraph leaves nsqso_born.inc in its working directory
    sub = os.path.join(proc, "SubProcesses")
    pdirs = [d for d in os.listdir(sub) if d.startswith("P")] if os.path.isdir(sub) else []
    if not pdirs:
        sys.exit("MadGraph wrote no process:\n" + r.stdout[-1500:])
    pdir = os.path.join(sub, pdirs[0])
    subprocess.run(["make", "check"], cwd=pdir, capture_output=True)
    card = os.path.join(proc, "Cards", "param_card.dat")

    def me(t):
        set_card(card, {k: v * t for k, v in COEFF.items()} | {"Lam6": 1000.0})
        out = subprocess.run(["./check"], cwd=pdir, capture_output=True, text=True).stdout
        m = re.search(r"Matrix element\s*=\s*([0-9.E+-]+)", out)
        if not m:
            sys.exit("the standalone check printed no matrix element:\n" + out[-800:])
        return float(m.group(1))

    m0 = me(0.0)
    ts = [1.0, 0.5, 0.25, 0.125]
    dev = [me(t) / m0 - 1 for t in ts]
    print(f"mu- > e- ve~ vm, NP<=2, W width zero, |M|^2 at the Standard-Model point {m0:.10e}")
    for t, d in zip(ts, dev):
        print(f"   t = {t:<6g} |M|^2/SM - 1 = {d:+.4e}")
    ratios = [dev[i] / dev[i + 1] if dev[i + 1] else float("inf") for i in range(3)]
    print("   ratios per halving:", " ".join(f"{x:.2f}" for x in ratios), "  (8 is third order, 4 second, 2 first)")
    ok = abs(dev[-1]) < 1e-12 or ratios[-1] > 6.5
    print("G_F closure:", "PASS, the deviation is third order" if ok else "FAIL, G_F moves below third order")
    print("work directory:", work)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
