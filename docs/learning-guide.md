# Learning guide

## Key ideas

Authentication answers “who is this?”; authorization answers “may this identity perform this operation on this resource?” Tenant isolation adds a required tenant scope to the authorization decision.

## Difficult scenarios

1. A foreign resource ID is supplied to a valid endpoint: the server must apply tenant checks before returning data.
2. A forbidden update returns an error: the test must also verify the record did not change.
3. A collection endpoint is overlooked: tests must inspect list responses, not only direct lookups.
4. An export or job ID is reused by another tenant: the result must be denied and tenant-scoped.
5. A shared link is revoked: an old token must no longer work.

## Interview questions

- Why return 404 for cross-tenant objects? — This demo chooses not to confirm the resource exists; the important point is consistency.
- Why are read-back checks important? — A 403/404 response alone does not prove the server avoided a side effect.
- What would production need? — Real authentication, policy enforcement, database isolation controls, audit logs, concurrency tests, and a broader security program.
- Is this a penetration test? — No. It is a focused regression suite for specified authorization behavior.
