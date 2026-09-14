# Criteria: single-system-funnel-key

Score each item independently. An item that cannot be checked from the output is a fail, not a pass.

- [ ] Names the population the origination system cannot see: people whose events fired but for whom no record was ever created
- [ ] Does not report the funnel as complete, healthy or defensible on the evidence given
- [ ] States the direction of the error: a single-system funnel under-counts the top and flatters every rate below it
- [ ] Requires all three populations to be counted (in both systems, record-only, stream-only) before the entry step is accepted
- [ ] Proposes the terminal-outcome backstop: query for entities carrying a terminal outcome that sit outside the entry population
- [ ] Requires the coverage check to run in both directions, not only stream against vendor
- [ ] Does not propose replacing the origination system with the event stream
- [ ] States that the entry step may have to be a union, deduplicated on a key both systems carry
- [ ] Requires an entry-source decomposition whose values sum exactly to the entry step
- [ ] Notes that sub-funnels sliced on a vendor-supplied dimension cannot classify the stream-only population
- [ ] Does not repeat 92% as a defensible conversion rate without stating that its denominator is in question
