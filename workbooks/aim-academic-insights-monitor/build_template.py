#!/usr/bin/env python3
"""Generate the AIM (Academic Insights Monitor) workbook TEMPLATE spec.

Scope: navigation + filters only (per user request) — branded header w/ logo,
4-box filter bar (unbound visual shell), functional segmented nav toggles, and
titled placeholder cards where charts/KPIs go. No data-model source is required.
"""
import json

# ---- palette (sampled from the AIM report images) ----
PAGE   = "#0A1E44"   # page background / header band (dark navy)
CARD   = "#123C74"   # panels / filter boxes (medium navy)
BORDER = "#1E4E8C"   # subtle panel border
LABEL  = "#BCD0EC"   # filter label text
SUB    = "#AEC2E0"   # subtitle text
INPUT  = "#EAF1FA"   # light 'All' input chip
INK    = "#0A1E44"
ORANGE = "#E8730C"   # active nav-pill accent (matches AIM report)

# The AIM logo already uploaded in the stridelearning org (harvested from the
# existing "AIM Template" workbook). Org-scoped upload key — renders the real
# logo on publish. A copy of the image is committed at assets/aim-logo.png.
LOGO_KEY = "2be5e6bd-91bf-4555-af8e-7a478785c5b8/fe7ac478-b589-49b6-9d3b-bf956668cc05.png"
SUBTITLE = 'Report Date: 08/02/2026 &nbsp;|&nbsp; Student Count: 8,237'

# ------------------------------------------------------------------ builders
def card_style(bg=CARD, border=BORDER, width=1, radius="round"):
    s = {"backgroundColor": bg}
    if radius:
        s["borderRadius"] = radius
    if border and width:
        s["borderColor"] = border
        s["borderWidth"] = width
    return s

def container(cid, style=None):
    e = {"id": cid, "kind": "container"}
    if style is not None:
        e["style"] = style
    return e

def text(tid, body, valign="middle"):
    return {"id": tid, "kind": "text", "body": body, "verticalAlign": valign}

def image(iid, key):
    return {"id": iid, "kind": "image",
            "source": {"kind": "upload", "key": key},
            "style": {"fit": "contain"}}

def segmented(sid, control_id, values, labels, active=None, name=None):
    # name="" suppresses the auto-humanized controlId label above the pills
    # (the doc's toggles carry no label). selectedColor tints the active pill
    # orange to match the AIM report accent.
    e = {
        "kind": "control",
        "id": sid,
        "controlId": control_id,
        "controlType": "segmented",
        "name": name or "",
        "source": {"kind": "manual", "valueType": "text",
                   "values": values, "labels": labels},
        "value": active,
        "style": {"borderRadius": "round"},
        "optionStyle": {"style": "pill", "selectedColor": ORANGE},
    }
    return e

def filter_box_body(label, value):
    return (f'<span style="color: {LABEL}">**{label}**</span>\n\n'
            f'<span style="background-color: {INPUT}">'
            f'&nbsp;&nbsp;{value} &#9662;&nbsp;&nbsp;</span>')

def title_body(title):
    return (f'# <span style="color: #FFFFFF">**{title}**</span>\n\n'
            f'<span style="color: {SUB}">{SUBTITLE}</span>')

def card_title_body(title):
    return f'### <span style="color: #FFFFFF">**{title}**</span>'


# ------------------------------------------------------------------ page spec
# Each page: (id, page-name, title, grade_label, [nav segmented defs], [card titles], card_cols)
# nav def: (suffix, controlId, values, labels, active)
FT = "FT"
PAGES = [
    dict(id="p-target-overview", name="Target Overview", title="Target Overview",
         grade="GRADE", navs=[], extra_additional_filters=True,
         cards=["% Course Passing", "Students Passing All", "Predicted Grad Rate",
                "Priority Indicator", "Time in Class Connect", "Time in Course",
                "Time in Intervention Tool", "Course Activity"], cols=3),
    dict(id="p-school-demographics", name="School Demographics", title="School Demographics",
         grade="GRADE",
         navs=[("demo", "DemoView",
                ["enrollment", "persistence", "mtss"],
                ["Enrollment by Program", "Student Persistence & Status", "MTSS Distribution"],
                "enrollment")],
         cards=["Student Count by Grade Band", "Enrollment by Program",
                "Student Count by Ethnicity", "Student Counts by School Group"], cols=2),
    dict(id="p-student-engagement", name="Student Engagement", title="Student Engagement",
         grade="GRADE",
         navs=[("cdur", "CourseDurationView", ["overall", "ela", "math"],
                ["Overall", "ELA", "Math"], "overall"),
               ("dact", "DaysActivityView", ["l7d", "wk4", "ytd", "missed"],
                ["Last 7 Days", "4 Wk Avg", "Year to Date", "Days Missed"], "l7d"),
               ("ccon", "ClassConnectView", ["overall", "ela", "math"],
                ["Overall", "ELA", "Math"], "overall"),
               ("trem", "RemediationView", ["ela", "math"], ["ELA", "Math"], "ela")],
         cards=["Course Duration (Last 7 Days)", "Days with Course Activity",
                "Required Class Connect Sessions (Last 7 Days)", "Time in Remediation"], cols=2),
    dict(id="p-academics", name="Academics", title="Academics",
         grade="GRADE BAND",
         navs=[("subj", "AcademicsSubject", ["ela", "math"], ["ELA", "Math"], "ela"),
               ("prate", "PassingRatesView", ["percent", "grades", "all"],
                ["Percent Passing", "Grade Details", "Passing All"], "all")],
         cards=["Growth Assessment", "Passing Rates",
                "Prior Year State Assessment", "Advanced Enrollment"], cols=2),
    dict(id="p-graduation", name="Graduation", title="Graduation",
         grade="GRADE",
         navs=[("gsubj", "CourseSubject",
                ["all", "ela", "ele", "his", "mth", "none", "sci"],
                ["Select all", "ELA", "ELE", "HIS", "MTH", "No Subj", "SCI"], "ela")],
         cards=["High School Passing Details", "Failing Courses by Count",
                "High School Course Details", "High School Drop Out"], cols=2),
    dict(id="p-mtss", name="MTSS", title="MTSS",
         grade="GRADE",
         navs=[("ccs", "ClassConnectMode", ["invited", "attended"],
                ["Invited", "Attended"], "invited")],
         cards=["MTSS Tier Alignment", "Required Class Connect Sessions",
                "Current Tier 1 Recommendation Details", "Course Passing Rate"], cols=2),
    dict(id="p-student-details", name="Student Details", title="Student Details",
         grade="GRADE", navs=[], bulk_ids=True,
         cards=["Student Details"], cols=1),
    dict(id="p-definitions", name="Definitions", title="Definitions",
         grade="GRADE", navs=[], no_filter_bar=False,
         cards=["Metric Definitions"], cols=1),
    dict(id="p-version-history", name="Version History", title="Version History",
         grade="GRADE", navs=[], no_filter_bar=True,
         cards=["Version History"], cols=1),
]

FILTERS = lambda grade: [("SCHOOL", "All"), (grade, "All"),
                         ("FULL/PART TIME", FT), ("REPORT DATE", "Latest Date")]
ADD_FILTERS = [("COHORT GRAD YEAR", "All"), ("ETHNICITY", "All"),
               ("STUDENT PROGRAM", "All"), ("NEW / RETURNING", "All"),
               ("SCHOOL OF RECORD", "All"), ("FAY STUDENT", "All")]


def build_page(pg):
    els = []
    lx = []            # layout XML children of the page-bg container
    pid = pg["id"]
    row = 1            # running grid row cursor within the bg container

    def place(eid, c0, c1, r0, r1):
        lx.append(f'      <LayoutElement elementId="{eid}" gridColumn="{c0} / {c1}" gridRow="{r0} / {r1}"/>')

    def place_container(eid, c0, c1, r0, r1, children):
        lx.append(f'      <GridContainer elementId="{eid}" type="grid" gridColumn="{c0} / {c1}" gridRow="{r0} / {r1}" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto">')
        lx.extend(children)
        lx.append('      </GridContainer>')

    # ---- header (logo + title), cols 1..10 ; filter bar cols 10..25 ----
    hdr = f"hdr-{pid}"
    logo = f"logo-{pid}"
    ttl = f"ttl-{pid}"
    els += [container(hdr, style=card_style(bg=PAGE, border=None, width=0)),
            image(logo, LOGO_KEY), text(ttl, title_body(pg["title"]), "middle")]
    hdr_children = [
        f'        <LayoutElement elementId="{logo}" gridColumn="1 / 25" gridRow="1 / 4"/>',
        f'        <LayoutElement elementId="{ttl}"  gridColumn="1 / 25" gridRow="4 / 7"/>',
    ]
    # header container spans cols 1..(10 or 25 if no filter bar), rows 1..7
    no_fb = pg.get("no_filter_bar")
    hdr_c1 = 25 if no_fb else 11
    place_container(hdr, 1, hdr_c1, 1, 7, hdr_children)

    # ---- filter bar (4 boxes) ----
    if not no_fb:
        cols = [11, 15, 18, 22, 25]  # 4 boxes across cols 11..25
        for i, (label, value) in enumerate(FILTERS(pg["grade"])):
            box = f"flt-{pid}-{i}"
            lbl = f"fltx-{pid}-{i}"
            els += [container(box, style=card_style()),
                    text(lbl, filter_box_body(label, value), "middle")]
            place_container(box, cols[i], cols[i + 1], 1, 6,
                            [f'        <LayoutElement elementId="{lbl}" gridColumn="1 / 25" gridRow="1 / 6"/>'])
    row = 7

    # ---- nav toggles (segmented) ----
    if pg["navs"]:
        nav_c = 5
        span = (24 - 2 * (nav_c - 1))  # leave margins
        for (suf, cid, vals, labs, active) in pg["navs"]:
            sid = f"nav-{pid}-{suf}"
            els.append(segmented(sid, f"{cid}-{pid[2:6]}", vals, labs, active))
            place(sid, nav_c, 24 - nav_c + 2, row, row + 2)
            row += 2
        row += 1

    # ---- bulk student id shell (Student Details) ----
    if pg.get("bulk_ids"):
        bc = f"bulk-{pid}"; bt = f"bulkx-{pid}"
        els += [container(bc, style=card_style()),
                text(bt, (f'<span style="color: {LABEL}">**BULK STUDENT IDS**</span>\n\n'
                          f'<span style="background-color: {INPUT}">&nbsp;&nbsp;Enter Student IDs&nbsp;&nbsp;</span>'
                          f'&nbsp;&nbsp;&nbsp;<span style="color: {SUB}">← INCLUDES / EXCLUDES IDs '
                          f'(comma or new line)</span>'), "middle")]
        place_container(bc, 6, 20, row, row + 3,
                        [f'        <LayoutElement elementId="{bt}" gridColumn="1 / 25" gridRow="1 / 4"/>'])
        row += 4

    # ---- content placeholder cards ----
    cols_n = pg["cols"]
    card_titles = pg["cards"]
    span = 24 // cols_n
    card_h = 8
    for idx, tname in enumerate(card_titles):
        r = idx // cols_n
        c = idx % cols_n
        c0 = 1 + c * span
        c1 = c0 + span if c < cols_n - 1 else 25
        r0 = row + r * card_h
        r1 = r0 + card_h
        cc = f"card-{pid}-{idx}"; ct = f"cardx-{pid}-{idx}"
        els += [container(cc, style=card_style()), text(ct, card_title_body(tname), "start")]
        place_container(cc, c0, c1, r0, r1,
                        [f'        <LayoutElement elementId="{ct}" gridColumn="1 / 25" gridRow="1 / 3"/>'])
    used_rows = ((len(card_titles) + cols_n - 1) // cols_n) * card_h
    row += used_rows

    # ---- additional filters panel (Target Overview only) ----
    if pg.get("extra_additional_filters"):
        af = f"addf-{pid}"; aft = f"addfx-{pid}"
        af_children = [f'        <LayoutElement elementId="{aft}" gridColumn="1 / 25" gridRow="1 / 3"/>']
        els += [container(af, style=card_style(bg="#0E2C57")),
                text(aft, ('### <span style="color: #FFFFFF">**Additional Filters**</span>'
                           f'  <span style="color: {SUB}">— slide-out pane (rendered static; '
                           'button-triggered panes are unsupported in workbook-as-code)</span>'),
                     "middle")]
        af_cols = [1, 5, 9, 13, 17, 21, 25]
        for i, (label, value) in enumerate(ADD_FILTERS):
            box = f"af-{pid}-{i}"; lbl = f"afx-{pid}-{i}"
            els += [container(box, style=card_style()),
                    text(lbl, filter_box_body(label, value), "middle")]
            af_children.append(
                f'        <GridContainer elementId="{box}" type="grid" gridColumn="{af_cols[i]} / {af_cols[i+1]}" gridRow="3 / 7" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto">')
            af_children.append(f'          <LayoutElement elementId="{lbl}" gridColumn="1 / 25" gridRow="1 / 5"/>')
            af_children.append('        </GridContainer>')
        # active filters card
        acf = f"actf-{pid}"; acft = f"actfx-{pid}"
        els += [container(acf, style=card_style(bg="#0B2650")),
                text(acft, ('<span style="color: {0}">**ACTIVE FILTERS**</span>\n\n'
                            'Report Date = 2026-08-02\n\nFT/PT Status = FT').format(LABEL), "start")]
        af_children.append(
            f'        <GridContainer elementId="{acf}" type="grid" gridColumn="1 / 25" gridRow="7 / 12" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto">')
        af_children.append(f'          <LayoutElement elementId="{acft}" gridColumn="1 / 25" gridRow="1 / 6"/>')
        af_children.append('        </GridContainer>')
        place_container(af, 1, 25, row, row + 12, af_children)
        row += 12

    # ---- wrap everything in the page-bg container ----
    bg = f"bg-{pid}"
    els.insert(0, container(bg, style=card_style(bg=PAGE, border=None, width=0, radius=None)))
    page_xml = (
        f'<?xml version="1.0" encoding="utf-8"?>\n'
        f'<Page type="grid" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto" id="{pid}">\n'
        f'  <GridContainer elementId="{bg}" type="grid" gridColumn="1 / 25" gridRow="1 / {row+1}" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto">\n'
        + "\n".join(lx) +
        f'\n  </GridContainer>\n</Page>'
    )
    return {"id": pid, "name": pg["name"], "elements": els}, page_xml


pages, layouts = [], []
for pg in PAGES:
    page, xml = build_page(pg)
    pages.append(page)
    layouts.append(xml)

spec = {
    "name": "AIM — Academic Insights Monitor (Template)",
    "folderId": "3c5422bd-6d61-4739-ac4e-de8aec9a66c1",  # stridelearning → My Documents
    "description": "K12 Academic Insights Monitor — navigation + filter template shell. "
                   "Header/logo, filter bars, and segmented nav toggles across 9 pages. "
                   "Charts/KPIs intentionally omitted (placeholder cards mark their positions).",
    "schemaVersion": 1,
    "themeOverrides": {"pageWidth": "large", "space": {"unit": "small"}},
    "pages": pages,
    "layout": "".join(layouts),
}

out = "workbooks/aim-academic-insights-monitor/spec.json"
with open(out, "w") as f:
    json.dump(spec, f, indent=2)
print("wrote", out)
print("pages:", len(pages), "| total elements:",
      sum(len(p["elements"]) for p in pages))
