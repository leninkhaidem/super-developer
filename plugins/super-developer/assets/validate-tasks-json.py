#!/usr/bin/env python3
"""Validate super-developer tasks.json and verification.json files."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

FEATURE_STATUSES = {"planned", "reviewed", "in-progress", "completed", "on-hold"}
TASK_STATUSES = {"pending", "in-progress", "done", "blocked", "skipped"}
DESIGN_DECISION_SOURCES = {"design-preflight", "planner"}
PHASE_ID_RE = re.compile(r"P[1-9]\d*")
TASK_ID_RE = re.compile(r"(P[1-9]\d*)-T\d{3}")
TASK_AC_ID_RE = re.compile(r"(P[1-9]\d*-T\d{3})-AC[1-9]\d*")
WORK_PACKAGE_ID_RE = re.compile(r"WP[1-9]\d*")
DESIGN_DECISION_ID_RE = re.compile(r"DD-[1-9]\d*")
CONTEXT_BUNDLE_ID_RE = re.compile(r"CTX-[1-9]\d*")
SPEC_REQ_RE = re.compile(r"^\s*-\s*(REQ-[1-9]\d*)\s*:")
SPEC_AC_RE = re.compile(r"^\s*-\s*(AC-[1-9]\d*)\s*:")

SOURCE_REF_TYPES = {"spec_req", "spec_ac", "design_decision", "context_bundle"}
BUNDLE_SOURCE_TYPES = {"docs", "code", "spec", "external", "repo"}
LEDGER_STATUSES = {"verified", "failed", "blocked", "manual_required"}
LEDGER_METHODS = {
    "unit_test",
    "integration_test",
    "e2e_test",
    "table_driven_test",
    "static_inspection",
    "manual",
    "command",
    "mixed",
}
COMMAND_EVIDENCE_METHODS = {
    "unit_test",
    "integration_test",
    "e2e_test",
    "table_driven_test",
    "command",
    "mixed",
}

RISK_TAGS = {
    "security",
    "privacy",
    "safety",
    "persistence",
    "data-integrity",
    "migration",
    "runtime-contract",
    "library-contract",
    "public-api",
    "exported-types",
    "concurrency",
    "idempotency",
    "replay",
    "performance",
    "resource-bounds",
    "cross-package-integration",
    "schema",
    "traceability",
    "validation",
    "orchestration",
    "git-state",
    "integration",
    "subagent-contract",
    "review",
    "audit",
    "fix-loop",
    "quality-contract",
    "documentation",
    "consistency",
    "validation-samples",
    "docs",
}

TARGETED_REVIEW_RISK_TAGS = {
    "security",
    "privacy",
    "safety",
    "persistence",
    "data-integrity",
    "migration",
    "runtime-contract",
    "library-contract",
    "public-api",
    "exported-types",
    "concurrency",
    "idempotency",
    "replay",
    "performance",
    "resource-bounds",
    "cross-package-integration",
    "schema",
    "traceability",
    "validation",
    "orchestration",
    "git-state",
    "integration",
    "subagent-contract",
    "review",
    "audit",
    "fix-loop",
    "quality-contract",
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate super-developer task plans and optional verification ledgers."
    )
    parser.add_argument("path", help="Path to .tasks/<feature>/tasks.json")
    parser.add_argument(
        "--final",
        action="store_true",
        help="Also validate verification.json as a final/audit gate.",
    )
    parser.add_argument(
        "--verification",
        help="Path to verification.json (defaults to sibling verification.json).",
    )
    parser.add_argument(
        "--worktree",
        help="Worktree used for stale-evidence checks (defaults to current directory).",
    )
    args = parser.parse_args()

    tasks_path = Path(args.path)
    try:
        with tasks_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: file not found: {tasks_path}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON: {exc}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as exc:
        print(f"ERROR: unable to read tasks.json: {exc}", file=sys.stderr)
        return 2

    spec_path = tasks_path.with_name("SPEC.md")
    errors, plan_index = validate_tasks_json(data, tasks_path=tasks_path, spec_path=spec_path)

    if args.final:
        verification_path = Path(args.verification) if args.verification else tasks_path.with_name("verification.json")
        errors.extend(
            validate_verification_json_file(
                verification_path,
                plan_index,
                worktree=Path(args.worktree) if args.worktree else Path.cwd(),
            )
        )

    if errors:
        print(f"ERROR: tasks.json validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    if args.final:
        print("OK: tasks.json and verification.json are valid")
    else:
        print("OK: tasks.json is valid")
    return 0


def validate_tasks_json(
    data: Any, *, tasks_path: Path | None = None, spec_path: Path | None = None
) -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    plan_index: dict[str, Any] = {
        "feature": None,
        "schema_version": 2,
        "task_ids": set(),
        "task_ac_ids": set(),
        "task_ac_sources": {},
        "task_to_package": {},
        "context_bundle_ids": set(),
    }
    if not isinstance(data, dict):
        return ["root: expected JSON object"], plan_index

    schema_version = validate_schema_version(data, errors)
    plan_index["schema_version"] = schema_version
    plan_index["feature"] = data.get("feature")

    validate_top_level(data, errors)
    if "context_bundles" not in data:
        errors.append("context_bundles: expected array")
    context_bundle_ids = validate_context_bundles(
        data.get("context_bundles", []), errors, required=True
    )
    plan_index["context_bundle_ids"] = context_bundle_ids

    phases = data.get("phases")
    work_packages = data.get("work_packages")

    task_ids: set[str] = set()
    task_dependencies: dict[str, list[str]] = {}
    task_phase_order: dict[str, int] = {}
    task_ac_ids: set[str] = set()
    task_ac_sources: dict[str, list[dict[str, str]]] = {}

    design_decision_ids = collect_design_decision_ids(data.get("design_decisions"))

    if isinstance(phases, list):
        validate_phases(
            phases,
            errors,
            task_ids,
            task_dependencies,
            task_phase_order,
            task_ac_ids=task_ac_ids,
            task_ac_sources=task_ac_sources,
            design_decision_ids=design_decision_ids,
            context_bundle_ids=context_bundle_ids,
        )
    else:
        errors.append("phases: expected array")

    if isinstance(work_packages, list):
        task_to_package = validate_work_packages(
            work_packages,
            errors,
            task_ids,
            task_dependencies,
            context_bundle_ids=context_bundle_ids,
        )
        plan_index["task_to_package"] = task_to_package
    else:
        errors.append("work_packages: expected array")

    validate_task_dependencies(task_dependencies, task_ids, task_phase_order, errors)

    spec_ids = parse_spec_ids(spec_path, errors) if spec_path else {"spec_req": set(), "spec_ac": set()}
    validate_source_ref_targets(
        task_ac_sources,
        errors,
        spec_ids=spec_ids,
        design_decision_ids=design_decision_ids,
        context_bundle_ids=context_bundle_ids,
    )
    validate_spec_coverage(task_ac_sources, spec_ids, errors)
    if isinstance(work_packages, list):
        validate_context_bundle_consumers(
            data.get("context_bundles", []),
            work_packages,
            phases if isinstance(phases, list) else [],
            task_ids,
            errors,
            task_ac_sources,
        )

    plan_index["task_ids"] = task_ids
    plan_index["task_ac_ids"] = task_ac_ids
    plan_index["task_ac_sources"] = task_ac_sources
    return errors, plan_index


def validate_schema_version(data: dict[str, Any], errors: list[str]) -> int:
    value = data.get("schema_version")
    if isinstance(value, bool) or not isinstance(value, int):
        errors.append("schema_version: expected integer 2")
        return 2
    if value != 2:
        errors.append(f"schema_version: expected 2, got {value!r}")
        return 2
    return value


def validate_top_level(data: dict[str, Any], errors: list[str]) -> None:
    for field in ("feature", "title", "description", "created_at", "status"):
        require_non_empty_string(data, field, field, errors)

    status = data.get("status")
    if isinstance(status, str) and status not in FEATURE_STATUSES:
        errors.append(
            f"status: expected one of {sorted(FEATURE_STATUSES)}, got {status!r}"
        )

    created_at = data.get("created_at")
    if isinstance(created_at, str) and created_at.strip():
        validate_iso_datetime(created_at, "created_at", errors)

    if "design_decisions" not in data:
        errors.append("design_decisions: expected array")
        return

    design_decisions = data["design_decisions"]
    if not isinstance(design_decisions, list):
        errors.append("design_decisions: expected array")
        return
    validate_design_decisions(design_decisions, errors)


def collect_design_decision_ids(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    ids: set[str] = set()
    for decision in value:
        if isinstance(decision, dict) and isinstance(decision.get("id"), str):
            ids.add(decision["id"])
    return ids


def validate_design_decisions(
    design_decisions: list[Any], errors: list[str]
) -> None:
    decision_ids: list[str] = []
    for index, decision in enumerate(design_decisions):
        path = f"design_decisions[{index}]"
        if not isinstance(decision, dict):
            errors.append(f"{path}: expected object")
            continue

        for field in ("id", "decision", "rationale", "source"):
            require_non_empty_string(decision, field, f"{path}.{field}", errors)

        decision_id = decision.get("id")
        if isinstance(decision_id, str) and decision_id.strip():
            if not DESIGN_DECISION_ID_RE.fullmatch(decision_id):
                errors.append(f"{path}.id: expected DD-<N>, got {decision_id!r}")
            decision_ids.append(decision_id)

        source = decision.get("source")
        if isinstance(source, str) and source not in DESIGN_DECISION_SOURCES:
            errors.append(
                f"{path}.source: expected one of {sorted(DESIGN_DECISION_SOURCES)}, got {source!r}"
            )

        alternatives = decision.get("alternatives_considered")
        if not isinstance(alternatives, list):
            errors.append(f"{path}.alternatives_considered: expected array")
        elif not all(isinstance(item, str) for item in alternatives):
            errors.append(f"{path}.alternatives_considered: expected string array")

    add_duplicate_errors(decision_ids, "design decision id", "design_decisions", errors)
    validate_sequential_ids(decision_ids, "DD-", "design_decisions", errors)


def validate_context_bundles(value: Any, errors: list[str], *, required: bool) -> set[str]:
    if value is None and not required:
        return set()
    if not isinstance(value, list):
        if required:
            errors.append("context_bundles: expected array")
        return set()

    bundle_ids: list[str] = []
    for index, bundle in enumerate(value):
        path = f"context_bundles[{index}]"
        if not isinstance(bundle, dict):
            errors.append(f"{path}: expected object")
            continue
        for field in ("id", "title"):
            require_non_empty_string(bundle, field, f"{path}.{field}", errors)
        bundle_id = bundle.get("id")
        if isinstance(bundle_id, str) and bundle_id.strip():
            if not CONTEXT_BUNDLE_ID_RE.fullmatch(bundle_id):
                errors.append(f"{path}.id: expected CTX-<N>, got {bundle_id!r}")
            bundle_ids.append(bundle_id)

        required_for = require_string_list(
            bundle, "required_for", f"{path}.required_for", errors
        )
        for ref in required_for:
            if not (WORK_PACKAGE_ID_RE.fullmatch(ref) or TASK_ID_RE.fullmatch(ref)):
                errors.append(
                    f"{path}.required_for: expected WP<N> or task id, got {ref!r}"
                )

        sources = bundle.get("sources")
        if not isinstance(sources, list) or not sources:
            errors.append(f"{path}.sources: expected non-empty array")
        else:
            for source_index, source in enumerate(sources):
                source_path = f"{path}.sources[{source_index}]"
                if not isinstance(source, dict):
                    errors.append(f"{source_path}: expected object")
                    continue
                source_type = source.get("type")
                if not isinstance(source_type, str) or source_type not in BUNDLE_SOURCE_TYPES:
                    errors.append(
                        f"{source_path}.type: expected one of {sorted(BUNDLE_SOURCE_TYPES)}, got {source_type!r}"
                    )
                require_non_empty_string(
                    source, "path_or_url", f"{source_path}.path_or_url", errors
                )
                claims = require_string_list(
                    source, "claims", f"{source_path}.claims", errors
                )
                if not claims:
                    errors.append(f"{source_path}.claims: expected at least one item")

        verification_required = require_string_list(
            bundle,
            "verification_required",
            f"{path}.verification_required",
            errors,
        )
        if not verification_required:
            errors.append(f"{path}.verification_required: expected at least one item")

    add_duplicate_errors(bundle_ids, "context bundle id", "context_bundles", errors)
    validate_sequential_ids(bundle_ids, "CTX-", "context_bundles", errors)
    return set(bundle_ids)

def validate_context_bundle_consumers(
    bundles: Any,
    work_packages: list[Any],
    phases: list[Any],
    task_ids: set[str],
    errors: list[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
) -> None:
    if not isinstance(bundles, list):
        return

    def string_set(value: Any) -> set[str]:
        if not isinstance(value, list):
            return set()
        return {item for item in value if isinstance(item, str)}

    package_ids = {
        package.get("id")
        for package in work_packages
        if isinstance(package, dict) and isinstance(package.get("id"), str)
    }
    package_tasks = {
        package["id"]: string_set(package.get("task_ids"))
        for package in work_packages
        if isinstance(package, dict) and isinstance(package.get("id"), str)
    }
    task_to_package = {
        task_id: package_id
        for package_id, package_task_ids in package_tasks.items()
        for task_id in package_task_ids
    }
    package_bundle_refs = {
        package["id"]: string_set(package.get("required_context_bundles"))
        for package in work_packages
        if isinstance(package, dict) and isinstance(package.get("id"), str)
    }
    task_bundle_refs: dict[str, set[str]] = {}
    for phase in phases:
        if not isinstance(phase, dict) or not isinstance(phase.get("tasks"), list):
            continue
        for task in phase["tasks"]:
            if isinstance(task, dict) and isinstance(task.get("id"), str):
                task_bundle_refs[task["id"]] = string_set(task.get("required_context_bundles"))
    bundle_required_for: dict[str, set[str]] = {}
    for index, bundle in enumerate(bundles):
        if not isinstance(bundle, dict) or not isinstance(bundle.get("id"), str):
            continue
        refs = string_set(bundle.get("required_for"))
        bundle_required_for[bundle["id"]] = refs
        for ref in refs:
            if ref not in package_ids and ref not in task_ids:
                errors.append(
                    f"context_bundles[{index}].required_for: unknown package/task reference {ref!r}"
                )
            elif ref in package_ids and bundle["id"] not in package_bundle_refs.get(ref, set()):
                errors.append(
                    f"context_bundles[{index}].required_for: package {ref!r} must include {bundle['id']!r} in required_context_bundles"
                )
            elif ref in task_ids:
                containing_package = task_to_package.get(ref)
                if (
                    bundle["id"] not in task_bundle_refs.get(ref, set())
                    and bundle["id"] not in package_bundle_refs.get(containing_package, set())
                ):
                    errors.append(
                        f"context_bundles[{index}].required_for: task {ref!r} or containing package must include {bundle['id']!r} in required_context_bundles"
                    )

    for ac_id, refs in task_ac_sources.items():
        task_id = ac_id.rsplit("-AC", 1)[0]
        containing_package = task_to_package.get(task_id)
        for ref in refs:
            if ref.get("type") != "context_bundle":
                continue
            bundle_id = ref.get("id")
            if not isinstance(bundle_id, str):
                continue
            if (
                bundle_id not in task_bundle_refs.get(task_id, set())
                and bundle_id not in package_bundle_refs.get(containing_package, set())
            ):
                errors.append(
                    f"acceptance criterion {ac_id}: context_bundle source_ref {bundle_id!r} must be listed in the task or containing package required_context_bundles"
                )
            required_for = bundle_required_for.get(bundle_id, set())
            if task_id not in required_for and containing_package not in required_for:
                errors.append(
                    f"acceptance criterion {ac_id}: context_bundle source_ref {bundle_id!r} must list {task_id!r} or containing package in context_bundles[].required_for"
                )

    for package in work_packages:
        if not isinstance(package, dict) or not isinstance(package.get("id"), str):
            continue
        package_id = package["id"]
        package_task_ids = package_tasks.get(package_id, set())
        bundle_refs = string_set(package.get("required_context_bundles"))
        for bundle_ref in bundle_refs:
            refs = bundle_required_for.get(bundle_ref, set())
            if package_id not in refs and not (package_task_ids & refs):
                errors.append(
                    f"work package {package_id}: required_context_bundles {bundle_ref!r} must list {package_id!r} or one contained task in context_bundles[].required_for"
                )

    for phase in phases:
        if not isinstance(phase, dict) or not isinstance(phase.get("tasks"), list):
            continue
        for task in phase["tasks"]:
            if not isinstance(task, dict) or not isinstance(task.get("id"), str):
                continue
            task_id = task["id"]
            bundle_refs = string_set(task.get("required_context_bundles"))
            for bundle_ref in bundle_refs:
                refs = bundle_required_for.get(bundle_ref, set())
                if task_id not in refs and task_to_package.get(task_id) not in refs:
                    errors.append(
                        f"task {task_id}: required_context_bundles {bundle_ref!r} must list {task_id!r} or containing package in context_bundles[].required_for"
                    )


def validate_phases(
    phases: list[Any],
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
    task_phase_order: dict[str, int],
    task_ac_ids: set[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    phase_ids: list[str] = []
    phase_orders: list[int] = []

    for phase_index, phase in enumerate(phases):
        phase_path = f"phases[{phase_index}]"
        if not isinstance(phase, dict):
            errors.append(f"{phase_path}: expected object")
            continue

        for field in ("id", "name", "description"):
            require_non_empty_string(phase, field, f"{phase_path}.{field}", errors)

        phase_id = phase.get("id")
        if isinstance(phase_id, str) and phase_id.strip():
            if not PHASE_ID_RE.fullmatch(phase_id):
                errors.append(f"{phase_path}.id: expected P<N>, got {phase_id!r}")
            phase_ids.append(phase_id)

        order = phase.get("order")
        if isinstance(order, bool) or not isinstance(order, int):
            errors.append(f"{phase_path}.order: expected integer")
        else:
            phase_orders.append(order)

        tasks = phase.get("tasks")
        if not isinstance(tasks, list):
            errors.append(f"{phase_path}.tasks: expected array")
            continue

        for task_index, task in enumerate(tasks):
            validate_task(
                task,
                f"{phase_path}.tasks[{task_index}]",
                phase_id if isinstance(phase_id, str) else None,
                order if isinstance(order, int) else phase_index + 1,
                errors,
                task_ids,
                task_dependencies,
                task_phase_order,
                task_ac_ids=task_ac_ids,
                task_ac_sources=task_ac_sources,
                design_decision_ids=design_decision_ids,
                context_bundle_ids=context_bundle_ids,
            )

    add_duplicate_errors(phase_ids, "phase id", "phases", errors)
    validate_sequential_ids(phase_ids, "P", "phases", errors)
    validate_sequential_orders(phase_orders, "phases[].order", errors)


def validate_task(
    task: Any,
    task_path: str,
    phase_id: str | None,
    phase_order: int,
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
    task_phase_order: dict[str, int],
    task_ac_ids: set[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    if not isinstance(task, dict):
        errors.append(f"{task_path}: expected object")
        return

    for field in ("id", "title", "description", "status", "context"):
        require_non_empty_string(task, field, f"{task_path}.{field}", errors)

    task_id = task.get("id")
    if isinstance(task_id, str) and task_id.strip():
        match = TASK_ID_RE.fullmatch(task_id)
        if not match:
            errors.append(f"{task_path}.id: expected <PhaseID>-T<NNN>, got {task_id!r}")
        elif phase_id is not None and match.group(1) != phase_id:
            errors.append(
                f"{task_path}.id: task id phase {match.group(1)!r} does not match {phase_id!r}"
            )

        if task_id in task_ids:
            errors.append(f"{task_path}.id: duplicate task id {task_id!r}")
        task_ids.add(task_id)
        task_phase_order[task_id] = phase_order

    status = task.get("status")
    if isinstance(status, str) and status not in TASK_STATUSES:
        errors.append(
            f"{task_path}.status: expected one of {sorted(TASK_STATUSES)}, got {status!r}"
        )
    if status == "done":
        if require_non_empty_string(
            task, "completed_at", f"{task_path}.completed_at", errors
        ):
            validate_iso_datetime(task["completed_at"], f"{task_path}.completed_at", errors)
    if status == "blocked":
        require_non_empty_string(
            task, "blocked_reason", f"{task_path}.blocked_reason", errors
        )

    dependencies = require_string_list(
        task, "dependencies", f"{task_path}.dependencies", errors
    )
    if isinstance(task_id, str) and task_id.strip():
        task_dependencies[task_id] = dependencies

    validate_structured_acceptance_criteria(
        task,
        task_path,
        task_id if isinstance(task_id, str) else None,
        errors,
        task_ac_ids,
        task_ac_sources,
    )
    bundle_refs = require_string_list(
        task,
        "required_context_bundles",
        f"{task_path}.required_context_bundles",
        errors,
        required=False,
    )
    for bundle_ref in bundle_refs:
        if bundle_ref not in context_bundle_ids:
            errors.append(
                f"{task_path}.required_context_bundles: unknown context bundle {bundle_ref!r}"
            )

def validate_structured_acceptance_criteria(
    task: dict[str, Any],
    task_path: str,
    task_id: str | None,
    errors: list[str],
    task_ac_ids: set[str],
    task_ac_sources: dict[str, list[dict[str, str]]],
) -> None:
    criteria = task.get("acceptance_criteria")
    if not isinstance(criteria, list):
        errors.append(f"{task_path}.acceptance_criteria: expected array")
        return
    if not criteria:
        errors.append(f"{task_path}.acceptance_criteria: expected at least one item")

    for index, criterion in enumerate(criteria):
        path = f"{task_path}.acceptance_criteria[{index}]"
        if not isinstance(criterion, dict):
            errors.append(f"{path}: expected object for schema_version 2")
            continue
        for field in ("id", "criterion", "source_refs"):
            if field == "source_refs":
                continue
            require_non_empty_string(criterion, field, f"{path}.{field}", errors)

        ac_id = criterion.get("id")
        if isinstance(ac_id, str) and ac_id.strip():
            match = TASK_AC_ID_RE.fullmatch(ac_id)
            if not match:
                errors.append(f"{path}.id: expected <TaskID>-AC<N>, got {ac_id!r}")
            elif task_id is not None and match.group(1) != task_id:
                errors.append(
                    f"{path}.id: criterion id task {match.group(1)!r} does not match {task_id!r}"
                )
            if ac_id in task_ac_ids:
                errors.append(f"{path}.id: duplicate acceptance criterion id {ac_id!r}")
            task_ac_ids.add(ac_id)

        refs = criterion.get("source_refs")
        if not isinstance(refs, list) or not refs:
            errors.append(f"{path}.source_refs: expected non-empty array")
            parsed_refs: list[dict[str, str]] = []
        else:
            parsed_refs = []
            for ref_index, ref in enumerate(refs):
                parsed = validate_source_ref(ref, f"{path}.source_refs[{ref_index}]", errors)
                if parsed is not None:
                    parsed_refs.append(parsed)
        if isinstance(ac_id, str) and ac_id.strip():
            task_ac_sources[ac_id] = parsed_refs

        hint = criterion.get("verification_hint")
        if hint is not None and (not isinstance(hint, str) or not hint.strip()):
            errors.append(f"{path}.verification_hint: expected non-empty string when present")


def validate_source_ref(ref: Any, path: str, errors: list[str]) -> dict[str, str] | None:
    if not isinstance(ref, dict):
        errors.append(f"{path}: expected object")
        return None
    ref_type = ref.get("type")
    ref_id = ref.get("id")
    if not isinstance(ref_type, str) or ref_type not in SOURCE_REF_TYPES:
        errors.append(
            f"{path}.type: expected one of {sorted(SOURCE_REF_TYPES)}, got {ref_type!r}"
        )
        return None
    if not isinstance(ref_id, str) or not ref_id.strip():
        errors.append(f"{path}.id: expected non-empty string")
        return None
    return {"type": ref_type, "id": ref_id}


def parse_spec_ids(spec_path: Path | None, errors: list[str]) -> dict[str, set[str]]:
    ids = {"spec_req": set(), "spec_ac": set()}
    if spec_path is None:
        errors.append("SPEC.md: path unavailable for traceability validation")
        return ids
    if not spec_path.exists():
        errors.append(f"SPEC.md: expected sibling file at {spec_path}")
        return ids

    req_ids: list[str] = []
    ac_ids: list[str] = []
    try:
        spec_lines = spec_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        errors.append(f"SPEC.md: unable to read {spec_path}: {exc}")
        return ids
    for line in spec_lines:
        req_match = SPEC_REQ_RE.match(line)
        if req_match:
            req_ids.append(req_match.group(1))
        ac_match = SPEC_AC_RE.match(line)
        if ac_match:
            ac_ids.append(ac_match.group(1))

    add_duplicate_errors(req_ids, "SPEC requirement id", "SPEC.md Requirements", errors)
    add_duplicate_errors(ac_ids, "SPEC acceptance criterion id", "SPEC.md Acceptance Criteria", errors)
    ids["spec_req"] = set(req_ids)
    ids["spec_ac"] = set(ac_ids)
    if not req_ids:
        errors.append("SPEC.md Requirements: expected at least one REQ-<N> id")
    if not ac_ids:
        errors.append("SPEC.md Acceptance Criteria: expected at least one AC-<N> id")
    return ids


def validate_source_ref_targets(
    task_ac_sources: dict[str, list[dict[str, str]]],
    errors: list[str],
    *,
    spec_ids: dict[str, set[str]],
    design_decision_ids: set[str],
    context_bundle_ids: set[str],
) -> None:
    for ac_id, refs in task_ac_sources.items():
        for ref in refs:
            ref_type = ref["type"]
            ref_id = ref["id"]
            if ref_type == "spec_req" and ref_id not in spec_ids["spec_req"]:
                errors.append(f"acceptance criterion {ac_id}: unknown SPEC requirement {ref_id!r}")
            elif ref_type == "spec_ac" and ref_id not in spec_ids["spec_ac"]:
                errors.append(f"acceptance criterion {ac_id}: unknown SPEC acceptance criterion {ref_id!r}")
            elif ref_type == "design_decision" and ref_id not in design_decision_ids:
                errors.append(f"acceptance criterion {ac_id}: unknown design decision {ref_id!r}")
            elif ref_type == "context_bundle" and ref_id not in context_bundle_ids:
                errors.append(f"acceptance criterion {ac_id}: unknown context bundle {ref_id!r}")


def validate_spec_coverage(
    task_ac_sources: dict[str, list[dict[str, str]]],
    spec_ids: dict[str, set[str]],
    errors: list[str],
) -> None:
    covered_req = {
        ref["id"]
        for refs in task_ac_sources.values()
        for ref in refs
        if ref["type"] == "spec_req"
    }
    covered_ac = {
        ref["id"]
        for refs in task_ac_sources.values()
        for ref in refs
        if ref["type"] == "spec_ac"
    }
    for req_id in sorted(spec_ids["spec_req"] - covered_req):
        errors.append(f"SPEC requirement {req_id}: not covered by any task acceptance criterion")
    for ac_id in sorted(spec_ids["spec_ac"] - covered_ac):
        errors.append(f"SPEC acceptance criterion {ac_id}: not covered by any task acceptance criterion")


def validate_task_dependencies(
    task_dependencies: dict[str, list[str]],
    task_ids: set[str],
    task_phase_order: dict[str, int],
    errors: list[str],
) -> None:
    for task_id, dependencies in task_dependencies.items():
        for duplicate in duplicates(dependencies):
            errors.append(f"task {task_id}: duplicate dependency {duplicate!r}")
        for dependency in dependencies:
            if dependency == task_id:
                errors.append(f"task {task_id}: must not depend on itself")
            elif dependency not in task_ids:
                errors.append(f"task {task_id}: unknown dependency {dependency!r}")
            elif task_phase_order.get(dependency, 0) > task_phase_order.get(task_id, 0):
                errors.append(
                    f"task {task_id}: depends on future-phase task {dependency!r}"
                )

    cycle = find_cycle(task_dependencies)
    if cycle:
        errors.append(f"task dependencies contain cycle: {' -> '.join(cycle)}")


def validate_work_packages(
    work_packages: list[Any],
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
    context_bundle_ids: set[str],
) -> dict[str, str]:
    package_ids: list[str] = []
    package_task_refs: dict[str, list[str]] = {}
    package_dependencies: dict[str, list[str]] = {}
    package_parallel: dict[str, list[str]] = {}

    for package_index, package in enumerate(work_packages):
        package_path = f"work_packages[{package_index}]"
        if not isinstance(package, dict):
            errors.append(f"{package_path}: expected object")
            continue

        for field in ("id", "title", "description", "rationale"):
            require_non_empty_string(package, field, f"{package_path}.{field}", errors)

        package_id = package.get("id")
        if isinstance(package_id, str) and package_id.strip():
            if not WORK_PACKAGE_ID_RE.fullmatch(package_id):
                errors.append(
                    f"{package_path}.id: expected WP<N>, got {package_id!r}"
                )
            package_ids.append(package_id)

        task_refs = require_string_list(
            package, "task_ids", f"{package_path}.task_ids", errors
        )
        depends_on = require_string_list(
            package, "depends_on", f"{package_path}.depends_on", errors
        )
        parallel_safe_with = require_string_list(
            package,
            "parallel_safe_with",
            f"{package_path}.parallel_safe_with",
            errors,
        )
        require_string_list(
            package, "primary_paths", f"{package_path}.primary_paths", errors
        )
        require_string_list(
            package,
            "verification_commands",
            f"{package_path}.verification_commands",
            errors,
        )

        validate_package_v2_fields(
            package,
            package_path,
            errors,
            context_bundle_ids=context_bundle_ids,
        )

        if isinstance(package_id, str) and package_id.strip():
            package_task_refs[package_id] = task_refs
            package_dependencies[package_id] = depends_on
            package_parallel[package_id] = parallel_safe_with

        if not task_refs:
            errors.append(f"{package_path}.task_ids: expected at least one task id")
        if len(task_refs) == 1:
            require_non_empty_string(
                package, "rationale", f"{package_path}.rationale", errors
            )
        for duplicate in duplicates(task_refs):
            errors.append(f"{package_path}.task_ids: duplicate task id {duplicate!r}")
        for duplicate in duplicates(depends_on):
            errors.append(f"{package_path}.depends_on: duplicate package id {duplicate!r}")
        for duplicate in duplicates(parallel_safe_with):
            errors.append(
                f"{package_path}.parallel_safe_with: duplicate package id {duplicate!r}"
            )

    add_duplicate_errors(package_ids, "work package id", "work_packages", errors)
    validate_sequential_ids(package_ids, "WP", "work_packages", errors)
    task_to_package = validate_package_task_coverage(package_task_refs, task_ids, errors)
    validate_package_dependency_fields(package_dependencies, package_parallel, errors)
    validate_package_dependency_graph(package_dependencies, errors)
    validate_parallel_symmetry(package_parallel, errors)
    validate_cross_package_task_dependencies(
        package_task_refs, package_dependencies, task_dependencies, errors
    )
    return task_to_package


def validate_package_v2_fields(
    package: dict[str, Any],
    package_path: str,
    errors: list[str],
    *,
    context_bundle_ids: set[str],
) -> None:
    risk_tags = require_string_list(package, "risk_tags", f"{package_path}.risk_tags", errors)
    for tag in risk_tags:
        if tag not in RISK_TAGS:
            errors.append(
                f"{package_path}.risk_tags: unknown risk tag {tag!r}; expected one of {sorted(RISK_TAGS)}"
            )

    bundle_refs = require_string_list(
        package,
        "required_context_bundles",
        f"{package_path}.required_context_bundles",
        errors,
    )
    for bundle_ref in bundle_refs:
        if bundle_ref not in context_bundle_ids:
            errors.append(
                f"{package_path}.required_context_bundles: unknown context bundle {bundle_ref!r}"
            )

    targeted = package.get("targeted_review_required")
    if not isinstance(targeted, bool):
        errors.append(f"{package_path}.targeted_review_required: expected boolean")
        return
    triggering_tags = sorted(set(risk_tags) & TARGETED_REVIEW_RISK_TAGS)
    if triggering_tags and not targeted:
        errors.append(
            f"{package_path}.targeted_review_required: must be true because risk_tags include targeted-review trigger(s) {triggering_tags}"
        )


def validate_package_task_coverage(
    package_task_refs: dict[str, list[str]], task_ids: set[str], errors: list[str]
) -> dict[str, str]:
    task_to_packages: dict[str, list[str]] = defaultdict(list)
    for package_id, refs in package_task_refs.items():
        for task_id in refs:
            if task_id not in task_ids:
                errors.append(
                    f"work package {package_id}: unknown task id {task_id!r} in task_ids"
                )
            else:
                task_to_packages[task_id].append(package_id)

    task_to_package: dict[str, str] = {}
    for task_id in sorted(task_ids):
        packages = task_to_packages.get(task_id, [])
        if not packages:
            errors.append(f"task {task_id}: not assigned to any work package")
        elif len(packages) > 1:
            errors.append(
                f"task {task_id}: assigned to multiple work packages {sorted(packages)}"
            )
        else:
            task_to_package[task_id] = packages[0]
    return task_to_package


def validate_package_dependency_fields(
    package_dependencies: dict[str, list[str]],
    package_parallel: dict[str, list[str]],
    errors: list[str],
) -> None:
    package_ids = set(package_dependencies) | set(package_parallel)
    for package_id in sorted(package_ids):
        for dependency in package_dependencies.get(package_id, []):
            if dependency == package_id:
                errors.append(f"work package {package_id}: must not depend on itself")
            elif dependency not in package_ids:
                errors.append(
                    f"work package {package_id}: unknown package dependency {dependency!r}"
                )
            if dependency in package_parallel.get(package_id, []):
                errors.append(
                    f"work package {package_id}: {dependency!r} cannot be both a dependency and parallel-safe"
                )
        for parallel_id in package_parallel.get(package_id, []):
            if parallel_id == package_id:
                errors.append(
                    f"work package {package_id}: must not list itself in parallel_safe_with"
                )
            elif parallel_id not in package_ids:
                errors.append(
                    f"work package {package_id}: unknown parallel_safe_with package {parallel_id!r}"
                )


def validate_package_dependency_graph(
    package_dependencies: dict[str, list[str]], errors: list[str]
) -> None:
    cycle = find_cycle(package_dependencies)
    if cycle:
        errors.append(f"work package dependencies contain cycle: {' -> '.join(cycle)}")


def validate_parallel_symmetry(
    package_parallel: dict[str, list[str]], errors: list[str]
) -> None:
    for package_id, parallel_ids in package_parallel.items():
        for parallel_id in parallel_ids:
            if parallel_id not in package_parallel:
                continue
            if package_id not in package_parallel[parallel_id]:
                errors.append(
                    f"work package {package_id}: parallel_safe_with {parallel_id!r} is not symmetric"
                )


def validate_cross_package_task_dependencies(
    package_task_refs: dict[str, list[str]],
    package_dependencies: dict[str, list[str]],
    task_dependencies: dict[str, list[str]],
    errors: list[str],
) -> None:
    task_to_package: dict[str, str] = {}
    for package_id, task_refs in package_task_refs.items():
        for task_id in task_refs:
            if task_id not in task_to_package:
                task_to_package[task_id] = package_id

    for task_id, dependencies in task_dependencies.items():
        package_id = task_to_package.get(task_id)
        if package_id is None:
            continue
        for dependency in dependencies:
            dependency_package = task_to_package.get(dependency)
            if dependency_package is None or dependency_package == package_id:
                continue
            if dependency_package not in package_dependencies.get(package_id, []):
                errors.append(
                    f"work package {package_id}: missing depends_on {dependency_package!r} "
                    f"because task {task_id} depends on {dependency}"
                )


def validate_verification_json_file(
    verification_path: Path, plan_index: dict[str, Any], *, worktree: Path
) -> list[str]:
    errors: list[str] = []
    try:
        with verification_path.open("r", encoding="utf-8") as f:
            ledger = json.load(f)
    except FileNotFoundError:
        return [f"verification.json: file not found at {verification_path}"]
    except json.JSONDecodeError as exc:
        return [f"verification.json: invalid JSON: {exc}"]
    except (OSError, UnicodeDecodeError) as exc:
        return [f"verification.json: unable to read {verification_path}: {exc}"]

    errors.extend(validate_verification_json(ledger, plan_index, worktree=worktree))
    return errors


def validate_verification_json(
    ledger: Any, plan_index: dict[str, Any], *, worktree: Path
) -> list[str]:
    errors: list[str] = []
    if not isinstance(ledger, dict):
        return ["verification.json root: expected object"]

    schema_version = ledger.get("schema_version")
    if (
        isinstance(schema_version, bool)
        or not isinstance(schema_version, int)
        or schema_version != 1
    ):
        errors.append(f"verification.schema_version: expected integer 1, got {schema_version!r}")

    feature = ledger.get("feature")
    if feature != plan_index.get("feature"):
        errors.append(
            f"verification.feature: expected {plan_index.get('feature')!r}, got {feature!r}"
        )

    entries = ledger.get("entries")
    if not isinstance(entries, list):
        errors.append("verification.entries: expected array")
        return errors

    task_ac_ids: set[str] = set(plan_index.get("task_ac_ids", set()))
    seen_ac_ids: set[str] = set()
    for index, entry in enumerate(entries):
        validate_ledger_entry(entry, f"verification.entries[{index}]", errors, plan_index, worktree)
        if isinstance(entry, dict) and isinstance(entry.get("criterion_id"), str):
            seen_ac_ids.add(entry["criterion_id"])

    for ac_id in sorted(task_ac_ids - seen_ac_ids):
        errors.append(f"verification.entries: missing ledger entry for acceptance criterion {ac_id}")
    for ac_id in sorted(seen_ac_ids - task_ac_ids):
        errors.append(f"verification.entries: unknown acceptance criterion {ac_id!r}")
    for duplicate in duplicates(
        [
            entry["criterion_id"]
            for entry in entries
            if isinstance(entry, dict) and isinstance(entry.get("criterion_id"), str)
        ]
    ):
        errors.append(f"verification.entries: duplicate criterion_id {duplicate!r}")

    return errors


def validate_ledger_entry(
    entry: Any,
    path: str,
    errors: list[str],
    plan_index: dict[str, Any],
    worktree: Path,
) -> None:
    if not isinstance(entry, dict):
        errors.append(f"{path}: expected object")
        return

    criterion_id = entry.get("criterion_id")
    task_id = entry.get("task_id")
    package_id = entry.get("package_id")
    status = entry.get("status")
    method = entry.get("method")

    for field in ("criterion_id", "task_id", "package_id", "status", "method"):
        require_non_empty_string(entry, field, f"{path}.{field}", errors)

    if isinstance(criterion_id, str):
        match = TASK_AC_ID_RE.fullmatch(criterion_id)
        if not match:
            errors.append(f"{path}.criterion_id: expected <TaskID>-AC<N>, got {criterion_id!r}")
        elif isinstance(task_id, str) and match.group(1) != task_id:
            errors.append(
                f"{path}.task_id: expected {match.group(1)!r} from criterion_id, got {task_id!r}"
            )
    if isinstance(task_id, str):
        if task_id not in plan_index.get("task_ids", set()):
            errors.append(f"{path}.task_id: unknown task id {task_id!r}")
        expected_package = plan_index.get("task_to_package", {}).get(task_id)
        if expected_package and isinstance(package_id, str) and package_id != expected_package:
            errors.append(
                f"{path}.package_id: expected {expected_package!r} for task {task_id}, got {package_id!r}"
            )

    if isinstance(status, str) and status not in LEDGER_STATUSES:
        errors.append(f"{path}.status: expected one of {sorted(LEDGER_STATUSES)}, got {status!r}")
    if status in {"failed", "blocked"}:
        errors.append(f"{path}.status: final ledger cannot contain {status!r} entry")
    if isinstance(method, str) and method not in LEDGER_METHODS:
        errors.append(f"{path}.method: expected one of {sorted(LEDGER_METHODS)}, got {method!r}")

    validate_ledger_source_refs(entry, path, errors, plan_index)
    validate_ledger_state(entry.get("state"), f"{path}.state", errors, worktree, entry)
    validate_ledger_evidence(
        entry.get("evidence"), f"{path}.evidence", errors, method=method
    )

    if status == "manual_required" or method == "manual":
        validate_manual_evidence(
            entry.get("manual_evidence"),
            f"{path}.manual_evidence",
            errors,
            criterion_id=criterion_id if isinstance(criterion_id, str) else None,
            known_criteria=set(plan_index.get("task_ac_ids", set())),
        )


def validate_ledger_source_refs(
    entry: dict[str, Any], path: str, errors: list[str], plan_index: dict[str, Any]
) -> None:
    criterion_id = entry.get("criterion_id")
    refs = entry.get("source_refs")
    if not isinstance(refs, list) or not refs:
        errors.append(f"{path}.source_refs: expected non-empty array")
        return
    parsed_refs: list[dict[str, str]] = []
    for index, ref in enumerate(refs):
        parsed = validate_source_ref(ref, f"{path}.source_refs[{index}]", errors)
        if parsed is not None:
            parsed_refs.append(parsed)
    expected = (
        plan_index.get("task_ac_sources", {}).get(criterion_id)
        if isinstance(criterion_id, str)
        else None
    )
    if expected is not None and sorted(parsed_refs, key=ref_sort_key) != sorted(expected, key=ref_sort_key):
        errors.append(f"{path}.source_refs: does not match task acceptance criterion source_refs")


def ref_sort_key(ref: dict[str, str]) -> tuple[str, str]:
    return (ref["type"], ref["id"])


def validate_ledger_state(
    state: Any,
    path: str,
    errors: list[str],
    worktree: Path,
    entry: dict[str, Any],
) -> None:
    if not isinstance(state, dict):
        errors.append(f"{path}: expected object")
        return
    for field in ("git_ref", "commit", "worktree", "captured_at"):
        require_non_empty_string(state, field, f"{path}.{field}", errors)
    captured_at = state.get("captured_at")
    if isinstance(captured_at, str) and captured_at.strip():
        validate_iso_datetime(captured_at, f"{path}.captured_at", errors)

    commit = state.get("commit")
    evidence = entry.get("evidence")
    evidence_files = extract_evidence_paths(evidence)
    if isinstance(commit, str) and commit.strip() and evidence_files:
        stale = evidence_paths_changed_since(commit, evidence_files, worktree)
        if stale is True:
            errors.append(
                f"{path}.commit: stale evidence; cited files changed after {commit!r}"
            )
        elif stale is None:
            errors.append(
                f"{path}.commit: unable to verify evidence freshness for {commit!r} in {worktree}"
            )


def validate_ledger_evidence(
    evidence: Any, path: str, errors: list[str], *, method: Any
) -> None:
    if not isinstance(evidence, dict):
        errors.append(f"{path}: expected object")
        return

    files = require_string_list(evidence, "files", f"{path}.files", errors)
    commands = evidence.get("commands")
    if not isinstance(commands, list):
        errors.append(f"{path}.commands: expected array")
        commands = []
    if not files and not commands:
        errors.append(f"{path}: expected file/symbol evidence or command evidence")
    if method in COMMAND_EVIDENCE_METHODS and not commands:
        errors.append(f"{path}.commands: expected at least one command for command evidence")

    for index, command in enumerate(commands):
        command_path = f"{path}.commands[{index}]"
        if not isinstance(command, dict):
            errors.append(f"{command_path}: expected object")
            continue
        for field in ("cwd", "command", "observed"):
            require_non_empty_string(command, field, f"{command_path}.{field}", errors)
        exit_code = command.get("exit_code")
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            errors.append(f"{command_path}.exit_code: expected integer")
        elif exit_code != 0:
            errors.append(f"{command_path}.exit_code: final ledger command must pass, got {exit_code}")

    require_string_list(evidence, "edge_cases", f"{path}.edge_cases", errors, required=False)
    require_string_list(evidence, "context_bundles", f"{path}.context_bundles", errors, required=False)
    mocks = evidence.get("mocks")
    if mocks is not None and (not isinstance(mocks, str) or not mocks.strip()):
        errors.append(f"{path}.mocks: expected non-empty string when present")


def validate_manual_evidence(
    evidence: Any,
    path: str,
    errors: list[str],
    *,
    criterion_id: str | None,
    known_criteria: set[str],
) -> None:
    if not isinstance(evidence, dict):
        errors.append(f"{path}: expected object for manual_required entry")
        return
    required_fields = (
        "criterion_ids",
        "approval_provenance",
        "observed_result",
        "scope",
        "limits",
        "state_reference",
        "approved_at",
    )
    for field in required_fields:
        if field == "criterion_ids":
            values = require_string_list(evidence, field, f"{path}.{field}", errors)
            if not values:
                errors.append(f"{path}.{field}: expected at least one criterion id")
            for manual_criterion_id in values:
                if manual_criterion_id not in known_criteria:
                    errors.append(
                        f"{path}.{field}: unknown acceptance criterion {manual_criterion_id!r}"
                    )
            if criterion_id is not None and criterion_id not in values:
                errors.append(
                    f"{path}.{field}: must include ledger criterion_id {criterion_id!r}"
                )
        else:
            require_non_empty_string(evidence, field, f"{path}.{field}", errors)
    approved_at = evidence.get("approved_at")
    if isinstance(approved_at, str) and approved_at.strip():
        validate_iso_datetime(approved_at, f"{path}.approved_at", errors)
    approved = evidence.get("approved")
    if approved is not True:
        errors.append(f"{path}.approved: expected true for approved manual evidence")


def extract_evidence_paths(evidence: Any) -> list[str]:
    if not isinstance(evidence, dict):
        return []
    raw_files = evidence.get("files")
    if not isinstance(raw_files, list):
        return []
    paths: list[str] = []
    for item in raw_files:
        if not isinstance(item, str):
            continue
        stripped = item.strip()
        if stripped.startswith(("http://", "https://")):
            continue
        path = stripped.split(":", 1)[0].strip()
        if path:
            paths.append(path)
    return paths


def evidence_paths_changed_since(commit: str, paths: list[str], worktree: Path) -> bool | None:
    try:
        subprocess.run(
            ["git", "rev-parse", "--verify", f"{commit}^{{commit}}"],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
        tracked_result = subprocess.run(
            ["git", "ls-files", "--error-unmatch", "--", *paths],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        committed_result = subprocess.run(
            ["git", "diff", "--quiet", f"{commit}..HEAD", "--", *paths],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        worktree_result = subprocess.run(
            ["git", "diff", "--quiet", "HEAD", "--", *paths],
            cwd=worktree,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if tracked_result.returncode != 0:
        return True
    if committed_result.returncode not in (0, 1) or worktree_result.returncode not in (0, 1):
        return None
    return committed_result.returncode == 1 or worktree_result.returncode == 1


def require_non_empty_string(
    obj: dict[str, Any], field: str, path: str, errors: list[str]
) -> bool:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected non-empty string")
        return False
    return True


def require_string_list(
    obj: dict[str, Any],
    field: str,
    path: str,
    errors: list[str],
    *,
    required: bool = True,
) -> list[str]:
    if field not in obj and not required:
        return []
    value = obj.get(field)
    if not isinstance(value, list):
        errors.append(f"{path}: expected string array")
        return []
    strings = [item for item in value if isinstance(item, str) and item.strip()]
    if len(strings) != len(value):
        errors.append(f"{path}: expected non-empty string array")
    return strings


def validate_iso_datetime(value: str, path: str, errors: list[str]) -> None:
    try:
        datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        errors.append(f"{path}: expected ISO 8601 datetime string")


def validate_sequential_orders(values: list[int], path: str, errors: list[str]) -> None:
    if not values:
        return
    expected = list(range(1, len(values) + 1))
    if sorted(values) != expected:
        errors.append(f"{path}: expected sequential values {expected}, got {sorted(values)}")


def validate_sequential_ids(
    values: list[str], prefix: str, path: str, errors: list[str]
) -> None:
    valid_numbers = sorted(
        int(value.removeprefix(prefix))
        for value in values
        if value.startswith(prefix) and value.removeprefix(prefix).isdigit()
    )
    if not valid_numbers:
        return
    expected_numbers = list(range(1, len(valid_numbers) + 1))
    if valid_numbers != expected_numbers:
        expected_ids = [f"{prefix}{number}" for number in expected_numbers]
        actual_ids = [f"{prefix}{number}" for number in valid_numbers]
        errors.append(f"{path}: expected sequential ids {expected_ids}, got {actual_ids}")


def add_duplicate_errors(
    values: list[str], label: str, path: str, errors: list[str]
) -> None:
    for value in duplicates(values):
        errors.append(f"{path}: duplicate {label} {value!r}")


def duplicates(values: list[Any]) -> list[Any]:
    return sorted(
        (value for value, count in Counter(values).items() if count > 1),
        key=lambda item: repr(item),
    )


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, str] = {}
    path: list[str] = []

    def visit(node: str) -> list[str] | None:
        marker = state.get(node)
        if marker == "visiting":
            start = path.index(node)
            return path[start:] + [node]
        if marker == "visited":
            return None

        state[node] = "visiting"
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in graph:
                continue
            cycle = visit(neighbor)
            if cycle:
                return cycle
        path.pop()
        state[node] = "visited"
        return None

    for node in graph:
        cycle = visit(node)
        if cycle:
            return cycle
    return None


if __name__ == "__main__":
    raise SystemExit(main())
