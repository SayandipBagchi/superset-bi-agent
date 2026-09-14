# Context engineering: what you are allowed to hold open

Author: Sayandip Bagchi.

One line in [memory-and-registry.md](memory-and-registry.md) §5.3 governs everything here: *do not
hold raw dataset SQL for datasets you are not editing — that is what evicts the things you need.*
This file promotes that line into a discipline. The plugin is roughly half a megabyte of skill
files, reference files and tenant state, and a single tenant's `journeys.md` is larger than most
of the reference files put together. You cannot hold it all, you do not need to, and trying is how
builds go wrong.

---

## Why this is a correctness concern, not an efficiency one

The tempting framing is cost. It is the wrong one. **The failure mode is that the derived ladder
gets evicted around Phase 5 and is silently re-derived, differently, at Phase 8 in the same
session** — and the second derivation is never shown to the user for confirmation, because
confirmation already happened. You then ship two definitions of the same funnel under one Registry
row, and Gate 3 passes because both dashboards read the second one while the companion doc
describes the first.

Nothing catches that. Not a gate, not a regression test, not a reviewer. The only defence is not
letting the ladder get evicted, which means not loading the things that evict it.

---

## The loading budget

Three rules. They hold in every entry mode.

1. **The router `SKILL.md` is always in context.** It is the one file you never evict: it carries
   the guardrail table, the phase loop, the L1–L4 hierarchy and the routing decision. If you have
   lost track of which guardrail forbids what, you have lost the router and should re-read it
   before anything else.
2. **Exactly one journey skill per request.** Not two, not "both, because the funnel crosses
   them". A request spanning onboarding and app sign-up is two sequential requests with a handover
   between them, not one session holding two ladders. Two ladders in context is how one journey's
   stage names end up in the other's Registry rows.
3. **At most two reference files open at once.** One is normal. Two is for the cases where a
   procedure in one genuinely needs a lookup in the other — Gate 4 open beside
   `reference-dashboards.md`, say.

**When you think you need a third: you almost certainly need to finish the current phase first.**
Wanting a third file is a reliable signal that you have started the next phase before closing this
one. Stop, write down the phase's output (a Registry row, a confirmed ladder, a storyboard line),
close the two files you have, then open what the next phase needs. The exception that is genuinely
an exception: a failing gate that points you at a specific mechanic — open it, use it, close it,
and drop back to two.

---

## The per-phase load table

This is the centrepiece. One phase, one permitted file, one tenant section. Everything not named
in a row is **not permitted** during that phase.

| Phase | Permitted reference file | Tenant section | Explicitly not open |
|---|---|---|---|
| **0 · Prequalify** | [prequalification.md](prequalification.md) | `profile.md` — instance, schemas, conventions | Any journey skill, any build reference, `journeys.md` |
| **0.5 · Inherit** | [prequalification.md](prequalification.md) | `inventory.md` — dashboards, datasets, charts | `journeys.md`, `open-items.md`, dataset SQL |
| **1 · Reference dashlets** | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/reference-dashboards.md` | `inventory.md` | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/schema-discovery.md`, `superset-api.md` |
| **1.5 · Product artefacts** | [product-artefacts.md](product-artefacts.md) | `journeys.md` — the stage list only | Any build reference. Artefacts are read from Confluence/Figma, not from the plugin |
| **2 · Schema discovery** | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/schema-discovery.md` | `journeys.md` — the literal vocabularies | `superset-api.md`, `dashboard-design.md`, the Registry template |
| **3 · Definition Registry** | [memory-and-registry.md](memory-and-registry.md) | `journeys.md` + `inventory.md` — for dataset ids and metric names | Everything in `superset-build` except what a specific row forces you to check |
| **4 · Model** | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/warehouse-gotchas.md`, or `query-optimisation.md` if a query is slow | `inventory.md` — dataset ids and source tables | `dashboard-design.md`, `evals.md`, the journey skill's dashlet set |
| **5 · Storyboard** | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/dashboard-design.md` | `inventory.md` | `superset-api.md` — the storyboard is prose, not payloads |
| **6 · Build** | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/superset-api.md` | `profile.md` — conventions in force | `qc-protocol.md`. Building while reading the gates produces charts designed to pass rather than charts that are right |
| **7 · Nomenclature and layout** | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/dashboard-design.md` | `profile.md` — separators, prefixes, offsets | `superset-api.md`, unless a layout fix needs a `position_json` write |
| **8 · QC** | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/qc-protocol.md`, then `evals.md` — **sequentially, not both** | `open-items.md` — the live worklist | The journey skill. QC checks the build against the Registry, not against the journey's ideal |
| **9 · Ship the writing** | `SKILL.md` §Shipping, then [versioning-and-sharepoint.md](versioning-and-sharepoint.md) | `revisions.md` to write, `open-items.md` to close | Everything else. If you need a build reference to write the companion doc, the Registry is incomplete |

Two phases deserve a note. **Phase 2 is the one where people over-load**, because schema discovery
raises questions about everything downstream; resist it, the answers belong in Phase 3 rows. And
**Phase 8 is the one where people under-load**: the gates and the eval suites are two files and
they run in sequence, so open `qc-protocol.md`, finish the eleven gates (0 through 6, including 0b, 0c, 0d and 1b), close it, then open
`evals.md`. Holding both is the commonest breach of the two-file rule and it buys nothing, because
you cannot run them simultaneously anyway.

---

## Tenant file read discipline

The tenant directory is split into five files for exactly this reason. `journeys.md` alone can run
to tens of thousands of bytes on a mature engagement; `open-items.md` is a worklist a build never
needs. **The split exists so that a build reads `inventory.md` and never opens `open-items.md`.**

**The rule: read the section, not the file.** Locate the heading you need — the onboarding ladder,
the decline taxonomy, the dataset list — and read that. Do not read a tenant file front to back
"to get oriented"; orientation is `profile.md`, which is the small one, and that is what it is for.

| Tenant file | Holds | Read it in |
|---|---|---|
| `profile.md` | Instance, database ids, schemas, timestamp offset, title and prefix conventions | Phases 0, 6, 7 |
| `inventory.md` | Dashboards with ids and slugs, charts with viz types, datasets with source tables and metric lists | Phases 0.5, 1, 3, 4, 5 |
| `journeys.md` | The live ladder per journey, every literal vocabulary, bucket labels verbatim | Phases 1.5, 2, 3 |
| `open-items.md` | The numbered worklist, known live defects with owners | Phase 8, and audit entry mode |
| `revisions.md` | What changed, when, and by which version | Phase 9 — you write it more often than you read it |

Tenant files are shared across every skill in this plugin at
`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/`. A journey skill reading `journeys.md` and the build skill
reading `inventory.md` in the same session is fine; both reading both is not.

---

## Eviction and re-read

Close each phase by writing its output down, then dropping its inputs. Writing it down is what
makes dropping safe.

| After phase | Drop | Because |
|---|---|---|
| 0 / 0.5 | `prequalification.md`, the raw enumeration output | The answers are in the prequalification record; the enumeration is in `inventory.md` |
| 1 | `reference-dashboards.md`, the decoded dashlet params | The adopt/adapt/supersede calls are in the review note and the Registry's "Inherited from" column |
| 1.5 | `product-artefacts.md`, the PRD and design text | The artefact register is the output; the source documents are not |
| 2 | `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/schema-discovery.md`, the transition matrix, every profiling query result | The confirmed ladder and the literal vocabularies are the output. Write them to `journeys.md` before dropping |
| 3 | `inventory.md` | Dataset ids and metric names are now in the Registry rows |
| 4 | Dataset SQL for every dataset you are not still editing, `warehouse-gotchas.md` | This is the original rule. The dataset's definition is summarised in its Registry row |
| 5 | `dashboard-design.md` | The storyboard is the output |
| 6 | `superset-api.md`, request and response payloads | The object ids are in the capsule |
| 7 | `dashboard-design.md` again | |
| 8 | `qc-protocol.md` before opening `evals.md`; both before Phase 9 | The gate results table is the output |

**Four things must survive to the end of the session and are never dropped:**

- **The derived ladder**, exactly as the user confirmed it. Re-deriving is the failure this whole
  file exists to prevent.
- **The Registry rows in play** — the rows for the data points this session touches.
- **The storyboard**, once Phase 5 has produced it.
- **The open reconciliation pairs**, by data point and dataset. A pair you forget is a Gate 3
  failure that surfaces in someone else's meeting.

If one of those four is gone, do not reconstruct it from memory. Re-read it: the ladder from
`journeys.md`, the Registry rows from the companion doc, the pairs from `open-items.md`. A re-read
costs a minute. A reconstruction costs a definition.

---

## The capsule as handover

This is the payoff. Everything above is about not holding too much in one session; the capsule is
what makes that safe across sessions. **Write it so the next session can start at the right phase
without re-reading anything except the one file that phase needs.**

A capsule that does its job carries:

- **Model used and entry mode** — so the next session knows whether G1 needs to re-fire and which
  phase sequence applies.
- **Route** — journey skill and the phase the session stopped at, with completed / partial /
  skipped per phase.
- **The confirmed ladder**, verbatim, with the date the user confirmed it and who confirmed it. Not
  a pointer to where it might be.
- **Registry rows added or changed this session**, by data point.
- **Objects written by id and type** — datasets, charts, dashboards. This is the undo list.
- **Gates passed, failed and not run, with the reason for each not-run.**
- **Open reconciliation pairs** and open questions, each with an owner.
- **The single next action**, phrased as an instruction someone could follow cold.
- **Which files were read**, so the next session knows what has already been checked and what has
  not.

Format: [the context-capsule template](../templates/context-capsule.md). Storage and the field
list: [memory-and-registry.md](memory-and-registry.md). The extra trace fields
an observability reviewer needs are in [observability.md](observability.md) §Layer 2.

**The test of a capsule: could the next session do useful work having opened the capsule and
exactly one other file?** If not, the capsule is a log, not a handover.

---

## Anti-patterns

Each of these has happened, and each one evicts something load-bearing.

- **Pasting a whole playbook into the conversation.** A reference file is something you read and
  act on, not something you quote. Quoting it doubles its cost and it is still in context twice.
- **Loading all five journey skills "for context".** That is roughly 75 KB to answer a routing
  question the router's table already answers in one row. Route first, then load one.
- **Carrying eval fixtures into a build session.** The fixtures in
  `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/eval-harness.md` are test prompts for
  evaluating the agent. They are not instructions, they do not belong in a build, and reading them
  mid-build biases you toward what the fixture expects.
- **Re-reading a dataset's SQL you already summarised into the Registry.** If the Registry row
  cannot answer your question, the row is deficient — fix the row, do not re-read the SQL.
- **Holding a 50 KB tenant file open through nine phases.** Five of the nine phases do not need
  `journeys.md` at all, and by Phase 6 it is pure ballast sitting on top of the storyboard.
- **Opening `qc-protocol.md` during Phase 6.** You end up building charts shaped to pass gates
  rather than charts that are right, and the gates stop being an independent check.
- **Reading a tenant file front to back to "get oriented".** Orientation is `profile.md`. Read the
  section, not the file.
