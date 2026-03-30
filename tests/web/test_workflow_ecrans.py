import csv
import io
import os
import sqlite3
import zipfile
from datetime import datetime
from pathlib import Path


def test_prendre_requires_login(client):
    response = client.post("/prendre", data={"ref_ecran": "999"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_prendre_marks_screen_as_out(client, add_serigraphie, test_db, set_user_session):
    entry = add_serigraphie(ref_ecran=300, n="045", sorti=0)
    set_user_session(prenom="Bob")

    response = client.post("/prendre", data={"ref_ecran": str(entry["ref_ecran"])})
    assert response.status_code == 200
    assert b"pris avec" in response.data

    with sqlite3.connect(test_db) as connection:
        cursor = connection.execute(
            "SELECT sorti FROM serigraphie WHERE ref_ecran = ?", (entry["ref_ecran"],)
        )
        (sorti,) = cursor.fetchone()
    assert sorti == 1


def test_ranger_updates_flags(client, add_serigraphie, test_db, set_user_session):
    entry = add_serigraphie(ref_ecran=301, n="046", sorti=1, lave=0)
    set_user_session(prenom="Bob")

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


def test_prendre_creates_daily_trace_file(client, add_serigraphie, monkeypatch, set_user_session):
    import APP

    entry = add_serigraphie(ref_ecran=305, n="050", sorti=0)
    set_user_session(prenom="Bob")
    fake_now = datetime(2024, 1, 15, 8, 30, 0)
    monkeypatch.setattr(APP, "_current_timestamp", lambda: fake_now)

    response = client.post("/prendre", data={"ref_ecran": str(entry["ref_ecran"])})
    assert response.status_code == 200

    log_dir = Path(os.environ["APP_LOGS_DIR"])
    log_file = log_dir / "15-01-2024.csv"
    assert log_file.exists()

    with log_file.open(encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))

    assert rows[0] == ["ref_ecran", "libelle", "personne", "personne_rangement", "heure_sortie", "heure_rangement", "lave"]
    assert rows[1] == [
        str(entry["ref_ecran"]),
        entry["libelle"],
        "Bob",
        "",
        "08:30:00",
        "",
        "",
    ]


def test_ranger_updates_trace_even_cross_day(client, add_serigraphie, monkeypatch, set_user_session):
    import APP

    entry = add_serigraphie(ref_ecran=306, n="051", sorti=0, lave=0)
    set_user_session(prenom="Bob")
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
        "Bob",
        "09:00:00",
        "11:45:00 (11-02-2024)",
        "Oui",
    ]


def test_export_logs_requires_admin(client, set_user_session):
    set_user_session(admin=False)
    response = client.get("/export_logs")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_export_logs_builds_zip(client, set_user_session):
    set_user_session(admin=True)
    logs_dir = Path(os.environ["APP_LOGS_DIR"])
    logs_dir.mkdir(parents=True, exist_ok=True)
    sample = logs_dir / "01-03-2024.csv"
    sample.write_text("ref;libelle\n1;TEST\n", encoding="utf-8")

    response = client.get("/export_logs")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/zip")
    assert response.headers["Content-Disposition"].startswith("attachment; filename=screen_logs_")

    with zipfile.ZipFile(io.BytesIO(response.data)) as archive:
        names = archive.namelist()
        assert "01-03-2024.csv" in names


def test_purge_logs_requires_admin(client, set_user_session):
    set_user_session(admin=False)
    response = client.post("/purge_logs")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/index")


def test_purge_logs_exports_and_deletes(client, set_user_session):
    set_user_session(admin=True)
    logs_dir = Path(os.environ["APP_LOGS_DIR"])
    logs_dir.mkdir(parents=True, exist_ok=True)
    sample = logs_dir / "02-03-2024.csv"
    sample.write_text("ref;libelle\n2;TEST\n", encoding="utf-8")

    response = client.post("/purge_logs")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"].startswith("attachment; filename=screen_logs_cleared_")
    assert not any(logs_dir.glob("*.csv"))

    with zipfile.ZipFile(io.BytesIO(response.data)) as archive:
        assert "02-03-2024.csv" in archive.namelist()


def test_prendre_suffix_match_single(client, add_serigraphie, test_db, set_user_session):
    """Typing the last characters of a ref_ecran should find the screen."""
    add_serigraphie(ref_ecran=50100, n="070", sorti=0)
    set_user_session(prenom="Bob")

    # Only type the last 3 digits
    response = client.post("/prendre", data={"ref_ecran": "100"})
    assert response.status_code == 200
    assert b"pris avec" in response.data

    with sqlite3.connect(test_db) as connection:
        cursor = connection.execute(
            "SELECT sorti FROM serigraphie WHERE ref_ecran = ?", (50100,)
        )
        (sorti,) = cursor.fetchone()
    assert sorti == 1


def test_prendre_suffix_match_multiple(client, add_serigraphie, set_user_session):
    """When multiple screens match a suffix, show disambiguation message."""
    add_serigraphie(ref_ecran=10200, n="071", sorti=0)
    add_serigraphie(ref_ecran=20200, n="072", sorti=0)
    set_user_session(prenom="Bob")

    response = client.post("/prendre", data={"ref_ecran": "200"})
    assert response.status_code == 200
    html = response.data.decode("utf-8")
    assert "Plusieurs" in html
    assert "10200" in html
    assert "20200" in html


def test_prendre_suffix_match_none(client, add_serigraphie, set_user_session):
    """When no screen matches the suffix, show error."""
    add_serigraphie(ref_ecran=99999, n="073", sorti=0)
    set_user_session(prenom="Bob")

    response = client.post("/prendre", data={"ref_ecran": "00000"})
    assert response.status_code == 200
    assert "non trouv" in response.data.decode("utf-8")


def test_ranger_displays_error_for_unknown_reference(client, set_user_session):
    set_user_session(prenom="Bob")

    response = client.post(
        "/ranger",
        data={
            "ref_ecran": "999",
            "lavee": "oui",
        },
    )
    assert response.status_code == 200
    assert "n&#39;existe pas" in response.data.decode("utf-8")


def test_ranger_handles_missing_log_entry(client, add_serigraphie, test_db, set_user_session, monkeypatch):
    import APP

    entry = add_serigraphie(ref_ecran=310, n="060", sorti=1, lave=0)
    set_user_session(prenom="Bob")
    sync_calls = []
    monkeypatch.setattr(APP, "_sync_daily_log", lambda conn, day: sync_calls.append(day))

    response = client.post(
        "/ranger",
        data={
            "ref_ecran": str(entry["ref_ecran"]),
            "lavee": "non",
        },
    )
    assert response.status_code == 200
    assert sync_calls == []

    with sqlite3.connect(test_db) as connection:
        row = connection.execute(
            "SELECT sorti, lave FROM serigraphie WHERE ref_ecran = ?",
            (entry["ref_ecran"],),
        ).fetchone()
    assert row == (0, 0)
