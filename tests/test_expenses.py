from fastapi.testclient import TestClient


def register_user(client: TestClient, name: str, email: str, password: str, role: str = "user"):
    return client.post(
        "/users/",
        json={
            "name": name,
            "email": email,
            "password": password,
            "role": role,
        },
    )


def login_user(client: TestClient, email: str, password: str):
    return client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
    )


def get_auth_headers(client: TestClient, email: str, password: str):
    login_response = login_user(client, email, password)
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_create_expense(client: TestClient):
    register_user(client, "Maren", "maren@example.com", "MyPass123", "user")
    headers = get_auth_headers(client, "maren@example.com", "MyPass123")

    response = client.post(
        "/expenses/",
        json={
            "title": "Train ticket",
            "amount": 52.5,
            "category": "Travel",
            "description": "Milton Keynes to London return",
        },
        headers=headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Train ticket"
    assert data["amount"] == 52.5
    assert data["category"] == "Travel"
    assert data["status"] == "draft"


def test_get_my_expenses(client: TestClient):
    register_user(client, "Maren", "maren@example.com", "MyPass123", "user")
    headers = get_auth_headers(client, "maren@example.com", "MyPass123")

    client.post(
        "/expenses/",
        json={
            "title": "Lunch",
            "amount": 12,
            "category": "Food",
            "description": "Lunch meeting",
        },
        headers=headers,
    )

    response = client.get("/expenses/", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Lunch"


def test_filter_expenses(client: TestClient):
    register_user(client, "Maren", "maren@example.com", "MyPass123", "user")
    headers = get_auth_headers(client, "maren@example.com", "MyPass123")

    client.post(
        "/expenses/",
        json={
            "title": "Train ticket",
            "amount": 52.5,
            "category": "Travel",
            "description": "Milton Keynes to London return",
        },
        headers=headers,
    )

    client.post(
        "/expenses/",
        json={
            "title": "Lunch",
            "amount": 12,
            "category": "Food",
            "description": "Lunch meeting",
        },
        headers=headers,
    )

    response = client.get("/expenses/?min_amount=50", headers=headers)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "Train ticket"


def test_submit_expense(client: TestClient):
    register_user(client, "Maren", "maren@example.com", "MyPass123", "user")
    headers = get_auth_headers(client, "maren@example.com", "MyPass123")

    create_response = client.post(
        "/expenses/",
        json={
            "title": "Hotel",
            "amount": 145,
            "category": "Travel",
            "description": "One night stay",
        },
        headers=headers,
    )

    expense_id = create_response.json()["id"]

    submit_response = client.post(f"/expenses/{expense_id}/submit", headers=headers)

    assert submit_response.status_code == 200
    assert submit_response.json()["status"] == "submitted"


def test_cannot_edit_submitted_expense(client: TestClient):
    register_user(client, "Maren", "maren@example.com", "MyPass123", "user")
    headers = get_auth_headers(client, "maren@example.com", "MyPass123")

    create_response = client.post(
        "/expenses/",
        json={
            "title": "Hotel",
            "amount": 145,
            "category": "Travel",
            "description": "One night stay",
        },
        headers=headers,
    )

    expense_id = create_response.json()["id"]

    client.post(f"/expenses/{expense_id}/submit", headers=headers)

    update_response = client.put(
        f"/expenses/{expense_id}",
        json={
            "title": "Updated Hotel",
            "amount": 150,
            "category": "Travel",
            "description": "Updated stay",
        },
        headers=headers,
    )

    assert update_response.status_code == 400
    assert update_response.json()["detail"] == "Only draft expenses can be edited"


def test_admin_can_approve_expense(client: TestClient):
    register_user(client, "Normal User", "user@example.com", "UserPass123", "user")
    user_headers = get_auth_headers(client, "user@example.com", "UserPass123")

    register_user(client, "Admin User", "admin@example.com", "AdminPass123", "admin")
    admin_headers = get_auth_headers(client, "admin@example.com", "AdminPass123")

    create_response = client.post(
        "/expenses/",
        json={
            "title": "Flight",
            "amount": 300,
            "category": "Travel",
            "description": "Conference travel",
        },
        headers=user_headers,
    )

    expense_id = create_response.json()["id"]

    client.post(f"/expenses/{expense_id}/submit", headers=user_headers)

    approve_response = client.post(f"/expenses/{expense_id}/approve", headers=admin_headers)

    assert approve_response.status_code == 200
    assert approve_response.json()["status"] == "approved"