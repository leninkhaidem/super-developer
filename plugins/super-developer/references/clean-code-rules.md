# Development Quality Contract

Implementation, repair, review, and audit agents MUST apply this contract during Super Developer workflow execution.

Use RFC 2119 meanings for MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY.

Correctness, safety, caller contracts, verification, and trust boundaries are MUST-level requirements. Maintainability rules are SHOULD-level heuristics unless they protect a MUST-level requirement.

## 1. Scope and Severity

A change is non-trivial when it touches multiple files, changes behavior/public API/data/error handling, affects generated artifacts/docs/contracts, introduces security/privacy/reliability/concurrency/performance risk, refactors shared code, or requires verification by package scope, repository convention, or risk profile.

Tiny isolated edits MAY be exempt from the full evidence block, but they still MUST preserve correctness and avoid collateral cleanup.

Severity guidance:

- **BLOCKER**: MUST-level violation, unverified non-trivial behavior, broken caller contract, fake success state, security/privacy/safety/data/integrity risk, missing trust-boundary validation, incompatible public API change, unsafe migration, missing required verification, or unresolved assigned obligation.
- **CODE-QUALITY**: maintainability violation without immediate correctness/safety impact, unjustified duplication, unclear boundary, unnecessary coupling, hard-to-review structure, inconsistent good convention, or local complexity that materially raises maintenance risk.
- **ADVISORY**: optional improvement, style preference grounded in local convention, small clarity improvement, or future cleanup useful but not required now.

Reviewers MUST classify at the seriousness justified by evidence. Findings that materially affect correctness, safety, maintainability, or verification confidence MUST NOT remain advisory.

## 2. Discovery Gate

For non-trivial changes, implementers MUST:

- read requirements, package scope, assigned Slice context, and existing code before editing;
- search callsites before changing exported symbols, public APIs, data models, or shared behavior;
- treat existing code as evidence, not authority;
- classify discovered patterns as contract, good convention, defective existing pattern, or unknown.

Preserve contracts. Follow good conventions. Do not spread defective patterns. When evidence is unknown, choose the simplest local fit and surface uncertainty.

## 3. Design Gate

Before implementation, non-trivial work MUST identify:

- caller contract for success, failure, partial success, and invalid input;
- trust boundaries and runtime validation requirements;
- module boundaries and dependency direction;
- verification tied to assigned Slice/package/proof obligations and changed behavior;
- applicable security, privacy, data-integrity, performance, concurrency, default/omission, lifecycle, and failure concerns;
- public API, persistence, migration, configuration, operational, or generated-contract implications.

## 4. Implementation Gate

Implementation MUST:

- solve the complete in-scope behavior/risk class implied by the package, not only an example path;
- preserve contracts and dependency direction unless the accepted plan explicitly changes them;
- update affected callsites, tests, docs, generated artifacts, schemas, and contracts;
- keep changes focused on assigned scope;
- stop for approval before product/design changes, speculative features, broad refactors, new dependencies/services, unsafe commands, or external facts/credentials;
- use a clean cutover by default, documenting any incremental migration required for compatibility, rollout risk, or shared ownership.

## 5. Testing and Verification Gate

Non-trivial changes MUST have relevant verification and MUST run targeted checks before completion. Prefer real integration paths over mocks. Mocks MUST NOT replace the contract under test at external/library/runtime/API boundaries unless the seam was already verified or isolation is the behavior under test.

Disclose mocks, skipped checks, manual observations, and command scope in completion evidence.

## 6. Contracts, Boundaries, and Errors

- Callers MUST be able to distinguish success, failure, partial success, and invalid input.
- Fallible boundaries MUST handle, propagate, retry with bounds, compensate, or fail closed.
- Silent fallback is prohibited unless documented product behavior and observable when relevant.
- Runtime validation is REQUIRED at trust boundaries: user input, network/API input, files, environment/config, database rows, queues, subprocesses, LLM/tool output, and generated artifacts.
- Public API compatibility MUST be preserved unless the accepted plan requires a breaking change.
- Secrets MUST NOT be hardcoded, logged, committed, or exposed in errors.
- Privacy-sensitive data MUST be minimized, validated, access-controlled, and excluded from unnecessary logs, traces, prompts, fixtures, and generated artifacts.

## 7. Data, Operations, and Concurrency

Persistence and migration changes MUST define compatibility, rollback/backfill behavior, idempotency, data integrity checks, and partial-failure handling.

Performance-sensitive changes MUST identify resource bounds, expected complexity, and worst-case behavior. Unbounded loops, retries, fanout, memory growth, queue growth, or blocking I/O are blocker risks when reachable.

Concurrency-sensitive changes MUST define ownership, locking/atomicity/idempotency, race behavior, cancellation/timeout behavior, and cleanup on failure.

External integrations MUST validate responses, handle timeouts/retries with bounds, expose distinguishable failure, and avoid treating malformed responses as success.

## 8. Maintainability Heuristics

SHOULD-level rules:

- one primary responsibility per file/module;
- create/extract focused seams when new behavior would mix responsibilities;
- avoid broad cleanup unless it directly supports the current change;
- abstract duplication only when it is the same concept, a shared invariant, or a bug fix that must apply consistently;
- avoid speculative factories, wrappers, flags, hooks, extension points, or configuration knobs;
- prefer descriptive names over explanatory comments;
- replace reused domain magic values with named constants;
- keep parameter lists readable;
- avoid unchecked dynamic typing where narrower types or runtime validation express the contract;
- remove unreachable code, orphan files, stale exports, obsolete shims, and unresolved TODO/FIXME/HACK markers for current-scope work.

## 9. Compact Completion Evidence

For non-trivial work, completion reports MUST include:

```markdown
Quality Contract Evidence:
- Inspection outcome: <contracts/conventions/defective patterns/unknowns found>
- Boundary/design choice: <caller contract, seam, trust boundary, and error strategy>
- Behavior/risk class covered: <edge/failure/security/privacy/data/concurrency cases or why not applicable>
- Affected artifacts: <files, public contracts/APIs, callsites, tests, docs, generated artifacts>
- Verification run: <commands/tests/scenarios with observed result>
- Rule exceptions: <MUST/SHOULD exception and justification, or none>
```

For planned-feature package work, this evidence complements the package proof Markdown; it does not replace package proof, package verification, review-code readiness, or audit.

## 10. Language Adapters

### TypeScript

- Validate `unknown`, JSON, request bodies, environment variables, LLM/tool output, and database/API payloads crossing trust boundaries.
- Do not use `any` to bypass contracts, validation, or type errors; isolate and narrow it immediately if unavoidable.
- Check exported type changes against imports/callsites.
- Handle promise rejection through `await`, return propagation, or explicit fire-and-forget documentation with an error sink.

### Python

- Validate untyped inputs at module boundaries and when loading JSON/YAML/env/files.
- Avoid broad `except Exception` unless rethrowing, wrapping with context, or deliberately handling a boundary.
- Keep import-time side effects explicit; configuration, I/O, and network calls SHOULD live behind functions or adapters.
- Public signature changes MUST update callers and tests.

### Go

- Check returned `error` values or document why ignoring is safe.
- Use `context.Context` for request-scoped I/O, cancellation, deadlines, and external calls.
- Validate decoded JSON, flags/env/config, database rows, and RPC inputs before trusting them.
- Keep interfaces small and consumer-owned.

### Rust

- Do not use `unwrap`/`expect` in production paths unless the invariant is local, proven, and documented.
- Validate deserialized/config/external data before converting into trusted domain types.
- Prefer explicit ownership and lifetimes over cloning when clone cost or semantics matter.
- Public enum/struct changes MUST consider downstream pattern matches and serialization compatibility.
