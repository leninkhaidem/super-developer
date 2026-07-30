# Convergence & Delivery Loop — Design Spec

Status: **DELIVERED** on `chore/prompt-budget-cleanup`. Written as a proposal; now maintained as the
record of what actually shipped. Passages corrected after delivery are marked **DELIVERED /
CORRECTED**. The original reasoning is kept, not deleted, so the trade-offs stay auditable and a
future reader can see which claims were wrong and why.
Branch: `chore/prompt-budget-cleanup`
Baseline measured: this worktree, all numbers below are measured, none estimated
Delivered by commits `654023b` (cost-based routing, bounded repair loop, deliver-on-exhaustion),
`e8beb31` (stop-evidence obligation reachable from every stop), and `a37cd8d` (escalate once on
exhaustion, artifact-path conventions).

Reading caveat: the fenced blocks in §2 are the **proposal's** draft wording. The delivered wording
lives in the tree and differs in detail; where a detail matters it is quoted verbatim in §2.4, §2.5,
or §11.

## Recommendation up front

**Adopt the Minimum Viable Change only, plus one cheap add-on (Add-on 1).**
Recommend AGAINST the convergence test, the orchestrator/worker split, a new preflight
section, and a 13th shared reference.

The recommended change edits **one file** (`skills/diagnose-and-fix/SKILL.md`) at
**six line ranges**, and leaves all 38 existing numeric-cap lines untouched.

**DELIVERED / CORRECTED (D1): the shipped change edits three files, not one.** Review of this spec
found two of its factual claims wrong, and each correction pulled in a file the recommendation had
ruled out:

| File edited | Why |
|---|---|
| `skills/diagnose-and-fix/SKILL.md` | §2.1 cost test and §2.2 step 15 as designed, **plus** the explicit three-attempt cap §2.2 wrongly claimed was unnecessary (§2.2 correction), plus the exhaustion escalation and the `DIAGNOSIS.md` path convention (§2.5, §11 q2) |
| `skills/diagnose-and-fix/references/fix-implementer-contract.md` | the worker's scope-expansion stop had to be rekeyed off category onto authorized scope, or its own worker would refuse the repairs §2.1 newly routes to it; **plus** the right-size clause (§2.4) |
| `skills/implement/SKILL.md` | stop-evidence obligation, because open question 4 was wrong (§1 correction), its `.tasks/<feature>/reports/` location, and the exhaustion escalation (§2.5) |

The claim about the 38 cap lines held. Measured with the §5 grep at `23e3e52` (pre-change) versus the
delivered tree: 38 lines / 14 files → 43 lines / 15 files, and diffing the two grep outputs shows
**additions only** — the 5 added lines are step 12's new cap plus the escalation clauses. No
pre-existing cap line was reworded.

Reason: the pain is real but narrow, and most of the machinery in the original brief
would replace a mechanically checkable rule ("3 attempts") with an unfalsifiable one
("did this attempt yield new information?"). A judgement with no failure signal cannot
be verified by a reviewer, cannot be tested by `test_skill_prompts.py`, and cannot be
detected when a mid-tier agent applies it wrongly. That is precisely the class of
unfalsifiable prompt complexity this repo has been removing. Confronting that trade
head-on: the numeric cap's inflexibility is a *known, bounded* cost; the convergence
test's inconsistency would be an *unknown, unbounded* one.

## 1. Problem statement

| Objective | Actual pain | Diagnosis |
|---|---|---|
| 1. Frictionless agentic loop | Two incidental interruptions inside an already-authorized bug repair: task-local Testing Authorization (`skills/diagnose-and-fix/SKILL.md:63-67` and `:68-69`) and `.superdeveloper/preferences.yml` creation (`:90-92`). | Narrow. Two clauses. |
| 2. Avoid overengineering | Not currently violated by the cap; would be violated by the fix originally proposed. | The cap is 38 lines of *repetition*, but repetition of a rule that costs nothing to read and cannot be misread. |
| 3. Bugs must not be dragged through planning | `skills/diagnose-and-fix/SKILL.md:22-23` routes "cross-module/service, contract, schema, security, data, concurrency, performance, dependency, or otherwise broad/risky" through `implementation-plan`. That list matches nearly every real defect, so planning is the de-facto default. | **This is the real defect.** One line pair. |
| (unstated but real) Never return empty-handed | `diagnose-and-fix` has no artifact store. On a Stop it returns a **chat-only** diagnosis (`:129-132` Output) and may have committed nothing (delivery `local only`). The user returns to an empty branch. | Genuine gap. `implement` does *not* share it — its packages, proof, and report artifacts are already durable on disk when it stops. |

The empty-handed problem is therefore **specific to `diagnose-and-fix`**, not to
`implement`. That single observation removes most of the proposed scope.

**DELIVERED / CORRECTED (D3): the second half of that claim is wrong.** `implement`'s durable
artifacts are real, but the citation behind the claim — `skills/implement/SKILL.md:47-48`, "the
package result report is the durable done-evidence receipt" — covers **done** evidence only.
Non-convergence can fire **at readiness**, before any package agent has been dispatched, and at that
moment no package report, proof, or package branch exists yet: the user really does return to nothing
but chat. `implement` therefore also received a stop-evidence obligation (see §11 q4 and §2.5). The
gap is **narrower** in `implement` than in `diagnose-and-fix` — usually there are artifacts — but it
is not absent, and "usually" is not a design guarantee.

## 2. Minimum viable change (RECOMMENDED)

Three edits, one file. Two of them are approved decisions A/B/C; the third is the
delivery clause.

**DELIVERED / CORRECTED:** this section is the proposal. What shipped is this plus four additions —
the explicit cap (§2.2 correction), the scope-expansion rekey and right-size clause (§2.4), the
exhaustion escalation (§2.5), and the two artifact-path conventions (§11 q2). §12 accounts for the
difference.

### 2.1 Cost-based routing (approved decisions A, B, C) — replaces a category list

Replace `skills/diagnose-and-fix/SKILL.md:22-23`:

> `- Keep repairs minimal. Route cross-module/service, contract, schema, security, data, concurrency, performance,`
> `  dependency, or otherwise broad/risky change through `implementation-plan`.`

with:

```
- Keep repairs minimal. Classify a repair by cost, not by category. It is `localized` when both hold: the
  mechanism is confirmed by evidence, ideally a deterministic failing test, and the change is bounded and cheaply
  reversible. When both hold, fix and review it here whatever subsystem it touches.
- A repair is `broad/risky` and goes through `implementation-plan` only when one of these holds: the mechanism is
  unconfirmed and the fix requires choosing between viable designs; the change is hard to reverse, such as a
  schema or data migration or a published contract or API; or the blast radius cannot be bounded.
```

**Why this is the cheapest possible form of the change.** `broad/risky` is used as a
label at seven other sites. Redefining the label at its single point of definition
makes all seven inherit the new meaning with **zero further edits**:

| Free-riding site | Text | Still correct? |
|---|---|---|
| `diagnose-and-fix/SKILL.md:25-26` | "For a broad/risky production repair, preserve the confirmed diagnosis…" | Yes |
| `diagnose-and-fix/SKILL.md:77` | "blast radius and `localized` versus `broad/risky` classification" | Yes — now better defined |
| `diagnose-and-fix/SKILL.md:97` | "Route expansion back to diagnosis and broad/risky work to `implementation-plan`" | Yes — this **is** degradation-ladder rung 2 |
| `diagnose-and-fix/SKILL.md:114` | "Broad/risky existing-system or feature change → invoke `implementation-plan`" | Yes |
| `diagnose-and-fix/SKILL.md:123` | "A localized fix expands beyond approved paths or crosses a broad/risky boundary." | Yes |
| `diagnose-and-fix/references/fix-implementer-contract.md:78` | "The parent re-diagnoses and routes broad/risky work to `implementation-plan`" | Yes |
| `worktree/references/bugfix-hotfix-workflow.md:88` | "When a confirmed broad/risky production repair is routed through planning…" | Yes |

Security-forces-planning removal (decision C) is safe. Verified in this worktree:

- `skills/review-code/SKILL.md:40` — "add at most one specialist only when the diff/evidence triggers a sensitive surface: security/privacy/safety;"
- `skills/review-code/SKILL.md:74` — "🔴 **BLOCKING** — must resolve before merge/commit/audit handoff: correctness, security, privacy, safety,"
- `skills/review-code/SKILL.md:96` — "Documented intent disputes only non-security/privacy/safety findings; real security/privacy/safety risks stay confirmed."

All three still say what decision C assumes. Security therefore keeps a blocking gate
on the localized path.

### 2.2 Deliver-on-exhaustion (the one genuinely new obligation)

Add step 15 to `skills/diagnose-and-fix/SKILL.md` (after current step 14):

```
15. If the repair cannot be completed — unconfirmed mechanism, review non-convergence, or a named blocker — do not
    return empty-handed. In the approved bugfix worktree leave the deterministic reproducing test (or the exact
    reason none exists) and a written diagnosis file naming the mechanism evidence, what was tried, and the exact
    blocker. Land them only at the delivery level already authorized: `local only` leaves them uncommitted.
    Escalation changes method, never authority; never merge, push, or act outside the authorization to deliver it.
```

**No new exhaustion trigger is needed.** `diagnose-and-fix:100-103` (step 12) invokes
`review-code`, whose Stop-if already reads *"A blocking seam finding will not converge
within 3 attempts."* (`skills/review-code/SKILL.md:143`, echoed at
`references/pipeline-report.md:66`). The existing numeric cap already bounds the
`diagnose-and-fix` repair loop. Step 15 only changes **what happens on expiry**, from
"stop" to "deliver, then stop".

**DELIVERED / CORRECTED (D2) — the paragraph above was this spec's blocking error B1. It is false.**
The `diagnose-and-fix` repair loop was genuinely **unbounded**, for three independent reasons:

- `:143` speaks of a **seam** finding — pipeline-mode vocabulary. `diagnose-and-fix` step 12 passes
  no pipeline context and no PR identifier, so `review-code` selects **local** mode
  (`skills/review-code/SKILL.md:26`) and loads `references/local-workflow.md`.
- `skills/review-code/references/local-workflow.md` contains **no cap at all**. Measured in the
  delivered tree: 104 lines, and `grep -ciE "three|attempt|converge"` returns `0`.
- Even where a cap does exist it bounds `review-code`'s own repair loop, not the outer
  `diagnose-and-fix` fix → review → refix loop, which the parent owns. Nothing stopped the parent
  dispatching a fresh Fix Implementer indefinitely.

The methodological lesson: "an existing rule already covers this" must be verified along the actual
invocation path, in the mode actually selected, at the loop actually owned — not by finding the
number `3` somewhere in the callee.

So an **explicit** cap was delivered in step 12: at most three total repair attempts per confirmed
mechanism; attempt 1 is the initial fix; attempts 2 and 3 must each name a material delta in
mechanism, evidence, or strategy; never retry unchanged and never exceed three total. `3` matches the
existing 38 cap statements, so this adds a bound, not a concept, and **no** "convergence" judgement
was introduced. Step 15 then changes what happens on expiry — from "stop" to "deliver, escalate once,
then stop" (§2.5).

### 2.3 The degradation ladder is 2/3 already built

| Rung | Where it lives | Action |
|---|---|---|
| 1. Localized fix/review loop | `diagnose-and-fix:83-103` steps 8–12, bounded by `review-code/SKILL.md:143` | keep as-is |
| 2. Escalate to `implementation-plan` | `diagnose-and-fix:97` (validation) and `:114-115` (Load if needed) | keep as-is |
| 3. Land repro test + written diagnosis + named blocker | **does not exist** | add (§2.2) |

Rung 2 is *not* auto-escalation from inside the repair loop, and should not become
that. Auto-escalating mid-loop would silently convert an authorized `localized` repair
into a `broad/risky` one — new authority, which decision G forbids. The existing
route (re-diagnose, then route) preserves the authority boundary and costs nothing.

**DELIVERED / CORRECTED:** rung 2 **is** now reached automatically on exhaustion, in both skills. The
hazard named above is real and was not dismissed — it is resolved by separating *method* from
*authority*, which is exactly what §2.5 sets out. Read §2.5 as superseding the "keep as-is" verdict
for rung 2 in the table above, and nothing else in this section.

### 2.4 Right-size clause in the fix implementer contract (DELIVERED — absent from the proposal)

The proposal never mentioned this and should have. Cost-based routing (§2.1) deliberately stops
sending confirmed, bounded, reversible bugs through `implementation-plan` — which also stops sending
them past `skills/implementation-plan/references/design-preflight.md:9`, the plan-time
**over-engineering** lens: *"It flags **over-engineering** — abstractions, layers, configuration,
state, flags, extension points, dependencies, or package splits that are not traced to an accepted
requirement, the `## Acceptance` criteria, or evidenced risk."* Removing planning from the bug path
removes that lens with it, so objective 2 (avoid overengineering, maintainability) would have been
quietly weakened by the very change meant to serve objective 3.

One sentence restores it at the point of work, appended to step 4 ("Minimal fix") of
`skills/diagnose-and-fix/references/fix-implementer-contract.md:64-65`:

> "Add no abstraction, flag, layer, configuration, or extension point that does not trace to the
> confirmed mechanism."

It mirrors what the feature path already tells its workers —
`skills/implement/references/package-agent-contract.md:12` ("the smallest complete implementation
that fully satisfies the assigned closure obligations") and `:57` (the "Right-size pass") — so a bug
worker and a package worker are now held to the same right-sizing bar. It is one sentence in an
existing contract step: no new file, no new section, no new concept, and it lands where the code is
actually written rather than where a reviewer might later notice the bloat.

### 2.5 Escalate once on exhaustion (DELIVERED — replaces add-on 7, and supersedes rung 2's "keep as-is")

Objective 1 is *delivery*, not a halt. A user who is away from the keyboard should not return to a
stopped loop. So exhausting the cap now **escalates** instead of stopping, in both skills. The
numeric cap is unchanged, and no "convergence" or "did this attempt teach us anything?" judgement was
introduced — that was rejected twice on review as unfalsifiable and stays rejected (§3 add-on 2).

**`implement`.** On exhausting 3 attempts on a **code** repair cluster, the cluster is re-classified
as a possible plan defect and, when it qualifies, routed through the **already existing** Plan-defect
route (`skills/implement/SKILL.md:37-41`) instead of being returned to the user. No new machinery:
the route, its qualification test, and its `implementation-continuation` /
`implementation-continuation-focused` modes already existed for plan defects found at readiness,
verification, integration, final review, and audit. Exhaustion is simply one more discovery point.

**`diagnose-and-fix`.** On exhausting 3 attempts on a confirmed mechanism, step 15 still runs first,
and then the parent re-diagnoses and hands the confirmed diagnosis to `implementation-plan` —
degradation-ladder rung 2 — the same route as the validation clause in step 10 (`:110-111` in the
delivered file, `:97` at baseline) and the `Load if needed` entry (`:141` delivered, `:114-115` at
baseline) — now reached automatically rather than only by a fresh user instruction. Line numbers in
§§1–10 are baseline numbers and have shifted; the delivered file is the authority.

**How the authority hazard of §2.3 is resolved.** §2.3 was right that auto-escalation must not
silently convert an authorized `localized` repair into a `broad/risky` one. The resolution separates
method from authority instead of dropping the escalation:

- The handoff to `implementation-plan` is **planning only**. Planning produces artifacts and keeps
  its own approval gate before anything is implemented, so pre-authorizing the *handoff* grants no
  implementation authority. The skill already said so, unchanged: *"Approval of an
  `implementation-plan` route authorizes only the diagnosis handoff and planning; the later Execution
  Contract and delivery gates separately own implementation, source/sidecar publication, target
  merge/push, and release."*
- Because the handoff carries no implementation authority, the fallback is folded into the **standard
  Fix Authorization** so it is covered by default and never becomes a second ask. Delivered wording:
  *"It also covers one exhaustion fallback: if that localized repair exhausts its three attempts,
  re-diagnose and hand the confirmed diagnosis to `implementation-plan` without another ask. That
  handoff is planning only, and planning keeps its own separate approval gate before anything is
  implemented, so it grants no implementation authority and never converts the authorized
  `localized` repair into a `broad/risky` one."* Implementation, delivery, target merge/push, and
  release keep their existing separate gates.
- Step 15 still runs before the escalation, so the away-from-keyboard user returns to **durable
  artifacts plus a plan awaiting approval**, never a bare halt and never a silently widened repair.
- In `implement` the same principle is enforced by the Plan-defect route's **existing**
  qualification: routing is allowed only when it preserves approved semantics, scope, visible
  behavior, risk, and manual exceptions. Delivered wording: *"Escalation changes method, never
  authority: if routing it would change any of those, that is new semantic authority and you stop
  here instead."*

**How termination stays provable by counting.** At most **one** escalation per cluster identity
(`implement`) or per confirmed mechanism (`diagnose-and-fix`); a relabeled or reclustered unit earns
no second escalation; a second exhaustion of the same identity stops for the user. Delivered wording,
`implement`: *"Allow at most one such escalation per cluster identity — if that same cluster exhausts
3 attempts again after readiness is restored, stop for the user, and relabeling or reclustering earns
no second escalation."* And `diagnose-and-fix`: *"at most one such escalation per confirmed
mechanism, and a relabeled mechanism earns no second one. If the same mechanism exhausts three
attempts again, stop for the user."* Worst case per unit is therefore 3 attempts → 1 escalation → 3
attempts → stop. Ping-pong between implementation and planning is impossible by counting alone, with
no judgement required.

## 3. Add-ons, each judged on its own cost

| # | Add-on | Pain it removes beyond the minimum | Files / lines touched | Checkable? | Verdict |
|---|---|---|---|---|---|
| 1 | Fold the two incidental asks into the one Fix Authorization (decision D/H) | Real: removes 2 mid-loop interruptions inside an already-approved repair | 1 file, 3 line ranges, ≈net +2 lines | Yes — count the "ask" points in the file | **ADOPT** |
| 2 | Convergence test replacing the numeric cap (decision E) | None that the minimum does not already cover | 14 files, 38 lines | **No** — "new information?" has no failure signal | **REJECT** |
| 3 | Orchestrator-vs-worker convergence split (nuance 2) | Only meaningful if #2 lands | 14 files | Partly | **REJECT** (moot without #2) |
| 4 | New preflight section (decision F) | ~Nothing — 3 of 4 checks already exist and already sit before the authorization gate (§4) | +1 section per skill | Yes but redundant | **REJECT** |
| 5 | Autonomy envelope as a time/token budget (decision H) | Speculative; agents cannot measure their own token spend reliably, so the budget would be aspirational | 2+ files | **No** | **REJECT** — the existing `approve auto-resolve` / `step-by-step` / `abort` choice at `implement/references/execution-contract.md:135-139` already sets the envelope once |
| 6 | 13th shared reference for the convergence rule (§7) | None once #2 is rejected — there is no new rule to share | +1 file, 14 bindings | n/a | **REJECT** |
| 7 | Raise the cap 3 → 5 | Speculative: would help only if halts are premature, which is unmeasured | 14 files, 38 lines | Yes | **DEFER** — if the user later has evidence of premature halts, the cheapest fix is a mechanical `3`→`5` sweep over the 38 lines and nothing else, as its own separate change |

### Why the convergence test specifically fails its cost test

- **It is unfalsifiable in the only place it matters.** `test_skill_prompts.py` and
  `audit-skill.py` can check line caps, frontmatter, and link resolution. Neither can
  check "was this attempt materially different?". A reviewer reading a transcript
  cannot either, because the orchestrator's judgement is not recorded anywhere.
- **The current rule already contains the useful half.** Every cap site already
  requires the *material-delta* precondition — e.g. `implement/SKILL.md:34-36`,
  `package-dispatch.md:133-134` ("Identity is not progress"),
  `repair-agent-contract.md:38-40` ("a relevant material state/evidence/strategy delta
  must close/narrow the gate…"). Convergence is *already* the gate on each attempt.
  The number is only the outer bound. Replacing the number deletes the bound and keeps
  what already exists.
- **Non-termination becomes possible.** With the number gone, the only stopping
  condition would be an agent's own judgement that it is not learning — exactly the
  judgement a stuck agent is worst at making.
- **The three unit types (nuance 1) survive untouched.** Because we keep the cap, the
  empirical-question ledger, the code-repair cluster circuit, and the plan-defect
  route stay distinct exactly as written today. No flattening risk at all.
- **`empirical-spike`'s producer role (nuance 3) survives untouched.** Its cap
  statement at `:23-25` is a *rejection* rule for malformed/over-cap/unchanged inbound
  packets and needs a number to reject against. It never prompts or routes today
  (`:20-22`) and this design does not touch it.

## 4. Redundancy check: the preflight already exists

Verified by reading `skills/diagnose-and-fix/SKILL.md`. The four requested preflight
checks map onto existing numbered steps, and **all of them already run before** the
single authorization ask at step 7:

| Requested check | Already present at | Quote |
|---|---|---|
| Can reproduce | step 5 (`:71-72`) and status vocabulary in step 6 (`:74`) | "Reproduce and minimize the failure." / "`reproduced`, `not reproduced`, `deterministic failing test`, or `blocked`" |
| Have testing authority | step 3 (`:63-67`) | "resolve testing authority… If authority is insufficient, invoke `testing` or stop with `blocked`/`not-run`" |
| Have required access / credentials | step 4 (`:68-70`) + Stop-if (`:120`, `:126-127`) | "Ask exact approval before instrumentation, validation writes, unsafe commands, credentials, network, service use" / "Root cause is unconfirmed and next evidence requires unavailable input or an unapproved action." |
| Change is reversible | **not stated as such**; nearest is step 6's "blast radius and `localized` versus `broad/risky` classification" (`:77`) | — |

All four already precede the single authorization ask at step 7 (`:82`).
Only the reversibility check is missing, and §2.1 supplies it as axis (ii) of the
two-axis test, at the exact point where it is used. **No new preflight section.**
Adding one would restate three obligations that already exist and already run early —
the classic way these prompts bloat.

## 5. Site-by-site map — all 38 cap lines

Measured with:
```
grep -rniE "three[ -]?(total[ -])?attempt|three-total-attempt|attempts? ?(IDs? )?2[-–]3|attempts 1[-–]3|attempt 3|attempt-3|3 total|3 non-converging|3 attempts|3 materially|over-cap|two materially changed follow-ups|\(2 or 3\)|exceed three" \
  --include='*.md' plugins/super-developer/
```
Result: **38 lines across 14 files.** The brief's list of 12 files / ~20 lines is
wrong on both counts. Missing files were `plugins/super-developer/README.md` (2 lines)
and `skills/implementation-plan/references/validation-checklist.md` (1 line).
`CHANGELOG.md:54` also states the cap but is a historical record and must not change.

**Disposition for all 38: KEEP AS-IS.** The recommended design does not alter the cap,
so no site needs rewriting, delegating, or deleting. Listed in full so a reviewer can
confirm nothing was quietly left inconsistent (the failure mode of reverted commit
6e03ce6).

| # | file:line | quote (short) | change |
|---|---|---|---|
| 1 | `references/package-lifecycle.md:80` | "three-attempt cap: after **3** non-converging repair attempts, stop rather than rename or recluster" | keep |
| 2 | `README.md:27` | "one initial run and at most two materially changed follow-ups are allowed" | keep |
| 3 | `README.md:242` | "…and three-attempt non-convergence still stop." | keep |
| 4 | `skills/empirical-spike/SKILL.md:23` | "one logical question has at most three total attempts" | keep (nuance 3: rejection rule) |
| 5 | `skills/empirical-spike/SKILL.md:24` | "attempt 1 is the initial run; attempts 2–3 are fresh invocations" | keep |
| 6 | `skills/empirical-spike/SKILL.md:25` | "Reject out-of-order, over-cap, or unchanged follow-ups" | keep |
| 7 | `skills/review-plan/references/plan-review-resolution.md:80` | "method, or signal at attempts 2–3" | keep |
| 8 | `skills/review-plan/SKILL.md:33` | "attempts 2–3 are fresh invocations with incremented IDs" | keep |
| 9 | `skills/review-plan/SKILL.md:34` | "Never retry unchanged or exceed three total attempts." | keep |
| 10 | `skills/review-plan/SKILL.md:68` | "method, or signal at attempts 2–3" | keep |
| 11 | `skills/review-plan/SKILL.md:102` | "A logical question reaches attempt 3 without accepted evidence" | keep |
| 12 | `skills/review-code/references/pipeline-report.md:52` | "preserve logical identity through the three-attempt cap" | keep |
| 13 | `skills/review-code/references/pipeline-report.md:66` | "a blocking seam finding that will not converge within 3 attempts" | keep — **this is the exhaustion trigger §2.2 reuses** |
| 14 | `skills/review-code/SKILL.md:126` | "preserve logical cluster identity and the three-attempt cap" | keep |
| 15 | `skills/review-code/SKILL.md:143` | "A blocking seam finding will not converge within 3 attempts." | keep — **trigger reused by §2.2** |
| 16 | `skills/implementation-plan/references/validation-checklist.md:23` | "no unchanged, over-cap, or unbounded question" | keep |
| 17 | `skills/implementation-plan/SKILL.md:31` | "incremented attempt IDs 2–3, and a named corrected packet" | keep |
| 18 | `skills/implementation-plan/SKILL.md:32` | "three total attempts or continually emerging/unbounded questions are non-convergence" | keep |
| 19 | `skills/implementation-plan/SKILL.md:83` | "may invoke attempts 2–3 under the stable question ID" | keep |
| 20 | `skills/implementation-plan/SKILL.md:84` | "never retry unchanged or exceed three total" | keep |
| 21 | `skills/implementation-plan/SKILL.md:101` | "Stop on an unchanged/over-cap question" | keep |
| 22 | `skills/implementation-plan/SKILL.md:131` | "exhausts attempt 3 without an accepted result" | keep |
| 23 | `skills/implement/references/repair-agent-contract.md:28` | "Preserve its logical identity/three-attempt cap" | keep — **nuance 2: worker contract must keep a number** |
| 24 | `skills/implement/references/package-integration-gates.md:96` | "attempt 1 is initial; attempts 2–3" | keep |
| 25 | `skills/implement/references/package-integration-gates.md:97` | "Three total attempts exhaust the circuit" | keep |
| 26 | `skills/implement/references/package-dispatch.md:133` | "Attempt 1 is initial; attempts 2–3 name a material code/diagnostic delta." | keep |
| 27 | `skills/implement/references/package-dispatch.md:134` | "Identity is not progress and cannot reset the three-total-attempt cap." | keep |
| 28 | `skills/implement/references/execution-contract.md:34` | "Each logical question has at most three total attempts" | keep |
| 29 | `skills/implement/references/execution-contract.md:35` | "attempts 2–3 are each a fresh invocation with stable ID" | keep |
| 30 | `skills/implement/references/execution-contract.md:70` | "stable logical-question ID; attempts 1–3" | keep |
| 31 | `skills/implement/references/execution-contract.md:123` | "the existing three-total-attempt circuit; never retry unchanged" | keep |
| 32 | `skills/implement/references/execution-contract.md:134` | "attempt-3 exhaustion, unbounded questions" | keep |
| 33 | `skills/implement/SKILL.md:34` | "Attempt 1 is initial; attempts 2–3 must be fresh, materially changed" | keep |
| 34 | `skills/implement/SKILL.md:35` | "Three total attempts exhaust the circuit" | keep |
| 35 | `skills/implement/SKILL.md:45` | "invoke `empirical-spike` once per attempt under the three-attempt circuit" | keep |
| 36 | `skills/implement/SKILL.md:77` | "incremented attempt ID (2 or 3)" | keep |
| 37 | `skills/implement/SKILL.md:92` | "the three-total-attempt circuit" | keep |
| 38 | `skills/implement/SKILL.md:137` | "exhausted 3 total materially changed attempts" | keep |

### The six ranges that DO change (all in `skills/diagnose-and-fix/SKILL.md`)

| file:line | quote (short) | change |
|---|---|---|
| `:22-23` | "Route cross-module/service, contract, schema, security, data, concurrency, performance, dependency, or otherwise broad/risky change through `implementation-plan`." | **rewrite** to the two-axis cost test (§2.1). Keep "Keep repairs minimal." verbatim. |
| `:44-45` | "One response may authorize the displayed localized route through the selected branch delivery. Unnamed scope, delivery, or side effects remain unauthorized." | **rewrite** to also cover routine testing authority, named `preferences.yml` creation, and diagnosis delivery. Keep the "Unnamed … remain unauthorized" sentence verbatim. The "Target merge/push and cleanup stay at their existing owning boundaries." sentence continues onto `:45-46` and must be preserved intact. |
| `:65-66` (step 3) | "or task-local Testing Authorization for an exact focused approval" | **append ≈9 words**: the Fix Authorization may supply it up front. Every other clause of step 3 unchanged. |
| `:90-92` (step 9) | "require authorization for that exceptional write before creating it there; never create it in root or silently" | **narrow edit**: accept the Fix Authorization's named coverage in place of a second ask. "never create it in root or silently" stays verbatim. |
| after `:107` (new step 15) | — | **add** the deliver-on-exhaustion step (§2.2) |
| `:118-127` (Stop if) | (whole block) | **keep as-is.** Step 15 runs *before* the stop; the stop conditions themselves do not loosen. |

## 6. Obligation inventory

Every safety obligation currently expressed in or adjacent to the six changing ranges,
where it lives afterwards, and how to prove it survived. Modelled directly on what
commit 6e03ce6 silently dropped.

| # | Obligation | Currently at | Afterwards | Verification grep (from `plugins/super-developer/`) |
|---|---|---|---|---|
| 1 | "Keep repairs minimal." | `d&f:22` | same line, unchanged prefix | `grep -c "Keep repairs minimal" skills/diagnose-and-fix/SKILL.md` → `1` |
| 2 | Broad/risky work routes to `implementation-plan` | `d&f:23` | new second bullet (§2.1), plus untouched `:97`, `:114` | `grep -c "implementation-plan" skills/diagnose-and-fix/SKILL.md` — baseline `6` lines, must be ≥ `6` |
| 3 | Preserve confirmed diagnosis + production-base/hotfix/target delivery context on planning handoff | `d&f:24-27` | unchanged | `grep -c "production-base/hotfix/target delivery" skills/diagnose-and-fix/SKILL.md` → `1` |
| 4 | Exact **leases** remain mandatory | `d&f:46`, `:54` | unchanged | `grep -n "leases" skills/diagnose-and-fix/SKILL.md` → lines `46`, `54` |
| 5 | **Ancestry checks** remain mandatory | `d&f:54` | unchanged | `grep -n "ancestry" skills/diagnose-and-fix/SKILL.md` → line `54` |
| 6 | Separate target-merge / target-push bindings | `d&f:54` and step 13 `:104-106` | unchanged | `grep -n "target-merge/target-push" skills/diagnose-and-fix/SKILL.md` → line `54`; `grep -c "target_push" …` → `1` |
| 7 | **Cleanup proofs** in the internal receipt | `d&f:50` | unchanged | `grep -n "cleanup proofs" skills/diagnose-and-fix/SKILL.md` → line `50` |
| 8 | Untracked records include **Git/index-compatible mode** | `d&f:93` | unchanged — the `index-compatible` qualifier is the exact word 6e03ce6 dropped | `grep -c "Git/index-compatible mode" skills/diagnose-and-fix/SKILL.md` → `1` |
| 9 | Untracked records include symlink target and **binary provenance** | `d&f:93`, `:99` | unchanged | `grep -c "binary provenance" skills/diagnose-and-fix/SKILL.md` → `2`; `grep -c "symlink target" …` → `2` |
| 10 | Never infer approval from silence / "fix this" / diagnosis approval | `d&f:30` | unchanged | `grep -c "Never infer approval from silence" skills/diagnose-and-fix/SKILL.md` → `1` |
| 11 | No live incident containment or production mutation | `d&f:31-33`, step 8 `:86`, Stop-if `:124-125` | unchanged | `grep -n "containment" skills/diagnose-and-fix/SKILL.md` → lines `6`, `31`, `86`, `124` (4 hits) |
| 12 | Root checkout never used for repair or delivery | `d&f:20-21` (Always) and `:87-88` (step 8) | unchanged | `grep -c "Keep root checkout files/index user-owned" …` → `1`; `grep -c "use root as the repair or delivery checkout" …` → `1` |
| 13 | Target merge/push and cleanup stay at existing owning boundaries | `d&f:45-46` (sentence wraps the line break) | unchanged sentence inside the rewritten `:44-46` block | `grep -c "existing owning" skills/diagnose-and-fix/SKILL.md` → `1` (do **not** grep the full phrase; it is line-wrapped) |
| 14 | Unnamed scope / delivery / side effects remain unauthorized | `d&f:44-45` | preserved verbatim as the final sentence of the rewritten block | `grep -n "remain unauthorized" skills/diagnose-and-fix/SKILL.md` → lines `45`, `82` (2 hits) |
| 15 | Revalidate every binding immediately before its action; never silently absorb drift | `d&f:50-51`, `:53` | unchanged | `grep -c "Never silently absorb drift" …` → `1`; `grep -c "Revalidate every binding" …` → `1` |
| 16 | Testing authority resolution incl. `invoke testing` / stop `blocked`/`not-run`; never report not-run as passed | `d&f:63-67` | unchanged except the appended clause | `grep -n "never report not-run work as passed" skills/diagnose-and-fix/SKILL.md` → line `67` |
| 17 | Exact approval before instrumentation / unsafe commands / credentials / network / service use; spikes in a throwaway worktree, history never promoted | `d&f:68-70` | unchanged | `grep -n "promote their history" skills/diagnose-and-fix/SKILL.md` → line `70` |
| 18 | `preferences.yml` never created in root or silently; gitignored local creation | `d&f:90-92` | unchanged clause; only the *who authorizes* changes | `grep -c "never create it in root" skills/diagnose-and-fix/SKILL.md` → `1`; `grep -c "gitignored local" …` → `1` |
| 19 | Do not implement substantive edits inline | `d&f:94` | unchanged | `grep -c "Do not implement substantive edits inline" …` → `1` |
| 20 | Never expand authority implicitly | `d&f:97` | unchanged, reinforced by step 15's "Escalation changes method, never authority" | `grep -c "never expand authority implicitly" …` → `1`; `grep -c "never authority" …` → `1` (new, from step 15) |
| 21 | Commit only under the exact receipt, CLEAN snapshot, reviewed-only staging; merge never pushes by itself | `d&f:104-106` | unchanged; step 15 explicitly defers to the authorized delivery level | `grep -n "merge never pushes by itself" skills/diagnose-and-fix/SKILL.md` → line `106` |
| 22 | Preserve useful fixtures; clean only approved throwaway artifacts | `d&f:107` | unchanged (step 15 is added after it, and its artifacts are *not* throwaway) | `grep -n "Preserve useful fixtures" skills/diagnose-and-fix/SKILL.md` → line `107` |
| 23 | Release / force-push / remote-delete keep separate approval boundaries | `d&f:45-46` plus the `worktree` and `release` skills | unchanged; no edit touches them | `git diff --stat -- plugins/super-developer/skills/release plugins/super-developer/skills/worktree` → empty |
| 24 | The three-attempt cap and its 38 statements | 38 lines, 14 files (§5) | **all unchanged** | rerun the §5 grep; must still return exactly 38 lines / 14 files |

Reviewer recipe: run every grep above against the pre-change and post-change trees and
diff the outputs. Only rows 2, 13, 14, 16, 18, 20 may differ, and only in the ways
stated. Row 24 must be byte-identical.

## 7. Shared reference: NO

Do not add a 13th shared reference. Justification:

- Once the convergence test is rejected, **there is no new rule to share**. The
  duplication that exists is 38 statements of `3`, which is cheap to read, impossible
  to misread, and locally contextualised (each site names its own unit type — question
  ledger, repair cluster, seam finding).
- Consolidating would *relocate* burden, not reduce it: each of the 14 files would
  still need a pointer line, so the line count barely moves while a new indirection
  hop appears in every affected prompt. Against objective 2.
- `audit-skill.py:449-450` fails a reference file that links another reference file, so
  the 8 affected **reference** files could not use the ordinary `../../references/x.md`
  form. (Proven live: `conceptualize` FAILS today on exactly this, at
  `references/slice-template.md` → `../../../references/conceptualize-slice-authority.md`.)
  The repo's existing workaround is the repo-root-relative form
  `plugins/super-developer/references/x.md`, which `looks_like_backticked_path`
  (`audit-skill.py:313`) does not classify as a local link — e.g.
  `repair-agent-contract.md:22`. It works, but it means the link is *unverified by the
  auditor*, so half the binding sites would be silently breakable. That is the exact
  half-done-consolidation failure mode of 6e03ce6.
- Recommendation: **leave the duplication alone.**

## 8. Net volume delta (measured on the proposed text)

| File | Now | After | Δ lines | Δ words |
|---|---|---|---|---|
| `skills/diagnose-and-fix/SKILL.md` | 132 lines / 1286 words | ≈145 lines / ≈1496 words | **+13** | **+210** |
| all other 14 cap-bearing files | unchanged | unchanged | 0 | 0 |

Measured components: `:22-23` 2 lines/19 words → 6 lines/102 words (+4/+83);
`:44-45` 2/21 → 4/55 (+2/+34); new step 15 +5/+83; steps 3 and 9 ≈ +2/+10.

**This design does not reduce total prompt volume — it adds 13 lines to one file.**
Justification: the addition is one genuinely new obligation (deliver something rather
than nothing) plus the prose needed to state a *test* instead of a *list*. The list it
replaces was shorter but wrong. The rejected add-ons would have added an estimated
several hundred lines across 14 files for no checkable benefit; rejecting them is where
the volume discipline is applied.

Budget compliance (measured caps from `audit-skill.py:31-36`): 145 lines < 200 hard
cap. 1496 words is inside the 600–1500 skill target and far under the 1800 warning —
but it is **within 4 words of the target ceiling**, so the implementer must count and,
if it overruns, trim §2.1's third sentence rather than compress the prose.

**DELIVERED / CORRECTED — the estimate above under-counted, because the scope grew (§12).** Measured
in the delivered tree with `wc -l -w` and `audit-skill.py`:

| File | Baseline `23e3e52` | Delivered | Δ lines | Δ words |
|---|---|---|---|---|
| `skills/diagnose-and-fix/SKILL.md` | 132 / 1286 | **162 / 1744** | +30 | +458 |
| `skills/diagnose-and-fix/references/fix-implementer-contract.md` | 96 / 900 | **100 / 980** | +4 | +80 |
| `skills/implement/SKILL.md` | 147 / 1554 | **157 / 1700** | +10 | +146 |
| all other cap-bearing files | unchanged | unchanged | 0 | 0 |

All three are inside the 200-line hard cap and under the 1800-word warning;
`diagnose-and-fix/SKILL.md` has **56 words** of headroom against that warning, which is the binding
constraint on any future edit to it. Both SKILL.md files exceed the 600–1500 word *target* and
therefore emit one `words outside target` warning each — a warning, not a failure, and
`implement/SKILL.md` already emitted it before this change. `diagnose-and-fix/SKILL.md` has no line
over 120 characters; `implement/SKILL.md` has one, pre-existing at line 69 and untouched here.

## 9. Risks

| Risk | Severity | Mitigation / what a reviewer must scrutinise |
|---|---|---|
| **A genuinely risky bug now takes the localized path.** The two-axis test admits security, schema-adjacent, and concurrency defects that the category list excluded. | **Highest** — scrutinise hardest | Axis (ii) "bounded and cheaply reversible" plus the explicit `implementation-plan` list must both be read *conjunctively*. `review-code:40/74/96` supplies the security backstop. Reviewer should hand-test the wording against 5 real past defects and check the routing comes out right. |
| Mid-tier agent reads only the first bullet and treats every bug as localized. | Medium | The second bullet must stay adjacent and start with the word "only". Do not split them across a section boundary. |
| "Cheaply reversible" is itself a judgement. | Medium | Accepted, and bounded: it only ever *widens* the localized path, and everything on that path still passes `review-code` blocking gates and the existing delivery approvals. It never authorizes an action. |
| Step 15 is read as licence to commit when delivery was `local only`. | Medium | The step names the constraint twice. Reviewer must confirm both sentences survive and that obligation-inventory row 21 is intact. |
| Non-termination / runaway loops | **Low, by construction** | The numeric caps are untouched (row 24). No loop loses its bound. This is the single biggest advantage of the minimal design over the originally briefed one. **DELIVERED:** §2.5's escalation adds at most one extra bounded cycle per unit identity (3 → escalate once → 3 → stop), so the bound is still a finite count with no judgement in it. §2.2's correction also *added* a bound where there was none. |
| Silent obligation loss (the 6e03ce6 failure) | Medium | §6 with 24 greps; row 24 must be byte-identical. |
| `diagnose-and-fix` word count drifts past 1500 → new audit warning | Low | Measured in §8; implementer must recount. |
| `README.md:242` and `CHANGELOG.md:54` describe the old routing wording | Low | Neither mentions the category list; both describe the cap, which is unchanged. Verify no README sentence claims security forces planning: `grep -n "security" plugins/super-developer/README.md`. |

## 10. Verification plan

Baseline **measured in this worktree before any change**:

```
cd plugins/super-developer/assets && python3 -m unittest discover -s tests
  → Ran 67 tests … FAILED (failures=1)
  → the single failure is test_semgrep_rules.SemgrepRulesTest
     .test_scan_invokes_structured_privacy_argv_and_writes_raw_summary
     (macOS /private/var vs /var symlink) — pre-existing, unrelated

for d in plugins/super-developer/skills/*/; do
  python3 plugins/super-developer/skills/skill-authoring/scripts/audit-skill.py "$d"; done
  → 12 PASS, 3 FAIL (pre-existing): code-doc (SKILL.md > 200 lines),
    conceptualize (hidden second-hop reference in references/slice-template.md),
    perspectives (folded description 487 > 280 chars)
```

After implementation, all three must hold **identically** — same 67/1, same 12/3, and
`diagnose-and-fix` must still print `RESULT: PASS`. Then:

1. Rerun the §5 grep → still exactly 38 lines / 14 files.
2. Run all 24 §6 greps and diff against baseline; only rows 2, 13, 14, 16, 18, 20 differ.
3. `grep -c "cross-module/service" plugins/super-developer/skills/diagnose-and-fix/SKILL.md` → `0`.
4. `wc -l -w plugins/super-developer/skills/diagnose-and-fix/SKILL.md` → ≤ 200 lines, ≤ 1500 words.

**DELIVERED / CORRECTED:** the three baselines held exactly (67 tests / 1 pre-existing failure; 12
PASS / 3 FAIL; `diagnose-and-fix` still `RESULT: PASS`). Check 4's ≤ 1500-word half was **not** met
and was superseded: the delivered file is 1744 words, which is over the 600–1500 *target* (one
warning) and under the 1800 *warning threshold* that `audit-skill.py` actually gates on. Check 1 was
superseded too: the grep now returns 43 lines / 15 files, because step 12's new cap and §2.5's
escalation clauses match it. What must still hold is the stronger statement: the 38 pre-existing cap
lines are byte-identical, provable by diffing the grep outputs and seeing additions only.

## 11. Open questions for the user — ALL FOUR NOW CLOSED

Each question is kept verbatim, with the decision recorded under it.

1. **Risk appetite on the widened localized path.** Confirm that a *confirmed,
   bounded, reversible* security or concurrency defect really should be fixed without
   planning, backed only by `review-code`'s blocking security gate. This is the one
   place where the design trades safety for speed.

   **DECIDED — accepted by the user.** A confirmed, bounded, reversible defect is fixed on the
   localized path whatever its category. The backstops are unchanged: `review-code`'s blocking
   security/privacy/safety gate (`skills/review-code/SKILL.md:40`, `:74`, `:96`) and the worker's
   scope-expansion stop, which still fires on unauthorized paths, changed public API/schema/contract,
   unauthorized dependency/service/config changes, live actions, unsafe commands, or broader
   verification, and which still forbids the worker widening its own authority
   (`fix-implementer-contract.md:76-80`). This remains the design's highest-severity risk (§9 row 1)
   and is the thing to re-examine first if a bad repair ever ships.
2. **Where the rung-3 diagnosis file goes.** Step 15 says "in the approved bugfix
   worktree". `diagnose-and-fix` has no artifact store, so this needs a path
   convention (e.g. `docs/diagnosis/<name>.md`, or an untracked note). Left
   unspecified deliberately; needs one decision.

   **DECIDED — two conventions, one per skill, each reusing what already exists rather than inventing
   an artifact kind.**
   - `diagnose-and-fix` (no artifact store): the written diagnosis is **`DIAGNOSIS.md` at the root of
     the approved bugfix worktree**, and the reproducing test goes in **the repository's normal test
     location** — so it is a real test a human can run, not an orphan note. Delivered wording:
     *"preserve the deterministic reproducing test, if one was produced, in the repository's normal
     test location, and a short written diagnosis as `DIAGNOSIS.md` at that worktree's root"*. Under
     `local only` **both stay uncommitted** in that worktree with their paths reported; they are
     committed on the bugfix branch only when the authorization covers a commit. Never pushed, never
     merged, and no new approval gate.
   - `implement` (has an artifact store): stop evidence goes in the artifact root's **existing**
     reports directory as **`.tasks/<feature>/reports/stop-<logical-id>.md`**, never the root
     checkout. `references/artifact-store.md:69` already lists `reports` among
     `.tasks/<feature>/{SPEC.md,tasks.json,packages,proofs,reports,reviews}`, so this adds no
     directory and no artifact kind.
3. **Add-on 7 (cap 3 → 5).** Only worth doing with evidence of premature halts. Does
   the user have such evidence?

   **NOT ADOPTED.** The cap stays at **3** everywhere. There is no evidence of premature halts, so
   raising the number would have been speculative churn across 38 lines. The diagnosis was also
   wrong-headed: the user's complaint is the **halt**, not the number, and 5 attempts still ends in a
   halt. Exhaustion therefore **escalates** instead (§2.5), under two constraints:
   **(a) authority-preserving** — escalation changes method, never authority; it is allowed only where
   it preserves approved semantics, scope, visible behavior, risk, and manual exceptions, and in
   `diagnose-and-fix` only because the handoff is planning-only with its own downstream approval gate;
   **(b) one escalation per identity** — per cluster identity in `implement`, per confirmed mechanism
   in `diagnose-and-fix`, with no reset by relabeling or reclustering, so termination stays provable
   by counting.
4. **Is `implement`'s empty-handed case actually a problem?** This spec asserts it is
   not, because task artifacts, package branches, proof and report files are already
   durable on stop. If the user has seen `implement` leave nothing usable, that
   assertion is wrong and §2's scope must widen.

   **RESOLVED — the assertion was wrong, and §2's scope widened accordingly.** See the correction in
   §1: the cited `implement:47-48` covers **done** evidence only, and non-convergence can fire at
   readiness before any package agent is dispatched, when no report exists. `implement/SKILL.md` now
   carries a stop-evidence obligation on every Stop-if and exhausted circuit, with the location fixed
   per q2. It is one requirement in the existing Stop-if block — no artifact store was invented and no
   approval gate was added.

## 12. Delivered scope versus the recommended minimum

The delivered change **intentionally exceeds** §2's "minimum viable change". The excess is entirely
accounted for, and each item is either a correction of an error in this spec or a consequence of one:

| # | Beyond the minimum | Why it was unavoidable |
|---|---|---|
| 1 | Explicit three-attempt cap in `diagnose-and-fix` step 12 | §2.2's "no new trigger is needed" was false (blocking error B1); the loop was unbounded, so "deliver on exhaustion" had no exhaustion to fire on |
| 2 | Stop-evidence obligation in `implement/SKILL.md` | open question 4's assertion was false; the empty-handed window is real at readiness |
| 3 | Scope-expansion stop rekeyed in `fix-implementer-contract.md` | §2.1 routes confirmed cross-module/security/concurrency repairs to the localized path, and the worker's old category-based stop would have refused exactly those — a livelock |
| 4 | Right-size clause in `fix-implementer-contract.md` (§2.4) | §2.1 removes the bug path's only over-engineering lens (`design-preflight.md:9`); nothing else replaced it |
| 5 | Escalate once on exhaustion, both skills (§2.5) | the halt itself was the user's complaint; add-on 7 would not have fixed it |
| 6 | Two artifact-path conventions (§11 q2) | open question 2 was left undecided, which meant every agent would invent its own path |

Items 1–4 are corrections; 5–6 are the two decisions that closed the remaining open questions. What
was rejected stayed rejected: no convergence test, no orchestrator/worker split, no preflight section,
no autonomy envelope, no 13th shared reference, no reference-to-reference link, and no change to any
pre-existing cap line.
