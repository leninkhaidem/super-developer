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
  package shape, parallel-safety claims) inside `implement`. These
  affect sub-agent scheduling, not what ships.
- Per-fix approval in `review-code` *pipeline blanket mode*. Code
  findings get fixed unless the fix involves a real design choice
  (defined below). Local-mode `fix` workflows preserve their existing
  per-fix `yes/skip` semantics when the user has not authorized
  blanket mode.
- Defining an explicit `abort` keyword. Stopping the prompt stream is
  natural — the user simply does not respond. Auto-applied edits made
  before the silence remain in tasks.json (they are durable on
  purpose); prompted edits do not partially apply.

## Locked Decisions

| # | Decision | Choice |
|---|---|---|
| 1 | Filter rule | Outcome-changing **OR** security/privacy/safety-tagged |
| 2 | Skill scope | `review-plan` + `review-code` only |
| 3 | Pipeline blanket mode | Threshold rule: auto-apply when reviewer verdict is unanimous AND finding is non-security AND single-reviewer mode is not in effect; prompt otherwise |
| 4 | Persistence | None |
| 5 | Abort handling | Not defined — implicit no-op if stream is interrupted |
| 6 | Input mechanism | Plain-text prompts in chat (no `AskUserQuestion`) |
| 7 | Architecture | Hybrid — shared mechanics in a reference; per-skill filter inline |
| 8 | Single-reviewer plan review | Always prompt for outcome-changing findings, even under blanket approval |
| 9 | Gate 2 under blanket approval | Always blocking, regardless of blanket mode |
| 10 | AC rewrites | Auto-apply only when the rewrite is purely cosmetic (whitespace, punctuation, grammar with no operator-meaning shift); otherwise prompt |
| 11 | `parallel_safe_with` edits | Auto-apply (sub-agent scheduling, not shipped outcome) |

## Architecture

A new shared reference defines pure UX mechanics. Each skill defines
inline what counts as outcome-changing for its own finding shape.

```
references/decision-prompts.md          ← prompt template, blanket
                                           threshold, summary format
                                           (mechanics only)

skills/review-plan/SKILL.md
   Step 7  → filter findings; prompt or auto-apply
   Step 9  → Gate 2 surfaces both bands; remains blocking under blanket

skills/review-code/SKILL.md
   `fix`   → promote finding to decision card only when fix involves
             a real design choice
```

## The Shared Reference: `references/decision-prompts.md`

Contains three things only.

### 1. Prompt Card Template

Single canonical layout. Both skills emit cards in this exact shape.
The box-drawing borders below are **illustrative** — implementers may
substitute simpler horizontal-rule formatting if the host environment
renders monospace poorly. The element order, content, and prompt-key
conventions are normative; the borders are not.

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

**Plain-language headline.** ≤80 characters. Derived from the
reviewer's `TITLE` line by stripping target-locator prefixes
(`TASK:P1-T003 — `, `WP:WP1.parallel_safe_with — `) and any acronyms
that already appear in `references/work-packages.md` glossary terms.
No further paraphrasing — the goal is recognizability for someone who
read the original finding, not translation for someone who didn't.

### 2. Letter-Prompt Convention

- Single-letter keys per option, drawn from letters not reserved.
- **Reserved keys: `B` and `D`.** Option keys may not use these.
- Recommendation always tagged `(recommended)`.
- Default Enter takes the recommended option.
- Every card with more than one decision remaining offers
  `[B] Apply my recommendation to all <N> remaining`. `[B]` skips
  any remaining findings tagged security, privacy, or safety —
  those continue to prompt individually even after `[B]` is used.
- Optional `[D] More details` per card when the reviewer's case has
  supporting context worth showing on demand.

### 3. Pipeline Blanket-Mode Threshold

When the user has authorized end-to-end automation
(`proceed through all stages` or equivalent), the orchestrator
auto-takes the recommendation when **all three** conditions hold:

- The reviewer's verdict on the recommendation is unanimous (no
  conflicting alternative path was raised by another reviewer)
- The finding is **not** tagged security, privacy, or safety
- The plan review is operating in escalated (multi-reviewer) mode —
  i.e., both the Plan Quality Reviewer and the Adversarial Plan
  Challenger ran and agree

Otherwise the orchestrator pauses the pipeline and presents the card.
Auto-taken decisions surface in the post-review summary as
`← auto (blanket-approved, low-risk)` so the user can spot any silent
choices when reading the summary.

**Single-reviewer plan review.** When `review-plan` runs with only the
Plan Quality Reviewer (no escalation), the threshold's third condition
is not satisfied, so blanket mode does **not** auto-apply
outcome-changing findings. Every outcome-changing finding prompts,
even under `proceed through all stages`. This keeps the user as the
tiebreaker whenever there is no second reviewer to provide consensus
signal.

**Gate 2 always blocks.** Regardless of blanket-mode authorization,
Step 9 (Post-Review Announcement / Gate 2) is a hard pause. The user
must explicitly approve Gate 2 before finalization. Bypassing Gate 2
would defeat the purpose of the auto-applied audit trail — the user
would only see silent decisions after implementation has run.

### Constructing the Recommendation

The orchestrator builds the recommended option for each card from the
reviewer's `FIX:` line, treated as the recommendation verbatim. When
the `FIX:` line names a single concrete action ("Add P1-T001 to
P1-T003.dependencies"), that becomes the recommended option as
written. The orchestrator does not paraphrase, summarize, or expand
the line.

When two reviewers file findings on the same target with different
`FIX:` lines, the orchestrator does not pick one. It generates a
prompt that lists both `FIX:` lines as alternatives, marks the
finding as a forced prompt regardless of severity tag, and lets the
user resolve.

When the reviewer's `FIX:` line is multi-clause (the reviewer proposed
more than one concrete action separated by "AND" or by enumeration),
each clause becomes a separate option on the card and the
recommendation is the first clause unless the reviewer explicitly
ordered them otherwise.

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
- Rewrite an acceptance criterion in any way other than purely
  cosmetic (whitespace, punctuation, grammar with no operator-meaning
  shift). Rewrites that introduce or remove a numeric bound, an HTTP
  status, an error code, a verification environment, or any other
  testable specific are outcome-changing
- Add or remove a phase
- Move a task between phases or packages such that order or dependency
  shifts
- Move a boundary between in-scope and out-of-scope items
- Change the verification scope, environment, or test surface required
  by an acceptance criterion (e.g., "unit tests pass" → "integration
  tests pass against staging DB")
- Realign a task's spec-traceability identifier when the realignment
  would leave the original SPEC requirement uncovered (no remaining
  task cites it)
- The finding is tagged security, privacy, or safety, regardless of
  the above

A finding is **auto-applied** (recommendation taken silently, surfaced
in Gate 2 summary) when its proposed fix:

- Rewrites or rephrases task description wording without changing the
  user-visible outcome
- Trims a description that exceeds the 600-character budget
- Removes anti-pattern content (code snippets, line numbers,
  step-by-step instructions in task descriptions)
- Performs a purely cosmetic acceptance-criterion rewrite (whitespace,
  punctuation, grammar; no testable specifics added or removed)
- Realigns spec ↔ task traceability identifiers when both source and
  target SPEC requirements remain covered by some task after the
  realignment
- Reshapes work packages while preserving task membership and external
  dependencies
- Adjusts `parallel_safe_with` claims (sub-agent scheduling, not
  shipped outcome)

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
- Any test-only fix, regardless of approach count, since it does not
  change shipped runtime behavior

When promoted, the card uses the shared template. When not promoted,
the fix is applied directly without user input.

The existing `local-workflow.md` and `pr-workflow.md` per-fix
`yes/skip` approval semantics are preserved when the user has **not**
authorized blanket mode. When blanket mode is authorized, the
decision-card filter above replaces per-fix approval — silent fixes
land directly, design-decision findings prompt.

## Gate 2 Summary Format (review-plan)

Step 9 keeps its existing `What Will Be Delivered` template and adds
two new sections.

```markdown
### Decisions made (<N>)
- <plain-language headline>  → <outcome>
- ...

### Auto-applied refinements (<N>)
- <plain-language description of the silent fix>
  - For acceptance-criterion rewrites: include the before → after text
    inline so the user can spot any locked-in implementation detail
- ...
```

If either section is empty, omit it.

**Re-review interaction.** If `review-plan` enters re-review (Step 8)
because of remaining blockers, the Gate 2 summary lists auto-applied
edits **cumulatively across all rounds**, not just the final round.
A blocker raised in round 2 may be caused by an edit auto-applied in
round 1; cumulative listing keeps that audit trail intact.

## Files Touched

- **New**: `plugins/super-developer/references/decision-prompts.md`
- **Modify**: `plugins/super-developer/skills/review-plan/SKILL.md`
  (Step 7, Step 9)
- **Modify**: `plugins/super-developer/skills/review-code/SKILL.md`
  (Pipeline `fix` action)

`references/local-workflow.md` and `references/pr-workflow.md` absorb
a single sentence pointing at the shared reference for the
design-decision branch under blanket mode. Their existing per-fix
`yes/skip` approval semantics are preserved when blanket mode is not
authorized.

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
every card. Security/privacy/safety findings continue to prompt
individually even after `[B]`.

**Recommendation drift.** The orchestrator uses the reviewer's `FIX:`
line verbatim as the recommendation. It does not paraphrase. Two
reviewers with different `FIX:` lines on the same target produce a
forced prompt with both alternatives shown — the user is the
tiebreaker.

**Auto-applied items hidden from view.** The Gate 2 summary always
lists auto-applied items in their own section, with before/after text
inline for acceptance-criterion rewrites. The user always sees what
was decided silently before approving the final plan.

**Pipeline mode subtly changes behavior.** When the user authorizes
unattended runs, the threshold rule may auto-take recommendations the
user would have inspected. Mitigations: (1) the threshold excludes
security, privacy, and safety findings; (2) the threshold excludes
single-reviewer mode entirely (no consensus signal → no auto-apply);
(3) Gate 2 always blocks regardless of blanket mode; (4) the Gate 2
summary marks auto-taken items with
`← auto (blanket-approved, low-risk)` for post-hoc review.

**Re-review surfaces blockers caused by previously-applied edits.**
The Gate 2 summary lists auto-applied edits cumulatively across all
re-review rounds. A blocker in round N may be caused by an edit
applied in round N-1; the cumulative listing makes this discoverable.

## Out of Scope for This Design

- A separate UX layer in `implement` for runtime adjustments.
- Persistent decision logs.
- Translation of reviewer findings into plain-English prose.
- A configuration surface for users to tune the threshold rule.
- A `/resume-review` command for partial-state continuation.
