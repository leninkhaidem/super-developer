---
name: spike-to-plan
description: >
  Runs an empirical feasibility spike for uncertain feature work, discards exploratory code, and hands observed evidence to implementation-plan. Use when planning depends on an unverified assumption or the user mentions uncertain feature work, feasibility spike, prototype before planning, validate approach, integration unknown, performance/concurrency risk, API/library behavior unknown, or UX/data-model uncertainty.
---

# Spike to Plan

Use this when a feature plan depends on a risky assumption that docs or code inspection cannot verify.
Do not build production features directly: spike code is evidence, not implementation.

## Quick start

Example invocation: "Before planning offline sync, run a feasibility spike to validate the conflict-resolution approach."

1. Clarify the behavior and success criteria.
2. Identify the single planning assumption to test.
3. Prefer codebase/docs evidence; spike only if the question remains unresolved.
4. Run a bounded isolated spike, then delete throwaway code.
5. Hand observed evidence to `implementation-plan`.

## Workflow

### 1. Frame the planning question

- Clarify desired behavior, acceptance criteria, constraints, and non-goals.
- State the exact question or assumption blocking a reliable implementation plan.
- Do not spike routine, low-risk work that can be planned from existing facts.
- Define the smallest evidence that would confirm or reject the assumption.

### 2. Exhaust non-code evidence first

- Explore the codebase, existing tests, docs, official library/API documentation, and prior project decisions when tools can answer the question.
- If non-code evidence resolves the assumption, skip the spike and proceed directly to `implementation-plan` with citations to observed facts.
- Mark guesses as unresolved; do not turn plausible assumptions into plan decisions.

### 3. Spike in isolation only when needed

- Prefer the `worktree` skill: create a temporary `spike/<name>` branch/worktree using project conventions when available.
- Current-tree fallback is allowed only for small, low-risk spikes.
- If the current tree is dirty, ask before spiking. Never auto-stash, reset, discard, or overwrite user changes.
- Limit spike scope to answering the planning question.
- No production implementation, broad refactors, dependency upgrades, public contract changes, formatting sweeps, or unrelated cleanup.

### 4. Capture evidence

Record a concise spike brief for handoff, not as a durable project file:

- Planning question / assumption.
- Approach and why it was bounded.
- Files inspected or temporarily changed.
- Commands, scenarios, measurements, screenshots, traces, or fixtures used.
- Observed results, including failed or rejected approaches.
- Recommended direction and why the evidence supports it.
- Remaining risks and what must be tested during implementation.
- Acceptance criteria or task implications for the future plan.

### 5. Clean up spike artifacts

- Delete throwaway spike code, temporary harnesses, branches, and worktrees after extracting evidence.
- Preserve only useful fixtures, traces, or minimal repro artifacts when they are needed by the future plan and belong in a stable project location.
- Do not commit or ship exploratory spike code.

### 6. Hand off to implementation-plan

- Invoke or hand off to `implementation-plan` after evidence is sufficient.
- Persist accepted decisions in `design_decisions`; do not persist the spike brief or exploratory code as plan artifacts.
- Include rejected approaches and remaining risks so the plan can create targeted tasks and verification.

## Stop conditions

Stop and ask before continuing when:

- Evidence is insufficient to recommend a direction.
- External access, credentials, production data, or paid services are required.
- The spike would require invasive production changes, broad refactors, dependency upgrades, or changes to shared contracts.
- The dirty current tree prevents a safe isolated spike and no worktree option is available.

## Final report

Report only observed facts:

- Planning question answered or still blocked.
- Evidence gathered and commands/scenarios run.
- Recommended planning direction.
- Rejected approaches.
- Cleanup performed.
- Next `implementation-plan` handoff or blocker.
