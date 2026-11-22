# Russia Trade Re-Concentration — Reproducibility Package

This repository contains the corrected analysis code, compact analysis dataset, derived tables, figures, and reproducibility documentation for the Russia trade re-concentration study. The manuscript file itself is intentionally **not included**.

The analysis is **descriptive and longitudinal, not a causal identification design**. The principal comparison is 2019–2021 versus 2023–2024, with 2022 treated as an adjustment year.

## Key corrected findings

- Russia import country-level HHI: **0.0827 → 0.2987**.
- Russia import EU27-bloc HHI: **0.1950 → 0.3260**.
- Russia export country-level HHI: **0.0471 → 0.1488**.
- Russia export EU27-bloc HHI: **0.1573 → 0.1604**; in the balanced sample it declined **0.1857 → 0.1658**.
- China share of Russian imports: **23.86% → 53.65%**.
- Bank of Russia denominator sensitivity: **22.90% → 37.03%**, or **+14.13 pp**.
- Partner–year FE robustness: China × Post **+28.15 pp** for imports and **+17.50 pp** for exports; India × Post **+15.35 pp** for exports.
- Revised import PPML-HDFE did **not** converge within 1,000 demeaning iterations and is not used as supporting evidence; export PPML-HDFE is auxiliary only.

The machine-readable key-result summary is in `results/tables/T23_Manuscript_Key_Results_Summary.csv`; FE results are in `results/tables/T24_FE_Robustness_Estimates.csv`.

## Repository structure

```text
.
├── README.md
├── README_KR.md
├── CITATION.cff
├── requirements.txt
├── environment.yml
├── code/
│   ├── Russia_Trade_Corrected_Reanalysis_v2_4_FE_Fixed_Colab.ipynb
│   └── verify_release_outputs.py
├── data/
│   ├── Russia_BACI_Lite_Dataset.zip
│   └── README.md
├── results/
│   ├── tables/
│   ├── figures/
│   ├── logs/
│   ├── workbooks/
│   └── OUTPUT_MANIFEST.csv
└── docs/
    ├── CODEBOOK.md
    ├── REPRODUCIBILITY.md
    ├── RESULTS.md
    ├── CHANGELOG.md
    ├── LICENSE_NOTICE.md
    └── SHA256SUMS.txt
```

## Included analysis dataset

`data/Russia_BACI_Lite_Dataset.zip` is included in this release. It contains the compact inputs required by the notebook:

- `russia_import_partner_hs6_year.parquet`
- `russia_export_partner_hs6_year.parquet`
- `russia_import_hs6_year_summary.parquet`
- `russia_export_hs6_year_summary.parquet`
- `china_world_trade_year.parquet`
- `metadata.json`

The metadata identifies the source as **CEPII BACI HS2012 V202601**, covering 2015–2024. This is a compact analysis dataset, not the complete CEPII BACI distribution.

## Quick start — Google Colab

1. Download or clone this repository.
2. Upload `data/Russia_BACI_Lite_Dataset.zip` to `/content/`, preserving the filename `Russia_BACI_Lite_Dataset.zip`.
3. Open `code/Russia_Trade_Corrected_Reanalysis_v2_4_FE_Fixed_Colab.ipynb`.
4. Choose **Runtime → Run all**.
5. Compare generated outputs with `results/` and run `code/verify_release_outputs.py` for the release checks.

Expected Colab input path:

```text
/content/Russia_BACI_Lite_Dataset.zip
```

For local execution, see `docs/REPRODUCIBILITY.md`.

## Critical data-definition notes

- Main pre-period: **2019–2021**.
- Adjustment year: **2022**, excluded from the principal pre/post comparison.
- Main post-period: **2023–2024**.
- EU27 uses the current 27-member composition consistently over 2015–2024.
- France is represented by BACI/Comtrade customs-area code **251** in the supplied Lite dataset and is included in EU27.
- United Kingdom is excluded from EU27.
- Italy is resolved at runtime from candidate codes **380/381** according to the input dataset.
- FE coefficients are descriptive robustness estimates, not causal treatment effects.

## Reproducing the release checks

From the repository root:

```bash
python code/verify_release_outputs.py
```

The supplied release is expected to reproduce, within normal floating-point precision, the key values documented in `docs/REPRODUCIBILITY.md`.

## Data and redistribution note

This repository includes the author-prepared compact analysis ZIP supplied for reproducibility. It does **not** include the complete CEPII BACI source distribution. Before public redistribution, users should review the source provider's applicable terms; see `data/README.md` and `docs/LICENSE_NOTICE.md`.

## Citation

Use `CITATION.cff` for machine-readable citation metadata. The replication-package DOI recorded in the project is:

**10.5281/zenodo.24412589**
