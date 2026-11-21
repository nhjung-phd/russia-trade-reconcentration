# Russia Trade Re-Concentration: All-in-One analysis script (No DiD)
# Generated from the clean replication notebook.
# All comments and user-facing messages are in English.


# ===== Notebook code cell 1 =====
%pip -q install pandas numpy scipy matplotlib statsmodels pyarrow openpyxl tqdm linearmodels pyfixest

from pathlib import Path
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
import zipfile, shutil, json, warnings
from tqdm.auto import tqdm
from linearmodels.panel import PanelOLS, RandomEffects
import pyfixest as pf

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", 200)
pd.set_option("display.width", 200)

ROOT = Path("/content/russia_trade_master")
RAW = ROOT / "raw"
LITE = ROOT / "lite"
OUT = ROOT / "outputs"
TAB = OUT / "tables"
FIG = OUT / "figures"

for p in [RAW, LITE, OUT, TAB, FIG]:
    p.mkdir(parents=True, exist_ok=True)

SEARCH_DIRS = [
    Path("/content"),
    Path("/content/BACI"),
    Path("/content/drive/MyDrive/BACI"),
]

# ===== Notebook code cell 3 =====
def find_file(name):
    for d in SEARCH_DIRS:
        if d.exists():
            p = d / name
            if p.exists():
                return p
    return None

def mount_drive_if_needed():
    try:
        from google.colab import drive
        drive.mount("/content/drive", force_remount=False)
    except Exception as e:
        print("Drive mount:", e)

lite_zip = find_file("Russia_BACI_Lite_Dataset.zip")
baci_zip = find_file("BACI_HS12_V202601.zip")

if lite_zip is None and baci_zip is None:
    mount_drive_if_needed()
    lite_zip = find_file("Russia_BACI_Lite_Dataset.zip")
    baci_zip = find_file("BACI_HS12_V202601.zip")

print("Found Lite ZIP:", lite_zip)
print("Found BACI ZIP:", baci_zip)

# ===== Notebook code cell 4 =====
# Fixed config
BACI_VERSION = "202601"
YEARS = list(range(2015, 2025))
PRE = [2019, 2020, 2021]
ADJUSTMENT_YEAR = 2022
POST = [2023, 2024]

RUS = 643
CHN = 156
IND = 699
TUR = 792
KAZ = 398

EU27 = [
    40,56,100,191,196,203,208,233,246,250,276,300,348,372,
    380,428,440,442,470,528,616,620,642,703,705,724,752
]

if lite_zip is None:
    if baci_zip is None:
        raise FileNotFoundError(
            "Russia_BACI_Lite_Dataset.zip or BACI_HS12_V202601.zip is required."
        )

    print("Lite dataset not found. Building from BACI ZIP...")
    with zipfile.ZipFile(baci_zip) as z:
        names = z.namelist()

    annual_files = {}
    for y in YEARS:
        expected = f"BACI_HS12_Y{y}_V{BACI_VERSION}.csv"
        matches = [n for n in names if Path(n).name == expected]
        if not matches:
            raise FileNotFoundError(expected)
        annual_files[y] = matches[0]

    import_rows, export_rows, china_world_rows = [], [], []

    with zipfile.ZipFile(baci_zip) as z:
        for y in YEARS:
            imp_acc, exp_acc = {}, {}
            chn_world_exp, chn_world_imp = 0.0, 0.0

            with z.open(annual_files[y]) as f:
                reader = pd.read_csv(
                    f, usecols=["i","j","k","v","q"], dtype={"k":"string"},
                    chunksize=700_000, low_memory=False
                )

                for chunk in tqdm(reader, desc=f"Extract {y}", leave=False):
                    chunk["k"] = chunk["k"].astype("string").str.zfill(6)
                    chunk["v"] = pd.to_numeric(chunk["v"], errors="coerce").fillna(0.0)
                    chunk["q"] = pd.to_numeric(chunk["q"], errors="coerce").fillna(0.0)
                    chunk["i"] = pd.to_numeric(chunk["i"], errors="coerce")
                    chunk["j"] = pd.to_numeric(chunk["j"], errors="coerce")

                    # Russia imports: partner i -> Russia
                    imp = chunk[chunk["j"].eq(RUS)]
                    if not imp.empty:
                        g = imp.groupby(["i","k"], as_index=False)[["v","q"]].sum()
                        for r in g.itertuples(index=False):
                            key = (int(r.i), str(r.k))
                            rec = imp_acc.setdefault(key, {"v":0.0,"q":0.0})
                            rec["v"] += float(r.v)
                            rec["q"] += float(r.q)

                    # Russia exports: Russia -> partner j
                    exp = chunk[chunk["i"].eq(RUS)]
                    if not exp.empty:
                        g = exp.groupby(["j","k"], as_index=False)[["v","q"]].sum()
                        for r in g.itertuples(index=False):
                            key = (int(r.j), str(r.k))
                            rec = exp_acc.setdefault(key, {"v":0.0,"q":0.0})
                            rec["v"] += float(r.v)
                            rec["q"] += float(r.q)

                    chn_world_exp += float(chunk.loc[chunk["i"].eq(CHN), "v"].sum())
                    chn_world_imp += float(chunk.loc[chunk["j"].eq(CHN), "v"].sum())

            for (partner, hs6), vals in imp_acc.items():
                import_rows.append({
                    "year": y, "partner": partner, "hs6": hs6,
                    "value_kUSD": vals["v"], "quantity_ton": vals["q"]
                })
            for (partner, hs6), vals in exp_acc.items():
                export_rows.append({
                    "year": y, "partner": partner, "hs6": hs6,
                    "value_kUSD": vals["v"], "quantity_ton": vals["q"]
                })
            china_world_rows.append({
                "year": y,
                "china_world_export_kUSD": chn_world_exp,
                "china_world_import_kUSD": chn_world_imp
            })

    imp_detail = pd.DataFrame(import_rows)
    exp_detail = pd.DataFrame(export_rows)
    china_world = pd.DataFrame(china_world_rows)

    for df in [imp_detail, exp_detail]:
        df["hs6"] = df["hs6"].astype("string").str.zfill(6)
        df["hs2"] = df["hs6"].str[:2]
        df["hs4"] = df["hs6"].str[:4]

    def add_partner_values(base, detail, side):
        partner_map = [(CHN,"china"), (IND,"india"), (TUR,"turkiye"), (KAZ,"kazakhstan")]
        for code, name in partner_map:
            g = detail[detail["partner"].eq(code)].groupby(["year","hs6"], as_index=False)["value_kUSD"].sum()
            g = g.rename(columns={"value_kUSD": f"{name}_{side}_kUSD"})
            base = base.merge(g, on=["year","hs6"], how="left")
        eu = detail[detail["partner"].isin(EU27)].groupby(["year","hs6"], as_index=False)["value_kUSD"].sum()
        eu = eu.rename(columns={"value_kUSD": f"eu27_{side}_kUSD"})
        base = base.merge(eu, on=["year","hs6"], how="left")
        return base

    imp = imp_detail.groupby(["year","hs6","hs2","hs4"], as_index=False).agg(
        world_import_kUSD=("value_kUSD","sum"),
        world_import_qty=("quantity_ton","sum")
    )
    imp = add_partner_values(imp, imp_detail, "import")
    for c in ["china_import_kUSD","india_import_kUSD","turkiye_import_kUSD","kazakhstan_import_kUSD","eu27_import_kUSD"]:
        imp[c] = imp[c].fillna(0.0)
    for name in ["china","india","turkiye","eu27"]:
        imp[f"{name}_share"] = np.where(
            imp["world_import_kUSD"] > 0,
            imp[f"{name}_import_kUSD"] / imp["world_import_kUSD"],
            np.nan
        )

    exp = exp_detail.groupby(["year","hs6","hs2","hs4"], as_index=False).agg(
        world_export_kUSD=("value_kUSD","sum"),
        world_export_qty=("quantity_ton","sum")
    )
    exp = add_partner_values(exp, exp_detail, "export")
    for c in ["china_export_kUSD","india_export_kUSD","turkiye_export_kUSD","kazakhstan_export_kUSD","eu27_export_kUSD"]:
        exp[c] = exp[c].fillna(0.0)
    for name in ["china","india","turkiye","eu27"]:
        exp[f"{name}_share"] = np.where(
            exp["world_export_kUSD"] > 0,
            exp[f"{name}_export_kUSD"] / exp["world_export_kUSD"],
            np.nan
        )

    tmp = ROOT / "lite_temp"
    tmp.mkdir(exist_ok=True)

    imp_detail.to_parquet(tmp/"russia_import_partner_hs6_year.parquet", index=False)
    exp_detail.to_parquet(tmp/"russia_export_partner_hs6_year.parquet", index=False)
    imp.to_parquet(tmp/"russia_import_hs6_year_summary.parquet", index=False)
    exp.to_parquet(tmp/"russia_export_hs6_year_summary.parquet", index=False)
    china_world.to_parquet(tmp/"china_world_trade_year.parquet", index=False)

    with open(tmp/"metadata.json","w",encoding="utf-8") as f:
        json.dump({
            "source":"CEPII BACI HS2012 V202601",
            "years":YEARS,
            "note":"Auto-built by master notebook"
        }, f, indent=2, ensure_ascii=False)

    lite_zip = ROOT / "Russia_BACI_Lite_Dataset.zip"
    if lite_zip.exists():
        lite_zip.unlink()
    shutil.make_archive(str(lite_zip.with_suffix("")), "zip", tmp)
    print("Built Lite ZIP:", lite_zip)

else:
    print("Using existing Lite ZIP:", lite_zip)

# ===== Notebook code cell 5 =====
# Extract Lite ZIP
if LITE.exists():
    shutil.rmtree(LITE)
LITE.mkdir(parents=True)

with zipfile.ZipFile(lite_zip) as z:
    z.extractall(LITE)

imp_detail = pd.read_parquet(LITE/"russia_import_partner_hs6_year.parquet")
exp_detail = pd.read_parquet(LITE/"russia_export_partner_hs6_year.parquet")
imp = pd.read_parquet(LITE/"russia_import_hs6_year_summary.parquet")
exp = pd.read_parquet(LITE/"russia_export_hs6_year_summary.parquet")
china_world = pd.read_parquet(LITE/"china_world_trade_year.parquet")

for df in [imp_detail, exp_detail]:
    if "hs2" not in df.columns:
        df["hs2"] = df["hs6"].astype("string").str.zfill(6).str[:2]

print("Loaded datasets:")
print("imp_detail:", imp_detail.shape)
print("exp_detail:", exp_detail.shape)
print("imp summary:", imp.shape)
print("exp summary:", exp.shape)

# ===== Notebook code cell 7 =====
def yearly_partner_shares(detail):
    total = detail.groupby("year")["value_kUSD"].sum()
    rows = []
    for y in sorted(detail.year.unique()):
        d = detail[detail.year.eq(y)]
        den = total.loc[y]
        eu = d[d.partner.isin(EU27)]["value_kUSD"].sum()
        rows.append({
            "year": y,
            "China": d.loc[d.partner.eq(CHN), "value_kUSD"].sum()/den if den else np.nan,
            "India": d.loc[d.partner.eq(IND), "value_kUSD"].sum()/den if den else np.nan,
            "Turkiye": d.loc[d.partner.eq(TUR), "value_kUSD"].sum()/den if den else np.nan,
            "Kazakhstan": d.loc[d.partner.eq(KAZ), "value_kUSD"].sum()/den if den else np.nan,
            "EU27": eu/den if den else np.nan
        })
    return pd.DataFrame(rows)

def prepost_summary(df, side):
    rows = []
    for c in ["China","India","Turkiye","Kazakhstan","EU27"]:
        pre = df[df.year.isin(PRE)][c].mean()
        post = df[df.year.isin(POST)][c].mean()
        rows.append({"side": side, "partner": c, "pre": pre, "post": post, "change_pp": 100*(post-pre)})
    return pd.DataFrame(rows)

def concentration_from_detail(detail):
    rows = []
    for y, d in detail.groupby("year"):
        g = d.groupby("partner")["value_kUSD"].sum()
        vals = g[g>0].values.astype(float)
        s = vals/vals.sum()
        ss = np.sort(s)[::-1]
        hhi = np.sum(s*s)
        rows.append({
            "year": y,
            "HHI": hhi,
            "CR1": ss[0],
            "CR3": ss[:3].sum(),
            "Entropy": -np.sum(s*np.log(s)),
            "EffectiveN": 1/hhi
        })
    return pd.DataFrame(rows)

def conc_summary(df, side):
    rows = []
    for c in ["HHI","CR1","CR3","Entropy","EffectiveN"]:
        pre = df[df.year.isin(PRE)][c].mean()
        post = df[df.year.isin(POST)][c].mean()
        rows.append({
            "side": side,
            "metric": c,
            "pre": pre,
            "post": post,
            "change": post-pre,
            "growth_pct": (post/pre-1)*100 if pre!=0 else np.nan
        })
    return pd.DataFrame(rows)

def build_prepost(df, cols):
    pre = df[df.year.isin(PRE)].groupby(["hs6","hs2"], as_index=False)[cols].mean()
    post = df[df.year.isin(POST)].groupby(["hs6","hs2"], as_index=False)[cols].mean()
    pre = pre.rename(columns={c:f"{c}_pre" for c in cols})
    post = post.rename(columns={c:f"{c}_post" for c in cols})
    out = pre.merge(post, on=["hs6","hs2"], how="inner")
    for c in cols:
        out[f"delta_{c}"] = out[f"{c}_post"] - out[f"{c}_pre"]
    return out

def rank_biserial(d):
    d = np.asarray(d)
    d = d[np.isfinite(d) & (d != 0)]
    if len(d) == 0:
        return np.nan
    ranks = stats.rankdata(np.abs(d))
    wp = ranks[d>0].sum()
    wm = ranks[d<0].sum()
    return (wp-wm)/(wp+wm) if (wp+wm)>0 else np.nan

def bootstrap_ci(d, func=np.mean, B=3000, seed=42):
    d = np.asarray(d)
    d = d[np.isfinite(d)]
    rng = np.random.default_rng(seed)
    vals = np.array([func(rng.choice(d, size=len(d), replace=True)) for _ in range(B)])
    return np.quantile(vals, [0.025, 0.975])

def signflip_p(d, B=5000, seed=42):
    d = np.asarray(d)
    d = d[np.isfinite(d)]
    obs = np.mean(d)
    rng = np.random.default_rng(seed)
    sims = np.array([(d * rng.choice([-1,1], size=len(d))).mean() for _ in range(B)])
    return (np.sum(np.abs(sims) >= abs(obs)) + 1) / (B + 1)

def summarize_change(d, label):
    d = np.asarray(d)
    d = d[np.isfinite(d)]
    wil = stats.wilcoxon(d, zero_method="wilcox", alternative="two-sided")
    ci_mean = bootstrap_ci(d, np.mean)
    ci_median = bootstrap_ci(d, np.median)
    return {
        "outcome": label,
        "n_hs6": len(d),
        "mean_change_pp": 100*np.mean(d),
        "median_change_pp": 100*np.median(d),
        "share_positive_pct": 100*np.mean(d>0),
        "wilcoxon_p": wil.pvalue,
        "bootstrap_mean_lo_pp": 100*ci_mean[0],
        "bootstrap_mean_hi_pp": 100*ci_mean[1],
        "bootstrap_median_lo_pp": 100*ci_median[0],
        "bootstrap_median_hi_pp": 100*ci_median[1],
        "permutation_p": signflip_p(d),
        "rank_biserial": rank_biserial(d)
    }

# ===== Notebook code cell 9 =====
# T1
imp_partner = yearly_partner_shares(imp_detail)
exp_partner = yearly_partner_shares(exp_detail)
t1 = pd.concat([prepost_summary(imp_partner, "Import"),
                prepost_summary(exp_partner, "Export")], ignore_index=True)

# T2
imp_conc = concentration_from_detail(imp_detail)
exp_conc = concentration_from_detail(exp_detail)
t2 = pd.concat([conc_summary(imp_conc, "Import"),
                conc_summary(exp_conc, "Export")], ignore_index=True)

# T3
t3 = t1[t1.partner.isin(["China","India","Turkiye"])].copy()

# T4
dep_rows = []
for y, g in imp.groupby("year"):
    x = g[g.world_import_kUSD.gt(0)].copy()
    dep_rows.append({
        "year": y,
        "eligible_hs6": len(x),
        "china_ge_50": int((x.china_share >= .50).sum()),
        "china_ge_70": int((x.china_share >= .70).sum()),
        "china_ge_90": int((x.china_share >= .90).sum()),
        "share_ge_50": (x.china_share >= .50).mean(),
        "share_ge_70": (x.china_share >= .70).mean(),
        "share_ge_90": (x.china_share >= .90).mean(),
    })
dep = pd.DataFrame(dep_rows)

def dep_prepost(col):
    pre = dep[dep.year.isin(PRE)][col].mean()
    post = dep[dep.year.isin(POST)][col].mean()
    return pre, post, (post/pre - 1)*100 if pre else np.nan

t4_rows = []
for c in ["eligible_hs6","china_ge_50","china_ge_70","china_ge_90","share_ge_50","share_ge_70","share_ge_90"]:
    pre, post, g = dep_prepost(c)
    t4_rows.append({"metric": c, "pre": pre, "post": post, "growth_pct": g})
t4 = pd.DataFrame(t4_rows)

# T5
imp_nonenergy = yearly_partner_shares(imp_detail[imp_detail.hs2.ne("27")])
exp_nonenergy = yearly_partner_shares(exp_detail[exp_detail.hs2.ne("27")])
t5 = pd.concat([prepost_summary(imp_nonenergy, "Import_nonenergy"),
                prepost_summary(exp_nonenergy, "Export_nonenergy")], ignore_index=True)

# T6
energy = exp_detail[(exp_detail.partner.eq(CHN)) & (exp_detail.hs6.astype(str).str.zfill(6).eq("270900"))].copy()
annual_energy = energy.groupby("year", as_index=False).agg(
    value_kUSD=("value_kUSD","sum"),
    quantity_ton=("quantity_ton","sum")
)
annual_energy["unit_value_USD_ton"] = np.where(
    annual_energy.quantity_ton > 0,
    annual_energy.value_kUSD*1000/annual_energy.quantity_ton,
    np.nan
)
def mean_ys(df, col, ys):
    return df[df.year.isin(ys)][col].mean()

t6 = pd.DataFrame([{
    "hs6": "270900",
    "pre_value_kUSD": mean_ys(annual_energy, "value_kUSD", PRE),
    "post_value_kUSD": mean_ys(annual_energy, "value_kUSD", POST),
    "value_growth_pct": (mean_ys(annual_energy, "value_kUSD", POST)/mean_ys(annual_energy, "value_kUSD", PRE)-1)*100,
    "pre_quantity_ton": mean_ys(annual_energy, "quantity_ton", PRE),
    "post_quantity_ton": mean_ys(annual_energy, "quantity_ton", POST),
    "quantity_growth_pct": (mean_ys(annual_energy, "quantity_ton", POST)/mean_ys(annual_energy, "quantity_ton", PRE)-1)*100,
    "pre_unit_value": mean_ys(annual_energy, "unit_value_USD_ton", PRE),
    "post_unit_value": mean_ys(annual_energy, "unit_value_USD_ton", POST),
    "unit_value_growth_pct": (mean_ys(annual_energy, "unit_value_USD_ton", POST)/mean_ys(annual_energy, "unit_value_USD_ton", PRE)-1)*100
}])

# T7
rus_imp = imp_detail.groupby("year")["value_kUSD"].sum()
rus_exp = exp_detail.groupby("year")["value_kUSD"].sum()
china_to_russia = imp_detail[imp_detail.partner.eq(CHN)].groupby("year")["value_kUSD"].sum()
russia_to_china = exp_detail[exp_detail.partner.eq(CHN)].groupby("year")["value_kUSD"].sum()
cw = china_world.set_index("year")

gap_rows = []
for y in sorted(imp_detail.year.unique()):
    rim = china_to_russia.get(y, 0)/rus_imp.loc[y]
    cex = china_to_russia.get(y, 0)/cw.loc[y, "china_world_export_kUSD"]
    rex = russia_to_china.get(y, 0)/rus_exp.loc[y]
    cim = russia_to_china.get(y, 0)/cw.loc[y, "china_world_import_kUSD"]
    for direction, a, b in [("ImportSide", rim, cex), ("ExportSide", rex, cim)]:
        ratio = a/b if b>0 else np.nan
        gap_rows.append({
            "year": y, "direction": direction,
            "RussiaExposure": a, "ChinaExposure": b,
            "Difference": a-b,
            "Ratio": ratio,
            "LogRatio": np.log(ratio) if ratio>0 else np.nan
        })
gap = pd.DataFrame(gap_rows)

t7_rows = []
for direction, d in gap.groupby("direction"):
    for c in ["Difference","Ratio","LogRatio"]:
        pre = d[d.year.isin(PRE)][c].mean()
        post = d[d.year.isin(POST)][c].mean()
        t7_rows.append({"direction": direction, "metric": c, "pre": pre, "post": post, "change": post-pre})
t7 = pd.DataFrame(t7_rows)

# T8
def segmented_fit(df, ycol, break_year):
    d = df[["year", ycol]].dropna().copy()
    d["time"] = d.year - d.year.min()
    d["post"] = (d.year >= break_year).astype(int)
    d["time_after"] = np.where(d.year >= break_year, d.year - break_year, 0)
    X = sm.add_constant(d[["time","post","time_after"]])
    m = sm.OLS(d[ycol], X).fit(cov_type="HAC", cov_kwds={"maxlags":1})
    return {
        "break_year": break_year,
        "aic": m.aic,
        "post_coef": m.params.get("post", np.nan),
        "post_p": m.pvalues.get("post", np.nan),
        "trend_change_coef": m.params.get("time_after", np.nan),
        "trend_change_p": m.pvalues.get("time_after", np.nan)
    }

series = {
    "ImportShare_China": imp_partner[["year","China"]].rename(columns={"China":"y"}),
    "ExportShare_China": exp_partner[["year","China"]].rename(columns={"China":"y"}),
    "Import_HHI": imp_conc[["year","HHI"]].rename(columns={"HHI":"y"}),
    "Export_HHI": exp_conc[["year","HHI"]].rename(columns={"HHI":"y"})
}
break_rows = []
for name, d in series.items():
    for b in range(2018, 2024):
        r = segmented_fit(d, "y", b)
        r["series"] = name
        break_rows.append(r)
breaks = pd.DataFrame(break_rows)
t8_best = breaks.sort_values(["series","aic"]).groupby("series").head(1).reset_index(drop=True)

# HS6 stats
imp_pp = build_prepost(imp, ["china_share","eu27_share","india_share","turkiye_share"])
exp_pp = build_prepost(exp, ["china_share","eu27_share","india_share","turkiye_share"])

hs6_rows = []
for df, name in [(imp_pp, "Import"), (exp_pp, "Export")]:
    for col, partner in [("delta_china_share","China"),("delta_eu27_share","EU27"),
                         ("delta_india_share","India"),("delta_turkiye_share","Turkiye")]:
        hs6_rows.append(summarize_change(df[col], f"{name}: {partner} share"))
hs6_stats = pd.DataFrame(hs6_rows)

# Non-energy HS6 stats
nonenergy_stats = pd.DataFrame([
    summarize_change(imp_pp[imp_pp.hs2.ne("27")]["delta_china_share"], "Import non-energy: China"),
    summarize_change(exp_pp[exp_pp.hs2.ne("27")]["delta_china_share"], "Export non-energy: China"),
    summarize_change(imp_pp[imp_pp.hs2.ne("27")]["delta_eu27_share"], "Import non-energy: EU27"),
    summarize_change(exp_pp[exp_pp.hs2.ne("27")]["delta_eu27_share"], "Export non-energy: EU27"),
])

# China-EU correlation
d_corr = imp_pp[["hs6","hs2","delta_china_share","delta_eu27_share"]].dropna().copy()
pearson = stats.pearsonr(d_corr["delta_eu27_share"], d_corr["delta_china_share"])
spearman = stats.spearmanr(d_corr["delta_eu27_share"], d_corr["delta_china_share"])
corr = pd.DataFrame([{
    "n": len(d_corr),
    "pearson_r": pearson.statistic, "pearson_p": pearson.pvalue,
    "spearman_rho": spearman.statistic, "spearman_p": spearman.pvalue,
    "share_EUdown_ChinaUp_pct": 100*np.mean((d_corr["delta_eu27_share"]<0)&(d_corr["delta_china_share"]>0))
}])

display(t1.round(4))
display(t2.round(4))
display(t4.round(4))
display(hs6_stats.round(4))

# ===== Notebook code cell 11 =====
# ============================================================
# R1-R8 robustness suite
# ============================================================

def conc_table(d):
    rows = []
    for y, g in d.groupby("year"):
        s = g.groupby("partner")["value_kUSD"].sum()
        s = s[s > 0]
        sh = s / s.sum()
        rows.append(dict(
            year=y,
            China=sh.get(CHN, 0.0),
            EU27=sh[sh.index.isin(EU27)].sum(),
            HHI=(sh**2).sum(),
            CR3=sh.sort_values(ascending=False).iloc[:3].sum(),
            Entropy=-(sh*np.log(sh)).sum(),
            EffN=1/(sh**2).sum(),
            total_bnUSD=s.sum()/1e6,
            n_partners=len(s)
        ))
    return pd.DataFrame(rows).set_index("year")

def prepost_table(t, post=POST):
    return pd.DataFrame({
        "pre": t.loc[PRE].mean(),
        "post": t.loc[post].mean()
    }).T

def balanced_partners(d, years=range(2019, 2025)):
    pos = d[d.value_kUSD > 0].groupby(["partner","year"]).size().unstack(fill_value=0)
    years = list(years)
    missing = [y for y in years if y not in pos.columns]
    if missing:
        raise ValueError(f"Missing years in balanced-panel construction: {missing}")
    return pos.index[(pos[years] > 0).all(axis=1)]

# -------------------------
# R1. Coverage diagnostics
# -------------------------
coverage_rows = []
for side, d in [("Import", imp_detail), ("Export", exp_detail)]:
    t = conc_table(d)[["total_bnUSD","n_partners"]].copy()
    t["Belarus_bnUSD"] = (
        d[d.partner.eq(112)].groupby("year")["value_kUSD"]
        .sum().reindex(t.index).fillna(0)/1e6
    )
    t["side"] = side
    coverage_rows.append(t.reset_index())

r1 = pd.concat(coverage_rows, ignore_index=True)
r1.to_csv(TAB/"R1_coverage_by_year.csv", index=False)
display(r1.round(3))

# -------------------------
# R2. Balanced partner panel
# -------------------------
r2_rows = []
balanced_ids = {
    "Import": balanced_partners(imp_detail),
    "Export": balanced_partners(exp_detail)
}

for side, d in [("Import", imp_detail), ("Export", exp_detail)]:
    bal = balanced_ids[side]
    samples = [
        ("baseline", d),
        ("balanced_partners", d[d.partner.isin(bal)]),
        ("excl_Belarus", d[d.partner.ne(112)])
    ]
    for label, dd in samples:
        for post_label, post_years in [("2023-24", POST), ("2023only", [2023])]:
            pp = prepost_table(conc_table(dd), post_years)
            for m in ["China","EU27","HHI","CR3","Entropy","EffN"]:
                r2_rows.append(dict(
                    side=side, sample=label, post=post_label, metric=m,
                    pre=pp.loc["pre",m],
                    post_val=pp.loc["post",m],
                    change=pp.loc["post",m]-pp.loc["pre",m]
                ))

r2 = pd.DataFrame(r2_rows)
r2.to_csv(TAB/"R2_balanced_partner_robustness.csv", index=False)
display(r2[r2.post.eq("2023-24")].round(4))

# Annual balanced-partner trajectories for pre-trend / Figure 1 robustness
imp_bal_yearly = conc_table(imp_detail[imp_detail.partner.isin(balanced_ids["Import"])]).reset_index()
exp_bal_yearly = conc_table(exp_detail[exp_detail.partner.isin(balanced_ids["Export"])]).reset_index()
imp_bal_yearly.to_csv(TAB/"R2_import_balanced_by_year.csv", index=False)
exp_bal_yearly.to_csv(TAB/"R2_export_balanced_by_year.csv", index=False)

# -------------------------
# R3. BoP denominator bound
# -------------------------
# Bank of Russia, Russia's Balance of Payments in 2019–2025
# (Analytical Presentation), single official vintage. USD bn.
# Used only as a denominator sensitivity bound, not as a BACI substitute.
BOP_IMPORTS = {
    2021: 301.047,
    2023: 303.086,
    2024: 301.548
}

chn_imp_bn = imp_detail[imp_detail.partner.eq(CHN)].groupby("year")["value_kUSD"].sum()/1e6
baci_imp_bn = imp_detail.groupby("year")["value_kUSD"].sum()/1e6

r3 = pd.DataFrame([
    {
        "year": y,
        "China_bnUSD": chn_imp_bn.get(y, np.nan),
        "BACI_imports_bnUSD": baci_imp_bn.get(y, np.nan),
        "BoP_imports_bnUSD": v,
        "China_share_BoPdenom": (chn_imp_bn.get(y, np.nan)/v if v else np.nan),
        "BACI_to_BoP_coverage": (baci_imp_bn.get(y, np.nan)/v if v else np.nan)
    }
    for y, v in BOP_IMPORTS.items()
])
r3.to_csv(TAB/"R3_bop_denominator_bound.csv", index=False)
display(r3.round(4))

# BoP-denominator import-side exposure-gap sensitivity.
# ChinaExposure is based on China's trade denominator from T7; only the Russia-side import denominator is replaced.
imp_gap_base = gap[gap.direction.eq("ImportSide")].set_index("year")
r3_gap_rows = []
for _, rr in r3.iterrows():
    y = int(rr["year"])
    rus_share = rr["China_share_BoPdenom"]
    chn_share = imp_gap_base.loc[y, "ChinaExposure"]
    r3_gap_rows.append({
        "year": y,
        "RussiaExposure_BoPdenom": rus_share,
        "ChinaExposure": chn_share,
        "Difference": rus_share-chn_share,
        "Ratio": rus_share/chn_share if chn_share>0 else np.nan,
        "LogRatio": np.log(rus_share/chn_share) if rus_share>0 and chn_share>0 else np.nan
    })
r3_gap = pd.DataFrame(r3_gap_rows)
r3_gap.to_csv(TAB/"R3_bop_exposure_gap_sensitivity.csv", index=False)
display(r3_gap.round(4))

# Pre/post summary uses 2021 as the pre reference because the BoP sensitivity table
# is constructed for 2021, 2023 and 2024; this is not the same pre-window as the main 2019–2021 BACI analysis.
r3_gap_summary = pd.DataFrame([{
    "metric": m,
    "pre_2021": r3_gap.loc[r3_gap.year.eq(2021), m].iloc[0],
    "post_2023_24": r3_gap.loc[r3_gap.year.isin([2023,2024]), m].mean(),
    "change": r3_gap.loc[r3_gap.year.isin([2023,2024]), m].mean() - r3_gap.loc[r3_gap.year.eq(2021), m].iloc[0]
} for m in ["Difference","Ratio","LogRatio"]])
r3_gap_summary.to_csv(TAB/"R3_bop_exposure_gap_prepost.csv", index=False)
display(r3_gap_summary.round(4))

# -------------------------
# R4. HS6 dependence: baseline vs balanced partner sample
# -------------------------
def dep_counts(d):
    w = d.groupby(["year","hs6"])["value_kUSD"].sum()
    c = (
        d[d.partner.eq(CHN)].groupby(["year","hs6"])["value_kUSD"].sum()
        .reindex(w.index).fillna(0)
    )
    valid = w > 0
    s = (c[valid] / w[valid])
    ww = w[valid]

    out = s.groupby("year").agg(
        eligible="size",
        ge50=lambda x: (x >= .5).sum(),
        ge70=lambda x: (x >= .7).sum(),
        ge90=lambda x: (x >= .9).sum()
    )
    out["value_share_in_ge50"] = (
        (ww*(s >= .5)).groupby("year").sum()/ww.groupby("year").sum()
    )
    return out

imp_bal_ids = balanced_ids["Import"]
r4_base = dep_counts(imp_detail)
r4_bal = dep_counts(imp_detail[imp_detail.partner.isin(imp_bal_ids)])

r4 = pd.concat(
    {"baseline": r4_base, "balanced": r4_bal},
    names=["sample","year"]
).reset_index()
r4.to_csv(TAB/"R4_dependence_counts_balanced.csv", index=False)
display(r4.round(4))

# Pre/post summary for manuscript
r4_pp_rows = []
for sample, g in r4.groupby("sample"):
    for metric in ["eligible","ge50","ge70","ge90","value_share_in_ge50"]:
        pre_val = g[g.year.isin(PRE)][metric].mean()
        post_val = g[g.year.isin(POST)][metric].mean()
        r4_pp_rows.append({
            "sample": sample,
            "metric": metric,
            "pre": pre_val,
            "post": post_val,
            "change": post_val-pre_val,
            "growth_pct": ((post_val/pre_val-1)*100 if pre_val != 0 else np.nan)
        })
r4_pp = pd.DataFrame(r4_pp_rows)
r4_pp.to_csv(TAB/"R4_dependence_prepost_balanced.csv", index=False)
display(r4_pp.round(3))

# -------------------------
# R5. Sign / zero decomposition
# -------------------------
r5_rows = []
for side, df in [("Import", imp_pp), ("Export", exp_pp)]:
    for p in ["china","eu27","india","turkiye"]:
        d = df[f"delta_{p}_share"].dropna()
        r5_rows.append(dict(
            side=side, partner=p, n=len(d),
            pos_pct=100*(d > 0).mean(),
            zero_pct=100*(d == 0).mean(),
            neg_pct=100*(d < 0).mean()
        ))
r5 = pd.DataFrame(r5_rows)
r5.to_csv(TAB/"R5_sign_decomposition.csv", index=False)
display(r5.round(2))

# -------------------------
# R6. HS4 cluster bootstrap
# -------------------------
def cluster_boot(df, col, B=3000, seed=42):
    x = df[["hs6", col]].dropna().copy()
    x["hs4"] = x.hs6.astype(str).str.zfill(6).str[:4]
    g = x.groupby("hs4")[col].agg(["sum","count"])
    S = g["sum"].values
    N = g["count"].values
    rng = np.random.default_rng(seed)
    k = len(g)
    bs = np.empty(B)
    for b in range(B):
        idx = rng.integers(0, k, k)
        bs[b] = S[idx].sum()/N[idx].sum()
    q = 100*np.quantile(bs, [.025,.975])
    return len(g), q[0], q[1]

r6_rows = []
for side, df in [("Import", imp_pp), ("Export", exp_pp)]:
    for c in ["delta_china_share","delta_eu27_share","delta_india_share","delta_turkiye_share"]:
        k, lo, hi = cluster_boot(df, c)
        r6_rows.append({
            "side": side,
            "outcome": c,
            "n_hs4_clusters": k,
            "cluster_boot_ci_lo_pp": lo,
            "cluster_boot_ci_hi_pp": hi
        })
r6 = pd.DataFrame(r6_rows)
r6.to_csv(TAB/"R6_hs4_cluster_bootstrap.csv", index=False)
display(r6.round(3))

# -------------------------
# R7. EU-to-China absorption pattern
# -------------------------
r7d = imp_pp[["delta_china_share","delta_eu27_share","eu27_share_pre"]].dropna()
slope = np.polyfit(r7d.delta_eu27_share, r7d.delta_china_share, 1)[0]
dom = r7d[r7d.eu27_share_pre > .5]

mean_deu = dom.delta_eu27_share.mean()
mean_dchn = dom.delta_china_share.mean()
absorption_ratio = (
    mean_dchn / abs(mean_deu)
    if mean_deu < 0 else np.nan
)

r7 = pd.DataFrame([{
    "ols_slope_dChina_on_dEU": slope,
    "n_EU_dominant": len(dom),
    "EU_dominant_dEU_pp": 100*mean_deu,
    "EU_dominant_dChina_pp": 100*mean_dchn,
    "absorption_ratio": absorption_ratio,
    "absorption_pct": 100*absorption_ratio if pd.notna(absorption_ratio) else np.nan
}])
r7.to_csv(TAB/"R7_eu_to_china_absorption.csv", index=False)
display(r7.round(3))

# -------------------------
# R8. Export energy decomposition: China vs India
# -------------------------
def partner_export_decomposition(detail, partner_code, partner_name):
    d = detail[detail.partner.eq(partner_code)].copy()

    annual_all = d.groupby("year").agg(
        value_kUSD=("value_kUSD","sum"),
        quantity_ton=("quantity_ton","sum")
    )
    annual_energy = d[d.hs2.eq("27")].groupby("year").agg(
        energy_value_kUSD=("value_kUSD","sum"),
        energy_quantity_ton=("quantity_ton","sum")
    )
    annual_non = d[d.hs2.ne("27")].groupby("year").agg(
        nonenergy_value_kUSD=("value_kUSD","sum"),
        nonenergy_quantity_ton=("quantity_ton","sum")
    )
    annual = annual_all.join(annual_energy, how="left").join(annual_non, how="left").fillna(0)
    annual["energy_value_share"] = np.where(
        annual["value_kUSD"]>0,
        annual["energy_value_kUSD"]/annual["value_kUSD"],
        np.nan
    )

    rows = []
    for metric in [
        "value_kUSD","energy_value_kUSD","nonenergy_value_kUSD",
        "quantity_ton","energy_quantity_ton","nonenergy_quantity_ton",
        "energy_value_share"
    ]:
        pre_val = annual.loc[annual.index.isin(PRE), metric].mean()
        post_val = annual.loc[annual.index.isin(POST), metric].mean()
        rows.append({
            "partner": partner_name,
            "metric": metric,
            "pre": pre_val,
            "post": post_val,
            "change": post_val-pre_val,
            "growth_pct": ((post_val/pre_val-1)*100 if pre_val != 0 else np.nan)
        })

    # HS270900 separately
    crude = d[d.hs6.astype(str).str.zfill(6).eq("270900")].groupby("year").agg(
        crude_value_kUSD=("value_kUSD","sum"),
        crude_quantity_ton=("quantity_ton","sum")
    )
    for metric in ["crude_value_kUSD","crude_quantity_ton"]:
        pre_val = crude.loc[crude.index.isin(PRE), metric].mean() if len(crude) else np.nan
        post_val = crude.loc[crude.index.isin(POST), metric].mean() if len(crude) else np.nan
        rows.append({
            "partner": partner_name,
            "metric": metric,
            "pre": pre_val,
            "post": post_val,
            "change": post_val-pre_val if pd.notna(pre_val) and pd.notna(post_val) else np.nan,
            "growth_pct": ((post_val/pre_val-1)*100 if pd.notna(pre_val) and pre_val != 0 else np.nan)
        })

    annual = annual.reset_index()
    annual["partner"] = partner_name
    return pd.DataFrame(rows), annual

r8_china, r8_china_year = partner_export_decomposition(exp_detail, CHN, "China")
r8_india, r8_india_year = partner_export_decomposition(exp_detail, IND, "India")
r8 = pd.concat([r8_china, r8_india], ignore_index=True)
r8_year = pd.concat([r8_china_year, r8_india_year], ignore_index=True)

# Link aggregate partner-share changes to non-energy changes
for partner_name in ["China","India"]:
    overall = t1[(t1.side=="Export") & (t1.partner==partner_name)]["change_pp"]
    nonen = t5[(t5.side=="Export_nonenergy") & (t5.partner==partner_name)]["change_pp"]
    if len(overall) and len(nonen):
        r8.loc[len(r8)] = {
            "partner": partner_name,
            "metric": "aggregate_export_share_change_pp",
            "pre": np.nan, "post": np.nan,
            "change": float(overall.iloc[0]),
            "growth_pct": np.nan
        }
        r8.loc[len(r8)] = {
            "partner": partner_name,
            "metric": "nonenergy_export_share_change_pp",
            "pre": np.nan, "post": np.nan,
            "change": float(nonen.iloc[0]),
            "growth_pct": np.nan
        }

r8.to_csv(TAB/"R8_export_energy_decomposition.csv", index=False)
r8_year.to_csv(TAB/"R8_export_energy_by_year.csv", index=False)
display(r8.round(3))

# ===== Notebook code cell 13 =====
# Figure 1: Import partner shares
plt.figure(figsize=(10,5.5))
for p in ["China","EU27","India","Turkiye"]:
    plt.plot(imp_partner["year"], 100*imp_partner[p], marker="o", label=p)
# balanced-partner China series is available from 2019 onward by construction
if "imp_bal_yearly" in globals():
    plt.plot(imp_bal_yearly["year"], 100*imp_bal_yearly["China"], marker="s", linestyle="--", label="China (balanced partners)")
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year"); plt.ylabel("Share (%)")
plt.title("Russia import partner shares, 2015–2024")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure1_Import_Partner_Shares.png", dpi=300)
plt.show()

# Figure 2: Concentration
plt.figure(figsize=(10,5.5))
plt.plot(imp_conc["year"], imp_conc["HHI"], marker="o", label="Import HHI")
plt.plot(exp_conc["year"], exp_conc["HHI"], marker="o", label="Export HHI")
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year"); plt.ylabel("HHI")
plt.title("Trade concentration (HHI), 2015–2024")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure2_Trade_Concentration_HHI.png", dpi=300)
plt.show()

plt.figure(figsize=(10,5.5))
plt.plot(imp_conc["year"], imp_conc["EffectiveN"], marker="o", label="Import effective N")
plt.plot(exp_conc["year"], exp_conc["EffectiveN"], marker="o", label="Export effective N")
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year"); plt.ylabel("Effective number of partners")
plt.title("Effective number of trade partners, 2015–2024")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure2b_Effective_Number_of_Partners.png", dpi=300)
plt.show()

# Figure 3: High dependence counts
plt.figure(figsize=(10,5.5))
plt.plot(dep["year"], dep["china_ge_50"], marker="o", label="China share ≥50%")
plt.plot(dep["year"], dep["china_ge_70"], marker="o", label="China share ≥70%")
plt.plot(dep["year"], dep["china_ge_90"], marker="o", label="China share ≥90%")
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year"); plt.ylabel("Number of HS6 products")
plt.title("Russia import products highly dependent on China")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure3_High_Dependence_HS6_Counts.png", dpi=300)
plt.show()

# Figure 4: HS6 distribution of China share changes
delta = imp_pp["delta_china_share"].dropna()
plt.figure(figsize=(9,5.5))
plt.hist(100*delta, bins=50)
plt.axvline(0, linewidth=1)
plt.axvline(100*delta.mean(), linestyle="--", linewidth=1)
plt.xlabel("Post − pre China share (percentage points)")
plt.ylabel("Number of HS6 products")
plt.title("Distribution of HS6-level changes in China's import share")
plt.tight_layout()
plt.savefig(FIG/"Figure4_HS6_China_Share_Change_Distribution.png", dpi=300)
plt.show()

# Figure 5: China vs EU scatter
plt.figure(figsize=(8,6.5))
plt.scatter(100*d_corr["delta_eu27_share"], 100*d_corr["delta_china_share"], alpha=.35, s=16)
plt.axhline(0, linewidth=1)
plt.axvline(0, linewidth=1)
plt.xlabel("Change in EU27 share (percentage points)")
plt.ylabel("Change in China share (percentage points)")
plt.title("HS6-level import reorientation: EU27 decline vs China increase")
plt.tight_layout()
plt.savefig(FIG/"Figure5_HS6_EU_vs_China_Scatter.png", dpi=300)
plt.show()

# Figure 6: Bilateral exposure gap (optional but useful)
gap_imp = gap[gap.direction.eq("ImportSide")].copy()
gap_exp = gap[gap.direction.eq("ExportSide")].copy()
plt.figure(figsize=(10,5.5))
plt.plot(gap_imp["year"], 100*gap_imp["Difference"], marker="o", label="Import-side exposure gap")
plt.plot(gap_exp["year"], 100*gap_exp["Difference"], marker="o", label="Export-side exposure gap")
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year"); plt.ylabel("Difference in exposure (percentage points)")
plt.title("Russia–China bilateral trade exposure gap")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure6_Bilateral_Exposure_Gap.png", dpi=300)
plt.show()

# ===== Notebook code cell 15 =====
# R1 Figure: partner coverage
plt.figure(figsize=(10,5.5))
for side in ["Import","Export"]:
    x = r1[r1.side.eq(side)]
    plt.plot(x["year"], x["n_partners"], marker="o", label=side)
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year")
plt.ylabel("Number of observed partners")
plt.title("R1. Observed trade-partner coverage")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure_R1_Partner_Coverage.png", dpi=300)
plt.show()

# R2 Figure: baseline vs balanced import China share and HHI
r2plot = r2[
    (r2.side.eq("Import")) &
    (r2.post.eq("2023-24")) &
    (r2["sample"].isin(["baseline","balanced_partners"])) &
    (r2.metric.isin(["China","HHI"]))
].copy()

fig, ax = plt.subplots(figsize=(8.5,5.5))
tmp = r2plot[r2plot.metric.eq("China")]
xpos = np.arange(len(tmp))
ax.bar(xpos-0.18, 100*tmp["pre"], width=.36, label="Pre")
ax.bar(xpos+0.18, 100*tmp["post_val"], width=.36, label="Post")
ax.set_xticks(xpos)
ax.set_xticklabels(tmp["sample"])
ax.set_ylabel("China import share (%)")
ax.set_title("R2. China import share: baseline vs balanced partners")
ax.legend()
fig.tight_layout()
fig.savefig(FIG/"Figure_R2_Balanced_China_Share.png", dpi=300)
plt.show()

# R4 Figure: high-dependence counts baseline vs balanced
plt.figure(figsize=(10,5.5))
for sample, marker in [("baseline","o"),("balanced","s")]:
    x = r4[r4["sample"].eq(sample)]
    plt.plot(x["year"], x["ge90"], marker=marker, label=f"{sample}: China share ≥90%")
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year")
plt.ylabel("Number of HS6 products")
plt.title("R4. Extreme China dependence: baseline vs balanced sample")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure_R4_Extreme_Dependence_Balanced.png", dpi=300)
plt.show()

# R5 Figure: positive/zero/negative decomposition for exports
x = r5[r5.side.eq("Export")].copy()
plt.figure(figsize=(9,5.5))
bottom = np.zeros(len(x))
for col, lab in [("pos_pct","Increase"),("zero_pct","No change"),("neg_pct","Decrease")]:
    plt.bar(x["partner"], x[col], bottom=bottom, label=lab)
    bottom += x[col].values
plt.ylabel("HS6 products (%)")
plt.title("R5. Export HS6 sign decomposition")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure_R5_Export_Sign_Decomposition.png", dpi=300)
plt.show()

# R7 Figure: EU decline vs China increase, EU-dominant subsample highlighted
plt.figure(figsize=(8,6.5))
plt.scatter(
    100*r7d["delta_eu27_share"],
    100*r7d["delta_china_share"],
    alpha=.18, s=12, label="All HS6"
)
plt.scatter(
    100*dom["delta_eu27_share"],
    100*dom["delta_china_share"],
    alpha=.35, s=14, label="Pre-period EU share >50%"
)
plt.axhline(0, linewidth=1)
plt.axvline(0, linewidth=1)
plt.xlabel("Change in EU27 share (pp)")
plt.ylabel("Change in China share (pp)")
plt.title("R7. EU-to-China reorientation pattern")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure_R7_EU_China_Absorption.png", dpi=300)
plt.show()

# R8 Figure: energy share in exports to China and India
plt.figure(figsize=(10,5.5))
for partner_name in ["China","India"]:
    x = r8_year[r8_year.partner.eq(partner_name)]
    plt.plot(x["year"], 100*x["energy_value_share"], marker="o", label=partner_name)
plt.axvline(2022, linestyle="--", linewidth=1)
plt.xlabel("Year")
plt.ylabel("HS27 share of bilateral export value (%)")
plt.title("R8. Energy intensity of Russian exports to China and India")
plt.legend()
plt.tight_layout()
plt.savefig(FIG/"Figure_R8_Export_Energy_Intensity.png", dpi=300)
plt.show()

# ===== Notebook code cell 17 =====
# Save tables
imp_partner.to_csv(TAB/"T1_import_partner_shares.csv", index=False)
exp_partner.to_csv(TAB/"T1_export_partner_shares.csv", index=False)
t1.to_csv(TAB/"T1_prepost_summary.csv", index=False)

imp_conc.to_csv(TAB/"T2_import_concentration_by_year.csv", index=False)
exp_conc.to_csv(TAB/"T2_export_concentration_by_year.csv", index=False)
t2.to_csv(TAB/"T2_concentration_summary.csv", index=False)

t3.to_csv(TAB/"T3_china_specificity.csv", index=False)

dep.to_csv(TAB/"T4_HS6_dependence_by_year.csv", index=False)
t4.to_csv(TAB/"T4_HS6_dependence_prepost.csv", index=False)

t5.to_csv(TAB/"T5_nonenergy_prepost.csv", index=False)

annual_energy.to_csv(TAB/"T6_annual_energy_to_china.csv", index=False)
t6.to_csv(TAB/"T6_crude_oil_value_quantity.csv", index=False)

gap.to_csv(TAB/"T7_exposure_gap_by_year.csv", index=False)
t7.to_csv(TAB/"T7_exposure_gap_prepost.csv", index=False)

breaks.to_csv(TAB/"T8_break_screening.csv", index=False)
t8_best.to_csv(TAB/"T8_best_breaks.csv", index=False)

imp_pp.to_csv(TAB/"HS6_import_prepost_changes.csv", index=False)
exp_pp.to_csv(TAB/"HS6_export_prepost_changes.csv", index=False)
hs6_stats.to_csv(TAB/"HS6_statistical_tests.csv", index=False)
nonenergy_stats.to_csv(TAB/"HS6_nonenergy_statistical_tests.csv", index=False)
corr.to_csv(TAB/"China_EU_change_correlation.csv", index=False)

# Final audit
audit_rows = []
audit_rows.append(["Import China share change (pp)", float(t1[(t1.side=='Import') & (t1.partner=='China')]['change_pp'].iloc[0])])
audit_rows.append(["Import HHI growth (%)", float(t2[(t2.side=='Import') & (t2.metric=='HHI')]['growth_pct'].iloc[0])])
audit_rows.append(["HS6 China>=50 count growth (%)", float(t4[t4.metric=='china_ge_50']['growth_pct'].iloc[0])])
audit_rows.append(["HS6 China>=70 count growth (%)", float(t4[t4.metric=='china_ge_70']['growth_pct'].iloc[0])])
audit_rows.append(["HS6 China>=90 count growth (%)", float(t4[t4.metric=='china_ge_90']['growth_pct'].iloc[0])])
audit_rows.append(["Non-energy import China change (pp)", float(t5[(t5.side=='Import_nonenergy') & (t5.partner=='China')]['change_pp'].iloc[0])])
audit_rows.append(["Crude oil quantity growth (%)", float(t6['quantity_growth_pct'].iloc[0])])
audit_rows.append(["HS6 import China mean change (pp)", float(hs6_stats[hs6_stats.outcome=='Import: China share']['mean_change_pp'].iloc[0])])
audit_rows.append(["HS6 import EU mean change (pp)", float(hs6_stats[hs6_stats.outcome=='Import: EU27 share']['mean_change_pp'].iloc[0])])
audit = pd.DataFrame(audit_rows, columns=["Metric","FinalValue"])
audit.to_csv(TAB/"FINAL_CONSISTENCY_AUDIT.csv", index=False)

# Workbook
xlsx = OUT / "Russia_Trade_Master_Final_Results.xlsx"
with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
    t1.to_excel(w, sheet_name="T1_partner", index=False)
    t2.to_excel(w, sheet_name="T2_concentration", index=False)
    t3.to_excel(w, sheet_name="T3_specificity", index=False)
    dep.to_excel(w, sheet_name="T4_dependence_year", index=False)
    t4.to_excel(w, sheet_name="T4_dependence_prepost", index=False)
    t5.to_excel(w, sheet_name="T5_nonenergy", index=False)
    annual_energy.to_excel(w, sheet_name="T6_energy_year", index=False)
    t6.to_excel(w, sheet_name="T6_crude_summary", index=False)
    t7.to_excel(w, sheet_name="T7_exposure_gap", index=False)
    t8_best.to_excel(w, sheet_name="T8_best_breaks", index=False)
    hs6_stats.to_excel(w, sheet_name="HS6_stats", index=False)
    nonenergy_stats.to_excel(w, sheet_name="HS6_nonenergy_stats", index=False)
    corr.to_excel(w, sheet_name="China_EU_corr", index=False)
    audit.to_excel(w, sheet_name="Final_audit", index=False)


# Robustness workbook
robust_xlsx = OUT / "Russia_Trade_Master_Robustness_Results.xlsx"
with pd.ExcelWriter(robust_xlsx, engine="openpyxl") as w:
    r1.to_excel(w, sheet_name="R1_coverage", index=False)
    r2.to_excel(w, sheet_name="R2_balanced", index=False)
    r3.to_excel(w, sheet_name="R3_BoP_bound", index=False)
    r4.to_excel(w, sheet_name="R4_dep_year", index=False)
    r4_pp.to_excel(w, sheet_name="R4_dep_prepost", index=False)
    r5.to_excel(w, sheet_name="R5_signs", index=False)
    r6.to_excel(w, sheet_name="R6_HS4_boot", index=False)
    r7.to_excel(w, sheet_name="R7_absorption", index=False)
    r8.to_excel(w, sheet_name="R8_energy", index=False)
    r8_year.to_excel(w, sheet_name="R8_energy_year", index=False)

# Add robustness sheets to the main workbook as well
with pd.ExcelWriter(xlsx, engine="openpyxl", mode="a", if_sheet_exists="replace") as w:
    r1.to_excel(w, sheet_name="R1_coverage", index=False)
    r2.to_excel(w, sheet_name="R2_balanced", index=False)
    r3.to_excel(w, sheet_name="R3_BoP_bound", index=False)
    r4_pp.to_excel(w, sheet_name="R4_balanced_dep", index=False)
    r5.to_excel(w, sheet_name="R5_signs", index=False)
    r6.to_excel(w, sheet_name="R6_cluster_boot", index=False)
    r7.to_excel(w, sheet_name="R7_absorption", index=False)
    r8.to_excel(w, sheet_name="R8_energy", index=False)


# Metadata
metadata = {
    "input_priority": ["Russia_BACI_Lite_Dataset.zip", "BACI_HS12_V202601.zip"],
    "source_used": str(lite_zip),
    "years": YEARS,
    "pre": PRE,
    "adjustment_year": ADJUSTMENT_YEAR,
    "post": POST,
    "design": "non-causal structural empirical analysis",
    "robustness": ["coverage audit","balanced partner panel","BoP denominator bound","balanced HS6 dependence","sign-zero decomposition","HS4 cluster bootstrap","EU-China absorption","export energy decomposition"],
    "outputs": {
        "tables_dir": str(TAB),
        "figures_dir": str(FIG),
        "excel": str(xlsx.name)
    }
}
with open(OUT/"analysis_metadata.json","w",encoding="utf-8") as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

# Zip everything
zip_out = ROOT / "Russia_Trade_Master_Outputs.zip"
if zip_out.exists():
    zip_out.unlink()
shutil.make_archive(str(zip_out.with_suffix("")), "zip", OUT)

print("Excel:", xlsx)
print("ZIP:", zip_out)

print('Structural outputs completed; panel module will run next.')

# ===== Notebook code cell 21 =====

KEY_PARTNERS = {
    "China": CHN,
    "India": IND,
    "Turkiye": TUR,
    "Kazakhstan": KAZ,
}

def partner_year_panel(detail, balanced_window=range(2019, 2025)):
    """Build partner×year panel using a balanced partner universe.
    Shares use the total trade of the balanced partner sample in each year.
    """
    d = detail.groupby(["partner", "year"], as_index=False)["value_kUSD"].sum()
    required = set(balanced_window)
    pos_years = (
        d[d["value_kUSD"] > 0]
        .groupby("partner")["year"]
        .apply(lambda s: set(map(int, s.tolist())))
    )
    balanced = [int(p) for p, ys in pos_years.items() if required.issubset(ys)]

    years = sorted(map(int, detail["year"].unique()))
    grid = pd.MultiIndex.from_product([balanced, years], names=["partner", "year"]).to_frame(index=False)
    p = grid.merge(d, on=["partner", "year"], how="left")
    p["value_kUSD"] = p["value_kUSD"].fillna(0.0)

    den = p.groupby("year")["value_kUSD"].transform("sum")
    p["share"] = np.where(den > 0, p["value_kUSD"] / den, np.nan)

    p["china"] = p["partner"].eq(CHN).astype(int)
    p["india"] = p["partner"].eq(IND).astype(int)
    p["turkiye"] = p["partner"].eq(TUR).astype(int)
    p["kazakhstan"] = p["partner"].eq(KAZ).astype(int)
    p["eu27"] = p["partner"].isin(EU27).astype(int)
    p["post"] = p["year"].isin(POST).astype(int)

    for g in ["china", "india", "turkiye", "kazakhstan", "eu27"]:
        p[f"{g}_post"] = p[g] * p["post"]

    return p, balanced

def tidy_linearmodels(res, model_name, side):
    rows = []
    ci = res.conf_int()
    for term in res.params.index:
        rows.append({
            "side": side,
            "model": model_name,
            "term": str(term),
            "estimate": float(res.params.loc[term]),
            "std_error": float(res.std_errors.loc[term]),
            "t_stat": float(res.tstats.loc[term]),
            "p_value": float(res.pvalues.loc[term]),
            "ci_low": float(ci.loc[term].iloc[0]),
            "ci_high": float(ci.loc[term].iloc[1]),
            "nobs": int(res.nobs),
        })
    return pd.DataFrame(rows)

def fit_partner_fe_re(detail, side):
    p, balanced = partner_year_panel(detail)

    # Match manuscript design: omit 2022 adjustment year.
    m = p[p["year"].ne(ADJUSTMENT_YEAR)].dropna(subset=["share"]).copy()
    m = m.set_index(["partner", "year"]).sort_index()

    inter = ["china_post", "india_post", "turkiye_post", "kazakhstan_post", "eu27_post"]
    # Remove interaction variables with no variation in a particular sample.
    inter = [c for c in inter if m[c].nunique() > 1]

    yd = pd.get_dummies(
        m.index.get_level_values("year"),
        prefix="year",
        drop_first=True,
        dtype=float
    )
    yd.index = m.index

    X = pd.concat([m[inter].astype(float), yd], axis=1)
    X = sm.add_constant(X, has_constant="add")
    y = m["share"].astype(float)

    fe = PanelOLS(
        y, X,
        entity_effects=True,
        drop_absorbed=True,
        check_rank=False
    ).fit(cov_type="clustered", cluster_entity=True)

    re_mod = RandomEffects(y, X)
    re = re_mod.fit(cov_type="clustered", cluster_entity=True)

    fe_tidy = tidy_linearmodels(fe, "Two-way FE", side)
    re_tidy = tidy_linearmodels(re, "Random Effects", side)

    # Hausman comparison for the substantive interaction coefficients only.
    common = [c for c in inter if c in fe.params.index and c in re.params.index]
    if common:
        b_fe = fe.params.loc[common].values
        b_re = re.params.loc[common].values
        V = fe.cov.loc[common, common].values - re.cov.loc[common, common].values
        diff = b_fe - b_re
        Vinv = np.linalg.pinv(V)
        stat = float(diff.T @ Vinv @ diff)
        # Numerical covariance differences can occasionally yield a tiny negative value.
        stat_for_p = max(stat, 0.0)
        df = len(common)
        pval = float(stats.chi2.sf(stat_for_p, df))
    else:
        stat, df, pval = np.nan, 0, np.nan

    hausman = pd.DataFrame([{
        "side": side,
        "terms_compared": ", ".join(common),
        "hausman_chi2": stat,
        "df": df,
        "p_value": pval,
        "interpretation": (
            "Small p favors FE over RE, but treat as a model-comparison diagnostic rather than causal identification."
        )
    }])

    meta = {
        "side": side,
        "balanced_partner_n": len(balanced),
        "years_used": sorted(set(m.index.get_level_values("year"))),
        "adjustment_year_excluded": ADJUSTMENT_YEAR,
    }
    return p.reset_index(drop=True), fe, re, fe_tidy, re_tidy, hausman, meta

def hs6_event_profile(summary_df, outcome, side, cluster_col="hs4", base_year=2021):
    """HS6 product FE event profile.
    Coefficients are within-HS6 changes relative to 2021; not a causal event study.
    """
    d = summary_df[["year", "hs6", "hs4", outcome]].dropna().copy()
    # Balanced HS6 panel over the full 2015–2024 period.
    counts = d.groupby("hs6")["year"].nunique()
    keep = counts[counts.eq(len(YEARS))].index
    d = d[d["hs6"].isin(keep)].copy()

    d = d.set_index(["hs6", "year"]).sort_index()
    years = sorted(set(d.index.get_level_values("year")))
    event_years = [y for y in years if y != base_year]

    X = pd.DataFrame(index=d.index)
    for y in event_years:
        X[f"year_{y}"] = (d.index.get_level_values("year") == y).astype(float)
    X = sm.add_constant(X, has_constant="add")

    y = d[outcome].astype(float)

    clusters = pd.DataFrame(
        {cluster_col: d[cluster_col].astype(str).values},
        index=d.index
    )
    try:
        res = PanelOLS(
            y, X,
            entity_effects=True,
            drop_absorbed=True,
            check_rank=False
        ).fit(cov_type="clustered", clusters=clusters)
        cluster_used = cluster_col
    except Exception:
        res = PanelOLS(
            y, X,
            entity_effects=True,
            drop_absorbed=True,
            check_rank=False
        ).fit(cov_type="clustered", cluster_entity=True)
        cluster_used = "hs6"

    ci = res.conf_int()
    rows = []
    for yr in event_years:
        term = f"year_{yr}"
        if term in res.params.index:
            rows.append({
                "side": side,
                "outcome": outcome,
                "year": yr,
                "base_year": base_year,
                "estimate": float(res.params[term]),
                "estimate_pp": 100 * float(res.params[term]),
                "std_error": float(res.std_errors[term]),
                "ci_low_pp": 100 * float(ci.loc[term].iloc[0]),
                "ci_high_pp": 100 * float(ci.loc[term].iloc[1]),
                "p_value": float(res.pvalues[term]),
                "balanced_hs6_n": int(len(keep)),
                "cluster": cluster_used,
            })
    # Add base year as zero for plotting.
    rows.append({
        "side": side, "outcome": outcome, "year": base_year, "base_year": base_year,
        "estimate": 0.0, "estimate_pp": 0.0, "std_error": np.nan,
        "ci_low_pp": 0.0, "ci_high_pp": 0.0, "p_value": np.nan,
        "balanced_hs6_n": int(len(keep)), "cluster": cluster_used
    })
    out = pd.DataFrame(rows).sort_values("year").reset_index(drop=True)
    return out, res

def plot_event_profile(df, title, filename):
    x = df.sort_values("year")
    plt.figure(figsize=(9, 5.5))
    plt.plot(x["year"], x["estimate_pp"], marker="o")
    low = x["ci_low_pp"].to_numpy(float)
    high = x["ci_high_pp"].to_numpy(float)
    est = x["estimate_pp"].to_numpy(float)
    plt.fill_between(x["year"], low, high, alpha=0.18)
    plt.axhline(0, linewidth=1)
    plt.axvline(2022, linestyle="--", linewidth=1)
    plt.xlabel("Year")
    plt.ylabel("Within-HS6 change vs 2021 (percentage points)")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(FIG / filename, dpi=300)
    plt.show()

def build_bloc_hs6_panel(detail, side):
    """Construct HS6×bloc×year panel including explicit zero flows."""
    d = detail.copy()
    d["hs6"] = d["hs6"].astype("string").str.zfill(6)
    if "hs4" not in d.columns:
        d["hs4"] = d["hs6"].str[:4]

    def classify_partner(p):
        if p == CHN: return "China"
        if p == IND: return "India"
        if p == TUR: return "Turkiye"
        if p == KAZ: return "Kazakhstan"
        if p in EU27: return "EU27"
        return None

    d["bloc"] = d["partner"].map(classify_partner)
    d = d[d["bloc"].notna()].copy()

    agg = d.groupby(["year", "hs6", "hs4", "bloc"], as_index=False)["value_kUSD"].sum()

    hs6s = sorted(agg["hs6"].unique())
    blocs = ["EU27", "China", "India", "Turkiye", "Kazakhstan"]
    grid = pd.MultiIndex.from_product(
        [YEARS, hs6s, blocs],
        names=["year", "hs6", "bloc"]
    ).to_frame(index=False)
    grid["hs4"] = grid["hs6"].astype(str).str[:4]

    out = grid.merge(
        agg[["year", "hs6", "bloc", "value_kUSD"]],
        on=["year", "hs6", "bloc"],
        how="left"
    )
    out["value_kUSD"] = out["value_kUSD"].fillna(0.0)

    out["post"] = out["year"].isin(POST).astype(int)
    for b, var in [
        ("China", "china_post"),
        ("India", "india_post"),
        ("Turkiye", "turkiye_post"),
        ("Kazakhstan", "kazakhstan_post"),
    ]:
        out[var] = (out["bloc"].eq(b).astype(int) * out["post"])

    out["pair_id"] = out["hs6"].astype(str) + "__" + out["bloc"].astype(str)
    out["side"] = side
    return out

def fit_ppml_hdfe(detail, side):
    d = build_bloc_hs6_panel(detail, side)
    m = d[d["year"].ne(ADJUSTMENT_YEAR)].copy()

    formula = (
        "value_kUSD ~ china_post + india_post + turkiye_post + kazakhstan_post "
        "| pair_id + year"
    )
    model = pf.fepois(
        formula,
        data=m,
        vcov={"CRV1": "hs4"}
    )

    tidy = model.tidy().reset_index()
    # Normalize varying pyfixest tidy column names across versions.
    rename = {
        "Coefficient": "term",
        "Estimate": "estimate",
        "Std. Error": "std_error",
        "Pr(>|t|)": "p_value",
        "Pr(>|z|)": "p_value",
        "2.5%": "ci_low",
        "97.5%": "ci_high",
        "index": "term",
    }
    tidy = tidy.rename(columns={k:v for k,v in rename.items() if k in tidy.columns})

    if "term" not in tidy.columns:
        tidy = tidy.rename(columns={tidy.columns[0]: "term"})
    # Common current pyfixest names
    for src, dst in [
        ("Estimate", "estimate"),
        ("Std. Error", "std_error"),
        ("Pr(>|t|)", "p_value"),
        ("Pr(>|z|)", "p_value"),
        ("estimate", "estimate"),
        ("std_error", "std_error"),
        ("p_value", "p_value"),
        ("conf_low", "ci_low"),
        ("conf_high", "ci_high"),
    ]:
        if src in tidy.columns and dst not in tidy.columns:
            tidy = tidy.rename(columns={src: dst})

    tidy["side"] = side
    tidy["exp_beta_minus_1_pct"] = np.where(
        "estimate" in tidy.columns,
        100 * (np.exp(pd.to_numeric(tidy["estimate"], errors="coerce")) - 1),
        np.nan
    )
    return d, model, tidy

def save_model_text(obj, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(str(obj))

# ===== Notebook code cell 23 =====

panel_results = {}
hausman_all = []
coef_all = []

for side, detail in [("Import", imp_detail), ("Export", exp_detail)]:
    p, fe, re_model, fe_tidy, re_tidy, hausman, meta = fit_partner_fe_re(detail, side)
    panel_results[side] = {
        "panel": p, "fe": fe, "re": re_model, "meta": meta
    }
    fe_tidy.to_csv(TAB / f"P1_{side.lower()}_partner_FE.csv", index=False)
    re_tidy.to_csv(TAB / f"P1_{side.lower()}_partner_RE.csv", index=False)
    p.to_csv(TAB / f"P1_{side.lower()}_balanced_partner_panel.csv", index=False)
    save_model_text(fe, OUT / f"P1_{side.lower()}_FE_summary.txt")
    save_model_text(re_model, OUT / f"P1_{side.lower()}_RE_summary.txt")

    coef_all += [fe_tidy, re_tidy]
    hausman_all.append(hausman)

coef_all = pd.concat(coef_all, ignore_index=True)
hausman_all = pd.concat(hausman_all, ignore_index=True)
coef_all.to_csv(TAB / "P1_FE_RE_all_coefficients.csv", index=False)
hausman_all.to_csv(TAB / "P2_Hausman_FE_vs_RE.csv", index=False)

display(coef_all[coef_all["term"].str.contains("_post", na=False)])
display(hausman_all)

# ===== Notebook code cell 25 =====

event_outputs = []

for side, summary_df, outcomes in [
    ("Import", imp, ["china_share", "eu27_share"]),
    ("Export", exp, ["china_share", "eu27_share"]),
]:
    for outcome in outcomes:
        ev, res = hs6_event_profile(summary_df, outcome, side, base_year=2021)
        event_outputs.append(ev)
        partner_name = "China" if outcome.startswith("china") else "EU27"
        fn = f"P3_{side.lower()}_{partner_name.lower()}_event_profile.csv"
        ev.to_csv(TAB / fn, index=False)
        save_model_text(res, OUT / fn.replace(".csv", "_summary.txt"))
        plot_event_profile(
            ev,
            f"{side}: {partner_name} HS6 share — product FE event profile",
            f"Figure_P3_{side}_{partner_name}_EventProfile.png"
        )

event_all = pd.concat(event_outputs, ignore_index=True)
event_all.to_csv(TAB / "P3_HS6_event_profiles_all.csv", index=False)

display(event_all)

# ===== Notebook code cell 27 =====

ppml_outputs = []
ppml_models = {}

for side, detail in [("Import", imp_detail), ("Export", exp_detail)]:
    ppml_panel, model, tidy = fit_ppml_hdfe(detail, side)
    ppml_models[side] = model
    ppml_outputs.append(tidy)
    ppml_panel.to_parquet(TAB / f"P4_{side.lower()}_HS6_bloc_panel.parquet", index=False)
    tidy.to_csv(TAB / f"P4_{side.lower()}_PPML_HDFE.csv", index=False)
    save_model_text(model, OUT / f"P4_{side.lower()}_PPML_HDFE_summary.txt")
    print(f"\\n--- {side} PPML-HDFE ---")
    display(tidy)

ppml_all = pd.concat(ppml_outputs, ignore_index=True)
ppml_all.to_csv(TAB / "P4_PPML_HDFE_all.csv", index=False)

# ===== Notebook code cell 29 =====

# Compact audit / summary
summary_rows = []

for side in ["Import", "Export"]:
    # FE interaction estimates
    f = coef_all[(coef_all["side"] == side) & (coef_all["model"] == "Two-way FE")]
    for term in ["china_post","india_post","turkiye_post","kazakhstan_post","eu27_post"]:
        z = f[f["term"] == term]
        if len(z):
            summary_rows.append({
                "analysis": "Partner-year FE",
                "side": side,
                "term": term,
                "estimate": float(z["estimate"].iloc[0]),
                "p_value": float(z["p_value"].iloc[0]),
                "interpretation": "Change in balanced-partner trade share after 2022, conditional on partner FE and year controls."
            })

# PPML
if "ppml_all" in globals():
    for _, r in ppml_all.iterrows():
        term = str(r.get("term", ""))
        if term in ["china_post","india_post","turkiye_post","kazakhstan_post"]:
            summary_rows.append({
                "analysis": "HS6-bloc PPML-HDFE",
                "side": r.get("side", ""),
                "term": term,
                "estimate": pd.to_numeric(r.get("estimate", np.nan), errors="coerce"),
                "p_value": pd.to_numeric(r.get("p_value", np.nan), errors="coerce"),
                "interpretation": "Relative post-2022 multiplicative shift versus EU27, controlling HS6×bloc FE and year FE."
            })

panel_summary = pd.DataFrame(summary_rows)
panel_summary.to_csv(TAB / "PANEL_ROBUSTNESS_SUMMARY.csv", index=False)

# Methodological notes for manuscript use
notes = """# Panel robustness interpretation

1. Partner-year FE/RE is a robustness comparison, not causal identification.
2. China is one country; cluster-robust significance for China×Post should not be treated as a many-treated-cluster design.
3. HS6 event profiles are within-product longitudinal trajectories relative to 2021, not causal event-study estimates.
4. PPML-HDFE includes zero trade and absorbs HS6×bloc time-invariant heterogeneity plus common year shocks.
5. 2022 is excluded from pre/post FE and PPML as the adjustment year, consistent with the manuscript.
6. A statistically weaker or null panel result must be reported rather than deleted; it may indicate that aggregate reconcentration is concentrated in value rather than breadth.
"""
(OUT / "PANEL_METHOD_NOTES.md").write_text(notes, encoding="utf-8")

# Excel workbook
xlsx = OUT / "Russia_Trade_Panel_Robustness_Results.xlsx"
with pd.ExcelWriter(xlsx, engine="openpyxl") as w:
    coef_all.to_excel(w, sheet_name="P1_FE_RE", index=False)
    hausman_all.to_excel(w, sheet_name="P2_Hausman", index=False)
    event_all.to_excel(w, sheet_name="P3_EventProfiles", index=False)
    if "ppml_all" in globals():
        ppml_all.to_excel(w, sheet_name="P4_PPML", index=False)
    panel_summary.to_excel(w, sheet_name="Panel_Summary", index=False)

# metadata
metadata = {
    "source": "CEPII BACI HS2012 V202601",
    "years": YEARS,
    "pre": PRE,
    "adjustment_year": ADJUSTMENT_YEAR,
    "post": POST,
    "analyses": [
        "Partner-year FE",
        "Partner-year RE",
        "Hausman FE-vs-RE",
        "HS6 product-FE event profile",
        "HS6×partner-bloc PPML-HDFE"
    ],
    "causal_claim": False,
}
(OUT / "panel_analysis_metadata.json").write_text(
    json.dumps(metadata, indent=2, ensure_ascii=False),
    encoding="utf-8"
)


print("Panel result workbook created:", xlsx)
print("Panel tables and event-profile figures created.")

# ===== Notebook code cell 31 =====

# ---------- Publication-ready tables and figures ----------
PUB = OUT / "publication"
PUB_TAB = PUB / "tables"
PUB_FIG = PUB / "figures"
for p in [PUB, PUB_TAB, PUB_FIG]:
    p.mkdir(parents=True, exist_ok=True)

def _savefig(name):
    plt.tight_layout()
    plt.savefig(PUB_FIG / name, dpi=300, bbox_inches="tight")
    plt.close()

def coefficient_plot(df, terms, title, filename, xscale=100.0, xlabel="Effect (percentage points)"):
    d = df[df["term"].isin(terms)].copy()
    if d.empty:
        return
    d["label"] = d["term"].map({
        "china_post":"China × Post",
        "india_post":"India × Post",
        "turkiye_post":"Türkiye × Post",
        "kazakhstan_post":"Kazakhstan × Post",
        "eu27_post":"EU27 × Post",
    }).fillna(d["term"])
    d["est_plot"] = pd.to_numeric(d["estimate"], errors="coerce") * xscale
    d["lo_plot"] = pd.to_numeric(d["ci_low"], errors="coerce") * xscale
    d["hi_plot"] = pd.to_numeric(d["ci_high"], errors="coerce") * xscale
    d = d.dropna(subset=["est_plot"]).sort_values("est_plot")
    y = np.arange(len(d))
    plt.figure(figsize=(8.5, 5.2))
    plt.errorbar(
        d["est_plot"], y,
        xerr=[d["est_plot"]-d["lo_plot"], d["hi_plot"]-d["est_plot"]],
        fmt="o", capsize=4
    )
    plt.axvline(0, linewidth=1)
    plt.yticks(y, d["label"])
    plt.xlabel(xlabel)
    plt.title(title)
    _savefig(filename)

def fe_re_compare_plot(df, side, filename):
    terms = ["china_post","india_post","turkiye_post","kazakhstan_post","eu27_post"]
    d = df[(df["side"] == side) & (df["term"].isin(terms))].copy()
    if d.empty:
        return
    d["label"] = d["term"].map({
        "china_post":"China × Post",
        "india_post":"India × Post",
        "turkiye_post":"Türkiye × Post",
        "kazakhstan_post":"Kazakhstan × Post",
        "eu27_post":"EU27 × Post",
    })
    models = ["Two-way FE","Random Effects"]
    labels = [x for x in ["China × Post","India × Post","Türkiye × Post","Kazakhstan × Post","EU27 × Post"]
              if x in set(d["label"])]
    x = np.arange(len(labels))
    width = 0.36
    plt.figure(figsize=(9.5,5.5))
    for j, model in enumerate(models):
        tmp = d[d["model"] == model].set_index("label").reindex(labels)
        vals = pd.to_numeric(tmp["estimate"], errors="coerce").to_numpy() * 100
        plt.bar(x + (j-0.5)*width, vals, width=width, label=model)
    plt.axhline(0, linewidth=1)
    plt.xticks(x, labels, rotation=20, ha="right")
    plt.ylabel("Coefficient (percentage points)")
    plt.title(f"{side}: FE vs RE post-2022 interaction estimates")
    plt.legend()
    _savefig(filename)

def ppml_plot(df, side, filename):
    terms = ["china_post","india_post","turkiye_post","kazakhstan_post"]
    d = df[(df["side"] == side) & (df["term"].isin(terms))].copy()
    if d.empty:
        return
    d["label"] = d["term"].map({
        "china_post":"China × Post",
        "india_post":"India × Post",
        "turkiye_post":"Türkiye × Post",
        "kazakhstan_post":"Kazakhstan × Post",
    })
    if "exp_beta_minus_1_pct" not in d.columns:
        d["exp_beta_minus_1_pct"] = 100*(np.exp(pd.to_numeric(d["estimate"], errors="coerce"))-1)
    d = d.dropna(subset=["exp_beta_minus_1_pct"]).sort_values("exp_beta_minus_1_pct")
    y = np.arange(len(d))
    plt.figure(figsize=(8.5,5.0))
    plt.barh(y, d["exp_beta_minus_1_pct"])
    plt.axvline(0, linewidth=1)
    plt.yticks(y, d["label"])
    plt.xlabel("Relative post-2022 change vs EU27 (%)")
    plt.title(f"{side}: HS6×bloc PPML-HDFE")
    _savefig(filename)

def prepost_partner_plot(panel_df, side, filename):
    d = panel_df.copy()
    d = d[d["year"].ne(ADJUSTMENT_YEAR)]
    d["period"] = np.where(d["year"].isin(PRE), "Pre (2019–2021)",
                    np.where(d["year"].isin(POST), "Post (2023–2024)", "Other"))
    d = d[d["period"].isin(["Pre (2019–2021)", "Post (2023–2024)"])]
    groups = {
        "China": CHN,
        "India": IND,
        "Türkiye": TUR,
        "Kazakhstan": KAZ,
    }
    rows = []
    for name, code in groups.items():
        x = d[d["partner"].eq(code)].groupby("period")["share"].mean()
        rows.append({
            "partner": name,
            "Pre": 100*x.get("Pre (2019–2021)", np.nan),
            "Post": 100*x.get("Post (2023–2024)", np.nan)
        })
    # EU27 aggregated share
    eu = d[d["partner"].isin(EU27)].groupby(["year","period"])["share"].sum().reset_index()
    eu2 = eu.groupby("period")["share"].mean()
    rows.append({
        "partner":"EU27",
        "Pre":100*eu2.get("Pre (2019–2021)", np.nan),
        "Post":100*eu2.get("Post (2023–2024)", np.nan)
    })
    z = pd.DataFrame(rows)
    x = np.arange(len(z))
    w = .36
    plt.figure(figsize=(9,5.4))
    plt.bar(x-w/2, z["Pre"], width=w, label="Pre")
    plt.bar(x+w/2, z["Post"], width=w, label="Post")
    plt.xticks(x, z["partner"], rotation=15)
    plt.ylabel("Balanced-partner trade share (%)")
    plt.title(f"{side}: balanced-partner pre/post shares")
    plt.legend()
    _savefig(filename)
    z.to_csv(PUB_TAB / f"Table_{side}_Balanced_PrePost.csv", index=False)

# 1-2. FE coefficient plots
for side in ["Import","Export"]:
    f = coef_all[(coef_all["side"]==side) & (coef_all["model"]=="Two-way FE")]
    coefficient_plot(
        f,
        ["china_post","india_post","turkiye_post","kazakhstan_post","eu27_post"],
        f"{side}: two-way FE post-2022 interactions",
        f"Figure_FE_{side}.png"
    )

# 3-4. FE vs RE comparison
for side in ["Import","Export"]:
    fe_re_compare_plot(coef_all, side, f"Figure_FE_RE_Comparison_{side}.png")

# 5-8. Event-profile plots are already created earlier; copy to publication folder
for p in FIG.glob("Figure_P3_*_EventProfile.png"):
    shutil.copy2(p, PUB_FIG / p.name)

# 9-10. PPML-HDFE plots
if "ppml_all" in globals():
    for side in ["Import","Export"]:
        ppml_plot(ppml_all, side, f"Figure_PPML_HDFE_{side}.png")

# 11-12. Balanced pre/post comparison
for side in ["Import","Export"]:
    prepost_partner_plot(
        panel_results[side]["panel"],
        side,
        f"Figure_Balanced_PrePost_{side}.png"
    )

# Publication-ready compact tables
core_terms = ["china_post","india_post","turkiye_post","kazakhstan_post","eu27_post"]
fe_pub = coef_all[(coef_all["model"]=="Two-way FE") & coef_all["term"].isin(core_terms)].copy()
re_pub = coef_all[(coef_all["model"]=="Random Effects") & coef_all["term"].isin(core_terms)].copy()

cols = ["side","term","estimate","std_error","p_value","ci_low","ci_high","nobs"]
fe_pub[cols].to_csv(PUB_TAB / "Table_FE_Core.csv", index=False)
re_pub[cols].to_csv(PUB_TAB / "Table_RE_Core.csv", index=False)
hausman_all.to_csv(PUB_TAB / "Table_Hausman.csv", index=False)
event_all.to_csv(PUB_TAB / "Table_EventProfiles.csv", index=False)
if "ppml_all" in globals():
    ppml_all.to_csv(PUB_TAB / "Table_PPML_HDFE.csv", index=False)
panel_summary.to_csv(PUB_TAB / "Table_Panel_Robustness_Summary.csv", index=False)

# One publication workbook
pub_xlsx = PUB / "Russia_Trade_Panel_Publication_Tables.xlsx"
with pd.ExcelWriter(pub_xlsx, engine="openpyxl") as w:
    fe_pub[cols].to_excel(w, sheet_name="FE_Core", index=False)
    re_pub[cols].to_excel(w, sheet_name="RE_Core", index=False)
    hausman_all.to_excel(w, sheet_name="Hausman", index=False)
    event_all.to_excel(w, sheet_name="EventProfiles", index=False)
    if "ppml_all" in globals():
        ppml_all.to_excel(w, sheet_name="PPML_HDFE", index=False)
    panel_summary.to_excel(w, sheet_name="Summary", index=False)

# Visual index
index_lines = [
    "# Publication figures",
    "",
    "The following files are automatically generated:",
    "",
]
for p in sorted(PUB_FIG.glob("*.png")):
    index_lines.append(f"- `{p.name}`")
(PUB / "FIGURE_INDEX.md").write_text("\n".join(index_lines), encoding="utf-8")

print("Publication tables:", len(list(PUB_TAB.glob("*"))))
print("Publication figures:", len(list(PUB_FIG.glob("*.png"))))
print("Publication workbook:", pub_xlsx)

# ===== Notebook code cell 33 =====
# Final full inventory and ZIP
# Convenience folders: collect every generated CSV and PNG in one place.
ALL_PUB = OUT / "publication"
ALL_TAB = ALL_PUB / "all_tables"
ALL_FIG = ALL_PUB / "all_figures"
ALL_TAB.mkdir(parents=True, exist_ok=True)
ALL_FIG.mkdir(parents=True, exist_ok=True)

# Copy instead of move: original analytic folder structure remains intact.
for p in sorted(TAB.glob("*.csv")):
    shutil.copy2(p, ALL_TAB / p.name)
for p in sorted(FIG.glob("*.png")):
    shutil.copy2(p, ALL_FIG / p.name)
# Add publication-specific panel files too.
for p in sorted((OUT / "publication" / "tables").glob("*.csv")):
    if p.parent != ALL_TAB:
        target = ALL_TAB / ("panel_" + p.name if (ALL_TAB / p.name).exists() else p.name)
        shutil.copy2(p, target)
for p in sorted((OUT / "publication" / "figures").glob("*.png")):
    if p.parent != ALL_FIG:
        target = ALL_FIG / ("panel_" + p.name if (ALL_FIG / p.name).exists() else p.name)
        shutil.copy2(p, target)

inventory = []
for p in sorted(OUT.rglob("*")):
    if p.is_file():
        inventory.append({
            "relative_path": str(p.relative_to(OUT)),
            "size_bytes": int(p.stat().st_size),
            "suffix": p.suffix.lower(),
        })
inv = pd.DataFrame(inventory)
inv.to_csv(OUT / "FULL_OUTPUT_INVENTORY.csv", index=False)

# Counts for quick audit
fig_count = len(list(OUT.rglob("*.png")))
csv_count = len(list(OUT.rglob("*.csv")))
xlsx_count = len(list(OUT.rglob("*.xlsx")))
print(f"PNG figures: {fig_count}")
print(f"CSV tables/results: {csv_count}")
print(f"Excel workbooks: {xlsx_count}")

full_meta = {
    "source": "CEPII BACI HS2012 V202601",
    "years": YEARS,
    "pre": PRE,
    "adjustment_year": ADJUSTMENT_YEAR,
    "post": POST,
    "structural_analysis": True,
    "panel_robustness": True,
    "panel_models": [
        "Partner-year two-way FE",
        "Random effects",
        "Hausman comparison",
        "HS6 product-FE event profile",
        "HS6×partner-bloc PPML-HDFE"
    ],
    "causal_claim": False,
    "output_counts": {"png": fig_count, "csv": csv_count, "xlsx": xlsx_count},
}
(OUT / "FULL_ANALYSIS_METADATA.json").write_text(
    json.dumps(full_meta, indent=2, ensure_ascii=False), encoding="utf-8"
)

zip_base = ROOT / "Russia_Trade_Full_AllInOne_Outputs"
zip_path = Path(str(zip_base) + ".zip")
if zip_path.exists():
    zip_path.unlink()
shutil.make_archive(str(zip_base), "zip", OUT)

print("\nFINAL OUTPUT ZIP:", zip_path)
print("All structural + panel tables and figures are included.")

try:
    from google.colab import files
    files.download(str(zip_path))
except Exception as e:
    print("Non-Colab environment. Output archive:", zip_path)
