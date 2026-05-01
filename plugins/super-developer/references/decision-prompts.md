# Decision Prompts — Shared Mechanics

Pure UX mechanics consumed by `review-plan` and `review-code`. Each skill defines its own outcome filter, blanket-mode eligibility, and side-effect gates inline; this reference defines only how prompts are presented and how the orchestrator constructs the recommended option for each card. The four sections below are independent: the card template, the letter-prompt convention, skill-owned blanket-mode policy, and the recommendation-construction algorithm.

## 1. Prompt Card Template

Single canonical layout. Both skills emit cards in this exact shape. The box-drawing borders below are **illustrative only** — implementers may substitute simpler horizontal-rule formatting if the host environment renders monospace poorly. The element order, the content of each field, and the letter-key conventions are required; the borders are not.

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

The `Progress: ●○○○` indicator visualises the `<X> of <Y>` counter from the header line. Filled circles mark decisions already resolved; hollow circles mark remaining decisions. Implementers may substitute any equivalent left-to-right progress glyph if circles render poorly.

### Plain-language headline

≤80 characters. Derived from the reviewer's `TITLE` line by stripping target-locator prefixes (`TASK:P1-T003 — `, `WP:WP1.parallel_safe_with — `). No further paraphrasing — the goal is recognizability for someone who read the original finding, not translation for someone who didn't.

### Card field source mapping

Every card field maps to a specific reviewer-output element. The orchestrator does not synthesize prose from scratch.

| Card field | Source |
|---|---|
| `<plain-language headline>` | Reviewer's `TITLE` line, prefix-stripped |
| `Outcome impact:` | One sentence naming the filter category that promoted the finding (e.g., "Adds a task" / "Removes an acceptance criterion" / "Tagged security") |
| `<Reviewer's case>` | Reviewer's `ISSUE:` line verbatim, optionally truncated to 3 lines with an ellipsis if longer |
| `What ships either way:` | Bullets enumerating items the reviewer's `FIX:` line does not touch (only present when the reviewer's `COST:` line explicitly enumerates preserved items) |
| `[<key>] <option>` | Reviewer's `FIX:` line, verbatim (see Constructing the Recommendation) |
| `<pro/con>` | Reviewer's `COST:` line, one bullet per cost item; omitted when `COST:` is absent |

## 2. Letter-Prompt Convention

- Single-letter keys per option, drawn from letters not reserved.
- **Reserved keys: `B` and `D`.** Option keys may not use these.
- Recommendation always tagged `(recommended)`.
- Default Enter takes the recommended option.
- Every card with more than one decision remaining offers `[B] Apply my recommendation to all <N> remaining`. `[B]` applies only to the remaining cards that the invoking skill has already deemed eligible for blanket handling; findings tagged security, privacy, or safety continue to prompt individually unless that skill explicitly defines a stricter rule. Review-code eligibility is owned by `skills/review-code/SKILL.md` (`Design-Decision Filter`) and mode-specific workflow references.
- Optional `[D] More details` per card when the reviewer's case has supporting context worth showing on demand.

## 3. Skill-Owned Blanket-Mode Policy

This shared reference does not decide which findings qualify for blanket mode. Each invoking skill owns its outcome filters, side-effect gates, and safety exceptions; this file only defines how an eligible decision card is displayed once the skill has chosen to present or auto-apply it.

For `review-plan`, preserve the existing pipeline threshold: when the user has authorized end-to-end automation (`proceed through all stages` or equivalent), the orchestrator auto-takes the recommendation only when **all** conditions hold:

- The plan review is operating in escalated multi-reviewer mode, meaning both the Plan Reviewer and the Security/Failure-Mode Reviewer participated.
- Those reviewers agree on the recommended path (no conflicting alternative path was raised by another reviewer).
- The finding is **not** tagged security, privacy, or safety.

Otherwise the orchestrator pauses the pipeline and presents the card. Auto-taken decisions surface in the post-review summary as `← auto (blanket-approved, low-risk)` so the user can spot any silent choices when reading the summary.

### Single-reviewer plan review

When `review-plan` runs with only the Plan Reviewer (no security escalation), the threshold's first condition is not satisfied, so blanket mode does **not** auto-apply outcome-changing findings. Every outcome-changing finding prompts, even under `proceed through all stages`. This keeps the user as the tiebreaker whenever there is no second reviewer to provide consensus signal.

### Gate 2 always blocks

Regardless of blanket-mode authorization, `review-plan` Step 9 (Post-Review Announcement / Gate 2) is a hard pause. The user must explicitly approve Gate 2 before finalization. Bypassing Gate 2 would defeat the purpose of the auto-applied audit trail — the user would only see silent decisions after implementation has run.

## 4. Constructing the Recommendation

The orchestrator builds the recommended option for each card from the reviewer's `FIX:` line, treated as the recommendation verbatim. When the `FIX:` line names a single concrete action ("Add P1-T001 to P1-T003.dependencies"), that becomes the recommended option as written. The orchestrator does not paraphrase, summarize, or expand the line.

When two reviewers file findings on the same target with different `FIX:` lines, the orchestrator does not pick one. It generates a prompt that lists both `FIX:` lines as alternatives, marks the finding as a forced prompt regardless of severity tag, and lets the user resolve.

When the reviewer's `FIX:` line contains multiple clauses, the orchestrator distinguishes conjunction from disjunction:

- **Conjunction** (clauses joined by `AND`, `and`, `+`, or enumerated as a sequence the reviewer expects to apply together): treat as a single recommended option whose text is the entire multi-clause line verbatim. Both/all actions apply when the option is selected.
- **Disjunction** (clauses joined by `OR`, `or alternatively`, or presented as numbered/lettered alternatives): split into separate options on the card. The first listed alternative is the default recommendation unless the reviewer explicitly ordered them otherwise.

When the connector is ambiguous (e.g., a comma-separated list with no explicit `AND` / `OR`), default to conjunction — the safer choice, since splitting a conjunction loses required actions while combining a disjunction merely costs the user one extra prompt-key.
