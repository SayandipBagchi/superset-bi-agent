---
description: Run QC the eleven gates (0 through 6, including 0b, 0c, 0d and 1b) on a dashboard suite and report pass, fail or not-run per gate
argument-hint: "[the dashboard or suite to check] [optional: the gates to focus on]"
---

Use the `superset-build` skill in QC mode.

Run the gates in order — 0, 0b, 0c, 0d, 1, 1b, 2, 3, 4, 5, 6 — and return a table of gate, verdict
and the evidence you actually gathered, failures first. Query the reconciliation pairs rather than
eyeballing them. For each failure, name the dashlet to fix or descope and the owner. Default to the
whole suite when no subset is named.

Every gate gets a recorded verdict. A gate you could not run in the current operating mode is
**NOT RUN with the reason**, never a pass — and say which half of Gate 5 you checked, because 5a
is API-checkable in any mode and 5b needs a browser. Treat a systematic timestamp-offset difference
as a definition difference, not a freshness tolerance to wave through.

Do not publish past a failing gate, do not reconcile two disagreeing numbers by choosing one, and
do not soften a fail into a caveat on your own authority.

Suite:

$ARGUMENTS
