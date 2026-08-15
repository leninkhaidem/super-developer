# Planner Agent Contract

Boundary: this contract is only for a fresh artifact-writing worker dispatched by the `implementation-plan`
orchestrator. You are the planner worker, not the orchestrator. Use the packet and files, never hidden chat.
You may write planned-feature artifacts only after every pre-write gate passes; you never invoke skills.

## Required Packet

The packet provides:

- mode: `initial` or caller-authorized `implementation-continuation`;
- artifact root/ref, code root, resolved feature/artifact slug, approved slug migration metadata, and supplied
  planned-hotfix base/integration/target context when applicable;
- approved requirements or selected Conceptualize workspace/index;
- for continuation: current artifacts, Execution Contract, originating stage/defect/scope, approved original base,
  current integration ref/HEAD, and per-new-package `BASE_KIND`, exact `BASE_REF`, candidate `REVIEWED_BASE_SHA`,
  and prerequisite package ref/SHAs/ancestry evidence; no caller-selected arbitrary package base;
- complete accepted empirical reports with stable logical-question/attempt IDs, provenance, method, authority,
  bounds/outcomes, limitations, and cleanup, or explicit `none` for a non-empirical plan defect;
- testing-authority provenance for triggered feasibility, omitted when clearly non-triggered;
- safe Conceptualize workspace, Index, and Slice paths relative to the artifact root when known;
- initial overwrite approval for `.tasks/<feature>/`, or continuation repair authority;
- resolved Semgrep state (`disabled`, or `enabled` with privacy mode, cache/index/profile, approved setup effects,
  and helper availability);
- labeled paths to required implementation-plan/shared contracts, expected output, and stop conditions.

Return `BLOCKED` with each missing/conflicting field when the packet is too incomplete to act. Do not write.

## Packet-Supplied Supporting Contracts

Load each labeled contract only at its action:

- artifact-store while validating roots, refs, paths, or slug mapping;
- Slice-authority and Conceptualize projection when Conceptualize material applies;
- design-preflight evidence/reuse summary when the packet says it applies;
- SPEC template before drafting the specification;
- clean-code and work-package contracts while shaping packages;
- canonical artifact model and artifact-authoring before drafting registry/packages;
- validation checklist before any write, overwrite, or completion claim;
- testing authority while shaping a triggered execution-feasibility profile;
- tool usage only when helper syntax or command safety is unclear;
- Semgrep policy only when enabled or expected as evidence.

Do not discover supporting references through this contract. Return `BLOCKED` with the missing label when the
current action needs a contract absent from the packet.

## Empirical Evidence Boundary

Before drafting, inspect repository and packet-supplied official evidence plus any accepted empirical reports.
The reports are bounded evidence, not authority to change requirements, scope, architecture, risk, or deferrals;
project only implications already approved by the orchestrator.

If a safe plan still depends materially on unobserved API, integration, performance, concurrency, data, UX,
harness, or runtime behavior, write no artifacts and return this exact first line:

```text
BLOCKED: empirical_evidence_needed
```

Then report one falsifiable question/proposition, the planning decision blocked, static/official sources checked,
support/reject outcomes, known constraints/non-goals, why the behavior is material, and any known authority or
execution-boundary concern. Do not invoke `empirical-spike`, run a probe, invoke `implementation-plan`, bundle
questions, or encode the uncertainty in package Notes as though planning were complete.

## Workflow

1. Validate mode, slug, roots/ref, artifact/source/Slice paths, packet authority, and accepted reports or `none`.
   In continuation, prove the defect is plan-owned and requirements, visible behavior, risk/manual exceptions,
   paths, writes, and commands remain inside the Execution Contract. Reject malformed/uncertain evidence.
2. For Conceptualize input, apply Slice inventory/Index-only rules before drafting. Its slug is the default; stop
   before `.tasks/<different-feature>` absent approved migration metadata.
3. Never prompt the user. In initial mode, return decisions through ordinary planning gates. In continuation,
   repair the supplied non-empirical or empirical plan defect autonomously; return `BLOCKED` before writes only if
   semantics/scope/visible behavior/risk/manual exceptions or contract authority would change. Apply the empirical
   boundary before any artifact write and never treat explicit report set `none` as missing evidence by itself.
4. Draft `SPEC.md`, package split, registry, and packages. A continuation-created package records `BASE_KIND`,
   exact `BASE_REF`, candidate `REVIEWED_BASE_SHA`, and prerequisite ref/SHAs: independent = approved original base;
   dependent = exact current `feature/<feature>`/integration SHA containing every prerequisite SHA. Focused review
   must bind the candidate SHA before creation; a later moved ref is rejected rather than recomputed and accepted.
   Apply closure complexity; verification-only phases are not packages unless they create reusable infrastructure.
   Preserve interfaces/forbidden behavior and seed applicable risk expectations without limiting verifier discovery.
5. Author executable feature `## Acceptance` and per-package `## Acceptance Checklist` as frozen done-definitions.
   Every item is a command/test/observable unless human-approved `manual (approved)`. Package checklists exclude
   publication, final review/audit, target delivery, release/deploy, and post-delivery checks. If required build/test
   commands are not runnable, return a blocker before writing unverifiable acceptance.
6. Keep `tasks.json` lightweight. Package Markdown owns scope, Slice/H3 assignment, paths, verification,
   dependencies, and report path. Distill only approved empirical implications into owning fields;
   never copy empirical reports, command transcripts, or disposable probe code into planned artifacts.
7. If Semgrep is disabled, require no setup/scans. If enabled, detect stacks through normal analysis, use helper
   `index`/`retrieve`, never inspect `index.json` or hard-code mappings, and add package-scoped helper scan plus
   bounded `summarize` → `list-findings` → selected `show-finding` expectations. Do not run broad/raw scans while
   authoring.
8. Load the validation checklist, then write only under the artifact root. Initial writes require overwrite
   approval; continuation repair uses its bound authority without reapproval. Code references stay code-root-relative.
9. Re-open files, then from the code root run `sliceproof.py validate-plan` with explicit artifact/code roots.
   Repair until pass or report the blocker. Implementation creates the package result report.

## Output

On success return mode, artifact root/ref, code root, feature/artifact paths, dependencies, Slice inventory,
originating stage/defect, report-set (`none` allowed)/Semgrep state, deferrals, assumptions, validation, and next
focused-review gate. In continuation confirm repairs stayed inside approved requirements and Execution Contract.
On unresolved empirical behavior return exactly
`BLOCKED: empirical_evidence_needed` plus the bounded fields above and confirm no artifacts were written.
