# Agentic Delivery Harness North-Star Design

**Status:** Architecture-redesign candidate after challenge; not implementation authority
**Date:** 2026-07-18  
**User-confirmed invariant:** Every planned feature retains a portable artifact sidecar.  
**Existing foundation under reconciliation:** `790bf679466b3738e422b3eb23a951a92a239a6f`

## Purpose

Design `super-developer` as a bounded autonomous delivery harness rather than a chain of skills that repeatedly
hands defects, approvals, and lifecycle ownership to one another.

The intended user experience is:

> The user helps the Conceptualizer establish the feature, authorizes one reviewed and execution-ready proposal,
> and then receives either the independently verified result or one precise escalation that agents cannot
> legitimately resolve within the accepted authority.

This design prioritizes preventing avoidable loops before implementation. Repair classification and circuit
breaking remain last-resort convergence controls, not the primary user experience.

## Delivery Commitment and Honest Limit

The parent owner commits not to hand this amendment off as complete unless observed lifecycle behavior improves
pre-implementation serious-gap interception and clean-path friction while preserving zero escaped seeded serious
defects and improving final deliverable confidence. Fewer calls, prompt-token checks, helper success, or
intention-only documentation cannot establish completion.

The design must shift every reasonably discoverable requirement, architecture, feasibility, dependency, risk,
authority, and verification-seam gap before Implementation Authorization. Foreseeable uncertainty that would
change the plan is resolved through repository evidence, a focused user decision, or a bounded empirical spike;
it is not knowingly deferred until package implementation. This interrupts the cascade in which an incomplete
requirement produces an invalid plan, misleading tests, repeated findings, and repeated repairs.

No credible process can guarantee that every coding defect or runtime interaction is knowable before code exists.
The enforceable promise is prevention plus early containment:

- implementation starts only from requirement-complete, architecture-aware, feasibility-checked, cold-reviewed,
  execution-ready authority;
- implementation owners stabilize actual behavior and affected regression before independent handoff;
- independent roles remain wherever they provide distinct risk information and are removed only when duplicative;
- serious findings are batched by root cause, receive one eligible closure repair per cluster, and never become an
  unchanged retry loop;
- no open serious finding, failing required check, stale/contradicted evidence, unsafe drift, or unresolved final
  verdict is represented as complete.

Before final program handoff, the parent owner must provide evidence that:

1. every governing invariant and core acceptance scenario in this design is implemented; these are non-waivable
   for claims that the agentic-harness amendment is complete;
2. retained Phase 1 behavior has been reconciled rather than layered under contradictory new rules;
3. the fixed baseline corpus shows earlier detection for seeded upstream failures, zero escaped seeded serious
   defects, no stage-detection regression, and bounded false blockers;
4. representative clean low and standard flows use one formal authorization, zero repair waves, and lower
   delegated-call amplification than the exact baseline;
5. seeded implementation, integration, public-contract, test-fidelity, evidence, exact-state, portability, and
   same-cluster failures are detected at their specified stages;
6. all affected repository tests, behavioral fresh-agent scenarios, skill audits, line caps, link/diff checks,
   continuation drills, and bounded cold full-diff review pass;
7. documentation describes behavior actually enforced by prompts and helpers;
8. the worktree is clean and exact reviewed commits are reported; push, merge, and release occur only with their
   separately required authority.

If these conditions cannot be demonstrated, the correct handoff is `blocked` or `needs_decision`, not
`completed`.

## Success Definition

A successful clean path has these properties:

1. The Conceptualizer drives requirements discovery and preserves implementation-shaping decisions.
2. Design and feasibility risks are investigated before planning.
3. The Planner produces a requirement-complete, architecture-aware, verifiable plan and self-challenges it.
4. A cold reviewer challenges the plan before the user authorizes implementation.
5. Technical plan defects are resolved agent-to-agent; only product or protected-authority decisions return to
   the user.
6. The user makes exactly one formal implementation authorization after plan review and readiness checks.
7. One Delivery Owner autonomously coordinates implementation, integration, testing, eligible repairs, evidence,
   review, and audit inside that authorization.
8. Independent assurance is proportionate to named risk and uses non-overlapping roles.
9. The user is not interrupted for routine in-scope defects, tests, reruns, or evidence refresh.
10. Completion and exact reviewed state are durable in the mandatory sidecar and can be continued on another
    system without hidden chat context.

## Terminology

- **Conversational decision:** a focused question during discovery or plan resolution. It is not a formal
  implementation gate.
- **Sidecar Portability Authorization:** explicit task instruction or durable preference permitting only non-force,
  compare-and-swap pushes from the sidecar to the exact namespaced `artifacts/<feature>` ref during discovery and
  planning. It is a protected remote-write permission, not implementation authority.
- **Human Authorization Envelope:** user-owned outcomes, constraints, exclusions, product/interface invariants,
  accepted material risks, protected side effects, and spending/command bounds. Agents cannot change it.
- **Technical Plan Baseline:** the exact reviewed architecture, packages, commands, verification topology, and
  execution details proposed under the Human Authorization Envelope. Agents may version and cold-review a
  technical correction without prompting only while the envelope remains unchanged.
- **Implementation Authorization:** the one formal user gate immediately before product implementation. It accepts
  the Human Authorization Envelope, initial Technical Plan Baseline, exact state, and bounded auto-resolve policy.
- **Authorization Digest:** the immutable canonical digest over the human envelope, initial technical baseline,
  artifact candidate, base code identity/status, dependencies, assurance routing, covered actions, budgets, and
  allowed technical-amendment policy.
- **Effective Authorization Digest:** the Authorization Digest plus the ordered, exact, cold-reviewed technical
  amendment chain. The authorization ID and human envelope remain unchanged; each technical revision changes the
  effective digest and accepted artifact checkpoint.
- **Auto-resolve:** autonomous work within the accepted envelope and actions. It is not blanket permission.
- **Stable Candidate Identity:** immutable package/integrated code, semantic-artifact, runtime-evidence, profile,
  and proof identities produced after stabilization and offered to independent assurance; verifier outputs are not
  part of the candidate.
- **Pre-freeze boundary receipt:** package or boundary-specialist PASS bound to one Stable Candidate Identity and
  consumed-contract digests before dependent unlock. It is an input to the Final Freeze.
- **Final Freeze:** the immutable integrated candidate plus pre-freeze boundary receipts consumed by final
  assurance. Code-review, final-specialist, audit, and Verification Summary receipts are outputs and are excluded.
- **Post-freeze assurance receipt:** an immutable output bound to the Final Freeze and any explicitly preceding
  receipt digests in the acyclic final-assurance graph.
- **Checkpoint transaction:** publish every code object to an immutable retained remote checkpoint ref, verify it,
  then CAS-commit sidecar state that references it. Sidecar state never points to local-only code.
- **Closure cycle:** an initial independent serious rejection (strike 1), one eligible root-cause repair, and one
  affected closure check. Closure failure is strike 2 and opens the circuit. Ordinary coding/test iteration before
  a stable-candidate claim is not a closure cycle.
- **Lifecycle State:** one CAS-updated mechanical sidecar snapshot containing stage, authorization lineage, owner,
  package/wave state, repair budget, cluster strikes, freeze/receipt identities, and next legal actions. It is not
  product authority or an event ledger.
- **Artifact sidecar:** the mandatory portable `artifacts/<feature>` authority containing `.planning/`, `.tasks/`,
  accepted state, subordinate evidence, lifecycle state, and final verification state.

## Governing Invariants

1. **Mandatory sidecar-only planned lifecycle.** Every planned feature uses the namespaced sidecar; current-root
   `.planning`/`.tasks` modes are rejected or migrated before planning. No profile may replace the sidecar with
   chat, a hidden database, or code-branch files.
2. **One formal implementation gate.** Gate 1, Gate 2, and a later Execution Contract must not become separate
   approvals. One Implementation Authorization owns the transition to product code writes.
3. **One lifecycle owner.** After authorization, only the Delivery Owner advances stages or decides repair,
   technical reassessment, escalation, and completion. Children perform bounded work and return.
4. **Human and technical authority are distinct.** Agents may revise and cold-review technical means inside the
   unchanged Human Authorization Envelope. Any product/interface invariant, scope, material risk, protected side
   effect, or explicit user-selected technical constraint change requires the user.
5. **Cold assurance remains independent.** Implementers do not certify their own final result.
6. **Assurance follows named risk.** File count and call targets never lower assurance; profile precedence is
   `high > standard > low` and runtime discovery promotes rather than bypasses.
7. **Behavior precedes evidence claims.** Verification establishes obligations, production paths, and causal
   observations before trusting proofs, reports, matrices, or labels.
8. **No unchanged retry.** Every repeated action requires changed code/evidence, a narrower hypothesis, or decisive
   new information and must fit the authorization-wide budget.
9. **Exact-state binding.** Authorization, stable candidates, review, audit, and completion bind canonical artifact,
   code, runtime-evidence, profile, and receipt identities; subjective “material drift” cannot rebind them.
10. **Portable continuation is core safety.** Phase A/B cannot activate unless a cold system can resume from a
    quiescent CAS checkpoint without chat, reset strikes, duplicate ownership, or infer completion.
11. **Protected actions stay protected.** Target merge/push, force operations, release/tag/delete, unplanned
    credentials/dependencies/services, destructive actions, and unaccepted external effects require explicit
    authority.

## Target Lifecycle

```text
Interactive Conceptualization
        |
        v
Design and Feasibility Preflight
        |
        v
Plan Authoring and Planner Self-Challenge
        |
        v
Cold Plan Challenge
        |
        +-- product/authority question --> User --> focused authority revision
        +-- technical defect -----------> agent-owned revision + affected cold re-review
        |
        v
Execution-Readiness Validation
        |
        v
ONE Implementation Authorization
        |
        v
Exact Freshness Guard + Authorized Activation Check
        |
        v
Autonomous Package Waves and Stabilization
        |
        +-- selected boundary verification before dependent unlock
        |
        v
Risk-Adaptive Final Assurance
        |
        +-- eligible defect --> one repair/cluster within bounded wave + closure check
        +-- envelope change/open circuit/budget stop --> precise user escalation
        |
        v
Append-Only Final Receipt and User Notification
```

## Stage 1 — Interactive Conceptualization

The Conceptualizer owns the interview process. It gathers repository/research evidence before asking the user and
asks one focused, recommendation-bearing question at a time.

It preserves, in sidecar Slices:

- intended outcomes and observable behavior;
- personas, inputs, outputs, defaults, and error behavior;
- constraints, non-goals, rejected alternatives, and accepted tradeoffs;
- interface-bearing and architecture-sensitive decisions;
- edge cases, failure modes, lifecycle behavior, and recovery expectations;
- privacy, security, data, concurrency, compatibility, and operational concerns;
- acceptance and verification expectations;
- explicit deferrals and unresolved blockers.

The Conceptualizer runs a completeness challenge before handoff. It may repair faithful capture without asking,
but must return to the user for ambiguity, contradiction, risk acceptance, scope change, or a decision an agent
cannot own. Planning must not rely on hidden conversation context.

There is no additional ceremonial approval merely to let planning read settled decisions. The later
Implementation Authorization accepts the complete reviewed proposal. If planning or review exposes a missing
product decision, the focused question returns through the Conceptualizer and updates durable authority.

Planned-feature discovery has no current-root artifact mode. The Conceptualizer derives and creates the local
sidecar before its first artifact write. Before the first remote checkpoint, it resolves Sidecar Portability
Authorization from the explicit request or a durable preference; otherwise it asks one focused remote-write
permission. That permission covers only the exact non-force CAS push to `artifacts/<feature>` from the sidecar and
never code, target, tag, release, force, or delete refs. Declining it blocks the portable planning transition rather
than silently falling back to current-root artifacts. The initial checkpoint initializes Lifecycle State, verifies
an absent or expected remote parent, and records the exact remote commit.

## Stage 2 — Design and Feasibility Preflight

Preflight occurs before plan authoring. It determines whether a credible plan can be written without inventing
architecture, prerequisites, or verification.

It inspects or establishes:

- current architecture, ownership, state, routing, and public-interface boundaries;
- product/interface invariants versus agent-owned technical choices;
- generated contracts, persistence/data migration, concurrency, cancellation, replay, and lifecycle concerns;
- dependency, credential, environment, and external-integration feasibility;
- actual production paths and credible test/observation seams;
- bounded command authority, cleanup, shared resources, and broad-regression placement;
- whether empirical uncertainty requires a bounded spike before planning.

Safe repository inspection, read-only probes, and reversible local experiments in a disposable spike worktree
proceed under discovery authority only when they do not modify production branches, manifests/lockfiles, shared
services, credentials, remote state, or external systems. Their exact commands, disposable writes, cleanup, and
observations are checkpointed. A spike requiring a protected action gets one focused discovery-authority decision;
it is not disguised as implementation or inherited into later execution.

Product choices, protected access, material risk acceptance, or an infeasible requirement return to the user.
Plan-changing empirical uncertainty is observed before planning. A required prerequisite exits preflight as
`proven-ready`, `protected-activation-required`, or `blocked`; it cannot disappear into prose.

## Stage 3 — Plan Authoring and Self-Challenge

The Planner converts authoritative Slices and preflight evidence into one coherent sidecar plan. It separates:

- the **Human Authorization Envelope** the user must own; and
- the versioned **Technical Plan Baseline** agents may correct inside that envelope.

The plan must include:

- requirement and acceptance-criterion coverage;
- deliverables, exclusions, product/interface invariants, and agent-owned technical choices;
- projected architecture invariants;
- package boundaries, dependencies, consumed contracts, integration ownership, and logical owners;
- production/test surfaces and implementation-sensitive risks;
- verification seams, focused checks, affected broad checks, and evidence expectations;
- execution prerequisites with durable provenance and activation disposition;
- cleanup, command/write bounds, protected actions, and total autonomous budgets;
- feature assurance profile, per-package `boundary | final` routing, receipt producers, and completion equation;
- the proposed auto-resolve boundary and user-escalation conditions;
- canonical Authorization Digest inputs and allowed deterministic mutations.

Before cold review, the Planner self-challenges requirement coverage, architecture validity, package closure,
consumed-contract exactness, actual-path testability, environment feasibility, assurance routing, completion
receipts, and contradictory or unverifiable claims. A plan that knowingly leaves these unresolved is not
review-ready.

## Stage 4 — Cold Plan Challenge

One cold Plan Reviewer receives files and exact roots, not hidden chat summaries. It challenges completeness,
authority separation, architecture, package/consumed contracts, verification credibility, execution feasibility,
risk selection, exact-state inputs, and auto-resolve safety.

The reviewer returns one batched result:

- **Mechanical or technical plan defect inside the envelope:** Planner revises the Technical Plan Baseline and
  affected cold review runs without prompting the user.
- **Human-envelope change:** ask the user one focused question with a recommendation.
- **Empirical feasibility uncertainty:** run a bounded spike under the Stage-2 rules and revise from observation.
- **Technical architecture invalidation with an envelope-preserving alternative:** return to preflight/planning and
  cold-review the replacement automatically.
- **No credible envelope-preserving design:** return the exact product/risk/constraint decision to the user.
- **Clean:** advance to readiness validation.

The Planner gets one coherent correction pass for a serious review cluster followed by affected re-review. A
second failure of that cluster stops for method/authority reassessment. A changed reviewer, package label, or
technical wording does not mint a new cluster; unrelated findings do not inherit its strike.

No blocking Gate 1 precedes cold review. Review improves the proposal before user authorization.

## Stage 5 — Execution-Readiness Validation

After review defines exact packages, commands, dependencies, and environments—but before authorization—the
orchestrator records source-bound readiness results:

- plan and sidecar structure are mechanically valid;
- exact base code commit and clean-status digest are known;
- required tools and non-protected environments are proven available;
- safe baseline tests and readiness probes have bounded results;
- package dependencies, consumed contracts, and integration order are coherent;
- every required prerequisite is `proven-ready` or `protected-activation-required` with an exact covered activation
  command and failure consequence;
- commands, writes, reruns, cleanup, pushes, budgets, and exclusions are concrete.

A missing required credential/service/tool or other plan-changing prerequisite is `blocked` and prevents
Implementation Authorization. Optional capability may be disclosed and excluded. A protected prerequisite that
can only be tested under authority must be included explicitly in the one authorization and checked immediately
after it, before product writes or package fanout.

## Stage 6 — One Implementation Authorization

The single user gate presents a concise decision surface containing:

- the Human Authorization Envelope: outcomes, exclusions, product/interface invariants, accepted risks, protected
  effects, and budgets;
- the reviewed initial Technical Plan Baseline and its agent-owned correction boundary;
- architecture invariants and named assurance profile/routing;
- exact artifact candidate tree/commit, exact base code commit and clean-status digest, dependency/prerequisite
  state, package/receipt topology, covered actions, and expected deterministic mutations;
- safe readiness results plus each covered protected-activation check;
- precise escalation, repair-wave, delegated-call, command/time, and circuit-open limits;
- the canonical Authorization Digest over all of the above.

Primary choice: **Approve and auto-resolve**. Other choices are **Request changes** and **Abort**. A supervised mode
may remain an explicit preference but does not interrupt the default path.

Approval creates an immutable authorization ID and initial Authorization Digest. The deterministic reviewed-status
and authorization record are checkpointed; the verified exact artifact commit becomes the accepted input. There is
no second Execution Contract approval. A later technical correction records parent/new Technical Plan Baselines,
affected-state invalidation, cold-review receipt, exact checkpoint, and a Technical Amendment Digest. The ordered
chain produces a new Effective Authorization Digest under the same authorization ID only if the Human
Authorization Envelope, covered actions, and amendment policy remain unchanged. An envelope change requires a new
user authorization.

## Stage 7 — Exact Freshness Guard and Authorized Activation

Immediately before product implementation, a deterministic guard checks equality—not subjective materiality:

- authorization ID/digest and accepted artifact tree/commit;
- exact base code commit and clean-status digest;
- dependency/prerequisite snapshot, profile, package routing, and covered actions;
- expected deterministic worktree/status mutations only.

Any unlisted difference invalidates the guard and routes through affected technical review; a new user decision is
required only if the Human Authorization Envelope changes.

Then run covered `protected-activation-required` probes before product writes or package fanout. A successful probe
is checkpointed into Lifecycle State. A failure may be auto-resolved only by an exact covered activation/cleanup
action; otherwise it returns one precise prerequisite escalation. This activation check is not design preflight
and cannot introduce a new unreviewed dependency or architecture choice.

## Stage 8 — Autonomous Package Waves and Stabilization

The Delivery Owner creates/resumes bounded package waves, assigns one logical owner per package or architectural
surface, and retains all lifecycle continuation. It acquires the durable owner token through a compare-and-swap
Lifecycle State update; a second host cannot silently become owner.

Each implementation owner must converge its package before independent handoff:

1. establish accepted obligations, invariants, authorization ID, and consumed-contract digests;
2. implement production behavior and actual execution paths;
3. create or update causal tests and observations;
4. run focused checks and the earliest credible affected broad regression;
5. inspect the full owned diff and integration contract;
6. repair ordinary local defects while evidence is fresh;
7. refresh proof only after behavior stabilizes;
8. commit a clean package candidate and return its exact code commit/tree, base/diff identity, semantic artifact
   and proof/evidence digests, profile/routing, and command results.

That handoff is the package Stable Candidate Identity. Ordinary edit/test/debug iteration before it is bounded by
progress plus authorization command/time limits and is not a closure strike. Unchanged retries and timeout
inflation are forbidden.

A package routed `boundary` receives independent verification immediately after stabilization and before its
output can unlock a dependent package or independently consumed contract. Only a fresh PASS receipt bound to the
candidate and consumed-contract digests unlocks that edge. A package routed `final` may defer independent semantic
verification to final assurance only when it has no independently consumed/material boundary requiring earlier
trust. Helpers and registry/package contracts must encode the routing; they may not require a fabricated report or
silently bypass a selected boundary.

Parallelism is used only for genuinely independent ownership. The Delivery Owner checkpoints Lifecycle State and
finalized package paths at quiescent wave boundaries with path-specific staging and remote-parent CAS; it never
captures another active package through broad staging.

## Stage 9 — Risk-Adaptive Independent Assurance

`standard` is the default. `low` must satisfy every eligibility condition. Any high trigger wins. The accepted
SPEC/package authority owns profile, routing, and specialist placement; mechanical state mirrors controlled values
only for dispatch and validation.

### Acyclic receipt graph

Every receipt has exactly one side of freeze `F`:

```text
Effective Authorization A
        |
        +--> package candidate P[i] --> boundary/package-specialist receipt B[i]
        |                                  |
        +--> integrated code + semantic artifacts + runtime evidence
                                           |
                                           v
                       F = freeze(A, integrated state, evidence, B[*])
                                           |
                    +----------------------+----------------------+
                    |                                             |
             low: combined C(F)                         standard/high: code review R(F)
                    |                                             |
                    |                                  high only: final specialists S[j](F, R)
                    |                                             |
                    |                                  completion audit U(F, R, S[*])
                    |                                             |
                    +----------------------+----------------------+
                                           |
                                  Verification Summary V
```

`B[i]` is a pre-freeze input produced before dependent consumption. A domain specialist assigned to a package or
consumed contract produces `B[i]` and cannot also claim final-state coverage. `R`, final-state `S[j]`, `U`, and `C`
are post-freeze outputs. Final specialists run only after code-review PASS and own a named integrated threat,
privacy, data, concurrency, compatibility, or operational lens not owned by code review or audit. Audit receives
clean prerequisite receipt digests and owns accepted-outcome reconciliation; it does not repeat their lenses.
`V` references the graph but proves nothing independently.

Profile equations are therefore:

| Profile | Pre-freeze equation | Post-freeze equation |
|---|---|---|
| Low | One coherent `final` package proof; no boundary/sensitive/shared/public/lifecycle trigger | `F → C(code-risk PASS, completion PASS) → V` |
| Standard | PASS `B[i]` for every `boundary` package; coherent leaf packages may use `final` | `F → R(PASS) → U(PASS, R) → V` |
| High | Enhanced PASS `B[i]` for every material package/consumed boundary and each package-bound specialist | `F → R(PASS) → S[*](PASS, F, R) → U(PASS, F, R, S[*]) → V` |

Receipt ownership is non-overlapping:

- **Package verifier or package-bound specialist:** package-local behavior/tests/evidence and named consumed
  contract/risk; emits pre-freeze `B[i]`.
- **Code reviewer:** integrated implementation/test risk, merge behavior, cross-package contracts, regressions, and
  direct semantic coverage for packages routed `final`; emits `R`.
- **Final-state specialist:** one named integrated risk absent from package and generic code-review ownership;
  emits `S[j]` only after `R` PASS.
- **Completion auditor:** read-only Human Authorization Envelope and accepted-plan reconciliation over `F` and
  prerequisite receipts; emits `U`.
- **Combined low verifier:** explicit code-risk and completion verdicts in `C`.
- **Delivery Owner:** classification, repair, checkpointing, and lifecycle transitions; emits no semantic verdict.

A serious failure at `R`, `S[j]`, `U`, or `C` routes through Stage 10. Any repair changes integrated semantic input,
so it creates a new `F`; every downstream receipt from the old freeze is invalid. Pre-freeze `B[i]` is retained only
when exact affected-state analysis proves its package/contract inputs unchanged. Standard/high audit is never
started before all preceding receipts PASS.

Runtime discovery that raises profile, package routing, or specialist placement invalidates affected candidates
and the current graph. The Delivery Owner records promotion, updates/reviews the Technical Plan Baseline, and
advances the Effective Authorization Digest/checkpoint. It proceeds without user input only when envelope, covered
actions, budgets, and protected effects stay inside authorization. A low verifier discovering a higher trigger
returns `PROFILE_INVALID`, not PASS or repair. Downgrade requires a new reviewed baseline and user authorization.

Helpers must validate the graph topologically: profile/routing, required `B[i]`, exact `F`, allowed incoming receipt
digests, receipt role, and final equation. They reject a receipt on both sides of `F`, a missing required boundary,
a substitute report for `final`, or a summary used as semantic proof.

## Stage 10 — Finding and Repair Convergence

Independent verifiers return all serious findings in one batch with accepted requirement/invariant, root
mechanism, architectural surface, observed verification signatures, severity, class, and boundedness. They do not
repair or invoke another stage.

Canonical cluster identity is the accepted requirement/invariant plus root mechanism and architectural surface.
Verification signatures, agents, commits, package labels, and prompts are observations and cannot mint a new
cluster. Lifecycle State persists lineage and strikes across hosts and successors. Mixed findings use precedence:
human-envelope gap, technical architecture invalidation, implementation/integration defect, test/evidence defect,
then confidence enhancement.

A human-envelope gap returns directly to the user. Technical architecture invalidation exits code repair and gets
one bounded Stage-2-to-4 technical redesign/review when an envelope-preserving alternative is credible; recurrence
of the mechanism or no credible alternative returns to the user. Only implementation, integration, and
test-fidelity clusters enter the closure-repair state machine; stale evidence is refreshed only after its bound
behavior is stable.

The deterministic eligible-cluster state machine is:

1. initial serious independent rejection records strike 1 and authorizes one eligible root-cause repair;
2. the logical implementation owner makes that one repair and runs actual-path targeted plus affected broad checks
   before refreshing evidence;
3. the original verifier session, or an exact successor, performs one affected closure check;
4. PASS closes the cluster; FAIL records strike 2 and opens the circuit immediately.

A repair wave batches all currently known eligible clusters. The Implementation Authorization sets total
post-handoff repair-wave, delegated-call, command, and elapsed-time budgets: default maximum one wave for low, two
for standard, and an explicitly justified finite value for high. An unrelated new cluster may consume another
wave only if budget remains; budget exhaustion produces one batched escalation. No new agent, commit, timeout, or
renamed finding resets cluster or lifecycle-wide limits.

## User Interruption Contract

After Implementation Authorization, the user is interrupted only when at least one of these is true:

1. the Human Authorization Envelope is missing, contradictory, or must change;
2. bounded technical replanning cannot produce a credible envelope-preserving design;
3. scope, material risk, protected effects, cost, or authorization-wide budgets must expand;
4. a new dependency, service, credential, permission, destructive action, or external effect is required outside
   authorization;
5. security/privacy/safety/data-loss risk needs acceptance;
6. no credible verification seam can be established;
7. exact accepted state or exclusive ownership cannot be recovered safely;
8. a serious cluster opens its circuit or the total repair/command/time budget is exhausted.

An escalation first CAS-checkpoints quiescent state and presents the blocker, evidence, prior bounded attempts,
affected envelope/technical surfaces, recommendation, and alternatives. It never asks a vague “what next?” when a
concrete decision can be formulated.

Routine compilation/test failures, local implementation iteration, technical plan correction inside the unchanged
envelope, implementation/integration/test-fidelity repair, bounded reruns, profile promotion inside covered
budgets, evidence refresh, and listed non-force sidecar/feature pushes do not re-prompt.

## Mandatory Portable Sidecar and Checkpoint Protocol

All planned-feature stages validate a sidecar root/ref distinct from the code root. Existing current-root
`.planning`/`.tasks` artifacts are legacy input only: they must be path-safely imported into a namespaced sidecar,
checkpointed with provenance, and revalidated before planning. Planned Conceptualize, planning, review,
implementation, pipeline review, audit, helpers, and tests must reject current-root authority rather than silently
preserving two modes.

The sidecar remote ref and every code checkpoint ref are retained by default. Release or cleanup may delete them
only through a separate explicit retention decision after final evidence is preserved.

Product/completion authority remains small:

1. **Human Authorization Envelope and versioned Technical Plan:** Slices plus accepted SPEC/package authority,
   authorization ID/effective digest, exact baseline, and reviewed technical revisions.
2. **Verification Summary:** append-only `V` naming `F`, the required receipt DAG, deviations, limitations, and
   verdict.

One canonical Lifecycle State snapshot is initialized with the sidecar and is mechanical continuation state, not
a third product authority or event log. It contains:

- schema/generation, feature, quiescence, stage, and next legal actions;
- authorization ID/effective digest and exact artifact/code checkpoint refs and SHAs;
- assurance graph, package/wave dispositions, active owner token, and takeover state;
- canonical cluster lineage/strikes and latest freeze/receipt identities;
- authorization-wide maxima plus monotonically issued/used repair waves, delegated calls by role, command units,
  cost units when applicable, `started_at`, and absolute `deadline_at`;
- bounded active reservations for the next wave/call. Issued budget never decreases; a crash cannot reclaim it or
  reset the deadline. Uncertain clock/budget state fails closed.

### Two-phase recoverable checkpoint

Before dispatch, the Delivery Owner reserves the wave/call/command allocation through a sidecar CAS checkpoint.
Each reservation has a unique generation; abandoned work remains charged. Package agents write only assigned paths
and report actual usage for observation, never authority expansion.

At a quiescent package/integration checkpoint:

1. verify the active owner, generation, remote parents, budgets, and finalized path set;
2. commit clean code and allocate an immutable unique ref such as
   `refs/heads/checkpoints/<feature>/<slot>/g<generation>`;
3. non-force push that code ref, fetch/verify its exact SHA is remotely reachable, and retain it;
4. update Lifecycle State and finalized sidecar paths to reference only verified remote code refs/SHAs;
5. path-stage and commit the sidecar from the expected parent, then non-force CAS-push only
   `artifacts/<feature>` and verify the remote commit.

A crash after step 3 leaves an unreferenced code checkpoint that resume ignores and later cleanup may collect. A
crash after step 5 is recoverable because all referenced code objects already exist remotely. The sidecar may never
reference a local-only commit. Broad `git add -A`, force push, mutable checkpoint refs, and sidecar-first publication
are forbidden.

Initial discovery uses the same CAS rule without code refs under Sidecar Portability Authorization. Implementation
Authorization separately covers creation of the exact namespaced code checkpoint refs used during autonomous
work. A remote without safe non-force namespaced refs cannot claim portable planned-feature execution.

Ownership takeover requires evidence the prior owner stopped plus a CAS generation change; elapsed lease time
alone cannot reset ownership, budgets, or strikes. Cold resume fetches and verifies every referenced ref/SHA, begins
from the last quiescent state, treats later local commits/evidence as untrusted recovery input, and never infers
`done`. Minimal resume, exclusive ownership, monotonic budgets, two-phase publication, remote retention, and
fail-closed recovery are Phase A/B prerequisites.

Registry data, Lifecycle State, proofs, reports, command outputs, and receipts remain subordinate; none may
redefine accepted behavior or completion.

## Completion and Notification

After implementation stabilizes and all pre-freeze package/runtime evidence is final, the Delivery Owner creates
immutable `F` containing authorization ID/effective digest, exact remotely reachable clean integrated code
commit/tree and base/diff, canonical semantic-artifact path manifest/tree, runtime-evidence digests,
profile/routing, pre-freeze `B[*]`, cluster state, and command results. The manifest includes accepted
plan/proof/boundary-report inputs and excludes Lifecycle State plus post-freeze `C/R/S/U/V` paths.

Post-freeze receipts are append-only outputs bound according to the Stage-9 DAG. Any production, test,
accepted-plan, proof, boundary report, runtime evidence, profile, or routing change creates a new `F` and
invalidates its downstream receipts. Receipt-file/Lifecycle-State commits do not rebind semantic inputs.

A deterministic final validator checks one authorization lineage, remotely reachable `F`, acyclic profile equation,
allowed receipt predecessors/digests, closed clusters, monotonic budgets/deadline, and no drift. It accepts only:

- **low:** `F → C(two PASS verdicts) → V`;
- **standard:** `F → R(PASS) → U(PASS) → V`;
- **high:** `F → R(PASS) → S[*](PASS) → U(PASS) → V`.

`V` references verified outputs and is CAS-checkpointed as the append-only final receipt. Completion notification
occurs only after that checkpoint; `V` cannot make a failed or missing predecessor pass.

The user receives delivered outcomes, important decisions, assurance results, deviations/limitations, exact
feature/artifact refs, and any separately authorized next action. Internal transcripts and duplicate gate prose are
omitted. Target merge/push, force operations, release/tagging, branch deletion, and deployment remain separately
authorized.

## How the Design Prevents Loops

| Loop source | Preventive control |
|---|---|
| Missing requirements discovered during implementation | Conceptualizer completeness challenge plus reviewer authority-gap check |
| Architecture discovered after packages are written | Pre-planning feasibility and envelope/technical-invariant separation |
| Unimplementable verification plan | Preflight establishes actual paths; Planner binds causal checks, routing, receipts, and broad placement |
| Reviewer receives an obviously red implementation | Exact stable-candidate contract and full owner self-review before handoff |
| Dependents build on an untrusted package | Selected boundary PASS precedes dependency unlock |
| Many verifiers repeat the same work | Profile completion equations and non-overlapping receipt ownership |
| Review and audit are both invalidated by one repair | Standard/high code review reaches closure before audit starts |
| Findings arrive one at a time | Each cold reviewer returns one batched result |
| Repair agents repeatedly rediscover context | Logical owner plus CAS lifecycle/cluster handback |
| Evidence is refreshed before behavior is fixed | Behavior-first repair and regression ordering |
| Same mechanism is renamed for another attempt | Canonical cluster lineage excludes agent/signature/commit identity |
| Many unrelated repairs continue indefinitely | Authorization-wide repair-wave/call/command/time budget |
| User repeatedly approves technical correction | Human envelope remains fixed while technical revisions are cold-reviewed agent-to-agent |
| A crash resets progress or strikes | Quiescent CAS checkpoint and fail-closed cold resume |
| Agents continue after protected authority is needed | Explicit interruption contract and fail-closed states |

## Quality Demonstration Protocol

The behavioral baseline is plugin v1.39.0 at `df7396f677c026cd8bfdf2d0e9baca29e5a03791`; Phase 1 at `790bf67` is a
safety reference, not a substitute baseline. Before source amendment, freeze reproducible low and standard clean
fixtures plus seeded failure fixtures derived from field evidence and the core scenarios below. Each fixture names
initial git/artifact state, user inputs, allowed commands, seed, expected detection stage/class, expected user
prompts, and terminal verdict.

Run baseline and candidate with fresh agent contexts and fixed packets. Record delegated calls by role, formal user
prompts, technical questions, repair waves, closure checks, stage of first correct detection, false blockers,
terminal result, and exact commits. Static prompt-token assertions and helper fixtures support contract coverage but
do not count as behavioral evidence.

Candidate acceptance requires:

- 100% of seeded serious faults detected with the specified class and no later than the scenario oracle;
- 100% of requirement, architecture, feasibility, plan-changing prerequisite, and verification-seam seeds
  intercepted before Implementation Authorization; protected-activation failures that cannot be observed safely
  beforehand are intercepted before product writes or package fanout;
- at least the known v1.39 late-discovery seeds moved to an earlier stage, with no serious seed detected later than
  baseline and zero escaped serious seeds;
- zero serious false blockers on clean fixtures and fewer than 10% false blockers across the bounded corpus;
- exactly one formal implementation authorization and zero post-handoff repair waves on clean fixtures;
- at most one repair per canonical cluster, deterministic circuit-open on failed closure, and no unchanged retry;
- a clean low path of Planner, Plan Reviewer, Implementer, and combined verifier after discovery; standard/high
  calls may exceed that only for named boundaries/risks and must match their planned topology;
- cold cross-system continuation from every quiescent stage fixture without hidden chat, duplicate owner, lost
  strike, partial-evidence capture, or inferred completion.

Call reduction fails acceptance if any quality or stage oracle regresses. Core invariants and scenarios cannot be
waived to satisfy the metrics.

## Phase 1 Reconciliation

The current Phase 1 checkpoint is not the completed user journey. It is a provisional safety foundation whose
exact contracts must be reconciled, not merely supplemented.

### Retain in principle

- one post-authorization Delivery Owner and return-only children;
- exact-state and focused-amendment intent;
- architecture-invariant projection;
- finding classification and logical owner continuity;
- behavior-before-evidence verification;
- affected broad regression before proof/report refresh;
- same-cluster stopping, after correcting identity and strike semantics.

### Required amendments

- `review-plan`: remove blocking Gate 1 and make reviewed candidate plus authorization envelope the sole user gate;
- `implement` Execution Contract: become the content of that gate, not a second approval; remove routine repair
  re-prompts in auto-resolve;
- planning/preflight/spike contracts: separate safe disposable discovery from protected action and block unresolved
  plan-changing prerequisites;
- convergence contract: separate human envelope from technical-plan revisions; persist cluster identity/strikes and
  define initial rejection → one repair → one closure → circuit;
- package lifecycle, work packages, artifact schemas, and `sliceproof.py`: encode profile/package routing, run
  selected boundary verification before dependency unlock, and validate profile-specific completion without fake
  universal reports;
- final lifecycle: replace sibling review/audit with combined low or serial standard/high receipts bound to one
  immutable freeze;
- artifact-store/Slice/tool/helper contracts: retire current-root planned-feature authority, add safe legacy import,
  and fence initial namespaced CAS publication under Sidecar Portability Authorization;
- sidecar/worktree/release contracts: add monotonic-budget Lifecycle State, immutable remote code checkpoint refs,
  code-before-sidecar two-phase publication, path-specific quiescent CAS, cold resume, exclusive takeover, acyclic
  final receipts, and remote ref retention by default;
- tests: add behavioral baseline fixtures, stage oracles, drift/promotion/dependency/receipt/continuation cases, and
  retain prompt/helper tests only as supporting evidence.

### Remove or reject

- child-owned lifecycle continuation or recursive repair;
- Gate 1, a second execution approval, or routine in-boundary reapproval;
- universal package reports where routing selects final coverage;
- sibling final review/audit against a state likely to change or a specialist receipt used on both sides of `F`;
- cluster or budget identity that resets through a new signature, agent, host, package label, or commit;
- current-root planned authority, broad concurrent sidecar staging, sidecar-first publication, local-only referenced
  code, release-default ref deletion, hidden-chat continuation, or floating state;
- assurance justified only by file/call count or semantic proof inferred from helper/prose/matrices.

## Recommended Delivery Phases

### Phase A — Pre-implementation correctness, exact authorization, and minimum portability

Strengthen Conceptualize completeness; enforce sidecar-only planned authority and initial portability permission;
move feasibility before planning; add Planner self-challenge; make cold review precede approval; prove prerequisites;
consolidate one Authorization Digest gate; and establish monotonic-budget Lifecycle State, immutable remote code
checkpoint refs, two-phase code-before-sidecar CAS, exclusive owner, and cold resume. Phase A is not releasable
without publication/crash continuation drills.

### Phase B — Autonomous delivery, adaptive assurance, and authoritative completion

Add exact stable candidates, consumed-boundary unlock, the acyclic `B → F → C/R/S/U → V` receipt graph,
profile-specific helper equations, combined low or serial standard/high final assurance, deterministic repair
waves/circuits, Verification Summary, and final notification. Integrate retained Phase 1 primitives only after
conflicts are replaced. Phase B is not releasable without the fixed corpus and receipt-DAG validation.

### Phase C — Extended lifecycle and release durability

Add richer park/cancel/supersede UX, crash recovery beyond quiescent checkpoints, retention policy controls,
evidence compaction, release/cleanup continuity, and supported degraded-host operations. Core exact identity,
resume, CAS checkpointing, remote retention, and final summary are not deferred to Phase C.

The existing Phase 1 branch remains remotely preserved but must not merge or release as the completed amendment
until reconciliation and Phase A/B acceptance are complete.

## Core Acceptance Scenarios

These are non-waivable. Each implemented fixture must declare exact initial state, seed, expected first-detection
stage/class, permitted calls/prompts, and terminal verdict.

| # | Given / seed | Required result |
|---|---|---|
| 1 | Clean low feature with one coherent package | One formal authorization, four expected delegated roles after discovery, zero repair waves, combined two-verdict PASS, final receipt |
| 2 | Clean standard feature with a meaningful boundary | Selected boundary PASS before consumption, code-review PASS before audit dispatch, zero repair waves |
| 3 | Technical plan defect inside unchanged envelope | One batched reviewer result, agent-owned revision and affected cold re-review, no user prompt |
| 4 | Missing product/interface decision | One focused user question updates the envelope before authorization |
| 5 | Omitted architecture/public-contract/verification seam | Preflight or plan challenge blocks before authorization with the correct class |
| 6 | Required tool/service/credential unavailable | Readiness is `blocked`; no authorization or fanout; covered protected activation is checked immediately after approval |
| 7 | Ordinary local implementation defect before handoff | Logical owner stabilizes it within progress budget; no closure strike or user prompt |
| 8 | Package output consumed by a dependent | Exact boundary receipt and contract digests PASS before dependent unlock |
| 9 | Standard code-review defect | One batched repair wave and affected closure PASS; audit runs once on the new freeze |
| 10 | Runtime low-to-high trigger | Candidate/profile invalidated, technical baseline promoted/reviewed, Effective Authorization Digest and checkpoint advance, required high topology runs; user asked only if envelope/budget changes |
| 11 | Technical architecture invalidation with envelope-preserving alternative | Automatic return to preflight/planning and cold review; no code repair and no user prompt |
| 12 | Architecture/product invariant cannot be preserved | CAS checkpoint plus one precise user decision; no automatic technical mutation |
| 13 | Same serious mechanism fails after its one repair | Initial rejection is strike 1; failed closure is strike 2 and circuit opens across agent/commit/signature changes |
| 14 | Any unlisted artifact/code/dependency/profile drift | Exact freshness/freeze validator rejects; no subjective rebind |
| 15 | Host stops before/after each code/sidecar publication step | Referenced code is already remote, orphan code refs are ignored, cold resume preserves owner/stage/issued budgets/deadline/strikes/next action, and completion is never inferred |
| 16 | Low/standard/high final receipt graphs | Validator accepts only the declared acyclic predecessor order and rejects circular, cross-freeze, missing, duplicate-role, or summary-as-proof receipts |
| 17 | Existing current-root artifacts or first remote sidecar push | Planned lifecycle requires safe migration to sidecar; exact namespaced initial CAS push has explicit portability authority; no silent current-root fallback |
| 18 | Target merge/release or unplanned protected action | Completion notifies once; protected operation cannot inherit sidecar portability or implementation auto-resolve authority |

## Challenger Acceptance Standard

Approve only if the lifecycle and non-waivable scenarios are achievable without:

- a second formal implementation approval or hidden protected-action gate;
- user involvement for envelope-preserving technical correction or routine repair;
- unresolved plan-changing prerequisites at authorization;
- subjective/floating state, circular receipt edges, local-only referenced code, or unsafe dependency unlock;
- unbounded planner/reviewer, implementation, repair-wave, or verifier loops;
- duplicate assurance ownership or a specialist on both sides of the freeze;
- resetting profile, cluster, monotonic budget/deadline, or ownership across hosts/agents/commits;
- current-root planned authority, unauthorized initial sidecar publication, or deferred Phase-A/B portability;
- claiming quality from call reduction, token checks, helpers, or prose without the fixed behavioral corpus.
