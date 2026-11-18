# Public Release Checklist

Before switching the GitHub repository from private to public:

- [ ] Confirm final manuscript title.
- [ ] Confirm final author list and author order.
- [ ] Replace placeholder repository URL in `CITATION.cff`.
- [ ] Add the accepted/published article DOI when available.
- [ ] Confirm whether `data/derived/` may be redistributed.
- [ ] If redistribution is uncertain, remove `data/derived/` before public release.
- [ ] Select a software license for the code.
- [ ] Confirm that no private paths, credentials, or personal files remain in notebooks.
- [ ] Re-run the master notebook once from a clean Colab runtime.
- [ ] Confirm that every table and figure in the manuscript maps to a file in `results/`.
