(* validate/check_bilinears.wls [operator file]  --  are the quadratic terms canonical at 1/Lambda^4?

   The base brings the Lagrangian to canonical form through second order: it shifts g, g' and the
   vev, rotates the neutral gauge fields and rescales W and h.  Its second-order relations were
   derived for the whole Lagrangian, that is assuming every dimension-six operator is evaluated on
   the shifted couplings and the rotated fields to first order.  Whether the operator file
   delivers that is a statement about two-point terms, and FeynRules computes no two-point
   vertices, MadGraph reads none, and a Ward identity sees only the charged and coloured ones.
   So nothing in the rest of the validation looks at the Z, the photon-Z mixing or the Higgs.

   This does.  Multiply the quadratic part of the Lagrangian, minus the canonical quadratic terms
   it is supposed to equal, by a spectator field that occurs nowhere else (the neutral Goldstone,
   absent in the unitary gauge).  Every two-point term becomes a three-point vertex and FeynRules
   computes it.  With the dimension-six coefficients of the input relations and cHG switched on at
   t, t/2 and t/4, each such vertex must fall by 8 per halving: a residue at second order falls
   by 4 and one at first order by 2.  The one-point term fixes the mass parameter of the potential,
   as it does in the derivation (see below), and the Higgs mass is then part of the test.

     DIM8_ROOT=... wolframscript -file validate/check_bilinears.wls [dim6_smeftsim.fr]
*)
$root = Environment["DIM8_ROOT"];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9ops = If[Length[$ScriptCommandLine] >= 2, $ScriptCommandLine[[2]], "dim6_smeftsim.fr"];
z9base = If[Length[$ScriptCommandLine] >= 3, $ScriptCommandLine[[3]], "base_inputscheme.fr"];
(* gen.fr as well: the second-order shifts of the base are functions of dimension-eight
   coefficients, which that file declares, and without it they have no numerical value and stay
   in every expression as symbols *)
LoadModel[z9base, z9ops, "gen.fr"];
z9f[z9x_] := If[! NumericQ[z9x], "NOT NUMERIC", If[z9x == 0, "0", ToString[InputForm[N[Round[z9x, 10.^(Floor[Log10[Abs[z9x]]] - 2)]]]]]];
Print["[bilinear] base ", z9base, "  operators ", z9ops, "  first-order list ", DIM6$FirstOrder];

z9c6 = {cHW -> 0.7, cHB -> -0.4, cHWB -> 0.3, cHDD -> 0.5, cHl3 -> 0.2, cll1 -> -0.6, cHbox -> 0.45, cH -> 0.35, cHG -> 0.8};
z9rulesAt[z9t_] := (UpdateParameters[Sequence @@ (z9c6 /. (z9a_ -> z9b_) :> (z9a -> z9t z9b))];
  (* the masses of the Z and the Higgs are declared with their particles and are not in
     M$Parameters, so they are named: left symbolic, the canonical mass terms cancel nothing *)
  (# -> NumericalValue[#]) & /@ Select[Join[First /@ M$Parameters, {MZ, MH}], NumericQ[NumericalValue[#]] &]);
z9coef[z9x_] := Which[NumericQ[z9x], Abs[N[z9x]], Head[z9x] === Times, Abs[N[Times @@ Cases[z9x, _?NumericQ, {1}]]], True, 1.];
z9params := Join[First /@ M$Parameters, {MZ, MH}];
z9left[z9e_] := Intersection[Cases[z9e, _Symbol, {0, Infinity}], z9params];
(* the kinetic part (two momenta) and the mass part (none) of a two-point term are measured
   separately: they carry different units, and taken together the mass residue, in GeV^2, hides a
   kinetic residue a thousand times its relative size.  The first version of this test did take
   them together and passed the W, the Z and the photon-Z mixing on the strength of their masses. *)
z9mag[z9e_, z9r_, z9kin_] := Module[{z9y = Expand[z9e /. z9r], z9l},
  z9l = Select[If[Head[z9y] === Plus, List @@ z9y, {z9y}], If[z9kin, ! FreeQ[#, FV | SP] &, FreeQ[#, FV | SP] &]];
  If[z9l === {} || z9y === 0, 0., Max[z9coef /@ z9l]]];

z9L = LSM + L6cl2 + L6cl3 + L6cl4;
z9q = GetQuadraticTerms[z9L];
z9F[z9v_, z9m_, z9n_] := del[z9v[z9n], z9m] - del[z9v[z9m], z9n];
z9can = -1/4 z9F[A, mu, nu] z9F[A, mu, nu] - 1/4 z9F[Z, mu, nu] z9F[Z, mu, nu] + 1/2 MZ^2 Z[mu] Z[mu] -
  1/2 z9F[Wbar, mu, nu] z9F[W, mu, nu] + MW^2 Wbar[mu] W[mu] + 1/2 del[H, mu] del[H, mu] - 1/2 MH^2 H^2 -
  1/4 (del[G[nu, aa], mu] - del[G[mu, aa], nu]) (del[G[nu, aa], mu] - del[G[mu, aa], nu]);
z9bos = {A, Z, W, Wbar, H, G};
(* The spectator carries no momentum.  A two-point term is defined up to a total derivative, and
   multiplying by the spectator spoils that: h Box h and -(d h)^2 are the same kinetic term and
   different three-point vertices unless nothing flows out through the third leg.  O_Hbox is
   written with the box, and before this substitution the test reported its kinetic term as a
   first-order failure of a Lagrangian that was canonical. *)
z9atrest[{z9p_, z9e_}] := Module[{z9g = First[Select[z9p, #[[1]] === G0 &]][[2]], z9o, z9a, z9b},
  z9o = DeleteCases[z9p[[All, 2]], z9g]; {z9a, z9b} = z9o;
  {z9p, Expand[z9e /. {FV[z9g, _] -> 0, SP[z9g, _] -> 0, SP[_, z9g] -> 0} /.
     {FV[z9b, z9m_] :> -FV[z9a, z9m], SP[z9b, z9b] -> SP[z9a, z9a], SP[z9a, z9b] -> -SP[z9a, z9a], SP[z9b, z9a] -> -SP[z9a, z9a]}]}];
z9pick[z9v_] := z9atrest /@ Select[z9v, SubsetQ[z9bos, DeleteCases[#[[1, All, 1]], G0]] &];
z9ref = z9pick[FeynmanRules[G0 z9can, ScreenOutput -> False]];
z9dif = z9pick[FeynmanRules[G0 (z9q - z9can), ScreenOutput -> False]];
Print["[bilinear] two-point structures in the canonical reference: ", Sort[#[[1, All, 1]] & /@ z9ref]];
Print["[bilinear] two-point structures in (Lagrangian - canonical): ", Sort[#[[1, All, 1]] & /@ z9dif]];
(* The Higgs mass parameter of the potential is not an input and no vertex depends on it: it
   multiplies (v + h)^2 and so enters the one- and two-point terms only.  It is whatever puts the
   minimum of the potential at the vev, and the base's relation for the quartic was derived with
   it eliminated that way.  The base file keeps the Standard-Model expression for it, which is
   harmless for the model and wrong for this test, so here it is solved for: the tadpole is
   linear in muH^2.  What is then tested is the statement that matters, that with the vev at the
   minimum the Higgs mass is MH and its kinetic term canonical. *)
z9pot = Expand[z9L /. {(A | Z | W | Wbar)[_] -> 0, G[__] -> 0, _Dot -> 0, del[__] -> 0}];
z9tad = Coefficient[z9pot, H, 1]; z9m2 = -2 Coefficient[z9pot, H, 2];
z9ts = {1, 1/2, 1/4};
z9rs = Function[z9t, Module[{z9r = DeleteCases[z9rulesAt[z9t], muH -> _], z9mu2, z9sol},
    z9sol = z9mu2 /. First[Solve[(z9tad /. muH -> Sqrt[z9mu2] /. z9r) == 0, z9mu2]];
    Print["[potential] t = ", z9t, "  muH^2 at the minimum / (MH^2/2) - 1 = ", z9f[z9sol/(MH^2/2 /. z9r) - 1],
          "   (m_h^2 - MH^2)/MH^2 = ", z9f[((z9m2 /. muH -> Sqrt[z9sol]) - MH^2 /. z9r)/(MH^2 /. z9r)]];
    Append[z9r, muH -> Sqrt[z9sol]]]] /@ z9ts;
Module[{z9l = Union @@ (z9left[Expand[#[[2]] /. z9rs[[1]]]] & /@ z9dif)},
  If[z9l =!= {}, Print["[bilinear] ABORT: parameters with no numerical value: ", z9l]; Quit[1]]];
z9refmag[z9kin_] := Association[(Sort[DeleteCases[#[[1, All, 1]], G0]] -> z9mag[#[[2]], z9rs[[1]], z9kin]) & /@ z9ref];
z9bad = 0;
Do[Module[{z9k = Sort[DeleteCases[z9v[[1, All, 1]], G0]], z9m, z9sc},
   Do[z9m = z9mag[z9v[[2]], #, z9kin] & /@ z9rs;
      z9sc = Lookup[z9refmag[z9kin], Key[z9k], 0.]; If[z9sc == 0., z9sc = If[z9kin, 1., MZ^2 /. z9rs[[1]]]];
      Print["[twopoint] ", z9k, If[z9kin, "  kinetic", "  mass   "], " residue/canonical at t = 1, 1/2, 1/4: ", z9f /@ (z9m/z9sc),
            "   ratios ", If[z9m[[2]] > 0 && z9m[[3]] > 0, z9f /@ {z9m[[1]]/z9m[[2]], z9m[[2]]/z9m[[3]]}, "exact zero"]];
      If[z9m[[3]] > 10^-13 z9sc && z9m[[2]]/z9m[[3]] < 6.5, z9bad++], {z9kin, {True, False}}]], {z9v, z9dif}];
Print["[bilinear] ", If[z9bad == 0, "PASS: every two-point residue falls as t^3", ToString[z9bad] <> " two-point residues fall slower than t^3"]];
Print["[alldone]"];
