# Operating modes: direct REST, Chrome extension, MCP connector

**There are three modes, not two.** This agent can run through **direct authenticated REST**
against `/api/v1/*` (a session cookie or token from any HTTP client — no browser, no MCP), through
the **Chrome extension** (driving the user's authenticated browser), or through an **MCP
connector** (a Superset, warehouse or database MCP server). All three work. They have different
strengths, and the best setup is usually a hybrid.

Direct REST is the mode that is easiest to forget and most often correct. The entire live state in
`${CLAUDE_PLUGIN_ROOT}/tenants/<name>/inventory.md` — dashboard ids and slugs, chart inventories, dataset SQL, metric
lists, the verbatim stage ladders — was gathered that way, with no browser open.

**Establish the mode in Phase 0, before promising anything.** Capability differs enough that the
plan changes.

## Detect, then confirm

1. Check what is actually available in the session — credentials for the Superset instance, the
   `claude-in-chrome` browser tools, a warehouse/Superset MCP server, or several of these.
2. Confirm with the user:

> I can work three ways: direct API calls against Superset with a token or session cookie, through
> your Chrome session, or through an MCP connector. Direct API is fastest and works unattended.
> I'll still need Chrome for two things — reviewing a CDP funnel, and eyeballing that the
> dashboard actually renders. Which do you have set up?

3. Smoke-test the path before building on it: one trivial query, one trivial API read.

If none is available, search the connector registry for a relevant MCP before falling back to
manual — do not silently assume the browser path.

## Capability matrix

| Capability | **Direct REST** | **Chrome extension** | **MCP connector** |
|---|---|---|---|
| Superset dataset / metric / chart / dashboard CRUD | ✔ full — every `/api/v1/*` verb | ✔ full, from page JS context | Only if the MCP exposes the Superset REST API |
| Enumerate an existing suite (Phase 0.5) | ✔ **best** — cheap, paged, scriptable | ✔ same calls, truncation-prone | Depends on what the connector exposes |
| Run ad-hoc SQL | ✔ `POST /api/v1/sqllab/execute/` | ✔ same endpoint from page context | ✔ usually direct to the warehouse — fastest |
| High-volume discovery queries | ✔ no page context, no truncation | ~ workable; responses truncate, aggregate in SQL | ✔ **best** |
| Gate 5 — chart↔dashboard M2M association | ✔ `GET /api/v1/dashboard/{id}/charts` | ✔ | ✔ if it exposes the REST API |
| Gate 5 — the pixels actually rendering | ✖ | ✔ **only path** | ✖ |
| Review a CDP dashboard | ✖ no usable read API | ✔ **only path** | ✖ |
| Read Confluence / SharePoint | ✖ unless separately credentialed | ✔ | Depends on the connector |
| Survives SSO / MFA without extra setup | ✔ a long-lived token or exported session cookie rides past both | ✔ rides the existing browser session | Depends on the connector's auth |
| Unattended / scheduled runs | ✔ | ✖ needs the browser open and authenticated | ✔ |

**Direct REST is strictly better than Chrome for everything except two things: verifying pixels,
and reviewing the CDP.** It is also, alongside MCP, one of only two unattended-capable modes — if
the user wants a recurring refresh, Chrome is not the answer.

## The hybrid pattern — the recommended default

Do not pick one mode and suffer with it. The standard shape:

- **Phase 0.5 inherit and Phase 6 build → direct REST.** Enumeration is many small paged reads and
  the writes are plain JSON; both are faster and cleaner without a page in the loop. Recipes:
  `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/superset-api.md`.
- **Phase 2 discovery and Gate 0/3 QC queries → MCP where one exists, direct REST otherwise.**
  These are many narrow queries at volume, and a warehouse MCP avoids the SQL Lab round-trip
  entirely.
- **Phase 1 CDP review → Chrome.** There is no other path.
- **Gate 5 pixel check → Chrome.** Check the M2M association over REST first; open the browser only
  to confirm the dashboard renders.

Keep the Definition Registry as the shared artefact across all three — it is the thing that makes
a split-mode build coherent.

## Direct REST mode: operating notes

- Authenticate once and confirm it worked before building: `GET /api/v1/me/` or any cheap list
  endpoint. A 302 to a login page is the usual failure and it does not look like an error.
- Two auth routes: a session cookie exported from an authenticated browser, or
  `POST /api/v1/security/login` for a JWT you then send as `Authorization: Bearer`. Both survive
  SSO/MFA, because both are obtained *after* it.
- List endpoints need Rison-encoded `q=` parameters and they are not optional at suite scale — the
  default page size will lie to you about how many objects exist. Syntax:
  `${CLAUDE_PLUGIN_ROOT}/skills/superset-build/references/superset-api.md`.
- CSRF may not be enforced (it is not on every deployment). If a POST 400s on CSRF, fetch
  `/api/v1/security/csrf_token/` and send `X-CSRFToken` with the matching session cookie.
- **Never `SELECT *`** on a table with nested/`SUPER` columns — it will blow the response.
- This is the only mode where you can be truly non-interactive. That cuts both ways: nobody is
  watching, so verify every write by reading it back.

## Chrome mode: operating notes

- Call the tab-context tool once at the start. **Create a new tab** for this work; do not reuse
  tab ids from another session. If a tool errors that a tab is invalid, re-read the context
  rather than retrying.
- Site permissions must be granted for the Superset instance (and the CDP) in the extension
  before anything works. If calls fail immediately, this is the first thing to check.
- **`window.*` is wiped by navigation.** Re-install the SQL/API helpers after every page load, and
  never park in-progress content on `window` across a navigation.
- **Never trigger a JS `alert`/`confirm`/`prompt` or a browser modal.** They block all subsequent
  extension commands and the session goes unresponsive until the user dismisses it manually.
  Avoid clicking anything with a confirmation dialog; use the REST API instead of UI buttons for
  destructive operations.
- Keep response payloads small — aggregate in SQL, slice long JSON before returning.
- Watch for `beforeunload` handlers on analytics SPAs when navigating away from an edited view.
- If browser calls fail two or three times in a row, stop and tell the user what you tried rather
  than looping.

## MCP mode: operating notes

- Confirm the database/instance the connector actually points at before running anything — a
  connector named for one tenant may be scoped to another.
- Confirm it is read-only. This agent never writes to the warehouse.
- If the MCP exposes SQL but not Superset object CRUD, say so early and plan the hybrid rather
  than discovering it at build time. Direct REST is the natural other half.
- Interactively authenticated connectors may be absent in headless runs. If the user wants a
  scheduled refresh, check that the credential survives the laptop closing.

## What does not change between modes

The method, the prequalification, the Definition Registry, the QC gates and the triangulation
requirement are identical. Mode affects *how* you reach the data, never *what you are allowed to
publish without checking*.

**One caveat does change, and it applies to any non-browser mode — direct REST and MCP alike.**
Gate 5 has two halves and they are not equally reachable:

- **The M2M association half is checkable by API in every mode.**
  `GET /api/v1/dashboard/{id}/charts` tells you whether the chart is actually attached, which is
  the cause of nearly every blank dashlet. Run it. There is no excuse for skipping this one.
- **The pixel half is Chrome-only.** Whether the chart renders, whether a component points at a
  deleted chart, whether the layout survived the write — you cannot see any of it without a
  browser.

In a non-browser mode, report exactly which half you checked, and ask the user to eyeball the
dashboard for the other. Never report a clean Gate 5 you could not actually perform.
