# Warehouse gotchas (Redshift / SUPER / event exports)

Each of these has cost real debugging time. Most fail **silently** — zero rows, a null column,
a plausible-but-wrong number — which is why they are worth memorising rather than rediscovering.

## Redshift SQL

**`ts` is a reserved alias.** `select ... as ts` throws `syntax error at or near "ts"`. Use
`evt_ts`, `event_ts`, anything else. Same caution for `timestamp`, `date`, `year`, `user`.

**`MEDIAN` cannot be combined with `COUNT(DISTINCT)` in the same aggregation.** The query errors
at execution, not parse time, so it survives into a chart. If your dataset is already one row
per entity, use `COUNT(*)` instead of `COUNT(DISTINCT id)` and the conflict disappears.

Confirmed in use: on one engagement a dataset carries `median_mins_to_signin` and is one row per
user — which is exactly why the metric is expressible at all. Collapsing to entity grain in the
dataset is not only a performance move; it is what makes `MEDIAN` legal.

**`PERCENTILE_CONT` is a window function here**, not a plain aggregate. Wrap it:
`select distinct percentile_cont(0.9) within group (order by x) over ()`.

**Integer division truncates.** Always `1.0 *` the numerator on a rate.

**`NULLIF` the denominator on every rate.** A zero-population cohort otherwise kills the whole
chart, not just one cell.

## SUPER / nested columns

**camelCase keys must be quoted, or they silently return NULL:**

```sql
event.event_attributes."accountId"::varchar        -- correct
event.event_attributes.accountId::varchar          -- returns null, no error
provider_details."mandateType"::varchar            -- correct
```

This is the single most expensive trap in the list: the query runs, returns rows, and every
value is null — which looks like "the field isn't populated" rather than "I addressed it wrong".
Confirm with `json_serialize()` before trusting an empty result.

**`json_extract_path_text` throws on the string `'null'`.** Guard it:

```sql
case when json_serialize(x) = 'null' then null
     else json_extract_path_text(json_serialize(x), 'key', true) end
```

**Always cast** (`::varchar`, `::bigint`) when pulling a scalar out of `SUPER`. Comparisons
against an uncast `SUPER` value behave unpredictably.

**Never `SELECT *`** from a table with a `SUPER` column via the API — the response payload
explodes and gets truncated.

## Event-stream semantics

**Empty string is not null.** Pre-auth / anonymous events carry `uid = ''`. Wrap every identity
column in `nullif(col,'')` before counting distinct, or all anonymous traffic collapses into a
single phantom user.

**Epoch, not the export date.** Derive time from the event's own epoch field plus the tenant's
offset. Export/batch date columns carry backfill and will misattribute cohorts. Which offset,
and whether it is the right one, is the next section — get it wrong and every cohort is shifted
by a fixed amount that no reconciliation will surface as an error.

**A prefix match on a status column is a column that lies in waiting.** `status like 'Referred%'`
collapses every `Referred *` variant into one bucket, and it will keep doing so silently when the
upstream service adds `Referred_Manual` next quarter — no error, no row-count change, a bucket that
quietly grows. On one engagement a dataset does exactly this for its `Referred` terminal, and it
is a standing open item.
Where you must prefix-match, enumerate the matched values with counts and first-seen dates at
build time, ship the enumeration in the companion doc, and re-run it each session.

**Take the last value, not the max.** For an attribute that changes over an object's life
(channel, rail, status), `max()` picks alphabetically or numerically, which is meaningless.
Use the most recent non-null:

```sql
with last_val as (
  select id, attr from (
    select id, attr, row_number() over (partition by id order by insert_timestamp desc) rn
    from audit where attr is not null) q
  where rn = 1)
```

This matters wherever a fallback exists — e.g. a mandate attempted on one rail that falls back
to another. The object should be counted under its **final** rail, and the fallback rate itself
is a metric worth exposing.

## Timezone offsets and cohort boundaries

Epoch conversion needs an offset, and the offset is a modelling decision, not a formatting one.
**Establish it explicitly per tenant, write it down, and check it against the product's market.**

```sql
timestamp 'epoch' + event.event_time::bigint * interval '1 second'
  + interval '5.5 hours'          -- e.g. IST, on a UK/GBP product. See below.
    as evt_ts
```

**This happens for real: on one engagement two datasets convert epochs with `interval '5.5 hours'`
— IST — on a UK/GBP product.** Three consequences, all of which belong on the dashboard as a caveat:

| Consequence | Why it bites |
|---|---|
| A UK event between 00:00 and 05:30 lands in the **previous** IST day's cohort | Every daily series is shifted for a 5.5-hour slice of traffic. Nothing errors |
| Month boundaries on the epoch-converting datasets are offset from those whose sources are not epoch-based | **A cross-dataset monthly comparison is not like-for-like.** This is the one that reaches a stakeholder |
| `pct_same_day` and `median_mins_to_signin` on such a dataset become same-***IST***-day measures | The highest-consequence instance: a same-day rate that means "same day in a timezone the user does not live in" |

> **Do not let this pass a QC gate as a freshness tolerance.** An offset skew presents as a small
> percentage gap between two datasets, which reads exactly like lag. It is not lag: lag closes,
> an offset does not. It is a definition difference and it blocks the comparison until it is
> named. `qc-protocol.md` Gate 4, tolerance bands.

Either the offset is a deliberate "report in the operating team's local business hours" choice — in which case
say so on the dashboard, in words, next to the date filter — or it is a defect. Log it as an open
item; it is not yours to resolve silently.

## Currency and minor units

**Convert from minor units in the dataset, never in the chart.** A chart-level `/100` is invisible
to the next person, survives no copy-paste, and is wrong the moment someone adds a second metric.

**One notation per surface, consistent within it.** Pick `GBP` or `£` for a given surface and
hold it. One engagement mixes them: a dataset's bucket labels write `GBP 50` / `GBP 200` /
`GBP 500`, while the prose around the same numbers writes `£`. Bucket labels are dimension values and are
read alongside each other, so consistency inside the bucket set matters more than consistency
with the prose beside it — but state the currency and the unit in the chart title either way, so
neither surface has to carry it alone.

## Joining across layers

**Never add a number from an upstream table to a number from a downstream one.** They are
different populations at different points in a chain. Model the chain explicitly (see
`${CLAUDE_PLUGIN_ROOT}/skills/transactions-spends/SKILL.md`) rather than reconciling by subtraction.

**Compute deltas per day and floor at zero** when differencing two feeds with different lags.
Netting across days produces negative "losses" and destroys the reader's trust in the page.
Where the downstream feed leads the upstream one on some days, surface that as its own labelled
row rather than hiding it.

**Broken join keys are common.** When a link column is null on a material share of rows, check
whether a second key (a borrower id, a device id, an account id) can recover the link. If it
can, implement the fallback *and* a metric counting how often it fires, named after the key that
rescued it — on one engagement that metric is `resolved_via_customer_id`. Then **report the trend**: a link
whose breakage rate moves materially month over month is a live incident, not a quirk, and the
metric is worthless if nobody charts it.

> The failure mode seen in the wild: the fallback metric ships but **no link-health dashlet**
> does, so the metric exists, nothing reads it, and the trend nobody is watching is invisible.
> Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## Grain discipline

- Check `count(*) = count(distinct key)` before treating a column as the grain.
- Filter rollup tables to the atomic period (`DAY`) before aggregating.
- A distinct-count metric is **not additive across dimension rows.** A month-wise table keyed on
  one date and counting distinct entities dated another will have rows that sum past the total.
  That is correct behaviour — but say so in the doc, or re-key the dimension to the entity's own
  cohort date if additivity matters more.
- Attributes recorded at day grain (flags on an account × day table) cannot be used as
  customer-grain attributes. This produces confident-looking segmentations that mean nothing.

## Join direction and the driving table

**The table you read FROM decides which rows can exist. A join can only ever remove rows from it,
never add the ones that were never there.**

This is the highest-consequence structural defect in this file, because it produces a dataset that
is internally consistent, reconciles against itself perfectly, and is quietly missing a fifth of
its population.

**The pattern.** A fact table (the events) is enriched by a message/log/vendor table (a few extra
attributes). Someone writes it as `FROM enrichment e LEFT JOIN fact f` because the enrichment
table was where they found the attribute they needed. Now any fact row with no enrichment row is
not "unmatched" — it is **absent from the driving set entirely**, and no LEFT JOIN anywhere can
bring it back.

**Why it is dangerous rather than merely wrong: the loss is rarely random.** The rows that fail to
produce an enrichment record are usually the ones where something went wrong — timeouts, system
malfunctions, aborted flows. So the missing population correlates with the failure mode the
dashboard exists to measure. In a worked case, 21% of declines were missing overall but **94% of
system-malfunction declines** were, and a whole production incident was invisible.

**Rules:**

- **Drive FROM the grain you are reporting on.** If the dashlet counts authorisations, read from
  the authorisations table. Enrichment tables are joined *to*, never *from*.
- **Enrichment must be optional.** If the attribute is missing, derive it another way or label it
  — never let its absence delete the row.
- **Check both directions before you trust a join.** Count rows on each side, count matches, and
  report both unmatched rates. One of them is usually a finding.

### A WHERE predicate on the right table silently turns LEFT JOIN into INNER JOIN

```sql
FROM a LEFT JOIN b ON b.k = a.k
WHERE b.tenant_id = '<tenant-id>'  -- ← every unmatched row has NULL here and is dropped
```

The join reads as LEFT and behaves as INNER. Predicates on the right table belong **in the ON
clause**, or inside a subquery that filters `b` before the join. Predicates on the driving table
belong in WHERE.

This one is doubly nasty because it can cost **zero rows today** — if every row happens to match
the predicate — and start deleting data the moment a new value appears. Test it by moving the
predicate and comparing counts; if the counts differ, it was never a LEFT JOIN.

### Duplicate join keys fan out counts *and* money

A join key that is not unique on the right multiplies rows. Symptoms: a total larger than the
source table's row count, and monetary sums inflated by more than the row inflation (because the
duplicated rows are not a random sample of value).

- **Check before joining:** `count(*)` vs `count(distinct key)` on the right table.
- **Fix by pre-aggregating** to one row per key in a subquery, not by `DISTINCT` on the result.
- **When you pre-aggregate an amount, verify the choice matters:** count keys with more than one
  distinct value for that column. If it is a handful with a trivial spread, `MIN`/`MAX` is safe
  and you can say so. If it is many, the column is not a per-key attribute and needs a rule.
- Removing a fan-out **reduces published figures**. That is a correction, not a regression — but
  state the old value, the new one, and the row count that caused it, or it reads as a bug.

## Decoded labels versus raw codes

**A column named for a code may contain the decoded description of that code.** Two tables carry
"the processing code": one holds `000000`, the other holds `Goods/Service Purchase`. They are the
same fact in different alphabets.

Applying a documented business rule literally — `WHERE processing_code = '000000'` — against the
decoded column **matches nothing, raises no error, and silently undercounts** the category the
rule defines. In a worked case this understated one decline class by 27%.

- Before using a code column in a rule, **look at its distinct values**. Codes and prose are
  obvious on sight and impossible to spot in a column name.
- Where both spellings exist, **derive the mapping empirically** by joining the two and grouping —
  do not assume the obvious pairing.
- A verified label↔code mapping is often the thing that lets you **drop a fragile join entirely**,
  because the decoded column already carries what the join was fetching.
- Record the mapping in the Definition Registry. It is the sort of fact that gets re-derived
  differently by the next person.

## Duplicate rows in an "immutable" event table

Fact tables that look append-only still carry duplicates. Check `count(*)` against
`count(distinct id)`, and then check whether the duplicates are byte-identical or genuinely
distinct messages that reuse an id.

Report the impact **on the metric that matters**, not in general: duplicates concentrated in
successful rows do not affect a failure count, and saying so precisely is worth more than a
blanket warning. Never silently de-duplicate a source table you do not own — measure it, state
it, and let the owner decide.
