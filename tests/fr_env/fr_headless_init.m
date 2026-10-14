(* Common headless initialisation for FeynRules 2.3 (the build uses 2.3.49) on Mathematica 14.x.
   Usage (in a .wls, with $root the repository):   Get[$root <> "/tests/fr_env/fr_headless_init.m"]
   Set FR$PathOverride before Get to the FeynRules directory; the scripts in validate/ set it to
   external/feynrules/feynrules-current under $root.
   Set FR$NKernels before Get to choose the number of parallel subkernels (default 4, 0 = serial).
   Nothing under $FeynRulesPath is modified: both compatibility settings below are applied at
   runtime in the kernel. *)
If[!ValueQ[FR$PathOverride], FR$PathOverride = "$HOME/Downloads/feynrules-current"];
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
   these places at once.  Both settings are applied on the master kernel and on every subkernel. *)
FRFix[] := (Unprotect[System`MatrixSymbol]; ClearAll[System`MatrixSymbol]; SetOptions[ValueQ, Method -> "Legacy"];);
FRFix[];
If[FR$NKernels > 0,
  LaunchKernels[FR$NKernels];
  ParallelEvaluate[Unprotect[System`MatrixSymbol]; ClearAll[System`MatrixSymbol]; SetOptions[ValueQ, Method -> "Legacy"];];
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
If[FR$NKernels > 0, FR$KernelNumber = $KernelCount];  (* only used in FeynRules progress messages *)
Print["[init] FeynRules ", FR$VersionNumber, " loaded on Mathematica ", $Version, " with ", $KernelCount, " subkernels"];
Print["[init] DownValues[MatrixSymbol] master/sub: ", Length[DownValues[MatrixSymbol]], " / ", If[FR$NKernels>0, ParallelEvaluate[Length[DownValues[MatrixSymbol]]], "n/a"]];
Print["[init] Options[ValueQ] master/sub: ", Options[ValueQ], " / ", If[FR$NKernels>0, ParallelEvaluate[Options[ValueQ]], "n/a"]];
