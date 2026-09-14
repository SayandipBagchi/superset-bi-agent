# Tenant: `aurora` — open items

Author: Sayandip Bagchi.

*Illustrative example on invented data. The Gate 3 reconciliation worklist and the numbered open
items with owners. Read at Phase 8, and whenever a gate fails.* **As of 2026-06-12 (rev 5).**

## Gate 3 reconciliation worklist

Every data point computed in more than one place. These break first, and each needs a recorded
delta rather than an assumption that they agree.

| Pair | Status |
|---|---|
| Applications started: `origination_analytics.applications` vs `events_curated.application_events` | **Open** — 27% landing-coverage gap, unexplained (AU-05) |
| Posted spend (dataset 45) vs authorisations (`bi_100001.auth_rollup_base`) | Reconciled rev 4 via dataset 48. Different measures; never summed |
| Ever-transacted (274, lifetime) vs spend-active (154, reporting month) | Reconciled rev 4. Different denominators, kept in different sentences |
| Repayment objects vs ledger accounts | Reconciled rev 5 on `account_ref`: 1,388 of 1,391 |

## Open items

| Id | Item | Kind | Owner |
|---|---|---|---|
| AU-01 | Timezone offset: datasets 41 and 42 convert epochs with `interval '5.5 hours'` on a UK product. Deliberate or defect — **unresolved** | Defect | product |
| AU-02 | `stage_reached` × `overall_outcome` cross-tab not built | Gap | unassigned |
| AU-03 | No acquisition-source dimension exists on dataset 44; source-split dashlets are not applicable here | Scope | — |
| AU-04 | Mandate link-health metric exists on dataset 43 but has no chart | Gap | unassigned |
| AU-05 | 27% landing-coverage gap between the event stream and the origination vendor | Analysis | product + engineering |
| AU-06 | Two front-end events no dataset reads: `applicationStartClick`, `ApplyCTAClicked`. Candidate intent signals, never evaluated | Analysis | unassigned |
| AU-07 | Superset default `count` metric still present on dataset 44 | Defect | **closed rev 5** |
| AU-08 | Cross-dashboard month boundaries differ between epoch and non-epoch datasets | Defect | unassigned |

Four of the eight have no owner. That is recorded rather than tidied away: an unassigned item is a
decision nobody has taken, and it reads differently in a review from one somebody is working on.
AU-01 and AU-05 are the two that change published numbers if they resolve the wrong way.

