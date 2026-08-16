from __future__ import annotations

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


def remove_h3_section(text: str, section: str) -> str:
    return re.sub(rf"\n### {re.escape(section)}\n.*?(?=\n### |\n## |\Z)", "\n", text, count=1, flags=re.DOTALL)


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
        self.reports_dir = self.feature_dir / "reports"
        self.slice_dir = self.artifact_root / ".planning" / "fixture" / "slices"
        self.package_path = self.package_dir / "WP1.md"
        self.report_path = self.reports_dir / "WP1.package-verification.md"
        self.tasks_path = self.feature_dir / "tasks.json"
        self.slice_path = self.slice_dir / "helper.md"
        self.feature_dir.mkdir(parents=True)
        self.package_dir.mkdir()
        self.reports_dir.mkdir()
        self.slice_dir.mkdir(parents=True)
        self.evidence_asset = self.repo / "plugins" / "super-developer" / "assets" / "sliceproof.py"
        self.evidence_test = self.repo / "plugins" / "super-developer" / "assets" / "tests" / "test_sliceproof.py"
        self.evidence_ref = self.repo / "plugins" / "super-developer" / "references" / "tool-usage.md"
        self.evidence_test.parent.mkdir(parents=True)
        self.evidence_ref.parent.mkdir(parents=True)
        self.evidence_asset.write_text("def validate_plan():\n    pass\n", encoding="utf-8")
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

    def plan(self, *, include_proof_path: bool = False) -> dict:
        package = {
            "id": "WP1",
            "path": ".tasks/fixture/packages/WP1.md",
            "report_path": ".tasks/fixture/reports/WP1.package-verification.md",
            "status": "pending",
            "depends_on": [],
        }
        if include_proof_path:
            package["proof_path"] = ".tasks/fixture/proofs/WP1.proof.md"
        return {
            "feature": "fixture",
            "title": "Fixture",
            "status": "planned",
            "spec_path": ".tasks/fixture/SPEC.md",
            "authoritative_slices": [".planning/fixture/slices/helper.md"],
            "work_packages": [package],
        }

    def write_plan(self, plan: dict) -> None:
        self.tasks_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

    def spec_text(self) -> str:
        return textwrap.dedent(
            """
            # Fixture Spec

            ## Acceptance
            - AC-1: helper validates the fixture plan — check: `sliceproof.py validate-plan` — expected: exit 0.
            - AC-2: helper validates completed package results — check: `sliceproof.py validate-package-complete` — expected: exit 0.
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

            ### HELPER-PROOF-002 - Result files and checklist coverage are mechanical
            The helper checks result coverage without semantic scoring.

            ### HELPER-CONTEXT-003
            Context-only IDs must be readable but do not create required result rows.

            ### HELPER-PIPE-004 — Result rows preserve A | B table content
            Escaped pipe characters in generated result table cells must round-trip through validation.

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
                - `HELPER-PROOF-002` — Result files and checklist coverage are mechanical

                Context only:
                {context_line}
                """
            ).strip(),
            "Primary Paths": "\n".join(f"- `{path}`" for path in primary_paths),
            "Verification Expectations": textwrap.dedent(
                """
                - `sliceproof.py validate-plan` succeeds for the valid fixture.
                - `sliceproof.py validate-package-complete` fails FAIL/blocker reports and passes complete results.
                """
            ).strip(),
            "Acceptance Checklist": (
                acceptance_checklist
                if acceptance_checklist is not None
                else textwrap.dedent(
                    """
                    - AC-1: registry and package references validate mechanically — check: `sliceproof.py validate-plan` — expected: exit 0.
                    - AC-2: completed package results validate mechanically — check: `sliceproof.py validate-package-complete` — expected: exit 0.
                    """
                ).strip()
            ),
            "Package Verification Report": "- `.tasks/fixture/reports/WP1.package-verification.md`",
            "Dependencies": "- None.",
        }
        if missing_section:
            sections.pop(missing_section)
        body = ["# Work Package: WP1 — Helper behavior", ""]
        for name, value in sections.items():
            body.extend([f"## {name}", value, ""])
        return "\n".join(body)

    def report_text(
        self,
        *,
        worktree: str | None = None,
        git_ref: str | None = None,
        commit: str | None = None,
        ac2_pointer: str | None = None,
        gaps: str = "- none",
    ) -> str:
        worktree = str(self.repo.resolve(strict=False)) if worktree is None else worktree
        git_ref = "wp/fixture/WP1" if git_ref is None else git_ref
        commit = REPORT_COMMIT if commit is None else commit
        ac2_pointer = ac2_pointer or "`sliceproof.py validate-package-complete` (exit 0; fixture observed pass)"
        return textwrap.dedent(
            f"""
            ## Package Verification: WP1

            ### Verdict
            PASS

            ## Acceptance Checklist Result
            - AC-1: pass — pointer: `plugins/super-developer/assets/sliceproof.py` — observed: exit 0; fixture ran validate-plan.
            - AC-2: pass — pointer: {ac2_pointer}

            ## Blocking findings
            - none

            ## Advisory notes
            - none

            ## Reviewed state
            - Worktree: `{worktree}`
            - Git Ref: `{git_ref}`
            - Commit: `{commit}`

            ## Gaps
            {gaps}
            """
        ).lstrip()

    def write_completed_report(self, **kwargs) -> None:
        self.report_path.write_text(self.report_text(**kwargs), encoding="utf-8")

    def write_simple_package_artifacts(self, package_id: str, *, must_ids: list[str], context_ids: list[str] | None = None) -> None:
        context_ids = context_ids or []
        titles = {
            "HELPER-PLAN-001": "Registry and package references validate mechanically",
            "HELPER-PROOF-002": "Result files and checklist coverage are mechanical",
            "HELPER-CONTEXT-003": "Context-only IDs stay required reading",
            "HELPER-PIPE-004": "Result rows preserve table content",
            "HELPER-INTERFACE-005": "Interface-bearing rows require exactness",
        }
        report_rel = f".tasks/fixture/reports/{package_id}.package-verification.md"
        package_path = self.package_dir / f"{package_id}.md"
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
            "## Package Verification Report",
            f"- `{report_rel}`",
            "",
            "## Dependencies",
            "- None.",
            "",
        ])
        package_path.write_text("\n".join(package_lines), encoding="utf-8")
        report_path.write_text(self.report_text(git_ref=f"wp/fixture/{package_id}"), encoding="utf-8")


class SliceproofTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SliceproofFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_validate_plan_accepts_new_shape_registry_without_proof_path(self) -> None:
        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertEqual(["WP1"], data["packages"])
        self.assertNotIn("proof_path", self.fixture.plan()["work_packages"][0])
        self.assertNotIn("create-proof", SLICEPROOF_PATH.read_text(encoding="utf-8"))
        self.assertNotIn("validate-proof", SLICEPROOF_PATH.read_text(encoding="utf-8"))
        self.assertNotIn("proof_path", SLICEPROOF.REGISTRY_PACKAGE_KEYS)

    def test_validate_plan_accepts_bootstrap_registry_that_still_declares_proof_path(self) -> None:
        proofs = self.fixture.feature_dir / "proofs"
        proofs.mkdir()
        (proofs / "WP1.proof.md").write_text("# leftover historical proof\n", encoding="utf-8")
        self.fixture.write_plan(self.fixture.plan(include_proof_path=True))
        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

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

    def test_explicit_roots_apply_to_remaining_helper_commands(self) -> None:
        fixture = SliceproofFixture(separate_roots=True)
        try:
            fixture.write_completed_report()
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

    def test_missing_assigned_h3_fails_closed_with_section_scoped_error(self) -> None:
        self.fixture.slice_path.write_text(remove_h3_section(self.fixture.slice_path.read_text(encoding="utf-8"), "HELPER-CONTEXT-003"), encoding="utf-8")

        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "assigned H3 'HELPER-CONTEXT-003' not found in Slice '.planning/fixture/slices/helper.md'",
            "\n".join(json.loads(result.stderr)["errors"]),
        )

    def test_validate_package_complete_accepts_new_shape_without_eight_section_proof(self) -> None:
        self.fixture.write_completed_report()
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
        self.assertTrue(data["new_shape"])
        self.assertTrue(data["mechanical_only"])
        self.assertFalse(data["semantic_done"])
        self.assertNotIn("proof_path", data)
        self.assertFalse((self.fixture.feature_dir / "proofs" / "WP1.proof.md").exists())
        self.assertFalse(marker.exists(), "validate-package-complete unexpectedly invoked git")

        unknown = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP9")
        self.assertNotEqual(0, unknown.returncode)
        self.assertIn("unknown package id WP9", "\n".join(json.loads(unknown.stderr)["errors"]))

    def test_proof_path_plus_report_path_cannot_cheap_pass_as_new_shape(self) -> None:
        proofs = self.fixture.feature_dir / "proofs"
        proofs.mkdir()
        (proofs / "WP1.proof.md").write_text("# leftover historical proof\n", encoding="utf-8")
        self.fixture.write_plan(self.fixture.plan(include_proof_path=True))
        self.fixture.write_completed_report()

        result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("cannot apply new-shape PASS while proof_path is declared", "\n".join(json.loads(result.stderr)["errors"]))

        plan = self.fixture.plan(include_proof_path=True)
        plan["work_packages"][0]["status"] = "done"
        self.fixture.write_plan(plan)
        final = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertNotEqual(0, final.returncode, final.stdout + final.stderr)
        self.assertIn("cannot apply new-shape PASS while proof_path is declared", "\n".join(json.loads(final.stderr)["errors"]))

    def test_fail_or_blocker_report_cannot_complete(self) -> None:
        good = self.fixture.report_text()
        cases = [
            ("fail verdict", good.replace("\nPASS\n", "\nFAIL\n"), "Verdict must be PASS"),
            (
                "open blocker",
                good.replace("## Blocking findings\n- none", "## Blocking findings\n- data loss risk"),
                "open blocking findings",
            ),
            (
                "non-pass item",
                good.replace("- AC-2: pass —", "- AC-2: fail —"),
                "result must be pass",
            ),
        ]
        for name, report_text, expected in cases:
            with self.subTest(name=name):
                self.fixture.report_path.write_text(report_text, encoding="utf-8")
                result = self.fixture.run(
                    "validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1"
                )
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected, "\n".join(json.loads(result.stderr)["errors"]))

    def test_hollow_non_path_pass_is_not_semantic_done(self) -> None:
        self.fixture.write_completed_report(ac2_pointer="looks good, observed success")
        result = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        data = json.loads(result.stdout)
        self.assertTrue(data["ok"])
        self.assertTrue(data["mechanical_only"])
        self.assertFalse(data["semantic_done"])

    def test_pointer_resolve_keeps_symlink_and_escape_coverage(self) -> None:
        if not hasattr(os, "symlink"):
            self.skipTest("symlink not available on this platform")

        cases = []

        def missing_path(fixture: SliceproofFixture) -> None:
            fixture.write_completed_report(ac2_pointer="`plugins/super-developer/assets/missing.py`")

        cases.append(("missing path", missing_path, "file not found"))

        def absolute_path(fixture: SliceproofFixture) -> None:
            fixture.write_completed_report(ac2_pointer="`/tmp/escape.py`")

        cases.append(("absolute path", absolute_path, "not absolute/home/drive-qualified"))

        def home_path(fixture: SliceproofFixture) -> None:
            fixture.write_completed_report(ac2_pointer="`~/escape.py`")

        cases.append(("home path", home_path, "not absolute/home/drive-qualified"))

        def parent_escape(fixture: SliceproofFixture) -> None:
            fixture.write_completed_report(ac2_pointer="`../escape.py`")

        cases.append(("parent escape", parent_escape, "path must not contain"))

        def symlink_escape(fixture: SliceproofFixture) -> None:
            outside = fixture.external_worktree / "outside.py"
            outside.write_text("escaped\n", encoding="utf-8")
            link = fixture.repo / "plugins" / "super-developer" / "assets" / "escaped.py"
            os.symlink(outside, link)
            fixture.write_completed_report(ac2_pointer="`plugins/super-developer/assets/escaped.py`")

        cases.append(("symlink escape", symlink_escape, "refusing symlink-escaped pointer"))

        for name, mutate, expected in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    mutate(fixture)
                    result = fixture.run("validate-package-complete", str(fixture.tasks_path), "--package", "WP1")
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

        self.fixture.write_completed_report(ac2_pointer="`test:plugins/super-developer/assets/tests/test_sliceproof.py::missing`")
        test_id = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, test_id.returncode, test_id.stdout + test_id.stderr)

        self.fixture.write_completed_report(ac2_pointer="`python3 -m pytest plugins/super-developer/assets/tests/missing.py`")
        command = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, command.returncode, command.stdout + command.stderr)

    def test_validate_final_passes_without_git_metadata_and_does_not_call_git(self) -> None:
        self.fixture.write_completed_report()
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
        self.assertFalse(json.loads(result.stdout)["semantic_done"])
        self.assertFalse(marker.exists(), "validate-final unexpectedly invoked git")

    def test_validate_final_does_not_compare_report_git_fields_to_current_checkout(self) -> None:
        self.fixture.init_git(branch="current/branch")
        self.fixture.write_completed_report(
            worktree=str(self.fixture.repo.parent / "other-worktree"),
            git_ref="refs/heads/not-current",
            commit=REPORT_COMMIT,
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

    def test_validate_plan_rejects_package_with_no_executable_acceptance_item(self) -> None:
        self.fixture.package_path.write_text(
            self.fixture.package_text(
                acceptance_checklist=(
                    "- AC-1: operator confirms the rendered result — check: manual (approved) "
                    "— verify: inspect the fixture output."
                )
            ),
            encoding="utf-8",
        )
        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "at least one independently confirmable executable check",
            "\n".join(json.loads(result.stderr)["errors"]),
        )

    def test_validate_package_complete_reports_pending_verification_verdict_intact(self) -> None:
        self.fixture.write_completed_report()
        report = self.fixture.report_path.read_text(encoding="utf-8").replace(
            "### Verdict\nPASS", "### Verdict\nPENDING_VERIFICATION", 1
        )
        self.fixture.report_path.write_text(report, encoding="utf-8")
        result = self.fixture.run(
            "validate-package-complete",
            *self.fixture.root_args(),
            str(self.fixture.tasks_path),
            "--package",
            "WP1",
        )
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        errors = "\n".join(json.loads(result.stderr)["errors"])
        self.assertIn("Verdict must be PASS (found PENDING_VERIFICATION)", errors)

    def test_validate_plan_flags_compound_acceptance_claims_without_blocking(self) -> None:
        self.fixture.package_path.write_text(
            self.fixture.package_text(
                acceptance_checklist=(
                    "- AC-1: ingestion validates schema and rejects future rows and enforces the cap "
                    "— check: `pytest tests/test_a.py` — expected: exit 0.\n"
                    "- AC-2: helper emits the summary — check: `pytest tests/test_b.py` — expected: exit 0."
                )
            ),
            encoding="utf-8",
        )
        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["semantic_done"])
        atomicity = [item for item in payload["advisories"] if item["kind"] == "acceptance_atomicity"]
        self.assertEqual(["AC-1"], [item["item"] for item in atomicity])
        self.assertEqual("WP1", atomicity[0]["package"])

    def test_validate_plan_closure_size_advisory_clears_with_recorded_justification(self) -> None:
        oversized = "\n".join(
            f"- AC-{index}: fixture outcome {index} — check: `pytest tests/test_{index}.py` — expected: exit 0."
            for index in range(1, 11)
        )
        self.fixture.package_path.write_text(
            self.fixture.package_text(acceptance_checklist=oversized),
            encoding="utf-8",
        )
        flagged = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, flagged.returncode, flagged.stdout + flagged.stderr)
        flagged_payload = json.loads(flagged.stdout)
        closure = [item for item in flagged_payload["advisories"] if item["kind"] == "closure_size"]
        self.assertEqual(1, len(closure), flagged_payload["advisories"])
        self.assertEqual(10, closure[0]["acceptance_items"])

        self.fixture.package_path.write_text(
            self.fixture.package_path.read_text(encoding="utf-8")
            + "\n## Notes\n- Closure justification: one ingestion lifecycle; splitting duplicates the shared harness.\n",
            encoding="utf-8",
        )
        justified = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, justified.returncode, justified.stdout + justified.stderr)
        justified_payload = json.loads(justified.stdout)
        self.assertEqual(
            [],
            [item for item in justified_payload["advisories"] if item["kind"] == "closure_size"],
        )

    def test_validate_plan_atomicity_advisory_ignores_check_and_rejects_clauses(self) -> None:
        self.fixture.package_path.write_text(
            self.fixture.package_text(
                acceptance_checklist=(
                    "- AC-1: helper rejects alias spellings — check: `pytest tests/test_a.py` "
                    "— expected: exit 0 and bounded output — rejects: accepting `--dryrun` and `--dry_run`."
                )
            ),
            encoding="utf-8",
        )
        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            [],
            [item for item in payload["advisories"] if item["kind"] == "acceptance_atomicity"],
        )

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

    def test_validate_plan_rejects_weak_acceptance_items(self) -> None:
        cases = [
            ("placeholder", "- TODO", "is a placeholder"),
            (
                "TODO-leading requirement description",
                "- AC-1: TODO later — check: `x`",
                "requirement description is missing or placeholder",
            ),
            (
                "TBD-leading requirement description",
                "- AC-1: TBD later — check: `x`",
                "requirement description is missing or placeholder",
            ),
            (
                "to-be-determined requirement description",
                "- AC-1: to-be-determined later — check: `x`",
                "requirement description is missing or placeholder",
            ),
            ("empty check payload", "- AC-1: finished — check:", "must include a non-empty 'check:' payload"),
            (
                "expected clause without check payload",
                "- AC-1: finished — check: — expected: exit 0",
                "must include a non-empty 'check:' payload",
            ),
            (
                "verify label without manual description",
                "- AC-1: operator confirms result — manual (approved) — verify:",
                "must include a non-empty description",
            ),
            ("no check grammar", "- AC-1: something is finished", "must name an executable 'check:'"),
            (
                "duplicate id",
                "- AC-1: a — check: `x`\n- AC-1: b — check: `y`",
                "duplicate acceptance item ID",
            ),
            ("no id", "- finished without an id — check: `x`", "must start with a stable ID"),
        ]
        for name, checklist, expected in cases:
            with self.subTest(name=name):
                fixture = SliceproofFixture()
                try:
                    fixture.package_path.write_text(
                        fixture.package_text(acceptance_checklist=checklist), encoding="utf-8"
                    )
                    result = fixture.run("validate-plan", str(fixture.tasks_path))
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                    self.assertIn(expected, "\n".join(json.loads(result.stderr)["errors"]))
                finally:
                    fixture.cleanup()

        mixed = SliceproofFixture()
        try:
            mixed.package_path.write_text(
                mixed.package_text(
                    acceptance_checklist=(
                        "- AC-1: helper validates the fixture plan — check: `sliceproof.py validate-plan` — expected: exit 0.\n"
                        "- AC-2: operator confirms the rendered result — check: manual (approved) "
                        "— verify: inspect the fixture output."
                    )
                ),
                encoding="utf-8",
            )
            mixed_result = mixed.run("validate-plan", str(mixed.tasks_path))
            self.assertEqual(0, mixed_result.returncode, mixed_result.stdout + mixed_result.stderr)
        finally:
            mixed.cleanup()

        spec_path = self.fixture.feature_dir / "SPEC.md"
        spec_path.write_text("# Fixture Spec\n\n## Acceptance\n- TODO\n", encoding="utf-8")
        result = self.fixture.run("validate-plan", str(self.fixture.tasks_path))
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("is a placeholder", "\n".join(json.loads(result.stderr)["errors"]))
        spec_path.write_text(self.fixture.spec_text(), encoding="utf-8")

    def test_report_verdict_rejects_fenced_smuggling_and_duplicates(self) -> None:
        fixture = SliceproofFixture()
        try:
            fixture.write_completed_report()
            good = fixture.report_text()
            cases = [
                (
                    "fenced pass before actual fail",
                    "```md\n## Verdict\nPASS\n```\n\n" + good.replace("### Verdict\nPASS", "## Verdict\nFAIL"),
                    "Verdict must be PASS",
                ),
                (
                    "mixed fence cannot hide actual fail",
                    "```md\n~~~\n" + good + "```\n\n" + good.replace("### Verdict\nPASS", "## Verdict\nFAIL"),
                    "Verdict must be PASS",
                ),
                (
                    "duplicate verdict",
                    good.replace("### Verdict\nPASS", "### Verdict\nPASS\n\n## Verdict\nPASS"),
                    "exactly one canonical Verdict heading/value",
                ),
            ]
            for name, report_text, expected in cases:
                with self.subTest(name=name):
                    fixture.report_path.write_text(report_text, encoding="utf-8")
                    package = fixture.run(
                        "validate-package-complete", str(fixture.tasks_path), "--package", "WP1"
                    )
                    self.assertNotEqual(0, package.returncode, package.stdout + package.stderr)
                    self.assertIn(expected, "\n".join(json.loads(package.stderr)["errors"]))

                    plan = fixture.plan()
                    plan["work_packages"][0]["status"] = "done"
                    fixture.write_plan(plan)
                    final = fixture.run("validate-final", str(fixture.tasks_path))
                    self.assertNotEqual(0, final.returncode, final.stdout + final.stderr)
                    self.assertIn(expected, "\n".join(json.loads(final.stderr)["errors"]))
        finally:
            fixture.cleanup()

    def test_report_verdict_accepts_valid_report_after_nonclosing_fence_markers(self) -> None:
        fixture = SliceproofFixture()
        try:
            fixture.write_completed_report()
            good = fixture.report_text()
            examples = [
                "```md\n~~~\n## Verdict\nFAIL\n```\n\n",
                "````md\n```\n## Verdict\nFAIL\n````\n\n",
            ]
            for example in examples:
                with self.subTest(example=example.splitlines()[0]):
                    fixture.report_path.write_text(example + good, encoding="utf-8")
                    package = fixture.run(
                        "validate-package-complete", str(fixture.tasks_path), "--package", "WP1"
                    )
                    self.assertEqual(0, package.returncode, package.stdout + package.stderr)
        finally:
            fixture.cleanup()

    def test_validate_package_complete_enforces_checklist_outcome_and_gaps_metadata(self) -> None:
        good = self.fixture.report_text()
        cases = [
            ("fail verdict", good.replace("\nPASS\n", "\nFAIL\n"), "Verdict must be PASS"),
            (
                "missing frozen item",
                good.replace(
                    "- AC-2: pass — pointer: `sliceproof.py validate-package-complete` (exit 0; fixture observed pass)\n",
                    "",
                ),
                "missing frozen item AC-2",
            ),
            (
                "open blocker",
                good.replace("## Blocking findings\n- none", "## Blocking findings\n- data loss risk"),
                "open blocking findings",
            ),
            ("no reviewed state", good.split("## Reviewed state")[0] + "\n## Gaps\n- none\n", "Reviewed state"),
            ("missing gaps", good.split("## Gaps")[0], "missing ## Gaps section"),
            (
                "gaps without approval",
                good.replace("## Gaps\n- none", "## Gaps\n- leftover historical proof not migrated."),
                "approval, provenance, and scope",
            ),
        ]
        for name, report_text, expected in cases:
            with self.subTest(name=name):
                self.fixture.write_completed_report()
                self.fixture.report_path.write_text(report_text, encoding="utf-8")
                result = self.fixture.run(
                    "validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1"
                )
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected, "\n".join(json.loads(result.stderr)["errors"]))

        approved = self.fixture.report_text(
            gaps="- Approved by user; provenance: product owner accepted leftover note; scope: WP1 result only."
        )
        self.fixture.report_path.write_text(approved, encoding="utf-8")
        ok = self.fixture.run("validate-package-complete", str(self.fixture.tasks_path), "--package", "WP1")
        self.assertEqual(0, ok.returncode, ok.stdout + ok.stderr)

    def test_validate_final_requires_done_status_and_lightweight_report(self) -> None:
        self.fixture.write_completed_report()
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
                    - `HELPER-PROOF-002` — Result files and checklist coverage are mechanical

                    Context only:
                    - `HELPER-CONTEXT-003` — Context-only IDs stay required reading
                    """
                ).strip(),
                "- None.",
            ),
            encoding="utf-8",
        )
        self.fixture.write_completed_report()
        result = self.fixture.run("validate-final", str(self.fixture.tasks_path))
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
