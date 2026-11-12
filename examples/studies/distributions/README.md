# Distribution samples

The event samples behind the two distribution figures of the paper: `p p > w+ w-` and the
electroweak `p p > h h j j`, at 13.6 TeV with `models/dim8_mw`, every coefficient of a class at 1
and Lam at 3 TeV. Each row holds 10^5 events. The rows are the Standard Model (`NP=0`), the
interference (`NP^2==2`) of each class a figure shows, and the square (`NP<=2 NP^2==4`) of the one
class whose square it draws:

| process | Standard Model | interference | square |
|---|---|---|---|
| `p p > w+ w-` | full model | `cls14`, `cls6`, `cls13`, `cls15` | `cls14` |
| `p p > h h j j QCD=0` | `bosonic` card | `cls4`, `cls6`, `cls7`, `cls15` | `cls7` |

The cross-section tables use the runs of `../diboson` and `../vbf_dihiggs`, 5000 events for an
interference and 1000 for a square. These runs are separate and larger because a figure bins the
pair mass up to about 2.4 TeV, where a Standard-Model bin of a 5000-event sample holds a handful of
events. The HHjj rows use the cuts and the `bosonic` card of `../vbf_dihiggs`.

Each row was run on its own, one study directory a row, and merged here with `merge_rows.py`,
which carries the row's record and cards. An interference row is

    DIM8_SKIP_FULL=1 DIM8_CLASS_ORDERS="NP^2==2" \
        examples/studies/run_study.sh <dir> models/dim8_mw 100000

with `classes.txt` naming the class, a square row the same with `DIM8_CLASS_ORDERS="NP<=2 NP^2==4"`
and `DIM8_NEV_SQ=100000`, and a Standard-Model row `DIM8_ORDERS="NP=0"` with an empty `classes.txt`.
Every row has its record in `records.tsv`, which `provenance.py check results.tsv` reads.

The distributions are written by `plot_study.py` from the event files in `lhe/`, with the SM row
first, each interference row, and the square labelled `<class> squared`, for example

    examples/studies/plot_study.py ww_classes SM=lhe/p_p___wp_wm_dim8_mw_NP_0.lhe.gz \
        'psi2X2D=lhe/p_p___wp_wm_dim8_mwmcls14_NP_2__2.lhe.gz' \
        'psi2X2D squared=lhe/p_p___wp_wm_dim8_mwmcls14_NP__2_NP_2__4.lhe.gz'

and `paper_figure.py` draws the figure from the table it writes, with `--errors` for the band of
one standard deviation of the Monte Carlo error.
