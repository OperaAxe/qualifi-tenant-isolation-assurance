# Test strategy

Tests are API-level integration checks using FastAPI's local `TestClient`. Each test resets synthetic state before execution. Every denial assertion is paired with a read-back assertion when mutation could have occurred.

## Test oracles

- Tenant oracle: every returned record has the authenticated tenant ID; foreign IDs return 404.
- Role oracle: the HTTP status matches the documented permission matrix.
- Side-effect oracle: a forbidden update/delete/export/job does not change or expose state.
- Link oracle: a link is readable before revocation and unavailable after revocation.
- Job oracle: the completed result contains only records from the job creator's tenant.

The design follows OWASP guidance to enforce authorization server-side on every request, deny by default, and test object-level authorization rather than trusting an identifier alone.
