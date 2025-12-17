import os
import sqlite3
import sys
from pathlib import Path
from typing import Callable, Dict, Any

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def _init_database(db_path: Path) -> None:
    """Create a fresh SQLite database using the shared schema."""
    schema_sql = SCHEMA_PATH.read_text(encoding="utf-8")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.executescript(schema_sql)


@pytest.fixture()
def test_db(monkeypatch, tmp_path) -> Path:
    """
    Provide a temporary SQLite database path and point the Flask app to it
    via the DATABASE_PATH environment variable.
    """
    db_path = tmp_path / "armoire.test.db"
    monkeypatch.setenv("DATABASE_PATH", str(db_path))
    logs_dir = tmp_path / "logs"
    monkeypatch.setenv("APP_LOGS_DIR", str(logs_dir))
    _init_database(db_path)
    return db_path


@pytest.fixture()
def app(test_db):
    """Return a Flask app configured for testing with the temporary DB."""
    import APP as app_module

    test_db_path = Path(os.environ["DATABASE_PATH"])
    app_module.DATABASE_PATH = test_db_path

    flask_app = app_module.app
    flask_app.config.update(
        {
            "TESTING": True,
        }
    )
    yield flask_app


@pytest.fixture()
def client(app):
    """Flask test client helper."""
    return app.test_client()


@pytest.fixture()
def add_user(test_db) -> Callable[..., Dict[str, Any]]:
    """Utility fixture to insert a user in the temporary database."""

    def _add_user(
        identifiant: str = "user1",
        prenom: str = "Test",
        nom: str = "User",
        admin: int = 0,
    ) -> Dict[str, Any]:
        with sqlite3.connect(test_db) as connection:
            connection.execute(
                "INSERT INTO users (identifiant, prenom, nom, admin) VALUES (?, ?, ?, ?)",
                (identifiant, prenom, nom, admin),
            )
            connection.commit()
            cursor = connection.execute(
                "SELECT id, identifiant, prenom, nom, admin FROM users WHERE identifiant = ?",
                (identifiant,),
            )
            row = cursor.fetchone()
        return {
            "id": row[0],
            "identifiant": row[1],
            "prenom": row[2],
            "nom": row[3],
            "admin": row[4],
        }

    return _add_user


@pytest.fixture()
def add_serigraphie(test_db) -> Callable[..., Dict[str, Any]]:
    """Utility fixture to insert a serigraphie entry for tests."""

    def _add_serigraphie(
        ref_ecran: int = 1001,
        libelle: str = "Ref test",
        pcb: int = 123,
        fab: str = "AB",
        n_fab: str = "F123456",
        type_: str = "TypeX",
        n: str = "001",
        sorti: int = 0,
        lave: int = 1,
    ) -> Dict[str, Any]:
        with sqlite3.connect(test_db) as connection:
            connection.execute(
                """
                INSERT INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n, sorti, lave)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (ref_ecran, libelle, pcb, fab, n_fab, type_, n, sorti, lave),
            )
            connection.commit()
            cursor = connection.execute(
                "SELECT ref_ecran, libelle, pcb, fab, n_fab, type, n, sorti, lave FROM serigraphie WHERE ref_ecran = ?",
                (ref_ecran,),
            )
            row = cursor.fetchone()
        return {
            "ref_ecran": row[0],
            "libelle": row[1],
            "pcb": row[2],
            "fab": row[3],
            "n_fab": row[4],
            "type": row[5],
            "n": row[6],
            "sorti": row[7],
            "lave": row[8],
        }

    return _add_serigraphie
