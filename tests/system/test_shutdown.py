import APP


def test_shutdown_linux_invokes_system(monkeypatch, client):
    calls = {}
    monkeypatch.setattr(APP.platform, "system", lambda: "Linux")
    monkeypatch.setattr(APP.subprocess, "run", lambda cmd: calls.setdefault("cmd", cmd))

    response = client.post("/shutdown")
    assert response.status_code == 200
    assert calls["cmd"] == ["/usr/bin/sudo", "shutdown", "-h", "now"]
    assert "Arrêt du système" in response.data.decode("utf-8")


def test_shutdown_windows_exits_process(monkeypatch, client):
    exit_called = {}

    def fake_exit(code):
        exit_called["code"] = code

    monkeypatch.setattr(APP.platform, "system", lambda: "Windows")
    monkeypatch.setattr(APP.os, "_exit", fake_exit)

    response = client.post("/shutdown")
    assert response.status_code == 200
    assert exit_called["code"] == 0
    assert "Serveur Windows arrêté" in response.data.decode("utf-8")


def test_shutdown_accessible_without_auth(monkeypatch, client):
    """Le bouton Éteindre est sur la page de login — intentionnellement sans auth (kiosque)."""
    # Prevent actual shutdown or process exit on the GitHub Actions VM
    monkeypatch.setattr(APP.subprocess, "run", lambda *args, **kwargs: None)
    monkeypatch.setattr(APP.os, "_exit", lambda code: None)

    response = client.post("/shutdown")
    # Ne doit pas retourner 401/403
    assert response.status_code == 200
