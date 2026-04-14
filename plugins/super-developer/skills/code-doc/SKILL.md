---
name: code-doc
description: >
  Generates comprehensive documentation for any codebase via hybrid analysis (native extractors +
  LLM agents). Triggers on phrases like "document this codebase", "generate documentation",
  "create docs for this repo", "write documentation", "document the code", "generate codebase docs",
  "create architecture docs", "write a developer guide", "document this project".
---

# Code-Doc — Adaptive Codebase Documentation

A hybrid documentation generator that combines language-native extractors for API-level accuracy
with LLM agents for synthesis, architecture narratives, and developer guides. Zero-config default —
just point at a repo.

---

## Delegation Model

**Scout orchestrates. Analysts write to files. Doc Writers fan out.**

- **You are the Scout** — handle detection, planning, synthesis, and coordination
- **Analyst agents** (`task(agent_type='explore')`) read code and write full analysis to
  `{project}/.codedoc/` files. They return only compact summaries (max 15 lines) to you.
  You hold summaries, not full analysis — this prevents context overflow.
- **Doc Writer agents** (`task(agent_type='general-purpose')`) each read assigned `.codedoc/`
  files and produce one output document
- **Reviewer agents** (`task(agent_type='explore')`) validate generated docs
- All agents are stateless — provide complete context in each spawn

The `.codedoc/` directory is transient — created at analysis start, consumed by doc writers,
cleaned up after generation. Add `.codedoc/` to `.gitignore`. Never commit it.

### Analyst Output Protocol

Every analyst agent must:

1. Write full analysis to their assigned `.codedoc/{name}-analysis.md` file
2. Return ONLY a compact summary to you (max 15 lines):
   - File written path
   - Key stats (counts, patterns found)
   - Notable findings or anomalies

---

## Workflow

### Step 1 — Scout & Detect

Accept the repository path (defaults to cwd). Scan the codebase:

1. Detect project type, languages, frameworks, and libraries
2. Identify architecture patterns, entry points, and module boundaries
3. Detect monorepo structure if present
4. `--with-build` flag (optional) — enables build-assisted analysis for resolved types

**Monorepo handling:** If workspace patterns detected (`pnpm-workspace.yaml`, `lerna.json`,
`packages/*/package.json`, etc.), list sub-projects and let user choose **unified** (single doc set)
or **per-project** (separate docs per package). Per-project repeats Steps 2–8 for each.

---

### Step 2 — Assess Existing Docs

Inventory existing documentation and classify:

| Level | Action |
|-------|--------|
| **No docs** | Fresh generation |
| **Partial** | Fill gaps, preserve existing |
| **Comprehensive** | Augment-only — propose additions, never overwrite. Preserve `<!-- human -->` blocks entirely. |

---

### Step 3 — Propose Doc Plan

Present the plan to the user for confirmation before proceeding.

**Core documents** (always generated):

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview, quick start |
| `docs/architecture-guide.md` | System design, component relationships |
| `docs/developer-guide.md` | Setup, development workflow |
| `docs/codebase-context.md` | LLM-optimized codebase summary |

**Optional documents** (proposed based on detection):

| Document | Condition |
|----------|-----------|
| `docs/api-reference.md` | Routes/endpoints detected |
| `docs/data-model.md` | ORM/schema/database detected |
| `docs/component-guide.md` | Frontend/UI components detected |
| `docs/infrastructure.md` | CI/CD, Docker, IaC detected |

Wait for user confirmation before proceeding.

---

### Step 4 — Analyze

**Always delegate analysis to sub-agents.** Do not attempt to analyze the codebase yourself.

1. Create analysis directory: `mkdir -p {project}/.codedoc`
2. Run **native extractors** first (if available): TypeDoc, Sphinx, godoc, javadoc, rustdoc, DocFX.
   Save output to `.codedoc/native-extractors/`. This provides ground-truth for signatures and types.
3. **Spawn analyst agents** in parallel based on what you detected:

| Agent | Condition | Output File |
|-------|-----------|-------------|
| Architecture Analyst | Always | `.codedoc/architecture-analysis.md` |
| API Surface Analyst | Routes/endpoints detected | `.codedoc/api-analysis.md` |
| Data Model Analyst | ORM/schema detected | `.codedoc/data-model-analysis.md` |
| Component Analyst | Frontend detected | `.codedoc/component-analysis.md` |
| Infrastructure Analyst | CI/Docker/IaC detected | `.codedoc/infrastructure-analysis.md` |

Each analyst receives: project context, framework info, file scope, native extractor output path,
and their assigned output file. They write full analysis and return a compact summary.

---

### Step 5 — Synthesize

Read `.codedoc/` files selectively (not all at once) and build a unified model:

1. Unify data models — merge native extractor types with analyst findings
2. Correlate cross-cutting concerns — trace flows across components
3. Detect inconsistencies between analyst outputs
4. Identify documentation-worthy flows and key paths
5. Write synthesis to `{project}/.codedoc/synthesis.md`

---

### Step 6 — User Checkpoint

Present synthesis summary: architecture pattern, component count, data flows, API endpoints,
key findings, and any inconsistencies. User confirms, aborts, or requests re-analysis of a
specific area.

---

### Step 7 — Generate

Fan out documentation generation to parallel doc writer agents.

Each writer is spawned via `task(agent_type='general-purpose')` with:
- Assigned output file path
- List of `.codedoc/` analysis files to read
- READ `references/generation.md` for document templates, Mermaid patterns, and update/merge logic

Core writers always spawn (README, Architecture, Developer Guide, Codebase Context).
Optional writers spawn based on the doc plan from Step 3.

All generated docs include frontmatter:

```yaml
---
codedoc_version: 1
generated: "<ISO 8601 timestamp>"
project_hash: "<short git hash>"
---
```

**Update mode** (re-generation):

| Mode | Condition | Behavior |
|------|-----------|----------|
| **Fresh** | No existing docs | Generate all |
| **Regenerate** | Existing code-doc output (`codedoc_version` frontmatter) | Archive to `.docs-archive/<timestamp>/`, regenerate, merge `<!-- human -->` blocks |
| **Augment** | Existing human docs (no frontmatter, high quality) | Preserve entirely, add only user-approved additions |

---

### Step 8 — Review & Commit

Spawn 3 reviewer agents (`task(agent_type='explore')`) in parallel.

READ `references/review.md` for reviewer checklists and severity taxonomy.

| Reviewer | Focus |
|----------|-------|
| **Accuracy** | Cross-reference against native extractor output, verify code paths exist |
| **Completeness** | All planned sections populated, no TODO placeholders |
| **Clarity** | Writing quality, consistent terminology, actionable instructions |

Severity: 🔴 BLOCKER (must fix) · 🟠 WARNING (should fix) · 🟡 INFO (optional).
Fix all 🔴s. User decides on 🟠s. Maximum 2 fix iterations.

After review passes:

1. Stage and commit: `docs: generate codebase documentation via code-doc`
2. Clean up: `rm -rf {project}/.codedoc`
3. Report summary to user

---

## Sub-Agent Summary

| Role | Agent Type | Model |
|------|-----------|-------|
| Analyst | `explore` | Haiku |
| Doc Writer | `general-purpose` | Sonnet |
| Reviewer | `explore` | Sonnet |

---

_Designed for multi-agent orchestration. Requires: `git`, native extractors per language (optional)._
