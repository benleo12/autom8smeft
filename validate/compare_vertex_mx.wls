(* validate/compare_vertex_mx.wls -- compare two vertex caches coupling by coupling.

   Usage: wolframscript -file compare_vertex_mx.wls <dirA> <dirB> <block> [<block> ...]

   Every vertex of A must appear in B with the same field content and a coupling whose
   difference canonicalises to zero.  The two caches may store different but equivalent
   forms (the averaging canonicaliser produced symmetrised sums, the current one a single
   canonical representative), so the difference has to go through canonCoup and the numeric
   colour test, exactly as the worker does when it decides a vertex vanishes.

   The model MUST be loaded first: the cached expressions carry FeynRules` heads (Eps, f,
   Index, T), and without FeynRules on the context path the rules below would be written in
   Global` and match nothing, reporting every vertex as different. *)
$root = "${DIM8_ROOT:-.}";
z9args = Rest[$ScriptCommandLine];
FR$NKernels = 0;
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
LoadModel[If[Environment["DIM8_BASE"] === $Failed, "base.fr", Environment["DIM8_BASE"]], "gen.fr"];
Unprotect[$RecursionLimit]; $RecursionLimit = 20000;

canonEps = Eps[z8args__] :> Signature[{z8args}] Eps[Sequence @@ Sort[{z8args}]];
canonF = f[z8args__] :> Signature[{z8args}] f[Sequence @@ Sort[{z8args}]];
dummies[z8e_] := Union[Cases[z8e, Index[_, _Symbol?(StringContainsQ[ToString[#], "$"] &)], Infinity]];
(* Averaging over all relabellings is exact but factorial in the number of dummies of one
   type; the class-14 W blocks (up to ten Lorentz dummies per coupling) never finished.
   Instead each monomial is brought to a canonical relabelling: the factors are ordered by a
   dummy-blind key, the dummies are renamed in order of first appearance, and among factors
   whose keys tie every ordering is tried and the Order-minimal result kept.  Two monomials
   equal up to dummy names then coincide exactly, which is all Expand needs to cancel them. *)
dummyQ[z8s_Symbol] := StringContainsQ[ToString[z8s], "$"];
blind[z8fac_] := z8fac /. Index[z8ty_, _Symbol?dummyQ] :> Index[z8ty, Z8DUM];
canonName[z8ty_, z8k_] := Index[z8ty, Symbol[ToString[z8ty] <> "$c" <> ToString[z8k]]];
renameByAppearance[z8facs_List] := Module[{z8seen, z8counts, z8rules},
  z8seen = DeleteDuplicates[Cases[z8facs, Index[_, _Symbol?dummyQ], Infinity]];
  z8counts = <||>;
  z8rules = (z8counts[#[[1]]] = Lookup[z8counts, #[[1]], 0] + 1; # -> canonName[#[[1]], z8counts[#[[1]]]]) & /@ z8seen;
  Times @@ (z8facs /. z8rules)];
canonTerm[z8t_] := Module[{z8facs, z8groups, z8orderings},
  If[FreeQ[z8t, Index[_, _Symbol?dummyQ]], Return[z8t]];
  z8facs = If[Head[z8t] === Times, List @@ z8t, {z8t}];
  z8groups = SortBy[GatherBy[z8facs, blind], blind[First[#]] &];
  z8orderings = Tuples[Permutations /@ z8groups];
  oddUnderSwapQ[First[Sort[renameByAppearance[Flatten[#]] & /@ z8orderings]]]];
(* a single monomial that changes sign when two of its own dummies of one type are swapped
   (p^m1 p^m2 Eps[m1, m2, ...]) is zero by itself; the averaging saw that, the canonical
   relabelling alone does not, so test every same-type pair explicitly *)
oddUnderSwapQ[z8t_] := Module[{z8byType, z8pairs},
  z8byType = GatherBy[dummies[z8t], First];
  z8pairs = Flatten[Subsets[#, {2}] & /@ z8byType, 1];
  If[AnyTrue[z8pairs, (z8t /. {#[[1]] -> #[[2]], #[[2]] -> #[[1]]}) === -z8t &], 0, z8t]];
symDummies[z8e_] := Module[{z8x = Expand[z8e]},
  If[Head[z8x] === Plus, Total[canonTerm /@ List @@ z8x], canonTerm[z8x]]];
canonCoup[z8c_] := Module[{z8e},
  z8e = Expand[symDummies[Expand[z8c /. canonEps /. canonF]] /. canonEps /. canonF];
  If[z8e === 0, 0, Simplify[z8e, TimeConstraint -> 10]]];   (* the zero test is exact after Expand; Simplify only compacts *)
(* Third syntactic zero, found on a charge-conjugated colour-epsilon chain
   (tests/gen_smoke/cctest.log, L3): the traceless-generator identity
   eps_{abd} T_{dc} + eps_{bcd} T_{da} + eps_{cad} T_{db} = 0, which no rewriting rule above
   knows.  Rather than collect SU(3) identities one by one, evaluate the colour algebra
   numerically: external colour/gluon indices get random values, dummies are summed, and
   T, f, d, Eps become numbers.  Whatever spin/Lorentz structure remains must vanish
   identically for a handful of random assignments; a nonzero tensor is caught with
   probability one.  Only used on couplings that survived canonCoup. *)
gellMann = {{{0,1,0},{1,0,0},{0,0,0}}, {{0,-I,0},{I,0,0},{0,0,0}}, {{1,0,0},{0,-1,0},{0,0,0}},
  {{0,0,1},{0,0,0},{1,0,0}}, {{0,0,-I},{0,0,0},{I,0,0}}, {{0,0,0},{0,0,1},{0,1,0}},
  {{0,0,0},{0,0,-I},{0,I,0}}, {{1,0,0},{0,1,0},{0,0,-2}}/Sqrt[3]};
tNum[z8a_, z8i_, z8j_] := gellMann[[z8a, z8i, z8j]]/2;
fNum = Table[-2 I Tr[(gellMann[[z8a]].gellMann[[z8b]] - gellMann[[z8b]].gellMann[[z8a]]).gellMann[[z8c]]]/8, {z8a, 8}, {z8b, 8}, {z8c, 8}] // Simplify;
dNum = Table[2 Tr[(gellMann[[z8a]].gellMann[[z8b]] + gellMann[[z8b]].gellMann[[z8a]]).gellMann[[z8c]]]/8, {z8a, 8}, {z8b, 8}, {z8c, 8}] // Simplify;
colourQ[z8e_] := !FreeQ[z8e, Index[Colour | Gluon, _]];
(* colour zero test: the worker's exact version (exhaustive over the external colour
   assignments), loaded from fr_worker.wls so the two can never drift apart again; the
   sampled six-seed copy that used to live here was unsound for sparse tensors (2026-09-03) *)
Module[{z8w = Import[$root <> "/validate/fr_worker.wls", "Text"], z8a, z8b},
  z8a = StringPosition[z8w, "colourQ[z8e_] :="][[1, 1]]; z8b = StringPosition[z8w, "canonVerts[z8v_List] :="][[1, 1]];
  ToExpression[StringTake[z8w, {z8a, z8b - 1}]]];

z9load[z9f_] := (Clear[FR$Vert]; Get[z9f]; FR$Vert);
z9fail = 0;
Do[
  z9A = z9load[z9args[[1]] <> "/" <> z9b <> ".mx"]; z9B = z9load[z9args[[2]] <> "/" <> z9b <> ".mx"];
  z9bad = 0; z9miss = 0;
  Do[z9pos = Position[z9B[[All, 1]], z9v[[1]]];
     If[z9pos === {}, z9miss++; Print["  missing in B: ", z9v[[1]]],
       z9d = canonCoup[z9v[[2]] - z9B[[z9pos[[1, 1]], 2]]];
       If[z9d =!= 0 && !colourZeroQ[z9d], z9bad++; Print["  DIFFERS: ", z9v[[1]]]]],
     {z9v, z9A}];
  If[z9miss > 0 || z9bad > 0 || Length[z9A] =!= Length[z9B], z9fail++];
  Print["[compare] ", z9b, " A ", Length[z9A], " B ", Length[z9B], " missing ", z9miss, " differing ", z9bad,
        If[z9miss == 0 && z9bad == 0 && Length[z9A] == Length[z9B], "  IDENTICAL", "  MISMATCH"]],
  {z9b, z9args[[3 ;;]]}];
Print["[alldone] blocks ", Length[z9args] - 2, " mismatched ", z9fail];
