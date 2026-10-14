#!/bin/bash
# Selection counts for the processes quoted in the paper, from the CURRENT
# build/vertex_index.json (regenerate it after a cache change with ./dim8 index, which runs
# validate/dump_vertex_index.wls), with one insertion and with --two-insertions.
cd "$(dirname "$0")/.."
export DIM8_VDIR=${DIM8_VDIR:-$HOME/dim8auto_build/vertices}
echo "index blocks: $(python3 -c "import json;d=json.load(open('build/vertex_index.json'));print(len(d.get('blocks',d)))")"
printf "%-16s %8s %8s\n" process one-ins two-ins
for p in "p p > h j j" "p p > z h" "p p > w+ w-" "u u~ > w+ w-" "u u~ > z h" "u u~ > a h"; do
  a=$(./dim8 select "$p" 2>/dev/null | grep -cE "^ *Q_")
  b=$(./dim8 select --two-insertions "$p" 2>/dev/null | grep -cE "^ *Q_")
  printf "%-16s %8s %8s\n" "$p" "$a" "$b"
done
