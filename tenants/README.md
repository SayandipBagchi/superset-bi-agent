# Tenant files

Author: Sayandip Bagchi.

Everything in this directory is **live state for one engagement**. Nothing in here is portable, and
nothing in here belongs in a skill file. The skills are tenant-clean by design and a validator
enforces it: a programme name appearing anywhere under `skills/` fails the build.

Each tenant gets a directory named for the programme in lower case, holding five files. The split
is not cosmetic. It exists so a build can read the one part it needs instead of loading fifty
kilobytes of state it will never use. Read the section, not the file.

| File | Holds | Read it when |
|---|---|---|
| `profile.md` | Instance, schema families and join keys, conventions in force, the go-live boundary and internal-user rule, third parties in the journey | Phase 0, and before writing any SQL |
| `inventory.md` | Dashboards with ids and slugs, chart inventory per dashboard, datasets with their full metric lists | Phase 0.5 when inheriting, and Phase 6 when building |
| `journeys.md` | The derived stage ladder, every bucket and state vocabulary verbatim, and the dated worked examples, one section per journey | Phase 2, for the journey you are actually working on |
| `open-items.md` | The Gate 3 reconciliation worklist and the numbered open-item tracker with owners | Phase 8, and when a gate fails |
| `revisions.md` | What changed, when, and why, newest first | When a number moved and nobody knows why |

## Starting a new tenant

1. Copy `_template/profile.md` to `<name>/profile.md` and fill it in from Phase 0. Do not copy
   another tenant's file and edit it; that is how a ladder gets carried across, and it is the
   failure that Directive 1 and G10 exist to prevent.
2. Create the other four as stubs with their headings and nothing under them. An empty section is
   honest; an inherited section is a lie that reconciles.
3. Record measure values only with an as-of date, and treat any figure older than the dashboard's
   last-changed timestamp as unverified.

## The rule that keeps this working

Before writing a fact into a skill file, ask: **would this sentence still be true on a different
engagement?** If not, it is tenant state and it belongs here. The decision procedure in full is in
`${CLAUDE_PLUGIN_ROOT}/skills/superset-bi-agent/references/fine-tuning.md`.
