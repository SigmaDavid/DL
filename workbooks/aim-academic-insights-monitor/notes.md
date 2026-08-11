# AIM — Academic Insights Monitor (Template) — Notes

## Status — PUBLISHED (2026-08-11)

- **Workbook id:** `9311230d-49bc-4d10-9b67-3ba06881efeb`
- **URL:** https://app.sigmacomputing.com/stridelearning/workbook/AIM-Academic-Insights-Monitor-Template-4tvHCSn0YuRgHFSlXPPUHF
- **Folder:** My Documents (`3c5422bd-6d61-4739-ac4e-de8aec9a66c1`)
- **Host:** `https://api.us-a.aws.sigmacomputing.com` (the injected
  `api-us-a.aws...` base was egress-blocked; the dotted `api.us-a.aws...`
  host both passes egress and authenticates).
- **Verified:** POST OK · all 189 elements compile clean
  (`verify-workbook.sh`) · PDF export visually matches the source doc
  (header/logo, filter bar, segmented nav toggles, page grid).
- **Logo:** uses the org's existing AIM upload key
  (`2be5e6bd.../fe7ac478....png`, harvested from the existing "AIM
  Template") — renders the real logo, no external hosting needed.

### One pending refinement (committed spec is ahead of live)

`spec.json` includes two cosmetic tweaks not yet applied to the live
workbook: segmented `name:""` (suppress the auto-humanized controlId label
above each toggle) and `optionStyle.selectedColor` orange (match the report
accent). The PUT to apply them was blocked by a **transient Cloudflare
managed challenge** on writes (GET/POST had worked; curl can't solve a JS
challenge). Re-run when the challenge clears:
`scripts/api/publish-workbook.sh put 9311230d-49bc-4d10-9b67-3ba06881efeb workbooks/aim-academic-insights-monitor/spec.json`
(prefix `export SIGMA_BASE_URL="https://api.us-a.aws.sigmacomputing.com"`).

## Goal

A reusable **navigation + filter template shell** for K12's "Academic Insights
Monitor" (AIM) workbook, reproduced from the 17 screenshots in
`AIM_Report_and_Tables.docx`. Charts and KPIs are intentionally out of scope —
the template carries the branded header/logo, the filter bar, the segmented
in-page nav toggles, and titled placeholder cards marking where each viz goes.

## What's in the spec

9 pages (`spec.json`), dark-navy theme via nested background containers:

| Page | Nav toggles (functional `segmented`) | Filter bar |
|------|--------------------------------------|-----------|
| Target Overview | — (+ Additional Filters panel) | School / Grade / Full-Part Time / Report Date |
| School Demographics | Enrollment by Program · Persistence & Status · MTSS Distribution | ✓ |
| Student Engagement | Overall·ELA·Math ×2 · Last7/4Wk/YTD/Missed · ELA·Math | ✓ |
| Academics | ELA·Math · Percent Passing·Grade Details·Passing All | ✓ (Grade Band) |
| Graduation | Course Subject (Select all·ELA·ELE·HIS·MTH·No Subj·SCI) | ✓ |
| MTSS | Invited · Attended | ✓ |
| Student Details | — (Bulk Student IDs shell) | ✓ |
| Definitions | — | ✓ |
| Version History | — | — |

## Data sources

- **None.** This is a source-less template. The 4-box filter bar and the
  Additional Filters pane are **unbound visual shells** (styled containers +
  label text), not live controls — by design (see prompt-of-record). Segmented
  nav toggles use `source.kind: manual`, so they are functional without data.

## Known limitations / to wire up

1. ~~`folderId` placeholder~~ — resolved to My Documents and published.
2. ~~Logo URL placeholder~~ — now uses the org's existing AIM upload key;
   the real logo renders. (`assets/aim-logo.png` kept as a committed copy.)
   Note: this API version uses `image.source:{kind:"upload",key}` +
   `style`, NOT `url` — the skill's `others.md` is out of date on this.
3. **Filter bar is non-functional** until each box is converted to a real
   `list`/`date` control bound to a stridelearning data-model element. The
   shells mark position + labels only.
4. **Additional Filters slide-out** is rendered as a **static panel** on Target
   Overview — button-triggered panes/modals are unsupported in
   workbooks-as-code (`reference/specification/others.md`).
5. **Nav pill accent** — `optionStyle.selectedColor` orange is in the spec but
   pending the refinement PUT (see Status). Live workbook currently shows the
   theme-default blue selected pill.
6. **Verified in Sigma** — POST OK, `verify-workbook.sh` clean, PDF export
   compared against the source doc. (Prior "egress blocked" note resolved once
   the working host/base URL was found.)

## Regenerate

```bash
python3 workbooks/aim-academic-insights-monitor/build_template.py
python3 scripts/validate-spec.py workbooks/aim-academic-insights-monitor/spec.json
```

## Iteration log

| Date | Iteration file | Prompt file | What worked | What broke | Promoted to skill? |
|------|----------------|-------------|-------------|------------|--------------------|
| 2026-08-03 | iterations/2026-08-03T000000Z.json | prompts/2026-08-03T000000Z.md | 9-page shell, 189 els, all 13 checks pass | egress blocked — no live POST/verify | no |
| 2026-08-11 | (live) | — | Published to My Documents (wb 9311230d); real logo via upload key; POST/verify/PDF all good | `borderRadius:null` + image `url` rejected (fixed → upload source); refinement PUT blocked by transient Cloudflare challenge | image-upload shape worth promoting to `others.md` |

## Open questions / decisions

- Confirm destination folder in stridelearning.
- Confirm logo hosting URL.
- Decide whether to promote the filter shells to real bound controls (needs a
  data model).
