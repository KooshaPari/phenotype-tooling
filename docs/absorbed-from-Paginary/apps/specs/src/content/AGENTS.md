# AGENTS.md — PhenoSpecs

## Project Overview

- **Name**: PhenoSpecs (Specifications & Standards)
- **Description**: Technical specifications, standards, and API definitions for Phenotype ecosystem
- **Location**: `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoSpecs`
- **Language Stack**: OpenAPI, AsyncAPI, Markdown
- **Published**: Private (Phenotype org)

## Quick Start

```bash
# Navigate to project
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoSpecs

# Validate specs
make validate

# Generate docs
make docs
```

## Architecture

### Specifications Repository

```
┌─────────────────────────────────────────────────────────────────┐
│                     Specification Types                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐   │
│  │   OpenAPI         │  │   AsyncAPI      │  │   JSON Schema   │   │
│  │   (REST APIs)     │  │   (Events)      │  │   (Validation)  │   │
│  └────────┬────────┘  └────────┬────────┘  └────────┬────────┘   │
└───────────┼───────────────────┼───────────────────┼──────────────┘
            │                   │                   │
            └───────────────────┼───────────────────┘
                                │
┌───────────────────────────────▼───────────────────────────────┐
│                     Registry & Discovery                           │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │                    registry.yaml                              │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │ │
│  │  │ Services │  │ Versions │  │ Owners   │  │ Status   │  │ │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │ │
│  └──────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Quality Standards

### Spec Quality

- **Validation**: Spectral
- **Linting**: openapi-lint
- **Breaking**: oasdiff
- **Documentation**: Redoc

## Git Workflow

### Branch Naming

Format: `&lt;type>/&lt;spec>/&lt;description>`

Examples:
- `spec/api/add-authentication`
- `breaking/v2/remove-deprecated`
- `docs/readme/update-links`

## CLI Commands

```bash
make validate
make docs
make breaking
```

## Resources

- [OpenAPI](https://spec.openapis.org/)
- [AsyncAPI](https://www.asyncapi.com/)
- [Phenotype Registry](https://github.com/KooshaPari/phenotype-registry)

## Agent Notes

**Critical Details:**
- Version all specs
- Breaking changes documented
- Registry kept updated
- Validate in CI
