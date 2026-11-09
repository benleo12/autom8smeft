#!/usr/bin/env python3
"""The selector's vertex list against the vertices of the released models.

    python3 validate/index_vs_ufo.py [--models DIR] [--index FILE] [--write]
    python3 validate/index_vs_ufo.py --linear MODEL_A MODEL_B

./dim8 select decides which operators reach a process from build/vertex_index.json, the field
content of every vertex FeynRules derives for each operator block.  This compares that list with
the released models: for each block and field content, does each model have a vertex of that
content whose coupling depends on the block's coefficient?  The dimension-eight blocks are checked
against every model in models/ (dim8_plain and the four released ones), the dimension-six classes
against models/dim68_is (the four-fermion class at the level of the class, since the list splits it
into four blocks).  models/dim68_mw carries the same classes, and validate/dim6_vs_smeftsim.py
compares its dimension-six vertices with those of SMEFTsim's {M_W, M_Z, G_F} model one by one.

Four outcomes.
  missing       a model has a vertex the list lacks.  The selector would drop an operator that
                contributes.  Error.
  inconsistent  the list has a vertex that some models have and others lack.  One build has lost a
                vertex: a dimension-eight operator's vertices do not depend on the input scheme or
                the dimension-six sector.  Error.
  absent        the list has a vertex that every model lacks.  FeynRules wrote a vertex whose
                coupling vanishes identically, through a parameter relation such as
                cw g1SM = sw gwSM = e, a symmetry, or charge conservation, and the selector would
                list an operator through a vertex that does not exist.
  absorbed      some models lack a vertex of an input-relation coefficient (INPUT_SCHEME_WCS of
                ./dim8), because their input scheme absorbs it.  Every input-scheme model puts the
                vacuum piece of (H^dag H)^2 G G into the normalisation of the gluon and so has no
                three-gluon vertex of Q_{G^2H^4}^{(1)}, and the {M_W, M_Z, G_F} models, dim8_mw and
                dim68_mw, where G_F and M_W fix the W-lepton coupling, have no W-lepton vertex of
                Q_{l^2H^4D}^{(2,4)}.  Expected, not an error.
--write removes the absent entries from build/vertex_index.json, and the absorbed ones that only
dim8_plain has, so that the list follows the input-scheme models, and writes every absorbed vertex
with the models that carry it to build/vertex_index_absorbed.json, from which ./dim8 select gives
each released model its own vertices.  It refuses to while there is an error.  The exit status is
1 when there is an error.  --index reads and writes another file in place of build/vertex_index.json,
as ./dim8 rebuild does with the lists it has just written, which replace the ones ./dim8 select reads
only when this has passed.

Whether a model has a vertex is decided from the linear response of its couplings.  Each
coefficient is switched on alone, along 1 and along i, and the response is the derivative at zero,
from symmetric differences at +-1e-3 and +-5e-4 combined so that the quadratic and the cubic terms
the input-scheme series carry beyond 1/Lambda^4 cancel.  Every internal parameter the coefficient enters is recomputed, so that a
coefficient reaching a coupling through the gluon normalisation or a shift of g2 is followed.  A vertex content is live in a coefficient when the change, summed over all the
vertex objects of that content per canonical (Lorentz, colour) structure, exceeds 1e-8 of the
triangle-inequality bound on it: the same expressions with every subtraction turned into an
addition and every factor into its modulus.  Two vertex objects whose couplings cancel therefore
count as no vertex.  A relation that cancels identically leaves about 1e-16 of the bound, a genuine
dependence at least 1e-2 of it.  A model has a vertex that the list should carry when the vertex is
live and the coefficient appears in one of its couplings by name, as FeynRules writes an operator's
own vertices, so that the shifts the input scheme spreads over the SM vertices do not count as an
operator's own.  A coefficient counts for its block whether it is the operator's own or that of a
further flavour structure (the flavour entries of docs/block_index.json), since a structure can give
a vertex the operator's own coefficient does not: Q_{q^4B}^{(4)} vanishes with two flavour-diagonal
currents and lives with Y_u Y_u^dag on one of them.  The responses are taken at the card's inputs,
except that an input the card sets to zero, the mass of a light quark or lepton or the Cabibbo
angle, takes a value of its own (validate/generic_inputs.py): the card is massless there, and a
vertex proportional to a light Yukawa coupling is a vertex of the model all the same.  The models
are read as text and evaluated with cmath, so no MadGraph is needed.

--linear compares two models coupling by coupling instead of vertex by vertex.  For every vertex
(by field content) and every dimension-eight coefficient, switched on alone to 1 and to i, it takes
the change of each coupling entry, and the two models must agree on the signed sum of those changes
and on their sorted moduli, to 1e-6 of the largest.  An operator's own vertices do not depend on
the input scheme or on the dimension-six sector at linear order, so dim8_plain, dim8_is and
dim68_is must agree on every coefficient except those of the input relations (the
INPUT_SCHEME_WCS of ./dim8 and their flavour structures), whose vertices carry the compensating terms of the scheme.  Those are
listed separately, by vertex, since two models in the same scheme must agree on them too.  This
catches a vertex that exists in both models but has lost a coupling, or carries a different one,
which the vertex lists alone cannot see.  The exit status is 1 on any other difference.  Two
models may write one structure with its dummy indices named differently term by term, or split one
coupling over such copies, so the entries are also compared per canonical structure, measured
against the entries themselves; and a response below 1e-9 of the coefficient's largest response in
the model is round-off of the finite differences (a 1e-19 remnant in one model against the exact
zero the release step left in the other), counted and not compared.  A 1 per cent change planted on
one coupling is reported (2026-10-25).
"""
import ast
import cmath
import collections
import itertools
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import basis  # noqa: E402
import dsl  # noqa: E402
from generic_inputs import generic_value  # noqa: E402
from check_legs import DIM6  # noqa: E402  the dimension-six coefficients by class
from lambda_routes import DIM6 as DIM6_BLOCKS  # noqa: E402  L6cl block -> class

DIM6_NAMES = {w for ws in DIM6.values() for w in ws.split()}
# dim8_plain is the raw model kept for vertex comparisons and is not in models/ of the public tree, so the
# models compared are the ones present: the models of the default basis and, where they are present, those of
# the Murphy basis (gen/basis.py), which carry the suffix _murphy.  A block is compared with the models of its
# basis, and an operator common to the two bases with all of them.
DIM8_MODELS = [m + s for s in ("", "_murphy") for m in ["dim8_is", "dim8_plain", "dim8_mw", "dim68_is", "dim68_mw"]
               if os.path.isfile(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "models", m + s, "parameters.py"))]
IS_MODELS = [m for m in DIM8_MODELS if not m.startswith("dim8_plain")]
PLAIN_MODEL = "dim8_plain"


def model_basis(m):
    return "murphy" if m.endswith("_murphy") else "geo"


def models_of(wcs, models):
    """The models among `models` in which a block with the coefficients wcs belongs."""
    b = basis.of_wcs(wcs)
    return [m for m in models if b is None or model_basis(m) == b]
DIM6_MODEL = "dim68_is"
TOL = 1e-8
# The response to a coefficient is its derivative at zero, from symmetric differences at +-EPS and
# +-EPS/2: the input-scheme series carry terms beyond 1/Lambda^4 (a dimension-six coefficient cubed,
# a dimension-eight one squared), and a change taken at c = 1 counts them as a vertex, for instance
# on the photon's charge coupling in the {alpha, M_Z, G_F} models, which moves only as c^3 there.
EPS = 1e-3
# the directions of a pair of coefficients along which read_model takes a mixed second derivative,
# each coefficient along 1 or along i, which together see a coefficient that enters complex conjugated
DIRS2 = ((1.0, 1.0), (1.0, 1j), (1j, 1.0), (1j, 1j))

# UFO particle names -> the selector's labels: FeynRules class names, with bar for the antiparticle
LABEL = {"a": "A", "Z": "Z", "H": "H", "g": "G", "W+": "W", "W-": "Wbar",
         "G0": "G0", "G+": "GP", "G-": "GPbar"}    # the Goldstone bosons only with read_model(goldstones=True)
for _cls, _members in (("uq", "u c t"), ("dq", "d s b"), ("l", "e- mu- ta-"), ("vl", "ve vm vt")):
    for _m in _members.split():
        LABEL[_m] = _cls
        LABEL[_m[:-1] + "+" if _m.endswith("-") else _m + "~"] = _cls + "bar"


class _Bound(ast.NodeTransformer):
    """expr -> the triangle-inequality bound on it: subtractions become additions, every name,
    number and function value its modulus, a complex conjugate its argument's bound.  A power keeps
    its exponent, which is a number in a UFO."""

    @staticmethod
    def _abs(node):
        return ast.Call(func=ast.Name(id="abs", ctx=ast.Load()), args=[node], keywords=[])

    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Pow):
            return ast.BinOp(left=self.visit(node.left), op=ast.Pow(), right=node.right)
        if isinstance(node.op, (ast.Add, ast.Sub)):
            # a long coupling is a sum thousands of terms deep along its left spine: walk the spine
            # without recursion, and rebuild the bound as a balanced sum so that it compiles shallow
            terms, n = [], node
            while isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub)):
                terms.append(n.right)
                n = n.left
            terms = [self.visit(t) for t in [n] + terms[::-1]]
            while len(terms) > 1:
                terms = [ast.BinOp(left=terms[i], op=ast.Add(), right=terms[i + 1]) if i + 1 < len(terms)
                         else terms[i] for i in range(0, len(terms), 2)]
            return terms[0]
        node.left, node.right = self.visit(node.left), self.visit(node.right)
        return node

    def visit_UnaryOp(self, node):
        return self.visit(node.operand) if isinstance(node.op, (ast.USub, ast.UAdd)) else self._abs(node)

    def visit_Call(self, node):
        if isinstance(node.func, ast.Name) and node.func.id == "complexconjugate":
            return self.visit(node.args[0])
        return self._abs(node)

    def visit_Name(self, node):
        return self._abs(node)

    def visit_Constant(self, node):
        return self._abs(node)

    def visit_Attribute(self, node):
        return self._abs(node)


def _compile(expr, bound=False):
    tree = ast.parse(expr, mode="eval")
    if bound:
        tree = ast.fix_missing_locations(_Bound().visit(tree))
    return compile(tree, "<coupling>", "eval")


def read_model(model, inputs=None, only=None, coeffs=None, goldstones=False, pairs=None, generic=False):
    """Read a UFO as text and evaluate it with cmath.  `inputs` overrides external parameters by
    name, `generic` gives an input that is zero on the card, a light mass or cabi, a value of its
    own (validate/generic_inputs.py), so that what exists is decided away from the massless limit,
    `only` restricts the coefficients probed to those names, and `coeffs` names the
    coefficients of a model written with other conventions, whose names neither start with c8 nor
    are SMEFTsim's (validate/dim6_vs_smeftsim.py and validate/vs_matchete_ufo.py use them).  The
    vertices with a Goldstone boson are skipped, as the selector's unitary-gauge list has none,
    unless goldstones is True (validate/onshell_zero.py on a Feynman-gauge model).  `pairs`, a set
    of couplings, asks for the second derivatives of those couplings as well (pair_dep and live2
    below).  A dict with
      own     {sorted labels: coefficients that appear by name in a coupling of a vertex of that
               content and move it}, the operator's own vertices as FeynRules writes them
      live    {sorted labels: coefficients whose linear response, summed over every vertex of that
               content per canonical (Lorentz, colour) structure, does not vanish}
      lin     {(sorted labels, coefficient, 1 or 1j): [(structure, colour, change) per entry]}
      dep     {coupling: the coefficients that appear in it by name and move it}, from which own is
               gathered, for a reader that needs the couplings apart (validate/dim6_index.py keeps
               those of interaction order NP=1)
      moved   {coupling: the coefficients that move it, by name or through an internal parameter},
               the same test without the name, which validate/dim6_index.py reads for a coefficient
               that moves Standard Model vertices through the normalisation of a field, as C_HBox
               moves every vertex with one Higgs boson through that of the Higgs field
      pair_dep {coupling named in pairs: the pairs (n1, n2) of coefficients, n1 <= n2 and a
               coefficient paired with itself included, whose mixed second derivative at zero moves it}
      live2   {sorted labels: the pairs whose mixed second derivative, summed over every vertex of
               that content per canonical (Lorentz, colour) structure, does not vanish}, over the
               couplings named in pairs
      failed  [couplings that could not be evaluated]
      entries [(UFO particle names, PDG codes, [(colour, Lorentz structure, coupling)]) per vertex]
      resp    {(coupling, coefficient, 1 or 1j): its derivative at zero}
      value   {coupling: its value with every coefficient at zero}
    A coefficient that enters a coupling through an internal parameter, as the input-scheme
    coefficients do through the gluon normalisation d8fG or the shift of g2, is followed: those
    parameters are recomputed with the coefficient on.  Two vertices whose couplings cancel, one
    carrying the coefficient by name and one through such a parameter, are then not live.

    The second derivatives are meant for couplings that vanish with every coefficient at zero and are
    products of two of them, as the couplings of interaction order NP=2 of a dimension-six sector are
    (a linear vertex times an input shift or a field normalisation).  Such a coupling has no first
    derivative at zero, and its mixed second derivatives say which coefficients it multiplies.  For
    each pair of the coefficients that reach the coupling, by name or through internal parameters,
    the two are set together to (+-e v1, +-e v2), every internal parameter that either enters being
    recomputed, with v1 and v2 along 1 or along i, so that a coefficient that enters complex
    conjugated is seen too, and the second differences at e = EPS and EPS/2 are combined so that the
    quartic term cancels.  The pair moves the coupling when the largest of them exceeds 1e-8 of the
    largest value of the coupling's triangle-inequality bound at the points evaluated, over EPS^2,
    and the same bound, summed over the vertex objects of a content, measures whether the summed
    response survives there, as for the first derivatives."""
    rd = lambda f: open(os.path.join(model, f + ".py")).read()  # noqa: E731
    ns = {"cmath": cmath, "complex": complex, "pi": cmath.pi}
    for m in re.finditer(r"(\w+) = Function\(\s*name = '\w+',\s*arguments = \(([^)]*)\),\s*expression = '([^']*)'",
                         rd("function_library")):
        args = ",".join(a.strip().strip("'\"") for a in m.group(2).split(",") if a.strip())
        ns[m.group(1)] = eval(f"lambda {args}: {m.group(3)}", dict(ns))
    params = re.findall(r"(\w+) = Parameter\(\s*name = '\w+',\s*nature = '(\w+)',\s*type = '\w+',\s*"
                        r"value = ('[^']*'|[^,]+),(.*?)\)\n", rd("parameters"), re.S)
    coef = set()
    for name, nature, value, rest in params:
        # by name: the parameter block DIM6 also holds the dimension-six scale Lam6
        if coeffs is not None:
            if name in coeffs:
                coef.add(name)
        elif name.startswith("c8") or re.sub(r"(Abs|Ph|Re|Im)$", "", name) in DIM6_NAMES:
            coef.add(name)
    todo = []
    for name, nature, value, rest in params:
        if nature == "external":
            ns[name] = 0.0 if name in coef else complex(generic_value(name, eval(value)) if generic else eval(value))
            if inputs and name in inputs:
                ns[name] = complex(inputs[name])
        else:
            todo.append((name, value.strip("'")))
    order = []                               # the internal parameters in an order that evaluates
    for _ in range(len(todo) + 1):
        left = []
        for name, value in todo:
            try:
                ns[name] = eval(value, ns)
                order.append((name, value))
            except (NameError, ZeroDivisionError, ValueError, TypeError):
                left.append((name, value))
        if not left or len(left) == len(todo):
            break
        todo = left
    # complex coefficients appear in couplings by their internal name (Re + i Im) or their parts
    if coeffs is None:
        coef |= {n for n, nat, v, r in params if nat == "internal" and
                 (n.startswith("c8") or re.sub(r"(Abs|Ph|Re|Im)$", "", n) in DIM6_NAMES)}
    word = re.compile(r"\b[A-Za-z_]\w*\b")
    # the coefficients each internal parameter depends on, through other internal parameters, and
    # for each coefficient the parameters to recompute, in evaluation order (a coefficient is a
    # leaf, the internal combination of a complex one's parts included)
    pdeps, chain = {}, collections.defaultdict(list)
    for name, value in order:
        if name in coef:
            continue
        d = set()
        for x in set(word.findall(value)):
            d |= {x} if x in coef else pdeps.get(x, set())
        pdeps[name] = d
        for n in d:
            chain[n].append((name, compile(value, name, "eval")))
    shifted = {}

    def setting(n, v):
        """The internal parameters that move with coefficient n alone set to v, at their new values."""
        if (n, v) not in shifted:
            keep, k0 = {p: ns[p] for p, _ in chain[n]}, ns[n]
            ns[n] = v
            for p, c in chain[n]:
                ns[p] = eval(c, ns)
            shifted[(n, v)] = {p: ns[p] for p, _ in chain[n]}
            ns.update(keep)
            ns[n] = k0
        return shifted[(n, v)]

    pos = {p: i for i, (p, _) in enumerate(order)}
    shifted2 = {}

    def setting2(n1, x1, n2, x2):
        """The internal parameters that move with coefficients n1 and n2 set to x1 and x2 together, at
        their new values, recomputed in evaluation order.  A coefficient paired with itself (n1 == n2)
        is set to x1 + x2."""
        if (n1, x1, n2, x2) not in shifted2:
            todo = sorted(dict(chain[n1] + chain[n2]).items(), key=lambda pc: pos[pc[0]])
            keep, k1, k2 = {p: ns[p] for p, _ in todo}, ns[n1], ns[n2]
            if n1 == n2:
                ns[n1] = x1 + x2
            else:
                ns[n1], ns[n2] = x1, x2
            for p, c in todo:
                ns[p] = eval(c, ns)
            shifted2[(n1, x1, n2, x2)] = {p: ns[p] for p, _ in todo}
            ns.update(keep)
            ns[n1], ns[n2] = k1, k2
        return shifted2[(n1, x1, n2, x2)]

    dep, failed, resp, scale, reach, value = {}, [], {}, {}, {}, {}
    moved, pair_dep, plist, resp2, scale2 = {}, {}, {}, {}, {}
    for g, expr in re.findall(r"(GC_\w+) = Coupling\(\s*name = '\w+',\s*value = '([^']*)'", rd("couplings")):
        try:
            value[g] = complex(eval(expr, ns))
        except Exception:
            value[g] = complex("nan")
        names = set(word.findall(expr))
        lit = names & coef
        allc = lit.union(*(pdeps[x] for x in names if x in pdeps))
        if only is not None:
            lit, allc = lit & only, allc & only
        reach[g] = allc
        if not allc:
            dep[g] = moved[g] = set()
            continue
        if pairs is not None and g in pairs:
            plist[g] = list(itertools.combinations_with_replacement(sorted(allc), 2))
        hit, moves = set(), set()
        try:
            code, bcode = _compile(expr), _compile(expr, bound=True)
            b0 = eval(bcode, ns)
            for n in allc:
                for v in (1.0, 1j):
                    val = {}
                    for s in (EPS, -EPS, EPS / 2, -EPS / 2):
                        over = setting(n, s * v)
                        keep, k0 = {p: ns[p] for p in over}, ns[n]
                        ns.update(over)
                        ns[n] = s * v
                        val[s] = eval(code, ns)
                        if v == 1.0 and s == EPS:
                            scale[(g, n)] = max(eval(bcode, ns) - b0, 0.0) / EPS
                        ns.update(keep)
                        ns[n] = k0
                    # symmetric differences at EPS and EPS/2, combined so that the cubic term cancels
                    d1 = (val[EPS] - val[-EPS]) / (2 * EPS)
                    d2 = (val[EPS / 2] - val[-EPS / 2]) / EPS
                    resp[(g, n, v)] = (4 * d2 - d1) / 3
                change = max(abs(resp[(g, n, 1.0)]), abs(resp[(g, n, 1j)]))
                if scale[(g, n)] > 0 and change > TOL * scale[(g, n)]:
                    moves.add(n)
                    if n in lit:
                        hit.add(n)
            for n1, n2 in plist.get(g, ()):
                big, sc = 0.0, 0.0
                for v1, v2 in DIRS2:
                    d = {}
                    for e in (EPS, EPS / 2):
                        acc = 0j
                        for s1, s2 in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
                            x1, x2 = s1 * e * v1, s2 * e * v2
                            over = setting2(n1, x1, n2, x2)
                            keep, k1, k2 = {p: ns[p] for p in over}, ns[n1], ns[n2]
                            ns.update(over)
                            if n1 == n2:
                                ns[n1] = x1 + x2
                            else:
                                ns[n1], ns[n2] = x1, x2
                            acc += s1 * s2 * eval(code, ns)
                            if e == EPS:
                                sc = max(sc, eval(bcode, ns) - b0)
                            ns.update(keep)
                            ns[n1], ns[n2] = k1, k2
                        d[e] = acc / (4 * e * e)
                    # second differences at EPS and EPS/2, combined so that the quartic term cancels
                    resp2[(g, n1, n2, v1, v2)] = r2 = (4 * d[EPS / 2] - d[EPS]) / 3
                    big = max(big, abs(r2))
                scale2[(g, n1, n2)] = sc / EPS ** 2
                if sc > 0 and big > TOL * scale2[(g, n1, n2)]:
                    pair_dep.setdefault(g, set()).add((n1, n2))
        except Exception:                    # counted, and an error: never silently skipped
            failed.append(g)
            hit, moves = set(lit), set(allc)
            if g in plist:
                pair_dep[g] = set(plist[g])
        dep[g], moved[g] = hit, moves
    label, pdg = {}, {}
    ptxt = rd("particles")
    for var, code, name, anti in re.findall(r"(\w+) = Particle\(\s*pdg_code = (-?\d+),\s*name = '([^']*)',\s*antiname = '([^']*)'", ptxt):
        label[var], pdg[var] = name, int(code)
        label[var + "__anti"], pdg[var + "__anti"] = anti, (int(code) if anti == name else -int(code))
    for var, base in re.findall(r"(\w+) = (\w+)\.anti\(\)", ptxt):
        label[var], pdg[var] = label[base + "__anti"], pdg[base + "__anti"]
    entries = []
    own = collections.defaultdict(set)
    lin = collections.defaultdict(list)
    tot = collections.defaultdict(lambda: collections.defaultdict(complex))
    bound = collections.defaultdict(float)
    tot2 = collections.defaultdict(lambda: collections.defaultdict(complex))
    bound2 = collections.defaultdict(float)
    lstruct = dict(re.findall(r"(\w+) = Lorentz\(\s*name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '([^']*)'",
                              rd("lorentz")))
    for parts, col, lor, cpl in re.findall(
            r"Vertex\(\s*name = '\w+',\s*particles = \[([^\]]*)\],\s*color = \[([^\]]*)\],\s*"
            r"lorentz = \[([^\]]*)\],\s*couplings = \{([^}]*)\}", rd("vertices"), re.S):
        pvars = re.findall(r"P\.(\w+)", parts)
        names = [label[p] for p in pvars]
        codes = [pdg[p] for p in pvars]
        if any(n.startswith("gh") for n in names) or (not goldstones and any(
                n in ("G0", "G+", "G-") or abs(c) in (250, 251) for n, c in zip(names, codes))):
            continue                         # ghosts and Goldstones, which the selector ignores too
        lors = re.findall(r"L\.(\w+)", lor)
        cols = re.findall(r"'([^']*)'", col)
        # every vertex, keyed by PDG code, whatever the model calls its particles
        entries.append((names, codes, [(cols[int(ci)], lstruct.get(lors[int(li)], ""), g)
                                       for ci, li, g in re.findall(r"\((\d+),(\d+)\):C\.(GC_\w+)", cpl)]))
        if any(n not in LABEL for n in names):
            continue                         # a particle the selector's labels do not name (SMEFTsim's Z1)
        key = tuple(sorted(LABEL[n] for n in names))
        for g in set(re.findall(r"C\.(GC_\w+)", cpl)):
            own[key] |= dep.get(g, set())
        for ci, li, g in re.findall(r"\((\d+),(\d+)\):C\.(GC_\w+)", cpl):  # every entry
            struct = lstruct.get(lors[int(li)], "")
            form, c0 = _canon(struct)
            ccol, csign = _canon_colour(cols[int(ci)])
            for n in reach.get(g, ()):
                for v in (1.0, 1j):
                    d = resp.get((g, n, v), 0j)
                    lin[(key, n, v)].append((struct, cols[int(ci)], d))
                    tot[(key, n)][(form, ccol, v)] += d * c0 * csign
                bound[(key, n)] += scale.get((g, n), 0.0) * abs(c0)
            for pr in plist.get(g, ()):      # the pairs, for the couplings named in pairs
                for v1, v2 in DIRS2:
                    tot2[(key, pr)][(form, ccol, v1, v2)] += resp2.get((g,) + pr + (v1, v2), 0j) * c0 * csign
                bound2[(key, pr)] += scale2.get((g,) + pr, 0.0) * abs(c0)
    # a vertex content is live in a coefficient when the response summed over all its vertex
    # objects survives on some structure: 1e-16 of the bound is a cancellation, 1e-2 a coupling
    live = collections.defaultdict(set)
    for (key, n), per in tot.items():
        if bound[(key, n)] > 0 and max(abs(z) for z in per.values()) > TOL * bound[(key, n)]:
            live[key].add(n)
    # and live in a pair when the mixed second derivative summed so survives
    live2 = collections.defaultdict(set)
    for (key, pr), per in tot2.items():
        if bound2[(key, pr)] > 0 and max(abs(z) for z in per.values()) > TOL * bound2[(key, pr)]:
            live2[key].add(pr)
    return {"own": own, "live": live, "lin": lin, "dep": dep, "failed": failed, "entries": entries,
            "resp": resp, "value": value, "moved": moved, "pair_dep": pair_dep, "live2": live2}


def _poly(expr):
    """A UFO Lorentz structure as {sorted tuple of factors: coefficient}.  The factors are components
    with explicit indices (P(4,1), Gamma(3,2,-1), ProjM(-1,1), ...), so they commute."""
    def add(a, b, sign):
        out = dict(a)
        for m, v in b.items():
            out[m] = out.get(m, 0) + sign * v
        return {m: v for m, v in out.items() if abs(v) > 1e-12}

    def mul(a, b):
        out = {}
        for ma, va in a.items():
            for mb, vb in b.items():
                m = tuple(sorted(ma + mb))
                out[m] = out.get(m, 0) + va * vb
        return {m: v for m, v in out.items() if abs(v) > 1e-12}

    def walk(n):
        if isinstance(n, ast.BinOp):
            a = walk(n.left)
            if isinstance(n.op, ast.Pow):
                r = {(): 1}
                for _ in range(int(ast.literal_eval(n.right))):
                    r = mul(r, a)
                return r
            b = walk(n.right)
            if isinstance(n.op, ast.Add):
                return add(a, b, 1)
            if isinstance(n.op, ast.Sub):
                return add(a, b, -1)
            if isinstance(n.op, ast.Mult):
                return mul(a, b)
            if isinstance(n.op, ast.Div):
                return {m: v / b[()] for m, v in a.items()}
        if isinstance(n, ast.UnaryOp):
            a = walk(n.operand)
            return {m: -v for m, v in a.items()} if isinstance(n.op, ast.USub) else a
        if isinstance(n, ast.Constant):
            return {(): complex(n.value)}
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name) and n.func.id == "complex":
            return {(): complex(*[ast.literal_eval(x) for x in n.args])}
        return {(ast.unparse(n).replace(" ", ""),): 1}
    return walk(ast.parse(expr, mode="eval").body)


_CANON = {}


_DUMMY = re.compile(r"(?<=[(,])-(\d+)(?=[,)])")


def _canon_term(term):
    """One term of a structure (a sorted tuple of factors) with its summed (negative) indices
    relabelled to the smallest form.  Each term of a UFO structure sums over its own dummies, so the
    relabelling is made term by term: a structure that writes one term with two dummies swapped is
    the same structure (dim8_is writes Q_{leBHD^2}^{(3)} on H Z Z l lbar that way), and one
    relabelling for the whole sum cannot see it."""
    dummies = sorted({d for f in term for d in _DUMMY.findall(f)}, key=int)
    best = term
    for perm in itertools.permutations(range(1, len(dummies) + 1)):
        ren = dict(zip(dummies, perm))
        t = tuple(sorted(_DUMMY.sub(lambda x: f"-{ren[x.group(1)]}", f) for f in term))
        if t < best:
            best = t
    return best


def _canon(struct):
    """(canonical form, factor): the structure equals factor times the canonical form, which has
    leading coefficient one and the summed indices of each term relabelled to the smallest form, so
    that two structures differing by a sign, a normalisation or the names of their dummy indices
    share a canonical form.  A structure that vanishes identically has factor zero."""
    if struct not in _CANON:
        merged = {}
        for term, v in (_poly(struct) if struct else {(): 1}).items():
            k = _canon_term(term)
            merged[k] = merged.get(k, 0) + v
        big = max([abs(v) for v in merged.values()] + [0.0])
        poly = sorted((m, v) for m, v in merged.items() if abs(v) > 1e-12 * big)
        if not poly:
            _CANON[struct] = (((("0",), 1.0, 0.0),), 0.0)
        else:
            c0 = poly[0][1]
            _CANON[struct] = (tuple((m, round((v / c0).real, 9), round((v / c0).imag, 9)) for m, v in poly), c0)
    return _CANON[struct]


_CANON_COLOUR = {}
# colour tensors with a symmetry in all their indices: f, Epsilon and EpsilonBar change sign under
# an odd permutation, d does not
_ANTISYM, _SYM = {"f", "Epsilon", "EpsilonBar"}, {"d"}


def _canon_colour(col):
    """(canonical form, sign): the colour string equals sign times the canonical form.  The
    indices of f, d, Epsilon and EpsilonBar are sorted, with the sign of the permutation for the
    antisymmetric ones, the factors are sorted, and the summed (negative) indices relabelled to the
    smallest form.  FeynRules writes the SM four-gluon colour as f(-1,1,2)*f(3,4,-1) and the
    dimension-eight piece that cancels it as f(-1,1,2)*f(-1,3,4), and compared as strings the
    two looked like different structures, so that the vanishing four-gluon vertex of
    Q_{G^2H^4}^{(1)} in the input-scheme models was taken to exist."""
    if col not in _CANON_COLOUR:
        facs = re.findall(r"(\w+)\(([^)]*)\)", col)
        if not facs:
            _CANON_COLOUR[col] = (col.strip(), 1)
            return _CANON_COLOUR[col]
        dummies = sorted({x for _, a in facs for x in a.split(",") if x.strip().startswith("-")}, key=lambda x: -int(x))
        best = None
        for perm in itertools.permutations(range(1, len(dummies) + 1)):
            ren = {d: str(-k) for d, k in zip(dummies, perm)}
            sign, out = 1, []
            for name, a in facs:
                idx = [ren.get(x.strip(), x.strip()) for x in a.split(",")]
                if name in _ANTISYM or name in _SYM:
                    srt = sorted(idx, key=lambda x: (int(x) < 0, abs(int(x))))
                    if name in _ANTISYM:
                        # parity of the permutation that sorts idx
                        perm_idx = [idx.index(x) for x in srt]
                        inv = sum(1 for i in range(len(perm_idx)) for j in range(i + 1, len(perm_idx)) if perm_idx[i] > perm_idx[j])
                        sign *= -1 if inv % 2 else 1
                    idx = srt
                out.append(f"{name}({','.join(idx)})")
            form = "*".join(sorted(out))
            if best is None or form < best[0]:
                best = (form, sign)
        _CANON_COLOUR[col] = best
    return _CANON_COLOUR[col]


def _resolved(entries):
    """The coupling changes of one vertex summed per canonical (Lorentz, colour) structure."""
    out = collections.defaultdict(complex)
    for struct, col, d in entries:
        form, c0 = _canon(struct)
        ccol, csign = _canon_colour(col)
        out[(form, ccol)] += d * c0 * csign
    return out


def input_scheme_wcs():
    """The coefficients of the input relations, read from ./dim8 so the two lists cannot drift, with the
    flavour structures of their operators (the flavour entries of docs/block_index.json, without Re and Im)."""
    m = re.search(r"^INPUT_SCHEME_WCS = \[([^\]]*)\]", open(os.path.join(ROOT, "dim8")).read(), re.M | re.S)
    names = set(re.findall(r'"(\w+)"', m.group(1)))
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    return names | {re.sub(r"(Re|Im)$", "", f) for e in idx if set(e["wcs"]) & names for f in e.get("flavour", [])}


def compare_linear(path_a, path_b, tol=1e-6):
    """Exit status 1 if two models differ in the linear dependence of a vertex on a coefficient
    outside the input relations."""
    ra, rb = read_model(path_a, generic=True), read_model(path_b, generic=True)
    fa, la, fb, lb = ra["failed"], ra["lin"], rb["failed"], rb["lin"]
    if fa or fb:
        print(f"couplings that could not be evaluated: {len(fa)} in A, {len(fb)} in B")
    scheme = input_scheme_wcs()
    base = lambda n: re.sub(r"(Re|Im)$", "", n)  # noqa: E731
    common = {k[1] for k in la} & {k[1] for k in lb}
    bad, bad_scheme, n = collections.defaultdict(list), collections.defaultdict(list), 0
    resolved_same = negligible = 0
    # the largest response of each coefficient over every vertex of both models: a response 1e-9 of
    # it is the round-off of the finite differences (1e-19 where the couplings are 1e-7), and one
    # model holding such a remnant while the other holds an exact zero is no difference
    cmax = collections.defaultdict(float)
    for lin in (la, lb):
        for k, ents in lin.items():
            for e in ents:
                cmax[k[1]] = max(cmax[k[1]], abs(e[2]))
    for k in sorted(set(la) | set(lb), key=str):
        if k[1] not in common or not k[1].startswith("c8"):
            continue                         # a coefficient only one model has (the dimension-six ones)
        ea, eb = la.get(k, []), lb.get(k, [])
        a, b = [e[2] for e in ea], [e[2] for e in eb]
        scale = max([abs(z) for z in a + b] + [1e-300])
        if scale <= 1e-9 * cmax[k[1]]:
            n += 1
            negligible += 1
            continue
        ma = sorted(abs(z) for z in a if abs(z) > tol * scale)
        mb = sorted(abs(z) for z in b if abs(z) > tol * scale)
        n += 1
        same = abs(sum(a) - sum(b)) <= tol * scale and len(ma) == len(mb) and \
            all(abs(x - y) <= tol * scale for x, y in zip(ma, mb))
        if not same:
            # the two models may write one coupling on structures that differ by a sign or a
            # normalisation, or split it differently: compare per canonical structure
            ra, rb = _resolved(ea), _resolved(eb)
            # measured against the entries themselves: a vertex whose entries cancel in both models
            # resolves to round-off, and round-off against round-off is no difference
            sc = max([abs(z) for z in list(ra.values()) + list(rb.values())] + [scale])
            if all(abs(ra.get(q, 0) - rb.get(q, 0)) <= tol * sc for q in set(ra) | set(rb)):
                resolved_same += 1
                continue
            (bad_scheme if base(k[1]) in scheme else bad)[base(k[1])].append(" ".join(k[0]))
    print(f"{n} (vertex, coefficient, 1 or i) responses compared, {path_a} against {path_b}")
    print(f"{resolved_same} agree only once the couplings are put on common Lorentz structures "
          f"(one model writes a structure with the opposite sign or splits a coupling)")
    print(f"{negligible} are below 1e-9 of the coefficient's largest response in both models (round-off)")
    print(f"differences outside the input relations: {sum(len(v) for v in bad.values())} "
          f"in {len(bad)} coefficients")
    for w, keys in sorted(bad.items()):
        print(f"  {w:16s} {len(keys):3d}  e.g. {', '.join(sorted(set(keys))[:4])}")
    print(f"differences in the input-relation coefficients (expected): "
          f"{sum(len(v) for v in bad_scheme.values())} in {len(bad_scheme)} of {len(scheme)}")
    # listed as well, since two models in the same scheme should not differ here either
    for w, keys in sorted(bad_scheme.items()):
        print(f"  {w:16s} {len(keys):3d}  e.g. {', '.join(sorted(set(keys))[:4])}")
    return 1 if bad or fa or fb else 0


def by_block(model_vertices, block_of):
    """{block: set of field contents} from read_model's output and a coefficient -> block map."""
    out = collections.defaultdict(set)
    for key, names in model_vertices.items():
        for n in names:
            b = block_of(n)
            if b:
                out[b].add(key)
    return out


def no_vertex_problems(models_dir, models, catalogue):
    """Which operators a model lacks and should have, or has and should lack.  A count of the basis cannot see an
    operator whose vertices all vanish, so every baryon-number-conserving coefficient must occur in couplings.py of
    each model, apart from the operators of dsl.NO_VERTEX, which must not, and so must the coefficient of every
    further flavour structure (docs/block_index.json), which vanishes on the card where it carries a light Yukawa
    coupling and must stay in the model all the same."""
    out = []
    flavour = {e["ops"][0]: sorted({re.sub(r"(Re|Im)$", "", f) for f in e.get("flavour", [])})
               for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json")))}
    # A name occurs when a whole word of the file is the name, or the name with Re or Im.  The words that begin as
    # the names do are read once per model: one search of a file of half a gigabyte per name took twenty minutes a
    # model, against six seconds.
    names = [e["wc"] for e in catalogue if not e["b_violating"]] + [f for fs in flavour.values() for f in fs]
    word = re.compile(r"\b(?:" + "|".join(sorted({re.escape(n[:2]) for n in names})) + r")\w*")
    for m in models:
        words = set(word.findall(open(os.path.join(models_dir, m, "couplings.py"), errors="replace").read()))

        def occurs(name):
            return any(name + s in words for s in ("", "Re", "Im"))
        for e in catalogue:
            if e["b_violating"] or not models_of([e["wc"]], [m]):
                continue
            has = occurs(e["wc"])
            if has == (e["label"] in dsl.NO_VERTEX):
                out.append(f"{m}: {e['label']} ({e['wc']}) " + ("has a coupling and should vanish" if has else "has no coupling"))
            for f in flavour.get(e["label"], []):
                if not occurs(f):
                    out.append(f"{m}: {e['label']}, flavour structure {f}, has no coupling")
    return out


def main(argv):
    if "--linear" in argv:
        i = argv.index("--linear")
        return compare_linear(argv[i + 1], argv[i + 2])
    models_dir = argv[argv.index("--models") + 1] if "--models" in argv else os.path.join(ROOT, "models")
    index_path = argv[argv.index("--index") + 1] if "--index" in argv else os.path.join(ROOT, "build", "vertex_index.json")
    index = json.load(open(index_path))
    # an operator's own coefficients and those of its further flavour structures (block DIM8F)
    wc8 = {re.sub(r"(Re|Im)$", "", w) if w in e.get("flavour", []) else w: e["block"]
           for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json"))) for w in e["wcs"] + e.get("flavour", [])}
    bviol = {e["block"] for e in json.load(open(os.path.join(ROOT, "docs", "catalogue.json"))) if e["b_violating"]}
    cls6 = {w: c for c, ws in DIM6.items() for w in ws.split()}
    block6 = {}
    for b, (c, _) in DIM6_BLOCKS.items():
        block6.setdefault(c, "L6cl8" if c == "psi^4" else b)

    def block8(n):
        return wc8.get(n) or wc8.get(re.sub(r"(Re|Im)$", "", n))

    def block_6(n):
        c = cls6.get(n) or cls6.get(re.sub(r"(Abs|Ph|Re|Im)$", "", n))
        return block6.get(c)

    lost = no_vertex_problems(models_dir, IS_MODELS, json.load(open(os.path.join(ROOT, "docs", "catalogue.json"))))
    for line in lost:
        print("[no vertex] " + line)
    if lost:
        return 1
    # own: a vertex carrying the coefficient by name that is also live; live: the vertex exists
    own8, live8, own6, live6, failures = {}, {}, None, None, 0
    for m in DIM8_MODELS:
        r = read_model(os.path.join(models_dir, m), generic=True)
        failures += len(r["failed"])
        if r["failed"]:
            print(f"{m}: {len(r['failed'])} couplings could not be evaluated, e.g. {r['failed'][:3]}")
        mine = {k: r["own"][k] & r["live"][k] for k in r["own"]}
        own8[m], live8[m] = by_block(mine, block8), by_block(r["live"], block8)
        if m == DIM6_MODEL:
            own6, live6 = by_block(mine, block_6), by_block(r["live"], block_6)
        print(f"read {m}: {len(r['live'])} field contents, {len(live8[m])} dimension-eight blocks with a vertex")

    # The input-scheme models must agree on every vertex.  dim8_plain, which has no input scheme,
    # may in addition carry a vertex of an input-scheme coefficient that the scheme absorbs, such
    # as the three-gluon vertex of Q_{G^2H^4}^{(1)}, whose vacuum piece the scheme puts into the
    # normalisation of the gluon.  The list follows the input-scheme models.
    scheme_blocks = {block8(w) for w in input_scheme_wcs()}
    wcs_of = {e["block"]: e["wcs"] for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json")))}
    missing, inconsistent, absent, absorbed, uncompared = [], [], [], [], []
    for b, verts in index.items():
        listed = {tuple(sorted(v)) for v in verts}
        if b.startswith("L8op"):
            if b in bviol:                 # baryon-number violating, in no released model
                continue
            # the models of the block's basis.  The list keeps, unchecked, the vertices of a block whose basis
            # has no model here.
            ms = models_of(wcs_of.get(b, []), DIM8_MODELS)
            if not ms:
                uncompared.append(b)
                continue
            ism = [m for m in IS_MODELS if m in ms]
            own = {m: own8[m].get(b, set()) for m in ms}
            live = {m: live8[m].get(b, set()) for m in ms}
            scheme = b in scheme_blocks
            for m in ms:
                for k in sorted(own[m] - listed):
                    if m.startswith(PLAIN_MODEL) and scheme and not any(k in live[x] for x in ism):
                        absorbed.append((b, k, ism, "not listed"))
                    else:
                        missing.append((b, m, k))
            for k in sorted(listed):
                where = [m for m in ms if k in live[m]]
                if not where:
                    absent.append((b, k))
                elif len(where) < len(ms):
                    if scheme:
                        absorbed.append((b, k, sorted(set(ms) - set(where)),
                                         "dropped" if all(m.startswith(PLAIN_MODEL) for m in where) else "kept"))
                    else:
                        inconsistent.append((b, k, sorted(set(ms) - set(where))))
        else:
            key = "L6cl8" if b.startswith("L6cl8") else b
            if not b.startswith("L6cl8"):  # a four-fermion sub-block holds part of the class only
                for k in sorted(own6.get(key, set()) - listed):
                    missing.append((b, DIM6_MODEL, k))
            for k in sorted(listed):
                if k not in live6.get(key, set()):
                    absent.append((b, k))
    # the four-fermion class as a whole
    listed8 = {tuple(sorted(v)) for b, vs in index.items() if b.startswith("L6cl8") for v in vs}
    for k in sorted(own6.get("L6cl8", set()) - listed8):
        missing.append(("L6cl8", DIM6_MODEL, k))

    def show(title, rows, fmt):
        print(f"\n{title}: {len(rows)}")
        for r in rows:
            print("  " + fmt(r))

    show("missing (a model has the vertex, the list does not)", missing,
         lambda r: f"{r[0]:8s} {' '.join(r[2])}   in {r[1]}")
    show("inconsistent (some models have the vertex, these lack it)", inconsistent,
         lambda r: f"{r[0]:8s} {' '.join(r[1])}   missing from {', '.join(r[2])}")
    per = collections.Counter(b for b, _ in absent)
    show("absent (every model lacks the vertex)", absent, lambda r: f"{r[0]:8s} {' '.join(r[1])}")
    print(f"  ({len(per)} blocks; {sum(1 for b in per if not index_has_live(b, absent, index))} of them "
          f"have no vertex in any model)")
    show("absorbed by an input scheme (an input-relation coefficient; expected)", absorbed,
         lambda r: f"{r[0]:8s} {' '.join(r[1])}   lacking in {', '.join(r[2])}, {r[3]}")
    if uncompared:
        print(f"\nnot compared, no model of their basis in {models_dir}: {len(uncompared)} blocks, kept as listed "
              f"({' '.join(sorted(uncompared, key=lambda b: int(b[4:])))})")
    bad = missing or inconsistent or failures
    if "--write" in argv:
        if bad:
            print("\nnot written: the errors above come first")
            return 1
        drop = collections.defaultdict(set)
        for b, k in absent + [(b, k) for b, k, _, how in absorbed if how == "dropped"]:
            drop[b].add(k)
        new = {b: [v for v in vs if tuple(sorted(v)) not in drop[b]] for b, vs in index.items()}
        put_json(index_path, new)
        print(f"\nwrote {os.path.relpath(index_path, ROOT)}: "
              f"{sum(len(v) for v in drop.values())} entries removed")
        # The absorbed vertices, with the models that carry them, so that ./dim8 select can give
        # each released model its own vertices: dim8_plain the ones only it has, and dim8_mw none of
        # those its scheme absorbs.
        side = os.path.join(ROOT, "build", "vertex_index_absorbed.json")
        put_json(side, {"models": DIM8_MODELS, "absorbed": [
            {"block": b, "fields": list(k), "carried_by": sorted(set(DIM8_MODELS) - set(lacking))}
            for b, k, lacking, _ in absorbed]})
        print(f"wrote {os.path.relpath(side, ROOT)}: {len(absorbed)} absorbed vertices")
    return 1 if bad else 0


def put_json(path, data):
    """Write through a temporary file, so that a failed write never leaves a truncated list."""
    json.dump(data, open(path + ".tmp", "w"))
    os.replace(path + ".tmp", path)


def index_has_live(b, absent, index):
    """Whether block b keeps at least one listed vertex after the absent ones are removed."""
    gone = {k for bb, k in absent if bb == b}
    return any(tuple(sorted(v)) not in gone for v in index[b])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
