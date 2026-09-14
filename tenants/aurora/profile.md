# Tenant: `aurora` — profile

Author: Sayandip Bagchi.

> **An illustrative example on invented data.** Aurora is not a real engagement: the host, ids,
> vendors and every figure are fictional. It ships so the shape of a tenant directory and the five
> lessons it carries are legible without reading a real client's state.

*Instance, schemas, conventions and boundaries. Filled in during Phase 0; every line was asked, not
inferred.* **As of 2026-06-12 (rev 5).**

## 1 · Instance

| | |
|---|---|
| Superset host | `superset.example.internal` |
| Tenant id | `100001` |
| Database connection name and id | `aurora-warehouse` / `3` |
| Environment | **production** — confirmed by the programme lead on 2026-04-10, verified by reproducing the published "applications started" figure of 1,240 |
| Market and currency | UK / GBP |
| Go-live / market launch date | **2026-03-02** — recorded in writing, not inferred (G8) |
| Confluence space and index page | `<SPACE>` / `<PAGE_ID>` |

## 2 · Schema families

| Family | Layer | Holds | Confirmed |
|---|---|---|---|
| `card_core_service_100001` | core-service audit (CDC) | `automatic_payment_config_audit`, `payment_audit` | Repayments spine; transitions, not snapshots |
| `ledger_100001.account_day_base` | ledger | account × day facts | Source of truth for posted spend |
| `bi_100001.auth_rollup_base` | BI rollup | pre-aggregated authorisations | Carries `time_period` rollup rows — **filter to `DAY` or every figure multiplies** |
| `events_raw.raw_events_data` | event stream | all events, 18,400 rows, incl. `aurora-onboarding-event` | The only place the backend ladder exists |
| `events_curated.application_events` | event stream (curated) | **six front-end events only** | No backend ladder; curation dropped it |
| `origination_analytics` | vendor analytics | `applications` (records and outcomes), `quotations` (soft-eligibility checks) | Yes — see the `approval_status` trap, §3 |

**Join keys and their direction:**

- repayment object `.account_ref` ↔ `ledger_100001.account_day_base.ledger_account_id` — unique on
  the right? yes; unmatched 3 of 1,391 (0.2%). **The working bridge.**
- `payer_ledger_id` ↔ `ledger_account_id` — **rejected.** Zero overlap, 31% empty string
  (Lesson 3, `journeys.md`).

**Duplicate concepts across schemas** (G10):

| Data point | Candidates | Chosen | Delta | Decided |
|---|---|---|---|---|
| Applications started | `origination_analytics.applications`; `events_curated.application_events` | origination | 27% of landings never reach the vendor record | rev 2 (AU-05) |
| Spend | `ledger_100001.account_day_base`; `bi_100001.auth_rollup_base` | ledger, for posted spend | Not like-for-like — authorisations are attempts, ledger rows are postings. **Never summed** | rev 4 |

## 3 · Conventions in force

- **Timestamp convention:** epoch base milliseconds, offset `interval '5.5 hours'` on datasets 41
  and 42, matches the market? **No** — this is a UK product. Deliberate or defect is unresolved
  (AU-01). It skews month boundaries silently, which is AU-08 on a second dashboard.
- **Title separator:** ` · `. **Metric prefixes:** `f_` funnel counts, `p_` conversions, `se_`
  soft-eligibility measures — one conversion prefix, never two. **Dimension-value prefixes:**
  ordinal prefixes are house style and control sort order; never on metric verbose names.
- **`approval_status` does not mean what it says (Lesson 5).**
  `origination_analytics.applications.approval_status` reads like the application outcome. It is
  the **soft-eligibility** decision. It shows **22** declines; the real application declines are
  **386**, in a different column entirely. A funnel built on the obvious column undercounts
  declines seventeen-fold, renders cleanly and errors on nothing. Every dashlet touching that
  table is checked against this before it ships.

## 4 · Internal users and the go-live boundary (G8)

Go-live **2026-03-02**. Internal users carry an account-level flag — **not** a date cut, which
matters because 24 of the 498 accounts on book are internal (4.8%) and they keep transacting after
go-live. Internal activity is **excluded by default**, shown as a separate segment on request.
Date-filter-exempt views checked separately: the `bi_100001.auth_rollup_base` rollup rows, which
survive a date filter and contaminate silently.

## 5 · Third parties in the journey

| Role | Vendor | Surfaces as |
|---|---|---|
| Identity / KYC | IDCheck | identity-verification pass/fail, decline categories |
| Bank connection, origination and decisioning | LoanFlow | route split, drop-off stage, decision outcome |
| Payments PSP | Larkspur Pay | repayment rails, mandate authorisation, failure reasons |
| Fraud engine | Sentinel | decline categories |
| Device / risk | Sentinel Device | risk-step outcomes |
| Credit bureau, at soft eligibility | Northgate Bureau | soft-eligibility pass/fail |

## 6 · Feature availability matrix (G9)

| Feature | Onboarding | App sign-up | Transactions | Repayments |
|---|---|---|---|---|
| Pre-application stage (soft eligibility) | ✔ | — | — | — |
| Backend stage ladder in events | ✔ (`events_raw` only) | ✖ | — | — |
| Acquisition-source dimension | ✖ (AU-03) | ✖ | ✖ | ✖ |
| Card activation separate from account activation, D7–D60 cohorts | — | ✔ | — | — |
| RFM segmentation | — | — | ✔ (queried, no chart) | — |
| Autopay config, one-off payments, mandate link-health metric | — | — | — | ✔ (link health has no chart — AU-04) |

## 7 · Known live defects

| # | Defect | Owner | Raised |
|---|---|---|---|
| AU-01 | Datasets 41 and 42 apply `interval '5.5 hours'` on a UK product — **unresolved** | product | rev 2 |
| AU-08 | Month boundaries differ between epoch and non-epoch datasets | unassigned | rev 5 |
| — | `approval_status` is the soft-eligibility decision, not the application outcome (§3) | documented, not open | rev 4 |

The full tracker, gaps included, is in `open-items.md`.

*Siblings: `inventory.md`, `journeys.md`, `open-items.md`, `revisions.md`.*
