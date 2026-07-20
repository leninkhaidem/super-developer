from __future__ import annotations

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
REPORT_COMMIT = "0123456789abcdef0123456789abcdef01234567"


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
        self.slice_dir = self.artifact_root / ".planning" / "fixture" / "slices"
        self.package_path = self.package_dir / "WP1.md"
        self.proof_path = self.proofs_dir / "WP1.proof.md"
        self.report_path = self.reports_dir / "WP1.package-verification.md"
        self.tasks_path = self.feature_dir / "tasks.json"
        self.slice_path = self.slice_dir / "helper.md"
        self.feature_dir.mkdir(parents=True)
        self.package_dir.mkdir()
        self.proofs_dir.mkdir()
        self.reports_dir.mkdir()
        self.slice_dir.mkdir(parents=True)
        self.evidence_asset = self.repo / "plugins" / "super-developer" / "assets" / "sliceproof.py"
        self.evidence_test = self.repo / "plugins" / "super-developer" / "assets" / "tests" / "test_sliceproof.py"
        self.evidence_ref = self.repo / "plugins" / "super-developer" / "references" / "tool-usage.md"
        self.evidence_test.parent.mkdir(parents=True)
        self.evidence_ref.parent.mkdir(parents=True)
        self.evidence_asset.write_text("def validate_plan():\n    pass\n\ndef validate_proof():\n    pass\n", encoding="utf-8")
        self.evidence_test.write_text("def test_validate_plan_accepts_valid_registry_package_slice_fixture():\n    pass\n", encoding="utf-8")
        self.evidence_ref.write_text("# Tool Usage\n\n## sliceproof.py\n", encoding="utf-8")
        (self.feature_dir / "SPEC.md").write_text(self.spec_text(), encoding="utf-8")
        self.slice_path.write_text(self.slice_text(), encoding="utf-8")
        self.package_path.write_text(self.package_text(), encoding="utf-8")
        self.write_plan(self.plan())

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

    def init_git(self, branch: str = "wp/fixture/WP1") -> None:
        self.git_checked("init")
        self.git_checked("config", "user.email", "sliceproof@example.invalid")
        self.git_checked("config", "user.name", "Sliceproof Fixture")
        self.git_checked("config", "commit.gpgsign", "false")
        self.git_checked("checkout", "-b", branch)
        self.git_checked("add", ".")
        self.git_checked("commit", "-m", "initial fixture")

    def plan(self) -> dict:
        return {
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
                    "report_path": ".tasks/fixture/reports/WP1.package-verification.md",
                    "status": "pending",
                    "depends_on": [],
                }
            ],
        }

    def write_plan(self, plan: dict) -> None:
        self.tasks_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    def spec_text(self) -> str:
        return textwrap.dedent(
            """
            # Fixture Spec

            ## Acceptance
            - AC-1: helper validates the fixture plan — check: `sliceproof.py validate-plan` — expected: exit 0.
            - AC-2: helper validates completed proofs — check: `sliceproof.py validate-proof` — expected: exit 0.
            """
        ).lstrip()

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
        acceptance_checklist: str | None = None,
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
            "Acceptance Checklist": (
                acceptance_checklist
                if acceptance_checklist is not None
                else textwrap.dedent(
                    """
                    - AC-1: registry and package references validate mechanically — check: `sliceproof.py validate-plan` — expected: exit 0.
                    - AC-2: completed proofs validate mechanically — check: `sliceproof.py validate-proof` — expected: exit 0.
                    """
                ).strip()
            ),
            "Proof": "- `.tasks/fixture/proofs/WP1.proof.md`",
            "Package Verification Report": "- `.tasks/fixture/reports/WP1.package-verification.md`",
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

    def report_text(
        self,
        proof_text: str | None = None,
        *,
        worktree: str | None = None,
        git_ref: str | None = None,
        commit: str | None = None,
    ) -> str:
        worktree = str(self.repo.resolve(strict=False)) if worktree is None else worktree
        git_ref = "wp/fixture/WP1" if git_ref is None else git_ref
        commit = REPORT_COMMIT if commit is None else commit
        return textwrap.dedent(
            f"""
            ## Acceptance Checklist Result
            - AC-1: pass — evidence: `sliceproof.py validate-plan` exit 0 in unittest fixture.
            - AC-2: pass — evidence: `sliceproof.py validate-proof` exit 0 in unittest fixture.

            ## Blocking findings
            - none

            ## Advisory notes
            - none

            ## Reviewed state
            - Worktree: `{worktree}`
            - Git Ref: `{git_ref}`
            - Commit: `{commit}`
            """
        ).lstrip()

    def write_completed_proof_and_report(self) -> None:
        proof = self.completed_proof()
        self.proof_path.write_text(proof, encoding="utf-8")
        self.report_path.write_text(self.report_text(proof), encoding="utf-8")

    def write_simple_package_artifacts(
        self,
        package_id: str,
        *,
        must_ids: list[str],
        context_ids: list[str] | None = None,
    ) -> None:
        context_ids = context_ids or []
        titles = {
            "HELPER-PLAN-001": "Registry and package references validate mechanically",
            "HELPER-PROOF-002": "Proof placeholders and proof closure are mechanical",
            "HELPER-CONTEXT-003": "Context-only IDs stay required reading",
            "HELPER-PIPE-004": "Proof rows preserve table content",
            "HELPER-INTERFACE-005": "Interface-bearing rows require exactness",
        }
        proof_rel = f".tasks/fixture/proofs/{package_id}.proof.md"
        report_rel = f".tasks/fixture/reports/{package_id}.package-verification.md"
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
            "## Acceptance Checklist",
            f"- AC-1: {package_id} fixture report validates mechanically — check: `sliceproof.py validate-package-complete` — expected: exit 0.",
            "",
            "## Proof",
            f"- `{proof_rel}`",
            "",
            "## Package Verification Report",
            f"- `{report_rel}`",
            "",
            "## Dependencies",
            "- None.",
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
        report_path.write_text(self.report_text(git_ref=f"wp/fixture/{package_id}"), encoding="utf-8")


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

            proof_check = fixture.run("validate-proof", *fixture.root_args(), ".tasks/fixture/tasks.json", "--package", "WP1")
            self.assertEqual(0, proof_check.returncode, proof_check.stdout + proof_check.stderr)

            package_check = fixture.run("validate-package-complete", *fixture.root_args(), ".tasks/fixture/tasks.json", "--package", "WP1")
            self.assertEqual(0, package_check.returncode, package_check.stdout + package_check.stderr)

            plan = fixture.plan()
            plan["work_packages"][0]["status"] = "done"
            fixture.write_plan(plan)
            final_check = fixture.run("validate-final", *fixture.root_args(), ".tasks/fixture/tasks.json")
            self.assertEqual(0, final_check.returncode, final_check.stdout + final_check.stderr)
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

        missing_section_text = self.fixture.package_text(missing_section="Package Verification Report")
        cases.append(("missing report section", lambda fixture: fixture.package_path.write_text(missing_section_text, encoding="utf-8"), "missing required section ## Package Verification Report"))

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

    def test_missing_assigned_h3_fails_closed_with_section_scoped_error(self) -> None:
        self.fixture.slice_path.write_text(remove_h3_section(self.fixture.slice_path.read_text(encoding="utf-8"), "HELPER-CONTEXT-003"), encoding="utf-8")

        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "assigned H3 'HELPER-CONTEXT-003' not found in Slice '.planning/fixture/slices/helper.md'",
            "\n".join(json.loads(result.stderr)["errors"]),
        )

    def test_validate_package_complete_accepts_pre_done_package_without_git(self) -> None:
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

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual("pending", data["package_status"])
        self.assertEqual(["VE-1", "VE-2"], data["verification_expectation_rows"])
        self.assertFalse(marker.exists(), "validate-package-complete unexpectedly invoked git")

        unknown = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP9")
        self.assertNotEqual(0, unknown.returncode)
        self.assertIn("unknown package id WP9", "\n".join(json.loads(unknown.stderr)["errors"]))

    def test_validate_final_passes_without_git_metadata_and_does_not_call_git(self) -> None:
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

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertFalse(marker.exists(), "validate-final unexpectedly invoked git")

    def test_validate_final_does_not_compare_report_git_fields_to_current_checkout(self) -> None:
        self.fixture.init_git(branch="current/branch")
        proof = self.fixture.completed_proof()
        self.fixture.proof_path.write_text(proof, encoding="utf-8")
        self.fixture.report_path.write_text(
            self.fixture.report_text(
                proof,
                worktree=str(self.fixture.repo.parent / "other-worktree"),
                git_ref="refs/heads/not-current",
                commit=REPORT_COMMIT,
            ),
            encoding="utf-8",
        )
        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)

        result = self.fixture.run("validate-final", str(self.fixture.tasks_path))

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validate_plan_requires_non_empty_package_acceptance_checklist(self) -> None:
        present = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, present.returncode, present.stdout + present.stderr)

        cases = [
            (
                "missing section",
                self.fixture.package_text(missing_section="Acceptance Checklist"),
                "missing required section ## Acceptance Checklist",
            ),
            (
                "empty section",
                self.fixture.package_text(acceptance_checklist=""),
                "## Acceptance Checklist must list at least one checklist item",
            ),
        ]
        for name, package_text, expected_error in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    fixture.package_path.write_text(package_text, encoding="utf-8")
                    result = fixture.run("validate-plan", str(fixture.tasks_path))
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

    def test_validate_plan_requires_non_empty_spec_acceptance(self) -> None:
        present = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, present.returncode, present.stdout + present.stderr)

        spec_path = self.fixture.feature_dir / "SPEC.md"
        cases = [
            ("missing section", "# Fixture Spec\n", "missing required section ## Acceptance"),
            (
                "empty section",
                "# Fixture Spec\n\n## Acceptance\n",
                "## Acceptance must list at least one feature-level acceptance item",
            ),
        ]
        for name, spec_text, expected_error in cases:
            with self.subTest(name=name):
                spec_path.write_text(spec_text, encoding="utf-8")
                result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected_error, "\n".join(json.loads(result.stderr)["errors"]))
        spec_path.write_text(self.fixture.spec_text(), encoding="utf-8")

    def test_validate_final_requires_done_status_and_lightweight_report(self) -> None:
        self.fixture.write_completed_proof_and_report()
        not_done = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, not_done.returncode)
        self.assertIn("expected 'done'", "\n".join(json.loads(not_done.stderr)["errors"]))

        plan = self.fixture.plan()
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        done = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)
        self.assertEqual([], json.loads(done.stdout)["advisories"])

        self.fixture.report_path.write_text("", encoding="utf-8")
        empty_report = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, empty_report.returncode)
        self.assertIn("must be non-empty", "\n".join(json.loads(empty_report.stderr)["errors"]))

        self.fixture.report_path.unlink()
        missing_report = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, missing_report.returncode)
        self.assertIn("report: file not found", "\n".join(json.loads(missing_report.stderr)["errors"]))

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
        self.fixture.report_path.write_text(self.fixture.report_text(completed), encoding="utf-8")
        result = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
