# Agentic Delivery Harness North-Star Design

**Status:** Candidate for independent challenge; not implementation authority  
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

The parent owner commits not to hand this amendment off as complete unless the delivered workflow demonstrably
improves clean-path friction and preserves or improves serious-defect detection and final deliverable quality.
Partial contracts, passing prompt-token tests, helper success, or documentation claims are not completion.

The design must shift every reasonably discoverable requirement, architecture, feasibility, dependency, risk,
authority, and verification-seam gap before Implementation Authorization. Foreseeable uncertainty that would
change the plan is resolved through repository evidence, a focused user decision, or a bounded empirical spike;
it is not knowingly deferred until package implementation. This addresses the cascading failure mode in which an
incomplete requirement produces an invalid plan, misleading tests, repeated findings, and repeated repairs.

No credible process can guarantee that every coding defect or runtime interaction is knowable before code exists.
The enforceable promise is therefore prevention plus early containment:

- implementation starts only from requirement-complete, architecture-aware, feasibility-checked, cold-reviewed,
  execution-ready authority;
- implementation owners stabilize actual behavior and affected regression before independent handoff;
- independent roles remain wherever they provide distinct risk information and are removed only when duplicative;
- serious findings are batched by root cause, receive at most one eligible closure repair per cluster, and never
  become an unchanged retry loop;
- no open serious finding, failing required check, stale/contradicted evidence, unsafe drift, or unresolved audit
  issue is represented as complete.

Before final handoff, the parent owner must provide evidence that:

1. every accepted lifecycle requirement and scenario in this design is implemented or explicitly approved out of
   scope;
2. retained Phase 1 behavior has been reconciled rather than accidentally layered under contradictory new rules;
3. clean-path gate and delegated-call amplification is lower than the baseline for representative low and
   standard flows;
4. seeded requirement, architecture, implementation, integration, public-contract, test-fidelity, evidence,
   exact-state, and same-cluster failures are still detected at the correct stage;
5. no seeded serious-defect detection regression is accepted merely to reduce calls;
6. all affected repository tests, skill audits, line caps, link/diff checks, and bounded cold full-diff review pass;
7. documentation describes the behavior actually enforced by prompts/helpers rather than the intended behavior;
8. the worktree is clean and the exact reviewed commits are reported; push, merge, and release occur only with
   their separately required authority.

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

- **Conversational decision:** a focused question during discovery or plan resolution. It is not a formal lifecycle
  gate.
- **Implementation Authorization:** the one formal user gate immediately before implementation. It combines exact
  plan acceptance with bounded auto-resolve authority.
- **Auto-resolve:** autonomous work within explicitly accepted product, write, command, risk, and side-effect
  boundaries. It is not blanket permission.
- **Stable candidate:** an implementation state whose owner has completed planned actual-path checks, affected
  regression, self-review, and evidence updates and is ready for independent verification.
- **Closure cycle:** an independent serious finding, one eligible repair of its coherent root cause, and the
  affected verification used to establish closure. Ordinary coding/test iteration before a readiness claim is not
  a closure cycle.
- **Artifact sidecar:** the mandatory portable `artifacts/<feature>` authority containing `.planning/`, `.tasks/`,
  accepted state, subordinate evidence, and final verification state.

## Governing Invariants

1. **Mandatory sidecar.** No planned-feature profile may replace the sidecar with chat, a hidden database, or only
   code-branch files.
2. **One formal implementation gate.** Gate 1, Gate 2, and a later Execution Contract must not become separate
   approvals. One Implementation Authorization owns the transition to code writes.
3. **One lifecycle owner.** After authorization, only the Delivery Owner advances stages or decides repair,
   reassessment, escalation, and completion. Children perform bounded work and return.
4. **Product authority remains human.** Agents may repair mechanics and implementation, but may not invent product
   behavior, accept material risk, narrow scope, or override accepted design.
5. **Cold assurance remains independent.** Implementers do not certify their own final result.
6. **Assurance follows named risk.** File count and agent-call targets never lower assurance.
7. **Behavior precedes evidence claims.** Verification establishes obligations, production paths, and causal
   observations before trusting proofs, reports, matrices, or labels.
8. **No unchanged retry.** Every repeated action must be justified by changed code/evidence, a narrower hypothesis,
   or decisive new information.
9. **Exact-state binding.** Authorization, review, audit, and completion bind safe artifact and code identities.
10. **Protected actions stay protected.** Target merge/push, force operations, release/tag/delete, unplanned
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
        +-- product/authority question --> User --> focused plan revision
        |
        v
Execution-Readiness Validation
        |
        v
ONE Implementation Authorization
        |
        v
Mechanical Freshness Guard
        |
        v
Autonomous Implementation and Stabilization
        |
        v
Risk-Adaptive Independent Assurance
        |
        +-- eligible defect --> one bounded repair + affected closure check
        +-- design/authority/open circuit --> precise user escalation
        |
        v
Durable Verification Summary and User Notification
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

## Stage 2 — Design and Feasibility Preflight

Preflight occurs before plan authoring, not after implementation begins. It determines whether a credible plan can
be written without inventing architecture or verification.

It inspects or establishes:

- current architecture, ownership, state, routing, and public-interface boundaries;
- accepted architecture invariants and existing repository conventions;
- generated contracts, persistence/data migration, concurrency, cancellation, replay, and lifecycle concerns;
- dependency, credential, environment, and external-integration feasibility;
- actual production paths and credible test/observation seams;
- bounded command authority, cleanup, shared resources, and broad-regression placement;
- whether empirical uncertainty requires a bounded spike before planning.

Safe repository inspection and bounded read-only probes proceed autonomously. Product choices, protected access,
material risk acceptance, or an infeasible requirement return to the user. Unresolved empirical uncertainty is
observed through a bounded spike and fed back into planning; it is not deferred casually to implementation.

## Stage 3 — Plan Authoring and Self-Challenge

The Planner converts all safe authoritative Slices and preflight evidence into one coherent sidecar plan. The plan
must include:

- requirement and acceptance-criterion coverage;
- deliverables, exclusions, and exact interface obligations;
- projected architecture invariants;
- package boundaries, dependencies, integration contracts, and logical owners;
- production/test surfaces and implementation-sensitive risks;
- verification seams, focused checks, affected broad checks, and evidence expectations;
- execution prerequisites, cleanup, command/write bounds, and protected actions;
- feature assurance selection and package/final assurance topology;
- the proposed auto-resolve boundary and user-escalation conditions.

Before cold review, the Planner self-challenges requirement coverage, architecture validity, package closure,
integration ownership, actual-path testability, environment feasibility, and contradictory or unverifiable claims.
A plan that knowingly leaves these unresolved is not review-ready.

## Stage 4 — Cold Plan Challenge

One cold Plan Reviewer receives files and exact roots, not hidden chat summaries. It challenges completeness,
architecture, package/integration contracts, verification credibility, execution feasibility, risk selection, and
auto-resolve safety.

The reviewer returns one batched result:

- **Mechanical or technical plan defect:** Planner repairs it autonomously.
- **Missing product decision or risk acceptance:** ask the user one focused question with a recommendation.
- **Empirical feasibility uncertainty:** run a bounded spike and revise from observed evidence.
- **Architecture invalidation:** return to design/preflight rather than polishing package prose.
- **Clean:** advance to readiness validation.

The Planner gets one coherent correction pass for a serious review cluster followed by affected re-review. A
second failure of the same cluster means the design method or authority is inadequate; stop for reassessment rather
than starting a planner/reviewer loop. Unrelated findings do not inherit that strike.

No blocking Gate 1 precedes cold review. Safe review should improve the proposal before asking the user to approve
implementation.

## Stage 5 — Execution-Readiness Validation

After review defines exact packages, commands, dependencies, and environments—but before user authorization—the
orchestrator validates all safe readiness facts that can reasonably be checked:

- plan and sidecar structure are mechanically valid;
- baseline repository state and intended refs are known;
- required tools and already-authorized environments are available;
- bounded readiness probes and baseline tests are credible;
- package dependencies and integration order are coherent;
- required credentials/services/external access are available or explicitly identified;
- commands, writes, reruns, cleanup, pushes, and exclusions are concrete.

This is not implementation and does not perform protected installs, service starts, credentialed operations, or
external side effects without authority. Anything that cannot be checked safely is disclosed in the authorization
with its consequence and trigger.

## Stage 6 — One Implementation Authorization

The single user gate presents a concise decision surface containing:

- accepted outcomes, exclusions, and unresolved approved deferrals;
- reviewed implementation/package plan;
- architecture invariants and named risk profile;
- verification, review, audit, and specialist topology;
- exact artifact candidate and the deterministic reviewed-status/checkpoint mutation;
- covered code/test/docs writes, commands, bounded reruns, evidence refresh, worktrees, and listed pushes;
- dependency/environment assumptions and readiness results;
- protected actions that remain excluded;
- precise escalation and circuit-open conditions.

Primary choice: **Approve and auto-resolve**. Other choices are **Request changes** and **Abort**. A supervised mode
may remain an explicit user/project preference, but it does not shape or interrupt the default autonomous path.

Approval authorizes the declared implementation boundary and deterministic artifact checkpoint. The checkpoint is
verified and its exact commit becomes the accepted input. There is no second Execution Contract approval after
this gate.

## Stage 7 — Mechanical Freshness Guard

Immediately before the first implementation write, perform a cheap deterministic guard—not another agent phase:

- accepted artifact checkpoint matches authorization;
- code base/ref and planned worktree roots have not drifted materially;
- worktrees are safe and package assignments remain coherent;
- authorization still covers the first planned actions.

Expected worktree creation or deterministic status/checkpoint mutations are not semantic drift. Unexpected
artifact change invalidates authorization. Material code-base drift returns through affected planning/review and,
when it changes the accepted proposal or risk, a new authorization. The guard performs no design discovery that
should have happened during preflight.

## Stage 8 — Autonomous Implementation and Stabilization

The Delivery Owner creates/resumes bounded package waves, assigns one logical owner per package or architectural
surface, and retains all lifecycle continuation.

Each implementation owner must converge its package before independent handoff:

1. establish the relevant accepted obligations and invariants;
2. implement production behavior and actual execution paths;
3. create or update causal tests and observations;
4. run focused checks and the earliest credible affected broad regression;
5. inspect the full owned diff and integration contract;
6. repair ordinary local defects while evidence is fresh;
7. refresh proof only after behavior stabilizes;
8. return one stable-candidate handoff or one precise blocker.

Ordinary edit/test/debug iteration within this stage is expected and bounded by progress, command safety, and the
Execution Authorization. It does not count as independent closure failure. Agents must not prematurely hand off a
known-red candidate merely to let another role rediscover it.

Parallelism is used only for genuinely independent ownership. Dependent or shared-state work proceeds in waves so
that integration defects are not manufactured by the orchestration topology.

## Stage 9 — Risk-Adaptive Independent Assurance

`standard` is the default when risk is uncertain. `low` must be explicit and justified. Triggered sensitive risk
promotes assurance automatically when covered by authorization; assurance is never silently downgraded.

| Profile | Eligibility | Package boundary | Final assurance |
|---|---|---|---|
| Low | One coherent boundary, established patterns, deterministic actual-path checks, no sensitive/shared/public/lifecycle trigger | No dedicated verifier unless discovery promotes risk | One cold verifier returns separate code-risk and completion verdicts |
| Standard | Normal multi-surface work or any meaningful uncertainty | Dedicated verification only for independently meaningful, parallel, consumed, or material package boundaries | Cold code review reaches closure, then a different read-only completion audit |
| High | Security/privacy/safety/credentials, persistent data/migration, public/generated/external contracts, concurrency/shared state/replay/cancellation/lifecycle, destructive/external effects, cross-package invariants, or weak verification seam | Enhanced independent verification at every material boundary plus named specialists | Cold code review reaches closure, then a different read-only audit against the stable exact state |

Roles do not repeat one another:

- **Package verifier:** package-owned obligations, behavior, test fidelity, and evidence at a meaningful boundary.
- **Code reviewer:** integrated implementation, tests, interfaces, regressions, and code-risk findings.
- **Completion auditor:** read-only reconciliation of accepted outcomes against the exact reviewed state; it
  selectively falsifies high-value claims but does not restart wholesale code review.
- **Combined low-risk verifier:** applies both lenses explicitly in one cold pass and returns two verdicts.
- **Delivery Owner:** classifies findings, delegates repairs, refreshes state, and advances or stops.

For standard/high assurance, code review and audit are serial. Audit starts only after code-review findings are
closed and evidence is refreshed, avoiding a repair that invalidates a concurrently running audit. Triggered
specialists provide a distinct expertise or threat lens; they are not added merely to increase agent count.

## Stage 10 — Finding and Repair Convergence

Independent verifiers return all serious findings in one batch with root cause/invariant, affected surfaces,
verification signature, severity, and boundedness. They do not repair or invoke another lifecycle stage.

The Delivery Owner classifies each cluster:

- requirement gap;
- architecture invalidation;
- implementation defect;
- integration regression;
- test-fidelity gap;
- stale or contradicted evidence;
- confidence enhancement.

Requirement gaps and architecture invalidations do not enter automatic repair. Eligible implementation,
integration, and test-fidelity findings are grouped by coherent root cause and receive one bounded repair from the
logical implementation owner. After repair, run actual-path targeted checks and the affected broad regression
before refreshing evidence.

The original verifier session should perform the focused closure check when feasible; otherwise a successor gets
an exact handback. Closure checks inspect affected surfaces, widening only for material, shared, sensitive, or
uncertain impact. A second failed closure for the same serious mechanism opens the circuit. New agents, prompts,
commits, timeouts, or renamed findings do not reset it.

## User Interruption Contract

After Implementation Authorization, the user is interrupted only when at least one of these is true:

1. accepted product behavior is missing, contradictory, or must change;
2. accepted architecture cannot satisfy an invariant;
3. scope or named risk materially expands;
4. a new dependency, service, credential, permission, destructive action, or external side effect is required
   outside authorization;
5. security/privacy/safety/data-loss risk needs acceptance;
6. no credible verification seam can be established;
7. exact accepted state cannot be recovered safely;
8. the same serious cluster fails its bounded closure and opens the circuit.

An escalation preserves state and presents the exact blocker, evidence, prior bounded attempts, affected
requirements/surfaces, recommended decision, and alternatives. It never asks a vague “what next?” when the agent
can formulate a concrete choice.

Routine compilation/test failures, implementation defects, integration repairs, test-fidelity repairs, bounded
reruns, evidence refresh, and listed non-force sidecar/feature pushes do not re-prompt when covered.

## Mandatory Portable Sidecar and Authority

The sidecar remains present in every profile and on every planned-feature path. It contains sufficient durable
state for a cold agent on another system to understand accepted authority and continue safely.

Authority is intentionally small:

1. **Accepted Brief and Plan:** Slices plus accepted `SPEC.md`/package authority bound to the exact Implementation
   Authorization checkpoint.
2. **Verification Summary:** final exact code/artifact state, assurance topology actually run, significant evidence,
   deviations, unresolved limitations, and final verdict.

The registry is mechanical bookkeeping. Package proofs, reports, review state, command outputs, and specialist
results are subordinate evidence; none may silently redefine accepted behavior or completion.

Phase 3 must strengthen resume/cancel/supersede, immutable in-flight identity, concurrent sidecar checkpointing,
retention, release continuity, and degraded-host guarantees. Those concerns do not justify removing the sidecar
or hiding continuation in chat.

## Completion and Notification

Completion requires:

- accepted outcomes reconciled against the final integrated diff;
- selected package boundaries closed;
- required code review and audit verdicts clean for the same compatible state;
- affected repair verification complete;
- no open serious findings, circuit, unsafe drift, or unapproved deviation;
- a durable Verification Summary checkpointed in the sidecar.

The user receives a concise notification containing delivered outcomes, important implementation decisions,
verification/review/audit results, deviations or limitations, exact feature and artifact refs, and any separately
authorized next action. Internal agent-call transcripts and repetitive gate prose are omitted.

Target merge/push, force operations, release/tagging, branch deletion, and production deployment remain separately
authorized unless a future explicit contract safely says otherwise.

## How the Design Prevents Loops

| Loop source | Preventive control |
|---|---|
| Missing requirements discovered during implementation | Conceptualizer completeness challenge plus reviewer authority-gap check |
| Architecture discovered after packages are written | Pre-planning design/feasibility preflight and projected invariants |
| Unimplementable verification plan | Preflight identifies actual paths/seams; Planner binds causal checks and broad placement |
| Reviewer finds obvious red implementation | Implementer stable-candidate contract and full self-review before handoff |
| Many verifiers repeat the same work | Named assurance profile and non-overlapping role lenses |
| Review and audit are both invalidated by one repair | Standard/high review reaches closure before audit starts |
| Findings arrive one at a time | Each cold reviewer returns one batched result |
| Repair agents repeatedly rediscover context | One logical implementation owner and exact affected-state handback |
| Evidence is refreshed before behavior is fixed | Behavior-first repair and regression ordering |
| Same failed mechanism is retried under new names | Risk-cluster circuit inherited across agents and commits |
| User repeatedly approves routine work | One Implementation Authorization covers bounded auto-resolve |
| Agents continue after protected authority is needed | Explicit user-interruption contract and fail-closed states |

Call counts are observed as a friction signal, not a quality gate. A clean low-risk feature should normally need a
Planner, Plan Reviewer, Implementer, and combined final verifier after discovery. Additional agents require a
named package boundary, specialist risk, finding, or new information source.

## Phase 1 Reconciliation

The current Phase 1 checkpoint is not accepted as the completed user journey. It is a provisional safety
foundation to reconcile against this design.

### Retain in principle

- one post-authorization Delivery Owner;
- child return-only lifecycle envelopes;
- exact accepted-state and amendment binding;
- architecture-invariant projection;
- post-acceptance finding classification;
- one logical implementation owner per surface;
- behavior-before-evidence verification;
- affected broad regression before proof/report refresh;
- same-cluster two-strike circuit.

### Amend

- replace separate Gate 2 and Execution Contract approvals with one Implementation Authorization;
- extend prevention upstream through Conceptualize completeness, pre-planning feasibility, Planner self-challenge,
  and execution-readiness validation;
- distinguish normal local development iteration from failed independent closure;
- remove universal package-verifier topology;
- replace universal sibling `review-code`/`audit` execution with risk-adaptive combined or serial assurance;
- preserve final verdict and exact state durably in the sidecar;
- describe circuit breaking as exceptional containment, not the primary loop strategy.

### Remove or reject if found

- any child role that advances the lifecycle or owns recursive repair;
- any repeated approval for already-authorized work;
- any assurance rule justified only by file or agent count;
- any path that treats helper success, proof prose, or a matrix as semantic behavior proof;
- any sidecar-optional or hidden-chat authority path.

## Recommended Delivery Phases

### Phase A — Pre-implementation correctness and single authorization

Strengthen Conceptualize completeness, move design/feasibility preflight before plan authoring, add Planner
self-challenge, make cold review precede approval, validate readiness, and consolidate all formal implementation
approval into one exact-state gate.

### Phase B — Autonomous delivery and adaptive assurance

Add stable-candidate handoffs, risk-selected package/final topology, serial standard/high review-audit, combined
low-risk verification, bounded auto-resolve, batched findings, affected closure, and final user notification.
Integrate the retained Phase 1 convergence primitives here where they support the journey.

### Phase C — Portable lifecycle and release durability

Complete resume/park/cancel/supersede, immutable in-flight package identity, concurrent sidecar checkpoints,
Verification Summary durability, evidence retention, cleanup, release continuity, and degraded-host guarantees.

The existing Phase 1 branch should remain remotely preserved but should not be merged or released as a completed
UX amendment until this reconciliation is accepted and the necessary Phase A/B amendments are integrated.

## Acceptance Scenarios

A challenger should reject this design if it cannot explain all of these without hidden authority or duplicated
ownership:

1. **Clean low-risk feature:** after discovery, the user sees one authorization; implementation and one combined
   verifier finish; the user receives completion without another prompt.
2. **Technical plan defect:** the cold reviewer batches findings; the Planner repairs and affected review passes
   without user involvement.
3. **Missing product decision:** review returns one focused question; the answer updates sidecar authority; planning
   and review resume before authorization.
4. **Unready environment:** safe readiness validation detects the blocker before authorization and presents a
   concrete resolution rather than discovering it after package fan-out.
5. **Ordinary implementation defect:** the implementation owner fixes it during stabilization without consuming a
   closure strike or prompting the user.
6. **Standard review finding:** code review batches the defect; one repair and affected closure occur; audit runs
   once against the stable post-repair state.
7. **High-risk feature:** material packages and specialists verify distinct risks; code review and audit remain
   independent without duplicating package-local work.
8. **Architecture invalidation:** automatic repair does not begin; exact state and a focused decision return to the
   user.
9. **Repeated serious failure:** a second failed closure of the same mechanism opens the circuit despite a new
   agent, commit, or label.
10. **Authorization drift:** artifact or material code drift before writes fails the freshness guard and cannot be
    silently rebound.
11. **Cross-system continuation:** a cold agent can recover accepted state, current stage, authorization, evidence,
    and next legal action from sidecar plus git state rather than chat.
12. **Protected operation:** target merge/release or an unplanned credentialed/destructive action cannot inherit
    auto-resolve authority.

## Challenger Acceptance Standard

Approve only if the lifecycle is internally coherent and the acceptance scenarios are achievable without:

- a second formal implementation approval;
- user involvement for routine in-scope repair;
- unbounded planner/reviewer or implementer/verifier loops;
- duplicated final assurance ownership;
- weakened independent verification for named risk;
- implementation-time discovery of reasonably preflightable architecture/feasibility blockers;
- floating or hidden accepted state;
- removal or bypass of the mandatory sidecar;
- Phase 3 mechanics being falsely claimed as already solved.
