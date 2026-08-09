def test_login_success(client):
    response = client.post("/api/auth/login", json={"email": "user@pulse.com", "password": "user123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "user@pulse.com"
    assert data["user"]["role"] == "user"

def test_login_invalid_credentials(client):
    response = client.post("/api/auth/login", json={"email": "user@pulse.com", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "incorretos" in response.json()["detail"]

def test_register_new_user(client):
    response = client.post("/api/auth/register", json={
        "email": "newuser@pulse.com",
        "password": "newpassword123"
    })
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify logging in with newly created user
    login_res = client.post("/api/auth/login", json={
        "email": "newuser@pulse.com",
        "password": "newpassword123"
    })
    assert login_res.status_code == 200

def test_register_duplicate_email(client):
    response = client.post("/api/auth/register", json={
        "email": "user@pulse.com",
        "password": "user123"
    })
    assert response.status_code == 400
    assert "já está cadastrado" in response.json()["detail"]

def test_get_me_authenticated(client, user_headers):
    response = client.get("/api/auth/me", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "user@pulse.com"
    assert data["role"] == "user"

def test_get_me_unauthorized(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401

def test_change_password(client, user_headers):
    response = client.post("/api/auth/change-password", json={
        "current_password": "user123",
        "new_password": "newuserpassword456"
    }, headers=user_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

    # Verify login with old password fails
    fail_login = client.post("/api/auth/login", json={"email": "user@pulse.com", "password": "user123"})
    assert fail_login.status_code == 401

    # Verify login with new password succeeds
    success_login = client.post("/api/auth/login", json={"email": "user@pulse.com", "password": "newuserpassword456"})
    assert success_login.status_code == 200
