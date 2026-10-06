#!/usr/bin/env python3
"""Copy a UFO to <dir>_on with every dimension-eight coefficient set to a value (default 0.7).

    validate/ufo_on.py <UFO dir> [value]

MadGraph's `check lorentz` / `check gauge` evaluate the model at the DEFAULT parameter values in
parameters.py: the optional param-card argument of `check` leaves the couplings untouched (tested
on MG5_aMC 3.5.3: g g > h g stays "not checked" with a card that switches Q_{G^2H^4}^{(1)} on),
and `set c8... 0.7` at the top level sets MG5 options, not parameters.  So a check with the
operators on needs a copy of the model whose defaults are on.  This edits parameters.py value
line by value line (a blanket sed once turned "c8l2WH2Dx1 ... 1" into "c8l2WH2Dx10.7"); the scale
Lam keeps its default.  Pure Python.
"""
import os, re, shutil, sys


def main(argv):
    if len(argv) < 2:
        print(__doc__); return 2
    src = os.path.abspath(argv[1]).rstrip("/"); val = argv[2] if len(argv) > 2 else "0.7"
    dst = src + "_on"
    if os.path.exists(dst): shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__", "*.pyc", "*.log", "*.cmd"))
    p = os.path.join(dst, "parameters.py"); lines = open(p).read().split("\n")
    out, pending, n = [], False, 0
    for l in lines:
        if re.match(r"\w+ = Parameter\(name = 'c8\w+'", l): pending = True
        if pending and re.match(r"\s*value = 0,?\s*$", l):
            l = l.replace("value = 0", f"value = {val}"); n += 1; pending = False
        elif pending and "value =" in l:
            pending = False
        out.append(l)
    open(p, "w").write("\n".join(out))
    print(f"{dst}: {n} coefficients set to {val}; import it as {os.path.basename(dst)}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
