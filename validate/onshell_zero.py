#!/usr/bin/env python3
"""Which three-point vertices of two fermions vanish between on-shell massless spinors.

    python3 validate/onshell_zero.py                                   the released models
    python3 validate/onshell_zero.py --fg tests/gen_smoke/onshell_fg   and the Goldstone vertices
    python3 validate/onshell_zero.py --list-fg-blocks                  the blocks that UFO needs

gen/lambda_series.py needs to know, for a three-point operator vertex with two fermion legs and a
boson leg, what it gives when both fermions are on shell and massless and the boson is off shell.
A vertex whose fermions are both external is then the whole story, and a vertex that vanishes
there differs from zero only by terms proportional to the fermions' equations of motion, which
cancel the propagator of an internal fermion.  Each vertex of each operator block is given one of
  zero     it vanishes between on-shell massless spinors at a generic point,
  k2       it does not, but it vanishes wherever k^2 = 0, k the boson's momentum, and so is k^2
           times a remainder,
  generic  anything else,
  absent   it has no linear response to the block's coefficients in the model: FeynRules listed
           the vertex, but its couplings cancel,
  unchecked  its structures did not name one row and one column leg, and it was not evaluated
           (gen/lambda_series.py then counts it as it is, and names it),
and the outcomes are written to build/onshell_zero.json under "outcomes", {block: {"Z uq uqbar":
outcome, ...}}, the legs sorted as gen/lambda_routes.py sorts them, beside "models" and
"feynman_gauge_model", the models read, and "disagreements", the vertices that two of them judge
differently.  A coupling that names a coefficient of a block and cannot be evaluated would leave its
vertex judged on the couplings that can, or read as absent, so the file is then not written and the
run stops with the couplings named.  A coupling that names none of them enters no outcome, so it stops
nothing: the Feynman-gauge model, written without the truncation of the released models, holds shift
products of the Standard Model at high NP that are too long for the reader.

How.  Each model is read with the reader of validate/index_vs_ufo.py, which gives every coupling's
linear response to a coefficient at zero, the internal parameters it moves included, with the light
masses that the card sets to zero at values of their own (validate/generic_inputs.py), so that a
first-generation vertex proportional to a Yukawa coupling is seen.  A vertex is
contracted with the external states of validate/vertex_contract.py: the boson leg with a random
complex polarisation vector, colour indices with random colour vectors, and the fermion legs with
solutions of the massless Dirac equation.  The leg on the row of a structure's spinor indices takes
a row solution, w p-slash = 0, and the leg on the column a column solution, p-slash w = 0, since
Gamma(3,2,1) is (gamma^mu)_{s2 s1} and ALOHA contracts it with the outgoing fermion's spinor on
the left.  The momenta are complex, p = |lambda>[lambdatilde| for each fermion, so that
k^2 = <12>[21] can vanish with the two momenta independent: on the branch <12> = 0 and on the
branch [12] = 0.  A polynomial in independent spinors that vanishes on both branches is divisible
by <12>[21] = k^2, so a vertex that vanishes on both, but not at a generic point, is k2.  A
vertex counts as vanishing at a point where it is below 1e-7 of its largest single term at a generic
off-shell point, evaluated with random spinors.  The scale is taken off shell because a term that
carries a fermion's p^2, as (p1 - p2).k = p1^2 - p2^2 in the Higgs vertex of psi^2H^2D^3 does,
vanishes at every on-shell point whatever the spinors, so that at the same point the vertex would be
compared with its own rounding.  For the same reason a vertex whose couplings cancel is recognised
at an off-shell point, with random spinors.  Only the first-generation members are
evaluated (u, d, e, ve), since the top quark is not massless.  As in validate/index_vs_ufo.py, a
coefficient counts in a coupling only where it appears by name, so that the shifts an input scheme
spreads over the Standard Model vertices are not taken for an operator's own vertex, and a block
is evaluated only in a model that has all of its coefficients and is written in the block's basis
(gen/basis.py).  The Goldstone vertices need a
Feynman-gauge model of the blocks concerned, which FeynRules writes in the development tree when it
builds the Feynman-gauge vertex lists.  The release carries their outcomes in
build/onshell_zero.json, but not that model.
"""
import argparse
import collections
import json
import os
import re
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import basis  # noqa: E402
import index_vs_ufo as IU  # noqa: E402
import vertex_contract as VC  # noqa: E402
from check_legs import DIM6 as DIM6_WCS  # noqa: E402  the dimension-six coefficients by class
from lambda_routes import DIM6 as DIM6_BLOCKS  # noqa: E402  L6cl block -> class

OUT = os.path.join(ROOT, "build", "onshell_zero.json")
# The models read by default, in order, the first that has a block deciding its outcomes.  dim68_is holds
# every three-point vertex of two fermions of build/vertex_index.json: it declares every
# dimension-eight coefficient and the dimension-six classes, and its input scheme absorbs no vertex
# of two fermions (build/vertex_index_absorbed.json, where the one absorbed vertex of two fermions,
# the W-lepton vertex of Q_{l^2H^4D}^{(2,4)}, is missing from dim8_mw alone).  Without dim8_plain,
# as in the public tree, dim68_is alone is read.  dim8_plain, read first where it is present, has
# no input relations, so that a dimension-eight coefficient moves only its own vertices there, and
# dim68_is then checks it.  Without either, dim8_is reads the dimension-eight blocks, which it holds
# with all their vertices of two fermions, and the dimension-six vertices are left out of the file,
# which ./dim8 series then names.  dim8_mw is never read by default, since a vertex it lacks would
# be written absent for every model.
MODELS = ([m for m in ("models/dim8_plain", "models/dim68_is") if os.path.isfile(os.path.join(ROOT, m, "parameters.py"))]
          or [m for m in ("models/dim8_is",) if os.path.isfile(os.path.join(ROOT, m, "parameters.py"))])
# The same models in the Murphy basis (gen/basis.py), where present, are read after them.  They alone carry
# the vertices of the class-11 operators of that basis, and the blocks the two bases share must come out the
# same in both.
MODELS += [m + "_murphy" for m in MODELS if os.path.isfile(os.path.join(ROOT, m + "_murphy", "parameters.py"))]
FERMIONS = {"uq", "uqbar", "dq", "dqbar", "l", "lbar", "vl", "vlbar"}
GOLDSTONES = {"G0", "GP", "GPbar"}
LIGHT = {1, 2, 11, 12}                       # |PDG| of u, d, e, ve
# a vertex vanishes at a point below this fraction of its largest term: the responses are symmetric
# differences, good to about 1e-12, and a vertex that does not vanish is of the order of its terms
TOL = 1e-7
SIG = [np.array([[0, 1], [1, 0]], complex), np.array([[0, -1j], [1j, 0]]), np.array([[1, 0], [0, -1]], complex)]
# the arguments of a spinor structure that carry the row and the column index
SPIN_ARGS = {"Gamma": (1, 2), "Gamma5": (0, 1), "ProjM": (0, 1), "ProjP": (0, 1), "Identity": (0, 1),
             "Sigma": (2, 3), "C": (0, 1)}
ORDER = {"absent": 0, "zero": 1, "k2": 2, "generic": 3}


def three_point(index):
    """{block: {legs}} of the three-point vertices with two fermion legs in a vertex index."""
    out = collections.defaultdict(set)
    for b, verts in index.items():
        for v in verts:
            if len(v) == 3 and sum(x in FERMIONS for x in v) == 2:
                out[b].add(" ".join(sorted(v)))
    return out


def goldstone_blocks(index):
    """three_point(index) for the blocks with such a vertex with a Goldstone boson: the blocks that
    the Feynman-gauge model is written from (in the development tree, by hpc/run_fg_index.sh).  That
    model declares the coefficients of every block, so a block outside it would read as absent
    there."""
    return {b: ks for b, ks in three_point(index).items() if any(GOLDSTONES & set(k.split()) for k in ks)}


def block_wcs():
    """{block: its coefficients}: the dimension-eight blocks from docs/block_index.json, with the
    coefficients of their further flavour structures, the dimension-six ones by class from
    validate/check_legs.py."""
    out = {e["block"]: list(e["wcs"]) + sorted({re.sub(r"(Re|Im)$", "", f) for f in e.get("flavour", [])})
           for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json")))}
    for b, (cls, _) in DIM6_BLOCKS.items():
        out[b] = DIM6_WCS[cls].split()
    return out


def model_names(model):
    """{coefficient: the names it has in the model}, a complex one as itself and its parts."""
    txt = open(os.path.join(model, "parameters.py")).read()
    out = collections.defaultdict(list)
    for n in re.findall(r"(\w+) = Parameter\(\s*name = '\w+'", txt):
        out[re.sub(r"(Abs|Ph|Re|Im)$", "", n)].append(n)
    return out


# ------------------------------------------------------------------------------ kinematics ----

def null(lam, lamt):
    """The momentum p^mu of the rank-one matrix p_mu sigma^mu = |lambda>[lambdatilde|."""
    P = np.outer(lam, lamt)
    return np.array([np.trace(P)] + [-np.trace(s @ P) for s in SIG]) / 2


def slash(p):
    return np.einsum("mij,m->ij", VC.GAM, VC.G @ p)


def solutions(m):
    """The two unit vectors w with m w = 0, for a 4x4 matrix of rank two."""
    _, _, vh = np.linalg.svd(m)
    return [vh[2].conj(), vh[3].conj()]


def point(rng, branch):
    """(p_row, p_col): two complex massless momenta, generic, with <12> = 0 or with [12] = 0."""
    def z():
        return rng.normal(size=2) + 1j * rng.normal(size=2)
    lr, ltr, lc, ltc = z(), z(), z(), z()
    a = complex(rng.normal(), rng.normal())
    if branch == "angle":
        lc = a * lr
    elif branch == "square":
        ltc = a * ltr
    return null(lr, ltr), null(lc, ltc)


def offshell(rng):
    """(p_row, p_col): two generic complex momenta, not null, of the size of those of point()."""
    return tuple(rng.normal(size=4) + 1j * rng.normal(size=4) for _ in range(2))


def roles(ents):
    """(row leg, column leg) of the spinor indices of a vertex, the same in every structure, or None."""
    rows, cols = set(), set()
    for _, struct, _ in ents:
        for name, args in re.findall(r"\b(Gamma5|Gamma|ProjM|ProjP|Identity|Sigma|C)\(([^()]*)\)", struct):
            a = [int(x) for x in args.split(",")]
            i, j = SPIN_ARGS[name]
            if a[i] > 0:
                rows.add(a[i])
            if a[j] > 0:
                cols.add(a[j])
    if len(rows) == 1 and len(cols) == 1 and rows != cols:
        return rows.pop(), cols.pop()
    return None


# ------------------------------------------------------------------------- classification ----

def _values(ents, resp, direction, codes, r, c, b, pr, pc, rng, onshell):
    """[(|vertex|, scale)] over the spinor solutions and two draws of the boson's polarisation and the
    colour vectors: the vertex contracted with on-shell spinors at (pr, pc) (onshell), or with random
    spinors at a generic off-shell point, and the largest single term contracted with random spinors
    at a generic off-shell point, where no term vanishes for want of a fermion's p^2."""
    qr, qc = offshell(rng)
    if not onshell:
        pr, pc = qr, qc
    mom = {r: pr, c: pc, b: -(pr + pc)}
    mom_off = {r: qr, c: qc, b: -(qr + qc)}
    reps = {k + 1: VC.colour_of(p) for k, p in enumerate(codes)}
    if onshell:
        pairs = [(x, y) for x in solutions(slash(pr).T) for y in solutions(slash(pc))]
    else:
        pairs = [(rng.normal(size=4) + 1j * rng.normal(size=4), rng.normal(size=4) + 1j * rng.normal(size=4))]
    out = []
    for _ in range(2):
        pol = {k: rng.normal(size=4) + 1j * rng.normal(size=4) for k in (1, 2, 3)}
        col = {k: rng.normal(size=8 if reps[k] == 8 else 3) + 1j * rng.normal(size=8 if reps[k] == 8 else 3)
               for k in (1, 2, 3)}
        ref = {r: rng.normal(size=4) + 1j * rng.normal(size=4), c: rng.normal(size=4) + 1j * rng.normal(size=4)}
        ref = {k: w / np.linalg.norm(w) for k, w in ref.items()}
        e_ref = VC.Ext(pol, {**ref, b: None}, col, mom_off)
        scale = 0.0
        for colour, struct, g in ents:
            d = resp.get((g,) + direction, 0j)
            if d:
                scale = max(scale, abs(d * VC.evaluate(colour, e_ref.colour_ns(reps))
                                       * VC.evaluate(struct, e_ref.lorentz_ns())))
        for x, y in pairs:
            spin = {r: x / np.linalg.norm(x), c: y / np.linalg.norm(y), b: None}
            e = VC.Ext(pol, spin, col, mom)
            tot = 0j
            for colour, struct, g in ents:
                d = resp.get((g,) + direction, 0j)
                if d:
                    tot += d * VC.evaluate(colour, e.colour_ns(reps)) * VC.evaluate(struct, e.lorentz_ns())
            out.append((abs(tot), scale))
    return out


def _vanishes(vals):
    return all(v <= TOL * s for v, s in vals) and any(s > 0 for _, s in vals)


def classify(ents, codes, resp, directions, seed=0):
    """The outcome of one vertex (its UFO entries, all of one particle list) for one block."""
    rc = roles(ents)
    if rc is None:
        return None
    r, c = rc
    b = ({1, 2, 3} - {r, c}).pop()
    best = "absent"
    for direction in directions:
        if not any(resp.get((g,) + direction, 0j) for _, _, g in ents):
            continue
        rng = np.random.default_rng(seed)
        pr, pc = point(rng, None)
        off = _values(ents, resp, direction, codes, r, c, b, pr, pc, rng, False)
        if _vanishes(off):
            continue                                   # the couplings cancel: no vertex in this direction
        gen = _values(ents, resp, direction, codes, r, c, b, pr, pc, rng, True)
        pr2, pc2 = point(rng, None)
        gen += _values(ents, resp, direction, codes, r, c, b, pr2, pc2, rng, True)
        if _vanishes(gen):
            out = "zero"
        else:
            branches = []
            for branch in ("angle", "square", "angle", "square"):
                pa, pb = point(rng, branch)
                branches += _values(ents, resp, direction, codes, r, c, b, pa, pb, rng, True)
            out = "k2" if _vanishes(branches) else "generic"
        if ORDER[out] > ORDER[best]:
            best = out
    return best


def evaluate(model, wanted, goldstones=False, failed=None):
    """{block: {legs: outcome}} for the (block, legs) pairs of wanted whose block has all of its
    coefficients in the model and belongs to its basis, from its first-generation vertices.  The couplings that the reader
    of validate/index_vs_ufo.py could not evaluate and that name one of these coefficients are
    printed and added to failed, since a vertex would be judged without them: on the couplings that
    remain, or as absent when none does."""
    names = model_names(model)
    wcs = block_wcs()
    # parameters.py declares the coefficients of both bases whatever blocks were written, so a block of the
    # other basis would have all of its coefficients and no vertex, and read as absent
    mb = basis.of_model(model)
    mine = {b: [n for w in wcs[b] for n in names[w]] for b in wanted
            if wcs.get(b) and all(w in names for w in wcs[b]) and basis.in_basis(wcs[b], mb)}
    if not mine:
        return {}
    only = {n for ns in mine.values() for n in ns}
    r = IU.read_model(model, only=only, goldstones=goldstones, generic=True)
    # a coefficient's response counts in a coupling where it appears by name: the operator's own
    # vertex as FeynRules writes it, not a shift of the input relations
    literal = {g: set(re.findall(r"\b[A-Za-z_]\w*\b", expr)) for g, expr in re.findall(
        r"(GC_\w+) = Coupling\(\s*name = '\w+',\s*value = '([^']*)'", open(os.path.join(model, "couplings.py")).read())}
    bad = [g for g in r["failed"] if literal.get(g, set()) & only]
    if bad:
        print(f"{os.path.relpath(model, ROOT)}: {len(bad)} couplings could not be evaluated, e.g. {', '.join(bad[:3])}")
        if failed is not None:
            failed += [(model, g) for g in bad]
    elif r["failed"]:
        print(f"{os.path.relpath(model, ROOT)}: {len(r['failed'])} couplings could not be evaluated and name none of "
              f"the coefficients, e.g. {', '.join(r['failed'][:3])}")
    resp = {k: d for k, d in r["resp"].items() if k[1] in literal.get(k[0], ())}
    byleg = collections.defaultdict(lambda: collections.defaultdict(list))   # key -> particle list -> entries
    codes_of = {}
    for pnames, codes, ents in r["entries"]:
        if len(pnames) != 3 or any(n not in IU.LABEL for n in pnames):
            continue
        labels = [IU.LABEL[n] for n in pnames]
        ferm = [abs(cd) for lab, cd in zip(labels, codes) if lab in FERMIONS]
        if len(ferm) != 2 or not set(ferm) <= LIGHT:
            continue
        byleg[" ".join(sorted(labels))][tuple(pnames)] += ents
        codes_of[tuple(pnames)] = codes
    out = {}
    for b, ns in mine.items():
        directions = [(n, v) for n in ns for v in (1.0, 1j)]
        for key in sorted(wanted[b]):
            # absent when no vertex of the content responds; unchecked when none could be read
            got, read = "absent", not byleg.get(key)
            for plist, ents in byleg.get(key, {}).items():
                o = classify(ents, codes_of[plist], resp, directions)
                if o is not None:
                    read = True
                    if ORDER[o] > ORDER[got]:
                        got = o
            out.setdefault(b, {})[key] = got if read else "unchecked"
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", default=MODELS, help="the unitary-gauge models (default: %(default)s)")
    ap.add_argument("--fg", default=None, help="a Feynman-gauge model for the vertices with a Goldstone boson")
    ap.add_argument("--out", default=OUT)
    ap.add_argument("--list-fg-blocks", action="store_true",
                    help="print the blocks of build/vertex_index_fg.json with a three-point vertex of two fermions "
                         "and a Goldstone boson, the content of the Feynman-gauge model")
    a = ap.parse_args(argv[1:])
    fgi = os.path.join(ROOT, "build", "vertex_index_fg.json")
    if (a.list_fg_blocks or a.fg) and not os.path.exists(fgi):
        sys.exit("build/vertex_index_fg.json is missing: the Goldstone vertices to evaluate are those of the "
                 "Feynman-gauge vertex lists, which are not in this tree")
    if a.list_fg_blocks:
        want = goldstone_blocks(json.load(open(fgi)))
        print("\n".join(sorted(want, key=lambda b: (b[:4], int(b[4:]) if b[4:].isdigit() else 0, b))))
        return 0
    wanted = three_point(json.load(open(os.path.join(ROOT, "build", "vertex_index.json"))))
    outcomes, source, disagree, failed, read = {}, {}, [], [], []
    for m in a.models:
        path = m if os.path.isabs(m) else os.path.join(ROOT, m)
        if not os.path.isfile(os.path.join(path, "parameters.py")):
            print(f"skipped {m}: no parameters.py")
            continue
        read.append(m)
        for b, per in evaluate(path, wanted, failed=failed).items():
            for key, o in per.items():
                if (b, key) in source:
                    if outcomes[b][key] != o:
                        disagree.append([b, key, source[(b, key)], outcomes[b][key], m, o])
                    continue
                outcomes.setdefault(b, {})[key] = o
                source[(b, key)] = m
        print(f"read {m}")
    if a.fg:
        # the blocks the model was written from, whose vertices without a Goldstone boson are compared
        # with the released models' outcomes and whose Goldstone vertices are taken from it
        wanted_fg = goldstone_blocks(json.load(open(fgi)))
        path = a.fg if os.path.isabs(a.fg) else os.path.join(ROOT, a.fg)
        # named relative to the tree in what is written, so that no machine's path reaches build/
        fg = os.path.relpath(path, ROOT) if os.path.abspath(path).startswith(ROOT + os.sep) else a.fg
        for b, per in evaluate(path, wanted_fg, goldstones=True, failed=failed).items():
            for key, o in per.items():
                if (b, key) in source:
                    if outcomes[b][key] != o:
                        disagree.append([b, key, source[(b, key)], outcomes[b][key], fg, o])
                    continue
                if not GOLDSTONES & set(key.split()):
                    continue                       # a unitary vertex the released models did not carry
                outcomes.setdefault(b, {})[key] = o
                source[(b, key)] = fg
        print(f"read {fg} (Feynman gauge)")
    if not read:
        sys.exit("no model to read: give --models, or put models/dim68_is (or models/dim8_is) in place")
    if failed:
        # an unevaluated coupling would leave its vertex judged without it, so nothing is written
        print(f"not written: {len(failed)} couplings could not be evaluated (above), and a vertex whose couplings "
              "did not evaluate would be judged on the others or read as absent")
        return 1
    data = {"models": read, "feynman_gauge_model": fg if a.fg else None, "outcomes": outcomes, "disagreements": disagree}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(data, open(a.out + ".tmp", "w"), indent=1, sort_keys=True)
    os.replace(a.out + ".tmp", a.out)
    count = collections.Counter(o for per in outcomes.values() for o in per.values())
    print(f"wrote {os.path.relpath(a.out, ROOT)}: {sum(count.values())} vertices of "
          f"{len(outcomes)} blocks, " + ", ".join(f"{k} {count[k]}" for k in list(ORDER) + ["unchecked"] if count[k]))
    for row in disagree:
        print("  disagreement: {} {}: {} in {}, {} in {}".format(row[0], row[1], row[3], row[2], row[5], row[4]))
    return 1 if disagree else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
