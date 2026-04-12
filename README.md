# Super Developer

A Claude Code plugin that orchestrates the full development lifecycle — from divergent ideation through structured planning, parallel implementation with git worktree isolation, and multi-agent adversarial code review.

One plugin. Seven skills. Zero manual git juggling.

---

## What It Does

Super Developer turns Claude Code into an opinionated development workflow engine. Instead of scattered slash commands and ad-hoc prompts, it provides a structured pipeline where each stage feeds the next — with parallel sub-agents doing the heavy lifting and adversarial review gates catching issues before they ship.

```
[perspectives]        Optional — divergent problem-solving for complex decisions
      |
      v
    plan  --->  review-plan  --->  implement  --->  [audit]  --->  review-code
                     |                  |                               |
              2 adversarial       git worktrees +               4 specialists +
              review agents      parallel sub-agents            Skeptic agent
```

The pipeline flows automatically with confirmation gates. Say **"proceed through all stages"** and it runs end-to-end without stopping. Or invoke any skill independently — they work standalone too.

---

## Skills

### Pipeline Skills

| Skill | What It Does |
|---|---|
| **plan** | Converts a brainstorming session or design discussion into a structured task plan under `.tasks/<feature>/` with `CONTEXT.md` and `tasks.json`. Infers the feature name from context — no need to provide one. |
| **review-plan** | Design review gate. Spawns two Opus-class sub-agents in parallel — a **Completeness Reviewer** and an **Adversarial Design Challenger** — to validate the plan cold from files only. Re-reviews until both approve (max 3 rounds). |
| **implement** | Orchestrator. Analyzes the dependency graph, creates git worktrees for each task, spawns parallel Opus-class sub-agents to write code, merges completed work into the feature branch, and loops until all tasks are done. The main agent manages all git infrastructure; sub-agents only write code. |
| **review-code** | Multi-agent code review. Spawns 4 specialist agents (Security, Logic, Performance, Architecture) in parallel, then an adversarial **Skeptic Agent** that independently tries to disprove every serious finding using a 6-point false-positive checklist. Works in 3 modes: pipeline (feature branch), GitHub PR, or local changes. |

### Standalone Skills

| Skill | What It Does |
|---|---|
| **perspectives** | Divergent problem-solving. Spawns 3-5 Opus-class sub-agents, each approaching the problem from a distinct angle (Infrastructure, Architecture, Data, Root Cause, etc.). A final Skeptic agent stress-tests and synthesizes proposals into a ranked recommendation. |
| **tasks** | Implementation status dashboard. Shows progress across all features or drills into a specific one with phase-by-phase breakdown. Can modify task status on request. |
| **audit** | Post-implementation verification. Spawns a read-only sub-agent that checks every acceptance criterion against the actual codebase. Produces a PASS/FAIL report. Optional in the pipeline — skipped unless explicitly requested. |

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

See [`references/git-worktree-strategy.md`](references/git-worktree-strategy.md) for the complete workflow including bugfix, hotfix, and multi-phase dependency handling.

---

## Installation

### Option 1: Clone and use directly

```bash
git clone https://github.com/leninkhaidem/super-developer.git
claude --plugin-dir /path/to/super-developer
```

### Option 2: Add to your project

```bash
# From your project directory
claude --plugin-dir /path/to/super-developer
```

The plugin loads all 7 skills automatically via Claude Code's auto-discovery mechanism. No configuration required.

---

## Usage

### Full Pipeline

Start a conversation, discuss what you want to build, then:

```
> Plan this feature
```

The agent infers the feature name, creates the task plan, and asks to continue. Say **"proceed through all stages"** to run the full pipeline end-to-end, or confirm each step individually.

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
| "Plan this feature" | Creates plan, asks to continue |
| "Proceed through all stages" | Runs plan -> review-plan -> implement -> review-code without stopping |
| "Include audit" | Adds the optional audit step before code review |
| Confirm at each gate | Step-by-step control over the pipeline |

---

## Plugin Structure

```
super-developer/
+-- .claude-plugin/
|   +-- plugin.json                     # Plugin manifest
+-- references/
|   +-- git-worktree-strategy.md        # Shared git workflow reference
+-- skills/
|   +-- perspectives/
|   |   +-- SKILL.md                    # Divergent problem-solving
|   +-- plan/
|   |   +-- SKILL.md                    # Discussion -> structured tasks
|   +-- review-plan/
|   |   +-- SKILL.md                    # Design review gate
|   +-- tasks/
|   |   +-- SKILL.md                    # Status dashboard
|   +-- implement/
|   |   +-- SKILL.md                    # Orchestrator + git worktrees
|   +-- audit/
|   |   +-- SKILL.md                    # Post-implementation verification
|   +-- review-code/
|       +-- SKILL.md                    # Multi-agent code review
|       +-- references/
|           +-- pr-workflow.md          # GitHub PR review workflow
|           +-- local-workflow.md       # Local code review workflow
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
| Adversarial review at every gate | Completeness + Challenger for plans, 4 specialists + Skeptic for code — false positives are filtered, not just flagged |
| Git worktree isolation | Parallel sub-agents work in separate worktrees — no branch switching, no merge conflicts during implementation |
| Pipeline with confirmation gates | Flows automatically but stays under user control — blanket approval for speed, step-by-step for precision |
| Audit is optional | Not every feature needs formal verification — skip it by default, invoke when thoroughness matters |
| Feature name inference | The agent reads the conversation and proposes a name — no need to interrupt the flow for something obvious |

---

## License

MIT
