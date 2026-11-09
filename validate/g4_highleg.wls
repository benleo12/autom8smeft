#!/usr/bin/env wolframscript
(* validate/g4_highleg.wls  --  the cache side of validate/g4_highleg.py.

     wolframscript -file validate/g4_highleg.wls dump  <cache dir> <out.json> <block> ...
     wolframscript -file validate/g4_highleg.wls merge <cache dir> <json dir> <block>=<coefficient> ...

   What it does.  `dump` writes the vertices of cached blocks as lists of terms, which
   validate/g4_highleg.py check evaluates beside the plane waves.  `merge` runs validate/g4_highleg.py
   write, on the gen.fr of this tree, and adds the seven- and eight-gluon vertices it computes to a block
   FeynRules built up to six legs, in the form of FeynRules' own vertices, and adds "highleg 7 8" (the numbers of gluons added, or
   "highleg none") to its status line.  The block keeps "maxlegs 6", which says how far FeynRules went.
   Merging again replaces what was merged, and the file of the block is replaced in one step.

   When to reach for it.  ./dim8 build merges by itself, for the blocks of CAPPED_WCS there.

   What must hold.  The merged block goes through validate/g4_highleg.py check by way of `dump`, so what
   is compared is the block in the cache and not the list it came from.  A block whose status line has no
   "maxlegs 6" stops the script with status 1, since it has FeynRules' own vertices at those legs, and so
   does a symbol the block's own vertices do not hold, which would be a vertex in another context that
   WriteUFO cannot read. *)
args = Rest[$ScriptCommandLine];
If[Length[args] < 4, Print["usage: g4_highleg.wls dump|merge <cache dir> <out.json|json dir> <block> or <block>=<coefficient> ..."]; Exit[2]];
{mode, vdir, target} = Take[args, 3];
blocks = Drop[args, 3];
$HistoryLength = 0;

zLoad[b_] := Module[{mx = FileNameJoin[{vdir, b <> ".mx"}], wx = FileNameJoin[{vdir, b <> ".wxf"}]},
  ClearAll[FR$Vert];
  Which[FileExistsQ[mx], Get[mx], FileExistsQ[wx], FR$Vert = Import[wx, "WXF"],
    True, Print["[abort] no ", b, " in ", vdir]; Exit[1]];
  If[! ListQ[FR$Vert], Print["[abort] ", b, " does not hold a vertex list"]; Exit[1]];
  FR$Vert];

(* ---- dump ---- *)
zIdx[x_] := Switch[x[[2]], _FeynRules`Ext, x[[2, 1]], _Symbol, SymbolName[x[[2]]],
  _, Print["[abort] an index this script cannot read: ", x]; Exit[1]];
zFrac[z_] := With[{r = Rationalize[z, 0]}, {Numerator[Re[r]], Denominator[Re[r]], Numerator[Im[r]], Denominator[Im[r]]}];
zTerm[t_] := Module[{zf = If[Head[t] === Times, List @@ t, {t}], zc = 1, zcol = {}, zlor = {}, zpar = <||>},
  (* a tensor to a power is that tensor several times: SP[1, 2]^2 at four gluons *)
  zf = Flatten[Replace[zf, Power[zb_ /; Head[zb] =!= Symbol, ze_Integer?Positive] :> ConstantArray[zb, ze], {1}]];
  Do[Which[
      NumericQ[x], zc *= x,
      Head[x] === Symbol, zpar[SymbolName[x]] = Lookup[zpar, SymbolName[x], 0] + 1,
      Head[x] === Power && Head[x[[1]]] === Symbol, zpar[SymbolName[x[[1]]]] = Lookup[zpar, SymbolName[x[[1]]], 0] + x[[2]],
      MemberQ[{"f", "dSUN", "IndexDelta"}, SymbolName[Head[x]]], AppendTo[zcol, Prepend[zIdx /@ (List @@ x), SymbolName[Head[x]]]],
      MemberQ[{"ME", "Eps"}, SymbolName[Head[x]]], AppendTo[zlor, Prepend[zIdx /@ (List @@ x), SymbolName[Head[x]]]],
      SymbolName[Head[x]] === "FV", AppendTo[zlor, {"FV", x[[1]], zIdx[x[[2]]]}],
      SymbolName[Head[x]] === "SP", AppendTo[zlor, {"SP", x[[1]], x[[2]]}],
      True, Print["[abort] a factor this script cannot read: ", x]; Exit[1]], {x, zf}];
  <|"c" -> zFrac[zc], "par" -> zpar, "col" -> zcol, "lor" -> zlor|>];
zTerms[e_] := Module[{zx = Expand[e]}, Which[zx === 0, {}, Head[zx] === Plus, zTerm /@ (List @@ zx), True, {zTerm[zx]}]];

If[mode === "dump",
  Module[{out = <||>},
    Do[Module[{vs = zLoad[b]},
        If[! AllTrue[vs, Union[#[[1, All, 1]]] === {FeynRules`G} &],
          Print["[abort] ", b, " has a vertex with a field that is no gluon"]; Exit[1]];
        out[b] = Function[v, <|"legs" -> Length[v[[1]]], "terms" -> zTerms[v[[2]]]|>] /@ vs;
        Print["[dump] ", b, ": ", ({#["legs"], Length[#["terms"]]} & /@ out[b])]], {b, blocks}];
    Export[target, out, "RawJSON"];
    Print["[wrote] ", target]];
  Exit[0]];

(* ---- merge ---- *)
zLor[x_Integer] := FeynRules`Index[FeynRules`Lorentz, FeynRules`Ext[x]];
zGlu[x_Integer] := FeynRules`Index[FeynRules`Gluon, If[x > 0, FeynRules`Ext[x], Symbol["Gluon$c" <> ToString[-x]]]];
zCol[{"f", a_, b_, c_}] := FeynRules`f[zGlu[a], zGlu[b], zGlu[c]];
zCol[{"d", a_, b_, c_}] := FeynRules`dSUN[zGlu[a], zGlu[b], zGlu[c]];
zEnt[{"m", a_, b_}] := FeynRules`ME[zLor[a], zLor[b]];
zEnt[{"v", k_, a_}] := FeynRules`FV[k, zLor[a]];
zEnt[{"e", args__}] := Module[{zk = 0, zp = 1, zout},
  zout = Map[If[# > 0, zLor[#],
      Module[{zd = FeynRules`Index[FeynRules`Lorentz, Symbol["Lorentz$c" <> ToString[++zk]]]}, zp *= FeynRules`FV[-#, zd]; zd]] &, {args}];
  zp FeynRules`Eps @@ zout];
zVertex[zn_, zterms_, zwc_] := Module[{zlegs = Table[{FeynRules`G, k}, {k, zn}]},
  (* i (-i)^(8-n) (-1)^(n-4), see validate/g4_highleg.py *)
  {zlegs, Times[If[zn == 8, I, -1], Symbol[zwc], FeynRules`gs^(zn - 4), Global`Lam^(-4),
     Total[Function[zt, Rational[zt[[1]], zt[[2]]] (Times @@ (zCol /@ zt[[3]])) (Times @@ (zEnt /@ zt[[4]]))] /@ zterms]]}];

If[mode === "merge",
  (* the vertices are computed here and not kept between runs, so they cannot be those of an older gen.fr *)
  z9root = If[Environment["DIM8_ROOT"] === $Failed, ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
  z9pairs = StringSplit[#, "="] & /@ blocks;
  If[! AllTrue[z9pairs, Length[#] == 2 &], Print["[abort] merge takes <block>=<coefficient>"]; Exit[2]];
  z9rc = Run["python3 '" <> FileNameJoin[{z9root, "validate", "g4_highleg.py"}] <> "' write '" <>
    FileNameJoin[{z9root, "tests", "gen_smoke", "gen.fr"}] <> "' '" <> target <> "' " <> StringRiffle[z9pairs[[All, 2]], " "]];
  If[z9rc =!= 0, Print["[abort] validate/g4_highleg.py write stopped with status ", z9rc]; Exit[1]];
  blocks = z9pairs[[All, 1]];
  Do[Module[{st = FileNameJoin[{vdir, b <> ".status"}], line, zj, vs, zadd, zold, znew, zlegs, zout, zext},
      If[! FileExistsQ[st], Print["[abort] no status line for ", b]; Exit[1]];
      line = Import[st, "Text"];
      If[! StringContainsQ[line, "maxlegs 6"],
        Print["[abort] ", b, " was not built up to six legs, so it holds FeynRules' own vertices beyond them"]; Exit[1]];
      zj = Import[FileNameJoin[{target, b <> ".highleg.json"}], "RawJSON"];
      vs = Select[zLoad[b], Length[#[[1]]] <= 6 &];
      zadd = KeyValueMap[zVertex[ToExpression[#1], #2, zj["wc"]] &, zj["vertices"]];
      (* the symbols of the new vertices must be those of the block's own, or WriteUFO cannot read them *)
      zold = Union[Cases[vs, _Symbol, {0, Infinity}, Heads -> True]];
      znew = Union[Cases[zadd, _Symbol, {0, Infinity}, Heads -> True]];
      (* the metric tensor is new to a block that FeynRules built with its Eps pair as written *)
      znew = Select[Complement[znew, zold, {FeynRules`ME}], ! StringContainsQ[SymbolName[#], "$c"] &];
      If[znew =!= {}, Print["[abort] ", b, ": the new vertices hold symbols the block does not: ", znew]; Exit[1]];
      zout = Join[vs, zadd];
      zlegs = Sort[Length[#[[1]]] & /@ zadd];
      FR$Vert = zout;
      zext = If[FileExistsQ[FileNameJoin[{vdir, b <> ".mx"}]], "mx", "wxf"];
      With[{ztmp = FileNameJoin[{vdir, b <> ".highleg." <> zext}], zdest = FileNameJoin[{vdir, b <> "." <> zext}]},
        If[zext === "mx", DumpSave[ztmp, FR$Vert], Export[ztmp, FR$Vert, "WXF"]];
        RenameFile[ztmp, zdest, OverwriteTarget -> True]];
      line = StringReplace[line, RegularExpression["\\|\\s*highleg [^|]*(\\||$)"] -> "$1"];
      line = StringReplace[line, RegularExpression["\\| vertices [0-9]+"] -> "| vertices " <> ToString[Length[zout]]];
      line = StringReplace[line, RegularExpression["\\|\\s*src "] ->
        "| highleg " <> If[zlegs === {}, "none", StringRiffle[ToString /@ zlegs, " "]] <> " | src "];
      If[! StringContainsQ[line, "highleg"], line = StringTrim[line] <> " | highleg " <> If[zlegs === {}, "none", StringRiffle[ToString /@ zlegs, " "]]];
      Export[st, line, "Text"];
      Print["[merge] ", b, ": added ", If[zlegs === {}, "nothing, its vertices are zero", zlegs], " | ", line]], {b, blocks}];
  Exit[0]];
Print["[abort] unknown mode ", mode]; Exit[2];
