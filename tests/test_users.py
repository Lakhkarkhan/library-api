def test_admin_can_promote_user(client, admin_headers, user_headers):
    user_id = client.get("/auth/me", headers=user_headers).json()["id"]
    res = client.patch(f"/users/{user_id}/role", json={"role": "admin"}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "admin"


def test_regular_user_cannot_change_roles(client, user_headers):
    user_id = client.get("/auth/me", headers=user_headers).json()["id"]
    res = client.patch(f"/users/{user_id}/role", json={"role": "admin"}, headers=user_headers)
    assert res.status_code == 403


def test_invalid_role_rejected(client, admin_headers):
    res = client.patch("/users/1/role", json={"role": "superuser"}, headers=admin_headers)
    assert res.status_code == 422


def test_promote_missing_user(client, admin_headers):
    res = client.patch("/users/999/role", json={"role": "admin"}, headers=admin_headers)
    assert res.status_code == 404
