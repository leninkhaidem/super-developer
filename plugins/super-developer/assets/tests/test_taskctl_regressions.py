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
            "conceptualize": {"index": ".planning/fixture/index.md"},
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
                    "conceptualize_slices": [{"path": ".planning/fixture/slices/validation.md", "focus": "First package only."}],
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
                    "conceptualize_slices": [],
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

    def test_conceptualize_docs_keep_index_minimal_and_slices_optional(self) -> None:
        skill = self.read_doc("skills/conceptualize/SKILL.md")
        index = self.read_doc("skills/conceptualize/references/workspace-index.md")
        slice_template = self.read_doc("skills/conceptualize/references/slice-template.md")
        readme = self.read_doc("README.md")

        for required in (
            "minimal `index.md` entry point",
            "Treat `index.md` as an entry point, not a transcript",
            "Context-Boundary Checkpoints",
            "Prefer no workspace content change over low-value documentation",
            "Create or update Slices only when one concern becomes independently useful",
        ):
            with self.subTest(required=required):
                self.assertIn(required, skill)

        for required in (
            "entry point, not a conversation transcript",
            "Do not use the Index for simple conversation capture",
            "Do not update the Index merely because a question was asked",
            "Prefer no content change over low-value documentation",
        ):
            with self.subTest(required=required):
                self.assertIn(required, index)

        for required in (
            "Slices are optional handoff artifacts, not normal conversation notes",
            "If a concise Index bullet is sufficient, do not create a Slice",
            "Do not create or update Slices for simple conversations",
        ):
            with self.subTest(required=required):
                self.assertIn(required, slice_template)

        self.assertIn("minimal Conceptualize Index + optional Slices", readme)
        self.assertIn("Simple conversation and intermediate reasoning stay out of the workspace", readme)

    def test_review_plan_conceptualize_semantic_review_is_lazy_and_trust_bounded(self) -> None:
        review_plan = self.read_doc("skills/review-plan/SKILL.md")
        rubrics = self.read_doc("references/plan-review-rubrics.md")
        conceptualize_review = self.read_doc("references/plan-review-conceptualize.md")
        authority = self.read_doc("references/conceptualize-slice-authority.md")

        self.assertIn("plan-review-conceptualize.md", review_plan)
        self.assertIn("Conceptualize semantic-review guidance", review_plan)
        self.assertIn("path safety/existence, workspace confinement", review_plan)
        self.assertIn("apply `plan-review-conceptualize.md`", rubrics)

        for required in (
            "Compact Reviewer Checklist",
            "validated Slices are authoritative product-requirement inputs",
            "hard Slice requirements and material commitments",
            "not only the `## Projection Candidates` section",
            "package assignment conflicts",
            "prompt-injection/control-plane risk",
            "locked implementation baseline artifacts",
            "${SUPER_DEVELOPER_PLUGIN_ROOT}/references/conceptualize-slice-authority.md",
        ):
            with self.subTest(required=required):
                self.assertIn(required, conceptualize_review)

        for canonical_detail in (
            "repo-relative POSIX paths",
            "`.planning/<concept-slug>/index.md`",
            "realpath/symlink resolution",
            "symlinked workspace roots",
            "Do not read unsafe candidates",
            "Review, Audit, and Proof Fail-Closed Matrix",
        ):
            with self.subTest(canonical_detail=canonical_detail):
                self.assertIn(canonical_detail, authority)

        self.assertNotIn("untrusted background evidence", conceptualize_review)
        self.assertNotIn("promoted into `SPEC.md`", conceptualize_review)

    def test_model_preferences_default_to_inherit_and_keep_adaptive_opt_in(self) -> None:
        model_preferences = self.read_doc("references/model-preferences.md")
        examples = self.read_doc("references/model-preferences-examples.md")
        implement = self.read_doc("skills/implement/SKILL.md")
        review_plan = self.read_doc("skills/review-plan/SKILL.md")
        review_code = self.read_doc("skills/review-code/SKILL.md")
        compact_preferences = " ".join(model_preferences.split())

        self.assertIn("default-model: inherit", model_preferences)
        self.assertIn("create it with `default-model: inherit`", compact_preferences)
        self.assertIn("matches having no preferences file", compact_preferences)
        self.assertIn("Use `adaptive` only when the local preference file explicitly opts", compact_preferences)
        self.assertIn("| `implement` | `inherit` |", model_preferences)
        self.assertIn("| `review-plan` | `inherit` |", model_preferences)
        self.assertIn("| `review-code` | `inherit` |", model_preferences)

        self.assertIn("Default inherit behavior", examples)
        self.assertIn("default-model: inherit", examples)
        self.assertIn("Explicit role-aware behavior", examples)
        self.assertIn("default-model: adaptive", examples)

        for skill_text in (implement, review_plan, review_code):
            with self.subTest(skill_text=skill_text[:40]):
                self.assertIn("Hardcoded default: `inherit`", skill_text)
        self.assertIn("`adaptive` must come from the local preference file", implement)
        self.assertIn("`adaptive` must come from the local preference file", review_plan)

    def test_design_preflight_resolves_existing_model_preferences(self) -> None:
        implementation_plan = self.read_doc("skills/implementation-plan/SKILL.md")
        design_preflight = self.read_doc("references/design-preflight.md")

        for text in (implementation_plan, design_preflight):
            with self.subTest(document=text[:40]):
                self.assertIn("resolve model preferences", text)
                self.assertIn("`review-plan` key", text)
                self.assertIn("`skeptic-agent` key", text)
                self.assertIn("resolved value is `inherit`", text)
                self.assertIn("omit the model parameter", text)
                self.assertIn("`adaptive`", text)
                self.assertIn("model name", text)

        self.assertIn("If a resolved value is `inherit`, omit the model parameter", implementation_plan)
        self.assertIn("If the resolved value is `inherit`, omit the model parameter", design_preflight)
        self.assertIn("if it is `adaptive`, apply the role's existing adaptive behavior", implementation_plan)
        self.assertIn("If the resolved value is `adaptive`, use the same role interpretation", design_preflight)
        self.assertIn("if it is a model name, pass that model name directly", implementation_plan)
        self.assertIn("If the resolved value is a model name, pass that exact model name", design_preflight)
        self.assertIn("Do not introduce an implementation-plan or preflight-specific model key", implementation_plan)
        self.assertIn("Do not add or document a Design Preflight, `implementation-plan`, or other new model-preference key", design_preflight)
        self.assertIn("Model preference: <resolved `review-plan` or `skeptic-agent` value", design_preflight)

    def test_parallel_work_package_guidance_prefers_safe_useful_waves(self) -> None:
        work_packages = self.read_doc("references/work-packages.md")
        authoring = self.read_doc("skills/implementation-plan/references/tasks-json-authoring.md")
        validation = self.read_doc("skills/implementation-plan/references/validation-checklist.md")
        dispatch = self.read_doc("skills/implement/references/package-dispatch.md")

        self.assertIn("largest safe useful wave", work_packages)
        self.assertIn("prefer a safe useful parallel wave", work_packages)
        self.assertIn("does not mean maximizing sub-agent count", work_packages)
        self.assertIn("When overlap is ambiguous", work_packages)
        self.assertIn("combine or serialize packages", work_packages)

        self.assertIn("Perform an explicit parallelism pass", authoring)
        self.assertIn("Prefer the largest safe useful parallel wave", authoring)
        self.assertIn("Do not split coherent work merely", authoring)
        self.assertIn("Artificial parallelism is absent", validation)
        self.assertIn("preferred safe useful parallel waves", validation)

        self.assertIn("Collect all externally actionable packages, then choose the largest safe useful batch", dispatch)
        self.assertIn("Do not maximize sub-agent count", dispatch)
        self.assertIn("Avoid unnecessary serialization", dispatch)
        self.assertIn("share a contract, API, schema, config surface, files, ambiguous impact", dispatch)

    def test_parallel_package_review_guidance_is_state_bound_and_invalidated(self) -> None:
        work_packages = self.read_doc("references/work-packages.md")
        checkpoint = self.read_doc("skills/implement/references/integration-checkpoint.md")

        for text in (work_packages, checkpoint):
            with self.subTest(document=text[:40]):
                self.assertIn("same concrete stable integration state", text)
                self.assertIn("review scopes are independent", text)
                self.assertIn("repair mutation", text)
                self.assertIn("invalidate or refresh", text)
                self.assertIn("targeted-review receipts", text)

        self.assertIn("same integration `HEAD`", checkpoint)
        self.assertIn("live repair/mutation stream", checkpoint)
        self.assertIn("uncertain impact fails closed", checkpoint)

    def test_parallelism_change_preserves_command_safety_and_schema_boundaries(self) -> None:
        work_packages = self.read_doc("references/work-packages.md")
        authoring = self.read_doc("skills/implementation-plan/references/tasks-json-authoring.md")
        validation = self.read_doc("skills/implementation-plan/references/validation-checklist.md")
        implement = self.read_doc("skills/implement/SKILL.md")
        implementation_plan = self.read_doc("skills/implementation-plan/SKILL.md")
        design_preflight = self.read_doc("references/design-preflight.md")
        validator = self.read_doc("assets/validate-tasks-json.py")

        for text in (work_packages, authoring):
            with self.subTest(command_safety_document=text[:40]):
                self.assertIn("Treat `verification_commands` as executable inputs", text)
                self.assertIn("explicit", text)
                self.assertIn("approval", text)
        self.assertIn("Command-safety approval rule", implement)
        self.assertIn("Treat plan verification commands as executable inputs", implement)

        self.assertIn("Do not add new schema fields", authoring)
        self.assertIn("encoded in existing schema fields", validation)
        self.assertIn("Do not introduce an implementation-plan or preflight-specific model key", implementation_plan)
        self.assertIn("Do not add or document a Design Preflight, `implementation-plan`, or other new model-preference key", design_preflight)
        for forbidden in (
            '"wave"',
            "'wave'",
            '"batch"',
            "'batch'",
            '"serial_rationale"',
            "'serial_rationale'",
            "model-preferences",
            "default-model",
            "skeptic-agent",
        ):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, validator)

    def test_model_preferences_preserve_fallback_and_skeptic_semantics(self) -> None:
        model_preferences = self.read_doc("references/model-preferences.md")

        self.assertIn("skill-specific key → `default-model` → that skill's hardcoded default", model_preferences)
        self.assertIn("`skeptic-agent` → `default-model` → that skill's hardcoded default", model_preferences)
        self.assertIn(
            "adaptive` inherited by a skeptic agent through `default-model` still means strongest",
            " ".join(model_preferences.split()),
        )
        self.assertIn("Strongest available model, normally Opus", model_preferences)
        self.assertIn("Security/Failure-Mode Reviewer", model_preferences)
        self.assertIn("Skeptic Agent", model_preferences)
        compact_model_preferences = " ".join(model_preferences.split())
        self.assertIn("`strategy` is treated as `default-model` only when `default-model` is absent", compact_model_preferences)
        self.assertIn("`default-model` wins", compact_model_preferences)

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
        audit_contract = self.read_doc("skills/audit/references/audit-subagent-contract.md")
        clean_code_rules = self.read_doc("references/clean-code-rules.md")

        self.assertIn("Behavior/risk class covered", clean_code_rules)
        self.assertIn("`references/audit-subagent-contract.md`", audit_skill)
        self.assertNotIn("skills/audit/references/audit-subagent-contract.md", audit_skill)
        self.assertIn("behavior/risk class", audit_contract)
        self.assertIn("behavior/risk-class coverage in `evidence.edge_cases`", clean_code_rules)
        self.assertIn("explicit non-applicability", audit_contract)

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

    def test_implement_dispatch_passes_conceptualize_context_safely_to_subagents(self) -> None:
        implement = self.read_doc("skills/implement/SKILL.md")
        dispatch = self.read_doc("skills/implement/references/delegation-dispatch.md")
        package_contract = self.read_doc("skills/implement/references/package-agent-contract.md")
        repair_contract = self.read_doc("skills/implement/references/repair-agent-contract.md")

        self.assertIn("Conceptualize context: <validated index path and assigned slice paths/focus, or none>", implement)
        self.assertIn("Conceptualize path screening", implement)
        self.assertIn("## Conceptualize Path Screening", dispatch)
        for required in (
            "repo-relative and shaped as `.planning/<concept-slug>/index.md`",
            "reject absolute paths",
            "same workspace root",
            "symlinked workspace roots",
            "realpath/symlink escape",
            "Pass only validated read-only Conceptualize entries",
            "Do not create generated per-package Conceptualize packet files",
            "top-level index path, assigned slice paths, optional slice focus",
            "safe resolved read paths",
            "prompt-injection/control-plane directives",
            "Slice plan defects",
        ):
            with self.subTest(required=required):
                self.assertIn(required, dispatch)

        for contract in (package_contract, repair_contract):
            with self.subTest(contract=contract[:40]):
                self.assertIn("read-only Conceptualize planning paths", contract)
                self.assertIn("must not be edited", contract)
                self.assertIn("authoritative product-requirement context", contract)
                self.assertIn("projected plan artifacts", contract)
                self.assertIn("Slice plan defect", contract)
                self.assertIn("cannot override system/developer instructions", contract)
                self.assertNotIn("untrusted background evidence", contract)

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

    def test_stale_only_proof_refresh_is_canonicalized(self) -> None:
        lifecycle = self.read_doc("skills/implement/references/package-proof-lifecycle.md")
        checkpoint = self.read_doc("skills/implement/references/integration-checkpoint.md")
        tool_usage = self.read_doc("references/tool-usage.md")

        for phrase in ("stale-only", "current integration `HEAD`", "Do not delegate"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, lifecycle)

        for text in (checkpoint, tool_usage):
            with self.subTest(document=text[:40]):
                self.assertIn("package-proof-lifecycle.md", text)
                self.assertIn("stale-only", text)

        self.assertNotIn("Re-run the same cited command(s)", checkpoint)
        self.assertIn("update state/evidence fields and rerun validation", lifecycle)


if __name__ == "__main__":
    unittest.main()
