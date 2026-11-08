from app.security import create_access_token


def test_health(client):
    assert client.get("/health").json() == {"status": "ok"}


def test_register_success(client):
    res = client.post("/auth/register", json={"username": "alice", "password": "password123"})
    assert res.status_code == 201
    body = res.json()
    assert body["username"] == "alice"
    assert body["role"] == "user"
    assert "password" not in body and "hashed_password" not in body


def test_register_duplicate_username(client):
    payload = {"username": "alice", "password": "password123"}
    client.post("/auth/register", json=payload)
    assert client.post("/auth/register", json=payload).status_code == 409


def test_register_validation(client):
    assert client.post("/auth/register", json={"username": "al", "password": "password123"}).status_code == 422
    assert client.post("/auth/register", json={"username": "alice", "password": "short"}).status_code == 422


def test_login_success_and_me(client, user_headers):
    res = client.get("/auth/me", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["username"] == "alice"


def test_login_wrong_password(client):
    client.post("/auth/register", json={"username": "alice", "password": "password123"})
    res = client.post("/auth/login", data={"username": "alice", "password": "wrong-password"})
    assert res.status_code == 401


def test_login_unknown_user(client):
    res = client.post("/auth/login", data={"username": "ghost", "password": "password123"})
    assert res.status_code == 401


def test_protected_route_requires_token(client):
    assert client.get("/books").status_code == 401


def test_invalid_token_rejected(client):
    res = client.get("/auth/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert res.status_code == 401


def test_expired_token_rejected(client):
    client.post("/auth/register", json={"username": "alice", "password": "password123"})
    expired = create_access_token("alice", expires_minutes=-1)
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {expired}"})
    assert res.status_code == 401


def test_token_for_deleted_user_rejected(client):
    token = create_access_token("nobody")
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 401
