from __future__ import annotations

import json
import re
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
            "Operate as a testing workflow meta-skill",
            "first establish or load the repository's approved testing workflow",
            "Do not default to standalone test edits or commands",
            "Choose an explicit mode before acting: initialize/update workflow, author/alter tests using an accepted/current canonical workflow, or delegate execution-oriented work",
            "Keep this eager prompt meta-level",
            "project methodology in `docs/testing/workflow.md` or linked companion docs",
            "use skill references only as optional proposal/adaptation aids",
        ]:
            self.assertIn(" ".join(needle.split()), skill_compact)

        for needle in [
            "It is not a stack methodology and does not authorize test writes, test runs, installs, browser use, network access, live services, or config/CI changes",
            "Use this reference only as an optional proposal/adaptation aid",
            "Approved project workflow docs (`docs/testing/workflow.md` and linked companions) govern repository-specific testing behavior",
            "this reference must not override them or authorize standalone test edits/runs",
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
            "Check `docs/testing/workflow.md` before test edits, commands, or delegation",
            "If it is missing, stale, ambiguous, conflicting, unsafe, refused, or not accepted/current, establish, update, adopt, migrate, or link through that canonical file first",
            "`missing`: no canonical entry point exists",
            "Run candidate discovery and ask the user whether to adopt, migrate, link, or initialize through `docs/testing/workflow.md` before test edits, command runs, or delegation",
            "`stale/ambiguous/conflicting`: a workflow exists but its commands, paths, stack assumptions, approval gates, safety stance, or acceptance/currentness conflict",
            "`unsafe/refused`: the workflow or user decision would require unsafe, secret-bearing, production, or unapproved side effects, or the user refuses canonical workflow creation/update/adoption/linking",
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
            "Candidate choice alone is not enough to proceed",
            "First write or update `docs/testing/workflow.md` so it incorporates or references the approved candidate",
            "If the user refuses all canonical-file options, stop",
            "Do not perform one-off test edits, command execution, or delegation",
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
            "name the recommended strategy and why repo evidence supports it",
            "ask one focused confirmation or risk-boundary question when evidence is insufficient",
            "For missing browser E2E strategy, inspect the web stack, existing scripts/tests, app entry points, dev-server assumptions, auth/data risks, and docs",
            "strategy establishment still stops at a documentation proposal",
            "does not install dependencies, create browser config, write tests, run browsers, start services, use recordings, touch secrets, access the network, edit config/CI/orchestration, or execute tests",
            "Before writing root `AGENTS.md` or any `docs/testing/*` file, present a draft summary and proposed file changes",
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
            "Explicit testing-workflow lifecycle requests include initialize, update, adopt, migrate, link, and revise, including greenfield repositories with no/minimal tests, no strategy, or no canonical workflow",
            "For greenfield/no-strategy repos or explicit initialize, update, adopt, migrate, link, or revise requests, load `references/strategy-interview.md`",
            "Treat absent/minimal tests, no documented strategy, and existing testing docs as source evidence, not a reason to skip the interview",
            "run the strategy interview; existing docs are source material, not a skip condition",
            "Ordinary authoring, alteration, or execution may use an accepted/current workflow without the full interview when it adequately answers the task",
            "missing, stale, ambiguous, conflicting, unsafe, or insufficient workflows fail closed to establish/update mode",
            "Explicit initialize, update, adopt, migrate, link, or revise requests still route to the strategy interview; existing docs are source material",
            "For greenfield/no-strategy repositories and explicit initialize, update, adopt, migrate, link, or revise requests, load `references/strategy-interview.md` and run the strategy interview before accepted workflow-doc writes",
            "Existing workflows, absent/minimal tests, candidates, and companion docs inform the recommendation but do not skip the interview",
            "`missing`: no canonical entry point exists, including greenfield repositories with no/minimal tests or no documented testing strategy",
            "Run candidate discovery and ask the user whether to adopt, migrate, link, or initialize through `docs/testing/workflow.md` before test edits, command runs, or delegation",
            "candidates are source material only: they govern test work only after `docs/testing/workflow.md` exists, is accepted/current, and incorporates or references them through an approved adopt, migrate, link, or initialize decision",
            "Candidate choice alone is not enough to proceed",
            "First write or update `docs/testing/workflow.md` so it incorporates or references the approved candidate",
            "candidate handling: any adopted, migrated, or linked candidate is incorporated or referenced by the canonical workflow entry before it can govern delegated work",
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
            "folder/taxonomy and central feature test index or coverage-index stance (used, linked, or not used) for new plans, tests, evidence, reports, plus legacy stay-put or migration stance",
            "feature/domain plan policy, approved plan path/version expectations, and plan-before-work gates",
            "The workflow draft should name: confidence goals; mandatory and active conditional domains; plan, test, evidence, report, and central feature test index stance; execution choices and approvals; reliability/cleanup semantics; legacy stance; companion docs; redaction; and the update procedure",
            "Recommend a clean structure for new plans/tests going forward, but leave legacy tests where they are unless the user explicitly asks for migration",
            "Keep plans high-level and reviewable. They are scenario/deliverable contracts, not command recipes",
            "Feature/domain plan starter (high-level scenario contract, not a command recipe)",
            "Nontrivial/high-risk work includes live integration, browser E2E, cross-stack behavior, multi-scenario coverage, risky data/setup, or approval-gated tooling/config changes",
            "Before covered writes or execution, create a Markdown plan, present it, and wait for explicit approval in the current task",
            "Interview decisions feed the repository testing workflow, not a default standalone questionnaire",
            "Draft or revise `docs/testing/workflow.md` and linked `docs/testing/*` companions with the accepted strategy decisions",
            "A separate checklist or decision record is optional for large or high-risk strategy updates, not the default",
            "These plan/report paths are not substitutes for the canonical workflow entry point",
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
            "Approved plan path/version: <path+version, or workflow-approved no-plan reason>",
            "Current-task approvals already granted: <exact approvals or none>",
            "Approval-gated actions to stop for: <commands/writes/browser/live/network/etc.>",
            "Plan-to-result report: map plan scenarios to authored tests/results, selected choices, evidence, skipped/not-run items, redaction, cleanup status, and follow-up risks",
            "approved plan path/version and scenario-to-test/result mapping, or workflow-approved no-plan reason",
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
            "Authoring, alteration, and execution are delegated only after canonical workflow consultation",
            "If no executor or sub-agent is available, return a workflow-aware instruction packet and stop",
            "The main agent remains an orchestrator",
            "workflow state: `docs/testing/workflow.md` exists, is accepted/current for the task, and has been read by the orchestrator before delegation",
            "candidate handling: any adopted, migrated, or linked candidate is incorporated or referenced by the canonical workflow entry before it can govern delegated work",
            "Testing delegation packet",
            "User goal: <requested testing outcome>",
            "Precondition: docs/testing/workflow.md exists, is accepted/current, and governs this task",
            "Workflow entry: docs/testing/workflow.md",
            "Companion docs to consult: <paths or none>",
            "Required first step: read the canonical workflow entry and companions; receipt/report must cite them",
            "Allowed scope: <test files/fixtures/helpers/docs/commands/evidence surfaces>",
            "Disallowed scope: <production/runtime code, unapproved config/dependencies/CI/orchestration, etc.>",
            "Current-task approvals already granted: <exact approvals or none>",
            "Approval-gated actions to stop for: <commands/writes/browser/live/network/etc.>",
            "Command safety: classify commands, use bounded timeouts, no unsafe/default live side effects",
            "Evidence/reporting: sanitized commands, outputs, artifacts, outcomes, cleanup, blocked reasons",
            "Product-failure routing: do not edit product code; report reproduction and route to owner",
            "The executor's first reportable fact should prove workflow consultation",
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
            "If optional generic, web, or browser references are useful, load them only after canonical workflow state is resolved or while drafting an initialization/update proposal; never let them override approved project workflow docs",
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

    def test_diagnose_and_fix_recommends_one_route_and_reviewed_delivery(self) -> None:
        text = read_repo("plugins/super-developer/skills/diagnose-and-fix/SKILL.md")
        compact = " ".join(text.split())
        for needle in [
            "exactly one recommended route",
            "stop/missing-info",
            "localized `worktree` fix",
            "`implementation-plan`",
            "named diagnostic spike",
            "approve the recommended route",
            "shared `../../references/model-preferences.md`",
            "resolved model/policy",
            "After any delivered localized fix, invoke `review-code`",
            "push `origin bugfix/<name>`",
            "unless the user explicitly excluded remote side effects",
        ]:
            self.assertIn(" ".join(needle.split()), compact)
        self.assertNotIn("Ask for one explicit approval choice", text)

    def test_worktree_bugfix_push_and_target_merge_skip_are_explicit(self) -> None:
        bugfix = read_repo("plugins/super-developer/skills/worktree/references/bugfix-hotfix-workflow.md")
        for forbidden in [
            "fix, commit, verify",
            "fix, commit, verify the focused bug scenario",
            "fix, commit, verify the production failure path",
        ]:
            self.assertNotIn(forbidden, bugfix.lower())
        for needle in [
            "git push -u origin bugfix/<name>",
            "after verification and clean `review-code`",
            "Commit bugfix changes only after verification and CLEAN `review-code`/approved delivery",
            "Commit hotfix branch changes only after verification, CLEAN `review-code`, and approved delivery",
            "not approval to merge into or push `<base-branch>`, `feature/<feature>`, or",
            "git worktree add .worktrees/hotfix-<name> -b hotfix/<name> <base-branch>",
            "git worktree add .worktrees/hotfix-merge-<name> <base-branch>",
            "git push origin <base-branch>",
            "git merge <base-branch> --no-edit",
            "`main` may be an example value for `<base-branch>`",
            "remote side effects",
        ]:
            self.assertIn(needle, bugfix)
        for line in bugfix.splitlines():
            if re.search(r"\bmain\b", line):
                self.assertIn("`main` may be an example value for `<base-branch>`", line)

        cleanup = read_repo("plugins/super-developer/skills/worktree/references/cleanup-safety.md")
        for needle in [
            "git merge-base --is-ancestor feature/<feature> <target-ref>",
            "already merged; skip the target merge",
            "git merge --no-ff feature/<feature>",
            "Production hotfix worktrees stay until the hotfix merge to `<base-branch>`",
            "<worktree-on-base-branch>",
        ]:
            self.assertIn(needle, cleanup)
        self.assertNotIn("hotfix merge to `main`", cleanup)
        self.assertNotIn("<worktree-on-main>", cleanup)

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
            "return JSON on stdout",
            "return JSON on stderr with `errors` and a top-level `advisories` array",
            "`validate-final` aggregates advisories across packages",
            "State Binding grammar delimiter rejection",
            "the verifier computes no digests",
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
            "mechanical signal only",
        ]:
            self.assertIn(needle, gates + lifecycle)
        self.assertIn("review-code readiness and final audit PASS", lifecycle)

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

    def test_repair_freshness_uses_affected_surface_classification_and_proportional_reruns(self) -> None:
        lifecycle = read_repo("plugins/super-developer/references/package-lifecycle.md")
        gates = read_repo("plugins/super-developer/skills/implement/references/package-integration-gates.md")
        dispatch = read_repo("plugins/super-developer/skills/implement/references/package-dispatch.md")

        for text in [lifecycle, gates]:
            with self.subTest(surface=text[:40]):
                self.assertIn("affected-surface", text)
                self.assertIn("narrow", text)
                self.assertIn("bounded", text)
                self.assertIn("cannot be bounded", text)
                self.assertIn("delivered behavior", text)
                self.assertIn("evidence bindings", text)
                self.assertIn("contracts", text)
                self.assertIn("integration", text)
                self.assertRegex(text, r"safety/security/privacy/data")
                self.assertIn("source bindings", text)
                self.assertIn("validate-package-complete", text)
                self.assertIn("validate-proof", text)
                self.assertIn("package verification", text)
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
        self.assertIn("invoke `review-code` and `audit` only", compact_text(implement))
        self.assertIn("semantic truthfulness remains with package verification and final audit", gates)
        self.assertIn("Declare readiness only when package evidence, review-code readiness, and final audit PASS", gates)

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


if __name__ == "__main__":
    unittest.main()
