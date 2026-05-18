# Development Quality Contract

Implementation, audit, and review agents MUST apply this contract during development workflow execution.

Use RFC 2119 meanings for MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY.

Hybrid model: correctness, safety, caller contracts, tests/verification, and trust-boundaries are MUST-level requirements. Maintainability rules are SHOULD-level heuristics unless they protect a MUST-level requirement; exceptions to SHOULD rules require explicit justification.

## 1. Scope and Severity

### Non-Trivial Change Threshold

A change is non-trivial when any item applies:

- It touches more than one file.
- It changes behavior, public API, data model, permissions, persistence, external integration, or error handling.
- It adds a business-logic module or function.
- Tests are required by the task, plan, repository convention, or risk profile.
- It introduces security, privacy, reliability, concurrency, performance, migration, or rollback risk.
- It refactors shared code.
- It affects generated artifacts, documentation, contracts, schemas, or user-facing examples.

Tiny isolated edits MAY be exempt when they do not affect runtime behavior or shared contracts, but the implementer MUST still preserve correctness and avoid collateral cleanup.

### Enforcement Severity

- **BLOCKER**: MUST-level violation, unverified non-trivial behavior change, broken caller contract, fake success state, security/privacy/safety/data-loss/integrity risk, missing trust-boundary validation, incompatible public API change, unsafe migration, missing required test/verification, or unresolved acceptance criterion.
- **CODE-QUALITY**: SHOULD-level maintainability violation without immediate correctness/safety impact, unjustified duplication, unclear boundary, unnecessary coupling, hard-to-review structure, inconsistent good convention, or local complexity that materially raises maintenance risk.
- **ADVISORY**: Optional improvement, style preference grounded in local conventions, small clarity improvement, or future cleanup that is useful but not required for the current change.

Audit and review agents MUST classify findings using these severities. A finding that materially affects correctness, safety, maintainability risk, or verification confidence MUST NOT remain an advisory suggestion; classify it at the serious severity justified by the evidence. Exceptions to SHOULD rules MUST include explicit justification in completion evidence or review context.

## 2. Phase Gates

### Discovery Gate

For non-trivial changes, implementers MUST:

- Read the relevant requirements, task acceptance criteria, and existing code before editing.
- Search for callsites before changing exported symbols, public APIs, data models, or shared behavior.
- Treat existing code as evidence, not authority. Classify discovered patterns as:
  - **contract**: externally depended on; MUST preserve or migrate compatibly.
  - **good convention**: healthy local pattern; SHOULD follow.
  - **legacy-bad pattern**: known or evident defect; MUST NOT spread.
  - **unknown**: insufficient evidence; use the simplest local fit and surface uncertainty.

### Design Gate

Before implementation, non-trivial work MUST identify:

- The caller contract: success, failure, partial success, and invalid input behavior.
- Trust boundaries and runtime validation requirements.
- Module boundaries and dependency direction.
- A verification plan tied to acceptance criteria, changed behavior, and relevant edge/failure cases.
- The behavior/risk class implied by the task or package, including applicable security, privacy, data-integrity, performance, concurrency, default/omission, and lifecycle concerns.
- Any public API, persistence, migration, configuration, security, privacy, performance, or concurrency implications.

### Implementation Gate

Implementation MUST:

- Treat acceptance criteria as minimum proof obligations, not permission to implement only the narrow happy path; solve the complete in-scope behavior/risk class implied by the accepted task or package.
- Preserve contracts and dependency direction unless the task explicitly changes them.
- Update callsites, tests, docs, generated artifacts, schemas, and contracts affected by the change.
- Keep changes focused on the assigned scope.
- Stop for approval instead of silently expanding into product/design changes, speculative features, unrelated cleanup, broad refactors, new dependencies/services, or unsafe operations.
- Use a clean cutover by default. Incremental migration MAY be used only when required by shared ownership, compatibility, rollout risk, or explicit plan constraint; the consistency boundary MUST be documented.

### Testing and Verification Gate

Non-trivial behavior changes MUST have relevant tests or verification. Implementers MUST run the targeted verification that covers the changed behavior before completion. Internal behavior SHOULD be tested with real integration paths instead of mocks. Mocks MUST NOT replace the contract under test: external/library/runtime/API boundary behavior that the feature depends on proving must use the real library, documented fixture shape, captured real payload, or an already-verified seam. Mocks MAY be used behind already-verified seams, at external service boundaries, or when isolation is the behavior under test, and MUST be disclosed in completion evidence or the assigned package proof.

### Completion Evidence Gate

Non-trivial completion reports MUST include the compact evidence block in §9. Planned-feature package work MUST also update the assigned package proof with criterion-level evidence. Missing, vague, stale, failed, blocked, reopened/unaccepted, or unapproved manual evidence is a BLOCKER for audit.

### Audit and Review Gate

Audit MUST verify acceptance criteria and MUST-level quality-contract compliance. Review-code MUST use this contract for maintainability, safety, API, and failure-mode findings without replacing audit as the authoritative completeness proof. Initial discovery review clean results MUST include concrete dynamic-lens coverage evidence; boilerplate statements such as `looks good` or `no issues found` do not prove that a required lens was covered.

In the unified delivery pipeline, implementer/fix sub-agents own substantive code/test/documentation changes and targeted verification. The orchestrator owns git, dispatch, merge, evidence validation, and integration checks; it MUST NOT apply substantive production/test/documentation fixes inline except for explicit user-approved plan/status/metadata or mechanical merge-conflict artifacts.

## 3. Contracts, Boundaries, and Errors

- Callers MUST be able to distinguish success, failure, partial success, and invalid input. Code MUST NOT return plausible success output after failure.
- Every fallible boundary MUST have an explicit error strategy: handle, propagate, retry with bounds, compensate, or fail closed. Silent fallback is prohibited unless it is documented product behavior and observable to the caller when relevant.
- Runtime validation is REQUIRED at trust boundaries: user input, network/API input, files, environment/config, database rows crossing schema assumptions, queues, subprocesses, LLM/tool output, and generated artifacts.
- Public API compatibility MUST be preserved unless the accepted plan requires a breaking change. Breaking changes MUST update callsites and affected contracts/docs.
- Dependency direction MUST remain coherent: high-level policy SHOULD NOT depend on low-level details when an existing seam can carry the dependency.

## 4. Module Boundaries and Refactoring

- Do not extend a file or module when the new behavior adds a second responsibility. Create or extract a focused module, seam, adapter, or helper with a clear reason to change.
- A file SHOULD have one primary responsibility and a name that explains it.
- Broad cleanup is separate work. Local cleanup MAY be done when it directly supports the current change, reduces risk, or makes verification possible.
- Generated code is exempt from manual structure rules only when clearly generated and not manually edited. Generator inputs/templates remain subject to this contract.

### Contract-Preserving Open/Closed Principle

Existing behavior, caller contracts, public APIs, persistence semantics, security/privacy posture, and operational contracts are closed unless the accepted plan explicitly approves a change. Internal edits are allowed when they preserve those contracts and are the natural responsibility location. Do not create speculative wrappers, subclasses, flags, or adapter layers merely to avoid touching existing code; do create or use seams when new behavior would otherwise mix responsibilities or change existing contracts implicitly.

## 5. Duplication and Abstraction

Use the same-reason-to-change test:

- Duplication SHOULD remain when similar code represents different concepts or changes for different reasons.
- Duplication SHOULD be abstracted when it is the same concept/behavior, a bug fix must apply consistently, or a contract must be enforced centrally.
- Abstractions MUST earn their keep through current callers, consistency, or boundary control. Speculative factories, wrappers, flags, hooks, extension points, and configuration knobs are prohibited.

## 6. Simplicity, Dependencies, and Configuration

- Prefer the simplest design that satisfies current requirements, preserves contracts, and remains testable.
- Do not add speculative features, flags, options, or compatibility layers.
- A new runtime dependency requires explicit justification and user approval before implementation. The justification MUST include purpose, alternatives, operational/security risk, and maintenance cost.
- A dev-only dependency SHOULD be justified when it is risky, heavy, security-sensitive, or changes project workflow.
- Configuration changes MUST document defaults, required variables, failure behavior, and deployment impact.

## 7. Safety, Data, and Operations

- Secrets MUST NOT be hardcoded, logged, committed, or exposed in errors. Secret-bearing values MUST be redacted in logs and reports.
- Privacy-sensitive data MUST be minimized, validated, access-controlled, and excluded from unnecessary logs, traces, prompts, fixtures, and generated artifacts.
- Persistence and migration changes MUST define compatibility, rollback/backfill behavior, idempotency, data integrity checks, and partial-failure handling.
- Performance-sensitive changes MUST identify resource bounds, expected complexity, and worst-case behavior. Unbounded loops, retries, fanout, memory growth, queue growth, or blocking I/O are BLOCKER risks when reachable.
- Concurrency-sensitive changes MUST define ownership, locking/atomicity/idempotency, race behavior, cancellation/timeout behavior, and cleanup on failure.
- External integrations MUST validate responses, handle timeouts/retries with bounds, expose distinguishable failure, and avoid treating malformed responses as success.
- Documentation/contracts MUST be updated when user-visible behavior, public APIs, configuration, migrations, generated artifacts, or operational procedures change.

## 8. Maintainability Heuristics

These are SHOULD rules unless they protect a MUST-level contract:

- Keep functions small enough to review in one pass; extract named helpers when nesting, branching, or mixed concerns obscure behavior.
- Prefer descriptive names over explanatory comments. Comments should explain non-obvious why, not restate what.
- Replace magic values with named constants when the value has domain meaning or is reused.
- Keep parameter lists readable; use an options object/struct when arguments are numerous, ambiguous, or commonly defaulted together.
- Avoid `any`/unchecked dynamic typing when a narrower type or runtime validation can express the contract.
- Do not leave unreachable code, orphan files, stale exports, TODO/FIXME/HACK markers for current-scope work, or obsolete compatibility shims.

## 9. Compact Completion Evidence

For non-trivial work, completion evidence MUST include:

```markdown
Quality Contract Evidence:
- Inspection outcome: <what existing patterns were classified as contract/good convention/legacy-bad/unknown>
- Boundary/design choice: <module seam, caller contract, trust-boundary validation, and error strategy>
- Behavior/risk class covered: <in-scope class, relevant edge/failure/security/privacy cases, or why not applicable>
- Affected artifacts: <files, public contracts/APIs, callsites, tests, docs, schemas, generated artifacts>
- Verification run: <commands/tests/scenarios run, with observed result>
- Rule exceptions: <MUST/SHOULD exception and justification, or "none">
```

For planned-feature pipeline work, this evidence block does not replace the assigned package proof. The proof entry for each completed acceptance criterion MUST include state binding, source refs, file/symbol evidence, command results or manual evidence, relevant edge/failure and behavior/risk-class coverage in `evidence.edge_cases`, context-bundle citations when applicable, mock disclosure, and observed behavior.

## 10. Language Adapters

The universal contract above takes precedence. Apply these examples by language:

### TypeScript

- Runtime validation is REQUIRED for `unknown`, JSON, request bodies, environment variables, LLM/tool output, and database/API payloads crossing trust boundaries.
- Do not use `any` to bypass caller contracts, validation, or type errors; if unavoidable at an external boundary, isolate it and narrow immediately.
- Public exported type changes MUST be checked against imports/callsites.
- Promise boundaries MUST handle rejection through `await`, return propagation, or explicit fire-and-forget documentation with error sink.

### Python

- Validate untyped inputs at module boundaries and when loading JSON/YAML/env/files.
- Avoid broad `except Exception` unless rethrowing, wrapping with context, or deliberately handling a boundary; never use empty `except` blocks.
- Keep side effects explicit at import time; configuration, I/O, and network calls SHOULD live behind functions or adapters.
- Public function signature changes MUST update callers and tests.

### Go

- Always check returned `error` values or document why ignoring is safe.
- Use `context.Context` for request-scoped I/O, cancellation, deadlines, and external calls.
- Validate decoded JSON, flags/env/config, database rows, and RPC inputs before trusting them.
- Keep interfaces small and consumer-owned; do not introduce an interface for a single speculative implementation.

### Rust

- Do not use `unwrap`/`expect` in production paths unless the invariant is local, proven, and documented; propagate or map errors otherwise.
- Validate deserialized/config/external data before converting into trusted domain types.
- Prefer explicit ownership and lifetimes over cloning to satisfy the compiler when clone cost or semantics matter.
- Public enum/struct changes MUST consider downstream pattern matches and serialization compatibility.
