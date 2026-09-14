# Playbook: acquisition source and the pre-application stage

**This section varies more between engagements than any other part of the funnel.** One tenant
runs soft-eligibility quotes through a decisioning vendor, another takes aggregator traffic,
another is invite-only, another cross-sells to an existing base with no pre-application stage at
all. Nothing here can be ported. Ask every time.

It also matters disproportionately: on more than one build, the pre-application stage turned out
to lose two orders of magnitude more people than the funnel stage the team was focused on. If
you skip it because the brief said "onboarding funnel", you will measure the wrong constraint.

**This pre-funnel usually has no dashboard of its own.** It is normally a second dataset on the
onboarding dashboard, carrying two or three charts. Two consequences: that dashboard's global date
filter needs a native filter target for **each** dataset or the pre-funnel silently ignores it, and
the reconciliation between this section and the funnel below it becomes a **same-dashboard** check,
which is the easiest kind to run and the most embarrassing kind to fail.

Live state for this journey is in `${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/journeys.md`. Read the
section for this journey only.

## Prequalifying questions — ask before any schema work

### Does a pre-application stage exist, and what is it called here?

- Soft eligibility / soft search / pre-qualification / quotation / pre-approval / waitlist /
  invite — **use the tenant's word**, and get the state names.
- Is it a **credit decision** (soft search returning approve/decline) or a **marketing
  qualification** (form fill, waitlist signup)? These behave completely differently and the
  conversion expectations are not comparable.
- If it is a credit decision, **is it binary or tiered?** Tiered is common, and a tier is not
  simply a nicer approval: on one engagement the upper tier is a *pre-validated* outcome that lets
  the applicant skip the bank-connection stage downstream, so the pre-funnel decision determines
  the application's route. The segment mapping that results is routinely read backwards; check the
  live one in the tenant file before you label anything, and read
  `${CLAUDE_PLUGIN_ROOT}/skills/onboarding-funnel/SKILL.md` for how routes are modelled.
- Is there **no** pre-application stage? That is a valid answer — say so on the dashboard rather
  than leaving a reader to wonder.

### Which acquisition sources feed it?

Ask which of these are live, and whether the dashboard should split by them:

| Source | What to watch for |
|---|---|
| Direct — own site or app | Usually the cleanest attribution |
| Aggregator / price comparison | High volume, low intent. Will dominate the top of the funnel and drag the headline rate down. Almost always needs its own funnel |
| Partner / embedded / co-brand | Check whether the partner runs its own eligibility step upstream that you cannot see |
| Paid marketing landing page | Attribution usually lives in a marketing field (utm/campaign), not the decisioning table |
| Existing-customer cross-sell / pre-approved | May **skip** the pre-application stage entirely — a parallel route, not a step |
| Branch or agent assisted | Often a different state machine altogether |
| Waitlist / invite code | The constraint is invite issuance, not conversion. Model issuance as step one |

**Is the funnel expected to be one funnel or one per source?** If sources have materially
different intent, an overall rate is misleading on its own — same rule as approval routes.

> **"Neither" is a real answer.** On one engagement the pre-funnel dataset carries no source or
> channel dimension at all, meaning a single acquisition source or an uncaptured one. Where that
> is the case, **do not prescribe a by-source dashlet** — it is not applicable, and leaving it
> prescribed makes the section look half-built. If a source dimension appears later, that is a
> schema change, not a chart change.

### Where does the data live and how does it link?

- Which system owns the pre-application record — decisioning vendor, aggregator feed, marketing
  analytics, or the core product?
- **What is the key that links a pre-application record to an application?** Get the field name.
- Is source/channel captured **on the application** as a field, or only inferable from the
  upstream record? (If only upstream, a broken link also loses your source attribution.)
- Is there an **attribution window** — how long between the quote and the application does the
  tenant still consider it the same journey?

### Grain and counting

- **Can one person hold many pre-application records?** Almost always yes. Then eligibility steps
  count **quotations/checks** and application steps count **applications** — two different grains
  in one funnel, which must be stated on the dashboard.
- Are declined applicants **re-quoted**? Repeat quotes inflate the denominator and make the
  headline conversion rate look far worse than the per-person reality. Report both:
  checks, distinct people, and checks per person.
- Which number does the tenant already quote for "applications started" — the pre-application
  system's count or the onboarding system's? **They will differ.** Find out which one leadership
  uses before you publish a different one. Both counts frequently exist on the same dashboard, one
  per dataset, which makes the disagreement catchable in a single query.

## Modelling

- **Grain: one row per pre-application record** (quotation/check), with the decision, the source,
  the timestamp, and the resolved application id.
- Latest row per record id — these tables are usually append-only with revisions.
- Resolve the application in **two passes**: the direct link where present, then a fallback on a
  person-level key (borrower id, customer id, hashed identity).

```sql
coalesce(q.linked_application_id, b.app_id) as resolved_app_id
```

  **Both column names above are illustrative.** A `coalesce` written from a pattern like this
  routinely has one side verified against the schema and the other assumed from its name, and the
  assumed side is the one that returns nulls forever without erroring — check that **each** column
  exists, on the table you are actually querying, against live SQL before copying this.

- Expose a **`resolved_via_customer_id`** metric so the underlying data defect stays visible rather
  than being silently patched. Report its trend by month. (On a recent engagement the metric is
  live and the dashlet was never built — see Dashlets.)
- Cohort-date on the pre-application record's own timestamp for the pre-funnel, but be explicit
  that the application funnel below it is cohort-dated on the **application**.

## Traps

**The link will be broken on a material share of records.** Expect a null rate in the tens of
percent on the field that ties a quotation to an application. Check whether a person-level key
recovers it — usually most of them. Without the fallback the pre-funnel reports far fewer
applications than the funnel directly beneath it on the same page, which is the most visible
possible inconsistency.

**And it degrades.** A link that is 29% broken one month and 50% the next is a live incident, not
a quirk. Chart it by month and escalate it. On one engagement this is currently invisible: the
metric exists, the chart does not.

**Non-additive month rows.** If the month table is keyed on quote month while the metric counts
distinct applications, rows can sum past the total — a person quoting in two months lands in
both. This is correct behaviour but reads as a bug. Either state it in the doc or re-key the
month dimension onto the application's own cohort month. On a recent engagement this is live and
unmitigated: the by-month chart runs on a dataset carrying both quote-grain and
application-grain metrics, with no evidence the re-keying was applied. Check it before the first
stakeholder adds up a column.

**"Passed eligibility" is not "was offered and accepted".** There are usually several steps
between a soft-search approval and an application actually starting. Ask what they are; do not
draw a single arrow across them.

**Decision values may be messy — enumerate them before writing a `CASE`.** Expect blanks, a
literal `0`, and vendor-specific labels elsewhere; keep an explicit "no decision" bucket rather
than folding it into declined. Where a tenant's values have already been enumerated and recorded,
use those literals verbatim; do not re-derive them, and **never collapse two approval tiers into
one**, because the tier is what determines the downstream route.

**A field that exists on one table but not another.** Counts and flags on the application record
are frequently absent from the quotation record even where the names suggest otherwise. Verify
the column exists on the table you are actually querying before building on it.

## Dashlets

1. **Pre-application funnel** — checks performed → passed → progressed to an application →
   applications started → **applications completed**, with the end-to-end rate. Horizontal box
   view. The fifth step is what closes the loop between this section and the onboarding funnel's
   exit. Report declined and no-decision counts alongside passed, not as a residual.
2. **By month** — the same steps as a calendar table, with the fallback-resolution count beside
   them.
3. **By acquisition source** — only if more than one source is live. Where no source dimension
   exists on the dataset, this dashlet is not applicable; say so rather than leaving it
   prescribed.
4. **Link health** — share of applications with no direct pre-application link, by month. Small,
   but it is the dashlet that stops the whole section being disbelieved. Where the
   `resolved_via_customer_id` metric already exists on the dataset, this is a chart build, not a
   modelling job.

Skip a "decision mix" pie unless the tenant asks — the mix is usually better stated as a sentence
in the doc than given a dashlet. Where the decision is tiered, that sentence must name all three
tiers.

## Triangulation

| Check | How |
|---|---|
| Pre-application count vs the funnel entry beneath it | Applications started must reconcile between the two sections **on the same page**: the pre-funnel's applications-started metric vs the funnel's own entry metric. This is the check that catches the broken link. The live pair is recorded in the tenant file |
| Applications completed vs the onboarding exit | The pre-funnel's applications-completed metric vs the funnel's completion metric. A second same-page check the funnel view alone will not give you |
| Vendor/aggregator reported volume vs your count | Ask the user for the partner's number; a gap is a feed problem. Enumerate any existing acquisition-funnel dashboard on the instance and decode it before claiming Gate 4 passes |
| Source attribution: upstream vs application field | Where both exist, compare. Disagreement means the application field is being set late or defaulted. Not runnable where neither side captures a source |
| Distinct people vs records | Establishes the repeat-quote inflation factor once, so you can explain the headline rate |

## Interpretation

Lead with the ratio that reframes the roadmap. If a large number pass eligibility and a tiny
number reach an application, say plainly that **passing eligibility is not the constraint** and
size the loss in absolute people against the funnel stage the team is currently working on. That
single comparison is usually the most valuable output of the whole dashboard.

Where the decision is tiered, report the tiers separately in that sentence. A single "N approved"
hides whether the approvals were pre-validated or not, and the two tiers convert differently
downstream.

**Quote-grain and application-grain metrics routinely share one dataset.** Never put them in one
summed column without a grain label on the row, and name the grain in the chart title.

**Name the link-health metric for the key that recovered the link**, not for the fact that
something fell back: `resolved_via_customer_id` beats `resolved_via_fallback`.

Live decision literals, metric names and the current pre-funnel figures for a tenant are in
`${CLAUDE_PLUGIN_ROOT}/tenants/<tenant>/journeys.md`. Read the section for this journey only.
