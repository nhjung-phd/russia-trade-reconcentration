# Replication Instructions

## Recommended: one-notebook workflow

Use:

`code/Russia_Trade_Master_AllInOne_Colab.ipynb`

### Option A — reproduce from raw BACI

1. Download `BACI_HS12_V202601.zip` from CEPII.
2. Upload it to `/content/BACI/` or `/content/drive/MyDrive/BACI/`.
3. Open the master notebook in Google Colab.
4. Run all cells.
5. The notebook creates the Russia-specific Lite dataset automatically and then runs every analysis.
6. Download `Russia_Trade_Master_Final_Outputs.zip`.

### Option B — reproduce from derived Lite data

If `Russia_BACI_Lite_Dataset.zip` is available, place it in `/content`, `/content/BACI`, or `/content/drive/MyDrive/BACI`.
The master notebook detects it automatically and skips the 1.2GB raw-data extraction step.

## Modular workflow

For debugging or methodological inspection:

1. `code/01_BACI_Russia_Extractor_Colab.ipynb`
2. `code/02_Russia_HS6_Statistical_Analysis_Colab.ipynb`

The first notebook creates the Lite dataset. The second notebook runs HS6-level statistical analysis without re-reading the original BACI archive.

## Expected outputs

- CSV result tables
- 300-dpi PNG figures
- Excel workbook
- JSON metadata
- consistency audit
