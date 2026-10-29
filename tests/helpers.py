"""Small building blocks shared by the tests."""
from httpx import AsyncClient

PASSWORD = "correct-horse-1"


async def register(client: AsyncClient, email: str, name: str = "Alice"):
    return await client.post("/auth/register", json={"name": name, "email": email, "password": PASSWORD})


async def auth_headers(client: AsyncClient, email: str, name: str = "Alice") -> dict[str, str]:
    """Register a user, log in, and return the Authorization header for that user."""
    await register(client, email, name)
    response = await client.post("/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


async def create_post(client: AsyncClient, headers: dict[str, str], title: str = "First post"):
    return await client.post(
        "/posts/", json={"title": title, "content": "Some content for the post."}, headers=headers
    )
