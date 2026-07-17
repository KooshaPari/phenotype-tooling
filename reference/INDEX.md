# Global Reference Documentation Index

This document provides a hierarchical index of all reference documentation available for LLM code generation. Each category is linked to relevant thegent agents for hyperspecialization.

---

## Table of Contents
1. [General Reference](#1-general-reference)
2. [Domain-Specific](#2-domain-specific)
3. [Language-Specific](#3-language-specific)
4. [Application-Specific](#4-application-specific)
5. [Agent ↔ Reference Mapping](#5-agent--reference-mapping)

---

## 1. General Reference

| Document | Path | Description |
|----------|------|-------------|
| **UI Design Principles** | `UI_DESIGN_PRINCIPLES_REFERENCE.md` | Core UI heuristics, layout grids, component specs, accessibility |
| **Software Architecture** | `SOFTWARE_ARCHITECTURE_REFERENCE.md` | Clean/Hexagonal/DDD, metrics thresholds, API design |
| **Design Patterns** | `SOFTWARE_DESIGN_PATTERNS_REFERENCE.md` | GoF, SOLID, anti-patterns, decision trees |

---

## 2. Domain-Specific

### Data Engineering
| Document | Path | Agents |
|----------|------|--------|
| Data Engineering | `DATA_ENGINEERING_REFERENCE.md` | `research-scout`, `performance-tuner` (pipeline optimization) |

### Microservices & Distributed Systems
| Document | Path | Agents |
|----------|------|--------|
| Microservices Architecture | `MICROSERVICES_ARCHITECTURE_REFERENCE.md` | `software-planning-architect`, `component-modularity-architect`, `dependency-risk-manager` |

### Frontend Architecture
| Document | Path | Agents |
|----------|------|--------|
| Frontend Architecture | `FRONTEND_ARCHITECTURE_REFERENCE.md` | `performance-optimization-specialist`, `qa-test-coverage-expert` |

### Authentication & Authorization
| Document | Path | Agents |
|----------|------|--------|
| Auth & AuthZ | `AUTHENTICATION_AUTHORIZATION_REFERENCE.md` | `security-auditor`, `atoms-security-reviewer` |

### Performance
| Document | Path | Agents |
|----------|------|--------|
| Performance Optimization | `performance/PERFORMANCE_OPTIMIZATION.md` | `performance-optimization-specialist`, `performance-tuner` |

### Testing
| Document | Path | Agents |
|----------|------|--------|
| Testing Strategies | `testing/TESTING_STRATEGIES.md` | `test-strategist`, `qa-test-coverage-expert`, `qa-verification-lead` |

### Security
| Document | Path | Agents |
|----------|------|--------|
| Security Best Practices | `security/SECURITY_BEST_PRACTICES.md` | `security-auditor`, `atoms-security-reviewer`, `dependency-risk-manager` |

### API
| Document | Path | Agents |
|----------|------|--------|
| API Design | `API_DESIGN_REFERENCE.md` | `api-contract-inspector`, `api-testing-specialist` |

### CLI Design
| Document | Path | Agents |
|----------|------|--------|
| CLI Design | `CLI_DESIGN_REFERENCE.md` | `software-planning-architect` |

### DevOps & Infrastructure
| Document | Path | Agents |
|----------|------|--------|
| DevOps & Platform | `DEVOPS_PLATFORM_REFERENCE.md` | `ops-concierge`, `dependency-risk-manager` |

### Accessibility
| Document | Path | Agents |
|----------|------|--------|
| WCAG Guidelines | `UI_DESIGN_PRINCIPLES_REFERENCE.md` (section 5) | `accessibility-testing-expert` |

---

## 3. Language-Specific

### Python
| Document | Path |
|----------|------|
| Ruff Config | `thegent/templates/python/pyproject.template.toml` |
| Pytest Config | `thegent/templates/quality/pytest-config.toml` |

### TypeScript
| Document | Path |
|----------|------|
| Oxlint Config | `thegent/templates/typescript/oxlint.config.json` |
| Vitest Config | `thegent/templates/typescript/vitest.config.ts` |

### Rust
| Document | Path |
|----------|------|
| Clippy Config | `thegent/templates/rust/clippy.toml` |

### Go
| Document | Path |
|----------|------|
| Golangci Config | `thegent/templates/go/.golangci.yml` |

### Bash
| Document | Path |
|----------|------|
| ShellCheck Config | `thegent/templates/bash/.shellcheckrc` |

---

## 4. Application-Specific

### MCP Server Development
| Document | Path |
|----------|------|
| MCP Integration | `thegent/docs/guides/MCP_INTEGRATION_GUIDE.md` |

### CLI Applications
| Document | Path |
|----------|------|
| CLI Patterns | `SOFTWARE_DESIGN_PATTERNS_REFERENCE.md` (section 2.2) |

### Web Applications
| Document | Path |
|----------|------|
| Web Security | `security/SECURITY_BEST_PRACTICES.md` |

---

## 5. Agent ↔ Reference Mapping

| Agent | Primary Reference | Secondary References |
|-------|-------------------|---------------------|
| `security-auditor` | `security/SECURITY_BEST_PRACTICES.md` | `AUTHENTICATION_AUTHORIZATION_REFERENCE.md`, `SOFTWARE_ARCHITECTURE_REFERENCE.md` |
| `atoms-security-reviewer` | `security/SECURITY_BEST_PRACTICES.md` | `AUTHENTICATION_AUTHORIZATION_REFERENCE.md`, `SOFTWARE_DESIGN_PATTERNS_REFERENCE.md` |
| `test-strategist` | `testing/TESTING_STRATEGIES.md` | `FRONTEND_ARCHITECTURE_REFERENCE.md`, `performance/PERFORMANCE_OPTIMIZATION.md` |
| `qa-test-coverage-expert` | `testing/TESTING_STRATEGIES.md` | `FRONTEND_ARCHITECTURE_REFERENCE.md`, `UI_DESIGN_PRINCIPLES_REFERENCE.md` |
| `qa-verification-lead` | `testing/TESTING_STRATEGIES.md` | `SOFTWARE_ARCHITECTURE_REFERENCE.md` |
| `performance-optimization-specialist` | `performance/PERFORMANCE_OPTIMIZATION.md` | `FRONTEND_ARCHITECTURE_REFERENCE.md`, `SOFTWARE_ARCHITECTURE_REFERENCE.md` |
| `performance-tuner` | `performance/PERFORMANCE_OPTIMIZATION.md` | `DATA_ENGINEERING_REFERENCE.md`, `testing/TESTING_STRATEGIES.md` |
| `api-contract-inspector` | `API_DESIGN_REFERENCE.md` | `security/SECURITY_BEST_PRACTICES.md`, `MICROSERVICES_ARCHITECTURE_REFERENCE.md` |
| `api-testing-specialist` | `testing/TESTING_STRATEGIES.md` | `API_DESIGN_REFERENCE.md`, `MICROSERVICES_ARCHITECTURE_REFERENCE.md` |
| `accessibility-testing-expert` | `UI_DESIGN_PRINCIPLES_REFERENCE.md` | `FRONTEND_ARCHITECTURE_REFERENCE.md`, `testing/TESTING_STRATEGIES.md` |
| `dependency-risk-manager` | `security/SECURITY_BEST_PRACTICES.md` | `DEVOPS_PLATFORM_REFERENCE.md`, `SOFTWARE_DESIGN_PATTERNS_REFERENCE.md` |
| `code-review-refactor-expert` | `SOFTWARE_DESIGN_PATTERNS_REFERENCE.md` | `SOFTWARE_ARCHITECTURE_REFERENCE.md` |
| `software-planning-architect` | `SOFTWARE_ARCHITECTURE_REFERENCE.md` | `MICROSERVICES_ARCHITECTURE_REFERENCE.md`, `FRONTEND_ARCHITECTURE_REFERENCE.md` |
| `component-modularity-architect` | `FRONTEND_ARCHITECTURE_REFERENCE.md` | `SOFTWARE_ARCHITECTURE_REFERENCE.md`, `SOFTWARE_DESIGN_PATTERNS_REFERENCE.md` |
| `quality-gatekeeper` | `SOFTWARE_ARCHITECTURE_REFERENCE.md` | `testing/TESTING_STRATEGIES.md` |
| `ops-concierge` | `DEVOPS_PLATFORM_REFERENCE.md` | `SOFTWARE_ARCHITECTURE_REFERENCE.md`, `performance/PERFORMANCE_OPTIMIZATION.md` |
| `observability-sentinel` | `MICROSERVICES_ARCHITECTURE_REFERENCE.md` | `DEVOPS_PLATFORM_REFERENCE.md`, `security/SECURITY_BEST_PRACTICES.md` |

---

## Usage

### For Agents
Agents should reference these documents when:
1. Generating code in a specific domain
2. Making architecture decisions
3. Validating code quality
4. Making recommendations

### Example Agent Prompt Addition
```
When working on performance-critical code, reference:
- docs/reference/performance/PERFORMANCE_OPTIMIZATION.md
- docs/reference/testing/TESTING_STRATEGIES.md
```

---

## Contributing

To add new reference docs:
1. Create document in appropriate subdirectory
2. Add entry to this index
3. Update agent mappings if applicable

---

*Last Updated: 2026-02-16*
