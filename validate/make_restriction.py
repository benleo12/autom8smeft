#!/usr/bin/env python3
"""Write a MadGraph restriction card that keeps a chosen set of dimension-eight operators.

    validate/make_restriction.py <UFO dir> <card name> <selector> [<selector> ...]

Selectors, mixed freely:
    Q_{G^2H^4}^{(1)}       an operator name as in docs/block_index.json (Murphy's notation)
    c8G2H4x1               a Wilson-coefficient name (complex ones keep both Re and Im parts)
    L8op593  or  593       a block number
    cls:6                  every operator of a class number (Murphy's class numbering)
    all                    every dimension-eight operator (a card that keeps everything)

Writes <UFO dir>/restrict_<card name>.dat.  Importing the model as
    import model <UFO dir>-<card name>
makes MadGraph drop every coefficient that the card sets to zero, together with every vertex
whose couplings then vanish, so the resulting model contains only the kept operators and the
Standard Model, whatever process is generated afterwards.  Pure Python: no Mathematica needed.

MadGraph's rules for the card: a parameter set to 0 is removed from the model, one set to
exactly 1 is frozen at 1, and external parameters with identical values are merged into one.
The kept coefficients are therefore given distinct placeholder values 0.100, 0.101, ... which
carry no meaning: set the physical values in the run's param_card.dat as usual.  Everything
that is not a dimension-eight coefficient (masses, inputs, dimension-six coefficients, which
default to zero and are removed too unless the model ships a dimension-six Lagrangian) is
copied from the UFO's defaults.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def main(argv):
    if len(argv) < 4:
        print(__doc__); return 2
    ufo, name, selectors = os.path.abspath(argv[1]), argv[2], argv[3:]
    index = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    by_block = {e["block"]: e for e in index}
    by_op = {op: e for e in index for op in e["ops"]}
    by_wc = {wc: e for e in index for wc in e["wcs"]}
    params = open(os.path.join(ufo, "parameters.py")).read()
    ufo_dim8 = re.findall(r"name = '(c8\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,\s*texname = '[^']*',\s*lhablock = 'DIM8',\s*lhacode = \[ (\d+) \]", params)
    ufo_names = {n for n, _ in ufo_dim8}
    if not ufo_names:
        print("no DIM8 external parameters found in", ufo); return 2

    wanted_wcs, blocks = set(), []
    for s in selectors:
        if s == "all":
            for e in index: wanted_wcs |= set(e["wcs"]); blocks.append(e["block"])
        elif s.startswith("cls:"):
            hits = [e for e in index if e["cls"] == int(s[4:])]
            if not hits: print("no operators in class", s[4:]); return 2
            for e in hits: wanted_wcs |= set(e["wcs"]); blocks.append(e["block"])
        elif s in by_op:
            wanted_wcs |= set(by_op[s]["wcs"]); blocks.append(by_op[s]["block"])
        elif s in by_wc:
            wanted_wcs.add(s); blocks.append(by_wc[s]["block"])
        elif s in by_block or ("L8op" + s) in by_block:
            e = by_block.get(s) or by_block["L8op" + s]
            wanted_wcs |= set(e["wcs"]); blocks.append(e["block"])
        else:
            print("unknown selector:", s, "(operator name, coefficient, block number, cls:N or all)"); return 2
    # complex coefficients appear in the UFO as <wc>Re and <wc>Im; real ones as <wc>
    keep = sorted(n for n in ufo_names if n in wanted_wcs or n[:-2] in wanted_wcs and n[-2:] in ("Re", "Im"))
    not_in_ufo = sorted(w for w in wanted_wcs if w not in ufo_names and w + "Re" not in ufo_names)
    if not_in_ufo:
        print("WARNING: not present in this UFO (its operator blocks were not included when the UFO was written):", ", ".join(not_in_ufo))
    if not keep:
        print("nothing to keep"); return 2

    # A partial UFO still carries the whole basis in parameters.py, so a coefficient being there
    # does not mean any vertex uses it.  Restricting to operators with no vertices leaves a model
    # whose couplings never carry NP, and MadGraph then rejects "NP^2==2" with "model order NP^2
    # not valid for this model", which is a confusing way to learn that the block was not built.
    # A complex coefficient reaches the couplings as its base name, an internal parameter built
    # from the external <name>Re and <name>Im, so the parts are checked through the base.
    used = set(re.findall(r"\bc8\w+\b", open(os.path.join(ufo, "couplings.py")).read()))
    live = [n for n in keep if n in used or re.sub(r"(Re|Im)$", "", n) in used]
    if not live:
        print("WARNING: none of the kept coefficients appears in any vertex of this UFO, so the")
        print("         restricted model will have no NP coupling order at all and orders like")
        print("         NP^2==2 will be rejected.  Write the UFO with these operator blocks first.")
        return 2
    if len(live) < len(keep):
        # Coefficients with no vertex are set to zero like the rest: a placeholder value would
        # change nothing in MadGraph and would make the card's "kept" count a lie.  The usual
        # reasons are the baryon-number-violating blocks (675 to 734, not in the shipped model)
        # and the nine operators that vanish identically for a flavour-universal coefficient.
        dropped = [n for n in keep if n not in live]
        print(f"note: {len(dropped)} of the {len(keep)} selected coefficients have no vertex in this UFO and are"
              f" set to zero with the rest: {', '.join(dropped)[:300]}{' ...' if len(', '.join(dropped)) > 300 else ''}")
        keep = live

    # Write the card from parameters.py directly (the UFO's write_param_card.py needs an older
    # Python).  Every external parameter goes in, blocks in the UFO's usual order, DECAY entries
    # from the particles' width parameters.
    ext = re.findall(r"(\w+) = Parameter\(name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = ([^,]*),\s*texname = '[^']*',\s*lhablock = '(\w+)',\s*lhacode = \[ ([\d, ]+) \]", params)
    blocks_order = ["SMINPUTS", "MASS", "CKMBLOCK", "DIM6", "DIM8", "YUKAWA"]
    seen = [b for b in blocks_order if any(e[3] == b for e in ext)] + sorted({e[3] for e in ext} - set(blocks_order) - {"DECAY"})
    out, k, kept, zeroed = [], 0, 0, 0
    def num(v):
        try: return float(eval(v, {"__builtins__": {}}, {"cmath": __import__("cmath")}))
        except Exception: return 0.0
    for b in seen:
        out.append(f"Block {b} ")
        for _, pname, value, blk, codes in ext:
            if blk != b: continue
            code = " ".join(c.strip() for c in codes.split(","))
            v = num(value)
            if b == "DIM8" and pname.startswith("c8"):   # the scale Lam shares the block and must stay
                if pname in keep: v = 0.1 + 0.001 * k; k += 1; kept += 1
                else: v = 0.0; zeroed += 1
            out.append(f"  {code} {v:.6e} # {pname} ")
    for _, pname, value, blk, codes in ext:
        if blk == "DECAY":
            out.append(f"DECAY {codes.strip()} {num(value):.6e} # {pname} ")
    dest = os.path.join(ufo, f"restrict_{name}.dat")
    header = [f"# restriction card '{name}' written by validate/make_restriction.py",
              f"# keeps {kept} dimension-eight coefficient(s) from {len(set(blocks))} operator block(s): " + " ".join(sorted(set(blocks), key=lambda b: int(b[4:]))),
              "# kept coefficients carry placeholder values; set the physical values in the run's param_card.dat",
              # release_model.sh builds into <name>.new and swaps at the end, so the basename
              # during a release is "dim8_is.new" and the printed import line was unusable.
              "# import with:  import model "
              + re.sub(r"\.new$", "", os.path.basename(ufo)) + "-" + name]
    open(dest, "w").write("\n".join(header + out))
    print(f"wrote {dest}: kept {kept} coefficients ({', '.join(keep)}), zeroed {zeroed}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
