#!/usr/bin/env python3
"""The terminal view of ./dim8 select and ./dim8 series: their text, coloured by one rule and wrapped.

One rule colours every term: how fast it grows relative to the Standard Model at high energy, red for E^4,
orange for E^2, plain for E^0, and grey for a term that falls with the energy or enters only through the
Yukawa coupling or the mass of a light fermion.  A line at the top names the fastest-growing terms of
dimensions eight and six.  Powers are written as superscripts (lambda^4 as λ⁴, psi^2X^2D as ψ²X²D), the
notes of ./dim8 select are shortened to tags with a legend, and long lines wrap to the terminal.

./dim8 uses the view only when its output is a terminal, NO_COLOR is unset and TERM is not dumb, or when
FORCE_COLOR is set (FORCE_COLOR=1 ./dim8 select "p p > w+ w-" | less -R).  Anything that reads the output
through a pipe or a file gets the plain text, byte for byte, and so do --json and --latex.

    python3 gen/pretty.py <file of plain output> [width]     the view of a saved output
"""
from __future__ import annotations

import io
import os
import re
import sys
import textwrap
from contextlib import redirect_stdout

# one colour a growth, readable on a dark and on a light background
GROW = {4: "1;38;5;160", 2: "38;5;166", 0: "", -1: "38;5;245"}
BOLD, GREY, GREEN = "1", "38;5;245", "1;38;5;28"
SUP = str.maketrans("0123456789-", "⁰¹²³⁴⁵⁶⁷⁸⁹⁻")
GROUP = {"s": "s channel", "t": "t channel", "u": "u channel", "c": "contact"}

# the notes of ./dim8 select, each shortened to the tag the legend explains
TAGS = [("only through a power of g_s, which QCD=0 removes, together with the Yukawa coupling or the mass of a "
         "light quark or a lepton", "g_s and y_f only"),
        ("only through the Yukawa coupling or the mass of a light quark or a lepton", "y_f only"),
        ("only through a power of g_s, which QCD=0 removes", "g_s only"),
        ("only with a second dimension-six insertion, of this coefficient or another", "second insertion"),
        ("only with a second operator insertion", "second insertion"),
        ("has no tree once the flavours of the external particles are kept", "no tree"),
        ("enters G_F only with nonzero electron and muon Yukawas", "G_F needs y_e, y_mu"),
        ("the input relations, and this vertex ", "input relations, "),
        ("and the input relations", "+ input relations")]


def wanted(stream=sys.stdout):
    if os.environ.get("NO_COLOR"):
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    return stream.isatty() and os.environ.get("TERM", "") != "dumb"


def width():
    """The columns of the terminal, from the first of stdout, stderr and stdin that is one (the output may be a
    pipe into less while stderr is the terminal), else COLUMNS, else 120.  A terminal may report 0 columns
    (script, an editor's terminal), which counts as not knowing."""
    for fd in (1, 2, 0):
        try:
            n = os.get_terminal_size(fd).columns
        except OSError:
            continue
        if n > 0:
            return n
    n = os.environ.get("COLUMNS", "")
    return int(n) if n.isdigit() and int(n) > 0 else 120


def paint(s, code):
    return f"\033[{code}m{s}\033[0m" if code and s else s


def grow(e):
    return GROW[4] if e >= 4 else GROW[2] if e >= 2 else GROW[0] if e >= 0 else GROW[-1]


def math(s):
    """lambda^4 -> λ⁴, Lambda^4 -> Λ⁴, psi^2X^2D -> ψ²X²D, Q_{q^2W^2D}^{(1)} -> Q_q²W²D(1), Q_{H\\widetilde W B}
    -> Q_HW̃B, Q_{H\\Box} -> Q_H□, y_mu -> y_μ."""
    s = re.sub(r"\bLambda\^(-?\d+)", lambda m: "Λ" + m.group(1).translate(SUP), s)
    s = re.sub(r"\blambda\^(-?\d+)", lambda m: "λ" + m.group(1).translate(SUP), s)
    s = re.sub(r"\\widetilde ?([A-Za-z]) ?", "\\1\u0303", s).replace("\\Box", "□")
    s = re.sub(r"\bQ_\{([^{}]*)\}\^\{\(([^)]*)\)\}", r"Q_\1(\2)", s)
    s = re.sub(r"\bQ_\{([^{}]*)\}", r"Q_\1", s)
    s = re.sub(r"\bpsi(?=\^|\b)", "ψ", s)
    s = re.sub(r"(?<=[A-Za-zψλΛ)])\^(-?\d+)", lambda m: m.group(1).translate(SUP), s)
    return re.sub(r"\by_mu\b", "y_μ", s)


def sup(e):
    return str(e).translate(SUP)


def legend():
    keys = [(GROW[4], "E⁴"), (GROW[2], "E²"), (BOLD, "E⁰"), (GROW[-1], "falls with E, or y_f only")]
    return "  " + paint("growth relative to the SM:", GREY) + "  " + "   ".join(paint("■ " + t, c) for c, t in keys)


def footnote(line, cols):
    """A line of the plain output that is neither a term nor a header: its label bold, the rest grey, wrapped."""
    text = math(line.strip())
    head, sep, _ = text.partition(": ")
    rows = textwrap.wrap("  " + text, width=cols, subsequent_indent="    ", break_on_hyphens=False) or [""]
    n = len("  " + head + sep) if sep and len("  " + head + sep) <= len(rows[0]) else 0
    return [paint(rows[0][:n], BOLD) + paint(rows[0][n:], GREY)] + [paint(r, GREY) for r in rows[1:]]


# ------------------------------------------------------------------------------------------- series --

TERM = re.compile(r"^    lambda\^(-?\d+)\s+dim (\d+)\s+(\S+?)(\*)?(?: \(([^)]*)\))?\s+(.*?)\s+"
                  r"E\^(-?\d+) v\^(\d+)/Lambda\^(\d+)\s+(.*)$")
SMTERM = re.compile(r"^    lambda\^(-?\d+)\s+SM\s+(.*)$")


def _growth(e, v, k):
    """E^4 v^0/Lambda^4 -> E⁴/Λ⁴, E^0 v^2/Lambda^2 -> v²/Λ²."""
    num = (f"E{sup(e)}" if e != "0" else "") + (f"v{sup(v)}" if v != "0" else "")
    return f"{num or '1'}/Λ{sup(k)}"


def _fastest(lines):
    """The fastest-growing terms of dimensions eight and six of one result, as the line under its header."""
    terms, group = [], None
    for line in lines:
        m = TERM.match(line)
        if m:
            terms.append((int(m.group(7)), int(m.group(2)), m.group(3), group))
        elif line.startswith("  A_"):
            group = line.strip()[2:]
    out = []
    for d in (8, 6):
        top = max((t[0] for t in terms if t[1] == d), default=None)
        if top is not None:
            names = sorted({math(c) + ("" if g is None else " " + GROUP.get(g, "A_" + g))
                            for e, dd, c, g in terms if dd == d and e == top})
            out.append(paint(f"dim {d}: ", BOLD) + paint(", ".join(names) + f"  E{sup(top)}", grow(top)))
    return "   ".join(out)


def _series_result(lines, cols):
    out, sm = [], paint(f"{'SM':4s}", BOLD)
    for i, line in enumerate(lines):
        m, s = TERM.match(line), SMTERM.match(line)
        if i == 0:
            proc, sep, rest = line.partition(": ")
            out.append(paint(proc, BOLD) + paint(("   " + rest) if sep else "", GREY))
        elif line.startswith("  model "):
            out.append(paint("  " + math(line.strip()), GREY))
        elif line.startswith("  Standard Model amplitude of the channel"):
            p = re.search(r"lambda\^(-?\d+)", line).group(1)
            out.append("  " + paint(f"SM amplitude λ{sup(p)}", BOLD) + paint("    fastest growth  ", GREY)
                       + _fastest(lines))
        elif line.startswith(("  an unmarked W or Z", "  no Standard Model tree in this channel")):
            out.append(paint("  " + line.strip(), GREY))
        elif line.startswith("  A_"):
            if not any(x.startswith("  A_") for x in lines[:i]):
                out.append(legend())
                out.append(paint(f"  {'power':9s} {'dim':4s} {'class':14s} {'couplings':24s} {'vs SM':10s} operators",
                                 GREY))
            g = line.strip()[2:]
            out.append(paint(f"  {GROUP.get(g, 'A_' + g)}", BOLD))
        elif s:
            out.append(f"    {math('lambda^' + s.group(1)):5s}   {sm} {math(s.group(2))}")
        elif m:
            p, d, cls, star, why, coup, e, v, k, ops = m.groups()
            code = grow(int(e))
            row = (f"  {paint('★', GROW[4]) if star else ' '} {math('lambda^' + p):5s}   d{d:3s} "
                   f"{paint(f'{math(cls):14s}', code)} {math(coup):24s} {paint(f'{_growth(e, v, k):10s}', code)} "
                   + paint(math(ops), GREY if code == GROW[-1] else ""))
            out.append(row + (paint(f"  ({why})", GREY) if why else ""))
        elif line.strip():
            out += footnote(line, cols)
        else:
            out.append("")
    return out


def series(lines, cols):
    """The view of ./dim8 series, result by result (--vbf prints one result a polarisation channel).  A result
    starts at its unindented header line, and the notes that end the output stay with the last one."""
    blocks = []
    for line in lines:
        if not blocks or (line and not line.startswith((" ", "note:"))):
            blocks.append([])
        blocks[-1].append(line)
    return [row for b in blocks for row in _series_result(b, cols)]


# ------------------------------------------------------------------------------------------- select --

CLS = re.compile(r"^class (\d+):$")


def op_row(line):
    """(name, coefficient, power or None, 'via', 'class' or '', the legs or the class, [notes]) of an operator
    line of ./dim8 select, which prints f"  {name:34s} {coefficient:16s} {power:10s} via {legs}" and its notes,
    each as "   (note)", with "class N" for "via ..." in the input relations, or nothing after the power.  The
    columns are read by position, since a name may hold a space (Q_{H\\widetilde W}).  None for any other line."""
    if len(line.rstrip()) < 39 or not line.startswith("  ") or line[2] == " " or line[36:37] != " " \
            or not re.fullmatch(r"c\w+", line[37:53].strip()):
        return None
    pw, rest = line[54:64].strip(), line[65:]
    p = re.fullmatch(r"lambda\^(-?\d+)", pw)
    if (pw and not p) or line[53:54] not in (" ", "") or (rest and line[64] != " "):
        return None
    kind, _, after = rest.partition(" ")
    if kind not in ("via", "class", ""):
        return None
    legs, _, notes = after.partition("   (")
    notes = re.split(r"\)   \(", notes[:-1]) if notes else []
    return line[2:36].strip(), line[37:53].strip(), int(p.group(1)) if p else None, kind, legs, notes


def _tags(notes):
    out = []
    for note in notes:
        for long, short in TAGS:
            note = note.replace(long, short)
        out.append(math(note))
    return out


def select(lines, cols):
    from lambda_routes import CLASSES
    sm = 0
    for line in lines:
        m = re.search(r"Standard Model amplitude (?:of the channel )?is lambda\^(-?\d+)", line)
        if m:
            sm = int(m.group(1))
    # the growth of every operator with a power, for the line that names the fastest classes
    count, cls, dim = {}, None, 8
    for line in lines:
        if CLS.match(line):
            cls, dim = CLASSES.get(int(CLS.match(line).group(1)), "?"), 8
        elif line.startswith("dimension six"):
            cls, dim = line.split(", ", 1)[-1].rstrip(":"), 6
        elif line.startswith("through the "):
            cls = None
        r = op_row(line)
        if r and r[2] is not None and r[3] == "via" and cls is not None:
            e = (8 if dim == 8 else 4) - (r[2] - sm)
            count.setdefault((dim, e), {}).setdefault(cls, 0)
            count[(dim, e)][cls] += 1
    lead = []
    for d in (8, 6):
        top = max((e for dd, e in count if dd == d), default=None)
        if top is not None:
            names = ", ".join(f"{math(c)} ({n})" for c, n in count[(d, top)].items())
            lead.append(paint(f"dim {d}: ", BOLD) + paint(names + f"  E{sup(top)}", grow(top)))
    out, dim, legs_ir = [], 8, False
    for line in lines:
        r, mc = op_row(line), CLS.match(line)
        if line.startswith("process :"):
            out.append(paint(line.split(":", 1)[1].strip(), BOLD))
        elif line.startswith(("external:", "model   :")):
            out.append(paint("  " + math(line), GREY))
        elif line.startswith("selected: "):
            n = re.match(r"selected: (\d+)( of the 674 dimension-eight operators through a vertex)( of the process)?(.*)$",
                         line)
            out.append("  " + (paint(n.group(1), BOLD) + n.group(2) + math(n.group(4)) if n else math(line[10:])))
        elif line.startswith("          "):
            out.append(paint(math(line), GREY))
        elif line.startswith("each operator with the vertex of its leading tree"):
            continue
        elif line.startswith("(Lambda, E, v) ~"):
            out.append("  " + paint("fastest growth  ", GREY) + "   ".join(lead))
            out.append(legend())
            out.append(paint(f"  {'operator':22s} {'coefficient':14s} {'power':6s} leading vertex", GREY))
        elif mc:
            dim, legs_ir = 8, False
            n = int(mc.group(1))
            out.append(paint(f"class {n}  " + math(CLASSES.get(n, "")), BOLD))
        elif line.startswith(("dimension six", "through the ")):
            dim = 6 if line.startswith("dimension six") else dim
            legs_ir = line.startswith("through the ") or "input relations" in line
            out.append(paint(math(line.rstrip(":")), BOLD))
        elif r:
            name, wc, p, kind, legs, notes = r
            if p is None:
                code, pw = GROW[-1], ""
            else:
                code = grow((8 if dim == 8 else 4) - (p - sm)) if kind == "via" and not legs_ir else ""
                pw = math(f"lambda^{p}")
            row = (f"  {paint(f'{math(name):22s}', code)} {wc:14s} {paint(f'{pw:6s}', code)} "
                   + paint(math(legs) if kind == "via" else f"class {legs}" if kind else "", GREY))
            tags = _tags(notes)
            out.append(row + ("  " + paint(" · ".join(tags), GROW[-1]) if tags else ""))
        elif line.lstrip("\n").startswith("wrote "):
            out.append(paint(line.strip(), GREEN))
        elif line.startswith(("import with:", "then set:")):
            label, rest = line.split(":", 1)
            out.append(paint(label + ":", BOLD) + paint(rest, GREEN))
        elif line.strip():
            out += footnote(line, cols)
        else:
            out.append("")
    return out


# ------------------------------------------------------------------------------------------- the CLI --

def render(text, cols=None):
    """The view of a plain output of ./dim8 select or ./dim8 series, or the text as it is when it is neither.
    It is never drawn narrower than 60 columns, below which a wrapped footnote would hold a word a line."""
    cols = max(cols or width(), 60)
    lines = text.split("\n")
    if any(x.startswith("selected: ") for x in lines):
        return "\n".join(select(lines, cols))
    if any(x.startswith("  A_") for x in lines):
        return "\n".join(series(lines, cols))
    return text


def run(func, a):
    """Run a command of ./dim8 with its output caught, and print the view of it, also when it stops.  Should
    the view fail on an output, the plain text is printed instead and stderr says why, so that the result of
    the command is never lost to its display."""
    buf = io.StringIO()
    try:
        with redirect_stdout(buf):
            code = func(a)
    finally:
        text = buf.getvalue()
        if text:
            try:
                shown = render(text.rstrip("\n")) + "\n"
            except Exception as e:           # noqa: BLE001  the plain text is the result, the view only its display
                shown = text
                print(f"gen/pretty.py could not draw this output ({type(e).__name__}: {e}), so it is the plain "
                      "text. NO_COLOR=1 turns the view off.", file=sys.stderr)
            sys.stdout.write(shown)
            sys.stdout.flush()
    return code or 0


def main(argv) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    print(render(open(argv[1]).read().rstrip("\n"), int(argv[2]) if len(argv) > 2 else None))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
