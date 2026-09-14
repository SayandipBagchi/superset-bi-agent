---
description: Get or fix a funnel view by routing it to the journey skill that owns it
argument-hint: "[the funnel question, or the chart that looks wrong] [optional: the tenant]"
---

Use the `superset-bi-agent` skill to route, then the journey skill it names.

Identify two things before doing anything else, and state both back. First the **journey** —
`onboarding-funnel`, `app-signup`, `transactions-spends`, `repayments`, or
`concentration-analysis` where the headline is an event count that will be read as a population.
Pre-eligibility is the pre-funnel of onboarding, not a fifth journey. Then the **entry mode** —
greenfield, extend, audit or port — because it decides which phases run.

Then answer from that journey skill: the grain, the ladder as it is actually recorded for this
tenant, where the loss sits, and the triangulation pair that proves the number. Read the live
ladder out of the tenant's `journeys.md` rather than re-deriving it, and if you do re-derive,
diff against the recorded one and report the diff.

Do not build a funnel on a ladder you assumed or carried over, do not promote an interim event to
a funnel step, and do not answer a question spanning two journeys from one journey's skill alone.

Funnel:

$ARGUMENTS
