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
            "schema_version": 2,
            "feature": "conceptualize-fixture",
            "title": "Conceptualize Fixture",
            "description": "Exercise Conceptualize metadata shape.",
            "created_at": "2026-05-29T00:00:00Z",
            "status": "planned",
            "conceptualize": {"index": ".planning/missing/index.md"},
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
                    "conceptualize_slices": [
                        {
                            "path": ".planning/missing/slices/context.md",
                            "focus": "Schema-only background.",
                        }
                    ],
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

    def errors_for(self, plan: dict) -> list[str]:
        errors, _ = validator.validate_tasks_json(
            plan, tasks_path=self.tasks_path, spec_path=self.spec_path
        )
        return errors

    def assertInvalid(self, plan: dict, expected: str) -> None:
        self.assertTrue(
            any(expected in error for error in self.errors_for(plan)),
            msg=f"missing {expected!r} in errors",
        )

    def test_valid_conceptualize_shape_does_not_require_existing_markdown_paths(self) -> None:
        plan = self.valid_plan()
        plan["conceptualize"]["index"] = ".planning/nonexistent/index.md"
        plan["work_packages"][0]["conceptualize_slices"][0]["path"] = (
            ".planning/nonexistent/slices/also-missing.md"
        )

        self.assertEqual([], self.errors_for(plan))

    def test_top_level_conceptualize_is_required_with_index(self) -> None:
        missing = self.valid_plan()
        missing.pop("conceptualize")
        self.assertInvalid(missing, "conceptualize: expected object")

        malformed = self.valid_plan()
        malformed["conceptualize"] = []
        self.assertInvalid(malformed, "conceptualize: expected object")

        missing_index = self.valid_plan()
        missing_index["conceptualize"] = {}
        self.assertInvalid(missing_index, "conceptualize.index: expected non-empty string")

    def test_work_package_conceptualize_slices_are_required_object_arrays(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
