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

**Scout orchestrates, Analysts read code.**

- The **Scout** (you, the orchestrator) handles detection, sizing, planning, and synthesis
- **Analyst agents** are spawned via `task(agent_type='explore')` to read code and produce findings
- **Reviewer agents** are spawned via `task(agent_type='explore')` to validate generated docs
- All agents are stateless — provide complete context in each spawn

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

Run analysis using native extractors first, then LLM analysts.

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

Native extractor output is fed to analysts as ground truth for function signatures, types, and
module structure.

### Analyst Agents (Spawned by Tier)

READ `references/analysis.md` sections 2–3 for complete analyst prompt templates and
language-specific patterns.

| Agent | Spawn Condition | Focus Area |
|-------|-----------------|------------|
| **Architecture Analyst** | Always | System structure, component relationships, data flow |
| **API Surface Analyst** | Routes/endpoints detected | REST/GraphQL endpoints, request/response schemas |
| **Data Model Analyst** | ORM/schema detected | Database schema, relationships, migrations |
| **Component Analyst** | Frontend detected | UI components, props, state management |
| **Infrastructure Analyst** | CI/Docker/IaC detected | Build pipeline, deployment, configuration |

### Tiered Agent Strategy

| Tier | Approach |
|------|----------|
| **Small** (< 200 files) | Scout performs analysis directly — no sub-agents |
| **Medium** (200–1000 files) | Scout + 2–3 most relevant analysts based on detection |
| **Large** (> 1000 files) | Full pipeline: scout + all relevant analysts in parallel |

### Agent Spawning

All analysts spawned via `task(agent_type='explore')` with:
- Complete context (project type, framework, file scope)
- Native extractor output as ground truth
- Structured Markdown output format
- Cross-reference requirements

---

## Step 5 — Synthesize

Merge analyst outputs and native extractor data into a unified model.

READ `references/analysis.md` section 4 for synthesis protocol.

### Synthesis Tasks

1. **Unify data models** — merge native extractor types with analyst findings
2. **Correlate cross-cutting concerns** — trace flows across components
3. **Detect inconsistencies** — flag contradictions between analyst outputs
4. **Identify documentation-worthy flows** — user journeys, critical paths

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

Produce documentation from synthesis model.

READ `references/generation.md` for document templates, Mermaid patterns, and update/merge logic.

### Generation Tasks

1. **Select templates** based on doc plan
2. **Populate templates** with synthesis data
3. **Generate diagrams** (Mermaid) for visual documentation
4. **Apply frontmatter** with generation metadata

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

### Commit

After review passes:
1. Stage generated docs
2. Commit with message: `docs: generate codebase documentation via code-doc`
3. Report summary to user

---

## Sub-Agent Architecture

| Agent Type | Model | Spawn Tool | Purpose |
|------------|-------|------------|---------|
| Analyst (Architecture) | Haiku | `task(agent_type='explore')` | System structure analysis |
| Analyst (API Surface) | Haiku | `task(agent_type='explore')` | Endpoint mapping |
| Analyst (Data Model) | Haiku | `task(agent_type='explore')` | Schema analysis |
| Analyst (Component) | Haiku | `task(agent_type='explore')` | UI component mapping |
| Analyst (Infrastructure) | Haiku | `task(agent_type='explore')` | CI/CD analysis |
| Reviewer (Accuracy) | Sonnet | `task(agent_type='explore')` | Fact verification |
| Reviewer (Completeness) | Sonnet | `task(agent_type='explore')` | Coverage check |
| Reviewer (Clarity) | Sonnet | `task(agent_type='explore')` | Writing quality |

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

Spawn analysts (Medium tier = 3 analysts):

1. **Architecture Analyst** → maps Next.js app structure, page routing, data flow
2. **API Surface Analyst** → documents 12 API routes with request/response schemas
3. **Data Model Analyst** → extracts Prisma schema, relationships, indexes

Native extractors:
- TypeDoc → TypeScript type definitions
- Prisma CLI → schema introspection

### Step 5 — Synthesis

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

Produce 7 documents with Mermaid diagrams:
- Architecture component diagram
- Data flow diagram
- Prisma ER diagram
- API endpoint documentation

### Step 8 — Review & Write

3 reviewers validate, no blockers found. Commit generated docs.

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
