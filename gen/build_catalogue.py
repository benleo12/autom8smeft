"""
gen/build_catalogue.py  --  read every operator row of Murphy's tables straight from the
LaTeX source, apply the documented patches, parse into the DSL, and write

    docs/murphy_parsed.json      one entry per row: label, class file, raw latex, patched
                                  latex, parse status, field content, number of DSL terms,
                                  WC name, flavour indices
    docs/murphy_parse_report.md  coverage per table file and the list of failures

Usage:  python3 gen/build_catalogue.py [--emit models/dev/generated.fr]
"""

from __future__ import annotations

import argparse
import collections
import glob
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(__file__))
from murphy_patches import apply_patches, patch_label  # noqa: E402
from parse_murphy import ParseError, parse_operator, wc_name  # noqa: E402

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "validate"))
from hermiticity import apply_convention, classify  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "murphy_src", "sections")

CLASS_OF_FILE = {
    "dim8_classes_1_2_3_4.tex": "1-4",
    "dim8_classes_5_6_7_8_v2.tex": "5-8",
    "dim8_classes_9.tex": "9",
    "dim8_classes_10_11_12_13_v2.tex": "10-13",
    "dim8_classes_14_v2.tex": "14",
    "dim8_classes_15.tex": "15",
    "dim8_classes_16_17.tex": "16-17",
    "dim8_classes_18_v6.tex": "18",
    "dim8_classes_19_v6.tex": "19",
    "dim8_classes_20.tex": "20",
    "dim8_classes_21_v3.tex": "21",
}


def extract_rows(path: str):
    """Yield (label, latex, plus_hc_flag, table_header) for every operator cell."""
    txt = open(path).read()
    # glue physical lines that belong to one table row (rows end with \\)
    lines = txt.split("\n")
    header = ""
    buf = ""
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("%"):
            continue
        m = re.search(r"\\multicolumn\{2\}\{c\}\{\\boldmath\$(.+?)\$\}", line)
        if m:
            header = m.group(1)
        if "Q_{" not in line and not buf:
            continue
        buf += " " + line
        if not line.endswith("\\\\") and "\\end{tabular}" not in line and not line.endswith("\\hdashline") and not line.endswith("\\hline"):
            # row continues on the next line unless it is the last row of a tabular
            if "&" in buf and buf.count("$") % 2 == 0 and (buf.rstrip().endswith("$") or buf.rstrip().endswith("\\hc$")):
                pass
            else:
                continue
        row = buf
        buf = ""
        row = row.replace("\\\\", " ").replace("\\hdashline", " ").replace("\\hline", " ")
        row = re.sub(r"\\end\{tabular\}.*$", "", row)
        cells = [c.strip() for c in row.split("&")]
        for k in range(0, len(cells) - 1, 2):
            lab, ex = cells[k], cells[k + 1]
            if "Q_{" not in lab:
                continue
            lab = lab.strip("$ ").strip()
            hc = "\\hc" in ex or "h.c." in ex or "\\hc" in lab or "\\hc" in header
            ex = re.sub(r"\+\s*\\hc", "", ex).strip()
            lab = re.sub(r"\s*\+\s*\\hc\s*$", "", lab).strip("$ ").strip()
            yield lab, ex, hc, header


def all_rows():
    """Every table row as (label, latex, plus_hc, header, file), baryon-number-conserving
    rows first in table order, then the B-violating ones in table order.  The block numbers
    of the drivers follow this order, so the B-violating classes (added later) sit at the
    end and never renumber a cached block."""
    rows = []
    for f in sorted(glob.glob(os.path.join(SRC, "dim8_classes_*.tex"))):
        fn = os.path.basename(f)
        for lab, ex, hc, header in extract_rows(f):
            rows.append((lab, ex, hc, header, fn))
    keep = [r for r in rows if "slashed B" not in r[3]]
    bviol = [r for r in rows if "slashed B" in r[3]]
    return keep + bviol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emit", help="write a FeynRules fragment with every parsed operator")
    ap.add_argument("--flavor", default="universal")
    ap.add_argument("--per-block", type=int, default=1, dest="per_block",
                    help="operators per Lagrangian block (1 = one per operator, the parallel/cacheable unit)")
    a = ap.parse_args()

    entries = []
    patch_log = []
    for lab, ex, hc, header, fn in all_rows():
            lab = patch_label(lab)
            patched = apply_patches(lab, ex, patch_log)
            mcls = re.match(r"\s*(\d+)", header)
            cls = int(mcls.group(1)) if mcls else 0
            bviol = "slashed B" in header
            e = dict(label=lab, file=fn, cls=cls, table=header, b_violating=bviol,
                     latex=ex, latex_patched=patched, plus_hc=hc, wc=None, status=None, error=None)
            try:
                e["wc"] = wc_name(lab)
                op = parse_operator(patched, lab, e["wc"], cls, plus_hc=hc, hermitian=(not hc))
                # V5, DSL half: the conjugacy is DERIVED, never taken from the typesetting
                v = classify(op)
                apply_convention(op, v)
                e["conjugacy"] = v.kind
                e["hc_mode"] = op.hc_mode
                e["gen_perm"] = v.gen_perm
                e["notes"] = op.notes
                e["status"] = "ok"
                e["n_terms"] = len(op.terms)
                e["fields"] = op.field_content()
                e["gens"] = list(op.gens)
                e["_op"] = op
            except (ParseError, ValueError, AssertionError, KeyError, IndexError) as err:
                e["status"] = "fail"
                e["error"] = f"{type(err).__name__}: {err}"
            entries.append(e)

    ok = [e for e in entries if e["status"] == "ok"]
    bad = [e for e in entries if e["status"] != "ok"]
    per_file = collections.OrderedDict()
    for e in entries:
        d = per_file.setdefault(e["file"], dict(total=0, ok=0))
        d["total"] += 1
        d["ok"] += e["status"] == "ok"

    rep = [f"# Murphy table parse report\n", f"{len(ok)} / {len(entries)} rows parsed into the DSL.\n",
           "| table file | rows | parsed |", "|---|---|---|"]
    rep += [f"| {k} | {v['total']} | {v['ok']} |" for k, v in per_file.items()]
    rep += ["\n## Patches applied to the source (candidate errata)\n"]
    for p in patch_log:
        rep.append(f"* `{p['label']}`: {p['reason']}\n  before: `{p['before']}`\n  after:  `{p['after']}`")
    # V5 (DSL half): derived conjugacy vs Murphy's "+ h.c." marks
    xt = collections.Counter((e["plus_hc"], e.get("conjugacy")) for e in ok)
    rep += ["\n## Derived conjugacy vs the published \"+ h.c.\" marks (V5, DSL half)\n",
            "| Murphy marks + h.c. | derived | rows | emitted as |", "|---|---|---|---|"]
    _how = {("real",): "", }
    for (mark, kind), n in sorted(xt.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]))):
        mode = {("hermitian"): "C Q, C real",
                ("antihermitian"): "C (i Q), C real, factor i restored",
                ("complex"): "C Q + h.c., C complex" if mark else "(C/2)(Q + h.c.), C real"}[kind]
        rep.append(f"| {mark} | {kind} | {n} | {mode} |")
    ah = [e for e in ok if e.get("conjugacy") == "antihermitian"]
    sym = [e for e in ok if e.get("hc_mode") == "sym"]
    rep += [f"\nThe {len(ah)} anti-Hermitian rows carry a bare `\\overleftrightarrow{{D}}`; Murphy's",
            "definition (conventions_v2.tex:87) puts the factor $i$ outside that symbol, so the",
            "rows are anti-Hermitian exactly as typeset and the $i$ is restored automatically.",
            f"\nThe {len(sym)} rows below are Hermitian only up to integration by parts, and are",
            "not marked `+ h.c.` in the source.  A Lagrangian density must be Hermitian, so they",
            "are emitted as the Hermitian part $(C/2)(Q + Q^\\dagger)$ with $C$ real, which",
            "coincides with $C Q$ whenever $Q$ is Hermitian:\n"]
    rep += [f"* `{e['label']}` (class {e['cls']})" for e in sym]

    rep += ["\n## Failures\n"]
    byerr = collections.defaultdict(list)
    for e in bad:
        byerr[e["error"].split(":")[0] + ": " + e["error"].split(":", 1)[1][:60]].append(e)
    for k, v in sorted(byerr.items(), key=lambda kv: -len(kv[1])):
        rep.append(f"\n### {k}  ({len(v)})\n")
        for e in v:
            rep.append(f"* `{e['label']}` ({e['file']}): `{e['latex']}`")
    open(os.path.join(ROOT, "docs", "murphy_parse_report.md"), "w").write("\n".join(rep) + "\n")

    slim = [{k: v for k, v in e.items() if not k.startswith("_")} for e in entries]
    json.dump(slim, open(os.path.join(ROOT, "docs", "murphy_parsed.json"), "w"), indent=1)
    print(f"{len(ok)} / {len(entries)} parsed; report in docs/murphy_parse_report.md")
    for k, v in per_file.items():
        print(f"  {k:36s} {v['ok']:4d} / {v['total']}")

    if a.emit:
        from emit_fr import emit_model_fragment

        ops = [e["_op"] for e in ok]
        # make WC names unique (the same label can appear in two tables only by mistake)
        seen = collections.Counter(o.wc for o in ops)
        dup = [w for w, c in seen.items() if c > 1]
        if dup:
            print("WARNING duplicate WC names:", dup)
        txt, index = emit_model_fragment(ops, per_block=a.per_block)
        os.makedirs(os.path.dirname(a.emit), exist_ok=True)
        open(a.emit, "w").write(txt)
        json.dump(index, open(os.path.join(ROOT, "docs", "block_index.json"), "w"), indent=1)
        print("wrote", a.emit, f"({len(ops)} operators, {len(index)} blocks); index in docs/block_index.json")


if __name__ == "__main__":
    main()
