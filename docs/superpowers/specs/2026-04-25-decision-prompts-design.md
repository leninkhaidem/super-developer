# Decision Prompts — Design

A user-input UX layer for the `review-plan` and `review-code` skills.
Prompts the user only at moments where the answer changes what ships
or where the finding is security/privacy/safety-tagged. Everything else
is auto-applied at the reviewer's recommendation and surfaced in a
post-review summary.

## Goal

Today, after plan review or code review, the user is shown a wall of
findings with similar shape and asked for one freeform decision
covering all of them. This causes overwhelm and rubber-stamping. This
design replaces the wall with one decision card at a time, only for
findings that genuinely need user input. Auto-applied findings remain
visible in the post-review summary so the user retains audit trust
without paying friction for every wording fix.

## Non-Goals

- Translating finding text into "plain English" prose. Findings keep
  the format the reviewer wrote.
- Persistence of decisions. Re-runs re-prompt; spec/tasks.json hold the
  final state once shipped.
- Prompting for runtime orchestration choices (serial vs parallel,
  package shape) inside `implement`. Same code ships either way.
- Per-fix approval in `review-code`. Code findings get fixed unless
  the fix involves a real design choice (defined below).
- Defining an explicit `abort` keyword. Stopping the prompt stream is
  natural — user simply does not respond, no state to clean up.

## Locked Decisions

| # | Decision | Choice |
|---|---|---|
| 1 | Filter rule | Outcome-changing **OR** security/privacy/safety-tagged |
| 2 | Skill scope | `review-plan` + `review-code` only |
| 3 | Pipeline blanket mode | Threshold rule: auto when reviewer verdict is unanimous AND finding is non-security; prompt otherwise |
| 4 | Persistence | None |
| 5 | Abort handling | Not defined — implicit no-op if stream is interrupted |
| 6 | Input mechanism | Plain-text prompts in chat (no `AskUserQuestion`) |
| 7 | Architecture | Hybrid — shared mechanics in a reference; per-skill filter inline |

## Architecture

A new shared reference defines pure UX mechanics. Each skill defines
inline what counts as outcome-changing for its own finding shape.

```
references/decision-prompts.md          ← prompt template, blanket
                                           threshold, summary format
                                           (mechanics only)

skills/review-plan/SKILL.md
   Step 7  → filter findings; prompt or auto-apply
   Step 9  → Gate 2 surfaces both bands

skills/review-code/SKILL.md
   `fix`   → promote finding to decision card only when fix involves
             a real design choice
```

## The Shared Reference: `references/decision-prompts.md`

Contains three things only.

### 1. Prompt Card Template

Single canonical layout. Both skills emit cards in this exact shape.

```
─────────────────────────────────────────────────────────────────
  <Skill> — Decisions Required (<X> of <Y>)
  Feature: <feature-name>            Progress: ●○○○
─────────────────────────────────────────────────────────────────
  Decision <N> — <plain-language headline>
─────────────────────────────────────────────────────────────────

  Outcome impact: <what changes in what ships>

  <Reviewer's case in 1-3 lines>

  What ships either way (when relevant):
    <bullets of unchanged things>

  What changes:
    [<key>] <option>  (recommended)
            <pro/con if non-obvious>
    [<key>] <option>
            <pro/con>

  Your call ▸ _
```

### 2. Letter-Prompt Convention

- Single-letter keys per option.
- Recommendation always tagged `(recommended)`.
- Default Enter takes the recommended option.
- Every card with more than one decision remaining offers
  `[B] Apply my recommendation to all <N> remaining`.
- Optional `[D] More details` per card when reviewer's case has
  supporting context worth showing on demand.

### 3. Pipeline Blanket-Mode Threshold

When the user has authorized end-to-end automation
(`proceed through all stages` or equivalent), the orchestrator
auto-takes the recommendation when **both** conditions hold:

- The reviewer's verdict on the recommendation is unanimous (no
  conflicting alternative path was raised by another reviewer)
- The finding is **not** tagged security, privacy, or safety

Otherwise the orchestrator pauses the pipeline and presents the card.
Auto-taken decisions surface in the post-review summary as
`← auto (blanket-approved, low-risk)` so the user can spot any silent
choices when reading the summary.

**Single-reviewer mode.** When `review-plan` runs with only the Plan
Quality Reviewer (no escalation), the unanimous condition is trivially
satisfied — there is no second reviewer to disagree. In that mode the
security/privacy/safety filter is the only operative guard, and
blanket mode auto-takes the recommendation for every non-security
outcome-changing finding. This is intentional: the user opted into
automation, the plan was below the escalation thresholds, and the
recommended path is the reviewer's only stated preference.

## Per-Skill Filter Rules

Each skill defines, inline within its existing finding-handling step,
which findings are outcome-changing and require a prompt versus which
are auto-applied at the reviewer's recommendation.

### `review-plan` filter

Added to Step 7 (Merge and Resolve).

A finding **requires a prompt** if its proposed fix would, when
accepted, do any of:

- Add or remove a task
- Add or remove a work package
- Add or remove an acceptance criterion that describes user-visible
  behavior
- Add or remove a phase
- Move a task between phases or packages such that order or dependency
  shifts
- Move a boundary between in-scope and out-of-scope items
- The finding is tagged security, privacy, or safety, regardless of
  the above

A finding is **auto-applied** (recommendation taken silently, surfaced
in Gate 2 summary) when its proposed fix:

- Rewrites or rephrases existing wording without changing the
  user-visible outcome
- Trims a description that exceeds the 600-character budget
- Removes anti-pattern content (code snippets, line numbers,
  step-by-step instructions in task descriptions)
- Rephrases an acceptance criterion while preserving the same
  observable outcome
- Aligns spec ↔ task traceability identifiers
- Reshapes work packages while preserving task membership and
  dependencies
- Adjusts `parallel_safe_with` claims

### `review-code` filter

Added to the Pipeline `fix` gated action and to the matching Phase 5
sections of `references/local-workflow.md` and `references/pr-workflow.md`.

A finding is **promoted to a decision card** only when **all three**
conditions hold:

1. Severity is `[BLOCKER]` or `[CRITICAL]`
2. The reviewer surfaced two or more valid fix approaches with
   different runtime behavior, blast radius, or public surface area
3. Picking among the approaches is a product or architecture decision
   rather than a code-quality decision

Examples that prompt:

- "SQL injection — parameterize the query (status quo) OR migrate to
  ORM (3 callers affected, behavior preserved)"
- "Auth bypass — fix at middleware (centralized) OR per-route guard
  (explicit but verbose)"
- "Race condition — pessimistic lock (slower) OR optimistic retry
  (more code, faster happy path)"

Examples that do **not** prompt (fixed silently with the only sensible
fix):

- "SQL injection — switch to parameterized query" (only one approach)
- "Off-by-one — change `<` to `<=`" (only one approach)
- "Missing null check — add guard" (only one approach)

When promoted, the card uses the shared template. When not promoted,
the fix is applied directly without user input, consistent with
existing `fix` semantics.

## Gate 2 Summary Format (review-plan)

Step 9 keeps its existing `What Will Be Delivered` template and adds
two new sections.

```markdown
### Decisions made (<N>)
- <plain-language headline>  → <outcome>
- ...

### Auto-applied refinements (<N>)
- <plain-language description of the silent fix>
- ...
```

If either section is empty, omit it.

## Files Touched

- **New**: `plugins/super-developer/references/decision-prompts.md`
- **Modify**: `plugins/super-developer/skills/review-plan/SKILL.md`
  (Step 7, Step 9)
- **Modify**: `plugins/super-developer/skills/review-code/SKILL.md`
  (Pipeline `fix` action)

`references/local-workflow.md` and `references/pr-workflow.md` may
absorb a single sentence pointing at the shared reference for the
design-decision branch; their existing per-fix approval semantics are
otherwise preserved.

## What This Design Does Not Change

- Reviewer agents' output formats (the structured `[SEV] TARGET — TITLE
  / ISSUE / FIX / COST` and `[SEV] FILE:LINE / WHY / FIX` blocks remain
  exactly as today). The orchestrator parses them; only the prompts
  around them change.
- Step numbering of either skill.
- Severity taxonomy or resolution rules.
- The Skeptic Agent's CONFIRMED / DISPUTED / DOWNGRADED verdict logic.

## Risks and Mitigations

**User fatigue from too many prompts.** The filter is deliberately
narrow — outcome-changing only — to keep prompt count low. The
`[B] Apply recommendation to all remaining` escape hatch exists on
every card.

**Recommendation drift.** The orchestrator constructs the
recommendation by reading the reviewer's `FIX:` and `COST:` lines.
When two reviewers disagree on the recommended path, the threshold
rule forces a prompt regardless of finding type — the user becomes the
tiebreaker.

**Auto-applied items hidden from view.** The Gate 2 summary always
lists auto-applied items in their own section. The user always sees
what was decided silently before approving the final plan.

**Pipeline mode subtly changes behavior.** When the user authorizes
unattended runs, the threshold rule may auto-take recommendations the
user would have inspected. Mitigation: the threshold excludes
security, privacy, and safety findings, and the Gate 2 summary marks
auto-taken items with `← auto (blanket-approved, low-risk)` for
post-hoc review.

## Out of Scope for This Design

- A separate UX layer in `implement` for runtime adjustments.
- Persistent decision logs.
- Translation of reviewer findings into plain-English prose.
- A configuration surface for users to tune the threshold rule.
- A `/resume-review` command for partial-state continuation.
