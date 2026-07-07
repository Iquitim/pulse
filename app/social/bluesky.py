import logging
from atproto import Client
from app.social.base import BaseSocialNetwork

logger = logging.getLogger(__name__)

class BlueskyNetwork(BaseSocialNetwork):
    def __init__(self, handle: str, password: str):
        self.handle = handle
        self.password = password
        self.client = None

    def connect(self) -> bool:
        if not self.handle or not self.password:
            return False
        try:
            self.client = Client()
            self.client.login(self.handle, self.password)
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao Bluesky ({self.handle}): {e}")
            return False

    def check_connection(self) -> bool:
        return self.connect()

    def publish(self, content: str) -> dict:
        # Garante conexão ativa
        if not self.client:
            connected = self.connect()
            if not connected or not self.client:
                raise ValueError("Cliente Bluesky não autenticado.")
        
        try:
            result = self.client.send_post(text=content)
            return {
                "status": "success",
                "uri": getattr(result, "uri", None),
                "cid": getattr(result, "cid", None)
            }
        except Exception as e:
            logger.error(f"Erro ao publicar no Bluesky ({self.handle}): {e}")
            raise e
