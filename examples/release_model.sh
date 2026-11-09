#!/bin/bash
# Turn a full-basis UFO written by validate/fr_writeufo.wls into the shipped model directory.
#   usage: examples/release_model.sh <UFO dir written by the writer> <release name, e.g. dim8_is>
# ./dim8 rebuild runs this for each model, after computing the vertices and writing the UFO.
# Steps: copy to a staging directory, drop caches and logs, set the author in __init__.py and
# append to it the two MadGraph fixes of examples/mg5_fixes.py (ALOHA routine names, parameter renaming), make
# write_param_card.py write the whole default card (examples/fix_param_card_writer.py), raise the NP expansion
# order to 4 so that double insertions can be requested (the writer sets 2), drop
# the identically vanishing Lorentz structures, write the decimal literals as exact fractions
# (validate/exact_literals.py), write an annotated parameter-card template, write
# the standard restriction cards (one per class of the Murphy basis, plus bosonic, cpeven, cpodd
# and all, and dim6 and both when the model carries a dimension-six sector), check that the model
# files are well formed, that they pass validate/audit_ufo.py and validate/check_dimensions_ufo.py
# and that MadGraph imports them, swap the result into models/<name>, and print the sizes.  Python
# and shell, plus MadGraph for the import test.  No Mathematica needed.
set -e
SRC=$(cd "${1:?UFO dir}" && pwd); NAME=${2:?release name}
ROOT=$(cd "$(dirname "$0")/.." && pwd); FINAL=$ROOT/models/$NAME; DEST=${FINAL}_new
# The staging directory must be a name MadGraph can import.  MadGraph takes the directory name as
# a Python module name, so a name with a dot, such as dim68_is.new, fails the import test below
# with a misleading "invalid syntax (object_library.py, ...)".  The model is built next to the
# final name and swapped in at the end, so that a MadGraph session importing the current release
# while this runs sees either the old directory or the new one, never a half-copied one.
mkdir -p $ROOT/models; rm -rf $DEST; cp -r $SRC $DEST
rm -rf $DEST/__pycache__ $DEST/*.log $DEST/*.cmd $DEST/param_card.dat
python3 - $DEST $ROOT/examples/mg5_fixes.py <<'EOF'
import re, sys, os
d = sys.argv[1]
# The UFO header names the authors of THIS model.  FeynRules copies M$Information of the base
# file into __init__.py, so the header carries whatever the base file names.  Setting the author
# here makes the release independent of the base file.
p = f"{d}/__init__.py"; s = open(p).read()
s = re.sub(r'__author__\s*=\s*"[^"]*"', '__author__ = "dim8auto"', s)
s = re.sub(r'__date__\s*=\s*"[^"]*"', '__date__ = "2026"', s)
# Without the fixes MadGraph 3.5 cannot link some processes of these models, p p > e+ e- g among them,
# and spends most of every import renaming parameters (see the file).  Users would have to patch
# MadGraph themselves.
if "_change_parameter_name_with_prefix" not in s:
    s = s.rstrip("\n") + "\n" + open(sys.argv[2]).read()
open(p, "w").write(s); print("__init__.py: author dim8auto, the MadGraph fixes of examples/mg5_fixes.py")
p = f"{d}/coupling_orders.py"; s = open(p).read()
s2 = re.sub(r"(NP = CouplingOrder\(name = 'NP',\s*expansion_order = )\d+", r"\g<1>4", s)
assert s2 != s or "expansion_order = 4" in s, "NP order block not found"
open(p, "w").write(s2); print("coupling_orders.py: NP expansion_order = 4")
# FeynRules copies its own UFO helper files into every model, and its object_library.py still has
# the Python 2 form `raise UFOError, "..."`.  Python 3 cannot import such a model, so every later
# step that imports it would stop.  MadGraph rewrites the file the first time it imports a model,
# which is why a UFO that had already been through MadGraph released without this step and a fresh
# one from the writer did not.  Rewrite the form here, then require every file to compile.
import glob
p = f"{d}/object_library.py"; s = open(p).read()
s2 = re.sub(r'raise (\w+),\s*("[^"\n]*")', r'raise \1(\2)', s)
if s2 != s: open(p, "w").write(s2); print("object_library.py: Python 2 raise statements rewritten")
bad = []
for f in sorted(glob.glob(f"{d}/*.py")):
    try: compile(open(f).read(), f, "exec")
    except SyntaxError as e: bad.append(f"{os.path.basename(f)}, line {e.lineno}: {e.msg}")
if bad: sys.exit("release stopped: model files that are not Python 3:\n  " + "\n  ".join(bad))
print("every model file compiles under Python 3")
# The Higgs quartic is the internal parameter lam.  MadGraph ignores case in parameter names, so it
# writes the scale Lam into the parameter card as lam__2, and "set Lam 3000" at its launch prompt is
# then accepted without effect, leaving the run at the default scale.  The quartic is renamed, which
# no user sees, so that the scale keeps its own name.
files = sorted(glob.glob(f"{d}/*.py"))
assert not any(re.search(r"\blamH\b", open(f).read()) for f in files), "lamH is already taken"
n = 0
for f in files:
    s = open(f).read()
    s2, k = re.subn(r"\blam\b", "lamH", s)
    if k:
        open(f, "w").write(s2); n += k
assert re.search(r"^lamH = Parameter\(name = 'lamH'", open(f"{d}/parameters.py").read(), re.M), \
    "the quartic lam was not found in parameters.py"
print(f"the Higgs quartic lam renamed lamH ({n} occurrences), so that MadGraph keeps the name Lam")
EOF
# MadGraph's default parameter card, which fills the entries a run's card leaves out, is written by the
# model's write_param_card.py, and FeynRules' copy stops at the first complex coefficient
python3 $ROOT/examples/fix_param_card_writer.py $DEST || { echo "release stopped: write_param_card.py"; exit 1; }
# Zeros that FeynRules writes without checking, removed in three stages.  An identically vanishing
# Lorentz structure, a group of structures in one vertex whose couplings are equal up to sign and
# whose sum vanishes, and a coefficient whose whole contribution vanishes (the four-fermion
# field-strength operators with two identical flavour-diagonal currents).
# ALOHA reduces any of them to a zero routine, omits the declarations of the arguments it no longer
# uses, and the generated Fortran fails to compile on any process reaching that vertex, with a
# message that points at the process rather than at the structure.  Every test evaluates the
# Dirac structures as well and imposes momentum conservation, at random values of every input.
# The tests need numpy, which MadGraph's Python need not have (the mini's mg5 environment has none):
# the first of $DIM8_NUMPY_PY, python3.13 and python3 that imports it runs them.
NPY=""
for p in ${DIM8_NUMPY_PY:-} python3.13 python3; do
  command -v "$p" > /dev/null && "$p" -c "import numpy" 2> /dev/null && { NPY=$p; break; }
done
[ -n "$NPY" ] || { echo "no Python with numpy for drop_zero_structures.py and audit_ufo.py: set DIM8_NUMPY_PY"; exit 1; }
$NPY $ROOT/validate/drop_zero_structures.py $DEST
# FeynRules writes a leading negative rational coefficient as a decimal, -0.16666666666666666*(...),
# and MadGraph's Fortran writer prints a decimal to seven digits, so in the compiled matrix element
# the coupling is off by 2e-7 and cancellations between couplings fail: the photon and Z exchanges in
# u_R u_R~ > W+ W- by 2e-7 s/MZ^2.  The decimals are written as the fractions they are.
python3 $ROOT/validate/exact_literals.py $DEST
# ---- the dimension-six inputs ----
# A model without a dimension-six sector of its own has the dimension-six coefficients of its input
# relations fixed at zero, since alone they are half a calculation, and a model with a sector is left
# as it is, which validate/freeze_dim6_inputs.py decides.  It runs before the parameter-card template
# and the restriction cards are written from parameters.py, so that neither holds them.
python3 $ROOT/validate/freeze_dim6_inputs.py $DEST
# ---- end of the dimension-six inputs ----
python3 - $DEST <<'EOF'
import re, sys, os
d = sys.argv[1]
# parameter-card template: every external parameter, DIM8 block annotated with operator names
import json, os
idx = json.load(open(os.path.join(os.path.dirname(os.path.dirname(d)), "docs", "block_index.json")))
op_of = {}
for e in idx:
    for w in e["wcs"] + e.get("flavour", []): op_of[w] = (e["ops"], e["cls"], e["block"])
params = open(f"{d}/parameters.py").read()
# Coefficients the model carries as parameters but uses in no vertex: the whole basis is written
# into parameters.py whatever blocks were built, so the 120 baryon-number-violating entries of
# blocks 675-734 (the Re and Im parts of 60 coefficients) sit in the card of a B-conserving model
# and setting them does nothing.  The template says so on the line.
used = set(re.findall(r"\bc8\w+\b", open(f"{d}/couplings.py").read()))
# a complex coefficient enters the couplings as its base name (an internal parameter built from
# the external Re and Im parts), so the parts count as used when the base is
used |= {n + s for n in list(used) for s in ("Re", "Im")}
# The model's basis (gen/basis.py): parameters.py declares the class-11 coefficients of both bases, and
# those of the other basis have no vertex in it.
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(d)), "gen"))
import basis
mbasis = basis.of_model(d)
other = basis.left_out(mbasis)
ext = re.findall(r"(\w+) = Parameter\(name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = ([^,]*),\s*texname = '[^']*',\s*lhablock = '(\w+)',\s*lhacode = \[ ([\d, ]+) \]", params)
def num(v):
    try: return float(eval(v, {"__builtins__": {}}, {"cmath": __import__("cmath")}))
    except Exception: return 0.0
order = ["SMINPUTS", "MASS", "CKMBLOCK", "DIM6", "DIM8", "DIM8F", "YUKAWA"]
blocks = [b for b in order if any(e[3] == b for e in ext)] + sorted({e[3] for e in ext} - set(order) - {"DECAY"})
seen_cls = set()
out = ["# parameter card template for the dimension-eight model: every Wilson coefficient is listed",
       "# in block DIM8 with its operator and class, and the coefficient of every further flavour",
       "# structure of a fermionic operator in block DIM8F; all are zero by default, Lam is the scale in",
       "# GeV.  Complex coefficients have Re and Im parts.  The operators are those of the Murphy basis",
       "# (arXiv:2005.00059)" + (", with the fifteen of class 11 replaced by operators in which every Higgs"
                                "\n# field carries a derivative (gen/basis.py)." if mbasis == "geo" else "."), ""]
for b in blocks:
    out.append(f"Block {b} ")
    for _, pname, value, blk, codes in ext:
        if blk != b: continue
        code = " ".join(c.strip() for c in codes.split(","))
        note = ""
        if b in ("DIM8", "DIM8F") and pname.startswith("c8"):
            base = pname if pname in op_of else re.sub(r"(Re|Im)$", "", pname)
            base = base if base in op_of else re.sub(r"x\d+x\d+$", "", base)
            if base in op_of:
                ops, cls, blk_ = op_of[base]
                # lhacode order is not class order throughout, so a class can come back later:
                # the banner goes in once, at its first appearance, and every line carries its class.
                if cls not in seen_cls:
                    out.append(f"#   ---- class {cls} ----"); seen_cls.add(cls)
                note = f"  {' , '.join(ops)} ({blk_}, class {cls})"
            if pname not in used and re.sub(r"F\w*$", "", re.sub(r"(Re|Im)$", "", pname)) in other:
                note += f"  [an operator of the {'Murphy' if mbasis == 'geo' else 'default'} basis, no vertex in this model]"
            elif pname not in used:
                note += "  [no vertex in this model, setting it does nothing]"
        # a model of order N (gen/towers.py): the members of the towers and the four-lepton members of the G_F relation
        elif re.fullmatch(r"DIM(1[0-9]|[2-9][0-9])F?", b) and re.match(r"c\d+[A-Za-z]", pname):
            d = int(re.match(r"c(\d+)", pname).group(1))
            base = "c8" + pname[len(f"c{d}"):]
            base = base if base in op_of else re.sub(r"(Re|Im)$", "", base)
            if base in op_of:
                note = f"  (H^dag H)^{(d - 8)//2} {' , '.join(op_of[base][0])} (class {op_of[base][1]})"
            else:
                note = f"  a member of dimension {d} with no operator of dimension eight (gen/towers.py)"
        elif b == "GEOGF":
            note = "  a four-lepton member that enters only the G_F relation, with no vertex"
        out.append(f"  {code} {num(value):.6e} # {pname}{note}")
for _, pname, value, blk, codes in ext:
    if blk == "DECAY": out.append(f"DECAY {codes.strip()} {num(value):.6e} # {pname}")
open(f"{d}/param_card_template.dat", "w").write("\n".join(out) + "\n")
dead = sum(1 for e in ext if e[3] in ("DIM8", "DIM8F") and e[1].startswith("c8") and e[1] not in used)
print("param_card_template.dat written:", sum(1 for e in ext if e[3] == "DIM8"), "DIM8 and",
      sum(1 for e in ext if e[3] == "DIM8F"), "DIM8F entries,", dead, "of them with no vertex in this model")
EOF
# a trial of ./dim8 rebuild (a name ending in _trial) holds a few blocks and is no example of a card, and the
# example card is that of the released models of the default basis, not of a model of order N (gen/towers.py,
# a name with _geo) or of the Murphy basis (gen/basis.py, a name with _murphy)
case $NAME in *_trial|*_geo*|*_murphy) ;; *) cp $DEST/param_card_template.dat $ROOT/examples/cards/param_card_template.dat;; esac
# standard restriction cards
MR="python3 $ROOT/validate/make_restriction.py $DEST"
for c in $(python3 -c "import json;print(' '.join(str(c) for c in sorted({e['cls'] for e in json.load(open('$ROOT/docs/block_index.json'))})))"); do
  $MR cls$c cls:$c | grep -E "WARNING|^note:" || true
done
$MR bosonic $(python3 -c "
import json; idx=json.load(open('$ROOT/docs/block_index.json'))
print(' '.join(e['block'] for e in idx if not any(ch in e['ops'][0] for ch in ('q','u','d','l','e','\\\\psi'))))") | grep -E "WARNING|^note:" || true
# CP parity comes from gen/cp_parity.py, which READS the field-by-field C x P derivation recorded
# in gen/operators.py, checked against the encoded terms at every build.  Counting dual field
# strengths is not the CP parity at dimension eight.  It
# disagrees with the derivation on 170 of the 438 operators with a real coefficient, and
# validate/cp_rates.py measures the difference as a 1.2 pb interference (coefficients at one, Lam = 1 TeV)
# where zero is required.
# So the cards ask the classifier and do not re-derive the rule or count anything.
# A card keeps coefficients, so each part of a complex coefficient, and each flavour structure of an
# operator, goes into the card of its own parity (gen/cp_parity.py, coefficient_sets).
# In a model of order N (gen/towers.py) the members of the towers go with them, each with its parity
# (cp_parity.tower_sets).
$MR cpeven $(python3 -c "
import sys; sys.path.insert(0,'$ROOT/gen'); import basis, cp_parity
print(' '.join(cp_parity.coefficient_sets(basis.of_model('$DEST'), '$DEST')[1]))") | grep -E "WARNING|^note:" || true
$MR cpodd $(python3 -c "
import sys; sys.path.insert(0,'$ROOT/gen'); import basis, cp_parity
print(' '.join(cp_parity.coefficient_sets(basis.of_model('$DEST'), '$DEST')[0]))") | grep -E "WARNING|^note:" || true
$MR all all | grep -E "WARNING|^note:" || true
# Two more when the model carries a dimension-six sector, because separating the two sectors is
# how you read NP^2==2: it holds the dimension-six square and the dimension-eight interference
# together, both being 1/Lambda^4, and there is no order that tells them apart.
# A dimension-six coefficient reaches the couplings as a bare symbol, cHG or cdH, not as a
# coupling NAME (those are all GC_<n>), so the test looks for the symbols in the coupling VALUES.
if grep -q "lhablock = 'DIM6'" $DEST/parameters.py && \
   python3 -c "import re,sys; sys.exit(0 if re.search(r\"value = '[^']*\\bc(HG|HW|HB|dH|uH|eH|qq1|ll)\\b\", open('$DEST/couplings.py').read()) else 1)"; then
  $MR dim6 dim6 | grep -E "WARNING|^note:" || true
  # In a model with both sectors "all" would read as both, and it keeps the dimension-eight one
  # alone, so the card has the name of what it keeps.  dim6 + dim8 = both at NP^2==2, since the
  # two sectors first meet at NP^2==3.
  $MR dim8 all | grep -E "WARNING|^note:" || true
  $MR both all dim6 | grep -E "WARNING|^note:" || true
  rm -f $DEST/restrict_all.dat
fi
# A model of order N (gen/towers.py) also gets the card of its two- and three-point functions: the classes whose
# operators make up the connections, with their towers, every coefficient that enters the input relations (the
# four-lepton operators of G_F among them) and the dimension-six sector, so that a decay of the Z, the W or the
# Higgs boson is computed with every operator that reaches it at the order of the model.
case $NAME in *_geo*)
  INPUTS=$(python3 - $DEST <<'EOF2'
import re, sys
txt = open(sys.argv[1] + "/parameters.py").read()
ext = set(re.findall(r"name = '(c\d+[A-Za-z]\w*)',\s*nature = 'external'", txt))
internal = dict(re.findall(r"name = '(\w+)',\s*nature = 'internal',\s*type = '\w+',\s*value = '([^']*)'", txt))
# the corrections to the inputs (gw1, vev2, ...) and every internal parameter they are written with, down to the coefficients
todo, seen, keep = [n for n in internal if re.fullmatch(r"(gw|g1|vev|aEW|MW2)\d+", n)], set(), set()
if not todo:
    sys.exit("no corrections to the inputs in " + sys.argv[1])
while todo:
    n = todo.pop()
    if n not in seen:
        seen.add(n)
        for w in re.findall(r"[A-Za-z_]\w*", internal[n]):
            if w in ext:
                keep.add(w)
            elif w in internal:
                todo.append(w)
print(" ".join(sorted(keep)))
EOF2
) || { echo "stopped: the coefficients of the input relations of $DEST were not found"; exit 1; }
  $MR poles cls:2 cls:3 cls:5 cls:6 cls:8 cls:10 cls:12 cls:13 dim6 $INPUTS | grep -E "WARNING|^note:" || true;;
esac
ls $DEST/restrict_*.dat | wc -l | xargs echo "restriction cards:"
# Cards this script does not write, such as only_q2H4D and ten, carry over from the current release, with
# the numbers of this model, since MadGraph reads a card by number and a corrected operator can move them
# (validate/rekey_cards.py), and with its defaults wherever they hold the defaults of the current release,
# since MadGraph takes a card's masses and mixing as the inputs of the restricted model.  The guard: a first
# release has no old directory and the glob stays literal.
for extra in $FINAL/restrict_*.dat; do
  [ -f "$extra" ] || continue
  b=$(basename $extra)
  [ -f $DEST/$b ] && continue
  [ "$b" = restrict_all.dat ] && [ -f $DEST/restrict_dim8.dat ] && continue
  cp $extra $DEST/$b
  python3 $ROOT/validate/rekey_cards.py $DEST --from $FINAL $DEST/$b || { echo "release stopped: the card $b cannot be carried over to this model"; exit 1; }
done
# ---- the cards carried over ----
# A card carried over from the current release may hold block DIM6, in a model that has since fixed the
# dimension-six inputs at zero, or the placeholder values of an older validate/make_restriction.py, which
# make MadGraph fuse different couplings.  Each step below leaves a card it has nothing to do for as it is.
python3 $ROOT/validate/freeze_dim6_inputs.py $DEST
python3 $ROOT/validate/make_restriction.py --renew $DEST
# ---- end of the cards carried over ----
# Nothing is swapped in until the model has been read back.  FeynRules does not stop when an
# evaluation fails inside WriteUFO.  It writes the failure into the file, for instance a
# "ClassAttributeCreation[couplings, ...TerminatedEvaluation...]" in place of the couplings of a
# vertex when an iteration limit is hit, and a check that reads the files by pattern does not see
# it.  So these checks run, in the order of their cost.  The files must be well formed (pure Python,
# always), the two audits must pass (pure Python, always), and MadGraph must import the model and
# build one process through it (when MadGraph is installed, and DIM8_SKIP_MG5_IMPORT=1 skips it with a
# warning).  A failure leaves the model it would have replaced in place.
python3 - $ROOT $DEST <<'EOF'
import sys
sys.path.insert(0, sys.argv[1] + "/validate")
import audit_ufo
bad = audit_ufo.well_formed(sys.argv[2])
for b in bad: print("MALFORMED", b)
if bad: sys.exit("release stopped: the model files are malformed, " + sys.argv[2] + " is left for inspection")
print("model files well formed")
EOF
# The audits read the model back against the encoding: coupling orders, chirality and fermion legs, and
# the mass dimension of every vertex.
$NPY $ROOT/validate/audit_ufo.py $DEST || { echo "release stopped: validate/audit_ufo.py failed, $DEST is left for inspection"; exit 1; }
python3 $ROOT/validate/check_dimensions_ufo.py $DEST || { echo "release stopped: validate/check_dimensions_ufo.py failed, $DEST is left for inspection"; exit 1; }
MG=${MG5_DIR:-${MG5_DIR:-/path/to/MG5_aMC}}
if [ "${DIM8_SKIP_MG5_IMPORT:-0}" = 1 ] || [ ! -x "$MG/bin/mg5_aMC" ]; then
  echo "WARNING: MadGraph import NOT tested (set MG5_DIR to test it). Do not publish this model untested."
else
  T=$(mktemp -d); PY311=$(command -v python3.11 || command -v python3)
  printf 'import model %s --modelname\ngenerate e+ e- > z h NP<=2\n' "$DEST" > "$T/import.cmd"
  (cd "$T" && $PY311 $MG/bin/mg5_aMC -f "$T/import.cmd" > "$T/import.log" 2>&1) || true
  if grep -q "1 processes with" "$T/import.log" && ! grep -qiE "^(Command .* interrupted|.*Error)" "$T/import.log"; then
    echo "MadGraph imports the model and generates through it"
  else
    grep -iE "error|interrupted|invalid" "$T/import.log" | head -5
    echo "release stopped: MadGraph could not import $DEST (log: $T/import.log)"; exit 1
  fi
  find "${DEST:?}" -maxdepth 1 \( -name __pycache__ -o -name '*.pkl' \) -prune -exec rm -r {} +
fi
rm -rf $FINAL.old; [ -d $FINAL ] && mv $FINAL $FINAL.old; mv $DEST $FINAL; rm -rf $FINAL.old; DEST=$FINAL
# The restriction cards live in the model directory only, so that no copy elsewhere can fall out
# of step with the model.
du -sh $DEST | cut -f1 | xargs echo "model size:"
grep -c "^V_" $DEST/vertices.py | xargs echo "vertices:"
echo "install: copy or symlink $DEST into MadGraph's models/ as $NAME"
