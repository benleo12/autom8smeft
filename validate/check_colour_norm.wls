(* validate/check_colour_norm.wls -- the numeric colour tensors of fr_worker.wls must satisfy their
   defining identities: f^{123} = 1, f^{147} = 1/2, d^{118} = 1/Sqrt[3], [T^a,T^b] = i f^{abc} T^c,
   {T^a,T^b} = delta^{ab}/3 + d^{abc} T^c, with T = lambda/2.  Added 2026-09-04 after the tables
   were found twice too large.  Run: DIM8_ROOT=<repo> wolframscript -file validate/check_colour_norm.wls *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]]; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";   (* the same FeynRules install as the worker, not the 2.3.34 fallback of the init file *)
FR$NKernels = 0; Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"]; LoadModel["base.fr", "gen.fr"];
z8w = Import[$root <> "/validate/fr_worker.wls", "Text"];
z8a = StringPosition[z8w, "gellMann = "][[1, 1]]; z8b = StringPosition[z8w, "canonVerts[z8v_List] :="][[1, 1]];
ToExpression[StringTake[z8w, {z8a, z8b - 1}]];
tt[a_] := gellMann[[a]]/2;
Print["f123 = ", fNum[[1, 2, 3]], "  f147 = ", fNum[[1, 4, 7]], "  d118 = ", Simplify[dNum[[1, 1, 8]]], " (expect 1, 1/2, 1/Sqrt[3])"];
comm = Max[Abs[Flatten[Table[tt[a].tt[b] - tt[b].tt[a] - I Sum[fNum[[a, b, c]] tt[c], {c, 8}], {a, 8}, {b, 8}]]]] // Simplify;
anti = Max[Abs[Flatten[Table[tt[a].tt[b] + tt[b].tt[a] - IdentityMatrix[3]/3 KroneckerDelta[a, b] - Sum[dNum[[a, b, c]] tt[c], {c, 8}], {a, 8}, {b, 8}]]]] // Simplify;
Print["commutator identity residual: ", comm, "   anticommutator identity residual: ", anti];
Print[If[comm == 0 && anti == 0 && fNum[[1, 2, 3]] == 1, "NORMALISATION PASS", "NORMALISATION FAIL"]];
If[!(comm == 0 && anti == 0 && fNum[[1, 2, 3]] == 1), Quit[1]];
