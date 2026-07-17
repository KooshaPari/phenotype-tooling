# Security Best Practices Reference

## 1. OWASP Top 10 (2021)

### A01: Broken Access Control
- Deny-by-default for all resources
- Validate permissions at every API endpoint
- Use short-lived JWT tokens
- **AVOID**: URL parameter modification, force browsing

### A02: Cryptographic Failures
- TLS 1.2+ with forward secrecy
- Strong hashing: Argon2, bcrypt, PBKDF2
- Authenticated encryption (AEAD)
- **AVOID**: MD5/SHA1, ECB mode, default keys

### A03: Injection
- Parameterized queries, ORMs
- Server-side allowlist validation
- **AVOID**: String concatenation in queries

### A04: Insecure Design
- Threat modeling during design
- Secure design patterns

### A05: Security Misconfiguration
- Hardened configurations
- Remove unused dependencies

### A06: Vulnerable Components
- Automated dependency scanning
- SBOM generation
- Regular CVE monitoring

### A07: Auth Failures
- Strong password policies
- MFA implementation
- Account lockout after failures

### A08: Software Integrity
- Digital signatures for updates
- Verify via checksums

### A09: Logging/Monitoring
- Log security events
- Structured JSON logging

### A10: Server-Side Request Forgery
- Denylist internal services
- Sanitize user URLs

---

## 2. Secure Coding

### Input Validation
```python
# Allowlist validation
def validate_user_id(id: str) -> int:
    parsed = int(id)
    if parsed <= 0 or parsed > MAX_ID:
        raise ValidationError('Invalid user ID')
    return parsed
```

### Output Encoding
```python
import html

def escape_html(unsafe: str) -> str:
    return html.escape(unsafe)
```

---

## 3. API Security

### Security Headers
```python
res.setHeader('Strict-Transport-Security', 'max-age=31536000')
res.setHeader('X-Content-Type-Options', 'nosniff')
res.setHeader('X-Frame-Options', 'DENY')
res.setHeader('Content-Security-Policy', "default-src 'self'")
```

### Rate Limiting
```python
from fastapi import FastAPI
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api")
@limiter.limit("100/minute")
async def api_endpoint(request: Request):
    pass
```

---

## 4. Secrets Management

### Environment Variables
```python
# GOOD
api_key = os.environ['API_KEY']

# BAD - Never hardcode
api_key = 'sk-1234567890'
```

### Vault Integration
```python
from hvac import Client

vault = Client(url='http://vault:8200', token=os.environ['VAULT_TOKEN'])
secret = vault.secrets.kv.v2.read_secret_version(path='myapp/api-key')
```

---

## 5. Dependency Security

### Audit Script
```json
{
  "scripts": {
    "security:audit": "npm audit --audit-level=high",
    "security:check": "snyk test"
  }
}
```

### .gitignore
```
.env
.env.local
*.pem
*.key
```

---

## 6. Zero Trust Architecture

**Principle**: Never trust, always verify

### Core Pillars
| Pillar | Implementation |
|--------|----------------|
| Identity | Strong auth (MFA, passwordless) |
| Device | Device posture, health checks |
| Network | Micro-segmentation, mTLS |
| Application | RBAC/ABAC, API gateways |
| Data | Encryption at rest/transit |

### mTLS Service-to-Service
```yaml
# Istio PeerAuthentication
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
spec:
  mtls:
    mode: STRICT
```

---

## 7. Supply Chain Security

### Software Bill of Materials (SBOM)
```bash
# Generate SBOM
syft packages dir:./src -o spdx-json > sbom.json
syft packages dir:./src -o cyclonedx-json > sbom.cdx.json

# Scan for vulnerabilities
grype sbom:sbom.json
```

### Dependency Pinning
```toml
# pyproject.toml - Pin exact versions
[project]
dependencies = [
    "fastapi==0.109.0",
    "pydantic==2.5.3",
]

# Use lockfile
pip-compile requirements.in --output-file requirements.lock
```

### SLSA Framework Levels
| Level | Requirements |
|-------|--------------|
| 1 | Build process documented |
| 2 | Version control, build service |
| 3 | Hardened builds, non-falsifiable provenance |
| 4 | Two-party review, hermetic builds |

---

## 8. API Security Patterns

### Authentication Patterns
```python
# OAuth 2.1 + PKCE (public clients)
from authlib.integrations.fastapi_client import OAuth

oauth = OAuth()
oauth.register(
    name='auth0',
    client_id='YOUR_CLIENT_ID',
    server_metadata_url='https://your-domain.auth0.com/.well-known/openid-configuration',
    client_kwargs={'code_challenge_method': 'S256'}
)

# JWT validation
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

async def get_current_user(token: str = Depends(security)):
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["RS256"])
        return payload
    except JWTError:
        raise HTTPException(401, "Invalid token")
```

### API Key Rotation
```python
# Support multiple valid keys during rotation
VALID_API_KEYS = {
    "key_v1": datetime(2024, 1, 1),  # Deprecated
    "key_v2": datetime(2025, 1, 1),  # Current
}

def validate_api_key(key: str) -> bool:
    if key not in VALID_API_KEYS:
        return False
    if VALID_API_KEYS[key] < datetime.now() - timedelta(days=30):
        log.warning(f"Using deprecated API key: {key[:8]}...")
    return True
```

---

## 9. Container Security

### Dockerfile Best Practices
```dockerfile
# Use distroless base
FROM gcr.io/distroless/python3-debian12

# Non-root user
USER nonroot:nonroot

# Read-only filesystem
# docker run --read-only ...

# Drop all capabilities, add only needed
# docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE ...
```

### Container Scanning
```bash
# Scan image for vulnerabilities
trivy image myapp:latest
grype myapp:latest

# Scan Dockerfile
hadolint Dockerfile
```

---

## 10. Incident Response

### Security Incident Runbook
1. **Detect**: Alerting on anomalous patterns
2. **Contain**: Isolate affected systems
3. **Eradicate**: Remove threat, patch vulnerability
4. **Recover**: Restore services, verify integrity
5. **Post-mortem**: Document, improve, share learnings

### Log Security Events
```python
import structlog

logger = structlog.get_logger()

def log_security_event(event_type: str, details: dict):
    logger.info(
        "security_event",
        event_type=event_type,
        severity="high",
        **details
    )

# Usage
log_security_event("auth_failure", {
    "user": "alice",
    "ip": "192.168.1.100",
    "reason": "invalid_password"
})
```

---

## Quick Checklist

| Category | Do | Don't |
|----------|-----|-------|
| Access Control | Deny-by-default | Trust URL params |
| Cryptography | TLS 1.2+, Argon2 | MD5, SHA1 |
| Injection | Parameterized queries | String concat |
| Auth | MFA, passwordless | Credential stuffing |
| Secrets | Env vars, vault | Hardcode |
| Dependencies | Scan for CVEs, SBOM | Unknown packages |
| Supply Chain | Pin versions, SLSA | Latest tags |
| Containers | Distroless, non-root | Root, privileged |
| Network | mTLS, segmentation | Flat network |
| Logging | Structured, security events | Sensitive data |

---

## Production Security Checklist

- [ ] All OWASP Top 10 addressed
- [ ] HTTPS enforced (TLS 1.2+)
- [ ] Security headers configured
- [ ] Rate limiting on all endpoints
- [ ] MFA enabled for admin access
- [ ] API key rotation < 90 days
- [ ] Dependency scanning in CI
- [ ] SBOM generated for releases
- [ ] Container images scanned
- [ ] Secrets in vault, not env vars
- [ ] Audit logging enabled
- [ ] Incident response runbooks ready
