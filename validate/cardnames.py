#!/usr/bin/env python3
"""Turn catalogue coefficient names into the names a param card actually has.

A complex Wilson coefficient is not an external parameter of the UFO: it is built from a real and
an imaginary part, so ``c8leq2HDx1`` appears in the card as ``c8leq2HDx1Re`` and
``c8leq2HDx1Im``.  ``docs/block_index.json`` carries the base name, and set_cards.py treats an
unknown name as an error on purpose, so anything that selects operators by name has to expand
the complex ones first.  This is the single place that knows how.
"""
from __future__ import annotations

import os
import re

_CACHE: dict = {}


def card_names(model: str) -> set:
    """Every parameter name the model's param card template carries."""
    model = os.path.abspath(model)
    if model not in _CACHE:
        p = os.path.join(model, "param_card_template.dat")
        if not os.path.exists(p):
            p = os.path.join(model, "restrict_all.dat")
        txt = open(p).read()
        # a card line is "  61 0.000000e+00 # c8q2W2Dx1  Q_{q^2W^2D}^{(1)} (L8op45, class 14)",
        # so the name is the first word after the hash and NOT the whole rest of the line
        _CACHE[model] = {m.group(1) for m in re.finditer(r"^\s*\d+\s+\S+\s*#\s*(\w+)", txt, re.M)}
    return _CACHE[model]


def expand(model: str, names) -> list:
    """The card entries for these coefficients: the name itself, or its Re and Im parts."""
    have = card_names(model)
    out = []
    for n in names:
        if n in have:
            out.append(n)
        elif n + "Re" in have or n + "Im" in have:
            out += [x for x in (n + "Re", n + "Im") if x in have]
    return out
