from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "agentic-lifecycle-scenarios.json"
SLICEPROOF_PATH = Path(__file__).resolve().parents[1] / "sliceproof.py"
EXPECTATION_KEYS = ("v1_39", "phase_1", "candidate")
SCENARIO_KEYS = {
    "id",
    "title",
    "initial_state_class",
    "initial_state",
    "user_inputs",
    "allowed_commands",
    "permitted_calls",
    "permitted_prompts",
    "seed",
    "expectations",
}
EXPECTATION_FIELDS = {
    "first_detection_stage",
    "first_detection_class",
    "maximum_formal_prompts",
    "repair_wave_expectation",
    "terminal_result",
    "notes",
}
TERMINAL_RESULTS = {
    "pass",
    "blocked",
    "needs_decision",
    "circuit_open",
    "rejected",
    "not_guaranteed",
}


def load_scenarios() -> dict:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


def run_git(cwd: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if check and result.returncode != 0:
        raise AssertionError(f"git {' '.join(args)} failed:\n{result.stdout}{result.stderr}")
    return result


def init_repo(path: Path) -> None:
    path.mkdir(parents=True)
    run_git(path, "init", "-b", "main")
    run_git(path, "config", "user.email", "agentic-fixture@example.invalid")
    run_git(path, "config", "user.name", "Agentic Fixture")
    run_git(path, "config", "commit.gpgsign", "false")


def init_bare(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        ["git", "init", "--bare", str(path)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


def commit_all(repo: Path, message: str) -> str:
    run_git(repo, "add", ".")
    run_git(repo, "commit", "-m", message)
    return run_git(repo, "rev-parse", "HEAD").stdout.strip()


def remote_ref(remote: Path, ref: str) -> str | None:
    result = subprocess.run(
        ["git", "ls-remote", str(remote), ref],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    line = result.stdout.strip()
    return line.split()[0] if line else None


def resolve_push_endpoint(repo: Path, authorized: str) -> str:
    result = run_git(repo, "remote", "get-url", "--push", "--all", "origin", check=False)
    endpoints = result.stdout.splitlines()
    if result.returncode != 0 or len(endpoints) != 1 or not endpoints[0] or endpoints[0] != authorized:
        raise ValueError("expected one unchanged authorized push endpoint")
    return endpoints[0]


def write_lifecycle_state(repo: Path, state: dict) -> Path:
    path = repo / ".tasks" / "fixture" / "lifecycle-state.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    return path


def canonical_digest(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def valid_lifecycle_state() -> dict:
    return {
        "schema_version": 1,
        "generation": 1,
        "feature": "fixture",
        "stage": "planning",
        "quiescent": True,
        "next_legal_actions": ["plan-review"],
        "owner": {"token": "owner-a", "host": "host-a", "disposition": "active", "takeover": None},
        "artifact_checkpoint": {"ref": "refs/heads/artifacts/fixture", "sha": None, "tree": None},
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
                    "delegated_calls": 2, "planner_correction_waves": 1,
                    "spike_waves": 0, "command_units": 3,
                },
                "started_at": "2026-07-18T10:00:00Z",
                "deadline_at": "2026-07-18T12:00:00Z",
            },
            "implementation": None,
            "active_reservation": None,
            "control_plane_reserve": {"maximum": 1, "issued": 0},
        },
        "packages": {}, "wave": None, "serious_clusters": [],
        "freeze": None, "receipts": [], "last_verified": None,
        "portability_authorization": "explicit fixture instruction",
    }


def run_lifecycle_validation(artifact_root: Path, code_root: Path, previous: str | None = None) -> subprocess.CompletedProcess[str]:
    command = [
        "python3", str(SLICEPROOF_PATH), "validate-lifecycle-state",
        "--artifact-root", str(artifact_root), "--code-root", str(code_root), "--feature", "fixture",
    ]
    if previous is not None:
        command.extend(["--previous-commit", previous])
    return subprocess.run(command, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


class AgenticLifecycleOracleTests(unittest.TestCase):
    def test_scenario_manifest_schema_is_complete(self) -> None:
        manifest = load_scenarios()
        self.assertEqual(
            {"schema_version", "corpus_id", "oracle_revisions", "scenarios"},
            set(manifest),
        )
        self.assertEqual(1, manifest["schema_version"])
        self.assertEqual(EXPECTATION_KEYS, tuple(manifest["oracle_revisions"]))
        for revision in manifest["oracle_revisions"].values():
            self.assertRegex(revision["commit"], r"^[0-9a-f]{40}$")
            self.assertTrue(revision["label"].strip())

        self.assertEqual(22, len(manifest["scenarios"]))
        for scenario in manifest["scenarios"]:
            with self.subTest(scenario=scenario["id"]):
                self.assertEqual(SCENARIO_KEYS, set(scenario))
                self.assertRegex(scenario["id"], r"^ADH-(0[1-9]|1[0-9]|2[0-2])$")
                self.assertTrue(scenario["title"].strip())
                self.assertTrue(scenario["initial_state_class"].strip())
                self.assertEqual(
                    {"code", "artifacts", "lifecycle"}, set(scenario["initial_state"])
                )
                for value in scenario["initial_state"].values():
                    self.assertTrue(value.strip())
                for field in (
                    "user_inputs",
                    "allowed_commands",
                    "permitted_calls",
                    "permitted_prompts",
                ):
                    self.assertIsInstance(scenario[field], list)
                    self.assertTrue(scenario[field])
                    self.assertTrue(all(isinstance(item, str) and item.strip() for item in scenario[field]))

                seed = scenario["seed"]
                self.assertEqual({"id", "class", "serious", "description"}, set(seed))
                self.assertIsInstance(seed["serious"], bool)
                self.assertTrue(seed["id"].strip())
                self.assertTrue(seed["class"].strip())
                self.assertTrue(seed["description"].strip())

                self.assertEqual(EXPECTATION_KEYS, tuple(scenario["expectations"]))
                for revision_name, expectation in scenario["expectations"].items():
                    self.assertEqual(EXPECTATION_FIELDS, set(expectation), revision_name)
                    self.assertTrue(expectation["first_detection_stage"].strip())
                    self.assertTrue(expectation["first_detection_class"].strip())
                    maximum_prompts = expectation["maximum_formal_prompts"]
                    self.assertTrue(maximum_prompts is None or maximum_prompts >= 0)
                    waves = expectation["repair_wave_expectation"]
                    self.assertEqual({"minimum", "maximum"}, set(waves))
                    self.assertGreaterEqual(waves["minimum"], 0)
                    if waves["maximum"] is not None:
                        self.assertGreaterEqual(waves["maximum"], waves["minimum"])
                    self.assertIn(expectation["terminal_result"], TERMINAL_RESULTS)
                    self.assertTrue(expectation["notes"].strip())

                candidate = scenario["expectations"]["candidate"]
                self.assertIsInstance(candidate["maximum_formal_prompts"], int)
                self.assertIsNotNone(candidate["repair_wave_expectation"]["maximum"])

    def test_scenario_manifest_identity_and_seed_fields_are_unique(self) -> None:
        scenarios = load_scenarios()["scenarios"]
        for field_getter in (
            lambda item: item["id"],
            lambda item: item["title"],
            lambda item: item["seed"]["id"],
            lambda item: item["seed"]["description"],
        ):
            values = [field_getter(item) for item in scenarios]
            self.assertEqual(len(values), len(set(values)))
        self.assertEqual([f"ADH-{number:02d}" for number in range(1, 23)], [s["id"] for s in scenarios])

    def test_sidecar_only_roots_drill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = root / "code"
            sidecar = root / "artifact-sidecar"
            init_repo(code)
            init_repo(sidecar)
            (code / "product.txt").write_text("base\n", encoding="utf-8")
            artifact = sidecar / ".tasks" / "fixture" / "SPEC.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("# Fixture\n", encoding="utf-8")
            commit_all(code, "code base")
            commit_all(sidecar, "sidecar base")

            code_root = Path(run_git(code, "rev-parse", "--show-toplevel").stdout.strip())
            artifact_root = Path(run_git(sidecar, "rev-parse", "--show-toplevel").stdout.strip())
            self.assertNotEqual(code_root, artifact_root)
            self.assertTrue(artifact.is_relative_to(artifact_root))
            self.assertFalse(artifact.is_relative_to(code_root))
            self.assertFalse((code / ".tasks").exists())

    def test_non_force_code_before_sidecar_publication_windows_drill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code_remote = root / "remotes" / "code.git"
            sidecar_remote = root / "remotes" / "sidecar.git"
            code = root / "code"
            sidecar = root / "sidecar"
            init_bare(code_remote)
            init_bare(sidecar_remote)
            init_repo(code)
            init_repo(sidecar)
            run_git(code, "remote", "add", "origin", str(code_remote))
            run_git(sidecar, "remote", "add", "origin", str(sidecar_remote))

            (code / "product.txt").write_text("candidate one\n", encoding="utf-8")
            code_sha = commit_all(code, "candidate")
            (sidecar / "README.md").write_text("sidecar\n", encoding="utf-8")
            commit_all(sidecar, "initial sidecar")
            checkpoint_ref = "refs/heads/checkpoints/fixture/integration/g1"
            artifact_ref = "refs/heads/artifacts/fixture"

            # Before code publication, a sidecar reference would point at a local-only object.
            self.assertIsNone(remote_ref(code_remote, checkpoint_ref))
            self.assertIsNone(remote_ref(sidecar_remote, artifact_ref))

            run_git(code, "push", "origin", f"HEAD:{checkpoint_ref}")
            self.assertEqual(code_sha, remote_ref(code_remote, checkpoint_ref))
            # A crash here leaves only an unreferenced orphan checkpoint.
            self.assertIsNone(remote_ref(sidecar_remote, artifact_ref))

            write_lifecycle_state(
                sidecar,
                {
                    "generation": 2,
                    "authorization_id": "auth-fixture",
                    "code_checkpoint": {"ref": checkpoint_ref, "sha": code_sha},
                },
            )
            commit_all(sidecar, "reference verified code")
            run_git(sidecar, "push", "origin", f"HEAD:{artifact_ref}")
            self.assertIsNotNone(remote_ref(sidecar_remote, artifact_ref))

            (code / "product.txt").write_text("rewritten candidate\n", encoding="utf-8")
            run_git(code, "add", "product.txt")
            run_git(code, "commit", "--amend", "-m", "rewritten candidate")
            rejected = run_git(code, "push", "origin", f"HEAD:{checkpoint_ref}", check=False)
            self.assertNotEqual(0, rejected.returncode, "immutable checkpoint ref must reject non-force rewrite")
            self.assertEqual(code_sha, remote_ref(code_remote, checkpoint_ref))

    def test_exact_push_endpoint_fence_ignores_distinct_fetch_url(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fetch_remote = root / "fetch.git"
            push_remote = root / "push.git"
            owner = root / "owner"
            init_bare(fetch_remote)
            init_bare(push_remote)
            init_repo(owner)
            run_git(owner, "remote", "add", "origin", str(fetch_remote))
            run_git(owner, "remote", "set-url", "--push", "origin", str(push_remote))
            (owner / "artifact.txt").write_text("endpoint-fenced\n", encoding="utf-8")
            sha = commit_all(owner, "endpoint-fenced candidate")
            ref = "refs/heads/artifacts/fixture"

            endpoint = resolve_push_endpoint(owner, str(push_remote))
            self.assertIsNone(remote_ref(Path(endpoint), ref))
            run_git(owner, "push", "--", endpoint, f"{sha}:{ref}")
            run_git(owner, "fetch", "--no-tags", "--", endpoint, ref)
            self.assertEqual(sha, run_git(owner, "rev-parse", "FETCH_HEAD").stdout.strip())
            self.assertEqual(sha, remote_ref(Path(endpoint), ref))
            self.assertIsNone(remote_ref(fetch_remote, ref), "fetch URL must not verify the push endpoint")
            self.assertEqual(endpoint, resolve_push_endpoint(owner, str(push_remote)))

            run_git(owner, "remote", "set-url", "--add", "--push", "origin", str(fetch_remote))
            with self.assertRaises(ValueError):
                resolve_push_endpoint(owner, str(push_remote))
            run_git(owner, "remote", "set-url", "--delete", "--push", "origin", str(fetch_remote))
            captured = resolve_push_endpoint(owner, str(push_remote))
            run_git(owner, "remote", "set-url", "--push", "origin", str(fetch_remote))
            with self.assertRaises(ValueError):
                resolve_push_endpoint(owner, captured)
            run_git(owner, "remote", "remove", "origin")
            with self.assertRaises(ValueError):
                resolve_push_endpoint(owner, captured)

    def test_current_root_rejection_and_migration_drill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code = root / "code"
            sidecar = root / "sidecar"
            outside = root / "outside-secret.md"
            init_repo(code)
            init_repo(sidecar)
            legacy_slice = code / ".planning" / "fixture" / "slices" / "feature.md"
            legacy_task = code / ".tasks" / "fixture" / "SPEC.md"
            unsafe_link = code / ".planning" / "fixture" / "slices" / "escape.md"
            legacy_slice.parent.mkdir(parents=True)
            legacy_task.parent.mkdir(parents=True)
            legacy_slice.write_text("# Legacy Slice\n", encoding="utf-8")
            legacy_task.write_text("# Legacy Spec\n", encoding="utf-8")
            outside.write_text("must not import\n", encoding="utf-8")
            unsafe_link.symlink_to(outside)
            source_head = commit_all(code, "legacy current-root artifacts")

            self.assertEqual(
                run_git(code, "rev-parse", "--show-toplevel").stdout.strip(),
                str(code),
                "current-root artifacts cannot establish a distinct planned authority",
            )
            candidates = (legacy_slice, legacy_task, unsafe_link)
            safe_sources = [
                source
                for source in candidates
                if not source.is_symlink()
                and source.is_file()
                and source.resolve().is_relative_to(code.resolve())
            ]
            self.assertEqual([legacy_slice, legacy_task], safe_sources)
            imported = []
            for source in safe_sources:
                relative = source.relative_to(code)
                destination = sidecar / relative
                destination.parent.mkdir(parents=True, exist_ok=True)
                self.assertFalse(destination.exists(), "migration must not overwrite")
                shutil.copy2(source, destination)
                imported.append(
                    {
                        "source": relative.as_posix(),
                        "destination": relative.as_posix(),
                        "sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                    }
                )
            provenance = sidecar / ".tasks" / "fixture" / "migration-provenance.json"
            provenance.write_text(
                json.dumps(
                    {
                        "source_root": str(code.resolve()),
                        "source_head": source_head,
                        "feature": "fixture",
                        "initiating_instruction": "fixture migration authorization",
                        "files": imported,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
            commit_all(sidecar, "import legacy artifacts")

            self.assertNotEqual(
                run_git(code, "rev-parse", "--show-toplevel").stdout.strip(),
                run_git(sidecar, "rev-parse", "--show-toplevel").stdout.strip(),
            )
            self.assertEqual(legacy_slice.read_text(), (sidecar / legacy_slice.relative_to(code)).read_text())
            self.assertEqual(legacy_task.read_text(), (sidecar / legacy_task.relative_to(code)).read_text())
            self.assertFalse((sidecar / unsafe_link.relative_to(code)).exists())
            persisted = json.loads(provenance.read_text(encoding="utf-8"))
            self.assertEqual(source_head, persisted["source_head"])
            self.assertEqual(imported, persisted["files"])
            tracked = run_git(sidecar, "ls-files").stdout.splitlines()
            self.assertIn(".tasks/fixture/migration-provenance.json", tracked)

    def test_initial_sidecar_cas_and_path_specific_staging_drill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote = root / "remote.git"
            owner = root / "owner"
            competitor = root / "competitor"
            init_bare(remote)
            init_repo(owner)
            run_git(owner, "remote", "add", "origin", str(remote))
            artifact_ref = "refs/heads/artifacts/fixture"
            slice_path = owner / ".planning" / "fixture" / "slices" / "feature.md"
            slice_path.parent.mkdir(parents=True)
            slice_path.write_text("# Portable Slice\n", encoding="utf-8")
            write_lifecycle_state(
                owner,
                {
                    "schema_version": 1,
                    "generation": 1,
                    "feature": "fixture",
                    "quiescent": True,
                    "stage": "conceptualization-checkpoint",
                    "next_legal_actions": ["planning"],
                    "portability_authorization": "explicit fixture instruction",
                    "artifact_ref": artifact_ref,
                    "expected_parent": "absent",
                    "code_checkpoints": [],
                },
            )
            (owner / "unfinalized.tmp").write_text("do not capture\n", encoding="utf-8")

            self.assertIsNone(remote_ref(remote, artifact_ref))
            run_git(
                owner,
                "add",
                ".planning/fixture/slices/feature.md",
                ".tasks/fixture/lifecycle-state.json",
            )
            staged = run_git(owner, "diff", "--cached", "--name-only").stdout.splitlines()
            self.assertEqual(
                [
                    ".planning/fixture/slices/feature.md",
                    ".tasks/fixture/lifecycle-state.json",
                ],
                staged,
            )
            run_git(owner, "commit", "-m", "initial sidecar")
            initial_sha = run_git(owner, "rev-parse", "HEAD").stdout.strip()
            run_git(owner, "push", "origin", f"{initial_sha}:{artifact_ref}")
            self.assertEqual(initial_sha, remote_ref(remote, artifact_ref))
            self.assertIsNone(remote_ref(remote, "refs/heads/main"))
            self.assertIsNone(remote_ref(remote, "refs/heads/feature/fixture"))

            run_git(root, "clone", str(remote), str(competitor))
            run_git(competitor, "config", "user.email", "competitor@example.invalid")
            run_git(competitor, "config", "user.name", "Competitor")
            run_git(competitor, "checkout", "-b", "artifact-copy", "origin/artifacts/fixture")
            (competitor / ".tasks" / "fixture" / "competitor.md").write_text(
                "advance remote\n", encoding="utf-8"
            )
            competitor_sha = commit_all(competitor, "competing sidecar CAS")

            (owner / ".tasks" / "fixture" / "owner.md").write_text("stale owner\n", encoding="utf-8")
            run_git(owner, "add", ".tasks/fixture/owner.md")
            run_git(owner, "commit", "-m", "stale owner checkpoint")
            owner_sha = run_git(owner, "rev-parse", "HEAD").stdout.strip()
            run_git(competitor, "push", "origin", f"{competitor_sha}:{artifact_ref}")
            rejected = run_git(owner, "push", "origin", f"{owner_sha}:{artifact_ref}", check=False)
            self.assertNotEqual(0, rejected.returncode)
            self.assertEqual(competitor_sha, remote_ref(remote, artifact_ref))

    def test_monotonic_budget_persistence_drill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote = root / "sidecar.git"
            owner = root / "owner"
            code = root / "code"
            resumed = root / "resumed"
            init_bare(remote)
            init_repo(owner)
            init_repo(code)
            run_git(owner, "remote", "add", "origin", str(remote))
            (code / "product.txt").write_text("base\n", encoding="utf-8")
            commit_all(code, "code base")

            state_one = valid_lifecycle_state()
            write_lifecycle_state(owner, state_one)
            initial = run_lifecycle_validation(owner, code)
            self.assertEqual(0, initial.returncode, initial.stdout + initial.stderr)
            generation_one = commit_all(owner, "budget generation one")
            run_git(owner, "push", "-u", "origin", "main")

            state_two = json.loads(json.dumps(state_one))
            state_two["generation"] = 2
            state_two["budgets"]["preauthorization"]["issued"]["delegated_calls"] = 3
            state_two["budgets"]["active_reservation"] = {
                "id": "reserve-2", "owner_token": "owner-a", "budget": "preauthorization",
                "generation": 2, "units": {"delegated_calls": 1},
            }
            state_two["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture",
                "artifact_sha": generation_one,
                "state_digest": canonical_digest(state_one),
                "generation": 1,
            }
            write_lifecycle_state(owner, state_two)
            advanced = run_lifecycle_validation(owner, code, generation_one)
            self.assertEqual(0, advanced.returncode, advanced.stdout + advanced.stderr)
            generation_two = commit_all(owner, "budget generation two")
            run_git(owner, "push", "origin", "main")

            run_git(root, "clone", "--branch", "main", str(remote), str(resumed))
            persisted = json.loads((resumed / ".tasks" / "fixture" / "lifecycle-state.json").read_text())
            self.assertEqual(state_two, persisted)
            resumed_check = run_lifecycle_validation(resumed, code, generation_one)
            self.assertEqual(0, resumed_check.returncode, resumed_check.stdout + resumed_check.stderr)

            reset = json.loads(json.dumps(state_two))
            reset["generation"] = 3
            reset["budgets"]["active_reservation"] = None
            reset["budgets"]["preauthorization"]["issued"]["delegated_calls"] = 0
            reset["last_verified"] = {
                "artifact_ref": "refs/heads/artifacts/fixture",
                "artifact_sha": generation_two,
                "state_digest": canonical_digest(state_two),
                "generation": 2,
            }
            write_lifecycle_state(resumed, reset)
            rejected = run_lifecycle_validation(resumed, code, generation_two)
            self.assertNotEqual(0, rejected.returncode, rejected.stdout + rejected.stderr)
            self.assertIn("cannot decrease", "\n".join(json.loads(rejected.stderr)["errors"]))

    def test_last_verified_escalation_drill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            remote = root / "sidecar.git"
            owner_a = root / "owner-a"
            owner_b = root / "owner-b"
            escalation_reader = root / "escalation-reader"
            init_bare(remote)
            init_repo(owner_a)
            run_git(owner_a, "remote", "add", "origin", str(remote))
            write_lifecycle_state(owner_a, {"generation": 1, "owner": "owner-a", "stage": "quiescent"})
            commit_all(owner_a, "verified generation one")
            run_git(owner_a, "push", "-u", "origin", "main")

            run_git(root, "clone", str(remote), str(owner_b))
            write_lifecycle_state(owner_a, {"generation": 2, "owner": "owner-a", "stage": "local-unverified"})
            commit_all(owner_a, "unverified local generation")
            write_lifecycle_state(owner_b, {"generation": 2, "owner": "owner-b", "stage": "quiescent"})
            commit_all(owner_b, "verified competing generation")
            run_git(owner_b, "push", "origin", "main")

            cas_loser = run_git(owner_a, "push", "origin", "main", check=False)
            self.assertNotEqual(0, cas_loser.returncode)
            remote_before = remote_ref(remote, "refs/heads/main")
            run_git(root, "clone", str(remote), str(escalation_reader))
            last_verified = json.loads(
                (escalation_reader / ".tasks" / "fixture" / "lifecycle-state.json").read_text()
            )
            self.assertEqual({"generation": 2, "owner": "owner-b", "stage": "quiescent"}, last_verified)
            self.assertNotEqual("local-unverified", last_verified["stage"])
            self.assertEqual(remote_before, remote_ref(remote, "refs/heads/main"))

    def test_cold_resume_drill(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            code_remote = root / "code.git"
            sidecar_remote = root / "sidecar.git"
            code_owner = root / "code-owner"
            sidecar_owner = root / "sidecar-owner"
            cold_sidecar = root / "cold-sidecar"
            cold_code = root / "cold-code"
            init_bare(code_remote)
            init_bare(sidecar_remote)
            init_repo(code_owner)
            init_repo(sidecar_owner)
            run_git(code_owner, "remote", "add", "origin", str(code_remote))
            run_git(sidecar_owner, "remote", "add", "origin", str(sidecar_remote))

            (code_owner / "product.txt").write_text("quiescent candidate\n", encoding="utf-8")
            code_sha = commit_all(code_owner, "quiescent candidate")
            checkpoint_ref = "refs/heads/checkpoints/fixture/wave-1/g7"
            run_git(code_owner, "push", "origin", f"HEAD:{checkpoint_ref}")
            self.assertEqual(code_sha, remote_ref(code_remote, checkpoint_ref))

            state = {
                "schema_version": 1,
                "generation": 7,
                "feature": "fixture",
                "quiescent": True,
                "stage": "package-wave-quiescent",
                "next_legal_actions": ["resume-owner-cas"],
                "owner": {"token": "owner-a", "disposition": "stopped"},
                "code_checkpoint": {"ref": checkpoint_ref, "sha": code_sha},
                "budgets": {
                    "issued_calls": 4,
                    "issued_repair_waves": 1,
                    "deadline_at": "2026-07-18T16:00:00Z",
                },
                "clusters": [{"id": "REQ-1|mechanism|surface", "strikes": 1}],
            }
            write_lifecycle_state(sidecar_owner, state)
            commit_all(sidecar_owner, "publish quiescent state")
            run_git(sidecar_owner, "push", "-u", "origin", "main")

            run_git(root, "clone", str(sidecar_remote), str(cold_sidecar))
            resumed = json.loads((cold_sidecar / ".tasks" / "fixture" / "lifecycle-state.json").read_text())
            self.assertEqual(state, resumed)
            self.assertTrue(resumed["quiescent"])
            self.assertEqual(1, resumed["clusters"][0]["strikes"])
            self.assertEqual(4, resumed["budgets"]["issued_calls"])
            self.assertNotEqual("completed", resumed["stage"])

            run_git(root, "clone", str(code_remote), str(cold_code))
            run_git(cold_code, "fetch", "origin", checkpoint_ref)
            self.assertEqual(code_sha, run_git(cold_code, "rev-parse", "FETCH_HEAD").stdout.strip())
            self.assertEqual(code_sha, remote_ref(code_remote, resumed["code_checkpoint"]["ref"]))


if __name__ == "__main__":
    unittest.main()
