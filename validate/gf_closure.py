#!/usr/bin/env python3
"""Is G_F still G_F?  Muon decay with the dimension-six coefficients of the input relations on.

    python3.11 validate/gf_closure.py <UFO dir with a dimension-six sector> [--keep DIR]

G_F is an input of the scheme, so the muon decay amplitude must not move when a coefficient is
switched on: the W-lepton vertices, the W mass and the four-lepton contact term change together
and the changes cancel.  At 1/Lambda^2 that is SMEFTsim's statement.  At 1/Lambda^4 it involves
the products of an operator with the first-order shifts, O_Hl3 at the corrected vev and on the
rescaled W.  No Ward identity and no two-point function is sensitive to these products, and
muon decay is a physical observable, which the others are not.

The test writes a standalone matrix element for mu- > e- ve~ vm with the amplitude at NP<=2,
evaluates it at MadGraph's fixed phase-space point with nine coefficients on at strength t, and
prints |M|^2/|M|^2_SM - 1 for t = 1, 1/2, 1/4, 1/8.  That must fall by eight per halving.

The W width is set to zero first.  A width that stays fixed while the W mass moves leaves a
first-order term of relative size Gamma_W^2/M_W^2 = 7e-4 times the shift of M_W^2 in
|1/(q^2 - M_W^2 + i M_W Gamma_W)|^2, which is real, is not what is being tested, and hides a
third-order residue completely.  What remains at first order with the width off is of relative
size m_mu^2/M_W^2, the momentum dependence of the propagator, at the 1e-8 level.

Reference output with the nine coefficients of COEFF on:
    t = 1        1/2       1/4       1/8
    -2.4e-3    -2.7e-4   -3.3e-5   -4.0e-6    ratios 8.7 8.3 8.2     dim68_is, {alpha, M_Z, G_F}
    -8.1e-8    -4.1e-8   -2.0e-8   -1.0e-8    ratios 2.0 2.0 2.0     dim68_mw, {M_W, M_Z, G_F}
A model without the products of an operator with the first-order shifts gives a second-order
deviation instead, with ratios near four.

In the {M_W, M_Z, G_F} scheme the W mass is an input and the higher orders cancel, so that the
first-order momentum dependence of the propagator is all that remains, and it falls by two per
halving.  G_F is defined at zero momentum transfer, while the W exchange of muon decay carries
q^2 up to m_mu^2 and the four-lepton contact term carries none, so no input relation removes it.
Its size is m_mu^2/M_W^2 = 1.7e-6 times the first-order shift, below m_mu^2/M_W^2 at every
strength.  The test therefore passes a deviation that falls by eight per halving, or one that
stays below m_mu^2/M_W^2 at every strength.  A missing first-order term would be of order
v^2/Lambda^2, about 1e-2 here, and a missing second-order term about 1e-3, so either fails both.
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


def mass(card, pdg):
    """The mass of a particle in the MASS block of a param card, or None when it is not there."""
    blk = re.search(r"(?ims)^\s*block\s+mass\b(.*?)(?=^\s*(?:block|decay)\b|\Z)", open(card).read())
    m = re.search(rf"(?m)^\s*{pdg}\s+([0-9.eE+-]+)", blk.group(1)) if blk else None
    return float(m.group(1)) if m else None


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    ufo = os.path.abspath(argv[1])
    if "lhablock = 'DIM6'" not in open(os.path.join(ufo, "parameters.py"), errors="replace").read():
        print(f"{ufo} has no block DIM6, so there is no dimension-six coefficient to switch on.  The check is for "
              "a model with a dimension-six sector, dim68_is or dim68_mw.")
        return 2
    mg = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
    work = argv[argv.index("--keep") + 1] if "--keep" in argv else tempfile.mkdtemp(prefix="gf_closure_")
    os.makedirs(work, exist_ok=True)
    # WriteUFO sets the NP expansion order to 2 and examples/release_model.sh raises it to 4.
    # Raise it in a copy, so the amplitude at NP=2 is allowed whatever state the model directory
    # is in.
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
        set_card(card, {k: v * t for k, v in COEFF.items()} | {"Lam": 1000.0})
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
    # the floor of the propagator's momentum dependence, m_mu^2/M_W^2.  In the {alpha, M_Z, G_F}
    # scheme the W mass is derived and is not on the card, and only the size of the floor needs it.
    mmu, mw = mass(card, 13), mass(card, 24) or 80.379
    floor = (mmu / mw) ** 2 if mmu else 0.0
    third = abs(dev[-1]) < 1e-12 or ratios[-1] > 6.5
    below = max(abs(d) for d in dev) < floor
    ok = third or below
    if third:
        verdict = "PASS, the deviation is third order"
    elif below:
        verdict = (f"PASS, the deviation stays below m_mu^2/M_W^2 = {floor:.1e} at every strength: the first-order "
                   "momentum dependence of the W propagator, with nothing above it")
    else:
        verdict = "FAIL, G_F moves below third order"
    print("G_F closure:", verdict)
    print("work directory:", work)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
