# Super Developer

A Claude Code plugin that orchestrates the full development lifecycle — from divergent ideation through requirements-spec-driven planning, parallel implementation with git worktree isolation, and multi-agent adversarial code review.

One plugin. Eight skills. Zero manual git juggling.

---

## What It Does

Super Developer turns Claude Code into an opinionated development workflow engine. Instead of scattered slash commands and ad-hoc prompts, it provides a structured pipeline where each stage feeds the next — with parallel sub-agents doing the heavy lifting and adversarial review gates catching issues before they ship.

```
[perspectives]              Optional — divergent problem-solving for complex decisions
       |
       v
  implementation-plan  --->  review-plan  --->  implement  --->  audit  --->  review-code
                     |                  |              |               |
              2 adversarial       git worktrees +  verify vs     4 specialists +
              review agents      parallel agents    plan         Skeptic agent
```

The pipeline flows automatically with confirmation gates. Say **"proceed through all stages"** and it runs end-to-end without stopping. Or invoke any skill independently — they work standalone too.

---

## Skills

| Skill | What It Does | Usage |
|---|---|---|
| **perspectives** | Divergent problem-solving. Spawns 3-5 Opus-class sub-agents, each approaching the problem from a distinct angle (Infrastructure, Architecture, Data, Root Cause, etc.). A final Skeptic agent stress-tests and synthesizes proposals into a ranked recommendation. | Standalone |
| **implementation-plan** | Converts a completed brainstorming or requirements discussion into a structured task plan under `.tasks/<feature>/` with `SPEC.md` and `tasks.json`. Infers the feature name from context — no need to provide one. | Pipeline + Standalone |
| **review-plan** | Plan review gate. Spawns two review sub-agents in parallel — a **Completeness Reviewer** and an **Adversarial Plan Challenger** — to validate `SPEC.md` and `tasks.json` cold from files only. Re-reviews until both approve (max 3 rounds). | Pipeline + Standalone |
| **tasks** | Implementation status dashboard. Shows progress across all features or drills into a specific one with phase-by-phase breakdown. Can modify task status on request. | Standalone |
| **implement** | Orchestrator. Analyzes the dependency graph, creates git worktrees for each task, spawns parallel Opus-class sub-agents to write code, merges completed work into the feature branch, and loops until all tasks are done. The main agent manages all git infrastructure; sub-agents only write code. | Pipeline + Standalone |
| **audit** | Post-implementation verification. Spawns a read-only sub-agent that checks every acceptance criterion against the actual codebase. Produces a PASS/FAIL report. Always runs in the pipeline after implement; also invocable standalone. | Pipeline + Standalone |
| **review-code** | Multi-agent code review. Spawns 4 specialist agents (Security, Logic, Performance, Architecture) in parallel, then an adversarial **Skeptic Agent** that independently tries to disprove every serious finding using a 6-point false-positive checklist. | Pipeline + Standalone + PR review |
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
- **All development happens in `.worktrees/`.** Each task gets its own worktree. Independent tasks run in parallel; dependent tasks branch from the feature ref.
- **The orchestrator owns git.** Sub-agents receive a worktree path and task instructions — they write code and commit, nothing else. The orchestrator creates worktrees, merges branches, verifies with `merge-base --is-ancestor`, and cleans up.
- **Feature branches are refs, not worktrees.** This keeps them unlocked for merging from any worktree.
- **Merge to main requires explicit approval.** "Push to remote" does not mean "merge to main."

```
project/                              <- always on 'main'
+-- .worktrees/
|   +-- auth/
|   |   +-- task-login/               <- branch: task/auth/login
|   |   +-- task-signup/              <- branch: task/auth/signup
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
| Adversarial review at every gate | Completeness + Plan Challenger for plans, 4 specialists + Skeptic for code — false positives are filtered, not just flagged |
| Git worktree isolation | Parallel sub-agents work in separate worktrees — no branch switching, no merge conflicts during implementation |
| Pipeline with confirmation gates | Flows automatically but stays under user control — blanket approval for speed, step-by-step for precision |
| Audit always runs in pipeline | Verifies "did we build what we planned" before code review begins — standalone review-code skips it |
| Feature name inference | The agent reads the conversation and proposes a name — no need to interrupt the flow for something obvious |

---

## License

MIT
