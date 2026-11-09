#!/usr/bin/env wolframscript
(* validate/x4_polynomial.wls  --  write the operators of a class as polynomials in the field strengths.

     wolframscript -file validate/x4_polynomial.wls <base.fr> <gen.fr,shim.fr> <pairs.m> <out.json>
     python3 validate/x4_polynomial.py <out.json>

   What it does.  An operator of X^4 is a product of field strengths.  Our encoding and the SmeftFR files
   both write it so, with FS[...], Eps, f and dSUN, and the shim makes the two name one FS.  So two
   operators are equal at every number of legs if they are equal as polynomials in independent
   antisymmetric tensors.  This script loads the model and the pair list of validate/fr_compare.wls, keeps
   FeynRules from opening the field strengths, and writes both sides of each pair as lists of terms.
   validate/x4_polynomial.py evaluates them.

   When to reach for it.  For the class X^4, where FeynRules exceeds 122 GB on the seven- and eight-field
   monomials and validate/fr_compare.wls cannot reach them.  Any other class has fields outside FS.

   What its output means, and what it must pass: see validate/x4_polynomial.py.  A term with anything but
   a number, field strengths and these tensors stops the script with status 1. *)
args = Rest[$ScriptCommandLine];
If[Length[args] < 4, Print["usage: x4_polynomial.wls base.fr gen.fr,shim.fr pairs.m out.json"]; Exit[2]];
{baseFile, genFile, pairsFile, outFile} = Take[args, 4];
FR$NKernels = 0;
z9root = If[Environment["DIM8_ROOT"] === $Failed, ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
FR$PathOverride = FileNameJoin[{z9root, "external", "feynrules", "feynrules-current"}];
Get[FileNameJoin[{z9root, "tests", "fr_env", "fr_headless_init.m"}]];
baseAbs = ExpandFileName[baseFile]; genAbsList = ExpandFileName /@ StringSplit[genFile, ","]; pairsAbs = ExpandFileName[pairsFile]; outAbs = ExpandFileName[outFile];
SetDirectory[DirectoryName[baseAbs]];
LoadModel @@ Join[{baseAbs}, genAbsList];
pairs = Get[pairsAbs];
zStr[x_] := ToString[x, InputForm];
zFactor[x_] := Which[
  MatchQ[x, FS[_, __]], Prepend[zStr /@ List @@ x, "FS"],
  MatchQ[x, Eps[__]], Prepend[zStr /@ List @@ x, "Eps"],
  MatchQ[x, f[_, _, _]], Prepend[zStr /@ List @@ x, "f"],
  MatchQ[x, dSUN[_, _, _]], Prepend[zStr /@ List @@ x, "d"],
  MatchQ[x, IndexDelta[_, _]], Prepend[zStr /@ List @@ x, "delta"],
  True, Print["[abort] a factor that is no field strength or tensor: ", zStr[x]]; Exit[1]];
zTerm[t_] := Module[{zf = If[Head[t] === Times, List @@ t, {t}], zc = 1, zout = {}},
  Do[Which[
      NumericQ[x], zc *= x,
      x === epsLorSign, Null,
      Head[x] === Power && IntegerQ[x[[2]]] && x[[2]] > 0, zout = Join[zout, ConstantArray[zFactor[x[[1]]], x[[2]]]],
      True, AppendTo[zout, zFactor[x]]], {x, zf}];
  <|"re" -> N[Re[zc]], "im" -> N[Im[zc]], "f" -> zout|>];
zTerms[e_] := Module[{zx = Expand[e]}, Which[zx === 0, {}, Head[zx] === Plus, zTerm /@ (List @@ zx), True, {zTerm[zx]}]];
(* FeynRules opens a field strength as soon as FS is evaluated, and ExpandIndices does so too, so both forms are read
   with FS inert and ExpandIndices holding its argument as it is.  HC of a field strength is the field strength, and
   OptimizeIndex only renames dummies. *)
zRead[blk_, wc_, rules_] := Block[{ExpandIndices, OptimizeIndex, HC, FS},
  ExpandIndices[x_, ___] := x; OptimizeIndex[x_, ___] := x; HC[x_] := x;
  zTerms[Coefficient[Expand[Symbol[blk] /. rules], wc]]];
out = Table[Module[{h, w, b, g, n}, {h, w, b, g, n} = pr;
    Print["[read] ", h, " ", b];
    <|"ref" -> h, "gen" -> b, "norm" -> N[n], "ref_terms" -> zRead[h, w, {}], "gen_terms" -> zRead[b, g, {Lam -> 1}]|>], {pr, pairs}];
Export[outAbs, out, "RawJSON"];
Print["[wrote] ", Length[out], " pairs to ", outAbs];
