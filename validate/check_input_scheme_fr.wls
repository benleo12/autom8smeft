(* Input-scheme acceptance test v6.
   (1) WC = 0: the variant must equal base.fr numerically and its LSM vertex CONTENTS must be
       base.fr's 31 plus, at most, entries whose couplings are numerically zero.
   (2) dim-6 = 0, dim-8 on, Lam = 3 TeV: in the MERGED Lagrangian LSM + the class-3 and class-6
       blocks that carry the input-scheme coefficients, the spurious photon couplings
       {A,A,H}, {A,H,Z}, {A,nu,nubar} must be O((v^4/Lam^4)^2) ~ 1e-9 relative, while a genuine
       dim-8 shift (the h W W coupling) is O(v^4/Lam^4) ~ 4.5e-5, and the photon-fermion
       ratio A l lbar / A uq uqbar stays -3/2.  Testing LSM alone is wrong: the rotation
       cancels against terms that live in the OPERATOR blocks, not in LSM.
   (3) step 5: the top two-point term of LYukawa + Q_{quH^5} stays at ymt with c8quH5 = 1. *)
$root = Environment["DIM8_ROOT"];
FR$NKernels = 0; FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];
z9base = $ScriptCommandLine[[2]];
LoadModel[z9base, "gen.fr"];
z9np[z9p_] := ToString[NumberForm[N[NumericalValue[z9p]], 10]];
z9content[z9v_] := Sort[DeleteDuplicates[ToString /@ (Sort /@ (z9v[[All, 1, All, 1]]))]];
z9find[z9v_, z9f_List] := Select[z9v, Sort[#[[1, All, 1]]] === Sort[z9f] &];
z9rules := (# -> NumericalValue[#]) & /@ Select[First /@ M$Parameters, NumericQ[NumericalValue[#]] &];
(* magnitude of a coupling: after substituting numbers for parameters, each additive term is
   (numeric factors) x (Lorentz/spin/colour structure).  Take the numeric FACTORS at level one
   only, so indices buried inside Index[..., Ext[3]] can never leak in; a term with no numeric
   factor has coefficient 1. *)
z9coef[z9t_] := Which[NumericQ[z9t], Abs[N[z9t]],
  Head[z9t] === Times, Abs[N[Times @@ Cases[z9t, _?NumericQ, {1}]]],
  True, 1.];
z9mag[z9v_, z9f_List] := Module[{z9s = z9find[z9v, z9f], z9e},
  If[z9s === {}, Return["absent"]];
  z9e = Expand[z9s[[1, 2]] /. z9rules];
  z9e = If[Head[z9e] === Plus, List @@ z9e, {z9e}];
  ToString[Max[z9coef /@ z9e], InputForm]];
z9sf[z9x_] := ToString[N[NumericalValue[z9x]], InputForm];
Print["[check] ", z9base, " params: gw=", z9np[gw], " g1=", z9np[g1], " vev=", z9np[vev], " MW=", z9np[MW], " lam=", z9np[lam]];
z9v = FeynmanRules[LSM, ScreenOutput -> False];
Print["[check] ", z9base, " LSM vertices ", Length[z9v]];
Print["[content] ", z9base, " ", StringRiffle[z9content[z9v], " ; "]];
If[StringContainsQ[z9base, "inputscheme"],
  Print["[zero] at WC=0, max |coupling| of {A,A,H} ", z9mag[z9v, {A, A, H}], "  {A,H,Z} ", z9mag[z9v, {A, H, Z}], "  {A,vl,vlbar} ", z9mag[z9v, {A, vl, vlbar}], "   (must be 0 or absent)"];
  UpdateParameters[c8W2H4x1 -> 0.5, c8W2H4x3 -> -0.3, c8B2H4x1 -> 0.4, c8WBH4x1 -> 0.6, c8H6x1 -> 0.8, c8H6x2 -> -0.2, Lam -> 3000];
  Print["[check] dim-8 on, Lam=3 TeV: gw2=", z9sf[gw2], " vev2=", z9sf[vev2], " TZA2=", z9sf[TZA2], " TAA2=", z9sf[TAA2], " MW=", z9sf[MW]];
  z9ops = FeynmanRules[L8op469 + L8op470 + L8op595 + L8op597 + L8op599 + L8op601, ScreenOutput -> False];
  z9all = MergeVertices[FeynmanRules[LSM, ScreenOutput -> False], z9ops];
  Print["[merged] vertices ", Length[z9all]];
  Print["[spurious] merged |coupling|: {A,A,H} ", z9mag[z9all, {A, A, H}], "  {A,H,Z} ", z9mag[z9all, {A, H, Z}], "  {A,vl,vlbar} ", z9mag[z9all, {A, vl, vlbar}], "   (expect ~1e-9 x scale, i.e. O((v^4/Lam^4)^2))"];
  Print["[physical] merged |coupling|: {H,W,Wbar} ", z9mag[z9all, {H, W, Wbar}], "  SM value ", z9mag[z9v, {H, W, Wbar}], "   (dim-8 shift expected at relative O(v^4/Lam^4) ~ 4.5e-5)"];
  z9e = z9find[z9all, {A, l, lbar}]; z9u = z9find[z9all, {A, uq, uqbar}];
  If[z9e =!= {} && z9u =!= {}, Print["[ward] merged ratio (A l lbar)/(A uq uqbar) = ", ToString[Simplify[(z9e[[1, 2]] /. z9rules)/(z9u[[1, 2]] /. z9rules)], InputForm], "   (must be -3/2 x deltas)"]];
  (* step 5: c8quH5 is COMPLEX, split into c8quH5Re/Im externals, so set the Re part.
     CheckMassSpectrum only flags disagreements above 0.1 percent and the shift at c8 = 1,
     Lam = 1 TeV is v^4/(4 Lam^4) = 0.092 percent, so use c8 = 5 (0.46 percent): an
     uncorrected Yukawa would be flagged, the corrected one must not.  FeynmanRules drops
     two-point terms, so GetMassSpectrum supplies the numbers. *)
  UpdateParameters[c8W2H4x1 -> 0, c8W2H4x3 -> 0, c8B2H4x1 -> 0, c8WBH4x1 -> 0, c8H6x1 -> 0, c8H6x2 -> 0, c8quH5Re -> 5, Lam -> 1000];
  (* since 2026-10-03 the Yukawa parameter keeps its Standard-Model value and the compensation of
     Q_{quH^5} is written out in LYukawa, so the two numbers printed here must now be EQUAL; what
     tests the compensation is the mass spectrum below *)
  Print["[mass] c8quH5Re=5, Lam=1 TeV: yt=", z9sf[yu[3, 3]], " vs SM Sqrt2 ymt/vev=", z9sf[Sqrt[2] ymt/vev], "   (equal: the compensation, ", z9sf[5 vevSM^4/4/Lam^4], ", is a separate term of LYukawa)"];
  Print["[mass] GetMassSpectrum[LYukawa + Q_{quH^5}]: ", ToString[InputForm[GetMassSpectrum[LYukawa + L8op28]]]];
  Print["[mass] CheckMassSpectrum (must report no disagreement despite c8quH5 = 5):"];
  CheckMassSpectrum[LYukawa + L8op28]];
Print["[alldone]"];
