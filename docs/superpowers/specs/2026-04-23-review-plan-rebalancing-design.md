# Review-Plan Rebalancing: Preventing Over-Engineering

## Problem

The `review-plan` skill has a structural bias toward over-engineering. Agent B (Adversarial Challenger) generates findings that the merge-and-resolve step resolves by addition rather than pushback. The severity resolution rules make it easier to add complexity than to justify rejecting it. Over multiple review rounds, this creates a ratchet effect where plans grow in scope without proportionate quality benefit.

### Root Causes

1. **Agent B proposes without costing.** Findings include a `FIX:` but no assessment of the fix's complexity burden. The orchestrator has no data to weigh proportionality.
2. **No dismissal path for CRITICALs.** Current options are "accept with documented rationale" or "revise the plan." Justifying rejection requires more effort than adding the thing — so the thing gets added.
3. **CONTEXT.md cap doesn't budget for review additions.** The 50-line hard cap was set for initial creation. Review legitimately adds Design Decisions entries, but has no headroom.
4. **Agent A doesn't verify plan quality standards.** The `implementation-plan` skill defines authoring rules (description budget, anti-patterns, independence test) but Agent A only checks structural completeness, not conformance to these rules.

## Design

### Change A: Agent B — Cost-of-Proposal Requirement

Add a mandatory `COST:` line to Agent B's output format for `[BLOCKER]` and `[CRITICAL]` findings:

```
[SEV] TARGET — TITLE
ISSUE: <what's wrong>
FIX: <concrete resolution>
COST: <complexity burden — new dependencies, additional tasks, maintenance surface, or "minimal" if trivial>
```

Rules:
- `COST:` is required for `[BLOCKER]` and `[CRITICAL]`, optional for `[SUGGESTION]`.
- Must be specific: "adds 2 tasks, new caching dependency, invalidation logic" — not "some complexity."
- The orchestrator uses `COST:` during merge-and-resolve to weigh whether the fix is proportionate to the risk.

This does not suppress findings or reduce Agent B's aggression. It makes Agent B accountable for the cost of its own advice.

### Change B: Merge-and-Resolve — Over-Engineering Dismissal Path

Add a third resolution option for `[CRITICAL]` findings in Step 5:

> **`[CRITICAL]` findings:** Either (a) provide documented rationale and record it in CONTEXT.md under "Design Decisions", (b) accept the alternative and revise the plan, OR **(c) dismiss as disproportionate — the fix's complexity cost exceeds the risk it addresses. Record a one-line justification in the review summary.**

Rules:
- Dismissal requires referencing the finding's `COST:` line — the orchestrator must explain why the cost outweighs the risk.
- Dismissed findings are logged, not silently dropped. They appear in the Gate 2 summary with a `← dismissed (disproportionate)` marker.
- A dismissed CRITICAL does not trigger a re-review round — it is considered resolved.
- `[BLOCKER]` findings cannot be dismissed. Only `[CRITICAL]` findings get this path.

This breaks the "easier to add than justify" bias by providing a lightweight rejection mechanism.

### Change C: CONTEXT.md Tiered Cap

Replace the current hard cap in `implementation-plan` Step 3:

**Before:** "Hard constraint: CONTEXT.md must not exceed 50 lines."

**After:** "Hard constraint: CONTEXT.md must not exceed **50 lines** at initial creation. After review-plan processing, the post-review cap is **75 lines** to accommodate design decisions and rationale added during review."

Enforcement points:
- `implementation-plan` Step 5 (validation): checks ≤50 lines.
- `review-plan` Step 5 (merge-and-resolve): when adding Design Decisions to CONTEXT.md, checks ≤75 lines. If a review addition would breach 75, the orchestrator must compress existing content before adding.

25 additional lines accommodates ~5-8 design decision entries with rationale.

### Change D: Agent A — Plan Conformance Check

Add a 7th check to Agent A's mandate — **Plan conformance** — verifying tasks against `implementation-plan`'s authoring standards:

- **Independence test:** Each task has a self-contained, verifiable outcome. A reviewer can verify the task's acceptance criteria without seeing any other task.
- **Description quality:** States WHAT to build and key constraints, not HOW to code it.
- **Description budget:** 200-400 characters target. Flag descriptions exceeding 600 characters as likely over-specification.
- **Anti-pattern scan:** No code snippets, line numbers, step-by-step implementation instructions, or library prescriptions (unless security-mandated).
- **No-duplication:** Task descriptions do not repeat content already in CONTEXT.md.
- **Acceptance criteria format:** Criteria describe verifiable behavioral outcomes, not implementation details.

Severity guidance:
- Independence test failures → `[BLOCKER]` (non-independent tasks cannot be verified).
- Description budget violations (>600 chars) → `[CRITICAL]` (over-specification constrains implementing agents).
- Anti-pattern violations → `[CRITICAL]` (same reason).
- Others → Agent A's judgment.

## Files Affected

| File | Changes |
|---|---|
| `plugins/super-developer/skills/review-plan/SKILL.md` | A (Agent B COST line), B (dismissal path), D (Agent A conformance check) |
| `plugins/super-developer/skills/implementation-plan/SKILL.md` | C (tiered cap) |

## Decisions

- **Agent B stays aggressive.** The fix is accountability (COST line), not suppression. An adversarial reviewer that self-censors defeats its purpose.
- **Re-review loop unchanged.** The existing early-exit condition (zero BLOCKERs, all CRITICALs resolved) is sufficient. The dismissal path prevents new CRITICALs from compounding across rounds.
- **Agent A's existing 6 checks unchanged.** The new plan conformance check is additive — it doesn't modify existing behavior.
- **No new agents or audit steps.** The three-agent panel and post-review scope audit approaches were considered and rejected as disproportionate to the problem.

## Out of Scope

- Changes to the `perspectives` skill (its Skeptic runs once, no re-review loop — lower over-engineering risk).
- Changes to Agent B's adversarial mandate or severity thresholds.
- Changes to the model selection logic in `model-preferences.md`.
- Changes to Gate 1 or Gate 2 mechanics.
