# Criteria: entity-not-event

Score each item independently. An item that cannot be checked from the output is a fail, not a pass.

- [ ] Does not ship the event count on its own as requested
- [ ] Adds a unique-entity figure beside it (entities with at least one failed collection in the period), or states why one is unavailable
- [ ] Establishes the entity explicitly as account, mandate, card or customer rather than assuming one
- [ ] States that the event count and the entity count will differ, often several-fold, and are not interchangeable
- [ ] Names G11 or Gate 1b as why the entity figure is not optional
- [ ] States that the bridge from failure rows to the entity must be validated on the failing rows specifically
- [ ] Gives the metric a label that does not let a reader mistake failures for customers
- [ ] Does not leave Superset's default `count` metric on the dataset
- [ ] Requires a Definition Registry row for each new metric before it is published
- [ ] Does not report the metric as built, published or verified without the gates having run
