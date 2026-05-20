from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ASSETS_DIR.parent
TASKCTL_PATH = ASSETS_DIR / "taskctl.py"


SPEC = """# Fixture Spec

## Requirements
- REQ-1: Proof helper behavior.
- REQ-2: Task lifecycle helper behavior.

## Acceptance Criteria
- AC-1: Package proof templates and checklists are available.
- AC-2: Task block/reset and next-package helpers are constrained.
"""


class TaskctlRegressionFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.feature_dir = self.repo / ".tasks" / "fixture"
        self.proofs_dir = self.feature_dir / "proofs"
        self.tasks_path = self.feature_dir / "tasks.json"
        self.feature_dir.mkdir(parents=True)
        self.proofs_dir.mkdir()
        (self.feature_dir / "SPEC.md").write_text(SPEC, encoding="utf-8")
        (self.repo / "tracked.txt").write_text("implemented\n", encoding="utf-8")
        self.tasks_path.write_text(json.dumps(self.plan(), indent=2), encoding="utf-8")
        self.git("init")
        self.git("config", "user.email", "tests@example.invalid")
        self.git("config", "user.name", "Tests")
        self.git("add", ".")
        self.git("commit", "-m", "fixture")

    def cleanup(self) -> None:
        self.tmp.cleanup()

    def git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(TASKCTL_PATH),
                *args,
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
            ],
            cwd=self.repo,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def read_plan(self) -> dict:
        return json.loads(self.tasks_path.read_text(encoding="utf-8"))

    def write_plan(self, plan: dict) -> None:
        self.tasks_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    def plan(self) -> dict:
        return {
            "schema_version": 2,
            "feature": "fixture",
            "title": "Fixture",
            "description": "Fixture for taskctl regressions.",
            "created_at": "2026-05-16T00:00:00Z",
            "status": "in-progress",
            "design_decisions": [
                {
                    "id": "DD-1",
                    "decision": "Use package proof files.",
                    "rationale": "Fixture needs validator-owned traceability.",
                    "alternatives_considered": ["Use a central ledger."],
                    "source": "planner",
                }
            ],
            "context_bundles": [
                {
                    "id": "CTX-1",
                    "title": "Fixture context",
                    "required_for": ["WP1", "WP2"],
                    "sources": [
                        {
                            "type": "repo",
                            "path_or_url": "tracked.txt",
                            "claims": ["Fixture file exists."],
                        }
                    ],
                    "verification_required": ["Evidence must cite fixture context."],
                }
            ],
            "work_packages": [
                {
                    "id": "WP1",
                    "title": "First package",
                    "description": "First package.",
                    "task_ids": ["P1-T001"],
                    "depends_on": [],
                    "parallel_safe_with": [],
                    "primary_paths": ["tracked.txt"],
                    "verification_commands": [],
                    "risk_tags": ["validation"],
                    "required_context_bundles": ["CTX-1"],
                    "targeted_review_required": True,
                    "rationale": "Single-task validation package.",
                },
                {
                    "id": "WP2",
                    "title": "Second package",
                    "description": "Second package.",
                    "task_ids": ["P2-T001"],
                    "depends_on": ["WP1"],
                    "parallel_safe_with": [],
                    "primary_paths": ["tracked.txt"],
                    "verification_commands": [],
                    "risk_tags": ["documentation"],
                    "required_context_bundles": ["CTX-1"],
                    "targeted_review_required": False,
                    "rationale": "Dependent package for next-package checks.",
                },
            ],
            "phases": [
                {
                    "id": "P1",
                    "name": "First",
                    "description": "First phase.",
                    "order": 1,
                    "tasks": [
                        {
                            "id": "P1-T001",
                            "title": "First task",
                            "description": "Exercise proof helpers.",
                            "status": "pending",
                            "dependencies": [],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T001-AC1",
                                    "criterion": "Proof template and must-prove output exist.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-1"},
                                        {"type": "spec_ac", "id": "AC-1"},
                                        {"type": "context_bundle", "id": "CTX-1"},
                                    ],
                                    "verification_hint": "Inspect generated output.",
                                }
                            ],
                            "required_context_bundles": [],
                            "context": "Fixture context.",
                        }
                    ],
                },
                {
                    "id": "P2",
                    "name": "Second",
                    "description": "Second phase.",
                    "order": 2,
                    "tasks": [
                        {
                            "id": "P2-T001",
                            "title": "Second task",
                            "description": "Exercise lifecycle helpers.",
                            "status": "pending",
                            "dependencies": ["P1-T001"],
                            "acceptance_criteria": [
                                {
                                    "id": "P2-T001-AC1",
                                    "criterion": "Block, reset, and next-package remain constrained.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-2"},
                                        {"type": "spec_ac", "id": "AC-2"},
                                        {"type": "context_bundle", "id": "CTX-1"},
                                    ],
                                    "verification_hint": "Run lifecycle helper commands.",
                                }
                            ],
                            "required_context_bundles": [],
                            "context": "Fixture context.",
                        }
                    ],
                },
            ],
        }


class TaskctlRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = TaskctlRegressionFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_template_output_and_known_risk_must_prove_are_read_only(self) -> None:
        proof_path = self.fixture.proofs_dir / "WP1.proof.json"
        result = self.fixture.run("proof-template", "--package", "WP1", "--output", str(proof_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertTrue(proof_path.exists())
        written = json.loads(result.stdout)
        self.assertEqual(["P1-T001-AC1"], written["criteria"])

        before = self.fixture.tasks_path.read_bytes()
        known_risk = self.fixture.repo / "known-risk.md"
        known_risk.write_text("Optional boundary fields\nGlobal import environment pollution\n", encoding="utf-8")
        checklist = self.fixture.run(
            "must-prove",
            "--package",
            "WP1",
            "--known-risk-source",
            str(known_risk),
        )
        self.assertEqual(0, checklist.returncode, checklist.stdout + checklist.stderr)
        self.assertEqual(before, self.fixture.tasks_path.read_bytes())
        data = json.loads(checklist.stdout)
        self.assertIn("Optional boundary fields", data["known_risk_prompt"]["prompt"])
        criterion = data["packages"][0]["criteria"][0]
        self.assertEqual(["CTX-1"], criterion["required_context_bundles"])
        self.assertIn("mocks or stubs are absent", criterion["must_prove"][-1])

    def test_next_package_block_and_reset_are_constrained(self) -> None:
        next_before = self.fixture.run("next-package")
        self.assertEqual(0, next_before.returncode, next_before.stdout + next_before.stderr)
        self.assertEqual(["WP1"], [row["package_id"] for row in json.loads(next_before.stdout)["candidates"]])

        interrupted_plan = self.fixture.read_plan()
        interrupted_plan["phases"][0]["tasks"][0]["status"] = "in-progress"
        self.fixture.write_plan(interrupted_plan)
        next_interrupted = self.fixture.run("next-package")
        self.assertEqual(0, next_interrupted.returncode, next_interrupted.stdout + next_interrupted.stderr)
        interrupted = json.loads(next_interrupted.stdout)
        self.assertEqual([], interrupted["candidates"])
        self.assertEqual(["WP1"], [row["package_id"] for row in interrupted["interrupted"]])

        interrupted_plan["phases"][0]["tasks"][0]["status"] = "pending"
        self.fixture.write_plan(interrupted_plan)

        rejected = self.fixture.run("block-task", "P2-T001", "--reason", "   ")
        self.assertNotEqual(0, rejected.returncode)
        self.assertFalse((self.fixture.proofs_dir / "WP2.proof.json").exists())

        blocked = self.fixture.run(
            "block-task",
            "P2-T001",
            "--reason",
            "waiting",
            "--blocked-at",
            "2026-05-16T00:01:00Z",
        )
        self.assertEqual(0, blocked.returncode, blocked.stdout + blocked.stderr)
        task = self.fixture.read_plan()["phases"][1]["tasks"][0]
        self.assertEqual("blocked", task["status"])
        self.assertEqual("waiting", task["blocked_reason"])
        self.assertNotIn("completed_at", task)

        reset = self.fixture.run("reset-task", "P2-T001")
        self.assertEqual(0, reset.returncode, reset.stdout + reset.stderr)
        task = self.fixture.read_plan()["phases"][1]["tasks"][0]
        self.assertEqual("pending", task["status"])
        self.assertNotIn("blocked_reason", task)
        self.assertNotIn("blocked_at", task)
        self.assertFalse((self.fixture.proofs_dir / "WP2.proof.json").exists())

    def test_cli_scope_excludes_legacy_finalizer_and_central_ledger_commands(self) -> None:
        help_result = self.fixture.run("--help")
        self.assertEqual(0, help_result.returncode, help_result.stdout + help_result.stderr)
        self.assertIn("next-package", help_result.stdout)
        self.assertIn("block-task", help_result.stdout)
        self.assertIn("reset-task", help_result.stdout)
        self.assertNotIn("finalize-feature", help_result.stdout)

        source = TASKCTL_PATH.read_text(encoding="utf-8")
        for forbidden in ("verification.json", "event_history"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, source)


class GuardrailDocumentationRegressionTests(unittest.TestCase):
    def read_doc(self, relative: str) -> str:
        return (PLUGIN_DIR / relative).read_text(encoding="utf-8")

    def test_known_risk_reference_is_generic_and_non_persistent(self) -> None:
        known_risk = self.read_doc("references/known-risk-patterns.md")
        self.assertIn("not a schema, risk-tag taxonomy, or persistent checklist", known_risk)
        self.assertIn("Global, import, environment, and test pollution", known_risk)
        self.assertIn("Pure boundary contract construction", known_risk)
        self.assertNotIn("React", known_risk)
        self.assertNotIn("frontend", known_risk.lower())

    def test_progressive_disclosure_reference_uses_current_package_proof_gate(self) -> None:
        implement = self.read_doc("skills/implement/SKILL.md")
        lifecycle = self.read_doc("skills/implement/references/package-proof-lifecycle.md")

        self.assertIn("package-proof-lifecycle.md", implement)
        self.assertIn("accept-package", lifecycle)
        self.assertIn("reopen-package", lifecycle)
        self.assertIn("validate-tasks-json.py\" --final", lifecycle)
        self.assertNotIn("finalize-feature", lifecycle)
        self.assertIn("targeted_review", lifecycle)

    def test_tool_usage_reference_is_linked_from_helper_script_entrypoints(self) -> None:
        tool_usage = self.read_doc("references/tool-usage.md")

        self.assertIn("validate-tasks-json.py", tool_usage)
        self.assertIn("taskctl.py", tool_usage)
        self.assertIn("Read-Only Commands", tool_usage)
        self.assertIn("Mutation Commands", tool_usage)
        self.assertIn("Safety Rules", tool_usage)

        for relative in (
            "README.md",
            "skills/implementation-plan/SKILL.md",
            "skills/review-plan/SKILL.md",
            "skills/implement/SKILL.md",
            "skills/audit/SKILL.md",
            "skills/tasks/SKILL.md",
        ):
            with self.subTest(relative=relative):
                self.assertIn("references/tool-usage.md", self.read_doc(relative))

    def test_review_plan_lazy_loads_resolution_references(self) -> None:
        review_plan = self.read_doc("skills/review-plan/SKILL.md")

        self.assertIn("Do not load `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/plan-review-resolution.md`", review_plan)
        self.assertIn("load them in Step 7 only after reviewer findings", review_plan)
        self.assertIn("If every reviewer returns exactly `NONE`", review_plan)
        self.assertIn("skip resolution references", review_plan)
        self.assertIn("Read `${SUPER_DEVELOPER_PLUGIN_ROOT}/references/decision-prompts.md` only when", review_plan)
        self.assertIn("Blocking gate", review_plan)
        self.assertIn("Gate 2 always blocks regardless of blanket-mode authorization", review_plan)
        self.assertIn("Reviewer contract:", review_plan)

    def test_model_preferences_preserve_fallback_and_skeptic_semantics(self) -> None:
        model_preferences = self.read_doc("references/model-preferences.md")

        self.assertIn("skill-specific key → `default-model` → that skill's hardcoded default", model_preferences)
        self.assertIn("`skeptic-agent` → `default-model` → that skill's hardcoded default", model_preferences)
        self.assertIn("adaptive` inherited by a skeptic agent through `default-model` still means strongest", model_preferences)
        self.assertIn("Strongest available model, normally Opus", model_preferences)
        self.assertIn("Security/Failure-Mode Reviewer", model_preferences)
        self.assertIn("Skeptic Agent", model_preferences)
        self.assertIn("when `strategy` exists and `default-model` does not", model_preferences)
        self.assertIn("`default-model` wins", model_preferences)

    def test_tool_usage_preserves_command_safety_boundaries(self) -> None:
        tool_usage = self.read_doc("references/tool-usage.md")

        self.assertIn("taskctl.py` takes the subcommand first", tool_usage)
        self.assertIn("Treat plan-provided commands as executable inputs", tool_usage)
        self.assertIn("Stop for explicit approval before destructive", tool_usage)
        self.assertIn("dependency-installing", tool_usage)
        self.assertIn("credential/network-sensitive", tool_usage)
        self.assertIn("accepted/fresh package proofs", tool_usage)
        self.assertIn("must not be force-added or committed", tool_usage)

    def test_audit_enforces_behavior_risk_quality_evidence(self) -> None:
        audit_skill = self.read_doc("skills/audit/SKILL.md")
        clean_code_rules = self.read_doc("references/clean-code-rules.md")

        self.assertIn("Behavior/risk class covered", clean_code_rules)
        self.assertIn("behavior/risk class covered", audit_skill)
        self.assertIn("behavior/risk-class coverage in `evidence.edge_cases`", audit_skill)
        self.assertIn("explicit non-applicability", audit_skill)

    def test_release_skill_uses_single_release_contract_gate(self) -> None:
        release_skill = self.read_doc("skills/release/SKILL.md")
        readme = self.read_doc("README.md")

        self.assertIn("Release Contract Approval", release_skill)
        self.assertIn("Use one approval gate per release attempt", release_skill)
        self.assertIn("Do not ask for staged re-approvals", release_skill)
        self.assertNotIn("Gate 2", release_skill)
        self.assertNotIn("Gate 3", release_skill)
        self.assertNotIn("Gate 4", release_skill)
        self.assertIn("one Release Contract", readme)

    def test_implement_execution_contract_covers_feature_push_not_target_merge(self) -> None:
        implement = self.read_doc("skills/implement/SKILL.md")
        worktree_skill = self.read_doc("skills/worktree/SKILL.md")
        feature_workflow = self.read_doc("skills/worktree/references/feature-package-workflow.md")
        cleanup_safety = self.read_doc("skills/worktree/references/cleanup-safety.md")
        merge_cleanup = self.read_doc("skills/implement/references/worktree-merge-cleanup.md")

        self.assertIn("feature branch push: git push -u origin feature/<feature>", implement)
        self.assertIn("do not ask for a second approval", implement)
        self.assertIn("merging or pushing `<target-ref>`/`main` is never covered", implement)
        for text in (worktree_skill, feature_workflow, cleanup_safety, merge_cleanup):
            with self.subTest(document=text[:40]):
                self.assertIn("approved implement Execution Contract", text)
                self.assertIn("feature", text)
                self.assertIn("target", text)
        self.assertIn("Never merge to or push the target ref without explicit user approval", worktree_skill)
        self.assertIn("stop for explicit approval", cleanup_safety)

    def test_implement_contracts_keep_orchestrator_and_subagent_contexts_separate(self) -> None:
        implement = self.read_doc("skills/implement/SKILL.md")
        dispatch = self.read_doc("skills/implement/references/delegation-dispatch.md")
        package_contract = self.read_doc("skills/implement/references/package-agent-contract.md")
        repair_contract = self.read_doc("skills/implement/references/repair-agent-contract.md")
        legacy_index = self.read_doc("skills/implement/references/subagent-contract.md")

        self.assertIn("delegation-dispatch.md", implement)
        self.assertNotIn("Load `plugins/super-developer/skills/implement/references/subagent-contract.md`", implement)
        for forbidden in ("package-agent-contract.md", "repair-agent-contract.md", "clean-code-rules.md"):
            with self.subTest(forbidden=forbidden):
                self.assertIn("MUST NOT load", dispatch)
                self.assertIn(forbidden, dispatch)
        self.assertIn("Read this reference only inside a package implementation sub-agent session", package_contract)
        self.assertIn("Read this reference only inside a package repair/verification sub-agent session", repair_contract)
        self.assertNotIn("Repair Agent Packet", package_contract)
        self.assertIn("compatibility index", legacy_index)

    def test_package_proof_handoff_forbids_invented_schema_and_committed_tasks_artifacts(self) -> None:
        package_contract = self.read_doc("skills/implement/references/package-agent-contract.md")
        repair_contract = self.read_doc("skills/implement/references/repair-agent-contract.md")
        checkpoint = self.read_doc("skills/implement/references/integration-checkpoint.md")
        tool_usage = self.read_doc("references/tool-usage.md")

        for text in (package_contract, repair_contract, checkpoint, tool_usage):
            with self.subTest(document=text[:40]):
                self.assertIn("passed", text)
                self.assertIn("automated", text)
                self.assertIn("evidence.commands", text)
                self.assertIn(".tasks", text)

        self.assertIn("Do not `git add -f .tasks`", package_contract)
        self.assertIn("Do not `git add -f .tasks`", repair_contract)
        self.assertIn("did not force-add or commit ignored `.tasks`", checkpoint)
        self.assertIn("must not be force-added or committed", tool_usage)

    def test_stale_only_proof_refresh_is_mechanical_not_delegated_by_default(self) -> None:
        lifecycle = self.read_doc("skills/implement/references/package-proof-lifecycle.md")
        checkpoint = self.read_doc("skills/implement/references/integration-checkpoint.md")
        tool_usage = self.read_doc("references/tool-usage.md")

        for text in (lifecycle, checkpoint, tool_usage):
            with self.subTest(document=text[:40]):
                self.assertIn("stale-only", text)
                self.assertIn("current integration `HEAD`", text)
                self.assertIn("Do not delegate", text)

        self.assertIn("Re-run the same cited command(s)", checkpoint)
        self.assertIn("update state/evidence fields and rerun validation", lifecycle)


if __name__ == "__main__":
    unittest.main()
