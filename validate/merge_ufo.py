#!/usr/bin/env python3
"""Join UFO models that FeynRules wrote in shards into one UFO.

    python3.11 validate/merge_ufo.py OUT SHARD [SHARD ...]

FeynRules' WriteUFO on the whole model runs for a day or more on two kernels.  hpc/write_shards.sh
instead writes the cached vertex lists in shards, each with WriteUFO on the same base model, all at
once, the base model's own vertices in the first shard only.  The shards then differ only in their
vertices, couplings and Lorentz structures, and this script joins those:

* the particles and coupling orders of every shard must be identical, and OUT takes them from the first
  shard;
* so must the parameters of the base model, which every shard has.  FeynRules adds to them internal
  parameters for the products of Yukawa and CKM entries that the vertices of a shard need, numbered
  in the order a shard meets them, so that one name means different products in different shards.
  The first shard has them too, for the flavour structures of the operators of the input relations,
  so the parameters of the base model are those that every shard has, in the order of the first.  OUT
  has each product once, under the name of the shard that first has it, or a new name where that one
  is taken, and the couplings of each shard are written with those names;
* a Lorentz structure is one object whatever shard wrote it, named as FeynRules names them (the spins
  as letters, then a number);
* the vertices of all shards with the same particles become one vertex, with the colour and Lorentz
  structures of all of them;
* where two couplings fall on the same colour and Lorentz structure, those with the same coupling orders
  are summed into one coupling, since MadGraph files the couplings of a vertex by their orders and keeps
  one per order and structure, and each of those with other orders goes into a vertex of its own with the
  same particles, as FeynRules writes them in a model of one piece.  A list of couplings on one structure
  is valid UFO, but the checks of the release (validate/drop_zero_structures.py, validate/audit_ufo.py,
  ...) read one coupling per structure;
* couplings with the same value and orders are one coupling.

What MadGraph computes from OUT is then what it computes from the UFO of the whole model, which
validate/compare_ufo.py checks coupling by coupling.
"""
import collections
import os
import re
import shutil
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from compare_ufo import leave_ufo, use_ufo  # noqa: E402

SHARED = ("particles.py", "coupling_orders.py")
PARAMETER = re.compile(r"^(\w+) = Parameter\(", re.M)
SPIN_LETTER = {-1: "U", 1: "S", 2: "F", 3: "V", 4: "R", 5: "T"}


def parameter_blocks(text):
    """The header of a parameters.py and its parameters as [(name, text of the definition)]."""
    ms = list(PARAMETER.finditer(text))
    # each ends in one blank line, whatever follows it in the file
    blocks = [(m.group(1), text[m.start():(ms[i + 1].start() if i + 1 < len(ms) else len(text))].rstrip() + "\n\n")
              for i, m in enumerate(ms)]
    return text[:ms[0].start()] if ms else text, blocks


def field(block, key):
    m = re.search(key + r" = ('(?:[^'\\]|\\.)*'|[^,)]+)", block)
    return m.group(1) if m else None


def renamer(names):
    """A function that renames the parameters named in the dict names, as whole words."""
    if not names:
        return lambda text: text
    rx = re.compile(r"\b(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b")
    return lambda text: rx.sub(lambda m: names[m.group(1)], text)


def merge_parameters(shards):
    """The parameters.py of OUT, and for each shard the renaming of its parameters in OUT."""
    parsed = [parameter_blocks(open(os.path.join(s, "parameters.py")).read()) for s in shards]
    head = parsed[0][0]
    common = set.intersection(*({n for n, _ in blocks} for _, blocks in parsed))
    base_blocks = [(n, b) for n, b in parsed[0][1] if n in common]
    base = dict(base_blocks)
    extra = collections.OrderedDict()   # name in OUT -> definition
    by_value = {}                       # (type, value in OUT's names) -> name in OUT
    renames = []
    for s, (_, blocks) in zip(shards, parsed):
        ren = {}
        for name, blk in blocks:
            if name in base and blk == base[name]:
                continue
            if field(blk, "nature") != "'internal'":
                sys.exit(f"the external parameter {name} differs between {shards[0]} and {s}, or not every shard has it: "
                         "the shards were not written on the same base model")
            key = (field(blk, "type"), renamer(ren)(field(blk, "value")))
            if key in by_value:
                ren[name] = by_value[key]
                continue
            new, k = name, 1
            while new in base or new in extra:
                new, k = f"{name}x{k}", k + 1
            ren[name] = new
            extra[new] = renamer(ren)(blk)
            by_value[key] = new
        renames.append(ren)
    return head + "".join(b for _, b in base_blocks) + "".join(extra.values()), renames, len(extra)


def load(ufo, rename=lambda text: text):
    """The vertices, couplings and Lorentz structures of a UFO as plain data, the couplings with the
    parameters renamed by rename."""
    use_ufo(ufo)
    try:
        import couplings as C
        import lorentz as L
        import particles as Pm
        import vertices as V
        # a particle by the name of its object in particles.py (ghG__tilde__), which vertices.py uses, and
        # not by its own name (ghG~), which is not a Python name
        pyname = {id(o): k for k, o in vars(Pm).items() if hasattr(o, "pdg_code")}
        coup = {c.name: (rename(c.value), tuple(sorted(c.order.items()))) for c in C.all_couplings}
        lor = {l.name: (tuple(l.spins), l.structure) for l in L.all_lorentz}
        for l in L.all_lorentz:
            extra = set(vars(l)) - {"name", "spins", "structure"}
            if extra:
                sys.exit(f"{ufo}: Lorentz structure {l.name} has attributes this script does not carry: {extra}")
        verts = []
        for v in V.all_vertices:
            cps = {}
            for key, c in v.couplings.items():
                cps[key] = [x.name for x in (c if isinstance(c, list) else [c])]
            verts.append(([pyname[id(p)] for p in v.particles], list(v.color), [l.name for l in v.lorentz], cps))
        return coup, lor, verts
    finally:
        leave_ufo(ufo)


def same(a, b):
    """Two files of the shards are the same model file: equal but for the date FeynRules writes into the
    header of each."""
    strip = lambda f: [l for l in open(f, errors="replace") if not l.startswith("# Date:")]
    return strip(a) == strip(b)


def header(text):
    """Everything before the first object a UFO file defines: the comments and the imports."""
    import re
    m = re.search(r"^\w+ = (Coupling|Lorentz|Vertex)\(", text, re.M)
    return (text[:m.start()] if m else text).rstrip("\n")


def main(argv):
    if len(argv) < 3:
        print(__doc__)
        return 2
    out, shards = argv[1], argv[2:]
    for s in shards[1:]:
        for f in SHARED:
            if not same(os.path.join(shards[0], f), os.path.join(s, f)):
                sys.exit(f"{f} differs between {shards[0]} and {s}: the shards were not written on the same base model")
    parameters, renames, n_extra = merge_parameters(shards)

    lorentz_names = {}                 # (spins, structure) -> merged name
    lorentz_count = collections.Counter()
    couplings = {}                     # (value, order) -> merged name
    vertices = collections.OrderedDict()   # particles -> {"color": [], "lorentz": [], "couplings": {(ci, li): [(value, order)]}}

    def lorentz_name(spins, structure):
        key = (spins, structure)
        if key not in lorentz_names:
            prefix = "".join(SPIN_LETTER[s] for s in spins)
            lorentz_count[prefix] += 1
            lorentz_names[key] = f"{prefix}{lorentz_count[prefix]}"
        return lorentz_names[key]

    n_in = 0
    for s, ren in zip(shards, renames):
        coup, lor, verts = load(os.path.abspath(s), renamer(ren))
        n_in += len(verts)
        for parts, colors, lors, cps in verts:
            m = vertices.setdefault(tuple(parts), {"color": [], "lorentz": [], "couplings": collections.defaultdict(list)})
            cmap = []
            for c in colors:
                if c not in m["color"]:
                    m["color"].append(c)
                cmap.append(m["color"].index(c))
            lmap = []
            for l in lors:
                name = lorentz_name(*lor[l])
                if name not in m["lorentz"]:
                    m["lorentz"].append(name)
                lmap.append(m["lorentz"].index(name))
            for (ci, li), names in cps.items():
                m["couplings"][(cmap[ci], lmap[li])].extend(coup[n] for n in names)

    def coupling_name(value, order):
        key = (value, order)
        if key not in couplings:
            couplings[key] = f"GC_{len(couplings) + 1}"
        return couplings[key]

    # the couplings of one structure: summed per coupling order, the first order in the vertex and each
    # further one in a vertex of its own with the same particles, holding only the structures it uses
    vlines = []
    k = 0
    for parts, m in vertices.items():
        layers = []                    # [{(ci, li): coupling name}], the first order of each structure, the second, ...
        for key in sorted(m["couplings"]):
            by_order = collections.OrderedDict()
            for value, order in m["couplings"][key]:
                by_order.setdefault(order, []).append(value)
            for j, (order, vals) in enumerate(by_order.items()):
                if j == len(layers):
                    layers.append({})
                layers[j][key] = coupling_name(vals[0] if len(vals) == 1 else " + ".join(f"({v})" for v in vals), order)
        for j, layer in enumerate(layers):
            if j == 0:
                colors, lors, entries = m["color"], m["lorentz"], layer
            else:
                cs, ls = sorted({ci for ci, _ in layer}), sorted({li for _, li in layer})
                colors, lors = [m["color"][i] for i in cs], [m["lorentz"][i] for i in ls]
                entries = {(cs.index(ci), ls.index(li)): n for (ci, li), n in layer.items()}
            k += 1
            vlines.append(f"V_{k} = Vertex(name = 'V_{k}',\n"
                          f"             particles = [ {', '.join('P.' + p for p in parts)} ],\n"
                          f"             color = [ {', '.join(repr(c) for c in colors)} ],\n"
                          f"             lorentz = [ {', '.join('L.' + l for l in lors)} ],\n"
                          f"             couplings = {{{','.join(f'({ci},{li}):C.{n}' for (ci, li), n in sorted(entries.items()))}}})\n")

    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(shards[0], out, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    first = os.path.abspath(shards[0])
    with open(os.path.join(out, "parameters.py"), "w") as f:
        f.write(parameters)
    with open(os.path.join(out, "vertices.py"), "w") as f:
        f.write(header(open(os.path.join(first, "vertices.py")).read()) + "\n\n\n" + "\n".join(vlines))
    with open(os.path.join(out, "couplings.py"), "w") as f:
        f.write(header(open(os.path.join(first, "couplings.py")).read()) + "\n\n\n")
        for (value, order), name in couplings.items():
            f.write(f"{name} = Coupling(name = '{name}',\n                value = {value!r},\n"
                    f"                order = {{{','.join(f'{o!r}:{n}' for o, n in order)}}})\n\n")
    with open(os.path.join(out, "lorentz.py"), "w") as f:
        f.write(header(open(os.path.join(first, "lorentz.py")).read()) + "\n\n\n")
        for (spins, structure), name in lorentz_names.items():
            f.write(f"{name} = Lorentz(name = '{name}',\n               spins = [ {', '.join(str(s) for s in spins)} ],\n"
                    f"               structure = {structure!r})\n\n")
    print(f"{len(shards)} shards, {n_extra} parameters added to those of the base model, "
          f"{n_in} vertices in, {k} out, {len(couplings)} couplings, "
          f"{len(lorentz_names)} Lorentz structures -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
