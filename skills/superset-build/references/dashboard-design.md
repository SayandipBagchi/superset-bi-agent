# Dashboard design: storyboarding, viz choice, nomenclature

## Storyboard first

Write the dashlet titles as a narrative before creating a chart. The test: reading the titles
top to bottom should tell the story without any numbers. If two adjacent titles don't have a
"which raises the question…" relationship, the order is wrong.

The arc that generalises across journeys:

| Position | Dashlet | Question it answers |
|---|---|---|
| 1 | Headline / population | How big is this, and what is the one rate? |
| 2 | The funnel | Where does the population go? |
| 3 | Sub-funnels by segment | Are we averaging two different products together? |
| 4 | Where it stops (stage × outcome) | Is the loss a decision or a behaviour? |
| 5 | Why it stops (reason per stage) | What is the actionable cause? |
| 6 | Cross-source check | Do the other sources agree? |
| 7 | Outcome of everyone | Is anyone unaccounted for? |
| 8 | Month-wise tables | Is it getting better or worse? |

Put a pre-funnel stage first when one exists (e.g. eligibility checks before applications) —
it usually reframes the whole dashboard, because the biggest loss is often *before* the funnel
everyone stares at.

## Viz choice

**Funnels: use a Table, not the funnel viz.** The ECharts funnel sorts by metric value, so any
tie or non-monotonic step silently reorders your stages. Build the horizontal box view instead:

- viz `table`, `query_mode: aggregate`, `groupby: []` (one row)
- metrics in step order, alternating count and conversion:
  `count → → % → count → → % → … → overall %`

This reads left to right like a funnel, preserves order absolutely, and puts conversion between
the counts it relates.

**Cross-tabs: pivot table.** Stage × outcome is the highest-value dashlet on most journey
dashboards and needs a pivot with totals on.

> **Prescribed, not built.** On at least one live suite no `pivot_table` chart exists at all, and
> the set-piece below about `stage_reached` × `last_stage` describes a dashlet that was **never
> built**. The prescription stands — it is the right dashlet — but check before writing as though
> it exists, and never cite it as an example a reader can go and look at. Where it is missing,
> log it: build it or descope it in writing. Live state is in
> `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.
>
> Nearest equivalent seen in the field: an `Outcome detail · by segment and last stage` table.
> It is a table of last stage by segment, not a stage × outcome cross-tab, and it does not carry
> totals.

**Distributions: bar, sorted descending, with the "no reason recorded" bucket kept visible.**
Do not hide unattributed volume — it is usually the finding. Use `bar` — a **non-time
distribution must not use a time-series viz**, which will try to order by a date it does not
have.

> **A defect found in the field:** an `Open Banking · drop-off reason` chart used
> `echarts_timeseries_bar` for a non-time distribution, while its Identity Verification twin
> (`Identity Verification · drop-off reason`) uses plain `bar`. Two sibling charts, same shape,
> two viz types. The rule is right; the build violates it.

**Donuts: only for outcome-of-everyone**, where the shares genuinely sum to 100% and there are
fewer than about seven slices. Concretely: `viz_type: pie` with `donut: true` in `params`, so the
prescription is checkable by API rather than by eye. Pair with a detail table.

**Trends: line for rates, bar for volumes.** Never dual-axis two things a reader might add up.

**Big number tiles:** reserve for the two or three figures the audience will quote. Everything
else is a table row.

## Layout

- 12-column grid. Full-width for funnels (they're wide by nature), halves for a bar + its detail
  table, thirds for tile rows.
- Markdown header rows to name sections — they cost nothing and make the storyboard legible.
- Global filters in the left rail, applied to every chart, with any deliberate exemption
  (e.g. an all-time RFM section) stated in that chart's title.
- Month-wise tables go at the bottom of their section, not interleaved with the funnels.

> **A defect found in the field:** on one dashboard the month-wise table sat **third of five**,
> between the funnel and the lag/drop-off analysis. A month-wise table interrupts the argument — it answers
> "is it getting better" before the reader has finished asking "where does it break".

## Nomenclature — standardise before you build

**No numeric prefixes on funnel step labels.** `1 · Application started` looks tidy on one
funnel and is wrong on the next, because the same metric sits at a different position in a
sub-funnel. Left-to-right order carries the sequence; every conversion column is `→ %`.

### Prefixes on dimension values are the house style

Not an exception — the convention. **Prefixes on dimension values, never on metric verbose names
or funnel step labels.** Table rows have no inherent order, so the prefix *is* the sort key; a
metric column already has its order from left to right, so a prefix there can only contradict it.

Two forms, both in force:

| Form | Use | Live examples |
|---|---|---|
| Ordinal — `0 ·`, `1 ·`, … | Buckets with a natural order: recency, frequency, monetary, lag | `1 · 0-7 days`, `3 · 15-30 days`, `0 · Before onboarding`, `8 · Not signed in` |
| Letter — `A ·`, `B ·`, … | Buckets with a deliberate reading order but no numeric meaning | `A · Signed in`, `B · Attempted, dropped before home screen`, `C · Never attempted sign-in`, `D · Signed in before onboarding completed (likely internal)` |

Use the letter form when a number would imply a magnitude or a step index the bucket does not
have. `D · Signed in before onboarding completed` is not the fourth step of anything; it is the
fourth thing you want the reader to look at.

Number from `0` when a "before the funnel" bucket exists, so the ordinary first bucket keeps
its intuitive `1`.

### ` · ` is the title separator

A middle dot with spaces either side separates a **section or qualifier** from its **subject**:

```
Month-wise · Mandates
RFM · headline
Sub-funnel · Approved (Open Banking route)
Authorisation chain · upstream → downstream → ledger
```

Qualifier first, subject second. It sorts every `Month-wise ·` chart together in the chart list
and tells a reader which section a chart belongs to when it is seen out of context — in a search
result, an alert, or a Confluence link. On one engagement roughly 30 of 51 live charts use it. Use a hyphen
or a colon for anything else and reserve ` · ` for this.

### Name the source in the title when more than one source is on the page

Name **both** the layer and the table: `(ledger: <ledger_fact_table>)`, `(switch: <auth_base_table>)`.

The layer alone (`(downstream, ledger)`) tells a stakeholder what it means but leaves an analyst
guessing which table to open. The table alone tells the analyst everything and the stakeholder
nothing — a raw table name is not a word. Suites in the field commonly use the table-only form,
`(source: <ledger_fact_table>)`; prefer the two-part form on new work. Also applies to `(backend)` vs
`(app-side)` where the split is instrumentation rather than layer.

Other rules:

- Use the tenant's vocabulary for stages, exactly as it appears in the data.
- Same data point → same words on every dashboard. "Spend-active accounts" is not "active
  spenders" on the next page.
- Verbose metric names are the column headers. Write them as they should read to a stakeholder,
  not as snake_case.
- Money: state the currency and unit in the title; convert minor units in the dataset, not the
  chart.

## Two columns you almost always need

- **`stage_reached`** — furthest stage reached, ignoring terminal outcome.
- **`last_stage`** — final resting state, where a terminal outcome outranks a stage label.

Funnel step loss and the "dropped at" bucket answer different questions, and the difference
between them is the decline volume. Shipping the cross-tab of the two pre-empts the most common
challenge you will get: *"the funnel says 81 didn't progress but the drop-off chart says 8"* —
because 73 were declined, and a decline is not a drop.

**Check whether that cross-tab actually exists before citing it** (see the "prescribed, not
built" note above). The example above is an illustration of the argument, not a description of a
shipped dashlet — a suite can carry a `last_stage` detail table and still have no `stage_reached`
dimension and no cross-tab of the two. Live state is in
`${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## Interpretation is part of the deliverable

Do not ship numbers without saying what they mean. On the dashboard, use markdown blocks
sparingly for the one or two structural facts a reader needs. In the companion doc, say plainly:
what the biggest loss is, whether it is behavioural or a decision, and what would have to change.

Behavioural losses (screen shown, user never acted) are UX problems. Decision losses (declined
on a rule) are policy problems. They go to different owners — always separate them.
