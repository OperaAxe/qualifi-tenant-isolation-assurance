# QualiFi Tenant Isolation Assurance

[![CI](https://github.com/OperaAxe/qualifi-tenant-isolation-assurance/actions/workflows/ci.yml/badge.svg)](https://github.com/OperaAxe/qualifi-tenant-isolation-assurance/actions/workflows/ci.yml)

A regression suite for tenant-level access control in a fictional SaaS API. The main question is straightforward: can a user from one customer read or change another customer's records by guessing or obtaining a resource ID?

All data is synthetic. The tests focus on observable authorization behaviour and on verifying that rejected requests did not cause side effects.

## Scenarios covered

- Listing projects must return records for the signed-in tenant only.
- Direct requests for another tenant's project must not reveal its contents.
- A denied cross-tenant update must leave the original record unchanged.
- Role restrictions must apply to members, viewers, admins, and owners.
- Export files, shared links, and background-job results must remain within the correct tenant.
- Expired or revoked links must no longer provide access.

One important check reads the record again after a denied update. A `403` or `404` response alone does not prove the server left the data untouched.

## Run locally

Requires Python 3.13.

```bash
python3.13 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
pytest
```

Useful test selections:

```bash
pytest -m boundary
pytest -m rbac
pytest -m side_effect
```

The demo uses an `X-User` header to select a synthetic identity. The authorization rules and roles are documented in `docs/authorization-matrix.md`.

## Scope

**Status: in development.** This is not a penetration test or a production security certification. It does not verify a real identity provider, database row-level security, object storage, concurrency controls, or cryptography. A passing run only supports the specific scenarios represented by the test suite.
