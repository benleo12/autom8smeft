(* validate/np_truncate.m  --  keep the 1/Lambda^4 content of a merged vertex list.

   Usage, after LoadModel:   Get[$root <> "/validate/np_truncate.m"];
                             {merged, report} = ztTruncate[merged];

   With the input-scheme base model the rotated Standard-Model Lagrangian carries pieces whose
   couplings are polynomials in the shift parameters that vanish only through the parameter
   relations (cw g1SM = sw gwSM = e, for instance), and pieces beyond 1/Lambda^4 that are
   products of two or more shifts.  FeynRules keeps both because neither is syntactically zero.  The
   test here works term by term, never on a whole vertex, because one vertex can hold a genuine
   dimension-eight structure next to such a piece: the {A,H,Z} vertex carries the derivative
   coupling h Z_{mu nu} F^{mu nu} of the X^2H^4 and XH^4D^2 operators, of order v^3/Lambda^4,
   together with a non-derivative h Z_mu A^mu piece that is zero through 1/Lambda^4.

   Each vertex is expanded and its terms are grouped into pieces labelled by
     structure  the product of the factors that are not parameters (momenta, metric, epsilon,
                gamma matrices, colour and flavour deltas), and
     NP order   the sum of the InteractionOrder declared on the parameters of the term, which is
                how WriteUFO assigns the coupling orders MadGraph selects on.
   Then
     - a piece is ZERO when its terms cancel to 1e-10 of the sum of their moduli at two unrelated
       points: every NP-carrying coefficient at a different irrational value, Lambda at 3 and at
       4.5 TeV, and the electroweak inputs moved at the second point, so that a cancellation that
       depends on the input values cannot pass;
     - a structure whose pieces at NP <= 2, the orders of the 1/Lambda^4 model, are all zero is
       removed with its pieces of higher order, since what is left of it is a remnant of the
       rotation beyond the order the input relations are corrected to;
     - a vertex with no piece at NP <= 2 left is removed.
   The pieces above NP 2 of a structure with genuine content at NP <= 2 are kept, since no
   NP^2==2 or NP<=2 run selects them.  A comparison of two structures that are equal only through
   momentum conservation or a Lorentz identity is not made, so such a cancellation is kept, never
   removed: the test can leave a zero in the model but cannot remove a genuine coupling. *)

ztNPof[ztOpts_List] := Module[{ztIO = InteractionOrder /. ztOpts},
  If[ztIO === InteractionOrder, 0,
    Total[Cases[If[MatchQ[ztIO, {_Symbol, _Integer}], {ztIO}, ztIO], {NP, ztN_Integer} :> ztN]]]];

ztInit[] := Module[{},
  ztParams = First /@ M$Parameters;
  ztParamQ = AssociationThread[ztParams -> True];
  ztOptsOf = Association[(#[[1]] -> Flatten[{#[[2]]}]) & /@ M$Parameters];
  ztNP = ztNPof /@ ztOptsOf;
  ztEpsRules = Dispatch[KeyValueMap[#1 -> ztEps^#2 #1 &, Select[ztNP, # != 0 &]]];
  (* the coefficients the probes move: every external parameter that carries an NP order *)
  ztExtQ[ztP_] := (ParameterType /. ztOptsOf[ztP]) === External;
  ztExt = Select[ztParams, ztExtQ[#] && ztNP[#] > 0 &];
  ztEW = Select[{aEWM1, aEW, Gf, MZ, MH}, KeyExistsQ[ztOptsOf, #] && ztExtQ[#] &];];

(* a factor is a parameter factor when every symbol in it is a model parameter or a built-in *)
ztParamFactorQ[ztX_] := AllTrue[DeleteDuplicates[Cases[{ztX}, _Symbol, {0, Infinity}, Heads -> True]],
  Context[#] === "System`" || KeyExistsQ[ztParamQ, #] &];

(* a term -> {structure, parameter factor} *)
ztSplit[ztT_] := Module[{ztF = If[Head[ztT] === Times, List @@ ztT, {ztT}]},
  {Times @@ Select[ztF, ! ztParamFactorQ[#] &], Times @@ Select[ztF, ztParamFactorQ]}];

ztOrder[ztP_] := Exponent[(ztP /. Conjugate[ztX_] :> ztX) /. ztEpsRules, ztEps];

(* The probe values must have no integer relation among them.  Multiples of one irrational number,
   k GoldenRatio mod 1, form an arithmetic progression, so x_k - x_{k+1} - x_{k+2} + x_{k+3} is an
   integer, often zero, at such a point: the combination c8q2H2D3x1 - x2 - x3 + x4 of the left-handed
   Z u ubar coupling vanished at both probes in the combined model, where the dimension-six
   coefficients shift the positions, and a genuine piece was removed.  Square roots of distinct
   primes are linearly independent over the rationals, so no integer combination of them vanishes;
   the two probes use disjoint sets of primes. *)
ztSetProbe[ztK_] := Module[{ztN = Length[ztExt]},
  UpdateParameters @@ Join[
    Thread[ztExt -> N[Table[If[ztK == 1, 1/2 + FractionalPart[Sqrt[Prime[ztI]]],
                                         -(3/10 + FractionalPart[Sqrt[Prime[ztN + ztI]]])], {ztI, ztN}], 20]],
    If[MemberQ[ztParams, Lam], {Lam -> If[ztK == 1, 3000., 4500.]}, {}],
    If[ztK == 2, Thread[ztEW -> (1.013 NumericalValue /@ ztEW)], {}]];
  ztRules = Dispatch[(# -> NumericalValue[#]) & /@ Select[ztParams, NumericQ[NumericalValue[#]] &]]];

ztVal[ztP_] := Module[{ztV = N[ztP /. ztRules]}, If[NumericQ[ztV], ztV, N[NumericalValue[ztP]]]];

ztTruncate[ztMerged_List] := Module[{ztOrig, ztTerms, ztSplits, ztOrders, ztV1, ztV2, ztGroups,
    ztOut = {}, ztReport = {}, ztWorstZero = 0., ztBestKept = Infinity, ztUnjudged = 0},
  ztInit[];
  ztOrig = Join[Thread[ztExt -> (NumericalValue /@ ztExt)], Thread[ztEW -> (NumericalValue /@ ztEW)],
                If[MemberQ[ztParams, Lam], {Lam -> NumericalValue[Lam]}, {}]];
  ztTerms = (If[Head[#] === Plus, List @@ #, {#}] &[Expand[#[[2]]]]) & /@ ztMerged;
  ztSplits = Map[ztSplit, ztTerms, {2}];
  ztOrders = Map[ztOrder, ztSplits[[All, All, 2]], {2}];
  ztSetProbe[1]; ztV1 = Map[ztVal, ztSplits[[All, All, 2]], {2}];
  ztSetProbe[2]; ztV2 = Map[ztVal, ztSplits[[All, All, 2]], {2}];
  UpdateParameters @@ ztOrig;
  Do[
    Module[{ztKeys = Transpose[{ztSplits[[ztI, All, 1]], ztOrders[[ztI]]}], ztIdx, ztZero = {},
        ztLive, ztKeep, ztFields = ztMerged[[ztI, 1, All, 1]]},
      ztIdx = GroupBy[Range[Length[ztKeys]], ztKeys[[#]] &];
      KeyValueMap[Function[{ztKey, ztJ},
        Module[{ztS1 = Abs[Total[ztV1[[ztI, ztJ]]]], ztA1 = Total[Abs[ztV1[[ztI, ztJ]]]],
                ztS2 = Abs[Total[ztV2[[ztI, ztJ]]]], ztA2 = Total[Abs[ztV2[[ztI, ztJ]]]], ztR},
          If[ztA1 == 0 || ztA2 == 0, ztUnjudged++,
            ztR = Max[ztS1/ztA1, ztS2/ztA2];
            If[ztR <= 10^-10, AppendTo[ztZero, ztKey]; ztWorstZero = Max[ztWorstZero, ztR],
              ztBestKept = Min[ztBestKept, ztR]]]]], ztIdx];
      (* structures with a nonzero piece at NP <= 2 *)
      ztLive = AssociationThread[Select[Complement[Keys[ztIdx], ztZero], #[[2]] <= 2 &][[All, 1]] -> True];
      ztZero = AssociationThread[ztZero -> True];
      ztKeep = Select[Range[Length[ztKeys]],
        ! KeyExistsQ[ztZero, ztKeys[[#]]] && KeyExistsQ[ztLive, ztKeys[[#, 1]]] &];
      If[Length[ztKeep] < Length[ztKeys],
        AppendTo[ztReport, {ztFields, Length[ztKeys] - Length[ztKeep], Length[ztKeys],
          Sort[DeleteDuplicates[ztKeys[[Complement[Range[Length[ztKeys]], ztKeep], 2]]]],
          If[Length[ztLive] == 0, "vertex removed", "vertex kept"]}]];
      (* a vertex nothing is removed from keeps FeynRules' own expression, unexpanded, so that only
         the vertices the truncation acts on are written differently *)
      Which[Length[ztKeep] == Length[ztKeys], AppendTo[ztOut, ztMerged[[ztI]]],
            Length[ztLive] > 0, AppendTo[ztOut, {ztMerged[[ztI, 1]], Total[ztTerms[[ztI, ztKeep]]]}]]],
    {ztI, Length[ztMerged]}];
  {ztOut, <|"changed" -> ztReport, "worstZero" -> ztWorstZero, "bestKept" -> ztBestKept,
            "unjudged" -> ztUnjudged|>}];

(* one line per changed vertex, and the separation the classification ran with *)
ztPrintReport[ztRep_] := (
  Scan[Print["[truncate] ", #[[1]], ": ", #[[2]], " of ", #[[3]], " terms removed (NP orders ",
             #[[4]], "), ", #[[5]]] &, ztRep["changed"]];
  Print["[truncate] separation: removed pieces cancel to <= ", ScientificForm[ztRep["worstZero"], 2],
        " of their moduli, kept pieces to >= ", ScientificForm[ztRep["bestKept"], 2],
        "; ", ztRep["unjudged"], " pieces vanish term by term at a probe and are kept"]);
