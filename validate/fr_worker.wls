(* validate/fr_worker.wls  --  compute and cache one Lagrangian block at a time.

   The expensive parts of a dimension-eight build are per block and independent: the
   ExpandIndices evaluation and the FeynmanRules call.  This worker does both for its
   share of the blocks, caches the vertex list to disk, and runs CheckHermiticity on the
   way past, so one pass produces both the V5 result and the input to WriteUFO.

   Usage:
     wolframscript -file fr_worker.wls <shard> <nshards> [nblocks] [nkernels] [recursionlimit]
     wolframscript -file fr_worker.wls 43,49,54 0 [nblocks] [nkernels]      (explicit blocks)

   Caching and resumption: a block whose .mx already exists is skipped, so the sweep can
   be killed and restarted, re-sharded across a different number of processes, or extended
   after the catalogue changes, without recomputing anything.  Delete the .mx to force a
   rebuild.

   Outputs, per block:
     build/vertices/<block>.mx        DumpSave of  FR$Vert  (the vertex list)
     build/vertices/<block>.status    one line: block | ops | terms | vertices |
                                      nonhermitian | tEval | tVert | tHerm
*)

(* DIM8_ROOT lets the same script run off-machine, e.g. on an HPC system *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
args = Rest[$ScriptCommandLine];
(* a non-numeric first argument is a block NAME; ToExpression would evaluate it to the
   block's own Lagrangian and the [alldone] line would print the whole thing *)
shard = If[StringContainsQ[args[[1]], ","] || ! StringMatchQ[args[[1]], NumberString], 0, ToExpression[args[[1]]]];
nshards = ToExpression[args[[2]]];
nblocks = If[Length[args] >= 3, ToExpression[args[[3]]], 674];
FR$NKernels = If[Length[args] >= 4, ToExpression[args[[4]]], 3];
z8rlWanted = If[Length[args] >= 5, ToExpression[args[[5]]], 2500];  (* applied AFTER FeynRules loads: FeynRulesPackage.m:1622 resets $RecursionLimit to 2500 *)
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
z9termwise = Environment["DIM8_TERMWISE"] =!= "0";
(* The Hermiticity check costs about three quarters of a block: on L8op94 it was 22266 s
   against 5792 s for the vertices themselves.  It is a validation (V5), not something the
   UFO writer needs, so it can be deferred to get a complete vertex cache sooner.  OPT IN
   with DIM8_HERM=0; the default remains the full check.  A block built that way records
   "nonhermitian -1", meaning NOT CHECKED rather than clean, and DIM8_HERMONLY=1 later
   re-runs just the check over blocks whose .mx already exists. *)
z9herm = Environment["DIM8_HERM"] =!= "0";
z9hermOnly = Environment["DIM8_HERMONLY"] === "1";   (* term-wise chunked evaluation, see below *)
z9chunk = If[Environment["DIM8_CHUNK"] === $Failed, 250, ToExpression[Environment["DIM8_CHUNK"]]];
(* DIM8_SPLIT=1: the chunk unit is a single expanded term instead of a whole monomial.  A monomial
   of a dual-dual G^4 operator is 24 metric products after the Eps-pair rewrite, and one such
   monomial with seven or eight gluon fields drove FeynmanRules past 122 GB (2026-09-05); with the
   split, DIM8_CHUNK=1 feeds FeynmanRules one term at a time.  Linear in the Lagrangian, so exact. *)
z9split = Environment["DIM8_SPLIT"] === "1";
(* DIM8_MAXLEGS=n: FeynRules' own MaxParticles option, vertices with more than n legs are not
   computed.  Opt-in fallback for the class-1 operators whose seven- and eight-gluon vertices
   exceed the memory of a node; an n-point vertex only enters tree amplitudes with at least n
   external legs, so a cap at 6 leaves every amplitude with up to six legs exact.  Recorded in
   the status line as "maxlegs n"; the whole-block CheckHermiticity path ignores it. *)
(* DIM8_EPSEPS (default on, 0 to disable): replace the product of two Lorentz Levi-Civita tensors in a monomial by the
   4D identity Eps[a,b,c,d] Eps[e,f,g,h] = -Det[ME[i,j]] (24 metric products; the sign of
   eps_{0123} squares away, so the identity holds in either convention).  The dual-dual
   operators Q_{G^4}^{(2),(4),(8)} drove a single-term FeynmanRules call past 80 GB with the
   two Eps contracted through eight gluon indices, while the non-dual G^4 operators with the
   same eight-gluon vertices build in under two hours below 60 GB; FeynRules' handling of the
   contracted Eps pair is the cost, not the legs.  Exact; validated on Q_{G^2B^2}^{(2)} against
   its Eps-carrying build (2026-09-04). *)
z9epseps = Environment["DIM8_EPSEPS"] =!= "0";   (* default ON since 2026-09-04; DIM8_EPSEPS=0 keeps the Eps pair *)
z9maxlegs = If[Environment["DIM8_MAXLEGS"] === $Failed, None, ToExpression[Environment["DIM8_MAXLEGS"]]];
(* DIM8_MINLEGS=n: FeynRules' MinParticles, only vertices with at least n legs; together with a
   capped build of the same block it splits an eight-gluon operator into a cheap part (up to six
   legs) and an expensive, checkpointed part (seven and eight legs), merged afterwards *)
z9minlegs = If[Environment["DIM8_MINLEGS"] === $Failed, None, ToExpression[Environment["DIM8_MINLEGS"]]];
(* DIM8_CHECKPOINT=1: after every chunk the accumulated vertices are saved to <vdir>/<block>.partial.mx
   and a restart resumes from there (the chunk list is fingerprinted), so a block that needs more
   than one 24 h job still completes *)
z9checkpoint = Environment["DIM8_CHECKPOINT"] === "1";
(* the option list is built after FeynRules is loaded (below), else MaxParticles is a Global` symbol *)

Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];

(* environment overrides for variant builds (e.g. a Feynman-gauge subset for MadGraph's
   check gauge):  DIM8_BASE = base model file in tests/gen_smoke (default base.fr),
   DIM8_VDIR = cache directory (default build/vertices) *)
z8base = If[Environment["DIM8_BASE"] === $Failed, "base.fr", Environment["DIM8_BASE"]];
vdir = If[Environment["DIM8_VDIR"] === $Failed, $root <> "/build/vertices", Environment["DIM8_VDIR"]];
If[! DirectoryQ[$root <> "/build"], CreateDirectory[$root <> "/build"]];
If[! DirectoryQ[vdir], CreateDirectory[vdir]];

t0 = AbsoluteTime[];
(* DIM8_BASE may name several files separated by ";", as the writer already allows, so that a
   base assembled from more than one model file loads here too.  That is how the dimension-six
   sector arrives: "base_inputscheme.fr;dim6_smeftsim.fr". *)
z8bases = StringTrim /@ StringSplit[z8base, ";"];
LoadModel[Sequence @@ Append[z8bases, "gen.fr"]];
(* the subkernels keep Mathematica's default $RecursionLimit = 2500 unless told otherwise;
   CheckHermiticity on a 334-vertex Feynman-gauge class-11 block died there *)
Unprotect[$RecursionLimit]; $RecursionLimit = z8rlWanted;
If[FR$NKernels > 0, With[{z8rl = z8rlWanted}, ParallelEvaluate[Unprotect[$RecursionLimit]; $RecursionLimit = z8rl]]];
Print["[cfg] RecursionLimit master ", $RecursionLimit, If[FR$NKernels > 0, {" subkernels ", ParallelEvaluate[$RecursionLimit]}, ""]];
Print["[cfg] base ", z8base, "  cache ", vdir, "  FeynmanGauge ", FeynmanGauge, "  termwise ", z9termwise, "  chunk ", z9chunk, "  hermiticity ", If[z9herm, "on", "DEFERRED"]];
Print["[time] LoadModel: ", Round[AbsoluteTime[] - t0, 0.1], " s;  parameters: ", Length[M$Parameters]];
z9mkFrOpts[] := Join[If[z9maxlegs === None, {}, {Symbol["FeynRules`MaxParticles"] -> z9maxlegs}],
                     If[z9minlegs === None, {}, {Symbol["FeynRules`MinParticles"] -> z9minlegs}]];
z9frOpts = z9mkFrOpts[];
(* A Lagrangian term with n field operators feeds exactly the n-point vertex, so with a leg range
   set the terms outside it are dropped BEFORE FeynmanRules: FeynRules would otherwise expand
   the eight-gluon term of a G^4 operator (the memory hog) only to discard its vertex under
   MaxParticles (the capped build of 432 died at 122 GB that way, 2026-09-05), and the
   MinParticles run would spend its time on the seventy chunks that hold nothing above six legs. *)
z9nfields[z9t_] := Module[{z9x = z9t /. Power[z9b_, z9n_Integer] /; !FreeQ[z9b, _Symbol?FieldQ] :> z9FPOW[z9n, Count[z9b, (_Symbol?FieldQ)[___], {0, Infinity}] + Count[z9b, _Symbol?FieldQ, {0, Infinity}]]},
  Total[Cases[z9x, z9FPOW[z9n_, z9k_] :> z9n z9k, {0, Infinity}]] + Count[z9x, (_Symbol?FieldQ)[___], {0, Infinity}] + Count[z9x, _Symbol?FieldQ, {0, Infinity}]];
z9legOK[z9t_] := With[{z9k = z9nfields[z9t]}, (z9maxlegs === None || z9k <= z9maxlegs) && (z9minlegs === None || z9k >= z9minlegs)];
z9legFilter[z9e_] := Module[{z9terms = If[Head[Expand[z9e]] === Plus, List @@ Expand[z9e], {Expand[z9e]}], z9keep},
  z9keep = Select[z9terms, z9legOK]; z9dropped += Length[z9terms] - Length[z9keep]; Total[z9keep]];
(* defined AFTER LoadModel so that Eps and ME are the FeynRules` symbols, not Global` ones *)
z9epsepsRule = Eps[z9a_, z9b_, z9c_, z9d_] Eps[z9e_, z9f_, z9g_, z9h_] :> -Det[Outer[ME, {z9a, z9b, z9c, z9d}, {z9e, z9f, z9g, z9h}]];

(* FeynRules never canonicalises the couplings it returns.  Two things it leaves undone
   produce vertices that are identically zero but not syntactically so, and CheckHermiticity
   then reports a difference of two zeros:
     - Eps (and the SU(3) f) are never antisymmetrised over their arguments, so a CP-odd
       vertex can come out as  c (Eps p1 p2 p3 - Eps p1 p3 p2)   (class 8, Q_{WH^4D^2}^{(2)});
     - summed (dummy) indices Gluon$1, Gluon$2, ... are never relabelled, so
       f[3,4,G2] f[5,6,G1] f[G1,G2,G3] + f[3,4,G1] f[5,6,G2] f[G1,G2,G3]  survives
       (class 14, Q_{q^2G^2D}^{(2)}: 12 "non-Hermitian" vertices, all zero).
   Canonicalise every coupling (sorted Eps/f arguments with the signature, then average over
   all relabellings of the dummy indices, type by type) and drop the vanishing ones. *)
canonEps = Eps[z8args__] :> Signature[{z8args}] Eps[Sequence @@ Sort[{z8args}]];
canonF = f[z8args__] :> Signature[{z8args}] f[Sequence @@ Sort[{z8args}]];
dummies[z8e_] := Union[Cases[z8e, Index[_, _Symbol], Infinity]];
(* Averaging over all relabellings is exact but factorial in the number of dummies of one
   type; the class-14 W blocks (up to ten Lorentz dummies per coupling) never finished.
   Instead each monomial is brought to a canonical relabelling: the factors are ordered by a
   dummy-blind key, the dummies are renamed in order of first appearance, and among factors
   whose keys tie every ordering is tried and the Order-minimal result kept.  Two monomials
   equal up to dummy names then coincide exactly, which is all Expand needs to cancel them. *)
dummyQ[z8s_Symbol] := True;   (* any symbol label is a dummy: externals are Ext[k]; OptimizeIndex names dummies \[Alpha]1 without a dollar *)
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
(* T = lambda/2, f^{abc} = -2 i Tr([T^a,T^b] T^c), d^{abc} = 2 Tr({T^a,T^b} T^c): with the
   Gell-Mann matrices that is Tr(...)/8.  Until 2026-09-04 the tables carried Tr(...)/4, i.e.
   f and d twice too large relative to T and delta; a zero test cannot drop a real vertex that
   way (an f f tensor is never proportional to a delta delta tensor) but it keeps every zero
   that rests on [T^a,T^b] = i f^{abc} T^c or the Fierz identity, and flags it non-Hermitian. *)
fNum = Table[-2 I Tr[(gellMann[[z8a]].gellMann[[z8b]] - gellMann[[z8b]].gellMann[[z8a]]).gellMann[[z8c]]]/8, {z8a, 8}, {z8b, 8}, {z8c, 8}] // Simplify;
dNum = Table[2 Tr[(gellMann[[z8a]].gellMann[[z8b]] + gellMann[[z8b]].gellMann[[z8a]]).gellMann[[z8c]]]/8, {z8a, 8}, {z8b, 8}, {z8c, 8}] // Simplify;
colourQ[z8e_] := !FreeQ[z8e, Index[Colour | Gluon, _]];
(* The first version of this test put ONE random value on each external colour index for six
   fixed seeds and dropped the coupling when all six evaluations vanished.  That is unsound
   for sparse tensors: a random triple of adjoint indices is a nonzero component of f or d
   about one time in ten, so all six samples missed with probability near one half, and with
   fixed seeds the miss was the same for every vertex with the same external index pattern.
   It deleted every bare f^{ABC} and d^{ABC} three-gluon vertex and every f T quark-gluon-gluon
   structure from the cache (found 2026-09-03 on Q_{G^3B}^{(3)}, which came out with no
   vertices at all).  A tensor is zero iff every component is zero, so enumerate ALL
   assignments of the external colour indices, stop at the first nonzero one, and do not test
   at all (keep the vertex) when there are more than z8maxCombos assignments; a coupling
   that is kept although zero costs nothing but a vertex in the UFO.  Simplify failing to
   reach 0 also keeps the vertex, so the test can only err on the safe side. *)
(* cap on the exhaustive enumeration: 40000 covers q qbar g g g (4608), q qbar g g g g (36864)
   and five gluons (32768); six gluons (262144) are not tested and kept.  With 4096 the finish
   job flagged the q^2G^2D family (L8op43, 54) on five-leg vertices whose zero the enumeration
   never reached (2026-09-04). *)
z8maxCombos = If[Environment["DIM8_MAXCOMBOS"] === $Failed, 40000, ToExpression[Environment["DIM8_MAXCOMBOS"]]];
(* dummies are summed TERM BY TERM: summing over the whole expression multiplies every term
   that lacks the dummy by 3 or 8, which can only mask a genuine zero (safe direction) but is
   not exact (2026-09-04) *)
colourSumTerm[z8t_] := Module[{z8e = z8t, z8dums = Union[Cases[z8t, Index[Colour | Gluon, _Symbol], Infinity]]},
  Do[z8e = Total[Table[z8e /. z8d -> z8v, {z8v, If[z8d[[1]] === Colour, 3, 8]}]], {z8d, z8dums}]; z8e];
colourAt[z8c_, z8ext_List, z8vals_List] := Module[{z8e = Expand[z8c /. Thread[z8ext -> z8vals]]},
  z8e = Total[colourSumTerm /@ If[Head[z8e] === Plus, List @@ z8e, {z8e}]];
  z8e = z8e /. {T[z8a_Integer, z8i_Integer, z8j_Integer] :> tNum[z8a, z8i, z8j],
            f[z8a_Integer, z8b_Integer, z8k_Integer] :> fNum[[z8a, z8b, z8k]],
            dSUN[z8a_Integer, z8b_Integer, z8k_Integer] :> dNum[[z8a, z8b, z8k]],
            Eps[z8i_Integer, z8j_Integer, z8k_Integer] :> Signature[{z8i, z8j, z8k}],
            IndexDelta[z8i_Integer, z8j_Integer] :> KroneckerDelta[z8i, z8j]};
  (* Expand, not Simplify: couplings arrive canonicalised (canonCoup), so like Lorentz monomials
     cancel exactly under Expand, and a nonzero remainder only KEEPS the vertex; Simplify with a
     time budget cost hours on the 4608-assignment enumeration of a fermionic zero (2026-09-04) *)
  Expand[z8e]];
(* Split the coupling ONCE into Lorentz/spin monomials and their colour polynomials: a term's
   key is the product of its factors carrying non-colour indices or momenta (FV, SP, ME, Eps,
   Ga, ...), its coefficient everything else (numbers, parameters, colour tensors).  Distinct
   keys are linearly independent syntactic objects, so the coupling vanishes for a colour
   assignment iff every coefficient does; enumerating the small colour polynomials is exact and
   hundreds of times cheaper than expanding the full expression per assignment (the block-43
   Hermiticity rerun took hours that way, 2026-09-04). *)
colourFactorQ[z8f_] := !FreeQ[z8f, Index[Colour | Gluon, _]];
lorentzFactorQ[z8f_] := !FreeQ[z8f, Index[Except[Colour | Gluon], _] | _FV | _SP | _ME | _Eps | _Ga | _ProjM | _ProjP | _SlashedP | _TensDot | _z9e | _z9p];   (* z9e, z9p: the Lorentz-level residual test below *)
colourSplit[z8c_] := Module[{z8e = Expand[z8c], z8terms},
  z8terms = If[Head[z8e] === Plus, List @@ z8e, {z8e}];
  Values[GroupBy[z8terms,
    Function[z8t, Times @@ Select[If[Head[z8t] === Times, List @@ z8t, {z8t}], lorentzFactorQ[#] && !colourFactorQ[#] &]] ->
    Function[z8t, Times @@ Select[If[Head[z8t] === Times, List @@ z8t, {z8t}], !(lorentzFactorQ[#] && !colourFactorQ[#]) &]], Total]]];
(* ---- exact colour tensor evaluation (2026-09-04) --------------------------------------
   The enumeration above is exact, but its cost is the number of external assignments times
   the number of colour polynomials, and anything above z8maxCombos is not tested at all,
   which in a Hermiticity residual means a flag: the finish job flagged the whole
   psi^2 X^2 D family on residual vertices with five and six legs, and the block-43 rerun
   with the cap lifted enumerated for hours.  So the colour polynomial is evaluated as a
   TENSOR instead: every factor (T, f, d, delta, the colour epsilon) is an explicit array,
   the dummies are contracted factor by factor (the shared axes reshaped into one and
   contracted with Dot, an einsum), and the polynomial vanishes iff the resulting array over
   the external indices does.  Every component is computed, nothing is sampled, and there is
   no cap.  Exact arithmetic: the entries lie in Q(i)(Sqrt[3]) and every array is kept as a
   pair {A, B} meaning A + Sqrt[3] B with Gaussian-rational A and B (B is the marker Z8Z
   when it vanishes identically), so no symbolic Sqrt[3] ever enters Dot or TensorProduct.
   The f and d tables are generated from the generator matrices in the same arithmetic and
   asserted against the defining identities and against fNum/dNum at load time.
   DIM8_COLOURTEST=enum restores the enumeration (validate/check_colour_test.wls runs both
   and requires identical verdicts). *)
z8colourEnum = Environment["DIM8_COLOURTEST"] === "enum";
z8dim[Colour] = 3; z8dim[Gluon] = 8;
Z8Z = Z8ZeroPart;
z8zeroM = ConstantArray[0, {3, 3}];
z8TA = Append[Most[gellMann], z8zeroM]/2;                                   (* lambda^1..7 are Gaussian rational *)
z8TB = Append[ConstantArray[z8zeroM, 7], {{1, 0, 0}, {0, 1, 0}, {0, 0, -2}}/3]/2;  (* lambda^8 = Sqrt[3] diag(1,1,-2)/3 *)
z8pm[{z8a1_, z8b1_}, {z8a2_, z8b2_}] := {z8a1.z8a2 + 3 z8b1.z8b2, z8a1.z8b2 + z8b1.z8a2};   (* (A1+s B1)(A2+s B2), s^2 = 3 *)
z8pT[z8a_] := {z8TA[[z8a]], z8TB[[z8a]]};
z8pTr[{z8a_, z8b_}] := {Tr[z8a], Tr[z8b]};
z8fAB = Table[-2 I z8pTr[z8pm[z8pm[z8pT[z8a], z8pT[z8b]] - z8pm[z8pT[z8b], z8pT[z8a]], z8pT[z8c]]], {z8a, 8}, {z8b, 8}, {z8c, 8}];
z8dAB = Table[2 z8pTr[z8pm[z8pm[z8pT[z8a], z8pT[z8b]] + z8pm[z8pT[z8b], z8pT[z8a]], z8pT[z8c]]], {z8a, 8}, {z8b, 8}, {z8c, 8}];
z8fA = z8fAB[[All, All, All, 1]]; z8fB = z8fAB[[All, All, All, 2]];
z8dA = z8dAB[[All, All, All, 1]]; z8dB = z8dAB[[All, All, All, 2]];
(* load-time assertions: values, the defining identities in the pair arithmetic, and agreement
   with the symbolic tables used by the enumeration *)
z8pScaleM[{z8fa_, z8fb_}, {z8ma_, z8mb_}] := {z8fa z8ma + 3 z8fb z8mb, z8fa z8mb + z8fb z8ma};
z8colourTablesOK = And[
  z8fA[[1, 2, 3]] == 1 && z8fB[[1, 2, 3]] == 0, z8fA[[1, 4, 7]] == 1/2, z8fA[[4, 5, 8]] == 0 && z8fB[[4, 5, 8]] == 1/2,
  z8dA[[1, 1, 8]] == 0 && z8dB[[1, 1, 8]] == 1/3, z8dA[[1, 4, 6]] == 1/2,
  AllTrue[Flatten[Table[z8pm[z8pT[z8a], z8pT[z8b]] - z8pm[z8pT[z8b], z8pT[z8a]]
      - I Sum[z8pScaleM[{z8fA[[z8a, z8b, z8c]], z8fB[[z8a, z8b, z8c]]}, z8pT[z8c]], {z8c, 8}], {z8a, 8}, {z8b, 8}]], # === 0 &],
  AllTrue[Flatten[Table[z8pm[z8pT[z8a], z8pT[z8b]] + z8pm[z8pT[z8b], z8pT[z8a]] - {KroneckerDelta[z8a, z8b] IdentityMatrix[3]/3, z8zeroM}
      - Sum[z8pScaleM[{z8dA[[z8a, z8b, z8c]], z8dB[[z8a, z8b, z8c]]}, z8pT[z8c]], {z8c, 8}], {z8a, 8}, {z8b, 8}]], # === 0 &],
  AllTrue[Flatten[Simplify[z8fA + Sqrt[3] z8fB - fNum]], # === 0 &], AllTrue[Flatten[Simplify[z8dA + Sqrt[3] z8dB - dNum]], # === 0 &],
  AllTrue[Flatten[Simplify[z8TA + Sqrt[3] z8TB - Table[tNum[z8a, z8i, z8j], {z8a, 8}, {z8i, 3}, {z8j, 3}]]], # === 0 &]];
If[!z8colourTablesOK, Print["[colour] FATAL: the exact colour tables fail their identities"]; Quit[3]];
z8pmap[z8fn_, {z8a_, z8b_}] := {z8fn[z8a], If[z8b === Z8Z, Z8Z, z8fn[z8b]]};
z8ptp[{z8a1_, z8b1_}, {z8a2_, z8b2_}] := {TensorProduct[z8a1, z8a2] + If[z8b1 === Z8Z || z8b2 === Z8Z, 0, 3 TensorProduct[z8b1, z8b2]],
  Which[z8b1 === Z8Z && z8b2 === Z8Z, Z8Z, z8b1 === Z8Z, TensorProduct[z8a1, z8b2], z8b2 === Z8Z, TensorProduct[z8b1, z8a2],
        True, TensorProduct[z8a1, z8b2] + TensorProduct[z8b1, z8a2]]};
z8pdot[{z8a1_, z8b1_}, {z8a2_, z8b2_}] := {z8a1.z8a2 + If[z8b1 === Z8Z || z8b2 === Z8Z, 0, 3 z8b1.z8b2],
  Which[z8b1 === Z8Z && z8b2 === Z8Z, Z8Z, z8b1 === Z8Z, z8a1.z8b2, z8b2 === Z8Z, z8b1.z8a2, True, z8a1.z8b2 + z8b1.z8a2]};
z8facArr[T[z8a_, z8i_, z8j_]] := {{z8TA, z8TB}, {z8a, z8i, z8j}};
z8facArr[f[z8a_, z8b_, z8c_]] := {{z8fA, z8fB}, {z8a, z8b, z8c}};
z8facArr[dSUN[z8a_, z8b_, z8c_]] := {{z8dA, z8dB}, {z8a, z8b, z8c}};
z8facArr[Eps[z8i_, z8j_, z8k_]] := {{LeviCivitaTensor[3, List], Z8Z}, {z8i, z8j, z8k}};
z8facArr[IndexDelta[z8i_, z8j_]] := {{IdentityMatrix[z8dim[z8i[[1]]]], Z8Z}, {z8i, z8j}};
z8facArr[_] := $Failed;
(* a dummy repeated inside one factor (a trace) is contracted there; three or more copies of a
   label in one factor make no sense and fail the term (the vertex is then kept) *)
z8self[{z8arr_, z8l_}] := Module[{z8cur = z8arr, z8labs = z8l, z8d, z8p},
  If[AnyTrue[Tally[z8labs], #[[2]] > 2 &], Return[$Failed]];
  While[(z8d = Select[Tally[z8labs], #[[2]] == 2 &]) =!= {},
    z8p = Flatten[Position[z8labs, z8d[[1, 1]], {1}, Heads -> False]];
    z8cur = z8pmap[TensorContract[#, {z8p}] &, z8cur]; z8labs = Delete[z8labs, List /@ z8p]];
  {z8cur, z8labs}];
z8maxArray = If[Environment["DIM8_MAXARRAY"] === $Failed, 4000000, ToExpression[Environment["DIM8_MAXARRAY"]]];
z8labDims[z8labs_] := z8dim[#[[1]]] & /@ z8labs;
(* one term: coefficient (everything without a colour index) times the contracted array over
   the external indices, in the order z8ext; externals the term does not carry are constant
   axes.  Returns {coef, {A, B}}, $Failed (unsupported head, malformed index pattern) or
   $TooLarge (an intermediate array above DIM8_MAXARRAY entries); both keep the vertex. *)
(* the array of a colour product is memoised: the same structures recur across the Lorentz
   monomials of one coupling and across the assignments of the Lorentz-level residual test *)
z8termArr[z8t_, z8ext_] := Module[{z8facs, z8coef, z8colprod, z8r},
  z8facs = If[Head[z8t] === Times, List @@ z8t, {z8t}];
  z8coef = Times @@ Select[z8facs, !colourFactorQ[#] &]; z8colprod = Times @@ Select[z8facs, colourFactorQ];
  z8r = z8colArrMemo[z8colprod, z8ext];
  If[z8r === $Failed || z8r === $TooLarge, z8r, {z8coef, z8r}]];
z8colArrMemo[z8cp_, z8ext_] := z8colArrMemo[z8cp, z8ext] = z8colArrRaw[z8cp, z8ext];
z8colArrRaw[z8t_, z8ext_] := Module[{z8facs, z8tens, z8cur, z8labs, z8rest, z8k, z8f, z8fl, z8shared, z8freeC, z8freeF,
    z8ordC, z8ordF, z8dC, z8dF, z8sd, z8m1, z8m2, z8prod, z8miss},
  z8facs = If[Head[z8t] === Times, List @@ z8t, {z8t}];
  z8facs = Flatten[z8facs /. Power[z8b_?colourFactorQ, z8n_Integer?Positive] :> ConstantArray[z8b, z8n], 1];
  z8tens = z8facArr /@ Select[z8facs, colourFactorQ];
  If[MemberQ[z8tens, $Failed], Return[$Failed]];
  z8tens = z8self /@ z8tens; If[MemberQ[z8tens, $Failed], Return[$Failed]];
  (* a term without any colour factor (the constant in Tr(T^a T^a) - 4) is a scalar, broadcast below *)
  If[z8tens === {}, z8cur = {1, Z8Z}; z8labs = {}; z8rest = {}, {z8cur, z8labs} = First[z8tens]; z8rest = Rest[z8tens]];
  While[z8rest =!= {},
    z8k = First[Ordering[-Length[Intersection[z8labs, #[[2]]]] & /@ z8rest, 1]];   (* the factor sharing most labels *)
    {z8f, z8fl} = z8rest[[z8k]]; z8rest = Delete[z8rest, z8k];
    z8shared = Intersection[z8labs, z8fl];
    If[z8shared === {},
      z8cur = z8ptp[z8cur, z8f]; z8labs = Join[z8labs, z8fl],
      z8freeC = Select[z8labs, !MemberQ[z8shared, #] &]; z8freeF = Select[z8fl, !MemberQ[z8shared, #] &];
      z8ordC = Flatten[Position[z8labs, #, {1}, Heads -> False] & /@ Join[z8freeC, z8shared]];
      z8ordF = Flatten[Position[z8fl, #, {1}, Heads -> False] & /@ Join[z8shared, z8freeF]];
      z8dC = z8labDims[z8freeC]; z8dF = z8labDims[z8freeF]; z8sd = Times @@ z8labDims[z8shared];
      z8m1 = z8pmap[ArrayReshape[Transpose[#, InversePermutation[z8ordC]], {Times @@ z8dC, z8sd}] &, z8cur];
      z8m2 = z8pmap[ArrayReshape[Transpose[#, InversePermutation[z8ordF]], {z8sd, Times @@ z8dF}] &, z8f];
      z8prod = z8pdot[z8m1, z8m2];
      z8cur = If[Join[z8dC, z8dF] === {}, z8pmap[#[[1, 1]] &, z8prod], z8pmap[ArrayReshape[#, Join[z8dC, z8dF]] &, z8prod]];
      z8labs = Join[z8freeC, z8freeF]];
    If[Times @@ z8labDims[z8labs] > z8maxArray, Return[$TooLarge]]];
  z8miss = Select[z8ext, !MemberQ[z8labs, #] &];
  Do[z8cur = z8ptp[z8cur, {ConstantArray[1, z8dim[z8m[[1]]]], Z8Z}]; AppendTo[z8labs, z8m], {z8m, z8miss}];
  If[Sort[z8labs] =!= Sort[z8ext], Return[$Failed]];    (* a dummy left over, or a label that is not external *)
  If[z8ext =!= {}, z8ordC = Flatten[Position[z8labs, #, {1}, Heads -> False] & /@ z8ext];
    z8cur = z8pmap[Transpose[#, InversePermutation[z8ordC]] &, z8cur]];
  z8cur];
(* non-zero short circuit: ONE non-zero component proves a polynomial non-zero, so a few random
   assignments are tried first; a zero verdict is never drawn from them (the full array decides).
   Kept vertices are the common case in the build path, where the full array cost 4 s per
   coupling on block 43 against 0.7 s for the enumeration's early exit (2026-09-04). *)
z8sampleNonzeroQ[z8p_, z8ext_] := Module[{z8dims = z8dim[#[[1]]] & /@ z8ext},
  z8ext =!= {} && AnyTrue[Table[RandomInteger[{1, #}] & /@ z8dims, {8}], colourAt[z8p, z8ext, #] =!= 0 &]];
z8polyZeroQ[z8p_, z8ext_] := Module[{z8terms, z8arrs, z8tot},
  If[z8sampleNonzeroQ[z8p, z8ext], Return[False]];
  z8terms = If[Head[z8p] === Plus, List @@ z8p, {z8p}];
  z8arrs = z8termArr[#, z8ext] & /@ z8terms;
  If[MemberQ[z8arrs, $TooLarge], Print["[colour] array above DIM8_MAXARRAY, vertex kept untested: ", z8ext]; Return[False]];
  If[MemberQ[z8arrs, $Failed], Print["[colour] unsupported colour term, vertex kept: ", StringTake[ToString[z8p, InputForm], UpTo[300]]]; Return[False]];
  z8tot = Total[(#[[1]] (#[[2, 1]] + If[#[[2, 2]] === Z8Z, 0, Sqrt[3] #[[2, 2]]])) & /@ z8arrs];
  If[z8ext === {}, Expand[z8tot] === 0, Union[Expand /@ Flatten[z8tot]] === {0}]];
colourZeroQEnum[z8c_, z8ext_] := Module[{z8dims, z8polys},
  z8dims = If[#[[1]] === Colour, 3, 8] & /@ z8ext;
  If[Times @@ z8dims > z8maxCombos, Return[False]];
  z8polys = Select[colourSplit[z8c], # =!= 0 &];
  AllTrue[z8polys, Function[z8p, NoneTrue[Tuples[Range /@ z8dims], colourAt[z8p, z8ext, #] =!= 0 &]]]];
colourZeroQ[z8c_] := Module[{z8ext, z8polys},
  If[!colourQ[z8c], Return[False]];
  z8ext = Union[Cases[z8c, Index[Colour | Gluon, Ext[_]], Infinity]];
  If[z8colourEnum, Return[colourZeroQEnum[z8c, z8ext]]];
  z8polys = Select[colourSplit[z8c], # =!= 0 &];
  AllTrue[z8polys, z8polyZeroQ[#, z8ext] &]];
canonVerts[z8v_List] := Module[{z8cv},
  z8cv = {#[[1]], canonCoup[#[[2]]]} & /@ z8v;
  z8cv = Select[z8cv, #[[2]] =!= 0 &];
  Select[z8cv, !colourZeroQ[#[[2]]] &]];

(* ---- Lorentz/Dirac-level zero test of a residual vertex (2026-09-05) ------------------------
   What survives canonicalisation and the exact colour test can still vanish through a Lorentz
   identity that no syntactic rule knows (Schouten: five antisymmetrised indices vanish in 4D,
   which is how the h.c. of an operator with a dual field strength comes back), through a
   Clifford identity, or through momentum conservation.  Q_{q^2GBD}^{(3)} (block 66) kept six
   such residual vertices, all zero.  So every survivor is evaluated EXACTLY as a polynomial:
   momenta are symbols p[i, mu] with the last one fixed by conservation (all incoming), every
   external Lorentz index is contracted with a symbolic vector e[k, mu], Lorentz dummies are
   summed against the metric, ME/FV/SP/Eps become components, Dirac structures become explicit
   4x4 matrices (Dirac representation, gamma5 = i g0 g1 g2 g3, ProjP = (1+gamma5)/2,
   Sig = i/2 [g, g]) with the external spin indices enumerated, and what remains is a
   polynomial in the p and e components whose colour coefficients go through the tensor test.
   A tensor vanishes iff that polynomial does, so nothing is sampled.  Eps is Signature with
   DIM8_EPSSIGN (default +1) as overall sign; only an identity mixing Eps with gamma5 could
   depend on it, and none is expected in a Hermiticity residual.  Unsupported structures
   (charge conjugation, anything left symbolic) keep the vertex flagged, with a message. *)
z9epsSign = If[Environment["DIM8_EPSSIGN"] === $Failed, 1, ToExpression[Environment["DIM8_EPSSIGN"]]];
z9eta = DiagonalMatrix[{1, -1, -1, -1}];
z9sigma = {{{0, 1}, {1, 0}}, {{0, -I}, {I, 0}}, {{1, 0}, {0, -1}}};
z9gam = Join[{ArrayFlatten[{{IdentityMatrix[2], 0}, {0, -IdentityMatrix[2]}}]}, Table[ArrayFlatten[{{0, z9sigma[[z9k]]}, {-z9sigma[[z9k]], 0}}], {z9k, 3}]];
z9g5 = I z9gam[[1]].z9gam[[2]].z9gam[[3]].z9gam[[4]];
z9gamOf[5] = z9g5; z9gamOf[z9m_Integer /; 1 <= z9m <= 4] := z9gam[[z9m]];
z9projP = (IdentityMatrix[4] + z9g5)/2; z9projM = (IdentityMatrix[4] - z9g5)/2;
z9sigM[z9m_, z9n_] := I/2 (z9gamOf[z9m].z9gamOf[z9n] - z9gamOf[z9n].z9gamOf[z9m]);
z9dmat[zGA[z9m_Integer]] := z9gamOf[z9m]; z9dmat[zPP] := z9projP; z9dmat[zPM] := z9projM;
z9dmat[zSIG[z9m_Integer, z9n_Integer]] := z9sigM[z9m, z9n]; z9dmat[z9x_] := (Print["[lorentz] unknown chain element: ", InputForm[z9x]]; Throw[$Failed, z9lor]);
z9pv[z9i_, z9m_, z9n_] := If[z9i < z9n, z9p[z9i, z9m], -Sum[z9p[z9j, z9m], {z9j, z9n - 1}]];
(* sum one index type term by term: z9pick[term] gives the index objects to sum, z9w[idx, value] the weight *)
z9sumIdx[z9e_, z9pick_, z9w_] := Module[{z9x = Expand[z9e], z9terms},
  z9terms = If[Head[z9x] === Plus, List @@ z9x, {z9x}];
  Total[Function[z9t, Module[{z9t2 = z9t}, Do[z9t2 = Sum[(z9t2 /. z9d -> z9v) z9w[z9d, z9v], {z9v, 4}], {z9d, z9pick[z9t]}]; z9t2]] /@ z9terms]];
(* a contracted index is any label that is not Ext[k]: FeynmanRules names its dummies mu$123,
   OptimizeIndex (used on the residual) names them \[Alpha]1, \[Beta]1, ... without a dollar *)
z9dummyQ[Ext[_]] := False; z9dummyQ[_] := True;
z9lorHeads = _zL | _zS | _zEPS | _zME | _zFV | _zSP | _zGA | _zPP | _zPM | _zSIG | _zTD | _zTDf | _zSLP | _Ga | _ProjP | _ProjM | _Sig | _TensDot | _SlashedP | _CC | Index[Lorentz | Spin, _];
z9lorentzKeepQ[z9v_] := Module[{z9r = z9lorentzZeroQ[z9v]},
  If[z9r === $Failed, Print["[lorentz] unsupported structure, vertex kept flagged: ", z9v[[1, All, 1]]]];
  z9r =!= True];
z9lorentzZeroQ[z9v_] := Catch[Module[{z9c = z9v[[2]], z9n = Length[z9v[[1]]], z9sp, z9ze, z9ext, z9polys},
  (* every FeynRules head goes inert BEFORE any integer is substituted: FeynRules rewrites
     TensDot[..][3, 4], Ga[1, 3, 4] and friends on sight *)
  z9c = z9c /. {HoldPattern[Eps[z9a_, z9b_, z9c2_, z9d_]] :> zEPS[z9a, z9b, z9c2, z9d], ME -> zME, FV -> zFV, SP -> zSP,
                Ga -> zGA, ProjP -> zPP, ProjM -> zPM, Sig -> zSIG, TensDot -> zTD, SlashedP -> zSLP};
  z9c = z9c /. {Index[Lorentz, z9x_] :> zL[z9x], Index[Spin, z9x_] :> zS[z9x]};
  (* HoldPattern everywhere: FeynRules evaluates TensDot[x][a, b] to x[a, b], so an unheld
     TensDot[z9objs__][a_, b_] pattern becomes (z9objs__)[a_, b_] and matches p[1, 1] *)
  (* chains as flat expressions: Cases does not look inside heads, so the Lorentz indices of a
     TensDot[...][a, b] head would never be summed *)
  z9c = z9c /. zTD[z9objs__][z9a_, z9b_] :> zTDf[{z9objs}, z9a, z9b];
  z9c = z9c /. {zSLP[z9i_, z9a_, z9b_] :> Sum[z9eta[[z9d, z9d]] zFV[z9i, z9d] zGA[z9d, z9a, z9b], {z9d, 4}],
                zTDf[{z9pre___, zSLP[z9i_], z9post___}, z9a_, z9b_] :> Sum[z9eta[[z9d, z9d]] zFV[z9i, z9d] zTDf[{z9pre, zGA[z9d], z9post}, z9a, z9b], {z9d, 4}]};
  z9sp = Union[Cases[z9c, zS[Ext[_]], Infinity]];
  Do[z9ze = z9c /. Thread[z9sp -> z9sv];
     (* external Lorentz indices against symbolic vectors, Lorentz dummies against the metric, spin dummies plain *)
     z9ze = z9sumIdx[z9ze, Function[z9t, Union[Cases[z9t, zL[Ext[_]], Infinity]]], Function[{z9d, z9val}, z9e[z9d[[1, 1]], z9val]]];
     z9ze = z9sumIdx[z9ze, Function[z9t, Union[Cases[z9t, zL[_?z9dummyQ], Infinity]]], Function[{z9d, z9val}, z9eta[[z9val, z9val]]]];
     z9ze = z9sumIdx[z9ze, Function[z9t, Union[Cases[z9t, zS[_?z9dummyQ], Infinity]]], Function[{z9d, z9val}, 1]];
     z9ze = z9ze /. {zME[z9i_Integer, z9j_Integer] :> z9eta[[z9i, z9j]], zEPS[z9a_Integer, z9b_Integer, z9c2_Integer, z9d_Integer] :> z9epsSign Signature[{z9a, z9b, z9c2, z9d}]};
     z9ze = z9ze /. {zSP[z9i_, z9j_] :> Sum[z9eta[[z9m, z9m]] z9pv[z9i, z9m, z9n] z9pv[z9j, z9m, z9n], {z9m, 4}], zFV[z9i_, z9m_Integer] :> z9pv[z9i, z9m, z9n]};
     z9ze = z9ze /. {zTDf[z9objs_List, z9a_Integer, z9b_Integer] :> (Dot @@ (z9dmat /@ z9objs))[[z9a, z9b]],
                     zGA[z9m_Integer, z9a_Integer, z9b_Integer] :> z9gamOf[z9m][[z9a, z9b]], zPP[z9a_Integer, z9b_Integer] :> z9projP[[z9a, z9b]],
                     zPM[z9a_Integer, z9b_Integer] :> z9projM[[z9a, z9b]], zSIG[z9m_Integer, z9n2_Integer, z9a_Integer, z9b_Integer] :> z9sigM[z9m, z9n2][[z9a, z9b]],
                     HoldPattern[IndexDelta[z9a_Integer, z9b_Integer]] :> KroneckerDelta[z9a, z9b]};
     z9ze = Expand[z9ze];
     If[z9ze === 0, Continue[]];
     If[!FreeQ[z9ze, z9lorHeads],   (* something stayed symbolic: unsupported, keep the flag *)
       Print["[lorentz] unsupported leftovers: ", Take[Union[Cases[z9ze, z9lorHeads, Infinity]], UpTo[6]] // InputForm]; Throw[$Failed, z9lor]];
     If[!colourQ[z9ze], Throw[False, z9lor]];
     z9ext = Union[Cases[z9ze, Index[Colour | Gluon, Ext[_]], Infinity]];
     z9polys = Select[colourSplit[z9ze], # =!= 0 &];
     If[!AllTrue[z9polys, z8polyZeroQ[#, z9ext] &], Throw[False, z9lor]],
     {z9sv, Tuples[Range[4], Length[z9sp]]}];
  True], z9lor];
(* load-time self-test: identities that must vanish and near misses that must not *)
Module[{zl1 = Index[Lorentz, Ext[1]], zl2 = Index[Lorentz, Ext[2]], zl3 = Index[Lorentz, Ext[3]], zl4 = Index[Lorentz, Ext[4]], zld = Index[Lorentz, Lorentz$1],
        zs1 = Index[Spin, Ext[3]], zs2 = Index[Spin, Ext[4]], zlegs = {{V, 1}, {V, 2}, {F, 3}, {F, 4}}, zsch, zres},
  zsch = (SP[1, 2] Eps[zl1, zl2, zl3, zl4] - FV[1, zl1] Eps[zld, zl2, zl3, zl4] FV[2, zld] - FV[1, zl2] Eps[zl1, zld, zl3, zl4] FV[2, zld] - FV[1, zl3] Eps[zl1, zl2, zld, zl4] FV[2, zld] - FV[1, zl4] Eps[zl1, zl2, zl3, zld] FV[2, zld]);
  zres = {z9lorentzZeroQ[{zlegs, zsch}], !z9lorentzZeroQ[{zlegs, zsch + 2 FV[1, zl4] Eps[zl1, zl2, zl3, zld] FV[2, zld]}],
    z9lorentzZeroQ[{zlegs, TensDot[Ga[zl1], Ga[zl2]][zs1, zs2] + TensDot[Ga[zl2], Ga[zl1]][zs1, zs2] - 2 ME[zl1, zl2] IndexDelta[zs1, zs2]}],
    z9lorentzZeroQ[{zlegs, TensDot[Ga[zl1], Ga[zl2]][zs1, zs2] - TensDot[Ga[zl2], Ga[zl1]][zs1, zs2] + 2 I Sig[zl1, zl2, zs1, zs2]}],
    z9lorentzZeroQ[{zlegs, ProjP[zs1, zs2] + ProjM[zs1, zs2] - IndexDelta[zs1, zs2]}],
    z9lorentzZeroQ[{zlegs, SlashedP[1, zs1, zs2] - Ga[zld, zs1, zs2] FV[1, zld]}],
    z9lorentzZeroQ[{zlegs, FV[1, zl1] + FV[2, zl1] + FV[3, zl1] + FV[4, zl1]}],
    !z9lorentzZeroQ[{zlegs, Ga[zl1, zs1, zs2] - Ga[zl2, zs1, zs2]}],
    !z9lorentzZeroQ[{zlegs, TensDot[Ga[zl1], ProjP][zs1, zs2] - TensDot[Ga[zl1], ProjM][zs1, zs2]}],
    z9lorentzZeroQ[{zlegs, T[Index[Gluon, Ext[1]], Index[Colour, Ext[3]], Index[Colour, Ext[4]]] (Ga[zld, zs1, zs2] ME[zld, zl1] - Ga[zl1, zs1, zs2])}],
    !z9lorentzZeroQ[{zlegs, T[Index[Gluon, Ext[1]], Index[Colour, Ext[3]], Index[Colour, Ext[4]]] Ga[zl1, zs1, zs2] Eps[zl1, zl2, zld, Index[Lorentz, Lorentz$2]] FV[1, zld] FV[2, Index[Lorentz, Lorentz$2]]}]};
  Print["[lorentz] self-test (Schouten, flipped, Clifford anticommutator, commutator vs Sig, projectors, slash, conservation, two near misses, colour times metric identity, colour times Eps p p): ", zres];
  If[zres =!= ConstantArray[True, 11], Print["[lorentz] FATAL: the Lorentz/Dirac zero test fails its self-test"]; Quit[3]]];

(* ---- term-wise evaluation -------------------------------------------------------------
   FeynmanRules collects vertices across the whole expanded Lagrangian and its cost grows
   roughly quadratically with the number of expanded terms: one of the 24 monomials of
   Q_{q^2W^2D}^{(2)} (720 expanded terms) takes 16 s to expand and 147 s in FeynmanRules,
   the full block never finished in 31 h.  Feynman rules are linear in the Lagrangian, so
   the block is evaluated monomial by monomial (same ExpandIndices options and the same
   post-processing as the emitted Module), the expanded pieces are grouped into chunks of
   at most DIM8_CHUNK terms, FeynmanRules runs per chunk and MergeVertices adds the
   couplings of identical vertices.  The h.c. buckets (z8lagN, z8lagS) get their HC per
   chunk, and the Hermiticity test is FeynmanRules[L - HC[L]] per chunk exactly as
   CheckHermiticity does it.  DIM8_TERMWISE=0 restores the whole-block path.
   Worker-side names carry a z9 prefix: the z8 names are the emitted index symbols and
   assigning to one of them (z8s1 = ...) leaks into the evaluated Lagrangian. *)
z9epsCanon = Eps[z9a__] :> Signature[{z9a}] Eps[Sequence @@ Sort[{z9a}]];
z9nt[z9e_] := If[Head[z9e] === Plus, Length[z9e], 1];
z9post[z9l_] := (OptimizeIndex[z9l] /. z9epsCanon) /. del[z9x_, z9m1_] del[z9x_, z9m2_] Eps[z9n1__, z9m1_, z9n2__, z9m2_, z9n3__] :> 0;
(* The h.c. piece and the Hermiticity normalisation MUST expand with the same option as the
   direct piece.  Without FlavorExpand -> {SU2W, SU2D}, FeynmanRules expands the generation
   indices of the conjugate piece into members (e, mu, ta, ...), the direct and conjugate
   halves never merge, and a complex block comes out generation-expanded on one side:
   L8op400 gave 228 vertices term-wise against 21 whole-block (found 2026-09-03). *)
z9hc[z9l_] := z9post[ExpandIndices[HC[z9l], FlavorExpand -> {SU2W, SU2D}]];
(* CheckHermiticity normalises BOTH sides with OptimizeIndex[ExpandIndices[.]] before subtracting;
   without that the Dirac chains of L and HC[L] differ syntactically and nothing cancels *)
z9norm[z9l_] := OptimizeIndex[ExpandIndices[z9l, FlavorExpand -> {SU2W, SU2D}]] /. z9epsCanon;   (* same post-processing as the direct part, else L - HC[L] keeps del del Eps terms that vanish only by antisymmetry *)
z9pieces[nm_String] := Module[{z9body, z9sets},
  z9body = Extract[ToExpression[nm, InputForm, OwnValues], {1, 2}, Hold];
  z9sets = Cases[z9body, HoldPattern[Set[z9v_, ExpandIndices[z9s_, ___] /. z8fmgr]] :> {Hold[z9v], Hold[z9s]}, Infinity];
  (* A block that is not one of ours has no z8lagH = ExpandIndices[...] /. z8fmgr structure to
     match, so nothing is found and the block would build as empty.  SMEFTsim's dimension-six
     classes are exactly that case: L6cl1 := (cG OG + ...)/LambdaSMEFT^2, with the ExpandIndices
     calls buried inside each operator's own definition.  Fall back to evaluating the block and
     splitting the result into monomials, which is what the chunking needs and all it needs.
     The Hermitian-conjugate flag is False for those: SMEFTsim's classes that need an h.c. add
     it themselves (L6cl5, L6cl6, L6cl8d), so the worker must not add a second one. *)
  If[z9sets === {},
    Module[{z9ev = Expand[ToExpression[nm]]},
      Print["[foreign] ", nm, " has no dim8auto block structure; split as a plain Lagrangian"];
      Return[{False, #} & /@ If[Head[z9ev] === Plus, List @@ z9ev, {z9ev}]]]];
  Flatten[Table[With[{z9hcQ = z9set[[1]] =!= Hold[z8lagH], z9ev = Expand[ReleaseHold[z9set[[2]]]]},
      {z9hcQ, #} & /@ If[Head[z9ev] === Plus, List @@ z9ev, {z9ev}]], {z9set, z9sets}], 1]];
z9vertsTermwise[nm_String] := Module[{z9ps, z9lags, z9chunks, z9cur, z9n, z9vs, z9hs, z9fm, z9tot, z9L, z9t, z9c, z9i, z9start, z9ck, z9sig},
  z9fm = If[Not[FeynmanGauge], {G0|GP|GPbar -> 0}, {}];
  z9tE = z9tV = z9tH = 0;
  z9t = AbsoluteTime[];
  z9ps = z9pieces[nm];
  If[z9epseps, z9ps = {#[[1]], Expand[#[[2]] /. z9epsepsRule]} & /@ z9ps;
    Print["[epseps] ", nm, " monomials after the Eps-pair rewrite ", Total[z9nt[#[[2]]] & /@ z9ps]]];
  z9lags = {#[[1]], z9post[ExpandIndices[#[[2]], FlavorExpand -> {SU2W, SU2D}] /. z9fm]} & /@ z9ps;
  z9lags = Select[z9lags, #[[2]] =!= 0 &];
  If[z9maxlegs =!= None || z9minlegs =!= None,
    z9dropped = 0; z9lags = {#[[1]], z9legFilter[#[[2]]]} & /@ z9lags; z9lags = Select[z9lags, #[[2]] =!= 0 &];
    Print["[legs] ", nm, " leg range ", {z9minlegs, z9maxlegs}, ": terms dropped before FeynmanRules ", z9dropped, ", kept ", Total[z9nt[#[[2]]] & /@ z9lags]]];
  If[z9split, z9lags = Flatten[Table[If[Head[z9l[[2]]] === Plus, {z9l[[1]], #} & /@ (List @@ z9l[[2]]), {z9l}], {z9l, z9lags}], 1];
    Print["[split] ", nm, " monomial structure flattened: ", Length[z9lags], " expanded terms are the chunk units"]];
  z9chunks = {}; z9cur = {}; z9n = 0;
  Do[If[z9cur =!= {} && (z9n + z9nt[z9l[[2]]] > z9chunk || z9cur[[1, 1]] =!= z9l[[1]]),
       AppendTo[z9chunks, z9cur]; z9cur = {}; z9n = 0];
     AppendTo[z9cur, z9l]; z9n += z9nt[z9l[[2]]], {z9l, z9lags}];
  If[z9cur =!= {}, AppendTo[z9chunks, z9cur]];
  z9tE = Round[AbsoluteTime[] - z9t, 0.1];
  Print["[termwise] ", nm, " monomials ", Length[z9ps], " expanded terms ", Total[z9nt[#[[2]]] & /@ z9lags], " chunks ", Length[z9chunks], " tExpand ", z9tE];
  z9vs = {}; z9hs = {}; z9start = 1;
  z9ck = vdir <> "/" <> nm <> ".partial.mx"; z9sig = Hash[{Length /@ z9chunks, z9chunk, z9maxlegs, z9minlegs, z9epseps, z9hermOnly, z9split}];
  If[z9checkpoint && FileExistsQ[z9ck],
    Quiet[Get[z9ck]];
    If[ValueQ[z9ckSig] && z9ckSig === z9sig, z9vs = z9ckVs; z9hs = z9ckHs; z9tV = z9ckTV; z9tH = z9ckTH; z9start = z9ckDone + 1;
      Print["[checkpoint] ", nm, " resuming after chunk ", z9ckDone, " of ", Length[z9chunks]],
      Print["[checkpoint] ", nm, " partial file does not match this chunk list, starting over"]]];
  Do[z9c = z9chunks[[z9i]]; z9L = Total[z9c[[All, 2]]];
     z9tot = If[z9c[[1, 1]], z9L + z9hc[z9L], z9L];
     (* the Hermiticity-only pass needs the residual alone; recomputing the direct vertices
        cost the finish job 20 hours on a heavy W block whose vertices were already cached *)
     If[!z9hermOnly, z9t = AbsoluteTime[]; z9vs = Join[z9vs, FeynmanRules[z9tot, ScreenOutput -> False, Sequence @@ z9frOpts]]; z9tV += AbsoluteTime[] - z9t];
     If[z9herm || z9hermOnly,
       z9t = AbsoluteTime[]; z9hs = Join[z9hs, FeynmanRules[z9norm[z9tot] - z9norm[HC[z9tot]], ScreenOutput -> False, Sequence @@ z9frOpts]]; z9tH += AbsoluteTime[] - z9t];
     If[z9checkpoint, z9ckSig = z9sig; z9ckDone = z9i; z9ckVs = z9vs; z9ckHs = z9hs; z9ckTV = z9tV; z9ckTH = z9tH;
       DumpSave[z9ck <> ".tmp", {z9ckSig, z9ckDone, z9ckVs, z9ckHs, z9ckTV, z9ckTH}]; RenameFile[z9ck <> ".tmp", z9ck, OverwriteTarget -> True];
       Print["[checkpoint] ", nm, " chunk ", z9i, " of ", Length[z9chunks], " saved, vertices so far ", Length[z9vs]]],
     {z9i, z9start, Length[z9chunks]}];
  If[z9checkpoint && FileExistsQ[z9ck], DeleteFile[z9ck]];
  {If[z9vs === {}, {}, MergeVertices[z9vs]], If[z9hs === {}, {}, MergeVertices[z9hs]]}];

(* A block is addressed by NAME.  The dimension-eight catalogue names its blocks L8op<n>, so an
   integer argument still works and means that; a string argument lets a Lagrangian block that is
   not ours be cached the same way, which is how SMEFTsim's dimension-six classes L6cl1...L6cl8d
   enter the same vertex cache and the same UFO without any of the merge logic changing. *)
(* The dimension-six blocks, to first order in the base's first-order corrections.  The operator
   file (gen/make_dim6.py) evaluates each operator on the corrected couplings and the rotated
   fields, and names the corrections in DIM6$FirstOrder.  A product of an operator with ONE of them
   is a 1/Lambda^4 term and belongs in the model; a product with two is 1/Lambda^6 beside a
   dimension-six coefficient and does not, and an operator with four gauge fields produces them
   up to the fourth power.  The file drops what it can see as an explicit power; this drops the
   rest, on the finished vertex, where a coupling is an honest polynomial in the parameters.
   With no list, or an empty one (the --linear file), nothing happens. *)
z9firstOrder[z9vs_List] := If[! (ListQ[DIM6$FirstOrder] && DIM6$FirstOrder =!= {}), z9vs,
  Module[{z9r = (# -> z9ordeps #) & /@ DIM6$FirstOrder, z9out},
    z9out = Function[z9v, {z9v[[1]], Module[{z9e = Expand[z9v[[2]] /. z9r]},
      (z9e /. z9ordeps -> 0) + Coefficient[z9e, z9ordeps, 1]]}] /@ z9vs;
    Print["[firstorder] ", Length[z9vs], " vertices cut at first order in ", DIM6$FirstOrder, ", ",
          Count[z9out, {_, 0}], " of them vanish"];
    DeleteCases[z9out, {_, 0}]]];
runblk[n_Integer] := runblk["L8op" <> ToString[n]];
runblk[nm_String] := Module[{mx, st, tt, lagX, te, tv, th, nv, nh, nraw},
  mx = vdir <> "/" <> nm <> ".mx";
  st = vdir <> "/" <> nm <> ".status";
  (* DIM8_HERMONLY: revisit blocks built with the check deferred (status "nonhermitian -1")
     and run only the Hermiticity test on them, leaving the cached vertices alone. *)
  If[z9hermOnly,
    If[! (FileExistsQ[mx] && FileExistsQ[st]), Print["[skip] ", nm, " not built yet"]; Return[Null]];
    If[! StringContainsQ[Import[st, "Text"], "nonhermitian -1"],
      Print["[skip] ", nm, " already checked"]; Return[Null]];
    tt = AbsoluteTime[];
    (* a block built with a leg cap (status "maxlegs n", or "minlegs n") must be checked with the
       same cap: without it the residual of a capped G^4 block recomputes the eight-gluon vertices
       that the cap was there to avoid (shard 1 of the finish pass on 433, 2026-09-05) *)
    z9stCap = StringCases[Import[st, "Text"], "maxlegs " ~~ z9d : DigitCharacter .. :> ToExpression[z9d]];
    z9stMin = StringCases[Import[st, "Text"], "minlegs " ~~ z9d : DigitCharacter .. :> ToExpression[z9d]];
    {z9maxSaved, z9minSaved} = {z9maxlegs, z9minlegs};
    If[z9stCap =!= {}, z9maxlegs = First[z9stCap]]; If[z9stMin =!= {}, z9minlegs = First[z9stMin]];
    z9frOpts = z9mkFrOpts[];
    If[z9stCap =!= {} || z9stMin =!= {}, Print["[herm] ", nm, " checked with the block's own leg range: ", {z9minlegs, z9maxlegs}]];
    z9rawH = If[z9termwise, z9vertsTermwise[nm][[2]], CheckHermiticity[Symbol[nm], ScreenOutput -> False]];
    {z9maxlegs, z9minlegs} = {z9maxSaved, z9minSaved}; z9frOpts = z9mkFrOpts[];
    z9tCol = AbsoluteTime[]; z9resid = canonVerts[z9rawH]; z9nCol = Length[z9resid];
    z9resid = Select[z9resid, z9lorentzKeepQ]; nh = Length[z9resid]; z9tCol = Round[AbsoluteTime[] - z9tCol, 0.1];
    Print["[hermlorentz] ", nm, " survivors of the colour test ", z9nCol, ", of the Lorentz/Dirac test ", nh];
    th = Round[AbsoluteTime[] - tt, 0.1];
    Print["[hermtime] ", nm, " expand ", z9tE, " residual FeynmanRules (with HC and normalisation) ", Round[z9tH, 0.1], " canonicalisation+colour test ", z9tCol, " raw residual vertices ", Length[z9rawH]];
    (* DIM8_HERMDUMP=1: keep the evidence of a flag, the raw residual (before canonicalisation
       and the colour test) and the survivors, in <vdir>/<nm>.herm.mx, and name the surviving
       vertices by their legs *)
    If[Environment["DIM8_HERMDUMP"] === "1", DumpSave[vdir <> "/" <> nm <> ".herm.mx", {z9rawH, z9resid}];
      Print["[hermdump] ", nm, " raw residual vertices ", Length[z9rawH], " surviving ", nh, ": ", (#[[1, All, 1]] & /@ z9resid)]];
    Export[st, StringReplace[Import[st, "Text"],
      {"nonhermitian -1" -> "nonhermitian " <> ToString[nh],
       RegularExpression["tHerm [0-9.]+"] -> "tHerm " <> ToString[th]}], "Text"];
    Print["[herm] ", nm, " | nonhermitian ", nh, " | tHerm ", th];
    Return[Null]];
  If[FileExistsQ[mx] && FileExistsQ[st],
    Print["[skip] ", nm, " cached"]; Return[Null]];

  If[z9termwise,
    {z9rawV, z9rawH} = z9vertsTermwise[nm]; te = z9tE;
    tt = AbsoluteTime[]; nraw = Length[z9rawV]; FR$Vert = canonVerts[z9rawV];
    If[StringStartsQ[nm, "L6"], FR$Vert = z9firstOrder[FR$Vert]]; tv = Round[z9tV + AbsoluteTime[] - tt, 0.1];
    nv = Length[FR$Vert];
    DumpSave[mx, FR$Vert];
    tt = AbsoluteTime[];
    nh = If[z9herm, Length[Select[canonVerts[z9rawH], z9lorentzKeepQ]], -1];
    th = If[z9herm, Round[z9tH + AbsoluteTime[] - tt, 0.1], 0],
    (* whole-block path *)
    tt = AbsoluteTime[]; lagX = Symbol[nm]; te = Round[AbsoluteTime[] - tt, 0.1];
    tt = AbsoluteTime[]; FR$Vert = FeynmanRules[lagX, ScreenOutput -> False, Sequence @@ z9frOpts]; nraw = Length[FR$Vert];
    FR$Vert = canonVerts[FR$Vert];
    If[StringStartsQ[nm, "L6"], FR$Vert = z9firstOrder[FR$Vert]]; tv = Round[AbsoluteTime[] - tt, 0.1];
    nv = Length[FR$Vert];
    DumpSave[mx, FR$Vert];
    tt = AbsoluteTime[];
    nh = If[z9herm, Length[Select[canonVerts[CheckHermiticity[lagX, ScreenOutput -> False]], z9lorentzKeepQ]], -1];
    th = If[z9herm, Round[AbsoluteTime[] - tt, 0.1], 0]];

  Export[st, nm <> " | vertices " <> ToString[nv] <> " | rawvertices " <> ToString[nraw] <> " | nonhermitian " <> ToString[nh] <>
             " | tEval " <> ToString[te] <> " | tVert " <> ToString[tv] <> " | tHerm " <> ToString[th] <>
             If[z9maxlegs === None, "", " | maxlegs " <> ToString[z9maxlegs]] <>
             If[z9minlegs === None, "", " | minlegs " <> ToString[z9minlegs]], "Text"];
  Print["[done] ", nm, " | vertices ", nv, " | nonhermitian ", nh,
        " | tEval ", te, " | tVert ", tv, " | tHerm ", th];
  ClearAll[FR$Vert]; Clear[lagX];
];

(* first argument may also be an explicit comma-separated block list, e.g. "43,49,54" *)
(* A token that is not an integer is taken as a block NAME and passed through unchanged, so
     fr_worker.wls L6cl1,L6cl2,L6cl8a 0
   caches those blocks off whatever base DIM8_BASE names. *)
blocks = If[StringContainsQ[args[[1]], ","] || nshards === 0,
  Function[z9t, If[StringMatchQ[z9t, NumberString], ToExpression[z9t], z9t]] /@ StringSplit[args[[1]], ","],
  Range[shard, nblocks, nshards]];
Do[runblk[n], {n, blocks}];
Print["[alldone] shard ", shard, " total ", Round[AbsoluteTime[] - t0, 0.1], " s"];
