# Decision Prompts Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace bulk reviewer-finding decision walls in `review-plan` and `review-code` with one decision card at a time, only for findings that change what ships or are tagged security/privacy/safety. Auto-applied refinements remain visible in the post-review summary.

**Architecture:** Add a shared `references/decision-prompts.md` defining prompt mechanics (card template, letter conventions, blanket-mode threshold, recommendation construction, card-field source mapping). Each consuming skill keeps its own outcome-changing filter inline within its existing finding-handling step. Plan review's Gate 2 (Step 9) gains two new sections — `Decisions made` and `Auto-applied refinements` — and remains a hard pause regardless of blanket-mode. Step 8 gains a per-round accumulator. Code review's pipeline `fix` action gates a finding to a decision card only when the fix is a real design choice (≥2 valid approaches with different runtime behavior); local-mode `yes/skip` semantics preserved when blanket mode is not authorized.

**Tech Stack:** Markdown-based Claude/Pi skill files, shell verification with `rg` and `git diff`, git worktree isolation.

---

## Design Source

This plan implements `docs/superpowers/specs/2026-04-25-decision-prompts-design.md`. Read that spec before starting any task — it defines the locked decisions, the per-skill filters, and the card mechanics this plan operationalizes. The spec's Locked Decisions table (LD 1–11) is the source of truth when a step here is ambiguous.

---

## File Map

- **Create**: `plugins/super-developer/references/decision-prompts.md`
  - Shared UX mechanics: card template, letter convention, blanket-mode threshold, recommendation construction, card-field source mapping.
- **Modify**: `plugins/super-developer/skills/review-plan/SKILL.md`
  - Step 7 (Merge and Resolve) — add outcome filter + decision-card flow.
  - Step 8 (Re-Review) — note per-round accumulator state for auto-applied edits.
  - Step 9 (Gate 2) — add `Decisions made` and `Auto-applied refinements` sections; mark as always-blocking.
- **Modify**: `plugins/super-developer/skills/review-code/SKILL.md`
  - Pipeline `fix` action — promote design-decision findings to decision cards under blanket mode; preserve per-fix `yes/skip` outside blanket mode.
- **Modify**: `plugins/super-developer/skills/review-code/references/local-workflow.md`
  - One-sentence pointer to `decision-prompts.md` for the design-decision branch under blanket mode.
- **Modify**: `plugins/super-developer/skills/review-code/references/pr-workflow.md`
  - Same one-sentence pointer.

5 files total: 1 new, 4 modified.

No changes are required to `implement`, `tasks`, or any other skill — this design's scope is `review-plan` + `review-code`.

---

### Task 1: Add the shared decision-prompts reference

**Files:**
- Create: `plugins/super-developer/references/decision-prompts.md`

- [ ] **Step 1: Create the reference file**

Write `plugins/super-developer/references/decision-prompts.md` with the exact body below. Strip the outer triple-backtick fence when saving.

```markdown
# Decision Prompts — Shared Mechanics

Pure UX mechanics consumed by `review-plan` and `review-code`. Each skill defines its own outcome filter inline; this reference defines only how prompts are presented and how blanket mode interacts with them.

## 1. Prompt Card Template

Single canonical layout. Both skills emit cards in this exact shape. The box-drawing borders below are **illustrative** — implementers may substitute simpler horizontal-rule formatting if the host environment renders monospace poorly. The element order, content, and prompt-key conventions are normative; the borders are not.

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
- Every card with more than one decision remaining offers `[B] Apply my recommendation to all <N> remaining`. `[B]` skips any remaining findings tagged security, privacy, or safety — those continue to prompt individually even after `[B]` is used.
- Optional `[D] More details` per card when the reviewer's case has supporting context worth showing on demand.

## 3. Pipeline Blanket-Mode Threshold

When the user has authorized end-to-end automation (`proceed through all stages` or equivalent), the orchestrator auto-takes the recommendation when **all** conditions hold:

- The plan review is operating in escalated (multi-reviewer) mode — i.e., both the Plan Quality Reviewer and the Adversarial Plan Challenger ran.
- Those reviewers agree on the recommended path (no conflicting alternative path was raised by another reviewer).
- The finding is **not** tagged security, privacy, or safety.

Otherwise the orchestrator pauses the pipeline and presents the card. Auto-taken decisions surface in the post-review summary as `← auto (blanket-approved, low-risk)` so the user can spot any silent choices when reading the summary.

### Single-reviewer plan review

When `review-plan` runs with only the Plan Quality Reviewer (no escalation), the threshold's first condition is not satisfied, so blanket mode does **not** auto-apply outcome-changing findings. Every outcome-changing finding prompts, even under `proceed through all stages`. This keeps the user as the tiebreaker whenever there is no second reviewer to provide consensus signal.

### Gate 2 always blocks

Regardless of blanket-mode authorization, `review-plan` Step 9 (Post-Review Announcement / Gate 2) is a hard pause. The user must explicitly approve Gate 2 before finalization. Bypassing Gate 2 would defeat the purpose of the auto-applied audit trail — the user would only see silent decisions after implementation has run.

## 4. Constructing the Recommendation

The orchestrator builds the recommended option for each card from the reviewer's `FIX:` line, treated as the recommendation verbatim. When the `FIX:` line names a single concrete action ("Add P1-T001 to P1-T003.dependencies"), that becomes the recommended option as written. The orchestrator does not paraphrase, summarize, or expand the line.

When two reviewers file findings on the same target with different `FIX:` lines, the orchestrator does not pick one. It generates a prompt that lists both `FIX:` lines as alternatives, marks the finding as a forced prompt regardless of severity tag, and lets the user resolve.

When the reviewer's `FIX:` line contains multiple clauses, the orchestrator distinguishes conjunction from disjunction:

- **Conjunction** (clauses joined by `AND`, `and`, `+`, or enumerated as a sequence the reviewer expects to apply together): treat as a single recommended option whose text is the entire multi-clause line verbatim. Both/all actions apply when the option is selected.
- **Disjunction** (clauses joined by `OR`, `or alternatively`, or presented as numbered/lettered alternatives): split into separate options on the card. The first listed alternative is the default recommendation unless the reviewer explicitly ordered them otherwise.

When the connector is ambiguous (e.g., a comma-separated list with no explicit `AND` / `OR`), default to conjunction — the safer choice, since splitting a conjunction loses required actions while combining a disjunction merely costs the user one extra prompt-key.
```

- [ ] **Step 2: Verify the reference exists and contains the core sections**

Run:

```bash
rg -n "^## 1\. Prompt Card Template|^## 2\. Letter-Prompt Convention|^## 3\. Pipeline Blanket-Mode Threshold|^## 4\. Constructing the Recommendation" plugins/super-developer/references/decision-prompts.md
```

Expected: four matching headings.

- [ ] **Step 3: Verify reserved keys, single-reviewer rule, and gate-2 rule are present**

Run:

```bash
rg -n "Reserved keys: \`B\` and \`D\`|Single-reviewer plan review|Gate 2 always blocks|conjunction|disjunction" plugins/super-developer/references/decision-prompts.md
```

Expected: at least 5 matching lines.

- [ ] **Step 4: Commit Task 1**

```bash
git add plugins/super-developer/references/decision-prompts.md
git commit -m "$(cat <<'EOF'
docs: add decision-prompts shared reference

Defines the prompt card template, letter-prompt conventions, blanket-
mode threshold rule (escalated + agree + non-security), single-reviewer
override, gate-2 always-blocks rule, recommendation construction
(verbatim FIX, AND vs OR clauses), and card field source mapping.
Consumed by review-plan and review-code.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 2: Add the outcome filter and decision-card flow to `review-plan` Step 7

**Files:**
- Modify: `plugins/super-developer/skills/review-plan/SKILL.md`

The current Step 7 ("Merge and Resolve") collects findings from spawned reviewers and applies severity resolution rules in three flat bullets (BLOCKER / CRITICAL / SUGGESTION). After this task, Step 7 also classifies findings as outcome-changing vs auto-applied per the spec's `review-plan` filter, and presents outcome-changing findings using the shared decision-prompts mechanics.

- [ ] **Step 1: Insert the outcome filter subsection**

In `plugins/super-developer/skills/review-plan/SKILL.md`, locate the heading `## Step 7: Merge and Resolve`. Insert this new subsection **immediately after** the heading and **before** the existing `Collect structured findings` paragraph:

```markdown
### Outcome Filter

Before resolving severity, classify each finding's proposed fix:

A finding **requires a user-facing decision card** if its `FIX:` would, when accepted, do any of:

- Add or remove a task
- Add or remove a work package
- Add or remove an acceptance criterion that describes user-visible behavior
- Rewrite an acceptance criterion in any way other than purely cosmetic (whitespace, punctuation, grammar with no operator-meaning shift). Rewrites that introduce or remove a numeric bound, an HTTP status, an error code, a verification environment, or any other testable specific are outcome-changing.
- Add or remove a phase
- Move a task between phases or packages such that order or dependency shifts
- Move a boundary between in-scope and out-of-scope items
- Change the verification scope, environment, or test surface required by an acceptance criterion (e.g., "unit tests pass" → "integration tests pass against staging DB")
- Realign a task's spec-traceability identifier when the realignment would leave the original SPEC requirement uncovered (no remaining task cites it)
- The finding is tagged security, privacy, or safety, regardless of the above

A finding is **auto-applied** (recommendation taken silently, surfaced in Gate 2 summary) when its `FIX:` does any of:

- Rewrites or rephrases task description wording without changing the user-visible outcome
- Trims a description that exceeds the 600-character budget
- Removes anti-pattern content (code snippets, line numbers, step-by-step instructions in task descriptions)
- Performs a purely cosmetic acceptance-criterion rewrite (whitespace, punctuation, grammar; no testable specifics added or removed)
- Realigns spec ↔ task traceability identifiers when both source and target SPEC requirements remain covered by some task after the realignment
- Reshapes work packages while preserving task membership and external dependencies
- Adjusts `parallel_safe_with` claims (sub-agent scheduling, not shipped outcome)

**Safety-tag override.** Any finding tagged security, privacy, or safety prompts regardless of which auto-apply category it would otherwise fall into.

**Ambiguous-rewrite default.** When an acceptance-criterion rewrite is neither obviously cosmetic nor obviously testable-specific, prompt. The "any other testable specific" catch-all covers a list that cannot be exhaustively enumerated; when the orchestrator cannot determine the rewrite's category mechanically, defer to the user.

### Decision-Card Flow

For each finding classified as requiring a user-facing decision, present a card using `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`. Read that reference once at the start of Step 7; do not re-read it per finding.

Apply the blanket-mode threshold from the reference: when running unattended (`proceed through all stages` or equivalent) AND the threshold conditions all hold, take the reviewer's recommendation silently and tag the entry `← auto (blanket-approved, low-risk)` for the Gate 2 summary. Otherwise present the card and wait for user input.

For each auto-applied finding, take the reviewer's recommendation silently. Append the finding to the round's auto-applied accumulator (see Step 8) for surfacing in Gate 2.
```

- [ ] **Step 2: Update the existing severity-resolution paragraph to reference the filter**

Locate this exact existing line in Step 7:

```
Collect structured findings from the spawned reviewer(s). Apply severity resolution rules:
```

Replace with:

```
Collect structured findings from the spawned reviewer(s). Classify each finding using the Outcome Filter above. For findings requiring a user-facing decision, present cards via the Decision-Card Flow above. For auto-applied findings, take the reviewer's recommendation silently and record in the round's auto-applied accumulator. Then apply severity resolution rules:
```

- [ ] **Step 3: Verify Step 7 references the new reference and contains the filter**

Run:

```bash
rg -n "references/decision-prompts.md|### Outcome Filter|### Decision-Card Flow|Safety-tag override|Ambiguous-rewrite default|auto-applied accumulator" plugins/super-developer/skills/review-plan/SKILL.md
```

Expected: at least 6 matching lines.

- [ ] **Step 4: Commit Task 2**

```bash
git add plugins/super-developer/skills/review-plan/SKILL.md
git commit -m "$(cat <<'EOF'
feat(review-plan): outcome filter and decision-card flow in Step 7

Classify each reviewer finding as outcome-changing (presented as a
decision card via the new shared reference) vs auto-applied (silently
taken with the reviewer's recommendation, accumulated for Gate 2).
Safety-tagged findings always prompt regardless of category.
Ambiguous AC rewrites default to prompt.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 3: Add the per-round accumulator note to `review-plan` Step 8

**Files:**
- Modify: `plugins/super-developer/skills/review-plan/SKILL.md`

Step 8 ("Re-Review if Changes Were Made") today re-runs reviewers but maintains no per-round audit trail. The cumulative-listing rule in Gate 2 requires accumulating auto-applied edits across rounds. This task documents that accumulator as Step 8 state.

- [ ] **Step 1: Insert the accumulator note**

Locate this exact existing line in Step 8:

```
Re-review only at the depth required by the changes:
```

Insert this new paragraph **immediately above** that line:

```markdown
**Per-round auto-applied accumulator.** Step 7 records auto-applied edits to a per-round buffer (e.g., `auto_applied[round_n]`). When Step 8 enters a new round, append a new buffer; do not overwrite. Step 9's Gate 2 summary reads all buffers across rounds 1..N. When all rounds collapse to a single round, the round headers are omitted in Gate 2 and the listing reverts to a flat bullet list.

```

- [ ] **Step 2: Verify the accumulator note is present**

Run:

```bash
rg -n "Per-round auto-applied accumulator" plugins/super-developer/skills/review-plan/SKILL.md
```

Expected: one match.

- [ ] **Step 3: Commit Task 3**

```bash
git add plugins/super-developer/skills/review-plan/SKILL.md
git commit -m "$(cat <<'EOF'
feat(review-plan): per-round auto-applied accumulator in Step 8

Document the per-round buffer Step 7 appends to and Step 9 reads. Each
re-review round adds its own buffer; Gate 2 lists cumulatively across
rounds, grouped by round when there is more than one.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 4: Add Gate 2 summary sections and always-blocks rule to `review-plan` Step 9

**Files:**
- Modify: `plugins/super-developer/skills/review-plan/SKILL.md`

Step 9 today shows the final-state plan deliverables with `← modified` / `← added` / `← dismissed` markers. After this task, Step 9 also surfaces the explicit `Decisions made` and `Auto-applied refinements` sections and is documented as always-blocking under blanket mode.

- [ ] **Step 1: Add the Decisions Made and Auto-Applied Refinements template**

Locate this exact existing block in Step 9 (the example template):

```markdown
### What Will Be Delivered
- JWT auth middleware on all /api/* routes
- Rate limiting (200 req/15min/IP) ← modified by review
- Error recovery for token refresh failures ← added by review
- Distributed cache layer ← dismissed (disproportionate)
- CORS configuration for new namespace
```

Append this block **immediately after** the existing example, inside the same fenced markdown block:

```markdown

### Decisions made (4)
- WP1 over-scope        → P1-T003 moved to tests/regression/
- Orphan sweep          → kept
- Read-fail-fast guard  → kept
- picture_area threshold → bundled with WP2

### Auto-applied refinements (8 total)

Round 1 (5):
- AC-7 reworded (S3 atomicity already covers torn writes)
  - before: "no torn writes / no partial bytes"
  - after:  "two concurrent writes produce a coherent body matching one of the writes' bodies"
- AC-2 perf bound removed (was undefined)
- ACs 3, 5, 9 tightened (rephrasing only)
- WP9 split into WP9a + WP9b (delegation only)
- Spec/task traceability IDs aligned (both sides remain covered)

Round 2 (3):
- P3-T001, P2-T002 trimmed to intent
- Backend-down integration tests added to P5-T002
- SPEC.md softened on cached-pipeline error wording
```

- [ ] **Step 2: Add the section-format rule**

Locate this exact existing rule in Step 9 (in the **Rules:** list):

```
- Every `← added by review` or `← modified by review` marker must map to a specific review finding that caused the change.
```

Insert this new rule **immediately after** that rule:

```markdown
- The `### Decisions made` section lists each user-facing decision (one per outcome-changing finding) with its resolved outcome. Omit the section when no user-facing decisions were taken.
- The `### Auto-applied refinements` section lists every finding the orchestrator resolved silently, grouped by re-review round when the review entered re-review (Step 8); a flat bullet list otherwise. For acceptance-criterion rewrites, include the before → after text inline so the user can spot any locked-in implementation detail. Omit the section when nothing was auto-applied.
```

- [ ] **Step 3: Document Gate 2 always blocks**

Locate this exact existing rule in Step 9:

```
- **Blocking gate** — the user must explicitly approve before finalization.
```

Replace with:

```markdown
- **Blocking gate** — the user must explicitly approve before finalization. **Gate 2 always blocks regardless of blanket-mode authorization** (`proceed through all stages` does not bypass it). Bypassing Gate 2 would defeat the purpose of the auto-applied audit trail — the user would only see silent decisions after implementation has run.
```

- [ ] **Step 4: Verify Step 9 contains the new sections and rule**

Run:

```bash
rg -n "### Decisions made|### Auto-applied refinements|Gate 2 always blocks regardless of blanket-mode" plugins/super-developer/skills/review-plan/SKILL.md
```

Expected: at least 3 matching lines.

- [ ] **Step 5: Commit Task 4**

```bash
git add plugins/super-developer/skills/review-plan/SKILL.md
git commit -m "$(cat <<'EOF'
feat(review-plan): decisions and auto-applied sections in Gate 2

Add the Decisions Made and Auto-Applied Refinements sections to the
Gate 2 announcement template, with the per-round grouping rule for
re-review and the AC before/after inline format. Document Gate 2 as
always-blocking regardless of blanket-mode authorization.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 5: Add the design-decision filter and decision-card flow to `review-code` Pipeline `fix` action

**Files:**
- Modify: `plugins/super-developer/skills/review-code/SKILL.md`

The current Pipeline `fix` action says "Fix confirmed 🔴 and 🟠 findings in the merge worktree, with per-fix approval. Commit fixes to the feature branch." After this task, when blanket mode is authorized, the per-fix approval is replaced for **design-decision** findings only by a card via the shared reference; non-design-decision findings are fixed silently. When blanket mode is **not** authorized, the existing per-fix `yes/skip` semantics in `local-workflow.md` and `pr-workflow.md` are preserved.

- [ ] **Step 1: Replace the Pipeline `fix` row's action description**

Locate this exact existing line in the **Pipeline Gated Actions** table:

```
| `fix` | Fix confirmed 🔴 and 🟠 findings in the merge worktree, with per-fix approval. Commit fixes to the feature branch. |
```

Replace with:

```
| `fix` | Fix confirmed 🔴 and 🟠 findings in the merge worktree. Under blanket mode, design-decision findings (see Design-Decision Filter below) are presented as decision cards via `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`; all other fixes apply silently. Outside blanket mode, per-fix `yes/skip` semantics from `references/local-workflow.md` and `references/pr-workflow.md` are preserved. Commit fixes to the feature branch. |
```

- [ ] **Step 2: Add the Design-Decision Filter subsection**

Locate the heading `### Pipeline Context — Report & Actions` near the end of the file. Insert this new subsection **immediately before** that heading:

```markdown
### Design-Decision Filter

When applying fixes under blanket mode, a finding is **promoted to a decision card** only when **all three** conditions hold:

1. Severity is `[BLOCKER]` or `[CRITICAL]`.
2. The reviewer surfaced two or more valid fix approaches with different runtime behavior, blast radius, or public surface area.
3. Picking among the approaches is a product or architecture decision rather than a code-quality decision.

Examples that prompt:

- "SQL injection — parameterize the query (status quo) OR migrate to ORM (3 callers affected, behavior preserved)"
- "Auth bypass — fix at middleware (centralized) OR per-route guard (explicit but verbose)"
- "Race condition — pessimistic lock (slower) OR optimistic retry (more code, faster happy path)"

Examples that do **not** prompt (fixed silently with the only sensible fix):

- "SQL injection — switch to parameterized query" (only one approach)
- "Off-by-one — change `<` to `<=`" (only one approach)
- "Missing null check — add guard" (only one approach)
- Any test-only fix, regardless of approach count, since it does not change shipped runtime behavior

When promoted, the card uses the shared template at `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`. Outside blanket mode, the existing per-fix `yes/skip` semantics in the workflow references continue to apply.

```

- [ ] **Step 3: Verify the filter and reference are present**

Run:

```bash
rg -n "### Design-Decision Filter|references/decision-prompts.md|Outside blanket mode|when all three" plugins/super-developer/skills/review-code/SKILL.md
```

Expected: at least 3 matching lines.

- [ ] **Step 4: Commit Task 5**

```bash
git add plugins/super-developer/skills/review-code/SKILL.md
git commit -m "$(cat <<'EOF'
feat(review-code): design-decision filter for pipeline fix action

Under blanket mode, promote a finding to a decision card only when it
is BLOCKER/CRITICAL with ≥2 valid approaches that change runtime
behavior, blast radius, or public surface. All other fixes apply
silently. Outside blanket mode, per-fix yes/skip semantics from the
local and PR workflow references are preserved.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 6: Add the blanket-mode pointer to `review-code/references/local-workflow.md`

**Files:**
- Modify: `plugins/super-developer/skills/review-code/references/local-workflow.md`

- [ ] **Step 1: Locate the Phase 5 actions section and append a blanket-mode note**

Read the file to locate Phase 5. The Phase 5 section describes per-fix `yes/skip` semantics. After the existing Phase 5 actions table or list, append this exact block as a new subsection:

```markdown

### Blanket-mode override

When the user has authorized blanket mode (`proceed through all stages` or equivalent), the per-fix `yes/skip` flow above is replaced by the design-decision filter in the parent SKILL — see `### Design-Decision Filter` in `${CLAUDE_PLUGIN_ROOT}/skills/review-code/SKILL.md`. Design-decision findings present a card via `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`; all other fixes apply silently.
```

- [ ] **Step 2: Verify the pointer is present**

Run:

```bash
rg -n "### Blanket-mode override|Design-Decision Filter|references/decision-prompts.md" plugins/super-developer/skills/review-code/references/local-workflow.md
```

Expected: at least 3 matching lines.

- [ ] **Step 3: Commit Task 6**

```bash
git add plugins/super-developer/skills/review-code/references/local-workflow.md
git commit -m "$(cat <<'EOF'
docs(review-code): blanket-mode pointer in local-workflow

Add a Phase 5 subsection noting that per-fix yes/skip semantics are
replaced by the design-decision filter in the parent SKILL when
blanket mode is authorized.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 7: Add the blanket-mode pointer to `review-code/references/pr-workflow.md`

**Files:**
- Modify: `plugins/super-developer/skills/review-code/references/pr-workflow.md`

- [ ] **Step 1: Locate the Phase 5 actions section and append a blanket-mode note**

Append this exact subsection at the end of the Phase 5 actions section:

```markdown

### Blanket-mode override

When the user has authorized blanket mode (`proceed through all stages` or equivalent), the per-fix `yes/skip` flow above is replaced by the design-decision filter in the parent SKILL — see `### Design-Decision Filter` in `${CLAUDE_PLUGIN_ROOT}/skills/review-code/SKILL.md`. Design-decision findings present a card via `${CLAUDE_PLUGIN_ROOT}/references/decision-prompts.md`; all other fixes apply silently.
```

- [ ] **Step 2: Verify the pointer is present**

Run:

```bash
rg -n "### Blanket-mode override|Design-Decision Filter|references/decision-prompts.md" plugins/super-developer/skills/review-code/references/pr-workflow.md
```

Expected: at least 3 matching lines.

- [ ] **Step 3: Commit Task 7**

```bash
git add plugins/super-developer/skills/review-code/references/pr-workflow.md
git commit -m "$(cat <<'EOF'
docs(review-code): blanket-mode pointer in pr-workflow

Add a Phase 5 subsection noting that per-fix yes/skip semantics are
replaced by the design-decision filter in the parent SKILL when
blanket mode is authorized.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

### Task 8: Final verification

**Files:**
- Inspect all files changed by Tasks 1-7.

- [ ] **Step 1: Check working tree**

Run:

```bash
git status --short
```

Expected: clean working tree after all task commits.

- [ ] **Step 2: Check the new shared reference is referenced from every consumer**

Run:

```bash
rg -n "references/decision-prompts.md" plugins/super-developer
```

Expected: matches in `review-plan/SKILL.md`, `review-code/SKILL.md`, `review-code/references/local-workflow.md`, `review-code/references/pr-workflow.md` (4 distinct files).

- [ ] **Step 3: Check the outcome filter and decision-card flow are present in review-plan**

Run:

```bash
rg -n "### Outcome Filter|### Decision-Card Flow|Per-round auto-applied accumulator|Safety-tag override|Ambiguous-rewrite default" plugins/super-developer/skills/review-plan/SKILL.md
```

Expected: at least 5 matching lines (one per phrase).

- [ ] **Step 4: Check Gate 2 has both new sections and the always-blocks rule**

Run:

```bash
rg -n "### Decisions made|### Auto-applied refinements|Gate 2 always blocks regardless of blanket-mode" plugins/super-developer/skills/review-plan/SKILL.md
```

Expected: at least 3 matching lines.

- [ ] **Step 5: Check the design-decision filter is present in review-code**

Run:

```bash
rg -n "### Design-Decision Filter|all three.*conditions|test-only fix" plugins/super-developer/skills/review-code/SKILL.md
```

Expected: at least 3 matching lines.

- [ ] **Step 6: Check both review-code workflow references have the blanket-mode override**

Run:

```bash
rg -n "### Blanket-mode override" plugins/super-developer/skills/review-code/references/local-workflow.md plugins/super-developer/skills/review-code/references/pr-workflow.md
```

Expected: 2 matches (one per file).

- [ ] **Step 7: Check no stale phrasing slipped in**

Run:

```bash
rg -n "asked for one freeform decision|wall of findings|six findings as a single|paraphrase the FIX" plugins/super-developer
```

Expected: no matches. (These are phrasings used in the spec or in conversation that should not appear in the shipped skill files.)

- [ ] **Step 8: Review the diff scope**

Run:

```bash
git diff main...HEAD -- plugins/super-developer
```

Expected: changes limited to the five files listed in this plan's File Map (one created, four modified). No accidental edits elsewhere.

---

## Backward Compatibility

- Existing `review-plan` flows that do not use blanket mode are unchanged. The decision-card flow is invoked for every plan review, but in single-reviewer mode the user is always prompted on outcome-changing findings — same prompt count as today, just one card per finding instead of one wall.
- Existing `review-code` flows in local mode (without blanket authorization) keep their `yes/skip` semantics. Pipeline-mode runs without blanket authorization also keep per-fix approval. The new design-decision filter only activates under blanket mode.
- `audit`, `implement`, `tasks`, and `code-doc` skills are not touched.

## Self-Review

- **Spec coverage**: Every locked decision (LD 1–11) maps to a task: LD 1 (filter rule) → Task 2; LD 2 (skill scope) → Tasks 2 + 5; LD 3 (threshold rule) → Task 1; LD 4 (no persistence) → no task needed (default); LD 5 (abort = no-op) → no task needed (Non-Goals doc only); LD 6 (plain text) → Task 1 card template; LD 7 (hybrid architecture) → Tasks 1 + 2 + 5; LD 8 (single-reviewer always prompts) → Task 1; LD 9 (Gate 2 always blocks) → Task 4; LD 10 (AC rewrites prompt unless cosmetic) → Task 2 filter; LD 11 (`parallel_safe_with` auto-apply) → Task 2 filter.
- **Placeholder scan**: No `TBD`, `TODO`, or vague directives. All steps include the exact text to write or the exact `rg` command and expected match count.
- **Type / name consistency**: Field names used consistently across tasks: `Outcome Filter`, `Decision-Card Flow`, `Design-Decision Filter`, `Blanket-mode override`, `Decisions made`, `Auto-applied refinements`, `Per-round auto-applied accumulator`. The shared reference's section numbering (`## 1. Prompt Card Template`, `## 2. Letter-Prompt Convention`, etc.) is set in Task 1 and not referenced by number elsewhere — referrers cite section names instead, so renumbering inside Task 1 will not break later tasks.
