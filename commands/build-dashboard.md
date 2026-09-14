---
description: Model and build a dashlet or dashboard headlessly over the REST API, then read it back and verify
argument-hint: "[the dashlet or dashboard to build] [optional: the dashboard id or slug]"
---

Use the `superset-build` skill, Phases 4 to 7.

Model before you build: one semantic dataset per journey × source layer × grain, every count and
conversion defined as a dataset metric rather than a chart-level aggregate, and one native-filter
target per dataset. Storyboard the dashlets as a narrative first — the titles read top to bottom
should tell the story without the numbers. Then build over the REST API and **verify by read-back
after every write and again after a reload**: API-created charts are not attached by default and
render blank until the M2M association step. Return the object ids created, the read-back result
per object, and the gates still outstanding.

Take a `zz_backup_` copy of the original SQL of any dataset you did not author before editing it.
Build only metrics that have a Definition Registry row; where a definition is missing or contested,
stop and say so rather than settling it inside a dataset.

Do not publish past a failing gate, do not leave Superset's default `count` on a dataset, and do
not report a chart as built on the strength of the create call alone.

Build ask:

$ARGUMENTS
