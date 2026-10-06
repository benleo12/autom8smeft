#!/bin/bash
# Turn a full-basis UFO written by validate/fr_writeufo.wls into the shipped model directory.
#   usage: examples/release_model.sh <UFO dir written by the writer> <release name, e.g. dim8_is>
# Steps: copy to models/<name>, drop caches and logs, raise the NP expansion order to 4 so that
# double insertions can be requested (the writer sets 2), write the standard restriction cards
# (one per Murphy class, plus bosonic / two-fermion / four-fermion / CP-even groups), write an
# annotated parameter-card template, and print the sizes.  Pure Python and shell.
set -e
SRC=$(cd "${1:?UFO dir}" && pwd); NAME=${2:?release name}
ROOT=$(cd "$(dirname "$0")/.." && pwd); FINAL=$ROOT/models/$NAME; DEST=${FINAL}_new
# The staging directory must be a name MadGraph can import: it takes the directory name as a
# Python module name, and "dim68_is.new" stopped the import test below with "invalid syntax
# (object_library.py, line 268)", the message of a model it had not managed to convert, on a
# model that imports without complaint from any directory whose name has no dot (2026-10-05).
# Built next to the final name and swapped in at the end, so that a MadGraph session importing
# the current release while this runs sees either the old directory or the new one, never a
# half-copied one.
mkdir -p $ROOT/models; rm -rf $DEST; cp -r $SRC $DEST
rm -rf $DEST/__pycache__ $DEST/*.log $DEST/*.cmd $DEST/param_card.dat
python3 - $DEST <<'EOF'
import re, sys, os
d = sys.argv[1]
# The UFO header names the people who wrote THIS model.  FeynRules copies M$Information of the
# base file into __init__.py, and the base file's Standard-Model half descends from the model of
# Hays, Martin, Setford and Sanz, whose names and e-mail addresses were shipped as the authors of
# two releases before this line existed (2026-09-07 and again 2026-09-23); the base files now carry
# dim8auto, and this makes the release independent of them.
p = f"{d}/__init__.py"; s = open(p).read()
s = re.sub(r'__author__\s*=\s*"[^"]*"', '__author__ = "dim8auto"', s)
s = re.sub(r'__date__\s*=\s*"[^"]*"', '__date__ = "2026"', s)
open(p, "w").write(s); print("__init__.py: author dim8auto")
p = f"{d}/coupling_orders.py"; s = open(p).read()
s2 = re.sub(r"(NP = CouplingOrder\(name = 'NP',\s*expansion_order = )\d+", r"\g<1>4", s)
assert s2 != s or "expansion_order = 4" in s, "NP order block not found"
open(p, "w").write(s2); print("coupling_orders.py: NP expansion_order = 4")
EOF
# Identically vanishing Lorentz structures.  FeynRules writes a structure without checking whether
# it is zero.  ALOHA then reduces the routine to zero, omits the declarations of the arguments it
# no longer uses, and the generated Fortran fails to compile on any process reaching that vertex,
# with a message that points at the process rather than at the structure.  Nine of them sit in a
# freshly written full-basis UFO, on fifty vertices, and only fifteen of the fifty have nothing
# else in them, so the rest are edited rather than dropped.  The test this uses evaluates Dirac
# structures too and imposes momentum conservation; the earlier one did neither and found none.
$(command -v python3.13 || command -v python3) $ROOT/validate/drop_zero_structures.py $DEST
python3 - $DEST <<'EOF'
import re, sys, os
d = sys.argv[1]
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
# CP parity comes from gen/cp_parity.py, which READS the field-by-field C x P derivation stored
# in the catalogue.  Three versions of this card were wrong before that.  The first tested the
# operator LABEL for "tilde", which matches nothing, so the card was really "operators with a real
# coefficient" and shipped 128 CP-odd ones.  The second counted "widetilde" in the printed row.
# The third counted dual field strengths per term of the parsed operator, which is a better count
# and still a count: it disagrees with the derivation on 170 of the 438 real-coefficient rows and
# validate/cp_rates.py measures the difference as a 1.2 pb interference where zero is required.
# Ask the classifier.  Do not re-derive the rule here, and do not count anything.
$MR cpeven $(python3 -c "
import sys; sys.path.insert(0,'$ROOT/gen'); import cp_parity, json
cp=cp_parity.table(); idx=json.load(open('$ROOT/docs/block_index.json'))
print(' '.join(e['block'] for e in idx
               if int(e['block'][4:]) <= 674 and {cp[o] for o in e['ops']} == {'even'}))") | grep -E "WARNING|^note:" || true
$MR cpodd $(python3 -c "
import sys; sys.path.insert(0,'$ROOT/gen'); import cp_parity, json
cp=cp_parity.table(); idx=json.load(open('$ROOT/docs/block_index.json'))
print(' '.join(e['block'] for e in idx
               if int(e['block'][4:]) <= 674 and {cp[o] for o in e['ops']} == {'odd'}))") | grep -E "WARNING|^note:" || true
$MR all all | grep -E "WARNING|^note:" || true
# Two more when the model carries a dimension-six sector, because separating the two sectors is
# how you read NP^2==2: it holds the dimension-six square and the dimension-eight interference
# together, both being 1/Lambda^4, and there is no order that tells them apart.
# A dimension-six coefficient reaches the couplings as a bare symbol, cHG or cdH, not as a
# coupling NAME (those are all GC_<n>), so the test has to look for the symbols in the coupling
# VALUES.  Testing for "name = 'c...'" found nothing and silently skipped both cards.
if grep -q "lhablock = 'DIM6'" $DEST/parameters.py && \
   python3 -c "import re,sys; sys.exit(0 if re.search(r\"value = '[^']*\\bc(HG|HW|HB|dH|uH|eH|qq1|ll)\\b\", open('$DEST/couplings.py').read()) else 1)"; then
  $MR dim6 dim6 | grep -E "WARNING|^note:" || true
  $MR both all dim6 | grep -E "WARNING|^note:" || true
fi
ls $DEST/restrict_*.dat | wc -l | xargs echo "restriction cards:"
for extra in $FINAL/restrict_*.dat; do [ -f "$extra" ] || continue; b=$(basename $extra); [ -f $DEST/$b ] || cp $extra $DEST/$b; done   # cards written by hand into the old release survive (guard: a first release has no old directory and the glob stays literal)
# Nothing is swapped in until the model has been read back.  FeynRules does not stop when an
# evaluation fails inside WriteUFO: it writes the failure into the file.  On 2026-10-04 an
# iteration limit left a "ClassAttributeCreation[couplings, ...TerminatedEvaluation...]" where the
# couplings of one photon-Z-Higgs vertex should have been, in two models, and one of them was
# committed as a release, because every check that ran on it read the files by pattern and none
# of them asked Python or MadGraph to import it.  Two checks, in the order of their cost: the
# files are well formed (pure Python, always), and MadGraph imports the model and builds one
# process through it (when MadGraph is installed; DIM8_SKIP_MG5_IMPORT=1 skips it, loudly).
python3 - $ROOT $DEST <<'EOF'
import sys
sys.path.insert(0, sys.argv[1] + "/validate")
import audit_ufo
bad = audit_ufo.well_formed(sys.argv[2])
for b in bad: print("MALFORMED", b)
if bad: sys.exit("release stopped: the model files are malformed, " + sys.argv[2] + " is left for inspection")
print("model files well formed")
EOF
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
# The restriction cards live in the model directory and are not copied anywhere else: the copies
# under examples/cards/ went stale, lost Block DIM6 and named a model that does not exist.
du -sh $DEST | cut -f1 | xargs echo "model size:"
grep -c "^V_" $DEST/vertices.py | xargs echo "vertices:"
echo "install: copy or symlink $DEST into MadGraph's models/ as $NAME"
