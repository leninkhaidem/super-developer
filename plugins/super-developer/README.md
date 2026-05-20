# Super Developer

A portable coding-assistant workflow, currently packaged as a Claude Code plugin, that orchestrates the full development lifecycle — from divergent ideation through requirements-spec-driven planning, parallel implementation with git worktree isolation, multi-agent adversarial code review, and gated release publishing.

One plugin. Eleven skills. Zero manual git juggling.

---

## What It Does

Super Developer packages portable skill instructions into an opinionated development workflow engine. In Claude Code, it replaces scattered slash commands and ad-hoc prompts with a structured pipeline where each stage feeds the next — with right-sized sub-agent work packages, git worktree isolation, and adversarial review gates catching issues before they ship.

```
[perspectives]              Optional — divergent problem-solving for complex decisions
       |
       v
  implementation-plan  --->  review-plan  --->  implement
                     |                  |              |
              structured ACs       plan gate      Execution Contract
              + traceability                    package self-verify
                                                  targeted review
                                                  review-code discovery
                                                  fix verification
                                                  final audit
```

The pipeline flows automatically with confirmation gates. Say **"proceed through all stages"** or approve `implement`'s Execution Contract auto-resolve mode and it runs implementation, package self-verification, targeted review, review-code discovery, delegated fixes, delta Fix Verification Review, triggered widening/escalation when required, and final internal audit once review-code reaches audit readiness. Or invoke any skill independently — they work standalone too.

---

## Skills

| Skill | What It Does | Usage |
|---|---|---|
| **perspectives** | Divergent problem-solving. Spawns 3-5 Opus-class sub-agents, each approaching the problem from a distinct angle (Infrastructure, Architecture, Data, Root Cause, etc.). A final Skeptic agent stress-tests and synthesizes proposals into a ranked recommendation. | Standalone |
| **implementation-plan** | Converts a completed brainstorming or requirements discussion into a structured task plan under `.tasks/<feature>/` with `SPEC.md`, structured task-level acceptance criteria, traceability source refs, `context_bundles`, `design_decisions`, and work packages. Runs triggered Design Preflight and conditional `spike-to-plan` evidence collection before durable plan artifacts for nontrivial/risky features. | Pipeline + Standalone |
| **spike-to-plan** | Empirical feature spikes that validate uncertain assumptions before implementation planning. Produces planning evidence only; accepted outcomes become `design_decisions`, not persisted spike code. | Standalone + Planning hook |
| **review-plan** | Plan review gate. Performs deterministic schema/traceability validation, then spawns one **Plan Reviewer** that challenges the approach first and checks artifact quality second. Adds a dedicated **Security/Failure-Mode Reviewer** only for security/privacy/safety-sensitive plans or explicit escalation. Validates `SPEC.md`, `tasks.json`, context bundles, risk metadata, work packages, and accepted `design_decisions` cold from files only. | Pipeline + Standalone |
| **tasks** | Implementation status dashboard. Shows progress across all features or drills into a specific one with phase-by-phase breakdown and package-proof evidence-health warnings. Can modify task status on request, but status overrides do not create verification evidence. | Standalone |
| **spike-and-fix** | Bug-report troubleshooting that runs evidence-first diagnosis, validates candidate fixes in an isolated spike, then extracts a clean regression-tested bugfix/hotfix. Escalates to implementation planning when the blast radius is large. | Standalone |
| **implement** | Unified delivery orchestrator. Presents an Execution Contract, creates git worktrees per package, dispatches packages to self-verifying sub-agents, validates package proof evidence before merge/unlock, runs risk-triggered targeted package review, coordinates delegated fixes, invokes review-code discovery/fix verification, and finishes with final internal audit. | Pipeline + Standalone |
| **audit** | Acceptance-completeness verification. Spawns a read-only sub-agent that checks every SPEC/task acceptance criterion and accepted package proof against the final codebase state. It is the final internal pipeline gate after review-code audit readiness and remains invocable standalone. | Internal pipeline gate + Standalone |
| **review-code** | Bounded multi-agent code review. Always runs one **Code Reviewer**, adds at most one optional **Specialist Reviewer** for the highest-priority risk trigger, and uses a **Skeptic Agent** to verify serious findings before reporting. Initial discovery uses dynamic risk lenses and compact coverage evidence; local and pipeline `fix` paths delegate non-trivial fixes and verify closure with Fix Verification Review. PR mode is review-only and has no code-fix path. | Pipeline + Standalone + PR review |
| **code-doc** | Generate comprehensive documentation for any codebase via hybrid analysis (native extractors + LLM agents). Adaptive 8-step pipeline: Scout → Existing Doc Assessment → Doc Plan → Analyze (delegate to sub-agents) → Synthesize → User Checkpoint → Generate (fan-out doc writers) → Review & Handoff. Never auto-commits; it may propose a commit, but only runs it after explicit approval. Outputs core docs (protected/conditional README plus architecture-guide, developer-guide, codebase-context) plus recommended artifacts such as navigation, patterns, config, errors, flows, boundaries, inventory, and security. | Standalone |
| **release** | Prepare and publish releases through one Release Contract covering base-branch detection (`main`/`master`), changelog/docs decisions, version bumps, checks, pushes/tags/GitHub releases, and exact cleanup of release worktrees and feature branches. | Standalone |

`review-code` works in **3 modes** — it auto-detects which to use:

| Mode | When | What it reviews | Fix boundary |
|---|---|---|---|
| **Pipeline** | During unified delivery after `implement` package work completes | Feature branch diff against `main` from the merge worktree, with available plan/package-proof/context artifacts as task-awareness context | Delegates confirmed serious fixes in coherent batches; final internal audit runs after review-code reaches audit readiness |
| **PR** | You provide a PR identifier (`owner/repo#42`, URL, or `#42`) | Full PR diff from GitHub via `gh` CLI | Review-only: can approve, request changes, edit the report, or abort; no code-fix path and no local Fix Verification Review |
| **Local** | No pipeline context, no PR identifier | Staged changes, unstaged changes, or branch diff (auto-detected) | `fix` delegates non-trivial fixes to a Fix Implementer, then requires a delegated Fix Verification Reviewer before post-fix commit/readiness |


### Review-Code Reviewer Topology

`review-code` uses bounded reviewer caps instead of unconditional specialist fanout:

- **Normal review cap:** Code Reviewer + conditional Skeptic Agent = 2 reviewers.
- **Risky review cap:** Code Reviewer + one selected Specialist Reviewer + conditional Skeptic Agent = 3 reviewers.
- **Specialist priority:** security/privacy/safety, then data integrity/persistence, then performance, then architecture/integration. If several triggers match, only the highest-priority specialist runs.
- **Big diffs:** broad diffs are split into semantic batches; each batch keeps the same reviewer caps, and a final global integration pass deduplicates and checks cross-batch conflicts without reopening full fanout.
- **Task-awareness:** available `SPEC.md`, `tasks.json`, package proofs, context bundles, and audit results help review-code flag apparent omissions, contradictions, stale evidence, or regressions. These are consistency signals only; audit remains authoritative for acceptance-criteria and planned-task completeness.
- **Local fixes:** non-trivial local `fix` work is delegated to a Fix Implementer and then verified by a Fix Verification Reviewer against the fix delta. The main agent only handles super-simple mechanical typo/formatting fixes inline.
- **PR boundary:** PR mode is review-only for code changes; it does not apply fixes and does not run local Fix Verification Review.
- **Pipeline boundary:** pipeline review runs before final internal audit. Confirmed serious findings are delegated to Fix Implementers in coherent root-cause/package/risk batches; the orchestrator does not apply substantive production/test/documentation fixes inline.

### Review-Code Loop Governance

- **Discovery review:** reviewers use dynamic risk lenses selected from mode, diff surface, task/package context, risk tags, changed files, and discovered risk signals. Clean reports require compact concrete coverage rows plus completed Skeptic handling for serious candidates.
- **Fix verification:** pipeline and local fixes use delta Fix Verification Review for assigned dedupe keys and fix-introduced serious regressions. Full or widened rereview is not the normal post-fix path; it runs only when documented widening triggers fire.
- **Pipeline auto-resolve:** confirmed serious findings block readiness until fixed and verified `closed`. Repeated failures change strategy through stronger fix agents, specialist/widened verification, semantic batching, or other escalation before user input; user stops are reserved for authority boundaries such as product/design changes, scope expansion, unsafe/external actions, new dependencies, credentials, risk acceptance, or no viable verification seam.
- **Review state vs proof:** pipeline review may keep one lightweight `.tasks/<feature>/reviews/review-code-state.json` governance snapshot, but it is not proof, audit evidence, an event log, or an acceptance ledger. Package proofs remain the acceptance evidence surface and must be refreshed when review-code fixes affect their evidence.
- **Suggestions:** suggestions are report-only by default. Automatic suggestion fixes are allowed only when bundled with a confirmed serious fix, same-scope, near-zero-risk, behavior-preserving, and adding no review surface; PR mode still performs no code fixes.
- **Progressive disclosure:** always-loaded skill files keep mode routing and critical invariants up front, then lazy-load detailed references such as `local-actions.md`, `pr-actions.md`, `pipeline-actions.md`, `finding-contract.md`, and `fix-verification.md` only when the workflow reaches that phase.

---

## Git Worktree Strategy

The `implement` skill follows a branch-isolated, agent-managed git workflow:

- **Main stays on `main`.** The main working tree never switches branches. Ever.
- **Development happens in `.worktrees/`.** Each delegated work package gets its own worktree. Multiple substantial independent packages may run in parallel; related tasks are bundled to avoid repeated codebase exploration.
- **The orchestrator owns git.** Sub-agents receive a work package, task IDs, primary paths, and a worktree path — they write code and commit per task ID, while the orchestrator creates worktrees, merges branches, verifies integration, and cleans up.
- **Feature branches are refs, not worktrees.** This keeps them unlocked for merging from any worktree.
- **Merge to main requires explicit approval.** "Push to remote" does not mean "merge to main."

```
project/                              <- always on 'main'
+-- .worktrees/
|   +-- auth/
|   |   +-- wp-WP1/                   <- branch: task/auth/WP1 (package: backend auth)
|   |   +-- wp-WP2/                   <- branch: task/auth/WP2 (package: login UI)
|   |   +-- merge/                    <- branch: feature/auth
```

See [`skills/worktree/SKILL.md`](skills/worktree/SKILL.md) for the complete workflow including spike, bugfix, hotfix, and multi-phase dependency handling.

---

## Installation

### Install from GitHub (recommended)

Add the repository as a marketplace and install — no cloning required:

```bash
# 1. Add the marketplace (one-time)
/plugin marketplace add leninkhaidem/super-developer

# 2. Install the plugin
/plugin install super-developer@super-developer-marketplace
```

To update later:

```bash
/plugin update super-developer@super-developer-marketplace
```

### Install from local directory

If you prefer to clone first:

```bash
git clone https://github.com/leninkhaidem/super-developer.git
claude --plugin-dir /path/to/super-developer/plugins/super-developer
```

### Installation scopes

| Scope | Flag | Where it applies |
|---|---|---|
| User (default) | `--scope user` | All your projects |
| Project | `--scope project` | Shared with team via `.claude/settings.json` |
| Local | `--scope local` | This project only, gitignored |

Claude Code loads all 11 skills automatically via plugin auto-discovery. Other hosts need equivalent skill/plugin discovery and a `SUPER_DEVELOPER_PLUGIN_ROOT` variable pointing at the plugin root.

---

## Usage

### Full Pipeline

Start a conversation, discuss what you want to build, then:

```
> Plan this feature
```

The agent infers the feature name, creates `SPEC.md` and schema-versioned `tasks.json`, then asks to continue through plan review and the `implement` Execution Contract. Say **"proceed through all stages"** to run the full pipeline end-to-end, or confirm each gate individually.

### Individual Skills

```
> Get me some perspectives on this architecture decision
> Show me the task status
> Review this PR: owner/repo#42
> Review my code
> Audit the auth-system feature
> Spike and fix this regression: checkout fails when the cart has a deleted item
> Spike this feature assumption before planning: can the vendor API stream partial results with retries?
```

### Package Proof Helper

`assets/taskctl.py` provides package-proof helpers for planned features. Package proofs are the planned-feature evidence surface: read-only commands inspect `.tasks/<feature>/tasks.json` and `.tasks/<feature>/proofs/WP<N>.proof.json`, package lifecycle commands write only the selected package proof's accepted/reopened state, and task lifecycle helpers perform constrained block/reset mutations in `tasks.json`. The helper does not mutate generated artifacts, proof history, event logs, or unrelated proof files.

Read-only commands:

- `proof-template`: emit a deterministic proof template for one work package.
- `validate-proof`: validate one package proof file.
- `validate-proofs`: validate exactly one proof file for every work package.
- `must-prove`: emit acceptance criteria and evidence obligations.
- `summary`: emit task, package, and proof-health summary output.
- `next-package`: emit proof-ready dependency candidates and interrupted packages without persisting package status.

Package-level lifecycle proof writers:

- `accept-package`: validate and write accepted lifecycle state for one package proof.
- `reopen-package`: write reopened lifecycle state for one package proof.

Constrained task lifecycle helpers:

- `block-task`: mark one task blocked with a required reason.
- `reset-task`: reset one interrupted or blocked task to pending after orchestrator review.

These commands do not run recorded package verification commands. Accepted package proofs must cite passing evidence for required package verification commands and required targeted package review. Final implementation and audit gates require completed task lifecycle plus one valid, current, lifecycle-accepted proof file per planned work package. Historical `verification.json` files are not authoritative package or final evidence. See [`references/package-lifecycle.md`](references/package-lifecycle.md) for the helper boundary index and [`skills/implement/references/package-proof-lifecycle.md`](skills/implement/references/package-proof-lifecycle.md) for canonical lifecycle transition, provenance, freshness, dirty-proof, and final-gate semantics.

For exact command shapes, read-only vs mutation boundaries, and helper-script safety rules, see [`references/tool-usage.md`](references/tool-usage.md).

### Pipeline Flow Control

| What you say | What happens |
|---|---|
| "Plan this feature" | Creates `SPEC.md` and `tasks.json`, asks to continue |
| "Proceed through all stages" | Runs implementation-plan -> review-plan -> implement -> review-code discovery/fix verification -> final audit, stopping only at required decision/unsafe-state gates |
| Approve auto-resolve at Execution Contract | Runs package implementation, sub-agent self-verification, targeted package review, review-code discovery, delegated fixes, Fix Verification Review, triggered widening/escalation, and final audit when audit-ready |
| Confirm at each gate | Step-by-step control over plan review, Execution Contract, review/fix, and final audit |

---

## Plugin Structure

```
super-developer/
+-- .claude-plugin/
|   +-- plugin.json                     # Plugin manifest
+-- assets/
|   +-- validate-tasks-json.py             # tasks.json schema/dependency validator
+-- references/
|   +-- clean-code-rules.md               # Development Quality Contract for agents
|   +-- model-preferences.md              # Sub-agent model selection schema
|   +-- work-packages.md                  # Work-package delegation contract
|   +-- decision-prompts.md               # Decision-card UX mechanics (review-plan + review-code)
|   +-- design-preflight.md              # Triggered planning challenge before durable task plans
|   +-- plan-review-findings.md          # Plan reviewer finding format and severity contract
|   +-- plan-review-rubrics.md           # Narrowed plan reviewer role rubrics
|   +-- plan-review-resolution.md        # Main-agent plan review triage and re-review rules
|   +-- package-lifecycle.md             # Targeted package proof lifecycle semantics
|   +-- tool-usage.md                    # Helper script command shapes and safety rules
+-- skills/
|   +-- worktree/
|   |   +-- SKILL.md                       # Git worktree strategy
|   +-- spike-and-fix/
|   |   +-- SKILL.md                    # Evidence-first bug diagnosis + clean fix
|   +-- spike-to-plan/
|   |   +-- SKILL.md                    # Empirical feature spike before durable planning
|   +-- perspectives/
|   |   +-- SKILL.md                    # Divergent problem-solving
|   +-- implementation-plan/
|   |   +-- SKILL.md                    # Requirements -> SPEC.md + tasks.json
|   +-- review-plan/
|   |   +-- SKILL.md                    # Plan review gate
|   +-- tasks/
|   |   +-- SKILL.md                    # Status dashboard
|   +-- implement/
|   |   +-- SKILL.md                    # Orchestrator + git worktrees
|   +-- audit/
|   |   +-- SKILL.md                    # Post-implementation verification
|   +-- review-code/
|   |   +-- SKILL.md                    # Multi-agent code review
|   |   +-- references/
|   |       +-- pr-workflow.md          # GitHub PR review workflow
|   |       +-- local-workflow.md       # Local code review workflow
|   +-- code-doc/
|       +-- SKILL.md                    # Codebase documentation generator
|       +-- references/
|           +-- update-merge.md         # Update/merge logic for existing docs
|   +-- release/
|       +-- SKILL.md                    # Single-contract release preparation and publishing
```

---

## Requirements

- **Claude Code with plugin support** for packaged installation; other hosts need equivalent skill/plugin support and `SUPER_DEVELOPER_PLUGIN_ROOT`
- **Python 3** (tasks.json validation asset)
- **git** (all skills)
- **GitHub CLI (`gh`)** (review-code PR mode only) — [install](https://cli.github.com/)

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Main agent orchestrates, sub-agents implement and self-verify | Separation of concerns — orchestrator manages git state, dispatch, evidence validation, and integration checks; sub-agents write code, run targeted checks, and update criterion-level evidence |
| Adaptive adversarial review | One Plan Reviewer runs by default; a Security/Failure-Mode Reviewer is added only for security/privacy/safety-sensitive plans or escalation. Code review uses dynamic discovery lenses, a bounded topology, at most one Specialist Reviewer selected by risk priority, and a conditional Skeptic Agent to verify serious findings and risky clean coverage before reporting. |
| Git worktree isolation | Parallel sub-agents work in separate worktrees — no branch switching, no merge conflicts during implementation |
| Package proofs as evidence gate | Planned-feature pipelines require one accepted `.tasks/<feature>/proofs/WP<N>.proof.json` per work package. Proof entries must be criterion-scoped, state-bound, and current in the resolved worktree; review-code governance state never replaces package proof acceptance. |
| Evidence-first bug fixing | Bug work starts from reproduced evidence, uses isolated spike validation for candidate fixes when needed, then extracts durable tests and a clean fix branch instead of shipping exploratory changes. Review/audit fixes generalize the bug class and update affected package proof evidence. |
| Evidence-first planning for uncertain features | Planning uses triggered Design Preflight and, only when repo/docs inspection cannot resolve material assumptions, `spike-to-plan` to gather empirical evidence before durable `.tasks/` artifacts. Accepted outcomes are recorded as `design_decisions`; exploratory spike code is not persisted as the plan. |
| Pipeline with Execution Contract gates | Flows automatically but stays under user control — auto-resolve for speed, step-by-step for precision, and hard stops for design/product changes, unsafe commands, missing facts, stale state, or no viable verification seam after governed escalation |
| Audit remains authoritative | Pipeline audit verifies "did we build what we planned" after review-code discovery, delegated fixes, Fix Verification Review, any triggered widening/escalation, and affected package-proof refresh complete. Review-code task-awareness findings are consistency signals, not completeness proof. |
| Feature name inference | The agent reads the conversation and proposes a name — no need to interrupt the flow for something obvious |
| Work packages as delegation unit | Sub-agents are valuable, but each spawn has fixed context cost. Bundling related tasks into substantial packages reduces repeated codebase exploration while preserving parallelism for independent workstreams. |
| One decision at a time | Reviewer findings that change what ships are presented as individual decision cards (recommendation + alternatives + tradeoffs). For review-code, decision cards are limited to confirmed serious findings with multiple materially different fix approaches; blanket mode does not bypass security/privacy/safety sniffing, Skeptic verification, or stale-state gates. |

---

## License

MIT
