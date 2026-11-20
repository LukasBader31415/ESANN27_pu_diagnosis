# Numbers in the paper and where they come from

All paths are relative to `paper/results/`. The notebook `paper/reproduce_paper.ipynb` prints this table next to the values in the paper; this file is written by `python paper/paper_numbers.py --markdown`.

| Short | File |
|---|---|
| OOF | `2026-11-11_A_auswertung_naicsfix/hub_oof_profil.csv` |
| LIST | `2026-11-11_A_auswertung_naicsfix/hauptliste_neu.csv` |
| KV | `2026-11-11_A_auswertung_naicsfix/kverlauf_s1.csv` |
| EB | `2026-11-11_A_auswertung_naicsfix/eval_beschreibend.csv` |
| AN | `2026-11-11_A_auswertung_naicsfix/vergleich_alt_neu.csv` |
| KNEE | `2026-11-10_A_L2_hub/isolation_knick.csv` |
| REF | `2026-11-11_A_AP2_hub_naicsfix/vergleichsmodelle.csv` |
| TWP | `2026-11-11_A_AP2_hub_naicsfix/zwillinge_paare.csv` |
| TWA | `2026-11-11_A_AP2_hub_naicsfix/zwillinge_pair_auc.csv` |
| RAW | `2026-11-11_A_AP2_hub/roh_innerhalb_naics.csv` |
| IND | `2026-11-07_A_R9_stufe1/r9s1_beschreibend.csv` |
| SIM | `2026-11-07_A_R9_steckbrief/sb_aehnlichkeit.csv` |
| SPY | `2026-11-12_A_spy_naicsfix/spy_trennung.csv` |
| R10E | `2026-11-17_A_R10_auswertung/r10_erwartung.csv` |
| R10G | `2026-11-17_A_R10_auswertung/r10_gruppen.csv` |
| R10D | `2026-11-17_A_R10_auswertung/r10_drift.csv` |
| FILT | `2026-11-17_A_R13_reject_filter/filter_varianten.csv` |
| REJ | `2026-11-17_A_R13_reject_filter/reject_kurve.csv` |
| TOP | `2026-11-17_A_R13_reject_filter/vertrieb_top.csv` |
| SIZE | `2026-11-17_A_R14_groesse_pflanz/groesse_zwillinge.csv` |
| SIZEM | `2026-11-17_A_R14_groesse_pflanz/groesse_modelle.csv` |
| PLANT | `2026-11-17_A_R14_groesse_pflanz/pflanz_modelle.csv` |
| MATV | `2026-11-18_A_R15_werkstoffe/views_neu.csv` |
| MATM | `2026-11-18_A_R15_werkstoffe/werkstoff_modelle.csv` |
| MAT4 | `2026-11-18_A_R15_werkstoffe/stufe3_fits.csv` |

Column names in the CSVs are German: `stets falsch` = always wrong, `stets richtig` = always right, `erwartet` = expected, `Käufer` = buyer, `Kandidat` = candidate, `Kontrolle` = comparison customers (label 0, always right, not isolated), `gekippt` = flipped (planted), `ungekippt` = unflipped, `je Paar` = per pair, `je Code` / `je Schlüssel` = per code, `Mittel` = mean, `gepoolt` = pooled, `belegt` = evidence found, `Knick` = knee, `neu` = corrected NAICS matrix, `alt` = matrix published with ECML 2026.

| Location | Quantity | Paper | From CSV | File | Column / row |
|---|---|---|---|---|---|
| Abstract, Sect. 1, 2 | customers | 2,025 | 2,025 | OOF | `n`, rows frozen / neu, label 0 + label 1 |
| Abstract, Sect. 2 | BA of the frozen model | .585 | .585 | EB | `neu_ba_end`, variant frozen (also REF row `frozen K 6`) |
| Sect. 1 | BA of the prototype model of the ECML 2026 paper | about .59 | external | – | number from the ECML 2026 paper (Table 8 there), not from this repository (see note 1) |
| Sect. 2 | buyers (label 1) | 1,038 | 1,038 | OOF | `n`, frozen / neu / label 1 |
| Sect. 2 | no observed purchase (label 0) | 987 | 987 | OOF | `n`, frozen / neu / label 0 |
| Sect. 2 | base rate | .51 | .51 | TOP | `grundrate` (= 1038 / 2025 = .513) |
| Fig. 1b (label in the figure) | base rate | .51 | .51 | TOP | `grundrate` |
| Sect. 2 | learned weights exceed frozen by at most (K between 2 and 20) | .006 | .006 | KV | max over K of `ba_end`(learned) − `ba_end`(frozen), stand neu (see note 2) |
| Sect. 2 | frozen BA over K (K = 4–20 in this file) | changes not substantially | .577–.587 | KV | `ba_end`, variant frozen, stand neu (see note 2) |
| Sect. 3 | isolated: knee of the distance curve | 17.6 % | 17.6 % | KNEE | `knick_obere_anteil` (published matrix; corrected matrix see note 3) |
| Sect. 3 | candidates (fixed on the published matrix) | 319 | 319 | LIST | row `Gruppe Kandidat`, `n_alt` |
| Sect. 3 | of these, also candidates on the corrected matrix | 247 | 247 (= 77 %) | LIST | row `Gruppe Kandidat`, `schnitt` |
| Sect. 3 | industry twin pairs | 11,205 | 11,205 | TWP | `n_paare`, row naics_primaer |
| Sect. 3 | customers in twin pairs | 1,851 | 1,851 | TWP | `n_kunden_in_paaren` |
| Sect. 3 | primary codes with twin pairs | 139 | 139 | TWP | `n_schluessel` |
| Sect. 3 | share of buyers flipped | 10 % | 10 % | PLANT | `n_gekippt` / 1038 |
| Sect. 3, Fig. 1a | random draws of planted buyers | three | 3 | PLANT | `seed` 101, 102, 103 (row `Mittel` = pooled over the draws) |
| Tab. 1, Sect. 4.1 | label 0 always wrong, observed | 463 | 463 | OOF | `stets_falsch`, frozen / neu / label 0 |
| Tab. 1, Sect. 4.1 | label 0 always wrong, expected (null model) | 117 | 117 | OOF | `erwartet_falsch`, label 0 |
| Tab. 1, Sect. 4.1 | buyers always wrong, observed | 184 | 184 | OOF | `stets_falsch`, label 1 |
| Tab. 1 / Sect. 4.1 | buyers always wrong, expected | 1 / fewer than one | 1 / fewer than one (0.64) | OOF | `erwartet_falsch`, label 1 |
| Tab. 1 | control of the reference models: frozen model | BA .585 | BA .585 | REF | row `frozen K 6` |
| Tab. 1, Sect. 4.1 | BA of RF, HGB, L1, SVM | .56–.59 | .56–.59 | REF | `ba_mittel`, rows HGB, Random Forest, L1, SVM (see note 6) |
| Sect. 3, Tab. 1 | control: primary codes only | .50 | .50 | TWA | `pair_auc`, naics_primaer / NAICS nur Primärcode / je Paar / alle |
| Sect. 4.2 | pair AUC products (HS) | .50 | .50 | TWA | score `HS (k 15)`, je Paar, alle |
| Sect. 4.2 | pair AUC applications | .50 | .50 | TWA | score `AM (k 31)`, je Paar, alle |
| Sect. 4.2 | pair AUC full NAICS view | .57 | .57 | TWA | score `NAICS voll (k 31)`, je Paar, alle |
| Tab. 1 | views (range) | .50–.57 | .50–.57 | TWA | HS, AM, NAICS voll |
| Sect. 4.2 | single features tested within industries | 104 | 104 | RAW | rows |
| Sect. 4.2 | carriers per feature at least | 20 | 20 | RAW | `n_traeger_in_schichten` (min) |
| Sect. 4.2 | smallest q of the single features | q > .8 | q ≥ .821 | RAW | `q_bh` (min; see note 4) |
| Tab. 1, Sect. 4.2 | pair AUC company size [95 % interval] | .56 [.53, .60] | .56 [.53, .60] | SIZE | `pair_auc`, `ci_lo`, `ci_hi`, employees_total / je Paar (revenue .56 as well) |
| Tab. 1, Sect. 4.2 | pair AUC materials [95 % interval] | .55 [.52, .59] | .55 [.52, .59] | MATV | `pair_auc`, `ci_lo`, `ci_hi`, view V3 (materials only; see note 5) |
| Sect. 4.2 | materials as a fourth view, Δ BA | −.001 | −.001 | MAT4 | mean of `delta_ba` over 50 fits |
| Tab. 1, Sect. 4.2 | largest Δ BA from size or materials in any model | ≤ .02 | .019 | SIZEM, MATM, MAT4 | max of `ba_mittel` in Δ rows, and mean `delta_ba` |
| Tab. 1, Sect. 4.3, Fig. 1a | AUC planted vs. label 0, M³GLVQ | .61 | .61 | PLANT | `auc_gekippt`, seed Mittel, M³GLVQ |
| Tab. 1, Sect. 4.3, Fig. 1a | AUC planted vs. label 0, RF | .63 | .63 | PLANT | `auc_gekippt`, seed Mittel, RF |
| Tab. 1, Sect. 4.3, Fig. 1a | AUC planted vs. label 0, HGB | .62 | .62 | PLANT | `auc_gekippt`, seed Mittel, HGB |
| Tab. 1, Sect. 4.3 | planted minus unflipped buyers | as for other buyers | −.005, .006, .009 | PLANT | `diff_gekippt_minus_ungekippt`, seed Mittel |
| Sect. 4.3 | planted buyers among label-0 always wrong | 45 % | 45 % | PLANT | `anteil_gekippt_in_L0_stets_falsch`, M³GLVQ |
| Sect. 4.3 | share of planted buyers in that group | 14 % | 14 % | PLANT | `precision_liste`, M³GLVQ |
| Sect. 4.3 | times their share among label 0 in training | about 1.5 | 1.45 | PLANT | `lift` (= .138 / .095) |
| Tab. 1, Sect. 4.3 | spy AUC s̄, L1, HGB | .57–.58 | .57–.58 | SPY | `auc`, seed gepoolt, rows s̄, L1 stratified, HGB |
| Tab. 1, Sect. 4.3 | spy AUC within industries | .54 | .54 | SPY | `auc`, gepoolt, L1 grouped by primary code |
| Sect. 4.3 | cleaning flags label 0 | 53 % | 53 % | FILT | `anteil_entfernt_0_mittel` |
| Sect. 4.3 | cleaning flags buyers | 32 % | 32 % | FILT | `anteil_entfernt_1_mittel`, B1 |
| Tab. 1, Sect. 4.3 | Δ BA, both classes cleaned | −.006 | −.006 | FILT | `delta_ba_mittel`, B1 |
| Tab. 1, Sect. 4.3 | Δ BA, only label 0 cleaned | −.023 | −.023 | FILT | `delta_ba_mittel`, B2 (−.0235) |
| Sect. 4.3 | rejected at 70 % / 50 % coverage, candidates vs. comparison customers | less often | .072 vs. .098; .266 vs. .400 | REJ | `anteil_zurueckgewiesen_*`, stand neu, mitte 0 |
| Sect. 4.4 | candidates / comparison customers checked | 161 / 161 | 161 / 161 | R10G | `n` |
| Tab. 1, Sect. 4.4 | evidence: candidates | 17 % | 17 % | R10G | `anteil_belegt` (28/161) |
| Tab. 1, Sect. 4.4 | evidence: comparison customers | 19 % | 19 % | R10G | `anteil_belegt` (30/161) |
| Tab. 1, Sect. 4.4 | evidence: known buyers | 21 % | 21 % | R10G | `anteil_belegt` |
| Sect. 4.4 | known buyers with evidence | 32 of 155 | 32 of 155 | R10G | `n_belegt`, `n` |
| Sect. 4.4 | Fisher test buyers vs. comparison customers | p = .38 | p = .38 | R10E | `p` (one-sided) |
| Sect. 4.4 | agreement on re-checked companies | 37 of 40 | 37 of 40 | R10D | `wert` × `n`, row Firmenstatus gleich (.925) |
| Sect. 5, Fig. 1b | share of buyers in the top 5 % | .72 | .72 | TOP | `precision_kaeufer`, neu, .05 |
| Sect. 5 | base rate | .51 | .51 | TOP | `grundrate` |
| Sect. 4.1 (no number) | candidates as close to buyers as buyers to each other (combined distance) | as close | cand–buyer .57, within buyers .56, cand–comparison .75 | SIM | `mittel`, distanz kombiniert (frozen) |
| Sect. 4.1 (no number) | buyer share in own NAICS code (share difference) | almost as high as for buyers, far higher than for comparison customers | cand vs. buyers −.07, cand vs. comparison .73 | IND | `delta`, merkmal kaeuferanteil_naics_alt |

## Notes

1. The introduction quotes "about .59" for the prototype model of the ECML 2026 paper (Table 8 there); it is not
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
6. The reference models come from the run on the corrected matrix (`2026-11-11_A_AP2_hub_naicsfix`). The three models
   on raw features do not depend on the NAICS matrix; the SVM does (.558 here, .560 on the published matrix,
   `vergleich_alt_neu.csv`, rows "B5 BA").
