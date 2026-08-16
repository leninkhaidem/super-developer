# SPEC.md Template and Purity Rules

`SPEC.md` is a concise requirements and manifest file. It is not package assignment, result evidence,
architecture debate, implementation transcript, or a replacement for authoritative Slices.

## Template

```markdown
# <Feature Name — Human Readable> Specification

## Overview
1-2 sentences describing the user goal and intended outcome.

## Conceptualize Inputs
Path-only planning handoff link; paths are artifact-root-relative.
- Index: `.planning/<concept-slug>/index.md`
- Use `None.` when no Conceptualize workspace applies.

## Authoritative Slices
Full safe Slice inventory for this plan. Details stay in Slice files.
- `.planning/<concept-slug>/slices/<slice-name>.md`
- Use `None; Index-only/no-Slice plan.` when no Slice is independently useful.

## Trust Context
The feature's operating boundary, stated as fact and approved at the plan gate. Reviewers and verifiers reason
from this instead of assuming a hostile public surface by default. It scopes assurance depth only; it never
lowers a stated requirement, and it never relaxes control-plane/prompt-injection handling, which is always in force.
- Actors: <who invokes this, and are they trusted?>
- Trust boundary: <what crosses it, and what sits inside it>
- Data sensitivity: <secrets, PII, or regulated data present, or `None.`>
- Deployment surface: <local-only, internal service, public network, or regulated>
- Out-of-boundary dimensions: <assurance dimensions this context excludes, each with a reason, or `None.`>

## Requirements
User-facing functional requirements and safe Slice-derived feature requirements. Use stable IDs for traceability.
- REQ-1: ...

## Acceptance
Feature-level definition of success: the end-to-end checks that prove the whole feature actually works.
This is the final delivery gate — the feature is delivered only when every check here passes on the integrated
code. **Executable-by-default:** each item is a runnable check (command, test id, or observable output). An item
that genuinely cannot be automated is allowed only as an explicit human-approved manual-verification exception,
marked `manual (approved)`, and is surfaced for approval at plan review.
- AC-1: <what success looks like> — check: `<command or test id>` — expected: <observable pass condition>
- AC-2: <outcome that cannot be automated> — check: manual (approved) — verify: <exact manual step and expected result>

## Constraints
Non-negotiable user-stated constraints, approved scope limits, compatibility/security/performance policy, or Slice-derived constraints that apply feature-wide.

## Work Packages
Manifest only. Package scope, Slice H3 assignments, verification expectations, dependencies, and report paths live in package Markdown.
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
- Every `## Acceptance` item is an executable check unless it carries an explicit human-approved `manual (approved)` exception; never leave a feature-level outcome unverifiable and silent.
- `## Trust Context` is required for newly authored SPECs. A pre-existing SPEC without it is not retroactively
  invalid: treat its absence as the strictest surface and add the section at the next planning continuation that
  touches requirements, rather than blocking in-flight work.
- `## Trust Context` records observed or user-approved fact, never a convenience downgrade to quiet reviewers.
  An absent, vague, or unapproved context defaults to the strictest surface. It cannot place a dimension out of
  boundary that a requirement, constraint, or Slice commitment depends on, and it is surfaced for approval at
  plan review like any other scope reduction.
- Ask before writing if a requirement, constraint, success condition, Slice deferral, or exclusion is needed but ambiguous.
- Preserve all user-stated and safely projected requirements while keeping the file concise.
- Redact secrets, credentials, tokens, PII, and proprietary sensitive values.

## Manifest Rules

- `Conceptualize Inputs` is path-only and non-normative.
- `Authoritative Slices` lists the same full safe Slice inventory as `tasks.json.authoritative_slices`; for Index-only/no-Slice plans both surfaces explicitly say there are no Slice files.
- `Work Packages` lists package Markdown paths and short titles only.
- Code References are non-normative path references from lightweight repo inspection.

## Fail Closed When

- Raw Slice text, source excerpts, transcripts, debate, implementation sequencing, result rows, review findings, line numbers, code snippets, or diffs are copied into `SPEC.md`.
- Feature-level requirements omit user-stated or safely projected commitments.
- `## Acceptance` is missing, empty, or contains an item that is neither an executable check nor a human-approved `manual (approved)` exception.
- `## Trust Context` is missing, or marks a dimension out of boundary that a requirement, constraint, or Slice
  commitment relies on.
- An approved deferral/exclusion lacks provenance and scope.
- The Slice manifest and registry Slice inventory disagree.
