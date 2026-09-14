# Evals — run after every creation, and before every publish

The QC gates (in the superset-build SKILL.md) tell you whether *this* build is sound. Evals tell you whether it is still
sound **tomorrow**, after someone else edits a dataset, after the vendor changes a field, after
you fix something unrelated. Gates are a checkpoint; evals are a ratchet.

**Contract:**

- **Golden** and **Regression** suites run **after every creation and before every publish**, and
  again on any change to a dataset, chart, filter or layout. Any FAIL blocks publication.
- **Adversarial** runs before a first publish, before any leadership review, and after any change
  to a definition. A FAIL is not automatically blocking, but it must be answered in writing.
- Results ship in the companion doc as a dated table. **A suite that was not run is reported as
  NOT RUN, never as passed.**

Every test below is written as: what it asserts, how to run it, and what a failure means. Where a
test needs tenant-specific values, they live in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/`, not here.

---

# 1 · Golden tests

Fixed anchor values, agreed with the user, that must not move except for a reason you can name.
These are the numbers someone would quote in a review.

**How to build the set.** At first publish, pick 8–15 anchors spanning every dashboard: the
funnel entry, the funnel exit, one conversion rate, each reconciliation pair, the internal-user
share, and one figure per journey. Record value, query, and as-of date. **Freeze them at a fixed
window** (e.g. `cohort >= go-live and cohort < first-of-current-month`) so they do not drift with
new data — a golden test on an open-ended window tests nothing.

| Field | Example |
|---|---|
| Id | `G-03` |
| Assertion | Onboarding `Completed`, cohort Jul 2026, equals 123 |
| Query | `select sum(s_completed) from (<onboarding dataset sql>) z where cohort_ts >= '2026-07-01' and cohort_ts < '2026-08-01'` |
| Expected | `123` |
| Tolerance | exact |
| As-of | 2026-08-11 |
| If it fails | A closed month changed. Either a definition moved or the source was restated. Find which before publishing. |

**Rules.**

- Golden values on **closed periods** are exact-match. No tolerance band.
- Golden values on **open periods** are forbidden. If you want one, close the window.
- A golden test that fails is never "fixed" by updating the expected value. Update it only after
  writing down *why* it moved, in the changelog.
- Golden tests belong to the **tenant**, not the skill. Store them in the tenant file.

The shape of a golden set: one assertion per row with an id, the assertion in words and an
exact expected value or an equality/monotonicity relation — anchored on the first complete
post-go-live month. Live state is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/open-items.md`.

---

# 2 · Regression tests

Structural invariants. Tenant-independent — these run on **every** engagement, and each one
exists because something in this list has already gone wrong.

## 2.1 From the gates

| Id | Assertion | Failure means |
|---|---|---|
| R-01 | Every published metric maps to exactly one Definition Registry row | Untraceable number on a page |
| R-02 | No dataset retains Superset's default `count` | A metric with no definition |
| R-03 | Every funnel is non-increasing left to right | Definition error, not time travel |
| R-04 | No conversion metric sits between two states with identical counts | A 100% step carrying no information |
| R-05 | Every shared data point returns the same value on every dashboard, **by query** | Gate 3 failure |
| R-06 | Every dataset on a dashboard is a target of that dashboard's date filter | A filter that silently covers part of the page |
| R-07 | Every chart is associated to a dashboard **and** present in `position_json` | Chart exists, renders nowhere |
| R-08 | No dataset is referenced by zero charts; no chart sits on zero dashboards | Orphans |
| R-09 | No two charts on a dashboard share a concept **and** a source under different titles | The duplicate-chart trap |
| R-10 | Outcome buckets sum to the population; residuals are named | Unlabelled remainder |

## 2.2 From the guardrails

| Id | Assertion | Guardrail |
|---|---|---|
| R-11 | The running model is Opus 5 or Sonnet 5, and the fresh-invocation prompt fired | G1 |
| R-12 | No write of any kind was issued to the warehouse | G2 |
| R-13 | The reference-review note and the stage ladder were both confirmed by the user | G3 |
| R-14 | Every patched inconsistency has a metric counting how often the patch fired | G4 |
| R-15 | Every superseded reference number is stated old-vs-new in one sentence | G5 |
| R-16 | **Go-live date is recorded in writing**, `user_type` exists, filter defaults to Customer only, internal count is a visible metric | G8 |
| R-17 | **Every date-filter-exempt view has been checked separately for internal users** | G8 |

## 2.3 From documentation drift

| Id | Assertion | Failure means |
|---|---|---|
| R-18 | Every metric, column and bucket named in the docs exists live under that exact spelling | Doc drift |
| R-19 | Every dashlet the docs call essential either exists live or is listed as an open build ask | Asserting a chart that was never built |
| R-22 | Every cross-reference in the docs resolves: relative links to files that exist, `${CLAUDE_PLUGIN_ROOT}` paths to real skills, and no pointer to a file that was moved or deleted | Structural, run by `scripts/validate_skill.py` |
| R-20 | No two worked examples count the same population differently without stating why | The skill failing its own Gate 3 |
| R-21 | Every figure in the docs is older than, or stamped against, its dashboard's last-changed time | Stale numbers presented as fact |
| R-22 | **After any `PUT /api/v1/dataset/{id}/refresh`, re-assert R-02** | **Refresh silently re-adds Superset's default `count` metric.** Removing it must be the last step in any sequence that includes a refresh |
| R-23 | For every chart, the sum of its grouped rows equals the population named in its title | Chart-level filters quietly shrinking a total |
| R-24 | **Every chart on a dashboard shares the same population filter, or its title says why not** | Sibling charts silently answering about different populations |
| R-25 | Entities excluded by a population filter are counted by a named metric somewhere | Silent exclusion |
| R-26 | **The artefact register exists and every stage is reconciled PRD ↔ Design ↔ Events** | G9 — a funnel describing the instrumentation, not the journey |
| R-27 | **The feature availability matrix exists per module, with no assumed cells** | G9 — a ported feature set |
| R-28 | Every stage declares its instrumentation (BE / FE / both / neither); no stage silently absent | A funnel that implies everyone leaving step N reached step N+1 |
| R-29 | Every zero or 100% step is checked against feature flags and first-seen dates before being reported as drop-off | Unfired events reported as user behaviour |
| R-30 | **The environment is recorded — CDP workspace UAT/prod, Superset connection, schemas with tenant id** | G10 — a suite built on UAT reconciles against itself perfectly |
| R-31 | **A number the business already quotes has been reproduced from the chosen source** | The only test that settles the environment question |
| R-32 | For every data point available in more than one schema: choice, rejected alternatives and count delta are recorded | Silent schema selection |
| R-34 | **Every date-filter-exempt dataset has `main_dttm_col` explicitly null** | Superset assigns one on its own; the date filter then binds to a view that must not be filtered |
| R-35 | **Every window function is partitioned by every dimension a chart filters on** | Precomputed ranks re-sliced by a chart filter. Assert the last decile's cumulative share is exactly 100.0% |
| R-36 | **Every API-created chart has a saved `query_context`** | Without it Gate 3 cannot be run by query, and thumbnails break |
| R-37 | **Every aggregate-mode table that needs a dimension order sorts by a sort metric, not `order_by_cols`** | `order_by_cols` is ignored in aggregate mode; the table renders shuffled |
| R-38 | **Any modified dataset that was not authored by this agent has a `zz_backup_*` copy of its original SQL** | Dataset SQL has no version history |
| R-39 | **Every population exclusion is counted by a visible metric and every step of the chain is named** | An unexplained delta against a sibling dashboard |
| R-33 | Environment and schema provenance appear on the dashboard, not only in the doc | A reader who cannot tell which environment produced the number |

---

# 3 · Adversarial tests

Written from the position of someone trying to make the dashboard wrong. Run these before a
leadership review. **Each is phrased as the question a hostile reviewer asks.**

## 3.1 Population attacks

| Id | The attack | What it catches |
|---|---|---|
| A-01 | "Is anyone in here who isn't a customer?" | Internal/staff/test users — on one engagement 20% of transactions. Check the date-exempt views separately |
| A-02 | "What's the earliest row in each source, and does the dashboard say so?" | Coverage-window differences masquerading as data-quality gaps |
| A-03 | "Show me the same number on the other dashboard, right now, same filters" | Definitions that drifted between dashboards |
| A-04 | "Which of these two numbers does leadership already quote, and does yours match?" | Silent supersession |
| A-05 | "Add up your buckets. Do they equal the total?" | Unlabelled residuals |
| A-06 | "Can one person appear twice?" | Entity-grain errors in user-keyed funnels |

## 3.2 Source and field attacks

| Id | The attack | What it catches |
|---|---|---|
| A-07 | "When did each state **first appear**? Not the earliest row — the earliest row *of that value*." | A state introduced mid-stream used as a funnel entry. Cost us `f_created` |
| A-08 | "Is this field an array? Are you reading element 0 only?" | A flattened `<reason_array>_0` column read as *the* reason: 29% of declines carried an empty array, so element 0 was NULL and the reason was simply absent |
| A-09 | "Does this column mean what its name says?" | `approval_status` is the **soft-eligibility** decision — 22 declines against 386 real ones |
| A-10 | "Is this table one row per entity?" | `<origination-vendor>.applications`: 6,380 rows for 1,240 applications. Naive count overstates 5× |
| A-11 | "Does this table mix grains?" | `auth_rollup_base` carries DAY/WEEK/WTD/MONTH/MTD/YEAR/YTD. Omitting the filter multi-counts ~7× |
| A-12 | "What units? Both sides?" | Switch in GBP, ledger in pence. Dividing both by 100 is a 100× error |
| A-13 | "Does a LIKE or prefix match hide anything?" | `Referred%` was absorbing six variants, newest five days old |
| A-14 | "What happens to NULLs in the date column?" | 8 ledger rows vanished from every month table |
| A-15 | "Is this a rollup table with totals rows?" | Double counting |
| A-16 | "Show me the join key null rate." | Silent inner-join loss |

## 3.3 Time attacks

| Id | The attack | What it catches |
|---|---|---|
| A-17 | "Is 'July' the same 31 days on every dashboard?" | Timezone offsets applied to some datasets and not others |
| A-18 | "What's the refresh lag of each source on this page?" | Fresh numerator over stale denominator — on one engagement, T-0 switch vs T-3 ledger |
| A-19 | "Is the most recent period complete?" | Partial-period figures read as a decline |
| A-20 | "Is this date default a stale literal or a meaningful anchor?" | **Ask before 'fixing' it.** On one engagement the stale-looking literal was the go-live date, not rot |
| A-21 | "Does the date filter reach the views that are exempt from it?" | Lifetime RFM was 100% contaminated |

## 3.4 Object-inspection attacks

Cheap, and each one has produced a wrong conclusion in this skill's own history.

| Id | The attack | What it catches |
|---|---|---|
| A-22 | "Did you read `params`, or `form_data`?" | They disagree. `params` is truth for viz type and metrics |
| A-23 | "Did you read `position_json`, or the order `/charts` returned?" | `/charts` returns creation order. **Only `position_json` describes layout** |
| A-24 | "Is this metric actually used by any chart?" | Orphan metrics that look like part of a funnel and are not |
| A-25 | "Did you verify after the write, and again after a reload?" | Charts that save but never render |
| A-26 | "Do you own the object you are about to change?" | 403s discovered mid-change. Check before planning a delete |
| A-31 | **"Is there a chart-level filter excluding the very rows you are trying to count?"** | The decline-reason dashlet carried `decline_reason <> '(none)'`. Regrouping and re-labelling changed nothing until that filter came off — the exclusion was in the chart, not the data. **Always read `adhoc_filters` before diagnosing a missing population** |
| A-32 | "Does the chart total equal the population it claims to describe?" | A chart headed 'decline reasons' that sums to less than declines. Assert the total, not just the buckets |
| A-33 | **"Are all charts on this dashboard scoped to the SAME population?"** | One chart missing the funnel's population filter disagrees with every sibling. On one dashboard five charts carried `s_started=1` and the decline-reasons chart did not — 243 vs 259. **List every chart's filters side by side; the odd one out is the bug** |
| A-34 | "Where do the entities excluded by the population filter go?" | Excluding is fine; losing them is not. The 16 declined-before-start needed their own metric, not silence |
| A-35 | **"Is this step zero because nobody reached it, or because the feature is switched off?"** | Built-but-not-launched. Unfired events look like steps nobody reached, so the error always flatters the product |
| A-36 | **"Show me a stage in the PRD that has no event."** | Instrumentation gaps. The funnel skips them silently and the previous step's exit reads as the next step's entry |
| A-37 | **"Which of these features does this engagement actually have?"** — go through the repayments list rail by rail | A ported feature set. Rails, PSP, autopay, one-off, retries and returns are all optional |
| A-38 | "Which artefact is most current — the PRD, the design, or the events?" | Reconciling to a stale spec. The design is usually newer than the PRD |
| A-39 | **"Is this production?"** — then: "prove it without using the name" | UAT. Both environments are named after the product, and UAT reconciles against itself perfectly |
| A-40 | **"Does this table exist in another schema too? What does the count say there?"** | Silent schema choice. Unequal counts mean the schemas are not copies |
| A-41 | "Reproduce a number leadership already quotes, from this source." | The single decisive environment and schema check |

## 3.6 Entity-grain and structural attacks

Added v2.11.0. Every one of these caught a live defect.

| Id | The attack | What it catches |
|---|---|---|
| **A-42** | **"How many *customers* is that, not how many events?"** | An event count read as a population. The ratio is routinely 4-6x. If the dashboard cannot answer, the metric is not actionable -- see `${CLAUDE_PLUGIN_ROOT}/skills/concentration-analysis/SKILL.md` |
| **A-43** | **"Which table does this query read FROM?"** | Join-direction inversion. Driving from the enrichment table instead of the fact table silently deletes rows that never had an enrichment record -- and those rows correlate with failure, so the loss is biased toward whatever the dashboard exists to measure |
| **A-44** | **"Is there a WHERE predicate on the right-hand table of that LEFT JOIN?"** | A LEFT JOIN that behaves as INNER. Can cost zero rows today and start deleting data the moment a new value appears |
| **A-45** | **"Is the join key unique on the right?"** | Fan-out. Inflates counts, and inflates money by more than it inflates rows |
| **A-46** | **"Does this column hold the code, or the decoded description of the code?"** | A documented rule applied literally against a decoded label matches nothing, errors nowhere, and undercounts the category it defines |
| **A-47** | **"Was this ranked before or after the chart's filter was applied?"** | Precomputed `NTILE` / `ROW_NUMBER` / running `SUM` over a population a chart then filters. The Pareto is plausible and wrong. Tell: the last decile's cumulative share is not exactly 100.0% |
| **A-48** | **"When did this value FIRST appear -- and is it all on one day?"** | A-07's sharper form. Clustering by first-seen date turns a "data quality gap" into an **incident**: 72 of one code, all inside 5.5 hours on one date, was an unreported outage nobody had escalated |
| **A-49** | **"This patch fixes the instance -- what share of the defect does it leave?"** | A per-incident patch offered for a structural bug. Measure its coverage, and check whether the residue is **still accruing**; if it is, the gap regrows the day after the patch ships |
| **A-50** | **"If you change this dataset, how do you get back?"** | Superset keeps no version history for dataset SQL. No backup means the change is one-way |

## 3.5 Narrative attacks

| Id | The attack |
|---|---|
| A-27 | "What decision changes because of this chart?" — if nothing, it is decoration |
| A-28 | "What's the largest bucket, and is it 'Other'?" |
| A-29 | "Which number here would you least like to be asked to defend?" — start there |
| A-30 | "If this is wrong, who finds out, and how long does it take?" |

---

# 4 · Running and reporting

## Order

```
build → Gates 0–6 → Golden → Regression → Adversarial → publish → companion doc
                       ↑                                    ↓
                       └──────── any change re-runs ────────┘
```

## The results table — ships in the companion doc

| Suite | Run | Passed | Failed | Not run | Notes |
|---|---|---|---|---|---|
| Golden | 2026-08-11 | 10 | 1 | 0 | G-07 at 3.2%, inside tolerance |
| Regression | 2026-08-11 | 19 | 1 | 1 | R-08 failed: one orphan dataset. R-12 not run in MCP-only mode |
| Adversarial | 2026-08-11 | 27 | 3 | 0 | A-01, A-08, A-17 — see caveats 1–3 |

**Reporting rules.**

- A failed adversarial test that you decide not to fix becomes a **numbered caveat with an
  owner**. It does not become silence.
- A test you could not run in your operating mode is **NOT RUN**. Never infer a pass.
- When a golden value legitimately moves, the changelog entry says which value, from what to
  what, and why.

## Adding tests

Every defect found in the wild becomes a test before it is fixed. That is the ratchet: the suite
should only ever grow, and every entry in §3 above is there because it already caught something
real on a live dashboard.
