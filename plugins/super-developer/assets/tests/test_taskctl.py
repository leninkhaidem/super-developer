from __future__ import annotations

import ast
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1]
TASKCTL_PATH = ASSETS_DIR / "taskctl.py"
VALIDATOR_PATH = ASSETS_DIR / "validate-tasks-json.py"
SPEC = """# CLI Proof Feature

## Requirements
- REQ-1: Emit read-only proof templates.
- REQ-2: Validate package proofs.
- REQ-3: Preserve final verification ledgers.

## Acceptance Criteria
- AC-1: Proof templates are deterministic.
- AC-2: Proof validation is exposed through the CLI.
- AC-3: Final verification ledgers remain authoritative.
"""


class TaskctlCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.tmp_path = Path(self.tmp.name)
        self.repo = self.tmp_path / "repo"
        self.repo.mkdir()
        self.feature_dir = self.repo / ".tasks" / "cli-feature"
        self.feature_dir.mkdir(parents=True)
        (self.feature_dir / "SPEC.md").write_text(SPEC, encoding="utf-8")
        (self.repo / "tracked.txt").write_text("initial\n", encoding="utf-8")
        self.tasks = self.build_tasks_json()
        self.tasks_path = self.feature_dir / "tasks.json"
        self.tasks_path.write_text(json.dumps(self.tasks, indent=2), encoding="utf-8")
        self.git("init")
        self.git("config", "user.email", "tests@example.com")
        self.git("config", "user.name", "Tests")
        self.git("add", ".")
        self.git("commit", "-m", "initial")
        self.commit = self.git("rev-parse", "HEAD").stdout.strip()
        self.sentinel = self.tmp_path / "recorded-command-ran"
        self.proofs_dir = self.feature_dir / "proofs"
        self.proofs_dir.mkdir()
        self.write_valid_proofs()

    def tearDown(self) -> None:
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

    def build_tasks_json(self) -> dict:
        return {
            "schema_version": 2,
            "feature": "cli-feature",
            "title": "CLI Feature",
            "description": "Exercise taskctl read-only commands.",
            "created_at": "2026-05-16T00:00:00Z",
            "status": "reviewed",
            "design_decisions": [
                {
                    "id": "DD-1",
                    "decision": "Expose read-only proof helpers.",
                    "rationale": "Package proofs are additive in this release.",
                    "alternatives_considered": ["Mutating lifecycle commands were rejected."],
                    "source": "design-preflight",
                }
            ],
            "context_bundles": [
                {
                    "id": "CTX-1",
                    "title": "CLI context",
                    "required_for": ["WP1"],
                    "sources": [
                        {
                            "type": "code",
                            "path_or_url": "plugins/super-developer/assets/taskctl.py",
                            "claims": ["taskctl is a read-only wrapper over validator proof primitives."],
                        }
                    ],
                    "verification_required": ["CLI evidence cites CTX-1."],
                },
                {
                    "id": "CTX-2",
                    "title": "Final gate context",
                    "required_for": ["WP2"],
                    "sources": [
                        {
                            "type": "code",
                            "path_or_url": "plugins/super-developer/assets/validate-tasks-json.py",
                            "claims": ["verification.json final validation remains authoritative."],
                        }
                    ],
                    "verification_required": ["Final-gate evidence cites CTX-2."],
                },
            ],
            "work_packages": [
                {
                    "id": "WP1",
                    "title": "CLI proof commands",
                    "description": "Expose proof helpers.",
                    "task_ids": ["P1-T001"],
                    "depends_on": [],
                    "parallel_safe_with": [],
                    "primary_paths": ["plugins/super-developer/assets/taskctl.py"],
                    "verification_commands": [],
                    "risk_tags": ["orchestration", "validation"],
                    "required_context_bundles": ["CTX-1"],
                    "targeted_review_required": True,
                    "rationale": "The CLI command surface is isolated.",
                },
                {
                    "id": "WP2",
                    "title": "Final compatibility",
                    "description": "Preserve final verification ledgers.",
                    "task_ids": ["P1-T002"],
                    "depends_on": ["WP1"],
                    "parallel_safe_with": [],
                    "primary_paths": ["plugins/super-developer/assets/validate-tasks-json.py"],
                    "verification_commands": [],
                    "risk_tags": ["validation"],
                    "required_context_bundles": ["CTX-2"],
                    "targeted_review_required": True,
                    "rationale": "Final-gate compatibility is isolated.",
                },
            ],
            "phases": [
                {
                    "id": "P1",
                    "name": "CLI",
                    "description": "CLI proof helper coverage.",
                    "order": 1,
                    "tasks": [
                        {
                            "id": "P1-T001",
                            "title": "CLI helpers",
                            "description": "Expose read-only proof helpers.",
                            "status": "in-progress",
                            "dependencies": [],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T001-AC1",
                                    "criterion": "The CLI emits deterministic proof templates.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-1"},
                                        {"type": "spec_ac", "id": "AC-1"},
                                        {"type": "context_bundle", "id": "CTX-1"},
                                    ],
                                    "verification_hint": "Run proof-template and inspect stable JSON.",
                                },
                                {
                                    "id": "P1-T001-AC2",
                                    "criterion": "The CLI validates package proofs.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-2"},
                                        {"type": "spec_ac", "id": "AC-2"},
                                        {"type": "design_decision", "id": "DD-1"},
                                        {"type": "context_bundle", "id": "CTX-1"},
                                    ],
                                    "verification_hint": "Run validate-proof and validate-proofs.",
                                },
                            ],
                            "required_context_bundles": [],
                            "context": "Read-only proof helpers.",
                        },
                        {
                            "id": "P1-T002",
                            "title": "Final compatibility",
                            "description": "Keep verification.json authoritative.",
                            "status": "in-progress",
                            "dependencies": ["P1-T001"],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T002-AC1",
                                    "criterion": "Final verification ledger validation remains authoritative.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-3"},
                                        {"type": "spec_ac", "id": "AC-3"},
                                        {"type": "context_bundle", "id": "CTX-2"},
                                    ],
                                    "verification_hint": "Run validate-tasks-json.py --final.",
                                }
                            ],
                            "required_context_bundles": [],
                            "context": "Final validation compatibility.",
                        },
                    ],
                }
            ],
        }

    def command_record(self, observed: str = "Recorded command evidence stayed inert.") -> dict:
        return {
            "cwd": str(self.repo),
            "command": (
                f"{sys.executable} -c "
                f"\"from pathlib import Path; Path({str(self.sentinel)!r}).write_text('ran')\""
            ),
            "exit_code": 0,
            "observed": observed,
        }

    def entry(self, criterion_id: str, package_id: str, context_bundles: list[str]) -> dict:
        task_id = criterion_id.rsplit("-AC", 1)[0]
        source_refs = self.source_refs_for(criterion_id)
        return {
            "criterion_id": criterion_id,
            "task_id": task_id,
            "package_id": package_id,
            "status": "verified",
            "method": "command",
            "source_refs": source_refs,
            "state": {
                "git_ref": "HEAD",
                "commit": self.commit,
                "worktree": str(self.repo),
                "captured_at": "2026-05-16T00:00:00Z",
            },
            "evidence": {
                "files": ["tracked.txt"],
                "commands": [self.command_record()],
                "edge_cases": ["recorded commands are inspected but not executed"],
                "context_bundles": context_bundles,
                "mocks": "none",
            },
        }

    def source_refs_for(self, criterion_id: str) -> list[dict[str, str]]:
        for phase in self.tasks["phases"]:
            for task in phase["tasks"]:
                for criterion in task["acceptance_criteria"]:
                    if criterion["id"] == criterion_id:
                        return copy.deepcopy(criterion["source_refs"])
        raise AssertionError(f"unknown criterion {criterion_id}")

    def proof(self, package_id: str) -> dict:
        if package_id == "WP1":
            entries = [
                self.entry("P1-T001-AC1", "WP1", ["CTX-1"]),
                self.entry("P1-T001-AC2", "WP1", ["CTX-1"]),
            ]
        elif package_id == "WP2":
            entries = [self.entry("P1-T002-AC1", "WP2", ["CTX-2"])]
        else:
            raise AssertionError(f"unknown package {package_id}")
        return {
            "schema_version": 1,
            "feature": "cli-feature",
            "package_id": package_id,
            "entries": entries,
        }

    def final_ledger(self) -> dict:
        return {
            "schema_version": 1,
            "feature": "cli-feature",
            "entries": [
                *self.proof("WP1")["entries"],
                *self.proof("WP2")["entries"],
            ],
        }

    def write_valid_proofs(self) -> None:
        for package_id in ("WP1", "WP2"):
            (self.proofs_dir / f"{package_id}.proof.json").write_text(
                json.dumps(self.proof(package_id), indent=2),
                encoding="utf-8",
            )

    def taskctl(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(TASKCTL_PATH), *args],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def validator(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), *args],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def snapshot_files(self) -> dict[str, bytes]:
        snapshot: dict[str, bytes] = {}
        for path in sorted(self.repo.rglob("*")):
            if path.is_file():
                snapshot[str(path.relative_to(self.repo))] = path.read_bytes()
        return snapshot

    def assert_read_only(self, *args: str, expected_returncode: int = 0) -> subprocess.CompletedProcess[str]:
        before = self.snapshot_files()
        result = self.taskctl(*args)
        after = self.snapshot_files()
        self.assertEqual(expected_returncode, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(self.sentinel.exists())
        return result

    def test_help_lists_only_release_one_read_only_commands(self) -> None:
        result = self.taskctl("--help")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for command in ("proof-template", "validate-proof", "validate-proofs", "must-prove", "summary"):
            self.assertIn(command, result.stdout)
        for forbidden in ("accept-package", "finalize-feature", "reopen-package", "status mutation"):
            self.assertNotIn(forbidden, result.stdout)
        self.assertIn("Read-only additive", result.stdout)

    def test_all_approved_commands_are_read_only_on_success(self) -> None:
        commands = [
            ("proof-template", "--tasks", str(self.tasks_path), "--package", "WP1"),
            (
                "validate-proof",
                "--tasks",
                str(self.tasks_path),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            ("validate-proofs", "--tasks", str(self.tasks_path)),
            ("must-prove", "--tasks", str(self.tasks_path)),
            ("summary", "--tasks", str(self.tasks_path)),
        ]
        for command in commands:
            with self.subTest(command=command[0]):
                self.assert_read_only(*command)

    def test_proof_template_and_plan_derived_outputs_are_deterministic(self) -> None:
        first = self.assert_read_only(
            "proof-template", "--tasks", str(self.tasks_path), "--package", "WP1"
        )
        second = self.assert_read_only(
            "proof-template", "--tasks", str(self.tasks_path), "--package", "WP1"
        )
        self.assertEqual(first.stdout, second.stdout)
        template = json.loads(first.stdout)
        self.assertEqual("cli-feature", template["feature"])
        self.assertEqual("WP1", template["package_id"])
        self.assertEqual(["P1-T001-AC1", "P1-T001-AC2"], [entry["criterion_id"] for entry in template["entries"]])
        self.assertEqual(["CTX-1"], template["entries"][0]["evidence"]["context_bundles"])

        must_prove = json.loads(
            self.assert_read_only(
                "must-prove", "--tasks", str(self.tasks_path), "--package", "WP1"
            ).stdout
        )
        package = must_prove["packages"][0]
        self.assertEqual(["orchestration", "validation"], package["risk_tags"])
        self.assertEqual({"in-progress": 1}, package["task_status_counts"])
        self.assertEqual("valid", package["proof"]["status"])
        self.assertEqual(
            "Run proof-template and inspect stable JSON.",
            package["criteria"][0]["verification_hint"],
        )

        summary = json.loads(
            self.assert_read_only("summary", "--tasks", str(self.tasks_path)).stdout
        )
        self.assertEqual("verification.json remains authoritative in this release.", summary["final_gate"])
        self.assertEqual({"valid": 2}, summary["proof_health"])

    def test_validate_proof_and_validate_proofs_return_structured_failures(self) -> None:
        valid_single = json.loads(
            self.assert_read_only(
                "validate-proof",
                "--tasks",
                str(self.tasks_path),
                str(self.proofs_dir / "WP1.proof.json"),
            ).stdout
        )
        self.assertTrue(valid_single["ok"])
        valid_all = json.loads(
            self.assert_read_only("validate-proofs", "--tasks", str(self.tasks_path)).stdout
        )
        self.assertTrue(valid_all["ok"])

        missing = self.assert_read_only(
            "validate-proof",
            "--tasks",
            str(self.tasks_path),
            str(self.proofs_dir / "missing.proof.json"),
            expected_returncode=1,
        )
        missing_error = json.loads(missing.stderr)
        self.assertFalse(missing_error["ok"])
        self.assertIn("file not found", "\n".join(missing_error["errors"]))

        (self.proofs_dir / "WP2.proof.json").unlink()
        missing_all = self.assert_read_only(
            "validate-proofs",
            "--tasks",
            str(self.tasks_path),
            expected_returncode=1,
        )
        self.assertIn("WP2", "\n".join(json.loads(missing_all.stderr)["errors"]))

    def test_cli_rejects_malformed_proof_json_and_document_shapes(self) -> None:
        proof_path = self.proofs_dir / "WP1.proof.json"
        proof_path.write_text("{", encoding="utf-8")
        malformed_json = self.assert_read_only(
            "validate-proof",
            "--tasks",
            str(self.tasks_path),
            str(proof_path),
            expected_returncode=1,
        )
        self.assertIn("invalid JSON", "\n".join(json.loads(malformed_json.stderr)["errors"]))

        proof_path.write_text(json.dumps([]), encoding="utf-8")
        malformed_shape = self.assert_read_only(
            "validate-proof",
            "--tasks",
            str(self.tasks_path),
            str(proof_path),
            expected_returncode=1,
        )
        self.assertIn("root: expected object", "\n".join(json.loads(malformed_shape.stderr)["errors"]))

    def test_cli_validates_sibling_spec_before_plan_operations(self) -> None:
        (self.feature_dir / "SPEC.md").unlink()
        result = self.assert_read_only(
            "proof-template",
            "--tasks",
            str(self.tasks_path),
            "--package",
            "WP1",
            expected_returncode=1,
        )
        self.assertIn("SPEC.md: expected sibling file", "\n".join(json.loads(result.stderr)["errors"]))

    def test_recorded_command_evidence_is_inert_for_proof_reading_commands(self) -> None:
        commands = [
            (
                "validate-proof",
                "--tasks",
                str(self.tasks_path),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            ("validate-proofs", "--tasks", str(self.tasks_path)),
            ("must-prove", "--tasks", str(self.tasks_path)),
            ("summary", "--tasks", str(self.tasks_path)),
        ]
        for command in commands:
            with self.subTest(command=command[0]):
                self.assert_read_only(*command)
                self.assertFalse(self.sentinel.exists())

    def test_final_verification_json_compatibility_ignores_package_proofs(self) -> None:
        verification_path = self.feature_dir / "verification.json"
        verification_path.write_text(json.dumps(self.final_ledger(), indent=2), encoding="utf-8")
        (self.proofs_dir / "WP1.proof.json").write_text("{", encoding="utf-8")
        valid = self.validator(
            "--final",
            "--worktree",
            str(self.repo),
            str(self.tasks_path),
        )
        self.assertEqual(0, valid.returncode, valid.stdout + valid.stderr)
        self.assertIn("verification.json are valid", valid.stdout)

        invalid_ledger = self.final_ledger()
        invalid_ledger["entries"][0]["status"] = "failed"
        verification_path.write_text(json.dumps(invalid_ledger, indent=2), encoding="utf-8")
        invalid = self.validator(
            "--final",
            "--worktree",
            str(self.repo),
            str(self.tasks_path),
        )
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("cannot contain 'failed'", invalid.stdout)

    def test_taskctl_uses_only_stdlib_imports(self) -> None:
        tree = ast.parse(TASKCTL_PATH.read_text(encoding="utf-8"))
        imports: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name.split(".", 1)[0] for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imports.add(node.module.split(".", 1)[0])
        self.assertLessEqual(
            imports,
            {
                "__future__",
                "argparse",
                "collections",
                "importlib",
                "json",
                "pathlib",
                "sys",
                "typing",
            },
        )


if __name__ == "__main__":
    unittest.main()
