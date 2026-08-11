#!/usr/bin/env python3
"""Final cleanup of AIM AI: Target Overview + School Demographics + Student
Engagement. Flat layout (no containers), white filters, light section titles,
tidy placeholders, a live CallText AI-insight band per page, chat placeholder
on Target Overview. Preserves all KPI/chart/control data bindings."""
import json, re

SRC="/tmp/claude-0/-home-user-DL/2e203b9f-1796-54ee-8fff-7694e13a147c/scratchpad/aim_ai.json"
OUT="/tmp/claude-0/-home-user-DL/2e203b9f-1796-54ee-8fff-7694e13a147c/scratchpad/put_body.json"
d=json.load(open(SRC)); doc=d["document"]; els={e["id"]:e for e in doc["elements"]}
WHITE="#FFFFFF"; SUB="#AEC2E0"; ORANGE="#ff8a3d"; AIC="#E8EEF7"; MODEL="llama3.1-8b"
new=[]
def T(tid,body,va="middle"): new.append({"id":tid,"kind":"text","body":body,"verticalAlign":va}); return tid
def stitle(tid,t,va="end"): return T(tid,f'### <span style="color: {WHITE}">**{t}**</span>',va)
def ai(tid,prompt):
    return T(tid,f'### <span style="color: {ORANGE}">**✨ AI Insight**</span>\n\n'
        f'<span style="color: {AIC}">{{{{ Replace(CallText("SNOWFLAKE.CORTEX.COMPLETE","{MODEL}","{prompt}") , \'"\', "") }}}}</span>',"start")
def E(eid,c,r): return f'  <Element elementId="{eid}" gridColumn="{c}" gridRow="{r}"/>'
def style_filters(ids):
    for cid in ids:
        els[cid]["style"]={"backgroundColor":WHITE,"borderRadius":"round"}
        if isinstance(els[cid].get("name"),str): els[cid]["name"]=els[cid]["name"].replace(" Filter","")

# ============================ PAGE 1: Target Overview ============================
style_filters(["7udbR5xYkD","hjOAiV49PM","Kp-0bfZOwB","_Auo1suVH0"])
def val(l): return (f'<p style="text-align: center"><span style="color: {WHITE}">**{l}**</span></p>\n\n'
                    f'<p style="text-align: center"><span style="color: {SUB}">— —</span></p>')
els["vKRJrPV2GN"]["body"]=val("ELA"); els["-n5cQYOvCn"]["body"]=val("MTH")
els["CVldGmESth"]["body"]=val("ELA"); els["YTr5ZDNQeu"]["body"]=val("MTH")
els["eLYytFqTHv"]["body"]=f'<p style="text-align: center"><span style="color: {SUB}">*Deploying in a future update*</span></p>'
els["tk3xK3bcFV"]["body"]=('<p class="h-large" style="text-align: center"><span style="color: '
  f'{WHITE}">**4+ DAYS**</span></p>\n\n<p class="p-large" style="text-align: center"><span style="color: #FF5A47">0%</span></p>')
RULES=('Output ONLY two sentences with no preamble, header, label, or bullet points. '
 'Use ONLY the figures given below and never invent or estimate any other numbers, '
 'percentages, rates, or breakdowns. ')
ai("z-ai1",'You are a K-12 academic operations analyst for school leaders. '+RULES+
 'Figures: overall course passing rate " & Text(Round(Avg([Student Base/Course Passing])*100,0)) '
 '& "%, students passing all courses " & Text(Round(Avg([Student Base/Pass All Flag])*100,0)) '
 '& "%, total students " & Text(Sum([Student Base/Student Count])) & ". '
 'Name one strength and one area to watch using only these figures.')
T("z-chat",
  f'### <span style="color: {ORANGE}">**💬 Ask AIM Assistant**</span>\n\n'
  f'<span style="color: {WHITE}">Chat with your custom AIM agent here.</span>\n\n'
  f'<span style="color: {SUB}">*Placeholder — add a **Chat** element in the Sigma UI at this spot '
  '(chat elements can’t be created via the workbooks-as-code API).*</span>',"start")
for t,i in [("% Course Passing","s0"),("Students Passing All / Predicted Grad Rate","s1"),
    ("Priority Indicator","s2"),("Time in Class Connect","s3"),("Time in Course","s4"),
    ("Time in Intervention Tool","s5"),("Course Activity","s6")]: stitle("z-"+i,t)
P1=["<?xml version=\"1.0\" encoding=\"utf-8\"?>",
 '<Page type="grid" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto" id="JBEvwL2q4p">',
 E("v1hC8Mln8y","1 / 5","1 / 3"),E("yQSu72Uu8e","5 / 25","1 / 3"),E("HXIcAhWz4Z","1 / 25","3 / 4"),
 E("7udbR5xYkD","1 / 7","4 / 6"),E("hjOAiV49PM","7 / 13","4 / 6"),E("Kp-0bfZOwB","13 / 19","4 / 6"),E("_Auo1suVH0","19 / 25","4 / 6"),
 E("z-ai1","1 / 25","6 / 10"),
 E("z-s0","1 / 25","10 / 11"),E("NucZkotA-N","1 / 9","11 / 15"),E("edif2DUjeF","9 / 17","11 / 15"),E("ZqwdkKZeLS","17 / 25","11 / 15"),
 E("z-s1","1 / 25","15 / 16"),E("O2hmPt9VwH","1 / 13","16 / 20"),E("eLYytFqTHv","13 / 25","16 / 20"),
 E("z-s2","1 / 25","20 / 21"),E("vKRJrPV2GN","1 / 13","21 / 25"),E("-n5cQYOvCn","13 / 25","21 / 25"),
 E("z-s3","1 / 25","25 / 26"),E("I9AWQCHh5m","1 / 9","26 / 30"),E("yhEecEPr6t","9 / 17","26 / 30"),E("Uk9DWWsZ4P","17 / 25","26 / 30"),
 E("z-s4","1 / 25","30 / 31"),E("EIPO-WXh37","1 / 9","31 / 35"),E("Xn-1Csq21I","9 / 17","31 / 35"),E("lDyFs7S8ut","17 / 25","31 / 35"),
 E("z-s5","1 / 25","35 / 36"),E("CVldGmESth","1 / 13","36 / 40"),E("YTr5ZDNQeu","13 / 25","36 / 40"),
 E("z-s6","1 / 25","40 / 41"),E("tk3xK3bcFV","1 / 13","41 / 45"),E("z-chat","13 / 25","41 / 46"),
 '</Page>']

# ============================ PAGE 2: School Demographics ========================
style_filters(["8vCct9RQWr","hjR0kekSIT","ryvflNYopn","c8tajZ3Usn"])
# recolor the empty-tab "coming soon" notes to light + centered
for eid,msg in [("0VaR8i9M_A","Enrollment by Program charts and table coming soon"),
                ("ZFp_lLjyVN","Student Persistence &amp; Status charts coming soon"),
                ("W8JMbfp_Xd","MTSS Distribution charts coming soon")]:
    els[eid]["body"]=f'<p style="text-align: center"><span style="color: {SUB}">*{msg}*</span></p>'
ai("z-ai2",'You are a K-12 enrollment analyst for school leaders. '+RULES+
 'Do not mention any grade-band or ethnicity percentages. '
 'Figures: total enrolled students " & Text(Sum([Student Base/Student Count])) '
 '& ", overall course passing rate " & Text(Round(Avg([Student Base/Course Passing])*100,0)) & "%. '
 'Summarize enrollment scale and overall academic standing only.')
P2=['<Page type="grid" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto" id="NMOiOt_wFj">',
 E("i0oVTk_vQI","1 / 5","1 / 3"),E("pK7k5cY_Y0","5 / 25","1 / 3"),E("8ngwpWk253","1 / 25","3 / 4"),
 E("8vCct9RQWr","1 / 7","4 / 6"),E("hjR0kekSIT","7 / 13","4 / 6"),E("ryvflNYopn","13 / 19","4 / 6"),E("c8tajZ3Usn","19 / 25","4 / 6"),
 E("z-ai2","1 / 25","6 / 10"),
 E("c80UKROUne","1 / 13","10 / 26"),E("7NXeYBeLBR","13 / 25","10 / 26"),
 '  <TabbedContainer elementId="KcW3Nx3cW7" type="tabbed-container" gridColumn="1 / 25" gridRow="26 / 46">',
 '    <Tab gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto"><Element elementId="0VaR8i9M_A" gridColumn="1 / 25" gridRow="1 / 3"/></Tab>',
 '    <Tab gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto"><Element elementId="ZFp_lLjyVN" gridColumn="1 / 25" gridRow="1 / 3"/></Tab>',
 '    <Tab gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto"><Element elementId="W8JMbfp_Xd" gridColumn="1 / 25" gridRow="1 / 3"/></Tab>',
 '  </TabbedContainer>',
 '</Page>']

# ============================ PAGE 3: Student Engagement =========================
style_filters(["pUPQWdYowV","w4GlP5MckU","m-GEZmngmO","gPXt3U8BEM"])
els["xNpMGsYgKV"]["body"]=('### <span style="color: '+WHITE+'">Days with Course Activity (Last 7 Days)</span>\n\n'
  '<p style="text-align: center"><span style="color: '+SUB+'">*Chart coming soon*</span></p>')
els["0NS3iR049U"]["body"]=('### <span style="color: '+WHITE+'">Required Class Connect Sessions (Last 7 Days)</span>\n\n'
  '<p style="text-align: center"><span style="color: '+SUB+'">*Chart coming soon*</span></p>')
els["-k7RqAzYwl"]["body"]=('### <span style="color: '+WHITE+'">Time in Remediation</span>\n\n'
  '<p style="text-align: center"><span style="color: '+SUB+'">*Chart coming soon*</span></p>')
ai("z-ai3",'You are a K-12 student-engagement analyst for school leaders. '+RULES+
 'Figures: average course duration last 7 days " '
 '& Text(Round(Avg(Number([Student Base/Total Course Duration L 7 D])),1)) & " hours, '
 'average days with activity last 7 days " '
 '& Text(Round(Avg(Number([Student Base/Days W Act L 7 D])),1)) & ". '
 'Note one positive signal and one risk using only these figures.')
P3=['<Page type="grid" gridTemplateColumns="repeat(24, 1fr)" gridTemplateRows="auto" id="PncQor0EDL">',
 E("6Kpv0katuw","1 / 5","1 / 3"),E("g8GbQOrroR","5 / 25","1 / 3"),E("5-YFytlIwy","1 / 25","3 / 4"),
 E("pUPQWdYowV","1 / 7","4 / 6"),E("w4GlP5MckU","7 / 13","4 / 6"),E("m-GEZmngmO","13 / 19","4 / 6"),E("gPXt3U8BEM","19 / 25","4 / 6"),
 E("z-ai3","1 / 25","6 / 10"),
 E("sKU6pyzn9-","1 / 13","10 / 26"),E("xNpMGsYgKV","13 / 25","10 / 26"),
 E("0NS3iR049U","1 / 13","26 / 40"),E("-k7RqAzYwl","13 / 25","26 / 40"),
 '</Page>']

# ---- splice all three page blocks; keep Raw/Staging verbatim ----
xml=doc["layout"]
xml=re.sub(r'<\?xml[^>]*\?>\s*<Page[^>]*id="JBEvwL2q4p".*?</Page>', "\n".join(P1), xml, count=1, flags=re.S)
xml=re.sub(r'<Page[^>]*id="NMOiOt_wFj".*?</Page>', "\n".join(P2), xml, count=1, flags=re.S)
xml=re.sub(r'<Page[^>]*id="PncQor0EDL".*?</Page>', "\n".join(P3), xml, count=1, flags=re.S)
doc["layout"]=xml
doc["elements"].extend(new)
body={k:v for k,v in d.items() if k in ("name","folderId","document")}
json.dump(body,open(OUT,"w"))
print("added",len(new),"new elements; total",len(doc["elements"]))
