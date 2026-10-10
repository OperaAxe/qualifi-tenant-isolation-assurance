# QualiFi Tenant Isolation & Authorization Assurance

A **local authorization regression-testing project** for a fictional multi-tenant SaaS API. It demonstrates how QA engineers can detect tenant-boundary, object-level authorization, role-permission, export, shared-link, and asynchronous-job defects.

This is not a penetration test, security certification, or claim that the demonstration API is completely secure. All users, tenants, and records are synthetic and local.

## What it demonstrates

- Server-side tenant checks on collections and direct object IDs
- Owner/admin/member/viewer permission rules
- Side-effect assertions for forbidden update/delete requests
- Tenant-scoped exports and background-job results
- Shared-link expiration/revocation policy
- Deterministic API tests with isolated fixtures

## Setup

### Windows PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest
```

### Bash

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest
```

## Architecture

- `app/main.py` — FastAPI demonstration API with synthetic tenants and in-memory records
- `tests/` — boundary, RBAC, side-effect, export, shared-link, and job tests
- `.github/workflows/ci.yml` — offline-compatible GitHub Actions validation

Authentication is represented by the synthetic `X-User` header. This keeps the authorization focus visible and avoids introducing a real identity provider.

## Permission policy

- `owner` and `admin`: create/delete projects, create exports, create/revoke shared links, create jobs
- `member`: create/update projects; cannot delete, export, or manage links/jobs
- `viewer`: read tenant projects; cannot mutate or create privileged operations
- Cross-tenant access returns `404` to avoid confirming that another tenant's resource exists.

## Run targeted tests

```bash
pytest -m boundary
pytest -m rbac
pytest -m side_effect
pytest --junitxml=test-results/junit.xml
```

## How to interpret failures

A failed test may indicate an authorization defect, an incorrect permission rule, a fixture issue, or an environment problem. For mutation tests, inspect the follow-up read to distinguish a blocked request from a hidden side effect. The JUnit report is machine-readable and is uploaded by CI.

## Scope and limitations

This repository checks a deliberately small set of API behaviors. It does not test a real identity provider, database row-level security, object storage, rate limiting, audit logs, concurrency races, cryptography, or a complete threat model. Passing these tests does not prove complete security and does not replace a professional security assessment.

See `docs/threat-model-and-scope.md`, `docs/authorization-matrix.md`, `docs/test-strategy.md`, `docs/learning-guide.md`, and `docs/demo-script.md`.
