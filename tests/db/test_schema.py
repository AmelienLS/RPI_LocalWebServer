import sqlite3
from pathlib import Path

import pytest

SCHEMA_SQL = Path(__file__).resolve().parents[2] / "database" / "schema.sql"


def _connection():
    conn = sqlite3.connect(":memory:")
    schema = SCHEMA_SQL.read_text(encoding="utf-8")
    conn.executescript(schema)
    return conn


def test_users_identifiant_unique():
    conn = _connection()
    conn.execute(
        "INSERT INTO users (identifiant, prenom, nom, admin) VALUES (?, ?, ?, ?)",
        ("dup", "A", "B", 0),
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO users (identifiant, prenom, nom, admin) VALUES (?, ?, ?, ?)",
            ("dup", "X", "Y", 1),
        )


def test_serigraphie_ref_and_n_unique():
    conn = _connection()
    conn.execute(
        """
        INSERT INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n)
        VALUES (1, 'L1', 10, 'AB', 'F000001', 'Type', '001')
        """
    )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n)
            VALUES (1, 'L2', 11, 'CD', 'F000002', 'Type', '002')
            """
        )
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            """
            INSERT INTO serigraphie (ref_ecran, libelle, pcb, fab, n_fab, type, n)
            VALUES (2, 'L3', 12, 'EF', 'F000003', 'Type', '001')
            """
        )
