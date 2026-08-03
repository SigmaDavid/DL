# AIM — Academic Insights Monitor (Template) — Notes

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

## Known limitations / to wire up after publish

1. **`folderId`** is a placeholder (`REPLACE_WITH_STRIDELEARNING_FOLDER_ID`) —
   resolve the real stridelearning destination folder before POST. See
   `PUBLISH.md`.
2. **Logo URL** is a placeholder — Sigma `image` elements need a public HTTPS
   URL. The extracted asset is at `assets/aim-logo.png`; host it and swap the
   `LOGO_URL` in `build_template.py` (or the `url` fields in `spec.json`).
3. **Filter bar is non-functional** until each box is converted to a real
   `list`/`date` control bound to a stridelearning data-model element. The
   shells mark position + labels only.
4. **Additional Filters slide-out** is rendered as a **static panel** on Target
   Overview — button-triggered panes/modals are unsupported in
   workbooks-as-code (`reference/specification/others.md`).
5. **Nav pill accent color** follows the workbook theme; the orange highlight in
   the screenshots needs a theme override to reproduce exactly.
6. **Not visually verified in Sigma** — the API host was unreachable this
   session (egress policy). Passed all 13 `validate-spec.py` checks offline;
   run the GET-back + visual verify after the first successful POST.

## Regenerate

```bash
python3 workbooks/aim-academic-insights-monitor/build_template.py
python3 scripts/validate-spec.py workbooks/aim-academic-insights-monitor/spec.json
```

## Iteration log

| Date | Iteration file | Prompt file | What worked | What broke | Promoted to skill? |
|------|----------------|-------------|-------------|------------|--------------------|
| 2026-08-03 | iterations/2026-08-03T000000Z.json | prompts/2026-08-03T000000Z.md | 9-page shell, 189 els, all 13 checks pass | egress blocked — no live POST/verify | no |

## Open questions / decisions

- Confirm destination folder in stridelearning.
- Confirm logo hosting URL.
- Decide whether to promote the filter shells to real bound controls (needs a
  data model).
