---
description: Turn an event count into an affected-population view — unique entities, attempts per entity, and the concentration tail
argument-hint: "[the event count and where it comes from] [optional: the entity — user, account, card, mandate]"
---

Use the `concentration-analysis` skill.

Establish the entity before building anything: ask whether they mean users, accounts, cards,
applications or mandates, test whether that entity is 1:1 with the word they used, and validate the
entity bridge **on the failing rows specifically** — a bridge verified on successful events is not
verified. Then return the set: unique entities affected, attempts per affected entity in fixed
bands, the decile Pareto whose cumulative share ends at exactly 100.0%, and the band-by-reason
composition that shows whether the tail is a different phenomenon from the body.

Lead with the entity count and the median, not the mean, and say plainly how far the event count
overstates customer impact. Exclude internal and test entities and state that you did — they fail
more often than customers and they concentrate in exactly the tail you are pointing at. Record
"unique entities affected" as its own Definition Registry row, not a variant of the event count.

Do not report an event count as a population, do not substitute the grain your data happens to
have for the word the stakeholder used, and do not rank over the whole population and then let a
chart filter to a segment.

Event count:

$ARGUMENTS
