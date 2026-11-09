"""
validate/audit_ufo.py  --  structural audit of a generated UFO, no Mathematica needed.

Reads the python files of a UFO directory as text (load_ufo says why) and checks the things
a wrong Feynman rule would most likely break:

  1. every coupling that carries a Wilson coefficient has the coupling order NP = 2.  The one
     exception is the product of an operator term with a tagged input-scheme shift, which is
     NP = 3 or 4.  In a model of order N (gen/towers.py) the coefficient of a member of dimension d
     of a tower has NP = (d - 4)/2, or more with a shift, and is audited below as the operator of
     dimension eight it multiplies by (H^dag H)^k, whose fermions and chiralities it has.  MergeVertices can put several operators on one coupling, and every one of
     them is audited.  The coefficient of a further flavour structure (block DIM8F) is
     audited here and below as the operator it belongs to.
  2. chirality: for every coupling that depends on a WC, the Lorentz structure it
     multiplies must carry the projector of that operator's fermion bilinear, ProjP for
     right-handed (u, d, e), ProjM for left-handed (q, l).  The expected chirality comes
     from the operator's encoding in gen/operators.py, so this ties the UFO back to the
     encoded operator through FeynRules.  Operators with a charge-conjugated bilinear are
     not audited for chirality.  The couplings that multiply one structure or a multiple of it,
     on one list of particles and with one colour structure, are audited as their sum (each
     times the multiple), which is what the amplitude holds.
  3. the number of fermion legs of every dim-8 vertex matches the operator's field content.
  4. no coupling without an NP order depends on a Wilson coefficient, directly or through any
     chain of internal parameters.  If such a coupling carried the shifted vev, Yukawas or
     Higgs quartic, the NP=0 amplitude would move with the coefficients and NP^2==2 would hold
     terms quadratic in them.  A MASS that depends on a coefficient is reported but is not a
     problem, since a generator counts orders on couplings and the {alpha, M_Z, G_F} scheme
     derives M_W.
  5. the files are what MadGraph can read: no Mathematica residue, every vertex well formed.

Usage:  python3 validate/audit_ufo.py <ufo_dir>      (a Python with numpy)
"""

from __future__ import annotations

import cmath
import functools
import hashlib
import importlib
import json
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "gen"))
sys.path.insert(0, os.path.join(ROOT, "validate"))

RIGHT = {"u", "d", "e"}
# the tagged shift parameters of the input scheme, every one O(1/Lambda^2) or O(1/Lambda^4), and in a model
# of order N those of every order through N, with the rescalings of the gluon and of g_s (gen/derive_geo.py)
SHIFT = re.compile(r"\b(gw[1-9]|g1[1-9]|vev[1-9]|MW2[1-9]|aEW[1-9]|rW[1-9]|rh[1-9]|T(ZZ|ZA|AZ|AA)[1-9]|lamr[1-9]|yr[1-9]|rG[1-9]|sG[1-9])\b")
# the blocks of the coefficients of the towers of a model of order N (gen/towers.py, gen/input_scheme.py)
TOWER_BLOCK = re.compile(r"DIM(1[0-9]|[2-9][0-9])F?|GEOGF")


class _V:
    pass


def load_ufo(path: str):
    """Read the UFO text files by pattern.  FeynRules writes python 2 syntax, so the files are
    not imported.  Returns an object with all_vertices, each with .name, .particles (objects
    with .name/.spin), .lorentz (objects with .name/.structure) and .couplings
    {(ic, il): coupling(.name/.value/.order)}."""
    def blocks(fn, head):
        txt = open(os.path.join(path, fn)).read()
        return re.findall(rf"(\w+) = {head}\((.*?)\)\n\n", txt + "\n\n", re.S)

    def field(body, key):
        m = re.search(rf"{key}\s*=\s*(.*?)(?:,\s*\n\s*\w+\s*=|\Z)", body, re.S)
        return m.group(1).strip() if m else ""

    parts = {}
    for name, body in blocks("particles.py", "Particle"):
        o = _V(); o.name = re.search(r"name = '([^']*)'", body).group(1); o.spin = int(field(body, "spin")); parts[name] = o
    for name, body in blocks("particles.py", r"P\.\w+\.anti"):
        pass
    txt = open(os.path.join(path, "particles.py")).read()
    for m in re.finditer(r"(\w+) = (\w+)\.anti\(\)", txt):
        o = _V(); o.name = m.group(1); o.spin = parts[m.group(2)].spin; parts[m.group(1)] = o
    lor = {}
    for name, body in blocks("lorentz.py", "Lorentz"):
        o = _V(); o.name = name; o.structure = re.search(r"structure = '([^']*)'", body).group(1); lor[name] = o
    coup = {}
    for name, body in blocks("couplings.py", "Coupling"):
        o = _V(); o.name = name; o.value = re.search(r"value = '([^']*)'", body, re.S).group(1)
        o.order = eval(re.search(r"order = (\{[^}]*\})", body).group(1)); coup[name] = o
    ol = _V(); ol.all_vertices = []
    for name, body in blocks("vertices.py", "Vertex"):
        v = _V(); v.name = name
        v.particles = [parts[x] for x in re.findall(r"P\.(\w+)", field(body, "particles"))]
        v.lorentz = [lor[x] for x in re.findall(r"L\.(\w+)", field(body, "lorentz"))]
        v.color = re.findall(r"'([^']*)'", field(body, "color"))
        v.couplings ={(int(a), int(b)): coup[c] for a, b, c in re.findall(r"\((\d+),(\d+)\):C\.(\w+)", field(body, "couplings"))}
        ol.all_vertices.append(v)
    return ol


def operators_by_wc():
    """wc name -> Operator, from the encoding gen/operators.py (read through ./dim8).  The coefficient of a
    further flavour structure (block DIM8F, its name without Re or Im) maps to the operator it belongs to,
    whose fields, chiralities and mass dimension a flavour structure leaves as they are."""
    sys.argv = ["x"]
    exec(open(os.path.join(ROOT, "dim8")).read().split("def main():")[0], g := {"__name__": "dim8lib", "__file__": os.path.join(ROOT, "dim8")})
    ops = {o.wc: o for o in g["_parse_all"]()}
    for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json"))):
        for f in e.get("flavour", []):
            f = re.sub(r"(Re|Im)$", "", f)
            ops[f] = ops[max((w for w in e["wcs"] if f.startswith(w + "F")), key=len)]
    return ops


def tower_members(ufo: str):
    """{coefficient: (mass dimension, block)} of the members of the towers of a model of order N, the external
    parameters c<d><label> of the blocks DIM10, DIM10F, DIM12, ... and GEOGF.  Empty for every other model."""
    txt = open(os.path.join(ufo, "parameters.py")).read()
    ext = re.findall(r"name = '(c(\d+)[A-Za-z]\w*)',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,"
                     r"\s*texname = '[^']*',\s*lhablock = '(\w+)'", txt)
    return {n: (int(d), blk) for n, d, blk in ext if TOWER_BLOCK.fullmatch(blk)}


def member_operators(members, ops):
    """{coefficient: (operator, mass dimension)} for the members with vertices, the coefficients of block GEOGF
    left out, a complex one under the name without Re or Im as wc_in reports it.  The operator is that of
    dimension eight that the member multiplies by (H^dag H)^k, since the fermions, their chiralities and the
    field strengths are its own, or for the towers of Q_{WH^6D^2}^{(5),(6)}, which have none, the member of
    gen/towers.py."""
    out, own = {}, []
    for n, (d, blk) in members.items():
        if blk == "GEOGF":
            continue
        n = re.sub(r"(Re|Im)$", "", n)
        parent = "c8" + re.match(r"c\d+(.*)", n).group(1)
        if parent in ops:
            out[n] = (ops[parent], d)
        else:
            own.append((n, d))
    if own:
        import towers
        made = {o.wc: o for d in sorted({d for _, d in own}) for o in towers.tower(d)}
        missing = [n for n, _ in own if n not in made]
        if missing:
            raise SystemExit(f"members with no operator of dimension eight and none in gen/towers.py: {missing}")
        out.update({n: (made[n], d) for n, d in own})
    return out


def wc_in(value: str, wcs):
    # One scan of the value, then set lookups.  A compiled regex per coefficient per coupling
    # takes most of an hour on the full model, where this takes seconds.  Complex WCs appear
    # through their Re/Im parts too.
    names = set(re.findall(r"\b\w+\b", value))
    wcs = wcs if isinstance(wcs, (set, dict)) else set(wcs)
    found = {n for n in names if n in wcs}
    found |= {n[:-2] for n in names if n.endswith(("Re", "Im")) and n[:-2] in wcs}
    return sorted(found)


def coefficient_closure(ufo: str):
    """The internal parameters that depend on a Wilson coefficient, transitively, and the masses
    among them.  A coefficient is any external parameter of a DIM6, DIM8 or DIM8F block, or of a block of the towers."""
    txt = open(os.path.join(ufo, "parameters.py")).read()
    ext = re.findall(r"(\w+) = Parameter\(name = '\w+',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,\s*texname = '[^']*',\s*lhablock = '(\w+)'", txt)
    coeffs = {n for n, blk in ext if blk in ("DIM6", "DIM8", "DIM8F") or TOWER_BLOCK.fullmatch(blk)}
    internal = re.findall(r"(\w+) = Parameter\(name = '\w+',\s*nature = 'internal',\s*type = '\w+',\s*value = '([^']*)'", txt, re.S)
    dep = set(coeffs)
    changed = True
    while changed:
        changed = False
        for n, v in internal:
            if n not in dep and any(w in dep for w in re.findall(r"\b\w+\b", v)):
                dep.add(n); changed = True
    dep -= coeffs
    masses = set(re.findall(r"mass = Param\.(\w+)", open(os.path.join(ufo, "particles.py")).read()))
    return coeffs, dep, dep & masses


def well_formed(ufo: str):
    """The files must be what MadGraph can read.  FeynRules writes a failed evaluation INTO the
    UFO instead of stopping: an iteration limit inside WriteUFO leaves
    "ClassAttributeCreation[couplings, {... TerminatedEvaluation[IterationLimit] ...}]" where a
    vertex's couplings should be.  load_ufo reads entries by pattern and does not see such an
    entry, so this check requires that no Mathematica residue appears anywhere and that every
    Vertex( that is opened is a well-formed entry."""
    problems = []
    for fn in ("vertices.py", "couplings.py", "lorentz.py", "parameters.py", "particles.py"):
        txt = open(os.path.join(ufo, fn)).read()
        for bad in ("TerminatedEvaluation", "ClassAttributeCreation", "PYDicEntry", "$Failed", "$Aborted", "<>"):
            n = txt.count(bad)
            if n:
                problems.append(f"{fn}: {n} occurrence(s) of Mathematica residue '{bad}'")
    vtxt = open(os.path.join(ufo, "vertices.py")).read()
    opened = len(re.findall(r"^V_\d+ = Vertex\(", vtxt, re.M))
    parsed = len(re.findall(r"^V_\d+ = Vertex\(name = '\w+',\s*particles = \[[^\]]*\],\s*color = \[[^\]]*\],"
                            r"\s*lorentz = \[[^\]]*\],\s*couplings = \{[^}]*\}\)", vtxt, re.M))
    if opened != parsed:
        problems.append(f"vertices.py: {opened} vertices opened, {parsed} well formed")
    return problems


def main(ufo: str) -> int:
    ol = load_ufo(ufo)
    ops = operators_by_wc()
    # the members of the towers of a model of order N, with the NP order of each
    member = member_operators(tower_members(ufo), ops)
    np_of = {w: 2 for w in ops}
    np_of.update({w: (d - 4)//2 for w, (_, d) in member.items()})
    ops = dict(ops, **{w: o for w, (o, _) in member.items()})
    wcs = set(ops)
    problems = well_formed(ufo)
    nd8 = 0
    coeffs, dep, dep_masses = coefficient_closure(ufo)
    for m in sorted(dep_masses):
        print(f"  note: mass parameter {m} depends on the coefficients (expected for a derived mass)")
    hidden = coeffs | dep
    nut = 0
    for v in ol.all_vertices:
        for (ic, il), c in v.couplings.items():
            if "NP" in c.order:
                continue
            nut += 1
            bad = sorted(set(re.findall(r"\b\w+\b", c.value)) & hidden)
            if bad:
                problems.append(f"{v.name} {[p.name for p in v.particles]}: {c.name} order {c.order} depends on the coefficients through {bad}")
    print(f"  {nut} couplings without an NP order, none depending on a coefficient" if not any("depends on the coefficients through" in p for p in problems)
          else f"  {nut} couplings without an NP order audited")
    summed = _summed(ol, wcs)
    for v in ol.all_vertices:
        parts = [p.name for p in v.particles]
        nferm = sum(1 for p in v.particles if p.spin == 2)
        for (ic, il), c in v.couplings.items():
            ws = wc_in(c.value, wcs)
            if not ws:
                continue
            nd8 += 1
            # MergeVertices sums the couplings of different operators on one Lorentz
            # structure, so a coupling may carry several WCs; every one is audited.
            # Negative QED orders come from vev factors (vev = 2 MW sw/ee carries QED -1),
            # the usual FeynRules/SMEFTsim pattern; MadGraph only warns about them.
            # A coupling that carries a coefficient is NP:2, unless it is the product of an
            # operator term with one of the tagged input-scheme shifts (the Higgs field rotation
            # rh1, rh2 multiplying the class-12 Yukawa compensation, for instance), which is
            # NP:3 or NP:4 and correctly so: a 1/Lambda^6 or 1/Lambda^8 term no order selection
            # of the paper reaches.
            for w in ws:
                n = np_of[w]
                if c.order.get("NP") != n and not (c.order.get("NP", 0) > n and SHIFT.search(c.value)):
                    problems.append(f"{v.name} {parts}: {c.name} order {c.order} (expected NP:{n} for {w})")
            value = summed.get((v.name, ic, il), c.value)
            for w in ws:
                op = ops[w]
                fc = op.field_content()
                if nferm != fc["N_f"]:
                    problems.append(f"{v.name} {parts}: {op.name} has {fc['N_f']} fermions, vertex has {nferm}")
                _chirality(v, il, c, op, w, nferm, problems, value)
    print(f"{ufo}: {len(ol.all_vertices)} vertices, {nd8} dimension-eight couplings audited"
          + (f", the {len(member)} members of the towers with them" if member else ""))
    for p in problems:
        print("  PROBLEM " + p)
    print("audit: " + ("PASS" if not problems else f"{len(problems)} problems"))
    return 1 if problems else 0


def _summed(ol, wcs):
    """The coupling the chirality audit reads for each entry of a fermion vertex whose structure has
    multiples among the entries on the same particles and colour structure: the sum of their couplings,
    each times the multiple, keyed by (vertex, colour index, Lorentz index).  FeynRules can write one
    structure more than once (with other names for its summed indices, the opposite sign, its gamma
    matrices in another order) and put the terms of one coefficient on each: in dim8_mw the vertices
    V_9607 and V_9608, both b~ s g g Z, hold the four terms of a flavour structure of
    Q_{qdGHD^2}^{(3)} three to one, and V_56119, e+ mu- a Z Z H, those of Q_{leBHD^2}^{(1)} on two
    structures, one minus the other.  The amplitude holds the sum.  Two structures are multiples when
    their values at three random kinematic points are (validate/zero_vertex.py, the evaluation of
    validate/drop_zero_structures.py), and, for a structure that evaluation does not cover, when they
    read alike (_canonical)."""
    import numpy as np
    import zero_vertex as Z
    vals = {}
    def at_points(st, n):
        if (st.name, n) not in vals:
            parsed = Z.parse(st.structure)
            pts = [Z.evaluate(parsed, np.random.default_rng(700 + r), n) for r in range(3)]
            vals[(st.name, n)] = None if any(x is None for x in pts) else (np.array([x[0] for x in pts]), max(x[1] for x in pts))
        return vals[(st.name, n)]
    def multiple(b, a):   # lam with b = lam a at every point, or None
        (bv, bs), (av, as_) = b, a
        if np.max(np.abs(av)) <= 1e-9 * as_:
            return None
        lam = complex(np.vdot(av, bv) / np.vdot(av, av))
        return lam if np.max(np.abs(bv - lam * av)) <= 1e-9 * max(bs, abs(lam) * as_) else None
    groups = {}
    for v in ol.all_vertices:
        if any(p.spin == 2 for p in v.particles):
            for (ic, il), c in v.couplings.items():
                if wc_in(c.value, wcs):
                    groups.setdefault((tuple(p.name for p in v.particles), v.color[ic]), []).append((v, ic, il, c))
    out = {}
    for entries in groups.values():
        if len(entries) < 2:
            continue
        n = len(entries[0][0].particles)
        for v, ic, il, c in entries:
            mine = v.lorentz[il]
            a = at_points(mine, n)
            terms = []
            for v2, ic2, il2, c2 in entries:
                other = v2.lorentz[il2]
                if other.name == mine.name:
                    lam = 1
                elif a is not None and (b := at_points(other, n)) is not None:
                    lam = multiple(b, a)
                else:
                    lam = 1 if _canonical(other.structure) == _canonical(mine.structure) else None
                if lam is not None:
                    terms.append(f"({c2.value})" if lam == 1 else f"complex({lam.real!r}, {lam.imag!r})*({c2.value})")
            if len(terms) > 1:
                out[(v.name, ic, il)] = " + ".join(terms)
    return out


_TENSOR = re.compile(r"\b(P|Gamma|Gamma5|Metric|ProjP|ProjM|Epsilon|Identity|Sigma|C)\(([-\d,]*)\)")


@functools.lru_cache(maxsize=None)
def _canonical(structure: str) -> str:
    """A Lorentz structure written so that two ways of writing one structure read alike: its terms
    sorted, and the summed indices (the negative ones) of each term renamed in the order they first
    appear.  Each step leaves the structure as it is, so equal results are equal structures.  Two
    equal structures may still read differently (a sum in parentheses, factors in another order),
    and are then audited apart, as before."""
    # a sign between terms: outside all parentheses, after something, and not after * / or an exponent's e
    terms, depth, start, prev = [], 0, 0, ""
    for i, ch in enumerate(structure):
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        elif ch in "+-" and depth == 0 and prev and prev not in "*/eE":
            terms.append(structure[start:i]); start = i
        if not ch.isspace():
            prev = ch
    terms.append(structure[start:])
    out = []
    for t in terms:
        t = t.strip()
        sign, body = ("-", t[1:].strip()) if t.startswith("-") else ("+", t.lstrip("+").strip())
        if body.startswith("(") and body.endswith(")"):
            d = 0
            for i, ch in enumerate(body):
                d += (ch == "(") - (ch == ")")
                if d == 0:
                    break
            if i == len(body) - 1:
                body = body[1:-1]
        names = {}
        body = _TENSOR.sub(lambda m: m.group(1) + "(" + ",".join(
            names.setdefault(a, f"~{len(names)}") if a.startswith("-") else a for a in m.group(2).split(",")) + ")", body)
        out.append(sign + body)
    return " ".join(sorted(out))


_OWN = {"cmath", "complex", "complexconjugate"}   # the names of the evaluation itself, left to the globals
_ENV = {"cmath": cmath, "complex": complex, "complexconjugate": lambda z: complex(z).conjugate(), "__builtins__": {}}


@functools.lru_cache(maxsize=None)
def _fixed(name: str) -> complex:
    """The value of a symbol in the evaluation of _shares: a nonzero complex number fixed by its name."""
    h = hashlib.sha256(name.encode()).digest()
    return complex(0.5 + h[0] / 255, 0.5 + h[1] / 255)


# A coupling's names, and its compiled expression with the values of its symbols, once per coupling: the
# audit asks for them for every coefficient of the coupling, and on a flavour model the hashing and
# compiling repeated each time took most of an hour.
@functools.lru_cache(maxsize=64)
def _names(value: str):
    return frozenset(re.findall(r"\b\w+\b", value))


@functools.lru_cache(maxsize=64)
def _compiled(value: str):
    return compile(value, "<coupling>", "eval"), {n: _fixed(n) for n in _names(value) if n not in _OWN}


def _shares(value: str, w: str):
    """Which terms of an operator carry the coefficient w in a coupling: [False] the direct one, [True] its
    Hermitian conjugate, [False, True] both, None when the coupling cannot tell them apart.  An operator's
    own complex coefficient is an internal parameter, and its conjugate term holds complexconjugate(w).  The
    coefficient of a further flavour structure (block DIM8F) is written in its parts, w_Re + i w_Im, so that
    its conjugate term holds w_Re - i w_Im.  The coupling, linear in the two, is evaluated with each at one
    and every other symbol at a value fixed by its name: the share whose w_Im part is i times its w_Re part
    is the direct term, and the one at -i the conjugate.  A coupling with one part only, as of a structure
    whose coefficient is real, holds the two terms with the same coefficient."""
    if f"complexconjugate({w})" in value:
        return [True]
    names = _names(value)
    pre, pim = w + "Re", w + "Im"
    if pre not in names or pim not in names:
        return None if pre in names or pim in names else [False]
    code, fixed = _compiled(value)
    def f(x, y):
        return complex(eval(code, _ENV, {**fixed, pre: x, pim: y}))
    a, b = f(1, 0) - f(0, 0), f(0, 1) - f(0, 0)
    scale = abs(a) + abs(b)
    out = [conj for conj, z in ((False, (a - 1j * b) / 2), (True, (a + 1j * b) / 2)) if abs(z) > 1e-9 * scale]
    return out or None


def _chirality(v, il, c, op, w, nferm, problems, value):
            from dsl import Psi
            struct = v.lorentz[il].structure
            parts = [p.name for p in v.particles]
            # chirality.  UFO convention (calibrated on the SM W vertex V_40 and on
            # Q_{quWH^3}^{(1)}): the particle list names the
            # particle each FIELD CREATES, and ProjX(-1,p) sits on the position p of the
            # unbarred field.  The Hermitian-conjugate term (_shares) has as its unbarred
            # field the direct term's barred one.
            def need_of(conj):
                need = set()
                for f in op.terms[0].factors:
                    if isinstance(f, Psi) and f.cc:
                        need.add("CC")
                    elif isinstance(f, Psi) and (f.bar == conj):
                        need.add("ProjP" if f.name in RIGHT else "ProjM")
                return need
            try:
                shares = _shares(value, w)
            except Exception as e:
                problems.append(f"{v.name} {parts}: {op.name}: the direct and the conjugate term of {w} in {c.name} cannot be told apart ({e})")
                return
            needs = [need_of(conj) for conj in (shares or (False, True))]
            if any("CC" in n for n in needs):
                return  # FeynRules re-expresses fermion-flow-violating chains, so they are not audited here
            def missing(need):
                return [(pr, "needs") for pr in ("ProjP", "ProjM") if pr in need and pr not in struct] + \
                       [(pr, "must not have") for pr in ("ProjP", "ProjM") if pr not in need and pr in struct and nferm]
            if shares is None:
                # the two terms with one coefficient: the structure is that of the one or of the other
                if all(missing(n) for n in needs):
                    problems.append(f"{v.name} {parts}: {op.name} (direct or h.c.) has neither projector set, structure {v.lorentz[il].name} = {struct}")
                return
            term = {(False,): "direct", (True,): "h.c.", (False, True): "direct and h.c."}[tuple(shares)]
            for pr, what in missing(set().union(*needs)):
                problems.append(f"{v.name} {parts}: {op.name} ({term}) {what} {pr}, structure {v.lorentz[il].name} = {struct}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "models", "dim8_is")))
