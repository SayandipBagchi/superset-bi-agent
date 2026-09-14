# The companion doc

Author: Sayandip Bagchi.

The dashboard is the interface and this document is half of it. A dashboard shipped without a
written companion gets misread inside a week: somebody quotes a number with the wrong population,
somebody else finds a chart that disagrees, and the suite loses its credibility in a meeting you
are not in. **The companion doc always ships.** This file is the authoritative list of what it must
contain — eight sections, none of them optional — and the rules that make each one worth reading.

---

## The skeleton

```
# <Dashboard name> — companion doc

**As of <date>. Dashboard last changed <timestamp>. Built on <model>. Version <semver>.**

## 1 · How it is built
Datasets, source tables and the layer each one reads. The filter targets.

## 2 · Definition Registry
The full nine-column table. One row per data point.

## 3 · The stage ladder
As derived, verbatim, in order. Who confirmed it and when.

## 4 · What the numbers say now
The headline reading, dated. Each figure with its Registry data point.

## 5 · Reference-dashlet reconciliation
Every adopt / adapt / supersede call, with the old number and the reason for the difference.

## 6 · Caveats
Numbered. Each with an owner.

## 7 · Eval results
Per suite: pass / fail / not-run, dated.

## 8 · Session context capsule
The capsule, appended. Model used, entry mode, what changed by id, gates, next action.
```

## The rules, section by section

**1 · How it is built.** List every dataset by **id and name**, its source tables fully qualified,
and the **layer** each table belongs to — ledger, switch, event stream, core-service audit, vendor
analytics, BI rollup. Naming the layer is what lets a reader see why two dashlets on the same page
legitimately differ. Then list the native filter targets, one per dataset: a multi-dataset
dashboard whose date filter names only one dataset silently shows several different periods with
no error, so if there are four datasets there must be four targets, and the doc is where that is
checked from outside.

**2 · Definition Registry.** The full table, in full, inline. Not a link, not a summary of the
interesting rows. Columns and rules are in
[the Definition Registry template](definition-registry.md). A reader who wants to know where a
number came from has to find it in the document they already have open, or they will ask in a
meeting instead. Gate 1 requires every published metric to map to exactly one row; this section is
where that claim is checkable.

**3 · The stage ladder.** As **derived**, verbatim, and **in order**. Not tidied, not renamed into
something more readable, not reordered to match the PRD. Use the warehouse's own literals and, where
they are unfriendly, put the plain-English gloss beside them rather than instead of them. Record
who confirmed the ladder and on what date — that confirmation is the Phase 2 blocking checkpoint,
and a ladder with no name against it was assumed.

**4 · What the numbers say now.** The reading, dated, and **stamped with the dashboard's
last-changed timestamp**. Both dates, because they answer different questions: the as-of date says
when the figures were taken, the last-changed timestamp says whether a definition has moved under
them since. Any figure older than the last-changed timestamp is unverified and must be labelled so.
Every figure names its Registry data point. Keep this section short; it is the reading, not the
analysis.

**5 · Reference-dashlet reconciliation.** One entry per reference dashlet reviewed in Phase 1,
including sibling dashboards nobody linked you to. Each entry states the call — **adopt**, **adapt**
or **supersede** — the old number, your number, and the reason for the difference. G5 forbids
superseding silently, and this section is where the obligation is discharged. "Adopted, unchanged"
is a legitimate entry and still gets written down, because the next person needs to know the
dashlet was looked at rather than missed.

**6 · Caveats.** A numbered list. **Every caveat has an owner** — a person, not a team, not "TBD".
A caveat without an owner is a disclaimer, and disclaimers do not get fixed. What lands here: the
unexplained residuals, the instrumentation holes, the date-cut-only internal-user rule, the
timestamp offset that disagrees with the market, the adversarial failures you chose not to fix, and
any gate reported NOT RUN. Numbering matters because these get referenced from the open-items file
in `${CLAUDE_PLUGIN_ROOT}/tenants/<name>/open-items.md`.

**7 · Eval results.** A table, dated, with **pass / fail / not-run counts per suite** — golden,
regression, adversarial. Not a sentence saying the evals ran. A suite you could not run in your
operating mode is reported NOT RUN with the reason, never as passed, and the same holds for the
gates in section 6. Definitions of the suites are in
`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/evals.md`.

> | Suite | Pass | Fail | Not run | Run on |
> |---|---|---|---|---|
> | Golden | 12 | 0 | 0 | 2026-03-11 |
> | Regression | 9 | 0 | 2 | 2026-03-11 |
> | Adversarial | 26 | 3 | 1 | 2026-03-09 |
>
> *The three adversarial failures are caveats 4, 5 and 7. The two regression not-runs need a
> browser; this was a REST-only session.*

**8 · Session context capsule.** Appended verbatim from
[the context capsule template](context-capsule.md), including **the model used**. The capsule is
what lets the next session resume rather than restart, and the companion doc is one of its two
homes — the other being the SharePoint supporting-docs folder. Append, do not overwrite: the
capsules accumulate, newest last, and together they are the build's history.

## The verbal handoff

The doc is what they read. The handoff is what you say, and it is **two or three sentences**: the
headline finding, the biggest loss, and the one data-quality item that needs an owner. Nothing
else — no tour of the sections, no caveat list read aloud. They will read the doc if they want the
rest, and they are far likelier to read it if you have not already recited it.

**How to use this file.** Draft the doc from a completed Registry rather than from the dashboard;
if you find yourself opening a build reference to write it, the Registry is incomplete and that is
the real finding. Where this template and a section's own authority disagree — the Registry
columns, the capsule fields, the eval definitions — that authority wins and this list simply says
the section must be present. Where the doc and the live dashboard disagree, the dashboard wins and
you have doc-vs-live drift, which Gate 6 treats as a defect rather than a documentation chore.
