(* ======================================================================================
   validate/smeftfr_pairs.m
   --------------------------------------------------------------------------------------
   SmeftFR v3.03 vs dim8auto: the BOSONIC dimension-eight operators of the Murphy basis
   (arXiv:2005.00059 v6), Murphy classes 1 to 8.

   Consumed by validate/fr_compare.wls, same five-column format as validate/v7_pairs.m:

       { handBlock, handWC, genBlock, genWC, normalisation }

   with the meaning

       handBlock|_{handWC}  ==  normalisation * genBlock|_{genWC -> handWC, Lam -> 1}

   Here the "hand" side is SmeftFR and the "gen" side is ours, so the fifth column is the
   factor k in

       O_SmeftFR  =  k * Q_ours .

   RUNNING IT
   ----------
   fr_compare.wls must be given three model files rather than two, because the SmeftFR
   blocks need validate/smeftfr_shim.fr on top of our base model:

       LoadModel["tests/gen_smoke/base.fr", "tests/gen_smoke/gen.fr",
                 "validate/smeftfr_shim.fr"];

   The shim defines SMEFT$WB, SMEFTGaugeRules, the Gl / Phi8 / Phi8bar aliases and the 89
   SmeftFR Wilson coefficients, and it Gets the eight SmeftFR bosonic Lagrangian files so
   that every LQ... block named below exists.  See the header of that file for the full
   convention audit.

   HOW THIS FILE WAS DERIVED
   -------------------------
   * SmeftFR side: external/smeftfr_3_03/lagrangian_dim8_fr_files/21_X4.fr, 22_phi8.fr,
     23_phi6D2.fr, 24_phi4D4.fr, 25_X3phi2.fr, 26_X2phi4.fr, 27_X2phi2D2.fr and
     28_Xphi4D2.fr, read term by term.  Every block name below is the literal LQ<name>
     defined in one of those files and every coefficient is SMEFT$WB <> <name> with
     SMEFT$WB = "c".
   * Our side: docs/block_index.json.  Every genBlock below was checked to exist there
     with exactly the quoted Murphy label in its "ops" list and exactly the quoted Wilson
     coefficient in its "wcs" list, and the emitted, fully SU(2)-expanded form in
     tests/gen_smoke/gen.fr was read back for at least one representative operator in
     every class to confirm the component decomposition.
   * Reference: both were compared against the Murphy tables themselves, in
     murphy_src/sections/dim8_classes_1_2_3_4.tex and
     murphy_src/sections/dim8_classes_5_6_7_8_v2.tex.

   WHY ALMOST EVERY NORMALISATION IS 1
   -----------------------------------
   * Both models declare Ta = PauliSigma/2 and both write Murphy's tau as an explicit
     "2 Ta", so there is no factor of 2 anywhere in classes 5 to 8.  Our generator emits
     the SU(2)-expanded components of tau, verified explicitly on Q_{WBH^4}^{(1)},
     Q_{W^2BH^2}^{(1)} and Q_{W^3H^2}^{(1)}.
   * Both write the dual as one half times a Levi-Civita with the two FREE indices first,
     so the epsilon sign convention cancels and no epsLorSign appears.
   * SmeftFR's coefficients absorb 1/Lambda^4 and ours carry it explicitly, but
     fr_compare.wls sets Lam -> 1 on the generated side, so the two agree.
   * The covariant derivative sign is not corrected here.  The SmeftFR sources contain no
     hard-coded signs, only DC and FS, so loading them into our model makes them adopt our
     FR$DSign = -1, which is Murphy's D = d + i g A.  Full discussion in the shim header.

   THE ONE NORMALISATION THAT IS NOT 1: class 8
   --------------------------------------------
   All six rows of Murphy's class 8 are ANTI-Hermitian exactly as typeset, because the
   Higgs bilinear D^mu H^dag tau^I D^nu H is contracted with an antisymmetric field
   strength.  Our catalogue records this in docs/catalogue.json as
   conjugacy = "antihermitian", and our generator therefore emits Q_ours = i times the
   operator as written.  SmeftFR transcribes the row literally, with no
   i.  Hence O_SmeftFR = Q_ours / i = -I * Q_ours for all six.  Cross-checked numerically
   on the h h W3 piece of Q_{WH^4D^2}^{(1)}: SmeftFR gives coefficient -1, we give -I.
   This is a genuine, benign disagreement about where the i lives, not about the operator.

   DELIBERATELY EXCLUDED
   ---------------------
   * Murphy class 3, H^6 D^2, BOTH operators, LQphi6Box and LQphi6D2.  This is a real
     basis disagreement and is the most interesting finding here.  Murphy's class 3 is
         Q_{H^6}^{(1)} = (H^dag H)^2 (D_mu H^dag D^mu H)
         Q_{H^6}^{(2)} = (H^dag H) (H^dag tau^I H) (D_mu H^dag tau^I D^mu H)
     which is what our generator emits, verified term by term against gen.fr.  SmeftFR
     instead implements
         LQphi6Box = (phi^dag phi)^2 Box(phi^dag phi)
         LQphi6D2  = (phi^dag phi) |phi^dag D_mu phi|^2
     the dim-8 analogues of the Warsaw Q_{H Box} and Q_{HD}.  The counts agree, 2 and 2,
     but the operators are different.  Using tau^I_ab tau^I_cd = 2 d_ad d_cb - d_ab d_cd
     one gets the exact algebraic relation
         LQphi6D2 = 1/2 Q_{H^6}^{(1)} + 1/2 Q_{H^6}^{(2)}
     which is a LINEAR COMBINATION of two of our blocks and therefore cannot be written as
     a single row of this file.  LQphi6Box is worse: it equals a combination of the two
     only after an integration by parts, so it is not even algebraically reducible to our
     blocks, and pairing it against either one would be a guaranteed false failure.
     Both are left out on purpose.  The two coefficients cphi6Box and cphi6D2 are still
     declared by the shim so this can be checked by hand.

   87 pairs.
   ====================================================================================== *)

{
  {"LQG3phi2n1",   cG3phi2n1,     "L8op587", c8G3H2x1,      1}   (* Q_{G^3H^2}^{(1)} *),
  {"LQG3phi2n2",   cG3phi2n2,     "L8op588", c8G3H2x2,      1}   (* Q_{G^3H^2}^{(2)} *),
  {"LQW3phi2n1",   cW3phi2n1,     "L8op589", c8W3H2x1,      1}   (* Q_{W^3H^2}^{(1)} *),
  {"LQW3phi2n2",   cW3phi2n2,     "L8op590", c8W3H2x2,      1}   (* Q_{W^3H^2}^{(2)} *),
  {"LQW2Bphi2n1",  cW2Bphi2n1,    "L8op591", c8W2BH2x1,     1}   (* Q_{W^2BH^2}^{(1)} *),
  {"LQW2Bphi2n2",  cW2Bphi2n2,    "L8op592", c8W2BH2x2,     1}   (* Q_{W^2BH^2}^{(2)}; two-term row, both terms present on both sides *)
}
