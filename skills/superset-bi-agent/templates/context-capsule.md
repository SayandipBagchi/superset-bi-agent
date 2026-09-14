# The session context capsule

Author: Sayandip Bagchi.

Close every session with one. A dashboard suite is built over many sessions by different people,
and the expensive artefacts — the confirmed ladder, the adopt/supersede calls, the object ids you
wrote — evaporate unless somebody writes them down at the end. The capsule is that writing-down. It
is episodic memory, and the next session starts by reading it. The spec is
[memory-and-registry.md](../references/memory-and-registry.md) §5.4; the handover discipline it
serves is [context-engineering.md](../references/context-engineering.md) §The capsule as handover.

---

## The skeleton

```
## Session capsule — <date>

**Model used:** <Opus 5 / Sonnet 5>, confirmed at G1 by <who>
**Entry mode:** <greenfield / extend / audit / port>
**Route:** <journey skill> · stopped at Phase <n>

**Confirmed ladder** (verbatim, confirmed by <who> on <date>):
<stage> → <stage> → <stage> → <stage>

**What changed**
- Dashboards: <id> <name> — <created / edited: what>
- Datasets:   <id> <name> — <created / edited: what>
- Charts:     <id> <name> — <created / edited: what>

**Registry rows added or changed**
- <data point> — <added / redefined: what moved>

**Gates**
- Passed:  <list>
- Failed:  <gate> — <what failed, and what was descoped or fixed>
- NOT RUN: <gate> — <why, in one clause>

**Eval suites:** golden <p/f/nr> · regression <p/f/nr> · adversarial <p/f/nr>

**Open questions**
1. <question> — owner <who>

**Open reconciliation pairs**
- <data point>: dataset <id> vs dataset <id> — <status>

**Files read this session:** <list>

**Next action:** <one instruction someone could follow cold>
```

## The rules

**Append it to two places: the companion doc, and the SharePoint supporting-docs folder.** The
companion doc copy is what a stakeholder finds; the SharePoint copy is what survives the dashboard
being rebuilt. Protocol in
[versioning-and-sharepoint.md](../references/versioning-and-sharepoint.md).

**The next session starts by reading it.** Which means it is written for a reader who was not
there and has no memory of the conversation. "Fixed the funnel" is not a capsule entry. "Chart 151
re-dated from event date to cohort date, because the March step went up" is.

**A gate that was not run is recorded as NOT RUN with the reason. Never omitted, never reported as
passed.** A gate you could not run in your operating mode — a render check with no browser, a
vendor triangulation with no vendor access — is a known hole, and a known hole is survivable. A
silently skipped gate is indistinguishable from a passed one, and that is not.

**Objects go in by id.** The ids are the undo list. A capsule that says "created the repayments
dashboard" leaves the next person enumerating the instance to find out what to roll back.

**The ladder goes in verbatim, not as a pointer.** "As confirmed in `journeys.md`" is what the
capsule is meant to replace. Write the stages out.

**One next action, phrased as an instruction.** Not a status, not a list of everything outstanding
— the outstanding work is the open-items file. The capsule names the single thing to do first.

## What the capsule must carry so nothing is re-read

This is the test, and it comes from
[context-engineering.md](../references/context-engineering.md): **could the next session do useful
work having opened the capsule and exactly one other file?** If not, it is a log rather than a
handover.

That test is what forces the fields above. Model and entry mode mean G1 and the phase sequence
resolve without reasoning. The verbatim ladder means Phase 2 is not re-derived — re-derivation is
the silent failure this whole discipline exists to prevent, because a second derivation is never
shown to the user for confirmation. Object ids mean the instance need not be enumerated. Gate
verdicts mean QC resumes rather than restarts. "Files read this session" means the next session
knows what has already been checked, which is the difference between reading one file and reading
nine.

## One worked capsule

A mid-build session on a generic engagement, extending an existing suite.

> ## Session capsule — 2026-03-11
>
> **Model used:** Opus 5, confirmed at G1 by the requester
> **Entry mode:** extend
> **Route:** `repayments` · stopped at Phase 8
>
> **Confirmed ladder** (verbatim, confirmed by the product lead on 2026-03-04):
> Mandate requested → Mandate active → Collection scheduled → Collection presented → Collection
> settled, with terminal states Failed and Returned
>
> **What changed**
> - Dashboards: 15 `Repayments` — added the month-wise section at the foot
> - Datasets: 43 `repayment_objects` — added `f_mandate_returned`, partitioned the decile
>   window by `user_type`
> - Charts: 151 `Outcome of everyone · Mandates` created; 152 `Headline · Collections` edited to
>   add the unique-account denominator beside the event count (G11)
>
> **Registry rows added or changed**
> - Mandate returned — added; source `card_core_service_<tenant>.payment_audit`,
>   `status = 'RETURNED'`
> - Collection presented — redefined; was event-dated, now cohort-dated on mandate activation
>
> **Gates**
> - Passed: 0, 0b, 0c, 0d, 1, 1b, 2, 3, 6
> - Failed: none
> - NOT RUN: 4 — PSP portal access not granted, so the vendor-side settlement count could not be
>   triangulated. Raised as open item 14.
> - NOT RUN: 5 — REST-only session, no browser, so the render check on chart 151 is unverified.
>
> **Eval suites:** golden 11/0/0 · regression 9/0/2 · adversarial 26/3/1
>
> **Open questions**
> 1. Are returns re-presented automatically, or is a return terminal? Affects whether the funnel
>    is monotonic by construction — owner: the payments lead.
>
> **Open reconciliation pairs**
> - Collections settled: dataset 43 vs dataset 45 (ledger) — 0.4% gap, unexplained, open.
>
> **Files read this session:** router `SKILL.md`, `repayments/SKILL.md`, `qc-protocol.md`,
> `tenants/<name>/inventory.md`, `tenants/<name>/open-items.md`
>
> **Next action:** get PSP portal access and run Gate 4 on collections settled before this
> dashboard is shown to anyone outside the team. Do not publish chart 151 until Gate 5 is run in
> a browser.

**How to use it.** Fill the skeleton at the end of the session, not from memory the next morning.
Where this template and [memory-and-registry.md](../references/memory-and-registry.md) §5.4
disagree on the field set, the reference wins; where the capsule and the live instance disagree
about what exists, the instance wins and the capsule was written carelessly.
