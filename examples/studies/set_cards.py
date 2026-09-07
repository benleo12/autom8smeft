#!/usr/bin/env python3
"""Edit a generated MadGraph process directory's cards in place, without the launch prompt.

    examples/studies/set_cards.py <process dir> "NAME=VALUE" ["NAME=VALUE" ...]

Each assignment is looked up in Cards/param_card.dat (matched on the parameter name in the
trailing comment, which is how the UFO writes it) and then in Cards/run_card.dat (matched on the
"= name" field).  Names are matched up to case and up to the "__2" suffix MadGraph appends when
a parameter name collides with one it already has: the scale Lam is written into the card as
"lam__2" because the dimension-six block already carries a Lam6, so a literal match would miss
it.  The name "dim8_all" is special: it sets every dimension-eight Wilson
coefficient of block DIM8 except the scale Lam, which is what the studies mean by "every
coefficient at 1".  Unknown names are an error, not a warning: MadGraph's interactive `set`
accepts a misspelt parameter silently and the run then quietly uses the default, which has cost
this project a day before.  Prints one line per card entry it changed.
"""
import re, sys, os


def norm(n):
    """Card name to lookup key: MadGraph lowercases and may append __2 on a name collision."""
    return re.sub(r"__\d+$", "", n).lower()


def edit_param(path, asg):
    keys = {norm(k): k for k in asg}
    lines, hits = open(path).read().split("\n"), {}
    for i, l in enumerate(lines):
        m = re.match(r"^(\s*(?:\d+\s+)+)([-\deE.+]+)(\s*#\s*(\w+))", l)
        if not m:
            continue
        name, key = m.group(4), norm(m.group(4))
        val = asg.get(keys.get(key, ""))
        if val is None and "dim8_all" in asg and key.startswith("c8") and key != "lam":
            val = asg["dim8_all"]
        if val is not None:
            lines[i] = f"{m.group(1)}{float(val):.6e}{m.group(3)}"
            hits[keys.get(key, name)] = float(val)
    open(path, "w").write("\n".join(lines))
    return hits


# Run-card entries MadGraph accepts but does not print in the default card: absent lines are
# appended.  hel_recycling is the one that matters here: the helicity recycler's amplitude
# splitter fails on the dimension-eight Lorentz structures of the full model ("split amp are not
# supported for spin2 and 3/2", from hel_recycle.py), so every study run switches it off.
HIDDEN = {"hel_recycling"}


def edit_run(path, asg):
    keys = {norm(k): k for k in asg}
    lines, hits = open(path).read().split("\n"), {}
    present = {norm(m.group(1)) for l in lines for m in [re.match(r"^\s*\S+\s*=\s*(\w+)", l)] if m}
    for k in asg:
        if norm(k) in HIDDEN and norm(k) not in present:
            lines.append(f" {asg[k]} = {norm(k)} ! appended by set_cards.py"); hits[k] = asg[k]
    for i, l in enumerate(lines):
        m = re.match(r"^(\s*)(\S+)(\s*=\s*)(\w+)(\s.*)?$", l)
        if not m or norm(m.group(4)) not in keys:
            continue
        name, val = keys[norm(m.group(4))], asg[keys[norm(m.group(4))]]
        lines[i] = f"{m.group(1)}{val}{m.group(3)}{m.group(4)}{m.group(5) or ''}"
        hits[name] = val
    open(path, "w").write("\n".join(lines))
    return hits


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    d, asg = argv[1], dict(a.split("=", 1) for a in argv[2:])
    pc, rc = os.path.join(d, "Cards", "param_card.dat"), os.path.join(d, "Cards", "run_card.dat")
    hits = edit_param(pc, asg)
    n8 = sum(1 for k in hits if norm(k).startswith("c8") and k not in asg)
    hits.update(edit_run(rc, asg))
    missing = [k for k in asg if k not in hits and k != "dim8_all"]
    if missing:
        print("set_cards: no such parameter or run-card entry:", ", ".join(missing))
        return 2
    if "dim8_all" in asg and not n8:
        print("set_cards: dim8_all requested but the model has no c8 coefficients left")
        return 2
    named = {k: v for k, v in hits.items() if k in asg}
    print(f"set_cards: {n8} dimension-eight coefficients at {asg.get('dim8_all', '-')}"
          + (", " + ", ".join(f"{k}={v}" for k, v in sorted(named.items())) if named else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
