# Stride — Enrollment & Program Performance Command Center

A branded Sigma workbook generated for **Stride, Inc. (NYSE: LRN)** — K-12 online
education + career learning — via the `sigma-company-dashboard-v2` skill from the
`cmiller-coder/millersigma` repo (cloned into this session).

## Live deliverable

- **Workbook:** https://app.sigmacomputing.com/stridelearning/workbook/1FZlZoIp10gZrpPKAsb58y
- **Workbook ID:** `371bf52a-e13b-4eff-bb86-186de233140e`
- **Org:** `stridelearning` (production, `api.us-a.aws.sigmacomputing.com`, org `2be5e6bd-…`)
- **Folder:** `My Documents / Stride Learning` (`69f26de8-…`)
- **Connection:** `Stride-POC` Snowflake (`a466ec39-…`) — SQL is pure generated
  (Snowflake `GENERATOR`/`SEQ4`, no source tables), so any live warehouse resolves it.
- **Surfaces built:** Command Center + Enrollment Planning (scenario modeler) +
  Student Segments (cohort builder). ~201 elements. Native marker strip (no bespoke plugin).
- Live spec captured in [`spec.json`](./spec.json); page renders in [`renders/`](./renders).

## Economics mapping (the important decision)

Stride is an **enrollment × tuition** business, not a balance × rate one, so it hits
the guide's "'Net Revenue' is a spread" trap head-on. The clean mapping used
(same shape Delta/NVIDIA landed on), with `funding_rate = 0` on every line:

| generic slot | Stride meaning | KPI label |
|---|---|---|
| volume (`bal_base`) | program revenue ($MM) | Revenue ($M) |
| `yield_rate` | gross margin % | Gross margin % |
| Net Revenue column | revenue × margin = **gross profit** | Gross profit ($M) |
| `opex_ratio` | SG&A as a share of gross profit | — |
| Contribution column | gross profit − SG&A = **operating income** | Operating income ($M) |
| `units_base` | average enrollments (K) | Enrollments (K) |
| `delinq_rate` | at-risk re-enrollment % | risk signal |

Calibrated to **FY2026** (ended 30 Jun 2026, reported 4 Aug 2026), and the render
values track the real figures closely:

| metric | real FY2026 | in workbook |
|---|---|---|
| Total revenue | $2,518.1M | ~$2,252M TTM (Revenue KPI) |
| General Education | $1,417.8M | $1,418M |
| Career Learning | $1,100.3M | $1,100M |
| Gross margin | 37.7% | 38.1% |
| Operating income | $450.8M (17.9%) | ~$406M TTM (18.0%) |
| Avg enrollments | 243.9K | 249K |
| Revenue / enrollment | $9,914 | cited by the Copilot agent |

Programs (products): Online Public Schools, Private & Tuition (General Education);
Middle-High Career, Adult Skills — MedCerts/Tech Elevator/Galvanize (Career Learning).

## Reproducing / updating

The per-prospect config lives entirely in the millersigma skill's
`scripts/company.py` (`STRIDE` block + `LABELS`/`SEGMENTS`/`VOCAB`/`POP`/`FOOTPRINTS`/
`subs`/`STATEMENTS["stride"]`). The exact source diff is in
[`millersigma-stride.patch`](./millersigma-stride.patch) — apply it on top of a fresh
`cmiller-coder/millersigma` clone. `sigmaapi.py` was repointed from staging to this
production org (see "Auth" below).

```bash
# in millersigma/skills/sigma-company-dashboard-v2/scripts
SURFACES=command,model,cohort COMPANY=stride python3 build_sofi.py create
COMPANY=stride python3 build_sofi.py update 371bf52a-e13b-4eff-bb86-186de233140e
python3 shot.py workbook 371bf52a-e13b-4eff-bb86-186de233140e ../shots/stride
```

## Auth note (why the default host failed)

The injected `SIGMA_BASE_URL` is `https://api-us-a.aws.sigmacomputing.com` (hyphenated),
which the session's agent proxy rejects with a 502 CONNECT tunnel error. The reachable
production host is the **dotted** `https://api.us-a.aws.sigmacomputing.com`. `sigmaapi.py`
was repointed there and reads its client id/secret from `~/.sigma-portals/prod.env`
(outside the workspace, `chmod 600`).

## Known limitation — PDF report skipped

The pixel-perfect PDF statement (`build_statement.py`, a "Family Enrollment Statement"
for Stride) was requested but **skipped**: on this production org
`POST /v2/reports/spec` returns **404** (the reports-as-code *write* endpoint is not
enabled there — only `GET /v2/reports` is available; the write API was only ever
verified on staging). The full `STATEMENTS["stride"]` config is authored and validated
(Balance Due $1,243, Learning Credits 2,000) and is included in the patch, so it will
build unchanged the moment that endpoint is enabled (or when run on a staging org).

## One post-render fix applied

The Enrollments KPI first rendered as `14` (the documented `units_base` scaling quirk:
displayed ≈ max(units_base) × max(state_share) × 1.157). Scaling all `units_base`
values by ~17.4× landed it at `249K` (prior `231K`), matching the real 243.9K.
