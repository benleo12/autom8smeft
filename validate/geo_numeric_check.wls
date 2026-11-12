(* validate/geo_numeric_check.wls N  --  does validate/geo_numeric.m give the parameters of the model of order N
   the values FeynRules gives them?

   Loads the model as validate/check_fermion_masses_geo.wls does, switches every coefficient with an NP
   order p on at c_p/2^p (the point t = 1/2 of the checks), and compares z8numRules with UpdateParameters and
   NumericalValue, parameter by parameter and component by component, to ten digits.  A component that
   NumericalValue leaves unevaluated (one that is zero only through the Definitions of its matrix) is
   counted apart, with the value z8numRules gives it.

     DIM8_ROOT=... wolframscript -file validate/geo_numeric_check.wls 2 *)
$root = If[Environment["DIM8_ROOT"] === $Failed, ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9N = ToExpression[$ScriptCommandLine[[2]]];
z9gen = "gen_geo" <> ToString[Max[z9N, 2]] <> ".fr";
z9gen = If[FileExistsQ[z9gen], z9gen, "gen_geo4.fr"];
z9base = "base_geo" <> ToString[z9N] <> "_mw.fr";
z9miss = Select[{z9base, "dim6_geo.fr", z9gen, "gen.fr"}, ! FileExistsQ[#] &];
If[z9miss =!= {}, Print["[numcheck] ABORT: not in ", Directory[], ": ", z9miss]; Exit[1]];
LoadModel[z9base, "dim6_geo.fr", z9gen, "gen.fr"];
If[z8geoN =!= z9N, Print["[numcheck] ABORT: the base is of order ", z8geoN]; Exit[1]];
Get[$root <> "/validate/geo_numeric.m"];
z9npOf[z9p_] := Module[{z9io = InteractionOrder /. Flatten[{z9p[[2]]}]},
  If[z9io === InteractionOrder, 0, Total[Cases[If[MatchQ[z9io, {_Symbol, _Integer}], {z9io}, z9io], {NP, z9n_Integer} :> z9n]]]];
SeedRandom[20261108];
z9set = Join[{Lam -> 1000.}, (#[[1]] -> RandomReal[{-1, 1}] 3^z9npOf[#]/2^z9npOf[#]) & /@
   Select[M$Parameters, z8numExternalQ[#] && z9npOf[#] > 0 &]];
Print["[numcheck] ", Length[z9set] - 1, " coefficients set"];
{z9tf, z9mine} = AbsoluteTiming[z8numRules[z9set]];
z9mine = Association[z9mine];
Print["[numcheck] z8numRules: ", Length[z9mine], " values in ", Round[z9tf, 0.1], " s"];
{z9tu, z9u} = AbsoluteTiming[UpdateParameters @@ z9set];
Print["[numcheck] UpdateParameters: ", Round[z9tu, 0.1], " s"];
z9all = Join @@ (If[z8numMatrixQ[#], z8numComponents[#], {#[[1]]}] & /@ M$Parameters);
z9bad = {}; z9unev = {}; z9same = 0;
Do[Module[{z9fr = NumericalValue[z9p], z9me = Lookup[z9mine, z9p, Missing[]]},
   Which[
     ! NumericQ[z9fr], AppendTo[z9unev, z9p -> z9me],
     MissingQ[z9me] || Abs[z9fr - z9me] > 10^-10 Max[Abs[z9fr], 10^-4], AppendTo[z9bad, {z9p, z9fr, z9me}],
     True, z9same++]], {z9p, z9all}];
Print["[numcheck] agree to ten digits: ", z9same, " of ", Length[z9all]];
Print["[numcheck] left unevaluated by NumericalValue: ", Length[z9unev], ", all zero here: ", AllTrue[Values[Association[z9unev]], # == 0 &],
      "  e.g. ", Take[z9unev, UpTo[6]]];
Print["[numcheck] ", If[z9bad === {}, "PASS", "DIFFER: " <> ToString[Length[z9bad]] <> " " <> ToString[Take[z9bad, UpTo[10]]]]];
Exit[If[z9bad === {}, 0, 1]]
