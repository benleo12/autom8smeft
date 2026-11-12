(* validate/geo_cache_check.wls N BLOCKS [CACHEDIR]  --  do the cached vertices of a connection block equal its Module's?

   A model of order N (gen/towers.py) takes its vertices with at most three legs from the blocks G8op<i> and
   T<d>op<i> of gen_geo<N>.fr.  The Module of such a block ends in Return[z8geoTrunc[..., p]], which puts the
   corrections of the base on the fields and the couplings to the order N - p the block owes, and
   validate/fr_worker.wls caches the block term by term, without evaluating that Return: it applies the
   truncation itself (z9retOrder).  A block cached without it is right at its own order p and wrong above it,
   and nothing else sees that: the two-point checks evaluate the Modules, not the cache, and the export check
   (validate/geo_export_check.py) compares the written model with the one of 1/Lambda^4 at NP <= 2.

   Here the Module of each block is evaluated whole, FeynmanRules gives its vertices with at most three legs,
   and each is compared with the cached one, NP order by NP order through N, at a point where every
   coefficient has an irrational value and Lambda = 3 TeV (validate/geo_numeric.m gives every other parameter
   there).  The two couplings of a vertex are compared as polynomials: the momenta as components with the last
   fixed by conservation, each external Lorentz index against a vector, the summed Lorentz indices against the
   metric, the Dirac chains as explicit matrices with the external spin indices enumerated, as the worker does
   for its zero test of a Hermiticity residual (z9lorentzZeroQ), and the generation indices enumerated as well,
   the summed ones summed.  Two couplings are the same vertex exactly
   when these polynomials are, whatever the names of their summed indices, the order of the arguments of their
   Eps, or the momenta they are written with: the cache is written in the worker's canonical form (canonCoup)
   and FeynmanRules' output is not.  A block passes when no coefficient of a polynomial differs by more than
   10^-9 of the largest coefficient its Module has at that order.  What a cache holds above the order N is
   reported and not compared: validate/np_truncate.m removes it when the model is written.

     DIM8_ROOT=... wolframscript -file validate/geo_cache_check.wls 4 G8op44,T10op44 [CACHEDIR]
     DIM8_ROOT=... wolframscript -file validate/geo_cache_check.wls 4 all [CACHEDIR]      every block of gen_geo4.json

   CACHEDIR defaults to the first directory of DIM8_VDIR.  The exit status is 0 when every block passes, 1 when
   one fails, 2 when one could not be checked (no cached block, a name that gen_geo<N>.json does not hold, a
   parameter without a value, a structure the polynomial does not know, a base of another order), whatever the
   others did.  One line a block:
     [cachecheck] G8op44 order 4: PASS ...     or FAIL ...     or NOT CHECKED ...
   and a last line [cachecheck] order 4 against <dir>: n blocks, n PASS, n FAIL, n NOT CHECKED.
   The Module's own ExpandIndices is capped at three legs (validate/truncexp.m), which keeps every term with at
   most three legs.  DIM8_TRUNCEXP=0 evaluates it as it stands, hours for the largest blocks, with
   the same result.  The check can fail: G8op44 of order 4 as the worker cached it before it applied the
   truncation differs by 0.8 of the largest coefficient at NP 3 and 4, and exits 1.
   DIM8_PROGRESS names a file that gets every line of the report as it is written. *)
$root = If[Environment["DIM8_ROOT"] === $Failed, ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
z9args = Rest[$ScriptCommandLine];
If[! StringQ[$root] || Length[z9args] < 2, Print["usage: DIM8_ROOT=... wolframscript -file validate/geo_cache_check.wls N BLOCK[,BLOCK...]|all [CACHEDIR]"]; Quit[2]];
z9N = ToExpression[z9args[[1]]];
z9vdir = Which[Length[z9args] >= 3, z9args[[3]],
  StringQ[Environment["DIM8_VDIR"]], First[StringTrim /@ StringSplit[Environment["DIM8_VDIR"], ";"]],
  True, Print["[cachecheck] no CACHEDIR given and DIM8_VDIR is not set"]; Quit[2]];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9prog = Environment["DIM8_PROGRESS"];
z9say[z9s__] := Module[{z9l = StringJoin[ToString /@ {z9s}], z9h}, Print[z9l];
  If[StringQ[z9prog], z9h = OpenAppend[z9prog]; WriteString[z9h, DateString[{"Hour", ":", "Minute", ":", "Second"}], " ", z9l, "\n"]; Close[z9h]]];
z9num[z9x_] := ToString[If[z9x == 0, 0, N[z9x, 3]], InputForm];
Unprotect[$RecursionLimit]; $RecursionLimit = 10000;
z9gen = "gen_geo" <> ToString[z9N] <> ".fr";
If[! FileExistsQ[z9gen] || ! FileExistsQ[StringReplace[z9gen, ".fr" -> ".json"]], Print["[cachecheck] no ", z9gen, " with its .json in tests/gen_smoke"]; Quit[2]];
z9json = Import[StringReplace[z9gen, ".fr" -> ".json"], "RawJSON"];
z9orderOf = Association[(#["block"] -> (#["dim"] - 4)/2) & /@ z9json];
z9blocks = If[z9args[[2]] === "all", Keys[z9orderOf], StringTrim /@ StringSplit[z9args[[2]], ","]];
(* the files the worker loads (validate/fr_worker.wls z9models) *)
LoadModel[Sequence @@ Join[{"base_geo" <> ToString[z9N] <> "_mw.fr", "dim6_geo.fr", z9gen, "gen.fr"}, If[FileExistsQ["gen_flavour.fr"], {"gen_flavour.fr"}, {}]]];
If[z8geoN =!= z9N, z9say["[cachecheck] order ", z9N, ": NOT CHECKED: the base is of order ", z8geoN]; Quit[2]];
Get[$root <> "/validate/truncexp.m"];
Get[$root <> "/validate/geo_numeric.m"];

(* the NP order of a parameter.  A parameter with an order is graded by that power of z9eps, and so is the
   general flavour coefficient of a fermionic block (z8F2, z8F4 of gen_flavour.fr), which carries indices, has
   no value at an external generation and has the order p of the block's operator *)
z9npOf[z9p_] := Module[{z9io = InteractionOrder /. Flatten[{z9p[[2]]}]},
  If[z9io === InteractionOrder, 0, Total[Cases[If[MatchQ[z9io, {_Symbol, _Integer}], {z9io}, z9io], {NP, z9n_Integer} :> z9n]]]];
z9np = Association[(#[[1]] -> z9npOf[#]) & /@ M$Parameters];
z9grade = Dispatch[KeyValueMap[#1 -> z9eps^#2 #1 &, Select[z9np, # != 0 &]]];
z9flavQ[z9y_Symbol] := StringStartsQ[SymbolName[z9y], "z8F"]; z9flavQ[_] := False;
z9gradeFlav[z9c_, z9p_] := z9c /. {Conjugate[(z9y_?z9flavQ)[z9i__]] :> z9eps^z9p z9FLc[z9y][z9i], (z9y_?z9flavQ)[z9i__] :> z9eps^z9p z9FL[z9y][z9i]};

(* the point: every external parameter with an NP order at an irrational number, the components of the general
   flavour coefficients at complex ones, Lambda at 3 TeV.  z8numRules quits with status 1 when a parameter has
   no value: here that is a check not made, status 2 *)
z9ext = Select[M$Parameters, (ParameterType /. Flatten[{#[[2]]}]) === External && z9npOf[#] > 0 &][[All, 1]];
z9comp = Flatten[z8numComponents /@ Select[M$Parameters, StringStartsQ[SymbolName[#[[1]]], "z8F"] && z8numMatrixQ[#] &]];
z9rules = Catch[Block[{Quit = (Throw[$Failed, "z9numeric"] &)},
  Dispatch[z8numRules[Join[{Lam -> 3000.}, Thread[z9ext -> N[Table[1/2 + FractionalPart[Sqrt[Prime[z9i]]], {z9i, Length[z9ext]}], 20]],
    Thread[z9comp -> Table[N[1/2 + FractionalPart[Sqrt[Prime[Length[z9ext] + 2 z9i]]] + I (1/3 + FractionalPart[Sqrt[Prime[Length[z9ext] + 2 z9i + 1]]])], {z9i, Length[z9comp]}]]]]]], "z9numeric"];
If[z9rules === $Failed, z9say["[cachecheck] order ", z9N, ": NOT CHECKED: validate/geo_numeric.m found no value for a parameter at the point"]; Quit[2]];

(* a coupling at the point, its NP orders as powers of z9eps *)
z9atPoint[z9c_, z9p_] := (z9gradeFlav[z9c, z9p] /. z9grade /. z9rules) /. {Conjugate[z9eps] -> z9eps, Conjugate[Power[z9eps, z9k_]] :> z9eps^z9k};

(* the polynomial of a coupling of a vertex with z9n legs, one for each choice of the external spin indices *)
z9eta = DiagonalMatrix[{1, -1, -1, -1}];
z9sig2 = {{{0, 1}, {1, 0}}, {{0, -I}, {I, 0}}, {{1, 0}, {0, -1}}};
z9gam = Join[{ArrayFlatten[{{IdentityMatrix[2], 0}, {0, -IdentityMatrix[2]}}]}, Table[ArrayFlatten[{{0, z9sig2[[z9k]]}, {-z9sig2[[z9k]], 0}}], {z9k, 3}]];
z9g5 = I z9gam[[1]].z9gam[[2]].z9gam[[3]].z9gam[[4]];
z9gamOf[5] = z9g5; z9gamOf[z9m_Integer /; 1 <= z9m <= 4] := z9gam[[z9m]];
z9projP = (IdentityMatrix[4] + z9g5)/2; z9projM = (IdentityMatrix[4] - z9g5)/2;
z9sigM[z9m_, z9n_] := I/2 (z9gamOf[z9m].z9gamOf[z9n] - z9gamOf[z9n].z9gamOf[z9m]);
z9dmat[zGA[z9m_Integer]] := z9gamOf[z9m]; z9dmat[zPP] := z9projP; z9dmat[zPM] := z9projM;
z9dmat[zSIG[z9m_Integer, z9n_Integer]] := z9sigM[z9m, z9n]; z9dmat[z9x_] := Throw[{$Failed, z9x}, z9lor];
z9pv[z9i_, z9m_, z9n_] := If[z9i < z9n, z9p[z9i, z9m], -Sum[z9p[z9j, z9m], {z9j, z9n - 1}]];
(* one kind of index summed term by term over z9r values: z9pick[term] gives the index objects to sum, z9w[index, value] the weight *)
z9sumIdx[z9e_, z9pick_, z9w_, z9r_: 4] := Module[{z9x = Expand[z9e], z9terms},
  z9terms = If[Head[z9x] === Plus, List @@ z9x, {z9x}];
  Total[Function[z9t, Module[{z9t2 = z9t}, Do[z9t2 = Sum[(z9t2 /. z9d -> z9v) z9w[z9d, z9v], {z9v, z9r}], {z9d, z9pick[z9t]}]; z9t2]] /@ z9terms]];
z9dummyQ[Ext[_]] := False; z9dummyQ[_] := True;
z9lorHeads = _zL | _zS | _zG | _zEPS | _zME | _zFV | _zSP | _zGA | _zPP | _zPM | _zSIG | _zTD | _zTDf | _zSLP | _Ga | _ProjP | _ProjM | _Sig | _TensDot | _SlashedP | _CC | Index[Lorentz | Spin, _];
z9poly[0, _] = <||>;
z9poly[z9c0_, z9n_Integer] := Catch[Module[{z9c = z9c0, z9sp, z9gx, z9ze, z9out = <||>},
  (* every FeynRules head goes inert before any integer is substituted: FeynRules rewrites TensDot[..][3, 4],
     Ga[1, 3, 4] and the like on sight *)
  z9c = z9c /. {HoldPattern[Eps[z9a_, z9b_, z9c2_, z9d_]] :> zEPS[z9a, z9b, z9c2, z9d], ME -> zME, FV -> zFV, SP -> zSP,
                Ga -> zGA, ProjP -> zPP, ProjM -> zPM, Sig -> zSIG, TensDot -> zTD, SlashedP -> zSLP};
  z9c = z9c /. {Index[Lorentz, z9x_] :> zL[z9x], Index[Spin, z9x_] :> zS[z9x], Index[Generation, z9x_] :> zG[z9x]};
  (* the structure constant with its arguments sorted, as the worker's canonical form has it *)
  z9c = z9c /. f[z9a__] :> Signature[{z9a}] f[Sequence @@ Sort[{z9a}]];
  z9c = z9c /. zTD[z9objs__][z9a_, z9b_] :> zTDf[{z9objs}, z9a, z9b];
  z9c = z9c /. {zSLP[z9i_, z9a_, z9b_] :> Sum[z9eta[[z9d, z9d]] zFV[z9i, z9d] zGA[z9d, z9a, z9b], {z9d, 4}],
                zTDf[{z9pre___, zSLP[z9i_], z9post___}, z9a_, z9b_] :> Sum[z9eta[[z9d, z9d]] zFV[z9i, z9d] zTDf[{z9pre, zGA[z9d], z9post}, z9a, z9b], {z9d, 4}]};
  z9sp = Union[Cases[z9c, zS[Ext[_]], Infinity]]; z9gx = Union[Cases[z9c, zG[Ext[_]], Infinity]];
  Do[z9ze = z9c /. Thread[z9sp -> z9sv[[1]]] /. Thread[z9gx -> z9sv[[2]]];
     z9ze = z9sumIdx[z9ze, Function[z9t, Union[Cases[z9t, zG[_?z9dummyQ], Infinity]]], Function[{z9d, z9val}, 1], 3];
     z9ze = z9sumIdx[z9ze, Function[z9t, Union[Cases[z9t, zL[Ext[_]], Infinity]]], Function[{z9d, z9val}, z9e[z9d[[1, 1]], z9val]]];
     z9ze = z9sumIdx[z9ze, Function[z9t, Union[Cases[z9t, zL[_?z9dummyQ], Infinity]]], Function[{z9d, z9val}, z9eta[[z9val, z9val]]]];
     z9ze = z9sumIdx[z9ze, Function[z9t, Union[Cases[z9t, zS[_?z9dummyQ], Infinity]]], Function[{z9d, z9val}, 1]];
     z9ze = z9ze /. {zME[z9i_Integer, z9j_Integer] :> z9eta[[z9i, z9j]], zEPS[z9a_Integer, z9b_Integer, z9c2_Integer, z9d_Integer] :> Signature[{z9a, z9b, z9c2, z9d}]};
     z9ze = z9ze /. {zSP[z9i_, z9j_] :> Sum[z9eta[[z9m, z9m]] z9pv[z9i, z9m, z9n] z9pv[z9j, z9m, z9n], {z9m, 4}], zFV[z9i_, z9m_Integer] :> z9pv[z9i, z9m, z9n]};
     z9ze = z9ze /. {zTDf[z9objs_List, z9a_Integer, z9b_Integer] :> (Dot @@ (z9dmat /@ z9objs))[[z9a, z9b]],
                     zGA[z9m_Integer, z9a_Integer, z9b_Integer] :> z9gamOf[z9m][[z9a, z9b]], zPP[z9a_Integer, z9b_Integer] :> z9projP[[z9a, z9b]],
                     zPM[z9a_Integer, z9b_Integer] :> z9projM[[z9a, z9b]], zSIG[z9m_Integer, z9n2_Integer, z9a_Integer, z9b_Integer] :> z9sigM[z9m, z9n2][[z9a, z9b]],
                     HoldPattern[IndexDelta[z9a_Integer, z9b_Integer]] :> KroneckerDelta[z9a, z9b]};
     (* the components of the general flavour coefficients and of the matrix parameters, now at integer generations *)
     z9ze = z9ze /. {z9FL[z9y_][z9i__Integer] :> z9y[z9i], z9FLc[z9y_][z9i__Integer] :> Conjugate[z9y[z9i]]} /. z9rules;
     z9ze = Expand[z9ze];
     If[! FreeQ[z9ze, z9lorHeads], Throw[{$Failed, Take[Union[Cases[z9ze, z9lorHeads, Infinity]], UpTo[3]]}, z9lor]];
     If[! (NumericQ[z9ze] && z9ze == 0), z9out[z9sv] = z9ze],
     {z9sv, Tuples[{Tuples[Range[4], Length[z9sp]], Tuples[Range[3], Length[z9gx]]}]}];
  z9out], z9lor];
(* the coefficients of a polynomial at each power of z9eps: <|order -> {coefficient, ...}|>.  A sum of numbers
   that cancel leaves a machine zero, which has lost its power of z9eps: an order whose coefficients are all
   zero is no order *)
z9big[z9l_] := Max[Append[Abs /@ Flatten[{z9l}], 0]];
z9coefs[z9q_] := If[z9q === 0, <||>,
  Module[{z9y = Expand[z9q], z9os}, z9os = Union[Exponent[z9y, z9eps, List]];
    Select[Association[Function[z9o, z9o -> With[{z9w = Coefficient[z9y, z9eps, z9o]}, CoefficientRules[z9w, Variables[z9w]][[All, 2]]]] /@ z9os], z9big[#] > 0 &]]];
(* the polynomial must know one coupling written two ways, a near miss, momentum conservation and the Clifford algebra *)
Module[{zl1 = Index[Lorentz, Ext[1]], zl2 = Index[Lorentz, Ext[2]], zl3 = Index[Lorentz, Ext[3]], zs1 = Index[Spin, Ext[1]], zs2 = Index[Spin, Ext[2]], za, zb, zt},
  za = Eps[zl2, zl1, Index[Lorentz, z9mu1], Index[Lorentz, z9mu2]] FV[1, Index[Lorentz, z9mu1]] FV[2, Index[Lorentz, z9mu2]];
  zb = -Eps[Index[Lorentz, z9nu2], Index[Lorentz, z9nu1], zl1, zl2] FV[1, Index[Lorentz, z9nu2]] FV[2, Index[Lorentz, z9nu1]];
  zt = {z9poly[za - zb, 3] === <||>, z9poly[za + zb, 3] =!= <||>, z9poly[FV[1, zl1] + FV[2, zl1] + FV[3, zl1], 3] === <||>,
        z9poly[TensDot[Ga[zl3], Ga[Index[Lorentz, z9mu1]]][zs1, zs2] FV[3, Index[Lorentz, z9mu1]] + TensDot[Ga[Index[Lorentz, z9mu1]], Ga[zl3]][zs1, zs2] FV[3, Index[Lorentz, z9mu1]] - 2 FV[3, zl3] IndexDelta[zs1, zs2], 3] === <||>,
        z9poly[SlashedP[1, zs1, zs2] - Ga[Index[Lorentz, z9mu1], zs1, zs2] FV[1, Index[Lorentz, z9mu1]], 3] === <||>,
        z9poly[TensDot[Ga[zl3], ProjP][zs1, zs2] - TensDot[Ga[zl3], ProjM][zs1, zs2], 3] =!= <||>};
  If[zt =!= ConstantArray[True, 6], z9say["[cachecheck] order ", z9N, ": NOT CHECKED: the polynomial of a coupling fails its own test ", zt]; Quit[2]]];

(* the parameters of a coupling by NP order, for the report of a failure *)
z9parQ[z9x_] := AllTrue[DeleteDuplicates[Cases[{z9x}, _Symbol, {0, Infinity}, Heads -> True]], Context[#] === "System`" || KeyExistsQ[z9np, #] &];
z9pars[0, _] = <||>;
z9pars[z9e_, z9p_] := Module[{z9par = <||>},
  Do[Module[{z9f = If[Head[z9t] === Times, List @@ z9t, {z9t}], z9s, z9c, z9o},
       z9s = Times @@ Select[z9f, ! z9parQ[#] &]; z9c = Times @@ Select[z9f, z9parQ];
       z9o = Exponent[(z9c /. Conjugate[z9y_] :> z9y) /. z9grade, z9eps] + If[FreeQ[z9s, _Symbol?z9flavQ], 0, z9p];
       z9par[z9o] = Union[Lookup[z9par, z9o, {}], Select[Cases[z9c, _Symbol, {0, Infinity}], KeyExistsQ[z9np, #] &]]],
     {z9t, If[Head[#] === Plus, List @@ #, {#}] &[Expand[z9e]]}];
  z9par];

(* the Module with its own ExpandIndices capped at three doublet fields.  The parameter sums that
   validate/truncexp.m abbreviates stay abbreviated through the Module's steps after the expansion, as in the
   worker, and are put back as the Module hands its sum to z8geoTrunc, which has to see them to cut their
   products: OptimizeIndex on the sums written out takes twenty minutes for a block of dimension twelve. *)
z9capOn = False; z9gt = 0;
(* ExpandIndices and FeynmanRules take time that grows faster than the number of terms, and both are linear: the
   operator is expanded monomial by monomial and the Feynman rules are taken 250 terms at a time, as the worker
   does.  Each factor of a monomial that holds a field and no doublet (a field strength, a fermion) gives every
   term at least one leg, so the cap on the doublet fields of the monomial is three less the number of such
   factors, as in the worker (z9hard): W^3 H^2 is expanded at its vacuum value only. *)
z9mono[z9m_] := If[Head[#] === Plus, List @@ #, {#}] &[Expand[z9m]];
z9factors[z9m_] := Flatten[If[Head[z9m] === Times, List @@ z9m, {z9m}] /. Power[z9b_, z9n_Integer?Positive] :> Table[z9b, {z9n}]];
z9hard[z9m_] := Count[z9factors[z9m], z9f_ /; ! z9phiQ[z9f] && ! FreeQ[z9f, _Symbol?FieldQ | (_Symbol?FieldQ)[___]]];
DownValues[ExpandIndices] = Prepend[DownValues[ExpandIndices],
  HoldPattern[ExpandIndices[z9m_, z9o___] /; z9capOn] :> Block[{z9capOn = False}, Total[z9expandIdxB[#, 3 - z9hard[#], z9o] & /@ z9mono[z9m]]]];
DownValues[z8geoTrunc] = Prepend[DownValues[z8geoTrunc],
  HoldPattern[z8geoTrunc[z9L_, z9q_] /; z9capOn] :> Block[{z9capOn = False}, z9gt++; z8geoTrunc[z9L /. z9abbrevBack, z9q]]];

z9tol = 10^-9;
z9check[z9b_String] := Module[{z9p, z9file, z9x, z9vm, z9vc, z9am, z9ac, z9t = AbsoluteTime[], z9scale = <||>, z9diff = <||>, z9pm = <||>, z9pc = <||>,
    z9os, z9fail, z9above = {}, z9lines, z9stop = None},
  If[! KeyExistsQ[z9orderOf, z9b], z9say["[cachecheck] ", z9b, " order ", z9N, ": NOT CHECKED: not a block of ", StringReplace[z9gen, ".fr" -> ".json"]]; Return[2]];
  z9p = z9orderOf[z9b];
  z9file = SelectFirst[{z9vdir <> "/" <> z9b <> ".mx", z9vdir <> "/" <> z9b <> ".wxf"}, FileExistsQ, None];
  If[z9file === None, z9say["[cachecheck] ", z9b, " order ", z9N, ": NOT CHECKED: no ", z9b, ".mx in ", z9vdir]; Return[2]];
  Clear[FR$Vert]; If[FileExtension[z9file] === "wxf", FR$Vert = Quiet[Import[z9file, "WXF"]], Quiet[Get[z9file]]];
  If[! ListQ[FR$Vert], z9say["[cachecheck] ", z9b, " order ", z9N, ": NOT CHECKED: ", z9file, " does not hold a vertex list"]; Return[2]];
  z9vc = Select[FR$Vert, Length[#[[1]]] <= 3 &];
  z9gt = 0; z9x = Block[{z9capOn = True}, Symbol[z9b]];
  If[z9gt =!= 1 || ! FreeQ[z9x, Alternatives @@ z9abbrevBack[[All, 1]]],
    z9say["[cachecheck] ", z9b, " order ", z9N, ": NOT CHECKED: ", If[z9gt =!= 1, "the Module passed its sum through z8geoTrunc " <> ToString[z9gt] <> " times, not once",
      "the Module passed its sum through z8geoTrunc once and its result still holds a parameter sum that validate/truncexp.m abbreviates"]]; Return[2]];
  z9vm = If[z9x === 0, {}, Flatten[FeynmanRules[Total[#], ScreenOutput -> False, MaxParticles -> 3] & /@ Partition[If[Head[z9x] === Plus, List @@ z9x, {z9x}], UpTo[250]], 1]];
  z9am = GroupBy[z9vm, (#[[1, All, 1]] &) -> (#[[2]] &), Total]; z9ac = Association[(#[[1, All, 1]] -> #[[2]]) & /@ z9vc];
  z9vm = Keys[z9am];
  Do[Module[{z9cm = Lookup[z9am, Key[z9k], 0], z9cc = Lookup[z9ac, Key[z9k], 0], z9qm, z9qc, z9a, z9c, z9d},
       z9qm = z9poly[z9atPoint[z9cm, z9p], Length[z9k]]; z9qc = z9poly[z9atPoint[z9cc, z9p], Length[z9k]];
       If[! AssociationQ[z9qm] || ! AssociationQ[z9qc], z9stop = {z9k, "a structure the polynomial does not know " <> ToString[InputForm[Last[If[AssociationQ[z9qm], z9qc, z9qm]]]]}; Break[]];
       Do[z9a = z9coefs[Lookup[z9qm, Key[z9sv], 0]]; z9c = z9coefs[Lookup[z9qc, Key[z9sv], 0]]; z9d = z9coefs[Expand[Lookup[z9qm, Key[z9sv], 0] - Lookup[z9qc, Key[z9sv], 0]]];
          If[! AllTrue[Flatten[{Values[z9a], Values[z9c]}], NumericQ], z9stop = {z9k, "a parameter without a value"}; Break[]];
          KeyValueMap[(z9scale[#1] = Max[Lookup[z9scale, #1, 0], z9big[#2]]) &, z9a];
          KeyValueMap[(z9diff[#1] = Max[Lookup[z9diff, #1, 0], z9big[#2]]) &, z9d];
          z9above = Union[z9above, Select[Keys[z9c], # > z9N &]];
          If[Keys[z9a] =!= {} && (Min[Keys[z9a]] < z9p || Max[Keys[z9a]] > z9N), z9stop = {z9k, "pieces of the Module of NP order " <> ToString[Keys[z9a]] <> ", outside " <> ToString[z9p] <> " to " <> ToString[z9N]}; Break[]],
          {z9sv, Union[Keys[z9qm], Keys[z9qc]]}];
       If[z9stop =!= None, Break[]];
       KeyValueMap[(z9pm[#1] = Union[Lookup[z9pm, #1, {}], #2]) &, z9pars[z9cm, z9p]]; KeyValueMap[(z9pc[#1] = Union[Lookup[z9pc, #1, {}], #2]) &, z9pars[z9cc, z9p]]],
     {z9k, Union[Keys[z9am], Keys[z9ac]]}];
  If[z9stop =!= None, z9say["[cachecheck] ", z9b, " order ", z9N, ": NOT CHECKED: ", ToString[z9stop[[1]]], ": ", z9stop[[2]]]; Return[2]];
  z9os = Select[Union[Keys[z9scale], Keys[z9diff]], # <= z9N &];
  z9fail = Select[z9os, Lookup[z9diff, #, 0] > z9tol Lookup[z9scale, #, 0] &];
  z9lines = StringRiffle[("NP " <> ToString[#] <> ": " <> If[Lookup[z9scale, #, 0] > 0, z9num[Lookup[z9diff, #, 0]/z9scale[#]], If[Lookup[z9diff, #, 0] > 0, "no piece in the Module", "0"]]) & /@ z9os, ", "];
  z9say["[cachecheck] ", z9b, " order ", z9N, ": ", If[z9fail === {}, "PASS", "FAIL"], ": ", Length[z9vm], " vertices of the Module with at most three legs, ", Length[z9vc],
    " cached; largest |Module - cache| / largest coefficient of the Module at ", If[z9lines === "", "no order", z9lines],
    If[z9fail === {}, "", "; parameters of the Module that the cache lacks at " <> StringRiffle[("NP " <> ToString[#] <> " " <>
        ToString[Complement[Lookup[z9pm, #, {}], Lookup[z9pc, #, {}]]]) & /@ z9fail, ", "] <> ", of the cache that the Module lacks " <>
        ToString[Union @@ (Complement[Lookup[z9pc, #, {}], Lookup[z9pm, #, {}]] & /@ z9fail)]],
    "; NP orders of the cache above ", z9N, ": ", If[z9above === {}, "none", ToString[z9above]], " (", Round[AbsoluteTime[] - z9t], " s)"];
  If[z9fail === {}, 0, 1]];
z9res = Association[(# -> z9check[#]) & /@ z9blocks];
z9say["[cachecheck] order ", z9N, " against ", z9vdir, ": ", Length[z9res], " blocks, ", Count[z9res, 0], " PASS, ", Count[z9res, 1], " FAIL", If[Count[z9res, 1] > 0, " " <> ToString[Keys[Select[z9res, # === 1 &]]], ""],
  ", ", Count[z9res, 2], " NOT CHECKED", If[Count[z9res, 2] > 0, " " <> ToString[Keys[Select[z9res, # === 2 &]]], ""]];
Quit[Which[MemberQ[Values[z9res], 2], 2, MemberQ[Values[z9res], 1], 1, True, 0]];
