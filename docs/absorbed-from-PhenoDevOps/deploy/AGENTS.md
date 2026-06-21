# Agent Rules - PhenoDevOps Deploy

**This project is managed through AgilePlus.**

## Project Overview

### Name
PhenoDevOps Deploy (Kubernetes & Helm Deployment System)

### Description
The Phenotype Deploy system provides comprehensive Kubernetes and Helm deployment capabilities for the Phenotype ecosystem. It enables declarative, versioned, and reproducible application deployments across multiple environments with support for rollback and status monitoring.

### Location
`/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoDevOps/deploy`

### Language Stack
- **Go**: Primary implementation (k8s.go)
- **Kubernetes**: Deployment manifests, Helm charts
- **Helm**: Package management
- **YAML**: Configuration definitions

### Purpose & Goals
- **Mission**: Provide reliable, automated deployment capabilities for Phenotype services
- **Primary Goal**: Enable declarative, versioned Kubernetes deployments
- **Secondary Goals**:
  - Support Helm chart lifecycle management
  - Provide rollback capabilities
  - Enable environment-specific configuration
  - Deliver comprehensive deployment status monitoring

### Key Responsibilities
1. **Kubernetes Deployment**: Manage Deployment, Service, ConfigMap resources
2. **Helm Operations**: Install, upgrade, rollback charts
3. **Namespace Management**: Resource isolation and organization
4. **Status Monitoring**: Real-time deployment status and health
5. **Configuration**: Environment-specific config handling

---

## Quick Start Commands

### Prerequisites

```bash
# Go 1.24+
brew install go@1.24

# Kubernetes CLI (kubectl)
brew install kubectl

# Helm package manager
brew install helm

# Access to Kubernetes cluster
kubectl cluster-info
```

### Installation

```bash
# Navigate to deploy
cd /Users/kooshapari/CodeProjects/Phenotype/repos/PhenoDevOps/deploy

# Install Go dependencies
cd .. && go mod download

# Build the deploy module
cd deploy
go build
```

### Development Environment Setup

```bash
# Copy environment configuration
cp .env.example .env

# Configure kubeconfig
export KUBECONFIG=~/.kube/config

# Verify cluster access
kubectl get nodes

# Create namespace
kubectl create namespace phenotype-dev
```

### Running Examples

```bash
# Deploy example application
go run k8s.go deploy --file examples/deployment.yaml

# Deploy with Helm
go run k8s.go helm-install --chart ./charts/phenotype-service

# Check deployment status
go run k8s.go status --deployment phenotype-api

# Rollback deployment
go run k8s.go rollback --deployment phenotype-api --revision 2
```

### Verification

```bash
# Run tests
cd .. && go test ./deploy/...

# Verify deployments
kubectl get deployments -n phenotype-dev

# Check pod status
kubectl get pods -n phenotype-dev

# View logs
kubectl logs -l app=phenotype-api -n phenotype-dev
```

---

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer                                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │   Deploy     │  │   Rollback   │  │    Status    │           │
│  │   Handler    │  │   Handler    │  │   Handler    │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
└─────────┼─────────────────┼─────────────────┼─────────────────────┘
          │                 │                 │
          └─────────────────┼─────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Core Engine                                    │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐  ┌─────────────────────┐             │
│  │  Kubernetes         │  │  Helm               │             │
│  │  Deployer           │  │  Deployer           │             │
│  │                     │  │                     │             │
│  │  • Deployments      │  │  • Install          │             │
│  │  • Services         │  │  • Upgrade          │             │
│  │  • ConfigMaps       │  │  • Rollback         │             │
│  │  • Ingress          │  │  • Uninstall        │             │
│  └──────────┬──────────┘  └──────────┬──────────┘             │
│             │                        │                        │
│             └──────────┬─────────────┘                        │
│                        │                                      │
│                        ▼                                      │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              Manifest Generator                         │  │
│  │                                                         │  │
│  │  • Template processing                                  │  │
│  │  • Environment substitution                             │  │
│  │  • Validation                                           │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Execution Layer                                │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │   kubectl    │  │    helm      │  │   kubeconfig         │   │
│  │   process    │  │   process    │  │   manager            │   │
│  │              │  │              │  │                      │   │
│  │ • Apply      │  │ • Install    │  │ • Context switch     │   │
│  │ • Delete     │  │ • Upgrade    │  │ • Auth management    │   │
│  │ • Get        │  │ • Rollback   │  │ • Multi-cluster      │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Deployment Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Flow                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. Manifest Loading                                            │
│  ┌─────────┐                                                     │
│  │ YAML/   │  Load and parse deployment manifests               │
│  │ JSON    │                                                     │
│  └────┬────┘                                                     │
│       │                                                         │
│       ▼                                                         │
│  2. Template Processing                                         │
│  ┌─────────┐                                                     │
│  │ Templating│  Environment variables, config injection            │
│  │ Engine  │                                                     │
│  └────┬────┘                                                     │
│       │                                                         │
│       ▼                                                         │
│  3. Validation                                                  │
│  ┌─────────┐                                                     │
│  │ Schema  │  Validate manifest structure and values             │
│  │ Validate│                                                     │
│  └────┬────┘                                                     │
│       │                                                         │
│       ▼                                                         │
│  4. Pre-Deployment                                              │
│  ┌─────────┐                                                     │
│  │ Pre-flight│  Resource checks, quota validation                │
│  │ Checks  │                                                     │
│  └────┬────┘                                                     │
│       │                                                         │
│       ▼                                                         │
│  5. Execution                                                   │
│  ┌─────────┐                                                     │
│  │ kubectl │  Apply manifests to cluster                        │
│  │ apply   │                                                     │
│  └────┬────┘                                                     │
│       │                                                         │
│       ▼                                                         │
│  6. Verification                                                │
│  ┌─────────┐                                                     │
│  │ Health  │  Check deployment health and readiness             │
│  │ Checks  │                                                     │
│  └────┬────┘                                                     │
│       │                                                         │
│       ▼                                                         │
│  7. Completion                                                  │
│  ┌─────────┐                                                     │
│  │ Done    │  Deployment successful                               │
│  │ or      │  or Rollback on failure                              │
│  │ Rollback│                                                     │
│  └─────────┘                                                     │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Helm Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                    Helm Chart Lifecycle                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │  helm   │───▶│  helm   │───▶│  helm   │───▶│  helm   │     │
│  │ install │    │ upgrade │    │ status  │    │ rollback│     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│       │              │              │              │          │
│       ▼              ▼              ▼              ▼          │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐     │
│  │ Release │    │ Release │    │ Release │    │ Release │     │
│  │ v1      │    │ v2      │    │ Info    │    │ v1      │     │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘     │
│                                                                 │
│  Revision History:                                              │
│  • Revision 1: Initial deployment                                 │
│  • Revision 2: Upgrade with new image                           │
│  • Revision 3: Rollback to revision 1                            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quality Standards

### Testing Requirements

#### Test Coverage
- **Minimum Coverage**: 70% for deployment logic
- **Critical Paths**: 90% for rollback and health checks
- **Integration Tests**: Required for all deployment types

#### Test Categories
```bash
# Unit tests
cd .. && go test ./deploy/...

# Integration tests (requires cluster)
go test ./deploy/... -tags integration

# Helm tests
helm test <release-name>
```

### Code Quality

#### Go Standards
```bash
# Linting
cd .. && golangci-lint run ./deploy/...

# Formatting
gofmt -l -w deploy/

# Testing
go test -race ./deploy/...
```

### Deployment Standards

| Check | Requirement | Verification |
|-------|-------------|--------------|
| Pre-flight | Resource quotas | kubectl describe |
| Health checks | Liveness, readiness | probe success |
| Rollback | < 60s recovery | timer measure |
| Idempotency | Same result on re-run | test suite |

---

## Git Workflow

### Branch Strategy

```
main
  │
  ├── feature/helm-rollback
  │   └── PR #15 → squash merge ──┐
  │                              │
  ├── feature/multi-cluster      │
  │   └── PR #16 → squash merge ──┤
  │                              │
  ├── fix/deployment-timeout     │
  │   └── PR #17 → squash merge ──┤
  │                              │
  └── hotfix/rollback-failure ───┘
      └── PR #18 → merge commit
```

### Branch Naming

```
feature/<component>-<description>
fix/<issue>-<scope>
chore/<maintenance>
docs/<topic>
```

### Commit Conventions

```
feat(helm): add rollback support

Implements helm rollback with revision tracking.
Supports rollback to any previous revision.

- Rollback handler implementation
- Revision history tracking
- Automatic rollback on deployment failure

Closes #33

fix(k8s): resolve deployment timeout issue

Large deployments were timing out during rolling updates.
Now properly waits for pod readiness with configurable timeout.
```

---

## File Structure

```
PhenoDevOps/deploy/
├── docs/                       # Documentation
│   ├── SPEC.md                 # This specification
│   ├── ADR/                    # Architecture decisions
│   │   ├── ADR-001-kubernetes-native-deployment.md
│   │   ├── ADR-002-helm-package-manager.md
│   │   └── ADR-003-kubectl-exec.md
│   ├── SOTA.md                 # State of the art research
│   └── PLAN.md                 # Implementation plan
│
├── examples/                   # Example deployments
│   ├── deployment.yaml
│   ├── service.yaml
│   └── helm-chart/
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/
│
├── k8s.go                      # Kubernetes operations
│
├── README.md
└── AGENTS.md                   # This file
```

---

## CLI Commands

### Deploy CLI

```bash
# Kubernetes Operations
go run k8s.go deploy --file deployment.yaml
go run k8s.go deploy --dir ./manifests/
go run k8s.go delete --deployment phenotype-api
go run k8s.go status --deployment phenotype-api

# Helm Operations
go run k8s.go helm-install --chart ./charts/service
go run k8s.go helm-upgrade --chart ./charts/service --version 2.0.0
go run k8s.go helm-rollback --release phenotype-api --revision 1
go run k8s.go helm-uninstall --release phenotype-api

# Namespace Operations
go run k8s.go create-namespace --name phenotype-dev
go run k8s.go delete-namespace --name phenotype-dev

# Configuration
go run k8s.go config set-context --cluster prod
go run k8s.go config view

# Diagnostics
go run k8s.go doctor
go run k8s.go logs --deployment phenotype-api
go run k8s.go exec --pod phenotype-api-xxx --command "sh"
```

### Development Commands

```bash
# Build
cd .. && go build ./deploy/...

# Test
cd .. && go test ./deploy/...

# Lint
cd .. && golangci-lint run ./deploy/...

# Format
gofmt -l -w deploy/
```

---

## Troubleshooting

### Common Issues

#### Issue: Deployment fails with "ImagePullBackOff"

**Symptoms:**
```
ImagePullBackOff: Back-off pulling image
```

**Diagnosis:**
```bash
# Check image name
kubectl describe pod <pod-name> -n <namespace>

# Verify image exists
docker pull <image-name>

# Check image pull secrets
kubectl get secrets -n <namespace>
```

**Resolution:**
- Correct image name/tag in deployment
- Add image pull secrets for private registries
- Verify Docker registry is accessible

---

#### Issue: Helm upgrade fails with "has no deployed releases"

**Symptoms:**
```
Error: "phenotype-api" has no deployed releases
```

**Diagnosis:**
```bash
# Check release status
helm list --all --namespace phenotype-dev

# Check release history
helm history phenotype-api --namespace phenotype-dev

# Verify namespace
kubectl get namespace phenotype-dev
```

**Resolution:**
```bash
# Delete failed release
helm delete phenotype-api --namespace phenotype-dev

# Or force new release
helm install phenotype-api ./chart --namespace phenotype-dev --replace
```

---

#### Issue: Rollback timeout

**Symptoms:**
Rollback operation times out or hangs.

**Diagnosis:**
```bash
# Check current revision
helm history phenotype-api

# Check pod status
kubectl get pods -n phenotype-dev

# View rollback events
kubectl get events -n phenotype-dev --sort-by='.lastTimestamp'
```

**Resolution:**
- Increase rollback timeout: `--timeout 10m`
- Force rollback: `--force`
- Check resource constraints
- Manually scale down/up if needed

---

#### Issue: kubeconfig not found

**Symptoms:**
```
Unable to connect to the server: no such file or directory
```

**Diagnosis:**
```bash
# Check kubeconfig
ls -la ~/.kube/config
echo $KUBECONFIG

# Test connection
kubectl cluster-info
```

**Resolution:**
```bash
# Set kubeconfig
export KUBECONFIG=~/.kube/config

# Or merge configs
export KUBECONFIG=~/.kube/config:~/.kube/prod-config

# Verify context
kubectl config current-context
```

---

### Debug Mode

```bash
# Enable verbose logging
export DEPLOY_LOG_LEVEL=debug

# kubectl verbose
kubectl apply -f deployment.yaml -v=8

# Helm debug
helm install phenotype-api ./chart --debug --dry-run

# View raw API calls
kubectl apply -f deployment.yaml -v=9 2>&1 | tee api-calls.log
```

### Recovery Procedures

```bash
# Emergency rollback
helm rollback phenotype-api 1 --force

# Scale to zero (emergency stop)
kubectl scale deployment phenotype-api --replicas=0

# Delete and recreate
kubectl delete -f deployment.yaml
kubectl apply -f deployment.yaml

# Drain node (maintenance)
kubectl drain <node-name> --ignore-daemonsets
```

---

## Agent Self-Correction & Verification Protocols

### Critical Rules

1. **Safety First**
   - Always run pre-flight checks
   - Validate manifests before apply
   - Test in staging before production
   - Keep rollback ready

2. **Idempotency**
   - Deployments must be idempotent
   - Same input produces same output
   - Handle re-runs gracefully
   - Check current state before changes

3. **Observability**
   - Log all deployment actions
   - Track revision history
   - Monitor deployment health
   - Alert on failures

4. **Multi-Environment**
   - Separate configs per environment
   - Never mix dev/prod contexts
   - Use namespaces for isolation
   - Environment-specific secrets

---

*This AGENTS.md is a living document. Update it as PhenoDevOps Deploy evolves.*
