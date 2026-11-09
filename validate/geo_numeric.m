(* validate/geo_numeric.m  --  the numerical value of every parameter of the loaded model, at given values of
   some of its external parameters, for validate/check_bilinears_geo.wls and validate/check_fermion_masses_geo.wls.

   FeynRules' UpdateParameters takes six minutes per call on a model of order N, with its four thousand
   parameters, and NumericalValue leaves the components of a matrix parameter that are zero only through its
   Definitions (yl[1,2], the off-diagonal Yukawas) unevaluated.  z8numRules[{name -> value, ...}] instead
   starts from the masses and the external parameters (their values in the model, those given replacing
   them) and evaluates the internal parameters from their Value in passes, each with every value found so
   far, until none is left.  A component of a matrix parameter comes from the rules of its Value or, failing
   those, from its Definitions, and so does a scalar with Definitions and no Value (gw and g1).  It returns
   the rules of every parameter and component, and stops with the names of those it could not evaluate.
   validate/geo_numeric_check.wls compares it with UpdateParameters and NumericalValue. *)
z8numOpt[z8p_] := Flatten[{z8p[[2]]}];
z8numMatrixQ[z8p_] := MatchQ[Indices /. z8numOpt[z8p], {__}];
z8numComponents[z8p_] := Flatten[Outer[z8p[[1]], Sequence @@ (IndexRange[#] /. NoUnfold -> Identity & /@ (Indices /. z8numOpt[z8p]))]];
z8numExternalQ[z8p_] := (ParameterType /. z8numOpt[z8p]) === External;
z8numRules[z8set_List] := Module[{z8known = Association[], z8todo = {}, z8found = True, z8disp, z8masses},
  (* the masses of the particles that carry a number, which the values use as parameters *)
  z8masses = Cases[Cases[M$ClassesDescription, (Mass -> z8m_) :> z8m, Infinity], {z8s_Symbol, z8v_?NumericQ} :> (z8s -> z8v), {0, Infinity}];
  Scan[(z8known[#[[1]]] = N[#[[2]]]) &, z8masses];
  Scan[Function[z8p, Which[
      z8numExternalQ[z8p], z8known[z8p[[1]]] = N[NumericalValue[z8p[[1]]]],
      z8numMatrixQ[z8p], Scan[AppendTo[z8todo, {z8p, #}] &, z8numComponents[z8p]],
      True, AppendTo[z8todo, {z8p, z8p[[1]]}]]], M$Parameters];
  Scan[(z8known[#[[1]]] = N[#[[2]]]) &, z8set];
  While[z8todo =!= {} && z8found,
    z8found = False;
    z8disp = Dispatch[Normal[z8known]];
    z8todo = Select[z8todo, Function[z8e, Module[{z8p = z8e[[1]], z8c = z8e[[2]], z8rhs, z8val},
        (* a scalar with Definitions and no Value (gw -> gwSM (1 + gw1 + ...)) is its definition *)
        z8rhs = If[z8numMatrixQ[z8p] || (Value /. z8numOpt[z8p]) === Value,
          z8c /. Cases[Flatten[{Value /. z8numOpt[z8p]}], _Rule | _RuleDelayed]
              /. Cases[Flatten[{Definitions /. z8numOpt[z8p]}], _Rule | _RuleDelayed],
          Value /. z8numOpt[z8p]];
        z8val = Quiet[N[z8rhs /. z8disp]];
        If[NumericQ[z8val], z8known[z8c] = z8val; z8found = True; False, True]]]]];
  If[z8todo =!= {}, Print["[numeric] STOPPED: no value for ", Take[z8todo[[All, 2]], UpTo[20]]]; Quit[1]];
  Normal[z8known]];
