def test_register_user(client):
    response = client.post(
        "/users/",
        json={
            "name": "Maren",
            "email": "maren@example.com",
            "password": "MyPass123",
            "role": "user",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "maren@example.com"
    assert "password" not in data


def test_duplicate_email_rejected(client):
    payload = {
        "name": "Maren",
        "email": "maren@example.com",
        "password": "MyPass123",
        "role": "user",
    }

    client.post("/users/", json=payload)
    response = client.post("/users/", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_login_success(client):
    client.post(
        "/users/",
        json={
            "name": "Admin",
            "email": "admin@example.com",
            "password": "MyPass123",
            "role": "admin",
        },
    )

    response = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "MyPass123"},
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_failure(client):
    response = client.post(
        "/auth/login",
        data={"username": "wrong@example.com", "password": "badpass"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


def test_users_route_requires_auth(client):
    response = client.get("/users/")
    assert response.status_code in (401, 403)


def test_users_route_forbids_normal_user(client):
    client.post(
        "/users/",
        json={
            "name": "User1",
            "email": "user@example.com",
            "password": "MyPass123",
            "role": "user",
        },
    )

    login = client.post(
        "/auth/login",
        data={"username": "user@example.com", "password": "MyPass123"},
    )
    token = login.json()["access_token"]

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert response.json()["detail"] == "Admin access required"


def test_users_route_allows_admin(client):
    client.post(
        "/users/",
        json={
            "name": "Admin",
            "email": "admin@example.com",
            "password": "MyPass123",
            "role": "admin",
        },
    )

    login = client.post(
        "/auth/login",
        data={"username": "admin@example.com", "password": "MyPass123"},
    )
    token = login.json()["access_token"]

    response = client.get("/users/", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["email"] == "admin@example.com"
