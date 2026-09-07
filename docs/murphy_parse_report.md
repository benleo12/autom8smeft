# Murphy table parse report

734 / 734 rows parsed into the DSL.

| table file | rows | parsed |
|---|---|---|
| dim8_classes_10_11_12_13_v2.tex | 41 | 41 |
| dim8_classes_14_v2.tex | 44 | 44 |
| dim8_classes_15.tex | 99 | 99 |
| dim8_classes_16_17.tex | 42 | 42 |
| dim8_classes_18_v6.tex | 73 | 73 |
| dim8_classes_19_v6.tex | 169 | 169 |
| dim8_classes_1_2_3_4.tex | 49 | 49 |
| dim8_classes_20.tex | 84 | 84 |
| dim8_classes_21_v3.tex | 45 | 45 |
| dim8_classes_5_6_7_8_v2.tex | 40 | 40 |
| dim8_classes_9.tex | 48 | 48 |

## Patches applied to the source (candidate errata)

* `Q_{l^2H^4D}^{(1)}`: missing \bar on first fermion (class 13 table)
  before: `$ i (l_p \gamma^{\mu} l_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
  after:  `$ i (\bar l_p \gamma^{\mu} l_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
* `Q_{l^2H^4D}^{(2)}`: missing \bar on first fermion (class 13 table)
  before: `$ i (l_p \gamma^{\mu} \tau^I l_r) [(H^{\dag} \overleftrightarrow{D}_{\mu}^I H) (H^{\dag} H) + (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} \tau^I H)]$`
  after:  `$ i (\bar l_p \gamma^{\mu} \tau^I l_r) [(H^{\dag} \overleftrightarrow{D}_{\mu}^I H) (H^{\dag} H) + (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} \tau^I H)]$`
* `Q_{l^2H^4D}^{(3)}`: missing \bar on first fermion (class 13 table)
  before: `$ i \epsilon^{IJK} (l_p \gamma^{\mu} \tau^I l_r) (H^{\dag} \overleftrightarrow{D}_{\mu}^J H) (H^{\dag} \tau^K H)$`
  after:  `$ i \epsilon^{IJK} (\bar l_p \gamma^{\mu} \tau^I l_r) (H^{\dag} \overleftrightarrow{D}_{\mu}^J H) (H^{\dag} \tau^K H)$`
* `Q_{l^2H^4D}^{(4)}`: missing \bar on first fermion (class 13 table)
  before: `$ \epsilon^{IJK} (l_p \gamma^{\mu} \tau^I l_r) (H^{\dag} \tau^J H) D_{\mu} (H^{\dag} \tau^K H)$`
  after:  `$ \epsilon^{IJK} (\bar l_p \gamma^{\mu} \tau^I l_r) (H^{\dag} \tau^J H) D_{\mu} (H^{\dag} \tau^K H)$`
* `Q_{e^2H^4D}`: missing \bar on first fermion (class 13 table)
  before: `$ i (e_p \gamma^{\mu} e_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
  after:  `$ i (\bar e_p \gamma^{\mu} e_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
* `Q_{q^2H^4D}^{(1)}`: missing \bar on first fermion (class 13 table)
  before: `$ i (q_p \gamma^{\mu} q_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
  after:  `$ i (\bar q_p \gamma^{\mu} q_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
* `Q_{q^2H^4D}^{(2)}`: missing \bar on first fermion (class 13 table)
  before: `$ i (q_p \gamma^{\mu} \tau^I q_r) [(H^{\dag} \overleftrightarrow{D}_{\mu}^I H) (H^{\dag} H) + (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} \tau^I H)]$`
  after:  `$ i (\bar q_p \gamma^{\mu} \tau^I q_r) [(H^{\dag} \overleftrightarrow{D}_{\mu}^I H) (H^{\dag} H) + (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} \tau^I H)]$`
* `Q_{q^2H^4D}^{(3)}`: missing \bar on first fermion (class 13 table)
  before: `$ i \epsilon^{IJK} (q_p \gamma^{\mu} \tau^I q_r) (H^{\dag} \overleftrightarrow{D}_{\mu}^J H) (H^{\dag} \tau^K H)$`
  after:  `$ i \epsilon^{IJK} (\bar q_p \gamma^{\mu} \tau^I q_r) (H^{\dag} \overleftrightarrow{D}_{\mu}^J H) (H^{\dag} \tau^K H)$`
* `Q_{q^2H^4D}^{(4)}`: missing \bar on first fermion (class 13 table)
  before: `$ \epsilon^{IJK} (q_p \gamma^{\mu} \tau^I q_r) (H^{\dag} \tau^J H) D_{\mu} (H^{\dag} \tau^K H)$`
  after:  `$ \epsilon^{IJK} (\bar q_p \gamma^{\mu} \tau^I q_r) (H^{\dag} \tau^J H) D_{\mu} (H^{\dag} \tau^K H)$`
* `Q_{u^2H^4D}`: missing \bar on first fermion (class 13 table)
  before: `$ i (u_p \gamma^{\mu} u_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
  after:  `$ i (\bar u_p \gamma^{\mu} u_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
* `Q_{d^2H^4D}`: missing \bar on first fermion (class 13 table)
  before: `$ i (d_p \gamma^{\mu} d_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
  after:  `$ i (\bar d_p \gamma^{\mu} d_r) (H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
* `Q_{udH^4D}`: missing \bar on first fermion (class 13 table)
  before: `$ i (u_p \gamma^{\mu} d_r) (\widetilde H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
  after:  `$ i (\bar u_p \gamma^{\mu} d_r) (\widetilde H^{\dag} \overleftrightarrow{D}_{\mu} H) (H^{\dag} H)$`
* `Q_{leq^2HD}^{(6)}`: gamma^nu should be gamma^mu (index mismatch)
  before: `$i (\bar q_p \gamma^\nu \tau^I q_r) [(\bar l_s D_\mu e_t) \tau^I H]$`
  after:  `$i (\bar q_p \gamma^\mu \tau^I q_r) [(\bar l_s D_\mu e_t) \tau^I H]$`
* `Q_{qud^2HD}^{(4)}`: stray $ before ]
  before: `$i (\bar d_p \gamma^\mu T^A u_r) [(\bar q_s T^A d_t)  D_\mu \widetilde H$]`
  after:  `$i (\bar d_p \gamma^\mu T^A u_r) [(\bar q_s T^A d_t)  D_\mu \widetilde H]`
* `Q_{qud^2HD}^{(6)}`: stray trailing backslash
  before: `$i (\bar d_p \gamma^\mu T^A d_r) [(D_\mu \bar q_s T^A u_t) \widetilde H]$ \`
  after:  `$i (\bar d_p \gamma^\mu T^A d_r) [(D_\mu \bar q_s T^A u_t) \widetilde H]$ `
* `Q_{lqd^2H^2}`: missing C in (l q) bilinear (class 18 table)
  before: `$\epsilon_{\alpha\beta\gamma} \epsilon_{jk} \epsilon_{mn} (l_p^j q_r^{m\alpha}) (d_s^\beta C d_t^\gamma) H^k H^n$`
  after:  `$\epsilon_{\alpha\beta\gamma} \epsilon_{jk} \epsilon_{mn} (l_p^j C q_r^{m\alpha}) (d_s^\beta C d_t^\gamma) H^k H^n$`
* `Q_{eq^2dH^2}`: missing C in (e d) bilinear (class 18 table)
  before: `$\epsilon_{\alpha\beta\gamma} \epsilon_{jk} \epsilon_{mn} (e_p d_r^\alpha) (q_s^{j\beta} C q_t^{m\gamma}) H^k H^n$`
  after:  `$\epsilon_{\alpha\beta\gamma} \epsilon_{jk} \epsilon_{mn} (e_p C d_r^\alpha) (q_s^{j\beta} C q_t^{m\gamma}) H^k H^n$`

## Derived conjugacy vs the published "+ h.c." marks (V5, DSL half)

| Murphy marks + h.c. | derived | rows | emitted as |
|---|---|---|---|
| False | antihermitian | 68 | C (i Q), C real, factor i restored |
| False | complex | 14 | (C/2)(Q + h.c.), C real |
| False | hermitian | 356 | C Q, C real |
| True | complex | 296 | C Q + h.c., C complex |

The 68 anti-Hermitian rows carry a bare `\overleftrightarrow{D}`; Murphy's
definition (conventions_v2.tex:87) puts the factor $i$ outside that symbol, so the
rows are anti-Hermitian exactly as typeset and the $i$ is restored automatically.

The 14 rows below are Hermitian only up to integration by parts, and are
not marked `+ h.c.` in the source.  A Lagrangian density must be Hermitian, so they
are emitted as the Hermitian part $(C/2)(Q + Q^\dagger)$ with $C$ real, which
coincides with $C Q$ whenever $Q$ is Hermitian:

* `Q_{l^2H^2D^3}^{(1)}` (class 11)
* `Q_{l^2H^2D^3}^{(2)}` (class 11)
* `Q_{l^2H^2D^3}^{(3)}` (class 11)
* `Q_{l^2H^2D^3}^{(4)}` (class 11)
* `Q_{e^2H^2D^3}^{(1)}` (class 11)
* `Q_{e^2H^2D^3}^{(2)}` (class 11)
* `Q_{q^2H^2D^3}^{(1)}` (class 11)
* `Q_{q^2H^2D^3}^{(2)}` (class 11)
* `Q_{q^2H^2D^3}^{(3)}` (class 11)
* `Q_{q^2H^2D^3}^{(4)}` (class 11)
* `Q_{u^2H^2D^3}^{(1)}` (class 11)
* `Q_{u^2H^2D^3}^{(2)}` (class 11)
* `Q_{d^2H^2D^3}^{(1)}` (class 11)
* `Q_{d^2H^2D^3}^{(2)}` (class 11)

## Failures

