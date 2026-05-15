# tasks.json Authoring Guide

Load this when drafting `.tasks/<feature-name>/tasks.json`.

`tasks.json` is the implementation plan: task decomposition, traceable acceptance criteria, accepted planning decisions, context bundles, work packages, and verification hints. Keep `SPEC.md` requirements-only.

## Example Shape

```json
{
  "schema_version": 2,
  "feature": "<feature-name>",
  "title": "Human-readable feature title",
  "description": "One-line summary of what this feature delivers",
  "created_at": "<ISO 8601>",
  "status": "planned",
  "design_decisions": [
    {
      "id": "DD-1",
      "decision": "Concise accepted design decision",
      "rationale": "Why this decision best satisfies the requirements and constraints",
      "alternatives_considered": ["Alternative considered and why it was not chosen"],
      "source": "design-preflight"
    }
  ],
  "context_bundles": [
    {
      "id": "CTX-1",
      "title": "External/runtime contract title",
      "required_for": ["WP1"],
      "sources": [
        {
          "type": "docs",
          "path_or_url": "https://docs.example.invalid/contract",
          "claims": ["Specific behavior implementers must not infer or mock."]
        }
      ],
      "verification_required": ["Tests must use the documented/captured contract shape for this boundary."]
    }
  ],
  "work_packages": [
    {
      "id": "WP1",
      "title": "Short package title",
      "description": "Coherent implementation bundle delivered by one sub-agent.",
      "task_ids": ["P1-T001"],
      "depends_on": [],
      "parallel_safe_with": [],
      "primary_paths": ["path/to/module/"],
      "verification_commands": [],
      "risk_tags": ["library-contract"],
      "required_context_bundles": ["CTX-1"],
      "targeted_review_required": true,
      "rationale": "Why these tasks should share one implementation context."
    }
  ],
  "phases": [
    {
      "id": "P1",
      "name": "Phase name",
      "description": "What this phase accomplishes as a unit",
      "order": 1,
      "tasks": [
        {
          "id": "P1-T001",
          "title": "Short descriptive title",
          "description": "WHAT to build and key constraints. References affected files/modules. Does not prescribe exact code or implementation steps.",
          "status": "pending",
          "dependencies": [],
          "acceptance_criteria": [
            {
              "id": "P1-T001-AC1",
              "criterion": "Specific, verifiable outcome.",
              "source_refs": [
                { "type": "spec_req", "id": "REQ-1" },
                { "type": "spec_ac", "id": "AC-1" }
              ],
              "verification_hint": "Optional proof hint, command, edge case, or contract constraint."
            }
          ],
          "required_context_bundles": ["CTX-1"],
          "context": "Why this task exists — the SPEC.md requirement or acceptance criterion that motivated it."
        }
      ]
    }
  ]
}
```

Use `schema-reference.md` for a concise field map. The machine contract is `${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/validate-tasks-json.py`.

## Design Decision Guidance

- Always include top-level `design_decisions`; use `[]` when none are worth preserving.
- Persist concise accepted decisions only, not full reviewer debate, discarded comments, transient Preflight Brief content, or raw spike notes.
- Record decisions that materially affect implementation boundaries, verification, security/privacy/safety posture, compatibility, sequencing, or task decomposition.
- If the user or repo context requires building on top of another feature branch, record the planned implementation base/target refs as a design decision so `implement` and `review-code` do not default silently to `main`.
- Use `source: "design-preflight"` for decisions accepted from preflight resolution. Use `source: "planner"` for planner decisions and accepted empirical spike outcomes adopted by the main agent.
- Do not record obvious restatements of SPEC requirements.
- Keep rationale in `tasks.json`; do not leak architecture rationale into SPEC.md.

## Task Authoring Guidance

- Descriptions state WHAT to build, not HOW to code it.
- Reference affected files/modules and existing patterns where useful, e.g. "Follow middleware pattern in `src/middleware/cors.ts`."
- Include constraints that are not safely discoverable from SPEC.md, referenced files, or immediate imports: external API contracts, security policies, performance bounds, or planning confirmations.
- Do not include exact code snippets, function bodies, line numbers, step-by-step instructions, library choices unless security-mandated, or generic defensive-coding advice.
- The `description` field covers WHAT + constraints. The `context` field covers WHY and links back to SPEC requirements or acceptance criteria.
- Target concise descriptions. If a description reads like a code tutorial, trim to intent plus constraints.
- Each task should be scoped for one focused agent session and grouped into phases that deliver testable increments.
- Dependencies must not be circular. Tasks in later phases may depend on earlier or same-phase tasks, but phase order must remain coherent.

## Acceptance Criteria Guidance

Criteria describe verifiable outcomes, not internal implementation steps:

- Good: "Returns empty list on any network or parse error."
- Good: "XML parsing is safe against XXE attacks; verification must prove unsafe external entities are rejected."
- Good: "Response latency is within the user-stated bound under the stated concurrency."
- Bad: "Uses `express-rate-limit` library" unless that exact library is a user-approved or security-mandated constraint.
- Bad: "Parser tries lxml first, falls back to html.parser."

Every task acceptance criterion is an object with:
- a stable `id` that implementers, verification ledgers, reviewers, and audits can cite;
- `criterion` as the observable outcome;
- non-empty typed `source_refs` pointing to SPEC IDs, design decisions, or context bundles;
- `verification_hint` when proof depends on an edge case, command, performance bound, library/runtime behavior, manual evidence, or no-mocks constraint.

Complete traceability is mandatory: every SPEC `REQ-*` and `AC-*` must be covered by at least one task acceptance criterion, and every task criterion must cite at least one valid source ref. Do not create floating criteria for nice-to-have work.

## Context Bundle Guidance

Use `context_bundles` only when future agents need durable ground truth not safely discoverable from SPEC.md and local code. Appropriate triggers include external API/library/runtime behavior, security/privacy policy, persistence semantics, command safety, cross-package assumptions, or verified spike findings.

A context bundle is not a design essay. It must contain source-backed claims and verification obligations. Implementers, fixers, reviewers, and auditors must be able to read the bundle cold and know what they must not infer, mock, or silently change.

## Task Substance Rule

Each task must have a self-contained, verifiable outcome: a change independently meaningful when described in one sentence.

Merge tasks that lack standalone intent. If a task is only a mechanical step toward another task's goal, such as adding an import, creating a type alias, creating an empty migration file, or adding a route constant, fold it into the task that gives it meaning unless the integration step itself has independent acceptance criteria.

Independence test: can a reviewer verify this task's acceptance criteria without seeing any other task? If no, merge it with the task it serves.

Description quality test: does this tell the agent WHAT to achieve, or HOW to code it? If it reads like a tutorial, trim it.

Small tasks can pass when independently verifiable and meaningful, such as adding rate-limiting middleware to auth endpoints or configuring CORS policy for a new API namespace.

## Work-Package Authoring Guidance

Use `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md` as the source of truth for package semantics, risk metadata, targeted review, and runtime adjustment.

- Create `work_packages` for every generated plan. Tasks remain the tracking unit; work packages are the delegation unit.
- Every task ID must appear in exactly one work package.
- Group tasks by subsystem, module, directory, API surface, UI flow, data model, or shared test surface.
- Prefer substantial coherent packages over one-task packages. A one-task package requires a rationale that the task is large, risky, or naturally isolated.
- A package may include tasks with internal dependencies when one sub-agent can complete them sequentially in the same context.
- Use `depends_on` only for dependencies on other work packages.
- Fill `primary_paths` with likely files/directories to inspect first when known.
- Fill `verification_commands` only with commands known to exist or strongly implied by the project. Use `[]` rather than inventing commands.
- Treat `verification_commands` as executable inputs: they must be scoped, deterministic, and known-safe. Unsafe, externally visible, credential/network-sensitive, dependency-installing, or overly broad commands require explicit Execution Contract approval before implementation runs them.
- Use `parallel_safe_with` conservatively. Default to `[]` unless likely file/module impact is verified. If two packages touch the same subsystem or files, combine or serialize them.
- Use package boundaries to keep caller contracts, migrations, failure modes, or cross-module invariants visible to one agent when needed.
- Use risk tags and `targeted_review_required` per `validate-tasks-json.py` and `work-packages.md`; do not copy a long taxonomy into plans or skills.
- Use `required_context_bundles` when a package depends on a bundle. Each listed bundle must also list the package or one of its tasks in `required_for`.
