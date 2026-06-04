# Decision Prompts

Load when a skill must present user-facing decision cards for review findings or workflow choices. This reference owns display mechanics only; each skill owns eligibility, side-effect gates, and whether a decision may be auto-applied.

## Card Template

Use this field order. Borders are illustrative; plain separators are acceptable.

```text
─────────────────────────────────────────────────────────────────
  <Skill> — Decisions Required (<X> of <Y>)
  Feature: <feature-name>            Progress: ●○○○
─────────────────────────────────────────────────────────────────
  Decision <N> — <plain-language headline>
─────────────────────────────────────────────────────────────────

  Outcome impact: <what changes in what ships>

  <reviewer's case in 1-3 lines>

  What ships either way (when relevant):
    <bullets of unchanged things>

  What changes:
    [<key>] <option>  (recommended)
            <pro/con if non-obvious>
    [<key>] <option>
            <pro/con>

  Your call ▸ _
```

Rules:

- Plain-language headline is ≤80 characters and derived from the reviewer `TITLE` by removing locator prefixes.
- `Outcome impact` names the filter category that promoted the finding.
- The reviewer's case comes from `ISSUE`, truncated only when necessary.
- Options come from `FIX` lines; do not invent replacement actions.
- Costs/pros/cons come from `COST` when present.

## Letter Keys

- Use single-letter keys not otherwise reserved.
- Reserved keys: `B` and `D`.
- The recommended option is tagged `(recommended)`.
- Pressing Enter selects the recommended option.
- `[B] Apply my recommendation to all <N> remaining` may appear only when the invoking skill has already determined the remaining findings are blanket-eligible.
- `[D] More details` may appear when supporting context is worth showing on demand.

## Blanket-Mode Boundary

This reference does not decide blanket eligibility. The invoking skill must decide:

- which finding categories require user approval;
- which side effects are allowed;
- whether security, privacy, or safety findings force prompts;
- whether pipeline automation may auto-apply low-risk recommendations.

When auto-applying a recommendation, the invoking skill's summary must label it clearly, for example `← auto (blanket-approved, low-risk)`.

## Constructing Recommendations

Use the reviewer's `FIX` line as the recommendation text.

If reviewers file duplicate findings with different `FIX` lines, do not choose silently. Present the alternatives and force a prompt.

Interpret multi-clause `FIX` lines as follows:

- conjunction (`AND`, `and`, `+`, or a clear required sequence): one option containing the full line;
- disjunction (`OR`, `or alternatively`, or numbered alternatives): split into options and default to the first unless the reviewer explicitly orders them otherwise;
- ambiguous comma lists: default to conjunction.

The safe bias is to preserve required combined actions rather than split them incorrectly.
