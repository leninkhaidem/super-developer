# Right-Sized Change Routing

## Boundary

Use before choosing exploration, direct task execution, or the planned-feature pipeline. This reference selects
work; it does not authorize implementation, commands, artifact creation, publication, or cleanup.

## Route by Need

- **Discussion:** when intent or a material decision remains open, use `conceptualize` or continue the current
  discussion. Invocation alone creates no files and implies no planning or implementation permission.
- **Direct task:** when the user requests execution of a clear, bounded, low-risk change with a known owning
  surface and credible verification, use the task-appropriate skill (for example `skill-authoring`,
  `diagnose-and-fix`, or `readme-polish`) or ordinary direct coding for a narrow code change. Do not invoke the
  package-only `implement` skill or manufacture `.planning/`/`.tasks/` merely to make this route fit that skill.
- **Planned feature:** use `implementation-plan` when the user explicitly requests a plan, or execution needs
  durable multi-package coordination, substantial cross-cutting design, unresolved implementation-shaping
  decisions, material risk acceptance, or separate ownership/evidence boundaries. Use the smallest coherent
  package set; one package is valid. Reviewed-plan approval precedes package execution.

Size alone does not establish low risk. Authentication, sensitive data, persistence/migration, public contracts,
concurrency, destructive actions, and uncertain verification warrant explicit assessment even for a one-file
change. If the direct route develops one of these planning needs, pause to resolve the decision or route to
planning; do not silently expand scope.

## Direct-Task Floor

Before writing, establish the accepted outcome, intended write scope, applicable safety/testing authority, and
how to verify it. A concise conversation summary is sufficient when it is complete and remains available to the
executor. Delegated or resumed work receives a self-contained packet; persist the smallest handoff when chat
context cannot be carried reliably. Existing authoritative Slices must be read and honored, not bypassed by
calling the work small.

After writing, run the applicable checks and report observed outcomes and limitations. Obtain independent code
review when the change's risk or task contract calls for it. Direct work does not claim planned-feature audit
PASS without the planned-feature artifacts and gates. No route permits invented requirements, skipped required
verification, destructive actions, or external publication without applicable authority.

## Planning Handoff

Conceptualize may finish with a chat summary, a compact Index, or focused Slices. Do not backfill Slices solely
because planning is next. A fresh planner must receive the complete approved requirements and decisions in its
packet or safe durable files; hidden conversation history is never a dependency. Existing Slices retain their
full inventory/projection/approval requirements. Explicit planning requests still produce the normal planned
artifact set; lightweight routing is not a silently weakened form of plan approval.
