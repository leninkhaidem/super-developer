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
- REQ-2: Reuse proof evidence semantics.
- REQ-3: Validate proof-native final gates.

## Acceptance Criteria
- AC-1: Package proof roots are validated.
- AC-2: Proof evidence semantics are reused.
- AC-3: Accepted package proofs are authoritative for final validation.
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
                    "title": "Final gate",
                    "description": "Validate proof-native final gates.",
                    "task_ids": ["P1-T003"],
                    "depends_on": ["WP1"],
                    "parallel_safe_with": [],
                    "primary_paths": ["plugins/super-developer/assets/validate-tasks-json.py"],
                    "verification_commands": [],
                    "risk_tags": ["validation"],
                    "required_context_bundles": [],
                    "targeted_review_required": True,
                    "rationale": "Final proof-gate checks are isolated coverage.",
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
                            "description": "Reuse proof evidence validation.",
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
                            "title": "Final proof gate",
                            "description": "Require accepted package proofs for final validation.",
                            "status": "in-progress",
                            "dependencies": ["P1-T002"],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T003-AC1",
                                    "criterion": "Final validation requires accepted package proofs.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-3"},
                                        {"type": "spec_ac", "id": "AC-3"},
                                    ],
                                    "verification_hint": "Validate final proof gates without ledger consultation.",
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

    def proof(self, package_id: str = "WP1") -> dict:
        if package_id == "WP1":
            entries = [
                self.entry("P1-T001-AC1", package_id="WP1"),
                self.entry("P1-T002-AC1", package_id="WP1"),
            ]
        elif package_id == "WP2":
            entries = [self.entry("P1-T003-AC1", package_id="WP2")]
        else:
            raise AssertionError(f"unknown package {package_id}")
        return {
            "schema_version": 1,
            "feature": "proof-feature",
            "package_id": package_id,
            "entries": entries,
        }

    def targeted_review(self, *, required: bool = True) -> dict:
        return {
            "required": required,
            "performed": True,
            "reviewer": "targeted package reviewer",
            "result": "passed",
            "evidence": "Targeted package review report: package delta and proof evidence passed.",
            "reviewed_at": "2026-05-16T00:00:00Z",
        }

    def proof_path(self, package_id: str = "WP1") -> Path:
        return self.feature_dir / "proofs" / f"{package_id}.proof.json"

    def write_proof_file(self, proof: dict, package_id: str = "WP1") -> Path:
        proof_path = self.proof_path(package_id)
        proof_path.parent.mkdir(exist_ok=True)
        proof_path.write_text(json.dumps(proof, indent=2), encoding="utf-8")
        return proof_path

    def lifecycle_state(self, proof: dict, state: str, **overrides: object) -> dict:
        timestamp_field = f"{state}_at"
        command = "accept-package" if state == "accepted" else "reopen-package"
        lifecycle = {
            "state": state,
            "package_id": proof["package_id"],
            "proof_path": str(validator.normalized_existing_or_candidate_path(self.proof_path(proof["package_id"]))),
            "proof_digest": validator.package_proof_digest(proof),
            timestamp_field: "2026-05-16T00:00:00Z",
            "writer": {
                "tool": validator.PACKAGE_LIFECYCLE_WRITER_TOOL,
                "command": command,
                "schema_version": validator.PACKAGE_LIFECYCLE_WRITER_SCHEMA_VERSION,
            },
            "state_binding": {
                "state": state,
                "worktree": str(validator.normalized_existing_or_candidate_path(self.repo)),
                "git_ref": "HEAD",
                "commit": self.commit,
            },
        }
        lifecycle.update(overrides)
        return lifecycle

    def proof_with_lifecycle(
        self, state: str, package_id: str = "WP1", **overrides: object
    ) -> dict:
        proof = self.proof(package_id)
        if state == "accepted":
            proof["targeted_review"] = self.targeted_review(required=True)
        proof["lifecycle"] = self.lifecycle_state(proof, state, **overrides)
        return proof

    def mark_plan_complete(self) -> None:
        self.tasks["status"] = "completed"
        for phase in self.tasks["phases"]:
            for task in phase["tasks"]:
                task["status"] = "done"
                task["completed_at"] = "2026-05-16T00:00:00Z"
        self.tasks_path.write_text(json.dumps(self.tasks, indent=2), encoding="utf-8")
        errors, plan_index = validator.validate_tasks_json(
            self.tasks,
            tasks_path=self.tasks_path,
            spec_path=self.feature_dir / "SPEC.md",
        )
        self.assertEqual([], errors)
        self.plan_index = plan_index

    def set_package_verification_commands(self, package_id: str, commands: list[str]) -> None:
        for package in self.tasks["work_packages"]:
            if package["id"] == package_id:
                package["verification_commands"] = commands
                break
        else:
            raise AssertionError(f"unknown package {package_id}")
        self.tasks_path.write_text(json.dumps(self.tasks, indent=2), encoding="utf-8")
        errors, plan_index = validator.validate_tasks_json(
            self.tasks,
            tasks_path=self.tasks_path,
            spec_path=self.feature_dir / "SPEC.md",
        )
        self.assertEqual([], errors)
        self.plan_index = plan_index

    def validate_proof_file(self, proof: dict, package_id: str = "WP1") -> list[str]:
        proof_path = self.write_proof_file(proof, package_id)
        return validator.validate_package_proof_json_file(
            proof_path,
            self.plan_index,
            worktree=self.repo,
            tasks_path=self.tasks_path,
        )

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

    def test_lifecycle_absent_accepted_and_reopened_states_are_validated(self) -> None:
        self.assertEqual([], self.validate_proof(self.proof()))
        self.assertEqual([], self.validate_proof_file(self.proof_with_lifecycle("accepted")))
        self.assertEqual([], self.validate_proof_file(self.proof_with_lifecycle("reopened")))

        malformed = self.proof()
        malformed["lifecycle"] = "accepted"
        self.assertIn("lifecycle: expected object", "\n".join(self.validate_proof_file(malformed)))

        unknown = self.proof()
        unknown["lifecycle"] = {"state": "finalized"}
        self.assertIn("lifecycle.state: expected one of", "\n".join(self.validate_proof_file(unknown)))

        wrong_package = self.proof_with_lifecycle("accepted")
        wrong_package["lifecycle"]["package_id"] = "WP2"
        self.assertIn(
            "lifecycle.package_id: expected package proof package_id 'WP1'",
            "\n".join(self.validate_proof_file(wrong_package)),
        )

    def test_lifecycle_provenance_digest_and_state_binding_fail_closed(self) -> None:
        missing_provenance = self.proof_with_lifecycle("accepted")
        missing_provenance["lifecycle"].pop("writer")
        self.assertIn(
            "lifecycle.writer: expected field",
            "\n".join(self.validate_proof_file(missing_provenance)),
        )

        manual_prepopulation = self.proof_with_lifecycle("accepted")
        manual_prepopulation["lifecycle"]["writer"] = {
            "tool": "manual-editor",
            "command": "accept-package",
            "schema_version": 1,
        }
        self.assertIn(
            "lifecycle.writer.tool: expected 'taskctl.py'",
            "\n".join(self.validate_proof_file(manual_prepopulation)),
        )

        wrong_digest = self.proof_with_lifecycle("accepted", proof_digest="sha256:" + "0" * 64)
        self.assertIn(
            "lifecycle.proof_digest: expected",
            "\n".join(self.validate_proof_file(wrong_digest)),
        )

        wrong_commit = self.proof_with_lifecycle("accepted")
        wrong_commit["lifecycle"]["state_binding"]["commit"] = "deadbeef"
        self.assertIn(
            "unable to verify accepted proof freshness",
            "\n".join(self.validate_proof_file(wrong_commit)),
        )

        wrong_path = self.proof_with_lifecycle("accepted", proof_path=str(self.repo / "other.proof.json"))
        self.assertIn(
            "lifecycle.proof_path: expected",
            "\n".join(self.validate_proof_file(wrong_path)),
        )

        changed_content = self.proof_with_lifecycle("accepted")
        changed_content["entries"][0]["evidence"]["edge_cases"].append("proof content changed after acceptance")
        self.assertIn(
            "lifecycle.proof_digest: expected",
            "\n".join(self.validate_proof_file(changed_content)),
        )

        (self.repo / "tracked.txt").write_text("changed after acceptance\n", encoding="utf-8")
        stale = self.proof_with_lifecycle("accepted")
        self.assertIn(
            "stale accepted proof state",
            "\n".join(self.validate_proof_file(stale)),
        )
        self.git("checkout", "--", "tracked.txt")

    def test_lifecycle_transition_table_and_idempotency_rules(self) -> None:
        self.assertEqual(
            {"none": {"accepted"}, "accepted": {"reopened"}, "reopened": {"accepted"}},
            validator.PACKAGE_LIFECYCLE_TRANSITIONS,
        )
        self.assertEqual([], validator.package_lifecycle_transition_errors(self.proof(), "accepted"))

        accepted = self.proof_with_lifecycle("accepted")
        self.assertEqual([], validator.package_lifecycle_transition_errors(accepted, "accepted"))
        self.assertEqual([], validator.package_lifecycle_transition_errors(accepted, "reopened"))
        self.assertIn(
            "accepted -> accepted is only allowed",
            "\n".join(
                validator.package_lifecycle_transition_errors(
                    {**accepted, "entries": accepted["entries"][:1]},
                    "accepted",
                )
            ),
        )

        reopened = self.proof_with_lifecycle("reopened")
        self.assertEqual([], validator.package_lifecycle_transition_errors(reopened, "accepted"))
        self.assertIn(
            "reopened -> reopened is not allowed",
            "\n".join(validator.package_lifecycle_transition_errors(reopened, "reopened")),
        )
        self.assertIn(
            "none -> reopened is not allowed",
            "\n".join(validator.package_lifecycle_transition_errors(self.proof(), "reopened")),
        )

    def test_lifecycle_freshness_requires_git_tracked_path_scoped_evidence(self) -> None:
        modified = self.proof_with_lifecycle("accepted")
        (self.repo / "tracked.txt").write_text("modified\n", encoding="utf-8")
        self.assertIn("stale accepted proof state", "\n".join(self.validate_proof_file(modified)))
        self.git("checkout", "--", "tracked.txt")

        renamed = self.proof_with_lifecycle("accepted")
        self.git("mv", "tracked.txt", "renamed.txt")
        self.assertIn("stale accepted proof state", "\n".join(self.validate_proof_file(renamed)))
        self.git("mv", "renamed.txt", "tracked.txt")

        deleted = self.proof_with_lifecycle("accepted")
        (self.repo / "tracked.txt").unlink()
        self.assertIn("stale accepted proof state", "\n".join(self.validate_proof_file(deleted)))
        self.git("checkout", "--", "tracked.txt")

        untracked = self.proof()
        (self.repo / "untracked.txt").write_text("not in git\n", encoding="utf-8")
        untracked["entries"][0]["evidence"]["files"] = ["untracked.txt"]
        untracked["lifecycle"] = self.lifecycle_state(untracked, "accepted")
        self.assertIn("stale accepted proof state", "\n".join(self.validate_proof_file(untracked)))

        url_only = self.proof()
        url_only["entries"][0]["evidence"]["files"] = ["https://example.com/evidence"]
        url_only["lifecycle"] = self.lifecycle_state(url_only, "accepted")
        self.assertIn(
            "accepted lifecycle requires path-scoped file evidence",
            "\n".join(self.validate_proof_file(url_only)),
        )

        manual = self.proof()
        manual["entries"][0]["status"] = "manual_required"
        manual["entries"][0]["method"] = "manual"
        manual["entries"][0]["evidence"]["commands"] = []
        manual["entries"][0]["manual_evidence"] = {
            "criterion_ids": ["P1-T001-AC1"],
            "approval_provenance": "Reviewer confirmed the tracked file evidence in the package proof.",
            "observed_result": "The reviewer inspected tracked.txt and confirmed the proof evidence matched.",
            "scope": "Package proof lifecycle acceptance evidence.",
            "limits": "Manual evidence cannot prove git path freshness.",
            "state_reference": "tracked.txt at commit " + self.commit,
            "approved_at": "2026-05-16T00:00:00Z",
            "approved": True,
        }
        manual["lifecycle"] = self.lifecycle_state(manual, "accepted")
        self.assertIn(
            "accepted lifecycle requires git-tracked file evidence, not manual evidence",
            "\n".join(self.validate_proof_file(manual)),
        )

    def test_accepted_package_requires_targeted_review_when_plan_requires_it(self) -> None:
        missing_review = self.proof()
        missing_review["lifecycle"] = self.lifecycle_state(missing_review, "accepted")
        self.assertIn(
            "targeted_review: required for targeted_review_required package",
            "\n".join(self.validate_proof_file(missing_review)),
        )

        malformed_review = self.proof_with_lifecycle("accepted")
        malformed_review["targeted_review"]["result"] = "failed"
        malformed_review["lifecycle"]["proof_digest"] = validator.package_proof_digest(malformed_review)
        self.assertIn(
            "targeted_review.result: expected 'passed'",
            "\n".join(self.validate_proof_file(malformed_review)),
        )

    def test_accepted_package_requires_required_verification_command_evidence(self) -> None:
        required_command = "python3 -m unittest discover plugins/super-developer/assets/tests"
        self.set_package_verification_commands("WP1", [required_command])

        missing_command = self.proof_with_lifecycle("accepted")
        self.assertIn(
            f"verification_commands: missing passing proof evidence for verification_commands entry {required_command!r}",
            "\n".join(self.validate_proof_file(missing_command)),
        )

        proven = self.proof()
        proven["targeted_review"] = self.targeted_review(required=True)
        proven["entries"][0]["evidence"]["commands"].append(
            {
                "cwd": str(self.repo),
                "command": required_command,
                "exit_code": 0,
                "observed": "Package verification command passed.",
            }
        )
        proven["lifecycle"] = self.lifecycle_state(proven, "accepted")
        self.assertEqual([], self.validate_proof_file(proven))

    def test_reopened_lifecycle_does_not_enforce_accepted_freshness(self) -> None:
        (self.repo / "tracked.txt").write_text("modified after lifecycle state\n", encoding="utf-8")
        self.git("add", "tracked.txt")
        self.git("commit", "-m", "update tracked evidence")
        current_commit = self.git("rev-parse", "HEAD").stdout.strip()
        reopened = self.proof_with_lifecycle("reopened")
        for entry in reopened["entries"]:
            entry["state"]["commit"] = current_commit
        reopened["lifecycle"]["proof_digest"] = validator.package_proof_digest(reopened)
        self.assertEqual([], self.validate_proof_file(reopened))

    def test_lifecycle_rejects_out_of_scope_release_two_persistence_fields(self) -> None:
        forbidden_fields = (
            "proof_history",
            "event_log",
            "generated_checklist",
            "targeted_review_state",
            "workflow_engine_state",
            "finalization",
        )
        for field in forbidden_fields:
            with self.subTest(field=field):
                proof = self.proof()
                proof[field] = []
                self.assertIn(
                    f"package proof.{field}: forbidden Release 2 lifecycle persistence field",
                    "\n".join(self.validate_proof_file(proof)),
                )

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

    def test_final_validation_requires_accepted_package_proofs(self) -> None:
        self.mark_plan_complete()
        self.write_proof_file(self.proof_with_lifecycle("accepted"), "WP1")
        self.write_proof_file(self.proof_with_lifecycle("accepted", "WP2"), "WP2")
        verification_path = self.feature_dir / "verification.json"
        invalid_ledger = self.final_ledger()
        invalid_ledger["entries"][0]["status"] = "failed"
        verification_path.write_text(json.dumps(invalid_ledger, indent=2), encoding="utf-8")

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
        self.assertIn("package proofs are valid", result.stdout)

    def test_final_validation_requires_completed_task_lifecycle(self) -> None:
        self.write_proof_file(self.proof_with_lifecycle("accepted"), "WP1")
        self.write_proof_file(self.proof_with_lifecycle("accepted", "WP2"), "WP2")

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
        self.assertNotEqual(0, result.returncode)
        self.assertIn("feature.status: expected 'completed'", result.stdout)
        self.assertIn("task P1-T001.status: expected 'done'", result.stdout)

    def test_final_validation_rejects_missing_or_reopened_package_proofs(self) -> None:
        self.mark_plan_complete()
        verification_path = self.feature_dir / "verification.json"
        verification_path.write_text(json.dumps(self.final_ledger(), indent=2), encoding="utf-8")
        proofs = self.feature_dir / "proofs"
        proofs.mkdir()
        self.write_proof_file(self.proof_with_lifecycle("accepted"), "WP1")

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
        self.assertNotEqual(0, result.returncode)
        self.assertIn("WP2: package proof: file not found", result.stdout)

        self.write_proof_file(self.proof_with_lifecycle("reopened", "WP2"), "WP2")
        reopened = subprocess.run(
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
        self.assertNotEqual(0, reopened.returncode)
        self.assertIn("expected 'accepted'", reopened.stdout)

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
