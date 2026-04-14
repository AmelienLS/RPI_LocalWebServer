def test_close_db_redirects_to_index(client, set_user_session):
    set_user_session(admin=True)
    response = client.get("/close_db")
    assert response.status_code == 302
    assert response.headers["Location"] == "/index"


def test_close_db_without_session_redirects(client):
    response = client.get("/close_db")
    # La redirection vers /index est faite, puis /index redirige vers / si non connecté
    assert response.status_code == 302
    assert response.headers["Location"] == "/index"
