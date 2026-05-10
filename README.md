# Blog API

A production-ready REST API built with **FastAPI** and **PostgreSQL**, featuring JWT authentication, layered architecture, and Redis caching.

---

## Features

- **JWT Authentication** — secure register and login with bcrypt password hashing and token-based access control
- **Post Management** — full CRUD operations with ownership validation and authorization
- **Layered Architecture** — clean separation between router, service, CRUD, and database layers
- **Database Migrations** — schema versioning with Alembic including tags and post-tags support
- **Redis Caching** — response caching and rate limiting on authentication endpoints
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
│   ├── dependencies/   # FastAPI dependencies (auth)
│   └── main.py         # app entry point
├── alembic/            # database migrations
├── .env.example        # environment variables template
├── docker-compose.yml
└── requirements.txt
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
uvicorn app.main:app --reload
```

**7 — Open API docs**
```
http://localhost:8000/docs
```

### Run with Docker

```bash
docker-compose up --build
```

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

## Running Tests

```bash
pytest
```

---

## License

MIT
