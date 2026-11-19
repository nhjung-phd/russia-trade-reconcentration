# Verified results used in the final manuscript

This repository contains the executed structural and panel-robustness outputs used to prepare the final Korean manuscript for submission to *질서경제저널*.

## Structural results

- China share of Russian imports (BACI-observed trade): **+29.80 percentage points** from the 2019–2021 mean to the 2023–2024 mean.
- Balanced-partner sensitivity: **+28.00 percentage points**.
- Bank of Russia BoP-denominator sensitivity: approximately **+12.89 percentage points**.
- China import-share HS4-cluster bootstrap 95% CI: **[22.54, 25.33] percentage points**.
- HS6 products with China share >= 90% in the balanced sample: **143 -> 844** (approximately **+489.9%**).
- Import-side bilateral exposure-gap change under BACI: **+28.70 percentage points**; under the BoP-denominator sensitivity definition, the absolute gap widens by about **+11.88 percentage points**, while ratio/log-ratio asymmetry changes little.

## Panel robustness results

### Partner-year fixed effects

- Import, `China x Post`: **0.30488** (about **+30.49 percentage points**), p < .001.
- Export, `China x Post`: **0.19815** (about **+19.82 percentage points**), p < .001.

### Hausman comparison

- Import: chi-square(5) = **74.99**, p < .001.
- Export: chi-square(5) = **133.96**, p < .001.

These diagnostics favor FE over RE for the reported interaction set. They are model-comparison diagnostics, not a causal-identification result.

### HS6 product fixed-effects event profiles

The Chinese import share shows a pre-2022 upward tendency and a marked acceleration after 2022. Relative to 2021, the within-HS6 China import-share profile rises by approximately **+21.84 percentage points in 2023** and **+26.58 percentage points in 2024**. This supports an interpretation of post-2022 acceleration rather than a completely new trend beginning in 2022.

### HS6 x partner-bloc PPML-HDFE

Relative to EU27, controlling for HS6-by-bloc fixed effects and year fixed effects:

- Import `China x Post`: beta = **1.6129**, p < .001; exp(beta)-1 = **+401.7%**.
- Export `China x Post`: beta = **2.2320**, p < .001; exp(beta)-1 = **+831.9%**.

The exponentiated PPML coefficients are **relative shifts versus the EU27 reference**, not absolute growth rates of China trade.

## Interpretation boundary

The study is a non-causal longitudinal structural analysis. The 2022 period combines war, sanctions, firm exit, Russian policy responses, energy-price changes, logistics and payment disruptions. FE and PPML-HDFE are therefore used as robustness checks for observed restructuring, not as identification of the causal effect of sanctions.
