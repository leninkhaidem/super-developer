#!/usr/bin/env python3
"""Proof and lifecycle helper for super-developer tasks.json plans."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


_SCRIPT_DIR = Path(__file__).resolve().parent
_VALIDATOR_PATH = _SCRIPT_DIR / "validate-tasks-json.py"


def _load_validator() -> Any:
    spec = importlib.util.spec_from_file_location("validate_tasks_json", _VALIDATOR_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"unable to load validator from {_VALIDATOR_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validator = _load_validator()


class TaskctlError(Exception):
    """Expected command failure with a concise user-facing message."""


def _json_bytes(data: Any) -> bytes:
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _write_json_atomic(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = _json_bytes(data)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(payload)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, path)
    except BaseException:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _load_plan(args: argparse.Namespace) -> tuple[dict[str, Any], dict[str, Any], Path]:
    tasks_path = _tasks_path(args)
    spec_path = _spec_path(args, tasks_path)
    result = validator.validate_plan_file(tasks_path, spec_path=spec_path)
    if result.errors:
        raise TaskctlError("tasks plan validation failed:\n" + _bullet_list(result.errors))
    if not isinstance(result.data, dict):
        raise TaskctlError("tasks plan root is not an object")
    return result.data, result.plan_index, tasks_path


def _load_json(path: Path, label: str) -> Any:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError as exc:
        raise TaskctlError(f"{label} not found at {path}") from exc
    except json.JSONDecodeError as exc:
        raise TaskctlError(f"{label} contains invalid JSON: {exc}") from exc
    except OSError as exc:
        raise TaskctlError(f"unable to read {label} at {path}: {exc}") from exc


def _tasks_path(args: argparse.Namespace) -> Path:
    if args.tasks is not None:
        return args.tasks
    if args.feature is None:
        raise TaskctlError("provide --feature or --tasks")
    return Path(".tasks") / args.feature / "tasks.json"


def _spec_path(args: argparse.Namespace, tasks_path: Path) -> Path | None:
    if args.spec is not None:
        return args.spec
    candidate = tasks_path.parent / "SPEC.md"
    return candidate if candidate.exists() else None


def _proofs_dir(args: argparse.Namespace, tasks_path: Path) -> Path:
    if getattr(args, "proofs_dir", None) is not None:
        return args.proofs_dir
    return tasks_path.parent / "proofs"


def _proof_path(args: argparse.Namespace, tasks_path: Path, package_id: str) -> Path:
    if getattr(args, "proof", None) is not None:
        return args.proof
    return _proofs_dir(args, tasks_path) / f"{package_id}.proof.json"


def _worktree(args: argparse.Namespace) -> Path:
    return args.worktree.resolve() if args.worktree is not None else Path.cwd().resolve()


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _bullet_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _ok(data: Any) -> int:
    sys.stdout.write(json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")
    return 0


def _package(plan: dict[str, Any], package_id: str) -> dict[str, Any]:
    for package in plan.get("work_packages", []):
        if isinstance(package, dict) and package.get("id") == package_id:
            return package
    raise TaskctlError(f"unknown work package {package_id!r}")


def _task(plan: dict[str, Any], task_id: str) -> dict[str, Any]:
    for task in _iter_tasks(plan):
        if task.get("id") == task_id:
            return task
    raise TaskctlError(f"unknown task {task_id!r}")


def _iter_tasks(plan: dict[str, Any]) -> list[dict[str, Any]]:
    tasks: list[dict[str, Any]] = []
    for phase in plan.get("phases", []):
        if not isinstance(phase, dict):
            continue
        for task in phase.get("tasks", []):
            if isinstance(task, dict):
                tasks.append(task)
    return tasks


def _package_tasks(plan: dict[str, Any], package_id: str) -> list[dict[str, Any]]:
    package = _package(plan, package_id)
    return [_task(plan, task_id) for task_id in package.get("task_ids", [])]


def _criteria_for_package(plan: dict[str, Any], package_id: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    task_ids = set(_package(plan, package_id).get("task_ids", []))
    for task in _iter_tasks(plan):
        task_id = task.get("id")
        if task_id not in task_ids:
            continue
        for criterion in task.get("acceptance_criteria", []):
            if isinstance(criterion, dict):
                rows.append({"task": task, "criterion": criterion})
    return sorted(rows, key=lambda row: row["criterion"].get("id", ""))


def _criterion_entry_skeleton(row: dict[str, Any], package: dict[str, Any]) -> dict[str, Any]:
    task = row["task"]
    criterion = row["criterion"]
    criterion_id = criterion.get("id", "")
    package_id = package.get("id", "")
    context_bundles = _required_context_bundle_ids_for_task(package, task)
    return {
        "criterion_id": criterion_id,
        "task_id": task.get("id", ""),
        "package_id": package_id,
        "status": _ledger_status("manual_required"),
        "method": _ledger_method("manual"),
        "source_refs": criterion.get("source_refs", []),
        "state": {
            "git_ref": "<branch-or-ref>",
            "commit": "<commit>",
            "worktree": "<worktree-path>",
            "captured_at": "<ISO-8601>",
        },
        "evidence": {
            "files": ["<changed-file-or-symbol>"],
            "commands": [],
            "edge_cases": [criterion.get("verification_hint", "<edge case or invariant>")],
            "context_bundles": context_bundles,
            "mocks": "No mocks used, or disclose exact mock/stub scope.",
        },
        "manual_evidence": {
            "criterion_ids": [criterion_id] if criterion_id else [],
            "approval_provenance": "<who/what approved manual evidence>",
            "observed_result": "<observed result>",
            "scope": "<scope reviewed>",
            "limits": "<known limits>",
            "state_reference": "<commit/ref/artifact>",
            "approved_at": "<ISO-8601>",
            "approved": False,
        },
    }


def _command_skeleton(command: str) -> dict[str, Any]:
    return {"cwd": "<worktree>", "command": command, "exit_code": 0, "observed": "<observed output>"}


def cmd_proof_template(args: argparse.Namespace) -> int:
    plan, _plan_index, tasks_path = _load_plan(args)
    package = _package(plan, args.package_id)
    proof = {
        "schema_version": 1,
        "feature": plan.get("feature"),
        "package_id": args.package_id,
        "package_verification": {
            "commands": [_command_skeleton(command) for command in package.get("verification_commands", [])]
        },
        "targeted_review": _targeted_review_template(plan, package),
        "entries": [
            _criterion_entry_skeleton(row, package)
            for row in _criteria_for_package(plan, args.package_id)
        ],
    }
    output = getattr(args, "output", None)
    if output is None:
        return _ok(proof)
    if output.exists() and not args.force:
        raise TaskctlError(f"refusing to overwrite existing proof template at {output}; pass --force")
    _write_json_atomic(output, proof)
    return _ok({"written": str(output), "criteria": [entry["criterion_id"] for entry in proof["entries"]], "tasks": str(tasks_path)})


def _targeted_review_template(plan: dict[str, Any], package: dict[str, Any]) -> dict[str, Any] | None:
    if not _requires_targeted_review(package):
        return None
    return {
        "status": "pending",
        "package_id": package.get("id"),
        "scope": "targeted package review for current package state",
        "reviewed_at": "<ISO-8601>",
        "state": {"commit": "<commit>", "git_ref": "<branch-or-ref>", "worktree": "<worktree-path>"},
        "findings": [],
        "approved_by": "<reviewer or review artifact>",
    }


def _requires_targeted_review(package: dict[str, Any]) -> bool:
    risk_tags = set(package.get("risk_tags", []))
    return bool(package.get("targeted_review_required")) or bool(risk_tags & validator.TARGETED_REVIEW_RISK_TAGS)


def _required_context_bundle_ids_for_task(package: dict[str, Any], task: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for source in (package.get("required_context_bundles", []), task.get("required_context_bundles", [])):
        for bundle_id in source:
            if isinstance(bundle_id, str) and bundle_id not in seen:
                ids.append(bundle_id)
                seen.add(bundle_id)
    return ids

def _required_context_bundle_ids_for_package(plan: dict[str, Any], package: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    seen: set[str] = set()
    for bundle_id in package.get("required_context_bundles", []):
        if isinstance(bundle_id, str) and bundle_id not in seen:
            ids.append(bundle_id)
            seen.add(bundle_id)
    package_task_ids = set(package.get("task_ids", []))
    for task in _iter_tasks(plan):
        if task.get("id") not in package_task_ids:
            continue
        for bundle_id in task.get("required_context_bundles", []):
            if isinstance(bundle_id, str) and bundle_id not in seen:
                ids.append(bundle_id)
                seen.add(bundle_id)
    return ids

def _validate_package_proof(args: argparse.Namespace, plan_index: dict[str, Any], tasks_path: Path, package_id: str) -> Any:
    proof_path = _proof_path(args, tasks_path, package_id)
    return validator.validate_package_proof_file(proof_path, plan_index, package_id=package_id, worktree=_worktree(args))


def cmd_validate_proof(args: argparse.Namespace) -> int:
    _plan, plan_index, tasks_path = _load_plan(args)
    result = _validate_package_proof(args, plan_index, tasks_path, args.package_id)
    return _ok({"ok": not result.errors, "package_id": args.package_id, "errors": result.errors, "criterion_ids": sorted(result.criterion_ids)}) or (0 if not result.errors else 1)


def cmd_validate_proofs(args: argparse.Namespace) -> int:
    plan, plan_index, tasks_path = _load_plan(args)
    result = validator.validate_all_package_proofs(_proofs_dir(args, tasks_path), plan_index, worktree=_worktree(args))
    errors = list(result.errors)
    for package in plan.get("work_packages", []):
        if not isinstance(package, dict):
            continue
        package_id = package.get("id")
        if not isinstance(package_id, str):
            continue
        try:
            package_gates = _require_package_gates(args, plan, tasks_path, package_id)
        except TaskctlError as exc:
            errors.append(f"package {package_id}: {exc}")
        else:
            for gate in package_gates:
                errors.append(f"package {package_id}: {gate}")
    _ok({"ok": not errors, "errors": errors, "criterion_ids": sorted(result.criterion_ids)})
    return 0 if not errors else 1


def _proof_json(args: argparse.Namespace, tasks_path: Path, package_id: str) -> dict[str, Any]:
    proof = _load_json(_proof_path(args, tasks_path, package_id), f"proof {package_id}")
    if not isinstance(proof, dict):
        raise TaskctlError(f"proof {package_id} root must be an object")
    return proof


def _require_package_gates(args: argparse.Namespace, plan: dict[str, Any], tasks_path: Path, package_id: str) -> list[str]:
    package = _package(plan, package_id)
    proof = _proof_json(args, tasks_path, package_id)
    missing: list[str] = []
    expected_commands = [str(command) for command in package.get("verification_commands", [])]
    if expected_commands:
        recorded = _proof_commands(proof.get("package_verification"))
        for command in expected_commands:
            if command not in recorded:
                missing.append(f"package verification command not recorded as passing: {command}")
    if _requires_targeted_review(package):
        review = proof.get("targeted_review")
        current = _current_commit(_worktree(args))
        if not isinstance(review, dict):
            missing.append("targeted package review evidence is missing")
        else:
            if review.get("status") != "passed":
                missing.append("targeted package review status is not passed")
            if review.get("package_id") != package_id:
                missing.append(f"targeted package review package_id {review.get('package_id')!r} does not match {package_id!r}")
            if not _non_empty(review.get("reviewed_at")):
                missing.append("targeted package review reviewed_at is missing")
            if not _non_empty(review.get("scope")):
                missing.append("targeted package review scope is missing")
            commit = _nested(review, "state", "commit")
            if not _non_empty(commit):
                missing.append("targeted package review state.commit is missing")
            elif current is None:
                missing.append("unable to determine current commit for targeted package review freshness")
            else:
                fresh = _is_ancestor_commit(_worktree(args), commit)
                if fresh is None:
                    missing.append(f"unable to verify targeted package review commit {commit!r} against current commit {current!r}")
                elif not fresh:
                    missing.append(f"targeted package review commit {commit!r} is not an ancestor of current commit {current!r}")
    return missing


def _proof_commands(section: Any) -> set[str]:
    commands: set[str] = set()
    if not isinstance(section, dict):
        return commands
    for row in section.get("commands", []):
        if not isinstance(row, dict):
            continue
        command = row.get("command")
        exit_code = row.get("exit_code")
        observed = row.get("observed")
        cwd = row.get("cwd")
        if (
            isinstance(command, str)
            and command
            and exit_code == 0
            and _non_empty(observed)
            and observed.strip() != "<observed output>"
            and _non_empty(cwd)
            and cwd.strip() != "<worktree>"
        ):
            commands.add(command)
    return commands



def _is_ancestor_commit(worktree: Path, ancestor: str) -> bool | None:
    try:
        result = subprocess.run(
            ["git", "merge-base", "--is-ancestor", ancestor, "HEAD"],
            cwd=worktree,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError:
        return None
    if result.returncode == 0:
        return True
    if result.returncode == 1:
        return False
    return None

def _current_commit(worktree: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=worktree,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError:
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def _non_empty(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _nested(value: Any, *keys: str) -> Any:
    current = value
    for key in keys:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def _task_status(name: str) -> str:
    if name not in validator.TASK_STATUSES:
        raise RuntimeError(f"validator does not define task status {name!r}")
    return name


def _feature_status(name: str) -> str:
    if name not in validator.FEATURE_STATUSES:
        raise RuntimeError(f"validator does not define feature status {name!r}")
    return name


def _ledger_status(name: str) -> str:
    if name not in validator.LEDGER_STATUSES:
        raise RuntimeError(f"validator does not define proof status {name!r}")
    return name


def _ledger_method(name: str) -> str:
    if name not in validator.LEDGER_METHODS:
        raise RuntimeError(f"validator does not define proof method {name!r}")
    return name

def _validate_after_mutation(data: dict[str, Any], tasks_path: Path, spec_path: Path | None) -> dict[str, Any]:
    errors, plan_index = validator.validate_tasks_json(data, tasks_path=tasks_path, spec_path=spec_path)
    if errors:
        raise TaskctlError("refusing to write invalid tasks plan:\n" + _bullet_list(errors))
    return plan_index


def cmd_accept_package(args: argparse.Namespace) -> int:
    plan, plan_index, tasks_path = _load_plan(args)
    proof_result = _validate_package_proof(args, plan_index, tasks_path, args.package_id)
    if proof_result.errors:
        raise TaskctlError("package proof validation failed:\n" + _bullet_list(proof_result.errors))
    missing = _require_package_gates(args, plan, tasks_path, args.package_id)
    if missing:
        raise TaskctlError("package acceptance gates are missing:\n" + _bullet_list(missing))
    completed_at = args.completed_at or _now_iso()
    for task in _package_tasks(plan, args.package_id):
        task["status"] = _task_status("done")
        task["completed_at"] = completed_at
        task.pop("blocked_reason", None)
        task.pop("blocked_at", None)
    _validate_after_mutation(plan, tasks_path, _spec_path(args, tasks_path))
    _write_json_atomic(tasks_path, plan)
    return _ok({"accepted": args.package_id, "completed_at": completed_at, "tasks": [task.get("id") for task in _package_tasks(plan, args.package_id)]})


def _final_gate_errors(plan: dict[str, Any], worktree: Path) -> list[str]:
    errors: list[str] = []
    current = _current_commit(worktree)
    for field in ("final_integration_review", "final_audit"):
        gate = plan.get(field)
        if not isinstance(gate, dict):
            errors.append(f"{field} evidence is missing")
            continue
        if gate.get("status") != "passed":
            errors.append(f"{field}.status is not passed")
        stamp_field = "reviewed_at" if field == "final_integration_review" else "audited_at"
        if not _non_empty(gate.get(stamp_field)):
            errors.append(f"{field}.{stamp_field} is missing")
        if not _non_empty(gate.get("source")):
            errors.append(f"{field}.source is missing")
        commit = _nested(gate, "state", "commit")
        if current is None:
            errors.append(f"unable to determine current commit for {field} freshness")
        elif commit != current:
            errors.append(f"{field}.state.commit {commit!r} does not match current commit {current!r}")
    return errors

def _final_gate_sources(args: argparse.Namespace) -> tuple[str, str] | None:
    review_source = getattr(args, "final_review_source", None)
    audit_source = getattr(args, "final_audit_source", None)
    if review_source is None and audit_source is None:
        return None
    if not _non_empty(review_source) or not _non_empty(audit_source):
        raise TaskctlError("--final-review-source and --final-audit-source must both be non-empty when recording final gates")
    return review_source.strip(), audit_source.strip()


def _record_final_gates(plan: dict[str, Any], args: argparse.Namespace) -> bool:
    sources = _final_gate_sources(args)
    if sources is None:
        return False
    current = _current_commit(_worktree(args))
    if current is None:
        raise TaskctlError("unable to determine current commit for final gate evidence")
    reviewed_at = audited_at = _now_iso()
    worktree = str(_worktree(args))
    review_source, audit_source = sources
    plan["final_integration_review"] = {
        "status": "passed",
        "source": review_source,
        "reviewed_at": reviewed_at,
        "state": {"git_ref": "HEAD", "commit": current, "worktree": worktree},
    }
    plan["final_audit"] = {
        "status": "passed",
        "source": audit_source,
        "audited_at": audited_at,
        "state": {"git_ref": "HEAD", "commit": current, "worktree": worktree},
    }
    return True


def cmd_finalize_feature(args: argparse.Namespace) -> int:
    plan, plan_index, tasks_path = _load_plan(args)
    final_gates_recorded = _record_final_gates(plan, args)
    proof_result = validator.validate_all_package_proofs(_proofs_dir(args, tasks_path), plan_index, worktree=_worktree(args))
    missing = list(proof_result.errors)
    for package in plan.get("work_packages", []):
        if not isinstance(package, dict):
            continue
        package_id = package.get("id")
        if isinstance(package_id, str):
            try:
                package_gates = _require_package_gates(args, plan, tasks_path, package_id)
            except TaskctlError as exc:
                missing.append(f"package {package_id}: {exc}")
            else:
                for gate in package_gates:
                    missing.append(f"package {package_id}: {gate}")
    for task in _iter_tasks(plan):
        if task.get("status") != _task_status("done"):
            missing.append(f"task {task.get('id')} is not done")
    missing.extend(_final_gate_errors(plan, _worktree(args)))
    if missing:
        _ok({"ok": False, "mutated": False, "final_gates_recorded": False, "missing_gates": missing})
        return 1
    completed_at = args.completed_at or _now_iso()
    plan["status"] = _feature_status("completed")
    plan["completed_at"] = completed_at
    _validate_after_mutation(plan, tasks_path, _spec_path(args, tasks_path))
    _write_json_atomic(tasks_path, plan)
    return _ok({"ok": True, "mutated": True, "final_gates_recorded": final_gates_recorded, "completed_at": completed_at})


def cmd_block_task(args: argparse.Namespace) -> int:
    reason = args.reason.strip()
    if not reason:
        raise TaskctlError("block-task requires a non-empty --reason")
    plan, _plan_index, tasks_path = _load_plan(args)
    task = _task(plan, args.task_id)
    task["status"] = _task_status("blocked")
    task["blocked_reason"] = reason
    task["blocked_at"] = args.blocked_at or _now_iso()
    task.pop("completed_at", None)
    _validate_after_mutation(plan, tasks_path, _spec_path(args, tasks_path))
    _write_json_atomic(tasks_path, plan)
    return _ok({"blocked": args.task_id, "reason": reason})


def cmd_reset_task(args: argparse.Namespace) -> int:
    plan, _plan_index, tasks_path = _load_plan(args)
    task = _task(plan, args.task_id)
    task["status"] = _task_status("pending")
    for field in ("blocked_reason", "blocked_at", "completed_at"):
        task.pop(field, None)
    _validate_after_mutation(plan, tasks_path, _spec_path(args, tasks_path))
    _write_json_atomic(tasks_path, plan)
    return _ok({"reset": args.task_id, "status": task["status"]})


def cmd_summary(args: argparse.Namespace) -> int:
    plan, plan_index, tasks_path = _load_plan(args)
    tasks = _iter_tasks(plan)
    task_counts = _counts(task.get("status") for task in tasks)
    packages = []
    proofs_dir = _proofs_dir(args, tasks_path)
    for package in sorted(plan.get("work_packages", []), key=lambda p: p.get("id", "") if isinstance(p, dict) else ""):
        if not isinstance(package, dict):
            continue
        package_id = package.get("id")
        package_tasks = _package_tasks(plan, package_id)
        proof_path = proofs_dir / f"{package_id}.proof.json"
        result = validator.validate_package_proof_file(proof_path, plan_index, package_id=package_id, worktree=_worktree(args))
        packages.append({
            "id": package_id,
            "title": package.get("title"),
            "task_counts": _counts(task.get("status") for task in package_tasks),
            "proof": {"path": str(proof_path), "ok": not result.errors, "errors": result.errors},
            "targeted_review_required": _requires_targeted_review(package),
        })
    return _ok({"feature": plan.get("feature"), "status": plan.get("status"), "task_counts": task_counts, "packages": packages})


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def cmd_next_package(args: argparse.Namespace) -> int:
    plan, _plan_index, _tasks_path = _load_plan(args)
    done_packages = {
        package.get("id")
        for package in plan.get("work_packages", [])
        if isinstance(package, dict) and all(task.get("status") == _task_status("done") for task in _package_tasks(plan, package.get("id")))
    }
    candidates = []
    blocked = []
    for package in sorted(plan.get("work_packages", []), key=lambda p: p.get("id", "") if isinstance(p, dict) else ""):
        if not isinstance(package, dict):
            continue
        package_id = package.get("id")
        tasks = _package_tasks(plan, package_id)
        statuses = {task.get("status") for task in tasks}
        missing_deps = [dep for dep in package.get("depends_on", []) if dep not in done_packages]
        blocked_tasks = [task.get("id") for task in tasks if task.get("status") == _task_status("blocked")]
        if blocked_tasks:
            blocked.append({"id": package_id, "blocked_tasks": blocked_tasks, "missing_dependencies": missing_deps})
        if not missing_deps and not blocked_tasks and _task_status("pending") in statuses:
            candidates.append({"id": package_id, "title": package.get("title"), "task_ids": package.get("task_ids", [])})
    return _ok({"candidates": candidates, "blocked": blocked, "completed_packages": sorted(done_packages)})


def cmd_must_prove(args: argparse.Namespace) -> int:
    plan, _plan_index, _tasks_path = _load_plan(args)
    package = _package(plan, args.package_id)
    bundles = _context_bundles(plan, _required_context_bundle_ids_for_package(plan, package))
    known_risk = _known_risk(args)
    checklist = {
        "feature": plan.get("feature"),
        "package_id": args.package_id,
        "title": package.get("title"),
        "risk_tags": package.get("risk_tags", []),
        "targeted_review_required": _requires_targeted_review(package),
        "required_context_bundles": bundles,
        "verification_commands": package.get("verification_commands", []),
        "acceptance_criteria": [],
        "known_risk_prompt": known_risk,
    }
    for row in _criteria_for_package(plan, args.package_id):
        task = row["task"]
        criterion = row["criterion"]
        checklist["acceptance_criteria"].append({
            "id": criterion.get("id"),
            "task_id": task.get("id"),
            "criterion": criterion.get("criterion"),
            "verification_hint": criterion.get("verification_hint"),
            "source_refs": criterion.get("source_refs", []),
            "required_context_bundles": _required_context_bundle_ids_for_task(package, task),
            "must_prove": [
                "criterion behavior is implemented in the current worktree state",
                "evidence cites changed files/symbols and observed commands where applicable",
                "edge cases and failure modes from the verification hint are covered or explicitly bounded",
                "mocks/stubs are absent or disclosed with exact scope",
            ],
        })
    return _ok(checklist)


def _context_bundles(plan: dict[str, Any], ids: list[str]) -> list[dict[str, Any]]:
    wanted = set(ids)
    bundles = []
    for bundle in plan.get("context_bundles", []):
        if isinstance(bundle, dict) and bundle.get("id") in wanted:
            bundles.append({
                "id": bundle.get("id"),
                "title": bundle.get("title"),
                "sources": bundle.get("sources", []),
                "verification_required": bundle.get("verification_required", []),
            })
    return sorted(bundles, key=lambda bundle: bundle.get("id", ""))



def _known_risk(args: argparse.Namespace) -> dict[str, Any] | None:
    source = args.known_risk_source
    if source is None:
        source = _SCRIPT_DIR.parent / "references" / "known-risk-patterns.md"
    if not source.exists():
        return None
    try:
        content = source.read_text(encoding="utf-8")
    except OSError as exc:
        raise TaskctlError(f"unable to read known-risk prompt source {source}: {exc}") from exc
    lines = [line.rstrip() for line in content.splitlines() if line.strip()]
    return {"path": str(source), "prompt": "\n".join(lines)}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage tasks.json package proof files and lifecycle state.")
    parser.add_argument("--feature", help="feature directory under .tasks/ used when --tasks is omitted")
    parser.add_argument("--tasks", type=Path, help="path to .tasks/<feature>/tasks.json")
    parser.add_argument("--spec", type=Path, help="path to SPEC.md; defaults to sibling of tasks.json when present")
    parser.add_argument("--worktree", type=Path, default=Path.cwd(), help="worktree used for proof freshness checks")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("proof-template", help="emit or write a package proof skeleton for one work package")
    p.add_argument("package_id")
    p.add_argument("--output", type=Path, help="write template to this proof path instead of stdout")
    p.add_argument("--force", action="store_true", help="overwrite an existing --output file")
    p.set_defaults(func=cmd_proof_template)

    p = sub.add_parser("validate-proof", help="validate one .tasks/<feature>/proofs/<WP-ID>.proof.json file")
    p.add_argument("package_id")
    p.add_argument("--proof", type=Path, help="explicit proof path; defaults to proofs/<WP-ID>.proof.json")
    p.add_argument("--proofs-dir", type=Path, help="proof directory used when --proof is omitted")
    p.set_defaults(func=cmd_validate_proof)

    p = sub.add_parser("validate-proofs", help="validate every package proof file for the feature")
    p.add_argument("--proofs-dir", type=Path, help="proof directory; defaults to tasks.json sibling proofs/")
    p.set_defaults(func=cmd_validate_proofs)

    p = sub.add_parser("accept-package", help="mark package tasks done after proof, verification, and review gates pass")
    p.add_argument("package_id")
    p.add_argument("--proof", type=Path, help="explicit package proof path")
    p.add_argument("--proofs-dir", type=Path, help="proof directory used when --proof is omitted")
    p.add_argument("--completed-at", help="ISO-8601 timestamp to record; defaults to current UTC time")
    p.set_defaults(func=cmd_accept_package)

    p = sub.add_parser("finalize-feature", help="preflight or complete the feature after all proofs and final gates pass")
    p.add_argument("--proofs-dir", type=Path, help="proof directory; defaults to tasks.json sibling proofs/")
    p.add_argument("--completed-at", help="ISO-8601 timestamp to record when completion is allowed")
    p.add_argument("--final-review-source", help="non-empty review-code CLEAN provenance to record as final integration review evidence")
    p.add_argument("--final-audit-source", help="non-empty audit PASS provenance to record as final audit evidence")
    p.set_defaults(func=cmd_finalize_feature)

    p = sub.add_parser("block-task", help="mark one task blocked with a required reason")
    p.add_argument("task_id")
    p.add_argument("--reason", required=True, help="non-empty blocker reason")
    p.add_argument("--blocked-at", help="ISO-8601 timestamp to record; defaults to current UTC time")
    p.set_defaults(func=cmd_block_task)

    p = sub.add_parser("reset-task", help="reset one task to pending and clear blocked/completion lifecycle fields")
    p.add_argument("task_id")
    p.set_defaults(func=cmd_reset_task)

    p = sub.add_parser("summary", help="report feature, task, package, and proof health without mutation")
    p.add_argument("--proofs-dir", type=Path, help="proof directory; defaults to tasks.json sibling proofs/")
    p.set_defaults(func=cmd_summary)

    p = sub.add_parser("next-package", help="report dependency-ready packages without persisting package status")
    p.set_defaults(func=cmd_next_package)

    p = sub.add_parser("must-prove", help="emit a deterministic read-only package checklist")
    p.add_argument("package_id")
    p.add_argument("--known-risk-source", type=Path, help="optional known-risk prompt source to include when present")
    p.set_defaults(func=cmd_must_prove)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except TaskctlError as exc:
        sys.stderr.write(str(exc) + "\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
