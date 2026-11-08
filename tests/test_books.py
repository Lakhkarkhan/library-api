BOOK = {"title": "Dune", "author": "Frank Herbert", "isbn": "9780441013593", "year": 1965}


def create(client, headers, **overrides):
    return client.post("/books", json={**BOOK, **overrides}, headers=headers)


def test_create_and_get_book(client, user_headers):
    res = create(client, user_headers)
    assert res.status_code == 201
    book = res.json()
    assert book["title"] == "Dune"

    fetched = client.get(f"/books/{book['id']}", headers=user_headers)
    assert fetched.status_code == 200
    assert fetched.json() == book


def test_create_requires_auth(client):
    assert client.post("/books", json=BOOK).status_code == 401


def test_create_validation(client, user_headers):
    res = client.post("/books", json={"title": "", "author": "X"}, headers=user_headers)
    assert res.status_code == 422


def test_duplicate_isbn_conflict(client, user_headers):
    create(client, user_headers)
    assert create(client, user_headers, title="Other").status_code == 409


def test_get_missing_book(client, user_headers):
    assert client.get("/books/999", headers=user_headers).status_code == 404


def test_list_pagination_and_search(client, user_headers):
    for i in range(5):
        create(client, user_headers, title=f"Book {i}", isbn=f"isbn-{i}", author="Some Author")
    create(client, user_headers, title="Neuromancer", isbn="isbn-n", author="William Gibson")

    assert len(client.get("/books", headers=user_headers).json()) == 6
    assert len(client.get("/books?limit=2", headers=user_headers).json()) == 2
    assert len(client.get("/books?skip=4", headers=user_headers).json()) == 2

    found = client.get("/books?q=gibson", headers=user_headers).json()
    assert [b["title"] for b in found] == ["Neuromancer"]


def test_owner_can_update(client, user_headers):
    book_id = create(client, user_headers).json()["id"]
    res = client.put(f"/books/{book_id}", json={**BOOK, "title": "Dune (Revised)"}, headers=user_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Dune (Revised)"


def test_non_owner_cannot_update(client, user_headers, other_headers):
    book_id = create(client, user_headers).json()["id"]
    res = client.put(f"/books/{book_id}", json=BOOK, headers=other_headers)
    assert res.status_code == 403


def test_admin_can_update_any_book(client, user_headers, admin_headers):
    book_id = create(client, user_headers).json()["id"]
    res = client.put(f"/books/{book_id}", json={**BOOK, "year": 1966}, headers=admin_headers)
    assert res.status_code == 200
    assert res.json()["year"] == 1966


def test_update_missing_book(client, user_headers):
    assert client.put("/books/999", json=BOOK, headers=user_headers).status_code == 404


def test_regular_user_cannot_delete(client, user_headers):
    book_id = create(client, user_headers).json()["id"]
    assert client.delete(f"/books/{book_id}", headers=user_headers).status_code == 403


def test_admin_can_delete(client, user_headers, admin_headers):
    book_id = create(client, user_headers).json()["id"]
    assert client.delete(f"/books/{book_id}", headers=admin_headers).status_code == 204
    assert client.get(f"/books/{book_id}", headers=admin_headers).status_code == 404


def test_delete_missing_book(client, admin_headers):
    assert client.delete("/books/999", headers=admin_headers).status_code == 404
