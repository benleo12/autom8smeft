(* validate/compare_blocks_exact.wls -- exact vertex-by-vertex equality of two cached blocks.
   Usage: DIM8_ROOT=<repo> wolframscript -file validate/compare_blocks_exact.wls A.mx B.mx
   Every vertex of A must have a vertex in B with the same fields (and vice versa) whose coupling
   difference vanishes under the worker's own exact tests: canonicalisation, the tensor colour
   test and the Lorentz/Dirac polynomial test (symbolic momenta and polarisations, explicit
   Dirac matrices).  No sampling and no cap on the colour assignments, so six-gluon vertices are
   compared exactly too (compare_vertex_numeric.wls gives up above 4096 colour assignments).
   Exit code 0 when the blocks agree, 1 otherwise. *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
(* resolve the two files BEFORE the model load changes the working directory: relative paths
   silently failed to open afterwards and the script compared two empty lists as "EQUAL" (2026-09-05) *)
{fA, fB} = AbsoluteFileName /@ $ScriptCommandLine[[2 ;; 3]];
If[MemberQ[{fA, fB}, $Failed], Print["COMPARE FAILED: file not found ", $ScriptCommandLine[[2 ;; 3]]]; Quit[2]];
FR$PathOverride = $root <> "/external/feynrules/feynrules-current"; FR$NKernels = 0;
Get[$root <> "/tests/fr_env/fr_headless_init.m"]; SetDirectory[$root <> "/tests/gen_smoke"]; LoadModel["base.fr", "gen.fr"];
z8w = Import[$root <> "/validate/fr_worker.wls", "Text"];
z8a = StringPosition[z8w, "canonEps = "][[1, 1]]; z8b = StringPosition[z8w, "(* ---- term-wise evaluation"][[1, 1]];
ToExpression[StringTake[z8w, {z8a, z8b - 1}]];
loadVerts[f_] := Module[{v}, Clear[FR$Vert]; If[Get[f] === $Failed, Print["COMPARE FAILED: cannot read ", f]; Quit[2]];
  v = FR$Vert; Clear[FR$Vert];
  If[Head[v] =!= List || v === {}, Print["COMPARE FAILED: no vertex list in ", f]; Quit[2]]; v];
vA = loadVerts[fA]; vB = loadVerts[fB];
key[v_] := Sort[v[[1, All, 1]]];
Print["A: ", Length[vA], " vertices ", Tally[key /@ vA] // InputForm];
Print["B: ", Length[vB], " vertices ", Tally[key /@ vB] // InputForm];
ok = True;
If[Sort[key /@ vA] =!= Sort[key /@ vB], Print["FIELD CONTENT DIFFERS"]; ok = False];
(* match by field content; when a field content appears more than once, try all pairings *)
Do[cands = Select[vB, key[#] === key[a] &];
   (* same leg order is needed for the coupling difference: align B's legs to A's *)
   found = False;
   Do[If[a[[1, All, 1]] =!= b[[1, All, 1]], Continue[]];
      d = canonCoup[a[[2]] - b[[2]]];
      If[d === 0 || colourZeroQ[d] || z9lorentzZeroQ[{a[[1]], d}] === True, found = True; Break[]], {b, cands}];
   Print[If[found, "same    ", "DIFFERS "], a[[1, All, 1]]]; ok = ok && found,
   {a, vA}];
Print[If[ok, "BLOCKS EQUAL", "BLOCKS DIFFER"]]; If[!ok, Quit[1]];
