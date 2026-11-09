#!/usr/bin/env python3
"""Give the restriction cards that a release carries over the numbers of the model they now belong to.

    validate/rekey_cards.py <UFO dir> [--from <UFO dir it replaces>] <card> [<card> ...]

MadGraph reads a card by block and number, and the name after the # on each line is only a comment.  The
numbers of block DIM8 are positions in the encoding (emit_parameters in gen/emit_fr.py), so an operator
that changes between a real and a complex coefficient moves every later coefficient by one.  A card that
examples/release_model.sh does not write, such as one of ./dim8 select --card, comes over from the model
being replaced with the old numbers, and importing the model with it would silently keep other operators
than the ones its comments name.  This step reads each entry by its name and writes it with the number
that name has in parameters.py of the new model.

A card whose blocks, numbers and names are already those of the model is left as it is, byte for byte.
Otherwise a name the new model has keeps the value it had, and a coefficient that has changed between
real and complex passes its value on: a kept coefficient stays kept in its one entry or in its two.  The
values themselves carry no meaning, and the release gives the kept ones their placeholders in the next
step (validate/make_restriction.py --renew).  A coefficient the card does not list, an operator appended
to the encoding for one, is zero, since the card did not ask for it, and any other new parameter takes
its default.  An entry the model no longer has as an external parameter goes, as the dimension-six inputs
of a model that has fixed them at zero do, unless it is a coefficient that the card keeps, which stops
the release, since the card could no longer do what it says.  So does a line that cannot be read, or an
entry without a name.  Pure Python: it reads and writes text and imports nothing of the model.

A card also holds the Standard-Model inputs (the masses, the widths, the Cabibbo angle, the Yukawa
couplings), and MadGraph takes them as the defaults of the restricted model and removes the ones that are
zero.  A card written by ./dim8 select or validate/make_restriction.py holds the defaults of its model, so
when a release moves a default (the light fermion masses and the Cabibbo angle went to zero when the
defaults became SMEFTsim's) the card would keep the old one, and a run through it would not be at the
inputs of the model.  With --from, the model being replaced, an input the card holds at that model's
default takes the default of the new model, and an input the card holds at any other value was chosen and
keeps it.  Without --from every input keeps the value it had.
"""
import os
import re
import sys

# as validate/make_restriction.py reads the external parameters
EXTERNAL = re.compile(r"(\w+) = Parameter\(name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = ([^,]*),"
                      r"\s*texname = '[^']*',\s*lhablock = '(\w+)',\s*lhacode = \[ ([\d, ]+) \]")
BLOCK_ORDER = ["SMINPUTS", "MASS", "CKMBLOCK", "DIM6", "DIM8", "DIM8F", "YUKAWA"]
BLOCK = re.compile(r"\s*block\s+(\w+)", re.I)
ENTRY = re.compile(r"\s*((?:\d+\s+)+)([-+\d.eE]+)\s*#\s*(\w+)")
DECAY = re.compile(r"\s*decay\s+(\d+)\s+([-+\d.eE]+)\s*#\s*(\w+)", re.I)


def model_entries(ufo):
    """The external parameters of a UFO in the order of its parameters.py, as (block, number, name, default)."""
    with open(os.path.join(ufo, "parameters.py"), errors="replace") as fh:
        params = fh.read()
    out = []
    for _, name, value, block, codes in EXTERNAL.findall(params):
        out.append((block, " ".join(c.strip() for c in codes.split(",")), name, value.strip()))
    return out


def read_card(text):
    """(the lines before the first block, {name: (block, number, value as printed)}), or a ValueError."""
    head, entries, block = [], {}, None
    for line in text.split("\n"):
        if not line.strip() or line.lstrip().startswith("#"):
            if block is None:
                head.append(line)
            continue
        b = BLOCK.match(line)
        if b:
            block = b.group(1).upper()
            continue
        d = DECAY.match(line)
        m = ENTRY.match(line) if block is not None else None
        if d:
            entries[d.group(3)] = ("DECAY", d.group(1), d.group(2))
        elif m:
            entries[m.group(3)] = (block, " ".join(m.group(1).split()), m.group(2))
        else:
            raise ValueError(f"a line that cannot be read: {line.strip()}")
    return head, entries


def number(printed):
    try:
        return float(printed)
    except ValueError:
        raise ValueError(f"a value that cannot be read: {printed}") from None


def default(printed):
    """The default of a parameter as a card prints it.  A default that is not a plain number is zero, as
    in validate/make_restriction.py."""
    try:
        return f"{float(printed):.6e}"
    except ValueError:
        return f"{0.0:.6e}"


def is_coefficient(block, name):
    return (block in ("DIM8", "DIM8F") and name.startswith("c8")) or (block == "DIM6" and name != "Lam6")


def stale_inputs(entries, model, before):
    """The inputs a card holds at the default of the model being replaced (`before`, {name: default}, or
    None), where the new model has another default."""
    if before is None:
        return set()
    new_default = {n: d for _, _, n, d in model}
    return {n for n, (b, _, v) in entries.items()
            if not is_coefficient(b, n) and n in before and n in new_default
            and number(v) == number(default(before[n])) and number(default(new_default[n])) != number(v)}


def rekey(text, model, before=None):
    """The text of a card with the numbers of the model, and with the inputs of stale_inputs at the model's
    defaults, the same text when nothing has moved.  A ValueError says why the card cannot be carried over."""
    head, entries = read_card(text)
    follow = stale_inputs(entries, model, before)
    if not follow and {(n, b, c) for n, (b, c, _) in entries.items()} == {(n, b, c) for b, c, n, _ in model}:
        return text
    have = {n for _, _, n, _ in model}

    def value_of(block, name, dflt):
        if name in follow:
            return default(dflt)
        if name in entries:
            return entries[name][2]
        if not is_coefficient(block, name):
            return default(dflt)
        # the two entries of a complex coefficient from the one of a real coefficient, and the other way
        parts = []
        if name[-2:] in ("Re", "Im") and name[:-2] in entries:
            parts = [entries[name[:-2]][2]]
        parts += [entries[name + s][2] for s in ("Re", "Im") if name + s in entries]
        return next((p for p in parts if number(p) != 0.0), f"{0.0:.6e}")

    lost = [n for n, (b, _, v) in entries.items() if is_coefficient(b, n) and n not in have and number(v) != 0.0
            and not (n[-2:] in ("Re", "Im") and n[:-2] in have) and n + "Re" not in have]
    if lost:
        raise ValueError(f"it keeps what the model no longer has: {', '.join(sorted(lost))}")
    blocks = [b for b in BLOCK_ORDER if any(e[0] == b for e in model)]
    blocks += sorted({e[0] for e in model} - set(BLOCK_ORDER) - {"DECAY"})
    out = list(head)
    for b in blocks:
        out.append(f"Block {b} ")
        out += [f"  {c} {value_of(b, n, d)} # {n} " for blk, c, n, d in model if blk == b]
    out += [f"DECAY {c} {value_of('DECAY', n, d)} # {n} " for blk, c, n, d in model if blk == "DECAY"]
    return "\n".join(out) + ("\n" if text.endswith("\n") else "")


def main(argv):
    args = argv[1:]
    before = None
    if len(args) >= 2 and args[1] == "--from":
        old_model = model_entries(args[2])
        if not old_model:
            print(f"no external parameters in {os.path.join(args[2], 'parameters.py')}")
            return 2
        before = {n: d for _, _, n, d in old_model}
        args = args[:1] + args[3:]
    if len(args) < 2:
        print(__doc__)
        return 2
    model = model_entries(args[0])
    if not model:
        print(f"no external parameters in {os.path.join(args[0], 'parameters.py')}")
        return 2
    moved = 0
    for card in args[1:]:
        with open(card, newline="") as fh:
            old = fh.read()
        try:
            follow = sorted(stale_inputs(read_card(old)[1], model, before))
            new = rekey(old, model, before)
        except ValueError as e:
            print(f"{os.path.basename(card)}: {e}")
            return 1
        if follow:
            print(f"{os.path.basename(card)}: {len(follow)} inputs at the old defaults take the new ones ({', '.join(follow)})")
        if new != old:
            with open(card + ".tmp", "w", newline="") as fh:
                fh.write(new)
            os.replace(card + ".tmp", card)
            moved += 1
    print(f"{os.path.basename(os.path.normpath(args[0]))}: {moved} of {len(args) - 1} cards carried over with new numbers or inputs")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
