# DevOps & Platform Engineering Reference

## 1. CI/CD Pipeline Design

### 1.1 GitHub Actions

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Cache dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('**/pyproject.toml') }}

      - name: Install
        run: pip install -e .

      - name: Test
        run: pytest

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v1
```

### 1.2 Fast-Fail Gates

```
Stage 1 (fast):   Syntax → Lint → Type Check (0-30s)
Stage 2 (medium): Unit Tests → Security Scan (30s-2min)
Stage 3 (slow):   Integration Tests → Coverage (2-10min)
```

---

## 2. Container Patterns

### 2.1 Multi-stage Dockerfile

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
RUN pip install uv
COPY . .
RUN uv sync --prod

# Runtime stage
FROM python:3.12-slim
COPY --from=builder /app /app
USER 1000:1000
WORKDIR /app
CMD ["python", "-m", "app"]
```

### 2.2 Security Best Practices

```dockerfile
# Non-root user
RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -D appuser

# Read-only filesystem
USER 1000:1000

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

---

## 3. Docker Compose

```yaml
version: '3.8'
services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/app
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s

  db:
    image: postgres:15
    environment:
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
      POSTGRES_DB: app
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U user -d app"]
      interval: 10s
```

---

## 4. Infrastructure as Code

### 4.1 Terraform Structure

```
terraform/
├── main.tf
├── variables.tf
├── outputs.tf
├── modules/
│   ├── vpc/
│   ├── ecs/
│   └── rds/
└── environments/
    ├── dev/
    └── prod/
```

### 4.2 Module Example

```hcl
module "ecs_service" {
  source = "./modules/ecs"

  name        = var.service_name
  cluster_arn = var.cluster_arn
  container_image = var.container_image
  port        = var.port
  environment = var.environment

  desired_count = var.desired_count
  memory        = var.memory
  cpu           = var.cpu
}
```

---

## 5. Configuration Management

### 5.1 12-Factor App

| Factor | Implementation |
|--------|---------------|
| Codebase | Single git repo |
| Dependencies | Explicit (pyproject.toml, package.json) |
| Config | Environment variables |
| Backing Services | Treat as attached resources |
| Build/Release/Run | Strict separation |
| Processes | Stateless, share nothing |
| Port Binding | Export via port binding |
| Concurrency | Scale via processes |
| Disposability | Fast startup, graceful shutdown |
| Dev/Prod Parity | Keep environments similar |
| Logs | Treat as event stream |
| Admin Processes | Run in same environment |

### 5.2 Environment Config

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str = "sqlite:///db.sqlite"
    debug: bool = False
    log_level: str = "info"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---

## 6. Deployment Strategies

### 6.1 Rolling Update

```yaml
# Kubernetes
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

### 6.2 Blue-Green

```
[Load Balancer] → [Blue v1] (active)
               → [Green v2] (standby)

# Deploy to green, test, then switch
```

### 6.3 Canary

```
[Load Balancer] → 10% v2
               → 90% v1

# Gradually increase traffic
```

---

## 7. Secret Management

### 7.1 Environment Variables

```bash
# Never commit secrets
export API_KEY="sk-xxx"
export DATABASE_PASSWORD="secret"
```

### 7.2 Vault Integration

```python
import hvac

client = hvac.Client(url=os.environ['VAULT_ADDR'], token=os.environ['VAULT_TOKEN'])
secret = client.secrets.kv.v2.read_secret_version(path='app/database')
```

### 7.3 External Secrets Operator (Kubernetes)

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: api-key
spec:
  secretStoreRef:
    name: vault-backend
    kind: SecretStore
  target:
    name: api-key
  data:
    - secretKey: API_KEY
      remoteRef:
        key: app/secrets
        property: api_key
```

---

## 8. Monitoring Basics

### 8.1 Prometheus Metrics

```python
from prometheus_client import Counter, Histogram

requests_total = Counter('app_requests_total', 'Total requests')
request_duration = Histogram('app_request_duration_seconds', 'Request duration')

@app.get("/health")
def health():
    requests_total.inc()
    return {"status": "ok"}
```

### 8.2 Health Checks

```python
# Readiness: can handle requests
# Liveness: needs restart

@app.get("/health/readiness")
def readiness():
    if not db.is_connected():
        raise HTTPException(503, "Database unavailable")
    return {"status": "ready"}

@app.get("/health/liveness")
def liveness():
    return {"status": "alive"}
```

---

## 9. Kubernetes Basics

### 9.1 Pod

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app
spec:
  containers:
    - name: app
      image: myapp:latest
      ports:
        - containerPort: 8000
      resources:
        requests:
          memory: "256Mi"
          cpu: "250m"
        limits:
          memory: "512Mi"
          cpu: "500m"
```

### 9.2 Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: app
spec:
  selector:
    app: myapp
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
```

---

## Quick Reference

| Need | Use | NOT |
|------|-----|-----|
| CI/CD | GitHub Actions | Jenkins (legacy) |
| Containers | Docker | Raw processes |
| Orchestration | Kubernetes | Manual deployment |
| IaC | Terraform | Cloud console |
| Config | pydantic-settings | Manual env parsing |
| Secrets | Vault | Git-committed secrets |
| Monitoring | Prometheus + Grafana | Custom metrics |

---

*For detailed examples, see full DevOps research document.*
