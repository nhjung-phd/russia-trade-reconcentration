# Reproducibility Guide

## Google Colab
1. Upload `data/Russia_BACI_Lite_Dataset.zip` to the Colab runtime or place it in the location expected by the notebook.
2. Open `notebooks/Russia_Trade_Full_AllInOne_NoDID_English.ipynb`.
3. Install the packages in `requirements.txt` if they are not already available.
4. Run all cells from top to bottom.
5. The notebook creates structural-result tables, sensitivity analyses, panel estimates, figures, publication tables, and an integrated output archive.

## Interpretation boundary
The pre/post, FE/RE, HS6 year-profile, and PPML-HDFE analyses characterize structural and longitudinal changes. They are not used to identify the pure causal effect of sanctions because multiple shocks occurred concurrently and Russia is the focal treated economy.
