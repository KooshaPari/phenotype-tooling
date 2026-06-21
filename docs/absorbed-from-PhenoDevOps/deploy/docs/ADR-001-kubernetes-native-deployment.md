# ADR-001: Kubernetes Native Deployment Strategy

## Status
**Accepted**

## Context

The Phenotype Deploy system needs to support container orchestration and application deployment across multiple environments. We must decide on the primary deployment target and strategy.

### Requirements

1. **Container Orchestration:** Must support containerized application deployment
2. **Industry Standard:** Should use widely-adopted technologies for ecosystem compatibility
3. **Multi-Environment:** Must support dev, staging, and production environments
4. **Rollback Capability:** Must support quick rollback to previous versions
5. **Declarative Configuration:** Infrastructure should be defined as code

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Kubernetes (k8s)** | Industry standard, rich ecosystem, declarative, battle-tested | Complexity, learning curve |
| **Docker Compose** | Simple, familiar, good for dev | Not production-ready, no native orchestration |
| **Nomad** | Simpler than k8s, multi-datacenter | Smaller ecosystem, less tooling |
| **AWS ECS** | Managed, AWS-integrated | Vendor lock-in, less portable |
| **Self-hosted containers** | Full control | Operational burden, no orchestration |

## Decision

**We will use Kubernetes as the primary deployment target**, with support for Docker Compose in development environments.

### Rationale

1. **Ecosystem Momentum:** Kubernetes has won the container orchestration wars and is the de facto standard
2. **Tooling:** Rich ecosystem of tools (Helm, ArgoCD, Prometheus, Istio)
3. **Cloud Native Foundation:** Backed by CNCF, ensuring long-term support
4. **Portability:** Runs on any cloud provider or on-premises
5. **Declarative Model:** Aligns with GitOps principles and infrastructure-as-code

### Consequences

**Positive:**
- Access to extensive ecosystem of tools and operators
- Portable across cloud providers
- Strong community support
- Excellent observability integration

**Negative:**
- Steep learning curve for team members
- Complex operational model
- Resource overhead from control plane

## Implementation

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                     Phenotype Deploy                           │
├────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │   Config    │───>│   Deployer  │───>│   Monitor   │       │
│  │   Parser    │    │   (k8s)     │    │   (k8s)     │       │
│  └─────────────┘    └──────┬──────┘    └─────────────┘       │
│                           │                                   │
│                    ┌──────▼──────┐                          │
│                    │  Kubernetes  │                          │
│                    │   API/CLI   │                          │
│                    └─────────────┘                          │
└────────────────────────────────────────────────────────────────┘
```

### Key Components

1. **KubernetesDeployer:** Direct kubectl integration for imperative deployments
2. **HelmDeployer:** Chart-based deployments with templating
3. **ManifestGenerator:** Dynamic Kubernetes manifest generation

### Code Structure

```go
// Package deploy provides Kubernetes and Helm deployment capabilities
package deploy

// Config holds deployment configuration
type Config struct {
    Environment string
    Namespace   string
    Replicas    int
    Image       string
}

// KubernetesDeployer handles Kubernetes deployments
type KubernetesDeployer struct {
    config *Config
    logger *slog.Logger
}

// HelmDeployer handles Helm chart deployments
type HelmDeployer struct {
    chartPath string
    namespace string
    values    map[string]string
    logger    *slog.Logger
}
```

## Alternatives

### Docker Compose for Development

For local development, we support Docker Compose as an alternative:

```go
// DockerComposeDeployer for local development
type DockerComposeDeployer struct {
    composeFile string
    projectName string
}
```

This is intentionally simpler and only suitable for single-node development environments.

## Related Decisions

- ADR-002: Helm as Package Manager
- ADR-003: kubectl over Client Libraries

## References

1. [Kubernetes Documentation](https://kubernetes.io/docs/)
2. [CNCF Survey Results 2023](https://www.cncf.io/reports/cncf-annual-survey-2023/)
3. [Helm Documentation](https://helm.sh/docs/)

---

*Last Updated: 2026-04-05*
