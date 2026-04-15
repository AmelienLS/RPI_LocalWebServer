import sqlite3


def test_gerer_utilisateurs_requires_admin(client):
    response = client.get("/gerer_utilisateurs")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_gerer_utilisateurs_lists_users(client, add_user, set_user_session):
    set_user_session(admin=True)
    add_user(identifiant="alice", prenom="Alice", nom="Dupont")

    response = client.get("/gerer_utilisateurs")
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "Alice" in body
    assert "Dupont" in body


def test_modifierU_requires_admin(client):
    response = client.get("/modifierU?id=1")
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_modifierU_updates_user(client, add_user, test_db, set_user_session):
    set_user_session(admin=True)
    user = add_user(identifiant="bob", prenom="Bob", nom="Martin")

    response = client.post(
        "/modifierU",
        data={
            "id": str(user["id"]),
            "identifiant": "bob",
            "prenom": "Robert",
            "nom": "Martin",
        },
    )
    assert response.status_code == 302

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT prenom FROM users WHERE id = ?", (user["id"],)
        ).fetchone()
    assert row[0] == "Robert"


def test_modifierU_rejects_duplicate_identifiant(client, add_user, set_user_session):
    set_user_session(admin=True)
    add_user(identifiant="carol", prenom="Carol", nom="A")
    user = add_user(identifiant="dave", prenom="Dave", nom="B")

    response = client.post(
        "/modifierU",
        data={
            "id": str(user["id"]),
            "identifiant": "carol",
            "prenom": "Dave",
            "nom": "B",
        },
    )
    assert response.status_code == 200
    assert "existe déjà" in response.data.decode("utf-8")


def test_supprimerU_requires_admin(client):
    response = client.post("/supprimerU", data={"id": "1"})
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_supprimerU_deletes_user(client, add_user, test_db, set_user_session):
    set_user_session(admin=True, prenom="Admin")
    user = add_user(identifiant="todelete", prenom="ToDel", nom="User")

    response = client.post("/supprimerU", data={"id": str(user["id"])})
    assert response.status_code == 302

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE id = ?", (user["id"],)
        ).fetchone()
    assert row is None


def test_supprimerU_cannot_delete_self(client, add_user, test_db, set_user_session):
    set_user_session(admin=True, prenom="Moi")
    user = add_user(identifiant="moi", prenom="Moi", nom="Admin")

    response = client.post("/supprimerU", data={"id": str(user["id"])})
    assert response.status_code == 302

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT 1 FROM users WHERE id = ?", (user["id"],)
        ).fetchone()
    assert row is not None


def test_ajouterU_requires_admin(client):
    response = client.get("/ajouterU")
    # Sans session : redirige vers / (login)
    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_ajouterU_duplicate_identifiant(client, add_user, set_user_session):
    set_user_session()
    add_user(identifiant="dup-user")

    response = client.post(
        "/ajouterU",
        data={
            "identifiant": "dup-user",
            "prenom": "Dup",
            "nom": "User",
        },
    )
    assert response.status_code == 200
    assert "existe déjà" in response.data.decode("utf-8")


def test_ajouterU_creates_user(client, test_db, set_user_session):
    set_user_session(admin=True)

    response = client.post(
        "/ajouterU",
        data={
            "identifiant": "eve-admin",
            "prenom": "Eve",
            "nom": "Admin",
            "admin": "on",
        },
    )
    assert response.status_code == 200
    assert "Utilisateur ajouté avec succès" in response.data.decode("utf-8")

    with sqlite3.connect(test_db) as connection:
        row = connection.execute(
            "SELECT identifiant, prenom, nom, admin FROM users WHERE identifiant = ?",
            ("eve-admin",),
        ).fetchone()
    assert row == ("eve-admin", "Eve", "Admin", 1)
