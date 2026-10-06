(* ======================================================================================
   validate/v7_pairs.m
   --------------------------------------------------------------------------------------
   Pair list consumed by validate/fr_compare.wls:

       wolframscript -file validate/fr_compare.wls \
           prior_work/hand_typed/dim8_geosmeftVBF.fr  <generated.fr>  validate/v7_pairs.m

   Each entry is  {handBlock, handWC, genBlock, genWC, normalisation}  with the meaning

       handBlock|_{handWC}  ==  normalisation * genBlock|_{genWC -> handWC, Lam -> 1}

   i.e. "normalisation" is the factor k in  O_hand = k * Q_Murphy, so that
   C_Murphy = k * c_hand.  handBlock/genBlock are strings (fr_compare.wls applies
   Symbol[...] to them); handWC/genWC are bare symbols.

   HOW THIS FILE WAS DERIVED
   -------------------------
   * Hand-typed side: docs/hand_typed_operators.md Section 3 ("dim8_geosmeftVBF.fr"),
     cross-checked line by line against prior_work/hand_typed/dim8_geosmeftVBF.fr.
     Every block name and every coefficient name below was verified to occur verbatim in
     that .fr file (blocks at lines 814-1134, coefficient declarations at lines 478-513).
     The "normalisation" column is the catalogue's "relation" column: it is 1 wherever the
     hand-typed prefactor already converts Ta = sigma/2 into Murphy's tau (2 Ta = tau), and
     2 for the four blocks that carry a prefactor 4 in front of a *single* Ta.
   * Generated side: docs/block_index.json.  Every "genBlock" below was checked to exist
     there with exactly the quoted Murphy label in its "ops" list and exactly the quoted
     Wilson coefficient in its "wcs" list; the emitted forms in tests/gen_smoke/gen.fr were
     read term by term (they are fully SU(2)-expanded, so no symbolic adjoint index and no
     Ta/Eps survive on the generated side) and the SU(2) component decomposition
     tau^I_ab tau^I_cd = 2 d_ad d_cb - d_ab d_cd was verified explicitly for every block
     containing a tau (x) tau structure.
   * Both sides use FeynRules' covariant-derivative sign and both are unitary gauge, so no
     convention adjustment is needed; the comparison is FeynRules-internal.
   * No hand-typed VBF block applies Sum[outlag, {aa,1,3}, ...] and none returns
     outlag + HC[outlag] (checked by grep), so neither the spurious factor 3 nor the
     Hermitian-conjugate doubling described in the catalogue affects any entry here.

   DELIBERATELY EXCLUDED (see the final report accompanying this file)
   ------------------------------------------------------------------
   * L6 (cHW, cHB, cHWB, cHQ1, cHQ3, cHu, cHd): dimension-6 Warsaw operators, no
     generated counterpart exists (the generator emits Murphy dim-8 operators only).
   * L8contact9 (c2Q2HWD5) and L8contact10 (c2Q2HWD6), Q^{(9),(11)}_{q^2WH^2D}: the
     catalogue flags these with [star] because the adjoint indices aa, bb occur only inside
     Ta[...] and Eps[...], are carried by no field, and no explicit Sum is applied; it
     defers the verdict to its Section 7, which is absent from the document.  Ambiguous,
     so excluded.
   * newL8geo1, newL8geo2, newL8geo3, newL8geo4, newL8geo1u, newL8geo2u, newL8geo1d,
     newL8geo2d (c2Q2H3D1-4, c2u2H3D1,2, c2d2H3D1,2): class 11 psi^2 H^2 D^3 in the
     Corbett/VBF-paper form, which is not a Murphy basis element.  They map onto Murphy's
     Q^{(1..4)}_{psi^2H^2D^3} only after integration by parts plus equations of motion,
     and the EOM pieces spill into classes 12, 13, 15 and 18.  A vertex-by-vertex test
     cannot pass, so no pair is emitted.

   26 pairs.
   ====================================================================================== *)

{
  (* ---- class 18, psi^4 H^2 ------------------------------------------------------- *)
  {"L8testtest4L",   c2H4Q1,     "L8op237", c8q4H2x1,     1},  (* Q_{q^4H^2}^{(1)} *)
  {"L8testtest4L",   c2H4Q2,     "L8op238", c8q4H2x2,     1},  (* Q_{q^4H^2}^{(2)}; hand prefactor 4 Ta Ta = tau tau *)
  {"L8testtest4L",   c2H4Q3,     "L8op239", c8q4H2x3,     1},  (* Q_{q^4H^2}^{(3)}; hand prefactor 4 Ta Ta = tau tau *)
  {"L8testtest4R",   c2H4u,      "L8op247", c8u4H2,       1},  (* Q_{u^4H^2} *)
  {"L8testtest4R",   c2H4d,      "L8op248", c8d4H2,       1},  (* Q_{d^4H^2} *)
  {"L8testtest4R",   c2H2u2d,    "L8op251", c8u2d2H2x1,   1},  (* Q_{u^2d^2H^2}^{(1)} *)
  {"L8testtest2L2R", c2H2Q2u1,   "L8op261", c8q2u2H2x1,   1},  (* Q_{q^2u^2H^2}^{(1)} *)
  {"L8testtest2L2R", c2H2Q2u2,   "L8op262", c8q2u2H2x2,   1},  (* Q_{q^2u^2H^2}^{(2)}; hand prefactor 4 Ta Ta = tau tau *)
  {"L8testtest2L2R", c2H2Q2d1,   "L8op265", c8q2d2H2x1,   1},  (* Q_{q^2d^2H^2}^{(1)} *)
  {"L8testtest2L2R", c2H2Q2d2,   "L8op266", c8q2d2H2x2,   1},  (* Q_{q^2d^2H^2}^{(2)}; hand prefactor 4 Ta Ta = tau tau *)

  (* ---- class 15, psi^2 X H^2 D : quark doublet, B ---------------------------------- *)
  {"L8contactZ5",    c2Q2HBD1,   "L8op177", c8q2BH2Dx1,   1},  (* Q_{q^2BH^2D}^{(1)}: (qbar g^nu tau^I q) D^mu(H^dag tau^I H) B_{mu nu} *)
  {"L8contactZ6",    c2Q2HBD2,   "L8op179", c8q2BH2Dx3,   1},  (* Q_{q^2BH^2D}^{(3)}: Hermitian form, the hand block supplies the i of H^dag i Dlr H *)
  {"L8contactZ7",    c2Q2HBD3,   "L8op181", c8q2BH2Dx5,   1},  (* Q_{q^2BH^2D}^{(5)}: (qbar g^nu q) D^mu(H^dag H) B_{mu nu} *)
  {"L8contactZ8",    c2Q2HBD4,   "L8op183", c8q2BH2Dx7,   1},  (* Q_{q^2BH^2D}^{(7)}: Hermitian form with the explicit i *)

  (* ---- class 15, psi^2 X H^2 D : quark doublet, W ---------------------------------- *)
  {"L8contact5",     c2Q2HWD1,   "L8op165", c8q2WH2Dx1,   1},  (* Q_{q^2WH^2D}^{(1)}: hand prefactor 2 Ta = tau *)
  {"L8contact6",     c2Q2HWD2,   "L8op167", c8q2WH2Dx3,   1},  (* Q_{q^2WH^2D}^{(3)} *)
  {"L8contact7",     c2Q2HWD3,   "L8op169", c8q2WH2Dx5,   1},  (* Q_{q^2WH^2D}^{(5)} *)
  {"L8contact8",     c2Q2HWD4,   "L8op171", c8q2WH2Dx7,   1},  (* Q_{q^2WH^2D}^{(7)} *)

  (* ---- class 15, psi^2 X H^2 D : up singlet ---------------------------------------- *)
  {"L8contactZu5",   c2u2HWD1,   "L8op111", c8u2WH2Dx1,   2},  (* Q_{u^2WH^2D}^{(1)}: hand prefactor 4 with a SINGLE Ta, so O = 2 Q *)
  {"L8contactZu6",   c2u2HWD2,   "L8op113", c8u2WH2Dx3,   2},  (* Q_{u^2WH^2D}^{(3)}: same factor 2 *)
  {"L8contactZu7",   c2u2HBD1,   "L8op115", c8u2BH2Dx1,   1},  (* Q_{u^2BH^2D}^{(1)} *)
  {"L8contactZu8",   c2u2HBD2,   "L8op117", c8u2BH2Dx3,   1},  (* Q_{u^2BH^2D}^{(3)} *)

  (* ---- class 15, psi^2 X H^2 D : down singlet -------------------------------------- *)
  {"L8contactZd5",   c2d2HWD1,   "L8op123", c8d2WH2Dx1,   2},  (* Q_{d^2WH^2D}^{(1)}: hand prefactor 4 with a SINGLE Ta, so O = 2 Q *)
  {"L8contactZd6",   c2d2HWD2,   "L8op125", c8d2WH2Dx3,   2},  (* Q_{d^2WH^2D}^{(3)}: same factor 2 *)
  {"L8contactZd7",   c2d2HBD1,   "L8op127", c8d2BH2Dx1,   1},  (* Q_{d^2BH^2D}^{(1)} *)
  {"L8contactZd8",   c2d2HBD2,   "L8op129", c8d2BH2Dx3,   1}   (* Q_{d^2BH^2D}^{(3)} *)
}
