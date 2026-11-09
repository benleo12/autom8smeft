(* validate/check_bilinears_geo.wls N  --  are the quadratic terms of the model of order N canonical through t^N?

   validate/check_bilinears.wls for the models of order N (gen/towers.py), whose base (gen/input_scheme.py
   write_variant with n = N) carries the input relations, the rotation of the neutral gauge fields, the
   rescalings of W, h and the gluon, the quartic and the Yukawas to O(t^N), t = 1/Lambda^2, and whose
   operators of NP order p carry those corrections to order N - p.  The two-point terms are the place
   where all of them meet: the gauge kinetic and mass matrices, the Higgs kinetic term and mass.

   The Lagrangian is the Standard Model of the base plus every block with a bosonic two-point term at the
   vacuum: the dimension-six classes X^2H^2 (G6cl4), H^6 (G6cl2) and H^4D^2 (G6cl3), and the members of
   every dimension of the connection classes H^8, H^6D^2 and X^2H^4 (gen_geo<N>.json).  Every coefficient
   with an NP order p is switched on at c_p t^p, with c_p a fixed number times 3^p and Lambda = Lambda_6 =
   1 TeV, so that each order is a few per cent of the one before at t = 1.  The coefficients of operators
   with no two-point term are on as well: those that enter G_F move the vev, which the mass terms see.
   Each two-point residue must fall by 2^(N+1) per halving of t (by at least 0.75 of it), from t = 1/2 to
   1/4 to 1/8.  A residue left at order k < N + 1 falls by 2^k only.  The mass parameter of the potential
   is solved for at the minimum, as in validate/check_bilinears.wls, so the Higgs mass is part of the test.

     DIM8_ROOT=... wolframscript -file validate/check_bilinears_geo.wls 4 [PREFIX]
   reads tests/gen_smoke/base_geo4_mw.fr, dim6_geo.fr, gen_geo4.fr and gen_geo4.json.  With PREFIX the blocks
   whose names start with it are left out (T12 for the members of dimension twelve), and the test must then
   fail: that is the check that it can.
*)
$root = Environment["DIM8_ROOT"];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9N = ToExpression[$ScriptCommandLine[[2]]];
z9base = "base_geo" <> ToString[z9N] <> "_mw.fr";
z9drop = If[Length[$ScriptCommandLine] >= 3, $ScriptCommandLine[[3]], None];
z9gen = "gen_geo" <> ToString[Max[z9N, 2]] <> ".fr";
z9gen = If[FileExistsQ[z9gen], z9gen, "gen_geo4.fr"];
LoadModel[z9base, "dim6_geo.fr", z9gen, "gen.fr"];
Print["[bilinear] base ", z9base, "  towers ", z9gen, "  order ", z9N, "  z8geoN ", z8geoN];
If[z8geoN =!= z9N, Print["[bilinear] ABORT: the base is of order ", z8geoN]; Quit[1]];

(* the connection blocks with a bosonic two-point term, up to the dimension 2N + 4 *)
z9json = Import[StringReplace[z9gen, ".fr" -> ".json"], "RawJSON"];
z9blocks = Join[{"G6cl2", "G6cl3", "G6cl4"},
  #["block"] & /@ Select[z9json, MemberQ[{2, 3, 6}, #["cls"]] && #["dim"] <= 2 z9N + 4 &]];
If[z9drop =!= None, z9blocks = Select[z9blocks, ! StringStartsQ[#, z9drop] &]; Print["[bilinear] NEGATIVE CONTROL: blocks ", z9drop, "* left out"]];
Print["[bilinear] blocks: ", z9blocks];

z9f[z9x_] := If[! NumericQ[z9x], "NOT NUMERIC", If[z9x == 0, "0", ToString[InputForm[N[Round[z9x, 10.^(Floor[Log10[Abs[z9x]]] - 2)]]]]]];
z9npOf[z9p_] := Module[{z9io = InteractionOrder /. Flatten[{z9p[[2]]}]},
  If[z9io === InteractionOrder, 0, Total[Cases[If[MatchQ[z9io, {_Symbol, _Integer}], {z9io}, z9io], {NP, z9n_Integer} :> z9n]]]];
z9ext = Select[M$Parameters, (ParameterType /. Flatten[{#[[2]]}]) === External && z9npOf[#] > 0 &];
SeedRandom[20261108];
z9c = (#[[1]] -> {z9npOf[#], RandomReal[{-1, 1}] 3^z9npOf[#]}) & /@ z9ext;
Print["[bilinear] coefficients on: ", Length[z9c], " (", Counts[z9c[[All, 2, 1]]], " by NP order)"];
(* every parameter at the point t, from validate/geo_numeric.m: UpdateParameters takes minutes per call here *)
Get[$root <> "/validate/geo_numeric.m"];
z9rulesAt[z9t_] := z8numRules[Join[{Lam -> 1000., Lam6 -> 1000.}, (#[[1]] -> #[[2, 2]] z9t^#[[2, 1]]) & /@ z9c]];
z9coef[z9x_] := Which[NumericQ[z9x], Abs[N[z9x]], Head[z9x] === Times, Abs[N[Times @@ Cases[z9x, _?NumericQ, {1}]]], True, 1.];
z9params := Join[First /@ M$Parameters, {MZ, MH}];
z9left[z9e_] := Intersection[Cases[z9e, _Symbol, {0, Infinity}], z9params];
z9mag[z9e_, z9r_, z9kin_] := Module[{z9y = Expand[z9e /. z9r], z9l},
  z9l = Select[If[Head[z9y] === Plus, List @@ z9y, {z9y}], If[z9kin, ! FreeQ[#, FV | SP] &, FreeQ[#, FV | SP] &]];
  If[z9l === {} || z9y === 0, 0., Max[z9coef /@ z9l]]];

z9L = LSM + Total[Symbol /@ z9blocks];
z9q = GetQuadraticTerms[z9L];
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
z9dif = z9pick[FeynmanRules[G0 (z9q - z9can), ScreenOutput -> False]];
Print["[bilinear] two-point structures in the canonical reference: ", Sort[#[[1, All, 1]] & /@ z9ref]];
Print["[bilinear] two-point structures in (Lagrangian - canonical): ", Sort[#[[1, All, 1]] & /@ z9dif]];
z9pot = Expand[z9L /. {(A | Z | W | Wbar)[_] -> 0, G[__] -> 0, _Dot -> 0, del[__] -> 0}];
z9tad = Coefficient[z9pot, H, 1]; z9m2 = -2 Coefficient[z9pot, H, 2];
z9ts = {1/2, 1/4, 1/8};
z9rs = Function[z9t, Module[{z9r = DeleteCases[z9rulesAt[z9t], muH -> _], z9mu2, z9sol},
    z9sol = z9mu2 /. First[Solve[(z9tad /. muH -> Sqrt[z9mu2] /. z9r) == 0, z9mu2]];
    Print["[potential] t = ", z9t, "  muH^2 at the minimum / (MH^2/2) - 1 = ", z9f[z9sol/(MH^2/2 /. z9r) - 1],
          "   (m_h^2 - MH^2)/MH^2 = ", z9f[((z9m2 /. muH -> Sqrt[z9sol]) - MH^2 /. z9r)/(MH^2 /. z9r)]];
    Append[z9r, muH -> Sqrt[z9sol]]]] /@ z9ts;
Module[{z9l = Union @@ (z9left[Expand[#[[2]] /. z9rs[[1]]]] & /@ z9dif)},
  If[z9l =!= {}, Print["[bilinear] ABORT: parameters with no numerical value: ", z9l]; Quit[1]]];
z9refmag[z9kin_] := Association[(Sort[DeleteCases[#[[1, All, 1]], G0]] -> z9mag[#[[2]], z9rs[[1]], z9kin]) & /@ z9ref];
z9want = 2^(z9N + 1);
z9bad = 0;
Do[Module[{z9k = Sort[DeleteCases[z9v[[1, All, 1]], G0]], z9m, z9sc},
   Do[z9m = z9mag[z9v[[2]], #, z9kin] & /@ z9rs;
      z9sc = Lookup[z9refmag[z9kin], Key[z9k], 0.]; If[z9sc == 0., z9sc = If[z9kin, 1., MZ^2 /. z9rs[[1]]]];
      Print["[twopoint] ", z9k, If[z9kin, "  kinetic", "  mass   "], " residue/canonical at t = 1/2, 1/4, 1/8: ", z9f /@ (z9m/z9sc),
            "   ratios ", If[z9m[[2]] > 0 && z9m[[3]] > 0, z9f /@ {z9m[[1]]/z9m[[2]], z9m[[2]]/z9m[[3]]}, "exact zero"]];
      If[z9m[[3]] > 10^-13 z9sc && z9m[[2]]/z9m[[3]] < 0.75 z9want, z9bad++], {z9kin, {True, False}}]], {z9v, z9dif}];
Print["[bilinear] ", If[z9bad == 0, "PASS: every two-point residue falls as t^" <> ToString[z9N + 1],
  ToString[z9bad] <> " two-point residues fall slower than t^" <> ToString[z9N + 1]]];
Print["[alldone]"];
