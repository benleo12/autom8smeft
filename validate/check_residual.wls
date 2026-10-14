(* validate/check_residual.wls -- decide a Hermiticity flag at the vertex level.
   The worker's Hermiticity test is FeynmanRules[L - HC[L]] per chunk, canonicalised, with the
   colour polynomials tested exactly.  A survivor of these steps can still be zero through a
   Lorentz identity (Schouten: five antisymmetrised indices vanish in 4D, the case for
   operators with a dual field strength) or through momentum conservation, which the syntactic
   canonicalisation cannot see, so the worker also applies its Lorentz/Dirac zero test before
   it counts a vertex as non-Hermitian.  This script shows that decision vertex by vertex.  It
   loads the residual saved by
   DIM8_HERMDUMP=1 (<vdir>/<block>.herm.mx: z9rawH raw, z9resid survivors) and evaluates every
   survivor with the worker's Lorentz/Dirac zero test, z9lorentzZeroQ: the momenta are symbols
   with the last one fixed by momentum conservation, every external Lorentz index is contracted
   with a symbolic vector, Lorentz dummies are summed against the metric, ME/FV/SP/Eps become
   components, and the Dirac structures (Ga, ProjP/M, Sig, TensDot, SlashedP) become explicit
   4x4 matrices with the external spin indices enumerated.  The colour polynomial that remains
   is contracted exactly with the worker's tensor test.  Nothing is sampled, so a survivor
   reported nonzero is a genuine residual; a structure the test does not support is reported
   as such and stays flagged.  The worker's load-time self-test runs first: among other cases,
   a Schouten identity must vanish and its one-sign-flipped variant must not.
   Run: DIM8_ROOT=<repo> DIM8_VDIR=<cache> DIM8_BLOCK=L8op73 wolframscript -file validate/check_residual.wls *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
vdir = If[Environment["DIM8_VDIR"] === $Failed, $root <> "/build/vertices", Environment["DIM8_VDIR"]];
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";   (* the same FeynRules install as the worker, not the default path of the init file *)
FR$NKernels = 0;
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"]; LoadModel["base.fr", "gen.fr"];
z8w = Import[$root <> "/validate/fr_worker.wls", "Text"];
z8a = StringPosition[z8w, "canonEps = "][[1, 1]]; z8b = StringPosition[z8w, "(* ---- term-wise evaluation"][[1, 1]];
ToExpression[StringTake[z8w, {z8a, z8b - 1}]];   (* canonicalisation, the exact colour tensor test *)
If[!TrueQ[z8colourTablesOK], Print["colour tables failed"]; Quit[3]];
(* the evaluator z9lorentzZeroQ and its load-time self-test come from the worker's region loaded above *)
If[Environment["DIM8_BLOCK"] === $Failed, Print["no DIM8_BLOCK given; self-test only"]; Quit[0]];
blk = Environment["DIM8_BLOCK"];
Get[vdir <> "/" <> blk <> ".herm.mx"];
Print[blk, ": raw residual vertices ", Length[z9rawH], ", survivors ", Length[z9resid]];
nReal = 0;
Do[Print["  coupling: ", StringTake[ToString[InputForm[v[[2]]]], UpTo[700]]];
   Print["  ", v[[1, All, 1]], "  terms ", Length[If[Head[Expand[v[[2]]]] === Plus, List @@ Expand[v[[2]]], {v[[2]]}]],
     "  heads ", Union[Cases[v[[2]], (Ga | ProjP | ProjM | Sig | TensDot | SlashedP | Eps | T | f | dSUN)[___], Infinity][[All, 0]]]];
   Module[{zr = z9lorentzZeroQ[v]}, Which[zr === True, Print["    ZERO (Lorentz/Dirac identity or momentum conservation)"], zr === $Failed, nReal++; Print["    UNSUPPORTED structure, stays flagged"], True, nReal++; Print["    NONZERO: a genuine residual"]]],
   {v, z9resid}];
Print[blk, ": survivors nonzero at the Lorentz/Dirac level ", nReal, " of ", Length[z9resid]];
