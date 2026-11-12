#!/usr/bin/env python3
"""Where every number of a study comes from, and the check the table and figure scripts make
before they write anything.

    examples/studies/provenance.py check <results.tsv> [<results.tsv> ...]
    examples/studies/provenance.py recover <results.tsv> [--search DIR ...] [--model PREFIX=DIR ...]
    examples/studies/provenance.py attest <results.tsv> <same_couplings.tsv> [<same_couplings.tsv> ...]
    examples/studies/provenance.py model <model dir> [restriction card]
    examples/studies/provenance.py lhe <results.tsv> <process> <restriction card or ""> <order>
    examples/studies/provenance.py signed <results.tsv> [<results.tsv> ...]

run_study.sh keeps beside each results file a record of every one of its rows, records.tsv beside
results.tsv and records_<x>.tsv beside results_<x>.tsv.  A record names

  the model    its name, the sha256 of the UFO's python files, which are what MadGraph imports (the
               pickle it caches beside them is rebuilt from them), the sha256 of the release archive
               models/<name>.tar.xz when the directory holds exactly the files of the release's list
               models/<name>.sha256, and the sha256 of the restriction card, with a copy of that card in
               <study>/cards/<sha256>.restrict.dat.gz,
  MadGraph     its version, and the import and generate commands of the run,
  the cards    a hash of the entries of the param card and of the run card as the run used them, with
               a copy of each in <study>/cards/ under that hash, and the values the check reads off
               them (Lam and the values of the dimension-eight coefficients, the run-card entries
               that run_study.sh and processes.txt set),
  the result   the cross section and error of the row, its event file and that file's sha256, the
               integrated weight and error MadGraph wrote into the file's header, and the error of the
               cross section that the signed weights of the events give.

A card is hashed by its entries (block, indices and value, or name and value, sorted) and not by its
bytes, so the copy MadGraph writes into the header of an event file and the file in Cards/ have one
hash although their comments differ.  A card shared by many runs is stored once.

`check` stops with a list of what disagrees, unless
  - every row has one record, and the row's cross section, error, event count, settings and event
    file are the record's,
  - the record's cross section and error are those of the event file's header, and the event file
    is the recorded one (its sha256) wherever the study's lhe/ directory is present,
  - the cards agree with the row, read from their copies in cards/: Lam is the settings' Lam, every
    dimension-eight coefficient has the value the settings give it, the coefficients present are those
    the restriction card of the model column keeps, the run generated the row's process at the row's
    order, its event count is the row's, and its beam energies, scale choice and cuts are those of
    run_study.sh and processes.txt,
  - the rows come from one model version, one hash of the UFO's files, and the rows of one restriction
    card from one version of that card, one sha256,
  - that model version is the release's: the hash of the python files that the release's list
    models/<name>.sha256 gives, so that no archive is unpacked for the check.
MadGraph takes the error of a cross section from the absolute values of the weights of its phase-space
points, so the error it quotes for a term with weights of both signs, an interference, is too small.  The
events of a row are drawn from at least as many points as there are events, so the error of the signed cross
section is at most the quoted error and the error of the mean of the signed event weights added in quadrature
(mc_error), and that bound is what the tables compare with a tenth of an entry.  For a square, whose weights
have one sign, the second term vanishes.  `signed` writes that error into the records of rows run before
the records had it, from their event files, each the recorded one (its sha256).

A decay (one particle in, such as z > e+ e-) is not integrated.  run_study.sh evaluates MadGraph's standalone
matrix element with examples/studies/decay_width.f, and the row's file is that program's printout,
lhe/<tag>.width.txt, in place of an event file.  For such a row the check computes the width again from the
printout, |M|^2 |p| / (8 pi M^2), checks that the matrix element is the same along the three directions it was
evaluated in, and that the row has no event count and its record no run card (the standalone output has one,
which its matrix element does not read).
A row with a number and no event file cannot be checked and stops the check, and so does a card whose
copy is missing.  A row whose settings set_cards.py refused (BAD_SETTING) was never run, and set_cards.py
leaves both of its cards as MadGraph wrote them, so they are not compared with its settings.  Event files
are not shipped with the repository, so where a study has no lhe/ directory the check reads the header
values the record carries, and says that it did.  A row run with another model version or another
version of its restriction card counts as the table's only after `attest` has written into its record
that validate/same_couplings.py found the two models equal, at the values of the row's cards and in
every vertex that a tree diagram of the row's process can contain, with the second model restricted by
its own card of that name.

`recover` writes the records of rows run before run_study.sh kept them, from what the runs left
behind.  MadGraph writes the proc card, the run card, the param card and the integrated weight into
the header of every event file.  An event file is looked for under the row's file name in the study's
lhe/ and in every lhe/ directory below each --search directory, and it is the row's only if its
header has the row's cross section and error, process, order and model.  A row with no event file
of its own (no diagram, a failure) is matched to a results file below a --search directory that has
the same row.  --model PREFIX=DIR says that a run whose import path starts with PREFIX used the model
in DIR, which gives the record its model hash, and it is taken only when every entry of the header's
param card is an entry of that model's restriction card.  PREFIX matches an import path that is PREFIX or
goes on below it, after a '/' or a '-'.  Each matched event file is copied into the study's lhe/ under the
row's name, unless the file there is the event file of another row of a results file of the study, and the
rows that cannot be traced are listed.

A recovered record says so in its identity column.  Its model and card are those --model names for the
run's import path, which nothing the run left confirms (two builds with one parameter layout have the same
param card), while run_study.sh measures them at the run.  `check` therefore refuses a recovered row until
`attest` has tied it, through a comparison by validate/same_couplings.py of that model with another one, to
the model of the table, and it refuses a recovered row with no event file in every case: it has to be run
again.
"""
import contextlib, fcntl, glob, gzip, hashlib, math, os, re, shutil, sys, tempfile, time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

COLS = ["process", "model", "order", "sigma_pb", "error_pb", "nevents", "settings", "lhe",
        "lhe_sha256", "lhe_sigma_pb", "lhe_error_pb", "lhe_signed_error_pb", "mg5", "model_sha256", "release_sha256",
        "card_sha256", "import", "generate", "param_card", "run_card", "dim8", "run", "same_as", "same_card", "source",
        "identity"]
ROW = ["process", "model", "order", "sigma_pb", "error_pb", "nevents", "settings", "lhe"]
# the run-card entries run_study.sh sets on every run; processes.txt adds the cuts of a process
DRIVER_RUN = {"ebeam1": "6800", "ebeam2": "6800", "dynamical_scale_choice": "3", "hel_recycling": "False"}
# The cuts of MadGraph's leading-order run card with the values it writes them at (RunCardLO of
# madgraph/various/banner.py, 3.5).  A cut of a run card that processes.txt does not set for the process must
# have this value, so that a cut nobody asked for, or one processes.txt no longer gives, is seen.
CUT_DEFAULTS = dict(
    [(n, "20.0" if n == "ptj" else "10.0" if n in ("pta", "ptl") else "0.0")
     for n in ("ptj", "ptb", "pta", "ptl", "misset", "ptheavy", "ej", "eb", "ea", "el", "etajmin", "etabmin", "etaamin",
               "etalmin", "drbb", "drbj", "drab", "drbl", "mmjj", "mmbb", "mmaa", "mmll", "mmnl", "ptllmin", "xptj", "xptb",
               "xpta", "xptl", "ptj1min", "ptj2min", "ptj3min", "ptj4min", "cutuse", "ptl1min", "ptl2min", "ptl3min",
               "ptl4min", "htjmin", "ihtmin", "ht2min", "ht3min", "ht4min", "ptgmin", "xetamin", "deltaeta", "xqcut",
               "dsqrt_shat")]
    + [(n, "-1.0") for n in ("ptjmax", "ptbmax", "ptamax", "ptlmax", "missetmax", "ejmax", "ebmax", "eamax", "elmax", "etab",
                             "drjjmax", "drbbmax", "drllmax", "draamax", "drbjmax", "drajmax", "drjlmax", "drabmax", "drblmax",
                             "dralmax", "mmjjmax", "mmbbmax", "mmaamax", "mmllmax", "mmnlmax", "ptllmax", "ptj1max", "ptj2max",
                             "ptj3max", "ptj4max", "ptl1max", "ptl2max", "ptl3max", "ptl4max", "htjmax", "ihtmax", "ht2max",
                             "ht3max", "ht4max", "ktdurham", "ptlund")]
    + [(n, "0.4") for n in ("drjj", "drll", "draa", "draj", "drjl", "dral", "dparameter")]
    + [("etaj", "5.0"), ("etaa", "2.5"), ("etal", "2.5"), ("cut_decays", "False")]
    + [(n, "{}") for n in ("pt_min_pdg", "pt_max_pdg", "e_min_pdg", "e_max_pdg", "eta_min_pdg", "eta_max_pdg", "mxx_min_pdg")])
WORDS = {"NO_DIAGRAMS", "NO_OUTPUT", "BAD_SETTING", "FAILED", "ZERO", "NOT_INTEGRATED"}
NUM = r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?"


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _put(path, data):
    """Write the bytes data to path through a temporary file of its own in the same directory, renamed into
    place, so that two writers of one file never share a temporary file and a reader never sees half of one."""
    fd, t = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(path)), prefix=os.path.basename(path) + ".", suffix=".part")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        os.chmod(t, 0o644)
        os.replace(t, path)
    except BaseException:
        if os.path.exists(t):
            os.remove(t)
        raise


@contextlib.contextmanager
def records_lock(path):
    """An exclusive lock on the study directory of a records file, held by every writer of its records:
    append_record (run_study.sh), and the rewrites of attest, recover and merge_rows.py, which read the
    file, change it and write it back.  A record appended while a rewrite runs would otherwise be lost."""
    fd = os.open(os.path.dirname(os.path.abspath(path)), os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        os.close(fd)


def records_path(results):
    """records.tsv beside results.tsv, records_<x>.tsv beside results_<x>.tsv."""
    d, b = os.path.split(os.path.abspath(results))
    return os.path.join(d, ("records" + b[len("results"):]) if b.startswith("results") else "records_" + b)


# ---------------------------------------------------------------------------------------------
# the model


def ufo_hashes(model_dir):
    return {f: sha256_file(os.path.join(model_dir, f)) for f in sorted(os.listdir(model_dir))
            if f.endswith(".py") and os.path.isfile(os.path.join(model_dir, f))}


def model_id(model_dir, card=""):
    """(model hash, release archive sha256 or '-', restriction-card sha256 or '-') of a model
    directory.  The model hash is the sha256 of the list of its python files with their sha256."""
    hashes = ufo_hashes(model_dir)
    mh = hashlib.sha256("".join(f"{h}  {f}\n" for f, h in sorted(hashes.items())).encode()).hexdigest()
    rc = os.path.join(model_dir, f"restrict_{card}.dat") if card else ""
    ch = sha256_file(rc) if card and os.path.isfile(rc) else "-"
    return mh, release_of(model_dir, hashes, card, ch), ch


def release_of(model_dir, hashes, card, card_hash):
    """The sha256 of models/<name>.tar.xz when the directory is that release: its python files are
    those of the release's list <name>.sha256, no more and no fewer, and so is its restriction card
    where the release has one of that name.  '-' otherwise, a model built or edited locally."""
    name = os.path.basename(os.path.normpath(model_dir))
    for d in (os.path.dirname(os.path.normpath(model_dir)), os.path.join(ROOT, "models")):
        lst, arc = os.path.join(d, name + ".sha256"), os.path.join(d, name + ".tar.xz")
        if not (os.path.isfile(lst) and os.path.isfile(arc)):
            continue
        rel = {}
        for l in open(lst):
            w = l.split(None, 1)
            if len(w) == 2 and w[1].strip().startswith(name + "/"):
                rel[w[1].strip()[len(name) + 1:]] = w[0]
        if {f: h for f, h in rel.items() if f.endswith(".py") and "/" not in f} != hashes:
            continue
        if card and f"restrict_{card}.dat" in rel and rel[f"restrict_{card}.dat"] != card_hash:
            continue
        return sha256_file(arc)
    return "-"


_released = {}


def released_version(base):
    """(model hash, where it was read) of the released model <base>: from its list models/<base>.sha256, the
    sha256 of the "hash  file" lines of its top-level python files, which is the hash model_id gives the
    unpacked release, so that no archive has to be unpacked; else, in a tree that holds the release unpacked
    and no list (the public tree before publish.sh packs it), the hash of models/<base>/.  (None, why) when
    neither is there."""
    md = model_dir_of(base)
    if (base, md) not in _released:
        lst = os.path.join(os.path.dirname(md), base + ".sha256")
        out = (None, f"neither models/{base}.sha256, the list of the release, nor models/{base}/")
        if os.path.isfile(lst):
            rel = {}
            for line in open(lst):
                w = line.split(None, 1)
                f = w[1].strip()[len(base) + 1:] if len(w) == 2 and w[1].strip().startswith(base + "/") else ""
                if f.endswith(".py") and "/" not in f:
                    rel[f] = w[0]
            out = ((hashlib.sha256("".join(f"{h}  {f}\n" for f, h in sorted(rel.items())).encode()).hexdigest(), f"models/{base}.sha256")
                   if rel else (None, f"models/{base}.sha256 lists no python file of {base}"))
        elif os.path.isdir(md) and any(f.endswith(".py") for f in os.listdir(md)):
            out = (model_id(md)[0], f"models/{base}/")
        _released[(base, md)] = out
    return _released[(base, md)]


def release_problems(rows, what):
    """The rows [(where, model column, (model version, card version))] that do not count as rows of the released
    model their model column names: their version, the run's or the one `attest` found equal to it, is not
    the release's."""
    out, by = [], {}
    for where, model, (mv, cv) in rows:
        by.setdefault(model.partition("-")[0], []).append((where, mv))
    for base, rs in sorted(by.items()):
        rv, how = released_version(base)
        if rv is None:
            out.append(f"{what} of {base} cannot be tied to a released model: {how}")
            continue
        off = [(w, v) for w, v in rs if v != rv]
        if off:
            out.append(f"{what}: {len(off)} rows of {base} come from model {off[0][1][:12]} (e.g. {off[0][0]}), and the release "
                       f"is model {rv[:12]} ({how}); rerun them, or compare the two models at their cards "
                       "(validate/same_couplings.py, then provenance.py attest)")
    return out


# ---------------------------------------------------------------------------------------------
# the cards


def param_entries(text):
    """{(block, indices): (value, name)} of an SLHA param card; a width is block 'decay'.  The name
    is the first word of the comment, or the whole comment where MadGraph marks a value it fixed
    itself ("d : 0.0" for a massless quark)."""
    out, block = {}, None
    for line in text.splitlines():
        body, _, c = line.partition("#")
        c = c.split()
        name = " ".join(c) if len(c) > 1 and c[1] == ":" else (c[0] if c else "")
        w = body.split()
        if not w:
            continue
        if w[0].lower() == "block":
            block = w[1].lower() if len(w) > 1 else None
        elif w[0].lower() == "decay" and len(w) > 2:
            block = None
            out[("decay", (w[1],))] = (w[2], name.split(" : ")[0])
        elif block:
            out[(block, tuple(w[:-1]))] = (w[-1], name)
    return out


def run_entries(text):
    """{name: value} of a MadGraph run card, from its "value = name ! comment" lines."""
    out = {}
    for line in text.splitlines():
        s = line.split("!", 1)[0]
        if s.lstrip().startswith("#") or "=" not in s:
            continue
        v, n = s.rsplit("=", 1)
        if re.fullmatch(r"\s*\w+\s*", n):
            out[n.strip().lower()] = v.strip()
    return out


def canon(v):
    try:
        return repr(float(v))
    except ValueError:
        return v.strip()


def card_hash(entries):
    """sha256 of a card's entries, one per line and sorted, so that a reformatted copy hashes alike."""
    if entries and isinstance(next(iter(entries)), tuple):
        lines = [f"{b} {' '.join(i)} {canon(v)}" for (b, i), (v, _) in entries.items()]
    else:
        lines = [f"{n} = {canon(v)}" for n, v in entries.items()]
    return hashlib.sha256("\n".join(sorted(lines)).encode()).hexdigest()


def store_card(study, text, kind):
    """Keep a copy of a card in <study>/cards/<hash>.<kind>_card.dat.gz and return its hash."""
    e = param_entries(text) if kind == "param" else run_entries(text)
    h = card_hash(e)
    p = os.path.join(study, "cards", f"{h}.{kind}_card.dat.gz")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        _put(p, gzip.compress(text.encode()))
    return h


def load_card(study, h, kind):
    p = os.path.join(study, "cards", f"{h}.{kind}_card.dat.gz")
    if h in ("", "-") or not os.path.exists(p):
        return None
    with gzip.open(p, "rt") as f:
        return f.read()


def store_restriction(study, model_dir, card, h):
    """Keep a copy of the restriction card a row was imported with in <study>/cards/<sha256>.restrict.dat.gz,
    so that the check reads the coefficients it keeps wherever the model directory is, and whatever card
    of that name the model there carries now."""
    src = os.path.join(model_dir, f"restrict_{card}.dat") if card else ""
    if h in ("", "-") or not src or not os.path.isfile(src) or sha256_file(src) != h:
        return
    p = os.path.join(study, "cards", f"{h}.restrict.dat.gz")
    if not os.path.exists(p):
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(src, "rb") as f:
            _put(p, gzip.compress(f.read()))


def load_restriction(study, h, base, card, model_dir=None):
    """The text of the restriction card of sha256 h: the copy in <study>/cards/, or else the card of the model
    directory (models/<base> unless model_dir is given) when it is that file.  None when neither is."""
    p = os.path.join(study, "cards", f"{h}.restrict.dat.gz")
    if h not in ("", "-") and os.path.exists(p):
        with gzip.open(p, "rb") as f:
            b = f.read()
        if hashlib.sha256(b).hexdigest() == h:
            return b.decode()
    rp = os.path.join(model_dir or model_dir_of(base), f"restrict_{card}.dat")
    if h not in ("", "-") and os.path.isfile(rp) and sha256_file(rp) == h:
        return open(rp).read()
    return None


def is_c8(name):
    n = re.sub(r"__\d+$", "", name).lower()
    return n.startswith("c8") and n != "lam"


def dim8_summary(entries):
    """'Lam=3000 c8=1:57': Lam, and how many dimension-eight coefficients the card has at each value."""
    lam, vals = None, {}
    for (b, i), (v, n) in entries.items():
        if n.lower() == "lam":
            lam = v
        elif is_c8(n):
            k = f"{float(v):g}"
            vals[k] = vals.get(k, 0) + 1
    out = f"Lam={float(lam):g}" if lam is not None else "Lam=-"
    return out + " c8=" + (",".join(f"{k}:{vals[k]}" for k in sorted(vals, key=float)) if vals else "-")


def run_summary(entries, extra_names=()):
    names = list(DRIVER_RUN) + ["nevents", "sde_strategy"] + [n for n in extra_names if n not in DRIVER_RUN]
    return " ".join(f"{n}={entries[n].replace(' ', '')}" for n in dict.fromkeys(names) if n in entries)


# ---------------------------------------------------------------------------------------------
# event files


def lhe_header(path):
    """What MadGraph writes into the header of an event file: its version, the proc, run and param
    cards, the integrated weight, and the cross section and error of the <init> block (summed over
    its processes, the errors in quadrature)."""
    op = gzip.open if path.endswith(".gz") else open
    tags = {"<MGVersion>": "mg5", "<MG5ProcCard>": "proc", "<MGRunCard>": "run", "<slha>": "param", "<init>": "init"}
    out = {"mg5": "-", "proc": "", "run": "", "param": "", "xsec": None, "init": None}
    sect, buf = None, []
    with op(path, "rt", errors="replace") as f:
        for line in f:
            t = line.strip()
            if t.startswith("<event"):
                break
            if t in tags:
                sect, buf = tags[t], []
                continue
            if sect and t.startswith("</"):
                if sect == "init":
                    rows = [[float(x) for x in l.split()] for l in buf[1:] if l.strip() and not l.lstrip().startswith("<")]
                    out["init"] = (sum(r[0] for r in rows), sum(r[1] ** 2 for r in rows) ** 0.5) if rows else None
                elif sect == "mg5":
                    out["mg5"] = "".join(buf).strip().lstrip("#").strip() or "-"
                else:
                    out[sect] = "".join(l for l in buf if l.strip() not in ("<![CDATA[", "]]>"))
                sect = None
                continue
            if sect:
                buf.append(line)
            m = re.search(r"Integrated weight \(pb\)\s*:\s*(" + NUM + ")", line)
            if m:
                out["xsec"] = float(m.group(1))
    return out


def signed_error(path, run_text):
    """The error of the cross section that the signed event weights of an event file give: sqrt(N var(w)) / N for
    weights normalised to their average (MadGraph's event_norm = average, its default), sqrt(N var(w)) for
    event_norm = sum, with the event_norm of the run card of the file's header."""
    norm = run_entries(run_text).get("event_norm", "average").strip().lower() if run_text else "average"
    if norm not in ("average", "sum"):
        raise ValueError(f"{path}: event_norm = {norm}, whose weights do not add up to a cross section")
    n = s = s2 = 0.0
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", errors="replace") as f:
        head = False
        for line in f:
            t = line.lstrip()
            if t.startswith("<event>") or t.startswith("<event "):
                head = True
            elif head:
                if t.startswith("<") or len(t.split()) < 3:
                    raise ValueError(f"{path}: an event with no first line, which holds its weight")
                w = float(t.split()[2])   # XWGTUP, the third number of the event's first line
                n, s, s2, head = n + 1, s + w, s2 + w * w, False
    if not n:
        return 0.0
    e = math.sqrt(n * max(s2 / n - (s / n) ** 2, 0.0))
    return e / n if norm == "average" else e


def mc_error(err, rec):
    """An upper bound on the Monte Carlo error of a row's cross section, from its error err and its record: err
    and the error of its signed event weights added in quadrature (see the docstring of this module)."""
    e = _f((rec or {}).get("lhe_signed_error_pb", "-"))
    return math.hypot(err, e) if e is not None else err


WIDTH_LINES = {"mass of the decaying particle (GeV)": 1, "masses of the products (GeV)": 2,
               "momentum of a product (GeV)": 1, "width (GeV)": 1}


def width_printout(path):
    """What examples/studies/decay_width.f printed for a two-body decay, in the form of lhe_header: the width as
    xsec and init (width, 0), since it is exact, and under "problems" what disagrees in the printout, a line
    that is not one of the program's, a matrix element that depends on the direction of the decay, or a width
    that is not |M|^2 |p| / (8 pi M^2) of the numbers printed."""
    out = {"mg5": "-", "proc": "", "run": "", "param": "", "xsec": None, "init": None, "problems": []}
    bad = out["problems"].append
    v, me = {}, []
    for line in open(path, errors="replace"):
        name, eq, rest = line.strip().partition(" = ")
        if not line.strip():
            continue
        try:
            nums = [float(x) for x in rest.split()]
        except ValueError:
            nums = None
        if eq and nums and re.fullmatch(r"matrix element [123] \(GeV\^2, cos theta, phi\)", name) and len(nums) == 3:
            me.append(nums)
        elif eq and nums and WIDTH_LINES.get(name) == len(nums) and name not in v:
            v[name] = nums
        else:
            bad(f"a line that decay_width.f does not print: {line.strip()[:80]!r}")
    if len(me) != 3 or len(v) != len(WIDTH_LINES):
        bad(f"{len(me)} matrix elements and {len(v)} of the {len(WIDTH_LINES)} other lines of decay_width.f")
        return out
    if not all(math.isfinite(x) for n in list(v.values()) + me for x in n):
        bad("a number that is not finite")
        return out
    (M,), (m2, m3), (p,), (w,) = (v[n] for n in WIDTH_LINES)
    m1 = me[0][0]
    if max(abs(e[0] - m1) for e in me) > 1e-9 * abs(m1):
        bad("the matrix element depends on the direction of the decay: " + ", ".join(f"{e[0]:.10g}" for e in me))
    kl = (M * M - (m2 + m3) ** 2) * (M * M - (m2 - m3) ** 2)
    if kl <= 0 or abs(math.sqrt(kl) / (2 * M) - p) > 1e-12 * p:
        bad(f"the momentum {p} is not that of a decay of a mass {M} to {m2} and {m3}")
    elif abs(m1 * p / (8 * math.pi * M * M) - w) > 1e-12 * abs(w):
        bad(f"the width {w} is not |M|^2 |p| / (8 pi M^2) = {m1 * p / (8 * math.pi * M * M)}")
    out["xsec"], out["init"] = w, (w, 0.0)
    return out


def result_file(path):
    """The header of an event file, or what decay_width.f printed for a decay (lhe/<tag>.width.txt)."""
    return width_printout(path) if path.endswith(".width.txt") else lhe_header(path)


def is_decay(process):
    return len(process.partition(">")[0].split()) == 1


def proc_commands(text):
    """(import argument, generate argument) of a proc card, MadGraph's line continuations joined."""
    text = text.replace("\\\n", "")
    imp = [l.split(None, 2)[2].strip() for l in text.splitlines() if re.match(r"\s*import\s+model\s+\S", l)]
    gen = [l.split(None, 1)[1].strip() for l in text.splitlines() if re.match(r"\s*generate\s+\S", l)]
    return (imp[-1] if imp else "-"), (" ".join(gen[-1].split()) if gen else "-")


def mg5_version(mg_dir):
    try:
        m = re.search(r"version\s*=\s*(\S+)", open(os.path.join(mg_dir, "VERSION")).read())
        return m.group(1) if m else "-"
    except OSError:
        return "-"


# ---------------------------------------------------------------------------------------------
# writing records


def read_tsv(path):
    rows = [l.rstrip("\n").split("\t") for l in open(path) if l.strip()]
    return rows[0], rows[1:]


def key(r):
    return (r["process"].strip(), r["model"], r["order"])


def as_dict(head, row):
    return {h: (row[i] if i < len(row) else "") for i, h in enumerate(head)}


def write_records(path, recs):
    """Write a records file, every record (a dict) with the columns of COLS.  A caller that read the file
    first holds records_lock from the read to this write."""
    _put(path, ("\t".join(COLS) + "\n" + "".join("\t".join(str(rec.get(c, "-")) or "-" for c in COLS) + "\n"
                                                for rec in recs)).encode())


def read_records(path):
    """The records of a records file as dicts, [] when there is no such file."""
    if not os.path.exists(path):
        return []
    hr, recs = read_tsv(path)
    return [as_dict(hr, r) for r in recs]


def append_record(results, rec):
    p = records_path(results)
    with records_lock(p):
        if os.path.exists(p) and read_tsv(p)[0] != COLS:
            write_records(p, read_records(p))   # a file written before a column was added gets it, as "-"
        new = not os.path.exists(p)
        with open(p, "a") as f:
            if new:
                f.write("\t".join(COLS) + "\n")
            f.write("\t".join(str(rec.get(c, "-")) or "-" for c in COLS) + "\n")


def identity_of(rec):
    """How a record knows the model and restriction card of its run: "measured", the hashes of the directory
    MadGraph imported, taken by run_study.sh at the run, or "recovered", the directory that
    `recover --model` says a run's import path stood for, which nothing the run left can confirm.  A record
    written before the column existed says which through its source."""
    v = (rec.get("identity") or "-").strip()
    if v not in ("", "-"):
        return v
    return "recovered" if (rec.get("source") or "").startswith("recovered") else "measured"


def extras_of(study, process):
    """The run-card settings processes.txt gives a process (after its first '|'), {} if it has none."""
    p = os.path.join(study, "processes.txt")
    if not os.path.exists(p):
        return None
    for line in open(p):
        line = line.rstrip("\r\n")
        if not line.replace(" ", "") or line.lstrip().startswith("#"):
            continue
        proc, _, rest = line.partition("|")
        if " ".join(proc.split()) == " ".join(process.split()):
            return dict(t.split("=", 1) for t in rest.partition("|")[0].split() if "=" in t)
    return None


def fill_cards(rec, study, param_text, run_text, proc_text):
    ex = extras_of(study, rec["process"]) or {}
    if param_text:
        rec["param_card"] = store_card(study, param_text, "param")
        rec["dim8"] = dim8_summary(param_entries(param_text))
    if run_text:
        rec["run_card"] = store_card(study, run_text, "run")
        rec["run"] = run_summary(run_entries(run_text), ex)
    if proc_text:
        imp, gen = proc_commands(proc_text)
        rec["import"], rec["generate"] = os.path.basename(imp.rstrip("/")), gen


def record(argv):
    """record [--row] <results file> <row> <model dir> <card> <process dir> <run name> <MadGraph dir> <model id>
    The call run_study.sh makes for every row it writes, while the process directory still exists.  With
    --row it first appends the row to the results file, under the lock that merge_rows.py holds while it
    rewrites that file, so that a merge running meanwhile cannot drop the row."""
    if "--row" in argv:
        argv = [a for a in argv if a != "--row"]
        with records_lock(records_path(argv[0])):
            with open(argv[0], "a") as f:
                f.write(argv[1] + "\n")
    results, line, model, card, d, rn, mg = argv[:7]
    mid = argv[7:10] if len(argv) >= 10 else model_id(model, card)
    study = os.path.dirname(os.path.abspath(results))
    row = as_dict(read_tsv(results)[0], line.split("\t"))
    rec = {c: row[c] for c in ROW}
    rec.update(mg5=mg5_version(mg), model_sha256=mid[0], release_sha256=mid[1], card_sha256=mid[2], identity="measured",
               source="run_study.sh " + time.strftime("%Y-%m-%d %H:%M") + (f" {rn}" if rn not in ("-", "run_01") else ""))
    cards = os.path.join(d, "Cards")
    rd = lambda f: open(os.path.join(cards, f)).read() if os.path.exists(os.path.join(cards, f)) else ""
    proc = rd("proc_card_mg5.dat")
    if not proc and os.path.exists(d + ".mg5"):
        proc = open(d + ".mg5").read()   # no process directory (no diagrams): the commands run_study.sh gave MadGraph
    # the standalone output of a decay has a run card too, which its matrix element does not read
    param, run = rd("param_card.dat"), ("" if is_decay(rec["process"]) else rd("run_card.dat"))
    if rec.get("lhe", "-") != "-":
        p = os.path.join(study, rec["lhe"])
        h = result_file(p)
        rec["lhe_sha256"] = sha256_file(p)
        rec["lhe_sigma_pb"] = f"{h['xsec']:.10g}" if h["xsec"] is not None else "-"
        rec["lhe_error_pb"] = f"{h['init'][1]:.10g}" if h["init"] else "-"
        if not p.endswith(".width.txt"):
            rec["lhe_signed_error_pb"] = f"{signed_error(p, h['run']):.10g}"
        # the cards of the events are the ones MadGraph wrote into the header of the event file, since
        # Cards/run_card.dat no longer has the seed the run used once the run is over
        param, run = h["param"] or param, h["run"] or run
    fill_cards(rec, study, param, run, proc)
    store_restriction(study, model, card, rec["card_sha256"])
    append_record(results, rec)
    print(f"provenance: recorded {rec['process'].strip()} | {rec['model']} | {rec['order']} in {records_path(results)}")
    return 0


# ---------------------------------------------------------------------------------------------
# the check


def sig_digits(s):
    m = re.fullmatch(r"[-+]?(\d*)\.?(\d*)(?:[eE][-+]?\d+)?", s.strip())
    if not m:
        return None
    digits = (m.group(1) + m.group(2)).lstrip("0")
    return max(len(digits), 1)


def same_printed(s, x):
    """The number s as MadGraph printed it is x rounded to the digits s shows."""
    try:
        v = float(s)
    except (TypeError, ValueError):
        return False
    n = sig_digits(s)
    # nan and inf parse as numbers and are no cross section, and neither is a value with no digits
    if x is None or n is None or not (math.isfinite(v) and math.isfinite(x)):
        return False
    return float(f"{x:.{n}g}") == v or abs(x - v) <= 0.5 * 10 ** (int(f"{v:e}".split("e")[1]) - n + 1) * (1 + 1e-9)


def same_value(a, b):
    """Two card values compare as numbers, as booleans, as the numbers of two dictionaries or lists that
    MadGraph and processes.txt space differently ({25: 100.0} and {25:100}, {} and {}), and otherwise as words,
    so that nn23lo1 is not nn23nlo1."""
    a, b = a.strip(), b.strip()
    try:
        x, y = float(a), float(b)
        return abs(x - y) <= 1e-6 * max(abs(x), abs(y)) or x == y
    except ValueError:
        pass
    tf = {"true": True, ".true.": True, "t": True, "false": False, ".false.": False, "f": False}
    if a.lower() in tf and b.lower() in tf:
        return tf[a.lower()] == tf[b.lower()]
    if a[:1] in "{[(" and b[:1] in "{[(" and a[:1] == b[:1]:
        return [float(x) for x in re.findall(NUM, a)] == [float(x) for x in re.findall(NUM, b)]
    return a.replace(" ", "").lower() == b.replace(" ", "").lower()


def settings_of(s):
    return dict(t.split("=", 1) for t in s.split() if "=" in t)


def restriction_keeps(text):
    """The dimension-eight coefficients a restriction card keeps (its nonzero entries)."""
    return {n for (b, i), (v, n) in param_entries(text).items() if is_c8(n) and float(v) != 0}


def model_dir_of(name):
    return os.path.join(ROOT, "models", name)


def check_record(rec, row, study, have_lhe, problems, where):
    """Every disagreement between a row, its record, its event file and its cards, appended to problems."""
    bad = lambda what: problems.append(f"{where}: {what}")
    row = dict(row, lhe=row["lhe"].strip() or "-")   # an early results file left the field empty for no event file
    for c in ROW:
        if (row[c].strip() if c == "process" else row[c]) != (rec[c].strip() if c == "process" else rec[c]):
            bad(f"{c} is {row[c]!r} in the results file and {rec[c]!r} in the record")
    sig, lhe = row["sigma_pb"], row["lhe"]
    numeric = sig not in WORDS and sig != "-"
    if numeric and lhe == "-":
        bad("a cross section with no event file, so it cannot be traced to a run")
    decay = is_decay(row["process"])
    if lhe != "-" and decay != lhe.endswith(".width.txt"):
        bad(f"a {'decay' if decay else 'scattering process'} whose file {lhe} is "
            + ("not the printout of decay_width.f" if decay else "the printout of decay_width.f, which is for decays"))
    if lhe != "-":
        if not (same_printed(sig, _f(rec["lhe_sigma_pb"])) and same_printed(row["error_pb"], _f(rec["lhe_error_pb"]))):
            bad(f"the event file's header gives {rec['lhe_sigma_pb']} +- {rec['lhe_error_pb']} pb, the row {sig} +- {row['error_pb']}")
        if not decay and _f(rec.get("lhe_signed_error_pb", "-")) is None:
            bad("the record has no error of the signed event weights, which `provenance.py signed` writes from the event files")
        p = os.path.join(study, lhe)
        if have_lhe:
            if not os.path.exists(p):
                bad(f"the event file {lhe} is missing")
            elif sha256_file(p) != rec["lhe_sha256"]:
                bad(f"{lhe} is not the recorded event file (sha256 differs), it was overwritten by another run")
            else:
                h = result_file(p)
                for what in h.get("problems", []):
                    bad(f"{lhe}: {what}")
                e = _f(rec.get("lhe_signed_error_pb", "-"))
                if not decay and e is not None:
                    g = signed_error(p, h["run"])
                    if abs(g - e) > 1e-9 * max(abs(g), abs(e)):
                        bad(f"{lhe} gives {g:.10g} pb for the error of its signed event weights, the record {e:.10g}")
                if not (h["xsec"] is not None and same_printed(sig, h["xsec"]) and h["init"] and same_printed(row["error_pb"], h["init"][1])):
                    bad(f"{lhe} gives {h['xsec']} +- {h['init'][1] if h['init'] else '-'} pb")
    if rec["model_sha256"] in ("", "-"):
        bad("the record does not say which model version the row was run with")
    elif identity_of(rec) == "recovered":
        # `recover --model` took the model and restriction card from the run's import path, and nothing the
        # run left confirms them (a model that differs only in parameters.py has the same param card)
        if lhe == "-":
            bad(f"its model and restriction card were recovered ({rec.get('source', '-')}) with no event file, so "
                "nothing the run left says which model and card it used; run it again (examples/studies/run_study.sh, "
                "then merge_rows.py)")
        elif rec.get("same_as", "-") in ("", "-"):
            bad("its model and restriction card were recovered from the run's import path (provenance.py recover "
                "--model) and not measured, and no comparison with another model has tied the run to a model; "
                "compare its model with the table's at its cards (validate/same_couplings.py, then provenance.py "
                "attest) or run it again")
    if rec["mg5"] in ("", "-"):
        bad("the record does not say which MadGraph version ran the row")
    # the restriction card the run was imported with, read from its copy in cards/, so that the check does
    # not depend on which version of the model is in models/ when it runs.  A row with no diagrams needs it
    # too, since validate/same_couplings.py compares that row at the values of its card.
    base, _, rcard = row["model"].partition("-")
    keep = None
    if rcard:
        text = load_restriction(study, rec["card_sha256"], base, rcard)
        if text is None:
            bad(f"no copy of restrict_{rcard}.dat with the recorded sha256 {(rec['card_sha256'] or '-')[:12]} in cards/ "
                f"or models/{base}/, so the coefficients it keeps cannot be compared with the param card")
        else:
            keep = {re.sub(r"__\d+$", "", n).lower() for n in restriction_keeps(text)}
    sc = rec.get("same_card", "-") or "-"
    if sc != "-" and (not rcard or load_restriction(study, sc, base, rcard) is None):
        bad(f"the record counts the row as one run with the restriction card {sc[:12]}, and cards/ has no copy of that card")
    # the run itself: the model column's model and card, the row's process at the row's order.  A row with no
    # diagrams has them too, from the commands run_study.sh gave MadGraph.
    if rec["import"] not in ("", "-") and rec["import"] != row["model"]:
        bad(f"the run imported {rec['import']}, the row says {row['model']}")
    want = " ".join((row["process"] + " " + ("NP=0" if row["order"] == "NP=0 on" else row["order"])).split())
    if rec["generate"] in ("", "-"):
        bad("the record has no generate command")
    elif rec["generate"] != want:
        bad(f"the run generated {rec['generate']!r}, the row is {want!r}")
    if sig in {"NO_DIAGRAMS", "NO_OUTPUT"}:
        return   # MadGraph never wrote cards for these
    if sig == "BAD_SETTING":
        return   # set_cards.py refused the settings and left both cards as MadGraph wrote them, so nothing was run
    # the param card against the settings column and the restriction card
    if rec["param_card"] in ("", "-") or rec["dim8"] in ("", "-"):
        bad("the record has no param card")
    elif (pt := load_card(study, rec["param_card"], "param")) is None:
        bad(f"no copy of the param card {rec['param_card'][:12]} in cards/, so the values of its coefficients "
            "cannot be compared with the settings and the restriction card")
    else:
        e = param_entries(pt)
        if card_hash(e) != rec["param_card"]:
            bad(f"cards/{rec['param_card']}.param_card.dat.gz is not the card of that hash")
        if dim8_summary(e) != rec["dim8"]:
            bad(f"the param card gives {dim8_summary(e)}, the record {rec['dim8']}")
        s = settings_of(row["settings"])
        lam = re.search(r"Lam=(\S+)", rec["dim8"]).group(1)
        if "Lam" in s and not same_value(s["Lam"], lam):
            bad(f"the param card has Lam = {lam}, the settings {s['Lam']}")
        named = {k.lower(): v for k, v in s.items() if k not in ("dim8_all", "Lam")}
        names = {re.sub(r"__\d+$", "", n).lower(): v for (b, i), (v, n) in e.items()}
        for k, v in named.items():
            if k in names and not same_value(names[k], v):
                bad(f"{k} is {names[k]} in the param card, {v} in the settings")
        if "dim8_all" in s:
            off = [n for n, v in names.items() if is_c8(n) and n not in named and not same_value(v, s["dim8_all"])]
            if off:
                bad(f"dim8_all={s['dim8_all']} but {len(off)} dimension-eight coefficients differ, {', '.join(sorted(off)[:4])}")
        # the coefficients present are those the restriction card of the model column keeps
        c8 = {n for n in names if is_c8(n)}
        if keep is not None and c8 != keep:
            bad(f"the param card has {len(c8)} dimension-eight coefficients, restrict_{rcard}.dat keeps {len(keep)}")
    # a decay is evaluated at one phase-space point, with no run card and no events
    if decay:
        if row["nevents"] != "-":
            bad(f"a decay has no event count, the row has {row['nevents']}")
        if rec["run_card"] not in ("", "-"):
            bad("a decay has no run card, and the record names one")
        return
    # the run card against the driver, the row's event count and processes.txt
    if rec["run_card"] in ("", "-"):
        bad("the record has no run card")
        return
    rt = load_card(study, rec["run_card"], "run")
    if rt is None:
        bad(f"no copy of the run card {rec['run_card'][:12]} in cards/, so the run's event count, beams, scale and "
            "cuts cannot be compared with the row")
        return
    run = run_entries(rt)
    if card_hash(run) != rec["run_card"]:
        bad(f"cards/{rec['run_card']}.run_card.dat.gz is not the card of that hash")
    want = dict(DRIVER_RUN)
    want["nevents"] = row["nevents"]
    ex = extras_of(study, row["process"])
    if ex is None:
        bad(f"{'processes.txt does not list ' + row['process'].strip() if os.path.exists(os.path.join(study, 'processes.txt')) else 'the study has no processes.txt'}"
            ", so the cuts of the run card cannot be compared with the cuts the study gives the process")
    want.update({k.lower(): v for k, v in (ex or {}).items()})
    for k, v in want.items():
        if k == "sde_strategy":
            continue   # run_study.sh may rerun a row with sde_strategy=2, which changes the sampling only
        if k not in run:
            bad(f"the run card has no {k}, which should be {v}")
        elif not same_value(run[k], v):
            bad(f"{k} is {run[k]} in the run card, {v} for this row")
    # and the other way round: a cut of the run card that processes.txt does not set has MadGraph's value
    if ex is not None:
        for k, v in sorted(run.items()):
            if k in CUT_DEFAULTS and k not in want and not same_value(v, CUT_DEFAULTS[k]):
                bad(f"{k} is {v} in the run card, and processes.txt sets no {k} for {row['process'].strip()} "
                    f"(MadGraph writes {CUT_DEFAULTS[k]})")


def _f(s):
    try:
        return float(s)
    except (TypeError, ValueError):
        return None


def version_of(rec):
    """(model version, restriction-card version) a row counts as: those of its run, or those of the model and
    card that `attest` found equal to its run at the couplings."""
    attested = rec.get("same_card", "-") not in ("", "-")
    mv = rec["same_as"] if rec.get("same_as", "-") not in ("", "-") else rec["model_sha256"]
    return mv, (rec["same_card"] if attested else rec.get("card_sha256", "-") or "-")


def mixed_versions(rows, what):
    """The disagreements of a set of rows [(where, model column, (model version, card version))]: more than one
    model version, or, for a restriction card, more than one version of that card."""
    out, models, cards = [], {}, {}
    for where, model, (mv, cv) in rows:
        models.setdefault(mv, []).append(where)
        if "-" in model:
            cards.setdefault(model, {}).setdefault(cv, []).append(where)
    if len(models) > 1:
        out.append(f"{what} come from {len(models)} model versions: "
                   + "; ".join(f"{v[:12]} ({len(w)} rows, e.g. {w[0]})" for v, w in models.items()))
    for model, by in sorted(cards.items()):
        if len(by) > 1:
            out.append(f"{what} of {model} come from {len(by)} versions of restrict_{model.partition('-')[2]}.dat: "
                       + "; ".join(f"{v[:12]} ({len(w)} rows, e.g. {w[0]})" for v, w in by.items())
                       + ", and no comparison at the couplings has made them one")
    return out


def check(results, problems=None, quiet=False):
    """Check one results file against its records; returns {row key: (model version, card version)} and
    appends every disagreement to problems."""
    problems = [] if problems is None else problems
    study = os.path.dirname(os.path.abspath(results))
    rel = os.path.relpath(results, ROOT) if os.path.abspath(results).startswith(ROOT) else results
    rp = records_path(results)
    if not os.path.exists(rp):
        problems.append(f"{rel}: no records file {os.path.basename(rp)}, so no row can be traced to a run")
        return {}
    hr, recs = read_tsv(rp)
    hd, rows = read_tsv(results)
    byk = {}
    for r in recs:
        d = as_dict(hr, r)
        byk.setdefault(key(d), []).append(d)
    have_lhe = os.path.isdir(os.path.join(study, "lhe"))
    if not have_lhe and not quiet:
        print(f"provenance: {rel} has no lhe/ directory, so the event files are checked through their recorded headers only", file=sys.stderr)
    seen, versions = {}, {}
    for n, r in enumerate(rows, start=2):
        d = as_dict(hd, r)
        k = key(d)
        where = f"{rel} line {n} ({k[0]} | {k[1]} | {k[2]})"
        if k in seen:
            problems.append(f"{where}: the same process, model and order as line {seen[k]}, and a table would take either")
            continue
        seen[k] = n
        rs = byk.get(k, [])
        if len(rs) != 1:
            problems.append(f"{where}: {'no record' if not rs else str(len(rs)) + ' records'}")
            continue
        check_record(rs[0], d, study, have_lhe, problems, where)
        versions[k] = version_of(rs[0])
    return versions


def require(results_files, what):
    """Stop unless every row of these results files checks out, all of them come from one model version,
    and the rows of each restriction card from one version of that card; return the model version.  The
    table and figure scripts call this before writing anything."""
    problems, rows = [], []
    for f in results_files:
        for k, v in check(f, problems).items():
            rows.append((f"{_rel(f)}: {' | '.join(k)}", k[1], v))
    problems += mixed_versions(rows, "the rows") + release_problems(rows, "the rows")
    if problems:
        sys.exit(f"{what}: not written, the study data does not check out\n  " + "\n  ".join(problems[:40])
                 + (f"\n  ... and {len(problems) - 40} more" if len(problems) > 40 else "")
                 + "\n(examples/studies/provenance.py check <results.tsv> lists every disagreement)")
    return rows[0][2][0] if rows else None


def event_record(path):
    """(record, results file) of the study row whose event file this is.  Stops for a file that does not sit
    in the lhe/ directory of a study with records, and for one that no record of its study names, since
    nothing then says which run made it."""
    p = os.path.abspath(path)
    lhe_dir, study = os.path.dirname(p), os.path.dirname(os.path.dirname(p))
    if os.path.basename(lhe_dir) != "lhe":
        sys.exit(f"{path}: not in the lhe/ directory of a study, so no record says which run made it "
                 "(run_study.sh writes the event files of a study there, with their records)")
    if not any(f.startswith("records") and f.endswith(".tsv") for f in os.listdir(study)):
        sys.exit(f"{path}: the study {os.path.basename(study)} has no records file, so no record says which run made "
                 "this event file (provenance.py recover writes the records of rows run before they were kept)")
    h = sha256_file(p)
    for f in sorted(os.listdir(study)):
        if f.startswith("records") and f.endswith(".tsv"):
            for d in read_records(os.path.join(study, f)):
                if d["lhe"] != "-" and os.path.abspath(os.path.join(study, d["lhe"])) == p:
                    if d["lhe_sha256"] != h:
                        sys.exit(f"{path}: not the event file recorded in {f} (sha256 differs), it was overwritten by another run")
                    res = os.path.join(study, "results" + f[len("records"):])
                    if not os.path.exists(res):
                        sys.exit(f"{path}: recorded in {f}, and the study has no {os.path.basename(res)} beside it")
                    return d, res
    sys.exit(f"{path}: an event file of the study {os.path.basename(study)} that no record names")


def require_events(paths, what):
    """The check for a distribution: each event file is the one the record of a study row names, the
    results file holding that row checks out, and the files come from one model version and, for each
    restriction card, from one version of it.  Returns [(path, sha256, model version, results file)] for
    the sources file."""
    out, problems, rows, checked = [], [], [], {}
    for p in paths:
        rec, res = event_record(p)
        if res not in checked:
            checked[res] = check(res, problems, quiet=True)
        k = key(rec)
        if k not in checked[res]:
            problems.append(f"{_rel(p)}: its record ({' | '.join(k)}) is not that of a row of {_rel(res)}")
            continue
        rows.append((f"{_rel(res)}: {' | '.join(k)}", k[1], checked[res][k]))
        out.append((p, rec["lhe_sha256"], checked[res][k][0], res))
    problems += mixed_versions(rows, "the event files") + release_problems(rows, "the event files")
    if problems:
        sys.exit(f"{what}: not written\n  " + "\n  ".join(problems[:40]))
    return out


def sources_path(tsv):
    """<prefix>.sources.tsv for <prefix>_mVV.tsv or <prefix>_pT.tsv, the event files behind both."""
    return re.sub(r"_(mVV|pT)\.tsv$", "", tsv) + ".sources.tsv"


# the files plot_study.py writes for a prefix, which its sources file names with their sha256
TABLES = ("_mVV.tsv", "_pT.tsv", "_mVV_err.tsv", "_pT_err.tsv", "_mVV_R.tsv", "_stat.json")


def write_sources(prefix, labels, checked):
    """<prefix>.sources.tsv: for each column of the tables plot_study.py wrote for prefix, its event file with the
    file's sha256, the model version of its run and the results file of its row, and then each of those
    tables with its sha256, so that a figure is drawn only from a table those event files made."""
    lines = ["kind\tlabel\tpath\tsha256\tmodel_version\tresults"]
    lines += [f"events\t{label}\t{_rel(os.path.abspath(p))}\t{h}\t{v}\t{_rel(os.path.abspath(res)) if res != '-' else '-'}"
              for label, (p, h, v, res) in zip(labels, checked)]
    lines += [f"table\t-\t{_rel(os.path.abspath(prefix + s))}\t{sha256_file(prefix + s)}\t-\t-" for s in TABLES if os.path.exists(prefix + s)]
    _put(prefix + ".sources.tsv", ("\n".join(lines) + "\n").encode())


def _rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, ROOT) if a.startswith(ROOT + os.sep) else p


def _abs(p):
    """A path as a sources file writes it: relative to the top of the repository, or absolute outside it."""
    return os.path.abspath(p if os.path.isabs(p) else os.path.join(ROOT, p))


def _found(p, roots):
    """A path below a --search directory, from that directory's name on (studiesmw/diboson/...)."""
    a = os.path.abspath(p)
    for r in sorted(roots, key=len, reverse=True):
        if a.startswith(r.rstrip(os.sep) + os.sep):
            return os.path.relpath(a, os.path.dirname(r.rstrip(os.sep)))
    return _rel(p)


def require_sources(tsv, what, others=()):
    """The check for a figure drawn from a plot_study.py table: the sources file beside it names the table and
    the event files that made it.  The table, and each of `others` (the <prefix>_stat.json of its errors), must
    be the file plot_study.py wrote, its sha256 unchanged, every column of the table must have its event file,
    each event file must be that of a study row that still checks out, and they must come from the released
    model and, for each restriction card, from one version of it."""
    sp = sources_path(tsv)
    if not os.path.exists(sp):
        sys.exit(f"{what}: not written, {tsv} has no {os.path.basename(sp)} naming the event files behind it "
                 "(plot_study.py writes one; remake the table with it)")
    head, srows = read_tsv(sp)
    if "kind" not in head:
        sys.exit(f"{what}: not written, {sp} was written by an earlier plot_study.py, which did not record the tables it "
                 f"made, so nothing ties {tsv} to its event files; remake the table with plot_study.py")
    problems, rows, checked, tables, labels = [], [], {}, {}, []
    for r in srows:
        d = as_dict(head, r)
        if d["kind"] == "table":
            tables[_abs(d["path"])] = d["sha256"]
            continue
        labels.append(d["label"])
        if d["results"] in ("", "-"):
            problems.append(f"{sp}: {d['label']} was drawn from {d['path']}, which is not the event file of a study row, "
                            "so no record says which run made it")
            continue
        res = _abs(d["results"])
        if not os.path.exists(res):
            problems.append(f"{sp}: {d['label']} names the results file {d['results']}, which does not exist")
            continue
        if res not in checked:
            checked[res] = check(res, problems, quiet=True)
        mine = [x for x in read_records(records_path(res)) if x["lhe_sha256"] == d["sha256"] and key(x) in checked[res]]
        if not mine:
            problems.append(f"{sp}: {d['label']} names an event file that no row of {_rel(res)} has")
            continue
        k = key(mine[0])
        v = checked[res][k]
        if v[0] != d["model_version"]:
            problems.append(f"{sp}: {d['label']} was drawn from model {d['model_version'][:12]}, its record now says {v[0][:12]}")
        rows.append((f"{_rel(res)}: {' | '.join(k)}", k[1], v))
        lp = _abs(d["path"])
        if os.path.isdir(os.path.join(os.path.dirname(res), "lhe")) and os.path.exists(lp) and sha256_file(lp) != d["sha256"]:
            problems.append(f"{sp}: {d['path']} has changed since the table was made")
    # the table drawn is one those event files made, unchanged since, with an event file for every column
    for f in [tsv] + [o for o in others if o]:
        if _abs(os.path.abspath(f)) not in tables:
            problems.append(f"{sp} does not name {f}, so nothing says which event files made it")
        elif not os.path.exists(f) or sha256_file(f) != tables[_abs(os.path.abspath(f))]:
            problems.append(f"{f} has changed since plot_study.py wrote it with {os.path.basename(sp)}, so its numbers may "
                            "not be those of the event files the sources file names")
    cols = read_tsv(tsv)[0][2:] if os.path.exists(tsv) else []
    if cols != labels:
        problems.append(f"{tsv} has the columns {', '.join(cols) or 'none'}, and {os.path.basename(sp)} names event files for "
                        f"{', '.join(labels) or 'none'}"
                        + (f", none for {', '.join(c for c in cols if c not in labels)}" if any(c not in labels for c in cols) else ""))
    problems += mixed_versions(rows, f"the event files of {tsv}") + release_problems(rows, f"the event files of {tsv}")
    if problems:
        sys.exit(f"{what}: not written\n  " + "\n  ".join(problems[:40]))


# ---------------------------------------------------------------------------------------------
# recovering the records of rows run before records were kept


def event_index(roots):
    """{file name: [paths]} of every event file in an lhe/ directory below the search directories."""
    idx = {}
    for root in roots:
        for dp, dn, fn in os.walk(root):
            if os.path.basename(dp) == "lhe":
                for f in fn:
                    if f.endswith(".lhe.gz") or f.endswith(".lhe"):
                        idx.setdefault(f, []).append(os.path.join(dp, f))
    return idx


def results_index(roots, skip):
    """{row: [directory]} of the rows of every results file below the search directories."""
    idx = {}
    for root in roots:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                p = os.path.join(dp, f)
                if not (f.startswith("results") and f.endswith(".tsv")) or os.path.abspath(p) == skip:
                    continue
                try:
                    h, rows = read_tsv(p)
                except (OSError, UnicodeDecodeError):
                    continue
                for r in rows:
                    d = as_dict(h, r)
                    idx.setdefault(tuple(d.get(c, "").strip() for c in ROW[:7]), []).append(dp)
    return idx


def nodiagram_index(roots):
    """{(model, generate): (log, import path, MadGraph version)} of every generate command that a
    MadGraph log below the search directories answers with NoDiagramException."""
    idx = {}
    for root in roots:
        for dp, dn, fn in os.walk(root):
            for f in fn:
                p = os.path.join(dp, f)
                if not f.endswith(".log") or os.path.getsize(p) > 20 << 20:
                    continue
                text = open(p, errors="replace").read()
                if "NoDiagramException" not in text:
                    continue
                m = re.search(r"VERSION\s+(\S+)", text)
                imp, gen = None, None
                for line in text.replace("\\\n", "").splitlines():
                    if re.match(r"\s*import\s+model\s+\S", line):
                        imp = line.split(None, 2)[2].strip()
                    elif re.match(r"\s*generate\s+\S", line):
                        gen = " ".join(line.split(None, 1)[1].split())
                    elif "NoDiagramException" in line and imp and gen:
                        idx.setdefault((os.path.basename(imp.rstrip("/")), gen), (p, imp, m.group(1) if m else "-"))
    return idx


def layout_fits(param_text, model_dir, card):
    """Whether a param card is one the model gives: every entry is an entry of the same name of the
    model's restriction card (of its param_card_template.dat for the unrestricted model), and the
    dimension-eight coefficients present are those the card keeps (all of them, unrestricted)."""
    p = os.path.join(model_dir, f"restrict_{card}.dat" if card else "param_card_template.dat")
    if not os.path.isfile(p):
        return False
    ref = param_entries(open(p).read())
    got = param_entries(param_text)
    if not all(k in ref and ref[k][1].lower() == n.lower() for k, (v, n) in got.items() if k[0] != "decay" and " : " not in n):
        return False
    keep = {k for k, (v, n) in ref.items() if is_c8(n) and (not card or float(v) != 0)}
    return keep == {k for k, (v, n) in got.items() if is_c8(n)}


def header_matches(h, d):
    """Whether the header h of an event file (lhe_header) is that of the results row d: its cross section and
    error, its generate command (the row's process at the row's order) and its model."""
    imp, gen = proc_commands(h["proc"])
    want = " ".join((d["process"] + " " + ("NP=0" if d["order"] == "NP=0 on" else d["order"])).split())
    return bool(same_printed(d["sigma_pb"], h["xsec"]) and h["init"] and same_printed(d["error_pb"], h["init"][1])
                and gen == want and os.path.basename((imp or "").rstrip("/")) == d["model"])


def holder(study, path, mine):
    """The row of a results file of the study, other than mine (results file name, row key), whose event file
    path is by its header, or False.  recover must not overwrite it, although no record names it yet: results
    files of one study share event-file names (results_v1.tsv and results_dim8_is.tsv), and the row whose
    file it is may be recovered later."""
    if not os.path.exists(path):
        return False
    h = lhe_header(path)
    for f in sorted(os.listdir(study)):
        if f.startswith("results") and f.endswith(".tsv"):
            hd, rows = read_tsv(os.path.join(study, f))
            for r in rows:
                d = as_dict(hd, r)
                if all(c in d for c in ROW) and (f, key(d)) != mine and header_matches(h, d):
                    return f"{f}, {' | '.join(key(d))}"
    return False


def under(where, prefix):
    """Whether the import path where is prefix or lies below it: prefix ends at a path separator or at a
    '-' (models/dim8_is- for its restricted names), or where goes on with one, so that the prefix
    .../models/dim8_is does not take .../models/dim8_is_murphy."""
    if not where.startswith(prefix):
        return False
    rest = where[len(prefix):]
    return not rest or rest[0] in "/-" or prefix[-1:] in ("/", "-")


def taken(study, rel, mine):
    """Whether another record of the study names the event file rel with its present content."""
    p = os.path.join(study, rel)
    if not os.path.exists(p):
        return False
    h = None
    for f in os.listdir(study):
        if f.startswith("records") and f.endswith(".tsv"):
            hr, recs = read_tsv(os.path.join(study, f))
            for r in recs:
                d = as_dict(hr, r)
                if d["lhe"] == rel and (f, key(d)) != mine:
                    h = h or sha256_file(p)
                    if d["lhe_sha256"] == h:
                        return f"{f}, {' | '.join(key(d))}"
    return False


def recover(argv):
    results = os.path.abspath(argv[0])
    roots = [os.path.abspath(argv[i + 1]) for i, a in enumerate(argv) if a == "--search"]
    models = [argv[i + 1].split("=", 1) for i, a in enumerate(argv) if a == "--model"]
    dry = "--dry" in argv
    study = os.path.dirname(results)
    hd, rows = read_tsv(results)
    rp = records_path(results)
    # a row whose record names its model is done; one recovered without it is tried again
    done = set()
    with records_lock(rp):
        if os.path.exists(rp):
            hr, recs = read_tsv(rp)
            whole = [r for r in recs if as_dict(hr, r)["model_sha256"] not in ("", "-")]
            done = {key(as_dict(hr, r)) for r in whole}
            if len(whole) < len(recs) and not dry:
                write_records(rp, [as_dict(hr, r) for r in whole])
    events, others, logs = event_index([study] + roots), results_index(roots, results), nodiagram_index(roots)
    ids, lost, n_new, by_model = {}, [], 0, {}
    keep = (lambda rec: None) if dry else (lambda rec: append_record(results, rec))
    for n, r in enumerate(rows, start=2):
        d = as_dict(hd, r)
        if key(d) in done:
            continue
        n_new += 1
        d["lhe"] = d["lhe"].strip() or "-"
        rec = {c: d.get(c, "-") for c in ROW}
        rec["source"] = "recovered: no event file and no run found"
        rec["identity"] = "recovered"   # the model and card are what --model says, not what the run measured
        what = f"line {n}: {d['process'].strip()} | {d['model']} | {d['order']} | {d['sigma_pb']}"
        base, _, rcard = d["model"].partition("-")
        want = " ".join((d["process"] + " " + ("NP=0" if d["order"] == "NP=0 on" else d["order"])).split())
        hits, why = [], []
        if d["lhe"] != "-":
            own = os.path.join(study, d["lhe"])
            cands = ([own] if os.path.exists(own) else []) + [p for p in events.get(os.path.basename(d["lhe"]), []) if p != own]
            for p in cands:
                h = lhe_header(p)
                imp, gen = proc_commands(h["proc"])
                if not (same_printed(d["sigma_pb"], h["xsec"]) and h["init"] and same_printed(d["error_pb"], h["init"][1])):
                    why.append(f"{_rel(p)} has {h['xsec']:.6g} pb" if h["xsec"] is not None and math.isfinite(h["xsec"])
                               else f"{_rel(p)} has no cross section")
                elif gen != want or os.path.basename(imp.rstrip("/")) != d["model"]:
                    why.append(f"{_rel(p)} generated {gen!r} with {os.path.basename(imp.rstrip('/'))}")
                else:
                    hits.append((p, h, imp))
        where, mg = None, "-"
        if hits:
            p, h, where = hits[0]
            if os.path.abspath(p) != os.path.abspath(os.path.join(study, d["lhe"])):
                mine = (os.path.basename(rp), key(d))
                t = taken(study, d["lhe"], mine) or holder(study, os.path.join(study, d["lhe"]), (os.path.basename(results), key(d)))
                if t:
                    lost.append(f"{what}: its event file is in {_rel(p)}, and lhe/{os.path.basename(d['lhe'])} holds the one of {t}")
                    keep(rec)
                    continue
                if not dry:
                    dst = os.path.join(study, d["lhe"])
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    fd, t = tempfile.mkstemp(dir=os.path.dirname(dst), prefix=os.path.basename(dst) + ".", suffix=".part")
                    os.close(fd)
                    shutil.copy2(p, t); os.replace(t, dst)
            rec["lhe_sha256"] = sha256_file(p)
            rec["lhe_sigma_pb"], rec["lhe_error_pb"] = f"{h['xsec']:.10g}", f"{h['init'][1]:.10g}"
            rec["lhe_signed_error_pb"] = f"{signed_error(p, h['run']):.10g}"
            rec["mg5"] = h["mg5"]
            if not dry:
                fill_cards(rec, study, h["param"], h["run"], h["proc"])
            rec["source"] = "recovered from the header of " + _found(p, roots) +(f" (the same numbers in {len(hits) - 1} more)" if len(hits) > 1 else "")
        elif d["lhe"] == "-" and d["sigma_pb"] in WORDS:
            dirs = others.get(tuple(d.get(c, "").strip() for c in ROW[:7]), [])
            if dirs:
                where = os.path.join(dirs[0], d["model"])   # the run's import path, as the task named it
                # the MadGraph version of a run that left no event file is that of its neighbours
                for q in sorted(glob.glob(os.path.join(dirs[0], "lhe", "*")) + glob.glob(os.path.join(os.path.dirname(dirs[0]), "*", "lhe", "*"))):
                    mg = lhe_header(q)["mg5"]
                    if mg != "-":
                        break
                rec["mg5"] = mg
                rec["source"] = "recovered from the results file of " + _found(dirs[0], roots)
            elif (d["model"], want) in logs and d["sigma_pb"] == "NO_DIAGRAMS":
                log, where, rec["mg5"] = logs[(d["model"], want)]
                rec["import"], rec["generate"] = d["model"], want   # the commands the log answers with no diagram
                rec["source"] = "recovered from the MadGraph log " + _found(log, roots)
        if where is None:
            lost.append(f"{what}: " + ("no event file of that name" if d["lhe"] != "-" and not why else
                                       "no event file with these numbers (" + "; ".join(why[:3]) + ")" if why else
                                       "no event file, and no run of that row in a searched results file"))
            keep(rec)
            continue
        for prefix, mdir in models:
            if under(where, prefix):
                if hits and not layout_fits(hits[0][1]["param"], mdir, rcard):
                    lost.append(f"{what}: run with {where}, whose param card is not one {mdir} gives")
                    rec["source"] += ", model not identified"
                    break
                if mdir not in ids:
                    ids[mdir] = model_id(mdir)
                rec["model_sha256"], rec["release_sha256"] = ids[mdir][0], ids[mdir][1]
                by_model[mdir] = by_model.get(mdir, 0) + 1
                rc = os.path.join(mdir, f"restrict_{rcard}.dat")
                rec["card_sha256"] = sha256_file(rc) if rcard and os.path.isfile(rc) else "-"
                if not dry:
                    store_restriction(study, mdir, rcard, rec["card_sha256"])
                break
        else:
            lost.append(f"{what}: run with {where}, a model no --model names")
        keep(rec)
    print(f"{_rel(results)}: {n_new} rows without a record, {n_new - len(lost)} traced, {len(lost)} cannot be traced"
          + (" (dry run, nothing written)" if dry else ""))
    for m, k in by_model.items():
        print(f"   {k} rows run with {m} (model {ids[m][0][:12]}, release {ids[m][1][:12]})")
    for l in lost:
        print("   " + l)
    return 0


def attest(argv):
    """Write into the records of a results file which rows ran with a model and restriction card that
    validate/same_couplings.py found equal to the model named in its output, restricted by that model's
    own card of the row's name: equal at the values of the row's cards, in every vertex that a tree
    diagram of the processes it compared can contain.  A verdict covers a row only when the row's process
    is one of those processes, since a vertex that no diagram of those processes contains may differ."""
    results = argv[0]
    need = {"model_a", "model_b", "card", "card_sha256", "card_b", "param_card", "differing", "couplings_differing", "processes"}
    found = {}
    for vf in argv[1:]:
        hv, vs = read_tsv(vf)
        if need - set(hv):
            sys.exit(f"{vf}: no {', '.join(sorted(need - set(hv)))} column, written by an earlier validate/same_couplings.py "
                     "that did not say which restriction cards and processes it compared; run it again")
        for r in vs:
            d = as_dict(hv, r)
            k = (d["model_a"], d["card"], d["card_sha256"], d["param_card"])
            same = d["differing"] == "0" and d["couplings_differing"] in ("0", "-")
            found.setdefault(k, []).append((d["model_b"], d["card_b"], same, set(d["processes"].split(";"))))
    rp = records_path(results)
    n, models_b = {"same": 0, "differ": 0, "not compared": 0, "compared for other processes only": 0}, set()
    with records_lock(rp):   # a record run_study.sh appends meanwhile is not lost by the rewrite
        recs = read_records(rp)
        for d in recs:
            vs = found.get((d["model_sha256"], d["model"].partition("-")[2] or "-", d["card_sha256"] or "-", d["param_card"] or "-"), [])
            mine = [v for v in vs if " ".join(d["process"].split()) in v[3]]
            ok = [v for v in mine if v[2]]
            if not vs:
                n["not compared"] += 1
            elif not mine:
                n["compared for other processes only"] += 1
            elif ok:
                n["same"] += 1
                models_b.add(ok[0][0][:12])
                # a model compared with itself says nothing of the run, so it does not count as a comparison
                d["same_as"] = ok[0][0] if ok[0][0] != d["model_sha256"] else "-"
                d["same_card"] = ok[0][1] if d["model"].partition("-")[2] else "-"
            else:
                n["differ"] += 1
                d["same_as"], d["same_card"] = "-", "-"
        write_records(rp, recs)
    print(f"{_rel(rp)}: {n['same']} rows have at their cards the couplings of model {', '.join(sorted(models_b)) or '-'} and count as "
          f"its rows, {n['differ']} do not, {n['not compared']} were not compared"
          + (f", {n['compared for other processes only']} were compared only in other processes" if n["compared for other processes only"] else ""))
    return 0


def recorded_lhe(argv):
    """lhe <results.tsv> <process> <card> <order>: the event file the record of that row names,
    the model being the study's ("" for the plain model).  A script that draws distributions finds its samples
    with it, and so reads the event files of the runs whose cross sections the tables print."""
    results, proc, card, order = argv[:4]
    hd, rows = read_tsv(results)
    base = {as_dict(hd, r)["model"].split("-")[0] for r in rows}
    if len(base) != 1:
        sys.exit(f"{_rel(results)}: rows from {len(base)} models ({', '.join(sorted(base))})")
    k = (" ".join(proc.split()), base.pop() + (f"-{card}" if card else ""), order)
    if not os.path.exists(records_path(results)):
        sys.exit(f"{_rel(results)}: no records file, so no event file can be named")
    hr, recs = read_tsv(records_path(results))
    mine = [d for d in (as_dict(hr, r) for r in recs) if (" ".join(d["process"].split()), d["model"], d["order"]) == k]
    if len(mine) != 1 or mine[0]["lhe"] in ("", "-"):
        sys.exit(f"{_rel(results)}: {'no record' if not mine else 'no event file in the record' if len(mine) == 1 else 'several records'} for {' | '.join(k)}")
    print(os.path.join(os.path.dirname(os.path.abspath(results)), mine[0]["lhe"]))
    return 0


def signed(argv):
    """signed <results.tsv> ...: write into the records the error of the signed weights of each row's event file,
    which must be the recorded one (its sha256).  A results file is written whole or not at all."""
    for results in argv:
        study, p, n = os.path.dirname(os.path.abspath(results)), records_path(results), 0
        with records_lock(p):
            recs = read_records(p)
            for rec in recs:
                lhe = rec.get("lhe", "-").strip() or "-"
                if lhe == "-" or lhe.endswith(".width.txt"):
                    continue
                f = os.path.join(study, lhe)
                if not os.path.exists(f) or sha256_file(f) != rec.get("lhe_sha256"):
                    sys.exit(f"{_rel(results)}: {' | '.join(key(rec))}: {lhe} is "
                             + ("missing" if not os.path.exists(f) else "not the recorded event file (sha256 differs)")
                             + ", and no record of the file was changed")
                rec["lhe_signed_error_pb"] = f"{signed_error(f, lhe_header(f)['run']):.10g}"
                n += 1
            write_records(p, recs)
        print(f"provenance: the error of the signed event weights of {n} rows in {_rel(p)}")
    return 0


def main(argv):
    if len(argv) < 3 or argv[1] not in ("check", "recover", "record", "attest", "model", "lhe", "signed"):
        print(__doc__)
        return 2
    cmd, args = argv[1], argv[2:]
    if cmd == "record":
        return record(args)
    if cmd == "recover":
        return recover(args)
    if cmd == "attest":
        return attest(args)
    if cmd == "lhe":
        return recorded_lhe(args)
    if cmd == "signed":
        return signed(args)
    if cmd == "model":
        print(" ".join(model_id(args[0], args[1] if len(args) > 1 else "")))
        return 0
    problems, rows = [], []
    for f in args:
        for k, v in check(f, problems).items():
            rows.append((f"{_rel(f)}: {' | '.join(k)}", k[1], v))
    problems += mixed_versions(rows, "the rows") + release_problems(rows, "the rows")
    for p in problems:
        print(p)
    vs = {}
    for _, _, (mv, cv) in rows:
        vs[mv] = vs.get(mv, 0) + 1
    print(f"{len(problems)} disagreements; model versions: " + (", ".join(f"{v[:12]} ({n} rows)" for v, n in vs.items()) or "none"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
