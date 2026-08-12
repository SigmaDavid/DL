# Aramark — Sigma Company Dashboard v2 build

Generated with the `sigma-company-dashboard-v2` skill from
[cmiller-coder/millersigma](https://github.com/cmiller-coder/millersigma) for
**https://www.aramark.com**.

## Live workbook

- **URL:** https://staging.sigmacomputing.io/papercranestaging/workbook/5KT5qS66QeMD4vl4CzHZHb
- **Workbook ID:** `bd21ffe2-2d31-4012-8d91-31f49357d501`
- **Org:** `papercranestaging` (staging), folder `My Documents/Claude Builder`
- **Surfaces built:** all three — Command Center + Margin Planning (scenario
  modeler) + Account Segments (cohort builder). 199 elements, 3 overlays, 3 agents.

## What it contains

- **Command Center** — Aramark red brand-gradient header with the real Aramark
  logo recoloured white; 4 comparative KPIs (Adj. operating income, Segment
  operating income, Managed revenue, Client accounts); an AI-authored insight
  band; Period / Product / Date-grain / Color-by controls; US plan-attainment
  map; sector-stacked AOI time series; a Performance-by-sector table; product
  baseball cards → modal → "Model in Margin Planning" drill-through; and an
  Aramark Copilot agent.
- **Margin Planning** — a "Food & labor cost shock (bps)" scenario modeler over
  an editable Assumptions input table (AOI margin Δ / Cost of services Δ per
  sector), projected-vs-baseline bars, uplift KPIs, and a Scenario Copilot.
- **Account Segments** — a cohort builder over client accounts (tier + dining
  frequency + services), 4 reactive KPIs, distribution charts, and a Cohort
  Copilot.

## How Aramark was modelled

Config lives in `aramark_company_block.py` (appended to the skill's
`scripts/company.py` — the only file that changes per prospect). Six lines of
business = Aramark's food & facilities sectors: **Business & Industry,
Education, Healthcare & Senior Living, Sports/Leisure/Corrections, Facilities &
Other, International**. Calibrated to the post-Vestis-spin food & support
services business (~$16–19B managed revenue; the rendered headline is
**$16.2B managed revenue / $1.35B adjusted operating income**, ~8% AOI margin).

Aramark is a real cost-of-services business, so the generator's income-minus-cost
formula genuinely computes its margin (HANDOFF §8): modelled the fee-only way
(`funding_rate = 0`, `yield_rate` = the true AOI margin), so the "Net Revenue"
spread reads as **adjusted operating income** and the volume KPI reads as
**managed revenue**. `balance_type` carries Aramark's real contract structure
(P&L vs client-interest/management-fee). `SEGMENTS` translates the six hardcoded
SoFi product names and the generic tier/engagement bands into Aramark's
vocabulary so no "Personal Loans" filter value leaks into the cohort page.
`POP` overrides per-account economics to institutional scale.

## Builder bug fixed (affects every non-SoFi company)

`sql/nim_bridge.sql` (the page-1 waterfall) hard-coded SoFi's product constants
instead of using the shared `__PRODUCTS__` substitution every other table uses,
so the waterfall rendered SoFi's dollar figures for **any** company. Fixed to
use `__PRODUCTS__` (see `nim_bridge.sql.patch`) — reproduces SoFi's numbers
exactly for SoFi and fixes Aramark/Marriott/Delta/NVIDIA/etc. Worth reporting
upstream to `cmiller-coder/millersigma`.

## Reproduce

```bash
git clone https://github.com/cmiller-coder/millersigma
cd millersigma
# append aramark_company_block.py to skills/sigma-company-dashboard-v2/scripts/company.py
# apply nim_bridge.sql.patch
# copy aramark_logo_white.datauri.txt to skills/sigma-company-dashboard-v2/assets/
# provide papercranestaging creds in ~/.sigma-portals/staging.env
#   (SIGMA_STAGING_CLIENT_ID / SIGMA_STAGING_CLIENT_SECRET)
cd skills/sigma-company-dashboard-v2/scripts
COMPANY=aramark python3 build_sofi.py create
python3 shot.py workbook <new-id> ../shots/aramark   # then LOOK at the PNGs
```

## Not built (offered as follow-ups)

- **Bespoke hero plugin** — a new plugin must be hosted on jsDelivr off the
  public millersigma repo (HANDOFF §9), which this checkout can't push to.
  Built plugin-clean like Marriott; a food-service day-part heatmap + food-cost
  commodity ticker is the natural bespoke fit for Aramark.
- **Pixel-perfect PDF report** (`build_statement.py`) — a separate script plus a
  whole `STATEMENTS` config block.

## Environment note

This session's egress policy blocks Aramark's own production Sigma host
(`api-us-a.aws.sigmacomputing.com`), so the build targeted the reachable
`papercranestaging` staging org using the provided credentials. To build into a
different org, allow-list that org's API host and point `scripts/sigmaapi.py`
(`BASE` / `ORG_ID` / folder / connection) at it.
