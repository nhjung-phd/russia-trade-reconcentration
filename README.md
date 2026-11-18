# Russia's Post-2022 Trade Reorientation and Re-Concentration

Replication code, derived analytical data, tables, and figures for a structural empirical study of Russia's post-2022 trade reorientation.

## Research focus

The study examines whether Russia's post-2022 trade adjustment was associated with broad diversification or with renewed concentration on a smaller set of trading partners.

The empirical design is **non-causal**. It characterizes structural change rather than estimating the causal effect of sanctions.

The core analytical sequence is:

`Post-2022 trade reorientation → partner re-concentration → asymmetric bilateral trade exposure`

## Data source

The analysis uses **CEPII BACI, HS2012, Version 202601**, for 2015–2024.

Raw BACI data are not redistributed in this repository. Download the original source archive from CEPII:

https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/baci_webpage.html#download-links

Required raw file:

`BACI_HS12_V202601.zip`

## Study periods

- Full sample: 2015–2024
- Pre-period: 2019–2021
- Adjustment year: 2022
- Post-period: 2023–2024

## Main analyses

- Partner-share trajectories
- HHI, CR1, CR3, Shannon entropy, and effective number of partners
- China specificity relative to India and Türkiye
- HS6-level dependence thresholds
- Non-energy robustness
- Crude-oil value–quantity robustness
- Bilateral Russia–China trade exposure gap
- Exploratory structural-break screening
- HS6-level Wilcoxon, bootstrap, permutation, and effect-size analysis
- HS6-level EU27 decline vs China increase correlation

## Repository structure

```text
russia-trade-reconcentration/
├── README.md
├── requirements.txt
├── .gitignore
├── code/
│   ├── Russia_Trade_Master_AllInOne_Colab.ipynb
│   ├── 01_BACI_Russia_Extractor_Colab.ipynb
│   └── 02_Russia_HS6_Statistical_Analysis_Colab.ipynb
├── data/
│   ├── README.md
│   └── derived/
│       ├── russia_import_partner_hs6_year.parquet
│       ├── russia_export_partner_hs6_year.parquet
│       ├── russia_import_hs6_year_summary.parquet
│       ├── russia_export_hs6_year_summary.parquet
│       ├── china_world_trade_year.parquet
│       └── metadata.json
├── results/
│   ├── Russia_Trade_Master_Final_Results.xlsx
│   ├── analysis_metadata.json
│   ├── tables/
│   └── figures/
└── docs/
    ├── analysis_design.md
    ├── variable_dictionary.md
    └── replication_instructions.md
```

## Reproduce everything in one run

The recommended workflow is:

`code/Russia_Trade_Master_AllInOne_Colab.ipynb`

### From the raw BACI archive

1. Download `BACI_HS12_V202601.zip` from CEPII.
2. Put the file in `/content/BACI/` or `/content/drive/MyDrive/BACI/`.
3. Open the master notebook in Google Colab.
4. Run all cells.
5. The notebook automatically extracts the Russia-specific Lite dataset, runs T1–T8, performs HS6 statistical inference, and creates all tables and figures.

### From the Lite analytical dataset

If a local `Russia_BACI_Lite_Dataset.zip` is available, the master notebook detects it first and skips the raw-data extraction step.

## Main output files

`results/tables/` includes:

- partner-share summaries
- concentration indices
- HS6 dependence counts
- non-energy robustness
- crude-oil value/quantity results
- bilateral exposure-gap results
- structural-break screening
- HS6 statistical tests
- final consistency audit

`results/figures/` includes:

- import partner shares
- HHI
- effective number of partners
- high-dependence HS6 counts
- HS6 China-share change distribution
- HS6 EU27-vs-China share-change scatter
- bilateral exposure gap

## Statistical inference

The HS6 analysis reports:

- Wilcoxon signed-rank tests
- Bootstrap 95% confidence intervals
- Sign-flip permutation tests
- Rank-biserial effect sizes

These tests assess whether the post-2022 structural changes are systematic across products. They should not be interpreted as causal estimates.

## Reproducibility note

The repository contains the code, generated result tables, figures, and a Russia-specific derived analytical dataset. The original 1.2GB BACI archive is excluded.

Before public release, confirm that redistribution of the derived BACI extracts in `data/derived/` is compatible with the applicable CEPII/UN Comtrade terms. If not, delete `data/derived/`; the extractor notebook reproduces it from the official raw BACI archive.

## Citation

If this repository is associated with a published article, replace this section with the final article citation and DOI.

Suggested repository citation before publication:

> Jung, N. H., et al. Replication materials for *Russia's Post-2022 Trade Reorientation and Re-Concentration*. GitHub repository, 2026.

## License

No software or data license has been assigned in this package. Select an appropriate license before making the repository public. A common choice for code is MIT, while data redistribution rights should be evaluated separately.
