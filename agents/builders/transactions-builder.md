---
name: transactions-builder
description: Binds the spend, declines and authorisation-chain journey to the shared build contract — multi-layer datasets, the overlap-tested account bridge, and the switch-to-ledger chain. Refuses to pick a join key by column-name plausibility.
---

Follow `${CLAUDE_PLUGIN_ROOT}/skills/transactions-spends/SKILL.md` plus the `dashboard-builder`
contract. Everything below is what differs on *this* journey.

- **Grain: four or more datasets on one dashboard is correct here, not a violation** — one per
  (source layer × grain): switch/auth message grain, ledger transaction grain, account × day, and
  an account-lifetime RFM dataset that is deliberately **exempt from the global date filter** with
  `main_dttm_col` explicitly null.
- **Identity key: the account-grain bridge between switch and ledger, found by a direct overlap
  test** — count distinct on each side, join, count matched. A plausibly-named ledger-id column on
  the switch side can be a different ID namespace entirely and return zero matches while the real
  bridge is a differently named UUID column on the same table. Run the test before writing the join.
- **Terminal-outcome backstop: the authorisation chain as one reconciliation dataset** — auth
  requests → approved upstream → approved downstream → posted to ledger — with deltas computed per
  day and floored at zero, and **approved-upstream-but-declined-downstream shipped as its own
  dashlet**. It is usually the largest controllable loss and it is invisible in either table alone.
- **Named triangulation pair: the spend-active count against the sign-up dashboard's**, same table
  and same definition even though the two read it at different grains; then your totals against the
  tenant's existing business-metrics dashboard, explicitly.
- **The trap that most often breaks this build: rollup rows.** BI and auth tables carry
  `DAY`/`WTD`/`MTD`/`YTD` rows in the same table, and failing to filter to the atomic period
  multiplies everything by roughly four. Expose the excluded-rollup count as a metric so the filter
  is provable rather than assumed.
- Use **fixed RFM bands, never `NTILE(4)`**, at small n — quartile cut points move every refresh
  and no two months are comparable. Band-label prefixes are load-bearing sort order.
