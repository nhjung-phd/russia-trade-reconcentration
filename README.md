# Russia Trade Re-Concentration — Final Reproducibility Repository v3.0

This repository accompanies the manuscript by **Nak Hyun Jung (first author)** and **Taebeom Ahn (corresponding author)** on post-2022 Russian trade reorientation and partner re-concentration.

It contains both the **analysis code** and the **actual executed derivative outputs** used in the final Korean manuscript prepared for submission to *질서경제저널*.

## Recommended entry point

Use:

`notebooks/Russia_Trade_Full_AllInOne.ipynb`

A clean `Run all` performs the structural analysis and the additional panel robustness analysis in one workflow.

## What is included

### Structural analysis
- Partner shares and concentration measures
- HHI, CR1/CR3, Shannon entropy, effective number of partners
- HS6 pre/post distributional analysis
- Wilcoxon signed-rank tests
- Bootstrap and sign-flip permutation tests
- HS4-cluster bootstrap
- Balanced-partner sensitivity
- Bank of Russia denominator sensitivity
- China-dependence thresholds
- EU-to-China absorption diagnostics
- Energy/non-energy decomposition
- Bilateral trade-exposure-gap analysis

### Panel robustness
- Partner-year two-way fixed effects
- Random effects
- Hausman FE-vs-RE comparison
- HS6 product fixed-effects year profiles
- HS6 x partner-bloc PPML-HDFE with zero trade retained

These panel models are used as **robustness checks**, not as a causal identification strategy for sanctions.

## Final verified results

Selected results from the executed outputs:

- China share of Russian imports, BACI: **+29.80 pp**
- Balanced-partner sensitivity: **+28.00 pp**
- BoP-denominator sensitivity: **about +12.89 pp**
- HS4-cluster bootstrap CI for the mean HS6 China-import-share change: **[22.54, 25.33] pp**
- China share >= 90% HS6 products in the balanced sample: **143 -> 844**
- Partner FE `China x Post`: **+30.49 pp (imports)** and **+19.82 pp (exports)**
- Hausman: **chi-square(5)=74.99** for imports and **133.96** for exports, both p < .001
- PPML-HDFE `China x Post`: **beta=1.6129** for imports and **beta=2.2320** for exports, both p < .001

See `docs/RESULTS_SUMMARY.md` for interpretation and boundaries.

## Repository structure

```text
.
├── README.md
├── VERSION
├── CITATION.md
├── CITATION.cff
├── requirements.txt
├── .gitignore
├── SHA256SUMS.txt
├── REPRODUCIBILITY_CHECKLIST.md
│
├── data/
│   └── README.md
│
├── notebooks/
│   ├── Russia_Trade_Full_AllInOne.ipynb
│   ├── Russia_Trade_Master_Structural.ipynb
│   └── Russia_Trade_Panel_Robustness.ipynb
│
├── manuscript/
│   ├── Russia_Trade_Reconcentration_KR_Ordo_Final.docx
│   └── assets/
│
├── results/
│   ├── tables/
│   ├── figures/
│   ├── publication/
│   ├── Russia_Trade_Master_Final_Results.xlsx
│   ├── Russia_Trade_Master_Robustness_Results.xlsx
│   └── Russia_Trade_Panel_Robustness_Results.xlsx
│
└── docs/
    ├── RUN_FULL_ANALYSIS_KR.md
    └── RESULTS_SUMMARY.md
```

## Data

Raw CEPII BACI files are **not** redistributed here. See `data/README.md`.

The notebooks accept either the official `BACI_HS12_V202601.zip` source archive or the project Lite dataset. The repository includes only derivative outputs used in the manuscript.

## Quick reproduction in Google Colab

1. Upload `notebooks/Russia_Trade_Full_AllInOne.ipynb` to Colab.
2. Upload or mount `Russia_BACI_Lite_Dataset.zip` or the official `BACI_HS12_V202601.zip`.
3. Select **Runtime -> Run all**.
4. Compare the generated outputs with the checked-in `results/` directory.

Detailed Korean instructions are in `docs/RUN_FULL_ANALYSIS_KR.md`.

## Interpretation boundary

This is a longitudinal structural study using repeated country- and product-level trade observations. It does not claim that the reported post-2022 changes are the pure causal effect of sanctions. War, sanctions, firm exit, Russian policy responses, energy prices, logistics, and payment disruptions changed simultaneously.

## Release

Repository release: **v3.0-final-results**

This release integrates the final manuscript and the actually executed panel-robustness outputs.
