# Fine-tuning: the improvement ratchet

Author: Sayandip Bagchi.

This is prompt-and-skill tuning, not model-weight fine-tuning. Nobody trains anything here — no
gradients, no checkpoints, no dataset of labelled builds; what gets tuned is the text of the
skills, the guardrails, the eval suites and the tenant files. If you arrived wanting weight-level
work, read the next section before going any further, because almost every request that arrives
phrased as "fine-tune the model" is satisfied by a better guardrail, and the guardrail ships
today.

---

## The boundary, and what to do instead

A model that produces a wrong funnel does so because it was not told the ladder, not because its
weights lack the capacity to hold one. The failures this agent actually has are **definition
failures, grain failures, environment failures and instrumentation failures** — all four are
failures of *what the agent knew and was required to check*, and all four are fixable in text.

| You want | What you actually need |
|---|---|
| "Make it stop assuming the stage ladder" | G3's blocking checkpoint, and an eval fixture that punishes a ported ladder |
| "Teach it our decline taxonomy" | A tenant file section in `journeys.md`, not a training set |
| "Make it faster on this engagement" | A tenant file that is current, so Phase 2 is a diff rather than a rediscovery |
| "Make it more careful about X" | A guardrail with a gate behind it. A guardrail with no assertion is a suggestion |
| "Make it sound more like us" | Nomenclature conventions in `profile.md` and the layout rules in Phase 7 |

If, after that, the need is genuinely weight-level — a domain vocabulary the model cannot
tokenise, a latency floor no prompt can reach — that is a platform conversation with the model
provider and it is out of scope for this plugin. Say so plainly rather than approximating it with
more prose.

---

## The ratchet

The existing rule is the spine of everything below:

> **Every failure becomes a test before it is fixed, and the same complaint from two teams becomes
> a guardrail, not a note.**

Two halves, and both matter.

**Test before fix.** A fix with no test is a fix that regresses the next time somebody refactors
the file that contained it. Writing the test first also forces you to state the failure precisely
enough to assert, which is where half of all "fixes" turn out to be fixing the wrong thing. Every
entry in the adversarial suite in
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/evals.md` §3 exists because it caught
something real on a live dashboard, and the suite only ever grows.

**Two teams, not two occurrences.** One team hitting the same thing twice is a tenant problem; two
teams hitting it once each is a structural problem. G8 exists because internal users turned out to
be a fifth of one programme's transactions and then showed up again elsewhere. The count that
promotes something is the count of *engagements*, not the count of incidents.

---

## The escalation ladder

Where a finding lands depends only on how many times it has been seen and whether fixing it
changes behaviour. Work down the table until a row's test is true.

| Rung | Trigger | What you write | Test for "is it on this rung?" |
|---|---|---|---|
| **1 · Caveat** | Seen **once**, on one engagement | A caveat on the **Definition Registry row** for the affected data point, with an owner | Could a reader of that one row have avoided this? If yes, stop here |
| **2 · Test** | Seen **twice**, anywhere | A regression test (`R-nn`) if it is a structural invariant, or an adversarial test (`A-nn`) if it is a question a reviewer should ask | Can you phrase it as an assertion with a true/false answer, or as a hostile question? Then it is a test |
| **3 · Guardrail** | The **same complaint from two engagements** | A new guardrail in [guardrails.md](guardrails.md), with the failure it is named after, plus the gate or regression test that enforces it | Does it change what the agent is allowed to do, not just what it should check? A guardrail can refuse work; a test only reports |
| **4 · Version bump** | Structural, or behaviour-changing | A semver bump per [versioning-and-sharepoint.md](versioning-and-sharepoint.md) §2, with release notes and an archived prior version | Would an existing session behave differently after this change? Then it is a bump, and the size of the bump is set by whether the *contract* changed |

Three things that keep the ladder honest:

- **Never skip to rung 3 because it feels important.** A guardrail that has been seen once is a
  guess dressed as a rule, and every unearned guardrail makes the earned ones cheaper.
- **Never stop below the rung the trigger demands.** A finding seen twice that stays a caveat is
  how the caveat list grows to forty items nobody reads.
- **Rung 2 is not optional on the way to rung 3.** A guardrail with no test behind it cannot be
  regressed, and per the eval harness, a harness failure that produces no new build-level test has
  taught the skill nothing.

---

## The knowledge-capture decision rule

**This is the most important section in this file.** When you learn a new fact during a build, it
has exactly one correct home, and the cost of getting it wrong is not tidiness. Tenant state
written into what were supposed to be portable playbooks is how a skill accumulates tens of
kilobytes of one engagement's live numbers, ladder and object ids — and then ports them,
confidently and wrongly, onto the next engagement.

### The decision procedure

Ask these in order and stop at the first yes.

1. **Is it true of this tenant only?** — a ladder, a literal, an object id, a dataset name, a
   known defect, a go-live date, a decline taxonomy, a PSP, an anchor value.
   → **`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/`**, in the right one of the five files.
2. **Is it true of this journey on any tenant?** — a funnel shape that recurs, a trap specific to
   repayment mandates, a dashlet set that every onboarding dashboard needs.
   → **The journey skill** (`onboarding-funnel`, `app-signup`, `transactions-spends`, `repayments`,
   `concentration-analysis`).
3. **Is it true of any journey on any tenant?** — a way of being wrong that does not care what the
   dashboard is about.
   → **The router `SKILL.md`, or a guardrail in [guardrails.md](guardrails.md).** Guardrail if it
   can refuse work; router if it is routing, sequencing or hierarchy.
4. **Is it a mechanical fact about Superset or the warehouse?** — an API behaviour, a dialect
   quirk, a viz-type limitation, a query pattern.
   → **`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/`**, in `superset-api.md`,
   `warehouse-gotchas.md`, `query-optimisation.md` or `dashboard-design.md`.

### The test

> **Would this sentence still be true on a different engagement? If not, it is tenant state.**

Apply it to the sentence you are about to write, not to the topic. "Decline taxonomies vary per
engagement and must be derived" passes — it is true anywhere, and it belongs in a skill. "The
decline taxonomy has nine categories, of which two are vendor-supplied" fails — it describes one
engagement and belongs in `journeys.md`. The topic is the same; only one of the two sentences is
portable.

Two corollaries that catch most of the leakage:

- **A worked example that only works on one engagement is tenant content.** If you want the
  example in a skill file, rewrite it with the tenant's specifics replaced by the shape — "a
  vendor-recorded population and a stream-recorded population that overlap partially", not the
  two table names.
- **An object id is never skill content.** Dataset ids, chart ids, dashboard ids and slugs belong
  in `inventory.md`, always, with no exceptions.

### Measure values

**Measure values are never skill content.** Counts, rates, currency amounts, shares, ratios — they
age in days, and they are the single largest source of contradictions between a skill file and
the live suite. They go in **tenant content only**, and **only with an as-of date**. Treat any
figure older than its dashboard's last-changed timestamp as unverified, and never quote one
without its date.

The one exception is a *ratio of kinds* stated as a range rather than a number: "event counts and
affected-entity counts routinely differ by a large multiple" is a portable warning; "declines
were 4.7× the affected users" is a tenant fact with a date.

### Where each of the five tenant files takes what

| Fact | File |
|---|---|
| Instance, database ids, schemas, timestamp offset, naming conventions | `profile.md` |
| Dashboards, charts, datasets, metric lists, source tables, ids and slugs | `inventory.md` |
| The live ladder, terminal states, bucket labels, decline categories, rails, FE event names | `journeys.md` |
| Numbered open items, known live defects, unresolved questions, each with an owner | `open-items.md` |
| What changed, when, under which skill version, and why | `revisions.md` |

---

## The skill release loop

### Changing a description without breaking triggering

**Descriptions are what the host matches on.** They are not documentation; they are the routing
surface. Editing one changes which requests reach which skill, and the two failure modes are
opposite and both silent.

- **Two skills claiming the same request.** Broaden one description into another's territory and
  the host picks arbitrarily. The tell: a request that used to reach the router now lands in
  `superset-build` and skips the model gate and prequalification entirely. This plugin keeps them
  apart by negative clauses — `superset-build`'s description ends by saying what to use instead
  for the model gate, prequalification, guardrails, routing, observability and context
  engineering. **Keep the negative clauses when you edit; they carry the boundary.**
- **A narrowed description silently ceasing to fire.** Trim the phrases a user actually types and
  the skill stops being selected, with no error anywhere. Nobody reports this — they just stop
  using it.

The procedure for any description edit:

1. **List the phrasings the skill must win**, from real requests, before you touch the text.
2. **List the phrasings a sibling skill must keep.** Write both lists down; they are the test.
3. Edit. **Keep the trigger vocabulary and the negative clauses**; the prose between them is what
   you may change.
4. **Re-run the routing check across all seven skills** against both lists. A request must reach
   exactly one skill and it must be the right one.
5. Check the hard limits below.

### The hard limits

| Field | Limit |
|---|---|
| A `SKILL.md` frontmatter `description` | **under 1024 characters** |
| The `plugin.json` `description` | **under 500 characters** |

Measure them, do not estimate them. Both are already close to their ceilings in this plugin, so an
addition usually means a deletion — and the thing you delete is prose, never trigger vocabulary or
a negative clause.

### The pre-release regression check

Run all five before any version ships. This is step 2 of the release protocol in
[versioning-and-sharepoint.md](versioning-and-sharepoint.md) §3; a version that fails does not
ship, it ships as a patch that fixes the diff.

| Check | What it asserts |
|---|---|
| **Doc-vs-live diff** | Every metric, column and bucket named in the docs exists live under that exact spelling — R-18 |
| **Internal consistency** | No two worked examples count the same population differently without saying why — R-20. The skill passing its own Gate 3 |
| **Cross-reference check (R-22)** | Every object, file and cross-reference named in the docs resolves: relative links to files that exist, `${CLAUDE_PLUGIN_ROOT}` paths to real skills, dashlets to charts that were actually built — R-19 |
| **Prescription check** | Every rule is one someone could follow tomorrow. A prescription with no procedure behind it is a slogan; either give it a procedure or delete it |
| **Model gate check** | The G1 language is intact in `SKILL.md` and in [guardrails.md](guardrails.md), and the per-phase model table still matches the phase loop |

The behavioural half of a release is the human harness, not these five:
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/eval-harness.md`. Any programmatic
dimension dropping to zero blocks a release regardless of the total score. Semver rules, archival
and the changelog format: [versioning-and-sharepoint.md](versioning-and-sharepoint.md).

---

## What feedback to collect, and from whom

The reviewer pack already exists — §7 and §8 of
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/eval-harness.md`. Send it to people who
know their engagement's data better than the agent does: the analyst who owns the numbers
leadership quotes, and the engineer who owns the pipeline behind them. One carefully-scored
fixture beats ten skimmed, and partial returns are useful.

**Its most valuable output is §8, the knowledge capture — not the scores.** The scores tell you
whether this version behaved; §8 tells you the ladder, the vocabulary, the tables that lie and the
things the agent should refuse on that engagement, and that content goes straight into
`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/` where it stops the next person re-deriving it differently.
A returned pack with every score blank and §8 filled is a good return. The reverse is not.

Then close the loop, in this order: reproduce and fix programmatic failures first; write the test
before the fix; promote anything seen on two engagements up the ladder; bump the version; archive
the prior one; and tell the reviewer what their review changed.
