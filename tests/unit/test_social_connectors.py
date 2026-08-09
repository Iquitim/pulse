import json
import pytest
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

def test_registry_threads_client():
    creds = json.dumps({"access_token": "mock_token_123"})
    encrypted_creds = encrypt_value(creds)
    
    client = get_social_network_client("threads", encrypted_creds)
    assert isinstance(client, ThreadsNetwork)
    assert client.check_connection() is True
    
    pub_result = client.publish("Post de teste no Threads")
    assert pub_result["status"] == "success"
    assert "threads://" in pub_result["uri"]
