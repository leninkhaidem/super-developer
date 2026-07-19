# Super Developer

Super Developer is a portable coding-assistant workflow, packaged as a Claude Code plugin, for moving from
exploration through implementation-ready planning, autonomous delivery, risk-adaptive assurance, documentation,
and release preparation.

One plugin. 15 skills. No manual git juggling.

---

## What It Does

Super Developer replaces scattered prompts with one file-backed journey for New and existing-system changes:

```text
Conceptualize
  -> requirement / architecture / feasibility / prerequisite / production-path preflight
  -> implementation-ready plan + cold challenge
  -> exactly ONE Implementation Authorization
  -> Delivery Owner autonomous package delivery / repair / checkpoints
  -> boundary B[i] when pre-consumption trust is required; otherwise final routing
  -> immutable final freeze F
  -> low F -> C(code-risk PASS, completion PASS) -> V
     standard F -> R(PASS/closure) -> U(PASS, F, R) -> V
     high F -> R(PASS/closure) -> S[*](each PASS, F, R) -> U(PASS, F, R, S[*]) -> V
  -> checkpoint index-only V -> verified notification
```

Preflight resolves missing requirements and triggered architecture, feasibility, prerequisite, and real
production-path verification seams before authorization; protected activation is checked before product writes or
fanout. Cold `review-plan` challenges the implementation-ready package topology, evidence plan, routing, and finite
budgets. Its clean initial result presents the sole authorization. There is no later implementation decision.

After authorization, `implement` is the Delivery Owner. It autonomously dispatches and stabilizes packages,
classifies and batches covered repairs, reruns affected evidence, and publishes code-before-sidecar checkpoints.
Nested envelope-preserving amendments return cold receipts to the same owner; no child restarts delivery or mints
new authority. Budgets and C/R/S/U call consumption are cumulative across agents, resumes, repairs, and freezes.
An initial serious rejection is strike 1; a failed closure for the same accepted invariant, root mechanism, and
architectural surface is strike 2 and opens the automatic-repair circuit.

Assurance follows meaningful risk and consumption boundaries, never file, test, or agent count. `boundary`
packages receive a pre-freeze independent `B[i]`; coherent leaves route directly to final assurance without a
fabricated report. Final assurance is exactly one serial profile equation over immutable `F`. All C/R/S/U roles
are cold, read-only, and return-only. `V` only indexes the same-freeze outputs and deviations; it proves nothing by
itself. The Delivery Owner checkpoints `V`, validates the graph, and then notifies.

Validated Slices remain product/design authority only. Workflow, tool, Git, proof, and assurance authority stays in
the plugin instructions and shared references.

---

## Portable Authority and Continuity

Every planned feature uses a mandatory portable orphan `artifacts/<feature>` sidecar at a resolved Git worktree
root distinct from the code root. `.planning/`, `.tasks/`, proofs, receipts, and Lifecycle State exist only there;
current-root copies are migration input, never planned-feature authority. Code is checkpointed first under direct,
immutable `refs/heads/checkpoints/<feature>/<slot>/g<generation>` refs, then referenced by a non-force sidecar CAS
checkpoint. A symbolic, moved, local-only, missing, or mismatched ref fails closed.

`.tasks/<feature>/lifecycle-state.json` is a compact exact current snapshot: disposition/stage, immutable
authorization lineage, owner, direct refs, fixed maxima and issued usage, packages, serious clusters, freeze, and
current receipt pointers. Git history is the history; Lifecycle State is not an event log, semantic proof, or
permission. Super Developer adds no dashboard, evaluation ledger, state service, or second completion system.

Cold interruption handling uses only verified portable state:

- **Park** records one quiescent remote checkpoint and its exact resume point without resetting authority or budgets.
- **Resume** fetches that parked sidecar and every named direct code ref; later local state is untrusted recovery input.
- **Cancel** records a terminal no-action snapshot and grants no cleanup or completion claim.
- **Supersede** records a cold-reviewed replacement and immutable old-to-new package map; it grants no inherited authority.
- **Completed** is terminal and cannot resume.

---

## Planned-Feature Artifact Model

| Artifact | Purpose |
|---|---|
| `.planning/<feature>/index.md` | Optional Conceptualize workspace entry point. |
| `.planning/<feature>/slices/*.md` | Optional authoritative product/design Slices. |
| `.tasks/<feature>/SPEC.md` | Accepted source baseline, requirements, constraints, architecture invariants, non-goals, and verification summary. |
| `.tasks/<feature>/tasks.json` | Bookkeeping only: profile, package paths, modes, status, and dependencies. |
| `.tasks/<feature>/packages/<WP-ID>.md` | Work-package assignment, consumed contracts, evidence expectations, and boundary/final routing. |
| `.tasks/<feature>/proofs/<WP-ID>.proof.md` | Implementer closure claims and observed package evidence. |
| `.tasks/<feature>/reports/<WP-ID>.package-verification.md` | Conditional pre-freeze `B[i]` for `boundary`; absent with a null report path for `final`. |
| `.tasks/<feature>/semgrep/*` | Optional local helper-produced package/integration evidence. |
| `.tasks/<feature>/assurance/<freeze-id>/` | Immutable `F` plus same-freeze C or R/S/U outputs and index-only `V`. |
| `.tasks/<feature>/reviews/review-code-state.json` | Optional governance context only; never final authority or lifecycle state. |
| `.tasks/<feature>/lifecycle-state.json` | Compact CAS continuation snapshot and current receipt pointers; never a history ledger. |

Package evidence uses minimum-sufficient **Selected Causal Evidence**: each chosen typed anchor names the
behavior/risk, why it is sufficient, substitutes or fixtures, and a fresh command result. One causal test may support
related obligations. Counts, LOC, ratios, coverage percentages, suite volume, labels, matrices, and helper success
never establish semantic sufficiency; matrices index reviewed evidence instead of defining it.

---

## `sliceproof.py` Helper Contract

`plugins/super-developer/assets/sliceproof.py` is the only planned-feature mechanical helper. Use explicit absolute,
distinct artifact/code roots:

```bash
ROOTS=(--artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT")
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan "${ROOTS[@]}" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" create-proof "${ROOTS[@]}" ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-proof "${ROOTS[@]}" ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete "${ROOTS[@]}" ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final "${ROOTS[@]}" ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-lifecycle-state "${ROOTS[@]}" --feature <feature> --previous-commit <prior-sha> # omit predecessor at generation 1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-agentic-completion "${ROOTS[@]}" --feature <feature>
```

- `validate-plan`, `create-proof`, and `validate-proof` check safe artifact mechanics and package closure shape.
- `validate-package-complete` branches by mode: exact `B[i]` binding for `boundary`, or null-report direct-final
  deferral for `final`; it runs before package `done` and proves no semantics.
- `validate-final` is the **pre-freeze** package-equation check. It requires done packages and mode-correct package
  evidence, but does not claim post-freeze assurance ran.
- `validate-lifecycle-state` checks exact compact local topology, immutable lineage, predecessor ancestry, direct
  refs, monotonic budgets, packages, and transitions. Remote reachability/CAS remains worktree-owned.
- `validate-agentic-completion` is the **post-freeze** read-only graph check after `V` is checkpointed. It validates
  one profile equation and same-freeze lineage before notification.

The helper does not run tests, judge causal sufficiency, perform assurance, mutate lifecycle state, fetch, push, or
replace C/R/S/U verdicts. See [`references/tool-usage.md`](references/tool-usage.md),
[`references/slice-first-artifacts.md`](references/slice-first-artifacts.md), and
[`references/package-lifecycle.md`](references/package-lifecycle.md) for detailed boundaries.

---

## Local Model Preferences

The only supported preferences file is `.superdeveloper/preferences.yml`. It is developer-local/gitignored. Model values are `inherit`, `adaptive`, or an exact model name:

```yaml
models:
  default-model: inherit
  implementation-plan: inherit
  design-preflight: adaptive
  implement: adaptive
  review-plan: adaptive
  review-code: inherit
  skeptic-agent: adaptive
```

Unsupported local preference files are ignored; `.superdeveloper/preferences.yml` is the current contract.

---

## Optional Local Semgrep Validation

Semgrep validation is optional, local-first, and disabled by default. Ordinary planning, implementation, review, and audit continue without helper setup, scan evidence, or internet access when `semgrep.enabled: false`.

### Local Semgrep preferences and policy files

Semgrep reads only the `semgrep:` section of `.superdeveloper/preferences.yml`:

```yaml
semgrep:
  enabled: false
  privacy-mode: true
  rules-provider: plugin-community-cache
  project-policy-gate: skeptic
```

Project-local Semgrep files are also developer-local/gitignored:

| Path | Role |
|---|---|
| `.superdeveloper/semgrep/excluded-rules.yml` | Compact command policy; each safe `excluded-rules[].id` becomes one helper-owned `--exclude-rule` argument. |
| `.superdeveloper/semgrep/local-rules.yml` | Additive project-local Semgrep rules, included automatically when present. |
| `.superdeveloper/semgrep/stack-profile.yml` | Machine-local lookup from detected stacks to absolute local Semgrep config paths. |

### Rule cache, network boundary, and helper use

Community rules are shared per installed plugin under `${SUPER_DEVELOPER_PLUGIN_ROOT}/.cache/semgrep-rules/community` with inventory at `${SUPER_DEVELOPER_PLUGIN_ROOT}/.cache/semgrep-rules/index.json`. First opt-in happens before implementation planning and names any approved network setup/update: clone the community rules repo if the cache is missing, or `git pull --ff-only` inside the cache when it already exists. If the plugin cache is not writable, the workflow stops for an approved shared-cache alternative instead of cloning into the project. Routine scans must not clone, pull, fetch Registry configs, sync rules, use cloud/AppSec/CI/Pro/secrets modes, emit telemetry, or use `auto`.

Agents use the wrapper for all Semgrep work: `index`, `retrieve`, `scan`, `summarize`,
`list-findings`, and `show-finding`. Scan commands use
`python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...`; agents never run raw direct `semgrep` scans. They do not inspect `index.json` manually, hand-assemble Semgrep shell
commands, or dump/read raw Semgrep JSON. Normal finding consumption is bounded: `summarize` first,
filtered/limited `list-findings` second, and selected `show-finding` only for stable local refs.
`show-finding` code excerpts require `--target <scan-scope>` and
`--expected-summary-digest <summary_digest>` from recorded summary evidence.

### Evidence, freshness, and findings

Enabled package scans write paired local evidence under `.tasks/<feature>/semgrep/`:

```text
.tasks/<feature>/semgrep/<WP-ID>.semgrep.json
.tasks/<feature>/semgrep/<WP-ID>.semgrep-summary.json
```

When concrete cross-package/shared-surface risk requires a final integrated check, the one-shot integrated scan writes:

```text
.tasks/<feature>/semgrep/integration.semgrep.json
.tasks/<feature>/semgrep/integration.semgrep-summary.json
```

Proofs and package verification reports cite raw path, raw digest, summary path, summary digest, scan scope, and a concise helper-derived finding/no-finding summary when Semgrep is enabled or contracted. Evidence is invalid when it escapes `.tasks/<feature>/semgrep/`, uses unpaired stems, traverses or follows symlinks outside the repo/worktree/task evidence root, has stale/mismatched digests, or comes from wholesale raw JSON consumption.

Semgrep findings preserve Semgrep severity but are advisory by default. They do not create product requirements, override Slice/plan authority, automatically become Super Developer blockers, or trigger fix-all/unbounded scan-repair loops. Package scans are primary; integrated scans are conditional and one-shot. Local exclusions or local rules follow the `project-policy-gate: skeptic` authority model: implementers may propose, independent verifier/reviewer/skeptic authority may authorize, the orchestrator writes compact local policy, and final audit is read-only.

---

## Skills

| Skill | What It Does | Usage |
|---|---|---|
| **conceptualize** | Runs an optional one-question-at-a-time exploration, maintains an ignored workspace Index, and writes focused Slices only when useful. | Standalone + pre-planning |
| **implementation-plan** | Runs requirement/architecture/feasibility/prerequisite/production-path preflight, then creates the implementation-ready SPEC, registry, routed packages, proof paths, and conditional report paths. | Pipeline + standalone |
| **skill-authoring** | Creates or revises compact skills with on-demand references and a mid-tier-agent followability gate. | Standalone + internal |
| **review-plan** | Cold-challenges package authority, feasibility, evidence, routing, and budgets; its clean initial result presents the sole Implementation Authorization. | Pipeline + standalone |
| **implement** | Delivery Owner after authorization: autonomous package delivery, classified repair, code/sidecar checkpoints, boundary/final routing, final freeze, assurance dispatch, `V`, and notification. | Pipeline |
| **review-code** | Reviews PR/local diffs, or returns planned-feature `C` (low) or `R` (standard/high) for one immutable freeze; pipeline mode never claims completion authority. | Pipeline + standalone + PR review |
| **audit** | Returns standard/high completion receipt `U` only after same-freeze `R` PASS (and required high `S[*]`); never a standalone universal final decision. | Pipeline standard/high only |
| **spike-to-plan** | Runs empirical feasibility spikes before planning and routes accepted evidence into durable planning artifacts. | Planning hook |
| **diagnose-and-fix** | Diagnoses issues evidence-first, reports findings for approval, then routes approved fixes through worktree or implementation-plan. | Standalone |
| **testing** | Establishes or updates reusable project testing workflow docs, then routes test authoring, alteration, and execution through the approved workflow. | Standalone |
| **perspectives** | Explores architecture or design options from multiple angles with a final skeptic synthesis. | Standalone |
| **worktree** | Provides git worktree runbooks for planned features, bugfixes, hotfixes, spikes, cleanup, and target-merge safety. | Internal + standalone |
| **code-doc** | Generates or updates codebase documentation through scout, analysis, synthesis, review, and handoff stages. | Standalone |
| **readme-polish** | Authors or polishes a repository README and optional repository metadata without expanding into whole-codebase docs. | Standalone |
| **release** | Prepares and publishes releases behind a single release contract covering checks, pushes, tags, notes, and cleanup. | Standalone |

---

## Review-Code Modes

| Mode | Trigger | Boundary |
|---|---|---|
| **Planned-feature pipeline** | Explicit feature context plus a Delivery-Owner-supplied immutable `F` and current package evidence. | Returns low `C` or standard/high `R`; never records completion readiness, dispatches later roles, repairs, or creates `V`. |
| **PR** | PR URL, `owner/repo#N`, or `#N` in a repository with `gh` available. | Review-only for code changes; GitHub side effects require the PR action gate. |
| **Local** | No planned-feature context and no PR identifier. | Reviews one complete caller-bound or locally captured state: committed base-to-HEAD plus staged, unstaged, and untracked files together. Repairs require the local action gate, owning repair contract when supplied, rebinding, and fix verification. |

Ordinary PR/local review does not inherit planned-feature Slice, proof, report, or audit obligations unless planned-feature artifacts are explicitly in scope.

---

## Git Worktree Strategy

The `implement` and `worktree` skills keep the root worktree user-owned and create isolated package worktrees:

```text
project/                               # user-owned root; do not switch branches
+-- .worktrees/
|   +-- auth/
|   |   +-- wp-WP1/                    # branch: wp/auth/WP1
|   |   +-- wp-WP2/                    # branch: wp/auth/WP2
|   |   +-- merge/                     # branch/ref: feature/auth
```

Key rules:

- The Delivery Owner owns branch/worktree creation, merges, checkpoints, cleanup, and authorized pushes.
- Package agents edit only their assigned package worktree and proof Markdown handoff.
- Every covered sidecar/code/feature push uses one unchanged captured push endpoint and exact non-force ref.
- Code checkpoints are published and verified before path-specific sidecar CAS commits reference them.
- Target/main merge or push always requires separate explicit approval.
- Cleanup requires merge-base proof and clean worktrees.

### Release retention

The remotely verified sidecar containing final `V` and every immutable checkpoint ref named by Lifecycle State,
`F`, or `V` are retained through and after release by default. Target delivery, publishing, ordinary feature
cleanup, Sidecar Portability Authorization, and Implementation Authorization never imply their deletion. Portable
evidence cleanup occurs only when explicitly requested, after final target sync, under a separate exact decision
that first proves equivalent durable preservation and then verifies every deletion. Otherwise release reports the
retained refs without another prompt.

---

## Installation

### Install from GitHub

```bash
/plugin marketplace add leninkhaidem/super-developer
/plugin install super-developer@super-developer-marketplace
```

Update later:

```bash
/plugin update super-developer@super-developer-marketplace
```

### Install from local directory

```bash
git clone https://github.com/leninkhaidem/super-developer.git
claude --plugin-dir /path/to/super-developer/plugins/super-developer
```

Claude Code discovers packaged skills automatically. Other hosts need equivalent plugin/skill discovery and `SUPER_DEVELOPER_PLUGIN_ROOT` pointing at `plugins/super-developer`.

---

## Usage

### Full planned-feature pipeline

```text
> Plan this feature
```

A delegated planner writes the sidecar SPEC, registry, package assignments, and evidence paths after design/
feasibility preflight. Cold `review-plan` challenges and resolves technical defects, then an initial clean review
presents the sole **Implementation Authorization**: **Approve and auto-resolve**, **Request changes**, or **Abort**.
Approval checkpoints one immutable authorization ID/input snapshot. `implement` then owns autonomous delivery;
nested envelope-preserving amendments return cold receipts under that same ID, while envelope/protected/budget
changes stop for one focused authority decision. Boundary receipts and final assurance return to that owner, which
checkpoints index-only `V`, validates completion, and notifies—there is no later implementation approval.

Useful standalone prompts:

```text
> Conceptualize this product idea before planning
> Get perspectives on this architecture decision
> Spike this feature assumption before planning
> Review this PR: owner/repo#42
> Review my code
> Spike and fix this regression
> Establish this project's testing workflow for browser E2E
> Add test coverage for this behavior using the approved testing workflow
> Polish this repository README
> Prepare a release
> Document this codebase
```

---

## Plugin Structure

```text
plugins/super-developer/
+-- .claude-plugin/
|   +-- plugin.json
+-- assets/
|   +-- semgrep_rules.py
|   +-- sliceproof.py
|   +-- tests/
|       +-- test_semgrep_rules.py
|       +-- test_skill_prompts.py
|       +-- test_sliceproof.py
+-- references/
|   +-- clean-code-rules.md
|   +-- conceptualize-slice-authority.md
|   +-- decision-prompts.md
|   +-- known-risk-patterns.md
|   +-- model-preferences.md
|   +-- package-lifecycle.md
|   +-- semgrep.md
|   +-- slice-first-artifacts.md
|   +-- tool-usage.md
|   +-- work-packages.md
+-- skills/
|   +-- audit/
|   |   +-- SKILL.md
|   |   +-- references/audit-subagent-contract.md
|   +-- code-doc/
|   |   +-- SKILL.md
|   |   +-- references/update-merge.md
|   +-- conceptualize/
|   |   +-- SKILL.md
|   |   +-- references/final-handoff.md
|   |   +-- references/slice-template.md
|   |   +-- references/workspace-index.md
|   +-- implementation-plan/
|   |   +-- SKILL.md
|   |   +-- references/artifact-authoring.md
|   |   +-- references/conceptualize-inputs.md
|   |   +-- references/design-preflight.md
|   |   +-- references/spec-template.md
|   |   +-- references/validation-checklist.md
|   +-- implement/
|   |   +-- SKILL.md
|   |   +-- references/execution-contract.md
|   |   +-- references/package-agent-contract.md
|   |   +-- references/package-dispatch.md
|   |   +-- references/package-verification.md
|   |   +-- references/repair-agent-contract.md
|   |   +-- references/package-integration-gates.md
|   +-- review-code/
|   |   +-- SKILL.md
|   |   +-- references/fix-implementer-contract.md
|   |   +-- references/local-workflow.md
|   |   +-- references/pipeline-report.md
|   |   +-- references/pr-workflow.md
|   +-- review-plan/
|   |   +-- SKILL.md
|   |   +-- references/plan-review-findings.md
|   |   +-- references/plan-review-resolution.md
|   |   +-- references/plan-review-rubrics.md
|   +-- skill-authoring/
|   |   +-- SKILL.md
|   +-- testing/
|   |   +-- SKILL.md
|   |   +-- references/workflow-contract.md
|   |   +-- references/delegation-packets.md
|   |   +-- references/core/generic-testing.md
|   |   +-- references/web/application-testing.md
|   |   +-- references/web/browser-e2e-stack-setup.md
|   +-- worktree/
|   |   +-- SKILL.md
|   |   +-- references/bugfix-hotfix-workflow.md
|   |   +-- references/cleanup-safety.md
|   |   +-- references/feature-package-workflow.md
|   +-- perspectives/SKILL.md
|   +-- diagnose-and-fix/
|   |   +-- SKILL.md
|   |   +-- references/fix-implementer-contract.md
|   +-- readme-polish/
|   |   +-- SKILL.md
|   |   +-- references/banner-examples.md
|   +-- spike-to-plan/SKILL.md
|   +-- release/SKILL.md
```

---

## Requirements

- Claude Code with plugin support, or another host with equivalent skill/plugin loading.
- Python 3 for `sliceproof.py` and local helper assets.
- git for worktree-based workflows and optional approved Semgrep rule-cache clone/pull setup.
- Semgrep CLI only when optional local Semgrep validation is enabled.
- GitHub CLI (`gh`) for PR review mode only.

---

## Operating Principles

| Principle | Why it matters |
|---|---|
| Slice-first planning | Slices capture durable product/design understanding while control-plane authority stays out of Slice text. |
| Progressive disclosure | `SKILL.md` files route and guard; detailed contracts load only at action points. |
| Package delegation | Work packages are large enough for useful execution; only meaningful consumed/risk boundaries add `B[i]`. |
| Minimum-sufficient evidence | Selected causal anchors prove accepted behavior and risk; volume and matrices never substitute for judgment. |
| Risk-adaptive final assurance | Immutable `F` follows exactly low C, serial standard R/U, or serial high R/S/U before index-only `V`. |
| Portable bounded continuity | Compact Lifecycle State plus direct immutable refs supports cold park/resume/cancel/supersede without a dashboard, ledger, or state service. |
| Explicit Git authority | Feature pushes, target merges, cleanup, and release operations happen only under their named contracts; portable evidence is retained by default. |

---

## License

MIT
