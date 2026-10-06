(* validate/fr_writeufo.wls  --  merge the cached per-block vertex lists into one UFO.

   No Lagrangian is passed to WriteUFO.  The vertices were computed block by block by
   fr_worker.wls in separate processes and cached, so this step only loads them, merges
   the ones that share a particle content, and writes the UFO.  It is cheap compared with
   the work the workers already did.

   Usage:
     wolframscript -file fr_writeufo.wls [outputName] [selectionFile]

   selectionFile, if given, is a text file with one block name per line (L8op17 and so
   on): only those blocks go into the UFO.  That is how a process-oriented variant is
   built out of the same cache, with no recomputation.  With no selection every cached
   block is used.
*)

(* DIM8_ROOT lets the same script run off-machine, e.g. on an HPC system *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
args = Rest[$ScriptCommandLine];
outname = If[Length[args] >= 1, args[[1]], "dim8_full"];
selfile = If[Length[args] >= 2, args[[2]], ""];
If[selfile =!= "", selfile = ExpandFileName[selfile]];   (* resolve before SetDirectory *)
FR$NKernels = 2;
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";

Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];

t0 = AbsoluteTime[];
(* DIM8_BASE may name several files, separated by ";", so that a base built from somebody else's
   model (SMEFTsim, say) can be loaded as the set of files it ships as.  DIM8_LSM names the
   Lagrangian symbol to take the Standard-Model-side vertices from, since SMEFTsim calls its
   dimension-six-inclusive one LSMEFT and reserves LSM for the pure Standard Model. *)
z8base = If[Environment["DIM8_BASE"] === $Failed, "base.fr", Environment["DIM8_BASE"]];
z8bases = StringTrim /@ StringSplit[z8base, ";"];
LoadModel[Sequence @@ Append[z8bases, "gen.fr"]];
Print["[time] LoadModel: ", Round[AbsoluteTime[] - t0, 0.1], " s"];

(* DIM8_VDIR may name several cache directories separated by ";".  The dimension-six sector is
   built into its own directory so that a plain dimension-eight build cannot pick it up by
   accident; a combined model asks for both.  The FIRST directory is the one the base-vertex
   cache is written to.  A block name appearing in two directories is an error rather than a
   silent choice, since the two would be different computations of the same name. *)
vdirs = StringTrim /@ StringSplit[If[Environment["DIM8_VDIR"] === $Failed,
    $root <> "/build/vertices", Environment["DIM8_VDIR"]], ";"];
vdir = First[vdirs];
Print["[cfg] base ", z8base, "  caches ", vdirs, "  FeynmanGauge ", FeynmanGauge];
files = Flatten[FileNames["*.mx", #] & /@ vdirs];
files = Select[files, ! StringStartsQ[FileBaseName[#], "base_"] &];   (* base-vertex caches are not blocks *)
(* nor is anything else a worker leaves beside a block: <block>.herm.mx holds the residual of a
   Hermiticity check, not a vertex list (see the load loop below for what loading one did) *)
files = Select[files, ! StringContainsQ[FileBaseName[#], "."] &];
Module[{dup = Select[Tally[FileBaseName /@ files], #[[2]] > 1 &]},
  If[dup =!= {}, Print["[abort] the same block name is cached in more than one directory: ",
    dup[[All, 1]]]; Quit[1]]];
If[selfile =!= "",
  Module[{want = Select[StringTrim /@ StringSplit[Import[selfile, "Text"], "\n"], # =!= "" &]},
    files = Select[files, MemberQ[want, FileBaseName[#]] &];
    Print["[sel] ", Length[want], " blocks requested, ", Length[files], " found in the cache"];
    If[Length[files] < Length[want], Print["[abort] requested blocks missing from the cache"]; Quit[1]]];
];
Print["[load] ", Length[files], " cached vertex lists"];

(* The base model's own vertices.  For our Standard Model file this is seconds and caching it
   would be pointless.  For a base that carries a dimension-six sector it is not: SMEFTsim's
   LSMEFT ran past two hours and twenty minutes here without finishing, and it is the same
   computation on every invocation, whether the run merges three dimension-eight blocks or all
   674.  So it is cached beside the operator blocks, keyed on the base file list and the
   Lagrangian symbol, and computed once.  DIM8_NOSMCACHE=1 forces a recompute. *)
tt = AbsoluteTime[];
(* the NAMES, kept as strings: the symbols evaluate to whole Lagrangians, so hashing or
   printing it gives a different key every run and megabytes of output *)
(* DIM8_LSM may be a '+'-separated LIST of Lagrangian symbols, computed one at a time and merged.
   FeynRules is fine to a few hundred expanded terms and then blows up, so a single call on
   SMEFTsim's whole LSMEFT ran seven hours without finishing while its eleven named class blocks
   are each tractable.  This is the same chunking validate/fr_worker.wls uses on our own
   dimension-eight blocks, applied to somebody else's dimension-six sector. *)
z8lsmname = If[Environment["DIM8_LSM"] === $Failed, "LSM", Environment["DIM8_LSM"]];
z8lsmparts = StringTrim /@ StringSplit[z8lsmname, "+"];
(* keyed on the CONTENT of the base files as well as their names: on 2026-10-03 the input-scheme
   base changed its Higgs sector with the file name unchanged, and a key on the name alone would
   have handed every later run the old vertices *)
z8smkey = IntegerString[Hash[{z8base, z8lsmname, FeynmanGauge,
    Import[FileNameJoin[{$root, "tests/gen_smoke", #}], "Text"] & /@ z8bases}, "SHA256"], 16];
z8smfile = FileNameJoin[{vdir, "base_" <> z8smkey <> ".mx"}];
If[FileExistsQ[z8smfile] && Environment["DIM8_NOSMCACHE"] === $Failed,
  Get[z8smfile];                                   (* restores FR$BaseVert *)
  smVerts = FR$BaseVert; ClearAll[FR$BaseVert];
  Print["[cache] base vertices from ", FileNameTake[z8smfile], ": ", Length[smVerts]],
  smVerts = MergeVertices @@ Table[
    Module[{tp = AbsoluteTime[], v},
      v = FeynmanRules[Symbol[part], ScreenOutput -> False];
      Print["  [base] ", part, ": ", Length[v], " vertices (",
            Round[AbsoluteTime[] - tp, 0.1], " s)"];
      v], {part, z8lsmparts}];
  FR$BaseVert = smVerts;
  DumpSave[z8smfile, FR$BaseVert];
  ClearAll[FR$BaseVert];
  Print["[cache] base vertices computed and saved to ", FileNameTake[z8smfile]]];
Print["[time] base (", z8lsmname, ") vertices: ", Length[smVerts],
      " (", Round[AbsoluteTime[] - tt, 0.1], " s)"];

all = {smVerts};
(* Every file must define FR$Vert, and the loop checks that it did.  It did not use to.  A file
   that defines something else leaves FR$Vert without a value, AppendTo then stores the SYMBOL in
   the list, and the next file's Get gives that symbol a value before the list is next evaluated:
   the next block is in the model twice.  L6cl5.herm.mx, the dump of a Hermiticity check, sat
   beside L6cl5.mx in the dimension-six cache, and the dim68_is written on 2026-10-04 carried
   every dimension-six Yukawa operator at twice its strength, in a model whose earlier builds had
   agreed with SMEFTsim on exactly those vertices. *)
Do[
  Module[{},
    ClearAll[FR$Vert];
    Get[z8file];                       (* restores FR$Vert *)
    If[! ListQ[FR$Vert],
      Print["[abort] ", z8file, " does not hold a vertex list"]; Quit[1]];
    AppendTo[all, FR$Vert];
    ClearAll[FR$Vert];
  ], {z8file, files}];
If[! AllTrue[all, ListQ], Print["[abort] a loaded vertex list is not a list"]; Quit[1]];
Print["[load] ", Length[all], " vertex lists, ", Total[Length /@ all], " vertices before merge"];

tt = AbsoluteTime[];
merged = MergeVertices @@ all;
Print["[merge] ", Length[merged], " vertices (", Round[AbsoluteTime[] - tt, 0.1], " s)"];

tt = AbsoluteTime[];
(* DIM8_NPORDER raises the NP coupling-order limit.  Each dimension-eight coupling carries
   NP order 2, so with the default limit of 2 MadGraph will not generate a diagram with two
   dimension-eight vertices even though the vertices are present: it needs NP 4.  Only set
   this for a deliberate 1/Lambda^8 study, since with the limit at 4 the usual NP^2==2
   selection no longer cleanly means "dim-6 squared plus dim-8 interference". *)
If[Environment["DIM8_NPORDER"] =!= $Failed,
  M$InteractionOrderLimit = M$InteractionOrderLimit /.
    {NP, _} -> {NP, ToExpression[Environment["DIM8_NPORDER"]]};
  Print["[cfg] NP coupling-order limit raised to ", Environment["DIM8_NPORDER"],
        " (two dimension-eight insertions allowed)"]];
(* DIM8_TRUNCATE=1: with the input-scheme base model the rotated SM Lagrangian carries a few
   vertices ({A,A,H}, {A,H,Z}, {A,nu,nubar}, ...) whose couplings are polynomials in the shift
   parameters that vanish only through the parameter relations: FeynRules keeps them because
   they are not syntactically zero, and numerically they are O(Lambda^-8), below the
   truncation (measured 1e-9 relative at Lam = 3 TeV).  Drop a merged vertex only if its
   coupling vanishes at zero coefficients, responds to the input-scheme coefficients, and
   scales as Lambda^-8 between 3 and 6 TeV (ratio 2^-8): a genuine dim-8 vertex scales as 2^-4
   and an SM one not at all, so neither can be caught. *)
If[Environment["DIM8_TRUNCATE"] === "1",
  Module[{z9wc, z9lam0, z9rulesAt, z9coef, z9mag, z9c0, z9c3, z9c6, z9keep, z9dropped},
    z9wc = Select[{c8W2H4x1, c8W2H4x3, c8B2H4x1, c8WBH4x1, c8H6x1, c8H6x2, c8l2H4Dx2, c8l2H4Dx4}, MemberQ[First /@ M$Parameters, #] &];
    z9lam0 = NumericalValue[Lam];
    z9rulesAt[z9vals_List, z9l_] := (UpdateParameters[Sequence @@ Thread[z9wc -> z9vals], Lam -> z9l];
      (# -> NumericalValue[#]) & /@ Select[First /@ M$Parameters, NumericQ[NumericalValue[#]] &]);
    z9coef[z9t_] := Which[NumericQ[z9t], Abs[N[z9t]], Head[z9t] === Times, Abs[N[Times @@ Cases[z9t, _?NumericQ, {1}]]], True, 1.];
    z9mag[z9c_, z9r_] := Module[{z9e = Expand[z9c /. z9r]}, Max[z9coef /@ If[Head[z9e] === Plus, List @@ z9e, {z9e}]]];
    z9c0 = With[{z9r = z9rulesAt[0 z9wc, 3000]}, z9mag[#[[2]], z9r] & /@ merged];
    z9c3 = With[{z9r = z9rulesAt[1 + 0 z9wc, 3000]}, z9mag[#[[2]], z9r] & /@ merged];
    z9c6 = With[{z9r = z9rulesAt[1 + 0 z9wc, 6000]}, z9mag[#[[2]], z9r] & /@ merged];
    UpdateParameters[Sequence @@ Thread[z9wc -> 0], Lam -> z9lam0];
    z9keep = Table[! (z9c0[[z9i]] < 10^-12 Max[1, z9c3[[z9i]]] && z9c3[[z9i]] > 0 && z9c6[[z9i]]/z9c3[[z9i]] < 2^-6), {z9i, Length[merged]}];
    z9dropped = Pick[merged, Not /@ z9keep];
    Print["[truncate] dropped ", Length[z9dropped], " Lambda^-8 vertices: ", (#[[1, All, 1]] & /@ z9dropped)];
    merged = Pick[merged, z9keep]]];
(* DIM8_MAXLEGS=n: drop merged vertices with more than n legs before writing, so a UFO is
   consistent whatever leg cap the cached blocks were built with (see fr_worker.wls). *)
If[Environment["DIM8_MAXLEGS"] =!= $Failed,
  Module[{z9ml = ToExpression[Environment["DIM8_MAXLEGS"]], z9drop},
    z9drop = Select[merged, Length[#[[1]]] > z9ml &];
    Print["[maxlegs] dropped ", Length[z9drop], " vertices with more than ", z9ml, " legs; legs -> count ", Tally[Length[#[[1]]] & /@ z9drop]];
    merged = Select[merged, Length[#[[1]]] <= z9ml &]]];
(* A coupling of more than 4096 terms.  FeynRules adds up the terms of a vertex that share a
   colour and a Lorentz structure through an UpValue,
       CollectCouplObject[a_] + CollectCouplObject[b_] := CollectCouplObject[a + b]
   (Interfaces/UFO/PYIntVertices.m), which Mathematica applies once per term, re-evaluating the
   same sum each time.  At the default $IterationLimit of 4096 a structure with more terms than
   that is never summed.  The evaluation is terminated, WriteUFO prints one message among
   thousands of lines and carries on, and what it writes into vertices.py for that structure is
   the text "C." <> TerminatedEvaluation[IterationLimit]: the coupling is lost at every order and
   the file no longer imports.  The g^{mu nu} photon-Z-Higgs coefficient reached 5810 terms once
   the vev, the gauge couplings and the field rotation were all written as tagged sums, and two
   models were written that way on 2026-10-04 before the cause was found.  The limit is lifted,
   and the written file is read back, because a limit nobody knew about is exactly the kind of
   thing that comes back. *)
$IterationLimit = Infinity;
If[FR$NKernels > 0, ParallelEvaluate[$IterationLimit = Infinity]];
Print["[cfg] IterationLimit ", $IterationLimit, "  largest vertex: ",
      Max[Length[If[Head[#] === Plus, #, {#}] &[Expand[#[[2]]]]] & /@ merged], " terms"];
WriteUFO[Input -> merged, Output -> outname, AddDecays -> False, Optimization -> False];
Module[{z9txt = StringJoin[Import[FileNameJoin[{outname, #}], "Text"] & /@ {"vertices.py", "couplings.py", "lorentz.py", "parameters.py"}]},
  If[StringContainsQ[z9txt, "TerminatedEvaluation" | "ClassAttributeCreation" | "PYDicEntry" | "$Failed" | "$Aborted"],
    Print["[abort] the written model contains an unevaluated Mathematica expression; it is not a usable UFO"]; Quit[1]]];
Print["[ufo] ", outname, " written in ", Round[AbsoluteTime[] - tt, 0.1], " s"];
Print["[alldone] total ", Round[AbsoluteTime[] - t0, 0.1], " s"];
