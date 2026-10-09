"""Integration tests for AI Content Studio REST API endpoints."""

from starlette.testclient import TestClient


def test_health_and_root(client: TestClient):
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["name"] == "AI Content Studio"

    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"


def test_projects_crud_api(client: TestClient):
    # Create
    create_resp = client.post(
        "/projects",
        json={"name": "Social Growth Q4", "description": "Multi-channel expansion"},
    )
    assert create_resp.status_code == 201
    proj = create_resp.json()
    proj_id = proj["id"]
    assert proj["name"] == "Social Growth Q4"

    # Get
    get_resp = client.get(f"/projects/{proj_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == proj_id

    # List
    list_resp = client.get("/projects")
    assert list_resp.status_code == 200
    assert any(p["id"] == proj_id for p in list_resp.json())

    # Update
    patch_resp = client.patch(f"/projects/{proj_id}", json={"name": "Social Growth 2026"})
    assert patch_resp.status_code == 200
    assert patch_resp.json()["name"] == "Social Growth 2026"

    # Delete
    del_resp = client.delete(f"/projects/{proj_id}")
    assert del_resp.status_code == 204

    # 404
    assert client.get(f"/projects/{proj_id}").status_code == 404


def test_content_items_api(client: TestClient):
    # Setup project
    p = client.post("/projects", json={"name": "Engineering Publication"}).json()
    p_id = p["id"]

    # Create content
    c_resp = client.post(
        "/content",
        json={
            "project_id": p_id,
            "title": "Clean Code in Python",
            "body": "Tips for writing readable and maintainable python codebases.",
            "content_type": "blog",
            "tags": ["python", "clean-code"],
            "tone": "technical",
        },
    )
    assert c_resp.status_code == 201
    content = c_resp.json()
    c_id = content["id"]
    assert content["word_count"] > 0

    # Get
    assert client.get(f"/content/{c_id}").status_code == 200

    # Update body -> triggers revision
    upd_resp = client.patch(
        f"/content/{c_id}",
        json={"body": "Updated tips for writing readable python codebases with new patterns."},
    )
    assert upd_resp.status_code == 200

    # Revisions
    revs_resp = client.get(f"/content/{c_id}/revisions")
    assert revs_resp.status_code == 200
    assert len(revs_resp.json()) == 2

    # Filter
    filter_resp = client.get(f"/content?project_id={p_id}&content_type=blog")
    assert filter_resp.status_code == 200
    assert len(filter_resp.json()) == 1


def test_generator_and_repurpose_api(client: TestClient):
    # Setup project
    p = client.post("/projects", json={"name": "AI Pipeline"}).json()
    p_id = p["id"]

    # Generate with save_to_project_id
    gen_resp = client.post(
        f"/generator/generate?save_to_project_id={p_id}",
        json={
            "topic": "Event-Driven Microservices",
            "content_type": "tweet",
            "tone": "viral",
            "keywords": ["kafka", "rabbitmq"],
        },
    )
    assert gen_resp.status_code == 200
    data = gen_resp.json()
    assert "saved_content_id" in data["metadata"]
    saved_id = int(data["metadata"]["saved_content_id"])

    # Verify saved item exists in DB
    item_resp = client.get(f"/content/{saved_id}")
    assert item_resp.status_code == 200
    assert item_resp.json()["project_id"] == p_id

    # Repurpose with auto-save
    rep_resp = client.post(
        f"/generator/repurpose?save_to_project_id={p_id}",
        json={
            "source_text": "Building scalable REST APIs with FastAPI and SQLite. Tips on indexing, transactions, and concurrency.",
            "tone": "professional",
        },
    )
    assert rep_resp.status_code == 200
    assert len(rep_resp.json()["items"]) == 5

    # Check analytics summary
    analytics_resp = client.get(f"/analytics/summary?project_id={p_id}")
    assert analytics_resp.status_code == 200
    analytics = analytics_resp.json()
    assert analytics["total_items"] >= 6


def test_api_edge_cases_and_404s(client: TestClient):
    # Non-existent project operations
    assert client.get("/projects/999999").status_code == 404
    assert client.patch("/projects/999999", json={"name": "New"}).status_code == 404
    assert client.delete("/projects/999999").status_code == 404

    # Non-existent content operations
    assert client.get("/content/999999").status_code == 404
    assert client.patch("/content/999999", json={"title": "New Title"}).status_code == 404
    assert client.delete("/content/999999").status_code == 404
    assert client.get("/content/999999/revisions").status_code == 404

    # Target project 404 in generator
    gen_404 = client.post(
        "/generator/generate?save_to_project_id=999999",
        json={"topic": "Test Topic", "content_type": "blog"},
    )
    assert gen_404.status_code == 404

    # Target project 404 in repurpose
    rep_404 = client.post(
        "/generator/repurpose?save_to_project_id=999999",
        json={"source_text": "A long enough source text for testing 404 behavior."},
    )
    assert rep_404.status_code == 404

