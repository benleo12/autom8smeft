(* validate/check_fermion_masses_geo.wls N [PREFIX]  --  are the fermion masses of the model of order N its inputs through t^N?

   The fermion half of validate/check_bilinears_geo.wls.  In the model of order N (gen/towers.py) the
   Yukawa couplings of the base carry the factor 1 + yr1 + ... + yrN and a compensation of the operators
   psi^2H^5 and their towers (H^dag H)^k psi^2H^5, both from gen/derive_geo.py and written out in LYukawa
   by gen/input_scheme.py, so that the mass of each fermion stays at its input through O(t^N).  The
   Lagrangian is the Standard Model of the base plus every block with a fermion two-point term at the
   vacuum: the dimension-six class psi^2H^3 (G6cl5) and the members of every dimension of the class
   psi^2H^5 (gen_geo<N>.json, class 12).  Every coefficient with an NP order p is switched on at c_p t^p,
   as in validate/check_bilinears_geo.wls, so the coefficients that move the vev through G_F are on too.
   The fermion two-point terms at t, minus those at t = 0 (the Standard Model, whose masses are the inputs
   by construction), must fall by 2^(N+1) per halving of t, from t = 1/2 to 1/4 to 1/8, for every pair of
   flavours.  A fermion whose input mass is zero has no Yukawa and, with the flavour structures of the
   model, no term from these operators either, so it is reported as an exact zero.

     DIM8_ROOT=... wolframscript -file validate/check_fermion_masses_geo.wls 4 [PREFIX]
   With PREFIX the blocks whose names start with it are left out (T10 for the members of dimension ten),
   while their compensation stays in the base, and the test must then fail.
*)
$root = Environment["DIM8_ROOT"];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9N = ToExpression[$ScriptCommandLine[[2]]];
z9base = "base_geo" <> ToString[z9N] <> "_mw.fr";
z9drop = If[Length[$ScriptCommandLine] >= 3, $ScriptCommandLine[[3]], None];
z9gen = "gen_geo" <> ToString[Max[z9N, 2]] <> ".fr";
z9gen = If[FileExistsQ[z9gen], z9gen, "gen_geo4.fr"];
LoadModel[z9base, "dim6_geo.fr", z9gen, "gen.fr"];
Print["[fermion] base ", z9base, "  towers ", z9gen, "  order ", z9N, "  z8geoN ", z8geoN];
If[z8geoN =!= z9N, Print["[fermion] ABORT: the base is of order ", z8geoN]; Quit[1]];

z9json = Import[StringReplace[z9gen, ".fr" -> ".json"], "RawJSON"];
z9blocks = Join[{"G6cl5"}, #["block"] & /@ Select[z9json, #["cls"] == 12 && #["dim"] <= 2 z9N + 4 &]];
If[z9drop =!= None, z9blocks = Select[z9blocks, ! StringStartsQ[#, z9drop] &]; Print["[fermion] NEGATIVE CONTROL: blocks ", z9drop, "* left out"]];
Print["[fermion] blocks: ", z9blocks];

z9f[z9x_] := If[! NumericQ[z9x], "NOT NUMERIC", If[z9x == 0, "0", ToString[InputForm[N[Round[z9x, 10.^(Floor[Log10[Abs[z9x]]] - 2)]]]]]];
z9npOf[z9p_] := Module[{z9io = InteractionOrder /. Flatten[{z9p[[2]]}]},
  If[z9io === InteractionOrder, 0, Total[Cases[If[MatchQ[z9io, {_Symbol, _Integer}], {z9io}, z9io], {NP, z9n_Integer} :> z9n]]]];
z9ext = Select[M$Parameters, (ParameterType /. Flatten[{#[[2]]}]) === External && z9npOf[#] > 0 &];
SeedRandom[20261108];
z9c = (#[[1]] -> {z9npOf[#], RandomReal[{-1, 1}] 3^z9npOf[#]}) & /@ z9ext;
Print["[fermion] coefficients on: ", Length[z9c], " (", Counts[z9c[[All, 2, 1]]], " by NP order)"];
z9params := Join[First /@ M$Parameters, {MZ, MH}];
(* every parameter and component at the point t, from validate/geo_numeric.m: UpdateParameters takes minutes
   per call here, and NumericalValue leaves the off-diagonal Yukawas, zero through their Definitions, unevaluated *)
Get[$root <> "/validate/geo_numeric.m"];
z9rulesAt[z9t_] := z8numRules[Join[{Lam -> 1000., Lam6 -> 1000.}, (#[[1]] -> #[[2, 2]] z9t^#[[2, 1]]) & /@ z9c]];
(* FeynmanRules writes a flavour index as Index[Generation, 2], the rules as yu[2, 2] *)
z9num[z9e_, z9r_] := Expand[z9e /. Index[_, z9i_Integer] :> z9i /. z9r];
z9coef[z9x_] := Which[NumericQ[z9x], Abs[N[z9x]], Head[z9x] === Times, Abs[N[Times @@ Cases[z9x, _?NumericQ, {1}]]], True, 1.];
z9mag[z9y_, z9kin_] := Module[{z9l},
  z9l = Select[If[Head[z9y] === Plus, List @@ z9y, {z9y}], If[z9kin, ! FreeQ[#, FV | SP | SlashedP] &, FreeQ[#, FV | SP | SlashedP] &]];
  If[z9l === {} || z9y === 0, 0., Max[z9coef /@ z9l]]];
z9left[z9e_] := Intersection[Cases[z9e, _Symbol, {0, Infinity}, Heads -> True], z9params];

(* a fermionic block holds the general flavour coefficient z8F2[f1, f2] of its operator, which the UFO writer
   replaces block by block by the flavour structures of the model (gen_geo<N>_flavour_rules.m), the structures
   the compensation in LYukawa is written with.  The same rules act here on the Lagrangian of each block, and
   a general coefficient left over stops the check, since it has no value and would be read as a factor one. *)
z8FlavourRules = <||>; z8FlavourPlaceholders = {};   (* as validate/fr_writeufo.wls starts them *)
Get[StringReplace[z9gen, ".fr" -> "_flavour_rules.m"]];
z9blockL[z9b_] := If[KeyExistsQ[z8FlavourRules, z9b], Symbol[z9b] /. z8FlavourRules[z9b], Symbol[z9b]];
z9L = LSM + Total[z9blockL /@ z9blocks];
If[z8FlavourPlaceholders === {}, Print["[fermion] ABORT: no flavour placeholders declared by the rules"]; Quit[1]];
If[! FreeQ[z9L, Alternatives @@ z8FlavourPlaceholders],
  Print["[fermion] ABORT: general flavour coefficients left in the Lagrangian: ", Select[z8FlavourPlaceholders, ! FreeQ[z9L, #] &]]; Quit[1]];
Print["[fermion] flavour structures of the model on the blocks ", Select[z9blocks, KeyExistsQ[z8FlavourRules, #] &]];
z9q = GetQuadraticTerms[z9L];
(* the spectator G0 carries no momentum, as in validate/check_bilinears.wls *)
z9atrest[{z9p_, z9e_}] := Module[{z9g = First[Select[z9p, #[[1]] === G0 &]][[2]], z9o, z9a, z9b},
  z9o = DeleteCases[z9p[[All, 2]], z9g]; {z9a, z9b} = z9o;
  {z9p, Expand[z9e /. {FV[z9g, _] -> 0, SP[z9g, _] -> 0, SP[_, z9g] -> 0} /. {FV[z9b, z9m_] :> -FV[z9a, z9m]}]}];
z9isF[z9x_] := FermionQ[z9x] === True && GhostFieldQ[z9x] =!= True;
z9vf = z9atrest /@ Select[FeynmanRules[G0 z9q, FlavorExpand -> True, ScreenOutput -> False],
  Length[#[[1]]] == 3 && Count[#[[1, All, 1]], _?z9isF] == 2 &];
Print["[fermion] two-point fermion structures: ", Sort[DeleteCases[#[[1, All, 1]], G0] & /@ z9vf]];
If[z9vf === {}, Print["[fermion] ABORT: no fermion two-point term"]; Quit[1]];
z9ts = {1/2, 1/4, 1/8};
z9r0 = z9rulesAt[0];
z9rs = z9rulesAt /@ z9ts;
Module[{z9l = Union @@ (z9left[z9num[#[[2]], z9rs[[1]]]] & /@ z9vf)},
  If[z9l =!= {}, Print["[fermion] ABORT: parameters with no numerical value: ", z9l]; Quit[1]]];
z9want = 2^(z9N + 1);
z9bad = 0; z9live = 0;
z9scale = Max[z9mag[z9num[#[[2]], z9r0], False] & /@ z9vf];
Do[Module[{z9k = DeleteCases[z9v[[1, All, 1]], G0], z9e0 = z9num[z9v[[2]], z9r0], z9m, z9sc},
   Do[z9m = z9mag[Expand[z9num[z9v[[2]], #] - z9e0], z9kin] & /@ z9rs;
      (* an off-diagonal pair has no mass at t = 0, and its residue is measured against the largest mass *)
      z9sc = If[z9kin, 1., If[z9mag[z9e0, False] > 0., z9mag[z9e0, False], z9scale]];
      If[Max[z9m] == 0., Continue[]];
      If[! z9kin, z9live++];
      Print["[twopoint] ", z9k, If[z9kin, "  kinetic", "  mass   "], "  mass at t = 0: ", z9f[z9mag[z9e0, False]],
            "   residue/mass at t = 1/2, 1/4, 1/8: ", z9f /@ (z9m/z9sc),
            "   ratios ", If[z9m[[2]] > 0 && z9m[[3]] > 0, z9f /@ {z9m[[1]]/z9m[[2]], z9m[[2]]/z9m[[3]]}, "exact zero"]];
      If[z9m[[3]] > 10^-13 z9sc && z9m[[2]]/z9m[[3]] < 0.75 z9want, z9bad++], {z9kin, {True, False}}]], {z9v, z9vf}];
Print["[fermion] ", z9live, " fermion mass terms move with the coefficients; the others are exact zeros"];
If[z9live == 0, Print["[fermion] ABORT: nothing to test"]; Quit[1]];
Print["[fermion] ", If[z9bad == 0, "PASS: every fermion two-point residue falls as t^" <> ToString[z9N + 1],
  ToString[z9bad] <> " fermion two-point residues fall slower than t^" <> ToString[z9N + 1]]];
Print["[alldone]"];
