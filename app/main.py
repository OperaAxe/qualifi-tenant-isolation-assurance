from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, status
from pydantic import BaseModel, Field

app = FastAPI(title="QualiFi Tenant Isolation Demo", version="0.1.0")

USERS = {
    "alice-owner": {"tenant": "tenant-a", "role": "owner"},
    "alice-member": {"tenant": "tenant-a", "role": "member"},
    "alice-viewer": {"tenant": "tenant-a", "role": "viewer"},
    "bob-admin": {"tenant": "tenant-b", "role": "admin"},
    "bob-member": {"tenant": "tenant-b", "role": "member"},
}
PROJECTS: dict[str, dict[str, Any]] = {
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
EXPORTS: dict[str, dict[str, Any]] = {}
SHARED_LINKS: dict[str, dict[str, Any]] = {}
JOBS: dict[str, dict[str, Any]] = {}


class ProjectIn(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class ShareIn(BaseModel):
    project_id: str
    expires_in_seconds: int = Field(default=3600, ge=1, le=86400)


def actor(x_user: str | None) -> dict[str, str]:
    if not x_user or x_user not in USERS:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown user")
    return {"id": x_user, **USERS[x_user]}


def require_tenant(record: dict[str, Any], user: dict[str, str]) -> None:
    if record["tenant_id"] != user["tenant"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found")


def require_role(user: dict[str, str], *roles: str) -> None:
    if user["role"] not in roles:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Insufficient permission")


def project_or_404(project_id: str) -> dict[str, Any]:
    project = PROJECTS.get(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/projects")
def list_projects(x_user: str | None = Header(default=None)) -> list[dict[str, Any]]:
    user = actor(x_user)
    return [p for p in PROJECTS.values() if p["tenant_id"] == user["tenant"]]


@app.get("/api/projects/{project_id}")
def get_project(project_id: str, x_user: str | None = Header(default=None)) -> dict[str, Any]:
    user = actor(x_user)
    project = project_or_404(project_id)
    require_tenant(project, user)
    return project


@app.post("/api/projects", status_code=201)
def create_project(payload: ProjectIn, x_user: str | None = Header(default=None)) -> dict[str, Any]:
    user = actor(x_user)
    require_role(user, "owner", "admin", "member")
    project = {
        "id": uuid4().hex,
        "tenant_id": user["tenant"],
        "name": payload.name,
        "owner": user["id"],
    }
    PROJECTS[project["id"]] = project
    return project


@app.patch("/api/projects/{project_id}")
def update_project(
    project_id: str, payload: ProjectIn, x_user: str | None = Header(default=None)
) -> dict[str, Any]:
    user = actor(x_user)
    project = project_or_404(project_id)
    require_tenant(project, user)
    require_role(user, "owner", "admin", "member")
    project["name"] = payload.name
    return project


@app.delete("/api/projects/{project_id}", status_code=204)
def delete_project(project_id: str, x_user: str | None = Header(default=None)) -> None:
    user = actor(x_user)
    project = project_or_404(project_id)
    require_tenant(project, user)
    require_role(user, "owner", "admin")
    del PROJECTS[project_id]


@app.post("/api/exports", status_code=202)
def create_export(x_user: str | None = Header(default=None)) -> dict[str, Any]:
    user = actor(x_user)
    require_role(user, "owner", "admin")
    export_id = uuid4().hex
    record = {
        "id": export_id,
        "tenant_id": user["tenant"],
        "status": "complete",
        "records": [p.copy() for p in PROJECTS.values() if p["tenant_id"] == user["tenant"]],
    }
    EXPORTS[export_id] = record
    return {"id": export_id, "status": record["status"]}


@app.get("/api/exports/{export_id}")
def get_export(export_id: str, x_user: str | None = Header(default=None)) -> dict[str, Any]:
    user = actor(x_user)
    export = EXPORTS.get(export_id)
    if not export:
        raise HTTPException(status_code=404, detail="Export not found")
    require_tenant(export, user)
    return export


@app.post("/api/shared-links", status_code=201)
def create_shared_link(
    payload: ShareIn, x_user: str | None = Header(default=None)
) -> dict[str, Any]:
    user = actor(x_user)
    project = project_or_404(payload.project_id)
    require_tenant(project, user)
    require_role(user, "owner", "admin")
    token = uuid4().hex
    SHARED_LINKS[token] = {
        "token": token,
        "tenant_id": user["tenant"],
        "project_id": project["id"],
        "expires_at": datetime.now(UTC) + timedelta(seconds=payload.expires_in_seconds),
        "revoked": False,
    }
    return {"token": token, "expires_at": SHARED_LINKS[token]["expires_at"].isoformat()}


@app.get("/shared/{token}")
def read_shared_link(token: str) -> dict[str, Any]:
    link = SHARED_LINKS.get(token)
    if not link or link["revoked"] or datetime.now(UTC) >= link["expires_at"]:
        raise HTTPException(status_code=404, detail="Shared link unavailable")
    return PROJECTS[link["project_id"]]


@app.delete("/api/shared-links/{token}", status_code=204)
def revoke_shared_link(token: str, x_user: str | None = Header(default=None)) -> None:
    user = actor(x_user)
    link = SHARED_LINKS.get(token)
    if not link:
        raise HTTPException(status_code=404, detail="Shared link not found")
    require_tenant(link, user)
    require_role(user, "owner", "admin")
    link["revoked"] = True


@app.post("/api/jobs", status_code=202)
def create_job(x_user: str | None = Header(default=None)) -> dict[str, str]:
    user = actor(x_user)
    require_role(user, "owner", "admin")
    job_id = uuid4().hex
    JOBS[job_id] = {
        "id": job_id,
        "tenant_id": user["tenant"],
        "status": "complete",
        "result": [p.copy() for p in PROJECTS.values() if p["tenant_id"] == user["tenant"]],
    }
    return {"id": job_id, "status": "complete"}


@app.get("/api/jobs/{job_id}")
def get_job(job_id: str, x_user: str | None = Header(default=None)) -> dict[str, Any]:
    user = actor(x_user)
    job = JOBS.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    require_tenant(job, user)
    return job
