def test_static_functions_route_serves_file(client):
    response = client.get("/Functions/Ecran.js")
    assert response.status_code == 200
    assert response.data


def test_static_images_route_serves_file(client):
    response = client.get("/Images/Logo.png")
    assert response.status_code == 200
    assert response.mimetype.startswith("image/")
