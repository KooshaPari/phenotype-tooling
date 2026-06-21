# ADR-001: Docker Compose as Configuration Format

## Status
**Accepted**

## Context

The Phenotype Docker utilities need a configuration format for defining multi-container applications. We must choose between various container orchestration specification formats.

### Requirements

1. **Human-Readable:** Easy for developers to write and understand
2. **Tooling Support:** Wide editor and IDE support
3. **Multi-Container:** Define relationships between services
4. **Extensible:** Support for volumes, networks, environment variables
5. **Industry Standard:** Widely adopted in the ecosystem

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Docker Compose YAML** | Industry standard, rich features, great tooling | Complex specification |
| **Kubernetes YAML** | Production-ready, extensive ecosystem | Verbose, complex |
| **TOML** | Simple, clear | Limited ecosystem |
| **CUE** | Type-safe, validation | Steep learning curve |
| **JSON** | Machine-readable | Verbose, no comments |
| **Custom Format** | Full control | Maintenance burden |

## Decision

**We will use Docker Compose v3 specification** as the primary configuration format.

### Rationale

1. **Industry Standard:** Most widely used local development format
2. **Rich Ecosystem:** Extensive tooling, validation, documentation
3. **Developer Familiarity:** Most developers already know it
4. **Feature Completeness:** Covers volumes, networks, secrets, health checks

### Consequences

**Positive:**
- Immediate developer familiarity
- Rich tooling support (VS Code extensions, CLI)
- Can be deployed with docker-compose or converted to Kubernetes

**Negative:**
- Docker-specific terminology
- Some features don't translate to production
- Version complexity (v2 vs v3)

## Implementation

### Compose Structure

```yaml
version: "3.9"

services:
  app:
    image: phenotype/app:latest
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - LOG_LEVEL=info
    depends_on:
      - db
    networks:
      - backend
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    volumes:
      - db_data:/var/lib/postgresql/data
    environment:
      POSTGRES_DB: phenotype
      POSTGRES_USER: app
    networks:
      - backend

volumes:
  db_data:

networks:
  backend:
    driver: bridge
```

### Go Implementation

```go
// DockerComposeConfig represents docker-compose configuration
type DockerComposeConfig struct {
    Version  string                    `yaml:"version"`
    Services map[string]ServiceConfig  `yaml:"services"`
    Volumes  map[string]VolumeConfig    `yaml:"volumes,omitempty"`
    Networks map[string]NetworkConfig   `yaml:"networks,omitempty"`
    Secrets  map[string]SecretConfig   `yaml:"secrets,omitempty"`
}

// ServiceConfig holds service configuration
type ServiceConfig struct {
    Image       string            `yaml:"image,omitempty"`
    Build       *BuildConfig      `yaml:"build,omitempty"`
    Command     interface{}       `yaml:"command,omitempty"`
    Ports       []string          `yaml:"ports,omitempty"`
    Environment map[string]string `yaml:"environment,omitempty"`
    Volumes     []string          `yaml:"volumes,omitempty"`
    DependsOn   []string          `yaml:"depends_on,omitempty"`
    Networks    []string          `yaml:"networks,omitempty"`
    HealthCheck *HealthCheckConfig `yaml:"healthcheck,omitempty"`
}

// BuildConfig holds Docker build configuration
type BuildConfig struct {
    Context    string            `yaml:"context"`
    Dockerfile string            `yaml:"dockerfile,omitempty"`
    Args       map[string]string `yaml:"args,omitempty"`
    Target     string            `yaml:"target,omitempty"`
}

// Generate generates docker-compose.yml content
func (c *DockerComposeConfig) Generate() (string, error) {
    bytes, err := yaml.Marshal(c)
    if err != nil {
        return "", err
    }
    return string(bytes), nil
}
```

## Related Decisions

- ADR-002: OCI Image Format Support
- ADR-003: Container Runtime Abstraction

---

*Last Updated: 2026-04-05*
