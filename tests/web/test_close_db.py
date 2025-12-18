def test_close_db_displays_confirmation(client, set_user_session):
    set_user_session(admin=True)
    response = client.get("/close_db")
    assert response.status_code == 200
    assert "connexion à la base de données a été fermée" in response.data.decode("utf-8")
