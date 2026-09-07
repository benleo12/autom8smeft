"""
gen/process.py  --  "give me a process, get the dimension-eight operators that can
contribute to it".

This is the front end of the public model.  A user writes a MadGraph process string and
gets back the subset of the basis that can appear in a tree diagram for that process,
which is then emitted as a small FeynRules model and a small UFO.  The point is that
nobody should have to import a 1220-coupling model to study one final state.

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
more.  An arbitrary cutoff would have silently dropped long decay chains.

Vev insertions need no special handling.  FeynRules already emits the reduced vertices
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
# multiplet: in the flavour-universal model u and c carry identical Wilson coefficients
# and identical quantum numbers, so keeping both only multiplies the search by a constant.
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
# process parsing
# --------------------------------------------------------------------------------------


class ProcessError(ValueError):
    pass


def parse_process(proc: str, collapse: bool = True) -> List[List[str]]:
    """A MadGraph process string to a list of external slots, each a list of the FeynRules
    particles that slot may be, in the all-incoming convention that FeynRules vertex lists
    use: initial-state particles as themselves, final-state particles conjugated.

    Decay chains written with commas are flattened: the decaying particle disappears from
    the final state and its decay products join it, which is the right thing here because
    a decay chain is one tree and the dimension-eight vertex may sit anywhere in it.
    """
    proc = proc.strip().lower()
    proc = re.sub(r"\b(qcd|qed|np)\s*[<>=]+\s*\d+", "", proc)  # drop coupling orders
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
            decayed.append(left[0])
        outgoing += right

    # a decayed parent is internal, not external
    for d in decayed:
        if d in outgoing:
            outgoing.remove(d)

    slots: List[List[str]] = []
    for p in incoming:
        slots.append(_expand(p, collapse))
    for p in outgoing:
        slots.append([anti(x) for x in _expand(p, collapse)])
    if len(slots) < 2:
        raise ProcessError("need at least two external particles")
    return slots


def _expand(tok: str, collapse: bool) -> List[str]:
    names = MULTI.get(tok, [tok])
    if collapse:
        names = list(dict.fromkeys(COLLAPSE.get(n, n) for n in names))
    out = []
    for n in names:
        if n not in MG_TO_FR:
            raise ProcessError(f"unknown particle {n!r}")
        out.append(MG_TO_FR[n])
    return list(dict.fromkeys(out))


# --------------------------------------------------------------------------------------
# tree reachability
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
        # index the SM vertices by each field they contain, so reach() does not rescan
        # Index by BOTH the class name and its generation members.  The dimension-eight
        # vertex index names fermion legs by class (uq, uqbar, dq, l, ...), and _reach looks
        # the SM vertices up under anti(leg), so the class name must be a key: indexing by
        # members alone left every fermion-class lookup empty, and any diagram in which a
        # dimension-eight fermion leg continued as an internal line into an SM vertex was
        # silently never found (caught on Q_{quH^5} for p p > z h, whose u ubar -> Z h
        # diagram through an SM ubar u Z vertex is a perfectly good tree).  Boson legs were
        # unaffected only because their class name is their member name.
        self.by_field: Dict[str, List[Tuple[str, ...]]] = {}
        for v in self.sm:
            for f in set(v):
                for m in set(_members(f)) | {f}:
                    self.by_field.setdefault(m, []).append(v)
        self._reach_cache: Dict[Tuple[str, Tuple[str, ...]], bool] = {}

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
    # ``reach_via_dim8`` answers that inner question, and it is the same recursion as
    # ``reach`` with one extra case: the propagator may land directly on the second dim-8
    # vertex instead of on an SM vertex.
    def _reach_through(self, f: str, group: Tuple[str, ...], v2: Tuple[str, ...]) -> bool:
        """f connects to exactly ``group`` through a tree containing dim-8 vertex ``v2`` once."""
        af = anti(f)
        # (a) the propagator lands on v2 itself
        for i, x in enumerate(v2):
            if _same_field(x, af):
                rest = list(v2)
                rest.pop(i)
                if 1 <= len(rest) <= len(group):
                    for parts in _partitions(group, len(rest)):
                        if all(self.reach(rest[j], parts[j]) for j in range(len(rest))):
                            return True
                break
        # (b) the propagator lands on an SM vertex; exactly one of its other legs carries v2
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
                    if not self._reach_through(rest[k], parts[k], v2):
                        continue
                    if all(self.reach(rest[j], parts[j]) for j in range(len(rest)) if j != k):
                        return True
        return False

    def pair_fits(self, legs: Sequence[str], externals: Tuple[str, ...],
                  all_dim8: Sequence[Tuple[str, ...]]) -> bool:
        """Can this vertex sit in a tree for ``externals`` alongside one other dim-8 vertex?"""
        n = len(legs)
        for a in range(n):                      # the leg that carries the second insertion
            others = [legs[i] for i in range(n) if i != a]
            # the other legs take a proper subset of the externals, the rest goes through leg a
            for k in range(len(others) + 1):
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
                    for v2 in all_dim8:
                        if self._reach_through(legs[a], remainder, v2):
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


def select(proc: str, vertex_index: Dict[str, List[List[str]]], sm_vertices: Sequence[Sequence[str]],
           collapse: bool = True, two_insertions: bool = False) -> Dict[str, List[str]]:
    """Block name -> the vertex that lets it contribute, for every block that can."""
    slots = parse_process(proc, collapse=collapse)
    sel = Selector(sm_vertices)
    # every concrete assignment of the multiparticle slots, deduplicated as multisets
    assignments = {tuple(sorted(a)) for a in _product(slots)}
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
    # vertex.  Order 1/Lambda^8, so this is opt in; see Selector.pair_fits.
    all_dim8 = tuple(sorted({tuple(sorted(v)) for vs in vertex_index.values() for v in vs}))
    for block, verts in vertex_index.items():
        if block in hits:
            continue
        for ext in assignments:
            for legs in verts:
                if sel.pair_fits(list(legs), ext, all_dim8):
                    hits[block] = list(legs)
                    break
            if block in hits:
                break
    return hits


def _product(slots: List[List[str]]):
    if not slots:
        yield ()
        return
    for head in slots[0]:
        for rest in _product(slots[1:]):
            yield (head,) + rest


def load_data(root: str = ROOT, with_dim6: bool = False):
    """The dimension-eight vertex index and the vertices allowed on internal lines.

    Internal lines are Standard Model only.  A diagram with one dimension-eight vertex
    and one dimension-six vertex is order 1/Lambda^6, so including the dimension-six
    vertices here would select operators that cannot contribute at 1/Lambda^4.  Pass
    with_dim6=True only when selecting for the dimension-six squared piece.
    """
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
    return json.load(open(vi)), internal
