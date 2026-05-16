from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "validate-tasks-json.py"
SPEC = """# Proof Feature

## Requirements
- REQ-1: Validate package proof roots.
- REQ-2: Reuse ledger evidence semantics.
- REQ-3: Preserve final ledger validation.

## Acceptance Criteria
- AC-1: Package proof roots are validated.
- AC-2: Ledger evidence semantics are reused.
- AC-3: Final ledger validation remains authoritative.
"""


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_tasks_json", VALIDATOR_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class PackageProofValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.feature_dir = self.repo / ".tasks" / "proof-feature"
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
        errors, plan_index = validator.validate_tasks_json(
            self.tasks,
            tasks_path=self.tasks_path,
            spec_path=self.feature_dir / "SPEC.md",
        )
        self.assertEqual([], errors)
        self.plan_index = plan_index
        self.sentinel = self.repo / "sentinel-ran"

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
            "feature": "proof-feature",
            "title": "Proof Feature",
            "description": "Exercise package proof validation.",
            "created_at": "2026-05-16T00:00:00Z",
            "status": "reviewed",
            "design_decisions": [
                {
                    "id": "DD-1",
                    "decision": "Reuse ledger validation.",
                    "rationale": "A single validator owns evidence semantics.",
                    "alternatives_considered": ["A separate proof schema was rejected."],
                    "source": "design-preflight",
                }
            ],
            "context_bundles": [
                {
                    "id": "CTX-1",
                    "title": "Package context",
                    "required_for": ["WP1"],
                    "sources": [
                        {
                            "type": "code",
                            "path_or_url": "plugins/super-developer/assets/validate-tasks-json.py",
                            "claims": ["Package proof validation uses validator-owned plan indexes."],
                        }
                    ],
                    "verification_required": ["Cite CTX-1 in WP1 proof evidence."],
                },
                {
                    "id": "CTX-2",
                    "title": "Task context",
                    "required_for": ["P1-T002"],
                    "sources": [
                        {
                            "type": "repo",
                            "path_or_url": "plugins/super-developer/references/work-packages.md",
                            "claims": ["Task-specific context must be cited when applicable."],
                        }
                    ],
                    "verification_required": ["Cite CTX-2 for P1-T002 criteria."],
                },
            ],
            "work_packages": [
                {
                    "id": "WP1",
                    "title": "Proof validator",
                    "description": "Validate proof files.",
                    "task_ids": ["P1-T001", "P1-T002"],
                    "depends_on": [],
                    "parallel_safe_with": [],
                    "primary_paths": ["plugins/super-developer/assets/validate-tasks-json.py"],
                    "verification_commands": [],
                    "risk_tags": ["schema", "validation"],
                    "required_context_bundles": ["CTX-1"],
                    "targeted_review_required": True,
                    "rationale": "Both tasks exercise the validator proof contract.",
                },
                {
                    "id": "WP2",
                    "title": "Compatibility",
                    "description": "Validate final ledger compatibility.",
                    "task_ids": ["P1-T003"],
                    "depends_on": ["WP1"],
                    "parallel_safe_with": [],
                    "primary_paths": ["plugins/super-developer/assets/validate-tasks-json.py"],
                    "verification_commands": [],
                    "risk_tags": ["validation"],
                    "required_context_bundles": [],
                    "targeted_review_required": True,
                    "rationale": "Final ledger checks are isolated compatibility coverage.",
                },
            ],
            "phases": [
                {
                    "id": "P1",
                    "name": "Proofs",
                    "description": "Proof validation.",
                    "order": 1,
                    "tasks": [
                        {
                            "id": "P1-T001",
                            "title": "Root binding",
                            "description": "Validate root binding.",
                            "status": "in-progress",
                            "dependencies": [],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T001-AC1",
                                    "criterion": "Root binding is validated.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-1"},
                                        {"type": "spec_ac", "id": "AC-1"},
                                        {"type": "design_decision", "id": "DD-1"},
                                    ],
                                    "verification_hint": "Validate good and bad proof roots.",
                                }
                            ],
                            "required_context_bundles": [],
                            "context": "Root proof binding.",
                        },
                        {
                            "id": "P1-T002",
                            "title": "Ledger semantics",
                            "description": "Reuse ledger evidence validation.",
                            "status": "in-progress",
                            "dependencies": ["P1-T001"],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T002-AC1",
                                    "criterion": "Ledger semantics are reused.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-2"},
                                        {"type": "spec_ac", "id": "AC-2"},
                                        {"type": "context_bundle", "id": "CTX-2"},
                                    ],
                                    "verification_hint": "Validate evidence and context-bundle failures.",
                                }
                            ],
                            "required_context_bundles": ["CTX-2"],
                            "context": "Evidence validation.",
                        },
                        {
                            "id": "P1-T003",
                            "title": "Final compatibility",
                            "description": "Keep final ledger validation authoritative.",
                            "status": "in-progress",
                            "dependencies": ["P1-T002"],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T003-AC1",
                                    "criterion": "Final validation remains authoritative.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-3"},
                                        {"type": "spec_ac", "id": "AC-3"},
                                    ],
                                    "verification_hint": "Validate final ledger without proof consultation.",
                                }
                            ],
                            "required_context_bundles": [],
                            "context": "Final ledger compatibility.",
                        },
                    ],
                }
            ],
        }

    def command_for(self, observed: str = "Command evidence inspected as inert data.") -> dict:
        return {
            "cwd": str(self.repo),
            "command": f"{sys.executable} -c \"from pathlib import Path; Path({str(self.sentinel)!r}).write_text('ran')\"",
            "exit_code": 0,
            "observed": observed,
        }

    def evidence(self, context_bundles: list[str] | None = None) -> dict:
        return {
            "files": ["tracked.txt"],
            "commands": [self.command_for()],
            "edge_cases": ["recorded command evidence was treated as data"],
            "context_bundles": context_bundles or ["CTX-1"],
            "mocks": "none",
        }

    def entry(self, criterion_id: str, *, package_id: str = "WP1") -> dict:
        task_id = criterion_id.rsplit("-AC", 1)[0]
        return {
            "criterion_id": criterion_id,
            "task_id": task_id,
            "package_id": package_id,
            "status": "verified",
            "method": "command",
            "source_refs": copy.deepcopy(self.plan_index["task_ac_sources"][criterion_id]),
            "state": {
                "git_ref": "HEAD",
                "commit": self.commit,
                "worktree": str(self.repo),
                "captured_at": "2026-05-16T00:00:00Z",
            },
            "evidence": self.evidence(
                ["CTX-1", "CTX-2"] if criterion_id == "P1-T002-AC1" else ["CTX-1"]
            ),
        }

    def proof(self) -> dict:
        return {
            "schema_version": 1,
            "feature": "proof-feature",
            "package_id": "WP1",
            "entries": [
                self.entry("P1-T001-AC1"),
                self.entry("P1-T002-AC1"),
            ],
        }

    def final_ledger(self) -> dict:
        return {
            "schema_version": 1,
            "feature": "proof-feature",
            "entries": [
                self.entry("P1-T001-AC1"),
                self.entry("P1-T002-AC1"),
                self.entry("P1-T003-AC1", package_id="WP2"),
            ],
        }

    def validate_proof(self, proof: object) -> list[str]:
        return validator.validate_package_proof_json(
            proof,
            self.plan_index,
            worktree=self.repo,
        )

    def assertInvalidProof(self, proof: object, expected: str) -> None:
        errors = self.validate_proof(proof)
        self.assertTrue(errors, "proof should be invalid")
        self.assertIn(expected, "\n".join(errors))

    def test_valid_proof_covers_owned_criteria_and_keeps_commands_inert(self) -> None:
        self.assertEqual([], self.validate_proof(self.proof()))
        self.assertFalse(self.sentinel.exists())

    def test_proof_file_path_must_match_feature_proofs_directory_and_filename(self) -> None:
        proofs_dir = self.feature_dir / "proofs"
        proofs_dir.mkdir()
        expected_path = proofs_dir / "WP1.proof.json"
        expected_path.write_text(json.dumps(self.proof(), indent=2), encoding="utf-8")
        self.assertEqual(
            [],
            validator.validate_package_proof_json_file(
                expected_path,
                self.plan_index,
                worktree=self.repo,
                tasks_path=self.tasks_path,
            ),
        )

        wrong_directory = self.repo / "not-the-feature-dir" / "WP1.proof.json"
        wrong_directory.parent.mkdir()
        wrong_directory.write_text(json.dumps(self.proof(), indent=2), encoding="utf-8")
        wrong_directory_errors = validator.validate_package_proof_json_file(
            wrong_directory,
            self.plan_index,
            worktree=self.repo,
            tasks_path=self.tasks_path,
        )
        self.assertIn("package proof path: expected", "\n".join(wrong_directory_errors))
        self.assertIn(str(expected_path), "\n".join(wrong_directory_errors))

        wrong_filename = proofs_dir / "WP01.proof.json"
        wrong_filename.write_text(json.dumps(self.proof(), indent=2), encoding="utf-8")
        wrong_filename_errors = validator.validate_package_proof_json_file(
            wrong_filename,
            self.plan_index,
            worktree=self.repo,
            tasks_path=self.tasks_path,
        )
        self.assertIn("package proof path: expected", "\n".join(wrong_filename_errors))
        self.assertIn(str(expected_path), "\n".join(wrong_filename_errors))

    def test_proof_file_validation_fails_closed_without_tasks_path(self) -> None:
        proofs_dir = self.feature_dir / "proofs"
        proofs_dir.mkdir()
        expected_path = proofs_dir / "WP1.proof.json"
        expected_path.write_text(json.dumps(self.proof(), indent=2), encoding="utf-8")

        missing_tasks_path_errors = validator.validate_package_proof_json_file(
            expected_path,
            self.plan_index,
            worktree=self.repo,
        )
        self.assertIn("tasks_path is required", "\n".join(missing_tasks_path_errors))

        wrong_directory = self.repo / "not-the-feature-dir" / "WP1.proof.json"
        wrong_directory.parent.mkdir()
        wrong_directory.write_text(json.dumps(self.proof(), indent=2), encoding="utf-8")
        wrong_directory_errors = validator.validate_package_proof_json_file(
            wrong_directory,
            self.plan_index,
            worktree=self.repo,
        )
        self.assertIn("tasks_path is required", "\n".join(wrong_directory_errors))

    def test_malformed_proof_json_and_document_shapes_are_rejected(self) -> None:
        proof_path = self.feature_dir / "proofs" / "WP1.proof.json"
        proof_path.parent.mkdir()
        proof_path.write_text("{", encoding="utf-8")
        errors = validator.validate_package_proof_json_file(
            proof_path,
            self.plan_index,
            worktree=self.repo,
            tasks_path=self.tasks_path,
        )
        self.assertIn("invalid JSON", "\n".join(errors))

        self.assertInvalidProof([], "package proof root: expected object")
        self.assertInvalidProof({"schema_version": 1, "feature": "proof-feature", "package_id": "WP1"}, "entries: expected array")
        self.assertInvalidProof({"schema_version": 1, "feature": "proof-feature", "package_id": "WP1", "entries": {}}, "entries: expected array")

        missing_schema = self.proof()
        missing_schema.pop("schema_version")
        self.assertInvalidProof(missing_schema, "schema_version")

        invalid_schema = self.proof()
        invalid_schema["schema_version"] = "1"
        self.assertInvalidProof(invalid_schema, "schema_version")

        wrong_types = self.proof()
        wrong_types["feature"] = 7
        wrong_types["package_id"] = 3
        self.assertInvalidProof(wrong_types, "package_id: expected non-empty string")

    def test_wrong_binding_missing_extra_and_duplicate_criteria_are_rejected(self) -> None:
        wrong_feature = self.proof()
        wrong_feature["feature"] = "other-feature"
        self.assertInvalidProof(wrong_feature, "feature: expected 'proof-feature'")

        wrong_package = self.proof()
        wrong_package["package_id"] = "WP2"
        self.assertInvalidProof(wrong_package, "not owned by package 'WP2'")

        missing = self.proof()
        missing["entries"] = missing["entries"][:1]
        self.assertInvalidProof(missing, "missing proof entry for acceptance criterion P1-T002-AC1")

        extra = self.proof()
        extra["entries"].append(self.entry("P1-T003-AC1", package_id="WP2"))
        self.assertInvalidProof(extra, "acceptance criterion 'P1-T003-AC1' is not owned by package 'WP1'")

        duplicate = self.proof()
        duplicate["entries"].append(copy.deepcopy(duplicate["entries"][0]))
        self.assertInvalidProof(duplicate, "duplicate criterion_id 'P1-T001-AC1'")

    def test_ledger_semantic_failures_are_reused_for_proof_entries(self) -> None:
        source_mismatch = self.proof()
        source_mismatch["entries"][0]["source_refs"] = [{"type": "spec_req", "id": "REQ-2"}]
        self.assertInvalidProof(source_mismatch, "source_refs: does not match")

        failed = self.proof()
        failed["entries"][0]["status"] = "failed"
        self.assertInvalidProof(failed, "cannot contain 'failed' entry")

        blocked = self.proof()
        blocked["entries"][0]["status"] = "blocked"
        self.assertInvalidProof(blocked, "cannot contain 'blocked' entry")

        malformed_manual = self.proof()
        malformed_manual["entries"][0]["status"] = "manual_required"
        malformed_manual["entries"][0]["method"] = "manual"
        malformed_manual["entries"][0]["evidence"]["commands"] = []
        self.assertInvalidProof(malformed_manual, "manual_evidence: expected object")

        vague_manual = self.proof()
        vague_manual["entries"][0]["status"] = "manual_required"
        vague_manual["entries"][0]["method"] = "manual"
        vague_manual["entries"][0]["evidence"]["commands"] = []
        vague_manual["entries"][0]["manual_evidence"] = {
            "criterion_ids": ["P1-T001-AC1"],
            "approval_provenance": "User approved in chat.",
            "observed_result": "approved",
            "scope": "all good",
            "limits": "none known",
            "state_reference": "approved",
            "approved_at": "2026-05-16T00:00:00Z",
            "approved": True,
        }
        self.assertInvalidProof(vague_manual, "approval-only or vague")

    def test_required_context_bundle_citations_are_rejected_when_missing(self) -> None:
        missing_package_context = self.proof()
        missing_package_context["entries"][0]["evidence"]["context_bundles"] = []
        self.assertInvalidProof(missing_package_context, "context bundle citation 'CTX-1'")

        missing_task_context = self.proof()
        missing_task_context["entries"][1]["evidence"]["context_bundles"] = ["CTX-1"]
        self.assertInvalidProof(missing_task_context, "context bundle citation 'CTX-2'")

    def test_stale_file_evidence_is_rejected(self) -> None:
        (self.repo / "tracked.txt").write_text("changed after proof\n", encoding="utf-8")
        self.assertInvalidProof(self.proof(), "stale evidence")

    def test_final_ledger_compatibility_does_not_consult_package_proofs(self) -> None:
        verification_path = self.feature_dir / "verification.json"
        verification_path.write_text(json.dumps(self.final_ledger(), indent=2), encoding="utf-8")
        proofs = self.feature_dir / "proofs"
        proofs.mkdir()
        (proofs / "WP1.proof.json").write_text("{", encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR_PATH),
                "--final",
                "--worktree",
                str(self.repo),
                str(self.tasks_path),
            ],
            cwd=self.repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("verification.json are valid", result.stdout)

    def test_final_ledger_rejects_existing_invalid_cases(self) -> None:
        self.assertEqual(
            [],
            validator.validate_verification_json(self.final_ledger(), self.plan_index, worktree=self.repo),
        )

        stale = self.final_ledger()
        (self.repo / "tracked.txt").write_text("changed after ledger\n", encoding="utf-8")
        self.assertIn(
            "stale evidence",
            "\n".join(
                validator.validate_verification_json(stale, self.plan_index, worktree=self.repo)
            ),
        )
        self.git("checkout", "--", "tracked.txt")

        failed = self.final_ledger()
        failed["entries"][0]["status"] = "failed"
        self.assertIn(
            "cannot contain 'failed'",
            "\n".join(
                validator.validate_verification_json(failed, self.plan_index, worktree=self.repo)
            ),
        )

        blocked = self.final_ledger()
        blocked["entries"][0]["status"] = "blocked"
        self.assertIn(
            "cannot contain 'blocked'",
            "\n".join(
                validator.validate_verification_json(blocked, self.plan_index, worktree=self.repo)
            ),
        )

        missing = self.final_ledger()
        missing["entries"].pop()
        self.assertIn(
            "missing ledger entry for acceptance criterion P1-T003-AC1",
            "\n".join(
                validator.validate_verification_json(missing, self.plan_index, worktree=self.repo)
            ),
        )

        malformed = []
        self.assertIn(
            "root: expected object",
            "\n".join(
                validator.validate_verification_json(malformed, self.plan_index, worktree=self.repo)
            ),
        )

        incomplete = self.final_ledger()
        incomplete["entries"][0].pop("evidence")
        self.assertIn(
            "evidence: expected object",
            "\n".join(
                validator.validate_verification_json(incomplete, self.plan_index, worktree=self.repo)
            ),
        )

        vague = self.final_ledger()
        vague["entries"][0]["status"] = "manual_required"
        vague["entries"][0]["method"] = "manual"
        vague["entries"][0]["evidence"]["commands"] = []
        vague["entries"][0]["manual_evidence"] = {
            "criterion_ids": ["P1-T001-AC1"],
            "approval_provenance": "User approved in chat.",
            "observed_result": "ok",
            "scope": "all good",
            "limits": "none known",
            "state_reference": "ok",
            "approved_at": "2026-05-16T00:00:00Z",
            "approved": True,
        }
        self.assertIn(
            "approval-only or vague",
            "\n".join(
                validator.validate_verification_json(vague, self.plan_index, worktree=self.repo)
            ),
        )


if __name__ == "__main__":
    unittest.main()
