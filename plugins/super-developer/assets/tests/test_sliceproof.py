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
REPORT_CONTRACT_PATH = ASSETS_DIR.parent / "references" / "package-verification-report.md"
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
        plan_gaps: str = "- none",
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

            ## Plan gaps
            {plan_gaps}

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


class ReportContractTemplateTests(unittest.TestCase):
    """The canonical template must hand authors every required section.

    A required section is only frictionless if copying the contract's own template satisfies it. If the two ever
    drift, every report authored from the contract fails the helper for a reason the contract does not mention.
    """

    def test_contract_template_carries_every_required_report_section(self) -> None:
        contract = REPORT_CONTRACT_PATH.read_text(encoding="utf-8")
        fences = re.findall(r"^```md\n(.*?)^```", contract, flags=re.DOTALL | re.MULTILINE)
        self.assertTrue(fences, f"{REPORT_CONTRACT_PATH} no longer contains a ```md report template")
        template_sections = set(SLICEPROOF.split_h2_sections(fences[0]))
        self.assertEqual(set(), SLICEPROOF.REQUIRED_REPORT_SECTIONS - template_sections)


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

    def test_validate_package_complete_rejects_pass_prefixed_verdict_tokens(self) -> None:
        for token in ("PASS_PENDING", "PASS_WITH_NOTES"):
            with self.subTest(token=token):
                self.fixture.write_completed_report()
                report = self.fixture.report_path.read_text(encoding="utf-8").replace(
                    "### Verdict\nPASS", f"### Verdict\n{token}", 1
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
                self.assertIn(
                    f"Verdict must be PASS (found {token})",
                    "\n".join(json.loads(result.stderr)["errors"]),
                )

    PLAN_GAPS_SLOT = "## Plan gaps\n- none"

    def run_with_plan_gaps(self, body: str | None):
        """Rewrite the report's ``## Plan gaps`` section, or drop it entirely when ``body`` is None."""
        self.fixture.write_completed_report()
        original = self.fixture.report_path.read_text(encoding="utf-8")
        self.assertIn(self.PLAN_GAPS_SLOT, original)
        replacement = "" if body is None else f"## Plan gaps\n{body}"
        report = original.replace(self.PLAN_GAPS_SLOT, replacement, 1)
        self.fixture.report_path.write_text(report, encoding="utf-8")
        return self.fixture.run(
            "validate-package-complete", *self.fixture.root_args(), str(self.fixture.tasks_path), "--package", "WP1"
        )

    def test_validate_package_complete_fails_on_open_plan_gap(self) -> None:
        result = self.run_with_plan_gaps("- warrant: plan-gap \u2014 cancellation path is not on the frozen checklist.")
        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("still open", "\n".join(json.loads(result.stderr)["errors"]))

    def test_validate_package_complete_requires_a_written_plan_gaps_disposition(self) -> None:
        """Reports are gitignored, so a deleted section leaves no diff to audit. Requiring the section makes the
        cheapest escape a written `- none` rather than an invisible absence; prose, a fence, and an empty section
        are refused so an entry cannot be dissolved back into one."""
        for label, body, expected in (
            ("section deleted", None, "missing ## Plan gaps section"),
            ("empty section", "", "bulleted list"),
            ("prose, not a bullet", "warrant: plan-gap \u2014 cancellation path is missing.", "bulleted list"),
            (
                "entry hidden in a code fence",
                "```\n- warrant: plan-gap \u2014 cancellation path is missing.\n```",
                "bulleted list",
            ),
        ):
            with self.subTest(shape=label):
                result = self.run_with_plan_gaps(body)
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
                self.assertIn(expected, "\n".join(json.loads(result.stderr)["errors"]))

    def test_validate_package_complete_accepts_plan_gaps_closed_in_place(self) -> None:
        """Closure must never require erasure, and must never punish an accurate description. Both lifecycle
        routes keep the record of the omitted requirement in the report, and any substantive free-text closure
        counts -- including one whose wording overlaps the placeholder and unresolved-marker vocabularies."""
        for label, body in (
            ("none", "- none"),
            ("none upper case", "- NONE"),
            # Parity with ## Gaps, which accepts a terminating period through is_empty_gaps_deviations_section.
            ("none with terminator", "- None."),
            (
                "repaired via continuation",
                "- warrant: plan-gap \u2014 cancellation path. closed: repaired by continuation package WP1b, AC-7 added.",
            ),
            # Free text is taken as written: "missing" is an approval-placeholder token, yet this closure is real.
            (
                "free-text closure naming the continuation",
                "- warrant: plan-gap \u2014 cancellation path. closed: WP1b adds the missing cancellation AC",
            ),
            ("short but specific closure", "- warrant: plan-gap \u2014 cancellation path. closed: repaired by WP1b"),
            # Sentence-cased keyword: closure detection folds case, so `Closed:` is the same disposition.
            ("sentence-cased closure keyword", "- warrant: plan-gap \u2014 cancellation path. Closed: repaired by WP1b"),
            # A backticked continuation name is ordinary Markdown; entries are read whole, not unwrapped to it.
            (
                "backticked continuation name",
                "- warrant: plan-gap \u2014 cancellation path. closed: repaired by `WP1b`",
            ),
            # "gap" is the vocabulary of this section: a closure is free to use it without being read as unresolved.
            ("closure naming the gap it closed", "- warrant: plan-gap \u2014 cancellation path. closed: the gap is now AC-7"),
            # The marker scan is scoped to the closure value, so a gap *described* with OPEN/TODO stays closable.
            (
                "unresolved marker in the description only",
                "- warrant: plan-gap \u2014 the open-file limit. closed: repaired by WP1b",
            ),
            (
                "todo in the description only",
                "- warrant: plan-gap \u2014 the TODO scanner is unbounded. closed: repaired by WP1b",
            ),
            (
                "durably approved out of scope",
                "- warrant: plan-gap \u2014 cancellation path. Approved by user; provenance: plan gate 2026-08-16; "
                "scope: deferred to the resilience feature.",
            ),
        ):
            with self.subTest(closure=label):
                result = self.run_with_plan_gaps(body)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validate_package_complete_accepts_wrapped_and_nested_plan_gap_closures(self) -> None:
        """Long entries wrap, which is this repository's own house style. If a closure recorded on a continuation
        or sub-bullet read as still open, the cheapest recovery would be `- none` — the erasure this gate exists
        to prevent. `## Gaps` already accepts these shapes, so plan gaps must too."""
        for label, body in (
            (
                "wrapped closure",
                "- warrant: plan-gap \u2014 cancellation path is not on the checklist.\n"
                "  closed: repaired by continuation package WP1b, AC-7 added.",
            ),
            (
                "sub-bullet closure",
                "- warrant: plan-gap \u2014 cancellation path.\n  - closed: repaired by continuation package WP1b.",
            ),
            (
                "lazy continuation",
                "- warrant: plan-gap \u2014 cancellation path.\nclosed: repaired by continuation package WP1b.",
            ),
            (
                "wrapped approval route",
                "- warrant: plan-gap \u2014 cancellation path. Approved by user;\n"
                "  provenance: plan gate 2026-08-16; scope: deferred to the resilience feature.",
            ),
            (
                "two wrapped entries both closed",
                "- warrant: plan-gap \u2014 A.\n  closed: repaired by WP1b.\n"
                "- warrant: plan-gap \u2014 B.\n  closed: repaired by WP1c.",
            ),
        ):
            with self.subTest(shape=label):
                result = self.run_with_plan_gaps(body)
                self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validate_package_complete_reads_plan_gaps_in_every_bullet_marker(self) -> None:
        """Reports are hand-written, so `-`, `*`, and ordered markers must all open an entry and carry their own
        wrapped continuations. A marker the parser silently ignored would make a real gap unreadable."""
        for label, body, expect_ok in (
            ("dash closed", "- warrant: plan-gap \u2014 X.\n  closed: repaired by WP1b.", True),
            ("star closed", "* warrant: plan-gap \u2014 X.\n  closed: repaired by WP1b.", True),
            ("ordered closed", "1. warrant: plan-gap \u2014 X.\n   closed: repaired by WP1b.", True),
            ("star open", "* warrant: plan-gap \u2014 X is not on the frozen checklist.", False),
            ("ordered open", "1. warrant: plan-gap \u2014 X is not on the frozen checklist.", False),
        ):
            with self.subTest(marker=label):
                result = self.run_with_plan_gaps(body)
                if expect_ok:
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                else:
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validate_package_complete_finds_an_open_entry_in_any_position(self) -> None:
        """Grouping wrapped lines must not let an open entry hide behind a closed neighbour, in either order,
        and a stray `- none` beside a real entry must not clear the section."""
        for label, body in (
            ("second entry open", "- warrant: plan-gap \u2014 A.\n  closed: repaired by WP1b.\n- warrant: plan-gap \u2014 B is missed."),
            ("first entry open", "- warrant: plan-gap \u2014 A is missed.\n- warrant: plan-gap \u2014 B.\n  closed: repaired by WP1c."),
            ("none before a real entry", "- none\n- warrant: plan-gap \u2014 X is not on the checklist"),
            ("none after a real entry", "- warrant: plan-gap \u2014 X is not on the checklist\n- none"),
            ("wrapped but still open", "- warrant: plan-gap \u2014 the cancellation path\n  is not on the frozen checklist."),
        ):
            with self.subTest(shape=label):
                result = self.run_with_plan_gaps(body)
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)

    CLOSED_BULLET = "- warrant: plan-gap \u2014 cancellation. closed: repaired by WP1b"
    OPEN_BULLET = "- warrant: plan-gap \u2014 cancellation path is not on the frozen checklist."

    def test_validate_package_complete_reads_every_visible_plan_gap_bullet(self) -> None:
        """Whatever Markdown renders as a disposition must be read. Grouping wrapped lines is what lets a closure
        live on a continuation, but it must never let a closed neighbour swallow a bullet the reader can still
        see, and prose ahead of the first bullet is just as visible. The two frictionless shapes -- a wrapped
        closure and a sub-bullet closure -- must keep costing the author nothing."""
        for label, body, expect_ok in (
            # A bullet is present, so the section is a list; the prose above it is a second visible entry.
            (
                "prose before the first bullet",
                "warrant: plan-gap \u2014 OPEN cancellation gap.\n" + self.CLOSED_BULLET,
                False,
            ),
            # One space of indent is below the `- ` content column: an unmistakable sibling.
            ("one-space sibling bullet", self.CLOSED_BULLET + "\n " + self.OPEN_BULLET, False),
            # A sibling is a sibling whether or not it names a warrant, so the outer level alone has to open an
            # entry. Reading indent by the content column is what keeps this bullet from folding out of sight.
            (
                "one-space sibling that opens no warrant",
                self.CLOSED_BULLET + "\n - the retry budget is still absent",
                False,
            ),
            # A deeper bullet that opens another `warrant:` is a new disposition, not detail, so folding it away
            # would let the closed entry above it hide an open gap.
            ("two-space nested bullet", self.CLOSED_BULLET + "\n  " + self.OPEN_BULLET, False),
            ("three-space nested bullet", self.CLOSED_BULLET + "\n   " + self.OPEN_BULLET, False),
            # Detail under a closed entry opens no warrant, so it costs the author nothing. Demanding a
            # disposition for every `evidence:` or `owner:` line is the friction that pushes authors to `- none`.
            ("detail sub-bullet under a closed entry", self.CLOSED_BULLET + "\n  - evidence: see §3", True),
            (
                "several detail sub-bullets under a closed entry",
                self.CLOSED_BULLET + "\n  - evidence: see §3\n  - owner: WP1b",
                True,
            ),
            # Only a bullet that *starts* a warrant opens an entry. Matching the word anywhere would turn a
            # detail line that merely refers to the gap into an open disposition the author never wrote.
            (
                "detail sub-bullet mentioning a warrant mid-text",
                self.CLOSED_BULLET + "\n  - evidence: the warrant: plan-gap note in §3",
                True,
            ),
            # `+` is a CommonMark bullet. Reading only `-` and `*` would render this gap to the author while
            # hiding it from the gate, and would reject a `+` section that is honestly closed.
            ("plus-marker sibling gap", self.CLOSED_BULLET + "\n+ " + self.OPEN_BULLET[2:], False),
            ("plus-marker closed entry", "+ " + self.CLOSED_BULLET[2:], True),
            ("plus-marker none", "+ none", True),
            # A tab indents past the content column, so measuring it as one character would read these as
            # siblings and reject a closure the author did write.
            (
                "tab-indented sub-bullet closure",
                "- warrant: plan-gap — cancellation path.\n\t- closed: repaired by WP1b",
                True,
            ),
            ("tab-indented detail under a closed entry", self.CLOSED_BULLET + "\n\t- evidence: see §3", True),
            # A closure inside a comment renders nothing, so it cannot clear a gap the reader still sees.
            (
                "closure hidden in an HTML comment",
                "- warrant: plan-gap — cancellation is absent <!-- closed: repaired by WP1b -->",
                False,
            ),
            # A nested warrant carries its own closure. Folding it upward would let it close the open entry it
            # sits inside, which is the swallowing this parser exists to prevent.
            (
                "child warrant closure does not close an open parent",
                "- warrant: plan-gap — cancellation is absent\n  - warrant: plan-gap — retry; closed: WP1b",
                False,
            ),
            # Emphasis around the field name still opens an entry; otherwise a bolded nested gap folds away.
            (
                "emphasised nested warrant",
                self.CLOSED_BULLET + "\n  - **warrant:** plan-gap — retry budget is absent",
                False,
            ),
            # Only `warrant: plan-gap` opens an entry, so a detail line that merely discusses the field is
            # detail. Treating any `warrant:` as an entry charged this line a disposition it never needed.
            (
                "detail sub-bullet about the warrant field",
                self.CLOSED_BULLET + "\n  - *warrant*: field is now documented in the contract",
                True,
            ),
            # `1)` is an ordered marker too. Reading only `1.` hid this gap and rejected an honest `1)` section.
            ("paren-ordered sibling gap", self.CLOSED_BULLET + "\n1) " + self.OPEN_BULLET[2:], False),
            ("paren-ordered closed entry", "1) " + self.CLOSED_BULLET[2:], True),
            # A closure belongs to the gap it is written under. Folding it into every enclosing bullet let a
            # nested gap's repair silently close the separate, still-open gap around it.
            (
                "nested gap closure does not reach the open gap enclosing it",
                "- warrant: plan-gap — cancellation is absent\n"
                "  - warrant: plan-gap — retry budget is absent\n"
                "    closed: repaired by WP1b\n"
                "  - evidence: see §3",
                False,
            ),
            (
                "nested gap sub-bullet closure does not reach the gap enclosing it",
                "- warrant: plan-gap — cancellation is absent\n"
                "  - warrant: plan-gap — retry budget is absent\n"
                "    - closed: repaired by WP1b",
                False,
            ),
            # Comments are removed without disturbing line structure: stripping must not fuse two lines into
            # one, and must not turn the text beside a comment into a fence that swallows what follows.
            (
                "comment beside a fence marker",
                self.CLOSED_BULLET + "\n<!-- -->```\n" + self.OPEN_BULLET,
                False,
            ),
            (
                "multi-line comment does not splice the next entry away",
                self.CLOSED_BULLET + "<!-- c\n--> - warrant: plan-gap — retry budget is absent",
                False,
            ),
            # A fence has to be real in both texts. A marker written inside a comment renders as nothing, so
            # treating it as a fence would swallow every gap after it while the reader still sees them.
            (
                "fence marker inside a comment is not a fence",
                self.CLOSED_BULLET + "\n<!-- draft\n``` -->\n" + self.OPEN_BULLET,
                False,
            ),
            (
                "commented-out fenced example is not a fence",
                self.CLOSED_BULLET + "\n<!-- ```\nx\n``` -->\n" + self.OPEN_BULLET,
                False,
            ),
            # ...and the converse: a marker that only appears once a comment is removed was never written.
            (
                "comment beside a fence marker forges no fence",
                self.CLOSED_BULLET + "\n<!-- -->```\n" + self.OPEN_BULLET,
                False,
            ),
            # A genuine fenced example between two gaps still hides only itself.
            (
                "real fence between gaps hides only the fenced text",
                self.CLOSED_BULLET + "\n```\nexample\n```\n" + self.OPEN_BULLET,
                False,
            ),
            # Each gap is closed under itself. Sending a closure to the outermost entry instead of the nearest
            # one would leave the inner gap open while silently closing the outer.
            (
                "sibling gaps each closed beneath themselves",
                "- warrant: plan-gap — cancellation is absent\n  closed: fixed by WP1a\n"
                "  - warrant: plan-gap — retry budget is absent\n    closed: fixed by WP1b",
                True,
            ),
            # The same, with each closure written as a sub-bullet rather than a continuation line: both routes
            # have to reach the nearest gap, not the outermost one.
            (
                "nested gaps each closed by their own sub-bullet",
                "- warrant: plan-gap — cancellation is absent\n  - closed: fixed by WP1a\n"
                "  - warrant: plan-gap — retry budget is absent\n    - closed: fixed by WP1b",
                True,
            ),
            ("paren-ordered none", "1) none", True),
            # `- none` is the written claim whether or not an example sits beside it. Reading emptiness from the
            # raw body instead of the parsed entries made the fenced text turn `none` into an open entry.
            ("fenced example beside a written none", "- none\n```\n- warrant: plan-gap — sample\n```", True),
            (
                "wrapped continuation closure",
                "- warrant: plan-gap \u2014 cancellation path.\n  closed: repaired by WP1b",
                True,
            ),
            (
                "nested sub-bullet closure",
                "- warrant: plan-gap \u2014 cancellation path.\n  - closed: repaired by WP1b",
                True,
            ),
            # A sub-bullet that wraps still closes the entry above it: the continuation belongs to both.
            (
                "wrapped closure inside a sub-bullet",
                "- warrant: plan-gap \u2014 cancellation path.\n  - the frozen checklist omits cancellation\n"
                "    closed: repaired by WP1b",
                True,
            ),
        ):
            with self.subTest(shape=label):
                result = self.run_with_plan_gaps(body)
                if expect_ok:
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                else:
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validate_package_complete_reads_plan_gaps_past_mismatched_fences(self) -> None:
        """A fence closes only on its own delimiter. Toggling on any fence line would let a `~~~` inside a
        ``` block reopen it, so an entry after the real close would read as fenced and vanish."""
        for label, body, expect_ok in (
            (
                "tilde line inside a backtick fence",
                self.CLOSED_BULLET + "\n```\n~~~\n```\n" + self.OPEN_BULLET,
                False,
            ),
            (
                "backtick line inside a tilde fence",
                self.CLOSED_BULLET + "\n~~~\n```\n~~~\n" + self.OPEN_BULLET,
                False,
            ),
            # Control: genuinely fenced text is an example, not a disposition, and stays unread.
            (
                "genuinely fenced open bullet",
                self.CLOSED_BULLET + "\n```\n" + self.OPEN_BULLET + "\n```",
                True,
            ),
        ):
            with self.subTest(shape=label):
                result = self.run_with_plan_gaps(body)
                if expect_ok:
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                else:
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)

    def test_plan_gap_fence_shapes_fail_on_the_open_gap_not_a_broken_section(self) -> None:
        """A fence the parser wrongly honours never closes, so it eats the headings after the section and the run
        still fails -- on the wrong thing. Only the message separates a caught gap from a corrupted report, so
        these shapes assert it rather than the exit code alone."""
        for label, body in (
            ("comment beside a fence marker", self.CLOSED_BULLET + "\n<!-- -->```\n" + self.OPEN_BULLET),
            ("fence marker inside a comment", self.CLOSED_BULLET + "\n<!-- draft\n``` -->\n" + self.OPEN_BULLET),
            ("commented-out fenced example", self.CLOSED_BULLET + "\n<!-- ```\nx\n``` -->\n" + self.OPEN_BULLET),
            ("real fence between two gaps", self.CLOSED_BULLET + "\n```\nexample\n```\n" + self.OPEN_BULLET),
        ):
            with self.subTest(shape=label):
                result = self.run_with_plan_gaps(body)
                errors = json.loads(result.stderr)["errors"]
                self.assertEqual(1, len(errors), errors)
                self.assertIn("still open", errors[0])

    def test_section_split_ignores_fences_that_only_exist_inside_comments(self) -> None:
        """`split_h2_sections` decides where every section ends, so a fence it wrongly honours swallows the
        headings after it. It shares one fence reader with the plan-gap parser precisely so the two cannot
        disagree about what a fence is."""
        text = "## Plan gaps\n- none\n<!-- ```\nx\n``` -->\n\n## Gaps\n- none\n"
        self.assertEqual({"Plan gaps", "Gaps"}, set(SLICEPROOF.split_h2_sections(text)))
        fenced = "## Plan gaps\n- none\n```\n## Not a heading\n```\n\n## Gaps\n- none\n"
        self.assertEqual({"Plan gaps", "Gaps"}, set(SLICEPROOF.split_h2_sections(fenced)))

    def test_invisible_stripping_is_scoped_to_the_closure_value(self) -> None:
        """Dropping invisible characters makes a closure honest, but the approval detector reads whole words, so
        doing it there would splice a placeholder into a longer token and hide it. The two must stay separate."""
        for value in ("x\u200bnone", "2\u200btbd"):
            with self.subTest(value=value):
                self.assertTrue(SLICEPROOF.is_approval_placeholder_value(value))
        self.assertFalse(SLICEPROOF.is_substantive_closure("\u200b"))
        self.assertTrue(SLICEPROOF.is_substantive_closure("repaired by WP1b"))

    def test_validate_package_complete_rejects_plan_gap_closures_that_render_nothing(self) -> None:
        """A closure is read as written, so it must actually be written. Text that renders as nothing at all, or
        that denies the closure outright, records nothing an auditor can read; free prose still costs nothing."""
        for label, body, expect_ok in (
            ("html comment closure", "- warrant: plan-gap \u2014 cancellation path. closed: <!-- -->", False),
            ("zero-width closure", "- warrant: plan-gap \u2014 cancellation path. closed: \u200b", False),
            ("false denies the closure", "- warrant: plan-gap \u2014 cancellation path. closed: false", False),
            ("null is the same non-answer as nil", "- warrant: plan-gap \u2014 cancellation path. closed: null", False),
            # Controls: substantive free prose is taken as written, including wording the placeholder scan knows.
            ("short specific closure", "- warrant: plan-gap \u2014 cancellation path. closed: repaired by WP1b", True),
            (
                "closure naming the missing AC",
                "- warrant: plan-gap \u2014 cancellation path. closed: WP1b adds the missing cancellation AC",
                True,
            ),
            # A comment beside real prose only drops the part that renders nothing.
            (
                "commented aside beside real prose",
                "- warrant: plan-gap \u2014 cancellation path. closed: repaired by WP1b <!-- see thread -->",
                True,
            ),
        ):
            with self.subTest(closure=label):
                result = self.run_with_plan_gaps(body)
                if expect_ok:
                    self.assertEqual(0, result.returncode, result.stdout + result.stderr)
                else:
                    self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validate_package_complete_rejects_placeholder_plan_gap_closure(self) -> None:
        for label, body in (
            ("todo marker", "- warrant: plan-gap \u2014 cancellation path. closed: TODO"),
            ("placeholder closure", "- warrant: plan-gap \u2014 cancellation path. closed: TBD"),
            ("bare affirmation", "- warrant: plan-gap \u2014 cancellation path. closed: yes"),
            ("bare denial", "- warrant: plan-gap \u2014 cancellation path. closed: no"),
            ("bare completion claim", "- warrant: plan-gap \u2014 cancellation path. closed: done"),
            # Case folding: an upper-case non-answer is the same non-answer.
            ("bare non-answer upper case", "- warrant: plan-gap \u2014 cancellation path. closed: N/A"),
            # Terminator folding: normalization strips a trailing period, so "Pending." is still contentless.
            ("bare non-answer with terminator", "- warrant: plan-gap \u2014 cancellation path. closed: Pending."),
            ("empty closure", "- warrant: plan-gap \u2014 cancellation path. closed:"),
            # Punctuation-only closure: the captured value normalises to nothing, so it records nothing.
            ("punctuation-only closure", "- warrant: plan-gap \u2014 cancellation path. closed: --"),
            ("period-only closure", "- warrant: plan-gap \u2014 cancellation path. closed: ."),
            ("approval alone", "- warrant: plan-gap \u2014 cancellation path. Approved by user."),
            # The gap description is free prose and must never decide the gate. An open entry whose wording
            # happens to contain "none" is still open; only a `- none` disposition clears the section.
            ("open entry whose text contains none", "- warrant: plan-gap \u2014 none of the cancellation paths are covered"),
            # Near-miss tokens must not read as a closure route.
            ("disclosed is not closed", "- warrant: plan-gap \u2014 cancellation path. disclosed: to the user"),
            ("unclosed is not closed", "- warrant: plan-gap \u2014 cancellation path. unclosed: still pending"),
            (
                "approval and provenance but no scope",
                "- warrant: plan-gap \u2014 cancellation path. Approved by user; provenance: plan gate 2026-08-16.",
            ),
            # Discriminating case for the unresolved-marker branch, scoped to the closure value: a closure that
            # admits the gap is still open contradicts itself. Only the marker scan catches it.
            (
                "closure that is still open",
                "- warrant: plan-gap \u2014 cancellation path. closed: repaired by WP1b but still open",
            ),
            # Every closure on the entry must hold: a real one must not launder a contentless second one.
            (
                "one real and one contentless closure",
                "- warrant: plan-gap \u2014 two omissions. closed: repaired by WP1b; closed: TBD",
            ),
            # A single open entry alongside a closed one must still fail: every entry is checked.
            (
                "second entry still open",
                "- warrant: plan-gap \u2014 cancellation path. closed: repaired by WP1b\n"
                "- warrant: plan-gap \u2014 retry budget is not on the frozen checklist",
            ),
        ):
            with self.subTest(shape=label):
                result = self.run_with_plan_gaps(body)
                self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)


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
