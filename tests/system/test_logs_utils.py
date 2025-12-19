import csv
import os
import sqlite3
import zipfile
from datetime import date
from pathlib import Path

import APP


def test_build_logs_archive_adds_readme_when_empty(monkeypatch, tmp_path):
    logs_dir = tmp_path / "logs"
    monkeypatch.setenv("APP_LOGS_DIR", str(logs_dir))

    archive_stream = APP._build_logs_archive()

    with zipfile.ZipFile(archive_stream) as archive:
        assert "README.txt" in archive.namelist()
        readme = archive.read("README.txt").decode("utf-8")
        assert "Aucun journal disponible" in readme


def test_sync_daily_log_generates_csv(test_db):
    log_date = date(2024, 4, 2)
    with sqlite3.connect(test_db) as connection:
        connection.row_factory = sqlite3.Row
        connection.execute(
            """
            INSERT INTO sortie_logs (ref_ecran, libelle, personne, sortie_ts, rangement_ts, lavee)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                10,
                "Ecran Trace",
                "Bob",
                "2024-04-02T08:15:00",
                "2024-04-02T09:45:00",
                1,
            ),
        )
        connection.commit()
        APP._sync_daily_log(connection, log_date)

    log_path = Path(os.environ["APP_LOGS_DIR"]) / "02-04-2024.csv"
    assert log_path.exists()
    with log_path.open(encoding="utf-8") as handle:
        rows = list(csv.reader(handle, delimiter=";"))
    assert rows[0] == ["ref_ecran", "libelle", "personne", "heure_sortie", "heure_rangement", "lave"]
    assert rows[1] == ["10", "Ecran Trace", "Bob", "08:15:00", "09:45:00", "Oui"]


def test_sync_daily_log_removes_file_when_no_entries(test_db):
    log_date = date(2024, 4, 5)
    log_path = Path(os.environ["APP_LOGS_DIR"]) / "05-04-2024.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text("old data", encoding="utf-8")

    with sqlite3.connect(test_db) as connection:
        connection.row_factory = sqlite3.Row
        APP._sync_daily_log(connection, log_date)

    assert not log_path.exists()
