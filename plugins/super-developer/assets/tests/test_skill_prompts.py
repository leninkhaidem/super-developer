from __future__ import annotations

from pathlib import Path
import unittest


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
CODE_DOC_SKILL = PLUGIN_ROOT / "skills" / "code-doc" / "SKILL.md"
CODE_DOC_UPDATE_MERGE = PLUGIN_ROOT / "skills" / "code-doc" / "references" / "update-merge.md"
REVIEW_CODE_SKILL = PLUGIN_ROOT / "skills" / "review-code" / "SKILL.md"
REVIEW_CODE_PIPELINE_REPORT = PLUGIN_ROOT / "skills" / "review-code" / "references" / "pipeline-report.md"
REVIEW_CODE_REPORT_TEMPLATE = PLUGIN_ROOT / "skills" / "review-code" / "references" / "report-template.md"
REVIEW_CODE_PIPELINE_ACTIONS = PLUGIN_ROOT / "skills" / "review-code" / "references" / "pipeline-actions.md"
REVIEW_CODE_FIX_VERIFICATION = PLUGIN_ROOT / "skills" / "review-code" / "references" / "fix-verification.md"
README = PLUGIN_ROOT / "README.md"


class CodeDocSkillPromptTests(unittest.TestCase):
    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def code_doc_readme_row(self) -> str:
        for line in self.read_text(README).splitlines():
            if line.startswith("| **code-doc** |"):
                return line
        self.fail("README is missing the code-doc skill row")

    def test_code_doc_uses_handoff_instead_of_auto_commit(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        self.assertIn("### Step 8 — Review & Handoff", skill)
        self.assertIn(
            "Never run `git add`, `git commit`, or `git add .` automatically.",
            skill,
        )
        self.assertIn("If the user explicitly approves a commit", skill)
        self.assertNotIn("### Step 8 — Review & Commit", skill)
        self.assertNotIn("Stage and commit:", skill)

    def test_code_doc_excludes_transient_artifacts_from_default_commit(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        self.assertIn("Clean transient analysis artifacts first", skill)
        self.assertIn("verify `.codedoc/` is absent", skill)
        self.assertIn("Exclude `.codedoc/` always", skill)
        self.assertIn("Exclude `.docs-archive/` by default", skill)
        self.assertIn("never broad `git add .`", skill)
        self.assertIn("Prefer adding `.codedoc/` to\n`.git/info/exclude`", skill)
        self.assertIn("only modify project `.gitignore` if the user explicitly", skill)

    def test_update_merge_archive_policy_requires_explicit_approval(self) -> None:
        reference = self.read_text(CODE_DOC_UPDATE_MERGE)

        self.assertIn("### Archive Handoff Policy", reference)
        self.assertIn("exclude it from the proposed commit", reference)
        self.assertIn("user explicitly approves committing the archive", reference)

    def test_code_doc_stops_before_degraded_docs(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        self.assertIn("Do not append Known Issues or proceed with degraded docs", skill)
        self.assertIn("until the\nuser explicitly approves", skill)

    def test_code_doc_protects_human_readme_by_default(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)
        reference = self.read_text(CODE_DOC_UPDATE_MERGE)

        self.assertIn("Do not blindly overwrite", skill)
        self.assertIn("Never blindly overwrite", reference)
        for text in (skill, reference):
            self.assertIn("missing, tiny/template-like", text)
            self.assertIn("already code-doc-generated", text)
            self.assertIn("explicitly approved", text)
        self.assertIn("Protected core target", skill)
        self.assertIn("conditional writer", skill)
        self.assertIn("Spawn the README writer only if README is missing", skill)
        self.assertNotIn("Core writers always spawn (README", skill)
        self.assertNotIn("**Core documents** (always generated)", skill)
        self.assertIn("optionally propose a small\nlink section", skill)
        self.assertIn("propose (do not apply) an optional link section", reference)

    def test_code_doc_update_mode_does_not_use_readme_line_count_heuristic(self) -> None:
        reference = self.read_text(CODE_DOC_UPDATE_MERGE)

        self.assertIn("Apply README protection criteria, not line count", reference)
        self.assertIn("Preserve short but meaningful human READMEs", reference)
        self.assertNotIn("If >50 lines", reference)
        self.assertNotIn("If <50 lines", reference)

    def test_code_doc_stateless_prompts_are_self_contained(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        writer_context = (
            "Confirmed doc plan",
            "Update mode (`Fresh`, `Regenerate`, or `Augment`)",
            "Protected paths, README protection decision",
            "Target audience, tone/style",
            "Frontmatter/metadata schema",
            "Secret redaction rules",
            "Source/path citation expectations",
            "No-placeholder rule",
            "native extractor report/status summary",
            "synthesis summary",
        )
        analyst_context = (
            "confirmed doc plan",
            "assigned `.codedoc/{name}-analysis.md` path",
            "protected paths, README protection decision",
            "Native extractor context",
            "Citation/confidence protocol",
            "Source/path evidence requirements",
            "Output/report structure",
        )
        reviewer_context = (
            "generated/modified doc paths",
            "Frontmatter/metadata expectations",
            "augmentation_mode: true",
            "Secret redaction rules",
            "Native extractor report/status summary",
            "Citation/confidence protocol",
            "Source/path evidence requirements",
            "Output/report structure",
        )

        for required_context in writer_context + analyst_context + reviewer_context:
            self.assertIn(required_context, skill)

    def test_code_doc_persists_extractor_transparency_before_cleanup(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        self.assertIn("Treat `.codedoc/native-extractors/*` as transient", skill)
        self.assertIn("before cleanup, copy extractor status/transparency", skill)
        self.assertIn("Persist native extractor transparency", skill)

    def test_code_doc_secret_redaction_rules(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        self.assertIn("### Secret Redaction Rules", skill)
        self.assertIn("never expose secret values, tokens, credentials", skill)
        self.assertIn("document only variable names, purpose", skill)
        self.assertIn("Redact observed values as `<redacted>`", skill)
        self.assertIn("flag\nsuspected secrets for user handling", skill)

    def test_code_doc_structures_analyst_and_reviewer_outputs(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        self.assertIn("Cite source paths", skill)
        self.assertIn("include confidence (`high`/`medium`/`low`)", skill)
        self.assertIn("confidence (`high`/`medium`/`low`)", skill)
        for required_field in (
            "severity",
            "affected doc",
            "claim being challenged",
            "evidence\npath/source",
            "recommended fix",
        ):
            self.assertIn(required_field, skill)

    def test_code_doc_project_hash_fallback_wording_is_consistent(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)
        reference = self.read_text(CODE_DOC_UPDATE_MERGE)

        for text in (skill, reference):
            self.assertIn("short git", text)
            self.assertIn("uncommitted", text)
            self.assertIn("no-git", text)
        self.assertNotIn("project_hash: {git SHA or \"uncommitted\"}", reference)

    def test_code_doc_reports_native_extractor_transparency(self) -> None:
        skill = self.read_text(CODE_DOC_SKILL)

        self.assertIn(".codedoc/native-extractors/report.md", skill)
        for status in ("attempted", "ran", "failed", "skipped"):
            self.assertIn(status, skill)
        self.assertIn("command, output path, and failure/skip reason", skill)
        self.assertIn("Native extractor transparency", skill)
        self.assertIn("commands, output paths, and reasons", skill)

    def test_readme_matches_code_doc_handoff_and_current_catalog(self) -> None:
        row = self.code_doc_readme_row()

        self.assertIn("Review & Handoff", row)
        self.assertIn("Never auto-commits", row)
        for current_artifact in (
            "navigation",
            "patterns",
            "config",
            "errors",
            "flows",
            "boundaries",
            "inventory",
            "security",
        ):
            self.assertIn(current_artifact, row)
        for stale_artifact in (
            "api-reference",
            "data-model",
            "component-guide",
            "infrastructure",
        ):
            self.assertNotIn(stale_artifact, row)



class ReviewCodePromptCompressionTests(unittest.TestCase):
    def read_text(self, path: Path) -> str:
        return path.read_text(encoding="utf-8")

    def test_pipeline_clean_path_defers_fix_path_reference(self) -> None:
        skill = self.read_text(REVIEW_CODE_SKILL)
        template = self.read_text(REVIEW_CODE_REPORT_TEMPLATE)
        report = self.read_text(REVIEW_CODE_PIPELINE_REPORT)
        actions = self.read_text(REVIEW_CODE_PIPELINE_ACTIONS)

        self.assertIn("`references/pipeline-report.md`", skill)
        self.assertIn("Load `references/pipeline-actions.md`\n  only after **ISSUES FOUND**", skill)
        self.assertIn("Pipeline context: values come from `pipeline-report.md`.", template)
        self.assertNotIn("Pipeline context: values come from `pipeline-actions.md`.", template)
        self.assertIn("Do not load\nfix implementer packets, dirty-proof handling, widening rules", report)
        self.assertIn("Clean reviews stop at `pipeline-report.md`", actions)
        self.assertIn("clean-path stale-state/audit-readiness gate", actions)

    def test_pipeline_clean_path_keeps_non_bypass_gates_visible(self) -> None:
        skill = self.read_text(REVIEW_CODE_SKILL)
        report = self.read_text(REVIEW_CODE_PIPELINE_REPORT)

        self.assertIn("baseline security/privacy/safety sniff", skill)
        self.assertIn("Blanket\nmode cannot skip, silence, or replace this sniff", skill)
        self.assertIn("Serious findings require Skeptic verification", skill)
        self.assertIn("Blanket mode cannot bypass", skill)
        self.assertIn("baseline\n  security/privacy/safety sniff", report)
        self.assertIn("Stale-State Gate for Clean Readiness", report)
        self.assertIn("Clean\nreview-code output is not package proof", report)

    def test_fix_verification_owns_widening_and_non_closed_routing(self) -> None:
        actions = self.read_text(REVIEW_CODE_PIPELINE_ACTIONS)
        verification = self.read_text(REVIEW_CODE_FIX_VERIFICATION)

        self.assertIn("canonical owner for fix-verification closure verdicts", verification)
        self.assertIn("## Non-Closed Routing and Strategy Changes", verification)
        self.assertIn("## Widening Trigger Names", verification)
        self.assertIn("Do not repeat the same fix or review prompt with more tokens", verification)
        self.assertIn("Pipeline keeps only this safety kernel", actions)
        self.assertNotIn("| Same dedupe key remains", actions)
        self.assertNotIn("- `scope_expansion` —", actions)


if __name__ == "__main__":
    unittest.main()
