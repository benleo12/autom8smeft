"""
validate/check_symbol_clash.py  --  V15.

Every emitted Lagrangian block scopes its index names.  If one of those names is also a
symbol the model defines, the scoping silently corrupts the model: with ``Block`` the
global value is cleared for the duration of the expansion, and even with ``Module`` a
name that the model uses can be shadowed.  Nothing warns.  Three real cases have been
found this way in this project:

  * a single-letter loop variable ``b`` clobbered the b quark (session 1),
  * ``ee`` is the electromagnetic coupling,
  * ``mu`` is the muon (``ClassMembers -> {e, mu, ta}``).

So the check is mechanical: read every symbol the base model declares, and assert that
the index pools and block locals are disjoint from it.  Run on every build.

Usage:  python3 validate/check_symbol_clash.py [base.fr ...]
Exit status 1 on any clash.
"""

from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "gen"))

from dsl import ALL_INDEX_NAMES  # noqa: E402
from emit_fr import BLOCK_LOCALS  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
DEFAULT_MODELS = [os.path.join(ROOT, "models", "base", "sm.fr")]


def model_symbols(path: str) -> dict:
    """Every name the model file declares: parameters, particle classes and their members,
    index names, gauge group names and coupling constants."""
    src = open(path).read()
    out = {}

    def add(kind, names):
        for n in names:
            n = n.strip()
            if n:
                out.setdefault(n, set()).add(kind)

    add("parameter", re.findall(r"^\s*([A-Za-z][A-Za-z0-9]*)\s*==\s*\{", src, re.M))
    add("class", re.findall(r"ClassName\s*->\s*([A-Za-z][A-Za-z0-9]*)", src))
    for g in re.findall(r"ClassMembers\s*->\s*\{([^}]*)\}", src):
        add("member", g.split(","))
    add("index", re.findall(r"IndexName\s*->\s*([A-Za-z][A-Za-z0-9]*)", src))
    add("index", re.findall(r"IndexRange\[\s*Index\[\s*([A-Za-z][A-Za-z0-9]*)", src))
    add("group", re.findall(r"^\s*([A-Za-z][A-Za-z0-9]*)\s*==\s*\{\s*Abelian", src, re.M))
    add("coupling", re.findall(r"CouplingConstant\s*->\s*([A-Za-z][A-Za-z0-9]*)", src))
    add("selfconj", re.findall(r"Unphysical\s*->\s*True[^}]*ClassName\s*->\s*([A-Za-z][A-Za-z0-9]*)", src))
    return out


REQUIRED_FLAGS = {
    # FeynRules builds DC as  del[f,mu] - I FR$DSign g A,  so FR$DSign = 1 (its default)
    # means D = d - i g A.  Murphy's basis defines D = d + i g A, so the flag must be -1.
    # Getting this wrong flips the sign of the gauge piece of every covariant derivative
    # in every operator, silently.  SMEFTsim sets the same value.
    "FR$DSign": "-1",
}


def check_flags(path: str) -> List[str]:
    src = open(path).read()
    bad = []
    for flag, want in REQUIRED_FLAGS.items():
        m = re.search(re.escape(flag) + r"\s*=\s*(-?[0-9]+)\s*;", src)
        if m is None:
            bad.append(f"{flag} is not set (FeynRules default applies, which is wrong here)")
        elif m.group(1) != want:
            bad.append(f"{flag} = {m.group(1)}, expected {want}")
    return bad


def check_comments(path: str) -> List[str]:
    """A stray '*)' inside a comment silently truncates it and the rest of the line
    becomes code.  This happened writing the header of this very file, where the text
    "newL8geo*)" ended the comment early.

    The scan tokenises rather than counting occurrences, because the three characters
    "(*)" would otherwise register as both an opener and a closer.  Mathematica comments
    nest, so depth is tracked rather than a single flag.
    """
    src = open(path).read()
    depth = i = 0
    line = 1
    bad = []
    while i < len(src) - 1:
        two = src[i:i + 2]
        if two == "(*":
            depth += 1
            i += 2
            continue
        if two == "*)":
            depth -= 1
            if depth < 0:
                bad.append(f"comment closed but never opened, line {line}")
                depth = 0
            i += 2
            continue
        if src[i] == "\n":
            line += 1
        i += 1
    if depth:
        bad.append(f"comment left open at end of file (depth {depth})")
    return bad


def main(paths) -> int:
    ours = set(ALL_INDEX_NAMES) | set(BLOCK_LOCALS.split(","))
    bad = []
    total = 0
    for p in paths:
        if not os.path.exists(p):
            print(f"  (skipped, not found: {p})")
            continue
        syms = model_symbols(p)
        total += len(syms)
        for n in sorted(ours & set(syms)):
            bad.append((os.path.basename(p), n, ",".join(sorted(syms[n]))))
    for p in paths:
        if os.path.exists(p):
            for msg in check_flags(p) + check_comments(p):
                bad.append((os.path.basename(p), msg, "convention"))
    print(f"V15 symbol clash: {len(ours)} emitted names vs {total} model symbols")
    if bad:
        print("FAIL:")
        for f, n, k in bad:
            print(f"  {f}: {n}  ({k})")
        return 1
    print("V15 PASS, no emitted name collides with a model symbol")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:] or DEFAULT_MODELS))
