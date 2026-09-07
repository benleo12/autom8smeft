"""
validate/compare_caches.py  --  consistency test between two vertex caches.

After the switch to the numeric-SU(2) dialect (validate/cutover_numeric.sh) the old cache,
built with FeynRules' own SU(2) expansion, is kept in build/vertices_flavexp.  For every
block that carries NO SU(2) tensor (no tau, no epsilon on SU(2) indices) the two dialects
differ only in bookkeeping, so their vertex counts must agree exactly.  A disagreement on
such a block means the new emission changed physics where it had no business to, and is
a bug.  Blocks that do carry SU(2) tensors are expected to differ (that was the point),
and are reported separately with the FeynRules charge warnings they produced.

Usage:  python3 validate/compare_caches.py [old_dir] [new_dir]
"""

from __future__ import annotations

import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


def read_status(d: str) -> dict:
    out = {}
    if not os.path.isdir(d):
        return out
    for f in os.listdir(d):
        if not f.endswith(".status") or f.startswith("."):   # skip macOS ._ sidecars
            continue
        s = open(os.path.join(d, f)).read()
        if "SKIPPED" in s:
            continue
        m = re.search(r"(L8op\d+) \| vertices (\d+)(?: \| rawvertices (\d+))? \| nonhermitian (\d+)", s)
        if m:
            out[m.group(1)] = dict(vertices=int(m.group(2)), raw=int(m.group(3) or m.group(2)), nonherm=int(m.group(4)))
    return out


def su2_tensor_blocks(model_path: str) -> set:
    """Blocks whose ORIGINAL (symbolic) emission carried tau or an SU(2) epsilon."""
    g = open(model_path).read()
    out = set()
    for m in re.finditer(r"(L8op\d+) := Module\[.*?\n\];\n", g, re.S):
        body = m.group(0)
        if re.search(r"\bTa\[|Eps\[z8[i-r],z8[i-r]\]|Eps\[z8[A-F],z8[A-F],z8[A-F]\]", body):
            out.add(m.group(1))
    return out


def main(old_dir: str, new_dir: str) -> int:
    old, new = read_status(old_dir), read_status(new_dir)
    idx = {b["block"]: b for b in json.load(open(os.path.join(ROOT, "docs", "block_index.json")))}
    # which blocks had SU(2) tensors, judged from the last symbolic model kept for the purpose
    sym_model = os.path.join(ROOT, "tests", "gen_smoke", "gen_flavexp.fr")
    su2 = su2_tensor_blocks(sym_model) if os.path.exists(sym_model) else set()
    both = sorted(set(old) & set(new), key=lambda b: int(b[4:]))
    same = diff_plain = diff_su2 = 0
    print(f"{len(both)} blocks in both caches ({len(old)} old, {len(new)} new)")
    for b in both:
        o, n = old[b], new[b]
        if o["raw"] == n["raw"] and o["nonherm"] == n["nonherm"]:
            same += 1
            continue
        tag = "SU2-tensor block, difference expected" if b in su2 else "PLAIN BLOCK, MUST NOT DIFFER"
        if b in su2:
            diff_su2 += 1
        else:
            diff_plain += 1
        print(f"  {b:8s} {idx[b]['ops'][0]:26s} old {o['raw']:4d}/{o['nonherm']:<4d} new {n['raw']:4d}/{n['nonherm']:<4d}  {tag}")
    print(f"identical: {same}, differ (SU2 tensors, expected): {diff_su2}, differ (plain, BUG): {diff_plain}")
    return 1 if diff_plain else 0


if __name__ == "__main__":
    a = sys.argv[1:]
    sys.exit(main(a[0] if a else os.path.join(ROOT, "build", "vertices_flavexp"),
                  a[1] if len(a) > 1 else os.environ.get("DIM8_VDIR", os.path.join(ROOT, "build", "vertices"))))
