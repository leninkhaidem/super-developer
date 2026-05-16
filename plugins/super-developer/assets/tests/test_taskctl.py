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
from unittest import mock
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1]
TASKCTL_PATH = ASSETS_DIR / "taskctl.py"
VALIDATOR_PATH = ASSETS_DIR / "validate-tasks-json.py"
SPEC = """# CLI Proof Feature

## Requirements
- REQ-1: Emit read-only proof templates.
- REQ-2: Validate package proofs.
    - REQ-3: Use accepted package proofs for final validation.

## Acceptance Criteria
- AC-1: Proof templates are deterministic.
- AC-2: Proof validation is exposed through the CLI.
    - AC-3: Accepted package proofs are authoritative for final validation.
"""


def load_taskctl_module():
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("taskctl_under_test", TASKCTL_PATH)
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode


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
                            "claims": ["accepted package proofs are authoritative for final validation."],
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
                    "title": "Final proof gate",
                    "description": "Require accepted package proofs.",
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
                            "title": "Final proof gate",
                            "description": "Require accepted package proofs.",
                            "status": "in-progress",
                            "dependencies": ["P1-T001"],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T002-AC1",
                                    "criterion": "Accepted package proof validation remains authoritative.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-3"},
                                        {"type": "spec_ac", "id": "AC-3"},
                                        {"type": "context_bundle", "id": "CTX-2"},
                                    ],
                                    "verification_hint": "Run validate-tasks-json.py --final with accepted proofs.",
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

    def read_proof(self, package_id: str = "WP1") -> dict:
        return json.loads((self.proofs_dir / f"{package_id}.proof.json").read_text(encoding="utf-8"))

    def write_proof(self, proof: dict, package_id: str = "WP1") -> None:
        (self.proofs_dir / f"{package_id}.proof.json").write_text(
            json.dumps(proof, indent=2),
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

    def snapshot_tree(self, root: Path) -> dict[str, tuple[str, bytes]]:
        snapshot: dict[str, tuple[str, bytes]] = {}
        for path in sorted(root.rglob("*")):
            relative = str(path.relative_to(root))
            if path.is_dir():
                snapshot[relative] = ("dir", b"")
            elif path.is_file():
                snapshot[relative] = ("file", path.read_bytes())
        return snapshot

    def snapshot_read_only_paths(self) -> dict[str, dict[str, tuple[str, bytes]]]:
        return {
            "repo": self.snapshot_tree(self.repo),
            "assets": self.snapshot_tree(ASSETS_DIR),
        }

    def assert_only_repo_path_changed(
        self,
        before: dict[str, dict[str, tuple[str, bytes]]],
        after: dict[str, dict[str, tuple[str, bytes]]],
        changed_path: Path,
    ) -> None:
        changed_relative = str(changed_path.relative_to(self.repo))
        self.assertEqual(before["assets"], after["assets"])
        self.assertEqual(set(before["repo"]), set(after["repo"]))
        changed = {
            path
            for path in before["repo"]
            if before["repo"][path] != after["repo"][path]
        }
        self.assertEqual({changed_relative}, changed)

    def assert_read_only(self, *args: str, expected_returncode: int = 0) -> subprocess.CompletedProcess[str]:
        before = self.snapshot_read_only_paths()
        result = self.taskctl(*args)
        after = self.snapshot_read_only_paths()
        self.assertEqual(expected_returncode, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(self.sentinel.exists())
        return result

    def accept_package(
        self, package_id: str = "WP1", expected_returncode: int = 0
    ) -> subprocess.CompletedProcess[str]:
        result = self.taskctl(
            "accept-package",
            "--tasks",
            str(self.tasks_path),
            "--worktree",
            str(self.repo),
            str(self.proofs_dir / f"{package_id}.proof.json"),
        )
        self.assertEqual(expected_returncode, result.returncode, result.stdout + result.stderr)
        return result

    def reopen_package(
        self, package_id: str = "WP1", expected_returncode: int = 0
    ) -> subprocess.CompletedProcess[str]:
        result = self.taskctl(
            "reopen-package",
            "--tasks",
            str(self.tasks_path),
            "--worktree",
            str(self.repo),
            str(self.proofs_dir / f"{package_id}.proof.json"),
        )
        self.assertEqual(expected_returncode, result.returncode, result.stdout + result.stderr)
        return result

    def assert_rejected_without_write(
        self, command: tuple[str, ...], expected_error: str
    ) -> subprocess.CompletedProcess[str]:
        before = self.snapshot_read_only_paths()
        result = self.taskctl(*command)
        after = self.snapshot_read_only_paths()
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
        self.assertFalse(self.sentinel.exists())
        return result

    def test_help_lists_release_two_lifecycle_commands_without_finalizers(self) -> None:
        result = self.taskctl("--help")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        for command in (
            "proof-template",
            "validate-proof",
            "validate-proofs",
            "must-prove",
            "summary",
            "accept-package",
            "reopen-package",
        ):
            self.assertIn(command, result.stdout)
        for forbidden in ("finalize-feature", "status mutation", "task status"):
            self.assertNotIn(forbidden, result.stdout)
        self.assertIn("Accepted package proofs", result.stdout)

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

    def test_validator_backed_command_does_not_create_helper_cache_files(self) -> None:
        assets_cache = ASSETS_DIR / "__pycache__"
        shutil.rmtree(assets_cache, ignore_errors=True)
        before = self.snapshot_read_only_paths()
        self.assertNotIn("__pycache__", before["assets"])
        self.assertFalse(any(path.startswith("__pycache__/") for path in before["assets"]))

        result = self.taskctl(
            "validate-proof",
            "--tasks",
            str(self.tasks_path),
            str(self.proofs_dir / "WP1.proof.json"),
        )

        after = self.snapshot_read_only_paths()
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual(before, after)
        self.assertFalse(assets_cache.exists())
        self.assertFalse(any(path == "__pycache__" or path.startswith("__pycache__/") for path in after["assets"]))
        self.assertFalse(self.sentinel.exists())

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
        self.assertEqual("unaccepted", package["proof"]["status"])
        self.assertEqual(
            "Run proof-template and inspect stable JSON.",
            package["criteria"][0]["verification_hint"],
        )

        summary = json.loads(
            self.assert_read_only("summary", "--tasks", str(self.tasks_path)).stdout
        )
        self.assertEqual(
            "accepted package proofs are authoritative in this release.", summary["final_gate"]
        )
        self.assertEqual({"unaccepted": 2}, summary["proof_health"])

    def test_accept_package_writes_selected_proof_lifecycle_state(self) -> None:
        proof_path = self.proofs_dir / "WP1.proof.json"
        before = self.snapshot_read_only_paths()

        result = self.accept_package()
        after = self.snapshot_read_only_paths()

        self.assert_only_repo_path_changed(before, after, proof_path)
        output = json.loads(result.stdout)
        self.assertTrue(output["ok"])
        self.assertEqual("accept-package", output["command"])
        self.assertEqual("WP1", output["package_id"])
        self.assertEqual("none", output["lifecycle"]["previous_state"])
        self.assertEqual("accepted", output["lifecycle"]["state"])
        self.assertTrue(output["lifecycle"]["changed"])
        proof = self.read_proof()
        lifecycle = proof["lifecycle"]
        self.assertEqual("accepted", lifecycle["state"])
        self.assertEqual("WP1", lifecycle["package_id"])
        self.assertEqual(str(proof_path.resolve(strict=False)), lifecycle["proof_path"])
        self.assertEqual(
            {"tool": "taskctl.py", "command": "accept-package", "schema_version": 1},
            lifecycle["writer"],
        )
        self.assertEqual("accepted", lifecycle["state_binding"]["state"])
        self.assertEqual(str(self.repo.resolve(strict=False)), lifecycle["state_binding"]["worktree"])
        self.assertEqual(self.commit, lifecycle["state_binding"]["commit"])
        self.assertFalse(self.sentinel.exists())

    def test_accept_package_is_idempotent_for_same_valid_proof(self) -> None:
        first = json.loads(self.accept_package().stdout)
        self.assertTrue(first["lifecycle"]["changed"])
        before = self.snapshot_read_only_paths()

        second = json.loads(self.accept_package().stdout)
        after = self.snapshot_read_only_paths()

        self.assertEqual(before, after)
        self.assertEqual("accepted", second["lifecycle"]["previous_state"])
        self.assertEqual("accepted", second["lifecycle"]["state"])
        self.assertFalse(second["lifecycle"]["changed"])
        self.assertFalse(self.sentinel.exists())

    def test_accept_package_rebinds_same_proof_to_new_worktree(self) -> None:
        self.accept_package()
        merge_worktree = self.tmp_path / "merge-worktree"
        self.git("worktree", "add", "-b", "feature-merge", str(merge_worktree), "HEAD")
        proof_path = self.proofs_dir / "WP1.proof.json"
        before = self.snapshot_read_only_paths()

        result = self.taskctl(
            "accept-package",
            "--tasks",
            str(self.tasks_path),
            "--worktree",
            str(merge_worktree),
            str(proof_path),
        )
        after = self.snapshot_read_only_paths()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assert_only_repo_path_changed(before, after, proof_path)
        output = json.loads(result.stdout)
        self.assertEqual("accepted", output["lifecycle"]["previous_state"])
        self.assertEqual("accepted", output["lifecycle"]["state"])
        self.assertTrue(output["lifecycle"]["changed"])
        proof = self.read_proof()
        self.assertEqual(
            str(merge_worktree.resolve(strict=False)),
            proof["lifecycle"]["state_binding"]["worktree"],
        )
        self.assertEqual("feature-merge", proof["lifecycle"]["state_binding"]["git_ref"])
        self.assertEqual(self.commit, proof["lifecycle"]["state_binding"]["commit"])
        validated = self.taskctl(
            "validate-proof",
            "--tasks",
            str(self.tasks_path),
            "--worktree",
            str(merge_worktree),
            str(proof_path),
        )
        self.assertEqual(0, validated.returncode, validated.stdout + validated.stderr)
        self.assertFalse(self.sentinel.exists())

    def test_accept_package_rejects_changed_or_fake_accepted_state_without_write(self) -> None:
        accepted = self.read_proof()
        self.accept_package()

        changed = self.read_proof()
        changed["entries"][0]["evidence"]["edge_cases"].append("proof changed after acceptance")
        self.write_proof(changed)
        self.assert_rejected_without_write(
            (
                "accept-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            "proof_digest",
        )

        self.write_proof(accepted)
        self.accept_package()
        missing_writer = self.read_proof()
        missing_writer["lifecycle"].pop("writer")
        self.write_proof(missing_writer)
        self.assert_rejected_without_write(
            (
                "accept-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            "writer",
        )

        self.write_proof(accepted)
        self.accept_package()
        fake_writer = self.read_proof()
        fake_writer["lifecycle"]["writer"]["tool"] = "manual-editor"
        self.write_proof(fake_writer)
        self.assert_rejected_without_write(
            (
                "accept-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            "manual-editor",
        )

        self.write_proof(accepted)
        self.accept_package()
        wrong_path = self.read_proof()
        wrong_path["lifecycle"]["proof_path"] = str(self.repo / "wrong.proof.json")
        self.write_proof(wrong_path)
        self.assert_rejected_without_write(
            (
                "accept-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            "proof_path",
        )

    def test_accept_package_rejects_stale_or_wrong_proof_path_without_write(self) -> None:
        self.accept_package()
        (self.repo / "tracked.txt").write_text("changed after acceptance\n", encoding="utf-8")
        self.assert_rejected_without_write(
            (
                "accept-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            "stale accepted proof state",
        )
        self.git("checkout", "--", "tracked.txt")

        self.write_proof(self.proof("WP1"), package_id="WP2")
        self.assert_rejected_without_write(
            (
                "accept-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP2.proof.json"),
            ),
            "package proof path: expected",
        )

    def test_reopen_package_writes_selected_proof_and_allows_reacceptance(self) -> None:
        self.accept_package()
        proof_path = self.proofs_dir / "WP1.proof.json"
        before = self.snapshot_read_only_paths()

        reopened = json.loads(self.reopen_package().stdout)
        after = self.snapshot_read_only_paths()

        self.assert_only_repo_path_changed(before, after, proof_path)
        self.assertEqual("accepted", reopened["lifecycle"]["previous_state"])
        self.assertEqual("reopened", reopened["lifecycle"]["state"])
        proof = self.read_proof()
        self.assertEqual("reopened", proof["lifecycle"]["state"])
        self.assertEqual("reopen-package", proof["lifecycle"]["writer"]["command"])

        reaccepted = json.loads(self.accept_package().stdout)
        self.assertEqual("reopened", reaccepted["lifecycle"]["previous_state"])
        self.assertEqual("accepted", reaccepted["lifecycle"]["state"])
        self.assertTrue(reaccepted["lifecycle"]["changed"])
        self.assertEqual("accepted", self.read_proof()["lifecycle"]["state"])
        self.assertFalse(self.sentinel.exists())

    def test_reopen_package_clears_stale_accepted_lifecycle_state(self) -> None:
        self.accept_package()
        proof_path = self.proofs_dir / "WP1.proof.json"
        proof = self.read_proof()
        proof["entries"][0]["evidence"]["edge_cases"].append("proof edited after acceptance")
        self.write_proof(proof)
        (self.repo / "tracked.txt").write_text("changed after acceptance\n", encoding="utf-8")
        before = self.snapshot_read_only_paths()

        reopened = json.loads(self.reopen_package().stdout)
        after = self.snapshot_read_only_paths()

        self.assert_only_repo_path_changed(before, after, proof_path)
        self.assertEqual("accepted", reopened["lifecycle"]["previous_state"])
        self.assertEqual("reopened", reopened["lifecycle"]["state"])
        self.assertTrue(reopened["lifecycle"]["changed"])
        proof = self.read_proof()
        self.assertEqual("reopened", proof["lifecycle"]["state"])
        self.assertEqual("reopen-package", proof["lifecycle"]["writer"]["command"])
        self.assertFalse(self.sentinel.exists())

    def test_reopen_package_rejects_malformed_accepted_digest_without_write(self) -> None:
        self.accept_package()
        proof = self.read_proof()
        proof["lifecycle"]["proof_digest"] = "not-a-digest"
        self.write_proof(proof)

        self.assert_rejected_without_write(
            (
                "reopen-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            "proof_digest: expected sha256 digest string",
        )

    def test_accept_package_replaces_stale_reopened_digest_after_valid_proof_edit(self) -> None:
        self.accept_package()
        self.reopen_package()
        proof_path = self.proofs_dir / "WP1.proof.json"
        proof = self.read_proof()
        proof["entries"][0]["evidence"]["edge_cases"].append("valid proof edit after reopen")
        self.write_proof(proof)
        before = self.snapshot_read_only_paths()

        accepted = json.loads(self.accept_package().stdout)
        after = self.snapshot_read_only_paths()

        self.assert_only_repo_path_changed(before, after, proof_path)
        self.assertEqual("reopened", accepted["lifecycle"]["previous_state"])
        self.assertEqual("accepted", accepted["lifecycle"]["state"])
        self.assertTrue(accepted["lifecycle"]["changed"])
        proof = self.read_proof()
        self.assertEqual("accepted", proof["lifecycle"]["state"])
        self.assertEqual(accepted["lifecycle"]["proof_digest"], proof["lifecycle"]["proof_digest"])
        self.assertFalse(self.sentinel.exists())

    def test_accept_package_rejects_malformed_reopened_digest_without_write(self) -> None:
        self.accept_package()
        self.reopen_package()
        proof = self.read_proof()
        proof["lifecycle"]["proof_digest"] = "not-a-digest"
        self.write_proof(proof)

        self.assert_rejected_without_write(
            (
                "accept-package",
                "--tasks",
                str(self.tasks_path),
                "--worktree",
                str(self.repo),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            "proof_digest: expected sha256 digest string",
        )

    def test_reopen_package_rejects_invalid_transitions_without_write(self) -> None:
        reopen_command = (
            "reopen-package",
            "--tasks",
            str(self.tasks_path),
            "--worktree",
            str(self.repo),
            str(self.proofs_dir / "WP1.proof.json"),
        )
        self.assert_rejected_without_write(reopen_command, "none -> reopened is not allowed")

        self.accept_package()
        self.reopen_package()
        self.assert_rejected_without_write(reopen_command, "reopened -> reopened is not allowed")

        self.write_proof(self.proof("WP1"))
        self.accept_package()
        fake_writer = self.read_proof()
        fake_writer["lifecycle"]["writer"]["tool"] = "manual-editor"
        self.write_proof(fake_writer)
        self.assert_rejected_without_write(reopen_command, "manual-editor")

    def test_lifecycle_commands_do_not_truncate_original_on_write_failure(self) -> None:
        taskctl = load_taskctl_module()
        proof_path = self.proofs_dir / "WP1.proof.json"
        original = proof_path.read_bytes()
        stdout = io.StringIO()
        stderr = io.StringIO()

        with mock.patch.object(taskctl.os, "replace", side_effect=OSError("simulated replace failure")):
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                exit_code = taskctl.main(
                    [
                        "accept-package",
                        "--tasks",
                        str(self.tasks_path),
                        "--worktree",
                        str(self.repo),
                        str(proof_path),
                    ]
                )

        self.assertEqual(1, exit_code)
        self.assertEqual(original, proof_path.read_bytes())
        self.assertFalse(list(self.proofs_dir.glob("*.tmp")))
        self.assertIn("unable to write", "\n".join(json.loads(stderr.getvalue())["errors"]))
        self.assertEqual("", stdout.getvalue())

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

    def test_recorded_command_evidence_is_inert_for_lifecycle_commands(self) -> None:
        self.accept_package()
        self.assertFalse(self.sentinel.exists())
        self.reopen_package()
        self.assertFalse(self.sentinel.exists())
        self.accept_package()
        self.assertFalse(self.sentinel.exists())
        commands = [
            (
                "validate-proof",
                "--tasks",
                str(self.tasks_path),
                str(self.proofs_dir / "WP1.proof.json"),
            ),
            ("validate-proofs", "--tasks", str(self.tasks_path)),
            ("summary", "--tasks", str(self.tasks_path)),
        ]
        for command in commands:
            with self.subTest(command=command[0]):
                self.assert_read_only(*command)
                self.assertFalse(self.sentinel.exists())

    def test_final_validation_requires_accepted_package_proofs(self) -> None:
        verification_path = self.feature_dir / "verification.json"
        self.accept_package("WP1")
        self.accept_package("WP2")
        invalid_ledger = self.final_ledger()
        invalid_ledger["entries"][0]["status"] = "failed"
        verification_path.write_text(json.dumps(invalid_ledger, indent=2), encoding="utf-8")
        valid = self.validator(
            "--final",
            "--worktree",
            str(self.repo),
            str(self.tasks_path),
        )
        self.assertEqual(0, valid.returncode, valid.stdout + valid.stderr)
        self.assertIn("package proofs are valid", valid.stdout)

        self.reopen_package("WP2")
        verification_path.write_text(json.dumps(self.final_ledger(), indent=2), encoding="utf-8")
        invalid = self.validator(
            "--final",
            "--worktree",
            str(self.repo),
            str(self.tasks_path),
        )
        self.assertNotEqual(0, invalid.returncode)
        self.assertIn("expected 'accepted'", invalid.stdout)

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
                "datetime",
                "importlib",
                "json",
                "os",
                "pathlib",
                "subprocess",
                "sys",
                "tempfile",
                "typing",
            },
        )


if __name__ == "__main__":
    unittest.main()
