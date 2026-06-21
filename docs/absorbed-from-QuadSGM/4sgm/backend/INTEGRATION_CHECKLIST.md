# Integration Checklist - Repository Pattern

Use this checklist to integrate the repository pattern into your FastAPI application.

## Pre-Integration

- [ ] Review `repositories/README.md` for architecture overview
- [ ] Review `repositories/USAGE_GUIDE.md` for usage patterns
- [ ] Review `repositories/examples.py` for real-world examples
- [ ] Verify Python 3.8+ installed (for typing.Protocol)

## Step 1: Install Dependencies

```bash
# If using Supabase adapter (production)
pip install supabase

# For testing (already installed)
pip install pytest pytest-asyncio
```

- [ ] Supabase installed (for production)
- [ ] Pytest/pytest-asyncio installed (for tests)

## Step 2: Environment Configuration

### Development
```bash
# Use mock adapter (no database needed)
export REPOSITORY_ADAPTER=mock
```

### Testing
```bash
# Use mock adapter (all tests)
export REPOSITORY_ADAPTER=mock
```

### Production
```bash
# Use Supabase adapter
export REPOSITORY_ADAPTER=supabase
export SUPABASE_URL=https://project.supabase.co
export SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

- [ ] Development environment configured
- [ ] Testing environment configured
- [ ] Production environment configured

## Step 3: Verify Installation

```bash
# Test import
python -c "from repositories.dependencies import get_product_repo; print('OK')"

# Run tests
pytest 4sgm/backend/repositories/test_repositories.py -v
```

- [ ] Imports work without errors
- [ ] All 27 tests pass
- [ ] No database errors (using mock)

## Step 4: Update FastAPI App

### Basic Integration

```python
# In app.py or main.py
from fastapi import FastAPI, Depends
from repositories.dependencies import get_product_repo

app = FastAPI()

@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    repo = Depends(get_product_repo)
):
    """Get product by ID."""
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

- [ ] Import dependencies in app.py
- [ ] Add get_product_repo dependency to at least one route
- [ ] Test route works with mock adapter

### Full Integration (Optional)

```python
# Create service layer
from repositories.dependencies import get_product_repo

class ProductService:
    def __init__(self, repo):
        self.repo = repo

    async def get_product(self, product_id: str):
        return await self.repo.get(product_id)

    async def search_products(self, query: str):
        return await self.repo.search(query)

# Use in routes
@app.get("/products/search")
async def search(
    q: str,
    repo = Depends(get_product_repo)
):
    service = ProductService(repo)
    return await service.search_products(q)
```

- [ ] Create service classes if needed
- [ ] Inject repositories into services
- [ ] Test service methods work

## Step 5: Test Integration

### With Mock Adapter

```bash
export REPOSITORY_ADAPTER=mock
pytest tests/ -v
```

- [ ] All existing tests still pass
- [ ] Repository tests pass (27 tests)
- [ ] No database connection errors

### With Supabase (Production)

```bash
export REPOSITORY_ADAPTER=supabase
export SUPABASE_URL=https://project.supabase.co
export SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Test with real database
python -m pytest tests/ -v
```

- [ ] Set Supabase environment variables
- [ ] All tests pass with real database
- [ ] No connection errors

## Step 6: Migrate Existing Routes (Optional)

For each route currently using direct database access:

### Before
```python
@app.get("/products/{product_id}")
async def get_product(product_id: str, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404)
    return product
```

### After
```python
@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    repo = Depends(get_product_repo)
):
    product = await repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404)
    return product
```

- [ ] Migrate product routes
- [ ] Migrate cart routes
- [ ] Migrate order routes
- [ ] Migrate customer routes
- [ ] Migrate shipping routes
- [ ] Migrate RFQ routes

## Step 7: Create Custom Adapters (If Needed)

If you need Oracle, SAP, MongoDB, etc.:

1. Create adapter file: `repositories/adapters/custom.py`
2. Implement all 6 repository classes
3. Update `repositories/dependencies.py`
4. Test with `REPOSITORY_ADAPTER=custom`

- [ ] Custom adapter created (if needed)
- [ ] All protocol methods implemented
- [ ] Dependencies.py updated
- [ ] Tested with environment variable

## Step 8: Documentation

- [ ] Add repository documentation to project docs
- [ ] Train team on repository pattern
- [ ] Link to `repositories/README.md` in project docs
- [ ] Link to `repositories/USAGE_GUIDE.md` in code comments

## Step 9: Deployment

### Staging
```bash
export REPOSITORY_ADAPTER=supabase
export SUPABASE_URL=...
export SUPABASE_KEY=...

# Deploy and test
python app.py
```

- [ ] Deploy to staging environment
- [ ] Test all routes in staging
- [ ] Monitor logs for errors

### Production
```bash
export REPOSITORY_ADAPTER=supabase
export SUPABASE_URL=...
export SUPABASE_KEY=...

# Deploy
sst deploy --stage production
```

- [ ] Deploy to production
- [ ] Monitor application logs
- [ ] Verify database connectivity
- [ ] Test critical routes

## Troubleshooting

### Import Errors
```
ModuleNotFoundError: No module named 'repositories'
```
**Solution**: Verify `repositories/` directory exists with `__init__.py`

### "No module named 'supabase'"
```
ImportError: No module named 'supabase'
```
**Solution**: Install supabase library
```bash
pip install supabase
```

### Database Connection Errors
```
SUPABASE_URL and SUPABASE_KEY environment variables required
```
**Solution**: Set environment variables or use mock adapter
```bash
export REPOSITORY_ADAPTER=mock
```

### Async/Await Issues
```
TypeError: object coroutine can't be used in 'await' expression
```
**Solution**: Ensure all repository calls use `await`
```python
# Correct
product = await repo.get(id)

# Wrong
product = repo.get(id)  # Missing await!
```

### Tests Failing with Database Errors
**Solution**: Use mock adapter for tests
```bash
export REPOSITORY_ADAPTER=mock
pytest tests/ -v
```

## Post-Integration Checklist

- [ ] All routes updated to use repositories
- [ ] All tests passing with mock adapter
- [ ] All tests passing with Supabase adapter
- [ ] No direct database imports in routes
- [ ] Services use dependency injection
- [ ] Error handling consistent across routes
- [ ] Logging configured in repositories
- [ ] Documentation updated
- [ ] Team trained on pattern
- [ ] Deployed to staging successfully
- [ ] Deployed to production successfully

## Performance Checklist

- [ ] Pagination implemented for list endpoints
- [ ] N+1 queries avoided (use relationship loading)
- [ ] Indexes configured in Supabase
- [ ] Connection pooling enabled (Supabase client)
- [ ] Caching added at service layer (if needed)
- [ ] Load tested with production data
- [ ] Monitoring configured for slow queries

## Security Checklist

- [ ] No hardcoded API keys (use environment variables)
- [ ] Supabase RLS policies configured (if applicable)
- [ ] Input validation at route level
- [ ] Error messages don't leak sensitive data
- [ ] Logging doesn't include sensitive data
- [ ] Service role keys never in src/ or app/
- [ ] JWT validation configured (if using auth)

## Future Enhancements

Consider these improvements after initial integration:

- [ ] Add caching layer (Redis adapter)
- [ ] Add audit logging
- [ ] Add soft deletes
- [ ] Add transaction support
- [ ] Add bulk operations
- [ ] Add query builders for complex filters
- [ ] Add multi-tenancy support
- [ ] Add GraphQL adapter

## Support

For issues or questions:
1. Check `repositories/README.md`
2. Check `repositories/USAGE_GUIDE.md`
3. Review `repositories/examples.py`
4. Check test examples in `repositories/test_repositories.py`
5. Review protocol definitions in `repositories/base.py`

## Quick Reference

### Common Commands

```bash
# Run all repository tests
pytest repositories/test_repositories.py -v

# Run specific test
pytest repositories/test_repositories.py::test_product_create -v

# Check imports
python -c "from repositories.dependencies import *; print('OK')"

# Development (mock)
export REPOSITORY_ADAPTER=mock
python app.py

# Production (Supabase)
export REPOSITORY_ADAPTER=supabase
export SUPABASE_URL=...
export SUPABASE_KEY=...
python app.py
```

### File Locations

| File | Purpose | Location |
|------|---------|----------|
| Protocol definitions | Repository contracts | `repositories/base.py` |
| Supabase implementations | Production adapter | `repositories/adapters/supabase.py` |
| Mock implementations | Testing adapter | `repositories/adapters/mock.py` |
| Dependency injection | FastAPI integration | `repositories/dependencies.py` |
| Documentation | How to use | `repositories/USAGE_GUIDE.md` |
| Architecture guide | Overview | `repositories/README.md` |
| Examples | Real usage | `repositories/examples.py` |
| Tests | Test suite | `repositories/test_repositories.py` |

## Success Criteria

- [ ] All routes use repositories (not direct database access)
- [ ] All tests pass with mock adapter
- [ ] All tests pass with Supabase adapter
- [ ] No database setup needed for tests
- [ ] No hardcoded API keys in code
- [ ] Full documentation available
- [ ] Team trained and confident
- [ ] Deployed to staging successfully
- [ ] Deployed to production successfully
- [ ] Can swap Supabase for Oracle with just environment variable change

**Integration Complete!**
