---
name: signup-builder
description: Binds the onboarded-to-first-spend funnel to the shared build contract — onboarded-user grain, the two-step model with interim detail, and the exclusive activation-window partition. Refuses to promote an interim event to a step.
---

Follow `${CLAUDE_PLUGIN_ROOT}/skills/app-signup/SKILL.md` plus the `dashboard-builder` contract.
Everything below is what differs on *this* journey.

- **Grain: one row per onboarded user**, unbounded window, cohort-dated on onboarding completion so
  a sign-in three weeks later still counts in the month the user onboarded.
- **Identity key: `nullif(uid,'')`.** Pre-auth events carry an empty string, so a raw distinct count
  collapses every anonymous user into one and destroys the denominator. Wrap it everywhere, and
  carry the account-mapping coverage rate — anything below 100% caps every downstream step.
- **Terminal-outcome backstop: every onboarded user lands in exactly one bucket.** Signed in;
  attempted and dropped; never attempted; signed in *before* onboarding completed. Where activation
  windows are built, the exclusive D7/D15/D30/D60/60+/not-yet-activated/too-new partition must sum
  to total onboarded **exactly** — that replaces monotonicity as the correctness check.
- **Named triangulation pairs: this journey's funnel entry against `onboarding-funnel`'s
  `Completed` count** (the reciprocal of that builder's pair, and it must agree in both
  directions), and **the app-side spend flag against the ledger's transacting accounts.**
  Where the ledger is joined *into* this dataset rather than checked against it, this is the suite's
  largest reconciliation exposure, because the same ledger table feeds the transactions dashboard at
  a different grain.
- **The trap that most often breaks this build: inverting the step numbering.** The funnel is **two
  steps** — the onboarding-completion population, then the first authenticated app event. OTP
  issued, auth method set and the FE authorisation event are **interim detail beneath step 2**, not
  steps before it. Promote one and nothing reconciles against the step-2 metric.
- Define spend as **posted**, never authorised, or activation stops being a superset of spenders.
  And check the payload, not the name: account activation is not card activation.
