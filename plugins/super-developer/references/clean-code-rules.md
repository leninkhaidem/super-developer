# Development Quality Contract

This contract defines an acceptable change: code maintainers can understand, verify, and modify without
avoidable risk or scattered edits. It is not a style guide or lint substitute. Use RFC 2119 meanings for MUST,
MUST NOT, SHOULD, SHOULD NOT, and MAY.

## Scope

- Implementation and repair agents MUST follow this contract for changed code and behavior.
- Review and audit agents MUST apply its evidence and severity rules; preferences are not findings.
- Planning agents use it to expose design, risk, and verification needs only.

A change is material when it affects behavior, public contracts, data, errors, shared code, prompts or workflow
artifacts, generated artifacts, package verification, or security/privacy/reliability/concurrency/performance risk.
Tiny edits MAY use lighter evidence, but MUST preserve correctness and avoid collateral changes.

## Required Outcomes

For every material change, agents MUST ensure:

- **Truthful behavior:** success, failure, partial success, invalid input, defaults, and skipped work are
  distinguishable. Silent fallback and fake success require explicit acceptance and observability.
- **Preserved contracts:** caller behavior, public APIs, persistence, configuration, schemas, generated artifacts,
  and operations remain compatible unless accepted requirements authorize a break.
- **Validated boundaries:** untrusted or dynamic input is narrowed before trusted use. Errors are explicit and do
  not expose secrets or private data.
- **Maintainable ownership:** changed behavior has a clear owner and cohesive boundary. Likely future changes avoid
  scattered edits and duplicated conditionals.
- **Justified complexity:** abstractions, dependencies, configuration, state, retries, caches, flags, and extension
  points require a current requirement or evidenced risk.
- **Readable behavior:** project vocabulary, control flow, state transitions, defaults, and errors reveal intent.
- **Testable design:** important behavior is observable through deterministic seams. Isolate I/O, time, randomness,
  globals, subprocesses, networks, tools, and framework lifecycle when they make proof brittle.
- **Complete, focused work:** update affected callsites, tests, docs, schemas, examples, and generated artifacts;
  avoid unrelated cleanup and speculative capability.

Material maintainability risks MUST be fixed or explicitly accepted. Maintainability is mandatory, but formatting
or a preferred design alone is not evidence.

## Maintainability Ground Rules

Use these defaults unless repository evidence justifies otherwise:

- Give each concept, invariant, policy, boundary, and caller contract one clear owner.
- Keep changes local; when behavior requires scattered edits, introduce the smallest useful seam.
- Reuse the same concept or policy, not merely similar code. Avoid speculative extension mechanisms.
- Prefer simple data flow and explicit state over deep nesting, temporal coupling, or action at a distance.
- Hide incidental framework, vendor, storage, and transport shapes behind coherent operations.
- Direct dependencies toward stable behavior; isolate volatile collaborators where useful.
- Treat difficult setup, nondeterminism, and excessive mocking as design feedback.
- In brownfield code, preserve contracts without copying defects; improve the touched path and report broader
  cleanup separately.

Linters and pattern names do not prove maintainability. Record non-obvious, material tradeoffs.

## Operational Gates

1. **Discover:** read requirements and relevant code; search callsites before changing shared behavior, contracts,
   data, or generated artifacts; identify outcomes, trust boundaries, conventions, and likely change paths.
2. **Design:** state the caller contract, behavior owner, failure strategy, boundaries, dependency direction,
   material risks, future-change path, and verification approach.
3. **Implement:** make the smallest complete change for the required behavior and risk class. Preserve contracts and
   update affected artifacts; do not add stale code, broad cleanup, or speculative features.
4. **Verify:** exercise real behavior where practical. Cover material success, failure, invalid/default input,
   boundaries, and affected contracts. Inspect relevant data, migration, security, privacy, concurrency, lifecycle,
   network, subprocess, performance, and resource risks. Bound timeouts, retries, fanout, queues, and cleanup when
   used. Disclose mocks, skips, manual checks, and static inspection. Mocks MUST NOT replace an otherwise unverified
   external, library, runtime, or API contract.
5. **Review or audit:** establish correctness and evidence truthfulness before polish. Every serious finding MUST
   identify the affected caller, future change, verification claim, or material risk.

## Stop and Escalate

Stop rather than invent requirements or accept risk when the correct change needs an unapproved product/API
decision, scope expansion, broad refactor, new service or dependency, destructive action, credentials, unavailable
external facts, unsafe command, migration risk, or security/privacy/reliability tradeoff.

## Finding Severity

Use the strongest severity supported by material evidence:

- **BLOCKER:** correctness, safety, security, privacy, data integrity, caller-contract, trust-boundary, migration, or
  required-verification failure; fake success; or an unresolved assigned obligation.
- **CODE-QUALITY:** concrete maintainability risk such as unclear ownership, scattered future edits, unjustified
  duplication or abstraction, excess coupling, dependency leakage, cognitive complexity, or poor testability.
- **ADVISORY:** optional improvement, local convention, minor clarity suggestion, or preference without material risk.

A ground-rule deviation is not automatically a finding. A maintainability concern becomes CODE-QUALITY only when
its brittleness, change cost, test burden, misuse risk, or likely defect surface is explained. Promote it to BLOCKER
only when that evidence also creates a blocker-class risk.

## Quality Contract Evidence

Material implementation or repair completion reports MUST include:

```markdown
Quality Contract Evidence:
- Inspection: <relevant contracts, conventions, defects, and unknowns>
- Design: <behavior owner, caller contract, trust boundary, error strategy, and change-locality choice>
- Risks: <material success, failure, edge, safety, data, maintainability, or resource cases>
- Affected artifacts: <code, callsites, tests, docs, schemas, and generated artifacts>
- Verification: <checks and disclosed limits>
- Rule exceptions: <MUST or ground-rule exception and justification, or none>
```

In planned-package workflows, cite existing proof rows and reports instead of restating them. Do not create a
standalone clean-code report, proof file, registry field, lifecycle state, or command ledger.
