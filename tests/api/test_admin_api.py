def test_user_audit_logs(client, user_headers):
    response = client.get("/api/audit-logs", headers=user_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_admin_users_list_forbidden_for_regular_user(client, user_headers):
    response = client.get("/api/admin/users", headers=user_headers)
    assert response.status_code == 403
    assert "Acesso negado" in response.json()["detail"]

def test_admin_users_list_allowed_for_admin(client, admin_headers):
    response = client.get("/api/admin/users", headers=admin_headers)
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2
    assert any(u["email"] == "admin@pulse.com" for u in users)

def test_admin_invite_code_generation(client, admin_headers):
    payload = {
        "code": "PULSE-TEST-1234",
        "max_uses": 5,
        "plan_tier": "pro"
    }
    response = client.post("/api/admin/invite-codes", json=payload, headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["code"] == "PULSE-TEST-1234"


