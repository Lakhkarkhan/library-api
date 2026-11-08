# Library API

A REST API built with **FastAPI**, featuring JWT authentication, role-based access control, full CRUD, automated tests, Docker support, and a CI pipeline.

![CI](https://github.com/YOUR-USERNAME/library-api/actions/workflows/ci.yml/badge.svg)

## Features

- **JWT authentication**: register, log in, and access protected routes with a bearer token
- **Password security**: passwords are hashed with bcrypt and never returned by the API
- **Role-based access**: `user` and `admin` roles with different permissions
- **Full CRUD** for books, with search and pagination
- **Validation and clear errors**: Pydantic models, proper 401/403/404/409/422 responses
- **28 automated tests** (about 94% coverage) using pytest and an in-memory database
- **Docker + Docker Compose** with PostgreSQL
- **GitHub Actions CI** that runs tests and builds the image on every push
- **Interactive API docs** (Swagger UI) generated automatically

## Permissions

| Action | Anonymous | User | Admin |
|---|:---:|:---:|:---:|
| Register / log in | yes | yes | yes |
| List and view books | no | yes | yes |
| Create a book | no | yes | yes |
| Edit a book | no | own books | any book |
| Delete a book | no | no | yes |
| Change a user's role | no | no | yes |

## Quick start (local)

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt

uvicorn app.main:app --reload
```

Open **http://localhost:8000/docs** for the interactive documentation. Use the **Authorize** button after logging in to try protected endpoints.

To start with an admin account, set these before launching:

```bash
export ADMIN_USERNAME=admin
export ADMIN_PASSWORD=choose-a-strong-password
```

## Quick start (Docker)

```bash
docker compose up --build
```

This starts the API on port 8000 with a PostgreSQL database. Override the defaults with environment variables:

```bash
SECRET_KEY=$(openssl rand -hex 32) ADMIN_PASSWORD=my-strong-password docker compose up --build
```

## Running the tests

```bash
pytest --cov=app --cov-report=term-missing
```

## API overview

| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/register` | Create an account |
| POST | `/auth/login` | Get an access token (form fields: `username`, `password`) |
| GET | `/auth/me` | Current user profile |
| GET | `/books` | List books (`q`, `skip`, `limit` query params) |
| POST | `/books` | Create a book |
| GET | `/books/{id}` | Get one book |
| PUT | `/books/{id}` | Update a book (owner or admin) |
| DELETE | `/books/{id}` | Delete a book (admin) |
| PATCH | `/users/{id}/role` | Change a user's role (admin) |
| GET | `/health` | Health check |

### Example

```bash
# Register and log in
curl -X POST localhost:8000/auth/register -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'

TOKEN=$(curl -s -X POST localhost:8000/auth/login \
  -d "username=alice&password=password123" | python -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# Create and list books
curl -X POST localhost:8000/books -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Dune", "author": "Frank Herbert", "year": 1965}'

curl "localhost:8000/books?q=dune" -H "Authorization: Bearer $TOKEN"
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `SECRET_KEY` | dev placeholder | Signs JWTs. **Set a long random value in production.** |
| `DATABASE_URL` | `sqlite:///./library.db` | Any SQLAlchemy URL (PostgreSQL in Docker) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Token lifetime |
| `ADMIN_USERNAME` / `ADMIN_PASSWORD` | unset | Seeds an admin user on startup |

See `.env.example` for a template.

## Project structure

```
app/
  main.py          # app setup, startup, admin seeding
  config.py        # environment-based settings
  database.py      # SQLAlchemy engine and sessions
  models.py        # User and Book tables
  schemas.py       # request/response models
  security.py      # password hashing and JWT helpers
  deps.py          # auth dependencies (current user, admin check)
  routers/         # auth, books, users endpoints
tests/             # pytest suite
Dockerfile
docker-compose.yml
.github/workflows/ci.yml
```

## Ideas for next steps

- Add database migrations with Alembic
- Add refresh tokens and rate limiting on login
- Add borrowing/returning books with due dates

## License

MIT
