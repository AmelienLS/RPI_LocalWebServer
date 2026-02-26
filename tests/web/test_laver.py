"""Tests for the /laver route and the washing section on /index."""
import sqlite3


# ---------------------------------------------------------------------------
# /laver route
# ---------------------------------------------------------------------------

def test_laver_requires_login(client):
    response = client.post("/laver", data={"ref_ecran": "1001"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_laver_marks_screen_as_washed(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=False, prenom="Alice")
    add_serigraphie(ref_ecran=600, libelle="Ecran lavage", n="060", sorti=0, lave=0)

    response = client.post("/laver", data={"ref_ecran": "600"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")

    with sqlite3.connect(test_db) as conn:
        row = conn.execute("SELECT lave FROM serigraphie WHERE ref_ecran = 600").fetchone()
    assert row[0] == 1


def test_laver_updates_sortie_logs(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=False, prenom="Bob")
    add_serigraphie(ref_ecran=601, libelle="Ecran log", n="061", sorti=0, lave=0)

    # Insert a log entry simulating a return without washing
    with sqlite3.connect(test_db) as conn:
        conn.execute(
            """
            INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts, rangement_ts, lavee)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (601, "Ecran log", "Bob", "2026-01-15T08:00:00", "2026-01-15T17:00:00", 0),
        )
        conn.commit()

    client.post("/laver", data={"ref_ecran": "601"})

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT lavee FROM sortie_logs WHERE ref_ecran = 601"
        ).fetchone()
    assert row[0] == 1


def test_laver_ignores_screen_already_washed(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=False, prenom="Alice")
    add_serigraphie(ref_ecran=602, libelle="Ecran propre", n="062", sorti=0, lave=1)

    client.post("/laver", data={"ref_ecran": "602"})

    with sqlite3.connect(test_db) as conn:
        row = conn.execute("SELECT lave FROM serigraphie WHERE ref_ecran = 602").fetchone()
    assert row[0] == 1  # unchanged


def test_laver_ignores_screen_currently_out(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=False, prenom="Alice")
    add_serigraphie(ref_ecran=603, libelle="Ecran sorti", n="063", sorti=1, lave=0)

    client.post("/laver", data={"ref_ecran": "603"})

    with sqlite3.connect(test_db) as conn:
        row = conn.execute(
            "SELECT sorti, lave FROM serigraphie WHERE ref_ecran = 603"
        ).fetchone()
    assert row[0] == 1  # still out
    assert row[1] == 0  # not marked as washed


def test_laver_no_log_entry_still_updates_serigraphie(client, set_user_session, add_serigraphie, test_db):
    """lave=0 set via /modifier (no sortie_logs entry) — serigraphie is still updated."""
    set_user_session(admin=False, prenom="Alice")
    add_serigraphie(ref_ecran=604, libelle="Ecran sans log", n="064", sorti=0, lave=0)

    client.post("/laver", data={"ref_ecran": "604"})

    with sqlite3.connect(test_db) as conn:
        row = conn.execute("SELECT lave FROM serigraphie WHERE ref_ecran = 604").fetchone()
    assert row[0] == 1


# ---------------------------------------------------------------------------
# /index — washing section
# ---------------------------------------------------------------------------

def test_index_shows_laver_section_when_screens_need_washing(
    client, set_user_session, add_serigraphie
):
    set_user_session(admin=False, prenom="Alice")
    ecran = add_serigraphie(ref_ecran=605, libelle="A laver", n="065", sorti=0, lave=0)

    response = client.get("/index")
    body = response.data.decode("utf-8")
    assert str(ecran["ref_ecran"]) in body
    assert ecran["libelle"] in body
    assert ecran["n"] in body


def test_index_hides_laver_section_when_nothing_to_wash(
    client, set_user_session, add_serigraphie
):
    set_user_session(admin=False, prenom="Alice")
    add_serigraphie(ref_ecran=606, libelle="Propre", n="066", sorti=0, lave=1)

    response = client.get("/index")
    body = response.data.decode("utf-8")
    assert "laver-actions" not in body
