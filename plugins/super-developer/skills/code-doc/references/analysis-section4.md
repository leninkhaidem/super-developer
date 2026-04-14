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
