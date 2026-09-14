# The Definition Registry

Author: Sayandip Bagchi.

This is the Phase 3 artefact, and it is the most important thing you produce. Build it **before any
chart exists**. One row per data point, never per chart: a data point that appears on two
dashboards has **one** row, and both dashboards read it. The Registry is what makes "two numbers
that should match" a structural property of the build rather than a thing you hope for. The
specification it implements is [memory-and-registry.md](../references/memory-and-registry.md) §5.1;
this file is the fill-in form.

---

## The columns

Nine, all of them required. Each one exists because leaving it out has cost somebody a rebuild.

**Data point.** The concept in stakeholder language, not in column language. "Spend-active
account", not `count_of_transactions > 0`. This is the name that appears in a conversation.

**Definition in words.** One sentence a non-analyst can check. Include the window and the
qualifying condition. If you cannot write it in a sentence, you have two data points.

**Source table.** Fully qualified — schema and table. Name the layer in your head as you write it:
ledger, switch, event stream, core-service audit, vendor analytics, BI rollup. You never add across
layers.

**Column / event.** The literal column, expression or event name, spelled exactly as the warehouse
spells it. Verbatim, including case and underscores.

**Dataset id.** The Superset dataset the metric lives on, by numeric id.

**Metric name.** The Superset metric name, following the tenant's naming convention.

**Grain.** The entity and period one row represents — `account × day`, `application`,
`mandate × month`. A grain mismatch between two rows is the reconciliation failure you have not
found yet.

**Inherited from.** The Phase 1 call: adopt, adapt or supersede, and what from. Name the reference
dashlet and the reason.

**Used on.** Every dashboard the data point appears on. This column is how you know which
dashboards to re-check when a definition changes.

## The table to fill

```
| Data point | Definition in words | Source table | Column / event | Dataset id | Metric name | Grain | Inherited from | Used on |
|---|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |
```

## The rules

**`Dataset id` and `Metric name` are not optional.** A mature suite carries well over a hundred
metrics across nine or more datasets. A Registry keyed only on prose cannot be traced back to an
object, which means nobody can confirm that the row and the chart describe the same thing. A row
without an id and a metric name is a note, not a Registry row.

**Record every adopt / adapt / supersede decision in "Inherited from".** That is where the Phase 1
reference review lands. Superseding silently is G5, and G5 is the guardrail that costs the most
credibility when it is broken — state the old number, yours, and the reason for the difference.

**Any new chart needing an existing data point uses the registered source.** Not an equivalent
table, not a quicker join, not a chart-level aggregate that happens to agree today. If the
registered source genuinely cannot serve the chart, that is a discussion with the user about
changing the row — never a local workaround in one chart's SQL. A local workaround is exactly how
the two-numbers problem is born.

**A row is added before the chart, not after it.** Registry coverage is a Gate 1 check: every
published metric maps to exactly one row. Backfilling rows from finished charts inverts the point
of the exercise, because by then the definition is whatever the SQL happened to say.

**One row, one definition.** If two dashboards reach the same data point through two datasets, the
row still stays single, and the pair goes on the Gate 3 reconciliation list in
`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/open-items.md`.

**Never store a measure value in the Registry.** Counts, rates and currency figures age in days.
They belong in the dated companion doc, carrying their own as-of date.

## One worked row

A generic engagement, mid-build, with one reference dashlet already decoded.

> | Data point | Definition in words | Source table | Column / event | Dataset id | Metric name | Grain | Inherited from | Used on |
> |---|---|---|---|---|---|---|---|---|
> | Spend-active account | Account with at least one posted transaction in the reporting window | `ledger_<tenant>.account_day_base` | `count_of_transactions > 0` | 45 | `se_spend_active_accounts` | account × day | **Supersedes** the vendor-analytics "active users" dashlet, which counted app opens rather than posted spend | Transactions, App sign-up |
> | Mandate set up | Mandate reaching an active state with the PSP, first occurrence per account | `card_core_service_<tenant>.automatic_payment_config_audit` | `status = 'ACTIVE'` | 43 | `f_mandate_active` | mandate | **Adopted** from the repayments reference dashboard, window and analysis type unchanged | Repayments |
> | Application declined at decisioning | Application reaching a terminal declined state at the decisioning stage, cohort-dated on application start | `events_raw.raw_events_data` | `state = 'DECLINED'` | 41 | `f_declined_decisioning` | application | **Adapted** from the onboarding reference funnel: same state literal, but cohort-dated on start rather than event-dated, because event-dating made the funnel go up in month boundaries | Onboarding |

Note what each "Inherited from" entry does. It does not say "from the old dashboard". It says which
call was made and what the difference was, so that the next person who finds the old number can see
in one line why yours differs from it.

## How it ships

The Registry ships **with the dashboard**, in full, inside the companion doc — see
[the companion-doc template](companion-doc.md). Not as an attachment, not as a link to a working
file, and not as a summary of the interesting rows. A reader who wants to know where a number came
from must be able to find it in the same document they are already reading, or they will ask in a
meeting instead.

**How to use this file.** Fill the blank table during Phase 3 and keep it as your working copy for
the session; the rows in play are one of the four things that must survive to the end of the
session (see [context-engineering.md](../references/context-engineering.md)). Where this template
and the spec in [memory-and-registry.md](../references/memory-and-registry.md) appear to disagree,
the spec wins — this file is a convenience form over it, not a second authority. Where the Registry
and a live chart disagree, neither wins automatically: that is a Gate 1 failure, and you stop and
find out which one is wrong before publishing anything.
