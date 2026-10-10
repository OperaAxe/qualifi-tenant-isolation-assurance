# Threat model and scope

## Fictional asset

The API represents tenant-owned projects, exports, shared links, and asynchronous job results.

## In-scope threats

- Broken object-level authorization through a foreign project/export/job ID
- Cross-tenant collection leakage
- Role escalation through a lower-privilege request
- Unauthorized mutation with a valid but wrong resource ID
- Shared-link access after revocation
- Tenant context loss in a simulated background job

## Out of scope

No internet scanning, third-party testing, credential harvesting, real customer data, real queue, real cloud storage, or professional penetration testing occurs. The demo uses a synthetic header identity and in-memory data.

Passing the tests means only that the implemented examples satisfy the implemented assertions at the time of the run.
