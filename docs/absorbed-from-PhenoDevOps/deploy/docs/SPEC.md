# SPEC: Deploy System

## 1. Overview

The Phenotype Deploy system provides comprehensive Kubernetes and Helm deployment capabilities for the Phenotype ecosystem. It enables declarative, versioned, and reproducible application deployments across multiple environments.

### 1.1 Purpose

This specification defines the architecture, interfaces, and behavior of the Deploy system, including:

- Kubernetes manifest deployment and management
- Helm chart installation and lifecycle management
- Rollback and status monitoring capabilities
- Environment-specific configuration handling

### 1.2 Scope

**In Scope:**
- Kubernetes Deployment resources
- Helm chart operations (install, upgrade, rollback)
- Namespace and resource management
- Deployment status monitoring
- Configuration management

**Out of Scope:**
- Infrastructure provisioning (handled by Terraform/Pulumi)
- Service mesh configuration
- Certificate management
- Secrets management (handled by infrastructure/secrets)

### 1.3 Target Audience

- Platform Engineers
- DevOps Engineers
- Site Reliability Engineers (SREs)
- Application Developers

### 1.4 Document Conventions

- **MUST:** Required for compliance
- **SHOULD:** Recommended but not required
- **MAY:** Optional
- **SHALL:** Synonym for MUST

---

## 2. Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                            Phenotype Deploy                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        API Layer                                     │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌────────────┐ │  │
│  │  │   Deploy    │  │   Rollback  │  │   Status    │  │  Validate  │ │  │
│  │  │   Handler   │  │   Handler   │  │   Handler   │  │   Handler  │ │  │
│  │  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └─────┬──────┘ │  │
│  └─────────┼────────────────┼────────────────┼───────────────┼────────┘  │
│            │                │                │               │           │
│  ┌─────────┼────────────────┼────────────────┼───────────────┼────────┐  │
│  │         ▼                ▼                ▼               ▼        │  │
│  │  ┌─────────────────────────────────────────────────────────────┐ │  │
│  │  │                    Core Engine                             │ │  │
│  │  ├─────────────────────────────────────────────────────────────┤ │  │
│  │  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐ │ │  │
│  │  │  │  Kubernetes │  │    Helm     │  │      Manifest           │ │ │  │
│  │  │  │  Deployer   │  │  Deployer   │  │     Generator           │ │ │  │
│  │  │  └─────────────┘  └─────────────┘  └─────────────────────────┘ │ │  │
│  │  └─────────────────────────────────────────────────────────────┘ │  │
│  └────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                      Execution Layer                                 │  │
│  │  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────────┐ │  │
│  │  │   kubectl   │    │    helm     │    │    kubeconfig           │ │  │
│  │  │   process   │    │   process   │    │    manager              │ │  │
│  │  └─────────────┘    └─────────────┘    └─────────────────────────┘ │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                    Target Infrastructure                           │  │
│  │         ┌──────────────────────────────────────────────┐            │  │
│  │         │            Kubernetes Cluster(s)            │            │  │
│  │         │  ┌──────────┐  ┌──────────┐  ┌──────────┐    │            │  │
│  │         │  │   Dev    │  │  Staging │  │   Prod   │    │            │  │
│  │         │  └──────────┘  └──────────┘  └──────────┘    │            │  │
│  │         └──────────────────────────────────────────────┘            │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                                                           │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Component Diagram

```
                    ┌─────────────────┐
                    │    Client       │
                    │   (CLI/API)     │
                    └────────┬────────┘
                             │
                             ▼
            ┌────────────────────────────────┐
            │      deploy.Deployer Interface  │
            │         (Abstraction)           │
            └────────────────┬─────────────────┘
                             │
            ┌────────────────┼────────────────┐
            │                │                │
            ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │  Kubernetes  │ │    Helm      │ │   Docker     │
    │  Deployer    │ │  Deployer    │ │   Compose    │
    └──────┬───────┘ └──────┬───────┘ └──────┬───────┘
           │                │                │
           ▼                ▼                ▼
    ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │   kubectl    │ │    helm      │ │ docker compose│
    │   exec       │ │    exec      │ │    exec       │
    └──────────────┘ └──────────────┘ └──────────────┘
```

### 2.3 Data Flow

#### 2.3.1 Deployment Flow

```
┌─────────┐    ┌───────────┐    ┌──────────┐    ┌─────────┐    ┌─────────┐
│  Input  │───>│  Config   │───>│ Generate │───>│ Execute │───>│ Verify  │
│  Params │    │  Validate │    │ Manifest │    │ Deploy  │    │ Status  │
└─────────┘    └───────────┘    └──────────┘    └─────────┘    └─────────┘
     │              │               │              │              │
     │              │               │              │              │
     ▼              ▼               ▼              ▼              ▼
   YAML/JSON    Check all        Template      kubectl/      Poll for
   Config File   required         manifest      helm exec     readiness
                fields exist
```

#### 2.3.2 Rollback Flow

```
┌─────────┐    ┌───────────┐    ┌──────────┐    ┌─────────┐
│  Rollback│───>│  Identify │───>│ Execute  │───>│ Verify  │
│  Request │    │  Previous │    │ Rollback │    │ Status  │
│          │    │  Revision │    │          │    │         │
└─────────┘    └───────────┘    └──────────┘    └─────────┘
                    │
                    ▼
            ┌───────────────┐
            │  Helm: Get     │
            │  previous      │
            │  revision      │
            │                │
            │  K8s: Get      │
            │  rollout       │
            │  history       │
            └───────────────┘
```

### 2.4 Module Structure

```
deploy/
├── docs/                   # Documentation
│   ├── SOTA.md            # State of the Art research
│   ├── ADR-*.md           # Architecture Decision Records
│   └── SPEC.md            # This specification
├── k8s.go                 # Kubernetes deployer implementation
├── k8s_test.go            # Kubernetes deployer tests
├── helm.go                # Helm deployer implementation (future)
├── helm_test.go           # Helm deployer tests
├── config.go              # Configuration types
├── errors.go              # Error definitions
├── interface.go           # Deployer interface
├── go.mod                 # Go module definition
└── README.md              # Project readme
```

---

## 3. Interfaces

### 3.1 Core Deployer Interface

All deployer implementations MUST satisfy the following interface:

```go
// Deployer defines the contract for all deployment implementations
// Following the Strategy Pattern for different deployment targets
type Deployer interface {
    // Deploy performs a deployment operation
    // Context cancellation MUST be respected
    // Returns error if deployment fails
    Deploy(ctx context.Context) error
    
    // Rollback reverts to the previous version
    // SHOULD be idempotent
    // Returns error if rollback fails
    Rollback(ctx context.Context) error
    
    // Status returns the current deployment status
    // MUST not modify state
    // Returns error if status cannot be determined
    Status(ctx context.Context) (*DeploymentStatus, error)
    
    // Name returns the deployer name for logging and identification
    Name() string
}

// DeploymentStatus provides detailed deployment information
type DeploymentStatus struct {
    // State indicates the current deployment state
    State DeploymentState
    
    // ReadyReplicas is the number of ready pods/instances
    ReadyReplicas int32
    
    // DesiredReplicas is the target number of replicas
    DesiredReplicas int32
    
    // UpdatedReplicas is the number of replicas with updated spec
    UpdatedReplicas int32
    
    // AvailableReplicas is the number of available replicas
    AvailableReplicas int32
    
    // Message provides human-readable status information
    Message string
    
    // LastUpdated indicates when the status was last checked
    LastUpdated time.Time
    
    // Conditions provides detailed condition information
    Conditions []DeploymentCondition
}

// DeploymentState represents the deployment lifecycle state
type DeploymentState string

const (
    // StatePending indicates deployment is pending
    StatePending DeploymentState = "Pending"
    
    // StateProgressing indicates deployment is in progress
    StateProgressing DeploymentState = "Progressing"
    
    // StateComplete indicates deployment completed successfully
    StateComplete DeploymentState = "Complete"
    
    // StateFailed indicates deployment failed
    StateFailed DeploymentState = "Failed"
    
    // StateUnknown indicates state cannot be determined
    StateUnknown DeploymentState = "Unknown"
)

// DeploymentCondition provides detailed condition information
type DeploymentCondition struct {
    Type    string
    Status  string
    Reason  string
    Message string
}
```

### 3.2 Kubernetes-Specific Interface

```go
// KubernetesDeployer handles Kubernetes deployments
type KubernetesDeployer struct {
    config *Config
    logger *slog.Logger
}

// Config holds deployment configuration
type Config struct {
    // Name is the deployment name (required)
    Name string
    
    // Namespace is the target namespace (default: "default")
    Namespace string
    
    // Replicas is the desired replica count (default: 1)
    Replicas int
    
    // Image is the container image (required)
    Image string
    
    // Version is the application version (optional)
    Version string
    
    // Environment identifies the target environment
    Environment string
    
    // Port is the container port (default: 8080)
    Port int
    
    // Resources defines CPU/memory constraints
    Resources Resources
    
    // Env defines environment variables
    Env map[string]string
    
    // Labels defines additional pod labels
    Labels map[string]string
    
    // Annotations defines pod annotations
    Annotations map[string]string
    
    // Strategy defines the deployment strategy
    Strategy DeploymentStrategy
}

// Resources defines resource constraints
type Resources struct {
    Requests ResourceSpec
    Limits   ResourceSpec
}

// ResourceSpec defines resource amounts
type ResourceSpec struct {
    CPU    string // e.g., "100m", "1"
    Memory string // e.g., "128Mi", "1Gi"
}

// DeploymentStrategy defines rollout strategy
type DeploymentStrategy struct {
    Type          string // "RollingUpdate" or "Recreate"
    MaxUnavailable string // e.g., "25%"
    MaxSurge       string // e.g., "25%"
}

// NewKubernetesDeployer creates a new K8s deployer
func NewKubernetesDeployer(cfg Config) *KubernetesDeployer

// Apply applies a Kubernetes manifest from string
func (k *KubernetesDeployer) Apply(ctx context.Context, manifest string) error

// Deploy deploys an application
func (k *KubernetesDeployer) Deploy(ctx context.Context) error

// Rollback rolls back a deployment
func (k *KubernetesDeployer) Rollback(ctx context.Context) error

// Status returns deployment status
func (k *KubernetesDeployer) Status(ctx context.Context) (*DeploymentStatus, error)

// Name returns the deployer name
func (k *KubernetesDeployer) Name() string
```

### 3.3 Helm-Specific Interface

```go
// HelmDeployer handles Helm deployments
type HelmDeployer struct {
    chartPath string
    namespace string
    values    map[string]string
    logger    *slog.Logger
}

// HelmConfig holds Helm-specific configuration
type HelmConfig struct {
    // ChartPath is the path to the Helm chart (required)
    ChartPath string
    
    // Namespace is the target namespace (default: "default")
    Namespace string
    
    // ReleaseName is the Helm release name (required)
    ReleaseName string
    
    // Values is the map of Helm values
    Values map[string]string
    
    // ValueFiles is a list of values file paths
    ValueFiles []string
    
    // Version is the chart version to install (optional)
    Version string
    
    // Repo is the chart repository URL (optional)
    Repo string
    
    // Wait indicates whether to wait for deployment to be ready
    Wait bool
    
    // Timeout is the operation timeout
    Timeout time.Duration
}

// ReleaseInfo holds release information
type ReleaseInfo struct {
    Name      string
    Namespace string
    Revision  string
    Status    string
    Chart     string
    AppVersion string
}

// NewHelmDeployer creates a new Helm deployer
func NewHelmDeployer(chartPath, namespace string) *HelmDeployer

// SetValue sets a Helm value
func (h *HelmDeployer) SetValue(key, value string)

// Install installs a Helm chart
func (h *HelmDeployer) Install(ctx context.Context, releaseName string) error

// Upgrade upgrades a Helm release
func (h *HelmDeployer) Upgrade(ctx context.Context, releaseName string) error

// Rollback rolls back a Helm release
func (h *HelmDeployer) Rollback(ctx context.Context, releaseName string) error

// List lists Helm releases
func (h *HelmDeployer) List(ctx context.Context) ([]ReleaseInfo, error)

// GetValues returns the current Helm values
func (h *HelmDeployer) GetValues(ctx context.Context, releaseName string) (map[string]interface{}, error)
```

---

## 4. Data Models

### 4.1 Configuration Models

```go
// DeploymentConfig is the top-level configuration structure
type DeploymentConfig struct {
    // APIVersion identifies the configuration schema version
    APIVersion string `yaml:"apiVersion" json:"apiVersion"`
    
    // Kind identifies the configuration type
    Kind string `yaml:"kind" json:"kind"`
    
    // Metadata provides configuration metadata
    Metadata ConfigMetadata `yaml:"metadata" json:"metadata"`
    
    // Spec contains the deployment specification
    Spec DeploymentSpec `yaml:"spec" json:"spec"`
}

// ConfigMetadata provides configuration metadata
type ConfigMetadata struct {
    Name        string            `yaml:"name" json:"name"`
    Namespace   string            `yaml:"namespace,omitempty" json:"namespace,omitempty"`
    Labels      map[string]string `yaml:"labels,omitempty" json:"labels,omitempty"`
    Annotations map[string]string `yaml:"annotations,omitempty" json:"annotations,omitempty"`
}

// DeploymentSpec contains the deployment specification
type DeploymentSpec struct {
    // Replicas is the desired number of replicas
    Replicas *int32 `yaml:"replicas,omitempty" json:"replicas,omitempty"`
    
    // Image defines the container image
    Image ImageSpec `yaml:"image" json:"image"`
    
    // Resources defines resource constraints
    Resources ResourceRequirements `yaml:"resources,omitempty" json:"resources,omitempty"`
    
    // Ports defines exposed ports
    Ports []PortSpec `yaml:"ports,omitempty" json:"ports,omitempty"`
    
    // Environment defines environment variables
    Environment []EnvVar `yaml:"environment,omitempty" json:"environment,omitempty"`
    
    // Volumes defines volume mounts
    Volumes []VolumeSpec `yaml:"volumes,omitempty" json:"volumes,omitempty"`
    
    // Strategy defines the deployment strategy
    Strategy StrategySpec `yaml:"strategy,omitempty" json:"strategy,omitempty"`
    
    // HealthCheck defines health check configuration
    HealthCheck *HealthCheckSpec `yaml:"healthCheck,omitempty" json:"healthCheck,omitempty"`
    
    // Service defines service configuration
    Service *ServiceSpec `yaml:"service,omitempty" json:"service,omitempty"`
    
    // Ingress defines ingress configuration
    Ingress *IngressSpec `yaml:"ingress,omitempty" json:"ingress,omitempty"`
}

// ImageSpec defines container image settings
type ImageSpec struct {
    // Repository is the image repository
    Repository string `yaml:"repository" json:"repository"`
    
    // Tag is the image tag
    Tag string `yaml:"tag,omitempty" json:"tag,omitempty"`
    
    // PullPolicy defines when to pull the image
    PullPolicy string `yaml:"pullPolicy,omitempty" json:"pullPolicy,omitempty"`
    
    // PullSecret is the secret for private registries
    PullSecret string `yaml:"pullSecret,omitempty" json:"pullSecret,omitempty"`
}

// PortSpec defines port configuration
type PortSpec struct {
    // Name is the port name
    Name string `yaml:"name" json:"name"`
    
    // Port is the container port
    Port int32 `yaml:"port" json:"port"`
    
    // Protocol is the port protocol (TCP/UDP)
    Protocol string `yaml:"protocol,omitempty" json:"protocol,omitempty"`
    
    // Expose indicates if the port should be exposed via service
    Expose bool `yaml:"expose,omitempty" json:"expose,omitempty"`
    
    // ServicePort is the service port (if different from container port)
    ServicePort *int32 `yaml:"servicePort,omitempty" json:"servicePort,omitempty"`
}

// EnvVar defines environment variables
type EnvVar struct {
    // Name is the variable name
    Name string `yaml:"name" json:"name"`
    
    // Value is the variable value (mutually exclusive with ValueFrom)
    Value string `yaml:"value,omitempty" json:"value,omitempty"`
    
    // ValueFrom sources the value from elsewhere
    ValueFrom *EnvVarSource `yaml:"valueFrom,omitempty" json:"valueFrom,omitempty"`
}

// EnvVarSource defines sources for environment variables
type EnvVarSource struct {
    // SecretKeyRef references a secret key
    SecretKeyRef *SecretKeySelector `yaml:"secretKeyRef,omitempty" json:"secretKeyRef,omitempty"`
    
    // ConfigMapKeyRef references a configmap key
    ConfigMapKeyRef *ConfigMapKeySelector `yaml:"configMapKeyRef,omitempty" json:"configMapKeyRef,omitempty"`
}

// SecretKeySelector selects a key from a Secret
type SecretKeySelector struct {
    Name string `yaml:"name" json:"name"`
    Key  string `yaml:"key" json:"key"`
}

// ConfigMapKeySelector selects a key from a ConfigMap
type ConfigMapKeySelector struct {
    Name string `yaml:"name" json:"name"`
    Key  string `yaml:"key" json:"key"`
}
```

### 4.2 Status Models

```go
// DeploymentStatusModel is the persisted status structure
type DeploymentStatusModel struct {
    // DeploymentID is a unique identifier
    DeploymentID string `json:"deployment_id"`
    
    // Name is the deployment name
    Name string `json:"name"`
    
    // Namespace is the target namespace
    Namespace string `json:"namespace"`
    
    // State is the current deployment state
    State string `json:"state"`
    
    // Replicas is the replica status
    Replicas ReplicaStatus `json:"replicas"`
    
    // Conditions are the deployment conditions
    Conditions []Condition `json:"conditions"`
    
    // Events are recent deployment events
    Events []DeploymentEvent `json:"events"`
    
    // StartedAt is when the deployment started
    StartedAt time.Time `json:"started_at"`
    
    // CompletedAt is when the deployment completed (if applicable)
    CompletedAt *time.Time `json:"completed_at,omitempty"`
    
    // Error information (if failed)
    Error *DeploymentError `json:"error,omitempty"`
}

// ReplicaStatus provides replica information
type ReplicaStatus struct {
    Desired   int32 `json:"desired"`
    Ready     int32 `json:"ready"`
    Available int32 `json:"available"`
    Updated   int32 `json:"updated"`
}

// Condition represents a deployment condition
type Condition struct {
    Type               string    `json:"type"`
    Status             string    `json:"status"`
    LastTransitionTime time.Time `json:"last_transition_time"`
    Reason             string    `json:"reason"`
    Message            string    `json:"message"`
}

// DeploymentEvent represents a deployment event
type DeploymentEvent struct {
    Type      string    `json:"type"`
    Message   string    `json:"message"`
    Timestamp time.Time `json:"timestamp"`
}

// DeploymentError provides error details
type DeploymentError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}
```

---

## 5. Behavior

### 5.1 Deployment Lifecycle

#### 5.1.1 State Machine

```
                    ┌─────────┐
                    │  IDLE   │
                    └────┬────┘
                         │ Deploy()
                         ▼
              ┌───────────────────┐
              │     PENDING       │
              │  (validating)     │
              └────────┬──────────┘
                       │
              ┌────────┴──────────┐
              │                   │
              ▼                   ▼
     ┌─────────────────┐  ┌──────────────┐
     │   VALIDATION    │  │   FAILED     │
     │    FAILED       │  │   (error)    │
     │   (invalid)     │  └──────────────┘
     └─────────────────┘
              │
              ▼
     ┌─────────────────┐
     │   DEPLOYING     │
     │  (executing)    │
     └────────┬────────┘
              │
     ┌────────┴──────────┐
     │                   │
     ▼                   ▼
┌─────────────┐  ┌──────────────┐
│   FAILED    │  │   VERIFYING  │
│  (deploy)   │  │  (checking)  │
└─────────────┘  └──────┬───────┘
                        │
               ┌────────┴──────────┐
               │                   │
               ▼                   ▼
      ┌──────────────┐  ┌──────────────┐
      │    FAILED    │  │   COMPLETE   │
      │  (verify)    │  │  (success)   │
      └──────────────┘  └──────────────┘
```

#### 5.1.2 State Transitions

| Current State | Event | Next State | Action |
|---------------|-------|------------|--------|
| IDLE | Deploy() | PENDING | Validate configuration |
| PENDING | Validation OK | DEPLOYING | Execute deployment |
| PENDING | Validation Fail | VALIDATION_FAILED | Return error |
| DEPLOYING | Deploy OK | VERIFYING | Check health |
| DEPLOYING | Deploy Fail | FAILED | Log error, cleanup |
| VERIFYING | Health OK | COMPLETE | Return success |
| VERIFYING | Health Fail | FAILED | Trigger rollback |
| Any | Rollback() | ROLLING_BACK | Execute rollback |
| ROLLING_BACK | Rollback OK | IDLE | Return to previous |
| ROLLING_BACK | Rollback Fail | FAILED | Manual intervention |

### 5.2 Error Handling

#### 5.2.1 Error Categories

```go
// DeploymentErrorCategory classifies deployment errors
type DeploymentErrorCategory string

const (
    // ConfigError indicates invalid configuration
    ConfigError DeploymentErrorCategory = "config"
    
    // NetworkError indicates network/connection issues
    NetworkError DeploymentErrorCategory = "network"
    
    // AuthError indicates authentication/authorization issues
    AuthError DeploymentErrorCategory = "auth"
    
    // ResourceError indicates resource constraint issues
    ResourceError DeploymentErrorCategory = "resource"
    
    // TimeoutError indicates timeout issues
    TimeoutError DeploymentErrorCategory = "timeout"
    
    // InternalError indicates internal system errors
    InternalError DeploymentErrorCategory = "internal"
    
    // ExternalError indicates external service errors
    ExternalError DeploymentErrorCategory = "external"
)

// DeploymentError provides structured error information
type DeploymentError struct {
    Category    DeploymentErrorCategory
    Code        string
    Message     string
    Cause       error
    Recoverable bool
    RetryAfter  time.Duration
}

func (e *DeploymentError) Error() string {
    if e.Cause != nil {
        return fmt.Sprintf("[%s:%s] %s: %v", e.Category, e.Code, e.Message, e.Cause)
    }
    return fmt.Sprintf("[%s:%s] %s", e.Category, e.Code, e.Message)
}

func (e *DeploymentError) Unwrap() error {
    return e.Cause
}
```

#### 5.2.2 Retry Logic

```go
// RetryConfig defines retry behavior
type RetryConfig struct {
    MaxAttempts  int
    InitialDelay time.Duration
    MaxDelay     time.Duration
    Multiplier   float64
}

// DefaultRetryConfig provides sensible defaults
var DefaultRetryConfig = RetryConfig{
    MaxAttempts:  3,
    InitialDelay: 1 * time.Second,
    MaxDelay:     30 * time.Second,
    Multiplier:   2.0,
}

// ShouldRetry determines if an error is retryable
func ShouldRetry(err error) bool {
    if deployErr, ok := err.(*DeploymentError); ok {
        return deployErr.Recoverable
    }
    
    // Check for transient network errors
    if isNetworkError(err) {
        return true
    }
    
    // Check for rate limiting
    if isRateLimitError(err) {
        return true
    }
    
    return false
}

// ExecuteWithRetry executes a function with retry logic
func ExecuteWithRetry(ctx context.Context, fn func() error, config RetryConfig) error {
    delay := config.InitialDelay
    
    for attempt := 1; attempt <= config.MaxAttempts; attempt++ {
        err := fn()
        if err == nil {
            return nil
        }
        
        if !ShouldRetry(err) || attempt == config.MaxAttempts {
            return fmt.Errorf("attempt %d/%d failed: %w", attempt, config.MaxAttempts, err)
        }
        
        // Wait before retry
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-time.After(delay):
        }
        
        // Exponential backoff with jitter
        delay = time.Duration(float64(delay) * config.Multiplier)
        if delay > config.MaxDelay {
            delay = config.MaxDelay
        }
    }
    
    return nil
}
```

### 5.3 Health Checks

#### 5.3.1 Deployment Health Verification

```go
// HealthCheckConfig defines health check parameters
type HealthCheckConfig struct {
    Enabled         bool
    InitialDelay    time.Duration
    Period          time.Duration
    Timeout         time.Duration
    SuccessThreshold int
    FailureThreshold int
}

// VerifyDeploymentHealth checks if deployment is healthy
func VerifyDeploymentHealth(ctx context.Context, deployer *KubernetesDeployer, config HealthCheckConfig) error {
    // Wait for initial delay
    select {
    case <-ctx.Done():
        return ctx.Err()
    case <-time.After(config.InitialDelay):
    }
    
    consecutiveSuccesses := 0
    consecutiveFailures := 0
    
    ticker := time.NewTicker(config.Period)
    defer ticker.Stop()
    
    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case <-ticker.C:
            status, err := deployer.Status(ctx)
            if err != nil {
                consecutiveFailures++
                if consecutiveFailures >= config.FailureThreshold {
                    return fmt.Errorf("health check failed after %d attempts: %w", consecutiveFailures, err)
                }
                continue
            }
            
            if status.State == StateComplete && status.ReadyReplicas == status.DesiredReplicas {
                consecutiveSuccesses++
                consecutiveFailures = 0
                
                if consecutiveSuccesses >= config.SuccessThreshold {
                    return nil
                }
            } else {
                consecutiveFailures++
                consecutiveSuccesses = 0
                
                if consecutiveFailures >= config.FailureThreshold {
                    return fmt.Errorf("deployment not healthy: %s", status.Message)
                }
            }
        }
    }
}
```

---

## 6. Configuration

### 6.1 File Format

Deployment configurations are specified in YAML format:

```yaml
# Example deployment configuration
apiVersion: deploy.kooshapari.com/v1
kind: Deployment
metadata:
  name: phenotype-api
  namespace: production
  labels:
    app.kubernetes.io/part-of: phenotype
    app.kubernetes.io/managed-by: deploy
    
spec:
  replicas: 3
  
  image:
    repository: ghcr.io/phenotype-dev/api
    tag: v2.1.0
    pullPolicy: IfNotPresent
    
  resources:
    requests:
      cpu: 100m
      memory: 128Mi
    limits:
      cpu: 500m
      memory: 512Mi
      
  ports:
    - name: http
      port: 8080
      protocol: TCP
      expose: true
      servicePort: 80
      
  environment:
    - name: LOG_LEVEL
      value: info
    - name: DATABASE_URL
      valueFrom:
        secretKeyRef:
          name: db-credentials
          key: url
          
  strategy:
    type: RollingUpdate
    maxUnavailable: 25%
    maxSurge: 25%
    
  healthCheck:
    enabled: true
    initialDelaySeconds: 30
    periodSeconds: 10
    timeoutSeconds: 5
    successThreshold: 1
    failureThreshold: 3
    
  service:
    type: ClusterIP
    annotations:
      prometheus.io/scrape: "true"
      
  ingress:
    enabled: true
    host: api.kooshapari.com
    tls: true
    annotations:
      cert-manager.io/cluster-issuer: letsencrypt
```

### 6.2 Environment-Specific Overrides

Environment-specific values can be provided through separate files:

```yaml
# values-dev.yaml - Development environment
spec:
  replicas: 1
  image:
    tag: latest
  environment:
    - name: LOG_LEVEL
      value: debug
```

```yaml
# values-prod.yaml - Production environment
spec:
  replicas: 5
  image:
    tag: v2.1.0
  environment:
    - name: LOG_LEVEL
      value: warn
  resources:
    limits:
      cpu: 1000m
      memory: 1Gi
```

### 6.3 Configuration Validation

```go
// ValidateConfig validates deployment configuration
func ValidateConfig(config *DeploymentConfig) error {
    var errors []string
    
    // Required fields
    if config.APIVersion == "" {
        errors = append(errors, "apiVersion is required")
    }
    
    if config.Metadata.Name == "" {
        errors = append(errors, "metadata.name is required")
    }
    
    if config.Spec.Image.Repository == "" {
        errors = append(errors, "spec.image.repository is required")
    }
    
    // Value validation
    if config.Spec.Replicas != nil && *config.Spec.Replicas < 0 {
        errors = append(errors, "spec.replicas must be non-negative")
    }
    
    if config.Spec.Image.PullPolicy != "" {
        validPolicies := []string{"Always", "Never", "IfNotPresent"}
        if !contains(validPolicies, config.Spec.Image.PullPolicy) {
            errors = append(errors, "spec.image.pullPolicy must be one of: Always, Never, IfNotPresent")
        }
    }
    
    if len(errors) > 0 {
        return fmt.Errorf("configuration validation failed:\n%s", strings.Join(errors, "\n"))
    }
    
    return nil
}
```

---

## 7. Operations

### 7.1 Deployment Command

```bash
# Deploy from configuration file
deploy apply -f deployment.yaml

# Deploy with specific environment
deploy apply -f deployment.yaml --env production

# Dry-run deployment
deploy apply -f deployment.yaml --dry-run

# Deploy with timeout
deploy apply -f deployment.yaml --timeout 10m

# Deploy with wait
deploy apply -f deployment.yaml --wait
```

### 7.2 Rollback Command

```bash
# Rollback to previous version
deploy rollback phenotype-api -n production

# Rollback to specific revision (Helm)
deploy rollback phenotype-api -n production --revision 3

# Rollback with timeout
deploy rollback phenotype-api -n production --timeout 5m
```

### 7.3 Status Command

```bash
# Get deployment status
deploy status phenotype-api -n production

# Watch status
deploy status phenotype-api -n production --watch

# Output as JSON
deploy status phenotype-api -n production -o json
```

### 7.4 List Command

```bash
# List all deployments
deploy list

# List in specific namespace
deploy list -n production

# List with labels
deploy list -l app.kubernetes.io/part-of=phenotype
```

---

## 8. Monitoring

### 8.1 Metrics

The Deploy system exports Prometheus-compatible metrics:

```go
// Metrics definitions
var (
    deploymentTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "deploy_deployments_total",
            Help: "Total number of deployments",
        },
        []string{"namespace", "status", "deployer"},
    )
    
    deploymentDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "deploy_deployment_duration_seconds",
            Help:    "Deployment duration in seconds",
            Buckets: prometheus.DefBuckets,
        },
        []string{"namespace", "deployer"},
    )
    
    deploymentStatus = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "deploy_deployment_status",
            Help: "Current deployment status (1=ready, 0=not ready)",
        },
        []string{"namespace", "name"},
    )
    
    rollbackTotal = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "deploy_rollbacks_total",
            Help: "Total number of rollbacks",
        },
        []string{"namespace", "trigger"},
    )
)
```

### 8.2 Logging

Structured logging using slog:

```go
// Log attributes
var (
    AttrDeploymentID = slog.String("deployment_id", "")
    AttrNamespace    = slog.String("namespace", "")
    AttrName         = slog.String("name", "")
    AttrStatus       = slog.String("status", "")
    AttrDuration     = slog.Duration("duration", 0)
    AttrError        = slog.Any("error", nil)
)

// Log examples
deployer.logger.Info("deployment started",
    AttrDeploymentID(id),
    AttrNamespace(config.Namespace),
    AttrName(config.Name),
)

deployer.logger.Info("deployment completed",
    AttrDeploymentID(id),
    AttrStatus("success"),
    AttrDuration(duration),
)

deployer.logger.Error("deployment failed",
    AttrDeploymentID(id),
    AttrError(err),
    AttrStatus("failed"),
)
```

### 8.3 Tracing

OpenTelemetry integration for distributed tracing:

```go
// Trace deployment
ctx, span := tracer.Start(ctx, "deployment",
    trace.WithAttributes(
        attribute.String("deployment.name", config.Name),
        attribute.String("deployment.namespace", config.Namespace),
        attribute.String("deployment.image", config.Image),
        attribute.Int("deployment.replicas", config.Replicas),
    ),
)
defer span.End()

// Add events
span.AddEvent("manifest_generated")
span.AddEvent("kubectl_started")
span.AddEvent("kubectl_completed")
```

---

## 9. Security

### 9.1 RBAC

Minimum required RBAC for Deploy operations:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: deploy-operator
rules:
  # Deployments
  - apiGroups: ["apps"]
    resources: ["deployments"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  
  # Pods (for status checking)
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  
  # Services
  - apiGroups: [""]
    resources: ["services"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  
  # Ingress
  - apiGroups: ["networking.k8s.io"]
    resources: ["ingresses"]
    verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
  
  # ConfigMaps and Secrets
  - apiGroups: [""]
    resources: ["configmaps", "secrets"]
    verbs: ["get", "list"]
  
  # Events (for logging)
  - apiGroups: [""]
    resources: ["events"]
    verbs: ["create", "patch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: deploy-operator-binding
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: deploy-operator
subjects:
  - kind: ServiceAccount
    name: deploy-operator
    namespace: default
```

### 9.2 Image Security

Image security requirements:

1. **Signed Images:** Images SHOULD be signed using Cosign
2. **SBOM:** Images SHOULD include SBOM attestations
3. **Vulnerability Scanning:** Images MUST pass vulnerability scans
4. **Minimal Base:** Images SHOULD use minimal base images (distroless, scratch)

```yaml
# Kyverno policy for image verification
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: verify-image-signatures
spec:
  validationFailureAction: enforce
  rules:
    - name: check-image-signature
      match:
        resources:
          kinds:
            - Pod
      verifyImages:
        - imageReferences:
            - "ghcr.io/phenotype-dev/*"
          required: true
          attestors:
            - entries:
                - keyless:
                    issuer: "https://token.actions.githubusercontent.com"
                    subject: "https://github.com/phenotype-dev/*"
```

---

## 10. Testing

### 10.1 Unit Testing

```go
// Mock command execution for testing
type mockCommandRunner struct {
    responses map[string]struct {
        output []byte
        err    error
    }
}

func TestKubernetesDeployer_Deploy(t *testing.T) {
    tests := []struct {
        name    string
        config  Config
        mock    mockCommandRunner
        wantErr bool
    }{
        {
            name: "successful deployment",
            config: Config{
                Name:      "test-app",
                Namespace: "default",
                Replicas:  1,
                Image:     "nginx:latest",
            },
            mock: mockCommandRunner{
                responses: map[string]struct {
                    output []byte
                    err    error
                }{
                    "kubectl apply -f -": {output: []byte("deployment.apps/test-app created"), err: nil},
                },
            },
            wantErr: false,
        },
        {
            name: "deployment fails",
            config: Config{
                Name:      "test-app",
                Namespace: "default",
                Replicas:  1,
                Image:     "nginx:latest",
            },
            mock: mockCommandRunner{
                responses: map[string]struct {
                    output []byte
                    err    error
                }{
                    "kubectl apply -f -": {output: nil, err: errors.New("connection refused")},
                },
            },
            wantErr: true,
        },
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            deployer := NewKubernetesDeployer(tt.config)
            deployer.commandRunner = &tt.mock
            
            err := deployer.Deploy(context.Background())
            if tt.wantErr {
                assert.Error(t, err)
            } else {
                assert.NoError(t, err)
            }
        })
    }
}
```

### 10.2 Integration Testing

```go
func TestKubernetesDeployer_Integration(t *testing.T) {
    if os.Getenv("INTEGRATION") != "true" {
        t.Skip("Set INTEGRATION=true to run integration tests")
    }
    
    // Requires running k3d/kind cluster
    ctx := context.Background()
    
    deployer := NewKubernetesDeployer(Config{
        Name:      "integration-test",
        Namespace: "default",
        Replicas:  1,
        Image:     "nginx:alpine",
    })
    
    // Test deployment
    err := deployer.Deploy(ctx)
    require.NoError(t, err)
    
    // Verify status
    status, err := deployer.Status(ctx)
    require.NoError(t, err)
    require.Equal(t, int32(1), status.DesiredReplicas)
    
    // Cleanup
    defer func() {
        cmd := exec.Command("kubectl", "delete", "deployment", "integration-test", "-n", "default")
        cmd.Run()
    }()
}
```

### 10.3 E2E Testing

```go
func TestE2E_FullDeploymentLifecycle(t *testing.T) {
    if os.Getenv("E2E") != "true" {
        t.Skip("Set E2E=true to run E2E tests")
    }
    
    ctx := context.Background()
    
    // Step 1: Deploy initial version
    v1Deployer := NewKubernetesDeployer(Config{
        Name:      "e2e-test",
        Namespace: "default",
        Replicas:  2,
        Image:     "nginx:1.24",
    })
    
    err := v1Deployer.Deploy(ctx)
    require.NoError(t, err)
    
    // Step 2: Verify deployment
    status, err := v1Deployer.Status(ctx)
    require.NoError(t, err)
    require.Equal(t, int32(2), status.ReadyReplicas)
    
    // Step 3: Deploy new version
    v2Deployer := NewKubernetesDeployer(Config{
        Name:      "e2e-test",
        Namespace: "default",
        Replicas:  2,
        Image:     "nginx:1.25",
    })
    
    err = v2Deployer.Deploy(ctx)
    require.NoError(t, err)
    
    // Step 4: Verify new version
    status, err = v2Deployer.Status(ctx)
    require.NoError(t, err)
    require.Equal(t, int32(2), status.ReadyReplicas)
    
    // Step 5: Rollback
    err = v2Deployer.Rollback(ctx)
    require.NoError(t, err)
    
    // Step 6: Verify rollback
    status, err = v1Deployer.Status(ctx)
    require.NoError(t, err)
    require.Equal(t, int32(2), status.ReadyReplicas)
    
    // Cleanup
    cmd := exec.Command("kubectl", "delete", "deployment", "e2e-test", "-n", "default")
    cmd.Run()
}
```

---

## 11. Appendices

### Appendix A: Glossary

| Term | Definition |
|------|------------|
| **Chart** | Helm package containing Kubernetes manifests |
| **Deployment** | Kubernetes resource managing pod replicas |
| **Helm** | Kubernetes package manager |
| **kubectl** | Kubernetes command-line tool |
| **Namespace** | Kubernetes virtual cluster partition |
| **Pod** | Smallest deployable Kubernetes unit |
| **Release** | Instance of a deployed Helm chart |
| **ReplicaSet** | Kubernetes controller ensuring pod count |
| **Rollback** | Reverting to previous deployment version |
| **Service** | Kubernetes network endpoint abstraction |

### Appendix B: Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| CONFIG_INVALID | Invalid configuration | 400 |
| DEPLOYMENT_FAILED | Deployment operation failed | 500 |
| NAMESPACE_NOT_FOUND | Target namespace doesn't exist | 404 |
| AUTH_DENIED | Authentication/authorization failed | 403 |
| TIMEOUT | Operation timed out | 504 |
| ROLLBACK_FAILED | Rollback operation failed | 500 |
| STATUS_UNAVAILABLE | Cannot determine deployment status | 503 |

### Appendix C: OpenAPI Schema

```yaml
openapi: 3.0.0
info:
  title: Deploy API
  version: 1.0.0
paths:
  /deployments:
    post:
      summary: Create deployment
      requestBody:
        content:
          application/yaml:
            schema:
              $ref: '#/components/schemas/DeploymentConfig'
      responses:
        202:
          description: Deployment accepted
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DeploymentResponse'
  /deployments/{name}/status:
    get:
      summary: Get deployment status
      responses:
        200:
          description: Deployment status
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/DeploymentStatus'

components:
  schemas:
    DeploymentConfig:
      type: object
      required: [apiVersion, kind, metadata, spec]
      properties:
        apiVersion:
          type: string
        kind:
          type: string
        metadata:
          $ref: '#/components/schemas/Metadata'
        spec:
          $ref: '#/components/schemas/DeploymentSpec'
    
    Metadata:
      type: object
      properties:
        name:
          type: string
        namespace:
          type: string
    
    DeploymentSpec:
      type: object
      properties:
        replicas:
          type: integer
        image:
          $ref: '#/components/schemas/ImageSpec'
    
    ImageSpec:
      type: object
      required: [repository]
      properties:
        repository:
          type: string
        tag:
          type: string
        pullPolicy:
          type: string
          enum: [Always, Never, IfNotPresent]
```

---

*End of Specification*
