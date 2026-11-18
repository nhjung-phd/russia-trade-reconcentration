# Reproducibility checklist

- [x] Master analysis notebook included.
- [x] Derived tables included.
- [x] Derived figures included.
- [x] Final and robustness Excel workbooks included.
- [x] Analysis metadata included.
- [x] Raw BACI data excluded.
- [x] Input-data acquisition instructions included.
- [x] Python package requirements included.
- [x] Bank of Russia denominator vintage pinned in the notebook/manuscript.
- [x] Reporting-coverage robustness outputs included.
- [x] HS4-cluster bootstrap outputs included.
- [x] BoP-denominator exposure-gap sensitivity included; interpretation limited to absolute percentage-point gap across denominator definitions.
- [x] Final consistency-audit table included.
- [x] Submission-ready manuscript included.
- [x] Publisher/source verification record included for Kolaja (2026), Głodowska et al. (2026), Gutmann et al. (2024), and the Bank of Russia BoP source.

## Before creating a public GitHub release

1. Run the notebook from top to bottom in a clean Colab runtime using the intended BACI input.
2. Confirm that `FINAL_CONSISTENCY_AUDIT.csv` reports the expected results.
3. Confirm the generated BoP denominator and exposure-gap CSV files match the manuscript tables.
4. Do not upload raw BACI archives.
5. Add the final journal citation/DOI after acceptance/publication.

- [x] `pyarrow` included for parquet I/O outside Colab.
- [x] README and VERSION synchronized to v1.4-reproducibility.
- [x] Master notebook automatically builds the Lite dataset from the official BACI archive when the Lite ZIP is absent.
