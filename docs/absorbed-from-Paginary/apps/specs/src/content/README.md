# PhenoSpecs - Specification Registry

**Unified specification registry for the Phenotype ecosystem.**

This repository serves as the **central source of truth** for design specifications, requirements documents, ADRs, and API contracts across all Phenotype projects.

---

## Quick Start

```bash
# Find a spec
ls specs/auth/                    # Auth domain specs
ls specs/crypto/                  # Crypto domain specs

# Read the registry
cat registry.yaml                 # See all registered specs

# Link to implementation
spec-links check                  # Verify spec-to-code traceability
```

---

## Registry Structure

| Directory | Purpose | Contents |
|-----------|---------|----------|
| `specs/` | Domain specifications | Feature specs by domain (auth, crypto, caching, etc.) |
| `adrs/` | Architecture decisions | ADRs in MADR format |
| `openapi/` | API contracts | OpenAPI 3.1 specifications |
| `integrations/` | Integration specs | Cross-system integration specifications |
| `registry.yaml` | Index | Central registry linking all specs to implementations |

---

## Usage

### For Developers

1. **Before implementing**: Check if spec exists in `specs/&lt;domain>/`
2. **Before deciding**: Check `adrs/` for prior architecture decisions
3. **Before integrating**: Check `openapi/` for API contracts
4. **Traceability**: Use `spec-links` to verify spec-to-code linkage

### For Spec Authors

```bash
# Create new spec
spec-new create specs/<domain>/<feature-name>

# This creates:
#   specs/<domain>/<feature-name>/
#   ├── spec.md          # Feature specification
#   ├── frd.md           # Functional requirements
#   └── plan.md          # Implementation plan
```

---

## Connection to Implementations

Specs in this registry link to actual code via:

1. **Traceability macros** in code (Rust: `#[trace_fr(...)]`, Go: `// FR: ...`)
2. **Registry entries** in `registry.yaml` mapping specs to repos
3. **catalog-info.yaml** in each repo referencing specs

---

## Registry Index

See [registry.yaml](./registry.yaml) for complete index with:
- Spec ID → File path
- Domain classification
- Implementation repo links
- Status (draft | specified | implementing | implemented)

---

## Governance

- **New specs**: Must follow [kitty-spec format](https://github.com/KooshaPari/AgilePlus/tree/main/kitty-specs)
- **Updates**: Require ADR if architectural impact
- **Deprecation**: Move to `archive/` with migration guide
- **Traceability**: All specs must link to at least one implementation

---

## Links

- [AgilePlus CLI](https://github.com/KooshaPari/AgilePlus) - Spec-driven development
- [HexaKit](https://github.com/KooshaPari/HexaKit) - Templates
- [PhenoHandbook](https://github.com/KooshaPari/PhenoHandbook) - Patterns & guidelines
