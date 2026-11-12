#!/usr/bin/env python3
"""Write a MadGraph restriction card that keeps a chosen set of dimension-eight operators.

    validate/make_restriction.py <UFO dir> <card name> <selector> [<selector> ...]
    validate/make_restriction.py --renew <UFO dir>

Selectors, mixed freely:
    Q_{G^2H^4}^{(1)}       an operator name as in docs/block_index.json (Murphy's notation), with every
                           flavour structure it has
    c8G2H4x1               a Wilson-coefficient name (complex ones keep both Re and Im parts): the
                           operator's own coefficient, or that of one of its flavour structures in block
                           DIM8F, such as c8quH5FU
    L8op593  or  593       a block number
    cls:6                  every operator of a class number (Murphy's class numbering)
    all                    every dimension-eight operator (a card that keeps everything)
    c10H6x1                in a model of order N (gen/towers.py), the coefficient of a member of a tower
    dim6                   every dimension-six coefficient, if the model has them
    dim6:cHq1              one named dimension-six coefficient
    MB=0                   an input that is not a coefficient (a mass, a width, a Yukawa coupling, an
                           input of the scheme) at a value other than the model's default.  MB=0 makes
                           the b quark massless while its Yukawa coupling, ymb, keeps its default, and
                           MadGraph then counts b in p and j (the five-flavour scheme)

In a model of order N each selector that keeps a dimension-eight coefficient c8<label> also keeps the
members of its tower, c10<label>, c12<label>, ..., since together they make one connection of the geometric
SMEFT.  cls:N and all also keep the members that have no operator of dimension eight: the towers of
Q_{WH^6D^2}^{(5),(6)} in class 8 and the four-lepton members of block GEOGF, which enter only the G_F relation,
in the class of Q_{l^4H^2}.

Writes <UFO dir>/restrict_<card name>.dat.  Importing the model as
    import model <UFO dir>-<card name>
makes MadGraph drop every coefficient that the card sets to zero, together with every vertex
whose couplings then vanish, so the resulting model contains only the kept operators and the
Standard Model, whatever process is generated afterwards.  Pure Python: no Mathematica needed.

MadGraph's rules for the card (models/import_ufo.py, detect_special_parameters,
detect_identical_parameters and detect_identical_couplings): a parameter set to 0 is removed from
the model, one set to exactly 1 is frozen at 1, external parameters of one block whose values are
equal or opposite are merged into one, a coupling that vanishes at the values of the card is removed
with its vertices, and couplings of one order whose values at the card agree up to sign, to about
ten digits, are fused into one, which keeps the formula of the first of them at any values of the
run.  So the values of the kept coefficients must satisfy no relation that does not hold for every
value.  An arithmetic sequence satisfies many, since 3 x 0.106 = 2 x 0.159 fuses -3 cHbox with 2 cee,
and so do the multiples of one number taken modulo 1.  The kept coefficients therefore get values
between 0.1 and 0.9 from a random generator seeded with the name of the coefficient, thirteen digits
of them, so that a coefficient has the same value on every card and a card written twice is the same
file, and a value that another parameter of the same block already has, of either sign, is drawn
again.  They carry no meaning: set the physical values in the run's param_card.dat as usual.  The
dimension-six coefficients of a model that has them are set to zero in the same way unless they
are selected with dim6 or dim6:<name>, and the selected ones get such values too.
Everything else (masses, inputs, the scale Lam) is copied from the UFO's defaults, unless
a NAME=VALUE selector sets it.

--renew gives the kept coefficients of every restriction card of a model those values, whatever
wrote the card, and leaves what each card keeps and every other line as they are.  The release runs
it on the cards it carries over from the model it replaces, which an older version may have written.
"""
import glob, json, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, os.path.join(ROOT, "gen"))
# a parameter line of a card: what comes before the value, the value, what comes after it, the name
CARD_LINE = re.compile(r"^(\s*(?:\d+\s+)+)([-\deE.+]+)(\s*#\s*(\w+).*)$")


def is_coefficient(block, name):
    """Whether an entry of a card is a coefficient, which a card keeps or zeroes.  The scale Lam shares
    block DIM8 and must stay."""
    return (block in ("DIM8", "DIM8F") and name.startswith("c8")) or block == "DIM6" or is_member(block, name)


# the blocks of the coefficients of the towers of a model of order N (gen/towers.py, gen/input_scheme.py)
TOWER_BLOCK = re.compile(r"DIM(1[0-9]|[2-9][0-9])F?|GEOGF")


def is_member(block, name):
    """Whether an entry of a card is the coefficient of a member of a tower, c<d><label> with d >= 10."""
    return bool(block and TOWER_BLOCK.fullmatch(block) and re.match(r"c\d+[A-Za-z]", name))


def label(name):
    """The label of a coefficient: c10H6x1 and c8H6x1 have the label H6x1."""
    return re.match(r"c\d+(.*)", name).group(1)


def placeholder(name, taken):
    """The value of a kept coefficient as the card prints it, with thirteen digits, and in the set of
    the absolute values its block already holds, which it skips.  Between 0.1 and 0.9 it is neither
    of the values that MadGraph treats apart, 0 and 1."""
    rnd = random.Random(name)
    while True:
        text = f"{0.1 + 0.8 * rnd.random():.12e}"
        if float(text) not in taken:
            taken.add(float(text))
            return text


def renew(ufo):
    """--renew: see the docstring of the file."""
    cards, changed = sorted(glob.glob(os.path.join(ufo, "restrict_*.dat"))), 0
    for card in cards:
        with open(card, newline="") as f:
            old = f.read()
        lines, block, kept, taken = old.split("\n"), None, [], {}
        for i, line in enumerate(lines):
            b = re.match(r"\s*block\s+(\w+)", line, re.I)
            if b:
                block = b.group(1).upper()
                continue
            m = CARD_LINE.match(line)
            if m and not is_coefficient(block, m.group(4)):
                taken.setdefault(block, set()).add(abs(float(m.group(2))))
            elif m and float(m.group(2)) != 0.0:
                kept.append((i, block, m))
        for i, blk, m in kept:
            lines[i] = m.group(1) + placeholder(m.group(4), taken.setdefault(blk, set())) + m.group(3)
        new = "\n".join(lines)
        if new != old:
            with open(card + ".tmp", "w", newline="") as f:
                f.write(new)
            os.replace(card + ".tmp", card)
            changed += 1
    print(f"{os.path.basename(ufo)}: new placeholder values in {changed} of {len(cards)} restriction cards")
    return 0


def main(argv):
    if len(argv) == 3 and argv[1] == "--renew":
        return renew(os.path.abspath(argv[2]))
    # A card with no selector reaches "nothing to keep" below, which is what ./dim8 select --card passes on
    # for a selection that holds nothing.
    if len(argv) < 3:
        print(__doc__); return 2
    ufo, name, selectors = os.path.abspath(argv[1]), argv[2], argv[3:]
    # the operators of the model's basis (gen/basis.py): class 11 in the default form or in the Murphy basis's
    import basis
    mb = basis.of_model(ufo)
    index = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    other = {k for e in index if not basis.in_basis(e["wcs"], mb) for k in e["ops"] + e["wcs"] + [e["block"], e["block"][4:]]}
    index = [e for e in index if basis.in_basis(e["wcs"], mb)]
    by_block = {e["block"]: e for e in index}
    by_op = {op: e for e in index for op in e["ops"]}
    by_wc = {wc: e for e in index for wc in e["wcs"]}
    # the two parts of a complex coefficient, each a card entry of its own (the CP cards keep one of them)
    for e in index:
        if e.get("hc_mode") == "complex":
            for w in e["wcs"]:
                by_wc[w + "Re"] = by_wc[w + "Im"] = e
    # the coefficients of the flavour structures, and the names of their Re and Im pairs
    for e in index:
        for n in e.get("flavour", []):
            by_wc[n] = e
            by_wc.setdefault(re.sub(r"(Re|Im)$", "", n), e)
    every = lambda e: set(e["wcs"]) | set(e.get("flavour", []))
    params = open(os.path.join(ufo, "parameters.py")).read()
    ufo_dim8 = re.findall(r"name = '(c8\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,\s*texname = '[^']*',\s*lhablock = 'DIM8F?',\s*lhacode = \[ (\d+) \]", params)
    ufo_names = {n for n, _ in ufo_dim8}
    if not ufo_names:
        print("no DIM8 external parameters found in", ufo); return 2
    # the members of the towers, in a model of order N
    members = re.findall(r"name = '(c\d+\w*)',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,\s*texname = '[^']*',"
                         r"\s*lhablock = '(\w+)'", params)
    members = sorted(n for n, blk in members if is_member(blk, n))

    def member_class(n):
        """The class of the member's operator of dimension eight, or for a member without one, the class of the
        operators whose labels share its stem (WH4D2x5 that of WH4D2x1, l4H2x3Fx00 that of l4H2x1)."""
        rest = label(n)
        for cand in (rest, re.sub(r"(Re|Im)$", "", rest), re.sub(r"F\w*$", "", rest)):
            if "c8" + cand in by_wc:
                return by_wc["c8" + cand]["cls"]
        stem = re.sub(r"x\w*$", "x", rest)
        hits = {e["cls"] for w, e in by_wc.items() if w.startswith("c8" + stem)}
        if len(hits) != 1:
            sys.exit(f"the member {n} belongs to no single class: {sorted(hits)}")
        return hits.pop()
    cls_of = {n: member_class(n) for n in members}
    # The dimension-six sector, when the model carries it.
    ufo_dim6 = re.findall(
        r"name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,"
        r"(?:\s*texname = '[^']*',)?\s*lhablock = 'DIM6'", params)
    # every external parameter, as (variable, name, default, block, codes), and the inputs among them
    ext = re.findall(r"(\w+) = Parameter\(name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = ([^,]*),\s*texname = '[^']*',\s*lhablock = '(\w+)',\s*lhacode = \[ ([\d, ]+) \]", params)
    inputs = {pname for _, pname, _, blk, _ in ext if not is_coefficient(blk, pname)}

    wanted_wcs, blocks, keep6, values, wanted_members = set(), [], set(), {}, set()
    for s in selectors:
        if "=" in s:
            pname, _, v = s.partition("=")
            if pname not in inputs:
                print("not an input of this model (a mass, a width, a Yukawa coupling or an input of the scheme):", pname)
                return 2
            try:
                values[pname] = float(v)
            except ValueError:
                print("not a number:", s); return 2
        elif s == "all":
            for e in index: wanted_wcs |= every(e); blocks.append(e["block"])
            wanted_members |= set(members)
        elif s.startswith("cls:"):
            hits = [e for e in index if e["cls"] == int(s[4:])]
            if not hits: print("no operators in class", s[4:]); return 2
            for e in hits: wanted_wcs |= every(e); blocks.append(e["block"])
            wanted_members |= {n for n in members if cls_of[n] == int(s[4:])}
        elif s == "dim6":
            if not ufo_dim6:
                print("this model has no DIM6 coefficients"); return 2
            keep6 |= set(ufo_dim6)
        elif s.startswith("dim6:"):
            if s[5:] not in ufo_dim6:
                print("not a DIM6 coefficient of this model:", s[5:]); return 2
            keep6.add(s[5:])
        elif s in by_op:
            wanted_wcs |= every(by_op[s]); blocks.append(by_op[s]["block"])
        elif s in by_wc:
            wanted_wcs.add(s); blocks.append(by_wc[s]["block"])
        elif s in by_block or ("L8op" + s) in by_block:
            e = by_block.get(s) or by_block["L8op" + s]
            wanted_wcs |= every(e); blocks.append(e["block"])
        elif s in members:
            wanted_members.add(s)
        elif s in other:
            print(f"{s} belongs to the other basis: this model holds class 11 in the "
                  + ("Murphy basis" if mb == "murphy" else "default basis") + " (gen/basis.py)"); return 2
        else:
            print("unknown selector:", s, "(operator name, coefficient, block number, cls:N, all or NAME=VALUE)"); return 2
    # complex coefficients appear in the UFO as <wc>Re and <wc>Im; real ones as <wc>
    keep = sorted(n for n in ufo_names if n in wanted_wcs or n[:-2] in wanted_wcs and n[-2:] in ("Re", "Im"))
    not_in_ufo = sorted(w for w in wanted_wcs if w not in ufo_names and w + "Re" not in ufo_names)
    if not_in_ufo:
        print("WARNING: not present in this UFO (its operator blocks were not included when the UFO was written):", ", ".join(not_in_ufo))
    # a member goes with its operator of dimension eight
    keep_t = sorted(n for n in members if n in wanted_members or label(n) in {label(k) for k in keep})
    if not keep and not keep6 and not keep_t:
        print("nothing to keep"); return 2

    # A partial UFO still carries the whole basis in parameters.py, so a coefficient being there
    # does not mean any vertex uses it.  Restricting to operators with no vertices leaves a model
    # whose couplings never carry NP, and MadGraph then rejects "NP^2==2" with "model order NP^2
    # not valid for this model".  That message does not say that the block was not built, so this
    # case is reported here with its reason.
    # A complex coefficient reaches the couplings as its base name, an internal parameter built
    # from the external <name>Re and <name>Im, so the parts are checked through the base.
    used = set(re.findall(r"\bc8\w+\b", open(os.path.join(ufo, "couplings.py")).read()))
    live = [n for n in keep if n in used or re.sub(r"(Re|Im)$", "", n) in used]
    if keep_t:
        # a member of block GEOGF has no vertex and enters the couplings through the inputs, the internal
        # parameters, so a member counts as used when it appears in either
        values_t = " ".join(re.findall(r"nature = 'internal',\s*type = '\w+',\s*value = '([^']*)'", params))
        used_t = set(re.findall(r"\bc\d+[A-Za-z]\w*\b", open(os.path.join(ufo, "couplings.py")).read() + " " + values_t))
        live_t = [n for n in keep_t if n in used_t or re.sub(r"(Re|Im)$", "", n) in used_t]
        if len(live_t) < len(keep_t):
            print(f"note: {len(keep_t) - len(live_t)} of the {len(keep_t)} selected members of the towers enter no coupling of "
                  f"this UFO and are set to zero with the rest: {', '.join(n for n in keep_t if n not in live_t)[:300]}")
        keep_t = live_t
    if not live and not keep6 and not keep_t:
        print("WARNING: none of the kept coefficients appears in any vertex of this UFO, so the")
        print("         restricted model will have no NP coupling order at all and orders like")
        print("         NP^2==2 will be rejected.  Write the UFO with these operator blocks first.")
        return 2
    if keep and len(live) < len(keep):
        # Coefficients with no vertex are set to zero like the rest: a placeholder value would
        # change nothing in MadGraph and would make the card's "kept" count a lie.  The usual
        # reasons are the baryon-number-violating blocks (675 to 734, not in the shipped model)
        # and the operator coefficients that vanish identically with flavour-diagonal currents (dsl.NO_VERTEX),
        # whose blocks keep vertices through their flavour structures, all but Q_{e^4B}^{(2)}.
        dropped = [n for n in keep if n not in live]
        print(f"note: {len(dropped)} of the {len(keep)} selected coefficients have no vertex in this UFO and are"
              f" set to zero with the rest: {', '.join(dropped)[:300]}{' ...' if len(', '.join(dropped)) > 300 else ''}")
        keep = live

    # Write the card from parameters.py directly (the UFO's write_param_card.py needs an older
    # Python).  Every external parameter goes in, blocks in the UFO's usual order, DECAY entries
    # from the particles' width parameters.
    blocks_order = ["SMINPUTS", "MASS", "CKMBLOCK", "DIM6", "DIM8", "DIM8F", "YUKAWA"]
    seen = [b for b in blocks_order if any(e[3] == b for e in ext)] + sorted({e[3] for e in ext} - set(blocks_order) - {"DECAY"})
    out, kept, kept6, kept_t, zeroed = [], 0, 0, 0, 0
    def num(v):
        try: return float(eval(v, {"__builtins__": {}}, {"cmath": __import__("cmath")}))
        except Exception: return 0.0
    # the absolute values each block already holds, as printed, from the parameters that keep their defaults
    # or that a NAME=VALUE selector sets
    taken = {}
    for _, pname, value, blk, codes in ext:
        if not is_coefficient(blk, pname):
            taken.setdefault(blk, set()).add(abs(float(f"{values.get(pname, num(value)):.6e}")))
    for b in seen:
        out.append(f"Block {b} ")
        for _, pname, value, blk, codes in ext:
            if blk != b: continue
            code = " ".join(c.strip() for c in codes.split(","))
            shown = f"{values.get(pname, num(value)):.6e}"
            if is_coefficient(b, pname):
                if pname in keep or pname in keep6 or pname in keep_t:
                    shown = placeholder(pname, taken.setdefault(b, set()))
                    if b in ("DIM8", "DIM8F"): kept += 1
                    elif is_member(b, pname): kept_t += 1
                    else: kept6 += 1
                else:
                    shown = f"{0.0:.6e}"; zeroed += 1
            out.append(f"  {code} {shown} # {pname} ")
    for _, pname, value, blk, codes in ext:
        if blk == "DECAY":
            out.append(f"DECAY {codes.strip()} {values.get(pname, num(value)):.6e} # {pname} ")
    dest = os.path.join(ufo, f"restrict_{name}.dat")
    header = [f"# restriction card '{name}' written by validate/make_restriction.py",
              f"# keeps {kept} dimension-eight coefficient(s) from {len(set(blocks))} operator block(s): " + " ".join(sorted(set(blocks), key=lambda b: int(b[4:]))),
              f"# keeps {kept6} dimension-six coefficient(s)",
              *([f"# keeps {kept_t} coefficient(s) of the members of the towers, above dimension eight"] if members else []),
              "# kept coefficients carry placeholder values; set the physical values in the run's param_card.dat",
              *(["# inputs at other values than the model's defaults: "
                 + " ".join(f"{k}={values[k]:g}" for k in sorted(values))] if values else []),
              # a staging suffix .new is stripped from the directory name, so that the printed
              # import line names the released model
              "# import with:  import model "
              + re.sub(r"[._]new$", "", os.path.basename(ufo)) + "-" + name]
    open(dest, "w").write("\n".join(header + out))
    shown = os.path.relpath(dest)
    if shown.startswith(".."):
        shown = dest
    print(f"wrote {shown}: kept {kept} dim-8" + (f" and {kept6} dim-6" if kept6 else "") + (f" and {kept_t} tower" if members else "")
          + f" coefficients, zeroed {zeroed}"
          + (", with " + ", ".join(f"{k} = {values[k]:g}" for k in sorted(values)) if values else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
