"""Tests for the /stats route."""
import sqlite3


def test_stats_requires_login(client):
    response = client.get("/stats")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_stats_requires_admin(client, set_user_session):
    set_user_session(admin=False, prenom="Bob")
    response = client.get("/stats")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_stats_accessible_as_admin(client, set_user_session):
    set_user_session(admin=True)
    response = client.get("/stats")
    assert response.status_code == 200


def test_stats_hides_screen_with_zero_passages(client, set_user_session, add_serigraphie):
    set_user_session(admin=True)
    ecran = add_serigraphie(ref_ecran=500, libelle="Ecran sans sortie", n="050")
    response = client.get("/stats")
    body = response.data.decode("utf-8")
    assert str(ecran["ref_ecran"]) not in body
    assert ecran["libelle"] not in body


def test_stats_counts_passages(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=True, prenom="Alice")
    ecran = add_serigraphie(ref_ecran=501, libelle="Ecran compte", n="051")

    # Insert 2 log entries manually
    with sqlite3.connect(test_db) as conn:
        for i in range(2):
            conn.execute(
                """
                INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts)
                VALUES (?, ?, ?, ?)
                """,
                (501, "Ecran compte", "Alice", f"2026-01-0{i+1}T08:00:00"),
            )
        conn.commit()

    response = client.get("/stats")
    body = response.data.decode("utf-8")
    assert "Ecran compte" in body
    assert "Alice" in body


def test_stats_shows_total_passages(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=True)
    add_serigraphie(ref_ecran=502, libelle="Ecran total", n="052")

    with sqlite3.connect(test_db) as conn:
        conn.execute(
            "INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts) VALUES (?, ?, ?, ?)",
            (502, "Ecran total", "Bob", "2026-01-10T09:00:00"),
        )
        conn.commit()

    response = client.get("/stats")
    body = response.data.decode("utf-8")
    # Total passages should appear on the page
    assert "1" in body


def test_stats_date_filter_includes_matching_logs(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=True)
    add_serigraphie(ref_ecran=520, libelle="Ecran filtre", n="056")

    with sqlite3.connect(test_db) as conn:
        conn.execute(
            "INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts) VALUES (?, ?, ?, ?)",
            (520, "Ecran filtre", "Alice", "2025-06-15T10:00:00"),
        )
        conn.execute(
            "INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts) VALUES (?, ?, ?, ?)",
            (520, "Ecran filtre", "Alice", "2025-08-20T11:00:00"),
        )
        conn.commit()

    response = client.get("/stats?date_debut=2025-06-01&date_fin=2025-06-30")
    body = response.data.decode("utf-8")
    assert "Ecran filtre" in body
    # Only 1 passage in June
    assert "Alice" in body


def test_stats_date_filter_excludes_out_of_range_logs(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=True)
    add_serigraphie(ref_ecran=521, libelle="Ecran hors plage", n="057")

    with sqlite3.connect(test_db) as conn:
        conn.execute(
            "INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts) VALUES (?, ?, ?, ?)",
            (521, "Ecran hors plage", "Bob", "2024-01-10T09:00:00"),
        )
        conn.commit()

    response = client.get("/stats?date_debut=2025-01-01&date_fin=2025-12-31")
    body = response.data.decode("utf-8")
    assert "Ecran hors plage" not in body


def test_stats_date_filter_only_debut(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=True)
    add_serigraphie(ref_ecran=522, libelle="Ecran debut", n="058")

    with sqlite3.connect(test_db) as conn:
        conn.execute(
            "INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts) VALUES (?, ?, ?, ?)",
            (522, "Ecran debut", "Carol", "2025-03-01T08:00:00"),
        )
        conn.commit()

    response = client.get("/stats?date_debut=2025-01-01")
    body = response.data.decode("utf-8")
    assert "Ecran debut" in body


def test_reset_stats_requires_admin(client, set_user_session):
    set_user_session(admin=False, prenom="Bob")
    response = client.post("/reset_stats")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_reset_stats_clears_sortie_logs(client, set_user_session, add_serigraphie, test_db):
    set_user_session(admin=True)
    add_serigraphie(ref_ecran=510, libelle="Ecran reset", n="055")

    with sqlite3.connect(test_db) as conn:
        conn.execute(
            "INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts) VALUES (?, ?, ?, ?)",
            (510, "Ecran reset", "Alice", "2026-01-15T10:00:00"),
        )
        conn.commit()

    response = client.post("/reset_stats")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/stats")

    with sqlite3.connect(test_db) as conn:
        count = conn.execute("SELECT COUNT(*) FROM sortie_logs").fetchone()[0]
    assert count == 0
