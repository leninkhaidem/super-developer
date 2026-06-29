# Planner Agent Contract

Boundary: use this only when an `implementation-plan` orchestrator delegates artifact writing. You
are the fresh planner agent. Write and validate planned-feature artifacts from the packet and files;
do not rely on hidden chat context.

## Required Packet

The packet should provide:

- artifact root, code root, artifact ref, resolved feature/artifact slug, and any approved slug
  rename/migration metadata;
- approved requirements or selected Conceptualize workspace/index;
- safe Conceptualize workspace, Index, and Slice paths relative to the artifact root when known;
- overwrite approval state for `.tasks/<feature>/` under the artifact root;
- resolved Semgrep state from the orchestrator (`disabled`, or `enabled` with privacy-mode, local cache/index/profile facts, approved setup side effects, and helper availability);
- paths to the implementation-plan references and shared references listed below, resolved from the
  code root/plugin tree;
- expected output fields and stop conditions.

Stop and report the missing field if the packet is too incomplete to plan safely.

## References to Use

Load these only as their step requires:

- `../../references/artifact-store.md` when artifact-root/code-root semantics or slug mapping matter;
- `references/conceptualize-inputs.md` when Conceptualize material applies;
- `references/design-preflight.md` when uncertainty blocks planning;
- `references/spec-template.md` before drafting `SPEC.md`;
- `../../references/clean-code-rules.md` and `../../references/work-packages.md` while shaping packages;
- `references/artifact-authoring.md` before drafting `tasks.json` and package Markdown;
- `references/validation-checklist.md` before writing, overwriting, or claiming success;
- `../../references/tool-usage.md` when helper command syntax or command safety is unclear;
- `../../references/semgrep.md` only when Semgrep is enabled or planner expectations mention Semgrep evidence/policy.

## Workflow

1. Validate the feature slug, artifact root/ref, code root, artifact paths, source paths, and Slice paths.
2. If a Conceptualize workspace applies, follow the Slice inventory/Index-only rules before writing
   artifacts. Treat the Conceptualize slug as the default feature/artifact slug; stop before writing
   `.tasks/<different-feature>` unless approved migration metadata is in the packet.
3. Ask/stop rather than inventing behavior, accepting risk, narrowing scope, or deferring material obligations.
4. Draft `SPEC.md`, package split, `tasks.json`, and package Markdown using the references above.
   Preserve exact interface/forbidden-behavior obligations; seed obvious package-specific risk expectations as deliverable-matrix `VE-<n>` row sources (interactive UI, retry/fail-closed, trigger precedence, lifecycle/restart/reaper, cache invalidation, model/default precedence, generated defaults, state pollution when applicable); and state that planner seeds do not limit verifier discovery.
   If Semgrep is disabled, do not require helper setup, scans, or evidence. If enabled, detect
   impacted stacks from normal repo/package analysis, use helper `index`/`retrieve` for local config
   paths/profile refresh, never inspect `index.json` manually or hard-code curated rule mappings, and
   add package verification expectations for `python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan ...`
   plus bounded `summarize` → limited `list-findings` → selected `show-finding` consumption
   (target plus expected summary digest for excerpts). Do
   not run broad scans or raw direct `semgrep` scans while authoring.
5. Keep `tasks.json` lightweight; package Markdown owns scope, Slice/H3 assignment, primary paths,
   verification expectations, dependencies, proof path, and report path.
6. Write files under the artifact root only after validation-checklist gates pass; code references stay
   code-root-relative and the artifact worktree need not contain plugin/source files.
7. Re-open files from disk, then from the code root run `sliceproof.py validate-plan` with explicit
   `--artifact-root <artifact-root> --code-root <code-root>`; repair until it passes or report the blocker.
8. Create proof placeholders only when implementation dispatch is already approved.

## Output

Return artifact root/ref, code root, feature path, SPEC/registry/package/proof/report paths, package
list with dependencies, authoritative Slice inventory or Index-only/no-Slice note, resolved Semgrep
state, approved deferrals, assumptions, validation command result, and next gate.
