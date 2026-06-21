# ADR-003: kubectl over Client Libraries

## Status
**Accepted**

## Context

When implementing the deployment system, we need to choose between using the official Kubernetes client libraries (client-go) or invoking kubectl directly as a subprocess.

### Requirements

1. **Simplicity:** Implementation should be straightforward and maintainable
2. **Feature Parity:** Must support all needed Kubernetes operations
3. **Error Handling:** Must properly capture and handle errors
4. **Output Capture:** Need to capture command output for logging and status
5. **Portability:** Should work across different Kubernetes versions
6. **Testing:** Should be testable without full cluster setup

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **kubectl exec** | Simple, handles auth, always up-to-date, familiar | Spawning processes, parsing output |
| **client-go** | Native Go, type-safe, efficient, programmatic | Complex, steep learning curve, version coupling |
| **controller-runtime** | Higher-level abstractions, Kubernetes-native | Heavy dependency, operator-focused |
| **REST API directly** | No dependencies, full control | Complex auth handling, low-level |

## Decision

**We will use kubectl subprocess execution for the initial implementation**, with a design that allows future migration to client-go.

### Rationale

1. **Simplicity:** Subprocess execution is straightforward and well-understood
2. **Auth Handling:** kubectl automatically handles kubeconfig, certificates, and cloud provider auth
3. **Version Agnostic:** Works with any Kubernetes version kubectl supports
4. **Feature Complete:** kubectl exposes all Kubernetes features immediately
5. **Debugging:** Easy to reproduce deployment steps manually for debugging

### Consequences

**Positive:**
- Fast development velocity
- No complex dependency management
- Automatic authentication handling
- Easy manual reproduction of issues

**Negative:**
- Process spawning overhead
- Output parsing required
- Less type-safe than client-go
- Harder to unit test

## Implementation

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│                    KubernetesDeployer                          │
├────────────────────────────────────────────────────────────────┤
│                                                                │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐       │
│  │   Config    │───>│  Generate   │───>│   Exec      │       │
│  │             │    │  Manifest   │    │   kubectl   │       │
│  └─────────────┘    └─────────────┘    └──────┬──────┘       │
│                                               │              │
│                                        ┌──────▼──────┐      │
│                                        │  Capture    │      │
│                                        │  Output     │      │
│                                        └──────┬──────┘      │
│                                               │              │
│                                        ┌──────▼──────┐      │
│                                        │   Log &     │      │
│                                        │   Status    │      │
│                                        └─────────────┘      │
└────────────────────────────────────────────────────────────────┘
```

### Core Implementation

```go
// KubernetesDeployer handles Kubernetes deployments
type KubernetesDeployer struct {
    config *Config
    logger *slog.Logger
}

// NewKubernetesDeployer creates a new K8s deployer
func NewKubernetesDeployer(cfg Config) *KubernetesDeployer {
    return &KubernetesDeployer{
        config: &cfg,
        logger: slog.Default(),
    }
}

// Apply applies a Kubernetes manifest
func (k *KubernetesDeployer) Apply(ctx context.Context, manifest string) error {
    cmd := exec.CommandContext(ctx, "kubectl", "apply", "-f", "-")
    cmd.Stdin = strings.NewReader(manifest)
    
    // Capture output for logging
    output, err := cmd.CombinedOutput()
    if err != nil {
        k.logger.Error("kubectl apply failed", 
            "error", err,
            "output", string(output))
        return fmt.Errorf("apply failed: %w - %s", err, output)
    }
    
    k.logger.Info("kubectl apply succeeded", "output", string(output))
    return nil
}

// Deploy deploys an application
func (k *KubernetesDeployer) Deploy(ctx context.Context) error {
    manifest := k.generateManifest()
    return k.Apply(ctx, manifest)
}

// Rollback rolls back a deployment
func (k *KubernetesDeployer) Rollback(ctx context.Context) error {
    cmd := exec.CommandContext(ctx, "kubectl", "rollout", "undo", 
        fmt.Sprintf("deployment/%s", k.config.Name),
        "-n", k.config.Namespace)
    
    output, err := cmd.CombinedOutput()
    if err != nil {
        return fmt.Errorf("rollback failed: %w - %s", err, output)
    }
    
    k.logger.Info("rollback completed", "output", string(output))
    return nil
}

// Status returns deployment status
func (k *KubernetesDeployer) Status(ctx context.Context) (*DeploymentStatus, error) {
    cmd := exec.CommandContext(ctx, "kubectl", "get", "deployment",
        k.config.Name, "-n", k.config.Namespace, "-o", "json")
    
    output, err := cmd.Output()
    if err != nil {
        return nil, fmt.Errorf("failed to get status: %w", err)
    }
    
    var deployment appsv1.Deployment
    if err := json.Unmarshal(output, &deployment); err != nil {
        return nil, fmt.Errorf("failed to parse status: %w", err)
    }
    
    return &DeploymentStatus{
        ReadyReplicas:     deployment.Status.ReadyReplicas,
        DesiredReplicas: *deployment.Spec.Replicas,
        UpdatedReplicas: deployment.Status.UpdatedReplicas,
        AvailableReplicas: deployment.Status.AvailableReplicas,
    }, nil
}

// generateManifest creates Kubernetes manifest from config
func (k *KubernetesDeployer) generateManifest() string {
    return fmt.Sprintf(`apiVersion: apps/v1
kind: Deployment
metadata:
  name: %s
  namespace: %s
  labels:
    app.kubernetes.io/name: %s
    app.kubernetes.io/version: "%s"
spec:
  replicas: %d
  selector:
    matchLabels:
      app: %s
  template:
    metadata:
      labels:
        app: %s
    spec:
      containers:
      - name: app
        image: %s
        ports:
        - containerPort: 8080
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
`, k.config.Name, k.config.Namespace, k.config.Name, k.config.Version,
   k.config.Replicas, k.config.Name, k.config.Name, k.config.Image)
}
```

## Migration Path to client-go

The implementation is designed to allow future migration:

```go
// Deployer interface abstracts kubectl implementation
type Deployer interface {
    Apply(ctx context.Context, manifest string) error
    Deploy(ctx context.Context) error
    Rollback(ctx context.Context) error
    Status(ctx context.Context) (*DeploymentStatus, error)
}

// Current implementation using kubectl
var _ Deployer = (*KubernetesDeployer)(nil)

// Future implementation using client-go
type ClientGoDeployer struct {
    client kubernetes.Interface
    config *Config
}

var _ Deployer = (*ClientGoDeployer)(nil)
```

## Testing Strategy

### Mocking kubectl

```go
// Mockable command execution
type CommandRunner interface {
    Run(ctx context.Context, name string, args ...string) ([]byte, error)
}

type RealCommandRunner struct{}

func (r *RealCommandRunner) Run(ctx context.Context, name string, args ...string) ([]byte, error) {
    cmd := exec.CommandContext(ctx, name, args...)
    return cmd.CombinedOutput()
}

type MockCommandRunner struct {
    responses map[string]mockResponse
}

type mockResponse struct {
    output []byte
    err    error
}

func (m *MockCommandRunner) Run(ctx context.Context, name string, args ...string) ([]byte, error) {
    key := name + " " + strings.Join(args, " ")
    if resp, ok := m.responses[key]; ok {
        return resp.output, resp.err
    }
    return nil, fmt.Errorf("unexpected command: %s", key)
}
```

### Integration Testing

```go
func TestKubernetesDeployer_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    
    // Requires running k3d/kind cluster
    deployer := NewKubernetesDeployer(Config{
        Name:      "test-app",
        Namespace: "default",
        Replicas:  1,
        Image:     "nginx:latest",
    })
    
    ctx := context.Background()
    
    // Test deployment
    err := deployer.Deploy(ctx)
    require.NoError(t, err)
    
    // Test status
    status, err := deployer.Status(ctx)
    require.NoError(t, err)
    require.Equal(t, int32(1), status.DesiredReplicas)
    
    // Cleanup
    cmd := exec.Command("kubectl", "delete", "deployment", "test-app")
    cmd.Run()
}
```

## Related Decisions

- ADR-001: Kubernetes Native Deployment Strategy
- ADR-002: Helm as Package Manager

## References

1. [kubectl Documentation](https://kubernetes.io/docs/reference/kubectl/)
2. [client-go Repository](https://github.com/kubernetes/client-go)
3. [controller-runtime](https://github.com/kubernetes-sigs/controller-runtime)

---

*Last Updated: 2026-04-05*
