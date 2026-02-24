import sqlite3


def test_ajouterU_requires_admin(client):
    response = client.get("/ajouterU")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


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
