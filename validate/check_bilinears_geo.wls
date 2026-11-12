(* validate/check_bilinears_geo.wls N  --  are the quadratic terms of the model of order N canonical through t^N?

   validate/check_bilinears.wls for the models of order N (gen/towers.py), whose base (gen/input_scheme.py
   write_variant with n = N) carries the input relations, the rotation of the neutral gauge fields, the
   rescalings of W, h and the gluon, the quartic and the Yukawas to O(t^N), t = 1/Lambda^2, and whose
   operators of NP order p carry those corrections to order N - p.  The two-point terms are the place
   where all of them meet: the gauge kinetic and mass matrices, the Higgs kinetic term and mass.

   The Lagrangian is the Standard Model of the base plus every block with a bosonic two-point term at the
   vacuum: the dimension-six classes X^2H^2 (G6cl4), H^6 (G6cl2) and H^4D^2 (G6cl3), and the members of
   every dimension of the connection classes H^8, H^6D^2 and X^2H^4 (gen_geo<N>.json).  Every coefficient
   with an NP order p is switched on at c_p t^p, with c_p a fixed number times 3^p and Lambda = 1 TeV,
   so that each order is a few per cent of the one before at t = 1.  The coefficients of operators
   with no two-point term are on as well: those that enter G_F move the vev, which the mass terms see.
   Each two-point residue must fall by 2^(N+1) per halving of t from t = 1/2 to 1/64.  The last ratio whose
   residue is above 10^-13 of the scale decides and must reach 0.85 of 2^(N+1).  A residue left at order k < N + 1 falls by 2^k only.  The mass parameter of the potential
   is solved for at the minimum, as in validate/check_bilinears.wls, so the Higgs mass is part of the test.

     DIM8_ROOT=... wolframscript -file validate/check_bilinears_geo.wls 4 [PREFIX]
   reads tests/gen_smoke/base_geo4_mw.fr, dim6_geo.fr, gen_geo4.fr and gen_geo4.json.  At order N the towers are
   those of gen_geo<N>.fr and gen_geo<N>.json (gen_geo2 at N = 1).  Where tests/gen_smoke holds no gen_geo<N>.fr
   the check reads gen_geo4.fr and gen_geo4.json in their place and takes from them the blocks up to the
   dimension 2N + 4, and its line "[bilinear] base ... towers ..." names the file it read.  With PREFIX the blocks
   whose names start with it are left out (T12 for the members of dimension twelve), and the test must then
   fail: that is the check that it can.  The exit status is 0 when every residue passes and 1 otherwise.
   The quadratic terms and the potential are taken unit by unit, the blocks one by one and LSM summand by
   summand, and each unit is kept (validate/twopoint_units.m).  A block is evaluated with the cap of two
   doublet fields on its own expansion (z9block2 below), so its unit holds its terms with at most two doublet
   fields: all of its two-point terms, and of its potential the terms through H^2, which hold the tadpole and
   the mass.  At order 4, where they take most of the time,
   K runs with DIM8_TWOPOINT_PREP=1 started at once share the units and quit, and a run without it reads them
   and does the check (hpc/twopoint_geo.sh).  The runs with and without PREFIX share the units they have in
   common.  DIM8_PROGRESS names a file that gets every line of the report as it is written.
*)
$root = If[Environment["DIM8_ROOT"] === $Failed, ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9N = ToExpression[$ScriptCommandLine[[2]]];
z9base = "base_geo" <> ToString[z9N] <> "_mw.fr";
z9drop = If[Length[$ScriptCommandLine] >= 3, $ScriptCommandLine[[3]], None];
z9gen = "gen_geo" <> ToString[Max[z9N, 2]] <> ".fr";
z9gen = If[FileExistsQ[z9gen], z9gen, "gen_geo4.fr"];
z9miss = Select[{z9base, "dim6_geo.fr", z9gen, "gen.fr", StringReplace[z9gen, ".fr" -> ".json"]}, ! FileExistsQ[#] &];
If[z9miss =!= {}, Print["[bilinear] ABORT: not in ", Directory[], ": ", z9miss]; Quit[1]];
LoadModel[z9base, "dim6_geo.fr", z9gen, "gen.fr"];
Print["[bilinear] base ", z9base, "  towers ", z9gen, "  order ", z9N, "  z8geoN ", z8geoN];
If[z8geoN =!= z9N, Print["[bilinear] ABORT: the base is of order ", z8geoN]; Quit[1]];
(* the two-point terms are taken with validate/truncexp.m: no term with more than two doublet fields is
   built, so a block of twelve doublets is not multiplied out *)
Get[$root <> "/validate/truncexp.m"];
Get[$root <> "/validate/twopoint_units.m"];
(* A block's Module expands its operator with ExpandIndices before anything here sees it: (H^dagger H)^2
   Q_{H^6}^{(1)} with its ten doublets into every term with up to twelve legs, each of which the Module then
   rotates and truncates (z8geoTrunc), 15805 s at order 4.  The check uses the terms with at most two doublet
   fields.  While z9capOn is set, a call of ExpandIndices goes through z9expandIdxB with the cap of two, as
   validate/fr_worker.wls takes a block monomial by monomial with its leg cap: the terms kept are terms of
   the full expansion, and the steps of the Module after it act on them as they did.  The parameter sums that
   validate/truncexp.m abbreviates are put back at once, except in a block that hands its sum to z8geoTrunc
   in its Return (the blocks of gen/towers.py): there they stay abbreviated through the steps in between, as in
   the worker, and are put back as z8geoTrunc takes the sum, which has to see them to cut their products.
   OptimizeIndex on the sums written out takes twenty minutes for such a block of dimension twelve, and 13 s
   this way.  DIM8_TRUNCEXP=0 gives the full expansion back. *)
z9capOn = False; z9late = False; z9gt = 0;
DownValues[ExpandIndices] = Prepend[DownValues[ExpandIndices],
  HoldPattern[ExpandIndices[z9m_, z9o___] /; z9capOn] :> Block[{z9capOn = False}, If[z9late, z9expandIdxB[z9m, 2, z9o], z9expandIdxB[z9m, 2, z9o] /. z9abbrevBack]]];
DownValues[z8geoTrunc] = Prepend[DownValues[z8geoTrunc],
  HoldPattern[z8geoTrunc[z9L_, z9q_] /; z9capOn && z9late] :> Block[{z9late = False}, z9gt++; z8geoTrunc[z9L /. z9abbrevBack, z9q]]];
z9towerQ[z9b_String] := MatchQ[Cases[Extract[ToExpression[z9b, InputForm, OwnValues], {1, 2}, Hold], HoldPattern[Return[z9r_]] :> Hold[z9r], Infinity],
  {Hold[z8geoTrunc[_, _Integer]]}];
z9block2[z9b_String] := Module[{z9x},
  Block[{z9capOn = True, z9late = z9towerQ[z9b], z9gt = 0},
    z9x = Symbol[z9b];
    If[z9late && z9gt =!= 1, z9say["[bilinear] ABORT: ", z9b, " passed its sum through z8geoTrunc ", z9gt, " times, not once"]; Quit[1]]];
  z9x /. z9abbrevBack];

(* the connection blocks with a bosonic two-point term, up to the dimension 2N + 4 *)
z9json = Import[StringReplace[z9gen, ".fr" -> ".json"], "RawJSON"];
z9blocks = Join[{"G6cl2", "G6cl3", "G6cl4"},
  #["block"] & /@ Select[z9json, MemberQ[{2, 3, 6}, #["cls"]] && #["dim"] <= 2 z9N + 4 &]];
If[z9drop =!= None, z9blocks = Select[z9blocks, ! StringStartsQ[#, z9drop] &]; z9say["[bilinear] NEGATIVE CONTROL: blocks ", z9drop, "* left out"]];
z9say["[bilinear] blocks: ", z9blocks];

z9f[z9x_] := If[! NumericQ[z9x], "NOT NUMERIC", If[z9x == 0, "0", ToString[InputForm[N[Round[z9x, 10.^(Floor[Log10[Abs[z9x]]] - 2)]]]]]];
z9npOf[z9p_] := Module[{z9io = InteractionOrder /. Flatten[{z9p[[2]]}]},
  If[z9io === InteractionOrder, 0, Total[Cases[If[MatchQ[z9io, {_Symbol, _Integer}], {z9io}, z9io], {NP, z9n_Integer} :> z9n]]]];
z9ext = Select[M$Parameters, (ParameterType /. Flatten[{#[[2]]}]) === External && z9npOf[#] > 0 &];
SeedRandom[20261108];
z9c = (#[[1]] -> {z9npOf[#], RandomReal[{-1, 1}] 3^z9npOf[#]}) & /@ z9ext;
z9say["[bilinear] coefficients on: ", Length[z9c], " (", Counts[z9c[[All, 2, 1]]], " by NP order)"];
(* every parameter at the point t, from validate/geo_numeric.m: UpdateParameters takes minutes per call here *)
Get[$root <> "/validate/geo_numeric.m"];
z9rulesAt[z9t_] := z8numRules[Join[{Lam -> 1000.}, (#[[1]] -> #[[2, 2]] z9t^#[[2, 1]]) & /@ z9c]];
z9coef[z9x_] := Which[NumericQ[z9x], Abs[N[z9x]], Head[z9x] === Times, Abs[N[Times @@ Cases[z9x, _?NumericQ, {1}]]], True, 1.];
z9params := Join[First /@ M$Parameters, {MZ, MH}];
z9left[z9e_] := Intersection[Cases[z9e, _Symbol, {0, Infinity}], z9params];
z9mag[z9e_, z9r_, z9kin_] := Module[{z9y = Expand[z9e /. z9r], z9l},
  z9l = Select[If[Head[z9y] === Plus, List @@ z9y, {z9y}], If[z9kin, ! FreeQ[#, FV | SP] &, FreeQ[#, FV | SP] &]];
  If[z9l === {} || z9y === 0, 0., Max[z9coef /@ z9l]]];

(* the quadratic terms and the potential unit by unit, the blocks one by one and LSM summand by summand
   (validate/twopoint_units.m): FeynRules takes time that grows faster than the number of terms, and the
   quadratic part of a sum is the sum of the quadratic parts.  GetQuadraticTerms is ExpandIndices with
   MaxParticles -> 2, MinParticles -> 2 and SymmetryFactor -> True (ToolBox.m), here with the cap of two
   doublet fields *)
z9quad[z9x_] := z9expandIdxB[z9x, 2, MaxParticles -> 2, MinParticles -> 2, SymmetryFactor -> True] /. z9abbrevBack;
z9potOf[z9x_] := Expand[z9x /. {(A | Z | W | Wbar)[_] -> 0, G[__] -> 0, _Dot -> 0, del[__] -> 0}];
(* a block is evaluated only by the run that computes it, and known by the model files, and the blocks come
   first, since some take long to evaluate and the runs then start on them at once.  The name of a block's
   unit says that it holds the terms with at most two doublet fields *)
z9files = {z9base, "dim6_geo.fr", z9gen, "gen.fr"};
z9qp = z9units["bil" <> ToString[z9N], Join[{# <> ".cap2", Hold[z9block2[#]], z9files} & /@ z9blocks, z9splitSum["LSM", LSM]], {z9quad[#], z9potOf[#]} &];
If[z9prep, Quit[0]];
{z9q, z9pot} = z9qp;
z9F[z9v_, z9m_, z9n_] := del[z9v[z9n], z9m] - del[z9v[z9m], z9n];
z9can = -1/4 z9F[A, mu, nu] z9F[A, mu, nu] - 1/4 z9F[Z, mu, nu] z9F[Z, mu, nu] + 1/2 MZ^2 Z[mu] Z[mu] -
  1/2 z9F[Wbar, mu, nu] z9F[W, mu, nu] + MW^2 Wbar[mu] W[mu] + 1/2 del[H, mu] del[H, mu] - 1/2 MH^2 H^2 -
  1/4 (del[G[nu, aa], mu] - del[G[mu, aa], nu]) (del[G[nu, aa], mu] - del[G[mu, aa], nu]);
z9bos = {A, Z, W, Wbar, H, G};
(* the spectator G0 carries no momentum, as in validate/check_bilinears.wls *)
z9atrest[{z9p_, z9e_}] := Module[{z9g = First[Select[z9p, #[[1]] === G0 &]][[2]], z9o, z9a, z9b},
  z9o = DeleteCases[z9p[[All, 2]], z9g]; {z9a, z9b} = z9o;
  {z9p, Expand[z9e /. {FV[z9g, _] -> 0, SP[z9g, _] -> 0, SP[_, z9g] -> 0} /.
     {FV[z9b, z9m_] :> -FV[z9a, z9m], SP[z9b, z9b] -> SP[z9a, z9a], SP[z9a, z9b] -> -SP[z9a, z9a], SP[z9b, z9a] -> -SP[z9a, z9a]}]}];
z9pick[z9v_] := z9atrest /@ Select[z9v, SubsetQ[z9bos, DeleteCases[#[[1, All, 1]], G0]] &];
z9ref = z9pick[FeynmanRules[G0 z9can, ScreenOutput -> False]];
z9tf = First[AbsoluteTiming[z9dif = z9pick[FeynmanRules[G0 (z9q - z9can), ScreenOutput -> False]]]];
z9say["[bilinear] two-point structures in the canonical reference: ", Sort[#[[1, All, 1]] & /@ z9ref]];
z9say["[bilinear] two-point structures in (Lagrangian - canonical): ", Sort[#[[1, All, 1]] & /@ z9dif], " (", Round[z9tf], " s)"];
(* the tadpole and the mass: the terms of the potential in H and H^2, which every unit holds in full *)
z9tad = Coefficient[z9pot, H, 1]; z9m2 = -2 Coefficient[z9pot, H, 2];
z9ts = 2^-Range[6];   (* t = 1/2 ... 1/64: the t^(N+1) fall only shows once the higher terms have died away *)
z9rs = Function[z9t, Module[{z9r = DeleteCases[z9rulesAt[z9t], muH -> _], z9mu2, z9sol},
    z9sol = z9mu2 /. First[Solve[(z9tad /. muH -> Sqrt[z9mu2] /. z9r) == 0, z9mu2]];
    z9say["[potential] t = ", z9t, "  muH^2 at the minimum / (MH^2/2) - 1 = ", z9f[z9sol/(MH^2/2 /. z9r) - 1],
          "   (m_h^2 - MH^2)/MH^2 = ", z9f[((z9m2 /. muH -> Sqrt[z9sol]) - MH^2 /. z9r)/(MH^2 /. z9r)]];
    Append[z9r, muH -> Sqrt[z9sol]]]] /@ z9ts;
Module[{z9l = Union @@ (z9left[Expand[#[[2]] /. z9rs[[1]]]] & /@ z9dif)},
  If[z9l =!= {}, z9say["[bilinear] ABORT: parameters with no numerical value: ", z9l]; Quit[1]]];
z9refmag[z9kin_] := Association[(Sort[DeleteCases[#[[1, All, 1]], G0]] -> z9mag[#[[2]], z9rs[[1]], z9kin]) & /@ z9ref];
z9want = 2^(z9N + 1);
z9bad = 0;
Do[Module[{z9ok, z9k = Sort[DeleteCases[z9v[[1, All, 1]], G0]], z9m, z9sc},
   Do[z9m = z9mag[z9v[[2]], #, z9kin] & /@ z9rs;
      z9sc = Lookup[z9refmag[z9kin], Key[z9k], 0.]; If[z9sc == 0., z9sc = If[z9kin, 1., MZ^2 /. z9rs[[1]]]];
      z9ok = Select[Range[Length[z9m] - 1], z9m[[# + 1]] > 10^-13 z9sc &];
      z9say["[twopoint] ", z9k, If[z9kin, "  kinetic", "  mass   "], " residue/canonical at t = 1/2 ... 1/64: ", z9f /@ (z9m/z9sc),
            "   ratios ", If[z9ok === {}, "below 10^-13 from t = 1/4", z9f /@ (z9m[[z9ok]]/z9m[[z9ok + 1]])]];
      (* the last ratio above the floor decides: a residue left at order k < N + 1 tends to 2^k there *)
      If[z9ok =!= {} && z9m[[Last[z9ok]]]/z9m[[Last[z9ok] + 1]] < 0.85 z9want, z9bad++], {z9kin, {True, False}}]], {z9v, z9dif}];
z9say["[bilinear] ", If[z9bad == 0, "PASS: every two-point residue falls as t^" <> ToString[z9N + 1],
  ToString[z9bad] <> " two-point residues fall slower than t^" <> ToString[z9N + 1]]];
z9say["[alldone]"];
Quit[If[z9bad == 0, 0, 1]];
