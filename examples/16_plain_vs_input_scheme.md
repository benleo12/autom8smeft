# 16: plain model versus input-scheme model

`dim8_plain` puts the operators on the FeynRules Standard Model as it comes: inputs are
{alpha, MZ, GF} in name, but the operators' contributions to the gauge boson kinetic terms, the
photon-Z mixing, the W mass, the vev and the Yukawas are left in the Lagrangian. Two problems
follow. Predictions for the input observables themselves are shifted by the operators, so a
"measured" MZ or GF is no longer the one in the card. And the UFO format has no two-point
vertices: an operator such as `Q_{G^2H^4}^{(1)}`, whose vev shifts the gluon kinetic term, keeps
its three- and four-gluon pieces while the compensating two-point piece is dropped, and gauge
invariance is broken at O(v^4/Lambda^4). MadGraph's `check lorentz` shows it on the shipped
models themselves, with every coefficient at 0.7 and Lam at 1 TeV (`validate/ufo_on.py` makes
the coefficients-on copies): `dim8_plain` fails on `u u~ > g g` at 4.9e-4, `g g > g g` at 6.1e-5
and `g g > g g g` at 1.0e-4, and on `u d~ > w+ a` at 5.2e-4, the W analogue of the same shift
(`Q_{W^2H^4}^{(1)}` rescales the W kinetic term), and passes at 1e-15 as soon as the coefficients
are off or on processes that no kinetic shift reaches (`u u~ > a a`, `a z`, `h a`, `w+ w-`, `z h`
pass on the plain model too), while
`dim8_is` passes at 1e-14 or better with them on, on those processes and on seven electroweak
ones (`u u~ > a a`, `a z`, `h a`, `w+ w-`, `z h`, `u d~ > w+ a`, `e+ e- > a a`).

`dim8_is` corrects the input relations to O(1/Lambda^4) (SMEFTsim conventions, formulae in
the input-scheme section of the paper), rotates the fields to canonical kinetic terms, and removes the
gluon kinetic shift by a form factor, so that every gauge coupling in every vertex is the one
defined by the inputs. It passes the same checks at machine precision. It is the model to use;
`dim8_plain` is kept for cross-checks of operators that touch none of these terms (four-fermion,
X^4, X^3 H^2, ...), where the two agree.

The same process in both:

    import model dim8_plain
    generate p p > w+ w- NP^2==2
    ...
    import model dim8_is
    generate p p > w+ w- NP^2==2
    ...

with the same coefficients gives identical results for operators that do not enter the input
relations, and differs by the induced shifts (in the W mass, in the W couplings, in the vev) for
those that do, which is the whole point.
