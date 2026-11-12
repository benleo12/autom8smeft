(* validate/truncexp.m  --  ExpandIndices with the terms above a leg cap never built.

   Usage, after LoadModel:   Get[$root <> "/validate/truncexp.m"];
                             z9expandIdxB[expr, cap, ExpandIndices options...] /. z9abbrevBack

   ExpandIndices multiplies out every factor first: a monomial with eight Higgs doublets and a field
   strength is expanded into all its terms with up to eleven legs, and one such monomial of T12op46 takes
   more than five hours, although only the terms with at most three legs are kept.  A doublet gives its
   vacuum value or one field (Phi[1] -> 0, Phi[2] -> (v + H)/Sqrt[2] in unitary gauge, plus the Goldstones
   in Feynman gauge).  The doublet definitions are graded by z9g on their field part, and FieldExpand drops
   each term whose lowest power of z9g is above the cap as it expands, so a term with more doublet fields
   than the cap is never built.  Every term kept is the term ExpandIndices gives without the cut, and the
   caller's own selection (a leg filter, MaxParticles) still runs on the result.

   The second cost is the parameters.  The doublet's vacuum value is vevSM (1 + vev1 + ... + vev4), and with
   FR$FExpand on FeynRules expands every product of such sums inside ExpandIndices: six doublets at their
   vacuum value are 210 terms that go through the index machinery one by one.  Each parameter sum in a field
   definition is replaced by a symbol z9P<k> during ExpandIndices.  The result carries those symbols, and
   the caller puts them back with /. z9abbrevBack.

   DIM8_TRUNCEXP=0 turns both off.  They are also off when a field other than the Higgs doublet has a
   vacuum value, or when the rewritten definitions do not give back the model's.

   validate/fr_worker.wls loads it for the leg cap DIM8_MAXLEGS, lowered for each monomial by the legs of its
   factors without a doublet (each gives at least one), and validate/check_bilinears_geo.wls takes the
   two-point terms through it with cap 2. *)
z9truncexp = Environment["DIM8_TRUNCEXP"] =!= "0";
z9phiQ[z9x_] := ! FreeQ[z9x, Phi | Phibar];
FeynRules`numQ[z9g] = True; FeynRules`CnumQ[z9g] = False;
z9vacPart[z9r_] := z9r /. {(z9f_Symbol?FieldQ)[___] :> 0, z9f_Symbol?FieldQ :> 0};
(* Only rules without patterns are rewritten, and never through With: With injecting a value into a
   rule renames the rule's pattern variables, so Ta[a_, b_, c_] :> PauliSigma[a, b, c]/2 came out with
   the global a, b, c on its right-hand side (and b, c are quark fields). *)
z9gradeRule[z9rule : (Rule | RuleDelayed)[z9l_, z9r_]] /; FreeQ[z9rule, Pattern | Blank] && ! FreeQ[z9l, Phi | Phibar] :=
  ReplacePart[z9rule, 2 -> z9vacPart[z9r] + z9g (z9r - z9vacPart[z9r])];
z9gradeRule[z9x_] := z9x;
(* the bound needs every field with a vacuum value to be the doublet: if a definition of another field has a
   constant part, the truncation is off *)
z9vevHeads = Union[Cases[MR$Definitions, (Rule | RuleDelayed)[z9l_, z9r_] /; FreeQ[z9r, Pattern | Blank] && FieldQ[If[AtomQ[z9l], z9l, Head[z9l]]] === True &&
    ! FreeQ[z9r, _Symbol?FieldQ] && (z9vacPart[z9r] /. HCanti -> Identity) =!= 0 :> If[AtomQ[z9l], z9l, Head[z9l]]]];
If[z9truncexp && ! SubsetQ[{Phi, Phibar}, z9vevHeads], z9truncexp = False;
  Print["[truncexp] OFF: fields other than the Higgs doublet have a vacuum value: ", z9vevHeads]];
Print["[truncexp] ", If[z9truncexp, "on", "off"], "; fields with a vacuum value ", z9vevHeads];
(* a term is dropped only when its lowest power of z9g is an integer above the bound; FeynRules also calls
   FieldExpand on lists (SU(2) Eps contractions), which are cut element by element *)
z9keepQ[z9t_, z9b_] := With[{z9e = Quiet[Exponent[z9t, z9g, Min]]}, ! (IntegerQ[z9e] && z9e > z9b)];
z9cutG[z9x_, z9b_] := Which[Head[z9x] === Plus, Select[z9x, z9keepQ[#, z9b] &], Head[z9x] === List, z9cutG[#, z9b] & /@ z9x,
  True, If[z9keepQ[z9x, z9b], z9x, 0]];
z9fieldFreeSumQ[z9x_] := Head[z9x] === Plus && FreeQ[z9x, _Symbol?FieldQ | (_Symbol?FieldQ)[___]] && ! NumericQ[z9x];
z9abbrevBack = {}; z9abN = 0;
z9abbrevSym[z9s_] := Module[{z9old = Cases[z9abbrevBack, (z9p_ -> z9s) :> z9p]},
  If[z9old =!= {}, First[z9old],
    z9abN++; With[{z9p = Symbol["z9P" <> ToString[z9abN]]},
      FeynRules`numQ[z9p] = True; FeynRules`CnumQ[z9p] = ! FreeQ[z9s, HCanti | Conjugate | I | Complex];
      AppendTo[z9abbrevBack, z9p -> z9s]; z9p]]];
(* ReplaceAll leaves the rest of a RuleDelayed right-hand side unevaluated; the symbol is put in with the
   With[..., z9p /; True] idiom, since a plain :> would leave z9abbrevSym[...] unevaluated inside the held part.
   The sum is looked up after evaluation, so Phibar's 1 + HCanti[vev1] + ... is the same z9P as Phi's. *)
z9abbrevRule[z9rule : (Rule | RuleDelayed)[_, z9r_]] /; FreeQ[z9rule, Pattern | Blank] && ! FreeQ[z9r, _Symbol?FieldQ | (_Symbol?FieldQ)[___]] :=
  z9rule /. z9s_?z9fieldFreeSumQ :> With[{z9p = z9abbrevSym[z9s]}, z9p /; True];
z9abbrevRule[z9x_] := z9x;
If[z9truncexp,
  z9defsAbbrev = z9abbrevRule /@ MR$Definitions; z9defsGraded = z9gradeRule /@ z9defsAbbrev;
  z9chg = Select[Range[Length[MR$Definitions]], z9defsGraded[[#]] =!= MR$Definitions[[#]] &];
  Print["[truncexp] parameter sums kept whole during ExpandIndices: ", InputForm[z9abbrevBack]];
  Print["[truncexp] field definitions rewritten: ", InputForm[z9defsGraded[[z9chg]]]];
  (* the rewritten rules have no patterns, so their right-hand sides can be evaluated and compared *)
  If[(Rule @@@ (z9defsAbbrev[[z9chg]] /. z9abbrevBack)) =!= (Rule @@@ MR$Definitions[[z9chg]]) ||
     (Rule @@@ (z9defsGraded[[z9chg]] /. z9g -> 1 /. z9abbrevBack)) =!= (Rule @@@ MR$Definitions[[z9chg]]) ||
     z9defsGraded[[All, 1]] =!= MR$Definitions[[All, 1]] || ! FreeQ[z9defsGraded, z9abbrevSym],
    z9truncexp = False; Print["[truncexp] OFF: the rewritten field definitions do not give back the model's"]]];
(* ExpandIndices[z9m, opts] without the terms that have more than z9b doublet fields, the parameter sums
   still abbreviated (put them back with /. z9abbrevBack); unchanged when the truncation is off *)
z9expandIdxB[z9m_, z9b_, z9opts___] := Module[{z9e},
  If[! z9truncexp, Return[ExpandIndices[z9m, z9opts]]];
  If[z9b < 0, Return[0]];
  Block[{MR$Definitions = z9defsGraded,
         FieldExpand = Function[z9x, z9cutG[If[FR$FExpand, Expand[z9x], Expand[z9x, _?(Not[FreeQ[#, _?FieldQ]] &)]], z9b]]},
    z9e = ExpandIndices[z9m, z9opts]];
  z9e /. z9g -> 1];
