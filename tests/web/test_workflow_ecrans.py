import csv
import os
import sqlite3
from datetime import datetime
from pathlib import Path


def _set_user_session(client, admin=False):
    with client.session_transaction() as session:
        session["prenom"] = "Bob"
        session["admin"] = 1 if admin else 0


def test_prendre_requires_login(client):
    response = client.post("/prendre", data={"ref_ecran": "999"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_prendre_marks_screen_as_out(client, add_serigraphie, test_db):
    entry = add_serigraphie(ref_ecran=300, n="045", sorti=0)
    _set_user_session(client)

    response = client.post("/prendre", data={"ref_ecran": str(entry["ref_ecran"])})
    assert response.status_code == 200
    assert b"prise avec" in response.data

    with sqlite3.connect(test_db) as connection:
        cursor = connection.execute(
            "SELECT sorti FROM serigraphie WHERE ref_ecran = ?", (entry["ref_ecran"],)
        )
        (sorti,) = cursor.fetchone()
    assert sorti == 1


def test_ranger_updates_flags(client, add_serigraphie, test_db):
    entry = add_serigraphie(ref_ecran=301, n="046", sorti=1, lave=0)
    _set_user_session(client)

    response = client.post(
        "/ranger",
        data={
            "ref_ecran": str(entry["ref_ecran"]),
            "lavee": "oui",
        },
    )
    assert response.status_code == 200

    with sqlite3.connect(test_db) as connection:
        cursor = connection.execute(
            "SELECT sorti, lave FROM serigraphie WHERE ref_ecran = ?", (entry["ref_ecran"],)
        )
        row = cursor.fetchone()

    assert row == (0, 1)


def test_prendre_creates_daily_trace_file(client, add_serigraphie, monkeypatch):
    import APP

    entry = add_serigraphie(ref_ecran=305, n="050", sorti=0)
    _set_user_session(client)
    fake_now = datetime(2024, 1, 15, 8, 30, 0)
    monkeypatch.setattr(APP, "_current_timestamp", lambda: fake_now)

    response = client.post("/prendre", data={"ref_ecran": str(entry["ref_ecran"])})
    assert response.status_code == 200

    log_dir = Path(os.environ["APP_LOGS_DIR"])
    log_file = log_dir / "15-01-2024.csv"
    assert log_file.exists()

    with log_file.open(encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows[0] == ["ref_ecran", "libelle", "personne", "heure_sortie", "heure_rangement", "lave"]
    assert rows[1] == [
        str(entry["ref_ecran"]),
        entry["libelle"],
        "Bob",
        "08:30:00",
        "",
        "",
    ]


def test_ranger_updates_trace_even_cross_day(client, add_serigraphie, monkeypatch):
    import APP

    entry = add_serigraphie(ref_ecran=306, n="051", sorti=0, lave=0)
    _set_user_session(client)
    timestamps = iter(
        (
            datetime(2024, 2, 10, 9, 0, 0),
            datetime(2024, 2, 11, 11, 45, 0),
        )
    )
    monkeypatch.setattr(APP, "_current_timestamp", lambda: next(timestamps))

    client.post("/prendre", data={"ref_ecran": str(entry["ref_ecran"])})
    response = client.post(
        "/ranger",
        data={
            "ref_ecran": str(entry["ref_ecran"]),
            "lavee": "oui",
        },
    )
    assert response.status_code == 200

    log_dir = Path(os.environ["APP_LOGS_DIR"])
    log_file = log_dir / "10-02-2024.csv"
    with log_file.open(encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows[-1] == [
        str(entry["ref_ecran"]),
        entry["libelle"],
        "Bob",
        "09:00:00",
        "11:45:00 (11-02-2024)",
        "Oui",
    ]
