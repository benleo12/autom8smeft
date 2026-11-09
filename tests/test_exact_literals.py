"""
tests/test_exact_literals.py: decimal literals of a UFO written as exact fractions.

Run:  python3 tests/test_exact_literals.py

On a small UFO written here: a leading -1/6 and -1/3 become (1./6.) and (1./3.) and evaluate to
the same doubles, a literal seven digits already reproduce (0.5, 2.5e-3, 6.) and a name with
digits (c8l2H2D3x1) are left alone, a decimal with no small fraction is left and reported, the
default value of an external parameter is never touched, the rewrite is idempotent, and --check
fails before and passes after.  Then every shipped model under models/ must pass --check, since a
seven-digit coupling breaks the photon/Z cancellation in MadGraph (validate/exact_literals.py).
"""

import glob
import io
import os
import shutil
import sys
import tempfile
from contextlib import redirect_stdout

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "validate"))

import exact_literals as X  # noqa: E402

COUPLINGS = """GC_1 = Coupling(name = 'GC_1',
                value = '-0.16666666666666666*(cw*complex(0,1)*g1SM)',
                order = {'QED':1})

GC_2 = Coupling(name = 'GC_2',
                value = '-0.3333333333333333*(c8l2H2D3x1*ee)/Lam**4 - (c8l2H2D3x2*ee)/(6.*Lam**4)',
                order = {'NP':2,'QED':1})

GC_3 = Coupling(name = 'GC_3',
                value = '0.5*ee + 2.5e-3*cw - 0.041666666666666664*sw',
                order = {'QED':1})
"""
PARAMETERS = """WT = Parameter(name = 'WT',
               nature = 'external',
               type = 'real',
               value = 1.50833649,
               texname = '0.1666666666666666',
               lhablock = 'DECAY',
               lhacode = [ 6 ])

x1 = Parameter(name = 'x1',
               nature = 'internal',
               type = 'real',
               value = '2**0.25*cw + 0.08333333333333333*sw',
               texname = 'x')
"""
LORENTZ = """FFV1 = Lorentz(name = 'FFV1',
               spins = [ 2, 2, 3 ],
               structure = '-0.3333333333333333*(P(-1,3)*Gamma(-1,2,1)) + P(3,1)/3.')
"""


def values(txt):
    import re
    return re.findall(r"(?:value|structure) = '([^']*)'", txt)


def run(argv):
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = X.main(argv)
    return code, buf.getvalue()


def main() -> int:
    ok = 0
    tmp = tempfile.mkdtemp()
    try:
        for name, txt in (("couplings.py", COUPLINGS), ("parameters.py", PARAMETERS), ("lorentz.py", LORENTZ)):
            open(os.path.join(tmp, name), "w").write(txt)
        code, out = run([tmp, "--check"])
        assert code == 1 and "couplings.py: 3 literal(s)" in out and "parameters.py: 1 literal(s)" in out, out
        ok += 1                                       # --check fails on the decimals
        code, out = run([tmp])
        assert code == 0, out
        c = open(os.path.join(tmp, "couplings.py")).read()
        p = open(os.path.join(tmp, "parameters.py")).read()
        lo = open(os.path.join(tmp, "lorentz.py")).read()
        assert "'-(1./6.)*(cw*complex(0,1)*g1SM)'" in c, c
        assert "-(1./3.)*(c8l2H2D3x1*ee)/Lam**4 - (c8l2H2D3x2*ee)/(6.*Lam**4)" in c, c
        assert "'0.5*ee + 2.5e-3*cw - (1./24.)*sw'" in c, c
        ok += 1                                       # the expected text, names and exact literals kept
        assert "value = 1.50833649," in p and "texname = '0.1666666666666666'" in p, p
        assert "'2**0.25*cw + (1./12.)*sw'" in p, p
        assert "structure = '-(1./3.)*(P(-1,3)*Gamma(-1,2,1)) + P(3,1)/3.'" in lo, lo
        ok += 1                                       # external defaults and texnames untouched
        env = {"cw": 0.8815, "sw": 0.4721, "g1SM": 0.3574, "ee": 0.3134, "Lam": 3000.0,
               "c8l2H2D3x1": 0.71, "c8l2H2D3x2": -1.3, "complex": complex, "P": lambda a, b: 1.7 * a + b,
               "Gamma": lambda a, b, c: 0.9 * a - b + c}
        for old, new in zip(values(COUPLINGS + PARAMETERS + LORENTZ), values(c + p + lo)):
            assert eval(old, dict(env)) == eval(new, dict(env)), (old, new)
        ok += 1                                       # the same doubles in Python, bit for bit
        before = c + p + lo
        code, out = run([tmp])
        assert code == 0 and before == (open(os.path.join(tmp, "couplings.py")).read()
                                        + open(os.path.join(tmp, "parameters.py")).read()
                                        + open(os.path.join(tmp, "lorentz.py")).read()), out
        code, out = run([tmp, "--check"])
        assert code == 0, out
        ok += 1                                       # idempotent, and --check passes after
        open(os.path.join(tmp, "parameters.py"), "a").write(
            "\ny1 = Parameter(name = 'y1',\n               nature = 'internal',\n"
            "               type = 'real',\n               value = '0.1234567891*cw',\n"
            "               texname = 'y')\n")
        code, out = run([tmp])
        assert code == 1 and "0.1234567891" in out and "value = '0.1234567891*cw'" in open(
            os.path.join(tmp, "parameters.py")).read(), out
        ok += 1                                       # no small fraction: left and reported
    finally:
        shutil.rmtree(tmp)
    shipped = sorted(os.path.dirname(f) for f in glob.glob(os.path.join(ROOT, "models", "*", "couplings.py")))
    for m in shipped:
        code, out = run([m, "--check"])
        assert code == 0, f"{os.path.relpath(m, ROOT)}:\n{out}"
    ok += 1                                           # every shipped model passes --check
    print(f"tests/test_exact_literals.py: {ok}/7 exact-literal checks pass "
          f"({len(shipped)} shipped models checked)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
