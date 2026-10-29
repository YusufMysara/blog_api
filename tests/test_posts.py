from app.core.redis import redis_client
from tests.helpers import auth_headers, create_post


async def test_creating_a_post_requires_a_token(client):
    response = await client.post("/posts/", json={"title": "Title", "content": "Some content for the post."})

    assert response.status_code == 401


async def test_a_created_post_can_be_read_with_its_author(client):
    headers = await auth_headers(client, "alice@example.com")
    created = (await create_post(client, headers)).json()

    response = await client.get(f"/posts/{created['id']}")

    assert response.status_code == 200
    assert response.json()["title"] == "First post"
    assert response.json()["author"]["email"] == "alice@example.com"


async def test_post_validation_rejects_a_short_title(client):
    headers = await auth_headers(client, "alice@example.com")

    response = await client.post(
        "/posts/", json={"title": "Hi", "content": "Some content for the post."}, headers=headers
    )

    assert response.status_code == 422


async def test_reading_a_missing_post_returns_404(client):
    response = await client.get("/posts/999")

    assert response.status_code == 404


async def test_the_post_list_is_paginated(client):
    headers = await auth_headers(client, "alice@example.com")
    for number in range(3):
        await create_post(client, headers, title=f"Post {number}")

    first_page = (await client.get("/posts/", params={"skip": 0, "limit": 2})).json()
    second_page = (await client.get("/posts/", params={"skip": 2, "limit": 2})).json()

    assert len(first_page) == 2
    assert len(second_page) == 1
    titles = {post["title"] for post in first_page + second_page}
    assert titles == {"Post 0", "Post 1", "Post 2"}


async def test_the_post_list_is_cached_and_a_new_post_clears_the_cache(client):
    headers = await auth_headers(client, "alice@example.com")
    await create_post(client, headers, title="Post one")

    first = await client.get("/posts/")
    assert await redis_client.exists("cache:posts:0:10")

    await create_post(client, headers, title="Post two")
    assert not await redis_client.exists("cache:posts:0:10")
    second = await client.get("/posts/")

    assert {post["title"] for post in first.json()} == {"Post one"}
    assert {post["title"] for post in second.json()} == {"Post one", "Post two"}


async def test_the_owner_can_update_a_post(client):
    headers = await auth_headers(client, "alice@example.com")
    post = (await create_post(client, headers)).json()

    response = await client.put(f"/posts/{post['id']}", json={"title": "Edited title"}, headers=headers)

    assert response.status_code == 200
    assert response.json()["title"] == "Edited title"


async def test_another_user_cannot_update_a_post(client):
    owner = await auth_headers(client, "alice@example.com")
    other = await auth_headers(client, "bob@example.com", name="Bob")
    post = (await create_post(client, owner)).json()

    response = await client.put(f"/posts/{post['id']}", json={"title": "Hijacked"}, headers=other)

    assert response.status_code == 403
    assert (await client.get(f"/posts/{post['id']}")).json()["title"] == "First post"


async def test_updating_a_missing_post_returns_404(client):
    headers = await auth_headers(client, "alice@example.com")

    response = await client.put("/posts/999", json={"title": "Edited title"}, headers=headers)

    assert response.status_code == 404


async def test_another_user_cannot_delete_a_post(client):
    owner = await auth_headers(client, "alice@example.com")
    other = await auth_headers(client, "bob@example.com", name="Bob")
    post = (await create_post(client, owner)).json()

    response = await client.delete(f"/posts/{post['id']}", headers=other)

    assert response.status_code == 403
    assert (await client.get(f"/posts/{post['id']}")).status_code == 200


async def test_the_owner_can_delete_a_post(client):
    headers = await auth_headers(client, "alice@example.com")
    post = (await create_post(client, headers)).json()

    response = await client.delete(f"/posts/{post['id']}", headers=headers)

    assert response.status_code == 204
    assert (await client.get(f"/posts/{post['id']}")).status_code == 404
