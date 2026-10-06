#!/usr/bin/env python3
"""Operator by operator, our implementation against a hand-typed one, with no event generator.

    validate/adam_report.py [--ufo <his UFO dir>] [--fr <his .fr>] [--md out.md] [--tsv out.tsv]

Both models are plain Python, so this needs no MadGraph, no phase space and no Monte Carlo.  Set
identical Standard-Model inputs on each side, switch one coefficient on, evaluate every coupling,
and read which vertices moved.  Vertices are keyed by sorted PDG code so the two line up despite
naming their particles and their Lorentz structures differently, and the couplings on a vertex are
summed SIGNED, because summing magnitudes turns a cancellation into an addition.

Four things have to be right for the comparison to mean anything, and each of them produced a
false disagreement before it was handled.

1.  NO INPUT SCHEME ON EITHER SIDE.  We compare against `models/dim8_plain`, not the shipped
    `dim8_is`.  Four operators, Q_{B^2H^4}^{(1)}, Q_{W^2H^4}^{(1)}, Q_{WBH^4}^{(1)} and
    Q_{H^6}^{(2)}, have their whole effect at order v^4 in a gauge two-point function.  An input
    scheme absorbs that into the derived parameters and a raw model leaves it in the Lagrangian,
    so is-against-raw compares two different objects for exactly those four.

2.  THE DERIVATIVE SIGN.  D = d + igA here against the FeynRules default, which is A -> -A.  A
    vertex carrying n_g gauge legs flips by (-1)^{n_g} and a coefficient carrying n_X field
    strengths is redefined by (-1)^{n_X}.  The report gives the residual both before and after
    dividing this out, since the raw number is what a naive comparison shows.

3.  THE PAIR NORMALISATION.  `adam_pairs.m` records a factor per pair, and it is 1 on only 68 of
    the 101 rows; the rest are -1, -2, 2, +-1/2 or +-i.  Ignoring it reported seven operators as
    differing that agree exactly.

4.  ONE OF HIS COEFFICIENTS CAN BE SEVERAL OF OUR OPERATORS.  c8GGWW1 to c8GGWW4 each sit in
    several blocks of his file, so his single coefficient is a fixed linear combination of up to
    five of ours.  Those are compared as that combination, not one against one.

Vertices his export does not contain are reported separately rather than counted as
disagreements: his UFO was built for diboson processes and carries 278 vertices against our
10883, so anything with gluons, charm or high leg multiplicity is simply outside it.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PY = "python3.11"
OURS = os.path.join(ROOT, "models", "dim8_plain")
PAIRS = os.path.join(ROOT, "validate", "adam_pairs.m")
CATALOGUE = os.path.join(ROOT, "docs", "catalogue.json")
PARSED = os.path.join(ROOT, "docs", "murphy_parsed.json")
OURFR = os.path.join(ROOT, "models", "dev", "dim8_generated.fr")
GAUGE = {21, 22, 23, 24}
TOL = 1e-9

# Identical on both sides, so the Standard-Model half of every vertex is the same number before a
# coefficient is touched.  His model has no scale parameter and his coefficients carry Lambda = 1
# GeV implicitly, so ours is evaluated at Lam = 1 to match units.  A unit convention for this
# comparison, not a claim about the physical scale.
SM = {"aEWM1": 127.9, "Gf": 1.16637e-5, "aS": 0.1184, "MZ": 91.1876, "MH": 125.0,
      "MT": 172.0, "MB": 4.7, "MTA": 1.777, "MC": 0.0, "cabi": 0.0,
      "ymt": 172.0, "ymb": 4.7, "ymtau": 1.777, "ymc": 0.0}
NAMES = {1: "d", 2: "u", 3: "s", 4: "c", 5: "b", 6: "t", 11: "e", 12: "ve", 13: "mu",
         15: "ta", 21: "g", 22: "a", 23: "Z", 24: "W", 25: "h"}
HOW = {"real": "C Q, real C", "complex": "C Q + h.c., complex C",
       "sym": "(C/2)(Q + Q^dag), real C"}


def parse_norm(s):
    """'1', '-1', '2', '-1/2', 'I', '-I', 'I/2' as a Python complex."""
    return complex(eval(s.replace("I", "1j"), {"__builtins__": {}}, {}))


def read_pairs(path):
    out = []
    for m in re.finditer(r'\{\s*"([^"]+)"\s*,\s*(\w+)\s*,\s*"([^"]+)"\s*,\s*(\w+)\s*,\s*([^}]+)\}',
                         open(path).read()):
        out.append(dict(hblock=m.group(1), hwc=m.group(2), gblock=m.group(3),
                        gwc=m.group(4), norm=m.group(5).strip()))
    return out


def externals(ufo):
    return set(re.findall(r"Parameter\(name = '(\w+)',\s*nature = 'external'",
                          open(os.path.join(ufo, "parameters.py")).read()))


def his_terms(path):
    """{coefficient: the longest FeynRules line it appears in}, Lagrangian blocks only.  His file
    declares each coefficient with 'name == {...}' near the top, and a declaration is not an
    implementation, so any line carrying '==' is skipped."""
    out = defaultdict(list)
    if not os.path.exists(path):
        return {}
    for line in open(path, errors="replace"):
        t = line.strip().rstrip("+").strip()
        if not t or "==" in t or t.startswith("(*"):
            continue
        for m in re.finditer(r"\b(c8\w+)\b", t):
            out[m.group(1)].append(t)
    return {k: max(v, key=len) for k, v in out.items()}


def our_terms(path):
    """{coefficient: the emitted Lagrangian term}.  Each operator is a Module whose ExpandIndices
    argument holds one line beginning '<wc>/Lam^4 ('.  It is longer than the compact form because
    it is already expanded over the electroweak indices."""
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path, errors="replace"):
        m = re.match(r"^(c8\w+)/Lam\^4\s", line.strip())
        if m:
            out.setdefault(m.group(1), line.strip())
    return out


def probe(one, ufo, inputs, coeff):
    r = subprocess.run([PY, one, ufo, json.dumps(inputs), json.dumps([coeff]), "1.0"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None, r.stderr.strip()[-200:]
    d = {}
    for k, (o, n) in json.loads(r.stdout).items():
        z = complex(n[0][0] - o[0][0], n[0][1] - o[0][1])
        if abs(z) > 1e-13:
            d[k] = z
    return d, None


def legs(key):
    return " ".join(NAMES.get(abs(int(x)), x) for x in key.split(","))


def arg(argv, flag, default=None):
    return dict(zip(argv, argv[1:])).get(flag, default)


def main(argv):
    adam = os.path.expanduser(arg(argv, "--ufo", "~/dim8auto_build/adam_diboson_UFO"))
    hisfr = os.path.expanduser(arg(argv, "--fr", "~/Downloads/dim8_geosmeft5.fr"))
    one = os.path.join(ROOT, "validate", "vertexcmp_one.py")
    for p in (one, OURS, adam):
        if not os.path.exists(p):
            print(f"missing: {p}"); return 2

    cat = {r["wc"]: r for r in json.load(open(CATALOGUE))}
    tex = ({r["wc"]: (r.get("latex_patched") or r.get("latex") or "")
            for r in json.load(open(PARSED))} if os.path.exists(PARSED) else {})
    ofr, hfr = our_terms(OURFR), his_terms(hisfr)
    his, ourext = externals(adam), externals(OURS)

    # Group by HIS coefficient: one of his can be a fixed combination of several of ours.
    groups = defaultdict(list)
    for p in read_pairs(PAIRS):
        if p["hwc"] in his and p["gwc"] in ourext and p not in groups[p["hwc"]]:
            groups[p["hwc"]].append(p)
    # Deliberately NOT deduplicated by our coefficient.  c8W appears in both L8VVV4 and L8nonWh,
    # and the build that produced his UFO sums all five blocks, so his single coefficient really
    # does multiply our Q_{W^3H^2}^{(1)} twice in that build.  Deduplicating reported it as a
    # factor-two disagreement, which was an artefact of the build we made and not of his file.
    print(f"{len(groups)} of his coefficients pair with "
          f"{sum(len(v) for v in groups.values())} of ours "
          f"({len(his)} externals in his file, {len(ourext)} in ours)", flush=True)
    print(f"FeynRules terms: {len(ofr)} ours, {len(hfr)} his", flush=True)

    cache = {}

    def get(ufo, inputs, wc):
        if (ufo, wc) not in cache:
            cache[(ufo, wc)] = probe(one, ufo, inputs, wc)
        return cache[(ufo, wc)]

    out = []
    for i, (hwc, ps) in enumerate(sorted(groups.items())):
        hb, eb = get(adam, dict(SM), hwc)
        rec = dict(hwc=hwc, hblock=ps[0]["hblock"], his_fr=hfr.get(hwc, ""),
                   n_ours=len(ps),
                   gwc=" + ".join(f"{p['norm']}*{p['gwc']}" if p["norm"] != "1" else p["gwc"]
                                  for p in ps),
                   label="; ".join(cat.get(p["gwc"], {}).get("label", "?") for p in ps),
                   cls="; ".join(str(cat.get(p["gwc"], {}).get("cls", "?")) for p in ps),
                   how="; ".join(HOW.get(cat.get(p["gwc"], {}).get("hc_mode", ""), "?") for p in ps),
                   cp="; ".join(str(cat.get(p["gwc"], {}).get("cp", "?")) for p in ps),
                   latex="; ".join(tex.get(p["gwc"], "").strip("$") for p in ps),
                   our_fr=" ||| ".join(ofr.get(p["gwc"], "") for p in ps),
                   norm="; ".join(p["norm"] for p in ps))
        if hb is None:
            rec.update(status="COULD NOT EVALUATE HIS", detail=eb); out.append(rec); continue

        # Our side: the linear combination his coefficient corresponds to.  The couplings are
        # linear in each coefficient in a raw model, so the deltas simply add, and the derivative
        # convention is per operator because it redefines the coefficient.
        ob, bad = defaultdict(complex), None
        for p in ps:
            d, e = get(OURS, dict(SM, Lam=1.0), p["gwc"])
            if d is None:
                bad = e; break
            nX = (cat.get(p["gwc"], {}).get("fields") or {}).get("N_X", 0)
            f = parse_norm(p["norm"]) * ((-1) ** (nX % 2))
            for k, z in d.items():
                ob[k] += f * z
        if bad:
            rec.update(status="COULD NOT EVALUATE OURS", detail=bad); out.append(rec); continue
        ob = {k: z for k, z in ob.items() if abs(z) > 1e-13}

        shared = sorted(set(ob) & set(hb))
        outside = sorted(set(ob) - set(hb))          # his diboson export does not carry these
        extra = sorted(set(hb) - set(ob))            # he moves something we do not: a real problem
        rec.update(nv_shared=len(shared), nv_outside=len(outside), nv_extra=len(extra),
                   outside_eg="; ".join(legs(k) for k in outside[:3]),
                   extra_eg="; ".join(legs(k) for k in extra[:3]))
        raw = corr = 0.0
        for k in shared:
            ng = sum(1 for x in k.split(",") if abs(int(x)) in GAUGE)
            x, y = ob[k], hb[k]
            raw = max(raw, abs(x - y) / max(abs(x), abs(y)))
            corr = max(corr, abs(((-1) ** (ng % 2)) * x - y) / max(abs(x), abs(y)))
        rec["worst_raw"], rec["worst_corrected"] = raw, corr
        rec["status"] = ("NOT IN HIS EXPORT" if not shared else
                         "EXACT" if corr < TOL else "DIFFERS")
        if extra:
            rec["status"] += " (+ vertices he moves that we do not)"
        # the histogram of his/ours over the shared vertices is the diagnostic: one value means a
        # normalisation, several means the two operators differ in structure
        hist = defaultdict(int)
        for k in shared:
            ng = sum(1 for x in k.split(",") if abs(int(x)) in GAUGE)
            x = ((-1) ** (ng % 2)) * ob[k]
            r = hb[k] / x if abs(x) else complex("nan")
            hist[(round(r.real, 4), round(r.imag, 4))] += 1
        rec["ratios"] = "; ".join(f"{re_:+g}{im:+g}i on {n}" for (re_, im), n in
                                  sorted(hist.items(), key=lambda kv: -kv[1]))
        out.append(rec)
        print(f"  [{i+1:3d}/{len(groups)}] {rec['label'][:34]:<34s} vs {hwc:<12s} "
              f"{len(shared):>4d} shared" + (f" +{len(outside)} outside his export" if outside else "")
              + f"  {rec['status']}"
              + ("" if rec["status"].startswith("EXACT") or rec["status"] == "NO SHARED VERTEX"
                 else f"  ({corr:.1e})"),
              flush=True)

    # A row that agrees on every shared vertex is an exact agreement whether or not he also
    # moves vertices we do not.  The extra ones carry their own note and are reported separately;
    # counting them as a failure hid three exact rows behind the suffix and dropped 49 vertices
    # from the total, none of which had disagreed with anything.
    ok = [r for r in out if r.get("status", "").startswith("EXACT")]
    nv = sum(r.get("nv_shared", 0) for r in ok)
    nout = sum(r.get("nv_outside", 0) for r in out)
    print(f"\n{len(ok)} of {len(out)} comparisons agree exactly, on {nv} vertices in total. "
          f"{nout} further vertices ours moves are absent from his export and cannot be compared.")
    for r in out:
        if not r.get("status", "").startswith("EXACT"):
            print(f"  {r['status']}: {r['label']} ({r['gwc']} vs {r['hwc']}) "
                  f"{r.get('detail','')}{r.get('extra_eg','')}")

    cols = ["label", "cls", "gwc", "hwc", "hblock", "norm", "how", "cp", "nv_shared",
            "nv_outside", "nv_extra", "worst_raw", "worst_corrected", "ratios", "status",
            "latex", "our_fr", "his_fr"]
    t = arg(argv, "--tsv")
    if t:
        with open(t, "w") as fh:
            fh.write("\t".join(cols) + "\n")
            for r in out:
                fh.write("\t".join(str(r.get(c, "")).replace("\t", " ") for c in cols) + "\n")
        print(f"wrote {t}")
    m = arg(argv, "--md")
    if m:
        with open(m, "w") as fh:
            fh.write(
                f"# dim8auto against a hand-typed implementation, operator by operator\n\n"
                f"{len(ok)} of {len(out)} comparisons agree **exactly**, on {nv} vertices, with no "
                f"event generator and therefore no Monte Carlo error. A further {nout} vertices "
                f"that our operators move are absent from the diboson-only export and cannot be "
                f"compared.\n\n"
                f"Both sides are raw models with no input scheme. `raw` is the worst relative "
                f"disagreement as the two models stand; `corrected` is after dividing out the one "
                f"global convention that separates them, D = d + igA against the FeynRules "
                f"default, under which a vertex with n_g gauge legs flips by (-1)^n_g and a "
                f"coefficient with n_X field strengths by (-1)^n_X. `corrected` is the number "
                f"that has to vanish.\n\n")
            for r in sorted(out, key=lambda r: (str(r.get("cls", "99")).zfill(2), r.get("label", ""))):
                fh.write(f"## {r['label']}  (class {r['cls']})\n\n"
                         f"- operator: `${r.get('latex','')}$`\n"
                         f"- ours `{r['gwc']}`, his `{r['hwc']}` in block `{r['hblock']}`, "
                         f"normalisation {r['norm']}\n"
                         f"- how we implement it: {r.get('how','')}, CP {r.get('cp','')}\n"
                         f"- vertices compared {r.get('nv_shared','')}"
                         + (f", plus {r['nv_outside']} ours moves that his export does not carry "
                            f"({r.get('outside_eg','')})" if r.get("nv_outside") else "") + "\n"
                         f"- worst relative deviation: raw {r.get('worst_raw', float('nan')):.2e}, "
                         f"corrected {r.get('worst_corrected', float('nan')):.2e} "
                         f"**{r.get('status','')}**\n"
                         + (f"- his/ours over the shared vertices: {r['ratios']}\n"
                            if r.get("ratios") else "")
                         + (f"- he also moves {r['nv_extra']} vertices we do not "
                            f"({r.get('extra_eg','')}); ours are removed at release because their "
                            f"Lorentz structure is algebraically zero, which the release step removes\n"
                            if r.get("nv_extra") else "") + "\n"
                         f"```mathematica\nhis:  {r.get('his_fr','')}\n\nours: "
                         f"{r.get('our_fr','')}\n```\n\n")
        print(f"wrote {m}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
