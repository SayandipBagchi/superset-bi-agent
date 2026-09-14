---
description: Audit an existing dashboard suite that is suspected wrong and return findings with owners
argument-hint: "[the suite or dashboard to audit] [optional: what looks wrong, and to whom]"
---

Use the `superset-bi-agent` skill for Phase 0.5, then the `superset-build` skill for the gates.

Inherit before you judge: enumerate every dashboard, dataset, chart and metric that is actually
live, alongside the tenant file's recorded ladder and vocabulary. Then run the eleven gates (0 through 6, including 0b, 0c, 0d and 1b) and the
regression suite. Return three things in this order — the inventory as found, the gate table with a
verdict per gate, and a findings list in which **every finding becomes a doc fix, a build ask or a
shipped caveat, and never nothing**, each with a named owner.

Check doc-versus-live drift explicitly: every metric, column and bucket the docs name must exist
live under that exact spelling, and every dashlet the docs call essential must exist or be an open
build ask. Report orphan datasets and charts, duplicate concepts shipped under different titles,
and any overlapping dashboard on the instance that has never been decoded — that last one is an
open Gate 4, not a nil return.

Do not fix what you find, do not edit the docs to match live so the drift disappears, and do not
report a gate you could not run in this operating mode as passed.

Suite to audit:

$ARGUMENTS
