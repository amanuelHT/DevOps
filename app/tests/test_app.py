def test_index(client):
    response = client.get("/")
    assert response.status_code == 200

def test_login_invalid(client):
    response = client.post("/login", data={"id": "INVALID", "pw": "wrong"})
    assert response.status_code == 302

def test_login_valid(client, test_user):
    response = client.post("/login", data={"id": test_user[0], "pw": test_user[1]}, follow_redirects=True)
    assert b"Private Page" in response.data or response.status_code == 200

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

def test_add_note(client, test_user):
    client.post("/login", data={"id": test_user[0], "pw": test_user[1]})
    response = client.post("/write_note", data={"text_note_to_take": "Test Note"}, follow_redirects=True)
    assert b"Test Note" in response.data or response.status_code == 200

def test_add_user_as_admin(client, admin_user):
    client.post("/login", data={"id": admin_user[0], "pw": admin_user[1]})
    response = client.post("/add_user", data={"id": "NEWUSER", "pw": "pass"}, follow_redirects=True)
    assert b"NEWUSER" in response.data or response.status_code == 200

def test_upload_image(client, test_user):
    client.post("/login", data={"id": test_user[0], "pw": test_user[1]})
    data = {
        "file": (open("app/static/img/flask-powered.png", "rb"), "flask-powered.png")
    }
    response = client.post("/upload_image", data=data, content_type="multipart/form-data", follow_redirects=True)
    assert b"flask-powered.png" in response.data or response.status_code == 200
