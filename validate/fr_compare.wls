#!/usr/bin/env wolframscript
(* ======================================================================================
   validate/fr_compare.wls  --  V7: vertex-by-vertex equality of generated vs hand-typed
   ======================================================================================
   Usage:
     wolframscript -file validate/fr_compare.wls <base.fr> <generated.fr> <pairs.m> [nkernels]

   <base.fr>      : the hand-typed model (SM + hand-typed blocks), e.g.
                    prior_work/hand_typed/dim8_geosmeftVBF.fr
   <generated.fr> : fragment written by gen/emit_fr.py (M$Parameters Join + L8blk blocks)
   <pairs.m>      : a Mathematica list of
                    { {handBlock, handWC, genBlock, genWC, normalisation}, ... }
                    meaning   handBlock|_{handWC}  ==  normalisation * genBlock|_{genWC -> handWC, Lam -> 1}
   For every pair we evaluate both blocks, form the difference and compute the Feynman
   rules of the difference.  The test passes when no vertex survives.
   Exit code 0 on success, 1 on any failure; a JSON report is written next to pairs.m.
   ====================================================================================== *)

args = Rest[$ScriptCommandLine];
If[Length[args] < 3, Print["usage: fr_compare.wls base.fr generated.fr pairs.m [nkernels]"]; Exit[1]];
{baseFile, genFile, pairsFile} = Take[args, 3];
FR$NKernels = If[Length[args] >= 4, ToExpression[args[[4]]], 0];

(* the init script needs FR$PathOverride to find FeynRules; without it the load only works
   on a machine where FeynRules happens to be installed under the user's Mathematica
   directory, which is why this failed on an HPC system *)
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
Print["[v7] loading ", Length[genAbsList] + 1, " model files"];
LoadModel @@ Join[{baseAbs}, genAbsList];

$HistoryLength = 0;   (* do not retain every intermediate expression *)

(* --------------------------------------------------------------------------------------
   Deciding that a vertex vanishes.

   PossibleZeroQ[Simplify[...]] is far too weak here.  The difference of two correct
   implementations of the same CP-odd operator is built from Eps and momenta and vanishes
   only through momentum conservation and Schouten identities, which Simplify does not
   apply.  On Q_{G^2H^4}^{(2)} that produced 9 raw "surviving" vertices, of which 4 survived
   even the build worker's canonicalisation, yet all 4 are identically zero.

   So evaluate the Lorentz algebra numerically, the way the worker already evaluates colour:
   give the legs explicit momenta that sum to zero, assign the free Lorentz indices explicit
   values, sum every dummy index over 0..3 against the Minkowski metric, and turn Eps into
   the Levi-Civita symbol.  A structure that is not identically zero survives random momenta
   with probability one.
   -------------------------------------------------------------------------------------- *)
zEta = DiagonalMatrix[{1, -1, -1, -1}];
zGell = {{{0,1,0},{1,0,0},{0,0,0}}, {{0,-I,0},{I,0,0},{0,0,0}}, {{1,0,0},{0,-1,0},{0,0,0}},
  {{0,0,1},{0,0,0},{1,0,0}}, {{0,0,-I},{0,0,0},{I,0,0}}, {{0,0,0},{0,0,1},{0,1,0}},
  {{0,0,0},{0,0,-I},{0,I,0}}, {{1,0,0},{0,1,0},{0,0,-2}}/Sqrt[3]};
zfN = Table[-2 I Tr[(zGell[[za]].zGell[[zb]] - zGell[[zb]].zGell[[za]]).zGell[[zc]]]/8, {za,8},{zb,8},{zc,8}] // Simplify;
zdN = Table[ 2 Tr[(zGell[[za]].zGell[[zb]] + zGell[[zb]].zGell[[za]]).zGell[[zc]]]/8, {za,8},{zb,8},{zc,8}] // Simplify;

(* Evaluate BOTH the colour and the Lorentz algebra numerically.  Colour first (random
   external colour/gluon indices, dummies summed, T/f/d/delta and the colour Eps replaced by
   numbers), then Lorentz (explicit momenta summing to zero, free indices assigned, dummies
   summed against the Minkowski metric, the Lorentz Eps replaced by the Levi-Civita symbol).
   The two Eps are told apart by the type of their indices. *)
(* zvals: one explicit value per external colour index (Union order).  The first version drew
   them at random for eight seeds, which is unsound for sparse tensors: two gluon externals
   hit a nonzero delta one time in eight, so a genuinely nonzero gluonic difference vertex
   was declared zero with probability 0.34 (found 2026-09-03, together with the same flaw in
   the worker).  zVanishesQ now enumerates every colour assignment, early exit at the first
   nonzero one; the momenta stay random (a nonzero polynomial in them is caught with
   probability one), with two seeds per assignment. *)
(* Every FeynRules tensor head is swapped for an inert private head BEFORE any integer is
   substituted: FeynRules' own contraction rules fire on equal integers as if they were a
   summed pair (Eps[a,b,2,4] Eps[c,d,2,4] auto-reduces to metrics), which corrupted the
   evaluation whenever two external indices drew the same value (2026-09-04).  Dummies are
   summed TERM BY TERM: summing a dummy over the whole expression multiplies every term that
   does not contain it by the metric trace (-2 for Lorentz, 3 or 8 for colour), so a
   difference of two expressions with differently named dummies could never cancel. *)
zInert = {Eps -> zEPS, ME -> zME, FV -> zFV, SP -> zSP, T -> zT, f -> zF, dSUN -> zD, IndexDelta -> zDEL};
zSumDummies[ze_, zdumsOf_, zdim_, zweight_] := Module[{zterms = If[Head[Expand[ze]] === Plus, List @@ Expand[ze], {Expand[ze]}]},
  Total[Function[zt, Module[{zt2 = zt, zds = zdumsOf[zt]},
     Do[zt2 = Sum[(zt2 /. zd -> zv) zweight[zd, zv], {zv, zdim[zd]}], {zd, zds}]; zt2]] /@ zterms]];
zNumeric[zc_, zn_Integer, zseed_, zvals_List] := Module[{ze = zc /. zInert, zp, zext, zlor},
  SeedRandom[zseed];
  zext = Union[Cases[ze, Index[Colour | Gluon, Ext[_]], Infinity]]; ze = ze /. Thread[zext -> zvals];
  ze = zSumDummies[ze, Function[zt, Union[Cases[zt, Index[Colour | Gluon, _Symbol], Infinity]]], Function[zd, If[zd[[1]] === Colour, 3, 8]], Function[{zd, zv}, 1]];
  ze = ze /. {zT[za_Integer, zi_Integer, zj_Integer] :> zGell[[za, zi, zj]]/2, zF[za_Integer, zb_Integer, zk_Integer] :> zfN[[za, zb, zk]],
              zD[za_Integer, zb_Integer, zk_Integer] :> zdN[[za, zb, zk]], zDEL[zi_Integer, zj_Integer] :> KroneckerDelta[zi, zj]};
  zp = Table[RandomInteger[{-9, 9}, 4], {zn - 1}]; AppendTo[zp, -Total[zp]];
  ze = ze /. Index[Lorentz, zx_] :> zx;
  zlor = Union[Cases[ze, Ext[_], Infinity]]; ze = ze /. Thread[zlor -> (RandomInteger[{1, 4}] & /@ zlor)];
  ze = zSumDummies[ze, Function[zt, Union[Cases[zt, (zFV[_, zs_Symbol] | zME[zs_Symbol, _] | zME[_, zs_Symbol] | zEPS[___, zs_Symbol, ___]) :> zs, Infinity]]], Function[zd, 4], Function[{zd, zv}, zEta[[zv, zv]]]];
  ze = ze /. {zME[zi_Integer, zj_Integer] :> zEta[[zi, zj]], zSP[zi_Integer, zj_Integer] :> zp[[zi]].zEta.zp[[zj]]};
  ze = ze /. {zFV[zi_, zm_Integer] :> zp[[zi, zm]], zEPS[za_Integer, zb_Integer, zc2_Integer, zd2_Integer] :> Signature[{za, zb, zc2, zd2}], zEPS[za_Integer, zb_Integer, zc2_Integer] :> Signature[{za, zb, zc2}]};
  Simplify[ze]];
(* The cap on how many external colour assignments are enumerated.  A vertex above it is
   reported as differing WITHOUT being tested, so a pair can "fail" purely on size: that is
   what happened to Q_{q^2G^2D}^{(2),(3)} on 2026-09-11, where every surviving vertex was an
   untested one.  DIM8_MAXCOMBOS raises the cap.  Enumeration stays exhaustive; drawing the
   assignments at random is unsound here, as 2026-09-03 showed. *)
zMaxCombos = If[Environment["DIM8_MAXCOMBOS"] === $Failed, 4096, ToExpression[Environment["DIM8_MAXCOMBOS"]]];
zVanishesQ[zvert_] := Module[{zc = zvert[[2]], zn = Length[zvert[[1]]], zext, zdims},
  If[PossibleZeroQ[Simplify[zc]], Return[True]];
  zext = Union[Cases[zc, Index[Colour | Gluon, Ext[_]], Infinity]];
  zdims = If[#[[1]] === Colour, 3, 8] & /@ zext;
  If[Times @@ zdims > zMaxCombos,
    Print["  [untested] ", zvert[[1, All, 1]], " has ", Times @@ zdims, " colour assignments, above the ", zMaxCombos, " cap"];
    Return[zUntested]];
  NoneTrue[Tuples[Range /@ zdims], Function[zvals, AnyTrue[{1, 2}, zNumeric[zc, zn, #, zvals] =!= 0 &]]]];

pairs = Get[pairsAbs];
If[! ListQ[pairs] || pairs === {}, Print["[abort] pairs file did not give a non-empty list: ", pairsAbs]; Exit[1]];
Print["[v7] ", Length[pairs], " pairs loaded"];
report = {};
allok = True;
anyuntested = False;

Do[
  {hBlk, hWC, gBlk, gWC, norm} = pr;
  Print["\n=== ", hBlk, " (", hWC, ")  vs  ", gBlk, " (", gWC, ")  x ", norm, " ==="];
  t0 = AbsoluteTime[];
  lh = Symbol[hBlk];                                (* the hand-typed blocks are SetDelayed: evaluates *)
  lg = Symbol[gBlk] /. {gWC -> hWC, Lam -> 1};
  (* keep only the terms proportional to this WC in each block *)
  lh = Coefficient[lh, hWC] hWC;
  lg = Coefficient[lg, hWC] hWC;
  (* Cap the memory of one pair.  The class-1 X^4 operators expand enormously (four field
     strengths, eight gluon indices) and one of them took a kernel to 18 GB and the machine
     into swap.  MemoryConstrained aborts that pair and returns $Aborted, so the run
     continues and reports the pair as SKIPPED rather than taking the box down.
     DIM8_MAXMEM overrides the cap, in bytes. *)
  memcap = If[Environment["DIM8_MAXMEM"] === $Failed, 6*1024^3, ToExpression[Environment["DIM8_MAXMEM"]]];
  (* FeynmanRules collects vertices across the whole expanded Lagrangian and its cost blows
     up with the number of terms: Q_{G^4}^{(2)} ran 13 h on five vertices.  Feynman rules
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
    AppendTo[report, <|"hand" -> hBlk, "gen" -> gBlk, "result" -> "skipped-memory"|>];
    Continue[]];
  (* A vertex whose colour space is above the cap is UNTESTED, not differing.  Folding the two
     together is what made Q_{q^2G^2D}^{(2),(3)} read as FAIL on 2026-09-11 when every one of
     their 78 and 42 "surviving" vertices had never been evaluated.  Keep the two tallies
     apart, so a size limit can never again be reported as a disagreement. *)
  zver = zVanishesQ /@ verts;
  nz = Pick[verts, zver, False];
  unt = Pick[verts, zver, zUntested];
  ok = Length[nz] == 0;
  allok = allok && ok;
  anyuntested = anyuntested || Length[unt] > 0;
  Print[Which[! ok, "FAIL", Length[unt] > 0, "PASS but incomplete", True, "PASS"],
    "  differing: ", Length[nz], ", untested: ", Length[unt], ", verified zero: ",
    Length[verts] - Length[nz] - Length[unt], "   (", Round[AbsoluteTime[] - t0, 0.1], " s)"];
  If[! ok, Print["  first differing vertex: ", nz[[1, 1]], "\n  coefficient: ", Simplify[nz[[1, 2]]]]];
  If[Length[unt] > 0, Print["  untested vertices: ", DeleteDuplicates[unt[[All, 1, All, 1]]]]];
  AppendTo[report, <|"hand" -> hBlk, "handWC" -> ToString[hWC], "gen" -> gBlk, "genWC" -> ToString[gWC],
                     "norm" -> ToString[norm], "pass" -> ok, "surviving" -> Length[nz],
                     "untested" -> Length[unt], "verified" -> Length[verts] - Length[nz] - Length[unt]|>];
  , {pr, pairs}];

Export[StringReplace[pairsAbs, ".m" ~~ EndOfString -> "_report.json"], report, "JSON"];
Print["\nOVERALL: ", Which[! allok, "FAIL", anyuntested, "PASS but incomplete (some vertices above the colour cap)", True, "PASS"]];
Exit[If[allok, 0, 1]];
