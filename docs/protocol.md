# The diagnosis protocol

A model trained on positive-unlabeled (PU) labels makes systematic errors: some label-0 objects are predicted as
positives in almost every repetition. Are they hidden positives (wrong labels) or look-alikes (overlapping classes)?
Each check below tests one possible explanation and has its own **control on the same data**, which shows whether the
check can detect anything at all.

**Ground rule.** A null result counts as a finding about the data only if the control of the check is passed.

In the paper, only the planted buyers were planned before the main run. The other checks were added later and are
exploratory, but each expectation was fixed before the check was computed.

The checks need only dissimilarity matrices (one per view) and PU labels, plus a group key per object for the twins
and raw features for the reference models and single-feature tests. Settings of all models:
`docs/reference_models.md`. The reusable package follows after the conference submission.

## Definitions

- **OOF**: 10 repetitions of stratified 5-fold cross-validation give ten out-of-fold predictions per object;
  s̄ = mean of the score s = (d0 − d1)/(d0 + d1) over the ten repetitions (d_c: distance to the closest prototype of
  class c).

- **Always wrong**: at most 2 of 10 OOF predictions correct (generally ≤ 20 %); **always right**: at least 9 of 10
  (≥ 90 %).
- **Isolated**: among the 10 % of objects with the largest mean distance to their 10 nearest neighbors (combined
  distance = mean of the views, all objects, no labels). Isolated objects are excluded from candidates and comparison
  customers, because their errors could stem from missing data rather than from overlapping classes. Sensitivity: the
  knee of the sorted distance curve (Kneedle) lies at 17.6 % on the NAICS matrix published with ECML 2026 and at
  14.7 % on the corrected one; with the knee as boundary, the candidate list shrinks from 319 to 303 on the published
  matrix; on the corrected matrix, where the 10 % rule also gives 319 candidates, it shrinks to 311
  (`paper/results/2026-11-10_A_L2_hub/isolation_knick.csv`, `2026-11-11_A_auswertung_naicsfix/vergleich_alt_neu.csv`).
- **Candidates**: label 0, always wrong for the model **and** the k-NN reference, not isolated.
  **Comparison customers**: label 0, always right for the model, not isolated.
- **Pair AUC**: over all pairs of a positive and a label-0 object with the same group key, the probability that the
  positive has the higher score (ties one half). Interval: cluster bootstrap over groups (2000 draws).
- **Reading of an AUC** (fixed before the paper's runs): *separates* if AUC ≥ .55 and the lower bound > .5;
  *does not separate* if the interval contains .5; otherwise *weak*.

## Checks

In the order of Table 1 of the paper; single features and the short list are reported in the text of the paper.

| Check | Question | Control | Output | Reading |
|---|---|---|---|---|
| **Error profile** | Are the errors tied to objects or to random splits? | binomial null model: each object correct with the pooled OOF recall of its class, independently per repetition; expected always wrong = n_c · P(X ≤ 2), X ~ Bin(10, recall_c) | observed vs. expected always wrong / always right per label | errors tied to objects if observed far above expected |
| **Reference models** | Are the errors specific to the model? | frozen model (BA .585); k-NN reference | BA of RF, HGB, L1 (raw features) and SVM (precomputed kernel exp(−γD) on the combined distance) | at the level of the frozen model = errors not specific to the model |
| **Twins** | Does anything separate positives from label 0 within a group? | a view that contains only the group key must give .50 (band [.48, .52], else the run is invalid) | pair AUC of the k-NN score of each view (k nearest of all objects, without the object and its partner, ties expanded) and of s̄ | AUC reading above |
| **Single features** | Does one raw feature separate positives within a group? | false discovery rate (Benjamini-Hochberg) | binary features with ≥ 20 carriers: Mantel-Haenszel odds ratio stratified by group (variance Robins-Breslow-Greenland), q-values; numeric features: pair AUC in the twins | q < .05 / AUC reading |
| **Planted positives** | Would a label error be found if there were one? | unflipped positives | one fixed set of 10 % of the positives flipped to 0 in training, per random draw (paper: three draws, seeds 101–103); AUC of s̄ for flipped vs. true label 0 and for unflipped positives vs. true label 0; share of flipped among label-0 always wrong, its precision and lift over the base rate | control passed if AUC ≥ target (paper: .70, fixed in advance); below the target, an empty error list is not informative |
| **Spy** | Do known positives hidden among the errors stand out? | the spies are known positives | pool = training label 0, always wrong, not isolated; AUC of s̄ for spies vs. true label 0 (pooled within draws, bootstrap over objects); additionally the share of true label 0 below the 5 % / 10 % quantile of s̄ among all spies | AUC reading; control passed if the lower bound > .5 |
| **Cleaning and reject** | Do the errors sit at a few mislabeled objects? | model without cleaning | Wilson editing on the fit part only (leave-one-out k-NN, k = 31, ties expanded), B1 remove flagged objects of both classes, B2 only flagged label 0; Δ BA per fold; reject curve on certainty \|s̄\|, share of candidates and comparison customers rejected | cleaning helps if Δ BA ≥ .01 (paper rule); candidates rejected less often than comparison customers = model is confident and still wrong |
| **Website check** (external check) | Do candidates show more evidence of need than comparison customers? | known positives (positive control) | share with evidence per group (undecidable = no evidence); one-sided Fisher tests positives vs. comparison customers and candidates vs. comparison customers | positive control passed if known buyers show more evidence than comparison customers; otherwise "no difference found, sensitivity of the check not established" |
| **Short list** | How useful is the ranking? | base rate | precision in the top q % by s̄ | under PU labels, precision underestimates the true share |
