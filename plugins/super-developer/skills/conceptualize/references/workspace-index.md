# Conceptualize Workspace Index

## Boundary

Load only for a needed durable write or existing workspace resume. The parent's Durability Gate decides whether
anything should be saved; this reference defines the optional Index, not another capture/approval gate.
Resuming is read-only recovery: read existing context before selecting the next question. It needs no new checkpoint
and never creates files or worktrees by itself.

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
- <Index-only: settled outcomes, constraints, decisions, relevant rationale and accepted tradeoffs>
- <Slice-backed: pointers to the owning Slice/H3 blocks, not duplicate commitments>

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

## Lossless Index-to-Slice Transition

Apply only when a focused Slice becomes independently useful, not merely because planning is next:

1. Inventory every approved implementation-shaping Index commitment before adding the first Slice. Pure orientation
   and workspace metadata may remain in the Index.
2. Carry each commitment into stable H3 blocks in appropriate focused Slices. Preserve its scope, rationale,
   accepted tradeoffs, non-goals, verification expectations, useful evidence, and user-decision provenance where
   present; do not invent missing details or narrow commitments during migration.
3. Keep open questions explicitly unresolved in the Index and relevant Slice question sections, not as approved
   H3 commitments. Preserve associated approved decisions and deferrals.
4. Verify every original commitment maps to complete Slice/H3 content before replacing detailed Index entries with
   pointers and returning a Slice-backed handoff. Leave one authoritative home for each commitment, not competing
   copies. The transition is faithful capture, not fresh product approval or permission to drop scope.

## Stop

Do not write if path/overwrite safety is uncertain or the update invents, narrows, defers, removes, or contradicts
an obligation without user authority. Open questions may be documented, but planning/execution readiness cannot
rely on unanswered material questions or hidden chat. Existing Slices cannot be bypassed by calling the Index complete.
Stop an Index-to-Slice transition that would lose approved context or leave a material commitment only in the Index.
