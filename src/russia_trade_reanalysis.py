#!/usr/bin/env python3
"""
Russia Trade Corrected Reanalysis v2.1
======================================

This version is organized for human readability.

The source is divided into:
    Block 1  - Configuration
    Block 2  - Data loading
    Block 3  - Country-code audit
    Block 4  - Concentration metrics
    Block 5  - Major partner shares
    Block 6  - HS6 product-level analysis
    Block 7  - EU27-China co-movement and non-energy analysis
    Block 8  - Balanced-partner sensitivity
    Block 9  - Bank of Russia denominator sensitivity
    Block 10 - Auxiliary revised PPML-HDFE
    Block 11 - Figure generation
    Block 12 - Result export

All comments and log messages are written in English.
Figures are saved without internal top titles; filenames describe the content.
"""

from __future__ import annotations

from pathlib import Path
import json
import os
import shutil
import zipfile

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt

# ============================================================
# 1. Project folders
# ============================================================
# All generated files are written under one root folder.
# In Google Colab, the default location is /content/russia_trade_corrected.

ROOT = Path(os.environ.get("RUSSIA_TRADE_ROOT", "/content/russia_trade_corrected"))

DATA_DIR = ROOT / "data"
OUTPUT_DIR = ROOT / "outputs"
TABLE_DIR = OUTPUT_DIR / "tables"
FIGURE_DIR = OUTPUT_DIR / "figures"
LOG_DIR = OUTPUT_DIR / "logs"
WORKBOOK_DIR = OUTPUT_DIR / "workbooks"

for folder in [
    DATA_DIR,
    OUTPUT_DIR,
    TABLE_DIR,
    FIGURE_DIR,
    LOG_DIR,
    WORKBOOK_DIR,
]:
    folder.mkdir(parents=True, exist_ok=True)

# Keep aliases used by the analysis functions.
OUT = OUTPUT_DIR
TAB = TABLE_DIR
FIG = FIGURE_DIR
LOG = LOG_DIR
WB = WORKBOOK_DIR


# ============================================================
# 2. Study period
# ============================================================

YEARS = list(range(2015, 2025))       # Full study period: 2015-2024
PRE = [2019, 2020, 2021]             # Main pre-period
POST = [2023, 2024]                  # Main post-period
ADJUSTMENT_YEAR = 2022               # Transition year, excluded from main pre/post comparison


# ============================================================
# 3. Key country codes
# ============================================================

CHN = 156   # China
IND = 699   # India
TUR = 792   # Türkiye
KAZ = 398   # Kazakhstan


# ============================================================
# 4. EU27 member codes
# ============================================================
# The analysis uses the current EU27 composition consistently
# throughout 2015-2024.
#
# France:
#   BACI/Comtrade customs-area code = 251
#
# Italy:
#   Some source/reference files use 380 and others use 381.
#   Therefore Italy is not hard-coded in EU27_BASE.
#   The code actually present in the input data is detected at runtime.
#
# United Kingdom:
#   Code 826 is intentionally excluded from the current EU27 definition.

EU27_BASE = [
    40,   # Austria
    56,   # Belgium
    100,  # Bulgaria
    191,  # Croatia
    196,  # Cyprus
    203,  # Czech Republic
    208,  # Denmark
    233,  # Estonia
    246,  # Finland
    251,  # France
    276,  # Germany
    300,  # Greece
    348,  # Hungary
    372,  # Ireland
    428,  # Latvia
    440,  # Lithuania
    442,  # Luxembourg
    470,  # Malta
    528,  # Netherlands
    616,  # Poland
    620,  # Portugal
    642,  # Romania
    703,  # Slovakia
    705,  # Slovenia
    724,  # Spain
    752,  # Sweden
]

ITALY_CANDIDATES = [380, 381]

COUNTRY_NAMES = {
    40: "Austria",
    56: "Belgium",
    100: "Bulgaria",
    191: "Croatia",
    196: "Cyprus",
    203: "Czech Republic",
    208: "Denmark",
    233: "Estonia",
    246: "Finland",
    251: "France",
    276: "Germany",
    300: "Greece",
    348: "Hungary",
    372: "Ireland",
    380: "Italy",
    381: "Italy",
    428: "Latvia",
    440: "Lithuania",
    442: "Luxembourg",
    470: "Malta",
    528: "Netherlands",
    616: "Poland",
    620: "Portugal",
    642: "Romania",
    703: "Slovakia",
    705: "Slovenia",
    724: "Spain",
    752: "Sweden",
    156: "China",
    699: "India",
    792: "Türkiye",
    398: "Kazakhstan",
}


# ============================================================
# 5. Bank of Russia goods-import totals
# ============================================================
# Unit: billion USD
# These values are used only for denominator-sensitivity analysis.

BOP_IMPORTS_BN_USD = {
    2019: 253.877,
    2020: 240.089,
    2021: 301.047,
    2023: 303.086,
    2024: 301.548,
}

print("Configuration loaded.")
print(f"Study period: {YEARS[0]}-{YEARS[-1]}")
print(f"Pre-period: {PRE}")
print(f"Adjustment year: {ADJUSTMENT_YEAR}")
print(f"Post-period: {POST}")



# ============================================================================
# BLOCK 2. DATA LOADING HELPERS
# ============================================================================

def find_lite_zip() -> Path:
    candidates = [
        Path("/content/Russia_BACI_Lite_Dataset.zip"),
        Path("/content/drive/MyDrive/Russia_BACI_Lite_Dataset.zip"),
        Path.cwd() / "Russia_BACI_Lite_Dataset.zip",
        ROOT / "Russia_BACI_Lite_Dataset.zip",
    ]
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(
        "Russia_BACI_Lite_Dataset.zip was not found. Upload it to Colab or set RUSSIA_TRADE_ROOT."
    )


def load_lite_data(lite_zip: Path):
    extract_dir = DATA_DIR / "lite"
    if extract_dir.exists():
        shutil.rmtree(extract_dir)
    extract_dir.mkdir(parents=True)
    with zipfile.ZipFile(lite_zip) as z:
        z.extractall(extract_dir)

    imp_detail = pd.read_parquet(extract_dir / "russia_import_partner_hs6_year.parquet")
    exp_detail = pd.read_parquet(extract_dir / "russia_export_partner_hs6_year.parquet")
    china_world = pd.read_parquet(extract_dir / "china_world_trade_year.parquet")

    for df in [imp_detail, exp_detail]:
        df["year"] = pd.to_numeric(df["year"], errors="raise").astype(int)
        df["partner"] = pd.to_numeric(df["partner"], errors="raise").astype(int)
        df["hs6"] = df["hs6"].astype("string").str.zfill(6)
        df["hs2"] = df["hs6"].str[:2]
        df["hs4"] = df["hs6"].str[:4]
        df["value_kUSD"] = pd.to_numeric(df["value_kUSD"], errors="coerce").fillna(0.0)

    return imp_detail, exp_detail, china_world


# ============================================================================
# BLOCK 3. COUNTRY-CODE AUDIT AND EU27 CONSTRUCTION
# ============================================================================

def resolve_eu27(imp_detail: pd.DataFrame, exp_detail: pd.DataFrame):
    observed = set(imp_detail["partner"].unique()).union(set(exp_detail["partner"].unique()))

    if 251 not in observed:
        raise ValueError(
            "France code 251 is not present in the input data. Check the BACI country-code reference before proceeding."
        )

    italy_present = [c for c in ITALY_CANDIDATES if c in observed]
    if len(italy_present) != 1:
        raise ValueError(
            f"Italy code could not be resolved unambiguously. Observed candidates: {italy_present}. "
            "Inspect the country-code reference distributed with the BACI vintage."
        )
    italy_code = italy_present[0]
    eu27 = EU27_BASE + [italy_code]

    audit = pd.DataFrame({
        "item": ["France code", "Italy code resolved", "EU27 member count", "France 250 observed", "France 251 observed", "Italy 380 observed", "Italy 381 observed"],
        "value": [251, italy_code, len(eu27), int(250 in observed), int(251 in observed), int(380 in observed), int(381 in observed)],
    })
    audit.to_csv(TAB / "A0_country_code_audit.csv", index=False)
    eu_members = pd.DataFrame({
        "code": sorted(eu27),
        "country": [COUNTRY_NAMES.get(c, f"Code {c}") for c in sorted(eu27)],
        "role": "EU27 member",
    })
    eu_members.to_csv(TAB / "A1_EU27_country_codes_used.csv", index=False)
    return eu27, italy_code, audit


# ============================================================================
# BLOCK 4. CONCENTRATION METRICS
# ============================================================================

def partner_year_values(detail: pd.DataFrame) -> pd.DataFrame:
    return detail.groupby(["year", "partner"], as_index=False)["value_kUSD"].sum()


def concentration_metrics(values: pd.Series) -> dict:
    v = np.asarray(values, dtype=float)
    v = v[np.isfinite(v) & (v > 0)]
    if v.size == 0 or v.sum() <= 0:
        return {"HHI": np.nan, "CR1": np.nan, "CR3": np.nan, "Entropy": np.nan, "Effective_N": np.nan, "Observed_partners": 0}
    s = v / v.sum()
    s_sorted = np.sort(s)[::-1]
    hhi = float(np.sum(s ** 2))
    entropy = float(-np.sum(s * np.log(s)))
    return {
        "HHI": hhi,
        "CR1": float(s_sorted[:1].sum()),
        "CR3": float(s_sorted[:3].sum()),
        "Entropy": entropy,
        "Effective_N": 1.0 / hhi,
        "Observed_partners": int(v.size),
    }


def concentration_by_year(detail: pd.DataFrame, eu27: list[int], aggregate_eu: bool, side: str) -> pd.DataFrame:
    py = partner_year_values(detail)
    rows = []
    for year, g in py.groupby("year"):
        g = g.copy()
        if aggregate_eu:
            eu_value = g.loc[g.partner.isin(eu27), "value_kUSD"].sum()
            other = g.loc[~g.partner.isin(eu27), ["partner", "value_kUSD"]].copy()
            values = pd.concat([other["value_kUSD"], pd.Series([eu_value])], ignore_index=True)
            scope = "EU27_bloc"
        else:
            values = g["value_kUSD"]
            scope = "country"
        rec = concentration_metrics(values)
        rec.update({"side": side, "year": int(year), "scope": scope})
        rows.append(rec)
    return pd.DataFrame(rows)


def prepost_metric_summary(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (side, scope), g in df.groupby(["side", "scope"]):
        pre = g[g.year.isin(PRE)]
        post = g[g.year.isin(POST)]
        for metric in ["HHI", "CR1", "CR3", "Entropy", "Effective_N", "Observed_partners"]:
            a = float(pre[metric].mean())
            b = float(post[metric].mean())
            rows.append({
                "side": side,
                "scope": scope,
                "metric": metric,
                "pre_2019_2021": a,
                "post_2023_2024": b,
                "change": b - a,
                "rate_change_pct": ((b / a - 1) * 100) if a not in [0, np.nan] and np.isfinite(a) else np.nan,
            })
    return pd.DataFrame(rows)


# ============================================================================
# BLOCK 5. MAJOR PARTNER-GROUP SHARES
# ============================================================================

def major_partner_shares(detail: pd.DataFrame, eu27: list[int], side: str) -> pd.DataFrame:
    py = partner_year_values(detail)
    total = py.groupby("year")["value_kUSD"].sum()
    groups = {
        "China": [CHN],
        "India": [IND],
        "Türkiye": [TUR],
        "Kazakhstan": [KAZ],
        "EU27": eu27,
    }
    rows = []
    for year in sorted(py.year.unique()):
        den = float(total.loc[year])
        gy = py[py.year.eq(year)]
        for name, codes in groups.items():
            num = float(gy.loc[gy.partner.isin(codes), "value_kUSD"].sum())
            rows.append({"side": side, "year": int(year), "partner_group": name, "share": num / den if den else np.nan})
    return pd.DataFrame(rows)


def prepost_partner_summary(shares: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (side, group), g in shares.groupby(["side", "partner_group"]):
        pre = float(g[g.year.isin(PRE)].share.mean())
        post = float(g[g.year.isin(POST)].share.mean())
        rows.append({"side": side, "partner_group": group, "pre_pct": pre * 100, "post_pct": post * 100, "change_pp": (post - pre) * 100})
    return pd.DataFrame(rows)


# ============================================================================
# BLOCK 6. HS6 PRODUCT-LEVEL STATISTICS
# ============================================================================

def hs6_group_share(detail: pd.DataFrame, codes: list[int], label: str) -> pd.DataFrame:
    world = detail.groupby(["year", "hs6", "hs2", "hs4"], as_index=False)["value_kUSD"].sum().rename(columns={"value_kUSD": "world_value"})
    grp = detail[detail.partner.isin(codes)].groupby(["year", "hs6"], as_index=False)["value_kUSD"].sum().rename(columns={"value_kUSD": "group_value"})
    out = world.merge(grp, on=["year", "hs6"], how="left")
    out["group_value"] = out["group_value"].fillna(0.0)
    out[label] = np.where(out.world_value > 0, out.group_value / out.world_value, np.nan)
    return out[["year", "hs6", "hs2", "hs4", label]]


def hs6_prepost_changes(detail: pd.DataFrame, group_map: dict[str, list[int]], side: str) -> pd.DataFrame:
    base = None
    for label, codes in group_map.items():
        d = hs6_group_share(detail, codes, label)
        if base is None:
            base = d
        else:
            base = base.merge(d, on=["year", "hs6", "hs2", "hs4"], how="outer")
    rows = []
    for hs6, g in base.groupby("hs6"):
        meta = g.iloc[0]
        rec = {"side": side, "hs6": hs6, "hs2": meta.hs2, "hs4": meta.hs4}
        for label in group_map:
            pre = g[g.year.isin(PRE)][label].mean()
            post = g[g.year.isin(POST)][label].mean()
            rec[f"pre_{label}"] = pre
            rec[f"post_{label}"] = post
            rec[f"delta_{label}_pp"] = (post - pre) * 100 if pd.notna(pre) and pd.notna(post) else np.nan
        rows.append(rec)
    return pd.DataFrame(rows)


def cluster_bootstrap_mean(values: pd.Series, clusters: pd.Series, reps: int = 3000, seed: int = 42):
    d = pd.DataFrame({"v": values, "c": clusters}).dropna()
    cluster_ids = d.c.unique()
    rng = np.random.default_rng(seed)
    means = np.empty(reps)
    grouped = {c: d.loc[d.c.eq(c), "v"].to_numpy() for c in cluster_ids}
    for r in range(reps):
        sampled = rng.choice(cluster_ids, size=len(cluster_ids), replace=True)
        x = np.concatenate([grouped[c] for c in sampled])
        means[r] = np.mean(x)
    return float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))


def summarize_hs6_changes(changes: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    rows = []
    for side, g in changes.groupby("side"):
        for label in labels:
            col = f"delta_{label}_pp"
            x = g[col].dropna()
            if x.empty:
                continue
            nz = x[x.ne(0)]
            if len(nz) > 0:
                try:
                    w = stats.wilcoxon(nz, zero_method="wilcox", alternative="two-sided")
                    wp = float(w.pvalue)
                except Exception:
                    wp = np.nan
                ranks = stats.rankdata(np.abs(nz))
                rbc = float(np.sum(ranks[nz > 0]) - np.sum(ranks[nz < 0])) / float(np.sum(ranks))
            else:
                wp, rbc = np.nan, np.nan
            lo, hi = cluster_bootstrap_mean(g[col], g["hs4"], reps=3000, seed=42)
            rows.append({
                "side": side,
                "group": label,
                "N": int(x.size),
                "mean_change_pp": float(x.mean()),
                "median_change_pp": float(x.median()),
                "increase_pct": float((x > 0).mean() * 100),
                "zero_pct": float((x == 0).mean() * 100),
                "decrease_pct": float((x < 0).mean() * 100),
                "wilcoxon_p": wp,
                "hs4_cluster_ci_low": lo,
                "hs4_cluster_ci_high": hi,
                "rank_biserial": rbc,
            })
    return pd.DataFrame(rows)


# ============================================================================
# BLOCK 7. EU27-CHINA CO-MOVEMENT AND NON-ENERGY ANALYSIS
# ============================================================================

def eu_china_comovement(import_changes: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    d = import_changes[["hs6", "hs2", "hs4", "pre_EU27", "delta_EU27_pp", "delta_China_pp"]].dropna().copy()
    pearson = stats.pearsonr(d.delta_EU27_pp, d.delta_China_pp)
    spearman = stats.spearmanr(d.delta_EU27_pp, d.delta_China_pp)
    quadrant = float(((d.delta_EU27_pp < 0) & (d.delta_China_pp > 0)).mean() * 100)
    eu_dom = d[d.pre_EU27 > 0.5].copy()
    mean_eu = float(eu_dom.delta_EU27_pp.mean())
    mean_china = float(eu_dom.delta_China_pp.mean())
    absorption = mean_china / abs(mean_eu) * 100 if mean_eu != 0 else np.nan
    summary = pd.DataFrame([{
        "N": len(d),
        "pearson_r": float(pearson.statistic),
        "pearson_p": float(pearson.pvalue),
        "spearman_rho": float(spearman.statistic),
        "spearman_p": float(spearman.pvalue),
        "EU_down_China_up_pct": quadrant,
        "EU_dominant_N": len(eu_dom),
        "EU_dominant_mean_EU_change_pp": mean_eu,
        "EU_dominant_mean_China_change_pp": mean_china,
        "absorption_ratio_pct": absorption,
    }])
    return summary, eu_dom


def nonenergy_summary(changes: pd.DataFrame, labels: list[str]) -> pd.DataFrame:
    d = changes[changes.hs2.ne("27")]
    rows = []
    for side, g in d.groupby("side"):
        for label in labels:
            col = f"delta_{label}_pp"
            if col in g:
                rows.append({"side": side, "group": label, "nonenergy_mean_change_pp": float(g[col].mean())})
    return pd.DataFrame(rows)


# ============================================================================
# BLOCK 8. BALANCED-PARTNER ROBUSTNESS
# ============================================================================

def balanced_partner_ids(detail: pd.DataFrame, window=range(2019, 2025)) -> list[int]:
    d = partner_year_values(detail)
    required = set(window)
    pos = d[d.value_kUSD > 0].groupby("partner")["year"].apply(lambda s: set(map(int, s.tolist())))
    return [int(p) for p, ys in pos.items() if required.issubset(ys)]


def balanced_panel(detail: pd.DataFrame) -> tuple[pd.DataFrame, list[int]]:
    ids = balanced_partner_ids(detail)
    d = partner_year_values(detail)
    grid = pd.MultiIndex.from_product([ids, YEARS], names=["partner", "year"]).to_frame(index=False)
    p = grid.merge(d, on=["partner", "year"], how="left")
    p["value_kUSD"] = p.value_kUSD.fillna(0.0)
    den = p.groupby("year").value_kUSD.transform("sum")
    p["share"] = np.where(den > 0, p.value_kUSD / den, np.nan)
    return p, ids


def partner_prepost_shift_with_placebo(panel: pd.DataFrame, partner_code: int, label: str) -> dict:
    d = panel[panel.year.isin(PRE + POST)].copy()
    means = d.groupby(["partner", d.year.isin(POST).rename("post")])["share"].mean().unstack()
    means.columns = ["pre" if c is False else "post" for c in means.columns]
    means["shift_pp"] = (means["post"] - means["pre"]) * 100
    observed = float(means.loc[partner_code, "shift_pp"]) if partner_code in means.index else np.nan
    placebo = means.loc[means.index != partner_code, "shift_pp"].dropna().to_numpy()
    if np.isfinite(observed) and placebo.size:
        # Two-sided rank-style placebo probability, descriptive rather than causal.
        p_rank = (1 + np.sum(np.abs(placebo) >= abs(observed))) / (1 + placebo.size)
        pct_rank = stats.percentileofscore(placebo, observed, kind="mean")
    else:
        p_rank, pct_rank = np.nan, np.nan
    return {
        "partner": label,
        "partner_code": partner_code,
        "pre_mean_share_pct": float(means.loc[partner_code, "pre"] * 100) if partner_code in means.index else np.nan,
        "post_mean_share_pct": float(means.loc[partner_code, "post"] * 100) if partner_code in means.index else np.nan,
        "shift_pp": observed,
        "placebo_rank_p_two_sided": float(p_rank),
        "placebo_percentile": float(pct_rank),
        "note": "Descriptive placebo-rank comparison across balanced partners; not a causal p-value.",
    }


# ============================================================================
# BLOCK 9. BANK OF RUSSIA DENOMINATOR SENSITIVITY
# ============================================================================

def bop_sensitivity(imp_detail: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    china = imp_detail[imp_detail.partner.eq(CHN)].groupby("year").value_kUSD.sum() / 1e6
    baci = imp_detail.groupby("year").value_kUSD.sum() / 1e6
    rows = []
    for y, bop in BOP_IMPORTS_BN_USD.items():
        rows.append({
            "year": y,
            "China_import_bnUSD": float(china.get(y, np.nan)),
            "BACI_import_bnUSD": float(baci.get(y, np.nan)),
            "BoP_import_bnUSD": bop,
            "China_share_BoP_pct": float(china.get(y, np.nan) / bop * 100),
            "BACI_to_BoP_coverage_pct": float(baci.get(y, np.nan) / bop * 100),
        })
    annual = pd.DataFrame(rows)
    pre = annual[annual.year.isin(PRE)].China_share_BoP_pct.mean()
    post = annual[annual.year.isin(POST)].China_share_BoP_pct.mean()
    summary = pd.DataFrame([{
        "pre_window": "2019-2021",
        "post_window": "2023-2024",
        "pre_China_share_BoP_pct": pre,
        "post_China_share_BoP_pct": post,
        "change_pp": post - pre,
    }])
    return annual, summary


# ============================================================================
# BLOCK 10. AUXILIARY REVISED PPML-HDFE
# ============================================================================

def build_ppml_panel(detail: pd.DataFrame, eu27: list[int]) -> pd.DataFrame:
    def classify(p):
        if p == CHN:
            return "China"
        if p == IND:
            return "India"
        if p == TUR:
            return "Türkiye"
        if p == KAZ:
            return "Kazakhstan"
        if p in eu27:
            return "EU27"
        return None

    d = detail.copy()
    d["bloc"] = d.partner.map(classify)
    d = d[d.bloc.notna()].copy()
    d = d.groupby(["year", "hs6", "hs4", "bloc"], as_index=False).value_kUSD.sum()

    # Explicitly complete zero trade cells for the five focal blocs.
    hs = d[["hs6", "hs4"]].drop_duplicates()
    grid = pd.MultiIndex.from_product(
        [hs.hs6.unique(), YEARS, ["EU27", "China", "India", "Türkiye", "Kazakhstan"]],
        names=["hs6", "year", "bloc"],
    ).to_frame(index=False)
    grid = grid.merge(hs, on="hs6", how="left")
    d = grid.merge(d, on=["year", "hs6", "hs4", "bloc"], how="left")
    d["value_kUSD"] = d.value_kUSD.fillna(0.0)
    d["post"] = d.year.isin(POST).astype(int)
    d = d[d.year.isin(PRE + POST)].copy()
    return d


def fit_revised_ppml(detail: pd.DataFrame, eu27: list[int], side: str) -> pd.DataFrame:
    try:
        import pyfixest as pf
    except Exception as exc:
        return pd.DataFrame([{"side": side, "status": f"pyfixest unavailable: {exc}"}])

    d = build_ppml_panel(detail, eu27)
    # HS6×year FE absorb product-specific annual shocks; HS6×bloc FE absorb
    # time-invariant product-bloc heterogeneity. EU27 is the reference bloc.
    formula = "value_kUSD ~ i(bloc, post, ref='EU27') | hs6:bloc + hs6:year"
    try:
        fit = pf.fepois(formula, data=d, vcov={"CRV1": "hs4"})
        tidy = fit.tidy().reset_index().rename(columns={"Coefficient": "term"})
        tidy.insert(0, "side", side)
        tidy["interpretation"] = "Conditional relative post-period change versus EU27 after HS6×bloc and HS6×year fixed effects; not an absolute growth rate or causal treatment effect."
        return tidy
    except Exception as exc:
        return pd.DataFrame([{"side": side, "status": f"PPML estimation failed: {exc}"}])


# ============================================================================
# BLOCK 11. FIGURE HELPERS: CORE FIGURES
# ============================================================================

def _save_figure(fig, filename: str):
    """Save a publication-ready figure without an internal top title."""
    fig.tight_layout()
    fig.savefig(FIG / filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_core_figures(conc: pd.DataFrame, shares: pd.DataFrame):
    """Create all core concentration and partner-share figures without chart titles."""
    # Major partner-group shares, one file per flow.
    for side in ["import", "export"]:
        fig, ax = plt.subplots(figsize=(8, 5))
        d = shares[shares.side.eq(side)]
        for group, g in d.groupby("partner_group"):
            ax.plot(g.year, g.share * 100, marker="o", label=group)
        ax.axvline(2022, linestyle="--", linewidth=1)
        ax.set_xlabel("Year")
        ax.set_ylabel("Share (%)")
        ax.legend()
        _save_figure(fig, f"Figure_{'01' if side == 'import' else '02'}_{side.capitalize()}_Major_Partner_Group_Shares_2015_2024.png")

    # HHI and effective N by flow, country vs EU27-bloc definition.
    spec = [
        ("import", "HHI", "Figure_03_Import_HHI_Country_vs_EU27_Bloc_2015_2024.png", "HHI"),
        ("export", "HHI", "Figure_04_Export_HHI_Country_vs_EU27_Bloc_2015_2024.png", "HHI"),
        ("import", "Effective_N", "Figure_05_Import_Effective_N_Country_vs_EU27_Bloc_2015_2024.png", "Effective number of partners"),
        ("export", "Effective_N", "Figure_06_Export_Effective_N_Country_vs_EU27_Bloc_2015_2024.png", "Effective number of partners"),
    ]
    for side, metric, fn, ylabel in spec:
        fig, ax = plt.subplots(figsize=(8, 5))
        d = conc[conc.side.eq(side)]
        for scope, g in d.groupby("scope"):
            label = "Country level" if scope == "country" else "EU27 aggregated as one bloc"
            ax.plot(g.year, g[metric], marker="o", label=label)
        ax.axvline(2022, linestyle="--", linewidth=1)
        ax.set_xlabel("Year")
        ax.set_ylabel(ylabel)
        ax.legend()
        _save_figure(fig, fn)

    # Observed partner counts.
    fig, ax = plt.subplots(figsize=(8, 5))
    d = conc[conc.scope.eq("country")]
    for side, g in d.groupby("side"):
        ax.plot(g.year, g.Observed_partners, marker="o", label=side.capitalize())
    ax.axvline(2022, linestyle="--", linewidth=1)
    ax.set_xlabel("Year")
    ax.set_ylabel("Observed trading partners")
    ax.legend()
    _save_figure(fig, "Figure_07_Observed_Trade_Partner_Counts_2015_2024.png")


# ============================================================================
# BLOCK 12. FIGURE HELPERS: HS6 FIGURES
# ============================================================================

def china_dependency_counts(import_changes: pd.DataFrame) -> pd.DataFrame:
    """Count HS6 categories above key China-share thresholds in pre and post periods."""
    rows = []
    # Use the pre/post China shares already calculated for each HS6 category.
    for threshold in [0.50, 0.70, 0.90]:
        pre_n = int((import_changes["pre_China"] >= threshold).sum())
        post_n = int((import_changes["post_China"] >= threshold).sum())
        rows.append({
            "China_share_threshold": threshold,
            "pre_HS6_count": pre_n,
            "post_HS6_count": post_n,
            "change_count": post_n - pre_n,
            "rate_change_pct": ((post_n / pre_n - 1) * 100) if pre_n else np.nan,
        })
    return pd.DataFrame(rows)


def make_hs6_figures(imp_changes: pd.DataFrame, exp_changes: pd.DataFrame, comov_detail: pd.DataFrame, china_dep: pd.DataFrame):
    """Create product-level figures without internal chart titles."""
    # Distribution of China import-share changes.
    fig, ax = plt.subplots(figsize=(8, 5))
    x = imp_changes["delta_China_pp"].dropna()
    ax.hist(x, bins=50)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.set_xlabel("Post minus pre China import share (percentage points)")
    ax.set_ylabel("Number of HS6 categories")
    _save_figure(fig, "Figure_08_HS6_China_Import_Share_Change_Distribution.png")

    # High China-dependency counts.
    fig, ax = plt.subplots(figsize=(8, 5))
    xx = np.arange(len(china_dep))
    width = 0.36
    ax.bar(xx - width/2, china_dep.pre_HS6_count, width, label="Pre 2019-2021")
    ax.bar(xx + width/2, china_dep.post_HS6_count, width, label="Post 2023-2024")
    ax.set_xticks(xx, [f">={int(v*100)}%" for v in china_dep.China_share_threshold])
    ax.set_xlabel("China share threshold")
    ax.set_ylabel("Number of HS6 categories")
    ax.legend()
    _save_figure(fig, "Figure_09_HS6_China_Import_Dependency_Threshold_Counts.png")

    # EU27-to-China co-movement scatter.
    fig, ax = plt.subplots(figsize=(7, 6))
    d = comov_detail.dropna(subset=["delta_EU27_pp", "delta_China_pp"])
    ax.scatter(d.delta_EU27_pp, d.delta_China_pp, s=12, alpha=0.45)
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.axvline(0, linestyle="--", linewidth=1)
    ax.set_xlabel("Change in EU27 import share (percentage points)")
    ax.set_ylabel("Change in China import share (percentage points)")
    _save_figure(fig, "Figure_10_HS6_EU27_Decline_vs_China_Increase_Scatter.png")

    # Export sign decomposition for China, India, Türkiye, EU27.
    labels = ["China", "India", "Türkiye", "EU27"]
    rows = []
    for label in labels:
        col = f"delta_{label}_pp"
        x = exp_changes[col].dropna()
        rows.append({"group": label, "Increase": (x > 0).mean()*100, "No change": (x == 0).mean()*100, "Decrease": (x < 0).mean()*100})
    sign = pd.DataFrame(rows)
    sign.to_csv(TAB / "T17_Export_HS6_Sign_Decomposition.csv", index=False)
    fig, ax = plt.subplots(figsize=(8, 5))
    bottom = np.zeros(len(sign))
    for key in ["Increase", "No change", "Decrease"]:
        ax.bar(sign.group, sign[key], bottom=bottom, label=key)
        bottom += sign[key].to_numpy()
    ax.set_ylabel("Share of HS6 categories (%)")
    ax.legend()
    _save_figure(fig, "Figure_11_Export_HS6_Sign_Decomposition_by_Partner_Group.png")


# ============================================================================
# BLOCK 13. FIGURE HELPERS: BALANCED SAMPLE AND BOP
# ============================================================================

def make_balanced_figures(balanced_summaries: pd.DataFrame):
    """Create balanced-sample concentration comparison figures."""
    for side in ["import", "export"]:
        d = balanced_summaries[(balanced_summaries.side == side) & (balanced_summaries.metric.isin(["HHI", "Effective_N"]))]
        for metric, ylabel, num in [("HHI", "HHI", "12" if side == "import" else "13"), ("Effective_N", "Effective number of partners", "14" if side == "import" else "15")]:
            x = d[d.metric.eq(metric)].copy()
            if x.empty:
                continue
            fig, ax = plt.subplots(figsize=(7, 5))
            pos = np.arange(len(x))
            width = 0.36
            ax.bar(pos-width/2, x.pre_2019_2021, width, label="Pre 2019-2021")
            ax.bar(pos+width/2, x.post_2023_2024, width, label="Post 2023-2024")
            ax.set_xticks(pos, ["Country level" if v == "country" else "EU27 as one bloc" for v in x.scope])
            ax.set_ylabel(ylabel)
            ax.legend()
            _save_figure(fig, f"Figure_{num}_{side.capitalize()}_Balanced_{metric}_Country_vs_EU27_Bloc.png")


def make_bop_figure(bop_annual: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(bop_annual.year, bop_annual.China_share_BoP_pct, marker="o", label="China share using Bank of Russia denominator")
    ax.axvline(2022, linestyle="--", linewidth=1)
    ax.set_xlabel("Year")
    ax.set_ylabel("China import share (%)")
    ax.legend()
    _save_figure(fig, "Figure_16_China_Import_Share_Bank_of_Russia_Denominator.png")


# ============================================================================
# BLOCK 14. LONGITUDINAL PROFILES AND PRODUCT INSPECTION
# ============================================================================

def top_hs6_changes(changes: pd.DataFrame, label: str, n: int = 50) -> pd.DataFrame:
    col = f"delta_{label}_pp"
    cols = ["side", "hs6", "hs2", "hs4", f"pre_{label}", f"post_{label}", col]
    return changes[cols].dropna().sort_values(col, ascending=False).head(n)


def hs6_year_profile(detail: pd.DataFrame, codes: list[int], group_label: str, side: str) -> pd.DataFrame:
    """Estimate a descriptive balanced-HS6 year profile relative to 2021."""
    d = hs6_group_share(detail, codes, "share")
    pivot = d.pivot(index="hs6", columns="year", values="share")
    available_years = [y for y in YEARS if y in pivot.columns]
    balanced = pivot.dropna(subset=available_years).copy()
    rows = []
    for y in available_years:
        vals = balanced[y]
        ref = balanced[2021] if 2021 in balanced.columns else np.nan
        delta = (vals - ref) * 100 if 2021 in balanced.columns else np.nan
        rows.append({
            "side": side,
            "group": group_label,
            "year": y,
            "balanced_HS6_N": int(len(balanced)),
            "mean_share_pct": float(vals.mean() * 100),
            "mean_change_vs_2021_pp": float(delta.mean()) if hasattr(delta, "mean") else np.nan,
            "median_change_vs_2021_pp": float(delta.median()) if hasattr(delta, "median") else np.nan,
        })
    return pd.DataFrame(rows)


def make_year_profile_figures(profile_df: pd.DataFrame):
    """Save one longitudinal HS6 profile figure per flow and partner group."""
    counter = 17
    for (side, group), g in profile_df.groupby(["side", "group"]):
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(g.year, g.mean_change_vs_2021_pp, marker="o")
        ax.axhline(0, linestyle="--", linewidth=1)
        ax.axvline(2022, linestyle="--", linewidth=1)
        ax.set_xlabel("Year")
        ax.set_ylabel("Mean HS6 share change vs 2021 (percentage points)")
        safe_group = group.replace("ü", "u").replace(" ", "_")
        _save_figure(fig, f"Figure_{counter:02d}_{side.capitalize()}_{safe_group}_HS6_Year_Profile_vs_2021.png")
        counter += 1


# ============================================================================
# BLOCK 15. FIGURE HELPERS: PLACEBO AND PPML
# ============================================================================

def make_placebo_figure(placebo: pd.DataFrame):
    """Plot balanced-partner pre/post shifts for the focal partners."""
    fig, ax = plt.subplots(figsize=(8, 5))
    d = placebo.copy()
    labels = [f"{r.side.capitalize()}-{r.partner}" for _, r in d.iterrows()]
    ax.bar(labels, d.shift_pp)
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_ylabel("Pre/post shift (percentage points)")
    ax.tick_params(axis="x", rotation=45)
    _save_figure(fig, "Figure_27_Balanced_Partner_PrePost_Shifts_Focal_Partners.png")


def make_ppml_figure(ppml_imp: pd.DataFrame, ppml_exp: pd.DataFrame):
    """Plot auxiliary PPML coefficients when a tidy numeric result is available."""
    pieces = []
    for side, d in [("Import", ppml_imp), ("Export", ppml_exp)]:
        if d is None or d.empty or "Estimate" not in d.columns:
            continue
        x = d.copy()
        x["side"] = side
        pieces.append(x)
    if not pieces:
        return
    d = pd.concat(pieces, ignore_index=True)
    # Keep interaction terms only when available.
    if "term" in d.columns:
        d = d[d["term"].astype(str).str.contains("bloc", case=False, na=False)]
    if d.empty:
        return
    fig, ax = plt.subplots(figsize=(9, 5))
    labels = [f"{r.side}: {getattr(r, 'term', '')}" for _, r in d.iterrows()]
    ax.bar(labels, d["Estimate"])
    ax.axhline(0, linestyle="--", linewidth=1)
    ax.set_ylabel("PPML coefficient")
    ax.tick_params(axis="x", rotation=45)
    _save_figure(fig, "Figure_28_Auxiliary_Revised_PPML_HDFE_Coefficients.png")


# ============================================================================
# BLOCK 16. WORKBOOK AND OUTPUT MANIFEST
# ============================================================================

def create_workbook_and_manifest():
    """Combine all CSV tables into one Excel workbook and write a complete output manifest."""
    csv_files = sorted(TAB.glob("*.csv"))
    xlsx_path = WB / "Russia_Trade_Corrected_Reanalysis_All_Tables.xlsx"
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as writer:
        used = set()
        for i, f in enumerate(csv_files, start=1):
            name = f.stem[:31]
            base = name
            k = 1
            while name in used:
                suffix = f"_{k}"
                name = (base[:31-len(suffix)] + suffix)
                k += 1
            used.add(name)
            pd.read_csv(f).to_excel(writer, sheet_name=name, index=False)

    manifest_rows = []
    for folder in [TAB, FIG, WB, LOG]:
        for f in sorted(folder.glob("*")):
            if f.is_file():
                manifest_rows.append({
                    "category": folder.name,
                    "filename": f.name,
                    "relative_path": str(f.relative_to(OUT)),
                    "size_bytes": f.stat().st_size,
                })
    pd.DataFrame(manifest_rows).to_csv(OUT / "OUTPUT_MANIFEST.csv", index=False)
    return xlsx_path

# =============================================================================
# EXECUTION WORKFLOW
# =============================================================================

def run_full_analysis():
    """Run the complete corrected analysis in a transparent sequence."""

    # -------------------------------------------------------------------------
    # STEP 1. Load data
    # -------------------------------------------------------------------------
    print("\n[STEP 1] Loading input data...")
    lite_zip = find_lite_zip()
    imp_detail, exp_detail, china_world = load_lite_data(lite_zip)

    # -------------------------------------------------------------------------
    # STEP 2. Audit country codes and construct EU27
    # -------------------------------------------------------------------------
    print("\n[STEP 2] Auditing country codes and constructing EU27...")
    eu27, italy_code, code_audit = resolve_eu27(imp_detail, exp_detail)

    # -------------------------------------------------------------------------
    # STEP 3. Country-level and EU27-bloc concentration
    # -------------------------------------------------------------------------
    print("\n[STEP 3] Calculating concentration measures...")
    conc = pd.concat([
        concentration_by_year(imp_detail, eu27, False, "import"),
        concentration_by_year(imp_detail, eu27, True,  "import"),
        concentration_by_year(exp_detail, eu27, False, "export"),
        concentration_by_year(exp_detail, eu27, True,  "export"),
    ], ignore_index=True)

    conc.to_csv(
        TAB / "T01_Country_and_EU27_Bloc_Concentration_by_Year.csv",
        index=False,
    )

    conc_summary = prepost_metric_summary(conc)
    conc_summary.to_csv(
        TAB / "T02_Country_and_EU27_Bloc_Concentration_PrePost.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # STEP 4. Major partner-group shares
    # -------------------------------------------------------------------------
    print("\n[STEP 4] Calculating major partner-group shares...")
    shares = pd.concat([
        major_partner_shares(imp_detail, eu27, "import"),
        major_partner_shares(exp_detail, eu27, "export"),
    ], ignore_index=True)

    shares.to_csv(
        TAB / "T03_Major_Partner_Group_Shares_by_Year.csv",
        index=False,
    )

    partner_summary = prepost_partner_summary(shares)
    partner_summary.to_csv(
        TAB / "T04_Major_Partner_Group_Shares_PrePost.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # STEP 5. HS6 product-level analyses
    # -------------------------------------------------------------------------
    print("\n[STEP 5] Running HS6 product-level analyses...")
    group_map = {
        "China": [CHN],
        "EU27": eu27,
        "India": [IND],
        "Türkiye": [TUR],
    }

    imp_changes = hs6_prepost_changes(
        imp_detail,
        group_map,
        "import",
    )

    exp_changes = hs6_prepost_changes(
        exp_detail,
        group_map,
        "export",
    )

    all_changes = pd.concat(
        [imp_changes, exp_changes],
        ignore_index=True,
    )

    all_changes.to_csv(
        TAB / "T05_HS6_PrePost_Share_Changes_All_Groups.csv",
        index=False,
    )

    hs6_stats = summarize_hs6_changes(
        all_changes,
        list(group_map),
    )

    hs6_stats.to_csv(
        TAB / "T06_HS6_Distributional_Statistics.csv",
        index=False,
    )

    china_dep = china_dependency_counts(imp_changes)
    china_dep.to_csv(
        TAB / "T07_HS6_China_Import_Dependency_Threshold_Counts.csv",
        index=False,
    )

    comov, eu_dom = eu_china_comovement(imp_changes)
    comov.to_csv(
        TAB / "T08_EU27_China_HS6_CoMovement_Summary.csv",
        index=False,
    )
    eu_dom.to_csv(
        TAB / "T09_EU27_Dominant_HS6_Products_Detail.csv",
        index=False,
    )

    nonenergy = nonenergy_summary(
        all_changes,
        list(group_map),
    )
    nonenergy.to_csv(
        TAB / "T10_NonEnergy_HS6_Mean_Changes.csv",
        index=False,
    )

    for side_name, data in [
        ("Import", imp_changes),
        ("Export", exp_changes),
    ]:
        for group in ["China", "EU27", "India", "Türkiye"]:
            top_hs6_changes(
                data,
                group,
                n=100,
            ).to_csv(
                TAB / f"T11_{side_name}_Top100_HS6_{group}_Share_Increases.csv",
                index=False,
            )

    # -------------------------------------------------------------------------
    # STEP 6. Balanced-partner sensitivity
    # -------------------------------------------------------------------------
    print("\n[STEP 6] Running balanced-partner sensitivity analysis...")

    observed_counts = conc[
        conc["scope"].eq("country")
    ][["side", "year", "Observed_partners"]].copy()

    observed_counts.to_csv(
        TAB / "T12_Observed_Trade_Partner_Counts_by_Year.csv",
        index=False,
    )

    panel_rows = []
    balanced_summaries = []

    for side, detail in [
        ("import", imp_detail),
        ("export", exp_detail),
    ]:
        panel, balanced_ids = balanced_panel(detail)

        panel.to_csv(
            TAB / f"T13_{side.capitalize()}_Balanced_Partner_Panel.csv",
            index=False,
        )

        pd.DataFrame({
            "partner_code": balanced_ids,
            "partner_name": [
                COUNTRY_NAMES.get(code, f"Code {code}")
                for code in balanced_ids
            ],
        }).to_csv(
            TAB / f"T14_{side.capitalize()}_Balanced_Partner_IDs.csv",
            index=False,
        )

        for code, label in [
            (CHN, "China"),
            (IND, "India"),
            (TUR, "Türkiye"),
            (KAZ, "Kazakhstan"),
        ]:
            record = partner_prepost_shift_with_placebo(
                panel,
                code,
                label,
            )
            record["side"] = side
            panel_rows.append(record)

        balanced_detail = detail[
            detail["partner"].isin(balanced_ids)
        ]

        country_metrics = concentration_by_year(
            balanced_detail,
            eu27,
            False,
            side,
        )

        bloc_metrics = concentration_by_year(
            balanced_detail,
            eu27,
            True,
            side,
        )

        balanced_summaries.append(
            prepost_metric_summary(
                pd.concat(
                    [country_metrics, bloc_metrics],
                    ignore_index=True,
                )
            )
        )

    placebo = pd.DataFrame(panel_rows)
    placebo.to_csv(
        TAB / "T15_Balanced_Partner_Shifts_and_Placebo_Ranks.csv",
        index=False,
    )

    balanced_summary = pd.concat(
        balanced_summaries,
        ignore_index=True,
    )

    balanced_summary.to_csv(
        TAB / "T16_Balanced_Country_and_EU27_Bloc_Concentration_PrePost.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # STEP 7. Bank of Russia denominator sensitivity
    # -------------------------------------------------------------------------
    print("\n[STEP 7] Running Bank of Russia denominator sensitivity...")
    bop_annual, bop_summary = bop_sensitivity(imp_detail)

    bop_annual.to_csv(
        TAB / "T18_Bank_of_Russia_Denominator_Sensitivity_by_Year.csv",
        index=False,
    )

    bop_summary.to_csv(
        TAB / "T19_Bank_of_Russia_Denominator_Sensitivity_PrePost.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # STEP 8. Balanced-HS6 longitudinal profiles
    # -------------------------------------------------------------------------
    print("\n[STEP 8] Building balanced-HS6 longitudinal profiles...")
    profile_frames = []

    longitudinal_groups = {
        "China": [CHN],
        "EU27": eu27,
        "India": [IND],
        "Türkiye": [TUR],
        "Kazakhstan": [KAZ],
    }

    for side, detail in [
        ("import", imp_detail),
        ("export", exp_detail),
    ]:
        for label, codes in longitudinal_groups.items():
            profile_frames.append(
                hs6_year_profile(
                    detail,
                    codes,
                    label,
                    side,
                )
            )

    profiles = pd.concat(
        profile_frames,
        ignore_index=True,
    )

    profiles.to_csv(
        TAB / "T20_HS6_Balanced_Year_Profiles_All_Focal_Groups.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # STEP 9. Auxiliary revised PPML-HDFE
    # -------------------------------------------------------------------------
    print("\n[STEP 9] Running auxiliary revised PPML-HDFE...")
    ppml_imp = fit_revised_ppml(
        imp_detail,
        eu27,
        "import",
    )

    ppml_exp = fit_revised_ppml(
        exp_detail,
        eu27,
        "export",
    )

    ppml_imp.to_csv(
        TAB / "T21_Revised_PPML_HDFE_Import.csv",
        index=False,
    )

    ppml_exp.to_csv(
        TAB / "T22_Revised_PPML_HDFE_Export.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # STEP 10. Manuscript-facing key results
    # -------------------------------------------------------------------------
    print("\n[STEP 10] Building key-results summary...")
    key_rows = []

    for side in ["import", "export"]:
        for scope in ["country", "EU27_bloc"]:
            subset = conc_summary[
                (conc_summary["side"] == side)
                & (conc_summary["scope"] == scope)
            ]

            for metric in ["HHI", "Effective_N"]:
                row = subset[
                    subset["metric"] == metric
                ]

                if row.empty:
                    continue

                result = row.iloc[0]

                key_rows.append({
                    "section": "concentration",
                    "side": side,
                    "definition": scope,
                    "measure": metric,
                    "pre": result["pre_2019_2021"],
                    "post": result["post_2023_2024"],
                    "change": result["change"],
                })

    key_df = pd.DataFrame(key_rows)
    key_df.to_csv(
        TAB / "T23_Manuscript_Key_Results_Summary.csv",
        index=False,
    )

    # -------------------------------------------------------------------------
    # STEP 11. Generate every figure
    # -------------------------------------------------------------------------
    print("\n[STEP 11] Generating all figures...")
    make_core_figures(conc, shares)
    make_hs6_figures(
        imp_changes,
        exp_changes,
        imp_changes,
        china_dep,
    )
    make_balanced_figures(balanced_summary)
    make_bop_figure(bop_annual)
    make_year_profile_figures(profiles)
    make_placebo_figure(placebo)
    make_ppml_figure(ppml_imp, ppml_exp)

    # -------------------------------------------------------------------------
    # STEP 12. Export metadata, workbook, manifest, and final ZIP
    # -------------------------------------------------------------------------
    print("\n[STEP 12] Exporting final result package...")

    metadata = {
        "input": str(lite_zip),
        "years": YEARS,
        "pre": PRE,
        "post": POST,
        "adjustment_year": ADJUSTMENT_YEAR,
        "EU27_codes": eu27,
        "EU27_members": {
            str(code): COUNTRY_NAMES.get(code, f"Code {code}")
            for code in eu27
        },
        "France_code": 251,
        "Italy_code_resolved": italy_code,
        "design": "non-causal structural and longitudinal analysis",
        "primary_concentration_definitions": [
            "country-level",
            "EU27 aggregated as one geopolitical bloc",
        ],
        "panel_inference": (
            "descriptive balanced-panel shifts with placebo-rank comparison; "
            "conventional singleton-treatment p-values are not primary evidence"
        ),
        "PPML": (
            "auxiliary; HS6×bloc and HS6×year fixed effects; EU27 reference"
        ),
        "figure_titles_inside_images": False,
    }

    with open(
        LOG / "analysis_metadata_corrected.json",
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            metadata,
            file,
            indent=2,
            ensure_ascii=False,
        )

    run_summary = [
        "Russia trade corrected reanalysis completed.",
        "France code used: 251",
        f"Italy code resolved from input data: {italy_code}",
        f"EU27 member count: {len(eu27)}",
        f"Main pre-period: {PRE}",
        f"Adjustment year excluded: {ADJUSTMENT_YEAR}",
        f"Main post-period: {POST}",
        "All figures are saved without internal top titles.",
    ]

    (LOG / "RUN_SUMMARY.txt").write_text(
        "\n".join(run_summary),
        encoding="utf-8",
    )

    workbook = create_workbook_and_manifest()

    manifest_rows = []

    for folder in [TAB, FIG, WB, LOG]:
        for file in sorted(folder.glob("*")):
            if file.is_file():
                manifest_rows.append({
                    "category": folder.name,
                    "filename": file.name,
                    "relative_path": str(file.relative_to(OUT)),
                    "size_bytes": file.stat().st_size,
                })

    pd.DataFrame(
        manifest_rows
    ).to_csv(
        OUT / "OUTPUT_MANIFEST.csv",
        index=False,
    )

    zip_path = (
        ROOT
        / "Russia_Trade_Corrected_Reanalysis_Outputs_v2_1.zip"
    )

    if zip_path.exists():
        zip_path.unlink()

    shutil.make_archive(
        str(zip_path.with_suffix("")),
        "zip",
        OUT,
    )

    print("\nCompleted corrected reanalysis.")
    print("Tables:", TAB)
    print("Figures:", FIG)
    print("Workbook:", workbook)
    print("Output ZIP:", zip_path)

    return zip_path


if __name__ == "__main__":
    run_full_analysis()
