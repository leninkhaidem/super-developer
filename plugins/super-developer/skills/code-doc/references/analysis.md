# Analysis Reference — Scout, Analysts & Synthesis

This document contains detection heuristics, analyst prompt templates, language-specific variants, and synthesis workflows for the code-doc skill.

---

## §1 Scout & Detection Heuristics

The scout phase uses signal-based heuristics to detect project characteristics. These are soft signals, not rigid rules—real projects often combine multiple patterns.

### §1.1 Project Type Heuristics

Detect project type by observing signals. A project may match multiple types (e.g., monorepo containing both library and web app).

#### Web Application (SPA)

| Signal | Weight | Notes |
|--------|--------|-------|
| `package.json` with `react`, `vue`, `angular`, `svelte` dep | High | Client-side framework |
| `src/index.tsx` or `src/main.ts` as entry | Medium | Standard SPA entry |
| `vite.config.*`, `webpack.config.*` present | Medium | Client bundler config |
| No `server/`, `api/`, `backend/` directories | Supporting | Pure client-side |
| `public/index.html` or `index.html` at root | Supporting | Static HTML shell |

**Conclusion:** → Single-page application. Focus on component tree, state management, routing.

#### Web Application (SSR/Fullstack)

| Signal | Weight | Notes |
|--------|--------|-------|
| `next.config.*`, `nuxt.config.*`, `remix.config.*` | High | SSR framework |
| `pages/` or `app/` directory with route files | High | File-based routing |
| `api/` routes alongside pages | Medium | Integrated backend |
| `getServerSideProps`, `loader`, server components | High | SSR patterns |
| Database client in deps (`prisma`, `drizzle`, `mongoose`) | Supporting | Data layer |

**Conclusion:** → Fullstack web app. Document both client components and server logic, API routes, data fetching patterns.

#### Library/Package

| Signal | Weight | Notes |
|--------|--------|-------|
| `lib/`, `src/` with `index.ts`/`index.js` exports | High | Library entry point |
| `package.json` with `main`, `module`, `exports` fields | High | Package distribution |
| `setup.py`/`pyproject.toml` with package metadata | High | Python package |
| `go.mod` with no `main.go` at root, exported packages | High | Go library |
| `Cargo.toml` with `[lib]` section | High | Rust crate |
| Minimal or no application entry point | Supporting | Not runnable |
| Extensive `test/` or `tests/` directory | Supporting | Library testing focus |

**Conclusion:** → Library/package. Focus on public API surface, exported types, usage examples.

#### CLI Tool

| Signal | Weight | Notes |
|--------|--------|-------|
| `pyproject.toml` with `[project.scripts]` or `console_scripts` | High | Python CLI |
| `package.json` with `bin` field | High | Node CLI |
| `cmd/` directory with main packages | High | Go CLI convention |
| `main.go` at root with `cobra`/`urfave/cli` imports | High | Go CLI frameworks |
| `argparse`, `click`, `typer` in Python deps | Medium | CLI frameworks |
| `yargs`, `commander`, `meow` in Node deps | Medium | CLI frameworks |
| No web server, no UI components | Supporting | Not a web app |

**Conclusion:** → CLI tool. Document commands, flags, configuration, usage examples.

#### Microservices

| Signal | Weight | Notes |
|--------|--------|-------|
| `docker-compose.yml` with multiple services | High | Multi-container setup |
| Multiple `Dockerfile`s in different directories | High | Containerized services |
| `services/` directory with independent subdirs | High | Service separation |
| Each service has own `package.json`/`go.mod`/`requirements.txt` | High | Independent deps |
| Kubernetes manifests (`k8s/`, `*.yaml` with `kind: Deployment`) | Medium | K8s orchestration |
| Message queue deps (`kafka`, `rabbitmq`, `redis` as queue) | Supporting | Inter-service comm |

**Conclusion:** → Microservices architecture. Document each service, inter-service communication, deployment topology.

#### Monolith

| Signal | Weight | Notes |
|--------|--------|-------|
| Single `package.json`/`go.mod`/`requirements.txt` at root | Medium | Unified deps |
| Large `src/` with deeply nested modules | Medium | All code in one tree |
| Single `Dockerfile` | Supporting | One deployable unit |
| No workspace configuration | Supporting | Not a monorepo |
| Database models + API routes + business logic colocated | Medium | All concerns together |

**Conclusion:** → Monolithic application. Document module boundaries, layered architecture, key workflows.

#### Monorepo

| Signal | Weight | Notes |
|--------|--------|-------|
| `package.json` with `workspaces` field | High | npm/yarn workspaces |
| `pnpm-workspace.yaml` present | High | pnpm workspaces |
| `lerna.json` present | High | Lerna monorepo |
| `nx.json` present | High | Nx monorepo |
| `Cargo.toml` with `[workspace]` section | High | Rust workspace |
| `go.work` file present | High | Go workspace |
| Multiple `package.json`/`go.mod` at different paths | Medium | Multi-project |
| `packages/`, `apps/`, `libs/` directory structure | Medium | Common monorepo layout |

**Conclusion:** → Monorepo. Detect sub-projects, offer unified vs per-project documentation.

#### Mobile Application

| Signal | Weight | Notes |
|--------|--------|-------|
| `android/` and/or `ios/` directories | High | Native mobile dirs |
| `react-native` in deps | High | React Native |
| `expo` in deps or `app.json` with expo config | High | Expo app |
| `flutter` directory or `pubspec.yaml` | High | Flutter app |
| `.xcodeproj`, `.xcworkspace` files | Medium | iOS project |
| `build.gradle` with Android plugin | Medium | Android project |

**Conclusion:** → Mobile application. Document screens/navigation, platform-specific code, native modules.

#### Desktop Application

| Signal | Weight | Notes |
|--------|--------|-------|
| `electron` in deps | High | Electron app |
| `tauri.conf.json` present | High | Tauri app |
| `main` and `renderer` process separation | Medium | Electron pattern |
| `src-tauri/` directory | Medium | Tauri structure |
| `.dmg`, `.exe`, `.AppImage` build targets | Supporting | Desktop distribution |
| `pyqt`, `tkinter`, `wxpython` imports | High | Python desktop |
| `fyne`, `wails` in Go deps | High | Go desktop |

**Conclusion:** → Desktop application. Document main/renderer processes, IPC, native integrations.

---

### §1.2 Framework Detection

Detect frameworks via dependency checks and file patterns. Use for tailored analysis prompts.

| Framework | Detection Pattern | Glob/File Check |
|-----------|-------------------|-----------------|
| **React** | `react` in package.json deps | `**/*.jsx`, `**/*.tsx`, `src/App.{jsx,tsx}` |
| **Next.js** | `next` in deps | `next.config.{js,mjs,ts}`, `pages/**/*`, `app/**/*` |
| **Vue** | `vue` in deps | `**/*.vue`, `src/App.vue`, `vite.config.ts` with vue plugin |
| **Nuxt** | `nuxt` in deps | `nuxt.config.{js,ts}`, `pages/**/*.vue` |
| **Angular** | `@angular/core` in deps | `angular.json`, `**/*.component.ts`, `**/*.module.ts` |
| **Django** | `django` in requirements/pyproject | `manage.py`, `settings.py`, `urls.py`, `**/views.py` |
| **Flask** | `flask` in requirements/pyproject | `app.py` or `**/__init__.py` with `Flask(__name__)` |
| **FastAPI** | `fastapi` in requirements/pyproject | `main.py` with `FastAPI()`, `**/routers/*.py` |
| **Spring Boot** | `spring-boot` in pom.xml/build.gradle | `**/Application.java`, `@SpringBootApplication`, `application.{yml,properties}` |
| **Rails** | `rails` in Gemfile | `config/routes.rb`, `app/controllers/**/*`, `Rakefile` |
| **Express** | `express` in package.json | `app.js`/`server.js` with `express()`, `**/routes/*.js` |
| **NestJS** | `@nestjs/core` in deps | `nest-cli.json`, `**/*.controller.ts`, `**/*.module.ts` |
| **Gin** | `github.com/gin-gonic/gin` in go.mod | `main.go` with `gin.Default()`, `**/handlers/*.go` |
| **Laravel** | `laravel/framework` in composer.json | `artisan`, `routes/web.php`, `app/Http/Controllers/**` |
| **Svelte/SvelteKit** | `svelte` or `@sveltejs/kit` in deps | `svelte.config.js`, `**/*.svelte`, `src/routes/**` |
| **Remix** | `@remix-run/node` in deps | `remix.config.js`, `app/routes/**`, `app/root.tsx` |

**Usage:** Run glob checks first (fast), then parse config files for confirmation. Framework detection drives analyst prompt selection.

---

### §1.3 Architecture Pattern Detection

Identify architecture patterns from directory structure and code organization.

#### MVC (Model-View-Controller)

| Signal | Confidence |
|--------|------------|
| `models/`, `views/`, `controllers/` directories | High |
| `app/models/`, `app/views/`, `app/controllers/` (Rails-style) | High |
| Django's `models.py`, `views.py` per app | High |
| Controller classes with action methods | Medium |
| View templates separate from logic | Supporting |

#### Layered Architecture

| Signal | Confidence |
|--------|------------|
| `presentation/`, `business/`, `data/` or `persistence/` layers | High |
| `api/`, `services/`, `repositories/` separation | High |
| `handlers/` → `services/` → `repositories/` call chain | Medium |
| Clear import direction (upper layers import lower) | Medium |
| DTOs/entities at layer boundaries | Supporting |

#### Hexagonal / Clean Architecture

| Signal | Confidence |
|--------|------------|
| `domain/`, `application/`, `infrastructure/` directories | High |
| `ports/` and `adapters/` directories | High |
| `core/` isolated from `infra/` | High |
| Interfaces defined in domain, implemented in infra | Medium |
| Dependency inversion (infra imports domain, not reverse) | Medium |
| Use cases / interactors as explicit classes | Supporting |

#### Microservices (see also §1.1)

| Signal | Confidence |
|--------|------------|
| Multiple independently deployable units | High |
| Service-to-service communication (HTTP, gRPC, messaging) | High |
| Each service owns its data store | Medium |
| API gateway or service mesh configuration | Supporting |
| Circuit breaker patterns (`resilience4j`, `polly`) | Supporting |

#### Serverless

| Signal | Confidence |
|--------|------------|
| `serverless.yml` or `serverless.ts` | High |
| `template.yaml` (AWS SAM) | High |
| `functions/` directory with handler files | High |
| Lambda handler signatures (`event`, `context`) | Medium |
| No long-running server process | Supporting |
| Cloud function deps (`@aws-sdk`, `firebase-functions`) | Supporting |

#### Event-Driven

| Signal | Confidence |
|--------|------------|
| Event bus / message broker integration | High |
| `events/`, `handlers/`, `subscribers/` directories | High |
| Event classes with `publish`/`subscribe` patterns | Medium |
| CQRS separation (commands vs queries) | Medium |
| Event sourcing patterns (event store, replay) | Supporting |
| Saga/choreography patterns | Supporting |

---

### §1.4 Entry Point & Module Boundary Detection

#### Entry Points

| Type | Detection Pattern |
|------|-------------------|
| **Node.js main** | `package.json` → `main` field, or `index.js`/`index.ts` at root |
| **Node.js bin** | `package.json` → `bin` field entries |
| **Python script** | `if __name__ == "__main__":` blocks |
| **Python package** | `__main__.py` in package directory |
| **Python CLI** | `pyproject.toml` → `[project.scripts]` entries |
| **Go binary** | `main.go` with `func main()`, or `cmd/*/main.go` |
| **Java** | Class with `public static void main(String[] args)` |
| **Spring Boot** | Class with `@SpringBootApplication` annotation |
| **Rust binary** | `src/main.rs` with `fn main()` |
| **Server startup** | Files named `server.{js,ts,py,go}`, `app.{js,ts,py}` |
| **Library index** | `src/index.{js,ts}`, `lib/index.{js,ts}`, `__init__.py` with exports |

#### Module Boundaries

| Pattern | Indicates |
|---------|-----------|
| Directory with own `package.json` | npm package boundary |
| Directory with `__init__.py` | Python package |
| Directory with `go.mod` | Go module boundary |
| Directory with `Cargo.toml` | Rust crate boundary |
| `index.{js,ts}` re-exporting from directory | Module public API |
| `internal/` directory (Go convention) | Private to module |
| `_` prefix on Python modules | Private by convention |
| Workspace member in monorepo config | Sub-project boundary |

---

### §1.5 Codebase Sizing

Count source files by type to determine agent strategy.

**File counting rules:**
- Include: `.ts`, `.tsx`, `.js`, `.jsx`, `.py`, `.go`, `.java`, `.rs`, `.rb`, `.php`, `.cs`, `.swift`, `.kt`
- Exclude: `node_modules/`, `vendor/`, `venv/`, `.venv/`, `target/`, `build/`, `dist/`, `__pycache__/`, `.git/`
- Exclude: Generated files (`*.generated.*`, `*.g.dart`, `*.pb.go`)
- Exclude: Type definitions from deps (`*.d.ts` in `node_modules/`)

**Counting command:**
```bash
find . -type f \( -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" -o -name "*.py" -o -name "*.go" -o -name "*.java" -o -name "*.rs" -o -name "*.rb" -o -name "*.php" \) \
  ! -path "*/node_modules/*" ! -path "*/vendor/*" ! -path "*/.venv/*" ! -path "*/venv/*" \
  ! -path "*/target/*" ! -path "*/build/*" ! -path "*/dist/*" ! -path "*/__pycache__/*" \
  | wc -l
```

**Size classifications:**

| Size | File Count | Agent Strategy |
|------|------------|----------------|
| **Small** | < 200 files | Single-agent mode. Scout + one analyst pass. |
| **Medium** | 200–1000 files | Scout + 2–3 concern-based analysts in parallel. |
| **Large** | > 1000 files | Full pipeline: scout + 4–5 analysts + dedicated synthesis. Monorepo detection triggers per-project option. |

**Why this matters:** Small codebases don't benefit from multi-agent overhead. Large codebases need parallel analysis to stay within time/cost budgets.

---

### §1.6 Existing Documentation Inventory

Before generating docs, inventory what exists. Never overwrite good human-written documentation.

**Scan targets:**

| Target | Check For |
|--------|-----------|
| `docs/` directory | Presence, file count, structure |
| `README.md` | Presence, length, sections |
| `CONTRIBUTING.md` | Presence, completeness |
| `CHANGELOG.md` | Presence, format |
| `API.md` or `api-docs/` | Manual API docs |
| Inline docstrings | JSDoc `/** */`, Python `"""docstrings"""`, Go `//` comments on exports |
| OpenAPI/Swagger | `openapi.yaml`, `swagger.json`, `**/openapi.*` |
| Architecture docs | `ARCHITECTURE.md`, `docs/architecture*`, `ADR/` |

**README quality heuristics:**

| Quality | Signals |
|---------|---------|
| **Minimal** | < 50 lines, only project name and basic description |
| **Adequate** | 50–200 lines, has installation + basic usage |
| **Comprehensive** | > 200 lines, has installation, usage, API overview, contributing, examples |

**Docstring coverage estimation:**
```bash
# JavaScript/TypeScript: count JSDoc comments vs exported functions
grep -r "^\s*/\*\*" --include="*.ts" --include="*.js" | wc -l  # JSDoc count
grep -r "^export " --include="*.ts" --include="*.js" | wc -l   # Export count

# Python: count docstrings vs function defs
grep -r '^\s*"""' --include="*.py" | wc -l   # Docstring count
grep -r "^\s*def " --include="*.py" | wc -l  # Function count
```

**Classification:**

| Level | Criteria | Action |
|-------|----------|--------|
| **No docs** | No README or < 20 lines, no docs/, < 10% docstring coverage | Fresh generation |
| **Partial** | README exists but thin, some docstrings, no architecture docs | Augment existing, fill gaps |
| **Comprehensive** | Good README, docs/ folder, > 50% docstring coverage, architecture docs | Preserve existing, augment only, flag for user review |

**Preservation rules:**
- Files with `<!-- human -->` or `<!-- manually maintained -->` markers: NEVER overwrite
- README.md with > 200 lines: augment only (add sections, don't rewrite)
- Existing `docs/*.md`: preserve, create new files for gaps
- Inline docstrings: never modify (native extractors read them)

---

### §1.7 Native Extractor Selection

Based on detected languages, select appropriate native documentation extractors. Native tools provide accurate API signatures; LLM analysts provide narrative and architecture understanding.

| Language | Primary Extractor | Command | Output |
|----------|-------------------|---------|--------|
| **TypeScript/JavaScript** | TypeDoc | `npx typedoc --json typedoc.json src/` | JSON with types, functions, classes |
| **Python** | Sphinx autodoc | `sphinx-apidoc -o docs/ src/` | RST files, or use `pydoc` for simple extraction |
| **Python (simple)** | pydoc | `python -m pydoc -w module` | HTML or use `ast` module for structured extraction |
| **Go** | godoc | `go doc -all ./...` or parse with `go/doc` | Package documentation |
| **Rust** | cargo doc | `cargo doc --no-deps --document-private-items` | HTML docs, parse from source via `rustdoc --output-format json` |
| **Java** | Javadoc | `javadoc -d docs/ -sourcepath src/ ...` | HTML documentation |
| **C#** | DocFX or XML docs | `dotnet build /p:GenerateDocumentationFile=true` | XML documentation file |
| **Ruby** | YARD | `yard doc` | HTML/JSON documentation |
| **PHP** | phpDocumentor | `phpdoc -d src/ -t docs/` | HTML documentation |

**Extractor availability check:**
```bash
# TypeScript
command -v npx && npm list typedoc

# Python
python -c "import sphinx" 2>/dev/null || echo "sphinx not available"

# Go
command -v go

# Rust
command -v cargo
```

**Fallback behavior:**
- If native extractor unavailable → analyst agents extract API surface via code reading
- Flag in output: `⚠️ No native extractor available for {language}. API signatures extracted via LLM analysis—verify accuracy.`
- Accuracy expectation: native extractor ~99% accurate, LLM extraction ~90% accurate (may miss overloads, generics edge cases)

**Integration flow:**
1. Scout detects primary language(s)
2. Check if extractor available and project is buildable
3. If `--with-build` flag: run extractor, feed output to analysts
4. If no flag or not buildable: analysts work from source directly

---

### §1.8 Monorepo Sub-Project Detection

Detect workspace roots and enumerate sub-projects. User chooses documentation strategy.

**Workspace root detection:**

| Tool | Config File | Workspace Field |
|------|-------------|-----------------|
| npm workspaces | `package.json` | `"workspaces": ["packages/*"]` |
| Yarn workspaces | `package.json` | `"workspaces": ["packages/*"]` |
| pnpm | `pnpm-workspace.yaml` | `packages:` list |
| Lerna | `lerna.json` | `"packages": ["packages/*"]` |
| Nx | `nx.json` + `workspace.json` | Projects in workspace.json |
| Turborepo | `turbo.json` | Uses npm/yarn/pnpm workspaces |
| Cargo | `Cargo.toml` | `[workspace] members = ["crates/*"]` |
| Go | `go.work` | `use` directives |

**Sub-project enumeration:**

```bash
# npm/yarn workspaces - expand globs from package.json workspaces field
node -e "console.log(require('./package.json').workspaces)"

# pnpm - parse pnpm-workspace.yaml
cat pnpm-workspace.yaml

# Lerna
cat lerna.json | jq '.packages'

# Nx
cat workspace.json | jq '.projects | keys'

# Cargo workspace
grep -A 20 '\[workspace\]' Cargo.toml | grep 'members'

# Go workspace
cat go.work | grep '^use'
```

**Sub-project classification:**

For each detected sub-project, run §1.1 heuristics to classify:

| Sub-project Path | Type | Entry Point |
|------------------|------|-------------|
| `packages/ui` | Library | `src/index.ts` |
| `packages/cli` | CLI Tool | `bin/cli.js` |
| `apps/web` | Web App (Next.js) | `pages/_app.tsx` |
| `apps/api` | Microservice | `src/server.ts` |

**Documentation strategy options:**

| Strategy | Description | When to use |
|----------|-------------|-------------|
| **Unified** | Single doc set covering all sub-projects | Tightly coupled monorepo, shared domain |
| **Per-project** | Separate doc set per sub-project | Independent packages, different audiences |
| **Hybrid** | Root architecture + per-project API docs | Mixed: shared infra + independent apps |

**User prompt:**
```
Detected monorepo with {N} sub-projects:
- packages/ui (Library)
- packages/cli (CLI Tool)
- apps/web (Next.js App)
...

Documentation strategy:
1. Unified — single comprehensive doc set
2. Per-project — separate docs for each sub-project
3. Hybrid — root architecture doc + per-project API docs

Choose [1/2/3]:
```

---

## §1 End

<!-- Section boundary: §2 Agent Prompt Templates follows -->


# Analysis Reference — §2 Agent Prompt Templates

This section provides 5 concern-based analyst prompt templates. Each template is a complete prompt ready to be passed to `task(agent_type='explore')`.

All analyst outputs use **structured Markdown** (not YAML) — this is LLM-to-LLM communication optimized for downstream synthesis.

---

## §2.1 Architecture Analyst

**Spawn Condition:** Always spawned for medium/large codebases (≥200 files). For small codebases (<200 files), this analysis is included in the single-agent mode.

### Complete Prompt Template

```markdown
# Architecture Analyst

You are analyzing a codebase to document its high-level architecture. Your output will be consumed by a synthesis agent, so use structured Markdown with consistent headers.

## Your Scope

Analyze the codebase for:
1. **Directory structure** — How is the code organized? What conventions are used?
2. **Module boundaries** — What are the major subsystems? Where are the boundaries?
3. **Entry points** — Where does execution begin? (main files, server entry, CLI entry, exports)
4. **Dependency graph** — How do modules depend on each other? What's the import direction?
5. **Design patterns** — What architectural patterns are evident? (MVC, hexagonal, microservices, monolith, etc.)

## Files to Analyze

Use these glob patterns to find relevant files:
- `**/package.json`, `**/pyproject.toml`, `**/go.mod`, `**/Cargo.toml`, `**/pom.xml`, `**/build.gradle` — dependency manifests
- `**/tsconfig.json`, `**/jsconfig.json` — module resolution config
- `**/*.md` in root and `/docs` — existing architecture documentation
- `**/src/**`, `**/lib/**`, `**/app/**`, `**/pkg/**` — source directories
- `**/index.{ts,js,py}`, `**/main.{ts,js,py,go,rs}`, `**/app.{ts,js,py}` — entry points
- `**/routes/**`, `**/controllers/**`, `**/handlers/**` — request handling layers
- `**/services/**`, `**/domain/**`, `**/core/**` — business logic layers
- `**/models/**`, `**/entities/**`, `**/schemas/**` — data layers

## Output Format

Structure your output EXACTLY as follows:

## Modules

List each major module/subsystem with:
- **Name**: Module identifier
- **Path**: Directory path(s)
- **Responsibility**: What this module does (1-2 sentences)
- **Visibility**: public | internal | private

Example:
### auth
- **Path**: `src/auth/`, `src/middleware/auth.ts`
- **Responsibility**: Handles user authentication, session management, and JWT token operations
- **Visibility**: public (exported via `src/index.ts`)

## Dependencies

Show the dependency direction between modules. Use a simple notation:
- `A → B` means A depends on B (A imports from B)
- Group by dependency type if helpful (runtime vs dev, internal vs external)

Internal module dependencies:
- `api → auth` (authentication middleware)
- `api → services` (business logic)
- `services → models` (data access)

Key external dependencies:
- `express` — HTTP framework
- `prisma` — ORM

## Entry Points

List all entry points with their purpose:
- **`src/index.ts`** — Main server entry, starts HTTP listener
- **`src/cli.ts`** — CLI tool entry point
- **`src/worker.ts`** — Background job processor

## Patterns

Identify architectural patterns with evidence:

### Layered Architecture
- **Evidence**: Distinct `controllers/`, `services/`, `models/` directories
- **Layers**: Controller → Service → Repository → Database
- **Notes**: Some controllers bypass services (technical debt in `legacy/`)

### Repository Pattern
- **Evidence**: `*Repository` classes in `src/repositories/`
- **Purpose**: Abstracts database access from business logic

## Key Abstractions

Document the most important interfaces/classes/types that define the system's contracts:

### `User`
- **Location**: `src/models/user.ts`
- **Purpose**: Core user entity used throughout auth and API layers
- **Used by**: auth, api, services

### `RequestContext`
- **Location**: `src/types/context.ts`
- **Purpose**: Request-scoped data passed through middleware chain
- **Used by**: All middleware and handlers

---

## Cross-References for Other Analysts

Note what other analysts should verify or expand on:
- **API Surface Analyst**: Verify endpoint list against `routes/` directory structure
- **Data Model Analyst**: The `models/` directory uses Prisma — provide schema details
- **Infrastructure Analyst**: Entry points suggest multiple deployment targets (server, worker, cli)
```

---

## §2.2 API Surface Analyst

**Spawn Condition:** Spawned when route definitions, controller patterns, or endpoint annotations are detected:
- Files matching: `**/routes/**`, `**/controllers/**`, `**/api/**`, `**/endpoints/**`
- Decorators/annotations: `@Get`, `@Post`, `@Route`, `@RequestMapping`, `@app.route`
- Framework patterns: Express `app.get()`, FastAPI `@router.get()`, Gin `r.GET()`
- OpenAPI/Swagger specs: `**/openapi.{yaml,json}`, `**/swagger.{yaml,json}`

### Complete Prompt Template

```markdown
# API Surface Analyst

You are documenting all public APIs exposed by this codebase. Your output will be consumed by a synthesis agent, so use structured Markdown with consistent headers.

## Your Scope

Analyze the codebase for:
1. **REST endpoints** — HTTP routes, methods, paths
2. **GraphQL operations** — Queries, mutations, subscriptions (if applicable)
3. **CLI commands** — If the project is a CLI tool
4. **Library exports** — Public API for library consumers
5. **Public interfaces** — Types/interfaces exposed for extension

## Input Sources

### Native Extractor Output (if available)
If the orchestrator provides native extractor output (TypeDoc JSON, Sphinx JSON, Godoc output), use it as your PRIMARY source for:
- Function signatures and types
- Parameter documentation
- Return types
- Export visibility

Location: `{repo_root}/.code-doc-cache/extractor-output.json` (if exists)

### Source Files to Analyze
- `**/routes/**/*.{ts,js,py,go,java}` — route definitions
- `**/controllers/**/*.{ts,js,py,go,java}` — controller classes
- `**/api/**/*.{ts,js,py,go,java}` — API handlers
- `**/resolvers/**/*.{ts,js,py,go}` — GraphQL resolvers
- `**/schema.{graphql,gql}`, `**/*.graphql` — GraphQL schema
- `**/openapi.{yaml,json}`, `**/swagger.{yaml,json}` — API specs
- `**/src/index.{ts,js}`, `**/lib.rs`, `**/mod.go` — library exports
- `**/bin/**`, `**/cli/**`, `**/cmd/**` — CLI commands

## Output Format

Structure your output EXACTLY as follows:

## Endpoints

Group by resource or domain area. For each endpoint:
- **Method + Path**: `GET /api/users/:id`
- **Handler**: `src/controllers/users.ts:getUser()`
- **Description**: Brief purpose
- **Auth**: Required authentication (none | token | api-key | session)

Example:

### Users

#### GET /api/users
- **Handler**: `src/controllers/users.ts:listUsers()`
- **Description**: List all users with pagination
- **Auth**: Bearer token required
- **Query params**: `page`, `limit`, `sort`

#### GET /api/users/:id
- **Handler**: `src/controllers/users.ts:getUser()`
- **Description**: Get single user by ID
- **Auth**: Bearer token required
- **Path params**: `id` (string, UUID)

#### POST /api/users
- **Handler**: `src/controllers/users.ts:createUser()`
- **Description**: Create new user
- **Auth**: Admin role required

### GraphQL Operations (if applicable)

#### Queries
- `users(page: Int, limit: Int): [User!]!` — List users with pagination
- `user(id: ID!): User` — Get user by ID

#### Mutations
- `createUser(input: CreateUserInput!): User!` — Create new user
- `updateUser(id: ID!, input: UpdateUserInput!): User!` — Update existing user

## Request/Response Schemas

Document key request/response shapes:

### CreateUserInput
```typescript
{
  email: string;      // Required, must be valid email
  name: string;       // Required, 1-100 chars
  role?: "user" | "admin";  // Optional, defaults to "user"
}
```

### UserResponse
```typescript
{
  id: string;         // UUID
  email: string;
  name: string;
  role: string;
  createdAt: string;  // ISO 8601 timestamp
  updatedAt: string;  // ISO 8601 timestamp
}
```

### PaginatedResponse<T>
```typescript
{
  data: T[];
  total: number;
  page: number;
  limit: number;
  hasMore: boolean;
}
```

## Authentication

Document authentication mechanisms:

### Bearer Token (JWT)
- **Header**: `Authorization: Bearer <token>`
- **Token source**: `/api/auth/login` endpoint
- **Expiry**: 24 hours
- **Refresh**: `/api/auth/refresh` endpoint

### API Key (for service-to-service)
- **Header**: `X-API-Key: <key>`
- **Scope**: Limited to read-only operations
- **Rate limit**: 1000 req/hour

## Error Codes

Document error response patterns:

### Standard Error Response
```typescript
{
  error: {
    code: string;      // Machine-readable code
    message: string;   // Human-readable message
    details?: object;  // Additional context
  }
}
```

### Common Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid authentication |
| `FORBIDDEN` | 403 | Authenticated but insufficient permissions |
| `NOT_FOUND` | 404 | Resource does not exist |
| `VALIDATION_ERROR` | 400 | Request body failed validation |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Unexpected server error |

---

## Cross-References for Other Analysts

- **Architecture Analyst**: Verify that endpoint groupings match module boundaries
- **Data Model Analyst**: Request/response schemas should align with database models
- **Infrastructure Analyst**: Authentication mechanism may have infrastructure dependencies (Redis for sessions, etc.)
```

---

## §2.3 Data Model Analyst

**Spawn Condition:** Spawned when ORM models, database schemas, or migrations are detected:
- Schema files: `**/schema.prisma`, `**/schema.graphql`, `**/*.sql`
- Migration directories: `**/migrations/**`, `**/db/migrate/**`, `**/alembic/**`
- ORM model files: `**/models/**/*.{ts,js,py,go,java}`, `**/entities/**/*.{ts,js,java}`
- Database config: `**/database.{yml,yaml,json}`, `**/knexfile.js`, `**/ormconfig.{ts,js,json}`

### Complete Prompt Template

```markdown
# Data Model Analyst

You are documenting the data layer of this codebase — database schemas, ORM models, migrations, and data flow. Your output will be consumed by a synthesis agent, so use structured Markdown with consistent headers.

## Your Scope

Analyze the codebase for:
1. **Database schemas** — Table/collection definitions, columns, types, constraints
2. **ORM models** — Application-level model definitions
3. **Relationships** — Foreign keys, associations, joins
4. **Migrations** — Schema evolution history
5. **Data flow** — How data moves through the application

## Input Sources

### Native Extractor Output (if available)
If the orchestrator provides Prisma schema output, TypeORM metadata, or similar, use it as PRIMARY source:
- Table definitions with exact column types
- Relationships and foreign keys
- Index definitions

Location: `{repo_root}/.code-doc-cache/schema-output.json` (if exists)

### Source Files to Analyze
- `**/schema.prisma` — Prisma schema
- `**/models/**/*.{ts,js,py,rb,java}` — ORM models
- `**/entities/**/*.{ts,js,java}` — TypeORM/JPA entities
- `**/migrations/**/*.{sql,ts,js,py,rb}` — migrations
- `**/db/migrate/**/*.rb` — Rails migrations
- `**/alembic/versions/**/*.py` — Alembic (SQLAlchemy) migrations
- `**/*.sql` — Raw SQL files
- `**/schema.graphql` — GraphQL schema (if used for data typing)
- `**/seeds/**`, `**/fixtures/**` — Seed data (reveals expected data shape)

## Output Format

Structure your output EXACTLY as follows:

## Tables/Collections

For each table/collection:
- **Name**: Table name
- **Purpose**: What data this stores (1 sentence)
- **Primary key**: Column(s) and type
- **Columns**: Name, type, constraints, description

Example:

### users
- **Purpose**: Stores user accounts and authentication data
- **Primary key**: `id` (UUID, auto-generated)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | Login email |
| `password_hash` | VARCHAR(255) | NOT NULL | Bcrypt hash |
| `name` | VARCHAR(100) | NOT NULL | Display name |
| `role` | ENUM('user','admin') | DEFAULT 'user' | Permission level |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |
| `updated_at` | TIMESTAMP | NOT NULL | Last modification |
| `deleted_at` | TIMESTAMP | NULLABLE | Soft delete marker |

**Indexes**:
- `idx_users_email` on `email` (unique)
- `idx_users_created_at` on `created_at`

### posts
- **Purpose**: Stores blog posts created by users
- **Primary key**: `id` (UUID)

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK, NOT NULL | Unique identifier |
| `user_id` | UUID | FK → users.id, NOT NULL | Author |
| `title` | VARCHAR(200) | NOT NULL | Post title |
| `content` | TEXT | NOT NULL | Post body (Markdown) |
| `status` | ENUM('draft','published') | DEFAULT 'draft' | Publication state |
| `published_at` | TIMESTAMP | NULLABLE | Publication time |

## Relationships

Document all relationships between tables:

### One-to-Many
- `users` → `posts`: One user has many posts (`posts.user_id` → `users.id`)
- `posts` → `comments`: One post has many comments (`comments.post_id` → `posts.id`)
- `users` → `comments`: One user has many comments (`comments.user_id` → `users.id`)

### Many-to-Many
- `posts` ↔ `tags`: Many-to-many via `post_tags` junction table
  - `post_tags.post_id` → `posts.id`
  - `post_tags.tag_id` → `tags.id`

### One-to-One
- `users` → `user_profiles`: Each user has one profile (`user_profiles.user_id` UNIQUE → `users.id`)

### Relationship Diagram (text representation)
```
users ─┬─< posts ─┬─< comments
       │          └─<> tags (via post_tags)
       └─ user_profiles
```

## Migrations

Document migration history and significant schema changes:

### Migration Timeline
| Version | Date | Description |
|---------|------|-------------|
| `001_initial` | 2024-01-15 | Create users, posts tables |
| `002_add_comments` | 2024-02-01 | Add comments table |
| `003_add_tags` | 2024-02-15 | Add tags and post_tags tables |
| `004_soft_delete` | 2024-03-01 | Add deleted_at to users, posts |
| `005_user_profiles` | 2024-03-15 | Add user_profiles table |

### Pending Migrations
- None (schema is up to date)

### Notable Schema Evolution
- **Soft delete added in 004**: Users and posts use `deleted_at` timestamp instead of hard delete
- **Breaking change in 003**: Added required `post_tags` for tag relationships (one-time data migration needed)

## Data Flow

Document how data moves through the application:

### Write Paths
1. **User registration**: API → UserService → UserRepository → users table
2. **Post creation**: API → PostService → PostRepository → posts table (with tags via post_tags)
3. **Comment submission**: API → CommentService → CommentRepository → comments table

### Read Paths
1. **User profile**: API → UserService → UserRepository (joins user_profiles)
2. **Post feed**: API → PostService → PostRepository (paginated, joins users for author)
3. **Post detail**: API → PostService → PostRepository (joins comments, tags)

### Caching
- User sessions: Redis (15-minute TTL)
- Post list: Redis (5-minute TTL, invalidated on new post)

### Background Jobs
- `SyncSearchIndex`: posts table → Elasticsearch (every 5 minutes)
- `CleanupSoftDeleted`: Hard-delete records where `deleted_at` > 30 days

---

## Cross-References for Other Analysts

- **API Surface Analyst**: Verify API request/response schemas match these table structures
- **Architecture Analyst**: Data flow aligns with module boundaries (Service → Repository pattern)
- **Infrastructure Analyst**: Redis and Elasticsearch dependencies need infrastructure docs
```

---

## §2.4 Component/UI Analyst

**Spawn Condition:** Spawned when frontend framework components are detected:
- React: `**/*.{jsx,tsx}` with React imports, `**/components/**`
- Vue: `**/*.vue`, `**/components/**/*.vue`
- Angular: `**/*.component.ts`, `**/app.module.ts`
- Svelte: `**/*.svelte`
- State management: `**/store/**`, `**/redux/**`, `**/vuex/**`, `**/context/**`
- Routing: `**/pages/**`, `**/routes/**`, `**/router.{ts,js}`

### Complete Prompt Template

```markdown
# Component/UI Analyst

You are documenting the frontend architecture of this codebase — component hierarchy, state management, routing, and UI patterns. Your output will be consumed by a synthesis agent, so use structured Markdown with consistent headers.

## Your Scope

Analyze the codebase for:
1. **Component hierarchy** — How components are organized and nested
2. **State management** — Global state, context, stores
3. **Routing** — Page structure and navigation
4. **Shared components** — Reusable UI building blocks
5. **Styling patterns** — CSS approach (modules, styled-components, Tailwind, etc.)

## Input Sources

### Native Extractor Output (if available)
If the orchestrator provides component tree extraction or Storybook metadata, use it as PRIMARY source.

Location: `{repo_root}/.code-doc-cache/component-tree.json` (if exists)

### Source Files to Analyze
- `**/components/**/*.{tsx,jsx,vue,svelte}` — components
- `**/pages/**/*.{tsx,jsx,vue,svelte}` — page components
- `**/app/**/*.{tsx,jsx}` — Next.js app router pages
- `**/views/**/*.{vue,tsx,jsx}` — view components
- `**/layouts/**/*.{tsx,jsx,vue,svelte}` — layout components
- `**/store/**/*.{ts,js}`, `**/redux/**`, `**/vuex/**` — state management
- `**/context/**/*.{tsx,jsx}` — React context providers
- `**/hooks/**/*.{ts,js}` — custom hooks
- `**/router.{ts,js}`, `**/routes.{ts,js}` — routing config
- `**/styles/**`, `**/*.module.css`, `**/tailwind.config.{js,ts}` — styling

## Output Format

Structure your output EXACTLY as follows:

## Component Tree

Document the component hierarchy from root to leaves. Use indentation to show nesting:

### App Structure
```
App
├── Layout
│   ├── Header
│   │   ├── Logo
│   │   ├── Navigation
│   │   └── UserMenu
│   ├── Sidebar (conditional: authenticated users)
│   │   ├── SidebarNav
│   │   └── SidebarFooter
│   └── Footer
├── Routes
│   ├── HomePage
│   │   ├── HeroSection
│   │   ├── FeatureGrid
│   │   └── CallToAction
│   ├── DashboardPage (protected)
│   │   ├── DashboardStats
│   │   ├── RecentActivity
│   │   └── QuickActions
│   ├── UserProfilePage
│   │   ├── ProfileHeader
│   │   ├── ProfileTabs
│   │   └── ProfileContent
│   └── SettingsPage (protected)
│       ├── SettingsNav
│       └── SettingsPanel
└── Modals (portal)
    ├── ConfirmDialog
    ├── LoginModal
    └── ImagePreview
```

### Component Categories
| Category | Path | Count | Description |
|----------|------|-------|-------------|
| Pages | `src/pages/` | 12 | Top-level route components |
| Layouts | `src/layouts/` | 3 | Page wrapper components |
| Features | `src/features/` | 8 | Feature-specific component groups |
| Shared | `src/components/` | 24 | Reusable UI components |
| Primitives | `src/components/ui/` | 15 | Base UI elements (Button, Input, etc.) |

## State Flow

Document state management architecture:

### Global State
**Technology**: Redux Toolkit (or Zustand/Vuex/Context — adapt as appropriate)

#### Store Structure
```
store/
├── auth/
│   ├── authSlice.ts      # user, token, isAuthenticated
│   └── authThunks.ts     # login, logout, refresh
├── posts/
│   ├── postsSlice.ts     # posts list, loading, error
│   └── postsThunks.ts    # fetchPosts, createPost
└── ui/
    └── uiSlice.ts        # sidebar open, theme, modals
```

#### Key State Shapes
```typescript
// Auth state
{
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

// Posts state
{
  items: Post[];
  selectedId: string | null;
  status: 'idle' | 'loading' | 'succeeded' | 'failed';
  error: string | null;
}
```

### Local State Patterns
- **Form state**: React Hook Form (`useForm`) for all forms
- **Server state**: TanStack Query for API data fetching
- **UI state**: `useState` for component-local UI state

### Data Flow Diagram
```
User Action
    ↓
Component (dispatch action)
    ↓
Redux Thunk (async logic)
    ↓
API Service (fetch)
    ↓
Reducer (update state)
    ↓
Selector (derive data)
    ↓
Component (re-render)
```

## Routes

Document application routes:

### Route Table
| Path | Component | Auth | Description |
|------|-----------|------|-------------|
| `/` | HomePage | public | Landing page |
| `/login` | LoginPage | guest-only | Authentication |
| `/signup` | SignupPage | guest-only | Registration |
| `/dashboard` | DashboardPage | protected | User dashboard |
| `/profile/:id` | UserProfilePage | public | User profile view |
| `/settings` | SettingsPage | protected | User settings |
| `/posts` | PostsListPage | public | All posts |
| `/posts/:id` | PostDetailPage | public | Single post |
| `/posts/new` | PostEditorPage | protected | Create post |
| `/posts/:id/edit` | PostEditorPage | protected | Edit post |

### Route Guards
- **Protected routes**: Redirect to `/login` if not authenticated
- **Guest-only routes**: Redirect to `/dashboard` if authenticated
- **Role-based**: Admin routes check `user.role === 'admin'`

### Navigation Structure
```
Header Nav: Home | Posts | [Dashboard] | [Profile ▾]
Sidebar Nav (authenticated): Dashboard | My Posts | Settings
Footer Nav: About | Contact | Privacy | Terms
```

## Shared Components

Document reusable components:

### UI Primitives (`src/components/ui/`)
| Component | Props | Description |
|-----------|-------|-------------|
| `Button` | `variant`, `size`, `disabled`, `loading` | Primary action button |
| `Input` | `type`, `error`, `label`, `placeholder` | Form input with label |
| `Select` | `options`, `value`, `onChange`, `multi` | Dropdown select |
| `Modal` | `isOpen`, `onClose`, `title`, `children` | Dialog overlay |
| `Card` | `title`, `children`, `footer` | Content container |
| `Avatar` | `src`, `name`, `size` | User avatar with fallback |
| `Badge` | `variant`, `children` | Status indicator |
| `Spinner` | `size` | Loading indicator |

### Composite Components (`src/components/`)
| Component | Description | Used In |
|-----------|-------------|---------|
| `UserCard` | User info display with avatar | Profile, Comments |
| `PostCard` | Post preview card | Feed, Dashboard |
| `Pagination` | Page navigation controls | All list pages |
| `SearchBar` | Search input with suggestions | Header, Posts |
| `EmptyState` | Placeholder for empty lists | All list pages |
| `ErrorBoundary` | Error catching wrapper | App root |

### Component Conventions
- All components use TypeScript with explicit prop interfaces
- Components are co-located with their styles (`Component.tsx` + `Component.module.css`)
- Storybook stories exist for all UI primitives (`Component.stories.tsx`)

---

## Cross-References for Other Analysts

- **API Surface Analyst**: Verify API endpoints match the data fetching in components
- **Architecture Analyst**: Component structure should align with module boundaries
- **Infrastructure Analyst**: Build and bundle configuration affects component organization
```

---

## §2.5 Infrastructure Analyst

**Spawn Condition:** Spawned when CI/CD, Docker, or deployment configurations are detected:
- Docker: `**/Dockerfile*`, `**/docker-compose*.{yml,yaml}`, `**/.dockerignore`
- CI/CD: `.github/workflows/**`, `.gitlab-ci.yml`, `Jenkinsfile`, `.circleci/**`, `.travis.yml`, `azure-pipelines.yml`
- Deployment: `**/k8s/**`, `**/kubernetes/**`, `**/helm/**`, `**/terraform/**`, `**/pulumi/**`
- Environment: `**/.env.example`, `**/config/**/*.{yml,yaml,json}`, `**/serverless.{yml,yaml}`

### Complete Prompt Template

```markdown
# Infrastructure Analyst

You are documenting the infrastructure and deployment configuration of this codebase — CI/CD pipelines, Docker setup, deployment targets, and environment management. Your output will be consumed by a synthesis agent, so use structured Markdown with consistent headers.

## Your Scope

Analyze the codebase for:
1. **CI/CD pipelines** — Build, test, deploy automation
2. **Containerization** — Docker configuration and multi-stage builds
3. **Deployment** — Target environments and deployment mechanisms
4. **Environment management** — Configuration, secrets, feature flags
5. **Infrastructure as Code** — Terraform, Pulumi, CloudFormation, etc.

## Source Files to Analyze
- `.github/workflows/**/*.{yml,yaml}` — GitHub Actions
- `.gitlab-ci.yml` — GitLab CI
- `Jenkinsfile` — Jenkins pipeline
- `.circleci/config.yml` — CircleCI
- `.travis.yml` — Travis CI
- `azure-pipelines.yml` — Azure DevOps
- `Dockerfile*`, `docker-compose*.{yml,yaml}` — Docker configs
- `**/k8s/**/*.{yml,yaml}`, `**/kubernetes/**` — Kubernetes manifests
- `**/helm/**` — Helm charts
- `**/terraform/**/*.tf` — Terraform configs
- `**/pulumi/**/*.{ts,py,go}` — Pulumi programs
- `serverless.{yml,yaml}` — Serverless Framework
- `vercel.json`, `netlify.toml`, `fly.toml` — Platform configs
- `.env.example`, `**/config/**` — Environment configs
- `Makefile`, `justfile`, `Taskfile.yml` — Task runners

## Output Format

Structure your output EXACTLY as follows:

## Build Pipeline

Document the CI/CD pipeline stages:

### Pipeline Overview
**Platform**: GitHub Actions (or GitLab CI, Jenkins, etc.)
**Trigger**: Push to `main`, `develop`; Pull requests to `main`

### Pipeline Stages
```
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│  Lint   │ →  │  Test   │ →  │  Build  │ →  │ Deploy  │
└─────────┘    └─────────┘    └─────────┘    └─────────┘
     │              │              │              │
   ESLint       Jest/Vitest    Docker build   Conditional
   Prettier     Coverage       Push to ECR    per branch
   TypeCheck    Integration
```

### Stage Details

#### Lint (`ci.yml`)
- **Runs on**: All pushes and PRs
- **Steps**: 
  1. Install dependencies (`pnpm install`)
  2. ESLint (`pnpm lint`)
  3. Prettier (`pnpm format:check`)
  4. TypeScript (`pnpm typecheck`)
- **Timeout**: 10 minutes

#### Test (`ci.yml`)
- **Runs on**: All pushes and PRs
- **Steps**:
  1. Install dependencies
  2. Unit tests (`pnpm test`)
  3. Integration tests (`pnpm test:integration`)
  4. Coverage upload to Codecov
- **Services**: PostgreSQL (via docker-compose)
- **Timeout**: 20 minutes

#### Build (`build.yml`)
- **Runs on**: Push to `main`, `develop`
- **Steps**:
  1. Build Docker image
  2. Tag with commit SHA and branch
  3. Push to container registry
- **Outputs**: Docker image in ECR

#### Deploy (`deploy.yml`)
- **Runs on**: Push to `main` (production), `develop` (staging)
- **Strategy**: Rolling update
- **Steps**:
  1. Pull latest image
  2. Update Kubernetes deployment
  3. Wait for rollout
  4. Smoke test

### Workflow Files
| File | Trigger | Purpose |
|------|---------|---------|
| `.github/workflows/ci.yml` | push, PR | Lint + Test |
| `.github/workflows/build.yml` | push to main/develop | Docker build |
| `.github/workflows/deploy.yml` | push to main/develop | Deploy to K8s |
| `.github/workflows/release.yml` | tag v* | Create GitHub release |

## Deployment

Document deployment configuration:

### Docker Configuration

#### Dockerfile
```dockerfile
# Multi-stage build
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

**Key points**:
- Multi-stage build (smaller final image)
- Alpine base (security + size)
- Production dependencies only
- Non-root user (security)

#### docker-compose.yml
- **Services**: app, postgres, redis
- **Networks**: internal (app ↔ postgres, redis)
- **Volumes**: postgres-data (persistent)
- **Use case**: Local development

### Kubernetes Deployment

#### Resources
| Resource | File | Description |
|----------|------|-------------|
| Deployment | `k8s/deployment.yaml` | App pods (3 replicas) |
| Service | `k8s/service.yaml` | ClusterIP service |
| Ingress | `k8s/ingress.yaml` | External access via nginx |
| ConfigMap | `k8s/configmap.yaml` | Non-secret config |
| Secret | `k8s/secret.yaml` | Sensitive config (sealed) |
| HPA | `k8s/hpa.yaml` | Auto-scaling (2-10 pods) |

#### Resource Limits
```yaml
resources:
  requests:
    memory: "256Mi"
    cpu: "100m"
  limits:
    memory: "512Mi"
    cpu: "500m"
```

## Environments

Document environment configuration:

### Environment Inventory
| Environment | URL | Branch | Purpose |
|-------------|-----|--------|---------|
| Development | localhost:3000 | any | Local development |
| Staging | staging.example.com | develop | Pre-production testing |
| Production | app.example.com | main | Live environment |

### Configuration Management

#### Environment Variables
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `NODE_ENV` | yes | — | Environment mode |
| `DATABASE_URL` | yes | — | PostgreSQL connection string |
| `REDIS_URL` | yes | — | Redis connection string |
| `JWT_SECRET` | yes | — | JWT signing secret |
| `PORT` | no | 3000 | HTTP server port |
| `LOG_LEVEL` | no | info | Logging verbosity |

#### Configuration Files
- `.env.example` — Template with all variables
- `.env.local` — Local overrides (gitignored)
- `config/default.json` — Default values
- `config/production.json` — Production overrides

## Secrets Management

Document how secrets are handled:

### Secret Storage
- **Development**: `.env.local` file (gitignored)
- **CI/CD**: GitHub Actions secrets
- **Kubernetes**: Sealed Secrets (encrypted in repo)
- **Production**: AWS Secrets Manager

### Secret Rotation
- `JWT_SECRET`: Rotated quarterly, supports key rollover
- `DATABASE_URL`: Managed by AWS RDS, auto-rotated
- API keys: Manual rotation, tracked in 1Password

### Secret Access Pattern
```
GitHub Actions → AWS Secrets Manager → Kubernetes Secret → Pod env var
```

### Security Notes
- No secrets in Docker images
- Secrets mounted as env vars, not files
- Audit log for secret access in AWS CloudTrail

---

## Cross-References for Other Analysts

- **Architecture Analyst**: Entry points should match Docker CMD and K8s containers
- **API Surface Analyst**: Ingress routes should align with API endpoints
- **Data Model Analyst**: Database connection requires `DATABASE_URL` secret
```

---

## Summary Table

| Analyst | Spawn Condition | Key Output Sections | Cross-References |
|---------|-----------------|---------------------|------------------|
| Architecture | Always (medium+) | Modules, Dependencies, Entry Points, Patterns, Key Abstractions | API, Data, Infra |
| API Surface | Routes/endpoints detected | Endpoints, Schemas, Auth, Error Codes | Arch, Data, Infra |
| Data Model | ORM/schema/migrations detected | Tables, Relationships, Migrations, Data Flow | API, Arch, Infra |
| Component/UI | Frontend framework detected | Component Tree, State Flow, Routes, Shared Components | API, Arch, Infra |
| Infrastructure | CI/CD/Docker detected | Build Pipeline, Deployment, Environments, Secrets | Arch, API, Data |


# §3 — Language-Specific Analyst Variants

Language-specific extraction patterns that supplement the concern-based analysts from §2. These variants provide deeper extraction when the scout detects a specific primary language.

> **Usage**: After concern-based analysts complete, spawn language-variant analysts for the detected primary language(s). Language variants enhance extraction depth—they don't replace concern-based analysis.

---

## §3.1 TypeScript/JavaScript

### 3.1.1 Module System & Project Structure

**Detection Heuristics**:
| Signal | Detection | Implication |
|--------|-----------|-------------|
| `package.json` with `"type": "module"` | ESM primary | Use `import/export` analysis |
| `.mjs` files present | ESM modules | Native ES modules |
| `.cjs` files present | CommonJS modules | `require()`/`module.exports` |
| `tsconfig.json` present | TypeScript project | Parse for paths, module resolution |
| `jsconfig.json` present | JS with editor support | Check paths, baseUrl |

**File Patterns (Globs)**:
```
# Source files
**/*.ts, **/*.tsx, **/*.js, **/*.jsx, **/*.mjs, **/*.cjs

# Config files
tsconfig.json, tsconfig.*.json, jsconfig.json
package.json, package-lock.json, yarn.lock, pnpm-lock.yaml, bun.lockb

# Build configs
webpack.config.{js,ts}, vite.config.{js,ts,mjs}, rollup.config.{js,ts,mjs}
esbuild.config.{js,mjs}, turbo.json, nx.json

# Barrel exports
**/index.ts, **/index.js, **/mod.ts
```

**Module Boundary Detection**:
```typescript
// Barrel exports (re-export aggregation)
// Look for: index.ts with only export statements
export * from './user';
export { AuthService } from './auth';
export type { UserDTO } from './types';

// Path aliases (from tsconfig.json)
{
  "compilerOptions": {
    "paths": {
      "@/*": ["./src/*"],
      "@components/*": ["./src/components/*"],
      "@lib/*": ["./src/lib/*"]
    }
  }
}
```

**Extract**:
- `exports` field in package.json (subpath exports)
- `main`, `module`, `types` entry points
- Workspace definitions (`workspaces` in package.json, `pnpm-workspace.yaml`)
- Path alias mappings from tsconfig `paths`

### 3.1.2 Framework Patterns

#### React
**Detection**: `react` in dependencies, `.tsx`/`.jsx` files, `'use client'`/`'use server'` directives

**Key Constructs**:
```typescript
// Hooks (custom hooks start with 'use')
function useAuth(): AuthContext { ... }
function useDebounce<T>(value: T, delay: number): T { ... }

// Components (PascalCase functions returning JSX)
function UserProfile({ userId }: Props): JSX.Element { ... }
const MemoizedList = React.memo(ListComponent);

// Context providers
const AuthContext = createContext<AuthContextType | null>(null);
export const AuthProvider: FC<PropsWithChildren> = ({ children }) => { ... };

// Server Components (Next.js App Router)
// Look for: 'use client' directive absence + async component
async function ServerComponent() {
  const data = await fetchData(); // Direct async in component
  return <div>{data}</div>;
}
```

**File Patterns**:
```
# Components
src/components/**/*.tsx, app/**/page.tsx, app/**/layout.tsx
pages/**/*.tsx (Next.js Pages Router)

# Hooks
src/hooks/use*.ts, **/use*.ts

# Context
src/context/*.tsx, src/providers/*.tsx
```

#### Vue
**Detection**: `vue` in dependencies, `.vue` files, `vite.config.ts` with `@vitejs/plugin-vue`

**Key Constructs**:
```typescript
// Composables (Vue 3 Composition API)
// Named exports starting with 'use'
export function useCounter() {
  const count = ref(0);
  const increment = () => count.value++;
  return { count, increment };
}

// defineComponent for type inference
export default defineComponent({
  props: { ... },
  setup(props, { emit }) { ... }
});

// Script setup (Vue 3.2+)
<script setup lang="ts">
const props = defineProps<{ msg: string }>();
const emit = defineEmits<{ (e: 'update', value: string): void }>();
</script>
```

**File Patterns**:
```
**/*.vue
src/composables/use*.ts
src/stores/*.ts (Pinia stores)
```

#### Angular
**Detection**: `@angular/core` in dependencies, `angular.json` config

**Key Constructs**:
```typescript
// Services (injectable singletons)
@Injectable({ providedIn: 'root' })
export class AuthService { ... }

// Components
@Component({
  selector: 'app-user-profile',
  templateUrl: './user-profile.component.html',
})
export class UserProfileComponent implements OnInit { ... }

// Pipes (data transformation)
@Pipe({ name: 'formatDate' })
export class FormatDatePipe implements PipeTransform { ... }

// Modules
@NgModule({
  declarations: [UserProfileComponent],
  imports: [CommonModule],
  exports: [UserProfileComponent],
})
export class UserModule { }
```

**File Patterns**:
```
**/*.component.ts, **/*.service.ts, **/*.pipe.ts
**/*.module.ts, **/*.directive.ts, **/*.guard.ts
angular.json, nx.json (Nx workspace)
```

#### Node.js/Express/Fastify
**Detection**: `express`/`fastify`/`@nestjs/core` in dependencies

**Key Constructs**:
```typescript
// Express middleware chain
app.use(cors());
app.use('/api', authMiddleware, apiRouter);

// Route handlers
router.get('/users/:id', validateParams, async (req, res) => { ... });

// NestJS decorators
@Controller('users')
export class UsersController {
  @Get(':id')
  @UseGuards(AuthGuard)
  findOne(@Param('id') id: string): Promise<User> { ... }
}
```

### 3.1.3 Type System Patterns

**Extract These Constructs**:

```typescript
// Discriminated unions (tagged unions)
type Result<T, E> = 
  | { success: true; data: T }
  | { success: false; error: E };

// Branded/nominal types
type UserId = string & { readonly brand: unique symbol };
type Email = string & { __brand: 'Email' };

// Utility type usage
type UserDTO = Pick<User, 'id' | 'name'>;
type PartialUser = Partial<User>;
type RequiredConfig = Required<Config>;

// Generic constraints
function process<T extends { id: string }>(items: T[]): Map<string, T>;

// Conditional types
type ApiResponse<T> = T extends Error ? ErrorResponse : SuccessResponse<T>;

// Mapped types
type Readonly<T> = { readonly [K in keyof T]: T[K] };

// Template literal types
type EventName = `on${Capitalize<string>}`;
type Routes = `/api/${string}`;

// Infer keyword
type ReturnTypeOf<T> = T extends (...args: any[]) => infer R ? R : never;

// Zod/io-ts schemas (runtime validation)
const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
});
type User = z.infer<typeof UserSchema>;
```

**Type Declaration Files**:
```
**/*.d.ts
types/**/*.ts
@types/**/*.d.ts
```

### 3.1.4 Build & Dependency Configuration

**Package Managers**:
| File | Manager | Workspace Pattern |
|------|---------|-------------------|
| `package-lock.json` | npm | `workspaces` in package.json |
| `yarn.lock` | Yarn | `workspaces` in package.json |
| `pnpm-lock.yaml` | pnpm | `pnpm-workspace.yaml` |
| `bun.lockb` | Bun | `workspaces` in package.json |

**Monorepo Tools**:
| File | Tool | Structure |
|------|------|-----------|
| `turbo.json` | Turborepo | `packages/*`, `apps/*` |
| `nx.json` | Nx | `apps/*`, `libs/*` |
| `lerna.json` | Lerna | `packages/*` |
| `rush.json` | Rush | `apps/*`, `libraries/*` |

**Build Config Extraction**:
```javascript
// vite.config.ts - extract aliases, plugins, build targets
export default defineConfig({
  resolve: {
    alias: { '@': path.resolve(__dirname, 'src') }
  },
  build: {
    target: 'es2020',
    lib: { entry: 'src/index.ts', formats: ['es', 'cjs'] }
  }
});

// tsconfig.json - extract module resolution, strict settings
{
  "compilerOptions": {
    "strict": true,
    "moduleResolution": "bundler",
    "target": "ES2022"
  }
}
```

---

## §3.2 Python

### 3.2.1 Package Structure

**Detection Heuristics**:
| Signal | Detection | Implication |
|--------|-----------|-------------|
| `pyproject.toml` | Modern packaging | Check `[build-system]`, `[project]` |
| `setup.py` + `setup.cfg` | Legacy packaging | Parse setup() call |
| `src/` layout | src-layout | Packages under `src/` |
| `__init__.py` hierarchy | Flat layout | Direct package directories |
| `py.typed` marker | Typed package | Full type hint coverage expected |

**File Patterns (Globs)**:
```
# Source files
**/*.py, **/*.pyi (stub files)

# Config files
pyproject.toml, setup.py, setup.cfg, MANIFEST.in
requirements*.txt, constraints.txt
Pipfile, Pipfile.lock, poetry.lock, uv.lock

# Package markers
**/__init__.py, **/py.typed
```

**Project Layouts**:
```
# src-layout (recommended)
project/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       └── module.py
├── tests/
└── pyproject.toml

# flat-layout (legacy)
project/
├── mypackage/
│   ├── __init__.py
│   └── module.py
├── tests/
└── setup.py
```

**Extract from `pyproject.toml`**:
```toml
[project]
name = "mypackage"
dependencies = ["requests>=2.28", "pydantic>=2.0"]

[project.optional-dependencies]
dev = ["pytest", "mypy", "ruff"]

[project.scripts]
mycli = "mypackage.cli:main"

[project.entry-points."mypackage.plugins"]
auth = "mypackage.plugins.auth:AuthPlugin"
```

### 3.2.2 Framework Patterns

#### Flask
**Detection**: `flask` in dependencies, `@app.route` decorators

**Key Constructs**:
```python
# Route decorators
@app.route('/users/<int:user_id>', methods=['GET', 'POST'])
def get_user(user_id: int) -> Response: ...

# Blueprints (modular routes)
users_bp = Blueprint('users', __name__, url_prefix='/api/users')

@users_bp.route('/')
def list_users(): ...

# Application factory
def create_app(config: Config) -> Flask:
    app = Flask(__name__)
    app.register_blueprint(users_bp)
    return app

# Extensions
db = SQLAlchemy()
migrate = Migrate()
```

**File Patterns**:
```
app.py, application.py, wsgi.py
**/routes.py, **/views.py, **/blueprints/*.py
```

#### Django
**Detection**: `django` in dependencies, `settings.py`, `urls.py`

**Key Constructs**:
```python
# URL patterns
urlpatterns = [
    path('users/', include('users.urls')),
    path('api/', include('api.urls')),
]

# Class-based views
class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

# Models
class User(AbstractUser):
    email = models.EmailField(unique=True)
    
    class Meta:
        ordering = ['-created_at']

# Signals
@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs): ...
```

**File Patterns**:
```
**/settings.py, **/settings/*.py
**/urls.py, **/views.py, **/models.py
**/serializers.py, **/admin.py
**/migrations/*.py
manage.py, wsgi.py, asgi.py
```

#### FastAPI
**Detection**: `fastapi` in dependencies, `@app.get`/`@router.post` decorators

**Key Constructs**:
```python
# Path operations with type hints
@app.get('/users/{user_id}', response_model=UserResponse)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> UserResponse: ...

# APIRouter for modular routes
router = APIRouter(prefix='/api/v1', tags=['users'])

# Dependency injection
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic models for request/response
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    model_config = ConfigDict(str_strip_whitespace=True)
```

**File Patterns**:
```
main.py, app.py
**/routers/*.py, **/api/*.py, **/endpoints/*.py
**/dependencies.py, **/deps.py
**/schemas.py, **/models.py
```

#### Click/Typer CLI
**Detection**: `click`/`typer` in dependencies, `@click.command` decorators

**Key Constructs**:
```python
# Click
@click.group()
def cli(): ...

@cli.command()
@click.option('--name', '-n', required=True)
@click.argument('path', type=click.Path(exists=True))
def process(name: str, path: str): ...

# Typer
app = typer.Typer()

@app.command()
def process(
    name: Annotated[str, typer.Option('--name', '-n')],
    path: Annotated[Path, typer.Argument()],
): ...
```

### 3.2.3 Type System Patterns

**Extract These Constructs**:

```python
# Type hints with modern syntax (3.10+)
def process(items: list[str]) -> dict[str, int]: ...

# Union types
def fetch(id: int | str) -> User | None: ...

# TypedDict for structured dicts
class UserDict(TypedDict):
    id: int
    name: str
    email: NotRequired[str]

# Protocols (structural typing)
class Comparable(Protocol):
    def __lt__(self, other: Self) -> bool: ...

# Generic classes
class Repository(Generic[T]):
    def get(self, id: int) -> T | None: ...
    def save(self, entity: T) -> T: ...

# Dataclasses
@dataclass(frozen=True, slots=True)
class User:
    id: int
    name: str
    created_at: datetime = field(default_factory=datetime.now)

# Pydantic models (runtime validation)
class User(BaseModel):
    id: int
    email: EmailStr
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str: ...

# NewType for type aliases
UserId = NewType('UserId', int)

# Literal types
Mode = Literal['read', 'write', 'append']

# ParamSpec for decorator typing
P = ParamSpec('P')
R = TypeVar('R')
def logged(func: Callable[P, R]) -> Callable[P, R]: ...
```

**Type Stub Files**:
```
**/*.pyi
stubs/**/*.pyi
typings/**/*.pyi
```

### 3.2.4 Testing Patterns

**pytest Fixtures & Configuration**:
```python
# conftest.py - shared fixtures
@pytest.fixture(scope='session')
def db_engine() -> Generator[Engine, None, None]:
    engine = create_engine('sqlite:///:memory:')
    yield engine
    engine.dispose()

@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()

# Parametrized tests
@pytest.mark.parametrize('input,expected', [
    ('hello', 'HELLO'),
    ('world', 'WORLD'),
])
def test_upper(input: str, expected: str): ...

# Markers
@pytest.mark.slow
@pytest.mark.integration
def test_full_workflow(): ...
```

**File Patterns**:
```
tests/**/test_*.py, tests/**/*_test.py
**/conftest.py
pytest.ini, pyproject.toml [tool.pytest]
```

### 3.2.5 Dependency Management

| Tool | Lock File | Config Location |
|------|-----------|-----------------|
| pip | `requirements.txt` | `requirements*.txt` |
| Poetry | `poetry.lock` | `pyproject.toml [tool.poetry]` |
| Pipenv | `Pipfile.lock` | `Pipfile` |
| uv | `uv.lock` | `pyproject.toml` |
| PDM | `pdm.lock` | `pyproject.toml [tool.pdm]` |

**Virtual Environment Detection**:
```
.venv/, venv/, env/, .env/
.python-version (pyenv)
.tool-versions (asdf)
```

---

## §3.3 Go

### 3.3.1 Package & Module Structure

**Detection Heuristics**:
| Signal | Detection | Implication |
|--------|-----------|-------------|
| `go.mod` | Go modules | Parse module path, dependencies |
| `go.work` | Multi-module workspace | Parse workspace members |
| `internal/` directory | Private packages | Not importable externally |
| `cmd/` directory | Binary entry points | Each subdir = separate binary |
| `pkg/` directory | Public library code | Importable by external projects |

**File Patterns (Globs)**:
```
# Source files
**/*.go

# Config files
go.mod, go.sum, go.work, go.work.sum

# Build/generate
**/*_generated.go, **/*_gen.go
**/mock_*.go, **/*_mock.go
```

**Standard Project Layout**:
```
project/
├── cmd/
│   ├── server/
│   │   └── main.go      # Binary: go build ./cmd/server
│   └── cli/
│       └── main.go      # Binary: go build ./cmd/cli
├── internal/            # Private packages
│   ├── auth/
│   └── database/
├── pkg/                 # Public library packages
│   └── api/
├── api/                 # OpenAPI specs, protobufs
├── go.mod
└── go.sum
```

**Module Boundaries**:
```go
// go.mod - module declaration
module github.com/org/project

go 1.22

require (
    github.com/gin-gonic/gin v1.9.1
    google.golang.org/grpc v1.62.0
)

// go.work - workspace for multi-module
go 1.22

use (
    ./services/auth
    ./services/api
    ./pkg/shared
)
```

### 3.3.2 Framework Patterns

#### Gin/Echo/Chi (HTTP Routers)
**Detection**: Import paths `github.com/gin-gonic/gin`, `github.com/labstack/echo`, `github.com/go-chi/chi`

**Key Constructs**:
```go
// Gin route groups
func SetupRoutes(r *gin.Engine) {
    api := r.Group("/api/v1")
    api.Use(AuthMiddleware())
    {
        api.GET("/users/:id", GetUser)
        api.POST("/users", CreateUser)
    }
}

// Chi middleware chain
r := chi.NewRouter()
r.Use(middleware.Logger)
r.Use(middleware.Recoverer)
r.Route("/api", func(r chi.Router) {
    r.Mount("/users", usersRouter)
})

// Echo groups
e := echo.New()
api := e.Group("/api", middleware.JWT())
api.GET("/users/:id", getUser)
```

#### gRPC
**Detection**: Import `google.golang.org/grpc`, `.proto` files, `*_grpc.pb.go`

**Key Constructs**:
```go
// Server implementation
type userServer struct {
    pb.UnimplementedUserServiceServer
}

func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    // Implementation
}

// Client usage
conn, _ := grpc.Dial(address, grpc.WithTransportCredentials(creds))
client := pb.NewUserServiceClient(conn)
```

**File Patterns**:
```
**/*.proto
**/*_grpc.pb.go, **/*.pb.go
```

#### Database (GORM/sqlx/pgx)
**Detection**: Import paths `gorm.io/gorm`, `github.com/jmoiron/sqlx`, `github.com/jackc/pgx`

**Key Constructs**:
```go
// GORM model
type User struct {
    gorm.Model
    Name  string `gorm:"size:255;not null"`
    Email string `gorm:"uniqueIndex"`
    Posts []Post `gorm:"foreignKey:UserID"`
}

// Repository pattern
type UserRepository interface {
    FindByID(ctx context.Context, id int64) (*User, error)
    Create(ctx context.Context, user *User) error
}
```

### 3.3.3 Interface & Error Patterns

**Interface Patterns (Implicit Implementation)**:
```go
// Small, focused interfaces (Go idiom)
type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

// Interface composition
type ReadWriter interface {
    Reader
    Writer
}

// Accept interfaces, return structs
func ProcessData(r Reader) (*Result, error) { ... }
```

**Error Handling Idioms**:
```go
// Sentinel errors
var (
    ErrNotFound     = errors.New("not found")
    ErrUnauthorized = errors.New("unauthorized")
)

// Custom error types
type ValidationError struct {
    Field   string
    Message string
}

func (e *ValidationError) Error() string {
    return fmt.Sprintf("%s: %s", e.Field, e.Message)
}

// Error wrapping (Go 1.13+)
if err != nil {
    return fmt.Errorf("failed to fetch user %d: %w", id, err)
}

// Error checking
if errors.Is(err, ErrNotFound) { ... }
if errors.As(err, &validationErr) { ... }
```

### 3.3.4 Concurrency Patterns

**Extract These Constructs**:
```go
// Context propagation
func ProcessRequest(ctx context.Context, req *Request) error {
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()
    
    select {
    case result := <-process(ctx, req):
        return handleResult(result)
    case <-ctx.Done():
        return ctx.Err()
    }
}

// Worker pool pattern
func worker(jobs <-chan Job, results chan<- Result) {
    for job := range jobs {
        results <- process(job)
    }
}

// errgroup for parallel operations
g, ctx := errgroup.WithContext(ctx)
for _, item := range items {
    item := item // capture
    g.Go(func() error {
        return process(ctx, item)
    })
}
if err := g.Wait(); err != nil { ... }
```

### 3.3.5 Build & Generate

**Build Tags**:
```go
//go:build linux && amd64
// +build linux,amd64

//go:build integration
// +build integration
```

**Generate Directives**:
```go
//go:generate mockgen -source=repository.go -destination=mock_repository.go
//go:generate stringer -type=Status
//go:generate protoc --go_out=. --go-grpc_out=. api.proto
```

**File Patterns**:
```
**/generate.go (often holds //go:generate directives)
Makefile, Taskfile.yml (build automation)
```

---

## §3.4 Java

### 3.4.1 Package & Project Structure

**Detection Heuristics**:
| Signal | Detection | Implication |
|--------|-----------|-------------|
| `pom.xml` | Maven project | Parse dependencies, modules |
| `build.gradle`/`build.gradle.kts` | Gradle project | Parse dependencies, plugins |
| `src/main/java` | Maven/Gradle layout | Standard source structure |
| `settings.gradle` | Multi-module Gradle | Parse included modules |
| `@SpringBootApplication` | Spring Boot | Full Spring context |

**File Patterns (Globs)**:
```
# Source files
**/*.java

# Config files
pom.xml, build.gradle, build.gradle.kts
settings.gradle, settings.gradle.kts
gradle.properties, gradle-wrapper.properties

# Spring config
**/application.yml, **/application.properties
**/application-*.yml, **/application-*.properties
**/bootstrap.yml

# Resources
src/main/resources/**
src/test/resources/**
```

**Project Layouts**:
```
# Maven/Gradle standard
project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/company/project/
│   │   └── resources/
│   └── test/
│       ├── java/
│       └── resources/
├── pom.xml (Maven) OR build.gradle (Gradle)
└── README.md

# Multi-module Maven
project/
├── parent/
│   └── pom.xml (parent POM)
├── module-api/
│   ├── src/main/java/
│   └── pom.xml
├── module-service/
│   ├── src/main/java/
│   └── pom.xml
└── pom.xml (aggregator)
```

**Package Hierarchy Convention**:
```
com.company.project
├── controller/      # REST controllers
├── service/         # Business logic
├── repository/      # Data access
├── model/           # Domain entities
├── dto/             # Data transfer objects
├── config/          # Configuration classes
├── exception/       # Custom exceptions
└── util/            # Utilities
```

### 3.4.2 Framework Patterns

#### Spring Boot
**Detection**: `spring-boot-starter` dependencies, `@SpringBootApplication`

**Key Constructs**:
```java
// Application entry
@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}

// REST Controller
@RestController
@RequestMapping("/api/v1/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;
    
    @GetMapping("/{id}")
    public ResponseEntity<UserDTO> getUser(@PathVariable Long id) {
        return ResponseEntity.ok(userService.findById(id));
    }
    
    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public UserDTO createUser(@Valid @RequestBody CreateUserRequest request) {
        return userService.create(request);
    }
}

// Service layer
@Service
@Transactional(readOnly = true)
public class UserServiceImpl implements UserService {
    private final UserRepository userRepository;
    
    @Transactional
    public UserDTO create(CreateUserRequest request) { ... }
}

// Repository
@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByEmail(String email);
    
    @Query("SELECT u FROM User u WHERE u.status = :status")
    List<User> findByStatus(@Param("status") UserStatus status);
}
```

**Spring Annotations to Extract**:
| Annotation | Layer | Purpose |
|------------|-------|---------|
| `@Controller`, `@RestController` | Web | HTTP endpoints |
| `@Service` | Business | Service beans |
| `@Repository` | Data | Data access beans |
| `@Component` | General | Generic beans |
| `@Configuration` | Config | Configuration classes |
| `@Bean` | Config | Bean definitions |
| `@Autowired`, `@RequiredArgsConstructor` | DI | Dependency injection |
| `@Transactional` | Data | Transaction management |
| `@Scheduled`, `@Async` | Async | Async operations |
| `@EventListener` | Events | Event handling |

#### JPA/Hibernate
**Detection**: `javax.persistence`/`jakarta.persistence` imports, `@Entity`

**Key Constructs**:
```java
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(nullable = false, unique = true)
    private String email;
    
    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL)
    private List<Order> orders;
    
    @ManyToMany
    @JoinTable(
        name = "user_roles",
        joinColumns = @JoinColumn(name = "user_id"),
        inverseJoinColumns = @JoinColumn(name = "role_id")
    )
    private Set<Role> roles;
}
```

### 3.4.3 Design Patterns

**Extract These Patterns**:

```java
// Builder pattern
@Builder
public class UserDTO {
    private Long id;
    private String name;
    private String email;
}
// Usage: UserDTO.builder().id(1L).name("John").build();

// Factory pattern
public interface PaymentProcessorFactory {
    PaymentProcessor create(PaymentMethod method);
}

@Component
public class PaymentProcessorFactoryImpl implements PaymentProcessorFactory {
    private final Map<PaymentMethod, PaymentProcessor> processors;
    
    public PaymentProcessor create(PaymentMethod method) {
        return processors.get(method);
    }
}

// Repository pattern (Spring Data)
public interface UserRepository extends JpaRepository<User, Long> {
    // Spring generates implementation
}

// DTO/Mapper pattern
@Mapper(componentModel = "spring")
public interface UserMapper {
    UserDTO toDto(User entity);
    User toEntity(CreateUserRequest request);
}
```

### 3.4.4 Type System Patterns

**Extract These Constructs**:
```java
// Generics with bounds
public interface Repository<T, ID extends Serializable> {
    Optional<T> findById(ID id);
    T save(T entity);
}

// Enum with behavior
public enum OrderStatus {
    PENDING {
        @Override
        public boolean canTransitionTo(OrderStatus next) {
            return next == CONFIRMED || next == CANCELLED;
        }
    },
    CONFIRMED { ... },
    CANCELLED { ... };
    
    public abstract boolean canTransitionTo(OrderStatus next);
}

// Records (Java 16+)
public record UserDTO(Long id, String name, String email) {}

// Sealed classes (Java 17+)
public sealed interface Shape permits Circle, Rectangle, Triangle {
    double area();
}
```

### 3.4.5 Build & Dependency

**Maven (`pom.xml`)**:
```xml
<project>
    <groupId>com.company</groupId>
    <artifactId>project</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>
    
    <modules>
        <module>module-api</module>
        <module>module-service</module>
    </modules>
    
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
        </dependency>
    </dependencies>
</project>
```

**Gradle (`build.gradle.kts`)**:
```kotlin
plugins {
    id("org.springframework.boot") version "3.2.0"
    id("io.spring.dependency-management") version "1.1.4"
    kotlin("jvm") version "1.9.21"
}

dependencies {
    implementation("org.springframework.boot:spring-boot-starter-web")
    testImplementation("org.springframework.boot:spring-boot-starter-test")
}
```

### 3.4.6 Testing Patterns

**JUnit 5 + Mockito**:
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository userRepository;
    
    @InjectMocks
    private UserServiceImpl userService;
    
    @Test
    void shouldReturnUser_whenUserExists() {
        // Given
        when(userRepository.findById(1L)).thenReturn(Optional.of(user));
        
        // When
        UserDTO result = userService.findById(1L);
        
        // Then
        assertThat(result.getId()).isEqualTo(1L);
        verify(userRepository).findById(1L);
    }
}

// Spring Boot test slices
@WebMvcTest(UserController.class)
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @MockBean
    private UserService userService;
    
    @Test
    void shouldReturnUser() throws Exception {
        mockMvc.perform(get("/api/v1/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(1));
    }
}

@DataJpaTest
class UserRepositoryTest {
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private TestEntityManager entityManager;
}
```

**File Patterns**:
```
src/test/java/**/*Test.java
src/test/java/**/*Tests.java
src/test/java/**/*IT.java (integration tests)
```

---

## §3.5 Rust

### 3.5.1 Crate & Module Structure

**Detection Heuristics**:
| Signal | Detection | Implication |
|--------|-----------|-------------|
| `Cargo.toml` | Rust project | Parse crate metadata, dependencies |
| `Cargo.lock` | Dependencies locked | Reproducible builds |
| `src/lib.rs` | Library crate | Public API |
| `src/main.rs` | Binary crate | Executable entry |
| `src/bin/*.rs` | Multiple binaries | Additional executables |

**File Patterns (Globs)**:
```
# Source files
**/*.rs

# Config files
Cargo.toml, Cargo.lock
rust-toolchain.toml, .cargo/config.toml

# Build artifacts (ignore)
target/
```

**Module Organization**:
```rust
// mod.rs style (older)
src/
├── lib.rs
├── models/
│   ├── mod.rs      // pub mod user;
│   └── user.rs
└── services/
    ├── mod.rs
    └── auth.rs

// Inline mod style (newer, Rust 2018+)
src/
├── lib.rs
├── models.rs       // Or models/mod.rs for submodules
└── services.rs

// lib.rs
pub mod models;
pub mod services;

// Re-exports in lib.rs
pub use models::User;
pub use services::AuthService;
```

**Workspace Structure**:
```toml
# Cargo.toml (workspace root)
[workspace]
members = [
    "crates/core",
    "crates/api",
    "crates/cli",
]

[workspace.dependencies]
tokio = { version = "1.0", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
```

### 3.5.2 Type System Patterns

**Extract These Constructs**:
```rust
// Trait definitions and implementations
trait Repository<T> {
    fn find_by_id(&self, id: i64) -> Option<T>;
    fn save(&self, entity: &T) -> Result<(), Error>;
}

impl Repository<User> for PostgresUserRepo {
    fn find_by_id(&self, id: i64) -> Option<User> { ... }
    fn save(&self, entity: &User) -> Result<(), Error> { ... }
}

// Derive macros
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct User {
    pub id: i64,
    pub name: String,
}

// Error types (thiserror)
#[derive(Debug, thiserror::Error)]
pub enum AppError {
    #[error("User not found: {0}")]
    NotFound(i64),
    #[error("Database error: {0}")]
    Database(#[from] sqlx::Error),
}

// Type aliases
type Result<T> = std::result::Result<T, AppError>;

// Newtype pattern
pub struct UserId(i64);

// Builder pattern (derive_builder)
#[derive(Builder)]
pub struct Config {
    #[builder(default = "8080")]
    port: u16,
    host: String,
}
```

### 3.5.3 Framework Patterns

**Actix-web/Axum**:
```rust
// Axum routes
let app = Router::new()
    .route("/users", get(list_users).post(create_user))
    .route("/users/:id", get(get_user).put(update_user))
    .layer(TraceLayer::new_for_http())
    .with_state(state);

// Handler with extractors
async fn get_user(
    State(db): State<DbPool>,
    Path(id): Path<i64>,
) -> Result<Json<User>, AppError> { ... }
```

### 3.5.4 Cargo Configuration

```toml
[package]
name = "my-crate"
version = "0.1.0"
edition = "2021"

[features]
default = ["json"]
json = ["serde_json"]
full = ["json", "async"]

[dependencies]
tokio = { version = "1", features = ["full"] }
serde = { version = "1", features = ["derive"] }

[dev-dependencies]
tokio-test = "0.4"

[[bin]]
name = "my-cli"
path = "src/bin/cli.rs"
```

---

## §3.6 C#/.NET

### 3.6.1 Solution & Project Structure

**Detection Heuristics**:
| Signal | Detection | Implication |
|--------|-----------|-------------|
| `*.sln` | Solution file | Multi-project structure |
| `*.csproj` | C# project | Parse SDK, dependencies |
| `global.json` | SDK version | .NET version pinned |
| `Program.cs` | Entry point | Application bootstrap |
| `Startup.cs` | ASP.NET config | Web app configuration |

**File Patterns (Globs)**:
```
# Source files
**/*.cs

# Project files
**/*.sln, **/*.csproj, **/*.fsproj

# Config
global.json, nuget.config, Directory.Build.props
appsettings.json, appsettings.*.json
```

**Project Layout**:
```
Solution/
├── Solution.sln
├── src/
│   ├── Api/
│   │   ├── Api.csproj
│   │   ├── Controllers/
│   │   └── Program.cs
│   ├── Domain/
│   │   └── Domain.csproj
│   └── Infrastructure/
│       └── Infrastructure.csproj
├── tests/
│   └── Api.Tests/
│       └── Api.Tests.csproj
└── Directory.Build.props
```

### 3.6.2 ASP.NET Patterns

**Key Constructs**:
```csharp
// Minimal API (NET 6+)
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddScoped<IUserService, UserService>();

var app = builder.Build();
app.MapGet("/users/{id}", async (int id, IUserService service) => 
    await service.GetById(id));
app.Run();

// Controller-based
[ApiController]
[Route("api/[controller]")]
public class UsersController : ControllerBase
{
    private readonly IUserService _userService;
    
    [HttpGet("{id}")]
    public async Task<ActionResult<UserDto>> GetUser(int id)
    {
        var user = await _userService.GetById(id);
        return user is null ? NotFound() : Ok(user);
    }
}

// Dependency injection
builder.Services.AddScoped<IUserRepository, UserRepository>();
builder.Services.AddSingleton<ICacheService, RedisCacheService>();
builder.Services.AddTransient<IEmailSender, SmtpEmailSender>();
```

### 3.6.3 Entity Framework

```csharp
// DbContext
public class AppDbContext : DbContext
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Order> Orders => Set<Order>();
    
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasKey(e => e.Id);
            entity.HasIndex(e => e.Email).IsUnique();
            entity.HasMany(e => e.Orders).WithOne(o => o.User);
        });
    }
}

// Entity
public class User
{
    public int Id { get; set; }
    public required string Email { get; set; }
    public ICollection<Order> Orders { get; set; } = new List<Order>();
}

// Repository pattern
public interface IUserRepository
{
    Task<User?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<User> AddAsync(User user, CancellationToken ct = default);
}
```

**File Patterns**:
```
**/Migrations/*.cs
**/*DbContext.cs
**/Entities/*.cs, **/Models/*.cs
```

### 3.6.4 Configuration

```csharp
// appsettings.json binding
public class DatabaseSettings
{
    public required string ConnectionString { get; set; }
    public int MaxRetries { get; set; } = 3;
}

// Registration
builder.Services.Configure<DatabaseSettings>(
    builder.Configuration.GetSection("Database"));

// Usage
public class UserService(IOptions<DatabaseSettings> options)
{
    private readonly DatabaseSettings _settings = options.Value;
}
```

---

## Summary: Language Detection Quick Reference

| Language | Primary Detection | Framework Signals |
|----------|-------------------|-------------------|
| **TypeScript** | `tsconfig.json`, `*.ts` | `react`, `vue`, `@angular/core`, `express` in deps |
| **Python** | `pyproject.toml`, `*.py` | `flask`, `django`, `fastapi` in deps |
| **Go** | `go.mod`, `*.go` | `gin-gonic`, `echo`, `grpc` imports |
| **Java** | `pom.xml`/`build.gradle`, `*.java` | `spring-boot-starter`, `@Entity` |
| **Rust** | `Cargo.toml`, `*.rs` | `actix-web`, `axum`, `tokio` in deps |
| **C#** | `*.csproj`, `*.cs` | `Microsoft.AspNetCore`, `Microsoft.EntityFrameworkCore` |

> **Next**: After language-specific analysis completes, proceed to §4 — Synthesis & Workflow Reconstruction to merge outputs into a unified codebase model.


# Analysis Reference — §4: Synthesis & Workflow Reconstruction

> How to merge analyst outputs + native extractor outputs into a unified codebase model

---

## §4.1 Data Model Unification

### Unified Model Structure

The synthesis phase merges all analyst Markdown outputs and native extractor data into a single unified codebase model:

```typescript
interface UnifiedCodebaseModel {
  projectProfile: ProjectProfile;
  modules: Module[];
  dependencies: Dependency[];
  entryPoints: EntryPoint[];
  dataFlows: DataFlow[];
  apiSurface: APIEndpoint[];
  componentTree: Component[];
  inconsistencies: Inconsistency[];
  documentationPlan: DocumentationPlan;
}
```

### Component Definitions

```typescript
interface Module {
  id: string;                    // e.g., "src/auth"
  name: string;                  // human-readable name
  path: string;                  // filesystem path
  files: string[];               // all files in module
  purpose: string;               // LLM-derived purpose statement
  exports: Export[];             // from native extractor
  imports: Import[];             // from native extractor
  internalDependencies: string[]; // module IDs within project
  externalDependencies: string[]; // npm/pip/etc packages
  confidence: "high" | "medium" | "low";
}

interface Dependency {
  source: string;                // module ID
  target: string;                // module ID or external package
  type: "import" | "runtime" | "dev" | "peer";
  importedSymbols: string[];     // specific exports used
}

interface EntryPoint {
  path: string;
  type: "main" | "cli" | "route" | "export" | "event";
  description: string;
  reachableModules: string[];    // modules accessible from entry
}

interface DataFlow {
  name: string;
  description: string;
  steps: FlowStep[];
  entryPoint: string;
  exitPoint: string;
  modulesCrossed: string[];
}

interface FlowStep {
  order: number;
  module: string;
  file: string;
  function: string;
  description: string;
}

interface APIEndpoint {
  method: "GET" | "POST" | "PUT" | "DELETE" | "PATCH" | string;
  path: string;
  handler: string;              // file:function
  parameters: Parameter[];      // from native extractor
  responseType: string;         // from native extractor
  description: string;          // from LLM analysis
  authRequired: boolean;
}

interface Component {
  name: string;
  path: string;
  type: "page" | "layout" | "component" | "hook" | "context" | "utility";
  props: Prop[];                // from native extractor
  children: string[];           // component IDs
  stateUsage: string[];         // state/store references
}
```

### Merge Strategy: Native Extractor ↔ LLM Analysis

| Data Type | Native Extractor (Source of Truth) | LLM Analysis (Supplementary) |
|-----------|-----------------------------------|------------------------------|
| Function signatures | ✅ Names, parameters, return types | Purpose descriptions |
| Type definitions | ✅ Full interface/class definitions | Usage context |
| Import/export lists | ✅ Exact symbols, paths | Dependency rationale |
| File structure | ✅ Actual paths, exists checks | Module boundary interpretation |
| API routes | ✅ Exact paths, methods | Business purpose, auth requirements |
| Module purpose | Exports only | ✅ Architectural role description |
| Design patterns | — | ✅ Pattern identification |
| Data flow | — | ✅ Cross-module flow narratives |
| Architecture decisions | — | ✅ Why decisions were made |

### Conflict Resolution Rules

When native extractor and LLM analysis disagree:

1. **Names/Signatures** → Extractor wins
   - LLM says `getUserById(id)`, extractor says `getUserById(userId: string)` → use extractor
   
2. **File Paths** → Extractor wins
   - LLM hallucinates `src/utils/helpers.ts`, extractor shows no such file → discard

3. **Type Information** → Extractor wins
   - LLM infers `returns User`, extractor shows `returns Promise<User | null>` → use extractor

4. **Module Boundaries** → Prefer extractor, augment with LLM
   - Extractor shows import/export graph, LLM adds "this is the authentication domain"

5. **Architectural Interpretation** → LLM wins
   - Extractor shows code structure, LLM interprets "this follows hexagonal architecture"

6. **Purpose/Intent** → LLM wins
   - Extractor has no semantic understanding, LLM provides business context

### Merge Algorithm

```markdown
## Merge Process

1. **Load native extractor output** as base truth
   - Parse TypeDoc/Sphinx/Godoc JSON output
   - Build symbol table: {path:symbol → definition}
   
2. **Load each analyst output** (Markdown)
   - Parse structured sections (modules, flows, patterns)
   - Extract claims: {module, purpose, patterns, relationships}

3. **Overlay LLM analysis onto extractor base**
   For each LLM-identified module:
   - Match to extractor module by path
   - Validate file references exist
   - Add: purpose, patterns, architectural role
   - Discard: any mismatched signatures/types
   
4. **Cross-reference analyst outputs**
   - Architecture analyst → API surface analyst (route→handler mapping)
   - Data model analyst → Architecture analyst (model→service mapping)
   - Component analyst → API analyst (component→endpoint mapping)

5. **Build dependency graph**
   - Nodes: all modules from extractor
   - Edges: import relationships from extractor
   - Annotations: LLM-derived edge purposes

6. **Detect flows** (see §4.4)

7. **Flag inconsistencies** (see §4.3)
```

---

## §4.2 Cross-Cutting Correlation

Map relationships across analyst outputs for common architectures.

### Architecture 1: REST API

**Pattern**: Routes → Controllers/Handlers → Services → Data Access → Database

```
┌──────────┐    ┌────────────┐    ┌──────────┐    ┌─────────────┐    ┌──────────┐
│  Routes  │───▶│ Controllers│───▶│ Services │───▶│ Repositories│───▶│ Database │
│ (paths)  │    │ (handlers) │    │ (logic)  │    │ (data layer)│    │ (schema) │
└──────────┘    └────────────┘    └──────────┘    └─────────────┘    └──────────┘
```

**Correlation Chain**:

| Step | What to Find | Where to Look | How to Identify |
|------|--------------|---------------|-----------------|
| 1. Routes | Route definitions | API Surface Analyst output | `## Routes` section, path + method + handler |
| 2. Route→Handler | Handler function | Architecture Analyst + Native extractor | Handler path from route, cross-ref to exports |
| 3. Handler→Service | Service calls | Architecture Analyst | Handler imports, `inject`/`new Service()` patterns |
| 4. Service→Repository | Data access calls | Data Model Analyst | Service imports, repository method calls |
| 5. Repository→Model | ORM model usage | Data Model Analyst + Native extractor | Repository returns, model type definitions |
| 6. Model→Schema | Database mapping | Data Model Analyst | Decorators (`@Entity`, `@Table`), migrations |

**Link Identification Patterns**:

```markdown
### Express.js
- Route file: `app.use('/users', userRouter)` or `router.get('/:id', controller.getUser)`
- Handler reference: String `'controller.method'` or direct function import
- Service injection: Constructor parameter or module import

### NestJS
- Route: `@Controller('users')`, `@Get(':id')`
- Handler: Method on controller class
- Service: `@Inject()` decorator, constructor injection

### FastAPI (Python)
- Route: `@app.get("/users/{id}")`
- Handler: Decorated function
- Service: Function parameter with `Depends(get_service)`

### Go (Chi/Gin/Echo)
- Route: `r.Get("/users/{id}", handler.GetUser)`
- Handler: Function matching `http.HandlerFunc` signature
- Service: Struct field or package function call
```

**Correlation Output Format**:

```markdown
### REST API Flow: Get User by ID

| Layer | File | Symbol | Purpose |
|-------|------|--------|---------|
| Route | src/routes/users.ts | GET /users/:id | Entry point |
| Handler | src/controllers/user.controller.ts | getUser() | Request handling |
| Service | src/services/user.service.ts | findById() | Business logic |
| Repository | src/repositories/user.repo.ts | findOne() | Data access |
| Model | src/models/user.entity.ts | User | Data structure |
```

---

### Architecture 2: Full-Stack Web App

**Pattern**: Pages/Components → State Management → API Client → Backend API → Database

```
┌────────┐    ┌───────────┐    ┌────────────┐    ┌─────────┐    ┌──────────┐
│ Pages/ │───▶│   State   │───▶│ API Client │───▶│ Backend │───▶│ Database │
│  UI    │    │  (store)  │    │  (fetch)   │    │   API   │    │          │
└────────┘    └───────────┘    └────────────┘    └─────────┘    └──────────┘
```

**Correlation Chain**:

| Step | What to Find | Where to Look | How to Identify |
|------|--------------|---------------|-----------------|
| 1. Pages | Page components | Component Analyst output | `## Pages` or route-based file structure |
| 2. Page→State | State usage | Component Analyst | `useStore`, `useSelector`, `useState` calls |
| 3. State→API | API calls in actions | Component + Architecture Analyst | `fetch()`, `axios`, action creators |
| 4. API Client→Backend | Endpoint mapping | API Surface Analyst | Base URL + path construction |
| 5. Backend→Handler | Server route handling | (Same as REST API above) | Route definition |
| 6. Handler→Database | Data persistence | Data Model Analyst | ORM calls, queries |

**Link Identification Patterns**:

```markdown
### Next.js + React Query
- Page: `app/users/page.tsx` or `pages/users.tsx`
- State: `useQuery(['users'], fetchUsers)` 
- API Client: `fetch('/api/users')` or tRPC procedure
- Backend: `app/api/users/route.ts` or `pages/api/users.ts`

### React + Redux + REST
- Page: Route component in `<Route path="/users" element={<UsersPage/>}/>`
- State: `useSelector(selectUsers)`, `useDispatch()`
- Actions: `dispatch(fetchUsers())` → thunk/saga
- API Client: `axios.get('/api/users')` in thunk

### Vue + Pinia + Axios
- Page: `pages/users.vue` or `views/Users.vue`
- State: `const store = useUserStore()`, `store.users`
- Actions: `store.fetchUsers()` → Pinia action
- API Client: `api.get('/users')` in store action

### SvelteKit
- Page: `routes/users/+page.svelte`
- Load: `routes/users/+page.ts` load function
- API: `routes/api/users/+server.ts`
- State: Svelte stores or `$page.data`
```

**Correlation Output Format**:

```markdown
### Full-Stack Flow: User List Page

| Layer | File | Symbol | Data |
|-------|------|--------|------|
| Page | app/users/page.tsx | UsersPage | Renders user list |
| Hook | hooks/useUsers.ts | useUsers() | React Query hook |
| API Client | lib/api.ts | getUsers() | fetch('/api/users') |
| API Route | app/api/users/route.ts | GET handler | Returns User[] |
| Service | services/user.ts | listUsers() | Business logic |
| Repository | repositories/user.ts | findAll() | Prisma query |
| Model | prisma/schema.prisma | User model | Data schema |
```

---

### Architecture 3: CLI Tool

**Pattern**: Commands → Handlers → Core Logic → I/O/Storage

```
┌──────────┐    ┌──────────┐    ┌────────────┐    ┌─────────────┐
│ Commands │───▶│ Handlers │───▶│ Core Logic │───▶│ I/O/Storage │
│ (parser) │    │ (actions)│    │ (business) │    │ (files/db)  │
└──────────┘    └──────────┘    └────────────┘    └─────────────┘
```

**Correlation Chain**:

| Step | What to Find | Where to Look | How to Identify |
|------|--------------|---------------|-----------------|
| 1. Commands | CLI command defs | Architecture Analyst | Command parser setup, subcommand registration |
| 2. Command→Handler | Action function | Architecture Analyst + Native extractor | Command `action:` or handler mapping |
| 3. Handler→Core | Business logic | Architecture Analyst | Handler imports, function calls |
| 4. Core→I/O | File/network ops | Architecture + Data Model Analyst | fs, http, database calls |
| 5. Config | Configuration | Architecture Analyst | Config loading, env vars |

**Link Identification Patterns**:

```markdown
### Node.js (Commander.js)
- Command: `program.command('init').action(initHandler)`
- Handler: `initHandler` function
- Core: Imported modules called by handler

### Python (Click/Typer)
- Command: `@app.command()` decorator
- Handler: Decorated function
- Core: Imported functions called in handler

### Go (Cobra)
- Command: `&cobra.Command{Use: "init", Run: runInit}`
- Handler: `runInit` function
- Core: Package functions called by handler

### Rust (Clap)
- Command: `#[derive(Parser)]` struct with subcommands
- Handler: Match arm in main or subcommand module
- Core: Library crate functions
```

**Correlation Output Format**:

```markdown
### CLI Flow: init command

| Layer | File | Symbol | Purpose |
|-------|------|--------|---------|
| Command | src/cli.ts | init | Subcommand definition |
| Handler | src/commands/init.ts | initHandler() | Argument parsing, orchestration |
| Core | src/core/project.ts | createProject() | Project scaffolding logic |
| Templates | src/templates/ | template files | Project templates |
| I/O | src/core/project.ts | writeFiles() | File system writes |
| Config | src/config.ts | loadConfig() | Read .toolrc |
```

---

## §4.3 Inconsistency Detection

Flag issues that indicate analysis gaps or codebase problems.

### Inconsistency Checklist

| Category | Check | Detection Method | Severity |
|----------|-------|------------------|----------|
| **Orphaned Modules** | Module imports nothing and is imported by nothing | Dependency graph has isolated node | WARNING |
| **Dead Exports** | Symbol exported but never imported | Export list − all import references | INFO |
| **Unused Dependencies** | Package in manifest but not imported | package.json deps − all imports | WARNING |
| **Phantom Imports** | Import statement but file/package doesn't exist | Native extractor shows unresolved import | ERROR |
| **Mismatched Interfaces** | Caller passes different args than callee expects | Compare call sites to function signatures | ERROR |
| **Undocumented Public APIs** | Exported function/class has no JSDoc/docstring | Native extractor: export + no doc comment | INFO |
| **Circular Dependencies** | Module A imports B imports C imports A | Cycle detection in dependency graph | WARNING |
| **Version Conflicts** | Same package at multiple versions | Lock file analysis | WARNING |
| **Missing Types** | TypeScript `any` escape hatches | Native extractor type analysis | INFO |
| **Deprecated Usage** | Calls to @deprecated symbols | Native extractor deprecation markers | INFO |

### Detection Algorithms

```markdown
### Orphaned Module Detection
```python
def find_orphaned_modules(modules, dependencies):
    """Modules with no incoming or outgoing edges"""
    connected = set()
    for dep in dependencies:
        connected.add(dep.source)
        connected.add(dep.target)
    return [m for m in modules if m.id not in connected]
```

### Dead Export Detection
```python
def find_dead_exports(modules, dependencies):
    """Exports never referenced by any import"""
    all_imports = set()
    for dep in dependencies:
        all_imports.update(dep.importedSymbols)
    
    dead = []
    for module in modules:
        for export in module.exports:
            if export.name not in all_imports:
                dead.append((module.path, export.name))
    return dead
```

### Unused Dependency Detection
```python
def find_unused_deps(manifest_deps, actual_imports):
    """Dependencies declared but never imported"""
    imported_packages = {parse_package_name(i) for i in actual_imports}
    return manifest_deps - imported_packages
```

### Circular Dependency Detection
```python
def find_cycles(dependencies):
    """Find all cycles in dependency graph using DFS"""
    graph = build_adjacency_list(dependencies)
    cycles = []
    visited = set()
    rec_stack = set()
    
    def dfs(node, path):
        visited.add(node)
        rec_stack.add(node)
        for neighbor in graph.get(node, []):
            if neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                cycles.append(path[cycle_start:] + [neighbor])
            elif neighbor not in visited:
                dfs(neighbor, path + [neighbor])
        rec_stack.remove(node)
    
    for node in graph:
        if node not in visited:
            dfs(node, [node])
    return cycles
```
```

### LLM vs Native Extractor Cross-Check

| LLM Claim | Native Extractor Validation | Action if Mismatch |
|-----------|---------------------------|-------------------|
| "Module X exports function Y" | Check exports list for Y | Remove claim, flag inconsistency |
| "Function takes params A, B" | Check function signature | Replace with extractor data |
| "File at path P" | Check file exists | Remove reference, flag |
| "Uses library L" | Check import statements | Verify import exists |
| "Implements interface I" | Check type declarations | Verify implements clause |
| "Returns type T" | Check return type annotation | Replace with extractor data |

### Inconsistency Output Format

```markdown
### Inconsistencies Found

#### Errors (must fix before documentation)
- **Phantom Import**: `src/services/user.ts` imports `@company/auth` but package not in dependencies
- **Mismatched Interface**: `userController.create()` calls `userService.createUser(data)` but service expects `createUser(email, password)`

#### Warnings (documentation may be incomplete)
- **Orphaned Module**: `src/utils/legacy-helper.ts` has no imports or exports
- **Circular Dependency**: `auth` → `user` → `permissions` → `auth`
- **Unused Dependency**: `lodash` in package.json but no imports found

#### Info (minor issues)
- **Dead Export**: `src/utils/index.ts` exports `formatCurrency` (never imported)
- **Undocumented API**: `src/api/handlers/create-order.ts` - `createOrder()` has no JSDoc
- **Missing Types**: 3 functions use `any` return type
```

---

## §4.4 Documentation-Worthy Flow Detection

Identify key flows that deserve documentation attention.

### Flow Categories

| Category | Description | Entry Point Signal | Exit Point Signal |
|----------|-------------|-------------------|-------------------|
| **Request Lifecycle** | HTTP request → response | Route handler | Response send |
| **Data Pipeline** | Input → transform → output | File read, API fetch | File write, API response |
| **Build Process** | Source → compile → bundle | Build script entry | Output directory write |
| **Authentication Flow** | Login → token → authorization | Login endpoint | Token verification |
| **Event Processing** | Event emit → handlers → side effects | Event emit call | Handler completion |
| **Background Job** | Job enqueue → process → complete | Queue push | Job completion callback |

### Flow Detection Heuristics

#### Primary Heuristic: Module Boundary Crossings

> **Rule**: Flows crossing 3+ module boundaries are documentation-worthy

```python
def is_documentation_worthy(flow):
    """A flow is worth documenting if it crosses 3+ modules"""
    unique_modules = set(step.module for step in flow.steps)
    return len(unique_modules) >= 3
```

#### Secondary Heuristics

| Heuristic | Signal | Why Document |
|-----------|--------|--------------|
| **Entry Point Involved** | Flow starts at main, CLI command, or route | Primary user-facing behavior |
| **Data Persistence** | Flow ends at database write | Critical data path |
| **External System** | Flow involves external API call | Integration point |
| **Authentication Gate** | Flow passes through auth middleware | Security-critical path |
| **Error Boundary** | Flow has multiple catch/error handlers | Error handling strategy |
| **Async Boundary** | Flow crosses async/await or queue | Concurrency model |

### Flow Detection Algorithm

```markdown
## Flow Detection Process

1. **Identify Entry Points**
   - Main functions (main.ts, index.ts, app.py)
   - Route handlers (from API Surface Analyst)
   - CLI commands (from Architecture Analyst)
   - Event listeners (from Architecture Analyst)
   - Exported public APIs

2. **Trace Forward from Entry Points**
   For each entry point:
   - Follow function calls using dependency graph
   - Track module crossings
   - Record call chain as FlowStep[]
   - Stop at: I/O operations, response sends, returns

3. **Classify Flows**
   For each traced flow:
   - Count module crossings
   - Identify flow category (request, pipeline, etc.)
   - Apply documentation-worthy heuristics

4. **Deduplicate and Rank**
   - Merge similar flows (same modules, different parameters)
   - Rank by: module crossings × entry point importance
   - Select top N for documentation (default: 5-10)

5. **Extract Key Decision Points**
   For each selected flow:
   - Identify conditionals that branch behavior
   - Identify error handling points
   - Identify authorization checks
```

### Flow Output Format

```markdown
### Detected Flow: User Registration

**Category**: Request Lifecycle  
**Modules Crossed**: 5 (routes → controller → service → repository → email)  
**Documentation Priority**: High

| Step | Module | File | Function | Description |
|------|--------|------|----------|-------------|
| 1 | routes | src/routes/auth.ts | POST /register | Entry: receive registration request |
| 2 | controller | src/controllers/auth.ts | register() | Validate input, call service |
| 3 | service | src/services/user.ts | createUser() | Hash password, create user record |
| 4 | repository | src/repos/user.ts | insert() | Persist to database |
| 5 | service | src/services/email.ts | sendWelcome() | Send welcome email |
| 6 | controller | src/controllers/auth.ts | register() | Exit: return success response |

**Key Decision Points**:
- Step 2: Input validation (reject if invalid email format)
- Step 3: Check if email already exists (reject if duplicate)
- Step 5: Email send failure doesn't fail registration (graceful degradation)

**Error Handling**:
- ValidationError → 400 response
- DuplicateEmailError → 409 response
- DatabaseError → 500 response with retry header
```

### Diagram-Worthy Flow Criteria

A flow should get a dedicated diagram if:

| Criterion | Threshold | Diagram Type |
|-----------|-----------|--------------|
| Module crossings | ≥ 4 | Sequence diagram |
| Branching paths | ≥ 3 alternatives | Flowchart |
| Async operations | ≥ 2 await points | Sequence with async notation |
| External systems | ≥ 2 integrations | Integration diagram |
| State transitions | ≥ 4 states | State diagram |

---

## §4.5 Synthesis Summary Format

Output format for User Checkpoint (SKILL.md step 6).

### Template

```markdown
## Codebase Analysis Summary

### Project Profile
- **Type**: [detected type from scout - e.g., "REST API", "Full-stack web app", "CLI tool"]
- **Primary Language**: [lang] ([framework]) — e.g., "TypeScript (Next.js + Prisma)"
- **Architecture**: [pattern] — e.g., "Layered (routes → services → repositories)"
- **Size**: [N files, N modules, N lines] — e.g., "127 files, 12 modules, ~8,500 lines"
- **Analysis Mode**: [single-agent | scout+analysts | full pipeline]

### Key Modules

| Module | Purpose | Files | Key Exports | Confidence |
|--------|---------|-------|-------------|------------|
| src/api | REST API routes and handlers | 15 | userRouter, authRouter | high |
| src/services | Business logic layer | 8 | UserService, AuthService | high |
| src/models | Data models and types | 6 | User, Post, Comment | high |
| src/utils | Shared utilities | 12 | logger, config, validators | medium |
| src/db | Database connection and queries | 4 | prisma, migrations | high |

**Confidence Levels**:
- **high**: Native extractor verified + LLM analysis consistent
- **medium**: LLM analysis only, plausible but unverified
- **low**: Inferred from limited signals, may be inaccurate

### Dependency Graph Summary

```
[api] ──▶ [services] ──▶ [models]
   │           │             │
   │           ▼             │
   │      [db/prisma] ◀──────┘
   │
   └──▶ [utils] (shared)
```

- **Circular Dependencies**: None detected | [list if found]
- **External Dependencies**: 23 packages (12 runtime, 11 dev)

### Detected Flows

1. **User Registration** — api → services → db → email (5 modules, high priority)
2. **Authentication** — api → services → db → jwt (4 modules, high priority)  
3. **CRUD Operations** — api → services → db (3 modules, medium priority)
4. **Background Jobs** — queue → workers → services → db (4 modules, medium priority)
5. **Error Handling** — middleware → logger → monitoring (3 modules, low priority)

### API Surface

| Method | Path | Handler | Auth Required |
|--------|------|---------|---------------|
| POST | /api/users | createUser | No |
| GET | /api/users/:id | getUser | Yes |
| PUT | /api/users/:id | updateUser | Yes |
| DELETE | /api/users/:id | deleteUser | Yes (admin) |
| POST | /api/auth/login | login | No |
| POST | /api/auth/refresh | refreshToken | Yes |

*[N total endpoints, M require authentication]*

### Proposed Diagrams

- [x] **Architecture Overview** — Module relationships and layers
- [x] **Dependency Graph** — Full import/export graph
- [x] **API Route Map** — All endpoints with methods
- [ ] **Database Schema** — *(skipped: no ORM detected)*
- [x] **Auth Flow** — Login → token → protected routes
- [ ] **Component Tree** — *(skipped: no frontend detected)*
- [ ] **Build Pipeline** — *(skipped: standard npm scripts only)*

### Inconsistencies Found

#### Errors (0)
*None detected*

#### Warnings (2)
- **Unused Dependency**: `moment` in package.json but no imports found
- **Circular Dependency**: `services/user` ↔ `services/permissions`

#### Info (3)
- **Dead Export**: `utils/index.ts` exports `legacyHelper` (never imported)
- **Undocumented API**: `services/email.ts` - `sendBulk()` has no JSDoc
- **Missing Types**: 2 functions use `any` return type

### Existing Documentation Assessment

| Document | Status | Action |
|----------|--------|--------|
| README.md | Exists (partial) | Augment — add architecture section |
| CONTRIBUTING.md | Missing | Generate |
| API.md | Exists (outdated) | Regenerate — API changed significantly |
| architecture.md | Missing | Generate |

### Documentation Plan

**Core Documents** (always generated):
- `README.md` — Project overview, setup, usage
- `architecture-guide.md` — System architecture, module relationships
- `developer-guide.md` — Development workflow, contribution guide
- `codebase-context.md` — AI-readable codebase summary

**Optional Documents** (proposed based on detection):
- [x] `api-reference.md` — REST API documentation (API surface detected)
- [ ] `database-schema.md` — *(no ORM/schema detected)*
- [ ] `component-guide.md` — *(no frontend detected)*
- [x] `deployment-guide.md` — Docker + CI/CD detected

### Generation Estimate

- **Documents**: 6 (4 core + 2 optional)
- **Diagrams**: 4
- **Estimated Generation Time**: ~3-5 minutes
- **Review Rounds**: Up to 2 (if blockers found)

---

**Proceed with documentation generation?** [Y/n]

*You can request changes to the plan before proceeding.*
```

### Summary Field Specifications

| Field | Source | Computation |
|-------|--------|-------------|
| Type | Scout detection | Primary heuristic match |
| Primary Language | Native extractor | File extension frequency + framework markers |
| Architecture | Architecture Analyst | Pattern classification |
| Size | Scout file count | files / modules / estimated LOC |
| Modules | All analysts merged | Deduplicated by path |
| Module Purpose | Architecture Analyst | First sentence of module description |
| Module Confidence | Merge quality | high if extractor verified, else medium/low |
| Flows | §4.4 detection | Ranked by priority |
| API Surface | API Surface Analyst | Endpoint list |
| Diagrams | All analysts | Checkboxes from detection signals |
| Inconsistencies | §4.3 detection | Grouped by severity |
| Existing Docs | Scout inventory | Assessment + recommended action |
| Doc Plan | Scout + synthesis | Core always + optional based on detection |

### User Checkpoint Interaction

At step 6, present the synthesis summary and wait for user confirmation:

```markdown
## User Checkpoint Options

1. **Proceed** — Generate documentation with current plan
2. **Modify Plan** — Adjust which documents/diagrams to generate
3. **Re-analyze** — Run analysis again with different parameters
4. **Export Summary** — Save synthesis summary without generating docs
5. **Cancel** — Abort documentation generation

Common Modifications:
- "Skip the API reference, we maintain that separately"
- "Add a component guide even though frontend detection was low"
- "Focus only on the auth module for now"
- "Increase detail level for the architecture guide"
```

---

## Quick Reference: Synthesis Checklist

Before presenting User Checkpoint, verify:

- [ ] All analyst outputs loaded and parsed
- [ ] Native extractor output loaded (if available)
- [ ] Merge conflicts resolved (extractor wins for signatures)
- [ ] Module list deduplicated and confidence-scored
- [ ] Dependency graph built with no phantom references
- [ ] Flows detected and ranked by documentation priority
- [ ] Inconsistencies detected and categorized
- [ ] Existing documentation inventoried
- [ ] Documentation plan finalized (core + optional)
- [ ] Diagrams proposed based on detection signals
- [ ] Summary formatted for user readability
