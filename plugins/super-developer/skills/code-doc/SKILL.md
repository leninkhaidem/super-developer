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

**Artifact catalog** (scout recommends based on codebase analysis):

| Document | Purpose | Condition |
|----------|---------|-----------|
| `docs/navigation.md` | Entry points, capability-to-file map, "how do I add X" guides | Codebase has >10 source files |
| `docs/patterns.md` | Naming conventions, code patterns, anti-hallucination index, inconsistencies | Always recommended |
| `docs/config.md` | Env vars, config files, feature flags with defaults and locations | `process.env`/config file usage detected |
| `docs/errors.md` | Error taxonomy, throw/catch mapping, unhandled gaps | Custom error classes or >5 distinct throw sites |
| `docs/flows.md` | Request lifecycle, state machines, event propagation | HTTP middleware, state enums, or event emitters detected |
| `docs/boundaries.md` | Layer rules, module contracts, import violations | Multi-directory architecture with >3 top-level modules |
| `docs/inventory.md` | Utility registry — "before you write it, we have it" | `utils/`, `lib/`, `helpers/`, or `shared/` directories |
| `docs/security.md` | Route auth matrix, input validation audit, concerns | Auth middleware, route definitions, or secrets handling |

**Scout recommendation process:**

1. After detection (Step 1), evaluate each catalog artifact's condition against the codebase
2. Recommend artifacts whose conditions are met, with a one-line justification per selection
3. Optionally propose up to **3 custom artifacts** not in the catalog — each requires a name,
   purpose, and justification explaining why this codebase warrants it
4. Present the full doc plan (core documents + recommended artifacts) to the user for confirmation

Example scout output:

```
Core: README.md, architecture-guide.md, developer-guide.md, codebase-context.md

Recommended artifacts:
  ✅ navigation.md — 47 source files across 8 directories
  ✅ patterns.md — always recommended
  ✅ config.md — 12 process.env references found
  ✅ flows.md — Express middleware chain + 3 state enums detected
  ⬚ errors.md — only 2 throw sites, insufficient for standalone doc
  ⬚ boundaries.md — flat directory structure
  ⬚ inventory.md — no utils/lib/helpers directories
  ⬚ security.md — no auth middleware detected

Custom: (none proposed)
```

Wait for user confirmation before proceeding.

---

### Step 4 — Analyze

**Always delegate analysis to sub-agents.** Do not attempt to analyze the codebase yourself.

1. Create analysis directory: `mkdir -p {project}/.codedoc`
2. Run **native extractors** first (if available): TypeDoc, Sphinx, godoc, javadoc, rustdoc, DocFX.
   Save output to `.codedoc/native-extractors/`. This provides ground-truth for signatures and types.
3. **Spawn analyst agents** in parallel based on the confirmed doc plan:

| Agent | Condition | Output File |
|-------|-----------|-------------|
| Architecture Analyst | Always | `.codedoc/architecture-analysis.md` |
| Catalog Artifact Analyst (×N) | One per selected artifact from Step 3 | `.codedoc/{artifact-name}-analysis.md` |
| Custom Artifact Analyst (×M) | One per approved custom artifact | `.codedoc/{custom-name}-analysis.md` |

For example, if Step 3 selected `navigation`, `patterns`, `config`, and `flows`, spawn 5 analysts:
Architecture + Navigation + Patterns + Config + Flows.

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

Core writers always spawn (README, Architecture, Developer Guide, Codebase Context).
Optional writers spawn based on the doc plan from Step 3.

All generated docs **must** include frontmatter (the Accuracy reviewer will flag missing fields as 🔴 BLOCKER):

```yaml
---
codedoc_version: 1
generated: "<ISO 8601 timestamp>"
project_hash: "<short git hash from `git rev-parse --short HEAD`>"
---
```

**Update mode** (re-generation):

IF existing docs detected, READ `references/update-merge.md` for archive, human block preservation, and augmentation logic.

| Mode | Condition | Behavior |
|------|-----------|----------|
| **Fresh** | No existing docs | Generate all |
| **Regenerate** | Existing code-doc output (`codedoc_version` frontmatter) | Archive to `.docs-archive/v{N}/`, regenerate, merge `<!-- human -->` blocks |
| **Augment** | Existing human docs (no frontmatter, high quality) | Preserve entirely, add only to `docs/codedoc/` subdirectory |

---

### Step 8 — Review & Commit

Spawn 3 reviewer agents (`task(agent_type='explore')`) in parallel.

| Reviewer | Focus |
|----------|-------|
| **Accuracy** | Cross-reference against native extractor output, verify code paths exist, confirm every generated doc has valid frontmatter (`codedoc_version`, `generated`, `project_hash`) |
| **Completeness** | All planned sections populated, no TODO placeholders |
| **Clarity** | Writing quality, consistent terminology, actionable instructions |

Severity: 🔴 BLOCKER (must fix) · 🟠 WARNING (should fix) · 🟡 INFO (optional).
Fix all 🔴s. User decides on 🟠s. Maximum 2 fix iterations.

If blockers remain after 2 iterations, append a `## Known Issues` section to README listing
unresolved items, then proceed.

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
