# Modelling: semantic datasets, metrics and nomenclature

Author: Sayandip Bagchi.

Phase 4 and Phase 7 in full. `SKILL.md` carries the rules you need to start; this file carries the
reasoning behind each one and the failure it prevents. Read it before modelling a new journey, and
whenever you are about to split a dataset or name a metric.

The governing idea: **numbers become identical across dashlets by construction, not by
discipline.** Every count and conversion is a dataset metric, charts are metric selections, and
nothing is computed at chart level. That is also the main query optimisation.

---

## Phase 4 — Model: one semantic dataset per journey × source layer × grain

Do not write bespoke SQL per chart. Build virtual datasets at the natural entity grain — one row
per application, mandate, account, transaction — with a flag and timestamp per stage, derived
buckets (`outcome_bucket`, `stage_reached`, `last_stage`, lag buckets, channel, source), a
`cohort_month`, and the segment dimensions.

**One dataset per journey is the starting point, not the rule.** Split when — and only when —
one of these is true:

- **Different source layer.** A switch/auth table and a ledger table are different layers; a
dataset that spans both is either a deliberate reconciliation dataset (name it as such) or a
bug. One dashboard legitimately runs on several datasets for this reason.
- **Different grain.** Account × day and account-lifetime are not the same dataset.
- **Different date semantics.** A view deliberately exempt from the global date filter (lifetime
RFM, say) cannot share a dataset with a windowed one.

**Corollary you must not skip: a multi-dataset dashboard needs one native-filter target per
dataset.** A date filter that names only one of four datasets silently leaves three unfiltered,
and the dashboard will show inconsistent periods with no error. See `superset-api.md`.

Define **every count and conversion as a dataset metric**, not a chart-level aggregate. Charts
become metric selections. This makes numbers identical across dashlets by construction rather
than by discipline, and is the main query optimisation — `query-optimisation.md`.

**Metric naming convention (v2.0, mandatory on new work).** Pick one and hold it across the
tenant: `f_<stage>` for stage counts/flags, `p_<from>_<to>` for conversions, `s<n>_` / `i<n>_`
only where a numbered step/interim distinction genuinely exists, domain prefixes (`se_`,
`mandates_`, `payments_`) for domain counts. **Never ship two conversion prefixes in one tenant**
(`p_` and `pct_` side by side is live debt on at least one engagement). **Never leave Superset's default
`count`.**

**Window functions must be partitioned by every dimension a chart may later filter on.**
`NTILE`, `ROW_NUMBER` and running `SUM` are computed when the dataset runs, not when the chart
filters. Rank over the whole population, filter to a segment in the chart, and the percentiles and
cumulative shares still describe the whole — plausible, wrong, and silent. Partition by
`user_type` and any other filterable dimension, then assert that the final cumulative share is
exactly 100.0%. A dataset carrying precomputed ranks must also be **exempt from the date filter**,
with `main_dttm_col` explicitly null — Superset assigns one on its own otherwise.

Two similar-looking derived columns you need both of:

- `stage_reached` — furthest stage reached, **ignoring** terminal outcome.
- `last_stage` — final resting state, where a terminal outcome outranks a stage label.

Funnel step loss and "dropped at" buckets measure different things; the gap between them is the
decline volume. Ship the cross-tab of the two — and if you decide not to, say so in the companion
doc rather than leaving the docs asserting a dashlet that doesn't exist.


## Phase 7 — Nomenclature and layout

Details in `dashboard-design.md`. The conventions that are non-negotiable:

- **No ordinal prefixes on metric labels or funnel step labels.** The same metric sits at
different positions in different funnels, so a fixed number is wrong in at least one.
Left-to-right order carries the sequence; every conversion column is `→ %`.
- **Ordinal and letter prefixes on *dimension values* are the house style, not an exception** —
`1 · 0-7 days`, `A · Signed in`. They control sort order in a cross-tab and they are correct.
The rule is: *prefixes on dimension values, never on metric verbose names.*
- **` · ` is the title separator** for a section/qualifier: `Month-wise · Mandates`,
`RFM · headline`, `Sub-funnel · Approved (Open Banking route)`.
- **Name the source layer in the title whenever more than one layer is on the page.** Prefer the
layer in stakeholder language with the table in parentheses — `Declines (switch: auth_rollup_base)`
— over a bare table name a reader cannot decode.
- Use the tenant's own vocabulary throughout. If the PSP has a name, write the name — not "the PSP".


---

## The failure behind each rule

Every rule above is named after something that has already gone wrong. If you are tempted to skip
one, this is what you are betting against.

**Splitting only for layer, grain or date semantics.** A dataset spanning a switch table and a
ledger table adds across layers, so the same transaction is counted once as an authorisation and
once as a posting. The total is plausible, larger than either source, and reconciles with nothing.
Gate 4 catches it only if someone thought to triangulate the two layers.

**One native-filter target per dataset.** This is the quietest failure in the package. A filter
that names one dataset does not error on the others; it simply does not reach them. Seen live: a
"Customer only" user-type filter left pointing at a dataset that had been superseded and removed
from the page, so every chart on that dashboard was silently including internal users, with the
filter sitting in the left rail looking applied. Gate 0b's last checkbox exists for exactly this.
Re-run it after **any** dataset supersession, not just at build time.

**Every count as a dataset metric.** Chart-level aggregates drift the moment two people edit two
charts. The dashboard then has two numbers for one concept and no way to tell which is right,
which is the failure the whole package is arranged around. It is also the main query cost: a
chart-level aggregate re-scans where a dataset metric does not.

**One naming convention per tenant.** Two conversion prefixes living side by side (`p_` and
`pct_`) means a reader cannot tell whether two similarly-named metrics are the same measure or
different ones, and neither can the next person to extend the suite. Superset's default `count`
surviving on a dataset means at least one chart is counting rows rather than the entity you think
it is counting, and Gate 1 fails.

**Partitioning window functions.** `NTILE`, `ROW_NUMBER` and running `SUM` are computed when the
dataset runs, not when the chart filters. Rank over the whole population, filter to a segment in
the chart, and the percentiles and cumulative shares still describe the whole population while
appearing to describe the segment. Plausible, wrong, and completely silent. The tell is a final
cumulative share that is not exactly 100.0%; assert it. A dataset carrying precomputed ranks must
also be exempt from the date filter with `main_dttm_col` explicitly null, because Superset assigns
one on its own otherwise and the ranks then describe a windowed subset.

**Both `stage_reached` and `last_stage`.** These look like the same column and are not. Furthest
stage reached ignores the terminal outcome; final resting state lets a terminal outcome outrank a
stage label. Funnel step loss and "dropped at" buckets therefore measure different things, and the
gap between them is the decline volume. Ship only one and you will be asked, in a review, why the
funnel says one number and the drop-off table says another, and you will not have an answer.

**The grain rule underneath all of it (G11).** Count entities, not events. An event count is not a
population, and any bridge between an event grain and an entity grain must be validated on the
failing rows with the unmatched rate reported. See
`${CLAUDE_PLUGIN_ROOT}/skills/superset-bi-agent/references/guardrails.md` G11 and `qc-protocol.md`
Gate 1b.
