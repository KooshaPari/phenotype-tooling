# Coverage Quick Reference

**Project:** 4SGM
**Last Updated:** 2026-02-23
**Overall Coverage:** 52.2%

## Quick Stats

| Metric | Value |
|--------|-------|
| Total Tests | 431 |
| Passed | 395 ✅ |
| Failed | 2 (OpenAI key) |
| Skipped | 3 |
| Coverage | 52.2% |
| Backend Tests | 400 |
| MCP Tests | 36 |
| Execution Time | ~17s |

## Test Coverage by Module

| Module | Tests | Coverage |
|--------|-------|----------|
| test_mcp_tools (all 7) | 56 | 100% |
| test_models | 18 | 100% |
| test_repositories | 13 | 100% |
| test_sse_streaming | 17 | 99% |
| test_pricing_discount_chain | 21 | 98% |
| test_shipping_chain | 19 | 98% |
| test_product_cart_order_chain | 24 | 97% |
| test_rfq_chain | 22 | 97% |
| test_session_management | 20 | 97% |
| test_error_handling | 27 | 96% |
| test_langfuse_integration | 13 | 96% |
| test_error_recovery_consistency | 24 | 93% |
| test_api_endpoints | 28 | 92% |
| test_database | 15 | 90% |
| test_exceptions | 21 | 95% |

## Run Tests

```bash
# All tests
python -m pytest 4sgm/backend/tests/ 4sgm/mcp_server/tests/ -v --cov=backend --cov-report=html

# Backend only
python -m pytest 4sgm/backend/tests/ -q --cov=backend --cov-report=term-missing

# MCP only
python -m pytest 4sgm/mcp_server/tests/ -v

# Specific test
python -m pytest 4sgm/backend/tests/unit/test_models.py -v
```

## View Reports

- **HTML:** Open `htmlcov/index.html` in browser
- **JSON:** `coverage.json` (machine-readable)
- **Terminal:** Run with `--cov-report=term-missing`

## Known Issues

1. **2 OpenAI API failures** in `test_langfuse_integration.py`
   - Requires OPENAI_API_KEY environment variable
   - Not a code defect, just missing external credentials

## Next: Set Coverage Target

```bash
# Example: Enforce 80% coverage on new code
pytest --cov=backend --cov-fail-under=80
```

See `TEST_COVERAGE_REPORT.md` for full details.
