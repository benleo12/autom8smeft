#!/usr/bin/env python3
"""Fill in the class cells a study never ran, so that a blank in the paper's grid is never
mistaken for a zero.

    validate/resolve_missing.py <study dir> [--write]

\\code{resolve_no_output.py} resolves a cell that IS in results.tsv and carries no cross section.
This resolves a cell that is not in results.tsv at all, which is a different and more dangerous
situation: three of the twelve processes skipped some class rows on cost, and in a table where a
dash means ``no diagram'' an absent row and an empty row look identical while meaning opposite
things.  For each missing (process, class) it asks MadGraph to generate the process on the
restricted model and writes back either ``NO_DIAGRAMS'' or ``NOT_INTEGRATED'', the latter meaning
the class does reach the process and the cross section was simply never measured.

Only diagram generation runs, never integration, so this is minutes and not hours, and it is
niced because the machine is usually shared.
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
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "missing")
ORDER = "NP^2==2"
NCLS = 21


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    st = os.path.abspath(argv[1])
    model = os.path.join(ROOT, "models", "dim8_is")
    write = "--write" in argv
    lines = [l.rstrip("\n").split("\t") for l in open(os.path.join(st, "results.tsv")) if l.strip()]
    head, rows = lines[0], lines[1:]
    ci = {k: i for i, k in enumerate(head)}
    have = {(r[ci["process"]].strip(), r[ci["model"]], r[ci["order"]]) for r in rows}
    procs = []
    for r in rows:                      # keep first-seen order, one entry per process
        p = r[ci["process"]].strip()
        if p not in procs:
            procs.append(p)

    todo = defaultdict(list)
    for p in procs:
        for c in range(1, NCLS + 1):
            if (p, f"dim8_is-cls{c}", ORDER) not in have:
                todo[f"dim8_is-cls{c}"].append(p)
    if not todo:
        print("no missing cells")
        return 0
    print(f"{sum(len(v) for v in todo.values())} missing cells in {len(todo)} class cards")

    os.makedirs(WORK, exist_ok=True)
    verdict = {}
    for tag, cells in sorted(todo.items(), key=lambda kv: int(kv[0].split("cls")[1])):
        m = f"{model}-{tag.split('-', 1)[1]}"
        sc = os.path.join(WORK, re.sub(r"\W+", "_", os.path.basename(st) + "_" + tag) + ".mg5")
        log = sc[:-4] + ".log"
        # MadGraph aborts a -f script at the first exception, and NoDiagramException is one, so
        # without this a card with several missing cells resolves only the first.
        open(sc, "w").write("\n".join(["set crash_on_error False", f"import model {m}"]
                                      + [f"generate {p} {ORDER}" for p in cells]) + "\n")
        subprocess.run(["nice", "-n", "19", PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc],
                       stdout=open(log, "w"), stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, check=False)
        txt = open(log, errors="replace").read()
        parts = re.split(r"^generate ", txt, flags=re.M)[1:]
        for p, seg in zip(cells, parts):
            if "NoDiagramException" in seg or "No amplitudes generated" in seg:
                v = "NO_DIAGRAMS"
            elif re.search(r"Process has \d+ diagrams", seg) or re.search(r"\d+ processes with \d+ diagrams", seg):
                v = "NOT_INTEGRATED"
            else:
                v = "UNRESOLVED"
            verdict[(p, tag)] = v
            print(f"{tag:<16s} {p:<22s} {v}", flush=True)

    n = {v: sum(1 for x in verdict.values() if x == v) for v in set(verdict.values())}
    print("\n" + ", ".join(f"{k}: {v}" for k, v in sorted(n.items())))
    if write:
        blank = {k: "" for k in head}
        out = ["\t".join(head)] + ["\t".join(r) for r in rows]
        for (p, tag), v in sorted(verdict.items()):
            if v == "UNRESOLVED":
                continue
            r = dict(blank, process=p, model=tag, order=ORDER, sigma_pb=v, error_pb="-",
                     nevents="0", settings="diagram generation only")
            out.append("\t".join(r.get(k, "") for k in head))
        open(os.path.join(st, "results.tsv"), "w").write("\n".join(out) + "\n")
        print(f"wrote {st}/results.tsv")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
