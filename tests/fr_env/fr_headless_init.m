(* Common headless initialisation for FeynRules 2.3.34 on Mathematica 14.x.
   Usage (in a .wls):   Get["${DIM8_ROOT:-.}/tests/fr_env/fr_headless_init.m"]
   Set FR$NKernels before Get to choose the number of parallel subkernels (default 4, 0 = serial).
   Nothing under $FeynRulesPath is modified: all fixes are applied at runtime in the kernel. *)
If[!ValueQ[FR$PathOverride], FR$PathOverride = "$HOME/Downloads/feynrules-current"];
$FeynRulesPath = FR$PathOverride;
If[!ValueQ[FR$NKernels], FR$NKernels = 4];

(* Fix 1: Mathematica >= 14.1 ships a Protected System`MatrixSymbol; FeynRules defines its own
   MatrixSymbol (mixing-matrix accessor in Core/MassDiagonalization.m), so the built-in must be
   unprotected and cleared before FeynRulesPackage.m is read. *)
(* Fix 2: Mathematica >= 12.2 changed ValueQ[f[x]] to return True whenever f has ANY definition
   (Method->Automatic = "SymbolDefinitionsPresent"). FeynRules assumes the 12.1 semantics
   (True only if f[x] actually evaluates) in Core/ExtractVertexTools.m:71 (NameIndices),
   Core/FRFormat.m:90,106 (IntLor/Int), Core/ClassDeclarations.m:1873-1877 (AddOrderBlock/MGOrder),
   Interfaces/UFO/PYIntVertices.m:730,896. Restoring the legacy method fixes all of them at once. *)
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
