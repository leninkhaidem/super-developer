# Implementation Artifact Authoring

## Contract

Use this contract while choosing deliverable mechanisms and acceptance checks, including settled designs and
continuations. Before drafting registry/package files, apply the packet-labeled canonical artifact model; it owns
file shapes and templates. Write `.tasks/`, Slice inventory, and declared result paths under the artifact root;
source/plugin/test paths are code-root-relative. Registry is bookkeeping, package Markdown owns assignment, and
`report_path` names the later independent result. Missing contract labels or safe write authority are `BLOCKED`.

## Smallest Complete Deliverable

- Separate required outcomes and approved constraints from suggested mechanisms. A variable, class, flag, or
  architectural sketch does not become a requirement merely by appearing in a discussion or earlier draft.
  Preserve explicit user/Slice commitments; propose changes to those through the existing decision route.
- Start with the existing owning code and a concrete end-to-end path. Prefer reuse or a local change when it meets
  the accepted behavior and risks; do not copy an existing defect or force reuse across an unsuitable boundary.
- For non-obvious added state, markers, abstractions, configuration, dependencies, retry policies, or extension
  points, compare removal or reuse with the proposal: what accepted outcome or evidenced failure would the simpler
  alternative miss? If none, cut the addition. A new requirement/check written to describe that addition is not
  independent justification. Hypothetical future needs, agent convenience, and ease of checking are insufficient.
- Keep policy and mutable state with the appropriate owner. Pass policy details across an interface only when the
  consumer's behavior needs them. Where correctness depends on a check and subsequent action, avoid splitting their
  authority or creating a check-then-act gap; reuse an existing safe operation before adding coordination machinery.
- Retain necessary validation, security, failure handling, compatibility, and verification. Small changes can be
  high risk. If simplification changes approved behavior, scope, or risk acceptance, stop for the owner to decide.
- Apply this reasoning while drafting, not as another review stage. Record only material decisions and rejected
  simpler alternatives in existing Scope/Notes; create no per-element justification ledger or new artifact.

## Acceptance Design

Apply to feature Acceptance and package checklists:

- Derive checks from required outcomes, approved constraints, and evidenced risks—not from every sentence or step
  in the proposed implementation. Keep implementation instructions in Scope/Notes and test details in tests.
- One item owns one coherent behavioral claim at an observable boundary. Success, failure, and boundary cases for
  that claim may share an item and a parameterized test or scenario suite. Split independently meaningful outcomes,
  not every assertion, input, phrase, or case. Preserve coverage of every material obligation.
- For each behavioral claim, identify a plausible wrong implementation and how the proposed check would reject it.
  Use the existing expected-result/failure description; no extra per-item field is required. A command that runs
  successfully but also passes for that wrong implementation is not adequate evidence.
- A grep or structure check proves only the literal artifact property it inspects. It is appropriate when that
  property is itself required, or as supporting evidence; it cannot prove runtime behavior, agent decisions, or
  enforcement merely because their descriptions appear in a file. Use a representative behavior/scenario check
  for those claims, or surface a precise `manual (approved)` verification for user approval. Do not invent a weak
  executable substitute to avoid acknowledging an automation gap. If no legitimate check meets the existing
  executable package floor, return a feasibility blocker rather than inventing an obligation to satisfy it.
- Review the resulting set for duplicated outcomes, supporting test cases promoted into obligations, and checks
  that only enforce an unnecessary design choice. Consolidate without losing distinct failure coverage. There is
  no numerical cap; a large set needs distinct outcomes/risks, not repeated wording checks or process completion rows.

## Registry

Use the supplied canonical registry template with these authoring rules:

- `feature` matches the safe slug and `.tasks/<feature>/`; a Conceptualize slug changes only with approved
  migration metadata. `spec_path` names the written SPEC.
- `authoritative_slices` is the full safe existing Slice inventory. It is empty only for chat-only, Index-only, or
  no-Slice plans with no authoritative Slice file.
- Package entries contain only `id`, `path`, `report_path`, `status`, and `depends_on`. Do not copy scope, H3
  assignment, primary paths, verification, evidence, findings, command output, or lifecycle history into them.
- IDs are stable `WP<N>`. Gaps and registry reorder are valid; never renumber or reuse an ID after reorder, split,
  merge, deferral, or retirement. Replacements receive fresh unused IDs.
- Dependencies are ID-only durable prerequisites and match package Markdown; rationale belongs in Notes.
- All artifact paths are artifact-root-relative POSIX paths. Reject absolute, traversal, home, drive-qualified,
  empty-segment, symlink-escape, or out-of-root paths.

## Package Assignment

Use the supplied canonical package template and Slice-assignment shape. Write `- None.` when no Slice or dependency
applies. The helper requires `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`,
`Package Verification Report`, and `Dependencies`; Notes is optional. Acceptance is the frozen closed package
done-definition. Keep deferrals, verification-profile reasons, repair constraints, and sequencing rationale in Notes.

Retain these specialized Acceptance forms where applicable:

```md
- AC-2: <non-automatable outcome> — check: manual (approved) — verify: <step and expected result>
- AC-3: <forbidden behavior outcome> — check: `<test id>` — expected: <pass condition>
  — rejects: <wrong-but-plausible implementation this check fails against>
```

## Authoring Rules

- Scope states package-owned behavior and boundaries. Name every changed externally observable surface: UI, CLI,
  API/errors, generated or operator docs, examples, reports/exports, operator logs, SDK material, prompts, or
  templates. Delivered surfaces use audience/domain language and are actionable/redacted where needed. `WP`,
  `Slice`, `contract`, `seam`, `stub`, `placeholder`, and `fixture` are leakage indicators only when they carry
  internal planning/staging meaning; legitimate domain/API/operator/developer-diagnostic or escaped raw input is
  allowed when audience-appropriate.
- `Must satisfy` IDs are closure obligations represented by Acceptance items. `Context only` requires a concrete
  reason and cannot hide work. Every material H3 in the full inventory is assigned, justified as context, or
  durably approved as deferred/out of scope/rejected/narrowed.
- Every material expectation and `Must satisfy` obligation is covered by an Acceptance item satisfying Acceptance
  Design above: a meaningful executable check or an explicit user-approved `manual (approved)` exception. Coverage
  may be many-to-one for facets/cases of one behavioral claim, never to hide unrelated outcomes.
- An item proving a Slice `Forbidden behaviors` clause names `rejects:` with a counterfeit implementation its check
  would fail. Prefer observable consequences over structural assertions. Use implementation structure only when no
  observable signal exists, and state why.
- Primary paths are code-root-relative starting points, not hard boundaries. Declare the result path now; produce
  evidence later.
- Apply packet-labeled package closure/dependency rules. Expectations are package-specific and cover applicable
  commands, static inspection, edge/failure/default behavior, trust boundaries, data, security, privacy,
  performance, concurrency, generated contracts, no-mock boundaries, lifecycle, and audience surfaces. A single
  `not-applicable: <dimensions>` line may name only dimensions the SPEC Trust Context already excludes and this
  package does not touch.
- Seed applicable exact-interface, forbidden-behavior, interactive UI, retry/fail-closed, trigger-precedence,
  restart/reaper, cache, model/default, generated-default, and state-pollution checks; identify the triggering
  surface instead of copying a worksheet. Planner seeds never limit verifier discovery from scope, Slices, code,
  tests, expectations, and known failure modes.
- Unresolved material behavior blocks all writes: return `BLOCKED: empirical_evidence_needed` to the orchestrator.
  For non-blocking feasibility, record repository-backed sources/bounds and testing-authority provenance in Notes
  or expectations.
- Dependencies match the registry and represent consumed durable prerequisites, not convenience serialization.
  Put non-obvious output/contract/evidence rationale in Notes.
- Record `standard`/`enhanced` profile seeds and evidence/risk reasons in Notes or expectations, never registry
  schema. A seed does not authorize later ungrounded downgrade while its risk remains.

## Semgrep Expectations

Disabled Semgrep imposes no setup, scan, or internet requirement. When enabled, keep evidence package-scoped:

- refresh the stack profile through helper `index`/`retrieve`; never inspect `index.json` or hard-code mappings;
- invoke only `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...` with local configs,
  writing `<WP-ID>.semgrep.json` and `.semgrep-summary.json` under `.tasks/<feature>/semgrep/`; never require direct
  raw `semgrep` scans;
- cite raw/summary paths, digest, scan scope, and a bounded finding/no-finding summary in result evidence;
- consume via `summarize`, filtered/limited `list-findings`, then selected `show-finding`; excerpts require
  `--target` and the expected summary digest. Never dump raw JSON;
- use an integrated one-shot scan only for a concrete cross-package/shared-surface risk.

## Fail Closed

Do not write when proposed machinery lacks a required outcome/evidenced-risk justification; a required section or
result path is absent; assignment is hidden in the registry; checklist coverage, atomicity, meaningful verification,
or forbidden-behavior falsification fails; a Slice obligation is hidden; visible surfaces or audience checks are
missing; expectations are boilerplate; dependencies are inconsistent; or the package cannot be independently
verified through its declared report. Return approval conflicts rather than silently cutting required behavior.
