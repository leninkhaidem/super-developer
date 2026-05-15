# Review-Code Design-Decision Filter

Load this reference only when a review mode permits fixes and a confirmed finding may require a user-facing product or architecture choice before delegation. It is shared by local and pipeline modes; PR mode remains review-only and has no code-fix path.

## Promotion Rule

When applying fixes under blanket or auto-resolve mode, promote a finding to a decision card only when all three conditions hold:

1. Severity is `[BLOCKER]` or `[CRITICAL]`.
2. The finding is Skeptic-confirmed and tied to the immutable reviewed state.
3. The reviewer surfaced two or more valid fix approaches with different runtime behavior, blast radius, or public surface area, and choosing among them is a product or architecture decision.

Findings that do not satisfy all three conditions are not decision cards. If the active mode permits fixing, unambiguous non-design fixes may be delegated silently after the active mode's state gate passes.

## Examples That Prompt

- "SQL injection — parameterize the query (status quo) OR migrate to ORM (3 callers affected, behavior preserved)"
- "Auth bypass — fix at middleware (centralized) OR per-route guard (explicit but verbose)"
- "Race condition — pessimistic lock (slower) OR optimistic retry (more code, faster happy path)"

## Examples That Do Not Prompt

- "SQL injection — switch to parameterized query" (only one approach)
- "Off-by-one — change `<` to `<=`" (only one approach)
- "Missing null check — add guard" (only one approach)
- Any test-only fix, regardless of approach count, since it does not change shipped runtime behavior

## Non-Bypass Rules

Blanket mode never bypasses the Code Reviewer's baseline security/privacy/safety sniff, the Skeptic requirement for serious findings, stale-state gates, delegated fix verification where a mode requires it, PR merge confirmation, or pipeline final-audit semantics.

Use `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/decision-prompts.md` for decision-card display mechanics after this filter decides a card is required.
