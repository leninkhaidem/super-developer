from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ASSETS_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ASSETS_DIR))
import semgrep_rules  # noqa: E402


class FakeSemgrepRunner:
    def __init__(self, raw: dict | None = None, returncode: int = 0, stderr: str = "") -> None:
        self.raw = raw if raw is not None else {"results": [], "errors": []}
        self.returncode = returncode
        self.stderr = stderr
        self.calls: list[dict] = []

    def __call__(self, argv, **kwargs):
        self.calls.append({"argv": argv, "kwargs": kwargs})
        output = Path(argv[argv.index("--output") + 1])
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps(self.raw), encoding="utf-8")
        return subprocess.CompletedProcess(argv, self.returncode, stdout="", stderr=self.stderr)


class SemgrepRulesFixture:
    def __init__(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.rules_root = self.root / "plugin" / ".cache" / "semgrep-rules" / "community"
        self.index_path = self.root / "plugin" / ".cache" / "semgrep-rules" / "index.json"
        self.repo.mkdir()
        self.rules_root.mkdir(parents=True)
        self.target = self.repo / "target"
        self.target.mkdir()
        self.fake_semgrep = self.root / "semgrep"
        self.fake_semgrep.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        self.fake_semgrep.chmod(0o755)

    def cleanup(self) -> None:
        self.tmp.cleanup()

    def write_rule(self, rel: str, *, language: str = "python", rule_id: str = "python.security.demo", metadata: str = "technology: [django]") -> Path:
        path = self.rules_root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        metadata_block = "\n".join(f"      {line}" for line in metadata.splitlines())
        path.write_text(
            f"rules:\n"
            f"  - id: {rule_id}\n"
            f"    pattern: $X\n"
            f"    message: demo finding\n"
            f"    languages: [{language}]\n"
            f"    severity: WARNING\n"
            f"    metadata:\n"
            f"{metadata_block}\n",
            encoding="utf-8",
        )
        return path

    def evidence_paths(self, stem: str = "WP2") -> tuple[Path, Path]:
        return (
            self.repo / ".tasks" / "feature" / "semgrep" / f"{stem}.semgrep.json",
            self.repo / ".tasks" / "feature" / "semgrep" / f"{stem}.semgrep-summary.json",
        )

    def parse(self, argv: list[str]):
        return semgrep_rules.build_parser().parse_args(argv)

    def run(self, argv: list[str], *, runner=None) -> tuple[int, str, str]:
        args = self.parse(argv)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            try:
                if runner is not None and args.command == "scan":
                    code = semgrep_rules.command_scan(args, runner=runner)
                else:
                    code = args.func(args)
            except semgrep_rules.HelperError as exc:
                print(f"error: {exc}", file=sys.stderr)
                code = 2
        return code, stdout.getvalue(), stderr.getvalue()

    def index(self) -> dict:
        code, stdout, stderr = self.run(
            [
                "index",
                "--rules-root",
                str(self.rules_root),
                "--index",
                str(self.index_path),
            ]
        )
        if code != 0:
            raise AssertionError(stderr)
        return json.loads(stdout)

    def retrieve(self, *stacks: str) -> Path:
        profile = self.repo / ".superdeveloper" / "semgrep" / "stack-profile.yml"
        argv = [
            "retrieve",
            "--index",
            str(self.index_path),
            "--rules-root",
            str(self.rules_root),
            "--write-profile",
            str(profile),
            "--repo-root",
            str(self.repo),
        ]
        for stack in stacks:
            argv.extend(["--stack", stack])
        code, _stdout, stderr = self.run(argv)
        if code != 0:
            raise AssertionError(stderr)
        return profile

    def scan_argv(self, profile: Path, raw: Path, summary: Path, *extra: str) -> list[str]:
        return [
            "scan",
            "--profile",
            str(profile),
            "--target",
            str(self.target),
            "--json-output",
            str(raw),
            "--summary-output",
            str(summary),
            "--semgrep-bin",
            str(self.fake_semgrep),
            "--repo-root",
            str(self.repo),
            *extra,
        ]


class SemgrepRulesTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = SemgrepRulesFixture()

    def tearDown(self) -> None:
        self.fixture.cleanup()

    def test_index_discovers_semgrep_yaml_and_extracts_languages_metadata(self) -> None:
        self.fixture.write_rule("python/django/rule.yml", language="python", metadata="technology: [django]\ncwe: [CWE-79]")
        self.fixture.write_rule("terraform/aws/rule.yaml", language="terraform", rule_id="terraform.aws.demo", metadata="category: security")

        result = self.fixture.index()
        index = json.loads(self.fixture.index_path.read_text(encoding="utf-8"))

        self.assertEqual(result["rule_files"], 2)
        self.assertEqual(index["freshness"]["source"], "content-fingerprint")
        python_entry = next(item for item in index["files"] if item["path"] == "python/django/rule.yml")
        self.assertEqual(python_entry["languages"], ["python"])
        self.assertIn("django", python_entry["metadata_terms"])
        self.assertIn("CWE-79", python_entry["metadata_terms"])

    def test_index_uses_git_commit_or_content_fingerprint_for_freshness(self) -> None:
        self.fixture.write_rule("python/rule.yml")
        git_dir = self.fixture.rules_root / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        ref = git_dir / "refs" / "heads" / "main"
        ref.parent.mkdir(parents=True)
        commit = "0123456789abcdef0123456789abcdef01234567"
        ref.write_text(commit + "\n", encoding="utf-8")

        self.fixture.index()
        index = json.loads(self.fixture.index_path.read_text(encoding="utf-8"))
        self.assertEqual(index["freshness"]["community_rules_commit"], commit)
        self.assertEqual(index["freshness"]["source"], "git-commit")

        # Without git metadata, content changes are represented by the content fingerprint.
        other = SemgrepRulesFixture()
        try:
            other.write_rule("python/rule.yml")
            other.index()
            first = json.loads(other.index_path.read_text(encoding="utf-8"))["freshness"]["content_fingerprint"]
            other.write_rule("python/rule.yml", rule_id="python.security.changed")
            other.index()
            second = json.loads(other.index_path.read_text(encoding="utf-8"))["freshness"]["content_fingerprint"]
            self.assertNotEqual(first, second)
        finally:
            other.cleanup()

    def test_retrieve_writes_absolute_profile_for_multiple_stacks_and_detects_stale_index(self) -> None:
        self.fixture.write_rule("python/django/rule.yml", language="python", metadata="technology: [django]")
        self.fixture.write_rule("terraform/aws/rule.yml", language="terraform", rule_id="terraform.aws.demo")
        self.fixture.index()

        profile = self.fixture.retrieve("python", "terraform")
        profile_data = semgrep_rules._load_yaml(profile, label="profile")

        self.assertEqual(profile_data["version"], 1)
        self.assertTrue(Path(profile_data["stacks"]["python"]["semgrep-configs"][0]).is_absolute())
        self.assertTrue(Path(profile_data["stacks"]["terraform"]["semgrep-configs"][0]).is_absolute())
        old_fingerprint = profile_data["rules-index"]["content-fingerprint"]

        self.fixture.write_rule("python/django/new.yml", language="python", rule_id="python.security.new")
        code, _stdout, stderr = self.fixture.run(
            [
                "retrieve",
                "--index",
                str(self.fixture.index_path),
                "--rules-root",
                str(self.fixture.rules_root),
                "--stack",
                "python",
                "--repo-root",
                str(self.fixture.repo),
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("stale", stderr)

        self.fixture.index()
        profile = self.fixture.retrieve("python")
        refreshed = semgrep_rules._load_yaml(profile, label="profile")
        self.assertNotEqual(old_fingerprint, refreshed["rules-index"]["content-fingerprint"])

    def test_retrieve_reports_missing_index_and_uses_generic_matching(self) -> None:
        self.fixture.write_rule("python/rule.yml")
        code, _stdout, stderr = self.fixture.run(
            [
                "retrieve",
                "--index",
                str(self.fixture.index_path),
                "--rules-root",
                str(self.fixture.rules_root),
                "--stack",
                "python",
                "--repo-root",
                str(self.fixture.repo),
            ]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("index is missing", stderr)
        source = (ASSETS_DIR / "semgrep_rules.py").read_text(encoding="utf-8")
        self.assertNotIn("STACK_MAP", source)
        self.assertNotIn("CURATED", source)

    def test_scan_invokes_structured_privacy_argv_and_writes_raw_summary(self) -> None:
        self.fixture.write_rule("python/rule.yml")
        self.fixture.index()
        profile = self.fixture.retrieve("python")
        excluded = self.fixture.repo / ".superdeveloper" / "semgrep" / "excluded-rules.yml"
        excluded.write_text("excluded-rules:\n  - id: python.security.demo\n    reason: test\n", encoding="utf-8")
        local_rules = self.fixture.repo / ".superdeveloper" / "semgrep" / "local-rules.yml"
        local_rules.write_text("rules:\n  - id: project.python.local\n    pattern: $X\n    message: local\n    languages: [python]\n    severity: ERROR\n", encoding="utf-8")
        raw, summary = self.fixture.evidence_paths("WP2")
        raw_payload = {
            "results": [
                {
                    "check_id": "python.security.demo",
                    "path": "target/app.py",
                    "start": {"line": 2, "col": 1},
                    "extra": {"severity": "ERROR", "message": "bad thing", "fingerprint": "abc"},
                }
            ],
            "errors": [],
        }
        fake = FakeSemgrepRunner(raw_payload)

        code, stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, raw, summary, "--excluded-rules", str(excluded), "--local-rules", str(local_rules)),
            runner=fake,
        )

        self.assertEqual(code, 0, stderr)
        call = fake.calls[0]
        argv = call["argv"]
        self.assertFalse(call["kwargs"].get("shell"))
        self.assertEqual(argv[1], "scan")
        self.assertIn("--metrics=off", argv)
        self.assertIn("--disable-version-check", argv)
        self.assertEqual(argv.count("--config"), 2)
        self.assertIn(str(local_rules.resolve()), argv)
        self.assertIn("--exclude-rule", argv)
        self.assertIn("python.security.demo", argv)
        self.assertIn("--json", argv)
        self.assertEqual(Path(argv[argv.index("--output") + 1]), raw)
        summary_data = json.loads(summary.read_text(encoding="utf-8"))
        self.assertEqual(summary_data["result_count"], 1)
        self.assertEqual(summary_data["severity_counts"], {"ERROR": 1})
        self.assertEqual(summary_data["raw_digest"], semgrep_rules._sha256_file(raw))
        self.assertRegex(summary_data["summary_digest"], r"^[0-9a-f]{64}$")
        self.assertIn("Semgrep scan complete", stdout)

        integration_raw, integration_summary = self.fixture.evidence_paths("integration")
        fake_integration = FakeSemgrepRunner({"results": [], "errors": []})
        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, integration_raw, integration_summary, "--excluded-rules", str(excluded), "--local-rules", str(local_rules)),
            runner=fake_integration,
        )
        self.assertEqual(code, 0, stderr)
        self.assertTrue(integration_raw.exists())
        self.assertEqual(json.loads(integration_summary.read_text(encoding="utf-8"))["result_count"], 0)

    def test_scan_rejects_registry_url_relative_missing_and_shell_like_configs(self) -> None:
        self.fixture.write_rule("python/rule.yml")
        self.fixture.index()
        profile = self.fixture.retrieve("python")
        profile_data = semgrep_rules._load_yaml(profile, label="profile")
        raw, summary = self.fixture.evidence_paths("WP2")
        bad_configs = ["auto", "p/python", "r/python", "https://semgrep.dev/p/python", "relative.yml", str(self.fixture.root / "missing.yml"), "/tmp/good;rm"]
        for bad_config in bad_configs:
            with self.subTest(bad_config=bad_config):
                mutated = profile_data.copy()
                mutated["stacks"] = {"python": {"semgrep-configs": [bad_config]}}
                semgrep_rules._write_yaml(profile, mutated)
                code, _stdout, stderr = self.fixture.run(self.fixture.scan_argv(profile, raw, summary), runner=FakeSemgrepRunner())
                self.assertNotEqual(code, 0)
                self.assertTrue(any(word in stderr for word in ["local", "exist", "separator", "absolute"]))
        self.fixture.index()
        profile = self.fixture.retrieve("python")
        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, raw, summary, "--target", "../outside"), runner=FakeSemgrepRunner()
        )
        self.assertNotEqual(code, 0)
        self.assertIn("traversal", stderr)

    def test_scan_rejects_unsafe_excludes_malformed_yamls_modes_and_bad_evidence_paths(self) -> None:
        self.fixture.write_rule("python/rule.yml")
        self.fixture.index()
        profile = self.fixture.retrieve("python")
        raw, summary = self.fixture.evidence_paths("WP2")
        excluded = self.fixture.repo / ".superdeveloper" / "semgrep" / "excluded-rules.yml"
        excluded.write_text("excluded-rules:\n  - id: 'bad;rm'\n", encoding="utf-8")
        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, raw, summary, "--excluded-rules", str(excluded)), runner=FakeSemgrepRunner()
        )
        self.assertNotEqual(code, 0)
        self.assertIn("unsafe", stderr + _stdout)

        excluded.write_text("excluded-rules: [", encoding="utf-8")
        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, raw, summary, "--excluded-rules", str(excluded)), runner=FakeSemgrepRunner()
        )
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid excluded rules YAML", stderr)

        bad_profile = profile.with_name("bad-stack-profile.yml")
        bad_profile.write_text("version: [", encoding="utf-8")
        code, _stdout, stderr = self.fixture.run(self.fixture.scan_argv(bad_profile, raw, summary), runner=FakeSemgrepRunner())
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid stack profile YAML", stderr)

        local_rules = self.fixture.repo / ".superdeveloper" / "semgrep" / "local-rules.yml"
        local_rules.write_text("rules: [", encoding="utf-8")
        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, raw, summary, "--local-rules", str(local_rules)), runner=FakeSemgrepRunner()
        )
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid local rules YAML", stderr)

        local_rules.unlink()
        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, raw, summary, "--semgrep-bin", "semgrep ci"), runner=FakeSemgrepRunner()
        )
        self.assertNotEqual(code, 0)
        self.assertIn("semgrep ci", stderr)

        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, raw, summary, "--semgrep-bin", str(self.fixture.root / "missing-semgrep")),
            runner=FakeSemgrepRunner(),
        )
        self.assertNotEqual(code, 0)
        self.assertIn("executable is missing", stderr)

        outside_raw = self.fixture.repo / ".superdeveloper" / "WP2.semgrep.json"
        code, _stdout, stderr = self.fixture.run(self.fixture.scan_argv(profile, outside_raw, summary), runner=FakeSemgrepRunner())
        self.assertNotEqual(code, 0)
        self.assertIn(".tasks/<feature>/semgrep", stderr)

        mismatch_summary = self.fixture.repo / ".tasks" / "feature" / "semgrep" / "WP3.semgrep-summary.json"
        code, _stdout, stderr = self.fixture.run(self.fixture.scan_argv(profile, raw, mismatch_summary), runner=FakeSemgrepRunner())
        self.assertNotEqual(code, 0)
        self.assertIn("share feature and stem", stderr)

    def test_scan_rejects_symlink_escapes_and_reports_nonzero_semgrep_without_fake_success(self) -> None:
        self.fixture.write_rule("python/rule.yml")
        self.fixture.index()
        profile = self.fixture.retrieve("python")
        raw, summary = self.fixture.evidence_paths("WP2")
        raw.parent.mkdir(parents=True)
        outside = self.fixture.root / "outside"
        outside.mkdir()
        symlink_raw = raw.parent / "WP3.semgrep.json"
        symlink_raw.symlink_to(outside / "WP3.semgrep.json")
        code, _stdout, stderr = self.fixture.run(
            self.fixture.scan_argv(profile, symlink_raw, raw.parent / "WP3.semgrep-summary.json"), runner=FakeSemgrepRunner()
        )
        self.assertNotEqual(code, 0)
        self.assertIn("symlink", stderr)

        fake = FakeSemgrepRunner({"results": [], "errors": [{"message": "parse error"}]}, returncode=3, stderr="fatal")
        code, _stdout, stderr = self.fixture.run(self.fixture.scan_argv(profile, raw, summary), runner=fake)
        self.assertNotEqual(code, 0)
        self.assertTrue(summary.exists())
        self.assertIn("exit code 3", stderr)
        self.assertIn("semgrep exited with code 3", summary.read_text(encoding="utf-8"))

    def write_raw(self, raw: Path, payload: dict) -> None:
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text(json.dumps(payload), encoding="utf-8")

    def test_summarize_produces_bounded_counts_errors_top_groups_and_digests(self) -> None:
        raw, summary = self.fixture.evidence_paths("WP2")
        self.write_raw(
            raw,
            {
                "results": [
                    {"check_id": "rule.a", "path": "target/a.py", "start": {"line": 1}, "extra": {"severity": "ERROR", "message": "A"}},
                    {"check_id": "rule.a", "path": "target/b.py", "start": {"line": 2}, "extra": {"severity": "WARNING", "message": "B"}},
                ],
                "errors": [{"message": "scan warning"}],
            },
        )
        code, stdout, stderr = self.fixture.run(
            ["summarize", "--json-output", str(raw), "--summary-output", str(summary), "--repo-root", str(self.fixture.repo)]
        )
        self.assertEqual(code, 0, stderr)
        data = json.loads(stdout)
        self.assertEqual(data["result_count"], 2)
        self.assertEqual(data["severity_counts"], {"ERROR": 1, "WARNING": 1})
        self.assertEqual(data["top_rules"][0], {"rule_id": "rule.a", "count": 2})
        self.assertEqual(data["top_path_groups"][0], {"path_group": "target", "count": 2})
        self.assertEqual(data["scan_errors"], ["scan warning"])
        self.assertEqual(data["raw_digest"], semgrep_rules._sha256_file(raw))
        self.assertRegex(data["summary_digest"], r"^[0-9a-f]{64}$")

    def test_list_findings_filters_limits_stable_refs_and_validates_stale_summary(self) -> None:
        raw, summary = self.fixture.evidence_paths("WP2")
        self.write_raw(
            raw,
            {
                "results": [
                    {"check_id": "rule.a", "path": "target/a.py", "start": {"line": 1}, "extra": {"severity": "ERROR", "message": "first\nline", "fingerprint": "fp-a"}},
                    {"check_id": "rule.b", "path": "target/b.py", "start": {"line": 5}, "extra": {"severity": "WARNING", "message": "second", "fingerprint": "fp-b"}},
                ]
            },
        )
        code, _stdout, stderr = self.fixture.run(
            ["summarize", "--json-output", str(raw), "--summary-output", str(summary), "--repo-root", str(self.fixture.repo)]
        )
        self.assertEqual(code, 0, stderr)
        code, stdout, stderr = self.fixture.run(
            ["list-findings", "--json-output", str(raw), "--severity", "ERROR", "--limit", "1", "--repo-root", str(self.fixture.repo)]
        )
        self.assertEqual(code, 0, stderr)
        data = json.loads(stdout)
        self.assertEqual(data["total_matching"], 1)
        self.assertEqual(data["findings"][0]["ref"], "F001")
        self.assertEqual(data["findings"][0]["location"], "target/a.py:1")
        self.assertEqual(data["findings"][0]["message"], "first")
        self.assertEqual(data["findings"][0]["fingerprint"], "fp-a")

        self.write_raw(raw, {"results": []})
        code, _stdout, stderr = self.fixture.run(
            ["list-findings", "--json-output", str(raw), "--repo-root", str(self.fixture.repo)]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("summary/raw digest mismatch", stderr)

    def test_show_finding_returns_one_detail_metadata_and_confined_context(self) -> None:
        source = self.fixture.target / "app.py"
        source.write_text("one\ntwo\nthree\nfour\n", encoding="utf-8")
        raw, summary = self.fixture.evidence_paths("WP2")
        self.write_raw(
            raw,
            {
                "results": [
                    {
                        "check_id": "rule.a",
                        "path": "app.py",
                        "start": {"line": 3, "col": 2},
                        "extra": {
                            "severity": "ERROR",
                            "message": "detail message",
                            "fingerprint": "fp-a",
                            "metadata": {"cwe": ["CWE-79"], "owasp": ["A03"], "unexpected": {"huge": "ignored"}},
                        },
                    }
                ]
            },
        )
        code, _stdout, stderr = self.fixture.run(
            [
                "summarize",
                "--json-output",
                str(raw),
                "--summary-output",
                str(summary),
                "--target",
                str(self.fixture.target),
                "--repo-root",
                str(self.fixture.repo),
            ]
        )
        self.assertEqual(code, 0, stderr)
        code, stdout, stderr = self.fixture.run(
            [
                "show-finding",
                "--json-output",
                str(raw),
                "--finding",
                "fp-a",
                "--context-lines",
                "1",
                "--repo-root",
                str(self.fixture.repo),
            ]
        )
        self.assertEqual(code, 0, stderr)
        detail = json.loads(stdout)["finding"]
        self.assertEqual(detail["ref"], "F001")
        self.assertEqual(detail["location"], "app.py:3:2")
        self.assertEqual(detail["metadata"], {"cwe": ["CWE-79"], "owasp": ["A03"]})
        self.assertEqual([line["line"] for line in detail["context"]], [2, 3, 4])

        self.write_raw(raw, {"results": [{"check_id": "rule.escape", "path": "../secret.txt", "start": {"line": 1}, "extra": {"severity": "ERROR", "message": "x"}}]})
        self.fixture.run(["summarize", "--json-output", str(raw), "--summary-output", str(summary), "--target", str(self.fixture.target), "--repo-root", str(self.fixture.repo)])
        code, _stdout, stderr = self.fixture.run(
            ["show-finding", "--json-output", str(raw), "--finding", "F001", "--context-lines", "1", "--repo-root", str(self.fixture.repo)]
        )
        self.assertNotEqual(code, 0)
        self.assertIn("traversal", stderr)

    def test_consumption_rejects_invalid_json_oversized_counts_and_sanitizes_hostile_strings(self) -> None:
        raw, summary = self.fixture.evidence_paths("WP2")
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_text("{not json", encoding="utf-8")
        code, _stdout, stderr = self.fixture.run(["summarize", "--json-output", str(raw), "--summary-output", str(summary), "--repo-root", str(self.fixture.repo)])
        self.assertNotEqual(code, 0)
        self.assertIn("Invalid JSON", stderr)

        self.write_raw(raw, {"results": [{} for _ in range(semgrep_rules.MAX_RESULTS + 1)]})
        code, _stdout, stderr = self.fixture.run(["summarize", "--json-output", str(raw), "--summary-output", str(summary), "--repo-root", str(self.fixture.repo)])
        self.assertNotEqual(code, 0)
        self.assertIn("oversized", stderr)

        self.write_raw(
            raw,
            {
                "results": [
                    {
                        "check_id": "rule.ctrl",
                        "path": "target/evil.py\x00",
                        "start": {"line": "not-int"},
                        "extra": {"severity": "error", "message": "bad\x00message" + "x" * 2000, "metadata": ["unexpected"]},
                    }
                ]
            },
        )
        code, stdout, stderr = self.fixture.run(
            ["list-findings", "--json-output", str(raw), "--repo-root", str(self.fixture.repo)]
        )
        self.assertEqual(code, 0, stderr)
        finding = json.loads(stdout)["findings"][0]
        self.assertEqual(finding["ref"], "F001")
        self.assertNotIn("\x00", finding["location"])
        self.assertIn("<truncated>", finding["message"])

    def test_static_inspection_no_network_fetch_no_registry_fallback_no_blocker_mapping(self) -> None:
        source = (ASSETS_DIR / "semgrep_rules.py").read_text(encoding="utf-8")
        forbidden = ["git clone", "git pull", "requests.", "urllib.request", "shell=True", "--config auto", "Super Developer BLOCKER"]
        for token in forbidden:
            self.assertNotIn(token, source)
        self.assertIn("--metrics=off", source)
        self.assertIn("--disable-version-check", source)
        self.assertIn("semgrep_severity_is_advisory", source)


if __name__ == "__main__":
    unittest.main()
