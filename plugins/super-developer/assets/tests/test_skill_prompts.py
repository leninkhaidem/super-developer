from __future__ import annotations

import re
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PLUGIN_ROOT.parents[1]
CANONICAL_SCAN = 'python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan'
STALE_PREF_PATH = ".superdeveloper/model-preferences.yml"
CURRENT_PREF_PATH = ".superdeveloper/preferences.yml"


def read_repo(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def prompt_surface_paths() -> list[Path]:
    paths = [REPO_ROOT / "README.md", PLUGIN_ROOT / "README.md"]
    paths.extend(sorted((PLUGIN_ROOT / "references").glob("*.md")))
    paths.extend(sorted((PLUGIN_ROOT / "skills").glob("**/*.md")))
    return paths


def context_window(text: str, needle: str, radius: int = 120) -> str:
    index = text.find(needle)
    if index < 0:
        return ""
    start = max(0, index - radius)
    end = min(len(text), index + len(needle) + radius)
    return text[start:end].lower()


class SkillPromptSurfaceTests(unittest.TestCase):
    def test_readmes_document_optional_local_semgrep_lifecycle_without_history(self) -> None:
        root_text = read_repo("README.md")
        for needle in [
            CURRENT_PREF_PATH,
            "disabled by default",
            "clone",
            "git pull --ff-only",
            "shipped helper",
            ".tasks/<feature>/semgrep/",
            "advisory",
            "read-only",
        ]:
            self.assertIn(needle, root_text)
        self.assertNotIn(STALE_PREF_PATH, root_text)

        plugin_text = read_repo("plugins/super-developer/README.md")
        for needle in [
            CURRENT_PREF_PATH,
            ".superdeveloper/semgrep/excluded-rules.yml",
            ".superdeveloper/semgrep/local-rules.yml",
            ".superdeveloper/semgrep/stack-profile.yml",
            "${SUPER_DEVELOPER_PLUGIN_ROOT}/.cache/semgrep-rules/community",
            "clone",
            "git pull --ff-only",
            "disabled by default",
            CANONICAL_SCAN,
            "raw direct `semgrep` scans",
            "summarize",
            "list-findings",
            "show-finding",
            "--expected-summary-digest",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep.json",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep-summary.json",
            ".tasks/<feature>/semgrep/integration.semgrep.json",
            ".tasks/<feature>/semgrep/integration.semgrep-summary.json",
            "raw digest",
            "summary digest",
            "advisory",
            "read-only",
        ]:
            self.assertIn(needle, plugin_text)
        self.assertNotIn(STALE_PREF_PATH, plugin_text)
        self.assertNotIn("--config auto", plugin_text)

    def test_action_point_references_require_wrapper_scan_and_forbid_raw_direct_semgrep(self) -> None:
        action_point_paths = [
            "plugins/super-developer/README.md",
            "plugins/super-developer/references/semgrep.md",
            "plugins/super-developer/references/tool-usage.md",
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md",
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md",
            "plugins/super-developer/skills/implement/references/execution-contract.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/skills/implement/references/package-integration-gates.md",
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/skills/review-code/references/pipeline-report.md",
        ]
        for rel in action_point_paths:
            with self.subTest(path=rel):
                self.assertIn(CANONICAL_SCAN, read_repo(rel))
        for rel in ["plugins/super-developer/README.md", "plugins/super-developer/references/semgrep.md"]:
            with self.subTest(path=rel, option="expected-summary-digest"):
                self.assertIn("--expected-summary-digest", read_repo(rel))

        raw_direct_command = re.compile(r"(?im)(?:^|[`\\s])semgrep\\s+(?:scan|ci)\\b")
        forbidden_helper_internals = ["--config auto", "--metrics=off", "--disable-version-check"]
        for path in prompt_surface_paths():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            self.assertIsNone(raw_direct_command.search(text), rel)
            for token in forbidden_helper_internals:
                self.assertNotIn(token, text, rel)

    def test_preference_path_contract_is_current_and_terse(self) -> None:
        current_path_surfaces = [
            "README.md",
            "CHANGELOG.md",
            "plugins/super-developer/README.md",
            "plugins/super-developer/references/model-preferences.md",
            "plugins/super-developer/references/semgrep.md",
            "plugins/super-developer/skills/conceptualize/SKILL.md",
            "plugins/super-developer/skills/conceptualize/references/final-handoff.md",
            "plugins/super-developer/skills/implementation-plan/SKILL.md",
        ]
        for rel in current_path_surfaces:
            self.assertIn(CURRENT_PREF_PATH, read_repo(rel), rel)

        no_history_surfaces = [
            "README.md",
            "CHANGELOG.md",
            "plugins/super-developer/README.md",
            "plugins/super-developer/references/semgrep.md",
            "plugins/super-developer/skills/conceptualize/SKILL.md",
            "plugins/super-developer/skills/implementation-plan/SKILL.md",
        ]
        for rel in no_history_surfaces:
            self.assertNotIn(STALE_PREF_PATH, read_repo(rel), rel)

        model_preferences = read_repo("plugins/super-developer/references/model-preferences.md")
        self.assertNotIn(STALE_PREF_PATH, model_preferences)
        self.assertNotIn("resolve/create", read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md"))

    def test_conceptualize_handoff_resolves_semgrep_before_plan_skill(self) -> None:
        conceptualize = read_repo("plugins/super-developer/skills/conceptualize/SKILL.md")
        transition = "Before invoking `implementation-plan` from a Conceptualize handoff"
        self.assertIn(transition, conceptualize)
        self.assertIn("parent/main planning", conceptualize)
        self.assertIn(CURRENT_PREF_PATH, conceptualize)
        self.assertIn("Semgrep opt-in/setup", conceptualize)
        self.assertIn("pass the resolved Semgrep state", conceptualize)
        self.assertNotIn("dispatch `implementation-plan` via Skill tool/fresh sub-agent", conceptualize)

        handoff = read_repo("plugins/super-developer/skills/conceptualize/references/final-handoff.md")
        self.assertIn("parent/main", handoff)
        self.assertIn(CURRENT_PREF_PATH, handoff)
        self.assertIn("Semgrep opt-in/setup", handoff)
        self.assertIn("before invoking `implementation-plan`", handoff)

        implementation_plan = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        self.assertIn("do not reopen opt-in", implementation_plan)
        self.assertIn("Only when no resolved Semgrep state is supplied", implementation_plan)
        self.assertIn("treat this as\n  direct invocation", implementation_plan)

    def test_obsolete_or_unsafe_terms_are_only_negative_guidance(self) -> None:
        for path in prompt_surface_paths():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            if STALE_PREF_PATH in text:
                self.fail(f"{rel}: greenfield harness must not reference legacy {STALE_PREF_PATH}")
            for token in [".superdeveloper/semgrep-policy.yml", "local-rule-files", "local-rules-path"]:
                if token in text:
                    window = context_window(text, token)
                    self.assertRegex(window, r"\b(do not|no|without|reject|forbid|forbidden|never)\b", f"{rel}: {token}")
            for line in text.splitlines():
                lowered = line.lower()
                if "semgrep" in lowered and "fix-all" in lowered:
                    self.assertRegex(lowered, r"\b(not|no|without|unless|advisory|bounded)\b", f"{rel}: {line}")
                if "semgrep" in lowered and "automatic" in lowered and "blocker" in lowered:
                    self.assertRegex(lowered, r"\b(not|no|without|unless)\b", f"{rel}: {line}")

    def test_semgrep_prompt_detail_stays_progressively_disclosed(self) -> None:
        skill_paths = [
            PLUGIN_ROOT / "skills" / "conceptualize" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "implementation-plan" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "implement" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "review-code" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "audit" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "skill-authoring" / "SKILL.md",
        ]
        eager_forbidden = [
            "semgrep-rules.git",
            ".cache/semgrep-rules/community",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep.json",
            CANONICAL_SCAN,
            "show-finding --",
            "list-findings --",
        ]
        for path in skill_paths:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            self.assertLessEqual(len(text.splitlines()), 150, rel)
            for token in eager_forbidden:
                self.assertNotIn(token, text, rel)

        semgrep_reference = PLUGIN_ROOT / "references" / "semgrep.md"
        text = semgrep_reference.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 150)
        self.assertLessEqual(len(text.split()), 900)
        self.assertIn("Load it only when resolving Semgrep state", text)
        self.assertNotIn("rules inventory", text.lower().replace("rule inventory", ""))

    def test_helper_user_facing_summaries_are_bounded_and_not_workflow_jargon(self) -> None:
        source = (PLUGIN_ROOT / "assets" / "semgrep_rules.py").read_text(encoding="utf-8")
        self.assertIn("Semgrep scan complete: findings=", source)
        self.assertIn("SUMMARY_TOP_N", source)
        self.assertIn("LIST_LIMIT_MAX", source)
        self.assertIn("semgrep_severity_is_advisory", source)
        summary_region = source[source.index("def _build_summary") : source.index("def _write_summary")]
        for workflow_word in ["proof", "package verification", "Slice", "planning", "staging"]:
            self.assertNotIn(workflow_word, summary_region)

    def test_diagnose_and_fix_recommends_one_route_and_reviewed_delivery(self) -> None:
        text = read_repo("plugins/super-developer/skills/diagnose-and-fix/SKILL.md")
        compact = " ".join(text.split())
        for needle in [
            "exactly one recommended route",
            "stop/missing-info",
            "localized `worktree` fix",
            "`implementation-plan`",
            "named diagnostic spike",
            "approve the recommended route",
            "shared `../../references/model-preferences.md`",
            "resolved model/policy",
            "After any delivered localized fix, invoke `review-code`",
            "push `origin bugfix/<name>`",
            "unless the user explicitly excluded remote side effects",
        ]:
            self.assertIn(" ".join(needle.split()), compact)
        self.assertNotIn("Ask for one explicit approval choice", text)

    def test_worktree_bugfix_push_and_target_merge_skip_are_explicit(self) -> None:
        bugfix = read_repo("plugins/super-developer/skills/worktree/references/bugfix-hotfix-workflow.md")
        for forbidden in [
            "fix, commit, verify",
            "fix, commit, verify the focused bug scenario",
            "fix, commit, verify the production failure path",
        ]:
            self.assertNotIn(forbidden, bugfix.lower())
        for needle in [
            "git push -u origin bugfix/<name>",
            "after verification and clean `review-code`",
            "Commit bugfix changes only after verification and CLEAN `review-code`/approved delivery",
            "Commit hotfix branch changes only after verification, CLEAN `review-code`, and approved delivery",
            "not approval to merge into or push `<base-branch>`, `feature/<feature>`, or",
            "git worktree add .worktrees/hotfix-<name> -b hotfix/<name> <base-branch>",
            "git worktree add .worktrees/hotfix-merge-<name> <base-branch>",
            "git push origin <base-branch>",
            "git merge <base-branch> --no-edit",
            "`main` may be an example value for `<base-branch>`",
            "remote side effects",
        ]:
            self.assertIn(needle, bugfix)
        for line in bugfix.splitlines():
            if re.search(r"\bmain\b", line):
                self.assertIn("`main` may be an example value for `<base-branch>`", line)

        cleanup = read_repo("plugins/super-developer/skills/worktree/references/cleanup-safety.md")
        for needle in [
            "git merge-base --is-ancestor feature/<feature> <target-ref>",
            "already merged; skip the target merge",
            "git merge --no-ff feature/<feature>",
            "Production hotfix worktrees stay until the hotfix merge to `<base-branch>`",
            "<worktree-on-base-branch>",
        ]:
            self.assertIn(needle, cleanup)
        self.assertNotIn("hotfix merge to `main`", cleanup)
        self.assertNotIn("<worktree-on-main>", cleanup)

    def test_interface_contract_thread_is_present_and_consistent(self) -> None:
        authority = read_repo("plugins/super-developer/references/conceptualize-slice-authority.md")
        for needle in [
            "**Interface contract**",
            "Forbidden behaviors",
            "ambiguous",
            "contradicted",
            "over-broad",
        ]:
            self.assertIn(needle, authority, "conceptualize-slice-authority.md")

        for rel in [
            "plugins/super-developer/skills/conceptualize/references/slice-template.md",
            "plugins/super-developer/skills/implementation-plan/references/conceptualize-inputs.md",
            "plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md",
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/skills/implement/references/repair-agent-contract.md",
            "plugins/super-developer/skills/audit/references/audit-subagent-contract.md",
        ]:
            self.assertIn("Interface contract", read_repo(rel), rel)

        self.assertIn("Forbidden behaviors", read_repo("plugins/super-developer/skills/implement/references/package-verification.md"))
        self.assertIn("[INTERFACE-EXACTNESS]", read_repo("plugins/super-developer/skills/audit/references/audit-subagent-contract.md"))
        self.assertIn("interface-contract seams", read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md"))

    def test_package_verification_deliverable_matrix_contract_is_durable(self) -> None:
        contract_rel = "plugins/super-developer/references/package-verification-report.md"
        contract = read_repo(contract_rel)
        verifier = read_repo("plugins/super-developer/skills/implement/references/package-verification.md")
        artifacts = read_repo("plugins/super-developer/references/slice-first-artifacts.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")
        risks = read_repo("plugins/super-developer/references/known-risk-patterns.md")

        for rel in [
            contract_rel,
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/references/slice-first-artifacts.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/references/known-risk-patterns.md",
        ]:
            self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)

        for token in [
            "### Deliverable Completeness Matrix",
            "Source ID",
            "Row Type",
            "Deliverable",
            "Evidence Type",
            "Evidence Refs",
            "Exactness / Risk Disposition",
            "Verdict",
            "delivered",
            "missing",
            "partial",
            "contradicted",
            "unverified",
        ]:
            self.assertIn(token, contract)

        for token in [
            "exact H3 ID",
            "VE-<n>",
            "RISK-<slug-or-n>",
            "verifier-selected",
            "planner seeds do not limit discovery",
            "non-applicable probes must not become checklist noise",
        ]:
            self.assertIn(token, contract)

        for token in [
            "Package Markdown Digest",
            "Proof Digest",
            "Assigned Slices",
            "Assigned Slice Digests",
            "Matrix Source Snapshot",
            "Worktree",
            "Git Ref",
            "Commit",
        ]:
            self.assertIn(token, contract)

        for token in [
            "code:<repo-relative-path>",
            "test:<repo-relative-path>",
            "static:<repo-relative-path>#section",
            "command:proof#Commands Run:<label>",
            "manual:scenario=<specific scenario>; observed=<specific result>",
            "unsafe, nonexistent, placeholder, fabricated, or structurally vague anchors",
        ]:
            self.assertIn(token, contract)

        for token in [
            "`### Slice Closure Review` and proof prose alone as completion blockers",
            "Helpers validate shape, row coverage, clean verdict state, bindings, and evidence-anchor structure only",
            "Package verifiers and final auditors judge semantic truthfulness and sufficiency",
        ]:
            self.assertIn(token, verifier)

        self.assertIn(contract_rel, verifier)
        self.assertIn(contract_rel, artifacts)
        self.assertIn(contract_rel, dispatch)
        self.assertIn("Required first reads", dispatch)
        self.assertIn("hidden chat context", dispatch)
        self.assertIn("deliverable completeness matrix", artifacts)
        self.assertIn("RISK-<...>", risks)
        self.assertIn("rationale/disposition", risks)

    def test_package_completion_helper_gates_done_unlock_merge_and_final_handoff(self) -> None:
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        command = 'python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete ".tasks/<feature>/tasks.json" --package <WP-ID>'

        self.assertIn("clean `validate-package-complete`", implement)
        self.assertIn(command, gates)
        self.assertIn(command, lifecycle)
        for text in [dispatch, lifecycle]:
            with self.subTest(surface=text[:40]):
                self.assertIn("fresh `PASS`", text)
                self.assertIn("clean `validate-package-complete`", text)
                self.assertIn("registry `done`", text)
                self.assertIn("proof rows", text)
        for needle in [
            "before accepting/merging as complete",
            "marking `done`",
            "unlocking dependents",
            "final readiness handoff",
            "mechanical signal only",
        ]:
            self.assertIn(needle, gates + lifecycle)
        self.assertIn("review-code readiness and final audit PASS", lifecycle)

    def test_planner_risk_seeding_preserves_verifier_discovery(self) -> None:
        artifact = read_repo("plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md")
        planner = read_repo("plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md")
        checklist = read_repo("plugins/super-developer/skills/implementation-plan/references/validation-checklist.md")
        packages = read_repo("plugins/super-developer/references/work-packages.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")

        for text in [artifact, planner, checklist, packages]:
            with self.subTest(surface=text[:40]):
                self.assertIn("VE-<n>", text)
                self.assertRegex(text, r"exact interfaces?|exact interface")
                self.assertIn("forbidden", text)
                for risk in [
                    "interactive UI",
                    "retry/fail-closed",
                    "trigger precedence",
                    "lifecycle/restart/reaper",
                    "cache invalidation",
                    "model/default precedence",
                    "generated defaults",
                    "state pollution",
                ]:
                    self.assertIn(risk, text)
        for text in [artifact, checklist, packages, dispatch]:
            with self.subTest(discovery=text[:40]):
                self.assertIn("do not limit verifier discovery", text)
                self.assertIn("changed code/diff", text)
                self.assertIn("known failure modes", text)
        self.assertIn("verifier-owned triggered risk selection", dispatch)

    def test_repair_freshness_uses_affected_surface_classification_and_proportional_reruns(self) -> None:
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")

        for text in [lifecycle, gates]:
            with self.subTest(surface=text[:40]):
                self.assertIn("affected-surface", text)
                self.assertIn("narrow", text)
                self.assertIn("bounded", text)
                self.assertIn("cannot be bounded", text)
                self.assertIn("delivered behavior", text)
                self.assertIn("evidence bindings", text)
                self.assertIn("contracts", text)
                self.assertIn("integration", text)
                self.assertRegex(text, r"safety/security/privacy/data")
                self.assertIn("source bindings", text)
                self.assertIn("validate-package-complete", text)
                self.assertIn("validate-proof", text)
                self.assertIn("package verification", text)
        for needle in [
            "package Markdown/digest",
            "assigned Slice source/digest",
            "matrix source snapshot",
            "matrix evidence anchors",
        ]:
            self.assertIn(needle, lifecycle)
        self.assertIn("matrix rows/evidence anchors", dispatch)
        self.assertIn("classified rerun scope", dispatch)

    def test_final_audit_consumes_matrices_as_reconciler_and_stack_backstop(self) -> None:
        audit_skill = read_repo("plugins/super-developer/skills/audit/SKILL.md")
        audit_contract = read_repo("plugins/super-developer/skills/audit/references/audit-subagent-contract.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        workflow = read_repo("plugins/super-developer/skills/worktree/references/feature-package-workflow.md")

        for token in [
            "bounded stack packet",
            "top integrated worktree/code state",
            "one or more related task/Slice artifact sets",
            "clean deliverable matrix",
            "validate-final",
        ]:
            self.assertIn(token, audit_skill)
        for token in [
            "deliverable-matrix reconciliation",
            "### Deliverable Completeness Matrix",
            "matrix source bindings",
            "evidence-anchor structure",
            "Matrix Reconciliation",
            "targeted skeptic backstop",
            "not a full second package verifier",
            "interface-bearing rows",
            "triggered risk rows",
            "global/cross-package seams",
            "stacked-feature obligations",
            "claims cheaply disprovable from code",
            "stale source bindings",
            "invalid evidence refs",
        ]:
            self.assertIn(token, audit_contract)
        for text in [gates, lifecycle, workflow]:
            with self.subTest(surface=text[:40]):
                self.assertIn("top integrated", text)
                self.assertIn("task/Slice artifact", text)
                self.assertRegex(text.lower(), r"do not audit .*follow-up")
                self.assertRegex(text.lower(), r"base feature|base/follow-up")
        self.assertIn("validate-package-complete", gates)
        self.assertIn("same top state", lifecycle)

    def test_review_code_uses_matrices_as_context_only_with_refresh_classification(self) -> None:
        review_skill = read_repo("plugins/super-developer/skills/review-code/SKILL.md")
        pipeline = read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md")

        for token in [
            "deliverable matrices are context only",
            "not a third deliverable-completeness gate",
            "proof/report invalidation",
            "invalidated matrix",
            "generic affected-surface impact classification",
        ]:
            self.assertIn(token, review_skill)
        for token in [
            "Use deliverable matrices as context only",
            "Do not own full deliverable completeness",
            "proof/report invalidation",
            "dirty matrix",
            "matrix rows/evidence anchors",
            "source bindings",
            "boundedness",
            "do not run full final gates solely because any new commit exists",
            "full matrix bodies",
            "proof/report transcripts",
            "separate completion ledgers",
        ]:
            self.assertIn(token, pipeline)

    def test_delivery_gate_prompt_changes_stay_progressively_disclosed(self) -> None:
        line_capped = [
            "plugins/super-developer/skills/audit/SKILL.md",
            "plugins/super-developer/skills/audit/references/audit-subagent-contract.md",
            "plugins/super-developer/skills/review-code/SKILL.md",
            "plugins/super-developer/skills/review-code/references/pipeline-report.md",
            "plugins/super-developer/skills/implement/SKILL.md",
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md",
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md",
            "plugins/super-developer/references/work-packages.md",
            "plugins/super-developer/references/package-lifecycle.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/skills/implement/references/package-integration-gates.md",
            "plugins/super-developer/skills/skill-authoring/SKILL.md",
            "plugins/super-developer/skills/skill-authoring/references/orchestrator-worker-contracts.md",
        ]
        for rel in line_capped:
            with self.subTest(path=rel):
                self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)

        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        self.assertNotIn("### Deliverable Completeness Matrix", implement)
        self.assertNotIn("Source ID | Row Type", implement)
        self.assertIn("invoke `review-code` and `audit` only", implement)
        self.assertIn("semantic truthfulness remains with package verification and final audit", gates)
        self.assertIn("Declare readiness only when package evidence, review-code readiness, and final audit PASS", gates)

        for rel in [
            "plugins/super-developer/skills/audit/SKILL.md",
            "plugins/super-developer/skills/review-code/SKILL.md",
        ]:
            text = read_repo(rel)
            self.assertNotIn("Source ID | Row Type", text, rel)
            self.assertNotIn("plugins/super-developer/skills/", text, rel)
        self.assertIn("Do not deep-link another skill's private references", read_repo("plugins/super-developer/skills/skill-authoring/SKILL.md"))


if __name__ == "__main__":
    unittest.main()
