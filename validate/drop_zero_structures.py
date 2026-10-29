#!/usr/bin/env python3
"""Remove identically vanishing Lorentz structures from a written UFO, in place.

    validate/drop_zero_structures.py <UFO dir> [--dry-run]     (zero_vertex.py needs numpy)

The structures come from validate/zero_vertex.py, which evaluates every structure at random
momenta obeying momentum conservation, with random polarisations for the vector legs and generic
four-component wavefunctions for the fermion legs.  Generic rather than on-shell on purpose: a
structure ALOHA will reduce to zero is one that vanishes as an expression, not one that happens
to vanish on shell.

A vertex that carries a zero structure is often mixed: some of its structures are zero and others
are not.  Dropping a mixed vertex would delete live physics.  Leaving it as it is keeps the dead
structure referenced, and then ALOHA reduces the routine to zero, omits the declarations of the
arguments it no longer uses, and the generated Fortran fails to compile with "Symbol 'f1' at (1)
has no IMPLICIT type" on any process reaching that vertex.  So a vertex whose structures are all
zero is deleted, and a mixed vertex is edited.  The edit is not a deletion of one list entry: a
UFO vertex keys its couplings by position in its own lorentz list, {(colour, lorentz): coupling},
so removing an entry renumbers every index above it.

A second kind of zero lives in a vertex rather than in a structure.  Two structures of one vertex
can each be nonzero and still cancel, when they carry couplings equal up to sign and their signed
sum vanishes.  Q_{q^4B}^{(4)} is the case: with flavour-universal coefficients its two quark
currents are identical, so the operator is symmetric in its Lorentz indices against an
antisymmetric field strength and vanishes, while FeynRules writes it as two structures that differ
by a relabelling inside one Epsilon and carry the same coupling.  MadGraph merges structures that
share a coupling into one routine, ALOHA reduces that routine to zero, and the process fails to
compile.  So, within each vertex and colour structure, the entries are grouped by coupling up to
sign, each group's signed sum is evaluated at a common random point, and a group that vanishes is
removed.

The same cancellation can be split over two vertices.  In the input-scheme models the vacuum piece
of Q_{G^2H^4}^{(1)} on the four-gluon vertex and the d8fG term that cancels it in the gluon kinetic
term are written into two vertices with the same legs, V_29 and V_30 of dim8_mw, with the colour
spelled f(-1,1,3)*f(-1,2,4) in one and f(-1,1,3)*f(2,4,-1) in the other.  The two are equal by
cyclicity, so the pair contributes nothing, but it leaves c8G2H4x1 on the four-gluon vertex for
anyone reading vertices.py to take as a shift of alpha_s.  So the groups are formed across every
vertex with the same legs in the same order, and colours are compared in a canonical spelling
(colour_key) with the sign that spelling costs.

A coefficient can also vanish as a whole without any single group doing so.  The field-strength
operators with two identical currents, such as Q_{q^4B}^{(2)}, are symmetric in the Lorentz
indices of an antisymmetric field strength and vanish for flavour-universal coefficients, but
some of their terms share couplings with live operators.  The third stage evaluates, for every
coefficient, its whole contribution to every vertex with all other coefficients at zero, at
common random points, and a coefficient whose contribution vanishes everywhere is set to zero in
the couplings, after which couplings that are identically zero and the entries that carry them
are removed.  All three stages run by default.
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
        raise SystemExit("zero_vertex.py did not run (needs numpy):\n"
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


def random_point(P, seed):
    """Values of every parameter at a random point: dimension-six and dimension-eight coefficients
    uniform in [0.3, 1.7], every other external input perturbed by up to 10 per cent, so that no
    test can depend on a default value (a Cabibbo-only CKM makes many couplings zero at the
    defaults without making them zero as expressions)."""
    import cmath, math, random
    ns = {"cmath": cmath, "math": math, "complex": complex,
          "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z}
    rnd = random.Random(seed)
    v = {}
    for p in P.all_parameters:
        if p.nature != "external":
            continue
        if p.lhablock in ("DIM8", "DIM6") and p.name not in ("Lam", "Lam6"):
            v[p.name] = rnd.uniform(0.3, 1.7)
        else:
            v[p.name] = float(p.value) * rnd.uniform(0.9, 1.1)
    for p in P.all_parameters:
        if p.nature == "internal":
            try:
                v[p.name] = eval(p.value, ns, v)
            except Exception:
                v[p.name] = float("nan")
    return v, ns


def colour_key(s: str):
    """A colour string in canonical spelling, and the sign that spelling costs.

    f is totally antisymmetric and d and Identity are symmetric, so f(2,4,-1) is f(-1,2,4) and
    f(2,1,3) is minus f(1,2,3).  Factors are put in a fixed order.  Dummy indices are not renamed,
    so two strings that differ only in their dummies stay apart, which can miss a cancellation but
    never invent one."""
    sign, out = 1, []
    for fac in s.replace(" ", "").split("*"):
        m = re.fullmatch(r"(f|d|Identity)\((-?\d+(?:,-?\d+)*)\)", fac)
        if m:
            idx = [int(x) for x in m.group(2).split(",")]
            if m.group(1) == "f":
                sign *= (-1) ** sum(1 for i in range(len(idx)) for j in range(i + 1, len(idx)) if idx[i] > idx[j])
            fac = f"{m.group(1)}({','.join(map(str, sorted(idx)))})"
        out.append(fac)
    return "*".join(sorted(out)), sign


def cancelling_entries(ufo: str) -> dict:
    """Vertex name -> set of (colour, lorentz) entries whose same-coupling group sums to zero.

    Couplings are evaluated with every external parameter at a distinct random value, so two
    couplings are grouped only if they are equal up to sign as expressions.  A group collects the
    entries of every vertex with the same legs in the same order and the same colour in canonical
    spelling.  Each group's signed sum of structures is then evaluated at three common kinematic
    points; a group is removed only if it vanishes at all three to 1e-9 of the size of its terms,
    which for a multilinear form is proof."""
    import cmath, math, random
    sys.path.insert(0, HERE)
    import numpy as np
    import zero_vertex as Z
    sys.path.insert(0, ufo)
    for mod in ("parameters", "couplings", "vertices", "lorentz", "object_library", "function_library"):
        sys.modules.pop(mod, None)
    import parameters as P, couplings as C, vertices as V
    val, ns = random_point(P, 20261014)
    gval = {}
    for c in C.all_couplings:
        try:
            gval[c.name] = complex(eval(c.value, ns, dict(val)))
        except Exception:
            gval[c.name] = complex("nan")
    struct = {}
    txt = open(os.path.join(ufo, "lorentz.py")).read()
    for name, st in re.findall(r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '([^']*)'\)", txt):
        struct[name] = st
    # every entry of every vertex, filed under its legs and its colour in canonical spelling
    legs = {}
    for vx in V.all_vertices:
        for (ci, li), cp in vx.couplings.items():
            g = gval.get(cp.name, complex("nan"))
            if g != g or g == 0:
                continue
            ck, cs = colour_key(vx.color[ci])
            legs.setdefault((tuple(p.name for p in vx.particles), ck), []).append(
                (vx.name, ci, li, vx.lorentz[li].name, cs * g))
    hits = {}
    for (parts, _), entries in legs.items():
        groups = []                                  # [reference value, members]
        for vn, ci, li, ln, g in entries:
            for grp in groups:
                ref = grp[0]
                if abs(g - ref) <= 1e-12 * abs(ref) or abs(g + ref) <= 1e-12 * abs(ref):
                    grp[1].append((vn, ci, li, ln, 1 if abs(g - ref) <= 1e-12 * abs(ref) else -1))
                    break
            else:
                groups.append([g, [(vn, ci, li, ln, 1)]])
        for ref, members in groups:
            if len(members) < 2:
                continue
            dead = True
            for rep in range(3):
                tot, scale = 0j, 0.0
                for vn, ci, li, ln, sign in members:
                    st = struct.get(ln)
                    e = None if st is None else Z.evaluate(Z.parse(st), np.random.default_rng(500 + rep), len(parts))
                    if e is None:
                        dead = False
                        break
                    tot += sign * e[0]
                    scale += e[1]
                if not dead or abs(tot) > 1e-9 * max(scale, 1e-300):
                    dead = False
                    break
            if dead:
                for vn, ci, li, ln, sign in members:
                    hits.setdefault(vn, set()).add((ci, li))
    return hits


def dead_coefficients(ufo: str) -> list:
    """Coefficients whose whole contribution to every vertex vanishes, all others at zero.

    Each coefficient part (a real coefficient, or the Re and Im parts of a complex one) is switched
    on alone.  The couplings that mention it are evaluated once, every Lorentz structure is
    evaluated once per common random point and cached, and the coefficient is dead when every
    vertex it touches sums to zero at three points."""
    import cmath, math
    sys.path.insert(0, HERE)
    import numpy as np
    import zero_vertex as Z
    sys.path.insert(0, ufo)
    for mod in ("parameters", "couplings", "vertices", "lorentz", "object_library", "function_library"):
        sys.modules.pop(mod, None)
    import parameters as P, couplings as C, vertices as V
    ns = {"cmath": cmath, "math": math, "complex": complex,
          "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z}
    ext = [p for p in P.all_parameters if p.nature == "external"]
    coef_parts = {p.name for p in ext if p.lhablock in ("DIM8", "DIM6") and p.name not in ("Lam", "Lam6")}
    bases = {re.sub(r"(Re|Im)$", "", n) for n in coef_parts} | coef_parts
    internal = [p for p in P.all_parameters if p.nature == "internal"]
    # coefficient -> couplings that mention it, by one scan of each coupling's identifiers
    by_coef = {}
    for c in C.all_couplings:
        for ident in set(re.findall(r"[A-Za-z_]\w*", c.value)):
            if ident in bases:
                by_coef.setdefault(re.sub(r"(Re|Im)$", "", ident), set()).add(c.name)
    cvalue = {c.name: compile(c.value, c.name, "eval") for c in C.all_couplings}
    # coupling -> (vertex, colour, lorentz) entries
    entries = {}
    for vx in V.all_vertices:
        for (ci, li), cp in vx.couplings.items():
            entries.setdefault(cp.name, []).append((vx, ci, li))
    struct = dict(re.findall(r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '([^']*)'\)",
                             open(os.path.join(ufo, "lorentz.py")).read()))
    cache = {}
    def S(name, nlegs, rep):
        k = (name, nlegs, rep)
        if k not in cache:
            cache[k] = Z.evaluate(Z.parse(struct[name]), np.random.default_rng(900 + rep), nlegs)
        return cache[k]
    import random as _r
    _rnd = _r.Random(20261015)
    base = {p.name: float(p.value) * _rnd.uniform(0.9, 1.1) for p in ext}
    for n in coef_parts:
        base[n] = 0.0
    dead = []
    for w in sorted(by_coef):
        parts = [n for n in (w, w + "Re", w + "Im") if n in coef_parts]
        alive = False
        for on in parts:
            vals = dict(base)
            vals[on] = 1.0
            for p in internal:
                try:
                    vals[p.name] = eval(p.value, ns, vals)
                except Exception:
                    vals[p.name] = float("nan")
            g = {}
            for cn in by_coef[w]:
                try:
                    g[cn] = complex(eval(cvalue[cn], ns, vals))
                except Exception:
                    g[cn] = complex("nan")
            # sum per (vertex, colour) over the entries whose coupling depends on w
            sums = {}
            for cn, gv in g.items():
                if gv != gv or gv == 0:
                    continue
                for vx, ci, li in entries.get(cn, ()):
                    sums.setdefault((vx.name, ci), (vx, []))[1].append((gv, vx.lorentz[li].name))
            for (vn, ci), (vx, terms) in sums.items():
                for rep in range(3):
                    tot, scale = 0j, 0.0
                    for gv, ln in terms:
                        e = S(ln, len(vx.particles), rep)
                        if e is None:
                            alive = True
                            break
                        tot += gv * e[0]
                        scale += abs(gv) * e[1]
                    if alive or abs(tot) > 1e-9 * max(scale, 1e-300):
                        alive = True
                        break
                if alive:
                    break
            if alive:
                break
        if not alive:
            dead.append(w)
    return dead


def zero_coefficients(ufo: str, dead: list, text_v: str) -> tuple[str, str, int, int]:
    """Set the dead coefficients to zero in couplings.py, drop the couplings that become identically
    zero and the vertex entries that carry them.  Returns new vertices and couplings text and counts."""
    import cmath, math, random
    C = open(os.path.join(ufo, "couplings.py")).read()
    names = sorted(set(dead) | {d + "Re" for d in dead} | {d + "Im" for d in dead}, key=len, reverse=True)
    pat = re.compile(r"\b(" + "|".join(map(re.escape, names)) + r")\b")
    C2 = re.sub(r"(value = ')([^']*)(')", lambda m: m.group(1) + pat.sub("0", m.group(2)) + m.group(3), C)
    # Only couplings that mention a dead coefficient change, and only those can have become zero.
    # Each is judged at two random points of every parameter, so a coupling that is zero merely at
    # the default inputs is kept.
    sys.path.insert(0, ufo)
    sys.modules.pop("parameters", None)
    import parameters as P
    pts = [random_point(P, seed) for seed in (1, 2)]
    zero_c = set()
    orig = dict(re.findall(r"^(GC_\d+) = Coupling\(name = 'GC_\d+',\s*value = '([^']*)'", C, re.M))
    for name, value in re.findall(r"^(GC_\d+) = Coupling\(name = 'GC_\d+',\s*value = '([^']*)'", C2, re.M):
        if not pat.search(orig.get(name, "")):
            continue
        try:
            vals = [complex(eval(value, ns_, dict(v))) for v, ns_ in pts]
        except Exception:
            continue
        if all(x == x and abs(x) == 0 for x in vals):
            zero_c.add(name)
    hits = {}
    for block in re.split(r"\n\n", text_v):
        m = re.match(r"\s*(V_\d+) = Vertex\(", block)
        if not m:
            continue
        for c, l, coup in re.findall(r"\((\d+),(\d+)\):C\.(\w+)", block):
            if coup in zero_c:
                hits.setdefault(m.group(1), set()).add((int(c), int(l)))
    V2, dropped, edited, lost = remove_entries(text_v, hits)
    return V2, C2, len(zero_c), lost


def remove_entries(text: str, hits: dict) -> tuple[str, int, int, int]:
    """Remove the given (colour, lorentz) entries from their vertices, renumbering the lorentz
    list and the coupling keys, and delete a vertex left with no coupling."""
    out, dropped, edited, lost = [], 0, 0, 0
    for block in re.split(r"\n\n", text):
        m = re.match(r"\s*(V_\d+) = Vertex\(", block)
        if not m or m.group(1) not in hits:
            out.append(block)
            continue
        bad = hits[m.group(1)]
        lm = re.search(r"lorentz = \[(.*?)\]", block, re.S)
        cm = re.search(r"couplings = \{(.*?)\}", block, re.S)
        names = re.findall(r"L\.(\w+)", lm.group(1))
        pairs = [(int(c), int(l), coup) for c, l, coup in re.findall(r"\((\d+),(\d+)\):(C\.\w+)", cm.group(1))]
        kept = [(c, l, coup) for c, l, coup in pairs if (c, l) not in bad]
        lost += len(pairs) - len(kept)
        if not kept:
            dropped += 1
            continue
        used = sorted({l for _, l, _ in kept})
        newpos = {old: new for new, old in enumerate(used)}
        block = block.replace(lm.group(0), "lorentz = [ " + ", ".join(f"L.{names[i]}" for i in used) + " ]")
        block = block.replace(cm.group(0), "couplings = {" + ",".join(f"({c},{newpos[l]}):{coup}" for c, l, coup in kept) + "}")
        edited += 1
        out.append(block)
    return "\n\n".join(out), dropped, edited, lost


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    ufo = os.path.abspath(argv[1])
    dry = "--dry-run" in argv
    zero = zero_structures(ufo)
    # FeynRules can also write the literal structure '0', which needs no numerical test.
    L = open(os.path.join(ufo, "lorentz.py")).read()
    zero |= set(re.findall(
        r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '0'\)", L))
    V = open(os.path.join(ufo, "vertices.py")).read()
    if zero:
        print(f"{len(zero)} identically vanishing structures: {' '.join(sorted(zero))}")
        V, dropped, edited, lost = rewrite_vertices(V, zero)
        print(f"vertices deleted {dropped}, vertices edited {edited}, "
              f"coupling entries removed from edited vertices {lost}")
    else:
        print("no identically vanishing Lorentz structures")
    hits = cancelling_entries(ufo)
    if hits:
        V, dropped2, edited2, lost2 = remove_entries(V, hits)
        print(f"cancelling same-coupling groups in {len(hits)} vertices: vertices deleted {dropped2}, "
              f"vertices edited {edited2}, coupling entries removed {lost2}")
    else:
        print("no cancelling same-coupling groups")
    dead = dead_coefficients(ufo)
    C = open(os.path.join(ufo, "couplings.py")).read()
    if dead:
        V, C, nzero, lost3 = zero_coefficients(ufo, dead, V)
        print(f"coefficients that vanish in every vertex: {len(dead)} ({' '.join(dead)}); "
              f"couplings now identically zero {nzero}, coupling entries removed {lost3}")
    else:
        print("no coefficient vanishes in every vertex")
    if not zero and not hits and not dead:
        return 0
    V2 = V
    still = set(re.findall(r"L\.(\w+)", V2))
    stillc = set(re.findall(r"C\.(\w+)", V2))
    allL = set(re.findall(r"^(\w+) = Lorentz\(", L, re.M))
    orphanL = sorted(allL - still)
    allc = set(re.findall(r"^(GC_\d+) = Coupling\(", C, re.M))
    orphanC = sorted(allc - stillc)
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
