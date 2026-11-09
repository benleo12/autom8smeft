"""
gen/process.py  --  "give me a process, get the dimension-eight operators that can
contribute to it".

This is the selector behind ``./dim8 select``.  A user writes a MadGraph process string and
gets back the subset of the basis that can appear in a tree diagram for that process.
``./dim8 select --card`` writes it as a restriction card for a released model, and
``./dim8 model`` and ``./dim8 ufo`` write it as a small FeynRules model or UFO.  The vertex
index also holds the dimension-six classes, which are selected the same way, and select_dim6
selects the dimension-six coefficients one by one, from the vertices of each coefficient in
``build/dim6_index.json`` (validate/dim6_index.py), with those that enter at 1/Lambda^4 only
together with a second dimension-six insertion.  The point is that nobody should have to
import every vertex of 674 operators to study one final state.

How the selection is decided
----------------------------
Not by field content, which is too crude (a four-quark operator contains only quarks but
cannot produce a lepton pair), and not by hand.  A dimension-eight operator contributes
to a process at tree level, at one insertion, exactly when one of its vertices can sit in
a tree whose external legs are the process.  Cutting that vertex out of the tree leaves
one subtree per leg, each containing at least one external.  So:

    contributes(op) iff  there is a vertex V of op, and a partition of the externals into
                         |V| non-empty groups, such that each leg of V connects to its
                         group through a tree of *Standard Model* vertices.

``reach(f, G)`` answers the inner question and is memoised.  Both vertex lists come from
FeynRules itself (``build/sm_vertices.json`` and ``build/vertex_index.json``, written by
validate/dump_vertex_index.wls), so the selection is decided by the same Feynman rules
that the generator will use, not by a hand-maintained table of which operator matters
where.  That is what makes it safe to trust: the criterion is necessary and sufficient at
tree level, so an operator is never silently dropped.

Internal lines are the whole point, and the search is not truncated.  There is no depth
limit on how many Standard Model vertices may sit between the dimension-eight vertex and
the external state, and none is needed: every SM vertex has at least three legs, so
removing the leg that carries the incoming propagator always leaves at least two, and the
group of externals is split among them into strictly smaller non-empty parts.  The
recursion therefore terminates on its own, after at most ``len(G)`` nested vertices,
which is the standard bound for a tree whose internal nodes all have degree three or
more.  An arbitrary cutoff would silently drop long decay chains.

Vev insertions need no special handling.  FeynRules already produces the reduced vertices
that a Higgs leg replaced by its vacuum expectation value produces, as separate lower
point entries in the same list.

Conventions
-----------
FeynRules writes a vertex as the list of particles with **all momenta incoming**, so the
selector uses the same convention throughout: an incoming particle of the process enters
as itself, an outgoing particle enters as its antiparticle.  Getting this backwards is
silent, because for a symmetric initial state such as ``p p`` the selected set happens to
come out the same, and it only bites on a charged final state.  Field labels are
FeynRules names, so ``W`` is the W+, ``Wbar`` the W-, and a bar suffix marks an
antiparticle unless the field is self-conjugate.  A line joining two vertices carries
conjugate labels at its two ends, which is what ``reach`` uses.
"""

from __future__ import annotations

import functools
import itertools
import json
import os
import re
from collections import Counter
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence, Set, Tuple

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# --------------------------------------------------------------------------------------
# particle names
# --------------------------------------------------------------------------------------

SELF_CONJUGATE = {"A", "Z", "G", "H", "B", "Wi", "G0"}

# FeynRules class names expand to their members; a vertex list may carry either, depending
# on whether the generation index survived ExpandIndices
CLASS_MEMBERS = {
    "l": ["e", "mu", "ta"],
    "vl": ["ve", "vm", "vt"],
    "uq": ["u", "c", "t"],
    "dq": ["d", "s", "b"],
}

# MadGraph names -> FeynRules names
MG_TO_FR = {
    "g": "G", "a": "A", "z": "Z", "h": "H",
    "w+": "W", "w-": "Wbar",
    "e-": "e", "e+": "ebar", "mu-": "mu", "mu+": "mubar", "ta-": "ta", "ta+": "tabar",
    "ve": "ve", "ve~": "vebar", "vm": "vm", "vm~": "vmbar", "vt": "vt", "vt~": "vtbar",
    "u": "u", "u~": "ubar", "c": "c", "c~": "cbar", "t": "t", "t~": "tbar",
    "d": "d", "d~": "dbar", "s": "s", "s~": "sbar", "b": "b", "b~": "bbar",
}

# MadGraph multiparticle labels.  Flavour is collapsed to one representative per gauge
# multiplet: u and c carry the same Wilson coefficients and quantum numbers, and the Yukawa
# couplings in which the released models differ between them are both counted as zero
# (only the top's is not), so keeping both only multiplies the search by a constant.
# Set collapse=False to expand them all.
MULTI = {
    "p": ["g", "u", "u~", "d", "d~", "c", "c~", "s", "s~", "b", "b~"],
    "j": ["g", "u", "u~", "d", "d~", "c", "c~", "s", "s~", "b", "b~"],
    "l+": ["e+", "mu+"],
    "l-": ["e-", "mu-"],
    "vl": ["ve", "vm"],
    "vl~": ["ve~", "vm~"],
    "l": ["e-", "mu-", "e+", "mu+"],
}
COLLAPSE = {"c": "u", "c~": "u~", "s": "d", "s~": "d~", "b": "d", "b~": "d~",
            "mu+": "e+", "mu-": "e-", "vm": "ve", "vm~": "ve~"}

# MadGraph's polarisation marks on a massive vector boson, w+{0} longitudinal and w+{T} transverse.
# MadGraph's {L} and {R} are the helicities -1 and +1, which the energy counting does not tell apart
# from {T}.  They are refused rather than read as transverse, since L also reads as longitudinal.
POLARISABLE = {"w+", "w-", "z"}
POL_MARKS = {"0": "0", "t": "T"}
# the Goldstone bosons of the Feynman-gauge base (tests/gen_smoke/base_fg.fr), FeynRules labels
GOLDSTONES = {"G0", "GP", "GPbar"}


def anti(f: str) -> str:
    if f in SELF_CONJUGATE:
        return f
    return f[:-3] if f.endswith("bar") else f + "bar"


def _members(f: str) -> List[str]:
    """A class label stands for any of its members; a member stands for itself."""
    base, bar = (f[:-3], "bar") if f.endswith("bar") and f[:-3] in CLASS_MEMBERS else (f, "")
    if base in CLASS_MEMBERS:
        return [m + bar for m in CLASS_MEMBERS[base]]
    return [f]


def _same_field(a: str, b: str) -> bool:
    """Do two labels denote the same particle, allowing one to be a class label?"""
    return a == b or bool(set(_members(a)) & set(_members(b)))


# --------------------------------------------------------------------------------------
# process strings
# --------------------------------------------------------------------------------------


class ProcessError(ValueError):
    pass


def parse_process(proc: str, collapse=True, marks: bool = False):
    """A MadGraph process string to a list of external slots, each a list of the FeynRules
    particles that slot may be, in the all-incoming convention that FeynRules vertex lists
    use: initial-state particles as themselves, final-state particles conjugated.

    collapse is True for the flavour collapse COLLAPSE, False for none, or another mapping of
    MadGraph names to apply instead (gen/lambda_routes.py keeps the b quark apart).

    Decay chains written with commas are flattened: the decaying particle disappears from
    the final state and its decay products join it, which is the right thing here because
    a decay chain is one tree and the dimension-eight vertex may sit anywhere in it.

    MadGraph's polarisation marks on a W or a Z, w+{0} (longitudinal) and w+{T} (transverse), are
    taken off the particle names.  With marks=True the marks are returned as well, as
    (slots, marks), one mark per slot ("0", "T" or None), and gen/lambda_routes.py and
    gen/lambda_series.py count the two polarisations separately.  A mark on any other particle or
    on a decayed particle is refused.
    """
    proc = proc.strip().lower()
    proc = re.sub(r"\b(qcd|qed|np)\s*[<>=]+\s*\d+", "", proc)  # drop coupling orders
    proc = re.sub(r"\s+\{", "{", proc)                         # w+ {0} as w+{0}
    stages = [s.strip() for s in proc.split(",") if s.strip()]
    if not stages:
        raise ProcessError("empty process")

    incoming: List[str] = []
    outgoing: List[str] = []
    decayed: List[str] = []
    for k, st in enumerate(stages):
        if ">" not in st:
            raise ProcessError(f"no '>' in {st!r}")
        lhs, rhs = st.split(">", 1)
        left = lhs.split()
        right = rhs.split()
        if k == 0:
            incoming = left
        else:
            if len(left) != 1:
                raise ProcessError(f"a decay stage needs exactly one parent: {st!r}")
            if _mark(left[0])[1] is not None:
                raise ProcessError(f"a polarisation mark on a decaying particle is not counted: {st!r}")
            decayed.append(left[0])
        outgoing += right

    # a decayed parent is internal, not external, and its polarisation is not an external one
    for d in decayed:
        bare = [_mark(x)[0] for x in outgoing]
        if d in bare:
            if _mark(outgoing[bare.index(d)])[1] is not None:
                raise ProcessError(f"{outgoing[bare.index(d)]} decays, so its polarisation mark is not "
                                   "that of an external particle. Mark only a W or Z that does not decay")
            outgoing.pop(bare.index(d))

    slots: List[List[str]] = []
    pols: List[Optional[str]] = []
    for p in incoming:
        name, mark = _mark(p)
        slots.append(_expand(name, collapse))
        pols.append(mark)
    for p in outgoing:
        name, mark = _mark(p)
        slots.append([anti(x) for x in _expand(name, collapse)])
        pols.append(mark)
    if len(slots) < 2:
        raise ProcessError("need at least two external particles")
    return (slots, pols) if marks else slots


def _mark(tok: str) -> Tuple[str, Optional[str]]:
    """(particle, polarisation mark) of a token: ("w+", "0") for w+{0}, ("w+", "T") for w+{T},
    (tok, None) without a mark."""
    m = re.fullmatch(r"(.+?)\{([^{}]*)\}", tok)
    if not m:
        if "{" in tok or "}" in tok:
            raise ProcessError(f"cannot read the polarisation mark of {tok!r}")
        return tok, None
    name, mark = m.group(1), m.group(2).strip()
    if name not in POLARISABLE:
        raise ProcessError(f"a polarisation mark on {name!r}: only w+, w- and z carry one here")
    if mark not in POL_MARKS:
        raise ProcessError(f"polarisation {{{mark}}} on {name}: use {{0}} (longitudinal) or {{T}} (transverse). "
                           "MadGraph's {L} and {R} are the helicities -1 and +1, which the counting does not "
                           "tell apart from {T}")
    return name, POL_MARKS[mark]


def _expand(tok: str, collapse) -> List[str]:
    names = MULTI.get(tok, [tok])
    if collapse:
        cmap = COLLAPSE if collapse is True else collapse
        names = list(dict.fromkeys(cmap.get(n, n) for n in names))
    out = []
    for n in names:
        if n not in MG_TO_FR:
            raise ProcessError(f"unknown particle {n!r}")
        out.append(MG_TO_FR[n])
    return list(dict.fromkeys(out))


# --------------------------------------------------------------------------------------
# can a vertex sit in a tree diagram of the process
# --------------------------------------------------------------------------------------


class Selector:
    """Decides which cached dimension-eight blocks can contribute to a process."""

    def __init__(self, sm_vertices: Sequence[Sequence[str]]):
        # Two-point entries are mass mixings, absorbed into propagators.  They cannot
        # change which operators contribute, and keeping them would break the
        # strictly-shrinking argument that lets the search run without a depth cutoff.
        # Ghosts never appear on a tree-level internal line (a ghost line must close into
        # a loop), so their vertices are dropped from the internal-line set as well.
        def usable(v):
            return len(v) >= 3 and not any(f.startswith("gh") for f in v)

        self.sm = [tuple(sorted(v)) for v in sm_vertices if usable(v)]
        self.dropped = [tuple(sorted(v)) for v in sm_vertices if not usable(v)]
        # index the SM vertices by each field they contain, so reach() does not rescan.
        # Index by BOTH the class name and its generation members.  The dimension-eight
        # vertex index names fermion legs by class (uq, uqbar, dq, l, ...), and _reach looks
        # the SM vertices up under anti(leg), so the class name must be a key.  Indexed by
        # members alone, every fermion-class lookup would be empty, and no diagram in which a
        # dimension-eight fermion leg continues as an internal line into an SM vertex would be
        # found (for example the u ubar -> Z h diagram of Q_{quH^5} in p p > z h, through an
        # SM ubar u Z vertex).  Boson legs need no such care because their class name is
        # their member name.
        self.by_field: Dict[str, List[Tuple[str, ...]]] = {}
        for v in self.sm:
            for f in set(v):
                for m in set(_members(f)) | {f}:
                    self.by_field.setdefault(m, []).append(v)
        self._reach_cache: Dict[Tuple[str, Tuple[str, ...]], bool] = {}
        # _reach_through's answers, one table for each set of second vertices pair_fits is given
        self._through_memo: Dict[Tuple[Tuple[str, ...], ...], Dict[Tuple[str, Tuple[str, ...]], bool]] = {}

    def _candidates(self, f: str):
        """SM vertices that contain field f, whether f is a class name or a member."""
        seen, out = set(), []
        for key in set(_members(f)) | {f}:
            for v in self.by_field.get(key, ()):
                if v not in seen:
                    seen.add(v)
                    out.append(v)
        return out

    # -- can leg field f connect to exactly the externals in group, via SM vertices? ----
    def reach(self, f: str, group: Tuple[str, ...]) -> bool:
        """No depth argument: the recursion is bounded by ``len(group)`` on its own,
        because every SM vertex leaves at least two legs once the incoming propagator is
        removed, so the group is split into strictly smaller non-empty parts."""
        key = (f, group)
        hit = self._reach_cache.get(key)
        if hit is not None:
            return hit
        self._reach_cache[key] = False   # cycle guard, overwritten below
        res = self._reach(f, group)
        self._reach_cache[key] = res
        return res

    def _reach(self, f: str, group: Tuple[str, ...]) -> bool:
        if len(group) == 1 and _same_field(f, group[0]):
            return True          # the leg is that external itself
        # otherwise the leg is a propagator into an SM vertex carrying anti(f)
        af = anti(f)
        for v in self._candidates(af):       # candidate SM vertices containing anti(f)
            rest = list(v)
            for i, x in enumerate(rest):     # remove one leg matching anti(f)
                if _same_field(x, af):
                    rest.pop(i)
                    break
            else:
                continue
            if len(rest) < 2 or len(rest) > len(group):
                continue
            for parts in _partitions(group, len(rest)):
                if all(self.reach(rest[i], parts[i]) for i in range(len(rest))):
                    return True
        return False

    # -- does a whole vertex fit the process? -------------------------------------------
    def vertex_fits(self, legs: Sequence[str], externals: Tuple[str, ...]) -> bool:
        n = len(legs)
        if n > len(externals):
            return False
        for parts in _partitions(externals, n):
            if all(self.reach(legs[i], parts[i]) for i in range(n)):
                return True
        return False

    def block_fits(self, vertices: Iterable[Sequence[str]], externals: Tuple[str, ...]) -> Optional[List[str]]:
        for legs in vertices:
            if self.vertex_fits(list(legs), externals):
                return list(legs)
        return None

    # -- two dimension-eight insertions -------------------------------------------------
    # A diagram with two dimension-eight vertices is order 1/Lambda^8, so it is NOT part
    # of a consistent 1/Lambda^4 analysis and is off by default.  It is what you want for
    # a dimension-eight-squared term used as a 1/Lambda^8 proxy, and for positivity or
    # unitarity arguments where the squared amplitude is the object of interest.
    #
    # The criterion generalises the one-insertion one.  Cut out the first dim-8 vertex V:
    # every leg but one goes to a pure Standard Model subtree of externals, and the
    # remaining leg goes to a subtree that contains the second dim-8 vertex exactly once.
    # ``_reach_through`` answers that inner question, and it is the same recursion as
    # ``reach`` with one extra case: the propagator may land directly on the second dim-8
    # vertex instead of on an SM vertex.  It is asked for all the candidate second vertices at
    # once, since any one of them will do, and memoised like ``reach``: without that, a leg that
    # can never close (a gluon among leptons and photons) made every call exhaust every split of
    # the group again, once per candidate, a search that grows exponentially with the number of
    # external particles.
    def _reach_through(self, f: str, group: Tuple[str, ...], v2s: Tuple[Tuple[str, ...], ...],
                       memo: Dict[Tuple[str, Tuple[str, ...]], bool]) -> bool:
        """f connects to exactly ``group`` through a tree containing one of the vertices ``v2s``, once.
        memo holds the answers for this set of second vertices.  The answer depends on f, the group and
        that set alone, the Standard Model vertices being fixed, and the recursion strictly shrinks the
        group, so it needs no cycle guard."""
        key = (f, group)
        hit = memo.get(key)
        if hit is None:
            hit = memo[key] = self._through(f, group, v2s, memo)
        return hit

    def _through(self, f: str, group: Tuple[str, ...], v2s: Tuple[Tuple[str, ...], ...],
                 memo: Dict[Tuple[str, Tuple[str, ...]], bool]) -> bool:
        af = anti(f)
        # (a) the propagator lands on a second vertex itself
        for v2 in v2s:
            for i, x in enumerate(v2):
                if _same_field(x, af):
                    rest = list(v2)
                    rest.pop(i)
                    if 1 <= len(rest) <= len(group):
                        for parts in _partitions(group, len(rest)):
                            if all(self.reach(rest[j], parts[j]) for j in range(len(rest))):
                                return True
                    break
        # (b) the propagator lands on an SM vertex, and exactly one of its other legs carries the
        # second vertex.  The other legs are tested first, with the memoised reach, and the leg that
        # carries it is searched only where they all close.
        for v in self._candidates(af):
            rest = list(v)
            for i, x in enumerate(rest):
                if _same_field(x, af):
                    rest.pop(i)
                    break
            else:
                continue
            if len(rest) < 2 or len(rest) > len(group):
                continue
            for parts in _partitions(group, len(rest)):
                for k in range(len(rest)):
                    if (all(self.reach(rest[j], parts[j]) for j in range(len(rest)) if j != k)
                            and self._reach_through(rest[k], parts[k], v2s, memo)):
                        return True
        return False

    def pair_fits(self, legs: Sequence[str], externals: Tuple[str, ...],
                  all_dim8: Sequence[Tuple[str, ...]], groups: bool = True) -> bool:
        """Can this vertex sit in a tree for ``externals`` alongside one other dim-8 vertex?

        The legs other than the one that carries the second vertex each reach a group of externals
        through Standard Model vertices, any proper subset of the externals in all, which is the whole
        criterion, and select() and select_dim6 both ask for it.  groups=False leaves those legs on
        external particles themselves, one each, which is the same search up to four external particles
        and with five or more does not look for a tree in which one of them reaches several.  It stays
        for the test that shows that difference."""
        n = len(legs)
        # The second vertices as the key of their table of answers, built only once the other legs of
        # some split close.  Building and hashing the key is a pass over every second vertex, over a
        # thousand field contents of the vertex index in select()'s second pass, most of whose calls
        # never get that far.
        v2s = memo = None
        for a in range(n):                      # the leg that carries the second insertion
            others = [legs[i] for i in range(n) if i != a]
            # the other legs take a proper subset of the externals, the rest goes through leg a: one
            # external each (groups=False), or a group each (groups=True)
            for k in (range(len(others), len(externals)) if groups else range(len(others) + 1)):
                if k > len(externals) - 1:
                    break
                for sub in _subsets(externals, k):
                    if len(sub) < len(others):
                        continue
                    remainder = _multiset_diff(externals, sub)
                    if not remainder:
                        continue
                    ok_here = (not others) or any(
                        all(self.reach(others[j], parts[j]) for j in range(len(others)))
                        for parts in _partitions(sub, len(others)))
                    if not ok_here:
                        continue
                    if memo is None:
                        v2s = tuple(tuple(v) for v in all_dim8)
                        memo = self._through_memo.setdefault(v2s, {})
                    if self._reach_through(legs[a], remainder, v2s, memo):
                        return True
        return False



@functools.lru_cache(maxsize=None)
def _subsets(items: Tuple[str, ...], k: int) -> Tuple[Tuple[str, ...], ...]:
    """Distinct k-element sub-multisets of ``items``."""
    return tuple(sorted({tuple(sorted(c)) for c in itertools.combinations(items, k)}))


def _multiset_diff(a: Tuple[str, ...], b: Tuple[str, ...]) -> Tuple[str, ...]:
    rest = list(a)
    for x in b:
        if x in rest:
            rest.remove(x)
    return tuple(sorted(rest))


@functools.lru_cache(maxsize=None)
def _partitions(items: Tuple[str, ...], n: int) -> Tuple[Tuple[Tuple[str, ...], ...], ...]:
    """All ways to split ``items`` into ``n`` non-empty labelled groups.  Cached, and
    deduplicated on the group contents so repeated particles do not multiply the work."""
    if n <= 0 or len(items) < n:
        return ()
    out: Set[Tuple[Tuple[str, ...], ...]] = set()

    def rec(i: int, groups: List[List[str]]):
        if i == len(items):
            if all(groups):
                out.add(tuple(tuple(sorted(g)) for g in groups))
            return
        for k in range(n):
            groups[k].append(items[i])
            rec(i + 1, groups)
            groups[k].pop()

    rec(0, [[] for _ in range(n)])
    return tuple(sorted(out))


# --------------------------------------------------------------------------------------
# top level
# --------------------------------------------------------------------------------------


# The Standard Model's own vertices in unitary gauge, by field content.  The base vertex list,
# build/sm_vertices.json, holds the whole dimension-six sector of the base the index was dumped
# from as well (load_data): h-gamma-gamma, g g h, four-fermion contacts, five-gluon vertices and
# the like.  A diagram with one dimension-eight vertex and one of those is order 1/Lambda^6, so the
# internal lines of a dimension-eight block are restricted to this set, which is checked against
# FeynRules' list at load time (every entry must be in it).  So are those of a dimension-six block:
# a second dimension-six vertex makes its tree 1/Lambda^4, which enters only through the
# interference with the Standard Model, and select_dim6 asks for exactly one such vertex, of the
# same coefficient or another, coefficient by coefficient, where the Standard Model has a tree.  On
# the processes of the paper the restriction changes no dimension-eight selection.
_SM_BOSONIC = ["A W Wbar", "W Wbar Z", "G G G", "H H H", "H W Wbar", "H Z Z",
               "A A W Wbar", "A W Wbar Z", "W W Wbar Wbar", "W Wbar Z Z", "G G G G", "H H H H",
               "H H W Wbar", "H H Z Z"]
_SM_CURRENTS = [("uq", "AZGH"), ("dq", "AZGH"), ("l", "AZH"), ("vl", "Z")]
_SM_CHARGED = ["uqbar dq W", "dqbar uq Wbar", "vlbar l W", "lbar vl Wbar"]
# The Standard Model's vertices with a Goldstone boson, in Feynman gauge, which gen/lambda_series.py
# uses for a longitudinal W or Z and for the Goldstone exchange that carries the k^mu k^nu/M^2 part
# of a unitary-gauge propagator.  From the kinetic term of the doublet come the derivative couplings
# of two scalars to a gauge boson, the couplings of a Goldstone boson to two gauge bosons through
# the vev and the seagulls with two gauge bosons.  From the potential come the couplings of three
# scalars through the vev and the quartics, and from the Yukawa terms the couplings to a fermion pair.
# Of these only the ones of the up-type quarks are listed, which reach the top quark
# (gen/lambda_routes.py keeps them on a top line).  Those of the down-type quarks and the leptons are
# proportional to light masses and are left out, as their Higgs couplings are left out of the routes.
# The charged entries GP dq uqbar and GPbar dqbar uq hold the b quark's coupling as well, tbar_L b_R G+ beside the top's
# tbar_R b_L G+, and the routes tell the two apart by chirality (lambda_routes.sm_options).  Ghosts
# never sit on a tree-level line.  Checked against FeynRules' list of the Feynman-gauge base at load time
# (build/sm_vertices_fg.json, made in Feynman gauge with Mathematica and FeynRules), and in both
# directions, FeynRules' Goldstone vertices less the ghosts and the light Yukawa couplings against
# this list, by a test of the development tree.
_SM_GOLDSTONE = ["A GP GPbar", "GP GPbar Z", "G0 GPbar W", "G0 GP Wbar", "G0 H Z", "GPbar H W", "GP H Wbar",
                 "A GPbar W", "A GP Wbar", "GPbar W Z", "GP Wbar Z",
                 "GP GPbar H", "G0 G0 H",
                 "G0 uq uqbar", "GP dq uqbar", "GPbar dqbar uq",
                 "GP GPbar W Wbar", "G0 G0 W Wbar", "GP GPbar Z Z", "G0 G0 Z Z", "A GP GPbar Z", "A A GP GPbar",
                 "G0 GPbar W Z", "G0 GP Wbar Z", "A G0 GPbar W", "A G0 GP Wbar",
                 "GPbar H W Z", "GP H Wbar Z", "A GPbar H W", "A GP H Wbar",
                 "GP GPbar H H", "G0 G0 H H", "GP GP GPbar GPbar", "G0 G0 GP GPbar", "G0 G0 G0 G0"]


def sm_vertex_set(goldstones: bool = False) -> Set[Tuple[str, ...]]:
    """The Standard Model's vertices of the lists above, as sorted field contents, with those of
    the Goldstone bosons when goldstones is True.  Not checked against FeynRules' list, which
    standard_model_vertices does."""
    sm = {tuple(sorted(v.split())) for v in _SM_BOSONIC + _SM_CHARGED + (_SM_GOLDSTONE if goldstones else [])}
    for f, bosons in _SM_CURRENTS:
        for b in bosons:
            sm.add(tuple(sorted([f + "bar", f, b])))
    return sm


def standard_model_vertices(base_vertices: Sequence[Sequence[str]], goldstones: bool = False) -> List[List[str]]:
    """The subset of the base model's vertex contents that the Standard Model has.  With
    goldstones=True the vertices of the Goldstone bosons are added, and the base list must be that
    of a Feynman-gauge base (load_data with gauge="feynman")."""
    sm = sm_vertex_set(goldstones)
    have = {tuple(sorted(v)) for v in base_vertices}
    missing = [" ".join(v) for v in sorted(sm) if v not in have]
    if missing:
        raise ValueError("Standard Model vertices absent from the base vertex list: " + ", ".join(missing)
                         + ("  (the Goldstone vertices need the Feynman-gauge list, build/sm_vertices_fg.json)"
                            if goldstones else ""))
    return [list(v) for v in sorted(sm)]


def select(proc: str, vertex_index: Dict[str, List[List[str]]], sm_vertices: Sequence[Sequence[str]],
           collapse: bool = True, two_insertions: bool = False, second: Optional[Set[str]] = None) -> Dict[str, List[str]]:
    """Block name -> the vertex that lets it contribute, for every block that can.  With
    two_insertions, a set passed as second receives the blocks that only the second pass finds,
    which have no tree with one insertion.

    The internal lines are the Standard Model's vertices (standard_model_vertices) for the blocks of
    both dimensions.  The base list holds the dimension-six vertices as well (load_data).  They are
    not internal lines here, since a dimension-six class would then be listed that only two or more
    dimension-six insertions bring into the process, with a reason that the route search, which
    counts Standard Model lines only, could not give.  Which dimension-six coefficients enter only
    with a second dimension-six insertion is select_dim6's question."""
    slots = parse_process(proc, collapse=collapse)
    sel = Selector(standard_model_vertices(sm_vertices))          # blocks of both dimensions
    # every concrete assignment of the multiparticle slots, deduplicated as multisets, and sorted so
    # that the vertex reported for a block does not depend on the interpreter's string hashing
    assignments = sorted({tuple(sorted(a)) for a in _product(slots)})
    hits: Dict[str, List[str]] = {}
    for block, verts in vertex_index.items():
        for ext in assignments:
            got = sel.block_fits(verts, ext)
            if got is not None:
                hits[block] = got
                break
    if not two_insertions:
        return hits
    # Second pass: operators that can only appear alongside a second dimension-eight
    # vertex.  Order 1/Lambda^8, so this is opt in, and Selector.pair_fits holds the criterion.  The
    # answer depends on the field content of the vertex and on the external particles alone, since
    # pair_fits tries every leg in every place, and the operators share most of their field contents,
    # so each pair of the two is asked once.
    all_dim8 = tuple(sorted({tuple(sorted(v)) for vs in vertex_index.values() for v in vs}))
    asked: Dict[Tuple[Tuple[str, ...], Tuple[str, ...]], bool] = {}
    for block, verts in vertex_index.items():
        if block in hits:
            continue
        for ext in assignments:
            for legs in verts:
                key = (tuple(sorted(legs)), ext)
                fits = asked.get(key)
                if fits is None:
                    fits = asked[key] = sel.pair_fits(list(legs), ext, all_dim8)
                if fits:
                    hits[block] = list(legs)
                    break
            if block in hits:
                if second is not None:
                    second.add(block)
                break
    return hits


def select_dim6(proc: str, coeff_index: Dict[str, Dict[str, List[List[str]]]], sm_vertices: Sequence[Sequence[str]],
                collapse: bool = True) -> Dict[str, Dict[str, object]]:
    """The dimension-six coefficients that enter the process at 1/Lambda^4, one by one: coefficient ->
    {"legs": the vertex that brings it in, "kind": "one" or "second"}.

    coeff_index is one model's entry of build/dim6_index.json (validate/dim6_index.py): coefficient ->
    {"one": the field contents of the vertices of order NP=1 that it moves, the Standard Model vertices
    that it rescales through the normalisation of a field included, "two": the field contents of the
    couplings of order NP=2 that multiply it by a second coefficient or by itself, those under "one"
    left out}.  A coefficient is of kind "one" when one of its NP=1 vertices fits a tree of the process
    whose other vertices are the Standard Model's, the criterion of select().  Its amplitude is then
    1/Lambda^2, and it enters at 1/Lambda^4 through the square of the dimension-six amplitude whether
    or not the Standard Model has a tree.  It is of kind "second" when it has no such tree but an
    amplitude of order 1/Lambda^4: an NP=2 vertex of its own that fits with Standard Model lines, or an
    NP=1 vertex that fits together with exactly one more NP=1 vertex, of the same coefficient or of
    another (Selector.pair_fits, with which select() finds a second dimension-eight insertion).
    Such an amplitude enters at 1/Lambda^4 only through its interference with the Standard Model, and
    amplitudes interfere only for one and the same external state, so a coefficient is of this kind
    only through an assignment of the external particles that has a Standard Model tree (the test of
    sm_tree, one assignment at a time), and in a process without one (sm_tree) no coefficient is.  The
    coefficients, the assignments and the vertices are taken in sorted order, so that the vertex
    reported does not depend on the interpreter's string hashing."""
    slots = parse_process(proc, collapse=collapse)
    sel = Selector(standard_model_vertices(sm_vertices))
    assignments = sorted({tuple(sorted(a)) for a in _product(slots)})
    out: Dict[str, Dict[str, object]] = {}
    for c in sorted(coeff_index):
        verts = sorted(coeff_index[c].get("one", []))
        for ext in assignments:
            got = sel.block_fits(verts, ext)
            if got is not None:
                out[c] = {"legs": got, "kind": "one"}
                break
    # the assignments with a Standard Model tree, by sm_tree's recursion: the first external particle
    # enters a Standard Model vertex whose other legs reach the rest
    with_sm = [ext for ext in assignments if sel.reach(anti(ext[0]), ext[1:])]
    if not with_sm:
        return out
    # the NP=1 vertices of every coefficient, any one of which may be the second insertion
    np1 = tuple(sorted({tuple(sorted(v)) for e in coeff_index.values() for v in e.get("one", [])}))
    for c in sorted(coeff_index):
        if c in out:
            continue
        two = sorted(coeff_index[c].get("two", []))
        for ext in with_sm:
            got = sel.block_fits(two, ext)
            if got is not None:
                out[c] = {"legs": got, "kind": "second"}
                break
        if c in out:
            continue
        for ext in with_sm:
            for legs in sorted(coeff_index[c].get("one", [])):
                if sel.pair_fits(list(legs), ext, np1):
                    out[c] = {"legs": list(legs), "kind": "second"}
                    break
            if c in out:
                break
    return dict(sorted(out.items()))


def sm_tree(proc: str, sm_vertices: Sequence[Sequence[str]], collapse: bool = True) -> bool:
    """Whether the Standard Model alone has a tree diagram for the process.

    Without one there is no amplitude for a dimension-eight one to interfere with: the
    interference vanishes at 1/Lambda^4 and the leading term is the square.  An operator that acts
    only through the input relations then changes nothing, since what it shifts is the
    Standard-Model amplitude.  The test is the selector's own recursion: the first external leg
    enters a Standard-Model vertex, whose other legs reach the remaining externals."""
    sel = Selector(standard_model_vertices(sm_vertices))
    for ext in {tuple(sorted(a)) for a in _product(parse_process(proc, collapse=collapse))}:
        if sel.reach(anti(ext[0]), ext[1:]):
            return True
    return False


# the fields of a vertex that carries g_s alone
QCD_FIELDS = {"G", "uq", "uqbar", "dq", "dqbar"}


def sm_electroweak(proc: str, sm_vertices: Sequence[Sequence[str]], collapse: bool = True) -> bool:
    """Whether some Standard-Model tree diagram of the process has an electroweak vertex.

    The input relations shift g_2, g_1, the vev, the neutral rotation and, in the {alpha, MZ, GF}
    scheme, the W mass, so they reach every vertex with a W, Z, photon or Higgs leg.  They reach no
    vertex of quarks and gluons alone, whose one coupling g_s = sqrt(4 pi alpha_s) is itself an
    input.  A process whose tree diagrams are all built from those (g g > g g, u u~ > g g,
    g g > t t~) is therefore untouched by them, while u u~ > d d~ is not, since a photon or a Z can
    join its two quark lines.  The test asks, for each electroweak vertex of the Standard Model,
    whether a tree diagram of the process contains it, with the selector's own criterion."""
    sm = standard_model_vertices(sm_vertices)
    sel = Selector(sm)
    ew = [v for v in sm if not set(v) <= QCD_FIELDS]
    for ext in sorted({tuple(sorted(a)) for a in _product(parse_process(proc, collapse=collapse))}):
        if any(sel.vertex_fits(v, ext) for v in ew):
            return True
    return False


def _product(slots: List[List[str]]):
    if not slots:
        yield ()
        return
    for head in slots[0]:
        for rest in _product(slots[1:]):
            yield (head,) + rest


def load_data(root: str = ROOT, with_dim6: bool = False, gauge: str = "unitary"):
    """The vertex index and the base model's vertices, from which select() takes the
    internal lines.

    The base vertex list, build/sm_vertices.json, carries the whole dimension-six sector of the
    base the index was dumped from as well: the vertices of the dimension-six operators in the
    base Lagrangian, those of the input scheme, and, since validate/dump_vertex_index.wls joins
    them whenever the index holds dimension-six blocks, every vertex of the dimension-six classes
    (g g h, four-fermion contacts, five-gluon vertices and the like, most of its field
    contents).  A diagram with one dimension-eight vertex and one dimension-six vertex is order
    1/Lambda^6, and one with two dimension-six vertices enters 1/Lambda^4 only through its
    interference with the Standard Model, so select() and select_dim6() take the internal lines
    of every block from the Standard Model subset (standard_model_vertices), and select_dim6()
    asks for a second dimension-six vertex itself, coefficient by coefficient.  with_dim6=True
    appends build/d6_vertices.json to the base list where that file exists, which matters only to
    a caller that builds its own Selector from the list.

    gauge="feynman" gives the Feynman-gauge lists instead, which gen/lambda_series.py counts
    longitudinal W and Z bosons with: build/vertex_index_fg.json and build/sm_vertices_fg.json,
    made in Feynman gauge with Mathematica and FeynRules, which ship in build/ with the release.  A
    block then has its vertices without a Goldstone boson from the unitary list, which
    validate/index_vs_ufo.py has checked against the released models and cleared of the vertices
    whose couplings cancel, and its vertices with a Goldstone boson from the Feynman-gauge list.
    The two lists agree on the vertices without one apart from the entries that check removed, which
    a test of the development tree checks.
    """
    if gauge not in ("unitary", "feynman"):
        raise ValueError(f"gauge is 'unitary' or 'feynman', not {gauge!r}")
    vi = os.path.join(root, "build", "vertex_index.json")
    sm = os.path.join(root, "build", "sm_vertices.json")
    for p in (vi, sm):
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"{p} is missing.  Run  wolframscript -file validate/dump_vertex_index.wls  "
                "after the vertex cache has been built by validate/fr_worker.wls.")
    internal = json.load(open(sm))
    if with_dim6:
        d6 = os.path.join(root, "build", "d6_vertices.json")
        if os.path.exists(d6):
            internal = internal + json.load(open(d6))
    index = json.load(open(vi))
    if gauge == "unitary":
        return index, internal
    vfg = os.path.join(root, "build", "vertex_index_fg.json")
    sfg = os.path.join(root, "build", "sm_vertices_fg.json")
    for p in (vfg, sfg):
        if not os.path.exists(p):
            raise FileNotFoundError(
                f"{os.path.relpath(p, root)} is missing.  The Feynman-gauge vertex lists, "
                "build/vertex_index_fg.json and build/sm_vertices_fg.json, are not in this tree.  They are "
                "made in Feynman gauge with Mathematica and FeynRules.")
    fg = json.load(open(vfg))
    lack = [b for b in index if (b.startswith("L6cl") or (b.startswith("L8op") and int(b[4:]) < 675)) and b not in fg]
    if lack:
        lack.sort(key=lambda b: (b[:4], int(b[4:]) if b[4:].isdigit() else 0, b))
        raise ValueError(f"build/vertex_index_fg.json lacks {len(lack)} entries of build/vertex_index.json "
                         f"({', '.join(lack[:6])}{', ...' if len(lack) > 6 else ''}), so the Feynman-gauge lists "
                         "in this tree are incomplete")
    merged = {}
    for b in sorted(set(index) | set(fg)):
        merged[b] = ([v for v in index.get(b, []) if not GOLDSTONES & set(v)]
                     + [v for v in fg.get(b, []) if GOLDSTONES & set(v)])
    return merged, json.load(open(sfg))
