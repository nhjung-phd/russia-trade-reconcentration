# Reproducibility protocol

## 1. Environment

Recommended: Google Colab or Python 3.11+.

Install dependencies from `requirements.txt` or create the Conda environment using `environment.yml`.

## 2. Input

The repository already includes `data/Russia_BACI_Lite_Dataset.zip`.

- **Colab:** upload/copy this ZIP to `/content/Russia_BACI_Lite_Dataset.zip`.
- **Local:** set `RUSSIA_TRADE_ROOT` to the repository `data/` directory (or copy the ZIP to the configured analysis root).

## 3. Execute

Run every cell in:

`code/Russia_Trade_Corrected_Reanalysis_v2_4_FE_Fixed_Colab.ipynb`

The notebook is ordered so that **Run all** performs the complete workflow.

## 4. Mandatory audit checkpoints

A successful run should verify:

1. France code = 251 is observed and included in the EU27.
2. Italy is resolved unambiguously from 380/381.
3. EU27 member count = 27.
4. Main pre-period = 2019–2021.
5. 2022 is excluded from the main pre/post comparison.
6. Main post-period = 2023–2024.

Inspect:

- `results/tables/A0_country_code_audit.csv`
- `results/tables/A1_EU27_country_codes_used.csv`
- `results/logs/analysis_metadata_corrected.json`

## 5. Key numerical checks

The reproduced outputs should be consistent, up to normal numerical precision, with:

| Result | Expected value |
|---|---:|
| Import country HHI, pre | 0.082714 |
| Import country HHI, post | 0.298742 |
| Import EU27-bloc HHI, pre | 0.194991 |
| Import EU27-bloc HHI, post | 0.326003 |
| Export country HHI, pre | 0.047122 |
| Export country HHI, post | 0.148844 |
| Export EU27-bloc HHI, pre | 0.157296 |
| Export EU27-bloc HHI, post | 0.160417 |
| FE Import China × Post | +28.1522 pp |
| FE Export China × Post | +17.5029 pp |
| FE Export India × Post | +15.3537 pp |
| BoR denominator China-share change | +14.1311 pp |

## 6. PPML status

- Revised import PPML-HDFE: expected to report failure to converge within 1,000 demeaning iterations in the supplied run; this is **not** supporting evidence.
- Export PPML-HDFE: auxiliary result only; coefficients are conditional relative changes versus EU27, not absolute growth rates.

## 7. Output inventory

`results/OUTPUT_MANIFEST.csv` lists every generated table, figure, log, and workbook included in the release.

## 8. Non-causal interpretation

Do not reinterpret the FE coefficients, year profiles, or PPML coefficients as causal sanctions effects. The research design intentionally reports structural and longitudinal association/robustness evidence.
