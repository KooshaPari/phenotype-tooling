# Testing Strategies Reference

## 1. TDD (Test-Driven Development)

### Red/Green/Refactor Cycle
1. **Red**: Write failing test
2. **Green**: Write minimal code to pass
3. **Refactor**: Improve code quality

### pytest Example
```python
# test_calculator.py
import pytest
from calculator import Calculator

class TestCalculator:
    def test_add_two_numbers(self):
        # Arrange
        calc = Calculator()
        # Act
        result = calc.add(2, 3)
        # Assert
        assert result == 5
```

---

## 2. BDD (Behavior-Driven Development)

### Gherkin Syntax
```gherkin
Feature: User Authentication
  Scenario: Successful login
    Given the user "alice" exists with password "secret123"
    When I log in with username "alice" and password "secret123"
    Then I should be redirected to the dashboard
```

### pytest-bdd
```python
from pytest_bdd import scenario, given, when, then

@scenario('login.feature', 'Successful login')
def test_login():
    pass
```

---

## 3. Testing Pyramid

| Level | Ratio | Purpose |
|-------|-------|---------|
| Unit | 70% | Fast, isolated tests |
| Integration | 20% | Component interactions |
| E2E | 10% | Full user scenarios |

---

## 4. Property-Based Testing (Hypothesis)

```python
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    """Addition should be commutative"""
    assert a + b == b + a

@given(st.lists(st.integers()))
def test_list_sorting_preserves_length(lst):
    """Sorting preserves list length"""
    assert len(sorted(lst)) == len(lst)
```

---

## 5. Mutation Testing

```bash
# Python with mutmut
pip install mutmut
mutmut run
mutmut show

# Target: >80% mutation score
```

---

## 6. Contract Testing (Pact)

### Consumer
```python
from pact import Consumer, Provider

pact = Consumer('UserClient').has_pact_with(Provider('UserService'))
pact.start_service()

result = pact.get_user(user_id=123)
result.status = 200
result.json() == {'id': 123, 'name': 'Test User'}
```

---

## Test Layout

```
project/
├── src/mypkg/
│   └── calculator.py
├── tests/
│   ├── unit/test_calculator.py
│   ├── integration/test_calculator_db.py
│   └── e2e/test_user_flow.py
└── pyproject.toml
```

---

## pytest Configuration

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = ["--strict-markers", "--tb=short"]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

---

## 7. Flaky Test Prevention

### Root Causes
| Cause | Solution |
|-------|----------|
| Async timing | Use event-based waiting, not arbitrary sleeps |
| Shared state | Isolate test data, reset between tests |
| External dependencies | Mock external services, use test containers |
| Floating point | Use approximate equality (`pytest.approx`) |
| Date/time | Use freezegun or time mocking |
| Random data | Seed random generators, use property-based testing |

### Event-Based Waiting Pattern
```python
# ❌ BAD: Arbitrary sleep
def test_async_operation():
    trigger_operation()
    time.sleep(2)  # Flaky!
    assert result.ready()

# ✅ GOOD: Poll with timeout
def test_async_operation():
    trigger_operation()
    wait_for(lambda: result.ready(), timeout=5)
    assert result.success()
```

---

## 8. Test Maturity Model

| Level | Coverage | Automation | Types | CI Integration |
|-------|----------|------------|-------|----------------|
| 1. MVP | 60% | Manual + CI | Unit | Basic |
| 2. Production | 80% | Full CI/CD | Unit + Integration | Gates |
| 3. Advanced | 90% | Full | + Contract, Mutation | Quality gates |
| 4. Mission-Critical | 95% | Full | + Chaos, Load | Multiple gates |
| 5. High-Reliability | 95%+ | Full | + Formal methods | Canary gates |

---

## 9. Mutation Testing

**Purpose**: Verify tests actually catch bugs

```bash
# Python: mutmut
mutmut run --paths-to-mutate=src/
mutmut results  # Show mutation score

# JavaScript: Stryker
npx stryker run

# Java: PIT
mvn org.pitest:pitest-maven:mutationCoverage
```

**Target**: >80% mutation score (tests kill 80%+ of mutants)

---

## 10. Chaos Testing

**Purpose**: Verify resilience under failure conditions

```python
# Using chaoslib
from chaoslib import Settings
from chaoslib.runner import Runner

experiment = {
    "title": "API Latency Test",
    "steady-state-hypothesis": {
        "title": "API responds within 500ms",
        "probes": [
            {"type": "python", "module": "myprobes", "func": "api_latency", "tolerance": 500}
        ]
    },
    "method": [
        {"type": "action", "name": "add_latency", "provider": {...}}
    ]
}
```

**Tools**: Chaos Monkey, Gremlin, Chaos Toolkit, Litmus

---

## 11. Snapshot/Golden File Testing

**Purpose**: Detect unintended output changes

```python
import pytest
from syrupy import SnapshotAssertion

def test_api_response(snapshot: SnapshotAssertion):
    response = client.get("/api/users/123")
    assert response.json() == snapshot
```

**When to use**: API responses, generated code, configuration files

---

## 12. Coverage Targets by Project Type

| Project Type | Line Coverage | Branch Coverage | Mutation Score |
|--------------|---------------|-----------------|----------------|
| Library | 90% | 85% | 80% |
| Web Service | 80% | 75% | 70% |
| CLI Tool | 80% | 75% | 75% |
| Data Pipeline | 75% | 70% | 65% |
| Critical Path | 95% | 90% | 85% |

---

## Summary

| Type | Use When |
|------|----------|
| TDD | Building new features |
| BDD | Collaboration with stakeholders |
| Unit | Core business logic |
| Integration | Database, API interactions |
| E2E | Critical user journeys |
| Property-Based | Complex transformations, edge cases |
| Contract | Microservices, API clients |
| Mutation | Verify test quality |
| Chaos | Verify system resilience |
| Snapshot | Detect unintended changes |

---

## Production Checklist

- [ ] Test coverage ≥80% (statements + branches)
- [ ] Mutation score ≥70%
- [ ] All E2E tests passing
- [ ] No flaky tests in last 30 days
- [ ] CI pipeline with quality gates
- [ ] Contract tests for all service boundaries
- [ ] Load tests for critical paths
- [ ] Security tests (SAST, dependency scan)
