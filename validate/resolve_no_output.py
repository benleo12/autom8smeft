#!/usr/bin/env python3
"""Decide whether a study's empty cells are "no diagram" or a real failure, from MadGraph.

    validate/resolve_no_output.py <study dir> [model dir] [--write]

The study driver records a cell with no cross section as ``NO_OUTPUT`` and the table generator
then reads the run log to tell a class that has no diagram in the process from one that crashed.
That works while the logs are there.  They are build artifacts and get cleaned, after which an
honest "no diagram" silently becomes an unexplained "no output" in a published table.

This re-derives the answer from the model instead of from a log, and it is cheap because it needs
only the diagram generation and not the integration: for each empty cell it asks MadGraph to
generate the process on the restricted model and records ``NO_DIAGRAMS`` if it raises
``NoDiagramException``.  Cells are grouped by model so that each restricted model is imported
once.  With --write the answers go back into results.tsv, so the resolution is stored with the
data and does not have to be redone.
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
PY = "python3.11"
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "nodiag")


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    st = os.path.abspath(argv[1])
    model = os.path.abspath(argv[2]) if len(argv) > 2 and not argv[2].startswith("-") \
        else os.path.join(ROOT, "models", "dim8_is")
    write = "--write" in argv
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(st, "results.tsv"))]
    head, rows = rows[0], rows[1:]
    ci = {k: i for i, k in enumerate(head)}
    todo = defaultdict(list)
    for r in rows:
        if r[ci["sigma_pb"]] in ("NO_OUTPUT", "BAD_SETTING", "FAILED"):
            todo[r[ci["model"]]].append((r[ci["process"]].strip(), r[ci["order"]]))
    if not todo:
        print("no unresolved cells")
        return 0
    os.makedirs(WORK, exist_ok=True)
    verdict = {}
    for tag, cells in sorted(todo.items()):
        card = tag.split("-", 1)[1] if "-" in tag else None
        m = f"{model}-{card}" if card else model
        sc = os.path.join(WORK, re.sub(r"\W+", "_", tag) + ".mg5")
        log = sc[:-4] + ".log"
        # MadGraph stops a -f script at the first exception, so a model with several empty
        # cells would resolve only the first one.  crash_on_error False makes it carry on.
        lines = ["set crash_on_error False", f"import model {m}"]
        for p, o in cells:
            lines.append(f"generate {p} {o}")
        open(sc, "w").write("\n".join(lines) + "\n")
        subprocess.run(["nice", "-n", "19", PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc],
                       stdout=open(log, "w"), stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, check=False)
        txt = open(log, errors="replace").read()
        # one "generate" echo per cell, in order; look at what follows each
        parts = re.split(r"^generate ", txt, flags=re.M)[1:]
        for (p, o), seg in zip(cells, parts):
            v = "NO_DIAGRAMS" if "NoDiagramException" in seg or "No amplitudes generated" in seg \
                else ("OK" if re.search(r"Process has \d+ diagrams", seg) else "UNRESOLVED")
            verdict[(p, tag, o)] = v
            print(f"{tag:<24s} {p:<22s} {o:<16s} {v}", flush=True)
    n = sum(1 for v in verdict.values() if v == "NO_DIAGRAMS")
    print(f"\n{n} of {len(verdict)} empty cells have no diagram; "
          f"{sum(1 for v in verdict.values() if v == 'OK')} do have diagrams and failed for "
          f"another reason; {sum(1 for v in verdict.values() if v == 'UNRESOLVED')} unresolved")
    if write:
        out = [head]
        for r in rows:
            k = (r[ci["process"]].strip(), r[ci["model"]], r[ci["order"]])
            if verdict.get(k) == "NO_DIAGRAMS":
                r[ci["sigma_pb"]] = "NO_DIAGRAMS"
            out.append(r)
        open(os.path.join(st, "results.tsv"), "w").write(
            "\n".join("\t".join(r) for r in out) + "\n")
        print(f"wrote {st}/results.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
