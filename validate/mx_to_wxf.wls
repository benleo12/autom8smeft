(* validate/mx_to_wxf.wls  --  convert a vertex cache to the portable WXF format.

     wolframscript -file validate/mx_to_wxf.wls <cache dir> <output dir>

   A .mx file can only be read on the platform that wrote it, so a cache built on one machine cannot
   be used by validate/fr_writeufo.wls on another, for instance a cluster.  The same vertex lists
   exported as WXF can, and the writer reads either.  Every operator block (FR$Vert) and every
   base-vertex cache (FR$BaseVert) is converted and read back, and the conversion stops if a list
   does not survive the round trip unchanged.  The Hermiticity dumps <block>.herm.mx hold no
   vertex list and are skipped. *)
z9args = Rest[$ScriptCommandLine];
If[Length[z9args] < 2, Print["usage: wolframscript -file mx_to_wxf.wls <cache dir> <output dir>"]; Quit[2]];
{z9in, z9out} = ExpandFileName /@ z9args[[1 ;; 2]];
Quiet[CreateDirectory[z9out, CreateIntermediateDirectories -> True]];
z9files = Select[FileNames["*.mx", z9in], ! StringContainsQ[FileBaseName[#], "."] &];
z9n = 0;
Do[
  ClearAll[FR$Vert, FR$BaseVert];
  Get[z9f];
  z9v = Which[ListQ[FR$Vert], FR$Vert, ListQ[FR$BaseVert], FR$BaseVert, True, $Failed];
  If[z9v === $Failed, Print["[skip] ", FileNameTake[z9f], " holds no vertex list"]; Continue[]];
  z9w = FileNameJoin[{z9out, FileBaseName[z9f] <> ".wxf"}];
  Export[z9w, z9v, "WXF"];
  If[Import[z9w, "WXF"] =!= z9v, Print["[abort] ", FileNameTake[z9f], " does not survive the round trip"]; Quit[1]];
  (* the status travels with the block: it carries the stamp of the source the block was built
     from, which validate/fr_writeufo.wls checks wherever the cache is used *)
  If[FileExistsQ[StringReplace[z9f, ".mx" ~~ EndOfString -> ".status"]],
    CopyFile[StringReplace[z9f, ".mx" ~~ EndOfString -> ".status"],
      FileNameJoin[{z9out, FileBaseName[z9f] <> ".status"}], OverwriteTarget -> True]];
  z9n++,
  {z9f, z9files}];
Print["[wxf] ", z9n, " of ", Length[z9files], " vertex lists converted to ", z9out];
