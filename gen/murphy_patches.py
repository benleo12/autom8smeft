"""
gen/murphy_patches.py  --  explicit, documented corrections to the LaTeX source of the
published tables (Murphy 2005.00059 v6) that are needed before parsing.

Every entry is applied by label (or by table) and logged.  Nothing is patched silently.
These are candidate errata for the published paper and are listed in the appendix of ours.
The physics intent in every case is unambiguous from the surrounding table and the text.
"""

import re

# (label regex, pattern, replacement, reason)
PATCHES = [
    # Class 13 (psi^2 H^4 D), whole table: the first fermion of every bilinear lacks \bar in
    # the source, e.g. "(l_p \gamma^{\mu} l_r)" for what must be (\bar l_p gamma^mu l_r)
    # (hypercharge and Lorentz structure leave no alternative; the text Eq. (q2H4D) and the
    # dimension-6 analogue Q_{Hl}^{(1)} confirm).
    (r"^Q_\{([lequd]\^2|ud)H\^4D\}", r"\(\s*([lequd])_p", r"(\\bar \1_p", "missing \\bar on first fermion (class 13 table)"),
    # Q_{leq^2HD}^{(6)}: gamma^\nu contracted with D_\mu; must be gamma^\mu (cf. (5) and the
    # rest of the class-20 table, all of which have gamma^mu D_mu)
    (r"^Q_\{leq\^2HD\}\^\{\(6\)\}$", r"\\gamma\^\\nu", r"\\gamma^\\mu", "gamma^nu should be gamma^mu (index mismatch)"),
    # Q_{qud^2HD}^{(4)}: a stray "$" inside the math closes the formula early in the source
    (r"^Q_\{qud\^2HD\}\^\{\(4\)\}$", r"\\widetilde H\$\]", r"\\widetilde H]", "stray $ before ]"),
    # Q_{qud^2HD}^{(6)}: stray trailing backslash in the source line
    (r"^Q_\{qud\^2HD\}\^\{\(6\)\}$", r"\\\s*$", r"", "stray trailing backslash"),
    # Two B-violating rows of class 18 write a bilinear of two unbarred fields without the
    # charge-conjugation matrix that every other row of the table carries and that the
    # Lorentz structure requires: (l_p^j q_r^{m alpha}) and (e_p d_r^alpha).
    (r"^Q_\{lqd\^2H\^2\}$", r"\(l_p\^j q_r", r"(l_p^j C q_r", "missing C in (l q) bilinear (class 18 table)"),
    (r"^Q_\{eq\^2dH\^2\}$", r"\(e_p d_r", r"(e_p C d_r", "missing C in (e d) bilinear (class 18 table)"),
]

# label corrections (the operator itself is fine, the name in the table is not)
LABEL_PATCHES = {
    # class 11 psi^2 H^2 D^3: the fourth q-type row is labelled with D^2 in the source
    "Q_{q^2H^2D^2}^{(4)}": "Q_{q^2H^2D^3}^{(4)}",
}


def patch_label(label: str) -> str:
    return LABEL_PATCHES.get(label, label)


def apply_patches(label: str, latex: str, log: list | None = None) -> str:
    out = latex
    for lab_re, pat, rep, why in PATCHES:
        if re.search(lab_re, label):
            new = re.sub(pat, rep, out)
            if new != out:
                if log is not None:
                    log.append(dict(label=label, before=out, after=new, reason=why))
                out = new
    return out
