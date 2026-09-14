---
name: onboarding-builder
description: Binds the onboarding and application funnel to the shared build contract — application grain, decline-versus-abandonment split, and the handover count to app sign-up. Refuses to build on an unconfirmed ladder.
---

Follow `${CLAUDE_PLUGIN_ROOT}/skills/onboarding-funnel/SKILL.md` plus the `dashboard-builder`
contract. Everything below is what differs on *this* journey.

- **Grain: one row per application, on a rolling unbounded window.** Keying on the user collapses
  repeat applicants and makes the funnel non-monotonic. Cohort-date on the application's first
  event.
- **Identity key: the application id**, with the decisioning vendor's table joined on it taking the
  **latest row per application**. Expect the pre-application record's application id to be null on
  a material share — recover the link on a borrower/customer id, expose a `resolved_via_customer_id`
  metric, and trend it, because a link degrading month over month is a live incident.
- **Terminal-outcome backstop: the `stage_reached` × `overall_outcome` cross-tab**, plus "outcome
  of everyone who started" summing to 100%. Funnel step loss and the drop-off bucket measure
  different things and the gap between them *is* the decline volume. A last-stage table is not a
  substitute: it does not total both ways.
- **Named triangulation pair: this journey's `Completed` count against `app-signup`'s funnel
  entry.** One *is* the other — identical, not close. A difference is a Gate 3 finding.
- **The trap that most often breaks this build: the entry state is newer than your window.** A
  state like "application created" can start being emitted mid-period and silently truncate every
  earlier cohort. Check first-seen date per state and enter on the earliest continuously-emitted
  one before a single chart exists.
- Two parallel routes converting an order of magnitude apart are not one product: ship both
  sub-funnels and keep only steps every route passes through in the overall funnel.
