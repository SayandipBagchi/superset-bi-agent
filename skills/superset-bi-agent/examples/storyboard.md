# A worked storyboard

Author: Sayandip Bagchi.

Phase 5 is where a chart collection becomes a dashboard. You write the dashlet list as a narrative
*before* you build anything: each dashlet gets a one-line question it answers and a level in the
L1–L4 descent, and the page passes when reading the titles top to bottom tells the story without
the numbers. This page shows the standard arc filled in for one journey, the title test applied to
it, and what the same journey looks like when the storyboard is skipped. The arc itself is
specified in
[`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/SKILL.md`](${CLAUDE_PLUGIN_ROOT}/skills/superset-build/SKILL.md)
Phase 5; this is a worked instance of it.

---

## The skeleton

```
Journey: <journey> · Dashboard: <name> · Population: <the one population every dashlet is scoped to>

| # | Title | Question it answers | Level |
|---|---|---|---|
| 1 | Pre-funnel · <…>            |  | L1/L2 |
| 2 | Headline · <…>              |  | L1    |
| 3 | <Journey> funnel · <…>      |  | L2    |
| 4 | Sub-funnel · <…>            |  | L2    |
| 5 | Where it breaks · <…>       |  | L3    |
| 6 | Why it breaks · <…>         |  | L4    |
| 7 | Outcome of everyone · <…>   |  | L3    |
| 8 | Month-wise · <…>            |  | all   |
```

## The rules

- **Eight dashlets is the arc, not a quota.** Drop a row only when the journey genuinely has no
  such thing — no pre-funnel where there is no eligibility step — and say in the storyboard why.
- **Every level reconciles upward.** L4 buckets sum to their L3 stage, L3 sums to the L2 step,
  L2's entry and exit are the L1 population. Where they do not, the residual is named.
- **Scope every dashlet to the same population**, and say so in the title where it differs.
- **Month-wise tables sit at the foot of their section.** Never interleaved with the funnels.
- **A reader starting at dashlet 2 must arrive at dashlet 6 without asking a question the page has
  not already answered.** If they cannot, the storyboard is wrong — not the data.

## The worked arc

An onboarding journey on a generic card programme, population: all applicants who started an
eligibility check on or after go-live, internal users excluded.

> | # | Title | Question it answers | Level |
> |---|---|---|---|
> | 1 | Pre-funnel · Eligibility check to quotation accepted | Of everyone who asked, how many got an offer they took? | L1/L2 |
> | 2 | Headline · Applications started and the approval rate | How is onboarding doing, in one population and one rate? | **L1** |
> | 3 | Onboarding funnel · Quotation accepted to card issued, cohort-dated | Where in the sequence do we lose them? | **L2** |
> | 4 | Sub-funnel · By acquisition source (aggregator, direct, referral) | Do the sources lose people at the same places, or are we averaging two different products? | L2 |
> | 5 | Where it breaks · Stage × outcome: declined, abandoned, still open | At the worst stage, is this our decision or their behaviour? | **L3** |
> | 6 | Why it breaks · Reason per major loss stage, with the front-end cross-check | Why do we decline them, and how far into the screen did the ones who walked away get? | **L4** |
> | 7 | Outcome of everyone · Final resting state, shares to 100% | Is anybody unaccounted for? | L3 |
> | 8 | Month-wise · Onboarding funnel by calendar month | Is any of this moving, and since when? | all |

Dashlet 5 is the one that earns the dashboard. Until you split declined from abandoned, the worst
funnel step is a number nobody can act on: a decline is a policy conversation and an abandonment is
a design one, and they sit in the same bar.

## The title test

Read the titles alone, in order, with no numbers on the page:

> Pre-funnel · Eligibility check to quotation accepted
> Headline · Applications started and the approval rate
> Onboarding funnel · Quotation accepted to card issued, cohort-dated
> Sub-funnel · By acquisition source
> Where it breaks · Stage × outcome: declined, abandoned, still open
> Why it breaks · Reason per major loss stage, with the front-end cross-check
> Outcome of everyone · Final resting state, shares to 100%
> Month-wise · Onboarding funnel by calendar month

That narrates: here is everyone who asked and how many got an offer; here is the headline; here is
where the sequence loses them; here is whether the sources behave differently; here is whether the
worst stage is a decision or a walk-away; here is why; here is what became of every single person;
here is whether it is moving. A stakeholder who reads only the left-hand column of the page knows
what the dashboard is for. **If the titles do not do that, rewrite the storyboard, not the charts.**

## What a bad storyboard looks like

Same journey, same data, no descent. Each of these has shipped somewhere.

- **A chart collection.** Eight dashlets, all L2 or all L4, in the order somebody thought of them:
  applications by day, KYC pass rate, a decline pie, a map, applications by day again but by
  source. Nothing answers a question raised by the thing above it, so the reader picks whichever
  chart supports the point they arrived with.
- **A headline that cannot be decomposed.** An approval-rate tile at the top with no funnel
  underneath it that adds up to the same population. It is a vanity metric the moment someone asks
  which stage moved, and the answer is not on the page — which means the answer gets produced ad
  hoc, from a different query, and disagrees.
- **Month-wise tables interleaved with the funnels.** A calendar table between dashlet 3 and
  dashlet 5 breaks the descent in half. The reader is pulled from "where do we lose them" into
  "what happened in February" and never gets back to the reason detail, which is the only section
  with an action in it.
- **A sub-funnel with a different population.** Dashlet 4 quietly drops the internal-user filter.
  It disagrees with every sibling, nobody knows which is right, and both get quoted.

## The repeat-entity block

**Where a module's headline is an event count — declines, failures, retries, errors — the arc
gains a block.** An event count is not a population (G11), and "N declines" is not a work queue
until you know how many entities they landed on. Add, inside that module:

| Add | What it shows | Level |
|---|---|---|
| Unique entities affected | How many distinct accounts or applicants the events actually hit | **L1** |
| Attempts per entity, in fixed bands | Whether this is many people once or few people many times | L3 |
| Concentration by decile, with cumulative share | What share of events the worst 10% of entities produce | L3 |
| Composition by band × reason | Whether the repeat population fails for a different reason than the one-off population | **L4** |

The last row is where the block pays for itself: heavy repeaters usually fail for one fixable
reason, and that reason is invisible in the overall reason split because the one-off population
outnumbers them. The bands must be fixed and stated, the deciles must be computed over the whole
population with the window partitioned by every dimension a chart may later filter on, and the
final cumulative share must be exactly 100.0%. Method:
[`${CLAUDE_PLUGIN_ROOT}/skills/concentration-analysis/SKILL.md`](${CLAUDE_PLUGIN_ROOT}/skills/concentration-analysis/SKILL.md).
