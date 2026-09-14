# Changelog — superset-bi-agent

## v3.0.0 — 2026-09-14

**Type:** Major · **Model used:** Opus 5 · **Entry mode:** Restructure

One 76KB skill became seven. Every invocation used to load the whole thing before deciding
anything, the QC gates were stated twice and had already drifted, and roughly 29KB of one
engagement's live state was welded into playbooks the package advertised as portable. This release
fixes the shape rather than the content: the substance moved, it was not rewritten.

Validated against a live instance before release: the whole suite enumerated, every dashlet mapped
to the skill that would now regenerate it, and several live defects found by the gates and
guardrails this package defines. Defects of that kind are recorded in the engagement's tenant file.

### Breaking
- **One skill became seven.** `superset-bi-agent` is now the router and governor only. Modelling,
  building, QC and evals moved to `superset-build`. The five journey playbooks became the skills
  `onboarding-funnel`, `app-signup`, `transactions-spends`, `repayments` and
  `concentration-analysis`. Anything that referenced `references/playbooks/*.md` must be repointed.
- **Tenant state left the skills.** The old single-engagement reference file is gone. Live state now
  lives in `tenants/<name>/` split five ways: `profile.md`, `inventory.md`, `journeys.md`,
  `open-items.md`, `revisions.md`. Skills are tenant-clean and the validator enforces it.
- **Cross-skill references must use `${CLAUDE_PLUGIN_ROOT}`.** Relative paths now only resolve
  within a single skill.
- **`version:` and `updated:` are gone from SKILL.md frontmatter.** Version is declared once, in
  `plugin.json`.

### Added
- **`agents/` — ten subagents.** `schema-profiler`, `dashboard-builder`, `qc-triangulator` and
  `eval-runner`; four journey builders under `builders/`, each carrying its journey's grain,
  identity key, terminal-outcome backstop and signature trap; and two reviewers under `review/`,
  `number-integrity` (G6 and G11) and `definition-drift` (the name and prescription checks).
- **`commands/` — six slash commands:** `new-engagement`, `funnel`, `build-dashboard`, `qc`,
  `concentration`, `audit-suite`.
- **`references/observability.md`.** Previously absent entirely. Freshness SLAs per source table,
  a standing health dashlet set, agent build traces extending the session capsule, a failure
  taxonomy, and drift detection in three kinds: schema drift, metric drift (with the frozen-anchor
  correctness alarm held separate from rolling open-period drift) and doc-vs-live drift.
- **`references/context-engineering.md`.** Previously absent. The loading budget, a per-phase load
  table, tenant-file read discipline, eviction and re-read rules, and the capsule as handover.
  Promotes the working-memory rule from a single line to the governing principle, on the grounds
  that context discipline is a correctness concern: an evicted stage ladder gets silently
  re-derived differently later in the same session.
- **`references/fine-tuning.md`.** Previously absent. States the boundary first (prompt-and-skill
  tuning, not model weights), then the ratchet, the escalation ladder from caveat to test to
  guardrail to version bump, the skill-release loop with its packaging ceilings, and the
  knowledge-capture decision rule whose absence is why tenant state leaked into the playbooks.
- **`references/portability.md`**, **`references/guardrails.md`**, **`references/prequalification.md`**,
  **`references/memory-and-registry.md`** and **`superset-build/references/modelling.md`**, carrying
  the bodies extracted from the old SKILL.md.
- **`templates/`** — definition registry, tenant profile, context capsule, companion doc — and
  **`examples/storyboard.md`**.
- **`evals/` — thirteen runnable cases with graders and two fixtures**, covering journey routing, the
  concentration reframe, gate blocking, entity-not-event, the single-system funnel key, the model
  gate, tenant purity, prompt injection via a pasted SQL comment, drift detection, context budget,
  and one negative case. This closes the v2.11.0 open item: the harness had no fixture for the
  repeat-entity pattern.
- **`scripts/validate_skill.py`**, **`hosts/openai.yaml`**, **`LICENSE`** and **`.gitignore`**.
- **`tenants/README.md`** and **`tenants/_template/profile.md`** for onboarding a new engagement
  without copying another tenant's file.

### Changed
- **The router SKILL.md is 20KB, down from 76KB**, and 323 lines against a 500-line ceiling. What
  remains is routing and governance: the model gate, the journey and entry-mode tables, the L1 to
  L4 hierarchy, the twelve guardrails as one line each, the phase loop, the five memory stores and
  the reference routing table.
- **The QC gates are stated once.** `superset-build/SKILL.md` carries one line per gate; the
  checklists live only in `references/qc-protocol.md`. The old duplication had already produced two
  conflicting versions of Gate 1b.
- **Duplication removed** between the old SKILL.md and `operating-modes.md`, `superset-api.md`,
  `reference-dashboards.md`, `product-artefacts.md`, `schema-discovery.md` and `dashboard-design.md`.
- **The sibling-dashboard contradiction is resolved.** `reference-dashboards.md` still described
  two undecoded sibling dashboards after v2.12.0 recorded one of them as decoded.
- **The tenant file's stale as-of stamp is corrected.** It read 2026-09-03 rev 3 while four later
  revisions dated 2026-09-10 sat beneath it.
- **The validator does not port the inherited dash ban.** This package uses the middle dot and the
  hyphen as house style; enforcing the ban would mean rewriting every file for no behavioural gain.
  Three checks replace it: tenant purity, the packaging ceilings, and agent frontmatter.

### Known gaps
- The changelog has no entries between v2.0 and v2.10. Those releases predate this file and have
  not been reconstructed.
- Some advisory write-ups cited by a tenant record are external artefacts and are not in this
  package. Citations now say so.

## v2.12.0 — 2026-09-10

**Type:** Minor · **Model used:** Opus 5 (Sonnet 5 for the first, superseded pass) ·
**Entry mode:** Extend + triangulate

Driven by a live engagement: an onboarding funnel counted "application started" from the
origination vendor's status event alone, missing applicants the event stream had seen land who
never entered the vendor's funnel. Fixing it surfaced a larger, unrelated defect and a second
projection of the event stream that nobody had recorded. Everything below is the
tenant-independent residue of that build; the engagement specifics stay in its tenant files.

### Added
- **Guardrail G12 — "A funnel keyed on one system's records cannot see the people that system never
  met."** Triangulating a vendor/origination system against an event stream, and the three
  populations a defensible top-of-funnel must name: in-both, vendor-only, and the **orphans** the
  vendor never recorded. Includes the **terminal-outcome backstop** (an entity with a terminal
  outcome has by definition started — query `<terminal flags> AND <entry flag> = 0`), the
  both-directions coverage rule, grain discipline, the decomposition requirement, and the
  re-check-what-the-union-broke step.
- **G12's two source traps**: one event stream exposed as several projections in different schemas
  (prove sameness by row count + min/max timestamp, never by name), and inspecting nested payloads
  with a serialize call rather than a varchar cast.
- **The "two projections of one event stream" section** in the tenant profile template: what each
  projection carries, which keys each exposes, and eight rules including the quotation-id trap and
  landing-event key coverage.
- Four anti-patterns covering vendor-vs-stream choice, unfiltered terminal outcomes, null payload
  casts, and untested identifier bridges.
- Nine new tenant open items on the driving engagement.

### Changed
- Three tenant revisions on the driving engagement: the onboarding funnel's entry redefined as a
  three-signal union, the pre-application dataset propagated to match, the three competing
  "started" numbers bridged and every one labelled with the definition it reads; a previously
  undecoded sibling dashboard decoded, with six cross-dashboard disparities named; the engagement
  owner's benchmark ruling recorded verbatim.
- The tenant profile's schema-family table now lists both projections of the event stream.

### Fixed
- **Retracted:** the claim that a given identifier bridged the event stream and the origination
  vendor. Tested — **zero overlap** against three candidate columns, and 34% empty string. The
  working bridge was a different pair entirely, found by testing every id-shaped column rather than
  by reading names. The technique is now in `superset-build/references/modelling.md`; the
  engagement's specific column names stay in its tenant files.
- Superset's default `count` metric removed from two datasets on the onboarding dashboard.
- A previously undecoded sibling dashboard decoded; one other still outstanding.
- Corrected previously-recorded state: the onboarding dashboard runs on **three** datasets and 19
  charts, not two and 17, and one reconciliation dataset had never been recorded at all.

### Open
- **A join-key correction collides with a published benchmark.** Re-keying the landing join is the
  correct fix and recovers dropped rows, but it moves a number the engagement has already quoted.
  Settle before the number is quoted again.
- Five further tenant items: a landing-coverage gap owned by product and engineering, date-filter
  targets, a composition dashlet, an intent-signal event never evaluated, and cross-dashboard month
  boundaries.

## v2.11.0 — 2026-09-10

**Type:** Minor · **Model used:** Opus 5 · **Entry mode:** Extend + audit

Driven by a live engagement: *"we show declined transactions, but one user can attempt many, so
the view is skewed — we need unique users who faced declines, attempts per user, and top X% of
users causing Y% of declines."* Everything below is the tenant-independent residue of that build.
The engagement-specific reconciliation is deliberately **not** carried into the skill.

### Added
- **`references/playbooks/repeat-entity-concentration.md`** — new playbook. Turning any event
  count into an affected-population view: entity selection and bridge validation, the five-dashlet
  set (headline / fixed bands / decile Pareto / composition / month-wise), two-dataset modelling,
  the precomputed-rank trap, population hygiene and the named-chain rule, verification checklist.
- **Guardrail G11 — "Count entities, not just events."** An event count is not a population;
  every such metric needs a unique-entity figure beside it or a stated reason why not.
- **Gate 1b — Entity grain and structure** (blocking): entity denominators, bridge validated on
  failing rows, window-function partitioning, `main_dttm_col` null on date-exempt datasets,
  `query_context` on API-created charts, sort metrics, join-direction and fan-out checks, backups.
- **Adversarial tests A-42 … A-50** (`references/evals.md` §3.6) — entity-grain and structural
  attacks, each derived from a defect found in the field.
- **Regression tests R-34 … R-39** — the structural invariants behind Gate 1b.
- Three quality metrics: entity-denominator coverage, precomputed-rank integrity, backup coverage.

### Changed
- **`references/warehouse-gotchas.md`** — three new sections: *Join direction and the driving
  table* (including the LEFT-JOIN-that-is-really-INNER predicate trap and duplicate-key fan-out
  on counts *and* money), *Decoded labels versus raw codes*, *Duplicate rows in an "immutable"
  event table*.
- **`references/superset-api.md`** — *Four things the API does silently* (`main_dttm_col`
  auto-assignment, `order_by_cols` ignored in aggregate mode, missing `query_context` on
  API-created charts, metric PUTs needing existing ids), plus *Changing a dataset you do not own —
  back it up first* and *Reading a dataset's SQL when the transport refuses it*.
- **SKILL.md** — Phase 4 gains the window-function partitioning rule and the date-exemption
  requirement; Phase 5 gains the repeat-entity block in the storyboard arc; five new anti-patterns.
- **Skill description** widened so the agent triggers on "unique users affected", "attempts per
  user" and "top X% cause Y%" phrasing, which previously did not reliably match.

### Packaging limits (hit during this release — recorded so they are not rediscovered)
- **`SKILL.md` frontmatter `description` must be <= 1024 characters.** The widened description was
  1,240 and blocked installation. Now 997.
- **`plugin.json` `description` must be <= 500 characters.** It was 546 and blocked installation
  after the first fix. Now 450.
- Check both before packaging; the two limits are different and the errors surface one at a time.

### Fixed
- Nothing in the docs was wrong; this release adds coverage rather than corrections.

### Open
- The eval harness (`references/eval-harness.md`) does not yet include a fixture for the
  repeat-entity pattern. Add one before the next major.
