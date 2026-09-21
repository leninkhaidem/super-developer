# Super Developer

Super Developer is a portable coding-assistant workflow, packaged as a Claude Code plugin, for moving from exploration to Slice-first planning, isolated implementation, bounded code review, final audit, documentation, and release preparation.

One plugin. 16 skills. No manual git juggling.

---

## What It Does

Super Developer scales the workflow to the work. Clear, bounded, low-risk changes use a task-appropriate direct
route with accepted scope and credible verification, not mandatory planning files. Explicit plan requests and
changes needing durable coordination, substantial design, or material risk decisions use this planned-feature model:

```text
conceptualize (optional; conversation first)
        |
        v
implementation-plan -> review-plan -> implement -> final review-code + final audit
        |                 |              |             |                  |
        |                 |              |             |                  final completeness gate
        |                 |              |             final code-risk gate
        |                 |              package agents + result reports
        |                 plan quality and Slice coverage gate
        SPEC.md + tasks.json registry + packages/reports
```

Conceptualize creates no files or worktrees merely because it was invoked. It checkpoints settled understanding
when durability is useful or necessary, or documentation is explicitly requested—not after every statement.
Simple outcomes may remain in chat; a compact Index or focused Slices serve complex discussions and handoffs.
See [`references/change-routing.md`](references/change-routing.md) for the route decision.

Validated Slices are product/design authority only. Workflow, tool, git, result, review, and audit authority stays in the plugin instructions and shared references. Planning, review, and implementation orchestrators may run `empirical-spike` once per attempt for a distinct material question after static evidence is insufficient; one initial run and at most two materially changed follow-ups are allowed. After `approve auto-resolve`, in-scope work is autonomous. Dirty probes clean only through exact receipt-owned local restoration; continuation packages use reviewed base/prerequisite evidence and remain safety nets through final gates.

---

## Planned-Feature Artifact Model

A planned feature lives under `.tasks/<feature>/` and points to optional `.planning/<concept>/` Slice material.

| Artifact | Purpose |
|---|---|
| `.planning/<concept>/index.md` | Optional Conceptualize workspace entry point. |
| `.planning/<concept>/slices/*.md` | Optional authoritative product/design Slices. |
| `.tasks/<feature>/SPEC.md` | Accepted requirements, constraints, non-goals, Slice inventory, and verification summary. |
| `.tasks/<feature>/tasks.json` | Lightweight registry only: feature metadata, package paths, `report_path`, status, and dependencies. |
| `.tasks/<feature>/packages/<WP-ID>.md` | Stable-ID assignment: scope, Slice obligations, primary paths, Acceptance, report path, dependencies, and verification depth/reason in Notes. |
| `.tasks/<feature>/reports/<WP-ID>.package-verification.md` | Independent package result; section shape owned by `references/package-verification-report.md`. |
| `.tasks/<feature>/reviews/review-code-state.json` | Review-code governance readiness for audit handoff. |

`tasks.json` is bookkeeping. Package Markdown owns assignment, `report_path` names the package result, review-code state owns final-review readiness, and audit owns the final PASS/FAIL judgment.

---

## `sliceproof.py` Helper Contract

`plugins/super-developer/assets/sliceproof.py` is the only planned-feature mechanical helper. It validates paths and artifact mechanics; it does not run tests, judge implementation sufficiency, write review readiness, or replace package verification, review-code, or audit.

Run from a repository or package worktree with explicit paths:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-plan ".tasks/<feature>/tasks.json"
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" render-report ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete ".tasks/<feature>/tasks.json" --package WP1
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-final ".tasks/<feature>/tasks.json"
```

Command boundaries:

- `validate-plan`: checks the registry, package Markdown, safe paths, dependencies, declared Slice H3 IDs, and that every package has at least one executable Acceptance Checklist item.
- `render-report`: emits an unverified result skeleton to stdout from the package Acceptance Checklist. It never writes files, runs checks, or invents passing evidence; preserve any existing result and Plan-gap history.
- `validate-package-complete`: read-only checklist coverage and cheap pointer resolve. It does not write the result file or judge semantics.
- `validate-final`: checks all packages are done and each result file is structurally complete.

See [`references/tool-usage.md`](references/tool-usage.md), [`references/slice-first-artifacts.md`](references/slice-first-artifacts.md), and [`references/package-lifecycle.md`](references/package-lifecycle.md) for the detailed boundaries.

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

Package result reports cite raw path, raw digest, summary path, summary digest, scan scope, and a concise
helper-derived finding/no-finding summary when Semgrep is enabled or contracted. Evidence is invalid when it escapes `.tasks/<feature>/semgrep/`, uses unpaired stems, traverses or follows symlinks outside the repo/worktree/task evidence root, has stale/mismatched digests, or comes from wholesale raw JSON consumption.

Semgrep findings preserve Semgrep severity but are advisory by default. They do not create product requirements, override Slice/plan authority, automatically become Super Developer blockers, or trigger fix-all/unbounded scan-repair loops. Package scans are primary; integrated scans are conditional and one-shot. Local exclusions or local rules follow the `project-policy-gate: skeptic` authority model: implementers may propose, independent verifier/reviewer/skeptic authority may authorize, the orchestrator writes compact local policy, and final audit is read-only.

---

## Skills

| Skill | What It Does | Usage |
|---|---|---|
| **conceptualize** | Explores one decision at a time; captures settled understanding at useful durability boundaries, with chat-only outcomes valid for simple work. | Standalone + pre-planning |
| **implementation-plan** | Orchestrates a fresh planner worker to create `SPEC.md`, the lightweight registry, package Markdown, and `report_path` declarations from approved requirements, Slices, or accepted empirical evidence. | Pipeline + standalone |
| **skill-authoring** | Creates or revises compact skills with on-demand references and a mid-tier-agent followability gate. | Standalone + internal |
| **review-plan** | Validates planned-feature artifacts, Slice coverage, package assignment, result-file expectations, and approved deferrals before implementation. | Pipeline + standalone |
| **implement** | Orchestrates package worktrees, package agents, package result reports, integration checkpoints, review-code, and audit handoff. | Pipeline + standalone |
| **review-code** | Runs bounded PR, local, or planned-feature pipeline code review with dynamic risk lenses, Skeptic verification for serious findings, and governed fix verification where the mode permits fixes. | Pipeline + standalone + PR review |
| **audit** | Final read-only planned-feature completeness gate over accepted artifacts, package result reports, optional review-code context, and integrated code state. | Final gate + standalone |
| **empirical-spike** | Produces a bounded caller-neutral report for one material unresolved empirical behavior; it neither implements nor chooses or invokes downstream workflows. | Standalone + conditional evidence hook |
| **diagnose-and-fix** | Diagnoses issues evidence-first, reports findings for approval, then routes approved fixes through worktree or implementation-plan. | Standalone |
| **testing** | Establishes or updates reusable project testing workflow docs, then routes test authoring, alteration, and execution through the approved workflow. | Standalone |
| **perspectives** | Explores architecture or design options from multiple angles with a final skeptic synthesis. | Standalone |
| **worktree** | Provides git worktree runbooks for planned features, bugfixes, hotfixes, spikes, cleanup, and target-merge safety. | Internal + standalone |
| **code-doc** | Generates or updates codebase documentation through scout, analysis, synthesis, review, and handoff stages. | Standalone |
| **walk-me-through** | Teaches features, PRs, releases, and code changes through read-only interactive walkthroughs with ASCII diagrams for practical ownership. | Standalone; explicit user invocation only |
| **readme-polish** | Authors or polishes a repository README and optional repository metadata without expanding into whole-codebase docs. | Standalone |
| **release** | Prepares and publishes releases behind a single release contract covering checks, pushes, tags, notes, and cleanup. | Standalone |

---

## Review-Code Modes

| Mode | Trigger | Boundary |
|---|---|---|
| **Planned-feature pipeline** | Explicit or inherited feature context plus `.tasks/<feature>/` artifacts and reviewed implementation state. | Consumes package result reports, records audit readiness, and routes serious fixes through result freshness rules. |
| **PR** | PR URL, `owner/repo#N`, or `#N` in a repository with `gh` available. | Review-only for code changes; GitHub side effects require the PR action gate. |
| **Local** | No planned-feature context and no PR identifier. | Reviews one complete caller-bound or locally captured state: committed base-to-HEAD plus staged, unstaged, and untracked files together. Repairs require the local action gate, owning repair contract when supplied, rebinding, and fix verification. |

Ordinary PR/local review does not inherit planned-feature Slice, result-report, or audit obligations unless planned-feature artifacts are explicitly in scope.

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

- The orchestrator owns branch/worktree creation, merges, cleanup, and approved pushes.
- Package agents edit only their assigned package worktree and may draft the declared result report.
- Feature-source publication cadence is explicit: local-only (no remote authorization), per-package, milestone, or final. Only a due, authorized publication gate requires a remote checkpoint; verified local integration can otherwise unlock dependents.
- Feature-branch pushes must match the approved Execution Contract; sidecar publication is separately authorized.
- Target/main merge or push always requires separate explicit approval.
- Cleanup requires merge-base proof and clean worktrees.

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

A delegated planner writes the artifacts and the draft flows directly into review. Plan and execution decisions
remain separately authorized; ready decisions may share one concise presentation. Auto-resolve covers only approved
in-scope work. Credentials, protected actions, scope/risk/manual changes, and target delivery retain their boundaries.

Implementation, review-owned repairs, and diagnose-and-fix share
[`bounded-attempts.md`](references/bounded-attempts.md): continue when task-relevant observations justify the next
safe, falsifiable correction or diagnostic. Reassess when evidence contradicts the diagnosis or progress stalls,
including inside long repair rounds. There is no default repair quota, count-triggered reassessment, or mandatory
counter bookkeeping without an applicable count limit. Preserve useful history and explicit limits across workers
and resumes; stop for non-convergence, a limit blocking required work, or missing safety/authority. Reopen planning
only for an evidenced plan defect or an authorized broad/risky decision. Existing verification, review, audit, command/worker
timeouts, termination, and cleanup remain required. Per-action timeouts do not guarantee a whole-task resource
ceiling; without external enforcement, aggregate effort control is best-effort. No new approval screen, progress
form, or retry ledger is added. Standalone empirical probes retain their separate three-invocation bound.

Final `review-code` is primary production-defect discovery, including changes from standard packages without a
separate verifier. The independent cold `audit` reconciles complete delivery evidence and inspects code when
concrete evidence/risk triggers warrant it. Same-state `CLEAN` and `PASS` are both required; neither gate
substitutes for the other. Mechanical-only artifact corrections can avoid a planner/reviewer relaunch, but never
change Acceptance, commands, dependency meaning, approvals, or evidence.

To evaluate ceremony, record available handoffs, interruptions, repeated checks, repair cycles, and unique
confirmed findings in existing final reports. Timing is optional observed data—not a completion gate or a new
telemetry requirement.

Useful standalone prompts:

```text
> Conceptualize this product idea before planning
> Get perspectives on this architecture decision
> Empirically test this API assumption within a bounded disposable probe
> Review this PR: owner/repo#42
> Review my code
> Audit the auth-system feature
> Spike and fix this regression
> Establish this project's testing workflow for browser E2E
> Add test coverage for this behavior using the approved testing workflow
> Polish this repository README
> Prepare a release
> Document this codebase
```

### Interactive walkthrough (explicit invocation only)

`walk-me-through` is standalone, read-only teaching for practical ownership, not a lifecycle stage or an automatic follow-up. It uses evidence-grounded explanations and compact ASCII diagrams to clarify behavior, decisions, risks, and where changes would begin.

Invoke it explicitly in Claude Code, replacing `<target>` with a feature, PR, release, or code change:

```text
/super-developer:walk-me-through <target>
```

---

## Plugin Structure and Checks

- `skills/`: entrypoints and action-specific worker contracts.
- `references/`: shared policy owners; callers load them at the relevant action instead of copying their rules.
- `assets/`: deterministic helpers and local regression tests.
- `.claude-plugin/plugin.json`: plugin manifest.

Run the local suite from the repository root:

```bash
python3 -m unittest discover -s plugins/super-developer/assets/tests
```

`test_sliceproof.py` and `test_semgrep_rules.py` exercise helper behavior. `test_skill_prompts.py`,
`test_lifecycle_design_guidance.py`, and `test_conceptualize_capture_policy.py` guard prompt structure/policy;
these static guards do not measure live agent behavior. The skill-authoring audit checks budgets and reference links.

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
| Conversation-first discovery | Write settled understanding when durability matters; do not create artifacts merely because a skill ran. |
| Slice-first planning | Existing Slices remain durable product/design authority while control-plane authority stays out of Slice text. |
| Progressive disclosure | `SKILL.md` files route and guard; detailed contracts load only at action points. |
| Package delegation | Work packages are large enough for useful sub-agent execution and small enough for focused result-file confirmation. |
| Independent verification | Package reports, review-code readiness, and audit each protect a different gate. None replaces another. |
| Read-only dashboards | Status views show mechanical signals without mutating lifecycle state or claiming semantic completion. |
| Explicit git authority | Feature pushes, target merges, cleanup, and release operations happen only under their named contracts. |

---

## Upstream Attribution

The design, review, and skill-authoring guidance adapts Matt Pocock's skills repository at pinned commit
`84fdeffd12f2ee307994d1eb6feb48173b6e0502`, licensed under the MIT License:

- https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/codebase-design/SKILL.md
- https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/engineering/code-review/SKILL.md
- https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/writing-for-agents/SKILL.md
- https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/skills/productivity/writing-for-agents/SKILL-MECHANICS.md
- https://raw.githubusercontent.com/mattpocock/skills/84fdeffd12f2ee307994d1eb6feb48173b6e0502/LICENSE

---

## License

MIT
