# Tenant: `aurora` — journeys

Author: Sayandip Bagchi.

*Illustrative example on invented data. The derived stage ladder per journey, the vocabulary
verbatim, and the dated worked examples. Read the section for the journey you are working on, and
only that section.* **As of 2026-06-12 (rev 5).**

## 1 · Onboarding

**Live.** Soft eligibility (Northgate Bureau; a credit decision, binary), application creation,
identity verification (IDCheck), bank connection and decisioning (LoanFlow), account creation. The
backend ladder exists only in `events_raw.raw_events_data`, on `aurora-onboarding-event` —
`events_curated.application_events` carries six front-end events and no ladder, so it cannot answer
a single funnel question. Ladder derived from the `previous_state → state` transition matrix,
confirmed with the programme lead at rev 2.

| Stage | Count | Of previous |
|---|---|---|
| Soft eligibility checks | 64,300 | — |
| Passed eligibility | 15,100 | 23.5% |
| Progressed to an application | 1,240 | 8.2% |
| Applications started | 1,240 | — |
| Identity verification passed | 1,020 | 82.3% |
| Bank connection completed | 920 | 90.2% |
| Decisioned — approved | 612 | 66.5% |
| **Onboarded** | **498** | **81.4%** |

The 1,240 resolve into 612 approved, **386 declined** and 242 abandoned before any decision —
decision loss and behavioural loss never share a bucket. Of the 612 approved, 498 onboarded.

**Worked example — Lesson 1, the pre-funnel framing contrast (rev 2, 2026-04-24).** The question
asked was "why is the funnel leaking at bank connection". That stage lost **100** applications
(1,020 verified, 920 connected) — real, worth fixing, and the whole programme was watching it. The
stage nobody had a chart for lost **13,860**: 15,100 passed eligibility, 1,240 progressed to an
application. Pre-qualified, told they were eligible, gone. Same funnel, two orders of magnitude
apart. The finding was not a conversion rate — it was that the funnel started in the wrong place.
**Where you draw the first stage decides what the answer can be.**

## 2 · App sign-up

**Live.** App sign-in, account activation and card activation as separate steps, first posted
transaction, activation-window cohorts. Dataset 42 on d13, keyed on the account and cohort-dated on
the onboarding date so a date filter cannot split one customer across two periods.

| Step | Count | Of previous | Lost |
|---|---|---|---|
| Onboarded | 498 | — | — |
| Signed in to the app | 470 | 94.4% | 28 |
| **Card activated** | **291** | **61.9%** | **179** |
| First posted transaction | 274 | 94.2% | 17 |

Activation-window cohorts, of the 291 activated: **D7 184 · D15 231 · D30 266 · D60 291** — 184
within a week, then 47, 35 and 25. Nobody activates after D60 here, so D60 is settled, not truncated.

**Worked example — Lesson 2, the activation cliff (rev 3, 2026-05-08).** Four steps, three
conversion rates: 94.4%, 61.9%, 94.2%. Reported as a table, every row invites a workstream and the
reader leaves with no decision. 224 customers were lost between onboarding and first spend, and
**179 of them — four in five — at card activation alone**; the other two steps lost 28 and 17
between them. So the sentence is not "end-to-end conversion is 55%" but *activation is the only
cliff; the rest of the journey already works.* One fix, one step, aimed at the first seven days
where 184 of the 291 activations happen.

## 3 · Transactions and spends

**Live.** Posted spend from `ledger_100001.account_day_base`, authorisations from
`bi_100001.auth_rollup_base` (filter `time_period = 'DAY'`), decline taxonomy on dataset 47, RFM on
dataset 46. Internal accounts carry a flag and are excluded by default (G8).

| | Total | Internal | Customer | Internal share |
|---|---|---|---|---|
| Accounts on book | 498 | 24 | 474 | 4.8% |
| Spend-active accounts | 163 | 9 | 154 | 5.5% |
| Transactions | 1,412 | 71 | 1,341 | 5.0% |

Customer spend **£68,240** across 1,341 posted transactions, **£50.89** average ticket.

**Two denominators that look like one.** 274 accounts have ever posted a transaction (§2, lifetime);
154 are spend-active (at least one posting in the reporting month). Declines are not inside the
1,412 either — those are attempts, the 1,412 are postings, and summing across the switch and the
ledger is the error dataset 48 exists to catch.

**RFM over the 154.** 48 Champions drove 61% of transactions — roughly 820 of the 1,341 — at about
£31 a ticket; 39 lower-frequency accounts turned over almost the same value at about £118 a ticket;
67 sit between them. Near-identical revenue, opposite behaviour: a frequency campaign aimed at the
average customer here would be aimed at nobody.

**Worked example — Lesson 3, the account bridge with zero overlap (rev 4, 2026-05-29).** The
repayments object carries `payer_ledger_id`; the ledger carries `ledger_account_id`. Names agree,
types agree, and the join was written on that basis. Tested before use: **zero overlap** — not a
low match rate, no row matched any row. 31% of the values were the empty string and the rest
belonged to a different id space. The working bridge was found by testing **every id-shaped
column** for overlap against `ledger_account_id` rather than by reading names: `account_ref`, at
**1,388 of 1,391** rows (99.8%). **Never take a join key on the evidence of its name.** Overlap is
one cheap query; a dashboard on a plausible key fails silently, which is the expensive way.

## 4 · Repayments

**Live.** Direct Debit via Larkspur Pay. Autopay configuration audited in
`card_core_service_100001.automatic_payment_config_audit`, payments in `payment_audit` — both **CDC
tables, transitions not snapshots**, so a mandate's current state is the last row for that mandate,
never a `count(*)`. Dataset 43 on d15, nine charts. Mandate ladder, from the CDC transition matrix
at rev 5: `initiated → authorised → active`, with `deleted` and `failed` terminal and reachable
from any of them. **Stage counts are not recorded here** — they were not reconciled against the PSP
before rev 5 closed, and an unreconciled count reconciles against itself and is wrong, which is
worse than a blank.

**Worked example — mandate link health, a metric with no chart (rev 5, 2026-06-12).** Dataset 43
defines a link-health metric: the share of repayment objects that bridge to a ledger account. On
the corrected bridge it reads **1,388 of 1,391, 99.8%**; on the plausible-looking `payer_ledger_id`
it read **zero**, and would have been published as a data outage. No chart reads it (AU-04) — so
the next person to ask "are mandates linking?" will write a fourth definition of it.

## 5 · Concentration

**Live.** Declines on dataset 47, at event grain, converted to account grain: unique accounts
affected, attempts per affected account, fixed bands, decile Pareto with cumulative share, and
band-by-reason composition.

**Worked example — Lesson 4, the subtraction chain (rev 5, 2026-06-12).** Never report the raw
event count. Subtract in order and **show the chain** — every step of it is a question somebody
will otherwise ask in the review:

| Step | Events |
|---|---|
| Decline events, raw | 1,204 |
| − no account id (attributable to nobody) | −3 → 1,201 |
| − internal accounts (G8) | −11 → 1,190 |
| − pre-go-live activity (G8) | −28 → 1,162 |
| **Attributable declines** | **1,162** |

**212 unique accounts affected, 5.5 attempts per affected account.** The headline that survives a
review is not "1,204 declines" but "212 customers, most of them more than once". **And the tail is
the finding.** The top decile — **22 accounts** — caused **41%** of all declines, and the tail is
not the body at higher volume: the 1–2 attempt band is dominated by `insufficient_funds`, a
customer-balance story, while the 10+ band is dominated by `card_not_activated`, an onboarding
defect that sends the customer back to §2's cliff. Reported as one number they cancel into
something nobody can action. Split by band, one goes to comms and the other to engineering — and
the 10+ band is a work queue of named accounts, not a reporting line.

