import sqlite3

import APP
from flask import session


def test_index_requires_login(client):
    response = client.get("/index")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_index_renders_admin_view(client, set_user_session):
    set_user_session(admin=True, prenom="Alice")
    response = client.get("/index")
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "Bienvenue, Alice" in body
    assert "Administration" in body


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


def test_login_missing_database_shows_hint(client, monkeypatch):
    monkeypatch.setattr(APP, "database_ready", lambda: False)

    response = client.get("/")
    assert response.status_code == 200
    assert "La base de données est introuvable" in response.data.decode("utf-8")


def test_login_handles_db_operational_error(client, monkeypatch):
    class BrokenConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def cursor(self):
            raise sqlite3.OperationalError("boom")

    monkeypatch.setattr(APP, "get_db_connection", lambda: BrokenConnection())

    response = client.post("/", data={"identifiant": "any"})
    assert response.status_code == 200
    assert "Erreur base de données" in response.data.decode("utf-8")


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
