import sqlite3


def _set_admin_session(client):
    with client.session_transaction() as session:
        session["prenom"] = "Admin"
        session["admin"] = 1


def test_ajouter_requires_admin(client):
    response = client.get("/ajouter")
    # Non admin users are redirected to /index
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_ajouter_validation_error(client):
    _set_admin_session(client)
    response = client.post(
        "/ajouter",
        data={
            "ref_ecran": "100",
            "libelle": "Lib",
            "pcb": "10",
            "fab": "A",  # invalid length
            "n_fab": "",
            "type": "Type",
            "n": "123",
        },
    )
    assert response.status_code == 200
    assert b"ne respectent pas les contraintes" in response.data


def test_ajouter_success_inserts_row(client, test_db):
    _set_admin_session(client)
    response = client.post(
        "/ajouter",
        data={
            "ref_ecran": "200",
            "libelle": "Super ecran",
            "pcb": "900",
            "fab": "AB",
            "n_fab": "F000001",
            "type": "TypeY",
            "n": "321",
        },
    )
    assert response.status_code == 200
    assert b"ajout" in response.data.lower()

    with sqlite3.connect(test_db) as connection:
        cursor = connection.execute(
            "SELECT ref_ecran, libelle, fab, n FROM serigraphie WHERE ref_ecran = ?", (200,)
        )
        row = cursor.fetchone()

    assert row == (200, "Super ecran", "AB", "321")
