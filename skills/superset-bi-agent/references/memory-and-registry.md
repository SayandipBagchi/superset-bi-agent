# Memory: the Definition Registry, the tenant file and the capsule

Author: Sayandip Bagchi.

This agent's failure mode is amnesia. A dashboard suite is built over many sessions by different
people, and the expensive artefacts - the derived ladder, the definitions, the adopt/supersede
calls - evaporate unless deliberately stored. `SKILL.md` has the five-store summary table; this
file has the formats.

---

## The five stores

Each has a job, and each fails differently when it is skipped.

## 5.1 Structured memory — the Definition Registry (the most important artefact)

Built in Phase 3, **before any chart exists**. One row per data point, not per chart. A data
point on two dashboards has **one** row.

| Data point | Definition in words | Source table | Column / event | Dataset id | Metric name | Grain | Inherited from | Used on |
|---|---|---|---|---|---|---|---|---|
| Spend-active account | Account with ≥1 posted transaction in range | `ledger_<tenant>.account_day_base` | `count_of_transactions > 0` | 45 | `se_spend_active_accounts` | account × day | supersedes the vendor-analytics "active users" dashlet | Txns, App sign-up |

The `Dataset id` and `Metric name` columns are new in v2.0 and non-optional: with ~170 metrics
across nine datasets, a Registry keyed only on prose cannot be traced back to an object.

Record adopt/adapt/supersede decisions from Phase 1 in "Inherited from". Any new chart needing an
existing data point uses the registered source; if it can't, that is a discussion with the user,
not a local workaround. **Ship the Registry with the dashboard.**

## 5.2 Long-term memory — the tenant current-state file

`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/`. This is the durable record of what is actually live, and it is the
single highest-value file in the skill. It holds:

- Host, dashboard ids **and slugs**, chart inventory with viz types, dataset ids and names.
- Every dataset's source tables and full metric list.
- **Every literal vocabulary**: the backend stage ladder in order, terminal states, segment
names, FE event names, every drop-off/outcome bucket label verbatim, decline categories,
repayment rails, state literals.
- Conventions in force: timestamp offset, title separators, prefix conventions.
- Known live defects with an owner.
- Sibling dashboards on the same instance that are reference dashboards whether or not anyone
said so.

**Read the tenant directory before Phase 2 on any work for that engagement** —
it turns a two-hour rediscovery into a five-minute diff.

## 5.3 Working memory — during a build

Hold, for the duration: the derived ladder, the Registry rows in play, the current storyboard,
and the reconciliation pairs. Do **not** hold raw dataset SQL for datasets you are not editing —
that is what evicts the things you need. Re-read from the tenant file instead.

## 5.4 Episodic memory — the session context capsule

Close every session with a capsule: model used, entry mode, what changed (dashboards, datasets,
charts, by id), which gates passed and which were skipped and why, open questions, and the next
action. Append it to the companion doc and to the SharePoint supporting-docs folder. The next
session starts by reading it.

## 5.5 File storage — versioned, in SharePoint

Skill docs, supporting docs and presentations live in a versioned SharePoint folder. Every change
to the skill bumps a version and archives the prior one. Protocol:
`versioning-and-sharepoint.md`.

## What *not* to store

Do not store measure values (counts, rates, £ figures) in the skill's reference files as if they
were facts. They age in days and they are the source of the contradictions the audit found. Store
them in dated companion docs and worked examples that carry their own as-of date, and treat every
figure older than the dashboard's last-changed timestamp as unverified.

---

