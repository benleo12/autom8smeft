(* ======================================================================================
   validate/smeftfr_by_class/class8.m
   --------------------------------------------------------------------------------------
   The Murphy class 8 (X H^4 D^2, 6 pairs, normalisation -I throughout) entries of
   validate/smeftfr_pairs.m, SmeftFR v3.03 against dim8auto, as a list of their own so that
   the class runs as a separate validate/fr_compare.wls job.  The format, the conventions,
   the normalisations and how to run the comparison are explained in the header of
   smeftfr_pairs.m.
   ====================================================================================== *)

{
  {"LQWphi4D2n1",  cWphi4D2n1,    "L8op621", c8WH4D2x1,     -I}   (* Q_{WH^4D^2}^{(1)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n2",  cWphi4D2n2,    "L8op622", c8WH4D2x2,     -I}   (* Q_{WH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n3",  cWphi4D2n3,    "L8op623", c8WH4D2x3,     -I}   (* Q_{WH^4D^2}^{(3)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n4",  cWphi4D2n4,    "L8op624", c8WH4D2x4,     -I}   (* Q_{WH^4D^2}^{(4)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQBphi4D2n1",  cBphi4D2n1,    "L8op625", c8BH4D2x1,     -I}   (* Q_{BH^4D^2}^{(1)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQBphi4D2n2",  cBphi4D2n2,    "L8op626", c8BH4D2x2,     -I}   (* Q_{BH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *)
}
