#!/usr/bin/env python3
"""Where the catalogue comes from, and what to say when a file is not there.

``docs/catalogue.json`` is the catalogue: one entry per operator of the Murphy basis, in block
order, with the label, the coefficient name, the class, the baryon number, the conjugacy, the CP
parity and the field content.  ``gen/operators.py`` is the same list as objects of gen/dsl.py,
which is the form the generation chain reads.  Both ship, and a script that needs only the
classification calls ``derived()``.

``docs/murphy_parsed.json`` is a working file of the authors that additionally carries the
typeset form of each operator.  It is not distributed.  A script that needs it calls
``parsed()``, which exits with that statement rather than a traceback when the file is absent.
"""
from __future__ import annotations

import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVED = os.path.join(ROOT, "docs", "catalogue.json")
PARSED = os.path.join(ROOT, "docs", "murphy_parsed.json")

NEED_SOURCE = """\
This check reads docs/murphy_parsed.json, a working file of the authors that is not distributed
with this repository.  Everything that needs the operators themselves reads gen/operators.py,
and everything that needs only the classification reads docs/catalogue.json.  Both ship.
"""


def derived():
    """The catalogue: label, wc, block, cls, b_violating, plus_hc, hc_mode, conjugacy, cp,
    n_terms, fields, gens.  Falls back to the authors' working file where only that exists."""
    if os.path.exists(DERIVED):
        return json.load(open(DERIVED))
    if os.path.exists(PARSED):
        return json.load(open(PARSED))
    sys.exit("no catalogue: expected docs/catalogue.json.\n" + NEED_SOURCE)


def parsed():
    """The authors' working file, with the typeset form of each operator.  Exits with a
    statement if it is absent, which is the normal state of a clone."""
    if os.path.exists(PARSED):
        return json.load(open(PARSED))
    sys.exit(NEED_SOURCE)


def have_source() -> bool:
    return os.path.exists(PARSED)
