# Bell Curve — Sigma custom plugin

Draws a density curve with a shaded band (e.g. the middle 80%), a bracket with
labelled intersection points, an optional vertical reference line (e.g. a
redemption gate) and an optional gray "probability mass" bar. Chart only —
titles, percentile tables and "Panel model / Baseline" badges stay as native
Sigma elements around it.

## Editor panel inputs

| Section | Input | Notes |
|---|---|---|
| Data | Source, Curve X, Curve Y (density) | One row per curve point (≈100–300 points is plenty) |
| Shading & intersection | Lower / Upper intersection (X) | Number **control variables** — shading, bracket ends and value labels follow them |
| | Reference line label | Text above the bracket, default `80% of flows` |
| Reference line | Reference X, label | Optional dashed vertical line (e.g. gate = 0.05) |
| Mass bar | Mass at left edge (0–1), label | Optional gray bar; height is proportional to the probability |
| Format & style | Value format, decimals, Y label, 3 colors | Format: fraction→%, points→%, or plain number |

Tip: the lower/upper X values can be driven by percentile columns in your data
(e.g. P10 and P90) by pointing the controls at them with an action or default
value formula.

## Run / register

```bash
cd plugins/bell-curve
npm install
npm run dev      # http://localhost:3000
```

In Sigma: Administration → Account → Custom Plugins → add a plugin with
production URL `http://localhost:3000` (dev) or your deployed `dist/` URL,
then add it to a workbook via Element bar → UI elements → Plugins.

`npm run build` outputs `dist/` (host anywhere over HTTPS). `dist/demo.html`
(or `npm run dev` → `/demo.html`) renders three sample charts without Sigma.
