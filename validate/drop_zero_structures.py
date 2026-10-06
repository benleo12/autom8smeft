#!/usr/bin/env python3
"""Remove identically vanishing Lorentz structures from a written UFO, in place.

    validate/drop_zero_structures.py <UFO dir> [--dry-run]     (needs numpy: python3.13 here)

The structures come from validate/zero_vertex.py, which evaluates every structure at random
momenta obeying momentum conservation, with random polarisations for the vector legs and generic
four-component wavefunctions for the fermion legs.  Generic rather than on-shell on purpose: a
structure ALOHA will reduce to zero is one that vanishes as an expression, not one that happens
to vanish on shell.

Why this exists as its own step rather than as a few lines inside the release script.  The release
script used validate/zero_lorentz.py, which tests each structure alone and skips anything carrying
a Gamma matrix.  That reports nothing on the released model while nine structures in it are zero,
on fifty vertices, and it also assumed the vertices carrying them are pure, i.e. that every
structure of the vertex is zero so the whole vertex can go.  Thirty-five of the fifty are mixed,
and dropping a mixed vertex would delete live physics while leaving it in place keeps the dead
structure referenced, which is the case that matters: ALOHA reduces the routine to zero, omits the
declarations of the arguments it no longer uses, and the generated Fortran fails to compile with
"Symbol 'f1' at (1) has no IMPLICIT type" on any process reaching that vertex.  So a mixed vertex
has to be edited rather than dropped, and the edit is not a deletion of one list entry: a UFO
vertex keys its couplings by position in its own lorentz list, {(colour, lorentz): coupling}, so
removing an entry renumbers every index above it.
"""
from __future__ import annotations

import os
import re
import subprocess
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def zero_structures(ufo: str) -> set[str]:
    """The identically vanishing structures of this UFO, from zero_vertex.py."""
    py = shutil.which("python3.13") or shutil.which("python3")
    r = subprocess.run([py, os.path.join(HERE, "zero_vertex.py"), ufo, "--structures"],
                       capture_output=True, text=True)
    m = re.search(r"identically zero (\d+)\s*\n\s*(.*)", r.stdout)
    if not m:
        raise SystemExit("zero_vertex.py did not run (needs numpy, python3.13 here):\n"
                         + (r.stdout + r.stderr)[-800:])
    names = m.group(2).split()
    if len(names) != int(m.group(1)):
        raise SystemExit(f"zero_vertex.py reported {m.group(1)} but named {len(names)}")
    return set(names)


def rewrite_vertices(text: str, zero: set[str]) -> tuple[str, int, int, int]:
    """Drop the zero structures from every vertex, renumbering the coupling keys.

    Returns the new text, the number of vertices deleted outright, the number edited, and the
    number of coupling entries removed from the edited ones.
    """
    out, dropped, edited, lost = [], 0, 0, 0
    for block in re.split(r"\n\n", text):
        if not re.match(r"\s*V_\d+ = Vertex\(", block):
            out.append(block)
            continue
        lm = re.search(r"lorentz = \[(.*?)\]", block, re.S)
        cm = re.search(r"couplings = \{(.*?)\}", block, re.S)
        names = re.findall(r"L\.(\w+)", lm.group(1)) if lm else []
        if not names or not (set(names) & zero):
            out.append(block)
            continue
        keep = [i for i, n in enumerate(names) if n not in zero]
        if not keep:
            dropped += 1                    # every structure of this vertex is zero
            continue
        newpos = {old: new for new, old in enumerate(keep)}
        pairs = re.findall(r"\((\d+),(\d+)\):(C\.\w+)", cm.group(1)) if cm else []
        newpairs, gone = [], 0
        for c, l, coup in pairs:
            if int(l) in newpos:
                newpairs.append(f"({c},{newpos[int(l)]}):{coup}")
            else:
                gone += 1
        block = block.replace(lm.group(0),
                              "lorentz = [ " + ", ".join(f"L.{names[i]}" for i in keep) + " ]")
        if cm:
            block = block.replace(cm.group(0), "couplings = {" + ",".join(newpairs) + "}")
        edited += 1
        lost += gone
        out.append(block)
    return "\n\n".join(out), dropped, edited, lost


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    ufo = os.path.abspath(argv[1])
    dry = "--dry-run" in argv
    zero = zero_structures(ufo)
    # FeynRules can also emit the literal structure '0', which no numerical test is needed for.
    L = open(os.path.join(ufo, "lorentz.py")).read()
    zero |= set(re.findall(
        r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '0'\)", L))
    if not zero:
        print("no identically vanishing Lorentz structures")
        return 0
    print(f"{len(zero)} identically vanishing structures: {' '.join(sorted(zero))}")

    V = open(os.path.join(ufo, "vertices.py")).read()
    V2, dropped, edited, lost = rewrite_vertices(V, zero)
    still = set(re.findall(r"L\.(\w+)", V2))
    stillc = set(re.findall(r"C\.(\w+)", V2))
    orphanL = sorted(zero - still)
    C = open(os.path.join(ufo, "couplings.py")).read()
    allc = set(re.findall(r"^(GC_\d+) = Coupling\(", C, re.M))
    orphanC = sorted(allc - stillc)
    print(f"vertices deleted {dropped}, vertices edited {edited}, "
          f"coupling entries removed from edited vertices {lost}")
    print(f"Lorentz entries now unreferenced {len(orphanL)}, couplings now unreferenced {len(orphanC)}")
    if dry:
        return 0

    for z in orphanL:
        L = re.sub(rf"(?<!\w){z} = Lorentz\(.*?\)\n\n", "", L, flags=re.S)
    for c in orphanC:
        C = re.sub(rf"(?<!\w){c} = Coupling\(.*?\)\n\n", "", C, flags=re.S)
    # All three files or none.  A vertices.py that has been renumbered against a couplings.py that
    # has not is a model that imports and gives wrong numbers, which is worse than one that fails,
    # so every file is staged beside its target and the renames happen together at the end.
    new = {"vertices.py": V2.rstrip("\n") + "\n", "lorentz.py": L, "couplings.py": C}
    for name, body in new.items():
        with open(os.path.join(ufo, name + ".part"), "w") as f:
            f.write(body)
    for name in new:
        os.replace(os.path.join(ufo, name + ".part"), os.path.join(ufo, name))
    print(f"rewrote {', '.join(new)} in {ufo}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
