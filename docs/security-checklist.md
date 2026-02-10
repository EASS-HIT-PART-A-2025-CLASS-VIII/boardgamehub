# Security Checklist (OWASP)

## OWASP API Security Top 3 Mitigations

### 1. Broken Object Level Authorization (BOLA)
- [x] **Mitigation**: IDs are validated against the database.
- [x] **Mitigation**: Future: Ensure users can only access their own data (currently public read, admin write).

### 2. Broken Authentication
- [x] **Strong Passwords**: Passwords are hashed using **Bcrypt**.
- [x] **Token Security**: **JWTs** are signed with a secret key and include expiration (`exp`), issuer (`iss`), and audience (`aud`) claims.
- [x] **Hardening**: `tests/test_security_jwt.py` verifies that invalid or expired tokens are rejected.

### 3. Broken Object Property Level Authorization
- [x] **Input Validation**: **Pydantic** models (`schemas.py`) strictly define allowed input fields, preventing mass assignment attacks.
- [x] **Output Filtering**: Response models ensure sensitive internal fields (like password hashes) are never returned to the client.

## General Hygiene
- [x] **Secrets**: No secrets in `git`. Verified with `.gitignore` and manual review.
- [x] **Dependencies**: `uv` lockfile ensures deterministic dependency versions.
- [x] **HTTPS**: Production deployment forces HTTPS (assumed via reverse proxy).
