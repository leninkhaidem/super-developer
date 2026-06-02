from __future__ import annotations

import copy
import importlib.util
import tempfile
from pathlib import Path
import unittest


VALIDATOR_PATH = Path(__file__).resolve().parents[1] / "validate-tasks-json.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_tasks_json", VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load validator module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


validator = load_validator()


class ConceptualizeSchemaValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        self.feature_dir = Path(self.tmpdir.name) / ".tasks" / "conceptualize-fixture"
        self.feature_dir.mkdir(parents=True)
        self.spec_path = self.feature_dir / "SPEC.md"
        self.spec_path.write_text(
            """# Conceptualize Fixture Specification

## Overview
Exercise Conceptualize schema validation.

## Conceptualize Inputs
- Index: `.planning/missing/index.md`

## Requirements
- REQ-1: The fixture must validate Conceptualize metadata shape.

## Acceptance Criteria
- AC-1: Invalid Conceptualize shape is rejected deterministically.
""",
            encoding="utf-8",
        )
        self.tasks_path = self.feature_dir / "tasks.json"

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def valid_plan(self) -> dict:
        return {
            "schema_version": 3,
            "feature": "conceptualize-fixture",
            "title": "Conceptualize Fixture",
            "description": "Exercise Conceptualize metadata shape.",
            "created_at": "2026-05-29T00:00:00Z",
            "status": "planned",
            "conceptualize": {
                "index": ".planning/missing/index.md",
                "slice_coverage": {
                    "state": "zero_slices",
                    "entries": [],
                    "rationale": "Selected workspace has no Slice Markdown files.",
                },
            },
            "design_decisions": [],
            "context_bundles": [],
            "work_packages": [
                {
                    "id": "WP1",
                    "title": "Schema package",
                    "description": "Validate schema shape.",
                    "task_ids": ["P1-T001"],
                    "depends_on": [],
                    "parallel_safe_with": [],
                    "primary_paths": ["plugins/super-developer/assets/validate-tasks-json.py"],
                    "verification_commands": [],
                    "risk_tags": ["schema", "validation"],
                    "required_context_bundles": [],
                    "targeted_review_required": True,
                    "rationale": "Single-package schema fixture.",
                    "conceptualize_slices": [],
                }
            ],
            "phases": [
                {
                    "id": "P1",
                    "name": "Schema",
                    "description": "Schema validation.",
                    "order": 1,
                    "tasks": [
                        {
                            "id": "P1-T001",
                            "title": "Validate Conceptualize shape",
                            "description": "Validate mandatory Conceptualize fields.",
                            "status": "pending",
                            "dependencies": [],
                            "acceptance_criteria": [
                                {
                                    "id": "P1-T001-AC1",
                                    "criterion": "Conceptualize schema shape is enforced.",
                                    "source_refs": [
                                        {"type": "spec_req", "id": "REQ-1"},
                                        {"type": "spec_ac", "id": "AC-1"},
                                    ],
                                    "verification_hint": "Run validator unit tests.",
                                }
                            ],
                            "required_context_bundles": [],
                            "context": "Covers Conceptualize metadata schema.",
                        }
                    ],
                }
            ],
        }

    def approval(self) -> dict:
        return {
            "source": "user",
            "approved_at": "2026-05-29T00:00:00Z",
            "provenance": "User approved this exclusion during implementation planning.",
            "scope": "Only the named Slice outcome is deferred from this plan.",
            "refs": [{"type": "task_ac", "id": "P1-T001-AC1"}],
        }

    def covered_plan(self) -> dict:
        plan = self.valid_plan()
        plan["conceptualize"]["slice_coverage"] = {
            "state": "covered",
            "entries": [
                {
                    "path": ".planning/missing/slices/promoted.md",
                    "disposition": "promoted",
                    "promoted_refs": [
                        {"type": "spec_req", "id": "REQ-1"},
                        {"type": "spec_ac", "id": "AC-1"},
                        {"type": "task_ac", "id": "P1-T001-AC1"},
                    ],
                    "rationale": "Required outcome was promoted into authoritative plan artifacts.",
                },
                {
                    "path": ".planning/missing/slices/background.md",
                    "disposition": "background_only",
                    "rationale": "Background research only; no required outcome was promoted.",
                },
                {
                    "path": ".planning/missing/slices/conflict.md",
                    "disposition": "conflict",
                    "rationale": "Conflict is documented for semantic plan review.",
                },
                {
                    "path": ".planning/missing/slices/deferred.md",
                    "disposition": "deferred",
                    "rationale": "Deferred by user approval.",
                    "approval": self.approval(),
                },
                {
                    "path": ".planning/missing/slices/out-of-scope.md",
                    "disposition": "out_of_scope",
                    "rationale": "Excluded by user approval.",
                    "approval": self.approval(),
                },
                {
                    "path": ".planning/missing/slices/rejected.md",
                    "disposition": "rejected",
                    "rationale": "Rejected by user approval.",
                    "approval": self.approval(),
                },
            ],
        }
        return plan

    def errors_for(self, plan: dict) -> list[str]:
        errors, _ = validator.validate_tasks_json(
            plan, tasks_path=self.tasks_path, spec_path=self.spec_path
        )
        return errors

    def assertInvalid(self, plan: dict, expected: str) -> None:
        errors = self.errors_for(plan)
        self.assertTrue(
            any(expected in error for error in errors),
            msg=f"missing {expected!r} in errors: {errors}",
        )

    def test_valid_zero_slice_state_is_valid(self) -> None:
        self.assertEqual([], self.errors_for(self.valid_plan()))

    def test_valid_coverage_entries_are_valid(self) -> None:
        self.assertEqual([], self.errors_for(self.covered_plan()))

    def test_valid_conceptualize_shape_does_not_require_existing_markdown_paths(self) -> None:
        plan = self.covered_plan()
        plan["conceptualize"]["index"] = ".planning/nonexistent/index.md"
        plan["conceptualize"]["slice_coverage"]["entries"][0]["path"] = (
            ".planning/nonexistent/slices/also-missing.md"
        )
        plan["work_packages"][0]["conceptualize_slices"] = [
            {
                "path": ".planning/nonexistent/slices/package-background.md",
                "focus": "Schema-only background.",
            }
        ]

        self.assertEqual([], self.errors_for(plan))

    def test_schema_v3_top_level_conceptualize_is_required_with_index_and_coverage(self) -> None:
        missing = self.valid_plan()
        missing.pop("conceptualize")
        self.assertInvalid(missing, "conceptualize: expected object")

        malformed = self.valid_plan()
        malformed["conceptualize"] = []
        self.assertInvalid(malformed, "conceptualize: expected object")

        missing_index = self.valid_plan()
        missing_index["conceptualize"] = {
            "slice_coverage": missing_index["conceptualize"]["slice_coverage"]
        }
        self.assertInvalid(missing_index, "conceptualize.index: expected non-empty string")

        missing_coverage = self.valid_plan()
        missing_coverage["conceptualize"].pop("slice_coverage")
        self.assertInvalid(missing_coverage, "conceptualize.slice_coverage: expected object")

    def test_schema_v3_work_package_conceptualize_slices_are_required_object_arrays(self) -> None:
        cases = [
            (lambda plan: plan["work_packages"][0].pop("conceptualize_slices"), "work_packages[0].conceptualize_slices: expected array"),
            (lambda plan: plan["work_packages"][0].__setitem__("conceptualize_slices", {}), "work_packages[0].conceptualize_slices: expected array"),
            (lambda plan: plan["work_packages"][0].__setitem__("conceptualize_slices", ["slice.md"]), "work_packages[0].conceptualize_slices[0]: expected object"),
            (lambda plan: plan["work_packages"][0].__setitem__("conceptualize_slices", [{}]), "work_packages[0].conceptualize_slices[0].path: expected non-empty string"),
            (lambda plan: plan["work_packages"][0].__setitem__("conceptualize_slices", [{"path": ""}]), "work_packages[0].conceptualize_slices[0].path: expected non-empty string"),
            (lambda plan: plan["work_packages"][0].__setitem__("conceptualize_slices", [{"path": ".planning/x/slices/a.md", "focus": 3}]), "work_packages[0].conceptualize_slices[0].focus: expected string when present"),
        ]
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                plan = copy.deepcopy(self.valid_plan())
                mutate(plan)
                self.assertInvalid(plan, expected)

    def test_empty_slice_assignments_are_valid_for_packages_without_relevant_slices(self) -> None:
        plan = self.valid_plan()
        plan["work_packages"][0]["conceptualize_slices"] = []

        self.assertEqual([], self.errors_for(plan))

    def test_slice_coverage_shape_state_disposition_and_rationale_are_validated(self) -> None:
        cases = [
            (lambda plan: plan["conceptualize"].__setitem__("slice_coverage", []), "conceptualize.slice_coverage: expected object"),
            (lambda plan: plan["conceptualize"]["slice_coverage"].__setitem__("state", "partial"), "conceptualize.slice_coverage.state: expected one of"),
            (lambda plan: plan["conceptualize"]["slice_coverage"].__setitem__("entries", {}), "conceptualize.slice_coverage.entries: expected array"),
            (lambda plan: plan["conceptualize"]["slice_coverage"].pop("rationale"), "conceptualize.slice_coverage.rationale: expected non-empty string"),
            (lambda plan: plan["conceptualize"].__setitem__("slice_coverage", {"state": "covered", "entries": []}), "conceptualize.slice_coverage.entries: expected at least one item when state is 'covered'"),
            (lambda plan: plan["conceptualize"]["slice_coverage"].__setitem__("entries", [{"path": ".planning/missing/slices/a.md", "disposition": "promoted", "promoted_refs": [{"type": "spec_req", "id": "REQ-1"}]}]), "conceptualize.slice_coverage.entries: expected empty array when state is 'zero_slices'"),
            (lambda plan: plan["conceptualize"].__setitem__("slice_coverage", {"state": "covered", "entries": [{"path": ".planning/missing/slices/a.md", "disposition": "unsupported", "rationale": "No."}]}), "conceptualize.slice_coverage.entries[0].disposition: expected one of"),
            (lambda plan: plan["conceptualize"].__setitem__("slice_coverage", {"state": "covered", "entries": [{"path": ".planning/missing/slices/a.md", "disposition": "background_only"}]}), "conceptualize.slice_coverage.entries[0].rationale: expected non-empty string"),
            (lambda plan: plan["conceptualize"].__setitem__("slice_coverage", {"state": "covered", "entries": [{"path": ".planning/missing/slices/a.md", "disposition": "promoted"}]}), "conceptualize.slice_coverage.entries[0].promoted_refs: expected array"),
        ]
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                plan = self.valid_plan()
                mutate(plan)
                self.assertInvalid(plan, expected)

    def test_promoted_reference_shape_and_targets_are_validated(self) -> None:
        cases = [
            (lambda entry: entry.__setitem__("promoted_refs", []), "conceptualize.slice_coverage.entries[0].promoted_refs: expected at least one item"),
            (lambda entry: entry.__setitem__("promoted_refs", ["REQ-1"]), "conceptualize.slice_coverage.entries[0].promoted_refs[0]: expected object"),
            (lambda entry: entry.__setitem__("promoted_refs", [{"type": "unknown", "id": "REQ-1"}]), "conceptualize.slice_coverage.entries[0].promoted_refs[0].type: expected one of"),
            (lambda entry: entry.__setitem__("promoted_refs", [{"type": "spec_req", "id": "REQ-404"}]), "conceptualize.slice_coverage.entries[0].promoted_refs[0]: unknown SPEC requirement 'REQ-404'"),
            (lambda entry: entry.__setitem__("promoted_refs", [{"type": "spec_ac", "id": "AC-404"}]), "conceptualize.slice_coverage.entries[0].promoted_refs[0]: unknown SPEC acceptance criterion 'AC-404'"),
            (lambda entry: entry.__setitem__("promoted_refs", [{"type": "task_ac", "id": "P1-T001-AC404"}]), "conceptualize.slice_coverage.entries[0].promoted_refs[0]: unknown task acceptance criterion 'P1-T001-AC404'"),
            (lambda entry: entry.__setitem__("promoted_refs", [{"type": "design_decision", "id": "DD-1"}]), "conceptualize.slice_coverage.entries[0].promoted_refs[0]: unknown design decision 'DD-1'"),
            (lambda entry: entry.__setitem__("promoted_refs", [{"type": "context_bundle", "id": "CTX-1"}]), "conceptualize.slice_coverage.entries[0].promoted_refs[0]: unknown context bundle 'CTX-1'"),
        ]
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                plan = self.covered_plan()
                mutate(plan["conceptualize"]["slice_coverage"]["entries"][0])
                self.assertInvalid(plan, expected)

    def test_scope_reducing_dispositions_require_valid_approval_metadata(self) -> None:
        cases = [
            (lambda entry: entry.pop("approval"), "conceptualize.slice_coverage.entries[3].approval: expected object"),
            (lambda entry: entry.__setitem__("approval", []), "conceptualize.slice_coverage.entries[3].approval: expected object"),
            (lambda entry: entry["approval"].pop("source"), "conceptualize.slice_coverage.entries[3].approval.source: expected non-empty string"),
            (lambda entry: entry["approval"].__setitem__("approved_at", "not-a-date"), "conceptualize.slice_coverage.entries[3].approval.approved_at: expected ISO 8601 datetime string"),
            (lambda entry: entry["approval"].__setitem__("refs", [{"type": "task_ac", "id": "P1-T001-AC404"}]), "conceptualize.slice_coverage.entries[3].approval.refs[0]: unknown task acceptance criterion 'P1-T001-AC404'"),
        ]
        for mutate, expected in cases:
            with self.subTest(expected=expected):
                plan = self.covered_plan()
                mutate(plan["conceptualize"]["slice_coverage"]["entries"][3])
                self.assertInvalid(plan, expected)

    def test_schema_v2_plans_without_conceptualize_metadata_remain_valid(self) -> None:
        plan = self.valid_plan()
        plan["schema_version"] = 2
        plan.pop("conceptualize")
        plan["work_packages"][0].pop("conceptualize_slices")

        self.assertEqual([], self.errors_for(plan))

    def test_schema_v2_conceptualize_coverage_is_compatible_but_validated_when_present(self) -> None:
        legacy_without_coverage = self.valid_plan()
        legacy_without_coverage["schema_version"] = 2
        legacy_without_coverage["conceptualize"].pop("slice_coverage")
        self.assertEqual([], self.errors_for(legacy_without_coverage))

        malformed_top_level = self.valid_plan()
        malformed_top_level["schema_version"] = 2
        malformed_top_level["conceptualize"] = {}
        self.assertInvalid(
            malformed_top_level,
            "conceptualize.index: expected non-empty string",
        )

        malformed_coverage = self.valid_plan()
        malformed_coverage["schema_version"] = 2
        malformed_coverage["conceptualize"]["slice_coverage"] = []
        self.assertInvalid(
            malformed_coverage,
            "conceptualize.slice_coverage: expected object",
        )

        malformed_package = self.valid_plan()
        malformed_package["schema_version"] = 2
        malformed_package["work_packages"][0]["conceptualize_slices"] = ["slice.md"]
        self.assertInvalid(
            malformed_package,
            "work_packages[0].conceptualize_slices[0]: expected object",
        )


if __name__ == "__main__":
    unittest.main()
