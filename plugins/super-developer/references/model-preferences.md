# Local Preferences
## Boundary
This reference governs developer-local preference resolution before a skill delegates or spawns
agents. Model resolution never authorizes inline execution; callers must still dispatch the
resolved role/skill as a fresh sub-agent or Skill-tool invocation.
## Canonical Primary Root
Before resolving the preferences path, establish the canonical primary Git root. Run from any primary or linked
worktree; do not substitute the current directory or `git rev-parse --show-toplevel`, which may name a linked
worktree:
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
```
Stop on any failure.
## Local File
Path: `$PROJECT_ROOT/.superdeveloper/preferences.yml`
Create the parent directory and file when missing with the full first-run defaults:
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
Keep `$PROJECT_ROOT/.superdeveloper/preferences.yml` gitignored; it is developer-local preference, not
repository state. It is the only supported preferences file. Before reading or creating it, validate the exact path
without following an unsafe redirect:
```bash
PREFERENCES_REL=.superdeveloper/preferences.yml
PREFERENCES_DIR="$PROJECT_ROOT/.superdeveloper"
PREFERENCES_PATH="$PROJECT_ROOT/$PREFERENCES_REL"
export PREFERENCES_DIR PREFERENCES_PATH
test -d "$PROJECT_ROOT"; test ! -L "$PROJECT_ROOT"
if
  git -C "$PROJECT_ROOT" ls-files --error-unmatch -- "$PREFERENCES_REL" >/dev/null 2>&1
then
  printf 'Refusing index-tracked developer preferences: %s\n' "$PREFERENCES_REL" >&2
  exit 1
else
  INDEX_STATUS=$?
  test "$INDEX_STATUS" -eq 1 || exit 1
fi
if test -e "$PREFERENCES_DIR" || test -L "$PREFERENCES_DIR"; then
  test -d "$PREFERENCES_DIR"; test ! -L "$PREFERENCES_DIR"
fi
if test -e "$PREFERENCES_PATH" || test -L "$PREFERENCES_PATH"; then
  test -f "$PREFERENCES_PATH"; test ! -L "$PREFERENCES_PATH"
else
  test ! -L "$PREFERENCES_PATH"
  git -C "$PROJECT_ROOT" check-ignore --quiet --no-index -- "$PREFERENCES_REL"
  if test ! -e "$PREFERENCES_DIR" && test ! -L "$PREFERENCES_DIR"; then
    mkdir "$PREFERENCES_DIR"
  fi
  # Repeat every mutable-path proof immediately before the exclusive create.
  if
    git -C "$PROJECT_ROOT" ls-files --error-unmatch -- "$PREFERENCES_REL" >/dev/null 2>&1
  then
    printf 'Refusing index-tracked developer preferences: %s\n' "$PREFERENCES_REL" >&2
    exit 1
  else
    INDEX_STATUS=$?
    test "$INDEX_STATUS" -eq 1 || exit 1
  fi
  test -d "$PREFERENCES_DIR"; test ! -L "$PREFERENCES_DIR"
  test ! -e "$PREFERENCES_PATH"; test ! -L "$PREFERENCES_PATH"
  git -C "$PROJECT_ROOT" check-ignore --quiet --no-index -- "$PREFERENCES_REL"
  python3 <<'PY'
import os, stat
data = """models:
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
""".encode()
parent_path = os.environ["PREFERENCES_DIR"]  # Parent of shell-validated PREFERENCES_PATH.
target_path = os.environ["PREFERENCES_PATH"]; basename = "preferences.yml"
def identity(item): return (item.st_dev, item.st_ino)
parent_before = os.stat(parent_path, follow_symlinks=False)
if not stat.S_ISDIR(parent_before.st_mode): raise NotADirectoryError(parent_path)
dir_fd = os.open(parent_path, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW); created_identity = None
def rollback_created():
    try:
        current = os.stat(basename, dir_fd=dir_fd, follow_symlinks=False)
    except FileNotFoundError:
        return
    if identity(current) != created_identity:
        raise RuntimeError("refusing to unlink a replacement preferences file")
    os.unlink(basename, dir_fd=dir_fd)
    os.fsync(dir_fd)
try:
    parent_open = os.fstat(dir_fd)
    if identity(parent_open) != identity(parent_before):
        raise RuntimeError("preferences directory changed during validation")
    fd = os.open(
        basename,  # Final component of shell-validated PREFERENCES_PATH.
        os.O_CREAT | os.O_EXCL | os.O_WRONLY | os.O_NOFOLLOW,
        0o600,
        dir_fd=dir_fd,
    )
    try:
        created_identity = identity(os.fstat(fd))
        remaining = memoryview(data)
        while remaining:
            written = os.write(fd, remaining)
            if written <= 0:
                raise OSError("preferences write made no progress")
            remaining = remaining[written:]
        os.fsync(fd)
    finally:
        os.close(fd)
    os.fsync(dir_fd)
    parent_after = os.stat(parent_path, follow_symlinks=False)
    target_after = os.stat(target_path, follow_symlinks=False)
    if identity(parent_after) != identity(parent_open) or identity(target_after) != created_identity:
        raise RuntimeError("preferences path changed during creation")
except BaseException:
    if created_identity is not None:
        try:
            rollback_created()
        except FileNotFoundError:
            pass
        except BaseException as rollback_error:
            raise RuntimeError("preferences creation failed and owned rollback could not complete") from rollback_error
    raise
finally:
    os.close(dir_fd)
PY
fi
```
Stop on any failure. The index probe treats only Git's documented status `1` as absence; index presence or any
other status fails closed before a preferences read or creation. An existing path may be read only when it is a
regular, non-symlink file under the validated regular, non-symlink parent. First-run creation repeats the exact
index-absence, parent/target type, target-absence, and ignore proofs immediately before an exclusive, non-overwriting
create relative to an opened `O_DIRECTORY | O_NOFOLLOW` parent descriptor. Python fsyncs and closes the created
file, then re-resolves the canonical parent and target and compares both identities with the opened directory and
created inode. On mismatch or failure it unlinks only when the retained descriptor's basename still identifies the
inode this operation created, fsyncs the directory, closes resources, and fails; it refuses to unlink an observed
replacement. This closes parent-rename races through the final identity check and owned rollback. Without external
coordination, stdlib cannot atomically prevent a rename after that check or a basename swap between rollback's
identity proof and unlink. Stop on any detected path change or rollback failure; never claim creation succeeded in
those cases. Also stop on a symlink, changed/non-directory parent, non-regular target, ignore failure, or collision.
This exact canonical-root file is a narrow developer-local exception; it authorizes no index change.
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
1. Establish the canonical primary root with the procedure above, validate the preferences path as specified, then
   read the existing regular file; when missing, perform the authorized first-run safety proofs and create it
   exclusively with the full defaults above.
2. Resolve role value from `models.<role>` (including `models.design-preflight`) → `models.default-model` → hardcoded `inherit`.
3. Interpret value: `inherit` omits model, `adaptive` applies role behavior, any other value is
   passed directly.
For Semgrep key meanings, local policy files, and cache/network boundaries, load `semgrep.md` only
at the Semgrep action point.
