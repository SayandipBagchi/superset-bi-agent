# Superset BI Agent

Author: Sayandip Bagchi. Version lives in `.claude-plugin/plugin.json`.

Builds, QCs and maintains Superset dashboard suites for credit card programmes, deriving each
engagement's real stage ladder from live data instead of assuming it.

**`superset-bi-agent`** The router and the governor. Establishes the model gate, prequalifies the
engagement, holds the twelve guardrails, the L1 to L4 metric hierarchy and the phase loop, and
decides which journey a request belongs to. It also owns the cross-cutting disciplines:
observability, context engineering and the improvement ratchet. It never builds anything itself.

**`superset-build`** Modelling, headless construction and verification. One semantic dataset per
journey by source layer by grain, chart and dashboard creation over the REST API with mandatory
read-back, the eleven sequential blocking QC gates, and the golden, regression and adversarial
eval suites. It builds and checks what the Definition Registry already defines; it never decides
what a metric means.

**`onboarding-funnel`**, **`app-signup`**, **`transactions-spends`**, **`repayments`** One per
journey. Each carries that journey's questions to ask, modelling rules, traps, dashlet set and
triangulation pairs. The boundaries are deliberate and mutually exclusive: onboarding ends at
onboarded, app sign-up runs from onboarded to first spend, transactions owns spend and declines,
repayments owns mandates and collections.

**`concentration-analysis`** Turns an event count into an affected-population view: unique entities
affected, attempts per entity in fixed bands, decile concentration with cumulative share, and the
band-by-reason composition. Any request whose headline is a count of declines, failures or retries
routes here regardless of which journey it arrived through.

## Layout

```tree
superset-bi-agent/
├── .claude-plugin/plugin.json   # name, version and author, declared once
├── commands/                    # 6 slash commands
├── agents/                      # 10 subagents, including builders/ and review/
├── skills/                      # 7 skills, each with its own references/
├── tenants/                     # shared live state, one directory per engagement
├── evals/                       # 13 cases with graders, plus fixtures
├── hosts/openai.yaml            # optional UI metadata, no behaviour
└── scripts/validate_skill.py    # structural validation, no dependencies
```

No `.mcp.json`, no `hooks/`, no `settings.json`. Skills are tenant-clean by construction: every
engagement-specific fact lives under `tenants/`, and the validator fails the package if a
programme name appears anywhere under `skills/`.

## Install

Clone the repository and install the clone as a local plugin:

```bash
git clone <repo-url> superset-bi-agent
claude plugin install ./superset-bi-agent
```

Run `python3 scripts/validate_skill.py` from inside the clone first if you want the structural
check before anything registers. The seven skills, ten agents and six commands register together.

## Use

The router fires on anything that scopes, routes or governs a dashboard build: *start a suite for
the new programme*, *which journey does this belong to*, *these two dashboards disagree*, *audit
this suite*. It runs the model gate first, on every fresh invocation, and refuses to build,
model or QC on an unsupported model.

Journey skills fire on their own vocabulary and hand off to each other at their stated boundaries.
`superset-build` fires on modelling, building, QC and evals. The commands are shortcuts into the
same paths: `/superset-bi-agent:new-engagement`, `:funnel`, `:build-dashboard`, `:qc`,
`:concentration`, `:audit-suite`.

Two things the package will not do, by design: publish past a failing gate, and carry one tenant's
stage ladder onto another. Both are guardrails with tests behind them.

## Tenants

`tenants/<name>/` holds five files so a build reads the part it needs rather than the whole
record: `profile.md`, `inventory.md`, `journeys.md`, `open-items.md`, `revisions.md`. Start a new
engagement from `tenants/_template/profile.md`, never by copying another tenant. See
`tenants/README.md`.

## Checking the package

```bash
python3 scripts/validate_skill.py
```

It checks the manifest, every skill's frontmatter keys and description ceiling, that the version
and author are declared exactly once, that each SKILL.md carries its behaviour markers and none of
its siblings' content, that every required reference exists and every link resolves, that
cross-skill links use `${CLAUDE_PLUGIN_ROOT}`, that each tenant has the full five-file set, that
every agent's frontmatter name matches its file stem, that every command passes `$ARGUMENTS`, that
the eval cases carry graders, and above all that **no engagement name appears in any skill file**.

## Portability

Plain Markdown, relative references within a skill and `${CLAUDE_PLUGIN_ROOT}` across skills, no
tool call, shell or network dependency in any skill body. Only `SKILL.md` is strictly required at
runtime; everything else degrades gracefully, and the model says what it could not read rather
than guessing. A host that flattens a single skill out of the package will break the cross-skill
links. Details in `skills/superset-bi-agent/references/portability.md`.
