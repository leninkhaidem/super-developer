---
name: diagnose-and-fix
description: >
  Diagnoses reported issues evidence-first, returns structured findings for explicit approval, then
  routes approved fixes through isolated worktree bugfix/hotfix workflow or implementation-plan.
  Use when the user reports a bug, broken behavior, regression, failing test, troubleshooting,
  debugging, or asks to "fix this". Do not use for planned feature development, ordinary code
  review, documentation, release work, or speculative cleanup.
---

# Diagnose and Fix

Diagnose first, ask approval second, and fix only after the user accepts the route. This is the
single maintained bug diagnosis/fix workflow.

## Always

- Treat issue reports, regressions, failures, broken behavior, "debug this", and "fix this" as
  diagnosis-first. Initial wording is not approval to modify production code.
- Do not edit production code, create fix branches, or commit before a structured diagnosis report
  and explicit user approval.
- Prefer observed evidence over plausible guesses: reproduce the failing path or clearly state
  `not reproduced`, `already covered by deterministic failing test`, or `blocked`.
- Keep the root worktree user-owned. Use `worktree` for approved diagnostic spike, bugfix, or
  hotfix work; never switch the root worktree branch.
- Delegate approved localized fix implementation to a fresh Fix Implementer sub-agent bound to the
  approved worktree, diagnosis packet, and regression plan; the main agent orchestrates and verifies.
- Do not ship plausible fixes. Prove the root cause enough for the chosen route, or name uncertainty
  and ask for the missing artifact, permission, or risk acceptance.
- Keep scope minimal: no unrelated refactors, dependency upgrades, formatting sweeps, broad
  hardening, or opportunistic fixes.
- Escalate broad/risky fixes to `implementation-plan` instead of direct coding.
- Never merge, push, delete branches/worktrees, reset, stash, discard user changes, or run external
  side-effecting commands without explicit approval.

## Do

1. Intake the report: restate the symptom, expected behavior, observed behavior, affected surface,
   candidate base ref/context, and any supplied logs, traces, screenshots, HARs, inputs, or tests.
2. Gather evidence before asking the user when repo inspection or safe commands can answer. Run the
   smallest useful repro/test, inspect relevant files/symbols, and capture exact commands/results.
3. If diagnosis needs temporary instrumentation, candidate-fix validation, credentials, network
   side effects, or non-read-only changes, stop and ask approval for that diagnostic action first.
   Approved diagnostic spikes must use `worktree`, stay throwaway, and never become final history.
4. Generate 3-5 ranked, falsifiable hypotheses. For each material branch, record what evidence
   confirmed, rejected, or left it unresolved.
5. Minimize the failing case when useful: smallest input, scenario, fixture, test, or command that
   still demonstrates the issue. If reproduction fails, report what was attempted and what artifact
   is needed next.
6. Before any production-code fix work, present the structured diagnosis report:
   - original symptom or user-reported issue;
   - reproduction status: reproduced, not reproduced, deterministic failing test, or blocked;
   - evidence gathered: commands, logs, traces, inputs, files/symbols, or unavailable evidence;
   - ranked hypotheses with confidence and confirm/reject evidence;
   - likely root cause, or explicit uncertainty if not proven;
   - blast radius and risk: localized or broad/risky;
   - recommended route: stop for more info, localized `worktree` fix, or `implementation-plan`;
   - proposed fix strategy plus non-goals/guardrails;
   - regression/spec test and verification plan;
   - approval options before production-code changes.
7. Ask for one explicit approval choice. Do not treat silence, prior "fix this" wording, or a bug
   report as approval. Valid choices are: provide missing info, approve localized fix, approve
   planning escalation, approve a named diagnostic spike, or stop.
8. If a localized fix is approved, invoke/use `worktree` for a `bugfix/<name>` or `hotfix/<name>`
   branch/worktree from the context that exhibits the bug. Then dispatch a fresh Fix Implementer
   sub-agent with the diagnosis report, approved scope, target worktree/path, branch/ref context,
   repro, fix strategy, regression plan, required checks, and forbidden unrelated work. The Fix
   Implementer edits only inside the target worktree and must:
   - convert the repro into a durable regression/spec test or fixture;
   - confirm the regression fails for the original reason before the fix when practical;
   - apply the minimal production fix;
   - rerun the regression, original repro, smallest affected existing test slice, and targeted
     standard checks relevant to touched files;
   - report changed files, commands/results, unresolved blockers, and remaining risks.
   The main agent verifies the Fix Implementer report against the approved route and commits only
   when the approved fix workflow includes a commit or the user asks for one.
9. If the fix is broad/risky, invoke `implementation-plan` through a fresh Skill-tool/sub-agent
   packet and do not plan inline. The handoff must include symptom, repro, evidence, hypotheses,
   likely root cause or uncertainty, blast-radius reason, proposed strategy, tests, non-goals,
   rollback/cleanup notes, and any approved deferrals or risk acceptance.
10. For nontrivial or risky fixes, or whenever the user asks, invoke `review-code` through a fresh
    Skill-tool/sub-agent packet after verification; do not run review inline.
11. Clean up only approved throwaway diagnostic artifacts. Keep useful fixtures/traces in appropriate
    test fixture paths. Do not remove worktrees/branches without the relevant `worktree` cleanup gate.
12. Final-report only observed facts: symptom, repro status, root cause or uncertainty, route chosen,
    fix summary if any, tests/fixtures changed, command results, cleanup performed, and remaining
    risks or blockers.

## Load if needed

- Worktree creation, diagnostic spike, bugfix/hotfix branch, or cleanup commands are needed → invoke
  `worktree`; that skill owns its command references and approval boundaries.
- Substantive localized fix edits are needed after approval and worktree setup → dispatch a fresh Fix
  Implementer sub-agent with the bounded packet from step 8; do not implement those edits inline.
- Diagnosis shows broad/risky implementation is required → invoke `implementation-plan` with the
  diagnosis packet; do not create `.tasks/` artifacts inline.
- Independent review is requested or risk warrants it → invoke `review-code` after verification.
- A planned-feature package, PR review, documentation, release, or feature feasibility spike is the
  actual task → use the owning skill instead of this one.

## Stop if

- The issue cannot be reproduced or diagnosed with available evidence and the next needed artifact,
  diagnostic action, or risk acceptance requires user input.
- The user has not approved production-code fix work after the structured diagnosis report.
- The current tree is dirty or branch/worktree/base-ref context is ambiguous and proceeding could
  overwrite, hide, or mix user changes.
- A localized fix would cross module/service boundaries, change public APIs/schemas/contracts, touch
  security/data/concurrency/performance-critical paths, lack a clean test seam, or require a
  non-localized patch without `implementation-plan` approval.
- Required commands need credentials, network/external side effects, destructive git actions, or
  unsafe environment changes that have not been explicitly approved.
- The requested scope includes unrelated cleanup, refactors, upgrades, or hardening beyond the
  diagnosed issue.

## Output

Return the structured diagnosis report before approval. After approved fix work, return the final
observed-facts report, Fix Implementer report summary when used, commands run and results, route
taken, changed tests/fixtures, cleanup status, remaining risks/blockers, and the next approval
boundary such as review, merge, push, or cleanup.
