# Stepped QC protocol

Run every gate, in order, before publishing. Record the result of each in the companion doc.
A gate that fails is not a note-to-self and not a caveat you can ship around — it blocks
publication. Fix the dashlet or descope it (G7). A finding the engagement owner has explicitly
ruled on is recorded as a ruling, with who ruled and when, never as a silent pass.

---

## Gate 0 — Source sanity

For every table feeding the dashboard:

- [ ] `max(time_col)` recorded. **Freshness differences between tables are the explanation for
      most reconciliation gaps** — know them before anyone asks.
- [ ] Grain confirmed: `count(*) = count(distinct key)`.
- [ ] Null rate on every join key. Anything material gets a fallback plus a counter metric.
- [ ] Rollup/period columns filtered to the atomic grain.
- [ ] Constant-column scan run: any field that is zero, null or identical to another field
      across all history is flagged, not used.
- [ ] Every derived attribute taken from the *last* value, not `max()`.

### Dataset hygiene — run this over the whole instance, not just the dashboard

These are cheap, they are all one API call, and each one is a live finding somewhere in most
suites.

- [ ] **No orphan datasets** — every dataset is referenced by at least one chart. Enumerate with
      `GET /api/v1/dataset/` and diff against the datasources on
      `GET /api/v1/dashboard/{id}/charts`.
- [ ] **No orphan charts** — every chart sits on at least one dashboard.
- [ ] `main_dttm_col` set on every dataset a time filter is expected to reach. Unset means the
      filter degrades to post-aggregation filtering, silently.
- [ ] `cache_timeout` set, and matched to the source's refresh cadence.

> A live example of what this catches: an orphan dataset carrying one metric, sitting on a
> *non-audit* table one autocomplete away from the journey's real spine, on no dashboard.
> Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## Gate 0b — Population sanity (internal users)

**Blocking.** Enforces guardrail G8. Pre-launch and staff entities are in every table, and at
early-stage volumes they are not a rounding error.

- [ ] The go-live / market launch date is **recorded in writing** from the user, not inferred.
- [ ] Every dataset with pre-launch entities carries a `user_type` dimension.
- [ ] The dashboard's user-type filter defaults to **Customer only**, and the label says so.
- [ ] The internal count ships as its own visible metric — never silently excluded.
- [ ] **Every date-filter-exempt view has been checked separately** (lifetime RFM, "ever active",
      cohort tables). A date default does not protect these and they contaminate silently.
- [ ] The go-live date and the internal share are stated **on the dashboard**.
- [ ] If the only identifier is the date cut, that limitation is a shipped caveat.
- [ ] **Every native filter resolves to a dataset that is actually on the page.** A filter left
      pointing at a superseded dataset silently stops filtering everything, and nothing errors.

## Gate 0c — Journey grounding (internal users' sibling)

**Blocking.** Enforces guardrail G9. A journey derived from data alone reconciles beautifully
against the wrong definition.

- [ ] The artefacts actually obtained are listed — PRD, designs, event dictionary — and the ones
      that don't exist are named as missing.
- [ ] The **artefact register** exists: PRD, Design and Events reconciled per stage.
- [ ] The **feature availability matrix** exists per module, every cell asked rather than assumed.
- [ ] Every stage in the ladder has its instrumentation declared — BE, FE, both, or **neither**.
- [ ] Every zero or 100% step has been checked against feature flags and first-seen dates before
      being reported as drop-off.
- [ ] The companion doc states **which rung of the fallback ladder** the journey was grounded on.

## Gate 0d — Environment and schema provenance

**Blocking.** Enforces guardrail G10. Names lie about both, and UAT is indistinguishable from
production by name alone.

- [ ] The vendor analytics workspace is named, and **confirmed by the user as UAT or production**.
- [ ] The Superset database connection and id are named, and confirmed to point at production.
- [ ] Every schema in use is listed with its tenant id.
- [ ] **A number the business already quotes has been reproduced from the chosen source.** Nothing
      else settles the environment question.
- [ ] For every data point available in more than one schema: the candidates were put to the user,
      the choice is recorded, the rejected alternatives are recorded, and the count delta between
      them is reported.
- [ ] Environment and schema provenance appear in the companion doc **and** on the dashboard.

## Gate 1 — Definition trace

- [ ] Every metric on the page maps to exactly one row of the Definition Registry.
- [ ] No two Registry rows describe the same concept.
- [ ] Any metric that could be computed two ways (authorisation vs posted, initiated vs
      completed) has the chosen way written into its verbose name or the chart title.
- [ ] **No dataset retains Superset's default `count` metric.** It has no Registry row by
      definition, and it is one click away from being dragged onto a chart.
- [ ] The user has seen and agreed the Registry.

> Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## Gate 1b — Entity grain and structure

**Blocking.** Enforces guardrail G11. An event count is not a population, and a window function
computed at the wrong grain is plausible, wrong and silent.

- [ ] Every event-count metric a stakeholder may quote has a **unique-entity figure beside it**, or
      a stated reason why not.
- [ ] Any entity bridge is validated **on the failing rows**, with the unmatched rate reported.
- [ ] Every window function is partitioned by every dimension a chart filters on, and the final
      cumulative share is **exactly 100.0%**.
- [ ] Every date-filter-exempt dataset has `main_dttm_col` explicitly **null**.
- [ ] Every API-created chart has a saved `query_context` — otherwise Gate 3 cannot be run by query.
- [ ] Every aggregate-mode table needing a dimension order sorts by a **sort metric**, not
      `order_by_cols`.
- [ ] For every join: the query drives **FROM the grain being reported**, no WHERE predicate sits on
      the right side of a LEFT JOIN, and the join key is unique on the right (or pre-aggregated).
- [ ] Any dataset modified but not authored here has a `zz_backup_*` copy of its original SQL.

## Gate 2 — Monotonicity

- [ ] Every funnel is non-increasing left to right.

**A step that goes up is a definition error, not a data curiosity.** The two causes, in order of
likelihood:

1. Two steps drawn from different sources with different populations (an app-side event counted
   against a backend-derived denominator).
2. A step defined on a different entity grain than the one before it.

Fix by re-defining, not by re-ordering. A real case: "first spend" exceeded "account activated"
because spend was measured from authorisation events and activation from account events; moving
spend to *posted transactions* made the activation event a strict superset — 100% of spenders
had it, zero exceptions — and the funnel became monotonic on one source.

- [ ] Any 100% step interrogated: if two states are perfectly coincident, one carries no
      information and should be removed or replaced with a state from another source that
      genuinely sits between them.

### Initiated/ongoing pairs — do not assert either side until it is resolved

A dataset that keeps **both** members of an initiated/ongoing pair for the same stage
(`<stage>_init` + `<stage>_ongoing`) **and** ships a conversion between them
(`p_<stage>_init_ongoing`) is ambiguous until somebody queries it. Vendor-stage pairs — bank
connection, identity verification — are where this shows up most often, and a dataset usually
carries several of them at once.

Exactly one of two things is true of each such pair:

| If | Then |
|---|---|
| The pair is **not** coincident in the live tenant | A coincidence claim in the docs is wrong and needs correcting |
| The pair **is** coincident | Gate 2's last checkbox is failing live, once for every pair |

Resolve by query — `count(distinct entity where init)` vs `count(distinct entity where ongoing)`,
and the set difference, not just the counts. Log it as a numbered open item in
`${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`. Until it is resolved, do not
cite either state as settled.

## Gate 3 — Cross-dashboard reconciliation

Run this as an **explicit query**, not by eye, whenever more than one dashboard exists.

- [ ] For each shared data point, query it from every dashboard's dataset under identical
      filters and assert equality.
- [ ] Where they differ, the cause is identified and either fixed or documented on both pages.
- [ ] **Pairs that sit on the same dashboard from different datasets are on the list.** These are
      the easiest kind to miss: nothing about the page tells you two charts came from two
      datasets, and a reviewer reading top to bottom will assume they agree.

```sql
select 'dash_a' as src, count(distinct id) from dataset_a where <same filters>
union all
select 'dash_b',        count(distinct id) from dataset_b where <same filters>;
```

Do this again after **any** change to a shared dataset. Numbers drift silently.

### The worklist this produces

The cross-dashboard health check (bottom of this file) produces a numbered pair list: data
point, dataset A, dataset B, and a note on why they must agree or by how much they may differ.
Pairs that sit on the **same dashboard** from two datasets are the easiest to miss and belong on
the list like any other. A table read by three datasets across two dashboards is the suite's
single largest reconciliation exposure — nothing in Superset enforces that three datasets derive
the same data point the same way. Re-run every pair each session, and again after any edit to a
shared dataset.

Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## Gate 4 — Cross-source triangulation

**Every headline number must be confirmed against at least one independent source.** Where the
sources disagree, the gap is quantified and explained — on the dashboard if it is a real funnel
stage, in the caveats if it is an instrumentation artefact.

### The triangulation matrix

| Number | Primary source | Triangulate against | What a gap usually means |
|---|---|---|---|
| Funnel stage counts | Backend event stream | Raw/CDC table of the service of record | Event emission gaps, or backfilled records that skipped a state |
| Onboarding / journey completions | Backend event | Decisioning vendor's application table | Broken application link, or records created outside the journey |
| App-side steps | CDP export | Backend S2S event for the same action | FE under-reporting (see below) |
| Spend / transaction counts | Ledger (downstream) | Switch/auth table (upstream) | Real: approved upstream, declined downstream. **This is a funnel stage, not an error** |
| Repayment / mandate states | Service CDC audit trail | S2S events, then FE events | Hard deletes bypassing the state machine |
| Pre-application / eligibility volume | Quotation or partner feed | The funnel entry on the same page | A broken application link — this must reconcile or the section is disbelieved |
| Anything in a saved vendor dashboard | Your dataset | The vendor dashboard (CDP funnel, BI dashboard) | Windowing and step-definition differences |
| **Every reference dashlet from Phase 1** | Your dataset | The dashlet the org already quotes | Must be explained per the adopt/adapt/supersede call, never left as a surprise |
| **Every sibling dashboard on the same instance** | Your dataset | Whatever the sibling shows for the same concept | Nobody linked it, so nobody reconciled it — and it is one API call away |

The spend/transaction row is normally implemented by a dedicated reconciliation dataset that
spans switch and ledger precisely so the chain can be sized. Name that dataset when you run the
row.

### Sibling dashboards are mandatory triangulation targets

A dashboard on the same instance is a reference dashboard whether or not anyone told you about
it. It is the cheapest triangulation available and the likeliest source of a "your number doesn't
match mine" meeting.

- [ ] Every dashboard on the instance enumerated (`GET /api/v1/dashboard/`), and each one that
      overlaps your subject matter decoded down to its chart datasources.

> An undecoded sibling dashboard is a standing Gate 4 failure, not a backlog item: the gate
> cannot pass while a dashboard overlapping your subject matter has never had its chart
> datasources read. A sibling's *title alone* can already establish that a vendor feed exists in
> the estate that no dataset of yours reads.
> Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

### Rules for reading a discrepancy

**Backend vs the CDP.** Expect FE to under-report. Before blaming data quality, check *which
code path emits the FE event*: an event fired only by an in-app polling handler will be captured
at ~90%+ for in-app WebView journeys and ~25% for external-browser handoffs. Segment the
capture rate by route — if the paired "started" event tracks the outcome event exactly in every
bucket, the loss is the route, not the pipeline. Report the capture rate per route; it is more
useful than the aggregate gap.

**Windowed vs unbounded.** A vendor funnel with a fixed window that chains an identified step to
a pre-auth step will report a catastrophic false drop (13% against a true 95% is a real
example). Always publish the unbounded absolute figure alongside any windowed one, and say which
is which.

**Event vs raw schema.** When the event stream and the service's own audit table disagree, the
audit table wins. Events can be missed; the CDC trail is what actually happened. Two patterns to
look for: entities that reached a later state without emitting an earlier one (usually
backfilled records), and hard deletes that never passed through the state machine.

**Upstream vs downstream.** Do not treat this as a data-quality problem. Model it as a chain and
size each step — the volume approved at the switch but declined at the account is often the
single largest controllable loss in the whole flow, and it is invisible in either table alone.

### Tolerance bands

| Gap | Treatment |
|---|---|
| 0% | Pass, but confirm you didn't just query the same source twice |
| < 2%, explained by freshness | Pass, state the lag in the caveats |
| 2–10% | Must be explained before publishing; usually a grain or window difference |
| > 10% | Blocks publication. Something structural is wrong |
| Primary < triangulation source | Always investigate. Your spine may be missing rows |
| **Any systematic timestamp-offset difference** | **Never a tolerance band.** See below |

> **A cohort-boundary skew caused by a timezone offset is a DEFINITION difference, not a
> freshness tolerance.** It will present as a small percentage — comfortably inside the "<2%,
> explained by freshness" row — and passing it there is wrong. Freshness is a lag that closes;
> an offset is a permanent disagreement about which day an event belongs to, and it does not
> shrink when the pipeline catches up. Two datasets that apply different offsets are not
> measuring the same month. Fix the offset, or state it as a caveat on both pages and stop
> comparing their monthly series.

This happens in practice: epoch-based datasets in a suite apply a tenant offset while the
non-epoch datasets beside them apply none, so their month boundaries do not line up. Check it
per dataset, not per suite. Mechanics in `warehouse-gotchas.md`; live state in
`${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## Gate 5 — Render check

**This gate has two halves and they need different modes.** The file used to read as though the
whole thing needed a browser; it does not.

### 5a · Association — checkable by API, in *any* mode

`GET /api/v1/dashboard/{id}/charts` returns the charts the M2M actually holds. Compare it to
what you intended to place. No browser required.

- [ ] Every chart you created appears in the dashboard's chart list (M2M row exists, not just a
      `position_json` reference) — otherwise the grid renders blank.
- [ ] No `position_json` component references a chart id absent from that list, and no chart in
      the list is absent from `position_json`.
- [ ] Chart count matches the storyboard count.
- [ ] **Re-checked after the write and again after any subsequent save.** Deletions can be
      reverted by a UI re-save if the user has the dashboard open.

### 5b · Pixels — Chrome only

- [ ] No orphaned components ("There is no chart definition associated with this component").
- [ ] Rows re-balanced to 12 columns after any removal.
- [ ] Global filters actually apply — change one and confirm the numbers move.
- [ ] Default date range is the one that was agreed.
- [ ] Nothing renders as an error tile or an empty grid cell.

In direct-REST or MCP mode, run 5a, report it as passed, and report 5b as **not performed** —
naming which half you checked. Do not report Gate 5 as a pass on the strength of 5a alone.

## Gate 6 — Narrative check

- [ ] Every number has an owner and an implied action.
- [ ] Behavioural losses and decision losses are separated.
- [ ] The largest bucket is not "Other" — or if it is, that is flagged as the first thing to fix.
- [ ] Every Gate 0 flag appears in the caveats list.
- [ ] Recent-cohort immaturity is stated ("an entity that started this week may still complete").
- [ ] **No two charts on a dashboard share a concept and a source under different titles.** Read
      the title list as a set, not as a page — near-duplicates are invisible in the layout and
      obvious in the list.
- [ ] Would this survive a hostile review? Specifically: could someone find two numbers on this
      page, or across this suite, that should match and don't?

> The near-duplicate this catches looks like `Declines by category, by month (source: X)` beside
> `Declines by category, monthly (source: X)` — same concept, same source, two titles differing
> only in how they say "by month".
> Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

---

## The cross-dashboard health check

When a tenant has a suite rather than a single dashboard, run this as a standalone exercise and
write up the result:

1. List every data point that appears on more than one dashboard — **and every data point
   computed by more than one dataset, including two datasets on the same dashboard.**
2. For each, record the dataset, column and definition used on each dashboard.
3. Query each under identical filters and compare.
4. For any mismatch: identify which definition is correct, fix the others, re-run.
5. Publish the resulting Registry as the shared contract.

The output is a standing worklist, not a one-off note. Its shape is under Gate 3 above; the live
worklist is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

Do this whenever a dashboard is added to a suite, and whenever a shared dataset changes.
