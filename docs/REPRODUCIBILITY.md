# Reproducibility Guide

## Recommended path (using included derivative data)
1. Clone or download this repository.
2. Unzip `data/Russia_BACI_Lite_Dataset.zip`.
3. Open `notebooks/Russia_Trade_Full_AllInOne_NoDID.ipynb`.
4. Install packages from `requirements.txt`.
5. Point the notebook to the unzipped Lite dataset if automatic discovery does not locate it.
6. Run the notebook from top to bottom.
7. Compare generated outputs with the archived files under `results/`.

## Google Colab
Upload:
- `notebooks/Russia_Trade_Full_AllInOne_NoDID.ipynb`
- `data/Russia_BACI_Lite_Dataset.zip`

Then select **Runtime → Run all**.

## Included audit trail
- Clean source notebook: `notebooks/Russia_Trade_Full_AllInOne_NoDID.ipynb`
- Executed notebook: `notebooks/Russia_Trade_Full_AllInOne_NoDID_executed.ipynb`
- Actual generated tables, figures, model summaries, and Excel workbooks: `results/`

## Analysis scope
The final replication source intentionally contains **no Difference-in-Differences module**. It includes structural trade analysis, distributional tests, sensitivity analyses, FE/RE, Hausman diagnostics, HS6 product-fixed-effect year profiles, and PPML-HDFE.
