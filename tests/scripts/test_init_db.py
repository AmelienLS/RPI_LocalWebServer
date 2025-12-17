import sqlite3
import subprocess
import sys
from pathlib import Path


def test_init_db_creates_admin(tmp_path):
    db_path = tmp_path / "custom.db"
    cmd = [
        sys.executable,
        str(Path("scripts") / "init_db.py"),
        "--database",
        str(db_path),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr

    with sqlite3.connect(db_path) as connection:
        row = connection.execute(
            "SELECT identifiant, admin FROM users WHERE identifiant = 'admin'"
        ).fetchone()
    assert row == ("admin", 1)


def test_init_db_force_overwrites(tmp_path):
    db_path = tmp_path / "over.db"
    first_cmd = [
        sys.executable,
        str(Path("scripts") / "init_db.py"),
        "--database",
        str(db_path),
    ]
    subprocess.run(first_cmd, check=True)

    second_cmd = first_cmd + ["--force"]
    result = subprocess.run(second_cmd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
