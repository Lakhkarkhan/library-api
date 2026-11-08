import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app
from app.models import User
from app.security import hash_password

# In-memory SQLite shared across the connection pool, fresh for every test
engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@pytest.fixture()
def db():
    Base.metadata.create_all(bind=engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    # Not using a context manager so the startup lifespan (file DB) is skipped
    yield TestClient(app)
    app.dependency_overrides.clear()


def register_and_login(client, username="alice", password="password123") -> dict:
    client.post("/auth/register", json={"username": username, "password": password})
    res = client.post("/auth/login", data={"username": username, "password": password})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}


@pytest.fixture()
def user_headers(client):
    return register_and_login(client, "alice")


@pytest.fixture()
def other_headers(client):
    return register_and_login(client, "bob")


@pytest.fixture()
def admin_headers(client, db):
    db.add(User(username="admin", hashed_password=hash_password("adminpass123"), role="admin"))
    db.commit()
    res = client.post("/auth/login", data={"username": "admin", "password": "adminpass123"})
    return {"Authorization": f"Bearer {res.json()['access_token']}"}
