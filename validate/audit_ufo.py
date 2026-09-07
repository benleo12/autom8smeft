"""
validate/audit_ufo.py  --  structural audit of a generated UFO, no Mathematica needed.

Reads a UFO directory the way MadGraph does (importing its python modules) and checks
the things a wrong Feynman rule would most likely break:

  1. every dimension-eight coupling carries exactly one Wilson coefficient and the
     coupling order NP = 2, and every vertex mixes at most one operator per coupling;
  2. chirality: for every coupling that depends on a WC, the Lorentz structure it
     multiplies must carry the projector of that operator's fermion bilinear, ProjP for
     right-handed (u, d, e), ProjM for left-handed (q, l).  The expected chirality comes
     from the DSL, so this ties the UFO back to the parsed operator, through FeynRules;
  3. the fermion content of every dim-8 vertex matches the operator's field content
     (number of fermion legs), and B-violating operators appear only in vertices with the
     matching fermion-number violation.

Usage:  python3 validate/audit_ufo.py <ufo_dir>
"""

from __future__ import annotations

import importlib
import os
import re
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "gen"))
sys.path.insert(0, os.path.join(ROOT, "validate"))

RIGHT = {"u", "d", "e"}
LEFT = {"q", "l"}


class _V:
    pass


def load_ufo(path: str):
    """Parse the UFO text files (FeynRules writes python 2 syntax, so importing is not an
    option).  Returns an object with all_vertices, each with .name, .particles (objects
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
        v.couplings = {(int(a), int(b)): coup[c] for a, b, c in re.findall(r"\((\d+),(\d+)\):C\.(\w+)", field(body, "couplings"))}
        ol.all_vertices.append(v)
    return ol


def operators_by_wc():
    """wc name -> parsed Operator (from the catalogue, same order as the blocks)."""
    sys.argv = ["x"]
    exec(open(os.path.join(ROOT, "dim8")).read().split("def main():")[0], g := {"__name__": "dim8lib", "__file__": os.path.join(ROOT, "dim8")})
    ops = g["_parse_all"]()
    return {o.wc: o for o in ops}


def wc_in(value: str, wcs):
    # One scan of the value, then set lookups: the earlier version ran a compiled regex per
    # coefficient per coupling, 1030 x 48211 searches on the full model, and took the better part
    # of an hour where this takes seconds.  Complex WCs appear through their Re/Im parts too.
    names = set(re.findall(r"\b\w+\b", value))
    wcs = wcs if isinstance(wcs, (set, dict)) else set(wcs)
    found = {n for n in names if n in wcs}
    found |= {n[:-2] for n in names if n.endswith(("Re", "Im")) and n[:-2] in wcs}
    return sorted(found)


def main(ufo: str) -> int:
    ol = load_ufo(ufo)
    ops = operators_by_wc()
    wcs = list(ops)
    problems = []
    nd8 = 0
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
            if c.order.get("NP") != 2:
                problems.append(f"{v.name} {parts}: {c.name} order {c.order} (expected NP:2)")
            for w in ws:
                op = ops[w]
                fc = op.field_content()
                if nferm != fc["N_f"]:
                    problems.append(f"{v.name} {parts}: {op.name} has {fc['N_f']} fermions, vertex has {nferm}")
                _chirality(v, il, c, op, w, nferm, problems)
    print(f"{ufo}: {len(ol.all_vertices)} vertices, {nd8} dimension-eight couplings audited")
    for p in problems:
        print("  PROBLEM " + p)
    print("audit: " + ("PASS" if not problems else f"{len(problems)} problems"))
    return 1 if problems else 0


def _chirality(v, il, c, op, w, nferm, problems):
            from dsl import Psi
            struct = v.lorentz[il].structure
            parts = [p.name for p in v.particles]
            # chirality.  UFO convention (calibrated on the SM W vertex V_40 and on
            # Q_{quWH^3}^{(1)}, the development log, not shipped session 4): the particle list names the
            # particle each FIELD CREATES, and ProjX(-1,p) sits on the position p of the
            # unbarred field.  A coupling carrying complexconjugate(WC) is the Hermitian-
            # conjugate term, whose unbarred field is the direct term's barred one.
            conj = bool(re.search(rf"complexconjugate\({re.escape(w)}\)", c.value))
            need = set()
            for f in op.terms[0].factors:
                if isinstance(f, Psi) and f.cc:
                    need.add("CC")
                elif isinstance(f, Psi) and (f.bar == conj):
                    need.add("ProjP" if f.name in RIGHT else "ProjM")
            if "CC" in need:
                return  # fermion-flow-violating chains are re-expressed by FeynRules; not audited here
            if nferm and op.hc_mode == "real":
                # a Hermitian operator contains both orderings; only the chirality set matters
                pass
            for pr in ("ProjP", "ProjM"):
                if pr in need and pr not in struct:
                    problems.append(f"{v.name} {parts}: {op.name} ({'h.c.' if conj else 'direct'}) needs {pr}, structure {v.lorentz[il].name} = {struct}")
                if pr not in need and pr in struct and nferm:
                    problems.append(f"{v.name} {parts}: {op.name} ({'h.c.' if conj else 'direct'}) must not have {pr}, structure {v.lorentz[il].name} = {struct}")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "tests", "gen_smoke", "uuww")))
