"""
validate/check_input_scheme.py  --  the corrected input relations must reduce to the SM.

Evaluates the derived formulae of gen/input_scheme_formulae.json numerically (Mathematica
syntax is arithmetic here, so ^ -> ** is the only translation) and checks the property that
is not negotiable: with every Wilson coefficient zero, gw, g1, vev and MW are the base.fr
values to machine precision.  Then checks that a nonzero coefficient actually moves them.
Needs neither Mathematica nor sympy.
"""
from __future__ import annotations
import json, math, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
aEWM1, Gf, MZ = 127.9, 1.16637e-5, 91.1876
aEW = 1/aEWM1


def sm():
    MW = math.sqrt(MZ**2/2 + math.sqrt(MZ**4/4 - math.pi/math.sqrt(2)*aEW/Gf*MZ**2))
    sw2 = 1 - (MW/MZ)**2; ee = math.sqrt(4*math.pi*aEW)
    return dict(gw=ee/math.sqrt(sw2), g1=ee/math.sqrt(1-sw2), vev=2*MW*math.sqrt(sw2)/ee, MW=MW)


def ev(expr, env):
    return eval(expr.replace("^", "**"), {"__builtins__": {}}, env)


def main() -> int:
    F = json.load(open(os.path.join(ROOT, "gen/input_scheme_formulae.json")))
    ref = sm()
    sw2 = (1 - math.sqrt(1 - 4*math.pi*aEW/(math.sqrt(2)*Gf*MZ**2)))/2
    env = dict(vevSM=1/math.sqrt(math.sqrt(2)*Gf), gwSM=math.sqrt(4*math.pi*aEW)/math.sqrt(sw2),
               g1SM=math.sqrt(4*math.pi*aEW)/math.sqrt(1-sw2))
    zero = {c: 0.0 for c in ["cHW", "cHB", "cHWB", "cHDD", "cHl3", "cll1", "c8W2H4x1", "c8W2H4x3",
                             "c8B2H4x1", "c8WBH4x1", "c8H6x1", "c8H6x2", "c8l2H4Dx2", "c8l2H4Dx4"]}
    def derived(wc, L6, L8):
        e = {**env, **wc, "L6": L6, "L8": L8}
        d = {k: env[f"{k}SM"]*(1 + ev(F[f"{k}1"], e) + ev(F[f"{k}2"], e)) for k in ("gw", "g1", "vev")}
        d["MW"] = math.sqrt(env["gwSM"]**2*env["vevSM"]**2/4*(1 + ev(F["MW21"], e) + ev(F["MW22"], e)))
        return d
    bad = False
    print("Standard Model limit (all coefficients zero):")
    got = derived(zero, 1e-6, 1e-12)
    for k in ("gw", "g1", "vev", "MW"):
        rel = abs(got[k]-ref[k])/ref[k]; bad |= rel > 1e-12
        print(f"  {k:3s} base.fr {ref[k]:.12f}   corrected {got[k]:.12f}   rel {rel:.1e}{'  MISMATCH' if rel > 1e-12 else ''}")
    # the canonical rotation pieces must vanish with the coefficients and move without them
    rot = [k for k in ("TZZ", "TZA", "TAZ", "TAA", "rW", "rh") if f"{k}1" in F]
    if rot:
        zero_r = {**zero, "cHbox": 0.0}
        e0 = {**env, **zero_r, "L6": 1e-6, "L8": 1e-12}
        worst = max(abs(ev(F[f"{k}{i}"], e0)) for k in rot for i in (1, 2))
        e1 = {**e0, "cHWB": 1.0}
        moved = abs(ev(F["TZA1"], e1)) + abs(ev(F["TAZ1"], e1))
        print(f"rotation: {len(rot)} field-rotation pieces, |value| at zero coefficients {worst:.1e}, Z-A mixing with cHWB=1 {moved:.3e}")
        if worst > 1e-15 or moved < 1e-12:
            print("  MISMATCH: rotation pieces do not vanish at the SM point, or do not respond to cHWB"); bad = True
    # step 4, the potential: SM limit, SMEFTsim's dMH2 at O(1/Lambda^2), and the tadpole
    MH = 125.0; vv = env["vevSM"]; lamSM = MH**2/(2*vv**2)
    def lam_mu(cH=0.0, cHbox=0.0, cHDD=0.0, c8H8=0.0, c8H6=0.0, L6=1e-6, L8=1e-12):
        Zh2 = 1 + cHDD*vv**2*L6/2 - 2*cHbox*vv**2*L6 + c8H6/4*vv**4*L8
        lam = (Zh2*MH**2/vv**2 + 3*cH*vv**2*L6 + 3*c8H8*vv**4*L8)/2
        return lam, lam*vv**2 - 0.75*cH*vv**4*L6 - 0.5*c8H8*vv**6*L8
    l0, m2 = lam_mu()
    okp = abs(l0 - lamSM)/lamSM < 1e-14 and abs(m2 - lamSM*vv**2)/(lamSM*vv**2) < 1e-14
    l1, _ = lam_mu(cH=0.4, cHbox=0.7, cHDD=0.5)
    target = -(vv**2*1e-6*(2*0.7 - 0.5/2 - 3*0.4/(2*lamSM)))
    okp &= abs((l1/lamSM - 1) - target) < 1e-12
    lam, mu2 = lam_mu(cH=0.4, cHbox=0.7, cHDD=0.5, c8H8=0.3, c8H6=0.2)
    Vp = -mu2*vv + lam*vv**3 - 0.75*0.4*1e-6*vv**5 - 0.5*0.3*1e-12*vv**7
    okp &= abs(Vp)/(lam*vv**3) < 1e-12
    print(f"potential: SM limit {'ok' if abs(l0-lamSM)/lamSM < 1e-14 else 'MISMATCH'}, dMH2 vs SMEFTsim diff {(l1/lamSM-1)-target:+.1e}, tadpole {abs(Vp)/(lam*vv**3):.1e}")
    bad |= not okp
    # step 5, the Yukawas: with y = sqrt2 m/v + c8 v^4 L8/4 the mass term of
    # -y v/sqrt2 + c8 v^5/(4 sqrt2) is exactly m for any c8
    mt, c8, L8 = 172.0, 0.8, 1e-12
    y = math.sqrt(2)*mt/vv + c8*vv**4*L8/4
    m_rec = y*vv/math.sqrt(2) - c8*vv**5*L8/(4*math.sqrt(2))
    print(f"yukawa: mass reconstructed with c8quH5 on {m_rec:.12f} vs input {mt}   rel {abs(m_rec-mt)/mt:.1e}")
    bad |= abs(m_rec - mt)/mt > 1e-14
    on = derived({**zero, "cHl3": 1.0}, 1e-6, 1e-12)
    if abs(on["vev"]-ref["vev"])/ref["vev"] < 1e-9:
        print("  WARNING: cHl3 = 1 did not move vev; the formulae are not wired in"); bad = True
    print("input scheme: " + ("FAIL" if bad else "PASS"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
