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
$root = If[Environment["DIM8_ROOT"] === $Failed, ParentDirectory[DirectoryName[$InputFileName]], Environment["DIM8_ROOT"]];
args = Rest[$ScriptCommandLine];
outname = If[Length[args] >= 1, args[[1]], "dim8_full"];
selfile = If[Length[args] >= 2, args[[2]], ""];
If[selfile =!= "", selfile = ExpandFileName[selfile]];   (* resolve before SetDirectory *)
(* DIM8_NKERNELS: the parallel kernels WriteUFO uses for its flavour expansion and its splitting (default 2) *)
FR$NKernels = If[Environment["DIM8_NKERNELS"] === $Failed, 2, ToExpression[Environment["DIM8_NKERNELS"]]];
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";

Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];

t0 = AbsoluteTime[];
(* DIM8_BASE may name several files, separated by ";", so that a base that includes another
   model (SMEFTsim's dimension-six sector) can be loaded as the set of files it ships as.  DIM8_LSM names the
   Lagrangian symbol to take the Standard-Model-side vertices from, since SMEFTsim calls its
   dimension-six-inclusive one LSMEFT and reserves LSM for the pure Standard Model. *)
z8base = If[Environment["DIM8_BASE"] === $Failed, "base.fr", Environment["DIM8_BASE"]];
z8bases = StringTrim /@ StringSplit[z8base, ";"];
LoadModel[Sequence @@ Append[z8bases, "gen.fr"]];
Print["[time] LoadModel: ", Round[AbsoluteTime[] - t0, 0.1], " s"];
(* The blocks of the fermionic operators are cached with a general flavour coefficient (z8F2 or z8F4,
   shared, since a block holds one operator), which gen_flavour_rules.m replaces block by block by the
   operator's flavour structures (gen/emit_flavour.py) as each block is loaded.  A block must come out
   with no placeholder left, or the UFO would hold a parameter it never defines, so the load loop below
   stops on one. *)
z8flavourFile = $root <> "/tests/gen_smoke/gen_flavour_rules.m";
If[FileExistsQ[z8flavourFile], Get[z8flavourFile];
  Print["[flavour] structures of the operators of ", Length[z8FlavourRules], " blocks from gen_flavour_rules.m"],
  z8FlavourRules = <||>; z8FlavourPlaceholders = {}];
(* DIM8_EXTRA_RULES: more files of flavour rules, separated by ";", for blocks that gen.fr does not define:
   the connection operators of the models of gen/towers.py, whose file joins its rules to these *)
If[Environment["DIM8_EXTRA_RULES"] =!= $Failed,
  Scan[(Get[$root <> "/tests/gen_smoke/" <> #];
        Print["[flavour] with ", #, ": structures of the operators of ", Length[z8FlavourRules], " blocks"]) &,
       StringTrim /@ StringSplit[Environment["DIM8_EXTRA_RULES"], ";"]]];
z8placeholderQ[z8e_] := ! FreeQ[z8e, Alternatives @@ z8FlavourPlaceholders];
(* DIM8_DROPBELOW: a file of block names whose vertices with at most three legs are left out as each is
   loaded, because a model of gen/towers.py takes those vertices from another cache, computed to a higher
   order.  Unset, every vertex of every block is kept. *)
z8dropBelow = If[Environment["DIM8_DROPBELOW"] === $Failed, {},
  Select[StringTrim /@ StringSplit[Import[ExpandFileName[Environment["DIM8_DROPBELOW"]], "Text"], "\n"], # =!= "" &]];
If[z8dropBelow =!= {}, Print["[cfg] the vertices with at most three legs of ", Length[z8dropBelow], " blocks are left out"]];
(* DIM8_PROVENANCE=<file>: which block gives which coefficient to a vertex of at most three legs, recorded as the
   blocks are loaded (after the flavour rules and DIM8_DROPBELOW), for the export check of a model of order N
   (validate/geo_export_check.py --prov), which requires each coefficient to reach such a vertex from one block
   only.  A line "<block> TAB loaded TAB <vertices with at most three legs> TAB <vertices with more>" per block,
   and a line "<block> TAB vertex TAB <its fields, sorted> TAB <coefficient>" per coefficient of each such
   vertex, and last the line "#end TAB <blocks recorded>", so that a record cut off reads as such
   (hpc/write_shards.sh complete, validate/geo_export_check.py).  A coefficient is a parameter with an NP order whose name starts with c: a Wilson coefficient, a
   part of a complex one or the coefficient of a flavour structure, and not a shift of the input relations
   (gw1, vev2, ...), which every block that the base rotates carries.  DIM8_PROVENANCE_ONLY=1 stops once the
   blocks are read, without the base vertices, the merge or WriteUFO, which records the provenance of a model
   written without it.  The base is not recorded: it is not a block, and the Yukawa compensation it carries is
   meant to meet the operators of psi^2H^5 on their own vertices. *)
z8prov = Environment["DIM8_PROVENANCE"];
z8provQ = StringQ[z8prov] && z8prov =!= "";
z8provOnly = Environment["DIM8_PROVENANCE_ONLY"] === "1";
If[z8provOnly && ! z8provQ, Print["[abort] DIM8_PROVENANCE_ONLY=1 needs DIM8_PROVENANCE"]; Quit[1]];
If[z8provQ,
  Get[$root <> "/validate/np_truncate.m"]; ztInit[];
  z8provCoef = AssociationThread[Select[Keys[ztNP], ztNP[#] > 0 && StringStartsQ[SymbolName[#], "c"] &] -> True];
  z8provStream = OpenWrite[ExpandFileName[z8prov]];
  Print["[prov] the coefficients of the vertices with at most three legs, block by block, to ", z8prov, " (",
        Length[z8provCoef], " coefficients)"]];
z8provRecord[z8b_String, z8verts_List] := Module[{z8low = Select[z8verts, Length[#[[1]]] <= 3 &]},
  WriteString[z8provStream, z8b, "\tloaded\t", Length[z8low], "\t", Length[z8verts] - Length[z8low], "\n"];
  Scan[Function[z8v, Module[{z8f = StringRiffle[Sort[ToString /@ z8v[[1, All, 1]]], " "]},
    Scan[WriteString[z8provStream, z8b, "\tvertex\t", z8f, "\t", SymbolName[#], "\n"] &,
      Union[Cases[z8v[[2]], z8s_Symbol /; KeyExistsQ[z8provCoef, z8s], {0, Infinity}, Heads -> True]]]]], z8low]];

(* DIM8_VDIR may name several cache directories separated by ";".  The dimension-six sector is
   built into its own directory so that a plain dimension-eight build cannot pick it up by
   accident; a combined model asks for both.  The FIRST directory is the one the base-vertex
   cache is written to.  A block name appearing in two directories is an error rather than a
   silent choice, since the two would be different computations of the same name. *)
vdirs = StringTrim /@ StringSplit[If[Environment["DIM8_VDIR"] === $Failed,
    $root <> "/build/vertices", Environment["DIM8_VDIR"]], ";"];
vdir = First[vdirs];
Print["[cfg] base ", z8base, "  caches ", vdirs, "  FeynmanGauge ", FeynmanGauge];
(* A cache entry is a .mx file, which only the platform that wrote it can read, or the same list
   exported as .wxf, which any platform can: validate/mx_to_wxf.wls converts a cache so that it can
   be used off-machine.  A directory holds one or the other for a block. *)
files = Flatten[FileNames[{"*.mx", "*.wxf"}, #] & /@ vdirs];
files = Select[files, ! StringStartsQ[FileBaseName[#], "base_"] &];   (* base-vertex caches are not blocks *)
(* nor is anything else a worker leaves beside a block: <block>.herm.mx holds the residual of a
   Hermiticity check, not a vertex list (the load loop below explains what loading one would do) *)
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
(* Every block must have been built from the source it has now: the cache is keyed on the name
   alone, and a block that predates a change of its operator would otherwise go into the model
   unnoticed (validate/cache_source.py says how it once did).  Stale stamps stop the write; blocks
   built before the stamps existed are counted and let through. *)
Module[{z8sel = If[selfile =!= "", selfile, ""], z8rc},
  If[Run["command -v python3 > /dev/null 2>&1"] =!= 0,
    Print["[warn] no python3 here, so the cached blocks are not checked against their source"],
    z8rc = Run["python3 '" <> $root <> "/validate/cache_source.py' check '" <> StringRiffle[vdirs, ";"] <> "' " <>
               If[z8sel =!= "", "'" <> z8sel <> "'", ""]];
    If[z8rc =!= 0, Print["[abort] cached blocks built from a different source than they have now; see the check above"]; Quit[1]]]];

(* The base model's own vertices.  For our Standard Model file this is seconds and caching it
   would be pointless.  For a base that carries a dimension-six sector it is not: SMEFTsim's
   LSMEFT takes more than two hours and twenty minutes here, and it is the same
   computation on every invocation, whether the run merges three dimension-eight blocks or all
   674.  So it is cached beside the operator blocks, keyed on the base file list and the
   Lagrangian symbol, and computed once.  DIM8_NOSMCACHE=1 forces a recompute. *)
tt = AbsoluteTime[];
(* the NAMES, kept as strings: the symbols evaluate to whole Lagrangians, so hashing or
   printing it gives a different key every run and megabytes of output *)
(* DIM8_LSM may be a '+'-separated LIST of Lagrangian symbols, computed one at a time and merged.
   FeynRules is fine to a few hundred expanded terms and then blows up, so a single call on
   SMEFTsim's whole LSMEFT does not finish in seven hours while its eleven named class blocks
   are each tractable.  This is the same chunking validate/fr_worker.wls uses on our own
   dimension-eight blocks, applied to SMEFTsim's dimension-six sector. *)
z8lsmname = If[Environment["DIM8_LSM"] === $Failed, "LSM", Environment["DIM8_LSM"]];
z8lsmparts = StringTrim /@ StringSplit[z8lsmname, "+"];
(* keyed on the CONTENT of the base files as well as their names: a base file can change with
   its name unchanged, and a key on the name alone would then hand every later run the old
   vertices *)
z8smkey = IntegerString[Hash[{z8base, z8lsmname, FeynmanGauge,
    Import[FileNameJoin[{$root, "tests/gen_smoke", #}], "Text"] & /@ z8bases}, "SHA256"], 16];
z8smfile = FileNameJoin[{vdir, "base_" <> z8smkey <> ".mx"}];
If[! FileExistsQ[z8smfile] && FileExistsQ[StringReplace[z8smfile, ".mx" ~~ EndOfString -> ".wxf"]],
  z8smfile = StringReplace[z8smfile, ".mx" ~~ EndOfString -> ".wxf"]];
(* a run that leaves the base out (DIM8_NOBASE=1, every shard of hpc/write_shards.sh but shard 0) does not read or
   compute its vertices either: they would be dropped below, and a shard started before shard 0 has cached them
   would otherwise compute them again *)
Which[z8provOnly, smVerts = {}; Print["[prov] the base vertices are not read"],
  Environment["DIM8_NOBASE"] === "1", smVerts = {}; Print["[cfg] DIM8_NOBASE=1: the base vertices are not read"],
  FileExistsQ[z8smfile] && Environment["DIM8_NOSMCACHE"] === $Failed,
  If[FileExtension[z8smfile] === "wxf", FR$BaseVert = Import[z8smfile, "WXF"],
    Get[z8smfile]];                                (* restores FR$BaseVert *)
  smVerts = FR$BaseVert; ClearAll[FR$BaseVert];
  Print["[cache] base vertices from ", FileNameTake[z8smfile], ": ", Length[smVerts]],
  True,
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

(* DIM8_NOBASE=1 leaves the base model's vertices out: a model written in shards (hpc/write_shards.sh)
   carries them in one shard only, and validate/merge_ufo.py joins the shards *)
all = If[Environment["DIM8_NOBASE"] === "1", Print["[cfg] base vertices left out"]; {}, {smVerts}];
(* Every file must define FR$Vert, and the loop checks that it does.  A file that defines
   something else leaves FR$Vert without a value, AppendTo then stores the SYMBOL in the list,
   and the next file's Get gives that symbol a value before the list is next evaluated, so the
   next block would enter the model twice.  A Hermiticity dump such as L6cl5.herm.mx beside
   L6cl5.mx is such a file; the selection above already leaves it out. *)
Do[
  Module[{},
    ClearAll[FR$Vert];
    If[FileExtension[z8file] === "wxf", FR$Vert = Import[z8file, "WXF"],
      Get[z8file]];                    (* restores FR$Vert *)
    If[! ListQ[FR$Vert],
      Print["[abort] ", z8file, " does not hold a vertex list"]; Quit[1]];
    If[KeyExistsQ[z8FlavourRules, FileBaseName[z8file]], FR$Vert = FR$Vert /. z8FlavourRules[FileBaseName[z8file]]];
    If[MemberQ[z8dropBelow, FileBaseName[z8file]], FR$Vert = Select[FR$Vert, Length[#[[1]]] >= 4 &]];
    If[z8FlavourPlaceholders =!= {},
      If[z8placeholderQ[FR$Vert],
        Print["[abort] ", z8file, " keeps a general flavour coefficient after the flavour structures replace it: ",
          Union[Cases[FR$Vert, Alternatives @@ z8FlavourPlaceholders, Infinity]]]; Quit[1]]];
    If[z8provQ, z8provRecord[FileBaseName[z8file], FR$Vert]];
    If[! z8provOnly, AppendTo[all, FR$Vert]];
    ClearAll[FR$Vert];
  ], {z8file, files}];
If[z8provQ, WriteString[z8provStream, "#end\t", Length[files], "\n"]; Close[z8provStream];
  Print["[prov] ", Length[files], " blocks recorded in ", z8prov]];
If[z8provOnly, Print["[prov] stopping after the blocks are read (DIM8_PROVENANCE_ONLY=1)"]; Quit[0]];
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
(* DIM8_TRUNCATE=1: with the input-scheme base model, keep the 1/Lambda^4 content of every
   vertex.  The rotated Standard-Model Lagrangian carries pieces that vanish only through the
   parameter relations or lie beyond 1/Lambda^4, and a vertex can hold such a piece next to a
   genuine dimension-eight structure ({A,H,Z} does), so the test is made term by term, on pieces
   labelled by Lorentz/colour structure and NP order: validate/np_truncate.m. *)
(* DIM8_ORDERCUT=n, in place of DIM8_TRUNCATE: keep the terms of NP order at most n on a vertex with at most three
   legs and at most 2 on one with more, by the NP orders of their parameters alone, and remove nothing else.  These
   are the caps of validate/np_truncate.m under DIM8_GEO_N=n, which this does not load.  It writes the reference
   of export check 6 (validate/geo_export_check.py --low): the blocks of the geo tree and the base in one piece,
   with DIM8_MAXLEGS=3, which the check compares with the model NP order by NP order.  The pieces that vanish
   only through the parameter relations stay in, and cancel in the value of a vertex.  The vertices with more
   legs than DIM8_MAXLEGS go first, so that they are not expanded.  The numerical value of every parameter is
   set once with validate/update_parameters.m, as the truncation leaves it: WriteUFO asks for each, and FeynRules'
   own definition of an internal parameter runs through the whole tree of its definition every time. *)
If[Environment["DIM8_ORDERCUT"] =!= $Failed,
  If[Environment["DIM8_TRUNCATE"] === "1",
    Print["[abort] DIM8_ORDERCUT and DIM8_TRUNCATE are two ways to cut a model: set one of them"]; Quit[1]];
  Module[{z9n = ToExpression[Environment["DIM8_ORDERCUT"]], z9np, z9tag, z9eps, z9ord, z9cut, z9all = 0, z9kept = 0,
      z9t = AbsoluteTime[]},
    If[! IntegerQ[z9n] || z9n < 2, Print["[abort] DIM8_ORDERCUT is the order N of the model, 2 or more"]; Quit[1]];
    If[Environment["DIM8_MAXLEGS"] =!= $Failed,
      merged = Select[merged, Length[#[[1]]] <= ToExpression[Environment["DIM8_MAXLEGS"]] &]];
    z9np[z9p_] := Module[{z9io = InteractionOrder /. Flatten[{z9p[[2]]}]},
      If[z9io === InteractionOrder, 0,
        Total[Cases[If[MatchQ[z9io, {_Symbol, _Integer}], {z9io}, z9io], {NP, z9k_Integer} :> z9k]]]];
    z9tag = Dispatch[(#[[1]] -> z9eps^z9np[#] #[[1]]) & /@ Select[M$Parameters, z9np[#] > 0 &]];
    z9ord[z9x_] := Exponent[(z9x /. Conjugate[z9c_] :> z9c) /. z9tag, z9eps];
    z9cut[{z9f_, z9e_}] := Module[{z9cap = If[Length[z9f] <= 3, z9n, 2],
        z9ts = (If[Head[#] === Plus, List @@ #, {#}] &)[Expand[z9e]], z9k},
      z9k = Select[z9ts, z9ord[#] <= z9cap &];
      z9all += Length[z9ts]; z9kept += Length[z9k];
      {z9f, Total[z9k]}];
    merged = Select[z9cut /@ merged, #[[2]] =!= 0 &];
    Print["[ordercut] ", z9kept, " of ", z9all, " terms kept by their NP order (at most ", z9n,
      " on a vertex with at most three legs, 2 with more), ", Length[merged], " vertices (",
      Round[AbsoluteTime[] - z9t, 0.1], " s)"]];
  Get[$root <> "/validate/update_parameters.m"]; z8UpdateParameters[]];
If[Environment["DIM8_TRUNCATE"] === "1",
  Get[$root <> "/validate/np_truncate.m"];
  tt = AbsoluteTime[];
  {merged, z9rep} = ztTruncate[merged];
  ztPrintReport[z9rep];
  Print["[time] truncation: ", Round[AbsoluteTime[] - tt, 0.1], " s, ", Length[merged], " vertices kept"]];
(* DIM8_DRYRUN=1: report the merge and the truncation, and stop before WriteUFO *)
If[Environment["DIM8_DRYRUN"] === "1", Print["[dryrun] stopping before WriteUFO"]; Quit[0]];
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
   the file no longer imports.  The g^{mu nu} photon-Z-Higgs coefficient reaches 5810 terms when
   the vev, the gauge couplings and the field rotation are all written as tagged sums.  So the
   limit is lifted, and the written files are read back and rejected if they hold an
   unevaluated Mathematica expression. *)
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
