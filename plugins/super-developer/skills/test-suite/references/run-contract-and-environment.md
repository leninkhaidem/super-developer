# Run Contract and Environment

Boundary: load before dependency installs, environment startup, secret/env-file writes, persistence
writes, generated/config changes, dashboard tooling, or any other side-effectful setup or execution.
No such action is authorized until the user approves the exact Run Contract.

## Run Contract Contents

The contract names the feature/head ref and commit to test, the target/base ref recorded separately,
and the branch/worktree where authored tests plus delivered feature code will run. Do not prove a
feature from target/base alone unless the delivered feature code is already included and recorded.

List exact approved actions:
- dependency install commands, package manager, workspace/package scope, network expectations, and any
  affected manifests, lockfiles, config, generated files, or tool caches;
- app, service, container, or daemon start commands; base URLs; health checks; ports; logs; process or
  container ownership; and teardown commands;
- env-file paths, secret variable names only, non-secret config values, seed/auth setup, and how values
  are supplied at runtime;
- persistence writes: database, queue, filesystem, object storage, browser profile, cache, fixture,
  namespace, seed, reset, and cleanup steps;
- run-specific artifact directories or IDs, whether they are gitignored, and retention expectations;
- optional dashboard/report tools, whether they are required or supplemental, and their output paths;
- non-authorized actions, including product-code edits, tracked secret writes, pushes, force operations,
  global/system installs, destructive shared-state operations, target/base merges, tags, and cleanup
  beyond this contract unless separately approved.

Approval is exact. A changed command, path, package manager, env-file location, port, persistence scope,
or teardown action requires renewed approval before execution. Worker packets may carry only the
approved contract and must stop on missing or ambiguous fields.

## Secrets and Env Files

Never write secret values to tracked files, committed docs, proof receipts, screenshots, videos, logs,
or dashboards. Committed text may name variable names and approved env-file paths only.

Secret values may be written only to an exact approved gitignored path. Before writing, verify the path
is untracked or ignored as intended. If the path is already tracked or appears to contain committed
secret-bearing content, stop for explicit untrack/new-path approval before any value is written.

## Idempotent Lifecycle

Each run uses a unique run ID or artifact directory. Commands must not depend on previous run leftovers,
ambient manual state, unrecorded local services, or stale dashboard artifacts. Integration, API, CLI,
and browser flows that touch state must use recorded seed, reset, namespace, fixture, or cleanup steps.

Teardown is required on success, red tests, abort, and stop paths for every owned process, container,
temporary file, database namespace, browser profile, or service started by the run, except where the
Run Contract explicitly keeps it alive. Record teardown result and any safe manual cleanup remaining.

Avoid destructive shared-state operations unless exact scope and recovery are approved. Do not run
against production or private data stores unless the user explicitly approves the environment, data
scope, and risk.

## Failure and Stop Rules

Stop and report instead of improvising when installs fail, health checks fail, ports conflict, required
credentials are absent, gitignore safety cannot be proven, state isolation is unclear, teardown cannot
be bounded, or safe rerunnable execution cannot be established. Include commands attempted, cwd, exit
code or observed failure, artifacts/log refs, likely cause, and the next approval or fix needed.
