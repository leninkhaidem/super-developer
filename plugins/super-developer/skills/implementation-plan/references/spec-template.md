# SPEC.md Template and Purity Rules

`SPEC.md` is concise product authority plus the reviewed planning proposal. It is not package proof, test inventory,
architecture debate, implementation transcript, lifecycle ledger, or a replacement for authoritative Slices.

## Template

```markdown
# <Feature Name> Specification

## Overview
<user goal and intended outcome>

## Accepted Source Baseline
<sanitized lossless request and follow-on/out-of-scope boundaries; or `None beyond requirements below.`>

## Conceptualize Inputs
- Index: `.planning/<concept-slug>/index.md`
- Or `None.`

## Authoritative Slices
- `.planning/<concept-slug>/slices/<slice-name>.md`
- Or `None; Index-only/no-Slice plan.`

## Human Authorization Envelope
- Outcomes and acceptance: <stable REQ/AC references plus any user-owned summary>
- Product and interface invariants: <fixed public/product choices, defaults, errors, compatibility>
- Constraints and exclusions: <stable constraint/out-of-scope references>
- Accepted material risks and protected effects: <explicit decisions or none>
- Spending/command/time bounds: <finite user-owned bounds>

## Requirements
- REQ-1: ...

## Acceptance Criteria
- AC-1: ...

## Constraints
<non-negotiable user constraints, compatibility/security/performance policy, and approved scope limits>

## Architecture Invariants
<accepted owner/state/transition/order/publication/cancellation/replay/forbidden rules, or explicit no-trigger note>

## Design and Feasibility Preflight
### Prerequisites
- <required|optional>: `proven-ready | protected-activation-required | blocked` — <source-bound evidence;
  exact protected probe/remedy and failure consequence when applicable>
### Production Paths and Verification Seams
- <entry → actual path → observable/failure signal; cheapest credible causal evidence level>
### Affected Broad Regression Placement
- <surface, owning layer, command/discovery source, and why/when it runs; or justified none>

## Technical Plan Baseline
<version/identity; architecture/ownership; package and consumed-contract topology; commands, writes, cleanup,
protected activation, verification topology, budgets, deterministic mutation boundary>

## Assurance Profile
- Profile: `low | standard | high` — <classification rationale under canonical assurance routing>
- Package routing: `<WP-ID>: boundary | final` — <named boundary/risk and one independent owner/lens/freeze side>
- Consumed-contract unlocks: <producer → dependent/consumer, exact contract digest source, required `B[i]`>
- Promotion trigger: <runtime discovery that invalidates candidate/profile/routing and advances reviewed baseline>

## Execution Readiness and Auto-Resolve
- Prerequisite summary: <all required ready or exact protected activation; `blocked` prevents readiness>
- Preauthorization Budget: <maxima/issued/deadline from Lifecycle State; no duplicate history>
- Proposed agent-owned correction boundary: <Technical Plan Baseline only>
- Human escalation: <envelope/protected/risk/budget/verification stops>

## Work Packages
- `packages/WP1.md` — <short title>

## Code References
- `path/to/file` — <relevance>
- Or `None identified.`

## Out of Scope
<approved exclusions/deferrals with provenance>
```

## Authority Rules

- Human Authorization Envelope is user-owned. Reference stable Requirements, Acceptance Criteria, Constraints, and
  Out of Scope entries instead of duplicating them. Agents must not alter outcomes, scope, product/interface
  invariants, accepted material risk, protected effects, or bounds.
- Technical Plan Baseline is the exact architecture, packages, commands, verification topology, and execution
  proposal. It may be corrected only while preserving the envelope and later review requirements.
- Include normative product content only when stated, approved, or safely projected from authoritative Slices.
  Never invent behavior, targets, security rules, compatibility, or success criteria.
- Preserve exact interfaces and forbidden behaviors. Ask before an ambiguous requirement, constraint, Slice
  disposition, exclusion, or risk acceptance.
- Redact secrets, credentials, tokens, PII, and sensitive proprietary values.

## Preflight and Verification Rules

- Every required prerequisite has one disposition. Known unavailable is `blocked`; capability checkable only with
  protected authority is `protected-activation-required`, not falsely ready. Optional unavailable capability is
  disclosed and excluded.
- Production seams name the actual path and causal observation. Broad placement names the earliest credible owning
  layer for shared/public/lifecycle risk.
- Assurance/routing follows the parent-supplied canonical routing contract, not a new ledger. `tasks.json` requires
  top-level `assurance_profile`; every package requires `verification_mode`, with a safe report path for `boundary`
  and `null` for `final`. A final-routed leaf never receives a fabricated report.
- Verification Expectations follow the minimum-sufficient acceptance rule in the work-package contract: confidence
  obligations plus cheapest credible causal evidence, not a test list. One test may prove multiple related rows.

## Manifest and Purity Rules

- `Conceptualize Inputs`, `Authoritative Slices`, and `Work Packages` are manifests only. Slice inventory matches
  `tasks.json.authoritative_slices`; Index-only/no-Slice plans say so explicitly.
- Work Packages list paths/titles only. Code References are verified code-root-relative paths.
- Keep package assignment, test cases, proof rows, review findings, command output, transcripts, debate, code,
  pseudo-code, line numbers, and diffs out of `SPEC.md`.
- Do not duplicate Lifecycle State budget history; reference its current maxima/issued/deadline.

## Fail Closed

Stop when baseline/requirements weaken approved intent; envelope and baseline are conflated; a required
prerequisite is `blocked` or missing; protected activation lacks an exact probe/remedy; actual path/seam/broad
placement is invented; assurance routing lacks named rationale; Slice manifests disagree; or a material deferral
lacks approval provenance.
