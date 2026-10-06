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
  (* ---- class 1, X^4 and X^3 X-prime  --  43 pairs, all normalisation 1 ---- *)
  {"LQG4n1",       cG4n1,         "L8op425", c8G4x1,        1},    (* Q_{G^4}^{(1)} *)
  {"LQG4n2",       cG4n2,         "L8op426", c8G4x2,        1},    (* Q_{G^4}^{(2)} *)
  {"LQG4n3",       cG4n3,         "L8op427", c8G4x3,        1},    (* Q_{G^4}^{(3)} *)
  {"LQG4n4",       cG4n4,         "L8op428", c8G4x4,        1},    (* Q_{G^4}^{(4)} *)
  {"LQG4n5",       cG4n5,         "L8op429", c8G4x5,        1},    (* Q_{G^4}^{(5)} *)
  {"LQG4n6",       cG4n6,         "L8op430", c8G4x6,        1},    (* Q_{G^4}^{(6)} *)
  {"LQG4n7",       cG4n7,         "L8op431", c8G4x7,        1},    (* Q_{G^4}^{(7)} *)
  {"LQG4n8",       cG4n8,         "L8op432", c8G4x8,        1},    (* Q_{G^4}^{(8)} *)
  {"LQG4n9",       cG4n9,         "L8op433", c8G4x9,        1},    (* Q_{G^4}^{(9)} *)
  {"LQW4n1",       cW4n1,         "L8op434", c8W4x1,        1},    (* Q_{W^4}^{(1)} *)
  {"LQW4n2",       cW4n2,         "L8op435", c8W4x2,        1},    (* Q_{W^4}^{(2)} *)
  {"LQW4n3",       cW4n3,         "L8op436", c8W4x3,        1},    (* Q_{W^4}^{(3)} *)
  {"LQW4n4",       cW4n4,         "L8op437", c8W4x4,        1},    (* Q_{W^4}^{(4)} *)
  {"LQW4n5",       cW4n5,         "L8op438", c8W4x5,        1},    (* Q_{W^4}^{(5)} *)
  {"LQW4n6",       cW4n6,         "L8op439", c8W4x6,        1},    (* Q_{W^4}^{(6)} *)
  {"LQB4n1",       cB4n1,         "L8op440", c8B4x1,        1},    (* Q_{B^4}^{(1)} *)
  {"LQB4n2",       cB4n2,         "L8op441", c8B4x2,        1},    (* Q_{B^4}^{(2)} *)
  {"LQB4n3",       cB4n3,         "L8op442", c8B4x3,        1},    (* Q_{B^4}^{(3)} *)
  {"LQG3Bn1",      cG3Bn1,        "L8op443", c8G3Bx1,       1},    (* Q_{G^3B}^{(1)} *)
  {"LQG3Bn2",      cG3Bn2,        "L8op444", c8G3Bx2,       1},    (* Q_{G^3B}^{(2)} *)
  {"LQG3Bn3",      cG3Bn3,        "L8op445", c8G3Bx3,       1},    (* Q_{G^3B}^{(3)} *)
  {"LQG3Bn4",      cG3Bn4,        "L8op446", c8G3Bx4,       1},    (* Q_{G^3B}^{(4)} *)
  {"LQG2W2n1",     cG2W2n1,       "L8op447", c8G2W2x1,      1},    (* Q_{G^2W^2}^{(1)} *)
  {"LQG2W2n2",     cG2W2n2,       "L8op448", c8G2W2x2,      1},    (* Q_{G^2W^2}^{(2)} *)
  {"LQG2W2n3",     cG2W2n3,       "L8op449", c8G2W2x3,      1},    (* Q_{G^2W^2}^{(3)} *)
  {"LQG2W2n4",     cG2W2n4,       "L8op450", c8G2W2x4,      1},    (* Q_{G^2W^2}^{(4)} *)
  {"LQG2W2n5",     cG2W2n5,       "L8op451", c8G2W2x5,      1},    (* Q_{G^2W^2}^{(5)} *)
  {"LQG2W2n6",     cG2W2n6,       "L8op452", c8G2W2x6,      1},    (* Q_{G^2W^2}^{(6)} *)
  {"LQG2W2n7",     cG2W2n7,       "L8op453", c8G2W2x7,      1},    (* Q_{G^2W^2}^{(7)} *)
  {"LQG2B2n1",     cG2B2n1,       "L8op454", c8G2B2x1,      1},    (* Q_{G^2B^2}^{(1)} *)
  {"LQG2B2n2",     cG2B2n2,       "L8op455", c8G2B2x2,      1},    (* Q_{G^2B^2}^{(2)} *)
  {"LQG2B2n3",     cG2B2n3,       "L8op456", c8G2B2x3,      1},    (* Q_{G^2B^2}^{(3)} *)
  {"LQG2B2n4",     cG2B2n4,       "L8op457", c8G2B2x4,      1},    (* Q_{G^2B^2}^{(4)} *)
  {"LQG2B2n5",     cG2B2n5,       "L8op458", c8G2B2x5,      1},    (* Q_{G^2B^2}^{(5)} *)
  {"LQG2B2n6",     cG2B2n6,       "L8op459", c8G2B2x6,      1},    (* Q_{G^2B^2}^{(6)} *)
  {"LQG2B2n7",     cG2B2n7,       "L8op460", c8G2B2x7,      1},    (* Q_{G^2B^2}^{(7)} *)
  {"LQW2B2n1",     cW2B2n1,       "L8op461", c8W2B2x1,      1},    (* Q_{W^2B^2}^{(1)} *)
  {"LQW2B2n2",     cW2B2n2,       "L8op462", c8W2B2x2,      1},    (* Q_{W^2B^2}^{(2)} *)
  {"LQW2B2n3",     cW2B2n3,       "L8op463", c8W2B2x3,      1},    (* Q_{W^2B^2}^{(3)} *)
  {"LQW2B2n4",     cW2B2n4,       "L8op464", c8W2B2x4,      1},    (* Q_{W^2B^2}^{(4)} *)
  {"LQW2B2n5",     cW2B2n5,       "L8op465", c8W2B2x5,      1},    (* Q_{W^2B^2}^{(5)} *)
  {"LQW2B2n6",     cW2B2n6,       "L8op466", c8W2B2x6,      1},    (* Q_{W^2B^2}^{(6)} *)
  {"LQW2B2n7",     cW2B2n7,       "L8op467", c8W2B2x7,      1},    (* Q_{W^2B^2}^{(7)} *)

  (* ---- class 2, H^8  --  1 pair ---- *)
  {"LQphi8",       cphi8,         "L8op468", c8H8,          1},    (* Q_{H^8} *)

  (* ---- class 4, H^4 D^4  --  3 pairs, all normalisation 1 ---- *)
  {"LQphi4D4n1",   cphi4D4n1,     "L8op471", c8H4x1,        1},    (* Q_{H^4}^{(1)} *)
  {"LQphi4D4n2",   cphi4D4n2,     "L8op472", c8H4x2,        1},    (* Q_{H^4}^{(2)} *)
  {"LQphi4D4n3",   cphi4D4n3,     "L8op473", c8H4x3,        1},    (* Q_{H^4}^{(3)} *)

  (* ---- class 5, X^3 H^2  --  6 pairs, all normalisation 1 ---- *)
  {"LQG3phi2n1",   cG3phi2n1,     "L8op587", c8G3H2x1,      1},    (* Q_{G^3H^2}^{(1)} *)
  {"LQG3phi2n2",   cG3phi2n2,     "L8op588", c8G3H2x2,      1},    (* Q_{G^3H^2}^{(2)} *)
  {"LQW3phi2n1",   cW3phi2n1,     "L8op589", c8W3H2x1,      1},    (* Q_{W^3H^2}^{(1)} *)
  {"LQW3phi2n2",   cW3phi2n2,     "L8op590", c8W3H2x2,      1},    (* Q_{W^3H^2}^{(2)} *)
  {"LQW2Bphi2n1",  cW2Bphi2n1,    "L8op591", c8W2BH2x1,     1},    (* Q_{W^2BH^2}^{(1)} *)
  {"LQW2Bphi2n2",  cW2Bphi2n2,    "L8op592", c8W2BH2x2,     1},    (* Q_{W^2BH^2}^{(2)}; two-term row, both terms present on both sides *)

  (* ---- class 6, X^2 H^4  --  10 pairs, all normalisation 1 ---- *)
  {"LQG2phi4n1",   cG2phi4n1,     "L8op593", c8G2H4x1,      1},    (* Q_{G^2H^4}^{(1)} *)
  {"LQG2phi4n2",   cG2phi4n2,     "L8op594", c8G2H4x2,      1},    (* Q_{G^2H^4}^{(2)} *)
  {"LQW2phi4n1",   cW2phi4n1,     "L8op595", c8W2H4x1,      1},    (* Q_{W^2H^4}^{(1)} *)
  {"LQW2phi4n2",   cW2phi4n2,     "L8op596", c8W2H4x2,      1},    (* Q_{W^2H^4}^{(2)} *)
  {"LQW2phi4n3",   cW2phi4n3,     "L8op597", c8W2H4x3,      1},    (* Q_{W^2H^4}^{(3)} *)
  {"LQW2phi4n4",   cW2phi4n4,     "L8op598", c8W2H4x4,      1},    (* Q_{W^2H^4}^{(4)} *)
  {"LQWBphi4n1",   cWBphi4n1,     "L8op599", c8WBH4x1,      1},    (* Q_{WBH^4}^{(1)} *)
  {"LQWBphi4n2",   cWBphi4n2,     "L8op600", c8WBH4x2,      1},    (* Q_{WBH^4}^{(2)} *)
  {"LQB2phi4n1",   cB2phi4n1,     "L8op601", c8B2H4x1,      1},    (* Q_{B^2H^4}^{(1)} *)
  {"LQB2phi4n2",   cB2phi4n2,     "L8op602", c8B2H4x2,      1},    (* Q_{B^2H^4}^{(2)} *)

  (* ---- class 7, X^2 H^2 D^2  --  18 pairs, all normalisation 1 ---- *)
  {"LQG2phi2D2n1", cG2phi2D2n1,   "L8op603", c8G2H2D2x1,    1},    (* Q_{G^2H^2D^2}^{(1)} *)
  {"LQG2phi2D2n2", cG2phi2D2n2,   "L8op604", c8G2H2D2x2,    1},    (* Q_{G^2H^2D^2}^{(2)} *)
  {"LQG2phi2D2n3", cG2phi2D2n3,   "L8op605", c8G2H2D2x3,    1},    (* Q_{G^2H^2D^2}^{(3)} *)
  {"LQW2phi2D2n1", cW2phi2D2n1,   "L8op606", c8W2H2D2x1,    1},    (* Q_{W^2H^2D^2}^{(1)} *)
  {"LQW2phi2D2n2", cW2phi2D2n2,   "L8op607", c8W2H2D2x2,    1},    (* Q_{W^2H^2D^2}^{(2)} *)
  {"LQW2phi2D2n3", cW2phi2D2n3,   "L8op608", c8W2H2D2x3,    1},    (* Q_{W^2H^2D^2}^{(3)} *)
  {"LQW2phi2D2n4", cW2phi2D2n4,   "L8op609", c8W2H2D2x4,    1},    (* Q_{W^2H^2D^2}^{(4)} *)
  {"LQW2phi2D2n5", cW2phi2D2n5,   "L8op610", c8W2H2D2x5,    1},    (* Q_{W^2H^2D^2}^{(5)}; two-term row *)
  {"LQW2phi2D2n6", cW2phi2D2n6,   "L8op611", c8W2H2D2x6,    1},    (* Q_{W^2H^2D^2}^{(6)}; two-term row *)
  {"LQWBphi2D2n1", cWBphi2D2n1,   "L8op612", c8WBH2D2x1,    1},    (* Q_{WBH^2D^2}^{(1)} *)
  {"LQWBphi2D2n2", cWBphi2D2n2,   "L8op613", c8WBH2D2x2,    1},    (* Q_{WBH^2D^2}^{(2)} *)
  {"LQWBphi2D2n3", cWBphi2D2n3,   "L8op614", c8WBH2D2x3,    1},    (* Q_{WBH^2D^2}^{(3)}; two-term row *)
  {"LQWBphi2D2n4", cWBphi2D2n4,   "L8op615", c8WBH2D2x4,    1},    (* Q_{WBH^2D^2}^{(4)}; two-term row *)
  {"LQWBphi2D2n5", cWBphi2D2n5,   "L8op616", c8WBH2D2x5,    1},    (* Q_{WBH^2D^2}^{(5)}; two-term row *)
  {"LQWBphi2D2n6", cWBphi2D2n6,   "L8op617", c8WBH2D2x6,    1},    (* Q_{WBH^2D^2}^{(6)}; two-term row *)
  {"LQB2phi2D2n1", cB2phi2D2n1,   "L8op618", c8B2H2D2x1,    1},    (* Q_{B^2H^2D^2}^{(1)} *)
  {"LQB2phi2D2n2", cB2phi2D2n2,   "L8op619", c8B2H2D2x2,    1},    (* Q_{B^2H^2D^2}^{(2)} *)
  {"LQB2phi2D2n3", cB2phi2D2n3,   "L8op620", c8B2H2D2x3,    1},    (* Q_{B^2H^2D^2}^{(3)} *)

  (* ---- class 8, X H^4 D^2  --  6 pairs, normalisation -I throughout, see note above ---- *)
  {"LQWphi4D2n1",  cWphi4D2n1,    "L8op621", c8WH4D2x1,     -I},    (* Q_{WH^4D^2}^{(1)}; our block carries the factor i that the Murphy row needs to be Hermitian, SmeftFR does not *)
  {"LQWphi4D2n2",  cWphi4D2n2,    "L8op622", c8WH4D2x2,     -I},    (* Q_{WH^4D^2}^{(2)}; our block carries the factor i that the Murphy row needs to be Hermitian, SmeftFR does not *)
  {"LQWphi4D2n3",  cWphi4D2n3,    "L8op623", c8WH4D2x3,     -I},    (* Q_{WH^4D^2}^{(3)}; our block carries the factor i that the Murphy row needs to be Hermitian, SmeftFR does not *)
  {"LQWphi4D2n4",  cWphi4D2n4,    "L8op624", c8WH4D2x4,     -I},    (* Q_{WH^4D^2}^{(4)}; our block carries the factor i that the Murphy row needs to be Hermitian, SmeftFR does not *)
  {"LQBphi4D2n1",  cBphi4D2n1,    "L8op625", c8BH4D2x1,     -I},    (* Q_{BH^4D^2}^{(1)}; our block carries the factor i that the Murphy row needs to be Hermitian, SmeftFR does not *)
  {"LQBphi4D2n2",  cBphi4D2n2,    "L8op626", c8BH4D2x2,     -I}     (* Q_{BH^4D^2}^{(2)}; our block carries the factor i that the Murphy row needs to be Hermitian, SmeftFR does not *)
}
