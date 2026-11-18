# Russia Trade Re-Concentration after 2022

Reproducibility repository for the manuscript:

**Trade Reorientation and Partner Re-Concentration in Russia after 2022: China-Centered Import Re-Concentration, Export-Market Reorientation, and Asymmetric Trade Exposure**

This repository contains the analysis notebook, derived tables and figures, robustness outputs, and the submission-ready manuscript. The study uses CEPII BACI V202601 (HS2012) bilateral merchandise-trade data for 2015–2024 and evaluates Russia's post-2022 trade reorientation as a descriptive structural and distributional change rather than as a causal effect of sanctions.

## Repository structure

```text
.
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   └── README.md
├── notebooks/
│   └── Russia_Trade_Master_AllInOne.ipynb
├── outputs/
│   ├── analysis_metadata.json
│   ├── tables/
│   ├── figures/
│   ├── Russia_Trade_Master_Final_Results.xlsx
│   └── Russia_Trade_Master_Robustness_Results.xlsx
└── manuscript/
    └── Russia_Trade_Reconcentration_Manuscript.docx
```

## Main reproducibility workflow

The master notebook is designed for Google Colab/Python and searches for input data in the following order:

1. `Russia_BACI_Lite_Dataset.zip` — a study-specific lightweight dataset created from the official BACI archive; or
2. `BACI_HS12_V202601.zip` — the official CEPII BACI V202601 HS2012 archive.

In Colab, upload one of the above ZIP files or place it in a mounted Google Drive location recognized by the notebook. Run the notebook from top to bottom. It creates the derived tables, figures, Excel workbooks, and consistency-audit outputs.

## Data availability and redistribution

The original CEPII BACI files are **not included in this repository**. Users should obtain BACI V202601 directly from CEPII and comply with CEPII's applicable data-use terms. The repository contains only code and derived analysis outputs used for reproducibility.

The Bank of Russia balance-of-payments merchandise-import values used for denominator sensitivity are pinned to a single publication vintage in the submission-ready notebook:

- 2021: USD 301.047 billion
- 2023: USD 303.086 billion
- 2024: USD 301.548 billion

These values are used only as a denominator-sensitivity bound because balance-of-payments merchandise imports and BACI customs-based trade are not conceptually identical.

## Analysis windows

- Full descriptive period: 2015–2024
- Pre period: 2019–2021
- Adjustment year: 2022
- Post period: 2023–2024

For the BoP denominator sensitivity, 2021 is the available pre benchmark used against the 2023–2024 post average. This is intentionally distinct from the main 2019–2021 BACI pre-period average and is documented in the notebook and manuscript.

## Main outputs

The notebook reproduces:

- partner-share and concentration measures: HHI, CR1/CR3, Shannon entropy, effective number of partners;
- HS6-level pre/post distributional statistics;
- Wilcoxon signed-rank, bootstrap, sign-flip permutation, and rank-biserial effect-size results;
- HS4-cluster bootstrap confidence intervals;
- balanced-partner robustness checks for post-2022 reporting discontinuity;
- Bank of Russia denominator-sensitivity bounds and BACI/BoP coverage ratios;
- BoP-denominator sensitivity for the Russia–China import-side exposure gap;
- extreme China-dependence thresholds at 50%, 70%, and 90%;
- EU27-decline/China-increase absorption diagnostics;
- energy/non-energy decomposition of exports to China and India;
- figures and final consistency-audit tables.

## Key robustness interpretation

The direction of China-centered Russian import re-concentration is robust, while its estimated magnitude depends on the denominator definition. The submission-ready manuscript distinguishes the approximately +29.8 percentage-point BACI-observed change, +28.0 percentage-point balanced-partner change, and the smaller BoP-denominator sensitivity estimate. For the import-side bilateral exposure result, the robust conclusion is limited to the widening of the absolute percentage-point difference; under the BoP denominator, ratio and log-ratio change only slightly.

## Software environment

Tested for a standard recent Google Colab/Python environment. Install required packages with:

```bash
pip install -r requirements.txt
```

The notebook also uses `google.colab` when executed in Colab; this module does not need to be installed separately in the Colab runtime.

## Publication-ready tables and figures

For a reviewer-friendly view that mirrors the final manuscript numbering, use [`publication/`](publication/README.md). It contains:

- `publication/tables/Table_01.csv` through `Table_15.csv`, extracted directly from the final manuscript;
- `publication/figures/Figure_01.png` through `Figure_12.png`, mapped exactly to the manuscript figure numbering; and
- `publication/KEY_RESULTS.md`, a concise navigation guide to the principal findings and robustness quantities.

The original computational outputs remain under `outputs/` for full traceability.

## Reproducibility notes

- Randomized procedures use the seed specified in the notebook.
- Raw BACI data are not redistributed.
- 2022 is treated as an adjustment year and excluded from the main pre/post averages.
- The study is descriptive/structural and does not claim causal identification of sanctions.
- Segmented-regression break screening is retained only as exploratory output because the annual time series is too short for strong formal break inference.

## Citation

If this repository is used in academic work, please cite the associated manuscript and CEPII BACI source. Update this section with the final journal citation/DOI after publication.

## Version

GitHub release package: **v1.4-reproducibility**  
Prepared from the submission-ready manuscript and master notebook. The notebook is intentionally distributed without saved cell outputs.


## Verified external references for this release

- Kolaja (2026) was verified as an online-first article in *Post-Communist Economies* (published online 3 November 2026; DOI 10.1080/14631377.2026.2757270).
- Głodowska et al. (2026) was verified in *The World Economy*, 49(8), 1692–1709 (DOI 10.1111/twec.70110).
- Bank of Russia BoP values were verified against *Russia’s Balance of Payments in 2019–2025 (Analytical Presentation)* (2026), Table 2; the direct source URL is recorded in the manuscript and data documentation.
- Gutmann et al. (2024) was verified as covering trade flows of 187 countries during 2002–2019 (DOI 10.1111/roie.12716).
- Detailed publisher/source verification notes are stored in `docs/REFERENCE_VERIFICATION.md`.
