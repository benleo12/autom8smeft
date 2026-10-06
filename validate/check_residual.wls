(* validate/check_residual.wls -- decide a Hermiticity flag at the vertex level.
   The worker's Hermiticity test is FeynmanRules[L - HC[L]] per chunk, canonicalised, colour
   polynomials tested exactly; what survives is counted as non-Hermitian.  A survivor can still
   be zero through a Lorentz identity (Schouten: five antisymmetrised indices vanish in 4D, the
   case for operators with a dual field strength) or through momentum conservation, which the
   syntactic canonicalisation cannot see.  This script loads the residual saved by
   DIM8_HERMDUMP=1 (<vdir>/<block>.herm.mx: z9rawH raw, z9resid survivors) and evaluates every
   survivor numerically: explicit momenta summing to zero (random integers, several seeds),
   EVERY assignment of the external Lorentz indices, Lorentz dummies summed against the metric,
   ME/FV/SP/Eps as numbers, then the colour polynomial that remains is contracted exactly with
   the worker's tensor test.  Dirac structures (Ga, ProjP/M, Sig, TensDot, SlashedP) stay
   symbolic with their Lorentz arguments evaluated, so identities of the Clifford algebra are
   NOT used: a survivor reported nonzero here can still vanish by a gamma-matrix identity.  A
   nonzero polynomial in the momenta is missed by all seeds with probability at most
   degree/19 per seed (Schwartz-Zippel, integers in [-9, 9]); with DIM8_SEEDS seeds (default 4)
   that is below 1e-3 for degree three and is printed.  Self-test first: a Schouten identity
   must vanish and its one-sign-flipped variant must not.
   Run: DIM8_ROOT=<repo> DIM8_VDIR=<cache> DIM8_BLOCK=L8op73 wolframscript -file validate/check_residual.wls *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
vdir = If[Environment["DIM8_VDIR"] === $Failed, $root <> "/build/vertices", Environment["DIM8_VDIR"]];
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";   (* the same FeynRules install as the worker, not the 2.3.34 fallback of the init file *)
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
