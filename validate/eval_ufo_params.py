#!/usr/bin/env python3
"""Evaluate a UFO's internal parameters for given external values, the way MadGraph does.

    validate/eval_ufo_params.py <UFO dir> [NAME=VALUE ...] [--show NAME,NAME,...]

Prints the input-scheme shifts (gw1, gw2, rW1, rW2, vev1, vev2, MW21, MW22, TAA2, TZA2, ...) and any
parameters named with --show, for the coefficient values given.  Needs a Python that can import the
UFO (3.11 works; the UFO's own files are Python 2 flavoured until MadGraph converts them).

The functions of the UFO's function_library.py (cond, reglog, re, im, ...) are made from their
expressions, as MadGraph makes them, so that a parameter written with any of them is evaluated.  The
relation for G_F with nonzero lepton Yukawa couplings uses cond, and without it M_W, vevT and gw2 of
those models came out as nan.  An internal parameter that cannot be evaluated is printed as nan, and
the script names it on stderr and exits with 1.
"""
import sys, os, ast, cmath, math

# A sum whose terms cancel to this fraction of the sum of their moduli is an identity and not a number: at a
# point where every input is generic, terms that are not identically opposite cancel by a few digits, never by
# ten, so what is left of them (the unitarity of the CKM matrix in a flavour matrix, cw^2 + sw^2 = 1 in a
# coupling) is rounding, 2^-74 on one machine and 0 on the next.  The threshold is that of validate/np_truncate.m.
RESIDUE = 1e-10
_AT = dict(lineno=1, col_offset=0, end_lineno=1, end_col_offset=0)

def _moduli(expr):
    """Compiled: the sum of the moduli of the terms of an expression, the summands of its sums and differences."""
    terms, stack = [], [ast.parse(expr, mode="eval").body]
    while stack:
        n = stack.pop()
        if isinstance(n, ast.BinOp) and isinstance(n.op, (ast.Add, ast.Sub)):
            stack += [n.left, n.right]
        elif isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
            stack.append(n.operand)
        else:
            terms.append(ast.Call(func=ast.Name(id="_modulus", ctx=ast.Load(), **_AT), args=[n], keywords=[], **_AT))
    while len(terms) > 1:      # a balanced tree, so that a sum of thousands of terms compiles
        terms = [ast.BinOp(left=terms[i], op=ast.Add(), right=terms[i + 1], **_AT) if i + 1 < len(terms) else terms[i]
                 for i in range(0, len(terms), 2)]
    return compile(ast.Expression(terms[0]), "<moduli>", "eval")

def cancelled(value, expr, ns, vals):
    """Whether the number the expression gave at vals is what rounding left of terms that cancel (RESIDUE).
    The zero tests take such a number for the exact zero it stands for, on every machine alike."""
    return value != 0 and abs(value) <= RESIDUE * eval(_moduli(expr), ns, vals)

def namespace():
    """The names an expression of the UFO on sys.path is evaluated with: cmath, math, complex,
    complexconjugate and the functions of its function_library.py, made from their expressions.
    Call it once the UFO's parameters are imported."""
    ns = {"cmath": cmath, "complexconjugate": lambda z: z.conjugate() if isinstance(z, complex) else z, "complex": complex, "math": math}
    try:
        import function_library as F
    except ImportError:
        F = None
    for f in (F.all_functions if F else []):
        # ('z') in a function library is the string 'z', not a tuple
        args = (f.arguments,) if isinstance(f.arguments, str) else tuple(f.arguments)
        ns[f.name] = eval(f"lambda {', '.join(args)}: {f.expr}", ns)
    ns["_modulus"] = abs
    return ns

def internal_parameters(P, vals, ns, residue=False):
    """The internal parameters of P.all_parameters, evaluated in their order into vals, which holds
    the external ones.  One that cannot be evaluated stops the script with its name, since a nan in
    its place makes a nan of every coupling that carries it, and a test would then leave those out.
    With residue, a parameter whose terms cancel to rounding is set to zero (cancelled)."""
    for p in P.all_parameters:
        if p.nature == "internal":
            try:
                vals[p.name] = eval(p.value, ns, vals)
                if residue and cancelled(vals[p.name], p.value, ns, vals):
                    vals[p.name] = 0.0
            except Exception as e:
                raise SystemExit(f"the internal parameter {p.name} = {p.value} cannot be evaluated "
                                 f"({type(e).__name__}: {e})")
    return vals

def coupling(name, value, ns, vals, residue=None):
    """The number a coupling is at vals, from its expression or the compiled expression.  One that
    cannot be evaluated, or that is not a number there, stops the script with its name.  With residue,
    the expression as text, a coupling whose terms cancel to rounding is zero (cancelled)."""
    try:
        g = complex(eval(value, ns, vals))
        if residue is not None and cancelled(g, residue, ns, vals):
            g = 0j
    except Exception as e:
        raise SystemExit(f"the coupling {name} cannot be evaluated ({type(e).__name__}: {e})")
    if g != g:
        raise SystemExit(f"the coupling {name} is not a number at the point it is evaluated at")
    return g

def main(argv):
    if len(argv) < 2: print(__doc__); return 2
    ufo = os.path.abspath(argv[1]); sys.path.insert(0, ufo)
    import parameters as P
    show = ["gw1", "gw2", "rW1", "rW2", "vev1", "vev2", "MW21", "MW22", "TAA1", "TAA2", "TZA2", "TZZ2", "rh2", "MW", "MW2SM", "vevT", "vevSM", "d8fG", "d8fW", "d8mW", "d8mZ"]
    vals = {}
    for p in P.all_parameters:
        if p.nature == "external": vals[p.name] = float(p.value)
    internal = {p.name for p in P.all_parameters if p.nature == "internal"}
    for a in argv[2:]:
        if a.startswith("--show"): show += a.split("=", 1)[1].split(",") if "=" in a else []
        elif a.startswith("dim8_all="):   # every dimension-eight coefficient at once, as the studies set them
            v = float(a.split("=", 1)[1])
            for k in list(vals):
                if k.startswith("c8"): vals[k] = v
        elif "=" in a:
            k, v = a.split("=", 1); vals[k] = float(v)
            if k in internal: print(f"warning: {k} is an internal parameter of this UFO, and the value given changes nothing", file=sys.stderr)
    ns = namespace()
    bad = {}
    for p in P.all_parameters:
        if p.nature == "internal":
            try: vals[p.name] = eval(p.value, ns, vals)
            except Exception as e:
                vals[p.name] = float("nan"); bad[p.name] = f"{type(e).__name__}: {e}"
    if bad:
        first = next(iter(bad))
        print(f"eval_ufo_params: {len(bad)} internal parameters could not be evaluated, the first {first} ({bad[first]})",
              file=sys.stderr)
    def r(z): return z.real if isinstance(z, complex) else z
    for k in show:
        if k in vals: print(f"{k:8s} = {r(vals[k]):.10g}")
    if all(k in vals for k in ("gw1", "gw2", "rW1", "rW2")):
        print("effective q q W coupling shift (1+gw1+gw2)(1+rW1+rW2)-1 =", f"{r((1+vals['gw1']+vals['gw2'])*(1+vals['rW1']+vals['rW2'])-1):.4g}")
    if "MW" in vals and "MW2SM" in vals:
        print("MW relative shift =", f"{r(vals['MW'])/math.sqrt(r(vals['MW2SM']))-1:.4g}")
    return 1 if bad else 0

if __name__ == "__main__": sys.exit(main(sys.argv))
