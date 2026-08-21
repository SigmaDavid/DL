#!/usr/bin/env python3
"""Synthetic Material Forecast dataset generator (~1M rows).

Reproduces the schema + formulas from the attached workbook
(Synthetic_Material_Forecast_Cost_Benefit_Dataset.xlsx):

  Forecast_Need   = round((Historical_Usage + Open_Project_Demand) * Seasonality * Trend * scenario_mult)
  Safety_Stock    = round(Forecast_Need * 0.20)          # Assumptions: Inventory Safety Stock 0.2
  Total_Required  = Forecast_Need + Safety_Stock
  Shortage        = max(0, Total_Required - Available)
  Shortage_Cost_$ = Shortage * Current_Unit_Cost         # verified against sample rows

Grain: material (SKU) x region x month x forecast scenario.
100% synthetic — no real Dominion Energy data, IDs, vendors, costs or records.
"""
import numpy as np, pandas as pd, gzip, os

SEED = 42
rng = np.random.default_rng(SEED)
OUT = os.path.dirname(os.path.abspath(__file__))

# --- dimensions -----------------------------------------------------------
REGIONS  = ["North", "South", "East", "West"]
REGION_MULT = {"North": 0.95, "South": 0.90, "East": 1.15, "West": 1.00}
SCENARIOS = {"Base": 1.00, "Low": 0.85, "High": 1.18}
N_SKU   = 1400                         # expanded from the 12 archetypes
MONTHS  = pd.date_range("2022-01-01", periods=60, freq="MS")   # 60 months
# 1400 x 4 x 60 x 3 = 1,008,000 rows

# 12 material archetypes from the workbook's Materials sheet:
# name, category, uom, current_unit_cost, base_monthly_usage, criticality
ARCH = [
    ("Composite Utility Pole",         "Structures",     "Each", 2100,   230, "High"),
    ("Crossarm Assembly",              "Structures",     "Each",  420,    90, "Low"),
    ("15 kV Cable",                    "Conductor",      "Foot",   12,  9000, "Low"),
    ("35 kV Cable",                    "Conductor",      "Foot",   27,  8200, "Low"),
    ("Pad-Mount Transformer 500 kVA",  "Transformers",   "Each", 26000,  150, "Critical"),
    ("Pole-Mount Transformer 50 kVA",  "Transformers",   "Each",  6200,  220, "Low"),
    ("Recloser Control Package",       "Protection",     "Each", 14500,  270, "High"),
    ("Switchgear Cabinet",             "Protection",     "Each", 19000,  330, "High"),
    ("Smart Meter",                    "Metering",       "Each",  145,   190, "High"),
    ("Communication Gateway",          "Communications", "Each",  980,   175, "Low"),
    ("Grounding Kit",                  "Accessories",    "Kit",   130,   220, "Critical"),
    ("Connector Set",                  "Accessories",    "Kit",    68,   240, "High"),
]
CRIT_LEVELS = ["Low", "Medium", "High", "Critical"]

# --- build the expanded SKU dimension -------------------------------------
sku_ids, sku_name, sku_cat, sku_uom, sku_cost, sku_base, sku_crit, sku_arch = ([] for _ in range(8))
for i in range(N_SKU):
    a = i % len(ARCH)                          # round-robin across archetypes
    name, cat, uom, cost, base, crit = ARCH[a]
    variant = i // len(ARCH) + 1
    sku_ids.append("MAT-%05d" % (1001 + i))
    sku_name.append("%s — Type %02d" % (name, variant))
    sku_cat.append(cat); sku_uom.append(uom); sku_arch.append(name)
    sku_cost.append(int(round(cost * rng.uniform(0.82, 1.28))))
    sku_base.append(base * rng.uniform(0.5, 1.7))
    # criticality mostly inherits the archetype, sometimes drifts one level
    ci = CRIT_LEVELS.index(crit if crit in CRIT_LEVELS else "Low")
    ci = int(np.clip(ci + rng.integers(-1, 2), 0, 3))
    sku_crit.append(CRIT_LEVELS[ci])

dim = pd.DataFrame({
    "Material_ID": sku_ids, "Material_Name": sku_name, "Material_Archetype": sku_arch,
    "Category": sku_cat, "UOM": sku_uom, "Current_Unit_Cost_$": sku_cost,
    "Criticality": sku_crit,
})
sku_cost = np.array(sku_cost); sku_base = np.array(sku_base)

# monthly seasonality (construction-season shaped) and per-month trend
mo = MONTHS.month.values
seasonality_by_month = np.round(1.0 + 0.15 * np.sin(2*np.pi*(mo-3)/12), 2)   # peak ~spring/summer
MONTH_TREND = 0.010                                                          # ~+1%/mo

# --- assemble the fact --------------------------------------------------
# Build the (SKU x region x month) grid first so that ACTUALS (historical usage,
# open demand) and INVENTORY (available) are computed once and stay identical
# across forecast scenarios — only the forward-looking Forecast_Need and its
# downstream (safety stock, total required, shortage, shortage cost) flex by
# scenario. Then tile the grid across the 3 scenarios.
n_r, n_m, n_s = len(REGIONS), len(MONTHS), len(SCENARIOS)
G = N_SKU * n_r * n_m                          # grid rows (scenario-independent)
print("grid rows:", G, "| target fact rows:", G * n_s)

g_sku   = np.repeat(np.arange(N_SKU), n_r * n_m)
g_region= np.tile(np.repeat(np.arange(n_r), n_m), N_SKU)
g_month = np.tile(np.arange(n_m), N_SKU * n_r)

region_arr = np.array(REGIONS)
scen_names = np.array(list(SCENARIOS.keys()))
scen_mult  = np.array(list(SCENARIOS.values()))
region_mult= np.array([REGION_MULT[r] for r in REGIONS])

g_base   = sku_base[g_sku] * region_mult[g_region]
g_season = seasonality_by_month[g_month]
g_trend  = np.power(1 + MONTH_TREND, g_month)

# actuals (scenario-independent)
g_hist = np.maximum(0, np.round(g_base * g_season * rng.uniform(0.80, 1.20, G))).astype(np.int64)
g_open = np.round(g_hist * rng.uniform(0.05, 0.45, G)).astype(np.int64)

# Base-scenario forecast drives the inventory position: available is set to cover
# the Base total-required with a coverage ratio centred just above 1.0, so ~25%
# of Base rows show a shortage (Low ~0%, High ~55%).
g_fc_base    = np.round((g_hist + g_open) * g_season * g_trend).astype(np.int64)
g_total_base = g_fc_base + np.round(g_fc_base * 0.20).astype(np.int64)
g_available  = np.maximum(0, np.round(g_total_base * rng.uniform(0.85, 1.45, G))).astype(np.int64)

# tile grid across scenarios
sku_ix   = np.tile(g_sku, n_s)
region_ix= np.tile(g_region, n_s)
month_ix = np.tile(g_month, n_s)
scen_ix  = np.repeat(np.arange(n_s), G)
season   = np.tile(g_season, n_s)
trend    = np.tile(g_trend, n_s)
hist     = np.tile(g_hist, n_s)
openq    = np.tile(g_open, n_s)
available= np.tile(g_available, n_s)

forecast = np.round((hist + openq) * season * trend * scen_mult[scen_ix]).astype(np.int64)
safety   = np.round(forecast * 0.20).astype(np.int64)
total_req= forecast + safety
shortage = np.maximum(0, total_req - available)
short_cost = shortage * sku_cost[sku_ix]

df = pd.DataFrame({
    "Demand_Month": MONTHS.values[month_ix],
    "Region": region_arr[region_ix],
    "Material_ID": dim["Material_ID"].values[sku_ix],
    "Material_Name": dim["Material_Name"].values[sku_ix],
    "Category": dim["Category"].values[sku_ix],
    "UOM": dim["UOM"].values[sku_ix],
    "Historical_Usage_Qty": hist,
    "Open_Project_Demand_Qty": openq,
    "Seasonality_Index": np.round(season, 2),
    "Trend_Index": np.round(trend, 3),
    "Forecast_Need_Qty": forecast,
    "Safety_Stock_Qty": safety,
    "Total_Required_Qty": total_req,
    "Available_Qty": available,
    "Projected_Shortage_Qty": shortage,
    "Projected_Shortage_Cost_$": short_cost,
    "Current_Unit_Cost_$": sku_cost[sku_ix],
    "Forecast_Scenario": scen_names[scen_ix],
})
print("rows:", len(df), "| cols:", len(df.columns))

# --- write outputs --------------------------------------------------------
dim.to_csv(os.path.join(OUT, "dim_materials.csv"), index=False)
df.to_parquet(os.path.join(OUT, "material_demand.parquet"), index=False, compression="snappy")
df.head(10000).to_csv(os.path.join(OUT, "material_demand_sample_10k.csv"), index=False)
with gzip.open(os.path.join(OUT, "material_demand.csv.gz"), "wt", newline="") as f:
    df.to_csv(f, index=False)

# --- validation ----------------------------------------------------------
base = df[df.Forecast_Scenario == "Base"]
print("\n=== validation ===")
print("distinct SKUs:", df.Material_ID.nunique(), "| regions:", df.Region.nunique(),
      "| months:", df.Demand_Month.nunique(), "| scenarios:", df.Forecast_Scenario.nunique())
chk = (df.Safety_Stock_Qty == np.round(df.Forecast_Need_Qty*0.2)).mean()
print("safety-stock formula holds:", round(chk,4))
print("total_required == need+safety:", (df.Total_Required_Qty==df.Forecast_Need_Qty+df.Safety_Stock_Qty).all())
print("shortage == max(0,req-avail):", (df.Projected_Shortage_Qty==np.maximum(0,df.Total_Required_Qty-df.Available_Qty)).all())
print("shortage_cost == shortage*cost:", (df["Projected_Shortage_Cost_$"]==df.Projected_Shortage_Qty*df["Current_Unit_Cost_$"]).all())
print("pct rows with a shortage:", round((df.Projected_Shortage_Qty>0).mean()*100,1),"%")
print("Base total forecast need:", f"{base.Forecast_Need_Qty.sum():,}")
print("Base total shortage cost $:", f"{base['Projected_Shortage_Cost_$'].sum():,}")
for fn in ["material_demand.parquet","material_demand.csv.gz","material_demand_sample_10k.csv","dim_materials.csv"]:
    p=os.path.join(OUT,fn); print(f"  {fn}: {os.path.getsize(p)/1e6:.1f} MB")
