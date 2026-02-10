# Release Checklist

**Release Date**: 2026-02-09
**Owner**: Dev Team

## 1. Quality Gates (Automation)
Run the following commands from the project root. All must pass before tagging a release.

- [ ] **Linting**:
  ```bash
  uv run ruff check .
  ```
  *Expected*: No errors.

- [ ] **Type Checking**:
  ```bash
  uv run mypy app
  ```
  *Expected*: Success (no issues found).

- [ ] **Tests**:
  ```bash
  uv run pytest
  ```
  *Expected*: All tests passed (green).

- [ ] **Documentation Build**:
  ```bash
  uv run mkdocs build
  ```
  *Expected*: Site built successfully.

## 2. FastMCP Probe
Verify the AI agent tool is functioning.

- [ ] **Probe Command**:
  ```bash
  uv run scripts/mcp_probe.py
  ```
  *Expected Output*: JSON response with boardgames list.

## 3. Security Scan
- [ ] **Secret Scan**:
  ```bash
  # Example if trufflehog is installed
  trufflehog filesystem --exclude .git .
  ```
  *Expected*: No secrets found.

## 4. Manual Verification
- [ ] **Pagination**: `GET /boardgames/?page=1&page_size=2` returns correct slice.
- [ ] **CSV**: `GET /boardgames/?format=csv` downloads valid CSV.
- [ ] **Auth**: Login returns token; Protected route rejects request without token.
