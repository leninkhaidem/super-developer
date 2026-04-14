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
with LLM agents for synthesis, architecture narratives, and developer guides. Produces comprehensive
documentation for any codebase — zero-config default, just point at a repo.

---

## Delegation Model

**Scout orchestrates, Analysts write to files, Doc Writers fan out.**

- The **Scout** (you, the orchestrator) handles detection, sizing, planning, and coordination
- **Analyst agents** are spawned via `task(agent_type='explore')` to read code and write full analysis to `{project}/.codedoc/` files — they return only compact summaries (max 15 lines) to the orchestrator. The orchestrator holds summaries, not full analysis — this prevents context overflow on large codebases.
- **Doc Writer agents** are spawned via `task(agent_type='general-purpose')` in parallel — each reads assigned `.codedoc/` files and produces one output document
- **Reviewer agents** are spawned via `task(agent_type='explore')` to validate generated docs
- All agents are stateless — provide complete context in each spawn

The `.codedoc/` directory is transient — created at analysis start, consumed by doc writers, cleaned up after generation. Never commit `.codedoc/` files.

---

## Step 1 — Accept & Scout

Accept the repository path and perform initial reconnaissance.

### Inputs

- Repository path (required) — defaults to cwd if not specified
- `--with-build` flag (optional) — enables build-assisted analysis for resolved types

### Scout Tasks

1. **Detect project type** using heuristics (not a rigid matrix)
2. **Detect frameworks and libraries** via package files and import patterns
3. **Size the codebase** for tiered agent strategy
4. **Identify entry points** and module boundaries
5. **Detect monorepo structure** if present

READ `references/analysis.md` section 1 for detection heuristics, framework patterns, and
sizing thresholds.

### Codebase Sizing

| Tier | File Count | Agent Strategy |
|------|-----------|----------------|
| Small | < 200 files | Single-agent mode — scout performs analysis directly |
| Medium | 200–1000 files | Scout + 2–3 concern-based analysts |
| Large | > 1000 files | Full multi-agent pipeline with all relevant analysts |

### Monorepo Detection

If workspace root patterns detected (e.g., `pnpm-workspace.yaml`, `lerna.json`, `packages/*/package.json`):

1. List detected sub-projects to user
2. User chooses: **unified docs** (single doc set for entire repo) or **per-project docs** (separate doc set per sub-project)
3. If per-project: repeat Steps 2–8 for each sub-project

---

## Step 2 — Assess Existing Documentation

Inventory existing documentation before generating anything.

### Documentation Inventory

Scan for documentation files:
- `README.md`, `docs/`, `doc/`, `documentation/`
- `ARCHITECTURE.md`, `CONTRIBUTING.md`, `CHANGELOG.md`
- API documentation (JSDoc output, Sphinx `_build/`, etc.)
- Inline code comments density

### Classification

| Level | Criteria | Action |
|-------|----------|--------|
| **No docs** | No README or minimal stub only | Fresh generation |
| **Partial** | README exists, some docs missing | Fill gaps, preserve existing |
| **Comprehensive** | Full doc set, high quality | Augment-only mode — propose additions, never overwrite |

### Augment-Only Mode

When existing docs are comprehensive:
- Do NOT regenerate existing well-written content
- Propose specific additions only (e.g., "add data flow diagram to architecture doc")
- User confirms each proposed addition
- Preserve `<!-- human -->` blocks and human-authored sections entirely

---

## Step 3 — Propose Doc Plan

Present the documentation plan to the user for confirmation.

### Core Documents (Always Generated)

| Document | Purpose | Target Lines |
|----------|---------|--------------|
| `README.md` | Project overview, quick start, badges | 100–200 |
| `docs/architecture-guide.md` | System architecture, component relationships | 200–400 |
| `docs/developer-guide.md` | Setup, development workflow, conventions | 150–300 |
| `docs/codebase-context.md` | LLM-optimized codebase summary | 300–500 |

### Optional Documents (Proposed Based on Detection)

| Document | Spawn Condition | Target Lines |
|----------|-----------------|--------------|
| `docs/api-reference.md` | Route definitions detected | 200–500 |
| `docs/data-model.md` | ORM/schema/database detected | 150–300 |
| `docs/component-guide.md` | Frontend/UI components detected | 200–400 |
| `docs/infrastructure.md` | CI/CD, Docker, IaC detected | 100–200 |

### Plan Presentation

```
📋 Documentation Plan for <project-name>

Detected: <project type>, <frameworks>, <architecture patterns>
Codebase: <file count> files (<size tier>)
Existing docs: <classification level>

Core Documents (always generated):
  ✓ README.md
  ✓ docs/architecture-guide.md
  ✓ docs/developer-guide.md
  ✓ docs/codebase-context.md

Optional Documents (based on detection):
  ✓ docs/api-reference.md — routes detected in src/routes/
  ✓ docs/data-model.md — Prisma schema detected

Proceed? [y/n]
```

Wait for user confirmation before proceeding to analysis.

---

## Step 4 — Analyze

Run analysis using native extractors first, then LLM analysts. Analysts write full output to `.codedoc/` files.

### Setup Analysis Directory

```bash
mkdir -p {project}/.codedoc
```

### Native Extractors (Run First)

Execute language-native documentation extractors for API-level accuracy:

| Language | Extractor | Output |
|----------|-----------|--------|
| TypeScript/JS | TypeDoc, JSDoc | JSON/HTML API docs |
| Python | Sphinx autodoc, pydoc | RST/HTML |
| Go | godoc | Plain text/HTML |
| Java | Javadoc | HTML |
| Rust | rustdoc | HTML/JSON |
| C# | DocFX, XML docs | XML/HTML |

Native extractor output is saved to `{project}/.codedoc/native-extractors/` and fed to analysts as ground truth for function signatures, types, and module structure.

### Analyst Agents (Spawned by Tier)

READ `references/analysis.md` sections 2–3 for complete analyst prompt templates and
language-specific patterns.

| Agent | Spawn Condition | Focus Area | Output File |
|-------|-----------------|------------|-------------|
| **Architecture Analyst** | Always | System structure, component relationships, data flow | `.codedoc/architecture-analysis.md` |
| **API Surface Analyst** | Routes/endpoints detected | REST/GraphQL endpoints, request/response schemas | `.codedoc/api-analysis.md` |
| **Data Model Analyst** | ORM/schema detected | Database schema, relationships, migrations | `.codedoc/data-model-analysis.md` |
| **Component Analyst** | Frontend detected | UI components, props, state management | `.codedoc/component-analysis.md` |
| **Infrastructure Analyst** | CI/Docker/IaC detected | Build pipeline, deployment, configuration | `.codedoc/infrastructure-analysis.md` |

### Tiered Agent Strategy

| Tier | Approach |
|------|----------|
| **Small** (< 200 files) | Scout performs analysis directly — writes results to `.codedoc/scout-analysis.md` |
| **Medium** (200–1000 files) | Scout + 2–3 most relevant analysts based on detection |
| **Large** (> 1000 files) | Full pipeline: scout + all relevant analysts in parallel |

### Agent Spawning

All analysts spawned via `task(agent_type='explore')` with:
- Complete context (project type, framework, file scope)
- Native extractor output path as ground truth reference
- Assigned output file path (agent writes full analysis to this file)
- Structured Markdown output format
- Cross-reference requirements

Each analyst prompt includes:
```
Write your FULL analysis output to: {output_file}
Format the file with a YAML frontmatter (project, analyst, timestamp) followed by your structured analysis.

Return to the orchestrator ONLY a compact summary (max 15 lines):
- File written: {output_file}
- Key stats (counts, patterns found)
- Notable findings or anomalies
```

Collect agent **summaries** (NOT full outputs). Full analysis persists in `.codedoc/` files.

---

## Step 5 — Synthesize

Merge analyst outputs from `.codedoc/` files and native extractor data into a unified model.

READ `references/analysis.md` section 4 for synthesis protocol.

### Synthesis Tasks

1. **Read `.codedoc/` files selectively** — load only the sections needed for each synthesis step, not all files simultaneously
2. **Unify data models** — merge native extractor types with analyst findings from `.codedoc/` files
3. **Correlate cross-cutting concerns** — trace flows across components
4. **Detect inconsistencies** — flag contradictions between analyst outputs
5. **Identify documentation-worthy flows** — user journeys, critical paths
6. **Write synthesis output** to `{project}/.codedoc/synthesis.md`

### Unified Model Structure

```markdown
## Synthesis Summary

### Architecture Overview
<high-level system description>

### Key Components
| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| ... | ... | ... |

### Data Flows
1. <flow name>: <source> → <processing> → <destination>

### API Surface
<summary of endpoints/interfaces>

### Inconsistencies Detected
- <any contradictions between analyst outputs>
```

---

## Step 6 — User Checkpoint

Present synthesis summary to user before generation.

### Checkpoint Format

```
📊 Analysis Complete — Synthesis Summary

Architecture: <pattern> (<confidence>)
Components: <count> identified
Data Flows: <count> documented
API Endpoints: <count> mapped

Key Findings:
• <finding 1>
• <finding 2>
• <finding 3>

Inconsistencies: <count> (will be flagged in docs)

Ready to generate documentation?
[y] Proceed  [n] Abort  [r] Re-analyze specific area
```

### Checkpoint Actions

| Input | Action |
|-------|--------|
| `y` | Proceed to generation |
| `n` | Abort pipeline |
| `r <area>` | Re-run analysis for specific area (e.g., `r api` re-runs API analyst) |

---

## Step 7 — Generate

Fan out documentation generation to parallel doc writer sub-agents.

READ `references/generation.md` for document templates, Mermaid patterns, doc writer prompts, and update/merge logic.

### Generation Tasks

1. **Plan doc structure** — identify which documents to generate based on doc plan (Step 3)
2. **Spawn doc writer agents** in parallel — each reads assigned `.codedoc/` files and produces one output document
3. **Collect writer summaries** (confirmation of files written, line counts, sections generated)

### Doc Writer Architecture

Each doc writer is spawned via `task(agent_type='general-purpose')` with:
- Assigned output file path
- List of `.codedoc/` analysis files to read
- Template spec from `references/generation.md`
- Mermaid diagram patterns from `references/generation.md`

| Writer | Input Files | Output |
|--------|-------------|--------|
| **README Writer** | All `.codedoc/*.md` summaries | `README.md` |
| **Architecture Guide Writer** | `.codedoc/architecture-analysis.md` + `synthesis.md` | `docs/architecture-guide.md` |
| **Developer Guide Writer** | `.codedoc/architecture-analysis.md` + `.codedoc/api-analysis.md` + `synthesis.md` | `docs/developer-guide.md` |
| **Codebase Context Writer** | All `.codedoc/*.md` files | `docs/codebase-context.md` |
| **API Reference Writer** | `.codedoc/api-analysis.md` + native extractor output | `docs/api-reference.md` |
| **Data Model Writer** | `.codedoc/data-model-analysis.md` + native extractor output | `docs/data-model.md` |
| **Component Guide Writer** | `.codedoc/component-analysis.md` | `docs/component-guide.md` |
| **Infrastructure Writer** | `.codedoc/infrastructure-analysis.md` | `docs/infrastructure.md` |

Core writers (README, Architecture, Developer, Codebase Context) always spawn. Optional writers spawn based on doc plan.

### Writer Prompt Template

Each writer receives:
```
You are generating documentation for: {project_name}
Project path: {project_path}
Analysis directory: {project_path}/.codedoc/

Read the following analysis files:
{list of assigned .codedoc/ files}

Follow the template spec in references/generation.md for your assigned document.
Use references/generation.md Mermaid patterns for all diagrams.
Write your output directly to: {output_file}
Apply frontmatter with generation metadata.

Return a compact summary: file written, line count, sections generated, diagrams included.
```

Spawn all doc writers in parallel. Collect completion summaries before proceeding to Step 8.

### Frontmatter Schema

```yaml
---
codedoc_version: 1
generated: "2024-01-15T10:30:00Z"
project_hash: "<short git hash or file content hash>"
---
```

### Update Mode (Re-generation)

Three modes based on existing documentation state:

| Mode | Condition | Behavior |
|------|-----------|----------|
| **Fresh** | No existing docs | Generate all documents |
| **Regenerate** | Existing code-doc output | Archive to `.docs-archive/`, regenerate, merge human blocks |
| **Augment** | Existing human docs (comprehensive) | Preserve entirely, add only approved additions |

Human content detection:
- Explicit `<!-- human -->` markers
- Heuristic: prose paragraphs not matching template structure

---

## Step 8 — Review & Write

Validate generated documentation before committing.

READ `references/review.md` for reviewer checklists and severity taxonomy.

### Reviewer Agents

Spawn 3 Sonnet-class reviewers in parallel:

| Reviewer | Focus |
|----------|-------|
| **Accuracy** | Cross-reference against native extractor output, verify code paths exist |
| **Completeness** | Check all planned sections populated, no TODO placeholders |
| **Clarity** | Technical writing quality, consistent terminology, actionable instructions |

### Severity Taxonomy

| Severity | Label | Action |
|----------|-------|--------|
| 🔴 | **BLOCKER** | Must fix before commit |
| 🟠 | **WARNING** | Should fix, not blocking |
| 🟡 | **INFO** | Optional improvement |

### Fix Loop

- Maximum 2 fix iterations
- Fix all 🔴 BLOCKERs
- User decides on 🟠 WARNINGs

### Commit & Cleanup

After review passes:
1. Stage generated docs
2. Commit with message: `docs: generate codebase documentation via code-doc`
3. Clean up: `rm -rf {project}/.codedoc` (analysis artifacts are transient)
4. Report summary to user

---

## Sub-Agent Architecture

| Agent Type | Model | Spawn Tool | Purpose | Output |
|------------|-------|------------|---------|--------|
| Analyst (Architecture) | Haiku | `task(agent_type='explore')` | System structure analysis | `.codedoc/architecture-analysis.md` |
| Analyst (API Surface) | Haiku | `task(agent_type='explore')` | Endpoint mapping | `.codedoc/api-analysis.md` |
| Analyst (Data Model) | Haiku | `task(agent_type='explore')` | Schema analysis | `.codedoc/data-model-analysis.md` |
| Analyst (Component) | Haiku | `task(agent_type='explore')` | UI component mapping | `.codedoc/component-analysis.md` |
| Analyst (Infrastructure) | Haiku | `task(agent_type='explore')` | CI/CD analysis | `.codedoc/infrastructure-analysis.md` |
| Doc Writer (per doc) | Sonnet | `task(agent_type='general-purpose')` | Generate one output doc | `docs/{doc-name}.md` |
| Reviewer (Accuracy) | Sonnet | `task(agent_type='explore')` | Fact verification | (in-memory results) |
| Reviewer (Completeness) | Sonnet | `task(agent_type='explore')` | Coverage check | (in-memory results) |
| Reviewer (Clarity) | Sonnet | `task(agent_type='explore')` | Writing quality | (in-memory results) |

### Agent Counts by Tier

| Tier | Analysts | Reviewers |
|------|----------|-----------|
| Small (< 200 files) | 0 (scout direct) | 3 |
| Medium (200–1000) | 2–3 | 3 |
| Large (> 1000) | 4–5 | 3 |

---

## Output Document Set

### Core Documents (Always Generated)

| Document | Purpose | Target Lines | Diagrams |
|----------|---------|--------------|----------|
| `README.md` | Quick start, overview | 100–200 | Optional: badge/status |
| `docs/architecture-guide.md` | System design | 200–400 | Required: component, data flow |
| `docs/developer-guide.md` | Dev setup, workflow | 150–300 | Optional: setup flow |
| `docs/codebase-context.md` | LLM context file | 300–500 | Required: dependency graph |

### Optional Documents

| Document | Spawn Condition | Target Lines | Diagrams |
|----------|-----------------|--------------|----------|
| `docs/api-reference.md` | Routes detected | 200–500 | Optional: sequence |
| `docs/data-model.md` | ORM/schema detected | 150–300 | Required: ER diagram |
| `docs/component-guide.md` | Frontend detected | 200–400 | Optional: component tree |
| `docs/infrastructure.md` | CI/Docker detected | 100–200 | Optional: pipeline flow |

---

## Update Mode Behavior

| Scenario | Detection | Action |
|----------|-----------|--------|
| First run | No `docs/` directory | Fresh generation |
| Re-run (code-doc output) | Frontmatter with `codedoc_version` | Archive → regenerate → merge |
| Re-run (human docs) | No frontmatter, high prose density | Augment-only, user confirms each addition |
| Mixed | Some code-doc, some human | Per-file: regenerate code-doc, augment human |

### Archive Location

Previous code-doc output archived to `.docs-archive/<timestamp>/` before regeneration.

---

## Analysis Artifacts

The `.codedoc/` directory under `{project}/` contains transient analysis files written by sub-agents during Step 4. These are consumed by doc writers in Step 7 and cleaned up in Step 8.

### File Layout

```
{project}/.codedoc/
├── architecture-analysis.md    # Architecture Analyst output
├── api-analysis.md             # API Surface Analyst output (if spawned)
├── data-model-analysis.md      # Data Model Analyst output (if spawned)
├── component-analysis.md       # Component Analyst output (if spawned)
├── infrastructure-analysis.md  # Infrastructure Analyst output (if spawned)
├── scout-analysis.md           # Scout direct analysis (Small tier only)
├── synthesis.md                # Unified model from Step 5
└── native-extractors/          # Raw output from language-native tools
    ├── typedoc-output/
    ├── sphinx-output/
    └── ...
```

### Cleanup

After Step 8 (review passes and docs are committed):
```bash
rm -rf {project}/.codedoc
```

If code-doc crashes mid-pipeline, `.codedoc/` may persist. Add `.codedoc/` to the project's `.gitignore` as a safety net. Never commit `.codedoc/` files.

---

## Fallback Behavior

When project type or framework is unrecognized:

1. **Fall back to generic analysis** — Architecture Analyst always runs
2. **Use file structure heuristics** — `src/`, `lib/`, `tests/` patterns
3. **Warn user** — "Unrecognized project type. Generating generic documentation."
4. **Generate core docs only** — Skip optional docs that require specific detection
5. **Request user input** if ambiguous — "Detected both Python and JavaScript. Primary language?"

---

## Worked Example

**Scenario:** Next.js + Prisma application

### Step 1 — Scout Detection

```
Scanning repository...

Project type: Web Application (SSR)
Primary language: TypeScript
Frameworks detected:
  - Next.js 14 (pages/ and app/ directories)
  - React 18 (JSX components)
  - Prisma ORM (prisma/schema.prisma)
  - Tailwind CSS (tailwind.config.js)

Architecture patterns:
  - Server-side rendering (app/ directory)
  - API routes (pages/api/ or app/api/)
  - Database layer (Prisma client)

Codebase size: 450 files (Medium tier)
Entry points: pages/_app.tsx, app/layout.tsx
```

### Step 2 — Existing Doc Assessment

```
Existing documentation: Partial
  ✓ README.md (basic, 50 lines)
  ✗ No architecture docs
  ✗ No developer guide
  ✓ Prisma schema comments (inline)
```

### Step 3 — Doc Plan

```
📋 Documentation Plan for next-prisma-app

Core Documents:
  ✓ README.md (enhance existing)
  ✓ docs/architecture-guide.md
  ✓ docs/developer-guide.md
  ✓ docs/codebase-context.md

Optional Documents (based on detection):
  ✓ docs/api-reference.md — 12 API routes detected
  ✓ docs/data-model.md — Prisma schema with 8 models
  ✓ docs/component-guide.md — 24 React components detected

Proceed? [y/n]
```

### Step 4 — Analysis

Create `.codedoc/` directory. Spawn analysts (Medium tier = 3 analysts):

1. **Architecture Analyst** → writes `.codedoc/architecture-analysis.md`, returns summary
2. **API Surface Analyst** → writes `.codedoc/api-analysis.md`, returns summary
3. **Data Model Analyst** → writes `.codedoc/data-model-analysis.md`, returns summary

Native extractors:
- TypeDoc → output saved to `.codedoc/native-extractors/typedoc/`
- Prisma CLI → output saved to `.codedoc/native-extractors/prisma/`

Orchestrator collects 3 compact summaries (not full analysis).

### Step 5 — Synthesis

Read `.codedoc/` files selectively to build unified model. Write to `.codedoc/synthesis.md`.

```
## Synthesis Summary

### Architecture Overview
Server-rendered Next.js application with Prisma ORM backend.
App Router pattern with server components and API routes.

### Key Components
| Component | Purpose | Dependencies |
|-----------|---------|--------------|
| app/layout.tsx | Root layout | Tailwind, AuthProvider |
| app/api/users/ | User CRUD API | Prisma, NextAuth |
| components/UserCard | User display | React, Tailwind |

### Data Flows
1. Auth flow: NextAuth → JWT → API routes → Prisma
2. Data fetch: Server Component → Prisma → React render

### API Surface
12 endpoints: 4 user, 3 post, 3 comment, 2 auth
```

### Step 6 — User Checkpoint

User confirms synthesis, proceeds to generation.

### Step 7 — Generate

Fan out 7 doc writer sub-agents in parallel:
- README Writer → reads all `.codedoc/` summaries → writes `README.md`
- Architecture Guide Writer → reads `.codedoc/architecture-analysis.md` + `synthesis.md` → writes `docs/architecture-guide.md`
- Developer Guide Writer → reads `.codedoc/architecture-analysis.md` + `api-analysis.md` + `synthesis.md` → writes `docs/developer-guide.md`
- Codebase Context Writer → reads all `.codedoc/` files → writes `docs/codebase-context.md`
- API Reference Writer → reads `.codedoc/api-analysis.md` + TypeDoc output → writes `docs/api-reference.md`
- Data Model Writer → reads `.codedoc/data-model-analysis.md` + Prisma output → writes `docs/data-model.md`
- Component Guide Writer → reads `.codedoc/component-analysis.md` → writes `docs/component-guide.md`

Collect 7 writer summaries (confirmation of files written).

### Step 8 — Review & Write

3 reviewers validate, no blockers found. Commit generated docs. Clean up `.codedoc/`.

---

## Monorepo Handling

### Detection

Monorepo detected via workspace patterns:
- `pnpm-workspace.yaml`
- `lerna.json`
- `packages/*/package.json`
- `apps/*/package.json`
- `workspaces` field in root `package.json`

### User Choice

```
🏢 Monorepo Detected

Sub-projects found:
  1. packages/api — Express API server
  2. packages/web — Next.js frontend
  3. packages/shared — Shared utilities
  4. packages/db — Prisma database layer

Documentation mode:
  [u] Unified — Single doc set covering entire monorepo
  [p] Per-project — Separate doc set for each package

Choose mode: [u/p]
```

### Unified Mode

- Single `docs/` at repo root
- Architecture doc covers cross-package relationships
- Package-specific details in subsections

### Per-Project Mode

- Each package gets own `docs/` directory
- Shared docs at root: `README.md`, `docs/monorepo-overview.md`
- Cross-references between package docs

---

_Designed for multi-agent orchestration. Requires: `git`, native extractors per language (optional)._
