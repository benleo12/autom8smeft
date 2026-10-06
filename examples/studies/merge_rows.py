#!/usr/bin/env python3
"""Merge rows from one study's results.tsv into another's, replacing failed rows.

    examples/studies/merge_rows.py <source results.tsv> <target results.tsv> [--replace]

A row is identified by (process, model, order).  A source row replaces a target row with the same
key whose sigma is FAILED, NO_OUTPUT or BAD_SETTING, or one that is absent; healthy target rows
are left alone and the source row is reported as skipped, unless --replace is given, in which case
every source row replaces its target row (used after the event files of a process had been
overwritten by a name collision, when the numbers were fine but the files were not).  The LHE file named in a merged row is
copied into the target study's lhe/ directory.  Used to fold reruns (a scratch study with one
process and no classes) back into the paper's studies without re-running what worked.
"""
import os, shutil, sys


def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    src, dst = argv[1], argv[2]; replace = "--replace" in argv
    S = [l.rstrip("\n").split("\t") for l in open(src)]; D = [l.rstrip("\n").split("\t") for l in open(dst)]
    hs, hd = S[0], D[0]
    if hs != hd:
        print("column headers differ:", hs, hd); return 2
    k = lambda r: (r[0].strip(), r[1].strip(), r[2].strip())
    bad = {"FAILED", "NO_OUTPUT", "BAD_SETTING"}
    idx = {k(r): i for i, r in enumerate(D[1:], start=1)}
    merged, skipped = 0, 0
    for r in S[1:]:
        if r[3] in bad: continue
        i = idx.get(k(r))
        if i is not None and D[i][3] not in bad and not replace:
            skipped += 1; continue
        lhe = r[hs.index("lhe")]
        if lhe != "-":
            s_lhe = os.path.join(os.path.dirname(src), lhe); d_lhe = os.path.join(os.path.dirname(dst), lhe)
            os.makedirs(os.path.dirname(d_lhe), exist_ok=True)
            if os.path.exists(s_lhe): shutil.copy(s_lhe, d_lhe)
        r = [r[0].strip()] + r[1:]   # a rerun's process field may carry the spacing of its processes.txt line
        if i is not None: D[i] = r
        else: D.append(r)
        merged += 1
    open(dst, "w").write("\n".join("\t".join(r) for r in D) + "\n")
    print(f"merged {merged} rows into {dst}, skipped {skipped} healthy ones")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
