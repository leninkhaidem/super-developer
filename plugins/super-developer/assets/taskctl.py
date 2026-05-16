#!/usr/bin/env python3
"""Helper commands for planned-feature package proofs."""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


VALIDATOR_PATH = Path(__file__).with_name("validate-tasks-json.py")


class TaskctlError(Exception):
    def __init__(self, errors: list[str], *, exit_code: int = 1) -> None:
        super().__init__("\n".join(errors))
        self.errors = errors
        self.exit_code = exit_code


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except TaskctlError as exc:
        write_json(
            sys.stderr,
            {
                "ok": False,
                "command": args.command,
                "errors": exc.errors,
            },
        )
        return exc.exit_code


def build_parser() -> argparse.ArgumentParser:
    description = (
        "Package-proof helper. This release adds package-level proof lifecycle "
        "writers while preserving verification.json as the final gate."
    )
    parser = argparse.ArgumentParser(description=description)
    subparsers = parser.add_subparsers(dest="command", required=True)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument(
        "--tasks",
        required=True,
        help="Path to .tasks/<feature>/tasks.json.",
    )
    common.add_argument(
        "--worktree",
        default=".",
        help="Worktree for stale evidence checks; defaults to current directory.",
    )

    proof_template = subparsers.add_parser(
        "proof-template",
        parents=[common],
        help="Emit a deterministic package proof template to stdout.",
    )
    proof_template.add_argument("--package", required=True, help="Work package id.")
    proof_template.set_defaults(func=cmd_proof_template)

    validate_proof = subparsers.add_parser(
        "validate-proof",
        parents=[common],
        help="Validate one package proof file.",
    )
    validate_proof.add_argument("proof", help="Path to WP<N>.proof.json.")
    validate_proof.set_defaults(func=cmd_validate_proof)

    validate_proofs = subparsers.add_parser(
        "validate-proofs",
        parents=[common],
        help="Validate exactly one proof file for every work package.",
    )
    validate_proofs.set_defaults(func=cmd_validate_proofs)

    must_prove = subparsers.add_parser(
        "must-prove",
        parents=[common],
        help="Emit acceptance criteria and evidence obligations.",
    )
    must_prove.add_argument("--package", help="Limit output to one work package.")
    must_prove.set_defaults(func=cmd_must_prove)

    summary = subparsers.add_parser(
        "summary",
        parents=[common],
        help="Emit read-only task, package, and proof-health summary.",
    )
    summary.add_argument("--package", help="Limit output to one work package.")
    summary.set_defaults(func=cmd_summary)

    accept_package = subparsers.add_parser(
        "accept-package",
        parents=[common],
        help="Write accepted lifecycle state for one package proof.",
    )
    accept_package.add_argument("proof", help="Exact path to WP<N>.proof.json.")
    accept_package.set_defaults(func=cmd_accept_package)

    reopen_package = subparsers.add_parser(
        "reopen-package",
        parents=[common],
        help="Write reopened lifecycle state for one package proof.",
    )
    reopen_package.add_argument("proof", help="Exact path to WP<N>.proof.json.")
    reopen_package.set_defaults(func=cmd_reopen_package)
    return parser


def cmd_proof_template(args: argparse.Namespace) -> int:
    validator, plan = load_plan(Path(args.tasks))
    package = require_package(plan, args.package)
    template = {
        "schema_version": validator.PACKAGE_PROOF_SCHEMA_VERSION,
        "feature": plan.data["feature"],
        "package_id": package["id"],
        "entries": [
            proof_template_entry(plan, package["id"], criterion)
            for criterion in package_criteria(validator, plan, package["id"])
        ],
    }
    write_json(sys.stdout, template)
    return 0


def cmd_validate_proof(args: argparse.Namespace) -> int:
    validator, plan = load_plan(Path(args.tasks))
    proof_path = Path(args.proof)
    errors = validator.validate_package_proof_json_file(
        proof_path,
        plan.index,
        worktree=Path(args.worktree),
        tasks_path=plan.tasks_path,
    )
    if errors:
        raise TaskctlError(errors)
    write_json(
        sys.stdout,
        {
            "ok": True,
            "proof_path": str(proof_path),
        },
    )
    return 0


def cmd_validate_proofs(args: argparse.Namespace) -> int:
    validator, plan = load_plan(Path(args.tasks))
    results, errors = validate_all_proofs(validator, plan, Path(args.worktree))
    if errors:
        raise TaskctlError(errors)
    write_json(
        sys.stdout,
        {
            "ok": True,
            "proofs": results,
        },
    )
    return 0


def cmd_must_prove(args: argparse.Namespace) -> int:
    validator, plan = load_plan(Path(args.tasks))
    packages = selected_packages(plan, args.package)
    output = {
        "feature": plan.data["feature"],
        "read_only": True,
        "packages": [
            package_must_prove(validator, plan, package, Path(args.worktree))
            for package in packages
        ],
    }
    write_json(sys.stdout, output)
    return 0


def cmd_summary(args: argparse.Namespace) -> int:
    validator, plan = load_plan(Path(args.tasks))
    packages = selected_packages(plan, args.package)
    package_summaries = [
        package_summary(validator, plan, package, Path(args.worktree))
        for package in packages
    ]
    proof_counts = Counter(item["proof"]["status"] for item in package_summaries)
    output = {
        "feature": plan.data["feature"],
        "status": plan.data["status"],
        "read_only": True,
        "final_gate": "verification.json remains authoritative in this release.",
        "proof_health": dict(sorted(proof_counts.items())),
        "packages": package_summaries,
    }
    write_json(sys.stdout, output)
    return 0


def cmd_accept_package(args: argparse.Namespace) -> int:
    return mutate_package_lifecycle(args, "accepted")


def cmd_reopen_package(args: argparse.Namespace) -> int:
    return mutate_package_lifecycle(args, "reopened")


def mutate_package_lifecycle(args: argparse.Namespace, target_state: str) -> int:
    validator, plan = load_plan(Path(args.tasks))
    worktree = Path(args.worktree)
    proof_path = Path(args.proof)
    proof = load_proof_for_lifecycle_mutation(
        validator,
        plan,
        proof_path,
        worktree,
        target_state=target_state,
    )
    package_id = proof["package_id"]
    previous_state = validator.package_lifecycle_state_name(proof)

    if previous_state == target_state == "accepted":
        errors = validator.validate_package_proof_json(
            proof,
            plan.index,
            worktree=worktree,
            proof_path=proof_path,
            tasks_path=plan.tasks_path,
            enforce_entry_freshness=False,
        )
        if errors:
            raise TaskctlError(errors)
        errors = validator.validate_package_proof_json(
            proof,
            plan.index,
            worktree=worktree,
            proof_path=proof_path,
            tasks_path=plan.tasks_path,
            enforce_entry_freshness=target_state == "accepted",
        )
        if errors:
            raise TaskctlError(errors)

    transition_errors = validator.package_lifecycle_transition_errors(proof, target_state)
    if transition_errors:
        raise TaskctlError(transition_errors)

    changed = not (previous_state == target_state == "accepted")
    if changed:
        proof[validator.PACKAGE_LIFECYCLE_FIELD] = build_lifecycle_state(
            validator,
            proof,
            target_state,
            proof_path=proof_path,
            worktree=worktree,
        )
        errors = validator.validate_package_proof_json(
            proof,
            plan.index,
            worktree=worktree,
            proof_path=proof_path,
            tasks_path=plan.tasks_path,
            enforce_entry_freshness=target_state == "accepted",
        )
        if errors:
            raise TaskctlError(errors)
        atomic_write_json(proof_path, proof)

    lifecycle = proof[validator.PACKAGE_LIFECYCLE_FIELD]
    output = {
        "ok": True,
        "command": args.command,
        "package_id": package_id,
        "proof_path": str(proof_path),
        "lifecycle": {
            "previous_state": previous_state,
            "state": target_state,
            "changed": changed,
            "proof_digest": lifecycle["proof_digest"],
        },
    }
    write_json(sys.stdout, output)
    return 0


class Plan:
    def __init__(self, data: dict[str, Any], index: dict[str, Any], tasks_path: Path) -> None:
        self.data = data
        self.index = index
        self.tasks_path = tasks_path
        self.tasks = index_tasks(data)
        self.criteria = index_criteria(data)


def load_proof_for_lifecycle_mutation(
    validator: Any,
    plan: Plan,
    proof_path: Path,
    worktree: Path,
    *,
    target_state: str,
) -> dict[str, Any]:
    proof = load_package_proof_file(proof_path)
    current_state = validator.package_lifecycle_state_name(proof)
    proof_without_lifecycle = {
        key: value
        for key, value in proof.items()
        if key != validator.PACKAGE_LIFECYCLE_FIELD
    }
    errors = validator.validate_package_proof_json(
        proof_without_lifecycle,
        plan.index,
        worktree=worktree,
        proof_path=proof_path,
        tasks_path=plan.tasks_path,
        enforce_entry_freshness=target_state == "accepted" and current_state != "accepted",
    )
    package_id = proof.get("package_id")
    validator.validate_package_lifecycle_state_for_replacement(
        proof,
        "package proof.lifecycle",
        errors,
        plan.index,
        worktree,
        package_id=package_id if isinstance(package_id, str) else None,
        proof_path=proof_path,
        tasks_path=plan.tasks_path,
    )
    if errors:
        raise TaskctlError(errors)
    if not isinstance(package_id, str) or not package_id.strip():
        raise TaskctlError(["package proof.package_id: expected non-empty string"])
    require_package(plan, package_id)
    return proof


def load_validated_proof(
    validator: Any, plan: Plan, proof_path: Path, worktree: Path
) -> dict[str, Any]:
    errors = validator.validate_package_proof_json_file(
        proof_path,
        plan.index,
        worktree=worktree,
        tasks_path=plan.tasks_path,
    )
    if errors:
        raise TaskctlError(errors)
    proof = load_package_proof_file(proof_path)
    package_id = proof.get("package_id")
    if not isinstance(package_id, str) or not package_id.strip():
        raise TaskctlError(["package proof.package_id: expected non-empty string"])
    require_package(plan, package_id)
    return proof


def load_package_proof_file(proof_path: Path) -> dict[str, Any]:
    try:
        with proof_path.open("r", encoding="utf-8") as f:
            proof = json.load(f)
    except FileNotFoundError:
        raise TaskctlError([f"package proof: file not found at {proof_path}"])
    except json.JSONDecodeError as exc:
        raise TaskctlError([f"package proof: invalid JSON: {exc}"])
    except (OSError, UnicodeDecodeError) as exc:
        raise TaskctlError([f"package proof: unable to read {proof_path}: {exc}"])
    if not isinstance(proof, dict):
        raise TaskctlError(["package proof root: expected object"])
    return proof


def build_lifecycle_state(
    validator: Any,
    proof: dict[str, Any],
    target_state: str,
    *,
    proof_path: Path,
    worktree: Path,
) -> dict[str, Any]:
    timestamp_field = f"{target_state}_at"
    command = "accept-package" if target_state == "accepted" else "reopen-package"
    return {
        "state": target_state,
        "package_id": proof["package_id"],
        "proof_path": str(validator.normalized_existing_or_candidate_path(proof_path)),
        "proof_digest": validator.package_proof_digest(proof),
        timestamp_field: datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "writer": {
            "tool": validator.PACKAGE_LIFECYCLE_WRITER_TOOL,
            "command": command,
            "schema_version": validator.PACKAGE_LIFECYCLE_WRITER_SCHEMA_VERSION,
        },
        "state_binding": {
            "state": target_state,
            "worktree": str(validator.normalized_existing_or_candidate_path(worktree)),
            "git_ref": current_git_ref(worktree),
            "commit": current_git_commit(worktree),
        },
    }


def current_git_ref(worktree: Path) -> str:
    result = run_git(worktree, "symbolic-ref", "--quiet", "--short", "HEAD", check=False)
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return current_git_commit(worktree)


def current_git_commit(worktree: Path) -> str:
    return run_git(worktree, "rev-parse", "HEAD").stdout.strip()


def run_git(
    worktree: Path, *args: str, check: bool = True
) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=worktree,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as exc:
        raise TaskctlError([f"git: unable to run {' '.join(args)} in {worktree}: {exc}"])
    if check and result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or f"exit {result.returncode}"
        raise TaskctlError([f"git {' '.join(args)} failed in {worktree}: {message}"])
    return result


def atomic_write_json(path: Path, value: Any) -> None:
    try:
        payload = json.dumps(value, indent=2, sort_keys=True) + "\n"
    except (TypeError, ValueError) as exc:
        raise TaskctlError([f"package proof: unable to serialize lifecycle state: {exc}"])

    tmp_name: str | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_name = tmp.name
            tmp.write(payload)
            tmp.flush()
            os.fsync(tmp.fileno())
        os.replace(tmp_name, path)
        tmp_name = None
    except OSError as exc:
        raise TaskctlError([f"package proof: unable to write {path}: {exc}"])
    finally:
        if tmp_name is not None:
            try:
                os.unlink(tmp_name)
            except FileNotFoundError:
                pass
            except OSError:
                pass


def load_plan(tasks_path: Path) -> tuple[Any, Plan]:
    validator = load_validator()
    try:
        with tasks_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        raise TaskctlError([f"tasks.json: file not found at {tasks_path}"], exit_code=2)
    except json.JSONDecodeError as exc:
        raise TaskctlError([f"tasks.json: invalid JSON: {exc}"], exit_code=2)
    except (OSError, UnicodeDecodeError) as exc:
        raise TaskctlError([f"tasks.json: unable to read {tasks_path}: {exc}"], exit_code=2)

    spec_path = tasks_path.with_name("SPEC.md")
    errors, plan_index = validator.validate_tasks_json(
        data,
        tasks_path=tasks_path,
        spec_path=spec_path,
    )
    if errors:
        raise TaskctlError(errors)
    return validator, Plan(data, plan_index, tasks_path)


def load_validator() -> Any:
    previous_dont_write_bytecode = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec = importlib.util.spec_from_file_location("validate_tasks_json", VALIDATOR_PATH)
        if spec is None or spec.loader is None:
            raise TaskctlError([f"validator: unable to load {VALIDATOR_PATH}"], exit_code=2)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.dont_write_bytecode = previous_dont_write_bytecode


def validate_all_proofs(
    validator: Any, plan: Plan, worktree: Path
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    results: list[dict[str, Any]] = []
    expected_paths = {
        validator.expected_package_proof_path(plan.tasks_path, package["id"])
        for package in work_packages(plan)
    }
    proofs_dir = plan.tasks_path.with_name("proofs")
    existing_paths = set(proofs_dir.glob("*.proof.json")) if proofs_dir.exists() else set()
    for extra_path in sorted(existing_paths - expected_paths):
        errors.append(f"package proof: unexpected proof file at {extra_path}")

    for package in work_packages(plan):
        proof_path = validator.expected_package_proof_path(plan.tasks_path, package["id"])
        proof_errors = validator.validate_package_proof_json_file(
            proof_path,
            plan.index,
            worktree=worktree,
            tasks_path=plan.tasks_path,
        )
        results.append(
            {
                "package_id": package["id"],
                "proof_path": str(proof_path),
                "ok": not proof_errors,
                "errors": proof_errors,
            }
        )
        errors.extend(f"{package['id']}: {error}" for error in proof_errors)
    return results, errors


def proof_template_entry(plan: Plan, package_id: str, criterion: dict[str, Any]) -> dict[str, Any]:
    criterion_id = criterion["id"]
    task_id = criterion_id.rsplit("-AC", 1)[0]
    context_bundles = sorted(
        required_context_bundles(plan, package_id, task_id, criterion_id)
    )
    return {
        "criterion_id": criterion_id,
        "task_id": task_id,
        "package_id": package_id,
        "status": "manual_required",
        "method": "manual",
        "source_refs": criterion["source_refs"],
        "state": {
            "git_ref": "",
            "commit": "",
            "worktree": "",
            "captured_at": "",
        },
        "evidence": {
            "files": [],
            "commands": [],
            "edge_cases": [],
            "context_bundles": context_bundles,
            "mocks": "none",
        },
        "manual_evidence": {
            "criterion_ids": [criterion_id],
            "approval_provenance": "",
            "observed_result": "",
            "scope": "",
            "limits": "",
            "state_reference": "",
            "approved_at": "",
            "approved": False,
        },
    }


def package_must_prove(
    validator: Any, plan: Plan, package: dict[str, Any], worktree: Path
) -> dict[str, Any]:
    proof = proof_health(validator, plan, package, worktree)
    criteria = []
    for criterion in package_criteria(validator, plan, package["id"]):
        criterion_id = criterion["id"]
        task_id = criterion_id.rsplit("-AC", 1)[0]
        task = plan.tasks[task_id]
        criteria.append(
            {
                "criterion_id": criterion_id,
                "task_id": task_id,
                "task_status": task["status"],
                "criterion": criterion["criterion"],
                "verification_hint": criterion.get("verification_hint"),
                "source_refs": criterion["source_refs"],
                "required_context_bundles": sorted(
                    required_context_bundles(plan, package["id"], task_id, criterion_id)
                ),
            }
        )
    return {
        "package_id": package["id"],
        "title": package["title"],
        "task_ids": package["task_ids"],
        "risk_tags": package["risk_tags"],
        "required_context_bundles": package["required_context_bundles"],
        "task_status_counts": dict(sorted(package_task_statuses(plan, package).items())),
        "proof": proof,
        "criteria": criteria,
    }


def package_summary(
    validator: Any, plan: Plan, package: dict[str, Any], worktree: Path
) -> dict[str, Any]:
    proof = proof_health(validator, plan, package, worktree)
    criteria = package_criteria(validator, plan, package["id"])
    return {
        "package_id": package["id"],
        "title": package["title"],
        "task_ids": package["task_ids"],
        "task_statuses": {
            task_id: plan.tasks[task_id]["status"] for task_id in package["task_ids"]
        },
        "risk_tags": package["risk_tags"],
        "required_context_bundles": package["required_context_bundles"],
        "criteria_total": len(criteria),
        "proof": proof,
    }


def proof_health(
    validator: Any, plan: Plan, package: dict[str, Any], worktree: Path
) -> dict[str, Any]:
    proof_path = validator.expected_package_proof_path(plan.tasks_path, package["id"])
    errors = validator.validate_package_proof_json_file(
        proof_path,
        plan.index,
        worktree=worktree,
        tasks_path=plan.tasks_path,
    )
    status = "valid" if not errors else "invalid"
    if errors and any("file not found" in error for error in errors):
        status = "missing"
    return {
        "status": status,
        "path": str(proof_path),
        "ok": not errors,
        "error_count": len(errors),
        "errors": errors,
    }


def package_criteria(
    validator: Any, plan: Plan, package_id: str
) -> list[dict[str, Any]]:
    ac_ids = validator.package_acceptance_criteria(plan.index, package_id)
    return [plan.criteria[ac_id] for ac_id in sorted(ac_ids)]


def required_context_bundles(
    plan: Plan, package_id: str, task_id: str, criterion_id: str
) -> set[str]:
    required = set(plan.index["package_required_context_bundles"].get(package_id, set()))
    required.update(plan.index["task_required_context_bundles"].get(task_id, set()))
    for ref in plan.index["task_ac_sources"].get(criterion_id, []):
        if ref.get("type") == "context_bundle":
            required.add(ref["id"])
    return required


def package_task_statuses(plan: Plan, package: dict[str, Any]) -> Counter[str]:
    return Counter(plan.tasks[task_id]["status"] for task_id in package["task_ids"])


def selected_packages(plan: Plan, package_id: str | None) -> list[dict[str, Any]]:
    if package_id is None:
        return work_packages(plan)
    return [require_package(plan, package_id)]


def require_package(plan: Plan, package_id: str) -> dict[str, Any]:
    for package in work_packages(plan):
        if package["id"] == package_id:
            return package
    raise TaskctlError([f"work package: unknown package id {package_id!r}"])


def work_packages(plan: Plan) -> list[dict[str, Any]]:
    return plan.data["work_packages"]


def index_tasks(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    tasks: dict[str, dict[str, Any]] = {}
    for phase in data["phases"]:
        for task in phase["tasks"]:
            tasks[task["id"]] = task
    return tasks


def index_criteria(data: dict[str, Any]) -> dict[str, dict[str, Any]]:
    criteria: dict[str, dict[str, Any]] = {}
    for phase in data["phases"]:
        for task in phase["tasks"]:
            for criterion in task["acceptance_criteria"]:
                criteria[criterion["id"]] = criterion
    return criteria


def write_json(stream: Any, value: Any) -> None:
    json.dump(value, stream, indent=2, sort_keys=True)
    stream.write("\n")


if __name__ == "__main__":
    raise SystemExit(main())
