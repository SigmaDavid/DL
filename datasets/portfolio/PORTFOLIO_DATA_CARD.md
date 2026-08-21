# Portfolio CSVs — Subprojects scaled to 1M, with matching tables

Relational scale-up of the workbook's portfolio tabs
(`Synthetic_Material_Forecast_Cost_Benefit_Dataset.xlsx`). Same schema and
derived-field formulas as the Excel; all four tables are referentially
consistent. **100% synthetic** — no real Dominion Energy data. Generator:
`gen_portfolio.py` (numpy/pandas, `seed=7`).

## Files (each `.csv` also provided gzipped as `.csv.gz`)

| file | rows | cols | grain |
|---|---|---|---|
| `Subprojects.csv` | **1,000,000** | 18 | one row / subproject |
| `Projects.csv` | 199,909 | 23 | one row / project (parents) |
| `Project_Materials.csv` | 1,000,000 | 12 | one row / subproject-material |
| `Material_Demand.csv` | 8,640 | 15 | one row / material-month-region-scenario |
| `Materials.csv` | 12 | 8 | shared material catalog (dimension) |
| `*_sample.csv` | 10,000 | — | plain-CSV previews of the two big tables |

`Subprojects` is capped at exactly 1,000,000 rows (2–8 subprojects per project,
so ~199,909 projects). `Project_Materials` is 1 material per subproject to keep
the file at the 1M cap with full coverage (the source averaged ~3; raise the
materials-per-subproject in the generator if you want more). `Material_Demand`
uses the 12-material catalog × 4 regions × 60 months × 3 scenarios (its natural
grain — well under 1M).

## Referential integrity (all verified True)

- every `Subprojects.Project_ID` exists in `Projects`
- every `Project_Materials.Subproject_ID` exists in `Subprojects`
- every `Project_Materials.Material_ID` / `Material_Demand.Material_ID` exists in `Materials`
- `Project_ID` and `Subproject_ID` are unique keys

## Derived-field formulas (verified against the workbook's own rows)

- **Projects:** `Total_Annual_Benefit = avoided + productivity + risk_reduction`;
  `NPV_Benefits = Total_Annual_Benefit × annuity(Benefit_Life, 8%)`;
  `Net_Benefit = NPV − Forecast_Cost`; `Benefit_Cost_Ratio = NPV / Forecast_Cost`;
  `ROI_% = Net_Benefit / Forecast_Cost`; `Schedule_Risk_Flag` = Past Planned End
  (end < today & not Complete) / Cost Pressure (cost variance > 10%) / On Track.
- **Subprojects:** `Cost_Variance = Forecast − Budget`;
  `Remaining_Cost = max(0, Forecast − Actual)`;
  `Benefit_Cost_Ratio = Expected_Annual_Benefit × 5 / Forecast_Cost` (undiscounted, benefit life 5).
- **Project_Materials:** `Forecast_Material_Cost = Estimated_Qty × Forecast_Unit_Cost`;
  `Availability_Status` from reserved/issued vs estimated; `Need_By_Quarter` from Required_Date.
- **Material_Demand:** `Forecast_Need = round((Historical+Open) × Seasonality × Trend × scenario)`;
  `Safety = round(Need×0.20)`; `Total = Need+Safety`;
  `Shortage = max(0, Total−Available)`; `Shortage_Cost = Shortage × Current_Unit_Cost`.

Illustrative only — not for real purchasing, budgeting, or project decisions.
