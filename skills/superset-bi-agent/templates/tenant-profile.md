# The tenant profile

Author: Sayandip Bagchi.

A tenant directory is the live state of one engagement: what is actually deployed, what the
warehouse actually calls things, and which boundaries were confirmed rather than assumed. Nothing
in it is portable and nothing in it belongs in a skill file. This page tells you where the real
template lives and how to start a directory; it deliberately does not restate the template, because
two copies of a form drift and then nobody knows which one is current.

**The real template is `${CLAUDE_PLUGIN_ROOT}/tenants/_template/profile.md`. Copy that.**

---

## What a tenant directory is

One directory per engagement, named for the programme in lower case, at
`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/`. It is shared by every skill in this plugin — the router,
the build skill and the five journey skills all read the same files, which is what stops two skills
holding two versions of the same ladder.

The directory holds five files. The split is not cosmetic: it exists so that a build reads the one
part it needs instead of loading tens of kilobytes of state it will never open.

| File | What it holds | Read it in |
|---|---|---|
| `profile.md` | Instance and host, tenant and database ids, the confirmed environment, schema families and join keys, conventions in force (timestamp offset, title separator, metric prefixes), the go-live boundary and internal-user rule, third parties in the journey, the feature availability matrix, known live defects | Phases 0, 6, 7 — and before writing any SQL |
| `inventory.md` | Dashboards with ids **and slugs**, charts with viz types, datasets with their source tables and full metric lists | Phases 0.5, 1, 3, 4, 5 |
| `journeys.md` | The derived stage ladder per journey, every literal vocabulary verbatim — states, buckets, decline categories, FE event names — and dated worked examples | Phases 1.5, 2, 3 |
| `open-items.md` | The Gate 3 reconciliation worklist and the numbered open items, each with an owner | Phase 8, and audit entry mode |
| `revisions.md` | What changed, when, and under which version, newest first | When a number moved and nobody knows why |

## Starting a new one

1. **Copy `${CLAUDE_PLUGIN_ROOT}/tenants/_template/profile.md`** to
   `${CLAUDE_PLUGIN_ROOT}/tenants/<name>/profile.md` and fill it in from Phase 0.
2. **Never copy another tenant's file and edit it.** That is how a stage ladder, a decline taxonomy
   or a PSP gets carried across an engagement that does not have it. The copied line reconciles
   perfectly and is wrong, which is the worst combination available. Directive 1 and G10 exist
   because this has already happened.
3. Create the other four files as stubs — headings, nothing under them. An empty section is honest;
   an inherited section is a lie that passes every gate.
4. Fill the environment row from a **reproduced number**, not from a hostname. Until that row is
   filled that way, nothing below it in the profile is trustworthy (G10).
5. Record measure values only with an as-of date, and treat any figure older than the dashboard's
   last-changed timestamp as unverified.

## The decision test

Before writing a fact into a skill file, ask:

> **Would this sentence still be true on a different engagement?**

If yes, it is a skill fact and it belongs in a skill or reference file. If no, it is tenant state
and it belongs in the tenant directory. A programme name, a dataset id, a state literal, a
vendor, a go-live date and a known defect all fail the test. The rule that an event count needs an
entity denominator passes it.

The full decision procedure, including where a finding goes when it is halfway between the two, is
in [fine-tuning.md](../references/fine-tuning.md). The read discipline — which file you are allowed
to open in which phase — is in [context-engineering.md](../references/context-engineering.md).

**How to use this file.** Treat it as a pointer, not a form. Fill in
`${CLAUDE_PLUGIN_ROOT}/tenants/_template/profile.md`, and if this page and that template ever
disagree about what a profile contains, the template in `tenants/` wins — it is the artefact that
ships, and this is a signpost to it. See also
[`${CLAUDE_PLUGIN_ROOT}/tenants/README.md`](${CLAUDE_PLUGIN_ROOT}/tenants/README.md), which is the
authority on the directory as a whole.
