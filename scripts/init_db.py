#!/usr/bin/env python3
"""
Utility script used to bootstrap the SQLite database required by the Flask app.

Examples
--------
Create or reset the database that lives in the instance/ directory:

    python scripts/init_db.py --force

Create a database somewhere else and skip the default admin account:

    python scripts/init_db.py --database /tmp/armoire.db --skip-admin
"""

from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = PROJECT_ROOT / "instance" / "armoire.db"
SCHEMA_PATH = PROJECT_ROOT / "database" / "schema.sql"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialise la base de données SQLite.")
    parser.add_argument(
        "--database",
        default=str(DEFAULT_DB_PATH),
        help=f"Chemin vers le fichier .db à créer (défaut: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Ecrase la base s'il existe déjà un fichier à cet emplacement.",
    )
    parser.add_argument(
        "--skip-admin",
        action="store_true",
        help="Ne crée pas de compte administrateur par défaut.",
    )
    parser.add_argument(
        "--admin-identifiant",
        default="admin",
        help="Identifiant de connexion du compte administrateur à créer.",
    )
    parser.add_argument(
        "--admin-prenom",
        default="Admin",
        help="Prénom du compte administrateur par défaut.",
    )
    parser.add_argument(
        "--admin-nom",
        default="Utilisateur",
        help="Nom du compte administrateur par défaut.",
    )
    return parser.parse_args()


def load_schema() -> str:
    if not SCHEMA_PATH.exists():
        raise FileNotFoundError(f"Schema introuvable: {SCHEMA_PATH}")
    return SCHEMA_PATH.read_text(encoding="utf-8")


def create_database(db_path: Path, schema_sql: str) -> None:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(db_path) as connection:
        connection.executescript(schema_sql)


def create_default_admin(connection: sqlite3.Connection, identifiant: str, prenom: str, nom: str) -> None:
    connection.execute(
        """
        INSERT OR IGNORE INTO users (identifiant, prenom, nom, admin)
        VALUES (?, ?, ?, 1)
        """,
        (identifiant, prenom, nom),
    )
    connection.commit()


def main() -> int:
    args = parse_args()
    db_path = Path(args.database).expanduser().resolve()
    schema_sql = load_schema()

    if db_path.exists():
        if not args.force:
            print(f"[!] Le fichier {db_path} existe déjà. Utilisez --force pour l'écraser.", file=sys.stderr)
            return 1
        db_path.unlink()

    print(f"[i] Création de la base de données à {db_path}")
    create_database(db_path, schema_sql)

    if not args.skip_admin:
        with sqlite3.connect(db_path) as connection:
            print(f"[i] Ajout du compte administrateur par défaut '{args.admin_identifiant}'")
            create_default_admin(connection, args.admin_identifiant, args.admin_prenom, args.admin_nom)

    print("[✓] Base de données initialisée avec succès.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
