# Changelog

## GitHub package v1.1 — 2026-11-22

- Removed the manuscript DOCX and manuscript-only figure folder from the repository package.
- Added `data/Russia_BACI_Lite_Dataset.zip` (compact executable analysis dataset supplied by the author).
- Updated README, data documentation, reproducibility instructions, redistribution notice, and checksums for the data-included release.
- Analysis code and corrected result outputs remain unchanged from v1.0.


## GitHub package v1.0 — 2026-11-22

- Based on manuscript `v16.8 Final`.
- Corrected EU27 country-code handling; France included as BACI/Comtrade customs-area code 251 and UK excluded.
- Added EU27-bloc concentration sensitivity.
- Standardized main comparison to 2019–2021 vs 2023–2024, excluding 2022.
- Added/updated Bank of Russia denominator sensitivity to +14.13 pp.
- Replaced earlier FE/RE/Hausman layer with descriptive partner–year two-way FE robustness using the main pre/post windows.
- FE estimates updated to corrected results (e.g., Import China × Post +28.15 pp; Export China × Post +17.50 pp).
- Removed revised import PPML-HDFE from supporting evidence because it did not converge within 1,000 demeaning iterations.
- Retained export PPML-HDFE only as an auxiliary specification.
- Updated corrected HS6, EU27-China co-movement, balanced-sample, and longitudinal outputs.
- Added full output manifest, codebook, reproduction protocol, and machine-readable citation.
