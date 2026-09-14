# Query optimisation across a dashboard suite

A dashboard is not one query, it is N queries fired at once on every load, plus N more each
time a filter changes. The default failure mode is eighteen dashlets each re-scanning a raw
event table. Optimise at the *suite* level, not the chart level.

## The core pattern: collapse the event stream once

**Bad:** every chart contains its own SQL over the raw event table, each re-parsing `SUPER`
payloads across tens of millions of rows.

**Good:** one virtual dataset per journey that collapses the stream to **one row per entity**,
with a boolean flag and timestamp per stage. Charts then aggregate a narrow table.

```sql
with e as (                       -- parse SUPER once
  select nullif(event.uid::varchar,'')                            as uid,
         event.event_attributes."objectId"::varchar               as entity_id,
         event.event_attributes."objectStatusName"::varchar       as state,
         timestamp 'epoch' + event.event_time::bigint * interval '1 second'
           + interval '5.5 hours'                                 as evt_ts
           -- ^ the tenant offset. On one engagement this was IST on a UK
           --   product: a modelling decision with cohort-boundary consequences,
           --   not a formatting one. See warehouse-gotchas.md, "Timezone offsets
           --   and cohort boundaries", before copying it to another tenant.
  from <events>
  where event.event_name::varchar = '<journey-event>'
),
agg as (                          -- collapse to entity grain
  select entity_id,
         min(evt_ts)                                              as cohort_ts,
         max(case when state = 'Started'  then 1 else 0 end) = 1  as f_started,
         min(case when state = 'Started'  then evt_ts end)        as t_started,
         ...
  from e group by 1
)
select a.*, date_trunc('month', a.cohort_ts) as cohort_month, d.segment, d.decline_reason
from agg a left join <decision_table> d on d.id = a.entity_id;
```

Payoffs beyond speed: the funnel is monotonic by construction, cohort-dating is free, and every
chart shares definitions because they share columns.

## Rules

**1. Metrics live on the dataset, not the chart.** Ad-hoc chart metrics are how two dashlets end
up with two definitions of the same number. Dataset metrics are also cached per dataset.

**2. Set `cache_timeout` on the dataset.** One value serves every chart on it. Match it to the
source's refresh cadence — a table that loads daily does not need a 60-second cache.

**3. Set `main_dttm_col`.** The global time filter binds to it, and Superset can push the range
into the virtual dataset's outer query. Without it, filters degrade into post-aggregation
filtering.

**4. Cohort-date, don't event-date.** Storing one `cohort_ts` per entity means a date filter
selects whole funnels. Event-dating forces each chart to re-derive the cohort and splits funnels
across period boundaries.

**5. Pre-compute the buckets.** `outcome_bucket`, `stage_reached`, `last_stage`, lag buckets,
channel — all in the dataset SQL as columns. A `CASE` ladder evaluated once per entity beats the
same ladder evaluated in six charts.

**6. Keep the dataset narrow.** Booleans and timestamps, not payload blobs. If a column is only
needed by one detail table, consider a second small dataset rather than widening the shared one.

**7. Split datasets on layer, grain and date semantics — then reconcile the overlaps.** Reuse a
dataset wherever two dashboards genuinely want the same rows at the same grain from the same
layer; that is cheaper and safer. But reuse is not the top-level rule, and forcing it produces a
dataset that spans two layers, which is worse than two datasets that disagree. Per Phase 4 of
this skill — **one semantic dataset per journey × source layer × grain** — split when any
of these differ:

| Split on | Because |
|---|---|
| **Source layer** | A switch/auth table and a ledger table are different populations. A dataset spanning both is either a deliberate reconciliation dataset — name it so — or a bug |
| **Grain** | Account × day and account-lifetime are not one dataset, whatever they share |
| **Date semantics** | A view deliberately exempt from the global date filter (lifetime RFM) cannot share a dataset with a windowed one |

**Where two datasets legitimately derive the same data point, that pair goes on the Gate 3
reconciliation list. It does not get merged.** The correctness guarantee comes from a query that
asserts equality every session, not from a shared object.

Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/inventory.md`.

**8. Aggregate in SQL when exploring.** During discovery, never pull row-level data back through
the API to count it in JS. Return the aggregate.

**9. Row limits are a correctness issue.** A table viz with `row_limit` below the cardinality of
its groupby silently truncates and the totals look wrong. Set it above the real cardinality, and
check the cardinality first.

The exposure is always the detail tables — the drop-off, decline-reason, failure-segregation
and outcome-detail dashlets. List them per dashboard and audit their row limits in that order.
Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/inventory.md`.

**10. Watch filter fan-out.** A dimension filter targeting *n* datasets fires *n* distinct-value
queries on load. Target only the datasets that need it.

**Corollary, and it is a correctness rule not a performance one: a native filter must target
every dataset on the page, or it silently filters only some of them.** There is no error, no
warning and no visual cue — half the page moves and half does not, and the reader assumes both
halves cover the same period.

Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/inventory.md`.

**11. Pushing the timezone conversion into the dataset SQL has a cost.** When `main_dttm_col` is
bound to a *computed* timestamp — an epoch plus an interval, rather than a stored column — range
pushdown behaves differently: the optimiser has an expression to reason about rather than a
column, and the range predicate may not reach the scan the way it would on a raw column. Do the
conversion once in the collapsing CTE (the core pattern above already does), keep the column
in the outer select, and measure a date-filtered load before assuming the pushdown survived.

## When a dashboard is already slow

Diagnose in this order:

1. **Chart count × dataset count.** Many charts on one cached dataset is fine; many charts on
   many uncached datasets is not.

   Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/inventory.md`.

2. **Is any chart running raw SQL?** Move it into the journey dataset.
3. **Is `main_dttm_col` set on every dataset?** Missing one turns a pushdown into a full scan.
4. **Are detail tables unbounded?** Cap them and add a "top N shown" note rather than letting
   them fetch everything.
5. **Is a rollup table being scanned without its period filter?** That is a silent 4–5× scan.
