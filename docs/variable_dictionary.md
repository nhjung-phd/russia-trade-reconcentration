# Variable Dictionary

## BACI source variables

| Variable | Meaning |
|---|---|
| `i` | Exporter code |
| `j` | Importer code |
| `k` | HS6 product code |
| `v` | Trade value, thousand USD |
| `q` | Quantity, metric tons |

## Derived variables

| Variable | Meaning |
|---|---|
| `world_import_kUSD` | Russia's total imports of an HS6 product |
| `china_import_kUSD` | Russia's imports of an HS6 product from China |
| `eu27_import_kUSD` | Russia's imports of an HS6 product from EU27 |
| `china_share` | China's share of Russia's HS6 imports or exports, depending on dataset |
| `eu27_share` | EU27 share of Russia's HS6 imports or exports |
| `india_share` | India's share |
| `turkiye_share` | Türkiye's share |
| `HHI` | Herfindahl–Hirschman concentration index across partners |
| `CR1` | Largest partner share |
| `CR3` | Sum of the three largest partner shares |
| `Entropy` | Shannon entropy of the partner-share distribution |
| `EffectiveN` | Inverse HHI, interpreted as effective number of partners |
| `Difference` | Bilateral trade exposure gap |
| `delta_*` | Post-period mean minus pre-period mean |
