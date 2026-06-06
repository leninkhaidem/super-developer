# Changelog and Release Notes

Owns changelog updates and GitHub release-note prose. Load only when changelog or release notes are created or changed.

## Changelog Contract

When updating or creating `CHANGELOG.md`:

- Inspect the most recent released section first, plus `Unreleased` when present.
- Treat the proposed lightweight format below as the preferred future format.
- If the latest release already uses the lightweight format, continue it without a separate format prompt.
- If the latest release is incompatible, ambiguous, or no changelog exists, prompt through the Release Contract before editing.
- Offer: adopt lightweight format for this release section, preserve existing format for this release, or skip changelog update.
- If the user chooses the lightweight format, use it for the current release section.
- Do not rewrite historical release sections merely to normalize style unless the Release Contract explicitly names that migration.
- Inspect the actual release diff, merge contents, commits since the previous release tag, and existing `Unreleased` notes.
- Do not rely only on implementation summaries, task names, PR titles, or branch names.
- Include all user-visible or operator-relevant additions, changes, fixes, removals, deprecations, security items, migrations,
  compatibility changes, and docs/help updates.
- Avoid catch-all feature-only summaries that hide fixes, removals, migrations, or behavior changes.

## Default Lightweight Format

Use this format when the latest release already follows it, or when the Release Contract choice adopts it for this release:

```md
# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [vX.Y.Z] - YYYY-MM-DD

### Added
- <user/operator-visible addition>

### Changed
- <behavior, compatibility, migration, or operational change>

### Fixed
- <bug fix and affected user/operator outcome>
```

Rules for this format:

- Keep `[Unreleased]` above released versions.
- Use `## [vX.Y.Z] - YYYY-MM-DD` for release headings.
- Include only non-empty change-kind sections.
- Add compare/reference links only if the repository already uses them or the Release Contract explicitly creates them.
- Include the Keep a Changelog URL in the header only when creating a durable new convention.
- Mention Semantic Versioning only when the project uses SemVer.

## Classification

- Use `Added`, `Changed`, `Deprecated`, `Removed`, `Fixed`, and `Security` for kind-based headings.
- If adopting the lightweight format, use standard kind sections even when older history used topic/domain subsections.
- If the user chose to preserve the existing format for this release, keep topic/domain subsections and make kind clear in each bullet.
- Move applicable `Unreleased` entries into the new version section and recreate or leave empty `Unreleased` according to repo convention.
- If creating a durable changelog convention, include the Keep a Changelog URL in the header. Mention Semantic Versioning only when the project uses SemVer.

## Human Prose Rules

Write for users/operators, not Git history readers:

- Translate implementation details into outcomes: what changed, why it matters, who is affected, and behavior differences.
- Avoid commit prefixes (`feat:`, `fix:`, `chore:`), hashes, ticket IDs, internal function names, and file paths unless meaningful to users.
- Combine noisy low-level commits into coherent bullets. Split only when readers experience or operate changes separately.
- Use clear past-tense verbs and plain language.
- Mention tests only when coverage or validation is itself notable to users/operators.

Examples:

- Prefer: `Fixed Query Chat copy fallback so browsers without clipboard access no longer crash the chat UI.`
- Avoid: `fix: clipboard fallback`.
- Prefer: `Changed workspace creation so non-platform-admin users request new team workspaces instead of creating them directly.`
- Avoid: `refactor workspace permissions`.

## Release Notes

Draft GitHub release notes from the final release diff and changelog section in simple human language.
The notes must match the final release commit and tag target. Do not publish notes copied from stale drafts, task plans, or pre-merge summaries.

## Readability Pass

Before the release commit or publication, compare the notes against the release diff and previous tag. Revise when entries are missing, misclassified,
too implementation-heavy, copied from commits, or collapsed under `Added` despite fixes, removals, migrations, compatibility changes, or behavior changes.
