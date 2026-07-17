# Dependency Injection and Registry Patterns Research

**Date**: 2026-02-15
**Purpose**: Research DI frameworks and registry patterns for building extensible primitives

---

## Table of Contents

1. [DI Framework Comparison](#di-framework-comparison)
2. [Registry Pattern Implementations](#registry-pattern-implementations)
3. [Provider Pattern Templates](#provider-pattern-templates)
4. [Auto-Discovery Patterns](#auto-discovery-patterns)
5. [Example: Generic HTTP Client Provider](#example-generic-http-client-provider)
6. [Best Practices and Recommendations](#best-practices-and-recommendations)

---

## DI Framework Comparison

### Python DI Frameworks

| Framework | Type | Strengths | Weaknesses | Best For |
|-----------|------|-----------|------------|----------|
| **dependency-injector** | Container-based | - Production-ready, Cython performance<br>- Rich provider types (Factory, Singleton, etc.)<br>- Explicit configuration | - More verbose configuration<br>- Steeper learning curve | Large applications with complex dependencies |
| **Lagom** | Type-based auto-wiring | - Zero configuration<br>- Type hint-based injection<br>- MyPy integration | - Less flexible for complex scenarios<br>- Newer, smaller ecosystem | Projects prioritizing type safety and simplicity |
| **injector** | Google-style | - Scope-based lifecycle<br>- Decorator-driven | - Scopes can be confusing<br>- Manual binding required | Projects using Google-style patterns |
| **FastAPI DI** | Framework-integrated | - Hierarchical dependencies<br>- Yield-based lifecycle<br>- Context manager support | - Tied to FastAPI framework<br>- Limited to request scope | FastAPI applications |
| **Manual (Protocol + Factory)** | Pattern-based | - Full control<br>- No framework overhead<br>- Type-safe with Protocol | - More boilerplate<br>- Manual lifecycle management | Small projects, libraries |

**Key Insights**:
- **dependency-injector** is the most comprehensive, suitable for production systems requiring explicit control
- **Lagom** excels at reducing boilerplate via type-based auto-wiring
- **FastAPI DI** integrates seamlessly with FastAPI's request lifecycle
- **Manual patterns** using Protocol provide zero-dependency type safety

**Sources**:
- [Lagom Comparison to Alternatives](https://lagom-di.readthedocs.io/en/stable/comparison/)
- [Dependency Injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [FastAPI Dependency Injection Guide 2026](https://thelinuxcode.com/dependency-injection-in-fastapi-2026-playbook-for-modular-testable-apis/)

---

### TypeScript/JavaScript DI Frameworks

| Framework | Type | Strengths | Weaknesses | Best For |
|-----------|------|-----------|------------|----------|
| **tsyringe** | Decorator-based | - Microsoft-maintained<br>- Lightweight<br>- Circular dependency support | - Reflection metadata required<br>- Limited advanced features | SPAs, edge functions, performance-critical apps |
| **InversifyJS** | Decorator-based | - Most feature-rich<br>- Middleware support<br>- Advanced binding options | - Larger bundle size<br>- Higher complexity | Large backend systems with complex binding logic |
| **awilix** | Registration-based | - Minimal boilerplate<br>- Performance-focused<br>- Simple API | - No decorator support<br>- Less "magical" | Bundle-sensitive apps, pragmatic teams |
| **NestJS** | Framework-integrated | - Complete application framework<br>- Lifecycle hooks<br>- Module system | - Framework lock-in<br>- Opinionated architecture | Full-stack enterprise applications |
| **Manual (Constructor Injection)** | Pattern-based | - Zero dependencies<br>- Explicit control | - Manual wiring<br>- No auto-discovery | Libraries, small apps |

**Key Insights**:
- **tsyringe** and **awilix** are best for performance-critical or bundle-sensitive applications
- **InversifyJS** offers the most power for complex enterprise scenarios
- **NestJS** provides a complete application framework beyond just DI
- Manual constructor injection works well for libraries that shouldn't impose DI frameworks on consumers

**Performance Benchmarks** (from DI Benchmark):
- Vanilla (manual): baseline (fastest)
- awilix: ~1.2x slower
- tsyringe: ~1.5x slower
- InversifyJS: ~2.5x slower
- NestJS: ~3x slower

**Sources**:
- [Dependency Injection Beyond NestJS](https://leapcell.io/blog/dependency-injection-beyond-nestjs-a-deep-dive-into-tsyringe-and-inversifyjs)
- [DI Benchmark Comparison](https://blog.vady.dev/di-benchmark-vanilla-registrycomposer-typed-inject-tsyringe-inversify-nestjs)
- [Top 5 TypeScript DI Containers](https://blog.logrocket.com/top-five-typescript-dependency-injection-containers/)

---

### Go DI Frameworks

| Framework | Type | Strengths | Weaknesses | Best For |
|-----------|------|-----------|------------|----------|
| **Wire** | Compile-time code generation | - Zero runtime overhead<br>- Compile-time validation<br>- No reflection | - Less flexible than runtime DI<br>- Requires code regeneration | Static dependency graphs, performance-critical apps |
| **Fx** | Runtime (Uber) | - Lifecycle management<br>- Graceful shutdown<br>- Module system | - Runtime reflection overhead<br>- More complex API | Complex services needing lifecycle hooks |
| **Dig** | Runtime (Uber) | - Flexible API<br>- Runtime resolution<br>- Dynamic composition | - Reflection-based errors<br>- Debugging challenges | Dynamic service composition |
| **Manual (Struct Composition)** | Pattern-based | - Idiomatic Go<br>- Explicit dependencies<br>- No magic | - Boilerplate for large apps<br>- Manual lifecycle | Most Go projects (Go philosophy favors this) |

**Key Insights**:
- **Wire** is preferred when dependency graphs are static and performance matters
- **Fx** excels when you need comprehensive lifecycle management (startup hooks, graceful shutdown)
- **Dig** provides the most flexibility for dynamic dependency resolution
- **Manual struct composition** is the most idiomatic Go approach and recommended for most projects

**Decision Matrix**:
- Static, performance-critical → **Wire**
- Complex lifecycle, modular architecture → **Fx**
- Dynamic composition needs → **Dig**
- Most Go projects → **Manual**

**Sources**:
- [Go DI Approaches: Wire vs Fx](https://leapcell.io/blog/go-dependency-injection-approaches-wire-vs-fx-and-manual-best-practices)
- [Dependency Injection for GO: Wire vs Dig](https://locxngo.medium.com/dependency-injection-for-go-google-wire-vs-uber-dig-6154ae7dab3f)
- [Go DI: Fx vs Wire vs Pure DI](https://medium.com/@geisonfgfg/dependency-injection-in-go-fx-vs-wire-vs-pure-di-structuring-maintainable-testable-applications-61c13939fd66)

---

## Registry Pattern Implementations

### Core Concepts

A **registry pattern** provides a centralized location for discovering and managing plugins, extensions, or service implementations. Key characteristics:

1. **Registration**: Mechanism for components to announce their availability
2. **Discovery**: Finding registered components at runtime or compile-time
3. **Retrieval**: Accessing registered components by key/type
4. **Type Safety**: Ensuring registered components match expected interfaces

### Python Registry Patterns

#### 1. Entry Points (Package Metadata)

```python
# setup.py or pyproject.toml
[project.entry-points."myapp.plugins"]
plugin_a = "myapp_plugin_a:PluginA"
plugin_b = "myapp_plugin_b:PluginB"

# Discovery code
from importlib.metadata import entry_points

def discover_plugins():
    discovered = entry_points(group='myapp.plugins')
    return {ep.name: ep.load() for ep in discovered}
```

**Advantages**:
- Standard Python packaging mechanism
- Cross-package plugin discovery
- No source code changes needed in host app

**Use Cases**: Flask extensions, pytest plugins, setuptools plugins

#### 2. Namespace Packages

```python
# myapp/plugins/__init__.py (empty, namespace package)
# Third-party packages can contribute to myapp.plugins namespace

# Discovery
import pkgutil
import myapp.plugins

def discover_plugins():
    return {
        name: __import__(f'myapp.plugins.{name}', fromlist=[''])
        for _, name, _ in pkgutil.iter_modules(myapp.plugins.__path__)
    }
```

**Advantages**:
- Decentralized plugin development
- No central registry needed

**Use Cases**: Large plugin ecosystems, distributed teams

#### 3. Decorator-based Registration

```python
from typing import Protocol, TypeVar, Generic, Dict, Type

T = TypeVar('T')

class PluginRegistry(Generic[T]):
    def __init__(self):
        self._registry: Dict[str, Type[T]] = {}

    def register(self, name: str):
        def decorator(cls: Type[T]) -> Type[T]:
            self._registry[name] = cls
            return cls
        return decorator

    def get(self, name: str) -> Type[T]:
        return self._registry[name]

    def all(self) -> Dict[str, Type[T]]:
        return self._registry.copy()

# Protocol definition
class MessageHandler(Protocol):
    def handle(self, message: str) -> None: ...

# Usage
handlers = PluginRegistry[MessageHandler]()

@handlers.register('email')
class EmailHandler:
    def handle(self, message: str) -> None:
        print(f"Emailing: {message}")

@handlers.register('sms')
class SMSHandler:
    def handle(self, message: str) -> None:
        print(f"SMS: {message}")

# Retrieval
handler_cls = handlers.get('email')
handler = handler_cls()
handler.handle("Hello")
```

**Advantages**:
- Type-safe with generics
- Clean, declarative syntax
- Self-documenting

**Use Cases**: Command handlers, serializers, validators

#### 4. `__init_subclass__` Auto-Registration

```python
class PluginBase:
    _registry: Dict[str, Type['PluginBase']] = {}

    def __init_subclass__(cls, plugin_name: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[plugin_name] = cls

    @classmethod
    def get_plugin(cls, name: str) -> Type['PluginBase']:
        return cls._registry[name]

# Usage - automatic registration on class definition
class EmailPlugin(PluginBase, plugin_name='email'):
    def send(self, msg: str):
        print(f"Email: {msg}")

class SMSPlugin(PluginBase, plugin_name='sms'):
    def send(self, msg: str):
        print(f"SMS: {msg}")

# Retrieval
plugin = PluginBase.get_plugin('email')()
plugin.send("Hello")
```

**Advantages**:
- Zero decorator boilerplate
- Registration happens at class definition time
- Type-safe with proper hints

**Use Cases**: Plugin systems, serialization backends, storage adapters

**Sources**:
- [Creating and Discovering Plugins - Python Packaging Guide](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/)
- [Implementing Registry Pattern with Decorators in Python](https://medium.com/@tihomir.manushev/implementing-the-registry-pattern-with-decorators-in-python-de8daf4a452a)
- [Building a Plugin Architecture with Python](https://mwax911.medium.com/building-a-plugin-architecture-with-python-7b4ab39ad4fc)

---

### TypeScript Registry Patterns

#### 1. Decorator-based Registration

```typescript
type Constructor<T> = new (...args: any[]) => T;

class Registry<T> {
  private registry = new Map<string, Constructor<T>>();

  register(name: string) {
    return (target: Constructor<T>) => {
      this.registry.set(name, target);
      return target;
    };
  }

  get(name: string): Constructor<T> | undefined {
    return this.registry.get(name);
  }

  all(): Map<string, Constructor<T>> {
    return new Map(this.registry);
  }
}

// Interface for type safety
interface MessageHandler {
  handle(message: string): void;
}

// Usage
const handlerRegistry = new Registry<MessageHandler>();

@handlerRegistry.register('email')
class EmailHandler implements MessageHandler {
  handle(message: string): void {
    console.log(`Email: ${message}`);
  }
}

@handlerRegistry.register('sms')
class SMSHandler implements MessageHandler {
  handle(message: string): void {
    console.log(`SMS: ${message}`);
  }
}

// Retrieval
const HandlerClass = handlerRegistry.get('email')!;
const handler = new HandlerClass();
handler.handle('Hello');
```

**Requirements**: `experimentalDecorators: true` in tsconfig.json

#### 2. Static Registration (No Decorators)

```typescript
interface Handler {
  handle(message: string): void;
}

class HandlerRegistry {
  private static handlers = new Map<string, new () => Handler>();

  static register<T extends Handler>(name: string, handler: new () => T): void {
    this.handlers.set(name, handler);
  }

  static get(name: string): Handler {
    const HandlerClass = this.handlers.get(name);
    if (!HandlerClass) throw new Error(`Handler ${name} not found`);
    return new HandlerClass();
  }
}

// Usage
class EmailHandler implements Handler {
  handle(message: string): void {
    console.log(`Email: ${message}`);
  }
}

HandlerRegistry.register('email', EmailHandler);

// Retrieval
const handler = HandlerRegistry.get('email');
handler.handle('Hello');
```

**Advantages**:
- No decorator configuration needed
- Works in all TypeScript environments
- Explicit registration

**Sources**:
- [Advanced TypeScript Techniques: Generics, Decorators](https://medium.com/@nikitinsn6/advanced-typescript-techniques-generics-decorators-and-more-25a2d10d8029)
- [TypeScript Generics Complete Guide 2026](https://devtoolbox.dedyn.io/blog/typescript-generics-complete-guide)

---

### Go Registry Patterns

#### 1. Package-level Registration

```go
package registry

import "sync"

type Handler interface {
    Handle(message string)
}

type Registry struct {
    mu       sync.RWMutex
    handlers map[string]func() Handler
}

var globalRegistry = &Registry{
    handlers: make(map[string]func() Handler),
}

func Register(name string, factory func() Handler) {
    globalRegistry.mu.Lock()
    defer globalRegistry.mu.Unlock()
    globalRegistry.handlers[name] = factory
}

func Get(name string) (Handler, bool) {
    globalRegistry.mu.RLock()
    defer globalRegistry.mu.RUnlock()
    factory, ok := globalRegistry.handlers[name]
    if !ok {
        return nil, false
    }
    return factory(), true
}

// Plugin packages call Register in init()
package email

import "myapp/registry"

type EmailHandler struct{}

func (h *EmailHandler) Handle(message string) {
    println("Email:", message)
}

func init() {
    registry.Register("email", func() registry.Handler {
        return &EmailHandler{}
    })
}
```

**Advantages**:
- Automatic registration via `init()`
- Thread-safe
- No reflection needed

**Use Cases**: Database drivers (database/sql), image formats (image)

#### 2. Explicit Registration with Generics (Go 1.18+)

```go
package registry

import "sync"

type Registry[T any] struct {
    mu        sync.RWMutex
    factories map[string]func() T
}

func NewRegistry[T any]() *Registry[T] {
    return &Registry[T]{
        factories: make(map[string]func() T),
    }
}

func (r *Registry[T]) Register(name string, factory func() T) {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.factories[name] = factory
}

func (r *Registry[T]) Get(name string) (T, bool) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    factory, ok := r.factories[name]
    if !ok {
        var zero T
        return zero, false
    }
    return factory(), true
}

// Usage
type Handler interface {
    Handle(message string)
}

var HandlerRegistry = registry.NewRegistry[Handler]()

type EmailHandler struct{}

func (h *EmailHandler) Handle(message string) {
    println("Email:", message)
}

func init() {
    HandlerRegistry.Register("email", func() Handler {
        return &EmailHandler{}
    })
}
```

**Advantages**:
- Type-safe with generics
- Explicit factory functions
- No interface{} casts

**Sources**:
- [C++ Patterns: Static Registration](https://dxuuu.xyz/cpp-static-registration.html) (concepts apply to Go)
- [Registry Pattern - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/registry-pattern/)

---

## Provider Pattern Templates

### Core Provider Pattern Concepts

A **provider** is an abstraction that:
1. Defines an interface for obtaining instances of a type
2. Encapsulates creation, lifecycle, and configuration
3. Allows swapping implementations without changing consumers
4. Supports multiple backends through a common interface

**Key Use Cases**:
- HTTP clients (requests, httpx, aiohttp)
- Database connections (PostgreSQL, MySQL, SQLite)
- Storage backends (S3, GCS, local filesystem)
- Message queues (RabbitMQ, Kafka, SQS)
- Cache backends (Redis, Memcached, in-memory)

---

### Python Provider Pattern

#### Generic Provider Protocol

```python
from typing import Protocol, TypeVar, Generic, runtime_checkable

T = TypeVar('T')

@runtime_checkable
class Provider(Protocol[T]):
    """Generic provider interface for dependency injection."""

    def provide(self) -> T:
        """Return an instance of T."""
        ...

    def cleanup(self) -> None:
        """Clean up resources (optional)."""
        ...

# Concrete implementation
class SingletonProvider(Generic[T]):
    """Provider that returns the same instance each time."""

    def __init__(self, factory: Callable[[], T]):
        self._factory = factory
        self._instance: Optional[T] = None

    def provide(self) -> T:
        if self._instance is None:
            self._instance = self._factory()
        return self._instance

    def cleanup(self) -> None:
        if hasattr(self._instance, 'close'):
            self._instance.close()
        self._instance = None

class FactoryProvider(Generic[T]):
    """Provider that creates a new instance each time."""

    def __init__(self, factory: Callable[[], T]):
        self._factory = factory

    def provide(self) -> T:
        return self._factory()

    def cleanup(self) -> None:
        pass  # Nothing to clean up

# Usage
def create_http_client() -> httpx.Client:
    return httpx.Client(timeout=30.0)

client_provider = SingletonProvider(create_http_client)
client = client_provider.provide()  # Same instance every time
```

#### Lifecycle-Aware Provider (FastAPI-style)

```python
from contextlib import contextmanager
from typing import Generator

class LifecycleProvider(Generic[T]):
    """Provider with startup/shutdown lifecycle hooks."""

    def __init__(
        self,
        factory: Callable[[], T],
        on_startup: Optional[Callable[[T], None]] = None,
        on_shutdown: Optional[Callable[[T], None]] = None
    ):
        self._factory = factory
        self._on_startup = on_startup
        self._on_shutdown = on_shutdown
        self._instance: Optional[T] = None
        self._started = False

    def startup(self) -> None:
        """Initialize the provider and call startup hook."""
        if not self._started:
            self._instance = self._factory()
            if self._on_startup:
                self._on_startup(self._instance)
            self._started = True

    def shutdown(self) -> None:
        """Shutdown the provider and call cleanup hook."""
        if self._started and self._instance:
            if self._on_shutdown:
                self._on_shutdown(self._instance)
            self._instance = None
            self._started = False

    def provide(self) -> T:
        if not self._started:
            raise RuntimeError("Provider not started. Call startup() first.")
        return self._instance

    @contextmanager
    def lifespan(self) -> Generator[T, None, None]:
        """Context manager for automatic lifecycle management."""
        self.startup()
        try:
            yield self.provide()
        finally:
            self.shutdown()

# Usage
def create_db_connection() -> Connection:
    return psycopg2.connect("postgresql://...")

def setup_db(conn: Connection) -> None:
    conn.execute("SET timezone='UTC'")

def teardown_db(conn: Connection) -> None:
    conn.close()

db_provider = LifecycleProvider(
    factory=create_db_connection,
    on_startup=setup_db,
    on_shutdown=teardown_db
)

# Automatic lifecycle
with db_provider.lifespan() as db:
    db.execute("SELECT * FROM users")
```

**Sources**:
- [Python Protocols: Leveraging Structural Subtyping](https://realpython.com/python-protocol/)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [FastAPI Dependency Injection 2026](https://thelinuxcode.com/dependency-injection-in-fastapi-2026-playbook-for-modular-testable-apis/)

---

### TypeScript Provider Pattern

#### Generic Provider Interface

```typescript
interface Provider<T> {
  provide(): T | Promise<T>;
  cleanup?(): void | Promise<void>;
}

// Singleton provider
class SingletonProvider<T> implements Provider<T> {
  private instance?: T;
  private factory: () => T;

  constructor(factory: () => T) {
    this.factory = factory;
  }

  provide(): T {
    if (!this.instance) {
      this.instance = this.factory();
    }
    return this.instance;
  }

  cleanup(): void {
    if (this.instance && typeof (this.instance as any).close === 'function') {
      (this.instance as any).close();
    }
    this.instance = undefined;
  }
}

// Factory provider
class FactoryProvider<T> implements Provider<T> {
  private factory: () => T;

  constructor(factory: () => T) {
    this.factory = factory;
  }

  provide(): T {
    return this.factory();
  }
}

// Async provider
class AsyncProvider<T> implements Provider<T> {
  private instance?: T;
  private factory: () => Promise<T>;
  private initialized = false;

  constructor(factory: () => Promise<T>) {
    this.factory = factory;
  }

  async provide(): Promise<T> {
    if (!this.initialized) {
      this.instance = await this.factory();
      this.initialized = true;
    }
    return this.instance!;
  }

  async cleanup(): Promise<void> {
    if (this.instance && typeof (this.instance as any).close === 'function') {
      await (this.instance as any).close();
    }
    this.instance = undefined;
    this.initialized = false;
  }
}

// Usage
const httpClientProvider = new SingletonProvider(() => {
  return new HTTPClient({ timeout: 5000 });
});

const client = httpClientProvider.provide();
```

#### Lifecycle-Aware Provider

```typescript
interface Lifecycle {
  startup?(): void | Promise<void>;
  shutdown?(): void | Promise<void>;
}

class LifecycleProvider<T extends Lifecycle> implements Provider<T> {
  private instance?: T;
  private factory: () => T;
  private started = false;

  constructor(factory: () => T) {
    this.factory = factory;
  }

  async startup(): Promise<void> {
    if (!this.started) {
      this.instance = this.factory();
      if (this.instance.startup) {
        await this.instance.startup();
      }
      this.started = true;
    }
  }

  async shutdown(): Promise<void> {
    if (this.started && this.instance) {
      if (this.instance.shutdown) {
        await this.instance.shutdown();
      }
      this.instance = undefined;
      this.started = false;
    }
  }

  provide(): T {
    if (!this.started || !this.instance) {
      throw new Error('Provider not started. Call startup() first.');
    }
    return this.instance;
  }
}

// Usage with NestJS-style module
class AppModule {
  private providers: LifecycleProvider<any>[] = [];

  async onModuleInit(): Promise<void> {
    for (const provider of this.providers) {
      await provider.startup();
    }
  }

  async onModuleDestroy(): Promise<void> {
    for (const provider of this.providers) {
      await provider.shutdown();
    }
  }
}
```

**Sources**:
- [Dependency Injection Beyond NestJS](https://leapcell.io/blog/dependency-injection-beyond-nestjs-a-deep-dive-into-tsyringe-and-inversifyjs)
- [Provider Pattern - patterns.dev](https://www.patterns.dev/vanilla/provider-pattern/)

---

### Go Provider Pattern

#### Generic Provider Interface

```go
package provider

import "context"

// Provider is a generic interface for providing instances of type T
type Provider[T any] interface {
    Provide(ctx context.Context) (T, error)
    Cleanup() error
}

// SingletonProvider returns the same instance each time
type SingletonProvider[T any] struct {
    factory  func() (T, error)
    instance T
    err      error
    once     sync.Once
}

func NewSingletonProvider[T any](factory func() (T, error)) *SingletonProvider[T] {
    return &SingletonProvider[T]{factory: factory}
}

func (p *SingletonProvider[T]) Provide(ctx context.Context) (T, error) {
    p.once.Do(func() {
        p.instance, p.err = p.factory()
    })
    return p.instance, p.err
}

func (p *SingletonProvider[T]) Cleanup() error {
    if closer, ok := any(p.instance).(io.Closer); ok {
        return closer.Close()
    }
    return nil
}

// FactoryProvider creates a new instance each time
type FactoryProvider[T any] struct {
    factory func() (T, error)
}

func NewFactoryProvider[T any](factory func() (T, error)) *FactoryProvider[T] {
    return &FactoryProvider[T]{factory: factory}
}

func (p *FactoryProvider[T]) Provide(ctx context.Context) (T, error) {
    return p.factory()
}

func (p *FactoryProvider[T]) Cleanup() error {
    return nil
}

// Usage
clientProvider := provider.NewSingletonProvider(func() (*http.Client, error) {
    return &http.Client{Timeout: 30 * time.Second}, nil
})

client, err := clientProvider.Provide(context.Background())
defer clientProvider.Cleanup()
```

#### Lifecycle Provider (Uber Fx-style)

```go
package provider

import (
    "context"
    "go.uber.org/fx"
)

type Lifecycle interface {
    OnStart(context.Context) error
    OnStop(context.Context) error
}

type LifecycleProvider[T Lifecycle] struct {
    factory  func() (T, error)
    instance T
    started  bool
    mu       sync.Mutex
}

func NewLifecycleProvider[T Lifecycle](factory func() (T, error)) *LifecycleProvider[T] {
    return &LifecycleProvider[T]{factory: factory}
}

func (p *LifecycleProvider[T]) Startup(ctx context.Context) error {
    p.mu.Lock()
    defer p.mu.Unlock()

    if p.started {
        return nil
    }

    instance, err := p.factory()
    if err != nil {
        return err
    }

    if err := instance.OnStart(ctx); err != nil {
        return err
    }

    p.instance = instance
    p.started = true
    return nil
}

func (p *LifecycleProvider[T]) Shutdown(ctx context.Context) error {
    p.mu.Lock()
    defer p.mu.Unlock()

    if !p.started {
        return nil
    }

    err := p.instance.OnStop(ctx)
    var zero T
    p.instance = zero
    p.started = false
    return err
}

func (p *LifecycleProvider[T]) Provide(ctx context.Context) (T, error) {
    p.mu.Lock()
    defer p.mu.Unlock()

    var zero T
    if !p.started {
        return zero, fmt.Errorf("provider not started")
    }
    return p.instance, nil
}

// Usage with Uber Fx
func NewDatabaseProvider() *LifecycleProvider[*Database] {
    return NewLifecycleProvider(func() (*Database, error) {
        return &Database{}, nil
    })
}

var Module = fx.Options(
    fx.Provide(NewDatabaseProvider),
    fx.Invoke(func(lc fx.Lifecycle, provider *LifecycleProvider[*Database]) {
        lc.Append(fx.Hook{
            OnStart: provider.Startup,
            OnStop:  provider.Shutdown,
        })
    }),
)
```

**Sources**:
- [Go DI Approaches: Wire vs Fx](https://leapcell.io/blog/go-dependency-injection-approaches-wire-vs-fx-and-manual-best-practices)
- [Uber Fx Documentation](https://github.com/uber-go/fx)

---

## Auto-Discovery Patterns

### Language-Specific Discovery Mechanisms

| Language | Mechanism | Compile-time | Runtime | Requires Config |
|----------|-----------|--------------|---------|-----------------|
| **Python** | Entry Points | ❌ | ✅ | setup.py/pyproject.toml |
| **Python** | Namespace Packages | ❌ | ✅ | Package structure |
| **Python** | `__init_subclass__` | ❌ | ✅ (at import) | ❌ |
| **Python** | Decorators | ❌ | ✅ (at import) | ❌ |
| **TypeScript** | Decorators | ❌ | ✅ (at module load) | tsconfig.json |
| **TypeScript** | Static Registration | ❌ | ✅ | ❌ |
| **Go** | `init()` functions | ❌ | ✅ (at program start) | ❌ |
| **Go** | Wire | ✅ | ❌ | Wire config |

---

### Python Auto-Discovery Patterns

#### Pattern 1: Entry Points (Best for Inter-Package Plugins)

```python
# pyproject.toml
[project.entry-points."myapp.handlers"]
email = "myapp_email:EmailHandler"
sms = "myapp_sms:SMSHandler"

# Auto-discovery
from importlib.metadata import entry_points

def discover_handlers():
    handlers = {}
    for ep in entry_points(group='myapp.handlers'):
        handlers[ep.name] = ep.load()
    return handlers

# Usage
handlers = discover_handlers()
email_handler = handlers['email']()
```

**When to Use**:
- Third-party plugins
- Distributed teams developing independent packages
- Flask-style extension ecosystem

#### Pattern 2: Namespace Packages (Best for Modular Monorepo)

```python
# Project structure:
# myapp/
#   plugins/
#     __init__.py  (namespace package - can be empty)
#     email.py
#     sms.py
#   core.py

# myapp/core.py
import pkgutil
import importlib

def discover_plugins():
    import myapp.plugins
    plugins = {}
    for importer, modname, ispkg in pkgutil.iter_modules(myapp.plugins.__path__):
        module = importlib.import_module(f'myapp.plugins.{modname}')
        # Assume each plugin module has a PLUGIN_CLASS attribute
        if hasattr(module, 'PLUGIN_CLASS'):
            plugins[modname] = module.PLUGIN_CLASS
    return plugins
```

**When to Use**:
- Internal plugin architecture
- Monorepo with multiple plugin packages
- Want plugins auto-discovered from file system

#### Pattern 3: `__init_subclass__` (Best for Simple Auto-Registration)

```python
from typing import Dict, Type

class HandlerBase:
    _registry: Dict[str, Type['HandlerBase']] = {}

    def __init_subclass__(cls, handler_type: str, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._registry[handler_type] = cls

    @classmethod
    def discover(cls) -> Dict[str, Type['HandlerBase']]:
        return cls._registry.copy()

# Plugins auto-register when class is defined
class EmailHandler(HandlerBase, handler_type='email'):
    def handle(self, message: str):
        print(f"Email: {message}")

class SMSHandler(HandlerBase, handler_type='sms'):
    def handle(self, message: str):
        print(f"SMS: {message}")

# Auto-discovery is automatic - just import the modules
import myapp.plugins.email  # Registers EmailHandler
import myapp.plugins.sms    # Registers SMSHandler

handlers = HandlerBase.discover()
```

**When to Use**:
- Simple plugin systems
- All plugins within same package
- Want zero decorator boilerplate

**Sources**:
- [Creating and Discovering Plugins - Python Packaging Guide](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/)
- [Kitty Litter - Plugins and Auto-discovery in Python](https://blog.tinbrain.net/blog/plugins-and-auto-discovery-python.html)

---

### TypeScript Auto-Discovery Patterns

#### Pattern 1: Decorator-based (Best for DI Integration)

```typescript
// registry.ts
export class HandlerRegistry {
  private static handlers = new Map<string, new () => Handler>();

  static register(name: string) {
    return function <T extends new () => Handler>(target: T) {
      HandlerRegistry.handlers.set(name, target);
      return target;
    };
  }

  static discover(): Map<string, new () => Handler> {
    return new Map(this.handlers);
  }

  static get(name: string): Handler {
    const HandlerClass = this.handlers.get(name);
    if (!HandlerClass) throw new Error(`Handler ${name} not found`);
    return new HandlerClass();
  }
}

// plugins/email.ts
@HandlerRegistry.register('email')
export class EmailHandler implements Handler {
  handle(message: string): void {
    console.log(`Email: ${message}`);
  }
}

// main.ts
import './plugins/email';  // Side-effect import registers handler
import './plugins/sms';

const handlers = HandlerRegistry.discover();
```

**Requires**: `experimentalDecorators: true` in tsconfig.json

#### Pattern 2: Module Side-Effects (Best for Framework-Free)

```typescript
// registry.ts
export class HandlerRegistry {
  private static handlers = new Map<string, new () => Handler>();

  static register(name: string, handler: new () => Handler): void {
    this.handlers.set(name, handler);
  }

  static discover(): Map<string, new () => Handler> {
    return new Map(this.handlers);
  }
}

// plugins/email.ts
import { HandlerRegistry } from '../registry';

export class EmailHandler implements Handler {
  handle(message: string): void {
    console.log(`Email: ${message}`);
  }
}

// Auto-register using module side-effect
HandlerRegistry.register('email', EmailHandler);

// main.ts
import './plugins/email';  // Triggers registration
import './plugins/sms';

const handlers = HandlerRegistry.discover();
```

**When to Use**:
- Don't want decorator dependency
- Works in all TypeScript environments
- Simple, explicit registration

---

### Go Auto-Discovery Patterns

#### Pattern 1: `init()` Function Registration

```go
// registry/registry.go
package registry

import "sync"

type Handler interface {
    Handle(message string)
}

var (
    mu       sync.RWMutex
    handlers = make(map[string]func() Handler)
)

func Register(name string, factory func() Handler) {
    mu.Lock()
    defer mu.Unlock()
    handlers[name] = factory
}

func Get(name string) (Handler, bool) {
    mu.RLock()
    defer mu.RUnlock()
    factory, ok := handlers[name]
    if !ok {
        return nil, false
    }
    return factory(), true
}

func Discover() map[string]func() Handler {
    mu.RLock()
    defer mu.RUnlock()
    result := make(map[string]func() Handler, len(handlers))
    for k, v := range handlers {
        result[k] = v
    }
    return result
}

// plugins/email/email.go
package email

import "myapp/registry"

type EmailHandler struct{}

func (h *EmailHandler) Handle(message string) {
    println("Email:", message)
}

func init() {
    registry.Register("email", func() registry.Handler {
        return &EmailHandler{}
    })
}

// main.go
package main

import (
    _ "myapp/plugins/email"  // Blank import triggers init()
    _ "myapp/plugins/sms"
    "myapp/registry"
)

func main() {
    handlers := registry.Discover()
    // handlers automatically contains 'email' and 'sms'
}
```

**When to Use**:
- Standard Go pattern (used by database/sql, image formats)
- Want automatic registration
- Plugin packages are known at compile time

#### Pattern 2: Explicit Registration (Best for Testability)

```go
// Avoid init(), use explicit registration instead
package main

import (
    "myapp/registry"
    "myapp/plugins/email"
    "myapp/plugins/sms"
)

func main() {
    // Explicit registration makes dependencies clear
    registry.Register("email", email.NewHandler)
    registry.Register("sms", sms.NewHandler)

    handlers := registry.Discover()
}
```

**When to Use**:
- Better testability (no global state in init)
- More explicit dependency management
- Easier to mock/stub in tests

**Go Best Practice**: Prefer explicit registration over `init()` for better testability, but `init()` is acceptable for driver-style registration (database drivers, image formats).

**Sources**:
- [C++ Patterns: Static Registration](https://dxuuu.xyz/cpp-static-registration.html) (concepts apply to Go)
- [Registry Pattern - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/registry-pattern/)

---

## Example: Generic HTTP Client Provider

This example demonstrates a complete implementation of a generic HTTP client provider supporting multiple backends (requests, httpx, aiohttp) with automatic backend selection, lifecycle management, and type-safe interfaces.

### Design Goals

1. **Backend Agnostic**: Support multiple HTTP client libraries
2. **Type Safe**: Full type hints and Protocol-based interfaces
3. **Lifecycle Aware**: Proper resource cleanup
4. **Auto-Discovery**: Automatic backend registration
5. **Configurable**: Configuration-driven backend selection
6. **Testable**: Easy to mock and test

---

### Implementation (Python)

#### 1. Core Interfaces

```python
# http_provider/interfaces.py
from typing import Protocol, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class HTTPRequest:
    """Standardized HTTP request."""
    method: str
    url: str
    headers: Optional[Dict[str, str]] = None
    params: Optional[Dict[str, Any]] = None
    json: Optional[Dict[str, Any]] = None
    timeout: Optional[float] = None

@dataclass
class HTTPResponse:
    """Standardized HTTP response."""
    status_code: int
    headers: Dict[str, str]
    body: bytes

    @property
    def text(self) -> str:
        return self.body.decode('utf-8')

    def json(self) -> Any:
        import json
        return json.loads(self.text)

class HTTPClient(Protocol):
    """Protocol for HTTP clients."""

    def request(self, req: HTTPRequest) -> HTTPResponse:
        """Execute HTTP request synchronously."""
        ...

    def close(self) -> None:
        """Close client and release resources."""
        ...

class AsyncHTTPClient(Protocol):
    """Protocol for async HTTP clients."""

    async def request(self, req: HTTPRequest) -> HTTPResponse:
        """Execute HTTP request asynchronously."""
        ...

    async def close(self) -> None:
        """Close client and release resources."""
        ...
```

#### 2. Backend Implementations

```python
# http_provider/backends/requests_backend.py
import requests
from ..interfaces import HTTPClient, HTTPRequest, HTTPResponse

class RequestsClient:
    """Adapter for requests library."""

    def __init__(self, timeout: float = 30.0):
        self.session = requests.Session()
        self.default_timeout = timeout

    def request(self, req: HTTPRequest) -> HTTPResponse:
        timeout = req.timeout or self.default_timeout
        response = self.session.request(
            method=req.method,
            url=req.url,
            headers=req.headers,
            params=req.params,
            json=req.json,
            timeout=timeout
        )
        return HTTPResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.content
        )

    def close(self) -> None:
        self.session.close()

# Auto-register (using registry from earlier)
from ..registry import http_client_registry

http_client_registry.register('requests', RequestsClient)

# http_provider/backends/httpx_backend.py
import httpx
from ..interfaces import HTTPClient, HTTPRequest, HTTPResponse

class HTTPXClient:
    """Adapter for httpx library (sync)."""

    def __init__(self, timeout: float = 30.0):
        self.client = httpx.Client(timeout=timeout)

    def request(self, req: HTTPRequest) -> HTTPResponse:
        response = self.client.request(
            method=req.method,
            url=req.url,
            headers=req.headers,
            params=req.params,
            json=req.json,
            timeout=req.timeout
        )
        return HTTPResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.content
        )

    def close(self) -> None:
        self.client.close()

http_client_registry.register('httpx', HTTPXClient)

# http_provider/backends/aiohttp_backend.py
import aiohttp
from ..interfaces import AsyncHTTPClient, HTTPRequest, HTTPResponse

class AIOHTTPClient:
    """Adapter for aiohttp library (async)."""

    def __init__(self, timeout: float = 30.0):
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.session: Optional[aiohttp.ClientSession] = None

    async def _ensure_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession(timeout=self.timeout)

    async def request(self, req: HTTPRequest) -> HTTPResponse:
        await self._ensure_session()

        timeout = aiohttp.ClientTimeout(total=req.timeout) if req.timeout else self.timeout

        async with self.session.request(
            method=req.method,
            url=req.url,
            headers=req.headers,
            params=req.params,
            json=req.json,
            timeout=timeout
        ) as response:
            body = await response.read()
            return HTTPResponse(
                status_code=response.status,
                headers=dict(response.headers),
                body=body
            )

    async def close(self) -> None:
        if self.session:
            await self.session.close()

from ..registry import async_http_client_registry
async_http_client_registry.register('aiohttp', AIOHTTPClient)
```

#### 3. Registry and Provider

```python
# http_provider/registry.py
from typing import Dict, Type, Callable
from .interfaces import HTTPClient, AsyncHTTPClient

class HTTPClientRegistry:
    """Registry for HTTP client backends."""

    def __init__(self):
        self._backends: Dict[str, Callable[..., HTTPClient]] = {}

    def register(self, name: str, backend: Callable[..., HTTPClient]) -> None:
        """Register a backend."""
        self._backends[name] = backend

    def get(self, name: str) -> Callable[..., HTTPClient]:
        """Get a backend by name."""
        if name not in self._backends:
            raise ValueError(f"Unknown backend: {name}. Available: {list(self._backends.keys())}")
        return self._backends[name]

    def available(self) -> list[str]:
        """List available backends."""
        return list(self._backends.keys())

# Global registries
http_client_registry = HTTPClientRegistry()
async_http_client_registry = HTTPClientRegistry()  # Same pattern for async

# http_provider/provider.py
from typing import Optional, Dict, Any
from .interfaces import HTTPClient
from .registry import http_client_registry

class HTTPClientProvider:
    """Provider for HTTP clients with auto-detection and lifecycle."""

    def __init__(
        self,
        backend: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.backend_name = backend or self._auto_detect_backend()
        self.config = config or {}
        self._client: Optional[HTTPClient] = None

    def _auto_detect_backend(self) -> str:
        """Auto-detect best available backend."""
        # Try in order of preference
        preferences = ['httpx', 'requests', 'aiohttp']
        available = http_client_registry.available()

        for pref in preferences:
            if pref in available:
                return pref

        if available:
            return available[0]

        raise RuntimeError("No HTTP client backends available")

    def provide(self) -> HTTPClient:
        """Provide an HTTP client instance."""
        if self._client is None:
            factory = http_client_registry.get(self.backend_name)
            self._client = factory(**self.config)
        return self._client

    def cleanup(self) -> None:
        """Clean up the client."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self) -> HTTPClient:
        return self.provide()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
```

#### 4. Configuration-Driven Selection

```python
# config.yaml
http:
  backend: httpx  # or 'requests', 'auto'
  timeout: 30.0
  retry:
    max_attempts: 3
    backoff_factor: 2.0

# usage.py
import yaml
from http_provider import HTTPClientProvider, HTTPRequest

# Load config
with open('config.yaml') as f:
    config = yaml.safe_load(f)

# Create provider from config
provider = HTTPClientProvider(
    backend=config['http']['backend'],
    config={'timeout': config['http']['timeout']}
)

# Use with context manager
with provider as client:
    response = client.request(HTTPRequest(
        method='GET',
        url='https://api.example.com/data'
    ))
    print(response.json())
```

#### 5. Dependency Injection Integration

```python
# With dependency-injector
from dependency_injector import containers, providers as di_providers

class Container(containers.DeclarativeContainer):
    config = di_providers.Configuration()

    http_client = di_providers.Singleton(
        HTTPClientProvider,
        backend=config.http.backend,
        config=config.http.client_config
    )

    api_service = di_providers.Factory(
        APIService,
        client=http_client.provided.provide()
    )

# With FastAPI
from fastapi import Depends

def get_http_client():
    provider = HTTPClientProvider()
    try:
        yield provider.provide()
    finally:
        provider.cleanup()

@app.get("/data")
async def get_data(client: HTTPClient = Depends(get_http_client)):
    response = client.request(HTTPRequest(method='GET', url='...'))
    return response.json()
```

#### 6. Testing with Mock Backend

```python
# tests/test_http_provider.py
import pytest
from http_provider import http_client_registry, HTTPClientProvider, HTTPRequest, HTTPResponse

class MockHTTPClient:
    """Mock HTTP client for testing."""

    def __init__(self):
        self.requests = []

    def request(self, req: HTTPRequest) -> HTTPResponse:
        self.requests.append(req)
        return HTTPResponse(
            status_code=200,
            headers={'content-type': 'application/json'},
            body=b'{"status": "ok"}'
        )

    def close(self) -> None:
        pass

@pytest.fixture
def mock_backend():
    """Register mock backend for testing."""
    http_client_registry.register('mock', MockHTTPClient)
    yield
    # Cleanup if needed

def test_http_provider_with_mock(mock_backend):
    provider = HTTPClientProvider(backend='mock')

    with provider as client:
        response = client.request(HTTPRequest(method='GET', url='http://test.com'))
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
```

---

### Key Patterns Demonstrated

1. **Protocol-based Abstraction**: `HTTPClient` protocol allows any implementation
2. **Adapter Pattern**: Each backend (requests, httpx, aiohttp) wrapped in adapter
3. **Registry Pattern**: Backends auto-register using decorators
4. **Provider Pattern**: `HTTPClientProvider` manages lifecycle and configuration
5. **Auto-Detection**: Automatically selects best available backend
6. **Configuration-Driven**: Backend selection via config files
7. **Context Manager**: Automatic resource cleanup
8. **DI Integration**: Works with FastAPI, dependency-injector, etc.
9. **Testability**: Easy to inject mock backends

---

## Best Practices and Recommendations

### Choosing a DI Framework

| Project Type | Python | TypeScript/JavaScript | Go |
|--------------|--------|----------------------|-----|
| **Small Library** | Manual (Protocol) | Manual (constructor injection) | Manual (struct composition) |
| **Medium App** | Lagom or FastAPI DI | tsyringe or awilix | Manual or Wire |
| **Large Enterprise** | dependency-injector | InversifyJS or NestJS | Fx |
| **Performance-Critical** | Manual | awilix | Wire |
| **Microservice** | FastAPI DI | NestJS | Fx |

### Registry Pattern Best Practices

1. **Type Safety First**: Use generics and protocols/interfaces
2. **Thread Safety**: Protect registry with locks (Go, Python threading)
3. **Fail Fast**: Validate registrations at startup, not at runtime
4. **Explicit Over Implicit**: Prefer explicit registration over magic
5. **Documentation**: Document registration mechanism clearly

### Provider Pattern Best Practices

1. **Lifecycle Management**: Always provide cleanup mechanisms
2. **Configuration**: Externalize configuration from code
3. **Error Handling**: Fail clearly when provider cannot initialize
4. **Lazy Initialization**: Create expensive resources only when needed
5. **Testing**: Always provide a way to inject test/mock implementations

### Anti-Patterns to Avoid

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Global Mutable State** | Hard to test, concurrency issues | Use DI container or context |
| **Hidden Dependencies** | Unclear what a component needs | Explicit constructor/factory parameters |
| **Over-Engineering** | DI for 3-line scripts | Use DI only when complexity warrants it |
| **Framework Lock-in** | Can't switch frameworks | Use Protocol/interface abstractions |
| **Singleton Abuse** | Hard to test, global state | Use scoped providers instead |
| **No Cleanup** | Resource leaks | Always implement cleanup/shutdown |

### When NOT to Use DI

- Scripts and utilities (< 100 lines)
- Pure functions and libraries
- Performance-critical hot paths
- When dependencies are truly static and never change

### Testing Strategies

1. **Mock Providers**: Create test implementations of Provider protocol
2. **Registry Clearing**: Clear registry between tests
3. **Explicit Injection**: Pass dependencies explicitly in tests
4. **Fixture Factories**: Use pytest fixtures / Go testing helpers
5. **Integration Tests**: Test real provider integrations separately

---

## References and Further Reading

### Python
- [Lagom Documentation](https://lagom-di.readthedocs.io/en/stable/)
- [Dependency Injector Documentation](https://python-dependency-injector.ets-labs.org/)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [FastAPI Dependency Injection 2026](https://thelinuxcode.com/dependency-injection-in-fastapi-2026-playbook-for-modular-testable-apis/)
- [Python Plugin Discovery Guide](https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/)
- [Implementing Registry Pattern with Decorators](https://medium.com/@tihomir.manushev/implementing-the-registry-pattern-with-decorators-in-python-de8daf4a452a)

### TypeScript/JavaScript
- [Dependency Injection Beyond NestJS](https://leapcell.io/blog/dependency-injection-beyond-nestjs-a-deep-dive-into-tsyringe-and-inversifyjs)
- [DI Benchmark Comparison](https://blog.vady.dev/di-benchmark-vanilla-registrycomposer-typed-inject-tsyringe-inversify-nestjs)
- [TypeScript Generics Complete Guide 2026](https://devtoolbox.dedyn.io/blog/typescript-generics-complete-guide)
- [Provider Pattern - patterns.dev](https://www.patterns.dev/vanilla/provider-pattern/)

### Go
- [Go DI Approaches: Wire vs Fx](https://leapcell.io/blog/go-dependency-injection-approaches-wire-vs-fx-and-manual-best-practices)
- [Dependency Injection for GO: Wire vs Dig](https://locxngo.medium.com/dependency-injection-for-go-google-wire-vs-uber-dig-6154ae7dab3f)
- [Uber Fx Documentation](https://github.com/uber-go/fx)
- [Google Wire Documentation](https://github.com/google/wire)

### General
- [Registry Pattern - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/registry-pattern/)
- [The Provider Pattern: A Comprehensive Guide](https://medium.com/@haidarally/the-provider-pattern-a-comprehensive-guide-with-c-examples-54c4a5cc0fd7)
- [Faraday HTTP Client (Ruby example of provider pattern)](https://github.com/lostisland/faraday)

---

## Appendix: Quick Reference Templates

### Python: Simple Decorator Registry

```python
from typing import TypeVar, Generic, Dict, Type

T = TypeVar('T')

class Registry(Generic[T]):
    def __init__(self):
        self._items: Dict[str, Type[T]] = {}

    def register(self, name: str):
        def decorator(cls: Type[T]) -> Type[T]:
            self._items[name] = cls
            return cls
        return decorator

    def get(self, name: str) -> Type[T]:
        return self._items[name]
```

### TypeScript: Simple Class Registry

```typescript
class Registry<T> {
  private items = new Map<string, new () => T>();

  register(name: string, cls: new () => T): void {
    this.items.set(name, cls);
  }

  get(name: string): T {
    const Cls = this.items.get(name);
    if (!Cls) throw new Error(`Not found: ${name}`);
    return new Cls();
  }
}
```

### Go: Simple Generic Registry

```go
type Registry[T any] struct {
    items map[string]func() T
    mu    sync.RWMutex
}

func NewRegistry[T any]() *Registry[T] {
    return &Registry[T]{items: make(map[string]func() T)}
}

func (r *Registry[T]) Register(name string, factory func() T) {
    r.mu.Lock()
    defer r.mu.Unlock()
    r.items[name] = factory
}

func (r *Registry[T]) Get(name string) (T, bool) {
    r.mu.RLock()
    defer r.mu.RUnlock()
    factory, ok := r.items[name]
    if !ok {
        var zero T
        return zero, false
    }
    return factory(), true
}
```

---

**End of Research Document**
