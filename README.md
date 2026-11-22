# Russia Trade Restructuring: Full Reproducibility Package

[![DOI](https://zenodo.org/badge/1462838898.svg)](https://doi.org/10.5281/zenodo.24412588)

This repository contains the full reproducibility package for the study of Russia's post-2022 trade restructuring, trade-partner concentration, and HS6 product composition.

## Version

Repository package version: **1.1.0**

The DOI badge points to the Zenodo **Concept DOI** so that it continues to resolve to the latest archived release. A new Zenodo Version DOI should be recorded after the corrected v1.1.0 GitHub release is archived.

## Main analytical corrections in v1.1.0

- France is coded as **251** in the analytical BACI/Comtrade country coding used here.
- Italy is detected from the actual input data as **380 or 381** rather than assumed.
- EU27 is checked to contain exactly 27 members.
- Country-level concentration and EU27-as-one-bloc concentration are reported in parallel.
- The main comparison is consistently **2019-2021 vs 2023-2024**.
- **2022 is excluded** from the main pre/post comparison and treated as an adjustment year.
- Bank of Russia denominator sensitivity uses the same 2019-2021 pre-window where possible.
- Conventional singleton-country FE p-values and Hausman tests are not treated as primary evidence.
- Revised PPML-HDFE is retained only as an auxiliary specification.

## Important PPML note

In the corrected v2.1 run, the revised **import PPML-HDFE did not converge** (`Demeaning failed after 1000 iterations`). This failure is preserved in the output package and must not be replaced with an invented estimate. Export PPML output is retained as an auxiliary result. The main conclusions should rely on the concentration, HS6, balanced-sample, and denominator-sensitivity evidence.

## Repository structure

```text
.
├── README.md
├── CITATION.cff
├── VERSION
├── requirements.txt
├── SHA256SUMS.txt
├── src/
│   └── russia_trade_reanalysis.py
├── notebooks/
│   └── Russia_Trade_Reanalysis_Colab.ipynb
├── config/
│   └── country_code_reference_used.csv
├── data/
│   ├── Russia_BACI_Lite_Dataset.zip
│   ├── Russia_HS6_Full_Product_List_Study_v1.1_Final.csv
│   └── README.md
├── results/
│   ├── tables/
│   ├── workbooks/
│   ├── OUTPUT_MANIFEST.csv
│   └── README.md
├── figures/
├── logs/
├── docs/
└── archives/
    └── Russia_Trade_Corrected_Reanalysis_Outputs_v2_1.zip
```

## Input data

The reproducibility input is:

`data/Russia_BACI_Lite_Dataset.zip`

The package contains the study-specific light analytical dataset used by the code. The original source is CEPII BACI V202601 / HS2012. See `data/README.md` and `docs/DATA_NOTICE.md` before public redistribution.

## How to reproduce in Google Colab

1. Open `notebooks/Russia_Trade_Reanalysis_Colab.ipynb` in Google Colab.
2. Upload `data/Russia_BACI_Lite_Dataset.zip` to `/content/`.
3. Run the notebook cells in order.
4. The notebook creates tables, figures, logs, a combined Excel workbook, and a final ZIP.
5. The final output archive is named:

`Russia_Trade_Corrected_Reanalysis_Outputs_v2_1.zip`

## Key result tables

- `T01_Country_and_EU27_Bloc_Concentration_by_Year.csv` — annual country- and bloc-level concentration measures.
- `T02_Country_and_EU27_Bloc_Concentration_PrePost.csv` — main concentration pre/post summary.
- `T04_Major_Partner_Group_Shares_PrePost.csv` — corrected partner-group shares including corrected EU27.
- `T06_HS6_Distributional_Statistics.csv` — HS6 distributional changes and inference.
- `T08_EU27_China_HS6_CoMovement_Summary.csv` — EU27 decline / China increase co-movement summary.
- `T15_Balanced_Partner_Shifts_and_Placebo_Ranks.csv` — balanced-panel focal-partner shifts and placebo ranks.
- `T16_Balanced_Country_and_EU27_Bloc_Concentration_PrePost.csv` — balanced-sample concentration sensitivity.
- `T19_Bank_of_Russia_Denominator_Sensitivity_PrePost.csv` — Bank of Russia denominator sensitivity using aligned pre/post periods.
- `T20_HS6_Balanced_Year_Profiles_All_Focal_Groups.csv` — longitudinal HS6 profiles.
- `T21_Revised_PPML_HDFE_Import.csv` / `T22_Revised_PPML_HDFE_Export.csv` — auxiliary PPML outputs; see convergence note above.
- `T23_Manuscript_Key_Results_Summary.csv` — compact manuscript-facing key results.

## Figures

All figures are stored in `figures/`. Figure images deliberately contain **no title at the top**. Their filenames identify their content. Axis labels, legends, and reference lines remain inside the images.

## HS6 product list

`data/Russia_HS6_Full_Product_List_Study_v1.1_Final.csv` contains the study's HS6 product list and product descriptions for transparent product-level inspection.

## Reproducibility metadata

- `logs/analysis_metadata_corrected.json` records the design settings used in the corrected run.
- `logs/RUN_SUMMARY.txt` records the country-code and period configuration.
- `results/OUTPUT_MANIFEST.csv` lists the generated outputs.
- `SHA256SUMS.txt` provides file hashes for integrity checking.

## Citation

For GitHub, use the Concept DOI badge above. After Zenodo archives the corrected v1.1.0 release, use that release's **Version DOI** in the manuscript when citing the exact replication snapshot.
