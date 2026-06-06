# Development Quality Contract

Implementation, repair, review, and audit agents MUST apply this contract during Super Developer workflow execution.

Use RFC 2119 meanings for MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY.

This is a language-agnostic craft contract plus operational gates. It is not a style guide, lint surrogate, language recipe catalog, or parallel proof system. Correctness, safety, caller contracts, verification, trust boundaries, data behavior, and error behavior are MUST-level obligations. Modifiability and durability are enforced clean-code criteria for meaningful work, but they do not outrank those first-class obligations.

## 1. What Clean Work Means

Clean work is code, tests, docs, and workflow evidence that a future maintainer can change safely because the behavior is truthful, the boundaries are visible, and the design carries only the concepts it actually needs.

For any non-trivial change, agents MUST protect:

- **Truthful behavior:** success, failure, partial success, invalid input, and skipped work are distinguishable; fake success and silent fallback are prohibited unless explicitly documented product behavior and observable where relevant.
- **Clear contracts:** public/shared APIs, package artifacts, proof claims, generated contracts, schemas, configuration, and operational surfaces remain compatible unless the accepted plan requires a breaking change.
- **Validated boundaries:** untrusted input from users, files, environment/config, network/API calls, database rows, queues, subprocesses, LLM/tool output, generated artifacts, and dynamic data is validated or narrowed before trusted use.
- **Local changeability:** new behavior has a clear owner, cohesive module boundary, and smallest useful seam so future changes do not require scattered edits or knowledge of incidental internals.
- **Readable intent:** names, domain vocabulary, control flow, state transitions, and tests explain the model and behavior, not merely mechanics.
- **Compact evidence:** quality evidence is concise and may cite existing package proof rows, verification outputs, tests, or review findings; do not create standalone clean-code proof/report artifacts.

A change is non-trivial when it touches multiple files, changes behavior/public API/data/error handling, affects generated artifacts/docs/contracts, introduces security/privacy/reliability/concurrency/performance risk, refactors shared code, or requires verification by package scope, repository convention, or risk profile. Tiny isolated edits MAY use lighter evidence, but still MUST preserve correctness and avoid collateral cleanup.

## 2. Severity and Material Evidence

Severity follows the strongest material risk supported by evidence:

- **BLOCKER:** MUST-level violation, unverified non-trivial behavior, broken caller contract, fake success state, security/privacy/safety/data/integrity risk, missing trust-boundary validation, incompatible public API change, unsafe migration, unresolved assigned obligation, or required verification/proof gap.
- **CODE-QUALITY:** maintainability issue with concrete material risk: brittle seam, scattered future edits, unclear ownership, unjustified duplication, speculative abstraction that hides behavior, excessive coupling, hard-to-review cognitive complexity, poor testability, dependency/framework leakage, or inconsistent domain model that materially raises change cost or completion confidence risk.
- **ADVISORY:** optional improvement, style preference grounded in local convention, small clarity improvement, or future cleanup useful but not required now.

Reviewers and auditors MUST NOT elevate taste, formatting preference, or personal style into serious findings. SHOULD-level maintainability concerns become serious only when evidence shows material brittleness, maintainability cost, caller-contract risk, safety/security/data risk, completion-confidence risk, or future-modification risk. Findings that materially affect correctness, safety, maintainability, or verification confidence MUST NOT remain advisory.

## 3. Craft Principles

### 3.1 Preserve contracts before reshaping code

The first clean-code question is whether callers can rely on the result. Preserve success/failure semantics, partial-failure reporting, invalid-input behavior, public API shape, persistence compatibility, generated artifacts, and documented operational expectations unless the accepted plan explicitly changes them.

### 3.2 Design around real seams

A seam is useful when it owns a real concept, invariant, boundary, or independently variable behavior. Prefer cohesive modules with one primary reason to change, explicit dependency direction, and replaceable edges for fallible or volatile collaborators. Do not split code merely to look abstract; do split when mixed responsibilities hide contracts, make tests brittle, or force scattered edits.

### 3.3 Reuse only real concepts

Reduce duplication when repeated code represents the same domain concept, invariant, policy, boundary behavior, bug fix, or caller contract. Keep superficial similarity local when abstraction would invent knobs, flags, factories, hooks, wrappers, or extension points without a current shared owner. Durable reuse follows the model; speculative generality is noise.

### 3.4 Prefer simplicity and small surfaces

The best design has few moving parts, a small public surface, and no unused extension mechanisms. Add configuration, dependencies, indirection, caches, retries, feature flags, or lifecycle states only when the requirement or risk justifies them. Extensibility should come from clear boundaries and stable contracts, not from guessing every future option.

### 3.5 Encapsulate implementation details

Good APIs are easy to use correctly and hard to misuse. Shared interfaces SHOULD expose coherent caller-facing operations, hide incidental storage/order/state details, avoid leaking framework/vendor shapes into domain logic, and make defaults/omissions explicit. Validate or narrow data at the boundary rather than spreading defensive guesses through callers.

### 3.6 Make cognitive load visible

Readability includes more than descriptive names. Watch for deep nesting, long functions, scattered conditionals, hidden temporal coupling, unclear ownership, implicit state transitions, misleading names, generic names that hide intent, and multiple names for the same concept. Prefer domain language that teaches the shared model.

### 3.7 Treat testability as design feedback

Hard-to-test behavior is often hard to change safely. Prefer deterministic seams, observable outcomes, narrow setup, and clear boundary behavior. Isolate time, randomness, I/O, global state, subprocesses, network calls, LLM/tool output, and framework lifecycle when they make behavior brittle or unverifiable. Mocks can support isolation, but they MUST NOT replace the external/library/runtime/API contract under test unless that seam was already verified or the isolation itself is the behavior under test.

### 3.8 Keep dependencies disciplined

Dependencies are design decisions, not conveniences. Avoid unnecessary packages/services and preserve intended dependency direction. Keep vendor/framework details behind boundaries where practical; do not let framework coupling spread into reusable or domain logic unless the accepted design requires it. Check dependency additions for lifecycle, security, operational, performance, and replacement cost.

### 3.9 Work cleanly in brownfield code

Messy surrounding code is evidence, not permission to spread mess. For new and meaningfully changed code, agents SHOULD meet this contract while minimizing disturbance to unrelated existing behavior. Classify existing patterns as contract, good convention, defective pattern, or unknown. Preserve real caller contracts, follow good conventions, avoid copying defective patterns merely for consistency, isolate new behavior behind the smallest useful clean seam, improve the touched path when needed for correctness or verification, and surface broader cleanup as separate scope instead of performing broad silent refactors.

## 4. Operational Gates

### 4.1 Discovery Gate

For non-trivial changes, implementers MUST:

- read requirements, package scope, assigned Slice context, and existing code before editing;
- search callsites before changing exported symbols, public APIs, data models, shared behavior, generated artifacts, or workflow contracts;
- classify discovered patterns as contract, good convention, defective existing pattern, or unknown;
- identify trust boundaries, caller-visible states, generated/persistence/config implications, and likely verification seams.

Preserve contracts. Follow good conventions. Do not spread defective patterns. When evidence is unknown, choose the simplest local fit and surface uncertainty.

### 4.2 Design Gate

Before implementing non-trivial work, identify:

- caller contract for success, failure, partial success, invalid input, default/omitted input, cancellation, and cleanup where relevant;
- trust boundaries and runtime validation/narrowing requirements;
- module boundaries, dependency direction, natural seams, and public surface changes;
- how the change remains modifiable: localized ownership, avoided scattered edits, justified reuse/duplication choices, and test protection for stable behavior;
- applicable security, privacy, data-integrity, performance, concurrency, persistence/migration, configuration, operational, generated-contract, and lifecycle concerns;
- verification tied to assigned Slice/package/proof obligations and changed behavior.

### 4.3 Implementation Gate

Implementation MUST:

- solve the complete in-scope behavior/risk class implied by the package, not only an example path;
- preserve contracts and dependency direction unless accepted artifacts explicitly change them;
- update affected callsites, tests, docs, generated artifacts, schemas, examples, and contracts within scope;
- keep changes focused on assigned scope and avoid broad cleanup unless it directly supports the current change;
- remove or avoid unreachable code, stale exports, obsolete shims, unresolved current-scope TODO/FIXME/HACK markers, and unchecked dynamic typing or unvalidated data at trust boundaries;
- stop for approval before product/design changes, speculative features, broad refactors, new dependencies/services, unsafe commands, credentials/external facts, destructive actions, or risk acceptance.

### 4.4 Verification Gate

Non-trivial changes MUST have targeted verification before completion. Prefer real integration paths over mocks, and disclose mocks, skipped checks, manual observations, command scope, and static inspections.

Verification SHOULD cover the material risk class: success, failure, partial/invalid/default input, trust-boundary validation, public-contract compatibility, persistence/migration safety, data integrity, security/privacy/safety, performance/resource bounds, concurrency/cancellation/cleanup, generated artifacts, and brownfield contract preservation where relevant.

### 4.5 Review and Audit Gate

Review and audit agents apply this contract as a material-risk filter:

- Confirm proof/evidence truthfulness before judging code polish.
- Report serious quality findings only with concrete evidence of brittleness, change-cost risk, caller-contract risk, safety/security/data risk, completion-confidence risk, or future-modification risk.
- Downgrade or omit findings that are pure taste, style preference, or optional cleanup without package-relevant risk.
- Treat missing verification, fake success, invalid proof claims, unvalidated trust-boundary input, public-contract breaks, and unresolved assigned obligations as blockers.

## 5. Common Risk Surfaces

Use these language-neutral surfaces instead of per-language adapters:

- **External input and dynamic data:** user input, JSON/YAML, CLI flags, request bodies, webhooks, messages, LLM/tool output, generated artifacts, and database/API payloads need validation or narrowing before trusted use.
- **Public/shared APIs:** exported functions, commands, prompts, schemas, package artifacts, config keys, file formats, and generated contracts need compatibility checks, clear defaults, and caller-misuse resistance.
- **Files, environment, and configuration:** missing, malformed, partial, secret-bearing, or environment-specific values need explicit failure behavior and privacy-safe diagnostics.
- **Persistence and migrations:** compatibility, rollback/backfill, idempotency, data integrity, partial failure, and recovery behavior must be defined when data shape or storage behavior changes.
- **Network, subprocess, and external services:** validate responses, bound timeouts/retries/fanout, expose distinguishable failure, and never treat malformed responses as success.
- **Errors and partial success:** errors should carry enough context for callers/operators without leaking secrets or private data; partial work needs observable status, compensation, or fail-closed behavior.
- **Async, concurrency, and lifecycle:** define ownership, atomicity/locking/idempotency, race behavior, cancellation/timeout, cleanup, and resource release for reachable concurrent or long-running paths.
- **Performance and resource bounds:** identify expected complexity and worst-case behavior; avoid unbounded loops, memory growth, retries, queues, blocking I/O, or fanout when reachable.
- **Framework and vendor boundaries:** isolate framework lifecycle, ORM/request objects, SDK response shapes, and vendor-specific types when spreading them would couple reusable/domain logic to volatile infrastructure.
- **Security and privacy:** secrets must not be hardcoded, logged, committed, or exposed in errors; privacy-sensitive data should be minimized, validated, access-controlled, and excluded from unnecessary prompts, fixtures, traces, and generated artifacts.

## 6. Compact Quality Contract Evidence

For non-trivial implementation or repair work, completion reports MUST include a compact block:

```markdown
Quality Contract Evidence:
- Inspection outcome: <contracts/conventions/defective patterns/unknowns found>
- Boundary/design choice: <caller contract, seam, trust boundary, and error strategy>
- Behavior/risk class covered: <edge/failure/security/privacy/data/performance/concurrency cases or why not applicable>
- Affected artifacts: <files, public contracts/APIs, callsites, tests, docs, generated artifacts>
- Verification run: <commands/tests/static inspections/manual observations with observed result; cite proof rows or reports instead of restating them>
- Rule exceptions: <MUST/SHOULD exception and justification, or none>
```

For planned-feature package work, this evidence complements existing SPEC/package/proof/report/review/audit artifacts. It MUST NOT introduce a standalone clean-code proof file, report file, registry field, lifecycle state, or command ledger, and it should not duplicate package proof rows beyond concise citations.

## 7. Lightweight Audit Cues

A quick quality pass should ask:

1. Can callers distinguish every material outcome, including failure and partial success?
2. Is untrusted or dynamic data validated at the boundary where it becomes trusted?
3. Would a likely future change be localized to one clear owner or seam?
4. Are reuse, duplication, dependencies, and extension points justified by real current concepts?
5. Do tests/proofs verify stable behavior and meaningful failure/risk cases without relying on mocks that replace the contract under test?
6. In brownfield areas, did new/touched code become cleaner without disturbing unrelated existing behavior?
7. Would any serious finding be backed by material risk rather than taste?

If the answer exposes correctness, safety, caller-contract, verification, trust-boundary, data, or security/privacy risk, treat it as a blocker. If it exposes material brittleness or maintainability risk, treat it as code-quality. If it is only preference, leave it advisory or unreported.
