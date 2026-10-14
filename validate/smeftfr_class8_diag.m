(* ======================================================================================
   validate/smeftfr_class8_diag.m
   --------------------------------------------------------------------------------------
   A normalisation scan for the three class-8 operators with a dual field strength,
   Q_{WH^4D^2}^{(2)}, Q_{WH^4D^2}^{(4)} and Q_{BH^4D^2}^{(2)}.  Each is paired with its SmeftFR
   block at the normalisations I, -1 and 1, the three alternatives to the -I of
   validate/smeftfr_pairs.m.  Since -I is the relative factor between SmeftFR's operator and
   ours, all nine entries must fail, which shows that the comparison resolves that factor,
   including the sign of the dual.  Format and conventions as in the header of
   smeftfr_pairs.m.
   ====================================================================================== *)

{
  {"LQWphi4D2n2",  cWphi4D2n2,    "L8op622", c8WH4D2x2, I},    (* Q_{WH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n4",  cWphi4D2n4,    "L8op624", c8WH4D2x4, I},    (* Q_{WH^4D^2}^{(4)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQBphi4D2n2",  cBphi4D2n2,    "L8op626", c8BH4D2x2, I}     (* Q_{BH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n2",  cWphi4D2n2,    "L8op622", c8WH4D2x2, -1},    (* Q_{WH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n4",  cWphi4D2n4,    "L8op624", c8WH4D2x4, -1},    (* Q_{WH^4D^2}^{(4)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQBphi4D2n2",  cBphi4D2n2,    "L8op626", c8BH4D2x2, -1}     (* Q_{BH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n2",  cWphi4D2n2,    "L8op622", c8WH4D2x2, 1},    (* Q_{WH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQWphi4D2n4",  cWphi4D2n4,    "L8op624", c8WH4D2x4, 1},    (* Q_{WH^4D^2}^{(4)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *),
  {"LQBphi4D2n2",  cBphi4D2n2,    "L8op626", c8BH4D2x2, 1}     (* Q_{BH^4D^2}^{(2)}; our block carries the factor i that makes the Murphy operator Hermitian, SmeftFR does not *)
}
