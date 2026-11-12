"""
tests/test_pretty.py: the terminal view of ./dim8 select and ./dim8 series (gen/pretty.py).

Run:  python3 tests/test_pretty.py       (with models/dim8_mw and models/dim68_mw unpacked)

In a pipe both commands print their plain text with no colour, and so does FORCE_COLOR=1 with NO_COLOR set,
and --json stays JSON under FORCE_COLOR.  Under FORCE_COLOR=1 the view keeps every coefficient of the plain
selection and every term of the plain series, and its line of fastest growth names what the counting gives:
psi^2X^2D in the contact terms at E^4 and X^3 in the s channel at E^2 for u u~ > w+ w-, psi^2H^2D^3 and
psi^2H^2D in the contact terms for u u~ > w+{0} w-{0}, and the classes X^4 (7 operators) and psi^2X^2D (6)
for p p > w+ w-, with X^3 (Q_W and Q_W~) at E^2 for dim68_mw.  Every coefficient of a selection keeps a row of
its own in the view, also one whose operator name holds a space (Q_{H\\widetilde W}), which a parser that split
the columns at spaces once left as raw text.  A command that stops still stops, with its message, and text that is neither output is
left as it is.  On a real pseudo-terminal, which reports 0 columns, ./dim8 series draws the view with nothing
on stderr (the width of 0 once crashed it there), and the view is the same at every width below 60.
"""

import json
import os
import re
import subprocess
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "gen"))

import pretty as V  # noqa: E402

ESC = "\033["
PLAIN = re.compile(r"\x1b\[[0-9;]*m")


def dim8(args, **env):
    e = {k: v for k, v in os.environ.items() if k not in ("NO_COLOR", "FORCE_COLOR")}
    e.update(env)
    return subprocess.run([sys.executable, os.path.join(ROOT, "dim8")] + args, capture_output=True, text=True,
                          env=e, timeout=600)


def main() -> int:
    for m in ("dim8_mw", "dim68_mw"):
        if not os.path.isfile(os.path.join(ROOT, "models", m, "couplings.py")):
            sys.exit(f"tests/test_pretty.py: unpack models/{m} first (cd models && tar -xJf {m}.tar.xz)")
    ok = 0
    runs = {"sel": ["select", "p p > w+ w-"], "sel6": ["select", "p p > w+ w-", "--model", "dim68_mw"],
            "T": ["series", "u u~ > w+ w-"], "L": ["series", "u u~ > w+{0} w-{0}"]}
    plain = {k: dim8(a) for k, a in runs.items()}
    view = {k: dim8(a, FORCE_COLOR="1") for k, a in runs.items()}
    for k in runs:
        assert plain[k].returncode == 0 and view[k].returncode == 0, (k, plain[k].stderr, view[k].stderr)
        assert ESC not in plain[k].stdout and ESC in view[k].stdout, k
    ok += 1                                           # plain in a pipe, the view under FORCE_COLOR
    both = dim8(runs["T"], FORCE_COLOR="1", NO_COLOR="1")
    assert both.returncode == 0 and both.stdout == plain["T"].stdout, both.stdout[:300]
    js = dim8(runs["T"] + ["--json"], FORCE_COLOR="1")
    assert js.returncode == 0 and ESC not in js.stdout and json.loads(js.stdout)["results"], js.stdout[:300]
    ok += 1                                           # NO_COLOR wins, and --json stays JSON
    for k in ("sel", "sel6"):
        shown = PLAIN.sub("", view[k].stdout).split("\n")
        wcs = re.findall(r"^  .{34} (c\w+) ", plain[k].stdout, re.M)   # select prints the name in 34 columns
        assert len(wcs) > 90, (k, len(wcs))
        for w in wcs:
            rows = [x for x in shown if re.search(rf"(?<![\w]){w}(?![\w])", x)]
            assert rows and not any(" via " in x for x in rows), (k, w, rows)
    ok += 1                                           # every coefficient of the selection is in the view, as a row
    for k in ("T", "L"):
        terms = [m.groups() for m in map(V.TERM.match, plain[k].stdout.split("\n")) if m]
        shown = PLAIN.sub("", view[k].stdout)
        assert terms and all(re.search(re.escape(V.math("lambda^" + t[0])) + r"\s+d" + t[1] + r"\s+"
                                       + re.escape(V.math(t[2])) + r"\s", shown) for t in terms), k
        assert shown.count("★") == sum(1 for t in terms if t[3]), k
    ok += 1                                           # every term of the series is in the view, starred alike
    lead = {k: next(x for x in PLAIN.sub("", view[k].stdout).split("\n") if "fastest growth" in x) for k in runs}
    assert "dim 8: ψ²X²D contact  E⁴" in lead["T"] and "dim 6: X³ s channel  E²" in lead["T"], lead["T"]
    assert "dim 8: ψ²H²D³ contact  E⁴" in lead["L"] and "dim 6: ψ²H²D contact  E²" in lead["L"], lead["L"]
    assert "dim 8: X⁴ (7), ψ²X²D (6)  E⁴" in lead["sel"], lead["sel"]
    assert "dim 8: X⁴ (7), ψ²X²D (6)  E⁴" in lead["sel6"] and "dim 6: X³ (2)  E²" in lead["sel6"], lead["sel6"]
    ok += 1                                           # the fastest growth, as the counting gives it
    nope = dim8(["select", "p p > w+ w-", "--model", "dim8_nope"], FORCE_COLOR="1")
    assert nope.returncode != 0 and nope.stderr.strip(), (nope.returncode, nope.stderr)
    text = "psi^2X^2D    leading power of the class's vertex\n  lambda^4 at four legs"
    assert V.render(text, 100) == text
    ok += 1                                           # a stop stays a stop, other text is left alone
    code, out, err = on_terminal(runs["T"])
    assert code == 0 and ESC in out and "fastest growth" in PLAIN.sub("", out) and not err.strip(), (code, err)
    assert V.render(plain["T"].stdout, 1) == V.render(plain["T"].stdout, 60)
    ok += 1                                           # on a terminal that reports 0 columns, and at any width
    print(f"tests/test_pretty.py: {ok}/7 checks of the terminal view pass")
    return 0


def on_terminal(args):
    """./dim8 with its stdout on a new pseudo-terminal, which reports 0 columns as script's and some editors' do."""
    import pty
    e = {k: v for k, v in os.environ.items() if k not in ("NO_COLOR", "FORCE_COLOR", "COLUMNS")}
    e["TERM"] = "xterm-256color"
    master, slave = pty.openpty()
    p = subprocess.Popen([sys.executable, os.path.join(ROOT, "dim8")] + args, stdout=slave,
                         stderr=subprocess.PIPE, stdin=subprocess.DEVNULL, env=e)
    os.close(slave)
    chunks = []
    while True:
        try:
            b = os.read(master, 65536)
        except OSError:                               # Linux: the other end is closed
            break
        if not b:                                     # macOS: end of file
            break
        chunks.append(b)
    os.close(master)
    err = p.stderr.read().decode()
    return p.wait(timeout=600), b"".join(chunks).decode("utf-8", "replace"), err


if __name__ == "__main__":
    sys.exit(main())
