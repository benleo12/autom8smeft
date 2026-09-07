#!/bin/bash
# Turn a full-basis UFO written by validate/fr_writeufo.wls into the shipped model directory.
#   usage: examples/release_model.sh <UFO dir written by the writer> <release name, e.g. dim8_is>
# Steps: copy to models/<name>, drop caches and logs, raise the NP expansion order to 4 so that
# double insertions can be requested (the writer sets 2), write the standard restriction cards
# (one per Murphy class, plus bosonic / two-fermion / four-fermion / CP-even groups), write an
# annotated parameter-card template, and print the sizes.  Pure Python and shell.
set -e
SRC=$(cd "${1:?UFO dir}" && pwd); NAME=${2:?release name}
ROOT=$(cd "$(dirname "$0")/.." && pwd); FINAL=$ROOT/models/$NAME; DEST=$FINAL.new
# Built next to the final name and swapped in at the end, so that a MadGraph session importing
# the current release while this runs sees either the old directory or the new one, never a
# half-copied one.
mkdir -p $ROOT/models; rm -rf $DEST; cp -r $SRC $DEST
rm -rf $DEST/__pycache__ $DEST/*.log $DEST/*.cmd $DEST/param_card.dat
python3 - $DEST <<'EOF'
import re, sys, os
d = sys.argv[1]
p = f"{d}/coupling_orders.py"; s = open(p).read()
s2 = re.sub(r"(NP = CouplingOrder\(name = 'NP',\s*expansion_order = )\d+", r"\g<1>4", s)
assert s2 != s or "expansion_order = 4" in s, "NP order block not found"
open(p, "w").write(s2); print("coupling_orders.py: NP expansion_order = 4")
# Vertices with an empty Lorentz structure.  FeynRules can emit a Vertex whose structure is the
# literal '0' (the full model had two: a g g g W- W- and a g g g W+ W+ from Q_{G^2W^2}^{(7)},
# the six-leg piece vanishing under exchange of the identical W legs), with a coupling attached
# that looks alive.  They contribute nothing but fail the dimension audit and confuse readers,
# so they go, together with the Lorentz entries and couplings nothing else uses.
L = open(f"{d}/lorentz.py").read(); V = open(f"{d}/vertices.py").read(); C = open(f"{d}/couplings.py").read()
zero = set(re.findall(r"(\w+) = Lorentz\(name = '\w+',\s*spins = \[[^\]]*\],\s*structure = '0'\)", L))
# ... and structures that are zero without saying so: FeynRules does not antisymmetrise Epsilon
# over its dummies, so a structure whose terms cancel under a relabelling reaches the UFO alive
# (the a H H and Z H H vertices of Q_{BH^4D^2}^{(2)}).  ALOHA then writes a Fortran routine with
# undeclared arguments and every process touching the vertex fails to compile.  Found numerically.
import subprocess, shutil
py13 = shutil.which("python3.13") or shutil.which("python3")
zl = subprocess.run([py13, os.path.join(os.path.dirname(os.path.dirname(d)), "validate", "zero_lorentz.py"), d], capture_output=True, text=True).stdout
m = re.search(r"identically zero Lorentz structures: \d+ \[([^\]]*)\]", zl)
if not m: raise SystemExit("zero_lorentz.py did not run (needs numpy, python3.13 here):\n" + zl[-500:])
numeric = set(re.findall(r"'(\w+)'", m.group(1)))
print("Lorentz structures found identically zero numerically:", sorted(numeric) or "none")
zero |= numeric
if zero:
    verts = re.findall(r"(V_\d+ = Vertex\(.*?\)\n\n)", V + "\n\n", re.S)
    drop = [v for v in verts if set(re.findall(r"L\.(\w+)", v)) <= zero]
    for v in drop: V = V.replace(v, "")
    open(f"{d}/vertices.py", "w").write(V.rstrip("\n") + "\n")
    still = set(re.findall(r"L\.(\w+)", V)); stillc = set(re.findall(r"C\.(\w+)", V))
    for z in zero - still:
        L = re.sub(rf"(?<!\w){z} = Lorentz\(.*?\)\n\n", "", L, flags=re.S)
    open(f"{d}/lorentz.py", "w").write(L)
    dead = [c for c in set(re.findall(r"C\.(\w+)", "".join(drop))) if c not in stillc]
    for c in dead:
        C = re.sub(rf"(?<!\w){c} = Coupling\(.*?\)\n\n", "", C, flags=re.S)
    open(f"{d}/couplings.py", "w").write(C)
    names = [re.search(r"particles = \[(.*?)\]", v, re.S).group(1).replace("P.", "").replace(" ", "").replace("\n", "") for v in drop]
    print(f"dropped {len(drop)} vertices with an empty Lorentz structure ({', '.join(names)}), {len(zero - still)} Lorentz entries, {len(dead)} couplings")
# parameter-card template: every external parameter, DIM8 block annotated with operator names
import json, os
idx = json.load(open(os.path.join(os.path.dirname(os.path.dirname(d)), "docs", "block_index.json")))
op_of = {}
for e in idx:
    for w in e["wcs"]: op_of[w] = (e["ops"], e["cls"], e["block"])
params = open(f"{d}/parameters.py").read()
# Coefficients the model carries as parameters but uses in no vertex: the whole basis is written
# into parameters.py whatever blocks were built, so the 120 baryon-number-violating coefficients
# of blocks 675-734 sit in the card of a B-conserving model and setting them does nothing.  Say so
# on the line rather than letting a user wonder why nothing changed.
used = set(re.findall(r"\bc8\w+\b", open(f"{d}/couplings.py").read()))
# a complex coefficient enters the couplings as its base name (an internal parameter built from
# the external Re and Im parts), so the parts count as used when the base is
used |= {n + s for n in list(used) for s in ("Re", "Im")}
ext = re.findall(r"(\w+) = Parameter\(name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = ([^,]*),\s*texname = '[^']*',\s*lhablock = '(\w+)',\s*lhacode = \[ ([\d, ]+) \]", params)
def num(v):
    try: return float(eval(v, {"__builtins__": {}}, {"cmath": __import__("cmath")}))
    except Exception: return 0.0
order = ["SMINPUTS", "MASS", "CKMBLOCK", "DIM6", "DIM8", "YUKAWA"]
blocks = [b for b in order if any(e[3] == b for e in ext)] + sorted({e[3] for e in ext} - set(order) - {"DECAY"})
seen_cls = set()
out = ["# parameter card template for the dimension-eight model: every Wilson coefficient is listed",
       "# in block DIM8 with its operator (Murphy basis, arXiv:2005.00059) and class; all are zero by",
       "# default, Lam is the scale in GeV.  Complex coefficients have Re and Im parts.", ""]
for b in blocks:
    out.append(f"Block {b} ")
    for _, pname, value, blk, codes in ext:
        if blk != b: continue
        code = " ".join(c.strip() for c in codes.split(","))
        note = ""
        if b == "DIM8" and pname.startswith("c8"):
            base = re.sub(r"(Re|Im)$", "", pname)
            base = base if base in op_of else re.sub(r"x\d+x\d+$", "", base)
            if base in op_of:
                ops, cls, blk_ = op_of[base]
                # lhacode order is not class order throughout, so a class can come back later:
                # the banner goes in once, at its first appearance, and every line carries its class.
                if cls not in seen_cls:
                    out.append(f"#   ---- class {cls} ----"); seen_cls.add(cls)
                note = f"  {' , '.join(ops)} ({blk_}, class {cls})"
            if pname not in used:
                note += "  [no vertex in this model, setting it does nothing]"
        out.append(f"  {code} {num(value):.6e} # {pname}{note}")
for _, pname, value, blk, codes in ext:
    if blk == "DECAY": out.append(f"DECAY {codes.strip()} {num(value):.6e} # {pname}")
open(f"{d}/param_card_template.dat", "w").write("\n".join(out) + "\n")
dead = sum(1 for e in ext if e[3] == "DIM8" and e[1].startswith("c8") and e[1] not in used)
print("param_card_template.dat written:", sum(1 for e in ext if e[3] == "DIM8"), "DIM8 entries,",
      dead, "of them with no vertex in this model")
EOF
cp $DEST/param_card_template.dat $ROOT/examples/cards/param_card_template.dat
# standard restriction cards
MR="python3 $ROOT/validate/make_restriction.py $DEST"
for c in $(python3 -c "import json;print(' '.join(str(c) for c in sorted({e['cls'] for e in json.load(open('$ROOT/docs/block_index.json'))})))"); do
  $MR cls$c cls:$c | grep -E "WARNING|^note:" || true
done
$MR bosonic $(python3 -c "
import json; idx=json.load(open('$ROOT/docs/block_index.json'))
print(' '.join(e['block'] for e in idx if int(e['block'][4:])<=674 and not any(ch in e['ops'][0] for ch in ('q','u','d','l','e','\\\\psi'))))") | grep -E "WARNING|^note:" || true
# CP parity is decided by the number of DUAL field strengths, which lives in the operator's
# LaTeX and never in its label: "'tilde' not in e['ops'][0]" matched nothing at all, so the card
# was really "operators with a real coefficient" and shipped 128 CP-odd ones, among them
# Q_{B^4}^{(3)} and every Q_{X^2H^2D}^{(2),(4)} dipole partner.  A block is kept only if EVERY
# operator in it has an even number of duals, ops[0] not being the whole block either.
$MR cpeven $(python3 -c "
import json
idx=json.load(open('$ROOT/docs/block_index.json'))
mur={e['label']: e for e in json.load(open('$ROOT/docs/murphy_parsed.json'))}
def duals(o):
    t = mur[o]['latex']
    return t.count('widetilde') + t.count(chr(92) + 'tilde')
print(' '.join(e['block'] for e in idx
               if int(e['block'][4:]) <= 674 and e['hc_mode'] == 'real'
               and all(duals(o) % 2 == 0 for o in e['ops'])))") | grep -E "WARNING|^note:" || true
$MR all all | grep -E "WARNING|^note:" || true
ls $DEST/restrict_*.dat | wc -l | xargs echo "restriction cards:"
for extra in $FINAL/restrict_*.dat; do [ -f "$extra" ] || continue; b=$(basename $extra); [ -f $DEST/$b ] || cp $extra $DEST/$b; done   # cards written by hand into the old release survive (guard: a first release has no old directory and the glob stays literal)
rm -rf $FINAL.old; [ -d $FINAL ] && mv $FINAL $FINAL.old; mv $DEST $FINAL; rm -rf $FINAL.old; DEST=$FINAL
# The restriction cards live in the model directory and are not copied anywhere else: the copies
# under examples/cards/ went stale, lost Block DIM6 and named a model that does not exist.
du -sh $DEST | cut -f1 | xargs echo "model size:"
grep -c "^V_" $DEST/vertices.py | xargs echo "vertices:"
echo "install: copy or symlink $DEST into MadGraph's models/ as $NAME"
