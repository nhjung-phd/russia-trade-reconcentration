# Data input instructions

Raw CEPII BACI data are intentionally excluded from this repository.

Use either:

1. `Russia_BACI_Lite_Dataset.zip` generated from the official BACI archive by the master notebook workflow; or
2. the official `BACI_HS12_V202601.zip` archive from CEPII.

For Google Colab, upload the ZIP to the runtime or place it in a Google Drive location searched by the notebook. The master notebook will detect the input and create its working directory under `/content/russia_trade_master`.

Do not commit raw BACI archives to the public repository unless redistribution is explicitly permitted by the data provider's terms.

## Automatic extraction behavior

If `Russia_BACI_Lite_Dataset.zip` is absent but the official `BACI_HS12_V202601.zip` archive is present, the master notebook automatically extracts Russia import/export HS6-year records and China world-trade totals, builds the lightweight parquet dataset, and then continues to the full analysis. A separate extractor notebook is therefore not required. Reading the generated parquet files requires `pyarrow`, which is included in `requirements.txt`.
