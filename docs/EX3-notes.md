# EX3 Notes - Security Hardening

## Overview
This document records the security hardening steps applied to the BoardGameHub API as part of Exercise 3. The focus was on securing credentials, implementing role-based access control (RBAC), and ensuring secrets hygiene.

## 1. Password Hashing
We replaced plaintext password storage with **Bcrypt** hashing using `passlib`.

- **Implementation**: `app/security.py`
- **Algorithm**: `bcrypt`
- **Library**: `passlib[bcrypt]`

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, password_hash: str) -> bool:
    return pwd_context.verify(plain_password, password_hash)
```

## 2. JWT Authentication
We implemented a robust JSON Web Token (JWT) issuance and validation system using `python-jose`.

- **Claims Enforced**:
    - `iss` (Issuer): Verified against `MOVIE_JWT_ISSUER` (or `BOARDGAME_JWT_ISSUER`)
    - `aud` (Audience): Verified against `MOVIE_JWT_AUDIENCE` (or `BOARDGAME_JWT_AUDIENCE`)
    - `exp` (Expiration): Tokens expire after a set duration (default 30 minutes)
    - `role`: Custom claim for RBAC (e.g., `admin`, `user`)

- **Endpoints Protected**:
    - `/internal/stats/refresh`: Requires `admin` role.

## 3. Secret Management
- **.env**: Local secrets are stored in `.env` (gitignored).
- **.env.example**: A template file with safe defaults is provided for developers.
- **Rotation**: We confirmed that no hardcoded secrets exist in the codebase.
- **Scanning**: We use tools like `trufflehog` or `gitleaks` to scan for accidental secret commits.

## 4. Tests
Security tests were added in `tests/test_security_jwt.py` to verify:
- 401 Unauthorized for missing tokens.
- 403 Forbidden for insufficient roles.
- 401 Unauthorized for expired tokens.
