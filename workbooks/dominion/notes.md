# Dominion Energy — Regulated Utility Performance Command Center

A branded Sigma workbook generated for **Dominion Energy, Inc. (NYSE: D)** — a
rate-regulated electric & gas utility — via the `sigma-company-dashboard-v2`
skill from the `cmiller-coder/millersigma` repo.

## Live deliverable

- **Workbook:** https://app.sigmacomputing.com/stridelearning/workbook/3mUnWxD9PF63Trbc0j51q5
- **Workbook ID:** `6eb61f5e-1e08-4282-9436-d5aa8c01f3dd`
- **Org:** production `api.us-a.aws.sigmacomputing.com` (org `2be5e6bd-…`)
- **Folder:** `My Documents / Dominion Energy` (`a1da89c8-…`)
- **Connection:** `Stride-POC` Snowflake (generated SQL is self-contained, so any
  live-warehouse connection resolves it).
- **Surfaces:** Command Center + Rate & Investment Planning (scenario modeler) +
  Customer Segments (cohort builder). Native marker strip (no bespoke plugin).
- Live spec in [`spec.json`](./spec.json); page renders in [`renders/`](./renders).

## Economics mapping

Regulated utility → the operating-earnings/spread model (`funding_rate = 0`):

| generic slot | Dominion meaning | KPI label |
|---|---|---|
| volume (`bal_base`) | segment operating revenue ($MM) | Operating revenue ($M) |
| `yield_rate` | operating-earnings margin % | Operating margin % |
| Net Revenue column | revenue × margin = **segment operating earnings** | Operating earnings ($M) |
| `opex_ratio` | corporate overhead share | — |
| Contribution column | earnings after Corporate & Other | Earnings after overhead ($M) |
| `units_base` | retail customers (K) | Customers (K) |

Calibrated to **FY2025** (reported early 2026); render values track the reals:

| metric | real FY2025 | in workbook |
|---|---|---|
| Operating revenue | $16,506M | $16,506M base (~$18.4B TTM) |
| Virginia / SC / Contracted revenue | ~$11,550M / $3,702M / $1,254M | matched |
| Segment operating earnings (DEV/DESC/Contracted) | $2,325M / $535M / $438M | $2,324M / $535M / $438M |
| Consolidated operating earnings | $2,966M | $2,967M (after overhead) |
| Customers | ~3.6M electric + 0.5M gas | 3,601K |

Business units (products): Virginia Electric Delivery, Virginia Power Generation
(Dominion Energy Virginia); South Carolina Electric, South Carolina Gas (Dominion
Energy South Carolina); Contracted Energy (Coastal Virginia Offshore Wind,
Millstone nuclear, solar).

## Reproducing / updating

Config lives in the millersigma skill's `scripts/company.py` (`DOMINION` block +
`LABELS`/`SEGMENTS`/`VOCAB`/`POP`/`FOOTPRINTS`/`subs`). The exact source diff is in
[`millersigma-dominion.patch`](./millersigma-dominion.patch); apply on a fresh
`cmiller-coder/millersigma` clone. `sigmaapi.py` is repointed to the production
US-A org (dotted host `api.us-a.aws.sigmacomputing.com`; the injected hyphenated
`api-us-a` host is proxy-blocked).

```bash
# in millersigma/skills/sigma-company-dashboard-v2/scripts
SURFACES=command,model,cohort COMPANY=dominion python3 build_sofi.py create
python3 shot.py workbook <id> ../shots/dominion
```

## Two post-render fixes applied

- Customers KPI first rendered `1,620K`; scaling retail `units_base` (~2.2×)
  landed it at `3,601K` (the documented `units_base` display quirk:
  ≈ max(units_base) × max(state_share) × 1.157).
- Revenue per customer first rendered `$42,501` (cohort skews C&I under the
  synthetic band distribution); lowered the `POP` per-customer bases to a
  believable blended `$8,159`.

## Note

No PDF report was built (the reports-as-code write endpoint `POST /v2/reports/spec`
returns 404 on this production org). The companion ~1M-row synthetic
material-forecast dataset for this task lives in `datasets/material-forecast/`.
