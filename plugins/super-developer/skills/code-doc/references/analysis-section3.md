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
