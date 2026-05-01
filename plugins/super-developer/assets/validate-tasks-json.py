#!/usr/bin/env python3
"""Validate super-developer tasks.json files.

This asset is intentionally dependency-free so skills can execute it before
trusting task plans produced by agents.
"""

from __future__ import annotations

import argparse
import json
import re
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
WORK_PACKAGE_ID_RE = re.compile(r"WP[1-9]\d*")
DESIGN_DECISION_ID_RE = re.compile(r"DD-[1-9]\d*")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a super-developer .tasks/<feature>/tasks.json file."
    )
    parser.add_argument("tasks_json", help="Path to the tasks.json file to validate")
    args = parser.parse_args()

    path = Path(args.tasks_json)
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read {path}: {exc}", file=sys.stderr)
        return 1

    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: invalid JSON in {path}: {exc}", file=sys.stderr)
        return 1

    errors = validate_tasks_json(data)
    if errors:
        print(f"ERROR: tasks.json validation failed with {len(errors)} error(s):")
        for error in errors:
            print(f"  - {error}")
        return 1

    print("OK: tasks.json is valid")
    return 0


def validate_tasks_json(data: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return ["root: expected JSON object"]

    validate_top_level(data, errors)

    phases = data.get("phases")
    work_packages = data.get("work_packages")

    task_ids: set[str] = set()
    task_dependencies: dict[str, list[str]] = {}
    task_phase_order: dict[str, int] = {}

    if isinstance(phases, list):
        validate_phases(phases, errors, task_ids, task_dependencies, task_phase_order)
    else:
        errors.append("phases: expected array")

    if isinstance(work_packages, list):
        validate_work_packages(work_packages, errors, task_ids, task_dependencies)
    else:
        errors.append("work_packages: expected array")

    validate_task_dependencies(task_dependencies, task_ids, task_phase_order, errors)
    return errors


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
        return

    design_decisions = data["design_decisions"]
    if not isinstance(design_decisions, list):
        errors.append("design_decisions: expected array")
        return
    validate_design_decisions(design_decisions, errors)



def validate_design_decisions(
    design_decisions: list[Any], errors: list[str]
) -> None:
    decision_ids: list[str] = []

    for decision_index, decision in enumerate(design_decisions):
        decision_path = f"design_decisions[{decision_index}]"
        if not isinstance(decision, dict):
            errors.append(f"{decision_path}: expected object")
            continue

        for field in ("id", "decision", "rationale", "source"):
            require_non_empty_string(decision, field, f"{decision_path}.{field}", errors)

        decision_id = decision.get("id")
        if isinstance(decision_id, str) and decision_id.strip():
            if not DESIGN_DECISION_ID_RE.fullmatch(decision_id):
                errors.append(
                    f"{decision_path}.id: expected DD-<N>, got {decision_id!r}"
                )
            decision_ids.append(decision_id)

        source = decision.get("source")
        if isinstance(source, str) and source.strip():
            if source not in DESIGN_DECISION_SOURCES:
                errors.append(
                    f"{decision_path}.source: expected one of "
                    f"{sorted(DESIGN_DECISION_SOURCES)}, got {source!r}"
                )

        require_string_list(
            decision,
            "alternatives_considered",
            f"{decision_path}.alternatives_considered",
            errors,
        )

    add_duplicate_errors(
        decision_ids, "design decision id", "design_decisions", errors
    )
    validate_sequential_ids(decision_ids, "DD-", "design_decisions", errors)


def validate_phases(
    phases: list[Any],
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
    task_phase_order: dict[str, int],
) -> None:
    phase_ids: list[str] = []
    phase_orders: list[int] = []

    for phase_index, phase in enumerate(phases):
        phase_path = f"phases[{phase_index}]"
        if not isinstance(phase, dict):
            errors.append(f"{phase_path}: expected object")
            continue

        phase_id = phase.get("id")
        if require_non_empty_string(phase, "id", f"{phase_path}.id", errors):
            assert isinstance(phase_id, str)
            if not PHASE_ID_RE.fullmatch(phase_id):
                errors.append(f"{phase_path}.id: expected P<N>, got {phase_id!r}")
            phase_ids.append(phase_id)

        require_non_empty_string(phase, "name", f"{phase_path}.name", errors)
        require_non_empty_string(
            phase, "description", f"{phase_path}.description", errors
        )

        order = phase.get("order")
        if isinstance(order, bool) or not isinstance(order, int) or order < 1:
            errors.append(f"{phase_path}.order: expected positive integer")
            phase_order = phase_index + 1
        else:
            phase_orders.append(order)
            phase_order = order

        tasks = phase.get("tasks")
        if not isinstance(tasks, list):
            errors.append(f"{phase_path}.tasks: expected array")
            continue

        for task_index, task in enumerate(tasks):
            validate_task(
                task,
                f"{phase_path}.tasks[{task_index}]",
                phase_id if isinstance(phase_id, str) else None,
                phase_order,
                errors,
                task_ids,
                task_dependencies,
                task_phase_order,
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

    criteria = require_string_list(
        task, "acceptance_criteria", f"{task_path}.acceptance_criteria", errors
    )
    if not criteria:
        errors.append(f"{task_path}.acceptance_criteria: expected at least one item")


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
            if dependency not in task_ids:
                errors.append(f"task {task_id}: unknown task dependency {dependency!r}")
                continue
            if task_phase_order[dependency] > task_phase_order[task_id]:
                errors.append(
                    f"task {task_id}: dependency {dependency!r} is in a later phase"
                )

    cycle = find_cycle({task_id: deps for task_id, deps in task_dependencies.items()})
    if cycle:
        errors.append(f"task dependencies contain cycle: {' -> '.join(cycle)}")


def validate_work_packages(
    work_packages: list[Any],
    errors: list[str],
    task_ids: set[str],
    task_dependencies: dict[str, list[str]],
) -> None:
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
    validate_package_task_coverage(package_task_refs, task_ids, errors)
    validate_package_dependency_fields(package_dependencies, package_parallel, errors)
    validate_package_dependency_graph(package_dependencies, errors)
    validate_parallel_symmetry(package_parallel, errors)
    validate_cross_package_task_dependencies(
        package_task_refs, package_dependencies, task_dependencies, errors
    )


def validate_package_task_coverage(
    package_task_refs: dict[str, list[str]], task_ids: set[str], errors: list[str]
) -> None:
    task_to_packages: dict[str, list[str]] = defaultdict(list)
    for package_id, refs in package_task_refs.items():
        for task_id in refs:
            if task_id not in task_ids:
                errors.append(
                    f"work package {package_id}: unknown task id {task_id!r} in task_ids"
                )
            else:
                task_to_packages[task_id].append(package_id)

    for task_id in sorted(task_ids):
        packages = task_to_packages.get(task_id, [])
        if not packages:
            errors.append(f"task {task_id}: not assigned to any work package")
        elif len(packages) > 1:
            errors.append(
                f"task {task_id}: assigned to multiple work packages {sorted(packages)}"
            )


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
    package_parallel: dict[str, list[str]], errors: list[str]) -> None:
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


def require_non_empty_string(
    obj: dict[str, Any], field: str, path: str, errors: list[str]
) -> bool:
    value = obj.get(field)
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path}: expected non-empty string")
        return False
    return True


def require_string_list(
    obj: dict[str, Any], field: str, path: str, errors: list[str]
) -> list[str]:
    value = obj.get(field)
    if not isinstance(value, list):
        errors.append(f"{path}: expected array")
        return []

    strings: list[str] = []
    for index, item in enumerate(value):
        item_path = f"{path}[{index}]"
        if not isinstance(item, str) or not item.strip():
            errors.append(f"{item_path}: expected non-empty string")
            continue
        strings.append(item)
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
        int(value[len(prefix) :])
        for value in set(values)
        if re.fullmatch(rf"{prefix}[1-9]\d*", value)
    )
    if not valid_numbers:
        return
    expected = list(range(1, len(valid_numbers) + 1))
    if valid_numbers != expected:
        expected_ids = [f"{prefix}{number}" for number in expected]
        actual_ids = [f"{prefix}{number}" for number in valid_numbers]
        errors.append(f"{path}: expected sequential ids {expected_ids}, got {actual_ids}")


def add_duplicate_errors(
    values: list[str], label: str, path: str, errors: list[str]
) -> None:
    for value in duplicates(values):
        errors.append(f"{path}: duplicate {label} {value!r}")


def duplicates(values: list[str]) -> list[str]:
    return sorted(value for value, count in Counter(values).items() if count > 1)


def find_cycle(graph: dict[str, list[str]]) -> list[str] | None:
    state: dict[str, str] = {}
    stack: list[str] = []

    def visit(node: str) -> list[str] | None:
        node_state = state.get(node)
        if node_state == "visiting":
            start = stack.index(node)
            return stack[start:] + [node]
        if node_state == "visited":
            return None

        state[node] = "visiting"
        stack.append(node)
        for dependency in graph.get(node, []):
            if dependency not in graph:
                continue
            cycle = visit(dependency)
            if cycle:
                return cycle
        stack.pop()
        state[node] = "visited"
        return None

    for node in sorted(graph):
        cycle = visit(node)
        if cycle:
            return cycle
    return None


if __name__ == "__main__":
    raise SystemExit(main())
