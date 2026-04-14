# Generation Reference — Document Templates & Mermaid Patterns

This reference defines the document templates and diagram patterns used by the code-doc skill during the generation phase. Section 3 (Update & Merge Logic) is in a separate file.

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
