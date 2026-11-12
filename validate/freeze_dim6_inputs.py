#!/usr/bin/env python3
"""Fix the dimension-six coefficients of the input relations at zero in a dimension-eight-only model.

    validate/freeze_dim6_inputs.py <UFO dir>            in place, a step of examples/release_model.sh
    validate/freeze_dim6_inputs.py <UFO dir> --check    change nothing, and exit 1 if the step would

The input relations of both schemes are written in eight dimension-six coefficients as well as the
dimension-eight ones (gen/input_scheme.py), so FeynRules writes those eight into every model built on
an input-scheme base, as external parameters of block DIM6.  In a model without a dimension-six sector
of its own they must stay at zero.  Set alone, one of them shifts the couplings and rotates the fields
without the operator whose terms those shifts cancel against, which is half a calculation, and in the
{alpha, MZ, GF} scheme it moves M_W at 1/Lambda^2.  This step makes the eight internal parameters of
value zero, and takes block DIM6 out of the parameter-card template and the restriction cards, so that
no card can set them.  The scale of the input relations, L6 = Lam**(-2), is the model's one scale Lam
of block DIM8, which stays as it is.  The expressions of the input relations stay as FeynRules wrote
them, since nothing else needs changing: an internal parameter of value zero is what MadGraph already
makes of every shift that a restriction card switches off.

A model with more in block DIM6 than those eight (DIM6_IN_BASE of ./dim8) has a dimension-six sector of
its own, in which they are coefficients like the others, and is left as it is.  So the step can run on
every model that is released, and running it twice changes nothing.  It stops, changing nothing, when
one of the eight has a default other than zero, which would change the model, or when it cannot read
one of the parameters of the block.  Pure Python: it reads and rewrites text and imports nothing of
the model.
"""
import glob
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# a parameter of block DIM6 as FeynRules writes it, with what the internal parameter keeps
EXTERNAL = re.compile(r"^(?P<var>\w+) = Parameter\(name = '(?P<name>\w+)',(?P<sep>\s+)nature = 'external',\s+"
                      r"type = '(?P<type>\w+)',\s+value = (?P<value>[^,\s]+),\s+texname = (?P<tex>'[^\n]*'),\s+"
                      r"lhablock = 'DIM6',\s+lhacode = \[ [\d, ]+ \]\)", re.M)


def in_base():
    """The parameters every input-scheme model carries in its base, DIM6_IN_BASE of ./dim8, read from there
    so that the two lists cannot drift."""
    m = re.search(r"^DIM6_IN_BASE = \{([^}]*)\}", open(os.path.join(ROOT, "dim8")).read(), re.M)
    return set(re.findall(r'"(\w+)"', m.group(1)))


def internal(m):
    """The internal parameter of value zero that replaces the external one matched by EXTERNAL."""
    return (f"{m.group('var')} = Parameter(name = '{m.group('name')}',{m.group('sep')}nature = 'internal',"
            f"{m.group('sep')}type = '{m.group('type')}',{m.group('sep')}value = '0',"
            f"{m.group('sep')}texname = {m.group('tex')})")


def without_block(text):
    """The text of a card without its block DIM6, every other line as it was."""
    out, inside = [], False
    for line in text.split("\n"):
        block = re.match(r"\s*block\s+(\w+)", line, re.I)
        if block:
            inside = block.group(1).upper() == "DIM6"
            if inside:
                continue
        elif inside:
            if re.match(r"\s*\d+\s+\S+\s*#", line):
                continue
            inside = False
        out.append(line)
    return "\n".join(out)


def write(path, text):
    """Replace a file in one step, so that a run that stops leaves no file half written."""
    with open(path + ".tmp", "w", newline="") as f:
        f.write(text)
    os.replace(path + ".tmp", path)


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    ufo, check = os.path.abspath(args[0]), "--check" in argv
    path = os.path.join(ufo, "parameters.py")
    if not os.path.isfile(path):
        print(f"{ufo} has no parameters.py")
        return 2
    with open(path, newline="") as f:
        text = f.read()
    found = list(EXTERNAL.finditer(text))
    in_block = text.count("lhablock = 'DIM6'")
    if len(found) != in_block:
        print(f"{path}: {in_block} parameters of block DIM6, of which {len(found)} could be read: nothing changed")
        return 2
    names = {m.group("name") for m in found}
    if names - in_base():
        print(f"{os.path.basename(ufo)}: has a dimension-six sector of its own, left as it is")
        return 0
    off = [m.group("name") for m in found if float(m.group("value")) != 0.0]
    if off:
        print(f"{path}: default other than zero for {', '.join(off)}: nothing changed")
        return 2
    new = EXTERNAL.sub(internal, text)
    cards = {}
    for card in sorted(glob.glob(os.path.join(ufo, "restrict_*.dat"))) + [os.path.join(ufo, "param_card_template.dat")]:
        if os.path.isfile(card):
            with open(card, newline="") as f:
                old = f.read()
            stripped = without_block(old)
            if stripped != old:
                cards[card] = stripped
    if check:
        if found or cards:
            print(f"{os.path.basename(ufo)}: {len(found)} parameters of block DIM6 still external, and block DIM6 in "
                  f"{len(cards)} cards")
            return 1
        print(f"{os.path.basename(ufo)}: no parameter of block DIM6 is external, and no card holds the block")
        return 0
    if new != text:
        write(path, new)
    for card, stripped in cards.items():
        write(card, stripped)
    if found or cards:
        print(f"{os.path.basename(ufo)}: {len(found)} parameters of block DIM6 made internal, the coefficients at "
              f"zero, and the block taken out of {len(cards)} cards")
    else:
        print(f"{os.path.basename(ufo)}: nothing to do")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
