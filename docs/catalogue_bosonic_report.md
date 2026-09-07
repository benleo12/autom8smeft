# Bosonic dimension-8 operator catalogue (Murphy classes 1 to 8)

Source: `murphy_src/sections/dim8_classes_1_2_3_4.tex` and `dim8_classes_5_6_7_8_v2.tex` of arXiv:2005.00059 v6, read together with `conventions_v2.tex`, `operator_classification_v5.tex`, `results_v5.tex` and `pheno_v4.tex`. Output JSON: `docs/catalogue_bosonic.json` (89 entries, validated with `json.load`). Every `latex` string was checked mechanically against the source rows (regex extraction of all `$Q_...$ & $...$` lines in the two files) with zero mismatches and zero missing rows.

## Conventions carried over from Murphy

Field strengths are `X = {G^A, W^I, B}`, the dual is `Xtilde_{mu nu} = (1/2) eps_{mu nu rho sigma} X^{rho sigma}` with `eps_{0123} = +1`. SU(2) generators are `t^I = tau^I/2` with adjoint indices `I,J,K` and the SU(2) epsilon has `eps_{12} = +1`. The Higgs bilinears that appear are `(H^dag H)`, `(H^dag tau^I H)` and `(D_mu H^dag [tau^I] D_nu H)`, whose conjugate is the same object with `mu <-> nu`. No `+h.c.` marks appear anywhere in the two bosonic tables, all 89 terms are meant to be real (one operator per term, no flavor indices). Murphy's type label is the field content raised to multiplicities, e.g. `Q_{W^2BH^2}^{(2)}`. Classes 3 and 4 are labelled `Q_{H^6}^{(i)}` and `Q_{H^4}^{(i)}` in the table (no derivative count in the subscript) although the pheno section writes `c_{H^6D^2}^{(i)}` for the same coefficients.

## Per-table summary

| Table label | Caption | Classes | Rows extracted | Murphy N_type / N_term (Table `tab:summary`) |
|---|---|---|---|---|
| `tab:smeft8class_1_2_3_4` | "The dimension-eight operators in the SMEFT whose field content is either entirely gauge field strengths or Higgs boson fields." | 1, 2, 3, 4 | 49 | see below |
| `tab:smeft8class_5_6_7_8` | "Bosonic dimension-eight operators in the SMEFT containing both gauge field strengths and Higgs boson fields." | 5, 6, 7, 8 | 40 | see below |

The first table is built from two `adjustbox` blocks: the first holds two side-by-side minipages (headers `1: X^4, X^3 X'` with G^4, W^4, B^4, G^3B, and `1: X^2 X'^2` with G^2W^2, G^2B^2, W^2B^2), the second holds three minipages for classes 2, 3, 4. The second table holds minipages for classes 5 and 6 in one row and 7 and 8 in a second row. All minipages were read, nothing is multi-operator per row (each row is one label and one expression).

## Per-class counts

| Class | Name | Murphy N_type | Murphy N_term | Murphy N_op (Henning et al.) | Extracted | Type labels seen | CP-even / CP-odd (derived, see below) |
|---|---|---|---|---|---|---|---|
| 1 | X^4 | 7 | 43 | 43 | 43 | G^4 (9), W^4 (6), B^4 (3), G^3B (4), G^2W^2 (7), G^2B^2 (7), W^2B^2 (7) | 26 / 17 |
| 2 | H^8 | 1 | 1 | 1 | 1 | H^8 | 1 / 0 |
| 3 | H^6 D^2 | 1 | 2 | 2 | 2 | H^6 (labelled without D^2) | 2 / 0 |
| 4 | H^4 D^4 | 1 | 3 | 3 | 3 | H^4 (labelled without D^4) | 3 / 0 |
| 5 | X^3 H^2 | 3 | 6 | 6 | 6 | G^3H^2 (2), W^3H^2 (2), W^2BH^2 (2) | 3 / 3 |
| 6 | X^2 H^4 | 5 (stated) | 10 | 10 | 10 | G^2H^4 (2), W^2H^4 (4), WBH^4 (2), B^2H^4 (2) = 4 labels | 5 / 5 |
| 7 | X^2 H^2 D^2 | 4 | 18 | 18 | 18 | G^2H^2D^2 (3), W^2H^2D^2 (6), WBH^2D^2 (6), B^2H^2D^2 (3) | 11 / 7 |
| 8 | X H^4 D^2 | 2 | 6 | 6 | 6 | WH^4D^2 (4), BH^4D^2 (2) | 3 / 3 |
| total | | 24 (Murphy: 7+1+1+1+3+5+4+2 = 24) | 89 | 89 | 89 | | 54 / 35 |

Bosonic terms contain exactly one operator each for any n_g (Murphy Sec. 3 first paragraph), so `n_flavor_structures_ng3 = 1` for all entries and the n_g = 3 count is also 89. No baryon-number violation is possible in this sector.

## Hermiticity and the factors of i

Murphy inserts an explicit `i` exactly where the Lorentz-antisymmetric (anti-Hermitian) part of `(D^mu H^dag tau^I D^nu H)` is projected out by an antisymmetric tensor structure: `Q_{W^2H^2D^2}^{(4),(6)}` and `Q_{WBH^2D^2}^{(3),(5)}`. I verified the symmetry of every tensor structure in class 7 and the placement of the i's is consistent throughout class 7. In class 8 however all six operators contract `(D^mu H^dag [tau^I] D^nu H)` with an antisymmetric `X_{mu nu}` and carry no `i`, so as written they are anti-Hermitian. The JSON records `hermitian = false` for the six class-8 entries with an explanatory note. The collaborators' hand-typed `dim8_geosmeft3_latest.fr` inserts `I` for `c8HDHW`, `c8HDHW2`, `c8HDHB` and `c8HDHWt2`, but not for `c8HDHWt` and `c8HDHBt`, which looks internally inconsistent and is flagged below.

## CP assignments and how they were obtained

Murphy does not label CP for the bosonic operators (the only statement is the light-by-light discussion where the single-dual X^4 combinations are called the parity-violating ones). The `cp` field was therefore derived, uniformly for all 89 entries, as the product of C and P parities. P is `(-1)^(number of dual field strengths)`. C was evaluated field by field with `B -> -B`, `W^I -> -s_I W^I`, `G^A -> -s_A G^A`, `H -> H^*`, where `s = +1` for generators whose matrix is symmetric (tau^1, tau^3 and the symmetric Gell-Mann matrices) and `s = -1` for antisymmetric ones (tau^2 and lambda^{2,5,7}). Consequences used: `(H^dag tau^I H) -> +s_I (...)`, the mu-nu-symmetric part of `(D_mu H^dag tau^I D_nu H)` goes to `+s_I (...)` and its antisymmetric part to `-s_I (...)`, `eps^{IJK}` (and `f^{ABC}`) contributes `s_I s_J s_K = -1`, while `d^{ABC}` contributes `+1`. This reproduces the standard "dual tensor means CP-odd" rule for every operator built only from singlet contractions, and it reproduces CP-even for `Q_W`, `Q_G`, `Q_{HWB}` and the HISZ-type `i (D H^dag tau D H) W` structure, and CP-odd for their duals, which is the correct known behaviour.

The rule deviates from the naive dual-tensor heuristic for exactly five operators, all of which combine a C-odd SU(2) structure (an `eps^{IJK}` with a real symmetric Higgs bilinear, or a `[B, W^I]` commutator with the imaginary antisymmetric Higgs bilinear) with W and B fields:

| Operator | Duals | Naive label | Derived C | Derived P | Derived CP | Hand-typed FR placement |
|---|---|---|---|---|---|---|
| `Q_{W^2H^2D^2}^{(5)}` | 1 | odd | odd | odd | even | `c8DHWt3a` in `L8CPV` |
| `Q_{WBH^2D^2}^{(3)}` | 0 | even | odd | even | odd | `c8DHWB2` in `L8nonWh` (CP-even block) |
| `Q_{WBH^2D^2}^{(5)}` | 1 | odd | odd | odd | even | no one-to-one counterpart (`c8DHWtB2/3` use different combinations) |
| `Q_{WH^4D^2}^{(3)}` | 0 | even | odd | even | odd | `c8HDHW2` in `L8` (CP-even block) |
| `Q_{WH^4D^2}^{(4)}` | 1 | odd | odd | odd | even | `c8HDHWt2` in `L8CPV` |

Three independent cross-checks were done for these: the T-parity (antiunitary, `i -> -i`, `d_mu -> -d^mu`, `W^I_mu -> s_I W^{I mu}`) gives the same answer via CPT in every case, and explicit unitary-gauge expansions give for `Q_{WH^4D^2}^{(3)}` the Hermitian structure `i phi^3 d_nu phi [W^-_mu W^{+ mu nu} - W^+_mu W^{- mu nu}]` (antisymmetric under W^+ <-> W^-, CP-odd), for `Q_{WBH^2D^2}^{(3)}` the structure `phi d_nu phi Z_mu [F, Z]^{mu nu}` (three C-odd neutral bosons and no epsilon, the same pattern as the CP-odd neutral triple gauge couplings h_1, h_2), and for `Q_{W^2H^2D^2}^{(5)}` the structure `-i d_mu phi d_nu phi [{W^-, Wtilde^+} - {W^+, Wtilde^-}]^{mu nu}` (CP-even). The per-class even/odd totals are unchanged by these reassignments (3+3 in class 8, 11+7 in class 7) only if the swaps are taken in pairs, which they are. Nevertheless this contradicts the placement in the trusted hand-typed FeynRules files, so it is listed as an open question rather than asserted as settled.

## Notes on specific rows

`Q_{W^2BH^2}^{(2)}` is written as a sum of two terms. Murphy states (classification Sec., class 5) that the two terms are equivalent via `Xtilde_{mu rho} Y^{rho nu} = -X^{nu rho} Ytilde_{rho mu} - (1/2) X_{ab} Ytilde^{ab} delta_mu^nu` and that the two-term form is kept only for backward compatibility with Hays, Martin, Trott (1808.00442). The relative sign and factor between the one-term and two-term normalisations is not spelled out in the source.

`Q_{WBH^2D^2}^{(5),(6)}` are typeset with `\widetilde{W}_\nu^{^I \rho}` (a stray inner superscript brace). Copied verbatim into the JSON. The intended object is `Wtilde^{I rho}_nu`.

`Q_{W^2BH^2}^{(1)}` and `Q_{B^2H^2D^2}^{(1)}` contain thin-space spacing commands (`B_{\mu}^{\,\nu}`, `B_{\nu}^{\,\,\,\rho}`). Copied verbatim.

`Q_{WBH^4}^{(1)}` and `Q_{B^2H^4}^{(1)}` have a leading space inside the math delimiters in the source. Copied verbatim (leading space retained) so that the mechanical check passes.

For the `X^2 X'^2` sub-table the seven-term pattern per pair is: (1) product of singlet bilinears, (2) same with both duals, (3) crossed bilinears `(X Y)(X Y)`, (4) crossed with duals, (5) dual on the first field, (6) dual on the second field, (7) crossed with one dual. `G^3B` uses `d^{ABC}` (an `f^{ABC}` contraction vanishes by symmetry of `(G^B G^C)`), and there is no `W^3B` since `d^{IJK} = 0` for SU(2).

## Open questions

1. Class 8 Hermiticity. All six `Q_{XH^4D^2}` operators are anti-Hermitian as written in Murphy v6 (no `i`), while the analogous class-13 operators in the same paper carry an explicit `i`. The UFO build must either insert `i` (the HISZ convention and what the hand-typed file does for four of the six) or use imaginary coefficients. Decide and document. Also check why the hand-typed file omits `I` on `c8HDHWt` and `c8HDHBt` (the dual versions) while including it on `c8HDHW`, `c8HDHB`, `c8HDHW2`, `c8HDHWt2`.
2. CP labels of the five operators in the table above (`Q_{W^2H^2D^2}^{(5)}`, `Q_{WBH^2D^2}^{(3),(5)}`, `Q_{WH^4D^2}^{(3),(4)}`). The derivation here says the naive dual-tensor rule fails for them and the hand-typed file follows the naive rule. This should be settled by an explicit CP transformation in Mathematica or by checking against Hays, Martin, Trott and Remmen, Rodd before any "CP-even only" subset is built.
3. Murphy's summary table gives `N_type = 5` for class 6 but the table contains only four type labels (`G^2H^4`, `W^2H^4`, `WBH^4`, `B^2H^4`). Possibly `W^2H^4` is being counted as two types (the `(H^dag H)^2` and `(H^dag tau H)^2` structures), or it is a typo. Does not affect the term count (10).
4. Normalisation of `Q_{W^2BH^2}^{(2)}` relative to a single-term form (see notes above).
5. Naming aliases: `Q_{H^6}^{(i)}` vs `C_{H^6D^2}^{(i)}` and `Q_{H^4}^{(i)}` for the `H^4D^4` class. The JSON uses the table labels. Downstream code should accept both.
6. The hand-typed FR file implements the CP-odd `WBH^2D^2` operators as `c8DHWtB2` (no `I`, combination `B Wtilde + B Wtilde - Btilde W - Btilde W`) and `c8DHWtB3` (with `I`, antisymmetric combination), which is a different basis choice from Murphy's (5),(6). A translation is needed if the hand-typed coefficients are to be mapped onto Murphy's.
