# Super Developer

A Claude Code plugin that orchestrates the full development lifecycle — from divergent ideation through requirements-spec-driven planning, parallel implementation with git worktree isolation, and multi-agent adversarial code review.

One plugin. Eight skills. Zero manual git juggling.

---

## What It Does

Super Developer turns Claude Code into an opinionated development workflow engine. Instead of scattered slash commands and ad-hoc prompts, it provides a structured pipeline where each stage feeds the next — with right-sized sub-agent work packages, git worktree isolation, and adversarial review gates catching issues before they ship.

```
[perspectives]              Optional — divergent problem-solving for complex decisions
       |
       v
  implementation-plan  --->  review-plan  --->  implement  --->  audit  --->  review-code
                     |                  |              |               |
              1–2 reviewers       work-package      verify vs       4 specialists +
              (adaptive)          dispatch          plan            Skeptic agent
```

The pipeline flows automatically with confirmation gates. Say **"proceed through all stages"** and it runs end-to-end without stopping. Or invoke any skill independently — they work standalone too.

---

## Skills

| Skill | What It Does | Usage |
|---|---|---|
| **perspectives** | Divergent problem-solving. Spawns 3-5 Opus-class sub-agents, each approaching the problem from a distinct angle (Infrastructure, Architecture, Data, Root Cause, etc.). A final Skeptic agent stress-tests and synthesizes proposals into a ranked recommendation. | Standalone |
| **implementation-plan** | Converts a completed brainstorming or requirements discussion into a structured task plan under `.tasks/<feature>/` with `SPEC.md`, task-level acceptance criteria, and work packages that define right-sized implementation delegation. | Pipeline + Standalone |
| **review-plan** | Plan review gate. Performs deterministic schema validation, then spawns a **Plan Quality Reviewer**; escalates to an **Adversarial Plan Challenger** for high-risk or ambiguous plans. Validates `SPEC.md` and `tasks.json` cold from files only. Re-reviews adaptively (max 3 semantic rounds). Findings that change what ships — or are tagged security/privacy/safety — are presented one decision card at a time; the rest are auto-applied at the reviewer's recommendation and surfaced in the Gate 2 summary. | Pipeline + Standalone |
| **tasks** | Implementation status dashboard. Shows progress across all features or drills into a specific one with phase-by-phase breakdown. Can modify task status on request. | Standalone |
| **implement** | Orchestrator. Analyzes planned work packages, creates git worktrees per package, dispatches substantial coherent packages to sub-agents, merges package branches into the feature branch, and runs lightweight integration checkpoints before downstream work begins. | Pipeline + Standalone |
| **audit** | Post-implementation verification. Spawns a read-only sub-agent that checks every acceptance criterion against the actual codebase. Produces a PASS/FAIL report. Always runs in the pipeline after implement; also invocable standalone. | Pipeline + Standalone |
| **review-code** | Multi-agent code review. Spawns 4 specialist agents (Security, Logic, Performance, Architecture) in parallel, then an adversarial **Skeptic Agent** that independently tries to disprove every serious finding using a 6-point false-positive checklist. Under blanket pipeline mode, the `fix` action prompts only when a finding has multiple valid fix approaches with different runtime behavior; all other fixes apply silently. Local mode preserves per-fix `yes/skip` semantics. | Pipeline + Standalone + PR review |
| **code-doc** | Generate comprehensive documentation for any codebase via hybrid analysis (native extractors + LLM agents). Adaptive 8-step pipeline: Scout → Existing Doc Assessment → Doc Plan → Analyze (delegate to sub-agents) → Synthesize → User Checkpoint → Generate (fan-out doc writers) → Review & Commit. Outputs 4 core docs (README, architecture-guide, developer-guide, codebase-context) plus optional docs (api-reference, data-model, component-guide, infrastructure). | Standalone |

`review-code` works in **3 modes** — it auto-detects which to use:

| Mode | When | What it reviews |
|---|---|---|
| **Pipeline** | After `implement` completes in the same session | Feature branch diff against `main` from the merge worktree |
| **PR** | You provide a PR identifier (`owner/repo#42`, URL, or `#42`) | Full PR diff from GitHub via `gh` CLI |
| **Local** | No pipeline context, no PR identifier | Staged changes, unstaged changes, or branch diff (auto-detected) |

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

See [`skills/worktree/SKILL.md`](skills/worktree/SKILL.md) for the complete workflow including bugfix, hotfix, and multi-phase dependency handling.

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

The plugin loads all 8 skills automatically via Claude Code's auto-discovery mechanism. No configuration required. Run `/reload-plugins` after installation to activate without restarting.

---

## Usage

### Full Pipeline

Start a conversation, discuss what you want to build, then:

```
> Plan this feature
```

The agent infers the feature name, creates `SPEC.md` and `tasks.json`, and asks to continue. Say **"proceed through all stages"** to run the full pipeline end-to-end, or confirm each step individually.

### Individual Skills

```
> Get me some perspectives on this architecture decision
> Show me the task status
> Review this PR: owner/repo#42
> Review my code
> Audit the auth-system feature
```

### Pipeline Flow Control

| What you say | What happens |
|---|---|
| "Plan this feature" | Creates `SPEC.md` and `tasks.json`, asks to continue |
| "Proceed through all stages" | Runs implementation-plan -> review-plan -> implement -> audit -> review-code without stopping |
| "Skip audit" | Skips the audit step (included by default in the pipeline) |
| Confirm at each gate | Step-by-step control over the pipeline |

---

## Plugin Structure

```
super-developer/
+-- .claude-plugin/
|   +-- plugin.json                     # Plugin manifest
+-- references/
|   +-- clean-code-rules.md               # Code quality rules
|   +-- model-preferences.md              # Sub-agent model selection schema
|   +-- work-packages.md                  # Work-package delegation contract
|   +-- decision-prompts.md               # Decision-card UX mechanics (review-plan + review-code)
+-- skills/
|   +-- worktree/
|   |   +-- SKILL.md                       # Git worktree strategy
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
```

---

## Requirements

- **Claude Code** with plugin support
- **git** (all skills)
- **GitHub CLI (`gh`)** (review-code PR mode only) — [install](https://cli.github.com/)

---

## Key Design Decisions

| Decision | Rationale |
|---|---|
| Main agent orchestrates, sub-agents implement | Separation of concerns — orchestrator manages git state, sub-agents write code without risk of infrastructure conflicts |
| Adaptive adversarial review | Plan Quality Reviewer always; Adversarial Plan Challenger escalates on risk. Code review pairs 4 specialists with a Skeptic agent — false positives are filtered, not just flagged. |
| Git worktree isolation | Parallel sub-agents work in separate worktrees — no branch switching, no merge conflicts during implementation |
| Pipeline with confirmation gates | Flows automatically but stays under user control — blanket approval for speed, step-by-step for precision |
| Audit always runs in pipeline | Verifies "did we build what we planned" before code review begins — standalone review-code skips it |
| Feature name inference | The agent reads the conversation and proposes a name — no need to interrupt the flow for something obvious |
| Work packages as delegation unit | Sub-agents are valuable, but each spawn has fixed context cost. Bundling related tasks into substantial packages reduces repeated codebase exploration while preserving parallelism for independent workstreams. |
| One decision at a time | Reviewer findings that change what ships are presented as individual decision cards (recommendation + alternatives + tradeoffs); wording, traceability, and scheduling fixes auto-apply at the reviewer's recommendation and surface in the post-review summary. Cuts overwhelm without losing audit trust. |

---

## License

MIT
