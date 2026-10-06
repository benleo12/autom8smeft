(* validate/merge_legs.wls -- join the two halves of a split block into the cache.
   A dual-dual G^4 block (426, 428, 432) is built in two runs: build/vertices_cap6/<block>.mx holds
   every vertex with up to six legs (DIM8_MAXLEGS=6), build/vertices_hi/<block>.mx every vertex with
   seven or eight legs (DIM8_MINLEGS=7, checkpointed).  FeynmanRules' MaxParticles/MinParticles
   partition the vertex list by leg count, so the union is the full block; MergeVertices adds
   nothing across the two (no vertex has both at most six and at least seven legs), it only sorts.
   Writes build/vertices/<block>.mx and .status (nonhermitian -1: the finish pass checks it) and
   refuses to overwrite a cache entry that is not itself a capped one.
   Run: DIM8_ROOT=<repo> [DIM8_VDIR=<cache>] wolframscript -file validate/merge_legs.wls 426 *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
FR$PathOverride = $root <> "/external/feynrules/feynrules-current"; FR$NKernels = 0;
vdir = If[Environment["DIM8_VDIR"] === $Failed, $root <> "/build/vertices", Environment["DIM8_VDIR"]];
lo = $root <> "/build/vertices_cap6"; hi = $root <> "/build/vertices_hi";
n = ToExpression[$ScriptCommandLine[[2]]]; nm = "L8op" <> ToString[n];
Get[$root <> "/tests/fr_env/fr_headless_init.m"]; SetDirectory[$root <> "/tests/gen_smoke"]; LoadModel["base.fr", "gen.fr"];
legs[v_] := Length[v[[1]]];
Get[lo <> "/" <> nm <> ".mx"]; vlo = FR$Vert; Clear[FR$Vert];
Get[hi <> "/" <> nm <> ".mx"]; vhi = FR$Vert; Clear[FR$Vert];
Print[nm, ": capped part ", Length[vlo], " vertices (legs ", Union[legs /@ vlo], "), high part ", Length[vhi], " vertices (legs ", Union[legs /@ vhi], ")"];
If[Max[legs /@ vlo] > 6 || (vhi =!= {} && Min[legs /@ vhi] < 7), Print["ABORT: the halves overlap in leg count"]; Quit[2]];
st = vdir <> "/" <> nm <> ".status";
If[FileExistsQ[st] && !StringContainsQ[Import[st, "Text"], "maxlegs 6"], Print["ABORT: the cache entry is not a capped block, not overwriting: ", Import[st, "Text"]]; Quit[2]];
FR$Vert = MergeVertices[Join[vlo, vhi]];
DumpSave[vdir <> "/" <> nm <> ".mx", FR$Vert];
slo = Import[lo <> "/" <> nm <> ".status", "Text"]; shi = Import[hi <> "/" <> nm <> ".status", "Text"];
tv[s_] := ToExpression[StringCases[s, "tVert " ~~ x : NumberString :> x][[1]]];
Export[st, nm <> " | vertices " <> ToString[Length[FR$Vert]] <> " | rawvertices " <> ToString[Length[vlo] + Length[vhi]] <> " | nonhermitian -1 | tEval 0 | tVert " <>
  ToString[tv[slo] + tv[shi]] <> " | tHerm 0 | merged legs<=6 + legs>=7", "Text"];
Print["written ", nm, ": ", Import[st, "Text"]];
