# Development Quality Contract

Implementation, repair, review, and audit agents MUST apply this contract during Super Developer workflow execution.
Use RFC 2119 meanings for MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY.

This language-agnostic contract combines a concise craft chapter with operational gates. It is not a style
guide, lint surrogate, language recipe catalog, or parallel proof system. Correctness, safety, caller
contracts, verification, trust boundaries, data behavior, and error behavior are MUST-level obligations.
Modifiability and durability are enforced clean-code criteria, but they do not outrank those duties.

A change is non-trivial when it touches multiple files, changes behavior/API/data/error handling, affects
contracts or generated/docs artifacts, introduces security/privacy/reliability/concurrency/performance risk,
refactors shared code, or requires package/repository verification. Tiny edits MAY use lighter evidence,
but still MUST preserve correctness and avoid collateral cleanup.

## 1. Clean Work
Clean work lets maintainers change safely because behavior is truthful, boundaries are visible, and the
design carries only the concepts it needs. For non-trivial changes, agents MUST protect:
- **Truthful outcomes:** success, failure, partial success, invalid input, and skipped work are
  distinguishable; no fake success or silent fallback unless accepted, documented, and observable.
- **Clear contracts:** APIs, package artifacts, proof claims, schemas, generated contracts, config, and
  operational surfaces stay compatible unless accepted artifacts require a break.
- **Validated boundaries:** untrusted or dynamic data is validated or narrowed before trusted use.
- **Local changeability:** behavior has a clear owner, cohesive boundary, and smallest useful seam.
- **Readable model:** names, domain vocabulary, flow, state transitions, and tests explain intent.
- **Compact evidence:** cite proof rows, verification output, tests, reports, or findings; do not create
  standalone clean-code proof/report artifacts.

## 2. Severity and Material Evidence
Severity follows the strongest material risk supported by evidence:
- **BLOCKER:** MUST-level violation, unverified non-trivial behavior, broken caller contract, fake success,
  security/privacy/safety/data/integrity risk, missing trust-boundary validation, incompatible public API,
  unsafe migration, unresolved assigned obligation, or required proof/verification gap.
- **CODE-QUALITY:** concrete maintainability risk: brittle seam, scattered future edits, unclear owner,
  unjustified duplication, speculative abstraction, excess coupling, cognitive complexity, poor testability,
  dependency/framework leakage, or domain-model inconsistency.
- **ADVISORY:** optional improvement, local style convention, small clarity improvement, or future cleanup.

Reviewers and auditors MUST NOT elevate taste, formatting preference, or personal style into serious
findings. Maintainability concerns become serious only with evidence of brittleness, change cost,
caller-contract risk, safety/security/data risk, completion-confidence risk, or future-modification risk.
Material correctness, safety, maintainability, or verification risks MUST NOT remain advisory.

## 3. Craft Principles
- **Preserve contracts first.** Callers must distinguish material outcomes. Preserve success/failure,
  partial-failure, invalid/default input, public API, persistence, generated-artifact, and operational
  expectations unless accepted artifacts change them.
- **Design around real seams.** A seam owns a concept, invariant, boundary, or variable behavior. Prefer
  cohesive modules, explicit dependency direction, and replaceable edges for fallible/volatile collaborators.
- **Reuse real concepts.** Reduce duplication for the same concept, invariant, policy, boundary behavior,
  bug fix, or caller contract. Keep superficial similarity local when abstraction would invent knobs,
  flags, factories, hooks, wrappers, or extension points.
- **Prefer simplicity and small surfaces.** Add config, dependencies, indirection, caches, retries, flags,
  or lifecycle states only when requirement or risk justifies them. Extensibility comes from clear seams.
- **Encapsulate details.** Shared APIs SHOULD expose coherent caller operations, hide incidental state or
  vendor/framework shapes, make defaults explicit, and be easy to use correctly and hard to misuse.
- **Make cognitive load visible.** Watch deep nesting, long functions, scattered conditionals, hidden
  temporal coupling, unclear ownership, implicit state transitions, misleading/generic names, and vocabulary drift.
- **Treat testability as design feedback.** Prefer deterministic seams, observable outcomes, narrow setup,
  and clear boundary behavior. Isolate brittle time, randomness, I/O, globals, subprocesses, network,
  LLM/tool output, and framework lifecycle. Mocks MUST NOT replace an unverified external/library/runtime/
  API contract under test.
- **Keep dependencies disciplined.** Dependencies are design decisions. Avoid unnecessary packages/services,
  preserve dependency direction, isolate vendor/framework details where practical, and check lifecycle,
  security, operations, performance, and replacement cost.
- **Work cleanly in brownfield code.** Messy surroundings are evidence, not permission to spread mess.
  New and meaningfully changed code SHOULD meet this contract while minimizing unrelated disturbance.
  Classify patterns as contract, convention, defective, or unknown; preserve real contracts, avoid copying
  defects, isolate the smallest useful clean seam, improve touched paths when needed, and surface broader
  cleanup as separate scope.

## 4. Operational Gates
- **Discovery:** read requirements, package scope, assigned Slice context, and existing code; search callsites
  before changing APIs, data models, shared behavior, generated artifacts, or workflow contracts; classify
  patterns; identify trust boundaries, caller-visible states, config/persistence/generated implications, and
  verification seams.
- **Design:** identify outcome contracts, invalid/default input, cancellation/cleanup when relevant,
  validation boundaries, module boundaries, dependency direction, public surface changes, modifiability
  strategy, risk surfaces, and verification tied to assigned proof obligations.
- **Implementation:** solve the in-scope behavior/risk class; preserve contracts/dependency direction unless
  accepted artifacts change them; update affected callsites/tests/docs/generated artifacts/schemas/examples;
  stay focused; avoid broad cleanup,
  stale code/TODOs, and unvalidated data; stop before product/design changes, speculative features, broad
  refactors, new services, unsafe commands, credentials, external facts, destructive actions, or risk acceptance.
- **Verification:** run targeted checks, prefer real paths over mocks, disclose mocks/skips/manual/static scope,
  and cover material outcomes, invalid/default input, trust-boundary validation, public contracts,
  persistence/data, security/privacy/safety, resource bounds, concurrency, generated artifacts, and brownfield
  contracts where relevant.
- **Review/audit:** confirm evidence truthfulness before polish; serious quality findings need concrete
  material risk; downgrade or omit taste/style/optional cleanup; treat missing verification, fake success,
  invalid proof claims, unvalidated boundaries, public-contract breaks, and unresolved obligations as blockers.

## 5. Common Risk Surfaces
Use these language-neutral surfaces instead of per-language adapters:
- External input/dynamic data: user input, JSON/YAML, requests, messages, LLM/tool output, and data payloads.
- Public/shared APIs: exports, commands, prompts, schemas, artifacts, config keys, file formats, defaults,
  generated contracts, and misuse resistance.
- Files/env/config: missing, malformed, partial, secret-bearing, or environment-specific values.
- Persistence/migrations: compatibility, rollback/backfill, idempotency, integrity, partial failure, recovery.
- Network/subprocess/services: validation, bounded timeouts/retries/fanout, distinguishable failure.
- Errors/partial success: context without secrets/private data; observable, compensated, or fail-closed work.
- Async/concurrency/lifecycle: ownership, locking/atomicity, idempotency, races, cancellation, cleanup, release.
- Performance/resources: expected complexity, worst case, and bounded loops, memory, retries, queues, I/O, fanout.
- Framework/vendor boundaries: isolate lifecycle, ORM/request objects, SDK shapes, and vendor types from domain logic.
- Security/privacy: no hardcoded/logged/committed secrets; minimize, validate, access-control, and exclude sensitive data.

## 6. Compact Quality Contract Evidence
For non-trivial implementation or repair work, completion reports MUST include:
```markdown
Quality Contract Evidence:
- Inspection outcome: <contracts/conventions/defective patterns/unknowns found>
- Boundary/design choice: <caller contract, seam, trust boundary, and error strategy>
- Behavior/risk class covered: <edge/failure/security/privacy/data/performance/concurrency cases or why not applicable>
- Affected artifacts: <files, public contracts/APIs, callsites, tests, docs, generated artifacts>
- Verification run: <commands/tests/static inspections/manual observations; cite proof rows or reports>
- Rule exceptions: <MUST/SHOULD exception and justification, or none>
```
For planned-feature package work, this evidence complements existing SPEC/package/proof/report/review/audit
artifacts. It MUST NOT introduce a standalone clean-code proof file, report file, registry field,
lifecycle state, or command ledger, and it should not duplicate package proof rows beyond concise citations.

## 7. Lightweight Audit Cues
Ask whether callers can distinguish outcomes; untrusted data is validated; future changes stay localized;
reuse, duplication, dependencies, and extension points are justified by current concepts; tests/proofs
verify stable behavior and risk cases without replacing real contracts with mocks; brownfield new/touched
code is cleaner without unrelated disturbance; and serious findings have material evidence rather than taste.
Treat correctness, safety, caller-contract, verification, trust-boundary, data, security, or privacy risk
as blocker; material brittleness or maintainability risk as code-quality; and preference as advisory or
unreported.
