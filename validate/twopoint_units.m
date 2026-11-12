(* validate/twopoint_units.m  --  a function of a Lagrangian unit by unit, each unit computed once and kept.

   Usage, after LoadModel:   Get[$root <> "/validate/twopoint_units.m"];
                             z9r = z9units[tag, units, f]
   units is a list of {name, expression} or {name, Hold[expression], files}, f maps one expression to its result
   (the quadratic terms, or a list of them and the potential), and z9r is the sum of f over the units.  The second
   form is for a block, a Module of the model files that takes long to evaluate: it is evaluated only by the run
   that computes it, and it is known by its name and the files instead of its value.  The two-point checks of the models of
   order N (validate/check_bilinears_geo.wls, validate/check_fermion_masses_geo.wls) give f the blocks one by
   one and LSM summand by summand, z9splitSum["LSM", LSM]: f is linear, so the sum over the summands is f of
   the sum, and at order 4 the quadratic terms of LSM take 16618 s in one kernel, most of these checks.

   The result of each unit is saved as <dir>/<tag>_<name>_<hash>.mx.  The hash is that of the unit's expression
   (of a block, its name and the contents of the files), of the field definitions of the model, of the definitions
   of f and of validate/truncexp.m, so a result is read again only for the same input, and a changed base or block
   is computed afresh.  The dummy indices of Module (a$28215) are renamed in the order they appear before hashing,
   since their numbers differ between kernels.  DIM8_TWOPOINT_DIR sets <dir>
   (default $root/build/twopoint).  With DIM8_TWOPOINT_PREP=1 the run computes only the units that no other run
   has taken (a lock directory beside the file), and the caller quits after it: K such runs started at once share
   the units, and a run without it then reads them all and computes what is missing.  A run killed in the middle
   leaves its lock, which the run without DIM8_TWOPOINT_PREP ignores.

   Each line of z9say goes to DIM8_PROGRESS as well, when that is set, and the file is closed after the line:
   wolframscript buffers its output, and a run killed at its time limit loses whatever it printed.
*)
z9prog = Environment["DIM8_PROGRESS"];
(* a fraction as 1/2 on one line, not in the three lines of its OutputForm, so that the lines can be compared with grep *)
z9say[z9s__] := Module[{z9l = StringJoin[If[Head[#] === Rational, ToString[#, InputForm], ToString[#]] & /@ {z9s}], z9h},
  Print[z9l];
  If[StringQ[z9prog], z9h = OpenAppend[z9prog]; WriteString[z9h, DateString[{"Hour", ":", "Minute", ":", "Second"}], " ", z9l, "\n"]; Close[z9h]]];
z9splitSum[z9name_String, z9x_] := If[Head[z9x] === Plus, MapIndexed[{z9name <> "." <> ToString[First[#2]], #1} &, List @@ z9x], {{z9name, z9x}}];
z9unitDir = If[StringQ[Environment["DIM8_TWOPOINT_DIR"]], Environment["DIM8_TWOPOINT_DIR"], $root <> "/build/twopoint"];
z9prep = Environment["DIM8_TWOPOINT_PREP"] === "1";
(* an expression as text for the hash, with its dummy indices renamed in order of appearance: LSM holds
   about a thousand symbols of Module (a$28215, ...) whose numbers depend on what the kernel evaluated before,
   and differ by a few between two kernels, so that without the renaming no run reads another's units *)
z9dummy = RegularExpression["\\b[A-Za-z][A-Za-z0-9]*\\$[0-9]+\\b"];
z9text[z9x_] := Module[{z9s = ToString[InputForm[z9x]], z9d, z9m},
  z9d = DeleteDuplicates[StringCases[z9s, z9dummy]];
  z9m = AssociationThread[z9d, ("z9dummy" <> ToString[#]) & /@ Range[Length[z9d]]];
  StringReplace[z9s, z9dummy :> z9m["$0"]]];
z9srcHash[z9f_] := Hash[{ToString[InputForm[MR$Definitions]], z9text[z9f],
    Cases[{z9f}, z9s_Symbol /; Context[z9s] === "Global`" :> z9text[DownValues[z9s]], {0, Infinity}, Heads -> True],
    If[FileExistsQ[$root <> "/validate/truncexp.m"], FileHash[$root <> "/validate/truncexp.m", "SHA256"], 0]}, "SHA256", "HexString"];
z9units[z9tag_String, z9us_List, z9f_] := Module[{z9src = z9srcHash[z9f], z9out = {}, z9read = 0, z9made = 0, z9skip = 0},
  If[! DirectoryQ[z9unitDir], Quiet[CreateDirectory[z9unitDir]]];
  Do[Module[{z9name = z9u[[1]], z9key, z9val, z9file, z9lock, z9t, z9r},
     {z9key, z9val} = If[Length[z9u] === 3, {{z9name, FileHash[#, "SHA256"] & /@ z9u[[3]]}, z9u[[2]]},
       {z9text[z9u[[2]]], Hold[Evaluate[z9u[[2]]]]}];
     z9file = FileNameJoin[{z9unitDir, z9tag <> "_" <> z9name <> "_" <> StringTake[Hash[{z9src, z9key}, "SHA256", "HexString"], 16] <> ".mx"}];
     z9lock = z9file <> ".lock";
     Which[
       FileExistsQ[z9file], If[! z9prep, AppendTo[z9out, Import[z9file, "MX"]]]; z9read++,
       z9prep && Quiet[CreateDirectory[z9lock]] === $Failed, z9skip++,
       True,
         z9t = AbsoluteTiming[z9f[ReleaseHold[z9val]]]; z9r = z9t[[2]];
         (* through a file of this kernel's own, so that two runs that compute one unit never write one file *)
         Export[z9file <> ".tmp" <> ToString[$ProcessID], z9r, "MX"];
         Quiet[RenameFile[z9file <> ".tmp" <> ToString[$ProcessID], z9file, OverwriteTarget -> True]];
         If[z9prep, Quiet[DeleteDirectory[z9lock]]];
         If[! z9prep, AppendTo[z9out, z9r]]; z9made++;
         z9say["[units] ", z9tag, " ", z9name, ": ", Round[z9t[[1]]], " s"]]], {z9u, z9us}];
  z9say["[units] ", z9tag, ": ", Length[z9us], " units, ", z9made, " computed, ", z9read, " read", If[z9prep, ", " <> ToString[z9skip] <> " taken by other runs", ""]];
  If[z9prep, Null, Total[z9out]]];
