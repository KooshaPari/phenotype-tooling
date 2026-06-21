# ADR-002: Helm as Package Manager

## Status
**Accepted**

## Context

For managing complex Kubernetes applications, we need a packaging solution that supports templating, versioning, and dependency management. Kubernetes manifests alone become unwieldy for multi-environment deployments.

### Requirements

1. **Templating:** Support variable substitution and conditional logic
2. **Versioning:** Track and manage versioned releases
3. **Dependencies:** Manage external chart dependencies
4. **Rollback:** Support rollbacks to previous releases
5. **Multi-Environment:** Support different configurations per environment
6. **Community Ecosystem:** Leverage existing community charts

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Helm** | Industry standard, rich template functions, dependency management, rollback | Template complexity, "templating YAML" issues |
| **Kustomize** | Native to kubectl, overlay approach, no templating | Less flexible for complex logic, no versioning |
| **CUE** | Type-safe, powerful constraints | Steep learning curve, newer, less ecosystem |
| **Pulumi** | Real programming language, state management | Heavyweight, requires state backend |
| **Jsonnet** | Powerful data templating | Non-standard, steep curve |
| **Raw K8s YAML** | Simple, no abstraction | Duplication, no DRY, manual versioning |

## Decision

**We will use Helm as the primary package manager**, with Kustomize support for simpler use cases.

### Rationale

1. **Market Dominance:** Helm is the most widely adopted Kubernetes package manager
2. **Rich Template Library:** Sprig functions provide extensive templating capabilities
3. **Dependency Management:** Charts can depend on other charts (e.g., databases)
4. **Release Management:** Built-in versioning and rollback capabilities
5. **Ecosystem:** Access to 1000+ pre-built charts on Artifact Hub

### Consequences

**Positive:**
- Access to extensive chart library
- Familiar templating (Go templates)
- Built-in release lifecycle management
- Hook system for pre/post deployment actions

**Negative:**
- "Templating YAML" complexity
- Debugging template issues can be difficult
- Template logic can become complex and hard to test

## Implementation

### Chart Structure

```
deploy/helm/
├── charts/                 # Sub-charts (dependencies)
├── templates/              # Kubernetes manifest templates
│   ├── _helpers.tpl       # Template helper definitions
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   └── hpa.yaml
├── Chart.yaml             # Chart metadata
├── values.yaml            # Default values
├── values-dev.yaml        # Dev environment overrides
├── values-prod.yaml       # Prod environment overrides
└── README.md
```

### Integration Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    HelmDeployer                                │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │   Values    │───>│   Template  │───>│   Render    │       │
│  │   Merge     │    │   Engine    │    │   Manifests │       │
│  └─────────────┘    └─────────────┘    └──────┬──────┘       │
│                                                │              │
│                                         ┌──────▼──────┐      │
│                                         │   Helm      │      │
│                                         │   Client    │      │
│                                         │   (exec)    │      │
│                                         └──────┬──────┘      │
│                                                │              │
│                                         ┌──────▼──────┐      │
│                                         │ Kubernetes  │      │
│                                         │   Cluster   │      │
│                                         └─────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

### Code Implementation

```go
// HelmDeployer handles Helm deployments
type HelmDeployer struct {
    chartPath string
    namespace string
    values    map[string]string
    logger    *slog.Logger
}

// NewHelmDeployer creates a new Helm deployer
func NewHelmDeployer(chartPath, namespace string) *HelmDeployer {
    return &HelmDeployer{
        chartPath: chartPath,
        namespace: namespace,
        values:    make(map[string]string),
        logger:    slog.Default(),
    }
}

// SetValue sets a Helm value
func (h *HelmDeployer) SetValue(key, value string) {
    h.values[key] = value
}

// Install installs a Helm chart
func (h *HelmDeployer) Install(ctx context.Context, releaseName string) error {
    args := []string{"install", releaseName, h.chartPath, "-n", h.namespace}
    
    for k, v := range h.values {
        args = append(args, "--set", fmt.Sprintf("%s=%s", k, v))
    }
    
    cmd := exec.CommandContext(ctx, "helm", args...)
    return cmd.Run()
}

// Upgrade upgrades a Helm release
func (h *HelmDeployer) Upgrade(ctx context.Context, releaseName string) error {
    args := []string{"upgrade", releaseName, h.chartPath, "-n", h.namespace}
    
    for k, v := range h.values {
        args = append(args, "--set", fmt.Sprintf("%s=%s", k, v))
    }
    
    // Add --install flag to handle both install and upgrade
    args = append(args, "--install")
    
    cmd := exec.CommandContext(ctx, "helm", args...)
    return cmd.Run()
}

// Rollback rolls back a Helm release
func (h *HelmDeployer) Rollback(ctx context.Context, releaseName string) error {
    cmd := exec.CommandContext(ctx, "helm", "rollback", releaseName, "-n", h.namespace)
    return cmd.Run()
}
```

## Kustomize Integration

For simpler deployments, we also support Kustomize:

```go
// KustomizeDeployer for overlay-based deployments
type KustomizeDeployer struct {
    kustomizationPath string
    namespace         string
}

func (k *KustomizeDeployer) Apply(ctx context.Context) error {
    cmd := exec.CommandContext(ctx, "kubectl", "apply", "-k", k.kustomizationPath, "-n", k.namespace)
    return cmd.Run()
}
```

Kustomize is preferred when:
- No complex templating logic needed
- Simple environment-specific overlays
- No external dependencies
- Team prefers configuration over templating

## Related Decisions

- ADR-001: Kubernetes Native Deployment Strategy
- ADR-003: kubectl over Client Libraries

## References

1. [Helm Documentation](https://helm.sh/docs/)
2. [Kustomize Documentation](https://kubectl.docs.kubernetes.io/references/kustomize/)
3. [Artifact Hub](https://artifacthub.io/)
4. [Helm Best Practices](https://helm.sh/docs/chart_best_practices/)

---

*Last Updated: 2026-04-05*
