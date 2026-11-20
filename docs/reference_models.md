# Reference models and main model

Settings as read from the code that produced the paper results (private development repository), not assumed.
Library versions: Python 3.12, scikit-learn 1.9.1, numpy 1.26.4, scipy 1.17.1, proto-dist-ml 1.0.1 (lock file of
the development environment; the versions on the compute server were not recorded separately).

The paper (Sect. 3) describes the reference models as "with class-balanced weights on the same splits". All four use
`class_weight="balanced"`; further settings that differ from the scikit-learn defaults (500 trees for the random
forest, one parameter tuned by inner cross-validation for L1 and the SVM, engineered input features) are listed below.
The numbers in the paper come from the run on the corrected NAICS matrix (`paper/results/2026-11-11_A_AP2_hub_naicsfix/
vergleichsmodelle.csv`, frozen model BA .585).

## Shared setup

- **Splits** (all models of Table 1 except where noted): 10 repetitions × stratified 5-fold,
  `StratifiedKFold(5, shuffle=True, random_state=2027 + rep)`; inside each training part, a stratified 20 %
  validation part is split off (`train_test_split(test_size=0.2, random_state=2027 + 1000·rep + fold)`) and **not
  used** by any model here; all models are trained on the remaining fit part. Checksum of all index arrays (int64,
  SHA-256, first 16 hex) `8b347df42b1a2c37`. Each customer gets 10 OOF predictions.
- **Dissimilarities**: each view scaled by the 5 % / 95 % quantiles of its upper triangle (all customers, no
  labels), clipped to [0, 1]. Combined distance = mean of the three views (= metric of the frozen model).
- **Raw features** (RF, HGB, L1): log1p of counts; 0/1 indicators for codes held by at least 20 customers
  (NAICS levels 2/3/4 of the primary code, HS 4-digit, application main and sub category); secondary-NAICS
  indicators; no further scaling except the standard scaler inside the L1 pipeline.
- **Scores**: AUC and pair AUC use the mean OOF score over the 10 repetitions (s̄ for M3GLVQ, `predict_proba[:, 1]`
  for RF/HGB/L1, `decision_function` for the SVM). BA uses `predict()` per fold, averaged over the 50 folds.

## Models

| Model | Class (library) | Settings that differ from the library defaults | Input |
|---|---|---|---|
| **M3GLVQ frozen** (main model) | `M3GLVQ_Global` (code in the companion repository ESANN27_weight_paths, based on proto-dist-ml MGLVQ) | K = 6 median prototypes per class, view weights fixed at a_v = 1/√3 (η = 0), T = 400 epochs, no early stop; initial prototypes by relational neural gas on the class sub-matrix of the combined distance (seed 42 + 100·rep + fold); prediction = nearest prototype; score s = (d0 − d1)/(d0 + d1 + 1e-5) | three views |
| **k-NN reference** | own code | k = 31 on the combined distance, exactly k neighbours from the fit part (stable sort; ties by index), score = share of buyers, prediction share > .5 | three views |
| **Random forest (RF)** | `RandomForestClassifier` (scikit-learn) | `n_estimators=500`, `class_weight="balanced"`, `random_state=20261111` | raw features with NAICS levels 2 and 3 |
| **Histogram gradient boosting (HGB)** | `HistGradientBoostingClassifier` | `class_weight="balanced"`, `random_state=20261111`, `categorical_features=[primary code]` (6-digit primary NAICS code as one categorical column, the 254 most frequent codes, the rest pooled) | raw features without NAICS levels, plus the primary code |
| **L1 logistic regression (L1)** | `StandardScaler` + `LogisticRegression` | `l1_ratio=1.0` (pure L1), `solver="liblinear"`, `class_weight="balanced"`, `max_iter=2000`; C ∈ {0.01, 0.1, 1, 10} by inner stratified 3-fold CV on the fit part (AUC, `random_state=20261111 + rep`); `vergleichsmodelle.csv` reports C = 0.1 (column `abstimmung`) | raw features with NAICS levels 2, 3 and 4 |
| **SVM** | `SVC(kernel="precomputed")` | `class_weight="balanced"`, C = 1; kernel exp(−f·g0·D) on the combined distance D, g0 = 1 / median of D on the fit part, f ∈ {0.5, 1, 2} by inner stratified 3-fold CV on BA (`random_state=20261111 + rep`); `vergleichsmodelle.csv` reports f = 1 | combined distance |
| **L1 grouped by primary code** (twins, spy "within industries") | as L1 | C ∈ {0.01, 0.03, 0.1, 0.3, 1, 3}, chosen by inner grouped 3-fold CV; outer CV: 5 folds grouped by primary code (groups permuted with seed 20261111 + rep and assigned by cumulative size), 10 repetitions; not the model splits; BA at threshold .5 | raw features without any primary-code feature |
| **Boosting depth 3** (size and materials, Sect. 4.2) | `HistGradientBoostingClassifier` | `max_depth=3`, `class_weight="balanced"`, `random_state=20261111 + rep`; folds as for L1 grouped | as L1 grouped (missing size values: native NaN) |

Size (Sect. 4.2): log1p(employees) and log1p(revenue, USD only) added to the features; RF and L1 impute the median
of the training part and add a missing-value indicator, HGB and boosting depth 3 use native NaN. Materials: number of
materials and 0/1 indicators for materials and material groups with at least 20 carriers.

## Planted buyers and spy (Sect. 4.3, Fig. 1a)

- **Flipped set**: one fixed set per seed, `default_rng(seed).choice(buyers, round(0.10 · 1038) = 104)`, seeds 101,
  102, 103; the set is flipped to label 0 in every fit (and validation) part; test labels stay unchanged.
- **M3GLVQ**: frozen K = 6 on the same 10 × 5 splits with the flipped training labels; score s̄.
  **RF, HGB**: as in the table above, trained on the flipped labels of the same splits; score = mean
  `predict_proba[:, 1]` over the repetitions.
- **AUC** of the flipped buyers against the true label-0 customers, and of the unflipped buyers against the true
  label-0 customers (Mann-Whitney, ties one half); per seed, and pooled over pairs within seeds ("Mittel"); 95 %
  intervals by a bootstrap over customers per seed and class (2000 draws, seed 20261111).
- **Always wrong** for the planted runs is counted against the training labels (flipped = 0).
- **Spy**: pool = training label 0, always wrong, not isolated. Scores: s̄ (planted M3GLVQ run); L1 with NAICS levels
  2/3/4 in its own stratified 5-fold CV (10 repetitions, seed 20261112 + rep); L1 grouped by primary code;
  HGB (`categorical_features=[primary code]`, `random_state=20261112 + rep`, without `class_weight`). OOF score = mean
  over repetitions. Spy threshold t = 5 % (10 %) quantile of s̄ among all 104 spies.

## Training filter (Sect. 4.3)

Wilson editing on the fit part only: leave-one-out k-NN on the combined distance, k = 31, all neighbours at distance
≤ d_k ("expand" ties), flagged if the share of buyers among the neighbours (> .5) predicts the other label. B1 removes
flagged customers of both classes, B2 only flagged label-0 customers; then the frozen model is refitted on the
filtered fit part with new initial prototypes and the same seed; test parts unchanged.

## Open points

- The library versions on the compute server were not recorded; the versions above are those of the development lock file.
