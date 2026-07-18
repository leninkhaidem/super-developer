# SPEC.md Template and Purity Rules

`SPEC.md` is a concise requirements and manifest file. It is not package assignment, proof evidence, architecture debate, implementation transcript, or a replacement for authoritative Slices.

## Template

```markdown
# <Feature Name — Human Readable> Specification

## Overview
1-2 sentences describing the user goal and intended outcome.

## Accepted Source Baseline
A sanitized, lossless statement of the approved request and explicit follow-on/out-of-scope boundaries. Preserve
source wording where omission or reinterpretation would change meaning; use `None beyond requirements below.`
when the requirements are already the complete direct baseline.

## Conceptualize Inputs
Path-only planning handoff link; paths are artifact-root-relative.
- Index: `.planning/<concept-slug>/index.md`
- Use `None.` when no Conceptualize workspace applies.

## Authoritative Slices
Full safe Slice inventory for this plan. Details stay in Slice files.
- `.planning/<concept-slug>/slices/<slice-name>.md`
- Use `None; Index-only/no-Slice plan.` when no Slice is independently useful.

## Requirements
User-facing functional requirements and safe Slice-derived feature requirements. Use stable IDs for traceability.
- REQ-1: ...

## Acceptance Criteria
Feature-level outcomes. Use stable IDs; prefer Given/When/Then when useful.
- AC-1: ...

## Constraints
Non-negotiable user-stated constraints, approved scope limits, compatibility/security/performance policy, or Slice-derived constraints that apply feature-wide.

## Architecture Invariants
For triggered Design Preflight only: concise accepted authority, state/transition, ordering/publication,
cancellation/replay, forbidden-behavior, actual-path test-seam, and broad-regression rules. Use
`None; Design Preflight did not trigger architecture invariants.` for narrow low-risk work. Do not store debate.

## Work Packages
Manifest only. Package scope, Slice H3 assignments, verification expectations, dependencies, proof paths, and report paths live in package Markdown.
- `packages/WP1.md` — <short title>

## Code References
Verified existing files/modules to inspect. Reference paths are code-root-relative only; no code excerpts or change instructions. Use `None identified.` when no safe references are known.
- `path/to/file` — why it is relevant.

## Out of Scope
User-approved exclusions, deferred items, or boundaries. Include approval provenance when an otherwise material Slice commitment is deferred, narrowed, rejected, or excluded.
```

## Source Rules

- Include normative product content only when stated, explicitly approved, or safely projected from authoritative Slice product/design commitments.
- Do not invent product behavior, architecture, performance targets, security rules, compatibility constraints, or success criteria to make the spec feel complete.
- Ask before writing if a requirement, constraint, success condition, Slice deferral, or exclusion is needed but ambiguous.
- Preserve the sanitized accepted source baseline plus all user-stated and safely projected requirements.
- Persist triggered accepted invariants as checkable constraints/acceptance rules, never architecture debate.
- Redact secrets, credentials, tokens, PII, and proprietary sensitive values.

## Manifest Rules

- `Conceptualize Inputs` is path-only and non-normative.
- `Authoritative Slices` lists the same full safe Slice inventory as `tasks.json.authoritative_slices`; for Index-only/no-Slice plans both surfaces explicitly say there are no Slice files.
- `Work Packages` lists package Markdown paths and short titles only.
- Code References are non-normative path references from lightweight repo inspection.

## Fail Closed When

- Raw Slice text, source excerpts, transcripts, debate, implementation sequencing, proof rows, review findings, line numbers, code snippets, or diffs are copied into `SPEC.md`.
- The accepted source baseline or feature requirements omit, weaken, or reinterpret an approved commitment.
- Triggered authority/state/transition/publication/forbidden/test-seam invariants remain chat-only or ambiguous.
- An approved deferral/exclusion lacks provenance and scope.
- The Slice manifest and registry Slice inventory disagree.
