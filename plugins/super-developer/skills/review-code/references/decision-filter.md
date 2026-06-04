# Review-Code User-Decision Filter

Load only when local or pipeline mode permits fixes and a confirmed finding may require a user-facing product or architecture choice before delegation. PR mode is review-only and has no code-fix path.

## Promotion Rule

Promote a finding to a user-decision card only when all are true:

1. Severity is 🔴 BLOCKER or 🟠 CRITICAL.
2. The finding is Skeptic-confirmed and tied to the immutable reviewed state.
3. The reviewer surfaced two or more valid fix approaches with materially different runtime behavior, blast radius, or public surface.
4. Choosing among those approaches is a product or architecture authority decision, not an implementation detail.

Findings that do not satisfy every condition are not decision cards. If the active mode permits fixing, unambiguous non-design fixes may be delegated silently after the active mode's state gate passes.

## Prompt Examples

- Parameterize query at the current seam or migrate the data access layer.
- Enforce authorization centrally in middleware or explicitly per route.
- Use pessimistic locking or optimistic retry for a race condition.

## Non-Prompt Examples

- Off-by-one change with one safe correction.
- Missing null guard with one obvious guard point.
- Test-only fix, regardless of approach count.
- Evidence refresh or report rerun with no product/runtime choice.

## Non-Bypass Rules

Blanket mode never bypasses baseline security/privacy/safety sniff, Skeptic verification, stale-state gates, delegated fix verification where a mode requires it, PR merge confirmation, proof/report freshness, or final audit semantics.

Use `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/decision-prompts.md` for decision-card display mechanics after this filter decides a card is required.
