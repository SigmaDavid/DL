import json,re,csv
cols=json.load(open("/tmp/dm_cols.json"))["entries"]
EL={"U_gDkztHu8":"RLS Table","wQoXfXvqgv":"Student"}
def src(f):
    m=re.match(r'\[([^/\]]+)/',f or ""); return m.group(1) if m else "(calculated)"
def dtype(c):
    t=c.get("type")
    return t.get("type") if isinstance(t,dict) else t

SUBJ={"Ela":"ELA","Mth":"Math","Sci":"Science","His":"History"}
def subj(tok): return SUBJ.get(tok, tok)

# curated descriptions keyed by exact label (highest priority)
OVER={
 "School Student Key":"Surrogate key uniquely identifying a student–school–snapshot record; the primary grain of the model and the key used for distinct student counts.",
 "Student Identity Id":"Stable unique identifier for the student across schools and years.",
 "Sams Student Id":"Student's identifier in the SAMS student administration system.",
 "Main School Id":"Identifier of the student's primary (home) school.",
 "School of Record":"The school officially responsible for the student's record and reporting.",
 "Student School":"Name of the school the student is currently attending.",
 "Student Name":"Student's full name.",
 "Student Short Name":"Student's abbreviated/display name.",
 "Recommended Record":"Flag marking the single recommended demographic record to use when a student has multiple (1 = use this record).",
 "Date of Birth":"Student's date of birth.",
 "Gender":"Student's gender.",
 "Hispanic or Latino":"Whether the student identifies as Hispanic or Latino.",
 "Standardized Ethnicity":"Student's ethnicity mapped to a standardized category.",
 "Ethnicity Id":"Numeric identifier for the student's ethnicity.",
 "Cohort Graduation Year":"Expected on-time high-school graduation year for the student's cohort.",
 "Grade Level":"Student's current grade level.",
 "Grade Band":"Grouped grade range (e.g., K-5, 6-8, 9-12) derived from grade level.",
 "Ft Pt Status":"Whether the student is enrolled full-time or part-time.",
 "New Returning Flag":"Whether the student is new to the school this year or returning.",
 "Start Status":"Student's enrollment start status for the term/year.",
 "Persistence":"Student persistence status — whether the student remains actively enrolled/engaged.",
 "Is Fay":"Full Academic Year flag — whether the student was enrolled for the full academic year (accountability inclusion).",
 "Report Date":"Date of the reporting snapshot for this record.",
 "Slicer Date":"Date value used to drive date slicer/parameter selection in downstream reports.",
 "School Entry Date":"Date the student entered the school.",
 "School Start Date":"Start date of the student's current school enrollment.",
 "School Year":"Academic year of the record (e.g., 2025-2026).",
 "School Year Start Date":"Start date of the academic year.",
 "Career Learning":"Career Learning program segment/indicator for the school or student.",
 "Region":"Geographic region of the school.",
 "State":"U.S. state of the school.",
 "School":"School identifier/short name.",
 "School Name":"Full name of the school.",
 "School Category":"Category classification of the school.",
 "School Group":"Grouping the school belongs to (e.g., management group).",
 "School Type":"Type of school (e.g., online public, private).",
 "Ap Course Count":"Number of Advanced Placement (AP) courses the student is enrolled in.",
 "Honors Course Count":"Number of honors courses the student is enrolled in.",
 "Course Passing":"Share of the student's courses currently passing.",
 "Course Passing Count":"Number of courses the student is currently passing.",
 "Course Failing Count":"Number of courses the student is currently failing.",
 "Course Failing Bckt":"Bucketed category of how many courses the student is failing.",
 "Missed Days Ytd":"Number of school days missed year-to-date.",
 "Days Since Act":"Days since the student's last course activity.",
 "Days W Act L 7 D":"Number of days with course activity in the last 7 days.",
 "Four Wk Avg Course Act":"Four-week rolling average of course activity.",
 "Ytd Avg Days Course Act":"Year-to-date average number of days with course activity.",
 "Rem Wk Range":"Bucketed weekly range of remediation time.",
 "Pass All Bckt":"Bucketed category summarizing whether the student is passing all courses.",
 "Pass All Flag":"Flag: student is passing all enrolled courses (1 = yes).",
 "RLSFlag":"Row-level-security flag (computed): 'true' when the current user is permitted to see this student's row (member of AIM team or matched via the RLS table).",
 "User":"User principal (email) in the row-level-security mapping table.",
 "Main School ID":"School identifier a user is authorized to see, in the row-level-security mapping table.",
 "User (RLS Table)":"Reference to the authorized user (email) from the RLS security table, used to evaluate row visibility.",
 "SUPPORT_TIER":"School support tier. NOTE: this column is currently an unresolved reference (source column RPT_DT_D_SCHOOL.SUPPORT_TIER is missing) and must be repointed before it will populate.",
}

def describe(label):
    base=re.sub(r'\s*\(RPT_[A-Z_]+\)$','',label).strip()
    if base in OVER: return OVER[base]
    sjm=re.search(r'\b(Ela|Mth|Sci|His)\b', base)
    sj=sjm.group(1) if sjm else None
    S=subj(sj) if sj else None
    sp=(S+" ") if S else ""
    win=" (end-of-year)" if base.endswith("Eoy") else " (middle-of-year)" if base.endswith("Moy") else ""
    # KPI Met family (check first; explicit mapping)
    m=re.match(r'Kpi Met (.+)$',base)
    if m:
        mapping={
          "Cc Ela":"the ELA Class Connect attendance KPI","Cc Mth":"the Math Class Connect attendance KPI","Cc Overall":"the overall Class Connect attendance KPI",
          "Course Ela":"the ELA course-activity KPI","Course Mth":"the Math course-activity KPI","Course Overall":"the overall course-activity KPI",
          "Crs Act":"the course-activity KPI","Pass All":"the passing-all-courses KPI","Pass Ela":"the ELA passing KPI","Pass Mth":"the Math passing KPI",
          "Priority Ela":"the ELA priority-intervention KPI","Priority Mth":"the Math priority-intervention KPI",
          "Rem Ela":"the ELA remediation KPI","Rem Mth":"the Math remediation KPI"}
        return f"Flag indicating whether the student met {mapping.get(m.group(1), m.group(1)+' KPI')} (Yes/No)."
    # MTSS
    if re.search(r'Mtss Tier$',base): return f"{sp}MTSS (Multi-Tiered System of Supports) intervention tier assigned to the student."
    if re.search(r'Mtss Rec$',base):  return f"Recommended {sp}MTSS intervention tier for the student based on performance data."
    if re.search(r'Mtss Match$',base):return f"Whether the student's assigned {sp}MTSS tier matches the recommended tier."
    # Grade / quintile
    if re.search(r'Grade Quintile$',base): return f"Performance quintile (1-5 bucket) of the student's {sp}grade."
    if re.search(r'\bGrade$',base) and sj: return f"Current {sp}course grade (percentage)."
    # Interim families (subject sits mid-label)
    if re.search(r'Interim Assessment',base): return f"{sp}interim diagnostic assessment result{win}."
    if re.search(r'Interim Benchmark',base):  return f"Whether the student met the {sp}interim assessment benchmark{win} (1 = met)."
    if re.search(r'Interim Participation',base): return f"Whether the student participated in the {sp}interim assessment{win} (1 = participated)."
    if re.search(r'Interim Window',base): return f"{sp}interim assessment testing window{win}."
    # Growth
    if re.search(r'Boy to Eoy Growth$',base): return f"{sp}assessment growth from beginning-of-year to end-of-year."
    if re.search(r'Boy to Moy Growth$',base): return f"{sp}assessment growth from beginning-of-year to middle-of-year."
    # Class Connect
    if re.search(r'Cc Att Req Flag$',base): return f"Flag: student is required to attend {sp}Class Connect (live synchronous) sessions."
    if re.search(r'Cc Hrs Attend Opt L 7 D$',base): return f"Hours of optional {sp}Class Connect sessions attended in the last 7 days."
    if re.search(r'Cc Hrs Attend Req L 7 D$',base): return f"Hours of required {sp}Class Connect sessions attended in the last 7 days."
    if re.search(r'Cc Hrs Invited Req L 7 D$',base): return f"Hours of required {sp}Class Connect sessions the student was invited to in the last 7 days."
    # Course duration / counts
    if re.search(r'Course Duration L 7 D$',base): return f"Total time spent in {sp}courses over the last 7 days."
    if re.search(r'Crs Ct$',base): return f"Number of {sp}courses the student is enrolled in."
    if re.search(r'Pass Ct$',base): return f"Number of {sp}courses the student is passing."
    # Remediation
    if re.search(r'Rem Tool$',base): return f"{sp}remediation tool/program assigned to the student."
    if re.search(r'Rem Wkly Time$',base): return f"Weekly time spent in {sp}remediation."
    # Pass All Flag by subject
    m=re.match(r'Pass All Flag (Ela|Mth|Sci|His)$',base)
    if m: return f"Flag: student is passing all {subj(m.group(1))} courses (1 = yes)."
    # Course-deficiency flags
    m=re.match(r'Cd (Ela|Mth|Total) Flag$',base)
    if m:
        who="overall" if m.group(1)=="Total" else subj(m.group(1))
        return f"Course-deficiency indicator flag for {who} (1 = deficiency present)."
    # Prior-year proficiency
    if base.startswith("Py "):
        pmap={
         "Ela Num Prof Levels":"Number of proficiency levels in the prior-year ELA state assessment scale.",
         "Ela Proficiency Level":"Prior-year ELA state-assessment proficiency level (label).",
         "Ela Proficiency Number":"Prior-year ELA proficiency level as a number.",
         "Ela Proficient Flag":"Flag: student was proficient on the prior-year ELA state assessment (1 = proficient).",
         "Ela Test Date":"Date of the prior-year ELA state assessment.",
         "Ela Test Name":"Name of the prior-year ELA state assessment.",
         "Mth Num Prof Levels":"Number of proficiency levels in the prior-year Math state assessment scale.",
         "Mth Proficiency Level":"Prior-year Math state-assessment proficiency level (label).",
         "Mth Proficiency Number":"Prior-year Math proficiency level as a number.",
         "Mth Proficient Flag":"Flag: student was proficient on the prior-year Math state assessment (1 = proficient).",
         "Mth Test Date":"Date of the prior-year Math state assessment.",
         "Mth Test Name":"Name of the prior-year Math state assessment."}
        if base[3:] in pmap: return pmap[base[3:]]
    return f"{base}."

rows=[]
for c in cols:
    label=c.get("label") or c.get("name")
    rows.append({"Element":EL.get(c.get("elementId"),c.get("elementId")),
                 "Source":src(c.get("formula")),"Field":label,
                 "Type":dtype(c),"Description":describe(label)})

with open("field_descriptions.csv","w",newline="") as f:
    wr=csv.DictWriter(f,fieldnames=["Element","Source","Field","Type","Description"]); wr.writeheader(); wr.writerows(rows)
json.dump({r["Field"]:r["Description"] for r in rows}, open("field_descriptions.json","w"), indent=2)
# markdown grouped by source
from collections import defaultdict
by=defaultdict(list)
for r in rows: by[r["Source"]].append(r)
with open("field_descriptions.md","w") as f:
    f.write("# Student_DM for AI — field descriptions ("+str(len(rows))+" fields)\n\n")
    for s in sorted(by,key=lambda k:-len(by[k])):
        f.write(f"## {s} ({len(by[s])})\n\n| Field | Type | Description |\n|---|---|---|\n")
        for r in sorted(by[s],key=lambda x:x["Field"]):
            f.write(f"| {r['Field']} | {r['Type']} | {r['Description']} |\n")
        f.write("\n")
print("wrote", len(rows), "descriptions")
# show a sample across categories
import random
for lbl in ["Mth Mtss Tier","Mth Mtss Rec","Ela Mtss Match","Kpi Met Pass Mth","Interim Benchmark Ela Eoy","Is Fay","Cc Hrs Attend Req L 7 D","Py Mth Proficient Flag","School Student Key","RLSFlag","SUPPORT_TIER","Grade Band"]:
    d=next((r["Description"] for r in rows if r["Field"]==lbl),"?")
    print(f"  {lbl}: {d}")
