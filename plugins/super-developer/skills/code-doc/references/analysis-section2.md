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
