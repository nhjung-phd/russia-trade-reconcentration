# Release notes — v1.3-reproducibility

Final pre-submission consistency release.

## Manuscript

- Aligned the bilateral trade exposure-gap definition with RQ3: the primary measure is the absolute percentage-point difference; ratio and log-ratio are supplementary diagnostics.
- Replaced the conceptual-sequence label `exposure asymmetry` with `absolute exposure gap` where it described the RQ3 analytical stage.
- Preserved the revised BoP interpretation: BACI supports widening in difference, ratio, and log-ratio, while the BoP sensitivity clearly supports only the widening of the absolute percentage-point gap.

## Reference verification

- Reverified Kolaja (2026) against Taylor & Francis.
- Reverified Głodowska et al. (2026) as *The World Economy* 49(8), 1692–1709.
- Reverified Gutmann et al. (2024) as a 187-country, 2002–2019 panel study.
- Reverified that the Bank of Russia URL resolves to *Russia’s Balance of Payments in 2019–2025 (Analytical Presentation)* and that Table 2 contains the pinned import values.
- Added `docs/REFERENCE_VERIFICATION.md`.

## Repository

- Version synchronized to v1.3-reproducibility.
- Existing `pyarrow` dependency and automatic BACI-to-Lite extraction workflow retained.
- Raw BACI data remain excluded.
