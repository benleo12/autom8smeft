(* validate/update_parameters_check.wls  --  does validate/update_parameters.m leave what FeynRules' UpdateParameters
   leaves?

   Loads the model of DIM8_BASE as validate/fr_writeufo.wls does and, from the same starting point, makes the
   three calls validate/np_truncate.m makes for a UFO (its two probes, then the return to the model's values),
   once with UpdateParameters and once with z8UpdateParameters.  After each call it compares
     - ParamList, EParamList, MassList, WidthList, M$ExtParams, M$IntParams, M$Masses and M$Widths, which must be
       identical, and
     - M$IntParamsNumericalValues and every definition of NumericalValue, which must have the same left-hand
       sides in the same order, and numbers that agree to twelve digits (the same arithmetic in another order).
   It prints the time of every call, and exits 0 on PASS.

     DIM8_ROOT=... DIM8_BASE="base_geo2_mw.fr;dim6_geo.fr;gen_geo2.fr" DIM8_GEO_N=2 \
       wolframscript -file validate/update_parameters_check.wls

   DIM8_UPDATE_CAP=s, for a model on which UpdateParameters does not end (order 4): the three calls are made
   with z8UpdateParameters alone, and after each one NumericalValue of every parameter and component is compared
   with validate/geo_numeric.m, which evaluates them another way (from the Value and Definitions of
   M$Parameters, in passes).  A component NumericalValue leaves without a number must be zero there (the off-diagonal
   components of a matrix that vanish through its Definitions).  After the first call it is also compared with FeynRules' own expression
   N[x //. M$IntParams /. M$ExtParams /. M$Masses /. M$Widths], parameter by parameter, for every parameter on
   which that expression ends within s seconds; the number it does not end on is printed. *)
$root = If[Environment["DIM8_ROOT"] === $Failed, ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9bases = StringTrim /@ StringSplit[If[Environment["DIM8_BASE"] === $Failed, "base.fr", Environment["DIM8_BASE"]], ";"];
LoadModel[Sequence @@ Append[z9bases, "gen.fr"]];
Get[$root <> "/validate/np_truncate.m"]; ztInit[];
Print["[update] ", Length[ParamList], " parameters, ", Length[ztExt], " coefficients moved by the probes, ",
  Count[ParamList, {_, Int, ___}], " internal parameters"];

z9orig = Join[Thread[ztExt -> (NumericalValue /@ ztExt)], Thread[ztEW -> (NumericalValue /@ ztEW)],
              If[MemberQ[ztParams, Lam], {Lam -> NumericalValue[Lam]}, {}]];
z9cap = Environment["DIM8_UPDATE_CAP"];
If[z9cap =!= $Failed,
  z9cap = ToExpression[z9cap];
  Get[$root <> "/validate/geo_numeric.m"];
  z9all = Join @@ (If[z8numMatrixQ[#], z8numComponents[#], {#[[1]]}] & /@ M$Parameters);
  z9agree[z9a_, z9b_] := NumericQ[z9a] && NumericQ[z9b] && Abs[z9a - z9b] <= 10^-12 Max[Abs[z9a], Abs[z9b]];
  z9ok = True;
  Do[Module[{z9t, z9other, z9bad = {}, z9unev = {}, z9same = 0},
      z9t = First[AbsoluteTiming[z8UpdateParameters @@ If[z9k <= 2, ztProbe[z9k], z9orig]]];
      z9other = Association[z8numRules[{}]];
      Do[Module[{z9nv = NumericalValue[z9p], z9o = Lookup[z9other, z9p, Missing[]]},
          Which[! NumericQ[z9nv], AppendTo[z9unev, z9p -> z9o],
                z9agree[z9nv, z9o], z9same++,
                True, AppendTo[z9bad, {z9p, z9nv, z9o}]]], {z9p, z9all}];
      Print["[update] call ", z9k, ": z8UpdateParameters ", Round[z9t, 0.01], " s; against validate/geo_numeric.m ", z9same, " of ",
        Length[z9all], " agree to twelve digits, ", Length[z9unev], " have no NumericalValue (zero through the Definitions of their matrix: ",
        AllTrue[Values[Association[z9unev]], # == 0 &], ")", If[z9bad === {}, "", "  DIFFER: " <> ToString[InputForm[Take[z9bad, UpTo[8]]]]]];
      z9ok = z9ok && z9bad === {} && AllTrue[Values[Association[z9unev]], TrueQ[# == 0] &];
      If[z9k == 1, Module[{z9done = 0, z9late = {}, z9off = {}, z9v, z9t0 = AbsoluteTime[]},
          Do[z9v = MemoryConstrained[TimeConstrained[N[z9x //. M$IntParams /. M$ExtParams /. M$Masses /. M$Widths], z9cap, $TimedOut], 6*10^9, $TimedOut];
             Which[z9v === $TimedOut, AppendTo[z9late, z9x],
                   z9v === NumericalValue[z9x] || z9agree[z9v, NumericalValue[z9x]], z9done++,
                   True, AppendTo[z9off, {z9x, z9v, NumericalValue[z9x]}]], {z9x, ParamList[[All, 1]]}];
          Print["[update] call 1: FeynRules' own expression, at most ", z9cap, " s a parameter (", Round[AbsoluteTime[] - z9t0], " s in all): ends on ",
            z9done + Length[z9off], " of ", Length[ParamList], " parameters, ", z9done, " of them agree to twelve digits; it does not end on ", Length[z9late],
            If[z9off === {}, "", "  DIFFER: " <> ToString[InputForm[Take[z9off, UpTo[8]]]]]];
          z9ok = z9ok && z9off === {}]]],
    {z9k, 3}];
  Print["[update] ", If[z9ok, "PASS", "DIFFER"]];
  Exit[If[z9ok, 0, 1]]];

z9start = {ParamList, EParamList, MassList, WidthList, M$ExtParams, M$IntParams, M$Masses, M$Widths,
           M$IntParamsNumericalValues, DownValues[NumericalValue]};
z9restore[] := ({ParamList, EParamList, MassList, WidthList, M$ExtParams, M$IntParams, M$Masses, M$Widths,
                 M$IntParamsNumericalValues} = Most[z9start]; DownValues[NumericalValue] = Last[z9start];);
z9snap[] := {{ParamList, EParamList, MassList, WidthList, M$ExtParams, M$IntParams, M$Masses, M$Widths},
             M$IntParamsNumericalValues, DownValues[NumericalValue]};
z9run[z9f_] := Module[{z9s = {}, z9t = {}},
  Do[AppendTo[z9t, First[AbsoluteTiming[z9f @@ If[z9k <= 2, ztProbe[z9k], z9orig]]]]; AppendTo[z9s, z9snap[]], {z9k, 3}];
  {z9t, z9s}];
{z9tA, z9A} = z9run[UpdateParameters];
Print["[update] UpdateParameters: ", Round[z9tA, 0.1], " s"];
z9restore[];
{z9tB, z9B} = z9run[z8UpdateParameters];
Print["[update] z8UpdateParameters: ", Round[z9tB, 0.01], " s"];

(* two right-hand sides, held: identical (SameQ, which lets two machine numbers differ in their last bit), or numbers
   of one kind whose relative difference is returned *)
z9numQ[z9h_Hold] := MatchQ[z9h, Hold[_Real | _Integer | _Rational | _Complex]];
z9rel[z9a_Hold, z9b_Hold] := Which[z9a === z9b, 0.,
  z9numQ[z9a] && z9numQ[z9b] && Head[First[z9a]] === Head[First[z9b]],
    N[Abs[First[z9a] - First[z9b]]/Max[Abs[First[z9a]], Abs[First[z9b]]]],
  True, Infinity];
z9sides[z9r_] := Replace[z9r, {HoldPattern[RuleDelayed[z9l_, z9v_]] :> {Hold[z9l], Hold[z9v]}, HoldPattern[Rule[z9l_, z9v_]] :> {Hold[z9l], Hold[z9v]}}];
z9cmp[z9x_List, z9y_List] := Module[{z9sx = z9sides /@ z9x, z9sy = z9sides /@ z9y, z9d},
  If[Length[z9sx] =!= Length[z9sy] || z9sx[[All, 1]] =!= z9sy[[All, 1]], Return[{False, 0, Infinity, {}}]];
  z9d = MapThread[z9rel[#1[[2]], #2[[2]]] &, {z9sx, z9sy}];
  {True, Count[z9d, 0.], Max[z9d, 0.], Take[Pick[z9sx[[All, 1]], (# > 10^-12 &) /@ z9d], UpTo[8]]}];
z9names = {"ParamList", "EParamList", "MassList", "WidthList", "M$ExtParams", "M$IntParams", "M$Masses", "M$Widths"};
z9ok = True;
Do[Module[{z9same = MapThread[SameQ, {z9A[[z9k, 1]], z9B[[z9k, 1]]}], z9iv, z9nv},
    z9iv = z9cmp[z9A[[z9k, 2]], z9B[[z9k, 2]]];
    z9nv = z9cmp[z9A[[z9k, 3]], z9B[[z9k, 3]]];
    Print["[update] call ", z9k, ": lists identical ", And @@ z9same,
      If[And @@ z9same, "", "  DIFFER: " <> ToString[Pick[z9names, z9same, False]]]];
    Print["[update] call ", z9k, ": NumericalValue, ", Length[z9A[[z9k, 3]]], " definitions, the same left-hand sides ", z9nv[[1]],
      ", ", z9nv[[2]], " identical, largest relative difference ", ScientificForm[z9nv[[3]], 2],
      If[z9nv[[4]] === {}, "", "  beyond twelve digits: " <> ToString[InputForm[z9nv[[4]]]]]];
    Print["[update] call ", z9k, ": M$IntParamsNumericalValues, ", Length[z9A[[z9k, 2]]], " values, the same left-hand sides ", z9iv[[1]],
      ", ", z9iv[[2]], " identical, largest relative difference ", ScientificForm[z9iv[[3]], 2],
      If[z9iv[[4]] === {}, "", "  beyond twelve digits: " <> ToString[InputForm[z9iv[[4]]]]]];
    z9ok = z9ok && And @@ z9same && z9nv[[1]] && z9iv[[1]] && z9nv[[3]] <= 10^-12 && z9iv[[3]] <= 10^-12],
  {z9k, 3}];
Print["[update] ", If[z9ok, "PASS", "DIFFER"]];
Exit[If[z9ok, 0, 1]]
