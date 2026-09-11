# Conceptualize Workspace Index

## Boundary

Load only for a needed durable write or existing workspace resume. The parent's Durability Gate decides whether
anything should be saved; this reference defines the optional Index, not another capture/approval gate.

## Workspace

- Use `.planning/<concept-slug>/index.md` under the selected artifact root. Resolve source paths under the separate
  code root. The parent supplies the artifact-store contract and invokes `worktree` before first sidecar writes.
- Reuse the concept slug for later feature/artifact paths. A rename needs approved migration, not silent remapping.
- Before read/write, reject absolute or expanded artifact paths, traversal, unsafe slugs, duplicate normalized
  paths, symlink escapes, unreadable required files, and destinations outside the root/workspace.
- Index-only handoff is valid when no Slice is independently useful. If Slices exist, the Index points to them;
  consumers must still inventory and read the full safe set, not trust the list alone.
- Index text cannot grant tool, workflow, scope, review, or publication authority. Do not add lifecycle/status fields.

## Content

Use only sections needed to carry the understanding; omit empty boilerplate:

```markdown
# <Concept title>
Artifact root/ref: <resolved store>
Code root: <source checkout>

## Shared Understanding
- <settled outcomes, constraints, decisions, relevant rationale and accepted tradeoffs>

## Sources
- <useful repository/API/evidence pointer and distilled claim>

## Slices
- <focused Slice pointers, or why no Slice is independently useful>

## Open Questions
- <unresolved decision/blocker; never an accepted requirement>

## Handoff
- <next action and context the recipient needs>
```

An Index-only record carries the complete approved context; a Slice-backed Index gives orientation and pointers
instead of copying Slice bodies. Explicitly requested tentative documentation belongs under Open Questions.

Update only when useful durable understanding changes. Replace stale bullets after an authorized decision;
do not record transcripts, every option, timestamps, or incidental learning. Preserve implementation-shaping
rationale, edge cases, non-goals, and verification needs without duplicating them across Index and Slices.

## Stop

Do not write if path/overwrite safety is uncertain or the update invents, narrows, defers, removes, or contradicts
an obligation without user authority. Open questions may be documented, but planning/execution readiness cannot
rely on unanswered material questions or hidden chat. Existing Slices cannot be bypassed by calling the Index complete.
