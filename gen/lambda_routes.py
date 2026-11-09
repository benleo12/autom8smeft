#!/usr/bin/env python3
"""The power of lambda of every dimension-six and dimension-eight class in a process, by its cheapest tree.

    gen/lambda_routes.py "p p > w+ w-" [--n 4]
    gen/lambda_routes.py "p p > h h j j QCD=0"

A tree is the product of its vertices and propagators.  In the energy counting of the
paper (Lambda, E, v) ~ (lambda^-3, lambda^-2, lambda^-1): a Standard Model three-point vertex
carries a momentum or a fermion pair and counts lambda^-2, or a vev and counts lambda^-1, a four-point vertex
counts lambda^0, a propagator lambda^4, and a vertex of an operator of mass dimension d with
m legs and p vacuum insertions lambda^(d-12+2m+p), that is lambda^(2m-4+p) at dimension eight
and lambda^(2m-6+p) at dimension six.  No Standard Model tree of an n-point process lies below
lambda^(2n-8), and the header gives the power SM of the channel's leading tree, so a dimension-eight
class entering at lambda^(SM+Delta) has
M8/MSM ~ E^(8-Delta) v^(Delta-4) / Lambda^4 and a dimension-six class M6/MSM ~ E^(4-Delta) v^(Delta-2) / Lambda^2.
The route printed beside each class is its cheapest tree: the operator vertex, its vacuum
insertions, and the Standard Model vertices the tree uses, which are the coupling factors that
multiply the term.

For every operator of a class, every vertex in the selector's list (build/vertex_index.json)
and every way of hanging the external particles on it through Standard Model vertices (the
same recursion as gen/process.py), the cheapest tree is kept.  Among trees of equal power the
one with the fewest Standard Model vertices is kept, compared at every step of the search, so
that a contact term is named before a smaller vertex that ties with it (the three-point vertex of
two massless quarks of psi^2H^2D^3 vanishes on shell).  A fermion line keeps a generation label:
the Standard Model vertices are flavour diagonal up to the Cabibbo mixing of the first two
generations (the CKM matrix of the released models is block diagonal, with the third generation
unmixed), so the label is 0 for the first two generations and 2 for the third, for quarks and
leptons alike.  At an operator vertex the fermion legs must pair into the Dirac chains of the
operator, each chain joining two fields of one generation, as gen/operators.py contracts them
(its flavour pairs, and their conjugate for the h.c.), the charge-conjugated chains of the
baryon-number-violating classes included.  The dimension-six blocks are not in the encoding, and
their chains are written by hand from the operators of tests/gen_smoke/dim6_smeftsim.fr
(DIM6_CHAINS).  The generation matters for one coupling only, the
Yukawa coupling, which is of order one for the top quark and enters like any vertex with a fermion
pair, at lambda^-2.  The Yukawa couplings of the other quarks and of the leptons are suppressed by
their masses and are left out, and so are the masses themselves.  The b quark is therefore not
collapsed onto d and s, since a b line turns into a top line at a W vertex.  A chain of a
dimension-six operator can carry a Yukawa coupling too: the dimension-six sector is SMEFTsim's, in
the U(3)^5 framework, where a chain of two different fields carries the Yukawa matrix that makes it
invariant, so that of those chains only the one of q and u at the third generation, which carries
y_t, is of order one, and the others are left out (dim6_yukawa).  The number of vacuum
insertions of a vertex is the operator's number of Higgs fields minus the Higgs legs of the
vertex.  Classes that enter only through the input relations have no tree here and are
lambda^(SM+8).  Whether a class interferes with the Standard Model is a separate question,
which gen/lambda_series.py answers from the chiralities of the external fermions.  An assignment
of the external particles that no tree can join, by its electric charge, baryon number, lepton
number or generation labels, is skipped (conserving()).  The number of external legs n is read
from the process unless --n is given.

./dim8 select counts the dimension-six sector of a model that carries one coefficient by
coefficient as well, from the vertices of each coefficient in build/dim6_index.json
(validate/dim6_index.py).  A coefficient is then a block of its own, keyed by its name, with the
Dirac chains of its operator, the Higgs fields of its class and its gluon field strengths
(DIM6_COEFF), and a chain of two different fields carries its Yukawa matrix as in its class
(dim6_yukawa).  A coefficient can also move Standard Model vertices through an internal parameter
of the model, as C_HBox moves h W W, h Z Z and the Yukawa couplings through the normalisation of the
Higgs field.  Such a vertex has the chains of the Standard Model vertex (DIM6_RESCALED_CHAINS) and
counts at its power and four more, v^2/Lambda^2 (leading, rescaled).

A fermion leg also carries the chirality of its field, L or R, beside its generation ("uqbar@2:R"),
and a barred leg the chirality of the field whose conjugate it is, so that the conjugate of t_L,
tbar P_R, is L.  In the chain ubar Gamma_A S(p) Gamma_B u the propagator joins the unbarred leg of
A, of label a, to the barred leg of B, of label b, as P_a (pslash + m) P_opp(b), and since
pslash P_opp(b) = P_b pslash, the pslash term survives when a = b and the mass term when a and b
differ.  A line between two legs of one label is therefore free, and a line between two labels
needs a mass, which only the top quark has here: m_t ~ v in place of pslash ~ E costs one power of
lambda, enters the power like any other cost, and the route names it, [m_t].  A light line, the b
quark's included, between two labels gives no tree.  The Standard Model vertices give their legs
the labels of their couplings: the W current joins two L legs, the photon, Z and gluon currents two
L or two R legs (a neutrino has no R), and a Yukawa coupling an L leg to an R leg, since y_f joins
the doublet to the singlet f_R.  It is the top's coupling where its R leg is a top quark, so that
of the couplings of a charged Goldstone boson to a top line, from -y_t qbar Htilde t_R + h.c. with
y_b = 0, the G+ vertex is tbar_R b_L ([GP dq uqbar] with uqbar R and dq L) and the G- vertex
bbar_L t_R.  The legs of an operator vertex take the labels of the fields of its Dirac chains, L
for l and q and R for e, u and d (chains()).  An external fermion takes either label, since the
counting sums over the helicities, and the label it takes matters only for the interference.  With
the labels a fermion line has twice the states, and the search keeps them apart in its cache.

A right-handed line couples to the photon and the Z through the hypercharge boson B alone, and B
has no vertex with a W pair.  Where a photon or Z line joins a neutral current of two R legs to a
pure-gauge vertex of the Standard Model with a W pair, [A W Wbar], [W Wbar Z] or one of the three
four-point ones, the photon and the Z trees therefore cancel up to M_Z^2/E^2, as in
e^2 Q/s - g^2 s_W^2 Q/(s - M_Z^2) = -g^2 s_W^2 Q M_Z^2/(s (s - M_Z^2)) for f_R fbar_R > W_T W_T, and
such a line costs two more powers of lambda (cancellation()).  B couples to h Z Z, to two Goldstone
bosons and to a Goldstone boson with a W, so no other vertex cancels, and a vertex of an operator
is counted as it is, since whether its photon and Z couplings cancel for a B depends on the
operator.

QCD=0 in the process, as for electroweak HHjj, removes every tree with a power of g_s, as MadGraph
does: the Standard Model vertices with a gluon, and an operator vertex with more gluon legs than the
operator has gluon field strengths, since each further gluon comes from a covariant derivative or
from the non-abelian part of a field strength and carries g_s.  Other QCD orders are refused.

A W or a Z in the process may carry MadGraph's polarisation mark, {T} or {0}.  A transverse one is
counted as an unmarked one.  A longitudinal one is counted by the equivalence theorem, as the paper
counts it: either its Goldstone boson takes its place, at no cost, or it keeps its gauge leg, whose
polarisation vector is of order M_W/E and costs one power of lambda.  The power of a class in the
channel is the smallest, over these choices, of the cost of the choice and the power of the tree,
and the Standard Model amplitude of the channel is found the same way (sm_power), which can differ
from lambda^(2n-8): W_L W_T and Z_T h are lambda^1, and so is b b~ > W_L W_T, whose t-channel tree
with one Goldstone coupling needs a top mass insertion.  The Goldstone vertices are those of the
Feynman-gauge lists (gauge="feynman", process.load_data), build/vertex_index_fg.json and
build/sm_vertices_fg.json, which are made in Feynman gauge with Mathematica and FeynRules and ship
in build/ with the release.  There a Goldstone boson counts as a Higgs field: it is not at the
vacuum, so p is the operator's number of Higgs fields minus its scalar legs, and a three-point
Standard Model vertex carries a vev when it has one or three scalars and a momentum when it has
none or two.
"""
import functools, itertools, json, os, sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import process as P  # noqa: E402
import dsl  # noqa: E402
import emit_fr  # noqa: E402

INF = 10 ** 6
MEMBERS = P.CLASS_MEMBERS                    # {"uq": ["u", "c", "t"], ...}, by generation
CLASS = {m: c for c, ms in MEMBERS.items() for m in ms}
CLASS.update({c: c for c in MEMBERS})
SECTOR = {"uq": "q", "dq": "q", "l": "l", "vl": "l"}
# A fermion line carries the generation label 0 (first two generations, which the Cabibbo angle
# mixes) or 2 (third generation, unmixed).  The leptons are labelled the same way, since some
# operators join a lepton and a quark of one generation in a Dirac chain.
THIRD = {"t", "b", "ta", "vt"}
HEAVY = {("uq", 2)}                          # the top quark, whose Yukawa coupling and mass are kept
# the names of a mass insertion on a top line and, in the search that says why an operator has no
# tree, on a light line (propagator())
TOP_MASS, LIGHT_MASS = "m_t", "m_f"
# the flavour collapse of gen/process.py with the b quark kept apart, since its doublet partner
# is the top quark
ROUTE_COLLAPSE = {k: v for k, v in P.COLLAPSE.items() if k not in ("b", "b~")}
# the FeynRules classes of the components of each field of the Murphy basis
COMPONENTS = {"l": ("l", "vl"), "e": ("l",), "q": ("uq", "dq"), "u": ("uq",), "d": ("dq",)}
# the chirality of each field of the Murphy basis, as gen/dsl.py writes it: L for the doublets l
# and q, R for the singlets e, u and d
CHIRALITY = {name: f["chir"] for name, f in dsl.FERMIONS.items()}


@functools.lru_cache(maxsize=None)
def _parts(f):
    """(base, bar, generation label, chirality label) of a leg: ("uq", "bar", 2, "R") for
    "uqbar@2:R", ("t", "", None, None) for "t", (f, "", None, None) for a boson."""
    g = c = None
    if ":" in f:
        f, c = f.split(":")
    if "@" in f:
        f, g = f.split("@")
        g = int(g)
    if f.endswith("bar") and f[:-3] in CLASS:
        return f[:-3], "bar", g, c
    return f, "", g, c


def is_fermion(f):
    return _parts(f)[0] in CLASS


def fclass(f):
    """The class label of a fermion leg with its bar: "uqbar" for "tbar" and for "uqbar@2:R"."""
    base, bar = _parts(f)[:2]
    return CLASS[base] + bar


def generation(f):
    """The generation label, 0 or 2, of a fermion member or a labelled leg; None for a class label."""
    base, _, g, _ = _parts(f)
    if g is not None:
        return g
    if base in MEMBERS:
        return None
    return 2 if base in THIRD else 0


def chirality(f):
    """The chirality label, L or R, of a labelled fermion leg, and None without one."""
    return _parts(f)[3]


def labels(f):
    """The chirality labels a fermion leg can take: L and R, and L alone for a neutrino."""
    return ("L",) if CLASS[_parts(f)[0]] == "vl" else ("L", "R")


def tag(f, g, c=None):
    """The fermion leg f with the generation label g and the chirality label c, as "uqbar@2:R"."""
    return f"{fclass(f)}@{g}" + (f":{c}" if c else "")


def anti(f):
    """The conjugate leg, at the other end of the line: it keeps the generation label of f and
    drops its chirality label, since the leg at the other end carries its own."""
    if is_fermion(f) and "@" in f:
        core, g = f.split("@")
        return f"{P.anti(core)}@{g.split(':')[0]}"
    return P.anti(f)


def sector(f):
    return SECTOR[CLASS[_parts(f)[0]]]


def generations(group, sec):
    """The generation labels of the external fermions of one sector, quarks "q" or leptons "l", in a group."""
    return {generation(x) for x in group if is_fermion(x) and generation(x) is not None and sector(x) == sec}


def matches(f, x):
    """Does the leg f end on the external particle x?  A labelled fermion leg needs the class and
    the generation label of x, and either chirality ends on it."""
    if is_fermion(f) and _parts(f)[2] is not None:
        return is_fermion(x) and fclass(x) == fclass(f) and generation(x) == generation(f)
    return P._same_field(f, x)


def _better(a, b):
    """A tree a is better than b if its power is smaller, or equal with fewer Standard Model
    vertices, a mass insertion counted as one."""
    return (a[0], len(a[1])) < (b[0], len(b[1]))


# ------------------------------------------------------------------------------ chirality ----
# The chirality labels of the legs of every vertex and the rule of the propagator between two of
# them, for Cheapest here and for gen/lambda_series.py's Frontier, which inherits variants() and
# assign() from it, so that the two searches cannot count chirality differently.

@functools.lru_cache(maxsize=None)
def sm_options(v, g, light=False):
    """The chirality labels of the two fermion legs of the Standard Model vertex v (a sorted tuple)
    whose fermion line has the generation label g, one dict {class with bar: label} per way, and
    one empty dict for a vertex without fermions.  The W current is ubar_L gamma d_L W+ and joins
    two L legs.
    The photon, Z and gluon currents join two L legs or two R legs, the neutrino's only two L legs,
    since it has no right-handed field.  A Yukawa coupling, of the Higgs boson or a Goldstone boson,
    joins an L leg to an R leg: -y_d qbar H d_R - y_u qbar Htilde u_R - y_e lbar H e_R + h.c.
    joins each singlet f_R to the doublet with the coupling y_f of its own flavour.  It is kept
    where its R leg is a top quark, whose y_t is of order one, so that on a top line [GP dq uqbar]
    is tbar_R b_L G+ and [GPbar dqbar uq] is bbar_L t_R G-, and with light=True also where it is a
    light fermion, the b quark's y_b included."""
    ferm = [x for x in v if is_fermion(x)]
    if not ferm:
        return ({},)
    bar = next(x for x in ferm if _parts(x)[1])
    plain = next(x for x in ferm if not _parts(x)[1])
    bos = [x for x in v if not is_fermion(x)]
    if any(b in SCALARS for b in bos):
        ways = [("L", "R"), ("R", "L")]
        if not light:
            ways = [(cb, cp) for cb, cp in ways if (CLASS[_parts(bar if cb == "R" else plain)[0]], g) in HEAVY]
    elif any(b in ("W", "Wbar") for b in bos):
        ways = [("L", "L")]
    else:
        ways = [("L", "L"), ("R", "R")]
    return tuple({fclass(bar): cb, fclass(plain): cp} for cb, cp in ways
                 if cb in labels(bar) and cp in labels(plain))


def propagator(f, c, light=False):
    """The mass insertions on the line from the leg f to a leg of chirality label c at its other
    end: () when the labels agree, the pslash term of the propagator, and ("m_t",) when they
    differ on a top line, the mass term, one power of lambda above it, since m_t ~ v stands where
    pslash ~ E stood.  A light line between two labels needs the mass of a light fermion, which
    the counting drops (None), and which light=True keeps as ("m_f",) to say why an operator has no
    tree.  A leg without a chirality label is the first external particle of a tree, which enters
    its vertex without a propagator, so its label is the vertex's at no cost."""
    cf = chirality(f)
    if cf is None or cf == c:
        return ()
    base, _, g, _ = _parts(f)
    if (CLASS[base], g) in HEAVY:
        return (TOP_MASS,)
    return (LIGHT_MASS,) if light else None


# The neutral electroweak bosons, and the pure-gauge vertices of the Standard Model with a W pair,
# which come from the SU(2) field strength, so that their neutral boson enters as W^3 and never as B
NEUTRAL = {"A", "Z"}
WW_GAUGE = {("A", "W", "Wbar"), ("W", "Wbar", "Z"), ("A", "A", "W", "Wbar"), ("A", "W", "Wbar", "Z"),
            ("W", "Wbar", "Z", "Z")}


def end_kind(v, rest, c):
    """What the Standard Model vertex v is at the end of a photon or Z line, for cancellation():
    "ww" for a pure-gauge vertex with a W pair, "rc" for a neutral current whose two fermion legs
    carry the label R, and None for any other.  rest are the legs of v other than the one that
    joins the line into it, with their labels (variants()), and c is the label of that leg, None
    for a boson."""
    if v in WW_GAUGE:
        return "ww"
    if len(v) == 3 and NEUTRAL & set(v) and sum(map(is_fermion, v)) == 2:
        labs = [chirality(x) for x in rest if is_fermion(x)] + ([c] if c else [])
        return "rc" if labs == ["R", "R"] else None
    return None


def cancellation(f, up, kd):
    """The powers of lambda a line f costs beyond its propagator when f is a photon or a Z between a
    right-handed neutral current and a pure-gauge vertex with a W pair, one at each end (up and kd,
    end_kind()): the photon and the Z trees cancel there up to M_Z^2/E^2, two powers of lambda,
    since a right-handed fermion couples to them through B alone and B has no vertex with a W pair.
    0 for any other line."""
    return 2 if f in NEUTRAL and {up, kd} == {"rc", "ww"} else 0


# The Dirac chains of the dimension-six blocks, which are not in the encoding, written by hand from
# the operators of tests/gen_smoke/dim6_smeftsim.fr: one entry per chain structure, with the
# operators that share it named on the line above, each chain as (barred field, unbarred field) in
# the names of the Warsaw basis, and chains() adds the h.c.  The primed four-fermion operators
# O_ll', O_qq^(1)', O_qq^(3)', O_uu' and O_dd' (Oll1, Oqq11, Oqq31, Ouu1 and Odd1) join two
# generations in each chain, and the Fierz identity of two currents of one chirality writes them as
# chains of one generation each, which are those of the unprimed ones.  The chains of one generation
# of the operators that carry a Yukawa or a CKM matrix (classes 5, 6, 8d and O_Hud) hold since both
# are block diagonal in the generation labels.  Those Yukawa matrices are the spurions of SMEFTsim's
# U(3)^5 framework (docs/DIM6.md): a chain of two different fields carries the one that makes it
# invariant, Conjugate[yu] on (q, u), Conjugate[yd] on (q, d) and yd on O_ledq's (dbar q),
# Conjugate[yl] on (l, e), and yu.CKM.Conjugate[yd] on the (u, d) of O_Hud, while a chain of one
# field carries none.  Of their entries only y_t, on the (q, u) chain of the third generation, is of
# order one (dim6_yukawa).
DIM6_CHAINS = {
    # psi^2H^3: O_eH, O_uH, O_dH, one chain of a doublet and a singlet
    "L6cl5": [(("l", "e"),), (("q", "u"),), (("q", "d"),)],
    # psi^2XH: O_eW and O_eB, O_uG, O_uW and O_uB, O_dG, O_dW and O_dB, the same chains
    "L6cl6": [(("l", "e"),), (("q", "u"),), (("q", "d"),)],
    # psi^2H^2D: O_Hl^(1,3), O_He, O_Hq^(1,3), O_Hu, O_Hd and O_Hud, the last one (ubar_R gamma d_R)
    "L6cl7": [(("l", "l"),), (("e", "e"),), (("q", "q"),), (("u", "u"),), (("d", "d"),), (("u", "d"),)],
    # (LL)(LL): O_ll and O_ll', O_qq^(1,3) and their primed ones, O_lq^(1,3)
    "L6cl8a": [(("l", "l"), ("l", "l")), (("q", "q"), ("q", "q")), (("l", "l"), ("q", "q"))],
    # (RR)(RR): O_ee, O_uu and O_uu', O_dd and O_dd', O_eu, O_ed, O_ud^(1,8)
    "L6cl8b": [(("e", "e"), ("e", "e")), (("u", "u"), ("u", "u")), (("d", "d"), ("d", "d")),
               (("e", "e"), ("u", "u")), (("e", "e"), ("d", "d")), (("u", "u"), ("d", "d"))],
    # (LL)(RR): O_le, O_lu, O_ld, O_qe, O_qu^(1,8), O_qd^(1,8)
    "L6cl8c": [(("l", "l"), ("e", "e")), (("l", "l"), ("u", "u")), (("l", "l"), ("d", "d")),
               (("q", "q"), ("e", "e")), (("q", "q"), ("u", "u")), (("q", "q"), ("d", "d"))],
    # the scalar and tensor ones: O_ledq = (lbar e)(dbar q), O_quqd^(1,8) = (qbar u)(qbar d),
    # O_lequ^(1,3) = (lbar e)(qbar u), two chains of a doublet and a singlet
    "L6cl8d": [(("l", "e"), ("d", "q")), (("q", "u"), ("q", "d")), (("l", "e"), ("q", "u"))],
}

# The dimension-six coefficients one by one, which ./dim8 select lists for a model with a dimension-six
# sector from build/dim6_index.json (validate/dim6_index.py): SMEFTsim's name -> (the operator's name
# in the Warsaw basis, written as ./dim8 writes the four of the input relations, the class block as
# DIM6 and DIM6_CHAINS key it, a four-fermion operator in the block of its chirality structure, and
# the Dirac chains of the operator in the form of DIM6_CHAINS, which chains() registers under the
# coefficient's name with their h.c., as it registers the classes).  A bosonic operator has no chain.
# The coefficients and their order within a class are those of validate/check_legs.py.  The primed
# four-fermion operators are the second flavour contraction of the U(3)^5 framework, which SMEFTsim
# names with the suffix 1: Oll1 = (lbar_p gamma l_r)(lbar_r gamma l_p) in
# tests/gen_smoke/dim6_smeftsim.fr, and so Oqq11, Oqq31, Ouu1 and Odd1, whose texnames in
# models/dim68_is/parameters.py carry "Prime".  The suffix 1 of cqq1, clq1, cHl1 and cHq1 is the
# singlet of the pair (1, 3) instead, and that of cud1, cqu1, cqd1 and cquqd1 the colour singlet of
# (1, 8).  The primed ones of cquqd1 and cquqd8 are cquqd11 and cquqd81, whose Yukawa matrices join the
# quark doublet of one Dirac chain to the singlet of the other.
DIM6_COEFF = {
    # X^3
    "cG": (r"Q_G", "L6cl1", ()),
    "cGtil": (r"Q_{\widetilde G}", "L6cl1", ()),
    "cW": (r"Q_W", "L6cl1", ()),
    "cWtil": (r"Q_{\widetilde W}", "L6cl1", ()),
    # H^6
    "cH": (r"Q_H", "L6cl2", ()),
    # H^4D^2
    "cHbox": (r"Q_{H\Box}", "L6cl3", ()),
    "cHDD": (r"Q_{HD}", "L6cl3", ()),
    # X^2H^2
    "cHW": (r"Q_{HW}", "L6cl4", ()),
    "cHB": (r"Q_{HB}", "L6cl4", ()),
    "cHWB": (r"Q_{HWB}", "L6cl4", ()),
    "cHG": (r"Q_{HG}", "L6cl4", ()),
    "cHGtil": (r"Q_{H\widetilde G}", "L6cl4", ()),
    "cHWtil": (r"Q_{H\widetilde W}", "L6cl4", ()),
    "cHBtil": (r"Q_{H\widetilde B}", "L6cl4", ()),
    "cHWBtil": (r"Q_{H\widetilde W B}", "L6cl4", ()),
    # psi^2H^3
    "ceH": (r"Q_{eH}", "L6cl5", (("l", "e"),)),
    "cuH": (r"Q_{uH}", "L6cl5", (("q", "u"),)),
    "cdH": (r"Q_{dH}", "L6cl5", (("q", "d"),)),
    # psi^2XH
    "ceW": (r"Q_{eW}", "L6cl6", (("l", "e"),)),
    "ceB": (r"Q_{eB}", "L6cl6", (("l", "e"),)),
    "cuG": (r"Q_{uG}", "L6cl6", (("q", "u"),)),
    "cuW": (r"Q_{uW}", "L6cl6", (("q", "u"),)),
    "cuB": (r"Q_{uB}", "L6cl6", (("q", "u"),)),
    "cdG": (r"Q_{dG}", "L6cl6", (("q", "d"),)),
    "cdW": (r"Q_{dW}", "L6cl6", (("q", "d"),)),
    "cdB": (r"Q_{dB}", "L6cl6", (("q", "d"),)),
    # psi^2H^2D, O_Hud being ubar_R gamma d_R
    "cHl1": (r"Q_{Hl}^{(1)}", "L6cl7", (("l", "l"),)),
    "cHl3": (r"Q_{Hl}^{(3)}", "L6cl7", (("l", "l"),)),
    "cHe": (r"Q_{He}", "L6cl7", (("e", "e"),)),
    "cHq1": (r"Q_{Hq}^{(1)}", "L6cl7", (("q", "q"),)),
    "cHq3": (r"Q_{Hq}^{(3)}", "L6cl7", (("q", "q"),)),
    "cHu": (r"Q_{Hu}", "L6cl7", (("u", "u"),)),
    "cHd": (r"Q_{Hd}", "L6cl7", (("d", "d"),)),
    "cHud": (r"Q_{Hud}", "L6cl7", (("u", "d"),)),
    # psi^4, (LL)(LL)
    "cll": (r"Q_{ll}", "L6cl8a", (("l", "l"), ("l", "l"))),
    "cll1": (r"Q_{ll}'", "L6cl8a", (("l", "l"), ("l", "l"))),
    "cqq1": (r"Q_{qq}^{(1)}", "L6cl8a", (("q", "q"), ("q", "q"))),
    "cqq11": (r"Q_{qq}^{(1)}'", "L6cl8a", (("q", "q"), ("q", "q"))),
    "cqq3": (r"Q_{qq}^{(3)}", "L6cl8a", (("q", "q"), ("q", "q"))),
    "cqq31": (r"Q_{qq}^{(3)}'", "L6cl8a", (("q", "q"), ("q", "q"))),
    "clq1": (r"Q_{lq}^{(1)}", "L6cl8a", (("l", "l"), ("q", "q"))),
    "clq3": (r"Q_{lq}^{(3)}", "L6cl8a", (("l", "l"), ("q", "q"))),
    # (RR)(RR)
    "cee": (r"Q_{ee}", "L6cl8b", (("e", "e"), ("e", "e"))),
    "cuu": (r"Q_{uu}", "L6cl8b", (("u", "u"), ("u", "u"))),
    "cuu1": (r"Q_{uu}'", "L6cl8b", (("u", "u"), ("u", "u"))),
    "cdd": (r"Q_{dd}", "L6cl8b", (("d", "d"), ("d", "d"))),
    "cdd1": (r"Q_{dd}'", "L6cl8b", (("d", "d"), ("d", "d"))),
    "ceu": (r"Q_{eu}", "L6cl8b", (("e", "e"), ("u", "u"))),
    "ced": (r"Q_{ed}", "L6cl8b", (("e", "e"), ("d", "d"))),
    "cud1": (r"Q_{ud}^{(1)}", "L6cl8b", (("u", "u"), ("d", "d"))),
    "cud8": (r"Q_{ud}^{(8)}", "L6cl8b", (("u", "u"), ("d", "d"))),
    # (LL)(RR)
    "cle": (r"Q_{le}", "L6cl8c", (("l", "l"), ("e", "e"))),
    "clu": (r"Q_{lu}", "L6cl8c", (("l", "l"), ("u", "u"))),
    "cld": (r"Q_{ld}", "L6cl8c", (("l", "l"), ("d", "d"))),
    "cqe": (r"Q_{qe}", "L6cl8c", (("q", "q"), ("e", "e"))),
    "cqu1": (r"Q_{qu}^{(1)}", "L6cl8c", (("q", "q"), ("u", "u"))),
    "cqu8": (r"Q_{qu}^{(8)}", "L6cl8c", (("q", "q"), ("u", "u"))),
    "cqd1": (r"Q_{qd}^{(1)}", "L6cl8c", (("q", "q"), ("d", "d"))),
    "cqd8": (r"Q_{qd}^{(8)}", "L6cl8c", (("q", "q"), ("d", "d"))),
    # the scalar and tensor ones
    "cledq": (r"Q_{ledq}", "L6cl8d", (("l", "e"), ("d", "q"))),
    "cquqd1": (r"Q_{quqd}^{(1)}", "L6cl8d", (("q", "u"), ("q", "d"))),
    "cquqd8": (r"Q_{quqd}^{(8)}", "L6cl8d", (("q", "u"), ("q", "d"))),
    "cquqd11": (r"Q_{quqd}^{(1)}'", "L6cl8d", (("q", "u"), ("q", "d"))),
    "cquqd81": (r"Q_{quqd}^{(8)}'", "L6cl8d", (("q", "u"), ("q", "d"))),
    "clequ1": (r"Q_{lequ}^{(1)}", "L6cl8d", (("l", "e"), ("q", "u"))),
    "clequ3": (r"Q_{lequ}^{(3)}", "L6cl8d", (("l", "e"), ("q", "u"))),
}
# the Warsaw-basis name of each coefficient, which ./dim8 select prints beside it
DIM6_NAMES = {c: e[0] for c, e in DIM6_COEFF.items()}
# The Standard Model vertices that a coefficient moves only through an internal parameter of the model,
# which build/dim6_index.json lists under "rescaled" (validate/dim6_index.py), have the Dirac chains of
# those Standard Model vertices.  C_HBox moves every vertex with one Higgs boson through the normalisation
# of the Higgs field, rh1 = (C_HBox - C_HD/4) v^2/Lambda^2 in models/dim68_is, among them the Yukawa
# couplings, which join q to u, q to d and l to e.  They carry the Yukawa matrix of their fields, as the
# chains of the same fields do in DIM6_CHAINS (those of psi^2H^3), so that dim6_yukawa counts y_t alone.
# chains() registers them under the coefficient's name beside the chains of its own operator, which
# C_HBox, a bosonic operator, does not have.  C_HD rescales the same vertices, but as a coefficient of
# the input relations it is listed through the vertices that name it alone.
DIM6_RESCALED_CHAINS = {"cHbox": [(("q", "u"),), (("q", "d"),), (("l", "e"),)]}


def field(leg):
    """The field of the Murphy (or Warsaw) basis of a fermion leg with a chirality label: q or l
    for an L label, and u, d or e for an R label, by the class of the leg."""
    cls = CLASS[_parts(leg)[0]]
    if chirality(leg) == "L":
        return "q" if SECTOR[cls] == "q" else "l"
    return {"uq": "u", "dq": "d", "l": "e"}[cls]


def dim6_yukawa(names, pairing, light=False):
    """The fermion legs, as positions in names, that a pairing of the legs of a dimension-six vertex
    into its chains (_pairings) needs on a top line, or None when one of its chains carries a Yukawa
    matrix with no entry of order one (DIM6_CHAINS).  A chain of one field carries none.  A chain of
    q and u carries y_u, whose one entry of order one is y_t, so that its u leg must be a top quark.
    A chain of any other two fields carries y_d, y_e or y_u y_d^dag, none of which has one.  With
    light=True every chain counts at every generation, for the search that says why an operator has
    no tree."""
    top = []
    for i, j in pairing:
        pair = {field(names[i]), field(names[j])}
        if len(pair) == 1 or light:
            continue
        if pair != {"q", "u"}:
            return None
        top.append(i if field(names[i]) == "u" else j)
    return tuple(top)


def _side(name, bar):
    """The legs that a field of the Murphy basis gives a vertex: the FeynRules classes of its
    components, with the bar and the chirality of the field, as "uqbar:L" for qbar."""
    return frozenset(f"{c}{'bar' if bar else ''}:{CHIRALITY[name]}" for c in COMPONENTS[name])


def _way(pairs):
    """A way as chains() keeps it, its pairs in a fixed order."""
    return tuple(sorted(pairs, key=lambda pr: [sorted(s) for s in pr]))


def chains():
    """block -> the ways its fermion legs pair into Dirac chains of one generation: a set of ways,
    each a tuple of pairs (A, B), A and B the legs that the two fields of a chain give a vertex with
    the chirality of each field (_side), with the conjugate of every way for the h.c., which turns
    psibar_X Gamma psi_Y into psibar_Y Gamma' psi_X, so that each field keeps its chirality and
    changes its bar.  The dimension-eight blocks are read from the flavour pairs of
    gen/operators.py.  A charge-conjugated chain of the B-violating blocks, psi^T C Gamma chi, has
    two legs of one bar, and each leg takes the chirality of its field, which charge conjugation
    does not change, so the same rule holds with no balance of fermions against antifermions.  Every
    term of every operator gives one field per flavour index, so every block with fermion legs has
    its chains, and a block whose terms did not would be left out, which Cheapest.assign refuses.
    The dimension-six blocks are those of DIM6_CHAINS, and each dimension-six coefficient with fermion
    legs is a block of its own, keyed by its name, with the chains of its operator (DIM6_COEFF) and
    those of the Standard Model vertices it rescales (DIM6_RESCALED_CHAINS)."""
    if getattr(chains, "cache", None) is None:
        from operators import OPS
        out = {}
        for i, op in enumerate(OPS):
            if not op.flavor_pairs:
                continue
            # the pairs a delta identifies and, in the Yukawa-scaled mode, those a Yukawa matrix joins, which
            # are the chains of the fields as they carry flavour and need not be the bilinears as written
            pairs = op.flavor_pairs
            if emit_fr.FLAVOR == "mfv":
                same, spurions = emit_fr.mfv_structure(op)
                pairs = tuple(same) + tuple((a, b) for _, _, a, b in spurions)
            ways, ok = set(), True
            for t in op.terms:
                psis = [f for f in t.factors if isinstance(f, dsl.Psi)]
                by_gen = {f.gen: f for f in psis}
                if len(by_gen) != len(psis) or any(a not in by_gen or b not in by_gen for a, b in pairs):
                    ok = False
                    break
                for flip in (False, True):
                    ways.add(_way([tuple(_side(f.name, f.bar != flip) for f in (by_gen[a], by_gen[b]))
                                   for a, b in pairs]))
            if ok:
                out[f"L8op{i + 1}"] = ways
        for block, ops in DIM6_CHAINS.items():
            out[block] = {_way([(_side(x, not flip), _side(y, flip)) for x, y in op])
                          for op in ops for flip in (False, True)}
        for coeff, (_, _, op) in DIM6_COEFF.items():
            ops = ([op] if op else []) + DIM6_RESCALED_CHAINS.get(coeff, [])
            if ops:
                out[coeff] = {_way([(_side(x, not flip), _side(y, flip)) for x, y in o])
                              for o in ops for flip in (False, True)}
        chains.cache = out
    return chains.cache


def _pairings(names, pairs, free=None):
    """Each way of splitting the fermion legs, named as _side names them, into the pairs (A, B) of
    a way, a leg in A and a leg in B for each, as a tuple of index pairs into names."""
    free = tuple(range(len(names))) if free is None else free
    if not pairs:
        if not free:
            yield ()
        return
    (A, B), rest = pairs[0], pairs[1:]
    for i in free:
        if names[i] in A:
            for j in free:
                if j != i and names[j] in B:
                    for more in _pairings(names, rest, tuple(k for k in free if k not in (i, j))):
                        yield ((i, j),) + more


SCALARS = {"H", "G0", "GP", "GPbar"}           # the Higgs boson and the Goldstone bosons
BOSONS = {"A", "Z", "W", "Wbar", "G"} | SCALARS
# the Goldstone boson of each massive vector, by FeynRules label, so that a final-state W+, which
# enters as Wbar, has the G- label GPbar
GOLDSTONE = {"Z": "G0", "W": "GP", "Wbar": "GPbar"}
DIM6 = {"L6cl1": ("X^3", 0), "L6cl2": ("H^6", 6), "L6cl3": ("H^4D^2", 4), "L6cl4": ("X^2H^2", 2),
        "L6cl5": ("psi^2H^3", 3), "L6cl6": ("psi^2XH", 1), "L6cl7": ("psi^2H^2D", 2),
        "L6cl8a": ("psi^4", 0), "L6cl8b": ("psi^4", 0), "L6cl8c": ("psi^4", 0), "L6cl8d": ("psi^4", 0)}
# the largest number of gluon field strengths among the coefficients of a dimension-six class:
# Q_G (X^3), Q_HG (X^2H^2) and the chromomagnetic dipoles (psi^2XH)
DIM6_NG = {"L6cl1": 3, "L6cl4": 2, "L6cl6": 1}
# and the number of each coefficient, for QCD=0, which is zero for the coefficients not named here
DIM6_COEFF_NG = {"cG": 3, "cGtil": 3, "cHG": 2, "cHGtil": 2, "cuG": 1, "cdG": 1}


def dimension_six(block):
    """Whether block is a dimension-six class (DIM6) or a dimension-six coefficient (DIM6_COEFF), whose
    chains of two different fields carry a Yukawa matrix (dim6_yukawa)."""
    return block in DIM6 or block in DIM6_COEFF


def yukawa_chains(block):
    """Whether the chains of two different fields of a block carry a Yukawa matrix (dim6_yukawa): those of a
    dimension-six block, and of a dimension-eight one in the Yukawa-scaled mode of gen/emit_fr.py."""
    return dimension_six(block) or (emit_fr.FLAVOR == "mfv" and str(block).startswith("L8op"))


def dim6_higgs(block):
    """The number of Higgs fields of a dimension-six class or coefficient, that of its class."""
    return DIM6[block][1] if block in DIM6 else DIM6[DIM6_COEFF[block][1]][1]


CLASSES = {1: "X^4", 2: "H^8", 3: "H^6D^2", 4: "H^4D^4", 5: "X^3H^2", 6: "X^2H^4", 7: "X^2H^2D^2",
           8: "XH^4D^2", 9: "psi^2X^2H", 10: "psi^2XH^3", 11: "psi^2H^2D^3", 12: "psi^2H^5",
           13: "psi^2H^4D", 14: "psi^2X^2D", 15: "psi^2XH^2D", 16: "psi^2XHD^2", 17: "psi^2H^3D^2",
           18: "psi^4H^2", 19: "psi^4X", 20: "psi^4HD", 21: "psi^4D^2"}


class Cheapest:
    """Minimal lambda cost for a leg to reach a group of externals through SM vertices.  A fermion
    leg carries a generation label, since a fermion line ends on an external fermion with its label,
    and a chirality label, since a line joins two legs of one label at no cost and two labels only
    through the top mass (propagator()).  chains is the output of chains(), which is the default and
    covers every block with fermion legs.  light_yukawa=True also lets the Yukawa coupling and the
    mass of a light quark or a lepton be a route, and so the dimension-six chains that carry a light
    Yukawa coupling (dim6_yukawa), which ./dim8 select uses only to say why an operator has no
    tree."""

    def __init__(self, sm, chains=None, light_yukawa=False):
        self.sm = [tuple(sorted(v)) for v in sm]
        self.by = {}
        for v in self.sm:
            for f in set(v):
                for m in set(P._members(f)) | {f}:
                    self.by.setdefault(m, []).append(v)
        self.cache = {}
        self.ltab = {}
        # vertex() memoised by what decides it, while Frontier keeps its own frontiers in vcache
        self.vmemo = {}
        # the argument hides the function chains() of this module
        self.chains = globals()["chains"]() if chains is None else chains
        self.light_yukawa = light_yukawa

    def _cands(self, f):
        # sorted, so that among routes of equal cost the one printed does not depend on the
        # interpreter's string hashing, which changes from run to run
        f = fclass(f) if is_fermion(f) else f
        seen, out = set(), []
        for key in sorted(set(P._members(f)) | {f}):
            for v in self.by.get(key, ()):
                if v not in seen:
                    seen.add(v)
                    out.append(v)
        return out

    @staticmethod
    def weight(v):
        """The power of a Standard Model vertex.  A three-point vertex with a fermion pair counts
        lambda^-2, the top Yukawa coupling included.  A bosonic one carries a vev and counts
        lambda^-1 when it has one or three scalars (hVV, hhh, and the Goldstone vertices phi VV and
        h phi phi), and a momentum, lambda^-2, when it has none or two (VVV, and the derivative
        couplings h phi V and phi phi V).  A four-point vertex counts lambda^0.  On the vertices of
        the unitary gauge, where hVV and hhh are the only bosonic vertices with a scalar, this is
        the rule of the paper."""
        if len(v) == 3:
            if any(is_fermion(x) for x in v):
                return -2
            return -1 if sum(x in SCALARS for x in v) in (1, 3) else -2
        return 0

    def variants(self, v, f, group):
        """For each way the fermion line through v can run, (legs, insertions, label): the legs of
        v other than the one that joins the leg f, with a generation label and a chirality label on
        every fermion (sm_options), the mass insertions of the line from f (propagator()), whose
        number adds to the power, and the chirality label of the leg of v that joins f, None when
        that leg is a boson.  A Yukawa vertex is kept only on a top line (unless light_yukawa)."""
        af = anti(f)
        rest = list(v)
        for i, x in enumerate(rest):
            if (is_fermion(x) and fclass(x) == fclass(af)) if is_fermion(af) else P._same_field(x, af):
                rest.pop(i)
                break
        else:
            return
        ferms = [i for i, x in enumerate(rest) if is_fermion(x)]
        if not ferms:
            yield rest, (), None
            return
        gens = [generation(af)] if is_fermion(af) else sorted(generations(group, sector(rest[ferms[0]])))
        for g in gens:
            for way in sm_options(v, g, self.light_yukawa):
                ins, c = (), None
                if is_fermion(af):
                    c = way[fclass(af)]
                    ins = propagator(f, c, self.light_yukawa)
                    if ins is None:
                        continue
                out = list(rest)
                for i in ferms:
                    out[i] = tag(rest[i], g, way[fclass(rest[i])])
                yield out, ins, c

    def reach(self, f, group, up=None):
        """(cost, SM vertices used) for leg f to reach exactly the externals in group.  A mass
        insertion on the line into a vertex is listed after the vertex, as ("m_t",).  f is a leg
        with a generation and a chirality label (assign, variants), or the root of a tree, its first
        external particle, with neither (sm_power), or a class label, which tries each generation
        and, without a chirality label, each label, so that only the root enters its first vertex
        with the label of that vertex at no cost (propagator()).  up is what the vertex at the other
        end of a photon or Z line is (end_kind()), for the cancellation of a right-handed current
        against a W pair (cancellation()), and None for the line of an external particle or of an
        operator vertex, which is counted as it is."""
        if len(group) == 1 and matches(f, group[0]):
            return (0, ())
        if f not in NEUTRAL:
            up = None
        key = (f, group, up)
        if key in self.cache:
            return self.cache[key]
        if is_fermion(f):
            gens = generations(group, sector(f))
            if generation(f) is None:                    # a class label: each generation and label
                best = (INF, ())
                for g in sorted(gens):
                    for c in ([chirality(f)] if chirality(f) else labels(f)):
                        got = self.reach(tag(f, g, c), group)
                        if _better(got, best):
                            best = got
                self.cache[key] = best
                return best
            if generation(f) not in gens:
                self.cache[key] = (INF, ())
                return self.cache[key]
        self.cache[key] = (INF, ())
        best = (INF, ())
        for v in self._cands(anti(f)):
            w = self.weight(v)
            for rest, ins, c in self.variants(v, f, group):
                kd = end_kind(v, rest, c)
                got = self._split_group(w + len(ins) + cancellation(f, up, kd), (v,) + tuple((x,) for x in ins),
                                        rest, group, kd)
                if _better(got, best):
                    best = got
        self.cache[key] = best
        return best

    def _split_group(self, w, head, rest, group, kd=None):
        """(cost, SM vertices used) for the legs rest of a vertex of power w to reach the externals
        in group, head being the vertex and the mass insertions of the line into it, and kd what the
        vertex is at the end of a photon or Z line among rest (end_kind())."""
        best = (INF, ())
        if len(rest) < 2 or len(rest) > len(group):
            return best
        for parts in P._partitions(group, len(rest)):
            c, used = w + 4, head
            for i in range(len(rest)):
                ci, ui = self.reach(rest[i], parts[i], kd)
                c += ci
                used += ui
                if c >= INF:
                    break
            if c < INF and _better((c, used), best):
                best = (c, used)
        return best

    def _labels(self, block, legs):
        """The chirality labels of the fermion legs of a vertex of the block, each tuple of them
        with which the legs pair into the Dirac chains of the block, with the pairings (index pairs
        into the fermion legs) that do it, each with the legs it needs on a top line (dim6_yukawa,
        none at dimension eight), or None when the block has no chains.  A pairing of a
        dimension-six vertex with a chain that carries a light Yukawa coupling is left out unless
        light_yukawa.  Cached per vertex, since it holds for every external state."""
        ways = self.chains.get(block)
        if ways is None:
            return None
        key = (block, legs)
        if key not in self.ltab:
            idx = [i for i, x in enumerate(legs) if is_fermion(x)]
            out = []
            for chis in itertools.product(*(labels(legs[i]) for i in idx)):
                names = [f"{fclass(legs[i])}:{c}" for i, c in zip(idx, chis)]
                prs = set()
                for way in ways:
                    if 2 * len(way) != len(names):
                        continue
                    for pr in _pairings(names, list(way)):
                        top = dim6_yukawa(names, pr, self.light_yukawa) if yukawa_chains(block) else ()
                        if top is not None:
                            prs.add((pr, top))
                if prs:
                    out.append((chis, prs))
            self.ltab[key] = out
        return self.ltab[key]

    def assign(self, legs, externals, block=None):
        """The legs of an operator vertex with a generation label and a chirality label on every
        fermion, for each assignment in which the fermion legs pair into the Dirac chains of the
        operator, each chain of one generation, and take the chiralities of the fields of their
        chains (chains(), _labels), with the u leg of a dimension-six chain that carries y_u on a
        top quark.  Every block with fermion legs has its chains, the B-violating ones included, and
        a vertex of a block without them is refused rather than given a rule of its own."""
        idx = [i for i, x in enumerate(legs) if is_fermion(x)]
        if not idx:
            yield list(legs)
            return
        table = self._labels(block, tuple(legs))
        if table is None:
            raise ValueError(f"{block}: a vertex with fermion legs and no Dirac chains (chains())")
        gens = {s: sorted(generations(externals, s)) for s in ("q", "l")}
        choices = [[generation(legs[i])] if generation(legs[i]) is not None else gens[sector(legs[i])] for i in idx]
        for combo in itertools.product(*choices):
            chis = [cs for cs, prs in table
                    if any(all(combo[a] == combo[b] for a, b in pr) and all(("uq", combo[a]) in HEAVY for a in top)
                           for pr, top in prs)]
            for cs in chis:
                spec = list(legs)
                for i, g, c in zip(idx, combo, cs):
                    spec[i] = tag(legs[i], g, c)
                yield spec

    def vertex(self, legs, externals, block=None):
        """(cost, SM vertices used) of the cheapest tree through the vertex legs of the operator of
        the block whose legs reach the externals.  Memoised on what decides it, the legs, the
        externals, the Dirac chains of the block and whether it is of dimension six (dim6_yukawa),
        as Frontier.vertex_all is, so that the blocks that share a vertex search it once."""
        ways = self.chains.get(block)
        key = (tuple(legs), externals, frozenset(ways) if ways is not None else None, yukawa_chains(block))
        if key in self.vmemo:
            return self.vmemo[key]
        best = (INF, ())
        for spec in self.assign(legs, externals, block):
            for parts in P._partitions(externals, len(spec)):
                c, used = 0, ()
                for i in range(len(spec)):
                    ci, ui = self.reach(spec[i], parts[i])
                    c += ci
                    used += ui
                    if c >= INF:
                        break
                if c < INF and _better((c, used), best):
                    best = (c, used)
        self.vmemo[key] = best
        return best


def leading(verts, dim, n_higgs, assignments, cheap, block=None, rescaled=()):
    """(lambda power, p, vertex legs, SM vertices) of the cheapest tree through any of the vertices
    verts of the operator of the block, or None when it has no tree: every tree needs the Yukawa
    coupling or the mass of a light quark or a lepton, the mass because a line joins two legs of
    different chirality and the Yukawa coupling at a Standard Model vertex or, at dimension six, in
    the coefficient of a chain (dim6_yukawa), or the flavours of the external particles cannot be
    joined.  Among trees of equal power the one with the fewest SM vertices is kept, a top mass
    insertion counted as one.  ./dim8 select prints it beside each operator.  assignments is a
    list of external multisets, or a dict from multiset to the cost of the polarisation choice
    that gives it (channel_assignments), which the power then includes.  A Goldstone leg is not at
    the vacuum, so p counts the scalar legs.  rescaled lists those of verts that the operator moves
    only through an internal parameter of the model, Standard Model vertices times v^2/Lambda^2, as
    C_HBox moves h W W, h Z Z and the Yukawa couplings through the normalisation of the Higgs field
    (build/dim6_index.json, "rescaled").  Such a vertex counts as the Standard Model vertex does
    (Cheapest.weight) and four powers of lambda more, with p = 2 for the v^2 and one more where the
    Standard Model vertex itself carries a vev, so that lambda^(2m-6+p) holds for it too."""
    items = assignments.items() if isinstance(assignments, dict) else [(a, 0) for a in assignments]
    resc = {tuple(sorted(v)) for v in rescaled}
    best = None
    for legs in verts:
        if tuple(sorted(legs)) in resc:
            w0 = Cheapest.weight(tuple(legs))
            p, w = (3 if w0 == -1 else 2), w0 + 4
        else:
            p = n_higgs - sum(legs.count(s) for s in SCALARS)
            w = dim - 12 + 2 * len(legs) + p  # lambda^(2m-4+p) at dimension eight, lambda^(2m-6+p) at six
        for ext, cost in items:
            c, used = cheap.vertex(list(legs), ext, block)
            if c >= INF:
                continue
            if best is None or (w + c + cost, len(used)) < (best[0], len(best[3])):
                best = (w + c + cost, p, list(legs), used)
    return best


# three times the electric charge of each class of fermion, and the charge of each charged boson
CHARGE3 = {"uq": 2, "dq": -1, "l": -3, "vl": 0}
BOSON_CHARGE = {"W": 1, "Wbar": -1, "GP": 1, "GPbar": -1}


def conserving(ext, baryon_number=True):
    """Whether a tree can join the external particles ext (all incoming): their electric charge
    adds up to zero and, for the Standard Model and the operators that conserve baryon number
    (baryon_number=True), so do their baryon number and their lepton number, and each generation
    label has as many fermions as antifermions, quarks and leptons counted together.  Every vertex
    keeps the generation label along a fermion line, a Standard Model vertex since the CKM matrix is
    block diagonal in the labels and an operator vertex since each of its Dirac chains joins two
    fields of one generation, a lepton and a quark in some of them, so that a line joins a fermion
    and an antifermion of one label.  The searches skip an assignment that fails, which has no
    tree.  The B-violating operators conserve the charge alone."""
    q3 = baryons = leptons = 0
    flow = Counter()
    for x in ext:
        if is_fermion(x):
            base, bar = _parts(x)[:2]
            s = -1 if bar else 1
            q3 += s * CHARGE3[CLASS[base]]
            if SECTOR[CLASS[base]] == "q":
                baryons += s
            else:
                leptons += s
            flow[generation(x)] += s
        else:
            q3 += 3 * BOSON_CHARGE.get(x, 0)
    if q3:
        return False
    return not baryon_number or not (baryons or leptons or any(flow.values()))


def channel_slots(slots, marks=None):
    """Each external slot as a list of (label, cost): the particles it may be, at cost 0, and for a
    longitudinal W or Z ({0}) its Goldstone boson at cost 0 or the gauge boson itself at cost 1, one
    power of lambda for a polarisation vector of order M_W/E.  A transverse one ({T}) is the gauge
    boson at cost 0, as an unmarked one is."""
    out = []
    for names, mark in zip(slots, marks or [None] * len(slots)):
        if mark == "0":
            v = names[0]
            out.append([(GOLDSTONE[v], 0), (v, 1)])
        else:
            out.append([(x, 0) for x in names])
    return out


def channel_assignments(alts):
    """{external multiset: the smallest cost of a choice of channel_slots that gives it}."""
    out = {}
    for combo in P._product(alts):
        ext = tuple(sorted(x for x, _ in combo))
        cost = sum(k for _, k in combo)
        if ext not in out or cost < out[ext]:
            out[ext] = cost
    return dict(sorted(out.items()))


def sm_power(alts, cheap):
    """The power of the Standard Model amplitude of the channel, the smallest over the choices of
    channel_slots of the cost of the choice and the power of the cheapest Standard Model tree, or
    None when there is no tree.  A tree is rooted at its first external particle, which enters a
    Standard Model vertex without a propagator, so 4 is taken off the cost of the line, and which,
    a fermion, takes the chirality of the leg it enters (propagator()).  An assignment that no tree
    can join (conserving()) is skipped."""
    best = None
    for ext, cost in channel_assignments(alts).items():
        if not conserving(ext):
            continue
        c, _ = cheap.reach(anti(ext[0]), ext[1:])
        if c < INF and (best is None or c - 4 + cost < best):
            best = c - 4 + cost
    return best


def qcd_zero(proc):
    """True when the process string asks for QCD=0 (or QCD<=0, QCD==0), False when it sets no QCD
    order.  Any other QCD order is refused, since the cheapest-tree search does not track it."""
    import re
    m = re.findall(r"\bQCD\s*(<=|==|=|>=|<|>)\s*(\d+)", proc, re.I)
    if not m:
        return False
    if all(op in ("=", "==", "<=") and int(n) == 0 for op, n in m) or all(op == "<" and int(n) == 1 for op, n in m):
        return True
    raise ValueError(f"only QCD=0 is supported, not {' '.join(op + n for op, n in m)}")


def gluon_strengths(block_index):
    """block -> the largest number of gluon field strengths among its operators, from the encoding,
    with those of the dimension-six classes (DIM6_NG) and of each dimension-six coefficient
    (DIM6_COEFF_NG)."""
    from operators import OPS
    ng = {op.name: max(sum(1 for f in t.factors if isinstance(f, dsl.FS) and f.group == "G") for t in op.terms)
          for op in OPS}
    out = {e["block"]: max(ng.get(o, 0) for o in e["ops"]) for e in block_index}
    out.update(DIM6_NG)
    out.update({c: DIM6_COEFF_NG.get(c, 0) for c in DIM6_COEFF})
    return out


def sm_lines(proc, base_vertices, gauge="unitary"):
    """The Standard Model vertices a tree of the process may use: those of standard_model_vertices,
    with the Goldstone vertices in Feynman gauge and without the gluon vertices under QCD=0."""
    sm = P.standard_model_vertices(base_vertices, goldstones=(gauge == "feynman"))
    return [v for v in sm if "G" not in v] if qcd_zero(proc) else sm


def routes(proc, vertex_index, base_vertices, catalogue, block_index=None, gauge="unitary"):
    """(dim, class name) -> (lambda power, p, operator label, vertex legs, SM vertices) of the cheapest
    tree, and the number of external legs.  A polarised W or Z in the process is counted through
    channel_slots, and a longitudinal one needs the Feynman-gauge lists (gauge="feynman").  The
    assignments of the external particles that no tree can join are skipped (conserving())."""
    slots, marks = P.parse_process(proc, collapse=ROUTE_COLLAPSE, marks=True)
    if "0" in marks and gauge != "feynman":
        raise ValueError("a longitudinal W or Z ({0}) is counted through its Goldstone boson, which needs the "
                         "Feynman-gauge vertex lists build/vertex_index_fg.json and build/sm_vertices_fg.json "
                         "(--gauge feynman)")
    if any(marks):
        assignments = {a: c for a, c in channel_assignments(channel_slots(slots, marks)).items() if conserving(a)}
    else:
        assignments = sorted(e for e in {tuple(sorted(a)) for a in P._product(slots)} if conserving(e))
    sm = sm_lines(proc, base_vertices, gauge)
    if qcd_zero(proc):
        # g_s at every Standard Model vertex with a gluon, and at every gluon an operator vertex
        # has beyond its gluon field strengths
        ng = gluon_strengths(block_index if block_index is not None else
                             json.load(open(os.path.join(ROOT, "docs", "block_index.json"))))
        vertex_index = {b: [v for v in vs if v.count("G") <= ng.get(b, 0)] for b, vs in vertex_index.items()}
    cheap = Cheapest(sm, chains=chains())
    best = {}
    for block, verts in vertex_index.items():
        if block.startswith("L8op"):
            e = catalogue.get(block)
            if not e or e["b_violating"]:
                continue
            dim, key, n_higgs, label = 8, (8, e["cls"]), e["fields"]["N_H"], e["label"]
        elif block in DIM6:
            dim, (name, n_higgs), label = 6, DIM6[block], block
            key = (6, name)
        else:
            continue
        got = leading(verts, dim, n_higgs, assignments, cheap, block)
        if got is not None and (key not in best or (got[0], len(got[3])) < (best[key][0], len(best[key][4]))):
            best[key] = (got[0], got[1], label, got[2], got[3])
    return best, len(slots)


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 2
    proc = argv[1]
    gauge = argv[argv.index("--gauge") + 1] if "--gauge" in argv else "unitary"
    cat = {e["block"]: e for e in json.load(open(os.path.join(ROOT, "docs", "catalogue.json")))}
    # a process, a mark or a QCD order the counting refuses, and missing or incomplete Feynman-gauge
    # lists, stop with the reason rather than a traceback
    try:
        vi, base = P.load_data(ROOT, gauge=gauge)
        best, n = routes(proc, vi, base, cat, gauge=gauge)
        smlist = sm_lines(proc, base, gauge)
    except (ValueError, FileNotFoundError) as e:
        sys.exit(f"{proc}: {e}")
    if "--n" in argv:
        n = int(argv[argv.index("--n") + 1])
    slots, marks = P.parse_process(proc, collapse=ROUTE_COLLAPSE, marks=True)
    # The Standard Model amplitude of the channel, found with the same choices as the trees, as
    # ./dim8 select finds it, so that an unmarked W or Z, which the powers count as transverse, is
    # transverse here too: p p > h j j is lambda^3 where 2n-8 = 2, and u u~ > z h is lambda^1 (Z_T h).
    sm = sm_power(channel_slots(slots, marks), Cheapest(smlist, chains=chains()))
    transverse = any(m is None and any(x in GOLDSTONE for x in s) for s, m in zip(slots, marks))
    channel = any(marks) or transverse
    if sm is None:
        where = " at QCD=0" if qcd_zero(proc) else " in this channel" if channel else ""
        print(f"{proc}: {n} external legs, no Standard Model tree{where}, so M/MSM is taken against "
              f"lambda^(2n-8) = lambda^{2 * n - 8}")
        sm = 2 * n - 8
    else:
        print(f"{proc}: {n} external legs, Standard Model amplitude{' of the channel' if channel else ''} ~ "
              f"lambda^{sm} (2n-8 = {2 * n - 8})"
              + (", an unmarked W or Z being counted as transverse ({T})" if transverse else ""))
    for dim in (6, 8):
        print(f" dimension {dim}:")
        for key in sorted((k for k in best if k[0] == dim), key=lambda k: (best[k][0], str(k[1]))):
            tot, p, lab, legs, used = best[key]
            d = tot - sm
            name = key[1] if dim == 6 else CLASSES[key[1]]
            ratio = (f"E^{4 - d} v^{d - 2}/Lambda^2" if dim == 6 else f"E^{8 - d} v^{d - 4}/Lambda^4")
            smv = " + ".join("[" + " ".join(v) + "]" for v in used) or "contact"
            print(f"  lambda^{tot:<2d}  M/MSM ~ {ratio:18s} {name:12s} via {lab:24s} [{' '.join(legs)}] p={p}   SM vertices: {smv}")
    rest = [CLASSES[k] for k in CLASSES if (8, k) not in best]
    print("  dimension-eight classes with no tree (input relations only, or not reached):", ", ".join(rest))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
