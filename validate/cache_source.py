#!/usr/bin/env python3
"""Which source a cached vertex block was built from, and whether that is still the source.

    python3 validate/cache_source.py stamp <cache dir> <block> [<block> ...]
    python3 validate/cache_source.py check <cache dir>[;<cache dir> ...] [<block list file>] [--strict]
    python3 validate/cache_source.py stale <cache dir> <block>
    python3 validate/cache_source.py hash <block>
    python3 validate/cache_source.py backstamp <cache dir> [--repo DIR] [--write]

The vertex cache is keyed on the block name alone, so without a check a block built before its
operator changed stays in the cache and goes into the next model, and nothing in the build notices.

A stamp is a hash of the code a block is built from, comments and whitespace removed, written into
its .status line as "src <hex>":
  L8op<n>  the definition of the block in tests/gen_smoke/gen.fr, the text from "L8op<n> :=" to the
           next block (a dimension-eight block does not depend on the base model),
  L6cl<x>  tests/gen_smoke/dim6_smeftsim.fr together with the input-scheme base the block was built
           on, on whose first-order corrections the dimension-six operators are evaluated: the files
           DIM8_BASE names besides dim6_smeftsim.fr ("base_inputscheme_mw.fr;dim6_smeftsim.fr" for the
           {MW, MZ, GF} model), base_inputscheme.fr when DIM8_BASE is unset.  The worker and the
           writer both pass DIM8_BASE on, so a dimension-six cache built on one scheme's base reads
           as stale when a model is written on the other's.  DIM8_L6BASES, when set, names these files in
           place of DIM8_BASE, for a model whose own base is another (the models of order n below).
  G8op<n>, T<d>op<n>  the blocks of the models of order n (gen/towers.py): the definition of the block in
           the gen_geo<n>.fr that DIM8_BASE names, together with the other files DIM8_BASE names except
           the dimension-six one, since the corrections the block carries to order n - p come from the base,
  G6cl<x>  the dimension-six file of such a model (dim6_geo<n>.fr in DIM8_BASE) together with the same base.
validate/fr_worker.wls stamps every block it builds.  Before it skips a cached block it asks `stale`,
which exits 0 when the stamp differs from the current source and 1 otherwise, and it rebuilds a stale
block.  Any failure to run this script therefore reads as not stale, and the writer still stops on the
block: `check` recomputes the hashes of the blocks in the cache directories (or those named in a block
list) and exits 1 when any stamp differs from the current source, so that validate/fr_writeufo.wls,
which calls it before loading anything, stops instead of writing a model from a stale block.  A block
without a stamp says nothing about its source: `check` names how many and does not stop for them, and
the worker skips them, and with --strict `check` stops for them too, and for a block of the list that no cache
holds, as hpc/build_geo.sh asks before it writes a model.  ./dim8 build gives one the stamp of the old code when it changes the block's
definition in gen.fr, `backstamp` does it for a whole cache, and ./dim8 rebuild takes no block without
a stamp, since it would release a model from such a block with only this count to show for it.

`backstamp` checks every status line without a stamp against the git history of tests/gen_smoke/gen.fr
in the checkout --repo names (by default this one).  The date of a block is the file date of its .mx,
which rsync -a and cp -p keep and which the Hermiticity-only pass of the worker, rewriting only the
.status, leaves alone.  A block agrees when its code is the same in the version of gen.fr committed last
before that date, in every later version and in the file on disk.  The later versions are in the test
since a build can run on a gen.fr that is committed afterwards, so that the version in force at the
date cannot by itself prove what the block was built from, and such a block is listed for a rebuild
although its vertices may be current.  A block that agrees gets the stamp of the current source.  Any
other gets the stamp of the version in force at its date, which reads as stale, so that the worker rebuilds
it and the writer stops on it until then.  It gets zeros when no version defines the block, or when its code
has come back to that form since, where that stamp would read as current.  The report lists those.  Without
--write nothing is written.  A block held only as .wxf has the file date of its conversion, and a
dimension-six block has its source outside gen.fr, so those are listed and left alone.  A cache copied
without its file dates reads as younger than it is, so run this on the cache as the build left it, or on
an rsync -a copy, and copy the status lines to the other caches.

Believe it when: stamping a block and then editing its definition in gen.fr makes `check` fail on
that block alone, and `stale` exit 0 for it.
"""
import hashlib
import os
import re
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SMOKE = os.path.join(ROOT, "tests", "gen_smoke")
GEN_IN_REPO = "tests/gen_smoke/gen.fr"
# the stamp of a block that has to be rebuilt and has no stamp of its own to read as stale, which no source hashes to
NO_VERSION = "0" * 16


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


def _blocks_of(gen_text, pattern=r"L8op\d+"):
    """block name -> its definition text in gen.fr (or, with the pattern of gen/towers.py's names, in
    gen_geo<n>.fr)"""
    starts = [(m.group(1), m.start()) for m in re.finditer(rf"^({pattern}) :=", gen_text, re.M)]
    out = {}
    for i, (name, a) in enumerate(starts):
        b = starts[i + 1][1] if i + 1 < len(starts) else len(gen_text)
        out[name] = gen_text[a:b]
    return out


def _hash_of(text):
    """The stamp of the definition of a dimension-eight block, 16 hex digits."""
    return hashlib.sha256(_code(text).encode()).hexdigest()[:16]


_GEN = {}


def use_gen_text(text):
    """Take the source of the dimension-eight blocks from this text instead of gen.fr on disk.
    ./dim8 build compares the cache with the text it is about to write, which its --dry-run does
    not write at all."""
    _GEN[SMOKE] = _blocks_of(text)


def changed_blocks(old_text, new_text):
    """block -> the stamp of its old code, for the blocks defined in both texts whose code differs"""
    old, new = _blocks_of(old_text), _blocks_of(new_text)
    return {b: _hash_of(old[b]) for b in new
            if b in old and old[b] != new[b] and _hash_of(old[b]) != _hash_of(new[b])}


def _l6_bases():
    """The base files a dimension-six block is evaluated on, in the order DIM8_BASE lists them, or
    DIM8_L6BASES when it is set.  With both unset this is base_inputscheme.fr alone, the base of the
    {alpha, MZ, GF} cache."""
    names = [f.strip() for f in os.environ.get("DIM8_L6BASES", os.environ.get("DIM8_BASE", "")).split(";")
             if f.strip()]
    names = [f for f in names if f != "dim6_smeftsim.fr"]
    return names or ["base_inputscheme.fr"]


def source_hash(block, smoke=None, bases=None):
    """The stamp of a block from the current source files, 16 hex digits.  bases names the base files
    of a dimension-six block, in place of what DIM8_BASE says."""
    smoke = smoke or SMOKE
    if block.startswith("L8op"):
        if smoke not in _GEN:
            _GEN[smoke] = _blocks_of(open(os.path.join(smoke, "gen.fr")).read())
        if block not in _GEN[smoke]:
            raise KeyError(f"{block} is not defined in {os.path.join(smoke, 'gen.fr')}")
        return _hash_of(_GEN[smoke][block])
    if block.startswith("L6"):
        h = hashlib.sha256()
        for f in ["dim6_smeftsim.fr"] + (_l6_bases() if bases is None else list(bases)):
            h.update(_code(open(os.path.join(smoke, f)).read()).encode())
        return h.hexdigest()[:16]
    if re.match(r"^(G8op\d+|T\d+op\d+|G6cl\w+)$", block):
        names = [f.strip() for f in os.environ.get("DIM8_BASE", "").split(";") if f.strip()]
        gen = [f for f in names if re.match(r"^gen_geo\d+\.fr$", f)]
        dim6 = [f for f in names if re.match(r"^dim6_geo\d*\.fr$", f)]
        base = [f for f in names if f not in gen + dim6]
        h = hashlib.sha256()
        if block.startswith("G6cl"):
            if len(dim6) != 1:
                raise KeyError(f"{block}: DIM8_BASE names no single dim6_geo file: {names}")
            h.update(_code(open(os.path.join(smoke, dim6[0])).read()).encode())
        else:
            if len(gen) != 1:
                raise KeyError(f"{block}: DIM8_BASE names no single gen_geo file: {names}")
            key = (smoke, gen[0])
            if key not in _GEN:
                _GEN[key] = _blocks_of(open(os.path.join(smoke, gen[0])).read(), r"G8op\d+|T\d+op\d+")
            if block not in _GEN[key]:
                raise KeyError(f"{block} is not defined in {os.path.join(smoke, gen[0])}")
            h.update(_code(_GEN[key][block]).encode())
        for f in base:
            h.update(_code(open(os.path.join(smoke, f)).read()).encode())
        return h.hexdigest()[:16]
    raise KeyError(f"no source rule for {block}")


def _stamp_in(status_path):
    """The stamp written in a .status file, or None.  errors="replace": a status file written by a
    Wolfram kernel on another platform can carry a non-UTF-8 byte."""
    if not os.path.exists(status_path):
        return None
    m = re.search(r"\bsrc ([0-9a-f]+)", open(status_path, errors="replace").read())
    return m.group(1) if m else None


def write_stamp(vdir, block, stamp_hex):
    """Write a stamp into the .status line of a block, replacing the one it has."""
    st = os.path.join(vdir, block + ".status")
    line = re.sub(r"\s*\|\s*src [0-9a-f]+", "", open(st, errors="replace").read().rstrip("\n"))
    open(st, "w").write(f"{line} | src {stamp_hex}\n")


def state(vdir, block, bases=None):
    """What a cache holds of a block, as the worker reads it: "missing" without a vertex file (.mx or
    .wxf) and a status line, "unstamped", "current", or "stale" when the stamp differs from the
    current source."""
    st = os.path.join(vdir, block + ".status")
    if not os.path.exists(st) or not any(os.path.exists(os.path.join(vdir, block + e)) for e in (".mx", ".wxf")):
        return "missing"
    have = _stamp_in(st)
    if have is None:
        return "unstamped"
    return "current" if have == source_hash(block, bases=bases) else "stale"


def stamp(vdir, blocks):
    for b in blocks:
        st = os.path.join(vdir, b + ".status")
        if not os.path.exists(st):
            sys.exit(f"{st} does not exist: build the block before stamping it")
        write_stamp(vdir, b, source_hash(b))
    print(f"stamped {len(blocks)} block(s) in {vdir}")
    return 0


def check(vdirs, blocks=None, strict=False):
    found = {}
    for d in vdirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            m = re.match(r"^((L8op\d+)|(L6cl\w+?)|(G6cl\w+?)|(G8op\d+)|(T\d+op\d+))\.(mx|wxf)$", f)
            if m and "." not in m.group(1):
                found.setdefault(m.group(1), d)
    names = sorted(found if blocks is None else [b for b in blocks if b in found])
    stale, unstamped = [], []
    for b in names:
        have = _stamp_in(os.path.join(found[b], b + ".status"))
        if have is None:
            unstamped.append(b)
        elif have != source_hash(b):
            stale.append(b)
    print(f"cache source check: {len(names)} blocks, {len(stale)} built from a different source, "
          f"{len(unstamped)} without a stamp (built before the check existed)")
    if stale:
        print("  stale: " + " ".join(stale[:30]) + (" ..." if len(stale) > 30 else ""))
        print("  rebuild them before writing a model: ./dim8 build a dimension-eight block, ./dim8 rebuild a "
              "dimension-six one, or validate/fr_worker.wls either")
    if not strict:
        return 1 if stale else 0
    missing = sorted(set(blocks or []) - set(found))
    if unstamped:
        print("  without a stamp (--strict): " + " ".join(unstamped[:30]) + (" ..." if len(unstamped) > 30 else ""))
    if missing:
        print(f"  in no cache (--strict): {len(missing)}: " + " ".join(missing[:30]) + (" ..." if len(missing) > 30 else ""))
    return 1 if stale or unstamped or missing else 0


def _block_key(b):
    """L8op<n> numerically, anything else by name after them."""
    return (0, int(b[4:]), "") if b.startswith("L8op") and b[4:].isdigit() else (1, 0, b)


def gen_versions(repo):
    """The committed versions of gen.fr in a checkout, oldest first, as (commit time, short hash,
    block -> stamp).  The commit time is the committer's, the later of the two dates of a commit,
    which can only send a block to an older version and so to a rebuild."""
    def git(*args):
        r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True, errors="replace")
        if r.returncode:
            sys.exit(f"git {' '.join(args)} failed in {repo}: {r.stderr.strip()}")
        return r.stdout

    rows = [line.split() for line in git("log", "--format=%H %ct", "--", GEN_IN_REPO).splitlines() if line.strip()]
    if not rows:
        sys.exit(f"{repo} has no history of {GEN_IN_REPO}")
    return [(int(when), sha[:7], {b: _hash_of(t) for b, t in _blocks_of(git("show", f"{sha}:{GEN_IN_REPO}")).items()})
            for sha, when in sorted(rows, key=lambda r: int(r[1]))]


def against_history(versions, block, when, current):
    """(whether a block built at time `when` agrees with the current source, the stamp of the version
    in force at that time, that version's short hash).  See the module docstring for the rule."""
    i = None
    for k, (t, _, _) in enumerate(versions):
        if t <= when:
            i = k
    if i is None:
        return False, NO_VERSION, None
    then = versions[i][2].get(block)
    if then is None:
        return False, NO_VERSION, versions[i][1]
    return all(v[2].get(block) == current for v in versions[i:]), then, versions[i][1]


def backstamp(vdir, repo=None, write=False):
    """Check the status lines without a stamp against the history of gen.fr, report, and with write
    give each its stamp.  See the module docstring."""
    versions = gen_versions(repo or ROOT)
    names = sorted((f[:-len(".status")] for f in os.listdir(vdir)
                    if f.endswith(".status") and not f.startswith(".") and f.count(".") == 1), key=_block_key)
    stamped, agree, rebuild, undated, other, per_version = [], [], [], [], [], {}
    for b in names:
        if _stamp_in(os.path.join(vdir, b + ".status")) is not None:
            stamped.append(b)
            continue
        try:
            current = source_hash(b) if b.startswith("L8op") else None
        except KeyError:
            current = None
        if current is None:
            other.append(b)
            continue
        mx = os.path.join(vdir, b + ".mx")
        if not os.path.exists(mx):
            undated.append(b)
            continue
        ok, then, version = against_history(versions, b, os.path.getmtime(mx), current)
        per_version[version] = per_version.get(version, 0) + 1
        # A block listed for a rebuild must read as stale.  The stamp of its version would read as
        # current if its code changed after that version and has since come back to the same form.
        (agree if ok else rebuild).append((b, current if ok else NO_VERSION if then == current else then))
    print(f"backstamp: {len(names)} status lines in {vdir}, {len(stamped)} already stamped, {len(agree)} agree "
          f"with the gen.fr of their date, {len(rebuild)} need a rebuild")
    dates = {sha: time.strftime("%Y-%m-%d %H:%M", time.gmtime(t)) for t, sha, _ in versions}
    for version in sorted(per_version, key=lambda v: dates.get(v, "")):
        where = f"{version} ({dates[version]} UTC)" if version else "no version, built before the first one"
        print(f"  dated at gen.fr {where}: {per_version[version]} blocks")
    if rebuild:
        print("  need a rebuild: " + " ".join(b for b, _ in rebuild))
    if undated:
        print(f"  no .mx, so no build date, left alone ({len(undated)}): " + " ".join(undated[:30]) + (" ..." if len(undated) > 30 else ""))
    if other:
        print(f"  source outside gen.fr, left alone ({len(other)}): " + " ".join(other[:30]) + (" ..." if len(other) > 30 else ""))
    if not write:
        print("  nothing written: --write stamps the blocks that agree and marks the others stale")
        return 0
    for b, hex_ in agree + rebuild:
        write_stamp(vdir, b, hex_)
    print(f"  stamped {len(agree)} blocks with the current source, marked {len(rebuild)} stale")
    return 0


def main(argv):
    if len(argv) < 3:
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
        rest = [x for x in argv[3:] if x != "--strict"]
        blocks = [l.strip() for l in open(rest[0]) if l.strip()] if rest else None
        return check(vdirs, blocks, "--strict" in argv[3:])
    if cmd == "stale" and len(argv) == 4:
        return 0 if state(os.path.expanduser(argv[2]), argv[3]) == "stale" else 1
    if cmd == "backstamp":
        rest = argv[3:]
        repo = os.path.expanduser(rest[rest.index("--repo") + 1]) if "--repo" in rest else None
        return backstamp(os.path.expanduser(argv[2]), repo, "--write" in rest)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
