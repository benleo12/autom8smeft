#!/usr/bin/env python3
"""The vertices of each dimension-six coefficient, which ./dim8 select lists the dimension-six sector with.

    python3 validate/dim6_index.py                              every model in models/ with a dimension-six sector
    python3 validate/dim6_index.py --models models/dim68_mw     the models named, the other entries of the file kept
    python3 validate/dim6_index.py --out PATH                   written to PATH instead of build/dim6_index.json

./dim8 select lists the dimension-six sector of a model that carries one of its own (models/dim68_is, and
models/dim68_mw) coefficient by coefficient, and for that it needs the vertices of each coefficient.
build/vertex_index.json cannot give them, since FeynRules derives the vertices of a dimension-six class
for the whole class at once.  This script reads them off the released UFOs and writes
build/dim6_index.json,

    {"how": "...", "models": {"dim68_is": {"cHq3": {"one": [["W", "dq", "uqbar"], ...], "rescaled": [...],
                                                    "two": [...]}, ...}, ...}}

with an entry for every coefficient of the model's block DIM6, an empty one where the coefficient has
no vertex, so that a coefficient missing from the file is a visible error and not a silent omission.
Run with --models, the script replaces the entries of the models named and keeps the others that the
file holds, and says which it kept, so that indexing dim68_mw on its own does not delete dim68_is.

Under "one" are the field contents of the vertices with a coupling of interaction order NP=1 that the
coefficient moves, a complex one by its internal combination or by its parts, the vertices that carry
its amplitude at 1/Lambda^2.  A coefficient moves a coupling by name or through an internal parameter
of the model.  C_HBox names no coupling outside the Higgs self-couplings, but it rescales every vertex
with one Higgs boson through the normalisation of the Higgs field, rh1 = (C_HBox - C_HD/4) v^2/Lambda^2
in models/dim68_is: h W W, h Z Z, the Yukawa couplings, and the vertices with two Higgs bosons.  Those
of its vertices that no coupling names it in, Standard Model vertices times v^2/Lambda^2, are listed
under "rescaled" as well, and ./dim8 select counts each at the power of that Standard Model vertex and
four more.  The four coefficients of the input relations, C_HD, C_HWB, C_Hl^(3) and C_ll'
(DIM6_INPUT_RELATION of ./dim8), keep to the vertices that name them: through the input relations they
move every W and Z vertex, which ./dim8 select lists under a heading of its own.  A content whose
couplings of order NP=1 move the coefficient but cancel, as the gauge vertices of C_HW cancel against
the rescaling of the W field, is not under "one".

Under "two" are the field contents of the couplings of order NP=2 that multiply the coefficient by a
second one, or by itself, and that are not under "one".  In dim68_is and dim68_mw those couplings are
the products of a linear dimension-six vertex with an input shift or a field normalisation: C_uG times
the gluon normalisation rG1 = C_HG v^2/Lambda^2 and the vev shift of C_Hl^(3) and C_ll' on the
chromomagnetic vertex of the top quark, C_W times the W normalisation of C_HW on its triple-gauge
vertex.  Such a vertex is a 1/Lambda^4 term that needs both coefficients, and it goes under "two" for
both.  The legs are labelled as build/vertex_index.json labels them, with the generations collapsed to
uq, dq, l and vl and bar for the antiparticle, and sorted.  The Goldstone bosons and the ghosts are left
out, since the released models are in unitary gauge.  One line per model says how many coefficients
have vertices of each kind.

How.  Each model is read with the reader of validate/index_vs_ufo.py, which gives every coupling's
linear response to each coefficient at zero, the internal parameters it moves included, and for the
couplings of order NP=2 the mixed second derivative at zero in every pair of the coefficients that reach
them.  A coupling moves with the coefficient, or with the pair, when the response exceeds 1e-8 of the
triangle-inequality bound on the change, and a field content counts when one of its couplings moves so
and the response summed over all the vertex objects of that content, per canonical (Lorentz, colour)
structure, does not cancel, the test of validate/index_vs_ufo.py.  A coupling that cannot be evaluated
would leave its vertex judged without it, so nothing is written then and the run stops with the
couplings named, as validate/onshell_zero.py does.  It stops as well when a model has a coefficient that
gen/lambda_routes.py does not know (DIM6_COEFF), since ./dim8 select could not place it in a class or
count its power of lambda, and when a coefficient to which gen/lambda_routes.py gives no Dirac chains
(DIM6_COEFF and DIM6_RESCALED_CHAINS) has a vertex with fermion legs under "one", since the route search
of ./dim8 select refuses such a vertex.  The exit status is 1 in each case, and when no model has a
dimension-six sector of its own.
"""
import argparse
import collections
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
sys.path.insert(0, os.path.join(ROOT, "gen"))
import index_vs_ufo as IU  # noqa: E402
import lambda_routes as LR  # noqa: E402  the coefficients ./dim8 select can place and count, and their chains

OUT = os.path.join(ROOT, "build", "dim6_index.json")
HOW = ("Written by validate/dim6_index.py from the released UFOs.  models: model -> coefficient -> 'one', "
       "the field contents (sorted labels of build/vertex_index.json, no Goldstone bosons or ghosts) of the "
       "vertices with a coupling of interaction order NP=1 that the coefficient moves, by name or through an "
       "internal parameter of the model (the four coefficients of the input relations by name alone), "
       "'rescaled', those of them where no coupling names the coefficient, Standard Model vertices that it "
       "moves through the normalisation of a field, and 'two', those of the couplings of order NP=2 that "
       "multiply the coefficient by a second one or by itself (a linear vertex times an input shift or a "
       "field normalisation) and that are not under 'one'.  Every coefficient of the model's block DIM6 has "
       "an entry.  gen/process.py select_dim6 and ./dim8 select read it.")


def in_base():
    """The dimension-six coefficients every input-scheme model carries in its base, DIM6_IN_BASE of ./dim8,
    read from there so that the two lists cannot drift."""
    m = re.search(r"^DIM6_IN_BASE = \{([^}]*)\}", open(os.path.join(ROOT, "dim8")).read(), re.M)
    return set(re.findall(r'"(\w+)"', m.group(1)))


def input_relation():
    """The four dimension-six coefficients of the input relations, DIM6_INPUT_RELATION of ./dim8, read from
    there so that the two lists cannot drift."""
    m = re.search(r"^DIM6_INPUT_RELATION = \[(.*?)\]$", open(os.path.join(ROOT, "dim8")).read(), re.M | re.S)
    return set(re.findall(r'"(\w+)"\)', m.group(1)))


def coefficients(model):
    """{coefficient: the names it has in the model} for the coefficients of the model's block DIM6, a complex
    one as its internal combination and its parts (cuH, cuHAbs, cuHPh), grouped as
    validate/onshell_zero.py model_names groups them.  The scale Lam6 shares the block and is not one."""
    txt = open(os.path.join(model, "parameters.py"), errors="replace").read()
    names = collections.defaultdict(list)
    for n in re.findall(r"(\w+) = Parameter\(\s*name = '\w+'", txt):
        names[re.sub(r"(Abs|Ph|Re|Im)$", "", n)].append(n)
    dim6 = set()
    for b in re.split(r"\n(?=\w+ = Parameter\()", txt):
        m = re.match(r"(\w+) = Parameter\(\s*name = '\w+',\s*nature = 'external'", b)
        if m and re.search(r"lhablock = 'DIM6'", b) and m.group(1) != "Lam6":
            dim6.add(re.sub(r"(Abs|Ph|Re|Im)$", "", m.group(1)))
    return {c: sorted(names[c]) for c in sorted(dim6)}


def has_sector(model):
    """Whether the model carries dimension-six coefficients beyond those of the input-scheme base, the test
    with which ./dim8 select decides that a model has a dimension-six sector of its own."""
    if not os.path.isfile(os.path.join(model, "parameters.py")):
        return False
    base = in_base()
    return any(c not in base for c in coefficients(model))


def index_model(model):
    """({coefficient: {"one": [legs, ...], "rescaled": [legs, ...], "two": [legs, ...]}}, the couplings that
    could not be evaluated)."""
    names = coefficients(model)
    of = {n: c for c, ns in names.items() for n in ns}
    by_name_only = input_relation()
    order = {}
    for g, orders in re.findall(r"(GC_\w+) = Coupling\(\s*name = '\w+',\s*value = '[^']*',\s*order = \{([^}]*)\}",
                                open(os.path.join(model, "couplings.py")).read()):
        m = re.search(r"'NP'\s*:\s*(-?\d+)", orders)
        order[g] = int(m.group(1)) if m else 0
    r = IU.read_model(model, only=set(of), pairs={g for g, o in order.items() if o == 2}, generic=True)
    one, own, two = collections.defaultdict(set), collections.defaultdict(set), collections.defaultdict(set)
    for pnames, _, ents in r["entries"]:
        if any(n not in IU.LABEL for n in pnames):
            continue                          # a particle the selector's labels do not name
        key = tuple(sorted(IU.LABEL[n] for n in pnames))
        for _, _, g in ents:
            if order.get(g) == 1:
                named = r["dep"].get(g, set())
                for n in named:               # named in the coupling and moving it
                    own[of[n]].add(key)
                for n in r["moved"].get(g, ()):  # by name, or through an internal parameter
                    if n in named or of[n] not in by_name_only:
                        one[of[n]].add(key)
            elif order.get(g) == 2:
                live2 = r["live2"].get(key, set())
                for n1, n2 in r["pair_dep"].get(g, ()):
                    if (n1, n2) in live2:     # the pair moves the coupling and does not cancel in the content
                        two[of[n1]].add(key)
                        two[of[n2]].add(key)
    out = {}
    for c, ns in names.items():
        # the content is the coefficient's when its vertex objects do not cancel in it
        mine = {k for k in one[c] if any(n in r["live"].get(k, ()) for n in ns)}
        out[c] = {"one": [list(k) for k in sorted(mine)],
                  "rescaled": [list(k) for k in sorted(mine - own[c])],
                  "two": [list(k) for k in sorted(two[c] - mine)]}
    return out, r["failed"]


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--models", nargs="+", default=None,
                    help="the UFO directories to read, the entries of other models in the file being kept "
                         "(default: every model in models/ with a dimension-six sector, the file written anew)")
    ap.add_argument("--out", default=OUT)
    a = ap.parse_args(argv[1:])
    if a.models is None:
        top = os.path.join(ROOT, "models")
        paths = [os.path.join(top, d) for d in sorted(os.listdir(top)) if has_sector(os.path.join(top, d))]
    else:
        paths = []
        for m in a.models:
            p = m if os.path.isabs(m) else os.path.join(ROOT, m)
            if has_sector(p):
                paths.append(p)
            else:
                print(f"skipped {m}: no parameters.py, or no dimension-six coefficient beyond those of the base")
    if not paths:
        sys.exit("no model with a dimension-six sector of its own to read (models/dim68_is, models/dim68_mw)")
    # the route search of ./dim8 select pairs the fermion legs of a vertex into the chains of its coefficient
    # and refuses a vertex with fermion legs of a coefficient that has none (Cheapest.assign)
    chains = LR.chains()
    data, failed, unknown, unchained = {}, [], [], []
    for p in paths:
        name = os.path.basename(os.path.normpath(p))
        entry, bad = index_model(p)
        if bad:
            print(f"{name}: {len(bad)} couplings could not be evaluated, e.g. {', '.join(bad[:3])}")
            failed += [(name, g) for g in bad]
        unknown += [(name, c) for c in entry if c not in LR.DIM6_COEFF]
        unchained += [(name, c, v) for c, e in entry.items() if c in LR.DIM6_COEFF and c not in chains
                      for v in e["one"] if any(LR.is_fermion(x) for x in v)]
        data[name] = entry
        n_one = sum(1 for e in entry.values() if e["one"])
        n_res = sum(1 for e in entry.values() if e["rescaled"])
        n_two = sum(1 for e in entry.values() if e["two"] and not e["one"])
        contents = {tuple(v) for e in entry.values() for v in e["one"] + e["two"]}
        print(f"{name}: {len(entry)} dimension-six coefficients, {n_one} with vertices at NP=1 ({n_res} of them "
              f"rescaling Standard Model vertices), {n_two} with vertices only at NP=2, together with a second "
              f"coefficient, and {len(entry) - n_one - n_two} with no vertex, in {len(contents)} field contents")
    if failed:
        print(f"not written: {len(failed)} couplings could not be evaluated (above), and a vertex whose couplings "
              "did not evaluate would be judged on the others or left out")
        return 1
    if unknown:
        print("not written: coefficients that gen/lambda_routes.py DIM6_COEFF does not know, so that ./dim8 select "
              "could not place them in a class or count their power of lambda: "
              + ", ".join(f"{c} ({m})" for m, c in unknown))
        return 1
    if unchained:
        print("not written: vertices with fermion legs of coefficients to which gen/lambda_routes.py gives no Dirac "
              "chains (DIM6_COEFF, DIM6_RESCALED_CHAINS), which the route search of ./dim8 select refuses: "
              + ", ".join(f"{c} [{' '.join(v)}] ({m})" for m, c, v in unchained[:8])
              + (f", and {len(unchained) - 8} more" if len(unchained) > 8 else ""))
        return 1
    out = a.out if os.path.isabs(a.out) else os.path.join(ROOT, a.out)
    # With --models the entries of the other models in the file are kept, so that indexing one model
    # does not delete the others.  Without it the file holds the models read and nothing else.
    kept = []
    if a.models is not None and os.path.exists(out):
        try:
            old = json.load(open(out))["models"]
            for m in sorted(old):
                if m not in data:
                    data[m] = old[m]
                    kept.append(m)
        except (OSError, ValueError, KeyError, TypeError, AttributeError) as e:
            print(f"{os.path.relpath(out, ROOT)} could not be read ({e.__class__.__name__}), so it now holds "
                  "the models read alone")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    json.dump({"how": HOW, "models": data}, open(out + ".tmp", "w"), indent=1, sort_keys=True)
    os.replace(out + ".tmp", out)
    read = sorted(os.path.basename(os.path.normpath(p)) for p in paths)
    print(f"wrote {os.path.relpath(out, ROOT)}: {', '.join(read)}"
          + (f", and kept the entries of {', '.join(kept)} that it held" if kept else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
