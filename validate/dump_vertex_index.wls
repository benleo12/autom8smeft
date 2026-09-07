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

LoadModel["base.fr", "gen.fr"];

fields[v_] := ToString /@ v[[1, All, 1]];

(* Internal lines are pure Standard Model: with one dimension-eight insertion a dim-6
   vertex anywhere else in the diagram is order 1/Lambda^6.  The base model carries no
   dimension six (that comes from SMEFTsim), so only LSM is exported here. *)
smv = FeynmanRules[LSM, ScreenOutput -> False];
Export[$root <> "/build/sm_vertices.json", DeleteDuplicates[fields /@ smv], "JSON"];
Print["[sm] ", Length[smv], " vertices"];

vdir = If[Environment["DIM8_VDIR"] === $Failed, $root <> "/build/vertices", Environment["DIM8_VDIR"]];
files = Select[FileNames["*.mx", vdir], ! StringStartsQ[FileNameTake[#], "._"] &];   (* skip macOS AppleDouble sidecars *)
Print["[dim8] ", Length[files], " cached blocks"];
idx = Association[];
Do[Module[{nm},
   nm = FileBaseName[z8file];
   If[FileByteCount[z8file] == 0, Continue[]];   (* SKIPPED placeholder, see fr_worker *)
   Get[z8file];
   idx[nm] = DeleteDuplicates[fields /@ FR$Vert];
   ClearAll[FR$Vert];
  ], {z8file, files}];
Export[$root <> "/build/vertex_index.json", idx, "JSON"];
Print["[dim8] wrote ", Length[idx], " blocks to build/vertex_index.json"];
Print["[alldone]"];
