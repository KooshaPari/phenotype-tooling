# Authentication & Authorization Best Practices Reference

## 1. Authentication Protocols (2026 Standards)

### OAuth 2.1 (RFC 9700) – The Secure Profile

**Mandatory for 2026**:
- Authorization Code + PKCE (no more implicit grant)
- Bearer token authentication + TLS 1.3
- Secure redirect validation

### PKCE (Proof Key for Code Exchange)

```
Flow:
1. Generate code_verifier (43-128 chars, random)
2. Create code_challenge = SHA256(code_verifier)
3. Authorization endpoint: ?code_challenge=...
4. Token endpoint: code_verifier + authorization_code

Server validates: SHA256(code_verifier) == code_challenge
```

**Critical**: Prevents authorization code interception attacks. Now mandatory for ALL apps.

### OpenID Connect (OIDC)

Identity layer on OAuth 2.0. Adds ID token + user info endpoint.

### SAML 2.0 (Enterprise)

Private back-channel authentication. Still common in enterprise federations.

### mTLS (Mutual TLS)

Bidirectional certificate verification. **2026 Update**: Public CAs stop issuing client auth certs after June 15, 2026 — enterprises must use private CAs.

---

## 2. Token Management

### JWT Token Lifecycle

**Access Token**: 15-60 min expiration
```
Header: { alg: "HS256", typ: "JWT" }
Payload: { email, roles, iat, exp, iss }
Signature: HMAC-SHA256(header.payload, secret)
```

**Refresh Token**: 30-90 days, rotated on each use

**Rotation Strategy** (2026 Best Practice):
- Issue new refresh token with each access token renewal
- Single-use tokens only
- **Reuse detection**: If refresh token reused, invalidate entire token family

### Token Validation (Critical)

Every service receiving a JWT must:
1. Verify signature (using issuer's public key)
2. Check expiration (not expired)
3. Validate issuer (trusted source)
4. Check token type (JWT, not other formats)

Never trust unvalidated tokens.

### Token Encryption (JWE)

If JWT payload contains sensitive data (PII, medical):
```
Use JWE (JSON Web Encryption)
Encrypt-then-sign for maximum security
```

### Token Revocation

- Implement blacklist (e.g., Redis) when user logs out
- Short expiration + rotation reduces revocation pressure
- Leakage is inevitable; rotation + reuse detection contain damage window

---

## 3. Authorization Models

### RBAC (Role-Based Access Control)

Assign users to roles → roles have permissions

```
User → Role (admin, editor, viewer)
Role → Permissions (create, read, update, delete)
```

**Strengths**: Simple, auditable | **Limits**: Can't express complex contextual rules

### ABAC (Attribute-Based Access Control)

Access decisions based on attributes:

```
"User can view document if:
  document.department == user.department
  AND document.status == 'draft'"

"Financial officer can approve if:
  user.role == 'finance_officer'
  AND amount < $10,000
  AND location == 'US Office'
  AND time.hour in [9-17]"
```

**Benefits**: Scales better, no policy explosion as resources grow

**2026 Migration Path**: Start RBAC → migrate to ABAC as complexity grows

---

## 4. Session Management & Cookies

### Secure Cookie Attributes

```
Set-Cookie: __Host-session=abc123;
            Path=/;
            HttpOnly;           # Blocks JavaScript access (XSS protection)
            Secure;             # HTTPS only (MITM protection)
            SameSite=Strict;    # CSRF protection
            Max-Age=3600;
```

**SameSite Values**:
- `Strict`: First-party context only (most secure)
- `Lax`: First-party + safe cross-site requests (default, balanced)
- `None`: Cross-site (requires Secure flag + HTTPS)

**__Host- Prefix**: Cookie limited to this domain, prevents hijacking by subdomains

---

## 5. Multi-Factor Authentication (MFA)

### TOTP (Time-Based One-Time Password)

```
Shared secret + current timestamp → 6-digit code (30-sec window)

Implementation:
1. User enables MFA
2. App generates secret, shows QR code
3. User scans with authenticator app (Google Authenticator, Authy)
4. User enters TOTP code to verify
5. Backup codes generated (one-time use)
```

**Time-skew tolerance**: ±1 min for clock drift

### Phishing-Resistant MFA (2026 Requirement)

**WebAuthn/FIDO2**: Cryptographic key-based, passwordless
- Private key stays on authenticator (phone, hardware key)
- Origin-bound (can't reuse on phishing sites)
- Biometric/PIN required

**Status**: Apple, Google, Microsoft all committed to passkey adoption

---

## 6. Passwordless Authentication

### WebAuthn/FIDO2 Flow

```
1. User clicks "Sign in"
2. Browser challenges with random nonce
3. Authenticator signs nonce with private key
4. Server verifies signature with stored public key
```

**Security Properties**:
- Phishing-resistant (origin-bound)
- No password database to breach
- Biometric + private key required
- Works across devices (cloud-synced)

### Passkey Ecosystem (2026 Mainstream)

iCloud Keychain, Google Password Manager, Microsoft Authenticator all support passkey sync

---

## 7. Password Hashing

### Recommendation (Rank Order)

1. **Argon2id** (2026 preferred):
   - Winner of Password Hashing Competition
   - Resistant to GPU/ASIC/side-channel attacks
   - Min: 19 MiB memory, 2 iterations
   - Security-conscious: 128 MiB, 3-5 iterations
   - Target: 200-500ms per hash

2. **Scrypt**: Alternative when Argon2 unavailable

3. **Bcrypt** (legacy only):
   - Cost 13-14 → 250-500ms
   - 72-byte password limit
   - Only for existing systems

4. **PBKDF2** (avoid new projects): 100K+ iterations needed

### Implementation

```python
from argon2 import PasswordHasher

ph = PasswordHasher()
hash = ph.hash(password)  # Stores hash with salt

# Verify
try:
    ph.verify(hash, password)
except VerifyMismatchError:
    # Password incorrect
```

---

## 8. API Key Management

### Generation & Storage

- Generate using cryptographically secure RNG
- Store in secrets manager (AWS Secrets Manager, Vault, etc.)
- Never commit to version control

### Rotation Strategy

**Two-Active-Key Pattern**:
1. Generate new key (key 3)
2. Update all consumers
3. Monitor for failures
4. Revoke oldest key (key 1)

**Rotation schedule**:
- High-privilege (write/delete): daily or weekly
- Low-privilege (read-only): monthly

### Monitoring & Audit

- Log all API key operations (create, rotate, revoke, use)
- Anomaly detection (unusual locations, IP, frequency)
- Secrets scanning: gitleaks, gitguardian

---

## 9. Zero Trust Architecture

### Core Principle

"Never Trust, Always Verify" — Assume breach

### Five Pillars

1. **Continuous Authentication**: Verify every access request independently
2. **Identity Verification**: Strong MFA, behavioral analytics, device health
3. **Explicit Verification**: Authenticate ALL users/devices/apps
4. **Least Privilege**: Minimum permissions, time-limited access
5. **Micro-Segmentation**: Network zones by application; enforce at app layer

### Implementation in 2026

- Shift from perimeter-based to identity-based security
- IAM + network ACLs + service mesh (Istio/Linkerd)
- Continuous monitoring with anomaly detection

---

## 10. Common Vulnerabilities & Mitigations

### OWASP Top 10 2025 — Identification & Authentication Failures (#7)

| Vulnerability | Mitigation |
|---|---|
| Credential stuffing | MFA, breach monitoring (Have I Been Pwned API) |
| Weak passwords | 12+ chars minimum, blacklist common passwords |
| Missing MFA | Require for admin accounts, encourage for users |
| Session fixation | Regenerate session IDs on login |
| Insecure recovery | Verify email before recovery, time-limited tokens |
| Plain-text passwords | Use Argon2id hashing |
| Missing token validation | Validate signature, expiration, issuer on every request |
| Account lockout vulnerability | Auto-lock after N failures, require admin unlock |

### Rate Limiting

Brute-force protection on login:
- Max 3 attempts per minute
- Exponential cooldown (locked 5 min, then 10 min, etc.)

### Secrets Scanning

- Pre-commit hooks (detect API keys, tokens)
- CI scanning (pip-audit, npm audit, gitleaks)
- Regular breach monitoring

---

## 11. Production Readiness Checklist

- [ ] OAuth 2.1 + PKCE implemented (no implicit grant)
- [ ] JWT signature, expiration, issuer validated on every request
- [ ] Refresh token rotation with reuse detection
- [ ] HTTPS + TLS 1.3 enforced
- [ ] Session cookies: HttpOnly + Secure + SameSite=Lax
- [ ] Password hashing: Argon2id (min 19 MiB, 2 iter)
- [ ] MFA enabled for admin accounts
- [ ] API keys in secrets manager (rotated regularly)
- [ ] Rate limiting on login (max 3 attempts/min)
- [ ] Audit logging for auth events
- [ ] Secrets scanning in CI/CD
- [ ] CORS configured restrictively
- [ ] Account lockout policy (N failed attempts → lock)

---

## References

- OWASP Top 10 2025: https://owasp.org/Top10/2025/
- RFC 9700 (OAuth 2.1): https://tools.ietf.org/html/rfc9700
- NIST SP 800-207 (Zero Trust): https://nvlpubs.nist.gov/nistpubs/specialpublications/nist.sp.800-207.pdf
- OWASP Auth Cheat Sheet: https://cheatsheetseries.owasp.org
- FIDO Alliance Passkeys: https://fidoalliance.org/passkeys/
- WebAuthn Spec: https://www.w3.org/TR/webauthn-3/
