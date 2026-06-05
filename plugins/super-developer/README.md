# Super Developer

Super Developer is a portable coding-assistant workflow, packaged as a Claude Code plugin, for moving from exploration to Slice-first planning, isolated implementation, bounded code review, final audit, documentation, and release preparation.

One plugin. 13 skills. No manual git juggling.

---

## What It Does

Super Developer replaces scattered prompts with a file-backed workflow. Planned-feature work uses one greenfield model:

```text
conceptualize (optional Index + Slices)
        |
        v
implementation-plan -> review-plan -> implement -> final review-code + final audit
        |                 |              |             |                  |
        |                 |              |             |                  final completeness gate
        |                 |              |             final code-risk gate
        |                 |              package agents + proof Markdown + reports
        |                 plan quality and Slice coverage gate
        SPEC.md + tasks.json registry + packages/proofs/reports
```

Validated Slices are product/design authority only. Workflow, tool, git, proof, review, and audit authority stays in the plugin instructions and shared references.

---

## Planned-Feature Artifact Model

A planned feature lives under `.tasks/<feature>/` and points to optional `.planning/<concept>/` Slice material.

| Artifact | Purpose |
|---|---|
| `.planning/<concept>/index.md` | Optional Conceptualize workspace entry point. |
| `.planning/<concept>/slices/*.md` | Optional authoritative product/design Slices. |
| `.tasks/<feature>/SPEC.md` | Accepted requirements, constraints, non-goals, Slice inventory, and verification summary. |
| `.tasks/<feature>/tasks.json` | Lightweight registry only: feature metadata, package paths, proof paths, report paths, status, and dependencies. |
| `.tasks/<feature>/packages/<WP-ID>.md` | Work-package assignment: scope, Slice obligations, primary paths, verification expectations, proof/report paths, dependencies. |
| `.tasks/<feature>/proofs/<WP-ID>.proof.md` | Package-agent closure evidence for Slice rows and verification expectations. |
| `.tasks/<feature>/reports/<WP-ID>.package-verification.md` | Independent package verification receipt bound to proof digest and reviewed state. |
| `.tasks/<feature>/reviews/review-code-state.json` | Review-code governance readiness for audit handoff. |

`tasks.json` is bookkeeping. Package Markdown owns assignment, proof Markdown owns closure evidence, package reports own independent verification receipt state, review-code state owns final-review readiness, and audit owns the final PASS/FAIL judgment.

---

## `sliceproof.py` Helper Contract

`plugins/super-developer/assets/sliceproof.py` is the only planned-feature mechanical helper. It validates paths and artifact mechanics; it does not run tests, judge implementation sufficiency, write review readiness, or replace package verification, review-code, or audit.

Run from a repository or package worktree with explicit paths:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
```

Command boundaries:

- `validate-plan`: checks the registry, package Markdown, safe paths, dependencies, and declared Slice H3 IDs.
- `create-proof`: creates the declared proof Markdown placeholder and refuses silent overwrite of edited evidence.
- `validate-proof`: checks required proof sections, closure rows, command/file evidence, blocking markers, and approved deferrals.
- `validate-final`: checks all packages are done, all proofs pass mechanically, and all package verification reports exist and bind to the current proof digest.

See [`references/tool-usage.md`](references/tool-usage.md), [`references/slice-first-artifacts.md`](references/slice-first-artifacts.md), and [`references/package-lifecycle.md`](references/package-lifecycle.md) for the detailed boundaries.

---

## Skills

| Skill | What It Does | Usage |
|---|---|---|
| **conceptualize** | Runs an optional one-question-at-a-time exploration, maintains an ignored workspace Index, and writes focused Slices only when useful. | Standalone + pre-planning |
| **implementation-plan** | Creates `SPEC.md`, the lightweight registry, package Markdown, proof paths, report paths, and proof placeholders from approved requirements, Slices, or spike evidence. | Pipeline + standalone |
| **skill-authoring** | Creates or revises agent skills with compact eager workflows, true on-demand references, and a 150-line eager maximum. | Standalone + internal |
| **review-plan** | Validates planned-feature artifacts, Slice coverage, package assignment, proof/report expectations, and approved deferrals before implementation. | Pipeline + standalone |
| **implement** | Orchestrates package worktrees, package agents, proof Markdown, package verification reports, integration checkpoints, review-code, and audit handoff. | Pipeline + standalone |
| **review-code** | Runs bounded PR, local, or planned-feature pipeline code review with dynamic risk lenses, Skeptic verification for serious findings, and governed fix verification where the mode permits fixes. | Pipeline + standalone + PR review |
| **audit** | Final read-only planned-feature completeness gate over accepted artifacts, proof Markdown, package reports, optional review-code context, and integrated code state. | Final gate + standalone |
| **tasks** | Read-only dashboard for registry, package, proof, report, and review-code readiness signals. | Standalone |
| **spike-to-plan** | Runs empirical feasibility spikes before planning and routes accepted evidence into durable planning artifacts. | Planning hook |
| **spike-and-fix** | Diagnoses bugs evidence-first, validates candidate fixes in isolation, then extracts a clean regression-tested fix. | Standalone |
| **perspectives** | Explores architecture or design options from multiple angles with a final skeptic synthesis. | Standalone |
| **worktree** | Provides git worktree runbooks for planned features, bugfixes, hotfixes, spikes, cleanup, and target-merge safety. | Internal + standalone |
| **code-doc** | Generates or updates codebase documentation through scout, analysis, synthesis, review, and handoff stages. | Standalone |
| **release** | Prepares and publishes releases behind a single release contract covering checks, pushes, tags, notes, and cleanup. | Standalone |

---

## Review-Code Modes

| Mode | Trigger | Boundary |
|---|---|---|
| **Planned-feature pipeline** | Explicit or inherited feature context plus `.tasks/<feature>/` artifacts and reviewed implementation state. | Consumes package proof/report signals, records audit readiness, and routes serious fixes through proof/report freshness rules. |
| **PR** | PR URL, `owner/repo#N`, or `#N` in a repository with `gh` available. | Review-only for code changes; GitHub side effects require the PR action gate. |
| **Local** | No planned-feature context and no PR identifier. | Reviews staged, unstaged, or branch diff; local fix actions require the local action gate and fix verification. |

Ordinary PR/local review does not inherit planned-feature Slice, proof, report, or audit obligations unless planned-feature artifacts are explicitly in scope.

---

## Git Worktree Strategy

The `implement` and `worktree` skills keep the root worktree user-owned and create isolated package worktrees:

```text
project/                               # user-owned root; do not switch branches
+-- .worktrees/
|   +-- auth/
|   |   +-- wp-WP1/                    # branch: wp/auth/WP1
|   |   +-- wp-WP2/                    # branch: wp/auth/WP2
|   |   +-- merge/                     # branch/ref: feature/auth
```

Key rules:

- The orchestrator owns branch/worktree creation, merges, cleanup, and approved pushes.
- Package agents edit only their assigned package worktree and proof Markdown handoff.
- Feature-branch push must match the approved Execution Contract.
- Target/main merge or push always requires separate explicit approval.
- Cleanup requires merge-base proof and clean worktrees.

---

## Installation

### Install from GitHub

```bash
/plugin marketplace add leninkhaidem/super-developer
/plugin install super-developer@super-developer-marketplace
```

Update later:

```bash
/plugin update super-developer@super-developer-marketplace
```

### Install from local directory

```bash
git clone https://github.com/leninkhaidem/super-developer.git
claude --plugin-dir /path/to/super-developer/plugins/super-developer
```

Claude Code discovers packaged skills automatically. Other hosts need equivalent plugin/skill discovery and `SUPER_DEVELOPER_PLUGIN_ROOT` pointing at `plugins/super-developer`.

---

## Usage

### Full planned-feature pipeline

```text
> Plan this feature
```

Planning writes `.tasks/<feature>/SPEC.md`, `.tasks/<feature>/tasks.json`, package Markdown, and declared proof/report paths. After plan review approval, `implement` presents an Execution Contract. Approve auto-resolve to continue through package implementation, package verification, final review-code, and final audit sibling checks, or choose step-by-step control at each gate.

Useful standalone prompts:

```text
> Conceptualize this product idea before planning
> Get perspectives on this architecture decision
> Spike this feature assumption before planning
> Show me task status
> Review this PR: owner/repo#42
> Review my code
> Audit the auth-system feature
> Spike and fix this regression
> Prepare a release
> Document this codebase
```

---

## Plugin Structure

```text
plugins/super-developer/
+-- .claude-plugin/
|   +-- plugin.json
+-- assets/
|   +-- sliceproof.py
|   +-- tests/
|       +-- test_sliceproof.py
+-- references/
|   +-- clean-code-rules.md
|   +-- conceptualize-slice-authority.md
|   +-- decision-prompts.md
|   +-- known-risk-patterns.md
|   +-- model-preferences.md
|   +-- package-lifecycle.md
|   +-- slice-first-artifacts.md
|   +-- tool-usage.md
|   +-- work-packages.md
+-- skills/
|   +-- audit/
|   |   +-- SKILL.md
|   |   +-- references/audit-subagent-contract.md
|   +-- code-doc/
|   |   +-- SKILL.md
|   |   +-- references/update-merge.md
|   +-- conceptualize/
|   |   +-- SKILL.md
|   |   +-- references/final-handoff.md
|   |   +-- references/slice-template.md
|   |   +-- references/workspace-index.md
|   +-- implementation-plan/
|   |   +-- SKILL.md
|   |   +-- references/artifact-authoring.md
|   |   +-- references/conceptualize-inputs.md
|   |   +-- references/design-preflight.md
|   |   +-- references/spec-template.md
|   |   +-- references/validation-checklist.md
|   +-- implement/
|   |   +-- SKILL.md
|   |   +-- references/execution-contract.md
|   |   +-- references/package-agent-contract.md
|   |   +-- references/package-dispatch.md
|   |   +-- references/package-verification.md
|   |   +-- references/repair-agent-contract.md
|   |   +-- references/package-integration-gates.md
|   +-- review-code/
|   |   +-- SKILL.md
|   |   +-- references/local-workflow.md
|   |   +-- references/pipeline-report.md
|   |   +-- references/pr-workflow.md
|   +-- review-plan/
|   |   +-- SKILL.md
|   |   +-- references/plan-review-findings.md
|   |   +-- references/plan-review-resolution.md
|   |   +-- references/plan-review-rubrics.md
|   +-- skill-authoring/
|   |   +-- SKILL.md
|   +-- tasks/
|   |   +-- SKILL.md
|   |   +-- references/dashboard-display.md
|   +-- worktree/
|   |   +-- SKILL.md
|   |   +-- references/bugfix-hotfix-workflow.md
|   |   +-- references/cleanup-safety.md
|   |   +-- references/feature-package-workflow.md
|   +-- perspectives/SKILL.md
|   +-- spike-and-fix/SKILL.md
|   +-- spike-to-plan/SKILL.md
|   +-- release/SKILL.md
```

---

## Requirements

- Claude Code with plugin support, or another host with equivalent skill/plugin loading.
- Python 3 for `sliceproof.py`.
- git for worktree-based workflows.
- GitHub CLI (`gh`) for PR review mode only.

---

## Operating Principles

| Principle | Why it matters |
|---|---|
| Slice-first planning | Slices capture durable product/design understanding while control-plane authority stays out of Slice text. |
| Progressive disclosure | `SKILL.md` files route and guard; detailed contracts load only at action points. |
| Package delegation | Work packages are large enough for useful sub-agent execution and small enough for focused proof/report verification. |
| Independent verification | Package reports, review-code readiness, and audit each protect a different gate. None replaces another. |
| Read-only dashboards | Status views show mechanical signals without mutating lifecycle state or claiming semantic completion. |
| Explicit git authority | Feature pushes, target merges, cleanup, and release operations happen only under their named contracts. |

---

## License

MIT
