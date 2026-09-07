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
z8base = If[Environment["DIM8_BASE"] === $Failed, "base.fr", Environment["DIM8_BASE"]];
LoadModel[z8base, "gen.fr"];
Print["[time] LoadModel: ", Round[AbsoluteTime[] - t0, 0.1], " s"];

vdir = If[Environment["DIM8_VDIR"] === $Failed, $root <> "/build/vertices", Environment["DIM8_VDIR"]];
Print["[cfg] base ", z8base, "  cache ", vdir, "  FeynmanGauge ", FeynmanGauge];
files = FileNames["*.mx", vdir];
If[selfile =!= "",
  Module[{want = Select[StringTrim /@ StringSplit[Import[selfile, "Text"], "\n"], # =!= "" &]},
    files = Select[files, MemberQ[want, FileBaseName[#]] &];
    Print["[sel] ", Length[want], " blocks requested, ", Length[files], " found in the cache"];
    If[Length[files] < Length[want], Print["[abort] requested blocks missing from the cache"]; Quit[1]]];
];
Print["[load] ", Length[files], " cached vertex lists"];

(* SM plus the dimension-six sector are cheap, compute them here *)
tt = AbsoluteTime[];
smVerts = FeynmanRules[LSM, ScreenOutput -> False];
Print["[time] LSM vertices: ", Length[smVerts], " (", Round[AbsoluteTime[] - tt, 0.1], " s)"];

all = {smVerts};
Do[
  Module[{},
    Get[z8file];                       (* restores FR$Vert *)
    AppendTo[all, FR$Vert];
    ClearAll[FR$Vert];
  ], {z8file, files}];
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
WriteUFO[Input -> merged, Output -> outname, AddDecays -> False, Optimization -> False];
Print["[ufo] ", outname, " written in ", Round[AbsoluteTime[] - tt, 0.1], " s"];
Print["[alldone] total ", Round[AbsoluteTime[] - t0, 0.1], " s"];
