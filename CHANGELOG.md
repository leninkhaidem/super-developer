# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

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
