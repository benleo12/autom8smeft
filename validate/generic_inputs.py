"""The Standard Model inputs at which a validation script decides whether a coupling or a vertex exists.

The default card, as SMEFTsim's, has the top and bottom quarks as the only massive fermions and a diagonal
CKM matrix (cabi = 0), and FeynRules writes the Yukawa couplings through the masses.  A coupling
proportional to a light Yukawa coupling or to the Cabibbo angle vanishes on that card without vanishing as
an expression: the flavour structures with Y_e on a lepton current, for one, vanish there for every lepton,
and the models must keep them for a card with massive leptons.  So a script that removes what vanishes, or
lists what exists, evaluates the inputs that are zero on the card at values of their own, between 0.1 and
0.3 (GeV for a mass, radians for cabi), fixed by the name, so that two models with the same inputs are
evaluated at the same point.  An input that is not zero on the card keeps its value, which the caller may
perturb.
"""
import hashlib
import os
import re

# the parameter blocks of the Wilson coefficients, whose values each script sets itself
COEFFICIENT_BLOCKS = ("DIM6", "DIM8", "DIM8F")


def generic_value(name, value, block=None):
    """The card value of an external input, or, when that is zero and the input is not a Wilson coefficient
    (an entry of COEFFICIENT_BLOCKS), a value of its own between 0.1 and 0.3 fixed by the name."""
    if value != 0 or block in COEFFICIENT_BLOCKS:
        return value
    h = hashlib.sha256(f"generic:{name}".encode()).digest()
    return 0.1 + 0.2 * int.from_bytes(h[:8], "big") / 2 ** 64


def zero_inputs(ufo, only=None):
    """{name: generic value} of the external inputs of a UFO that are zero on its card (the light Yukawa
    masses and cabi of the released models), read from its parameters.py, those of block `only` when it is
    given.  A restriction card written with them (validate/make_restriction.py NAME=VALUE) keeps the couplings
    these inputs carry, which MadGraph would otherwise remove with every vertex they alone make."""
    params = open(os.path.join(ufo, "parameters.py"), errors="replace").read()
    out = {}
    for name, value, block in re.findall(r"\w+ = Parameter\(name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*"
                                         r"value = ([^,]*),\s*texname = '[^']*',\s*lhablock = '(\w+)'", params):
        if block not in COEFFICIENT_BLOCKS and block != "DECAY" and only in (None, block) \
                and float(eval(value, {"__builtins__": {}})) == 0.0:
            out[name] = generic_value(name, 0.0, block)
    return out
