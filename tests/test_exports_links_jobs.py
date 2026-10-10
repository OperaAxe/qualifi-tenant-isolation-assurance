import pytest


@pytest.mark.side_effect
def test_export_contains_only_authorized_tenant_records(client):
    created = client.post("/api/exports", headers={"X-User": "alice-owner"})
    export_id = created.json()["id"]
    export = client.get(f"/api/exports/{export_id}", headers={"X-User": "alice-owner"})
    assert export.status_code == 200
    assert {item["tenant_id"] for item in export.json()["records"]} == {"tenant-a"}
    assert (
        client.get(f"/api/exports/{export_id}", headers={"X-User": "bob-admin"}).status_code == 404
    )


@pytest.mark.side_effect
def test_shared_link_respects_revoke_and_tenant_scope(client):
    created = client.post(
        "/api/shared-links",
        headers={"X-User": "alice-owner"},
        json={"project_id": "project-a-1", "expires_in_seconds": 60},
    )
    token = created.json()["token"]
    assert client.get(f"/shared/{token}").status_code == 200
    assert (
        client.delete(f"/api/shared-links/{token}", headers={"X-User": "bob-admin"}).status_code
        == 404
    )
    assert (
        client.delete(f"/api/shared-links/{token}", headers={"X-User": "alice-owner"}).status_code
        == 204
    )
    assert client.get(f"/shared/{token}").status_code == 404


@pytest.mark.side_effect
def test_background_job_preserves_tenant_context(client):
    created = client.post("/api/jobs", headers={"X-User": "bob-admin"})
    job_id = created.json()["id"]
    job = client.get(f"/api/jobs/{job_id}", headers={"X-User": "bob-admin"})
    assert job.status_code == 200
    assert {item["tenant_id"] for item in job.json()["result"]} == {"tenant-b"}
    assert client.get(f"/api/jobs/{job_id}", headers={"X-User": "alice-owner"}).status_code == 404
