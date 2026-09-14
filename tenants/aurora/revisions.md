# Tenant: `aurora` — revisions

Author: Sayandip Bagchi.

*Illustrative example on invented data. What changed, when and why — newest first. Read when a
number has moved and nobody knows why.*

**rev 5 — 2026-06-12.** Repayments built (d15, nine charts, dataset 43). Concentration view added:
the subtraction chain 1,204 → 1,162, 212 unique accounts affected, and the band-by-reason split
separating the `insufficient_funds` body from the `card_not_activated` tail (Lesson 4). AU-07
closed — default `count` metric removed from dataset 44. AU-08 raised: month boundaries differ
between the epoch datasets and the rest, which is AU-01 surfacing on a second dashboard.

**rev 4 — 2026-05-29.** Transactions built (d14, datasets 45 and 47). Account bridge corrected:
`payer_ledger_id` rejected on zero overlap and 31% empty string, `account_ref` ↔ `ledger_account_id`
adopted at 1,388 of 1,391 (Lesson 3). **Every figure joined on the old key before this date is
void, not merely stale.** The `approval_status` trap found and documented (Lesson 5): application
declines moved from 22 to **386** when read from the correct column — a seventeen-fold move in a
published number, caused by a column whose name describes a different decision.

**rev 3 — 2026-05-08.** App sign-up built (d13, dataset 42). Activation cliff identified: of 224
customers lost between onboarding and first spend, 179 are lost at card activation alone (Lesson 2).
Activation-window cohorts added in the same pass (D7 184 · D15 231 · D30 266 · D60 291), because
the cliff is only actionable once the window is known.

**rev 2 — 2026-04-24.** Onboarding built (d12, datasets 41 and 44). Lesson 1 recorded: the
pre-application stage loses 13,860 pre-qualified people against bank connection's 100, and the funnel
was redrawn to start at soft eligibility rather than at application creation. AU-01 raised on the
epoch offset; AU-05 on the 27% landing-coverage gap.

**rev 1 — 2026-04-10.** Phase 0 profile established. Environment confirmed as **production** by the
programme lead and verified by reproducing the published "applications started" figure of 1,240 —
not inferred from the hostname (G10). Go-live recorded in writing as 2026-03-02, with an
account-level internal flag, so the boundary is not a date cut (G8).
