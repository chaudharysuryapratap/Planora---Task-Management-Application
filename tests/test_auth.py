def test_register_creates_tokens_and_default_categories(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "Password123",
        },
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["user"]["email"] == "test@example.com"
    assert body["access_token"]
    assert body["refresh_token"]

    headers = {"Authorization": f"Bearer {body['access_token']}"}
    categories = client.get("/api/v1/categories", headers=headers)
    assert categories.status_code == 200
    assert len(categories.get_json()["data"]) == 3


def test_register_rejects_weak_password(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "password",
        },
    )
    assert response.status_code == 422


def test_login_and_refresh(client, registered_user):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "Password123"},
    )
    assert login.status_code == 200

    refresh_token = login.get_json()["refresh_token"]
    refreshed = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert refreshed.status_code == 200
    assert refreshed.get_json()["access_token"]


def test_logout_revokes_refresh_token(client, registered_user):
    token = registered_user["refresh_token"]
    logout = client.post("/api/v1/auth/logout", json={"refresh_token": token})
    assert logout.status_code == 200

    refreshed = client.post("/api/v1/auth/refresh", json={"refresh_token": token})
    assert refreshed.status_code == 401
