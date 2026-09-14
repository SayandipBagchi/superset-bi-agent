# Versioning and the SharePoint document home

Every change to this skill is versioned, and every version is archived in SharePoint alongside
the supporting docs and presentations that explain it. The point is not tidiness — it is that a
stakeholder who reads a dashboard companion doc in November needs to be able to find the skill
version that produced it.

---

## 1 · The SharePoint home

**Root:** an agent-docs folder in SharePoint or OneDrive for Business — one root for all agents,
whose URL your organisation's document estate determines. Record the URL once in the tenant
profile rather than here, so this file stays portable.

```
<agent-docs root>/
└── superset-bi-agent/
    ├── skill-docs/          current version of SKILL.md and every reference file
    ├── supporting-docs/     audits, definition registries, companion docs, session capsules
    ├── presentations/       stakeholder decks and architecture one-pagers
    └── archive/             every superseded version, one folder per version
```

One agent, one folder under the root. When another agent gets the same treatment, it becomes a
sibling of `superset-bi-agent/`, not a subfolder of it.

### What goes where

| Folder | Contents | Naming |
|---|---|---|
| `skill-docs/` | `SKILL.md`, `references/**` — **current version only** | Mirror the repo layout; keep `references/` as a real subfolder |
| `supporting-docs/` | Audit reports, definition registries, dashboard companion docs, session context capsules, release notes | `<yyyy-mm-dd>-<topic>.md` |
| `presentations/` | Decks and one-pagers for stakeholders | `<yyyy-mm-dd>-<topic>.pptx` / `.html` |
| `archive/` | One folder per superseded version, containing that version's complete `skill-docs/` tree | `v<major>.<minor>.<patch>/` |

`CHANGELOG.md` lives at `superset-bi-agent/` root — one file, never archived, always appended.

---

## 2 · Version numbering

Semantic, against the *behaviour of the agent*, not the byte count of the docs.

| Bump | When |
|---|---|
| **Major** (`2.0.0`) | The operating contract changes — a new guardrail that can refuse work, a restructure of SKILL.md, a new mandatory phase, a change to what "done" means |
| **Minor** (`2.1.0`) | New reference file, new playbook, a new gate, a materially rewritten phase, a new tenant current-state file |
| **Patch** (`2.0.1`) | Corrections to live state, stale names, typos, added open items, refreshed worked examples |

The version is **declared once**, in `version` in `.claude-plugin/plugin.json`. No SKILL.md carries
a `version:` or an `updated:` key — a version declared in seven skill files is a version that
drifts in six of them.

Two further places record it and must agree with the manifest:

1. The top row of `CHANGELOG.md`.
2. The `archive/v<x.y.z>/` folder name of the version it superseded.

---

## 3 · The release protocol

Run this on every change, however small. It takes about five minutes.

1. **Decide the bump** (§2) and set `version` in `.claude-plugin/plugin.json` — there and nowhere
   else. The date of the change is carried by the `CHANGELOG.md` entry written at step 5.
2. **Run the regression evals** — SKILL.md Block 8, "Regression evals". A version that fails the
   doc-vs-live diff does not ship; it ships as a patch that fixes the diff.
3. **Archive the outgoing version.** Copy the current `skill-docs/` tree to
   `archive/v<outgoing>/`. Do this *before* overwriting `skill-docs/`.
4. **Upload the new tree** to `skill-docs/`, replacing in place. SharePoint keeps its own file
   version history as a second safety net, but do not rely on it as the record — `archive/` is
   the record, because it preserves the tree, not just the file.
5. **Append to `CHANGELOG.md`** (§4).
6. **Write release notes** to `supporting-docs/<date>-release-notes-v<x.y.z>.md` for a major or
   minor bump. Patches need only the changelog line.
7. **Update the Confluence index** if a dashboard was added, renamed or re-slugged.
8. **Deliver the `.skill` package to the user** so they can install the new version. Uploading to
   SharePoint publishes the *documentation*; it does not update the running skill.

> **The two are separate.** A file in SharePoint is a document. A skill in the user's account is
> a running agent. Never report a SharePoint upload as "the skill is updated" — report it as
> "the docs are published; here's the package to install".

---

## 4 · CHANGELOG format

Newest first. One block per version. Keep entries specific enough to answer "why does this
dashboard's companion doc say something different from the current skill?"

```markdown
## v2.0.0 — 2026-08-11

**Type:** Major · **Model used:** Opus 5 · **Entry mode:** Audit + restructure

### Added
- Model gate: agent runs on Opus 5 or Sonnet 5 only, prompts on fresh invocation (Block 3).
- `${CLAUDE_PLUGIN_ROOT}/tenants/<name>/` — live state of record for that engagement's suite.

### Changed
- SKILL.md restructured into the eight-block agent architecture.

### Fixed
- `resolved_via_fallback` → `resolved_via_customer_id` (3 files).

### Open
- The open-item tracker, see `${CLAUDE_PLUGIN_ROOT}/tenants/<name>/open-items.md`.
```

Sections: **Added / Changed / Fixed / Removed / Open**. Omit empty ones.

---

## 5 · Creating the structure from scratch

For a new agent folder, from an authenticated SharePoint browser session:

```js
const base = '/personal/<your-site-path>';   // or '/sites/<team-site>' for a shared library
const d = await (await fetch(base + '/_api/contextinfo', {method:'POST',
  headers:{Accept:'application/json;odata=nometadata'}})).json();

const mk = p => fetch(base + "/_api/web/folders/addUsingPath(DecodedUrl=@u)?@u='"
  + encodeURIComponent(p) + "'", {method:'POST',
  headers:{Accept:'application/json;odata=nometadata','X-RequestDigest': d.FormDigestValue}});

const root = base + '/Documents/<agent-docs root>/<agent-name>';
for (const p of [root, root+'/skill-docs', root+'/skill-docs/references',
                 root+'/supporting-docs', root+'/presentations', root+'/archive']) await mk(p);
```

Uploading a file:

```js
await fetch(base + "/_api/web/GetFolderByServerRelativePath(DecodedUrl=@f)/Files"
  + "/AddUsingPath(DecodedUrl=@n,Overwrite=true)?@f='" + encodeURIComponent(folder)
  + "'&@n='" + encodeURIComponent(filename) + "'",
  {method:'POST', headers:{'X-RequestDigest': d.FormDigestValue}, body: contentString});
```

`addUsingPath` returns 200 on create and on an already-existing folder, so the loop is idempotent.
Get the digest once per session; it expires.

---

## 6 · Retention

Keep every archived version. These trees are small (~150 KB) and the cost of losing the version
that produced a disputed number is not.
