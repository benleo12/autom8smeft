(* validate/dump_vertex_index.wls  --  export vertex FIELD CONTENT to JSON.

   The process selector runs in Python and needs two things that only FeynRules knows:
   the field content of every Standard Model vertex, and the field content of every
   dimension-eight vertex.  Neither needs the couplings, only the leg lists, so this is a
   cheap pass over data already computed and cached by fr_worker.wls.

   Usage:  wolframscript -file dump_vertex_index.wls
   Writes: build/sm_vertices.json      [[field, ...], ...]
           build/vertex_index.json     {block: [[field, ...], ...], ...}
           build/lsm_vertices.json     [[field, ...], ...], the base Lagrangian LSM alone

   DIM8_INDEX_TAG names a variant of the lists, written beside the default ones instead of over
   them: with a Feynman-gauge base and cache, DIM8_INDEX_TAG=_fg writes build/vertex_index_fg.json,
   build/sm_vertices_fg.json and build/lsm_vertices_fg.json, which ship in build/ with the release
   and which gen/lambda_series.py counts longitudinal W and Z bosons with.

   DIM8_INDEX_MERGE=1 keeps the blocks of an existing vertex_index<tag>.json that the caches named here
   do not hold, for a corrected operator rebuilt in a cache of its own.  Without it the list holds
   exactly the blocks of those caches.
*)

(* DIM8_ROOT lets the same script run off-machine, e.g. on an HPC system *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
(* the tag goes into file names, so it may hold letters, digits and underscores only *)
z8tag = If[Environment["DIM8_INDEX_TAG"] === $Failed, "", Environment["DIM8_INDEX_TAG"]];
If[! StringMatchQ[z8tag, RegularExpression["[A-Za-z0-9_]*"]],
  Print["[abort] DIM8_INDEX_TAG may hold letters, digits and underscores only: ", z8tag]; Quit[1]];
FR$NKernels = 2;
FR$PathOverride = $root <> "/external/feynrules/feynrules-current";
Get[$root <> "/tests/fr_env/fr_headless_init.m"];
SetDirectory[$root <> "/tests/gen_smoke"];

(* DIM8_BASE, as elsewhere, may name several files separated by ";" *)
z8base = If[Environment["DIM8_BASE"] === $Failed, "base.fr", Environment["DIM8_BASE"]];
LoadModel[Sequence @@ Append[StringTrim /@ StringSplit[z8base, ";"], "gen.fr"]];

fields[v_] := ToString /@ v[[1, All, 1]];

smv = FeynmanRules[LSM, ScreenOutput -> False];
Print["[sm] ", Length[smv], " vertices"];

(* DIM8_VDIR may name several cache directories separated by ";", as the writer allows, so that
   the dimension-six blocks in their own directory are indexed alongside the dimension-eight
   ones. *)
vdirs = StringTrim /@ StringSplit[If[Environment["DIM8_VDIR"] === $Failed,
    $root <> "/build/vertices", Environment["DIM8_VDIR"]], ";"];
(* A file whose base name has a dot, such as L6cl5.herm.mx, the dump of a Hermiticity check, holds
   no vertex list and is skipped, as the writer skips it.  Loaded as a block it left FR$Vert
   undefined, the index entry unevaluated, and the export failed after truncating the old index.
   A block is read from its .mx file or from a .wxf file, the portable form that
   validate/mx_to_wxf.wls writes for a cache moved to another platform, as the writer reads either. *)
files = Select[Flatten[FileNames[{"*.mx", "*.wxf"}, #] & /@ vdirs],
  ! StringStartsQ[FileNameTake[#], "._"] && ! StringStartsQ[FileBaseName[#], "base_"] &&
  ! StringContainsQ[FileBaseName[#], "."] &];
Print["[blocks] ", Length[files], " cached blocks from ", Length[vdirs], " cache director",
  If[Length[vdirs] === 1, "y", "ies"]];
idx = Association[];
Do[Module[{nm},
   nm = FileBaseName[z8file];
   If[FileByteCount[z8file] == 0, Continue[]];   (* an empty file holds no vertex list *)
   ClearAll[FR$Vert];
   If[FileExtension[z8file] === "wxf", FR$Vert = Import[z8file, "WXF"], Get[z8file]];
   If[! ListQ[FR$Vert], Print["[abort] ", z8file, " holds no vertex list; nothing written"]; Quit[1]];
   idx[nm] = DeleteDuplicates[fields /@ FR$Vert];
   ClearAll[FR$Vert];
  ], {z8file, files}];
If[Environment["DIM8_INDEX_MERGE"] === "1" && FileExistsQ[$root <> "/build/vertex_index" <> z8tag <> ".json"],
  z8old = Import[$root <> "/build/vertex_index" <> z8tag <> ".json", "RawJSON"];
  If[! AssociationQ[z8old], Print["[abort] build/vertex_index", z8tag, ".json cannot be read to merge into; nothing written"]; Quit[1]];
  idx = Join[z8old, idx];
  Print["[blocks] merged with the ", Length[z8old], " blocks of build/vertex_index", z8tag, ".json"]];
(* write to a temporary file and move it into place only when the export succeeded, so that a
   failed export can never leave an empty index behind *)
z8put[z8path_, z8data_] := If[Export[z8path <> ".tmp", z8data, "JSON"] === $Failed,
  Print["[abort] could not write ", z8path, "; the previous file is kept"]; Quit[1],
  RenameFile[z8path <> ".tmp", z8path, OverwriteTarget -> True]];
z8put[$root <> "/build/vertex_index" <> z8tag <> ".json", idx];
Print["[blocks] wrote ", Length[idx], " blocks to build/vertex_index", z8tag, ".json"];

(* The internal lines of a diagram.  For one dimension-eight insertion they are pure Standard
   Model, since a dimension-six vertex anywhere else would make the diagram 1/Lambda^6.  That
   stops being true as soon as the model carries dimension six, because two dimension-six
   insertions are 1/Lambda^4 and a legitimate order to work at: an operator whose vertex needs a
   second dimension-six vertex to close the diagram would then be dropped by a
   Standard-Model-only internal set, and dropping an operator that can contribute is the one
   failure mode worth spending a slightly larger model to avoid.  So when dimension-six blocks
   are in the index, their vertices join this list, which then holds the whole dimension-six
   sector beside the Standard Model.  The Python side takes the internal lines of every block
   from the Standard Model subset of the list (gen/process.py, standard_model_vertices).  A
   dimension-six vertex beside a dimension-eight one is 1/Lambda^6, and a tree with two
   dimension-six vertices enters 1/Lambda^4 only through its interference with the Standard Model,
   which gen/process.py select_dim6 asks for coefficient by coefficient, one second vertex at a
   time, of the same coefficient or another, from build/dim6_index.json (validate/dim6_index.py). *)
z8d6 = Select[Keys[idx], StringStartsQ[#, "L6cl"] &];
z8int = DeleteDuplicates[fields /@ smv];
(* The base Lagrangian's own field contents, before any dimension-six block joins them: the list
   that gen/process.py's Standard Model vertices are compared with in both directions (by a
   test of the development tree), since the internal-line set below can hold the same content
   from a dimension-six block. *)
z8put[$root <> "/build/lsm_vertices" <> z8tag <> ".json", z8int];
If[z8d6 =!= {},
  z8int = DeleteDuplicates[Join[z8int, Flatten[Lookup[idx, z8d6], 1]]];
  Print["[internal] ", Length[z8d6], " dimension-six blocks joined the internal-line set: ",
    Length[z8int], " field contents (Standard Model alone had ", Length[DeleteDuplicates[fields /@ smv]], ")"],
  Print["[internal] Standard Model only: ", Length[z8int], " field contents"]];
z8put[$root <> "/build/sm_vertices" <> z8tag <> ".json", z8int];
Print["[alldone]"];
