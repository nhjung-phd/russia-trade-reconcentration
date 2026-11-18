# Publication-ready tables and figures

This folder provides a manuscript-numbered snapshot of the final tables and figures.

The CSV files under `tables/` are extracted directly from the final DOCX manuscript; the PNG files under `figures/` are mapped to the corresponding manuscript figure numbers.

## Tables

| Manuscript | File | Caption |
|---|---|---|
| Table 1 | `tables/Table_01.csv` | 선행연구 비교와 본 연구의 위치 |
| Table 2 | `tables/Table_02.csv` | 데이터와 연구설계 |
| Table 3 | `tables/Table_03.csv` | 주요 교역상대국 비중의 사전·사후 변화 |
| Table 4 | `tables/Table_04.csv` | 교역상대국 집중도 변화 |
| Table 5 | `tables/Table_05.csv` | 중국 고의존 HS6 품목 수의 변화 |
| Table 6 | `tables/Table_06.csv` | HS6 수준 사전·사후 변화의 통계검정 |
| Table 7 | `tables/Table_07.csv` | HS6별 EU27 감소와 중국 증가의 상관 |
| Table 8 | `tables/Table_08.csv` | HS27 제외 비에너지 HS6 통계검정 |
| Table 9 | `tables/Table_09.csv` | 대중국 원유 수출의 금액·물량·unit value 변화 |
| Table 10 | `tables/Table_10.csv` | 러시아-중국 bilateral trade exposure gap |
| Table 11 | `tables/Table_11.csv` | Baseline과 balanced-partner 수입구조 비교 |
| Table 12 | `tables/Table_12.csv` | Bank of Russia 총수입 분모와 BACI 커버리지 민감도 |
| Table 13 | `tables/Table_13.csv` | 중국 고의존 HS6: baseline과 balanced sample |
| Table 14 | `tables/Table_14.csv` | 수출 HS6 변화의 부호분해 |
| Table 15 | `tables/Table_15.csv` | 중국·인도 수출재편의 에너지 의존성 |

## Figures

| Manuscript | File | Caption | Source output |
|---|---|---|---|
| Figure 1 | `figures/Figure_01.png` | 러시아 수입의 주요 교역상대국 비중, 2015-2024 | `outputs/figures/Figure1_Import_Partner_Shares.png` |
| Figure 2 | `figures/Figure_02.png` | 러시아 수입·수출의 HHI, 2015-2024 | `outputs/figures/Figure2_Trade_Concentration_HHI.png` |
| Figure 3 | `figures/Figure_03.png` | 러시아 수입·수출의 유효 상대국 수, 2015-2024 | `outputs/figures/Figure2b_Effective_Number_of_Partners.png` |
| Figure 4 | `figures/Figure_04.png` | 중국 공급비중 50%·70%·90% 이상 HS6 품목 수 | `outputs/figures/Figure3_High_Dependence_HS6_Counts.png` |
| Figure 5 | `figures/Figure_05.png` | HS6별 중국 수입비중 사전·사후 변화분포 | `outputs/figures/Figure4_HS6_China_Share_Change_Distribution.png` |
| Figure 6 | `figures/Figure_06.png` | HS6별 EU27 수입비중 감소와 중국 수입비중 증가 | `outputs/figures/Figure5_HS6_EU_vs_China_Scatter.png` |
| Figure 7 | `figures/Figure_07.png` | 러시아-중국 bilateral trade exposure gap, 2015-2024 | `outputs/figures/Figure6_Bilateral_Exposure_Gap.png` |
| Figure 8 | `figures/Figure_08.png` | 연도별 관측 교역상대국 수 | `outputs/figures/Figure_R1_Partner_Coverage.png` |
| Figure 9 | `figures/Figure_09.png` | 중국 공급비중 90% 이상 품목: baseline vs balanced sample | `outputs/figures/Figure_R4_Extreme_Dependence_Balanced.png` |
| Figure 10 | `figures/Figure_10.png` | 수출 HS6 증가·0·감소 비중 | `outputs/figures/Figure_R5_Export_Sign_Decomposition.png` |
| Figure 11 | `figures/Figure_11.png` | EU 지배적 수입품목의 EU 감소와 중국 증가 | `outputs/figures/Figure_R7_EU_China_Absorption.png` |
| Figure 12 | `figures/Figure_12.png` | 대중국·대인도 수출의 HS27 금액비중 | `outputs/figures/Figure_R8_Export_Energy_Intensity.png` |

## Key robustness quantities

- BACI-observed China import-share change: **+29.80 percentage points**.
- Balanced-partner China import-share change: **+28.00 percentage points**.
- BoP-denominator sensitivity: **+12.89 percentage points**.
- BACI-based import exposure-gap change: **+28.70 percentage points**.
- BoP-denominator import exposure-gap change: **+11.88 percentage points**.
- Balanced-sample HS6 products with China share ≥90%: **+489.9%**.
- HS4-cluster bootstrap 95% CI for the mean HS6 China import-share change: **[22.54, 25.33] percentage points**.

For computational source files and diagnostic outputs, use `outputs/tables/` and `outputs/figures/`.
