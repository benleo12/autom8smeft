# Lambda power counting extract (Assi and Martin papers)

Source files read in full:

- `${DIM8_ROOT:-.}/docs/lambda_counting_paper.tex`  (Assi, Martin, "Energy-Enhanced Expansion of the Standard Model Effective Field Theory", PRD style, cited elsewhere as the lambda counting paper; referred to below as **LC**)
- `${DIM8_ROOT:-.}/docs/geosmeft_vbf_paper.tex`  (Assi, Martin, "Energy-Enhanced Dimension Eight SMEFT Effects in VBF Higgs production", JHEP style, BibTeX key `Assi:2024zap`; referred to below as **VBF**)
- Cross-checked against `${DIM8_ROOT:-.}/murphy_src/sections/{operator_classification_v5,results_v5,dim8_classes_10_11_12_13_v2,dim8_classes_15,dim8_classes_18_v6}.tex` for Murphy labels, and against `${DIM8_ROOT:-.}/prior_work/hand_typed/dim8_geosmeftVBF.fr` for the FeynRules coefficient names.
- BibTeX: `${DIM8_ROOT:-.}/paper/ref.bib`

Everything in Sections 1 to 4 is transcribed from the sources. Anything I derived myself is labelled **[derived]**. Discrepancies and ambiguities are collected in Section 6 and are not resolved here.

---

## 1. The lambda power counting algorithm (LC, Sec. II "Energy Expansion")

### 1.1 Setup

SMEFT Lagrangian (LC eq. `SMEFT_Lagrangian`):

```latex
\mathcal{L}_\text{SMEFT} = \mathcal{L}_\text{SM} + \sum_{i, j} \frac{c_j^{(i)}}{\Lambda^{i}} \mathcal{O}_j^{(4+i)}
```

Baseline assumption (verbatim): "we assume that $c_j^{(i)}/\Lambda^{i}$ are all of comparable magnitude, an assumption that reflects a weakly coupled new physics scenario." If a UV scenario generates hierarchies (strong couplings, $1/16\pi^2$ loop factors, symmetry zeros) "one simply multiplies the $\lambda$ weight of each affected vertex by the corresponding hierarchy factor."

Vertex-multiplicity decomposition (LC eq. `SMEFT_n_point`):

```latex
\mathcal{L}_\text{SMEFT}^{(n)} = \sum_j g_\text{SM}^j \lambda_j^{(n)} \mathcal{O}_\text{SM}^j + \sum_{i,k} c_k^{(i)} \frac{\lambda_k^{(n)}}{\Lambda^{i}} \mathcal{O}_k^{(4+i)}
```

"each component $\mathcal{L}_\text{SMEFT}^{(n)}$ contains interactions involving $n$ external legs." $\lambda^{(n)} \ne \lambda^{(n')}$ in general.

### 1.2 Scaling conditions (LC eq. `scaling_conditions`)

```latex
(\Lambda, E, v) \sim
\begin{cases}
(\lambda^{-3}, \lambda^{-2}, \lambda^{-1}) & \text{if } \Lambda \gg E \gg v, \\
(\lambda^{-3}, \lambda^{-1}, \lambda^{-1}) & \text{if } \Lambda \gg E \sim v,
\end{cases}
```

"for a dimensionless power counting parameter $\lambda\ll 1$ that is set by the field and derivative content of $\mathcal{O}$". Since the size of $\Lambda$ is accounted for, "one can take it to be of order one" in the $n$-point Lagrangian.

### 1.3 Dimension bookkeeping (LC eqs. `dimension_relation`, `operator_dimension`)

An on-shell $n$-point vertex has mass dimension $d = 4 - n$.

```latex
\left[\frac{E^q v^p}{\Lambda^D}\right] = q + p - D = d
```

```latex
D = \frac{3}{2} N_f + N_H + 2 N_X + N_D - 4
```

with $N_f$ = number of fermions, $N_H$ = number of Higgs bosons, $N_X$ = number of external bosons (field strengths), $N_D$ = number of covariant derivatives. ($D$ is the operator dimension minus 4, so $D=2$ at dim-6, $D=4$ at dim-8, $D=6$ at dim-10.)

### 1.4 Tree-level reachability condition (verbatim)

"given that the operator is able to generate at tree level the $n$-point vertex, meaning $N_f+N_X\leq n\leq 2N_f+N_X+N_D+N_H$"

(See Section 6, item Q4: as literally written this inequality excludes $X^4$ at $n=5,6$ and $H^2X^3$ at $n=6$, which nevertheless appear in the LC tables.)

### 1.5 Leading vertex: $p_{\rm min}$ and $q_{\rm max}$ (LC eqs. `power_v`, `power_E`)

```latex
p_{\rm min} = \max[N_f + N_X + N_H - n, 0]
```

```latex
q_{\rm max} = D + d - p_{\rm min}
```

### 1.6 Subleading vertices: $k$ and $k_{\rm max}$ (LC eq. `subleading_pq` and the unlabelled $k_{\max}$ equation)

```latex
p_k = p_{\rm min} + k, \quad q_k = q_{\rm max} - k
```

with $k \in \lbrace 0,1,\ldots,\min[k_{\rm max},q_{\rm max}]\rbrace$, where $k_{\rm max}$ "is only non-zero when $N_H>0$ and is given by"

```latex
k_{\text{max}} = N_H - \max\left[n - N_f - 2N_X - N_D,\; 0\right]
```

Vertex scaling including subleading terms:

```latex
\mathcal{V}_k^{(n)} \sim \frac{E^{q_k} v^{p_k}}{\Lambda^D}, \qquad p_k + q_k = D + d
```

$k=0$ is the leading contribution (maximal $E$ power, minimal $v$ power). $k>0$ replaces powers of $E$ by $v$ (Higgs field appearing as vev rather than physical $h$).

### 1.7 The lambda weight (LC, unlabelled equation following `subleading_pq`)

Defined in the regime $\Lambda \gg E \gg v$ using the first line of the scaling conditions:

```latex
\lambda_j^{(n)}=\lambda^{3D-2q_{\rm max}-p_{\rm min}}
```

"$(n)$ indicates the number of legs and $j$ labels the SMEFT operator it multiplies and $D$ is the mass dimension of said operator."

**[derived]** Substituting $q_{\max}=D+d-p_{\min}$ with $d=4-n$ gives $\lambda^{(n)} = \lambda^{\,D + 2n - 8 + p_{\min}}$. At dim-8 ($D=4$): $\lambda^{4+p_{\min}}$ for $n=4$, $\lambda^{6+p_{\min}}$ for $n=5$, $\lambda^{8+p_{\min}}$ for $n=6$. So the "leading" classes in each LC table are exactly those with $p_{\min}=0$, i.e. $N_f+N_X+N_H \le n$. I checked this numerically for all 21 dim-8 classes at $n=4,5,6$ and it reproduces the class membership of LC Tables IV, V, VI exactly (7, 14 and 19 classes respectively).

**[derived]** Additional counting conventions implicit in the LC tables (needed to reproduce the "Vertices" column): a fermion bilinear $\psi^2$ counts as one power of $E$ (each external spinor $\sim\sqrt{E}\sim\lambda^{-1}$, stated explicitly in LC Sec. V.A), each derivative $\partial$ counts as one $E$, a gauge field obtained from $D_\mu H \to g v V_\mu$ costs one $v$, and a field strength $X_{\mu\nu}$ gives $\partial V$ (one $E$) or, non-abelian, $V^2$.

### 1.8 Amplitude assembly rules used in the examples (LC Sec. V)

- SM 3-point couplings carry inverse powers: $g^{\rm SM}_{\bar q q V}/\lambda^2$ (two external spinors, $\sqrt{E}\sim\lambda^{-1}$ each) and $g^{\rm SM}_{hVV}/\lambda$ (proportional to $v$).
- Every propagator scales as $E^{-2}\sim\lambda^4$ (footnote: "the $\lambda$ counting treats $n$-particle vertices as amplitudes which should be glued together to make larger amplitudes" citing `Elvang:2013cua`).
- $\hat\Lambda$ is a pure bookkeeping device: $c^{(i)}_j \to c_j/\hat\Lambda^i$.
- Sub-leading vertices ($k>0$) that are not shown in the tables can be the leading contribution once glued into an amplitude (explicitly used in the VH example).

### 1.9 Stated caveats (verbatim or near verbatim)

1. **Minimal Warsaw-like basis required.** "to establish a consistent counting algorithm it is crucial to work in a minimal Warsaw-like basis. Our counting scheme treats each derivative as potentially contributing an energy factor. Given this limitation, eliminating redundant derivatives (those removable by integration by parts or via equations of motion) is essential to prevent an artificial boost in the counted energy scaling."
2. **Only $n \ge 4$ is robust.** "our counting method is only robust for $n \ge 4$ because the extra independent kinematic degrees of freedom guarantee that energy enhancements appear as expected, whereas for $n < 4$ the tight kinematic constraints limit the validity of an $E/\Lambda$ expansion. For 2- and 3-point vertices, we explicitly correct for these limitations, ensuring that the energy scaling tables (see Tables II and III) can be used without concern."
3. **2- and 3-point vertices are handled by geoSMEFT.** "For 2 and 3-particle vertices, the energy classification can be read off immediately thanks to the geometric SMEFT organization ... the $E$ scaling is fixed by the lowest-dimension operator that contains the vertex, with even higher-dimensional operators only contributing factors of $v$." Example: $(H^\dag H)X_{\mu\nu}X^{\mu\nu}$ gives $hVV\sim\lambda = vE/\Lambda^2$; at dim 8 and higher the only option is $(H^\dag H)^n X_{\mu\nu}X^{\mu\nu}$, scaling as the dim-6 value times $(v^2/\Lambda^2)^{n-1}$.
4. **Weak coupling, no hierarchies.** All $c_i/\Lambda$ comparable apart from the standard loop suppression.
5. **On-shell counting.** "our power counting is based on on-shell conditions, so vertices that vanish by the equations of motion are not properly ordered within this scheme."
6. **Leading order in $\lambda$ only.** Sub-leading corrections may matter; "the $\lambda$ counting we advocate for is a guide; large numerical or coupling prefactors that appear in explicit calculations can override it, so final priorities on what orders in $\lambda$ to keep should be set after computing the full amplitude."
7. **Helicity-blind weights.** "the $\lambda$ weights are helicity-blind since no assumption is made about whether the vertex leg ends up external or internal; once external $V_L$ or $V_T$ polarisations are fixed for a specific process, one should retain the operator structures that couple to those helicities."
8. **Tree/loop labels only through dim-8.** Tree vs loop classification follows `Craig:2019wmo` (with its assumptions, e.g. neglecting couplings of three heavy fields to one light field); the LC tables carry no tree/loop labels at dim-10.
9. **Illustrative removals.** Setting constrained or non-interfering operators to zero (rather than suppressing them) is a simplification; "a more complete phenomenological analysis would need to account for additional effects from flavor structure, loop-level matching, and off-shell dynamics."

### 1.10 Table coding scheme (LC Sec. III)

- plain: tree-level origin
- bold (`\looponly`): generated only at loop level
- underlined (`\mixedchirality`): mixed chirality (e.g. $e_c L$, $u_c Q$), suppressed under flavor universality / MFV
- bold and underlined (`\bothfeatures`): both loop-only and mixed chirality

(In the commented-out colour version of the macros these were black, dark orange, navy blue, and dark purple respectively. The phrase "operators shaded in purple" in LC Sec. V.A therefore means the `\bothfeatures` class.)

---

## 2. Dimension-8 rows of the LC energy scaling tables

Notation: "Vertices" lists field content of each vertex and its $E^q v^p$ scaling (overall $1/\Lambda^4$ suppressed). The first vertex in each cell is the leading ($k=0$) one. Coding column: T = tree (plain), L = loop-only (bold), M = mixed chirality (underlined), L+M = both. Entries in the source wrapped in `\textcolor{black}{...}` are typeset plain and are therefore tree-level; I mark them "T (explicit black)".

### 2.1 Two-point vertices, dim-8 (LC Table II, `tab:2pt_scaling_compact`)

| Class | Coding | $\lambda^{(2)}$ | Vertices |
|---|---|---|---|
| $H^8$ | T | $\lambda^8$ | $h^2: v^4$ |
| $H^6D^2$ | T | $\lambda^8$ | $(\partial h)^2: v^4$ |
| $H^4X^2$ | T | $\lambda^8$ | $h^2: v^4$ |
| $\psi^2H^5$ | M | $\lambda^8$ | $\psi^2: v^4$ |

Caption: "no new $E$ powers, all just dimension six scaling times powers of $v^2/\Lambda^2$."

### 2.2 Three-point vertices, dim-8 (LC Table III, `tab:3pt_scaling`)

| Class | Coding | $\lambda^{(3)}$ | Vertices |
|---|---|---|---|
| $H^8$ | T | $\lambda^7$ | $h^3: v^5$ |
| $H^6D^2$ | T | $\lambda^7$ | $hVV: v^5$ |
| $H^2X^3$ | L | $\lambda^4$ | $VVV: v^2E^3$ |
| $H^4X^2$ | T | $\lambda^5$ | $hVV: v^3E^2$ |
| $H^4XD^2$ | T | $\lambda^5$ | $hVV: v^3E^2$ |
| $\psi^2H^3X$ | M | $\lambda^5$ | $\psi^2V: v^3E^2$ |
| $\psi^2H^5$ | M | $\lambda^6$ | $h\psi^2: v^4E$ |
| $\psi^2H^4D$ | T | $\lambda^5$ | $(\partial h)\psi^2: v^3E^2$ |

Caption: "the energy scaling for a given vertex is fixed, so higher dimensional operators only introduce additional powers of $v$."

### 2.3 Four-point vertices, dim-8 (LC Table IV, `tab:4pt_scaling_replaced`)

Only classes generating the leading power of $\lambda$ at this dimension are shown in the source.

| Class | Coding | $\lambda^{(4)}$ | $(q,p)$ leading | Vertices (verbatim) |
|---|---|---|---|---|
| $X^4$ | L | $\lambda^4$ | (4,0) | $V^4: E^4$ |
| $H^4D^4$ | T | $\lambda^4$ | (4,0) | $(\partial h)^4: E^4,\; h^3V: E^3v,\; h^2V^2: E^2v^2,\; hV^3: Ev^3$ |
| $H^2X^2D^2$ | L | $\lambda^4$ | (4,0) | $(\partial h)^2V^2: E^4,\; (\partial h)V^3: E^3v,\; V^4: E^2v^2$ |
| $\psi^2H^2D^3$ | T | $\lambda^4$ | (4,0) | $\psi^2(\partial h)^2: E^4,\; \psi^2(\partial h)V: E^3v,\; \psi^2V^2: E^2v^2$ |
| $\psi^2X^2D$ | L | $\lambda^4$ | (4,0) | $\psi^2(\partial^2V)(\partial V): E^4$ |
| $\psi^2HXD^2$ | L+M | $\lambda^4$ | (4,0) | $\psi^2(\partial h)(\partial V): E^4,\; \psi^2(\partial V)^2: E^3v$ |
| $\psi^4D^2$ | T | $\lambda^4$ | (4,0) | $\psi^2(\partial\psi)^2: E^4$ |

Caption: "Unlike in the previous table, the energy dependence for 4-point vertices can increase as we consider higher and higher dimensional operators. For example, the $V^4$ vertex $\sim E^2$ at dimension six, but grows to $\sim E^4$ at dimension eight and $\sim E^6$ at dimension ten."

For reference, the dim-6 rows of the same table (all $\lambda^2$): $H^4D^2$ (T): $(\partial h)^2h^2: E^2,\ h^3V: vE,\ h^2V^2: v^2$. $H^2X^2$ (L): $h^2V^2: E^2,\ hV^3: vE,\ V^4: v^2$. $X^3$ (L): $V^4: E^2$. $\psi^2HX$ (L+M): $\psi^2V^2: vE,\ \psi^2h\partial V: E^2$. $\psi^2H^2D$ (T): $\psi^2Vh: vE,\ \psi^2h\partial h: E^2$. $\psi^4$ (T): $\psi^4: E^2$.

**[derived]** Dim-8 classes absent from LC Table IV, with their 4-point weight from the algorithm ($\lambda^{4+p_{\min}}$): $H^2X^3$, $H^4XD^2$, $\psi^2X^2H$, $\psi^2XH^2D$, $\psi^2H^3D^2$, $\psi^4X$, $\psi^4HD$ all $\lambda^5$ ($p_{\min}=1$); $H^6D^2$, $H^4X^2$, $\psi^2XH^3$, $\psi^2H^4D$, $\psi^4H^2$ all $\lambda^6$ ($p_{\min}=2$); $\psi^2H^5$ $\lambda^7$; $H^8$ $\lambda^8$. LC itself uses $\lambda^5$ for the $\psi^2H^2XD$ 4-point vertex in the $t\bar tH$ example, consistent with this.

### 2.4 Five-point vertices, dim-8 (LC Table V, `tab:5pt_scaling_replaced`)

| Class | Coding | $\lambda^{(5)}$ | $(q,p)$ leading | Vertices (verbatim) |
|---|---|---|---|---|
| $X^4$ | L | $\lambda^6$ | (3,0) | $(\partial V)^3V^2: E^3$ |
| $H^4D^4$ | T | $\lambda^6$ | (3,0) | $(\partial h)^3hV: E^3,\; (\partial h)^2hV^3: E^2v,\; (\partial h)hV^3: Ev^2,\; hV^4: v^3$ |
| $H^2X^3$ | L | $\lambda^6$ | (3,0) | $h^2(\partial V)^3: E^3,\; h(\partial V)^2V^2: E^2v,\; (\partial V)V^4: Ev^2$ |
| $H^2X^2D^2$ | L | $\lambda^6$ | (3,0) | $(\partial h)^2(\partial V)V^2: E^3,\; (\partial h)(\partial V)^2V^2: E^2v,\; (\partial V)^3V^2: Ev^2$ |
| $H^4XD^2$ | T | $\lambda^6$ | (3,0) | $(\partial h)^2(\partial V)h^2: E^3,\; (\partial h)^2hV^2: E^2v,\; (\partial h)hV^3: Ev^2,\; (\partial h)V^4: v^3$ |
| $\psi^2HX^2$ | L+M | $\lambda^6$ | (3,0) | $\psi^2h(\partial V)^2: E^3,\; \psi^2(\partial V)V^2: E^2v$ |
| $\psi^2H^2D^3$ | T | $\lambda^6$ | (3,0) | $\psi^2(\partial h)^2V: E^3,\; \psi^2(\partial h)V^2: E^2v,\; \psi^2V^3: Ev^2$ |
| $\psi^2H^2XD$ | T | $\lambda^6$ | (3,0) | $\psi^2(\partial h)(\partial V)h: E^3,\; \psi^2(\partial h)V^2: E^2v,\; \psi^2V^3: Ev^2$ |
| $\psi^2X^2D$ | L | $\lambda^6$ | (3,0) | $\psi^2(\partial V)^2V: E^3$ |
| $\psi^2HXD^2$ | L+M | $\lambda^6$ | (3,0) | $\psi^2(\partial h)(\partial V): E^3,\; \psi^2(\partial V)^2: E^2v$ |
| $\psi^2H^3D^2$ | M | $\lambda^6$ | (3,0) | $\psi^2(\partial h)^3: E^3,\; \psi^2(\partial h)^2V: E^2v,\; \psi^2(\partial h)V^2: Ev^2$ |
| $\psi^4D^2$ | T | $\lambda^6$ | (3,0) | $\psi^3(\partial\psi)V: E^3$ |
| $\psi^4X$ | T | $\lambda^6$ | (3,0) | $\psi^4(\partial V): E^3$ |
| $\psi^4HD$ | M | $\lambda^6$ | (3,0) | $\psi^4(\partial h): E^3,\; \psi^4V: E^2v$ |

Caption: "We only display operator classes with leading powers in $\lambda$, the remainder are subleading."

**[derived]** Classes absent from Table V: $H^6D^2$, $H^4X^2$, $\psi^2XH^3$, $\psi^2H^4D$, $\psi^4H^2$ at $\lambda^7$; $\psi^2H^5$ at $\lambda^8$; $H^8$ at $\lambda^9$.

### 2.5 Six-point vertices, dim-8 (LC Table VI, `tab:6pt_scaling_replaced`)

| Class | Coding | $\lambda^{(6)}$ | $(q,p)$ leading | Vertices (verbatim) |
|---|---|---|---|---|
| $X^4$ | L | $\lambda^8$ | (2,0) | $(\partial V)^2V^4: E^2$ |
| $H^6D^2$ | T | $\lambda^8$ | (2,0) | $(\partial h)^2h^4: E^2,\; (\partial h)h^4V: Ev,\; h^4V^2: v^2$ |
| $H^4D^4$ | T | $\lambda^8$ | (2,0) | $(\partial h)^2h^2V^2: E^2,\; (\partial h)h^3V^3: Ev,\; h^2V^4: v^2$ |
| $H^2X^3$ | L | $\lambda^8$ | (2,0) | $(\partial V)^2h^2V^2: E^2,\; (\partial V)hV^4: Ev,\; V^6: v^2$ |
| $H^4X^2$ | T (explicit black) | $\lambda^8$ | (2,0) | $(\partial V)^2h^4: E^2,\; (\partial V)V^2h^3: Ev,\; V^4h^2: v^2$ |
| $H^2X^2D^2$ | L | $\lambda^8$ | (2,0) | $h^2(\partial^2V)V^3: E^2,\; h(\partial V)V^4: Ev,\; V^6: v^2$ |
| $H^4XD^2$ | T | $\lambda^8$ | (2,0) | $h^4(\partial V)^2: E^2,\; h^3(\partial V)V^2: Ev,\; h^2V^4: v^2$ |
| $\psi^2HX^2$ | L+M | $\lambda^8$ | (2,0) | $\psi^2h(\partial V)V^2: E^2,\; \psi^2V^4: Ev$ |
| $\psi^2X^2D$ | L | $\lambda^8$ | (2,0) | $\psi^2(\partial V)V^3: E^2$ |
| $\psi^2H^3X$ | M | $\lambda^8$ | (2,0) | $\psi^2h^3(\partial V): E^2,\; \psi^2h^2V^2: Ev$ |
| $\psi^2H^2D^3$ | T | $\lambda^8$ | (2,0) | $\psi^2h(\partial V)V^2: E^2,\; \psi^2V^4: Ev$ |
| $\psi^2H^4D$ | T | $\lambda^8$ | (2,0) | $\psi^2h^3(\partial h): E^2,\; \psi^2h^3V: Ev$ |
| $\psi^2H^2XD$ | T | $\lambda^8$ | (2,0) | $\psi^2h^2(\partial V)V: E^2,\; \psi^2hV^3: Ev$ |
| $\psi^2HXD^2$ | L+M | $\lambda^8$ | (2,0) | $\psi^2h(\partial V)V^3: E^2,\; \psi^2V^4: Ev$ |
| $\psi^2H^3D^2$ | M | $\lambda^8$ | (2,0) | $\psi^2h^3(\partial V): E^2,\; \psi^2h^2V^2: Ev$ |
| $\psi^4H^2$ | T | $\lambda^8$ | (2,0) | $\psi^4h^2: E^2$ |
| $\psi^4D^2$ | T | $\lambda^8$ | (2,0) | $\psi^4V^2: E^2$ |
| $\psi^4X$ | T | $\lambda^8$ | (2,0) | $\psi^4V^2: E^2$ |
| $\psi^4HD$ | M | $\lambda^8$ | (2,0) | $\psi^4hV: E^2$ |

Caption: shown "up to dimension 8 in this case since the leading 6-point dimension 10 scaling is highly subleading in $\lambda^{10}$."

**[derived]** Absent: $\psi^2H^5$ at $\lambda^9$, $H^8$ at $\lambda^{10}$.

### 2.6 LC Table I (`fig:geo_org`): dim-8 operator counts by minimum vertex multiplicity

| Min. vertex | Classes and counts | Total |
|---|---|---|
| 2-point | $H^8$: 1, $H^6D^2$: 2, $H^4X^2$: 10, $\psi^2H^5$: 6 | 19 |
| 3-point | $H^2X^3$: 6, $XH^4D^2$: 6, $\psi^2H^3X$: 22, $\psi^2H^4D$: 13 | 47 |
| 4-point | $H^4D^4$: 3, $X^4$: 43, $H^2X^2D^2$: 18, $\psi^2HX^2$: 96, $\psi^2H^2D^3$: 16, $\psi^2X^2D$: 57, $\psi^2H^2XD$: 92, $\psi^2HXD^2$: 48, $\psi^2H^3D^2$: 36, $\psi^4H^2$: 96, $\psi^4HD$: 168, $\psi^4D^2$: 67 | 740 |
| 5-point | $\psi^4X$: 224 | 224 |
| All | | 1030 |

**[derived]** These are Murphy's $N_{\rm term}$ counts per class including both the baryon-number-violating terms and the "+37" terms that vanish without flavor structure ($\psi^4H^2$: 75+1+12+8 = 96, $\psi^4HD$: 134+2+32 = 168, $\psi^4D^2$: 55+10+2 = 67, $\psi^4X$: 156+12+44+12 = 224). 1030 = 993 + 37. Caption: geoSMEFT fully re-sums the 2- and 3-point operators (66 of them) but "for higher point vertices geoSMEFT re-sums only a small portion which happen not to be energy-enhanced."

---

## 3. Energy-enhanced dim-8 operators for VBF and VH

### 3.1 VBF ($pp \to Hjj$), from the VBF paper

**Scaling argument (VBF eq. `ecounting`, `coeffhierarchy`).** For $2\to3$ amplitudes (mass dimension $-1$):

```latex
\mathcal A_{\rm SM} \sim g^3_{\rm SM}\frac{v}{E^2},\quad
\mathcal A_{Hq}, \mathcal A_{Hu,d} \sim g_{\rm SM} ^2\frac{c_6\, v}{\Lambda^2},\quad
\mathcal A_{q^2H^2XD}, \mathcal A_{q^2H^2D^3} \sim g_{\rm SM} ^2\frac{c_8\, v\, E^2}{\Lambda^4},\quad
\mathcal A_{q^4H^2} \sim \frac{c_8\, v\, E^2}{\Lambda^4}
```

```latex
\frac{\mathcal{A}^*_{\rm SM}\mathcal{A}_8}{\mathcal{A}^*_{\rm SM}\mathcal{A}_6} \sim \Big(\frac{c_8}{c_6}\Big)\Big(\frac{E^2}{\Lambda^2} \Big).
```

$2\to2$ subprocess $qV\to q'H$ (VBF Sec. 4): $A_{\rm SM}\sim v/E$, $A_{\rm dim\text{-}6}\sim vE/\Lambda^2$, $A_{\rm dim\text{-}8}\sim vE^3/\Lambda^4$; an extra $1/E$ (quark current $E$ times propagator $1/E^2$) converts to the full VBF scaling. Longitudinal-$V$ limit, $\hat t\gg m^2_{Z,H}$ (VBF eq. `2to2largeT`):

```latex
{\cal A}(qZ_{L,\mu}\rightarrow q H) = -i\bra{\bar q}\slashed p_H |q] \frac{1}{\hat t}\Big (g_{Zq_Lq_L}g^{(1)}_{HZZ} + g^{(1)}_{ZHq_Lq_L} \frac{\hat t }{\Lambda^2} + (g^{(2)}_{ZHq_Lq_L} - g^{(3)}_{ZHq_Lq_L}) \frac{\hat t^2 }{2\Lambda^4}\Big)
```

and for $W$ (VBF eq. `2to2largeTa`), which has the extra $\hat s\hat t$ term:

```latex
{\cal A}(qW_{L,\mu}\rightarrow {q}' H) = -i\bra{\bar q}\slashed p_H |q] \frac{1}{\hat t}\Big (g_{Wq_Lq'_L}g^{(1)}_{HWW} + g^{(1)}_{WHq_Lq'_L} \frac{\hat t }{\Lambda^2} + (g^{(2)}_{WHq_Lq'_L} - g^{(4)}_{WHq_Lq'_L} ) \frac{\hat t^2 }{2\Lambda^4} - g^{(3)}_{WHq_Lq'_L}  \frac{\hat t\,(2\hat s + \hat t) }{2\Lambda^4}  \Big)
```

Effective-$W$ results (VBF eqs. `effW_dim6`, `effW_dim8`): for $W_L$, $\int d\theta^* 2{\rm Re}(A_{\rm SM}A^{(8)}_3) \sim v^2\hat s^2/(\Lambda^4 m_W^2)$ versus $\int d\theta^* 2{\rm Re}(A_{\rm SM}A^{(8)}_{24}) \sim v^2\hat s/\Lambda^4$, where $A_3 \propto g^{(3)}_{WHq_Lq'_L} \propto c^{(4)}_{q^2H^2D^3}$ and $A_{24}\propto (g^{(2)}-g^{(4)})_{WHq_Lq'_L}$, which contains $c^{(3)}_{q^2H^2D^3}$ and $c^{(3)}_{q^2WH^2D}$. For $W_T$ only $A_{24}$ interferes: $\sim v^2\hat s/\Lambda^4$. The $\psi^2XH^2D$ class drops out of the longitudinal limit ("they do not contain to longitudinal $V$ in the high energy limit"). Five-point $\psi^4H^2$ contact amplitudes are $\mathcal A = i g_{\psi_1\psi_2\psi_3\psi_4 H}\langle34\rangle[12]$ with $g\propto v/\Lambda^4$ (VBF eq. `5ptamp`), "unsuppressed in energy".

**Selection assumptions.** CP conservation and $U(3)^5$ flavour symmetry; only operators with SM chirality (LL or RR currents), colour-singlet current products, and Lorentz structures that interfere with the SM; $s$-channel topologies dropped (VBF cuts); Yukawa-suppressed topologies dropped. All retained operators are tree-level generated. Basis: geoSMEFT-compatible as in `Corbett:2023yhk` (2- and 3-point-contributing operators removed by IBP/EOM, e.g. $Q^{(1)}_{H^2H^{\dag2}D^4}=(H^\dag H)\Box^2(H^\dag H)$ of `Li:2020gnx` replaced by Murphy's $Q^{(1,2,3)}_{H^4}$ [Murphy class $H^4D^4$]).

**Dim-6 energy-enhanced operators (VBF Table 1, `tab:D6_biggest`).** $Q^{(1)}_{H\psi} = i(\bar\psi_p\gamma^\nu\psi_r)H^\dag\overleftrightarrow{D}_\mu H$ for $\psi=\{q,u,d\}$ and $Q^{(3)}_{Hq} = i(\bar q\gamma^\nu\sigma^I q)H^\dag\overleftrightarrow{D}_\mu\sigma_I H$. WC names: $c^{(1)}_{Hq}, c^{(3)}_{Hq}, c_{Hu}, c_{Hd}$. The $H^2X^2$ operators ($c_{HW}, c_{HB}, c_{HWB}$) enter $HVV$ but are sub-leading (transverse propagators). [Note: source writes $\gamma^\nu$ with $D_\mu$, index mismatch in the source.]

**Dim-8 energy-enhanced classes for VBF.** Three classes, all of which are leading ($\lambda^4$ or $\lambda^5$ at 4-point, $\lambda^6$ at 5-point, see Section 2):

**(a) Class $\psi^2XH^2D$ (Murphy class 15, LC label $\psi^2H^2XD$), VBF Table 3 `tab:D8_nongeo_ops1`.** VBF numbering differs from Murphy's, and VBF's $\overleftrightarrow D$ differs from Murphy's by a factor of $i$ (stated in the caption). Only the CP-even, non-dual structures appear. Mapping established by comparing the explicit operator forms:

| VBF label (and WC name $c^{(i)}_{\psi^2XH^2D}$) | VBF operator form | $\psi$ | Murphy label (same form, $\tau^I$ for $\sigma^I$) | FR name in `dim8_geosmeftVBF.fr` |
|---|---|---|---|---|
| $Q^{(1)}_{\psi^2BH^2D}$ | $(\bar\psi\gamma^\nu\psi)D^\mu(H^\dag H)B_{\mu\nu}$ | $q,u,d$ | $Q^{(5)}_{q^2BH^2D}$, $Q^{(1)}_{u^2BH^2D}$, $Q^{(1)}_{d^2BH^2D}$ | `c2Q2HBD3`, `c2u2HBD1`, `c2d2HBD1` |
| $Q^{(2)}_{\psi^2BH^2D}$ | $i(\bar\psi\gamma^\nu\psi)(H^\dag\overleftrightarrow D^\mu H)B_{\mu\nu}$ | $q,u,d$ | $Q^{(7)}_{q^2BH^2D}$, $Q^{(3)}_{u^2BH^2D}$, $Q^{(3)}_{d^2BH^2D}$ | `c2Q2HBD4`, `c2u2HBD2`, `c2d2HBD2` |
| $Q^{(3)}_{\psi^2BH^2D}$ | $(\bar\psi\gamma^\nu\sigma^I\psi)D^\mu(H^\dag\sigma^IH)B_{\mu\nu}$ | $q$ | $Q^{(1)}_{q^2BH^2D}$ | `c2Q2HBD1` |
| $Q^{(4)}_{\psi^2BH^2D}$ | $i(\bar\psi\gamma^\nu\sigma^I\psi)(H^\dag\overleftrightarrow D^{I\mu}H)B_{\mu\nu}$ | $q$ | $Q^{(3)}_{q^2BH^2D}$ | `c2Q2HBD2` |
| $Q^{(1)}_{\psi^2WH^2D}$ | $(\bar\psi\gamma^\nu\psi)D^\mu(H^\dag\sigma^IH)W^I_{\mu\nu}$ | $q,u,d$ | $Q^{(1)}_{q^2WH^2D}$, $Q^{(1)}_{u^2WH^2D}$, $Q^{(1)}_{d^2WH^2D}$ | `c2Q2HWD1`, `c2u2HWD1`, `c2d2HWD1` |
| $Q^{(2)}_{\psi^2WH^2D}$ | $i(\bar\psi\gamma^\nu\psi)(H^\dag\overleftrightarrow D^{I\mu}H)W^I_{\mu\nu}$ | $q,u,d$ | $Q^{(3)}_{q^2WH^2D}$, $Q^{(3)}_{u^2WH^2D}$, $Q^{(3)}_{d^2WH^2D}$ | `c2Q2HWD2`, `c2u2HWD2`, `c2d2HWD2` |
| $Q^{(3)}_{\psi^2WH^2D}$ | $(\bar\psi\gamma^\nu\sigma^I\psi)D^\mu(H^\dag H)W^I_{\mu\nu}$ | $q$ | $Q^{(5)}_{q^2WH^2D}$ | `c2Q2HWD3` |
| $Q^{(4)}_{\psi^2WH^2D}$ | $i(\bar\psi\gamma^\nu\sigma^I\psi)(H^\dag\overleftrightarrow D^\mu H)W^I_{\mu\nu}$ | $q$ | $Q^{(7)}_{q^2WH^2D}$ | `c2Q2HWD4` |
| $Q^{(5)}_{\psi^2WH^2D}$ | $\epsilon_{IJK}(\bar\psi\gamma^\nu\sigma^I\psi)D^\mu(H^\dag\sigma^JH)W^K_{\mu\nu}$ | $q$ | $Q^{(9)}_{q^2WH^2D}$ | `c2Q2HWD5` |
| $Q^{(6)}_{\psi^2WH^2D}$ | $i\epsilon_{IJK}(\bar\psi\gamma^\nu\sigma^I\psi)(H^\dag\overleftrightarrow D^{J\mu}H)W^K_{\mu\nu}$ | $q$ | $Q^{(11)}_{q^2WH^2D}$ | `c2Q2HWD6` |

Murphy's even-numbered partners (2,4,6,8,10,12 for $q^2WH^2D$; 2,4,6,8 for $q^2BH^2D$; 2,4 for $u^2/d^2$) are the $\widetilde X$ (CP-odd) versions and are not used. Murphy's $\psi^2GH^2D$ operators are not used (no gluon in VBF at this order). Caution: the FR file numbering of the $q^2BH^2D$ coefficients follows Murphy's ordering (triplet-triplet first), not the VBF table's (see Section 6, Q5).

**(b) Class $\psi^2H^2D^3$ (Murphy class 11), VBF Table 4 `tab:D8_nongeo_ops2`.** VBF uses a geoSMEFT-compatible form that is NOT identical to Murphy's operators (derivatives placed so that no 2- or 3-point vertex is generated). $D^2_{(\mu,\nu)}$ means derivatives symmetrised in Lorentz indices.

| VBF label / WC | VBF operator form | $\psi$ | FR name |
|---|---|---|---|
| $Q^{(1)}_{\psi^2H^2D^3}$ | $i(\bar\psi_p\gamma^\mu\psi_r)\left[(D_\nu H)^\dag(D^2_{(\mu,\nu)}H)-(D^2_{(\mu,\nu)}H)^\dag(D_\nu H)\right]$ | $q,u,d$ | `c2Q2H3D1`, `c2u2H3D1`, `c2d2H3D1` |
| $Q^{(2)}_{\psi^2H^2D^3}$ | $i(\bar\psi_p\gamma^\mu\overleftrightarrow D_\nu\psi_r)\left[(D_\mu H)^\dag(D_\nu H)+(D_\nu H)^\dag(D_\mu H)\right]$ | $q,u,d$ | `c2Q2H3D2`, `c2u2H3D2`, `c2d2H3D2` |
| $Q^{(3)}_{\psi^2H^2D^3}$ | $i(\bar\psi_p\gamma^\mu\sigma^I\psi_r)\left[(D_\nu H)^\dag\tau^I(D^2_{(\mu,\nu)}H)-(D^2_{(\mu,\nu)}H)^\dag\sigma^I(D_\nu H)\right]$ | $q$ | `c2Q2H3D3` |
| $Q^{(4)}_{\psi^2H^2D^3}$ | $i(\bar\psi_p\gamma^\mu\sigma^I\overleftrightarrow D_\nu\psi_r)\left[(D_\mu H)^\dag\tau^I(D_\nu H)+(D_\nu H)^\dag\tau^I(D_\mu H)\right]$ | $q$ | `c2Q2H3D4` |

Murphy's corresponding basis operators (class 11) are
$Q^{(1)}_{q^2H^2D^3} = i(\bar q_p\gamma^\mu D^\nu q_r)(D_{(\mu}D_{\nu)}H^\dag H)$,
$Q^{(2)}_{q^2H^2D^3} = i(\bar q_p\gamma^\mu D^\nu q_r)(H^\dag D_{(\mu}D_{\nu)}H)$,
$Q^{(3)}_{q^2H^2D^3} = i(\bar q_p\gamma^\mu\tau^ID^\nu q_r)(D_{(\mu}D_{\nu)}H^\dag\tau^IH)$,
$Q^{(4)}_{q^2H^2D^3} = i(\bar q_p\gamma^\mu\tau^ID^\nu q_r)(H^\dag\tau^ID_{(\mu}D_{\nu)}H)$ (typeset as `Q_{q^2H^2D^2}^{(4)}` in the Murphy v6 source, an evident typo), plus $Q^{(1,2)}_{u^2H^2D^3}$, $Q^{(1,2)}_{d^2H^2D^3}$ and $Q_{udH^2D^3}+{\rm h.c.}$ (the last is not used by VBF: flavor universality). The linear map between the VBF/geo forms and Murphy's forms is not given in either paper and I did not derive it (Section 6, Q6).

**(c) Class $\psi^4H^2$ (Murphy class 18, $(\bar LL)(\bar LL)H^2$, $(\bar RR)(\bar RR)H^2$, $(\bar LL)(\bar RR)H^2$ subclasses), VBF Table 5 `tab:D8_nongeo_ops3`.** Forms coincide with Murphy's. Only colour-singlet current products and same-chirality-per-current structures are kept (octet-current versions such as Murphy $Q^{(2)}_{u^2d^2H^2}$, $Q^{(3,4)}_{q^2u^2H^2}$, $Q^{(3,4)}_{q^2d^2H^2}$ do not interfere with the colour-singlet SM VBF amplitude in this basis; $(\bar LR)(\bar LR)$ and $(\bar LR)(\bar RL)$ have the wrong helicity). Murphy's $Q^{(5)}_{q^4H^2}$ (the $\epsilon^{IJK}$ structure, vanishing for one generation) and the flavour-only combination $Q^{(4)}_{q^4H^2}$ are not used.

| VBF label / WC | Operator | Murphy label | FR name |
|---|---|---|---|
| $Q^{(1)}_{q^4H^2}$ | $(\bar q\gamma^\mu q)(\bar q\gamma_\mu q)(H^\dag H)$ | $Q^{(1)}_{q^4H^2}$ | `c2H4Q1` |
| $Q^{(2)}_{q^4H^2}$ | $(\bar q\gamma^\mu q)(\bar q\gamma_\mu\sigma^Iq)(H^\dag\sigma^IH)$ | $Q^{(2)}_{q^4H^2}$ | `c2H4Q2` |
| $Q^{(3)}_{q^4H^2}$ | $(\bar q\gamma^\mu\sigma^Iq)(\bar q\gamma_\mu\sigma^Iq)(H^\dag H)$ | $Q^{(3)}_{q^4H^2}$ | `c2H4Q3` |
| $Q^{(1)}_{u^4H^2}$ | $(\bar u\gamma^\mu u)(\bar u\gamma_\mu u)(H^\dag H)$ | $Q_{u^4H^2}$ (no superscript in Murphy) | `c2H4u` |
| $Q^{(1)}_{d^4H^2}$ | $(\bar d\gamma^\mu d)(\bar d\gamma_\mu d)(H^\dag H)$ | $Q_{d^4H^2}$ | `c2H4d` |
| $Q^{(1)}_{u^2d^2H^2}$ | $(\bar u\gamma^\mu u)(\bar d\gamma_\mu d)(H^\dag H)$ | $Q^{(1)}_{u^2d^2H^2}$ | `c2H2u2d` |
| $Q^{(1)}_{q^2u^2H^2}$ | $(\bar q\gamma^\mu q)(\bar u\gamma_\mu u)(H^\dag H)$ | $Q^{(1)}_{q^2u^2H^2}$ | `c2H2Q2u1` |
| $Q^{(2)}_{q^2u^2H^2}$ | $(\bar q\gamma^\mu\sigma^Iq)(\bar u\gamma_\mu u)(H^\dag\sigma^IH)$ | $Q^{(2)}_{q^2u^2H^2}$ | `c2H2Q2u2` |
| $Q^{(1)}_{q^2d^2H^2}$ | $(\bar q\gamma^\mu q)(\bar d\gamma_\mu d)(H^\dag H)$ | $Q^{(1)}_{q^2d^2H^2}$ | `c2H2Q2d1` |
| $Q^{(2)}_{q^2d^2H^2}$ | $(\bar q\gamma^\mu\sigma^Iq)(\bar d\gamma_\mu d)(H^\dag\sigma^IH)$ | $Q^{(2)}_{q^2d^2H^2}$ | `c2H2Q2d2` |

(FR operator bodies verified for all three classes in `dim8_geosmeftVBF.fr`; the FR file uses `Ta` = $\tau^I/2$ with explicit factors of 4 to reproduce $\sigma^I\otimes\sigma^I$, and its $\psi^2H^2D^3$ terms carry the same relative factors of $i$, $1/2$ and 4 as listed there, e.g. `(I c2Q2H3D1/2)`, `I c2Q2H3D2`, `I 4*c2Q2H3D3/2`, `I 4*c2Q2H3D4`.)

**Numerical ranking in VBF (VBF Table 7 `tab:xsx8`, $\Lambda=1.2$ TeV, all $c_8=+1$, cuts $200<p_T^H<400$ GeV, $(m_{jj},\Delta\eta_{jj}) = (480\,{\rm GeV}, 2.5)$ and $(600\,{\rm GeV}, 3.0)$).** Coefficients with the largest deviations from SM: $c^{(3)}_{q^4H^2}$ (+10.0%, +9.7%), $c^{(3)}_{q^2H^2D^3}$ (+4.7%, +4.8%), $c^{(4)}_{q^2H^2D^3}$ (+3.2%, +3.3%, but breaks EFT validity at 1.2 TeV, needs $\Lambda>3$ TeV and was dropped), $c^{(3)}_{q^2WH^2D}$ (+2.4%, +2.5%), $c^{(1)}_{q^4H^2}$ (+1.5%, +1.8%). All others are below about 1.5% in magnitude. Coefficients listed in that table: $c^{(1,2,3)}_{q^4H^2}$, $c^{(1)}_{d^4H^2}$, $c^{(1)}_{u^4H^2}$, $c^{(1)}_{u^2d^2H^2}$, $c^{(1,2)}_{q^2d^2H^2}$, $c^{(1,2)}_{q^2u^2H^2}$, $c^{(1,3)}_{q^2BH^2D}$, $c^{(1,3,5)}_{q^2WH^2D}$, $c^{(1)}_{u^2WH^2D}$, $c^{(1)}_{u^2BH^2D}$, $c^{(1)}_{d^2WH^2D}$, $c^{(1)}_{d^2BH^2D}$, $c^{(1,2,3,4)}_{q^2H^2D^3}$, $c^{(1)}_{u^2H^2D^3}$, $c^{(1)}_{d^2H^2D^3}$. (The $i$-type operators $Q^{(2,4,6)}_{\psi^2WH^2D}$, $Q^{(2,4)}_{\psi^2BH^2D}$ and $Q^{(2)}_{u^2,d^2H^2D^3}$ appear in the operator tables but not in the cross-section table or in the $Z$ coupling table.)

Analytic expectation (VBF Sec. 4): $c^{(4)}_{q^2H^2D^3}$ via $g^{(3)}_{WHq_Lq'_L}$ is the single most energy-enhanced operator among those generating $qV\to q'H$ ($\hat s\hat t$ term, $W_L$ interference $\sim\hat s^2$); $c^{(3)}_{q^2H^2D^3}$ and $c^{(3)}_{q^2WH^2D}$ enter through $(g^{(2)}-g^{(4)})_{WHq_Lq'_L}$ and interfere for $W_T$; $(LL)(LL)$ contact operators $Q^{(1,3)}_{q^4H^2}$ interfere with the largest SM helicity amplitude. Differential results (VBF Sec. 6): $c^{(3)}_{q^4H^2}$ and $c^{(3)}_{q^2H^2D^3}$ give comparable high-$p_T^H$ enhancement; $c^{(3)}_{q^2H^2D^3}$ also shifts $\Delta\eta_{jj}$ and $\Delta\phi_{jj}$ while $c^{(3)}_{q^4H^2}$ and $c^{(3)}_{Hq}$ do not.

**Coupling dictionaries (VBF Tables 5, 6, 10), useful for validating the automated model.** $Z$ contact couplings, e.g.

```latex
g_{ZHu_Lu_L}^{(2)} = \frac{v}{4 c_w s_w} \left[ -e \left( c^{(1)}_{q^2H^2D^3} - c^{(3)}_{q^2H^2D^3} \right) + 4 c_w s_w \left( s_w \left( c^{(3)}_{q^2BH^2D} - c^{(1)}_{q^2BH^2D} \right) + c_w \left( c^{(1)}_{q^2WH^2D} - c^{(3)}_{q^2WH^2D} \right) \right) \right]
```

```latex
g_{ZHu_Lu_L}^{(3)} = \frac{v}{4 c_w s_w} \left[ 3 e \left( c^{(1)}_{q^2H^2D^3} - c^{(3)}_{q^2H^2D^3} \right) + 4 c_w s_w \left( s_w \left( c^{(3)}_{q^2BH^2D} - c^{(1)}_{q^2BH^2D} \right) + c_w \left( c^{(1)}_{q^2WH^2D} - c^{(3)}_{q^2WH^2D} \right) \right) \right]
```

($d_L$ versions: flip the relative signs to $+$ inside each bracket and overall $-e(c^{(1)}+c^{(3)})_{q^2H^2D^3}$ for $g^{(2)}$, $+3e(c^{(1)}+c^{(3)})$ for $g^{(3)}$.) $W$ contact couplings:

```latex
g_{WH\bar{u}_L d_L}^{(1)} = \sqrt{2}\,\frac{e v}{s_w}\, c_{Hq}^{(3)}\, V_{ud},\qquad
g_{WH\bar{u}_L d_L}^{(2)} = \frac{v}{2 \sqrt{2}\, s_w}\, V_{ud} \left[  e\, c^{(3)}_{q^2 H^2 D^3} - 4 s_w \big( c^{(3)}_{q^2 W H^2 D} + i\,c^{(3)}_{q^2 W H^2 D} \big) \right]
```

```latex
g_{WH\bar{u}_L d_L}^{(3)} = \frac{e v}{\sqrt{2}\, s_w}\, V_{ud}\, c^{(4)}_{q^2 H^2 D^3},\qquad
g_{WH\bar{u}_L d_L}^{(4)} = - \frac{v}{2 \sqrt{2}\, s_w}\, V_{ud} \left[ 3 e\, c^{(3)}_{q^2 H^2 D^3} + 4 s_w \big( c^{(3)}_{q^2 W H^2 D} + i c^{(5)}_{q^2 W H^2 D} \big) \right]
```

(The "$c^{(3)}+i c^{(3)}$" in $g^{(2)}$ is transcribed verbatim and is almost certainly a typo in the source, see Section 6, Q7.) Right-handed $Z$ couplings: $g^{(2)}_{ZHu_Ru_R} = -\frac{v}{4c_ws_w}\big(e\,c^{(1)}_{u^2H^2D^3} - 4c_ws_w(c^{(1)}_{u^2BH^2D}s_w + 2c^{(1)}_{u^2WH^2D}c_w)\big)$, $g^{(3)}_{ZHu_Ru_R} = \frac{v}{4c_ws_w}\big(3e\,c^{(1)}_{u^2H^2D^3} + 4c_ws_w(c^{(1)}_{u^2BH^2D}s_w + 2c^{(1)}_{u^2WH^2D}c_w)\big)$, and $u\to d$ likewise. Five-point contact couplings: $g_{u_Ld_Lu_Ld_LH} = 2v(c^{(1)}_{q^4H^2} - c^{(3)}_{q^4H^2} + 2c^{(3)}_{q^4H^2})$ [verbatim], $g_{u_Ld_Ru_Ld_RH} = v(c^{(1)}_{q^2d^2H^2} - c^{(2)}_{q^2d^2H^2})$, $g_{u_Rd_Ru_Rd_RH} = v\,c^{(1)}_{u^2d^2H^2}$, $g_{u_Lu_Lu_Lu_LH} = 2v(c^{(1)}_{q^4H^2} - c^{(2)}_{q^4H^2} + c^{(3)}_{q^4H^2})$, $g_{u_Ru_Lu_Ru_LH} = v(c^{(1)}_{q^2u^2H^2} - c^{(2)}_{q^2u^2H^2})$, $g_{u_Ru_Ru_Ru_RH} = 2v\,c^{(2)}_{u^4H^2}$ [verbatim], $g_{d_Ld_Ld_Ld_LH} = 2v(c^{(1)}_{q^4H^2} + c^{(2)}_{q^4H^2} + c^{(3)}_{q^4H^2})$, $g_{d_Rd_Ld_Rd_LH} = v(c^{(1)}_{q^2d^2H^2} + c^{(2)}_{q^2d^2H^2})$, $g_{d_Rd_Rd_Rd_RH} = 2v\,c^{(1)}_{d^4H^2}$.

### 3.2 VH, from the VBF paper (Sec. 7, `sec:associated`)

Simulation $pp\to Z(\bar qq)H$ with $75\le p_{T,Z}\le 400$ GeV, $70\le m_{jj}\le 110$ GeV (STXS-like), $\Lambda = 1.2$ TeV. Findings: $c^{(3)}_{H^2Q^2D^3}$ (the paper switches notation here; this is $c^{(3)}_{q^2H^2D^3}$) has a large effect growing with $p_T^H$ and "approaches the boundary of the EFT's validity"; it affects both VBF and VH. $c^{(3)}_{H^2Q^4}$ ($= c^{(3)}_{q^4H^2}$) has negligible effect in VH because the resonant $m_{jj}$ cuts suppress non-resonant contact topologies (crossing symmetry broken by cuts), consistent with `Martin:2023tvi`. The $\psi^2XH^2D$ and $\psi^2H^2D^3$ operators of VBF Tables 3 and 4 are exactly the operators shown in `Corbett:2023yhk` to be the complete set of dim-8 operators interfering with the SM in VH (with leptonic $V$ decay); $\psi^4H^2$ was not considered there.

### 3.3 VH, from the LC paper (Sec. V.A, `sec:VH`): $q\bar q\to VH$ at 4-point

Vertex expansions (LC eq. `vhtrips` and the two following unlabelled equations), verbatim:

```latex
g_{\bar{q}qV} = \frac{g^{\rm SM}_{\bar{q}qV}}{\lambda^2}
+ \frac{\lambda}{\hat\Lambda^2}\, c_{\psi^2HX}
+ \frac{\lambda^2}{\hat\Lambda^2}\, c_{\psi^2H^2D}
+ \frac{\lambda^5}{\hat\Lambda^4}\, c_{\psi^2H^3X}
+ \frac{\lambda^5}{\hat\Lambda^4}\, c_{\psi^2H^4D} + \cdots
```

```latex
g_{hVV} = \frac{g^{\rm SM}_{hVV}}{\lambda}
+ \frac{\lambda}{\hat\Lambda^2}\, c_{H^2X^2}
+ \frac{\lambda^3}{\hat\Lambda^2}\, c_{H^4D^2}
+ \frac{\lambda^5}{\hat\Lambda^2}\, c_{H^4XD^2}
+ \frac{\lambda^5}{\hat\Lambda^4}\, c_{H^4X^2} + \cdots
```

```latex
g_{\bar{q}qhV} = \frac{\lambda^2}{\hat\Lambda^2}\, c_{\psi^2HX}
+ \frac{\lambda^3}{\hat\Lambda^2}\, c_{\psi^2H^2D}
+ \frac{\lambda^4}{\hat\Lambda^4}\, c_{\psi^2HXD^2}
+ \frac{\lambda^5}{\hat\Lambda^4}\, c_{\psi^2H^2D^3}
+ \frac{\lambda^5}{\hat\Lambda^4}\, c_{\psi^2H^4D} + \cdots
```

(Coding in the source: $c_{\psi^2HX}$, $c_{\psi^2H^3X}$, $c_{\psi^2HXD^2}$ are `\bothfeatures`; $c_{H^2X^2}$ is `\looponly`; the rest plain.) Amplitudes (to $\mathcal O(\lambda^5)$, propagator $\sim\lambda^4$):

```latex
\mathcal{A}^{(1)}_{qqVh} = \lambda\, g^{\rm SM}_{\bar{q}qV}\, g^{\rm SM}_{hVV}
+ \frac{\lambda^3}{\hat\Lambda^2}\, g^{\rm SM}_{\bar{q}qV}\, c_{H^2X^2}
+ \frac{\lambda^4}{\hat\Lambda^2}\, g^{\rm SM}_{hVV}\, c_{\psi^2HX}
+ \frac{\lambda^5}{\hat\Lambda^2}\,\Bigl(g^{\rm SM}_{hVV}\, c_{\psi^2H^2D}
+ g^{\rm SM}_{\bar{q}qV}\, c_{H^4D^2}\Bigr) + \cdots,
\qquad
\mathcal{A}^{(2)}_{qqVh} = g_{\bar{q}qhV}
```

After dropping non-interfering operators (purple = `\bothfeatures`, plus $c_{H^2X^2}$ and $c_{H^4X^2}$ which feed transverse $V$) and setting the pole-constrained $c_{\psi^2H^2D}$, $c_{H^2X^2}$ to zero (assumptions as in `Hays:2018zze`, `Corbett:2023yhk`):

```latex
\mathcal{A}^{(1)}_{qqVh} = \lambda\, g^{\rm SM}_{\bar{q}qV}\, g^{\rm SM}_{hVV}
+ \frac{\lambda^5}{\hat\Lambda^2}\, g^{\rm SM}_{\bar{q}qV}\, c_{H^4D^2} + \cdots,
\qquad
\mathcal{A}^{(2)}_{qqVh} = \frac{\lambda^5}{\hat\Lambda^4}\, c_{\psi^2H^2D^3}
+ \frac{\lambda^5}{\hat\Lambda^4}\, c_{\psi^2H^4D} + \cdots
```

Conclusion (verbatim): "our analysis underscores the special importance of operators of the type $\psi^2H^2D^3$; their pronounced energy dependence and distinctive interference patterns make them especially promising probes of new physics, as also emphasized in Refs. `Corbett:2023yhk`, `Degrande:2023iob`, `Assi:2024zap`."

**Energy-enhanced dim-8 classes for VH according to LC:** $\psi^2H^2D^3$ (leading, $\lambda^5$ at the $\bar qqhV$ vertex), $\psi^2H^4D$ (quoted at $\lambda^5$, see Q3), $\psi^2HXD^2$ (formally $\lambda^4$, the most enhanced, but loop-level and mixed chirality so dropped), $\psi^2H^3X$ (dropped, same reason), $H^4XD^2$ and $H^4X^2$ in $hVV$ at $\lambda^5$ ($H^4X^2$ dropped as transverse).

### 3.4 Other LC example processes (for completeness)

**$gg\to t\bar tH$ (5-point, LC Sec. V.B).** Eight topologies; amplitude scalings verbatim:

```latex
\mathcal{A}^{(1)}_{ggttH} = \lambda^2\, g^{\rm SM}_{VVV}\, g^{\rm SM}_{\bar q q h}\, g^{\rm SM}_{\bar q q V}
+\frac{\lambda^4}{\hat \Lambda^2}\, g^{\rm SM}_{\bar q q V}\, g^{\rm SM}_{\bar q q h}\, c_{X^3}
+\frac{\lambda^5}{\hat \Lambda^2}\, g^{\rm SM}_{VVV}\, g^{\rm SM}_{\bar q q h}\, c_{\psi^2 H X}
+ \frac{\lambda^6}{\hat \Lambda^2}\, g^{\rm SM}_{VVV}\,\Bigl( g^{\rm SM}_{\bar q q h}\, c_{\psi^2 H^2 D} +  g^{\rm SM}_{\bar q q V}\,c_{\psi^2H^3}\Bigr) +\cdots
```
```latex
\mathcal{A}^{(2)}_{ggttH} = \lambda^2\, g^{\rm SM}_{\bar q q h}\,\Bigl(g^{\rm SM}_{\bar q q V}\Bigr)^2
+\frac{\lambda^5}{\hat \Lambda^2}\, g^{\rm SM}_{\bar q q V}\, g^{\rm SM}_{\bar q q h}\, c_{\psi^2 H X}
+ \frac{\lambda^6}{\hat \Lambda^2}\, g^{\rm SM}_{\bar q q V}\,\Bigl( g^{\rm SM}_{\bar q q h}\, c_{\psi^2 H^2 D} +  g^{\rm SM}_{\bar q q V}\,c_{\psi^2H^3}\Bigr) +\cdots
```
```latex
\mathcal{A}^{(3)}_{ggttH} = \frac{\lambda^5}{\hat \Lambda^2}\, g^{\rm SM}_{VVV}\, g^{\rm SM}_{\bar q q V}\, c_{H^2X^2} + \cdots,\qquad
\mathcal{A}^{(4)}_{ggttH} = \frac{\lambda^6}{\hat \Lambda^4}\, g^{\rm SM}_{\bar q q h}\, c_{\psi^2X^2D} + \cdots
```
```latex
\mathcal{A}^{(5)}_{ggttH} = \frac{\lambda^4}{\hat \Lambda^2}\, g^{\rm SM}_{\bar q q V}\, c_{\psi^2HX}
+ \frac{\lambda^6}{\hat \Lambda^4}\, g^{\rm SM}_{\bar q q V}\, c_{\psi^2HXD^2} +\cdots,\qquad
\mathcal{A}^{(6)}_{ggttH} = \frac{\lambda^4}{\hat \Lambda^2}\, g^{\rm SM}_{VVV}\, c_{\psi^2HX}
+ \frac{\lambda^6}{\hat \Lambda^4}\,\Bigl( g^{\rm SM}_{VVV}\, c_{\psi^2HXD^2} + c_{X^3}\,c_{\psi^2HX}\Bigr) + \cdots
```
```latex
\mathcal{A}^{(7)}_{ggttH} = \frac{\lambda^5}{\hat \Lambda^2}\, g^{\rm SM}_{\bar q q V}\, c_{H^2X^2} + \cdots,\qquad
\mathcal{A}^{(8)}_{ggttH} = \frac{\lambda^4}{\hat \Lambda^2}\,c_{\psi^2HX}
+\frac{\lambda^6}{\hat \Lambda^4}\, c_{\psi^2 H X^2}
```

(Coding: $c_{X^3}$, $c_{H^2X^2}$ loop-only; $c_{\psi^2HX}$, $c_{\psi^2HXD^2}$, $c_{\psi^2HX^2}$ both; $c_{\psi^2H^3}$ mixed chirality; $c_{\psi^2X^2D}$ is typeset `\mixedchirality` in $\mathcal A^{(4)}$ but `\looponly` in the following text and in the tables.) Conclusions: dropping suppressed/non-interfering terms the leading SMEFT term is $\lambda^5 c_{H^2X^2}$; zeroing it (Higgs-pole bound) moves the lead to the $\lambda^6$ 5-point vertex from $c_{\psi^2X^2D}$. Zeroing all loop-level operators: $\lambda^5 c_{\psi^2H^2D}$ and $\lambda^6 c_{\psi^2H^3}$; zeroing those too (pole bounds): all $\mathcal O(\lambda^7)$, from $c_{H^4D^2}$ at dim-6 and $c_{\psi^2H^2D^3}$, $c_{\psi^2H^2XD}$, $c_{\psi^2H^4D}$ at dim-8.

**$\bar qq\to jjHH$ (6-point, LC Sec. V.C).** $s$-channel, Yukawa-suppressed and $\psi^2h^2$ topologies dropped; eight topologies remain. Dominant SM topology $\sim\lambda^4$. Without assumptions the dominant SMEFT term is $\mathcal O(\lambda^6)$ from $c_{H^2X^2}$. Zeroing $c_{H^2X^2}$ ($H\to\gamma\gamma$), LEP-bounded $c_{\psi^2H^2D}$ and non-SM-helicity operators, the first SMEFT effects are $\mathcal O(\lambda^8)$ from $c_{H^4D^2}$ (dim-6) and $c_{\psi^2H^2D^3}$, $c_{\psi^2H^2XD}$, $c_{\psi^4H^2}$ (dim-8). LC states that two of these ($c_{\psi^2H^2D^3}$, $c_{\psi^4H^2}$) were confirmed as the most significant contributors to single-Higgs VBF in `Assi:2024zap`, "thereby validating our prescription."

**Summary of dim-8 classes singled out across both papers as energy enhanced and tree-level with SM-like chirality:** $\psi^2H^2D^3$ (VBF, VH, $t\bar tH$, $jjHH$), $\psi^2XH^2D$ (VBF, VH, $t\bar tH$, $jjHH$; LC writes it $\psi^2H^2XD$), $\psi^4H^2$ (VBF, $jjHH$; suppressed in VH by resonant cuts), $\psi^2H^4D$ (VH, $t\bar tH$ per LC), plus bosonic $H^4D^4$, $H^4XD^2$ and $H^4X^2$ where $hVV$ or $h^nV^m$ vertices enter. Loop-level leading classes at 4-point ($X^4$, $H^2X^2D^2$, $\psi^2X^2D$, $\psi^2HXD^2$) are formally most enhanced but are dropped under the tree-level assumption.

---

## 4. BibTeX keys in `paper/ref.bib` that are cited by the two papers

119 distinct keys are cited across the two `.tex` files; 91 exist in `ref.bib`, 28 do not. Below, keys grouped by the categories requested. Only keys present in `ref.bib` are listed unless stated otherwise.

- **SMEFT reviews and foundations:** `Buchmuller:1985jz`, `Brivio:2017vri`, `Henning:2015alf` (operator counting "2, 84, 30, 993, ..."), `DAmbrosio:2002vsn` (MFV), `Giudice:2007fh` (SILH), `Contino:2013kra`, `Falkowski:2014tna`, `Elias-Miro:2013eta`, `Gupta:2014rxa`.
- **Warsaw basis:** `Grzadkowski:2010es`.
- **Murphy basis:** `Murphy:2020rsh` (title in the bib entry has the typo "Eective").
- **Li et al basis:** `Li:2020gnx`.
- **geoSMEFT and geo-compatible dim-8 bases:** `Helset:2020yio`, `Hays:2020scx`, `Corbett:2021eux`, `Helset:2022pde`, `Assi:2023zid`, `Corbett:2021jox`, `Corbett:2023yhk` (geo-compatible basis for VH used by VBF paper), `Kim:2022amu`, `Corbett:2021cil`, `Martin:2023fad`.
- **FeynRules:** `Alloul:2013bka`.
- **UFO:** not cited by either paper. `Degrande:2011ua` ("UFO - The Universal FeynRules Output") is present in `ref.bib` and can be used.
- **MadGraph:** `Alwall:2014hca` (cited). `Alwall:2011uj` (MadGraph 5) is present but uncited.
- **SMEFTsim:** not cited by either paper. `Brivio:2017btx` and `Brivio:2020onw` (SMEFTsim 3.0) are present in `ref.bib` and can be used.
- **Dim-8 phenomenology:** `Hays:2018zze`, `Corbett:2023yhk`, `Corbett:2023qtg`, `Martin:2023tvi`, `Corbett:2021eux`, `Kim:2022amu`, `Degrande:2023iob`, `Dawson:2021xei`, `Dawson:2024ozw`, `Alioli:2020kez`, `Boughezal:2021tih`, `Boughezal:2022nof`, `Allwicher:2022gkm`, `Zhang:2021eeo`, `Biekotter:2020flu`, `Corbett:2021cil`, `Martin:2023fad`.
- **Dim-8 RGE:** `Chala:2021pll`, `DasBakshi:2022mwk`, `Boughezal:2024zqa`, `Helset:2022pde`, `Assi:2023zid`.
- **VBF / SMEFT-at-VBF / EWA:** `Araz:2020zyh`, `Banerjee:2019twi`, `Degrande:2016dqg`, `Dawson:1984gx` (effective W approximation), `Plehn:2001nj`, `Plehn:2001qg`, `Dittmaier:2012vm`, `LHCHiggsCrossSectionWorkingGroup:2011wcg`, `LHCHiggsCrossSectionWorkingGroup:2013rie`, `LHCHiggsCrossSectionWorkingGroup:2016ypw`.
- **Global fits / LEP constraints used for $c_6$ values:** `Ellis:2018gqa`, `Ellis:2020unq`, `Almeida:2021asy`, `Brivio:2021alv`, `deBlas:2016ojx`.
- **On-shell / amplitude methods:** `Ma:2019gtx` (present). Not present: `Shadmi:2018xan`, `Aoude:2019tzn`, `Durieux:2020gip`, `AccettulliHuber:2021uoa`, `Elvang:2013cua`.
- **Tree vs loop classification:** none present (`Craig:2019wmo`, `Arzt_1995`, `Buchalla:2022vjp` all missing).
- **Matching / UV hierarchies:** none present (`deBlas:2014mba`, `deBlas:2017xtg`, `Carmona:2021xtq`, `Fuentes-Martin:2022jrf`, `Li:2023cwy` missing). `Langacker:2008yv` present.
- **Other SMEFT pheno cited in intros (present):** `Englert:2014cva`, `Amar:2014fpa`, `Buschmann:2014sia`, `Craig:2014una`, `Ellis:2014dva`, `Ellis:2014jta`, `Banerjee:2015bla`, `Englert:2015hrx`, `Contino:2016jqw`, `Biekotter:2016ecg`, `Barklow:2017suo`, `Barklow:2017awn`, `Englert:2017aqb`, `banerjee1`, `Grojean:2018dqj`, `Biekotter:2018rhp`, `Goncalves:2018ptp`, `Gomez-Ambrosio:2018pnl`, `Freitas:2019hbk`, `Banerjee:2019pks`, `Gupta:2011be`, `Gupta:2012mi`, `Banerjee:2012xc`, `Gupta:2012fy`, `Banerjee:2013apa`, `Gupta:2013zza`, `Ghosh:2015gpa`, `Cohen:2016bsd`, `Ge:2016zro`, `Denizli:2017pyu`, `Khanpour:2017cfq`, `panico`, `Franceschini:2017xkh`, `Buckley:2014ana` (LHAPDF6), `Binosi:2008ig` (JaxoDraw).

**Cited but absent from `ref.bib` (28):** `AccettulliHuber:2021uoa`, `Aoude:2019tzn`, `Arganda:2018ftn`, `Arzt_1995`, **`Assi:2024zap`** (the VBF paper itself, needed for the new paper), `Bakshi:2024wzz`, `Bartocci:2023nvp`, `Bishara:2022vsc`, `Buchalla:2022vjp`, `CMS:2022gjd`, `Cappati:2022skp`, `Carmona:2021xtq`, `Celada:2024mcf`, `Cepeda:2019klc`, `Chen:2021rid`, `Craig:2019wmo`, `Dedes:2017zog`, `Dedes:2023zws`, `Delgado:2023ynh`, `Durieux:2020gip`, `Elvang:2013cua`, `Fuentes-Martin:2022jrf`, `Giani:2023gfq`, `Gomez-Ambrosio:2022qsi`, `Li:2023cwy`, `Shadmi:2018xan`, `deBlas:2014mba`, `deBlas:2017xtg`. The LC paper itself has no key in `ref.bib` either.

Other potentially useful keys present in `ref.bib` but not cited by these two papers: `Remmen:2019cyz` (dim-8 bosonic operators, positivity), `Remmen:2020uze`, `Chala:2021wpj`, `Chala:2023jyx`, `Chala:2023xjy`, `Li:2022rag`, `Corbett:2019cwl`, `Corbett:2020bqv` (SMEFT Feynman rules, background field gauge), `Corbett:2021iob`, `Trott:2021vqa`, `Brivio:2022pyi` (truncation/validity), `Brivio:2021yjb` (EW inputs), `Ellis:2023zim`, `Brivio:2019myy`, `Brivio:2014pfa`, `Martin:2021cvs`, `Harlander:2018yns`.

---

## 5. Quick-reference: LC class names versus Murphy class names

LC writes classes with the derivative count last and field strengths before Higgs in some cases. Correspondence (LC name: Murphy class number and name):

$X^4$: 1 $X^4$; $H^8$: 2; $H^6D^2$: 3; $H^4D^4$: 4; $H^2X^3$: 5 $X^3H^2$; $H^4X^2$: 6 $X^2H^4$; $H^2X^2D^2$: 7 $X^2H^2D^2$; $H^4XD^2$ (also written $XH^4D^2$ in LC Table I): 8 $XH^4D^2$; $\psi^2HX^2$: 9 $\psi^2X^2H$; $\psi^2H^3X$: 10 $\psi^2XH^3$; $\psi^2H^2D^3$: 11; $\psi^2H^5$: 12; $\psi^2H^4D$: 13; $\psi^2X^2D$: 14; $\psi^2H^2XD$: 15 $\psi^2XH^2D$; $\psi^2HXD^2$: 16 $\psi^2XHD^2$; $\psi^2H^3D^2$: 17; $\psi^4H^2$: 18; $\psi^4X$: 19; $\psi^4HD$: 20; $\psi^4D^2$: 21.

---

## 6. Open questions and discrepancies found in the sources (not resolved here)

- **Q1 (LC Table V, $H^4D^4$ row).** The vertex "$(\partial h)^2hV^3: E^2v$" has six fields in a 5-point table. Likely a typo for $(\partial h)^2hV^2$ or $(\partial h)hV^3$. Transcribed verbatim above.
- **Q2 (LC Tables V and VI, $\psi^2HXD^2$ row; Table VI $H^4D^4$ and $\psi^2HXD^2$ rows).** Table V lists "$\psi^2(\partial h)(\partial V): E^3$" (4 fields) for a 5-point vertex; Table VI lists "$(\partial h)h^3V^3: Ev$" (7 fields) and "$\psi^2h(\partial V)V^3: E^2$" (7 fields) for 6-point vertices. Field counts do not match the multiplicity. Transcribed verbatim.
- **Q3 (LC Sec. V.A, $\psi^2H^4D$ in $g_{\bar qqhV}$).** LC assigns $\lambda^5$ to the $\psi^2H^4D$ contribution to the 4-point $\bar qqhV$ vertex and then carries it at the same order as $\psi^2H^2D^3$ in $\mathcal A^{(2)}_{qqVh}$ (and at $\lambda^7$ in $t\bar tH$). Applying the algorithm literally ($N_f+N_X+N_H = 6$, $n=4$, $p_{\min}=2$, $q_{\max}=2$) gives $\lambda^{6}$ for the leading $\psi^2h\partial h\,v^2$ vertex and $\lambda^{7}$ for the $\psi^2hV\,v^3$ vertex, not $\lambda^5$. ($\lambda^5$ is the 3-point value from Table III.) I could not reconcile this and did not alter it. Also, in $g_{hVV}$ the $c_{H^4XD^2}$ term is written with $\hat\Lambda^2$ although the class is dim-8 (should presumably be $\hat\Lambda^4$).
- **Q4 (LC tree-level reachability inequality).** As written, $N_f+N_X\le n\le 2N_f+N_X+N_D+N_H$ excludes $X^4$ at $n=5,6$ and $H^2X^3$ at $n=6$, yet those rows appear in Tables V and VI (non-abelian field strengths supply $V^2$). The inequality should probably count $2N_X$ on the right-hand side, or the bound is meant loosely. Needs a decision for the automated implementation.
- **Q5 (numbering of $q^2BH^2D$).** The VBF paper's Table 3 numbers $Q^{(1)}_{\psi^2BH^2D}$ as the singlet-current times $D(H^\dag H)$ structure, but the hand-typed `dim8_geosmeftVBF.fr` assigns `c2Q2HBD1` to the triplet-triplet structure $(\bar q\gamma\tau^Iq)D(H^\dag\tau^IH)B$ (Murphy's ordering) and `c2Q2HBD3` to the singlet structure. For the $W$ operators the FR numbering agrees with the paper's table. It is therefore unclear whether the $c^{(1)}_{q^2BH^2D}$ and $c^{(3)}_{q^2BH^2D}$ entries of VBF Table 7 and of the $Z$ coupling table follow the table numbering or the FR numbering. Both give sub-percent effects, so the physics conclusions are unaffected, but a validation against the new automated model must fix this.
- **Q6 (basis map for $\psi^2H^2D^3$).** The VBF/geo forms $Q^{(1\ldots4)}_{\psi^2H^2D^3}$ (Table 4 of VBF, implemented verbatim in `dim8_geosmeftVBF.fr`) are not Murphy's operators. Neither paper gives the IBP/EOM relation to Murphy's $Q^{(1\ldots4)}_{q^2H^2D^3}$, $Q^{(1,2)}_{u^2,d^2H^2D^3}$. The relation must be derived (the original source is `Corbett:2023yhk` and `Hays:2018zze`) before numerical comparison of, e.g., $c^{(3)}_{q^2H^2D^3}$ effects between the hand-typed model and an automated Murphy-basis model.
- **Q7 (VBF Table 6 typo).** $g^{(2)}_{WH\bar u_Ld_L}$ contains "$c^{(3)}_{q^2WH^2D} + i\,c^{(3)}_{q^2WH^2D}$"; by analogy with $g^{(4)}$ ("$c^{(3)} + i c^{(5)}$") the imaginary partner is probably a different operator (the $\epsilon_{IJK}$ one, $c^{(5)}$, or the $i$-type $c^{(4)}/c^{(6)}$). Unresolved.
- **Q8 (VBF Table 10 typos).** $g_{u_Ld_Lu_Ld_LH} = 2v(c^{(1)} - c^{(3)} + 2c^{(3)})_{q^4H^2}$ simplifies to $2v(c^{(1)}+c^{(3)})$, suggesting one of the $c^{(3)}$ was meant to be $c^{(2)}$; $g_{u_Ru_Ru_Ru_RH} = 2v\,c^{(2)}_{u^4H^2}$ references a coefficient that does not exist in Table 5 (only $c^{(1)}_{u^4H^2}$).
- **Q9 (operator counts).** VBF says "out of 993 dimension-eight operators, only 66 contribute [to 2- and 3-point vertices], assuming flavor universality and conservation of baryon and lepton numbers." Murphy's 993 is the $n_g=1$ total including 98 baryon-number-violating terms (895 are $B$-conserving). LC Table I totals 1030 = 993 + 37 (the terms that vanish without flavour structure). The 66 (19 + 47) is consistent between the two papers.
- **Q10 (coding inconsistencies in LC).** $\psi^2X^2D$ is `\mixedchirality` in $\mathcal A^{(4)}_{ggttH}$ but `\looponly` in the tables and text; $\psi^2H^3$ is `\mixedchirality` in the amplitudes but is referred to as "$\looponly{c_{\psi^2H^3}}$" in the sentence "the leading SMEFT terms are $\lambda^5 c_{\psi^2H^2D}$ and $\lambda^6 c_{\psi^2H^3}$". Several dim-10 and one dim-8 entry ($H^4X^2$ at 6-point) are wrapped in explicit `\textcolor{black}` which renders as plain (tree). Whether $H^4X^2$ is meant to be tree-level (while $H^2X^2$ at dim-6 is loop-only) should be confirmed against `Craig:2019wmo`.
- **Q11 (VBF Table 1 index mismatch).** $Q^{(1,3)}_{H\psi}$ are written with $\gamma^\nu$ and $\overleftrightarrow D_\mu$; standard Warsaw has both $\mu$.
- **Q12 (VBF Table 4 mixed $\tau^I/\sigma^I$).** $Q^{(3)}_{\psi^2H^2D^3}$ uses $\tau^I$ in one term and $\sigma^I$ in the other; same matrix intended.
- **Q13 (dim-10 tree/loop).** LC explicitly gives no tree/loop labels at dim-10, so any extension of the automated basis beyond dim-8 cannot inherit the coding.
