"""Tests for the database setup page and config.ini persistence."""
import configparser
import importlib
import os
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _reload_app(monkeypatch, db_path: Path | None = None):
    """Re-import APP with a controlled DATABASE_PATH env var."""
    if db_path is not None:
        monkeypatch.setenv("DATABASE_PATH", str(db_path))
    else:
        monkeypatch.delenv("DATABASE_PATH", raising=False)
    import APP as app_module
    importlib.reload(app_module)
    return app_module


# ---------------------------------------------------------------------------
# _load_db_path_from_config / _save_db_path_to_config
# ---------------------------------------------------------------------------

def test_load_db_path_returns_none_when_no_config(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_INSTANCE_DIR", str(tmp_path))
    import APP as app_module
    importlib.reload(app_module)
    assert app_module._load_db_path_from_config() is None


def test_save_and_load_db_path_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_INSTANCE_DIR", str(tmp_path))
    import APP as app_module
    importlib.reload(app_module)

    fake_db = tmp_path / "mydb.db"
    fake_db.touch()

    app_module._save_db_path_to_config(fake_db)
    loaded = app_module._load_db_path_from_config()
    assert loaded == fake_db


def test_save_db_path_creates_valid_ini(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_INSTANCE_DIR", str(tmp_path))
    import APP as app_module
    importlib.reload(app_module)

    fake_db = tmp_path / "armoire.db"
    fake_db.touch()
    app_module._save_db_path_to_config(fake_db)

    cfg = configparser.ConfigParser()
    cfg.read(tmp_path / "config.ini", encoding="utf-8")
    assert cfg.get("database", "path") == str(fake_db)


# ---------------------------------------------------------------------------
# database_ready()
# ---------------------------------------------------------------------------

def test_database_ready_false_when_missing(tmp_path, monkeypatch):
    missing = tmp_path / "nonexistent.db"
    monkeypatch.setenv("DATABASE_PATH", str(missing))
    import APP as app_module
    app_module.DATABASE_PATH = missing
    assert not app_module.database_ready()


def test_database_ready_true_when_present(tmp_path, monkeypatch):
    db = tmp_path / "armoire.db"
    db.touch()
    monkeypatch.setenv("DATABASE_PATH", str(db))
    import APP as app_module
    app_module.DATABASE_PATH = db
    assert app_module.database_ready()


# ---------------------------------------------------------------------------
# GET /setup
# ---------------------------------------------------------------------------

def test_setup_get_returns_200_when_db_missing(app, monkeypatch):
    """GET /setup must always be accessible (not blocked by before_request)."""
    import APP as app_module
    app_module.DATABASE_PATH = Path("/nonexistent/armoire.db")
    flask_app = app_module.app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        resp = c.get("/setup")
    assert resp.status_code == 200
    assert b"Configuration" in resp.data


# ---------------------------------------------------------------------------
# POST /setup
# ---------------------------------------------------------------------------

def test_setup_post_valid_path_saves_and_redirects(tmp_path, monkeypatch, app):
    monkeypatch.setenv("APP_INSTANCE_DIR", str(tmp_path))
    import APP as app_module
    importlib.reload(app_module)

    real_db = tmp_path / "armoire.db"
    real_db.touch()
    # Point DATABASE_PATH to a missing file so the before_request would redirect
    app_module.DATABASE_PATH = tmp_path / "missing.db"

    flask_app = app_module.app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        resp = c.post("/setup", data={"path": str(real_db)})

    assert resp.status_code == 302
    assert resp.headers["Location"] in ("/", "http://localhost/")
    # config.ini must have been created
    assert (tmp_path / "config.ini").exists()
    # DATABASE_PATH must have been updated
    assert app_module.DATABASE_PATH == real_db


def test_setup_post_invalid_path_shows_error(tmp_path, monkeypatch, app):
    monkeypatch.setenv("APP_INSTANCE_DIR", str(tmp_path))
    import APP as app_module
    importlib.reload(app_module)

    app_module.DATABASE_PATH = tmp_path / "missing.db"
    flask_app = app_module.app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        resp = c.post("/setup", data={"path": "/does/not/exist/armoire.db"})

    assert resp.status_code == 200
    assert b"introuvable" in resp.data


# ---------------------------------------------------------------------------
# before_request guard
# ---------------------------------------------------------------------------

def test_before_request_redirects_to_setup_when_db_missing(app):
    import APP as app_module
    app_module.DATABASE_PATH = Path("/nonexistent/armoire.db")
    flask_app = app_module.app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        resp = c.get("/")
    assert resp.status_code == 302
    assert "/setup" in resp.headers["Location"]


def test_before_request_no_redirect_for_setup_itself(app):
    import APP as app_module
    app_module.DATABASE_PATH = Path("/nonexistent/armoire.db")
    flask_app = app_module.app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        resp = c.get("/setup")
    # Must NOT redirect (infinite loop prevention)
    assert resp.status_code != 302


def test_before_request_no_redirect_when_db_present(app, test_db):
    """Normal operation: login page is served when DB is present."""
    import APP as app_module
    app_module.DATABASE_PATH = test_db
    flask_app = app_module.app
    flask_app.config["TESTING"] = True
    with flask_app.test_client() as c:
        resp = c.get("/")
    assert resp.status_code == 200
