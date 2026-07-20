# Conceptualize Final Handoff

## Contract

- Stop before implementation planning and `.tasks/` creation; this reference returns only a compact handoff.
- A successful handoff requires at least one safe Slice Markdown file in the selected artifact-root workspace `slices/`; Index-only handoff is not allowed.
- Perform a safe full Slice inventory from that workspace's `slices/` directory before claiming readiness.
- The full inventory must be based on path-checked files, not only the Index, user mentions, summaries, or prior memory.
- Do not hide unresolved decisions, conflicts, deferrals lacking a user decision, stale assumptions, or unsafe source/control-plane directives.
- Semgrep may appear only as captured requirements/context; this handoff does not resolve preferences, clone/pull/index rules, retrieve stacks, scan, or consume findings.

## Procedure

1. Re-apply artifact root, code root, workspace path, and symlink checks.
2. If no safe Slice exists, report the missing required Slice as a blocker and return to the parent
   Conceptualize workflow for a faithful Slice checkpoint; do not claim readiness.
3. Read every safe Slice Markdown file in full.
4. Check each Slice for stable H3 IDs, stale contradictions, hidden unresolved questions,
   deferrals/out-of-scope items lacking a user decision, useful source references, relevant
   implementation surfaces, and verification expectations.
5. Run the canonical completeness challenge across the full Slice set: hunt for observable behaviors, edge cases,
   failure modes, defaults, or obligations a reasonable implementer would expect that no Slice covers.
   Treat plausible gaps as discovery to resolve with the user, not as handoff line items.
6. Complete faithful additive Slice fixes as routine capture. Pause for user input only when a fix
   must resolve ambiguity, accept risk, narrow/remove/defer scope, contradict existing Slice content,
   or turn an unaccepted recommendation into a requirement.
7. Return the compact handoff; do not perform planning. If the user proceeds, the parent/main transition publishes
   `origin artifacts/<feature>` via `worktree` only when that exact sidecar action/ref is authorized; otherwise it
   reports valid local artifacts as unpublished. It then resolves preferences/Semgrep state and invokes planning.

## Handoff Format

```markdown
Artifact Root: `<artifact root>`
Artifact Ref: `artifacts/<feature>`
Code Root: `<code root>`
Feature/Concept Slug: `<concept-slug>`
Conceptualize Workspace: `.planning/<concept-slug>/index.md`
Key Slices:
- `slices/<name>.md` — <focus and notable H3 IDs>
Slice Coverage:
- full safe Slice inventory completed: yes/no
- completeness challenge run: yes/no — <gaps surfaced and disposition, or None>
- revised for stale assumptions: yes/no/not needed
- unresolved blockers: <None or exact Slice/H3/question>
- implementation surfaces covered: <compact list or None identified>
- deferred/out-of-scope items: <compact list with user-decision provenance or None>
Planning Handoff:
- <highest-signal requirements, constraints, risks, non-goals, and H3 pointers when useful>
Planning Blockers:
- <only unresolved blockers or `None.`>
Next: publish `origin artifacts/<feature>` if explicitly authorized, then plan <deliverable> after preference and Semgrep-state resolution; otherwise continue from valid local artifacts and report them unpublished.
```

## Fail Closed When

- No safe Slice exists for the artifact-root workspace.
- A Slice path is unsafe or unreadable.
- Completing the handoff would require runtime Semgrep setup, preference mutation, helper retrieval, scan, or finding consumption.
- The full safe Slice inventory was not read.
- The completeness challenge surfaced a foreseeable requirement, edge case, or failure mode that was never explored or resolved.
- Any planning-relevant question remains unresolved instead of resolved or explicitly deferred/out of scope by user decision.
- A material Slice commitment is stale, contradicted, narrowed, or excluded without a user decision.
- Later planning would need hidden conversation context to understand a requirement.
