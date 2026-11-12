#!/usr/bin/env python3
"""The amplitude of a process topology by topology, as a series in lambda.

    gen/lambda_series.py "u u~ > w+ w-" [--latex | --json] [--group channel|vbf|none]
    gen/lambda_series.py "u u~ > w+{0} w-{0}"
    gen/lambda_series.py "p p > h h j j QCD=0" --vbf
    gen/lambda_series.py "u u~ > e+ e-" --model dim68_mw_murphy
    ./dim8 series ...                       (the same command)

gen/lambda_routes.py gives each class its cheapest tree.  This gives the series of the paper's
Sec. 5: for every topology of the process (the set of its propagators), the smallest power of
lambda of each class in that topology, with every product of Standard Model couplings that
reaches it, and the Standard Model's own terms, so that the Standard Model couplings, the
dimension-six terms and the dimension-eight terms of a process stand next to each other.  The
rules are those of gen/lambda_routes.py: (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1), a
Standard Model three-point vertex counts lambda^-2 with a momentum or a fermion pair and
lambda^-1 with a vev, a four-point vertex lambda^0, a propagator lambda^4, an operator vertex
of dimension d with m legs and p vacuum insertions lambda^(d-12+2m+p), and a top mass insertion,
which a top line needs between two legs of different chirality, lambda^1, written m_t among the
couplings.  Higher powers of a class in the same topology are dropped, as in the paper, and within
a group of topologies a class is given at its smallest power.

The terms are grouped (--group).  channel, the default at four legs, names the contact term c and
the s, t and u channels, t pairing the first initial particle with the first final one, and t and
u are merged for a fermion-antifermion initial state, as in eq:amp-ww.  vbf counts the propagators
that carry a fermion pair away from the rest of the tree, two being the core and fewer the quark
line, as in eq:amp-hhjj.  none gives one series.  A line is known by the externals it carries, so
identical particles (u u~ > u u~) merge topologies that differ only in which of them a line
carries.  A Standard Model coupling is named by its
fields, a quark q, a charged lepton e, a neutrino nu, any electroweak boson V, a gluon g, the Higgs
boson h and a Goldstone boson phi, so that photon and Z exchange are one term.  The top Yukawa
couplings are g_{\\bar tth} and g_{\\bar tt\\phi}, and a top mass insertion is m_t.

The model.  The vertices are those of the model that --model names, a path or a name in models/,
models/dim68_mw unless another is given, read as ./dim8 select reads it (dim8, _series_model).  The
series holds the dimension-eight operators of the model's basis alone (gen/basis.py).  In the default
basis every Higgs field of class 11, psi^2H^2D^3, carries a derivative, so that none of its vertices
has fewer than four fields, and a model with the suffix _murphy has the operators of the Murphy basis
there, which have three-point vertices.  The lists are without the vertices that the input scheme of
the model absorbs (build/vertex_index_absorbed.json) and without the operators that have no vertex in
the model, and they hold the dimension-six classes only for a model with a dimension-six sector of its
own, each with the vertices that a coefficient of the class moves in that model (build/dim6_index.json,
dim8 _live_dim6).  They are checked against the couplings of the model first: every dimension-eight coefficient
that the couplings name must belong to an operator whose vertices the lists hold, and those of class
11 to the basis the lists are read in, and the command stops otherwise.  The operators of the input
relations of the model's scheme, {MW, MZ, GF} or {alpha, MZ, GF}, shift every Standard Model term, by
v^4/Lambda^4 (lambda^8) at dimension eight and v^2/Lambda^2 (lambda^4) at dimension six, and have no
topology of their own.  They are listed after the terms for a process with an electroweak Standard
Model tree, the operators that ./dim8 select puts in its second group, and Q_{l^2e^2H^2}^{(1,2)}, which
enter G_F only with nonzero electron and muon Yukawa couplings, are named apart.  A model without input
relations (dim8_plain) says so.  The default is the combined model, where ./dim8 select takes
models/dim8_mw, since the series sets the dimension-six terms beside the dimension-eight ones.

Three things decide which terms are printed.

Interference.  Every fermion leg carries the chirality of its field, L or R, and a propagator joins
two legs of one label through its pslash and two labels through its mass, which only a top line
has, at one more power of lambda (gen/lambda_routes.py, propagator).  The external fermions of a
tree therefore have definite chiralities, its configuration, and amplitudes of different
configurations do not interfere.  A massless external fermion must match exactly, since it takes
the chirality of the vertex it ends on and no mass can change it.  A term interferes with the
Standard Model where its configuration is that of a Standard Model tree of the same external
particles: at leading order where the smallest power of the Standard Model trees of that
configuration is the Standard Model's leading power, and k powers of lambda down where it lies k
above it, when the term is marked so and never set in bold.  A right-handed quark line in
q qbar > W_T W_T is the case, whose photon and Z trees cancel up to M_Z^2/E^2 (gen/lambda_routes.py,
cancellation), two powers down.  A tree whose massless external fermions match no Standard Model
tree at any power is left out.  An external top quark of the other chirality costs the mass term of
its spinor, m_t/E: the term interferes one power down, is marked so and is never set in bold, and
with two such tops (m_t/E)^2.  A tree is compared with the Standard Model configuration that leaves
the fewest powers down in all, and among the trees of a term at its power the one that interferes
best decides.  Identical external particles are told apart by name and chirality only, so the
configurations are compared as multisets.  An operator none of whose trees interferes is left out,
and a class all of whose operators are left out goes with them.  The exact test needs the trees,
and a quicker one, which it implies, sets an operator aside before they are built (interfering()):
its barred and unbarred fermion fields must carry the same names of the Murphy basis (l, e, q, u,
d), counted with multiplicity, since a Standard Model line keeps its chirality and its sector and
so the name of its field.  A top line
is the exception, where a Yukawa coupling or the mass turns q into u.  It ends on a b or t quark,
since the CKM matrix is block diagonal, so that q and u count as one name in an initial and final
state with such a quark among its external particles, and as two in the others.

The Standard Model amplitude.  An initial state with no Standard Model tree (g g > w+ w-) has
nothing to interfere with.  Its terms are printed apart, as square only, and none is left out,
since the square does not ask for the chirality of the external fermions.

On-shell zeros.  A three-point operator vertex of two light fermions can vanish when both are on
shell and massless, or be proportional to the square k^2 of its boson's momentum
(build/onshell_zero.json, written by validate/onshell_zero.py).  Such a vertex differs from one
that vanishes on shell by terms proportional to the fermions' equations of motion.  A zero vertex
whose two fermions are external therefore gives no term, and with a fermion on an internal line
it cancels that line's propagator, leaving a local term of the same power.  A k2 vertex on an
internal boson gives k^2/(k^2 - M^2) = 1 + M^2/(k^2 - M^2), a local term of the same power and,
for a massive boson, the propagator two powers of lambda higher.  With the boson external it costs
k^2 = M^2 ~ v^2, two powers of lambda, and its equation-of-motion terms cancel the propagators of
its internal fermions.  A local term keeps the Standard Model couplings of the rest of its tree, so
that the contact term of psi^2H^2D^3 in u u~ > w+ w- reads (1 + g_{\\bar qqV} + g_{VVV}) times its
coefficient.  Without the file the vertices are counted as they are, and the output says so, and
so is a vertex that the file holds no outcome for or holds as unchecked, which the output names.

A W or a Z may carry MadGraph's polarisation mark, {T} or {0}.  A longitudinal one is its
Goldstone boson at no cost or the gauge boson at one power of lambda (gen/lambda_routes.py,
channel_slots), and the power of a class, or of a Standard Model topology, in the channel is the
smallest over these choices.  The Standard Model amplitude of the channel is found the same way,
and a dimension-eight term at most Delta = 4 powers of lambda above it, which grows at least as
E^4/Lambda^4 relative to it, is set in bold.  Delta is below 4 only in a channel whose Standard
Model amplitude lies above lambda^(2n-8), since a dimension-eight tree is at least lambda^(2n-4).
An unmarked W or Z is counted as transverse, as in the paper, and the output says so.  The
Goldstone vertices come from the Feynman-gauge lists (process.load_data, gauge="feynman"),
build/vertex_index_fg.json and build/sm_vertices_fg.json, which are made in Feynman gauge with
Mathematica and FeynRules, ship in build/ with the release and also give the internal lines.  A
propagator counts lambda^4 in Feynman gauge, while the k^mu k^nu/M^2 part of a unitary-gauge one
counts lambda^2, and Goldstone exchange carries it.  Without these lists the unitary ones are used,
which is exact wherever every internal W or Z ends on a light quark or lepton, and a longitudinal
mark is refused.

--vbf gives vector-boson fusion in the effective-W approximation: the W and Z bosons that the quark
lines exchange are taken as on-shell partons of definite polarisation.  The core,
w+{p} w-{p} > X and z{p} z{p} > X with X the final state without its jets, is dressed with the two
quark currents and their propagators, lambda^4 g_{\\bar qqV}^2, and the quark-line terms,
q qbar' V{p} > X, with one current and one propagator, lambda^2 g_{\\bar qqV}.  A quark line keeps
the trees in which its quark pair does not meet a single line, since a tree in which it does is a
tree of a core, which the cores count with both currents.  Each part carries the Standard Model
power of its own channel plus its dressing.  A statement about
longitudinal W bosons in vector-boson fusion is a statement in this approximation, since the
process itself has no external W.  The six-point contact terms with both quark lines in one vertex
are not part of it, and --group vbf on the whole process gives them.
"""
import argparse
import itertools
import json
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import process as P  # noqa: E402
import lambda_routes as LR  # noqa: E402

FG_INDEX = os.path.join(ROOT, "build", "vertex_index_fg.json")
ONSHELL = os.path.join(ROOT, "build", "onshell_zero.json")
# the massive bosons: k^2 = M^2 ~ v^2 on an external one, and on an internal one a vertex
# proportional to k^2 leaves M^2/(k^2 - M^2) beside its local term (onshell_terms).  A Goldstone
# boson has the mass of its vector in Feynman gauge.
MASSIVE = {"Z", "W", "Wbar", "H", "G0", "GP", "GPbar"}
GROUP_ORDER = ["s", "t", "u", "c", "core", "line", ""]
GROUP_TEX = {"s": r"\mathcal{A}_s", "t": r"\mathcal{A}_t", "u": r"\mathcal{A}_u", "c": r"\mathcal{A}_c",
             "core": r"\mathcal{A}_{\rm core}", "line": r"\mathcal{A}_{\rm line}", "": r"\mathcal{A}"}


# ------------------------------------------------------------------------- coupling names ----

LETTER = {"uq": "q", "dq": "q", "l": "e", "vl": r"\nu"}
MASS = LR.TOP_MASS                           # a top mass insertion (gen/lambda_routes.py, propagator)
BOSON_LETTER = {"H": "h", "G0": r"\phi", "GP": r"\phi", "GPbar": r"\phi",
                "A": "V", "Z": "V", "W": "V", "Wbar": "V", "G": "g"}
BOSON_ORDER = ["h", r"\phi", "V", "g"]
PAIR_ORDER = ["q", "e", r"\nu"]


def _join(tokens):
    """LaTeX tokens run together, with a space after a control word that a letter follows."""
    s = ""
    for t in tokens:
        if re.search(r"\\[A-Za-z]+$", s) and t[:1].isalpha():
            s += " "
        s += t
    return s


def coupling_name(v):
    """The name of the Standard Model coupling of vertex v (FeynRules labels), the subscript of g in
    the paper: \\bar qqV, VVV, hVV, hhVV, \\phi\\phi V, ...  The fermion pair comes first, then the
    Higgs bosons, the Goldstone bosons, the electroweak bosons and the gluons.  A Yukawa vertex is a
    route only on a top line (gen/lambda_routes.py), and is \\bar tth or \\bar tt\\phi.  The two
    orientations of a charged current have one name."""
    ferm = [x for x in v if LR.is_fermion(x)]
    bos = [x for x in v if not LR.is_fermion(x)]
    toks = []
    if ferm:
        if any(b in LR.SCALARS for b in bos):
            toks += ["\\bar ", "t", "t"]
        else:
            bar = next(x for x in ferm if LR._parts(x)[1])
            unbar = next(x for x in ferm if not LR._parts(x)[1])
            a, b = sorted((LETTER[LR.CLASS[LR._parts(bar)[0]]], LETTER[LR.CLASS[LR._parts(unbar)[0]]]),
                          key=PAIR_ORDER.index)
            toks += ["\\bar ", a, b]
    for key in BOSON_ORDER:
        toks += [key] * sum(BOSON_LETTER[x] == key for x in bos)
    return _join(toks)


def ascii_name(name):
    """g_qqV for \\bar qqV, g_hphiV for h\\phi V: the names of the text output.  A mass insertion,
    m_t, keeps its name."""
    if name == MASS:
        return name
    return "g_" + name.replace("\\bar ", "").replace("\\phi", "phi").replace("\\nu", "v").replace(" ", "")


def factor_tex(name):
    """g_{\\bar qqV} for the coupling \\bar qqV, and m_t for a top mass insertion."""
    return name if name == MASS else f"g_{{{name}}}"


def latex_class(cls):
    return cls.replace("psi", r"\psi")


# ---------------------------------------------------------------------- the frontier search ----

def _keep(out, key, power, monos):
    """Keep the smaller power per key, and the union of the monomials at equal power."""
    old = out.get(key)
    if old is None or power < old[0]:
        out[key] = (power, frozenset(monos))
    elif power == old[0]:
        out[key] = (power, old[1] | frozenset(monos))


def _times(monos, extra=()):
    """The products of one monomial from each set of monos, with the names extra, each sorted."""
    acc = [tuple(extra)]
    for ms in monos:
        acc = [a + m for a in acc for m in ms]
    return frozenset(tuple(sorted(a)) for a in acc)


def _conf(combo, head=()):
    """The configuration of a tree from those of its subtrees (the keys of combo): the sorted tuple
    of (external fermion, chirality label), a multiset."""
    return tuple(sorted(head + sum((x[0][1] for x in combo), ())))


class Frontier(LR.Cheapest):
    """LR.Cheapest.reach returning frontiers instead of minima.  A frontier is {key: (power,
    monomials)}: the key is (topology, configuration), the topology the frozenset of the groups of
    externals that the propagators of the subtree carry, its own line included, and the
    configuration the chirality label of each external fermion of the subtree (_conf), so that the
    trees of one topology that differ in it are kept apart for the interference test.  The power is
    the smallest of the trees of that key, and the monomials every product of Standard Model
    coupling names, with m_t for each top mass insertion, that reaches it.  The fermion lines keep
    their generation and chirality labels, and the vertices and propagators their rules, through
    LR.Cheapest.variants and LR.Cheapest.assign, which this class does not change, and a photon or
    Z line between a right-handed current and a W pair costs what it costs there (LR.cancellation).  With
    configurations=False every configuration is empty, which leaves the powers as they are and the
    frontiers as small as without the labels, for a series with no interference test."""

    def __init__(self, sm, chains=None, configurations=True):
        super().__init__(sm, chains=chains)
        self.configurations = configurations
        self.fcache = {}
        self.vcache = {}

    def reach_all(self, f, group, up=None):
        """The frontier of the trees by which leg f reaches exactly the externals in group.  A leg
        that ends on an external fermion gives it its chirality label.  A fermion leg without a
        chirality label is the first external particle of the tree (sm_all), which enters its vertex
        without a propagator and takes the label of the leg it enters.  A class label tries each
        generation and, without a chirality label, each label, as in LR.Cheapest.reach.  up is what
        the vertex at the other end of a photon or Z line is, for the cancellation of a right-handed
        current against a W pair, as in LR.Cheapest.reach (LR.end_kind, LR.cancellation)."""
        if len(group) == 1 and LR.matches(f, group[0]):
            c = LR.chirality(f) if self.configurations and LR.is_fermion(f) else None
            return {(frozenset(), ((group[0], c),) if c else ()): (0, frozenset({()}))}
        if f not in LR.NEUTRAL:
            up = None
        key = (f, group, up)
        if key in self.fcache:
            return self.fcache[key]
        out = {}
        self.fcache[key] = out           # filled below; the recursion reaches smaller groups only
        if LR.is_fermion(f):
            gens = LR.generations(group, LR.sector(f))
            if LR.generation(f) is None:                 # a class label: each generation and label
                for g in sorted(gens):
                    for cf in ([LR.chirality(f)] if LR.chirality(f) else LR.labels(f)):
                        for k, (c, m) in self.reach_all(LR.tag(f, g, cf), group).items():
                            _keep(out, k, c, m)
                return out
            if LR.generation(f) not in gens:
                return out
        af = LR.anti(f)
        root = self.configurations and LR.is_fermion(f) and LR.chirality(f) is None
        for v in self._cands(af):
            w, name = self.weight(v), coupling_name(v)
            for rest, ins, c_af in self.variants(v, f, group):
                if len(rest) < 2 or len(rest) > len(group):
                    continue
                kd = LR.end_kind(v, rest, c_af)
                wv = w + len(ins) + LR.cancellation(f, up, kd)
                head = ((af, c_af),) if root else ()
                for parts in P._partitions(group, len(rest)):
                    subs = []
                    for r, g in zip(rest, parts):
                        s = self.reach_all(r, g, kd)
                        if not s:
                            break
                        subs.append(s)
                    else:
                        for combo in itertools.product(*(s.items() for s in subs)):
                            k = frozenset().union(*(x[0][0] for x in combo)) | {group}
                            c = wv + 4 + sum(x[1][0] for x in combo)
                            _keep(out, (k, _conf(combo, head)), c, _times([x[1][1] for x in combo], (name,) + ins))
        return out

    def sm_all(self, ext):
        """The frontier of the Standard Model trees of the externals ext (a sorted tuple), rooted at
        its first particle, whose line into the first vertex is external: the group of the rest is
        not a propagator and costs no lambda^4."""
        return {(k - {ext[1:]}, conf): (c - 4, m)
                for (k, conf), (c, m) in self.reach_all(LR.anti(ext[0]), ext[1:]).items()}

    def vertex_all(self, legs, ext, block=None, outcome=None):
        """The frontier of the trees through the operator vertex legs, without the vertex's own
        power, after the on-shell rule for a three-point vertex of two fermions (onshell_terms),
        which keeps the configuration.  Every assignment of the vertex is searched: the top line
        that lets an operator interfere need not start at its vertex, since a b leg of the vertex
        reaches one through a W or Goldstone vertex.  Cached on what decides it: the legs, the
        externals, the Dirac chains of the block, whether it is of dimension six, whose chains
        carry Yukawa couplings (LR.dim6_yukawa), and the on-shell outcome."""
        ways = self.chains.get(block)
        ckey = (tuple(legs), ext, frozenset(ways) if ways is not None else None, block in LR.DIM6, outcome)
        if ckey in self.vcache:
            return self.vcache[ckey]
        out = {}
        self.vcache[ckey] = out
        for spec in self.assign(legs, ext, block):
            for parts in P._partitions(ext, len(spec)):
                subs = []
                for leg, part in zip(spec, parts):
                    s = self.reach_all(leg, part)
                    if not s:
                        break
                    subs.append(s)
                else:
                    for combo in itertools.product(*(s.items() for s in subs)):
                        k = frozenset().union(*(x[0][0] for x in combo))
                        conf = _conf(combo)
                        c = sum(x[1][0] for x in combo)
                        m = _times([x[1][1] for x in combo])
                        for k2, dc in onshell_terms(outcome, spec, parts, k):
                            _keep(out, (k2, conf), c + dc, m)
        return out


def onshell_terms(outcome, spec, parts, key):
    """The (key, extra power) of each term that a tree through a three-point vertex of two light
    fermions gives, by the vertex's on-shell outcome (validate/onshell_zero.py): spec are its legs,
    parts the group of externals of each leg, a group of one being an external particle on its own
    line.  A vertex that vanishes on shell is a sum of terms proportional to the equation of motion
    of one of its fermions, p-slash or p^2 of that leg, each of which cancels the propagator of an
    internal fermion and leaves a local term of the same power.  A vertex proportional to k^2 on
    shell adds k^2 times a remainder.  On an internal boson k^2/(k^2 - M^2) = 1 + M^2/(k^2 - M^2)
    leaves a local term of the same power and, for a massive boson, the propagator two powers of
    lambda higher, and on an external massive boson k^2 = M^2 ~ v^2 stands in place of E^2, two
    powers of lambda.  A local term keeps the Standard Model couplings of the rest of its tree.  A
    zero or k2 vertex with a top quark, which is not massless, is counted as it is, and so is one
    without an outcome or with any other, unchecked among them.  An absent vertex gives no term at
    any generation.  validate/onshell_zero.py reads the first generation, and in the released
    models, whose dimension-eight couplings differ between generations only by the Yukawa
    couplings the flavour spurions carry, and whose light Yukawa couplings are not zero, a vertex
    with no response there has none for the top quark either.  A model that
    set a light Yukawa coupling to zero would need the third generation evaluated before a vertex
    is written absent."""
    if outcome not in ("zero", "k2", "absent"):
        return [(key, 0)]
    if outcome == "absent":
        return []
    ferm = [i for i, x in enumerate(spec) if LR.is_fermion(x)]
    if len(spec) != 3 or len(ferm) != 2 or any(
            (LR.CLASS[LR._parts(spec[i])[0]], LR.generation(spec[i])) in LR.HEAVY for i in ferm):
        return [(key, 0)]
    b = 3 - sum(ferm)
    out = [(key - {parts[i]}, 0) for i in ferm if len(parts[i]) > 1]
    if outcome == "k2":
        if len(parts[b]) > 1:
            out.append((key - {parts[b]}, 0))
        if spec[b] in MASSIVE:
            out.append((key, 2))
    return out


# --------------------------------------------------------------------------- topologies ----

def _slots_of(group, lab):
    """The slots of a group of externals, each label on the first free slot that has it."""
    used = set()
    for x in group:
        used.add(next(i for i, y in enumerate(lab) if y == x and i not in used))
    return frozenset(used)


def topology(key, lab):
    """A tree's topology, the frozenset of its internal lines, each the set of the slots on the side
    away from slot 0, so that the choices of a polarised slot (a Goldstone boson or the gauge boson)
    share their topologies."""
    full = frozenset(range(len(lab)))
    out = set()
    for g in key:
        s = _slots_of(g, lab)
        out.add(full - s if 0 in s else s)
    return frozenset(out)


def _fermion_pair(side, lab):
    other = set(range(len(lab))) - side
    return any(len(s) == 2 and all(LR.is_fermion(lab[i]) for i in s) for s in (side, other))


def _qqbar(lab):
    """A fermion and an antifermion in the initial state, for which t and u are one group."""
    a, b = lab[0], lab[1]
    return LR.is_fermion(a) and LR.is_fermion(b) and bool(LR._parts(a)[1]) != bool(LR._parts(b)[1])


def group_of(topo, lab, mode):
    """The group of a topology: c, s, t or u at four legs (channel), core or line (vbf, and line for
    the quark-line sub-amplitudes of --vbf), or ''."""
    if mode == "none":
        return ""
    if mode == "vbf":
        return "core" if sum(_fermion_pair(side, lab) for side in topo) >= 2 else "line"
    if mode == "line":
        # q qbar' V > X: a tree in which the fermion pair meets a single line is a tree of the core
        return "core" if any(_fermion_pair(side, lab) for side in topo) else "line"
    if not topo:
        return "c"
    (side,) = topo
    # by the labels, so that identical particles do not tell t from u
    other = sorted(lab[i] for i in side)
    if other == sorted(lab[2:4]):
        return "s"
    if other == sorted((lab[1], lab[3])):
        return "t"
    return "t" if _qqbar(lab) else "u"


def _channel_sig(lab, mode):
    if mode != "channel":
        return None
    return (tuple(sorted(lab[:2])), tuple(sorted((lab[1], lab[3]))), tuple(sorted((lab[1], lab[2]))), _qqbar(lab))


# ----------------------------------------------------------------------------- the filter ----

def interfering(top=False):
    """block -> whether its operator can interfere with the Standard Model at leading order in the
    light fermion masses in any tree, a test that needs no tree: in every term the barred and the
    unbarred fermion fields carry the same names of the Murphy basis, counted with multiplicity.
    With top=True the names q and u are one, as on a top line.  The exact test of a tree implies
    it.  A Standard Model line keeps its chirality, so a light one ends on two legs of one label,
    and keeps its sector, and the label and the sector give the name: L is q or l, and R is u, d or
    e, of the one class a right-handed line keeps since the W current is left-handed.  A barred
    field of the operator of name X therefore reaches a barred external fermion of name X, an
    unbarred one an unbarred external fermion of its name, and a line of the Standard Model alone
    a barred and an unbarred external fermion of one name.  The configuration of a Standard Model
    tree, at any power, holds every name as often barred as unbarred, so an operator that does not
    cannot match one.  A top line is the exception, where a Yukawa coupling or the mass joins q and u, and
    so is an external top quark of the other chirality.  The test is unchanged by a Fierz
    rearrangement: (qbar u)(ubar q) passes and (lbar e)(dbar q) fails.  The dimension-six blocks
    are judged by the chain structures of their operators (LR.DIM6_CHAINS), and a block passes when
    one of them does.  The test does not ask for the Yukawa couplings that the dimension-six chains
    carry, which the trees count (LR.dim6_yukawa)."""
    cache = interfering.__dict__.setdefault("cache", {})
    if top in cache:
        return cache[top]
    import dsl
    from operators import OPS

    def name(n):
        return "q" if top and n == "u" else n

    out = {}
    for i, op in enumerate(OPS):
        ok = True
        for t in op.terms:
            psis = [f for f in t.factors if isinstance(f, dsl.Psi)]
            if Counter(name(f.name) for f in psis if f.bar) != Counter(name(f.name) for f in psis if not f.bar):
                ok = False
                break
        out[f"L8op{i + 1}"] = ok
    for b in LR.DIM6:
        ops = LR.DIM6_CHAINS.get(b)
        out[b] = not ops or any(Counter(name(x) for x, _ in op) == Counter(name(y) for _, y in op) for op in ops)
    cache[top] = out
    return out


def _top(x):
    """Is the external particle x a top quark?"""
    return LR.is_fermion(x) and (LR.CLASS[LR._parts(x)[0]], LR.generation(x)) in LR.HEAVY


def _split(conf):
    """A configuration as (its massless external fermions with their labels, the number of L labels
    on each top quark name), the parts that the interference test compares."""
    tops = Counter()
    for x, c in conf:
        if _top(x):
            tops[x] += c == "L"
    return tuple(x for x in conf if not _top(x[0])), tuple(sorted(tops.items()))


def _reference(smt):
    """{configuration: gap} for the Standard Model trees smt, (topology, labels, power, monomials,
    configuration) each, every configuration split as _split splits it, and its gap the smallest
    power of the trees of that configuration less the Standard Model's leading power.  smt holds
    every configuration at its smallest power in each topology, since the frontier keeps the
    configurations of a topology apart, so a configuration that only a subleading tree carries is
    there with its gap."""
    low = min(t[2] for t in smt)
    out = {}
    for t in smt:
        s = _split(t[4])
        out[s] = min(out.get(s, t[2] - low), t[2] - low)
    return out


def _mismatch(conf, ref):
    """The interference test of a tree of configuration conf against the Standard Model's ref
    (_reference): None when its massless external fermions match no configuration of ref, and the
    test fails, and otherwise (gap, mt) for the configuration of ref with the same massless ones
    that leaves the fewest powers down in all: its gap, the powers of lambda by which the Standard
    Model amplitude of that configuration lies below the leading one, and the number of external top
    quarks whose chirality differs from it, each a power of m_t/E.  Of two that leave as many, the
    one with the smaller gap is kept, so that an external top quark of the other chirality is named
    as such."""
    light, tops = _split(conf)
    best = None
    for (light2, tops2), gap in ref.items():
        if light2 != light:
            continue
        have = dict(tops2)
        k = sum(abs(n - have.get(x, 0)) for x, n in tops)
        if best is None or (gap + k, gap) < (best[0] + best[1], best[0]):
            best = (gap, k)
    return best


def _units(vertex_index, catalogue):
    """(block, dim, class, number of Higgs fields, label, vertices) for every block of the series,
    and {(dim, class): [its blocks]}.  The lists are those of one model, which holds the class-11
    operators of one basis (gen/basis.py, the basis of docs/catalogue.json), and lists that hold both
    stop with a ValueError, since class 11 would then count the operators of two bases at once."""
    units, blocks, bases = [], {}, set()
    for block, verts in vertex_index.items():
        if block.startswith("L8op"):
            e = catalogue.get(block)
            if not e or e["b_violating"]:
                continue
            if e.get("basis"):
                bases.add(e["basis"])
            dim, cls, nh, label = 8, LR.CLASSES[e["cls"]], e["fields"]["N_H"], e["label"]
        elif block in LR.DIM6:
            (cls, nh), dim, label = LR.DIM6[block], 6, block
        else:
            continue
        blocks.setdefault((dim, cls), []).append(block)
        units.append((block, dim, cls, nh, label, verts))
    if len(bases) > 1:
        raise ValueError("the vertex lists hold the class-11 operators of both bases (gen/basis.py), and a model "
                         "holds those of one, so they are not the lists of a model (./dim8 series --model)")
    return units, blocks


# ------------------------------------------------------------------------------ the series ----

def _block_index():
    return json.load(open(os.path.join(ROOT, "docs", "block_index.json")))


def _best(a, b):
    """Of two (gap, mt), the one that interferes best: the fewer powers down in all, then the
    smaller gap (_mismatch)."""
    return min(a, b, key=lambda x: (x[0] + x[1], x[0]))


def _rec(d, key, power, monos, label, lab, mt, gap=0):
    """Keep the smallest power per key, and at equal power the union of the monomials, operators and
    external legs, and the powers down its interference carries, gap from the Standard Model
    amplitude of its configuration and mt from its external top quarks, from the tree that
    interferes best."""
    old = d.get(key)
    if old is None or power < old["power"]:
        d[key] = {"power": power, "monos": set(monos), "ops": {label}, "legs": {lab}, "mt": mt, "gap": gap}
    elif power == old["power"]:
        old["monos"] |= monos
        old["ops"].add(label)
        old["legs"].add(lab)
        old["gap"], old["mt"] = _best((old["gap"], old["mt"]), (gap, mt))


def series(proc, vertex_index, sm, catalogue, group=None, onshell=None, interference=True,
           block_index=None, gauge="unitary"):
    """The series of a process, as a dict: the header (process, marks, n, 2n-8, the power of the
    channel's Standard Model amplitude, gauge, grouping, whether a W or Z is unmarked and so
    counted as transverse) and the terms, the Standard Model's with dim 4 and the classes' with
    dim 6 or 8, each with its group, power, coupling monomials, operators and the external legs
    that reach it (G0, GP, GPbar where a longitudinal leg took its Goldstone boson), gap, the
    powers of lambda by which the Standard Model amplitude of its configuration lies below the
    leading one, mt, the number of powers of m_t/E its interference carries from an external top
    quark of the other chirality, and top_flip, whether there is one (Interference above).  The
    operators left out are left_out_ops, (class, operator) each, and left_out_operators counts
    those of the classes not left out as a whole.  The initial states with a square-only term are
    square_initial.  sm is the list of Standard Model vertices (process.standard_model_vertices),
    onshell the outcomes of validate/onshell_zero.py or None, and interference=False keeps every
    tree.  group="line" groups the quark-line sub-amplitudes of --vbf (group_of)."""
    slots, marks = P.parse_process(proc, collapse=LR.ROUTE_COLLAPSE, marks=True)
    n = len(slots)
    if "0" in marks and gauge != "feynman":
        raise ValueError("a longitudinal W or Z ({0}) is counted through its Goldstone boson, which needs the "
                         "Feynman-gauge vertex lists build/vertex_index_fg.json and build/sm_vertices_fg.json")
    mode = group or ("channel" if n == 4 else "none")
    if mode not in ("channel", "vbf", "line", "none"):
        raise ValueError(f"unknown grouping {mode!r}")
    if mode == "channel" and n != 4:
        raise ValueError("--group channel names the s, t and u channels of a four-point process; use vbf or none")
    if LR.qcd_zero(proc):
        sm = [v for v in sm if "G" not in v]
        ng = LR.gluon_strengths(block_index if block_index is not None else _block_index())
        vertex_index = {b: [v for v in vs if v.count("G") <= ng.get(b, 0)] for b, vs in vertex_index.items()}
    alts = LR.channel_slots(slots, marks)
    units, count = _units(vertex_index, catalogue)
    plain = interfering(False) if interference else {}
    F = Frontier(sm, chains=LR.chains(), configurations=interference)
    flav = [i for i, m in enumerate(marks) if m is None]
    pol = [i for i, m in enumerate(marks) if m is not None]
    main = {"sm": {}, "ops": {}}
    square = {"sm": {}, "ops": {}, "initial": set()}
    unevaluated, seen = set(), set()
    # the blocks with a term, and those with trees in an initial state of the Standard Model none of
    # which interferes there
    kept, failed = set(), set()
    for fl in P._product([alts[i] for i in flav]):
        choices = []
        for pc in P._product([alts[i] for i in pol]):
            lab = [None] * n
            for i, (x, _) in zip(flav, fl):
                lab[i] = x
            for i, (x, _) in zip(pol, pc):
                lab[i] = x
            choices.append((tuple(lab), sum(k for _, k in pc)))
        sig = tuple(sorted((tuple(sorted(lab)), cost, _channel_sig(lab, mode)) for lab, cost in choices))
        if sig in seen:
            continue
        seen.add(sig)
        # a state that breaks the charge, the baryon or lepton number or a generation label has no
        # tree at all (LR.conserving), and the polarised slots, W and Z bosons or their Goldstone
        # bosons, carry the same charges in every choice
        if not LR.conserving(choices[0][0]):
            continue
        # the Standard Model trees of this initial state, over the choices of the polarised slots
        smt = []
        for lab, cost in choices:
            ext = tuple(sorted(lab))
            for (k, conf), (c, m) in F.sm_all(ext).items():
                smt.append((topology(k, lab), lab, c + cost, m, conf))
        target = main if smt else square
        squared = False                    # a square-only term of this state, which then is listed
        for topo, lab, c, m, _ in smt:
            # the smallest power of each topology over the choices and the chiralities, and its
            # monomials
            g = group_of(topo, lab, mode)
            old = main["sm"].get((g, topo))
            if old is None or c < old[0]:
                main["sm"][(g, topo)] = (c, set(m), g)
            elif c == old[0]:
                old[1].update(m)
        # the interference test, against the configurations of the Standard Model trees of this
        # initial state and their gaps, and none without a Standard Model tree, whose terms are
        # square only
        test = interference and bool(smt)
        ref, tested = (_reference(smt) if test else None), {}
        # the quick test that sets an operator aside before its trees are built (interfering()),
        # with q and u as one name where a b or t quark of this state lets a top line join them: the
        # CKM matrix is block diagonal, so a top line ends on such a quark, and the polarised slots
        # hold W and Z bosons only, so fl has every fermion of the state
        third = any(LR.is_fermion(x) and LR.sector(x) == "q" and LR.generation(x) == 2 for x, _ in fl)
        can = interfering(third) if test else {}
        for block, dim, cls, nh, label, verts in units:
            if test and not can.get(block, True):
                continue
            outc = onshell.get(block, {}) if onshell is not None else {}
            found = hit = False
            for legs in verts:
                p = nh - sum(legs.count(s) for s in LR.SCALARS)
                w = dim - 12 + 2 * len(legs) + p
                key3 = " ".join(sorted(legs)) if len(legs) == 3 and sum(map(LR.is_fermion, legs)) == 2 else None
                o = outc.get(key3) if key3 else None
                for lab, cost in choices:
                    ext = tuple(sorted(lab))
                    if len(legs) > len(ext):
                        continue
                    fr = F.vertex_all(list(legs), ext, block, o)
                    if fr and key3 and onshell is not None and o in (None, "unchecked"):
                        unevaluated.add((block, key3))
                    for (k, conf), (c, m) in fr.items():
                        found = True
                        gap = mt = 0
                        if test:
                            if conf not in tested:
                                tested[conf] = _mismatch(conf, ref)
                            if tested[conf] is None:
                                continue
                            gap, mt = tested[conf]
                        hit = True
                        squared = squared or not smt
                        _rec(target["ops"], (group_of(topology(k, lab), lab, mode), dim, cls), w + c + cost, m,
                             label, lab, mt, gap)
            if hit:
                kept.add(block)
            elif found and test:
                failed.add(block)
        if squared:
            square["initial"].add(tuple(sorted(x for x, _ in fl)))
    smp = min((v[0] for v in main["sm"].values()), default=None)
    terms, square_only = _terms(main, smp), _terms(square, None)
    have = {(t["dim"], t["cls"]) for t in terms + square_only}

    def gone(b):
        # left out: no term, and the operator fails the quick test or every tree of it fails the
        # exact one where there is a Standard Model tree
        return interference and b not in kept and (not plain.get(b, True) or b in failed)
    # a class is left out when all of its operators are
    left = sorted(cls for (dim, cls), bs in count.items() if all(map(gone, bs)) and (dim, cls) not in have)
    label_of = {u[0]: u[4] for u in units}
    out_ops = sorted((cls, label_of[b]) for (dim, cls), bs in count.items() for b in bs if gone(b))
    out = {"process": proc, "marks": marks, "n": n, "two_n_minus_8": 2 * n - 8, "sm_power": smp,
           "gauge": gauge, "group": mode, "onshell": onshell is not None,
           "unmarked": any(m is None and any(x in LR.GOLDSTONE for x in s) for s, m in zip(slots, marks)),
           "terms": terms, "square_only": square_only,
           "square_initial": sorted(square["initial"]),
           "left_out": left,
           "left_out_ops": [list(x) for x in out_ops],
           "left_out_operators": sum(cls not in left for cls, _ in out_ops),
           "unevaluated": sorted(" ".join(x) for x in unevaluated)}
    out["no_tree"] = [c for c in LR.CLASSES.values() if (8, c) not in have and c not in left]
    return out


def _terms(part, smp):
    """The terms of one part of the series, sorted by group, power and dimension."""
    terms = []
    per = {}
    for topo, (c, m, g) in part["sm"].items():
        per.setdefault((g, c), set()).update(m)
    for (g, c), m in per.items():
        terms.append({"group": g, "power": c, "dim": 4, "cls": None, "couplings": sorted(map(list, m)),
                      "ops": [], "legs": [], "delta": None if smp is None else c - smp, "bold": False,
                      "gap": 0, "mt": 0, "top_flip": False})
    for (g, dim, cls), d in part["ops"].items():
        delta = None if smp is None else d["power"] - smp
        terms.append({"group": g, "power": d["power"], "dim": dim, "cls": cls,
                      "couplings": sorted(map(list, d["monos"])), "ops": sorted(d["ops"]),
                      "legs": sorted(map(list, d["legs"])), "delta": delta,
                      "bold": dim == 8 and delta is not None and delta <= 4 and not d["mt"] and not d["gap"],
                      "gap": d["gap"], "mt": d["mt"], "top_flip": d["mt"] > 0})
    terms.sort(key=lambda t: (GROUP_ORDER.index(t["group"]), t["power"], t["dim"], t["cls"] or ""))
    return terms


def load_onshell(path=ONSHELL):
    """{block: {vertex legs: outcome}} from validate/onshell_zero.py, or None without the file."""
    if not os.path.exists(path):
        return None
    return json.load(open(path))["outcomes"]


# --------------------------------------------------------------------------------- --vbf ----

def _merge(results, shift, dress, title):
    """One series from several, every power raised by shift and every monomial multiplied by the
    names dress: the effective-W cores (or quark lines) of one polarisation channel.  Each current
    of the dressing puts a quark pair in place of its boson, one more external leg and two more
    powers of lambda, so n and 2n-8 are those of the dressed process.  A class or an operator is
    left out of the merged series when it is left out of every one of the series merged, and an
    initial state with a square-only term in any of them is listed."""
    out = dict(results[0])
    out["title"] = title
    out["processes"] = [r["process"] for r in results]
    out["n"] = results[0]["n"] + shift // 2
    out["two_n_minus_8"] = results[0]["two_n_minus_8"] + shift
    smp = [r["sm_power"] for r in results if r["sm_power"] is not None]
    out["sm_power"] = min(smp) + shift if smp else None
    for part in ("terms", "square_only"):
        acc = {}
        for r in results:
            for t in r[part]:
                key = (t["group"], t["dim"], t["cls"]) if t["dim"] != 4 else (t["group"], 4, t["power"])
                p = t["power"] + shift
                monos = {tuple(sorted(list(m) + list(dress))) for m in map(tuple, t["couplings"])}
                old = acc.get(key)
                if old is None or p < old["power"]:
                    acc[key] = dict(t, power=p, couplings=monos, ops=set(t["ops"]), legs={tuple(x) for x in t["legs"]})
                elif p == old["power"]:
                    old["couplings"] |= monos
                    old["ops"] |= set(t["ops"])
                    old["legs"] |= {tuple(x) for x in t["legs"]}
                    old["gap"], old["mt"] = _best((old["gap"], old["mt"]), (t["gap"], t["mt"]))
                    old["top_flip"] = old["mt"] > 0
        terms = []
        for t in acc.values():
            delta = None if out["sm_power"] is None or part == "square_only" else t["power"] - out["sm_power"]
            terms.append(dict(t, couplings=sorted(map(list, t["couplings"])), ops=sorted(t["ops"]),
                              legs=sorted(map(list, t["legs"])), delta=delta,
                              bold=t["dim"] == 8 and delta is not None and delta <= 4 and not t["mt"] and not t["gap"]))
        terms.sort(key=lambda t: (GROUP_ORDER.index(t["group"]), t["power"], t["dim"], t["cls"] or ""))
        out[part] = terms
    out["left_out"] = sorted(set.intersection(*(set(r["left_out"]) for r in results)))
    # the operators left out of every merged series, less those of the classes left out as a whole,
    # which the line of the classes names, as series() counts them
    ops = set.intersection(*({tuple(x) for x in r["left_out_ops"]} for r in results))
    out["left_out_ops"] = [list(x) for x in sorted(ops)]
    out["left_out_operators"] = sum(cls not in out["left_out"] for cls, _ in ops)
    out["square_initial"] = sorted(set().union(*({tuple(x) for x in r["square_initial"]} for r in results)))
    out["unevaluated"] = sorted(set().union(*(r["unevaluated"] for r in results)))
    out["no_tree"] = sorted(set.intersection(*(set(r["no_tree"]) for r in results)))
    return out


def vbf(proc, vertex_index, sm, catalogue, onshell=None, interference=True, block_index=None, gauge="unitary"):
    """The series of vector-boson fusion in the effective-W approximation: the cores and the quark
    lines of every polarisation channel, each dressed with its quark currents."""
    rhs = proc.split(",")[0].split(">", 1)[1]
    orders = " ".join(re.findall(r"\b(?:qcd|qed|np)\s*[<>=]+\s*\d+", rhs, re.I))
    final = [x for x in re.sub(r"\b(?:qcd|qed|np)\s*[<>=]+\s*\d+", "", rhs, flags=re.I).split() if x != "j"]
    if not final:
        raise ValueError("--vbf needs a final state besides the jets, as in p p > h h j j")
    X = " ".join(final)
    # the longitudinal channels need the Goldstone vertices of the Feynman-gauge lists
    core_pols = [("T", "T"), ("T", "0"), ("0", "0")] if gauge == "feynman" else [("T", "T")]
    line_pols = ["T", "0"] if gauge == "feynman" else ["T"]
    name = {"T": "T", "0": "L"}
    out = []

    def run(p, mode="none"):
        return series(f"{p} {orders}".strip(), vertex_index, sm, catalogue, group=mode, onshell=onshell,
                      interference=interference, block_index=block_index, gauge=gauge)

    def line_only(r):
        # the quark line's own trees: one in which the quark pair meets a single line is a tree of a
        # core (group_of, mode line), which the cores count with both currents.  The Standard Model
        # power stays that of all the trees, the channel the line terms are measured against.
        return dict(r, terms=[t for t in r["terms"] if t["group"] == "line"],
                    square_only=[t for t in r["square_only"] if t["group"] == "line"])
    for a, b in core_pols:
        res = [run(f"w+{{{a}}} w-{{{b}}} > {X}"), run(f"z{{{a}}} z{{{b}}} > {X}")]
        m = _merge(res, 4, ("\\bar qqV", "\\bar qqV"),
                   f"core, V_{name[a]} V_{name[b]} (effective-W approximation, dressed with lambda^4 g_qqV^2)")
        for t in m["terms"] + m["square_only"]:
            t["group"] = "core"
        out.append(m)
    for a in line_pols:
        res = [line_only(run(f"p p {v}{{{a}}} > {X}", "line")) for v in ("w+", "w-", "z")]
        m = _merge(res, 2, ("\\bar qqV",),
                   f"quark line, V_{name[a]} (effective-W approximation, dressed with lambda^2 g_qqV)")
        for t in m["terms"] + m["square_only"]:
            t["group"] = "line"
        out.append(m)
    return out


# ------------------------------------------------------------------------------- printing ----

def _mono_key(name):
    """The order of coupling names in print: fermion currents first, the top, the quarks and the
    leptons in that order, then the bosonic couplings, as the paper writes g_{\\bar qqV}\\, g_{VVV}.
    A top mass insertion follows the top couplings."""
    if name.startswith("\\bar "):
        return (0, "tqe".find(name[5]), name)
    if name == MASS:
        return (0, 0, name)
    return (1, BOSON_ORDER.index(name[0]) if name[0] in "hVg" else 1, name)


def _set_key(monos):
    return sorted((len(m), [_mono_key(x) for x in m]) for m in monos)


def _mono_tex(m):
    """g_{a}^2 g_{b} for the monomial (a, a, b), the fermion pair first; '' for the empty one."""
    names = sorted(set(m), key=_mono_key)
    return r"\, ".join(factor_tex(x) + (f"^{m.count(x)}" if m.count(x) > 1 else "") for x in names)


def _monos_tex(monos):
    """A sum of monomials, in brackets when there are several, 1 for the empty one beside others."""
    ms = sorted((tuple(m) for m in monos), key=lambda m: (len(m), [_mono_key(x) for x in m]))
    if ms == [()]:
        return ""
    body = " + ".join(_mono_tex(m) or "1" for m in ms)
    return rf"\big({body}\big)" if len(ms) > 1 else body


def _divide(m, common):
    m = list(m)
    for x in common:
        m.remove(x)
    return tuple(m)


def _group_tex(terms, factor=False):
    """The terms of one group, power by power: the Standard Model first, then dimension six, then
    dimension eight, classes with the same monomials together.  With factor, the power and the
    couplings common to every term are taken out in front of a bracket, as in eq:amp-hhjj."""
    p0, common = 0, ()
    if factor and terms:
        p0 = min(t["power"] for t in terms)
        allm = [tuple(m) for t in terms for m in t["couplings"]]
        cnt = Counter(allm[0]) if allm else Counter()
        for m in allm[1:]:
            cnt &= Counter(m)
        common = tuple(sorted(cnt.elements(), key=_mono_key))
    pieces = []
    for power in sorted({t["power"] for t in terms}):
        at = [t for t in terms if t["power"] == power]
        lam = rf"\lambda^{{{power - p0}}}\, " if (power - p0) or not factor else ""
        for t in (t for t in at if t["dim"] == 4):
            pieces.append(lam + (_monos_tex({_divide(m, common) for m in map(tuple, t["couplings"])}) or "1"))
        parts = []
        for d in (6, 8):
            byset = {}
            for t in (t for t in at if t["dim"] == d):
                ms = frozenset(_divide(m, common) for m in map(tuple, t["couplings"]))
                c = rf"c_{{{latex_class(t['cls'])}}}"
                byset.setdefault(ms, []).append(rf"\boldsymbol{{{c}}}" if t["bold"] else c)
            items = []
            for ms, cs in sorted(byset.items(), key=lambda kv: _set_key(kv[0])):
                coef = cs[0] if len(cs) == 1 else "(" + " + ".join(cs) + ")"
                g = _monos_tex(ms)
                items.append(f"{g}\\, {coef}" if g else coef)
            if items:
                body = " + ".join(items)
                if len(items) > 1:
                    body = (r"\big[" + body + r"\big]") if "(" in body else (r"\big(" + body + r"\big)")
                parts.append(f"{body}/\\hat\\Lambda^{d - 4}")
        if parts:
            body = " + ".join(parts)
            if len(parts) > 1:
                body = (r"\big[" + body + r"\big]") if r"\big(" in body or "(" in body else (r"\big(" + body + r"\big)")
            pieces.append(lam + body if lam else body)
    if factor and pieces:
        pieces[0] = rf"\lambda^{{{p0}}}\, " + (_mono_tex(common) + r"\, " if common else "") + r"\Big[\, " + pieces[0]
        pieces[-1] += r" \Big]"
    return pieces


def _model_text(m):
    """The scheme and the basis of the model of a result, and whether it has a dimension-six sector."""
    label = m["input_relations"]["label"]
    return ((f"{label} scheme" if label else "no input relations") + f", {m['basis_name']} basis"
            + ("" if m["dim6"] else ", no dimension-six sector of its own and so no dimension-six term"))


def _relations_lines(r):
    """What the input relations of the model give the process, as lines of the text output."""
    m, ir = r["model"], r["model"]["input_relations"]
    if not ir["label"]:
        return [f"  {m['path']} has no input relations, so an operator enters only through its own vertices"]
    if not ir["sm_tree"]:
        return [f"  the {ir['label']} input relations shift the Standard Model amplitude, which this process does not "
                "have, so none of their operators enters"]
    if not ir["electroweak"]:
        return [f"  the {ir['label']} input relations do not enter, since every Standard Model tree of the process is "
                "built from quark and gluon vertices, whose coupling g_s is the input alpha_s"]
    by = {}
    for cls, label in ir["dim8"]:
        by.setdefault(cls, []).append(label)
    out = [f"  through the {ir['label']} input relations, which shift every Standard Model term"
           + (" and the W mass" if ir["w_mass"] else "") + " by v^4/Lambda^4, eight powers of lambda: "
           + ", ".join(f"{cls} ({', '.join(ls)})" for cls, ls in by.items())]
    if ir["dim6"]:
        out.append("  and at dimension six by v^2/Lambda^2, four powers of lambda: " + ", ".join(ir["dim6"]))
    if ir["lepton_yukawa"]:
        out.append(f"  {', '.join(ir['lepton_yukawa'])} enter G_F only with nonzero electron and muon Yukawas, which "
                   "the counting sets to zero")
    return out


def latex(results):
    """The series as an align block in the notation of eq:amp-ww, one block per result."""
    lines = []
    for r in results:
        sm = "no Standard Model tree" if r["sm_power"] is None else f"Standard Model amplitude lambda^{r['sm_power']}"
        lines.append(f"% ./dim8 series \"{r['process']}\" --model {r['model']['path']}"
                     + (f"  ({r['title']})" if r.get("title") else "")
                     + f", {sm}, {r['gauge']} gauge, {_model_text(r['model'])}"
                     + (", an unmarked W or Z counted as transverse ({T})" if r.get("unmarked") else ""))
        groups = [g for g in GROUP_ORDER if any(t["group"] == g for t in r["terms"])]
        if groups:
            lines.append(r"\begin{align}")
        for gi, g in enumerate(groups):
            pieces = _group_tex([t for t in r["terms"] if t["group"] == g], factor=(g == "core"))
            row, rows = f"{GROUP_TEX[g]} &= ", []
            for k, pc in enumerate(pieces):
                if k and len(row) + len(pc) > 110:
                    rows.append(row + r" \nonumber\\")
                    row = r" &\quad + " + pc
                else:
                    row += (" + " if k else "") + pc
            end = "." if gi == len(groups) - 1 else r", \nonumber\\"
            rows.append(row + end)
            lines += rows
        if groups:
            lines.append(r"\end{align}")
        if r["square_only"]:
            lines.append("% square only (no Standard Model tree for "
                         + ", ".join(" ".join(x) for x in r.get("square_initial", [])) + "): "
                         + ", ".join(f"lambda^{t['power']} c_{{{t['cls']}}}" for t in r["square_only"] if t["dim"] != 4))
        lines += ["% " + x.strip() for x in _relations_lines(r)]
    return "\n".join(lines)


def _growth(t):
    d = t["delta"]
    if d is None or t["dim"] == 4:
        return ""
    if t["dim"] == 8:
        return f"E^{8 - d} v^{d - 4}/Lambda^4"
    return f"E^{4 - d} v^{d - 2}/Lambda^2"


def _monos_text(monos):
    out = []
    for m in sorted(monos, key=lambda m: (len(m), [_mono_key(x) for x in m])):
        if not m:
            out.append("(contact)")
            continue
        names = sorted(set(m), key=_mono_key)
        out.append(" ".join(ascii_name(x) + (f"^{m.count(x)}" if m.count(x) > 1 else "") for x in names))
    return " + ".join(out)


def text(results, notes=()):
    lines = []
    for r in results:
        if r.get("title"):
            lines.append(r["title"] + ":  " + ",  ".join(r.get("processes", [r["process"]])))
        else:
            lines.append(f"{r['process']}: {r['n']} external legs, {r['gauge']} gauge")
        lines.append(f"  model {r['model']['path']}, {_model_text(r['model'])}")
        if r["sm_power"] is None:
            lines.append("  no Standard Model tree in this channel: every term below is square only")
        else:
            lines.append(f"  Standard Model amplitude of the channel lambda^{r['sm_power']} (2n-8 = {r['two_n_minus_8']}). "
                         "A * marks a dimension-eight term at most four powers of lambda above it, which grows at "
                         "least as E^4/Lambda^4 relative to it")
        if r.get("unmarked"):
            lines.append("  an unmarked W or Z is counted as transverse, as w+{T}, and w+{0} gives its longitudinal channel")
        for part, head in (("terms", None), ("square_only", "square only, no Standard Model tree for "
                                             + ", ".join(" ".join(x) for x in r.get("square_initial", [])))):
            if part == "square_only" and not r[part]:
                continue
            if head:
                lines.append("  " + head + " (the leading term is the square, 1/Lambda^8 at dimension eight):")
            last = None
            for t in r[part]:
                if t["group"] != last and t["group"]:
                    lines.append(f"  A_{t['group']}")
                last = t["group"]
                if t["dim"] == 4:
                    lines.append(f"    lambda^{t['power']:<3d} SM      {_monos_text(map(tuple, t['couplings']))}")
                    continue
                ops = ", ".join(t["ops"][:3]) + (f" (+{len(t['ops']) - 3} more)" if len(t["ops"]) > 3 else "")
                mt, gap = t.get("mt", int(t["top_flip"])), t.get("gap", 0)
                mtx = "m_t/E" if mt == 1 else f"(m_t/E)^{mt}"
                why = ([f"interferes {gap} power{'s' if gap > 1 else ''} down"] if gap else []) \
                    + ([f"external top, carries {mtx}"] if mt else [])
                mark = "*" if t["bold"] else (f" ({', '.join(why)})" if why else "")
                lines.append(f"    lambda^{t['power']:<3d} dim {t['dim']}  {t['cls'] + mark:14s} "
                             f"{_monos_text(map(tuple, t['couplings'])):34s} {_growth(t):20s} {ops}")
        if r["left_out"]:
            lines.append("  left out, no interference at leading order in the light fermion masses: "
                         + ", ".join(r["left_out"]))
        if r.get("left_out_operators"):
            lines.append(f"  and {r['left_out_operators']} operators of the classes above, for the same reason")
        if r["no_tree"]:
            # the input relations of the model enter this process, or none of them does
            lines.append("  dimension-eight classes with no tree ("
                         + ("input relations only, or not reached" if r["model"]["input_relations"]["dim8"] else "not reached")
                         + "): " + ", ".join(r["no_tree"]))
        lines += _relations_lines(r)
        if r["unevaluated"]:
            lines.append("  three-point vertices of two fermions with no outcome in build/onshell_zero.json, or "
                         "unchecked there, counted as they are: "
                         + ", ".join(r["unevaluated"][:8]) + (" ..." if len(r["unevaluated"]) > 8 else ""))
        lines.append("")
    lines += list(notes)
    return "\n".join(lines)


# ------------------------------------------------------------------------------------ CLI ----

def add_arguments(p):
    p.add_argument("process", help='MadGraph syntax, with {0} or {T} on a W or Z, e.g. "u u~ > w+{0} w-{0}"')
    p.add_argument("--json", action="store_true", help="every term with its couplings, operators and external legs")
    p.add_argument("--latex", action="store_true", help="an align block in the notation of the paper (eq:amp-ww)")
    p.add_argument("--group", choices=("channel", "vbf", "none"), default=None,
                   help="channel: c, s, t, u (the default at four legs); vbf: core and quark line; none: one series")
    p.add_argument("--vbf", action="store_true",
                   help="vector-boson fusion in the effective-W approximation: the cores V{p} V{p} > X and the "
                        "quark lines q qbar' V{p} > X of every polarisation channel")
    p.add_argument("--gauge", choices=("feynman", "unitary"), default=None,
                   help="the vertex lists: feynman (the default when build/vertex_index_fg.json exists) or unitary")
    p.add_argument("--model", default="models/dim68_mw", metavar="DIR",
                   help="the released UFO whose vertices, basis and input scheme the series counts, read as "
                        "./dim8 select reads it, a path or a name in models/ (default models/dim68_mw, the "
                        "{MW, MZ, GF} scheme with the dimension-six sector, in the default basis)")


def run(a, read_model):
    """./dim8 series.  read_model(model, gauge, process) is the reader of ./dim8 (_series_model there),
    which reads the model as ./dim8 select reads it and gives its vertex lists, checked against it, its
    basis, its scheme and what its input relations give the process."""
    gauge = a.gauge or ("feynman" if os.path.exists(FG_INDEX) else "unitary")
    notes = []
    try:
        _, marks = P.parse_process(a.process, marks=True)
    except P.ProcessError as e:
        sys.exit(f"{a.process}: {e}")
    if gauge != "feynman" and "0" in marks:
        if a.gauge == "unitary":
            sys.exit(f"{a.process}: a longitudinal W or Z ({{0}}) is counted through its Goldstone boson, which the "
                     "unitary-gauge lists do not have. Leave out --gauge unitary, or mark the boson {T} for the "
                     "transverse count.")
        sys.exit(f"{a.process}: a longitudinal W or Z ({{0}}) is counted through its Goldstone boson, which needs the "
                 "Feynman-gauge vertex lists build/vertex_index_fg.json and build/sm_vertices_fg.json, which are not "
                 "in this tree. Mark the boson {T} for the transverse count.")
    if gauge == "unitary" and a.gauge is None:
        notes.append("note: the Feynman-gauge vertex lists, build/vertex_index_fg.json and build/sm_vertices_fg.json, "
                     "are not in this tree, so the "
                     "unitary ones are used. An internal W or Z between two bosonic vertices then misses the Goldstone "
                     "exchange that carries the k^mu k^nu/M^2 part of its propagator. A line that ends on a light "
                     "quark or lepton is exact.")
    if a.vbf and gauge != "feynman":
        notes.append("note: --vbf without the Feynman-gauge lists gives the transverse channels only.")
    try:
        # the vertex lists of the model, which stops the command where they do not fit it
        m = read_model(a.model, gauge, a.process)
        vi = m.pop("vertices")
        sm = P.standard_model_vertices(m.pop("base"), goldstones=(gauge == "feynman"))
    except (ValueError, FileNotFoundError) as e:   # Feynman-gauge lists asked for and missing or incomplete
        sys.exit(f"{a.process}: {e}")
    cat = {e["block"]: e for e in json.load(open(os.path.join(ROOT, "docs", "catalogue.json")))}
    ir = m["input_relations"]
    ir["dim8"] = [[LR.CLASSES[cat[b]["cls"]], cat[b]["label"]]
                  for b in sorted(ir["dim8"], key=lambda b: (cat[b]["cls"], int(b[4:])))]
    ir["lepton_yukawa"] = [cat[b]["label"] for b in ir["lepton_yukawa"]]
    onshell = load_onshell()
    if onshell is None:
        notes.append("note: build/onshell_zero.json is missing (python3 validate/onshell_zero.py), so a three-point "
                     "vertex of two fermions is counted even where it vanishes on shell.")
    kw = dict(onshell=onshell, gauge=gauge)
    try:
        results = (vbf(a.process, vi, sm, cat, **kw) if a.vbf
                   else [series(a.process, vi, sm, cat, group=a.group, **kw)])
    except ValueError as e:                    # a grouping, mark or QCD order the series cannot count
        sys.exit(f"{a.process}: {e}")
    for r in results:
        r["model"] = m
    if a.json:
        print(json.dumps({"results": results, "notes": notes}, indent=1))
    elif a.latex:
        print(latex(results))
        for x in notes:
            print("% " + x)
    else:
        print(text(results, notes))
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(prog="lambda_series.py", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    add_arguments(ap)
    a = ap.parse_args(argv)
    # the model is read by ./dim8, as ./dim8 select reads it, so that this and ./dim8 series are one command
    import importlib.machinery
    import importlib.util
    loader = importlib.machinery.SourceFileLoader("dim8_cli", os.path.join(ROOT, "dim8"))
    cli = importlib.util.module_from_spec(importlib.util.spec_from_loader("dim8_cli", loader))
    loader.exec_module(cli)
    return run(a, cli._series_model)


if __name__ == "__main__":
    sys.exit(main())
