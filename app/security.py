import os
import jwt
import bcrypt
import logging
from typing import Optional
from datetime import datetime, timedelta
from cryptography.fernet import Fernet

logger = logging.getLogger(__name__)

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "pulse-default-jwt-secret-key-32-chars-long-minimum-!!")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour token duration

# Fernet encryption key setup
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    logger.warning("ENCRYPTION_KEY não encontrada nas variáveis de ambiente. Usando chave padrão (NÃO RECOMENDADO EM PRODUÇÃO).")
    # Deterministic base64 valid Fernet key
    ENCRYPTION_KEY = "nSo9pQzaOxO8UR5HjnoPj8Tbgno7FGDj6I3a9T9nPss="

fernet = Fernet(ENCRYPTION_KEY.encode())

# Password hashing
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception as e:
        logger.error(f"Erro ao verificar senha: {e}")
        return False

# JWT tokens
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_access_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.PyJWTError:
        return None

# Fernet encryption/decryption
def encrypt_value(value: str) -> str:
    return fernet.encrypt(value.encode("utf-8")).decode("utf-8")

def decrypt_value(encrypted_value: str) -> str:
    return fernet.decrypt(encrypted_value.encode("utf-8")).decode("utf-8")
