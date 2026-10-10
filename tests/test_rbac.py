import pytest


@pytest.mark.rbac
def test_member_can_create_and_update_but_not_delete(client):
    headers = {"X-User": "alice-member"}
    created = client.post("/api/projects", headers=headers, json={"name": "Member project"})
    assert created.status_code == 201
    project_id = created.json()["id"]
    updated = client.patch(
        f"/api/projects/{project_id}", headers=headers, json={"name": "Updated member project"}
    )
    assert updated.status_code == 200
    assert client.delete(f"/api/projects/{project_id}", headers=headers).status_code == 403


@pytest.mark.rbac
def test_viewer_cannot_mutate(client):
    headers = {"X-User": "alice-viewer"}
    assert client.post("/api/projects", headers=headers, json={"name": "Nope"}).status_code == 403
    assert (
        client.patch(
            "/api/projects/project-a-1", headers=headers, json={"name": "Nope"}
        ).status_code
        == 403
    )
    assert client.delete("/api/projects/project-a-1", headers=headers).status_code == 403


@pytest.mark.rbac
def test_admin_can_create_export_and_member_cannot(client):
    admin = client.post("/api/exports", headers={"X-User": "bob-admin"})
    assert admin.status_code == 202
    assert client.post("/api/exports", headers={"X-User": "bob-member"}).status_code == 403


@pytest.mark.rbac
def test_missing_or_unknown_identity_is_denied(client):
    assert client.get("/api/projects").status_code == 401
    assert client.get("/api/projects", headers={"X-User": "nobody"}).status_code == 401
