# Product artefacts — ground the journey before you model it

**The warehouse tells you what fired. It cannot tell you what was supposed to fire.** That
difference is where the expensive mistakes live, and no amount of schema discovery closes it.

Four failure modes, all invisible from the data alone:

| Failure | What you see in the data | What it actually is |
|---|---|---|
| **Built but not launched** | A state with zero rows, or a step that loses 100% | A feature flag that is off, or a phased rollout that hasn't reached this segment |
| **Launched but not instrumented** | A stage that doesn't exist | A real step in the journey with no event behind it — the funnel silently skips it |
| **Instrumented but renamed** | A permanent zero from a fixed date | The app changed the event name; the old one will never fire again |
| **Not in this engagement at all** | Nothing — because you never looked for it | You ported another tenant's ladder and are now measuring a journey this product doesn't have |

A funnel built without the product artefacts is a description of the instrumentation, not of the
journey. It will be confidently wrong, and it will be wrong in the direction that flatters the
product — because unfired events look like steps nobody reached.

---

## 1 · Ask for the artefacts — Phase 0.1c

Ask **once, batched, before any SQL**, and ask per module. The agent is not entitled to these and
may not get all of them; the point is to know what you're missing before you build, not after.

> To build a funnel that matches the journey rather than the instrumentation, I need whatever
> exists of the following. Partial is fine — I'll tell you what I'm missing and what that costs.
>
> 1. **PRDs** — Confluence links or attachments, per module. Especially the acquisition /
>    pre-onboarding spec and the onboarding spec, which differ most between engagements.
> 2. **Designs** — Figma links for the journeys in scope, including the error and edge-case
>    screens.
> 3. **The event dictionary / tracking plan** — whatever names the events and says which are
>    server-side and which are app SDK.
> 4. **Feature availability per module** — which of these actually exist in *this* engagement,
>    and which are live vs built-but-off. (See §5 for the repayments list, which is the most
>    variable.)
> 5. **Cohort definitions the product team already uses** — if they segment users a particular
>    way in the PRD, the dashboard should use the same words.

**If the answer is "there's no PRD" or "the designs are out of date", that is a finding, not a
blocker.** Record it, use the fallback ladder in §7, and ship the limitation as a caveat.

---

## 2 · How to read a PRD for BI purposes

You are not reviewing the product. You are extracting six things. Read for these and skip the rest.

| Extract | Why it matters | What to write down |
|---|---|---|
| **The stage list, in order, with the product's own names** | This is the funnel spine, and the tenant's vocabulary is the vocabulary the dashboard must use | Each stage, its entry criterion and its exit criterion |
| **Parallel routes and segment splits** | A route that skips a stage makes a linear funnel non-monotonic. This is the single most common modelling error | Which segments take which path, and what determines the split |
| **Decision points and their outcomes** | Approved / referred / declined and every variant. A decision is not a drop-off | The full outcome vocabulary, including the ones that are rare |
| **Cohort definitions** | If the PRD says "new-to-bank" and the dashboard says "new users", nobody can reconcile them | The definition verbatim, and the field that implements it |
| **Feature flags, phasing and rollout plan** | Explains zeroes that are not drop-off. Also tells you which stages will appear later | Which features are on, for whom, from when |
| **Explicit out-of-scope** | Stops you building a dashlet for something that was deliberately deferred | The list, and the date it was decided |

**Two things a PRD will not tell you** and you must not infer from it: whether the thing was
actually built the way it was specified, and whether it was instrumented. That is what §4 is for.

---

## 3 · How to read designs (Figma) for BI purposes

Designs are the closest thing to a map of the front-end event surface, and they are the fastest
way to find the drop-off reasons you will need at L4.

- **Every distinct screen is a candidate FE event.** Count the screens in a journey and compare to
  the number of FE events that exist. A large gap means the funnel cannot explain *where in a
  step* people leave.
- **The error, decline and edge screens are the L4 vocabulary.** What does a user see when the
  bank connection fails, when identity verification is inconclusive, when a mandate is rejected?
  Those screens usually map one-to-one onto the drop-off buckets worth reporting.
- **Skip paths and conditional screens** confirm the parallel routes from the PRD. If the design
  shows a segment bypassing three screens, the funnel must branch.
- **Retry and re-entry flows** determine whether an entity can occupy a stage twice. This decides
  the grain and whether the funnel can be user-keyed at all.
- **Screens with no event behind them** are the honest answer to "why can't you tell me where they
  dropped?" — and belong in the caveats with an instrumentation ask.

Where there is no Figma access, a walkthrough of the app or a recorded demo answers the same
questions. Ask for one.

---

## 4 · The three-way reconciliation — PRD ↔ Design ↔ Events

**Do this before modelling, and show it back.** Every mismatch is either a finding for the product
team or a correction to your funnel. Neither should be discovered after publication.

| Pair | Agreement means | A mismatch means |
|---|---|---|
| **PRD ↔ Design** | The spec was designed as written | Scope changed after the PRD. **The design is usually the more current of the two** — check the dates |
| **Design ↔ Events** | The screens people see are instrumented | A step exists that the funnel cannot see. This is an instrumentation gap, and it becomes a caveat plus a ticket |
| **PRD ↔ Events** | The journey is measurable as specified | Either the feature isn't built, isn't launched, or fires under a different name. Check first-seen dates before concluding |
| **All three agree** | Model it | — |
| **All three differ** | — | Stop. Ask. Do not pick the one that makes the nicest funnel |

Record the result as an **artefact register** and ship it with the companion doc:

| Stage / feature | In PRD | In design | Event exists | Event firing (first seen) | Verdict |
|---|:---:|:---:|:---:|---|---|
| Bank account verification | ✔ | ✔ | ✔ `…` | 2026-06-29 | Model as a stage |
| Income verification | ✔ | ✔ | ✖ | — | **Gap** — caveat + instrumentation ask |
| Manual review queue | ✔ | ✖ | ✖ | — | Deferred; do not model |
| Referral bonus screen | ✖ | ✔ | ✔ `…` | 2026-07-24 | **Built after the PRD** — confirm scope |

---

## 5 · The feature availability matrix — mandatory before Phase 4

**No two engagements have the same feature set.** Assuming they do is Directive 1's failure mode,
and repayments is where it bites hardest — the module has the widest variation in the estate.

Fill this per module before modelling. **Every cell is asked, not assumed.**

| Feature | In this engagement? | Live or built-but-off? | Event exists? | In scope for v1 dashboard? |
|---|---|---|---|---|

### 5.1 Repayments — the variability list

Ask about every row. None of these is universal, and several are mutually exclusive.

**Rails and instruments**

- Direct Debit (and which scheme)
- VRP / variable recurring payments
- Open Banking single payment
- External bank transfer / push payment
- Card payment
- Standing instruction
- Wallet or stored balance

**Payment gateway / PSP** — *which one*, and whether there is more than one. The PSP's name shows
up in state literals, bucket labels and metric names; a doc that says "the PSP" is unreadable six
months later. Ask also whether a **fallback PSP** exists, because a payment that fails on one and
succeeds on the other will look like a retry.

**Features**

- Autopay / auto-debit — full balance, minimum due, or fixed amount?
- One-time / ad-hoc payment
- Scheduled future-dated payment
- Partial payment and overpayment
- Mandate modification (amount, date, account)
- Mandate cancellation, and whether it bypasses the state machine
- Retry logic — automatic, and how many attempts
- Refunds, reversals and returns

**Questions that change the model, not just the labels**

- Can a user hold **more than one mandate**? Then the funnel is mandate-keyed, not user-keyed.
- Can a payment **fall back from one rail to another**? Then a single logical payment has two
  technical records and naive counting double-counts it.
- Is the **initiation source** a separate axis from the rail? (App / autopay / external / agent.)
  Conflating the two produces a rail breakdown that doesn't sum.
- Does a payment **post to the ledger** on a different day from the PSP confirmation? Then the
  payments funnel spans two layers and needs the upstream/downstream treatment.

### 5.2 Onboarding — the variability list

- Pre-application stage: does one exist, what is it called, is it a credit decision or a marketing
  qualification, binary or tiered?
- Bank connection / open banking: mandatory, optional, or route-dependent?
- Identity verification vendor and whether it is synchronous
- Document upload and e-signature
- Manual review / referral queues and their outcomes
- Multiple product variants with different ladders

Full method for these two: `acquisition-source.md`, `${CLAUDE_PLUGIN_ROOT}/skills/onboarding-funnel/SKILL.md`,
`${CLAUDE_PLUGIN_ROOT}/skills/repayments/SKILL.md`.

---

## 6 · FE and BE triangulation, before building

Directive 3 says backend is truth and front-end corroborates. That is a rule about *modelling* —
but you cannot apply it until you know, per stage, **what instrumentation exists at all**.

For each stage in the confirmed ladder, establish:

| | Question |
|---|---|
| **BE** | Is there a server-side or CDC event? What is its name, and from what date has it been emitted? |
| **FE** | Is there an app SDK event? Which screen does it correspond to? |
| **Neither** | The stage is invisible. Say so on the chart — do not quietly drop the step, because the funnel will then imply that everyone who left the previous stage reached the next one |
| **Both** | Model the funnel on BE; use FE for the drop-off detail inside the step. Ship the coverage comparison as its own dashlet |

**The coverage dashlet is not optional where both exist.** Backend-vs-app-side coverage is how you
find out that an FE event fires on screen load while the BE event fires on submit — which makes
them look like a 40% drop when it is a definitional difference.

**Check first-seen date per event, always.** An event introduced mid-stream cannot be a funnel
entry, and this has already produced a live defect.

---

## 7 · When the artefacts don't exist

Common, and not a reason to stop. Work down this ladder, and record where you landed:

1. **PRD** — the intent.
2. **Event dictionary / tracking plan** — often more current than the PRD.
3. **Designs** — usually the most current artefact of all.
4. **The app itself** — a walkthrough or a demo recording.
5. **The engineer who built it** — one message, and usually definitive.
6. **The transition matrix** (`${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/schema-discovery.md` §3) — derive the ladder from observed state
   transitions.

**Never skip straight to 6 and present the result as the journey.** A derived ladder is a
hypothesis about the journey; it must be shown back and confirmed before anything is built
on it (Guardrail G3). State in the companion doc which rung you reached:

> *Journey grounded in: event dictionary + designs. No PRD available for repayments. The ladder
> below was derived from the transition matrix and confirmed by <name> on <date>. Stages marked ⚠
> have no backend event and cannot be measured.*

---

## 8 · Output of this phase

Three artefacts, all shipped with the companion doc:

1. **The artefact register** (§4) — what was read, what agreed, what didn't.
2. **The feature availability matrix** (§5) — per module, with in-scope decisions.
3. **The confirmed ladder** — the stage list, in order, with parallel routes drawn, **shown back
   to the user and agreed** before Phase 4.

Plus, for anything the data cannot answer: an instrumentation ask with an owner. That list is
often the most valuable thing the first dashboard delivers, because it is what makes the *second*
one possible.
