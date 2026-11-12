#!/usr/bin/env python3
"""What MadGraph would get wrong by importing a UFO with a restriction card.

    import card_fusion as F
    u = F.read_ufo(<model directory>)
    F.fusion_problems(u, <restriction card>, random.Random(1))   # [] when nothing would go wrong

MadGraph reads a restriction card as more than a list of what to keep (models/import_ufo.py).  It removes a
coupling that vanishes at the values of the card with its vertices, and it fuses couplings of one order whose
values at the card agree up to sign, to about ten digits, into one, which keeps the formula of the first at any
values of the run.  fusion_problems evaluates the couplings of the UFO at the card and at a second point of the
kept coefficients and lists the couplings MadGraph would fuse or remove at the card that differ, or do not
vanish, at the second point.  tests/test_restriction_cards.py runs it on every card of the released models, and
validate/cp_flavour.py on the card it writes before it runs.
"""

import ast
import cmath
import math
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from make_restriction import is_coefficient  # noqa: E402

WORD = re.compile(r"\b[A-Za-z_]\w*\b")


def entries(card):
    """(block, name, value) of every parameter line of a card, the DECAY lines aside."""
    block = None
    for line in open(card):
        b = re.match(r"^\s*block\s+(\w+)", line, re.I)
        if b:
            block = b.group(1).upper()
            continue
        m = re.match(r"^\s*(?:\d+\s+)+([-\deE.+]+)\s*#\s*(\w+)", line)
        if m:
            yield block, m.group(2), float(m.group(1))



def read_ufo(model):
    """A UFO read as text, as validate/index_vs_ufo.py reads one, in a form to evaluate again and again: the
    functions of the model (ns), the default of every external parameter, a coefficient at zero (external),
    the coefficients (coeffs), the internal parameters in an order that evaluates, compiled (order), and for
    every coupling its compiled value (codes), its text (exprs), its interaction order (orders) and the coefficients
    that reach it, by name or through an internal parameter (reach).  bases holds the values of the couplings with every
    coefficient at zero, by the other inputs."""
    rd = lambda f: open(os.path.join(model, f + ".py"), errors="replace").read()  # noqa: E731
    ns = {"cmath": cmath, "complex": complex, "pi": cmath.pi}
    if os.path.isfile(os.path.join(model, "function_library.py")):
        for m in re.finditer(r"(\w+) = Function\(\s*name = '\w+',\s*arguments = \(([^)]*)\),\s*expression = '([^']*)'",
                             rd("function_library")):
            args = ",".join(a.strip().strip("'\"") for a in m.group(2).split(",") if a.strip())
            ns[m.group(1)] = eval(f"lambda {args}: {m.group(3)}", dict(ns))
    external, coeffs, todo = {}, set(), []
    for name, nature, value, rest in re.findall(r"(\w+) = Parameter\(\s*name = '\w+',\s*nature = '(\w+)',\s*type = '\w+',\s*"
                                                r"value = ('[^']*'|[^,]+),(.*?)\)\n", rd("parameters"), re.S):
        if nature == "external":
            block = re.search(r"lhablock = '(\w+)'", rest)
            external[name] = complex(eval(value))
            if block and is_coefficient(block.group(1).upper(), name):
                coeffs.add(name)
                external[name] = 0.0
        else:
            todo.append((name, value.strip("'")))
    scope, order = dict(ns, **external), []
    for _ in range(len(todo) + 1):
        left = []
        for name, value in todo:
            try:
                scope[name] = eval(value, scope)
                order.append((name, value))
            except (NameError, ZeroDivisionError, ValueError, TypeError):
                left.append((name, value))
        if not left or len(left) == len(todo):
            break
        todo = left
    deps = {}
    for name, value in order:
        names = set(WORD.findall(value))
        deps[name] = (names & coeffs).union(*(deps[x] for x in names if x in deps))
    codes, exprs, orders, reach = {}, {}, {}, {}
    for g, expr, how in re.findall(r"(\w+) = Coupling\(\s*name = '\w+',\s*value = '([^']*)',\s*order = \{([^}]*)\}\)",
                                   rd("couplings")):
        names = set(WORD.findall(expr))
        codes[g] = compile(expr, g, "eval")
        exprs[g] = expr
        orders[g] = ",".join(sorted(x.strip() for x in how.split(",")))
        reach[g] = (names & coeffs).union(*(deps[x] for x in names if x in deps))
    return {"ns": ns, "external": external, "coeffs": coeffs, "codes": codes, "exprs": exprs, "orders": orders, "reach": reach,
            "order": [(n, compile(v, n, "eval")) for n, v in order], "bases": {}}


def internal_values(u, externals):
    ns = dict(u["ns"])
    ns.update(externals)
    for name, code in u["order"]:
        ns[name] = eval(code, ns)
    return ns


def rounded(z):
    """The value of a coupling as detect_identical_couplings of MadGraph compares it."""
    def digits(x):
        return round(x, int(abs(round(math.log(abs(x), 10), 0)) + 10)) if x else x
    return complex(digits(z.real), digits(z.imag))


def cancels(u, g, ns):
    """Is this coupling at these values only the rounding of terms that cancel?  That is the mark of a coupling that
    vanishes for every value, as -c c_w g_1 + c s_w g_2 does in the {MW, MZ, GF} scheme.  Its size against the other
    couplings of its order says nothing, since a six-leg coupling lies far below a three-leg one with its vevs."""
    terms, todo = [], [ast.parse(u["exprs"][g], mode="eval").body]
    while todo:
        t = todo.pop()
        if isinstance(t, ast.BinOp) and isinstance(t.op, (ast.Add, ast.Sub)):
            todo += [t.left, t.right]
        elif isinstance(t, ast.UnaryOp) and isinstance(t.op, (ast.USub, ast.UAdd)):
            todo.append(t.operand)
        else:
            terms.append(t)
    big = max(abs(eval(compile(ast.Expression(t), g, "eval"), ns)) for t in terms)
    return abs(eval(u["codes"][g], ns)) <= 1e-12 * big


def fusion_problems(u, card, rnd=None):
    """What MadGraph would get wrong by importing the model with this card: couplings of one order that it
    fuses at the values of the card and that differ at a second point of the kept coefficients, random or,
    with no generator, every one at 1, and couplings that it removes there and that do not vanish at that
    point.  Everything else stays as the card has it.  As in detect_identical_couplings, a coupling below
    1e-13 counts as zero unless some coupling lies between 1e-13 and 1e-10, and only one that is exactly
    zero then.  Couplings that vanish for every value (cancels) differ only by rounding and are no problem."""
    inputs, kept = {}, {}
    for block, name, v in entries(card):
        if name in u["coeffs"]:
            if v != 0.0:
                kept[name] = v
        elif name in u["external"]:
            inputs[name] = complex(v)
    zero = dict(u["external"], **inputs)
    key = tuple(sorted(inputs.items(), key=lambda kv: kv[0]))
    if key not in u["bases"]:
        ns = internal_values(u, zero)
        u["bases"][key] = {g: complex(eval(c, ns)) for g, c in u["codes"].items()}
    reached = [g for g, d in u["reach"].items() if not d.isdisjoint(kept)]

    ns1 = internal_values(u, dict(zero, **kept))
    ns2 = internal_values(u, dict(zero, **{n: (rnd.uniform(0.1, 0.9) if rnd else 1.0) for n in kept}))
    first = {g: complex(eval(u["codes"][g], ns1)) for g in reached}
    second = {g: complex(eval(u["codes"][g], ns2)) for g in reached}
    values = dict(u["bases"][key], **first)
    strict = any(1e-13 <= abs(z) < 1e-10 for z in values.values())
    gone = lambda z: z == 0 or (not strict and abs(z) < 1e-13)  # noqa: E731
    bad = []
    for g in reached:
        if gone(first[g]) and not cancels(u, g, ns2):
            bad.append(f"{g} vanishes at the card and not elsewhere, so MadGraph would remove its vertices")
    groups = {}
    for g in sorted(values):
        if gone(values[g]):
            continue
        v, how = rounded(values[g]), u["orders"][g]
        if (how, v) in groups:
            groups[(how, v)].append((g, 1))
        elif (how, -v) in groups:
            groups[(how, -v)].append((g, -1))
        else:
            groups[(how, v)] = [(g, 1)]
    for members in groups.values():
        g0 = members[0][0]
        for g, sign in members[1:]:
            a, b = second.get(g, values[g]), sign * second.get(g0, values[g0])
            if abs(a - b) > 1e-9 * max(abs(a), abs(b)) and not all(cancels(u, x, n) for x in (g, g0) for n in (ns1, ns2)):
                bad.append(f"{g} and {g0} agree at the card and not elsewhere, so MadGraph would fuse different couplings")
    return bad


if __name__ == "__main__":
    print(__doc__)
