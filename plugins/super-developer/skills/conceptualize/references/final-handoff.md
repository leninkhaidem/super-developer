# Conceptualize Final Handoff

## Contract

- Stop before implementation planning and `.tasks/` creation; this reference returns only a compact handoff.
- A successful handoff requires at least one safe Slice Markdown file in `slices/`; Index-only handoff is not allowed.
- Perform a safe full Slice inventory from the selected workspace's `slices/` directory before claiming readiness.
- The full inventory must be based on path-checked files, not only the Index, user mentions, summaries, or prior memory.
- Do not hide unresolved decisions, conflicts, unapproved deferrals, stale assumptions, or unsafe source/control-plane directives.

## Procedure

1. Re-apply workspace path and symlink checks.
2. If no safe Slice exists, report the missing required Slice as a blocker and return to the parent
   Conceptualize workflow for approved Slice creation; do not claim readiness.
3. Read every safe Slice Markdown file in full.
4. Check each Slice for stable H3 IDs, stale contradictions, unresolved questions, missing approval
   for deferrals/out-of-scope items, useful source references, relevant implementation surfaces, and
   verification expectations.
5. Ask for approval before material Slice fixes. If approval is not available, report the blocker rather than claiming planning readiness.
6. Return the compact handoff; do not perform planning. Any planning transition is handled by the
   parent Conceptualize skill via fresh Skill-tool/sub-agent invocation, never inline.

## Handoff Format

```markdown
Conceptualize Workspace: `.planning/<concept-slug>/index.md`
Key Slices:
- `slices/<name>.md` — <focus and notable H3 IDs>
Slice Coverage:
- full safe Slice inventory completed: yes/no
- revised for stale assumptions: yes/no/not needed
- unresolved blockers: <None or exact Slice/H3/question>
- implementation surfaces covered: <compact list or None identified>
- deferred/out-of-scope items: <compact list with approval provenance or None>
Planning Handoff:
- <highest-signal requirements, constraints, risks, non-goals, and H3 pointers when useful>
Open Questions:
- <only blockers or important uncertainties>
Next: ask to create an implementation plan for <deliverable> when ready.
```

## Fail Closed When

- No safe Slice exists for the workspace.
- A Slice path is unsafe or unreadable.
- The full safe Slice inventory was not read.
- Any planning-relevant question remains unresolved without explicit approved deferral.
- A material Slice commitment is stale, contradicted, narrowed, or excluded without approval.
- Later planning would need hidden conversation context to understand a requirement.
