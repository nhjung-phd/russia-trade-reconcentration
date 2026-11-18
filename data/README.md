# Data

## Raw source data

This project uses **CEPII BACI, HS2012, Version 202601**, covering 2015–2024.

The original BACI archive is **not included** in this repository.
Download the source data directly from the CEPII BACI download page and use:

`BACI_HS12_V202601.zip`

Place the raw archive in one of these Colab locations:

- `/content/BACI/BACI_HS12_V202601.zip`
- `/content/drive/MyDrive/BACI/BACI_HS12_V202601.zip`

CEPII BACI download page:
https://www.cepii.fr/DATA_DOWNLOAD/baci/doc/baci_webpage.html#download-links

## Derived data

`derived/` contains Russia-specific analytical extracts generated from the source BACI archive:

- `russia_import_partner_hs6_year.parquet`
- `russia_export_partner_hs6_year.parquet`
- `russia_import_hs6_year_summary.parquet`
- `russia_export_hs6_year_summary.parquet`
- `china_world_trade_year.parquet`
- `metadata.json`

These files are provided for computational reproducibility. Before making the repository public, the authors should confirm that redistribution of derived BACI data is consistent with the applicable CEPII/UN Comtrade terms. If there is any doubt, remove `data/derived/` and rely on the extractor notebook to recreate these files locally from the official BACI source.
