# Tenant: `<name>` — profile

*Instance, schemas, conventions and the boundaries that hold for this engagement. Filled in
during Phase 0. Every line here was asked, not inferred.*

**As of `<date>` (rev 1).**

---

## 1 · Instance

| | |
|---|---|
| Superset host | `<host>` |
| Tenant id | `<id>` |
| Database connection name and id | `<name>` / `<id>` |
| Environment | **UAT / production** — confirmed by `<who>` on `<date>`, verified by reproducing `<a number the business already quotes>` |
| Market and currency | `<market>` / `<ccy>` |
| Go-live / market launch date | `<date>` — recorded in writing from `<who>`, not inferred (G8) |
| Confluence space and index page | `<space>` / `<page>` |

*If the environment row is not filled in from a reproduced number, nothing below it is trustworthy.
Names do not settle the UAT question (G10).*

## 2 · Schema families

One row per schema. Name the layer, because you never add across layers.

| Family | Layer | Typically holds | Confirmed here |
|---|---|---|---|
| `<schema>` | event stream / ledger / switch / core-service audit / vendor analytics / BI rollup | | |

**Join keys and their direction:**

- `<left>.<col>` ↔ `<right>.<col>` — unique on the right? `<yes/no>`; unmatched rate `<%>`

**Duplicate concepts across schemas** (G10). For every data point available in more than one
schema, record the candidates, the choice, the rejected alternatives and the count delta:

| Data point | Candidates | Chosen | Delta between them | Decided by / when |
|---|---|---|---|---|

## 3 · Conventions in force

- **Timestamp convention:** epoch base `<base>`, offset applied `<offset>`, matches the market? `<yes/no>`.
  A mismatch is a caveat and silently skews month boundaries.
- **Title separator:** ` · `
- **Metric prefixes in use:** `<f_ / p_ / se_ / ...>`. One conversion prefix per tenant, never two.
- **Dimension-value prefixes:** ordinal and letter prefixes are house style and control sort order.
  Never on metric verbose names.

## 4 · Internal users and the go-live boundary (G8)

- Go-live date: `<date>`
- Identifier available for internal users: `<column / value / date-cut only>`
- If the only identifier is the date cut, that limitation is a **shipped caveat**.
- Date-filter-exempt views checked separately: `<list>` — these contaminate silently.

## 5 · Third parties in the journey

Ask each one; never infer from another tenant's dashboard.

| Role | Vendor | Surfaces as |
|---|---|---|
| Identity / KYC | | decline categories, bucket labels |
| Bank connection | | route split, drop-off stage |
| Payments PSP | | repayment rails, failure reasons |
| Fraud engine | | decline categories |
| Device / risk | | |

## 6 · Feature availability matrix (G9)

Every cell asked, none assumed.

| Feature | Onboarding | App sign-up | Transactions | Repayments |
|---|---|---|---|---|
| `<feature>` | ✔ / ✖ / phased | | | |

## 7 · Known live defects

| # | Defect | Owner | Raised |
|---|---|---|---|

---

*Sibling files: `inventory.md` (objects and metrics), `journeys.md` (ladders and vocabulary),
`open-items.md` (the worklist), `revisions.md` (what changed and when).*
