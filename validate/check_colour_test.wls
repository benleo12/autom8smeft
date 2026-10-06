(* Regression test for the worker's colour zero test (validate/fr_worker.wls).  History: the
   first version sampled one random value per external colour index for six fixed seeds and
   deleted every bare f^{ABC} / d^{ABC} three-gluon vertex and every f T quark-gluon-gluon
   structure from the cache (2026-09-03); the second enumerated every external assignment
   (exact, but hours on five-leg residuals and untested above a cap); the third (2026-09-04)
   contracts the colour tensors as exact arrays.  This test runs the exact tensor test
   (colourZeroQ) AND the enumeration (colourZeroQEnum) on every case, requires the two to
   agree, requires every nonzero structure to be KEPT and every identity to be DROPPED, and
   times both.  With a cached block given as DIM8_BLOCK=L8opNN (from DIM8_VDIR) it also runs
   both tests on every coupling of that block and on the differences between couplings.
   Run: DIM8_ROOT=<repo> wolframscript -file validate/check_colour_test.wls *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";   (* the same FeynRules install as the worker, not the 2.3.34 fallback of the init file *)
FR$NKernels = 0;   (* serial: no subkernels on a shared laptop *)
Get[$root <> "/tests/fr_env/fr_headless_init.m"];   (* loads FeynRules with the headless fixes, as the worker does *)
SetDirectory[$root <> "/tests/gen_smoke"]; LoadModel["base.fr", "gen.fr"];
z8w = Import[$root <> "/validate/fr_worker.wls", "Text"];
z8a = StringPosition[z8w, "canonEps = "][[1, 1]]; z8b = StringPosition[z8w, "(* ---- term-wise evaluation"][[1, 1]];
ToExpression[StringTake[z8w, {z8a, z8b - 1}]];   (* canonicalisation, both colour tests, canonVerts *)
Print["exact colour tables pass their identities: ", z8colourTablesOK];
g1 = Index[Gluon, Ext[1]]; g2 = Index[Gluon, Ext[2]]; g3 = Index[Gluon, Ext[3]]; g4 = Index[Gluon, Ext[4]]; g5 = Index[Gluon, Ext[5]];
c1 = Index[Colour, Ext[1]]; c2 = Index[Colour, Ext[2]]; c3 = Index[Colour, Ext[3]]; c4 = Index[Colour, Ext[4]];
cc1 = Index[Colour, Colour$1]; cc2 = Index[Colour, Colour$2]; gg1 = Index[Gluon, Gluon$1]; gg2 = Index[Gluon, Gluon$2]; gg3 = Index[Gluon, Gluon$3];
(* dummy names: never reuse a model parameter symbol (gg1 is the electric charge) *)
keep = {"f 3g" -> f[g1, g2, g3], "d 3g" -> dSUN[g1, g2, g3], "T qqg" -> T[g3, c1, c2], "TT qqgg" -> T[g3, c1, cc1] T[g4, cc1, c2],
   "ff 4g" -> f[g1, g2, gg1] f[g3, g4, gg1], "delta gg" -> IndexDelta[g1, g2], "fT qqgg" -> f[g3, g4, gg1] T[gg1, c1, c2],
   "dT qqgg" -> dSUN[g3, g4, gg1] T[gg1, c1, c2], "delta qq" -> IndexDelta[c1, c2],
   "commutator with the wrong factor: TT - TT - 2 i f T" ->
     T[g1, c1, cc1] T[g2, cc1, c2] - T[g2, c1, cc1] T[g1, cc1, c2] - 2 I f[g1, g2, gg1] T[gg1, c1, c2],
   "commutator with the fundamental indices swapped on one side" ->
     T[g1, c1, cc1] T[g2, cc1, c2] - T[g2, c2, cc1] T[g1, cc1, c1] - I f[g1, g2, gg1] T[gg1, c1, c2],
   "f T - f T with fundamental indices swapped" -> f[g1, g2, gg1] T[gg1, c1, c2] - f[g1, g2, gg1] T[gg1, c2, c1],
   "trace Tr(T^a T^a) - 3" -> T[gg1, cc1, cc2] T[gg1, cc2, cc1] - 3,
   "broadcast: T delta + delta delta" -> T[g1, c1, c2] IndexDelta[g2, g3] + IndexDelta[c1, c2] IndexDelta[g2, g3],
   "parameter coefficient: (gs - 2 gg1) f" -> (gs - 2 ee) f[g1, g2, g3],
   "five legs: f f T" -> f[g1, g2, gg1] f[g3, gg1, gg2] T[gg2, c1, c2],
   "colour epsilon" -> Eps[c1, c2, c3]};
drop = {"f contracted with symmetric d: f_{abe} d_{abc} (e, c external)" -> f[gg2, gg3, g1] dSUN[gg2, gg3, g3],
   "Jacobi: f_{abe}f_{cde}+f_{ace}f_{dbe}+f_{ade}f_{bce}" -> f[g1, g2, gg1] f[g3, g4, gg1] + f[g1, g3, gg1] f[g4, g2, gg1] + f[g1, g4, gg1] f[g2, g3, gg1],
   "commutator: TT - TT - i f T" -> T[g1, c1, cc1] T[g2, cc1, c2] - T[g2, c1, cc1] T[g1, cc1, c2] - I f[g1, g2, gg1] T[gg1, c1, c2],
   "anticommutator: TT + TT - delta delta/3 - d T" ->
     T[g1, c1, cc1] T[g2, cc1, c2] + T[g2, c1, cc1] T[g1, cc1, c2] - IndexDelta[g1, g2] IndexDelta[c1, c2]/3 - dSUN[g1, g2, gg1] T[gg1, c1, c2],
   "Fierz: T_{ij} T_{kl} - delta_{il} delta_{kj}/2 + delta_{ij} delta_{kl}/6" ->
     T[gg1, c1, c2] T[gg1, c3, c4] - IndexDelta[c1, c4] IndexDelta[c3, c2]/2 + IndexDelta[c1, c2] IndexDelta[c3, c4]/6,
   "antisymmetry: f T + f(swapped) T" -> f[g1, g2, gg1] T[gg1, c1, c2] + f[g2, g1, gg1] T[gg1, c1, c2],
   "trace Tr(T^a T^a) - 4" -> T[gg1, cc1, cc2] T[gg1, cc2, cc1] - 4,
   "Casimir: (T^a T^a)_{ij} - 4/3 delta_{ij}" -> T[gg1, c1, cc1] T[gg1, cc1, c2] - 4/3 IndexDelta[c1, c2],
   "f f with a common index vs Casimir: f_{acd} f_{bcd} - 3 delta_{ab}" -> f[g1, gg1, gg2] f[g2, gg1, gg2] - 3 IndexDelta[g1, g2],
   "d d contracted: d_{acd} d_{bcd} - 5/3 delta_{ab}" -> dSUN[g1, gg1, gg2] dSUN[g2, gg1, gg2] - 5/3 IndexDelta[g1, g2],
   "five legs, Jacobi times T" -> (f[g1, g2, gg1] f[g3, gg1, gg2] + f[g2, g3, gg1] f[g1, gg1, gg2] + f[g3, g1, gg1] f[g2, gg1, gg2]) T[gg2, c1, c2],
   "colour epsilon identity: eps_{abd} T_{dc} + eps_{bcd} T_{da} + eps_{cad} T_{db}" ->
     Eps[c1, c2, cc1] T[g1, cc1, c3] + Eps[c2, c3, cc1] T[g1, cc1, c1] + Eps[c3, c1, cc1] T[g1, cc1, c2]};
malformed = f[gg2, gg3, gg1] dSUN[gg2, gg3, g3];   (* gg1 occurs once: not a tensor expression; the tensor test must keep it *)
Print["malformed term kept by the tensor test (expected True): ", !colourZeroQ[malformed]];
ok = !colourZeroQ[malformed];
Do[z8ext = Union[Cases[t[[2]], Index[Colour | Gluon, Ext[_]], Infinity]];
   t1 = AbsoluteTime[]; r1 = colourZeroQ[t[[2]]]; t1 = Round[AbsoluteTime[] - t1, 0.01];
   t2 = AbsoluteTime[]; r2 = colourZeroQEnum[t[[2]], z8ext]; t2 = Round[AbsoluteTime[] - t2, 0.01];
   Print[If[!r1 && !r2, "ok  ", "FAIL"], " kept:    ", t[[1]], "   tensor ", r1, " ", t1, " s   enum ", r2, " ", t2, " s"];
   ok = ok && !r1 && !r2, {t, keep}];
Do[z8ext = Union[Cases[t[[2]], Index[Colour | Gluon, Ext[_]], Infinity]];
   t1 = AbsoluteTime[]; r1 = colourZeroQ[t[[2]]]; t1 = Round[AbsoluteTime[] - t1, 0.01];
   t2 = AbsoluteTime[]; r2 = colourZeroQEnum[t[[2]], z8ext]; t2 = Round[AbsoluteTime[] - t2, 0.01];
   Print[If[r1 && r2, "ok  ", "FAIL"], " dropped: ", t[[1]], "   tensor ", r1, " ", t1, " s   enum ", r2, " ", t2, " s"];
   ok = ok && r1 && r2, {t, drop}];
(* real couplings from a cached block: the two tests must agree on every coupling (all kept,
   the cache holds no zero) and on the pairwise differences of couplings with the same
   external colour indices, and the tensor test must not be slower *)
If[Environment["DIM8_BLOCK"] =!= $Failed,
  vdir = If[Environment["DIM8_VDIR"] === $Failed, $root <> "/build/vertices", Environment["DIM8_VDIR"]];
  Get[vdir <> "/" <> Environment["DIM8_BLOCK"] <> ".mx"];
  cs = Select[FR$Vert[[All, 2]], colourQ];
  Print["block ", Environment["DIM8_BLOCK"], ": ", Length[FR$Vert], " vertices, ", Length[cs], " with colour"];
  tT = tE = 0; nAgree = nDis = 0;
  Do[z8ext = Union[Cases[c, Index[Colour | Gluon, Ext[_]], Infinity]];
     t1 = AbsoluteTime[]; r1 = colourZeroQ[c]; tT += AbsoluteTime[] - t1;
     t2 = AbsoluteTime[]; r2 = colourZeroQEnum[c, z8ext]; tE += AbsoluteTime[] - t2;
     If[r1 === r2, nAgree++, nDis++; Print["DISAGREE on a coupling: tensor ", r1, " enum ", r2, " ext ", z8ext]];
     If[r1, Print["WARN: a cached coupling tests zero (stale cache?): ", z8ext]], {c, cs}];
  Print["couplings: agree ", nAgree, " disagree ", nDis, "  tensor ", Round[tT, 0.1], " s  enum ", Round[tE, 0.1], " s"];
  ok = ok && nDis == 0;
  (* differences of couplings sharing the external colour pattern: c1 - c2 and c1 - c1' with
     two external gluon labels exchanged; zero or not, the verdicts must agree *)
  grp = GatherBy[cs, Union[Cases[#, Index[Colour | Gluon, Ext[_]], Infinity]] &];
  nAgree = nDis = 0; tT = tE = 0;
  Do[If[Length[g] < 2, Continue[]];
     Do[d = canonCoup[g[[1]] - g[[i]]]; If[d === 0, Continue[]];
        z8ext = Union[Cases[d, Index[Colour | Gluon, Ext[_]], Infinity]];
        t1 = AbsoluteTime[]; r1 = colourZeroQ[d]; tT += AbsoluteTime[] - t1;
        t2 = AbsoluteTime[]; r2 = colourZeroQEnum[d, z8ext]; tE += AbsoluteTime[] - t2;
        If[r1 === r2, nAgree++, nDis++; Print["DISAGREE on a difference: tensor ", r1, " enum ", r2, " ext ", z8ext]],
        {i, 2, Min[Length[g], 4]}], {g, grp}];
  Print["differences: agree ", nAgree, " disagree ", nDis, "  tensor ", Round[tT, 0.1], " s  enum ", Round[tE, 0.1], " s"];
  ok = ok && nDis == 0];
Print[If[ok, "COLOUR TEST PASS", "COLOUR TEST FAIL"]]; If[!ok, Quit[1]];
