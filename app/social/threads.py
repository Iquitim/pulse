import logging
from app.social.base import BaseSocialNetwork

logger = logging.getLogger(__name__)

class ThreadsNetwork(BaseSocialNetwork):
    def __init__(self, access_token: str = ""):
        self.access_token = access_token

    def connect(self) -> bool:
        logger.info("[Mock Threads] Conexão com Threads simulada.")
        return True

    def check_connection(self) -> bool:
        return True

    def publish(self, content: str) -> dict:
        logger.info(f"[Mock Threads] Publicando atualização de status.")
        return {
            "status": "success",
            "uri": "threads://post/mock_post_9876",
            "cid": "mock_cid_threads"
        }
