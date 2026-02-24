def test_ecran_requires_login(client):
    response = client.get("/ecran")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_ecran_lists_entries(client, add_serigraphie, set_user_session):
    set_user_session(admin=False, prenom="Bob")
    entry_one = add_serigraphie(ref_ecran=400, libelle="Ecran One", n="101")
    entry_two = add_serigraphie(ref_ecran=401, libelle="Ecran Two", n="102")

    response = client.get("/ecran")
    assert response.status_code == 200
    body = response.data.decode("utf-8")
    assert entry_one["libelle"] in body
    assert entry_two["libelle"] in body
