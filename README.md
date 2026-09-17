# Superset BI Agent

Builds and maintains Apache Superset dashboard suites for credit card programmes, deriving each
engagement's real stage ladder from live data rather than assuming the one that worked last time.

A card programme's funnel is not knowable in advance. The stage names in the PRD, the event names
in the warehouse and the states the data actually transitions through are three different things,
and a dashboard built on the first two reconciles perfectly against the wrong definition. This
package derives the ladder from a transition matrix on live data, holds every number behind
blocking QC gates, and refuses to publish past a gate that failed.

**Use it if** you run Superset over a warehouse for a card or lending programme and you need an
onboarding, activation, spend or repayments suite that survives someone asking where a number came
from.

**Not for you if** your BI tool is not Superset, your domain is not a transactional financial
product, or you want a chart generated quickly and are content to reconcile it later. The gates
are the point, and they cost time on the way in.

**Status:** maintained, v3.0.0. Used weekly on live programmes.

## Two things it will not do

Publish past a failing gate, and carry one engagement's stage ladder onto another. Both have tests
behind them in `evals/`.

They are the first thing in this README because they are the two failures that cost the most. A
suite that publishes past a failed gate produces a number someone will act on. A ladder carried
from the last engagement produces a dashboard that reconciles perfectly against the wrong
definition, which is worse, because nothing about it looks broken.

## What is in it

| Skill | Owns |
|---|---|
| `superset-bi-agent` | Routing and governance. The model gate, prequalification, twelve guardrails, the L1 to L4 metric hierarchy, the phase loop, observability and context budget. Builds nothing itself. |
| `superset-build` | Modelling, headless construction over the REST API with mandatory read-back, eleven sequential blocking QC gates, and the golden, regression and adversarial eval suites. Decides no metric meanings. |
| `onboarding-funnel` | Pre-application through KYC and decisioning, ending at onboarded. |
| `app-signup` | Onboarded through app sign-in and activation to first posted transaction. |
| `transactions-spends` | Spend, declines, RFM, and the authorisation chain from switch to ledger. |
| `repayments` | Mandates, collections, rails, and the failure and return buckets on each. |
| `concentration-analysis` | Turns an event count into an affected-population view: unique entities, attempts per entity, decile concentration, and the band-by-reason composition. |

The journey boundaries are mutually exclusive by design, so a request lands in exactly one place.
Anything whose headline is a count of declines, failures or retries routes to
`concentration-analysis` regardless of which journey it arrived through, because a count of events
is not a count of customers.

## Tenant state

Everything engagement-specific lives under `tenants/<name>/`, split five ways so a build reads the
part it needs: `profile.md`, `inventory.md`, `journeys.md`, `open-items.md`, `revisions.md`. The
skills carry no engagement state at all, and `scripts/validate_skill.py` fails the package if a
programme name appears anywhere under `skills/`.

`tenants/aurora/` is a worked example on invented data. It is there so the five files have a filled
shape to read rather than only a blank one, and it carries the lessons that transfer: the
pre-funnel loss nobody was watching, the single activation cliff, finding a join key by testing
overlap rather than reading column names, the subtraction chain behind a published count, and a
column whose name says outcome and whose values say something else. Start a new engagement from
`tenants/_template/profile.md`, never by copying another tenant.

## Install

No clone needed:

```bash
claude plugin marketplace add SayandipBagchi/superset-bi-agent
claude plugin install superset-bi-agent@superset-bi-agent
```

Or from a local copy:

```bash
git clone https://github.com/SayandipBagchi/superset-bi-agent.git
claude plugin marketplace add ./superset-bi-agent
claude plugin install superset-bi-agent@superset-bi-agent
```

Seven skills, ten agents and six commands register together.

## Try it

```
/superset-bi-agent:new-engagement
```

It runs prequalification before anything else: operating mode, environment, go-live date, product
artefacts, acquisition source. Expect it to ask which Superset connection points at production and
to want one number the business already quotes, because reproducing that number is the only thing
that settles whether you are on the right source.

Then, once a suite exists:

```
/superset-bi-agent:funnel where do applications drop off
/superset-bi-agent:qc
/superset-bi-agent:audit-suite
```

The router also fires on plain phrasing: *these two dashboards disagree*, *why is this chart blank*,
*how many unique customers are behind that decline count*.

## Package, validation and portability

Seven skills, ten agents, six commands and thirteen eval cases, laid out under `commands/`,
`agents/`, `skills/`, `tenants/` and `evals/`. No `.mcp.json`, no `hooks/`, no `settings.json`.

```bash
python3 scripts/validate_skill.py
claude plugin validate .
claude plugin eval .
```

The validator checks the manifest, frontmatter keys and description ceilings, that version and
author are declared once, that every required reference exists and every link resolves, that
cross-skill links use `${CLAUDE_PLUGIN_ROOT}`, that each tenant has the full five-file set, command
wiring, agent frontmatter, and that no engagement name appears in any skill file.

Everything is plain Markdown with no tool call, shell or network dependency in any skill body. Only
`SKILL.md` is strictly required at runtime; the rest degrades gracefully, and the model says what it
could not read rather than guessing. Flattening a single skill out of the package breaks the
cross-skill links. Details in `skills/superset-bi-agent/references/portability.md`.

## Licence

MIT. Author: Sayandip Bagchi.
# Superset BI Agent

Builds and maintains Apache Superset dashboard suites for credit card programmes, deriving each
engagement's real stage ladder from live data rather than assuming the one that worked last time.

A card programme's funnel is not knowable in advance. The stage names in the PRD, the event names
in the warehouse and the states the data actually transitions through are three different things,
and a dashboard built on the first two reconciles perfectly against the wrong definition. This
package derives the ladder from a transition matrix on live data, holds every number behind
blocking QC gates, and refuses to publish past a gate that failed.

**Use it if** you run Superset over a warehouse for a card or lending programme and you need an
onboarding, activation, spend or repayments suite that survives someone asking where a number came
from.

**Not for you if** your BI tool is not Superset, your domain is not a transactional financial
product, or you want a chart generated quickly and are content to reconcile it later. The gates
are the point, and they cost time on the way in.

**Status:** maintained, v3.0.0. Used weekly on live programmes.

## Install

No clone needed:

```bash
claude plugin marketplace add SayandipBagchi/superset-bi-agent
claude plugin install superset-bi-agent@superset-bi-agent
```

Or from a local copy:

```bash
git clone https://github.com/SayandipBagchi/superset-bi-agent.git
claude plugin marketplace add ./superset-bi-agent
claude plugin install superset-bi-agent@superset-bi-agent
```

Seven skills, ten agents and six commands register together.

## Try it

```
/superset-bi-agent:new-engagement
```

It runs prequalification before anything else: operating mode, environment, go-live date, product
artefacts, acquisition source. Expect it to ask which Superset connection points at production and
to want one number the business already quotes, because reproducing that number is the only thing
that settles whether you are on the right source.

Then, once a suite exists:

```
/superset-bi-agent:funnel where do applications drop off
/superset-bi-agent:qc
/superset-bi-agent:audit-suite
```

The router also fires on plain phrasing: *these two dashboards disagree*, *why is this chart blank*,
*how many unique customers are behind that decline count*.

## What is in it

| Skill | Owns |
|---|---|
| `superset-bi-agent` | Routing and governance. The model gate, prequalification, twelve guardrails, the L1 to L4 metric hierarchy, the phase loop, observability and context budget. Builds nothing itself. |
| `superset-build` | Modelling, headless construction over the REST API with mandatory read-back, eleven sequential blocking QC gates, and the golden, regression and adversarial eval suites. Decides no metric meanings. |
| `onboarding-funnel` | Pre-application through KYC and decisioning, ending at onboarded. |
| `app-signup` | Onboarded through app sign-in and activation to first posted transaction. |
| `transactions-spends` | Spend, declines, RFM, and the authorisation chain from switch to ledger. |
| `repayments` | Mandates, collections, rails, and the failure and return buckets on each. |
| `concentration-analysis` | Turns an event count into an affected-population view: unique entities, attempts per entity, decile concentration, and the band-by-reason composition. |

The journey boundaries are mutually exclusive by design, so a request lands in exactly one place.
Anything whose headline is a count of declines, failures or retries routes to
`concentration-analysis` regardless of which journey it arrived through, because a count of events
is not a count of customers.

## Two things it will not do

Publish past a failing gate, and carry one engagement's stage ladder onto another. Both have tests
behind them in `evals/`.

## Tenant state

Everything engagement-specific lives under `tenants/<name>/`, split five ways so a build reads the
part it needs: `profile.md`, `inventory.md`, `journeys.md`, `open-items.md`, `revisions.md`. The
skills carry no engagement state at all, and `scripts/validate_skill.py` fails the package if a
programme name appears anywhere under `skills/`.

`tenants/aurora/` is a worked example on invented data. It is there so the five files have a filled
shape to read rather than only a blank one, and it carries the lessons that transfer: the
pre-funnel loss nobody was watching, the single activation cliff, finding a join key by testing
overlap rather than reading column names, the subtraction chain behind a published count, and a
column whose name says outcome and whose values say something else. Start a new engagement from
`tenants/_template/profile.md`, never by copying another tenant.

## Layout

```tree
superset-bi-agent/
├── .claude-plugin/              # plugin.json and marketplace.json
├── commands/                    # 6 slash commands
├── agents/                      # 10 subagents, including builders/ and review/
├── skills/                      # 7 skills, each with its own references/
├── tenants/                     # engagement state, one directory per engagement
├── evals/                       # 13 cases with graders, plus fixtures
├── hosts/openai.yaml            # optional UI metadata, no behaviour
└── scripts/validate_skill.py    # structural validation, stdlib only
```

No `.mcp.json`, no `hooks/`, no `settings.json`.

## Checking the package

```bash
python3 scripts/validate_skill.py
claude plugin validate .
claude plugin eval .
```

The validator checks the manifest, frontmatter keys and description ceilings, that version and
author are declared once, that every required reference exists and every link resolves, that
cross-skill links use `${CLAUDE_PLUGIN_ROOT}`, that each tenant has the full five-file set, command
wiring, agent frontmatter, and that no engagement name appears in any skill file.

## Portability

Plain Markdown, relative references within a skill and `${CLAUDE_PLUGIN_ROOT}` across skills, with
no tool call, shell or network dependency in any skill body. Only `SKILL.md` is strictly required at
runtime; everything else degrades gracefully, and the model says what it could not read rather than
guessing. Flattening a single skill out of the package breaks the cross-skill links. Details in
`skills/superset-bi-agent/references/portability.md`.

## Licence

MIT. Author: Sayandip Bagchi.
