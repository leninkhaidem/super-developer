---
name: spike-to-plan
description: Runs a bounded feasibility spike before implementation planning, discards exploratory code, and hands observed evidence to implementation-plan. Use when planning depends on uncertain API/library behavior, integration feasibility, performance/concurrency risk, data-model/UX uncertainty, or an explicit spike/prototype request. Do not use for routine implementation or code review.
---

# Spike to Plan

Answer the smallest empirical question needed to make a reliable greenfield implementation plan.

## Always

- Treat spike code as disposable evidence, not production implementation.
- Prefer repo/docs/official API evidence before writing exploratory code.
- Keep the spike isolated, bounded, reversible, and focused on one planning assumption.
- Preserve user work: do not stash, reset, overwrite, or discard dirty changes without approval.
- Do not persist exploratory code as planned-feature artifacts.
- Accepted outcomes that affect planning must remain durable through `SPEC.md` constraints/non-goals, package Markdown notes/verification expectations, Slice approval/deferral notes, or registry bookkeeping.

## Do

1. State the planning assumption, success/failure evidence, constraints, and non-goals.
2. Inspect existing code, tests, docs, and authoritative library/API docs first.
3. Spike only if the assumption remains material and unresolved.
4. Use an isolated temporary branch/worktree when practical; use the current tree only for small low-risk probes with a clean or user-approved state.
5. Run the minimum commands/scenarios/measurements needed to accept or reject the assumption.
6. Delete throwaway code, temporary harnesses, branches, and worktrees after extracting evidence.
7. Hand concise observed evidence to `implementation-plan`.

## Handoff to Implementation Plan

Return a spike brief with:

- planning question answered or still blocked;
- evidence sources, commands, scenarios, measurements, traces, screenshots, or fixtures used;
- observed result, including failed or rejected approaches;
- recommended planning direction and why evidence supports it;
- remaining risks and package verification expectations;
- durable planning destinations: `SPEC.md`, package Markdown, Slice approval/deferral notes, or registry bookkeeping;
- cleanup performed and any preserved fixture/repro artifact.

## Stop if

- Evidence is insufficient to recommend a direction.
- External access, credentials, production data, paid services, or unsafe commands are required.
- The spike would require invasive production changes, broad refactors, dependency upgrades, or public contract changes.
- Dirty worktree state prevents safe isolation and the user has not approved a current-tree probe.
- A planning decision changes product behavior, risk acceptance, or scope and needs user approval.

## Output

Report observed facts only, then either hand off to `implementation-plan` with the spike brief or state the exact blocker.
