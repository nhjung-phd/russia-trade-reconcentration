# Russia Trade Re-Concentration after 2022

Replication repository for the study **“Trade Reorientation and Partner Re-Concentration in Russia after 2022: China-Centered Import Re-Concentration, Export-Market Reorientation, and Longitudinal Panel Robustness.”**

**Authors**
- Nak Hyun Jung — first author
- Taebeom Ahn — corresponding author

Repository: https://github.com/nhjung-phd/russia-trade-reconcentration

> The repository is currently private during manuscript review. Access may be provided to editors and reviewers upon request.

## What is included

- Final No-DID manuscript
- Final No-DID All-in-One replication notebook
- Executed notebook used for the archived results
- Study-specific `Russia_BACI_Lite_Dataset.zip`
- Actual statistical outputs, CSV tables, Excel workbooks, model summaries, and PNG figures
- Publication-ready tables and figures
- Reproducibility and data/code-availability documentation

## Repository structure

```text
russia-trade-reconcentration/
├── README.md
├── VERSION
├── CITATION.cff
├── requirements.txt
├── SHA256SUMS.txt
├── data/
│   ├── README.md
│   └── Russia_BACI_Lite_Dataset.zip
├── notebooks/
│   ├── Russia_Trade_Full_AllInOne_NoDID.ipynb
│   └── Russia_Trade_Full_AllInOne_NoDID_executed.ipynb
├── manuscript/
│   └── Russia_Trade_Reconcentration_KR_Ordo_Final_NoDID.docx
├── results/
│   ├── tables/
│   ├── figures/
│   ├── publication/
│   └── *.xlsx / model summaries / metadata
└── docs/
    ├── DATA_AND_CODE_AVAILABILITY.md
    ├── RESULTS_SUMMARY.md
    └── REPRODUCIBILITY.md
```

## Data

The study uses CEPII BACI HS2012 V202601 for 2015–2024. The repository contains a **study-specific Russia-focused derivative dataset**, not the full BACI archive. See `data/README.md`.

## Main analyses

1. Partner shares and trade-concentration indices (HHI, CR1/CR3, Shannon entropy, effective number of partners)
2. HS6-level pre/post distributional tests
3. Balanced-partner and Bank of Russia denominator sensitivity
4. HS4-cluster bootstrap and additional robustness checks
5. Partner-year FE/RE and Hausman specification tests
6. HS6 product fixed-effects year profiles
7. HS6×partner-bloc PPML-HDFE

**No Difference-in-Differences analysis is included in the final source or reported results.**

## Reproduce

See `docs/REPRODUCIBILITY.md`. The quickest route is to run the clean notebook with the included Lite dataset.

## Key verified findings

- China import share: **+29.80 pp** in BACI-observed trade
- Balanced-partner estimate: **+28.00 pp**
- Official-denominator sensitivity: approximately **+12.89 pp**
- Partner-year FE China×Post: **+30.49 pp imports**, **+19.82 pp exports**
- Hausman tests favor FE for both import and export panels
- PPML-HDFE confirms significant post-2022 relative shifts toward China versus EU27

See `docs/RESULTS_SUMMARY.md` for details and interpretation cautions.

## Data and Code Availability

The full statement used for manuscript submission is in `docs/DATA_AND_CODE_AVAILABILITY.md`.

## Review status

This package is prepared for manuscript review. Keep the repository private until the journal's review and repository policies permit public release.
