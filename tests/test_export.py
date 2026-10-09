"""Tests for export endpoints."""

from starlette.testclient import TestClient


def test_export_formats(client: TestClient):
    # Setup project and content item
    p = client.post("/projects", json={"name": "Export Project"}).json()
    item = client.post(
        "/content",
        json={
            "project_id": p["id"],
            "title": "Modern Cloud Architecture",
            "body": "# Cloud Architecture\n\nCloud computing enables elastic scale and resilience.\n\n- Point 1\n- Point 2",
            "content_type": "blog",
        },
    ).json()
    item_id = item["id"]

    # 1. Export as Markdown
    md_resp = client.get(f"/export/{item_id}?format=markdown")
    assert md_resp.status_code == 200
    assert "text/markdown" in md_resp.headers["content-type"]
    assert "# Cloud Architecture" in md_resp.text

    # 2. Export as HTML
    html_resp = client.get(f"/export/{item_id}?format=html")
    assert html_resp.status_code == 200
    assert "text/html" in html_resp.headers["content-type"]
    assert "<!DOCTYPE html>" in html_resp.text
    assert "<h1>Cloud Architecture</h1>" in html_resp.text

    # 3. Export as JSON
    json_resp = client.get(f"/export/{item_id}?format=json")
    assert json_resp.status_code == 200
    data = json_resp.json()
    assert data["id"] == item_id
    assert data["word_count"] > 0

    # 4. 404 on non-existent content
    assert client.get("/export/999999?format=markdown").status_code == 404
