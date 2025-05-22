def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_login_invalid(client):
    response = client.post("/login", data={"id": "INVALID", "pw": "wrong"})
    assert response.status_code == 302  # should redirect

def test_public_page(client):
    response = client.get("/public/")
    assert response.status_code == 200
    assert b"public" in response.data.lower()

def test_private_requires_login(client):
    response = client.get("/private/", follow_redirects=True)
    assert b"401" in response.data or response.status_code == 401

def test_admin_requires_login(client):
    response = client.get("/admin/", follow_redirects=True)
    assert response.status_code in [401, 302]

def test_404(client):
    response = client.get("/nonexistentpage")
    assert response.status_code == 404
    assert b"404" in response.data
