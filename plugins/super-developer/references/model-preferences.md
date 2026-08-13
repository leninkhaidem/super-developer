# Local Preferences

## Boundary

This reference governs developer-local preference resolution before a skill delegates or spawns
agents. Model resolution never authorizes inline execution; callers must still dispatch the
resolved role/skill as a fresh sub-agent or Skill-tool invocation.

## Local File

Path: `$PROJECT_ROOT/.superdeveloper/preferences.yml`

Before reading or creating that file, resolve `$PROJECT_ROOT` with this NUL-safe primary-root
procedure (`git-common-dir` + first porcelain `worktree` record). `--show-toplevel`, cwd, and a
linked, package, or target worktree must not anchor the preferences path.

```bash
set -euo pipefail
COMMON_GIT_DIR="$(git rev-parse --path-format=absolute --git-common-dir)"
COMMON_GIT_DIR="$(cd "$COMMON_GIT_DIR" && pwd -P)"
PROJECT_ROOT=""
while IFS= read -r -d '' FIELD; do
  case "$FIELD" in
    "worktree "*) PROJECT_ROOT="${FIELD#worktree }"; break ;;
  esac
done < <(git --git-dir="$COMMON_GIT_DIR" worktree list --porcelain -z)
test -n "$PROJECT_ROOT"
PROJECT_ROOT="$(cd "$PROJECT_ROOT" && pwd -P)"
PRIMARY_GIT_DIR="$(git -C "$PROJECT_ROOT" rev-parse --path-format=absolute --git-dir)"
PRIMARY_GIT_DIR="$(cd "$PRIMARY_GIT_DIR" && pwd -P)"
test "$PRIMARY_GIT_DIR" = "$COMMON_GIT_DIR"
export PROJECT_ROOT
printf 'PROJECT_ROOT=%s\n' "$PROJECT_ROOT"
```

Stop on any failure. Create the parent directory and file when missing with the full first-run defaults:

```yaml
models:
  default-model: inherit
  implementation-plan: inherit
  design-preflight: adaptive
  implement: adaptive
  review-plan: adaptive
  review-code: inherit
  skeptic-agent: adaptive

semgrep:
  enabled: false
  privacy-mode: true
  rules-provider: plugin-community-cache
  project-policy-gate: skeptic
```

Keep `.superdeveloper/preferences.yml` gitignored; it is developer-local preference, not
repository state. It is the only supported preferences file. Create only that exact path; do not
create a preferences file under the current or linked worktree.

## Model Keys

Model preferences live under `models:`:

- `default-model` — fallback for every role.
- `implementation-plan` — delegated planning artifact writer.
- `design-preflight` — Design Preflight challenger sub-agents.
- `implement` — package implementation agents.
- `review-plan` — plan-review standard reviewers.
- `review-code` — code and specialist reviewers.
- `skeptic-agent` — adversarial reviewers across skills.

## Values

- `inherit` — omit model so the sub-agent inherits the orchestrator model.
- `adaptive` — use role-aware selection.
- `<model-name>` — pass the exact model name.

Adaptive defaults:

- `implementation-plan`: inherit unless local policy overrides.
- `design-preflight`: planning/challenge-aware selection, stronger for high-risk challenger lenses.
- `implement`: stronger model for complex/ambiguous packages; standard model for simple, patterned packages.
- `review-plan`: standard model.
- `review-code`: standard model.
- `skeptic-agent`: strongest available model.

## Resolution

1. Establish the canonical primary root, then read or create that exact file
   `$PROJECT_ROOT/.superdeveloper/preferences.yml` with the full defaults above when missing.
2. Resolve role value from `models.<role>` (including `models.design-preflight`) → `models.default-model` → hardcoded `inherit`.
3. Interpret value: `inherit` omits model, `adaptive` applies role behavior, any other value is
   passed directly.

For Semgrep key meanings, local policy files, and cache/network boundaries, load `semgrep.md` only
at the Semgrep action point.
