"""The two dimension-eight bases the models are written in.

The Murphy basis (arXiv:2005.00059) writes each of its fifteen operators of class 11, psi^2 H^2 D^3, with one
Higgs field that carries no derivative.  Set to its vacuum expectation value, that field leaves a vertex of two
fermions and one gauge or Higgs boson whose Feynman rule grows with the momenta, so that the two- and
three-point functions are not those of the field-space connections of the geometric SMEFT (arXiv:2001.01453).
The default basis replaces these fifteen by fifteen operators of the same class in which every Higgs field
carries a derivative, so that none of them has a vertex with fewer than four fields.  They are the operators that
arXiv:2306.00053 writes for this class, the class it finds to be the only one of the Murphy basis outside the
geometric SMEFT, extended to every fermion current: for each current, one with no derivative on the fermions,
    Q^{(g1)} = i(psibar gamma^mu psi)[(D^nu H)^dag D_(mu D_nu) H - (D_(mu D_nu) H)^dag D^nu H],
and one with the relative derivative on the fermions,
    Q^{(g2)} = i(psibar gamma^mu <->D_nu psi)[(D_mu H)^dag D_nu H + (D_nu H)^dag D_mu H],
with psibar <->D psi = psibar (D psi) - (D psibar) psi, the same with tau^I in both bilinears for the triplets
(g3, g4), and Q_{udH^2D^3}^{(g)} = i(ubar gamma^mu d)((D^nu Htilde)^dag D_(mu D_nu) H) + h.c.  Every other operator
is common to the two bases.

The two sets span the same operators up to the equations of motion and integration by parts: their contact
amplitudes of two fermions and two Higgs bosons have the same span, of the dimension the Hilbert series gives,
with one, two and three generations (tests/test_geo_basis.py).  On those amplitudes
    Q^{(1)} = Q^{(g1)}/4 - Q^{(g2)}/4,    Q^{(2)} = -Q^{(g1)}/4 - Q^{(g2)}/4
for each singlet current, the same for the triplets (3, 4 and g3, g4), and Q_{udH^2D^3} = -Q_{udH^2D^3}^{(g)}/2,
so that a point C^{(1)}, C^{(2)} of the Murphy basis has C^{(g1)} = (C^{(1)} - C^{(2)})/4 and
C^{(g2)} = -(C^{(1)} + C^{(2)})/4 in the default one.  The rest of the change of basis moves the coefficients of
other operators, which these amplitudes do not see: those of classes with more fields, and, through the Higgs
mass term of the equations of motion, dimension-six ones at order m_H^2/Lambda^4.

DIM8_BASIS=murphy writes the models in the Murphy basis, under the names of the default models with the
suffix _murphy.  The encoding, gen/operators.py, holds both sets, and the vertex cache both sets of blocks.
"""
from __future__ import annotations

import os
import re

BASES = ("geo", "murphy")
DEFAULT = "geo"
SUFFIX = {"geo": "", "murphy": "_murphy"}
# the name of each basis in what the commands print
NAME = {"geo": "default", "murphy": "Murphy"}

# class 11 of the Murphy basis, and the operators of the default basis that replace them, in the same order
MURPHY = ("c8l2H2D3x1", "c8l2H2D3x2", "c8l2H2D3x3", "c8l2H2D3x4", "c8e2H2D3x1", "c8e2H2D3x2",
          "c8q2H2D3x1", "c8q2H2D3x2", "c8q2H2D3x3", "c8q2H2D3x4", "c8u2H2D3x1", "c8u2H2D3x2",
          "c8d2H2D3x1", "c8d2H2D3x2", "c8udH2D3")
GEO = ("c8l2H2D3g1", "c8l2H2D3g2", "c8l2H2D3g3", "c8l2H2D3g4", "c8e2H2D3g1", "c8e2H2D3g2",
       "c8q2H2D3g1", "c8q2H2D3g2", "c8q2H2D3g3", "c8q2H2D3g4", "c8u2H2D3g1", "c8u2H2D3g2",
       "c8d2H2D3g1", "c8d2H2D3g2", "c8udH2D3g")
ONLY = {"murphy": frozenset(MURPHY), "geo": frozenset(GEO)}


def basis(b=None):
    """The basis asked for: b, or DIM8_BASIS, or the default."""
    b = b or os.environ.get("DIM8_BASIS") or DEFAULT
    if b not in BASES:
        raise SystemExit(f"DIM8_BASIS={b}: the bases are {', '.join(BASES)}")
    return b


def left_out(b=None):
    """The coefficients of the operators that belong to the other basis."""
    return ONLY["murphy" if basis(b) == "geo" else "geo"]


def of_wcs(wcs):
    """The basis a set of coefficients belongs to: "murphy", "geo", or None for the operators common to both."""
    wcs = set(wcs)
    for b in BASES:
        if wcs & ONLY[b]:
            return b
    return None


def in_basis(wcs, b=None):
    """Does an operator, or a block, with these coefficients belong to basis b?"""
    return not set(wcs) & left_out(b)


def ops(all_ops, b=None):
    """The operators of basis b, in the order of the encoding."""
    out = left_out(b)
    return [o for o in all_ops if o.wc not in out]


def model_name(name, b=None):
    """The name of a released model in basis b."""
    return name + SUFFIX[basis(b)]


def of_model(model):
    """The basis of a model directory, read off the class-11 coefficients its couplings carry, each with
    its flavour structures and its Re and Im parts.  parameters.py is no guide, since it declares every
    coefficient of the encoding, those of both bases, whatever blocks were written.  A model whose
    couplings carry neither set (a model cut down to a process) is taken to be in the default."""
    path = os.path.join(model, "couplings.py")
    text = open(path, errors="replace").read() if os.path.exists(path) else ""
    names = {re.sub(r"F\w*$", "", re.sub(r"(Re|Im)$", "", n)) for n in re.findall(r"\bc8(?:[lequd]2|ud)H2D3\w*", text)}
    found = [b for b in BASES if names & ONLY[b]]
    if len(found) > 1:
        raise SystemExit(f"{model}: its couplings carry class-11 coefficients of both bases")
    return found[0] if found else DEFAULT
