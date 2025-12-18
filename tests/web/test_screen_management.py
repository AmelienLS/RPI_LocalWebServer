import sqlite3


def test_modifier_fetches_entry(client, add_serigraphie, set_user_session):
    set_user_session()
    entry = add_serigraphie(ref_ecran=450, libelle="Fetch Screen")

    response = client.post("/modifier", data={"ref_ecran": str(entry["ref_ecran"])})
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert "Fetch Screen" in body
    assert str(entry["ref_ecran"]) in body


def test_modifier_updates_entry(client, add_serigraphie, test_db, set_user_session):
    set_user_session()
    entry = add_serigraphie(ref_ecran=451, libelle="Old Label", fab="AB", n="200")

    response = client.post(
        "/modifier",
        data={
            "old_ref_ecran": str(entry["ref_ecran"]),
            "new_ref_ecran": str(entry["ref_ecran"]),
            "libelle": "Updated Label",
            "pcb": "9999",
            "fab": "CD",
            "n_fab": "F765432",
            "type": "Updated",
            "n": "777",
            "sorti": "0",
            "lave": "1",
        },
    )
    assert response.status_code == 200
    assert "mise à jour avec succès" in response.data.decode("utf-8")

    with sqlite3.connect(test_db) as connection:
        row = connection.execute(
            """
            SELECT libelle, pcb, fab, n_fab, type, n, sorti, lave
            FROM serigraphie
            WHERE ref_ecran = ?
            """,
            (entry["ref_ecran"],),
        ).fetchone()
    assert row == ("Updated Label", 9999, "CD", "F765432", "Updated", "777", 0, 1)


def test_modifier_rejects_duplicate_reference(client, add_serigraphie, test_db, set_user_session):
    set_user_session()
    entry_one = add_serigraphie(ref_ecran=452, libelle="First", n="130")
    entry_two = add_serigraphie(ref_ecran=453, libelle="Second", n="131")

    response = client.post(
        "/modifier",
        data={
            "old_ref_ecran": str(entry_one["ref_ecran"]),
            "new_ref_ecran": str(entry_two["ref_ecran"]),
            "libelle": entry_one["libelle"],
            "pcb": "100",
            "fab": "EF",
            "n_fab": "F000111",
            "type": "TypeA",
            "n": "123",
            "sorti": "0",
            "lave": "0",
        },
    )
    assert response.status_code == 200
    assert "existe déjà" in response.data.decode("utf-8")

    with sqlite3.connect(test_db) as connection:
        row = connection.execute(
            "SELECT ref_ecran FROM serigraphie WHERE ref_ecran = ?",
            (entry_one["ref_ecran"],),
        ).fetchone()
    assert row == (entry_one["ref_ecran"],)


def test_supprimer_requires_admin(client):
    response = client.get("/supprimer")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_supprimer_check_and_delete(client, add_serigraphie, test_db, set_user_session):
    set_user_session()
    entry = add_serigraphie(ref_ecran=500, libelle="Delete Me", n="140")

    check_response = client.post(
        "/supprimer",
        data={"action": "check", "ref_ecran": str(entry["ref_ecran"])},
    )
    assert check_response.status_code == 200
    assert "Delete Me" in check_response.data.decode("utf-8")

    delete_response = client.post(
        "/supprimer",
        data={"action": "delete", "ref_ecran": str(entry["ref_ecran"])},
    )
    assert delete_response.status_code == 200

    with sqlite3.connect(test_db) as connection:
        row = connection.execute(
            "SELECT 1 FROM serigraphie WHERE ref_ecran = ?",
            (entry["ref_ecran"],),
        ).fetchone()
    assert row is None
