from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1]
SLICEPROOF_PATH = ASSETS_DIR / "sliceproof.py"
REPORT_EFFECTIVE_DIGEST = "sha256:" + "3" * 64
REPORT_AUTHORIZATION_ID = "auth-fixture-1"


def load_sliceproof_module():
    spec = importlib.util.spec_from_file_location("sliceproof_under_test", SLICEPROOF_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("Unable to load sliceproof.py for tests")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SLICEPROOF = load_sliceproof_module()


def remove_h2_section(text: str, section: str) -> str:
    return re.sub(rf"\n## {re.escape(section)}\n.*?(?=\n## |\Z)", "\n", text, count=1, flags=re.DOTALL)


def remove_h3_section(text: str, section: str) -> str:
    return re.sub(rf"\n### {re.escape(section)}\n.*?(?=\n### |\n## |\Z)", "\n", text, count=1, flags=re.DOTALL)


PLACEHOLDER_APPROVAL_VARIANTS = [
    "User-approved: pending; provenance: user note; scope: WP1 proof",
    "User-approved pending; provenance: user note; scope: WP1 proof",
    "User-approved - pending; provenance: user note; scope: WP1 proof",
    "Approved by TBD user; provenance: user note; scope: WP1 proof",
    "Approved by to-be-determined user; provenance: user note; scope: WP1 proof",
    "Approved by to_be_determined user; provenance: user note; scope: WP1 proof",
    "Approved by not-provided; provenance: user note; scope: WP1 proof",
    "Approved by not_supplied; provenance: user note; scope: WP1 proof",
    "Approved by user; provenance: none provided; scope: WP1 proof",
    "Approved by user; provenance: not provided; scope: WP1 proof",
    "Approved by user; provenance: not-provided; scope: WP1 proof",
    "Approved by user; provenance: not_supplied; scope: WP1 proof",
    "Approved by user; provenance: user note; scope: TBD after review",
    "Approved by user; provenance: user note; scope: not supplied",
    "Approved by user; provenance: user note; scope: not-supplied",
    "Approved by user; provenance: user note; scope: not_provided",
]


class SliceproofFixture:
    def __init__(self, *, separate_roots: bool = False) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.external_tmp = tempfile.TemporaryDirectory()
        self.workspace = Path(self.tmp.name)
        if separate_roots:
            self.repo = self.workspace / "code"
            self.artifact_root = self.workspace / "artifacts"
            self.repo.mkdir()
            self.artifact_root.mkdir()
        else:
            self.repo = self.workspace
            self.artifact_root = self.workspace
        self.external_worktree = Path(self.external_tmp.name)
        self.feature_dir = self.artifact_root / ".tasks" / "fixture"
        self.package_dir = self.feature_dir / "packages"
        self.proofs_dir = self.feature_dir / "proofs"
        self.reports_dir = self.feature_dir / "reports"
        self.semgrep_dir = self.feature_dir / "semgrep"
        self.slice_dir = self.artifact_root / ".planning" / "fixture" / "slices"
        self.package_path = self.package_dir / "WP1.md"
        self.proof_path = self.proofs_dir / "WP1.proof.md"
        self.report_path = self.reports_dir / "WP1.package-verification.md"
        self.tasks_path = self.feature_dir / "tasks.json"
        self.lifecycle_path = self.feature_dir / "lifecycle-state.json"
        self.slice_path = self.slice_dir / "helper.md"
        self.feature_dir.mkdir(parents=True)
        self.package_dir.mkdir()
        self.proofs_dir.mkdir()
        self.reports_dir.mkdir()
        self.semgrep_dir.mkdir()
        self.slice_dir.mkdir(parents=True)
        self.evidence_asset = self.repo / "plugins" / "super-developer" / "assets" / "sliceproof.py"
        self.evidence_test = self.repo / "plugins" / "super-developer" / "assets" / "tests" / "test_sliceproof.py"
        self.evidence_ref = self.repo / "plugins" / "super-developer" / "references" / "tool-usage.md"
        self.evidence_test.parent.mkdir(parents=True)
        self.evidence_ref.parent.mkdir(parents=True)
        self.evidence_asset.write_text("def validate_plan():\n    pass\n\ndef validate_proof():\n    pass\n", encoding="utf-8")
        self.evidence_test.write_text("def test_validate_plan_accepts_valid_registry_package_slice_fixture():\n    pass\n", encoding="utf-8")
        self.evidence_ref.write_text("# Tool Usage\n\n## sliceproof.py\n", encoding="utf-8")
        (self.feature_dir / "SPEC.md").write_text("# Fixture Spec\n", encoding="utf-8")
        self.slice_path.write_text(self.slice_text(), encoding="utf-8")
        self.package_path.write_text(self.package_text(), encoding="utf-8")
        self.write_plan(self.plan())
        self.init_candidate_git()

    def cleanup(self) -> None:
        self.tmp.cleanup()
        self.external_tmp.cleanup()

    def run(
        self,
        *args: str,
        env: dict[str, str] | None = None,
        cwd: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SLICEPROOF_PATH), *args],
            cwd=cwd or self.repo,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )

    def root_args(self) -> tuple[str, str, str, str]:
        return ("--artifact-root", str(self.artifact_root), "--code-root", str(self.repo))

    def git_checked(self, *args: str) -> str:
        result = subprocess.run(
            ["git", *args],
            cwd=self.repo,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {result.stdout}{result.stderr}")
        return result.stdout.strip()

    def init_candidate_git(self) -> None:
        self.git_checked("init", "-b", "wp/fixture/WP1")
        self.git_checked("config", "user.email", "sliceproof@example.invalid")
        self.git_checked("config", "user.name", "Sliceproof Fixture")
        self.git_checked("config", "commit.gpgsign", "false")
        self.git_checked("add", ".")
        self.git_checked("commit", "-m", "candidate base")
        self.report_base = self.git_checked("rev-parse", "HEAD")
        with self.evidence_asset.open("a", encoding="utf-8") as handle:
            handle.write("\n# candidate fixture change\n")
        self.git_checked("add", str(self.evidence_asset.relative_to(self.repo)))
        self.git_checked("commit", "-m", "candidate change")
        self.report_commit = self.git_checked("rev-parse", "HEAD")
        self.report_tree = self.git_checked("rev-parse", "HEAD^{tree}")
        self.report_diff_digest = SLICEPROOF.raw_git_diff_identity(
            self.repo,
            self.report_base,
            self.report_commit,
            "fixture diff",
        )
        self.report_ref = "wp/fixture/WP1"

    def init_git(self, branch: str = "wp/fixture/WP1") -> None:
        if branch != self.report_ref:
            self.git_checked("checkout", "-b", branch)

    def git_at(self, root: Path, *args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=root, check=False, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        if result.returncode != 0:
            raise AssertionError(f"git {' '.join(args)} failed: {result.stdout}{result.stderr}")
        return result.stdout.strip()

    def init_lifecycle_git_roots(self) -> None:
        if self.artifact_root == self.repo:
            raise AssertionError("Lifecycle authority fixture requires separate roots")
        self.git_at(self.artifact_root, "init", "-b", "main")
        for root in (self.artifact_root, self.repo):
            self.git_at(root, "config", "user.email", "sliceproof@example.invalid")
            self.git_at(root, "config", "user.name", "Sliceproof Fixture")
            self.git_at(root, "config", "commit.gpgsign", "false")

    def write_lifecycle(self, state: dict) -> None:
        self.lifecycle_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    def publish_code_checkpoint(self, ref: str, sha: str) -> dict[str, str]:
        self.git_at(self.repo, "update-ref", ref, sha)
        return {"ref": ref, "sha": sha}

    def write_controlled_completion(
        self,
        *,
        package_states: dict[str, str] | None = None,
        package_modes: dict[str, str] | None = None,
        assurance_profile: str = "standard",
        checkpoint_sha: str | None = None,
        include_checkpoint: bool = True,
    ) -> None:
        if self.artifact_root == self.repo:
            raise AssertionError("Controlled Lifecycle State fixture requires separate roots")
        if not hasattr(self, "controlled_lifecycle_initial"):
            self.init_lifecycle_git_roots()
            self.controlled_lifecycle_initial = self.lifecycle_state()
            self.write_lifecycle(self.controlled_lifecycle_initial)
            self.controlled_lifecycle_commit = self.commit_lifecycle("controlled lifecycle generation one")
        else:
            self.git_at(self.artifact_root, "reset", "--hard", self.controlled_lifecycle_commit)

        modes = package_modes or {"WP1": "boundary"}
        states = package_states or {package_id: "stabilized" for package_id in modes}
        progression = ["pending", "in_progress", "stabilized", "verified", "done"]
        unknown_states = set(states.values()) - set(progression)
        if unknown_states:
            raise AssertionError(f"unsupported controlled fixture target states: {sorted(unknown_states)}")
        if set(states) != set(modes):
            raise AssertionError("controlled fixture package states and modes must name the same packages")

        state = self.authorized_lifecycle_state(
            self.controlled_lifecycle_initial,
            self.controlled_lifecycle_commit,
        )
        state["assurance_profile"] = assurance_profile
        state["package_modes"] = modes
        if assurance_profile == "low":
            state["budgets"]["implementation"]["maxima"]["repair_waves"] = 1
        state["packages"] = {
            package_id: {"state": "pending", "wave": None}
            for package_id in modes
        }
        state["authorization"]["inputs"]["routing"] = SLICEPROOF.canonical_json_digest({
            "assurance_profile": assurance_profile,
            "package_modes": modes,
        })
        state["authorization"]["inputs"]["budget_authority"] = (
            SLICEPROOF.authorization_budget_authority_digest(state["budgets"])
        )
        effective_digest = SLICEPROOF.canonical_json_digest(state["authorization"]["inputs"])
        state["authorization"]["initial_digest"] = effective_digest
        state["authorization"]["effective_digest"] = effective_digest
        state["code_checkpoint"] = None
        if include_checkpoint:
            checkpoint_ref = "refs/heads/checkpoints/fixture/integration/g2"
            state["code_checkpoint"] = self.publish_code_checkpoint(
                checkpoint_ref,
                checkpoint_sha or self.report_commit,
            )

        previous_state = self.controlled_lifecycle_initial
        previous_commit = self.controlled_lifecycle_commit
        maximum_step = max(progression.index(target) for target in states.values())
        for step in range(maximum_step + 1):
            if step:
                state = copy.deepcopy(previous_state)
                state["generation"] = previous_state["generation"] + 1
                state["stage"] = "package-wave-quiescent"
                state["next_legal_actions"] = ["dispatch"]
                state["budgets"]["active_reservation"] = None
                state["packages"] = {
                    package_id: {
                        "state": progression[min(step, progression.index(target))],
                        "wave": None,
                    }
                    for package_id, target in states.items()
                }
                state["last_verified"] = {
                    "artifact_ref": "refs/heads/artifacts/fixture",
                    "artifact_sha": previous_commit,
                    "state_digest": SLICEPROOF.canonical_json_digest(previous_state),
                    "generation": previous_state["generation"],
                }
            self.write_lifecycle(state)
            if step < maximum_step:
                previous_state = copy.deepcopy(state)
                previous_commit = self.commit_lifecycle(f"controlled lifecycle generation {state['generation']}")

        self.controlled_effective_digest = effective_digest
        for report_path in sorted(self.reports_dir.glob("*.package-verification.md")):
            report_text = report_path.read_text(encoding="utf-8")
            report_text, replacements = re.subn(
                rf"(Authorization / Effective Digest: `{re.escape(REPORT_AUTHORIZATION_ID)} \| )sha256:[0-9a-f]{{64}}(`)",
                rf"\g<1>{effective_digest}\2",
                report_text,
            )
            if replacements:
                report_path.write_text(report_text, encoding="utf-8")

    def write_agentic_completion(
        self,
        profile: str,
        *,
        specialist_lenses: list[str] | None = None,
        clusters: list[dict] | None = None,
        completion_at: str = "2026-07-18T14:05:00Z",
        graph_mutator=None,
    ) -> dict:
        if self.artifact_root == self.repo:
            raise AssertionError("Agentic completion fixture requires separate roots")
        modes = {"WP1": "final"} if profile == "low" else {"WP1": "boundary"}
        if profile == "low":
            self.configure_primary_final(assurance_profile="low", status="done")
            self.proof_path.write_text(self.completed_proof(), encoding="utf-8")
        else:
            plan = self.plan()
            plan["assurance_profile"] = profile
            plan["work_packages"][0]["status"] = "done"
            self.write_plan(plan)
            self.package_path.write_text(self.package_text(), encoding="utf-8")
            proof = self.completed_proof()
            self.proof_path.write_text(proof, encoding="utf-8")
            self.report_path.write_text(
                self.report_text(proof, assurance_profile=profile), encoding="utf-8"
            )
        self.write_controlled_completion(
            package_states={"WP1": "done"},
            package_modes=modes,
            assurance_profile=profile,
        )
        done_state = json.loads(self.lifecycle_path.read_text(encoding="utf-8"))
        done_commit = self.commit_lifecycle("controlled done state")

        state = copy.deepcopy(done_state)
        state["generation"] += 1
        state["stage"] = "completed"
        state["quiescent"] = True
        state["next_legal_actions"] = []
        state["owner"]["disposition"] = "released"
        state["budgets"]["active_reservation"] = None
        state["budgets"]["implementation"]["issued"]["command_units"] = 1
        state["wave"] = None
        state["serious_clusters"] = copy.deepcopy(clusters or [])
        state["last_verified"] = {
            "artifact_ref": "refs/heads/artifacts/fixture",
            "artifact_sha": done_commit,
            "state_digest": SLICEPROOF.canonical_json_digest(done_state),
            "generation": done_state["generation"],
        }

        runtime_path = ".tasks/fixture/evidence/runtime.json"
        command_path = ".tasks/fixture/evidence/commands.json"
        runtime_digest = self.write_canonical_json(runtime_path, {"result": "PASS"})
        command_digest = self.write_canonical_json(command_path, {"command": "focused", "result": "PASS"})
        registry, _packages = SLICEPROOF.load_and_validate_plan(
            Path(".tasks/fixture/tasks.json"),
            artifact_root=self.artifact_root,
            code_root=self.repo,
        )
        manifest, manifest_errors = SLICEPROOF.expected_semantic_artifact_manifest(registry)
        if manifest_errors:
            raise AssertionError(manifest_errors)
        boundary_errors: list[str] = []
        boundary_receipts = SLICEPROOF.expected_boundary_receipts(registry, boundary_errors)
        if boundary_errors:
            raise AssertionError(boundary_errors)
        freeze_id = f"freeze-{profile}"
        freeze_path = SLICEPROOF.canonical_freeze_path("fixture", freeze_id)
        checkpoint = state["code_checkpoint"]
        freeze = {
            "schema_version": 1,
            "kind": "agentic-freeze",
            "id": freeze_id,
            "authorization": {
                "id": state["authorization"]["id"],
                "effective_digest": state["authorization"]["effective_digest"],
            },
            "code": {
                "checkpoint_ref": checkpoint["ref"],
                "commit": checkpoint["sha"],
                "tree": self.git_at(self.repo, "rev-parse", f"{checkpoint['sha']}^{{tree}}"),
                "base_commit": self.report_base,
                "raw_diff_digest": SLICEPROOF.raw_git_diff_identity(
                    self.repo, self.report_base, checkpoint["sha"], "completion fixture"
                ),
                "clean_status_digest": SLICEPROOF.digest_bytes(b""),
            },
            "semantic_artifacts": manifest,
            "runtime_evidence": [{"path": runtime_path, "digest": runtime_digest}],
            "assurance": {
                "profile": profile,
                "package_modes": modes,
                "required_boundary_receipts": boundary_receipts,
                "specialist_lenses": sorted(
                    specialist_lenses
                    if specialist_lenses is not None
                    else (["privacy"] if profile == "high" else [])
                ),
            },
            "serious_clusters_digest": SLICEPROOF.canonical_json_digest(state["serious_clusters"]),
            "command_results": [{"path": command_path, "digest": command_digest}],
            "frozen_at": "2026-07-18T14:00:00Z",
        }
        freeze_digest = self.write_canonical_json(freeze_path, freeze)
        state["freeze"] = {"id": freeze_id, "path": freeze_path, "digest": freeze_digest}
        freeze_predecessor = SLICEPROOF.predecessor_pointer(
            "F", "freeze", freeze_path, freeze_digest
        )
        receipt_files: dict[str, dict] = {}
        pointers: list[dict] = []

        def add_receipt(
            role: str,
            lens: str,
            predecessors: list[dict],
            recorded_at: str,
        ) -> dict:
            path = SLICEPROOF.canonical_receipt_path("fixture", freeze_id, role, lens)
            data = {
                "schema_version": 1,
                "role": role,
                "lens": lens,
                "freeze_id": freeze_id,
                "freeze_digest": freeze_digest,
                "authorization": freeze["authorization"],
                "predecessors": predecessors,
                "recorded_at": recorded_at,
            }
            if role == "C":
                data["verdicts"] = {"code_risk": "PASS", "completion": "PASS"}
            elif role in {"R", "S", "U"}:
                data["verdict"] = "PASS"
            else:
                data["deviations"] = []
                data["limitations"] = []
            digest = self.write_canonical_json(path, data)
            pointer = {
                "role": role,
                "lens": lens,
                "path": path,
                "digest": digest,
                "freeze_digest": freeze_digest,
            }
            receipt_files[path] = data
            pointers.append(pointer)
            return SLICEPROOF.predecessor_pointer(role, lens, path, digest)

        if profile == "low":
            combined = add_receipt(
                "C", "combined-low-assurance", [freeze_predecessor], "2026-07-18T14:01:00Z"
            )
            add_receipt(
                "V", "verification-summary", [freeze_predecessor, combined], completion_at
            )
        else:
            review = add_receipt(
                "R", "integrated-code-risk", [freeze_predecessor], "2026-07-18T14:01:00Z"
            )
            specialists = []
            for index, lens in enumerate(freeze["assurance"]["specialist_lenses"], start=2):
                specialists.append(add_receipt(
                    "S", lens, [freeze_predecessor, review], f"2026-07-18T14:0{index}:00Z"
                ))
            audit = add_receipt(
                "U",
                "accepted-outcome-reconciliation",
                [freeze_predecessor, review, *specialists],
                "2026-07-18T14:04:00Z",
            )
            add_receipt(
                "V",
                "verification-summary",
                [freeze_predecessor, review, *specialists, audit],
                completion_at,
            )
        state["receipts"] = pointers
        if graph_mutator is not None:
            graph_mutator(state, freeze, receipt_files)

        freeze_digest = self.write_canonical_json(freeze_path, freeze)
        state["freeze"]["digest"] = freeze_digest
        for pointer in state["receipts"]:
            data = receipt_files.get(pointer["path"])
            if data is not None:
                pointer["digest"] = self.write_canonical_json(pointer["path"], data)
        self.write_lifecycle(state)
        self.git_at(self.artifact_root, "add", ".")
        self.git_at(self.artifact_root, "commit", "-m", f"checkpoint {profile} V")
        completion_commit = self.git_at(self.artifact_root, "rev-parse", "HEAD")
        self.git_at(
            self.artifact_root,
            "update-ref",
            "refs/heads/artifacts/fixture",
            completion_commit,
        )
        return state

    def validate_agentic_completion(self) -> subprocess.CompletedProcess[str]:
        return self.run(
            "validate-agentic-completion", *self.root_args(), "--feature", "fixture"
        )

    def validate_lifecycle(self, previous_commit: str | None = None) -> subprocess.CompletedProcess[str]:
        args = ["validate-lifecycle-state", *self.root_args(), "--feature", "fixture"]
        if previous_commit is not None:
            args.extend(["--previous-commit", previous_commit])
        return self.run(*args)

    def commit_lifecycle(self, message: str) -> str:
        self.git_at(self.artifact_root, "add", ".tasks/fixture/lifecycle-state.json")
        self.git_at(self.artifact_root, "commit", "-m", message)
        return self.git_at(self.artifact_root, "rev-parse", "HEAD")

    def lifecycle_state(self) -> dict:
        return {
            "schema_version": 1,
            "generation": 1,
            "feature": "fixture",
            "stage": "planning",
            "quiescent": True,
            "next_legal_actions": ["plan-review"],
            "owner": {
                "token": "owner-1", "host": "host-a", "disposition": "active", "takeover": None,
            },
            "artifact_checkpoint": {
                "ref": "refs/heads/artifacts/fixture", "sha": None, "tree": None,
            },
            "code_checkpoint": None,
            "authorization": {
                "id": None, "initial_digest": None, "effective_digest": None,
                "inputs": None, "amendment_link": None,
            },
            "budgets": {
                "preauthorization": {
                    "maxima": {
                        "delegated_calls": 8, "planner_correction_waves": 2,
                        "spike_waves": 2, "command_units": 20,
                    },
                    "issued": {
                        "delegated_calls": 1, "planner_correction_waves": 0,
                        "spike_waves": 0, "command_units": 1,
                    },
                    "started_at": "2026-07-18T10:00:00Z",
                    "deadline_at": "2026-07-18T12:00:00Z",
                },
                "implementation": None,
                "active_reservation": None,
                "control_plane_reserve": {"maximum": 1, "issued": 0, "reservation": None},
            },
            "packages": {},
            "wave": None,
            "serious_clusters": [],
            "freeze": None,
            "receipts": [],
            "last_verified": None,
            "portability_authorization": "explicit fixture instruction",
        }

    def authorized_lifecycle_state(self, previous: dict, previous_commit: str) -> dict:
        state = copy.deepcopy(previous)
        state["generation"] = previous["generation"] + 1
        state["stage"] = "authorized"
        state["next_legal_actions"] = ["activate"]
        state["artifact_checkpoint"] = {
            "ref": "refs/heads/artifacts/fixture",
            "sha": previous_commit,
            "tree": self.git_at(self.artifact_root, "rev-parse", f"{previous_commit}^{{tree}}"),
        }
        state["packages"] = {"WP1": {"state": "pending", "wave": None}}
        state["assurance_profile"] = "standard"
        state["package_modes"] = {"WP1": "boundary"}
        state["budgets"]["implementation"] = {
            "maxima": {
                "repair_waves": 2, "delegated_calls": 6, "command_units": 30, "cost_units": 0,
            },
            "issued": {
                "repair_waves": 0, "delegated_calls": 1, "command_units": 0, "cost_units": 0,
            },
            "started_at": "2026-07-18T12:30:00Z",
            "deadline_at": "2026-07-18T16:00:00Z",
        }
        state["budgets"]["active_reservation"] = {
            "id": "reservation-2", "owner_token": "owner-1", "budget": "implementation",
            "generation": state["generation"], "units": {"delegated_calls": 1},
        }
        inputs = {
            "artifact_commit": state["artifact_checkpoint"]["sha"],
            "artifact_tree": state["artifact_checkpoint"]["tree"],
            "base_commit": self.git_at(self.repo, "rev-parse", "HEAD"),
            "clean_status": self.digest_text("clean status"),
            "dependencies": self.digest_text("dependencies and prerequisites"),
            "routing": SLICEPROOF.canonical_json_digest({
                "assurance_profile": state["assurance_profile"],
                "package_modes": state["package_modes"],
            }),
            "actions": self.digest_text("covered actions"),
            "budget_authority": SLICEPROOF.authorization_budget_authority_digest(state["budgets"]),
            "amendment_policy": self.digest_text("amendment policy"),
        }
        authorization_digest = SLICEPROOF.canonical_json_digest(inputs)
        state["authorization"] = {
            "id": "auth-fixture-1",
            "initial_digest": authorization_digest,
            "effective_digest": authorization_digest,
            "inputs": inputs,
            "amendment_link": None,
        }
        state["last_verified"] = {
            "artifact_ref": "refs/heads/artifacts/fixture",
            "artifact_sha": previous_commit,
            "state_digest": SLICEPROOF.canonical_json_digest(previous),
            "generation": previous["generation"],
        }
        return state

    def plan(self) -> dict:
        return {
            "feature": "fixture",
            "title": "Fixture",
            "status": "planned",
            "spec_path": ".tasks/fixture/SPEC.md",
            "authoritative_slices": [".planning/fixture/slices/helper.md"],
            "assurance_profile": "standard",
            "work_packages": [
                {
                    "id": "WP1",
                    "path": ".tasks/fixture/packages/WP1.md",
                    "proof_path": ".tasks/fixture/proofs/WP1.proof.md",
                    "report_path": ".tasks/fixture/reports/WP1.package-verification.md",
                    "verification_mode": "boundary",
                    "status": "pending",
                    "depends_on": [],
                }
            ],
        }

    def write_plan(self, plan: dict) -> None:
        self.tasks_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    def slice_text(self) -> str:
        return textwrap.dedent(
            """
            # Slice: Helper Behavior

            ### HELPER-OUTSIDE-998 — non-shared-understanding headings are ignored

            ## Shared Understanding
            ```md
            ### HELPER-CODE-999 — fenced code headings are examples only
            ```

            ### HELPER-PLAN-001 — Registry and package references validate mechanically
            The helper validates paths, required package sections, dependencies, and H3 IDs.

            ### HELPER-PROOF-002 - Proof placeholders and proof closure are mechanical
            The helper creates placeholders and checks completion markers without semantic scoring.

            ### HELPER-CONTEXT-003
            Context-only IDs must be readable but do not create required proof rows.

            ### HELPER-PIPE-004 — Proof rows preserve A | B table content
            Escaped pipe characters in generated proof table cells must round-trip through validation.

            ### HELPER-INTERFACE-005 — Interface-bearing rows require exactness
            Fixture report validation must identify interface-bearing Slice rows.

            **Interface contract**
            - Must exist: a stable fixture command interface.
            - Consumer: helper tests.
            - Exact interface: `validate-package-complete` returns JSON.
            - Forbidden behaviors: missing matrix rows or dirty evidence must not pass.
            - Expected evidence: code/test/static evidence anchors plus forbidden-behavior falsification.
            """
        ).lstrip()

    def package_text(
        self,
        *,
        missing_section: str | None = None,
        must_id: str | None = "HELPER-PLAN-001",
        context_id: str | None = "HELPER-CONTEXT-003",
        primary_paths: list[str] | None = None,
        verification_mode: str = "boundary",
        report_path: str | None = ".tasks/fixture/reports/WP1.package-verification.md",
        verification_rationale: str | None = None,
    ) -> str:
        must_line = (
            "- Registry and package references validate mechanically"
            if must_id is None
            else f"- `{must_id}` — Registry and package references validate mechanically"
        )
        context_line = (
            "- Context-only IDs stay required reading"
            if context_id is None
            else f"- `{context_id}` — Context-only IDs stay required reading"
        )
        primary_paths = primary_paths or ["plugins/super-developer/assets/sliceproof.py"]
        if verification_rationale is None:
            verification_rationale = (
                "Consumed helper contract boundary requires an independent package receipt."
                if verification_mode == "boundary"
                else "Owner: Code Reviewer; semantic verification is deferred to final assurance for this coherent leaf."
            )
        report_value = report_path if report_path is not None else "None — final assurance"
        sections = {
            "Scope": "Validate the Slice-first helper behavior with deterministic fixtures.",
            "Assigned Slices": textwrap.dedent(
                f"""
                ### `.planning/fixture/slices/helper.md`
                Must satisfy:
                {must_line}
                - `HELPER-PROOF-002` — Proof placeholders and proof closure are mechanical

                Context only:
                {context_line}
                """
            ).strip(),
            "Primary Paths": "\n".join(f"- `{path}`" for path in primary_paths),
            "Verification Expectations": textwrap.dedent(
                """
                - `sliceproof.py validate-plan` succeeds for the valid fixture.
                - `sliceproof.py validate-proof` fails placeholders and passes completed proof.
                """
            ).strip(),
            "Proof": "- `.tasks/fixture/proofs/WP1.proof.md`",
            "Independent Verification": textwrap.dedent(
                f"""
                - Mode: `{verification_mode}`
                - Report: `{report_value}`
                - Rationale: {verification_rationale}
                """
            ).strip(),
            "Dependencies": "- None.",
        }
        if missing_section:
            sections.pop(missing_section)
        body = ["# Work Package: WP1 — Helper behavior", ""]
        for name, value in sections.items():
            body.extend([f"## {name}", value, ""])
        return "\n".join(body)

    def completed_proof(
        self,
        *,
        status: str = "PASS",
        implementation: str = "sliceproof.py validates registry/package/Slice references.",
        verification: str = "unittest fixture observed the helper command exit 0.",
        gaps: str = "- None.",
    ) -> str:
        return textwrap.dedent(
            f"""
            # Package Proof: WP1 — Helper behavior

            ## Package Scope
            Validate the Slice-first helper behavior with deterministic fixtures.

            ## Assigned Slice Scope
            - `.planning/fixture/slices/helper.md`
              - Must satisfy: `HELPER-PLAN-001` — Registry and package references validate mechanically
              - Must satisfy: `HELPER-PROOF-002` — Proof placeholders and proof closure are mechanical
              - Context only: `HELPER-CONTEXT-003` — Context-only IDs stay required reading

            ## Slice Closure Table

            | Slice ID | Required understanding | Implementation evidence | Verification evidence | Status |
            |---|---|---|---|---|
            | `HELPER-PLAN-001` | Registry and package references validate mechanically | {implementation} | {verification} | {status} |
            | `HELPER-PROOF-002` | Proof placeholders and proof closure are mechanical | sliceproof.py creates placeholders and checks completion markers. | unittest fixture observed completed proof validation exit 0. | PASS |

            ## Acceptance / Verification Closure

            | Expectation | Evidence | Status |
            |---|---|---|
            | `sliceproof.py validate-plan` succeeds for the valid fixture. | unittest fixture observed validate-plan exit 0. | PASS |
            | `sliceproof.py validate-proof` fails placeholders and passes completed proof. | unittest fixture covers placeholder failure and completed proof pass. | PASS |

            ## Commands Run
            - python3 -m unittest discover -s plugins/super-developer/assets/tests (fixture subset observed pass)

            ## Files Changed / Inspected
            - plugins/super-developer/assets/sliceproof.py
            - plugins/super-developer/assets/tests/test_sliceproof.py

            ## Gaps, Deviations, or Deferred Items
            {gaps}

            ## Package Agent Completion Statement
            - Mechanical helper evidence recorded for all required rows.
            """
        ).lstrip()

    def digest_text(self, text: str) -> str:
        return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

    def write_canonical_json(self, relative_path: str, data: dict) -> str:
        path = self.artifact_root / relative_path
        path.parent.mkdir(parents=True, exist_ok=True)
        raw = SLICEPROOF.canonical_json_bytes(data)
        path.write_bytes(raw)
        return "sha256:" + hashlib.sha256(raw).hexdigest()

    def serious_cluster(
        self,
        *,
        observed_classes: list[str] | None = None,
        selected_class: str | None = None,
        signatures: list[str] | None = None,
        strikes: int = 1,
        disposition: str = "repair-eligible",
        repair: dict | None = None,
        closure: dict | None = None,
    ) -> dict:
        cluster = {
            "accepted_invariant": "Accepted helper output remains exact.",
            "root_mechanism": "candidate binding omits the exact helper output",
            "architectural_surface": "helper completion boundary",
        }
        classes = observed_classes or ["implementation-defect"]
        strongest_rank = min(SLICEPROOF.CLUSTER_CLASS_PRECEDENCE_RANK[name] for name in classes)
        selected = selected_class or next(
            name for name in classes
            if SLICEPROOF.CLUSTER_CLASS_PRECEDENCE_RANK[name] == strongest_rank
        )
        cluster.update({
            "id": SLICEPROOF.canonical_serious_cluster_id(cluster),
            "observed_signatures": signatures or [self.digest_text("observed helper failure")],
            "observed_classes": classes,
            "class": selected,
            "route": SLICEPROOF.CLUSTER_ROUTES[selected],
            "strikes": strikes,
            "disposition": disposition,
            "repair": repair,
            "closure": closure,
        })
        return cluster

    def package_markdown_digest(self) -> str:
        return self.digest_text(self.package_path.read_text(encoding="utf-8"))

    def package_markdown(self):
        return SLICEPROOF.parse_package_markdown(self.package_path, "WP1")

    def registry_package(self):
        return SLICEPROOF.RegistryPackage(
            package_id="WP1",
            path=".tasks/fixture/packages/WP1.md",
            proof_path=".tasks/fixture/proofs/WP1.proof.md",
            report_path=".tasks/fixture/reports/WP1.package-verification.md",
            status="pending",
            depends_on=[],
            verification_mode="boundary",
        )

    def assigned_slice_digests(self, assigned_slices: str = ".planning/fixture/slices/helper.md") -> str:
        if assigned_slices == "none":
            return "none"
        return SLICEPROOF.assigned_slice_digests_binding(self.artifact_root, self.package_markdown())

    def matrix_source_snapshot(self, assigned_slices: str = ".planning/fixture/slices/helper.md") -> str:
        if assigned_slices == "none":
            package_content = self.package_path.read_text(encoding="utf-8")
            return self.digest_text(f".tasks/fixture/packages/WP1.md\0{package_content}\0")
        return SLICEPROOF.matrix_source_snapshot_binding(self.artifact_root, self.registry_package(), self.package_markdown())

    def deliverable_matrix(self, *, assigned_slices: str = ".planning/fixture/slices/helper.md") -> str:
        rows = [
            "| Source ID | Row Type | Deliverable | Evidence Type | Evidence Refs | Exactness / Risk Disposition | Verdict |",
            "|---|---|---|---|---|---|---|",
        ]
        if assigned_slices != "none":
            rows.extend(
                [
                    "| HELPER-PLAN-001 | slice | Registry and package references validate mechanically. | mixed | static:plugins/super-developer/assets/sliceproof.py#validate_plan; test:plugins/super-developer/assets/tests/test_sliceproof.py::test_validate_plan_accepts_valid_registry_package_slice_fixture | no interface; fixture plan behavior covered | delivered |",
                    "| HELPER-PROOF-002 | slice | Proof placeholders and proof closure validate mechanically. | static | static:plugins/super-developer/assets/sliceproof.py#validate_proof | no interface; fixture proof behavior covered | delivered |",
                ]
            )
        rows.extend(
            [
                "| VE-1 | verification-expectation | `sliceproof.py validate-plan` succeeds for the valid fixture. | test | test:plugins/super-developer/assets/tests/test_sliceproof.py::test_validate_plan_accepts_valid_registry_package_slice_fixture | expectation covered; no interface | delivered |",
                "| VE-2 | verification-expectation | `sliceproof.py validate-proof` fails placeholders and passes completed proof. | static | static:plugins/super-developer/assets/sliceproof.py#validate_proof | expectation covered; no interface | delivered |",
            ]
        )
        return "\n".join(rows)

    def selected_causal_evidence(
        self,
        *,
        evidence_anchor: str = (
            "test:plugins/super-developer/assets/tests/test_sliceproof.py::"
            "test_validate_plan_accepts_valid_registry_package_slice_fixture"
        ),
        evidence_type: str = "test",
        behavior_risk: str = "Valid and malformed registry routing follows the executable helper path.",
        causal_sufficiency: str = (
            "The selected test invokes the real CLI parser and fails when required routing or binding changes."
        ),
        substitutes: str = "Temporary filesystem fixture; no mocked helper process.",
        command_result: str = (
            "`command:proof#Commands Run:fixture subset` — PASS, focused helper fixture completed with exit 0."
        ),
    ) -> str:
        return "\n".join(
            [
                "| Evidence Anchor | Evidence Type | Behavior / Risk Proven | Causal Sufficiency | Substitutes / Fixtures | Fresh Command Result |",
                "|---|---|---|---|---|---|",
                f"| {evidence_anchor} | {evidence_type} | {behavior_risk} | {causal_sufficiency} | {substitutes} | {command_result} |",
            ]
        )

    def candidate_binding(
        self,
        *,
        assurance_profile: str = "standard",
        verification_mode: str = "boundary",
        commit: str | None = None,
        tree: str | None = None,
        base_commit: str | None = None,
        diff_digest: str | None = None,
        runtime_evidence_digests: tuple[tuple[str, str], ...] = (),
        consumed_contract_digests: tuple[tuple[str, str], ...] = (),
        authorization_id: str = REPORT_AUTHORIZATION_ID,
        effective_digest: str = REPORT_EFFECTIVE_DIGEST,
    ):
        return SLICEPROOF.CandidateBinding(
            authorization_id=authorization_id,
            effective_digest=effective_digest,
            assurance_profile=assurance_profile,
            verification_mode=verification_mode,
            commit=self.report_commit if commit is None else commit,
            tree=self.report_tree if tree is None else tree,
            base_commit=self.report_base if base_commit is None else base_commit,
            diff_digest=self.report_diff_digest if diff_digest is None else diff_digest,
            runtime_evidence_digests=runtime_evidence_digests,
            consumed_contract_digests=consumed_contract_digests,
        )

    def binding_cli_args(
        self,
        *,
        assurance_profile: str = "standard",
        verification_mode: str = "boundary",
        runtime_evidence: str = "none",
        consumed_contract: str = "none",
        worktree: str | None = None,
        git_ref: str | None = None,
        commit: str | None = None,
        tree: str | None = None,
        base_commit: str | None = None,
        diff_digest: str | None = None,
        effective_digest: str = REPORT_EFFECTIVE_DIGEST,
    ) -> list[str]:
        return [
            "--authorization-id", REPORT_AUTHORIZATION_ID,
            "--effective-digest", effective_digest,
            "--assurance-profile", assurance_profile,
            "--verification-mode", verification_mode,
            "--worktree", worktree or str(self.repo.resolve(strict=False)),
            "--git-ref", git_ref or self.report_ref,
            "--commit", commit or self.report_commit,
            "--tree", tree or self.report_tree,
            "--base-commit", base_commit or self.report_base,
            "--diff-digest", diff_digest or self.report_diff_digest,
            "--runtime-evidence-digest", runtime_evidence,
            "--consumed-contract-digest", consumed_contract,
            "--verified-at", "2026-06-04T00:00:00Z",
        ]

    def report_text(
        self,
        proof_text: str | None = None,
        *,
        verdict: str = "PASS",
        package_markdown: str = ".tasks/fixture/packages/WP1.md",
        assigned_slices: str = ".planning/fixture/slices/helper.md",
        worktree: str | None = None,
        git_ref: str | None = None,
        commit: str | None = None,
        deliverable_matrix: str | None = None,
        triggered_risk_selection_notes: str = "- Not applicable: fixture helper report has no triggered runtime risk probes.",
        selected_causal_evidence: str | None = None,
        slice_closure_review: str | None = None,
        code_review_findings: str = "- None.",
        blocking_findings: str | None = "- None.",
        repair_guidance: str | None = "- None required.",
        semgrep_evidence: str | None = None,
        consumed_contract_digests: tuple[tuple[str, str], ...] = (),
        runtime_evidence_digests: tuple[tuple[str, str], ...] = (),
        authorization_id: str = REPORT_AUTHORIZATION_ID,
        effective_digest: str = REPORT_EFFECTIVE_DIGEST,
        assurance_profile: str = "standard",
        verification_mode: str = "boundary",
    ) -> str:
        if proof_text is None:
            proof_text = self.proof_path.read_text(encoding="utf-8")
        worktree = str(self.repo.resolve(strict=False)) if worktree is None else worktree
        git_ref = self.report_ref if git_ref is None else git_ref
        if deliverable_matrix is None:
            deliverable_matrix = self.deliverable_matrix(assigned_slices=assigned_slices)
        if selected_causal_evidence is None:
            selected_causal_evidence = self.selected_causal_evidence()
        if slice_closure_review is None:
            if assigned_slices == "none":
                slice_closure_review = "- None."
            else:
                slice_closure_review = textwrap.dedent(
                    """
                    | Slice ID | Proof status | Evidence sufficient? | Notes |
                    |---|---|---|---|
                    | `HELPER-PLAN-001` | `PASS` | yes | Fixture proof closure verified mechanically. |
                    | `HELPER-PROOF-002` | `PASS` | yes | Fixture proof closure verified mechanically. |
                    """
                ).strip()
        lines = [
            "## Package Verification: WP1",
            "",
            "### Verdict",
            verdict,
            "",
            "### Deliverable Completeness Matrix",
            deliverable_matrix,
            "",
            "### Triggered Risk Selection Notes",
            triggered_risk_selection_notes,
            "",
            "### Selected Causal Evidence",
            selected_causal_evidence,
            "",
            "### Slice Closure Review",
            slice_closure_review,
            "",
            "### Code Review Findings",
            code_review_findings,
            "",
        ]
        if blocking_findings is not None:
            lines.extend(["### Blocking Findings", blocking_findings, ""])
        if repair_guidance is not None:
            lines.extend(["### Repair Guidance", repair_guidance, ""])
        candidate = self.candidate_binding(
            authorization_id=authorization_id,
            effective_digest=effective_digest,
            assurance_profile=assurance_profile,
            verification_mode=verification_mode,
            commit=commit,
            runtime_evidence_digests=runtime_evidence_digests,
            consumed_contract_digests=consumed_contract_digests,
        )
        values = SLICEPROOF.state_binding_values(
            self.artifact_root,
            self.registry_package(),
            self.package_markdown(),
            self.proof_path,
            candidate=candidate,
            worktree=worktree,
            git_ref=git_ref,
            verified_at="2026-06-04T00:00:00Z",
        )
        values["Package Markdown"] = package_markdown
        lines.extend([SLICEPROOF.render_state_binding_block(values).rstrip("\n"), ""])
        if semgrep_evidence is not None:
            lines.extend(["## Semgrep Evidence", semgrep_evidence, ""])
        return "\n".join(lines)

    def write_semgrep_evidence(self, stem: str = "WP1") -> tuple[str, str, str, str]:
        raw = self.semgrep_dir / f"{stem}.semgrep.json"
        summary = self.semgrep_dir / f"{stem}.semgrep-summary.json"
        raw.write_text('{"errors": [], "results": []}\n', encoding="utf-8")
        raw_digest = hashlib.sha256(raw.read_bytes()).hexdigest()
        summary_data = {
            "raw_digest": raw_digest,
            "result_count": 0,
            "scan_errors": [],
            "severity_counts": {},
            "semgrep_severity_is_advisory": True,
        }
        canonical = json.dumps(summary_data, sort_keys=True, separators=(",", ":")).encode("utf-8")
        summary_digest = hashlib.sha256(canonical).hexdigest()
        summary_data["summary_digest"] = summary_digest
        summary.write_text(json.dumps(summary_data, sort_keys=True), encoding="utf-8")
        return (
            f".tasks/fixture/semgrep/{stem}.semgrep.json",
            raw_digest,
            f".tasks/fixture/semgrep/{stem}.semgrep-summary.json",
            summary_digest,
        )

    def semgrep_evidence_text(self, *, stem: str = "WP1", raw_digest: str | None = None, summary_digest: str | None = None) -> str:
        raw_path, actual_raw_digest, summary_path, actual_summary_digest = self.write_semgrep_evidence(stem)
        return textwrap.dedent(
            f"""
            - Status: `enabled`
            - Raw Path: `{raw_path}`
            - Raw Digest: `{raw_digest or actual_raw_digest}`
            - Summary Path: `{summary_path}`
            - Summary Digest: `{summary_digest or actual_summary_digest}`
            - Scan Scope: `package WP1 worktree`
            - Bounded Summary: `helper summarize reported 0 findings and 0 scan errors; no raw JSON was consumed by agents.`
            """
        ).strip()

    def write_completed_proof_and_report(self) -> None:
        proof = self.completed_proof()
        self.proof_path.write_text(proof, encoding="utf-8")
        self.report_path.write_text(self.report_text(proof), encoding="utf-8")

    def configure_primary_final(
        self,
        *,
        assurance_profile: str = "standard",
        status: str = "pending",
        rationale: str | None = None,
    ) -> None:
        plan = self.plan()
        plan["assurance_profile"] = assurance_profile
        plan["work_packages"][0].update({
            "verification_mode": "final",
            "report_path": None,
            "status": status,
        })
        self.write_plan(plan)
        self.package_path.write_text(
            self.package_text(
                verification_mode="final",
                report_path=None,
                verification_rationale=rationale,
            ),
            encoding="utf-8",
        )
        if self.report_path.exists() or self.report_path.is_symlink():
            self.report_path.unlink()

    def write_simple_package_artifacts(
        self,
        package_id: str,
        *,
        must_ids: list[str],
        context_ids: list[str] | None = None,
        verification_mode: str = "boundary",
        depends_on: list[str] | None = None,
    ) -> None:
        context_ids = context_ids or []
        depends_on = depends_on or []
        titles = {
            "HELPER-PLAN-001": "Registry and package references validate mechanically",
            "HELPER-PROOF-002": "Proof placeholders and proof closure are mechanical",
            "HELPER-CONTEXT-003": "Context-only IDs stay required reading",
            "HELPER-PIPE-004": "Proof rows preserve table content",
            "HELPER-INTERFACE-005": "Interface-bearing rows require exactness",
        }
        package_rel = f".tasks/fixture/packages/{package_id}.md"
        proof_rel = f".tasks/fixture/proofs/{package_id}.proof.md"
        report_rel = f".tasks/fixture/reports/{package_id}.package-verification.md"
        registry_report: str | None = report_rel if verification_mode == "boundary" else None
        package_path = self.package_dir / f"{package_id}.md"
        proof_path = self.proofs_dir / f"{package_id}.proof.md"
        report_path = self.reports_dir / f"{package_id}.package-verification.md"
        package_lines = [
            f"# Work Package: {package_id} — Helper behavior",
            "",
            "## Scope",
            f"Validate simple package {package_id} behavior with deterministic fixtures.",
            "",
            "## Assigned Slices",
            "### `.planning/fixture/slices/helper.md`",
            "Must satisfy:",
            *[f"- `{slice_id}` — {titles[slice_id]}" for slice_id in must_ids],
        ]
        if context_ids:
            package_lines.extend([
                "",
                "Context only:",
                *[f"- `{slice_id}` — {titles[slice_id]}" for slice_id in context_ids],
            ])
        package_lines.extend([
            "",
            "## Primary Paths",
            "- `plugins/super-developer/assets/sliceproof.py`",
            "",
            "## Verification Expectations",
            f"- `{package_id}` fixture report validates mechanically.",
            "",
            "## Proof",
            f"- `{proof_rel}`",
            "",
            "## Independent Verification",
            f"- Mode: `{verification_mode}`",
            f"- Report: `{report_rel if registry_report is not None else 'None — final assurance'}`",
            (
                "- Rationale: Shared helper contract boundary requires an independent package receipt."
                if verification_mode == "boundary"
                else "- Rationale: Owner: Code Reviewer; semantic verification is deferred to final assurance for this coherent leaf."
            ),
            "",
            "## Dependencies",
            *([f"- `{dependency}`" for dependency in depends_on] or ["- None."]),
            "",
        ])
        package_path.write_text("\n".join(package_lines), encoding="utf-8")
        scope_rows = [f"  - Must satisfy: `{slice_id}` — {titles[slice_id]}" for slice_id in must_ids]
        scope_rows.extend(f"  - Context only: `{slice_id}` — {titles[slice_id]}" for slice_id in context_ids)
        proof_rows = "\n".join(
            f"| `{slice_id}` | {titles[slice_id]} | sliceproof.py fixture code covers {slice_id}. | targeted helper validation observed pass for {package_id}. | PASS |"
            for slice_id in must_ids
        )
        proof_lines = [
            f"# Package Proof: {package_id} — Helper behavior",
            "",
            "## Package Scope",
            f"Validate simple package {package_id} behavior with deterministic fixtures.",
            "",
            "## Assigned Slice Scope",
            "- `.planning/fixture/slices/helper.md`",
            *scope_rows,
            "",
            "## Slice Closure Table",
            "",
            "| Slice ID | Required understanding | Implementation evidence | Verification evidence | Status |",
            "|---|---|---|---|---|",
            proof_rows,
            "",
            "## Acceptance / Verification Closure",
            "",
            "| Expectation | Evidence | Status |",
            "|---|---|---|",
            f"| `{package_id}` fixture report validates mechanically. | validate-package-complete fixture command observed pass. | PASS |",
            "",
            "## Commands Run",
            "- python3 -m pytest plugins/super-developer/assets/tests/test_sliceproof.py (fixture subset observed pass)",
            "",
            "## Files Changed / Inspected",
            "- plugins/super-developer/assets/sliceproof.py",
            "- plugins/super-developer/assets/tests/test_sliceproof.py",
            "",
            "## Gaps, Deviations, or Deferred Items",
            "- None.",
            "",
            "## Package Agent Completion Statement",
            f"- Mechanical helper evidence recorded for {package_id}.",
            "",
        ]
        proof_path.write_text("\n".join(proof_lines), encoding="utf-8")
        if verification_mode == "final":
            if report_path.exists() or report_path.is_symlink():
                report_path.unlink()
            return
        matrix_rows = [
            "| Source ID | Row Type | Deliverable | Evidence Type | Evidence Refs | Exactness / Risk Disposition | Verdict |",
            "|---|---|---|---|---|---|---|",
        ]
        matrix_rows.extend(
            f"| {slice_id} | slice | {titles[slice_id]}. | static | static:plugins/super-developer/assets/sliceproof.py#validate_plan | no interface; fixture row covered | delivered |"
            for slice_id in must_ids
        )
        matrix_rows.append(
            f"| VE-1 | verification-expectation | `{package_id}` fixture report validates mechanically. | static | static:plugins/super-developer/assets/sliceproof.py#validate_plan | expectation covered; no interface | delivered |"
        )
        slice_review_rows = [
            "| Slice ID | Proof status | Evidence sufficient? | Notes |",
            "|---|---|---|---|",
        ]
        slice_review_rows.extend(
            f"| `{slice_id}` | `PASS` | yes | Fixture proof closure verified mechanically. |" for slice_id in must_ids
        )
        package_md = SLICEPROOF.parse_package_markdown(package_path, package_id)
        registry_package = SLICEPROOF.RegistryPackage(
            package_id=package_id,
            path=package_rel,
            proof_path=proof_rel,
            report_path=registry_report,
            status="pending",
            depends_on=depends_on,
            verification_mode=verification_mode,
        )
        package_ref = f"wp/fixture/{package_id}"
        self.git_checked("update-ref", f"refs/heads/{package_ref}", self.report_commit)
        values = SLICEPROOF.state_binding_values(
            self.artifact_root,
            registry_package,
            package_md,
            proof_path,
            candidate=self.candidate_binding(),
            worktree=str(self.repo.resolve(strict=False)),
            git_ref=package_ref,
            verified_at="2026-06-04T00:00:00Z",
        )
        report_lines = [
            f"## Package Verification: {package_id}",
            "",
            "### Verdict",
            "PASS",
            "",
            "### Deliverable Completeness Matrix",
            *matrix_rows,
            "",
            "### Triggered Risk Selection Notes",
            "- Not applicable: fixture helper report has no triggered runtime risk probes.",
            "",
            "### Selected Causal Evidence",
            self.selected_causal_evidence(),
            "",
            "### Slice Closure Review",
            *slice_review_rows,
            "",
            "### Code Review Findings",
            "- None.",
            "",
            "### Blocking Findings",
            "- None.",
            "",
            "### Repair Guidance",
            "- None required.",
            "",
            SLICEPROOF.render_state_binding_block(values).rstrip("\n"),
            "",
        ]
        report_path.write_text("\n".join(report_lines), encoding="utf-8")


class SliceproofTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SliceproofFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_validate_plan_accepts_valid_registry_package_slice_fixture(self) -> None:
        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(["WP1"], data["packages"])
        self.assertEqual(["WP1"], data["validated_package_markdown"])

    def test_validate_plan_supports_explicit_sidecar_artifact_and_code_roots(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            self.assertFalse((fixture.artifact_root / "plugins").exists())
            self.assertTrue((fixture.repo / "plugins" / "super-developer" / "assets" / "sliceproof.py").is_file())

            result = fixture.run("validate-plan", *fixture.root_args(), ".tasks/fixture/tasks.json")

            self.assertEqual(0, result.returncode, result.stdout + result.stderr)
            data = json.loads(result.stdout)
            self.assertEqual(str(fixture.artifact_root.resolve(strict=False)), data["artifact_root"])
            self.assertEqual(str(fixture.repo.resolve(strict=False)), data["code_root"])

            default_root_result = fixture.run("validate-plan", ".tasks/fixture/tasks.json")
            self.assertNotEqual(0, default_root_result.returncode, default_root_result.stdout + default_root_result.stderr)
            self.assertIn("file not found", "\n".join(json.loads(default_root_result.stderr)["errors"]))

            swapped_roots = fixture.run(
                "validate-plan",
                "--artifact-root",
                str(fixture.repo),
                "--code-root",
                str(fixture.artifact_root),
                ".tasks/fixture/tasks.json",
            )
            self.assertNotEqual(0, swapped_roots.returncode, swapped_roots.stdout + swapped_roots.stderr)
            self.assertIn("file not found", "\n".join(json.loads(swapped_roots.stderr)["errors"]))
        finally:
            fixture.cleanup()

    def test_b2_registry_requires_controlled_profile_mode_and_conditional_report(self) -> None:
        plan = self.fixture.plan()
        plan["assurance_profile"] = "standard"
        plan["work_packages"][0]["verification_mode"] = "boundary"
        self.fixture.write_plan(plan)
        accepted = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        self.assertEqual(
            ("standard", {"WP1": "boundary"}),
            (json.loads(accepted.stdout)["assurance_profile"], json.loads(accepted.stdout)["package_modes"]),
        )

        cases = [
            ("missing profile", lambda item: item.pop("assurance_profile"), "assurance_profile"),
            ("unknown profile", lambda item: item.__setitem__("assurance_profile", "fast"), "assurance_profile"),
            (
                "invalid low boundary equation",
                lambda item: item.__setitem__("assurance_profile", "low"),
                "low profile requires exactly one coherent final package",
            ),
            (
                "missing mode",
                lambda item: item["work_packages"][0].pop("verification_mode"),
                "verification_mode",
            ),
            (
                "unknown mode",
                lambda item: item["work_packages"][0].__setitem__("verification_mode", "skip"),
                "verification_mode",
            ),
            (
                "boundary null report",
                lambda item: item["work_packages"][0].__setitem__("report_path", None),
                "boundary mode requires",
            ),
            (
                "final report substitute",
                lambda item: item["work_packages"][0].__setitem__("verification_mode", "final"),
                "final mode requires exactly null",
            ),
        ]
        for name, mutate, expected in cases:
            with self.subTest(name=name):
                invalid = copy.deepcopy(plan)
                mutate(invalid)
                self.fixture.write_plan(invalid)
                rejected = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
                self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                self.assertIn(expected, "\n".join(json.loads(rejected.stderr)["errors"]))

    def test_validate_lifecycle_state_accepts_exact_current_snapshot_and_is_read_only(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            fixture.write_lifecycle(initial)
            initial_check = fixture.validate_lifecycle()
            self.assertEqual(0, initial_check.returncode, initial_check.stdout + initial_check.stderr)
            self.assertEqual(
                SLICEPROOF.canonical_json_digest(initial), json.loads(initial_check.stdout)["state_digest"]
            )
            previous_commit = fixture.commit_lifecycle("initial lifecycle")

            current = fixture.authorized_lifecycle_state(initial, previous_commit)
            code_sha = fixture.git_at(fixture.repo, "rev-parse", "HEAD")
            current["code_checkpoint"] = fixture.publish_code_checkpoint(
                "refs/heads/checkpoints/fixture/integration/g2", code_sha
            )
            current["packages"]["WP1"] = {"state": "pending", "wave": "wave-2"}
            current["wave"] = {"id": "wave-2", "generation": 2, "state": "reserved", "packages": ["WP1"]}
            freeze_path = ".tasks/fixture/assurance/freeze-2/freeze.json"
            freeze_digest = fixture.write_canonical_json(freeze_path, {"fixture": "freeze"})
            review_path = ".tasks/fixture/assurance/freeze-2/review.json"
            review_digest = fixture.write_canonical_json(review_path, {"fixture": "review"})
            current["freeze"] = {
                "id": "freeze-2", "path": freeze_path, "digest": freeze_digest,
            }
            current["receipts"] = [{
                "role": "R", "lens": "integrated-code-risk", "path": review_path,
                "digest": review_digest, "freeze_digest": freeze_digest,
            }]
            fixture.write_lifecycle(current)
            status_before = fixture.git_at(fixture.artifact_root, "status", "--porcelain")

            accepted = fixture.validate_lifecycle(previous_commit)
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
            payload = json.loads(accepted.stdout)
            self.assertEqual((2, SLICEPROOF.canonical_json_digest(initial)), (
                payload["generation"], payload["previous_state_digest"],
            ))
            self.assertEqual(status_before, fixture.git_at(fixture.artifact_root, "status", "--porcelain"))
        finally:
            fixture.cleanup()

    def test_generation_one_and_unauthorized_state_reject_future_topology(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            self.assertEqual([], SLICEPROOF.validate_lifecycle_state_data(
                initial,
                artifact_root=fixture.artifact_root,
                code_root=fixture.repo,
                feature="fixture",
                verify_files=False,
                verify_git_objects=False,
            ))
            future_cases = {
                "artifact_checkpoint": lambda state: state["artifact_checkpoint"].update({
                    "sha": "1" * 40, "tree": "2" * 40,
                }),
                "code_checkpoint": lambda state: state.__setitem__(
                    "code_checkpoint",
                    {"ref": "refs/heads/checkpoints/fixture/local/g1", "sha": "1" * 40},
                ),
                "authorization": lambda state: state["authorization"].__setitem__("id", "auth-1"),
                "amendment": lambda state: state["authorization"].__setitem__("amendment_link", {
                    "parent_effective_digest": fixture.digest_text("parent"),
                    "amendment_digest": fixture.digest_text("amendment"), "artifact_sha": "1" * 40,
                }),
                "packages": lambda state: state["packages"].update({
                    "WP1": {"state": "pending", "wave": None},
                }),
                "wave": lambda state: state.__setitem__(
                    "wave", {"id": "wave-one", "generation": 1, "state": "reserved", "packages": ["WP1"]},
                ),
                "serious_clusters": lambda state: state["serious_clusters"].append(
                    fixture.serious_cluster()
                ),
                "freeze": lambda state: state.__setitem__("freeze", {
                    "id": "freeze-1",
                    "path": ".tasks/fixture/assurance/freeze-1/freeze.json",
                    "digest": fixture.digest_text("freeze"),
                }),
                "receipts": lambda state: state["receipts"].append({
                    "role": "U", "lens": "accepted-outcome-reconciliation",
                    "path": ".tasks/fixture/assurance/freeze-1/audit.json",
                    "digest": fixture.digest_text("audit"),
                    "freeze_digest": fixture.digest_text("freeze"),
                }),
            }
            for field, mutate in future_cases.items():
                with self.subTest(field=field):
                    state = copy.deepcopy(initial)
                    if field == "wave":
                        state["packages"] = {"WP1": {"state": "pending", "wave": "wave-one"}}
                    mutate(state)
                    errors = SLICEPROOF.validate_lifecycle_state_data(
                        state,
                        artifact_root=fixture.artifact_root,
                        code_root=fixture.repo,
                        feature="fixture",
                        verify_files=False,
                        verify_git_objects=False,
                    )
                    self.assertIn("generation 1 requires initial null/empty topology", "\n".join(errors))

            local_only = copy.deepcopy(initial)
            local_only["generation"] = 2
            local_only["code_checkpoint"] = {
                "ref": "refs/heads/checkpoints/fixture/local/g2", "sha": "1" * 40,
            }
            local_only["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture", "artifact_sha": "2" * 40,
                "state_digest": fixture.digest_text("state"), "generation": 1,
            }
            errors = SLICEPROOF.validate_lifecycle_state_data(
                local_only,
                artifact_root=fixture.artifact_root,
                code_root=fixture.repo,
                feature="fixture",
                verify_files=False,
                verify_git_objects=False,
            )
            self.assertIn("complete implementation authorization is required", "\n".join(errors))
        finally:
            fixture.cleanup()

    def test_lifecycle_schema_has_no_history_or_completion_semantics(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            fixture.write_lifecycle(initial)
            previous_commit = fixture.commit_lifecycle("generation one")

            historical = copy.deepcopy(initial)
            historical["authorization"] = {
                "id": None, "initial_digest": None, "effective_digest": None,
                "technical_amendments": [],
            }
            fixture.write_lifecycle(historical)
            rejected = fixture.validate_lifecycle()
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            history_errors = "\n".join(json.loads(rejected.stderr)["errors"])
            self.assertIn("technical_amendments", history_errors)
            self.assertIn("amendment_link", history_errors)

            mechanically_completed = fixture.authorized_lifecycle_state(initial, previous_commit)
            mechanically_completed["stage"] = "completed"
            mechanically_completed["next_legal_actions"] = []
            # Pending package, active owner, no freeze, and no final receipts are intentionally outside A4 semantics.
            fixture.write_lifecycle(mechanically_completed)
            accepted = fixture.validate_lifecycle(previous_commit)
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        finally:
            fixture.cleanup()

    def test_validate_lifecycle_state_rejects_unsafe_roots_paths_and_shapes(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            valid = fixture.lifecycle_state()
            cases = [
                (
                    "freeze digest",
                    lambda state: state.__setitem__("freeze", {
                        "id": "freeze-1",
                        "path": ".tasks/fixture/assurance/freeze-1/freeze.json",
                        "digest": "sha256:bad",
                    }),
                    "freeze.digest",
                ),
                (
                    "artifact ref",
                    lambda state: state["artifact_checkpoint"].__setitem__("ref", "refs/heads/main"),
                    "artifact_checkpoint.ref",
                ),
                (
                    "code ref and sha",
                    lambda state: state.__setitem__(
                        "code_checkpoint", {"ref": "refs/heads/checkpoints/other/x/g1", "sha": "abc"}
                    ),
                    "code_checkpoint",
                ),
                (
                    "uncharged reservation",
                    lambda state: state["budgets"].__setitem__("active_reservation", {
                        "id": "reserve-1", "owner_token": "owner-1", "budget": "preauthorization",
                        "generation": 1, "units": {"delegated_calls": 2},
                    }),
                    "not already charged",
                ),
                (
                    "missing required budget counter",
                    lambda state: (
                        state["budgets"]["preauthorization"]["maxima"].pop("spike_waves"),
                        state["budgets"]["preauthorization"]["issued"].pop("spike_waves"),
                    ),
                    "missing required counters",
                ),
                (
                    "unsafe receipt",
                    lambda state: (
                        state.__setitem__("freeze", {
                            "id": "freeze-1",
                            "path": ".tasks/fixture/assurance/freeze-1/freeze.json",
                            "digest": fixture.digest_text("freeze"),
                        }),
                        state["receipts"].append({
                            "role": "U", "lens": "accepted-outcome-reconciliation",
                            "path": "../audit.json", "digest": fixture.digest_text("audit"),
                            "freeze_digest": fixture.digest_text("freeze"),
                        }),
                    ),
                    "must not contain",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    state = copy.deepcopy(valid)
                    mutate(state)
                    errors = SLICEPROOF.validate_lifecycle_state_data(
                        state,
                        artifact_root=fixture.artifact_root,
                        code_root=fixture.repo,
                        feature="fixture",
                        verify_files=False,
                        verify_git_objects=False,
                    )
                    self.assertIn(expected, "\n".join(errors))

            fixture.write_lifecycle(valid)
            equal_roots = fixture.run(
                "validate-lifecycle-state", "--artifact-root", str(fixture.artifact_root),
                "--code-root", str(fixture.artifact_root), "--feature", "fixture",
            )
            self.assertNotEqual(0, equal_roots.returncode, equal_roots.stdout + equal_roots.stderr)
            self.assertIn("must be distinct", "\n".join(json.loads(equal_roots.stderr)["errors"]))

            nested_root = fixture.run(
                "validate-lifecycle-state", "--artifact-root", str(fixture.feature_dir),
                "--code-root", str(fixture.repo), "--feature", "fixture",
            )
            self.assertNotEqual(0, nested_root.returncode, nested_root.stdout + nested_root.stderr)
            self.assertIn("exact Git worktree root", "\n".join(json.loads(nested_root.stderr)["errors"]))

            if hasattr(os, "symlink"):
                target = fixture.feature_dir / "alternate-state.json"
                target.write_text(json.dumps(valid), encoding="utf-8")
                fixture.lifecycle_path.unlink()
                fixture.lifecycle_path.symlink_to(target)
                symlinked = fixture.validate_lifecycle()
                self.assertNotEqual(0, symlinked.returncode, symlinked.stdout + symlinked.stderr)
                self.assertIn("must not contain symlinks", "\n".join(json.loads(symlinked.stderr)["errors"]))
        finally:
            fixture.cleanup()

    def test_authorization_inputs_bind_exact_objects_routing_and_budget_authority(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            fixture.write_lifecycle(initial)
            generation_one = fixture.commit_lifecycle("generation one")
            authorized = fixture.authorized_lifecycle_state(initial, generation_one)
            fixture.write_lifecycle(authorized)
            accepted = fixture.validate_lifecycle(generation_one)
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
            alternate_tree = subprocess.run(
                ["git", "mktree"], cwd=fixture.artifact_root, input="", check=True,
                text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            ).stdout.strip()
            alternate_commit = fixture.git_at(
                fixture.artifact_root,
                "commit-tree", alternate_tree, "-p", generation_one, "-m", "alternate input tree",
            )

            cases = [
                (
                    "canonical inputs digest",
                    lambda state: state["authorization"].__setitem__("initial_digest", fixture.digest_text("wrong")),
                    "canonical inputs digest",
                ),
                (
                    "artifact commit object",
                    lambda state: state["authorization"]["inputs"].__setitem__("artifact_commit", alternate_tree),
                    "local git inspection failed",
                ),
                (
                    "artifact commit tree relation",
                    lambda state: state["authorization"]["inputs"].__setitem__("artifact_commit", alternate_commit),
                    "authorization artifact commit tree",
                ),
                (
                    "artifact tree object",
                    lambda state: state["authorization"]["inputs"].__setitem__("artifact_tree", generation_one),
                    "exact named tree",
                ),
                (
                    "artifact tree relation",
                    lambda state: state["authorization"]["inputs"].__setitem__("artifact_tree", alternate_tree),
                    "initial artifact checkpoint tree",
                ),
                (
                    "base commit object",
                    lambda state: state["authorization"]["inputs"].__setitem__("base_commit", "0" * 40),
                    "local git inspection failed",
                ),
                (
                    "routing digest",
                    lambda state: state["authorization"]["inputs"].__setitem__(
                        "routing", fixture.digest_text("other routing")
                    ),
                    "initial lifecycle routing",
                ),
                (
                    "budget authority digest",
                    lambda state: state["authorization"]["inputs"].__setitem__(
                        "budget_authority", fixture.digest_text("other budgets")
                    ),
                    "finite budget authority",
                ),
                (
                    "complete package modes",
                    lambda state: state.__setitem__("package_modes", {}),
                    "bind every lifecycle package exactly",
                ),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    invalid = copy.deepcopy(authorized)
                    mutate(invalid)
                    if name not in {"canonical inputs digest", "complete package modes"}:
                        invalid["authorization"]["initial_digest"] = SLICEPROOF.canonical_json_digest(
                            invalid["authorization"]["inputs"]
                        )
                        invalid["authorization"]["effective_digest"] = invalid["authorization"]["initial_digest"]
                    errors = SLICEPROOF.validate_lifecycle_state_data(
                        invalid,
                        artifact_root=fixture.artifact_root,
                        code_root=fixture.repo,
                        feature="fixture",
                        verify_files=False,
                        verify_git_objects=True,
                    )
                    self.assertIn(expected, "\n".join(errors))

            next_state = copy.deepcopy(authorized)
            next_state["generation"] = 3
            next_state["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture", "artifact_sha": generation_one,
                "state_digest": SLICEPROOF.canonical_json_digest(authorized), "generation": 2,
            }
            next_state["authorization"]["inputs"]["actions"] = fixture.digest_text("replacement actions")
            self.assertIn(
                "authorization inputs is immutable",
                "\n".join(SLICEPROOF.compare_lifecycle_states(authorized, next_state)),
            )

            invalid_initial = copy.deepcopy(authorized)
            invalid_initial["authorization"]["effective_digest"] = fixture.digest_text("not initial")
            self.assertIn(
                "initial authorization must start at its initial digest",
                "\n".join(SLICEPROOF.compare_lifecycle_states(initial, invalid_initial)),
            )
        finally:
            fixture.cleanup()

    def test_initial_authorization_rejects_older_same_tree_commit_substitution(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            fixture.write_lifecycle(initial)
            older_commit = fixture.commit_lifecycle("generation one")
            tree = fixture.git_at(fixture.artifact_root, "rev-parse", f"{older_commit}^{{tree}}")
            reviewed_commit = fixture.git_at(
                fixture.artifact_root,
                "commit-tree", tree, "-p", older_commit, "-m", "reviewed same-tree candidate",
            )
            fixture.git_at(fixture.artifact_root, "reset", "--hard", reviewed_commit)
            self.assertEqual(tree, fixture.git_at(fixture.artifact_root, "rev-parse", f"{reviewed_commit}^{{tree}}"))

            authorized = fixture.authorized_lifecycle_state(initial, reviewed_commit)
            fixture.write_lifecycle(authorized)
            accepted = fixture.validate_lifecycle(reviewed_commit)
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

            substituted = copy.deepcopy(authorized)
            substituted["artifact_checkpoint"]["sha"] = older_commit
            substituted["authorization"]["inputs"]["artifact_commit"] = older_commit
            digest = SLICEPROOF.canonical_json_digest(substituted["authorization"]["inputs"])
            substituted["authorization"]["initial_digest"] = digest
            substituted["authorization"]["effective_digest"] = digest
            fixture.write_lifecycle(substituted)
            rejected = fixture.validate_lifecycle(reviewed_commit)
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn(
                "must match the exact reviewed predecessor candidate",
                "\n".join(json.loads(rejected.stderr)["errors"]),
            )
        finally:
            fixture.cleanup()

    def test_lifecycle_transition_enforces_predecessor_owner_budget_and_current_lineage(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            fixture.write_lifecycle(initial)
            generation_one = fixture.commit_lifecycle("generation one")

            authorized = fixture.authorized_lifecycle_state(initial, generation_one)
            code_sha = fixture.git_at(fixture.repo, "rev-parse", "HEAD")
            authorized["code_checkpoint"] = fixture.publish_code_checkpoint(
                "refs/heads/checkpoints/fixture/integration/g2", code_sha
            )
            authorized["serious_clusters"] = [fixture.serious_cluster()]
            fixture.write_lifecycle(authorized)
            generation_two = fixture.commit_lifecycle("generation two")

            current = copy.deepcopy(authorized)
            current["generation"] = 3
            current["stage"] = "package-wave-quiescent"
            current["next_legal_actions"] = ["dispatch"]
            current["budgets"]["active_reservation"] = None
            affected_digest = fixture.digest_text("affected helper closure")
            current["budgets"]["implementation"]["issued"]["repair_waves"] = 1
            current["serious_clusters"][0].update({
                "strikes": 1,
                "disposition": "closed",
                "repair": {
                    "root_cause_digest": fixture.digest_text("one root-cause repair"),
                    "affected_surface_digest": affected_digest,
                },
                "closure": {
                    "verdict": "PASS",
                    "affected_surface_digest": affected_digest,
                    "evidence_digest": fixture.digest_text("affected closure PASS"),
                },
            })
            current["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture",
                "artifact_sha": generation_two,
                "state_digest": SLICEPROOF.canonical_json_digest(authorized),
                "generation": 2,
            }
            fixture.write_lifecycle(current)
            baseline = fixture.validate_lifecycle(generation_two)
            self.assertEqual(0, baseline.returncode, baseline.stdout + baseline.stderr)

            cases = [
                ("generation skip", lambda state: state.__setitem__("generation", 4), "generation must advance exactly once"),
                ("owner reset", lambda state: state["owner"].__setitem__("host", "host-b"), "owner host cannot reset"),
                ("artifact reset", lambda state: state["artifact_checkpoint"].update({"sha": None, "tree": None}), "artifact checkpoint cannot reset"),
                ("maximum reset", lambda state: state["budgets"]["preauthorization"]["maxima"].__setitem__("delegated_calls", 9), "maxima are fixed"),
                ("issued reset", lambda state: state["budgets"]["preauthorization"]["issued"].__setitem__("delegated_calls", 0), "cannot decrease"),
                ("deadline reset", lambda state: state["budgets"]["implementation"].__setitem__("deadline_at", "2026-07-18T17:00:00Z"), "deadline_at is fixed"),
                ("uncharged next reservation", lambda state: state["budgets"].__setitem__("active_reservation", {
                    "id": "reservation-3", "owner_token": "owner-1", "budget": "implementation",
                    "generation": 3, "units": {"delegated_calls": 1},
                }), "must be charged by this generation"),
                ("authorization jump", lambda state: state["authorization"].__setitem__("effective_digest", fixture.digest_text("jump")), "requires an exact amendment link"),
                ("cluster reset", lambda state: state.__setitem__("serious_clusters", []), "serious cluster"),
                ("checkpoint mutation", lambda state: state["code_checkpoint"].__setitem__("sha", "0" * 40), "immutable code checkpoint ref"),
            ]
            for name, mutate, expected in cases:
                with self.subTest(name=name):
                    invalid = copy.deepcopy(current)
                    mutate(invalid)
                    self.assertIn(expected, "\n".join(SLICEPROOF.compare_lifecycle_states(authorized, invalid)))

            prior_struck, reset_strike = copy.deepcopy(authorized), copy.deepcopy(current)
            prior_struck["serious_clusters"][0]["strikes"] = 2
            reset_strike["serious_clusters"][0]["strikes"] = 1
            self.assertIn("strikes cannot decrease", "\n".join(SLICEPROOF.compare_lifecycle_states(prior_struck, reset_strike)))

            terminal_cases = []
            prior_released, reactivated = copy.deepcopy(authorized), copy.deepcopy(current)
            prior_released["owner"]["disposition"] = "released"
            reactivated["owner"]["disposition"] = "active"
            terminal_cases.append((prior_released, reactivated, "released owner disposition is terminal"))

            prior_done, reset_package = copy.deepcopy(authorized), copy.deepcopy(current)
            prior_done["packages"]["WP1"]["state"] = "done"
            reset_package["packages"]["WP1"]["state"] = "pending"
            terminal_cases.append((prior_done, reset_package, "package WP1 cannot move from done to pending"))

            prior_wave, reset_wave = copy.deepcopy(authorized), copy.deepcopy(current)
            prior_wave["packages"]["WP1"]["wave"] = "wave-2"
            prior_wave["wave"] = {
                "id": "wave-2", "generation": 2, "state": "active", "packages": ["WP1"],
            }
            reset_wave["packages"]["WP1"]["wave"] = "wave-2"
            reset_wave["wave"] = {
                "id": "wave-2", "generation": 2, "state": "reserved", "packages": ["WP1"],
            }
            terminal_cases.append((prior_wave, reset_wave, "active wave cannot reset"))

            prior_closed, reopened = copy.deepcopy(current), copy.deepcopy(current)
            reopened["serious_clusters"][0].update({
                "strikes": 1, "disposition": "repair-eligible", "repair": None, "closure": None,
            })
            terminal_cases.append((prior_closed, reopened, "terminal disposition is immutable"))

            for previous_state, next_state, expected in terminal_cases:
                with self.subTest(terminal_transition=expected):
                    self.assertIn(
                        expected,
                        "\n".join(SLICEPROOF.compare_lifecycle_states(previous_state, next_state)),
                    )

            wrong_digest = copy.deepcopy(current)
            wrong_digest["last_verified"]["state_digest"] = fixture.digest_text("wrong")
            fixture.write_lifecycle(wrong_digest)
            rejected_digest = fixture.validate_lifecycle(generation_two)
            self.assertNotEqual(0, rejected_digest.returncode, rejected_digest.stdout + rejected_digest.stderr)
            self.assertIn("committed predecessor state", "\n".join(json.loads(rejected_digest.stderr)["errors"]))

            fixture.write_lifecycle(current)
            wrong_parent = fixture.validate_lifecycle(generation_one)
            self.assertNotEqual(0, wrong_parent.returncode, wrong_parent.stdout + wrong_parent.stderr)
            self.assertIn("does not match last_verified", "\n".join(json.loads(wrong_parent.stderr)["errors"]))

            fixture.write_lifecycle(initial)
            reset = fixture.validate_lifecycle()
            self.assertNotEqual(0, reset.returncode, reset.stdout + reset.stderr)
            self.assertIn("cannot reset committed lifecycle history", "\n".join(json.loads(reset.stderr)["errors"]))
        finally:
            fixture.cleanup()

    def test_b4_accepts_compact_low_standard_and_high_completion_graphs(self) -> None:
        cases = [
            ("low", None, ["C", "V"]),
            ("standard", None, ["R", "U", "V"]),
            ("high", [], ["R", "U", "V"]),
            ("high", ["privacy"], ["R", "S", "U", "V"]),
        ]
        for profile, specialist_lenses, expected_roles in cases:
            with self.subTest(profile=profile, specialist_lenses=specialist_lenses):
                fixture = SliceproofFixture(separate_roots=True)
                try:
                    state = fixture.write_agentic_completion(
                        profile, specialist_lenses=specialist_lenses
                    )
                    status_before = (
                        fixture.git_at(fixture.artifact_root, "status", "--porcelain"),
                        fixture.git_at(fixture.repo, "status", "--porcelain"),
                    )
                    accepted = fixture.validate_agentic_completion()
                    self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
                    self.assertEqual(status_before, (
                        fixture.git_at(fixture.artifact_root, "status", "--porcelain"),
                        fixture.git_at(fixture.repo, "status", "--porcelain"),
                    ))
                    payload = json.loads(accepted.stdout)
                    self.assertTrue(payload["pre_freeze_package_equation_validated"])
                    self.assertTrue(payload["post_freeze_assurance_validated"])
                    self.assertEqual(expected_roles, [item["role"] for item in payload["receipts"]])
                    self.assertEqual(
                        state["artifact_checkpoint"], payload["lifecycle_artifact_checkpoint"]
                    )
                    self.assertEqual(
                        fixture.git_at(fixture.artifact_root, "rev-parse", "HEAD"),
                        payload["verification_summary_checkpoint"]["commit"],
                    )
                    self.assertNotEqual(
                        payload["lifecycle_artifact_checkpoint"]["sha"],
                        payload["verification_summary_checkpoint"]["commit"],
                    )
                    self.assertEqual(
                        fixture.report_commit, payload["code_checkpoint"]["commit"]
                    )
                    self.assertEqual("2026-07-18T14:05:00+00:00", payload["completion_timestamp"])
                finally:
                    fixture.cleanup()

    def test_b4_rejects_malformed_receipt_graph_matrix(self) -> None:
        def node_pointer(state: dict, role: str) -> dict:
            item = next(pointer for pointer in state["receipts"] if pointer["role"] == role)
            return SLICEPROOF.predecessor_pointer(
                item["role"], item["lens"], item["path"], item["digest"]
            )

        def circular(state: dict, _freeze: dict, files: dict[str, dict]) -> None:
            review = next(item for item in state["receipts"] if item["role"] == "R")
            files[review["path"]]["predecessors"] = [node_pointer(state, "R")]

        def cross_freeze(state: dict, _freeze: dict, files: dict[str, dict]) -> None:
            audit = next(item for item in state["receipts"] if item["role"] == "U")
            files[audit["path"]]["freeze_id"] = "freeze-other"

        def postdecessor(state: dict, _freeze: dict, files: dict[str, dict]) -> None:
            review = next(item for item in state["receipts"] if item["role"] == "R")
            files[review["path"]]["predecessors"] = [node_pointer(state, "U")]

        def missing_role(state: dict, _freeze: dict, _files: dict[str, dict]) -> None:
            state["receipts"] = [item for item in state["receipts"] if item["role"] != "U"]

        def extra_role(state: dict, freeze: dict, files: dict[str, dict]) -> None:
            path = SLICEPROOF.canonical_receipt_path(
                "fixture", freeze["id"], "C", "combined-low-assurance"
            )
            files[path] = {
                "schema_version": 1,
                "role": "C",
                "lens": "combined-low-assurance",
                "freeze_id": freeze["id"],
                "freeze_digest": state["freeze"]["digest"],
                "authorization": freeze["authorization"],
                "predecessors": [SLICEPROOF.predecessor_pointer(
                    "F", "freeze", state["freeze"]["path"], state["freeze"]["digest"]
                )],
                "recorded_at": "2026-07-18T14:02:00Z",
                "verdicts": {"code_risk": "PASS", "completion": "PASS"},
            }
            state["receipts"].insert(1, {
                "role": "C", "lens": "combined-low-assurance", "path": path,
                "digest": state["freeze"]["digest"], "freeze_digest": state["freeze"]["digest"],
            })

        def duplicate_role(state: dict, _freeze: dict, _files: dict[str, dict]) -> None:
            state["receipts"].insert(1, copy.deepcopy(state["receipts"][0]))

        def summary_as_proof(state: dict, _freeze: dict, files: dict[str, dict]) -> None:
            summary = next(item for item in state["receipts"] if item["role"] == "V")
            files[summary["path"]]["verdict"] = "PASS"

        def unplanned_specialist(state: dict, freeze: dict, files: dict[str, dict]) -> None:
            path = SLICEPROOF.canonical_receipt_path(
                "fixture", freeze["id"], "S", "privacy"
            )
            files[path] = {
                "schema_version": 1, "role": "S", "lens": "privacy",
                "freeze_id": freeze["id"], "freeze_digest": state["freeze"]["digest"],
                "authorization": freeze["authorization"],
                "predecessors": [SLICEPROOF.predecessor_pointer(
                    "F", "freeze", state["freeze"]["path"], state["freeze"]["digest"]
                ), node_pointer(state, "R")],
                "recorded_at": "2026-07-18T14:02:00Z", "verdict": "PASS",
            }
            state["receipts"].insert(1, {
                "role": "S", "lens": "privacy", "path": path,
                "digest": state["freeze"]["digest"], "freeze_digest": state["freeze"]["digest"],
            })

        cases = [
            ("circular", circular, "acyclic same-freeze predecessors"),
            ("cross-freeze", cross_freeze, "cross-freeze binding"),
            ("postdecessor", postdecessor, "circular/postdecessor"),
            ("missing role", missing_role, "exact roles/lenses"),
            ("extra role", extra_role, "exact roles/lenses"),
            ("duplicate role", duplicate_role, "duplicate singleton role"),
            ("summary as proof", summary_as_proof, "unsupported field"),
        ]
        for name, mutate, expected in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture(separate_roots=True)
                try:
                    fixture.write_agentic_completion("standard", graph_mutator=mutate)
                    rejected = fixture.validate_agentic_completion()
                    self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                    self.assertIn(expected, "\n".join(json.loads(rejected.stderr)["errors"]))
                finally:
                    fixture.cleanup()

        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.write_agentic_completion(
                "high", specialist_lenses=[], graph_mutator=unplanned_specialist
            )
            rejected = fixture.validate_agentic_completion()
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("exact roles/lenses", rejected.stderr)
        finally:
            fixture.cleanup()

    def test_b4_cluster_identity_precedence_strikes_and_terminal_lineage(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            precedence_cluster = fixture.serious_cluster(
                observed_classes=[
                    "confidence-enhancement",
                    "test-fidelity-gap",
                    "architecture-invalidation",
                    "requirement-gap",
                ],
                disposition="routed",
            )
            self.assertEqual("requirement-gap", precedence_cluster["class"])
            self.assertEqual("human-envelope", precedence_cluster["route"])
            errors: list[str] = []
            SLICEPROOF.validate_serious_clusters([precedence_cluster], errors)
            self.assertEqual([], errors)

            equal_rank_cases = [
                (["implementation-defect", "integration-regression"], "implementation-defect", "repair-eligible"),
                (["implementation-defect", "integration-regression"], "integration-regression", "repair-eligible"),
                (["test-fidelity-gap", "evidence-stale-or-contradicted"], "test-fidelity-gap", "repair-eligible"),
                (["test-fidelity-gap", "evidence-stale-or-contradicted"], "evidence-stale-or-contradicted", "routed"),
            ]
            for observed, selected, disposition in equal_rank_cases:
                with self.subTest(equal_rank_selected=selected):
                    cluster = fixture.serious_cluster(
                        observed_classes=observed,
                        selected_class=selected,
                        disposition=disposition,
                    )
                    cluster_errors: list[str] = []
                    SLICEPROOF.validate_serious_clusters([cluster], cluster_errors)
                    self.assertEqual([], cluster_errors)
                    self.assertEqual(SLICEPROOF.CLUSTER_ROUTES[selected], cluster["route"])

            repair = {
                "root_cause_digest": fixture.digest_text("one repair"),
                "affected_surface_digest": fixture.digest_text("affected closure"),
            }
            passed = fixture.serious_cluster(
                strikes=1,
                disposition="closed",
                repair=repair,
                closure={
                    "verdict": "PASS",
                    "affected_surface_digest": repair["affected_surface_digest"],
                    "evidence_digest": fixture.digest_text("closure pass"),
                },
            )
            failed = fixture.serious_cluster(
                signatures=[fixture.digest_text("renamed agent/commit/signature")],
                strikes=2,
                disposition="circuit-open",
                repair=repair,
                closure={
                    "verdict": "FAIL",
                    "affected_surface_digest": repair["affected_surface_digest"],
                    "evidence_digest": fixture.digest_text("closure fail"),
                },
            )
            self.assertEqual(passed["id"], failed["id"], "observations cannot mint a new cluster")
            for cluster in (passed, failed):
                cluster_errors: list[str] = []
                SLICEPROOF.validate_serious_clusters([cluster], cluster_errors)
                self.assertEqual([], cluster_errors)

            reset = copy.deepcopy(failed)
            reset["strikes"] = 1
            reset["disposition"] = "repair-eligible"
            reset["repair"] = None
            reset["closure"] = None
            transition_errors = "\n".join(SLICEPROOF.compare_lifecycle_states(
                {**fixture.lifecycle_state(), "serious_clusters": [failed]},
                {**fixture.lifecycle_state(), "generation": 2, "serious_clusters": [reset],
                 "last_verified": {
                     "artifact_ref": "refs/heads/artifacts/fixture", "artifact_sha": "1" * 40,
                     "state_digest": fixture.digest_text("prior"), "generation": 1,
                 }},
            ))
            self.assertIn("strikes cannot decrease", transition_errors)
            self.assertIn("terminal disposition is immutable", transition_errors)

            changed_signature = copy.deepcopy(passed)
            changed_signature["observed_signatures"] = [fixture.digest_text("replacement-only signature")]
            transition_errors = "\n".join(SLICEPROOF.compare_lifecycle_states(
                {**fixture.lifecycle_state(), "serious_clusters": [passed]},
                {**fixture.lifecycle_state(), "generation": 2, "serious_clusters": [changed_signature],
                 "last_verified": {
                     "artifact_ref": "refs/heads/artifacts/fixture", "artifact_sha": "1" * 40,
                     "state_digest": fixture.digest_text("prior"), "generation": 1,
                 }},
            ))
            self.assertIn("terminal disposition is immutable", transition_errors)
        finally:
            fixture.cleanup()

    def test_b4_exhausted_budget_and_cas_loss_use_control_only_escalation(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            fixture.write_lifecycle(initial)
            previous_commit = fixture.commit_lifecycle("generation one")
            state = fixture.authorized_lifecycle_state(initial, previous_commit)
            state["stage"] = "needs-decision"
            state["next_legal_actions"] = ["escalate"]
            state["budgets"]["active_reservation"] = None
            maximum = state["budgets"]["implementation"]["maxima"]["repair_waves"]
            state["budgets"]["implementation"]["issued"]["repair_waves"] = maximum
            control = state["budgets"]["control_plane_reserve"]
            control.update({
                "issued": 1,
                "reservation": {
                    "id": "control-1",
                    "generation": state["generation"],
                    "operation": "safe-checkpoint",
                    "reason": "budget-exhausted",
                    "expected_parent": state["last_verified"]["artifact_sha"],
                    "checkpoint_digest": fixture.digest_text("safe checkpoint escalation"),
                    "conflict_digest": None,
                },
            })
            errors = SLICEPROOF.validate_lifecycle_state_data(
                state,
                artifact_root=fixture.artifact_root,
                code_root=fixture.repo,
                feature="fixture",
                verify_files=False,
                verify_git_objects=False,
            )
            self.assertEqual([], errors)

            cas_lost = copy.deepcopy(state)
            cas_lost["budgets"]["control_plane_reserve"]["reservation"].update({
                "operation": "last-verified",
                "reason": "cas-unavailable",
                "checkpoint_digest": None,
                "conflict_digest": fixture.digest_text("CAS parent unavailable"),
            })
            errors = SLICEPROOF.validate_lifecycle_state_data(
                cas_lost,
                artifact_root=fixture.artifact_root,
                code_root=fixture.repo,
                feature="fixture",
                verify_files=False,
                verify_git_objects=False,
            )
            self.assertEqual([], errors)

            takeover = copy.deepcopy(cas_lost)
            takeover["owner"]["host"] = "host-b"
            transition_errors = "\n".join(SLICEPROOF.compare_lifecycle_states(state, takeover))
            self.assertIn("cannot mutate ownership or take over", transition_errors)
            mutated = copy.deepcopy(cas_lost)
            mutated["packages"]["WP1"]["state"] = "in_progress"
            transition_errors = "\n".join(SLICEPROOF.compare_lifecycle_states(state, mutated))
            self.assertIn("cannot mutate semantic/checkpoint state", transition_errors)
            semantic_use = copy.deepcopy(cas_lost)
            semantic_use["budgets"]["active_reservation"] = {
                "id": "bad", "owner_token": "owner-1", "budget": "control-plane",
                "generation": semantic_use["generation"], "units": {"command_units": 1},
            }
            errors = SLICEPROOF.validate_lifecycle_state_data(
                semantic_use,
                artifact_root=fixture.artifact_root,
                code_root=fixture.repo,
                feature="fixture",
                verify_files=False,
                verify_git_objects=False,
            )
            self.assertIn("expected one of", "\n".join(errors))
        finally:
            fixture.cleanup()

    def test_b4_rejects_semantic_code_drift_deadline_and_receipt_mutation(self) -> None:
        drift_cases = ("semantic", "code")
        for kind in drift_cases:
            with self.subTest(kind=kind):
                fixture = SliceproofFixture(separate_roots=True)
                try:
                    fixture.write_agentic_completion("standard")
                    if kind == "semantic":
                        (fixture.feature_dir / "SPEC.md").write_text("# Drifted Spec\n", encoding="utf-8")
                    else:
                        with fixture.evidence_asset.open("a", encoding="utf-8") as handle:
                            handle.write("# unbound drift\n")
                    rejected = fixture.validate_agentic_completion()
                    self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                    self.assertIn("manifest" if kind == "semantic" else "clean", rejected.stderr.lower())
                finally:
                    fixture.cleanup()

        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.write_agentic_completion(
                "standard", completion_at="2026-07-18T16:00:01Z"
            )
            late = fixture.validate_agentic_completion()
            self.assertNotEqual(0, late.returncode, late.stdout + late.stderr)
            self.assertIn("fixed authorized deadline", late.stderr)

            checkpoint = fixture.git_at(fixture.artifact_root, "rev-parse", "HEAD")
            review_path = fixture.artifact_root / SLICEPROOF.canonical_receipt_path(
                "fixture", "freeze-standard", "R", "integrated-code-risk"
            )
            review_path.write_bytes(review_path.read_bytes() + b" ")
            append_errors = SLICEPROOF.validate_assurance_paths_append_only(
                fixture.artifact_root, "fixture", checkpoint
            )
            self.assertIn("append-only across freezes", "\n".join(append_errors))
        finally:
            fixture.cleanup()

    def test_package_state_transition_matrix_requires_reviewed_replan_reset(self) -> None:
        states = sorted(SLICEPROOF.PACKAGE_LIFECYCLE_STATES)
        for authorization_changed in (False, True):
            for old_state in states:
                expected = set(SLICEPROOF.PACKAGE_STATE_TRANSITIONS[old_state])
                if authorization_changed and old_state in SLICEPROOF.REPLAN_RESET_STATES:
                    expected.add("pending")
                for new_state in states:
                    with self.subTest(
                        authorization_changed=authorization_changed,
                        old_state=old_state,
                        new_state=new_state,
                    ):
                        errors = SLICEPROOF.compare_package_states(
                            {"WP1": {"state": old_state, "wave": None}},
                            {"WP1": {"state": new_state, "wave": None}},
                            authorization_changed,
                        )
                        self.assertEqual(new_state not in expected, bool(errors), errors)

        self.assertEqual([], SLICEPROOF.compare_package_states(
            {"WP1": {"state": "blocked", "wave": None}},
            {"WP1": {"state": "pending", "wave": None}},
            False,
        ))
        self.assertEqual([], SLICEPROOF.compare_package_states(
            {"WP1": {"state": "invalidated", "wave": None}},
            {"WP1": {"state": "in_progress", "wave": None}},
            False,
        ))
        reset_errors = SLICEPROOF.compare_package_states(
            {"WP1": {"state": "done", "wave": None}},
            {"WP1": {"state": "pending", "wave": None}},
            False,
        )
        self.assertIn("reviewed effective-digest change", "\n".join(reset_errors))

    def test_amendment_link_is_only_the_current_effective_digest_transition(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.init_lifecycle_git_roots()
            initial = fixture.lifecycle_state()
            fixture.write_lifecycle(initial)
            generation_one = fixture.commit_lifecycle("generation one")
            authorized = fixture.authorized_lifecycle_state(initial, generation_one)
            authorized["budgets"]["active_reservation"] = None
            authorized["owner"]["disposition"] = "stopped"
            fixture.write_lifecycle(authorized)
            generation_two = fixture.commit_lifecycle("generation two")

            amended = copy.deepcopy(authorized)
            amended["generation"] = 3
            amended["owner"] = {
                "token": "owner-2", "host": "host-b", "disposition": "active",
                "takeover": {
                    "previous_token": "owner-1", "previous_host": "host-a", "previous_generation": 2,
                    "evidence_digest": fixture.digest_text("prior owner stopped"),
                },
            }
            amended["artifact_checkpoint"] = {
                "ref": "refs/heads/artifacts/fixture",
                "sha": generation_two,
                "tree": fixture.git_at(fixture.artifact_root, "rev-parse", f"{generation_two}^{{tree}}"),
            }
            amendment_digest = fixture.digest_text("current technical amendment")
            link = {
                "parent_effective_digest": authorized["authorization"]["effective_digest"],
                "amendment_digest": amendment_digest,
                "artifact_sha": generation_two,
            }
            amended["authorization"]["amendment_link"] = link
            amended["authorization"]["effective_digest"] = SLICEPROOF.technical_amendment_effective_digest(
                link["parent_effective_digest"], link["amendment_digest"], link["artifact_sha"]
            )
            amended["assurance_profile"] = "high"
            amended["package_modes"] = {"WP1": "final"}
            amended["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture",
                "artifact_sha": generation_two,
                "state_digest": SLICEPROOF.canonical_json_digest(authorized),
                "generation": 2,
            }
            fixture.write_lifecycle(amended)
            accepted = fixture.validate_lifecycle(generation_two)
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

            same_checkpoint = copy.deepcopy(amended)
            same_checkpoint["artifact_checkpoint"] = copy.deepcopy(authorized["artifact_checkpoint"])
            same_checkpoint["authorization"]["amendment_link"]["artifact_sha"] = authorized[
                "artifact_checkpoint"
            ]["sha"]
            same_checkpoint["authorization"]["effective_digest"] = SLICEPROOF.technical_amendment_effective_digest(
                link["parent_effective_digest"],
                link["amendment_digest"],
                authorized["artifact_checkpoint"]["sha"],
            )
            same_errors = "\n".join(SLICEPROOF.compare_lifecycle_states(authorized, same_checkpoint))
            self.assertIn("requires a distinct artifact checkpoint", same_errors)

            prior_done, reviewed_reset = copy.deepcopy(authorized), copy.deepcopy(amended)
            prior_done["packages"]["WP1"]["state"] = "done"
            reviewed_reset["packages"]["WP1"]["state"] = "pending"
            self.assertFalse(any(
                "package WP1" in error
                for error in SLICEPROOF.compare_lifecycle_states(prior_done, reviewed_reset)
            ))

            for field, replacement in (
                ("id", "auth-replaced"),
                ("initial_digest", fixture.digest_text("replaced initial")),
                ("inputs", {**authorized["authorization"]["inputs"], "actions": fixture.digest_text("changed")}),
            ):
                with self.subTest(immutable=field):
                    changed = copy.deepcopy(amended)
                    changed["authorization"][field] = replacement
                    self.assertIn(
                        f"authorization {field} is immutable",
                        "\n".join(SLICEPROOF.compare_lifecycle_states(authorized, changed)),
                    )

            unrelated = copy.deepcopy(amended)
            tree = fixture.git_at(fixture.artifact_root, "rev-parse", f"{generation_two}^{{tree}}")
            unrelated_sha = fixture.git_at(
                fixture.artifact_root, "commit-tree", tree, "-p", generation_two, "-m", "unrelated descendant"
            )
            unrelated["artifact_checkpoint"].update({"sha": unrelated_sha, "tree": tree})
            unrelated["authorization"]["amendment_link"]["artifact_sha"] = unrelated_sha
            unrelated["authorization"]["effective_digest"] = SLICEPROOF.technical_amendment_effective_digest(
                link["parent_effective_digest"], link["amendment_digest"], unrelated_sha
            )
            fixture.write_lifecycle(unrelated)
            rejected_ancestry = fixture.validate_lifecycle(generation_two)
            self.assertNotEqual(0, rejected_ancestry.returncode, rejected_ancestry.stdout + rejected_ancestry.stderr)
            self.assertEqual(
                [], SLICEPROOF.validate_artifact_checkpoint_ancestry(fixture.artifact_root, authorized, unrelated),
                "old-to-new ancestry alone must not accept a side-branch checkpoint",
            )
            self.assertIn(
                "exact sidecar HEAD/predecessor lineage",
                "\n".join(json.loads(rejected_ancestry.stderr)["errors"]),
            )

            fixture.write_lifecycle(amended)
            generation_three = fixture.commit_lifecycle("generation three")
            next_state = copy.deepcopy(amended)
            next_state["generation"] = 4
            next_state["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture",
                "artifact_sha": generation_three,
                "state_digest": SLICEPROOF.canonical_json_digest(amended),
                "generation": 3,
            }
            fixture.write_lifecycle(next_state)
            stale_link = fixture.validate_lifecycle(generation_three)
            self.assertNotEqual(0, stale_link.returncode, stale_link.stdout + stale_link.stderr)
            self.assertIn("only for this generation", "\n".join(json.loads(stale_link.stderr)["errors"]))

            next_state["authorization"]["amendment_link"] = None
            fixture.write_lifecycle(next_state)
            cleared = fixture.validate_lifecycle(generation_three)
            self.assertEqual(0, cleared.returncode, cleared.stdout + cleared.stderr)
        finally:
            fixture.cleanup()

    def test_b2_same_root_lifecycle_is_non_authoritative_but_transition_rules_remain(self) -> None:
        controlled = {
            "authorization": {
                "id": REPORT_AUTHORIZATION_ID,
                "effective_digest": REPORT_EFFECTIVE_DIGEST,
            },
            "assurance_profile": "standard",
            "package_modes": {"WP1": "boundary"},
        }
        self.fixture.write_lifecycle(controlled)
        accepted = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
        self.fixture.write_completed_proof_and_report()
        bound = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertEqual(0, bound.returncode, bound.stdout + bound.stderr)
        report = self.fixture.report_path.read_text(encoding="utf-8").replace(
            REPORT_EFFECTIVE_DIGEST,
            "sha256:" + "9" * 64,
            1,
        )
        self.fixture.report_path.write_text(report, encoding="utf-8")
        stale_authorization = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertEqual(
            0,
            stale_authorization.returncode,
            stale_authorization.stdout + stale_authorization.stderr,
        )

        mismatched = self.fixture.plan()
        mismatched["assurance_profile"] = "high"
        self.fixture.write_plan(mismatched)
        compatible = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, compatible.returncode, compatible.stdout + compatible.stderr)

        previous = {
            "assurance_profile": "low",
            "package_modes": {"WP1": "final"},
            "packages": {"WP1": {"state": "stabilized", "wave": None}},
        }
        promoted = {
            "assurance_profile": "high",
            "package_modes": {"WP1": "boundary"},
            "packages": {"WP1": {"state": "stabilized", "wave": None}},
        }
        stale_errors = SLICEPROOF.compare_assurance_routing(previous, promoted, True, True)
        self.assertIn("must invalidate existing candidate for WP1", "\n".join(stale_errors))
        promoted["packages"]["WP1"]["state"] = "invalidated"
        self.assertEqual([], SLICEPROOF.compare_assurance_routing(previous, promoted, True, True))

        downgrade = copy.deepcopy(previous)
        downgrade["assurance_profile"] = "standard"
        self.assertIn(
            "profile downgrade requires a reviewed effective-digest amendment",
            "\n".join(SLICEPROOF.compare_assurance_routing(promoted, downgrade, True, False)),
        )

    def test_explicit_roots_apply_to_all_helper_commands(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            created = fixture.run("create-proof", *fixture.root_args(), ".tasks/fixture/tasks.json", "--package", "WP1")
            self.assertEqual(0, created.returncode, created.stdout + created.stderr)
            self.assertTrue(fixture.proof_path.is_file())
            self.assertFalse((fixture.repo / ".tasks" / "fixture" / "proofs" / "WP1.proof.md").exists())

            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(fixture.report_text(proof), encoding="utf-8")
            fixture.write_controlled_completion()

            proof_check = fixture.run("validate-proof", *fixture.root_args(), ".tasks/fixture/tasks.json", "--package", "WP1")
            self.assertEqual(0, proof_check.returncode, proof_check.stdout + proof_check.stderr)

            package_check = fixture.run("validate-package-complete", *fixture.root_args(), ".tasks/fixture/tasks.json", "--package", "WP1")
            self.assertEqual(0, package_check.returncode, package_check.stdout + package_check.stderr)

            plan = fixture.plan()
            plan["work_packages"][0]["status"] = "done"
            fixture.write_plan(plan)
            fixture.write_controlled_completion(package_states={"WP1": "done"})
            final_check = fixture.run("validate-final", *fixture.root_args(), ".tasks/fixture/tasks.json")
            self.assertEqual(0, final_check.returncode, final_check.stdout + final_check.stderr)
        finally:
            fixture.cleanup()

    def test_distinct_root_completion_rejects_forged_lifecycle_transitions(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(fixture.report_text(proof), encoding="utf-8")
            fixture.write_controlled_completion(package_states={"WP1": "pending"})

            pending = json.loads(fixture.lifecycle_path.read_text(encoding="utf-8"))
            initial_forgery = copy.deepcopy(pending)
            initial_forgery["packages"]["WP1"]["state"] = "stabilized"
            fixture.write_lifecycle(initial_forgery)
            rejected_initial = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertNotEqual(0, rejected_initial.returncode, rejected_initial.stdout + rejected_initial.stderr)
            self.assertIn(
                "initial authorization must introduce every package in pending state",
                "\n".join(json.loads(rejected_initial.stderr)["errors"]),
            )

            fixture.write_lifecycle(pending)
            pending_commit = fixture.commit_lifecycle("controlled pending generation")
            forged = copy.deepcopy(pending)
            forged["generation"] += 1
            forged["stage"] = "package-wave-quiescent"
            forged["next_legal_actions"] = ["dispatch"]
            forged["budgets"]["active_reservation"] = None
            forged["packages"]["WP1"]["state"] = "done"
            forged["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture",
                "artifact_sha": pending_commit,
                "state_digest": SLICEPROOF.canonical_json_digest(pending),
                "generation": pending["generation"],
            }
            fixture.write_lifecycle(forged)
            rejected_jump = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertNotEqual(0, rejected_jump.returncode, rejected_jump.stdout + rejected_jump.stderr)
            self.assertIn(
                "package WP1 cannot move from pending to done",
                "\n".join(json.loads(rejected_jump.stderr)["errors"]),
            )
        finally:
            fixture.cleanup()

    def test_distinct_root_checkpoint_head_cleanliness_and_tracked_evidence_are_bound(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(fixture.report_text(proof), encoding="utf-8")
            fixture.write_controlled_completion()

            accepted = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

            checkpoint_ref = "refs/heads/checkpoints/fixture/integration/g2"
            fixture.git_at(fixture.repo, "update-ref", checkpoint_ref, fixture.report_base)
            wrong_ref = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertNotEqual(0, wrong_ref.returncode, wrong_ref.stdout + wrong_ref.stderr)
            self.assertIn(
                "must resolve locally to the exact checkpoint sha",
                "\n".join(json.loads(wrong_ref.stderr)["errors"]),
            )
            fixture.git_at(fixture.repo, "update-ref", checkpoint_ref, fixture.report_commit)

            fixture.git_checked("checkout", "--detach", fixture.report_base)
            head_commands = [
                (
                    "validate-package-complete",
                    *fixture.root_args(),
                    ".tasks/fixture/tasks.json",
                    "--package",
                    "WP1",
                ),
                (
                    "emit-state-binding",
                    *fixture.root_args(),
                    ".tasks/fixture/tasks.json",
                    "--package",
                    "WP1",
                    *fixture.binding_cli_args(effective_digest=fixture.controlled_effective_digest),
                ),
            ]
            for command in head_commands:
                with self.subTest(command=command[0]):
                    wrong_head = fixture.run(*command)
                    self.assertNotEqual(0, wrong_head.returncode, wrong_head.stdout + wrong_head.stderr)
                    self.assertIn(
                        "HEAD must equal the exact bound candidate commit",
                        "\n".join(json.loads(wrong_head.stderr)["errors"]),
                    )
            fixture.git_checked("checkout", fixture.report_ref)

            fake_evidence = fixture.repo / "fake-evidence.py"
            fake_evidence.write_text("def forged(): pass\n", encoding="utf-8")
            report = fixture.report_path.read_text(encoding="utf-8").replace(
                "static:plugins/super-developer/assets/sliceproof.py#validate_plan",
                "static:fake-evidence.py#forged",
                1,
            )
            fixture.report_path.write_text(report, encoding="utf-8")
            dirty = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertNotEqual(0, dirty.returncode, dirty.stdout + dirty.stderr)
            dirty_errors = "\n".join(json.loads(dirty.stderr)["errors"])
            self.assertIn("worktree must be clean, including tracked and untracked files", dirty_errors)
            self.assertIn("must be a regular Git-tracked file in the bound candidate commit", dirty_errors)
        finally:
            fixture.cleanup()

    def test_distinct_root_completion_requires_controlled_stable_checkpoint_for_boundary_and_final(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(fixture.report_text(proof), encoding="utf-8")
            boundary_plan = fixture.plan()
            boundary_plan["work_packages"][0]["status"] = "done"
            fixture.write_plan(boundary_plan)
            fixture.write_controlled_completion()

            package_accepted = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertEqual(0, package_accepted.returncode, package_accepted.stdout + package_accepted.stderr)
            fixture.write_controlled_completion(package_states={"WP1": "done"})
            final_accepted = fixture.run("validate-final", *fixture.root_args(), ".tasks/fixture/tasks.json")
            self.assertEqual(0, final_accepted.returncode, final_accepted.stdout + final_accepted.stderr)

            fixture.write_lifecycle({
                "authorization": {
                    "id": REPORT_AUTHORIZATION_ID,
                    "effective_digest": fixture.controlled_effective_digest,
                },
                "assurance_profile": "standard",
                "package_modes": {"WP1": "boundary"},
                "packages": {"WP1": {"state": "done", "wave": None}},
                "code_checkpoint": {
                    "ref": "refs/heads/checkpoints/fixture/integration/g2",
                    "sha": fixture.report_commit,
                },
            })
            partial = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertNotEqual(0, partial.returncode, partial.stdout + partial.stderr)
            self.assertIn(
                "lifecycle-state.json: missing required field 'schema_version'",
                "\n".join(json.loads(partial.stderr)["errors"]),
            )

            boundary_failures = [
                (
                    {"package_states": {"WP1": "in_progress"}},
                    "must be stabilized, verified, or done",
                ),
                (
                    {"include_checkpoint": False},
                    "controlled code checkpoint is required",
                ),
                (
                    {"checkpoint_sha": fixture.report_base},
                    "boundary report commit must match the controlled code checkpoint",
                ),
            ]
            for kwargs, expected in boundary_failures:
                with self.subTest(mode="boundary", expected=expected):
                    fixture.write_controlled_completion(**kwargs)
                    rejected = fixture.run(
                        "validate-package-complete",
                        *fixture.root_args(),
                        ".tasks/fixture/tasks.json",
                        "--package",
                        "WP1",
                    )
                    self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                    self.assertIn(expected, "\n".join(json.loads(rejected.stderr)["errors"]))

            fixture.configure_primary_final(assurance_profile="standard", status="done")
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.write_controlled_completion(package_modes={"WP1": "final"})
            package_accepted = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP1",
            )
            self.assertEqual(0, package_accepted.returncode, package_accepted.stdout + package_accepted.stderr)
            fixture.write_controlled_completion(
                package_modes={"WP1": "final"},
                package_states={"WP1": "done"},
            )
            final_accepted = fixture.run("validate-final", *fixture.root_args(), ".tasks/fixture/tasks.json")
            self.assertEqual(0, final_accepted.returncode, final_accepted.stdout + final_accepted.stderr)

            fixture.write_controlled_completion(
                package_modes={"WP1": "final"},
                package_states={"WP1": "pending"},
                include_checkpoint=False,
            )
            for command in ("validate-package-complete", "validate-final"):
                with self.subTest(mode="final", command=command):
                    args = [command, *fixture.root_args(), ".tasks/fixture/tasks.json"]
                    if command == "validate-package-complete":
                        args.extend(["--package", "WP1"])
                    rejected = fixture.run(*args)
                    self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                    errors = "\n".join(json.loads(rejected.stderr)["errors"])
                    expected_state = (
                        "must be done"
                        if command == "validate-final"
                        else "must be stabilized, verified, or done"
                    )
                    self.assertIn(expected_state, errors)
                    self.assertIn("controlled code checkpoint is required", errors)
        finally:
            fixture.cleanup()

    def test_distinct_root_consumer_requires_fresh_done_boundary_dependency_unlock(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            producer_commit = fixture.report_commit
            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(
                fixture.report_text(
                    proof,
                    consumed_contract_digests=(("producer-contract", fixture.digest_text("contract")),),
                ),
                encoding="utf-8",
            )

            fixture.git_checked("checkout", "-b", "wp/fixture/WP2")
            fixture.git_checked("commit", "--allow-empty", "-m", "consumer candidate")
            consumer_commit = fixture.git_checked("rev-parse", "HEAD")
            fixture.report_base = producer_commit
            fixture.report_commit = consumer_commit
            fixture.report_tree = fixture.git_checked("rev-parse", "HEAD^{tree}")
            fixture.report_diff_digest = SLICEPROOF.raw_git_diff_identity(
                fixture.repo,
                producer_commit,
                consumer_commit,
                "consumer package diff",
            )
            fixture.report_ref = "wp/fixture/WP2"
            fixture.write_simple_package_artifacts(
                "WP2",
                must_ids=["HELPER-PIPE-004"],
                depends_on=["WP1"],
            )
            plan = fixture.plan()
            plan["work_packages"][0]["status"] = "done"
            plan["work_packages"].append({
                "id": "WP2",
                "path": ".tasks/fixture/packages/WP2.md",
                "proof_path": ".tasks/fixture/proofs/WP2.proof.md",
                "report_path": ".tasks/fixture/reports/WP2.package-verification.md",
                "verification_mode": "boundary",
                "status": "pending",
                "depends_on": ["WP1"],
            })
            fixture.write_plan(plan)
            modes = {"WP1": "boundary", "WP2": "boundary"}
            fixture.write_controlled_completion(
                package_states={"WP1": "done", "WP2": "stabilized"},
                package_modes=modes,
                checkpoint_sha=consumer_commit,
            )

            accepted = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP2",
            )
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

            fixture.write_controlled_completion(
                package_states={"WP1": "verified", "WP2": "stabilized"},
                package_modes=modes,
                checkpoint_sha=consumer_commit,
            )
            locked = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP2",
            )
            self.assertNotEqual(0, locked.returncode, locked.stdout + locked.stderr)
            self.assertIn(
                "controlled producer WP1 must be done",
                "\n".join(json.loads(locked.stderr)["errors"]),
            )

            fixture.write_controlled_completion(
                package_states={"WP1": "done", "WP2": "stabilized"},
                package_modes=modes,
                checkpoint_sha=consumer_commit,
            )
            fixture.git_checked("update-ref", "refs/heads/wp/fixture/WP1", consumer_commit)
            stale = fixture.run(
                "validate-package-complete",
                *fixture.root_args(),
                ".tasks/fixture/tasks.json",
                "--package",
                "WP2",
            )
            self.assertNotEqual(0, stale.returncode, stale.stdout + stale.stderr)
            self.assertIn(
                "Git Ref must resolve to the exact candidate commit",
                "\n".join(json.loads(stale.stderr)["errors"]),
            )
        finally:
            fixture.cleanup()

    def test_distinct_root_final_accepts_prior_boundary_candidates_and_requires_done_lifecycle(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            first_commit = fixture.report_commit
            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(fixture.report_text(proof), encoding="utf-8")

            fixture.git_checked("checkout", "-b", "wp/fixture/WP2")
            fixture.git_checked("commit", "--allow-empty", "-m", "second package candidate")
            second_commit = fixture.git_checked("rev-parse", "HEAD")
            fixture.report_base = first_commit
            fixture.report_commit = second_commit
            fixture.report_tree = fixture.git_checked("rev-parse", "HEAD^{tree}")
            fixture.report_diff_digest = SLICEPROOF.raw_git_diff_identity(
                fixture.repo,
                first_commit,
                second_commit,
                "second package diff",
            )
            fixture.report_ref = "wp/fixture/WP2"
            fixture.write_simple_package_artifacts("WP2", must_ids=["HELPER-PIPE-004"])

            plan = fixture.plan()
            plan["work_packages"][0]["status"] = "done"
            plan["work_packages"].append({
                "id": "WP2",
                "path": ".tasks/fixture/packages/WP2.md",
                "proof_path": ".tasks/fixture/proofs/WP2.proof.md",
                "report_path": ".tasks/fixture/reports/WP2.package-verification.md",
                "verification_mode": "boundary",
                "status": "done",
                "depends_on": [],
            })
            fixture.write_plan(plan)

            fixture.git_checked("checkout", "-b", "integration/fixture")
            fixture.git_checked("commit", "--allow-empty", "-m", "later integration checkpoint")
            integration_commit = fixture.git_checked("rev-parse", "HEAD")
            self.assertNotIn(integration_commit, {first_commit, second_commit})
            fixture.git_checked(
                "update-ref",
                "refs/heads/checkpoints/fixture/integration/g2",
                integration_commit,
            )
            fixture.write_controlled_completion(
                package_states={"WP1": "done", "WP2": "done"},
                package_modes={"WP1": "boundary", "WP2": "boundary"},
                checkpoint_sha=integration_commit,
            )

            accepted = fixture.run("validate-final", *fixture.root_args(), ".tasks/fixture/tasks.json")
            self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)
            self.assertEqual(
                [
                    ".tasks/fixture/reports/WP1.package-verification.md",
                    ".tasks/fixture/reports/WP2.package-verification.md",
                ],
                json.loads(accepted.stdout)["boundary_reports_validated"],
            )

            integration_dirt = fixture.repo / "untracked-integration-evidence.txt"
            integration_dirt.write_text("not part of the checkpoint\n", encoding="utf-8")
            dirty_final = fixture.run("validate-final", *fixture.root_args(), ".tasks/fixture/tasks.json")
            self.assertNotEqual(0, dirty_final.returncode, dirty_final.stdout + dirty_final.stderr)
            self.assertIn(
                "integration code root: worktree must be clean, including tracked and untracked files",
                "\n".join(json.loads(dirty_final.stderr)["errors"]),
            )
            integration_dirt.unlink()

            fixture.write_controlled_completion(
                package_states={"WP1": "done", "WP2": "verified"},
                package_modes={"WP1": "boundary", "WP2": "boundary"},
                checkpoint_sha=integration_commit,
            )
            rejected = fixture.run("validate-final", *fixture.root_args(), ".tasks/fixture/tasks.json")
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn(
                "controlled package WP2 must be done",
                "\n".join(json.loads(rejected.stderr)["errors"]),
            )
        finally:
            fixture.cleanup()

    def test_explicit_roots_reject_artifact_and_code_path_escape_masking(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not available on this platform")
        cases = []

        def artifact_symlink_mask(fixture: SliceproofFixture) -> None:
            fixture.package_path.unlink()
            outside = fixture.external_worktree / "WP1.md"
            outside.write_text(fixture.package_text(), encoding="utf-8")
            fixture.package_path.symlink_to(outside)
            code_package = fixture.repo / ".tasks" / "fixture" / "packages" / "WP1.md"
            code_package.parent.mkdir(parents=True)
            code_package.write_text(fixture.package_text(), encoding="utf-8")

        cases.append(("artifact symlink escape masked by code root", artifact_symlink_mask, "path escapes artifact root"))

        def missing_artifact_mask(fixture: SliceproofFixture) -> None:
            fixture.package_path.unlink()
            code_package = fixture.repo / ".tasks" / "fixture" / "packages" / "WP1.md"
            code_package.parent.mkdir(parents=True)
            code_package.write_text(fixture.package_text(), encoding="utf-8")

        cases.append(("missing artifact file masked by code root", missing_artifact_mask, "file not found"))

        def code_symlink_mask(fixture: SliceproofFixture) -> None:
            fixture.package_path.write_text(fixture.package_text(primary_paths=["src/escape.py"]), encoding="utf-8")
            artifact_source = fixture.artifact_root / "src" / "escape.py"
            artifact_source.parent.mkdir()
            artifact_source.write_text("# artifact-only source must not mask code-root escape\n", encoding="utf-8")
            outside = fixture.external_worktree / "escape.py"
            outside.write_text("# outside code root\n", encoding="utf-8")
            (fixture.repo / "src").symlink_to(fixture.external_worktree)

        cases.append(("code symlink escape masked by artifact root", code_symlink_mask, "path escapes code root"))

        def absolute_code_primary(fixture: SliceproofFixture) -> None:
            fixture.package_path.write_text(fixture.package_text(primary_paths=[str(fixture.repo / "absolute.py")]), encoding="utf-8")

        cases.append(("absolute code primary", absolute_code_primary, "not absolute/home/drive-qualified"))

        def parent_artifact_path(fixture: SliceproofFixture) -> None:
            plan = fixture.plan()
            plan["spec_path"] = "../SPEC.md"
            fixture.write_plan(plan)

        cases.append(("parent artifact path", parent_artifact_path, "path must not contain"))

        for name, mutate, expected_error in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture(separate_roots=True)
                try:
                    mutate(fixture)
                    result = fixture.run("validate-plan", *fixture.root_args(), ".tasks/fixture/tasks.json")
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

    def test_validate_plan_rejects_registry_path_package_report_and_h3_failures(self) -> None:
        cases = []

        unsupported_plan = self.fixture.plan()
        unsupported_plan["schema_extra"] = 4
        cases.append(("unsupported registry field", lambda fixture: fixture.write_plan(unsupported_plan), "unsupported registry field"))

        unsafe_plan = self.fixture.plan()
        unsafe_plan["work_packages"][0]["path"] = "../escape.md"
        cases.append(("unsafe path", lambda fixture: fixture.write_plan(unsafe_plan), "path must not contain"))

        unsafe_report = self.fixture.plan()
        unsafe_report["work_packages"][0]["report_path"] = "/tmp/WP1.package-verification.md"
        cases.append(("unsafe report path", lambda fixture: fixture.write_plan(unsafe_report), "not absolute/home/drive-qualified"))

        missing_section_text = self.fixture.package_text(missing_section="Independent Verification")
        cases.append(("missing independent verification", lambda fixture: fixture.package_path.write_text(missing_section_text, encoding="utf-8"), "missing required section ## Independent Verification"))

        unknown_dependency = self.fixture.plan()
        unknown_dependency["work_packages"][0]["depends_on"] = ["WP9"]
        cases.append(("unknown dependency", lambda fixture: fixture.write_plan(unknown_dependency), "unknown package id WP9"))

        missing_h3 = self.fixture.package_text(must_id="HELPER-MISSING-404")
        cases.append(("missing H3", lambda fixture: fixture.package_path.write_text(missing_h3, encoding="utf-8"), "not found as H3"))

        fenced_h3 = self.fixture.package_text(must_id="HELPER-CODE-999")
        cases.append(("fenced H3 ignored", lambda fixture: fixture.package_path.write_text(fenced_h3, encoding="utf-8"), "not found as H3"))

        outside_shared_h3 = self.fixture.package_text(must_id="HELPER-OUTSIDE-998")
        cases.append(("outside Shared Understanding H3 ignored", lambda fixture: fixture.package_path.write_text(outside_shared_h3, encoding="utf-8"), "not found as H3"))

        for name, mutate, expected_error in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    mutate(fixture)
                    result = fixture.run("validate-plan", str(fixture.tasks_path))
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

    def test_validate_plan_rejects_malformed_assignment_ids_in_must_and_context_lists(self) -> None:
        cases = [
            ("must lowercase", lambda fixture: fixture.package_path.write_text(fixture.package_text(must_id="helper-plan-001"), encoding="utf-8"), "must_satisfy ID 'helper-plan-001' has unsupported shape"),
            ("must bad shape", lambda fixture: fixture.package_path.write_text(fixture.package_text(must_id="HELPER-PLAN"), encoding="utf-8"), "must_satisfy ID 'HELPER-PLAN' has unsupported shape"),
            ("must missing", lambda fixture: fixture.package_path.write_text(fixture.package_text(must_id=None), encoding="utf-8"), "must_satisfy ID 'Registry and package references validate mechanically' has unsupported shape"),
            ("context lowercase", lambda fixture: fixture.package_path.write_text(fixture.package_text(context_id="helper-context-003"), encoding="utf-8"), "context_only ID 'helper-context-003' has unsupported shape"),
            ("context bad shape", lambda fixture: fixture.package_path.write_text(fixture.package_text(context_id="HELPER-CONTEXT"), encoding="utf-8"), "context_only ID 'HELPER-CONTEXT' has unsupported shape"),
            ("context missing", lambda fixture: fixture.package_path.write_text(fixture.package_text(context_id=None), encoding="utf-8"), "context_only ID 'Context-only IDs stay required reading' has unsupported shape"),
        ]
        for name, mutate, expected_error in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    mutate(fixture)
                    result = fixture.run("validate-plan", str(fixture.tasks_path))
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

    def test_create_proof_generates_idempotent_placeholder_from_package_markdown(self) -> None:
        result = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["created"])
        proof = self.fixture.proof_path.read_text(encoding="utf-8")
        self.assertIn("| `HELPER-PLAN-001` |", proof)
        self.assertIn("| `HELPER-PROOF-002` |", proof)
        self.assertIn("Context only: `HELPER-CONTEXT-003`", proof)
        self.assertNotIn("| `HELPER-CONTEXT-003` |", proof)

        second = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, second.returncode, second.stdout + second.stderr)
        second_data = json.loads(second.stdout)
        self.assertFalse(second_data["created"])
        self.assertTrue(second_data["already_existed"])
        self.assertEqual(proof, self.fixture.proof_path.read_text(encoding="utf-8"))

        placeholder_validation = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, placeholder_validation.returncode)
        self.assertIn("unresolved TODO/OPEN/GAP", "\n".join(json.loads(placeholder_validation.stderr)["errors"]))

    def test_create_proof_refuses_existing_repo_internal_symlink_at_proof_path(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not available on this platform")
        target = self.fixture.proofs_dir / "alternate.proof.md"
        target.write_text("existing target must not be overwritten\n", encoding="utf-8")
        os.symlink(target.name, self.fixture.proof_path)

        result = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertEqual("existing target must not be overwritten\n", target.read_text(encoding="utf-8"))
        self.assertIn("refusing to write through symlink proof path", "\n".join(json.loads(result.stderr)["errors"]))


    def test_validate_proof_accepts_completed_rows_and_rejects_blocking_or_unapproved_rows(self) -> None:
        self.fixture.proof_path.write_text(self.fixture.completed_proof(), encoding="utf-8")
        result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        cases = [
            ("TODO", "PASS", "TODO", "observed command output", "- None.", "implementation evidence is missing"),
            ("OPEN", "OPEN", "some implementation evidence", "observed command output", "- None.", "status OPEN blocks"),
            ("GAP", "GAP", "some implementation evidence", "observed command output", "- None.", "status GAP blocks"),
            ("DEFERRED", "DEFERRED", "some implementation evidence", "observed command output", "- None.", "DEFERRED requires approval"),
            ("N/A", "N/A", "some implementation evidence", "observed command output", "- None.", "N/A requires rationale"),
            ("missing verification", "PASS", "some implementation evidence", "", "- None.", "verification evidence is missing"),
            ("arbitrary gap", "PASS", "some implementation evidence", "observed command output", "- Investigate fixture evidence before dispatch.", "gap/deviation text without approval"),
            ("bare approval", "PASS", "some implementation evidence", "observed command output", "- Approval for gap; provenance: user note; scope: WP1 proof.", "gap/deviation text without approval"),
            ("pending approval", "PASS", "some implementation evidence", "observed command output", "- Approval pending; provenance: user note; scope: WP1 proof.", "gap/deviation text without approval"),
            ("negated approval", "PASS", "some implementation evidence", "observed command output", "- Unapproved gap; provenance: none; scope: all evidence.", "gap/deviation text without approval"),
            ("deferred pending approval", "DEFERRED", "approval requested; provenance: user note; scope: WP1 proof", "observed command output", "- None.", "DEFERRED requires approval"),
        ]
        for approval_variant in PLACEHOLDER_APPROVAL_VARIANTS:
            cases.append(
                (
                    f"gap approval placeholder: {approval_variant}",
                    "PASS",
                    "some implementation evidence",
                    "observed command output",
                    f"- {approval_variant}.",
                    "gap/deviation text without approval",
                )
            )
            cases.append(
                (
                    f"deferred approval placeholder: {approval_variant}",
                    "DEFERRED",
                    approval_variant,
                    "observed command output",
                    "- None.",
                    "DEFERRED requires approval",
                )
            )
            cases.append(
                (
                    f"n/a approval placeholder: {approval_variant}",
                    "N/A",
                    f"rationale: fixture row intentionally not applicable; {approval_variant}",
                    "observed command output",
                    "- None.",
                    "N/A requires rationale plus approval",
                )
            )
        for name, status, implementation, verification, gaps, expected_error in cases:
            with self.subTest(name=name):
                self.fixture.proof_path.write_text(
                    self.fixture.completed_proof(status=status, implementation=implementation, verification=verification, gaps=gaps),
                    encoding="utf-8",
                )
                invalid = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertNotEqual(0, invalid.returncode, invalid.stdout + invalid.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(invalid.stderr)["errors"]))

        approved_variants = [
            "Approved by user; provenance: user accepted excluding flaky external check; scope: this package proof only.",
            "User-approved: product owner; provenance: product owner accepted excluding flaky external check; scope: this package proof only.",
            "User-approved by product owner; provenance: product owner accepted excluding flaky external check; scope: this package proof only.",
        ]
        for approval in approved_variants:
            with self.subTest(approval=approval):
                approved_gap = self.fixture.completed_proof(gaps=f"- {approval}")
                self.fixture.proof_path.write_text(approved_gap, encoding="utf-8")
                approved = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertEqual(0, approved.returncode, approved.stdout + approved.stderr)

    def test_validate_proof_rejects_deferred_na_metadata_copied_from_non_evidence_cells(self) -> None:
        malicious_required = (
            "Registry and package references validate mechanically; rationale: copied source text says not applicable; "
            "Approved by user; provenance: copied Slice prose; scope: copied Required understanding only."
        )
        for status, expected_error in [
            ("DEFERRED", "DEFERRED requires approval"),
            ("N/A", "N/A requires rationale plus approval"),
        ]:
            with self.subTest(table="slice", status=status):
                proof = self.fixture.completed_proof(
                    status=status,
                    implementation="mechanical note without approval metadata.",
                    verification="verification note without approval metadata.",
                )
                proof = proof.replace(
                    "| `HELPER-PLAN-001` | Registry and package references validate mechanically |",
                    f"| `HELPER-PLAN-001` | {malicious_required} |",
                    1,
                )
                self.fixture.proof_path.write_text(proof, encoding="utf-8")
                result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))

        malicious_expectation = (
            "sliceproof.py validate-plan succeeds for the valid fixture; rationale: copied package prose says not applicable; "
            "Approved by user; provenance: copied Expectation prose; scope: copied Expectation only."
        )
        package_text = self.fixture.package_text().replace(
            "- `sliceproof.py validate-plan` succeeds for the valid fixture.",
            f"- {malicious_expectation}",
            1,
        )
        self.fixture.package_path.write_text(package_text, encoding="utf-8")
        original_expectation_row = (
            "| `sliceproof.py validate-plan` succeeds for the valid fixture. | "
            "unittest fixture observed validate-plan exit 0. | PASS |"
        )
        for status, expected_error in [
            ("DEFERRED", "DEFERRED requires approval"),
            ("N/A", "N/A requires rationale plus approval"),
        ]:
            with self.subTest(table="acceptance", status=status):
                proof = self.fixture.completed_proof().replace(
                    original_expectation_row,
                    f"| {malicious_expectation} | evidence note without approval metadata. | {status} |",
                    1,
                )
                self.fixture.proof_path.write_text(proof, encoding="utf-8")
                result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))

    def test_validate_proof_accepts_deferred_na_metadata_from_evidence_or_gaps(self) -> None:
        approval = "Approved by user; provenance: user approved closure metadata; scope: WP1 proof row only."
        rationale_approval = f"rationale: row intentionally not applicable; {approval}"
        original_expectation_row = (
            "| `sliceproof.py validate-plan` succeeds for the valid fixture. | "
            "unittest fixture observed validate-plan exit 0. | PASS |"
        )

        acceptance_deferred = self.fixture.completed_proof().replace(
            original_expectation_row,
            f"| `sliceproof.py validate-plan` succeeds for the valid fixture. | {approval} | DEFERRED |",
            1,
        )
        acceptance_na = self.fixture.completed_proof().replace(
            original_expectation_row,
            f"| `sliceproof.py validate-plan` succeeds for the valid fixture. | {rationale_approval} | N/A |",
            1,
        )
        slice_deferred_from_gaps = self.fixture.completed_proof(
            status="DEFERRED",
            implementation="deferred in explicit closure metadata.",
            verification="not run for deferred row.",
            gaps=f"- {approval}",
        )
        acceptance_na_from_gaps = self.fixture.completed_proof().replace(
            original_expectation_row,
            "| `sliceproof.py validate-plan` succeeds for the valid fixture. | deferred in explicit metadata. | N/A |",
            1,
        ).replace(
            "## Gaps, Deviations, or Deferred Items\n- None.",
            f"## Gaps, Deviations, or Deferred Items\n- {rationale_approval}",
            1,
        )

        cases = [
            (
                "slice deferred evidence",
                self.fixture.completed_proof(status="DEFERRED", implementation=approval, verification="not run for deferred row."),
            ),
            (
                "slice n/a evidence",
                self.fixture.completed_proof(status="N/A", implementation=rationale_approval, verification="not applicable."),
            ),
            ("slice deferred gaps", slice_deferred_from_gaps),
            ("acceptance deferred evidence", acceptance_deferred),
            ("acceptance n/a evidence", acceptance_na),
            ("acceptance n/a gaps", acceptance_na_from_gaps),
        ]
        for name, proof in cases:
            with self.subTest(name=name):
                self.fixture.proof_path.write_text(proof, encoding="utf-8")
                result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validate_proof_rejects_duplicate_unexpected_and_contradictory_rows(self) -> None:
        proof = self.fixture.completed_proof()
        duplicate_slice = (
            "| `HELPER-PLAN-001` | unresolved duplicate | TODO | TODO | OPEN |\n"
            "| `HELPER-PLAN-001` | Registry and package references validate mechanically |"
        )
        proof = proof.replace(
            "| `HELPER-PLAN-001` | Registry and package references validate mechanically |",
            duplicate_slice,
            1,
        )
        duplicate_expectation = (
            "| `sliceproof.py validate-plan` succeeds for the valid fixture. | TODO | OPEN |\n"
            "| `sliceproof.py validate-plan` succeeds for the valid fixture. |"
        )
        proof = proof.replace(
            "| `sliceproof.py validate-plan` succeeds for the valid fixture. |",
            duplicate_expectation,
            1,
        )
        proof = proof.replace(
            "| `HELPER-PROOF-002` | Proof placeholders and proof closure are mechanical |",
            "| `HELPER-EXTRA-999` | unexpected | evidence | verification | PASS |\n| `HELPER-PROOF-002` | Proof placeholders and proof closure are mechanical |",
            1,
        )
        self.fixture.proof_path.write_text(proof, encoding="utf-8")

        result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        errors = "\n".join(json.loads(result.stderr)["errors"])
        self.assertIn("duplicate Slice Closure Table row for HELPER-PLAN-001", errors)
        self.assertIn("HELPER-PLAN-001 status OPEN blocks", errors)
        self.assertIn("unexpected Slice Closure Table row for HELPER-EXTRA-999", errors)
        self.assertIn("duplicate Acceptance / Verification Closure row", errors)

    def test_escaped_pipe_table_cells_round_trip_from_generated_proof(self) -> None:
        package_text = self.fixture.package_text(must_id="HELPER-PIPE-004").replace(
            "- `sliceproof.py validate-plan` succeeds for the valid fixture.",
            "- `printf 'a|b' | wc -c` preserves escaped pipe output.",
        )
        self.fixture.package_path.write_text(package_text, encoding="utf-8")
        created = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        placeholder = self.fixture.proof_path.read_text(encoding="utf-8")
        self.assertIn("A \\| B", placeholder)
        self.assertIn("'a\\|b' \\| wc", placeholder)
        completed = placeholder.replace("TODO", "observed evidence").replace("OPEN", "PASS")
        self.fixture.proof_path.write_text(completed, encoding="utf-8")

        result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_create_proof_refuses_unsafe_overwrites_and_preserves_approved_replacement(self) -> None:
        first = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        filled = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(filled, encoding="utf-8")

        no_force = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, no_force.returncode)
        self.assertIn("refusing overwrite", "\n".join(json.loads(no_force.stderr)["errors"]))
        self.assertEqual(filled, self.fixture.proof_path.read_text(encoding="utf-8"))

        missing_approval = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1", "--force")
        self.assertNotEqual(0, missing_approval.returncode)
        self.assertIn("without approved replacement metadata", "\n".join(json.loads(missing_approval.stderr)["errors"]))
        self.assertEqual(filled, self.fixture.proof_path.read_text(encoding="utf-8"))

        weak_approval = self.fixture.run(
            "create-proof",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            "--force",
            "--approved-replacement",
            "approved replacement",
        )
        self.assertNotEqual(0, weak_approval.returncode)
        self.assertIn("approval, provenance, and scope", "\n".join(json.loads(weak_approval.stderr)["errors"]))
        self.assertEqual(filled, self.fixture.proof_path.read_text(encoding="utf-8"))

        non_approvals = [
            "approval pending; provenance: user note; scope: WP1 proof placeholder only.",
            "approval requested; provenance: user note; scope: WP1 proof placeholder only.",
            "Approved by user; provenance: none; scope: WP1 proof placeholder only.",
            "Approved by user; provenance: stale fixture proof intentionally reset; scope: TBD.",
            *PLACEHOLDER_APPROVAL_VARIANTS,
        ]
        for replacement in non_approvals:
            with self.subTest(replacement=replacement):
                rejected = self.fixture.run(
                    "create-proof",
                    str(self.fixture.tasks_path),
                    "--package",
                    "WP1",
                    "--force",
                    "--approved-replacement",
                    replacement,
                )
                self.assertNotEqual(0, rejected.returncode)
                self.assertIn("approval, provenance, and scope", "\n".join(json.loads(rejected.stderr)["errors"]))
                self.assertEqual(filled, self.fixture.proof_path.read_text(encoding="utf-8"))

        approved = self.fixture.run(
            "create-proof",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            "--force",
            "--approved-replacement",
            "Approved by user; provenance: stale fixture proof intentionally reset; scope: WP1 proof placeholder only.",
        )
        self.assertEqual(0, approved.returncode, approved.stdout + approved.stderr)
        data = json.loads(approved.stdout)
        backup = self.fixture.repo / data["preserved_existing_proof"]
        self.assertTrue(backup.exists())
        self.assertEqual(filled, backup.read_text(encoding="utf-8"))
        self.assertIn("TODO", self.fixture.proof_path.read_text(encoding="utf-8"))

    def test_create_proof_preserve_backup_rejects_dangling_symlink(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not available on this platform")
        filled = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(filled, encoding="utf-8")
        digest = hashlib.sha256(filled.encode("utf-8")).hexdigest()[:12]
        backup = self.fixture.proof_path.with_name(f"{self.fixture.proof_path.name}.preserved.{digest}.bak")
        outside = self.fixture.repo.parent / "outside-created-by-symlink.txt"
        if outside.exists():
            outside.unlink()
        os.symlink(outside, backup)

        result = self.fixture.run(
            "create-proof",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            "--force",
            "--approved-replacement",
            "Approved by user; provenance: stale evidence reset; scope: WP1 proof placeholder only.",
        )
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse(outside.exists())
        self.assertEqual(filled, self.fixture.proof_path.read_text(encoding="utf-8"))
        self.assertIn("preservation backup path is a symlink", "\n".join(json.loads(result.stderr)["errors"]))

    def test_cli_reports_structured_json_for_common_io_failures(self) -> None:
        directory_input = self.fixture.run("validate-plan", str(self.fixture.feature_dir))
        self.assertNotEqual(0, directory_input.returncode)
        self.assertNotIn("Traceback", directory_input.stderr)
        directory_errors = json.loads(directory_input.stderr)["errors"]
        self.assertIn("unable to read", "\n".join(directory_errors))

        self.fixture.slice_path.write_bytes(b"\xff")
        decode_error = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertNotEqual(0, decode_error.returncode)
        self.assertNotIn("Traceback", decode_error.stderr)
        self.assertIn("unable to decode UTF-8", "\n".join(json.loads(decode_error.stderr)["errors"]))

        self.fixture.slice_path.write_text(self.fixture.slice_text(), encoding="utf-8")
        self.fixture.proofs_dir.rmdir()
        self.fixture.proofs_dir.write_text("not a directory", encoding="utf-8")
        write_error = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, write_error.returncode)
        self.assertNotIn("Traceback", write_error.stderr)
        self.assertIn("unable to create directory", "\n".join(json.loads(write_error.stderr)["errors"]))

    def test_validate_final_requires_done_proofs_and_report_binding_fields(self) -> None:
        self.fixture.write_completed_proof_and_report()
        not_done = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, not_done.returncode)
        self.assertIn("expected 'done'", "\n".join(json.loads(not_done.stderr)["errors"]))

        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        done = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)

        valid_report = self.fixture.report_path.read_text(encoding="utf-8")
        state_binding_index = valid_report.index("## State Binding")
        state_binding_first_report = valid_report[state_binding_index:] + "\n" + valid_report[:state_binding_index]
        verdict_index = valid_report.index("### Verdict")
        slice_review_index = valid_report.index("### Slice Closure Review")
        code_review_index = valid_report.index("### Code Review Findings")
        h3_reordered_report = (
            valid_report[:verdict_index]
            + valid_report[slice_review_index:code_review_index]
            + valid_report[verdict_index:slice_review_index]
            + valid_report[code_review_index:]
        )
        valid_worktree_line = f"- Worktree: `{self.fixture.repo.resolve(strict=False)}`"
        valid_ref_line = "- Git Ref: `wp/fixture/WP1`"
        valid_commit_line = f"- Commit / Tree: `{self.fixture.report_commit} | {self.fixture.report_tree}`"
        valid_verified_at_line = "- Verified At: `2026-06-04T00:00:00Z`"
        report_cases = [
            (
                "missing package markdown",
                valid_report.replace("- Package Markdown: `.tasks/fixture/packages/WP1.md`\n", ""),
                "missing 'Package Markdown'",
            ),
            (
                "wrong package markdown",
                valid_report.replace(".tasks/fixture/packages/WP1.md", ".tasks/fixture/packages/WP2.md"),
                "State Binding Package Markdown must be .tasks/fixture/packages/WP1.md",
            ),
            (
                "missing assigned slices",
                valid_report.replace("- Assigned Slices: `.planning/fixture/slices/helper.md`\n", ""),
                "missing 'Assigned Slices'",
            ),
            (
                "wrong assigned slices",
                valid_report.replace(".planning/fixture/slices/helper.md", ".planning/fixture/slices/other.md"),
                "State Binding Assigned Slices must be .planning/fixture/slices/helper.md",
            ),
            (
                "relative worktree binding",
                valid_report.replace(valid_worktree_line, "- Worktree: `relative/worktree`"),
                "--worktree must be an absolute reviewed worktree path",
            ),
            (
                "state binding before source body",
                state_binding_first_report,
                "first report section must be ## Package Verification: WP1",
            ),
            (
                "source h3 sections out of order",
                h3_reordered_report,
                "source report sections must appear in order",
            ),
            (
                "invalid commit",
                valid_report.replace(valid_commit_line, f"- Commit / Tree: `not-a-commit | {self.fixture.report_tree}`"),
                "Commit must be an exact lowercase",
            ),
            (
                "too short commit",
                valid_report.replace(valid_commit_line, f"- Commit / Tree: `abc123 | {self.fixture.report_tree}`"),
                "Commit must be an exact lowercase",
            ),
            (
                "invalid verified at",
                valid_report.replace(valid_verified_at_line, "- Verified At: `not-a-date`"),
                "expected timezone-aware ISO-8601",
            ),
            (
                "failed verdict",
                valid_report.replace("### Verdict\nPASS", "### Verdict\nFAIL"),
                "### Verdict must be PASS for boundary package completion",
            ),
            (
                "invalid verdict spelling",
                valid_report.replace("### Verdict\nPASS", "### Verdict\npassed"),
                "### Verdict must be PASS or FAIL",
            ),
            (
                "missing source report body",
                valid_report.replace("## Package Verification: WP1", "# Package Verification Report: WP1 — Helper behavior"),
                "missing required section ## Package Verification: WP1",
            ),
            (
                "missing verdict",
                remove_h3_section(valid_report, "Verdict"),
                "missing required source section ### Verdict",
            ),
            (
                "missing selected causal evidence",
                remove_h3_section(valid_report, "Selected Causal Evidence"),
                "missing required source section ### Selected Causal Evidence",
            ),
            (
                "missing slice closure review",
                remove_h3_section(valid_report, "Slice Closure Review"),
                "missing required source section ### Slice Closure Review",
            ),
            (
                "missing code review findings",
                remove_h3_section(valid_report, "Code Review Findings"),
                "missing required source section ### Code Review Findings",
            ),
            (
                "slice closure placeholder",
                valid_report.replace("Fixture proof closure verified mechanically.", "TODO", 1),
                "### Slice Closure Review contains unresolved TODO/OPEN/GAP marker",
            ),
            (
                "slice closure missing required row",
                re.sub(r"\n\| `HELPER-PROOF-002` .*", "", valid_report, count=1),
                "### Slice Closure Review missing required row for HELPER-PROOF-002",
            ),
            (
                "slice closure non-pass proof status",
                valid_report.replace("| `HELPER-PLAN-001` | `PASS` | yes |", "| `HELPER-PLAN-001` | `DEFERRED` | yes |"),
                "HELPER-PLAN-001 Proof status must be PASS",
            ),
            (
                "slice closure insufficient evidence",
                valid_report.replace("| `HELPER-PLAN-001` | `PASS` | yes |", "| `HELPER-PLAN-001` | `PASS` | no |"),
                "HELPER-PLAN-001 Evidence sufficient? must be yes",
            ),
            (
                "code review findings placeholder",
                valid_report.replace("### Code Review Findings\n- None.", "### Code Review Findings\nTODO"),
                "### Code Review Findings must contain non-placeholder review evidence",
            ),
            (
                "blocking findings non-empty",
                valid_report.replace("### Blocking Findings\n- None.", "### Blocking Findings\n- Fixture blocker remains."),
                "### Blocking Findings must be empty or None for boundary completion",
            ),
            (
                "fail report missing blocking findings",
                remove_h3_section(valid_report.replace("### Verdict\nPASS", "### Verdict\nFAIL"), "Blocking Findings"),
                "FAIL report missing required source section ### Blocking Findings",
            ),
            (
                "fail report missing repair guidance",
                remove_h3_section(valid_report.replace("### Verdict\nPASS", "### Verdict\nFAIL"), "Repair Guidance"),
                "FAIL report missing required source section ### Repair Guidance",
            ),
        ]
        placeholder_variants = [
            "none",
            "no",
            "n/a",
            "na",
            "tbd",
            "to be determined",
            "to-be-determined",
            "to_be_determined",
            "todo",
            "open",
            "gap",
            "unknown",
            "unconfirmed",
            "missing",
            "absent",
            "pending",
            "requested",
            "awaiting",
            "not set",
            "not-set",
            "not_set",
            "unset",
            "not provided",
            "not-provided",
            "not_provided",
            "not supplied",
            "not-supplied",
            "not_supplied",
            "  to...be___determined  ",
            "  not---provided.  ",
        ]
        binding_fields = {
            "Worktree": valid_worktree_line,
            "Git Ref": valid_ref_line,
        }
        for field, valid_line in binding_fields.items():
            for placeholder in placeholder_variants:
                report_cases.append(
                    (
                        f"{field} placeholder {placeholder!r}",
                        valid_report.replace(valid_line, f"- {field}: `{placeholder}`"),
                        f"State Binding {field} must be non-placeholder",
                    )
                )
        for name, report, expected_error in report_cases:
            with self.subTest(name=name):
                self.fixture.report_path.write_text(report, encoding="utf-8")
                invalid_report = self.fixture.run("validate-final", str(self.fixture.tasks_path))
                self.assertNotEqual(0, invalid_report.returncode, invalid_report.stdout + invalid_report.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(invalid_report.stderr)["errors"]))

        with self.subTest(name="stale open findings rejected when present"):
            self.fixture.report_path.write_text(valid_report + "\n## Open Findings\n- OPEN stale blocker\n", encoding="utf-8")
            rejected = self.fixture.run("validate-final", str(self.fixture.tasks_path))
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("## Open Findings contains unresolved TODO/OPEN marker", "\n".join(json.loads(rejected.stderr)["errors"]))

        self.fixture.report_path.write_text(valid_report, encoding="utf-8")

        self.fixture.report_path.unlink()
        missing_report = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, missing_report.returncode)
        self.assertIn("report: file not found", "\n".join(json.loads(missing_report.stderr)["errors"]))

        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        self.fixture.report_path.write_text(self.fixture.report_text(proof), encoding="utf-8")
        self.fixture.proof_path.write_text(proof.replace("Mechanical helper evidence", "Changed proof evidence"), encoding="utf-8")
        stale_report = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, stale_report.returncode)
        self.assertIn("Proof Digest does not match current proof content", "\n".join(json.loads(stale_report.stderr)["errors"]))

    def test_state_binding_uses_section_scoped_tier_aware_slice_digests(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        self.fixture.report_path.write_text(self.fixture.report_text(proof), encoding="utf-8")
        binding = self.fixture.assigned_slice_digests()
        entries = SLICEPROOF.assigned_slice_digest_entries(self.fixture.artifact_root, self.fixture.package_markdown())

        self.assertEqual(SLICEPROOF.format_assigned_slice_digest_entries(entries), binding)
        self.assertIn(".planning/fixture/slices/helper.md|must_satisfy|HELPER-PLAN-001=sha256:", binding)
        self.assertIn(".planning/fixture/slices/helper.md|must_satisfy|HELPER-PROOF-002=sha256:", binding)
        self.assertIn(".planning/fixture/slices/helper.md|context_only|HELPER-CONTEXT-003=sha256:", binding)
        self.assertNotIn("HELPER-INTERFACE-005", binding)
        self.assertNotIn(self.fixture.digest_text(self.fixture.slice_path.read_text(encoding="utf-8")), binding)

        snapshot = self.fixture.matrix_source_snapshot()
        self.fixture.slice_path.write_text(
            self.fixture.slice_path.read_text(encoding="utf-8").replace(
                "Must exist: a stable fixture command interface.",
                "Must exist: a changed fixture command interface.",
                1,
            ),
            encoding="utf-8",
        )

        self.assertEqual(binding, self.fixture.assigned_slice_digests())
        self.assertEqual(snapshot, self.fixture.matrix_source_snapshot())
        result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_state_binding_is_order_independent_for_sections_and_assignments(self) -> None:
        original_binding = self.fixture.assigned_slice_digests()
        original_snapshot = self.fixture.matrix_source_snapshot()
        text = self.fixture.slice_path.read_text(encoding="utf-8")
        prefix, rest = text.split("\n### HELPER-PLAN-001", 1)
        sections = re.split(r"(?=\n### HELPER-[A-Z-]+-\d{3})", "\n### HELPER-PLAN-001" + rest)
        by_id = {re.match(r"\n### (HELPER-[A-Z-]+-\d{3})", section).group(1): section for section in sections if section.strip()}
        self.fixture.slice_path.write_text(
            prefix
            + by_id["HELPER-INTERFACE-005"]
            + by_id["HELPER-CONTEXT-003"]
            + by_id["HELPER-PROOF-002"]
            + by_id["HELPER-PLAN-001"]
            + by_id["HELPER-PIPE-004"],
            encoding="utf-8",
        )
        self.assertEqual(original_binding, self.fixture.assigned_slice_digests())
        self.assertEqual(original_snapshot, self.fixture.matrix_source_snapshot())

        self.fixture.slice_path.write_text(text, encoding="utf-8")
        package_text = self.fixture.package_text().replace(
            "- `HELPER-PLAN-001` — Registry and package references validate mechanically\n- `HELPER-PROOF-002` — Proof placeholders and proof closure are mechanical",
            "- `HELPER-PROOF-002` — Proof placeholders and proof closure are mechanical\n- `HELPER-PLAN-001` — Registry and package references validate mechanically",
            1,
        )
        self.fixture.package_path.write_text(package_text, encoding="utf-8")
        self.assertEqual(original_binding, self.fixture.assigned_slice_digests())

    def test_missing_assigned_h3_fails_closed_with_section_scoped_error(self) -> None:
        self.fixture.slice_path.write_text(remove_h3_section(self.fixture.slice_path.read_text(encoding="utf-8"), "HELPER-CONTEXT-003"), encoding="utf-8")

        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "assigned H3 'HELPER-CONTEXT-003' not found in Slice '.planning/fixture/slices/helper.md'",
            "\n".join(json.loads(result.stderr)["errors"]),
        )

    def test_assigned_slice_paths_with_state_binding_delimiters_fail_before_emit(self) -> None:
        cases = [
            ("pipe", ".planning/fixture/slices/helper|pipe.md", "|"),
            ("equals", ".planning/fixture/slices/helper=equals.md", "="),
            ("entry delimiter", ".planning/fixture/slices/helper; delimiter.md", "; "),
        ]
        for name, slice_rel, delimiter in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    new_slice = fixture.artifact_root / slice_rel
                    new_slice.parent.mkdir(parents=True, exist_ok=True)
                    new_slice.write_text(fixture.slice_text(), encoding="utf-8")
                    plan = fixture.plan()
                    plan["authoritative_slices"] = [slice_rel]
                    fixture.write_plan(plan)
                    fixture.package_path.write_text(
                        fixture.package_text().replace(".planning/fixture/slices/helper.md", slice_rel),
                        encoding="utf-8",
                    )
                    fixture.proof_path.write_text(fixture.completed_proof(), encoding="utf-8")

                    plan_result = fixture.run("validate-plan", str(fixture.tasks_path))
                    self.assertNotEqual(0, plan_result.returncode, plan_result.stdout + plan_result.stderr)
                    plan_errors = "\n".join(json.loads(plan_result.stderr)["errors"])
                    self.assertIn("State Binding Assigned Slice path must not contain", plan_errors)
                    self.assertIn("path|tier|H3-ID=sha256:<64-hex>", plan_errors)
                    self.assertIn(delimiter, plan_errors)

                    emit = fixture.run(
                        "emit-state-binding",
                        str(fixture.tasks_path),
                        "--package",
                        "WP1",
                        *fixture.binding_cli_args(),
                    )
                    self.assertNotEqual(0, emit.returncode, emit.stdout + emit.stderr)
                    self.assertEqual("", emit.stdout)
                    self.assertIn(
                        "State Binding Assigned Slice path must not contain",
                        "\n".join(json.loads(emit.stderr)["errors"]),
                    )
                finally:
                    fixture.cleanup()

    def test_two_tier_gate_emits_context_advisories_and_blocks_must_satisfy_drift(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        self.fixture.report_path.write_text(self.fixture.report_text(proof), encoding="utf-8")
        self.fixture.slice_path.write_text(
            self.fixture.slice_path.read_text(encoding="utf-8").replace(
                "Context-only IDs must be readable but do not create required proof rows.",
                "Context-only IDs changed but do not create required proof rows.",
                1,
            ),
            encoding="utf-8",
        )

        context_result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")

        self.assertEqual(0, context_result.returncode, context_result.stdout + context_result.stderr)
        advisories = json.loads(context_result.stdout)["advisories"]
        self.assertEqual(1, len(advisories))
        self.assertEqual(
            {
                "type": "context_only_slice_drift",
                "severity": "advisory",
                "package": "WP1",
                "slice_path": ".planning/fixture/slices/helper.md",
                "tier": "context_only",
                "h3_ids": ["HELPER-CONTEXT-003"],
            },
            {key: advisories[0][key] for key in ("type", "severity", "package", "slice_path", "tier", "h3_ids")},
        )

        fixture = SliceproofFixture()
        try:
            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(fixture.report_text(proof), encoding="utf-8")
            fixture.slice_path.write_text(
                fixture.slice_path.read_text(encoding="utf-8").replace(
                    "The helper validates paths, required package sections, dependencies, and H3 IDs.",
                    "The helper validates changed paths, required package sections, dependencies, and H3 IDs.",
                    1,
                ),
                encoding="utf-8",
            )

            must_result = fixture.run("validate-package-complete", str(fixture.tasks_path), "--package", "WP1")

            self.assertNotEqual(0, must_result.returncode, must_result.stdout + must_result.stderr)
            must_payload = json.loads(must_result.stderr)
            self.assertIn("must_satisfy Slice section drift for HELPER-PLAN-001", "\n".join(must_payload["errors"]))
            self.assertEqual([], must_payload["advisories"])
        finally:
            fixture.cleanup()

        fixture = SliceproofFixture()
        try:
            proof = fixture.completed_proof()
            fixture.proof_path.write_text(proof, encoding="utf-8")
            fixture.report_path.write_text(fixture.report_text(proof), encoding="utf-8")
            changed = fixture.slice_path.read_text(encoding="utf-8").replace(
                "The helper validates paths, required package sections, dependencies, and H3 IDs.",
                "The helper validates changed paths, required package sections, dependencies, and H3 IDs.",
                1,
            ).replace(
                "Context-only IDs must be readable but do not create required proof rows.",
                "Context-only IDs changed but do not create required proof rows.",
                1,
            )
            fixture.slice_path.write_text(changed, encoding="utf-8")

            mixed_result = fixture.run("validate-package-complete", str(fixture.tasks_path), "--package", "WP1")

            self.assertNotEqual(0, mixed_result.returncode, mixed_result.stdout + mixed_result.stderr)
            mixed_payload = json.loads(mixed_result.stderr)
            self.assertIn("must_satisfy Slice section drift for HELPER-PLAN-001", "\n".join(mixed_payload["errors"]))
            self.assertEqual(["HELPER-CONTEXT-003"], mixed_payload["advisories"][0]["h3_ids"])
        finally:
            fixture.cleanup()

    def test_validate_final_aggregates_context_only_advisories_across_packages(self) -> None:
        self.fixture.write_completed_proof_and_report()
        self.fixture.write_simple_package_artifacts("WP2", must_ids=["HELPER-PIPE-004"], context_ids=["HELPER-INTERFACE-005"])
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        plan["work_packages"].append(
            {
                "id": "WP2",
                "path": ".tasks/fixture/packages/WP2.md",
                "proof_path": ".tasks/fixture/proofs/WP2.proof.md",
                "report_path": ".tasks/fixture/reports/WP2.package-verification.md",
                "verification_mode": "boundary",
                "status": "pending",
                "depends_on": [],
            }
        )
        self.fixture.write_plan(plan)
        changed = self.fixture.slice_path.read_text(encoding="utf-8").replace(
            "Context-only IDs must be readable but do not create required proof rows.",
            "Context-only IDs changed but do not create required proof rows.",
            1,
        ).replace(
            "Must exist: a stable fixture command interface.",
            "Must exist: a changed fixture command interface.",
            1,
        )
        self.fixture.slice_path.write_text(changed, encoding="utf-8")

        failed = self.fixture.run("validate-final", str(self.fixture.tasks_path))

        self.assertNotEqual(0, failed.returncode, failed.stdout + failed.stderr)
        failed_payload = json.loads(failed.stderr)
        self.assertIn("work_packages[WP2].status: expected 'done'", "\n".join(failed_payload["errors"]))
        self.assertEqual(
            [("WP1", ["HELPER-CONTEXT-003"]), ("WP2", ["HELPER-INTERFACE-005"])],
            sorted((advisory["package"], advisory["h3_ids"]) for advisory in failed_payload["advisories"]),
        )

        plan["work_packages"][1]["status"] = "done"
        self.fixture.write_plan(plan)
        result = self.fixture.run("validate-final", str(self.fixture.tasks_path))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        advisories = json.loads(result.stdout)["advisories"]
        self.assertEqual(
            [("WP1", ["HELPER-CONTEXT-003"]), ("WP2", ["HELPER-INTERFACE-005"])],
            sorted((advisory["package"], advisory["h3_ids"]) for advisory in advisories),
        )

    def test_assigned_slice_digest_grammar_failures_are_hard_errors_before_drift_classification(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        valid_report = self.fixture.report_text(proof)
        valid_value = self.fixture.assigned_slice_digests()
        entries = valid_value.split("; ")

        cases = [
            ("missing", "; ".join(entries[1:]), "missing entry"),
            ("extra unknown H3", valid_value + "; .planning/fixture/slices/helper.md|must_satisfy|HELPER-PIPE-004=sha256:" + "0" * 64, "unknown H3"),
            ("duplicate", valid_value + "; " + entries[0], "duplicate entry"),
            ("malformed", "not-an-entry", "malformed entry"),
            ("unknown path", valid_value.replace(".planning/fixture/slices/helper.md", ".planning/fixture/slices/other.md", 1), "unknown path"),
            ("invalid tier", valid_value.replace("must_satisfy", "optional", 1), "invalid tier"),
            ("invalid digest", re.sub(r"sha256:[0-9a-f]{64}", "sha256:not-a-digest", valid_value, count=1), "invalid digest"),
            ("encoded tier mismatch", entries[0].replace("must_satisfy", "context_only", 1) + "; " + "; ".join(entries[1:]), "encoded tier mismatch"),
            ("unsorted", "; ".join(reversed(entries)), "entries must be sorted"),
        ]
        for name, digest_value, expected_error in cases:
            with self.subTest(name=name):
                self.fixture.report_path.write_text(
                    valid_report.replace(f"- Assigned Slice Digests: `{valid_value}`", f"- Assigned Slice Digests: `{digest_value}`"),
                    encoding="utf-8",
                )
                result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                payload = json.loads(result.stderr)
                self.assertIn(expected_error, "\n".join(payload["errors"]))
                self.assertEqual([], payload["advisories"])

    def test_emit_state_binding_round_trips_through_shared_formatter_and_parser(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        runtime_rel = ".tasks/fixture/runtime/WP1.txt"
        runtime_path = self.fixture.artifact_root / runtime_rel
        runtime_path.parent.mkdir(parents=True)
        runtime_path.write_text("focused command observed pass\n", encoding="utf-8")
        runtime_digest = SLICEPROOF.digest_bytes(runtime_path.read_bytes())
        contract_digest = "sha256:" + "6" * 64
        emit = self.fixture.run(
            "emit-state-binding",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            *self.fixture.binding_cli_args(
                runtime_evidence=f"{runtime_rel}={runtime_digest}",
                consumed_contract=f"helper-api={contract_digest}",
            ),
        )

        self.assertEqual(0, emit.returncode, emit.stdout + emit.stderr)
        expected_block = SLICEPROOF.render_state_binding_block(
            SLICEPROOF.state_binding_values(
                self.fixture.artifact_root,
                self.fixture.registry_package(),
                self.fixture.package_markdown(),
                self.fixture.proof_path,
                candidate=self.fixture.candidate_binding(
                    runtime_evidence_digests=((runtime_rel, runtime_digest),),
                    consumed_contract_digests=(("helper-api", contract_digest),),
                ),
                worktree=str(self.fixture.repo.resolve(strict=False)),
                git_ref="wp/fixture/WP1",
                verified_at="2026-06-04T00:00:00Z",
            )
        )
        self.assertEqual(expected_block, emit.stdout)
        parsed = SLICEPROOF.parse_key_values(emit.stdout)
        digest_value = SLICEPROOF.clean_cell_id(parsed["Assigned Slice Digests"])
        self.assertRegex(
            digest_value,
            r"^\.planning/fixture/slices/helper\.md\|must_satisfy\|HELPER-PLAN-001=sha256:[0-9a-f]{64}; "
            r"\.planning/fixture/slices/helper\.md\|must_satisfy\|HELPER-PROOF-002=sha256:[0-9a-f]{64}; "
            r"\.planning/fixture/slices/helper\.md\|context_only\|HELPER-CONTEXT-003=sha256:[0-9a-f]{64}$",
        )
        self.assertNotIn("\n", digest_value)
        self.assertEqual(
            f"{REPORT_AUTHORIZATION_ID} | {REPORT_EFFECTIVE_DIGEST}",
            SLICEPROOF.clean_cell_id(parsed["Authorization / Effective Digest"]),
        )
        self.assertEqual("standard | boundary", SLICEPROOF.clean_cell_id(parsed["Assurance Profile / Verification Mode"]))
        self.assertEqual(
            f"{self.fixture.report_commit} | {self.fixture.report_tree}",
            SLICEPROOF.clean_cell_id(parsed["Commit / Tree"]),
        )
        self.assertEqual(
            f"{self.fixture.report_base} | {self.fixture.report_diff_digest}",
            SLICEPROOF.clean_cell_id(parsed["Base / Diff Identity"]),
        )
        self.assertEqual(f"{runtime_rel}={runtime_digest}", SLICEPROOF.clean_cell_id(parsed["Runtime Evidence Digests"]))
        self.assertEqual(
            f"helper-api={contract_digest}",
            SLICEPROOF.clean_cell_id(parsed["Consumed Contract Digests"]),
        )

        report_without_binding = self.fixture.report_text(proof).split("## State Binding", 1)[0]
        self.fixture.report_path.write_text(report_without_binding + emit.stdout, encoding="utf-8")
        package_result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, package_result.returncode, package_result.stdout + package_result.stderr)
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        final_result = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, final_result.returncode, final_result.stdout + final_result.stderr)

        runtime_path.write_text("stale runtime evidence\n", encoding="utf-8")
        stale_runtime = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertNotEqual(0, stale_runtime.returncode, stale_runtime.stdout + stale_runtime.stderr)
        self.assertIn(
            "digest does not match current runtime evidence file",
            "\n".join(json.loads(stale_runtime.stderr)["errors"]),
        )

        bad_values = {
            str(self.fixture.repo.resolve(strict=False)): "relative/worktree",
            "wp/fixture/WP1": "todo",
            self.fixture.report_commit: "bad",
            "2026-06-04T00:00:00Z": "not-a-date",
        }
        bad = self.fixture.run(
            "emit-state-binding",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            *[bad_values.get(value, value) for value in self.fixture.binding_cli_args()],
        )
        self.assertNotEqual(0, bad.returncode, bad.stdout + bad.stderr)
        bad_errors = "\n".join(json.loads(bad.stderr)["errors"])
        self.assertIn("--worktree must be an absolute reviewed worktree path", bad_errors)
        self.assertIn("--git-ref must be a safe non-placeholder reviewed ref", bad_errors)
        self.assertIn("Commit must be an exact lowercase", bad_errors)
        self.assertIn("--verified-at: expected timezone-aware ISO-8601", bad_errors)

    def test_candidate_git_identity_rejects_well_shaped_non_reproducible_bindings(self) -> None:
        base_tree = self.fixture.git_checked("rev-parse", f"{self.fixture.report_base}^{{tree}}")
        self.fixture.git_checked("update-ref", "refs/heads/wp/fixture/base", self.fixture.report_base)
        reverse_diff = SLICEPROOF.raw_git_diff_identity(
            self.fixture.repo,
            self.fixture.report_commit,
            self.fixture.report_base,
            "reverse fixture diff",
        )
        nested = self.fixture.feature_dir.resolve(strict=False)
        cases = [
            (
                "well-shaped nonexistent commit",
                {"commit": "0" * 40},
                "local git inspection failed",
            ),
            (
                "wrong commit tree",
                {"tree": base_tree},
                "Tree must equal the exact candidate commit tree",
            ),
            (
                "non-ancestor base",
                {
                    "commit": self.fixture.report_base,
                    "tree": base_tree,
                    "base_commit": self.fixture.report_commit,
                    "diff_digest": reverse_diff,
                    "git_ref": "wp/fixture/base",
                },
                "Base commit must be an ancestor",
            ),
            (
                "ref resolves elsewhere",
                {"git_ref": "wp/fixture/base"},
                "Git Ref must resolve to the exact candidate commit",
            ),
            (
                "nested checkout path",
                {"worktree": str(nested)},
                "Worktree must be an existing exact Git worktree root",
            ),
            (
                "well-shaped invented diff",
                {"diff_digest": "sha256:" + "0" * 64},
                "canonical raw no-renames Git diff identity",
            ),
        ]
        for name, overrides, expected in cases:
            with self.subTest(name=name):
                result = self.fixture.run(
                    "emit-state-binding",
                    str(self.fixture.tasks_path),
                    "--package",
                    "WP1",
                    *self.fixture.binding_cli_args(**overrides),
                )
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected, "\n".join(json.loads(result.stderr)["errors"]))

        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        report = self.fixture.report_text(proof).replace(
            self.fixture.report_diff_digest,
            "sha256:" + "0" * 64,
            1,
        )
        self.fixture.report_path.write_text(report, encoding="utf-8")
        rejected_report = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertNotEqual(0, rejected_report.returncode, rejected_report.stdout + rejected_report.stderr)
        self.assertIn(
            "canonical raw no-renames Git diff identity",
            "\n".join(json.loads(rejected_report.stderr)["errors"]),
        )

    def test_incident_shape_changed_owner_sections_do_not_invalidate_other_packages(self) -> None:
        self.fixture.write_completed_proof_and_report()
        self.fixture.write_simple_package_artifacts("WP2", must_ids=["HELPER-PROOF-002"])
        self.fixture.write_simple_package_artifacts("WP3", must_ids=["HELPER-CONTEXT-003"])
        plan = self.fixture.plan()
        plan["work_packages"].extend(
            [
                {
                    "id": "WP2",
                    "path": ".tasks/fixture/packages/WP2.md",
                    "proof_path": ".tasks/fixture/proofs/WP2.proof.md",
                    "report_path": ".tasks/fixture/reports/WP2.package-verification.md",
                    "verification_mode": "boundary",
                    "status": "pending",
                    "depends_on": [],
                },
                {
                    "id": "WP3",
                    "path": ".tasks/fixture/packages/WP3.md",
                    "proof_path": ".tasks/fixture/proofs/WP3.proof.md",
                    "report_path": ".tasks/fixture/reports/WP3.package-verification.md",
                    "verification_mode": "boundary",
                    "status": "pending",
                    "depends_on": [],
                },
            ]
        )
        self.fixture.write_plan(plan)
        changed = self.fixture.slice_path.read_text(encoding="utf-8").replace(
            "The helper validates paths, required package sections, dependencies, and H3 IDs.",
            "The helper validates changed paths, required package sections, dependencies, and H3 IDs.",
            1,
        ).replace(
            "The helper creates placeholders and checks completion markers without semantic scoring.",
            "The helper creates changed placeholders and checks completion markers without semantic scoring.",
            1,
        )
        self.fixture.slice_path.write_text(changed, encoding="utf-8")

        wp1 = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        wp2 = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP2")
        wp3 = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP3")

        self.assertNotEqual(0, wp1.returncode, wp1.stdout + wp1.stderr)
        self.assertIn("must_satisfy Slice section drift for HELPER-PLAN-001", "\n".join(json.loads(wp1.stderr)["errors"]))
        self.assertNotEqual(0, wp2.returncode, wp2.stdout + wp2.stderr)
        self.assertIn("must_satisfy Slice section drift for HELPER-PROOF-002", "\n".join(json.loads(wp2.stderr)["errors"]))
        self.assertEqual(0, wp3.returncode, wp3.stdout + wp3.stderr)
        self.assertEqual([], json.loads(wp3.stdout)["advisories"])

    def test_validate_package_complete_requires_local_git_candidate_inspection(self) -> None:
        self.fixture.write_completed_proof_and_report()
        fake_bin = self.fixture.repo / "fake-bin"
        fake_bin.mkdir()
        marker = self.fixture.repo / "git-was-called"
        fake_git = fake_bin / "git"
        fake_git.write_text(
            "#!/bin/sh\n"
            "echo invoked > \"$SLICEPROOF_FAKE_GIT_MARKER\"\n"
            "exit 99\n",
            encoding="utf-8",
        )
        fake_git.chmod(0o700)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
        env["SLICEPROOF_FAKE_GIT_MARKER"] = str(marker)

        result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1", env=env)

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("local git inspection failed", "\n".join(json.loads(result.stderr)["errors"]))
        self.assertTrue(marker.exists(), "validate-package-complete did not inspect the bound Git candidate")

        unknown = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP9")
        self.assertNotEqual(0, unknown.returncode)
        self.assertIn("unknown package id WP9", "\n".join(json.loads(unknown.stderr)["errors"]))

    def test_b2_adh10_dependent_unlock_requires_boundary_receipt_and_contract_digest(self) -> None:
        self.fixture.write_completed_proof_and_report()
        self.fixture.write_simple_package_artifacts(
            "WP2",
            must_ids=["HELPER-PIPE-004"],
            verification_mode="final",
            depends_on=["WP1"],
        )
        plan = self.fixture.plan()
        plan["work_packages"].append({
            "id": "WP2",
            "path": ".tasks/fixture/packages/WP2.md",
            "proof_path": ".tasks/fixture/proofs/WP2.proof.md",
            "report_path": None,
            "verification_mode": "final",
            "status": "pending",
            "depends_on": ["WP1"],
        })
        self.fixture.write_plan(plan)

        missing_contract = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertNotEqual(0, missing_contract.returncode, missing_contract.stdout + missing_contract.stderr)
        self.assertIn(
            "requires at least one consumed-contract digest",
            "\n".join(json.loads(missing_contract.stderr)["errors"]),
        )

        contract_digest = ("helper-contract", "sha256:" + "5" * 64)
        proof = self.fixture.proof_path.read_text(encoding="utf-8")
        self.fixture.report_path.write_text(
            self.fixture.report_text(
                proof,
                consumed_contract_digests=(contract_digest,),
            ),
            encoding="utf-8",
        )
        unlocked = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertEqual(0, unlocked.returncode, unlocked.stdout + unlocked.stderr)
        self.assertTrue(json.loads(unlocked.stdout)["boundary_receipt_validated"])

        plan["work_packages"][0].update({"verification_mode": "final", "report_path": None})
        self.fixture.write_plan(plan)
        self.fixture.package_path.write_text(
            self.fixture.package_text(verification_mode="final", report_path=None),
            encoding="utf-8",
        )
        rejected_route = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertNotEqual(0, rejected_route.returncode, rejected_route.stdout + rejected_route.stderr)
        self.assertIn(
            "dependent producers must use boundary mode",
            "\n".join(json.loads(rejected_route.stderr)["errors"]),
        )

    def test_b2_adh02_standard_mixed_package_equation_is_pre_freeze_only(self) -> None:
        self.fixture.proof_path.write_text(self.fixture.completed_proof(), encoding="utf-8")
        self.fixture.write_simple_package_artifacts(
            "WP2",
            must_ids=["HELPER-PIPE-004"],
            verification_mode="final",
            depends_on=["WP1"],
        )
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        plan["work_packages"].append({
            "id": "WP2",
            "path": ".tasks/fixture/packages/WP2.md",
            "proof_path": ".tasks/fixture/proofs/WP2.proof.md",
            "report_path": None,
            "verification_mode": "final",
            "status": "done",
            "depends_on": ["WP1"],
        })
        self.fixture.write_plan(plan)
        self.fixture.report_path.write_text(
            self.fixture.report_text(
                consumed_contract_digests=(("helper-contract", "sha256:" + "5" * 64),),
            ),
            encoding="utf-8",
        )

        result = self.fixture.run("validate-final", str(self.fixture.tasks_path))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual([".tasks/fixture/reports/WP1.package-verification.md"], payload["boundary_reports_validated"])
        self.assertEqual(["WP2"], payload["final_deferrals_validated"])
        self.assertTrue(payload["pre_freeze_package_equation_validated"])
        self.assertFalse(payload["post_freeze_assurance_validated"])

    def test_b2_adh19_low_final_deferral_has_no_substitute_report_or_fake_assurance(self) -> None:
        self.fixture.proof_path.write_text(self.fixture.completed_proof(), encoding="utf-8")
        self.fixture.configure_primary_final(
            assurance_profile="low",
            status="done",
            rationale=(
                "Owner: Combined Low Verifier; semantic verification is deferred to final assurance for this coherent leaf."
            ),
        )

        package_result = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertEqual(0, package_result.returncode, package_result.stdout + package_result.stderr)
        package_payload = json.loads(package_result.stdout)
        self.assertTrue(package_payload["direct_final_deferral_validated"])
        self.assertFalse(package_payload["boundary_receipt_validated"])
        self.assertFalse(package_payload["post_freeze_assurance_validated"])

        final_result = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, final_result.returncode, final_result.stdout + final_result.stderr)
        final_payload = json.loads(final_result.stdout)
        self.assertEqual([], final_payload["boundary_reports_validated"])
        self.assertEqual(["WP1"], final_payload["final_deferrals_validated"])
        self.assertFalse(final_payload["post_freeze_assurance_validated"])

        substitute_binding = self.fixture.run(
            "emit-state-binding",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            *self.fixture.binding_cli_args(
                assurance_profile="low",
                verification_mode="final",
            ),
        )
        self.assertNotEqual(0, substitute_binding.returncode, substitute_binding.stdout + substitute_binding.stderr)
        self.assertIn(
            "final packages have no package report",
            "\n".join(json.loads(substitute_binding.stderr)["errors"]),
        )

        self.fixture.report_path.write_text("substitute receipt\n", encoding="utf-8")
        substitute = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertNotEqual(0, substitute.returncode, substitute.stdout + substitute.stderr)
        self.assertIn("fabricated or substitute report", "\n".join(json.loads(substitute.stderr)["errors"]))

    def test_b2_final_rationale_and_high_profile_lens_fail_closed(self) -> None:
        cases = [
            (
                "missing owner and deferral",
                "Coherent final leaf.",
                "must explicitly defer semantic verification",
            ),
            (
                "high lens missing",
                "Owner: Security Specialist; semantic verification is deferred to final assurance.",
                "must name the high-risk final-assurance lens",
            ),
        ]
        for name, rationale, expected in cases:
            with self.subTest(name=name):
                self.fixture.configure_primary_final(
                    assurance_profile="high" if name == "high lens missing" else "standard",
                    rationale=rationale,
                )
                rejected = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
                self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                self.assertIn(expected, "\n".join(json.loads(rejected.stderr)["errors"]))

        self.fixture.configure_primary_final(
            assurance_profile="high",
            rationale=(
                "Owner: Security Specialist; semantic verification is deferred to final assurance; "
                "lens: shared-state security."
            ),
        )
        accepted = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

    def _package_and_final_commands(self) -> list[tuple[str, tuple[str, ...]]]:
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        return [
            (
                "package-complete",
                ("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1"),
            ),
            ("final", ("validate-final", str(self.fixture.tasks_path))),
        ]

    def test_b2_adh22_selected_causal_evidence_compact_grammar(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        commands = self._package_and_final_commands()
        valid = self.fixture.selected_causal_evidence(
            behavior_risk=(
                "One selected CLI test proves required registry routing and malformed-input rejection together."
            ),
            causal_sufficiency=(
                "It invokes the production parser and its assertions fail for either missing or substituted routing."
            ),
            substitutes="Temporary artifact/code roots; no mocked helper process.",
        )
        for command_name, command in commands:
            with self.subTest(command=command_name):
                self.fixture.report_path.write_text(
                    self.fixture.report_text(proof, selected_causal_evidence=valid),
                    encoding="utf-8",
                )
                accepted = self.fixture.run(*command)
                self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

        lines = valid.splitlines()
        malformed = [
            (
                "wrong columns",
                valid.replace("Behavior / Risk Proven", "Wrong Evidence Column", 1),
                "columns must be exactly",
            ),
            (
                "no row",
                "\n".join(lines[:2]),
                "must include at least one evidence row",
            ),
            (
                "unsafe selected anchor",
                self.fixture.selected_causal_evidence(
                    evidence_anchor="test:../escape.py::test_escape"
                ),
                "path must not contain",
            ),
            (
                "unknown selected evidence type",
                self.fixture.selected_causal_evidence(evidence_type="screenshot"),
                "Evidence Type 'screenshot' is not supported",
            ),
            (
                "placeholder rationale",
                self.fixture.selected_causal_evidence(causal_sufficiency="TODO"),
                "must be a specific non-placeholder value",
            ),
            (
                "undisclosed substitutes",
                self.fixture.selected_causal_evidence(substitutes="N/A"),
                "Substitutes / Fixtures must be a specific non-placeholder value",
            ),
            (
                "failed command result",
                self.fixture.selected_causal_evidence(
                    command_result=(
                        "`command:proof#Commands Run:fixture subset` — FAIL, focused helper fixture failed."
                    )
                ),
                "Fresh Command Result must use",
            ),
            (
                "missing observed result",
                self.fixture.selected_causal_evidence(
                    command_result="`command:proof#Commands Run:fixture subset` — PASS"
                ),
                "Fresh Command Result must use",
            ),
            (
                "prose outside table",
                valid + "\nextra report prose",
                "exactly one contiguous Markdown table",
            ),
        ]
        for case_name, evidence, expected in malformed:
            with self.subTest(case=case_name):
                self.fixture.report_path.write_text(
                    self.fixture.report_text(proof, selected_causal_evidence=evidence),
                    encoding="utf-8",
                )
                rejected = self.fixture.run(
                    "validate-package-complete",
                    str(self.fixture.tasks_path),
                    "--package",
                    "WP1",
                )
                self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
                self.assertIn(expected, "\n".join(json.loads(rejected.stderr)["errors"]))

    def test_b2_adh22_obsolete_report_section_cannot_substitute_for_selected_evidence(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        report = remove_h3_section(self.fixture.report_text(proof), "Selected Causal Evidence")
        report = report.replace(
            "### Slice Closure Review",
            "### Test Review Scope\n- Obsolete substitute receipt.\n\n"
            "### Slice Closure Review",
            1,
        )
        self.fixture.report_path.write_text(report, encoding="utf-8")

        rejected = self.fixture.run(
            "validate-package-complete",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )

        self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
        errors = "\n".join(json.loads(rejected.stderr)["errors"])
        self.assertIn("missing required source section ### Selected Causal Evidence", errors)
        self.assertIn("obsolete ### Test Review Scope receipt is not supported", errors)

    def test_validate_package_complete_rejects_dirty_or_stale_matrices(self) -> None:
        first_matrix_row = (
            "| HELPER-PLAN-001 | slice | Registry and package references validate mechanically. | mixed | "
            "static:plugins/super-developer/assets/sliceproof.py#validate_plan; "
            "test:plugins/super-developer/assets/tests/test_sliceproof.py::test_validate_plan_accepts_valid_registry_package_slice_fixture | "
            "no interface; fixture plan behavior covered | delivered |"
        )
        second_slice_row = (
            "| HELPER-PROOF-002 | slice | Proof placeholders and proof closure validate mechanically. | static | "
            "static:plugins/super-developer/assets/sliceproof.py#validate_proof | no interface; fixture proof behavior covered | delivered |"
        )
        ve2_row = (
            "| VE-2 | verification-expectation | `sliceproof.py validate-proof` fails placeholders and passes completed proof. | static | "
            "static:plugins/super-developer/assets/sliceproof.py#validate_proof | expectation covered; no interface | delivered |"
        )
        cases = [
            (
                "old report shape without matrix",
                lambda fixture, report: remove_h3_section(report, "Deliverable Completeness Matrix"),
                "missing required source section ### Deliverable Completeness Matrix",
            ),
            (
                "missing H3 row",
                lambda fixture, report: report.replace("\n" + second_slice_row, "", 1),
                "missing required slice row for HELPER-PROOF-002",
            ),
            (
                "missing VE row",
                lambda fixture, report: report.replace("\n" + ve2_row, "", 1),
                "missing required verification-expectation row for VE-2",
            ),
            (
                "duplicate rows",
                lambda fixture, report: report.replace(first_matrix_row, first_matrix_row + "\n" + first_matrix_row, 1),
                "duplicate Deliverable Completeness Matrix row for HELPER-PLAN-001",
            ),
            (
                "dirty verdict",
                lambda fixture, report: report.replace("| delivered |", "| partial |", 1),
                "Verdict must be delivered for package completion",
            ),
            (
                "unsupported verdict",
                lambda fixture, report: report.replace("| delivered |", "| complete |", 1),
                "Verdict 'complete' is not supported",
            ),
            (
                "unsupported evidence type",
                lambda fixture, report: report.replace("| mixed |", "| screenshot |", 1),
                "Evidence Type 'screenshot' is not supported",
            ),
            (
                "placeholder evidence refs",
                lambda fixture, report: report.replace(
                    "static:plugins/super-developer/assets/sliceproof.py#validate_plan; test:plugins/super-developer/assets/tests/test_sliceproof.py::test_validate_plan_accepts_valid_registry_package_slice_fixture",
                    "TODO",
                    1,
                ),
                "Evidence Refs must be non-placeholder",
            ),
            (
                "nonexistent evidence path",
                lambda fixture, report: report.replace("plugins/super-developer/assets/sliceproof.py#validate_plan", "plugins/super-developer/assets/missing.py#validate_plan", 1),
                "file not found",
            ),
            (
                "unsafe evidence path",
                lambda fixture, report: report.replace("plugins/super-developer/assets/sliceproof.py#validate_plan", "../escape.py#validate_plan", 1),
                "path must not contain",
            ),
            (
                "vague evidence ref",
                lambda fixture, report: report.replace("static:plugins/super-developer/assets/sliceproof.py#validate_plan", "static:plugins/super-developer/assets/sliceproof.py", 1),
                "static evidence ref must include a concrete anchor",
            ),
            (
                "command ref not tied to proof",
                lambda fixture, report: report.replace(
                    first_matrix_row,
                    "| HELPER-PLAN-001 | slice | Registry and package references validate mechanically. | command | command:proof#Commands Run:not-run | no interface; fixture plan behavior covered | delivered |",
                    1,
                ),
                "command proof label 'not-run' was not found in proof ## Commands Run",
            ),
            (
                "manual ref missing observed field",
                lambda fixture, report: report.replace(
                    first_matrix_row,
                    "| HELPER-PLAN-001 | slice | Registry and package references validate mechanically. | manual | manual:scenario=operator checked fixture | no interface; fixture plan behavior covered | delivered |",
                    1,
                ),
                "manual evidence must include non-placeholder observed=...",
            ),
            (
                "stale package digest",
                lambda fixture, report: (fixture.package_path.write_text(fixture.package_path.read_text(encoding="utf-8") + "\n<!-- stale -->\n", encoding="utf-8"), report)[1],
                "Package Markdown Digest does not match current package Markdown content",
            ),
            (
                "must-satisfy section drift",
                lambda fixture, report: (
                    fixture.slice_path.write_text(
                        fixture.slice_path.read_text(encoding="utf-8").replace(
                            "The helper validates paths, required package sections, dependencies, and H3 IDs.",
                            "The helper validates paths, required package sections, dependencies, H3 IDs, and changed text.",
                            1,
                        ),
                        encoding="utf-8",
                    ),
                    report,
                )[1],
                "must_satisfy Slice section drift for HELPER-PLAN-001",
            ),
            (
                "triggered risk without rationale",
                lambda fixture, report: report.replace(
                    "| VE-1 |",
                    "| RISK-fixture | triggered-risk | Fixture risk checked. | static | static:plugins/super-developer/assets/sliceproof.py#validate_plan | checked | delivered |\n| VE-1 |",
                    1,
                ),
                "triggered-risk row must record rationale/disposition",
            ),
            (
                "triggered risk with bare triggered",
                lambda fixture, report: report.replace(
                    "| VE-1 |",
                    "| RISK-fixture | triggered-risk | Fixture risk checked. | static | static:plugins/super-developer/assets/sliceproof.py#validate_plan | triggered | delivered |\n| VE-1 |",
                    1,
                ),
                "triggered-risk row must record rationale/disposition",
            ),
            (
                "triggered risk with bare because",
                lambda fixture, report: report.replace(
                    "| VE-1 |",
                    "| RISK-fixture | triggered-risk | Fixture risk checked. | static | static:plugins/super-developer/assets/sliceproof.py#validate_plan | because | delivered |\n| VE-1 |",
                    1,
                ),
                "triggered-risk row must record rationale/disposition",
            ),
        ]
        for name, mutate, expected_error in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    proof = fixture.completed_proof()
                    fixture.proof_path.write_text(proof, encoding="utf-8")
                    report = fixture.report_text(proof)
                    fixture.report_path.write_text(mutate(fixture, report), encoding="utf-8")
                    result = fixture.run("validate-package-complete", str(fixture.tasks_path), "--package", "WP1")
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

    def test_validate_package_complete_does_not_trust_report_worktree_for_matrix_file_evidence(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        fake_paths = [
            ("outside-only/code.py", "def fake():\n    pass\n"),
            ("outside-only/test_fake.py", "def test_fake():\n    pass\n"),
            ("outside-only/evidence.md", "## fake-anchor\n"),
        ]
        for relative_path, content in fake_paths:
            target = self.fixture.external_worktree / relative_path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        fake_refs = (
            "code:outside-only/code.py#fake; "
            "test:outside-only/test_fake.py::test_fake; "
            "static:outside-only/evidence.md#fake-anchor"
        )
        matrix = self.fixture.deliverable_matrix().replace(
            "static:plugins/super-developer/assets/sliceproof.py#validate_plan; "
            "test:plugins/super-developer/assets/tests/test_sliceproof.py::test_validate_plan_accepts_valid_registry_package_slice_fixture",
            fake_refs,
            1,
        )
        report = self.fixture.report_text(proof, deliverable_matrix=matrix, worktree=str(self.fixture.external_worktree))
        self.fixture.report_path.write_text(report, encoding="utf-8")

        result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        errors = "\n".join(json.loads(result.stderr)["errors"])
        self.assertIn("code evidence path: file not found: outside-only/code.py", errors)

    def test_validate_package_complete_verifies_verification_output_labels(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        output_rel = ".tasks/fixture/verification-output/WP1.md"
        output_path = self.fixture.feature_dir / "verification-output" / "WP1.md"
        output_path.parent.mkdir(parents=True)
        output_path.write_text("# Durable verifier output\n\n## existing-label\nObserved command output.\n", encoding="utf-8")
        matrix = self.fixture.deliverable_matrix().replace(
            "| HELPER-PLAN-001 | slice | Registry and package references validate mechanically. | mixed | "
            "static:plugins/super-developer/assets/sliceproof.py#validate_plan; "
            "test:plugins/super-developer/assets/tests/test_sliceproof.py::test_validate_plan_accepts_valid_registry_package_slice_fixture |",
            "| HELPER-PLAN-001 | slice | Registry and package references validate mechanically. | command | "
            f"command:verification-output:{output_rel}#existing-label |",
            1,
        )
        self.fixture.report_path.write_text(self.fixture.report_text(proof, deliverable_matrix=matrix), encoding="utf-8")

        accepted = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")

        self.assertEqual(0, accepted.returncode, accepted.stdout + accepted.stderr)

        rejected_matrix = matrix.replace("#existing-label", "#not-a-real-label", 1)
        self.fixture.report_path.write_text(self.fixture.report_text(proof, deliverable_matrix=rejected_matrix), encoding="utf-8")

        rejected = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")

        self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
        errors = "\n".join(json.loads(rejected.stderr)["errors"])
        self.assertIn("verification-output label 'not-a-real-label' was not found", errors)

    def test_validate_package_complete_rejects_interface_rows_without_exactness(self) -> None:
        self.fixture.package_path.write_text(self.fixture.package_text(must_id="HELPER-INTERFACE-005"), encoding="utf-8")
        proof = self.fixture.completed_proof().replace("HELPER-PLAN-001", "HELPER-INTERFACE-005")
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        matrix = self.fixture.deliverable_matrix().replace("HELPER-PLAN-001", "HELPER-INTERFACE-005").replace(
            "no interface; fixture plan behavior covered",
            "interface checked",
            1,
        )
        report = self.fixture.report_text(proof, deliverable_matrix=matrix).replace("HELPER-PLAN-001", "HELPER-INTERFACE-005")
        self.fixture.report_path.write_text(report, encoding="utf-8")

        result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        errors = "\n".join(json.loads(result.stderr)["errors"])
        self.assertIn("interface row must record exact interface fulfillment", errors)
        self.assertIn("interface row must record forbidden-behavior falsification", errors)

        negated_matrix = self.fixture.deliverable_matrix().replace("HELPER-PLAN-001", "HELPER-INTERFACE-005").replace(
            "no interface; fixture plan behavior covered",
            "interface: exact; forbidden behavior not falsified",
            1,
        )
        negated_report = self.fixture.report_text(proof, deliverable_matrix=negated_matrix).replace(
            "HELPER-PLAN-001",
            "HELPER-INTERFACE-005",
        )
        self.fixture.report_path.write_text(negated_report, encoding="utf-8")

        negated = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")

        self.assertNotEqual(0, negated.returncode, negated.stdout + negated.stderr)
        negated_errors = "\n".join(json.loads(negated.stderr)["errors"])
        self.assertIn("interface row must not negate forbidden-behavior falsification", negated_errors)

        for disposition in (
            "interface: not exact; forbidden behavior falsified",
            "interface: inexact; forbidden behavior falsified",
        ):
            with self.subTest(disposition=disposition):
                inexact_matrix = self.fixture.deliverable_matrix().replace("HELPER-PLAN-001", "HELPER-INTERFACE-005").replace(
                    "no interface; fixture plan behavior covered",
                    disposition,
                    1,
                )
                inexact_report = self.fixture.report_text(proof, deliverable_matrix=inexact_matrix).replace(
                    "HELPER-PLAN-001",
                    "HELPER-INTERFACE-005",
                )
                self.fixture.report_path.write_text(inexact_report, encoding="utf-8")

                inexact = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")

                self.assertNotEqual(0, inexact.returncode, inexact.stdout + inexact.stderr)
                inexact_errors = "\n".join(json.loads(inexact.stderr)["errors"])
                self.assertIn("interface row contains non-exact interface disposition", inexact_errors)

    def test_validate_final_reuses_deliverable_matrix_validation(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        valid_report = self.fixture.report_text(proof)
        final_cases = [
            ("old shape", remove_h3_section(valid_report, "Deliverable Completeness Matrix"), "missing required source section ### Deliverable Completeness Matrix"),
            ("dirty verdict", valid_report.replace("| delivered |", "| unverified |", 1), "Verdict must be delivered for package completion"),
            ("stale source", valid_report, "Package Markdown Digest does not match current package Markdown content"),
        ]
        for name, report, expected_error in final_cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    proof_text = fixture.completed_proof()
                    fixture.proof_path.write_text(proof_text, encoding="utf-8")
                    plan = fixture.plan()
                    plan["work_packages"][0]["status"] = "done"
                    fixture.write_plan(plan)
                    report_text = fixture.report_text(proof_text)
                    if name == "old shape":
                        report_text = remove_h3_section(report_text, "Deliverable Completeness Matrix")
                    elif name == "dirty verdict":
                        report_text = report_text.replace("| delivered |", "| unverified |", 1)
                    else:
                        fixture.package_path.write_text(fixture.package_path.read_text(encoding="utf-8") + "\n<!-- stale -->\n", encoding="utf-8")
                    fixture.report_path.write_text(report_text, encoding="utf-8")
                    result = fixture.run("validate-final", str(fixture.tasks_path))
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

    def test_validate_final_validates_optional_semgrep_evidence_binding(self) -> None:
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)

        valid_evidence = self.fixture.semgrep_evidence_text()
        self.fixture.report_path.write_text(
            self.fixture.report_text(proof, semgrep_evidence=valid_evidence),
            encoding="utf-8",
        )
        valid = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, valid.returncode, valid.stdout + valid.stderr)

        cases = [
            (
                "missing status",
                valid_evidence.replace("- Status: `enabled`\n", ""),
                "## Semgrep Evidence missing 'Status'",
            ),
            (
                "outside tree",
                valid_evidence.replace(".tasks/fixture/semgrep/WP1.semgrep.json", ".tasks/fixture/WP1.semgrep.json"),
                "path must be under .tasks/fixture/semgrep/",
            ),
            (
                "wrong package stem",
                self.fixture.semgrep_evidence_text(stem="WP2"),
                "Raw Path must use package stem WP1.semgrep.json",
            ),
            (
                "raw digest mismatch",
                self.fixture.semgrep_evidence_text(raw_digest="0" * 64),
                "Raw Digest does not match current raw output",
            ),
            (
                "summary digest mismatch",
                self.fixture.semgrep_evidence_text(summary_digest="f" * 64),
                "Summary Digest does not match current summary output",
            ),
        ]
        for name, evidence, expected_error in cases:
            with self.subTest(name=name):
                self.fixture.report_path.write_text(
                    self.fixture.report_text(proof, semgrep_evidence=evidence),
                    encoding="utf-8",
                )
                result = self.fixture.run("validate-final", str(self.fixture.tasks_path))
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))

        with self.subTest(name="symlink evidence rejected"):
            raw_path, _raw_digest, _summary_path, _summary_digest = self.fixture.write_semgrep_evidence()
            raw_file = self.fixture.repo / raw_path
            raw_file.unlink()
            outside = self.fixture.repo / "outside.semgrep.json"
            outside.write_text("{}\n", encoding="utf-8")
            raw_file.symlink_to(outside)
            self.fixture.report_path.write_text(
                self.fixture.report_text(proof, semgrep_evidence=valid_evidence),
                encoding="utf-8",
            )
            result = self.fixture.run("validate-final", str(self.fixture.tasks_path))
            self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
            self.assertIn("path must not contain symlinks", "\n".join(json.loads(result.stderr)["errors"]))

    def test_validate_final_requires_local_git_candidate_inspection(self) -> None:
        self.fixture.write_completed_proof_and_report()
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        fake_bin = self.fixture.repo / "fake-bin"
        fake_bin.mkdir()
        marker = self.fixture.repo / "git-was-called"
        fake_git = fake_bin / "git"
        fake_git.write_text(
            "#!/bin/sh\n"
            "echo invoked > \"$SLICEPROOF_FAKE_GIT_MARKER\"\n"
            "exit 99\n",
            encoding="utf-8",
        )
        fake_git.chmod(0o700)
        env = os.environ.copy()
        env["PATH"] = f"{fake_bin}{os.pathsep}{env.get('PATH', '')}"
        env["SLICEPROOF_FAKE_GIT_MARKER"] = str(marker)

        result = self.fixture.run("validate-final", str(self.fixture.tasks_path), env=env)

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("local git inspection failed", "\n".join(json.loads(result.stderr)["errors"]))
        self.assertTrue(marker.exists(), "validate-final did not inspect the bound Git candidate")

    def test_validate_final_accepts_bound_candidate_that_is_not_current_head(self) -> None:
        self.fixture.init_git(branch="current/branch")
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        self.fixture.report_path.write_text(self.fixture.report_text(proof), encoding="utf-8")
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)

        result = self.fixture.run("validate-final", str(self.fixture.tasks_path))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_zero_slice_registry_allows_index_only_package_assignment(self) -> None:
        plan = self.fixture.plan()
        plan["authoritative_slices"] = []
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        self.fixture.package_path.write_text(
            self.fixture.package_text().replace(
                textwrap.dedent(
                    """
                    ### `.planning/fixture/slices/helper.md`
                    Must satisfy:
                    - `HELPER-PLAN-001` — Registry and package references validate mechanically
                    - `HELPER-PROOF-002` — Proof placeholders and proof closure are mechanical

                    Context only:
                    - `HELPER-CONTEXT-003` — Context-only IDs stay required reading
                    """
                ).strip(),
                "- None.",
            ),
            encoding="utf-8",
        )
        created = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, created.returncode, created.stdout + created.stderr)
        proof = self.fixture.proof_path.read_text(encoding="utf-8")
        completed = proof.replace("TODO", "observed evidence").replace("OPEN", "PASS")
        self.fixture.proof_path.write_text(completed, encoding="utf-8")
        emitted = self.fixture.run(
            "emit-state-binding",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            *self.fixture.binding_cli_args(),
        )
        self.assertEqual(0, emitted.returncode, emitted.stdout + emitted.stderr)
        self.assertIn("- Assigned Slices: `none`", emitted.stdout)
        self.assertIn("- Assigned Slice Digests: `none`", emitted.stdout)
        self.fixture.report_path.write_text(
            self.fixture.report_text(
                completed,
                assigned_slices="none",
                selected_causal_evidence=self.fixture.selected_causal_evidence(
                    command_result=(
                        "`command:proof#Commands Run:observed evidence` — PASS, generated fixture proof command closed."
                    )
                ),
            ),
            encoding="utf-8",
        )
        result = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
