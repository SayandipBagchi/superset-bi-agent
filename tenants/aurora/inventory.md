# Tenant: `aurora` — inventory

Author: Sayandip Bagchi.

*Illustrative example on invented data. What is deployed, under which ids and slugs. Read at
Phase 0.5 when inheriting and at Phase 6 when building.* **As of 2026-06-12 (rev 5).**

## Dashboards

| id | Title | Slug | Charts | Datasets |
|---|---|---|---|---|
| 12 | Aurora · Onboarding Journey | `aurora-onboarding-journey` | 16 | 41, 44 |
| 13 | Aurora · Onboarding to App Sign-up | `aurora-onboarding-to-app` | 6 | 42 |
| 14 | Aurora · Transactions & Spends | `aurora-transactions-spends` | 14 | 45, 47 |
| 15 | Aurora · Repayments | `aurora-repayments-mandates-payments` | 9 | 43 |

Forty-five charts across four dashboards.

> **The slug is the stable handle; the id is not.** Numeric ids are assigned per instance at
> creation, so the same dashboard carries a different id in UAT and in production and a link built
> from one resolves to the wrong object — or to nothing — the moment it crosses an environment.
> Address dashboards by slug in documentation and handovers; use the id only inside a single
> instance, in a single session, after reading the object back.

## Datasets

| id | Name | Backs |
|---|---|---|
| 41 | `aurora_onboarding_journey` | d12 — the application ladder |
| 42 | `aurora_onboarding_to_app` | d13 — onboarded through to first transaction |
| 43 | `aurora_repayment_objects` | d15 — mandates and payments |
| 44 | `aurora_soft_eligibility` | d12 — the pre-application stage |
| 45 | `aurora_spend_account_daily` | d14 — account × day spend |
| 46 | `aurora_spend_rfm` | — |
| 47 | `aurora_decline_reasons` | d14 — decline taxonomy and concentration |
| 48 | `aurora_auth_reconciliation` | — |

**Two orphans, and both are findings.** Datasets 46 and 48 are bound to no chart: 46 produced the
RFM split recorded in `journeys.md`, 48 is the switch-to-ledger reconciliation used at Gate 3. A
dataset that only ever runs ad hoc is a dashlet nobody has built, not a dataset that is fine as it
is — it carries definitions nobody reviews. AU-04 is the same shape on the mandate link-health
metric. Note also that only 41 and 42 apply the epoch offset of `profile.md` §3; that split is the
whole of AU-08.

