# Research: JWT-Based Authentication & Authorization

**Feature**: 001-jwt-auth
**Date**: 2026-01-12
**Status**: Complete

## Executive Summary

This research consolidates findings on implementing JWT-based authentication between Better Auth (Next.js) and FastAPI, with focus on security, user isolation, and best practices.

---

## Decision 1: JWT Signing Algorithm

**Decision**: Use HS256 (HMAC with SHA-256)

**Rationale**:
- Better Auth default algorithm
- Symmetric key algorithm - same secret for signing and verification
- Suitable for monolithic/two-service architecture with shared secret
- Faster than asymmetric alternatives (RS256)
- Industry standard for stateless authentication

**Alternatives Considered**:
| Algorithm | Pros | Cons | When to Use |
|-----------|------|------|-------------|
| HS256 | Fast, simple setup | Requires shared secret | Monolithic apps (chosen) |
| RS256 | Public key verification | Slower, key management overhead | Microservices |
| ES256 | Compact signatures | Complex setup | Mobile-focused apps |

---

## Decision 2: JWT Library for FastAPI

**Decision**: Use `python-jose[cryptography]`

**Rationale**:
- FastAPI official documentation recommendation
- Industry standard for JWT in Python
- Solid error handling with specific exception types
- Works with both symmetric (HS256) and asymmetric algorithms
- Active maintenance and security updates

**Alternatives Considered**:
| Library | Pros | Cons |
|---------|------|------|
| python-jose | FastAPI standard, robust | Slightly heavier |
| PyJWT | Simpler, faster | Less FastAPI docs |
| authlib | OAuth2 built-in | Overkill for this use case |

**Installation**: `pip install python-jose[cryptography]`

---

## Decision 3: Authentication Implementation Pattern

**Decision**: FastAPI Dependency Injection (not Middleware)

**Rationale**:
- Fine-grained control per route
- Can skip auth for public endpoints
- Better error messages per route
- More testable with dependency overrides
- Aligns with FastAPI's design philosophy
- Explicit dependencies over implicit middleware

**Implementation Pattern**:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials
from jose import jwt, JWTError

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthCredentials = Depends(security)
) -> TokenPayload:
    """Dependency that extracts and verifies JWT"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            key=settings.jwt_secret,
            algorithms=["HS256"]
        )
        return TokenPayload(**payload)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid credentials")

# Usage on protected routes
@app.get("/tasks")
async def get_tasks(user: TokenPayload = Depends(get_current_user)):
    return db.get_tasks(owner_id=user.sub)
```

---

## Decision 4: User Identity Source of Truth

**Decision**: JWT `sub` (subject) claim is authoritative for user identity

**Rationale**:
- Standard JWT claim for user identifier
- Better Auth places user ID in `sub` claim
- URL path parameters (`{user_id}`) must match JWT `sub`
- Prevents IDOR attacks by validating ownership at every request

**JWT Claims Structure (Better Auth)**:
```json
{
  "sub": "user_uuid_here",
  "exp": 1704067200,
  "iat": 1704063600,
  "email": "user@example.com",
  "sessionId": "session_uuid"
}
```

---

## Decision 5: HTTP Status Code for Unauthorized Access

**Decision**: Return 404 (Not Found) for unauthorized resource access

**Rationale**:
- OWASP recommendation for IDOR prevention
- Prevents information leakage (doesn't confirm resource exists)
- User trying to access another user's task shouldn't know it exists
- Consistent with "principle of least information"

**Error Code Taxonomy**:
| Scenario | Status Code | Response |
|----------|-------------|----------|
| No token / malformed token | 401 | "Invalid credentials" |
| Expired token | 401 | "Token has expired" |
| Invalid signature | 401 | "Invalid credentials" |
| Valid token, wrong user's resource | 404 | "Not found" |
| Resource doesn't exist | 404 | "Not found" |
| Missing required claim (sub) | 401 | "Invalid token claims" |

---

## Decision 6: Token Expiration Strategy

**Decision**: Use Better Auth defaults with sensible configuration

**Configuration**:
| Token Type | Duration | Rationale |
|------------|----------|-----------|
| Access Token | 15-60 minutes | Security vs UX balance |
| Session | 7 days | Better Auth default |
| Absolute Max | 30 days | Security backstop |

**Clock Skew Handling**: Allow 10-second leeway for server clock differences
```python
jwt.decode(token, secret, algorithms=["HS256"], options={"leeway": 10})
```

---

## Decision 7: Secret Management

**Decision**: Environment variable `BETTER_AUTH_SECRET`

**Requirements**:
- Minimum 32 characters (256 bits)
- Cryptographically random
- Same value in both Next.js and FastAPI
- Never committed to version control

**Generation**:
```bash
# OpenSSL (recommended)
openssl rand -hex 32

# Python
python -c "import secrets; print(secrets.token_hex(32))"
```

**Configuration Pattern**:
```python
# config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    jwt_secret: str = Field(alias="BETTER_AUTH_SECRET")
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
```

---

## Decision 8: Better Auth Session Type

**Decision**: Use `jwt` cookie cache strategy for Better Auth

**Rationale**:
- Better Auth supports multiple session strategies
- `jwt` strategy: "Standard JWT with HMAC-SHA256 signature (HS256). Signed but not encrypted - readable by anyone but tamper-proof."
- Matches FastAPI verification requirements
- Stateless - no server-side session lookup needed

**Better Auth Configuration**:
```typescript
// auth.ts
export const auth = betterAuth({
  secret: process.env.BETTER_AUTH_SECRET,
  session: {
    cookieCache: {
      enabled: true,
      strategy: "jwt",  // HS256 signed JWT
      maxAge: 60 * 5    // 5 minute cache
    }
  }
});
```

---

## Security Patterns Research

### IDOR Prevention (Insecure Direct Object Reference)

**Pattern**: Defense in Depth
```
Layer 1: Authentication (401 if no credentials)
   ↓
Layer 2: Ownership Check (verify JWT user_id matches path)
   ↓
Layer 3: Database Query Filter (WHERE owner_id = ?)
   ↓
Layer 4: Response Validation (404 if not found/unauthorized)
```

**Implementation**:
```python
@app.get("/users/{user_id}/tasks/{task_id}")
async def get_task(
    user_id: str,
    task_id: str,
    current_user: TokenPayload = Depends(get_current_user)
):
    # Layer 2: Path ownership check
    if current_user.sub != user_id:
        raise HTTPException(status_code=404)

    # Layer 3: DB query with owner filter
    task = await db.get_task(task_id=task_id, owner_id=user_id)

    # Layer 4: Not found response
    if not task:
        raise HTTPException(status_code=404)

    return task
```

### Token Validation Checklist

Per spec requirements:
- [x] Token signature verification using BETTER_AUTH_SECRET
- [x] Token expiration check (exp claim)
- [x] User ID extraction from "sub" claim
- [x] User ID matches route parameter validation
- [x] Invalid/malformed tokens rejected (401)
- [x] Expired tokens rejected (401)
- [x] Missing tokens rejected (401)

---

## Technology Stack Summary

| Component | Technology | Version |
|-----------|------------|---------|
| Frontend Auth | Better Auth | Latest |
| Frontend Framework | Next.js | 14+ |
| Backend Framework | FastAPI | 0.109+ |
| JWT Library | python-jose | 3.3+ |
| Config Management | pydantic-settings | 2.0+ |
| Python | Python | 3.11+ |
| Secret Management | Environment Variables | - |

---

## Open Questions Resolved

| Question | Resolution |
|----------|------------|
| JWT vs sessions | JWT (stateless per spec constraint) |
| Middleware vs dependency | Dependency injection |
| 403 vs 404 | 404 for security |
| Token expiration | Better Auth defaults (configurable) |
| User ID claim | `sub` (standard JWT) |
| Clock skew | 10-second leeway |

---

## References

- [FastAPI OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [Better Auth Next.js Integration](https://www.better-auth.com/docs/integrations/next)
- [Better Auth Session Management](https://www.better-auth.com/docs/concepts/session-management)
- [OWASP IDOR Prevention](https://owasp.org/www-community/attacks/Insecure_Direct_Object_References)
- [python-jose Documentation](https://python-jose.readthedocs.io/)
