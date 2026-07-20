# Converging Delivery Loop — Design Spec

Status: Accepted (design)
Date: 2026-07-20
Supersedes intent of: PR #58 "bounded agentic delivery harness" (left open, not merged)
Baseline: `main`

## Problem

The `implement → verify → repair` loop churns through many iterations and often
bounces work back to the user. Root cause is **strictness that never proved the
software works**:

1. The package verifier hard-FAILs on *paperwork* — proof Markdown, deliverable
   matrix, Test Review Scope receipt grammar — not just on code defects. The loop
   optimizes documents, not software.
2. A freshness cascade re-stales everything on every fix ("any frozen-input change
   invalidates it"), so one small repair forces re-documentation and re-verification
   of the whole package. O(n²) rework.
3. Multiple adversarial passes (package verifier, `review-code`, `audit`) each
   "challenge completeness" with no shared, closed definition of done — goalposts
   move every iteration, so reviewers never converge to CLEAN.
4. No severity bar: near-everything blocks. Advisory nits are treated as must-fix.
   (Agents literally reported the pipeline as "too strict.")
5. Fresh agents each iteration lose memory and re-litigate settled decisions.
6. The contracts themselves are dense 800-line walls; an LLM applies them maximally,
   adding strictness and burning context.

PR #58 tried to *force* this churning loop to terminate by adding a
distributed-systems control plane (~9,455-line validator). That is the wrong
direction. The fix is to remove the churn sources, not to add machinery.

## Principle

**Churn comes from opinion gates; assurance comes from evidence gates.**

Remove the subjective gates that never converge (and never proved anything).
Keep and strengthen the objective, executable evidence that does. Result: a loop
that is both faster *and* more trustworthy.

## User journey (unchanged)

conceptualize → plan → **Gate 2 plan approval (human)** → **one auto-resolve
authorization (human)** → autonomous loop → **"done" notification (human)**.

Exactly two human touchpoints before completion. After authorization the loop runs
silently until it either completes or hits a legitimate stop (below).

## Definition of Done (the core change)

### Per-package
A package is **done** iff every one of its plan-frozen **executable checks** passes
with **authentic** evidence. The checklist is:

- **Closed** — derived once from the plan's `Must satisfy` criteria + verification
  expectations, frozen at Gate 2. The verifier checks *exactly this list*, inventing
  nothing.
- **Executable-by-default** — each item maps to a runnable check (test / command /
  observable output). A non-executable item is allowed **only** as an explicit,
  human-approved manual-verification exception recorded at Gate 2. No silent gaps.
- **Binary** — each item pass/fail with a one-line evidence pointer.

### Feature-level (the end-to-end guarantee)
`SPEC.md` MUST contain a `## Acceptance` section authored during planning and approved
at Gate 2: the end-to-end "definition of success" for the whole feature, as executable
checks (same executable-by-default rule). The feature is **delivered** only when this
Acceptance check passes against the fully integrated code. This is the user's guarantee
anchor.

### Evidence authenticity (the one strictness we keep)
The verifier confirms the named checks *actually ran against real code and passed* —
no mocks that hide the behavior, no skipped assertions, no "PASS" prose without output.
Cheap, objective, convergent.

## Severity bar

Findings are classified `blocking` or `advisory`.

- **blocking** = correctness / security / data-loss / contract-break. Only these
  trigger repair.
- **advisory** = everything else (style, maintainability opinions, "could be more
  complete"). Logged in the result, never loops, never blocks done.

## Convergence rules

- **Delta-only re-verification.** After a repair, re-check only the checklist items
  the diff touches + a build/lint/test run. Do not re-verify the whole package or
  feature. Remove "any change invalidates it."
- **Integration review = seams only.** `review-code` inspects cross-package seams and
  contradictions; it does not re-open package-local code unless there is a real
  cross-package contradiction.
- **Audit is finite.** Audit confirms every checklist item has real passing evidence
  and the feature Acceptance check passed. It does not re-derive completeness.
- **Bounded repair.** N attempts per blocking finding-cluster (default N=3). On
  non-convergence → stop and notify the user with a precise summary. No infinite loops.
- **Decisions log.** One append-only note per feature of settled decisions / rejected
  approaches, passed to each fresh agent, so they stop re-litigating.

## Legitimate autonomous-loop stops (only these re-enter the human)

1. Scope / requirements change the plan didn't cover.
2. Missing credentials or external facts the agent cannot invent.
3. Destructive or out-of-contract action (target/main merge, force push, deletion).
4. Non-convergence (circuit breaker tripped).

Everything else — routine failures, repairs, reruns, verification, integration — the
loop handles silently.

## One lightweight result artifact

Collapse proof + verification report + deliverable-completeness matrix + Test Review
Scope receipt + State Binding + Semgrep-evidence into **one** package result file:

- what was built,
- each checklist item → pass / evidence-pointer,
- deferrals (with reason),
- commit ref.

`sliceproof` validates only: plan shape is well-formed, and every checklist item is
accounted for. It gets **smaller**, not bigger — the opposite of PR #58. The elaborate
matrix / receipt / freshness grammar validators are removed.

## Completion notification (the guarantee, in the user's hands)

On completion the user receives: the acceptance checklist (every item → passing, with
evidence pointer) + the feature-level Acceptance result, re-runnable by the user. Nothing
is "done" on an opinion.

## Build phases

- **P1** — Loop convergence: severity bar + closed per-package checklist + kill the
  freshness cascade (delta-only re-verify). Files: `implement/SKILL.md`,
  `implement/references/package-verification.md`, `review-code` (seams-only + severity),
  `audit` (finite checklist confirmation).
- **P2** — Acceptance gate in planning: mandatory `## Acceptance` in SPEC,
  executable-by-default with human-approved exceptions, frozen at Gate 2. Files:
  `implementation-plan`, `review-plan`, `conceptualize` handoff, `spec-template`.
- **P3** — Collapse artifacts into one result file; slim `sliceproof.py` accordingly.
- **P4** — De-jargon and consolidate references; reduce word count and file count.

## Non-goals

- No lifecycle state machine, CAS reservations, budget generations, receipt DAGs, or
  two-phase checkpoint publication (PR #58's machinery). Git-native refs + prose
  self-checks only.
- No increase in `sliceproof.py` scope. It validates artifact shape + checklist
  coverage, nothing more.
