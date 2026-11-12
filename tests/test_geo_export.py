"""
tests/test_geo_export.py  --  the export checks of the models of order N fail where they should.

Run:  python3 tests/test_geo_export.py [-v]      (a Python with numpy; -v prints what each failing case reports)

validate/geo_export_check.py gates the release of a model of order N (gen/towers.py).  Each of its checks is run
here on a small stand-in for a model of order 3, written as a UFO in a temporary directory: an electron and a
Z, the scale Lam, one coefficient of each of dimensions six, eight and ten with L6, L8, L10, and
input shifts gw1, gw2, gw3 of orders one to three, with the e e Z vertex at every order through NP = 3 and an
e e Z Z vertex at NP <= 2.  The stand-in passes, and each check fails on the defect it is there for:

1. orders: a coupling of order two declared NP 1, a coefficient of dimension ten with the scale of dimension
   eight, a name that is not defined, a vertex of three legs at NP 4 = N + 1, and the expansion order of NP
   below N,
2. four or more legs: the e e Z Z vertex given its NP = 3 piece (the untruncated vertex), and the same piece
   declared NP 2,
3. blocks: a second scale Lam6, a member missing from DIM10, a block DIM12 above 2N + 4, a card entry used twice,
4. included once, by block: a coefficient that reaches a vertex of at most three legs from a release block and
   from a geo block (a release block not dropped below four legs), a block written in two shards, and a record
   cut off before its end line,
5. included once, against a reference: the e e Z vertex doubled at NP = 2, once in its coupling and once as a
   second vertex of the same particles, against the stand-in as it is,
6. at most three legs, order by order, against the blocks written without the truncation (the e e Z vertex of
   the stand-in with a piece at NP = 2 that cancels between two couplings of different QED orders, which the
   truncation removes and the plain cut keeps): the piece at NP = 3 taken off the model, off by a percent, or
   there twice, and a pair in which neither holds a piece at NP = 3, which would be an empty test.
"""
import copy
import io
import os
import shutil
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "validate"))
import geo_export_check as X  # noqa: E402

N = 3

OBJECT_LIBRARY = '''
class UFOBaseClass(object):
    def __init__(self, *args, **options):
        for i, name in enumerate(self.require_args):
            setattr(self, name, args[i] if i < len(args) else options[name])
        for k, v in options.items():
            setattr(self, k, v)
all_particles, all_parameters, all_couplings, all_lorentz, all_vertices, all_orders = [], [], [], [], [], []
class Particle(UFOBaseClass):
    require_args = ['pdg_code', 'name', 'antiname', 'spin', 'color', 'mass', 'width', 'texname', 'antitexname', 'charge']
    def __init__(self, *a, **o):
        UFOBaseClass.__init__(self, *a, **o); all_particles.append(self)
class Parameter(UFOBaseClass):
    require_args = ['name', 'nature', 'type', 'value', 'texname']
    def __init__(self, *a, **o):
        UFOBaseClass.__init__(self, *a, **o); all_parameters.append(self)
class Coupling(UFOBaseClass):
    require_args = ['name', 'value', 'order']
    def __init__(self, *a, **o):
        UFOBaseClass.__init__(self, *a, **o); all_couplings.append(self)
class Lorentz(UFOBaseClass):
    require_args = ['name', 'spins', 'structure']
    def __init__(self, *a, **o):
        UFOBaseClass.__init__(self, *a, **o); all_lorentz.append(self)
class Vertex(UFOBaseClass):
    require_args = ['name', 'particles', 'color', 'lorentz', 'couplings']
    def __init__(self, *a, **o):
        UFOBaseClass.__init__(self, *a, **o); all_vertices.append(self)
class CouplingOrder(object):
    def __init__(self, name, expansion_order, hierarchy):
        self.name, self.expansion_order, self.hierarchy = name, expansion_order, hierarchy
        all_orders.append(self)
class Function(object):
    def __init__(self, name, arguments, expression):
        self.name, self.arguments, self.expression = name, arguments, expression
        self.f = eval('lambda ' + ','.join(arguments) + ': ' + expression, {'cmath': __import__('cmath')})
    def __call__(self, *a):
        return self.f(*a)
'''

FUNCTIONS = '''from object_library import Function
complexconjugate = Function(name = 'complexconjugate', arguments = ('z',), expression = 'z.conjugate()')
'''

PARTICLES = '''from object_library import Particle
e__minus__ = Particle(pdg_code = 11, name = 'e-', antiname = 'e+', spin = 2, color = 1, mass = 0, width = 0,
                      texname = 'e-', antitexname = 'e+', charge = -1)
e__plus__ = Particle(pdg_code = -11, name = 'e+', antiname = 'e-', spin = 2, color = 1, mass = 0, width = 0,
                     texname = 'e+', antitexname = 'e-', charge = 1)
Z = Particle(pdg_code = 23, name = 'Z', antiname = 'Z', spin = 3, color = 1, mass = 0, width = 0,
             texname = 'Z', antitexname = 'Z', charge = 0)
'''

LORENTZ = '''from object_library import Lorentz
FFV1 = Lorentz(name = 'FFV1', spins = [ 2, 2, 3 ], structure = 'Gamma(3,2,1)')
FFVV1 = Lorentz(name = 'FFVV1', spins = [ 2, 2, 3, 3 ], structure = 'Gamma(3,2,-1)*Gamma(4,-1,1)')
'''


def parameters(extra=()):
    """parameters.py of the stand-in: (name, nature, value, block, code)."""
    rows = [("Lam", "external", "1000.", "DIM8", 0), ("aEWM1", "external", "127.9", "SMINPUTS", 1),
            ("cHl3", "external", "0", "DIM6", 1), ("c8l2H4Dx2", "external", "0", "DIM8", 1),
            ("c10l2H4Dx2", "external", "0", "DIM10", 1),
            ("ee", "internal", "2*cmath.sqrt(1/aEWM1)*cmath.sqrt(cmath.pi)", None, None),
            ("vevSM", "internal", "246.", None, None),
            ("L6", "internal", "Lam**(-2)", None, None), ("L8", "internal", "Lam**(-4)", None, None),
            ("L10", "internal", "Lam**(-6)", None, None),
            ("gw1", "internal", "cHl3*vevSM**2*L6", None, None),
            ("gw2", "internal", "c8l2H4Dx2*vevSM**4*L8/2 - gw1**2", None, None),
            ("gw3", "internal", "c10l2H4Dx2*vevSM**6*L10/4 + gw1*gw2 + gw1**3/3", None, None)] + list(extra)
    out = ["from object_library import all_parameters, Parameter"]
    for name, nature, value, block, code in rows:
        if nature == "external":
            out.append(f"{name} = Parameter(name = '{name}', nature = 'external', type = 'real', value = {value}, "
                       f"texname = '{name}', lhablock = '{block}', lhacode = [ {code} ])")
        else:
            out.append(f"{name} = Parameter(name = '{name}', nature = 'internal', type = 'real', value = '{value}', "
                       f"texname = '{name}')")
    return "\n".join(out) + "\n"


# (name, value, orders): the e e Z vertex at NP = 0 ... 3, the e e Z Z vertex at NP = 0 ... 2
COUPLINGS = [("GC_1", "-(ee*complex(0,1))/2.", {"QED": 1}),
             ("GC_2", "-(ee*complex(0,1)*gw1)/2.", {"NP": 1, "QED": 1}),
             ("GC_3", "-(ee*complex(0,1)*gw2)/2.", {"NP": 2, "QED": 1}),
             ("GC_4", "-(ee*complex(0,1)*gw3)/2.", {"NP": 3, "QED": 1}),
             ("GC_5", "ee**2*complex(0,1)", {"QED": 2}),
             ("GC_6", "ee**2*complex(0,1)*(gw2 + 2*gw1**2)", {"NP": 2, "QED": 2})]
VERTICES = [("V_1", "e__plus__, e__minus__, Z", "FFV1", "GC_1"), ("V_2", "e__plus__, e__minus__, Z", "FFV1", "GC_2"),
            ("V_3", "e__plus__, e__minus__, Z", "FFV1", "GC_3"), ("V_4", "e__plus__, e__minus__, Z", "FFV1", "GC_4"),
            ("V_5", "e__plus__, e__minus__, Z, Z", "FFVV1", "GC_5"),
            ("V_6", "e__plus__, e__minus__, Z, Z", "FFVV1", "GC_6")]


def write(d, couplings=COUPLINGS, vertices=VERTICES, extra=(), expansion=N):
    os.makedirs(d, exist_ok=True)
    files = {"object_library.py": OBJECT_LIBRARY, "function_library.py": FUNCTIONS, "particles.py": PARTICLES,
             "lorentz.py": LORENTZ, "parameters.py": parameters(extra), "__init__.py": "",
             "coupling_orders.py": "from object_library import CouplingOrder\n"
                                   f"NP = CouplingOrder(name = 'NP',\n                   expansion_order = {expansion},\n"
                                   "                   hierarchy = 1)\n",
             "couplings.py": "from object_library import Coupling\n\n" + "".join(
                 f"{n} = Coupling(name = '{n}',\n                value = {v!r},\n"
                 f"                order = {{{','.join(f'{k!r}:{x}' for k, x in o.items())}}})\n\n" for n, v, o in couplings),
             "vertices.py": "from object_library import Vertex\nimport particles as P\nimport couplings as C\nimport lorentz as L\n\n" + "".join(
                 f"{n} = Vertex(name = '{n}',\n             particles = [ {', '.join('P.' + x.strip() for x in ps.split(','))} ],\n"
                 f"             color = [ '1' ],\n             lorentz = [ L.{lo} ],\n"
                 f"             couplings = {{(0,0):C.{c}}})\n\n" for n, ps, lo, c in vertices)}
    for f, t in files.items():
        open(os.path.join(d, f), "w").write(t)
    return d


EXPECTED = {10: {"c10l2H4Dx2"}}
cases = []


def check(name, problems, want_fail):
    cases.append((name, bool(problems) == want_fail, problems))


def ended(prov):
    """records as the writer leaves them, each with its end line"""
    for d in prov.values():
        d["end"] = len(d["loaded"])
    return prov


def read_check(p, blocks):
    """check 4 on the record files in p, a reader that stops on them counting as a problem"""
    try:
        return X.check_provenance(X.read_provenance([p]), blocks, out=lambda *a, **k: None)
    except SystemExit as e:
        return [f"read_provenance stopped: {e}"]


def swap(rows, name, value=None, order=None):
    out = []
    for n, v, o in rows:
        if n == name:
            v, o = (value if value is not None else v), (order if order is not None else o)
        out.append((n, v, o))
    return out


def run(tmp, tag, fn, **kw):
    m = X.Model(write(os.path.join(tmp, tag), **kw))
    return fn(m)


def main() -> int:
    quiet = lambda *a, **k: None
    orders = lambda m: X.check_orders(m, N, out=quiet)
    blocks = lambda m: X.check_blocks(m, N, EXPECTED, out=quiet)
    with tempfile.TemporaryDirectory() as tmp:
        check("1, 2. the stand-in passes the orders", run(tmp, "clean", orders), False)
        check("3. the stand-in passes the blocks", run(tmp, "clean_b", blocks), False)
        check("1. a coupling of order two declared NP 1 fails",
              run(tmp, "mislabel", orders, couplings=swap(COUPLINGS, "GC_3", order={"NP": 1, "QED": 1})), True)
        check("1. a coefficient of dimension ten with L8 fails",
              run(tmp, "scale", orders, couplings=swap(COUPLINGS, "GC_4", value="-(ee*complex(0,1)*c10l2H4Dx2*L8)/2.")), True)
        check("1. a name that is not defined fails",
              run(tmp, "undefined", orders, couplings=swap(COUPLINGS, "GC_3", value="-(ee*complex(0,1)*gw2*foo)/2.")), True)
        check("1. a vertex of three legs above N fails",
              run(tmp, "aboveN", orders, couplings=COUPLINGS + [("GC_7", "ee*gw2**2", {"NP": 4, "QED": 1})],
                  vertices=VERTICES + [("V_7", "e__plus__, e__minus__, Z", "FFV1", "GC_7")]), True)
        check("1. an NP expansion order below N fails", run(tmp, "expansion", orders, expansion=2), True)
        check("1. ... and passes as a raw model",
              X.check_orders(X.Model(os.path.join(tmp, "expansion")), N, raw=True, out=quiet), False)
        untrunc = COUPLINGS + [("GC_7", "ee**2*complex(0,1)*gw3", {"NP": 3, "QED": 2})]
        check("2. a vertex of four legs with its NP 3 piece (untruncated) fails",
              run(tmp, "untrunc", orders, couplings=untrunc,
                  vertices=VERTICES + [("V_7", "e__plus__, e__minus__, Z, Z", "FFVV1", "GC_7")]), True)
        check("2. ... and with that piece declared NP 2",
              run(tmp, "untrunc2", orders, couplings=swap(COUPLINGS, "GC_6", value="ee**2*complex(0,1)*(gw2 + gw3)")), True)
        check("3. a second scale fails",
              run(tmp, "lam6", blocks, extra=[("Lam6", "external", "1000.", "DIM6", 0)]), True)
        check("3. a member missing from DIM10 fails",
              X.check_blocks(X.Model(os.path.join(tmp, "clean_b")), N, {10: {"c10l2H4Dx2", "c10H6x1"}}, out=quiet), True)
        check("3. a block above 2N + 4 fails",
              run(tmp, "dim12", lambda m: X.check_blocks(m, 2, {}, out=quiet)), True)
        check("3. a card entry used twice fails",
              run(tmp, "twice", blocks, extra=[("c8H6x1", "external", "0", "DIM8", 1)]), True)
        # 4: provenance as the writer records it
        good = {"0.prov": {"loaded": {"G8op12": (3, 0), "L8op40": (0, 5), "G6cl7": (2, 0)},
                           "rows": [("G8op12", "Z e ebar", "c8l2H4Dx2"), ("G6cl7", "Z e ebar", "cHl3")]},
                "1.prov": {"loaded": {"L8op400": (0, 9)}, "rows": []}}
        model_blocks = ["G8op12", "L8op40", "G6cl7", "L8op400"]
        check("4. the provenance of the stand-in passes", X.check_provenance(ended(good), model_blocks, out=quiet), False)
        bad = copy.deepcopy(good)
        bad["0.prov"]["loaded"]["L8op40"] = (3, 5)
        bad["0.prov"]["rows"].append(("L8op40", "Z e ebar", "c8l2H4Dx2"))
        check("4. a release block not dropped below four legs fails", X.check_provenance(ended(bad), model_blocks, out=quiet), True)
        bad = copy.deepcopy(good)
        bad["1.prov"]["loaded"]["L8op40"] = (0, 5)
        check("4. a block written in two shards fails", X.check_provenance(ended(bad), model_blocks, out=quiet), True)
        check("4. a block missing from the shards fails", X.check_provenance(good, model_blocks + ["L8op41"], out=quiet), True)
        # the file format, through read_provenance
        p = os.path.join(tmp, "prov")
        os.makedirs(p)
        with open(os.path.join(p, "0.prov"), "w") as f:
            f.write("G8op12\tloaded\t3\t0\nG8op12\tvertex\tZ e ebar\tc8l2H4Dx2\nL8op40\tloaded\t3\t5\n"
                    "L8op40\tvertex\tZ e ebar\tc8l2H4Dx2\n#end\t2\n")
        check("4. ... read from the files the writer leaves", read_check(p, None), True)
        # a record cut off at a line boundary while the writer wrote the vertices of its last block
        whole = "G8op12\tloaded\t3\t0\nG8op12\tvertex\tZ e ebar\tc8l2H4Dx2\nG6cl7\tloaded\t2\t0\n"
        p2 = os.path.join(tmp, "prov2")
        os.makedirs(p2)
        open(os.path.join(p2, "0.prov"), "w").write(whole + "G6cl7\tvertex\tZ e ebar\tcHl3\n#end\t2\n")
        check("4. a whole record read from its file passes", read_check(p2, ["G8op12", "G6cl7"]), False)
        open(os.path.join(p2, "0.prov"), "w").write(whole)
        check("4. a record cut off before its end line fails", read_check(p2, ["G8op12", "G6cl7"]), True)
        # 5: against the stand-in itself
        ref = X.Model(os.path.join(tmp, "clean"))
        check("5. the stand-in passes against itself", X.check_reference(X.Model(os.path.join(tmp, "clean")), ref, out=quiet), False)
        check("5. a coupling doubled at NP 2 fails",
              run(tmp, "double", lambda m: X.check_reference(m, ref, out=quiet),
                  couplings=swap(COUPLINGS, "GC_3", value="2*(-(ee*complex(0,1)*gw2)/2.)")), True)
        check("5. a vertex of the same particles twice at NP 2 fails",
              run(tmp, "double2", lambda m: X.check_reference(m, ref, out=quiet),
                  vertices=VERTICES + [("V_7", "e__plus__, e__minus__, Z", "FFV1", "GC_3")]), True)
        check("5. ... but not above NP 2, which the reference does not hold",
              run(tmp, "double3", lambda m: X.check_reference(m, ref, out=quiet),
                  vertices=VERTICES + [("V_7", "e__plus__, e__minus__, Z", "FFV1", "GC_4")]), False)
        # 6: the vertices of at most three legs as the plain cut of the writer leaves them
        three = [v for v in VERTICES if v[1].count(",") == 2]
        cancel = [("GC_8", "ee*gw2", {"NP": 2, "QED": 1}), ("GC_9", "-ee*gw2", {"NP": 2, "QED": 3})]
        low = X.Model(write(os.path.join(tmp, "low"), couplings=COUPLINGS + cancel,
                            vertices=three + [("V_8", "e__plus__, e__minus__, Z", "FFV1", "GC_8"),
                                              ("V_9", "e__plus__, e__minus__, Z", "FFV1", "GC_9")]))
        six = lambda m: X.check_low(m, low, N, out=quiet)
        check("6. the stand-in passes against its blocks without the truncation",
              six(X.Model(os.path.join(tmp, "clean"))), False)
        check("6. the piece at NP 3 taken off the model fails",
              run(tmp, "six_off", six, vertices=[v for v in VERTICES if v[0] != "V_4"]), True)
        check("6. the piece at NP 3 off by a percent fails",
              run(tmp, "six_pc", six, couplings=swap(COUPLINGS, "GC_4", value="1.01*(-(ee*complex(0,1)*gw3)/2.)")), True)
        check("6. the piece at NP 3 there twice fails",
              run(tmp, "six_twice", six, vertices=VERTICES + [("V_7", "e__plus__, e__minus__, Z", "FFV1", "GC_4")]), True)
        low2 = X.Model(write(os.path.join(tmp, "low2"), vertices=[v for v in three if v[0] != "V_4"]))
        check("6. a pair without a piece at NP 3 fails, as an empty test",
              run(tmp, "six_empty", lambda m: X.check_low(m, low2, N, out=quiet),
                  vertices=[v for v in VERTICES if v[0] != "V_4"]), True)
    nbad = [c for c in cases if not c[1]]
    for name, ok, problems in cases:
        print(("ok   " if ok else "FAIL ") + name + ("" if ok else f"\n       {problems[:3]}"))
        if ok and problems and "-v" in sys.argv:
            print(f"       {problems[0]}")
    print(f"\n{len(cases) - len(nbad)}/{len(cases)} passed")
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
