#!/usr/bin/env python3
"""Evaluate a UFO's internal parameters for given external values, the way MadGraph does.

    validate/eval_ufo_params.py <UFO dir> [NAME=VALUE ...] [--show NAME,NAME,...]

Prints the input-scheme shifts (gw1, gw2, rW1, rW2, vev1, vev2, MW21, MW22, TAA2, TZA2, ...) and any
parameters named with --show, for the coefficient values given.  Needs a Python that can import the
UFO (3.11 works; the UFO's own files are Python 2 flavoured until MadGraph converts them).
"""
import sys, os, cmath, math

def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    ufo = os.path.abspath(argv[1]); sys.path.insert(0, ufo)
    import parameters as P
    show = ["gw1", "gw2", "rW1", "rW2", "vev1", "vev2", "MW21", "MW22", "TAA1", "TAA2", "TZA2", "TZZ2", "rh2", "MW", "MW2SM", "vevT", "vevSM", "d8fG", "d8fW", "d8mW", "d8mZ"]
    vals = {}
    for p in P.all_parameters:
        if p.nature == "external": vals[p.name] = float(p.value)
    for a in argv[2:]:
        if a.startswith("--show"): show += a.split("=", 1)[1].split(",") if "=" in a else []
        elif a.startswith("dim8_all="):   # every dimension-eight coefficient at once, as the studies set them
            v = float(a.split("=", 1)[1])
            for k in list(vals):
                if k.startswith("c8"): vals[k] = v
        elif "=" in a:
            k, v = a.split("=", 1); vals[k] = float(v)
    ns = {"cmath": cmath, "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z, "complex": complex, "math": math}
    for p in P.all_parameters:
        if p.nature == "internal":
            try: vals[p.name] = eval(p.value, ns, vals)
            except Exception: vals[p.name] = float("nan")
    def r(z): return z.real if isinstance(z, complex) else z
    for k in show:
        if k in vals: print(f"{k:8s} = {r(vals[k]):.10g}")
    if all(k in vals for k in ("gw1", "gw2", "rW1", "rW2")):
        print("effective q q W coupling shift (1+gw1+gw2)(1+rW1+rW2)-1 =", f"{r((1+vals['gw1']+vals['gw2'])*(1+vals['rW1']+vals['rW2'])-1):.4g}")
    if "MW" in vals and "MW2SM" in vals:
        print("MW relative shift =", f"{r(vals['MW'])/math.sqrt(r(vals['MW2SM']))-1:.4g}")
    return 0

if __name__ == "__main__": sys.exit(main(sys.argv))
