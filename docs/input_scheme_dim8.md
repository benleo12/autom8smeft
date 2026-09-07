# Dimension-eight operators and the {alpha, M_Z, G_F} input scheme

Status: drafted 2026-09-02 (analysis only, no Mathematica/FeynRules/MadGraph was run).
Sources read: `docs/murphy_parsed.json`, `docs/block_index.json`, `gen/dsl.py`,
`gen/emit_fr.py`, `tests/gen_smoke/base.fr`, `docs/hand_typed_operators.md`,
`the development log, not shipped`, `validate/conventions.md`, and the SmeftFR v3.03 source
(`external/smeftfr_3_03/smeftfr_3_03.tgz`, file `code/smeft_input_scheme.m`) used as an
independent cross-check of the bosonic sector.


> **Status 2026-09-02.** Steps 1 to 5 of the implementation plan below are implemented.
> The input relations (gen/derive_input_scheme.py) and the canonical field rotation
> (gen/derive_rotation.py) are derived exactly and expanded to O(1/Lambda^4), and both
> reproduce SMEFTsim at O(1/Lambda^2) to 1e-11; the potential and the Yukawas follow in
> closed form and reproduce SMEFTsim's dMH2 and SmeftFR's hlambda. gen/input_scheme.py emits
> them into the opt-in tests/gen_smoke/base_inputscheme.fr. Open question 1 (the f_WB sign)
> is settled by the SMEFTsim agreement; open question 2 (class-18 flavour contraction) was
> decided by the user in favour of delta_pr delta_st, so the four-lepton operators do not
> shift G_F. The FeynRules acceptance test (31 SM vertex contents, photon coupling ratio
> A l lbar / A u ubar = 3/2 with cHWB on, top mass fixed with c8quH5 on) runs on Perlmutter.

## 0. Scope, conventions and what "contributes" means

The Lagrangian is `L = L_SM + sum_i (C_i / Lam^4) Q_i`, with `Q_i` the Murphy v6 operators as
parsed into `docs/murphy_parsed.json` and `C_i` the dimensionless catalogue coefficient
`c8...` divided by `Lam^4`. Throughout, for each contributing coefficient I write the
dimensionless combination

    c_X  ==  C_X v^4 / Lam^4 ,

so every dim-8 shift quoted below is a *relative* shift of order `v^4/Lam^4`. There is no
dim-8 effect of lower order than that in the input sector: a dim-8 operator needs four
powers of `H` to reduce to a two-point function or a fermion-boson vertex, and each of
those is one power of `v`.

Conventions follow `validate/conventions.md` and Murphy Sec. 2: `D_mu = d_mu + i g1 y B_mu
+ i g2 t^I W^I_mu + i g3 T^A G^A_mu` (hence `FR$DSign = -1` in `base.fr`), `tau^I` are the
Pauli matrices, `t^I = tau^I/2`, and the Hermitian derivative is
`i H^dag Dlr_mu H = i H^dag (D_mu H) - i (D_mu H^dag) H`. `base.fr` puts the model in
unitary gauge with `Phi[1] -> 0`, `Phi[2] -> (vev + H)/Sqrt[2]`, so throughout I insert

    H = (0, (v+h)/Sqrt[2])^T ,  H^dag H = (v+h)^2/2 ,  H^dag tau^I H = -delta^{I3} (v+h)^2/2 .

The single most useful fact for the whole sweep is that **every covariant derivative
acting on H is at least linear in the fields**. At the vacuum, `D_mu H = (0, d_mu h/Sqrt2)
+ (gauge terms)`, with no field-independent piece. Consequently an operator containing `n`
derivatives distributed over its Higgs legs has a minimum field content of `n` plus
whatever the rest of the operator carries. That single counting rule kills most of the
basis: a two-point function needs exactly two fields, a fermion-boson vertex exactly
three.

The three inputs are extracted from three physical quantities, and only those three
quantities matter:

* `alpha` from the photon-fermion coupling in the Thomson limit `q^2 -> 0`,
* `M_Z` from the pole of the Z two-point function,
* `G_F` from the muon-decay amplitude at zero momentum transfer.

A dim-8 operator "contributes to the input scheme" only if it changes one of those three.
Operators that change, say, the `Z l l` coupling or `M_W` change *predictions*, not inputs,
and are outside the scope of this note.

## 1. Summary table

Only eight operators (plus one QCD analogue, plus two flavour-conditional ones) enter.

| Murphy label | catalogue WC | block | class | affects | induced term at the vev | order |
|---|---|---|---|---|---|---|
| `Q_{W^2H^4}^{(1)}` | `c8W2H4x1` | L8op595 | 6 | alpha, M_Z (and M_W prediction) | `(v^4/4) W^I_{mn}W^{I mn}` | `v^4/Lam^4` |
| `Q_{W^2H^4}^{(3)}` | `c8W2H4x3` | L8op597 | 6 | alpha, M_Z | `(v^4/4) W^3_{mn}W^{3 mn}` | `v^4/Lam^4` |
| `Q_{WBH^4}^{(1)}` | `c8WBH4x1` | L8op599 | 6 | alpha, M_Z | `-(v^4/4) W^3_{mn}B^{mn}` (kinetic mixing) | `v^4/Lam^4` |
| `Q_{B^2H^4}^{(1)}` | `c8B2H4x1` | L8op601 | 6 | alpha, M_Z | `(v^4/4) B_{mn}B^{mn}` | `v^4/Lam^4` |
| `Q_{H^6}^{(1)}` | `c8H6x1` | L8op469 | 3 | M_Z, G_F (absorbed into v), Z_h | `(v^4/4) x |D H|^2` and `(v^4/8)(dh)^2` | `v^4/Lam^4` |
| `Q_{H^6}^{(2)}` | `c8H6x2` | L8op470 | 3 | M_Z, G_F, Z_h | custodial-violating, `+` to M_Z, `-` to M_W | `v^4/Lam^4` |
| `Q_{l^2H^4D}^{(2)}` | `c8l2H4Dx2` | L8op31 | 13 | G_F | `-(g2 v^4/4)(lbar g^m tau^I l) W^I_m`, I=1,2 | `v^4/Lam^4` |
| `Q_{l^2H^4D}^{(4)}` | `c8l2H4Dx4` | L8op33 | 13 | G_F | same structure as above | `v^4/Lam^4` |
| `Q_{G^2H^4}^{(1)}` | `c8G2H4x1` | L8op593 | 6 | gluon kinetic form factor in LGauge (see 3(a), gluon) | `(v^4/4) G^A_{mn}G^{A mn}` | `v^4/Lam^4` |
| `Q_{l^4H^2}^{(1)}` | `c8l4H2x1` | L8op235 | 18 | G_F, **only in `general` flavour mode** | `(v^2/2)(lbar g l)(lbar g l)` | `v^4/Lam^4` rel. |
| `Q_{l^4H^2}^{(2)}` | `c8l4H2x2` | L8op236 | 18 | G_F, **only in `general` flavour mode** | `-(v^2/2)(lbar g l)(lbar g tau^3 l)` | `v^4/Lam^4` rel. |

Present but giving *no* linear effect, listed here because a reader will look for them:
`Q_{l^2H^4D}^{(3)}` (`c8l2H4Dx3`) shifts the `W l nu` vertex with a relative factor of `i`
and therefore does not interfere (Sec. 6), and the five CP-odd class-6 operators
(`c8G2H4x2`, `c8W2H4x2`, `c8W2H4x4`, `c8WBH4x2`, `c8B2H4x2`) reduce to a total derivative at
constant vev.

Counted per input: **alpha 4 operators**, **M_Z 6 operators**, **G_F 4 operators** (6 with
the flavour caveat), **alpha_s 1 operator**. Distinct electroweak operators: 8, or 10 with
the two class-18 four-lepton operators.

## 2. Definitions used below

Kinetic form factors, defined by

    L_2,kin = -(1/4)(1 - f_W)(W^1_{mn}W^{1 mn} + W^2_{mn}W^{2 mn})
              -(1/4)[(1 - f_W3) W^3_{mn}W^{3 mn} + (1 - f_B) B_{mn}B^{mn} - 2 f_WB W^3_{mn}B^{mn}]
              -(1/4)(1 - f_G) G^A_{mn}G^{A mn} ,

are, from class 6 alone,

    f_W  = c_{W^2H^4}^{(1)}
    f_W3 = c_{W^2H^4}^{(1)} + c_{W^2H^4}^{(3)}
    f_B  = c_{B^2H^4}^{(1)}
    f_WB = -(1/2) c_{WBH^4}^{(1)}
    f_G  = c_{G^2H^4}^{(1)}

Mass-term shifts, from class 3 alone,

    delta_mW = (c_{H^6}^{(1)} - c_{H^6}^{(2)}) / 4
    delta_mZ = (c_{H^6}^{(1)} + c_{H^6}^{(2)}) / 4

Charged-current vertex shift, from class 13,

    delta_gWl = (c_{l^2H^4D}^{(2)} + c_{l^2H^4D}^{(4)}) / 2

Higgs wavefunction, from class 3,

    Z_h = 1 + (c_{H^6}^{(1)} + c_{H^6}^{(2)}) / 4

with `s = s_W = g1/g_Z`, `c = c_W = g2/g_Z`, `g_Z = sqrt(g1^2+g2^2)`, `e = g1 g2 / g_Z`.

## 3. (a) Corrections to the gauge boson kinetic terms

**Class 6, `X^2 H^4`, is the only source.** The Higgs legs carry no derivatives, so the
four of them collapse straight onto `v^4` and leave the two field strengths as a genuine
two-point function. Using `H^dag H -> v^2/2` and `H^dag tau^I H -> -delta^{I3} v^2/2`:

    Q_{W^2H^4}^{(1)} = (H^dag H)^2 W^I W^I          ->  (v^4/4) W^I_{mn} W^{I mn}
    Q_{W^2H^4}^{(3)} = (H^dag t^I H)(H^dag t^J H) W^I W^J  ->  (v^4/4) W^3_{mn} W^{3 mn}
    Q_{WBH^4}^{(1)}  = (H^dag H)(H^dag t^I H) W^I B ->  -(v^4/4) W^3_{mn} B^{mn}
    Q_{B^2H^4}^{(1)} = (H^dag H)^2 B B              ->  (v^4/4) B_{mn} B^{mn}
    Q_{G^2H^4}^{(1)} = (H^dag H)^2 G G              ->  (v^4/4) G^A_{mn} G^{A mn}

Note that the basis is complete here for a good reason: `(H^dag tau^I H)(H^dag tau^I H) =
(H^dag H)^2` by the SU(2) completeness relation, which is why Murphy writes the third
operator with two free adjoint indices `I, J` and why there is no `(H^dag tau^I H)^2 B B`
entry. `Q_{WBH^4}^{(1)}` is the sole source of `B - W^3` kinetic mixing, the dim-8 analogue
of the Warsaw `Q_{HWB}`.

**The five CP-odd partners give nothing.** Each of `c8G2H4x2`, `c8W2H4x2`, `c8W2H4x4`,
`c8WBH4x2`, `c8B2H4x2` reduces at constant vev to `(v^4/4) Xtilde_{mn} Y^{mn}`, which is a
total derivative (the divergence of the Chern-Simons current) for both abelian and
non-abelian field strengths. They therefore drop out of the two-point functions entirely
and do not enter the canonical normalisation. They do of course survive in the `h V V` and
`V V V` vertices, where the `h`-dependence of `(v+h)^4` spoils the total-derivative
argument.

**Class 7 (`X^2 H^2 D^2`) contributes nothing, contrary to the expectation in the brief.**
Every class-7 operator carries the Higgs pair as `(D^mu H^dag D^nu H)` or
`(D^mu H^dag tau^I D_mu H)`. Since `D_mu H` has no field-independent piece, this bilinear is
at least quadratic in the fields, and multiplying by two field strengths gives a minimum
of four legs. Class 7 is a source of quartic gauge couplings and `h h V V` vertices, and
it has no two-point function at any order in `v`. This is worth stating explicitly because
it is an easy mistake to make: `(D^mu H^dag D_mu H)(W W)` *looks* like it should give
`(v^2/8)(g1 B - g2 W^3)^2 W W`, and it does, but that is a four-point vertex, not a
correction to the kinetic term.

**Class 8 (`X H^4 D^2`) contributes nothing.** The Higgs bilinear is again
`(D^mu H^dag tau^I D^nu H)`, minimum two legs, times one field strength, so the minimum is a
three-point `h V V` or `V V V` vertex. The Lorentz structure is antisymmetric in `mu nu`,
which additionally kills the `(d^mu h)(d^nu h)` piece.

**Class 5 (`X^3 H^2`) contributes nothing**, three field strengths being three legs at
minimum, and **class 1 (`X^4`) contributes nothing**, having no Higgs at all.

## 4. (b) Corrections to the gauge boson mass matrix

**Class 3, `H^6 D^2`, is the only direct source.** With `|D H|^2` evaluated at `h = 0`,

    D_mu H = ( i g2 (v/2) W^+_mu ,  (i/2)(v/Sqrt2)(g1 B_mu - g2 W^3_mu) )
    (D_mu H^dag D^mu H)|_{h=0} = (g2^2 v^2/4) W^+ W^- + (v^2/8)(g1 B - g2 W^3)^2
    (D_mu H^dag tau^3 D^mu H)|_{h=0} = (g2^2 v^2/4) W^+ W^- - (v^2/8)(g1 B - g2 W^3)^2

so that

    Q_{H^6}^{(1)} = (H^dag H)^2 (D_mu H^dag D^mu H)
        -> (v^4/4) [ (g2^2 v^2/4) W^+W^- + (v^2/8)(g1 B - g2 W^3)^2 ]

    Q_{H^6}^{(2)} = (H^dag H)(H^dag tau^I H)(D_mu H^dag tau^I D^mu H)
        -> -(v^4/4) [ (g2^2 v^2/4) W^+W^- - (v^2/8)(g1 B - g2 W^3)^2 ]

The first rescales the whole `|D H|^2` and is custodially symmetric. The second flips the
relative sign between the charged and neutral mass terms and is the dim-8 analogue of the
Warsaw `Q_{HD}`. Hence `delta_mW = (c1 - c2)/4` and `delta_mZ = (c1 + c2)/4` as defined
above. Both are absolute shifts `v^6 g^2 / Lam^4` and relative shifts `v^4/Lam^4`.

The `(g1 B - g2 W^3)` structure is untouched, so the mass matrix by itself never gives the
photon a mass, as required. What *does* rotate the photon direction is the kinetic mixing
`f_WB` of Sec. 3.

**Class 6 enters M_Z indirectly but unavoidably**, through the canonical normalisation.
The gauge-basis mass matrix is unchanged by class 6, but the physical eigenvalue is not.
Diagonalising, to first order in the small `f`'s, take `V = (W^3, B)^T = (1 + eps) Vhat`
with `eps = (1/2)(I - K)` and `K` the kinetic matrix. Writing

    g2hat = g2 (1 + f_W3/2) + g1 f_WB/2 ,    g1hat = g1 (1 + f_B/2) + g2 f_WB/2 ,

the massless eigenstate is `Ahat = (g1hat What^3 + g2hat Bhat)/sqrt(g1hat^2 + g2hat^2)` and

    M_Z^2 = (g_Z^2 v^2/4) [ 1 + delta_mZ + s^2 f_B + c^2 f_W3 + 2 s c f_WB ]
    M_W^2 = (g2^2 v^2/4) [ 1 + delta_mW + f_W ]

**Class 4 (`H^4 D^4`) contributes nothing, contrary to the expectation in the brief.** All
four Higgs legs carry a derivative, so the minimum field content is four. There is no
two-point function of any kind, in the gauge sector or the Higgs sector. Class 4 is a pure
source of `V V V V`, `h h V V` and `(dh)^4` vertices. This is confirmed independently by
SmeftFR v3, whose `Zh` and `Zg0` normalisation factors in `code/smeft_input_scheme.m`
involve `phi6Box` and `phi6D2` but never any of `phi4D4n1,2,3`.

**Class 7 contributes nothing to the mass matrix** for the same reason as in Sec. 3.

**Class 2 (`H^8`) contributes nothing to the mass matrix directly**, but it does shift the
scalar potential and therefore the location of the minimum. See Sec. 9 and the
implementation plan: as long as `muH` is re-solved so that the parameter `vev` remains the
stationary point (a tadpole condition), class 2 never touches `{alpha, M_Z, G_F}` and only
redefines `lam` and the `lam <-> M_H` relation.

### Cross-check against SmeftFR v3

SmeftFR v3.03 implements the complete *bosonic* dim-8 sector in the Murphy basis with
`phi^6 D^2` rebased to `{Q_{phi^6 Box}, Q_{phi^6 D^2}}`. Its `SMEFTGaugeInputsGF` builds

    Zgb^2  = 1 - 2 Lam V^2 C_{phiB}  - Lam^2 V^4 C_{B2phi4n1}
    Zgw^2  = 1 - 2 Lam V^2 C_{phiW}  - Lam^2 V^4 C_{W2phi4n1}
    Zgw3^2 = Zgw^2 - Lam^2 V^4 C_{W2phi4n3}
    Zg0^2  = 1 + (Lam/2) V^2 C_{phiD} + (Lam^2/4) V^4 C_{phi6D2}
    eps    = Lam V^2 (C_{phiWB} + (Lam V^2/2) C_{WBphi4n1}) / (Zgw3 Zgb)

with `Lam == 1/Lambda^2` in their notation. Identifying `1 - Zgb^2 = f_B`, `1 - Zgw^2 = f_W`,
`1 - Zgw3^2 = f_W3` and `Zg0^2 = 1 + delta_mZ`, every dim-8 coefficient above matches this
note exactly, including the relative factor of `1/2` between the dim-6 and dim-8 pieces of
the kinetic mixing. Their `phi6D2` operator is `(phi^dag phi)|phi^dag D_mu phi|^2`, which by
the SU(2) completeness relation is `(Q_{H^6}^{(1)} + Q_{H^6}^{(2)})/2`, so a pure
`C_{phi6D2}` direction corresponds to `C^{(1)} = C^{(2)} = C_{phi6D2}/2`, giving
`delta_mZ = c_{phi6D2}/4` and `delta_mW = 0`. That is exactly what SmeftFR encodes, and it
is the right answer since `|phi^dag D_mu phi|^2` only involves the lower doublet component
and so cannot touch the W mass.

The same identification also explains an apparent paradox worth recording: in Murphy's
basis `Q_{H^6}^{(1)}` shifts `M_W`, while in SmeftFR's basis no class-3 operator does.
Integrating by parts,

    Q_{H^6}^{(1)} = -(H^dag H)[d_mu (H^dag H)]^2 - (1/2)(H^dag H)^2 [ (D^2 H^dag) H + H^dag D^2 H ] + t.d.

and using the Higgs equation of motion the second bracket becomes pure potential and
Yukawa operators. Those shift the minimum of the potential, hence `v`, hence `M_W`. The two
bases agree once the input scheme is imposed. Concretely, `c_{H^6}^{(1)}` drops out of
`s_W^2`, out of `M_W/M_Z`, and out of every gauge-sector observable, being entirely
absorbed into the value of `v` extracted from `G_F`. It remains observable in the Higgs
sector through `Z_h` and through the `h`-dependence of `(v+h)^4`.

## 5. (c) Corrections to the Higgs kinetic term

**Class 3 only.** Keeping the `(d h)^2` piece,

    Q_{H^6}^{(1)} -> ((v+h)^4/4)(1/2)(d h)^2  ->  (v^4/8)(d h)^2
    Q_{H^6}^{(2)} -> +((v+h)^4/8)(d h)^2      ->  (v^4/8)(d h)^2

(the second gets two minus signs, one from `H^dag tau^3 H` and one from the `-|b|^2` in
`D H^dag tau^3 D H`, so it adds with the same sign as the first). Hence

    Z_h = 1 + (c_{H^6}^{(1)} + c_{H^6}^{(2)}) / 4 ,   h -> h / sqrt(Z_h) .

**Class 4 contributes nothing**, as argued in Sec. 4: four derivatives on four Higgs legs
give `(1/4)(d h)^4`, a four-point vertex, not a kinetic term. SmeftFR's `Zh` confirms this.

**Class 2 contributes nothing to the kinetic term**, only to the potential.

The Higgs kinetic term is *not* part of the `{alpha, M_Z, G_F}` extraction at tree level.
Muon decay has no Higgs exchange for massless leptons, the Z pole does not involve `h`, and
the Thomson limit does not either. `Z_h` is needed for a consistent model (it changes every
`h V V`, `h f f` and `h h h` coupling) but it does not feed back into the three inputs. It
is listed here because the brief asked for it and because the implementation must apply it.

## 6. (d) Corrections to muon decay and G_F

Write the muon-decay effective Lagrangian as
`L_eff = -(4 G_F/sqrt2)(nubar_mu g^a P_L mu)(ebar g_a P_L nu_e)`. In the SM,
`4 G_F/sqrt2 = g2^2/(2 M_W^2) = 2/v^2`.

### 6.1 The W-lepton vertex, class 13

The relevant vev insertions are

    (H^dag i Dlr^I_mu H)|_{h=0} = -(g2 v^2/2) W^I_mu + delta^{I3} (g1 v^2/2) B_mu
    (H^dag i Dlr_mu  H)|_{h=0} = -(v^2/2)(g1 B_mu - g2 W^3_mu) = +(v^2/2) g_Z Z_mu
    D_mu (H^dag tau^1 H)|_{h=0} = +(g2 v^2/2) W^2_mu ,  D_mu (H^dag tau^2 H)|_{h=0} = -(g2 v^2/2) W^1_mu

and the SM charged-current vertex from `i lbar g^mu D_mu l` is
`-(g2/2)(lbar g^mu tau^I l) W^I_mu` for `I = 1, 2`.

* `Q_{l^2H^4D}^{(1)}` and `Q_{e^2H^4D}` contain only the singlet Hermitian derivative, which
  at the vev is proportional to `Z` alone. They shift `Z l l` and `Z e e` and nothing else.
  Not an input.
* `Q_{l^2H^4D}^{(2)} = i (lbar g^mu tau^I l)[(H^dag Dlr^I_mu H)(H^dag H) + (H^dag Dlr_mu H)(H^dag tau^I H)]`.
  The second bracket forces `I = 3` and is neutral. The first gives, for `I = 1, 2`,
  `-(g2 v^4/4)(lbar g^mu tau^I l) W^I_mu`, i.e. exactly the SM structure with relative
  weight `v^4/(2 Lam^4)`. **Shifts G_F.**
* `Q_{l^2H^4D}^{(3)} = i eps^{IJK}(lbar g^mu tau^I l)(H^dag Dlr^J_mu H)(H^dag tau^K H)`.
  `H^dag tau^K H` forces `K = 3`, so only `J = 1, 2` survive and the result is
  `(g2 v^4/4)[(lbar g tau^1 l) W^2 - (lbar g tau^2 l) W^1]`. Using
  `tau^1 W^2 - tau^2 W^1 = i sqrt2 (tau^+ W^+ - tau^- W^-)` while the SM charged part is
  `-(g2/2) sqrt2 (tau^+ W^+ + tau^- W^-)`, the shift is **pure imaginary relative to the
  SM**, opposite in sign for `W^+` and `W^-`. With a real Wilson coefficient there is no
  linear interference in the muon-decay rate, so **`c8l2H4Dx3` does not shift G_F**. It is
  a CP-violating charged-current coupling.
* `Q_{l^2H^4D}^{(4)} = eps^{IJK}(lbar g^mu tau^I l)(H^dag tau^J H) D_mu(H^dag tau^K H)`.
  `H^dag tau^J H` forces `J = 3`. The two surviving terms are `(I,K) = (1,2)` with
  `eps^{132} = -1` and `(I,K) = (2,1)` with `eps^{231} = +1`, and the rotated
  `D_mu(H^dag tau^K H)` above conspires to give
  `-(g2 v^4/4)[(lbar g tau^1 l) W^1 + (lbar g tau^2 l) W^2]`, **the same SM-aligned
  structure as `Q^{(2)}`**. **Shifts G_F**, with the same relative weight `v^4/(2 Lam^4)`.

Hence only the combination `C^{(2)} + C^{(4)}` enters, and

    delta_gWl = (c_{l^2H^4D}^{(2)} + c_{l^2H^4D}^{(4)}) / 2 .

The corresponding quark operators `Q_{q^2H^4D}^{(2,3,4)}` and `Q_{udH^4D}` shift the `W q q'`
vertex and therefore the extracted CKM elements, not `G_F`.

### 6.2 Combining the vertex, the mass and the field normalisation

    4 G_F/sqrt2 = [g2^2 (1 + f_W)(1 + 2 delta_gWl)] / (2 M_W^2) + Delta_c
                = (2/v^2) [1 + 2 delta_gWl - delta_mW] + Delta_c

The W field normalisation `f_W` cancels exactly between the two vertices and the
propagator, as it must. This is a useful internal check on any implementation: **`f_W`
must not appear in the `G_F` relation, only in the `M_W` prediction and in `f_W3`.**

Defining `delta_G` by `4 G_F/sqrt2 = (2/v^2)(1 + delta_G)`,

    delta_G = 2 delta_gWl - delta_mW + (v^2/2) Delta_c .

### 6.3 Four-lepton contact operators, class 18, and the flavour caveat

The purely leptonic class-18 operators are `Q_{l^4H^2}^{(1,2)}`, `Q_{l^2e^2H^2}^{(1,2,3)}` and
`Q_{e^4H^2}`. Only the two `(Lbar L)(Lbar L)` ones can interfere with the SM `V-A` structure.
At the vev,

    Q_{l^4H^2}^{(1)} -> (v^2/2)(lbar_p g^a l_r)(lbar_s g_a l_t)
    Q_{l^4H^2}^{(2)} -> -(v^2/2)(lbar_p g^a l_r)(lbar_s g_a tau^3 l_t)

which is a `v^2/Lam^4` contact term, i.e. a relative shift of order `v^4/Lam^4` against the
SM `2/v^2`. The `(Lbar L)(Rbar R)` and `(Lbar R)(Lbar R)` leptonic operators produce
right-handed or scalar structures whose interference with the SM is suppressed by
`m_e/m_mu` (this is the Michel `eta` parameter), so they do not shift `G_F` at dim-8 linear
order.

**The flavour caveat is important and I flag it strongly.** The `mu -> e nubar_e nu_mu`
structure requires the flavour-off-diagonal assignment `C^{mu e e mu}`, exactly as for the
Warsaw `C_{ll}^{2112}`. Our emitter's `universal` mode (`gen/emit_fr.py:emit_term`, pairing
from `Operator.flavor_pairs` in `gen/dsl.py:589`) identifies generation indices *pairwise
in the order they appear*, i.e. `C^{prst} = C delta_{pr} delta_{st}`. With that contraction
both bilinears are flavour diagonal and SU(2) diagonal, the operator contains no
`(nubar_mu g nu_e)(ebar g mu)` structure, and

**in `universal` flavour mode the class-18 four-lepton operators give zero shift of G_F.**

The other U(3)^5-invariant contraction `C^{prst} = C delta_{pt} delta_{sr}` *does* give a
shift. The two are genuinely different operators (they are related by a Fierz rearrangement
that also rearranges the SU(2) indices, so `delta_{pt}delta_{sr}` equals
`(1/2)[singlet x singlet + triplet x triplet]` in weak isospin, not the singlet structure
alone). SmeftFR's own `G_F` shift uses `ll[2,1,1,2]`, the crossed structure, confirming that
this is the physically relevant flavour direction. Recommendation: extract `G_F` in
`general` flavour mode, or state the `universal`-mode convention explicitly in the model
documentation and accept that the four-lepton contribution is absent there.

### 6.4 What does not enter G_F

* **Class 21 (`psi^4 D^2`)**: the two derivatives turn into powers of the external momenta,
  so the contribution to the zero-momentum coefficient is `O(m_mu^2/Lam^4)` rather than
  `O(v^2/Lam^4)`, suppressed by `m_mu^2/v^2 ~ 2 x 10^-6` relative to the class-18 effect.
  Class 21 does not enter the input-scheme shift.
* **Class 20 (`psi^4 H D`)**: every operator pairs a vector current with a chirality-flipping
  scalar bilinear, and the derivative sits either on `H` (no field-independent piece, so no
  `v`-enhanced four-fermion term) or on a fermion (momentum-suppressed as in class 21).
  Both the chirality and the power counting kill it. Nothing.
* **Class 19 (`psi^4 X`)**: five-point, no tree contribution to `mu -> e nu nu`.
* **Class 11 (`psi^2 H^2 D^3`), contrary to the expectation in the brief**: this class *does*
  produce a genuine three-point `l l V` vertex, because `H^dag` collapses to `v` while
  `D_{(mu}D_{nu)}H` retains one gauge leg. But the vertex carries two momenta, of the form
  `v^2 q_{(mu} q_{nu)} p^nu gamma^mu`, and vanishes as `q -> 0`. In muon decay `q ~ m_mu`, so
  the effect is `O(v^2 m_mu^2/Lam^4)`, the same negligible order as class 21. Class 11 is
  important for high-energy Drell-Yan and VBF, and it is irrelevant to `G_F`.
* **Class 15 (`psi^2 X H^2 D`), contrary to the expectation in the brief**: both structures
  that appear, `D^mu(H^dag H)` and `(H^dag Dlr^{I mu} H)`, are at least linear in the fields,
  and they multiply a field strength which is also at least linear. Every class-15 operator
  therefore starts at a `psi psi V V` four-point vertex. There is **no** class-15 shift of
  any `psi psi V` coupling, so class 15 touches neither `G_F` nor `alpha`.

## 7. (e) The photon-fermion coupling

**No dim-8 operator shifts the photon-fermion coupling directly.** The cleanest argument is
the unbroken U(1)_em Ward identity: once the photon field is canonically normalised, its
coupling to a fermion of electric charge `Q = T^3 + Y` is exactly `ehat Q`, with `ehat` fixed
entirely by the gauge two-point functions. Everything else must either vanish at `q^2 = 0`
or be chirality-flipping.

Explicitly, working through the candidates:

* **Class 13** is the only class that produces a derivative-free `psi psi V` shift, and its
  singlet structure `(H^dag i Dlr_mu H) -> (v^2/2) g_Z Z_mu` and its triplet structure at
  `I = 3`, `-(g2 W^3 - g1 B) v^2/2 = -(v^2/2) g_Z Z`, are **both purely Z**. The photon simply
  does not appear. This is not an accident, it is the statement that `H^dag Dlr H` is a
  neutral current built from the broken generators.
* **Class 10 (`psi^2 X H^3`)** gives dipole operators `v^3 (lbar sigma^{mn} e) F_{mn}`. These
  are chirality-flipping and momentum-suppressed, contributing to `F_2` (the anomalous
  magnetic moment) and never to `F_1(0)`. No shift of `alpha`.
* **Classes 11, 15, 16** give momentum-dependent or two-boson vertices as discussed, all
  vanishing in the Thomson limit.
* **Classes 9 and 14** give `psi psi X X`, not `psi psi X`.

The whole effect on `alpha` therefore comes from the gauge kinetic terms of Sec. 3:

    ehat = e [ 1 + (c^2 f_B + s^2 f_W3 - 2 s c f_WB) / 2 ]

I derived this by substituting the kinetic-diagonalising rotation into `g2 T^3 W^3 + g1 Y B`
and checking that the coefficient of the photon is proportional to `T^3 + Y` with no
residual, which it is. Only `c8W2H4x1`, `c8W2H4x3`, `c8WBH4x1` and `c8B2H4x1` appear.

## 8. Class-by-class sweep, all 21 classes

| class | content | n ops | enters `{alpha, M_Z, G_F}`? | reason |
|---|---|---|---|---|
| 1 | `X^4` | 43 | no | no Higgs, four-gauge vertices only |
| 2 | `H^8` | 1 | no (but see note) | potential only, absorbed by re-solving `muH` for the tadpole |
| 3 | `H^6 D^2` | 2 | **yes, both** | gauge mass matrix and `Z_h` |
| 4 | `H^4 D^4` | 3 | no | all four `H` carry a derivative, minimum four legs |
| 5 | `X^3 H^2` | 6 | no | three field strengths, minimum three legs |
| 6 | `X^2 H^4` | 10 | **yes, 4 EW + 1 QCD** | CP-even ones give the gauge kinetic terms; the 5 CP-odd ones are total derivatives at constant vev |
| 7 | `X^2 H^2 D^2` | 18 | no | `D H` has no constant piece, minimum four legs |
| 8 | `X H^4 D^2` | 6 | no | minimum three legs, and antisymmetric in `mu nu` |
| 9 | `psi^2 X^2 H` | 48 | no | `psi psi X X`, never a two-point function or a `psi psi V` vertex |
| 10 | `psi^2 X H^3` | 11 | no | dipoles, chirality-flipping, vanish in the Thomson limit |
| 11 | `psi^2 H^2 D^3` | 15 | no | gives `psi psi V` but with two powers of `q`, `O(m_mu^2)` in `G_F`, zero at `q -> 0` for `alpha` |
| 12 | `psi^2 H^5` | 3 | no | Yukawa/mass relation only |
| 13 | `psi^2 H^4 D` | 12 | **yes, 2** (`x2`, `x4`) | `W l nu` vertex; `x3` is CP-odd and does not interfere; `x1`, `e2H4D` and the quark ones shift Z and CKM couplings, not inputs |
| 14 | `psi^2 X^2 D` | 57 | no | `psi psi X X`, no Higgs |
| 15 | `psi^2 X H^2 D` | 86 | no | every structure starts at `psi psi V V` |
| 16 | `psi^2 X H D^2` | 24 | no | `D H` has no constant piece, minimum `psi psi V V` |
| 17 | `psi^2 H^3 D^2` | 18 | no | `(D H^dag D H)` or `(H^dag D H)` both start at one leg, minimum four legs, so not even a fermion mass shift |
| 18 | `psi^4 H^2` | 65 | **conditionally, 2** | `Q_{l^4H^2}^{(1,2)}` shift `G_F` in `general` flavour mode, zero in our `universal` mode |
| 19 | `psi^4 X` | 169 | no | five-point |
| 20 | `psi^4 H D` | 84 | no | chirality-flipping and momentum- or `D H`-suppressed |
| 21 | `psi^4 D^2` | 53 | no | momentum-dependent, `O(m_mu^2/Lam^4)` |

## 9. Order counting: dim-6 squared plus dim-8 linear

A consistent `1/Lam^4` analysis writes every observable as

    O = O_SM + (1/Lam^2) O_6 + (1/Lam^4) [ O_8 + O_{6x6} ]

and the input-scheme shifts are no exception. Each shift is

    delta X = delta X^{(6)} / Lam^2 + [ delta X^{(8)} + delta X^{(6,6)} ] / Lam^4 .

Concretely, the `delta X^{(6,6)}` pieces come from three distinct places, and an
implementation that derives the shifts by hand can easily miss the last two:

1. **Genuine second-order terms in the exact diagonalisation.** The kinetic matrix
   `K = [[1-f_W3, f_WB],[f_WB, 1-f_B]]` and the mass matrix are exact. Diagonalising exactly
   and expanding at the end automatically produces terms such as `f_WB^2` and `f_B f_W3`,
   which at dim-6 order in the `f`'s are `(C_{HWB})^2 v^4/Lam^4` and so on.
2. **Second-order terms in inverting the input relations.** `1/(1+delta) = 1 - delta^{(6)} -
   delta^{(8)} - delta^{(6,6)} + (delta^{(6)})^2`. Solving `s_W^2 c_W^2 = pi alpha/(sqrt2 G_F M_Z^2)`
   for `s_W^2` and then for `M_W` introduces further cross terms.
3. **Non-interfering dim-6 structures squared.** `G_F` is extracted from a *rate*, so a
   dim-6 operator that does not interfere with the SM still contributes at `|C_6|^2/Lam^4`.
   SmeftFR's `c8` for the `G_F` scheme makes this explicit and is worth reproducing verbatim
   as the reference for our dim-6 sector when it is added:

       c6 = -2 ( C_ll[2,1,1,2] - C_phil3[1,1] - C_phil3[2,2] )
       c8 = C_ll[2,1,1,2]^2 - 2 C_ll[2,1,1,2](C_phil3[1,1] + C_phil3[2,2])
            + C_phil1[1,2] C_phil1[2,1] - C_phil3[1,2] C_phil3[2,1]
            + C_phil1[2,1] C_phil3[1,2] - C_phil1[1,2] C_phil3[2,1]
            + C_phil3[1,1]^2 + C_phil3[2,2]^2 + 4 C_phil3[1,1] C_phil3[2,2]
            + C_le[2,1,1,2]^2 / 4

   Note the last term. `C_le` produces a right-handed structure that does not interfere with
   the SM at all, yet its square is a legitimate `1/Lam^4` contribution to the muon
   lifetime. The same logic will apply to our dim-8 operators only at `1/Lam^8`, so it is
   purely a dim-6 concern, but it must be in the machinery from the start.

**What this means concretely for the implementation right now.** `tests/gen_smoke/base.fr`
ships no dimension-six operators at all (see its own header: "Nothing dimension-six ships
here"). In the model as it stands, every `delta X^{(6)}` is identically zero, so the
input-scheme shift reduces to the *linear dim-8* pieces derived in this note and nothing
else. The `(dim-6)^2` machinery becomes mandatory only when the Warsaw sector is added, and
the safe way to add it is not to type the cross terms by hand but to build the exact
kinetic and mass matrices symbolically, diagonalise exactly, and series-expand once at the
end, truncating at `1/Lam^4`. That is the geoSMEFT method and it is what SmeftFR's
`SMEFTExpOrder` does.

For the MG5 coupling-order bookkeeping, the plan already in `the development log, not shipped` is
consistent: dim-6 coefficients carry `InteractionOrder -> {NP,1}`, dim-8 carry `{NP,2}`,
`M$InteractionOrderLimit = {{NP,2}}`, so `NP^2==2` selects `dim-6^2 + dim-8 x SM`. A shift
parameter built as a product of two dim-6 coefficients must be declared `{NP,2}`.

## 10. Operators that vanish or fail to interfere

Recording these together, since a "zero" is as much a physics result as a "nonzero":

* `Q_{udWH^2}^{(1)}` and `Q_{udWH^2}^{(2)}` (`c8udWH2x1`, `c8udWH2x2`, class 15) vanish
  identically after SU(2) expansion. This is already asserted by `tests/test_emit.py:56-60`.
  Since class 15 contributes nothing to the input scheme in any case, this does not change
  the conclusions here.
* `Q_{eq^2uG}^{(2)}` (class 19, B-violating) gives zero vertices in the flavour-universal
  limit. Class 19 contributes nothing to the input scheme.
* The five CP-odd class-6 operators reduce to `Xtilde X` at constant vev, a total
  derivative, so they contribute nothing to the two-point functions. This is a genuine
  symmetry statement (the Chern-Simons current) rather than an accident of the vev.
* `Q_{l^2H^4D}^{(3)}` shifts the `W l nu` coupling with a relative factor of `i` and opposite
  signs for `W^+` and `W^-`. With a real Wilson coefficient the interference with the SM
  vanishes and `G_F` is untouched.
* In `universal` flavour mode all class-18 four-lepton operators give zero contribution to
  muon decay, as explained in Sec. 6.3.
* `c_{H^6}^{(1)}` is unobservable in the gauge sector: it drops out of `s_W^2` and of
  `M_W/M_Z`, being entirely absorbed into the value of `v` extracted from `G_F`. It is
  observable only through `Z_h` and the Higgs couplings.

## 11. Implementation plan

The steps below assume the emitter and `base.fr` stay as they are and the shifts are added
as a separate, generated block. Nothing here modifies existing files.

**Step 1. Add the shift parameters as `Internal`, `{NP,2}`.** Generate, into the parameter
section of the emitted model, one dimensionless parameter per form factor:

    dfW   = c8W2H4x1 vev^4/Lam^4
    dfW3  = (c8W2H4x1 + c8W2H4x3) vev^4/Lam^4
    dfB   = c8B2H4x1 vev^4/Lam^4
    dfWB  = -(1/2) c8WBH4x1 vev^4/Lam^4
    dfG   = c8G2H4x1 vev^4/Lam^4
    dmW   = (c8H6x1 - c8H6x2)/4 vev^4/Lam^4
    dmZ   = (c8H6x1 + c8H6x2)/4 vev^4/Lam^4
    dgWl  = (c8l2H4Dx2 + c8l2H4Dx4)/2 vev^4/Lam^4
    dZh   = (c8H6x1 + c8H6x2)/4 vev^4/Lam^4

each with `ParameterType -> Internal`, `InteractionOrder -> {NP,2}`. Keep them separate from
the SM parameters so that FeynRules never has to assign a single interaction order to a
quantity that mixes `NP^0` and `NP^2`. This is the trap that a naive `MW -> MW(1+dmW)`
substitution walks into.

**Step 2. Change the three input relations.** In the emitted parameter block, replace the
SM definitions by

    delta_G  = 2 dgWl - dmW                      (plus the class-18 term in general flavour)
    vev^2    = (1 + delta_G) / (Sqrt[2] Gf)
    delta_e  = (cw^2 dfB + sw^2 dfW3 - 2 sw cw dfWB)/2
    ee       = Sqrt[4 Pi aEW] (1 - delta_e)
    sw2 cw2  = (Pi aEW / (Sqrt[2] Gf MZ^2)) x
               (1 + delta_G + dmZ - 2 delta_e + sw^2 dfB + cw^2 dfW3 + 2 sw cw dfWB)
    MW^2     = cw^2 MZ^2 (1 + dmW + dfW - dmZ - sw^2 dfB - cw^2 dfW3 - 2 sw cw dfWB)

solving the quadratic `x(1-x) = sw2 cw2` for the low-`x` root as usual. Note that `vev` is
now defined from `Gf` directly rather than as `2 MW sw/ee`, which is the SM-only identity
currently in `base.fr` line 658. The right-hand sides that contain `sw`, `cw` inside the
shifts may be evaluated at their SM values, since the difference is `1/Lam^8`.

**Step 3. Canonically normalise the fields.** The gauge and Higgs rescalings of Secs. 3 and
5 multiply *every* vertex, not just the ones in the input relations. Two options:

  (a) Rescale in the Lagrangian. Define `W^{1,2} -> W^{1,2}(1 + dfW/2)`, the neutral
      two-by-two rotation of Sec. 4, and `h -> h(1 - dZh/2)`, and apply them to `LSM`
      before the dim-8 blocks are added. This is conceptually clean but changes the SM
      part of the model, which the project has so far kept pristine.

  (b) Add an explicit compensating Lagrangian. Since the rescalings are infinitesimal at
      `1/Lam^4`, `L_SM(phi + delta phi) = L_SM(phi) + delta phi . dL_SM/dphi`, and the
      correction term can be emitted as one more `{NP,2}` block. This keeps `base.fr`
      untouched and is easier to switch on and off for validation.

  Option (b) is recommended, with option (a) generated as a cross-check for V6.

**Step 4. Re-solve the tadpole.** With `Q_{H^8}`, `Q_{H^6}^{(1,2)}` (and later the Warsaw
`Q_H`) present, `muH = Sqrt[vev^2 lam]` no longer makes `vev` the stationary point of the
potential. Solve `dV/dh|_{h=0} = 0` for `muH` including the dim-8 potential terms, and
re-derive `lam` from `M_H^2 = Z_h^{-1} d^2V/dh^2|_{h=0}`. This does not touch
`{alpha, M_Z, G_F}` but it is required for the mass spectrum test V6 to pass.

**Step 5. Re-derive the Yukawas.** `yl, yu, yd` in `base.fr` are `Sqrt[2] m/vev` with no
SMEFT correction. Class 12 (`psi^2 H^5`) shifts the mass-Yukawa relation by
`v^4/Lam^4`, and `vev` itself is now shifted by Step 2. Both must be folded in before
`h f f` predictions are trusted. Not an input-scheme issue, listed for completeness.

**Step 6. Validation.** Three checks that are cheap and decisive:

  * `f_W` must cancel from `G_F`. Turn on only `c8W2H4x1`, compute the four-lepton effective
    coupling from the UFO, and confirm it is unchanged.
  * `c8H6x1` must cancel from `s_W^2` and from `M_W/M_Z`. Turn it on alone and confirm the
    only visible effects are in the Higgs sector.
  * Turn on `c8B2H4x1`, `c8W2H4x1`, `c8W2H4x3`, `c8WBH4x1`, `c8H6x1`, `c8H6x2` and compare the
    resulting `Zgb, Zgw, Zgw3, Zg0, eps` against SmeftFR v3 run on the same numerical point,
    using the basis map `C_{phi6D2} = 2 C^{(1)} = 2 C^{(2)}` for the class-3 direction. This
    is the single strongest available cross-check and it covers the entire bosonic half of
    this note. It slots naturally into V8 of the validation matrix.

## 12. Open questions

Flagged explicitly rather than guessed.

1. **Overall sign of the `f_WB` terms.** The relative sign between the kinetic mixing and
   the diagonal form factors depends on the sign convention of the covariant derivative
   (`FR$DSign = -1`), on the sign of `H^dag tau^3 H` at the vev, and on the definition
   `Z = c_W W^3 - s_W B`. I have kept all three self-consistent within this note and the
   result reproduces SmeftFR's structure, but I have not verified the *absolute* sign
   numerically. Check it with a single FeynRules run before trusting the `alpha` shift.

2. **The `universal` flavour convention for class 18.** I am confident that
   `C^{prst} = C delta_{pr} delta_{st}` gives zero contribution to muon decay and that
   `C^{prst} = C delta_{pt} delta_{sr}` does not, and that the emitter implements the
   former. I am *not* certain what the project intends the `universal` mode to mean
   physically, and this is a decision for the user, not for me. It affects whether two
   operators enter `G_F` or none do.

3. **CP assignment of `Q_{l^2H^4D}^{(3)}`.** The phase argument (relative factor `i`,
   opposite for `W^+` and `W^-`, hence no linear interference) is algebraically solid.
   Calling it "CP-odd" is my inference and is not taken from Murphy's tables, which the
   parser does not currently record CP information from. If a CP label is needed for V11,
   derive it independently.

4. **`Q_{l^2H^4D}^{(2)}` versus `Q_{l^2H^4D}^{(4)}`.** I find they shift the charged-current
   vertex with identical structure and identical weight, so only `C^{(2)} + C^{(4)}` is
   observable in `G_F`. That degeneracy is a slightly surprising result and deserves a
   FeynRules vertex-level confirmation before it is relied on.

5. **Momentum-dependent contributions to `G_F` from classes 11, 20 and 21.** I have argued
   they are suppressed by `m_mu^2/v^2`. That is certainly the right order, but the muon
   lifetime is measured to a part in `10^6`, so at some level of precision these are not
   strictly zero. I have not checked whether any of them produce a contribution that
   survives the phase-space integration with a coefficient large enough to matter for a
   tree-level UFO. For our purposes (a Monte Carlo model, not a global electroweak fit)
   dropping them is certainly safe.

6. **Class-3 basis translation.** The relation
   `Q_{phi^6 D^2}^{SmeftFR} = (Q_{H^6}^{(1)} + Q_{H^6}^{(2)})/2` follows from the SU(2)
   completeness relation and I have checked it reproduces SmeftFR's `Zg0`. The second
   direction, the map of `Q_{phi^6 Box}` onto Murphy's basis, involves an integration by
   parts and the Higgs equation of motion and I have *not* worked it out completely. It is
   needed only if the SmeftFR comparison of Step 6 is to be done in both directions.

7. **How FeynRules assigns a coupling order to a vertex whose coefficient is a sum of an
   `NP^0` and an `NP^2` piece.** I have recommended keeping the shift parameters separate
   for exactly this reason, but I have not verified how FeynRules 2.3.49 behaves if they
   are not kept separate. Worth a five-minute test before committing to a structure.

## Gluon kinetic term (added 2026-09-06)

The gluon does not mix, so `f_G` needs no field rotation, but it does need to be removed from
the Lagrangian: FeynRules' UFO export drops two-point vertices while keeping the three- and
four-gluon pieces of the same `(v^4/4) G^A_{mn} G^{A mn}` term, and MadGraph's Lorentz check
(the Ward identity for external gluons) then fails at O(v^4/Lambda^4) on g g > g g,
u u~ > g g and g g > g g g with `c8G2H4x1` alone switched on, and passes at 1e-15 with the
nine X^4 operators or with G^3H^2. The variant therefore carries

    LGauge  ⊃  -(1/4) (1 + d8fG) G^A_{mn} G^{A mn},    d8fG = c8G2H4x1 vev^4/Lam^4 ,

so that the merged Lagrangian (rotated SM + operator blocks) is exactly `-(1/4) G G` with
`gs = Sqrt[4 Pi aS]` in every gluon vertex (quarks and ghosts included): alpha_s is the coupling
of the canonical field and `Q_{G^2H^4}^{(1)}` survives only through its Higgs-dependent pieces.
`vev` (= vevSM) is the symbol the cached operator vertices carry, since the cache is built from
base.fr, so the cancellation is symbol for symbol; a first version used `vevT^4` and left an
untruncated `(v^4/Lam^4)^2` mismatch whenever the `H^6` partners shift the vev (Lorentz-check
residual of 1e-6 to 1e-5 with every coefficient on, none family by family). Earlier versions
of this note said "alpha_s only" and the parameter was defined but unused.

Also added the same day: `gwSM`, `g1SM` carry `InteractionOrder -> {QED,1}` and `vevSM`, `vevT`
`{QED,-1}`; without them FeynRules gave every SM coupling built from them the placeholder order
`{'1': 1}` and MadGraph refused both input-scheme UFOs ("Some couplings have '1' order").
