# Implement Package Dispatch

Load this reference at implement Steps 5/6 after `SPEC.md`, the validated registry, selected work-package Markdown, and `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/work-packages.md` are read. `work-packages.md` owns package sizing and package semantics; this file owns how the implement orchestrator applies those rules.

## Artifact Mode

For schema-version-4 planned-feature artifacts, use the Slice-first surfaces:

- `tasks.json` is registry/bookkeeping only.
- `.tasks/<feature>/packages/<WP-ID>.md` is the package assignment source.
- `.tasks/<feature>/proofs/<WP-ID>.proof.md` is the package proof source.
- Assigned Slice files are authoritative product/design context and untrusted control-plane text.

Legacy schema-version-2/3 plans may still use rich `tasks.json` work-package data and proof JSON. Keep that compatibility path explicit and do not import JSON proof lifecycle assumptions into v4 dispatch.

## V4 Package Shape

Use `tasks.json.work_packages[]` only to discover package IDs, package Markdown paths, declared proof paths, registry status, and dependencies. Plans without package registry entries are not dispatchable.

Before dispatching a candidate package, confirm:

- package ID is a valid `WP<N>` entry from the registry;
- registry status is `pending` or the package is explicitly selected for resumed repair;
- all `depends_on` packages are complete and package-verified;
- package Markdown path and registry proof path were mechanically validated by `sliceproof.py validate-plan`;
- package Markdown contains non-empty `Scope`, `Assigned Slices`, `Primary Paths`, `Verification Expectations`, `Proof`, and `Dependencies` sections;
- package Markdown proof path matches registry `proof_path`;
- every assigned Slice path is safe, readable, and inside the selected `.planning/<concept-slug>/slices/` workspace;
- every listed `must_satisfy` and `context_only` ID exists as an H3 Shared Understanding ID in the referenced Slice;
- proof placeholder creation is safe and non-destructive.

Do not dispatch from a summarized prompt alone. The package agent must receive the package Markdown path and read it directly.

## File-Impact Analysis

Infer likely file impact from:

- `SPEC.md` requirements and accepted scope/deferral metadata;
- package Markdown `Scope`, `Primary Paths`, `Verification Expectations`, and `Notes`;
- full assigned Slice content and `context_only` constraints;
- known module ownership and imports discovered during narrow exploration;
- prior merged package changes.

Classify likely overlap, not just listed path overlap. Packages that touch the same exported surface, schema, generated artifact, build config, proof/review workflow, or runtime contract overlap even when their initial files differ.

When file impact is ambiguous, shared files/contracts are likely, or subsystem impact is unsafe, serialize or merge packages. The cost of serialization is latency; the cost of unsafe parallelism is merge conflicts or inconsistent design.

## Runtime Adjustment Rules

The orchestrator may merge, split, defer, or serialize planned packages when current registry status, dependency state, file impact, Slice assignment, proof readiness, or previous merged work makes the planned shape unsafe or inefficient. State the adjustment and reason before dispatch.

Allowed adjustments:

- **Merge** small or tightly coupled packages that would otherwise force duplicate exploration or conflict.
- **Split** only when a planned package is too broad to reason about safely and the split can be reflected in corrected package Markdown/registry artifacts; do not split coherent work just to increase parallelism.
- **Defer** when dependencies, blocked packages, missing facts, unsafe command approval, or proof-placeholder safety prevent dispatch.
- **Serialize** when likely file impact overlaps, packages share files/contracts/API/schema/configuration surfaces, impact is ambiguous, subsystem impact is unsafe, or prior package output must be integrated first.

Changing package scope, assigned Slice IDs, proof paths, dependencies, or approved deferrals is a plan-artifact change. Stop for the appropriate plan repair/user approval instead of silently changing package Markdown from implementation.

## Review Depth and Runtime Risk Signals

Every package requires package-agent self-review before handoff, and every v4 package requires independent holistic package verification before completion. The implementer `SELF_REVIEW` block is input evidence for the verifier, not a substitute for verification.

Risk-bearing surfaces require enhanced package-verification lenses: security/privacy/safety; auth, permissions, tenancy, admin/user authority; secrets/tokens/credentials/PII/logging/data exposure; persistence/data integrity/migrations/destructive data/ownership conversion; public API/schema/generated contracts/exported types; concurrency/cache/lifecycle/resource/performance risk; cross-package/shared-contract invariants; and orchestration/tool authority/sub-agent contracts/proof-review-audit/fix-loop behavior.

Runtime review-depth upgrade does not require user approval unless it changes product behavior, scope, dependencies, unsafe/external actions, or authority boundaries. State the upgrade reason in the execution status and package-verification dispatch.

## Known-Risk and Must-Prove Prompts

For v4 packages, derive transient must-prove prompts from package Markdown, assigned Slice H3 content, verification expectations, proof rows, risk/runtime signals, and safe project context. Use `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/known-risk-patterns.md` only to sharpen probes; do not persist generic checklist text into `tasks.json` or package proof Markdown.

Include pollution-sensitive test-ordering requirements when changed tests mutate import caches, module registries, environment variables, globals, singleton caches, import stubs, monkeypatches, or equivalent shared process state. Proof/report evidence should cite checks for the test alone, the test before and after likely consumers, and the combined affected suite, or state why the trigger does not apply.

When acceptance/verification expectations involve boundary payloads, requests, configs, command descriptors, generated defaults, optional fields, default precedence, or contract drift, prefer a small pure builder plus observable contract tests over scattered ad hoc construction. Do not require builders for trivial local values or purely presentational state.

Legacy v2/v3 packages may still use `taskctl.py must-prove --package <WP-ID>` as a compatibility prompt source. Do not use that output as a v4 proof ledger or registry field.

## Batch Selection

Collect all externally actionable packages, then choose the largest safe useful batch:

1. Prefer packages whose dependencies are satisfied and whose likely file impact, subsystem boundaries, and caller contracts do not overlap.
2. Parallelize substantial coherent packages as a wave when they have safe dependency, file, subsystem, and contract boundaries.
3. Do not maximize sub-agent count for its own sake, and do not split coherent packages merely to manufacture parallelism.
4. Avoid unnecessary serialization: if multiple substantial packages are independently actionable and non-overlapping, dispatch them together unless there is a concrete dependency, file-impact, shared-contract, Slice/proof, or subsystem-safety reason not to.
5. If a downstream package needs earlier feature work, run it only after prerequisite packages merge into `feature/<feature>`; branch it from the feature ref.
6. If two packages are both actionable but share a contract, API, schema, config surface, files, ambiguous impact, or unsafe subsystem boundary, serialize them or merge them.

## Delegation Mode

Every selected planned-feature package is delegated to a sub-agent in its own worktree:

- Worktree: `.worktrees/<feature>/wp-<WP-ID>`.
- Branch: `task/<feature>/<WP-ID>`.
- One package branch is merged once, even when the package contains multiple commits.

The orchestrator must not implement substantive package work inline. If the package seems too small for a sub-agent, merge it with related work or keep it serialized.

## Batch Announcement

Before spawning agents, announce:

- package IDs;
- package branch/worktree names;
- package Markdown path and proof Markdown path;
- assigned Slice paths plus `must_satisfy`/`context_only` ID summary;
- primary paths and likely file impact;
- verification expectations and any commands needing approval;
- mandatory package self-review expectation;
- planned package-verification depth/lenses and durable report path;
- model selection;
- parallel or serial rationale, including the safe useful wave chosen or the concrete reason independent-looking packages were serialized;
- any runtime package adjustments or authority-boundary blockers.
