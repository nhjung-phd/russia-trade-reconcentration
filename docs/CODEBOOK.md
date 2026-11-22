# Codebook

## Core identifiers

- `year`: calendar year, 2015–2024.
- `partner`: numeric BACI/Comtrade partner or customs-area code.
- `hs6`: six-digit HS2012 merchandise category.
- `hs4`: first four digits of `hs6`; used as the cluster level for bootstrap/standard-error procedures.
- `hs2`: first two digits of `hs6`.
- `value_kUSD`: bilateral trade value in thousand USD.

## Focal partners

- China: 156
- India: 699
- Türkiye: 792
- Kazakhstan: 398

## EU27

The current EU27 composition is applied consistently over 2015–2024. France is code 251 in the analysis input. The United Kingdom is excluded. Italy is runtime-resolved from 380/381 depending on the source file.

## Study windows

- Full period: 2015–2024
- Main pre-period: 2019–2021
- Adjustment year: 2022
- Main post-period: 2023–2024

## Main outcomes

- partner share;
- HHI;
- CR1 / CR3;
- Shannon entropy;
- effective number of partners (`1/HHI` at the annual level);
- HS6-level change in focal-partner share;
- balanced-partner shifts;
- Bank of Russia denominator sensitivity;
- partner–year FE robustness estimates;
- HS6 longitudinal profiles;
- auxiliary export PPML-HDFE estimates.

## Important interpretation rule

FE and PPML specifications are robustness/longitudinal diagnostics. They do not identify the pure causal effect of sanctions or the war.
