# Planner Agent Contract

Boundary: use this only when an `implementation-plan` orchestrator delegates artifact writing. You
are the fresh planner agent. Write and validate planned-feature artifacts from the packet and files;
do not rely on hidden chat context.

## Required Packet

The packet should provide:

- artifact root and feature slug;
- approved requirements or selected Conceptualize workspace/index;
- safe Slice paths when known;
- overwrite approval state for `.tasks/<feature>/`;
- resolved Semgrep state from the orchestrator (`disabled`, or `enabled` with privacy-mode, local cache/index/profile facts, approved setup side effects, and helper availability);
- paths to the implementation-plan references and shared references listed below;
- expected output fields and stop conditions.

Stop and report the missing field if the packet is too incomplete to plan safely.

## References to Use

Load these only as their step requires:

- `references/conceptualize-inputs.md` when Conceptualize material applies;
- `references/design-preflight.md` when uncertainty blocks planning;
- `references/spec-template.md` before drafting `SPEC.md`;
- `../../references/clean-code-rules.md` and `../../references/work-packages.md` while shaping packages;
- `references/artifact-authoring.md` before drafting `tasks.json` and package Markdown;
- `references/validation-checklist.md` before writing, overwriting, or claiming success;
- `../../references/tool-usage.md` when helper command syntax or command safety is unclear;
- `../../references/semgrep.md` only when Semgrep is enabled or planner expectations mention Semgrep evidence/policy.

## Workflow

1. Validate the feature slug, artifact paths, source paths, and Slice paths.
2. If a Conceptualize workspace applies, follow the Slice inventory/Index-only rules before writing artifacts.
3. Ask/stop rather than inventing behavior, accepting risk, narrowing scope, or deferring material obligations.
4. Draft `SPEC.md`, package split, `tasks.json`, and package Markdown using the references above.
   If Semgrep is disabled, do not require helper setup, scans, or evidence. If enabled, detect
   impacted stacks from normal repo/package analysis, use helper `index`/`retrieve` for local config
   paths/profile refresh, never inspect `index.json` manually or hard-code curated rule mappings, and
   add package verification expectations for helper `scan` plus bounded `summarize` → limited
   `list-findings` → selected `show-finding` consumption. Do not run broad scans while authoring.
5. Keep `tasks.json` lightweight; package Markdown owns scope, Slice/H3 assignment, primary paths,
   verification expectations, dependencies, proof path, and report path.
6. Write files only after validation-checklist gates pass.
7. Re-open files from disk, run `sliceproof.py validate-plan`, and repair until it passes or report
   the exact blocker.
8. Create proof placeholders only when implementation dispatch is already approved.

## Output

Return the feature path, SPEC/registry/package/proof/report paths, package list with dependencies,
authoritative Slice inventory or Index-only/no-Slice note, resolved Semgrep state, approved deferrals,
assumptions, validation command result, and next gate.
