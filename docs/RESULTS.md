# Result map

## Concentration

Source: `results/tables/T23_Manuscript_Key_Results_Summary.csv`

| Flow | Definition | HHI pre | HHI post | Interpretation |
|---|---|---:|---:|---|
| Import | Country | 0.0827 | 0.2987 | Strong re-concentration |
| Import | EU27 as one bloc | 0.1950 | 0.3260 | Re-concentration remains |
| Export | Country | 0.0471 | 0.1488 | Country-level concentration rises |
| Export | EU27 as one bloc | 0.1573 | 0.1604 | Little overall bloc-level change |

## Partner–year FE robustness

Source: `results/tables/T24_FE_Robustness_Estimates.csv`

| Flow | Interaction | Coefficient (pp) |
|---|---|---:|
| Import | China × Post | +28.15 |
| Import | India × Post | +0.67 |
| Import | Türkiye × Post | +2.46 |
| Import | Kazakhstan × Post | +2.18 |
| Import | EU27 × Post | -0.66 |
| Export | China × Post | +17.50 |
| Export | India × Post | +15.35 |
| Export | Türkiye × Post | +2.96 |
| Export | Kazakhstan × Post | +0.53 |
| Export | EU27 × Post | -0.88 |

These are descriptive fixed-effects robustness estimates, not causal treatment effects.

## Bank of Russia denominator sensitivity

Source: `results/tables/T19_Bank_of_Russia_Denominator_Sensitivity_PrePost.csv`

- Pre 2019–2021: **22.90%**
- Post 2023–2024: **37.03%**
- Change: **+14.13 pp**

## PPML-HDFE

Sources:

- `results/tables/T21_Revised_PPML_HDFE_Import.csv`
- `results/tables/T22_Revised_PPML_HDFE_Export.csv`

Import did not converge within 1,000 demeaning iterations. Export estimates are auxiliary conditional relative changes versus EU27.
