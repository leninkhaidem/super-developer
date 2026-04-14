# Generation Reference — Document Templates, Mermaid Patterns & Doc Writer Agents

This reference defines the document templates (§1), diagram patterns (§2), and doc writer agent prompts (§2.5) used by the code-doc skill during the generation phase. Doc writers are spawned as parallel background agents using the fan-out pattern. Section 3 (Update & Merge Logic) covers re-analysis workflows.

---

## §1 Document Templates

### Frontmatter Schema (All Documents)

Every generated document MUST include this YAML frontmatter:

```yaml
---
codedoc_version: 1
generated: 2024-03-15T10:30:00Z
project_hash: a1b2c3d4e5f6
---
```

| Field | Type | Description |
|-------|------|-------------|
| `codedoc_version` | integer | Schema version for forward compatibility. Currently `1`. |
| `generated` | ISO-8601 | UTC timestamp when document was generated. |
| `project_hash` | string | Git SHA of HEAD at generation time, or `"uncommitted"` if working tree has uncommitted changes. |

---

### Core Documents (Always Generated)

These four documents are generated for every project regardless of type or size.

---

#### 1. README.md

**Target Length:** 80-120 lines  
**Purpose:** First-contact document for new developers. Enables immediate understanding and running of the project.

**Section Structure:**

```markdown
# {Project Name}

{One-line description: what the project does, not how it does it.}

## Overview

{2-3 paragraphs explaining:
- What problem this solves
- Who it's for
- Key features (bullet list, 3-5 items)}

## Quick Start

### Prerequisites
{Numbered list of what must be installed before setup}

### Installation
{Exact commands to install dependencies — copy-pasteable}

### Running
{Single command to start the application}

### Verification
{How to confirm it's working — e.g., "Navigate to http://localhost:3000"}

## Architecture

{Mermaid architecture overview diagram — see §2}

{1-2 paragraphs explaining the diagram: major components and their responsibilities}

## Tech Stack

| Category | Technology |
|----------|------------|
| Language | {e.g., TypeScript 5.x} |
| Framework | {e.g., Next.js 14} |
| Database | {e.g., PostgreSQL 15} |
| ... | ... |

## Documentation Index

| Document | Description |
|----------|-------------|
| [Architecture Guide](./architecture-guide.md) | Deep dive into system design |
| [Developer Guide](./developer-guide.md) | Setup, conventions, contributing |
| [Codebase Context](./codebase-context.md) | Machine-readable project metadata |
| {Optional docs if generated} | ... |
```

**Content Quality:**
- One-line description must be specific: "REST API for inventory management" not "A backend service"
- Quick Start must actually work — commands must be verified
- Architecture diagram required, not optional
- Tech stack includes versions where relevant

---

#### 2. architecture-guide.md

**Target Length:** 300-500 lines  
**Purpose:** Enable understanding of system design decisions and module relationships.

**Section Structure:**

```markdown
# Architecture Guide

## Module Overview

{File tree with annotations showing major directories and their purposes}

```
src/
├── api/           # HTTP handlers and route definitions
│   ├── routes/    # Express/Fastify route modules
│   └── middleware/# Auth, logging, error handling
├── core/          # Business logic, pure functions
│   ├── services/  # Domain services
│   └── models/    # Domain entities
├── data/          # Persistence layer
│   ├── repositories/ # Data access abstractions
│   └── migrations/   # Database schema changes
└── shared/        # Cross-cutting utilities
    ├── config/    # Environment and feature flags
    └── utils/     # Helper functions
```

{2-3 paragraphs explaining the rationale for this structure}

## Dependency Graph

{Mermaid dependency graph — see §2}

**Key Dependencies:**
- {Module A} depends on {Module B} for {reason}
- {External dependency X} provides {capability}

## Design Patterns

### {Pattern 1 Name} (e.g., Repository Pattern)

**Where:** {Location in codebase}
**Why:** {Problem it solves}
**How:** {Brief implementation description}

```typescript
// Example showing the pattern
```

{Repeat for each significant pattern — typically 2-4 patterns}

## Data Flow

{Mermaid sequence diagram — see §2}

### Primary Flow: {Name, e.g., "User Authentication"}

1. {Step 1 with module involved}
2. {Step 2 with module involved}
3. ...

### Secondary Flow: {Name} (if applicable)
{Same structure}

## Key Abstractions

### {Abstraction 1, e.g., "Service Interface"}

**Purpose:** {What it represents}
**Location:** `{file path}`
**Implementations:** {List of concrete implementations}

```typescript
// Interface or base class definition
```

{Repeat for 3-5 key abstractions}

## Extension Points

How to extend this system for common scenarios:

### Adding a New {Entity/Feature Type}

1. {Step with file location}
2. {Step with file location}
3. ...

### Integrating a New {External Service Type}

1. ...

{Include 2-3 extension scenarios relevant to the project type}
```

**Content Quality:**
- File tree must match actual project structure — no invented directories
- Design patterns must be actually used, not aspirational
- Extension points should be actionable with specific file paths

---

#### 3. developer-guide.md

**Target Length:** 300-500 lines  
**Purpose:** Enable a new developer to set up, build, test, and contribute to the project.

**Section Structure:**

```markdown
# Developer Guide

## Prerequisites

| Requirement | Version | Verification Command |
|-------------|---------|---------------------|
| Node.js | 18.x+ | `node --version` |
| npm | 9.x+ | `npm --version` |
| PostgreSQL | 15+ | `psql --version` |
| ... | ... | ... |

{Any additional setup like environment variables, API keys, etc.}

## Setup

### 1. Clone and Install

```bash
git clone {repo-url}
cd {project-name}
npm install
```

### 2. Environment Configuration

```bash
cp .env.example .env
```

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@localhost:5432/db` |
| ... | ... | ... |

### 3. Database Setup

```bash
npm run db:migrate
npm run db:seed  # Optional: load sample data
```

### 4. Verify Installation

```bash
npm run dev
# Expected: Server running at http://localhost:3000
```

## Build & Test

### Development

```bash
npm run dev        # Start with hot reload
npm run dev:debug  # Start with debugger attached
```

### Building

```bash
npm run build      # Production build
npm run build:check # Build without emitting (type check only)
```

### Testing

```bash
npm test           # Run all tests
npm run test:unit  # Unit tests only
npm run test:e2e   # End-to-end tests
npm run test:watch # Watch mode
npm run test:coverage # With coverage report
```

### Linting & Formatting

```bash
npm run lint       # Check for issues
npm run lint:fix   # Auto-fix issues
npm run format     # Format with Prettier
```

## Project Structure

```
{Annotated file tree — similar to architecture-guide but with developer focus}
```

### Key Directories for New Contributors

| Directory | What Goes Here | When to Modify |
|-----------|---------------|----------------|
| `src/api/routes/` | New API endpoints | Adding new features |
| `src/core/services/` | Business logic | Changing behavior |
| `tests/` | Test files | Always with code changes |

## Conventions

### Code Style

- {Convention 1: e.g., "Use named exports, not default exports"}
- {Convention 2: e.g., "Prefix private methods with underscore"}
- {Convention 3: e.g., "One component per file"}

### Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Files | kebab-case | `user-service.ts` |
| Classes | PascalCase | `UserService` |
| Functions | camelCase | `getUserById` |
| Constants | SCREAMING_SNAKE | `MAX_RETRY_COUNT` |
| Database tables | snake_case | `user_sessions` |

### Git Workflow

- Branch naming: `{type}/{ticket}-{description}` (e.g., `feat/PROJ-123-add-auth`)
- Commit format: Conventional Commits (`feat:`, `fix:`, `docs:`, etc.)
- PR requirements: {tests pass, review approval, etc.}

## Contributing

### Before You Start

1. Check existing issues for the feature/bug
2. Create an issue if none exists
3. Get assignment or approval before starting

### Making Changes

1. Create a feature branch from `main`
2. Write tests first (TDD encouraged)
3. Implement the feature
4. Ensure all tests pass
5. Update documentation if needed
6. Submit PR with description linking to issue

### PR Checklist

- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] No linting errors
- [ ] Changelog updated (if applicable)

## Common Tasks

### Adding a New API Endpoint

1. Create route handler in `src/api/routes/{resource}.ts`
2. Add service method in `src/core/services/{resource}Service.ts`
3. Add repository method if database access needed
4. Write tests in `tests/api/{resource}.test.ts`
5. Update API documentation

### Adding a New Database Migration

```bash
npm run db:migration:create -- --name {migration-name}
# Edit the generated file in src/data/migrations/
npm run db:migrate
```

### Debugging

1. VS Code: Use provided launch configuration
2. Chrome DevTools: `npm run dev:debug` then open `chrome://inspect`
3. Logging: Set `LOG_LEVEL=debug` in `.env`

{Include 3-5 common tasks relevant to the project type}
```

**Content Quality:**
- All commands must be verified to work
- Environment variables must match actual `.env.example`
- Common tasks must reflect real project patterns

---

#### 4. codebase-context.md

**Target Length:** 80-150 lines  
**Format:** YAML (this is the ONLY document that uses YAML format)  
**Purpose:** Machine-readable metadata for AI agents and tooling.

**Section Structure:**

```yaml
---
codedoc_version: 1
generated: 2024-03-15T10:30:00Z
project_hash: a1b2c3d4e5f6
---

# Codebase Context
# Machine-readable project metadata for AI agents and tooling

project:
  name: "{project-name}"
  type: "{web-app|api|library|cli|monorepo|mobile|desktop}"
  description: "{One-line description}"

stack:
  primary_language: "{language}"
  language_version: "{version}"
  framework: "{framework-name}"
  framework_version: "{version}"
  runtime: "{node|python|jvm|go|dotnet}"
  package_manager: "{npm|yarn|pnpm|pip|poetry|go-mod|maven|gradle}"

entry_points:
  main: "{path to main entry file}"
  build: "{build command}"
  test: "{test command}"
  dev: "{dev command}"

modules:
  - name: "{module-name}"
    path: "{relative-path}"
    file_count: {number}
    purpose: "{brief description}"
    exports:
      - "{exported-symbol}"
  # Repeat for each major module (typically 5-15)

dependencies:
  internal:
    - from: "{module-a}"
      to: "{module-b}"
      type: "{import|extends|implements}"
  external:
    production:
      - name: "{package-name}"
        version: "{version}"
        purpose: "{why it's used}"
    development:
      - name: "{package-name}"
        version: "{version}"
        purpose: "{why it's used}"

file_inventory:
  total_files: {number}
  by_type:
    typescript: {number}
    javascript: {number}
    json: {number}
    markdown: {number}
    yaml: {number}
    css: {number}
    # ... other types

configuration_files:
  - path: "{relative-path}"
    purpose: "{what it configures}"
  # Include: package.json, tsconfig.json, .env.example, docker-compose.yml, etc.

testing:
  framework: "{jest|pytest|go-test|junit|etc.}"
  coverage_threshold: "{percentage or 'not-configured'}"
  test_directories:
    - "{path}"

documentation:
  existing_docs:
    - path: "{relative-path}"
      type: "{readme|api-docs|guides|etc.}"
  generated_by_codedoc:
    - path: "{relative-path}"
```

**Content Quality:**
- All paths must exist in the repository
- File counts must be accurate
- Module exports should be verified against actual code
- Dependencies should match package manifest

---

### Optional Documents (Proposed by Scout)

These documents are generated only when the scout phase detects relevant patterns.

---

#### 5. api-reference.md

**Inclusion Criteria:** Scout detects API routes (Express, FastAPI, Gin, etc.)  
**Skip Criteria:** No route definitions found, or native extractor (OpenAPI) provides complete coverage

**Target Length:** Variable (scales with API surface)  
**Source:** Primarily from native extractor output, enhanced with LLM analysis

**Section Structure:**

```markdown
# API Reference

## Base URL

- Development: `http://localhost:{port}`
- Production: `{production-url}`

## Authentication

{Authentication method description}

| Header | Value | Required |
|--------|-------|----------|
| `Authorization` | `Bearer {token}` | Yes (except public endpoints) |

## Endpoints

### {Resource Group, e.g., "Users"}

#### `GET /api/users`

{Brief description}

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `limit` | integer | No | Max results (default: 20) |
| `offset` | integer | No | Pagination offset |

**Response:**

```json
{
  "data": [...],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

**Status Codes:**

| Code | Description |
|------|-------------|
| 200 | Success |
| 401 | Unauthorized |

---

#### `POST /api/users`

{Continue for each endpoint}

## Error Codes

| Code | Name | Description |
|------|------|-------------|
| `AUTH_001` | Invalid Token | JWT token is malformed or expired |
| `USER_001` | User Not Found | Requested user does not exist |

## Rate Limits

| Endpoint Pattern | Limit | Window |
|-----------------|-------|--------|
| `/api/*` | 100 requests | 1 minute |
| `/api/auth/*` | 10 requests | 1 minute |
```

---

#### 6. deployment-guide.md

**Inclusion Criteria:** Scout detects infrastructure config (Dockerfile, kubernetes/, terraform/, .github/workflows/, etc.)  
**Skip Criteria:** No deployment configuration found

**Target Length:** 150-300 lines

**Section Structure:**

```markdown
# Deployment Guide

## Environments

| Environment | URL | Branch | Auto-Deploy |
|-------------|-----|--------|-------------|
| Development | {url} | `develop` | Yes |
| Staging | {url} | `main` | Yes |
| Production | {url} | `main` (tagged) | Manual |

## Infrastructure

{Mermaid deployment topology diagram — see §2}

### Components

| Component | Service | Configuration |
|-----------|---------|---------------|
| Web Server | {e.g., Vercel, AWS ECS} | {config location} |
| Database | {e.g., RDS PostgreSQL} | {config location} |
| Cache | {e.g., ElastiCache Redis} | {config location} |

## CI/CD Pipeline

{Mermaid CI pipeline diagram — see §2}

### Pipeline Stages

1. **Build** — {description}
2. **Test** — {description}
3. **Deploy** — {description}

## Deployment Steps

### Automated (via CI)

1. Push to `main` branch
2. CI runs tests
3. On success, deploys to staging
4. Manual approval for production

### Manual Deployment

```bash
# Build
npm run build

# Deploy to staging
npm run deploy:staging

# Deploy to production (requires approval)
npm run deploy:production
```

## Monitoring

| Metric | Tool | Dashboard |
|--------|------|-----------|
| Uptime | {tool} | {link} |
| Errors | {tool} | {link} |
| Performance | {tool} | {link} |

## Rollback

### Automated
{How to trigger rollback in CI}

### Manual
```bash
# Revert to previous version
{commands}
```
```

---

#### 7. data-model.md

**Inclusion Criteria:** Scout detects ORM config, schema files, or database migrations  
**Skip Criteria:** No database or ORM detected

**Target Length:** 150-400 lines (scales with schema complexity)

**Section Structure:**

```markdown
# Data Model

## Entity Relationship Diagram

{Mermaid erDiagram — see §2}

## Tables/Collections

### {Table Name, e.g., "users"}

**Purpose:** {What this table represents}

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | UUID | PK | Unique identifier |
| `email` | VARCHAR(255) | UNIQUE, NOT NULL | User's email |
| `created_at` | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation time |

**Indexes:**
- `idx_users_email` on `email`

**Relationships:**
- Has many `posts` (via `posts.user_id`)
- Has one `profile` (via `profiles.user_id`)

{Repeat for each table — typically 5-20 tables}

## Relationships

| From | To | Type | Foreign Key |
|------|-----|------|-------------|
| `users` | `posts` | One-to-Many | `posts.user_id` |
| `posts` | `comments` | One-to-Many | `comments.post_id` |
| `users` | `roles` | Many-to-Many | `user_roles` (junction) |

## Migration History

| Version | Name | Date | Description |
|---------|------|------|-------------|
| 001 | create_users | 2024-01-15 | Initial users table |
| 002 | add_posts | 2024-01-20 | Posts and comments |
| 003 | add_user_roles | 2024-02-01 | Role-based access |
```

---

#### 8. components/{name}.md

**Inclusion Criteria:** Scout detects frontend framework (React, Vue, Svelte, etc.)  
**Skip Criteria:** No frontend detected  
**Generation:** One file per major component (determined by scout heuristics: shared components, complex state, >100 lines)

**Target Length:** 50-100 lines per component

**Section Structure:**

```markdown
# {ComponentName}

**Path:** `src/components/{ComponentName}/{ComponentName}.tsx`  
**Type:** {Presentational|Container|Layout|Form|etc.}

## Purpose

{2-3 sentences describing what this component does and when to use it}

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `items` | `Item[]` | Yes | - | Data to display |
| `onSelect` | `(item: Item) => void` | No | - | Selection callback |
| `loading` | `boolean` | No | `false` | Show loading state |

## State

| State | Type | Description |
|-------|------|-------------|
| `selectedIndex` | `number` | Currently selected item index |
| `isOpen` | `boolean` | Dropdown open state |

## Children/Composition

- Uses `{ChildComponent}` for {purpose}
- Wraps content in `{WrapperComponent}`

## Usage Examples

### Basic Usage

```tsx
<{ComponentName} items={items} onSelect={handleSelect} />
```

### With Loading State

```tsx
<{ComponentName} items={items} loading={isLoading} />
```

## Styling

- CSS Module: `{ComponentName}.module.css`
- Theme tokens: Uses `--color-primary`, `--spacing-md`
- Responsive: Breakpoints at `sm`, `md`, `lg`
```

---

### Quality Anti-Patterns

The generation phase MUST flag and reject the following patterns:

| Anti-Pattern | Example | Fix |
|--------------|---------|-----|
| **Placeholder content** | "This module handles various things" | Be specific: "This module validates JWT tokens and manages session state" |
| **Empty sections** | `## Testing\n\n(coming soon)` | Omit section entirely, or populate with actual content |
| **Hallucinated paths** | `src/utils/helpers.ts` (doesn't exist) | Verify all paths against actual file tree |
| **Hallucinated functions** | `getUserById()` (doesn't exist) | Cross-reference against native extractor output |
| **Overly generic descriptions** | "Handles data processing" | Specify what data, what processing, what outcome |
| **Copy-paste templates** | Unchanged boilerplate from templates | Customize every section for the specific project |
| **Missing versions** | "Uses React" | Include version: "Uses React 18.2" |
| **Outdated information** | Package versions from analysis don't match package.json | Re-verify against source files |
| **Circular definitions** | "The user service handles user services" | Define in terms of functionality, not name |

**Quality Benchmark:** A new developer joining the project on day 1 should be able to:
1. Understand what the project does (README)
2. Set up their development environment (Developer Guide)
3. Understand the architecture and where to make changes (Architecture Guide)
4. Find any API endpoint or data model (optional docs)

---

## §2 Mermaid Diagram Patterns

### Overview

Diagrams are generated using Mermaid syntax. Each diagram type has specific inclusion/skip criteria to avoid generating irrelevant or empty diagrams.

---

### Core Diagrams (Generate When Data Available)

These three diagrams are generated for all projects where the relevant data can be extracted.

---

#### 1. Architecture Overview (flowchart TD)

**Purpose:** High-level view of system layers and module relationships  
**Location:** README.md, architecture-guide.md

**Template:**

```mermaid
flowchart TD
    subgraph {Layer1Name}["🎯 {Layer1Label}"]
        {Module1}["{Module1Label}"]
        {Module2}["{Module2Label}"]
    end
    
    subgraph {Layer2Name}["⚙️ {Layer2Label}"]
        {Module3}["{Module3Label}"]
        {Module4}["{Module4Label}"]
    end
    
    subgraph {Layer3Name}["💾 {Layer3Label}"]
        {Module5}["{Module5Label}"]
    end
    
    {Module1} --> {Module3}
    {Module2} --> {Module3}
    {Module3} --> {Module5}
    {Module4} --> {Module5}
```

**Worked Example (Next.js + Prisma E-commerce):**

```mermaid
flowchart TD
    subgraph Presentation["🎯 Presentation Layer"]
        Pages["Pages & Layouts"]
        Components["UI Components"]
        Hooks["Custom Hooks"]
    end
    
    subgraph Application["⚙️ Application Layer"]
        API["API Routes"]
        Services["Business Services"]
        Validators["Input Validators"]
    end
    
    subgraph Data["💾 Data Layer"]
        Prisma["Prisma Client"]
        Cache["Redis Cache"]
    end
    
    subgraph External["☁️ External Services"]
        Stripe["Stripe API"]
        S3["AWS S3"]
    end
    
    Pages --> Hooks
    Pages --> Components
    Hooks --> API
    API --> Services
    API --> Validators
    Services --> Prisma
    Services --> Cache
    Services --> Stripe
    Services --> S3
```

**Inclusion Criteria:**
- At least 2 distinct architectural layers detected
- At least 3 modules with clear relationships

**Skip Criteria:**
- Single-file scripts or trivial projects (<5 files)
- Cannot determine module boundaries

---

#### 2. Dependency Graph (flowchart LR)

**Purpose:** Show import relationships between modules  
**Location:** architecture-guide.md

**Template:**

```mermaid
flowchart LR
    subgraph {Group1}["{Group1Label}"]
        {ModA}["{ModALabel}"]
        {ModB}["{ModBLabel}"]
    end
    
    subgraph {Group2}["{Group2Label}"]
        {ModC}["{ModCLabel}"]
    end
    
    subgraph external[External]
        {Ext1}("{Ext1Label}")
        {Ext2}("{Ext2Label}")
    end
    
    %% Internal dependencies (solid arrows)
    {ModA} --> {ModC}
    {ModB} --> {ModC}
    
    %% External dependencies (dashed arrows)
    {ModC} -.-> {Ext1}
    {ModA} -.-> {Ext2}
```

**Worked Example (Python FastAPI Service):**

```mermaid
flowchart LR
    subgraph api["API Layer"]
        routes["routes/"]
        deps["dependencies/"]
    end
    
    subgraph core["Core"]
        services["services/"]
        models["models/"]
    end
    
    subgraph data["Data"]
        repos["repositories/"]
        schemas["schemas/"]
    end
    
    subgraph external["External"]
        fastapi(("FastAPI"))
        sqlalchemy(("SQLAlchemy"))
        pydantic(("Pydantic"))
    end
    
    routes --> deps
    routes --> services
    deps --> services
    services --> repos
    services --> models
    repos --> schemas
    
    routes -.-> fastapi
    repos -.-> sqlalchemy
    schemas -.-> pydantic
    models -.-> pydantic
```

**Inclusion Criteria:**
- At least 3 internal modules with import relationships
- Can extract imports from code analysis

**Skip Criteria:**
- Single module project
- Import analysis inconclusive

---

#### 3. Data Flow (sequenceDiagram)

**Purpose:** Show primary request lifecycle or data pipeline  
**Location:** architecture-guide.md

**Template:**

```mermaid
sequenceDiagram
    participant {Actor} as {ActorLabel}
    participant {Comp1} as {Comp1Label}
    participant {Comp2} as {Comp2Label}
    participant {Comp3} as {Comp3Label}
    
    {Actor}->>+{Comp1}: {Action1}
    {Comp1}->>+{Comp2}: {Action2}
    {Comp2}->>+{Comp3}: {Action3}
    {Comp3}-->>-{Comp2}: {Response3}
    {Comp2}-->>-{Comp1}: {Response2}
    {Comp1}-->>-{Actor}: {Response1}
```

**Worked Example (User Authentication Flow):**

```mermaid
sequenceDiagram
    participant Client as Browser
    participant API as Auth API
    participant Service as AuthService
    participant DB as Database
    participant Cache as Redis
    
    Client->>+API: POST /auth/login
    API->>+Service: validateCredentials(email, password)
    Service->>+DB: findUserByEmail(email)
    DB-->>-Service: User record
    Service->>Service: verifyPassword(password, hash)
    Service->>+Cache: setSession(userId, token)
    Cache-->>-Service: OK
    Service-->>-API: { token, user }
    API-->>-Client: 200 OK { token, user }
```

**Inclusion Criteria:**
- At least one clear user-facing flow (HTTP request, CLI command, event)
- At least 3 components involved in the flow

**Skip Criteria:**
- No clear entry point
- Library/package with no runtime flow

---

### Optional Diagrams (Include When Relevant)

These diagrams are generated only when specific project characteristics are detected.

---

#### 4. Component Hierarchy (flowchart TD)

**Purpose:** Show React/Vue/Svelte component tree  
**Location:** architecture-guide.md, or components/index.md

**Template:**

```mermaid
flowchart TD
    subgraph pages["Pages"]
        {Page1}["{Page1Name}"]
        {Page2}["{Page2Name}"]
    end
    
    subgraph layouts["Layouts"]
        {Layout1}["{Layout1Name}"]
    end
    
    subgraph features["Feature Components"]
        {Feature1}["{Feature1Name}"]
        {Feature2}["{Feature2Name}"]
    end
    
    subgraph shared["Shared Components"]
        {Shared1}["{Shared1Name}"]
        {Shared2}["{Shared2Name}"]
    end
    
    {Page1} --> {Layout1}
    {Page2} --> {Layout1}
    {Layout1} --> {Feature1}
    {Layout1} --> {Feature2}
    {Feature1} --> {Shared1}
    {Feature2} --> {Shared1}
    {Feature2} --> {Shared2}
```

**Worked Example (React Dashboard):**

```mermaid
flowchart TD
    subgraph pages["Pages"]
        Dashboard["DashboardPage"]
        Settings["SettingsPage"]
    end
    
    subgraph layouts["Layouts"]
        AppLayout["AppLayout"]
        AuthLayout["AuthLayout"]
    end
    
    subgraph features["Features"]
        Analytics["AnalyticsPanel"]
        UserList["UserList"]
        SettingsForm["SettingsForm"]
    end
    
    subgraph shared["Shared"]
        Card["Card"]
        Table["DataTable"]
        Button["Button"]
        Modal["Modal"]
    end
    
    Dashboard --> AppLayout
    Settings --> AppLayout
    AppLayout --> Analytics
    AppLayout --> UserList
    Settings --> SettingsForm
    Analytics --> Card
    UserList --> Table
    UserList --> Card
    SettingsForm --> Button
    SettingsForm --> Modal
```

**Inclusion Criteria:**
- Frontend framework detected (React, Vue, Svelte, Angular)
- At least 5 components in component directory

**Skip Criteria:**
- No frontend framework
- Fewer than 5 components
- Component structure flat (no hierarchy)

---

#### 5. API Route Map (flowchart LR)

**Purpose:** Visual map of API endpoints grouped by resource  
**Location:** api-reference.md

**Template:**

```mermaid
flowchart LR
    subgraph {Resource1}["/{resource1}"]
        {R1GET}["GET /"]
        {R1POST}["POST /"]
        {R1ID}["GET /:id"]
        {R1PUT}["PUT /:id"]
        {R1DEL}["DELETE /:id"]
    end
    
    subgraph {Resource2}["/{resource2}"]
        {R2GET}["GET /"]
        {R2POST}["POST /"]
    end
    
    {R1ID} -.-> {R2GET}
```

**Worked Example (E-commerce API):**

```mermaid
flowchart LR
    subgraph auth["/auth"]
        login["POST /login"]
        register["POST /register"]
        logout["POST /logout"]
        refresh["POST /refresh"]
    end
    
    subgraph users["/users"]
        getUsers["GET /"]
        getUser["GET /:id"]
        updateUser["PUT /:id"]
        deleteUser["DELETE /:id"]
    end
    
    subgraph products["/products"]
        listProducts["GET /"]
        getProduct["GET /:id"]
        createProduct["POST /"]
        updateProduct["PUT /:id"]
    end
    
    subgraph orders["/orders"]
        listOrders["GET /"]
        getOrder["GET /:id"]
        createOrder["POST /"]
        cancelOrder["DELETE /:id"]
    end
    
    login -.->|"returns user"| getUser
    createOrder -.->|"references"| getProduct
```

**Inclusion Criteria:**
- API routes detected (Express, FastAPI, Gin, etc.)
- At least 5 endpoints

**Skip Criteria:**
- No API routes
- Fewer than 5 endpoints (table format sufficient)

---

#### 6. Database Schema (erDiagram)

**Purpose:** Entity-relationship diagram for database tables  
**Location:** data-model.md

**Template:**

```mermaid
erDiagram
    {Entity1} ||--o{ {Entity2} : "{relationship}"
    {Entity1} {
        {type1} {field1} PK
        {type2} {field2}
        {type3} {field3} FK
    }
    {Entity2} {
        {type1} {field1} PK
        {type2} {field2} FK
    }
```

**Worked Example (Blog Schema):**

```mermaid
erDiagram
    users ||--o{ posts : "writes"
    users ||--o{ comments : "writes"
    posts ||--o{ comments : "has"
    posts }o--o{ tags : "tagged with"
    
    users {
        uuid id PK
        string email UK
        string password_hash
        string display_name
        timestamp created_at
        timestamp updated_at
    }
    
    posts {
        uuid id PK
        uuid author_id FK
        string title
        text content
        string status
        timestamp published_at
        timestamp created_at
    }
    
    comments {
        uuid id PK
        uuid post_id FK
        uuid author_id FK
        text content
        timestamp created_at
    }
    
    tags {
        uuid id PK
        string name UK
        string slug UK
    }
    
    post_tags {
        uuid post_id FK
        uuid tag_id FK
    }
```

**Inclusion Criteria:**
- Database schema detected (ORM models, migrations, SQL files)
- At least 3 tables with relationships

**Skip Criteria:**
- No database
- Single table or no relationships
- Schema extraction failed

---

#### 7. Deployment Topology (flowchart TD)

**Purpose:** Show infrastructure components and their connections  
**Location:** deployment-guide.md

**Template:**

```mermaid
flowchart TD
    subgraph users["Users"]
        {Client}["{ClientLabel}"]
    end
    
    subgraph edge["Edge"]
        {CDN}["{CDNLabel}"]
        {LB}["{LoadBalancer}"]
    end
    
    subgraph compute["Compute"]
        {App1}["{AppInstance1}"]
        {App2}["{AppInstance2}"]
    end
    
    subgraph data["Data Stores"]
        {DB}[("{Database}")]
        {Cache}[("{Cache}")]
    end
    
    {Client} --> {CDN}
    {CDN} --> {LB}
    {LB} --> {App1}
    {LB} --> {App2}
    {App1} --> {DB}
    {App2} --> {DB}
    {App1} --> {Cache}
    {App2} --> {Cache}
```

**Worked Example (AWS Deployment):**

```mermaid
flowchart TD
    subgraph users["Users"]
        Browser["Browser"]
        Mobile["Mobile App"]
    end
    
    subgraph edge["AWS Edge"]
        CloudFront["CloudFront CDN"]
        WAF["WAF"]
    end
    
    subgraph compute["AWS Compute"]
        ALB["Application Load Balancer"]
        ECS1["ECS Task 1"]
        ECS2["ECS Task 2"]
        Lambda["Lambda Functions"]
    end
    
    subgraph data["AWS Data"]
        RDS[("RDS PostgreSQL")]
        ElastiCache[("ElastiCache Redis")]
        S3[("S3 Bucket")]
    end
    
    subgraph monitoring["Monitoring"]
        CloudWatch["CloudWatch"]
        XRay["X-Ray"]
    end
    
    Browser --> CloudFront
    Mobile --> CloudFront
    CloudFront --> WAF
    WAF --> ALB
    ALB --> ECS1
    ALB --> ECS2
    ECS1 --> RDS
    ECS2 --> RDS
    ECS1 --> ElastiCache
    ECS2 --> ElastiCache
    ECS1 --> S3
    Lambda --> S3
    ECS1 -.-> CloudWatch
    ECS2 -.-> CloudWatch
    Lambda -.-> XRay
```

**Inclusion Criteria:**
- Infrastructure config detected (Dockerfile, docker-compose, kubernetes/, terraform/, cloudformation/)
- At least 3 infrastructure components defined

**Skip Criteria:**
- No infrastructure configuration
- Local-only development setup
- Single container with no external dependencies

---

#### 8. CI Pipeline (flowchart LR)

**Purpose:** Show CI/CD workflow stages  
**Location:** deployment-guide.md

**Template:**

```mermaid
flowchart LR
    subgraph trigger["Trigger"]
        {Trigger1}["{TriggerLabel}"]
    end
    
    subgraph build["Build"]
        {Step1}["{BuildStep1}"]
        {Step2}["{BuildStep2}"]
    end
    
    subgraph test["Test"]
        {Step3}["{TestStep1}"]
        {Step4}["{TestStep2}"]
    end
    
    subgraph deploy["Deploy"]
        {Step5}["{DeployStep1}"]
        {Step6}["{DeployStep2}"]
    end
    
    {Trigger1} --> {Step1}
    {Step1} --> {Step2}
    {Step2} --> {Step3}
    {Step3} --> {Step4}
    {Step4} --> {Step5}
    {Step5} --> {Step6}
```

**Worked Example (GitHub Actions):**

```mermaid
flowchart LR
    subgraph trigger["Trigger"]
        Push["Push to main"]
        PR["Pull Request"]
    end
    
    subgraph build["Build Stage"]
        Checkout["Checkout"]
        Install["Install deps"]
        Compile["TypeScript compile"]
    end
    
    subgraph test["Test Stage"]
        Lint["ESLint"]
        Unit["Unit tests"]
        Integration["Integration tests"]
        E2E["E2E tests"]
    end
    
    subgraph deploy["Deploy Stage"]
        BuildImage["Build Docker image"]
        PushImage["Push to ECR"]
        DeployStaging["Deploy to staging"]
        Approval["Manual approval"]
        DeployProd["Deploy to prod"]
    end
    
    Push --> Checkout
    PR --> Checkout
    Checkout --> Install
    Install --> Compile
    Compile --> Lint
    Lint --> Unit
    Unit --> Integration
    Integration --> E2E
    E2E --> BuildImage
    BuildImage --> PushImage
    PushImage --> DeployStaging
    DeployStaging --> Approval
    Approval --> DeployProd
```

**Inclusion Criteria:**
- CI config detected (.github/workflows/, .gitlab-ci.yml, Jenkinsfile, .circleci/, bitbucket-pipelines.yml)
- At least 3 pipeline stages defined

**Skip Criteria:**
- No CI configuration
- Single-step CI (e.g., just "npm test")

---

### Mermaid Syntax Guidelines

1. **Node IDs:** Use camelCase without spaces: `userService`, `authController`
2. **Labels:** Use quotes for labels with spaces: `["User Service"]`
3. **Subgraphs:** Always include descriptive label: `subgraph api["API Layer"]`
4. **Arrows:**
   - Solid (`-->`) for primary/internal dependencies
   - Dashed (`-.->`) for external/optional dependencies
   - With labels (`-->|"label"|`) for relationship description
5. **Shapes:**
   - `[]` rectangles for modules/components
   - `()` rounded for processes/actions
   - `(())` circles for external services
   - `[()]` cylinders for databases/storage
6. **Icons:** Use emoji sparingly for layer headers: 🎯 Presentation, ⚙️ Application, 💾 Data, ☁️ External

---

## §2.5 Doc Writer Agent Prompts

Each doc writer is spawned as `task(agent_type='general-purpose')` and reads assigned `.codedoc/` analysis files to produce one output document. Writers follow the template specs from §1 and diagram patterns from §2.

The orchestrator fans out to all applicable writers in parallel, then collects completion summaries before proceeding to review.

### Common Prompt Prefix

```
Prompt prefix (prepend to all doc writers):
  You are generating documentation for: {project_name}
  Project path: {project_path}
  Analysis directory: {project_path}/.codedoc/

  Follow the template spec in references/generation.md for your assigned section.
  Use references/generation.md Mermaid patterns for all diagrams.
  Write your output directly to the assigned file path.
  Apply frontmatter: codedoc_version: 1, generated: <ISO-8601>, project_hash: <git-hash>
  Return a compact summary: file written, line count, sections generated, diagrams included.
```

### README Writer

```
Prompt (append to common prefix):
  Assigned output: {project_path}/README.md
  Template: §1.1 (or first core document template)
  Input: read ALL .codedoc/*.md files for project overview
  Target: 100–200 lines

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-readme", prompt=<above>)
```

### Architecture Guide Writer

```
Prompt (append to common prefix):
  Assigned output: {project_path}/docs/architecture-guide.md
  Template: §1.2 (architecture guide template)
  Input: read .codedoc/architecture-analysis.md + .codedoc/synthesis.md
  Target: 200–400 lines
  Focus: System design, component relationships, data flow diagrams

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-architecture", prompt=<above>)
```

### Developer Guide Writer

```
Prompt (append to common prefix):
  Assigned output: {project_path}/docs/developer-guide.md
  Template: §1.3 (developer guide template)
  Input: read .codedoc/architecture-analysis.md + .codedoc/api-analysis.md + .codedoc/synthesis.md
  Target: 150–300 lines
  Focus: Dev setup, workflow, code structure, API usage, extension points

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-dev-guide", prompt=<above>)
```

### Codebase Context Writer

```
Prompt (append to common prefix):
  Assigned output: {project_path}/docs/codebase-context.md
  Template: §1.4 (codebase context template)
  Input: read ALL .codedoc/*.md files for metadata extraction
  Target: 300–500 lines
  Focus: Machine-readable context for LLMs, dependency graph, file inventory

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-codebase-ctx", prompt=<above>)
```

### API Reference Writer (Optional)

```
Prompt (append to common prefix):
  Assigned output: {project_path}/docs/api-reference.md
  Template: §1.5 (API reference template, if exists)
  Input: read .codedoc/api-analysis.md + .codedoc/native-extractors/ output
  Target: 200–500 lines
  Focus: Endpoint documentation, request/response schemas, auth patterns

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-api-ref", prompt=<above>)
```

### Data Model Writer (Optional)

```
Prompt (append to common prefix):
  Assigned output: {project_path}/docs/data-model.md
  Template: §1.6 (data model template, if exists)
  Input: read .codedoc/data-model-analysis.md + .codedoc/native-extractors/ output
  Target: 150–300 lines
  Focus: Schema documentation, relationships, migrations, ER diagrams

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-data-model", prompt=<above>)
```

### Component Guide Writer (Optional)

```
Prompt (append to common prefix):
  Assigned output: {project_path}/docs/component-guide.md
  Template: §1.7 (component guide template, if exists)
  Input: read .codedoc/component-analysis.md
  Target: 200–400 lines
  Focus: UI components, props/state, component tree, interaction patterns

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-components", prompt=<above>)
```

### Infrastructure Writer (Optional)

```
Prompt (append to common prefix):
  Assigned output: {project_path}/docs/infrastructure.md
  Template: §1.8 (infrastructure template, if exists)
  Input: read .codedoc/infrastructure-analysis.md
  Target: 100–200 lines
  Focus: CI/CD pipeline, deployment, Docker setup, environment config

Invocation:
  task(agent_type="general-purpose", mode="background", name="doc-infra", prompt=<above>)
```

Spawn all applicable doc writers in parallel. Collect completion summaries before proceeding to review.

---

# Generation Reference — §3: Update & Merge Logic

Re-analysis workflow for previously documented codebases. Handles three modes based on existing documentation state to preserve human investment while keeping generated docs current.

---

## §3.1 Update Detection

Before generating documentation, detect the existing documentation state:

```
check_doc_state(project_root):
  docs_path = project_root / "docs/"
  
  if not docs_path.exists() or is_empty(docs_path):
    return MODE_A_FRESH
  
  # Check any markdown file for codedoc frontmatter
  for md_file in docs_path.glob("**/*.md"):
    frontmatter = parse_frontmatter(md_file)
    if "codedoc_version" in frontmatter:
      return MODE_B_CODEDOC_OUTPUT
  
  # Docs exist but no codedoc markers
  return MODE_C_HUMAN_WRITTEN
```

**Detection Priority:**
1. If `{project}/docs/` does not exist or is empty → **Mode (a): Fresh Generation**
2. If docs exist with `codedoc_version` in frontmatter → **Mode (b): Existing code-doc Output**
3. If docs exist WITHOUT codedoc frontmatter → **Mode (c): Human-Written Docs**

---

## §3.2 Mode (a): Fresh Generation

**Condition:** No existing `docs/` directory, or `docs/` exists but is empty.

**Workflow:**
1. Run full analysis pipeline (scout → analysts → synthesis)
2. Fan out to doc writer agents (§2.5) — spawn all core writers in parallel
3. Fan out to optional doc writer agents based on scout findings
4. Collect completion summaries from all writers
5. Set `codedoc_version: 1` in all generated document frontmatter
6. Write to `{project}/docs/`

**Frontmatter for fresh generation:**
```yaml
---
codedoc_version: 1
generated: 2024-01-15T10:30:00Z
project_hash: abc123  # Hash of analyzed codebase state
---
```

No special handling required — straightforward generation.

---

## §3.3 Mode (b): Existing code-doc Output

**Condition:** `docs/` exists and at least one file contains `codedoc_version` frontmatter.

This mode handles re-documentation of a codebase that was previously documented by code-doc. Human additions must be preserved.

### Step 1: Archive Existing Docs

Create a versioned archive before any modifications:

```
docs/.archive/v{N}/          # N = existing codedoc_version
├── README.md
├── architecture-guide.md
├── developer-guide.md
├── codebase-context.md
└── ...
```

Archive preserves the complete previous state for rollback if needed.

### Step 2: Detect Human Content

Identify human-authored content that must be preserved. Detection in priority order:

**2a. Explicit Markers (highest confidence)**
```markdown
<!-- human -->
This section was written by a developer and contains project-specific
context that cannot be automatically generated.
<!-- /human -->
```

**2b. Non-Template Headers**
Sections with headers not present in the template specification (from §1) are assumed human-authored:

```markdown
## Known Gotchas              <!-- Not in template → preserve -->
## Migration from v1 to v2    <!-- Not in template → preserve -->
## Troubleshooting            <!-- Not in template → preserve -->
```

**2c. Unmarked Substantive Sections**
Entire sections without codedoc markers but with substantive content (>10 lines of prose, not just code blocks):

```markdown
## Deployment Notes
<!-- No markers, but 15 lines of detailed deployment instructions -->
<!-- Preserve as human-authored -->
```

### Step 3: Regenerate Fresh Docs

Run the full analysis pipeline as if Mode (a), then fan out to doc writer agents (§2.5):
- Scout the codebase
- Run analysts
- Synthesize findings
- Spawn doc writer agents in parallel to generate fresh documents from templates

### Step 4: Re-insert Human Blocks

After regeneration, merge preserved human content back:

**4a. Matching Header Found:**
Re-insert preserved content AFTER the generated content under the same header:

```markdown
## Configuration

<!-- Generated content -->
The application uses environment variables for configuration...

<!-- human -->
### Legacy Configuration
For deployments before v2.0, the old config.ini format is still supported...
<!-- /human -->
```

**4b. No Matching Header:**
Append at the end of the relevant document with a note:

```markdown
<!-- NOTE: original header was "Database Quirks" -->
<!-- human -->
Our Postgres setup has a non-standard schema for historical reasons...
<!-- /human -->
```

**4c. Wrap All Preserved Content:**
Ensure all preserved blocks have explicit `<!-- human -->` markers for future runs (even if they were detected heuristically this time).

### Step 5: Version Bump

Update frontmatter in all regenerated documents:

```yaml
---
codedoc_version: 3      # Was 2, now 3
generated: 2024-03-20T14:00:00Z
project_hash: def456    # Updated hash
---
```

---

## §3.4 Mode (c): Existing Human-Written Docs

**Condition:** `docs/` exists with content but NO `codedoc_version` frontmatter anywhere.

⚠️ **CRITICAL MODE** — Existing well-written documentation must NOT be destroyed.

### Preservation Rules

**Rule 1: Never Overwrite Comprehensive README**
```
if README.md exists AND (
  line_count > 50 OR
  has_multiple_h2_sections
):
  DO NOT generate a new README.md
```

**Rule 2: Never Overwrite Curated Docs**
Any existing doc that appears manually curated (based on prose quality, custom sections, detailed examples) is preserved entirely.

**Rule 3: Generate Only Gap-Filling Docs**
| Document | Generation Rule |
|----------|-----------------|
| `codebase-context.md` | Always generate — machine metadata, doesn't overlap with human prose |
| `architecture-guide.md` | Only if no equivalent exists (`ARCHITECTURE.md`, `architecture/`, `design/`) |
| `developer-guide.md` | Only if no equivalent exists (`CONTRIBUTING.md`, `DEVELOPMENT.md`, `dev-guide.md`) |

### Augmentation Strategy

Generate code-doc output to a **subdirectory** to avoid conflicts:

```
docs/
├── README.md              # Human — preserved
├── CONTRIBUTING.md        # Human — preserved
├── API.md                 # Human — preserved
└── codedoc/               # Generated — new subdirectory
    ├── INDEX.md           # Links to both human and generated docs
    ├── codebase-context.md
    ├── architecture-guide.md   # Only if gap-filling
    └── diagrams/
        └── architecture.mmd
```

### Create Index Document

Generate `docs/codedoc/INDEX.md` that provides navigation:

```markdown
---
codedoc_version: 1
generated: 2024-01-15T10:30:00Z
---
# Documentation Index

## Existing Documentation
- [README](../README.md) — Project overview and quick start
- [Contributing](../CONTRIBUTING.md) — Contribution guidelines
- [API Reference](../API.md) — API documentation

## Generated Documentation
- [Codebase Context](./codebase-context.md) — Machine-readable project metadata
- [Architecture Guide](./architecture-guide.md) — System architecture overview

*Generated by code-doc. Existing documentation preserved.*
```

### Frontmatter for Mode (c)

Only generated docs receive codedoc frontmatter:
```yaml
---
codedoc_version: 1
generated: 2024-01-15T10:30:00Z
project_hash: abc123
augmentation_mode: true   # Indicates gap-filling only
---
```

Human docs are **never modified** — no frontmatter injection.

---

## §3.5 Edge Cases

| Situation | Detection | Handling |
|-----------|-----------|----------|
| **No existing docs** | `docs/` doesn't exist | Mode (a): fresh run, version 1 |
| **Empty docs folder** | `docs/` exists but contains no `.md` files | Mode (a): treat as no docs |
| **Human docs without frontmatter** | `docs/*.md` exist, none have `codedoc_version` | Mode (c): preserve entirely, generate only to `docs/codedoc/` |
| **Code-doc output without frontmatter** | Docs match code-doc templates but missing frontmatter | Treat as version 0, Mode (b): archive to `v0/` and regenerate |
| **Human block header changed** | Preserved block's original header no longer exists in template | Append with `<!-- NOTE: original header was "X" -->` |
| **Monorepo with mixed doc states** | Different sub-projects have different doc states | Handle each sub-project independently per its own state |
| **Only README.md (no docs/ folder)** | Root `README.md` exists, no `docs/` directory | If README >50 lines: Mode (c), create `docs/codedoc/`. If <50 lines: Mode (a), wrap README content as `<!-- human -->` block in generated README |
| **Partial codedoc output** | Some docs have `codedoc_version`, others don't | Mode (b) for the project, but preserve non-codedoc files as human content |
| **docs/ with only images/assets** | `docs/` contains only non-markdown files | Mode (a): treat as no documentation |
| **Nested docs structure** | `docs/` has subdirectories like `docs/api/`, `docs/guides/` | Scan recursively for frontmatter; preserve nested human structure in Mode (c) |

### Mode Detection Flowchart

```
┌─────────────────────────────────────────────────────────────────┐
│                    Start: Check docs/ state                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                   ┌──────────────────┐
                   │ docs/ exists?    │
                   └──────────────────┘
                    │              │
                   No             Yes
                    │              │
                    ▼              ▼
              ┌──────────┐  ┌───────────────────┐
              │ Mode (a) │  │ Has .md files?    │
              │ Fresh    │  └───────────────────┘
              └──────────┘      │           │
                               No          Yes
                                │           │
                                ▼           ▼
                          ┌──────────┐  ┌───────────────────────┐
                          │ Mode (a) │  │ Any codedoc_version?  │
                          │ Fresh    │  └───────────────────────┘
                          └──────────┘      │               │
                                           No              Yes
                                            │               │
                                            ▼               ▼
                                    ┌─────────────┐  ┌─────────────┐
                                    │  Mode (c)   │  │  Mode (b)   │
                                    │ Human Docs  │  │ Code-doc    │
                                    └─────────────┘  └─────────────┘
```

---

## Summary

| Mode | Condition | Action | Output Location |
|------|-----------|--------|-----------------|
| **(a) Fresh** | No docs or empty docs/ | Full generation | `docs/` |
| **(b) Code-doc Output** | `codedoc_version` present | Archive → Regenerate → Merge human blocks | `docs/` (in-place) |
| **(c) Human-Written** | Docs exist, no codedoc markers | Preserve all → Generate gaps only | `docs/codedoc/` |
