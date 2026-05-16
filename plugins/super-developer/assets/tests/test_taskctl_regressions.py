from __future__ import annotations

import ast
import contextlib
import copy
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1]
PLUGIN_DIR = ASSETS_DIR.parent
TASKCTL_PATH = ASSETS_DIR / "taskctl.py"
VALIDATOR_PATH = ASSETS_DIR / "validate-tasks-json.py"


def _load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to import {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


taskctl = _load_module(TASKCTL_PATH, "taskctl_under_test")
validator = taskctl.validator


class TaskctlFixture:
    def __init__(self, case: unittest.TestCase):
        self.case = case
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.feature_dir = self.root / ".tasks" / "fixture"
        self.tasks_path = self.feature_dir / "tasks.json"
        self.spec_path = self.feature_dir / "SPEC.md"
        self.proofs_dir = self.feature_dir / "proofs"
        self.proofs_dir.mkdir(parents=True)
        (self.root / "src").mkdir()
        (self.root / "src" / "implemented.txt").write_text("implemented\n", encoding="utf-8")
        self._git("init")
        self._git("config", "user.email", "taskctl-tests@example.invalid")
        self._git("config", "user.name", "Taskctl Tests")
        self.plan = self._plan()
        self.write_plan()
        self.spec_path.write_text(
            "# Fixture Spec\n\n"
            "## Requirements\n"
            "- REQ-1: Proof helper behavior.\n"
            "- REQ-2: Final completion gates.\n\n"
            "## Acceptance Criteria\n"
            "- AC-1: Package proof lifecycle works.\n"
            "- AC-2: Final completion remains gated.\n",
            encoding="utf-8",
        )
        self._git("add", ".")
        self._git("commit", "-m", "initial fixture")
        self.commit = self._git("rev-parse", "HEAD").stdout.strip()

    def cleanup(self) -> None:
        self.tmp.cleanup()

    def _git(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=self.root,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

    def _plan(self) -> dict:
        refs_1 = [{"type": "spec_req", "id": "REQ-1"}, {"type": "spec_ac", "id": "AC-1"}, {"type": "design_decision", "id": "DD-1"}]
        refs_2 = [{"type": "spec_req", "id": "REQ-2"}, {"type": "spec_ac", "id": "AC-2"}, {"type": "design_decision", "id": "DD-1"}]
        return {
            "schema_version": 2,
            "feature": "fixture",
            "title": "Fixture feature",
            "description": "Small valid task plan for taskctl regression coverage.",
            "created_at": "2026-05-16T00:00:00+00:00",
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
                        {"type": "repo", "path_or_url": "src/implemented.txt", "claims": ["Fixture code exists."]}
                    ],
                    "verification_required": ["Evidence must cite current fixture files."],
                },
                {
                    "id": "CTX-2",
                    "title": "Task-only fixture context",
                    "required_for": ["P1-T001"],
                    "sources": [
                        {"type": "repo", "path_or_url": "src/implemented.txt", "claims": ["Task-specific fixture context exists."]}
                    ],
                    "verification_required": ["Evidence must cite task-only fixture context when required."],
                },
            ],
            "work_packages": [
                {
                    "id": "WP1",
                    "title": "Proof package",
                    "description": "Package that requires targeted review.",
                    "task_ids": ["P1-T001"],
                    "depends_on": [],
                    "parallel_safe_with": [],
                    "primary_paths": ["src/implemented.txt"],
                    "verification_commands": ["python3 -m unittest discover plugins/super-developer/assets/tests"],
                    "risk_tags": ["validation"],
                    "required_context_bundles": ["CTX-1"],
                    "targeted_review_required": True,
                    "rationale": "Single-task package still needs targeted-review coverage.",
                },
                {
                    "id": "WP2",
                    "title": "Final package",
                    "description": "Package used for final completion gates.",
                    "task_ids": ["P2-T001"],
                    "depends_on": ["WP1"],
                    "parallel_safe_with": [],
                    "primary_paths": ["src/implemented.txt"],
                    "verification_commands": [],
                    "risk_tags": ["documentation"],
                    "required_context_bundles": ["CTX-1"],
                    "targeted_review_required": False,
                    "rationale": "Second package proves all-proof aggregation.",
                },
            ],
            "phases": [
                {
                    "id": "P1",
                    "name": "First phase",
                    "description": "Proof package phase.",
                    "order": 1,
                    "tasks": [
                        {
                            "id": "P1-T001",
                            "title": "Proof task",
                            "description": "Validate package proof behavior.",
                            "status": "pending",
                            "dependencies": [],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T001-AC1",
                                    "criterion": "Package proof validation and acceptance work.",
                                    "source_refs": refs_1,
                                    "verification_hint": "Cover proof success and rejection paths.",
                                }
                            ],
                            "required_context_bundles": ["CTX-2"],
                            "context": "Fixture task context.",
                        }
                    ],
                },
                {
                    "id": "P2",
                    "name": "Second phase",
                    "description": "Finalization phase.",
                    "order": 2,
                    "tasks": [
                        {
                            "id": "P2-T001",
                            "title": "Final task",
                            "description": "Validate final completion gating.",
                            "status": "pending",
                            "dependencies": ["P1-T001"],
                            "acceptance_criteria": [
                                {
                                    "id": "P2-T001-AC1",
                                    "criterion": "Final completion requires all proofs and final gates.",
                                    "source_refs": refs_2,
                                    "verification_hint": "Cover all-proof, review, audit, and status-bypass attempts.",
                                }
                            ],
                            "required_context_bundles": [],
                            "context": "Fixture task context.",
                        }
                    ],
                },
            ],
        }

    def write_plan(self) -> None:
        self.tasks_path.parent.mkdir(parents=True, exist_ok=True)
        self.tasks_path.write_text(json.dumps(self.plan, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    def read_plan(self) -> dict:
        return json.loads(self.tasks_path.read_text(encoding="utf-8"))

    def base_args(self) -> list[str]:
        return ["--tasks", str(self.tasks_path), "--worktree", str(self.root)]

    def run(self, *args: str) -> tuple[int, dict | None, str]:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = taskctl.main([*self.base_args(), *args])
        output = stdout.getvalue()
        data = json.loads(output) if output.strip() else None
        return code, data, stderr.getvalue()

    def valid_proof(self, package_id: str, *, include_targeted_review: bool = True) -> dict:
        proof = json.loads(self._command_json("proof-template", package_id))
        for entry in proof["entries"]:
            entry["status"] = "verified"
            entry["method"] = "static_inspection"
            entry["state"] = {
                "git_ref": "HEAD",
                "commit": self.commit,
                "worktree": str(self.root),
                "captured_at": "2026-05-16T00:01:00+00:00",
            }
            entry["evidence"] = {
                "files": ["src/implemented.txt"],
                "commands": [],
                "edge_cases": ["fixture edge case covered"],
                "context_bundles": ["CTX-1"],
                "mocks": "No mocks used.",
            }
            entry.pop("manual_evidence", None)
        package = next(package for package in self.plan["work_packages"] if package["id"] == package_id)
        proof["package_verification"] = {
            "commands": [
                {
                    "cwd": str(self.root),
                    "command": command,
                    "exit_code": 0,
                    "observed": f"Observed passing fixture command: {command}",
                }
                for command in package.get("verification_commands", [])
            ]
        }
        if proof.get("targeted_review") is not None and include_targeted_review:
            proof["targeted_review"] = {
                "status": "passed",
                "package_id": package_id,
                "scope": "targeted package review for current package state",
                "reviewed_at": "2026-05-16T00:02:00+00:00",
                "state": {"commit": self.commit, "git_ref": "HEAD", "worktree": str(self.root)},
                "findings": [],
                "approved_by": "fixture reviewer",
            }
        return proof

    def _command_json(self, *args: str) -> str:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(io.StringIO()):
            code = taskctl.main([*self.base_args(), *args])
        self.case.assertEqual(code, 0, stdout.getvalue())
        return stdout.getvalue()

    def write_proof(self, package_id: str, proof: dict) -> Path:
        path = self.proofs_dir / f"{package_id}.proof.json"
        path.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        return path

    def mark_all_tasks_done_manually(self) -> None:
        for phase in self.plan["phases"]:
            for task in phase["tasks"]:
                task["status"] = "done"
                task["completed_at"] = "2026-05-16T00:03:00+00:00"
        self.write_plan()

    def add_final_gates(self) -> None:
        self.plan = self.read_plan()
        self.plan["final_integration_review"] = {
            "status": "passed",
            "reviewed_at": "2026-05-16T00:04:00+00:00",
            "state": {"commit": self.commit, "git_ref": "HEAD", "worktree": str(self.root)},
        }
        self.plan["final_audit"] = {
            "status": "passed",
            "audited_at": "2026-05-16T00:05:00+00:00",
            "state": {"commit": self.commit, "git_ref": "HEAD", "worktree": str(self.root)},
        }
        self.write_plan()


class TaskctlRegressionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = TaskctlFixture(self)

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_proof_template_validate_all_summary_next_and_must_prove_are_deterministic(self) -> None:
        code, template, err = self.fixture.run("proof-template", "WP1")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(template["feature"], "fixture")
        self.assertEqual(template["package_id"], "WP1")
        self.assertEqual([entry["criterion_id"] for entry in template["entries"]], ["P1-T001-AC1"])
        self.assertEqual(template["entries"][0]["source_refs"], self.fixture.plan["phases"][0]["tasks"][0]["acceptance_criteria"][0]["source_refs"])
        self.assertEqual(template["targeted_review"]["status"], "pending")

        self.fixture.write_proof("WP1", self.fixture.valid_proof("WP1"))
        code, validated, err = self.fixture.run("validate-proof", "WP1")
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(validated["ok"])
        self.assertEqual(validated["criterion_ids"], ["P1-T001-AC1"])

        code, all_result, _ = self.fixture.run("validate-proofs")
        self.assertEqual(code, 1)
        self.assertFalse(all_result["ok"])
        self.assertTrue(any("missing proof file" in error for error in all_result["errors"]))
        self.fixture.write_proof("WP2", self.fixture.valid_proof("WP2"))
        code, all_result, err = self.fixture.run("validate-proofs")
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(all_result["ok"])
        self.assertEqual(all_result["criterion_ids"], ["P1-T001-AC1", "P2-T001-AC1"])

        before = self.fixture.tasks_path.read_bytes()
        code, summary, err = self.fixture.run("summary")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(before, self.fixture.tasks_path.read_bytes())
        self.assertEqual(summary["task_counts"], {"pending": 2})
        self.assertTrue(summary["packages"][0]["proof"]["ok"])

        code, next_package, err = self.fixture.run("next-package")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([row["id"] for row in next_package["candidates"]], ["WP1"])
        self.assertEqual(next_package["completed_packages"], [])

        known_risk = self.fixture.root / "known-risk.md"
        known_risk.write_text("Optional boundary fields\nGlobal import environment pollution\n", encoding="utf-8")
        code, checklist, err = self.fixture.run("must-prove", "WP1", "--known-risk-source", str(known_risk))
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(before, self.fixture.tasks_path.read_bytes())
        self.assertEqual([bundle["id"] for bundle in checklist["required_context_bundles"]], ["CTX-1", "CTX-2"])
        self.assertEqual(checklist["acceptance_criteria"][0]["required_context_bundles"], ["CTX-1", "CTX-2"])
        self.assertTrue(checklist["targeted_review_required"])
        self.assertIn("Optional boundary fields", checklist["known_risk_prompt"]["prompt"])
        self.assertIn("mocks/stubs are absent", checklist["acceptance_criteria"][0]["must_prove"][-1])

    def test_accept_package_requires_valid_proof_recorded_verification_and_targeted_review_then_updates_only_package_tasks(self) -> None:
        missing_review = self.fixture.valid_proof("WP1", include_targeted_review=False)
        missing_review["targeted_review"]["status"] = "pending"
        self.fixture.write_proof("WP1", missing_review)
        before = self.fixture.tasks_path.read_text(encoding="utf-8")
        code, data, err = self.fixture.run("accept-package", "WP1", "--completed-at", "2026-05-16T00:06:00+00:00")
        self.assertEqual(code, 2)
        self.assertIsNone(data)
        self.assertIn("targeted package review status is not passed", err)
        self.assertEqual(before, self.fixture.tasks_path.read_text(encoding="utf-8"))

        placeholder_command_evidence = self.fixture.valid_proof("WP1")
        for row in placeholder_command_evidence["package_verification"]["commands"]:
            row["cwd"] = "<worktree>"
            row["observed"] = "<observed output>"
        self.fixture.write_proof("WP1", placeholder_command_evidence)
        code, data, err = self.fixture.run("accept-package", "WP1", "--completed-at", "2026-05-16T00:06:00+00:00")
        self.assertEqual(code, 2)
        self.assertIsNone(data)
        self.assertIn("package verification command not recorded as passing", err)
        self.assertEqual(before, self.fixture.tasks_path.read_text(encoding="utf-8"))

        wrong_review_package = self.fixture.valid_proof("WP1")
        wrong_review_package["targeted_review"]["package_id"] = "WP2"
        self.fixture.write_proof("WP1", wrong_review_package)
        code, data, err = self.fixture.run("accept-package", "WP1", "--completed-at", "2026-05-16T00:06:00+00:00")
        self.assertEqual(code, 2)
        self.assertIsNone(data)
        self.assertIn("targeted package review package_id 'WP2' does not match 'WP1'", err)
        self.assertEqual(before, self.fixture.tasks_path.read_text(encoding="utf-8"))


        valid = self.fixture.valid_proof("WP1")
        self.fixture.write_proof("WP1", valid)
        code, accepted, err = self.fixture.run("accept-package", "WP1", "--completed-at", "2026-05-16T00:06:00+00:00")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(accepted["tasks"], ["P1-T001"])
        plan = self.fixture.read_plan()
        statuses = {task["id"]: task["status"] for phase in plan["phases"] for task in phase["tasks"]}
        self.assertEqual(statuses, {"P1-T001": "done", "P2-T001": "pending"})
        self.assertEqual(plan["status"], "in-progress")

        code, next_package, err = self.fixture.run("next-package")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual([row["id"] for row in next_package["candidates"]], ["WP2"])

    def test_proof_rejection_cases_do_not_mutate_plan(self) -> None:
        base = self.fixture.valid_proof("WP1")
        cases = {
            "missing": lambda p: p["entries"].clear(),
            "extra": lambda p: p["entries"].append(copy.deepcopy(self.fixture.valid_proof("WP2")["entries"][0])),
            "duplicate": lambda p: p["entries"].append(copy.deepcopy(p["entries"][0])),
            "wrong-package": lambda p: p.__setitem__("package_id", "WP2"),
            "failed": lambda p: p["entries"][0].__setitem__("status", "failed"),
            "blocked": lambda p: p["entries"][0].__setitem__("status", "blocked"),
            "source-ref-mismatch": lambda p: p["entries"][0].__setitem__("source_refs", [{"type": "spec_req", "id": "REQ-2"}]),
            "stale": lambda p: p["entries"][0]["state"].__setitem__("commit", "0000000000000000000000000000000000000000"),
        }
        original_plan = self.fixture.tasks_path.read_text(encoding="utf-8")
        for name, mutate in cases.items():
            with self.subTest(name=name):
                proof = copy.deepcopy(base)
                mutate(proof)
                self.fixture.write_proof("WP1", proof)
                code, result, _err = self.fixture.run("validate-proof", "WP1")
                self.assertEqual(code, 1)
                self.assertFalse(result["ok"])
                self.assertTrue(result["errors"])
                code, data, _err = self.fixture.run("accept-package", "WP1")
                self.assertEqual(code, 2)
                self.assertIsNone(data)
                self.assertEqual(original_plan, self.fixture.tasks_path.read_text(encoding="utf-8"))

    def test_block_and_reset_are_constrained_and_do_not_fabricate_proof(self) -> None:
        code, data, err = self.fixture.run("block-task", "P2-T001", "--reason", "   ")
        self.assertEqual(code, 2)
        self.assertIsNone(data)
        self.assertIn("non-empty --reason", err)
        self.assertFalse((self.fixture.proofs_dir / "WP2.proof.json").exists())

        code, blocked, err = self.fixture.run("block-task", "P2-T001", "--reason", "waiting", "--blocked-at", "2026-05-16T00:07:00+00:00")
        self.assertEqual((code, err), (0, ""))
        self.assertEqual(blocked["blocked"], "P2-T001")
        task = self.fixture.read_plan()["phases"][1]["tasks"][0]
        self.assertEqual(task["status"], "blocked")
        self.assertEqual(task["blocked_reason"], "waiting")
        self.assertNotIn("completed_at", task)

        code, reset, err = self.fixture.run("reset-task", "P2-T001")
        self.assertEqual((code, err), (0, ""))
        task = self.fixture.read_plan()["phases"][1]["tasks"][0]
        self.assertEqual(reset, {"reset": "P2-T001", "status": "pending"})
        self.assertEqual(task["status"], "pending")
        self.assertNotIn("blocked_reason", task)
        self.assertNotIn("blocked_at", task)
        self.assertFalse((self.fixture.proofs_dir / "WP2.proof.json").exists())

    def test_finalize_feature_reports_missing_package_proof_as_structured_preflight(self) -> None:
        self.fixture.write_proof("WP1", self.fixture.valid_proof("WP1"))
        self.fixture.mark_all_tasks_done_manually()
        self.fixture.add_final_gates()
        before = self.fixture.tasks_path.read_text(encoding="utf-8")

        code, preflight, err = self.fixture.run("finalize-feature")

        self.assertEqual((code, err), (1, ""))
        self.assertFalse(preflight["mutated"])
        self.assertTrue(any("WP2" in gate and "proof" in gate for gate in preflight["missing_gates"]))
        self.assertEqual(before, self.fixture.tasks_path.read_text(encoding="utf-8"))

    def test_finalize_feature_cannot_be_bypassed_by_status_changes_or_preflight_and_requires_final_gates(self) -> None:
        self.fixture.write_proof("WP1", self.fixture.valid_proof("WP1"))
        self.fixture.write_proof("WP2", self.fixture.valid_proof("WP2"))
        code, all_result, err = self.fixture.run("validate-proofs")
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(all_result["ok"])
        self.assertEqual(self.fixture.read_plan()["status"], "in-progress")

        code, preflight, err = self.fixture.run("finalize-feature")
        self.assertEqual((code, err), (1, ""))
        self.assertFalse(preflight["mutated"])
        self.assertIn("task P1-T001 is not done", preflight["missing_gates"])
        self.assertIn("final_integration_review evidence is missing", preflight["missing_gates"])
        self.assertEqual(self.fixture.read_plan()["status"], "in-progress")

        self.fixture.mark_all_tasks_done_manually()
        code, manual_status, err = self.fixture.run("finalize-feature")
        self.assertEqual((code, err), (1, ""))
        self.assertFalse(manual_status["mutated"])
        self.assertEqual(self.fixture.read_plan()["status"], "in-progress")
        self.assertTrue(any("final_audit" in gate for gate in manual_status["missing_gates"]))

        self.fixture.add_final_gates()
        code, completed, err = self.fixture.run("finalize-feature", "--completed-at", "2026-05-16T00:08:00+00:00")
        self.assertEqual((code, err), (0, ""))
        self.assertTrue(completed["mutated"])
        plan = self.fixture.read_plan()
        self.assertEqual(plan["status"], "completed")
        self.assertEqual(plan["completed_at"], "2026-05-16T00:08:00+00:00")

    def test_missing_targeted_review_blocks_package_and_therefore_final_completion(self) -> None:
        proof = self.fixture.valid_proof("WP1")
        proof.pop("targeted_review")
        self.fixture.write_proof("WP1", proof)
        self.fixture.write_proof("WP2", self.fixture.valid_proof("WP2"))
        self.fixture.mark_all_tasks_done_manually()
        self.fixture.add_final_gates()
        code, data, err = self.fixture.run("accept-package", "WP1")
        self.assertEqual(code, 2)
        self.assertIsNone(data)
        self.assertIn("targeted package review evidence is missing", err)
        code, completed, err = self.fixture.run("finalize-feature")
        self.assertEqual((code, err), (1, ""))
        self.assertFalse(completed["mutated"])
        self.assertIn("package WP1: targeted package review evidence is missing", completed["missing_gates"])
        self.assertEqual(self.fixture.read_plan()["status"], "in-progress")

    def test_targeted_review_package_id_mismatch_blocks_final_completion(self) -> None:
        proof = self.fixture.valid_proof("WP1")
        proof["targeted_review"]["package_id"] = "WP2"
        self.fixture.write_proof("WP1", proof)
        self.fixture.write_proof("WP2", self.fixture.valid_proof("WP2"))
        self.fixture.mark_all_tasks_done_manually()
        self.fixture.add_final_gates()
        code, completed, err = self.fixture.run("finalize-feature")
        self.assertEqual((code, err), (1, ""))
        self.assertFalse(completed["mutated"])
        self.assertIn("package WP1: targeted package review package_id 'WP2' does not match 'WP1'", completed["missing_gates"])
        self.assertEqual(self.fixture.read_plan()["status"], "in-progress")


class GuardrailDocumentationRegressionTests(unittest.TestCase):
    def read_doc(self, relative: str) -> str:
        return (PLUGIN_DIR / relative).read_text(encoding="utf-8")

    def test_taskctl_and_validator_import_only_stdlib_modules(self) -> None:
        allowed = {
            "__future__",
            "argparse",
            "collections",
            "dataclasses",
            "datetime",
            "importlib",
            "json",
            "os",
            "re",
            "subprocess",
            "sys",
            "tempfile",
            "pathlib",
            "typing",
        }
        for path in (TASKCTL_PATH, VALIDATOR_PATH):
            with self.subTest(path=path.name):
                tree = ast.parse(path.read_text(encoding="utf-8"))
                imports = set()
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(alias.name.split(".", 1)[0] for alias in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imports.add(node.module.split(".", 1)[0])
                self.assertLessEqual(imports, allowed)

    def test_cli_scope_has_no_tui_patch_event_history_or_central_ledger_commands(self) -> None:
        source = TASKCTL_PATH.read_text(encoding="utf-8")
        forbidden = ["curses", "prompt_toolkit", "rich", "json patch", "json-patch", "event_history", "event stream", "verification.json"]
        for token in forbidden:
            with self.subTest(token=token):
                self.assertNotIn(token, source)
        parser = taskctl.build_parser()
        commands = set(parser._subparsers._group_actions[0].choices)
        self.assertEqual(
            commands,
            {"proof-template", "validate-proof", "validate-proofs", "accept-package", "finalize-feature", "block-task", "reset-task", "summary", "next-package", "must-prove"},
        )

    def test_known_risk_and_must_prove_guardrails_are_generic_non_persistent_and_consumed(self) -> None:
        known_risk = self.read_doc("references/known-risk-patterns.md")
        self.assertIn("not a schema, risk-tag taxonomy, or persistent checklist", known_risk)
        self.assertIn("Global, import, environment, and test pollution", known_risk)
        self.assertIn("test alone, test before and after likely consumers, and the combined affected suite", known_risk)
        self.assertIn("Pure boundary contract construction", known_risk)
        self.assertNotIn("React", known_risk)
        self.assertNotIn("frontend", known_risk.lower())

        fixture = TaskctlFixture(self)
        try:
            code, checklist, err = fixture.run("must-prove", "WP1")
            self.assertEqual((code, err), (0, ""))
            self.assertEqual(fixture.tasks_path.read_text(encoding="utf-8"), json.dumps(fixture.plan, indent=2, sort_keys=True) + "\n")
            self.assertIsNotNone(checklist["known_risk_prompt"])
            self.assertIn("Known Risk Patterns", checklist["known_risk_prompt"]["prompt"])
            self.assertIn("Pure boundary contract construction", checklist["known_risk_prompt"]["prompt"])
        finally:
            fixture.cleanup()

    def test_focused_repair_review_pollution_and_gate_retention_docs_are_preserved(self) -> None:
        implement = self.read_doc("skills/implement/SKILL.md")
        integration = self.read_doc("skills/implement/references/integration-checkpoint.md")
        dispatch = self.read_doc("skills/implement/references/package-dispatch.md")
        review = self.read_doc("skills/review-code/SKILL.md")
        pipeline = self.read_doc("skills/review-code/references/pipeline-actions.md")
        skeptic = self.read_doc("skills/review-code/references/skeptic-checklist.md")

        self.assertIn("Do not update feature `status` to `completed` until final proof validation", implement)
        self.assertIn("final review-code/fix loop, and final audit pass", implement)
        self.assertIn("A generic status mutation cannot bypass final review-code", implement)
        self.assertIn("changed tests mutate import caches", integration)
        self.assertIn("test alone, test before and after likely consumers, and combined affected suite", integration)
        self.assertIn("fix commit alone does not close a serious finding", integration)
        self.assertIn("exact finding class no longer reproduces", integration)
        self.assertIn("does not replace the mandatory final whole-feature review-code pass or final audit", dispatch)
        self.assertIn("focused post-fix verification of serious finding classes", review)
        self.assertIn("pollution-sensitive ordering checks when triggered", review)
        self.assertIn("do not replace the normal final integration review or audit", pipeline)
        self.assertIn("Focused repair review is an additional closure gate", skeptic)

    def test_progressive_disclosure_and_lightweight_task_artifacts_are_guarded(self) -> None:
        implement = self.read_doc("skills/implement/SKILL.md")
        lifecycle = self.read_doc("skills/implement/references/package-proof-lifecycle.md")
        subagent = self.read_doc("skills/implement/references/subagent-contract.md")
        authoring = self.read_doc("skills/implementation-plan/references/tasks-json-authoring.md")
        readme = self.read_doc("README.md")

        self.assertIn("Load `plugins/super-developer/skills/implement/references/package-proof-lifecycle.md` before routine proof/status operations", implement)
        self.assertIn("Load `plugins/super-developer/skills/implement/references/package-dispatch.md`", implement)
        self.assertIn("Evidence gate: do not mark a task `done` merely because code was committed", implement)
        self.assertIn("final proof validation, package finalization gate, final review-code/fix loop, and final audit pass", implement)
        self.assertIn("not a TUI, workflow engine, generic JSON patcher, central ledger reconciler", lifecycle)
        self.assertIn("event streams, checklist state, proof logs, or package status fields", lifecycle)
        self.assertIn("orchestrator remains authoritative for git infrastructure, status transitions", subagent)
        self.assertIn("It must not edit `.tasks/<feature>/verification.json`, unrelated package proof files, `tasks.json` status fields", subagent)
        self.assertIn("orchestrator validates the package proof, package verification, and required review gates before it changes task status", subagent)
        self.assertIn("Do not add new schema fields, central verification ledgers, persistent checklist sections", authoring)
        self.assertIn("not a TUI, workflow engine, generic JSON patch tool, central ledger reconciler", readme)
        self.assertIn("Manual task-status overrides", readme)

        fixture = TaskctlFixture(self)
        try:
            heavyweight_keys = {"verification", "verification_history", "history", "events", "event_stream", "workflow_state", "proof_log", "checklists", "package_status"}
            self.assertTrue(heavyweight_keys.isdisjoint(fixture.plan))
        finally:
            fixture.cleanup()


if __name__ == "__main__":
    unittest.main()
