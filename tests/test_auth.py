from tests.helpers import PASSWORD, auth_headers, register


async def test_register_returns_the_user_without_the_password(client):
    response = await register(client, "alice@example.com")

    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "alice@example.com"
    assert body["is_active"] is True
    assert "password" not in body


async def test_register_rejects_a_duplicate_email(client):
    await register(client, "alice@example.com")

    response = await register(client, "alice@example.com")

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"


async def test_register_rejects_a_short_password(client):
    response = await client.post(
        "/auth/register", json={"name": "Alice", "email": "alice@example.com", "password": "short"}
    )

    assert response.status_code == 422


async def test_login_returns_a_bearer_token(client):
    await register(client, "alice@example.com")

    response = await client.post("/auth/login", json={"email": "alice@example.com", "password": PASSWORD})

    assert response.status_code == 200
    assert response.json()["token_type"] == "bearer"
    assert response.json()["access_token"]


async def test_login_rejects_a_wrong_password(client):
    await register(client, "alice@example.com")

    response = await client.post("/auth/login", json={"email": "alice@example.com", "password": "wrong-password"})

    assert response.status_code == 401


async def test_login_is_rate_limited_after_five_attempts(client):
    attempt = {"email": "nobody@example.com", "password": "wrong-password"}
    for _ in range(5):
        assert (await client.post("/auth/login", json=attempt)).status_code == 401

    response = await client.post("/auth/login", json=attempt)

    assert response.status_code == 429


async def test_a_protected_route_rejects_an_invalid_token(client):
    response = await client.post(
        "/posts/",
        json={"title": "Title", "content": "Some content for the post."},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401


async def test_a_valid_token_works_on_a_protected_route(client):
    headers = await auth_headers(client, "alice@example.com")

    response = await client.post(
        "/posts/", json={"title": "Title", "content": "Some content for the post."}, headers=headers
    )

    assert response.status_code == 200
