#!/usr/bin/env python3
"""The seven- and eight-gluon vertices of the Q_{G^4} operators with a dual field strength.

    wolframscript -file validate/g4_highleg.wls merge <cache dir> <out dir> <block>=<coefficient> ...
    python3 validate/g4_highleg.py write <gen.fr> <out dir> <coefficient> ...      (which that calls)
    python3 validate/g4_highleg.py check <gen.fr> <dump.json> [--points N]
    python3 validate/g4_highleg.py ufo   <gen.fr> <model dir> [--points N]

What it does.  FeynRules exceeds 122 GB on these vertices even one monomial at a time, so ./dim8 build
stops it at six legs for the six operators of CAPPED_WCS there.  This script writes the rest from the
operator itself.  An operator of Q_{G^4} is a number times four field strengths and Eps, f and dSUN
tensors, and FS[G,mu,nu,a] = del[G[nu,a],mu] - del[G[mu,a],nu] - gs f[a,b,c] G[mu,b] G[nu,c], with the
minus sign of our covariant derivative, D = del + i gs T G.  So a vertex of n gluons takes n - 4 field
strengths in their two-field piece and one derivative term from each of the others, and it is

    i (-i)^(8-n) (-gs)^(n-4) c / Lam^4  x  the sum over the n! assignments of the legs to the fields,

with del_mu -> -i p_mu, as FeynRules has it.  A pair of Eps tensors is written as metric tensors,
Eps[a,b,c,d] Eps[e,f,g,h] = -Det[ME], as validate/fr_worker.wls does.  There is no symbolic algebra and
no memory problem: at most 40320 assignments, each a sorting of tensors.  Terms equal up to the names
of the summed indices and the antisymmetry of f and Eps are collected, and a group of terms that
vanishes through the Jacobi identity is left out, which empties the vertices that are zero, those of
seven and eight gluons of Q_{G^4}^{(2)} and of eight gluons of Q_{G^4}^{(5)}.

When to reach for it.  ./dim8 build calls validate/g4_highleg.wls merge, for those six operators and
no other, so a person only needs `check` and `ufo`.  Any other operator is built by
FeynRules, and validate/fr_compare.wls is the test for those.

What its output means.  `write` puts one <block>.highleg.json per operator in the directory, the terms
of each nonzero vertex, and the blocks it is given are complete up to eight gluons once
validate/g4_highleg.wls has merged them.  It stops with status 1 if a vertex disagrees with the exact
value of validate/dualdual_highleg.py.  `check` and `ufo` print one line per operator and number of
gluons and a final PASS or FAIL, with status 1 on FAIL.

Believe it when.  `check` takes three routes to the same number at random rational colour vectors,
polarisations and momenta, with exact arithmetic over Q(sqrt 3): the multilinear coefficient of the
operator on plane waves (validate/dualdual_highleg.py, which knows nothing of permutations and is itself
tested on the Yang-Mills vertices), this script at every number of gluons on all nine operators, and the
vertices in the cache, which are FeynRules' own at up to six gluons for the six operators and at up to
eight for Q_{G^4}^{(1)}, Q_{G^4}^{(3)} and Q_{G^4}^{(7)}.  So the permutation sum is tested against
FeynRules on the vertices FeynRules can reach, signs, the factor of i and the Levi-Civita convention
included, and the new vertices against the plane waves.  It must also fail: each operator is compared
with every other, and one coefficient of each vertex is flipped, and these must disagree, or the script
stops.  `ufo` repeats the comparison on the vertices of a written UFO, which adds WriteUFO and the
translation into Metric, P and Epsilon, on all nine operators, FeynRules' vertices and these side by side.
"""
import argparse
import collections
import itertools
import json
import os
import random
import re
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dualdual_highleg as DD

Op = collections.namedtuple("Op", "wc block coef eps fs d")
ALL_WCS = tuple(f"c8G4x{k}" for k in range(1, 10))
Q1 = (Fr(1), Fr(0))
DNZ = [(a, b, c, DD.d[a][b][c]) for a in range(8) for b in range(8) for c in range(8) if not DD.qzero(DD.d[a][b][c])]


# ---------- the operators, read from the line FeynRules reads ----------------------------------
def read_operator(text, wc):
    """The operator of coefficient wc from its line in gen.fr.  Its block is the Module around it."""
    m = re.search(r"^\s*%s/Lam\^4 \(\((.*)\)\),?\s*$" % re.escape(wc), text, re.M)
    if not m:
        sys.exit(f"no line of the form {wc}/Lam^4 ((...)) in gen.fr")
    blocks = re.findall(r"^(L8op\d+) := Module", text[:m.start()], re.M)
    coef, eps, fs, dt = Fr(1), [], [], []
    for tok in re.findall(r"\(\d+/\d+\)|\w+\[[^\]]*\]|\S+", m.group(1)):
        args = tuple(tok[tok.index("[") + 1:-1].split(",")) if "[" in tok else ()
        if re.fullmatch(r"\(\d+/\d+\)", tok):
            coef *= Fr(tok[1:-1])
        elif tok.startswith("Eps["):
            eps.append(args)
        elif tok.startswith("FS[G,"):
            fs.append(args[1:])
        elif tok.startswith("dSUN["):
            dt.append(args)
        else:
            sys.exit(f"{wc}: a factor that is no field strength or tensor: {tok}")
    if len(fs) != 4 or len(eps) > 2:
        sys.exit(f"{wc}: {len(fs)} field strengths and {len(eps)} Eps tensors")
    return Op(wc, blocks[-1], coef, eps, fs, dt)


def parity(order):
    """1 for an odd permutation of 0..n-1 given as a list, 0 for an even one"""
    return sum(1 for i in range(len(order)) for j in range(i + 1, len(order)) if order[i] > order[j]) % 2


# ---------- canonical forms of the two tensors of a term ------------------------------------------
def canon_colour(tensors):
    """(sign, key) of a product of f, d and delta.  An argument is a leg (positive integer) or a summed
    index (anything else, appearing twice).  Colour here is a forest, so each tree is walked from the
    tensor with its lowest leg, the arguments of a tensor in order of the lowest leg behind them, and
    summed indices are numbered as they are met, -1, -2, ...  Products equal up to the names of the summed
    indices and the antisymmetry of f then have equal keys.  The Jacobi identity is not seen here."""
    where = {}
    for i, (_, args) in enumerate(tensors):
        for x in args:
            if not isinstance(x, int):
                where.setdefault(x, []).append(i)

    def other(x, i):
        a, b = where[x]
        return b if a == i else a

    def lowest(i, came):
        return min(x if isinstance(x, int) else lowest(other(x, i), x) for x in tensors[i][1] if x != came)

    sign, out, names, seen = 1, [], {}, set()

    def walk(i, came):
        nonlocal sign
        seen.add(i)
        kind, args = tensors[i]
        rest = sorted((x if isinstance(x, int) else lowest(other(x, i), x), p) for p, x in enumerate(args) if x != came)
        order = ([args.index(came)] if came is not None else []) + [p for _, p in rest]
        if kind == "f" and parity(order):
            sign = -sign
        new = []
        for p in order:
            x = args[p]
            if not isinstance(x, int) and x not in names:
                names[x] = -(len(names) + 1)
            new.append(x if isinstance(x, int) else names[x])
        out.append((kind, tuple(new)))
        for p in order:
            x = args[p]
            if not isinstance(x, int) and x != came:
                walk(other(x, i), x)

    roots = sorted((min(x for x in args if isinstance(x, int)), i) for i, (_, args) in enumerate(tensors)
                   if any(isinstance(x, int) for x in args))
    for _, i in roots:
        if i not in seen:
            walk(i, None)
    if len(seen) != len(tensors):
        raise ValueError(f"a colour tensor with no leg in its tree: {tensors}")
    return sign, tuple(out)


def contraction(x, y):
    """A pair of Lorentz carriers, positive for the polarisation of a leg, negative for its momentum"""
    if x > 0 and y > 0:
        return ("m", min(x, y), max(x, y))
    if x < 0 and y < 0:
        return ("s", min(-x, -y), max(-x, -y))
    return ("v", -min(x, y), max(x, y))


def canon_eps(args):
    """(sign, entry) of Levi-Civita on four carriers, (0, None) when two of them are equal"""
    order = sorted(range(4), key=lambda i: args[i])
    entry = tuple(args[i] for i in order)
    if len(set(entry)) < 4:
        return 0, None
    return (-1 if parity(order) else 1), ("e",) + entry


# ---------- the sum over assignments ---------------------------------------------------------------
def template(op, opened, signs):
    """(sign, colour tensors with slots as integers, deltas between slots, Lorentz structures) of one
    choice of field-strength pieces.  A Lorentz structure is (sign, pairs of carriers, Eps carriers), a
    carrier being (+1, slot) for the field on a slot and (-1, slot) for its derivative."""
    slots, tensors, sign, it = [], [("d", t) for t in op.d], 1, iter(signs)
    for i, (mu, nu, a) in enumerate(op.fs):
        if i in opened:
            slots += [(mu, f"b{i}", None), (nu, f"c{i}", None)]
            tensors.append(("f", (a, f"b{i}", f"c{i}")))
        else:
            s = next(it)
            sign *= s
            slots.append((nu, a, mu) if s > 0 else (mu, a, nu))
    carried = {}
    for s, (_, a, _) in enumerate(slots):
        carried.setdefault(a, []).append(s)
    single = {a: v[0] for a, v in carried.items() if len(v) == 1}
    deltas = [v for v in carried.values() if len(v) == 2]
    colour = [(k, tuple(single.get(x, x) for x in args)) for k, args in tensors]
    where = {}
    for s, (l, _, dl) in enumerate(slots):
        where.setdefault(l, []).append((1, s))
        if dl is not None:
            where.setdefault(dl, []).append((-1, s))

    def one(l):
        if len(where[l]) != 1:
            raise ValueError(f"{op.wc}: the Eps index {l} is not on one field strength")
        return where[l][0]

    onEps = {l for e in op.eps for l in e}
    pairs = [tuple(v) for l, v in where.items() if l not in onEps]
    if any(len(p) != 2 for p in pairs):
        raise ValueError(f"{op.wc}: a Lorentz index that is not contracted")
    if len(op.eps) == 2:
        lorentz = [(1 if parity(list(q)) else -1, pairs + [(one(op.eps[0][i]), one(op.eps[1][q[i]])) for i in range(4)], None)
                   for q in itertools.permutations(range(4))]
    elif len(op.eps) == 1:
        lorentz = [(1, pairs, [one(l) for l in op.eps[0]])]
    else:
        lorentz = [(1, pairs, None)]
    return sign, colour, deltas, lorentz


def group_terms(op, opened, n, flip=None):
    """{(colour key, Lorentz key): rational} of one choice of which field strengths give two fields"""
    part = {}
    for signs in itertools.product((1, -1), repeat=8 - n):
        sign, colour, deltas, lorentz = template(op, opened, signs)
        for perm in itertools.permutations(range(1, n + 1)):
            ct = [(k, tuple(perm[x] if isinstance(x, int) else x for x in args)) for k, args in colour]
            cs, ck = canon_colour(ct)
            if deltas:
                ck = tuple(sorted(("D", tuple(sorted((perm[a], perm[b])))) for a, b in deltas)) + ck
            for ls, prs, eps in lorentz:
                ents = [contraction(t1 * perm[s1], t2 * perm[s2]) for (t1, s1), (t2, s2) in prs]
                es = 1
                if eps is not None:
                    es, ent = canon_eps([t * perm[s] for t, s in eps])
                    if es == 0:
                        continue
                    ents.append(ent)
                key = (ck, tuple(sorted(ents)))
                part[key] = part.get(key, 0) + sign * cs * ls * es
    return {k: op.coef * v for k, v in part.items() if v}


def vertex_terms(op, n):
    """{(colour key, Lorentz key): rational}: the n-gluon vertex without its i (-i)^(8-n) (-gs)^(n-4) c / Lam^4.
    A group of terms that vanishes at random points is left out."""
    total = {}
    rng = random.Random(zero_seed(op.wc, n))
    points = [Point(draw(n, rng)) for _ in range(3)]
    for opened in itertools.combinations(range(4), n - 4):
        part = group_terms(op, opened, n)
        if all(DD.qzero(vertex_value(part, pt)) for pt in points):
            continue
        for k, v in part.items():
            total[k] = total.get(k, 0) + v
    return {k: v for k, v in total.items() if v}


def zero_seed(wc, n):
    return sum(ord(c) for c in wc) * 100 + n


# ---------- evaluation at a point ---------------------------------------------------------------
def draw(n, rng):
    """A random point, on which no colour vector, polarisation or momentum is zero"""
    while True:
        waves = DD.random_waves(n, rng, -9, 9)
        if all(any(w[0]) and any(w[1]) and any(w[2]) for w in waves):
            return waves


class Point:
    """Colour vectors, polarisations and momenta, by leg, in the form of validate/dualdual_highleg.py"""

    def __init__(self, waves):
        self.waves = waves
        self.col = {i + 1: [(Fr(x), Fr(0)) for x in w[0]] for i, w in enumerate(waves)}
        self.pol = {i + 1: w[1] for i, w in enumerate(waves)}
        self.mom = {i + 1: w[2] for i, w in enumerate(waves)}
        self.c_memo, self.l_memo, self.t_memo = {}, {}, {}

    def vec(self, x):
        return self.pol[x] if x > 0 else self.mom[-x]


def subtree(pt, d):
    """The 8-vector T^{a b c} u^b v^c of a tree named by nested tuples, its first argument open"""
    w = pt.t_memo.get(d)
    if w is not None:
        return w
    u, v = (pt.col[x] if isinstance(x, int) else subtree(pt, x) for x in d[2:])
    w = [DD.Q0] * 8
    for a, b, c, t in (DD.fnz if d[0] == "f" else DNZ):
        if DD.qzero(u[b]) or DD.qzero(v[c]):
            continue
        w[a] = DD.qadd(w[a], DD.qmul(t, DD.qmul(u[b], v[c])))
    pt.t_memo[d] = w
    return w


def colour_value(key, pt):
    val = pt.c_memo.get(key)
    if val is not None:
        return val
    trees = [t for t in key if t[0] != "D"]
    where = {}
    for i, (_, args) in enumerate(trees):
        for x in args:
            if x < 0:
                where.setdefault(x, []).append(i)

    def name(i, came):
        k, args = trees[i]
        return (k,) + tuple(x if x > 0 else ("open" if x == came else name(where[x][0] if where[x][1] == i else where[x][1], x))
                            for x in args)

    val, seen = Q1, set()
    for t in key:
        if t[0] == "D":
            s = DD.Q0
            for u, v in zip(pt.col[t[1][0]], pt.col[t[1][1]]):
                s = DD.qadd(s, DD.qmul(u, v))
            val = DD.qmul(val, s)
    for i in range(len(trees)):
        if i in seen:
            continue
        # a tree is written from its root, which holds no open index, and its tensors follow it in the key
        d = name(i, None)
        stack = [d]
        count = 0
        while stack:
            e = stack.pop()
            count += 1
            stack += [x for x in e[1:] if isinstance(x, tuple)]
        seen |= set(range(i, i + count))
        args = [pt.col[x] if isinstance(x, int) else subtree(pt, x) for x in d[1:]]
        s = DD.Q0
        for a, b, c, tv in (DD.fnz if d[0] == "f" else DNZ):
            if DD.qzero(args[0][a]) or DD.qzero(args[1][b]) or DD.qzero(args[2][c]):
                continue
            s = DD.qadd(s, DD.qmul(tv, DD.qmul(args[0][a], DD.qmul(args[1][b], args[2][c]))))
        val = DD.qmul(val, s)
    pt.c_memo[key] = val
    return val


def factor_value(ent, pt):
    v = pt.l_memo.get(ent)
    if v is not None:
        return v
    if ent[0] == "m":
        v = DD.dot(pt.pol[ent[1]], pt.pol[ent[2]])
    elif ent[0] == "v":
        v = DD.dot(pt.mom[ent[1]], pt.pol[ent[2]])
    elif ent[0] == "s":
        v = DD.dot(pt.mom[ent[1]], pt.mom[ent[2]])
    else:
        vs = [pt.vec(x) for x in ent[1:]]
        v = sum(s * vs[0][q[0]] * vs[1][q[1]] * vs[2][q[2]] * vs[3][q[3]] for q, s in DD.eps4.items())
    pt.l_memo[ent] = v
    return v


def vertex_value(terms, pt):
    """The sum over a dictionary of terms, as a number of Q(sqrt 3)"""
    acc = DD.Q0
    for (ck, lk), r in terms.items():
        lv = r
        for ent in lk:
            lv *= factor_value(ent, pt)
            if lv == 0:
                break
        if lv:
            acc = DD.qadd(acc, DD.qscale(colour_value(ck, pt), lv))
    return acc


def plane_waves(waves, n, ops):
    """{coefficient: n-field coefficient of X and Y forms}, validate/dualdual_highleg.py, without any
    factor.  That script numbers Q_{G^4}^{(k)} as 424 + k."""
    cache = {}

    def xy(S):
        if S not in cache:
            A, G1, G2 = DD.fields(waves, S)
            cache[S] = DD.XYpieces(G1, G2)
        return cache[S]

    return {o.wc: DD.multilinear(waves, n, lambda S, k=424 + int(o.wc.rsplit("x", 1)[1]): DD.op_piece(k, *xy(S), n))
            for o in ops}


def expected(ops, wave_values, wc):
    """The value of vertex_terms of an operator from the plane waves, in which X and Y have no factor"""
    return DD.qscale(wave_values[wc], ops[wc].coef)


# ---------- the vertices FeynRules wrote: the terms from validate/g4_highleg.wls dump ---------------
def read_lorentz(factors):
    """(sign, key) of the Lorentz factors of one term.  A summed index is resolved through the factor
    that gives it a value: FV[k,d] makes d the momentum of leg k, ME[d,x] makes it whatever x is."""
    bind = {}

    def res(x):
        return bind.get(x, x) if isinstance(x, str) else x

    pending, progress = list(factors), True
    while progress:
        progress, rest = False, []
        for ff in pending:
            if ff[0] == "FV" and isinstance(res(ff[2]), str):
                bind[res(ff[2])] = -ff[1]
                progress = True
            elif ff[0] == "ME" and isinstance(res(ff[1]), str) != isinstance(res(ff[2]), str):
                x, y = (res(ff[1]), res(ff[2])) if isinstance(res(ff[1]), str) else (res(ff[2]), res(ff[1]))
                bind[x] = y
                progress = True
            else:
                rest.append(ff)
        pending = rest

    def final(x):
        y = res(x)
        if isinstance(y, str):
            raise ValueError(f"a Lorentz index with nothing to contract it: {x} in {factors}")
        return y

    sign, out = 1, []
    for ff in pending:
        if ff[0] == "ME":
            out.append(contraction(final(ff[1]), final(ff[2])))
        elif ff[0] == "FV":
            out.append(contraction(-ff[1], final(ff[2])))
        elif ff[0] == "SP":
            out.append(contraction(-ff[1], -ff[2]))
        elif ff[0] == "Eps":
            es, ent = canon_eps([final(x) for x in ff[1:]])
            if es == 0:
                return 0, None
            sign *= es
            out.append(ent)
        else:
            raise ValueError(f"a Lorentz factor this script cannot read: {ff}")
    return sign, tuple(sorted(out))


def read_dumped(vertex, wc):
    """{(colour key, Lorentz key): (real part, imaginary part)} of a vertex of the dump, which holds the
    coefficient, gs and Lam in its terms; all three are checked and removed"""
    n, out = vertex["legs"], {}
    for t in vertex["terms"]:
        if {k: v for k, v in t["par"].items() if v} != {wc: 1, "Lam": -4, **({"gs": n - 4} if n > 4 else {})}:
            raise ValueError(f"{wc}: a term with the parameters {t['par']}")
        cs, ck = canon_colour([({"f": "f", "dSUN": "d"}[x[0]], tuple(x[1:])) for x in t["col"] if x[0] != "IndexDelta"])
        ds = [x for x in t["col"] if x[0] == "IndexDelta"]
        if ds:
            ck = tuple(sorted(("D", tuple(sorted(x[1:]))) for x in ds)) + ck
        ls, lk = read_lorentz(t["lor"])
        if ls == 0:
            continue
        s = cs * ls
        re_, im_ = out.get((ck, lk), (0, 0))
        out[(ck, lk)] = (re_ + s * Fr(t["c"][0], t["c"][1]), im_ + s * Fr(t["c"][2], t["c"][3]))
    return out


def phase(n):
    """(real, imaginary) of i (-i)^(8-n) (-1)^(n-4)"""
    return {8: (0, 1), 7: (-1, 0), 6: (0, -1), 5: (1, 0), 4: (0, 1)}[n]


# ---------- the commands ---------------------------------------------------------------------------
def to_lists(terms):
    return [[r.numerator, r.denominator, [[k, *args] for k, args in ck], [list(e) for e in lk]]
            for (ck, lk), r in sorted(terms.items(), key=lambda kv: repr(kv[0]))]


def cmd_write(a):
    text = open(a.genfr, errors="replace").read()
    ops = {w: read_operator(text, w) for w in a.coefficients}
    os.makedirs(a.outdir, exist_ok=True)
    rng = random.Random(20261101)
    bad = 0
    for w, op in ops.items():
        verts = {}
        for n in (7, 8):
            terms = vertex_terms(op, n)
            for _ in range(2):
                waves = draw(n, rng)
                want = expected(ops, plane_waves(waves, n, [op]), w)
                got = vertex_value(terms, Point(waves))
                if got != want:
                    print(f"[write] {op.block} {w} n={n}: {DD.fmt(got)} against the plane waves {DD.fmt(want)}")
                    bad += 1
            print(f"[write] {op.block} {w}: {n} gluons, {len(terms)} terms" + ("" if terms else " (zero vertex)"))
            if terms:
                verts[str(n)] = to_lists(terms)
        path = os.path.join(a.outdir, op.block + ".highleg.json")
        with open(path + ".tmp", "w") as out:
            json.dump({"block": op.block, "wc": w, "vertices": verts}, out)
        os.replace(path + ".tmp", path)
    if bad:
        sys.exit(f"[write] {bad} disagreements with the plane waves")
    print("[write] every vertex agrees with the plane waves")


def self_test(ops, terms, n, rng):
    """Each vertex must differ from the plane waves of every other operator, and from itself with one
    term changed.  Otherwise the comparison cannot fail."""
    waves = draw(n, rng)
    wv = plane_waves(waves, n, ops.values())
    pt = Point(waves)
    for w in ops:
        val = vertex_value(terms[w], pt)
        for x in ops:
            if x != w and val == expected(ops, wv, x) and not DD.qzero(val):
                sys.exit(f"[check] the vertex of {w} equals the plane waves of {x} at {n} gluons: the test cannot fail")
        # a tensor can vanish at a point of small integers, so the flip is of a term that contributes
        for key, r in terms[w].items():
            if vertex_value({key: r}, pt) != DD.Q0:
                if vertex_value({**terms[w], key: -r}, pt) == val:
                    sys.exit(f"[check] the vertex of {w} at {n} gluons does not see a flipped coefficient")
                break
        else:
            if terms[w]:
                sys.exit(f"[check] no term of the vertex of {w} at {n} gluons contributes at this point")


def cmd_check(a):
    text = open(a.genfr, errors="replace").read()
    ops = {w: read_operator(text, w) for w in ALL_WCS}
    dump = json.load(open(a.dump)) if a.dump else {}
    fails = 0
    rng = random.Random(a.seed)
    for n in range(4, 9):
        terms = {w: vertex_terms(op, n) for w, op in ops.items()}
        self_test(ops, terms, n, rng)
        cached = {}
        for w, op in ops.items():
            v = [x for x in dump.get(op.block, []) if x["legs"] == n]
            cached[w] = read_dumped(v[0], w) if v else None
        status = {w: [0, 0] for w in ops}
        nonzero = {w: False for w in ops}
        for _ in range(a.points):
            waves = draw(n, rng)
            wv = plane_waves(waves, n, ops.values())
            pt = Point(waves)
            ph = phase(n)
            for w in ops:
                want = expected(ops, wv, w)
                nonzero[w] = nonzero[w] or not DD.qzero(want)
                if vertex_value(terms[w], pt) != want:
                    status[w][0] += 1
                if cached[w] is not None:
                    re_ = vertex_value({k: v[0] for k, v in cached[w].items() if v[0]}, pt)
                    im_ = vertex_value({k: v[1] for k, v in cached[w].items() if v[1]}, pt)
                    if re_ != DD.qscale(want, ph[0]) or im_ != DD.qscale(want, ph[1]):
                        status[w][1] += 1
        for w, op in ops.items():
            bad = status[w][0] + status[w][1]
            where = "not in the cache" if cached[w] is None else f"cache {len(cached[w])} structures"
            missing = cached[w] is None and nonzero[w] and a.dump
            leftover = cached[w] is not None and not nonzero[w]
            ok = not bad and not missing and not leftover
            fails += not ok
            print(f"{'PASS' if ok else 'FAIL'}  {op.block} {w} {n} gluons: "
                  f"{'nonzero' if nonzero[w] else 'zero'}, written {len(terms[w])} terms, {where}, "
                  f"against the plane waves written {status[w][0]} and cache {status[w][1]} disagreements of {a.points}")
    print("OVERALL: " + ("FAIL" if fails else "PASS"))
    sys.exit(1 if fails else 0)


def cmd_ufo(a):
    """The vertices of a written UFO against the plane waves, floating point, one operator at a time"""
    import math
    import numpy as np
    import vertex_contract as VC
    from index_vs_ufo import read_model
    text = open(a.genfr, errors="replace").read()
    ops = {w: read_operator(text, w) for w in ALL_WCS}
    lam, alpha = 3000.0, 0.1184
    gs = math.sqrt(4 * math.pi * alpha)
    r = read_model(a.model, inputs={"Lam": lam, "aS": alpha}, only=set(ALL_WCS))
    fails = 0
    rng = random.Random(a.seed)
    G = VC.G
    for n in range(4, 9):
        entries = [e for e in r["entries"] if set(e[1]) == {21} and len(e[1]) == n]
        if len(entries) != 1:
            sys.exit(f"[ufo] {len(entries)} vertices of {n} gluons in {a.model}")
        ents = entries[0][2]
        for _ in range(a.points):
            waves = draw(n, rng)
            wv = plane_waves(waves, n, ops.values())
            # WriteUFO makes every particle outgoing, FV -> -FV (MakeOutgoingParticles in PYIntVertices.m), so
            # P of a model is minus the momentum of FeynRules' vertex, its own vertices and these alike
            ext = VC.Ext({i + 1: G @ np.array(w[1], float) for i, w in enumerate(waves)}, {},
                         {i + 1: np.array(w[0], float) for i, w in enumerate(waves)},
                         {i + 1: -G @ np.array(w[2], float) for i, w in enumerate(waves)})
            reps = {i + 1: 8 for i in range(n)}
            cval, lval = {}, {}
            tot = {w: 0j for w in ops}
            for colour, struct, g in ents:
                touched = [w for w in ops if r["resp"].get((g, w, 1), 0j)]
                if not touched:
                    continue
                if colour not in cval:
                    cval[colour] = VC.evaluate(colour, ext.colour_ns(reps))
                if struct not in lval:
                    lval[struct] = VC.evaluate(struct, ext.lorentz_ns())
                for w in touched:
                    tot[w] += r["resp"][(g, w, 1)] * cval[colour] * lval[struct]
            ph = complex(*phase(n))
            for w, op in ops.items():
                want = expected(ops, wv, w)
                val = (float(want[0]) + float(want[1]) * 3 ** 0.5) * ph * gs ** (n - 4) / lam ** 4
                ok = abs(tot[w] - val) <= 1e-9 * max(abs(val), abs(tot[w])) or (val == 0 and abs(tot[w]) * lam ** 4 < 1e-6)
                fails += not ok
                print(f"{'PASS' if ok else 'FAIL'}  {op.block} {w} {n} gluons: UFO {tot[w] * lam ** 4:.8g}, "
                      f"plane waves {val * lam ** 4:.8g} (times Lam^4)")
    print("OVERALL: " + ("FAIL" if fails else "PASS"))
    sys.exit(1 if fails else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("write")
    p.add_argument("genfr")
    p.add_argument("outdir")
    p.add_argument("coefficients", nargs="+")
    p.set_defaults(fn=cmd_write)
    p = sub.add_parser("check")
    p.add_argument("genfr")
    p.add_argument("dump", nargs="?")
    p.add_argument("--points", type=int, default=3)
    p.add_argument("--seed", type=int, default=20261101)
    p.set_defaults(fn=cmd_check)
    p = sub.add_parser("ufo")
    p.add_argument("genfr")
    p.add_argument("model")
    p.add_argument("--points", type=int, default=2)
    p.add_argument("--seed", type=int, default=20261102)
    p.set_defaults(fn=cmd_ufo)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
