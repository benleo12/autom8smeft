(* validate/v5_sweep.wls  --  V5, FeynRules half.

   CheckHermiticity on every generated Lagrangian block, plus the vertex count so that a
   block that is "Hermitian" only because it produced nothing is not mistaken for a pass.

   Usage:
     wolframscript -file v5_sweep.wls <shard> <nshards> [nblocks] [nkernels]

   Each shard loads the model once and walks blocks  shard, shard+nshards, ...  Results are
   appended one line at a time to  tests/v5/v5_results_<shard>.txt  as

     blk <n> | terms <t> | vertices <v> | nonhermitian <h> | tEval <s> | tVert <s> | tHerm <s>

   so a killed run still leaves everything it had finished.  Grep the log for [alldone]. *)

$root = "${DIM8_ROOT:-.}";
args = Rest[$ScriptCommandLine];
shard = ToExpression[args[[1]]];
nshards = ToExpression[args[[2]]];
nblocks = If[Length[args] >= 3, ToExpression[args[[3]]], 113];
FR$NKernels = If[Length[args] >= 4, ToExpression[args[[4]]], 3];
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";

Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];

outdir = $root <> "/tests/v5";
If[! DirectoryQ[outdir], CreateDirectory[outdir]];
outfile = outdir <> "/v5_results_" <> ToString[shard] <> ".txt";
If[FileExistsQ[outfile], DeleteFile[outfile]];
emit[s_String] := (Print[s]; PutAppend[OutputForm[s], outfile]);

t0 = AbsoluteTime[];
LoadModel["base.fr", "gen.fr"];
Print["[time] LoadModel: ", Round[AbsoluteTime[] - t0, 0.1], " s;  parameters: ", Length[M$Parameters]];

runblk[n_Integer] := Module[{nm, tt, lagX, vX, hX, te, tv, th},
  nm = "L8blk" <> ToString[n];
  tt = AbsoluteTime[]; lagX = Symbol[nm]; te = Round[AbsoluteTime[] - tt, 0.1];
  tt = AbsoluteTime[]; vX = FeynmanRules[lagX, ScreenOutput -> False]; tv = Round[AbsoluteTime[] - tt, 0.1];
  tt = AbsoluteTime[]; hX = CheckHermiticity[lagX, ScreenOutput -> False]; th = Round[AbsoluteTime[] - tt, 0.1];
  emit["blk " <> ToString[n] <> " | terms " <> ToString[Length[lagX]] <>
       " | vertices " <> ToString[Length[vX]] <> " | nonhermitian " <> ToString[Length[hX]] <>
       " | tEval " <> ToString[te] <> " | tVert " <> ToString[tv] <> " | tHerm " <> ToString[th]];
  ClearAll[lagX, vX, hX];
];

Do[runblk[n], {n, shard, nblocks, nshards}];
Print["[alldone] shard ", shard, " total ", Round[AbsoluteTime[] - t0, 0.1], " s"];
