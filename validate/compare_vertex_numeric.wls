(* validate/compare_vertex_numeric.wls -- numeric vertex-by-vertex equality of two cached blocks.
   Usage: DIM8_ROOT=<repo> wolframscript -file validate/compare_vertex_numeric.wls A.mx B.mx
   Every vertex of A must have a vertex in B with the same fields whose coupling difference
   vanishes under fr_compare.wls's numeric test (exhaustive external colour assignments,
   random integer momenta, inert tensor heads, term-by-term dummy sums).  Unlike
   compare_vertex_mx.wls, which proves equality symbolically after canonicalisation, this sees
   through algebraically different but equal forms, e.g. a Levi-Civita pair against its
   metric-determinant expansion (2026-09-04).  The numeric block below is a verbatim copy of
   fr_compare.wls lines between "zEta =" and the end of zVanishesQ; keep them in step. *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]]; FR$NKernels = 0;
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"]; LoadModel["base.fr", "gen.fr"];
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
zMaxCombos = 4096;
zVanishesQ[zvert_] := Module[{zc = zvert[[2]], zn = Length[zvert[[1]]], zext, zdims},
  If[PossibleZeroQ[Simplify[zc]], Return[True]];
  zext = Union[Cases[zc, Index[Colour | Gluon, Ext[_]], Infinity]];
  zdims = If[#[[1]] === Colour, 3, 8] & /@ zext;
  If[Times @@ zdims > zMaxCombos, Print["  [warn] ", zvert[[1, All, 1]], " has ", Times @@ zdims, " colour assignments, not tested numerically, reported as differing"]; Return[False]];
  NoneTrue[Tuples[Range /@ zdims], Function[zvals, AnyTrue[{1, 2}, zNumeric[zc, zn, #, zvals] =!= 0 &]]]];
args = Rest[$ScriptCommandLine]; Get[args[[1]]]; vA = FR$Vert; Get[args[[2]]]; vB = FR$Vert;
key[v_] := Sort[v[[1, All, 1]]]; bad = 0;
Do[mB = Select[vB, key[#] === key[va] &]; If[mB === {}, Print["missing in B: ", key[va]]; bad++; Continue[]];
   If[va[[1]] =!= mB[[1, 1]], Print["leg order differs, not compared: ", va[[1]], " vs ", mB[[1, 1]]]; bad++; Continue[]];
   d = {va[[1]], va[[2]] - mB[[1, 2]]}; z = zVanishesQ[d]; Print[key[va], If[z, "  EQUAL", "  DIFFERENT"]]; If[!z, bad++], {va, vA}];
Print["[numeric] A ", Length[vA], " B ", Length[vB], " differing ", bad, If[bad == 0 && Length[vA] == Length[vB], "  EQUAL", "  MISMATCH"]];
If[bad > 0 || Length[vA] != Length[vB], Quit[1]];
