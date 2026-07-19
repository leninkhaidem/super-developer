from __future__ import annotations

import json
import re
import subprocess
import tempfile
import unittest
from pathlib import Path


PLUGIN_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = PLUGIN_ROOT.parents[1]
CANONICAL_SCAN = 'python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/semgrep_rules.py" scan'
STALE_PREF_PATH = ".superdeveloper/model-preferences.yml"
CURRENT_PREF_PATH = ".superdeveloper/preferences.yml"


def read_repo(path: str) -> str:
    return (REPO_ROOT / path).read_text(encoding="utf-8")


def prompt_surface_paths() -> list[Path]:
    paths = [REPO_ROOT / "README.md", PLUGIN_ROOT / "README.md"]
    paths.extend(sorted((PLUGIN_ROOT / "references").glob("*.md")))
    paths.extend(sorted((PLUGIN_ROOT / "skills").glob("**/*.md")))
    return paths


def testing_prompt_surface_paths() -> list[Path]:
    return sorted((PLUGIN_ROOT / "skills" / "testing").glob("**/*.md"))


def context_window(text: str, needle: str, radius: int = 120) -> str:
    index = text.find(needle)
    if index < 0:
        return ""
    start = max(0, index - radius)
    end = min(len(text), index + len(needle) + radius)
    return text[start:end].lower()


def compact_text(text: str) -> str:
    return " ".join(text.split())


class SkillPromptSurfaceTests(unittest.TestCase):
    def test_readmes_document_optional_local_semgrep_lifecycle_without_history(self) -> None:
        root_text = read_repo("README.md")
        for needle in [
            CURRENT_PREF_PATH,
            "disabled by default",
            "clone",
            "git pull --ff-only",
            "shipped helper",
            ".tasks/<feature>/semgrep/",
            "advisory",
            "read-only",
        ]:
            self.assertIn(needle, root_text)
        self.assertNotIn(STALE_PREF_PATH, root_text)

        plugin_text = read_repo("plugins/super-developer/README.md")
        for needle in [
            CURRENT_PREF_PATH,
            ".superdeveloper/semgrep/excluded-rules.yml",
            ".superdeveloper/semgrep/local-rules.yml",
            ".superdeveloper/semgrep/stack-profile.yml",
            "${SUPER_DEVELOPER_PLUGIN_ROOT}/.cache/semgrep-rules/community",
            "clone",
            "git pull --ff-only",
            "disabled by default",
            CANONICAL_SCAN,
            "raw direct `semgrep` scans",
            "summarize",
            "list-findings",
            "show-finding",
            "--expected-summary-digest",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep.json",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep-summary.json",
            ".tasks/<feature>/semgrep/integration.semgrep.json",
            ".tasks/<feature>/semgrep/integration.semgrep-summary.json",
            "raw digest",
            "summary digest",
            "advisory",
            "read-only",
        ]:
            self.assertIn(needle, plugin_text)
        self.assertNotIn(STALE_PREF_PATH, plugin_text)
        self.assertNotIn("--config auto", plugin_text)

    def test_action_point_references_require_wrapper_scan_and_forbid_raw_direct_semgrep(self) -> None:
        action_point_paths = [
            "plugins/super-developer/README.md",
            "plugins/super-developer/references/semgrep.md",
            "plugins/super-developer/references/tool-usage.md",
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md",
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md",
            "plugins/super-developer/skills/implement/references/execution-contract.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/skills/implement/references/package-integration-gates.md",
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/skills/review-code/references/pipeline-report.md",
        ]
        for rel in action_point_paths:
            with self.subTest(path=rel):
                self.assertIn(CANONICAL_SCAN, read_repo(rel))
        for rel in ["plugins/super-developer/README.md", "plugins/super-developer/references/semgrep.md"]:
            with self.subTest(path=rel, option="expected-summary-digest"):
                self.assertIn("--expected-summary-digest", read_repo(rel))

        raw_direct_command = re.compile(r"(?im)(?:^|[`\\s])semgrep\\s+(?:scan|ci)\\b")
        forbidden_helper_internals = ["--config auto", "--metrics=off", "--disable-version-check"]
        for path in prompt_surface_paths():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            self.assertIsNone(raw_direct_command.search(text), rel)
            for token in forbidden_helper_internals:
                self.assertNotIn(token, text, rel)

    def test_preference_path_contract_is_current_and_terse(self) -> None:
        current_path_surfaces = [
            "README.md",
            "CHANGELOG.md",
            "plugins/super-developer/README.md",
            "plugins/super-developer/references/model-preferences.md",
            "plugins/super-developer/references/semgrep.md",
            "plugins/super-developer/skills/conceptualize/SKILL.md",
            "plugins/super-developer/skills/implementation-plan/SKILL.md",
        ]
        for rel in current_path_surfaces:
            self.assertIn(CURRENT_PREF_PATH, read_repo(rel), rel)

        no_history_surfaces = [
            "README.md",
            "CHANGELOG.md",
            "plugins/super-developer/README.md",
            "plugins/super-developer/references/semgrep.md",
            "plugins/super-developer/skills/conceptualize/SKILL.md",
            "plugins/super-developer/skills/implementation-plan/SKILL.md",
        ]
        for rel in no_history_surfaces:
            self.assertNotIn(STALE_PREF_PATH, read_repo(rel), rel)

        model_preferences = read_repo("plugins/super-developer/references/model-preferences.md")
        self.assertNotIn(STALE_PREF_PATH, model_preferences)
        for needle in [
            "design-preflight: adaptive",
            "`design-preflight` — Design Preflight challenger sub-agents.",
            "`models.design-preflight`",
        ]:
            self.assertIn(needle, model_preferences)

        design_preflight = read_repo("plugins/super-developer/skills/implementation-plan/references/design-preflight.md")
        for needle in ["`design-preflight` role", "`models.design-preflight`", "`models.default-model`"]:
            self.assertIn(needle, design_preflight)
        self.assertNotIn("Do not add a Design Preflight-specific model key", design_preflight)
        self.assertNotIn("standard planning/design challengers use the `review-plan` key", design_preflight)

        semgrep_reference = read_repo("plugins/super-developer/references/semgrep.md")
        self.assertIn("Semgrep reads only the `semgrep:` section", semgrep_reference)
        self.assertNotIn("models:", semgrep_reference)
        self.assertNotIn("default-model", semgrep_reference)

        self.assertNotIn("resolve/create", read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md"))

    def test_conceptualize_handoff_resolves_semgrep_before_plan_skill(self) -> None:
        conceptualize = read_repo("plugins/super-developer/skills/conceptualize/SKILL.md")
        conceptualize_compact = compact_text(conceptualize)
        transition = "Before invoking `implementation-plan` from a Conceptualize handoff"
        self.assertIn(transition, conceptualize_compact)
        self.assertIn("parent/main planning", conceptualize_compact)
        self.assertIn(CURRENT_PREF_PATH, conceptualize)
        self.assertIn("Semgrep opt-in/setup", conceptualize_compact)
        self.assertIn("passes resolved Semgrep state", conceptualize_compact)
        self.assertNotIn("dispatch `implementation-plan` via Skill tool/fresh sub-agent", conceptualize)

        handoff = read_repo("plugins/super-developer/skills/conceptualize/references/final-handoff.md")
        handoff_compact = compact_text(handoff)
        self.assertIn("parent/main", handoff)
        self.assertIn("resolves preferences and Semgrep state", handoff_compact)
        self.assertIn("then invokes `implementation-plan`", handoff_compact)

        implementation_plan = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        self.assertIn("do not reopen opt-in", implementation_plan)
        self.assertIn("Only when no resolved Semgrep state is supplied", implementation_plan)
        self.assertIn("treat this as\n  direct invocation", implementation_plan)

    def test_sidecar_only_authority_routes_migration_permission_and_publication_in_order(self) -> None:
        affected = [
            "plugins/super-developer/references/artifact-store.md",
            "plugins/super-developer/references/conceptualize-slice-authority.md",
            "plugins/super-developer/references/tool-usage.md",
            "plugins/super-developer/references/slice-first-artifacts.md",
            "plugins/super-developer/skills/conceptualize/SKILL.md",
            "plugins/super-developer/skills/conceptualize/references/final-handoff.md",
            "plugins/super-developer/skills/worktree/references/feature-package-workflow.md",
        ]
        texts = {path: read_repo(path) for path in affected}
        store = texts[affected[0]]
        concept = texts[affected[4]]
        handoff = texts[affected[5]]
        workflow = texts[affected[6]]
        combined = compact_text("\n".join(texts.values())).lower()

        # The authority route is causal: reject legacy authority, import safely, resolve the
        # narrow remote permission, initialize state, then publish/resume from verified CAS state.
        ordered_store_sections = [
            "## Sidecar-Only Authority",
            "## Provenance-Bound Legacy Import",
            "## Sidecar Portability Authorization",
            "## Initial Lifecycle State",
            "## Publication and Resume Invariants",
        ]
        for earlier, later in zip(ordered_store_sections, ordered_store_sections[1:]):
            self.assertLess(store.index(earlier), store.index(later))
        for forbidden_affirmative in [
            "legacy/current-root artifact stores remain valid",
            "omit both flags only for current-root stores",
            "current-root artifact store is explicitly selected",
        ]:
            self.assertNotIn(forbidden_affirmative, combined)
        self.assertIn("declining or failing migration blocks planning", combined)
        self.assertIn("never resume from the current-root copy", combined)

        concept_route = compact_text(concept)
        for earlier, later in [
            ("create the empty orphan sidecar before writing", "import with provenance and revalidate"),
            ("import with provenance and revalidate", "Resolve portability permission"),
        ]:
            self.assertLess(concept_route.index(earlier), concept_route.index(later))
        self.assertIn("explicit instruction", concept)
        self.assertIn("durable preference", concept)
        self.assertIn("ask one focused discovery question", concept)
        self.assertIn("Sidecar Portability Authorization", handoff)
        for excluded in ["code", "target", "release", "force", "deletion"]:
            self.assertIn(excluded, combined)

        initial = workflow[
            workflow.index("## Initial Authorized Sidecar Publication"):
            workflow.index("## Feature and Package Setup")
        ]
        self.assertLess(
            initial.index('git ls-remote --heads -- "$ARTIFACT_PUSH_ENDPOINT"'),
            initial.index('git push -- "$ARTIFACT_PUSH_ENDPOINT"'),
        )
        self.assertNotIn("git push origin", initial)
        self.assertLess(initial.index("git add --"), initial.index("git commit"))
        self.assertIn("refs/heads/artifacts/<feature>", initial)
        self.assertNotRegex(initial, r"git add (?:-A|--all|\.)")
        self.assertNotRegex(initial, r"git push[^\n]*--force")

        checkpoint = workflow[
            workflow.index("## Quiescent Code-Before-Sidecar Checkpoint"):
            workflow.index("## Safe Resume")
        ]
        self.assertLess(
            checkpoint.index('git push -- "$CODE_PUSH_ENDPOINT" "$CODE_SHA:$CODE_REF"'),
            checkpoint.index('cd "$ARTIFACT_ROOT"'),
        )
        self.assertIn("refs/heads/checkpoints/<feature>/<slot>/g<generation>", checkpoint)
        self.assertIn("FINALIZED_PATHS", checkpoint)
        self.assertNotRegex(checkpoint, r"git add (?:-A|--all|\.)")
        self.assertIn("last quiescent CAS snapshot", store)
        for path, text in texts.items():
            self.assertLessEqual(len(text.splitlines()), 150, path)

    def test_a2_preflight_causally_precedes_plan_and_bounds_discovery(self) -> None:
        planning = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        preflight = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/design-preflight.md"
        )
        planner = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md"
        )
        spec = read_repo("plugins/super-developer/skills/implementation-plan/references/spec-template.md")
        convergence = read_repo("plugins/super-developer/references/orchestration-convergence.md")
        spike = read_repo("plugins/super-developer/skills/spike-to-plan/SKILL.md")
        combined = compact_text("\n".join([planning, preflight, planner, spec, convergence, spike]))

        self.assertLess(planning.index("Run `references/design-preflight.md`"), planning.index("Dispatch a fresh planner"))
        for needle in [
            "Safe disposable discovery", "Protected discovery", "proven-ready",
            "protected-activation-required", "known-unavailable", "actual production path",
            "affected broad-regression", "Human Authorization Envelope", "Technical Plan Baseline",
            "Planner Self-Challenge", "boundary|final", "at most eight total delegated",
            "two total planner-correction waves", "two total spike waves", "absolute deadline",
            "Issued usage is monotonic", "needs_decision", "No event ledger is added",
        ]:
            self.assertIn(compact_text(needle), combined)
        for rel in [
            "plugins/super-developer/skills/implementation-plan/SKILL.md",
            "plugins/super-developer/skills/implementation-plan/references/design-preflight.md",
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
            "plugins/super-developer/skills/implementation-plan/references/spec-template.md",
            "plugins/super-developer/skills/spike-to-plan/SKILL.md",
            "plugins/super-developer/references/orchestration-convergence.md",
        ]:
            self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)

    def test_a2_minimum_sufficient_evidence_stops_test_volume_incentives(self) -> None:
        surfaces = [
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md",
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md",
            "plugins/super-developer/skills/testing/references/core/generic-testing.md",
            "plugins/super-developer/skills/implement/references/package-agent-contract.md",
        ]
        combined = compact_text("\n".join(read_repo(rel) for rel in surfaces)).lower()
        for needle in [
            "confidence obligations", "actual production path", "cheapest credible causal evidence",
            "one causal test", "prove multiple", "stop adding tests", "triggered risks",
            "test count", "test loc", "test-to-production ratio", "coverage percentage",
            "suite volume", "exhaustive suite review", "existing tests block only",
            "false-positive evidence", "hidden skip/focus/xfail", "flakiness/inconclusive",
            "harness/configuration", "solely for volume", "sole implementation authorization",
            "never add a routine second testing prompt",
        ]:
            self.assertIn(needle, combined)
        package_agent = read_repo(surfaces[-1])
        self.assertLess(
            package_agent.index("## Minimum Sufficient Test Rule"),
            package_agent.index("## Package Self-Review"),
        )
        generic = read_repo(surfaces[-2])
        self.assertLess(generic.index("Select the smallest maintainable evidence set"), generic.index("stop adding"))
        for rel in surfaces:
            self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)

    def test_a3_initial_and_nested_review_have_one_causal_authorization_gate(self) -> None:
        affected = [
            "plugins/super-developer/skills/review-plan/SKILL.md",
            "plugins/super-developer/skills/review-plan/references/plan-review-resolution.md",
            "plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md",
            "plugins/super-developer/skills/implement/SKILL.md",
            "plugins/super-developer/skills/implement/references/execution-contract.md",
            "plugins/super-developer/references/orchestration-convergence.md",
        ]
        texts = {rel: read_repo(rel) for rel in affected}
        review_raw = texts[affected[0]]
        review = compact_text(review_raw)
        implement = compact_text(texts[affected[3]])
        decision = compact_text(texts[affected[4]])
        convergence = compact_text(texts[affected[5]])
        combined = "\n".join(texts.values())

        # Shared cold challenge precedes two disjoint causal branches.
        self.assertLess(review.index("Dispatch one cold Plan Reviewer/Triage"), review.index("Aggregate all findings"))
        self.assertLess(review.index("dispatch affected cold re-review"), review.index("## Initial Branch"))
        initial = review_raw[
            review_raw.index("## Initial Branch — The One Gate"):
            review_raw.index("## Nested Amendment Branch — Return Only")
        ]
        nested = review_raw[
            review_raw.index("## Nested Amendment Branch — Return Only"):
            review_raw.index("## Stop if")
        ]
        for earlier, later in [
            ("validate execution readiness", "Construct the compact authorization `inputs` snapshot"),
            ("Construct the compact authorization `inputs` snapshot", "present the"),
            ("present the", "On `Approve and auto-resolve`"),
            ("On `Approve and auto-resolve`", "CAS-checkpoint"),
        ]:
            self.assertLess(initial.index(earlier), initial.index(later))
        for choice in ["Approve and auto-resolve", "Request changes", "Abort"]:
            self.assertIn(choice, initial)
            self.assertNotIn(choice, nested)
        self.assertIn("existing Delivery Owner", nested)
        self.assertIn("distinct reviewed descendant", nested)
        self.assertIn("derive the next effective digest", nested)
        self.assertIn("Never present authorization choices", nested)
        self.assertIn("The Delivery Owner validates", nested)

        # Initial digest is reproducible; nested mode preserves lineage and returns before continuation.
        for field in [
            "artifact_commit", "artifact_tree", "base_commit", "clean_status", "dependencies", "routing", "actions",
            "budget_authority", "amendment_policy",
        ]:
            self.assertIn(field, combined)
        self.assertIn("canonical JSON digest of exactly", combined)
        self.assertIn("inputs/initial digest", implement)
        self.assertLess(implement.index("Validate the receipt"), implement.index("run the exact freshness guard"))
        self.assertLess(
            implement.index("invoke cold `review-plan` explicitly in `nested-amendment` mode"),
            implement.index("Only after that validation checkpoint"),
        )
        self.assertIn("never offers choices, creates an ID", decision)
        self.assertIn("There is no later execution decision", convergence)
        self.assertIn("Never present another execution decision", implement)
        for stale in ["Gate 1", "Gate 2", "step-by-step", "approve auto-resolve"]:
            self.assertNotIn(stale, combined)
        for rel, text in texts.items():
            self.assertLessEqual(len(text.splitlines()), 150, rel)

    def test_a4_lifecycle_validation_is_mechanical_and_git_cas_remains_worktree_owned(self) -> None:
        affected = [
            "plugins/super-developer/references/slice-first-artifacts.md",
            "plugins/super-developer/references/artifact-store.md",
            "plugins/super-developer/skills/worktree/references/feature-package-workflow.md",
            "plugins/super-developer/skills/implement/references/execution-contract.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
        ]
        texts = {rel: read_repo(rel) for rel in affected}
        combined = compact_text("\n".join(texts.values())).lower()
        for token in [
            ".tasks/<feature>/lifecycle-state.json", "schema-v1", "distinct", "--previous-commit",
            "last_verified", "amendment_link", "effective digest", "maxima", "issued",
            "active reservation", "code checkpoint", "serious_clusters", "no sequence/history array",
            "optional", "boundary|final", "never reserves", "proves completion", "b3/b4 own",
        ]:
            self.assertIn(token, combined)
        for premature in ["technical_amendments", "matching `verification-summary`", "completed stage requires"]:
            self.assertNotIn(premature, combined)

        workflow = texts[affected[2]]
        initial = workflow[
            workflow.index("## Initial Authorized Sidecar Publication"):
            workflow.index("## Feature and Package Setup")
        ]
        checkpoint = workflow[
            workflow.index("## Quiescent Code-Before-Sidecar Checkpoint"):
            workflow.index("## Safe Resume")
        ]
        self.assertLess(initial.index("validate-lifecycle-state"), initial.index("git add --"))
        self.assertLess(
            checkpoint.index('git push -- "$CODE_PUSH_ENDPOINT" "$CODE_SHA:$CODE_REF"'),
            checkpoint.index("validate-lifecycle-state"),
        )
        self.assertLess(checkpoint.index("validate-lifecycle-state"), checkpoint.index("git add --"))
        self.assertIn(
            "Exact-endpoint remote reachability/CAS stays in the worktree contract",
            compact_text(texts[affected[3]]),
        )
        for rel, text in texts.items():
            self.assertLessEqual(len(text.splitlines()), 150, rel)

        helper = read_repo("plugins/super-developer/assets/sliceproof.py")
        self.assertIn('"validate-lifecycle-state"', helper)
        self.assertIn("canonical_json_digest", helper)
        self.assertNotIn("technical_amendments", helper)
        self.assertIn('"validate-agentic-completion"', helper)
        self.assertNotIn('["push"', helper)
        self.assertNotIn('["fetch"', helper)
        self.assertNotIn('["ls-remote"', helper)

    def test_phase_a_corrections_bind_endpoint_authorization_and_replan_state(self) -> None:
        workflow = read_repo(
            "plugins/super-developer/skills/worktree/references/feature-package-workflow.md"
        )
        store = read_repo("plugins/super-developer/references/artifact-store.md")
        artifacts = read_repo("plugins/super-developer/references/slice-first-artifacts.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        readme = read_repo("plugins/super-developer/README.md")

        endpoint_fence = workflow[
            workflow.index("## Exact Push Endpoint Fence"):
            workflow.index("## Layout and Local Sidecar Setup")
        ]
        for token in [
            "git remote get-url --push --all", '"${#endpoints[@]}" -eq 1',
            "assert_push_endpoint_unchanged", "one quoted argv value", "distinct `pushurl`",
        ]:
            self.assertIn(token, endpoint_fence)
        remote_commands = [
            line for line in workflow.splitlines()
            if re.search(r"\bgit (?:ls-remote|push|fetch)\b", line)
        ]
        self.assertTrue(remote_commands)
        for line in remote_commands:
            self.assertRegex(line, r'"\$(?:ARTIFACT|CODE)_PUSH_ENDPOINT"', line)
            self.assertNotRegex(line, r"\bgit (?:ls-remote|push|fetch)[^\n]*\borigin\b", line)
        self.assertIn("zero/multiple/changed endpoint", workflow)
        self.assertIn("Remote reachability belongs here", workflow)
        self.assertIn("exact configured push endpoint", store)

        artifact_compact = compact_text(artifacts)
        for token in [
            "Generation 1 is initial topology", "Initial publication with a code ref is invalid",
            "complete Implementation Authorization", "canonical sorted-key compact UTF-8 JSON",
            "distinct reviewed descendant", "exact sidecar lineage", "no sequence/history array",
            "reviewed effective-digest change", "blocked resolution", "explicit repair progression",
        ]:
            self.assertIn(token, artifact_compact)
        self.assertIn("requires a reviewed effective-digest", lifecycle)
        for obsolete in ["Execution Contract", "step-by-step", "sibling checks", "Gate-2"]:
            self.assertNotIn(obsolete, readme)
        self.assertIn("ONE Implementation Authorization", readme)
        self.assertIn("nested envelope-preserving amendments return cold receipts", compact_text(readme))

    def test_obsolete_or_unsafe_terms_are_only_negative_guidance(self) -> None:
        for path in prompt_surface_paths():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            if STALE_PREF_PATH in text:
                self.fail(f"{rel}: greenfield harness must not reference stale {STALE_PREF_PATH}")
            for token in [".superdeveloper/semgrep-policy.yml", "local-rule-files", "local-rules-path"]:
                if token in text:
                    window = context_window(text, token)
                    self.assertRegex(window, r"\b(do not|no|without|reject|forbid|forbidden|never)\b", f"{rel}: {token}")
            for line in text.splitlines():
                lowered = line.lower()
                if "semgrep" in lowered and "fix-all" in lowered:
                    self.assertRegex(lowered, r"\b(not|no|without|unless|advisory|bounded)\b", f"{rel}: {line}")
                if "semgrep" in lowered and "automatic" in lowered and "blocker" in lowered:
                    self.assertRegex(lowered, r"\b(not|no|without|unless)\b", f"{rel}: {line}")

    def test_semgrep_prompt_detail_stays_progressively_disclosed(self) -> None:
        skill_paths = [
            PLUGIN_ROOT / "skills" / "conceptualize" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "implementation-plan" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "implement" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "review-code" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "audit" / "SKILL.md",
            PLUGIN_ROOT / "skills" / "skill-authoring" / "SKILL.md",
        ]
        eager_forbidden = [
            "semgrep-rules.git",
            ".cache/semgrep-rules/community",
            ".tasks/<feature>/semgrep/<WP-ID>.semgrep.json",
            CANONICAL_SCAN,
            "show-finding --",
            "list-findings --",
        ]
        for path in skill_paths:
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            self.assertLessEqual(len(text.splitlines()), 150, rel)
            for token in eager_forbidden:
                self.assertNotIn(token, text, rel)

        semgrep_reference = PLUGIN_ROOT / "references" / "semgrep.md"
        text = semgrep_reference.read_text(encoding="utf-8")
        self.assertLessEqual(len(text.splitlines()), 150)
        self.assertLessEqual(len(text.split()), 900)
        self.assertIn("Load it only when resolving Semgrep state", text)
        self.assertNotIn("rules inventory", text.lower().replace("rule inventory", ""))

    def test_helper_user_facing_summaries_are_bounded_and_not_workflow_jargon(self) -> None:
        source = (PLUGIN_ROOT / "assets" / "semgrep_rules.py").read_text(encoding="utf-8")
        self.assertIn("Semgrep scan complete: findings=", source)
        self.assertIn("SUMMARY_TOP_N", source)
        self.assertIn("LIST_LIMIT_MAX", source)
        self.assertIn("semgrep_severity_is_advisory", source)
        summary_region = source[source.index("def _build_summary") : source.index("def _write_summary")]
        for workflow_word in ["proof", "package verification", "Slice", "planning", "staging"]:
            self.assertNotIn(workflow_word, summary_region)

    def test_testing_skill_core_contract_is_workflow_meta_and_progressive(self) -> None:
        skill = read_repo("plugins/super-developer/skills/testing/SKILL.md")
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        delegation = read_repo("plugins/super-developer/skills/testing/references/delegation-packets.md")
        strategy = read_repo("plugins/super-developer/skills/testing/references/strategy-interview.md")
        generic = read_repo("plugins/super-developer/skills/testing/references/core/generic-testing.md")
        web = read_repo("plugins/super-developer/skills/testing/references/web/application-testing.md")
        browser = read_repo("plugins/super-developer/skills/testing/references/web/browser-e2e-stack-setup.md")
        skill_compact = compact_text(skill)
        combined = compact_text("\n".join([skill, workflow, delegation, strategy, generic, web, browser]))

        for rel in [
            "plugins/super-developer/skills/testing/SKILL.md",
            "plugins/super-developer/skills/testing/references/workflow-contract.md",
            "plugins/super-developer/skills/testing/references/delegation-packets.md",
            "plugins/super-developer/skills/testing/references/strategy-interview.md",
            "plugins/super-developer/skills/testing/references/core/generic-testing.md",
            "plugins/super-developer/skills/testing/references/web/application-testing.md",
            "plugins/super-developer/skills/testing/references/web/browser-e2e-stack-setup.md",
        ]:
            self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)

        for needle in [
            "Establish, document, and apply project-specific testing workflows",
            "Resolve the repository's testing authority",
            "establish durable workflow docs when needed",
            "Do not default to standalone broad test edits or commands",
            "Choose a mode before acting: initialize/update workflow, author/alter tests, execute a bounded command, or delegate execution-oriented work",
            "Testing authority is required before test writes, harness/test commands, or delegation",
            "Authority is canonical workflow, routine-safe fallback for one parent-run local command, or task-local Testing Authorization",
            "Canonical workflow remains the durable authority for broad/reusable delegation, recurring",
            "Routine-safe fallback is narrow and command-specific",
            "Task-local Testing Authorization is a current-task one-off",
            "Missing workflow alone permits read-only discovery and planning",
            "Keep this eager prompt meta-level",
            "project methodology in `docs/testing/workflow.md` or linked companion docs",
            "use skill references only as optional proposal/adaptation aids",
        ]:
            self.assertIn(" ".join(needle.split()), skill_compact)

        for needle in [
            "It is not a stack methodology and does not authorize test writes, test runs, installs, browser use, network access, live services, or config/CI changes",
            "Use this reference only as an optional proposal/adaptation aid",
            "Approved project workflow docs (`docs/testing/workflow.md` and linked companions) and exact task-local testing authority govern repository-specific testing behavior",
            "this reference must not override them or authorize standalone test edits/runs by itself",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

        for obsolete in [
            "Standalone-first",
            "Use when asked for testing help, test plans/cases, or safe local test execution",
            "Authors test cases, writes safe test-only artifacts, and runs repo-discovered safe local test commands",
            "user-curated workflow",
        ]:
            self.assertNotIn(obsolete, skill)
        for eager_detail in [
            "Playwright + Allure",
            "human-review mode requires itemized evidence",
            "test:e2e:review",
            "E2E_BASE_URL",
            "docs/testing/<topic>.test-plan.md",
        ]:
            self.assertNotIn(eager_detail, skill)
        for forbidden in ["Semgrep", "staging", "Slice"]:
            self.assertNotIn(forbidden, combined)

    def test_testing_workflow_canonical_paths_and_lazy_discovery_are_static_contract(self) -> None:
        skill = read_repo("plugins/super-developer/skills/testing/SKILL.md")
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        combined = compact_text(f"{skill}\n{workflow}")

        for needle in [
            "root `AGENTS.md` should contain only a concise lazy pointer for testing work",
            "root-relative `docs/testing/workflow.md` is the reusable workflow entry point",
            "Companion docs live under `docs/testing/` and are loaded only when the workflow points to them",
            "`AGENTS.md`: a short lazy-loading pointer for testing work",
            "preserve unrelated content and add/update only the testing pointer",
            "`docs/testing/workflow.md`: the reusable testing workflow entry point",
            "`docs/testing/*`: optional companion docs loaded lazily when the entry point links them",
            "Do not silently choose alternate canonical paths",
            "Lowercase `agents.md` and existing testing docs may be candidates",
            "candidates are source material only",
            "`docs/testing/workflow.md` exists, is accepted/current, and incorporates or references them",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

        self.assertFalse((REPO_ROOT / "AGENTS.md").exists(), "repo must not add a real root AGENTS.md fixture")
        self.assertFalse((REPO_ROOT / "docs" / "testing" / "workflow.md").exists())
        self.assertFalse((REPO_ROOT / "docs" / "testing").exists(), "repo must not add real workflow docs")

    def test_testing_missing_canonical_workflow_candidate_gate_fails_closed(self) -> None:
        skill = read_repo("plugins/super-developer/skills/testing/SKILL.md")
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        combined = compact_text(f"{skill}\n{workflow}")

        for needle in [
            "Testing authority is required before test writes, harness/test commands, or delegation",
            "routine-safe fallback for one parent-run local command",
            "canonical-workflow`: required for broad/reusable delegation, recurring, browser/E2E, live service",
            "routine-safe fallback`: allowed without workflow only for one command that is repo-local and project-owned",
            "It is parent-run only, not delegation authority",
            "task-local Testing Authorization`: a current-task one-off for focused work or one focused delegated act",
            "`missing`: no canonical entry point exists",
            "Absence alone allows read-only discovery and planning",
            "For commands/writes, either prove routine-safe fallback, obtain task-local Testing Authorization",
            "`stale/ambiguous/conflicting`: a workflow exists but its commands, paths, stack assumptions",
            "`unsafe/refused`: the workflow or user decision would require unsafe, secret-bearing, production",
            "Discovery is bounded, read-only, path-safe, symlink-safe, and secret-aware",
            "Inspect only project-owned candidate locations",
            "`docs/testing/`, `docs/tests/`, and `docs/qa/`",
            "`README*` files under test, tests, spec, specs, e2e, integration, or similar test directories",
            "Avoid vendor/generated/dump/cache/build/dependency directories",
            "Do not follow symlinks outside the repository root",
            "Summarize only relevant, sanitized facts",
            "candidate path, why it looks like testing workflow material, scope/stack signals, known commands without secrets, and gaps/risks",
            "**adopt** an existing canonical-quality doc",
            "**migrate** useful content",
            "**link** from `docs/testing/workflow.md` to an existing curated companion doc",
            "**initialize** a new workflow from repo evidence and focused recommendations",
            "Candidate choice alone is not durable authority",
            "First write or update `docs/testing/workflow.md` so it incorporates or references the approved candidate before treating it as project policy",
            "proceed only for an exact routine-safe fallback or task-local Testing Authorization",
            "Do not treat a candidate doc as reusable workflow by itself",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

    def test_testing_initialization_update_is_recommendation_led_and_approval_gated(self) -> None:
        skill = read_repo("plugins/super-developer/skills/testing/SKILL.md")
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        browser = read_repo("plugins/super-developer/skills/testing/references/web/browser-e2e-stack-setup.md")
        combined = compact_text(f"{skill}\n{workflow}\n{browser}")

        for needle in [
            "Initialization/update is recommendation-led: inspect repo evidence before broad questions",
            "propose the best project-fit strategy",
            "ask focused confirmation questions",
            "present a draft summary and proposed file changes before writing workflow docs",
            "Start with repo evidence, not a broad questionnaire",
            "Then present a recommendation",
            "name the strategy and why repo evidence supports it",
            "ask one focused confirmation or risk-boundary question when evidence is insufficient",
            "For missing browser E2E strategy, inspect the web stack, existing scripts/tests, app entry points, dev-server assumptions, auth/data risks, and docs",
            "strategy establishment still stops at a documentation proposal",
            "does not install dependencies, create browser config, write tests, run browsers, start services, use recordings, touch secrets, access the network, edit config/CI/orchestration, or execute tests",
            "Before writing root `AGENTS.md` or any `docs/testing/*` file, present a draft naming the lazy pointer",
            "Write workflow docs only after explicit current-task approval",
            "If approval is not granted, continue focused discovery or stop with the draft",
            "After explicit approval, the main agent may create or surgically update root `AGENTS.md` and `docs/testing/*`",
            "Without approval, continue discovery or stop with the draft; leave no partial workflow docs as accepted",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

    def test_testing_strategy_interview_lifecycle_and_candidate_paths_are_static_contract(self) -> None:
        skill = read_repo("plugins/super-developer/skills/testing/SKILL.md")
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        strategy = read_repo("plugins/super-developer/skills/testing/references/strategy-interview.md")
        delegation = read_repo("plugins/super-developer/skills/testing/references/delegation-packets.md")
        combined = compact_text("\n".join([skill, workflow, strategy, delegation]))

        for needle in [
            "Explicit initialize/update/adopt/migrate/link/revise requests require a strategy interview after repository inspection",
            "For greenfield/no-strategy repositories and explicit initialize, update, adopt, migrate, link, or revise requests, follow the parent-owned strategy-interview branch before accepted workflow-doc writes",
            "Treat absent/minimal tests, no documented strategy, and existing testing docs as source evidence, not a reason to skip the interview",
            "existing docs are source material, not a skip",
            "Ordinary author/alter/execute may use accepted/current workflow, routine-safe fallback, or task-local Testing Authorization when adequate",
            "insufficient authority routes to this update path",
            "Explicit initialize, update, adopt, migrate, link, or revise requests still route to the strategy interview; existing docs are source material",
            "Existing workflows, absent/minimal tests, candidates, and companion docs inform the recommendation but do not skip the interview",
            "`missing`: no canonical entry point exists, including greenfield repositories with no/minimal tests or no documented testing strategy",
            "Absence alone allows read-only discovery and planning",
            "For commands/writes, either prove routine-safe fallback, obtain task-local Testing Authorization",
            "candidates are source material only: they govern reusable or high-risk test work only after `docs/testing/workflow.md` exists, is accepted/current, and incorporates or references them through an approved adopt, migrate, link, or initialize decision",
            "Candidate choice alone is not durable authority",
            "First write or update `docs/testing/workflow.md` so it incorporates or references the approved candidate",
            "candidate handling: any adopted, migrated, or linked candidate is incorporated or referenced by the canonical workflow entry before it can govern reusable/high-risk delegated work",
            "In adopt/migrate/link discussions, ask which existing docs or tests remain authoritative source material",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

    def test_testing_strategy_interview_domains_and_confidence_order_are_static_contract(self) -> None:
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        strategy = read_repo("plugins/super-developer/skills/testing/references/strategy-interview.md")
        strategy_compact = compact_text(strategy)
        combined = compact_text(f"{workflow}\n{strategy}")

        for earlier, later in [
            ("Inspect repo evidence first", "Summarize the evidence"),
            ("Summarize the evidence", "Start the user-facing strategy branch with the confidence outcome"),
            ("confidence outcome the user wants", "test levels, folders, templates, commands, approval gates, or tools"),
        ]:
            self.assertLess(strategy_compact.index(earlier), strategy_compact.index(later))

        for needle in [
            "Inspect repo evidence first: stack manifests, scripts, test directories, fixtures, existing docs, CI/config, app surfaces, report locations, data/auth boundaries, and stale/conflict signals",
            "Summarize the evidence, then ask one focused strategy question at a time",
            "do not dump a broad questionnaire",
            "Start the user-facing strategy branch with the confidence outcome the user wants before choosing test levels, folders, templates, commands, approval gates, or tools",
            "Use confidence examples only as optional explanation, not as a mandatory visible profile menu",
            "Continue until every mandatory core domain is answered, marked not applicable from evidence, or explicitly deferred by the user with the risk recorded in the draft",
            "tech stack, product/test surfaces, and risk boundaries the workflow must cover",
            "folder structure for new test plans, authored tests, fixtures/helpers, evidence, reports, and whether a central feature test index or coverage-index is used or deliberately not used",
            "feature/domain test plan policy, including when a plan gates authoring or execution",
            "user-friendly execution choices, current-task approvals, stop conditions, and command categories",
            "evidence/reporting expectations, redaction rules, and durable report locations",
            "data/setup/cleanup policy for local, integration, live, browser, or mutating tests",
            "legacy tests/docs handling: stay put by default, plus adopt/migrate/link choices when requested",
            "stale, ambiguous, conflicting, or unsafe workflow update procedure",
            "Activate browser/web domains only when repo evidence, user scope, or selected strategy makes them material",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

    def test_testing_strategy_interview_structure_plan_templates_and_output_are_static_contract(self) -> None:
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        strategy = read_repo("plugins/super-developer/skills/testing/references/strategy-interview.md")
        generic = read_repo("plugins/super-developer/skills/testing/references/core/generic-testing.md")
        combined = compact_text("\n".join([workflow, strategy, generic]))

        for heading in [
            "## Starter Feature or Domain Test Plan",
            "## Starter Plan-to-Result Report",
            "## Starter Execution Choices",
            "## Legacy and Migration Prompts",
        ]:
            self.assertIn(heading, strategy)

        for needle in [
            "folder/taxonomy and central feature test index or coverage-index stance for new plans, tests, evidence, and reports, plus legacy stance",
            "feature/domain plan policy and plan-before-work gates",
            "The workflow draft should name: confidence goals; mandatory and active conditional domains; plan, test, evidence, report, and central feature test index stance; execution choices and approvals; reliability/cleanup semantics; legacy stance; companion docs; redaction; and the update procedure",
            "Recommend a clean structure for new plans/tests going forward, but leave legacy tests where they are unless the user explicitly asks for migration",
            "Keep plans high-level and reviewable. They are scenario/deliverable contracts, not command recipes",
            "Feature/domain plan starter (high-level scenario contract, not a command recipe)",
            "Nontrivial/high-risk work includes live integration, browser E2E, cross-stack behavior, multi-scenario coverage, risky data/setup, or approval-gated tooling/config changes",
            "For a standalone testing task, create a Markdown plan before covered writes/execution, present it, and wait for explicit task-local approval",
            "In a planned-feature auto-resolve flow, the sole Implementation Authorization must already name the testing writes, commands, effects, bounds, and cleanup",
            "consume that authority and never add a routine second testing prompt",
            "Interview decisions feed the repository testing workflow, not a default standalone questionnaire",
            "Draft or revise `docs/testing/workflow.md` and linked `docs/testing/*` companions with the accepted strategy decisions",
            "A separate checklist or decision record is optional for large or high-risk strategy updates, not the default",
            "These paths do not replace the canonical workflow entry point",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

    def test_testing_strategy_interview_browser_web_conditionals_are_static_contract(self) -> None:
        strategy = read_repo("plugins/super-developer/skills/testing/references/strategy-interview.md")
        web = read_repo("plugins/super-developer/skills/testing/references/web/application-testing.md")
        browser = read_repo("plugins/super-developer/skills/testing/references/web/browser-e2e-stack-setup.md")
        combined = compact_text("\n".join([strategy, web, browser]))
        combined_lower = combined.lower()

        for needle in [
            "Activate browser/web questions only when repo evidence, user scope, or selected confidence goals show browser, frontend, web UX, UI-backed persistence, live web/API, or browser tooling relevance",
            "When active, evaluate material subcoverage such as accessibility cues, responsive/viewport behavior, cross-browser needs, screenshots/video, user journeys, browser state, and UI-backed persistence",
            "If inactive, record why browser/web coverage is not part of the current workflow instead of imposing it",
            "Browser/web subcoverage is conditional. During an active browser/web strategy interview or plan, evaluate material accessibility cues, responsive/viewport behavior, cross-browser needs, screenshots or video, user journeys, browser state, and UI-backed persistence from repo evidence and confidence goals",
            "do not impose them universally or ignore them when relevant",
            "Browser setup is an active conditional domain, not a universal requirement",
            "recommend Playwright + Allure as the preferred baseline only when repo evidence fits",
            "fall back to Playwright + Allure only when current tools cannot reasonably meet evidence/dashboard needs and user approval exists",
            "Do not invent a framework, package manager, Playwright, Allure, browser command, report command, file layout, or live target when repo evidence is absent",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

        for forbidden in [
            "must use playwright",
            "require playwright for every",
            "browser e2e is mandatory",
            "always ask browser",
            "accessibility for every repository",
            "responsive for every repository",
            "cross-browser for every repository",
            "always-on screenshots are required",
            "always-on videos are required",
        ]:
            self.assertNotIn(forbidden, combined_lower)

    def test_testing_strategy_interview_execution_reporting_and_reliability_are_static_contract(self) -> None:
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        strategy = read_repo("plugins/super-developer/skills/testing/references/strategy-interview.md")
        delegation = read_repo("plugins/super-developer/skills/testing/references/delegation-packets.md")
        generic = read_repo("plugins/super-developer/skills/testing/references/core/generic-testing.md")
        combined = compact_text("\n".join([workflow, strategy, delegation, generic]))

        for needle in [
            "Starter execution choices may be renamed by the accepted workflow, but should stay user-facing: focused check, feature confidence, active browser review, broad regression, or do not run yet",
            "The final workflow may rename these, but it should keep plain user-facing choices and approval gates",
            "Each choice should document what it proves, required approvals, command/evidence expectations, stop conditions, cleanup duties, and how results map back to the approved plan",
            "Each choice needs what it proves, approvals, stop conditions, evidence, and cleanup/reporting expectations",
            "Selected execution choice(s): <focused check/feature confidence/browser review/broad regression/do not run yet/etc.>",
            "Approved plan path/version: <path+version, or authority-approved no-plan reason>",
            "Current-task approvals already granted: <exact approvals or none>",
            "Approval-gated actions to stop for: <commands/writes/browser/live/network/etc.>",
            "Plan-to-result report: map plan scenarios to authored tests/results, selected choices, evidence, skipped/not-run items, redaction, cleanup status, and follow-up risks",
            "approved plan path/version and scenario-to-test/result mapping, or authority-approved no-plan reason",
            "selected execution choice(s), current approvals used, and choices skipped/not run with reasons",
            "sanitized evidence, artifacts, summaries, blocked approvals/preconditions, and redaction actions",
            "cleanup-failed/uncertain follow-up",
            "flaky or inconclusive is not pass",
            "Use strict outcome language: passed, failed, blocked-precondition, unsafe-needs-approval, inconclusive/flaky, and skipped/not-run or the project-approved equivalents",
            "Flaky, timed-out, ambiguous, or cleanup-uncertain results are not passes",
            "Live, integration, browser, or data-mutating tests require owned or isolated data, idempotent setup or equivalent isolation",
            "explicit follow-up when cleanup fails or is uncertain",
            "Do not default to uncontrolled shared-data mutation or hide cleanup failures in raw logs",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

    def test_testing_strategy_interview_reference_stays_progressive_and_semgrep_free(self) -> None:
        expected_surfaces = {
            "plugins/super-developer/skills/testing/SKILL.md",
            "plugins/super-developer/skills/testing/references/core/generic-testing.md",
            "plugins/super-developer/skills/testing/references/delegation-packets.md",
            "plugins/super-developer/skills/testing/references/strategy-interview.md",
            "plugins/super-developer/skills/testing/references/web/application-testing.md",
            "plugins/super-developer/skills/testing/references/web/browser-e2e-stack-setup.md",
            "plugins/super-developer/skills/testing/references/workflow-contract.md",
        }
        actual_surfaces = {path.relative_to(REPO_ROOT).as_posix() for path in testing_prompt_surface_paths()}
        self.assertEqual(expected_surfaces, actual_surfaces)

        for path in testing_prompt_surface_paths():
            text = path.read_text(encoding="utf-8")
            rel = path.relative_to(REPO_ROOT)
            lowered = text.lower()
            self.assertLessEqual(len(text.splitlines()), 150, rel)
            self.assertNotIn("semgrep", lowered, rel)
            self.assertNotIn(CANONICAL_SCAN.lower(), lowered, rel)
            self.assertNotIn("semgrep_rules.py", lowered, rel)
            self.assertNotIn("internet", lowered, rel)
            for forbidden in ["semgrep setup", "semgrep scan", "semgrep helper", "semgrep evidence"]:
                self.assertNotIn(forbidden, lowered, rel)

    def test_testing_delegation_packets_and_no_executor_fallback_are_workflow_aware(self) -> None:
        skill = read_repo("plugins/super-developer/skills/testing/SKILL.md")
        delegation = read_repo("plugins/super-developer/skills/testing/references/delegation-packets.md")
        combined = compact_text(f"{skill}\n{delegation}")

        for needle in [
            "Authoring, alteration, and execution are delegated only after canonical workflow or task-local Testing Authorization covers the delegated act",
            "If no executor/sub-agent is available, return a packet and stop",
            "The main agent remains an orchestrator",
            "authority state: accepted/current `docs/testing/workflow.md` plus companions; or task-local Testing Authorization for one focused delegated act",
            "requires canonical workflow authority",
            "candidate handling: any adopted, migrated, or linked candidate is incorporated or referenced by the canonical workflow entry before it can govern reusable/high-risk delegated work",
            "Testing delegation packet",
            "User goal: <requested testing outcome>",
            "Testing authority: <canonical-workflow | task-local Testing Authorization>",
            "Authority source: <docs/testing/workflow.md + companions, or exact one-off approval text>",
            "Required first step: read the authority source; receipt/report must cite it",
            "Allowed scope: <test files/fixtures/helpers/docs/commands/evidence surfaces>",
            "Disallowed scope: <production/runtime code, unapproved config/dependencies/CI/orchestration, etc.>",
            "Current-task approvals already granted: <exact approvals or none>",
            "Approval-gated actions to stop for: <commands/writes/browser/live/network/etc.>",
            "Command safety: classify commands, use bounded timeouts, no unsafe/default live side effects",
            "Evidence/reporting: sanitized commands, outputs, artifacts, outcomes, cleanup, blocked reasons",
            "Product-failure routing: do not edit product code; report reproduction and route to owner",
            "The executor's first reportable fact should prove authority consultation",
            "Final executor reports should include",
            "No-Executor Fallback",
            "Do not run commands or edit tests directly as a substitute for missing delegation",
        ]:
            self.assertIn(" ".join(needle.split()), combined)
        self.assertNotIn("user has explicitly chosen an adopted, migrated, or linked candidate for the current task", delegation)

    def test_testing_optional_reference_precedence_and_browser_strategy_are_retained(self) -> None:
        skill = read_repo("plugins/super-developer/skills/testing/SKILL.md")
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")
        generic = read_repo("plugins/super-developer/skills/testing/references/core/generic-testing.md")
        web = read_repo("plugins/super-developer/skills/testing/references/web/application-testing.md")
        browser = read_repo("plugins/super-developer/skills/testing/references/web/browser-e2e-stack-setup.md")
        combined = compact_text("\n".join([skill, workflow, generic, web, browser]))

        for rel in [
            "plugins/super-developer/skills/testing/references/core/generic-testing.md",
            "plugins/super-developer/skills/testing/references/web/application-testing.md",
            "plugins/super-developer/skills/testing/references/web/browser-e2e-stack-setup.md",
        ]:
            self.assertTrue((REPO_ROOT / rel).is_file(), rel)

        for needle in [
            "Authority precedence: system/developer/current user/current skill safety rules outrank project workflow docs; approved project workflow docs outrank optional skill-local references",
            "Optional skill-local references, used only as proposal/adaptation aids",
            "If optional generic, web, or browser references are useful, load them only after testing authority is resolved or while drafting an initialization/update proposal; never let them override approved project workflow docs",
            "Optional stack-agnostic test design, command safety, outcomes, durable plan/report schema, and write boundaries",
            "Optional web/frontend/backend/API/live/browser coverage planning and evidence concerns",
            "Optional browser E2E stack/evidence/reporting setup proposal material, including Playwright/Allure conventions",
            "Use this only as optional proposal/adaptation material after workflow-state discovery",
            "Approved project workflow docs (`docs/testing/workflow.md` and linked companions) govern repository-specific behavior",
            "During strategy establishment, stop at the workflow-documentation proposal",
            "Do not install tools, write tests, run browsers, start services, access live targets, record artifacts, or change config",
            "Never use this setup to target production, record secrets, mutate shared unsafe data, bypass the approved project workflow, or weaken product behavior",
        ]:
            self.assertIn(" ".join(needle.split()), combined)

    def test_testing_skill_is_discoverable_in_docs_and_metadata(self) -> None:
        skill_names = sorted(path.name for path in (PLUGIN_ROOT / "skills").iterdir() if path.is_dir())
        self.assertEqual(15, len(skill_names))
        self.assertIn("testing", skill_names)
        self.assertIn("readme-polish", skill_names)

        root = read_repo("README.md")
        plugin = read_repo("plugins/super-developer/README.md")
        metadata = json.loads(read_repo("plugins/super-developer/.claude-plugin/plugin.json"))
        for text in [root, plugin]:
            self.assertIn("15 skills", text)
            self.assertIn("testing", text)
            self.assertIn("readme-polish", text)
            for stale in ["12 skills", "13 skills", "14 skills"]:
                self.assertNotIn(stale, text)
        for needle in [
            "testing workflow strategy and delegated test work",
            "**testing** (establishes/updates reusable project testing workflows and routes authoring/execution through approved workflow docs)",
        ]:
            self.assertIn(needle, root)
        for needle in [
            "| **testing** | Establishes or updates reusable project testing workflow docs, then routes test authoring, alteration, and execution through the approved workflow. | Standalone |",
            "> Establish this project's testing workflow for browser E2E",
            "> Add test coverage for this behavior using the approved testing workflow",
            "|   |   +-- references/workflow-contract.md",
            "|   |   +-- references/delegation-packets.md",
        ]:
            self.assertIn(needle, plugin)
        for stale in [
            "test authoring/execution, parallel implementation",
            "**testing** (author test cases and run safe local test commands)",
            "| **testing** | Authors test cases, writes safe test-only artifacts, and runs repo-discovered safe local test commands with structured evidence. | Standalone |",
        ]:
            self.assertNotIn(stale, root + "\n" + plugin)
        self.assertIn("testing", metadata["keywords"])
        self.assertIn("readme", metadata["keywords"])
        self.assertNotIn("test authoring/execution", metadata["description"])

    def test_diagnose_and_fix_separates_human_authorization_from_internal_receipts(self) -> None:
        text = read_repo("plugins/super-developer/skills/diagnose-and-fix/SKILL.md")
        compact = compact_text(text)
        for needle in [
            "exactly one recommended route",
            "stop/missing-info",
            "localized isolated fix",
            "may plan approved changes to existing systems",
            "Ask for one compact, human-readable Fix Authorization",
            "approved paths and behavior goal, with explicit non-goals",
            "isolated route plus human branch/base names",
            "`local only`, `commit reviewed fix`, or `commit and push reviewed branch`",
            "One response may authorize the displayed localized route through the selected branch delivery",
            "Target merge/push and cleanup stay at their existing owning boundaries",
            "Users never need to understand or approve raw SHAs, checksums, leases, or state receipts",
            "derives mandatory internal receipts at action time from the `worktree` and review contracts",
            "authorized paths, non-root worktree/base/ref identity, reviewed state",
            "Revalidate every binding immediately before its action",
            "Orchestrator-owned progress within the authorized semantic action may bind/rebind",
            "unexpected/external drift, conflict, scope/risk change, or failed preconditions stop",
            "Existing exact leases, ancestry checks, and separate target-merge/target-push bindings remain mandatory",
            "Keep receipts internal unless requested, needed for audit/debug, or required to explain",
            "repair_owner=diagnose-and-fix",
            "repair_contract_path=references/fix-implementer-contract.md",
            "Review findings use review-code’s action gate. On explicit `fix`",
            "Initial approval never repairs",
            "capture its result SHA before deriving `target_push`",
            "merge never pushes by itself",
            "This skill never executes live incident containment or production mutation",
            "hand off to that procedure; without both, stop",
            "Never execute it within this skill",
            "`../../references/tool-usage.md`",
            "accepted/current `docs/testing/workflow.md`",
            "From the approved target worktree, resolve `implement`",
            "If `.superdeveloper/preferences.yml` is missing",
            "never create it in root or silently",
            "Include the internal receipt only on request",
        ]:
            self.assertIn(compact_text(needle), compact)
        for stale in [
            "## Approval Record",
            "proposed Approval Record values",
            "requires new approval",
            "Any live containment/production mutation lacks both",
            "target merge and target push are one safety boundary",
        ]:
            self.assertNotIn(stale, text)

    def test_fix_implementer_contract_recaptures_complete_starting_state(self) -> None:
        skill = read_repo("plugins/super-developer/skills/diagnose-and-fix/SKILL.md")
        contract_rel = (
            "plugins/super-developer/skills/diagnose-and-fix/references/fix-implementer-contract.md"
        )
        contract = read_repo(contract_rel)
        combined = compact_text(f"{skill}\n{contract}")
        self.assertIn("references/fix-implementer-contract.md", skill)
        self.assertIn("references/fix-implementer-contract.md", read_repo("plugins/super-developer/README.md"))
        self.assertLessEqual(len(contract.splitlines()), 150)
        for needle in [
            "Authority comes only from the complete packet plus this contract",
            "perform no repository action and return `BLOCKED`",
            "complete starting binding: HEAD and all category manifests/checksums, normally clean",
            "file type, Git/index-compatible mode, symlink target, and content digest or binary provenance",
            "recapture and compare the complete starting binding before action and immediately before its first write",
            "Any drift is `BLOCKED`",
            "Recapture HEAD and all four state categories",
            "compare every manifest/checksum to the packet",
            "immediately before the first write, recapture the complete starting binding again",
            "Never create/remove worktrees or branches",
            "stage; commit; merge; rebase; push/fetch/pull; reset",
            "Do not run destructive commands",
            "`BLOCKED: scope_expansion`",
            "The parent must compare this report and actual repository state",
        ]:
            self.assertIn(compact_text(needle), combined)

    def test_worktree_delivery_uses_atomic_cas_fail_fast_and_bound_cleanup(self) -> None:
        skill = read_repo("plugins/super-developer/skills/worktree/SKILL.md")
        bugfix = read_repo("plugins/super-developer/skills/worktree/references/bugfix-hotfix-workflow.md")
        cleanup = read_repo("plugins/super-developer/skills/worktree/references/cleanup-safety.md")
        combined = compact_text(f"{skill}\n{bugfix}\n{cleanup}")
        for needle in [
            "expected_remote_destination_sha=<sha|absent>",
            "expected_remote_ref_sha=<sha|absent>",
            "worktree_path=<path>; worktree_head=<sha>; worktree_state=<checksum>",
            "local_ref=<full refs/heads/...>; local_ref_kind=direct; local_ref_sha=<sha>",
            "landing_worktree=<path|not_applicable>; landing_head=<sha|not_applicable>",
            "REMOTE_LINE=\"$(git ls-remote --heads origin \"$DEST_REF\")\"",
            "if [[ \"$REMOTE_SHA\" == \"$SOURCE_SHA\" ]]",
            "remote already at source; no-op",
            "git push --force-with-lease=\"$DEST_REF:\" origin",
            "git merge-base --is-ancestor \"$EXPECTED\" \"$SOURCE_SHA\"",
            "git push --force-with-lease=\"$DEST_REF:$EXPECTED\" origin",
            "git merge-base --is-ancestor \"$EXPECTED\" \"$RESULT_SHA\"",
            "git push --force-with-lease=\"$TARGET_REF:$EXPECTED\" <remote>",
            "exact qualified lease is server-side CAS",
            "A command error cannot mean absent",
            "Every block is fresh Bash with `set -euo pipefail`",
            "git merge-base --is-ancestor <source-sha> <pre-merge-target-sha>",
            "Status 1 alone means merge needed",
            "LANDING_HEAD=\"$(git -C \"$LANDING\" rev-parse HEAD)\"",
            "test \"$LANDING_HEAD\" = \"<approved-integration-head>\"",
            "test \"$LANDING_HEAD\" = \"<approved-delivery-result-sha>\"",
            "git -C \"$LANDING\" merge-base --is-ancestor <approved-local-ref-sha> \"$LANDING_HEAD\"",
            "local_ref_kind=direct",
            "if git symbolic-ref -q \"$REF\"; then exit 1; fi",
            "git update-ref --no-deref -d \"$REF\" <approved-local-ref-sha>",
            "REF=refs/heads/wp/<feature>/<WP-ID>",
            "REF=refs/heads/feature/<feature>",
            "REF=refs/heads/artifacts/<feature>",
            "REF=refs/heads/spike/<name>",
            "concurrent movement fails CAS",
            "printf 'RESULT_SHA=%s\\n' \"$RESULT_SHA\"",
            "INTEGRATION_WORKTREE=<approved-integration-worktree>",
            "cd \"$INTEGRATION_WORKTREE\"",
            "an existing approved non-root integration path substitutes exactly",
            "Locked local target stays unchanged",
            "never claim local target was merged",
            "Orchestration may run at `$PROJECT_ROOT`",
            "Root files/index are user-owned: never switch, edit, merge, or deliver there",
            "Planned feature/sidecar pushes remain governed by their existing approved Execution Contract/checkpoint gates",
            "do not claim those contracts contain user-known SHA/snapshot fields",
            "Remote deletion never follows failed local cleanup",
            "test \"$RECAPTURED_WORKTREE_STATE_CHECKSUM\" = \"<approved-worktree-state-checksum>\"",
            "Bugfix/hotfix additionally recapture current landing HEAD/state",
            "Sidecar/spike require exact HEAD/state/status proof and direct-ref CAS",
        ]:
            self.assertIn(compact_text(needle), combined)

        for text in [bugfix, cleanup]:
            blocks = re.findall(r"```bash\n(.*?)```", text, flags=re.DOTALL)
            self.assertTrue(blocks)
            for block in blocks:
                self.assertEqual("set -euo pipefail", block.strip().splitlines()[0])

        push_lines = [
            line.strip()
            for line in f"{bugfix}\n{cleanup}".splitlines()
            if line.strip().startswith("git push")
        ]
        self.assertFalse(any(re.search(r"git push\s+--force(?:\s|$)", line) for line in push_lines))
        self.assertFalse(
            any("--force-with-lease" in line and "--force-with-lease=" not in line for line in push_lines)
        )
        self.assertNotIn("race or remote advance after validation is rejected by normal", combined.lower())
        self.assertNotIn("git push <remote> <result-sha>:refs/heads/<target-ref>", combined)
        self.assertNotIn("git merge-base --is-ancestor feature/<feature> <target-ref>", combined)
        self.assertNotIn("Default both to `main`", combined)
        self.assertNotRegex(combined, r"git branch -(?:d|D)\s")
        for line in cleanup.splitlines():
            if "git update-ref" in line and " -d " in line:
                self.assertIn("--no-deref", line)
        self.assertGreaterEqual(f"{bugfix}\n{cleanup}".count("printf 'RESULT_SHA=%s\\n'"), 2)

        disposable_block = next(
            block for block in re.findall(r"```bash\n(.*?)```", cleanup, re.DOTALL)
            if "refs/heads/artifacts/<feature>" in block
        )
        self.assertLess(
            disposable_block.index("git worktree remove"),
            disposable_block.index("git update-ref --no-deref -d"),
        )

    def test_primary_root_resolver_and_no_deref_delete_are_race_safe(self) -> None:
        skill = read_repo("plugins/super-developer/skills/worktree/SKILL.md")
        match = re.search(r"## Primary Root Resolver.*?```bash\n(.*?)```", skill, flags=re.DOTALL)
        self.assertIsNotNone(match)
        resolver = match.group(1)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "primary"
            linked = Path(tmp) / "linked"
            root.mkdir()

            def git(*args: str, cwd: Path = root, check: bool = True) -> subprocess.CompletedProcess[str]:
                return subprocess.run(
                    ["git", *args], cwd=cwd, check=check, text=True, capture_output=True
                )

            git("init", "-b", "main")
            git("config", "user.name", "Prompt Tests")
            git("config", "user.email", "prompt-tests@example.invalid")
            (root / "tracked.txt").write_text("one\n", encoding="utf-8")
            git("add", "tracked.txt")
            git("commit", "-m", "initial")
            git("worktree", "add", "-b", "linked-test", str(linked), "HEAD")

            self.assertEqual(str(linked.resolve()), git("rev-parse", "--show-toplevel", cwd=linked).stdout.strip())
            resolved = subprocess.run(
                ["bash", "-c", resolver], cwd=linked, check=True, text=True, capture_output=True
            )
            self.assertIn(f"PROJECT_ROOT={root.resolve()}", resolved.stdout)
            self.assertFalse((linked / ".worktrees").exists())

            old_sha = git("rev-parse", "HEAD").stdout.strip()
            git("branch", "cleanup-race", old_sha)
            (root / "tracked.txt").write_text("two\n", encoding="utf-8")
            git("commit", "-am", "advance")
            new_sha = git("rev-parse", "HEAD").stdout.strip()
            git("update-ref", "refs/heads/cleanup-race", new_sha, old_sha)

            stale_delete = git(
                "update-ref", "--no-deref", "-d", "refs/heads/cleanup-race", old_sha, check=False
            )
            self.assertNotEqual(0, stale_delete.returncode)
            self.assertEqual(new_sha, git("rev-parse", "refs/heads/cleanup-race").stdout.strip())
            git("update-ref", "--no-deref", "-d", "refs/heads/cleanup-race", new_sha)
            self.assertNotEqual(
                0, git("show-ref", "--verify", "refs/heads/cleanup-race", check=False).returncode
            )

            git("symbolic-ref", "refs/heads/cleanup-alias", "refs/heads/main")
            self.assertEqual(
                "refs/heads/main",
                git("symbolic-ref", "-q", "refs/heads/cleanup-alias").stdout.strip(),
            )
            symbolic_delete = git(
                "update-ref", "--no-deref", "-d", "refs/heads/cleanup-alias", new_sha,
                check=False,
            )
            self.assertEqual(0, symbolic_delete.returncode)
            self.assertEqual(new_sha, git("rev-parse", "refs/heads/main").stdout.strip())
            self.assertNotEqual(
                0, git("symbolic-ref", "-q", "refs/heads/cleanup-alias", check=False).returncode
            )

    def test_local_review_resolves_base_and_returns_parent_owned_repairs(self) -> None:
        local = read_repo("plugins/super-developer/skills/review-code/references/local-workflow.md")
        compact = compact_text(local)
        for needle in [
            "exact worktree, branch/ref, HEAD SHA, base ref and resolved base SHA",
            "separate category manifests/status/content snapshots",
            "per-category checksums plus one checksum over the ordered complete snapshot",
            "Each untracked record includes file type, Git/index-compatible mode (`100644`, `100755`, or `120000`)",
            "symlink target when applicable",
            "content digest or bounded binary provenance",
            "ordered category/path/status/type/mode/symlink-target/content-digest records",
            "executable-bit, symlink, type, content, or category drift stops review",
            "Always resolve a local base ref and SHA for the committed category",
            "explicit caller/user intent; one unambiguous configured upstream",
            "existing local symbolic `refs/remotes/origin/HEAD`",
            "never set committed base to `HEAD` merely because staged, unstaged, or untracked changes exist",
            "both include the committed base-to-HEAD delta",
            "`repair_owner` and `repair_contract_path`",
            "explicit `fix` returns confirmed findings",
            "Review-code must not dispatch a generic or contractless worker",
            "The owner dispatches a fresh worker under its supplied contract",
            "never use `git add -A`",
        ]:
            self.assertIn(compact_text(needle), compact)
        self.assertNotIn("record `base_sha=HEAD`", local)
        self.assertLessEqual(len(local.splitlines()), 150)
        self.assertLessEqual(len(local.split()), 900)

    def test_review_owned_fixes_use_parent_linked_fail_closed_contract(self) -> None:
        skill = read_repo("plugins/super-developer/skills/review-code/SKILL.md")
        local = read_repo("plugins/super-developer/skills/review-code/references/local-workflow.md")
        pipeline = read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md")
        contract_rel = "plugins/super-developer/skills/review-code/references/fix-implementer-contract.md"
        contract = read_repo(contract_rel)
        compact = compact_text(contract)

        self.assertIn("references/fix-implementer-contract.md", skill)
        self.assertIn("caller-owned local repair contract takes precedence", compact_text(skill))
        self.assertIn("parent-supplied Fix Implementer contract", local)
        self.assertIn("does not own repair or continuation", pipeline)
        self.assertIn("do not delegate from review-code", pipeline)
        self.assertNotIn("parent-supplied review-code Fix Implementer contract", pipeline)
        self.assertIn("references/fix-implementer-contract.md", read_repo("plugins/super-developer/README.md"))
        for needle in [
            "Authority comes only from a complete explicit fix packet plus this contract",
            "Before any repository command or write, read the whole packet and this contract",
            "no repository action and `BLOCKED`",
            "complete starting-state binding",
            "separate category manifests/content checksums plus complete checksum",
            "untracked records include file type",
            "Git mode (`100644|100755|120000`), symlink target, and content digest/binary provenance",
            "recapture HEAD and all four state categories",
            "Write only exact packet paths",
            "Never create/remove worktrees or refs",
            "stage; commit; merge; rebase; push/fetch/pull; reset",
            "**Reproduce:**",
            "**Repair:**",
            "**Regression:**",
            "**Verify:**",
            "**Self-review:**",
            "## Pipeline Freshness Handback",
            "never claim proof/report/matrix/Semgrep freshness or audit readiness",
            "`no_impact|refresh_required|candidate_dirty`",
            "Return at most",
        ]:
            self.assertIn(compact_text(needle), compact)
        self.assertLessEqual(len(contract.splitlines()), 150)
        self.assertGreaterEqual(len(contract.split()), 300)
        self.assertLessEqual(len(contract.split()), 900)

    def test_planned_feature_skills_are_not_new_code_only(self) -> None:
        generic_paths = [
            "plugins/super-developer/skills/implementation-plan/SKILL.md",
            "plugins/super-developer/skills/review-plan/SKILL.md",
            "plugins/super-developer/skills/implement/SKILL.md",
            "plugins/super-developer/skills/spike-to-plan/SKILL.md",
            "plugins/super-developer/README.md",
        ]
        combined = compact_text("\n".join(read_repo(rel) for rel in generic_paths))
        for rel in generic_paths:
            self.assertNotIn("greenfield", read_repo(rel).lower(), rel)
        for needle in [
            "fresh Slice-first planned-feature",
            "approved change may target a new or existing system",
            "supports approved changes to new or existing systems",
            "New and existing-system changes",
        ]:
            self.assertIn(compact_text(needle), combined)

        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        execution = read_repo("plugins/super-developer/skills/implement/references/execution-contract.md")
        for text in [implement, execution]:
            self.assertIn(
                "existing-system contract change not explicitly approved",
                compact_text(text),
            )
            self.assertNotIn("existing-feature contract change", text)
        self.assertIn("greenfield/no-strategy repositories", read_repo("plugins/super-developer/skills/testing/SKILL.md"))

    def test_parent_owned_shared_contracts_avoid_reference_second_hops(self) -> None:
        review = read_repo("plugins/super-developer/skills/review-code/SKILL.md")
        pipeline = read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md")
        worktree = read_repo("plugins/super-developer/skills/worktree/SKILL.md")
        feature = read_repo("plugins/super-developer/skills/worktree/references/feature-package-workflow.md")

        for path in [
            "../../references/package-verification-report.md",
            "../../references/package-lifecycle.md",
        ]:
            self.assertIn(path, review)
        review_compact = compact_text(review)
        self.assertIn("Load and pass `../../references/package-verification-report.md`", review_compact)
        self.assertIn("Pass `../../references/package-lifecycle.md` as a labeled path", review_compact)
        self.assertIn("load it only when proof/report freshness or non-bypass routing is disputed", review_compact)
        pipeline_compact = compact_text(pipeline)
        self.assertIn("parent-supplied package-verification-report contract", pipeline_compact)
        self.assertIn("parent-supplied package-lifecycle contract only when", pipeline_compact)
        self.assertNotIn("../../../references/package-", pipeline)
        self.assertIn("../../references/artifact-store.md", worktree)
        self.assertIn("parent-supplied artifact-store", compact_text(feature))
        self.assertNotIn("../../references/artifact-store.md", feature)

        plugin = read_repo("plugins/super-developer/README.md")
        for needle in [
            "complete caller-bound or locally captured state",
            "committed base-to-HEAD plus staged, unstaged, and untracked files together",
            "owning repair contract when supplied",
        ]:
            self.assertIn(needle, plugin)

    def test_interface_contract_thread_is_present_and_consistent(self) -> None:
        authority = read_repo("plugins/super-developer/references/conceptualize-slice-authority.md")
        for needle in [
            "**Interface contract**",
            "Forbidden behaviors",
            "ambiguous",
            "contradicted",
            "over-broad",
        ]:
            self.assertIn(needle, authority, "conceptualize-slice-authority.md")

        for rel in [
            "plugins/super-developer/skills/conceptualize/references/slice-template.md",
            "plugins/super-developer/skills/implementation-plan/references/conceptualize-inputs.md",
            "plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md",
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/skills/implement/references/repair-agent-contract.md",
            "plugins/super-developer/skills/audit/references/audit-subagent-contract.md",
        ]:
            self.assertIn("Interface contract", read_repo(rel), rel)

        self.assertIn("Forbidden behaviors", read_repo("plugins/super-developer/skills/implement/references/package-verification.md"))
        self.assertIn("[INTERFACE-EXACTNESS]", read_repo("plugins/super-developer/skills/audit/references/audit-subagent-contract.md"))
        self.assertIn("interface-contract seams", read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md"))

    def test_package_verification_deliverable_matrix_contract_is_durable(self) -> None:
        contract_rel = "plugins/super-developer/references/package-verification-report.md"
        contract = read_repo(contract_rel)
        verifier = read_repo("plugins/super-developer/skills/implement/references/package-verification.md")
        artifacts = read_repo("plugins/super-developer/references/slice-first-artifacts.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")
        risks = read_repo("plugins/super-developer/references/known-risk-patterns.md")

        for rel in [
            contract_rel,
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/references/slice-first-artifacts.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/references/known-risk-patterns.md",
        ]:
            self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)

        for token in [
            "### Deliverable Completeness Matrix",
            "Source ID",
            "Row Type",
            "Deliverable",
            "Evidence Type",
            "Evidence Refs",
            "Exactness / Risk Disposition",
            "Verdict",
            "delivered",
            "missing",
            "partial",
            "contradicted",
            "unverified",
        ]:
            self.assertIn(token, contract)

        for token in [
            "exact H3 ID",
            "VE-<n>",
            "RISK-<slug-or-n>",
            "verifier-selected",
            "planner seeds do not limit discovery",
            "non-applicable probes must not become checklist noise",
        ]:
            self.assertIn(token, contract)

        for token in [
            "Package Markdown Digest",
            "Proof Digest",
            "Assigned Slices",
            "Assigned Slice Digests",
            "Matrix Source Snapshot",
            "Worktree",
            "Git Ref",
            "Commit",
        ]:
            self.assertIn(token, contract)

        for token in [
            "code:<repo-relative-path>",
            "test:<repo-relative-path>",
            "static:<repo-relative-path>#section",
            "command:proof#Commands Run:<label>",
            "manual:scenario=<specific scenario>; observed=<specific result>",
            "unsafe, nonexistent, placeholder, fabricated, or structurally vague anchors",
        ]:
            self.assertIn(token, contract)

        for token in [
            "`### Slice Closure Review` and proof prose alone as completion blockers",
            "Helpers validate shape, row coverage, clean verdict state, bindings, and evidence-anchor structure only",
            "Package verifiers and final auditors judge semantic truthfulness and sufficiency",
        ]:
            self.assertIn(token, verifier)

        self.assertIn(contract_rel, verifier)
        self.assertIn(contract_rel, artifacts)
        self.assertIn(contract_rel, dispatch)
        self.assertIn("Required first reads", dispatch)
        self.assertIn("hidden chat context", dispatch)
        self.assertIn("deliverable completeness matrix", artifacts)
        self.assertIn("RISK-<...>", risks)
        self.assertIn("rationale/disposition", risks)

    def test_b1_adh02_standard_routes_meaningful_boundary_before_consumption(self) -> None:
        routing = read_repo("plugins/super-developer/references/assurance-routing.md")
        planner = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md"
        )
        gates = read_repo(
            "plugins/super-developer/skills/implement/references/package-integration-gates.md"
        )
        compact = compact_text("\n".join([routing, planner, gates]))
        for token in [
            "`standard` is the default",
            "meaningful internal boundaries",
            "A coherent leaf package may route `final`",
            "producer with a dependent",
            "fresh `PASS B[i]`",
            "pre-consumption unlock",
            "exactly one owner and one side of freeze",
        ]:
            self.assertIn(token, compact)
        self.assertLess(
            compact_text(routing).index("fresh `PASS B[i]`"),
            compact_text(routing).index("Registry `done`, proof, `SELF_REVIEW`"),
        )

    def test_b1_adh10_dependency_unlock_binds_exact_candidate_and_contract(self) -> None:
        routing = read_repo("plugins/super-developer/references/assurance-routing.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        dispatch = read_repo(
            "plugins/super-developer/skills/implement/references/package-dispatch.md"
        )
        combined = compact_text("\n".join([routing, lifecycle, dispatch]))
        for token in [
            "Stable Candidate Identity",
            "code commit/tree and base/diff identity",
            "proof and selected runtime-evidence digests",
            "profile/mode",
            "consumed-contract digests",
            "fresh `PASS B[i]`",
            "registry `done`",
            "proof rows",
            "`SELF_REVIEW`",
            "helper success alone",
            "does not unlock dependents",
        ]:
            self.assertIn(token, combined)
        self.assertIn("exact Stable Candidate Identity and consumed-contract digests", compact_text(dispatch))

    def test_b1_adh12_high_trigger_promotes_instead_of_passing(self) -> None:
        routing = read_repo("plugins/super-developer/references/assurance-routing.md")
        verifier = read_repo(
            "plugins/super-developer/skills/implement/references/package-verification.md"
        )
        compact = compact_text(routing)
        self.assertIn("Precedence is `high > standard > low`", compact)
        for token in [
            "One high trigger wins",
            "Runtime discovery never bypasses this order",
            "invalidates the affected Stable Candidate Identity",
            "promotes the Technical Plan Baseline",
            "advances the Effective Authorization Digest and checkpoint",
            "returns `PROFILE_INVALID`, never `PASS`",
            "Downgrade requires a newly reviewed baseline and Effective Authorization Digest",
            "ask the user only if envelope, material-risk acceptance, protected effects, covered actions, or budgets change",
        ]:
            self.assertIn(token, compact)
        self.assertIn("return `PROFILE_INVALID`", verifier)
        self.assertIn("never PASS,\ndowngrade, self-promote", verifier)

    def test_b1_adh22_uses_selected_causal_evidence_without_volume_gate(self) -> None:
        affected = [
            "plugins/super-developer/references/assurance-routing.md",
            "plugins/super-developer/references/work-packages.md",
            "plugins/super-developer/references/package-lifecycle.md",
            "plugins/super-developer/references/package-verification-report.md",
            "plugins/super-developer/references/slice-first-artifacts.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/skills/implement/references/package-integration-gates.md",
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/skills/implementation-plan/references/spec-template.md",
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
        ]
        texts = {path: read_repo(path) for path in affected}
        work_packages = compact_text(texts[affected[1]])
        report = compact_text(texts[affected[3]])
        verifier = compact_text(texts[affected[7]])
        for token in [
            "canonical minimum-sufficient test acceptance rule",
            "smallest maintainable causal evidence set",
            "One causal test or observation may prove multiple related requirements",
            "stop adding tests",
            "Only a concrete defect blocks",
        ]:
            self.assertIn(token, work_packages)
        for token in [
            "### Selected Causal Evidence",
            "Evidence Anchor",
            "Behavior / Risk Proven",
            "Causal Sufficiency",
            "Substitutes / Fixtures",
            "Fresh Command Result",
            "Do not census changed test populations",
            "rereview the suite",
        ]:
            self.assertIn(token, report)
        self.assertIn("Build `### Selected Causal Evidence`, not an exhaustive changed-population census", verifier)
        self.assertIn("Do not rereview the suite", verifier)
        for path in affected:
            with self.subTest(path=path):
                self.assertLessEqual(len(texts[path].splitlines()), 150, path)
        b1_contracts = "\n".join(texts[path] for path in affected)
        self.assertNotIn("### Test Review Scope", b1_contracts)
        self.assertNotIn("Changed Population", b1_contracts)

    def test_b3_final_assurance_is_serial_freeze_scoped_and_role_bounded(self) -> None:
        routing = read_repo("plugins/super-developer/references/assurance-routing.md")
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        review = read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md")
        audit = read_repo("plugins/super-developer/skills/audit/SKILL.md")
        convergence = read_repo("plugins/super-developer/references/orchestration-convergence.md")
        combined = compact_text("\n".join([routing, implement, gates, review, audit, convergence]))

        for equation in [
            "F → C(code-risk PASS, completion PASS) → V",
            "F → R(PASS/closure) → U(PASS, F, R) → V",
            "F → R(PASS/closure) → S[*] (each named integrated lens PASS, F, R) → U(PASS, F, R, S[*]) → V",
        ]:
            self.assertIn(equation, combined)
        self.assertIn("one cold combined read-only verifier", routing.lower())
        self.assertIn("do not dispatch a separate reviewer, auditor, or specialist", compact_text(routing))
        self.assertIn("`B[i]` roles are pre-freeze only and", gates)
        self.assertIn("final specialists post-freeze only", gates)
        self.assertIn("new `F`, and obtains `R` PASS/closure before", compact_text(routing))
        self.assertIn("read-only and return-only", combined)
        self.assertIn("only the Delivery Owner dispatches", combined)
        self.assertIn("Selected Causal Evidence` deeply plus only changed", compact_text(gates))
        self.assertIn("selectively falsifies high-value claims without suite rereview", compact_text(gates))
        self.assertIn("B4 owns executable final receipt validation", routing)
        for stale in ["ready_for_audit", "Audit can run as sibling", "audit-dispatch prerequisite"]:
            self.assertNotIn(stale, "\n".join([routing, implement, gates, review, audit, convergence]))

    def test_section_scoped_state_binding_prompt_contract_is_guarded(self) -> None:
        contract = read_repo("plugins/super-developer/references/package-verification-report.md")
        artifacts = read_repo("plugins/super-developer/references/slice-first-artifacts.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        tool_usage = read_repo("plugins/super-developer/references/tool-usage.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        review = read_repo("plugins/super-developer/skills/review-code/SKILL.md")
        audit = read_repo("plugins/super-developer/skills/audit/SKILL.md")
        contract_compact = compact_text(contract)
        tool_compact = compact_text(tool_usage)

        for token in ["Assigned Slices", "Assigned Slice Digests", "Matrix Source Snapshot"]:
            self.assertIn(token, contract)
        for token in [
            "emit-state-binding",
            "--worktree",
            "--git-ref",
            "--commit",
            "--verified-at",
            "path|tier|H3-ID=sha256:<64-hex>",
            "entries separated by `; `",
            "must not contain `|`, `=`, or the delimiter sequence `; `",
            "grammar delimiters",
            "must_satisfy section blocks only",
            "context_only_slice_drift",
            "fail closed before drift classification",
            "paste it verbatim",
            "do not hand-compute digests",
        ]:
            self.assertIn(token, contract_compact)
        for token in [
            "JSON on success",
            "JSON `errors` plus `advisories` on failure",
            "aggregated by `validate-final`",
            "State Binding grammar delimiter rejection",
            "verifiers never hand-compute",
        ]:
            self.assertIn(token, tool_compact)
        for text in [artifacts, lifecycle, tool_usage, gates, review, audit]:
            compact = compact_text(text)
            self.assertIn("context_only_slice_drift", compact)
            self.assertIn("non-blocking by default", compact)
            self.assertIn("affected-surface classification", compact)
        binding_text = "\n".join([
            contract[contract.index("## State Binding"):],
            lifecycle[lifecycle.index("## Freshness Rules"):lifecycle.index("## Final Readiness")],
            gates[gates.index("## Report Shape and Freshness"):gates.index("## Rejection and Repair")],
            context_window(review, "context_only_slice_drift", 400),
            context_window(audit, "context_only_slice_drift", 400),
        ]).lower()
        for token in [
            "backward-" + "c" + "ompat",
            "migr" + "ation",
            "leg" + "acy",
            "deprec" + "ation",
            "grand" + "father",
            "version-" + "gate",
            "format " + "upgraded",
            "re-" + "pin required",
        ]:
            self.assertNotIn(token, binding_text)

    def test_package_completion_helper_gates_done_unlock_merge_and_final_handoff(self) -> None:
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        self.assertIn("clean `validate-package-complete`", implement)
        for text in [gates, lifecycle]:
            with self.subTest(command_surface=text[:40]):
                self.assertIn('python3 "${SUPER_DEVELOPER_PLUGIN_ROOT}/assets/sliceproof.py" validate-package-complete', text)
                self.assertIn('--artifact-root "$ARTIFACT_ROOT" --code-root "$CODE_ROOT"', text)
                self.assertIn('".tasks/<feature>/tasks.json" --package <WP-ID>', text)
        for text in [dispatch, lifecycle]:
            with self.subTest(surface=text[:40]):
                self.assertIn("fresh `PASS`", text)
                self.assertIn("clean `validate-package-complete`", text)
                self.assertIn("registry `done`", text)
                self.assertIn("proof rows", text)
        for needle in [
            "before accepting/merging as complete",
            "marking `done`",
            "unlocking dependents",
            "final readiness handoff",
            "Helper success is mechanical",
        ]:
            self.assertIn(needle, gates + lifecycle)
        self.assertIn("profile-required PASS outputs and `V`", lifecycle)

    def test_planner_risk_seeding_preserves_verifier_discovery(self) -> None:
        artifact = read_repo("plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md")
        planner = read_repo("plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md")
        checklist = read_repo("plugins/super-developer/skills/implementation-plan/references/validation-checklist.md")
        packages = read_repo("plugins/super-developer/references/work-packages.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")

        for text in [artifact, planner, checklist, packages]:
            with self.subTest(surface=text[:40]):
                self.assertIn("VE-<n>", text)
                self.assertRegex(text, r"exact interfaces?|exact interface")
                self.assertIn("forbidden", text)
                for risk in [
                    "interactive UI",
                    "retry/fail-closed",
                    "trigger precedence",
                    "lifecycle/restart/reaper",
                    "cache invalidation",
                    "model/default precedence",
                    "generated defaults",
                    "state pollution",
                ]:
                    self.assertIn(risk, text)
        for text in [artifact, checklist, packages, dispatch]:
            with self.subTest(discovery=text[:40]):
                self.assertIn("do not limit verifier discovery", text)
                self.assertIn("changed code/diff", text)
                self.assertIn("known failure modes", text)
        self.assertIn("verifier-owned triggered risk selection", dispatch)

    def test_repair_freshness_uses_semantic_closure_and_proportional_reruns(self) -> None:
        packages = read_repo("plugins/super-developer/references/work-packages.md")
        artifact = read_repo("plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md")
        checklist = read_repo("plugins/super-developer/skills/implementation-plan/references/validation-checklist.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")
        verifier = read_repo("plugins/super-developer/skills/implement/references/package-verification.md")
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")

        packages_compact = compact_text(packages).lower()
        artifact_compact = compact_text(artifact).lower()
        checklist_compact = compact_text(checklist).lower()
        lifecycle_compact = compact_text(lifecycle).lower()
        gates_compact = compact_text(gates).lower()
        verifier_compact = compact_text(verifier).lower()

        for token in [
            "id-only",
            "sequencing prerequisites",
            "lower bound on readiness",
            "not an impact or staleness graph",
            "existing package `notes`",
            "consumed output, contract, or evidence",
        ]:
            self.assertIn(token, packages_compact)
        for token in [
            "dependencies are id-only durable sequencing prerequisites",
            "rationale belongs in package `notes`",
            "runtime impact or failure alone does not create an edge",
        ]:
            self.assertIn(token, artifact_compact)
        for token in [
            "unless one consumes a durable prerequisite",
            "temporary file/contract/proof overlap changes batching or serialization",
            "without inventing a dependency edge",
        ]:
            self.assertIn(token, checklist_compact)

        for token in [
            "provisional classification in orchestrator state and repair/verifier packets",
            "never a registry field or standalone impact receipt",
            "sequencing lower bound",
            "producing prerequisites",
            "consumers in any lifecycle state",
            "not represented by a dependency edge",
            "until no new affected surface appears",
            "failure, commit existence, merge ancestry, or dependency reachability alone does not stale a package",
            "actual code diff",
            "final code/proof/command-evidence state",
            "until stable",
            "classify uncertainty as unbounded",
            "fresh focused verification",
        ]:
            self.assertIn(token, lifecycle_compact)
        for token in [
            "apply `orchestration-convergence.md`",
            "classify the finding",
            "one logical primary implementation owner",
            "actual diff and invalidate affected reports",
            "actual-production-path targeted evidence",
            "affected broad regression before refreshing proof",
            "focused verification only for bounded impact",
            "fresh report and bindings",
            "only after the fresh report",
        ]:
            self.assertIn(token, gates_compact)
        for token in [
            "fresh independent pass and report",
            "carried-forward matrix row",
            "source inputs",
            "remain unchanged and uncontradicted",
            "dependency reachability alone does not require full verification",
            "repair owner to refresh affected proof rows",
            "final impact closure before verifier dispatch",
            "inspect but do not edit proof state",
        ]:
            self.assertIn(token, verifier_compact)
        focused_start = verifier.index("Focused re-verification is")
        focused_end = verifier.index("\n\nRequire the repair owner", focused_start)
        focused_rule = compact_text(verifier[focused_start:focused_end]).lower()
        self.assertIn(
            "widen for material/shared/sensitive/ cross-contract or uncertain impact",
            focused_rule,
        )
        self.assertNotIn("test-review populations", focused_rule)

        repair = gates[gates.index("## Rejection and Repair"):gates.index("## Conflict Handling")]
        repair_compact = compact_text(repair).lower()
        ordered = [
            "reproduce and repair one coherent root cause",
            "reclassify the actual diff",
            "actual-production-path targeted evidence",
            "affected broad regression before refreshing proof/command evidence",
            "refresh affected proof state",
            "run `validate-proof`",
            "focused verification only for bounded impact",
            "the verifier returns the fresh report and bindings",
            "only after the fresh report (boundary) or stable final candidate run `validate-package-complete`",
        ]
        for earlier, later in zip(ordered, ordered[1:]):
            self.assertLess(repair_compact.index(earlier), repair_compact.index(later))

        self.assertNotIn("after repair, update affected proof rows", verifier_compact)
        self.assertNotIn("full verification for delivered behavior", gates_compact)
        self.assertNotIn("if impact touches delivered behavior", lifecycle_compact)
        self.assertIn("selecting repair/post-gate impact, freshness, or rerun scope", implement.lower())
        for needle in [
            "package Markdown/digest",
            "assigned Slice source/digest",
            "matrix source snapshot",
            "matrix evidence anchors",
        ]:
            self.assertIn(needle, lifecycle)
        self.assertIn("matrix rows/evidence anchors", dispatch)
        self.assertIn("classified rerun scope", dispatch)

    def test_final_audit_consumes_matrices_as_reconciler_and_stack_backstop(self) -> None:
        audit_skill = read_repo("plugins/super-developer/skills/audit/SKILL.md")
        audit_contract = read_repo("plugins/super-developer/skills/audit/references/audit-subagent-contract.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        workflow = read_repo("plugins/super-developer/skills/worktree/references/feature-package-workflow.md")

        for token in [
            "bounded stack packet",
            "top integrated worktree/code state",
            "one or more related task/Slice artifact sets",
            "clean deliverable matrix",
            "validate-final",
        ]:
            self.assertIn(token, audit_skill)
        for token in [
            "deliverable-matrix reconciliation",
            "### Deliverable Completeness Matrix",
            "matrix source bindings",
            "evidence-anchor structure",
            "Matrix Reconciliation",
            "targeted skeptic backstop",
            "not a full second package verifier",
            "interface-bearing rows",
            "triggered risk rows",
            "global/cross-package seams",
            "stacked-feature obligations",
            "claims cheaply disprovable from code",
            "stale source bindings",
            "invalid evidence refs",
        ]:
            self.assertIn(token, audit_contract)
        for text in [gates, lifecycle]:
            with self.subTest(surface=text[:40]):
                self.assertIn("top integrated", text)
                self.assertIn("task/Slice artifact", text)
                self.assertRegex(text.lower(), r"do not audit .*follow-up")
                self.assertRegex(text.lower(), r"base feature|base/follow-up")
        workflow_compact = compact_text(workflow).lower()
        self.assertIn("top code state", workflow_compact)
        self.assertIn("base/follow-up artifact set", workflow_compact)
        self.assertIn("validate-package-complete", gates)
        self.assertIn("same top state", lifecycle)

    def test_review_code_uses_matrices_as_context_only_with_refresh_classification(self) -> None:
        review_skill = read_repo("plugins/super-developer/skills/review-code/SKILL.md")
        pipeline = read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md")

        review_skill_compact = compact_text(review_skill)
        for token in [
            "deliverable matrices are context only",
            "not a third deliverable-completeness gate",
            "proof/report invalidation",
            "invalidated matrix",
            "generic affected-surface impact classification",
        ]:
            self.assertIn(token, review_skill_compact)
        for token in [
            "Use deliverable matrices as context only",
            "Do not own full deliverable completeness",
            "proof/report invalidation",
            "dirty matrix",
            "matrix rows/evidence anchors",
            "source bindings",
            "boundedness",
            "do not run full final gates solely because any new commit exists",
            "full matrix bodies",
            "proof/report transcripts",
            "separate completion ledgers",
        ]:
            self.assertIn(token, pipeline)

    def test_delivery_gate_prompt_changes_stay_progressively_disclosed(self) -> None:
        line_capped = [
            "plugins/super-developer/skills/audit/SKILL.md",
            "plugins/super-developer/skills/audit/references/audit-subagent-contract.md",
            "plugins/super-developer/skills/review-code/SKILL.md",
            "plugins/super-developer/skills/review-code/references/pipeline-report.md",
            "plugins/super-developer/skills/implement/SKILL.md",
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md",
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md",
            "plugins/super-developer/references/work-packages.md",
            "plugins/super-developer/references/package-lifecycle.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/skills/implement/references/package-integration-gates.md",
            "plugins/super-developer/skills/skill-authoring/SKILL.md",
            "plugins/super-developer/skills/skill-authoring/references/orchestrator-worker-contracts.md",
        ]
        for rel in line_capped:
            with self.subTest(path=rel):
                self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)

        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        self.assertNotIn("### Deliverable Completeness Matrix", implement)
        self.assertNotIn("Source ID | Row Type", implement)
        self.assertIn("Dispatch only the profile equation", compact_text(implement))
        self.assertIn("semantic truth remains with independent assurance", compact_text(gates))
        self.assertIn("Readiness requires package evidence and", gates)
        self.assertIn("profile-required PASS outputs plus `V` bound to the same `F`", compact_text(gates))

        for rel in [
            "plugins/super-developer/skills/audit/SKILL.md",
            "plugins/super-developer/skills/review-code/SKILL.md",
        ]:
            text = read_repo(rel)
            self.assertNotIn("Source ID | Row Type", text, rel)
            self.assertNotIn("plugins/super-developer/skills/", text, rel)
        self.assertIn("Never deep-link its private references", read_repo("plugins/super-developer/skills/skill-authoring/SKILL.md"))

    def test_skill_authoring_enforces_mid_tier_consumer_followability(self) -> None:
        skill = read_repo("plugins/super-developer/skills/skill-authoring/SKILL.md")
        worker_contract = read_repo(
            "plugins/super-developer/skills/skill-authoring/references/orchestrator-worker-contracts.md"
        )
        skill_compact = compact_text(skill)
        worker_contract_compact = compact_text(worker_contract)
        do_start = skill.rindex("\n## Do\n")
        stop_start = skill.index("\n## Stop if\n", do_start)
        do_section = skill[do_start:stop_start]

        for token in [
            "competent mid-tier target agent",
            "Consumer Followability Gate",
            "one representative normal task",
            "ambiguous, failure, or high-risk task",
            "must guess a material action",
            "a vague quality instruction is insufficient",
            "one focused clarification",
            "inspect and report findings without modifying files",
            "Inspect repository instructions",
            "load `references/orchestrator-worker-contracts.md` before evaluating or drafting it",
        ]:
            self.assertIn(token, skill_compact)

        self.assertLess(do_section.index("Inspect repository instructions"), do_section.index("Decide whether"))
        review_start = do_section.index("If the mode is **review**")
        create_start = do_section.index("For **create or revise** mode only")
        self.assertLess(review_start, create_start)
        review_branch = do_section[review_start:create_start]
        create_branch = do_section[create_start:]
        self.assertIn("stop; do not draft, add, update, or edit files", review_branch)

        contract_path = "references/orchestrator-worker-contracts.md"
        audit_command = "scripts/audit-skill.py <skill-dir-or-SKILL.md>"
        self.assertEqual(skill.count(contract_path), 1)
        self.assertEqual(skill.count(contract_path), do_section.count(contract_path))
        self.assertEqual(skill.count(audit_command), 2)
        self.assertEqual(skill.count(audit_command), do_section.count(audit_command))
        self.assertIn(audit_command, review_branch)
        self.assertIn(audit_command, create_branch)

        for token in [
            "competent mid-tier worker",
            "missing or conflicting authority",
            "one normal packet and one missing-input or high-risk packet",
            "read its packet and worker contract before any write, command, or external side effect",
            "perform no action and return `BLOCKED`",
            "Only the orchestrator may clarify with the user or expand worker authority",
        ]:
            self.assertIn(token, worker_contract_compact)


    def test_closure_complexity_and_execution_feasibility_have_single_owners(self) -> None:
        packages = read_repo("plugins/super-developer/references/work-packages.md")
        artifact = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md"
        )
        checklist = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md"
        )
        planner = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md"
        )
        rubric = read_repo("plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md")
        artifact_compact = compact_text(artifact)
        checklist_compact = compact_text(checklist)
        planner_compact = compact_text(planner)
        rubric_compact = compact_text(rubric).lower()

        for token in [
            "## Package Sizing and Closure Complexity",
            "semantic closure complexity",
            "fixed proof/report/verification cost",
            "one coherent state/evidence boundary",
            "runtime surfaces/environments",
            "harness/helper/fixture populations",
            "proof/report refresh fanout",
            "never universal thresholds",
            "route unresolved empirical uncertainty to a spike",
        ]:
            self.assertIn(token.lower(), compact_text(packages).lower())
        for consumer in [artifact, checklist, planner, rubric]:
            self.assertNotIn("## Package Sizing and Closure Complexity", consumer)

        for token in [
            "material execution feasibility remains unresolved",
            "smallest credible bounded probe or broad-only justification",
            "testing-authority provenance",
            "exact budgets come from the resolved authority",
        ]:
            self.assertIn(token, artifact_compact)
        for token in [
            "materially unresolved execution feasibility",
            "Cost or breadth alone does not trigger a profile",
            "testing-authority provenance",
            "resolved testing authority",
        ]:
            self.assertIn(token, checklist_compact)
        self.assertIn("route empirical assumptions to a spike", planner_compact)
        for token in [
            "repo-backed command/harness/contract/fixture",
            "cost or breadth alone does not trigger a profile",
            "bounded, deterministic where controllable, cleanup-aware",
            "requires spike routing rather than implementation-time guessing",
        ]:
            self.assertIn(token, rubric_compact)

        combined = compact_text("\n".join([packages, artifact, checklist, planner, rubric])).lower()
        self.assertNotRegex(combined, r"\b(?:exactly|roughly)\s+\d+\s*(?:-|–|to)\s*\d+\s+scenarios\b")

    def test_execution_readiness_and_runtime_envelope_propagate_to_workers(self) -> None:
        tool = read_repo("plugins/super-developer/references/tool-usage.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")
        contract = read_repo("plugins/super-developer/skills/implement/references/execution-contract.md")
        package_agent = read_repo(
            "plugins/super-developer/skills/implement/references/package-agent-contract.md"
        )
        repair_agent = read_repo(
            "plugins/super-developer/skills/implement/references/repair-agent-contract.md"
        )
        generic = read_repo(
            "plugins/super-developer/skills/testing/references/core/generic-testing.md"
        )
        delegation = read_repo(
            "plugins/super-developer/skills/testing/references/delegation-packets.md"
        )

        for token in [
            "## Command Safety and Runtime Envelope",
            "stable identity",
            "Use exact budgets from resolved testing authority",
            "routine-safe deterministic local command",
            "progress/completion signal",
            "termination method",
            "cleanup obligation",
            "terminate owned descendants/process groups",
            "Do not repeat the same failing command or assertion",
        ]:
            self.assertIn(token, tool)

        dispatch_compact = compact_text(dispatch).lower()
        for token in [
            "trigger readiness only when material execution feasibility remains unresolved",
            "omit routine non-trigger bookkeeping",
            "smallest approved bounded probe",
            "documented broad-only branch",
            "broad or costly execution requires a clean readiness result",
            "classify plan, testing-authority/precondition, implementation, or orchestration ownership",
            "triggered readiness result/blockers only when applicable",
        ]:
            self.assertIn(token, dispatch_compact)

        contract_compact = compact_text(contract).lower()
        for token in [
            "resolved testing authority",
            "testing authority:",
            "omit when clearly non-triggered",
            "broad-only justification",
        ]:
            self.assertIn(token, contract_compact)
        pipeline = contract[contract.index("Pipeline:"):contract.index("Stop conditions:")]
        for earlier, later in [
            ("run root-aware final validation", "dispatch only the selected serial equation"),
            ("dispatch only the selected serial equation", "batch eligible repairs"),
            ("batch eligible repairs", "CAS-checkpoint `V`"),
            ("CAS-checkpoint `V`", "push the feature branch"),
        ]:
            self.assertLess(pipeline.index(earlier), pipeline.index(later))
        package_agent_compact = compact_text(package_agent).lower()
        repair_agent_compact = compact_text(repair_agent).lower()
        self.assertIn("packet-provided command identity", package_agent_compact)
        self.assertIn("timeout or uncertain cleanup as non-pass", package_agent_compact)
        self.assertIn("apply packet command identity", repair_agent_compact)
        self.assertIn("distinct identity/expected signal", repair_agent)

        generic_compact = compact_text(generic).lower()
        self.assertIn("no credible narrower check exists", generic_compact)
        self.assertIn("uncertain termination or cleanup is not a pass", generic_compact)
        self.assertIn("do not impose universal serialization", generic_compact)
        self.assertIn("Return after each failure", delegation)
        self.assertIn("relevant state/evidence/strategy delta", delegation)

    def test_pipeline_delivery_owner_call_return_is_canonical(self) -> None:
        convergence = read_repo("plugins/super-developer/references/orchestration-convergence.md")
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        planning = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        review_plan = read_repo("plugins/super-developer/skills/review-plan/SKILL.md")
        spike = read_repo("plugins/super-developer/skills/spike-to-plan/SKILL.md")
        review_code = read_repo("plugins/super-developer/skills/review-code/SKILL.md")
        pipeline = read_repo("plugins/super-developer/skills/review-code/references/pipeline-report.md")
        audit = read_repo("plugins/super-developer/skills/audit/SKILL.md")
        worktree = read_repo("plugins/super-developer/skills/worktree/references/feature-package-workflow.md")

        for token in [
            "Only the Delivery Owner advances",
            "caller and exact `return_to` stage",
            "terminal disposition",
            "The child planner/reviewer does not start or resume implementation itself",
            "A serious-cluster identity",
        ]:
            self.assertIn(token, convergence)

        self.assertIn("planned-feature Delivery Owner", implement)
        self.assertIn("no child restarts implementation", implement)
        self.assertIn("never invoke review or implementation", planning)
        self.assertIn("A nested review never invokes `implement`", compact_text(review_plan))
        self.assertIn("return it to the Delivery\n    Owner", spike)
        self.assertIn("never owns repair or lifecycle continuation", review_code)
        self.assertIn("does not own repair or continuation", pipeline)
        self.assertIn("never repair or advance the lifecycle", audit)
        self.assertIn("prove the candidate differs only by the\napproved status mutation", worktree)

    def test_triggered_preflight_projects_architecture_invariants_without_a_ledger(self) -> None:
        preflight = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/design-preflight.md"
        )
        planning = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        planner = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md"
        )
        spec = read_repo("plugins/super-developer/skills/implementation-plan/references/spec-template.md")
        authoring = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md"
        )
        checklist = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md"
        )
        review = read_repo(
            "plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md"
        )

        for token in [
            "Skip narrow, mechanical, low-risk plans",
            "ARCHITECTURE_INVARIANTS",
            "authoritative owner plus every ingress and mutation path",
            "ordering and linearization/publication point",
            "winning and losing generation/lease/owner behavior",
            "actual-production-path seams",
            "earliest credible affected broad-regression tripwire",
            "Do not add an architecture ledger",
        ]:
            self.assertIn(token, preflight)
        self.assertIn("sanitized accepted source baseline", planning)
        self.assertIn("accepted architecture invariants", planning)
        self.assertIn("accepted source baseline", planner)
        self.assertIn("## Accepted Source Baseline", spec)
        self.assertIn("## Architecture Invariants", spec)
        self.assertIn("actual-production-path seam", authoring)
        self.assertIn("broad regression before freeze", authoring)
        self.assertIn("triggered `ARCHITECTURE_INVARIANTS`", checklist)
        self.assertIn("losing-owner rules", review)
        self.assertLessEqual(len(preflight.splitlines()), 150)
        self.assertLessEqual(len(authoring.splitlines()), 150)
        self.assertLessEqual(len(checklist.splitlines()), 150)

    def test_behavior_first_verification_precedes_claims_and_freeze(self) -> None:
        verifier = read_repo(
            "plugins/super-developer/skills/implement/references/package-verification.md"
        )
        report = read_repo("plugins/super-developer/references/package-verification-report.md")
        audit = read_repo(
            "plugins/super-developer/skills/audit/references/audit-subagent-contract.md"
        )
        testing = read_repo(
            "plugins/super-developer/skills/testing/references/core/generic-testing.md"
        )
        execution = read_repo(
            "plugins/super-developer/skills/implement/references/execution-contract.md"
        )
        review = read_repo("plugins/super-developer/skills/review-code/SKILL.md")
        pipeline_review = read_repo(
            "plugins/super-developer/skills/review-code/references/pipeline-report.md"
        )

        verifier_compact = compact_text(verifier)
        ordered = [
            "### 1. Accepted obligations and invariants",
            "### 2. Bound production diff and actual path",
            "### 3. Causal tests and observations",
            "### 4. Implementer claims and proof reconciliation",
            "### 5. Deliverable matrix and triggered risks",
        ]
        for earlier, later in zip(ordered, ordered[1:]):
            self.assertLess(verifier.index(earlier), verifier.index(later))
        for token in [
            "Do not read implementer proof",
            "forces production preconditions/branch",
            "real collaborator outcome",
            "falsifies forbidden outcomes",
            "would fail if the invariant broke",
            "labels or outcome names alone are insufficient",
            "affected broad regression",
            "whether planned or discovered during inspection",
        ]:
            self.assertIn(token, verifier_compact)
        self.assertNotIn("contracted affected broad regression", verifier_compact)
        self.assertIn("A matrix indexes", report)
        self.assertIn("synthetic outcomes", report)
        audit_ordered = [
            "each artifact-root SPEC/registry/package Markdown",
            "frozen integrated production diff/code",
            "causal tests/runtime observations",
            "proof, verification reports",
        ]
        for earlier, later in zip(audit_ordered, audit_ordered[1:]):
            self.assertLess(audit.index(earlier), audit.index(later))
        self.assertIn("labels or counters alone are not evidence", compact_text(testing))
        pipeline = execution[execution.index("Pipeline:"):execution.index("Stop conditions:")]
        self.assertLess(pipeline.index("affected broad regression"), pipeline.index("proof/report refresh"))
        self.assertIn("first establishes accepted obligations and frozen production paths", review)
        pipeline_review_compact = compact_text(pipeline_review)
        pipeline_review_ordered = [
            "accepted SPEC/Slice obligations first",
            "frozen integration code/diff",
            "causal tests/runtime observations",
            "Reconcile implementer `SELF_REVIEW` and proof claims",
            "only afterward inspect package reports, deliverable matrices",
        ]
        for earlier, later in zip(pipeline_review_ordered, pipeline_review_ordered[1:]):
            self.assertLess(
                pipeline_review_compact.index(earlier), pipeline_review_compact.index(later)
            )
        for text in [verifier, report, audit, testing, pipeline_review]:
            self.assertLessEqual(len(text.splitlines()), 150)

    def test_phase_one_cold_review_authority_corrections_are_fail_closed(self) -> None:
        pipeline = read_repo(
            "plugins/super-developer/skills/review-code/references/pipeline-report.md"
        )
        repair = read_repo(
            "plugins/super-developer/skills/implement/references/repair-agent-contract.md"
        )
        planning = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        review = read_repo("plugins/super-developer/skills/review-plan/SKILL.md")
        rubric = read_repo(
            "plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md"
        )

        for forbidden in ["Fix Verification", "fix delegation", "fix_batches"]:
            self.assertNotIn(forbidden, pipeline)
        self.assertIn("Delivery Owner handoff", pipeline)
        self.assertIn("missing Delivery Owner repair/verification handback", pipeline)

        self.assertNotIn("while the circuit remains open", repair)
        self.assertIn("whose circuit remains closed", repair)
        self.assertIn("An open circuit never authorizes another repair command", repair)

        self.assertIn("old accepted/new candidate state", planning)
        self.assertIn("not the final accepted amendment handback", planning)
        for token in [
            "old and new accepted commits",
            "affected requirements/Slices/packages/assignments",
            "production/test surfaces",
            "stale proofs/reports/execution",
            "evidence-backed preserved state",
            "old-to-new package map",
        ]:
            self.assertIn(token, review)
        self.assertIn("candidate handback starts from the old accepted commit", rubric)

    def test_package_repair_circuit_is_progress_sensitive_and_two_strike(self) -> None:
        convergence = read_repo("plugins/super-developer/references/orchestration-convergence.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        repair_agent = read_repo(
            "plugins/super-developer/skills/implement/references/repair-agent-contract.md"
        )
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        combined = compact_text(
            "\n".join([convergence, dispatch, gates, repair_agent, lifecycle, implement])
        ).lower()

        for token in [
            "requirement-gap",
            "architecture-invalidation",
            "implementation-defect",
            "integration-regression",
            "test-fidelity-gap",
            "evidence-stale-or-contradicted",
            "confidence-enhancement",
            "failure mechanism",
            "architectural surface",
            "accepted invariant/contract",
            "agent, signature, label, commit, and timeout are not identity",
            "first failed closure",
            "second failed closure",
            "explicit user approval",
        ]:
            self.assertIn(token, combined)
        for non_progress in ["new agent", "model", "prompt", "commit", "status", "report", "matrix row"]:
            self.assertIn(non_progress, compact_text(convergence).lower())

        self.assertIn("one logical primary implementation owner", gates)
        self.assertIn("successor inherits state and never resets strikes", dispatch)
        self.assertIn("Owner identity changes never reset strikes", repair_agent)
        self.assertIn("no child restarts implementation", implement)

        repair = gates[gates.index("## Rejection and Repair"):gates.index("## Conflict Handling")]
        self.assertLess(repair.index("actual-production-path"), repair.index("refreshing proof"))
        self.assertLess(repair.index("`validate-proof`"), repair.index("focused verification"))
        self.assertLess(repair.index("fresh report"), repair.index("`validate-package-complete`"))
        self.assertNotIn("delegate a fresh repair agent", repair)
        self.assertNotIn("changes ownership", compact_text(repair).lower())

    def test_feasibility_workflow_and_spike_routes_are_followable(self) -> None:
        planning = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        planner = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md"
        )
        review = read_repo("plugins/super-developer/skills/review-plan/SKILL.md")
        resolution = read_repo(
            "plugins/super-developer/skills/review-plan/references/plan-review-resolution.md"
        )
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        spike = read_repo("plugins/super-developer/skills/spike-to-plan/SKILL.md")

        planning_compact = compact_text(planning)
        planner_compact = compact_text(planner)
        review_compact = compact_text(review)
        resolution_compact = compact_text(resolution)
        implement_compact = compact_text(implement)
        spike_compact = compact_text(spike)
        for token in [
            "resolve testing authority",
            "Missing workflow alone does not block read-only planning",
            "invoke `testing` to establish/update it or stop",
            "testing-authority provenance only for a triggered feasibility profile",
            "omit routine non-trigger state",
        ]:
            self.assertIn(token, planning_compact)
        self.assertIn("testing-authority provenance", planner_compact)
        self.assertIn("triggered testing-authority provenance", review_compact)
        self.assertIn("invoke `spike-to-plan`", review_compact)
        self.assertIn("through `implementation-plan`", review_compact)
        self.assertIn("### empirical feasibility blocker", resolution_compact)
        self.assertIn("must return through `implementation-plan`", resolution_compact)
        for token in [
            "invoke `spike-to-plan`",
            "through `implementation-plan` and `review-plan`",
            "revalidate before resuming",
        ]:
            self.assertIn(token, implement_compact)

        for token in [
            "../../references/tool-usage.md",
            "testing authority",
            "invoke `testing`",
            "explicitly bounded broad-only probe",
            "uncertain cleanup is inconclusive evidence",
            "Do not repeat an unchanged command",
            "fresh `implementation-plan` invocation",
        ]:
            self.assertIn(token, spike_compact)
        self.assertLessEqual(len(spike.splitlines()), 150)

    def test_execution_risk_probes_and_observability_stay_non_gating(self) -> None:
        risks = read_repo("plugins/super-developer/references/known-risk-patterns.md")
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")

        for token in [
            "Harness discovery and readiness",
            "Fixture-contract fidelity",
            "Asynchronous settlement and process ownership",
            "Timeout and fail-fast amplification",
            "do not persist these prompts as registry fields or generic checklists",
        ]:
            self.assertIn(token, risks)

        for token in [
            "Non-gating traces",
            "repair identity/progress",
            "Neither may mutate state",
            "required as proof",
            "non-gating stage timing when available",
        ]:
            self.assertIn(token, lifecycle + implement)
        self.assertNotIn("execution-trace", lifecycle + implement)

    def test_worker_contract_supporting_references_are_parent_owned(self) -> None:
        implementation = read_repo("plugins/super-developer/skills/implementation-plan/SKILL.md")
        planner = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md"
        )
        artifact = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md"
        )
        concept = read_repo(
            "plugins/super-developer/skills/implementation-plan/references/conceptualize-inputs.md"
        )
        implement = read_repo("plugins/super-developer/skills/implement/SKILL.md")
        workflow = read_repo("plugins/super-developer/skills/testing/references/workflow-contract.md")

        for path in [
            "../../references/conceptualize-slice-authority.md",
            "../../references/work-packages.md",
            "../../references/slice-first-artifacts.md",
            "references/conceptualize-inputs.md",
            "references/artifact-authoring.md",
            "references/validation-checklist.md",
        ]:
            self.assertIn(path, implementation)
        for path in [
            "references/package-agent-contract.md",
            "references/repair-agent-contract.md",
            "references/package-verification.md",
        ]:
            self.assertIn(path, implement)

        self.assertNotRegex(planner, r"`(?:\.\./|references/)[^`]+\.md`")
        self.assertNotIn("`${SUPER_DEVELOPER_PLUGIN_ROOT}/references/", artifact + concept)
        self.assertNotIn("`references/strategy-interview.md`", workflow)
        self.assertIn("Return `BLOCKED`", planner)

    def test_execution_reliability_prompt_changes_respect_skill_authoring_caps(self) -> None:
        capped = [
            "plugins/super-developer/skills/implementation-plan/SKILL.md",
            "plugins/super-developer/skills/review-plan/SKILL.md",
            "plugins/super-developer/skills/implement/SKILL.md",
            "plugins/super-developer/skills/testing/SKILL.md",
            "plugins/super-developer/skills/spike-to-plan/SKILL.md",
            "plugins/super-developer/references/work-packages.md",
            "plugins/super-developer/references/tool-usage.md",
            "plugins/super-developer/references/known-risk-patterns.md",
            "plugins/super-developer/references/package-lifecycle.md",
            "plugins/super-developer/skills/implementation-plan/references/design-preflight.md",
            "plugins/super-developer/skills/implementation-plan/references/artifact-authoring.md",
            "plugins/super-developer/skills/implementation-plan/references/validation-checklist.md",
            "plugins/super-developer/skills/implementation-plan/references/planner-agent-contract.md",
            "plugins/super-developer/skills/review-plan/references/plan-review-rubrics.md",
            "plugins/super-developer/skills/implement/references/execution-contract.md",
            "plugins/super-developer/skills/implement/references/package-dispatch.md",
            "plugins/super-developer/skills/implement/references/package-integration-gates.md",
            "plugins/super-developer/skills/implement/references/package-verification.md",
            "plugins/super-developer/skills/implement/references/package-agent-contract.md",
            "plugins/super-developer/skills/implement/references/repair-agent-contract.md",
            "plugins/super-developer/skills/testing/references/core/generic-testing.md",
            "plugins/super-developer/skills/testing/references/strategy-interview.md",
            "plugins/super-developer/skills/testing/references/delegation-packets.md",
        ]
        for rel in capped:
            with self.subTest(path=rel):
                self.assertLessEqual(len(read_repo(rel).splitlines()), 150, rel)


if __name__ == "__main__":
    unittest.main()
