# Conceptualize Final Handoff

Load when the user says the concept is ready for planning or asks for a final handoff.

## Contract

- Stop before implementation planning and `.tasks/` creation.
- Index-only handoff is allowed when no Slice is independently useful; say that explicitly.
- If any Slice exists, perform a safe full Slice inventory from the selected workspace's `slices/` directory before claiming readiness.
- The full inventory must be based on path-checked files, not only the Index, user mentions, summaries, or prior memory.
- Do not hide unresolved decisions, conflicts, unapproved deferrals, stale assumptions, or unsafe source/control-plane directives.

## Procedure

1. Re-apply workspace path and symlink checks.
2. If no Slice exists, verify the Index contains enough durable handoff context and state `Key Slices: None; Index-only handoff.`
3. If Slices exist, read every safe Slice Markdown file in full.
4. Check each Slice for stable H3 IDs, stale contradictions, unresolved questions, missing approval for deferrals/out-of-scope items, useful source references, relevant implementation surfaces, and verification expectations.
5. Ask for approval before material Slice fixes. If approval is not available, report the blocker rather than claiming planning readiness.
6. Return the compact handoff; do not invoke `implementation-plan` inline.

## Handoff Format

```markdown
Conceptualize Workspace: `.planning/<concept-slug>/index.md`
Key Slices:
- `slices/<name>.md` — <focus and notable H3 IDs>
- None; Index-only handoff. <why no Slice is independently useful>
Slice Coverage:
- full safe Slice inventory completed: yes/no/not applicable
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

- A Slice path is unsafe or unreadable.
- Slices exist but the full safe inventory was not read.
- Any planning-relevant question remains unresolved without explicit approved deferral.
- A material Slice commitment is stale, contradicted, narrowed, or excluded without approval.
- Later planning would need hidden conversation context to understand a requirement.
