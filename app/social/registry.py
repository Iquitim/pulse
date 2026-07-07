import json
import logging
from typing import Dict, Type
from app.social.base import BaseSocialNetwork
from app.social.bluesky import BlueskyNetwork
from app.social.twitter import TwitterNetwork
from app.social.threads import ThreadsNetwork
from app import security

logger = logging.getLogger(__name__)

NETWORK_CLASSES: Dict[str, Type[BaseSocialNetwork]] = {
    "bluesky": BlueskyNetwork,
    "twitter": TwitterNetwork,
    "threads": ThreadsNetwork
}

def get_social_network_client(platform: str, encrypted_credentials_str: str) -> BaseSocialNetwork:
    """
    Decifra as credenciais e retorna uma instância do cliente de rede social correspondente.
    """
    if platform not in NETWORK_CLASSES:
        raise ValueError(f"Plataforma de rede social não suportada: {platform}")
        
    try:
        # Decifra a string JSON das credenciais
        decrypted_json_str = security.decrypt_value(encrypted_credentials_str)
        credentials = json.loads(decrypted_json_str)
    except Exception as e:
        logger.error(f"Falha ao decifrar credenciais para a plataforma {platform}: {e}")
        raise ValueError("Chaves ou credenciais inválidas / corrompidas.")

    cls = NETWORK_CLASSES[platform]
    
    # Instancia de acordo com os parâmetros necessários de cada classe
    if platform == "bluesky":
        return cls(
            handle=credentials.get("handle", ""),
            password=credentials.get("password", "")
        )
    elif platform == "twitter":
        return cls(credentials=credentials)
    elif platform == "threads":
        return cls(
            access_token=credentials.get("access_token", "")
        )
    else:
        raise ValueError(f"Instanciação não configurada para a plataforma: {platform}")
