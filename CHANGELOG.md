# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

## [v1.40.5] - 2026-07-27

### Changed
- Changed package and repair implementation guidance to favor the smallest complete implementation and require self-review justification for added abstractions, flags, layers, configuration, dependencies, or extension points.

## [v1.40.4] - 2026-07-23

### Changed
- Changed Conceptualize to apply the shared right-sized-complexity rule before recommending design branches, cutting machinery not justified by accepted requirements or evidenced risk while preserving correctness, boundary validation, safety, and failure handling.

## [v1.40.3] - 2026-07-23

### Changed
- Changed planned-feature delivery to push and verify the remote feature branch after every accepted work-package merge while retaining all feature safety nets until whole-feature verification and cleanup gates pass.

## [v1.40.2] - 2026-07-21

### Changed
- Changed repair freshness to follow semantic impact rather than dependency descendants and to reuse equivalent-state evidence without redundant checks.

### Fixed
- Fixed repair clustering, cross-package scope authority, and package/review/audit role ownership so retries remain bounded and focused review cannot substitute for a complete same-freeze audit.

## [v1.40.1] - 2026-07-20

### Changed
- Changed Perspectives and Design Preflight routing to reuse sufficient current analysis and avoid forcing accepted low-risk work through planned-feature ceremony.

### Fixed
- Fixed package resizing after review expansion, package-versus-delivery acceptance, sidecar publication authorization, planned-hotfix execution, complexity-increasing review findings, and portable helper paths.

## [v1.40.0] - 2026-07-20

### Added
- Added frozen, executable feature acceptance checks and package acceptance checklists as the objective delivery definition.
- Added right-sizing guidance that identifies unnecessary complexity during design preflight and code review.

### Changed
- Changed autonomous delivery to a severity-based converging loop with delta-focused re-verification and at most three repair attempts per blocking cluster.
- Changed plan review to one approval gate, with security and failure-mode review joining the first wave when the planned surface requires it.
- Simplified package evidence and completion contracts so correctness, security, data-loss, and contract failures block delivery while non-blocking observations remain advisory.
- Changed planned-feature artifacts to require stable acceptance IDs with executable checks or explicitly approved manual verification; existing in-progress artifacts must be refreshed before validation.

### Removed
- Removed deliverable-matrix, receipt-grammar, and broad freshness-cascade requirements that created verification churn without proving behavior.

### Fixed
- Fixed package completion validation so fenced or duplicate verdicts cannot conceal a failing result.
- Fixed acceptance validation so placeholder requirements and empty executable or manual checks cannot pass the plan gate.

## [v1.39.0] - 2026-07-15

### Added
- Added a generic executable-verification preflight covering authority, prerequisites, safe targets, evidence capability, cleanup, redaction, and bounded termination.

### Changed
- Changed package planning so verification-only phases stay in package, wave, integration, or final verification unless they deliver substantial reusable verification infrastructure.
- Changed freshness routing to distinguish metadata rebinding, evidence-focused inspection, focused verification, and full verification while treating implementer and repair self-review as semantic inputs.
- Changed final readiness to freeze integrated code, artifacts, and runtime evidence before integration-focused review and selective audit reconciliation.
- Clarified verifier, reviewer, specialist, and auditor ownership to reduce duplicate work without weakening migration, security, data, or other sensitive-surface checks.
- Consolidated auto-resolve approval coverage for in-scope writes, execution, evidence collection, bounded reruns, and feature or sidecar pushes while preserving step-by-step and protected-action gates.

## [v1.38.0] - 2026-07-14

### Added
- Added testing authority with a bounded routine-safe local-command fallback and exact task-local authorization for focused one-off work.
- Added dedicated Fix Implementer contracts for diagnosis and review repair so delegated changes are bound to complete starting state and approved scope.

### Changed
- Changed testing workflow documentation from a universal prerequisite into durable authority for broad, reusable, delegated, browser, live-service, shared-data, and otherwise high-risk testing.
- Changed `diagnose-and-fix` approval to human-readable scope and delivery intent while keeping hashes, snapshots, leases, and drift checks internal.
- Changed implementation planning so a missing testing workflow does not block read-only or greenfield planning unless material execution feasibility requires testing authority.

### Fixed
- Fixed localized repair routing, review-state binding, and commit, push, merge, and cleanup gates so stale or concurrent repository state stops safely instead of being absorbed.
- Fixed bugfix and hotfix routing across active-feature, maintenance, and production-hotfix bases without using the root checkout for repair or delivery.

## [v1.37.0] - 2026-07-14

### Added
- Added closure-complexity package shaping and conditional execution-feasibility review/readiness so costly or uncertain evidence is resolved before broad fanout.
- Added a shared bounded-command runtime envelope, progress-sensitive repair circuit breaking, and non-gating execution observations.

### Changed
- Changed testing delegation and workflow guidance to require contract/fixture preflight, bounded staged execution, explicit process cleanup, and evidence-backed reruns.
- Clarified that package dependencies are sequencing prerequisites rather than automatic impact or staleness edges.

### Fixed
- Fixed revised skill routing and worker contracts to meet frontmatter budgets and remove hidden reference hops.
- Fixed repair impact handling to reconcile the actual delta, bound semantic cascades, preserve safe focused verification, and reject metadata-only circuit progress.

## [v1.36.4] - 2026-07-13

### Fixed
- Fixed agent-selected package hygiene checks so harmless blank lines at EOF do not block completion unless repository-declared checks require Git's default whitespace semantics.

## [v1.36.3] - 2026-07-13

### Added
- Added verifier-owned Test Review Scope receipts that record changed test populations as baseline-only, semantically sampled, or deeply reviewed with structured evidence.
- Added a deep-only `other-test-relevant` catch-all for novel test surfaces, with mandatory final-review and audit escalation rather than silent classification gaps.

### Changed
- Changed final planned-feature review to reconcile fresh package-local test receipts plus integration-only changes, avoiding routine deep rereview of already verified repetitive tests.
- Changed package completion and final validation to reject missing, malformed, stale, or explicitly unreviewed test scope; existing reports using the old shape must be refreshed.

### Fixed
- Fixed the package-report contract gap that treated omitted test scope as a blocker without providing a durable, mechanically enforceable way to record it.

## [v1.36.2] - 2026-07-13

### Added
- Added a Consumer Followability Gate for authored skills, including explicit inputs, decisions, safe defaults, action-point reference loads, and normal/risky dry runs for competent mid-tier agents.
- Added deterministic skill-audit regression coverage for frontmatter, local paths, reference ownership, progressive disclosure, and hard prompt-size limits.

### Changed
- Changed the development quality contract into a concise operational standard that mandates maintainable ownership, justified complexity, readable behavior, testable design, and evidence-based severity.
- Changed skill authoring to discover existing capabilities and governing contracts before drafting, separate read-only review from authorized edits, and preserve progressive disclosure without relying on inferred best practices.
- Strengthened orchestrator/worker guidance so workers read their packet and contract before acting and return `BLOCKED` rather than inventing missing authority.

### Fixed
- Fixed skill audits that could pass empty or duplicate frontmatter, mismatched skill names, broken Markdown or command paths, orphan references, hidden reference hops, and over-limit eager prompts.

## [v1.36.1] - 2026-07-09

### Added
- Added a dedicated testing strategy interview contract with confidence-first discovery, mandatory core domains, conditional browser/web prompts, and lightweight starters for test plans, plan-to-result reports, execution choices, and reliability/cleanup policy.
- Added prompt regression coverage for greenfield/no-strategy setup, candidate adoption and migration, plan/report contracts, conditional browser scope, and strict reliability defaults.

### Changed
- Changed testing workflow setup so explicit initialize, update, adopt, migrate, link, or revise requests interview users for both greenfield repositories and existing workflows before accepted workflow docs are written.
- Clarified new-test structure guidance so agents propose clean forward-looking plan/test/report locations, decide whether a coverage index is used, and leave legacy tests in place unless migration is requested.

## [v1.36.0] - 2026-07-08

### Added
- Added a dedicated `models.design-preflight` local preference for Design Preflight challenger dispatch.
- Added a canonical testing workflow contract and delegation packet guidance so test-authoring and test-execution agents always start from `docs/testing/workflow.md`.

### Changed
- Changed Semgrep guidance so the Semgrep reference reads only the `semgrep:` preference section.
- Changed the `testing` skill into a recommendation-led meta-skill that establishes, adopts, or migrates a project-specific testing strategy before delegating test work.
- Changed testing guidance to treat candidate testing docs and browser E2E references as optional strategy material until they are incorporated into the canonical workflow.

### Fixed
- Fixed testing delegation safeguards so agents cannot proceed to author or run tests when the canonical `docs/testing/workflow.md` entry point is missing or not accepted/current.

## [v1.35.0] - 2026-07-07

### Added
- Added the standalone `testing` skill for stack-agnostic test planning, test authoring, safe local test execution, and durable test evidence reporting.
- Added generic and web testing references, including browser E2E guidance for live-stack coverage, human-review artifacts, reproducible setup conventions, and approval-gated Playwright + Allure proposals.

### Changed
- Changed skill-authoring validation so nested skill reference folders are audited recursively, allowing testing guidance to scale under `core/`, `web/`, and future stack-specific parent folders.
- Updated Super Developer documentation and marketplace metadata to reflect the current 15-skill inventory, including `testing` and `readme-polish`.

## [v1.34.2] - 2026-07-02

### Changed
- Changed release cleanup guidance to default eligible local/remote feature branch, code worktree, and artifact sidecar cleanup in the Release Contract, keeping
  candidates only for hard blockers or explicit user requests.

## [v1.34.1] - 2026-06-30

### Added
- Added section-scoped Slice freshness so package verification reports bind only to referenced Slice H3 sections instead of whole Slice files, reducing unnecessary re-verification when unrelated sections change.
- Added `emit-state-binding` to generate canonical package report State Binding metadata for verifiers to paste without hand-computing digests.

### Changed
- Changed State Binding validation to distinguish `must_satisfy` section drift as a hard failure from `context_only` section drift as a non-blocking advisory surfaced through helper JSON output.
- Changed package verification, lifecycle, tool usage, review-code, and audit guidance to describe the section-scoped binding format and advisory routing.

### Fixed
- Fixed State Binding grammar handling so assigned Slice paths containing binding delimiters fail closed before the helper can emit an unparseable report binding.

## [v1.34.0] - 2026-06-29

### Added
- Added per-feature orphan artifact sidecar branches/worktrees so `.planning/` and `.tasks/` artifacts can stay durable without entering code branch history.
- Added root-aware `sliceproof.py` artifact-root/code-root handling for sidecar stores and deliverable-matrix file evidence.

### Changed
- Changed Conceptualize, implementation planning, implementation, review, audit, worktree, and release guidance to carry explicit artifact-root/code-root semantics.
- Changed sidecar lifecycle guidance to require checkpoint-only pushes and exact post-merge cleanup approval without merging artifact refs into deliverable branches.

## [v1.33.1] - 2026-06-25

### Added
- Added banner examples for readable ASCII and SVG README hero patterns so `readme-polish` can adapt user-supplied banner styles into legible repository front doors.

### Changed
- Changed `readme-polish` banner guidance to prioritize readable wordmarks, high contrast, short taglines, and a lazily loaded banner reference only when banner work is requested.

## [v1.33.0] - 2026-06-25

### Added
- Added package deliverable-completeness matrices and a `validate-package-complete` helper so package verification binds Slice and verification-expectation obligations to concrete evidence before packages are marked complete.
- Added upstream requirement-completeness challenges in Conceptualize, implementation planning, and plan review so agents explicitly ask what expected requirements, edge cases, defaults, or failure modes are missing before work packages are written.

### Changed
- Changed package lifecycle, implementation, review-code, and audit guidance so package verification is the primary semantic deliverable gate and final audit reconciles matrix completeness and freshness as a skeptic backstop.
- Changed planning and verification guidance to apply proportional post-gate refresh decisions based on impacted surfaces instead of file-type assumptions.

### Fixed
- Fixed matrix validation gaps so report-controlled worktree paths, non-exact interface dispositions, and unlabeled verification-output anchors cannot falsely pass package completion.

## [v1.32.1] - 2026-06-24

### Changed
- Changed `readme-polish` so Repository Polish Contracts can include GitHub and GitHub Enterprise repository metadata updates for About/description, website URL, topics/tags, and social preview handling.

## [v1.32.0] - 2026-06-24

### Added
- Added `readme-polish`, a README-front-door skill for creating or polishing a single repository README with an explicit checklist contract before README or banner writes.

### Changed
- Changed `conceptualize` so agents derive new concept slugs autonomously and ask about slug selection only when explicitly authorized or blocked by path-safety/collision concerns.
- Changed `diagnose-and-fix` to require evidence-confirmed root causes or explicit named blockers, keeping falsifiable hypotheses internal instead of presenting hedged likely causes as findings.
- Changed `skill-authoring` guidance to keep skill frontmatter descriptions concise, routing-only, and free of workflow detail or long trigger catalogs.


## [v1.31.3] - 2026-06-22

### Changed
- Changed `diagnose-and-fix` so diagnosis reports select one recommended route and ask approval for that route instead of asking users to choose the fix strategy.
- Changed localized bugfix delivery guidance to resolve implementer model preferences, require `review-code` before delivery claims, and push reviewed bugfix branches when approved.
- Changed worktree bugfix and release guidance to use approved `<base-branch>` and `<target-ref>` placeholders instead of hardcoding `main` for generic hotfix and cleanup flows.

### Fixed
- Fixed worktree bugfix and hotfix guidance that could imply committing before clean `review-code` verification.

## [v1.31.2] - 2026-06-22

### Changed
- Changed the release workflow so every contracted base-branch push is followed by local/remote base sync verification before tag creation, GitHub release publication, or cleanup.

## [v1.31.1] - 2026-06-22

### Changed
- Changed `diagnose-and-fix` so approved localized fix implementation is delegated to a fresh Fix Implementer sub-agent bound to the approved worktree, diagnosis packet, and regression plan.

## [v1.31.0] - 2026-06-22

### Added
- Added `diagnose-and-fix` as the single maintained issue diagnosis and bug-fix workflow, with structured evidence reporting and explicit approval before production-code changes.

### Changed
- Changed issue and `fix this` handling so agents diagnose first, route approved localized fixes through worktree isolation, and escalate broad or risky fixes to implementation planning.
- Replaced the old `spike-and-fix` skill path and documentation references with `diagnose-and-fix`.

## [v1.30.2] - 2026-06-22

### Changed
- Changed the implement workflow so package agents can install or add dependencies when exact commands and manifest or lockfile paths are approved in the Execution Contract, while unapproved dependency or service changes still stop the workflow.

## [v1.30.1] - 2026-06-21

### Fixed
- Fixed Semgrep setup guidance so agents ask before installing a missing local `semgrep` executable with `uv tool install semgrep`, and never install it during scan execution.

## [v1.30.0] - 2026-06-21

### Added
- Added optional privacy-first Semgrep validation for Super Developer workflows, using local helper-owned scans, task-scoped raw/summary evidence, and bounded finding views instead of raw JSON prompt dumps.
- Added falsifiable interface contracts to the planned-feature workflow: interface-bearing requirements are captured as exact, checkable obligations with explicit forbidden behaviors during conceptualization, carried through planning, and actively falsified at package verification and final audit, so vague requirements can no longer pass review while implemented incorrectly.

### Changed
- Changed model preferences so first-run creation writes every supported role key under `.superdeveloper/preferences.yml`, with the local preference file ignored by git.
- Changed planned-feature planning, implementation, review, and audit guidance so Semgrep opt-in, helper-only scans, advisory findings, and evidence freshness are handled through explicit local contracts.
- Changed skill-authoring guidance to reduce duplicate facts and file-role restatements while preserving safety-critical command/path repetition at lazy action points.

## [v1.29.10] - 2026-06-11

### Changed
- Changed implementation planning so work packages identify externally observable surfaces and verify audience-appropriate language without leaking Super Developer planning terms into delivered outputs.

## [v1.29.9] - 2026-06-10

### Changed
- Changed implementation planning so the skill delegates artifact drafting to a fresh planner using a compact planner-agent contract instead of drafting planning artifacts inline.
- Changed skill-authoring guidance so direct skill invocation remains the eager default while orchestrator/worker delegation details load only when that pattern is needed.

## [v1.29.8] - 2026-06-10

### Changed
- Changed release workflows so `prepare-only` integrates feature branches into the base branch, keeps changelog entries under `Unreleased`, pushes the base branch, and cleans up exact feature refs without creating tags or GitHub releases.
- Changed implement execution contracts so non-force pushes of the exact `feature/<feature>` ref are covered by default after integrated readiness while target/main pushes remain separate approvals.

## [v1.29.7] - 2026-06-09

### Changed
- Changed Conceptualize Slice capture so agents preserve implementation-shaping discussion details through a completeness rubric while keeping routine faithful captures low-friction and reserving user input for product decisions.

## [v1.29.6] - 2026-06-08

### Changed
- Changed package verification freshness rules so committed package states are reviewed once and binding-only report metadata refreshes no longer rerun semantic verification when reviewed inputs are unchanged.
- Clarified audit readiness so exact package commit report bindings remain valid after integration when ancestry and post-merge freshness prove the package state was unchanged.

## [v1.29.5] - 2026-06-07

### Changed
- Clarified Super Developer skill handoff instructions so downstream planning, spike, review, audit, and repair workflows require fresh Skill-tool or sub-agent invocations instead of inline execution.
- Changed the skill-authoring audit helper so every invocation enforces strict budget checks, even when `--strict` is omitted.

## [v1.29.4] - 2026-06-06

### Changed
- Improved the Super Developer Development Quality Contract with established principle grounding, maintainability and design-quality guidance, brownfield discipline, and material-risk calibration for planning, review, and audit workflows.

## [v1.29.3] - 2026-06-06

### Changed
- Changed Conceptualize handoff rules so sessions must create at least one Slice before handoff or planning instead of allowing Index-only handoffs.


## [v1.29.2] - 2026-06-06

### Fixed
- Fixed `skill-authoring` frontmatter so plugin skill loading no longer fails on malformed wrapped YAML descriptions.

### Added
- Added a skill-local `audit-skill.py` helper for deterministic skill frontmatter, metrics, local-link, and reference-budget checks.

## [v1.29.1] - 2026-06-06

### Fixed
- Fixed plugin and marketplace version metadata so installed plugin refreshes report the released version.

## [v1.29.0] - 2026-06-06

### Added
- Added a Slice-first planned-feature workflow built around Markdown Slice sources of truth, work-package Markdown assignments, Markdown package proofs, and the `sliceproof.py` helper.
- Added package verification and final-readiness artifacts that bind package proofs, reviewer reports, worktree state, and final validation.
- Added `skill-authoring` guidance for progressive disclosure, reference economy, density budgets, and authoring checks.
- Added release-specific contract, changelog, release-note, and git-safety references.

### Changed
- Reworked Super Developer skills around the Slice-first pipeline, clearer approval gates, and fewer stronger references.
- Changed planned-feature implementation to use `wp/<feature>/<WP-ID>` package branches, isolated package worktrees, and orchestrator-owned integration gates.
- Tightened final code review and audit contracts around integrated feature state, package coverage evidence, fix-verification closure, and non-bypassable proof/report requirements.
- Updated README docs to explain the Slice-first workflow and current skill surface.

### Fixed
- Hardened Slice proof validation against placeholder approvals, unassigned Slice claims, stale evidence, and bypassed proof closure.
- Fixed package verification report binding so reports must match proof digest, reviewed worktree state, package assignment, and verification output.
- Restored review-code safety contracts for global integration review, semantic big-diff batching, and dirty proof/report handling.

### Removed
- Removed legacy `taskctl.py`, rich JSON proof/task-state helpers, and the old validate-tasks-json workflow.
- Removed the unused tasks dashboard skill.
- Removed stale fragmented references and report templates superseded by consolidated Slice-first skill references.
