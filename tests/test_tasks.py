def test_task_crud(client, auth_headers):
    created = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "Ship Planora", "priority": "high"},
    )
    assert created.status_code == 201
    task_id = created.get_json()["id"]

    fetched = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert fetched.status_code == 200
    assert fetched.get_json()["title"] == "Ship Planora"

    updated = client.put(
        f"/api/v1/tasks/{task_id}",
        headers=auth_headers,
        json={"title": "Ship Planora safely"},
    )
    assert updated.status_code == 200

    completed = client.patch(
        f"/api/v1/tasks/{task_id}/status",
        headers=auth_headers,
        json={"status": "done"},
    )
    assert completed.status_code == 200
    assert completed.get_json()["completed_at"] is not None

    deleted = client.delete(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert deleted.status_code == 204

    missing = client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert missing.status_code == 404


def test_task_title_cannot_be_empty(client, auth_headers):
    response = client.post(
        "/api/v1/tasks",
        headers=auth_headers,
        json={"title": "", "priority": "medium"},
    )
    assert response.status_code == 422


def test_pagination_is_bounded(client, auth_headers):
    response = client.get("/api/v1/tasks?limit=1001", headers=auth_headers)
    assert response.status_code == 400
