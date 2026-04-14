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
