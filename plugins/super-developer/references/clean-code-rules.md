# Development Quality Contract

This contract defines an acceptable change: maintainers can understand, verify, and modify it without avoidable
risk or scattered edits. It is the single shared owner of codebase-design vocabulary and smell heuristics, not a
style guide or lint substitute. RFC 2119 meanings apply to MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY.

## Scope and Calibration

- Implementation and repair agents MUST follow this contract for changed code and behavior.
- Review and audit agents MUST apply its evidence and their own phase severity rules; preferences are not findings.
- Conceptualize and planning agents MUST use it to right-size design and expose only material risk and verification.

A change is material when it affects behavior, contracts, data, errors, shared code, prompts/workflow, generated
artifacts, verification, or security/privacy/reliability/concurrency/performance risk. Tiny or mechanical changes
MAY use lighter evidence and no Module-design ceremony, but MUST preserve correctness and avoid collateral change.
Every applicable design test and smell below MUST be considered; a matching shape is not automatically a defect or
refactoring command. Act only when repository or requirement evidence shows material brittleness, duplicated policy,
scattered edits, misuse/caller risk, test burden, cognitive/change cost, dependency leakage, or another contract risk.

Remediation covers changed behavior and directly affected Interfaces, Seams, Adapters, callers, tests, and evidence,
plus a pre-existing obstacle to correct implementation or credible verification. Do not expand into unrelated
brownfield cleanup, copy a legacy defect into new work, create per-smell evidence rows, or leak test-only variation
into a caller Interface. Report unrelated concerns through existing scope/advisory channels.

## Codebase Design Model

- A **Module** is any behavior-owning function, class, package, or tier-spanning slice with one caller-facing
  **Interface** and an internal **Implementation**; Module is scale-agnostic.
- An Interface is everything callers must understand for correct use: operations and types plus invariants,
  ordering, error modes, required configuration, and relevant performance characteristics. It is broader than a
  language keyword or type signature. Capitalized Slice **Interface contract** instead records product/design
  exactness and is not necessarily a Module Interface; preserve established trust/authority/artifact/lifecycle
  boundary and public API meanings.
- **Depth** is Interface **Leverage**, not implementation size or a lines-of-code ratio. Leverage is caller
  capability per unit of Interface learned. A **deep module** hides substantial decisions behind a small Interface;
  a **shallow module** adds little capability relative to what callers must learn. Ask whether fewer methods,
  simpler parameters, or hidden incidental complexity can deepen the Interface without losing required behavior.
- A **Seam** is the location of an Interface where behavior can vary without editing that location; Seams may be
  external (system/vendor boundary) or internal. An **Adapter** is an implementation role that satisfies the
  Interface at a Seam, not a synonym for Implementation; either may be larger than the other.
- Depth gives callers Leverage and maintainers **Locality**: change, defects, knowledge, and verification stay in
  one owner rather than spreading among callers.
- **Deletion test:** mentally remove the Module. Vanishing complexity indicates pass-through indirection;
  complexity redistributed among multiple callers shows the Module was concentrating real responsibility.
- The Interface is also the test surface: callers and tests use the same Seam, without exposing internals merely
  for tests. One Adapter suggests only hypothetical variation; two independent Adapters demonstrate a real Seam.
  Treat this as an anti-speculation test, not a ban on requirement- or risk-justified contracts.
- Testability defaults: accept volatile dependencies through the Interface instead of invisibly constructing them;
  return observable results instead of relying on hidden side effects where behavior permits; keep Interfaces small.

For material design work, identify the caller contract, owning Module, full Interface, Implementation boundary,
Seams, justified Adapters, intended Depth/Leverage/Locality, deletion-test result, dependency direction, failure
strategy, and verification through the Interface. Prefer Module in this reasoning, but never mechanically rename
established domain, safety, workflow, storage, boundary, or API terms.

## Evidence-Calibrated Smell Heuristics

Apply the complete set to changed paths. Fix material in-scope risk; retain harmless framework, compatibility,
generated, or local shapes with evidence. A label alone never authorizes speculative abstraction or broad cleanup.

- **Mysterious Name:** a changed name obscures a value, function, or type's domain meaning; rename when clearer
  intent exists, and treat inability to name honestly as design evidence rather than inventing jargon.
- **Duplicated Code:** material logic or policy repeats across changed locations; centralize the shared concept
  when drift/change risk is real, never for coincidental similarity.
- **Feature Envy:** behavior relies more on another owner's data than its own; move behavior or expose a cohesive
  operation on the owning Module when that improves ownership and Locality.
- **Data Clumps:** related fields or parameters repeatedly travel together; introduce a cohesive type only when
  they represent a genuine concept or invariant.
- **Primitive Obsession:** a primitive or string carries domain meaning, validation, or invalid states; use a
  focused domain type when it reduces misuse or centralizes invariants.
- **Repeated Switches:** the same type/code dispatch cascade recurs across changed paths; centralize dispatch in a
  map or Module, or use polymorphism, only when repetition creates material risk.
- **Shotgun Surgery:** one logical change requires edits in many locations; gather policy behind one Module or
  Seam when doing so makes future change local.
- **Divergent Change:** one Module changes for unrelated reasons; separate cohesive responsibilities when mixed
  ownership creates material change cost or defects.
- **Speculative Generality:** hooks, parameters, abstractions, or extension points lack an accepted requirement or
  evidenced risk; delete or inline that speculative surface.
- **Message Chains:** callers traverse collaborators or internal structure they should not know; hide navigation
  behind a meaningful Interface operation when that materially reduces coupling.
- **Middle Man:** a Module mainly delegates without policy, protection, or Leverage; use the deletion test and
  remove it unless a real Seam or contract justifies it.
- **Refused Bequest:** an inheritor or implementer ignores most inherited behavior; prefer composition or a smaller
  Interface when inheritance imposes irrelevant obligations.

## Required Outcomes and Operational Gates

Every material change MUST provide truthful success/failure/partial/invalid/default/skipped outcomes; preserve
caller/API/data/config/schema/operation contracts unless authorized; validate untrusted input before trusted use;
avoid secret/private-data leakage; keep one cohesive owner; reveal intent; and update affected callsites, tests,
docs, schemas, examples, and generated artifacts.

**Right-sized complexity:** choose the smallest complete design satisfying accepted requirements and Acceptance.
Every added state, marker, flag, abstraction, dependency, configuration, branch, retry, cache, or extension point
MUST trace to a current requirement or evidenced risk, otherwise cut it. Simplicity MUST NOT remove correctness,
boundary validation, safety, failure handling, or required verification.

1. **Discover/Design:** inspect requirements, conventions, outcomes, callers, boundaries, likely change paths, and
   risks; state owner, caller contract, failure strategy, dependency direction, Locality, and verification approach.
2. **Implement:** make the smallest complete change for the behavior/risk class; preserve contracts and avoid stale,
   speculative, or unrelated work.
3. **Verify:** exercise real behavior where practical, including material failure, invalid/default input, contracts,
   and relevant data/security/privacy/concurrency/lifecycle/network/subprocess/performance/resource risks. Bound and
   clean up timeouts/retries/fanout/queues. Disclose mocks, skips, manual/static checks; mocks MUST NOT hide an
   otherwise unverified external, library, runtime, or API contract.
4. **Review/audit:** establish correctness and truthful evidence before polish. Every serious finding identifies an
   affected caller, future change, verification claim, or material risk.

## Phase Consequences and Severity

Planning persists material implications in existing scope, package, Seam, risk, and verification fields. Code-writing
roles MUST fix material in-scope risk before handoff or use their existing blocker/scope route. Review-code retains
its own two-tier BLOCKING/ADVISORY authority: maintainability-only observations stay advisory unless independent
evidence establishes correctness, security, privacy, safety, data, or stated-contract failure. Package verification
and final audit retain frozen checklist/SPEC Acceptance authority and gain no smell checklist or automatic gate.

Shared classifications use the strongest evidence: **BLOCKER** for correctness/safety/security/privacy/data/caller-
contract/trust/migration/required-verification failure; **CODE-QUALITY** for concrete maintainability risk with
explained brittleness, cost, test burden, misuse, or defect surface; **ADVISORY** for optional preference or clarity.
The consuming phase decides the consequence. Stop rather than invent requirements or accept unapproved scope,
dependency/service, destructive action, credentials/facts, migration, or material risk tradeoffs.

## Quality Contract Evidence

Material implementation/repair reports MUST use existing proof/report surfaces and include:

```markdown
Quality Contract Evidence:
- Inspection: <contracts, conventions, defects, and unknowns>
- Design: <owner, caller contract, trust boundary, errors, and locality>
- Risks: <material success, failure, edge, safety, data, maintainability, or resource cases>
- Affected artifacts: <code, callsites, tests, docs, schemas, and generated artifacts>
- Verification: <checks and disclosed limits>
- Rule exceptions: <MUST/ground-rule exception and justification, or none>
```

Cite existing proof rows/reports rather than restating them. MUST NOT create a standalone quality report, artifact,
registry field, lifecycle state, command ledger, or per-smell results.
