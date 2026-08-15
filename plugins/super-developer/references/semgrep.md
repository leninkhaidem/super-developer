# Semgrep Local Reference

## Boundary
This compact reference owns Super Developer's local Semgrep preference, cache, file-role, privacy,
and policy-authority contract. It is not a helper implementation manual, rule inventory, or prompt
bundle. Load it only when resolving Semgrep state, preparing helper commands, or checking Semgrep
evidence/policy surfaces.

## Preferences
The only supported local preferences file is `$PROJECT_ROOT/.superdeveloper/preferences.yml`.
Semgrep reads only the `semgrep:` section:

```yaml
semgrep:
  enabled: false
  privacy-mode: true
  rules-provider: plugin-community-cache
  project-policy-gate: skeptic
```

- `enabled: false` keeps ordinary workflows working without Semgrep, helper setup, or internet.
- `privacy-mode: true` means local-only scans, no telemetry, no version check, no registry/URL
  configs, and no cloud/AppSec/CI/Pro/secrets-validation modes.
- `rules-provider: plugin-community-cache` derives rules from the installed plugin cache only.
- `project-policy-gate: skeptic` gates local policy/rule writes through independent authority.

Unsupported preference files are ignored. Other preference sections are out of scope for this
reference. Do not add `local-rules-path`, `local-rule-files`, a project-local community clone path,
or persistent network-sync preferences.

## Local Files and Roles
Project-local files are developer-local/gitignored by default:
- `.superdeveloper/preferences.yml` — Semgrep kill switch/provider/gate.
- `.superdeveloper/semgrep/excluded-rules.yml` — compact command policy for excluding community
  rule IDs.
- `.superdeveloper/semgrep/local-rules.yml` — actual project-local Semgrep rules, included
  automatically when present.
- `.superdeveloper/semgrep/stack-profile.yml` — local lookup table from detected stacks to absolute
  Semgrep config paths returned by the helper.

Task-scoped evidence is local/uncommitted under `.tasks/<feature>/semgrep/`:
- `<WP-ID>.semgrep.json` and `<WP-ID>.semgrep-summary.json` for package scans.
- `integration.semgrep.json` and `integration.semgrep-summary.json` for optional integrated scans.
Raw JSON is evidence, not prompt context; consume it through bounded helper views. Result reports
cite raw path, raw digest, summary path, summary digest, scan scope, and concise finding/no-finding
summary when Semgrep is enabled or contracted. Evidence outside `.tasks/<feature>/semgrep/`,
unpaired stems, symlinks, traversal, or digest mismatches is stale/invalid.

## Shared Cache and Network Boundary
Community rules live under the installed plugin root, not the project:

```text
${SUPER_DEVELOPER_PLUGIN_ROOT}/.cache/semgrep-rules/community
${SUPER_DEVELOPER_PLUGIN_ROOT}/.cache/semgrep-rules/index.json
```

First opt-in may run exactly one user-approved network setup/update action: missing `community/`
uses `git clone https://github.com/semgrep/semgrep-rules.git <community>`; existing `community/`
uses `git pull --ff-only` inside it. Routine scans must not clone, pull, fetch registry configs, or
silently sync rules. If the plugin cache is not writable, stop and ask for an approved shared cache
alternative; do not fall back to a project-local clone. If `semgrep` is missing during approved
setup, ask before installing it with `uv tool install semgrep`; never install during scan execution.

## Helper Command Contract
The helper asset owns `index`, `retrieve`, `scan`, `summarize`, `list-findings`, and
`show-finding`. Agents must not run raw direct `semgrep` scans, manually inspect `index.json`,
hand-assemble Semgrep shell commands, or read raw Semgrep JSON wholesale.

Canonical package scan wrapper:

```bash
python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan \
  --profile ".superdeveloper/semgrep/stack-profile.yml" \
  --excluded-rules ".superdeveloper/semgrep/excluded-rules.yml" \
  --local-rules ".superdeveloper/semgrep/local-rules.yml" \
  --target "<package-worktree-or-scope>" \
  --json-output ".tasks/<feature>/semgrep/<WP-ID>.semgrep.json" \
  --summary-output ".tasks/<feature>/semgrep/<WP-ID>.semgrep-summary.json"
```

Integrated or affected-scope rerun scans use the same wrapper; change only the target and output
stem, for example `integration.semgrep.json` plus `integration.semgrep-summary.json`. The wrapper
enforces local config paths, the `privacy-mode` contract above, structured arguments, safe
excluded-rule expansion, and bounded summary creation.

Normal consumption order is `summarize`, then filtered/limited `list-findings`, then
`show-finding` only for selected stable local finding refs. Use `show-finding --context-lines 0`
for metadata-only. For code excerpts, pass `--target <scan-scope>` plus externally recorded
`--expected-summary-digest <summary_digest>`; the helper rejects missing/mismatched summary binding
or widened target context.

## Policy Semantics and Authority
`.superdeveloper/semgrep/excluded-rules.yml` is command policy, not a narrative triage log:

```yaml
excluded-rules:
  - id: dockerfile.security.last-user-is-root.last-user-is-root
    reason: "Project-specific false positive or accepted local exception."
    decided-by: skeptic
```

Only `id` changes command behavior. `reason` and `decided-by` are compact provenance. The helper
validates IDs and rejects empty values, shell flags, spaces, separators, URLs, or other command
injection shapes. Do not create `.superdeveloper/semgrep-policy.yml`.

`.superdeveloper/semgrep/local-rules.yml` is additive actual Semgrep YAML. A local rule with the
same ID does not reliably override a community rule; to replace or suppress a community rule, list
the community rule ID in `excluded-rules.yml` and optionally add a local replacement rule.

Policy/rule update authority:
- User explicit approval always authorizes local `excluded-rules.yml` or `local-rules.yml` updates.
- Package implementers may propose exclusions/local rules, but must not suppress their own findings directly.
- Independent package verifiers, review-code reviewers, or skeptics may recommend evidence-based updates.
- With `project-policy-gate: skeptic`, skeptic agreement satisfies the default gate and authorizes
  the main orchestrator write without another user prompt.
- The main orchestrator performs only mechanical, compact, local/gitignored writes after authority is satisfied.
- Audit is read-only and must not update Semgrep preferences, excluded rules, local rules, stack
  profiles, or scan outputs.
- Exclusions must not hide real introduced security/privacy risks; material risks require a fix,
  explicit risk acceptance, or a serious review finding.

## Stack Profile
`.superdeveloper/semgrep/stack-profile.yml` (defined above) is a path lookup table, not an evidence
or confidence report:

```yaml
version: 1
rules-index:
  community-rules-commit: "abc1234"
  index-path: "/abs/path/to/plugins/super-developer/.cache/semgrep-rules/index.json"
stacks:
  python:
    semgrep-configs:
      - "/abs/path/to/plugins/super-developer/.cache/semgrep-rules/community/python"
```

If paths disappear, the plugin moves, or the rules commit changes, rerun helper retrieval instead
of editing paths by hand.
