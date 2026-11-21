# Manuscript Table Map

This file maps the manuscript tables to the machine-readable result files in `results/all_tables/`.

| Manuscript table | Topic | Primary machine-readable source(s) |
|---|---|---|
| Table 4 | Pre/post major partner shares | `T1_prepost_summary.csv`, `T1_import_partner_shares.csv`, `T1_export_partner_shares.csv` |
| Table 5 | Partner concentration | `T2_concentration_summary.csv`, `T2_import_concentration_by_year.csv`, `T2_export_concentration_by_year.csv` |
| Table 6 | China-dependent HS6 counts | `T4_HS6_dependence_prepost.csv`, `R4_dependence_prepost_balanced.csv`, `R4_dependence_counts_balanced.csv` |
| Table 7 | HS6 distributional tests | `HS6_statistical_tests.csv`, `R6_hs4_cluster_bootstrap.csv` |
| Table 8 | EU27 decline / China increase co-movement | `China_EU_change_correlation.csv`, `R7_eu_to_china_absorption.csv` |
| Table 9 | Non-energy and energy decomposition | `T5_nonenergy_prepost.csv`, `R8_export_energy_decomposition.csv`, `T6_crude_oil_value_quantity.csv` |
| Table 10 | Bilateral trade-exposure gap | `T7_exposure_gap_prepost.csv`, `R3_bop_exposure_gap_sensitivity.csv`, `R3_bop_exposure_gap_prepost.csv` |
| Table 11 | Coverage and sensitivity | `R1_coverage_by_year.csv`, `R2_balanced_partner_robustness.csv`, `R3_bop_denominator_bound.csv`, `R5_sign_decomposition.csv` |
| Table 12 | FE/RE and Hausman | `Table_FE_Core.csv`, `Table_RE_Core.csv`, `Table_Hausman.csv`, `P1_FE_RE_all_coefficients.csv` |
| Table 13 | PPML-HDFE | `Table_PPML_HDFE.csv`, `P4_PPML_HDFE_all.csv` |

The repository also retains intermediate and diagnostic CSV files so that the published tables can be traced back to the analysis outputs.
