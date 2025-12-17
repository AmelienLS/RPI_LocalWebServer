from flask import session


def test_index_requires_login(client):
    response = client.get("/index")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_login_invalid_identifiant(client):
    response = client.post("/", data={"identifiant": "ghost"})
    assert b"Identifiant incorrect" in response.data


def test_login_success_sets_session(client, add_user):
    add_user(identifiant="admin-user", prenom="Alice", admin=1)

    with client:
        response = client.post("/", data={"identifiant": "admin-user"})
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/index")
        assert session["prenom"] == "Alice"
        assert session["admin"] == 1


def test_logout_clears_session(client):
    with client.session_transaction() as flask_session:
        flask_session["prenom"] = "Alice"
        flask_session["admin"] = 1

    with client:
        response = client.get("/logout")
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/")
        assert "prenom" not in session
        assert "admin" not in session
