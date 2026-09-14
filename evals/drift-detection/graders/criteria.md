# Criteria: drift-detection

Score each item independently. An item that cannot be checked from the output is a fail, not a pass.

- [ ] Does not conclude "no data" or that the step genuinely has zero volume
- [ ] Names schema drift as a leading hypothesis: an event renamed or no longer emitted reads as a permanent zero
- [ ] Directs checking first-seen and last-seen date per state value rather than only a count
- [ ] Distinguishes a true zero from an instrumentation zero and says how to tell them apart
- [ ] Names establishing the exact date the series went to zero, and that a clean cliff on a fixed date points at a rename rather than behaviour
- [ ] Cites the observability reference (`references/observability.md`) as where the drift procedure lives
- [ ] Names schema drift as one of the three tracked drifts rather than treating drift as a single undifferentiated thing
- [ ] Checks the filter, the offset and the state spelling before concluding anything about the underlying journey
- [ ] Does not propose editing the chart, its filters or an expected value to make the zero go away
- [ ] Ends by placing the finding as a doc fix, a build ask or a shipped caveat, with an owner
- [ ] Quotes no volume, rate or recovery figure for the step as a fact
