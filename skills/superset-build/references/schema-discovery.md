# Schema discovery for a tenant you haven't seen


## Step 0 — Environment and schema provenance (before anything else)

Guardrail G10. **UAT and production look identical in every tool**, and a suite built on UAT
reconciles against itself perfectly — so no gate downstream will catch it.

**Confirm with the user, then verify empirically:**

| What | Ask | Verify by |
|---|---|---|
| CDP workspace / app id | "Is this UAT or production?" | Volume and recency of a known campaign or event |
| Superset database connection + id | "Does this connection point at prod?" | One instance can carry both — check the connection, not the hostname |
| Schema set + tenant id | "Which schemas, and which tenant id?" | Row counts, min/max timestamps |
| **The decider** | — | **Reproduce one number the business already quotes.** If the source can't, you are on the wrong one |

Never infer the environment from a name. Both environments are normally named after the product.

### The same data in more than one schema

Common, and the most expensive thing to get wrong late. For every candidate table name, list
**every** schema that contains it:

```sql
select table_schema, table_name
from information_schema.tables
where table_name in (<candidates>)
order by 2, 1;
```

Then, before choosing:

1. **Profile each candidate** — row count, distinct entity count, min and max timestamp, freshness.
2. **Put them to the user side by side and ask which is authoritative.** One message; it saves a
   rebuild. Do not pick the fullest, the newest, or the one with the tidiest name.
3. **Triangulate** — count the same entity in each and report the deltas. Equal counts mean the
   choice is low-risk. Unequal counts mean these are not copies, and the difference is a finding
   before it is a decision.
4. **Record the choice, the rejected alternatives and the delta** in the Definition Registry.

Ship environment and schema provenance in the companion doc and on the dashboard header.

---

The goal of this phase is to be able to say, with evidence: *this is the entity, this is its
grain, this is the real stage ladder, these are the columns that lie.* Assume nothing carries
over from another tenant except the shape of the questions.

## Step 1 — What can this user actually see

```sql
select table_schema, table_name, count(*) as cols
from information_schema.columns
group by 1,2 order by 1,2;
```

Then narrow to schemas that look tenant-relevant. On a card programme the recurring families are:

| Family | Typically holds | Shape to look for |
|---|---|---|
| Core service / CDC schema, usually per product and per tenant | Service-of-record CDC / audit trails — repayments, mandates, config changes | `<product>_core_service_<tenant-id>` with `*_audit` tables |
| Ledger schema | Account × day facts. **Downstream and usually the source of truth** for spend | A package or account-base fact table, one row per account per day |
| BI schema | Pre-aggregated BI tables, often with `time_period` rollup rows mixed in | An auth or spend base table carrying rollup rows; filter to `DAY` |
| Event-stream export, often exposed twice in two schemas | App + web event export (see the event-stream section below) | A raw events table and a curated subset — **prove which is which** |
| Origination / decisioning vendor schema | Application, quotation and decision records | Application and quotation tables keyed on the vendor's own id |

Names vary completely between deployments — the tenant id, the product prefix and the vendor all
change every time. Confirm each one empirically before building on it. Treat the right-hand column
as a shape to recognise, never a list to copy: a schema that matches a familiar name but not a
familiar shape is the trap this table exists to prevent.

### Enumerate the existing virtual datasets too

`information_schema` does not know about them. **A prior build's virtual datasets are part of the
schema surface** — they encode which tables the organisation already treats as the source of
truth, and which definitions are already in circulation.

```
GET /api/v1/dataset/                     → every dataset on the instance, id and name
GET /api/v1/dataset/{id}                 → sql, metrics[], columns[], main_dttm_col, cache_timeout
```

On one engagement all eight live datasets are `schema=public` virtual datasets whose "tables" exist nowhere
in `information_schema`. A discovery pass that runs only the query above would find none of them,
and would then re-derive from raw tables definitions that already exist — differently.

### Before you write "no raw source exists"

This is a claim that gets published in a caveat or a tenant vocabulary file and then has to be
walked back. It has happened: a tenant file stated "no raw response/processing code exists
anywhere on this instance" for the switch decline taxonomy, after a schema check that covered
only the two or three schema families already in use on the rest of the dashboard. The
per-transaction RC-code source was sitting one join away, in schemas that were never checked
because they were not the family already in use.

**Never conclude a raw/granular source doesn't exist from a partial search.** Before writing that
claim anywhere — a caveat, a tenant file, an answer to the user — do the exhaustive version:

1. Enumerate every schema the read-only user can see, not just the tenant-obvious family:
   `select distinct schema_name from svv_all_columns order by 1;` (Redshift) or
   `select distinct table_schema from information_schema.columns order by 1;` generically.
2. Grep the full schema list for the domain's likely nouns — for a decline/response-code search:
   `payment`, `message`, `auth%`, `response%`, `processing%`, `switch%` — not just the schema
   family already in use for other charts on the page.
3. For every schema that matches, list its tables and skim column names for the exact field
   you're looking for (a response/RC code, a processing code, a raw message body) before ruling
   it out.
4. Only after that sweep comes up empty may the claim say the source doesn't exist — and even
   then, phrase it as "not found in schemas X, Y, Z as of \<date\>" rather than an unqualified
   absolute, since a read-only role's visible schema set can itself be incomplete.

A wrong "doesn't exist" is worse than a slow search: it becomes a permanent caveat that blocks a
better rebuild until someone happens to re-check it by hand.

## Step 2 — Profile every candidate table

For each, get these in one query and record them:

```sql
select count(*)                              as rows,
       count(distinct <candidate_key>)       as distinct_key,
       min(<time_col>), max(<time_col>),
       sum(case when <join_key> is null then 1 else 0 end) as null_join_key
from <schema>.<table>;
```

Decisions this drives:

- `rows = distinct_key` → the key is the grain. Otherwise find the real grain before joining.
- `max(time_col)` → **freshness**. Compare across every table you intend to combine. A two-day
  lag on one table is the explanation for most "why don't these tie" questions.
- `null_join_key` → if this is material, the join is broken. Design a fallback path *and* a
  metric that counts how often the fallback fires.

### Rollup rows

BI tables often mix grains in one table via a `time_period` column (`DAY`/`WTD`/`MTD`/`YTD`).
**Filter to the atomic grain (`DAY`) or you will double count.** Check for this pattern in any
table with a period-like column before aggregating.

### Columns that lie

Run these two checks on every table you plan to use:

```sql
-- constant / never-populated columns
select count(distinct col_a), count(distinct col_b), ... from <table>;

-- columns that are secretly duplicates of each other
select sum(case when col_a <> col_b then 1 else 0 end) as differs from <table>;
```

Real findings this has caught: a "technical decline" counter that is zero across the entire
history; an "activation count" identical to transaction count on every row; failure-code and
failure-reason columns that are NULL on 100% of failures.

Each of these is a caveat to publish, not a column to quietly use.

## Step 3 — Derive the stage ladder from the data

Never hand-write the funnel order from a spec doc. Get it from the transitions.

```sql
select previous_state, state, count(*) as n
from <event_source>
group by 1,2
order by 1, n desc;
```

Read the matrix into a ladder, then check two things that break naive funnels:

**a) First-seen date per state.**

```sql
select state, min(evt_date) as first_seen, count(*) as n
from <event_source> group by 1 order by 2;
```

A state that only began being emitted part-way through your window **cannot be the funnel
entry** — using it silently truncates earlier cohorts. Pick the earliest state with continuous
coverage as the entry, and expose the newer one as a metric with a note.

**b) States that are perfectly coincident.** If `count(distinct entity where A) =
count(distinct entity where B)` and the sets are identical, the second state carries no
information. Drop it from the funnel rather than shipping a 100% step — or replace it with a
state from another source that genuinely sits between them.

Compare the **sets**, not just the counts. Two states with equal counts and different membership
are not coincident, and that is the case where the rule above would destroy real information.

> **A live case of exactly this, unresolved — do not assert either side.** A dataset keeps both
> members of two initiated/ongoing pairs **and** ships conversions between them. Either the
> pairs are not coincident — in which case the docs that call them coincident are wrong — or
> the build is violating this rule twice. Run the set comparison. `qc-protocol.md` Gate 2
> carries the same open question; live state is in
> `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

Then **show the ladder back to the user and get confirmation before building.**

### Write the derived answer down — immediately, not at the end

This step is the expensive one, and its output is currently the thing most likely to evaporate.
**The moment you have it, the derived ladder, the event inventory and every bucket vocabulary go
into `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/journeys.md`, verbatim and in order.** Not into a chart's SQL, not into the
session, not into a summary. If it only lives in SQL, the next session re-derives it — and
re-derives it differently, which is worse than not having it.

What gets written:

| Artefact | Form |
|---|---|
| Backend stage ladder | Verbatim strings, in order, with the terminals listed separately |
| Terminal states and any LIKE patterns | Including what the pattern currently matches, with counts |
| FE event inventory | Every event name, and whether it is a funnel step or corroboration only |
| Every bucket vocabulary | Verbatim labels, including their ordinal/letter prefixes |
| Segment values | Verbatim, with what each one actually means |

The shape of the answer: typically **one backend event** carrying the whole stage ladder plus
its terminals, and a separate set of **FE event names** covering screen loads, OTP, auth
method, activation and the third-party journey launches. Derive both, list them verbatim, and
write them to `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/journeys.md` — read that file before
re-deriving anything for an engagement already onboarded.

Run step 3(a)'s first-seen/last-seen query across that inventory in writing. An FE event the app
renamed is a permanent zero on whatever chart depends on it, and nothing about the chart says so.

## Step 4 — Parallel routes and segments

Ask the transition matrix whether the population splits. Typical shape: one segment routes
through an extra verification stage and another skips it. If so:

- They are **not comparable products** and must not share a single funnel without a segment
  breakdown beside it.
- Each route gets its own sub-funnel with its own step list.
- The overall funnel keeps only steps that every route passes through.

## Step 5 — Nested payloads

Event stores commonly hold attributes in a `SUPER`/JSON column. Inspect before addressing:

```sql
select json_serialize(event.event_attributes) from <events> where <filter> limit 5;
```

Then write paths against what you actually saw. See `warehouse-gotchas.md` for the quoting and
null-handling rules — getting these wrong returns *zero rows with no error*, which is the worst
possible failure mode.

## Step 6 — CDP export specifics (when present)

Where the tenant has a CDP export, treat it as a corroborating source, not a spine.

- `raw_events_data` — full export; `event` is a `SUPER` column. Inside it: `uid`, `event_name`,
  `event_time` (epoch seconds), `event_uuid`, `event_source`, `event_attributes`,
  `user_attributes`, `device_attributes`.
- **Identity:** `nullif(event.uid::varchar,'')`. Pre-auth events carry an **empty string**, not
  null. Counting distinct on the raw column collapses every anonymous user into one.
- **Time:** `timestamp 'epoch' + event.event_time::bigint * interval '1 second'` plus the
  tenant's offset — for example `+ interval '5.5 hours'` (IST). **Never `export_day`** — that is
  the export batch date and carries backfill. The offset is not a formatting detail; see Step 7
  and `warehouse-gotchas.md`, "Timezone offsets and cohort boundaries".
- **Freshness:** the export trails the live CDP by hours. Treat the current day as partial and
  close reporting on the last complete day.
- A separate web/analytics schema may exist with a small set of journey events; check whether
  it contains the backend onboarding event before relying on it (often it does not).

## Step 7 — Establish the timestamp convention explicitly

Do this as a named step with a written answer, not as a side effect of writing the first query.
Three questions, and all three go in the tenant file:

1. **What is the epoch base and unit?** Seconds or milliseconds — a factor of 1000 that produces
   dates in 1970 or in the year 55000, both of which are obvious, and a factor you will still get
   wrong once.
2. **What offset is applied, in the SQL, right now?** Not what should be applied. Read it out of
   the dataset SQL and quote the literal.
3. **Does that offset match the product's market?** Ask it explicitly. If it does not, it is a
   caveat, and it is one that reaches a stakeholder.

An offset that disagrees with the market silently skews cohort and month boundaries against every
dataset that does not apply it, and the resulting gap looks like freshness lag rather than a
definition difference.

> **A live case where it does not match:** the epoch-based datasets in a suite apply
> `interval '5.5 hours'` (IST) on a UK/GBP product while the non-epoch datasets beside them
> apply nothing, so their months do not line up and a cross-dataset monthly comparison is not
> like-for-like. Consequences and the QC treatment: `warehouse-gotchas.md`, "Timezone offsets
> and cohort boundaries". Live state is in
> `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

## Step 8 — Write it down

Everything above goes into the Definition Registry and the caveats list as you find it, and the
derived vocabularies go into `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/journeys.md` per Step 3. The discovery output is not
"I now know the schema" — it is a written artefact the user can challenge, and the next session
can diff rather than re-derive.
