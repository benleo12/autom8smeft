#!/usr/bin/env python3
"""Is G_F the muon-decay rate?  The rate at zero momentum transfer, from a UFO's own vertices.

    python3.11 validate/gf_rate_ufo.py UFO [--yme 50] [--ymm 120] [--only REGEX] [--seed 1] [--halvings 12]

What it does.  G_F is an input of the scheme, so the muon-decay rate of the model must give back the
input G_F whatever coefficients are on.  validate/gf_closure.py tests that through MadGraph at one
phase-space point, which cannot see a scalar coupling: the scalar enters through the integrated rate,
with the weight g(x)/f(x) of the Michel eta term.  This script reads the UFO alone (parameters.py,
couplings.py, vertices.py, lorentz.py, evaluated in Python as validate/compare_ufo.py does, no
MadGraph) and evaluates at zero momentum transfer

    the W-lepton vertices of (e, nu_e) and (mu, nu_mu), with their chiralities, and the W mass,
    the four-lepton contact vertices of e, nu_e, nu_mu, mu,

each from the UFO's own Lorentz structures with explicit Dirac matrices and every momentum zero.  It
adds the W exchange and the contact vertices into one four-lepton amplitude as MadGraph does, with the
sign MadGraph puts on a crossed four-fermion structure and the sign of the fermion lines of a vertex
against those of the W exchange, and projects it onto the Michel basis,

    L = -(2/v^2) [ A (ebar gamma^m P_L nu_e)(nubar_mu gamma_m P_L mu) + S (ebar P_L nu_e)(nubar_mu P_R mu) ],

with v^2 = 1/(sqrt2 G_F) of the input G_F, so that A = 1 and S = 0 in the Standard Model.  With
left-handed neutrinos nothing else exists, and the part of the amplitude outside the two is printed
and must vanish.  The rate

    192 pi^3 Gamma/(m_mu^5 G0^2) = (|A|^2 + |S|^2/4) f(x) + 2 sqrt(x) Re(A S*) g(x),   x = m_e^2/m_mu^2,
    f = 1 - 8x + 8x^3 - x^4 - 12x^2 ln x,   g = 1 + 9x - 9x^2 - x^3 + 6x(1 + x) ln x,

read as Gamma = G_F^2 m_mu^5 f(x)/(192 pi^3), the definition of the measured G_F, gives

    sqrt2 G_F v^2 = sqrt( |A|^2 + |S|^2/4 + 2 sqrt(x) Re(A S*) g(x)/f(x) ),

and the script prints its deviation from 1, the relative deviation of the model's G_F from the input.
The formula is exact in x.  A final state with other neutrino flavours, mu -> e nubar_i nu_j with
(i, j) other than (e, mu), adds to the rate without interfering.  Those vanish in the released flavour
conventions, and the script adds them and prints their largest coupling.

Zero momentum transfer is the definition of G_F.  Three things are left out by it: the momentum
dependence of the W propagator, m_mu^2/M_W^2, which the measurement removes by the factor
1 + 3 m_mu^2/(5 M_W^2), the operators with a derivative (psi^4 D^2, psi^4 H D, the dipoles), whose
vertices vanish at zero momentum, and the Goldstone bosons of a Feynman-gauge UFO.  The W is exchanged
in unitary gauge, where the q^m q^n part of the propagator vanishes at zero momentum transfer.

The inputs.  Every Wilson coefficient of the UFO (an external parameter of a block DIM<d> or DIM<d>F
whose name starts with c) takes a value c0 in [-1, 1) fixed by its name and the seed, as in
validate/compare_ufo.py, times t^((d-4)/2) at strength t.  That is Lambda -> Lambda/sqrt(t), so a
term of order 1/Lambda^(2k) scales as t^k.  With --only REGEX only the coefficients whose names match
are on, and the others keep the values of the card (0).  The electron and muon Yukawa masses (block
YUKAWA, entries 11 and 13) are set to --yme and --ymm in GeV.  The defaults are unphysically large so
that the Yukawa terms stand well above rounding, which is fine because the formula is exact in x.  The
lepton masses in x are those of the UFO, or the YUKAWA entry for a lepton the UFO keeps massless.

When to use it.  After any change to the input relations (gen/input_scheme.py,
gen/derive_input_scheme.py, gen/derive_geo.py) and on every model before it is released, with the
Yukawas on (the default) and with --yme 0 --ymm 0.  It needs numpy and takes a few seconds on a
released model: vertices.py and couplings.py are read as text and only the couplings of muon decay
are evaluated.

The output.  The inputs and the number of coefficients on, then at t = 1 the W couplings of the
electron and the muon relative to the Standard Model, A - 1, S and the part outside the Michel basis,
then one line per strength t = 1, 1/2, ... with A - 1, S, the deviation sqrt2 G_F v^2 - 1 and the
ratio of the deviation to that at twice the strength.

What it must pass.  An input relation complete through order N leaves a deviation of order t^(N+1).
For N = 2 the deviation falls by 8 per halving, and by 16 in a model with only dimension-eight
operators, whose next term is of order 1/Lambda^8.  A term missing at order k leaves a deviation
falling by 2^k.  The verdict is PASS when the deviation falls by at least 6.5 per halving over the
last three halvings above the rounding floor of 1e-13, or never rises above that floor, and the
Standard-Model point gives A = 1, S = 0 and nothing outside the Michel basis.  The scalar term is
what this test adds to validate/gf_closure.py.  It comes from Q_{l^2e^2H^2}^{(1,2)} with the lepton
Yukawas on: input relations without it leave a deviation that falls by 4 per halving with the default
Yukawas, and they pass with --yme 0 --ymm 0, where the term vanishes.
"""
import argparse
import cmath
import itertools
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compare_ufo as CU  # noqa: E402
import zero_vertex as Z  # noqa: E402

FLOOR = 1e-13            # below this the deviation is rounding
PL = (np.eye(4) - CU.GAMMA5) / 2
PR = (np.eye(4) + CU.GAMMA5) / 2
GLOW = np.diag(CU.G)     # the metric, which lowers an index
# the Michel basis in the pairing (ebar nu_e)(nubar_mu mu), axes [e, nu_e, nu_mu, mu]
B_V = sum(GLOW[m] * np.einsum("ab,cd->abcd", CU.GAMMA[m] @ PL, CU.GAMMA[m] @ PL) for m in range(4))
B_S = np.einsum("ab,cd->abcd", PL, PR)


def f_mu(x):
    return 1 - 8 * x + 8 * x ** 3 - x ** 4 - (12 * x ** 2 * math.log(x) if x > 0 else 0.0)


def g_mu(x):
    return 1 + 9 * x - 9 * x ** 2 - x ** 3 + (6 * x * (1 + x) * math.log(x) if x > 0 else 0.0)


def read_vertices(ufo, P):
    """[(particle names, colours, structure names, {(ci, li): [coupling names]})] of vertices.py, read as text,
    so that couplings.py, which a released model holds in half a gigabyte, is not imported."""
    names = {k: v.name for k, v in vars(P).items() if hasattr(v, "pdg_code")}
    txt = open(os.path.join(ufo, "vertices.py")).read()
    out = []
    for m in re.finditer(r"Vertex\(name\s*=\s*'\w+',\s*particles\s*=\s*\[([^\]]*)\],\s*color\s*=\s*\[([^\]]*)\],\s*"
                         r"lorentz\s*=\s*\[([^\]]*)\],\s*couplings\s*=\s*\{([^}]*)\}", txt):
        parts = [names[p.strip()[2:]] for p in m.group(1).split(",")]
        cols = re.findall(r"'([^']*)'", m.group(2))
        lors = [x.strip()[2:] for x in m.group(3).split(",")]
        coup = {}
        for ci, li, c in re.findall(r"\((\d+),\s*(\d+)\)\s*:\s*(\[[^\]]*\]|C\.\w+)", m.group(4)):
            coup[(int(ci), int(li))] = re.findall(r"C\.(\w+)", c)
        out.append((parts, cols, lors, coup))
    return out


def read_couplings(ufo, wanted):
    """{name: (value, orders)} of the couplings named in wanted, read from couplings.py line by line."""
    out, cur, buf = {}, None, []
    with open(os.path.join(ufo, "couplings.py")) as fh:
        for line in fh:
            m = re.match(r"(\w+) = Coupling\(", line)
            if m:
                cur, buf = (m.group(1) if m.group(1) in wanted else None), []
            if cur is None:
                continue
            buf.append(line)
            blk = "".join(buf)
            v = re.search(r"value\s*=\s*'(.*)',\s*order\s*=\s*(\{[^}]*\})\s*\)", blk, re.S)
            if v:
                out[cur] = (v.group(1), v.group(2))
                cur = None
    missing = set(wanted) - set(out)
    if missing:
        sys.exit(f"couplings not found in couplings.py: {' '.join(sorted(missing)[:10])}")
    return out


class ZeroMomentum:
    """The Lorentz namespace of validate/compare_ufo.py with every momentum zero and each leg given a unit
    vector, so that a structure evaluated over all unit vectors is its tensor in the legs' indices."""

    def __init__(self, nlegs):
        pt = object.__new__(CU.Point)
        pt.mom = {k: np.zeros(4) for k in range(1, nlegs + 1)}
        pt.lor, pt.spi, pt.col = {}, {}, {}
        self.pt, self.ns = pt, pt.lorentz_ns()

    def tensor(self, structure, spins):
        dims = [4 if s in (2, 3) else 1 for s in spins]
        code = compile(structure, "<structure>", "eval")
        out = np.zeros(dims, dtype=complex)
        unit = np.eye(4)
        for idx in itertools.product(*[range(d) for d in dims]):
            for k, s in enumerate(spins):
                if s == 2:
                    self.pt.spi[k + 1] = unit[idx[k]]
                elif s == 3:
                    self.pt.lor[k + 1] = unit[idx[k]]
            out[idx] = CU.scalar(eval(code, self.ns))
        return out


def main(argv=None):
    a = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    a.add_argument("ufo")
    a.add_argument("--yme", type=float, default=50.0, help="the electron Yukawa mass in GeV (block YUKAWA, 11)")
    a.add_argument("--ymm", type=float, default=120.0, help="the muon Yukawa mass in GeV (block YUKAWA, 13)")
    a.add_argument("--only", default=None, help="switch on only the Wilson coefficients matching this regular expression")
    a.add_argument("--seed", type=int, default=1)
    a.add_argument("--halvings", type=int, default=12)
    args = a.parse_args(argv)
    ufo = os.path.abspath(args.ufo)
    need = ("object_library.py", "parameters.py", "particles.py", "lorentz.py", "vertices.py", "couplings.py",
            "function_library.py")
    lack = [f for f in need if not os.path.isfile(os.path.join(ufo, f))]
    if lack:
        print(f"{args.ufo} is not an unpacked UFO: it has no {', '.join(lack)} "
              "(a released model is unpacked with tar -xJf models/<name>.tar.xz -C models)")
        return 2

    CU.use_ufo(ufo)
    try:
        import function_library as F
        import lorentz as L
        import parameters as PM
        import particles as P
        ns = {"cmath": cmath, "math": math, "complex": complex}
        ns.update({k: v for k, v in vars(F).items() if callable(v)})
        params = list(PM.all_parameters)
        ext = [p for p in params if p.nature == "external"]
        internal = [(p.name, compile(p.value, p.name, "eval")) for p in params if p.nature == "internal"]

        # the Wilson coefficients and their dimensions
        dim = {}
        for p in ext:
            m = re.fullmatch(r"DIM(\d+)F?", p.lhablock.upper())
            if m and p.name.startswith("c") and p.name != "cabi":
                dim[p.name] = int(m.group(1))
        on = {w for w in dim if args.only is None or re.search(args.only, w)}
        card = {p.name: float(p.value) for p in ext}

        # the inputs this script sets: the lepton Yukawas, and the lepton masses where the card has them
        by_code = {(p.lhablock.upper(), tuple(p.lhacode)): p.name for p in ext}
        lep = {pdg: by_code.get(("YUKAWA", (pdg,))) for pdg in (11, 13)}
        if None in lep.values():
            sys.exit(f"{ufo}: no YUKAWA entry 11 or 13, so the lepton Yukawas cannot be set")
        fixed = {lep[11]: args.yme, lep[13]: args.ymm}
        for pdg, y in ((11, args.yme), (13, args.ymm)):
            mname = by_code.get(("MASS", (pdg,)))
            if mname:
                fixed[mname] = y
        gf_name = "Gf" if "Gf" in card else by_code.get(("SMINPUTS", (2,)))
        if gf_name is None:
            sys.exit(f"{ufo}: no G_F among the external parameters (Gf, or SMINPUTS entry 2)")

        def evaluate_parameters(t):
            vals = {}
            for p in ext:
                v = card[p.name]
                if p.name in on:
                    v = CU.coefficient(p.name, args.seed) * t ** ((dim[p.name] - 4) / 2)
                vals[p.name] = fixed.get(p.name, v)
            for n, code in internal:
                vals[n] = eval(code, ns, vals)
            return vals

        # particles by PDG code
        part = {p.pdg_code: p for p in P.all_particles}
        e, mu, W = part[11], part[13], part[24]
        nus = [part[c] for c in (12, 14, 16) if c in part]
        mass_of = lambda p, vals, pdg: abs(vals[p.mass.name]) or abs(vals[lep[pdg]])
        gold = [p.name for p in P.all_particles if getattr(p, "GoldstoneBoson", False)]

        # the vertices of muon decay: W-lepton vertices and four-lepton contacts
        verts = read_vertices(ufo, P)
        want_w = {}
        for n in nus:
            # ebar nu_e W takes the W of charge +1 in a listing that conserves charge, nubar_mu mu W the other
            want_w[("e", n.name)] = sorted([e.name, n.antiname, W.name if W.charge > 0 else W.antiname])
            want_w[("mu", n.name)] = sorted([mu.antiname, n.name, W.antiname if W.charge > 0 else W.name])
        chans = [(ni, nj) for ni in nus for nj in nus]
        want_c = {(ni.name, nj.name): sorted([e.name, ni.antiname, nj.name, mu.antiname]) for ni, nj in chans}
        sel_w = {k: [v for v in verts if sorted(v[0]) == s] for k, s in want_w.items()}
        sel_c = {k: [v for v in verts if sorted(v[0]) == s] for k, s in want_c.items()}
        for (side, n), vs in sel_w.items():
            for v in vs:
                ch = sum(next(p for p in P.all_particles if p.name == x).charge for x in v[0])
                if abs(ch) > 1e-9:
                    sys.exit(f"{ufo}: the vertex {v[0]} does not conserve charge, so the W of the {side} side is not "
                             "the one assumed")
        if 12 not in part or 14 not in part or not sel_w[("e", part[12].name)] or not sel_w[("mu", part[14].name)]:
            sys.exit(f"{ufo}: no W vertex of (e, nu_e) or of (mu, nu_mu)")
        wanted = {c for vs in list(sel_w.values()) + list(sel_c.values()) for v in vs for cs in v[3].values() for c in cs}
        coup = read_couplings(ufo, wanted)
        ccode = {k: compile(v[0], k, "eval") for k, v in coup.items()}

        zm3, zm4, cache = ZeroMomentum(3), ZeroMomentum(4), {}

        def structure(lname):
            if lname not in cache:
                lo = getattr(L, lname)
                cache[lname] = ((zm3 if len(lo.spins) == 3 else zm4).tensor(lo.structure, lo.spins), lo.structure)
            return cache[lname]

        # each W vertex as [(coupling, M[m, row, col])], the row the barred fermion
        def w_terms(vs, row, col):
            terms = []
            for parts, cols, lors, cp in vs:
                i_row, i_col, i_w = parts.index(row), parts.index(col), [k for k, x in enumerate(parts) if x in (W.name, W.antiname)][0]
                for (ci, li), cs in cp.items():
                    if cols[ci].strip() != "1":
                        sys.exit(f"colour structure {cols[ci]} in a lepton vertex")
                    T, st = structure(lors[li])
                    if np.abs(T).max() == 0:
                        continue
                    for _, tens in Z.parse(st) or []:
                        fl = Z.fermion_flow(tens)
                        if fl not in (None, {}) and fl != {i_col + 1: i_row + 1}:
                            sys.exit(f"{lors[li]} = {st} in {parts}: fermion flow {fl}, not {col} -> {row}")
                    M = np.transpose(T, (i_w, i_row, i_col))
                    terms += [(c, M) for c in cs]
            return terms

        # each contact vertex as [(coupling, E[e, nu_i, nu_j, mu])] with the signs MadGraph gives it
        def c_terms(vs, ni, nj):
            rows, colsl = {e.name, nj.name}, {ni.antiname, mu.antiname}
            ref, crossed = {(ni.antiname, e.name), (mu.antiname, nj.name)}, {(ni.antiname, nj.name), (mu.antiname, e.name)}
            terms = []
            for parts, cols, lors, cp in vs:
                if {parts[0], parts[2]} != colsl or {parts[1], parts[3]} != rows:
                    sys.exit(f"{parts}: the fermions are not listed as MadGraph reads a four-fermion vertex, "
                             "antifermion then fermion on each line")
                lines = {(parts[0], parts[1]), (parts[2], parts[3])}
                p_rel = 1 if lines == ref else -1 if lines == crossed else None
                if p_rel is None:
                    sys.exit(f"{parts}: the lines {lines} are neither those of the W exchange nor crossed")
                axes = (parts.index(e.name), parts.index(ni.antiname), parts.index(nj.name), parts.index(mu.antiname))
                for (ci, li), cs in cp.items():
                    if cols[ci].strip() != "1":
                        sys.exit(f"colour structure {cols[ci]} in a lepton vertex")
                    T, st = structure(lors[li])
                    if np.abs(T).max() == 0:
                        continue
                    sgn = Z.structure_sign(st)
                    if sgn is None:
                        sys.exit(f"{lors[li]} = {st}: no fermion flow")
                    terms += [(c, p_rel * sgn * np.transpose(T, axes)) for c in cs]
            return terms

        W_e = {n.name: w_terms(sel_w[("e", n.name)], e.name, n.antiname) for n in nus}
        W_m = {n.name: w_terms(sel_w[("mu", n.name)], n.name, mu.antiname) for n in nus}
        C4 = {(ni.name, nj.name): c_terms(sel_c[(ni.name, nj.name)], ni, nj) for ni, nj in chans}

        def michel(t):
            vals = evaluate_parameters(t)
            g = {k: complex(eval(c, ns, vals)) for k, c in ccode.items()}
            mw = abs(vals[W.mass.name])
            norm = 2 * math.sqrt(2) * vals[gf_name]         # 2/v^2 of the input G_F
            out = {}
            for ni, nj in chans:
                V1 = sum((g[c] * M for c, M in W_e[ni.name]), np.zeros((4, 4, 4), complex))
                V2 = sum((g[c] * M for c, M in W_m[nj.name]), np.zeros((4, 4, 4), complex))
                E = 1j / mw ** 2 * np.einsum("mab,m,mcd->abcd", V1, GLOW, V2)
                E = E + sum((g[c] * T for c, T in C4[(ni.name, nj.name)]), np.zeros((4,) * 4, complex))
                # the neutrinos are left-handed: nu_e enters as P_L nu_e, nubar_mu as nubar_mu P_R
                El = np.einsum("abcd,be,fc->aefd", E, PL, PR)
                sol, *_ = np.linalg.lstsq(np.stack([B_V.ravel(), B_S.ravel()], 1), El.ravel(), rcond=None)
                cV, cS = 1j * sol[0], 1j * sol[1]              # L = -(cV O_V + cS O_S), the vertex is -i c
                rest = np.linalg.norm(El - sol[0] * B_V - sol[1] * B_S)
                out[(ni.name, nj.name)] = (cV / norm, cS / norm, rest / norm, np.linalg.norm(E - El) / norm)
            me, mm = mass_of(e, vals, 11), mass_of(mu, vals, 13)
            x = (min(me, mm) / max(me, mm)) ** 2 if max(me, mm) > 0 else 0.0
            return out, x, vals

        def rate(out, x):
            w = 2 * math.sqrt(x) * g_mu(x) / f_mu(x)
            r2 = sum(abs(A) ** 2 + abs(S) ** 2 / 4 + w * (A * S.conjugate()).real for A, S, _, _ in out.values())
            return math.sqrt(r2) - 1

        main_ch = (part[12].name, part[14].name)
        # the Standard-Model point
        out0, x0, _ = michel(0.0)
        A0, S0, rest0, _ = out0[main_ch]
        print(f"{ufo}")
        print(f"   {len(on)} of {len(dim)} Wilson coefficients on" + (f" (matching {args.only!r})" if args.only else "")
              + f", seed {args.seed}; {lep[11]} = {args.yme:g}, {lep[13]} = {args.ymm:g} GeV, x = m_e^2/m_mu^2 = {x0:.6g}")
        if gold:
            print(f"   the Goldstone bosons {' '.join(gold)} are not exchanged: the W is exchanged in unitary gauge")
        print(f"   Standard-Model point: A - 1 = {A0 - 1:.2e}, S = {abs(S0):.1e}, outside the Michel basis {rest0:.1e}")
        sm_ok = abs(A0 - 1) < 1e-12 and abs(S0) < 1e-12 and rest0 < 1e-12
        if not sm_ok:
            print("   FAIL: the Standard-Model point does not give the input G_F")

        out1, _, v1 = michel(1.0)
        A1, S1, rest1, rh1 = out1[main_ch]

        def wcoup(terms, vals):
            g = {k: complex(eval(c, ns, vals)) for k, c in ccode.items() if any(k == t[0] for t in terms)}
            V = sum((g[c] * M for c, M in terms), np.zeros((4, 4, 4), complex))
            return np.einsum("mab,m,mba->", V, GLOW, np.array([PL @ CU.GAMMA[m] for m in range(4)])) / 8   # Tr(V^m P_L gamma_m)/8
        v0 = evaluate_parameters(0.0)
        fe = wcoup(W_e[main_ch[0]], v1) / wcoup(W_e[main_ch[0]], v0)
        fm = wcoup(W_m[main_ch[1]], v1) / wcoup(W_m[main_ch[1]], v0)
        other = max((max(abs(o[0]), abs(o[1])) for k, o in out1.items() if k != main_ch), default=0.0)
        print(f"   t = 1: W couplings of e and mu / SM - 1 = {fe - 1:.4e}, {fm - 1:.4e}; M_W = {abs(v1[W.mass.name]):.6g}")
        print(f"          A - 1 = {A1 - 1:.4e}, S = {S1:.4e}, outside the Michel basis {rest1:.1e}, "
              f"right-handed neutrino part {rh1:.1e}, other neutrino flavours at most {other:.1e}")

        ts = [2.0 ** -k for k in range(args.halvings + 1)]
        dev = []
        print(f"   {'t':>10}  {'A - 1':>12}  {'|S|':>10}  {'sqrt2 GF v^2 - 1':>17}  ratio")
        for t in ts:
            out, x, _ = michel(t)
            d = rate(out, x)
            A, S = out[main_ch][:2]
            r = f"{dev[-1] / d:7.2f}" if dev and abs(d) > FLOOR and abs(dev[-1]) > FLOOR else ""
            dev.append(d)
            print(f"   {t:10.3e}  {(A - 1).real:+12.4e}  {abs(S):10.3e}  {d:+17.4e}  {r}")
        pairs = [dev[k - 1] / dev[k] for k in range(1, len(dev)) if abs(dev[k]) > FLOOR and abs(dev[k - 1]) > FLOOR]
        last = pairs[-3:]
        clean = rest1 < 1e-9 * max(1.0, abs(A1))
        if max(abs(d) for d in dev) <= FLOOR:
            ok, why = True, f"the deviation stays below {FLOOR:g} at every strength"
        elif len(last) < 3:
            ok, why = False, "fewer than three halvings above the rounding floor: raise the coefficients or the Yukawas"
        else:
            order = math.log2(min(last))
            ok = min(last) >= 6.5
            why = (f"the deviation falls by {' '.join(f'{z:.2f}' for z in last)} over the last halvings, "
                   f"order t^{order:.2f}" + ("" if ok else ": a term of the input relations is missing at this order"))
        ok = ok and sm_ok and clean
        if not clean:
            why += "; the amplitude has a part outside the Michel basis"
        print(f"G_F from the muon-decay rate: {'PASS' if ok else 'FAIL'}, {why}")
        return 0 if ok else 1
    finally:
        CU.leave_ufo(ufo)


if __name__ == "__main__":
    sys.exit(main())
