# The twelve guardrails

Author: Sayandip Bagchi.

Each guardrail is named after a failure that has already happened on a real engagement. The
one-line version of all twelve is the table in `SKILL.md`; this file carries the rationale and the
worked procedure. Read it before Phase 0 on a new engagement, and whenever you are about to do the
thing a guardrail forbids.

A guardrail is not advice. Four map to numbered blocking QC gates — G8 to Gate 0b, G9 to Gate 0c,
G10 to Gate 0d and G11 to Gate 1b. G3 maps to the two blocking checkpoints (the reference-dashlet
review and the derived stage ladder), G7 is the publishing rule that makes every gate blocking, and
G12 is enforced by eval only. So violating one does not produce a slightly worse dashboard, it
produces an unpublishable one.

---

## Guardrails

**G1 · Model gate.** Opus 5 or Sonnet 5 only. Prompt on fresh invocation. Full rule in the model gate section of `SKILL.md`.

**G2 · Read-only warehouse.** Never write to the warehouse. Dataset/chart/dashboard objects in
Superset's own metadata store are the only things you create.

**G3 · Confirm before building.** Two hard checkpoints where you stop and get user agreement:
the reference-dashlet review note (end of Phase 1) and the derived stage ladder (end of Phase 2).
These are the highest-value interrupts in the process; skipping them is the most expensive
mistake available to you.

**G4 · Flag inconsistency loudly, never paper over it.** A join key null on a third of rows, two
tables that should agree and don't, a field zero across all history — each is a finding for the
user and belongs in the shipped caveats, not in a silent `coalesce`. Where you *do* patch,
expose a metric counting how often the patch fired so the problem stays visible.

**G5 · Never supersede a reference number silently.** State the old number, yours, and the
difference in one repeatable sentence.

**G6 · No unlabelled residuals.** If shares don't sum to 100%, or two counts of the same
population differ, that gap gets a name and a dashlet or a caveat. It never gets rounded away.

**G7 · Do not publish past a failing gate.** The QC gates in the `superset-build` skill are sequential and blocking.

**G8 · Establish the go-live date, and filter internal users out. Never skip this.**

Every engagement has a period before market launch when the only people in the data are staff,
pilot users and test accounts. **Their activity is indistinguishable from customer activity in
every table**, and at early-stage volumes it is not a rounding error — on a recent engagement internal users
were **10% of accounts on book and 20% of all transactions**.

In Phase 0 you must obtain, in writing:

- The **go-live / market launch date** — the date real customers could first transact. Not the
date the code shipped, not the date the first account was opened.
- Whether there were **staged launches** (soft launch, invite-only, geographic phasing). Each
stage may need its own boundary.
- Whether internal users are **identifiable by any attribute other than date** — a staff flag, an
email domain, an account-type code, a test marker. If one exists it beats a date cut, because
internal users keep transacting after go-live.

Then, in every dataset carrying an entity that predates launch:

1. Add a **`user_type` derived column** (`Customer` / `Internal (pre go-live)`), not a filter
buried in a chart. It must be a dimension anyone can group by and see.
2. Default the dashboard's user-type filter to **Customer only**, and say so in the filter label.
3. **Ship the internal count as its own metric.** Excluding a population silently is how you get
asked "where did the other 21 go?" in a review. Make it visible and subtractable.
4. Check every **date-filter-exempt** view — lifetime RFM, cohort tables, "ever active" counts.
A date default does not protect them; they need the user-type filter explicitly, and they are
the views most likely to be quietly contaminated.
5. State the go-live date and the internal share **on the dashboard**, not just in the doc.

A date-based cut is a floor, not a solution: it catches entities *created* before launch and
misses internal users created after. Say which you have, and if it is only the date cut, ship it
as a caveat.

**G9 · Never derive a journey from data alone. Ground it in the product artefacts first.**

**The warehouse tells you what fired. It cannot tell you what was supposed to fire.** Four things
are invisible from the data and all four produce confidently wrong funnels:

- **Built but not launched** — a flag that's off reads as a step nobody reached.
- **Launched but not instrumented** — a real stage the funnel silently skips, so the previous
step's exit looks like the next step's entry.
- **Instrumented but renamed** — a permanent zero from a fixed date, read as a cliff.
- **Not in this engagement at all** — you ported another tenant's ladder and are measuring a
journey this product doesn't have.

Note the direction of the error: **unfired events look like steps nobody reached**, so a
data-only funnel flatters the product and understates the instrumentation gap.

Before modelling, in Phase 0.1c and Phase 1.5:

1. **Ask for the artefacts** — PRDs (Confluence links or attachments), Figma or design links
including the error and edge screens, the event dictionary / tracking plan, and the feature
availability per module. Batch the request; partial is fine.
2. **Reconcile three ways — PRD ↔ Design ↔ Events.** Every mismatch is either a finding for the
product team or a correction to your funnel. When all three disagree, **stop and ask — do not
pick the one that makes the nicest funnel.**
3. **Build the feature availability matrix** before Phase 4. No two engagements have the same
feature set. Repayments varies most: rails, PSP (*name it*), autopay, one-off, scheduled,
partial payment, mandate modification, retry logic and returns are all optional and several
are mutually exclusive.
4. **Establish per-stage instrumentation before applying Directive 3.** Backend-is-truth is a
modelling rule you cannot apply until you know which stages have a backend event *at all*. A
stage with neither BE nor FE coverage is declared on the chart, never quietly dropped.
5. **If no artefacts exist**, work down the fallback ladder in `product-artefacts.md`
§7 and **state in the companion doc which rung you reached.** A ladder derived from the
transition matrix is a hypothesis, not the journey — it must be confirmed (G3) before anything
is built on it.

Full method, including how to read a PRD and a Figma file specifically for BI purposes:
**`product-artefacts.md`**.

**G10 · Verify the environment and the schema empirically. Names lie about both.**

**UAT and production look identical in every tool.** A CDP workspace switcher, a Superset
database connection, a schema suffix — none of them announce which is which, and both are usually
named after the product. Building a suite on UAT is not a subtle error: it is a page of plausible
numbers that describe nobody, and it will not be caught by any gate, because UAT data reconciles
against itself perfectly.

**Establish and record before reading a single row:**

1. **The CDP** — which workspace / app id, and is it **UAT or production**? Ask the user to
confirm explicitly. Do not infer it from the workspace name.
2. **Superset** — which database connection and database id, and does that connection point at
production? A Superset instance can carry both.
3. **Schemas** — the exact schema set, and the tenant id embedded in the schema names.

**Then verify empirically, never by name:**

- **Row counts and max timestamps.** UAT is usually smaller and staler — but not always, and
"usually" is not a check.
- **A known-good anchor.** Take one number the business already quotes and reproduce it. If your
source cannot, you are on the wrong one. This is the only test that actually settles it.
- **Test-data density.** A population that is mostly staff-shaped is a UAT tell.

**When the same data point exists in more than one schema — and it frequently does:**

- **Enumerate every schema containing a candidate table before choosing one.** A single
`information_schema` query, and it prevents the most expensive class of rebuild.
- **Never pick silently.** Put the candidates to the user with row counts, min and max dates, and
freshness side by side, and ask which is authoritative. This is a one-message question that
saves a full rebuild.
- **Then triangulate.** Count the same entity in each candidate and report the deltas. Equal
counts mean the choice is low-risk. Unequal counts mean the schemas are not copies, and the
difference is a finding before it is a decision.
- **Record the choice, the rejected alternatives, and the delta** in the Definition Registry.
"Why not the other schema?" is a question you will be asked, once, in front of people.

Environment and schema provenance ship in the companion doc and on the dashboard header. A suite
whose readers cannot tell which environment produced it is not reviewable.

**The same empiricism applies in the other direction: before concluding a data point's raw source
doesn't exist anywhere, the schema sweep must be exhaustive, not just the schema family already in
use.** One session declared "no raw response/processing code exists on this instance" for the
switch decline taxonomy after checking three schemas — the two per-transaction tables that proved
it wrong were never in the search. Enumerate every visible schema, grep it for the domain's likely
nouns, and only write "doesn't exist" once that sweep is empty. Full method:
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/schema-discovery.md` ("Before you write
'no raw source exists'").


**G11 · Count entities, not just events. An event count is not a population.**

Whenever a metric counts *things that happened* — declines, failures, retries, errors, rejections,
contacts — a stakeholder will read it as *people affected*. Those two numbers routinely differ by
4-6x, because repeat events cluster on a small number of entities.

- **Every event-count metric a stakeholder might quote needs a unique-entity figure beside it**,
  or a stated reason why one is not available.
- **Establish the entity before building** — user, account, card, application, mandate — and never
  silently substitute the grain your data happens to have for the word the user used. Test whether
  they are 1:1 and say so.
- **Validate any entity bridge on the failing rows specifically.** A bridge verified on successful
  events is not verified; failures are exactly where identifiers go missing.
- **The tail is the finding.** Report the concentration, not just the average, and check whether
  the heavy tail is a different phenomenon from the body — it usually is.

Full method, including the five-dashlet set and the ranking bug that survives review:
**`${CLAUDE_PLUGIN_ROOT}/skills/concentration-analysis/SKILL.md`**.

**G12 · A funnel keyed on one system's records cannot see the people that system never met.
Triangulate the vendor, the event stream, and the orphans between them.**

Almost every journey is instrumented twice: an **origination/vendor system** that owns the record
(an origination system, an LOS, a KYC vendor) and an **event stream** that watches the customer (a CDP,
Segment, an app SDK). Build the funnel from either alone and it is wrong in a specific, predictable
direction — **it under-counts the top and flatters every conversion rate below it**, because the
denominator silently excludes everyone the chosen system never recorded.

Three populations exist, and a defensible top-of-funnel names all three:

| Population | Seen by | Typical fate |
|---|---|---|
| In both | vendor **and** stream | Counted correctly today |
| **Vendor-only** | vendor record exists, no event fired | Dropped by an event-derived funnel |
| **Stream-only — the orphans** | event fired, no vendor record ever created | Dropped by a vendor-derived funnel. Usually the most interesting group, because it is *pre-commitment* drop-off |

**Do this, in order:**

1. **Count all three before designing the entry step** — two anti-joins and a matched count. If the
   orphan population is material, the entry step is a **union**, not a choice, and the union needs a
   dedupe key that exists on both sides (see 4).
2. **Apply the terminal-outcome backstop.** *An entity that reached a later stage or a terminal
   outcome has, by definition, started.* Any funnel filtering on an early-stage flag must be tested
   for entities carrying a terminal outcome that sit **outside** the population:
   `<terminal flags set> AND <entry flag> = 0`. On one engagement this found **128 applications — 120
   declined, 4 approved, 4 who had completed onboarding — invisible on every chart of the
   dashboard**, a population that had grown 7.5x because nobody had asked. This check costs one
   query, needs no second system, and is the highest-yield item in G12.
3. **Never promote the stream to a replacement for the vendor.** Check coverage in *both*
   directions. On one engagement a third of vendor-recorded starters had no landing event at all, stable
   month over month — so the stream was additive, never a substitute. A one-directional check
   misses this and produces a confidently smaller funnel.
4. **Establish the entity and the grain before the union.** "Who landed" has a different count at
   every grain — device, person, quotation, application. Three plausible numbers for one concept is
   normal and none is wrong. State the grain on the chart, and dedupe on a key both systems carry.
5. **Ship the decomposition, not just the total.** Expose an `entry_source` dimension whose values
   sum exactly to the entry step, keep the pre-change figure as its own metric (G5), and name the
   residual left outside (G6). A union with no decomposition is unreviewable.
6. **Re-check what the union broke.** Any chart slicing by a vendor-supplied dimension — segment,
   decision, product — cannot classify the orphans, because that dimension comes from the record
   they never had. Sub-funnels that used to tile the population will silently stop tiling it. Test
   that the parts still sum; if they cannot, say so on the page and build a coverage dashlet.

**Two source traps underneath all of this:**

- **One stream is often exposed as several projections.** The same events can appear in a raw
  payload table and a curated flat table in another schema, with different keys and different
  coverage. Enumerate every schema carrying the event before choosing (G10), then prove they are
  the same stream by **row count and min/max timestamp**, not by name. The curated table is usually
  easier to key on; the raw one usually carries more events — check whether the curated one has the
  backend ladder at all before "consolidating" onto it.
- **Inspect nested payloads with a serialize call, never a cast.** Casting a `SUPER`/`JSON` column
  to varchar can return **null**, which reads as "there is no payload" and is a different claim
  entirely. A join key chosen on that basis silently drops rows and is expensive to unwind.

## Anti-patterns to refuse

- Building a funnel from FE events because the BE events "look incomplete" — they usually aren't.
- Porting another engagement's acquisition or onboarding ladder without re-deriving it.
- Publishing a number that contradicts a reference dashlet without explaining the difference.
- Silently deduplicating repeat entities to make a funnel monotonic.
- Reporting a windowed funnel number without the unbounded one beside it.
- Adding a number from an upstream table to a number from a downstream one.
- Using a field because its name matches the concept — names lie.
- Shipping a bucket called "Other" that is the largest bucket, without flagging it.
- Shipping two charts on one dashboard that share a concept and a source under different titles.
- Reporting an event count as though it were the number of customers affected.
- Ranking or accumulating over a population that a chart then filters — the percentiles silently
  describe a different population from the one on screen.
- Accepting a per-incident patch for a structural defect without measuring what share it leaves
  behind, and whether that residue is still growing.
- Rewriting a dataset you do not own without first preserving its original SQL.
- Driving a query FROM the enrichment table instead of the table whose grain you are reporting.
- Leaving Superset's default `count` metric on a dataset you built.
- Asserting in documentation that a dashlet exists when it was never built.
- Choosing between a vendor system and an event stream when the honest answer is a union — and
  never counting the orphans that neither one alone can see.
- Filtering a funnel on an early-stage flag without testing for entities that carry a terminal
  outcome and sit outside the population.
- Concluding a nested payload is empty because a varchar cast returned null.
- Treating an identifier as a bridge because its name matches, without testing overlap — and
  without checking the empty string as well as NULL.

---

## Phase-by-phase model guidance (G1 in detail)

| Phase | Opus 5 | Sonnet 5 |
|---|---|---|
| 0 Prequalify | ✔ preferred | ✔ acceptable |
| 0.5 Inherit an existing suite | ✔ preferred | ✔ acceptable |
| 1 Reference dashlet review | ✔ **required** | ✖ — adopt/adapt/supersede calls are the crux |
| 2 Schema discovery, ladder derivation | ✔ **required** | ✖ |
| 3 Definition Registry | ✔ **required** | ✖ |
| 4 Semantic dataset modelling | ✔ preferred | ~ only against a settled Registry |
| 5 Storyboard | ✔ preferred | ✔ acceptable |
| 6 Build (API mechanics) | ✔ | ✔ — mechanical, either is fine |
| 7 Layout / nomenclature | ✔ | ✔ |
| 8 QC gates | ✔ **required** for Gates 3 and 4 | ✔ for Gates 0, 2, 5 |
| 9 Ship the writing | ✔ | ✔ |

Rule of thumb: **Sonnet 5 executes a settled Registry; Opus 5 decides what goes in it.**


---

## The remaining engagement constraints

`SKILL.md` states the four load-bearing ones. These also hold on every engagement:

- **Small-n is normal early in a programme.** Quartile techniques such as `NTILE` are noise below
  a few hundred entities; use fixed banding and say why on the chart.
- **Some verification is impossible in non-browser modes.** Say which half you checked rather
  than reporting a pass you could not perform.
- **Orphaned Superset components survive UI re-saves.** A component you deleted in the API may
  still be in `position_json`.

## The shipping bar

A build is successful when all of these hold:

- Every published number traces to exactly one Definition Registry row.
- Every shared data point returns the identical value on every dashboard that shows it, verified
  by query, not by eye.
- Every number is triangulated against an independent source, or the gap is stated on the page.
- Reading the dashlet titles top to bottom tells the story without the numbers.
- The companion doc exists and names an owner for every open data-quality item.
- A reviewer who did not build it can reproduce any figure from the Registry in under five
  minutes.

Any one of these means the build is **not shippable**, whatever else passed: a funnel step that
goes up; a bucket called "Other" that is the largest bucket and unflagged; a number that
contradicts a reference dashlet with no explanation; a metric with no Registry row.
