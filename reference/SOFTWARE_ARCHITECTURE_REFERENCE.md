# Software Architecture Principles Reference

## 1. Architectural Styles

### Clean Architecture (Robert Martin/Uncle Bob)

**Core Principles:**
- **Independent of Frameworks**, **Testable**, **Independent of UI**, **Independent of Database**
- **The Dependency Rule**: Source code dependencies can only point **inwards**
- Cross-boundary communication uses **Dependency Inversion** (interfaces)
- Data crossing boundaries should be **simple data structures** (DTOs), not entities

**Four Layers (Inner to Outer):**

| Layer | Responsibility |
|-------|----------------|
| **Entities** | Enterprise-wide business rules, most general/high-level rules |
| **Use Cases** | Application-specific business rules |
| **Interface Adapters** | Converts data between formats and external agencies |
| **Frameworks/Drivers** | Outermost layer - frameworks, databases, tools |

---

### Hexagonal Architecture (Alistair Cockburn)

**Core Concepts:**

| Concept | Definition |
|---------|------------|
| **Ports** | APIs that define communication between application and external agencies |
| **Adapters** | Convert API definitions to signals needed by external devices |
| **Primary (Driving) Adapters** | Users, test harnesses, other programs |
| **Secondary (Driven) Adapters** | Databases, external services, mocks |

**Key Rule:** Code pertaining to the "inside" must **never leak into the "outside"**

---

### Domain-Driven Design (Eric Evans)

| Concept | Description |
|---------|-------------|
| **Bounded Contexts** | Strategic design element organizing large domains |
| **Aggregates** | Clusters of related entities treated as a single unit |
| **Entities** | Objects with distinct identity that persists |
| **Value Objects** | Objects defined by their attributes, not identity |
| **Domain Services** | Operations that don't belong to entities or value objects |

---

## 2. Architecture Decision Records (ADRs)

**Format: Y-Statement:**
> "We decided to [option] for [rationale], to achieve [positive consequences]. We would not do [alternatives] because [negative consequences]."

---

## 3. Code Quality Metrics & Thresholds

### Complexity Thresholds

| Metric | Threshold | Notes |
|--------|-----------|-------|
| **Cyclomatic Complexity** | <= 10 per function | Number of linearly independent paths |
| **Cognitive Complexity** | <= 15 per function | Weights branching by nesting depth |
| **Function Length (max)** | 40 lines | Industry standard |
| **Class Length (max)** | 200-500 lines | Depending on language |
| **Parameters** | <= 4 | More indicates need for parameter object |

### Coupling Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| **Afferent Coupling (Ca)** | Low | Classes that depend on a given class |
| **Efferent Coupling (Ce)** | Low | Classes that a given class depends on |
| **Instability** | < 0.3 | Ce / (Ca + Ce) - lower is more stable |

### Cohesion

| Metric | Target |
|--------|--------|
| **LCOM** | < 2 |
| **Single Responsibility** | 1 reason to change |

---

## 4. API Design Best Practices

### RESTful Design Rules

| Rule | Recommendation |
|------|----------------|
| **URI Naming** | Nouns for resources, plural (`/orders`) |
| **HTTP Methods** | GET (read), POST (create), PUT (replace), PATCH (update), DELETE (remove) |
| **Status Codes** | 200 (OK), 201 (Created), 400 (Bad Request), 404 (Not Found), 409 (Conflict) |
| **Versioning** | URI path (`/v1/...`) |
| **Pagination** | `?limit=25&offset=0` |
| **Filtering** | Query string (`?status=shipped`) |

---

## 5. Scalability Patterns

| Pattern | Purpose |
|---------|---------|
| **Circuit Breaker** | Handle faults that take variable time to fix |
| **Cache-Aside** | Load data on demand into cache |
| **Queue-Based Load Leveling** | Buffer between task and service |
| **Throttling** | Control resource consumption |
| **Retry** | Handle anticipated temporary failures |
| **Saga** | Manage consistency across microservices |
| **Event Sourcing** | Store state as append-only event series |
| **Bulkhead** | Isolate elements into pools so failure doesn't cascade |

---

## 6. Actionable Rules for LLM-Generated Code

### Function-Level Thresholds
```
MAX_FUNCTION_LINES = 40
MAX_CYCLOMATIC_COMPLEXITY = 10
MAX_COGNITIVE_COMPLEXITY = 15
MAX_PARAMETERS = 4
MAX_NESTING_DEPTH = 4
```

### Layer Dependency Rules
```
1. Entities → Use Cases → Interface Adapters → Frameworks
2. Dependencies point INWARD only
3. Cross-boundary calls use interfaces (dependency inversion)
4. DTOs cross boundaries, never domain entities
5. No framework imports in inner layers
```

### File Organization
```
/src
  /domain           # Entities, Value Objects, Domain Services
  /application      # Use Cases, Application Services
  /infrastructure   # Adapters, Repositories, External Services
  /presentation     # Controllers, DTOs, API definitions
```

---

## Sources

- [Clean Architecture - Uncle Bob](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Hexagonal Architecture - Alistair Cockburn](https://alistair.cockburn.us/hexagonal-architecture/)
- [ADR Documentation](https://adr.github.io/)
- [Microsoft Azure Architecture Patterns](https://learn.microsoft.com/en-us/azure/architecture/patterns/)
- [Microsoft Azure API Design Best Practices](https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design)
