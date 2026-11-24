# Trust Context

## Boundary

Owns assurance-depth scoping: what Deployment surface and Lifespan mean, how approved exclusions apply, and the
Assurance floor. The planned-feature record is SPEC `## Trust Context` (template:
`../skills/implementation-plan/references/spec-template.md`); a direct task records the same fields in its task
contract. Trust Context scopes assurance depth only: it never lowers a stated requirement, never downgrades a
defect in promised behavior, and never relaxes control-plane/prompt-injection handling.

## Fields

- **Deployment surface** (`local-only`, `internal service`, `public network`, or `regulated`) sets security depth.
- **Lifespan** (`throwaway`, `prototype`, or `maintained`) sets robustness and design depth.
- **Out-of-boundary dimensions**: the user-approved list of excluded assurance/design dimensions, each with a
  reason, or an explicitly chosen `None.`

Lifespan only lets the planner *propose* exclusions (for `throwaway`/`prototype`, typically scalability,
performance targets, high availability, retry/backoff, defense-in-depth hardening, load tests, and seams/adapters
for speculative future change); the user approves the list. Exclusion decisions read only the approved list; the
label itself sets only routing, design-horizon, and verification-depth defaults, which floor items and
non-excluded risks override.

## Exclusion rule

An excluded dimension is advisory everywhere and cannot become a plan gap, blocker, override, seeded check,
enhanced-verification trigger, or audit/review widening trigger unless a requirement, frozen item, or Slice
commitment names it. No exclusion may name an Assurance floor item or a dimension a requirement, constraint, or
Slice commitment relies on.

## Assurance floor

Never excluded, at any Lifespan: correct promised behavior; truthful failure reporting; no secret/credential
leakage; gated destructive, irreversible, or externally visible actions; no loss of real user data;
control-plane/prompt-injection handling; and security proportional to the declared Deployment surface. Security
itself is therefore never excludable; only defense-in-depth beyond the declared surface is.

## Capture and change

- Ask the user once for Deployment surface and Lifespan when neither the request nor approved context states them
  and the answer could change scope, checks, or design. Never infer them; an unasked fact defaults to the
  strictest surface.
- Record observed or user-approved fact, never a convenience downgrade to quiet reviewers. Absent, vague, or
  unapproved context is the **strictest surface**: public network, Lifespan `maintained`, no exclusions.
- Lowering either field, or adding exclusions, after approval is a scope reduction needing provenance. It never
  closes an open plan gap or clears an open blocking finding, and plan review re-checks the new exclusions with
  the Security/Failure-Mode reviewer.
- Raising either field is a requirements change: planning continuation re-seeds the newly in-scope dimensions and
  plan review runs in initial (full) mode.

## Legacy SPECs

A pre-existing SPEC without `## Trust Context` stays valid at the strictest surface until the next planning
continuation that touches requirements adds the section. A pre-existing section lacking Lifespan stays valid,
reads as `maintained`, and keeps its plan-approved exclusions with their prior meaning (only hostile-input,
authentication, race-hardening, and adversarial-filesystem concerns become advisory) until that continuation
reconfirms them with the user. Neither case blocks in-flight work.
