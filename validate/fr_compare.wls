#!/usr/bin/env wolframscript
(* ======================================================================================
   validate/fr_compare.wls  --  vertex-by-vertex equality of generated vs reference
   ======================================================================================
   Usage:
     wolframscript -file validate/fr_compare.wls <base.fr> <generated.fr> <pairs.m> [nkernels]

   <base.fr>      : the base model, e.g. tests/gen_smoke/base.fr.  The reference blocks are
                    defined by this file or by a shim listed with <generated.fr> (for the
                    SmeftFR comparison validate/smeftfr_shim.fr, see validate/smeftfr_pairs.m)
   <generated.fr> : fragment written by gen/emit_fr.py (M$Parameters Join + L8op blocks)
   <pairs.m>      : a Mathematica list of
                    { {refBlock, refWC, genBlock, genWC, normalisation}, ... }
                    meaning   refBlock|_{refWC}  ==  normalisation * genBlock|_{genWC -> refWC, Lam -> 1}
   For every pair we evaluate both blocks, form the difference and compute the Feynman
   rules of the difference.  The test passes when no vertex survives.
   Exit code 0 on success, 1 on any failure; a JSON report is written next to pairs.m.
   ====================================================================================== *)

args = Rest[$ScriptCommandLine];
If[Length[args] < 3, Print["usage: fr_compare.wls base.fr generated.fr pairs.m [nkernels]"]; Exit[1]];
{baseFile, genFile, pairsFile} = Take[args, 3];
FR$NKernels = If[Length[args] >= 4, ToExpression[args[[4]]], 0];

(* the init script needs FR$PathOverride to find FeynRules; without it the load only works
   on a machine where FeynRules is installed under the user's Mathematica directory *)
z9root = If[Environment["DIM8_ROOT"] === $Failed,
  ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
FR$PathOverride = FileNameJoin[{z9root, "external", "feynrules", "feynrules-current"}];
If[! DirectoryQ[FR$PathOverride], Print["[abort] FeynRules not found at ", FR$PathOverride]; Exit[1]];
Get[FileNameJoin[{z9root, "tests", "fr_env", "fr_headless_init.m"}]];

(* resolve every path BEFORE SetDirectory: afterwards a relative argument no longer
   resolves against the directory the user invoked the script from *)
(* <generated.fr> may be a comma-separated list, so that a comparison against a third-party
   implementation can add a shim file defining that package's field aliases and parameters *)
baseAbs = ExpandFileName[baseFile];
genAbsList = ExpandFileName /@ StringSplit[genFile, ","];
pairsAbs = ExpandFileName[pairsFile];
Do[If[! FileExistsQ[z9f], Print["[abort] file not found: ", z9f]; Exit[1]], {z9f, Join[{baseAbs}, genAbsList, {pairsAbs}]}];
SetDirectory[DirectoryName[baseAbs]];
Print["[compare] loading ", Length[genAbsList] + 1, " model files"];
LoadModel @@ Join[{baseAbs}, genAbsList];

$HistoryLength = 0;   (* do not retain every intermediate expression *)

(* --------------------------------------------------------------------------------------
   Deciding that a vertex vanishes.

   PossibleZeroQ[Simplify[...]] is far too weak here.  The difference of two correct
   implementations of the same CP-odd operator is built from Eps and momenta and vanishes
   only through momentum conservation and Schouten identities, which Simplify does not
   apply.  On Q_{G^2H^4}^{(2)}, for example, 9 raw vertices survive Simplify and 4 of them
   survive even the build worker's canonicalisation, yet all 4 are identically zero.

   So evaluate the Lorentz algebra numerically: give the legs explicit momenta that sum to
   zero, assign the free Lorentz indices explicit values, sum every dummy index over 0..3
   against the Minkowski metric, and turn Eps into the Levi-Civita symbol.  A structure that is not identically zero survives random momenta
   with probability one.
   -------------------------------------------------------------------------------------- *)
zEta = DiagonalMatrix[{1, -1, -1, -1}];
zGell = {{{0,1,0},{1,0,0},{0,0,0}}, {{0,-I,0},{I,0,0},{0,0,0}}, {{1,0,0},{0,-1,0},{0,0,0}},
  {{0,0,1},{0,0,0},{1,0,0}}, {{0,0,-I},{0,0,0},{I,0,0}}, {{0,0,0},{0,0,1},{0,1,0}},
  {{0,0,0},{0,0,-I},{0,I,0}}, {{1,0,0},{0,1,0},{0,0,-2}}/Sqrt[3]};
zfN = Table[-2 I Tr[(zGell[[za]].zGell[[zb]] - zGell[[zb]].zGell[[za]]).zGell[[zc]]]/8, {za,8},{zb,8},{zc,8}] // Simplify;
zdN = Table[ 2 Tr[(zGell[[za]].zGell[[zb]] + zGell[[zb]].zGell[[za]]).zGell[[zc]]]/8, {za,8},{zb,8},{zc,8}] // Simplify;

(* Evaluate BOTH the colour and the Lorentz algebra numerically.  Colour first (one
   assignment of the external colour/gluon indices, dummies summed, T/f/d/delta and the colour
   Eps replaced by numbers), then Lorentz (explicit momenta summing to zero, free indices
   assigned, dummies summed against the Minkowski metric, the Lorentz Eps replaced by the
   Levi-Civita symbol).  The two Eps are told apart by the type of their indices. *)
(* Every free index is contracted with a dense random vector of its own, a four-vector for a Lorentz
   index and an eight- or three-vector for a colour index, and the momenta are random and sum to zero.
   A vertex is multilinear in those vectors and polynomial in the momenta, so a nonzero vertex is
   nonzero at such a point with probability one.  Single random values of the indices would not do.  The
   tensors are sparse: g^{mu nu} g^{rho sigma} - g^{mu rho} g^{nu sigma} is zero at most values of its
   indices, and two gluon indices hit a nonzero delta one time in eight, so a test that draws index
   values can pass a vertex that differs.  Nothing is enumerated, so no colour space is too large.
   Every FeynRules tensor head is swapped for an inert private head BEFORE any integer is
   substituted: FeynRules' own contraction rules fire on equal integers as if they were a
   summed pair (Eps[a,b,2,4] Eps[c,d,2,4] auto-reduces to metrics), which would corrupt the
   evaluation whenever two dummy indices take the same value.  Dummies are summed TERM BY
   TERM: summing a dummy over the whole expression multiplies every term that does not contain
   it by the metric trace (-2 for Lorentz, 3 or 8 for colour), so a difference of two
   expressions with differently named dummies could never cancel.  The arithmetic is exact, over the
   rationals, sqrt 3 and i.  The other parameters take random rational values, since the two sides of a
   pair hold them as the same symbols and no relation between them may be used. *)
zInert = {Eps -> zEPS, ME -> zME, FV -> zFV, SP -> zSP, T -> zT, f -> zF, dSUN -> zD, IndexDelta -> zDEL};
zSumDummies[ze_, zdumsOf_, zdim_, zweight_] := Module[{zterms = If[Head[Expand[ze]] === Plus, List @@ Expand[ze], {Expand[ze]}]},
  Total[Function[zt, Module[{zt2 = zt, zds = zdumsOf[zt]},
     Do[zt2 = Sum[(zt2 /. zd -> zv) zweight[zd, zv], {zv, zdim[zd]}], {zd, zds}]; zt2]] /@ zterms]];
zDense[zc_, zn_Integer, zseed_] := Module[{ze = zc /. zInert, zp, zext, zcv, zlor, zlv, zcol, zlr, zF3, zD3, zT3, zpar},
  SeedRandom[zseed];
  zp = Table[RandomInteger[{-9, 9}, 4], {zn - 1}]; AppendTo[zp, -Total[zp]];
  zext = Union[Cases[ze, Index[Colour | Gluon, Ext[_]], Infinity]];
  zcv = Association[Thread[zext -> (RandomInteger[{-9, 9}, If[#[[1]] === Colour, 3, 8]] & /@ zext)]];
  ze = zSumDummies[ze, Function[zt, Union[Cases[zt, Index[Colour | Gluon, _Symbol], Infinity]]], Function[zd, If[zd[[1]] === Colour, 3, 8]], Function[{zd, zv}, 1]];
  zcol[za_Integer, zdim_] := UnitVector[zdim, za];
  zcol[za_, _] := zcv[za];
  zF3[za_, zb_, zk_] := zF3[za, zb, zk] = (zfN . zcol[zk, 8]) . zcol[zb, 8] . zcol[za, 8];
  zD3[za_, zb_, zk_] := zD3[za, zb, zk] = (zdN . zcol[zk, 8]) . zcol[zb, 8] . zcol[za, 8];
  zT3[za_, zi_, zj_] := zT3[za, zi, zj] = zcol[zi, 3] . (Total[zcol[za, 8] zGell]/2) . zcol[zj, 3];
  ze = ze /. {zF[za_, zb_, zk_] :> zF3[za, zb, zk], zD[za_, zb_, zk_] :> zD3[za, zb, zk], zT[za_, zi_, zj_] :> zT3[za, zi, zj],
              zDEL[zi_Integer, zj_Integer] :> KroneckerDelta[zi, zj], zDEL[zi_Integer, zj_] :> zcv[zj][[zi]],
              zDEL[zi_, zj_Integer] :> zcv[zi][[zj]], zDEL[zi_, zj_] :> zcv[zi] . zcv[zj],
              zEPS[za_, zb_, zk_] :> Det[{zcol[za, 3], zcol[zb, 3], zcol[zk, 3]}]};
  ze = ze /. Index[Lorentz, zx_] :> zx;
  zlor = Union[Cases[ze, Ext[_], Infinity]];
  zlv = Association[Thread[zlor -> (RandomInteger[{-9, 9}, 4] & /@ zlor)]];
  ze = zSumDummies[ze, Function[zt, Union[Cases[zt, (zFV[_, zs_Symbol] | zME[zs_Symbol, _] | zME[_, zs_Symbol] | zEPS[___, zs_Symbol, ___]) :> zs, Infinity]]], Function[zd, 4], Function[{zd, zv}, zEta[[zv, zv]]]];
  zlr[zm_Integer] := UnitVector[4, zm];
  zlr[zm_] := zlv[zm];
  ze = ze /. {zSP[zi_Integer, zj_Integer] :> zp[[zi]] . zEta . zp[[zj]],
              zFV[zi_, zm_Integer] :> zp[[zi, zm]], zFV[zi_, zm_] :> zp[[zi]] . zlv[zm],
              zME[zi_Integer, zj_Integer] :> zEta[[zi, zj]], zME[zi_Integer, zj_] :> zEta[[zi, zi]] zlv[zj][[zi]],
              zME[zi_, zj_Integer] :> zEta[[zj, zj]] zlv[zi][[zj]], zME[zi_, zj_] :> zlv[zi] . zEta . zlv[zj],
              zEPS[za_, zb_, zk_, zd2_] :> Det[zlr /@ {za, zb, zk, zd2}]};
  zpar = Union[Cases[ze, zx_Symbol /; !NumericQ[zx], {0, Infinity}, Heads -> False]];
  ze = ze /. Thread[zpar -> (Rational[RandomInteger[{1, 97}], RandomInteger[{1, 97}]] & /@ zpar)];
  Expand[ze]];
zVanishesQ[zvert_] := Module[{zn = Length[zvert[[1]]]},
  AllTrue[{1, 2, 3}, zDense[zvert[[2]], zn, #] === 0 &]];

(* The test must catch a difference and must pass an identity, and it stops here if it does not. *)
zL[k_] := Index[Lorentz, Ext[k]];
zG[k_] := Index[Gluon, Ext[k]];
zd1 = Index[Gluon, zzdum1]; zd2 = Index[Gluon, zzdum2]; zd3 = Index[Gluon, zzdum3]; zl1 = Index[Lorentz, zzdum4];
zSelf = {
  {"a metric-only difference on four gauge bosons", False, 4, ME[zL[1], zL[2]] ME[zL[3], zL[4]] - ME[zL[1], zL[3]] ME[zL[2], zL[4]]},
  {"a Levi-Civita tensor on four free indices", False, 4, Eps[zL[1], zL[2], zL[3], zL[4]]},
  {"a sparse colour tensor on four gluons", False, 4, IndexDelta[zG[1], zG[2]] IndexDelta[zG[3], zG[4]] ME[zL[1], zL[2]] ME[zL[3], zL[4]]},
  {"a colour tensor on six gluons, far above any enumeration", False, 6,
     f[zG[1], zG[2], zd1] f[zd1, zG[3], zd2] f[zd2, zG[4], zd3] f[zd3, zG[5], zG[6]] ME[zL[1], zL[2]] ME[zL[3], zL[4]] ME[zL[5], zL[6]]},
  {"a wrong relative sign", False, 3, FV[1, zL[2]] ME[zL[1], zL[3]] + FV[2, zL[1]] ME[zL[2], zL[3]]},
  {"the Jacobi identity", True, 4, (f[zG[1], zG[2], zd1] f[zG[3], zG[4], zd1] + f[zG[1], zG[3], zd1] f[zG[4], zG[2], zd1] + f[zG[1], zG[4], zd1] f[zG[2], zG[3], zd1]) ME[zL[1], zL[2]] ME[zL[3], zL[4]]},
  {"the Schouten identity", True, 5, Eps[zL[1], zL[2], zL[3], zL[4]] FV[1, zL[5]] - Eps[zL[5], zL[2], zL[3], zL[4]] FV[1, zL[1]] - Eps[zL[1], zL[5], zL[3], zL[4]] FV[1, zL[2]] - Eps[zL[1], zL[2], zL[5], zL[4]] FV[1, zL[3]] - Eps[zL[1], zL[2], zL[3], zL[5]] FV[1, zL[4]]},
  {"momentum conservation", True, 4, (FV[1, zL[1]] + FV[2, zL[1]] + FV[3, zL[1]] + FV[4, zL[1]]) ME[zL[2], zL[3]]},
  {"a contracted dummy against the scalar product", True, 3, FV[1, zl1] FV[2, zl1] - SP[1, 2]},
  {"f against d", True, 2, f[zd1, zd2, zG[1]] dSUN[zd1, zd2, zG[2]]}};
Do[If[zVanishesQ[{ConstantArray[{G, 1}, zt[[3]]], zt[[4]]}] =!= zt[[2]],
     Print["[abort] the vanishing test fails on ", zt[[1]]]; Exit[2]], {zt, zSelf}];
Print["[compare] the vanishing test passes its ", Length[zSelf], " cases"];

pairs = Get[pairsAbs];
If[! ListQ[pairs] || pairs === {}, Print["[abort] pairs file did not give a non-empty list: ", pairsAbs]; Exit[1]];
Print["[compare] ", Length[pairs], " pairs loaded"];
report = {};
allok = True;
anyskipped = False;

Do[
  {hBlk, hWC, gBlk, gWC, norm} = pr;
  Print["\n=== ", hBlk, " (", hWC, ")  vs  ", gBlk, " (", gWC, ")  x ", norm, " ==="];
  t0 = AbsoluteTime[];
  lh = Symbol[hBlk];                                (* the reference blocks are SetDelayed: evaluates *)
  lg = Symbol[gBlk] /. {gWC -> hWC, Lam -> 1};
  (* keep only the terms proportional to this WC in each block *)
  lh = Coefficient[lh, hWC] hWC;
  lg = Coefficient[lg, hWC] hWC;
  (* Cap the memory of one pair.  The class-1 X^4 operators expand enormously (four field
     strengths, eight gluon indices), and one of them can take a kernel to 18 GB and the
     machine into swap.  MemoryConstrained aborts that pair and returns $Aborted, so the run
     continues and reports the pair as SKIPPED rather than taking the machine down.
     DIM8_MAXMEM overrides the cap, in bytes. *)
  memcap = If[Environment["DIM8_MAXMEM"] === $Failed, 6*1024^3, ToExpression[Environment["DIM8_MAXMEM"]]];
  (* FeynmanRules collects vertices across the whole expanded Lagrangian and its cost blows
     up with the number of terms: in one call Q_{G^4}^{(2)} takes 13 h on five vertices.  Feynman rules
     are linear in L, so evaluate the difference monomial by monomial in chunks and merge,
     exactly as validate/fr_worker.wls does for the build.  DIM8_CMPCHUNK sets the chunk
     size; 0 restores the whole-difference path. *)
  cchunk = If[Environment["DIM8_CMPCHUNK"] === $Failed, 200, ToExpression[Environment["DIM8_CMPCHUNK"]]];
  verts = MemoryConstrained[
    diff = ExpandIndices[lh - norm lg];
    If[cchunk <= 0 || Head[Expand[diff]] =!= Plus,
      FeynmanRules[diff, ScreenOutput -> False],
      Module[{zterms = List @@ Expand[diff], zgrp, zout = {}},
        zgrp = Partition[zterms, UpTo[cchunk]];
        Print["   [chunked] ", Length[zterms], " terms in ", Length[zgrp], " chunks"];
        Do[zout = Join[zout, FeynmanRules[Total[zc], ScreenOutput -> False]], {zc, zgrp}];
        MergeVertices[zout]]],
    memcap, $Aborted];
  If[verts === $Aborted,
    Print["SKIPPED  exceeded the ", N[memcap/1024^3, 3], " GB cap"];
    AppendTo[report, <|"ref" -> hBlk, "gen" -> gBlk, "result" -> "skipped-memory"|>];
    anyskipped = True;
    Continue[]];
  zver = zVanishesQ /@ verts;
  nz = Pick[verts, zver, False];
  ok = Length[nz] == 0;
  allok = allok && ok;
  Print[If[ok, "PASS", "FAIL"], "  differing: ", Length[nz], ", verified zero: ",
    Length[verts] - Length[nz], "   (", Round[AbsoluteTime[] - t0, 0.1], " s)"];
  If[! ok, Print["  first differing vertex: ", nz[[1, 1]], "\n  coefficient: ", Short[nz[[1, 2]], 5]]];
  AppendTo[report, <|"ref" -> hBlk, "refWC" -> ToString[hWC], "gen" -> gBlk, "genWC" -> ToString[gWC],
                     "norm" -> ToString[norm], "pass" -> ok, "surviving" -> Length[nz],
                     "verified" -> Length[verts] - Length[nz]|>];
  , {pr, pairs}];

Export[StringReplace[pairsAbs, ".m" ~~ EndOfString -> "_report.json"], report, "JSON"];
(* a pair over the memory cap was not tested, so the list has not passed *)
Print["\nOVERALL: ", Which[! allok, "FAIL", anyskipped, "INCOMPLETE (some pairs over the memory cap)", True, "PASS"]];
Exit[If[allok && ! anyskipped, 0, 1]];
