"""
tests/test_geo_tower.py  --  the tower check of the models of order N fails where it should.

Run:  python3 tests/test_geo_tower.py [-v]      (a Python with numpy; -v prints the report of each case)

validate/geo_tower_check.py compares each member of a tower with its operator of dimension eight, and the two
towers without one, those of Q_{WH^6D^2}^{(5),(6)}, with their member of dimension ten and with
Q_{WH^4D^2}^{(1),(2)} on W+ W- a, H Z a and H Z Z.  Its stand-in here is a UFO of the vertices W+ W- a, W+ W- Z,
H Z a and H Z Z with the coefficients c8WH4D2x1, x2, their members c10WH4D2x1 and c12WH4D2x1, and c10WH4D2x5, x6 and
c12WH4D2x5, x6, each vertex at the value the check expects, except W+ W- Z of x5 and x6, which has no partner,
and with c8l4H2x1Fx00 and the four-lepton coefficients c10l4H2x3Fx00 and c12l4H2x3Fx00 that are new at dimension
ten, which shift every vertex through G_F with the opposite sign.  The stand-in passes, and the check fails on

  a member of dimension ten without a partner of dimension eight that is twice its value on W+ W- a,
  the same member without its vertex H Z a,
  the member of dimension ten of x6 off by a tenth on H Z Z,
  a member of dimension twelve of that tower off by half on W+ W- Z, against the member of dimension ten,
  a member of an ordinary tower off on W+ W- Z, against its operator,
  a model without the operator Q_{WH^4D^2}^{(2)}, so that the member of dimension ten of x6 has nothing to
  be compared with,
  the four-lepton coefficient of dimension ten with the sign of Q_{l^4H^2}^{(1)}, or off on W+ W- Z,
  its member of dimension twelve off on W+ W- a, against the member of dimension ten,
  a model without Q_{l^4H^2}^{(1)}, so that it has nothing to be compared with,

passes on a model in which neither of the two four-lepton coefficients has a vertex (a UFO written without the
vertices of the base), and says that a model without any member has nothing to compare (exit 2).

The stand-in also has a tower whose vertex cancels exactly, as Q_{W^2H^4}^{(1)} does on every vertex without a
Higgs boson in the models: c8W2H4x1 and its members c10W2H4x1 and c12W2H4x1 each carry two couplings on
W+ W- Z that cancel in exact arithmetic, with a different rounding residue at each dimension, (0.1 + 0.2) - 0.3,
(0.7 + 0.2) - 0.9 and (0.4 + 0.2) - 0.6.  The stand-in passes with them, since a vertex within the rounding of its
terms is none, and the check fails when the member of dimension ten leaves a part in 10^9 of its terms.
"""
import contextlib
import io
import os
import sys
import tempfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
sys.path.insert(0, os.path.join(ROOT, "validate"))
sys.path.insert(0, os.path.join(ROOT, "tests"))
import geo_tower_check as T  # noqa: E402
from test_geo_export import FUNCTIONS, OBJECT_LIBRARY  # noqa: E402

PARTICLES = '''from object_library import Particle
W__plus__ = Particle(pdg_code = 24, name = 'W+', antiname = 'W-', spin = 3, color = 1, mass = 0, width = 0,
                     texname = 'W+', antitexname = 'W-', charge = 1)
W__minus__ = Particle(pdg_code = -24, name = 'W-', antiname = 'W+', spin = 3, color = 1, mass = 0, width = 0,
                      texname = 'W-', antitexname = 'W+', charge = -1)
a = Particle(pdg_code = 22, name = 'a', antiname = 'a', spin = 3, color = 1, mass = 0, width = 0,
             texname = 'a', antitexname = 'a', charge = 0)
Z = Particle(pdg_code = 23, name = 'Z', antiname = 'Z', spin = 3, color = 1, mass = 0, width = 0,
             texname = 'Z', antitexname = 'Z', charge = 0)
H = Particle(pdg_code = 25, name = 'H', antiname = 'H', spin = 1, color = 1, mass = 0, width = 0,
             texname = 'H', antitexname = 'H', charge = 0)
'''

LORENTZ = '''from object_library import Lorentz
VVV1 = Lorentz(name = 'VVV1', spins = [ 3, 3, 3 ],
               structure = 'P(3,1)*Metric(1,2) - P(3,2)*Metric(1,2) - P(2,1)*Metric(1,3) + P(2,3)*Metric(1,3) + P(1,2)*Metric(2,3) - P(1,3)*Metric(2,3)')
VVS1 = Lorentz(name = 'VVS1', spins = [ 3, 3, 1 ], structure = 'P(1,2)*P(2,1) - P(-1,1)*P(-1,2)*Metric(1,2)')
'''

# the vertices, each with its Lorentz structure, and the number each coefficient of the stand-in carries on it
VERTICES = {"WWa": ("W__minus__, W__plus__, a", "VVV1"), "WWZ": ("W__minus__, W__plus__, Z", "VVV1"),
            "HZa": ("Z, a, H", "VVS1"), "HZZ": ("Z, Z, H", "VVS1")}
K = {("x1", "WWa"): 1.3, ("x1", "WWZ"): 0.7, ("x1", "HZa"): 0.4, ("x1", "HZZ"): -0.8,
     ("x2", "WWa"): -0.6, ("x2", "WWZ"): 0.9, ("x2", "HZa"): 1.1, ("x2", "HZZ"): 0.3,
     # x5 and x6 share the vertices W+ W- a, H Z a and H Z Z of x1 and x2, not W+ W- Z
     ("x5", "WWa"): 1.3, ("x5", "WWZ"): 0.2, ("x5", "HZa"): 0.4, ("x5", "HZZ"): -0.8,
     ("x6", "WWa"): -0.6, ("x6", "WWZ"): -0.5, ("x6", "HZa"): 1.1, ("x6", "HZZ"): 0.3,
     # the shift of each vertex through G_F, which the four-lepton coefficients share
     ("gf", "WWa"): 0.5, ("gf", "WWZ"): -0.3, ("gf", "HZa"): 0.2, ("gf", "HZZ"): 0.6}
GF = ["c8l4H2x1Fx00", "c10l4H2x3Fx00", "c12l4H2x3Fx00"]
# the tower whose vertex W+ W- Z cancels exactly: the two numbers of its first coupling, and the one of the second
CANCEL = {"c8W2H4x1": ("0.1", "0.2", 0.3), "c10W2H4x1": ("0.7", "0.2", 0.9), "c12W2H4x1": ("0.4", "0.2", 0.6)}


def weight(c, v):
    """The number coefficient c carries on vertex v: that of its operator, and for the four-lepton coefficients
    the shift through G_F, with the opposite sign for the operator new at dimension ten."""
    if c in GF:
        return K[("gf", v)]*(-1 if "l4H2x3" in c else 1)
    return K[(c[-2:], v)]


def coefficients():
    """(name, dimension) of the coefficients of the stand-in."""
    return ([("c8WH4D2x1", 8), ("c8WH4D2x2", 8), ("c10WH4D2x1", 10), ("c12WH4D2x1", 12)]
            + [(f"c{d}WH4D2{x}", d) for d in (10, 12) for x in ("x5", "x6")]
            + [(c, int(c[1:c.index("l")])) for c in GF]
            + [(c, int(c[1:c.index("W")])) for c in CANCEL])


def write(d, scale=None, drop=(), names=None, kick=None):
    """The stand-in in directory d: scale[(coefficient, vertex)] multiplies a coupling, drop leaves vertices out,
    names restricts the coefficients, and kick[coefficient] is the part of its terms that the vertex of a
    cancelling coefficient leaves over."""
    scale, kick = scale or {}, kick or {}
    os.makedirs(d, exist_ok=True)
    cs = [c for c in coefficients() if names is None or c[0] in names]
    par = ["from object_library import all_parameters, Parameter",
           "Lam = Parameter(name = 'Lam', nature = 'external', type = 'real', value = 1000., texname = 'Lam', "
           "lhablock = 'DIM8', lhacode = [ 0 ])",
           "vevSM = Parameter(name = 'vevSM', nature = 'internal', type = 'real', value = '246.', texname = 'v')"]
    for p in (8, 10, 12):
        par.append(f"L{p} = Parameter(name = 'L{p}', nature = 'internal', type = 'real', value = 'Lam**(-{p - 4})', "
                   f"texname = 'L{p}')")
    for i, (c, dim) in enumerate(cs, 1):
        par.append(f"{c} = Parameter(name = '{c}', nature = 'external', type = 'real', value = 0, texname = '{c}', "
                   f"lhablock = 'DIM{dim}', lhacode = [ {i} ])")
    coup, vert = [], []
    for c, dim in cs:
        if c in CANCEL:
            a, b, ab = CANCEL[c]
            pre = f"complex(0,1)*{c}*L{dim}*vevSM**2*(vevSM**2/2)**{(dim - 8) // 2}"
            n = len(coup) + 1
            for m, value in ((n, f"{pre}*({a} + {b})"), (n + 1, f"-{pre}*{ab * (1 - kick.get(c, 0.0))!r}")):
                coup.append(f"GC_{m} = Coupling(name = 'GC_{m}', value = '{value}', order = {{'NP':{(dim - 4) // 2}}})\n")
            ps, lo = VERTICES["WWZ"]
            vert.append(f"V_{n} = Vertex(name = 'V_{n}', particles = [ {', '.join('P.' + q.strip() for q in ps.split(','))} ], "
                        f"color = [ '1' ], lorentz = [ L.{lo} ], couplings = {{(0,0):[C.GC_{n}, C.GC_{n + 1}]}})\n")
            continue
        for v in VERTICES:
            if (c, v) in drop:
                continue
            # at the vacuum a member of dimension d is (v^2/2)^((d-8)/2) times its operator, with L_d for L_8
            value = f"complex(0,1)*{c}*L{dim}*vevSM**2*(vevSM**2/2)**{(dim - 8) // 2}*{weight(c, v) * scale.get((c, v), 1)}"
            n = len(coup) + 1
            coup.append(f"GC_{n} = Coupling(name = 'GC_{n}', value = '{value}', order = {{'NP':{(dim - 4) // 2}}})\n")
            ps, lo = VERTICES[v]
            vert.append(f"V_{n} = Vertex(name = 'V_{n}', particles = [ {', '.join('P.' + q.strip() for q in ps.split(','))} ], "
                        f"color = [ '1' ], lorentz = [ L.{lo} ], couplings = {{(0,0):C.GC_{n}}})\n")
    files = {"object_library.py": OBJECT_LIBRARY, "function_library.py": FUNCTIONS, "particles.py": PARTICLES,
             "lorentz.py": LORENTZ, "parameters.py": "\n".join(par) + "\n", "__init__.py": "",
             "couplings.py": "from object_library import all_couplings, Coupling\n" + "".join(coup),
             "vertices.py": "from object_library import all_vertices, Vertex\nimport particles as P\nimport couplings as C\n"
                            "import lorentz as L\n" + "".join(vert)}
    for f, t in files.items():
        open(os.path.join(d, f), "w").write(t)
    return d


def main() -> int:
    verbose = "-v" in sys.argv
    cases = [("the stand-in passes", {}, 0),
             ("x5 at dimension ten twice its value on W+ W- a fails", {"scale": {("c10WH4D2x5", "WWa"): 2.0}}, 1),
             ("x5 at dimension ten without H Z a fails", {"drop": {("c10WH4D2x5", "HZa")}}, 1),
             ("x6 at dimension ten off on H Z Z fails", {"scale": {("c10WH4D2x6", "HZZ"): 0.9}}, 1),
             ("x5 at dimension twelve off on W+ W- Z fails", {"scale": {("c12WH4D2x5", "WWZ"): 1.5}}, 1),
             ("x1 at dimension ten off on W+ W- Z fails", {"scale": {("c10WH4D2x1", "WWZ"): 1.01}}, 1),
             ("x6 without Q_{WH^4D^2}^{(2)} in the model fails",
              {"names": {c for c, _ in coefficients()} - {"c8WH4D2x2"}}, 1),
             ("the four-lepton coefficient of dimension ten with the sign of Q_{l^4H^2}^{(1)} fails",
              {"scale": {("c10l4H2x3Fx00", v): -1.0 for v in VERTICES}}, 1),
             ("the four-lepton coefficient of dimension ten off on W+ W- Z fails", {"scale": {("c10l4H2x3Fx00", "WWZ"): 1.1}}, 1),
             ("its member of dimension twelve off on W+ W- a fails", {"scale": {("c12l4H2x3Fx00", "WWa"): 0.5}}, 1),
             ("the four-lepton coefficient without Q_{l^4H^2}^{(1)} in the model fails",
              {"names": {c for c, _ in coefficients()} - {"c8l4H2x1Fx00"}}, 1),
             ("a model in which the four-lepton coefficients have no vertex passes",
              {"drop": {(c, v) for c in GF for v in VERTICES}}, 0),
             ("a model without members has nothing to compare", {"names": {"c8WH4D2x1", "c8WH4D2x2"}}, 2),
             ("a member that leaves a part in 10^9 of a vertex that cancels for its operator fails",
              {"kick": {"c10W2H4x1": 1e-9}}, 1)]
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for k, (name, kw, want) in enumerate(cases):
            d = write(os.path.join(tmp, f"case{k}"), **kw)
            buf = io.StringIO()
            with contextlib.redirect_stdout(buf):
                rc = T.main([d])
            ok = rc == want
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {name} (exit {rc}, wanted {want})")
            if verbose or not ok:
                print("     " + buf.getvalue().strip().replace("\n", "\n     "))
    print(f"\n{len(cases) - bad}/{len(cases)} passed")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
