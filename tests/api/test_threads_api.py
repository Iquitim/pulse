import pytest
from unittest.mock import patch, MagicMock

def test_admin_global_settings_threads(client, admin_headers):
    # Get initial settings
    res = client.get("/api/admin/global-settings", headers=admin_headers)
    assert res.status_code == 200
    data = res.json()
    assert "threads_app_id" in data
    assert "threads_app_secret_configured" in data
    assert "threads_redirect_uri" in data

    # Update Threads settings
    update_payload = {
        "threads_app_id": "test_th_app_123",
        "threads_app_secret": "test_th_secret_456",
        "threads_redirect_uri": "http://127.0.0.1:8000/api/social/threads/callback"
    }
    update_res = client.put("/api/admin/global-settings", json=update_payload, headers=admin_headers)
    assert update_res.status_code == 200

    # Verify settings persisted
    verify_res = client.get("/api/admin/global-settings", headers=admin_headers)
    assert verify_res.status_code == 200
    v_data = verify_res.json()
    assert v_data["threads_app_id"] == "test_th_app_123"
    assert v_data["threads_app_secret_configured"] is True
    assert v_data["threads_redirect_uri"] == "http://127.0.0.1:8000/api/social/threads/callback"

@patch("requests.get")
def test_user_connect_manual_threads_account(mock_get, client, user_headers):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"id": "th_user_1001", "username": "pulse_threads_user"}
    mock_get.return_value = mock_resp

    payload = {
        "platform": "threads",
        "account_handle": "@pulse_threads_user",
        "credentials": {
            "access_token": "valid_mock_threads_token",
            "user_id": "th_user_1001"
        }
    }
    res = client.post("/api/social-accounts", json=payload, headers=user_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"

    # Verify in list
    list_res = client.get("/api/social-accounts", headers=user_headers)
    assert list_res.status_code == 200
    accounts = list_res.json()
    assert any(a["platform"] == "threads" and a["account_handle"] == "@pulse_threads_user" for a in accounts)

def test_threads_login_endpoint(client, user_headers, admin_headers):
    # Set App ID and Secret first
    client.put("/api/admin/global-settings", json={
        "threads_app_id": "meta_app_id_999",
        "threads_app_secret": "meta_app_secret_888"
    }, headers=admin_headers)

    token = user_headers["Authorization"].split("Bearer ")[1]
    res = client.get(f"/api/social/threads/login?token={token}&handle=@user_test", follow_redirects=False)
    assert res.status_code == 307
    location = res.headers.get("location")
    assert "https://threads.net/oauth/authorize" in location
    assert "client_id=meta_app_id_999" in location
    assert "threads_basic" in location
    assert "threads_content_publish" in location

@patch("requests.get")
@patch("requests.post")
def test_threads_callback_flow(mock_post, mock_get, client, user_headers, admin_headers):
    client.put("/api/admin/global-settings", json={
        "threads_app_id": "meta_app_id_999",
        "threads_app_secret": "meta_app_secret_888"
    }, headers=admin_headers)

    token = user_headers["Authorization"].split("Bearer ")[1]
    login_res = client.get(f"/api/social/threads/login?token={token}&handle=@user_oauth", follow_redirects=False)
    cookies = login_res.cookies

    state = cookies.get("th_oauth_state")
    assert state is not None

    # Mock short-lived token POST
    short_resp = MagicMock()
    short_resp.status_code = 200
    short_resp.json.return_value = {"access_token": "short_token_xyz", "user_id": "th_user_555"}
    mock_post.return_value = short_resp

    # Mock long-lived exchange GET and me GET
    long_resp = MagicMock()
    long_resp.status_code = 200
    long_resp.json.return_value = {"access_token": "long_token_abc", "expires_in": 5184000}

    me_resp = MagicMock()
    me_resp.status_code = 200
    me_resp.json.return_value = {"id": "th_user_555", "username": "user_oauth"}

    mock_get.side_effect = [long_resp, me_resp]

    callback_res = client.get(
        f"/api/social/threads/callback?code=auth_code_123&state={state}",
        cookies=cookies
    )
    assert callback_res.status_code == 200
    assert "threads_connected" in callback_res.text
