#!/usr/bin/env python3
"""The MadGraph runs of validate/lambda_scaling.py: one process directory per process and model, and
one cross section per call, at a lepton collider of fixed energy.

    import mg_runs as R
    R.MODEL = <model directory>            # default $DIM8_MODEL, else models/dim8_mw
    d = R.generate("ww", "NP^2==2")        # import the model and output the process once
    sigma, error = R.one(d, "ww", label, ["dim8_all=1", "Lam=1000"], 1000.0, 2000, log)

The processes are those of PROCS, each with the angular acceptance its run card cuts on by PDG code,
since a fixed acceptance keeps the forward Standard-Model peak out of the energy dependence, and a
lepton collider keeps the parton luminosity out of it.  Each process is chosen so that at least one
class reaches it with a four-point contact vertex.  The process directories go below
$DIM8_BUILD/v12<tag> (default ~/dim8auto_build), where <tag> is empty for models/dim8_is and
_<model> otherwise.  R.WORK is that directory for R.MODEL as it is when R.WORK is read, and a restricted
model, dim8_mw-cls3, has the directory of its model, so a caller that runs several restrictions gives each
its own suffix.  MadGraph is $MG5_DIR (default ~/Downloads/MG5_aMC_v3_5_3), run with python3.11.

generate returns None when the process has no diagram at the order asked for, which is a result, and
stops the run with the reason when MadGraph gives no process directory for another cause.  one returns
(0.0, 0.0) when MadGraph reports a zero result, and (None, reason) when the cards were refused or the
run ended with neither a cross section nor a zero result.
"""
from __future__ import annotations

import os
import re
import subprocess

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
PY = "python3.11"
MODEL = os.environ.get("DIM8_MODEL", os.path.join(ROOT, "models", "dim8_mw"))
NICE = ["nice", "-n", "19"]


def mtag(model=None):
    """<tag> of a model, of MODEL as it is now without an argument: each model keeps its own process
    directories, except models/dim8_is, whose runs keep the names they had when it was the default.  A
    restricted model, dim8_mw-cls3, has the tag of its model."""
    name = os.path.basename((model or MODEL).rstrip("/")).split("-")[0]
    return "" if name == "dim8_is" else "_" + name


def work(model=None):
    """The directory of the runs of a model, of MODEL as it is now without an argument."""
    return os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "v12" + mtag(model))


def __getattr__(name):
    # MTAG and WORK are taken from MODEL each time they are read, so that they follow a MODEL set after the import
    if name == "MTAG":
        return mtag()
    if name == "WORK":
        return work()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


# Final states whose angular acceptance the run card can cut on by PDG code.  Each process is
# chosen so that at least one class reaches it with a four-point contact vertex.
PROCS = {
    "ww": ("e+ e- > w+ w-", "{24:1.1}"),
    "zh": ("e+ e- > z h", "{23:1.1,25:1.1}"),
    "mm": ("e+ e- > mu+ mu-", "{13:1.1}"),
    "uu": ("e+ e- > u u~", "{2:1.1}"),
}


def run(cmd, log, cwd=None):
    with open(log, "a") as fh:
        fh.write("\n$ " + " ".join(cmd) + "\n")
        return subprocess.run(NICE + cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, cwd=cwd, check=False).returncode


def reason(txt: str) -> str:
    """Why a step ended, from what it wrote to its log: MadGraph's error, the line after "with error:",
    and otherwise the last line, which is what set_cards.py or the shell says when it refuses.  The lines
    that run() writes, "$ command", are not the step's."""
    lines = [l for l in (re.sub(r"\x1b\[[0-9;]*m", "", x).strip() for x in txt.split("\n"))
             if l and l != "quit" and not l.startswith("$ ")]
    for k in range(len(lines) - 1, 0, -1):
        if lines[k - 1].endswith("with error:"):
            return lines[k]
    return lines[-1] if lines else "nothing was written"


def generate(tag: str, order: str = "NP^2==2", suffix: str = ""):
    """Import the model and output the process once.  Returns the process directory, or None when the
    process has no diagram at this order.  Without MadGraph, or when MadGraph gives no process directory
    for another cause, the run stops with the reason."""
    proc, _ = PROCS[tag]
    w = work()
    d = os.path.join(w, tag + suffix)
    if os.path.exists(os.path.join(d, "bin", "generate_events")):
        return d
    mg5 = os.path.join(MG, "bin", "mg5_aMC")
    if not os.path.isfile(mg5):
        raise SystemExit(f"[{tag}] no MadGraph at {mg5}: set MG5_DIR to the MadGraph directory")
    os.makedirs(w, exist_ok=True)
    sc = os.path.join(w, f"{tag}{suffix}.mg5")
    open(sc, "w").write(f"import model {MODEL}\ngenerate {proc} {order}\noutput {d} -f\n")
    log = os.path.join(w, f"{tag}{suffix}_gen.log")
    before = os.path.getsize(log) if os.path.exists(log) else 0
    rc = run([PY, mg5, "-f", sc], log)
    txt = open(log, errors="replace").read()[before:]
    made = os.path.exists(os.path.join(d, "bin", "generate_events"))
    if not made and "NoDiagramException" in txt:
        return None                       # MadGraph found no diagram at this order, which is a result
    if rc or not made:
        raise SystemExit(f"[{tag}] the generation of {proc} {order} with {MODEL} failed (exit status {rc}): "
                         f"{reason(txt)}\n  see {log}")
    open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
        "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
    return d


def one(d, tag, label, sets, energy, nev, log):
    """One cross section: edit the cards, integrate, read the result from the log.  Returns
    (sigma, error) in pb, (0.0, 0.0) when MadGraph reports a zero result, and (None, reason) when the
    cards were refused or the run ended with neither."""
    _, eta = PROCS[tag]
    common = [f"nevents={nev}", "lpp1=0", "lpp2=0", f"ebeam1={energy/2:g}", f"ebeam2={energy/2:g}",
              "hel_recycling=False", "use_syst=False", f"eta_max_pdg={eta}",
              # neutralise the default acceptance so eta_max_pdg is the ONLY cut, but only for the
              # entries this process's card actually has: MadGraph writes a minimal run card and
              # omits the lepton and jet blocks for a final state with neither, and set_cards.py
              # treats an unknown name as an error on purpose.
              "ptl=0", "etal=-1", "drll=0", "mmll=0", "ptj=0", "etaj=-1", "drjj=0", "ptgmin=0"]
    have = set(re.findall(r"=\s*(\w+)", open(os.path.join(d, "Cards", "run_card.dat")).read()))
    common = [a for a in common if a.split("=")[0] in have or a.startswith("hel_recycling")]
    before = os.path.getsize(log) if os.path.exists(log) else 0
    if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d] + common + sets, log):
        return None, "the cards were not set: " + reason(open(log, errors="replace").read()[before:])
    before = os.path.getsize(log) if os.path.exists(log) else 0
    rc = run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
    txt = open(log, errors="replace").read()[before:]
    m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
    if m:
        return float(m[-1][0]), float(m[-1][1])
    # a vanishing amplitude prints no cross section line: MadGraph's survey returns zero and says so
    if "Zero result detected" in txt or "zero cross section" in txt:
        return 0.0, 0.0
    return None, f"the run gave neither a cross section nor a zero result (exit status {rc}): {reason(txt)}"


if __name__ == "__main__":
    print(__doc__)
