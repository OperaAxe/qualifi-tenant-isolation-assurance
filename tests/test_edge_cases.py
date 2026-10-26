from datetime import UTC, datetime, timedelta

import pytest

from app.main import SHARED_LINKS


@pytest.mark.boundary
def test_foreign_and_missing_project_ids_are_both_not_found(client) -> None:
    foreign = client.get(
        "/api/projects/project-a-1", headers={"X-User": "bob-admin"}
    )
    missing = client.get(
        "/api/projects/project-does-not-exist", headers={"X-User": "bob-admin"}
    )

    assert foreign.status_code == 404
    assert missing.status_code == 404


@pytest.mark.boundary
@pytest.mark.side_effect
def test_cross_tenant_patch_is_denied_and_original_project_is_unchanged(client) -> None:
    before = client.get(
        "/api/projects/project-a-1", headers={"X-User": "alice-owner"}
    ).json()

    denied = client.patch(
        "/api/projects/project-a-1",
        headers={"X-User": "bob-admin"},
        json={"name": "Changed by the other tenant"},
    )
    after = client.get(
        "/api/projects/project-a-1", headers={"X-User": "alice-owner"}
    ).json()

    assert denied.status_code == 404
    assert after["name"] == before["name"]


def test_unknown_identity_cannot_list_projects(client) -> None:
    response = client.get("/api/projects")
    assert response.status_code == 401
    assert response.json()["detail"] == "Unknown user"


@pytest.mark.boundary
def test_expired_shared_link_is_not_available(client) -> None:
    created = client.post(
        "/api/shared-links",
        headers={"X-User": "alice-owner"},
        json={"project_id": "project-a-1", "expires_in_seconds": 60},
    )
    assert created.status_code == 201
    token = created.json()["token"]
    SHARED_LINKS[token]["expires_at"] = datetime.now(UTC) - timedelta(seconds=1)

    expired = client.get(f"/shared/{token}")
    assert expired.status_code == 404
