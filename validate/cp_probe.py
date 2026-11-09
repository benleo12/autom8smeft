#!/usr/bin/env python3
"""Which operators actually decouple from a CP-even rate, measured one set at a time.

    validate/cp_probe.py [--nev 4000] [--proc "p p > w+ w-"] [--lam 3000]

The CP test requires the CP-odd set to give zero interference with the Standard Model in a CP-even rate.
When it does not, the question is which operators are misassigned, and that is answered by
measuring candidate sets rather than by re-reading the rule.  This runs, in one process
directory, the sets that differ between the two ways of counting dual field strengths:

    whole-row   the number of ``\\widetilde`` characters in the printed row is odd
    per-term    the number of dual field strengths per term of the parsed operator is odd
    moved       the operators the two rules disagree about
    class14     the subset of ``moved`` in class 14, which is where most of them sit

A set whose interference is consistent with zero is CP odd.  A set that gives a per-cent-level
interference is not.

Each set holds the flavour structures of block DIM8F of its operators too.  Under the derivation a
structure has the parity gen/cp_parity.coefficient_sets gives it, that of its operator for the part "re"
and the other one for "im"; under dual counting the same rule is applied to the dual-count parity of the
operator.  At the inputs of the card the light Yukawa couplings and the Cabibbo angle are zero, so the
structures that are Yukawa insertions or crossed contractions have no vertex in p p > w+ w- and add
nothing there; validate/cp_flavour.py tests their parities at generic inputs.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "validate"))
sys.path.insert(0, os.path.join(ROOT, "gen"))
MG = os.environ.get("MG5_DIR", os.path.expanduser("~/Downloads/MG5_aMC_v3_5_3"))
PY = "python3.11"
MODEL = os.environ.get("DIM8_MODEL", os.path.join(ROOT, "models", "dim8_mw"))
# each model keeps its own process directories and results files, validate/cp_probe_<model>_lam<Lam>.tsv;
# models/dim8_is keeps the names it had when it was the default (cp_probe.tsv at 1 TeV)
MTAG = "" if os.path.basename(MODEL.rstrip("/")) == "dim8_is" else "_" + os.path.basename(MODEL.rstrip("/"))
WORK = os.path.join(os.environ.get("DIM8_BUILD", os.path.expanduser("~/dim8auto_build")), "v11probe" + MTAG)
OUT = os.path.join(ROOT, "validate", "cp_probe.tsv")
NICE = ["nice", "-n", "19"]


def sets():
    """Candidate CP-odd sets, as param-card entries.

    The classification the model uses is the field-by-field C times P derivation of
    gen/cp_parity.py.  The rule it replaces is dual counting, and the point of this probe is that
    the two can be told apart by measurement: a CP-odd operator cannot interfere with the
    Standard Model in a CP-even rate, so whichever set gives zero is the CP-odd one.

        derived     the derivation's CP-odd set
        dualcount   the set obtained by counting dual field strengths per term
        onlyderived operators the derivation calls odd and dual counting calls even
        onlydual    operators dual counting calls odd and the derivation calls even
    """
    sys.path.insert(0, os.path.join(ROOT, "gen"))
    sys.path.insert(0, os.path.join(ROOT, "validate"))
    import cp_parity, cardnames
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    cp = cp_parity.table()
    # dual_count reads the encoded operator (its terms and field strengths), not a catalogue entry
    from operators import OPS
    dual = {op.name: cp_parity.dual_count(op) for op in OPS}

    def blocks(parity, which):
        src = cp if which == "derived" else dual
        return [w for e in idx if not cp_parity.baryon_violating() & set(e["ops"]) and e["hc_mode"] == "real"
                and {src[o] for o in e["ops"]} == {parity} for w in e["wcs"]]

    d, u = set(blocks("odd", "derived")), set(blocks("odd", "dual"))
    # the flavour structures of the same operators (block DIM8F), with their parts' parities
    import basis
    import emit_flavour as EF
    odd8, even8 = cp_parity.coefficient_sets(basis.of_model(MODEL))
    placed = {**dict.fromkeys(even8, "even"), **dict.fromkeys(odd8, "odd")}
    flip = {"even": "odd", "odd": "even"}
    scope = {o for e in idx if not cp_parity.baryon_violating() & set(e["ops"]) and e["hc_mode"] == "real"
             for o in e["ops"]}
    structures = EF.load_structures()
    for op in OPS:
        if op.name not in scope or op.name not in structures:
            continue
        for s in EF.structure_parameters(op, structures[op.name]):
            for name, part, parity in s["externals"]:
                if name not in placed:
                    continue
                if placed[name] != parity:
                    raise SystemExit(f"{name}: parity {parity} from gen/emit_flavour.py, {placed[name]} from "
                                     "gen/cp_parity.coefficient_sets")
                if parity == "odd":
                    d.add(name)
                if (dual[op.name] if part == "re" else flip[dual[op.name]]) == "odd":
                    u.add(name)
    out = {"derived": sorted(d), "dualcount": sorted(u),
           "onlyderived": sorted(d - u), "onlydual": sorted(u - d)}
    return {k: cardnames.expand(MODEL, v) for k, v in out.items() if v}


def run(cmd, log):
    with open(log, "a") as fh:
        fh.write("\n$ " + " ".join(cmd[:6]) + (" ..." if len(cmd) > 6 else "") + "\n")
        return subprocess.run(NICE + cmd, stdout=fh, stderr=subprocess.STDOUT,
                              stdin=subprocess.DEVNULL, check=False).returncode


def main(argv) -> int:
    nev = int(argv[argv.index("--nev") + 1]) if "--nev" in argv else 4000
    proc = argv[argv.index("--proc") + 1] if "--proc" in argv else "p p > w+ w-"
    lam = argv[argv.index("--lam") + 1] if "--lam" in argv else "3000"
    # one process directory per process, and one results file per scale (the runs at 1 TeV are the
    # original cp_probe.tsv), so that a second process or scale never reuses the first one's
    tag = re.sub(r"[^A-Za-z0-9]", "_", proc.replace("+", "p").replace("-", "m"))
    out = OUT if float(lam) == 1000 and not MTAG else OUT.replace(".tsv", f"{MTAG}_lam{int(float(lam))}.tsv")
    S = sets()
    for k, v in S.items():
        print(f"{k:12s} {len(v):4d} coefficients", flush=True)
    os.makedirs(WORK, exist_ok=True)
    d = os.path.join(WORK, tag)
    log = os.path.join(WORK, tag + ".log")
    if not os.path.exists(os.path.join(d, "bin", "generate_events")):
        sc = os.path.join(WORK, tag + ".mg5")
        open(sc, "w").write(f"import model {MODEL}\ngenerate {proc} NP^2==2\noutput {d} -f\n")
        run([PY, os.path.join(MG, "bin", "mg5_aMC"), "-f", sc], log)
        if not os.path.exists(os.path.join(d, "bin", "generate_events")):
            print("generation failed, see", log)
            return 1
        open(os.path.join(d, "Cards", "me5_configuration.txt"), "a").write(
            "run_mode = 0\nnb_core = 1\nautomatic_html_opening = False\n")
    if not os.path.exists(out):
        open(out, "w").write("process\tset\tn\tsigma_pb\terror_pb\n")
    done = {tuple(l.split("\t")[:2]) for l in open(out).read().split("\n")[1:] if l}
    jobs = ["derived", "dualcount", "onlyderived", "onlydual"]
    if "--families" in argv:
        # The 27 disputed operators AND their family partners.  Within a family the members
        # differ by the relative sign of the two-term bracket and by an explicit factor of i,
        # and the question is whether the CP parity alternates along the family rather than
        # following the dual count; that can only be seen with the partners in the sample.
        import re as _re
        idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
        bywc = {w: e for e in idx for w in e["wcs"]}
        disputed = set(S.get("onlyderived", [])) | set(S.get("onlydual", []))
        base = {_re.sub(r"\^\{\(\d+\)\}$", "", bywc[w]["ops"][0]) for w in disputed if w in bywc}
        import cardnames as _cn
        import cp_parity as _cp
        fam = _cn.expand(MODEL, [w for e in idx if not _cp.baryon_violating() & set(e["ops"])
                                 and e["hc_mode"] == "real"
                                 and _re.sub(r"\^\{\(\d+\)\}$", "", e["ops"][0]) in base
                                 for w in e["wcs"]])
        for w in sorted(set(fam)):
            S["op:" + w] = [w]
            jobs.append("op:" + w)
        print(f"family mode: {len(set(fam))} coefficients in {len(base)} families", flush=True)
    if "--per-operator" in argv:
        # One coefficient at a time over the disputed set.  A CP-odd operator cannot interfere
        # with the Standard Model in a CP-even rate, so this measures the parity of each rather
        # than testing a rule: the set-level numbers say only that the set is mixed.
        idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
        lab = {w: e["ops"][0] for e in idx for w in e["wcs"]}
        for w in S.get("onlyderived", []) + S.get("onlydual", []):
            S["op:" + w] = [w]
            jobs.append("op:" + w)
        print(f"per-operator mode: {len(S.get('onlyderived', [])) + len(S.get('onlydual', []))} coefficients", flush=True)
    failed = 0
    for name in jobs:
        if (proc, name) in done or not S.get(name):
            continue
        # sde_strategy=2 as in validate/cp_rates.py, whose reason it gives
        common = [f"nevents={nev}", "ebeam1=6800", "ebeam2=6800",
                  "hel_recycling=False", "use_syst=False", "sde_strategy=2"]
        if run([PY, os.path.join(ROOT, "examples", "studies", "set_cards.py"), d] + common
               + ["dim8_all=0", f"Lam={lam}"] + [f"{w}=1" for w in S[name]], log):
            print(f"{name}: card error, see {log}", flush=True)
            failed += 1
            continue
        before = os.path.getsize(log)
        run([os.path.join(d, "bin", "generate_events"), "-f", "run_01"], log)
        txt = open(log, errors="replace").read()[before:]
        m = re.findall(r"Cross-section\s*:\s*([-\d.eE+]+)\s*\+-\s*([-\d.eE+]+)", txt)
        # a run that stopped writes no row, so that it is not read as a vanishing interference
        if not m or "interrupted with error" in txt:
            print(f"{name}: MadGraph gave no cross section, see {log}", flush=True)
            failed += 1
            continue
        x, e = float(m[-1][0]), float(m[-1][1])
        with open(out, "a") as fh:
            fh.write(f"{proc}\t{name}\t{len(S[name])}\t{x:.6g}\t{e:.6g}\n")
        print(f"{name:22s} n={len(S[name]):4d}  {x:12.5g} +- {e:.3g} pb"
              + ("   CP odd (consistent with zero)" if abs(x) < 3 * e else "   CP even (nonzero)"),
              flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
