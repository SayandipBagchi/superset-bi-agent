# Reviewing reference dashlets before you build

**Always ask whether reference dashlets exist, and review them before designing anything.** Not
to copy them — to know what the organisation currently believes, and to be able to explain
deliberately why your number differs.

The failure this prevents is specific and expensive: you publish a dashboard, someone opens the
CDP funnel they have been quoting for six months, the numbers disagree, and the meeting
becomes about your credibility rather than the finding. Reviewing first turns that into a
prepared line on the page.

## Reference dashboards on your own instance — start here

**A dashboard you didn't build is a reference dashboard whether or not anyone linked it to you.**
The reference dashlets most likely to contradict you are usually not in another tool. They are on
the same Superset instance, built by someone else, quoted by someone you have not met, and they
are one API call away.

So before you ask anyone anything, enumerate:

```
GET /api/v1/dashboard/?q=(columns:!(id,dashboard_title,slug,changed_on_utc,published),page_size:100)
```

Then, for every dashboard whose subject overlaps yours:

```
GET /api/v1/dashboard/{id}/charts     → slice_name, form_data.viz_type, form_data.datasource
GET /api/v1/dashboard/{id}/datasets
GET /api/v1/dataset/{id}              → sql, metrics[], columns[]
```

Full recipes and the Rison `q=` syntax: `superset-api.md`. This works in any mode — no
browser needed — and it gives you more than a screenshot ever will: the exact SQL, the exact
metric expressions, and the source tables the organisation already treats as truth.

Treat every result as Phase 1 material and a **Gate 4 triangulation target**. The ones nobody
mentioned are the ones that will surface in the meeting.

Undecoded siblings on the same instance are a standing Gate 4 blocker: the gate requires
triangulation against every reference dashlet from Phase 1, including siblings nobody linked.
Note what a sibling dashboard's *title alone* already tells you — a vendor named there whose
feeds no dataset reads is itself a finding.

Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## The prompt

Ask this in Phase 0, explicitly, and do not accept a vague answer — but ask it *after* you have
enumerated the instance, so you can name what you already found and get it explained:

> Are there existing dashlets I should review first — CDP funnels or behaviour charts,
> Superset or Data Studio dashboards, a BI/business-metrics dashboard, or a number leadership
> already quotes in a deck? Links, please. I'll decode what each one actually measures before I
> design anything, so I can either match it or explain the difference on the page.

Get **links**, not descriptions. And ask the follow-up: *which of these numbers does leadership
actually quote?* That one is the reconciliation target; the rest are context.

## What to extract from each reference dashlet

Record these in a short review note — one row per dashlet:

| Field | Why it matters |
|---|---|
| **Dashboard id and slug** (Superset) or URL (elsewhere) | What lets you find it again. The slug is the stable handle; ids differ between environments. Record both |
| Exact step definitions and event names | The most common cause of a differing number |
| **Window** (conversion/funnel window) | A 7-day window against your unbounded funnel explains most gaps by itself |
| **Analysis type** — unique users vs total events | Total events counts retries; unique users doesn't. Different questions |
| Granularity (entire / daily / monthly) | Affects whether the number is a sum of periods or a distinct count |
| Date range and whether it's rolling | A hardcoded range silently ages |
| Filters and segments applied | Often an invisible internal-user exclusion, or a missing one |
| Entity keyed on | User vs application vs account |
| Last edited / by whom | An unmaintained chart is context, not a target |

## Decode before you trust

Run these checks on every reference dashlet. Each has produced a real finding.

**1. Are its events still firing?** Query first-seen and last-seen date per event the dashlet
references.

```sql
select event_name, min(evt_date) as first_seen, max(evt_date) as last_seen, count(*) as n
from <events> where event_name in (...) group by 1;
```

An event with a `last_seen` months ago is a **permanent zero** on that chart — usually because
the app renamed it (a `…CTAClick` → `…Clicked` rename is a real example, and it silently broke
three funnel steps). The chart still renders; it just reports nothing. Flag it as a defect to
fix rather than treating the zero as a finding.

**2. Is any step structurally exclusive?** A step tied to one code path (e.g. a WebView-only
screen event) will exclude every user who took the other path, *before* any real drop-off is
measured. This can turn a true 26% into a reported 9%. Check what code path each event fires
from, not just its name.

**3. Is a step really a screen-load?** Screen-render events at the top of a funnel make step 1 →
step 2 look catastrophic when the drop is definitional. Say so rather than inheriting it.

**4. Does it chain an identified step to a pre-auth step?** Pre-auth events have no user id. A
funnel that windows across that boundary reports a false collapse — ~13% against a true ~95% is
a real case.

**5. Is it counting events where it means users, or the reverse?** Behaviour charts in particular
default to event counts.

**6. What layer is it reading?** A business-metrics dashboard usually reads the ledger; a
switch-level chart reads upstream. Numbers from the two are not comparable and must not be
reconciled by subtraction.

## Then decide: adopt, adapt, or supersede

For every metric the reference dashlet also covers, make an explicit call and record it in the
Definition Registry:

- **Adopt** — the reference definition is sound and already in use. Match it exactly, including
  its quirks, and note in the Registry that it is inherited. Consistency with what people quote
  beats a marginally better definition.
- **Adapt** — the intent is right, the mechanics are flawed (wrong window, event-count instead
  of users). Fix it, and put both numbers on the page or in the doc so the change is visible
  rather than surprising.
- **Supersede** — the reference is measuring the wrong thing. You must then (a) state the old
  number, (b) state yours, (c) explain the difference in one sentence a non-analyst can repeat.
  Never supersede silently.

**Never let a reference dashlet dictate the funnel shape.** Derive the ladder from the transition
matrix, then compare. If they disagree, that disagreement is itself a finding — usually the
reference was built from a spec doc rather than from the data.

## Useful source tables the reference dashboard points at

A reference dashboard's greatest value is often not its numbers but its **table references**. If
someone has already built a business-metrics dashboard, it tells you which table the organisation
treats as the source of truth for spend, accounts and transactions — which is exactly the
question Phase 1 has to answer. Read its chart definitions for the datasource before profiling
tables blind.

On the same instance this is free: `GET /api/v1/dashboard/{id}/charts` gives you every datasource
id, and `GET /api/v1/dataset/{id}` gives you the SQL those datasets run. Do it for every sibling
dashboard before you profile a single table.

## Which third parties are in the flow — answer it, don't just ask it

Every playbook asks which third parties sit in the journey — identity/KYC, bank connection,
payments PSP, fraud engine, device/risk. The question is asked constantly and answered nowhere, so
half the vocabulary on a dashboard reads as noise. Reference dashboards are where the answer
usually is: vendors surface as decline categories, bucket labels, state literals and metric name
fragments, and often in a sibling dashboard's *title*.

Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/inventory.md`.

Name them in titles and docs — if the PSP has a name, write the name, not "the PSP". And record the
negative findings too: a vendor that is in the estate but absent from every dataset is either a
coverage gap or a deliberate scope boundary, and someone should say which. A vendor that appears
in older documentation and is not evidenced anywhere in the live state does not go on the page.
Do not repeat a vendor name you cannot point at a column, literal or dashboard title for.

## Reviewing the CDP specifically

Second in priority to the same-instance sweep above, but still mandatory where CDP funnels
exist — it is the only place some of these numbers live, and it is where the number leadership
quotes most often comes from.

Most CDPs have no usable read API for this; use the Chrome path. The browser mechanics are out of
scope for this package, but the list is short: open each funnel's configuration and read the
ordered steps, the window duration, the analysis type and the granularity; where the rendered page
hides a setting, read it out of the front-end state rather than guessing it; and move between
funnels without reloading, because a single-page app will throw a `beforeunload` dialog and lose
the configuration you were mid-way through capturing.

For review purposes you need, per funnel: the ordered step list with exact event names, the
window, the analysis type, the granularity, and any segment filter. Capture it as text; a
screenshot is not enough to reconcile from.

## Output of this phase

A short **reference review note**, delivered to the user before you build:

1. One row per reference dashlet — **including every sibling dashboard on the same instance,
   with id and slug** — covering what it claims, what it actually measures, and whether it is
   healthy. A sibling you chose not to decode is a listed open item, not an omission.
2. Any broken/renamed/never-firing events found — these are engineering asks regardless of what
   you build.
3. The adopt / adapt / supersede call per metric, with reasoning.
4. The one number leadership quotes, and whether you will match it.

Get agreement on this note before designing the storyboard. It takes one round and removes almost
all of the "why doesn't this match" risk from launch.
