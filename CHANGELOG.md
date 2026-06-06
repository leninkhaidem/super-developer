# Changelog

All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog.

## [Unreleased]

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
