(* Common headless initialisation for FeynRules 2.3 (the build uses 2.3.49) on Mathematica 14 and 15.
   Usage (in a .wls, with $root the repository):   Get[$root <> "/tests/fr_env/fr_headless_init.m"]
   Set FR$PathOverride before Get to the FeynRules directory.  Without it the directory is
   external/feynrules/feynrules-current under the repository this file is in, which is what the
   scripts in validate/ set it to.
   Set FR$NKernels before Get to choose the number of parallel subkernels (default 4, 0 = serial).
   Nothing under $FeynRulesPath is modified: both compatibility settings below are applied at
   runtime in the kernel. *)
If[!ValueQ[FR$PathOverride], FR$PathOverride = FileNameJoin[{ParentDirectory[ParentDirectory[DirectoryName[$InputFileName]]], "external", "feynrules", "feynrules-current"}]];
$FeynRulesPath = FR$PathOverride;
If[!ValueQ[FR$NKernels], FR$NKernels = 4];

(* Setting 1: Mathematica >= 14.1 ships a Protected System`MatrixSymbol.  FeynRules defines its
   own MatrixSymbol (mixing-matrix accessor in Core/MassDiagonalization.m), so the built-in is
   unprotected and cleared before FeynRulesPackage.m is read. *)
(* Setting 2: from Mathematica 12.2, ValueQ[f[x]] returns True whenever f has ANY definition
   (Method->Automatic = "SymbolDefinitionsPresent").  FeynRules assumes the 12.1 semantics
   (True only if f[x] actually evaluates) in Core/ExtractVertexTools.m:71 (NameIndices),
   Core/FRFormat.m:90,106 (IntLor/Int), Core/ClassDeclarations.m:1873-1877 (AddOrderBlock/MGOrder),
   Interfaces/UFO/PYIntVertices.m:730,896.  The legacy method gives those semantics at all of
   these places at once.
   Setting 3: Mathematica 15 ships a Protected System`Commutator.  FeynRules defines its own in
   Core/ExtractVertexTools.m:110-135, the contraction rules of fields with creation operators that
   FeynmanRules extracts every vertex with, so the built-in is unprotected and cleared as well.  It
   is addressed by name, so that on Mathematica 14, which has no such symbol, nothing is created.
   All settings are applied on the master kernel and on every subkernel. *)
FRFix[] := (Unprotect[System`MatrixSymbol]; ClearAll[System`MatrixSymbol];
  If[Names["System`Commutator"] =!= {}, Unprotect["System`Commutator"]; ClearAll["System`Commutator"]];
  SetOptions[ValueQ, Method -> "Legacy"];);
FRFix[];
If[FR$NKernels > 0,
  LaunchKernels[FR$NKernels];
  ParallelEvaluate[Unprotect[System`MatrixSymbol]; ClearAll[System`MatrixSymbol];
    If[Names["System`Commutator"] =!= {}, Unprotect["System`Commutator"]; ClearAll["System`Commutator"]];
    SetOptions[ValueQ, Method -> "Legacy"];];
  FR$Parallel = True;
  FR$KernelNumber = 0;  (* FeynRules.m calls LaunchKernels[FR$KernelNumber]: 0 -> it reuses the kernels launched above *)
  ,
  FR$Parallel = False;
];
Off[General::stop];
(* FeynRules must be findable by name.  On a machine where it is not installed under
   $UserBaseDirectory/Applications this only works if its directory is on $Path, so add it
   explicitly rather than relying on the ambient environment (needed to run off-machine,
   e.g. on an HPC system). *)
If[! MemberQ[$Path, $FeynRulesPath], PrependTo[$Path, $FeynRulesPath]];
<< FeynRules`;
(* Without FeynRules LoadModel and FeynmanRules stay unevaluated, and a script that compares cached vertices
   would compare them as they are and still print a verdict.  So nothing goes on without it. *)
If[! MemberQ[$Packages, "FeynRules`"],
  Print["[init] ABORT: FeynRules did not load from ", $FeynRulesPath, ": unpack FeynRules 2.3.49 there, or set FR$PathOverride to its directory"]; Quit[1]];
If[FR$NKernels > 0, FR$KernelNumber = $KernelCount];  (* only used in FeynRules progress messages *)
(* Setting 4: LoadModel lists the blocks of the external parameters (ParametersMG in
   Core/ClassDeclarations.m) by removing repeated names with
       list //. {xx___, a_, yy___, a_, zz___} -> {xx, a, yy, zz}
   which removes one repetition per pass and costs the cube of the number of external parameters:
   9 s for the 1031 coefficients of block DIM8 alone and six minutes once the 2507 of the flavour
   structures in block DIM8F are there.  It leaves the first occurrence of each name in order, which
   is DeleteDuplicates, and that replaces it in the definition.  The rule is found by its form, a
   pattern name that occurs twice between three sequences, so that a FeynRules without it is left as
   it is. *)
FRDedupe = HoldPattern[ReplaceRepeated[x_, Verbatim[Rule][{Verbatim[Pattern][_, Verbatim[BlankNullSequence][]],
      Verbatim[Pattern][a_, Verbatim[Blank][]], Verbatim[Pattern][_, Verbatim[BlankNullSequence][]],
      Verbatim[Pattern][a_, Verbatim[Blank][]], Verbatim[Pattern][_, Verbatim[BlankNullSequence][]]}, _]]];
Print["[init] block names of the parameters deduplicated with DeleteDuplicates: ",
  Count[DownValues[ParametersMG], FRDedupe, Infinity], " place(s)"];
DownValues[ParametersMG] = DownValues[ParametersMG] /. FRDedupe :> DeleteDuplicates[x];
Print["[init] FeynRules ", FR$VersionNumber, " loaded on Mathematica ", $Version, " with ", $KernelCount, " subkernels"];
Print["[init] DownValues[MatrixSymbol] master/sub: ", Length[DownValues[MatrixSymbol]], " / ", If[FR$NKernels>0, ParallelEvaluate[Length[DownValues[MatrixSymbol]]], "n/a"]];
Print["[init] Options[ValueQ] master/sub: ", Options[ValueQ], " / ", If[FR$NKernels>0, ParallelEvaluate[Options[ValueQ]], "n/a"]];
