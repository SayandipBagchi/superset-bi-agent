# Phase 0: prequalify, and Phase 0.5: inherit

Author: Sayandip Bagchi.

Phase 0 is never skipped, on any entry mode. It is ten sub-steps of questions, and the answers are
what every later phase is built on. Getting one wrong is not a slow start, it is a rebuild.

Phase 0.5 replaces Phase 0's discovery half when a suite already exists: you inherit what is live
before you extend or audit it.

Ask these as questions to the user. Do not infer an answer from another tenant, from a column
name, or from a dashboard someone linked you to.

---

## Phase 0 — Prequalify (never skip)

Ask in one batched round, grouped. Use a multiple-choice question tool if available; otherwise
plain text, but batch it — do not drip-feed.

**0.1 Operating mode, environment and access.** Guardrail G10 — this is the question that
invalidates everything downstream if it is wrong, and it cannot be inferred.

- Which of the three operating modes? See `operating-modes.md`.
- Superset URL, **database connection and database id** — and **does that connection point at
production?** One instance can carry both.
- **CDP workspace / app id — is it UAT or production?** Ask explicitly; both environments are
normally named after the product, so the name settles nothing.
- Which schemas, and what is the tenant id embedded in them? **Confirm empirically, never by
name** — row counts, max timestamps, and one number the business already quotes.
- Is the SQL user read-only? (Assume yes; never test it by writing.)
- Scheduled email pulse reports wanted?

> **If any answer is "I think so", treat it as unknown.** Reproduce a quoted number from the
> source before building on it. UAT reconciles against itself perfectly, so no gate downstream
> will catch this.

**0.1b Programme timeline and internal users — ASK THIS ON EVERY NEW ENGAGEMENT.**
Guardrail G8. This is a first-round question, not a detail to pick up later: it changes the
population of every dashboard you are about to build, and it cannot be inferred from the data —
the earliest row in a table is a launch date only by coincidence.

> Before I look at any numbers, I need the programme timeline:
>
> 1. **What is the go-live / market launch date** — the date real external customers could first
> apply or transact? (Not the code-ship date, and not the date of the first account in the
> warehouse — those are usually earlier.)
> 2. **Was the launch staged?** Soft launch, invite-only, employee-only, geographic phasing —
> and what are the dates of each stage?
> 3. **Is there any way to identify internal / staff / test users other than by date** — a staff
> flag, an email domain, an account-type or product code, a test marker? If yes, that beats a
> date cut, because internal users keep transacting after go-live.
> 4. **Should internal activity be excluded by default, or shown as a separate segment?**

Record the answer verbatim in the tenant file and implement it per G8 before building anything.
If the answer is "I'm not sure", **stop and get it** — do not proceed on a guessed date. If no
non-date identifier exists, say plainly that the date cut catches only entities created before
launch and will miss internal users created after it, and ship that as a caveat.

**0.1c Product artefacts — ASK THIS ON EVERY ENGAGEMENT, BEFORE ANY SQL.**
Guardrail G9. Each engagement's onboarding journey, and especially its repayment feature set,
differs — and the difference is not visible in the warehouse. Batch this with 0.1b.

> To build funnels that match the journey rather than the instrumentation, I need whatever exists
> of the following. **Partial is fine** — I'll tell you what's missing and what it costs.
>
> 1. **PRDs** — Confluence links or attachments, per module. Especially the acquisition /
> pre-onboarding spec and the onboarding spec, which vary most between engagements.
> 2. **Designs** — Figma links for the journeys in scope, **including the error and edge-case
> screens** (those are usually the drop-off vocabulary).
> 3. **The event dictionary / tracking plan** — what's named, and which events are server-side
> versus app SDK.
> 4. **Feature availability per module** — which features exist *here*, and which are live versus
> built-but-flagged-off. For repayments specifically: which rails, which PSP (and is there a
> fallback?), autopay, one-off, scheduled, partial payment, mandate modification, retries,
> returns.
> 5. **Cohort definitions the product team already uses** — if the PRD segments users a particular
> way, the dashboard should use the same words.

"There is no PRD" and "the designs are stale" are **findings, not blockers**. Record which
artefacts you got, use the fallback ladder, and ship the limitation as a caveat.

**0.2 Reference dashlets — ask explicitly.**

> Are there existing dashlets I should review first — CDP funnels or behaviour charts,
> Superset dashboards, a BI/business-metrics dashboard, or a number leadership already quotes?
> Links, please.

Then ask **which of these does leadership actually quote?** That is the reconciliation target.
Independently of the answer, enumerate the instance yourself — sibling dashboards you were not
told about are still reference dashboards.

**This drives Phase 1 — do not skip it because the brief sounded greenfield.** Greenfield briefs
are usually wrong about that.

**0.3 Audience and decision** — who reads this, at what cadence, and what decision changes
because of it? Exec one-screen summary, or operator deep-dive? *That answer decides dashlet count
and whether detail tables ship at all.* Is this replacing an existing dashboard? Get the link.

**0.4 Acquisition source and the pre-application stage.** The least consistent part of any
engagement — **never carry it over from another tenant.** Full playbook:
`acquisition-source.md`.

- Is there a pre-application stage at all, and what is it called here — soft eligibility, soft
search, pre-qualification, quotation, pre-approval, waitlist, invite? **Use their word.**
- Is it a **credit decision** or a **marketing qualification**? Not comparable. And is the
decision binary or tiered? (A tiered example: Approved / Approved plus / Decline.)
- Which acquisition sources are live — direct, aggregator, partner/embedded, paid landing page,
existing-customer cross-sell, branch/agent, invite? Should the funnel split by source?
- Which system owns the pre-application record, and **what key links it to an application**?
- Can one person hold many pre-application records? *(Then eligibility counts records and
applications count applications — two grains in one funnel.)*
- Which number does the org already quote for "applications started" — the pre-application
system's or the onboarding system's? **They will differ.**

**0.5 Journey scope — the tenant-variable list.**

Ask about each in-scope journey. **These are the things that reliably differ per engagement:**

| Area | What to ask |
|---|---|
| Acquisition / pre-eligibility | See 0.4 — the most variable of all |
| Onboarding sequence | What are the states, in order? Parallel routes where a segment skips a stage? Which state is the true entry, and from what date has it been emitted? |
| FE vs BE instrumentation | Which journeys have server-side events, which only app SDK events, which only CDC/audit tables? Which is the contract of record? |
| Transaction methods | Card present / CNP / wallet / P2P / ATM / rails in use. Which are in scope? |
| App sign-up steps | What is the first authenticated event? Is there a pre-auth stage with no user id? What counts as "signed in"? |
| Spend decline taxonomy | Ask for the tenant's own list — do not offer Business/Technical/Fraud as if it were universal. Which layer owns it: switch, account, or ledger? Are there several unattributed buckets? |
| Repayment modes | Which **rails** exist (Direct Debit, VRP, Open Banking, external transfer, card, standing instruction)? Separately: which **initiation sources** (app, autopay, external, unknown)? Can one fall back to another? Who is the PSP? |

**0.6 Definitions — write these down verbatim.**

- What is an **active** user/account here? Logged in, activated, or transacted?
- What is a **spend**? Authorisation, posted, or settled? *(Posted is usually the defensible one.)*
- What is **onboarded**? Application completed, account created, or card issued?
- What is a **failure** vs a **drop-off**? A decline is a decision; an abandonment is a
behaviour. **They must not share a bucket.**

**0.7 Funnel semantics.**

- **Rolling or windowed?** Default to unbounded and say so.
- **Keyed on what entity** — user, application, account, mandate, transaction? *Repeat applicants
and multi-account users break user-keyed funnels.*
- **Cohort-dated on what?** Cohort-date on the entity's first event so a date filter never splits
a funnel across periods.

**0.8 Presentation and known unknowns.**

- Default date range, and is it changeable? Global filters for the left rail? Month-wise tables?
- Any tables you already know are stale, unpopulated, or lying?
- Any metric leadership quotes that I must reconcile to?

## Phase 0.5 — Inherit an existing suite

Whenever anything already exists. Cheap, and it prevents the most common failure in an extend/
audit engagement: building a tenth definition of a thing that already has nine.

1. `GET /api/v1/dashboard/` — every dashboard on the instance, with id, slug, title, last-changed.
Note the ones nobody told you about.
2. `GET /api/v1/dashboard/{id}/charts` for each in-scope dashboard — chart names, viz types,
datasource ids. Count them.
3. `GET /api/v1/dataset/{id}` for every datasource seen — name, source tables, SQL, metric list.
4. Build the **inherited Registry**: every metric, its dataset, its definition. Diff it against
`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/`. Everything in the diff is either a change since last session or a
gap in the file; both need writing up.
5. **Find the reconciliation pairs**: any data point computed by more than one dataset. These are
the Gate 3 worklist and they are the first thing to break.
6. **Find the orphans**: datasets referenced by no chart; charts on no dashboard; Superset's
default `count` metric left in place; two charts sharing a concept and a source under
different titles. Each is a finding.
7. Update the tenant current-state file before doing anything else.

