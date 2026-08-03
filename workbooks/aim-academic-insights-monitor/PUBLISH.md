# Publishing the AIM template to stridelearning

This spec was authored but **not published** — the Sigma REST API host was
unreachable from the build session (see step 1). Follow these steps to publish.

## 1. Restore API egress (required — the build session couldn't reach the API)

The workbook build ran in a Claude Code web environment whose network policy
**blocked** the Sigma REST API host:

```
api-us-a.aws.sigmacomputing.com  →  502 CONNECT (egress policy denial)
```

`help.sigmacomputing.com` was reachable; the API host was not. Fix one of:

- **Add the host to the environment's allowlist** (or switch to a network
  policy that permits it), then start a fresh session. Network policy is chosen
  when the environment is created — see
  https://code.claude.com/docs/en/claude-code-on-the-web (Network access).
- **Or publish from a machine/CLI session that can reach the API** (your
  laptop with this repo checked out, `SIGMA_*` env vars set).

Verify egress is back:

```bash
bash scripts/api/_env.sh && scripts/api/whoami.sh   # should list recent files
```

## 2. Fill in the two placeholders

**a) Destination folder.** Resolve the stridelearning folder you want the
workbook in, then set `folderId` in `spec.json`:

```bash
scripts/api/list-folders.sh                     # find the target folder's id
# edit spec.json → "folderId": "<real-folder-uuid>"
```

**b) Logo URL.** Host `assets/aim-logo.png` at a public HTTPS URL (Sigma
`image` elements can't take uploads via spec), then replace every
`https://REPLACE-WITH-YOUR-HOST.example.com/aim-logo.png` in `spec.json`
(9 occurrences, one per page). Easiest: edit `LOGO_URL` at the top of
`build_template.py` and re-run it, then re-validate.

## 3. Validate → POST → GET-back → verify

```bash
python3 scripts/validate-spec.py workbooks/aim-academic-insights-monitor/spec.json
scripts/api/publish-workbook.sh post workbooks/aim-academic-insights-monitor/spec.json
# note the returned workbook id, then:
scripts/api/publish-workbook.sh get-spec <wb-id> > workbooks/aim-academic-insights-monitor/spec.json
scripts/api/verify-workbook.sh <wb-id>
```

Then **open the workbook in the Sigma UI** and eyeball it against the
screenshots in the source doc — the API does not validate layout/visual
quality. Expect to adjust: grid proportions of the filter bar, nav pill accent
color (theme), and card sizing.

## 4. Turn the filter shells into real controls (optional, needs a data model)

The 4 header filter boxes + the Additional Filters pane are currently styled
**placeholders**. To make them filter data, pick a stridelearning data model,
add a source `table` element, and replace each shell container with a real
`list` / `date` control bound to the matching column — see
`.claude/skills/sigma-workbook-conventions/reference/specification/controls.md`.
