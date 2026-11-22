# Data inputs

This release **includes** `Russia_BACI_Lite_Dataset.zip` as the compact executable input for the analysis notebook.

## Included ZIP contents

| File | Purpose |
|---|---|
| `russia_import_partner_hs6_year.parquet` | Russian imports by partner, HS6, and year |
| `russia_export_partner_hs6_year.parquet` | Russian exports by partner, HS6, and year |
| `russia_import_hs6_year_summary.parquet` | Import HS6-year summary |
| `russia_export_hs6_year_summary.parquet` | Export HS6-year summary |
| `china_world_trade_year.parquet` | China world-trade totals used in bilateral-exposure calculations |
| `metadata.json` | Source/version/year metadata |

For the partner-HS6-year files the notebook normalizes `year`, `partner`, `hs6`, and `value_kUSD`, and derives HS2/HS4 identifiers as needed.

## Provenance recorded in metadata

- Source: **CEPII BACI HS2012 V202601**
- Years: **2015–2024**

The ZIP is a compact author-prepared analysis input, not the complete CEPII BACI source distribution.

## Execution

In Google Colab, upload the ZIP to:

`/content/Russia_BACI_Lite_Dataset.zip`

For local execution, point the analysis root to the repository `data/` directory or copy the ZIP to the notebook's configured root.

## Redistribution

The file is included in this package at the author's request for reproducibility. The full BACI source dataset is not included. Before publicly redistributing this compact derivative dataset, review the source provider's applicable license and attribution requirements.
