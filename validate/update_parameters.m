(* validate/update_parameters.m  --  FeynRules' UpdateParameters, with the same effect, in seconds.

   Usage, after LoadModel:   Get[$root <> "/validate/update_parameters.m"];
                             z8UpdateParameters[name -> value, ...]

   What it does.  UpdateParameters[name -> value, ...] gives external parameters new values and recomputes
   the numerical value of every parameter of the model.  z8UpdateParameters leaves the same things behind, in
   the same order: the new values in ParamList, EParamList, MassList and WidthList, the lists M$ExtParams,
   M$IntParams, M$Masses, M$Widths and M$IntParamsNumericalValues, and NumericalValue of every mass, width and
   parameter under its three names.

   When to reach for it.  Whenever a script sets parameters of a model with thousands of them and goes on
   with FeynRules (validate/np_truncate.m, three times for every UFO it writes).  FeynRules computes each value
   as N[x //. M$IntParams /. M$ExtParams /. M$Masses /. M$Widths], three times for every parameter
   (PRIVATE`SetNumericalValues in Core/OutputRoutines.m): the definitions of the internal parameters are
   written out in full inside one another before any number is put in, each value of an external parameter is
   then tried in turn on every part of the result, and ParamList is read again at every step of the loops.
   That is 150 s a call on the model of order 2, with its 4218 parameters, and it grows with the depth of the
   definitions.  Here every internal parameter is evaluated once, from the values of the parameters its
   definition names, and the values are looked up (Dispatch).  A script that only needs the numbers, and not
   FeynRules' state, has validate/geo_numeric.m (z8numRules), which also gives the components of a matrix that
   NumericalValue leaves unevaluated.

   What its result means.  The lists are FeynRules' own, identical.  The numbers are FeynRules' to the
   rounding of their last digits, since the same arithmetic is done in another order: on the nested
   definitions from the inside out, where FeynRules puts the numbers into the definitions written out in full.
   A parameter FeynRules leaves without a number (a definition that names something with no value) is left
   without one here.

   What it must pass.  validate/update_parameters_check.wls runs the three calls of validate/np_truncate.m
   with both, from the same starting point, and compares everything the two leave behind. *)

(* M$ExtParams, M$IntParams, M$Masses, M$Widths and M$IntParamsNumericalValues of PRIVATE`CreateParamLists[False],
   which appends them one rule at a time *)
z8uCreateParamLists[] := (
  M$ExtParams = (Rule[#[[1]], #[[3]]] /. NoValue[1] -> 1) & /@ Select[ParamList, #[[2]] === Ext &];
  M$IntParams = Rule[#[[1]], #[[3]]] & /@ Select[ParamList, #[[2]] === Int &];
  M$Masses = (Rule[#[[2]], #[[3]]] /. NoValue[1] -> 1) & /@ Select[MassList[[2]], #[[3]] =!= Internal &];
  M$Widths = (Rule[#[[2]], #[[3]]] /. NoValue[1] -> 1) & /@ Select[WidthList[[2]], #[[3]] =!= Internal &];
  M$IntParamsNumericalValues = M$IntParams;);

(* x //. M$IntParams /. M$ExtParams, then the masses ("M"), the widths ("W") or both ("MW") as FeynRules applies
   them to a mass, a width and a parameter.  z8uInt[kind, i] is the i-th internal parameter with those rules
   applied, kept once computed, and z8uLazy[kind] replaces an internal parameter by it. *)
z8uD[z8uL_List] := If[z8uL === {}, {}, Dispatch[z8uL]];
z8uEval[z8uK_][z8uX_] := Fold[ReplaceAll, z8uX /. z8uLazy[z8uK], Prepend[z8uTail[z8uK], z8uExtD]];
z8uPrepare[] := (
  (* a value that names another parameter would be replaced once by FeynRules and at every level here *)
  If[! AllTrue[Join[M$ExtParams, M$Masses, M$Widths][[All, 2]], NumericQ],
    Print["[abort] z8UpdateParameters: an external parameter, mass or width whose value is not a number: ",
      Take[Select[Join[M$ExtParams, M$Masses, M$Widths], ! NumericQ[#[[2]]] &], UpTo[10]]]; Quit[1]];
  z8uExtD = z8uD[M$ExtParams];
  z8uTail = <|"M" -> {z8uD[M$Masses]}, "W" -> {z8uD[M$Widths]}, "MW" -> {z8uD[M$Masses], z8uD[M$Widths]}|>;
  z8uRhs = M$IntParams[[All, 2]];
  ClearAll[z8uInt];
  z8uInt[z8uK_, z8uI_] := z8uInt[z8uK, z8uI] = z8uEval[z8uK][z8uRhs[[z8uI]]];
  z8uLazy = AssociationMap[Function[z8uK,
      z8uD[MapIndexed[With[{z8uI = First[#2]}, #1[[1]] :> z8uInt[z8uK, z8uI]] &, M$IntParams]]], {"M", "W", "MW"}];);

(* PRIVATE`SetNumericalValues[] *)
z8uSetNumericalValues[] := Block[{$RecursionLimit = 65536},
  Module[{z8uRev, z8uRevS, z8uNames, z8uVal, z8uF1, z8uF2, z8uIV},
    z8uRev = ParamRules /. Rule[z8uA_, z8uB_] :> Rule[z8uB, z8uA];
    z8uRevS = z8uRev /. Index[_, z8uA_] :> z8uA;
    z8uCreateParamLists[];
    z8uPrepare[];
    Do[NumericalValue[MassList[[2, z8uJ, 2]]] = N[z8uEval["M"][MassList[[2, z8uJ, 2]]]], {z8uJ, Length[MassList[[2]]]}];
    Do[NumericalValue[WidthList[[2, z8uJ, 2]]] = N[z8uEval["W"][WidthList[[2, z8uJ, 2]]]], {z8uJ, Length[WidthList[[2]]]}];
    z8uNames = ParamList[[All, 1]];
    z8uVal = N[z8uEval["MW"][#]] & /@ z8uNames;
    z8uF1 = (# /. z8uRev) & /@ z8uNames;
    z8uF2 = (# /. z8uRevS) & /@ z8uNames;
    Do[NumericalValue[z8uNames[[z8uJ]]] = z8uVal[[z8uJ]];
       NumericalValue[z8uF1[[z8uJ]]] = z8uVal[[z8uJ]];
       NumericalValue[z8uF2[[z8uJ]]] = z8uVal[[z8uJ]], {z8uJ, Length[z8uNames]}];
    z8uIV = M$IntParamsNumericalValues;
    Do[z8uIV[[z8uJ, 2]] = NumericalValue[z8uIV[[z8uJ, 2]]], {z8uJ, Length[z8uIV]}];
    M$IntParamsNumericalValues = z8uIV;
    ClearAll[z8uInt];]];

(* UpdateParameters[options] *)
z8UpdateParameters[z8uOpts___] := Module[{z8uNew, z8uEPL = EParamList, z8uML = MassList, z8uWL = WidthList},
  z8uNew = z8uD[Flatten[{z8uOpts}] /. ParamRules /. (ParamRules /. Index[_, z8uA_] :> z8uA)];
  ParamList = If[#[[2]] === Ext, ReplacePart[#, 3 -> ((#[[1]] /. z8uNew) /. (#[[1]] -> #[[3]]))], #] & /@ ParamList;
  Do[z8uEPL[[z8uJ, 2, z8uI, 2, -3]] = (z8uEPL[[z8uJ, 2, z8uI, 2, 1]] /. z8uNew) /.
       (z8uEPL[[z8uJ, 2, z8uI, 2, 1]] -> z8uEPL[[z8uJ, 2, z8uI, 2, -3]]),
     {z8uJ, Length[z8uEPL]}, {z8uI, Length[z8uEPL[[z8uJ, 2]]]}];
  EParamList = z8uEPL;
  Do[If[z8uML[[2, z8uJ, 3]] =!= Internal,
       z8uML[[2, z8uJ, 3]] = (z8uML[[2, z8uJ, 2]] /. z8uNew) /. (z8uML[[2, z8uJ, 2]] -> z8uML[[2, z8uJ, 3]])],
     {z8uJ, Length[z8uML[[2]]]}];
  MassList = z8uML;
  Do[If[z8uWL[[2, z8uJ, 3]] =!= Internal,
       z8uWL[[2, z8uJ, 3]] = (z8uWL[[2, z8uJ, 2]] /. z8uNew) /. (z8uWL[[2, z8uJ, 2]] -> z8uWL[[2, z8uJ, 3]])],
     {z8uJ, Length[z8uWL[[2]]]}];
  WidthList = z8uWL;
  z8uSetNumericalValues[];
  If[FR$Parallelize, UpdateFRDistributedVariables[]];];
