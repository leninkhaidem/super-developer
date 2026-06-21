# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

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
