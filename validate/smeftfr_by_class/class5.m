(* ======================================================================================
   validate/smeftfr_by_class/class5.m
   --------------------------------------------------------------------------------------
   The Murphy class 5 (X^3 H^2, 6 pairs, all normalisation 1) entries of
   validate/smeftfr_pairs.m, SmeftFR v3.03 against dim8auto, as a list of their own so that
   the class runs as a separate validate/fr_compare.wls job.  The format, the conventions,
   the normalisations and how to run the comparison are explained in the header of
   smeftfr_pairs.m.
   ====================================================================================== *)

{
  {"LQG3phi2n1",   cG3phi2n1,     "L8op587", c8G3H2x1,      1}   (* Q_{G^3H^2}^{(1)} *),
  {"LQG3phi2n2",   cG3phi2n2,     "L8op588", c8G3H2x2,      1}   (* Q_{G^3H^2}^{(2)} *),
  {"LQW3phi2n1",   cW3phi2n1,     "L8op589", c8W3H2x1,      1}   (* Q_{W^3H^2}^{(1)} *),
  {"LQW3phi2n2",   cW3phi2n2,     "L8op590", c8W3H2x2,      1}   (* Q_{W^3H^2}^{(2)} *),
  {"LQW2Bphi2n1",  cW2Bphi2n1,    "L8op591", c8W2BH2x1,     1}   (* Q_{W^2BH^2}^{(1)} *),
  {"LQW2Bphi2n2",  cW2Bphi2n2,    "L8op592", c8W2BH2x2,     1}   (* Q_{W^2BH^2}^{(2)}; two-term operator, both terms present on both sides *)
}
