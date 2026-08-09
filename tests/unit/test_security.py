from datetime import timedelta
from app.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    encrypt_value,
    decrypt_value
)

def test_password_hashing():
    raw_pwd = "supersecretpassword123"
    hashed = hash_password(raw_pwd)
    
    assert hashed != raw_pwd
    assert verify_password(raw_pwd, hashed) is True
    assert verify_password("wrongpassword", hashed) is False

def test_jwt_token_generation_and_verification():
    payload_data = {"sub": "test@pulse.com", "role": "user"}
    token = create_access_token(payload_data)
    
    assert token is not None
    assert isinstance(token, str)
    
    decoded = verify_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "test@pulse.com"
    assert decoded["role"] == "user"

def test_jwt_token_expiration():
    payload_data = {"sub": "expired@pulse.com"}
    expired_token = create_access_token(payload_data, expires_delta=timedelta(seconds=-10))
    
    decoded = verify_access_token(expired_token)
    assert decoded is None

def test_fernet_encryption_and_decryption():
    secret_text = "bsky-app-password-1234-5678"
    encrypted = encrypt_value(secret_text)
    
    assert encrypted != secret_text
    decrypted = decrypt_value(encrypted)
    assert decrypted == secret_text
