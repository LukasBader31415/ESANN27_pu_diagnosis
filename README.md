# When misclassified is not mislabeled

Code and aggregated results for

> Lukas Bader, Ina Terwey-Scheulen and Dietlind Zühlke. *When misclassified is not mislabeled: a controlled diagnosis
> of systematic errors in positive-unlabeled customer data.* ESANN 2027 (submitted).


```bibtex
@inproceedings{bader_2027_misclassified,
  author    = {Bader, Lukas and Terwey-Scheulen, Ina and Z{\"u}hlke, Dietlind},
  title     = {When misclassified is not mislabeled: a controlled diagnosis of systematic errors in
               positive-unlabeled customer data},
  booktitle = {European Symposium on Artificial Neural Networks, Computational Intelligence and Machine Learning (ESANN 2027)},
  year      = {2027},
  note      = {submitted}
}
```

## Summary

In B2B sales, purchase data are positive-unlabeled (PU): a customer without an observed purchase may still need the
product. On 2,025 real customers, a prototype-based model makes systematic errors, and we propose a diagnosis protocol
in which every check has its own control on the same data to ask whether these errors are hidden buyers. The errors
are systematic but the customers are look-alikes of buyers: nothing but company size and processed materials separates
them within an industry (weakly), planted label errors are found no better than other buyers, and a website check with
an LLM agent fails its positive control.

## Data

The customer data are confidential and not part of this repository. It contains only aggregated results
(`paper/results/`, CSV), from which every number, Table 1 and Fig. 1 of the paper are recomputed. Rows per code
(industry, product, material, application) are included only if at least 10 companies carry the code. The enrichment
pipeline and the LLM agent are proprietary and not part of this repository; aggregated counts are given.

**NAICS distance.** The industry view uses a level-based prefix distance: d = 1 − ℓ/5, where ℓ is the number of
shared levels of the five-level NAICS hierarchy (2 to 6 digits); where a secondary code exists, d is the minimum over
the code pairs, with a surcharge of .15 for each secondary code involved. The NAICS matrix published with our ECML
2026 paper contained a normalization error. The candidate list and the website check were fixed on that published
matrix before the error was found (247 of the 319 candidates are also candidates on the corrected matrix); all other
results use the corrected matrix.

**Customer groups.** *Candidates* are label-0 customers that are always wrong (at most 2 of 10 out-of-fold predictions
correct) for both the frozen model and a k-NN reference and are not isolated. *Comparison customers* are label-0
customers that are always right (at least 9 of 10) and not isolated. *Isolated* customers (the 10 % with the largest
mean distance to their ten nearest neighbors) are excluded, because their errors could stem from missing data rather
than overlap. The knee of the sorted distance curve lies at 17.6 % on the published NAICS matrix and at 14.7 % on the
corrected one (`paper/results/2026-11-20_A_isolation_knick_naicsfix/isolation_knick.csv`); with the knee as boundary, the candidate list shrinks from 319 to 303 on the published matrix; on the
corrected matrix, where the 10 % rule also gives 319 candidates, it shrinks to 311 (`docs/numbers.md`, note 3).

## Quickstart

Python 3.12.

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt          # Windows: .venv\Scripts\pip
.venv/bin/jupyter nbconvert --to notebook --execute paper/reproduce_paper.ipynb --output-dir output
```

- `paper/reproduce_paper.ipynb` (a few seconds): every number of the paper next to the value from the CSVs (the
  notebook stops if a number differs), Table 1 rebuilt and checked row by row, Fig. 1 in final size
  (`output/fig1.pdf`, `.png`). `docs/numbers.md` maps every number to file, column and row.

## The diagnosis protocol

The protocol needs only dissimilarity matrices (one per view) and labels, so it runs unchanged on new features or a
new enrichment. `docs/protocol.md` describes each check (question, control, reading) and `docs/reference_models.md`
the settings of the main model and the reference models. The reusable package follows after the conference
submission.

## Repository layout

```
paper/results/                aggregated results that feed the paper (one folder per evaluation run)
paper/paper_numbers.py        every number of the paper from the CSVs (writes docs/numbers.md)
paper/figures/make_fig1.py    Fig. 1
paper/reproduce_paper.ipynb   numbers, Table 1, Fig. 1
docs/                         numbers.md, protocol.md, reference_models.md
```

Column names in the result files are German; `docs/numbers.md` gives the translations used.

## Pre-registration

Expectations, thresholds and decision rules were committed in the private development repository before the
corresponding results were computed (the development history itself is not published). Commit times (UTC):

| Rule | Committed | Results |
|---|---|---|
| Target AUC .70 for planted buyers (`criteria_A.yaml`) | `b7eedc9`, 2026-10-21 19:53; precision of the score `4146889`, 2026-10-23 08:47 | `70d65ca`, 2026-10-23 09:57 |
| Candidate list fixed by SHA-256 checksums | `70d65ca`, 2026-10-23 09:57 | website check from 2026-11-04 on |
| Planted buyers, fixed set (seeds 101–103) and expectations (`criteria_A_R.yaml`) | `49e99ec`, 2026-10-23 10:50 | `6742bae`, 2026-10-23 13:39 |
| Website check: rule and sampling (`criteria_A_R8.yaml`) | `f10ea54`, 2026-11-04 16:52 | sample drawn `e6d8089`, 2026-11-04 16:59 |
| Website check: prompt, process steps and signal words with checksum | `c3ca9e0`, 2026-11-06 08:26 | agent results 2026-11-06 |
| Website check: evaluation rules, before unblinding (`auswertung_R8.yaml`) | `a60975e`, 2026-11-06 12:51 | `d76fc2d`, 2026-11-06 13:06 |
| Positive control of the website check (`criteria_A_R10.yaml`) | `af427c7`, 2026-11-13 13:20 | `4060d7f`, 2026-11-17 14:04 |
| Size within industries, planted buyers with RF/HGB | `7cf15db`, 2026-11-17 12:23 | `66a73cd`, 2026-11-17 16:24 |

Only the planted buyers were planned before the main run. The other checks were added later and are exploratory, but
each expectation was fixed before the check was computed.

## Use of AI

An AI assistant supported code development and language editing; the authors verified all results and take full
responsibility.

## License

Code: GNU General Public License v3.0 (`LICENSE`), as for the companion repository ESANN27_weight_paths and the
package that follows (its model code is derived from the GPL-licensed MGLVQ code in proto-dist-ml). Results in `paper/results/`:
Creative Commons Attribution 4.0 International (CC BY 4.0, `paper/results/LICENSE.md`).
