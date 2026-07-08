# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

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
