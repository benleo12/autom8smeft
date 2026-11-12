# The Z width at successive orders

The leptonic width `Gamma(Z -> e+ e-)` of the paper's figure, at each order of the expansion from
`1/Lambda^2` to `1/Lambda^8`, with `models/dim68_mw_geo4` (the `{MW, MZ, GF}` scheme, its two- and
three-point vertices complete through dimension twelve) and its `poles` restriction card. Every
coefficient the card keeps is at 1 (`coefficients.txt`): those of dimension eight with `dim8_all`, and those
of dimensions six, ten and twelve by name, among them the four-lepton coefficients of muon decay (block
`GEOGF`). The card keeps every coefficient that enters this decay at tree level, which
`./dim8 select "z > e+ e-" --model dim68_mw_geo4 --with-dim6` lists through `1/Lambda^4`, and every
coefficient of dimensions ten and twelve.

There is a results file for each Lambda, `results_L<Lambda>.tsv` with its records in `records_L<Lambda>.tsv`,
and each has five rows, one an order:

| order | the term of the width |
|---|---|
| `NP=0` | the Standard Model |
| `NP^2==1` | `1/Lambda^2`, dimension six |
| `NP^2==2` | `1/Lambda^4`: dimension eight, and dimension six twice |
| `NP<=3 NP^2==3` | `1/Lambda^6`, every product of amplitudes at that order |
| `NP<=4 NP^2==4` | `1/Lambda^8`, the same |

The width truncated at order N is the sum of the rows through `NP^2==N`.  A decay is not integrated:
`run_study.sh` has MadGraph write the standalone matrix element of the row's order, evaluates it with
`examples/studies/decay_width.f` along three directions of the decay, and takes the tree-level width
`|M|^2 |p| / (8 pi M_Z^2)`, which is exact.  The columns `sigma_pb` and `error_pb` hold the width in GeV and 0,
`nevents` is `-`, and `lhe` names the program's printout, `lhe/<run>.width.txt`, from which
`provenance.py` computes the width again.  MadGraph's event generation is not used for a decay because the
error it quotes is that of the absolute value of the weights, which is the same at every point of a
two-body phase space: the `NP^2==1` term here, whose helicities enter with both signs, came out 25 per
cent high in its survey with a quoted error of 1e-8.  The rows are made by

    for L in 1000 1250 1500 2000 2500 3000 4000 5000 6000 8000 10000 12500 15000 20000; do
      DIM8_LAM=$L DIM8_RESULTS=results_L$L DIM8_ORDERS="NP=0;NP^2==1;NP^2==2;NP<=3 NP^2==3;NP<=4 NP^2==4" \
          examples/studies/run_study.sh examples/studies/zwidth models/dim68_mw_geo4
    done

in turn.  A row takes about 14 minutes and 7 GB, nearly all of it MadGraph reading the model, so the rows here
were run as 70 jobs at once, one a row in a study of its own, and merged with `merge_rows.py`.  The figure is

    examples/studies/width_figure.py paper/figs/zwidth.pdf examples/studies/zwidth/results_L*.tsv \
        --lines examples/studies/zwidth/precision.txt --ymin 1e-8 --title '$Z\to e^+e^-$'

It draws the contribution at each order, `|Gamma_N - Gamma_(N-1)|/Gamma_SM`, named by its order
`1/Lambda^(2N)`, against Lambda, with the relative precision on the width of LEP and the one we estimate
for FCC-ee as horizontal lines (`precision.txt`, which gives the sources and how the FCC-ee value is
obtained).  A contribution is relevant at a precision where its curve lies above that precision's line.  The script stops unless every row checks
out against its record and comes from the released model, and unless the term of order k times
`Lambda^(2k)` is the same at every Lambda to the ten digits the rows print.
