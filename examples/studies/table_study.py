#!/usr/bin/env python3
"""Tables for the paper from a study's results.tsv.

    examples/studies/table_study.py <study dir> [model dir]

Writes <study dir>/table.md and <study dir>/table.tex: one block per process with the
Standard-Model cross section, the full-model interference and squared rows, and one line per
operator class with its interference (1/Lambda^4) and squared (1/Lambda^8) cross sections in pb,
the ratio of interference to the SM, and where a class gives no diagram at an order.  The W mass
of each row is recomputed from the model at the row's settings with validate/eval_ufo_params.py
(the early diboson rows carried a wrong value from a first version of the driver), so a row whose
vacuum differs from the Standard Model's is visible in the table.  Pure Python.
"""
import os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
def tex_proc(proc):
    """'p p > w+ w- z' -> '$pp \\to W^+ W^- Z$' for the LaTeX table (a bare '>' typesets wrongly)."""
    m = {"p": "p", "w+": "W^+", "w-": "W^-", "z": "Z", "h": "H", "a": "\\gamma", "j": "j", "g": "g",
         "t": "t", "t~": "\\bar t", "b": "b", "b~": "\\bar b",
         # leptons: a bare "e+" typesets as an italic e followed by a plus sign at text size
         "e+": "e^+", "e-": "e^-", "mu+": "\\mu^+", "mu-": "\\mu^-",
         "ta+": "\\tau^+", "ta-": "\\tau^-", "ve": "\\nu_e", "ve~": "\\bar\\nu_e",
         "u": "u", "u~": "\\bar u", "d": "d", "d~": "\\bar d", "c": "c", "c~": "\\bar c"}
    ini, fin = proc.strip().split(">", 1)
    fin = re.sub(r"\b(QCD|QED|NP)\S*", "", fin)
    return "$" + " ".join(m.get(x, x) for x in ini.split()) + " \\to " + " ".join(m.get(x, x) for x in fin.split()) + "$"


def tex_num(v):
    """A table number for LaTeX: math-mode minus, powers of ten instead of e-notation."""
    try: x = float(v)
    except (TypeError, ValueError): return str(v)
    if x == 0: return "$0$"
    if abs(x) >= 1e-3: return f"${x:.4g}$"
    m, e = f"{x:.2e}".split("e"); return f"${m}\\times 10^{{{int(e)}}}$"


def slug(proc):
    """'p p > w+ z' -> 'wpz', 'p p > w- z' -> 'wmz', 'p p > h h j j QCD=0' -> 'hhjj': the label
    must tell w+ from w-, or two tables of one study share a label."""
    ini, fin = proc.strip().split(">", 1)
    return "".join(x[0] + ("p" if x.endswith("+") else "m" if x.endswith("-") else "") for x in re.sub(r"\b(QCD|QED|NP)\S*", "", fin).split())


def tex_class(label):
    """'class 14 (psi^2 X^2 D)' -> 'class 14 ($\\psi^2 X^2 D$)': carets need math mode."""
    return re.sub(r"\(([^)]*)\)", lambda mm: "($" + mm.group(1).replace("psi", "\\psi") + "$)", label)


CLASS = {1: "X^4", 2: "H^8", 3: "H^6 D^2", 4: "H^4 D^4", 5: "X^3 H^2", 6: "X^2 H^4", 7: "X^2 H^2 D^2",
         8: "X H^4 D^2", 9: "psi^2 X^2 H", 10: "psi^2 X H^3", 11: "psi^2 H^2 D^3", 12: "psi^2 H^5",
         13: "psi^2 H^4 D", 14: "psi^2 X^2 D", 15: "psi^2 X H^2 D", 16: "psi^2 X H D^2", 17: "psi^2 H^3 D^2",
         18: "psi^4 H^2", 19: "psi^4 X", 20: "psi^4 H D", 21: "psi^4 D^2"}
_mw_cache = {}


def class_wcs(n):
    import json
    return [w for e in json.load(open(os.path.join(ROOT, "docs", "block_index.json"))) if e["cls"] == n for w in e["wcs"]]


def mw_of(model, settings, cls=None):
    """M_W from the model at these settings; for a class row only that class's coefficients are on,
    since the restricted model has no others, whatever dim8_all= says."""
    if cls is not None and "dim8_all=" in settings:
        v = re.search(r"dim8_all=(\S+)", settings).group(1)
        settings = " ".join(f"{w}={v}" for w in class_wcs(cls)) + " " + re.sub(r"dim8_all=\S+", "", settings)
    key = (model, settings)
    if key not in _mw_cache:
        py = "python3.11" if subprocess.run(["which", "python3.11"], capture_output=True).returncode == 0 else "python3"
        out = subprocess.run([py, os.path.join(ROOT, "validate", "eval_ufo_params.py"), model] + settings.split() + ["--show=MW"],
                             capture_output=True, text=True).stdout
        m = re.search(r"^MW\s*=\s*([-\d.eE+]+)", out, re.M)
        _mw_cache[key] = float(m.group(1)) if m else float("nan")
    return _mw_cache[key]


def fmt(x):
    try: x = float(x)
    except (TypeError, ValueError): return str(x)
    if x == 0: return "0"
    return f"{x:.4g}" if abs(x) >= 1e-3 else f"{x:.3e}"


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    st = os.path.abspath(argv[1]); model = os.path.abspath(argv[2]) if len(argv) > 2 else os.path.join(ROOT, "models", "dim8_is")
    rows = [l.rstrip("\n").split("\t") for l in open(os.path.join(st, "results.tsv"))]
    head, rows = rows[0], rows[1:]
    col = {h: i for i, h in enumerate(head)}
    procs = []
    for r in rows:
        if r[col["process"]] not in procs: procs.append(r[col["process"]])
    md, tex = [], []
    for proc in procs:
        R = [r for r in rows if r[col["process"]] == proc]
        if not any("-cls" in r[col["model"]] for r in R) and any("-op_" in r[col["model"]] for r in R):
            continue   # a per-operator scan: its full-model rows duplicate the class study's, the operator table below is the point
        def get(model_tag, order):
            for r in R:
                if r[col["model"]] == model_tag and r[col["order"]] == order: return r
            return None
        base = os.path.basename(model)
        full_tags = sorted({r[col["model"]] for r in R if "-cls" not in r[col["model"]] and "-op_" not in r[col["model"]]})   # single-operator rows have their own table
        sm = next((r for r in R if r[col["order"]] == "NP=0"), None)
        sm_x = float(sm[col["sigma_pb"]]) if sm and re.match(r"^-?[\d.]", sm[col["sigma_pb"]]) else float("nan")
        md.append(f"\n### {proc.strip()}\n")
        md.append(f"Standard Model: {fmt(sm_x)} pb" + (f" (+- {fmt(sm[col['error_pb']])})" if sm else "") + f", M_W = {mw_of(model, 'dim8_all=0 Lam=1000'):.2f} GeV\n")
        md.append("| operators | interference [pb] | deviation from SM [%] | squared [pb] | M_W [GeV] |")
        md.append("|---|---|---|---|---|")
        # footnotesize with tight columns: the deviation column carries powers of ten and the
        # widest process labels push a \small lrrrr table past the margin
        tex.append(f"\\begin{{table}}[t]\\centering\\footnotesize\\setlength{{\\tabcolsep}}{{4pt}}\n"
                   f"\\begin{{tabular}}{{@{{}}lrrrr@{{}}}}\\hline")
        tex.append(f"\\multicolumn{{5}}{{l}}{{{tex_proc(proc)}, $\\sigma_{{\\rm SM}} = {fmt(sm_x)}$ pb, $\\Lambda = 1$ TeV, $C_i = 1$}}\\\\")
        tex.append("operators & $\\sigma_{1/\\Lambda^4}$ [pb] & deviation [\\%] & $\\sigma_{1/\\Lambda^8}$ [pb] & $M_W$ [GeV]\\\\\\hline")
        def line(label, tag):
            i, s = get(tag, "NP^2==2"), get(tag, "NP<=2 NP^2==4")
            def val(r, tex=False):
                if r is None: return "not run"   # no row at all, which is not the same as zero
                v = r[col["sigma_pb"]]
                if v == "NO_OUTPUT":   # rows from the first driver: tell no-diagram from a real failure by the log
                    tag = re.sub(r"[^A-Za-z0-9_]", "_", f"{r[col['process']]}_{r[col['model']]}_{r[col['order']]}")
                    log = os.path.join(os.environ.get("DIM8_RUNS", os.path.expanduser("~/dim8auto_build/mg5runs")), tag + ".log")
                    if os.path.exists(log) and "NoDiagramException" in open(log).read(): v = "NO_DIAGRAMS"
                return {"NO_DIAGRAMS": "no diagram", "NO_OUTPUT": "no output", "FAILED": "failed", "BAD_SETTING": "bad setting"}.get(v, tex_num(v) if tex else fmt(v))
            ratio = ""
            if i and re.match(r"^-?[\d.]", i[col["sigma_pb"]]) and sm_x == sm_x and sm_x:
                dev = 100 * float(i[col["sigma_pb"]]) / sm_x   # the VBF paper's "SM deviation (%)" column
                # "-5.7e-03" typesets as "-5.7e - 03" in math mode; use a power of ten
                if abs(dev) >= 0.01:
                    ratio = f"{dev:+.2f}"
                else:
                    m, e = f"{dev:+.1e}".split("e")
                    ratio = f"{m}\\times 10^{{{int(e)}}}"
            settings = (i or s or {}) and (i or s)[col["settings"]] if (i or s) else "dim8_all=1 Lam=1000"
            cls = int(tag.rsplit("-cls", 1)[1]) if "-cls" in tag else None
            mw = mw_of(model, settings, cls) if (i or s) else float("nan")
            md.append(f"| {label} | {val(i)} | {ratio} | {val(s)} | {mw:.2f} |")
            tex.append(f"{tex_class(label)} & {val(i, True)} & {('$' + ratio + '$') if ratio else ''} & {val(s, True)} & ${mw:.2f}$\\\\")
        for t in full_tags:
            if t == base: line("all 674 operators at once", t)
            else: line(f"all, card {t.split('-', 1)[1].replace('_', chr(92) + '_')}", t)
        for n in range(1, 22):
            tag = f"{base}-cls{n}"
            if any(r[col["model"]] == tag for r in R): line(f"class {n} ({CLASS[n]})", tag)
        # linearity: at 1/Lambda^4 the interference is linear in the coefficients, so the class
        # rows must add up to the all-on row; a mismatch beyond the Monte Carlo errors would mean
        # a restriction card dropping something it should keep, or a coefficient the all-on run
        # sets that no class run does
        parts = [get(f"{base}-cls{n}", "NP^2==2") for n in range(1, 22)]
        vals = [(float(r[col["sigma_pb"]]), float(r[col["error_pb"]])) for r in parts if r and re.match(r"^-?[\d.]", r[col["sigma_pb"]])]
        allon = get(base, "NP^2==2")
        if vals and allon and re.match(r"^-?[\d.]", allon[col["sigma_pb"]]) and len([r for r in parts if r]) == 21:
            tot = sum(v for v, _ in vals); err = sum(e * e for _, e in vals) ** 0.5
            a, ae = float(allon[col["sigma_pb"]]), float(allon[col["error_pb"]])
            note = f"linearity check: sum of the class interferences {tot:.4g} +- {err:.2g} pb against the all-on row {a:.4g} +- {ae:.2g} pb ({(tot - a) / ((err * err + ae * ae) ** 0.5):+.1f} sigma)"
            md.append(f"\n{note}\n")
            # a p{} multicolumn, not an l: the note is one long unbreakable line otherwise and
            # it is what pushes these tables past the margin
            tex.append("\\multicolumn{5}{@{}p{0.97\\linewidth}@{}}{\\footnotesize "
                       + note.replace("+-", "$\\pm$").replace(" sigma", "$\\sigma$") + "}\\\\")
        tex.append("\\hline\\end{tabular}\n\\caption{" + tex_proc(proc) + " at 13.6 TeV: interference of one dimension-eight insertion with the Standard Model, its size relative to the Standard Model, the dimension-eight square, and the $W$ mass the input scheme derives with that class on.}\\label{tab:" + os.path.basename(st) + "-" + slug(proc) + "}\\end{table}\n")
    # per-operator rows (model tag "<model>-op_<coefficient>", from a scan over single-operator
    # cards): a second table, the operators ranked by the size of their interference, with the
    # class and the ratio to the Standard Model, in the style of the VBF paper's tables
    import json
    idx = json.load(open(os.path.join(ROOT, "docs", "block_index.json")))
    by_wc = {w: e for e in idx for w in e["wcs"]}
    for proc in procs:
        R = [r for r in rows if r[col["process"]] == proc and "-op_" in r[col["model"]]]
        if not R: continue
        sm = next((r for r in rows if r[col["process"]] == proc and r[col["order"]] == "NP=0"), None)
        sm_x = float(sm[col["sigma_pb"]]) if sm and re.match(r"^-?[\d.]", sm[col["sigma_pb"]]) else float("nan")
        ops = {}
        for r in R:
            wc = r[col["model"]].split("-op_", 1)[1]
            v = r[col["sigma_pb"]]; ok = bool(re.match(r"^-?[\d.]", v))
            ops.setdefault(wc, {})[r[col["order"]]] = (float(v) if ok else v, float(r[col["error_pb"]]) if ok else None)
        ranked = sorted(ops.items(), key=lambda kv: -abs(kv[1].get("NP^2==2", (0,))[0]) if isinstance(kv[1].get("NP^2==2", (0,))[0], float) else 0)
        md.append(f"\n### {proc.strip()}: one operator at a time ({len(ranked)} operators that can enter, ranked by |interference|)\n")
        md.append("| operator | class | coefficient | interference [pb] | deviation from SM [%] | squared [pb] |"); md.append("|---|---|---|---|---|---|")
        tex.append("\\begin{table}[t]\\centering\\small\n\\begin{tabular}{lcrrr}\\hline")
        tex.append(f"\\multicolumn{{5}}{{l}}{{{tex_proc(proc)}, one operator at a time; $\\sigma_{{\\rm SM}} = {fmt(sm_x)}$ pb, $\\Lambda = 1$ TeV, $C_i = 1$}}\\\\")
        tex.append("operator & class & $\\sigma_{1/\\Lambda^4}$ [pb] & deviation [\\%] & $\\sigma_{1/\\Lambda^8}$ [pb]\\\\\\hline")
        TOP = 20   # the LaTeX table keeps the twenty largest; the markdown table has them all
        for n_, (wc, d) in enumerate(ranked):
            e = by_wc.get(wc, {"ops": [wc], "cls": "?"}); i = d.get("NP^2==2", ("(pending)", None)); q = d.get("NP<=2 NP^2==4", ("(pending)", None))
            dev = f"{100 * i[0] / sm_x:+.3f}" if isinstance(i[0], float) and sm_x == sm_x and sm_x else ""
            md.append(f"| `{e['ops'][0]}` | {e['cls']} | `{wc}` | {fmt(i[0]) if isinstance(i[0], float) else i[0]} | {dev} | {fmt(q[0]) if isinstance(q[0], float) else q[0]} |")
            if n_ >= TOP: continue
            name = "$" + e["ops"][0] + "$"
            tex.append(f"{name} & {e['cls']} & {tex_num(i[0]) if isinstance(i[0], float) else i[0]} & {('$' + dev + '$') if dev else ''} & {tex_num(q[0]) if isinstance(q[0], float) else q[0]}\\\\")
        if len(ranked) > TOP:
            rest = [d.get("NP^2==2", (0.0,))[0] for _, d in ranked[TOP:] if isinstance(d.get("NP^2==2", (0.0,))[0], float)]
            tex.append(f"\\multicolumn{{5}}{{l}}{{\\footnotesize {len(ranked) - TOP} more operators below {fmt(max(abs(x) for x in rest) if rest else 0)} pb each (full list in the repository)}}\\\\")
        tex.append("\\hline\\end{tabular}\n\\caption{" + tex_proc(proc) + " at 13.6 TeV, one operator at a time: the operators that can enter the process, ranked by the size of their interference with the Standard Model.}\\label{tab:" + os.path.basename(st) + "-" + slug(proc) + "-operators}\\end{table}\n")
    open(os.path.join(st, "table.md"), "w").write("# " + os.path.basename(st) + " study\n" + "\n".join(md) + "\n")
    open(os.path.join(st, "table.tex"), "w").write("\n".join(tex))
    # These stay in the study directory.  They used to be copied into paper/tables as well, one
    # per process, and the paper printed all twelve; it now prints the class-by-process grid
    # instead, which says the same thing once rather than repeating the class column twelve times
    # and the derived W mass in every row of each.  Pass an output directory to place them
    # elsewhere.
    if len(sys.argv) > 3:
        pt = os.path.abspath(sys.argv[3]); os.makedirs(pt, exist_ok=True)
        open(os.path.join(pt, os.path.basename(st) + ".tex"), "w").write(
            "% generated by examples/studies/table_study.py from "
            + os.path.relpath(os.path.join(st, "results.tsv"), ROOT) + "\n" + "\n".join(tex))
        print("also wrote", os.path.join(pt, os.path.basename(st) + ".tex"))
    print("wrote", os.path.join(st, "table.md"), "and table.tex"); print("\n".join(md))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
