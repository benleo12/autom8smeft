(* ======================================================================================
   validate/smeftfr_by_class/class1.m
   --------------------------------------------------------------------------------------
   The Murphy class 1 (X^4 and X^3 X-prime, 43 pairs, all normalisation 1) entries of
   validate/smeftfr_pairs.m, SmeftFR v3.03 against dim8auto, as a list of their own so that
   the class runs as a separate validate/fr_compare.wls job.  The format, the conventions,
   the normalisations and how to run the comparison are explained in the header of
   smeftfr_pairs.m.
   ====================================================================================== *)

{
  {"LQB4n1",       cB4n1,         "L8op440", c8B4x1,        1}   (* Q_{B^4}^{(1)} *),
  {"LQB4n3",       cB4n3,         "L8op442", c8B4x3,        1}   (* Q_{B^4}^{(3)} *),
  {"LQB4n2",       cB4n2,         "L8op441", c8B4x2,        1}   (* Q_{B^4}^{(2)} *),
  {"LQW2B2n1",     cW2B2n1,       "L8op461", c8W2B2x1,      1}   (* Q_{W^2B^2}^{(1)} *),
  {"LQW2B2n3",     cW2B2n3,       "L8op463", c8W2B2x3,      1}   (* Q_{W^2B^2}^{(3)} *),
  {"LQW2B2n5",     cW2B2n5,       "L8op465", c8W2B2x5,      1}   (* Q_{W^2B^2}^{(5)} *),
  {"LQW2B2n7",     cW2B2n7,       "L8op467", c8W2B2x7,      1}   (* Q_{W^2B^2}^{(7)} *),
  {"LQW2B2n2",     cW2B2n2,       "L8op462", c8W2B2x2,      1}   (* Q_{W^2B^2}^{(2)} *),
  {"LQW2B2n4",     cW2B2n4,       "L8op464", c8W2B2x4,      1}   (* Q_{W^2B^2}^{(4)} *),
  {"LQW2B2n6",     cW2B2n6,       "L8op466", c8W2B2x6,      1}   (* Q_{W^2B^2}^{(6)} *),
  {"LQW4n1",       cW4n1,         "L8op434", c8W4x1,        1}   (* Q_{W^4}^{(1)} *),
  {"LQW4n3",       cW4n3,         "L8op436", c8W4x3,        1}   (* Q_{W^4}^{(3)} *),
  {"LQW4n5",       cW4n5,         "L8op438", c8W4x5,        1}   (* Q_{W^4}^{(5)} *),
  {"LQW4n2",       cW4n2,         "L8op435", c8W4x2,        1}   (* Q_{W^4}^{(2)} *),
  {"LQW4n4",       cW4n4,         "L8op437", c8W4x4,        1}   (* Q_{W^4}^{(4)} *),
  {"LQW4n6",       cW4n6,         "L8op439", c8W4x6,        1}   (* Q_{W^4}^{(6)} *),
  {"LQG2B2n1",     cG2B2n1,       "L8op454", c8G2B2x1,      1}   (* Q_{G^2B^2}^{(1)} *),
  {"LQG2B2n3",     cG2B2n3,       "L8op456", c8G2B2x3,      1}   (* Q_{G^2B^2}^{(3)} *),
  {"LQG2B2n5",     cG2B2n5,       "L8op458", c8G2B2x5,      1}   (* Q_{G^2B^2}^{(5)} *),
  {"LQG2B2n7",     cG2B2n7,       "L8op460", c8G2B2x7,      1}   (* Q_{G^2B^2}^{(7)} *),
  {"LQG2B2n2",     cG2B2n2,       "L8op455", c8G2B2x2,      1}   (* Q_{G^2B^2}^{(2)} *),
  {"LQG2B2n4",     cG2B2n4,       "L8op457", c8G2B2x4,      1}   (* Q_{G^2B^2}^{(4)} *),
  {"LQG2B2n6",     cG2B2n6,       "L8op459", c8G2B2x6,      1}   (* Q_{G^2B^2}^{(6)} *),
  {"LQG2W2n1",     cG2W2n1,       "L8op447", c8G2W2x1,      1}   (* Q_{G^2W^2}^{(1)} *),
  {"LQG2W2n3",     cG2W2n3,       "L8op449", c8G2W2x3,      1}   (* Q_{G^2W^2}^{(3)} *),
  {"LQG2W2n5",     cG2W2n5,       "L8op451", c8G2W2x5,      1}   (* Q_{G^2W^2}^{(5)} *),
  {"LQG2W2n7",     cG2W2n7,       "L8op453", c8G2W2x7,      1}   (* Q_{G^2W^2}^{(7)} *),
  {"LQG2W2n2",     cG2W2n2,       "L8op448", c8G2W2x2,      1}   (* Q_{G^2W^2}^{(2)} *),
  {"LQG2W2n4",     cG2W2n4,       "L8op450", c8G2W2x4,      1}   (* Q_{G^2W^2}^{(4)} *),
  {"LQG2W2n6",     cG2W2n6,       "L8op452", c8G2W2x6,      1}   (* Q_{G^2W^2}^{(6)} *),
  {"LQG3Bn1",      cG3Bn1,        "L8op443", c8G3Bx1,       1}   (* Q_{G^3B}^{(1)} *),
  {"LQG3Bn3",      cG3Bn3,        "L8op445", c8G3Bx3,       1}   (* Q_{G^3B}^{(3)} *),
  {"LQG3Bn2",      cG3Bn2,        "L8op444", c8G3Bx2,       1}   (* Q_{G^3B}^{(2)} *),
  {"LQG3Bn4",      cG3Bn4,        "L8op446", c8G3Bx4,       1}   (* Q_{G^3B}^{(4)} *),
  {"LQG4n1",       cG4n1,         "L8op425", c8G4x1,        1}   (* Q_{G^4}^{(1)} *),
  {"LQG4n3",       cG4n3,         "L8op427", c8G4x3,        1}   (* Q_{G^4}^{(3)} *),
  {"LQG4n5",       cG4n5,         "L8op429", c8G4x5,        1}   (* Q_{G^4}^{(5)} *),
  {"LQG4n7",       cG4n7,         "L8op431", c8G4x7,        1}   (* Q_{G^4}^{(7)} *),
  {"LQG4n9",       cG4n9,         "L8op433", c8G4x9,        1}   (* Q_{G^4}^{(9)} *),
  {"LQG4n2",       cG4n2,         "L8op426", c8G4x2,        1}   (* Q_{G^4}^{(2)} *),
  {"LQG4n4",       cG4n4,         "L8op428", c8G4x4,        1}   (* Q_{G^4}^{(4)} *),
  {"LQG4n6",       cG4n6,         "L8op430", c8G4x6,        1}   (* Q_{G^4}^{(6)} *),
  {"LQG4n8",       cG4n8,         "L8op432", c8G4x8,        1}   (* Q_{G^4}^{(8)} *)
}
