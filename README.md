# Blog API

[![CI](https://github.com/YusufMysara/blog_api/actions/workflows/ci.yml/badge.svg)](https://github.com/YusufMysara/blog_api/actions/workflows/ci.yml)

An async REST API for a blog, built with **FastAPI** and **PostgreSQL**, featuring JWT authentication, a layered architecture, Redis caching and rate limiting, and tests that run against a real database in CI.

---

## Features

- **JWT Authentication** — secure register and login with bcrypt password hashing and token-based access control
- **Post Management** — full CRUD operations with ownership validation and authorization
- **Layered Architecture** — clean separation between router, service, CRUD, and database layers
- **Database Migrations** — schema versioning with Alembic (the schema already includes `tags` and `post_tags` tables; tag endpoints are not built yet)
- **Redis Caching** — the paginated post list is cached for 60 seconds and cleared whenever a post is created, updated or deleted
- **Rate Limiting** — at most 5 login attempts per minute per IP, counted in Redis
- **Tests and CI** — pytest suite running against real PostgreSQL and Redis on every push and pull request
- **Docker Support** — fully containerized with Docker and docker-compose

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Database | PostgreSQL |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Caching | Redis |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Containerization | Docker + docker-compose |
| Validation | Pydantic v2 |

---

## Project Structure

```
blog_api/
├── app/
│   ├── core/           # config, security utilities
│   ├── models/         # SQLAlchemy database models
│   ├── schemas/        # Pydantic input/output schemas
│   ├── crud/           # database operations
│   ├── services/       # business logic
│   ├── routers/        # HTTP endpoints
│   └── dependencies/   # FastAPI dependencies (auth, rate limiting)
├── alembic/            # database migrations
├── tests/              # pytest suite (real PostgreSQL and Redis)
├── .github/workflows/  # CI
├── main.py             # app entry point
├── .env.example        # environment variables template
├── docker-compose.yml
├── requirements.txt
└── requirements-dev.txt
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL
- Redis
- Docker (optional)

### Run Locally

**1 — Clone the repository**
```bash
git clone https://github.com/YusufMysara/blog_api.git
cd blog_api
```

**2 — Create virtual environment**
```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux
```

**3 — Install dependencies**
```bash
pip install -r requirements.txt
```

**4 — Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your database and secret key values
```

**5 — Run database migrations**
```bash
alembic upgrade head
```

**6 — Start the server**
```bash
uvicorn main:app --reload
```

**7 — Open API docs**
```
http://localhost:8000/docs
```

### Run with Docker

```bash
docker-compose up --build
```

This starts PostgreSQL, Redis and the API, applies the migrations, and serves the API on <http://localhost:8000>. It publishes ports `5432`, `6379` and `8000`, so stop any local PostgreSQL or Redis using those ports first.

---

## Testing

19 tests cover registration, login, the login rate limit, token checks, post CRUD, ownership rules (403 for other users) and cache invalidation. They run against a real PostgreSQL database, built from the Alembic migrations, and a real Redis. Nothing is mocked.

Start throwaway containers (the tests create and drop their own `blog_test` database), then run pytest:

```bash
docker run -d --rm --name blog-test-pg -e POSTGRES_PASSWORD=postgres -p 127.0.0.1:5435:5432 postgres:16
docker run -d --rm --name blog-test-redis -p 127.0.0.1:6381:6379 redis:7
pip install -r requirements-dev.txt
python -m pytest
```

The tests refuse to run unless the database name ends in `_test`, so they can never touch your development data. GitHub Actions runs the same suite on every push and pull request.

---

## API Endpoints

### Authentication
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| POST | `/auth/register` | Create new account | Public |
| POST | `/auth/login` | Login and get token | Public |

### Posts
| Method | Endpoint | Description | Auth |
|---|---|---|---|
| GET | `/posts/` | Get all posts (paginated) | Public |
| GET | `/posts/{id}` | Get single post | Public |
| POST | `/posts/` | Create post | Protected |
| PUT | `/posts/{id}` | Update post | Protected (owner only) |
| DELETE | `/posts/{id}` | Delete post | Protected (owner only) |

---

## Architecture

This project follows a strict layered architecture:

```
HTTP Request
     ↓
Router       → handles HTTP, validates input/output
     ↓
Service      → business logic and rules
     ↓
CRUD         → database operations only
     ↓
PostgreSQL
```

Each layer has one responsibility and doesn't cross into another layer's concerns.

---

## Environment Variables

```env
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/blog_db
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REDIS_HOST=localhost
REDIS_PORT=6379
```

---

## Limitations

- Access tokens only: there are no refresh tokens or logout.
- The `tags` and `post_tags` tables exist in the schema, but no endpoint reads or writes them yet.
- The post list has no fixed sort order, so pages are not guaranteed to be stable while posts are being added.
- The login rate limit counts by client IP, so users behind one proxy share a limit.
