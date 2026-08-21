#!/usr/bin/env python3
"""Relational scale-up of the workbook's portfolio tables to CSV.

Subprojects -> ~1,000,000 rows, with referentially matching Projects (parents),
Project_Materials (children of subprojects), and Material_Demand — same schema and
derived-field formulas as Synthetic_Material_Forecast_Cost_Benefit_Dataset.xlsx.
Formulas verified against the workbook's own sample rows:

  Projects:  Total_Annual_Benefit = avoided + productivity + risk_reduction
             NPV_Benefits         = Total_Annual_Benefit * annuity(Benefit_Life, 8%)
             Net_Benefit          = NPV_Benefits - Forecast_Cost
             Benefit_Cost_Ratio   = NPV_Benefits / Forecast_Cost
             ROI_%                = Net_Benefit / Forecast_Cost
  Subprojects: Benefit_Cost_Ratio = Expected_Annual_Benefit * 5 / Forecast_Cost   (undiscounted, benefit life 5)
               Remaining_Cost     = max(0, Forecast_Cost - Actual_Cost)
  Project_Materials: Forecast_Material_Cost = Estimated_Qty * Forecast_Unit_Cost
  Material_Demand:   Forecast_Need = round((Historical+Open) * Seasonality * Trend * scenario)
                     Safety = round(Forecast_Need*0.20); Total = Need+Safety
                     Shortage = max(0, Total-Available); Shortage_Cost = Shortage*Current_Unit_Cost

100% synthetic. No real Dominion Energy data.
"""
import numpy as np, pandas as pd, os, gzip

SEED = 7
rng = np.random.default_rng(SEED)
OUT = os.path.dirname(os.path.abspath(__file__))
TODAY = np.datetime64("2026-08-21")
DISCOUNT = 0.08
def annuity(life, r=DISCOUNT): return (1-(1+r)**-life)/r
ANNUITY = {3: annuity(3), 5: annuity(5), 7: annuity(7)}

REGIONS   = np.array(["North", "South", "East", "West"])
PROGRAMS  = np.array(["Asset Renewal", "Resilience", "Capacity Expansion", "Grid Modernization"])
PRIORITY  = np.array(["Critical", "High", "Medium", "Low"])
STATUS    = np.array(["Planning", "Design", "Procurement", "Construction", "Complete"])
WORKTYPE  = np.array(["Site Preparation", "Design", "Equipment Installation",
                      "Controls & Commissioning", "Closeout"])

# 12-material catalog from the workbook's Materials tab (exact values):
# id, name, category, uom, std_cost, current_cost, lead_days, criticality, base_monthly_usage
MATERIALS = [
    ("MAT-1001","Composite Utility Pole","Structures","Each",1450,2100,45,"High",230),
    ("MAT-1002","Crossarm Assembly","Structures","Each",275,420,30,"Low",90),
    ("MAT-1003","15 kV Cable","Conductor","Foot",8.5,12,60,"Low",9000),
    ("MAT-1004","35 kV Cable","Conductor","Foot",18,27,75,"Low",8200),
    ("MAT-1005","Pad-Mount Transformer 500 kVA","Transformers","Each",18500,26000,120,"Critical",150),
    ("MAT-1006","Pole-Mount Transformer 50 kVA","Transformers","Each",4200,6200,90,"Low",220),
    ("MAT-1007","Recloser Control Package","Protection","Each",9800,14500,105,"High",270),
    ("MAT-1008","Switchgear Cabinet","Protection","Each",12500,19000,135,"High",330),
    ("MAT-1009","Smart Meter","Metering","Each",95,145,40,"High",190),
    ("MAT-1010","Communication Gateway","Communications","Each",650,980,55,"Low",175),
    ("MAT-1011","Grounding Kit","Accessories","Kit",85,130,21,"Critical",220),
    ("MAT-1012","Connector Set","Accessories","Kit",42,68,18,"High",240),
]
mats = pd.DataFrame(MATERIALS, columns=["Material_ID","Material_Name","Category","UOM",
    "Standard_Unit_Cost_$","Current_Unit_Cost_$","Lead_Time_Days","Criticality","base_usage"])

def mstr(m64):  # datetime64[M] -> 'YYYY-MM-01'
    return np.datetime_as_string(m64.astype("datetime64[D]"))

# ==========================================================================
# PROJECTS  (parents; trimmed so child subprojects total exactly 1,000,000)
# ==========================================================================
TARGET_SUB = 1_000_000
N0 = 215_000
subcount0 = rng.integers(2, 9, N0)                 # 2..8 subprojects per project
cs = np.cumsum(subcount0)
cut = int(np.searchsorted(cs, TARGET_SUB))          # last project needed
subcount = subcount0[:cut+1].copy()
subcount[cut] -= (cs[cut] - TARGET_SUB)             # trim last project to hit exactly 1,000,000
subcount = subcount[subcount > 0]
NP = len(subcount)
assert subcount.sum() == TARGET_SUB
print("projects:", NP, "| subprojects:", int(subcount.sum()))

pid_num = np.arange(1, NP+1)
Project_ID = np.array(["PRJ-%06d" % i for i in pid_num])
p_prog = PROGRAMS[rng.integers(0, 4, NP)]
p_reg  = REGIONS[rng.integers(0, 4, NP)]
p_pri  = PRIORITY[rng.choice(4, NP, p=[.18,.27,.32,.23])]
p_stat = STATUS[rng.choice(5, NP, p=[.22,.24,.22,.20,.12])]
p_start = np.datetime64("2025-01") + rng.integers(0, 34, NP).astype("timedelta64[M]")
p_end   = p_start + rng.integers(8, 31, NP).astype("timedelta64[M]")
baseline = (rng.integers(16, 192, NP) * 25_000).astype(np.int64)       # 400K..4.775M
forecast = np.round(baseline * (1 + rng.normal(0.03, 0.13, NP))).astype(np.int64)
forecast = np.maximum(forecast, 50_000)
actual   = np.round(forecast * rng.uniform(0.05, 0.98, NP)).astype(np.int64)
avoided  = (rng.integers(6, 125, NP) * 5_000).astype(np.int64)         # 30K..620K
prod_ben = (rng.integers(3, 59, NP) * 5_000).astype(np.int64)          # 15K..290K
risk_red = (rng.integers(4, 70, NP) * 5_000).astype(np.int64)          # 20K..345K
life     = np.array([3,5,7])[rng.integers(0, 3, NP)]
tab      = avoided + prod_ben + risk_red
ann_fac  = np.array([ANNUITY[int(l)] for l in life])
npv      = tab * ann_fac
cost_var = forecast - baseline
net_ben  = npv - forecast
bcr      = npv / forecast
roi      = net_ben / forecast
past_end = (p_end < TODAY) & (p_stat != "Complete")
cost_press = (cost_var / baseline) > 0.10
flag = np.where(past_end, "Past Planned End", np.where(cost_press, "Cost Pressure", "On Track"))

projects = pd.DataFrame({
    "Project_ID": Project_ID,
    "Project_Name": [f"{r} {pg} Project {i}" for r,pg,i in zip(p_reg,p_prog,pid_num)],
    "Program_Type": p_prog, "Region": p_reg, "Priority": p_pri, "Status": p_stat,
    "Planned_Start": mstr(p_start), "Planned_End": mstr(p_end),
    "Baseline_Cost_$": baseline, "Forecast_Cost_$": forecast, "Actual_Cost_To_Date_$": actual,
    "Annual_Avoided_Cost_$": avoided, "Annual_Productivity_Benefit_$": prod_ben,
    "Annual_Risk_Reduction_$": risk_red, "Benefit_Life_Yrs": life, "Discount_Rate": DISCOUNT,
    "Total_Annual_Benefit_$": tab, "Cost_Variance_$": cost_var,
    "NPV_Benefits_$": np.round(npv,2), "Net_Benefit_$": np.round(net_ben,2),
    "Benefit_Cost_Ratio": np.round(bcr,6), "ROI_%": np.round(roi,6), "Schedule_Risk_Flag": flag,
})

# ==========================================================================
# SUBPROJECTS  (~1,000,000; children of projects)
# ==========================================================================
N = TARGET_SUB
pidx = np.repeat(np.arange(NP), subcount)                         # parent index per subproject
start_of_group = np.repeat(np.cumsum(subcount) - subcount, subcount)
sp_seq = np.arange(N) - start_of_group + 1                        # 1..count within project
sub_pid = Project_ID[pidx]
Subproject_ID = np.char.add(np.char.add(sub_pid, "-SP"),
                            np.char.zfill((sp_seq).astype(str), 2))
s_wt   = WORKTYPE[rng.integers(0, 5, N)]
s_reg  = REGIONS[rng.integers(0, 4, N)]
s_stat = STATUS[rng.integers(0, 5, N)]
s_start= (p_start[pidx] + rng.integers(0, 6, N).astype("timedelta64[M]"))
s_end  = s_start + rng.integers(3, 21, N).astype("timedelta64[M]")
budget = (rng.integers(8, 90, N) * 10_000).astype(np.int64)          # 80K..890K
s_fc   = np.round(budget * (1 + rng.normal(0.05, 0.18, N))).astype(np.int64)
s_fc   = np.maximum(s_fc, 20_000)
compl  = np.round(rng.uniform(0.11, 0.98, N), 2)
s_act  = np.round(s_fc * compl * rng.uniform(0.85, 1.05, N)).astype(np.int64)
s_act  = np.minimum(s_act, s_fc)
exp_ben= (rng.integers(1, 33, N) * 5_000).astype(np.int64)           # 5K..160K
dep    = rng.integers(0, 5, N)
risk   = rng.integers(1, 6, N)
s_cv   = s_fc - budget
s_rem  = np.maximum(0, s_fc - s_act)
s_bcr  = np.round(exp_ben * 5 / s_fc, 6)

subprojects = pd.DataFrame({
    "Subproject_ID": Subproject_ID, "Project_ID": sub_pid,
    "Subproject_Name": np.char.add(s_wt.astype(object).astype(str),
                                   np.char.add(" Package ", sp_seq.astype(str))),
    "Work_Type": s_wt, "Region": s_reg, "Status": s_stat,
    "Planned_Start": mstr(s_start), "Planned_End": mstr(s_end),
    "Budget_$": budget, "Forecast_Cost_$": s_fc, "Actual_Cost_$": s_act,
    "Expected_Annual_Benefit_$": exp_ben, "Completion_%": compl,
    "Dependency_Count": dep, "Risk_Score_1_5": risk,
    "Cost_Variance_$": s_cv, "Remaining_Cost_$": s_rem, "Benefit_Cost_Ratio": s_bcr,
})

# ==========================================================================
# PROJECT_MATERIALS  (1 per subproject -> ~1,000,000, full referential coverage)
# ==========================================================================
midx = rng.integers(0, 12, N)
uom  = mats["UOM"].values[midx]
unit = mats["Current_Unit_Cost_$"].values[midx].astype(float)
lead = mats["Lead_Time_Days"].values[midx].astype(int)
is_foot = uom == "Foot"
est = np.where(is_foot, rng.integers(500, 10001, N), rng.integers(2, 81, N)).astype(np.int64)
res = np.round(est * rng.uniform(0.0, 1.0, N)).astype(np.int64)
iss = np.round(res * rng.uniform(0.0, 1.0, N)).astype(np.int64)
req = np.datetime64("2026-01") + rng.integers(0, 37, N).astype("timedelta64[M]")
fmc = (est * unit).astype(np.int64)
avail_status = np.where(res == 0, "Not Reserved",
                np.where(iss >= est, "Fulfilled", "Partial"))
months_to_req = (req.astype("datetime64[D]") - TODAY.astype("datetime64[D]")).astype(int)
lead_risk = np.where(months_to_req < lead, "At Risk", "Within Lead Time")
reqM = pd.to_datetime(mstr(req))
nbq = "Q" + reqM.quarter.astype(str) + " " + reqM.year.astype(str)

project_materials = pd.DataFrame({
    "Subproject_ID": Subproject_ID, "Project_ID": sub_pid,
    "Material_ID": mats["Material_ID"].values[midx], "Required_Date": mstr(req),
    "Estimated_Qty": est, "Reserved_Qty": res, "Issued_Qty": iss,
    "Forecast_Unit_Cost_$": unit.astype(np.int64) if np.all(unit==unit.astype(int)) else unit,
    "Forecast_Material_Cost_$": fmc,
    "Availability_Status": avail_status, "Lead_Time_Risk": lead_risk, "Need_By_Quarter": nbq.values,
})

# ==========================================================================
# MATERIAL_DEMAND  (matching: 12 materials x 4 regions x 60 months x 3 scenarios)
# ==========================================================================
MONTHS = pd.date_range("2022-01-01", periods=60, freq="MS")
SCEN = {"Base":1.00, "Low":0.85, "High":1.18}
REGION_MULT = {"North":0.95,"South":0.90,"East":1.15,"West":1.00}
mo = MONTHS.month.values
season_by_m = np.round(1.0 + 0.15*np.sin(2*np.pi*(mo-3)/12), 2)
grid = [(mi, r, k) for mi in range(12) for r in range(4) for k in range(60)]
gmi = np.array([g[0] for g in grid]); grg = np.array([g[1] for g in grid]); gk = np.array([g[2] for g in grid])
base_usage = mats["base_usage"].values[gmi] * np.array([REGION_MULT[x] for x in REGIONS])[grg]
season = season_by_m[gk]; trend = np.power(1.010, gk)
Gn = len(grid)
hist = np.maximum(0, np.round(base_usage*season*rng.uniform(0.80,1.20,Gn))).astype(np.int64)
openq= np.round(hist*rng.uniform(0.05,0.45,Gn)).astype(np.int64)
fc_base = np.round((hist+openq)*season*trend).astype(np.int64)
tot_base= fc_base + np.round(fc_base*0.20).astype(np.int64)
avail = np.maximum(0, np.round(tot_base*rng.uniform(0.85,1.45,Gn))).astype(np.int64)
rows=[]
cur = mats["Current_Unit_Cost_$"].values
for sname, smul in SCEN.items():
    fc = np.round((hist+openq)*season*trend*smul).astype(np.int64)
    sf = np.round(fc*0.20).astype(np.int64); tr = fc+sf
    sh = np.maximum(0, tr-avail); sc = sh*cur[gmi]
    rows.append(pd.DataFrame({
        "Demand_Month": np.datetime_as_string(MONTHS.values[gk],"D"),
        "Region": REGIONS[grg], "Material_ID": mats["Material_ID"].values[gmi],
        "Material_Name": mats["Material_Name"].values[gmi],
        "Historical_Usage_Qty": hist, "Open_Project_Demand_Qty": openq,
        "Seasonality_Index": season, "Trend_Index": np.round(trend,3),
        "Forecast_Need_Qty": fc, "Safety_Stock_Qty": sf, "Total_Required_Qty": tr,
        "Available_Qty": avail, "Projected_Shortage_Qty": sh,
        "Projected_Shortage_Cost_$": sc, "Forecast_Scenario": sname}))
material_demand = pd.concat(rows, ignore_index=True)

# ==========================================================================
# write CSVs (+ gzip + samples)
# ==========================================================================
def dump(df, name, sample=None):
    p = os.path.join(OUT, name+".csv")
    df.to_csv(p, index=False)
    with gzip.open(p+".gz","wt",newline="") as f: df.to_csv(f, index=False)
    if sample: df.head(sample).to_csv(os.path.join(OUT, name+"_sample.csv"), index=False)
    print(f"  {name}.csv: {len(df):>9,} rows, {os.path.getsize(p)/1e6:5.1f} MB (+ .csv.gz)")

mats.drop(columns=["base_usage"]).to_csv(os.path.join(OUT,"Materials.csv"), index=False)
print("wrote CSVs:")
dump(projects, "Projects")
dump(subprojects, "Subprojects", sample=10000)
dump(project_materials, "Project_Materials", sample=10000)
dump(material_demand, "Material_Demand")

# ==========================================================================
# validation
# ==========================================================================
print("\n=== validation ===")
print("rows -> Projects:", f"{len(projects):,}", "| Subprojects:", f"{len(subprojects):,}",
      "| Project_Materials:", f"{len(project_materials):,}", "| Material_Demand:", f"{len(material_demand):,}")
print("referential — every Subproject.Project_ID in Projects:",
      subprojects["Project_ID"].isin(set(projects["Project_ID"])).all())
print("referential — every PM.Subproject_ID in Subprojects:",
      project_materials["Subproject_ID"].isin(set(subprojects["Subproject_ID"])).all())
print("referential — every PM.Material_ID in Materials:",
      project_materials["Material_ID"].isin(set(mats["Material_ID"])).all())
print("referential — every Material_Demand.Material_ID in Materials:",
      material_demand["Material_ID"].isin(set(mats["Material_ID"])).all())
print("unique Subproject_ID:", subprojects["Subproject_ID"].is_unique, "| unique Project_ID:", projects["Project_ID"].is_unique)
# formula checks
pj=projects
print("Projects NPV==TAB*annuity:", bool(np.allclose(pj["NPV_Benefits_$"],
      pj["Total_Annual_Benefit_$"]*[ANNUITY[int(l)] for l in pj["Benefit_Life_Yrs"]], atol=0.5)))
print("Projects Net==NPV-Forecast:", bool(np.allclose(pj["Net_Benefit_$"], pj["NPV_Benefits_$"]-pj["Forecast_Cost_$"], atol=0.5)))
print("Subproj BCR==benefit*5/forecast:", bool(np.allclose(subprojects["Benefit_Cost_Ratio"],
      subprojects["Expected_Annual_Benefit_$"]*5/subprojects["Forecast_Cost_$"], atol=1e-4)))
print("PM cost==qty*unit:", bool((project_materials["Forecast_Material_Cost_$"]==
      (project_materials["Estimated_Qty"]*project_materials["Forecast_Unit_Cost_$"])).all()))
md=material_demand
print("MD shortage_cost==shortage*unit:", bool((md["Projected_Shortage_Cost_$"]==
      md["Projected_Shortage_Qty"]*mats.set_index("Material_ID").loc[md["Material_ID"],"Current_Unit_Cost_$"].values).all()))
