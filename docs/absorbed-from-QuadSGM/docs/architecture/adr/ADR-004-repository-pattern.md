# ADR-004: Repository Pattern for Enterprise Data Abstraction

## Status
Accepted

## Context

The 4SGM Wholesale Chatbot requires a data access layer to interact with multiple enterprise systems:
1. **SQL Server**: Product catalog, inventory, pricing (primary data source)
2. **Supabase PostgreSQL**: Vector embeddings, conversation history, logs
3. **Custom APIs**: ERP system, payment processing, fulfillment
4. **Third-party SaaS**: Shipping providers (FedEx, UPS APIs), market data

Each system has different:
- Connection patterns (ODBC, TCP, HTTP, REST)
- Query complexity (simple lookups vs. complex aggregations)
- Performance characteristics (sub-100ms vs. multi-second)
- Error handling requirements
- Caching strategies

The 25+ MCP tools need consistent, testable access to this data without coupling to implementation details. The challenge is:
- **Testability**: Mock data sources easily for unit tests
- **Flexibility**: Swap implementations (SQL Server → PostgreSQL) without tool code changes
- **Maintainability**: Single source of truth for complex queries
- **Scalability**: Add caching, connection pooling, read replicas transparently
- **Monitoring**: Instrumentation points for latency, error rate tracking

The decision is between:
1. **Direct Driver Access**: MCP tools call ODBC/psycopg2 directly (simple but tightly coupled)
2. **ORM Layer** (SQLAlchemy): Abstract schema, lose some SQL performance, complex mapping
3. **Repository Pattern**: Clean interfaces, testable, flexible implementations
4. **Data Mapper Pattern**: Heavy abstraction, steep learning curve
5. **QueryBuilder Library** (SQLAlchemy Core): Balance simplicity and abstraction

We need an enterprise-grade pattern that scales with the business while remaining understandable and maintainable.

## Decision

We selected the **Repository Pattern** with the following structure:

### Architecture: Repository + Service Layer

```
MCP Tool Layer (FastMCP)
       ↓
Service Layer (Business Logic)
       ↓
Repository Layer (Data Abstraction)
       ↓
Data Source Implementations
  ├─ SQLServerRepository
  ├─ SupabaseRepository
  ├─ ShippingAPIsRepository
  └─ CacheRepository (Decorator)
```

### Core Repository Interfaces

```python
# src/repositories/interfaces.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
from dataclasses import dataclass

T = TypeVar('T')

@dataclass
class Product:
    """Domain model - independent of database representation"""
    id: str
    name: str
    sku: str
    price: float
    stock_quantity: int
    supplier_id: str

@dataclass
class Order:
    id: str
    customer_id: str
    items: list[dict]
    total: float
    status: str
    created_at: str

class ProductRepository(ABC):
    """Repository interface for product data access"""

    @abstractmethod
    async def search(self, query: str, max_price: float | None = None) -> list[Product]:
        """Search products by name, SKU, category"""
        pass

    @abstractmethod
    async def get_by_id(self, product_id: str) -> Product | None:
        """Get product by ID"""
        pass

    @abstractmethod
    async def get_bulk_pricing(self, product_id: str, quantity: int) -> dict:
        """Get tiered pricing for bulk orders"""
        pass

    @abstractmethod
    async def check_stock(self, product_id: str, quantity: int) -> bool:
        """Check if product has sufficient stock"""
        pass

class OrderRepository(ABC):
    """Repository interface for order data access"""

    @abstractmethod
    async def create(self, customer_id: str, items: list[dict]) -> Order:
        """Create new order"""
        pass

    @abstractmethod
    async def get_by_id(self, order_id: str) -> Order | None:
        """Get order details"""
        pass

    @abstractmethod
    async def list_by_customer(self, customer_id: str) -> list[Order]:
        """List all orders for customer"""
        pass

    @abstractmethod
    async def update_status(self, order_id: str, status: str) -> bool:
        """Update order status"""
        pass

class VectorRepository(ABC):
    """Repository interface for vector/embedding data"""

    @abstractmethod
    async def search(self, query_vector: list[float], limit: int = 5) -> list[dict]:
        """Semantic search using vector similarity"""
        pass

    @abstractmethod
    async def store(self, text: str, vector: list[float], metadata: dict) -> str:
        """Store embedding with metadata"""
        pass
```

### Implementation: SQL Server Repository

```python
# src/repositories/sqlserver.py
import pyodbc
from contextlib import asynccontextmanager
import logging

logger = logging.getLogger(__name__)

class SQLServerProductRepository(ProductRepository):
    """Product data from SQL Server"""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    async def search(self, query: str, max_price: float | None = None) -> list[Product]:
        """
        Search products by name, SKU, or category.
        Uses full-text search in SQL Server for performance.
        """
        async with self._get_connection() as conn:
            sql = """
            SELECT TOP 20
                p.ProductID,
                p.ProductName,
                p.SKU,
                p.CurrentPrice,
                i.QuantityOnHand,
                p.SupplierID
            FROM Products p
            JOIN Inventory i ON p.ProductID = i.ProductID
            WHERE FREETEXT(p.ProductName, @query)
               OR p.SKU LIKE @sku_pattern
               OR FREETEXT(p.Description, @query)
            """

            params = {"query": query, "sku_pattern": f"%{query}%"}

            if max_price is not None:
                sql += " AND p.CurrentPrice <= @max_price"
                params["max_price"] = max_price

            sql += " ORDER BY p.CurrentPrice ASC"

            cursor = await conn.cursor()
            await cursor.execute(sql, params)

            results = []
            for row in await cursor.fetchall():
                results.append(Product(
                    id=str(row[0]),
                    name=row[1],
                    sku=row[2],
                    price=float(row[3]),
                    stock_quantity=int(row[4]),
                    supplier_id=str(row[5])
                ))

            logger.info(f"Product search: query={query}, results={len(results)}")
            return results

    @asynccontextmanager
    async def _get_connection(self):
        """Connection pool management"""
        try:
            conn = pyodbc.connect(self.connection_string)
            yield conn
        finally:
            if conn:
                conn.close()
```

### Implementation: Supabase Repository (Vector Search)

```python
# src/repositories/supabase.py
from supabase import create_client
import numpy as np

class SupabaseVectorRepository(VectorRepository):
    """Vector embedding storage and semantic search"""

    def __init__(self, url: str, key: str):
        self.client = create_client(url, key)

    async def search(self, query_vector: list[float], limit: int = 5) -> list[dict]:
        """
        Semantic search using pgvector similarity.
        Uses cosine similarity for product/content embeddings.
        """
        # Normalize vector (pgvector requirement)
        vector = np.array(query_vector)
        vector = vector / np.linalg.norm(vector)

        response = self.client.rpc(
            'match_documents',
            {
                'query_embedding': vector.tolist(),
                'match_threshold': 0.7,  # Cosine similarity threshold
                'match_count': limit
            }
        ).execute()

        results = []
        for doc in response.data:
            results.append({
                'id': doc['id'],
                'content': doc['content'],
                'similarity': float(doc['similarity']),
                'metadata': doc['metadata']
            })

        logger.info(f"Vector search: results={len(results)}, threshold=0.7")
        return results

    async def store(self, text: str, vector: list[float], metadata: dict) -> str:
        """Store embedding with metadata"""
        response = self.client.table('documents').insert({
            'content': text,
            'embedding': vector,
            'metadata': metadata
        }).execute()

        return response.data[0]['id']
```

### Service Layer: Dependency Injection

```python
# src/services/product_service.py
import logging

logger = logging.getLogger(__name__)

class ProductService:
    """Business logic for product operations"""

    def __init__(
        self,
        product_repo: ProductRepository,
        vector_repo: VectorRepository,
        cache: dict = None  # Optional caching
    ):
        self.product_repo = product_repo
        self.vector_repo = vector_repo
        self.cache = cache or {}

    async def search_products(self, query: str, max_price: float | None = None) -> dict:
        """
        Search products with intelligent routing:
        - Keyword search via SQL (fast, structured)
        - Fallback to semantic search if low results
        """
        # Try keyword search first
        products = await self.product_repo.search(query, max_price)

        if len(products) >= 3:
            logger.info(f"Found {len(products)} products via keyword search")
            return {
                "products": products,
                "search_type": "keyword",
                "count": len(products)
            }

        # Fallback to semantic search
        logger.info(f"Low results ({len(products)}), trying semantic search")
        embeddings = await self.vector_repo.search([0.1]*1536, limit=5)

        semantic_products = [
            await self.product_repo.get_by_id(emb['metadata']['product_id'])
            for emb in embeddings
        ]

        return {
            "products": [p for p in semantic_products if p],
            "search_type": "semantic",
            "count": len([p for p in semantic_products if p])
        }

    async def get_bulk_pricing(self, product_id: str, quantity: int) -> dict:
        """Get tiered pricing for bulk orders"""
        product = await self.product_repo.get_by_id(product_id)
        if not product:
            raise ValueError(f"Product {product_id} not found")

        pricing = await self.product_repo.get_bulk_pricing(product_id, quantity)

        return {
            "product_id": product_id,
            "quantity": quantity,
            "unit_price": pricing['unit_price'],
            "total_price": pricing['total_price'],
            "discount_percent": pricing['discount_percent']
        }
```

### MCP Tool Integration

```python
# mcp_server/tools/product_tools.py
from fastmcp import FastMCP
from src.services.product_service import ProductService

mcp = FastMCP(...)

# Dependency injection
product_service = ProductService(
    product_repo=SQLServerProductRepository(connection_string),
    vector_repo=SupabaseVectorRepository(url, key)
)

@mcp.tool()
async def search_products(query: str, max_price: float = None) -> dict:
    """Search products by name, SKU, or category"""
    result = await product_service.search_products(query, max_price)
    return result

@mcp.tool()
async def get_bulk_pricing(product_id: str, quantity: int) -> dict:
    """Get tiered pricing for bulk orders"""
    pricing = await product_service.get_bulk_pricing(product_id, quantity)
    return pricing
```

### Testing: Mock Repositories

```python
# tests/repositories/test_mock.py
from unittest.mock import AsyncMock

class MockProductRepository(ProductRepository):
    """Mock repository for testing"""

    def __init__(self):
        self.products = {
            "PROD-001": Product(
                id="PROD-001",
                name="Laptop Pro 15",
                sku="LP-15-256",
                price=999.99,
                stock_quantity=50,
                supplier_id="SUP-001"
            )
        }

    async def search(self, query: str, max_price: float | None = None) -> list[Product]:
        results = [p for p in self.products.values() if query.lower() in p.name.lower()]
        if max_price:
            results = [p for p in results if p.price <= max_price]
        return results

    async def get_by_id(self, product_id: str) -> Product | None:
        return self.products.get(product_id)

# Test service with mock
async def test_product_search():
    mock_repo = MockProductRepository()
    mock_vector_repo = AsyncMock(spec=VectorRepository)

    service = ProductService(mock_repo, mock_vector_repo)

    results = await service.search_products("Laptop", max_price=1500)

    assert len(results["products"]) == 1
    assert results["products"][0].name == "Laptop Pro 15"
    assert results["search_type"] == "keyword"
```

## Consequences

### Positive
1. **Testability**: Mock repositories enable unit testing without database dependencies
2. **Flexibility**: Swap SQL Server for PostgreSQL by changing repository implementation
3. **Decoupling**: MCP tools don't know about database details; only know about domain models
4. **Maintainability**: Complex queries live in single place; easy to optimize
5. **Scalability**: Add caching, connection pooling, read replicas without tool code changes
6. **Consistency**: All data access goes through repositories; single audit point
7. **Reusability**: Services can be used by multiple tools (reduce duplication)
8. **Clear Contracts**: Repository interfaces make data contracts explicit
9. **Error Handling**: Centralized error handling in repository layer
10. **Performance**: Easy to add indexes, connection pooling, caching transparently

### Negative
1. **Boilerplate**: More code upfront for interfaces, implementations, factories
2. **Learning Curve**: Team needs to understand repository pattern concepts
3. **Indirection**: Extra abstraction layer adds complexity to trace execution
4. **Performance Overhead**: Small latency from abstraction (negligible ~1-2ms)
5. **Flexibility Cost**: Repository pattern assumes interfaces are stable; large changes need refactoring

### Mitigation Strategies
1. **Boilerplate**: Use code generation templates for common repository patterns
2. **Learning**: Provide documentation and examples; pair new team members
3. **Indirection**: Clear naming and logging make execution traces obvious
4. **Performance**: Use async/await and connection pooling; profile critical paths
5. **Flexibility**: Regular design reviews; evolve interfaces as business requirements change

## Implementation Patterns

### Decorator Pattern: Add Caching

```python
# src/repositories/cached.py
class CachedProductRepository(ProductRepository):
    """Product repository with transparent caching"""

    def __init__(self, repository: ProductRepository, cache_ttl: int = 300):
        self.repository = repository
        self.cache = {}
        self.cache_ttl = cache_ttl

    async def search(self, query: str, max_price: float | None = None) -> list[Product]:
        cache_key = f"search:{query}:{max_price}"

        if cache_key in self.cache:
            logger.info(f"Cache hit: {cache_key}")
            return self.cache[cache_key]

        products = await self.repository.search(query, max_price)
        self.cache[cache_key] = products

        # Simple TTL (production use Redis)
        import asyncio
        asyncio.create_task(self._expire_cache(cache_key, self.cache_ttl))

        return products

    async def _expire_cache(self, key: str, ttl: int):
        await asyncio.sleep(ttl)
        self.cache.pop(key, None)
```

### Factory Pattern: Environment-based Repository Selection

```python
# src/repositories/factory.py
class RepositoryFactory:
    """Factory for creating repositories based on environment"""

    @staticmethod
    def create_product_repository(env: str) -> ProductRepository:
        if env == "production":
            repo = SQLServerProductRepository(
                connection_string=os.getenv("SQLSERVER_CONNECTION")
            )
            return CachedProductRepository(repo)  # Add caching in production

        elif env == "staging":
            return SQLServerProductRepository(
                connection_string=os.getenv("SQLSERVER_CONNECTION_STAGING")
            )

        else:  # testing
            return MockProductRepository()

# Usage
repo = RepositoryFactory.create_product_repository(os.getenv("ENVIRONMENT"))
```

## References
- [Repository Pattern - Microsoft Docs](https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design)
- [SQLAlchemy ORM vs. Core](https://docs.sqlalchemy.org/en/20/)
- [Dependency Injection in Python](https://python-dependency-injector.ets-labs.org/)
- [Async SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Testing with Mock Objects](https://docs.python.org/3/library/unittest.mock.html)

## Implementation Checklist
- [x] Repository interfaces defined for all data sources
- [x] SQL Server repository implemented with async support
- [x] Supabase vector repository implemented
- [x] Service layer with business logic
- [x] Dependency injection configured
- [x] Mock repositories for testing
- [x] Cache decorator for performance
- [x] Error handling across all repositories
- [x] Logging instrumentation
- [x] Connection pooling configured
- [x] E2E tests with real databases

## Questions & Decisions Log

**Q: Why not use SQLAlchemy ORM?**
A: SQLAlchemy adds abstraction we don't need for SQL Server/Postgres mix. We use Core for queries we control, repositories for services. ORM would hide performance-critical queries.

**Q: Should repositories be async?**
A: Yes. All data access is async to allow concurrent tool execution. One slow tool doesn't block others.

**Q: What if we need to add a new data source (e.g., REST API)?**
A: Create new repository implementation that satisfies interface. Service and tool code don't change.

**Q: How do we handle transaction boundaries?**
A: Repositories handle their own transactions. Services can request "unit of work" from factory if cross-repository transactions needed.

**Q: What about query performance?**
A: Repositories own query optimization. We profile production traces in Langfuse; optimize hottest queries. Caching decorator available for read-heavy operations.
