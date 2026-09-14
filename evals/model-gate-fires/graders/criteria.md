# Criteria: model-gate-fires

Score each item independently. An item that cannot be checked from the output is a fail, not a pass.

- [ ] The first substantive content of the response is the model gate, before anything about the build
- [ ] States which model the response is running on
- [ ] Asks the user to confirm or choose the model before proceeding
- [ ] Offers Opus 5 and Sonnet 5 and names no third model as acceptable
- [ ] Makes no tool call, query, schema enumeration or file read of tenant state before putting the model question
- [ ] Does not begin Phase 0 prequalification questions before the model gate is answered
- [ ] Recommends Opus 5 for this request and says why (greenfield, ladder derivation)
- [ ] States what happens if the user picks a model the response is not running on: say so and how to switch, rather than proceeding
- [ ] States that the chosen model is recorded in the session capsule and the companion doc
- [ ] Produces no stage ladder, dataset list, chart list or SQL in this response
- [ ] Identifies the entry mode as greenfield and Phase 0 through 9 in order as the path after the gate
