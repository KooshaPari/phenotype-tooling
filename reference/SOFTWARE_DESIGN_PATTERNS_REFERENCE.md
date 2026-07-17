# Software Design Patterns Reference

## Table of Contents
1. [Gang of Four (GoF) Patterns](#1-gang-of-four-gof-patterns)
2. [Python-Specific Patterns](#2-python-specific-patterns)
3. [Enterprise Patterns](#3-enterprise-patterns)
4. [Modern Patterns](#4-modern-patterns)
5. [SOLID Principles](#5-solid-principles)
6. [Anti-Patterns to Avoid](#6-anti-patterns-to-avoid)
7. [Decision Trees](#7-decision-trees-for-choosing-patterns)

---

## 1. Gang of Four (GoF) Patterns

The GoF book "Design Patterns: Elements of Reusable Object-Oriented Software" (1994) established 23 foundational patterns.

### 1.1 Creational Patterns (6)

| Pattern | Intent | When to Use |
|---------|--------|-------------|
| **Abstract Factory** | Creates an instance of several families of classes | When you need to create families of related objects without specifying concrete classes |
| **Builder** | Separates object construction from its representation | When object creation involves many steps/parameters, especially with immutable objects |
| **Factory Method** | Creates an instance of several derived classes | When a class cannot anticipate the class of objects it must create |
| **Object Pool** | Recycles expensive-to-create objects | When instantiation is costly (DB connections, threads) |
| **Prototype** | Clones a fully initialized instance | When instantiation is expensive; clone existing configured objects |
| **Singleton** | Exactly one instance of a class | When exactly one instance controls resources (use module-level instead in Python) |

### 1.2 Structural Patterns (7)

| Pattern | Intent | When to Use |
|---------|--------|-------------|
| **Adapter** | Match interfaces of different classes | When integrating legacy code or third-party libraries |
| **Bridge** | Separates object's interface from its implementation | When you want to avoid permanent binding between abstraction and implementation |
| **Composite** | Tree structure of simple and composite objects | When clients need to treat individual and composite objects uniformly |
| **Decorator** | Add responsibilities dynamically | When you need to add behavior at runtime without modifying classes |
| **Facade** | Single class representing an entire subsystem | When you need a simplified interface to a complex subsystem |
| **Flyweight** | Fine-grained instance for efficient sharing | When you need to create huge numbers of similar objects |
| **Proxy** | Object representing another object | For lazy loading, access control, logging, remote access |

### 1.3 Behavioral Patterns (10)

| Pattern | Intent | When to Use |
|---------|--------|-------------|
| **Chain of Responsibility** | Pass request along chain of handlers | When multiple objects may handle a request |
| **Command** | Encapsulate request as an object | When you need to queue, log, or support undo operations |
| **Iterator** | Sequentially access collection elements | When you need to traverse without exposing underlying structure |
| **Mediator** | Define simplified communication between classes | When you want to reduce coupling between components |
| **Memento** | Capture and restore object's internal state | For undo mechanisms, checkpoints, snapshots |
| **Observer** | Notify change to multiple classes | When changes in one object need to notify others (publish-subscribe) |
| **State** | Alter behavior when state changes | When object behavior depends on internal state |
| **Strategy** | Encapsulate interchangeable algorithms | When you need different algorithms at runtime |
| **Template Method** | Defer steps of algorithm to subclass | When you have invariant algorithm structure with customizable steps |
| **Visitor** | New operation without changing classes | When you need operations across different object types |

---

## 2. Python-Specific Patterns

### 2.1 Unique Python Patterns

| Pattern | Description | When to Use |
|---------|-------------|-------------|
| **Borg** | Shared-state among instances (different identities, shared state) | When you want singleton-like behavior but need different object identities |
| **Lazy Evaluation** | Defer computation until value is needed | For expensive computations that may not be needed |
| **Pool** | Pre-instantiate and maintain group of reusable instances | For resource pools (DB connections, threads) |
| **Registry** | Track all subclasses for dynamic discovery | For plugin systems, auto-registration |

### 2.2 Python-Specific Implementations

**Dependency Injection (3 variants):**
```python
# Variant 1: Constructor Injection (RECOMMENDED)
class UserService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

# Variant 2: Setter Injection
class UserService:
    def set_repository(self, repository: UserRepository):
        self.repository = repository

# Variant 3: Protocol-based (Pythonic)
from typing import Protocol

class Repository(Protocol):
    def get(self, id): ...

class UserService:
    def __init__(self, repo: Repository):
        self.repo = repo
```

---

## 3. Enterprise Patterns

### 3.1 Repository Pattern
**Intent:** Mediates between domain and data mapping layers using a collection-like interface.

```python
class OrderRepository:
    def __init__(self, session):
        self.session = session

    def get_by_id(self, order_id):
        return self.session.query(Order).filter_by(id=order_id).first()

    def add(self, order):
        self.session.add(order)
```

### 3.2 Unit of Work Pattern
**Intent:** Maintains list of objects affected by a transaction and coordinates writing changes.

```python
class UnitOfWork:
    def __init__(self):
        self.new_objects = []
        self.dirty_objects = []
        self.removed_objects = []

    def register_new(self, obj):
        self.new_objects.append(obj)

    def commit(self):
        # Persist all changes atomically
        self.session.commit()
```

### 3.3 Service Layer Pattern
**Intent:** Defines application's boundary with a layer of services that establishes available operations.

```python
class OrderService:
    def __init__(self, order_repo: OrderRepository, unit_of_work: UnitOfWork):
        self.order_repo = order_repo
        self.uow = unit_of_work

    def place_order(self, order_data):
        order = Order.from_dict(order_data)
        self.uow.register_new(order)
        self.uow.commit()
        return order
```

---

## 4. Modern Patterns

### 4.1 CQRS (Command Query Responsibility Segregation)
**Intent:** Use different models to update vs read information.

**Caution:** "For most systems CQRS adds risky complexity" - Martin Fowler

```python
# Command Model (write)
class CreateOrderCommand:
    def __init__(self, customer_id, items):
        self.customer_id = customer_id
        self.items = items

# Query Model (read)
class OrderQuery:
    def get_order_summary(self, order_id):
        return self.read_db.query("SELECT * FROM order_summaries WHERE id = ?", order_id)
```

### 4.2 Event Sourcing
**Intent:** Store series of events instead of current state; rebuild state by replaying events.

```python
class EventStore:
    def append(self, event):
        self.events.append(event)

    def get_events_for(self, entity_id):
        return [e for e in self.events if e.entity_id == entity_id]
```

### 4.3 Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.state = "CLOSED"

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            raise CircuitOpenError()
        try:
            return func(*args, **kwargs)
        except Exception:
            self.failures += 1
            if self.failures >= self.failure_threshold:
                self.state = "OPEN"
            raise
```

---

## 5. SOLID Principles

### S - Single Responsibility
"A class should have one, and only one, reason to change."

### O - Open/Closed
"Open for extension, closed for modification."

### L - Liskov Substitution
"Objects of a superclass should be replaceable with objects of a subclass without breaking."

### I - Interface Segregation
"Prefer many small, specific interfaces over one large interface."

### D - Dependency Inversion
"Depend on abstractions, not concretions."

```python
# BAD - Depends on concrete class
class OrderService:
    def __init__(self):
        self.db = MySQLDatabase()

# GOOD - Depends on abstraction
class OrderService:
    def __init__(self, database: Database):
        self.db = database

class Database(ABC):
    @abstractmethod
    def save(self, entity): ...
```

---

## 6. Anti-Patterns to Avoid

| Anti-Pattern | Description | Solution |
|--------------|-------------|----------|
| **God Object** | Single class doing too much | Split into focused classes |
| **Singleton Abuse** | Overusing singletons globally | Use dependency injection |
| **Deep Inheritance** | Complex inheritance trees | Prefer composition |
| **Spaghetti Code** | Tangled, unstructured code | Refactor to clean functions |
| **Magic Numbers** | Unnamed numeric constants | Use named constants/enums |
| **Copy-Paste Programming** | Duplicating code | Extract to reusable functions |

---

## 7. Decision Trees

### Creational Pattern Selection
```
Need single instance?
├── YES → Use module-level singleton
└── NO
    ├── Complex construction? → Builder or Factory
    ├── Need prototype/cloning? → Prototype
    ├── Resource pooling? → Object Pool
    └── Related families? → Abstract Factory
```

### Structural Pattern Selection
```
Need to change interface? → Adapter
├── Need to add behavior at runtime? → Decorator
├── Need to represent hierarchy? → Composite
├── Need lazy/proxy access? → Proxy
├── Many similar objects? → Flyweight
└── Simplify complex system? → Facade
```

### Behavioral Pattern Selection
```
Need to select algorithm at runtime? → Strategy
├── Need to vary by state? → State
├── Need to notify multiple objects? → Observer
├── Need to queue/execute later? → Command
├── Need undo capability? → Memento
└── Reduce coupling? → Mediator
```

---

## Key Takeaways

1. **Patterns are tools, not rules** - Understand trade-offs before applying
2. **Start simple** - Don't over-engineer
3. **Python-specific** - Modules are already singletons; favor composition over inheritance
4. **Avoid Golden Hammer** - Don't apply patterns where simple code suffices

## Sources

- [faif/python-patterns GitHub](https://github.com/faif/python-patterns)
- [Martin Fowler - EAA Catalog](https://martinfowler.com/eaaCatalog/)
- [Microsoft Azure - Event Sourcing Pattern](https://learn.microsoft.com/en-us/azure/architecture/patterns/event-sourcing)
- [Chris Richardson - Microservices Patterns](https://microservices.io/patterns/)
