#!/usr/bin/env python3
"""Check the dimension-six selection by matrix elements, with MadGraph as the judge.

    python3 validate/select_complement6.py "p p > w+ w-" --model models/dim68_mw
        [--sets 3] [--points 4] [--seed 1] [--tol 1e-10] [--drop cHW,cHB] [--keep DIR] [--generic]

./dim8 select --model <M> --with-dim6 claims that the dimension-six coefficients it keeps are all that
can change the process at 1/Lambda^4.  If the claim holds, the matrix element with every coefficient on
and the one with only the kept coefficients on are the same number.  This script computes both and
compares them, subprocess by subprocess, at each order.

Why matrix elements.  validate/select_complement.py keeps the complement of the selection and asks
for no diagram.  That cannot be done at dimension six, for two reasons.  A coefficient whose couplings
cancel between vertex objects, as the gauge vertices of C_HW cancel against the rescaling of the W
field at 1/Lambda^2, keeps those couplings in a restricted model, each of them nonzero, and MadGraph
draws diagrams that vanish.  And a coefficient can enter only together with a selected one, as C_HW
enters p p > w+ w- at 1/Lambda^4 on the triple-gauge vertex of C_W.  With C_W zeroed in the complement
that coupling is zero as well, so a complement could not fail for it.  Here both are on in the first
evaluation and the selected one alone in the second, and the difference is the effect of whatever
was left out, however it enters.

What it does.  The dimension-eight sector is off, through the restriction card dim6 of the combined
model, written afresh in the copy by validate/make_restriction.py so that the run does not rest on a
card carried over from an older release.  The process is written standalone twice, at NP^2==1 and at
NP^2==2, each in its own MadGraph session, since a session stops at an order with no diagram at all.
NP<=2 is never used, since it would add the squares of order 1/Lambda^8 that the selector rightly
leaves out.  The proton and the jet hold the b quark, as those of gen/process.py do, so that the check
reaches every subprocess the selector answers for.  Each subprocess directory gets a copy of MadGraph's check_sa.f with its one evaluation
replaced by a loop over --points phase-space points from its RAMBO generator, at a centre-of-mass energy
between one and two times that of check_sa.f, compiled as a separate program.  (P*/check_sa.f is a link
to the file all subprocesses share, which stays as it is.)  The generator's seed is fixed, so that a
program gives the same momenta whatever the card holds, as long as the masses do not move.  For each of
--sets random sets of coefficient values, real ones of random sign and of size between 0.2 and 1.2,
complex ones through a modulus of that size and a random phase, as the model carries them, the program
runs with the card at (a) every dimension-six coefficient at its value and (b) only the coefficients the
selection keeps at the same value and the others at zero.  Lam stays at its default, since at one order
every term scales with it alike.

The W mass.  In the {alpha, MZ, GF} scheme M_W is an internal parameter that moves with C_Hl^(3), C_ll',
C_HD and C_HWB at 1/Lambda^2 and with C_HB and C_HW at 1/Lambda^4, and a mass carries no order NP, so
NP^2==n does not take that motion out.  A process with a Standard Model tree with a W keeps all of them,
through the input relations and through its vertices with a W, and M_W stays as the model has it, since
what it then brings is of order 1/Lambda^4 and the check must see it.  A process with no Standard Model
tree has its whole 1/Lambda^4 term in the square of the dimension-six amplitude, on which the motion of
M_W is of order 1/Lambda^6, and the selection rightly leaves those coefficients out, as it does in
g g > w+ w-.  So for such a process the copy of the model has M_W at its Standard Model value, in both
evaluations.

What counts as agreeing.  |M|^2 of (a) and (b) comes from one compiled program at the same momenta, so
if nothing left out enters, the two differ at most by rounding, which the couplings that cancel between
vertex objects leave behind.  Double precision carries 2.2e-16 per operation, and a matrix element holds
thousands of operations and cancellations between diagrams of up to s/M_W^2 in the amplitude, so that
the rounding stays below 1e-11 of |M|^2.  --tol, default 1e-10, is the relative difference allowed.  A
term left out moves |M|^2 at NP^2==1 by order one and at NP^2==2 by at least v^2/Lambda^2 at Lambda = 1
TeV, about 0.06, times couplings of order one.  One that reaches the process only through a light Yukawa
coupling and a light mass can sit below the tolerance in u u~, at y_u m_u/E of about 4e-11, and shows in
b b~, at y_b m_b/E of about 1e-4, since the selection is blind to flavour, which is a second reason for
the b quark in the proton.  The released models have the light quarks and leptons massless and their
Yukawa couplings at zero on the card, so there such a term vanishes and the check cannot see it at all.
--generic gives every input that is zero on the card a value of its own (validate/generic_inputs.py,
0.1 to 0.3 GeV for a Yukawa mass, and cabi), in the card dim6 and so in every evaluation.  The light
fermions stay massless, so a chirality flip takes a Yukawa vertex, and a term that enters only through
the light Yukawa couplings moves |M|^2 by at least two insertions of the smallest of them, y^2 = 2 m^2/v^2,
about 3e-7.  The script computes that size and stops unless it lies a hundred times above --tol, rather
than pass a check that could not see such a term.  An interference can also vanish where the two
amplitudes do not, as that of C_G with the Standard Model does in g g > g g, and then the relative size
of two round-offs says nothing.  So a difference below 1e-13 of the largest squared order of the amplitude at that point agrees
as well, and is counted apart.  An order at which a subprocess has no diagram agrees, and is reported.

The output has one line per subprocess and order, with the largest |M|^2 and the largest relative
difference found, and for a subprocess and order that differ a FAIL line naming the number of points
that differ and the largest of them, by its set of values and its point, with the two values, the size
and the momenta.  If the momenta of (a) and (b) differ, a mass moved with a coefficient left out, and the
line says so.  --drop takes coefficients out of those kept, to show that the check can fail: --drop cHW
on p p > w+ w- must.  The exit status is 0 when everything agrees, 1 when a point differs and 2 or 3 when
the check could not be made.  A selection that keeps every coefficient is one of those, since it leaves
nothing to compare, and it most often means that build/dim6_index.json has no entry for the model.  A
model without a dimension-six sector of its own has nothing to check, and stops here.

Everything happens in a copy of the model, the card that ./dim8 select writes included, in a work
directory that is removed after a run that agrees unless --keep names it.  Needs MadGraph at $MG5_DIR,
python3.11 for MadGraph and a Fortran compiler for the standalone output.
"""
import json
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

PARTONS = "g u c d s b u~ c~ d~ s~ b~"
FLAGS = {"--generic"}         # the options that take no value
VEV = 246.22                  # GeV, (sqrt(2) G_F)^(-1/2), for the size of a light Yukawa coupling
FLOOR = 1e-13                 # of the largest squared order at the point, as the docstring says
# The loop that replaces the one evaluation of check_sa.f, printing enough digits to read the same doubles
# back.  RN and GET_MOMENTA are those of check_sa.f, and SMATRIX_SPLITORDERS returns the chosen order in
# ANS(0) and every squared order after it.  The two values are filled in per subprocess.
DRIVER = """
      SUBROUTINE ME_POINTS(SQRTS0,PMASS)
      IMPLICIT NONE
      INCLUDE "nexternal.inc"
      INTEGER NPOINTS, NSQSO
      PARAMETER (NPOINTS=%(points)d, NSQSO=%(nsq)d)
      REAL*8 SQRTS0, PMASS(NEXTERNAL)
      REAL*8 P(0:3,NEXTERNAL), ANS(0:NSQSO), SQRTS, RN
      INTEGER IP, I, J
      EXTERNAL RN
      DO IP=1,NPOINTS
         SQRTS=SQRTS0
         IF (NINCOMING.EQ.2) SQRTS=SQRTS0*(1D0+RN(1))
         CALL GET_MOMENTA(SQRTS,PMASS,P)
         CALL SMATRIX_SPLITORDERS(P,ANS)
         DO I=1,NEXTERNAL
            WRITE (*,'(A,I6,I4,4ES25.16E3)') 'PSPOINT',IP,I,
     &         (P(J,I),J=0,3)
         ENDDO
         WRITE (*,'(A,I6,I4,100ES25.16E3)') 'MEPOINT',IP,NSQSO,
     &      (ANS(J),J=0,NSQSO)
      ENDDO
      END
"""


def stop(message):
    """The check could not be made, which is not the same as a point that differs."""
    print(message)
    sys.exit(3)


def opt(argv, flag, default):
    for i, a in enumerate(argv):
        if a == flag and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith(flag + "="):
            return a.split("=", 1)[1]
    return default


def positional(argv):
    """The arguments that are neither options nor the values of options."""
    out, skip = [], False
    for a in argv[1:]:
        if skip:
            skip = False
        elif a.startswith("--"):
            skip = "=" not in a and a not in FLAGS
        else:
            out.append(a)
    return out


def model_dir(arg):
    """The UFO directory --model names, a path or a name in models/, as ./dim8 reads it."""
    for d in (os.path.abspath(arg), os.path.join(ROOT, "models", arg)):
        if os.path.isfile(os.path.join(d, "parameters.py")):
            return d
    stop(f"{arg} is neither a UFO directory (no parameters.py) nor a model in models/")


def base_name(n):
    """The coefficient an external parameter belongs to: cuH for cuHAbs and cuHPh."""
    return re.sub(r"(Abs|Ph|Re|Im)$", "", n)


def dim6_parameters(model):
    """The external parameters of block DIM6 of a UFO."""
    out = []
    for b in re.split(r"\n(?=\w+ = Parameter\()", open(os.path.join(model, "parameters.py"), errors="replace").read()):
        m = re.match(r"(\w+) = Parameter\(name = '\w+',\s*nature = 'external'", b)
        if m and "lhablock = 'DIM6'" in b:
            out.append(m.group(1))
    return out


def kept_by_selection(process, model, work):
    """The parameters of block DIM6 that ./dim8 select --with-dim6 keeps, from the card it writes into the
    copy of the model.  A selection with nothing at all to keep writes no card, and keeps none."""
    card = "select6"
    r = subprocess.run([sys.executable, os.path.join(ROOT, "dim8"), "select", process, "--model", model,
                        "--with-dim6", "--card", card], capture_output=True, text=True, cwd=ROOT)
    with open(os.path.join(work, "select.txt"), "w") as f:
        f.write(r.stdout + r.stderr)
    if r.returncode:
        if "nothing to keep" in r.stdout:
            return set()
        stop(f"./dim8 select stopped with status {r.returncode}:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")
    kept, block = set(), None
    with open(os.path.join(model, f"restrict_{card}.dat")) as f:
        for line in f:
            b = re.match(r"\s*block\s+(\w+)", line, re.I)
            if b:
                block = b.group(1).upper()
                continue
            m = re.match(r"\s*\d+\s+(\S+)\s*#\s*(\w+)", line)
            if block == "DIM6" and m and float(m.group(1)) != 0.0:
                kept.add(m.group(2))
    return kept


def restrict_to_dim6(model, inputs=()):
    """Write the restriction card dim6 into the copy of the model, every dimension-six coefficient kept
    and the dimension-eight sector zeroed, with the inputs NAME=VALUE given (--generic) at those values."""
    r = subprocess.run([sys.executable, os.path.join(HERE, "make_restriction.py"), model, "dim6", "dim6"] + list(inputs),
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode:
        stop(f"validate/make_restriction.py stopped with status {r.returncode}:\n{r.stdout[-1500:]}\n{r.stderr[-1500:]}")


def light_yukawa_floor(yukawas):
    """The smallest relative change of |M|^2 that a term entering only through the light Yukawa couplings
    makes at these Yukawa masses, {name: GeV}: two insertions of the smallest coupling, y^2 = 2 m^2 / v^2,
    since the light fermions are massless and a chirality flip takes a Yukawa vertex.  None when there are
    none."""
    return min(2 * m * m / VEV ** 2 for m in yukawas.values()) if yukawas else None


def no_sm_tree(proc):
    """Whether the Standard Model has no tree diagram for the process, by the test of ./dim8 select."""
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    import process as P

    with open(os.path.join(ROOT, "build", "sm_vertices.json")) as f:
        return not P.sm_tree(proc, json.load(f))


def hold_w_mass(model):
    """Give the W mass of a model its Standard Model value, where it is an internal parameter that moves
    with the coefficients, and return whether it was one.  In a model with M_W as an input nothing changes."""
    path = os.path.join(model, "parameters.py")
    with open(path, errors="replace") as f:
        text = f.read()
    new, n = re.subn(r"(^MW = Parameter\(name = 'MW',\s+nature = 'internal',\s+type = 'real',\s+value = )'[^']*'",
                     r"\1'cmath.sqrt(MW2SM)'", text, flags=re.M)
    if n and "MW2SM = Parameter(" not in text:
        stop(f"{path} has an internal M_W and no MW2SM, so its Standard Model value is not known here")
    if n:
        with open(path, "w") as f:
            f.write(new)
    return bool(n)


def standalone(process, order, work, modelname, mg, py):
    """The standalone output of the process at NP^2==order, as (its directory, the subprocess directories).
    No directories means that no subprocess has a diagram at that order."""
    out = os.path.join(work, f"np{order}")
    shutil.rmtree(out, ignore_errors=True)
    script, log = os.path.join(work, f"np{order}.mg5"), os.path.join(work, f"np{order}.log")
    with open(script, "w") as f:
        f.write(f"import model {os.path.join(work, modelname)}-dim6\n"
                f"define p = {PARTONS}\ndefine j = {PARTONS}\n"
                f"generate {process} NP^2=={order}\n"
                f"output standalone {out} -f --noeps=True\n")
    with open(log, "w") as f:
        subprocess.run([py, os.path.join(mg, "bin", "mg5_aMC"), "-f", script], stdout=f, stderr=subprocess.STDOUT,
                       stdin=subprocess.DEVNULL, cwd=work)     # MadGraph leaves files where it is run from
    sub = os.path.join(out, "SubProcesses")
    pdirs = sorted(d for d in os.listdir(sub) if d.startswith("P")) if os.path.isdir(sub) else []
    if not pdirs and "NoDiagramException" not in open(log, errors="replace").read():
        stop(f"MadGraph wrote no process at NP^2=={order} and did not say that there is no diagram: see {log}")
    return out, [os.path.join(sub, d) for d in pdirs]


def build_program(pdir, points):
    """Write me_points.f into a subprocess directory, from the check_sa.f that all of them share, and compile
    it with the makefile of the directory, which takes the program and its driver as variables."""
    shared = os.path.join(os.path.dirname(pdir), "check_sa.f")
    lines = open(shared).read().split("\n")
    first = next((i for i, l in enumerate(lines) if l.strip().lower() == "call printout()"), None)
    last = None if first is None else next((i for i, l in enumerate(lines) if i > first and l.strip().lower() == "end"), None)
    if last is None:
        stop(f"{shared} is not the driver this script knows")
    m = re.search(r"PARAMETER\s*\(\s*NSQAMPSO\s*=\s*(\d+)\s*\)", open(os.path.join(pdir, "matrix.f")).read())
    if not m:
        stop(f"{pdir}/matrix.f has no squared orders, which a process with NP^2 should have")
    with open(os.path.join(pdir, "me_points.f"), "w") as f:
        f.write("\n".join(lines[:first] + ["      CALL ME_POINTS(SQRTS,PMASS)"] + lines[last:])
                + DRIVER % {"points": points, "nsq": int(m.group(1))})
    r = subprocess.run(["make", "PROG=me_points", "CHECK_SA=me_points.o", "me_points"], cwd=pdir,
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    if r.returncode or not os.path.isfile(os.path.join(pdir, "me_points")):
        stop(f"the program of {pdir} did not compile:\n{(r.stdout + r.stderr)[-1500:]}")


def number(word):
    try:
        return float(word)
    except ValueError:                         # a field that overflowed its format
        return float("nan")


def evaluate(pdir, points):
    """{point: (|M|^2 at the chosen order, the largest squared order in size, the momenta)} of one run.  A
    program that stops before its last point stops the check, whose two evaluations could not be compared."""
    r = subprocess.run(["./me_points"], cwd=pdir, capture_output=True, text=True, stdin=subprocess.DEVNULL)
    me, moms = {}, {}
    for line in r.stdout.splitlines():
        w = line.split()
        if w and w[0] == "PSPOINT":
            moms.setdefault(int(w[1]), []).append([number(x) for x in w[3:]])
        elif w and w[0] == "MEPOINT":
            vals = [number(x) for x in w[3:]]
            me[int(w[1])] = (vals[0], max(abs(x) for x in vals[1:]))
    if len(me) != points:
        stop(f"the program of {pdir} printed {len(me)} of its {points} matrix elements (status {r.returncode}):\n"
             f"{(r.stdout + r.stderr)[-1500:]}")
    return {p: me[p] + (moms.get(p, []),) for p in me}


def card_with(template, values):
    """The text of a parameter card with the parameters of block DIM6 at the values given, every other line
    as it is.  The values are written with thirteen digits, since MadGraph's card reader keeps twenty
    characters.  A label is read up to case and up to a suffix __2, since MadGraph writes a name that clashes
    with another up to case in lower case and numbers the second, as it does with C_W, cW beside the internal
    cw."""
    lines, block, seen = template.split("\n"), None, set()
    by_label = {n.lower(): n for n in values}
    for i, line in enumerate(lines):
        b = re.match(r"\s*block\s+(\w+)", line, re.I)
        if b:
            block = b.group(1).upper()
            continue
        m = re.match(r"(\s*\d+\s+)\S+(\s*#\s*(\w+).*)$", line)
        if block == "DIM6" and m:
            label = re.sub(r"__\d+$", "", m.group(3)).lower()
            name = by_label.get(label)
            if name is None:
                stop(f"block DIM6 of the parameter card holds {m.group(3)}, which is not in block DIM6 of the model")
            lines[i] = f"{m.group(1)}{values[name]:.12e}{m.group(2)}"
            seen.add(name)
    lack = sorted(set(values) - seen)
    if lack:
        stop(f"the parameter card of the restricted model lacks {', '.join(lack)}, which this check would not test")
    return "\n".join(lines)


def random_values(names, rnd):
    """One random set: real coefficients of random sign and of size between 0.2 and 1.2, moduli of that size
    and phases anywhere but near zero."""
    out = {}
    for n in names:
        if n.endswith("Ph"):
            out[n] = rnd.choice((-1, 1)) * rnd.uniform(0.1, 3.0)
        elif n.endswith("Abs"):
            out[n] = rnd.uniform(0.2, 1.2)
        else:
            out[n] = rnd.choice((-1, 1)) * rnd.uniform(0.2, 1.2)
    return out


class Tally:
    """What one subprocess showed at one order."""

    def __init__(self):
        self.size = 0.0                        # the largest |M|^2
        self.worst = 0.0                       # the largest relative difference outside the rounding floor
        self.rounding = 0                      # the points that agree through the floor alone
        self.fails = []                        # (relative difference, set, point, a, b, momenta of a and of b)

    def add(self, iset, one, other, tol):
        """The two runs (a) = one and (b) = other, point by point."""
        for p in sorted(one):
            a, sa, ma = one[p]
            b, sb, mb = other[p]
            diff, big = abs(a - b), max(abs(a), abs(b))
            rel = diff / big if big else 0.0
            if big > self.size:
                self.size = big
            if a == b or diff <= tol * big:
                self.worst = max(self.worst, rel)
            elif diff <= FLOOR * max(sa, sb):
                self.rounding += 1
            else:
                # a value that is not a number counts as a difference, the largest of all
                self.fails.append((rel if rel == rel else float("inf"), iset, p, a, b, ma, mb))
                if rel == rel:
                    self.worst = max(self.worst, rel)

    def line(self):
        return (f"largest |M|^2 {self.size:.2e}, largest relative difference {self.worst:.2e}"
                + (f", {self.rounding} points at the rounding of the larger squared orders" if self.rounding else ""))


def report_fail(order, name, tally, total):
    """The FAIL line of a subprocess and order that differ, with the point that differs most."""
    rel, iset, p, a, b, ma, mb = max(tally.fails, key=lambda f: f[0])
    print(f"FAIL NP^2=={order} {name}: {len(tally.fails)} of {total} points differ, the most at set {iset + 1} of the "
          f"values, point {p}: |M|^2 = {a:.16e} with every coefficient on and {b:.16e} with those kept, a relative "
          f"difference of {rel:.2e}")
    moved = [abs(x - y) for pa, pb in zip(ma, mb) for x, y in zip(pa, pb)]
    if moved and max(moved) > 1e-9:
        print(f"     the momenta differ by up to {max(moved):.2e} GeV, so a mass moves with a coefficient left out")
    for k, leg in enumerate(ma, 1):
        print(f"     leg {k} (E, px, py, pz): " + " ".join(f"{x:+.10e}" for x in leg))


def main(argv):
    args = positional(argv)
    if not args:
        print(__doc__)
        return 2
    process = args[0]
    if re.search(r"\bnp\b", process, re.I) or "," in process or "{" in process:
        print("give the process with no NP order, no decay chain and no polarisation mark: this script adds NP^2==1 "
              "and NP^2==2 itself, MadGraph takes no squared order in a decay chain, and the marks do not change the "
              "selection")
        return 2
    from freeze_dim6_inputs import in_base

    source = model_dir(opt(argv, "--model", "models/dim68_mw"))
    modelname = os.path.basename(source)
    names = dim6_parameters(source)
    if not set(names) - in_base():
        print(f"{modelname} has no dimension-six sector of its own, and so no dimension-six selection to check")
        return 2
    mg = os.environ.get("MG5_DIR")
    if not mg or not os.path.isfile(os.path.join(mg, "bin", "mg5_aMC")):
        print("set MG5_DIR to the MadGraph directory (the one holding bin/mg5_aMC)")
        return 2
    py = shutil.which("python3.11") or sys.executable
    nsets, npoints = int(opt(argv, "--sets", "3")), int(opt(argv, "--points", "4"))
    seed, tol = int(opt(argv, "--seed", "1")), float(opt(argv, "--tol", "1e-10"))
    from generic_inputs import zero_inputs
    inputs = zero_inputs(source) if "--generic" in argv else {}
    floor = light_yukawa_floor(zero_inputs(source, "YUKAWA")) if inputs else None
    if floor is not None and floor < 100 * tol:
        stop(f"--generic: a term through the light Yukawa couplings moves |M|^2 by {floor:.1e} at the least, less than "
             f"a hundred times the tolerance {tol:g}, so the check could not see it.  Give --tol below {floor / 100:.1e}.")
    drop = {x for x in opt(argv, "--drop", "").split(",") if x}
    keep_dir = opt(argv, "--keep", None)
    work = os.path.abspath(keep_dir) if keep_dir else tempfile.mkdtemp(prefix="select6_")
    os.makedirs(work, exist_ok=True)
    open(os.path.join(work, ".metadata_never_index"), "w").close()   # no Spotlight on a run directory
    model = os.path.join(work, modelname)
    shutil.rmtree(model, ignore_errors=True)
    shutil.copytree(source, model, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.pkl", "*.log", "*.cmd"))

    # the selection, and what is left out of it
    kept = kept_by_selection(process, model, work)
    if len(kept) == len(names):
        stop(f"{process} in {modelname}: the selection keeps every dimension-six coefficient, so the two evaluations "
             "would be one card and the check could not fail.  Does build/dim6_index.json have an entry for this model "
             "(python3 validate/dim6_index.py)?")
    unknown = sorted(drop - {base_name(n) for n in kept})
    if unknown:
        print(f"--drop: not among the coefficients the selection keeps: {', '.join(unknown)}")
        return 2
    kept = {n for n in kept if base_name(n) not in drop}
    print(f"{process} in {modelname}: the selection keeps {len({base_name(n) for n in kept})} of the "
          f"{len({base_name(n) for n in names})} dimension-six coefficients, {len(kept)} of the {len(names)} card "
          "entries" + (f", with {', '.join(sorted(drop))} taken out of them, so this run should fail" if drop else ""))
    print(f"{nsets} sets of values, {npoints} phase-space points in each subprocess, relative tolerance {tol:g}")
    if inputs:
        print("at generic inputs: " + ", ".join(f"{k} = {v:.4f}" for k, v in sorted(inputs.items()))
              + (f"; a term through the light Yukawa couplings moves |M|^2 by at least {floor:.1e}, {floor / tol:.0e} times "
                 "the tolerance" if floor is not None else ""))
    restrict_to_dim6(model, [f"{k}={v!r}" for k, v in sorted(inputs.items())])
    if no_sm_tree(process) and hold_w_mass(model):
        print("no Standard Model tree: M_W is at its Standard Model value in both evaluations, since its shift would "
              "be of order 1/Lambda^6 on the square")

    # one standalone output per order, one program per subprocess, and the two cards of each set of values
    rnd = random.Random(seed)
    sets = [random_values(names, rnd) for _ in range(nsets)]
    tallies = {1: {}, 2: {}}
    for order in (1, 2):
        out, pdirs = standalone(process, order, work, modelname, mg, py)
        if not pdirs:
            continue
        for pdir in pdirs:
            build_program(pdir, npoints)
            tallies[order][os.path.basename(pdir)] = Tally()
        card = os.path.join(out, "Cards", "param_card.dat")
        template = open(card).read()
        for iset, values in enumerate(sets):
            runs = []
            for chosen in (values, {n: (v if n in kept else 0.0) for n, v in values.items()}):
                with open(card, "w") as f:
                    f.write(card_with(template, chosen))
                runs.append({pdir: evaluate(pdir, npoints) for pdir in pdirs})
            for pdir in pdirs:
                tallies[order][os.path.basename(pdir)].add(iset, runs[0][pdir], runs[1][pdir], tol)

    # one line per subprocess and order, then the subprocesses and orders that differ
    every = sorted(set(tallies[1]) | set(tallies[2]))
    if not every:
        print("no subprocess has a diagram at NP^2==1 or NP^2==2, so there is nothing to compare")
    for order in (1, 2):
        print(f"NP^2=={order}: {len(tallies[order])} subprocesses with a diagram")
        for name in every:
            print(f"  {name:30s} " + (tallies[order][name].line() if name in tallies[order]
                                      else "no diagram at this order, which agrees"))
    failed = [(order, name) for order in (1, 2) for name in sorted(tallies[order]) if tallies[order][name].fails]
    for order, name in failed:
        report_fail(order, name, tallies[order][name], nsets * npoints)
    if failed:
        print(f"FAIL: {len(failed)} subprocess and order pairs differ.  Work directory: {work}")
        return 1
    print(f"PASS: with the {len(names) - len(kept)} card entries the selection leaves out at zero, |M|^2 is unchanged "
          "at NP^2==1 and NP^2==2 in every subprocess")
    if keep_dir:
        print(f"work directory: {work}")
    else:
        shutil.rmtree(work, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
