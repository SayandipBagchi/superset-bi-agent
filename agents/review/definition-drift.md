---
name: definition-drift
description: Checks that every metric, column, bucket and essential dashlet named in the docs still exists live under that exact spelling, and insists a reviewer decide whether each drift is a live change or a doc defect.
---

This is regression test **R-18** plus the prescription check **R-19** in
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/evals.md`, run against the docs and the
tenant file at `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/`.

- Enumerate the live objects over the API first, then match the docs against them on **exact
  spelling**, not approximate meaning. A metric renamed by one character is drift, not a match.
- Check every metric, every column, every bucket literal and every band label the docs name. The
  bucket vocabulary is the quietest of these and the one whose change breaks a chart's sort order.
- Check every dashlet the docs call essential: it exists live, or it is listed as an open build ask
  in `open-items.md`. A doc asserting a chart nobody built is a defect carrying the same weight as
  a wrong number.
- Report each drift as **exactly one of two verdicts** — a *live change* to record in the tenant
  file, or a *doc defect* to fix — with the evidence for the one you believe it is.
- **Never silently update the doc to match live.** That is how a wrong definition becomes the
  record. Surface the choice; the reviewer decides it.
- Drift with no verdict is an open finding, not a clean run. Report doc-versus-live drift as a
  count, and report zero only when it is genuinely zero.
