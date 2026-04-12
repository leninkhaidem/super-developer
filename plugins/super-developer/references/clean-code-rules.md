# Clean Code Rules

Rules for sub-agents to follow during implementation. The orchestrator passes this file to every sub-agent. The audit skill verifies compliance.

Thresholds are guidelines — if a sub-agent has a justified reason to exceed one (e.g., a data migration file that is inherently long), note the reason in the commit message rather than forcing an unnatural split.

---

## File-Level Rules

**No god files.** A single source file must not exceed 300 lines. If it does, decompose into focused modules before continuing.

**One concern per file.** Each file has a single, clear responsibility. Do not mix data models, business logic, and presentation in the same file.

**No orphan files.** Every file created must be imported or referenced somewhere. Unreachable code is dead code.

---

## Function-Level Rules

**Controlled function size.** Functions must not exceed 50 lines. If a function grows beyond that, extract sub-functions with descriptive names.

**Maximum 4 parameters.** Functions with more than 4 parameters must use an options or config object. This keeps call sites readable.

**Single return type.** Functions return a consistent type. No ambiguity between returning a value, returning undefined, or throwing.

**Maximum 3 levels of nesting.** If indentation exceeds 3 levels (e.g., `if > for > if`), extract the inner block into a named function.

---

## Naming and Structure Rules

**Descriptive naming over comments.** Variable and function names must be self-documenting. If a comment is needed to explain what a variable holds, rename the variable instead.

**No magic numbers or strings.** Extract hardcoded values into named constants. `MAX_RETRIES = 3` over bare `3`.

**Follow existing patterns.** Before writing new code, read existing files in the same directory and follow the established conventions — naming, error handling style, import ordering, file structure.

---

## Safety Rules

**No `any` types** (TypeScript projects). Use proper types. If a type is truly unknown, use `unknown` and narrow it.

**No silenced errors.** No empty `catch` blocks. Log, rethrow, or handle — never swallow.

**No hardcoded secrets or credentials.** Use environment variables or config files only.

---

## Anti-Pattern Rules

**No unnecessary abstractions.** Do not create a factory, wrapper, or utility class for something used once. Three similar lines of code is better than a premature abstraction.

**No speculative code.** Do not add configuration options, feature flags, or extension points for hypothetical future requirements. Build for the task at hand.
