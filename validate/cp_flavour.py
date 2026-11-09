#!/usr/bin/env python3
"""The CP test of validate/cp_rates.py for the flavour structures of block DIM8F, at generic inputs.

    validate/cp_flavour.py --prepare [--procs tt,ww,...]
    validate/cp_flavour.py [--nev 10000] [--lam 3000] [--procs tt,ww,...] [--keep]
    validate/cp_flavour.py --report [--lam 3000]
    validate/cp_flavour.py --full ...       (any of the above, with process directories of the whole model)

cp_rates.py switches its CP-odd and CP-even sets on at the inputs of the card, where the light Yukawa
couplings and the Cabibbo angle are zero.  The flavour structures of block DIM8F are Yukawa insertions
(Y Y^dagger, y^4) and crossed contractions of four-fermion operators, so there they act on t and b lines
only, and no process of cp_rates.py has one.  Apart from the structures of the input relations, which
shift G_F, its DIM8F entries have no vertex in its processes, and its result says nothing about their
parities.  This runs the same test with only DIM8F switched on, at generic inputs (validate/
generic_inputs.py: each light Yukawa mass and cabi between 0.1 and 0.3), in p p > t t~ for the y_t^2
structures and in the processes of cp_rates.py that are their own CP conjugate.

--prepare
    Writes four restriction cards (validate/make_restriction.py) in a copy of the model of its own (its
    large files linked), so that the cards of the model directory stay as they are: the CP-odd DIM8F
    entries at generic inputs, the CP-even ones, both, and both at the inputs of the card.  The parities
    are those of gen/cp_parity.coefficient_sets, as in cp_rates.py.  The structures of the input relations
    (gen/input_scheme_formulae*.json) are left out of every card: they shift G_F, and with it every
    electroweak amplitude, through a CP-even route that has nothing to do with the flavour structures, and
    would make the CP-even control large whatever those do.  One MadGraph session per card, driven from
    Python so that a process without a diagram is a result and not the end of the session, counts the
    diagrams of each process with one DIM8F vertex (NP==2).  The session of the card with both sets at
    generic inputs also writes the process directory (NP^2==2, the interference) of each process that has
    such diagrams.  Beside the sessions, the card with both sets goes through fusion_problems of
    tests/test_restriction_cards.py: MadGraph fuses couplings that agree at the card's placeholder values,
    which must not happen to couplings that differ at the values of a run.
(default)
    Runs each process twice, with the CP-odd DIM8F entries at 1 and with the CP-even ones, every other
    coefficient at zero, Lam = 3 TeV, the generic inputs, and the settings and cuts of cp_rates.py, and
    appends sigma +- error to validate/cp_flavour_<model>_lam<Lam>.tsv.  A process directory is removed
    once both of its rows are written, unless --keep.
--report
    One line per process: both interferences, the diagram counts, and a verdict.  PASS needs the CP-odd
    interference consistent with zero (below three standard deviations) and the CP-even one nonzero at
    five or more.  With the CP-even one below that the test could not have failed and the line says
    VACUOUS; with no CP-odd diagram there is no CP-odd assignment to test and it says that too.

--full
    The process directories come from the whole model, as in cp_rates.py, written in one session with no
    restriction card, instead of from the card with both sets: MadGraph's restriction of this model at
    generic inputs can take hours.  The whole model keeps every coupling whatever the inputs, so the generic
    inputs set at the run reach the same structures.  The results go to cp_flavour_<model>_full_lam<Lam>.tsv,
    the diagram counts of --prepare are used when they are there.

p p > t t~ is its own CP conjugate, like the processes taken from cp_rates.py (its SELF_CONJUGATE), so a
CP-odd interference cancels in the total rate; cp_rates.py sets out why.
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
import random
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "gen"))
import cp_rates as C  # noqa: E402
from generic_inputs import zero_inputs  # noqa: E402

PROCS = {"tt": "p p > t t~", **{t: p for t, p in C.PROCS.items() if p in C.SELF_CONJUGATE}}
MODEL = C.MODEL
WORK = os.path.join(os.path.dirname(C.WORK), "cpf" + C.MTAG)
CARDS = {"odd": ("cpf8odd", True), "even": ("cpf8even", True), "both": ("cpf8both", True),
         "card": ("cpf8card", False)}             # (card name, at generic inputs)
FULL = "--full" in sys.argv
DIRS = os.path.join(WORK, "dirs_full" if FULL else "dirs")
COMMON = ["ebeam1=6800", "ebeam2=6800", "hel_recycling=False", "use_syst=False", "sde_strategy=2"]


def out_path(lam):
    return os.path.join(ROOT, "validate", f"cp_flavour{C.MTAG}{'_full' if FULL else ''}_lam{int(float(lam))}.tsv")


def flavour_sets():
    """The CP-odd and CP-even DIM8F card entries of cp_parity.coefficient_sets, without those of the input
    relations; the left-out ones; and the DIM8F entries that neither set holds."""
    odd, even = C.cp_sets()
    params = open(os.path.join(MODEL, "parameters.py"), errors="replace").read()
    f8 = set(re.findall(r"name = '(\w+)',\s*nature = 'external',\s*type = '\w+',\s*value = [^,]*,"
                        r"\s*texname = '[^']*',\s*lhablock = 'DIM8F'", params))
    rel = set()
    for f in glob.glob(os.path.join(ROOT, "gen", "input_scheme_formulae*.json")):
        rel |= set(re.findall(r"\bc8\w+", json.dumps(json.load(open(f)))))
    left = sorted(n for n in f8 if n in rel or re.sub(r"(Re|Im)$", "", n) in rel)
    pick = lambda s: sorted({n for n in s if n in f8 and n not in left})  # noqa: E731
    return pick(odd), pick(even), left, sorted(f8 - set(odd) - set(even) - set(left))


def private_model():
    """A copy of the model for the cards of this script: small files copied, large ones linked."""
    d = os.path.join(WORK, "model", os.path.basename(MODEL.rstrip("/")))
    if not os.path.isdir(d):
        os.makedirs(d)
        for f in sorted(os.listdir(MODEL)):
            src = os.path.join(MODEL, f)
            if not os.path.isfile(src) or f.startswith("restrict_") or f.endswith((".pkl", ".pyc", ".log")):
                continue
            if os.path.getsize(src) > 10 ** 7:
                os.symlink(os.path.realpath(src), os.path.join(d, f))
            else:
                shutil.copy(src, d)
    return d


def head_hash(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read(1 << 20)).hexdigest()


def slim(d):
    """Link the large files of the model copy MadGraph writes into a process directory (bin/internal/ufomodel)
    to the model's own, when they are the same file: half a gigabyte a directory otherwise."""
    u = os.path.join(d, "bin", "internal", "ufomodel")
    for f in ("couplings.py", "vertices.py", "lorentz.py"):
        p, src = os.path.join(u, f), os.path.join(MODEL, f)
        if os.path.isfile(p) and not os.path.islink(p) and os.path.getsize(p) == os.path.getsize(src) \
                and head_hash(p) == head_hash(src):
            os.remove(p)
            os.symlink(os.path.realpath(src), p)


def session(model, card, result, outdir, tags):
    """One MadGraph session on model-card: the number of diagrams with one DIM8F vertex of each process, and
    with outdir the interference process directory of each process that has some."""
    sys.path.insert(0, C.MG)
    import logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    import madgraph.interface.master_interface as MI

    mg = MI.MasterCmd()
    mg.no_notification()

    def run(line):
        mg.exec_cmd(line, errorhandling=False, printcmd=False, precmd=True, postcmd=True)

    run(f"import model {model}" + (f"-{card}" if card != "-" else ""))     # "-": the whole model
    res = {}
    for tag in tags:
        proc = PROCS[tag]
        res[tag] = {}
        if card != "-":
            try:
                run(f"generate {proc} NP==2")
                res[tag] = {"diagrams": sum(len(a.get("diagrams")) for a in mg._curr_amps)}
            except Exception as err:   # NoDiagramException above all
                res[tag] = {"diagrams": 0, "why": f"{type(err).__name__}: {str(err)[:200]}"}
        if outdir and (card == "-" or res[tag]["diagrams"]):
            d = os.path.join(outdir, tag)
            try:
                run(f"generate {proc} NP^2==2")
                run(f"output {d} -f")
            except Exception as err:
                res[tag]["output"] = f"{type(err).__name__}: {str(err)[:200]}"
            if os.path.exists(os.path.join(d, "bin", "generate_events")):
                open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
                    "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
                slim(d)
                res[tag]["dir"] = d
        print(f"[{card}] {proc}: {res[tag]}", flush=True)
        json.dump(res, open(result, "w"), indent=1)
    return 0


def guard(model, card):
    sys.path.insert(0, os.path.join(ROOT, "tests"))
    import test_restriction_cards as T
    found = T.fusion_problems(T.read_ufo(model), os.path.join(model, f"restrict_{card}.dat"), random.Random(1))
    print(f"fusion check of restrict_{card}.dat: {len(found)} couplings fused or removed wrongly"
          + (f", the first: {found[:3]}" if found else ""), flush=True)
    return 1 if found else 0


def prepare(tags):
    os.makedirs(WORK, exist_ok=True)
    if FULL:
        cwd = os.path.join(WORK, "s_full")
        os.makedirs(cwd, exist_ok=True)
        with open(os.path.join(WORK, "session_full.log"), "w") as log:
            rc = subprocess.run([C.PY, os.path.abspath(__file__), "--session", MODEL, "-",
                                 os.path.join(WORK, "reach_full.json"), DIRS] + tags,
                                stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=cwd).returncode
        made = [t for t in tags if os.path.exists(os.path.join(DIRS, t, "bin", "generate_events"))]
        print(f"whole model: process directories for {' '.join(made) or 'no process'} in {DIRS}"
              + (f"; none for {' '.join(t for t in tags if t not in made)}" if len(made) < len(tags) else ""))
        return rc or (0 if len(made) == len(tags) else 1)
    odd, even, left, unplaced = flavour_sets()
    print(f"DIM8F entries: {len(odd)} CP odd, {len(even)} CP even, {len(left)} of the input relations left out "
          f"({' '.join(left)}), {len(unplaced)} in neither set" + (f" ({' '.join(unplaced[:20])})" if unplaced else ""),
          flush=True)
    json.dump({"odd": odd, "even": even, "left": left}, open(os.path.join(WORK, "sets.json"), "w"), indent=1)
    pm = private_model()
    gen = [f"{k}={v!r}" for k, v in sorted(zero_inputs(MODEL).items())]
    print("generic inputs: " + " ".join(gen), flush=True)
    import make_restriction as MR
    keep = {"odd": odd, "even": even, "both": odd + even, "card": odd + even}
    for key, (card, generic) in CARDS.items():
        rc = MR.main(["make_restriction", pm, card] + keep[key] + (gen if generic else []))
        if rc:
            print(f"make_restriction stopped on card {card} with {rc}")
            return rc
    dirs = DIRS
    run = []
    for key, (card, _) in CARDS.items():
        log = open(os.path.join(WORK, f"session_{key}.log"), "w")
        cwd = os.path.join(WORK, f"s_{key}")      # MadGraph leaves files where it runs, one directory a session
        os.makedirs(cwd, exist_ok=True)
        run.append(subprocess.Popen([C.PY, os.path.abspath(__file__), "--session", pm, card,
                                     os.path.join(WORK, f"reach_{key}.json"), dirs if key == "both" else "-"] + tags,
                                    stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=cwd))
    log = open(os.path.join(WORK, "guard.log"), "w")
    g = subprocess.Popen([C.PY, os.path.abspath(__file__), "--guard", pm, CARDS["both"][0]],
                         stdout=log, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL, cwd=WORK)
    codes = [p.wait() for p in run] + [g.wait()]
    reach = {}
    for key in CARDS:
        path = os.path.join(WORK, f"reach_{key}.json")
        for tag, r in (json.load(open(path)) if os.path.exists(path) else {}).items():
            reach.setdefault(tag, {})[key] = r
    json.dump(reach, open(os.path.join(WORK, "reach.json"), "w"), indent=1)
    print(open(os.path.join(WORK, "guard.log")).read().strip().split("\n")[-1])
    print("diagrams with one DIM8F vertex (NP==2): CP-odd / CP-even / both at generic inputs; both at the inputs "
          "of the card")
    for tag in tags:
        r = reach.get(tag, {})
        n = [str(r.get(k, {}).get("diagrams", "?")) for k in CARDS]
        print(f"  {PROCS[tag]:16s} {n[0]:>5s} / {n[1]:>5s} / {n[2]:>5s};  {n[3]:>5s}"
              + ("   process directory written" if r.get("both", {}).get("dir") else ""))
    bad = [c for c in codes if c]
    if bad:
        print(f"{len(bad)} of the {len(codes)} sessions and checks stopped with an error: see {WORK}/*.log")
    return 1 if bad else 0


def card_keys(path):
    return {re.sub(r"__\d+$", "", m.group(1)).lower(): m.group(1)
            for m in re.finditer(r"^\s*\d+\s+\S+\s*#\s*(\w+)", open(path).read(), re.M)}


def runs(tags, nev, lam, keep):
    if not os.path.exists(os.path.join(WORK, "sets.json")):
        print(f"no {os.path.join(WORK, 'sets.json')}: run validate/cp_flavour.py --prepare first")
        return 2
    S = json.load(open(os.path.join(WORK, "sets.json")))
    path = os.path.join(WORK, "reach.json")
    reach = json.load(open(path)) if os.path.exists(path) else {}
    # a part with no diagram is not run; without the counts (--full before --prepare is done) every part is
    has = lambda tag, part: reach.get(tag, {}).get(part, {}).get("diagrams", None if FULL else 0) != 0  # noqa: E731
    gen = zero_inputs(MODEL)
    out = out_path(lam)
    if not os.path.exists(out):
        open(out, "w").write("process\tset\tn\tsigma_pb\terror_pb\tnevents\n")
    failed = 0
    for tag in tags:
        proc, d = PROCS[tag], os.path.join(DIRS, tag)
        done = {tuple(l.split("\t")[:2]) for l in open(out).read().split("\n")[1:] if l}
        if not os.path.exists(os.path.join(d, "bin", "generate_events")):
            print(f"[{tag}] no process directory: no DIM8F diagram at generic inputs, or --prepare was not run")
            continue
        have = card_keys(os.path.join(d, "Cards", "param_card.dat"))
        log = os.path.join(WORK, f"{tag}.log")
        for name, part in (("cpodd", "odd"), ("cpeven", "even")):
            if (proc, name) in done:
                continue
            on = [have[w.lower()] for w in S[part] if w.lower() in have]
            if not on or not has(tag, part):
                print(f"[{tag}] {name}: no structure of the set has a diagram in this process", flush=True)
                continue
            sets = ([f"nevents={nev}"] + COMMON + ["dim8_all=0", f"Lam={lam}"] + [f"{w}=1" for w in on]
                    + [f"{have[k.lower()]}={v!r}" for k, v in sorted(gen.items()) if k.lower() in have]
                    + C.CUTS.get(proc, []))
            if C.run([C.PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d] + sets, log):
                print(f"[{tag}] {name}: card error, see {log}", flush=True)
                failed += 1
                continue
            before = os.path.getsize(log)
            C.run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
            txt = open(log, errors="replace").read()[before:]
            m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
            if not m or "interrupted with error" in txt:
                print(f"[{tag}] {name}: MadGraph gave no cross section, see {log}", flush=True)
                failed += 1
                continue
            x, e = float(m[-1][0]), float(m[-1][1])
            with open(out, "a") as fh:
                fh.write(f"{proc}\t{name}\t{len(on)}\t{x:.6g}\t{e:.6g}\t{nev}\n")
            print(f"[{tag}] {name:6s} {len(on):4d} entries  {x:12.5g} +- {e:.3g} pb", flush=True)
        done = {tuple(l.split("\t")[:2]) for l in open(out).read().split("\n")[1:] if l}
        if not keep and all((proc, n) in done or not has(tag, p) for n, p in (("cpodd", "odd"), ("cpeven", "even"))):
            shutil.rmtree(d)
            print(f"[{tag}] removed {d}", flush=True)
    return 1 if failed else 0


def report(lam):
    out = out_path(lam)
    rows = {}
    if os.path.exists(out):
        for l in open(out).read().split("\n")[1:]:
            if l:
                p, s, n, x, e, _ = l.split("\t")
                rows[(p, s)] = (int(n), float(x), float(e))
    reach = json.load(open(os.path.join(WORK, "reach.json"))) if os.path.exists(os.path.join(WORK, "reach.json")) else {}
    g = os.path.join(WORK, "guard.log")
    print(open(g).read().strip().split("\n")[-1] if os.path.exists(g) else "no fusion check of the card was run")
    tally = {}
    for tag, proc in PROCS.items():
        r = reach.get(tag, {})
        n = {k: r.get(k, {}).get("diagrams") for k in CARDS}
        q = {k: "?" if v is None else v for k, v in n.items()}
        dg = f"DIM8F diagrams {q['odd']} CP-odd / {q['even']} CP-even at generic inputs, {q['card']} at the card's inputs"
        o, ev = rows.get((proc, "cpodd")), rows.get((proc, "cpeven"))
        sd = lambda r: None if r is None else abs(r[1]) / r[2] if r[2] > 0 else 0.0 if r[1] == 0 else float("inf")  # noqa: E731
        so, se = sd(o), sd(ev)
        num = lambda t, s, what: f"{what} {t[1]:.4g} +- {t[2]:.2g} pb ({s:.1f} sd, {t[0]} entries)" if t else f"{what} not run"  # noqa: E731
        if n["both"] == 0:
            verdict = "NONE"
            text = "no DIM8F diagram at generic inputs, so not a test"
        elif ev is None and o is None and not FULL and not r.get("both", {}).get("dir"):
            verdict = "NONE"
            text = f"MadGraph wrote no interference process ({r.get('both', {}).get('output', 'no reason given')})"
        elif ev is None or (n["odd"] != 0 and o is None):
            verdict = "INCOMPLETE"
            text = f"{num(ev, se or 0, 'CP even')}; {num(o, so or 0, 'CP odd')}"
        elif o is not None and so >= 3:
            verdict = "FAIL"
            text = f"the CP-odd interference is nonzero: {num(o, so, 'CP odd')}; {num(ev, se, 'CP even')}"
        elif se < 5:
            verdict = "VACUOUS"
            text = (f"the CP-even interference is not measurably nonzero, so the test could not have failed: "
                    f"{num(ev, se, 'CP even')}; {num(o, so or 0, 'CP odd')}")
        elif o is None:
            verdict = "VACUOUS"
            text = f"no CP-odd structure has a diagram, so there is no CP-odd assignment to test; {num(ev, se, 'CP even')}"
        else:
            verdict = "PASS"
            text = f"{num(ev, se, 'CP even')}; {num(o, so, 'CP odd')}, consistent with zero"
        tally[verdict] = tally.get(verdict, 0) + 1
        print(f"{verdict} B3 DIM8F {proc} (generic inputs, Lam = {int(float(lam))} GeV): {text}; {dg}")
    print("B3 DIM8F: " + ", ".join(f"{v} {k}" for k, v in sorted(tally.items())))
    return 0 if set(tally) <= {"PASS", "NONE"} else 1


def opt(argv, flag, default):
    return argv[argv.index(flag) + 1] if flag in argv else default


def main(argv) -> int:
    if "--session" in argv:
        i = argv.index("--session")
        model, card, result, outdir = argv[i + 1:i + 5]
        return session(model, card, result, None if outdir == "-" else outdir, argv[i + 5:])
    if "--guard" in argv:
        i = argv.index("--guard")
        return guard(argv[i + 1], argv[i + 2])
    lam = opt(argv, "--lam", "3000")
    if "--report" in argv:
        return report(lam)
    tags = opt(argv, "--procs", ",".join(PROCS)).split(",")
    if set(tags) - set(PROCS):
        print(f"unknown process tags {sorted(set(tags) - set(PROCS))}, the tags are {' '.join(PROCS)}")
        return 2
    if "--prepare" in argv:
        return prepare(tags)
    return runs(tags, int(opt(argv, "--nev", "10000")), lam, "--keep" in argv)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
