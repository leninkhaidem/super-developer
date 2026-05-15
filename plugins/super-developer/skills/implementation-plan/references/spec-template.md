# SPEC.md Template and Purity Rules

Load this when drafting `.tasks/<feature-name>/SPEC.md`.

`SPEC.md` is the requirements source of truth: what the user wants, how success is judged, and what is explicitly excluded. It is not an architecture brief, implementation plan, design decision log, or task breakdown.

## Template

```markdown
# <Feature Name — Human Readable> Specification

## Overview
1-2 sentences describing the user goal and intended outcome.

## Requirements
User-facing functional requirements. Use stable IDs for traceability.
- REQ-1: ...
- REQ-2: ...

## Acceptance Criteria
Feature-level, user-visible outcomes. Use stable IDs; prefer Given/When/Then when useful.
- AC-1: ...
- AC-2: ...

## Constraints
Non-negotiable user-stated constraints: compatibility, security, performance, policy, timing.

## Code References
Verified existing files/modules to inspect. Reference paths only; no code excerpts or change instructions. Use `None identified` when no safe references are known.
- `path/to/file`: why it is relevant.

## Out of Scope
User-stated exclusions and boundaries.
```

## Source Rules

- Include normative product content only when it was stated or explicitly approved by the user in the prior discussion.
- Do not invent product behavior, architecture, performance targets, security rules, compatibility constraints, or acceptance criteria to make the spec feel complete.
- If a requirement, constraint, success condition, or exclusion is needed but ambiguous, ask before writing files.
- Preserve all user-stated requirements even when keeping the file concise.
- Redact secrets, credentials, tokens, PII, and proprietary sensitive values. Use placeholders and describe the requirement without persisting raw sensitive data.

## Code References Rules

- Code References are non-normative; they help implementers start exploration but do not define product behavior.
- Include only paths verified by lightweight codebase inspection.
- Reference paths only. Do not include code snippets, pseudo-code, line numbers, diffs, or change instructions.
- If no relevant paths are known or safe to cite, write `None identified`.

## Purity Rules

- Keep SPEC.md requirements-only.
- Do not include task breakdowns, implementation sequencing, architecture rationale, or design decisions.
- SPEC.md may mention a file path, API, or existing module only as user-approved context or as a non-normative Code Reference.
- If the user explicitly made an architectural choice a product requirement, record the product requirement in SPEC.md and put implementation rationale in `tasks.json.design_decisions`.
- Use `REQ-*` and `AC-*` IDs so `tasks.json` can trace without duplicating whole sections.
