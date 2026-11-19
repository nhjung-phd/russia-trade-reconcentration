# Reproducibility checklist

- [x] Final manuscript included.
- [x] Structural master notebook included.
- [x] Panel robustness notebook included.
- [x] Full integrated notebook included.
- [x] Actual executed structural results included.
- [x] Actual executed FE/RE and Hausman results included.
- [x] Actual executed HS6 event-profile results included.
- [x] Actual executed PPML-HDFE results included.
- [x] Publication-ready CSV/Excel tables included.
- [x] Publication-ready PNG figures included.
- [x] Manuscript embedded images extracted for visual audit.
- [x] Raw BACI archive excluded.
- [x] Requirements file includes `pyarrow`, `linearmodels`, and `pyfixest`.
- [x] Interpretation explicitly limits panel models to robustness analysis rather than causal identification.
- [x] Checksums generated for repository files.

## Clean reproduction

1. Obtain the official CEPII BACI input or the project Lite dataset.
2. Create a fresh Python/Colab runtime.
3. Install `requirements.txt`.
4. Open `notebooks/Russia_Trade_Full_AllInOne.ipynb`.
5. Upload/mount the data ZIP.
6. Run all cells from top to bottom.
7. Compare generated outputs with `results/`, especially:
   - `results/publication/tables/`
   - `results/publication/figures/`
   - `results/Russia_Trade_Master_Final_Results.xlsx`
   - `results/Russia_Trade_Master_Robustness_Results.xlsx`
   - `results/Russia_Trade_Panel_Robustness_Results.xlsx`
