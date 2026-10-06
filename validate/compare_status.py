#!/usr/bin/env python3
"""Compare vertex counts block by block between a backup of status lines and a live cache.

usage: validate/compare_status.py <backup .tgz or directory of .status> <cache directory>

Written for the 2026-09-03 rebuild after the unsound colour zero test: it lists every block
whose vertex count changed, so the damage the test did is quantified rather than assumed.
Status lines look like  'L8op455 | vertices 6 | rawvertices 6 | nonhermitian -1 | ...'.
"""
import os, re, sys, tarfile, glob

def parse(text):
    m = re.search(r'(L8op\d+) \| vertices (\d+) \| rawvertices (\d+)', text)
    return (m.group(1), int(m.group(2)), int(m.group(3))) if m else None

def load_backup(path):
    out = {}
    if os.path.isdir(path):
        for f in glob.glob(os.path.join(path, 'L8op*.status')):
            r = parse(open(f, errors='replace').read())
            if r: out[r[0]] = r[1:]
    else:
        with tarfile.open(path) as t:
            for m in t.getmembers():
                if m.name.endswith('.status'):
                    r = parse(t.extractfile(m).read().decode(errors='replace'))
                    if r: out[r[0]] = r[1:]
    return out

def main():
    if len(sys.argv) < 3:
        print(__doc__ or "usage: validate/compare_status.py <backup> <cache directory>")
        return 2
    old = load_backup(sys.argv[1]); new = load_backup(sys.argv[2])
    common = sorted(set(old) & set(new), key=lambda b: int(b[4:]))
    changed = [(b, old[b], new[b]) for b in common if old[b][0] != new[b][0]]
    lost = sum(n[0] - o[0] for b, o, n in changed)
    print(f"blocks in both: {len(common)}, changed vertex count: {len(changed)}, net vertices recovered: {lost}")
    for b, o, n in changed:
        print(f"{b}: {o[0]} -> {n[0]} vertices (raw {o[1]} -> {n[1]})")
    missing = sorted(set(old) - set(new), key=lambda b: int(b[4:]))
    if missing: print(f"not yet rebuilt: {len(missing)}: {' '.join(missing[:20])}{' ...' if len(missing) > 20 else ''}")

if __name__ == '__main__':
    main()
