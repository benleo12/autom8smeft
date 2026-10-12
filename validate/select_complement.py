#!/usr/bin/env python3
"""Check that the operator selector leaves nothing out, with MadGraph as the judge.

    validate/select_complement.py "p p > w+ w-" [--model models/dim8_is] [--keep]

The selector (./dim8 select) claims that every dimension-eight operator with a vertex in some
tree diagram of the process is in its list.  This script keeps the COMPLEMENT instead: it writes
a restriction card that zeroes every selected operator and keeps every other one, imports the
released model with that card and asks MadGraph to generate the process at NP^2==2.  If the
claim holds, MadGraph finds no amplitude at all (NoDiagramException), and the script prints
PASS.  Any diagram it does find comes from an operator the selector missed, and the script
prints FAIL with the diagram count.  The dimension-six coefficients are zeroed as well, so that
the only NP vertices in the model are those of the unselected dimension-eight operators.

Do not read the completeness off diagram COUNTS instead.  The full model and a restricted
model generate different numbers of diagrams for the same process even when nothing is missed,
because MadGraph drops from a restricted model every vertex whose couplings evaluate to zero
with the card's values, while an unrestricted model keeps them.  On p p > w+ w- the released
model carries massive quarks and a Cabibbo-only CKM matrix, so the u-b-W coupling is exactly
zero: the unrestricted model generates twelve t-channel b-exchange diagrams per quark channel
that vanish identically, and the restricted one does not.

Needs the model linked into MadGraph's models directory under its own name (models/dim8_is as
dim8_is), MadGraph at $MG5_DIR, and python3.11 for MadGraph.  The restriction card is removed
afterwards unless --keep is given.
"""
import json, os, re, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if not args:
        print(__doc__); return 2
    process = args[0]
    model = os.path.abspath(args[1] if len(args) > 1 else _opt(argv, "--model", "models/dim8_is"))
    keep = "--keep" in argv
    mg = os.environ.get("MG5_DIR")
    if not mg or not os.path.isfile(os.path.join(mg, "bin", "mg5_aMC")):
        print("set MG5_DIR to the MadGraph directory (the one holding bin/mg5_aMC)"); return 2
    py = shutil.which("python3.11") or sys.executable
    name = re.sub(r"[^a-z0-9]+", "", process.lower()) or "proc"
    card = "comp_" + name

    # the selection, both groups, as the selector writes it
    sel = subprocess.run([os.path.join(ROOT, "dim8"), "select", process, "-o", card],
                         capture_output=True, text=True, cwd=ROOT)
    if sel.returncode:
        print(sel.stdout, sel.stderr); return sel.returncode
    selected = {l.strip() for l in open(os.path.join(ROOT, "build", card + ".blocks")) if l.strip()}
    index = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    complement = [e["block"] for e in index if int(e["block"][4:]) <= 674 and e["block"] not in selected]
    n_sel = sum(1 for b in selected if b.startswith("L8op"))
    print(f"{process}: {n_sel} dimension-eight operators selected, {len(complement)} in the complement")

    import make_restriction as MR
    rc = MR.main(["make_restriction", model, card] + complement)
    if rc:
        return rc
    script = os.path.join(ROOT, "build", card + ".mg5")
    open(script, "w").write(f"import model {os.path.basename(model)}-{card}\n"
                            f"generate {process} NP^2==2\nexit\n")
    log = os.path.join(ROOT, "build", card + ".log")
    with open(log, "w") as out:
        subprocess.run([py, os.path.join(mg, "bin", "mg5_aMC"), script], stdout=out, stderr=subprocess.STDOUT)
    text = open(log).read()
    if not keep:
        os.remove(os.path.join(model, f"restrict_{card}.dat"))
    m = re.search(r"Total: (\d+) processes with (\d+) diagrams", text)
    if "NoDiagramException" in text and not m:
        print(f"PASS: the complement of the selection generates no diagram for {process}")
        return 0
    if m:
        print(f"FAIL: the complement generates {m.group(2)} diagrams in {m.group(1)} subprocesses; see {log}")
        return 1
    print(f"MadGraph did not answer; see {log}")
    return 3


def _opt(argv, flag, default):
    for i, a in enumerate(argv):
        if a == flag and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(flag + "="):
            return a.split("=", 1)[1]
    return default


if __name__ == "__main__":
    sys.exit(main(sys.argv))
