from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1]
SLICEPROOF_PATH = ASSETS_DIR / "sliceproof.py"


class SliceproofFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.feature_dir = self.repo / ".tasks" / "fixture"
        self.package_dir = self.feature_dir / "packages"
        self.proofs_dir = self.feature_dir / "proofs"
        self.slice_dir = self.repo / ".planning" / "fixture" / "slices"
        self.package_path = self.package_dir / "WP1.md"
        self.proof_path = self.proofs_dir / "WP1.proof.md"
        self.tasks_path = self.feature_dir / "tasks.json"
        self.slice_path = self.slice_dir / "helper.md"
        self.feature_dir.mkdir(parents=True)
        self.package_dir.mkdir()
        self.proofs_dir.mkdir()
        self.slice_dir.mkdir(parents=True)
        (self.feature_dir / "SPEC.md").write_text("# Fixture Spec\n", encoding="utf-8")
        self.slice_path.write_text(self.slice_text(), encoding="utf-8")
        self.package_path.write_text(self.package_text(), encoding="utf-8")
        self.write_plan(self.plan())

    def cleanup(self) -> None:
        self.tmp.cleanup()

    def run(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SLICEPROOF_PATH), *args],
            cwd=self.repo,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

    def plan(self) -> dict:
        return {
            "schema_version": 4,
            "feature": "fixture",
            "title": "Fixture",
            "status": "planned",
            "spec_path": ".tasks/fixture/SPEC.md",
            "authoritative_slices": [".planning/fixture/slices/helper.md"],
            "work_packages": [
                {
                    "id": "WP1",
                    "path": ".tasks/fixture/packages/WP1.md",
                    "proof_path": ".tasks/fixture/proofs/WP1.proof.md",
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
            """
        ).lstrip()

    def package_text(
        self,
        *,
        missing_section: str | None = None,
        must_id: str | None = "HELPER-PLAN-001",
        context_id: str | None = "HELPER-CONTEXT-003",
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
        sections = {
            "Scope": "Validate the v4 Slice-first helper behavior with deterministic fixtures.",
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
            "Primary Paths": "- `plugins/super-developer/assets/sliceproof.py`",
            "Verification Expectations": textwrap.dedent(
                """
                - `sliceproof.py validate-plan` succeeds for the valid fixture.
                - `sliceproof.py validate-proof` fails placeholders and passes completed proof.
                """
            ).strip(),
            "Proof": "- `.tasks/fixture/proofs/WP1.proof.md`",
            "Dependencies": "- None.",
        }
        if missing_section:
            sections.pop(missing_section)
        body = ["# Work Package: WP1 — Helper behavior", ""]
        for name, value in sections.items():
            body.extend([f"## {name}", value, ""])
        return "\n".join(body)

    def completed_proof(self, *, status: str = "PASS", implementation: str = "sliceproof.py validates registry/package/Slice references.", verification: str = "unittest fixture observed the helper command exit 0.") -> str:
        return textwrap.dedent(
            f"""
            # Package Proof: WP1 — Helper behavior

            ## Package Scope
            Validate the v4 Slice-first helper behavior with deterministic fixtures.

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
            - None.

            ## Package Agent Completion Statement
            - Mechanical helper evidence recorded for all required rows.
            """
        ).lstrip()


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

    def test_validate_plan_rejects_path_dependency_section_and_h3_failures(self) -> None:
        cases = []

        unsafe_plan = self.fixture.plan()
        unsafe_plan["work_packages"][0]["path"] = "../escape.md"
        cases.append(("unsafe path", lambda fixture: fixture.write_plan(unsafe_plan), "path must not contain"))

        missing_section_text = self.fixture.package_text(missing_section="Proof")
        cases.append(("missing package section", lambda fixture: fixture.package_path.write_text(missing_section_text, encoding="utf-8"), "missing required section ## Proof"))

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
            (
                "must lowercase",
                lambda fixture: fixture.package_path.write_text(
                    fixture.package_text(must_id="helper-plan-001"), encoding="utf-8"
                ),
                "must_satisfy ID 'helper-plan-001' has unsupported shape",
            ),
            (
                "must bad shape",
                lambda fixture: fixture.package_path.write_text(fixture.package_text(must_id="HELPER-PLAN"), encoding="utf-8"),
                "must_satisfy ID 'HELPER-PLAN' has unsupported shape",
            ),
            (
                "must missing",
                lambda fixture: fixture.package_path.write_text(fixture.package_text(must_id=None), encoding="utf-8"),
                "must_satisfy ID 'Registry and package references validate mechanically' has unsupported shape",
            ),
            (
                "context lowercase",
                lambda fixture: fixture.package_path.write_text(
                    fixture.package_text(context_id="helper-context-003"), encoding="utf-8"
                ),
                "context_only ID 'helper-context-003' has unsupported shape",
            ),
            (
                "context bad shape",
                lambda fixture: fixture.package_path.write_text(
                    fixture.package_text(context_id="HELPER-CONTEXT"), encoding="utf-8"
                ),
                "context_only ID 'HELPER-CONTEXT' has unsupported shape",
            ),
            (
                "context missing",
                lambda fixture: fixture.package_path.write_text(fixture.package_text(context_id=None), encoding="utf-8"),
                "context_only ID 'Context-only IDs stay required reading' has unsupported shape",
            ),
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

    def test_create_proof_generates_placeholder_from_package_markdown(self) -> None:
        result = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        proof = self.fixture.proof_path.read_text(encoding="utf-8")
        self.assertIn("| `HELPER-PLAN-001` |", proof)
        self.assertIn("| `HELPER-PROOF-002` |", proof)
        self.assertIn("Context only: `HELPER-CONTEXT-003`", proof)
        self.assertNotIn("| `HELPER-CONTEXT-003` |", proof)

        placeholder_validation = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, placeholder_validation.returncode)
        self.assertIn("unresolved TODO/OPEN/GAP", "\n".join(json.loads(placeholder_validation.stderr)["errors"]))

    def test_validate_proof_accepts_completed_pass_rows_and_rejects_blocking_statuses(self) -> None:
        self.fixture.proof_path.write_text(self.fixture.completed_proof(), encoding="utf-8")
        result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

        cases = [
            ("TODO", "PASS", "TODO", "observed command output", "implementation evidence is missing"),
            ("OPEN", "OPEN", "some implementation evidence", "observed command output", "status OPEN blocks"),
            ("GAP", "GAP", "some implementation evidence", "observed command output", "status GAP blocks"),
            ("DEFERRED", "DEFERRED", "some implementation evidence", "observed command output", "DEFERRED requires explicit approved"),
            ("N/A", "N/A", "some implementation evidence", "observed command output", "N/A requires explicit rationale"),
            ("missing verification", "PASS", "some implementation evidence", "", "verification evidence is missing"),
        ]
        for name, status, implementation, verification, expected_error in cases:
            with self.subTest(name=name):
                self.fixture.proof_path.write_text(
                    self.fixture.completed_proof(status=status, implementation=implementation, verification=verification),
                    encoding="utf-8",
                )
                invalid = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertNotEqual(0, invalid.returncode, invalid.stdout + invalid.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(invalid.stderr)["errors"]))

    def test_validate_proof_rejects_duplicate_rows_and_scans_full_tables(self) -> None:
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
        self.fixture.proof_path.write_text(proof, encoding="utf-8")

        result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        errors = "\n".join(json.loads(result.stderr)["errors"])
        self.assertIn("duplicate Slice Closure Table row for HELPER-PLAN-001", errors)
        self.assertIn("HELPER-PLAN-001 status OPEN blocks", errors)
        self.assertIn("duplicate Acceptance / Verification Closure row", errors)
        self.assertIn("status OPEN blocks", errors)

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

    def test_validate_proof_rejects_negated_approval_for_deferrals(self) -> None:
        cases = [
            (
                "slice row",
                lambda proof: proof.replace(
                    "| `HELPER-PLAN-001` | Registry and package references validate mechanically | sliceproof.py validates registry/package/Slice references. | unittest fixture observed the helper command exit 0. | PASS |",
                    "| `HELPER-PLAN-001` | Registry and package references validate mechanically | deferred implementation with not approved deferral scope | verification evidence captured | DEFERRED |",
                ),
                "HELPER-PLAN-001 DEFERRED requires explicit approved",
            ),
            (
                "expectation row",
                lambda proof: proof.replace(
                    "| `sliceproof.py validate-plan` succeeds for the valid fixture. | unittest fixture observed validate-plan exit 0. | PASS |",
                    "| `sliceproof.py validate-plan` succeeds for the valid fixture. | no approval for deferral scope despite evidence | DEFERRED |",
                ),
                "DEFERRED requires explicit approved",
            ),
            (
                "gaps section",
                lambda proof: proof.replace(
                    "## Gaps, Deviations, or Deferred Items\n- None.\n",
                    "## Gaps, Deviations, or Deferred Items\n- DEFERRED by unapproved scope note.\n",
                ),
                "deferred gap/deviation requires explicit approved",
            ),
        ]
        for name, mutate, expected_error in cases:
            with self.subTest(name=name):
                self.fixture.proof_path.write_text(mutate(self.fixture.completed_proof()), encoding="utf-8")
                result = self.fixture.run("validate-proof", str(self.fixture.tasks_path), "--package", "WP1")
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))

                plan = self.fixture.plan()
                plan["work_packages"][0]["status"] = "done"
                self.fixture.write_plan(plan)
                final = self.fixture.run("validate-final", str(self.fixture.tasks_path))
                self.assertNotEqual(0, final.returncode, final.stdout + final.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(final.stderr)["errors"]))

    def test_create_proof_force_refuses_status_only_blocker_drift_without_backup(self) -> None:
        first = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        placeholder = self.fixture.proof_path.read_text(encoding="utf-8")
        drifted = placeholder.replace("| TODO | TODO | OPEN |", "| TODO | TODO | GAP |", 1)
        self.fixture.proof_path.write_text(drifted, encoding="utf-8")

        rejected = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1", "--force")
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual(drifted, self.fixture.proof_path.read_text(encoding="utf-8"))
        self.assertIn("proof status/content drift", "\n".join(json.loads(rejected.stderr)["errors"]))

        approved = self.fixture.run(
            "create-proof",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            "--force",
            "--approved-replacement",
            "User approved replacing stale status drift; existing proof must be preserved.",
        )
        self.assertEqual(0, approved.returncode, approved.stdout + approved.stderr)
        data = json.loads(approved.stdout)
        backup = self.fixture.repo / data["preserved_existing_proof"]
        self.assertEqual(drifted, backup.read_text(encoding="utf-8"))

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
            "User approved replacing stale evidence; existing proof must be preserved.",
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

    def test_create_proof_force_refuses_edited_gaps_section_and_preserves_file(self) -> None:
        first = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        placeholder = self.fixture.proof_path.read_text(encoding="utf-8")
        edited = placeholder.replace(
            "## Gaps, Deviations, or Deferred Items\n- None.\n",
            "## Gaps, Deviations, or Deferred Items\n- Investigate fixture evidence before dispatch.\n",
        )
        self.fixture.proof_path.write_text(edited, encoding="utf-8")

        rejected = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1", "--force")
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual(edited, self.fixture.proof_path.read_text(encoding="utf-8"))
        self.assertIn("contains filled proof evidence", "\n".join(json.loads(rejected.stderr)["errors"]))

    def test_create_proof_force_refuses_filled_evidence_without_preserving_approved_replacement(self) -> None:
        first = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)

        no_force = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, no_force.returncode)
        self.assertIn("already exists", "\n".join(json.loads(no_force.stderr)["errors"]))

        empty_force = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1", "--force")
        self.assertEqual(0, empty_force.returncode, empty_force.stdout + empty_force.stderr)

        filled = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(filled, encoding="utf-8")
        rejected = self.fixture.run("create-proof", str(self.fixture.tasks_path), "--package", "WP1", "--force")
        self.assertNotEqual(0, rejected.returncode)
        self.assertEqual(filled, self.fixture.proof_path.read_text(encoding="utf-8"))
        self.assertIn("contains filled proof evidence", "\n".join(json.loads(rejected.stderr)["errors"]))

        approved = self.fixture.run(
            "create-proof",
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
            "--force",
            "--approved-replacement",
            "User approved replacing stale evidence; existing proof must be preserved.",
        )
        self.assertEqual(0, approved.returncode, approved.stdout + approved.stderr)
        data = json.loads(approved.stdout)
        backup = self.fixture.repo / data["preserved_existing_proof"]
        self.assertTrue(backup.exists())
        self.assertEqual(filled, backup.read_text(encoding="utf-8"))
        self.assertIn("TODO", self.fixture.proof_path.read_text(encoding="utf-8"))

    def test_validate_final_requires_done_packages_and_valid_proofs(self) -> None:
        self.fixture.proof_path.write_text(self.fixture.completed_proof(), encoding="utf-8")
        not_done = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, not_done.returncode)
        self.assertIn("expected 'done'", "\n".join(json.loads(not_done.stderr)["errors"]))

        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        done = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)


if __name__ == "__main__":
    unittest.main()
