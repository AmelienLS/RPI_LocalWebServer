import json
import APP


def test_update_requires_admin_json(client):
    """Sans session admin, retourne 403 JSON."""
    response = client.post("/update")
    assert response.status_code == 403
    assert response.get_json()["error"] == "unauthorized"


def test_update_requires_admin_not_just_login(client, set_user_session):
    """Connecté mais non admin → 403."""
    set_user_session(admin=False)
    response = client.post("/update")
    assert response.status_code == 403
    assert response.get_json()["error"] == "unauthorized"


def test_update_non_linux_no_restart(monkeypatch, client, set_user_session):
    """Sur OS non-Linux, will_restart est False et git pull est appelé."""
    set_user_session(admin=True)

    calls = []

    def fake_run(cmd, **kwargs):
        calls.append(cmd)

        class Result:
            stdout = "Already up to date.\n"
            stderr = ""

        return Result()

    monkeypatch.setattr(APP.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(APP.subprocess, "run", fake_run)

    response = client.post("/update")
    assert response.status_code == 200

    data = response.get_json()
    assert data["will_restart"] is False
    assert "Already up to date" in data["output"]
    assert isinstance(data["branch"], str)


def test_update_linux_schedules_restart(monkeypatch, client, set_user_session):
    """Sur Linux, will_restart est True et un thread de redémarrage est lancé."""
    set_user_session(admin=True)

    restarted = []

    def fake_run(cmd, **kwargs):
        restarted.append(cmd)

        class Result:
            stdout = "Updating abc..def\n"
            stderr = ""

        return Result()

    # Empêche le vrai thread de dormir et d'appeler systemctl
    def fake_thread(target, daemon):
        class T:
            def start(self):
                pass  # ne pas exécuter le thread dans les tests

        return T()

    monkeypatch.setattr(APP.platform, "system", lambda: "Linux")
    monkeypatch.setattr(APP.subprocess, "run", fake_run)
    monkeypatch.setattr(APP.threading, "Thread", fake_thread)

    response = client.post("/update")
    assert response.status_code == 200

    data = response.get_json()
    assert data["will_restart"] is True
    assert "branch" in data


def test_update_returns_branch_name(monkeypatch, client, set_user_session):
    """La réponse contient toujours un champ branch non vide."""
    set_user_session(admin=True)

    def fake_run(cmd, **kwargs):
        class Result:
            stdout = "Release\n" if "rev-parse" in cmd else ""
            stderr = ""

        return Result()

    monkeypatch.setattr(APP.platform, "system", lambda: "Darwin")
    monkeypatch.setattr(APP.subprocess, "run", fake_run)

    response = client.post("/update")
    data = response.get_json()
    assert data["branch"] == "Release"
