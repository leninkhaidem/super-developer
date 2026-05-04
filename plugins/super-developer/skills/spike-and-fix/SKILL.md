---
name: spike-and-fix
description: >
  Runs disciplined bug diagnosis through an isolated spike, then converts validated evidence into a clean minimal fix. Use when the user reports bugs, troubleshooting needs, regressions, failing tests, "fix this", "broken", or "debug this".
---

# Spike and Fix

Use this for bug reports and regressions where the correct fix is not already proven.
Do not jump to production-code edits before evidence identifies the failing path.

## Quick start

Example invocation: "Debug this failing payment retry test and fix it."

1. Reproduce or use the existing deterministic failing repro.
2. Spike the smallest candidate fix in isolation.
3. Extract a durable regression/spec test.
4. Apply the minimal production fix on a clean bugfix/hotfix branch.
5. Verify, self-audit, optionally invoke `review-code`, then commit the final branch.

## Workflow

### 1. Triage and reproduce

- Treat broad triggers as in-scope: bug reports, troubleshooting, regressions, failing tests, "fix this", "broken", and "debug this".
- For unknown bugs, reproduce the reported symptom before coding. Capture the command, input, environment, logs, trace, screenshot, HAR, or failing case used.
- Minimize the repro when useful: smallest input, scenario, fixture, or test that still fails.
- Generate 3-5 ranked, falsifiable hypotheses with the evidence that would confirm or reject each.
- Fast path only when an existing deterministic failing repro/spec already matches the reported bug.

### 2. Stop when evidence is insufficient

If there is no reliable repro or spike evidence, stop before production-code changes. Ask for the missing artifact: logs, HAR, failing input, environment details, screen recording, or permission to add instrumentation. Do not ship plausible fixes.

### 3. Spike in isolation

- Prefer the `worktree` skill: create an isolated `spike/<name>` branch/worktree when available.
- A spike may contain only a focused spike test/harness plus the minimal candidate fix needed to validate a hypothesis.
- No refactors, cleanup, dependency upgrades, unrelated hardening, formatting sweeps, or opportunistic fixes in the spike.
- If worktrees are unavailable, use the current tree only for small, low-risk fixes. If the current tree is dirty, ask before any spike or final implementation.
- Never auto-stash, reset, discard, or overwrite user changes.

### 4. Escalate before broad coding

Invoke `implementation-plan` before broad implementation when the blast radius crosses module/service boundaries, changes public APIs/schemas/contracts, touches security/data/concurrency/performance-critical paths, lacks a proper test seam, or requires a non-localized patch.

If a minimal isolated spike is feasible, spike first. If the spike itself would be invasive, plan first.

Plan handoff must include: root cause, original repro, minimized failing case, ranked hypotheses, spike evidence, candidate approach, blast-radius reason, regression/spec tests, non-goals, and rollback/cleanup notes.

### 5. Convert spike to clean fix

After spike validation:

1. Create a clean `bugfix/<name>` or `hotfix/<name>` worktree using `worktree` conventions.
2. Do not commit spike work.
3. Convert the spike scenario into a durable regression/spec test or fixture in the appropriate test location.
4. Run that regression/spec test first and confirm it fails for the original reason.
5. Apply the minimal production-code fix.
6. Run the regression/spec test again and confirm it passes.
7. Run the original repro and the smallest affected existing test slice.
8. Run targeted standard checks relevant to touched files.

Verification must exercise the real failing path. Use mocks only for external systems.

### 6. Cleanup, audit, and commit

- Delete throwaway spike artifacts, worktrees, and branches after extracting durable tests/fixtures and summarized evidence.
- Keep only useful captured fixtures/traces under appropriate test fixture paths.
- Self-audit every fix against the repro, root cause, minimality, tests, and cleanup.
- Invoke `review-code` for nontrivial or risky fixes, or whenever the user asks.
- Commit the verified final fix branch after verification.
- Never merge or push without explicit approval.

## Final report

Report only observed facts:

- Original symptom.
- Root cause.
- Spike validation result.
- Final fix summary.
- Regression/spec test added or updated.
- Observed command results.
- Cleanup performed.
- Remaining risks or blockers.
