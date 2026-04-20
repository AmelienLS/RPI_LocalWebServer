"""Tests for user management routes: ajouterU, modifierU, supprimerU, gerer_utilisateurs."""
import sqlite3


# ---------------------------------------------------------------------------
# /ajouterU
# ---------------------------------------------------------------------------

def test_ajouterU_requires_admin(client, set_user_session):
    set_user_session(admin=False)
    response = client.get("/ajouterU")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_ajouterU_creates_non_admin_user_when_admin_field_empty(
    client, set_user_session, test_db
):
    """Hidden input admin='' (role bouton Utilisateur) → admin doit valoir 0."""
    set_user_session(admin=True, prenom="Admin")
    response = client.post(
        "/ajouterU",
        data={"prenom": "Marie", "nom": "Dupont", "identifiant": "mdupont", "admin": ""},
    )
    assert response.status_code == 200
    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT admin FROM users WHERE identifiant = 'mdupont'"
        ).fetchone()
    assert row is not None
    assert row[0] == 0


def test_ajouterU_creates_admin_user_when_admin_field_on(
    client, set_user_session, test_db
):
    """Hidden input admin='on' (role bouton Administrateur) → admin doit valoir 1."""
    set_user_session(admin=True, prenom="Admin")
    response = client.post(
        "/ajouterU",
        data={"prenom": "Jean", "nom": "Martin", "identifiant": "jmartin", "admin": "on"},
    )
    assert response.status_code == 200
    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT admin FROM users WHERE identifiant = 'jmartin'"
        ).fetchone()
    assert row is not None
    assert row[0] == 1


def test_ajouterU_rejects_duplicate_identifiant(client, set_user_session, add_user):
    set_user_session(admin=True, prenom="Admin")
    add_user(identifiant="existant", prenom="Paul", nom="Blanc")
    response = client.post(
        "/ajouterU",
        data={"prenom": "Autre", "nom": "Nom", "identifiant": "existant", "admin": ""},
    )
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "existe déjà" in body


# ---------------------------------------------------------------------------
# /modifierU
# ---------------------------------------------------------------------------

def test_modifierU_requires_admin(client, set_user_session):
    set_user_session(admin=False)
    response = client.post("/modifierU", data={"id": "1", "identifiant": "x", "prenom": "x", "nom": "x", "admin": ""})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_modifierU_sets_admin_to_zero_when_field_empty(
    client, set_user_session, add_user, test_db
):
    """Modifier un utilisateur admin → non-admin via admin='' doit passer admin à 0."""
    set_user_session(admin=True, prenom="Admin")
    user = add_user(identifiant="cible", prenom="Cible", nom="User", admin=1)

    client.post(
        "/modifierU",
        data={
            "id": str(user["id"]),
            "identifiant": "cible",
            "prenom": "Cible",
            "nom": "User",
            "admin": "",
        },
    )
    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT admin FROM users WHERE identifiant = 'cible'"
        ).fetchone()
    assert row[0] == 0


def test_modifierU_sets_admin_to_one_when_field_on(
    client, set_user_session, add_user, test_db
):
    """Modifier un utilisateur non-admin → admin via admin='on' doit passer admin à 1."""
    set_user_session(admin=True, prenom="Admin")
    user = add_user(identifiant="promo", prenom="Promo", nom="User", admin=0)

    client.post(
        "/modifierU",
        data={
            "id": str(user["id"]),
            "identifiant": "promo",
            "prenom": "Promo",
            "nom": "User",
            "admin": "on",
        },
    )
    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT admin FROM users WHERE identifiant = 'promo'"
        ).fetchone()
    assert row[0] == 1


def test_modifierU_rejects_duplicate_identifiant(
    client, set_user_session, add_user
):
    set_user_session(admin=True, prenom="Admin")
    add_user(identifiant="taken", prenom="Taken", nom="User")
    user = add_user(identifiant="tochange", prenom="ToChange", nom="User")

    response = client.post(
        "/modifierU",
        data={
            "id": str(user["id"]),
            "identifiant": "taken",
            "prenom": "ToChange",
            "nom": "User",
            "admin": "",
        },
    )
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "existe déjà" in body


# ---------------------------------------------------------------------------
# /supprimerU
# ---------------------------------------------------------------------------

def test_supprimerU_deletes_user(client, set_user_session, add_user, test_db):
    set_user_session(admin=True, prenom="Admin")
    user = add_user(identifiant="todelete", prenom="ToDelete", nom="User")

    response = client.post("/supprimerU", data={"id": str(user["id"])})
    assert response.status_code == 302

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE identifiant = 'todelete'"
        ).fetchone()
    assert row is None


def test_supprimerU_cannot_delete_self(client, set_user_session, add_user, test_db):
    """Un admin ne peut pas se supprimer lui-même (même prénom dans la session)."""
    set_user_session(admin=True, prenom="Admin")
    user = add_user(identifiant="selfdelete", prenom="Admin", nom="Self")

    client.post("/supprimerU", data={"id": str(user["id"])})

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT id FROM users WHERE identifiant = 'selfdelete'"
        ).fetchone()
    assert row is not None


# ---------------------------------------------------------------------------
# /gerer_utilisateurs
# ---------------------------------------------------------------------------

def test_gerer_utilisateurs_requires_admin(client, set_user_session):
    set_user_session(admin=False)
    response = client.get("/gerer_utilisateurs")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_gerer_utilisateurs_lists_users(client, set_user_session, add_user):
    set_user_session(admin=True, prenom="Admin")
    add_user(identifiant="u1", prenom="Alice", nom="Dupont")
    add_user(identifiant="u2", prenom="Bob", nom="Martin")

    response = client.get("/gerer_utilisateurs")
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "Alice" in body
    assert "Bob" in body
