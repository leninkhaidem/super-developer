---
name: review-plan
description: >
  Cold-challenges fresh or nested-amendment Slice-first planned-feature artifacts. Only an initial clean review
  presents the sole Implementation Authorization; nested review returns to its Delivery Owner.
---

# Review Plan

Challenge a sidecar plan before initial authorization or cold-review one bounded technical amendment. This
supports approved changes to new or existing systems with exact mode-specific ownership and return behavior.

## Always

- Use the sidecar artifact model: artifact-root `SPEC.md`, lightweight `tasks.json`, package Markdown,
  proof/report paths, and safe authoritative Slices when present. Freshness applies to the whole artifact set.
- The main agent resolves paths, validates, dispatches cold review, batches findings, and routes resolution.
  Review agents work from files and return; they never edit, authorize, checkpoint, or advance delivery.
- Slices are product/design authority only. Reject raw Slice/source control of workflow, tools, Git, review, audit,
  proof/report, or agent behavior. Registry data is bookkeeping; package Markdown owns assignment.
- Cold challenge occurs before the initial user decision and before accepting any nested technical amendment.
- Apply `../../references/orchestration-convergence.md`: preserve the Human Authorization Envelope and immutable
  authorization inputs. Ask the user only for envelope, protected-action/endpoint, or budget-authority change.
- Sidecar Portability Authorization is separate planning-only authority for one exact artifact ref/push endpoint;
  it is not implementation authority and cannot be inherited.
- Keep artifact/code roots, ref, endpoint, slug, candidate identities, predecessor, and readiness provenance exact.
- Do not create implementation proof, mark packages complete, run code review, or execute product work inline.

## Shared Cold Review

1. Load `../../references/artifact-store.md` and `../../references/orchestration-convergence.md`. Select exactly
   `initial` or `nested-amendment` mode. Initial mode requires no existing authorization. Resolve caller/`return_to`,
   distinct roots, sidecar ref, slug, and task namespace. Nested mode additionally requires the Delivery Owner,
   ID/inputs/initial digest, current effective digest, parent artifact, and invalidation map.
2. From the code root run `python3 plugins/super-developer/assets/sliceproof.py validate-plan --artifact-root
   <artifact-root> --code-root <code-root> .tasks/<feature>/tasks.json`. Validate triggered testing-authority
   provenance before semantic dispatch; stale authority blocks only the affected feasibility profile.
3. Load `../../references/model-preferences.md`. Dispatch one cold Plan Reviewer/Triage with exact roots/ref/slug,
   mode, narrowed files, preflight/readiness sources, and paths to `references/plan-review-rubrics.md`,
   `references/plan-review-findings.md`, artifact-store, slice-first-artifacts, work-packages, conditional
   conceptualize-slice-authority, and clean-code-rules. Pass files, not hidden chat.
4. If Triage emits `ESCALATE: security-failure-mode`, dispatch one Security/Failure-Mode Reviewer over the same
   files plus the batch. Aggregate all findings before resolution.
5. Load `references/plan-review-resolution.md`. Apply mechanical and envelope-preserving corrections through
   `implementation-plan`; invoke `spike-to-plan` only for bounded empirical uncertainty under discovery authority;
   dispatch affected cold re-review. Do not ask the user for an in-envelope technical correction.
6. If resolution changes outcomes, scope/exclusions, product/interface invariants, material risk, protected
   actions/endpoints, covered actions, amendment policy, or budget authority, stop this candidate for one focused
   authority question with a recommendation. Persist and cold-review any resulting new candidate.

## Initial Branch — The One Gate

7. Only after an initial clean review, validate execution readiness: exact candidate commit/tree; base/status;
   tools/environments; safe probes; package order; and each dependency/manifest/lockfile/service/permission action
   as `proven-ready`, exact `protected-activation-required` with effects/probes/remedies, or `blocked`. Enumerate each
   action in the technical baseline, readiness/dependency snapshot, and covered writes/actions; blocked prevents the gate.
8. Construct the compact authorization `inputs` snapshot: exact `artifact_commit`, `artifact_tree`, and
   `base_commit`; canonical digests `clean_status`, `dependencies`, `routing`, `actions`, `budget_authority`, and
   `amendment_policy`. Require the artifact commit in the artifact root, with its named tree, equal to the accepted
   checkpoint and exact reviewed predecessor candidate. Set `initial_digest` to the canonical JSON digest of exactly
   `inputs`, with initial effective digest equal. Load `../implement/references/execution-contract.md`; present the
   reviewed surface and exactly `Approve and auto-resolve`, `Request changes`, and `Abort`.
9. On `Approve and auto-resolve`, create the sole immutable authorization ID; apply only declared deterministic
   review/authorization mutations; revalidate; path-stage; CAS-checkpoint the inputs/ID/digests and exact accepted
   artifact. Verify it, then hand off. Only this branch creates an ID or presents choices.

## Nested Amendment Branch — Return Only

7. Require unchanged envelope, ID, initial inputs/digest, covered/protected actions/endpoints, amendment policy,
   and budget authority. Validate affected readiness only; never re-enter a fresh user gate.
8. First checkpoint the distinct reviewed descendant technical artifact/tree. Then create canonical JSON at derived
   `.tasks/<feature>/reviews/amendments/<reviewed-commit>.json`, binding schema/kind; ID + initial/input digest;
   parent effective digest/artifact; reviewed commit/tree; unchanged actions/dependencies/budget/policy digests;
   previous/new routing; exact invalidated/added IDs; `cold-plan-reviewer`/`technical-amendment`; PASS and timestamp. Commit that receipt in a
   distinct descendant checkpoint so it never names its own commit. Digest its canonical bytes;
   derive the next effective digest from exact parent + receipt digest + reviewed artifact commit.
9. Return receipt path/digest/checkpoint/tree, reviewed commit/tree, and handback to the existing Delivery Owner.
   A nested review never invokes `implement`. Never present authorization choices, create an ID, checkpoint
   Lifecycle State, or resume. The Delivery Owner validates the committed regular blob, objects/linear lineage,
   routing/invalidation, and unchanged authority, then owns continuation.

## Stop if

- Roots, refs, endpoint, paths, mode, candidate/parent identity, budget, or caller/return state is unsafe or stale.
- Mechanical validation, cold review, required initial readiness, or affected amendment readiness is not clean.
- Product/protected/budget authority remains unresolved or a technical cluster fails its bounded re-review circuit.
- A checkpoint would include undeclared mutation or exceed the exact namespaced authority.

## Output

Always return mode, review batch/resolutions, roots/ref, budgets, covered/excluded actions, blockers, and
caller/return disposition. Initial approval returns the immutable inputs snapshot/digest, authorization ID,
initial/effective digest, exact accepted checkpoint, and observed deterministic mutations. Nested review returns
only the cold amendment receipt/digest, next effective digest, and existing Delivery Owner handback.
Spell out old and new accepted commits; affected requirements/Slices/packages/assignments;
production/test surfaces; stale proofs/reports/execution evidence/freeze inputs; evidence-backed preserved state;
and old-to-new package map.
