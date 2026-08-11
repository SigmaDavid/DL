# AIM AI — layout cleanup + AI summaries + chat placeholder

Live workbook: **AIM AI** (`b7422acd-c347-47f8-a4ea-b014ea915c0d`)
https://app.sigmacomputing.com/stridelearning/workbook/AIM-AI-5zNPJbgz8VC6vNQ3i1AHNj
Folder: My Documents · API base: `https://api.us-a.aws.sigmacomputing.com`

## What was done (2026-08-11)

Edited the 3 dashboard pages (Target Overview, School Demographics, Student
Engagement); Raw/Staging left untouched. Transform in `transform.py`
(`t_final.py`), applied via `PUT /v2/workbooks/{id}/spec`. All data bindings
(KPIs, charts, controls) preserved — only styling/layout/text changed + new
elements added.

**Layout cleanup**
- Filters restyled to white cards (`style.backgroundColor:#FFFFFF`) so the
  previously dark-on-navy labels are readable; dropped the " Filter" suffix.
- Replaced the giant unframed white H1 placeholders with tidy, consistently
  sized light text under clear light **section titles** (Priority Indicator,
  Time in Class Connect, etc.).
- Reflowed each page into an even grid; School Demographics charts now sit
  side-by-side with the tabbed container full-width below.

**AI summaries** — one live `CallText` insight band per page:
`CallText("SNOWFLAKE.CORTEX.COMPLETE","llama3.1-8b", <prompt referencing Student Base metrics>)`
wrapped in `Replace(..., '"', "")`. Renders real numbers (e.g. Target Overview:
"overall course passing 83%, students passing all 75%").

**Chat element** — added a styled **placeholder** on Target Overview.
A real Sigma chat element is **not creatable via workbooks-as-code**
(Sigma docs list chat/AI/agent elements as unsupported in the spec). Add it in
the UI (see below).

## To add the real chat element (UI, ~30s)
1. Open the workbook → **Edit**.
2. On **Target Overview**, delete the "Ask AIM Assistant" placeholder text
   (bottom-right).
3. **Add element → Chat** (Sigma Assistant / agent element), pick the agent,
   drop it in that spot. **Publish.**
> Do this AFTER any further API PUTs — a PUT replaces the whole document and
> would remove a UI-added chat element.

## Gotchas learned (this newer `document`-wrapped schema)
- PUT body = `{name, folderId, document}` (strip response-only top-level fields).
- **`container` / `<GridContainer>` are rejected** here (masked
  `incident-id` 400) — only flat `<Element>` and `<TabbedContainer>/<Tab>`
  work. Used a flat layout instead of card containers.
- Text `<p>` must carry a **non-default** alignment/style (`center`/`right`/
  a class); bare `<p>` and `text-align:left` are rejected. Use `#`/`###`
  headings or plain markdown otherwise.
- CallText model: **`llama3.1-8b`** works in this org's Cortex;
  `claude-3-5-sonnet` returned N/A (not enabled).
- Some `[Student Base/...]` columns return **text** in a sourceless text
  element — wrap numerics in `Number(...)` before `Avg/Sum`
  (e.g. Total Course Duration, Days With Activity).

## Caveats
- AI summaries are LLM-generated and can state specifics not in the prompt
  (e.g. School Demographics invented grade-band/ethnicity %s from only the
  total count). Tighten prompts / feed more grounded numbers to reduce this.
- Cloudflare intermittently challenges writes via the agent proxy; retry.
