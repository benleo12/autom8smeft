#!/usr/bin/env python3
"""Make a model's write_param_card.py write the whole parameter card.

    examples/fix_param_card_writer.py <model dir> [<model dir> ...]

MadGraph runs the model's write_param_card.py in every process directory to write the default
parameter card, from which it takes any entry that the card of a run leaves out.  FeynRules copies
the script from its UFO template, which evaluates the parameters' expressions without the UFO's
own functions, so it stops at the first parameter that calls complexconjugate (the complex
coefficients of these models) with a NameError.  The default card then holds the blocks written
before it, a card without block DIM8F stops the run with a KeyError instead of taking the zeros of
the default, and every run prints the traceback.  This evaluates the expressions with
function_library.  It is idempotent, and examples/release_model.sh runs it on every model.
"""
import sys

OLD = (
    "        import cmath\n"
    "        from parameters import all_parameters\n"
    "        for parameter in all_parameters:\n"
    "            exec(\"%s = %s\" % (parameter.name, parameter.value))\n")
NEW = (
    "        import cmath\n"
    "        import function_library\n"
    "        from parameters import all_parameters\n"
    "        # the expressions call the functions of the UFO (complexconjugate, re, im, ...)\n"
    "        ns = {'cmath': cmath}\n"
    "        ns.update((k, v) for k, v in vars(function_library).items() if not k.startswith('_'))\n"
    "        for parameter in all_parameters:\n"
    "            exec(\"%s = %s\" % (parameter.name, parameter.value), ns)\n")
OLD_EVAL = "                value = complex(eval(param.value)).real\n"
NEW_EVAL = "                value = complex(eval(param.value, ns)).real\n"


def fix(d):
    p = f"{d}/write_param_card.py"
    s = open(p).read()
    if s.count(NEW) == 1 and s.count(NEW_EVAL) == 1:
        print(f"{p}: already evaluates with function_library")
        return
    if s.count(OLD) != 1 or s.count(OLD_EVAL) != 1:
        sys.exit(f"{p}: not the FeynRules template this fixes")
    s = s.replace(OLD, NEW).replace(OLD_EVAL, NEW_EVAL)
    compile(s, p, "exec")
    open(p, "w").write(s)
    print(f"{p}: evaluates the parameters with function_library")


if __name__ == "__main__":
    for d in sys.argv[1:]:
        fix(d)
