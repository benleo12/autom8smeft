(* validate/dump_vertex_index.wls  --  export vertex FIELD CONTENT to JSON.

   The process selector runs in Python and needs two things that only FeynRules knows:
   the field content of every Standard Model vertex, and the field content of every
   dimension-eight vertex.  Neither needs the couplings, only the leg lists, so this is a
   cheap pass over data already computed and cached by fr_worker.wls.

   Usage:  wolframscript -file dump_vertex_index.wls
   Writes: build/sm_vertices.json      [[field, ...], ...]
           build/vertex_index.json     {block: [[field, ...], ...], ...}
*)

(* DIM8_ROOT lets the same script run off-machine, e.g. on an HPC system *)
$root = If[Environment["DIM8_ROOT"] === $Failed, "${DIM8_ROOT:-.}", Environment["DIM8_ROOT"]];
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
   undefined, the index entry unevaluated, and the export failed after truncating the old index. *)
files = Select[Flatten[FileNames["*.mx", #] & /@ vdirs],
  ! StringStartsQ[FileNameTake[#], "._"] && ! StringStartsQ[FileBaseName[#], "base_"] &&
  ! StringContainsQ[FileBaseName[#], "."] &];
Print["[blocks] ", Length[files], " cached blocks from ", Length[vdirs], " cache director",
  If[Length[vdirs] === 1, "y", "ies"]];
idx = Association[];
Do[Module[{nm},
   nm = FileBaseName[z8file];
   If[FileByteCount[z8file] == 0, Continue[]];   (* an empty file holds no vertex list *)
   ClearAll[FR$Vert];
   Get[z8file];
   If[! ListQ[FR$Vert], Print["[abort] ", z8file, " holds no vertex list; nothing written"]; Quit[1]];
   idx[nm] = DeleteDuplicates[fields /@ FR$Vert];
   ClearAll[FR$Vert];
  ], {z8file, files}];
(* write to a temporary file and move it into place only when the export succeeded, so that a
   failed export can never leave an empty index behind *)
z8put[z8path_, z8data_] := If[Export[z8path <> ".tmp", z8data, "JSON"] === $Failed,
  Print["[abort] could not write ", z8path, "; the previous file is kept"]; Quit[1],
  RenameFile[z8path <> ".tmp", z8path, OverwriteTarget -> True]];
z8put[$root <> "/build/vertex_index.json", idx];
Print["[blocks] wrote ", Length[idx], " blocks to build/vertex_index.json"];

(* The internal lines of a diagram.  For one dimension-eight insertion they are pure Standard
   Model, since a dimension-six vertex anywhere else would make the diagram 1/Lambda^6.  That
   stops being true as soon as the model carries dimension six, because two dimension-six
   insertions are 1/Lambda^4 and a legitimate order to work at: an operator whose vertex needs a
   second dimension-six vertex to close the diagram would then be dropped by a
   Standard-Model-only internal set, and dropping an operator that can contribute is the one
   failure mode worth spending a slightly larger model to avoid.  So when dimension-six blocks
   are in the index, their vertices join the internal set.  The Python side (gen/process.py,
   standard_model_vertices) restricts the internal lines of a DIMENSION-EIGHT block to the
   Standard Model subset of this list, since a dimension-six vertex beside a dimension-eight one
   is 1/Lambda^6; the full set is used for the dimension-six blocks only. *)
z8d6 = Select[Keys[idx], StringStartsQ[#, "L6cl"] &];
z8int = DeleteDuplicates[fields /@ smv];
If[z8d6 =!= {},
  z8int = DeleteDuplicates[Join[z8int, Flatten[Lookup[idx, z8d6], 1]]];
  Print["[internal] ", Length[z8d6], " dimension-six blocks joined the internal-line set: ",
    Length[z8int], " field contents (Standard Model alone had ", Length[DeleteDuplicates[fields /@ smv]], ")"],
  Print["[internal] Standard Model only: ", Length[z8int], " field contents"]];
z8put[$root <> "/build/sm_vertices.json", z8int];
Print["[alldone]"];
