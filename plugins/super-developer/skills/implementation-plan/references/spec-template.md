# SPEC.md Template and Purity Rules

Load this when drafting `.tasks/<feature-name>/SPEC.md` for a schema-version-4 Slice-first plan.

`SPEC.md` is a concise feature-level requirements/manifest file. It is not the package assignment, proof ledger, architecture debate, implementation transcript, or replacement for authoritative Slices.

## Template

```markdown
# <Feature Name — Human Readable> Specification

## Overview
1-2 sentences describing the user goal and intended outcome.

## Conceptualize Inputs
Non-normative path-only planning handoff link.
- Index: `.planning/<concept-slug>/index.md`

## Authoritative Slices
Full safe Slice inventory for this plan. Details stay in the Slice files.
- `.planning/<concept-slug>/slices/<slice-name>.md`

## Requirements
User-facing functional requirements and any hard Slice-derived requirements that are safe to project at feature level. Use stable IDs for traceability.
- REQ-1: ...
- REQ-2: ...

## Acceptance Criteria
Feature-level outcomes. Use stable IDs; prefer Given/When/Then when useful.
- AC-1: ...
- AC-2: ...

## Constraints
Non-negotiable user-stated constraints, approved scope limits, compatibility/security/performance policy, or Slice-derived constraints that apply feature-wide.

## Work Packages
Manifest only. Package scope, Slice H3 assignments, verification expectations, dependencies, and proof paths live in package Markdown.
- `packages/WP1.md` — <short title>

## Code References
Verified existing files/modules to inspect. Reference paths only; no code excerpts or change instructions. Use `None identified` when no safe references are known.
- `path/to/file`: why it is relevant.

## Out of Scope
User-approved exclusions, deferred items, or boundaries. Include approval provenance when an otherwise material Slice requirement is deferred/out-of-scope.
```

## Source Rules

- Include normative product content only when it was stated, explicitly approved, or safely projected from authoritative Slice product/design commitments.
- Do not invent product behavior, architecture, performance targets, security rules, compatibility constraints, or acceptance criteria to make the spec feel complete.
- If a requirement, constraint, success condition, Slice deferral, or exclusion is needed but ambiguous, ask before writing files.
- Preserve all user-stated and safely projected requirements even when keeping the file concise.
- Redact secrets, credentials, tokens, PII, and proprietary sensitive values. Use placeholders and describe the requirement without persisting raw sensitive data.

## Manifest Rules

- `Conceptualize Inputs` contains only the selected Index path and non-normative wording.
- `Authoritative Slices` lists the same full safe Slice inventory that `tasks.json.authoritative_slices` records. Do not copy Slice prose.
- `Work Packages` lists package Markdown paths and short titles only. Do not duplicate package scope, H3 assignments, verification expectations, proof evidence, or dependency details.

## Purity Rules

- Keep `SPEC.md` requirements/manifest-only.
- Do not copy raw Conceptualize Slice content, design rationale, task decomposition, proof rows, review findings, transcripts, or coverage worksheets into `SPEC.md`.
- Slice-derived product requirements may appear in normal Requirements or Acceptance Criteria. Package-specific commitments belong in work-package Markdown; closure evidence belongs in proof Markdown.
- Do not include code snippets, pseudo-code, line numbers, diffs, implementation sequencing, or exact code instructions.
- Code References are non-normative path/reference sections. Include only paths verified by lightweight codebase inspection.
- If the user explicitly made an architectural choice a product requirement, record the product requirement in `SPEC.md` and put implementation-specific ramifications in affected package Markdown notes/verification expectations.
- Use `REQ-*` and `AC-*` IDs where helpful for review/audit traceability, but Slice H3 IDs are the addressable package closure obligations.
