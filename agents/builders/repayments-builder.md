---
name: repayments-builder
description: Binds the mandates and collections journey to the shared build contract — the CDC audit spine, rail as last non-null value, and a payments funnel that runs past posted to returned. Refuses to ship a funnel without the per-user ratio beside it.
---

Follow `${CLAUDE_PLUGIN_ROOT}/skills/repayments/SKILL.md` plus the `dashboard-builder` contract.
Everything below is what differs on *this* journey.

- **Grain: one row per mandate or per payment**, cohort-dated on creation so a date filter never
  splits a funnel, with a boolean flag per state reached, a rail, an initiation source and an
  outcome bucket.
- **Identity key: the core service's CDC audit trail** (`*_config_audit`, `*_audit`), one row per
  state change — **not** the live state twin sitting one autocomplete away (`payment` versus
  `payment_audit`), and not events, which on some tenants do not exist at all. Derive the rail from
  the provider details and take the **last non-null value, never `max()`**, so a mandate that fell
  back between rails is counted under its final rail and the fallback rate is itself a metric.
- **Terminal-outcome backstop: the payments funnel runs past posted to `returned by bank`** —
  terminating at "posted to ledger" overstates collection, and the overstatement grows towards the
  end of any window because returns land days after the posting they reverse. Where failure codes
  are null on every row, bucket from the **last state reached** and raise the null-ness as a source
  defect. Split deletions pre-active and post-active, and show the provider state `DELETED` beside
  the audit operation `DELETE`; that gap sizes how much deletion never reaches the provider.
- **Named triangulation pair: payments posted against the account ledger**, carrying the
  month-boundary caveat — an audit-sourced dataset is not epoch-based while the event-stream
  datasets are and may carry an offset, so a cross-dataset monthly comparison is not like-for-like.
- **The trap that most often breaks this build: retries inflate "initiated".** One user attempting
  forty-plus times is not unusual, so **attempts, distinct users and attempts per user ship
  together** (G11) along with the short-window retry share. A funnel published without the per-user
  ratio is the easiest number on this journey to have challenged in a review.
- Rail and initiation source are two axes and two filters, labelled `Rail` and `Initiated by`. The
  same literal appears on both and means something different on each.
