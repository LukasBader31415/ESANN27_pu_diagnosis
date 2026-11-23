"""Every number in Paper A, recomputed from the aggregated CSVs in paper/results/.

    python paper/paper_numbers.py              # print the table: location, value in the paper, value from the CSV
    python paper/paper_numbers.py --markdown   # rewrite docs/numbers.md

Each entry names the file and the column / row it is read from. `paper` is the value as printed in the paper
(main.tex, Overleaf version 884c0ed of 2026-11-23); `computed` is the value from the CSV, rounded the same way (half up).
"""
from __future__ import annotations

import argparse
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
RES = HERE / "results"

F = {  # short name -> file (relative to paper/results/)
    "OOF": "2026-11-11_A_auswertung_naicsfix/hub_oof_profil.csv",
    "LIST": "2026-11-11_A_auswertung_naicsfix/hauptliste_neu.csv",
    "KV": "2026-11-11_A_auswertung_naicsfix/kverlauf_s1.csv",
    "EB": "2026-11-11_A_auswertung_naicsfix/eval_beschreibend.csv",
    "AN": "2026-11-11_A_auswertung_naicsfix/vergleich_alt_neu.csv",
    "KNEE": "2026-11-10_A_L2_hub/isolation_knick.csv",
    "REF": "2026-11-11_A_AP2_hub_naicsfix/vergleichsmodelle.csv",
    "TWP": "2026-11-11_A_AP2_hub_naicsfix/zwillinge_paare.csv",
    "TWA": "2026-11-11_A_AP2_hub_naicsfix/zwillinge_pair_auc.csv",
    "RAW": "2026-11-11_A_AP2_hub/roh_innerhalb_naics.csv",
    "IND": "2026-11-07_A_R9_stufe1/r9s1_beschreibend.csv",
    "SIM": "2026-11-07_A_R9_steckbrief/sb_aehnlichkeit.csv",
    "SPY": "2026-11-12_A_spy_naicsfix/spy_trennung.csv",
    "R10E": "2026-11-17_A_R10_auswertung/r10_erwartung.csv",
    "R10G": "2026-11-17_A_R10_auswertung/r10_gruppen.csv",
    "R10D": "2026-11-17_A_R10_auswertung/r10_drift.csv",
    "FILT": "2026-11-17_A_R13_reject_filter/filter_varianten.csv",
    "REJ": "2026-11-17_A_R13_reject_filter/reject_kurve.csv",
    "TOP": "2026-11-17_A_R13_reject_filter/vertrieb_top.csv",
    "SIZE": "2026-11-17_A_R14_groesse_pflanz/groesse_zwillinge.csv",
    "SIZEM": "2026-11-17_A_R14_groesse_pflanz/groesse_modelle.csv",
    "PLANT": "2026-11-17_A_R14_groesse_pflanz/pflanz_modelle.csv",
    "MATV": "2026-11-18_A_R15_werkstoffe/views_neu.csv",
    "MATM": "2026-11-18_A_R15_werkstoffe/werkstoff_modelle.csv",
    "MAT4": "2026-11-18_A_R15_werkstoffe/stufe3_fits.csv",
}

_cache: dict[str, pd.DataFrame] = {}


def T(key: str) -> pd.DataFrame:
    if key not in _cache:
        _cache[key] = pd.read_csv(RES / F[key], dtype={"seed": str})
    return _cache[key]


def one(df: pd.DataFrame, col: str):
    if len(df) != 1:
        raise ValueError(f"expected exactly one row, got {len(df)}")
    return df[col].iloc[0]


# --------------------------------------------------------------------------- formatting (paper style, half up)
def _r(v: float, nd: int) -> Decimal:
    return Decimal(repr(float(v))).quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)


def f(v, nd=2):
    """.57 / .585 / −.006 (no leading zero, minus sign as in the paper)."""
    s = f"{_r(v, nd):f}"
    neg = s.startswith("-")
    s = s.lstrip("-")
    s = s[1:] if s.startswith("0.") else s
    return ("−" if neg and float(s) != 0 else "") + s


def pct(v):
    return f"{_r(100 * v, 0):f} %"


def n(v):
    return f"{int(round(float(v))):,}"


def rng(lo, hi, nd=2):
    return f"{f(lo, nd)}–{f(hi, nd)}"


def ci(row, est="pair_auc", lo="ci_lo", hi="ci_hi"):
    return f"{f(one(row, est))} [{f(one(row, lo))}, {f(one(row, hi))}]"


# --------------------------------------------------------------------------- selections
def oof(label):
    q = T("OOF")
    return q[(q.variant == "frozen") & (q.stand == "neu") & (q.label == label)]


def ref_models():
    q = T("REF")
    return q[q.modell.str.match(r"^(HGB|Random Forest|L1|SVM)")]


def twin(score):
    q = T("TWA")
    return one(q[(q.schluessel == "naics_primaer") & (q.score == score) & (q.gewichtung == "je Paar")
                 & (q.teilmenge == "alle")], "pair_auc")


def plant(model):
    q = T("PLANT")
    return q[(q.seed == "Mittel") & q.modell.str.startswith(model)]


def spy(prefix):
    q = T("SPY")
    return one(q[(q.seed == "gepoolt") & q.score.str.startswith(prefix)], "auc")


def r10(group, col="anteil_belegt"):
    q = T("R10G")
    return one(q[q.gruppe == group], col)


def filt(var, col):
    q = T("FILT")
    return one(q[q.variante == var], col)


def max_gain():
    """Largest mean Δ BA from adding size (R14) or materials (R15) to any model, and materials as 4th view."""
    a = T("SIZEM")
    a = a[a.zeile.str.startswith("Δ")].ba_mittel
    b = T("MATM")
    b = b[b.zeile == "Δ mit Werkstoffen − ohne"].ba_mittel
    c = T("MAT4").delta_ba.mean()
    return max(a.max(), b.max(), c)


def kv_gain():
    q = T("KV")
    q = q[q.stand == "neu"].pivot(index="K", columns="variant", values="ba_end")
    return float(q.drop(columns="frozen").sub(q.frozen, axis=0).max().max())


def reject(cover, who):
    q = T("REJ")
    r = q[(q.stand == "neu") & (q.mitte == 0.0) & (q.abdeckung.round(2) == cover)]
    return one(r, f"anteil_zurueckgewiesen_{who}")


def top(q_):
    t = T("TOP")
    return one(t[(t.stand == "neu") & (t.oberste.round(2) == q_)], "precision_kaeufer")


def sim(comp):
    s = T("SIM")
    return one(s[(s.distanz == "kombiniert (frozen)") & (s.vergleich == comp)], "mittel")


def ind(comp):
    s = T("IND")
    return one(s[(s.merkmal == "kaeuferanteil_naics_alt") & (s.vergleich == comp)], "delta")


# --------------------------------------------------------------------------- the numbers
# (location, quantity, value in the paper, computed string, short file, column / row)
def entries():
    E = []
    add = lambda loc, what, paper, comp, src, col: E.append(dict(location=loc, quantity=what, paper=paper,
                                                                   computed=comp, file=src, column_row=col))
    n0, n1 = int(one(oof(0), "n")), int(one(oof(1), "n"))
    eb = T("EB")
    ba_frozen = f(one(eb[eb.variant == "frozen"], "neu_ba_end"), 3)
    # Abstract, Sect. 1, Sect. 2
    add("Abstract, Sect. 1, 2", "customers", "2,025", n(n0 + n1), "OOF", "`n`, rows frozen / neu, label 0 + label 1")
    add("Abstract, Sect. 2", "BA of the frozen model", ".585", ba_frozen, "EB",
        "`neu_ba_end`, variant frozen (also REF row `frozen K 6`)")
    add("Sect. 1", "BA of the prototype model of the ECML 2026 paper", "around .59", "external", "–",
        "number from the ECML 2026 paper (Table 8 there), not from this repository (see note 1)")
    add("Sect. 2", "buyers (label 1)", "1,038", n(n1), "OOF", "`n`, frozen / neu / label 1")
    add("Sect. 2", "no observed purchase (label 0)", "987", n(n0), "OOF", "`n`, frozen / neu / label 0")
    add("Sect. 2", "base rate", ".51", f(n1 / (n0 + n1)), "TOP", "`grundrate` (= 1038 / 2025 = .513)")
    add("Fig. 1b (label in the figure)", "base rate", ".51", f(n1 / (n0 + n1)), "TOP", "`grundrate`")
    add("Sect. 2", "learned weights exceed frozen by at most (K between 2 and 20)", ".006", f(kv_gain(), 3), "KV",
        "max over K of `ba_end`(learned) − `ba_end`(frozen), stand neu (see note 2)")
    kv = T("KV")
    kv = kv[(kv.stand == "neu") & (kv.variant == "frozen")].ba_end
    add("Sect. 2", "frozen BA over K (K = 4–20 in this file)", "changes not substantially", rng(kv.min(), kv.max(), 3),
        "KV", "`ba_end`, variant frozen, stand neu (see note 2)")
    # Sect. 3
    kn = T("KNEE")
    add("Sect. 3", "isolated: knee of the distance curve", "17.6 %", f"{100 * float(one(kn, 'knick_obere_anteil')):.1f} %",
        "KNEE", "`knick_obere_anteil` (published matrix; corrected matrix see note 3)")
    lst = T("LIST")[T("LIST").objekt == "Gruppe Kandidat"]
    add("Sect. 3", "candidates (fixed on the published matrix)", "319", n(one(lst, "n_alt")), "LIST",
        "row `Gruppe Kandidat`, `n_alt`")
    add("Sect. 3", "of these, also candidates on the corrected matrix", "247",
        f"{n(one(lst, 'schnitt'))} (= {pct(one(lst, 'schnitt') / one(lst, 'n_alt'))})", "LIST",
        "row `Gruppe Kandidat`, `schnitt`")
    tw = T("TWP")
    tw = tw[tw.schluessel == "naics_primaer"]
    add("Sect. 3", "industry twin pairs", "11,205", n(one(tw, "n_paare")), "TWP", "`n_paare`, row naics_primaer")
    add("Sect. 3", "customers in twin pairs", "1,851", n(one(tw, "n_kunden_in_paaren")), "TWP", "`n_kunden_in_paaren`")
    add("Sect. 3", "primary codes with twin pairs", "139", n(one(tw, "n_schluessel")), "TWP", "`n_schluessel`")
    pl = plant("M³GLVQ")
    add("Sect. 3", "share of buyers flipped", "10 %", pct(one(pl, "n_gekippt") / n1), "PLANT", "`n_gekippt` / 1038")
    add("Sect. 3, Fig. 1a", "random draws of planted buyers", "three", str(int((T("PLANT").seed != "Mittel").sum() / 3)),
        "PLANT", "`seed` 101, 102, 103 (row `Mittel` = pooled over the draws)")
    # Table 1 and Sect. 4
    add("Tab. 1, Sect. 4.1", "label 0 always wrong, observed", "463", n(one(oof(0), "stets_falsch")), "OOF",
        "`stets_falsch`, frozen / neu / label 0")
    add("Tab. 1, Sect. 4.1", "label 0 always wrong, expected (null model)", "117", n(one(oof(0), "erwartet_falsch")),
        "OOF", "`erwartet_falsch`, label 0")
    add("Tab. 1, Sect. 4.1", "buyers always wrong, observed", "184", n(one(oof(1), "stets_falsch")), "OOF",
        "`stets_falsch`, label 1")
    e1 = float(one(oof(1), "erwartet_falsch"))
    add("Tab. 1 / Sect. 4.1", "buyers always wrong, expected", "1 / less than one",
        f"{n(e1)} / {'less than one' if e1 < 1 else 'not < 1'} ({e1:.2f})", "OOF", "`erwartet_falsch`, label 1")
    rm = ref_models()
    add("Tab. 1", "control of the reference models: frozen model", "BA .585",
        f"BA {f(one(T('REF')[T('REF').modell.str.startswith('frozen')], 'ba_mittel'), 3)}", "REF", "row `frozen K 6`")
    add("Tab. 1, Sect. 4.1", "BA of RF, HGB, LR, SVM", ".56–.59", rng(rm.ba_mittel.min(), rm.ba_mittel.max()), "REF",
        "`ba_mittel`, rows HGB, Random Forest, L1-logistisch (= LR), SVM (see note 6)")
    add("Sect. 3, Tab. 1", "control: primary codes only", ".50", f(twin("NAICS nur Primärcode (k 31)")), "TWA",
        "`pair_auc`, naics_primaer / NAICS nur Primärcode / je Paar / alle")
    add("Sect. 4.2", "pair AUC products (HS)", ".50", f(twin("HS (k 15)")), "TWA", "score `HS (k 15)`, je Paar, alle")
    add("Sect. 4.2", "pair AUC applications", ".50", f(twin("AM (k 31)")), "TWA", "score `AM (k 31)`, je Paar, alle")
    add("Sect. 4.2", "pair AUC full NAICS view", ".57", f(twin("NAICS voll (k 31)")), "TWA",
        "score `NAICS voll (k 31)`, je Paar, alle")
    add("Tab. 1", "views (range)", ".50–.57",
        rng(min(twin("HS (k 15)"), twin("AM (k 31)")), twin("NAICS voll (k 31)")), "TWA", "HS, AM, NAICS voll")
    raw = T("RAW")
    add("Sect. 4.2", "single features tested within industries", "104", n(len(raw)), "RAW", "rows")
    add("Sect. 4.2", "carriers per feature at least", "20", n(raw.n_traeger_in_schichten.min()), "RAW",
        "`n_traeger_in_schichten` (min)")
    add("Sect. 4.2", "smallest q of the single features", "q > .8", f"q ≥ {f(raw.q_bh.min(), 3)}", "RAW",
        "`q_bh` (min; see note 4)")
    sz = T("SIZE")
    add("Tab. 1, Sect. 4.2", "pair AUC company size [95 % interval]", ".56 [.53, .60]",
        ci(sz[(sz.feld == "employees_total") & (sz.gewichtung == "je Paar")]), "SIZE",
        "`pair_auc`, `ci_lo`, `ci_hi`, employees_total / je Paar (revenue .56 as well)")
    mv = T("MATV")
    add("Tab. 1, Sect. 4.2", "pair AUC materials [95 % interval]", ".55 [.52, .59]", ci(mv[mv.view == "V3"]), "MATV",
        "`pair_auc`, `ci_lo`, `ci_hi`, view V3 (materials only; see note 5)")
    add("Sect. 4.2", "materials as a fourth view, Δ BA", "−.001", f(T("MAT4").delta_ba.mean(), 3), "MAT4",
        "mean of `delta_ba` over 50 fits")
    add("Tab. 1, Sect. 4.2", "largest Δ BA from size or materials in any model", "≤ .02", f(max_gain(), 3),
        "SIZEM, MATM, MAT4", "max of `ba_mittel` in Δ rows, and mean `delta_ba`")
    for key, lab, val in (("M³GLVQ", "M³GLVQ", ".61"), ("RF", "RF", ".63"), ("HGB", "HGB", ".62")):
        add("Tab. 1, Sect. 4.3, Fig. 1a", f"AUC planted vs. label 0, {lab}", val, f(one(plant(key), "auc_gekippt")),
            "PLANT", f"`auc_gekippt`, seed Mittel, {key}")
    dd = [float(one(plant(k), "diff_gekippt_minus_ungekippt")) for k in ("M³GLVQ", "RF", "HGB")]
    add("Tab. 1, Sect. 4.3", "planted minus unflipped buyers", "as for other buyers", ", ".join(f(x, 3) for x in dd),
        "PLANT", "`diff_gekippt_minus_ungekippt`, seed Mittel")
    add("Sect. 4.3", "planted buyers among label-0 always wrong", "45 %",
        pct(one(pl, "anteil_gekippt_in_L0_stets_falsch")), "PLANT", "`anteil_gekippt_in_L0_stets_falsch`, M³GLVQ")
    add("Sect. 4.3", "share of planted buyers in that group", "14 %", pct(one(pl, "precision_liste")), "PLANT",
        "`precision_liste`, M³GLVQ")
    add("Sect. 4.3", "times their share among label 0 in training", "about 1.5", f"{float(one(pl, 'lift')):.2f}",
        "PLANT", "`lift` (= .138 / .095)")
    sp = [spy(p) for p in ("s̄", "L1-logistisch (Rohmerkmale, NAICS", "HistGradientBoosting")]
    add("Tab. 1, Sect. 4.3", "spy AUC s̄, LR, HGB", ".57–.58", rng(min(sp), max(sp)), "SPY",
        "`auc`, seed gepoolt, rows s̄, LR stratified (`L1-logistisch …`), HGB")
    add("Tab. 1, Sect. 4.3", "spy AUC within industries", ".54", f(spy("L1-logistisch (Rohmerkmale ohne")), "SPY",
        "`auc`, gepoolt, LR grouped by primary code (`L1-logistisch (Rohmerkmale ohne …`)")
    add("Sect. 4.3", "cleaning flags label 0", "53 %", pct(filt("B1", "anteil_entfernt_0_mittel")), "FILT",
        "`anteil_entfernt_0_mittel`")
    add("Sect. 4.3", "cleaning flags buyers", "32 %", pct(filt("B1", "anteil_entfernt_1_mittel")), "FILT",
        "`anteil_entfernt_1_mittel`, B1")
    add("Tab. 1, Sect. 4.3", "Δ BA, both classes cleaned", "−.006", f(filt("B1", "delta_ba_mittel"), 3), "FILT",
        "`delta_ba_mittel`, B1")
    add("Tab. 1, Sect. 4.3", "Δ BA, only label 0 cleaned", "−.023", f(filt("B2", "delta_ba_mittel"), 3), "FILT",
        "`delta_ba_mittel`, B2 (−.0235)")
    add("Sect. 4.3", "rejected at 70 % / 50 % coverage, candidates vs. comparison customers", "less often",
        f"{f(reject(0.7, 'kandidat'), 3)} vs. {f(reject(0.7, 'kontrolle'), 3)}; "
        f"{f(reject(0.5, 'kandidat'), 3)} vs. {f(reject(0.5, 'kontrolle'), 3)}", "REJ",
        "`anteil_zurueckgewiesen_*`, stand neu, mitte 0")
    add("Sect. 4.4", "candidates / comparison customers checked", "161 / 161",
        f"{n(r10('Kandidat', 'n'))} / {n(r10('Kontrolle', 'n'))}", "R10G", "`n`")
    add("Tab. 1, Sect. 4.4", "evidence: candidates", "17 %", pct(r10("Kandidat")), "R10G", "`anteil_belegt` (28/161)")
    add("Tab. 1, Sect. 4.4", "evidence: comparison customers", "19 %", pct(r10("Kontrolle")), "R10G",
        "`anteil_belegt` (30/161)")
    add("Tab. 1, Sect. 4.4", "evidence: known buyers", "21 %", pct(r10("Käufer")), "R10G", "`anteil_belegt`")
    add("Sect. 4.4", "known buyers with evidence", "32 of 155",
        f"{n(r10('Käufer', 'n_belegt'))} of {n(r10('Käufer', 'n'))}", "R10G", "`n_belegt`, `n`")
    add("Sect. 4.4", "Fisher test buyers vs. comparison customers", "p = .38", f"p = {f(one(T('R10E'), 'p'))}", "R10E",
        "`p` (one-sided)")
    d = T("R10D")
    dr = d[d.kennzahl.str.startswith("Firmenstatus")]
    add("Sect. 4.4", "agreement on re-checked companies", "37 of 40",
        f"{n(float(one(dr, 'wert')) * float(one(dr, 'n')))} of {n(one(dr, 'n'))}", "R10D",
        "`wert` × `n`, row Firmenstatus gleich (.925)")
    add("Sect. 5, Fig. 1b", "share of buyers (precision) in the top 5 % by s̄", ".72", f(top(0.05)), "TOP", "`precision_kaeufer`, neu, .05")
    add("Sect. 5", "base rate", ".51", f(one(T("TOP")[T("TOP").stand == "neu"].head(1), "grundrate")), "TOP",
        "`grundrate`")
    add("Sect. 4.1 (no number)", "candidates as close to buyers as buyers to each other (combined distance)",
        "as close", f"cand–buyer {f(sim('zwischen Kandidat – Käufer'))}, within buyers {f(sim('innerhalb Käufer'))}, "
        f"cand–comparison {f(sim('zwischen Kandidat – Kontrolle'))}", "SIM", "`mittel`, distanz kombiniert (frozen)")
    add("Sect. 4.1 (no number)", "buyer share in own NAICS code (share difference)",
        "almost as high as for buyers, considerably higher than for comparison customers",
        f"cand vs. buyers {f(ind('Kandidat vs. Käufer'))}, cand vs. comparison {f(ind('Kandidat vs. Kontrolle'))}",
        "IND", "`delta`, merkmal kaeuferanteil_naics_alt")
    return pd.DataFrame(E)


# entries whose paper value is a statement, an external number or a rounded summary; the table shows the values behind
# them, and the notebook checks every other entry for exact equality
VERBAL = {
    "BA of the prototype model of the ECML 2026 paper", "frozen BA over K (K = 4–20 in this file)",
    "of these, also candidates on the corrected matrix", "random draws of planted buyers",
    "buyers always wrong, expected", "smallest q of the single features",
    "largest Δ BA from size or materials in any model", "planted minus unflipped buyers",
    "times their share among label 0 in training",
    "rejected at 70 % / 50 % coverage, candidates vs. comparison customers",
    "candidates as close to buyers as buyers to each other (combined distance)",
    "buyer share in own NAICS code (share difference)",
}

# Table 1 of the paper (main.tex), row by row: check, control, result
TABLE1 = [
    ("Error profile", "binomial null model", "always wrong: L0 463 vs. 117, L1 184 vs. 1"),
    ("Reference models", "frozen model (BA .585)", "BA .56–.59 for RF, HGB, LR, SVM"),
    ("Industry twins", "primary codes only, must be .50", "views .50–.57, size .56, materials .55, ΔBA ≤ .02"),
    ("Planted buyers", "buyers not flipped", "AUC .61–.63 (M³GLVQ, RF, HGB), below .70, as for other buyers"),
    ("Spy", "spies are known buyers", "AUC .57–.58, within industries .54"),
    ("Cleaning, reject", "frozen model", "ΔBA −.006 / −.023, rejecting barely helps"),
    ("Website check", "known buyers (positive control)", "candidates 17 %, comparison 19 %, buyers 21 %"),
]


def table1(df=None):
    """Table 1 rebuilt from the CSVs (same wording as the paper, numbers from the entries)."""
    v = {r.quantity: r.computed for r in (entries() if df is None else df).itertuples()}
    planted = [v[f"AUC planted vs. label 0, {m}"] for m in ("M³GLVQ", "RF", "HGB")]
    gain = float("0" + v["largest Δ BA from size or materials in any model"].replace("−", "-"))
    rows = [
        ("Error profile", "binomial null model",
         f"always wrong: L0 {v['label 0 always wrong, observed']} vs. {v['label 0 always wrong, expected (null model)']}, "
         f"L1 {v['buyers always wrong, observed']} vs. {v['buyers always wrong, expected'].split(' /')[0]}"),
        ("Reference models", f"frozen model ({v['control of the reference models: frozen model']})",
         f"{'BA ' + v['BA of RF, HGB, LR, SVM']} for RF, HGB, LR, SVM"),
        ("Industry twins", f"primary codes only, must be {v['control: primary codes only']}",
         f"views {v['views (range)']}, size {v['pair AUC company size [95 % interval]'].split(' [')[0]}, "
         f"materials {v['pair AUC materials [95 % interval]'].split(' [')[0]}, ΔBA {'≤' if gain <= 0.02 else '>'} .02"),
        ("Planted buyers", "buyers not flipped",
         f"AUC {min(planted)}–{max(planted)} (M³GLVQ, RF, HGB), below .70, as for other buyers"),
        ("Spy", "spies are known buyers",
         f"AUC {v['spy AUC s̄, LR, HGB']}, within industries {v['spy AUC within industries']}"),
        ("Cleaning, reject", "frozen model",
         f"ΔBA {v['Δ BA, both classes cleaned']} / {v['Δ BA, only label 0 cleaned']}, rejecting barely helps"),
        ("Website check", "known buyers (positive control)",
         f"candidates {v['evidence: candidates']}, comparison {v['evidence: comparison customers']}, "
         f"buyers {v['evidence: known buyers']}"),
    ]
    return pd.DataFrame(rows, columns=["check", "control", "result"])


NOTES = """\
1. The introduction quotes "around .59" for the prototype model of the ECML 2026 paper (Table 8 there); it is not
   recomputed here. On the NAICS matrix published with that paper, the frozen model of this study reaches .579
   (`eval_beschreibend.csv`, `alt_ba_end`); on the corrected matrix .585 (abstract, Sect. 2).
2. .006 is the largest gain of a learned variant (G or CW, identity or sigmoid) over frozen in this study on the
   corrected matrix: +.0063, G identity, K = 4 (`kverlauf_s1.csv`: K = 4, 8, 10, 15, 20, five repetitions). The runs
   with K = 2 and K = 12 (largest gain +.0016) are not part of the aggregated files here.
3. The knee 17.6 % was computed on the published NAICS matrix (`isolation_knick.csv`, run of 2026-11-10). On the
   corrected matrix the knee lies at 14.7 % (`2026-11-20_A_isolation_knick_naicsfix/isolation_knick.csv`, row `neu`). With the
   knee as boundary, the candidate list shrinks from 319 to 303 on the published matrix; on the corrected matrix, where
   the 10 % rule also gives 319 candidates, it shrinks to 311 (`vergleich_alt_neu.csv`, row "Hauptliste L0 Region am
   Knick").
4. 104 features are listed; for 2 of them the stratified odds ratio is not estimable (empty `q_bh`); the
   smallest q among the 102 tested features is .821.
5. The materials number .55 is the pair AUC of the materials-only view V3 (`views_neu.csv`, .554). The number of
   materials per company gives .543 per pair and .555 per code (`werkstoff_zwillinge.csv`).
6. The reference models come from the run on the corrected matrix (`2026-11-11_A_AP2_hub_naicsfix`). CSV row names
   `L1-logistisch …` = LR (L1-regularized logistic regression). The three models on raw features do not depend on the NAICS matrix; the SVM does (.558 here, .560 on the published matrix,
   `vergleich_alt_neu.csv`, rows "B5 BA").
"""


def markdown(df: pd.DataFrame) -> str:
    rows = ["# Numbers in the paper and where they come from", "",
            "All paths are relative to `paper/results/`. The notebook `paper/reproduce_paper.ipynb` prints this table "
            "next to the values in the paper; this file is written by `python paper/paper_numbers.py --markdown`.", "",
            "Sect. 4.1–4.4 = the four unnumbered subsections of Section 4, in order. In the paper, LR is the "
            "L1-regularized logistic regression and L1 denotes label 1 (caption of Table 1); in the CSVs, the row "
            "names `L1-logistisch …` = LR.", "",
            "| Short | File |", "|---|---|"]
    rows += [f"| {k} | `{v}` |" for k, v in F.items()]
    rows += ["", "Column names in the CSVs are German: `stets falsch` = always wrong, `stets richtig` = always right, "
             "`erwartet` = expected, `Käufer` = buyer, `Kandidat` = candidate, `Kontrolle` = comparison customers "
             "(label 0, always right, not isolated), `gekippt` = flipped (planted), `ungekippt` = unflipped, "
             "`je Paar` = per pair, `je Code` / `je Schlüssel` = per code, `Mittel` = mean, `gepoolt` = pooled, "
             "`belegt` = evidence found, `Knick` = knee, `neu` = corrected NAICS matrix, `alt` = matrix published with "
             "ECML 2026.", "",
             "| Location | Quantity | Paper | From CSV | File | Column / row |", "|---|---|---|---|---|---|"]
    for r in df.itertuples():
        rows.append(f"| {r.location} | {r.quantity} | {r.paper} | {r.computed} | {r.file} | {r.column_row} |")
    rows += ["", "## Notes", "", NOTES]
    return "\n".join(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--markdown", action="store_true")
    a = ap.parse_args()
    df = entries()
    if a.markdown:
        out = HERE.parent / "docs" / "numbers.md"
        out.parent.mkdir(exist_ok=True)
        out.write_text(markdown(df), encoding="utf-8")
        print(f"written {out}")
    else:
        with pd.option_context("display.width", 200, "display.max_colwidth", 60, "display.max_rows", 200):
            print(df[["location", "quantity", "paper", "computed"]].to_string(index=False))


if __name__ == "__main__":
    main()
