import json
import pytest
from unittest.mock import patch, MagicMock
from app.social.registry import get_social_network_client, NETWORK_CLASSES
from app.social.threads import ThreadsNetwork
from app.security import encrypt_value

def test_registry_supported_platforms():
    assert "bluesky" in NETWORK_CLASSES
    assert "twitter" in NETWORK_CLASSES
    assert "threads" in NETWORK_CLASSES

def test_registry_unsupported_platform():
    with pytest.raises(ValueError, match="não suportada"):
        get_social_network_client("unsupported_network", "dummy_encrypted")

def test_registry_threads_client_initialization():
    creds = json.dumps({"access_token": "th_token_123", "user_id": "12345"})
    encrypted_creds = encrypt_value(creds)
    
    client = get_social_network_client("threads", encrypted_creds)
    assert isinstance(client, ThreadsNetwork)
    assert client.access_token == "th_token_123"
    assert client.user_id == "12345"

@patch("requests.get")
def test_threads_connect_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"id": "th_user_999", "username": "testuser"}
    mock_get.return_value = mock_response

    client = ThreadsNetwork({"access_token": "valid_token"})
    assert client.connect() is True
    assert client.user_id == "th_user_999"
    assert client.account_handle == "@testuser"
    assert client.check_connection() is True

@patch("requests.get")
def test_threads_connect_failure(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.text = "Invalid Token"
    mock_get.return_value = mock_response

    client = ThreadsNetwork({"access_token": "invalid_token"})
    assert client.connect() is False
    assert client.check_connection() is False

@patch("requests.get")
@patch("requests.post")
def test_threads_publish_success(mock_post, mock_get):
    # Mock connect GET /me
    mock_connect_resp = MagicMock()
    mock_connect_resp.status_code = 200
    mock_connect_resp.json.return_value = {"id": "user_123", "username": "testuser"}
    mock_get.return_value = mock_connect_resp

    client = ThreadsNetwork({"access_token": "valid_token", "user_id": "user_123"})
    
    # Mock Step 1 (Container) and Step 2 (Publish)
    resp_step1 = MagicMock()
    resp_step1.status_code = 200
    resp_step1.json.return_value = {"id": "container_456"}
    
    resp_step2 = MagicMock()
    resp_step2.status_code = 200
    resp_step2.json.return_value = {"id": "post_789"}

    mock_post.side_effect = [resp_step1, resp_step2]

    res = client.publish("Olá Mundo no Threads!")
    assert res["status"] == "success"
    assert res["cid"] == "post_789"
    assert "threads.net" in res["uri"]

@patch("requests.get")
@patch("requests.post")
def test_threads_publish_failure(mock_post, mock_get):
    mock_connect_resp = MagicMock()
    mock_connect_resp.status_code = 200
    mock_connect_resp.json.return_value = {"id": "user_123", "username": "testuser"}
    mock_get.return_value = mock_connect_resp

    client = ThreadsNetwork({"access_token": "valid_token", "user_id": "user_123"})
    
    resp_error = MagicMock()
    resp_error.status_code = 400
    resp_error.text = "Publish error"
    mock_post.return_value = resp_error

    with pytest.raises(Exception, match="Publish error"):
        client.publish("Erro no post")

@patch("requests.get")
def test_threads_refresh_token(mock_get):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"access_token": "new_refreshed_token", "expires_in": 5184000}
    mock_get.return_value = mock_resp

    client = ThreadsNetwork({"access_token": "old_token", "user_id": "user_123"})
    success = client.refresh_token()
    assert success is True
    assert client.access_token == "new_refreshed_token"

