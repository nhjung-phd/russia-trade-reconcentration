from pathlib import Path
import math
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TAB = ROOT / "results" / "tables"

def close(a, b, tol=1e-6):
    return math.isclose(float(a), float(b), rel_tol=0.0, abs_tol=tol)

checks = []

t23 = pd.read_csv(TAB / "T23_Manuscript_Key_Results_Summary.csv")
def get23(side, definition, measure, col):
    r = t23[(t23.side == side) & (t23.definition == definition) & (t23.measure == measure)].iloc[0]
    return r[col]

checks += [
    ("Import country HHI pre", get23("import", "country", "HHI", "pre"), 0.08271400151309377),
    ("Import country HHI post", get23("import", "country", "HHI", "post"), 0.2987416537970438),
    ("Import EU27 bloc HHI pre", get23("import", "EU27_bloc", "HHI", "pre"), 0.19499061369111073),
    ("Import EU27 bloc HHI post", get23("import", "EU27_bloc", "HHI", "post"), 0.32600262902091964),
    ("Export EU27 bloc HHI pre", get23("export", "EU27_bloc", "HHI", "pre"), 0.15729574099623767),
    ("Export EU27 bloc HHI post", get23("export", "EU27_bloc", "HHI", "post"), 0.16041742214354762),
]

t24 = pd.read_csv(TAB / "T24_FE_Robustness_Estimates.csv")
def fe(side, interaction):
    return t24[(t24.side == side) & (t24.interaction == interaction)].iloc[0]["coefficient_percentage_points"]

checks += [
    ("FE Import China x Post", fe("Import", "China × Post"), 28.152204144822417),
    ("FE Export China x Post", fe("Export", "China × Post"), 17.50285318741061),
    ("FE Export India x Post", fe("Export", "India × Post"), 15.353708321651352),
]

t19 = pd.read_csv(TAB / "T19_Bank_of_Russia_Denominator_Sensitivity_PrePost.csv").iloc[0]
checks.append(("BoR denominator change", t19["change_pp"], 14.13106868852401))

failed = []
for name, actual, expected in checks:
    ok = close(actual, expected)
    print(f"{'PASS' if ok else 'FAIL'}  {name}: {actual} (expected {expected})")
    if not ok:
        failed.append(name)

if failed:
    raise SystemExit(f"Verification failed: {failed}")

print("\nAll release-output checks passed.")
