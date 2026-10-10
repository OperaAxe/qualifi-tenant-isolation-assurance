import pytest
from fastapi.testclient import TestClient

from app.main import EXPORTS, JOBS, PROJECTS, SHARED_LINKS, app


@pytest.fixture(autouse=True)
def reset_data():
    PROJECTS.clear()
    PROJECTS.update(
        {
            "project-a-1": {
                "id": "project-a-1",
                "tenant_id": "tenant-a",
                "name": "Aster confidential project",
                "owner": "alice-owner",
            },
            "project-b-1": {
                "id": "project-b-1",
                "tenant_id": "tenant-b",
                "name": "Borealis confidential project",
                "owner": "bob-admin",
            },
        }
    )
    EXPORTS.clear()
    SHARED_LINKS.clear()
    JOBS.clear()
    yield


@pytest.fixture
def client():
    return TestClient(app)
