# Work Packages

Work packages are the delegation unit for Super Developer planned-feature implementation. In schema-version-4 Slice-first plans, package registry entries point to work-package Markdown assignment files; the Markdown package file, not `tasks.json`, carries package scope, assigned Slice H3 IDs, primary paths, verification expectations, dependencies, and proof path.

## Core Principle

Delegate substantial coherent work packages, not individual small tasks. Actively look for the largest safe useful wave of substantial packages that can proceed at the same time, then dispatch that wave in parallel. Preferred parallelism means reducing latency with coherent, non-overlapping work; it does not mean maximizing sub-agent count or splitting work purely to create more agents.

## Artifact Roles

For v4 Slice-first planned features:

- **Slice Markdown:** authoritative product/design source of truth.
- **Work-package Markdown:** authoritative package assignment.
- **`tasks.json`:** lightweight package registry/bookkeeping only.
- **Package proof Markdown:** package closure evidence against assigned `must_satisfy` Slice H3 IDs.
- **Package verification report:** durable package-local reviewer PASS/FAIL evidence before completion.

Legacy schema-version-2/3 plans may still use task acceptance criteria and proof JSON. Keep those compatibility paths explicit and do not duplicate rich assignment/proof evidence into v4 `tasks.json`.

## Package vs Task

- **Work package:** a coherent implementation bundle containing one package assignment and one package proof file.
- **Task:** a legacy/current tracking unit for older plans, or a human-readable sub-outcome when explicitly present.

In v4, package status in the registry is bookkeeping. It does not prove implementation, proof quality, package verification, final review, or audit readiness.

## Package Sizing

A good work package usually contains several related changes or one substantial/risky/naturally isolated change large enough to justify a dedicated sub-agent.

Prefer packages that are:

- coherent by subsystem, module, directory, user flow, data model, API surface, or test surface;
- large enough to justify sub-agent startup context;
- small enough for one agent to reason about safely;
- independently mergeable;
- clear about which paths to inspect first;
- explicit about assigned Slice H3 obligations and verification expectations.

Avoid one-task/tiny packages unless the work is substantial, risky, or naturally isolated.

## Package IDs

Package IDs use the `WP<N>` format with sequential numbering and no gaps (`WP1`, `WP2`, `WP3`, ...). Renumber when packages are reordered, split, or merged so the sequence stays contiguous.

## Dependencies

A work package may depend on earlier packages. For v4, dependencies live in both the registry `depends_on` array and package Markdown `## Dependencies`; they must match.

Internal sequencing inside a package is handled by the package agent. A package is externally blocked only when a dependency outside the package is not complete and package-verified.

## Parallel Safety

Mark or treat packages as parallel-safe only when likely file ownership, subsystem boundaries, Slice obligations, proof surfaces, and caller contracts do not overlap. When several packages are independently substantial and non-overlapping, prefer a safe useful parallel wave rather than leaving them serialized by default.

When overlap is ambiguous, files are shared, subsystem impact is unsafe, packages touch the same contract/API/schema/configuration surface, or proof/verification expectations depend on earlier output, combine or serialize packages. The cost of serialization is latency; the cost of unsafe parallelism is merge conflicts, inconsistent design, stale proof evidence, and invalid package verification reports.

## Primary Paths

`## Primary Paths` in package Markdown are starting points for code exploration, not hard boundaries. Agents should inspect those paths first and broaden only when imports, tests, Slice obligations, or verification expectations require it.

## Verification Expectations

For v4, package Markdown `## Verification Expectations` lists package-specific proof expectations: commands known to exist, static inspections, edge/failure cases, trust-boundary checks, no-mock constraints, generated-contract checks, or manual observations.

Treat package-provided commands as executable inputs. They must be scoped, deterministic, and known-safe. If a command is destructive, externally visible, credential/network-sensitive, installs dependencies/services, mutates data outside the worktree, or exceeds advertised package scope, the Execution Contract must stop for explicit user approval before it runs.

Every expectation must be addressed in the package proof Markdown `## Acceptance / Verification Closure` table. Do not create a second command ledger in the registry. Broad or expensive full-suite, generated-contract, typecheck, or lint commands should usually be batched as integration/final checks unless they are cheap by project convention or the only credible proof for an assigned package obligation.

## Package Proof Files

Each v4 package writes exactly one proof Markdown file:

```text
.tasks/<feature>/proofs/<WP-ID>.proof.md
```

The proof path is declared in the registry and package Markdown before implementation dispatch. The orchestrator creates the placeholder with `sliceproof.py create-proof`; the package agent fills evidence.

Proof Markdown must cover every package-assigned `must_satisfy` H3 ID and every verification expectation. It must not contain unresolved `TODO`, `OPEN`, `GAP`, unapproved `DEFERRED`, or unsupported `N/A` in required rows. Mechanical helper success is necessary but not sufficient; package verification and final audit judge evidence quality and semantic correctness.

If a review-code/audit repair touches a package's implementation, proof-cited files, verification expectations, assigned Slice commitments, package verification evidence, or audit handoff assumptions, refresh that package's proof Markdown before final readiness. Uncertain impact fails closed by refreshing candidate package proofs or recording explicit no-impact evidence; it is not silently ignored because one exact row was hard to identify.

Ignored `.tasks` proof artifacts are task-store files. Package branches must not force-add or commit them.

## Package Verification

Every v4 work package must pass one holistic package verification before completion. The verifier audits assigned Slice/proof obligations first, then reviews package code/evidence second.

Verification reads from files:

- work-package Markdown;
- full assigned Slice files;
- package proof Markdown;
- package implementation diff/code;
- package agent report and `SELF_REVIEW`;
- command/static verification output.

Verification returns a concise PASS/FAIL report and the orchestrator stores a durable receipt/report, conventionally:

```text
.tasks/<feature>/reports/<WP-ID>.package-verification.md
```

The report must bind to the reviewed package state: package ID, package Markdown path, proof path, Slice paths, worktree/commit or integration commit/range, verification commands/outputs reviewed, verifier identity, timestamp, verdict, Slice-closure review, code-review findings, repair/delta status, and any blockers.

A package cannot complete when the report is missing, failed, stale, bound to pre-repair evidence, contradicted by proof/code, or missing required state binding. A clean package-agent self-review is input evidence, not a substitute for package verification. Package verification is package-local and does not replace final integrated review-code or final audit.

## Risk and Review Lenses

V4 package Markdown and assigned Slices should carry package-specific risk and verification implications; do not add rich risk/proof ledgers to `tasks.json`. The orchestrator derives package-verification depth from package scope, Slice content, primary paths, verification expectations, runtime discoveries, and any legacy risk tags when present.

Risk surfaces that trigger enhanced lenses include:

- security, privacy, safety;
- persistence, data-integrity, migration;
- runtime-contract, library-contract;
- public API, exported types, schema/generated contracts;
- concurrency, idempotency, replay;
- performance, resource-bounds;
- cross-package integration;
- validation, traceability;
- orchestration, git-state, integration, subagent-contract;
- review, audit, fix-loop, quality-contract.

Documentation-only or reference-only packages still receive baseline package verification; risk determines depth/lenses, not whether verification runs.

## Runtime Adjustment

The implementation orchestrator may merge, split, defer, or reorder planned packages when current registry status, file impact, proof readiness, Slice assignment, or previous merged work makes the plan unsafe or inefficient. It must briefly state the reason before dispatching.

When runtime adjustment would change package scope, Slice H3 assignment, dependencies, proof path, or approved deferrals, the workflow must route through plan/package artifact repair or explicit user approval. Do not silently downgrade enhanced verification depth when a triggering risk remains.

## Anti-Patterns

- One work package per small task.
- Maximizing sub-agent count just because packages are independent.
- Leaving substantial, independent, non-overlapping packages serialized without a concrete dependency, file-impact, proof, or contract-safety reason.
- Splitting work that touches the same files, Slice obligation, subsystem, or proof surface.
- Bundling unrelated subsystems into a vague mega-package.
- Marking packages parallel-safe without checking likely file/proof/contract overlap.
- Giving a package no primary paths when relevant paths are known.
- Duplicating package scope, assigned H3 IDs, proof evidence, review receipts, or lifecycle ledgers into v4 `tasks.json`.
- Treating registry status, helper validation, package self-review, or a transient chat verdict as package proof.
