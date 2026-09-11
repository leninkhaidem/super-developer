# Conceptualize Final Handoff

## Contract

- This reference returns only a compact Conceptualize handoff. It does not create `.tasks/`, plan work, run
  Semgrep, mutate preferences, publish sidecars, or clean worktrees.
- A handoff may be chat-only, Index-only, or Slice-backed. Choose the smallest form that lets the next agent or
  user proceed without hidden conversation context.
- Chat-only is valid for simple settled work or when no durable record is useful. Include the full approved concise
  context in the response.
- Index-only is valid when durability is useful but no Slice is independently useful. The Index must contain enough
  approved context for the next step.
- Slice-backed handoff is required only when focused Slices are independently useful or already exist.
- If any safe Slice exists in the selected workspace, perform a full safe Slice inventory before claiming coverage.
- Do not hide unresolved decisions, conflicts, unapproved deferrals, stale assumptions, unsafe paths, or raw
  control-plane/source directives.
- Semgrep may appear only as captured requirements/context; this handoff does not resolve preferences, retrieve
  rule stacks, scan, or consume findings.

## Procedure

1. Decide whether any durable workspace exists or is needed under the parent Durability Gate.
2. For chat-only handoff, use the compact guidance below. State once that no files were needed; do not replace
   file ceremony with a mandatory report-shaped chat response. Complete the applicable checks before returning.
3. For Index-only handoff, re-apply artifact-root, code-root, workspace, and symlink checks; read the Index; verify
   it contains complete approved concise context and explains why no Slice is independently useful.
4. For Slice-backed handoff, re-apply path and symlink checks, then read every safe Slice Markdown file in the
   selected workspace's `slices/` directory in full. Do not rely only on the Index, user mentions, summaries,
   copied excerpts, or prior memory.
5. Check durable records for stable H3 IDs when Slices exist, stale contradictions, unresolved questions, useful
   source references, implementation surfaces, approved deferrals/out-of-scope items, and verification expectations.
6. Check the selected handoff for missing accepted outcomes, applicable edge cases, and concrete failure risks.
   Scale the completeness challenge to the work; do not invent speculative obligations for a simple change.
   Resolve material gaps with the user before claiming planning readiness. Keep routine check mechanics internal.
7. Complete faithful additive Index/Slice fixes as routine capture only when the Durability Gate still applies.
   Pause for user input when a fix must resolve ambiguity, accept risk, narrow/remove/defer scope, contradict
   existing durable content, or turn an unaccepted recommendation into a requirement.
8. Return the compact handoff. If the user proceeds to planning, the parent/main transition resolves preferences
   and Semgrep state and publishes an artifact sidecar only when that exact action/ref is authorized. If no sidecar
   exists or publication is unauthorized, report valid local context/artifacts as unpublished.

## Chat-Only Handoff

Use a short plain-language summary of the agreed outcome, important constraints or unresolved decisions, and next
step. Include evidence references and verification expectations only when material. Omit empty fields, internal
completeness rows, and artifact metadata for nonexistent files. A fresh recipient must still receive every
implementation-shaping commitment; brevity never means relying on hidden chat.

## Durable Handoff Format

```markdown
Artifact Root: `<artifact root or None>`
Artifact Ref: `<artifacts/<feature> or None>`
Code Root: `<code root>`
Feature/Concept Slug: `<concept-slug or None>`
Conceptualize Workspace: `<.planning/<concept-slug>/index.md or None>`
Durable Mode: `Index-only` | `Slice-backed`
Key Slices:
- `None — no Slice independently useful.`
- `slices/<name>.md` — <focus and notable H3 IDs>
Slice Coverage:
- full safe Slice inventory completed: yes/no/not applicable
- completeness challenge run: yes/no — <gaps surfaced and disposition, or None>
- revised for stale assumptions: yes/no/not needed
- unresolved blockers: <None or exact Index/Slice/H3/question>
- implementation surfaces covered: <compact list or None identified>
- deferred/out-of-scope items: <compact list with user-decision provenance or None>
Planning Handoff:
- <highest-signal approved requirements, constraints, risks, non-goals, tradeoffs, and pointers>
Planning Blockers:
- <only unresolved blockers or `None.`>
Next:
- <plan from this context, continue discovery, direct route, or publish sidecar only if explicitly authorized>
```

## Fail Closed When

- A requested durable handoff has no safe, readable Index.
- Slices exist but the full safe Slice inventory was not read.
- An Index-only handoff would force later agents to reconstruct hidden conversation context.
- A Slice path is unsafe or unreadable.
- Completing the handoff would require Semgrep setup, preference mutation, helper retrieval, scan, or finding
  consumption.
- A planning/direct-execution readiness claim leaves a material requirement, edge case, failure risk, or
  planning-relevant question unresolved instead of resolved or explicitly deferred/out of scope by user decision.
  Documentation or continued-discovery handoffs may carry clearly labeled open questions; those are valid notes,
  not readiness claims. State which next actions remain blocked.
- A material durable commitment is stale, contradicted, narrowed, deferred, or excluded without a user decision.
