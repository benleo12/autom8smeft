#!/usr/bin/env python3
"""Merge rows from one study's results.tsv into another's, replacing failed rows.

    examples/studies/merge_rows.py <source results.tsv> <target results.tsv> [--replace]

A row is identified by (process, model, order).  A source row replaces a target row with the same
key whose sigma is FAILED, NO_OUTPUT or BAD_SETTING, or one that is absent.  Healthy target rows
are left alone and the source row is reported as skipped, unless --replace is given, in which case
every source row replaces its target row (for instance to restore event files when the numbers
are right but the files are not).  The LHE file named in a merged row is copied into the target
study's lhe/ directory.  This folds reruns (a scratch study with one process and no classes) back
into the paper's studies without re-running what worked.

A row travels with its record (provenance.py): the record replaces the target's record of that
row, and the copies of its param, run and restriction cards go into the target's cards/.  A source row with no
record is not merged, since the target's tables would then hold a number no run can be traced to.
"""
import os, shutil, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import provenance as P  # noqa: E402


def main(argv):
    if len(argv) < 3:
        print(__doc__); return 2
    src, dst = argv[1], argv[2]; replace = "--replace" in argv
    S = [l.rstrip("\n").split("\t") for l in open(src)]; D = [l.rstrip("\n").split("\t") for l in open(dst)]
    hs, hd = S[0], D[0]
    if hs != hd:
        print("column headers differ:", hs, hd); return 2
    if not os.path.exists(P.records_path(src)):
        print(f"{src} has no records file {os.path.basename(P.records_path(src))}, so its rows cannot be traced to a run and none is merged")
        return 2
    hr, recs = P.read_tsv(P.records_path(src))
    srec = {}
    for x in recs:
        d = P.as_dict(hr, x)
        srec.setdefault(P.key(d), []).append(d)
    # the target's results and records are read, changed and written back under the lock every writer of its
    # records holds, so that a row run_study.sh appends to the target meanwhile is not lost
    with P.records_lock(P.records_path(dst)):
        return merge(src, dst, replace, hs, srec)


def copy_into(s, d):
    """Copy s to d through a temporary file of its own beside d, renamed into place."""
    os.makedirs(os.path.dirname(d), exist_ok=True)
    fd, t = tempfile.mkstemp(dir=os.path.dirname(d), prefix=os.path.basename(d) + ".", suffix=".part")
    os.close(fd)
    shutil.copy(s, t)
    os.replace(t, d)


def merge(src, dst, replace, hs, srec):
    S = [l.rstrip("\n").split("\t") for l in open(src)]; D = [l.rstrip("\n").split("\t") for l in open(dst)]
    T = P.read_records(P.records_path(dst))
    k = lambda r: (r[0].strip(), r[1].strip(), r[2].strip())
    bad = {"FAILED", "NO_OUTPUT", "BAD_SETTING"}
    idx = {k(r): i for i, r in enumerate(D[1:], start=1)}
    merged, skipped, untraced = 0, 0, []
    for r in S[1:]:
        if r[3] in bad: continue
        i = idx.get(k(r))
        if i is not None and D[i][3] not in bad and not replace:
            skipped += 1; continue
        rec = srec.get(k(r), [])
        if len(rec) != 1:
            untraced.append(" | ".join(k(r))); continue
        rec = dict(rec[0], process=r[0].strip())
        copies = [(rec.get(kind + "_card", "-"), f"{kind}_card.dat.gz") for kind in ("param", "run")]
        copies.append((rec.get("card_sha256", "-"), "restrict.dat.gz"))   # the restriction card
        copies.append((rec.get("same_card", "-"), "restrict.dat.gz"))     # the card it was found equal to
        for h, suffix in copies:
            name = f"{h}.{suffix}"
            s_card = os.path.join(os.path.dirname(src), "cards", name)
            d_card = os.path.join(os.path.dirname(dst), "cards", name)
            if h not in ("", "-") and os.path.exists(s_card) and not os.path.exists(d_card):
                copy_into(s_card, d_card)
        lhe = r[hs.index("lhe")]
        if lhe != "-":
            s_lhe = os.path.join(os.path.dirname(src), lhe); d_lhe = os.path.join(os.path.dirname(dst), lhe)
            if os.path.exists(s_lhe): copy_into(s_lhe, d_lhe)
        r = [r[0].strip()] + r[1:]   # a rerun's process field may carry the spacing of its processes.txt line
        if i is not None: D[i] = r
        else: D.append(r)
        T = [t for t in T if P.key(t) != P.key(rec)] + [rec]
        merged += 1
    P._put(dst, ("\n".join("\t".join(r) for r in D) + "\n").encode())
    P.write_records(P.records_path(dst), T)
    print(f"merged {merged} rows into {dst} with their records, skipped {skipped} healthy ones")
    for u in untraced:
        print(f"   not merged, no record in {os.path.basename(P.records_path(src))}: {u}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
