#!/usr/bin/env python3
"""Which source a cached vertex block was built from, and whether that is still the source.

    python3 validate/cache_source.py stamp <cache dir> <block> [<block> ...]
    python3 validate/cache_source.py check <cache dir>[;<cache dir> ...] [<block list file>]
    python3 validate/cache_source.py hash <block>

The vertex cache is keyed on the block name alone, so a block built before its operator changed
stays in the cache and goes into the next model.  That happened once: the dimension-six blocks of
2026-09-17 predate the subtraction of the vacuum piece of O_HG (2026-10-05), a cluster rebuild took
them, and the dimension-six sector of that dim68_is lost the subtraction and the second-order terms
of the operator file.  Nothing in the build noticed.

A stamp is a hash of the code a block is built from, comments and whitespace removed, written into
its .status line as "src <hex>":
  L8op<n>  the definition of the block in tests/gen_smoke/gen.fr, the text from "L8op<n> :=" to the
           next block (a dimension-eight block does not depend on the base model);
  L6cl<x>  tests/gen_smoke/dim6_smeftsim.fr together with tests/gen_smoke/base_inputscheme.fr, on
           whose first-order corrections the dimension-six operators are evaluated.
validate/fr_worker.wls stamps every block it builds.  `check` recomputes the hashes of the blocks
in the cache directories (or those named in a block list) and exits 1 when any stamp differs from
the current source, so that validate/fr_writeufo.wls, which calls it before loading anything,
stops instead of writing a model from a stale block.  A block without a stamp was built before the
guard existed: `check` names how many and does not stop for them.

Believe it when: stamping a block and then editing its definition in gen.fr makes `check` fail on
that block alone.
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "tests", "gen_smoke")


def _code(text):
    """FeynRules source with its (* comments *) removed and whitespace collapsed, so that a stamp
    changes with the code and not with a reworded comment"""
    out, depth, i = [], 0, 0
    while i < len(text):
        if text.startswith("(*", i):
            depth, i = depth + 1, i + 2
            continue
        if depth and text.startswith("*)", i):
            depth, i = depth - 1, i + 2
            continue
        if not depth:
            out.append(text[i])
        i += 1
    return re.sub(r"\s+", " ", "".join(out)).strip()


def _blocks_of(gen_text):
    """block name -> its definition text in gen.fr"""
    starts = [(m.group(1), m.start()) for m in re.finditer(r"^(L8op\d+) :=", gen_text, re.M)]
    out = {}
    for i, (name, a) in enumerate(starts):
        b = starts[i + 1][1] if i + 1 < len(starts) else len(gen_text)
        out[name] = gen_text[a:b]
    return out


_GEN = {}


def source_hash(block, smoke=None):
    """The stamp of a block from the current source files, 16 hex digits."""
    smoke = smoke or SMOKE
    h = hashlib.sha256()
    if block.startswith("L8op"):
        if smoke not in _GEN:
            _GEN[smoke] = _blocks_of(open(os.path.join(smoke, "gen.fr")).read())
        if block not in _GEN[smoke]:
            raise KeyError(f"{block} is not defined in {os.path.join(smoke, 'gen.fr')}")
        h.update(_code(_GEN[smoke][block]).encode())
    elif block.startswith("L6"):
        for f in ("dim6_smeftsim.fr", "base_inputscheme.fr"):
            h.update(_code(open(os.path.join(smoke, f)).read()).encode())
    else:
        raise KeyError(f"no source rule for {block}")
    return h.hexdigest()[:16]


def stamp(vdir, blocks):
    for b in blocks:
        st = os.path.join(vdir, b + ".status")
        if not os.path.exists(st):
            sys.exit(f"{st} does not exist: build the block before stamping it")
        line = re.sub(r"\s*\|\s*src [0-9a-f]+", "", open(st).read().rstrip("\n"))
        open(st, "w").write(f"{line} | src {source_hash(b)}\n")
    print(f"stamped {len(blocks)} block(s) in {vdir}")
    return 0


def check(vdirs, blocks=None):
    found = {}
    for d in vdirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            m = re.match(r"^((L8op\d+)|(L6cl\w+?))\.(mx|wxf)$", f)
            if m and "." not in m.group(1):
                found.setdefault(m.group(1), d)
    names = sorted(found if blocks is None else [b for b in blocks if b in found])
    stale, unstamped = [], []
    for b in names:
        st = os.path.join(found[b], b + ".status")
        txt = open(st).read() if os.path.exists(st) else ""
        m = re.search(r"\bsrc ([0-9a-f]+)", txt)
        if not m:
            unstamped.append(b)
        elif m.group(1) != source_hash(b):
            stale.append(b)
    print(f"cache source check: {len(names)} blocks, {len(stale)} built from a different source, "
          f"{len(unstamped)} without a stamp (built before the check existed)")
    if stale:
        print("  stale: " + " ".join(stale[:30]) + (" ..." if len(stale) > 30 else ""))
        print("  rebuild them (delete the .mx and .status, rerun validate/fr_worker.wls) before writing a model")
    return 1 if stale else 0


def main(argv):
    if len(argv) < 3 and not (len(argv) == 3 and argv[1] == "hash"):
        print(__doc__)
        return 2
    cmd = argv[1]
    if cmd == "hash":
        print(source_hash(argv[2]))
        return 0
    if cmd == "stamp":
        return stamp(argv[2], argv[3:])
    if cmd == "check":
        vdirs = [os.path.expanduser(d.strip()) for d in argv[2].split(";") if d.strip()]
        blocks = None
        if len(argv) > 3:
            blocks = [l.strip() for l in open(argv[3]) if l.strip()]
        return check(vdirs, blocks)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
