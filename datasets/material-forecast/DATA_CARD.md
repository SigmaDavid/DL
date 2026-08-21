# Synthetic Material Forecast Dataset (~1M rows)

Generated from the guidelines in the attached workbook
`Synthetic_Material_Forecast_Cost_Benefit_Dataset.xlsx` — a dashboard-ready,
**100% synthetic** utility material-demand / project cost-benefit dataset. No real
Dominion Energy data, IDs, vendors, costs, locations, or operational records.

## Files

| file | rows | notes |
|---|---|---|
| `gen_material_demand.py` | — | reproducible generator (numpy/pandas, `seed=42`) |
| `material_demand_sample_10k.csv` | 10,000 | preview of the fact table |
| `dim_materials.csv` | 1,400 | expanded SKU dimension (12 archetypes × variants) |
| *(full)* `material_demand.parquet` | **1,008,000** | produced by the generator (~14 MB); not committed — run the script |
| *(full)* `material_demand.csv.gz` | 1,008,000 | gzipped CSV (~19 MB); produced by the generator |

Run `python3 gen_material_demand.py` to (re)produce the full ~1M-row Parquet +
gzipped CSV alongside the sample and dimension files.

## Grain & dimensions

`Material_Demand` fact, one row per **material (SKU) × region × month × forecast
scenario**:

- **1,400 SKUs** expanded from the workbook's 12 material archetypes (Composite
  Utility Pole, 15/35 kV Cable, transformers, recloser, switchgear, smart meter,
  etc.), inheriting Category / UOM / cost band / criticality with per-SKU jitter.
- **4 regions** (North, South, East, West).
- **60 months** (2022-01 … 2026-12).
- **3 forecast scenarios** (Base, Low ×0.85, High ×1.18).

1,400 × 4 × 60 × 3 = **1,008,000 rows**, 18 columns.

## Formulas (reproduced from the workbook)

```
Forecast_Need_Qty       = round((Historical_Usage + Open_Project_Demand)
                                 × Seasonality_Index × Trend_Index × scenario_mult)
Safety_Stock_Qty        = round(Forecast_Need_Qty × 0.20)      # Assumptions: safety stock 0.2
Total_Required_Qty      = Forecast_Need_Qty + Safety_Stock_Qty
Projected_Shortage_Qty  = max(0, Total_Required_Qty − Available_Qty)
Projected_Shortage_Cost_$ = Projected_Shortage_Qty × Current_Unit_Cost_$
```

Actuals (historical usage, open demand) and inventory (`Available_Qty`) are
computed once per (SKU, region, month) and held constant across scenarios — only
the forward-looking forecast and its downstream flex by scenario, so the
Base/Low/High comparison is apples-to-apples.

## Validation (all pass)

- Row count 1,008,000; distinct SKUs 1,400 · regions 4 · months 60 · scenarios 3.
- Every formula identity holds exactly (safety stock, total required, shortage,
  shortage cost).
- Shortage incidence: **Base 24.8% · Low 0.0% · High 54.8%** of rows — realistic
  and scenario-meaningful for inventory-risk / cost-benefit analysis.

All values are illustrative only — not for real purchasing, budgeting, or
operational decisions.
