#!/usr/bin/env python3
"""Validate the superset-bi-agent plugin package. No third-party dependencies.

Run from anywhere:  python3 scripts/validate_skill.py

Ported from a sibling plugin's validator. The generic machinery is unchanged.
Three checks are specific to this package and are the reason it exists:

  * tenant purity   - no engagement name may appear anywhere under skills/
  * packaging limits - the description ceilings that break install when exceeded
  * agent frontmatter - name must equal the file stem, including under agents/review/

The inherited dash ban is deliberately NOT ported: this package's prose uses the
middle dot and the hyphen as house style throughout.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FRONTMATTER_KEYS = {"name", "description", "metadata", "allowed-tools", "license"}

MANIFEST = ROOT / ".claude-plugin" / "plugin.json"

# Engagement names. Tenant state lives in tenants/, never in a skill.
# Derived from the tenants/ directory rather than hardcoded, so onboarding a new engagement
# extends the purity check automatically -- and so this file never becomes a list of client
# names in its own right, which is exactly the leak it exists to prevent.
def _tenant_names() -> tuple[str, ...]:
    tenants_dir = ROOT / "tenants"
    if not tenants_dir.is_dir():
        return ()
    return tuple(
        sorted(
            d.name.lower()
            for d in tenants_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_")
        )
    )


TENANT_NAMES = _tenant_names()
# Matched with word boundaries so "several" and "average" do not trip it.
TENANT_WORD_RE = (
    re.compile(r"\b(" + "|".join(re.escape(n) for n in TENANT_NAMES) + r")\b", re.IGNORECASE)
    if TENANT_NAMES
    else None
)

# Packaging ceilings. Exceeding either breaks install.
MAX_SKILL_DESCRIPTION = 1024
MAX_PLUGIN_DESCRIPTION = 500

ROUTER = "superset-bi-agent"

SKILLS = {
    "superset-bi-agent": {
        "required": [
            "references/guardrails.md",
            "references/prequalification.md",
            "references/memory-and-registry.md",
            "references/operating-modes.md",
            "references/product-artefacts.md",
            "references/versioning-and-sharepoint.md",
            "references/observability.md",
            "references/context-engineering.md",
            "references/fine-tuning.md",
            "references/portability.md",
            "references/acquisition-source.md",
            "templates/definition-registry.md",
            "templates/tenant-profile.md",
            "templates/context-capsule.md",
            "templates/companion-doc.md",
            "examples/storyboard.md",
        ],
        "markers": [
            "model gate",
            "L1",
            "L4",
            "Entry mode",
            "G12",
            "Definition Registry",
            "Phase 0",
            "superset-build",
            "concentration-analysis",
        ],
        "anti_markers": [
            # The gate checklists belong to qc-protocol.md. Restating them here is
            # the duplication that had already drifted before the v3.0.0 split.
            "Gate 0b — Population sanity",
            "position_json",
        ],
    },
    "superset-build": {
        "required": [
            "references/superset-api.md",
            "references/dashboard-design.md",
            "references/modelling.md",
            "references/query-optimisation.md",
            "references/schema-discovery.md",
            "references/warehouse-gotchas.md",
            "references/reference-dashboards.md",
            "references/qc-protocol.md",
            "references/evals.md",
            "references/eval-harness.md",
        ],
        "markers": [
            "Source sanity",
            "Narrative check",
            "query_context",
            "Golden",
            "Adversarial",
            "semantic dataset",
            ROUTER,
        ],
        "anti_markers": [
            "twelve guardrails",
        ],
    },
    "onboarding-funnel": {
        "required": [],
        "markers": ["KYC", "Questions to ask", "Triangulation", "concentration-analysis", ROUTER],
        "anti_markers": ["mandate", "RFM"],
    },
    "app-signup": {
        "required": [],
        "markers": ["activation", "Questions to ask", "Triangulation", "concentration-analysis", ROUTER],
        "anti_markers": ["mandate", "RFM"],
    },
    "transactions-spends": {
        "required": [],
        "markers": ["decline", "RFM", "Questions to ask", "concentration-analysis", ROUTER],
        "anti_markers": ["mandate deletion"],
    },
    "repayments": {
        "required": [],
        "markers": ["mandate", "Questions to ask", "Triangulation", "concentration-analysis", ROUTER],
        "anti_markers": ["RFM"],
    },
    "concentration-analysis": {
        "required": [],
        "markers": ["unique", "Attempts per", "Questions to ask", "Triangulation", ROUTER],
        "anti_markers": ["mandate deletion"],
    },
}

REFERENCE_MARKERS = {
    "skills/superset-bi-agent/references/guardrails.md": [
        "G1", "G8", "G11", "G12", "Anti-patterns",
    ],
    "skills/superset-bi-agent/references/observability.md": [
        "freshness", "drift", "Schema drift", "Doc-vs-live",
    ],
    "skills/superset-bi-agent/references/context-engineering.md": [
        "budget", "evict", "capsule",
    ],
    "skills/superset-bi-agent/references/fine-tuning.md": [
        "not model-weight", "ratchet", "guardrail",
    ],
    "skills/superset-bi-agent/references/portability.md": [
        "SKILL.md", "CLAUDE_PLUGIN_ROOT", "evals",
    ],
    "skills/superset-build/references/qc-protocol.md": [
        "Gate 0", "Gate 3", "Gate 6",
    ],
}

COMMANDS = (
    "new-engagement.md",
    "funnel.md",
    "build-dashboard.md",
    "qc.md",
    "concentration.md",
    "audit-suite.md",
)

AGENTS = (
    "schema-profiler.md",
    "dashboard-builder.md",
    "qc-triangulator.md",
    "eval-runner.md",
    "builders/onboarding-builder.md",
    "builders/signup-builder.md",
    "builders/transactions-builder.md",
    "builders/repayments-builder.md",
    "review/number-integrity.md",
    "review/definition-drift.md",
)

ROOT_FILES = ("README.md", "CHANGELOG.md", "LICENSE", ".gitignore")

TENANT_FILES = ("profile.md", "inventory.md", "journeys.md", "open-items.md", "revisions.md")

PLUGIN_ROOT_TOKEN = "${CLAUDE_PLUGIN_ROOT}"


def parse_frontmatter(path: Path, errors: list[str]) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    rel = path.relative_to(ROOT)
    if not text.startswith("---\n"):
        errors.append(f"{rel}: must start with YAML frontmatter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        errors.append(f"{rel}: frontmatter must close with ---")
        return {}, text

    values: dict[str, str] = {}
    for number, line in enumerate(text[4:end].splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#") or line.startswith((" ", "\t")):
            continue
        if ":" not in line:
            errors.append(f"{rel}: frontmatter line {number} is not a key/value pair")
            continue
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if value[:1] in {'"', "'"} and value.endswith(value[:1]):
            value = value[1:-1]
        values[key] = value
    return values, text[end + len("\n---\n"):]


def check_manifest(errors: list[str]) -> dict:
    if not MANIFEST.is_file():
        errors.append("missing .claude-plugin/plugin.json")
        return {}
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"plugin.json is not valid JSON: {exc}")
        return {}
    for key in ("name", "version", "description", "author"):
        if not data.get(key):
            errors.append(f"plugin.json is missing {key}")
    if data.get("name") != ROOT.name:
        errors.append(f"plugin.json name must match the folder name: {ROOT.name}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(data.get("version", ""))):
        errors.append("plugin.json version must be semver, for example 3.0.0")
    description = data.get("description", "")
    if len(description) > MAX_PLUGIN_DESCRIPTION:
        errors.append(
            f"plugin.json description is {len(description)} characters, "
            f"over the {MAX_PLUGIN_DESCRIPTION} ceiling"
        )
    return data


def resolve_link(base: Path, target: str) -> Path | None:
    """Resolve a markdown link target. ${CLAUDE_PLUGIN_ROOT} resolves against ROOT."""
    if target.startswith(PLUGIN_ROOT_TOKEN):
        return (ROOT / target[len(PLUGIN_ROOT_TOKEN):].lstrip("/")).resolve()
    return (base / target).resolve()


def check_skill(slug: str, spec: dict, author: str, errors: list[str]) -> None:
    base = ROOT / "skills" / slug
    skill_md = base / "SKILL.md"
    if not skill_md.is_file():
        errors.append(f"missing skills/{slug}/SKILL.md")
        return

    frontmatter, body = parse_frontmatter(skill_md, errors)
    for key in frontmatter:
        if key not in FRONTMATTER_KEYS:
            errors.append(f"skills/{slug}: unsupported core frontmatter key: {key}")

    name = frontmatter.get("name", "")
    if name != slug:
        errors.append(f"skills/{slug}: frontmatter name must match the folder name")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        errors.append(f"skills/{slug}: name must be lowercase with single hyphens")

    description = frontmatter.get("description", "").strip()
    if not description:
        errors.append(f"skills/{slug}: description must be non-empty")
    if len(description) > MAX_SKILL_DESCRIPTION:
        errors.append(
            f"skills/{slug}: description is {len(description)} characters, "
            f"over the {MAX_SKILL_DESCRIPTION} ceiling"
        )
    if "Do not use" not in description and "do not use" not in description:
        errors.append(f"skills/{slug}: description should state when NOT to trigger")
    if "disable-model-invocation" in frontmatter:
        errors.append(f"skills/{slug}: no provider-specific invocation controls in portable frontmatter")

    head = skill_md.read_text(encoding="utf-8").split("\n---\n", 1)[0]
    if f"author: {author}" not in head:
        errors.append(f"skills/{slug}: frontmatter metadata must name the author: {author}")
    if re.search(r"^\s*version:", head, re.MULTILINE):
        errors.append(f"skills/{slug}: version must live only in plugin.json, not in skill frontmatter")

    line_count = len(body.splitlines())
    if line_count > 500:
        errors.append(f"skills/{slug}: SKILL.md body is {line_count} lines, over the 500-line target")

    for marker in spec["markers"]:
        if marker not in body:
            errors.append(f"skills/{slug}: SKILL.md is missing behaviour marker: {marker}")
    for marker in spec["anti_markers"]:
        if marker in body:
            errors.append(f"skills/{slug}: SKILL.md holds content that belongs elsewhere: {marker}")

    for relative in spec["required"]:
        if not (base / relative).is_file():
            errors.append(f"missing skills/{slug}/{relative}")


def check_links(errors: list[str]) -> None:
    """Every link must resolve inside the plugin. Crossing a skill needs the root token."""
    for path in sorted(ROOT.glob("skills/**/*.md")) + sorted(ROOT.glob("tenants/**/*.md")):
        base = path.parent
        rel = path.relative_to(ROOT)
        skill_root = None
        parts = rel.parts
        if parts[0] == "skills" and len(parts) > 1:
            skill_root = (ROOT / "skills" / parts[1]).resolve()
        text = path.read_text(encoding="utf-8")
        # Markdown links AND backtick-quoted paths. The house style points across
        # skills with backticks, so a link-only check misses most cross-references.
        targets = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
        # Backticked strings that are actually pointers: a ${CLAUDE_PLUGIN_ROOT}
        # path, or one relative to this file. A bare `journeys.md` in prose names
        # a file rather than pointing at one, and a package-root-relative path in
        # a layout table is illustrative, so neither is resolved here.
        POINTER_PREFIXES = ("references/", "templates/", "examples/", "../", "./")
        targets += [
            m for m in re.findall(r"`([^`\n]+\.md)`", text)
            if m.startswith(PLUGIN_ROOT_TOKEN) or m.startswith(POINTER_PREFIXES)
        ]
        for target in targets:
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            if "<" in target or ">" in target:
                continue  # a deliberate placeholder such as tenants/<name>/
            resolved = resolve_link(base, target)
            if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
                errors.append(f"{rel}: link escapes the plugin root: {target}")
                continue
            if not resolved.is_file():
                errors.append(f"{rel}: link target does not exist: {target}")
                continue
            if (
                skill_root is not None
                and not target.startswith(PLUGIN_ROOT_TOKEN)
                and skill_root not in resolved.parents
            ):
                errors.append(
                    f"{rel}: cross-skill link must use {PLUGIN_ROOT_TOKEN}: {target}"
                )


def check_tenant_purity(errors: list[str]) -> None:
    """The whole point of the v3.0.0 split: skills carry no engagement state."""
    if TENANT_WORD_RE is None:
        return
    for path in sorted(ROOT.glob("skills/**/*.md")):
        rel = path.relative_to(ROOT)
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            match = TENANT_WORD_RE.search(line)
            if match:
                errors.append(
                    f"{rel}:{number}: engagement name '{match.group(0)}' in a skill file. "
                    f"Tenant state belongs in tenants/"
                )


def check_tenants(errors: list[str]) -> list[str]:
    base = ROOT / "tenants"
    if not base.is_dir():
        errors.append("missing tenants/")
        return []
    if not (base / "README.md").is_file():
        errors.append("missing tenants/README.md")
    if not (base / "_template" / "profile.md").is_file():
        errors.append("missing tenants/_template/profile.md")
    names = sorted(p.name for p in base.iterdir() if p.is_dir() and not p.name.startswith("_"))
    for name in names:
        for filename in TENANT_FILES:
            if not (base / name / filename).is_file():
                errors.append(f"tenants/{name}: missing {filename}")
    return names


def check_references(errors: list[str]) -> None:
    for relative, markers in REFERENCE_MARKERS.items():
        path = ROOT / relative
        if not path.is_file():
            continue  # the per-skill required-file check already reported it
        text = path.read_text(encoding="utf-8")
        for marker in markers:
            if marker not in text:
                errors.append(f"{relative} is missing marker: {marker}")


def check_commands(errors: list[str]) -> None:
    for filename in COMMANDS:
        path = ROOT / "commands" / filename
        if not path.is_file():
            errors.append(f"missing commands/{filename}")
            continue
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            errors.append(f"commands/{filename}: must start with frontmatter")
        head = text.split("\n---\n", 1)[0]
        if "description:" not in head:
            errors.append(f"commands/{filename}: frontmatter needs a description")
        if "argument-hint:" not in head:
            errors.append(f"commands/{filename}: frontmatter needs an argument-hint")
        if "$ARGUMENTS" not in text:
            errors.append(f"commands/{filename}: must pass $ARGUMENTS through to the skill")


def check_agents(errors: list[str]) -> None:
    for relative in AGENTS:
        path = ROOT / "agents" / relative
        if not path.is_file():
            errors.append(f"missing agents/{relative}")
            continue
        frontmatter, body = parse_frontmatter(path, errors)
        stem = Path(relative).stem
        if frontmatter.get("name") != stem:
            errors.append(f"agents/{relative}: frontmatter name must equal the file stem: {stem}")
        if not frontmatter.get("description", "").strip():
            errors.append(f"agents/{relative}: needs a description")
        if not body.strip():
            errors.append(f"agents/{relative}: body is empty")

    found = sorted(
        str(p.relative_to(ROOT / "agents")) for p in (ROOT / "agents").rglob("*.md")
    )
    for extra in set(found) - set(AGENTS):
        errors.append(f"agents/{extra}: not declared in the validator's AGENTS list")


def check_evals(errors: list[str]) -> tuple[int, list[str]]:
    base = ROOT / "evals"
    if not base.is_dir():
        errors.append("missing evals/")
        return 0, []
    names = sorted(
        p.name for p in base.iterdir()
        if p.is_dir() and p.name not in {"results", "mocks", "fixtures"}
    )
    if not names:
        errors.append("evals/ holds no cases")
        return 0, []
    for name in names:
        case = base / name
        if not (case / "prompt.md").is_file():
            errors.append(f"evals/{name}: missing prompt.md")
        elif not (case / "prompt.md").read_text(encoding="utf-8").strip():
            errors.append(f"evals/{name}: prompt.md is empty")
        graders = case / "graders"
        if not graders.is_dir():
            errors.append(f"evals/{name}: missing graders/")
            continue
        for grader in ("criteria.md", "skill-fired.md"):
            path = graders / grader
            if not path.is_file():
                errors.append(f"evals/{name}: missing graders/{grader}")
            elif "- [ ]" not in path.read_text(encoding="utf-8"):
                errors.append(f"evals/{name}: graders/{grader} has no checkable items")
        case_yaml = case / "case.yaml"
        if case_yaml.is_file():
            text = case_yaml.read_text(encoding="utf-8")
            if not text.lstrip().startswith("context:"):
                errors.append(f"evals/{name}: case.yaml may only carry context.*")
            target = re.search(r"target_skill:\s*(\S+)", text)
            if target and target.group(1) not in SKILLS:
                errors.append(f"evals/{name}: target_skill is not a skill in this package")
    return len(names), names


def check_root_files(errors: list[str]) -> None:
    for filename in ROOT_FILES:
        if not (ROOT / filename).is_file():
            errors.append(f"missing {filename}")
    if not (ROOT / "hosts" / "openai.yaml").is_file():
        errors.append("missing hosts/openai.yaml")


def main() -> int:
    errors: list[str] = []
    manifest = check_manifest(errors)
    author = (manifest.get("author") or {}).get("name", "")

    for slug, spec in SKILLS.items():
        check_skill(slug, spec, author, errors)
    check_references(errors)
    check_links(errors)
    check_tenant_purity(errors)
    tenants = check_tenants(errors)
    check_commands(errors)
    check_agents(errors)
    check_root_files(errors)
    case_count, case_names = check_evals(errors)

    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"\n{len(errors)} problem(s) found.")
        return 1

    version = manifest.get("version", "?")
    print(f"PASS: {ROOT.name} v{version} is structurally valid")
    print(f"PASS: {len(SKILLS)} skills, {len(AGENTS)} agents, {len(COMMANDS)} commands")
    print("PASS: every link resolves, cross-skill links use ${CLAUDE_PLUGIN_ROOT}")
    print("PASS: no engagement name appears in any skill file")
    print(f"PASS: {len(tenants)} tenant(s) with the full five-file set: {', '.join(tenants)}")
    print("PASS: description ceilings respected (1024 per skill, 500 for the plugin)")
    print(f"PASS: version and author declared once, author is {author}")
    print(f"PASS: {case_count} eval cases with graders")
    for name in case_names:
        print(f"  - {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
