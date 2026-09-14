# Observability: watching the dashboards, and watching yourself

Author: Sayandip Bagchi.

Gates tell you whether this build is sound at the moment you publish it. Nothing in the gates runs
again afterwards. A suite that passed every gate in July can be quietly wrong by September because
a source stopped refreshing, a state literal was renamed, or a bucket in the companion doc no
longer exists live. This file is the standing discipline that closes that gap, and it has two
layers: observing the **dashboards** you built, and observing the **agent** that built them.

---

## Layer 1 · Observing the dashboards

### Freshness SLAs, one per source table

Gate 0 records `max(time_col)` once, at build time, and then never looks again. Promote that
single reading into a contract.

**Set the SLA from the table's own refresh cadence plus a tolerance**, never from a round number
you liked. Ask the pipeline owner how often the table is written; if nobody knows, observe
`max(time_col)` at three points a day for a week and take the worst observed lag as the cadence.

| Field | How to set it |
|---|---|
| **Cadence** | The interval at which the table is actually written — hourly, T-0 intraday, T-1 overnight, T-3 settlement |
| **Tolerance** | One full cadence period, plus the longest routine late run you observed. An overnight table with a 06:00 target and a worst observed finish of 08:40 gets a tolerance to 09:30, not to 06:15 |
| **Stale** | `now() - max(time_col) > cadence + tolerance` |
| **Measured on** | The atomic event timestamp, not an `updated_at` that a backfill touches |
| **Owner** | A named person for the pipeline, not a team alias |

**What "stale" means for a dashboard, not just for a table.** A dashboard is stale when *any*
source behind a number on it is stale, and the damage depends on where the table sits:

- **A stale denominator with a fresh numerator inflates every rate on the page.** This is the worst
  case and it always looks like good news. Flag it first.
- **A stale downstream table under a fresh upstream one** reads as a widening loss in the
  auth-to-ledger chain that is entirely artificial.
- **Two sources at different lags in one funnel** produce a false drop at the step where the lag
  changes. Record each source's lag per page, not per suite.

Publish the per-source lag on the dashboard header, not only in the companion doc. A reader who
cannot tell how fresh a number is cannot tell whether a fall is real.

### The health dashlet set

Every mature suite carries these. They are cheap, they read the same datasets the suite already
has, and each one is the detector for a failure that is otherwise invisible.

| # | Dashlet | Reads | What it catches |
|---|---|---|---|
| H1 | **Row count by day, per source table** | Each spine table | A pipeline that stopped, a partial load, a backfill that doubled a day |
| H2 | **Null rate per join key, by day** | Each join used in a semantic dataset | A key that starts arriving empty. Watch the empty string as well as `NULL` |
| H3 | **Orphan rate on each entity bridge** | Both sides of every bridge | The bridge degrading. Check it on the failing rows specifically (G11) |
| H4 | **Last-refresh timestamp per dataset** | `max(time_col)` per source | Freshness SLA breaches, and the relative-lag traps above |
| H5 | **"Other" / unattributed bucket as a share of its parent** | Every bucket dimension | A taxonomy going out of date as new literals appear (G6) |
| H6 | **Internal / pre-go-live share of the population** | The `user_type` dimension (G8) | A staff flag that stopped being set, or a date cut that has drifted |

H5 is the one people skip and the one that pays. A residual bucket growing from 3% to 18% is the
earliest visible sign of schema drift, and it shows up before anyone notices the funnel is wrong.

### Thresholds: what logs, what pages

Two levels only. A third level is a level nobody acts on.

| Condition | Level |
|---|---|
| Source within SLA, row count within ±20% of its trailing-28-day median | **Nothing** |
| Row count outside ±20% of the trailing median, one day | **Log** — note it, watch the next run |
| Null rate on a join key up more than 5 percentage points week on week | **Log** |
| "Other" bucket share up more than 5 percentage points week on week | **Log** |
| Orphan rate on a bridge up at all, on the failing-row subset | **Log**, and open an item |
| Any source past its freshness SLA | **Page** |
| Row count zero for a day on any spine table | **Page** |
| A golden anchor on a frozen closed period moves by any amount | **Page** — this is a correctness alarm, see below |
| A metric on a shared data point disagrees across two dashboards | **Page** — Gate 3 has regressed |
| Doc-vs-live name check fails (R-18) | **Log** before a release, **page** if it fires on a published suite |

Page means a human is interrupted. Reserve it for conditions where the dashboard is currently
lying to somebody, and keep the paging list short enough that it is still believed in six months.

### Use the pulse report as the alerting surface

Do not build alerting infrastructure. **The scheduled pulse report already described in `SKILL.md`
is the alerting surface.** It has a schedule, a recipient list and a permission model, and it is
the thing the audience already reads.

1. Build a **health dashboard** carrying H1 to H6, with the paging conditions expressed as chart
   thresholds and the logging conditions as trend lines.
2. Attach a Superset **report schedule** to it at the cadence of the fastest source it watches.
3. Add an **alert** (not a report) for each paging condition, so the mail only arrives when
   something is wrong. A daily "all clear" is read for two weeks and then filtered.
4. Confirm `ReportSchedule` permissions in Phase 0. The feature flag being on does not mean the
   role has them, and discovering this at handover costs a week.
5. Route the health alerts to the **pipeline owner named in the SLA table**, and the definition
   alerts to whoever owns the Definition Registry. They are rarely the same person.

---

## Layer 2 · Observing the agent

A later reviewer must be able to reconstruct how a build was produced without asking you. Record
the following during the build, not after it.

| Record | Why a reviewer needs it |
|---|---|
| **Route taken and entry mode** | Which journey skill owned the request, and greenfield / extend / audit / port. A port that skipped Phase 1.5 is a defect you can only see here |
| **Model used** | G1. Opus 5 or Sonnet 5, and which phases ran on which if the session switched |
| **Phase completion, with durations where available** | A phase that took two minutes was not performed. Completion alone is enough if timing is not available |
| **Every gate: passed / failed / not run, and why** | "Not run" is a legitimate state in non-browser modes. An inferred pass is not |
| **Which reference files were loaded** | Tells a reviewer what the build could and could not have known. A Gate 4 pass with `reference-dashboards.md` never opened is suspect |
| **Reconciliation pairs opened and closed** | The count of each, and the identity of every pair left open |
| **What was left open** | Open items with owners, unresolved questions, dashlets descoped past a failing gate |
| **Objects written, by id and type** | Datasets, charts, dashboards. This is the undo list |

**The session context capsule is the trace record.** It already carries model, entry mode, what
changed by id, gates passed and skipped, open questions and the next action — see
[the context-capsule template](../templates/context-capsule.md), with the field list in
[memory-and-registry.md](memory-and-registry.md). This file **extends** it; it does not
replace it. Add four fields to the capsule you already write:

- `route` — journey skill and entry mode.
- `files_loaded` — the reference files actually opened this session.
- `phases` — each phase with completed / partial / skipped and the reason for anything not
  completed.
- `recon_pairs` — opened, closed, still open, by data point.

One capsule per session, appended to the companion doc. A suite with six capsules has a build
history; a suite with none has folklore.

### A failure taxonomy

When something goes wrong, name which of these it is before you start fixing. The wrong
classification sends you to the wrong gate and you fix a symptom.

| Failure | The tell | Where it should have been caught |
|---|---|---|
| **Definition failure** | Two numbers that should match don't, and both queries are correct | Gate 1, Gate 3 |
| **Grain failure** | A count is an implausible multiple of another — 5×, 7× — or a funnel step rises | Gate 0 (grain confirmation), Gate 2 |
| **Environment failure** | Everything reconciles perfectly and no figure matches anything the business quotes | Gate 0 / G10, and only the known-good anchor settles it |
| **Instrumentation failure** | A step is zero, or flat, or stops on a fixed date | G9, Phase 1.5, adversarial A-35 and A-48 |
| **Render failure** | The number is right and nobody can see it — blank grid, orphan component, shuffled table | Gate 5a for association, 5b for pixels |

Definition and grain failures are the expensive pair: both survive review, because the page is
internally consistent. Environment failure is the most expensive of all, because it survives
*everything* — UAT reconciles against itself perfectly.

---

## Drift detection

Three kinds. The plugin already detects the third and nothing else. Each gets a detector, a
cadence, and an action.

### 1 · Schema drift

**What changes.** A column appears, disappears or changes type. A state literal stops being
emitted. A new state literal appears that no bucket claims.

**Detector.** Re-run the distinct-values-with-first-seen-date query over every literal vocabulary
in the tenant's `journeys.md` — the stage ladder, terminal states, decline categories, repayment
rails, outcome buckets — and diff the result against the file. Two columns matter: the value set,
and `min(event_ts)` per value. A new value with a first-seen date inside the last week is drift; a
new value with a first-seen date clustered into a few hours on one day is an **incident**, not
drift, and it needs escalating rather than reconciling. Run an `information_schema` diff alongside
it for the column set and types. Method:
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/schema-discovery.md`.

**Cadence.** Weekly, and again before any release.

**When it fires.** A disappeared literal means a chart is now reporting a permanent zero as
behaviour — treat it as an instrumentation failure and check the feature flag before the data. A
new literal falls into "Other" until somebody classifies it, so check H5 for the size of what you
have been silently bucketing. Update `journeys.md` in the tenant directory, log the change in
`revisions.md`, and if any published bucket definition changed, that is a G5 supersession with an
old-vs-new sentence, not a quiet edit.

### 2 · Metric drift

This one has two halves and conflating them is the reason it is usually done badly.

**Half A — the frozen anchors. This is a correctness alarm, not drift.** The golden anchor set is
defined on a **closed** period, exact-match, no tolerance
(`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/evals.md` §1). A closed period cannot
legitimately move. If a golden anchor moves **by any amount**, something was restated, a definition
changed, or a dataset was edited — page someone. Never widen the tolerance, and never update the
expected value before writing down in the changelog why it moved.

**Half B — the rolling comparison on open periods. This is drift.** Open periods are *supposed* to
move; that is what open means. So the alarm cannot be on the level. **Alarm on the rate of
change**: compute each registered definition week on week over a rolling window and flag a
movement outside its own trailing behaviour — a practical default is more than two standard
deviations of that metric's own trailing-eight-week change, with an absolute floor so a low-volume
metric does not alarm on three rows. Then ask the only question that matters: **is there a release
behind it?** Check `revisions.md` and the changelog. Movement with a release behind it is expected
and gets a changelog line. Movement with no release behind it is the finding.

Keep the two sets in separate tables with separate owners. A team that has learned to widen a
tolerance on a rolling metric will widen it on a frozen anchor too, and the day that happens the
golden set stops being worth running.

**Cadence.** Frozen anchors: before every publish, and weekly thereafter. Rolling comparison:
weekly.

**When it fires.** Frozen anchor moved — stop, find the cause before publishing anything else.
Rolling metric outside band with no release — open a numbered item, check the health dashlets
first (a freshness breach explains most of these), and if the sources are healthy, it is a real
change in the business or a real change in the data and both deserve a sentence to the owner.

### 3 · Doc-vs-live drift

**Already specified. Do not re-specify it.** Every metric, column and bucket named in the docs must
still exist live under that exact spelling. This is regression test **R-18** in
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/evals.md` §2.3, and it sits alongside R-19
(a dashlet the docs call essential exists live or is an open build ask) and R-21 (every figure is
stamped against its dashboard's last-changed time). Run those three as one check.

**Cadence.** Before every release — it is a blocking item in the release protocol in
[versioning-and-sharepoint.md](versioning-and-sharepoint.md) §3 — and quarterly on any published
suite nobody has touched.

**When it fires.** Before a release it is a patch that fixes the diff, not a note. On a published
suite it means somebody renamed an object without updating the companion doc, so find the rename
in `revisions.md` and repair the doc, the tenant file and the Registry row together.

---

## What observability produces

Never nothing. Every observation that fires becomes one of three things, with an owner and a date:
a **doc fix**, a **build ask** ticketed against the dashboard, or a **caveat shipped on the page**.
If the same observation fires on two engagements, it has stopped being an observation and become a
guardrail candidate — take it to the escalation ladder in [fine-tuning.md](fine-tuning.md).
