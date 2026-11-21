# Russia Trade Structure Restructuring: Partner Re-Concentration and Product Composition

Replication package for the manuscript **“A Study on the Restructuring of Russia's Trade Structure: Focusing on Trade-Partner Re-Concentration and Product Composition.”**

**Authors**
- Nak Hyun Jung — First Author
- Taebum Ahn — Corresponding Author

Repository: `https://github.com/nhjung-phd/russia-trade-reconcentration`

> The repository may remain private during peer review. Public release of the study-specific BACI derivative dataset should follow the applicable CEPII BACI redistribution terms.

## Repository contents

```text
Russia_Trade_Reconcentration_GitHub_v2.0/
├── README.md
├── VERSION
├── requirements.txt
├── SHA256SUMS.txt
├── data/
│   ├── README.md
│   ├── Russia_BACI_Lite_Dataset.zip
│   └── product_codebook/
├── notebooks/
│   └── Russia_Trade_Full_AllInOne_NoDID_English.ipynb
├── src/
│   └── russia_trade_all_in_one_no_did.py
├── results/
│   ├── README.md
│   ├── MANUSCRIPT_TABLE_MAP.md
│   ├── all_tables/
│   ├── workbooks/
│   └── metadata/
├── figures/
│   ├── README.md
│   ├── manuscript_composite/
│   ├── individual_clean/
│   └── analysis_outputs/
├── manuscript/
│   ├── Russia_Trade_Reconcentration_EN_v15.8.docx
│   └── Russia_Trade_Reconcentration_KR_v15.8.docx
└── docs/
    └── REPRODUCIBILITY.md
```

## Data and empirical scope

- Source: CEPII BACI HS2012 V202601
- Period: 2015–2024
- Main pre-period: 2019–2021
- Transition year: 2022
- Main post-period: 2023–2024
- Product unit: HS6
- Structural measures: partner shares, HHI, CR1/CR3, Shannon entropy, effective number of partners
- Distributional inference: Wilcoxon signed-rank test, bootstrap confidence intervals, sign-flip permutation tests, rank-biserial correlation, HS4-cluster bootstrap
- Panel analyses: partner-year FE/RE, Hausman tests, HS6 fixed-effects year profiles, PPML-HDFE

**No Difference-in-Differences analysis is included in the final source package.**

## Main result files

Machine-readable outputs are in `results/all_tables/`. See `results/MANUSCRIPT_TABLE_MAP.md` for the mapping between manuscript Tables 4–13 and the corresponding CSV outputs.

The package also includes the full HS6 product list with English descriptions in `data/product_codebook/`.

## Figures

- Final composite figures: `figures/manuscript_composite/`
- Clean individual figure files: `figures/individual_clean/`
- Complete analysis-generated figure set: `figures/analysis_outputs/`

## Source code

The primary replication source is `notebooks/Russia_Trade_Full_AllInOne_NoDID_English.ipynb`. A script export is provided in `src/russia_trade_all_in_one_no_did.py`. Korean comments, markdown explanations, and user-facing source messages have been translated to English.

## Reproduction

See `docs/REPRODUCIBILITY.md`. The recommended workflow is Google Colab with the included study-specific Lite dataset.

## Interpretation caution

The analyses document structural and longitudinal changes in Russia-related trade after 2022. The design does not isolate the pure causal effect of sanctions because the war, sanctions, corporate exits, payment and logistics changes, energy-price shocks, and Russian countermeasures occurred concurrently.

## Key manuscript-consistent results

- Import HHI: 0.0827 → 0.2987
- Import effective number of partners: 12.16 → 3.38
- Export HHI: 0.0471 → 0.1488
- Export effective number of partners: 21.24 → 6.77
- China share of Russian imports: 23.86% → 53.65%
- Balanced-partner China import-share change: +28.00 percentage points
- Bank of Russia denominator sensitivity: approximately +12.89 percentage points from 2021 to the 2023–2024 average
- Mean HS6-level China import-share change: +23.94 percentage points
- Mean HS6-level China export-share change: +2.38 percentage points

These values should be read together with the coverage and denominator-sensitivity results in the manuscript.
