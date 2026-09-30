# On Load Trigger (Sigma plugin)

Invisible plugin element that fires a workbook action the moment it loads.
Recreated from a screenshot of the `@sigmacomputing/plugin` React example.

- Editor panel: one **action-trigger** named `onLoadAction` (label "onLoad").
- Runtime: `useActionTrigger(config.onLoadAction)` is called once in a `useEffect`.
- Renders an empty transparent `<div>`.

## Run / register
```bash
npm install
npm run dev        # http://localhost:3000
```
Register the hosted URL (dev server or a static host serving `dist/` after `npm run build`):
```bash
python3 scripts/register_plugin.py "$SIGMA_BASE_URL" "$TOKEN" "On Load Trigger" "<https-url>" "Fires an action on load"
```
Then in the workbook add the plugin element, and under **onLoad** choose the action sequence to run.
