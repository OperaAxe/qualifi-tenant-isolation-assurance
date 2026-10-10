import pytest


@pytest.mark.boundary
def test_collection_lists_only_current_tenant(client):
    response = client.get("/api/projects", headers={"X-User": "alice-owner"})
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Aster confidential project"]
    assert "Borealis confidential project" not in names


@pytest.mark.boundary
@pytest.mark.side_effect
def test_direct_lookup_cannot_read_other_tenant(client):
    response = client.get("/api/projects/project-b-1", headers={"X-User": "alice-owner"})
    assert response.status_code == 404
    assert "Borealis" not in response.text


@pytest.mark.boundary
@pytest.mark.side_effect
def test_cross_tenant_update_does_not_mutate_record(client):
    response = client.patch(
        "/api/projects/project-b-1", headers={"X-User": "alice-member"}, json={"name": "Tampered"}
    )
    assert response.status_code == 404
    owner_read = client.get("/api/projects/project-b-1", headers={"X-User": "bob-admin"})
    assert owner_read.json()["name"] == "Borealis confidential project"


@pytest.mark.boundary
@pytest.mark.side_effect
def test_cross_tenant_delete_does_not_remove_record(client):
    response = client.delete("/api/projects/project-b-1", headers={"X-User": "alice-owner"})
    assert response.status_code == 404
    assert (
        client.get("/api/projects/project-b-1", headers={"X-User": "bob-admin"}).status_code == 200
    )
